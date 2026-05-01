# OCR With Tesseract

Tesseract 5 is the default OCR engine. Free, self-hosted, good enough for machine-printed text. For handwriting, low-quality scans, or structured forms at scale, move to Google Vision or AWS Textract — but budget the cost.

## Install (Debian / Ubuntu)

```bash
sudo apt-get update
sudo apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-fra \
    tesseract-ocr-swa \
    libtesseract-dev \
    poppler-utils            # for pdf2image
# Optional:
sudo apt-get install -y tesseract-ocr-script-latn tesseract-ocr-osd
```

Language packs are per-language (`eng`, `fra`, `swa`, etc.). Check installed languages:

```bash
tesseract --list-langs
```

Python bindings:

```bash
uv add pytesseract pillow opencv-python-headless pdf2image
```

## Page Segmentation Mode (PSM)

PSM tells Tesseract what shape of content to expect. Wrong PSM is the most common accuracy bug.

| PSM | Use case |
|-----|----------|
| 1   | Auto with OSD (orientation + script detection) |
| 3   | Auto (default) — fully automatic, no OSD |
| 4   | Single column of variable-height text (newspaper column) |
| 6   | **Single uniform block of text — default for receipts, invoices, paragraphs** |
| 7   | Single text line — useful for OCR'ing a cropped field (e.g. a total) |
| 8   | Single word — one token only |
| 11  | Sparse text, no particular order — loose scenes, signs, ID cards with scattered fields |
| 12  | Sparse text with OSD |
| 13  | Raw line, no Tesseract heuristics — for already-cleaned lines |

Rule of thumb:

- Receipts, invoices, letters, scanned docs → PSM 6.
- A cropped field (one amount, one name) → PSM 7 or 8.
- ID cards, business cards, posters → PSM 11.

## Preprocessing pipeline

Preprocessing dominates accuracy more than PSM or model choice. Standard pipeline:

```python
import cv2
import numpy as np
from PIL import Image
import pytesseract

def preprocess(path: str) -> np.ndarray:
    img = cv2.imread(path)

    # 1. Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. Upscale small images (OCR loves ~300 DPI equivalent)
    h, w = gray.shape
    if max(h, w) < 1600:
        scale = 1600 / max(h, w)
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # 3. Denoise
    gray = cv2.fastNlMeansDenoising(gray, h=15, templateWindowSize=7, searchWindowSize=21)

    # 4. Adaptive threshold (handles uneven lighting, shadows)
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=31, C=10,
    )

    # 5. Deskew
    thresh = deskew(thresh)

    return thresh

def deskew(img: np.ndarray) -> np.ndarray:
    coords = np.column_stack(np.where(img < 127))
    if len(coords) == 0:
        return img
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    if abs(angle) < 0.5:
        return img
    (h, w) = img.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE, borderValue=255)
```

Ordering matters: grayscale → upscale → denoise → threshold → deskew. Running denoise after threshold smears characters.

### Preprocessing decisions

| Symptom | Fix |
|---|---|
| Uneven lighting, shadowed corners | Adaptive threshold (not global Otsu) |
| Small font, low DPI phone photo | Upscale 2–3×, `INTER_CUBIC` |
| Speckled scan | `fastNlMeansDenoising` |
| Rotated scan | Deskew via `minAreaRect` |
| Coloured background / receipt with logo | Background subtraction via morphological opening |
| Bleed-through (double-sided paper) | Increase `C` in adaptive threshold (more aggressive) |

## Multi-language

```python
# English + French (common for ECOWAS, Francophone Africa)
text = pytesseract.image_to_string(img, lang="eng+fra", config="--psm 6")

# English + Swahili
text = pytesseract.image_to_string(img, lang="eng+swa", config="--psm 6")
```

Rules:

- Combine only languages actually on the page. Every extra language lowers accuracy for the dominant one.
- Order matters — put the dominant language first.
- For ID cards with a Latin field and a non-Latin field, run twice with different `lang=` and different crops.

## Extracting confidence

Use `image_to_data` with TSV output. Each word gets a `conf` (0–100).

```python
import pandas as pd

def ocr_with_confidence(img: np.ndarray, lang: str = "eng") -> pd.DataFrame:
    df = pytesseract.image_to_data(
        img,
        lang=lang,
        config="--psm 6",
        output_type=pytesseract.Output.DATAFRAME,
    )
    df = df[(df["conf"] >= 0) & (df["text"].astype(str).str.strip() != "")]
    return df[["page_num", "block_num", "line_num", "word_num", "left", "top", "width", "height", "conf", "text"]]

def low_confidence_words(df: pd.DataFrame, threshold: int = 60) -> pd.DataFrame:
    return df[df["conf"] < threshold]
```

Use confidence to decide:

- If average confidence over an invoice total region < 70 → route the document to human review.
- If confidence on a single critical field (amount, invoice number) < 80 → reject, do not auto-post.
- Log mean and min confidence per document in the `pipeline_runs` table.

## Regions of interest

OCR-ing the whole image and parsing the result with regex is brittle. For known layouts (each tenant's own receipt, an ID card), OCR the specific region:

```python
def ocr_region(img: np.ndarray, box: tuple[int, int, int, int], config: str = "--psm 7") -> str:
    x, y, w, h = box
    crop = img[y:y+h, x:x+w]
    return pytesseract.image_to_string(crop, config=config).strip()

total = ocr_region(img, box=(420, 980, 180, 42), config="--psm 7 -c tessedit_char_whitelist=0123456789.,")
```

`tessedit_char_whitelist` is a hard whitelist. For numeric fields it removes entire classes of errors (O vs 0, l vs 1).

## When to switch off Tesseract

Decision matrix:

| Situation | Tool |
|---|---|
| Clean machine-printed receipts, invoices, letters | Tesseract |
| Handwritten notes, cheque amounts | Google Vision Document AI / AWS Textract |
| Structured forms (key-value pairs) at scale | AWS Textract Forms or Azure Form Recogniser |
| Tables embedded in scans | AWS Textract Tables, then validate with pandas |
| ID cards with mixed script | Google Vision (better script handling) |
| Air-gapped / data sovereignty required | Tesseract only |
| Volumes > 10k documents/day with tight SLA | Cloud OCR for throughput; Tesseract can keep up but latency varies |

Cost sanity check (rough 2025):

- Tesseract: CPU only, ~0.5–2s per page on a modern server. Free.
- Google Vision: ~$1.50 per 1,000 pages (first 1M). Reliable and consistent.
- AWS Textract (basic): ~$1.50 per 1,000 pages; Forms/Tables features cost much more.

Break-even is around a few hundred documents per day. Under that, Tesseract is cheaper even counting your engineer's time.

## Integration with the pipeline

```python
def ocr_receipt(tenant_id: int, file_path: Path) -> OcrResult:
    img = preprocess(str(file_path))
    df = ocr_with_confidence(img, lang="eng")
    text = "\n".join(df.sort_values(["block_num", "line_num", "word_num"])["text"].astype(str))
    mean_conf = float(df["conf"].mean()) if not df.empty else 0.0
    min_conf = int(df["conf"].min()) if not df.empty else 0

    if mean_conf < 60:
        route_to_human_review(tenant_id, file_path, reason="ocr_low_confidence", mean_conf=mean_conf)

    return OcrResult(
        tenant_id=tenant_id,
        text=text,
        mean_confidence=mean_conf,
        min_confidence=min_conf,
        lang="eng",
    )
```

## Anti-patterns

- Running OCR on unprocessed colour images. Accuracy drops 20–40%.
- Global threshold (Otsu) on uneven-lit phone photos.
- Using PSM 3 for everything because it is the default.
- Skipping confidence scoring. Blind acceptance of OCR output in a financial pipeline is how you end up posting "O.OO" entries.
- Running Tesseract in a tight loop without a worker pool. It is CPU-bound — use a process pool, not threads.
