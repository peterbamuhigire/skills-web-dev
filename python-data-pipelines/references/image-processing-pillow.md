# Image Processing With Pillow

Pillow is the default for image work in these pipelines. For a 2–4× speedup on CPU-heavy resize/convert loops, swap in `pillow-simd`.

## Installation

```bash
# Standard
uv add pillow piexif

# Faster resize/convert (drop-in replacement; uninstall pillow first)
uv remove pillow
CC="cc -mavx2" uv add pillow-simd
```

`pillow-simd` is binary-compatible with Pillow. Same imports. It trades portability for speed; only install if the server has AVX2 and you are CPU-bound.

## Resize vs thumbnail

`resize()` returns a new image of exactly the size you ask.
`thumbnail()` shrinks in place and **preserves aspect ratio** — it will not exceed the given box.

```python
from PIL import Image

with Image.open(src) as img:
    # resize — exact dimensions, may distort
    out = img.resize((400, 400), Image.LANCZOS)

with Image.open(src) as img:
    # thumbnail — aspect preserved, fits inside 400x400
    img.thumbnail((400, 400), Image.LANCZOS)
    img.save(dst)
```

**Always use `Image.LANCZOS` for downscaling.** It is the best quality/speed tradeoff. `NEAREST` is fastest but ugly; `BICUBIC` is fine but slightly softer than LANCZOS.

For upscaling (rare in pipelines — avoid if possible), `BICUBIC` is adequate.

## Thumbnails at multiple sizes

A common SaaS pattern: serve one uploaded image at `sm`, `md`, `lg`.

```python
THUMB_SIZES = {
    "sm": (160, 160),
    "md": (400, 400),
    "lg": (1200, 1200),
}

def make_thumbnails(src: Path, out_dir: Path, tenant_id: int) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    with Image.open(src) as img:
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        for label, size in THUMB_SIZES.items():
            copy = img.copy()
            copy.thumbnail(size, Image.LANCZOS)
            dst = out_dir / f"{src.stem}_{label}.webp"
            copy.save(dst, "WEBP", quality=85, method=6)
            results[label] = dst
    return results
```

Rules:

- Convert to RGB once before making copies. `img.copy()` is cheap, repeated `convert()` is not.
- Use WebP or AVIF for serving; JPEG still for broad compatibility.
- `method=6` in WebP = slowest encode, best compression. Use 4 for latency-sensitive paths.

## EXIF-aware rotation

Phones store the image sensor's orientation in EXIF. The pixels are in sensor-native order; the app rotates on display based on the tag. If you resize without handling this, you get rotated thumbnails.

```python
from PIL import Image, ImageOps

with Image.open(src) as img:
    img = ImageOps.exif_transpose(img)   # applies rotation, removes EXIF orientation tag
```

`exif_transpose` rewrites the pixel data into the displayed orientation and drops the `Orientation` tag. Do this before every resize.

## EXIF stripping — always for public uploads

EXIF can include GPS, device model, and timestamps. Always strip it before serving publicly.

### Option 1: re-create the image (most thorough)

```python
from PIL import Image

def strip_all_metadata(src: Path, dst: Path) -> None:
    with Image.open(src) as img:
        img = ImageOps.exif_transpose(img)
        data = list(img.getdata())
        clean = Image.new(img.mode, img.size)
        clean.putdata(data)
        clean.save(dst)
```

This drops every piece of metadata — EXIF, XMP, IPTC, ICC profile (which you usually want to keep for colour accuracy, so prefer option 2).

### Option 2: piexif (preserves ICC, drops EXIF)

```python
import piexif
from PIL import Image

def strip_exif(src: Path, dst: Path) -> None:
    img = Image.open(src)
    img = ImageOps.exif_transpose(img)
    img.save(dst, img.format or "JPEG", exif=b"")   # write empty EXIF block
```

Or to strip in place on a JPEG:

```python
piexif.remove(str(path))
```

Rules:

- Strip EXIF on every tenant upload before public serving. Non-negotiable.
- Preserve ICC profile for images where colour accuracy matters (product photos, medical) — store the profile separately and reattach.
- Keep the original with EXIF intact in private storage if the tenant has a legal need for chain-of-custody (insurance claims, legal evidence). Never serve the original publicly.

## Watermarking

Scale the watermark relative to the base image. A fixed 200px logo looks huge on a thumbnail and tiny on a 4k photo.

```python
from PIL import Image

def add_watermark(src: Path, dst: Path, wm_path: Path, opacity: float = 0.5, width_ratio: float = 0.2) -> None:
    with Image.open(src).convert("RGBA") as base, Image.open(wm_path).convert("RGBA") as wm:
        # scale watermark to width_ratio of the base width
        target_w = int(base.width * width_ratio)
        ratio = target_w / wm.width
        wm = wm.resize((target_w, int(wm.height * ratio)), Image.LANCZOS)

        # adjust opacity
        alpha = wm.split()[3]
        alpha = alpha.point(lambda p: int(p * opacity))
        wm.putalpha(alpha)

        # position: bottom-right with 2% margin
        margin = int(base.width * 0.02)
        pos = (base.width - wm.width - margin, base.height - wm.height - margin)

        base.alpha_composite(wm, pos)
        base.convert("RGB").save(dst, "JPEG", quality=90)
```

Rules:

- Put the watermark somewhere the user cannot easily crop it out but where it does not obscure the subject. Bottom-right is standard.
- Use opacity 0.3–0.6. Above that reads as vandalism; below that disappears on busy backgrounds.
- Pre-render the watermark once at a large size; scale down per image. Never upscale a small watermark.

## Format conversion

| Format | Use when |
|---|---|
| JPEG | Photos, widest compatibility, no transparency needed |
| PNG | Screenshots, logos, anything with transparency |
| WebP | Modern web serving; 25–35% smaller than JPEG at same quality |
| AVIF | Even smaller than WebP; slower encode; use via `pillow-avif-plugin` |

```python
# JPEG — quality 85 is the usual sweet spot
img.save(dst, "JPEG", quality=85, optimize=True, progressive=True)

# WebP — lossy, quality 85, best compression
img.save(dst, "WEBP", quality=85, method=6)

# WebP — lossless (larger but crisp for UI assets)
img.save(dst, "WEBP", lossless=True, method=6)

# PNG — optimise
img.save(dst, "PNG", optimize=True, compress_level=9)
```

Rules:

- `quality=85` for JPEG/WebP is the honest default. Below 70 shows artefacts on gradients; above 92 is mostly wasted bytes.
- `progressive=True` on JPEG for web images: starts showing at low res while loading.
- Strip alpha channels before saving JPEG — Pillow will error on RGBA-to-JPEG. Always `convert("RGB")` first.

## Quality ladders

For a typical product photo pipeline, store three variants:

| Name | Size | Format | Quality | Purpose |
|---|---|---|---|---|
| thumb | 320×320 | WebP | 80 | Grid listing |
| card | 800×800 | WebP | 85 | Detail card, mobile |
| hero | 1600×1600 | WebP | 90 | Full-page hero |

Plus an original (private) for future re-encoding.

## Validating uploads

Before opening, validate:

```python
import magic
from PIL import Image, UnidentifiedImageError

ALLOWED = {"image/jpeg", "image/png", "image/webp", "image/heic"}
MAX_BYTES = 15 * 1024 * 1024   # 15 MB
MAX_PIXELS = 50 * 1_000_000    # 50 MP — guard against decompression bombs

Image.MAX_IMAGE_PIXELS = MAX_PIXELS

def validate_image_upload(path: Path) -> None:
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("file too large")
    mime = magic.from_file(str(path), mime=True)
    if mime not in ALLOWED:
        raise ValueError(f"mime not allowed: {mime}")
    try:
        with Image.open(path) as img:
            img.verify()                    # detect truncated/corrupt
    except UnidentifiedImageError:
        raise ValueError("not a recognised image")
```

Setting `Image.MAX_IMAGE_PIXELS` protects against decompression-bomb attacks (a 1KB PNG that expands to 40GB in RAM).

## HEIC on the backend

iPhones upload HEIC by default. Install `pillow-heif` to add a decoder:

```bash
uv add pillow-heif
```

```python
from pillow_heif import register_heif_opener
register_heif_opener()
# now Image.open works on .heic files
```

Re-encode to JPEG or WebP immediately on upload; do not serve HEIC back to browsers (patchy support).

## Colour space

Pillow preserves the ICC profile by default if you read/write formats that support it. For a neutral pipeline:

```python
# Convert to sRGB for web
from PIL import ImageCms

def to_srgb(img: Image.Image) -> Image.Image:
    icc = img.info.get("icc_profile")
    if not icc:
        return img
    src_profile = ImageCms.ImageCmsProfile(io.BytesIO(icc))
    dst_profile = ImageCms.createProfile("sRGB")
    return ImageCms.profileToProfile(img, src_profile, dst_profile, outputMode="RGB")
```

Without this, a wide-gamut DSLR photo will look washed out in some browsers.

## Anti-patterns

- Resizing without `exif_transpose` first → rotated thumbnails.
- Saving RGBA as JPEG without converting to RGB → exception.
- Fixed-size watermarks → huge on thumbs, invisible on originals.
- Not setting `Image.MAX_IMAGE_PIXELS` → decompression bomb DOS.
- Using threads for heavy Pillow work → GIL-bound. Use `ProcessPoolExecutor`.
- Serving the original EXIF-laden photo publicly.
- Re-encoding the same image multiple times through the serve path. Do it once on upload, cache the variants.
