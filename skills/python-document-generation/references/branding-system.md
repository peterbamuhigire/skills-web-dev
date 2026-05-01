# Branding System

One source of truth for brand across Excel, Word, and PDF output. Load the tenant's brand once per job; apply it consistently across every output type.

## Brand dataclass

```python
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from pathlib import Path

@dataclass(frozen=True, slots=True)
class Brand:
    # Core palette (hex with leading #).
    primary:    str
    secondary:  str
    accent:     str = "#F59E0B"

    # Neutrals.
    text:       str = "#111827"
    muted:      str = "#6B7280"
    surface:    str = "#FFFFFF"
    surface_alt:str = "#F9FAFB"
    border:     str = "#E5E7EB"

    # Semantic.
    success:    str = "#059669"
    warning:    str = "#D97706"
    danger:     str = "#DC2626"
    info:       str = "#2563EB"

    # Typography.
    font_family:        str = "Inter"
    font_family_mono:   str = "JetBrains Mono"

    # Assets.
    logo_path:          Path = field(default=None)   # PNG, prefer 800x200 px
    logo_dark_path:     Path | None = None           # light-on-dark variant
    favicon_path:       Path | None = None

    # Copy.
    tenant_name:        str = ""
    footer_tagline:     str = ""
    support_email:      str = ""
    support_phone:      str = ""

    # Versioning.
    version:            str = "1.0.0"
    updated_at:         str = ""   # ISO date

    @classmethod
    def from_tenant(cls, tenant) -> "Brand":
        return cls(
            primary=tenant.brand_primary or "#0B5FFF",
            secondary=tenant.brand_secondary or "#6B7280",
            accent=tenant.brand_accent or "#F59E0B",
            font_family=tenant.brand_font_family or "Inter",
            logo_path=Path(tenant.logo_path),
            tenant_name=tenant.name,
            footer_tagline=tenant.footer_tagline or "",
            support_email=tenant.support_email or "",
            version=tenant.brand_version or "1.0.0",
            updated_at=tenant.brand_updated_at.isoformat() if tenant.brand_updated_at else "",
        )

    def as_css_variables(self) -> str:
        return "\n".join([
            ":root {",
            f"  --brand-primary:   {self.primary};",
            f"  --brand-secondary: {self.secondary};",
            f"  --brand-accent:    {self.accent};",
            f"  --brand-text:      {self.text};",
            f"  --brand-muted:     {self.muted};",
            f"  --brand-surface:   {self.surface};",
            f"  --brand-border:    {self.border};",
            f"  --brand-success:   {self.success};",
            f"  --brand-warning:   {self.warning};",
            f"  --brand-danger:    {self.danger};",
            f"  --brand-font:      \"{self.font_family}\", sans-serif;",
            "}",
        ])
```

`frozen=True` stops accidental mutation mid-render. `slots=True` cuts memory per instance — relevant when the worker caches brands per tenant.

## Loading per tenant

```python
from functools import lru_cache

@lru_cache(maxsize=256)
def brand_for_tenant(tenant_id: int, brand_version: str) -> Brand:
    tenant = Tenant.load(tenant_id)
    return Brand.from_tenant(tenant)
```

Cache key includes `brand_version`. When the tenant updates their brand, they bump `brand_version` (see versioning below); cache entry invalidates automatically.

## Applying to xlsxwriter

```python
def xlsx_formats(wb, brand):
    base = {"font_name": brand.font_family}
    return {
        "title":     wb.add_format({**base, "bold": True, "font_size": 20, "font_color": brand.primary}),
        "h2":        wb.add_format({**base, "bold": True, "font_size": 14, "font_color": brand.text}),
        "header":    wb.add_format({**base, "bold": True, "bg_color": brand.primary,
                                     "font_color": "#FFFFFF", "border": 1}),
        "cell":      wb.add_format({**base, "border": 1, "border_color": brand.border}),
        "good":      wb.add_format({**base, "font_color": brand.success, "bold": True}),
        "bad":       wb.add_format({**base, "font_color": brand.danger, "bold": True}),
        "warn":      wb.add_format({**base, "font_color": brand.warning, "bold": True}),
        "muted":     wb.add_format({**base, "font_color": brand.muted, "italic": True}),
    }
```

## Applying to python-docx

```python
from docx.shared import Pt, RGBColor

def apply_word_styles(doc, brand):
    styles = doc.styles
    rgb = lambda hex_: RGBColor.from_string(hex_.lstrip("#"))

    normal = styles["Normal"]
    normal.font.name = brand.font_family
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = rgb(brand.text)

    for level, size in [(1, 20), (2, 15), (3, 12)]:
        s = styles[f"Heading {level}"]
        s.font.name = brand.font_family
        s.font.size = Pt(size)
        s.font.color.rgb = rgb(brand.primary)
        s.font.bold = True
```

## Applying to ReportLab

```python
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import TableStyle

def reportlab_styles(brand):
    base = getSampleStyleSheet()
    primary = colors.HexColor(brand.primary)
    text    = colors.HexColor(brand.text)
    muted   = colors.HexColor(brand.muted)

    return {
        "title": ParagraphStyle("title", parent=base["Heading1"],
                                fontName=f"{brand.font_family}-B",
                                fontSize=22, leading=26, textColor=primary),
        "h2":    ParagraphStyle("h2", parent=base["Heading2"],
                                fontName=f"{brand.font_family}-B",
                                fontSize=14, leading=18, textColor=primary),
        "body":  ParagraphStyle("body", parent=base["BodyText"],
                                fontName=brand.font_family,
                                fontSize=10, leading=14, textColor=text),
        "small": ParagraphStyle("small", fontName=brand.font_family,
                                fontSize=8, leading=11, textColor=muted),
    }

def reportlab_table_style(brand):
    return TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), colors.HexColor(brand.primary)),
        ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
        ("FONTNAME",    (0,0), (-1,0), f"{brand.font_family}-B"),
        ("FONTNAME",    (0,1), (-1,-1), brand.font_family),
        ("LINEBELOW",   (0,0), (-1,-1), 0.25, colors.HexColor(brand.border)),
    ])
```

## Applying to WeasyPrint

```python
from weasyprint import CSS

def weasyprint_stylesheets(brand, base_css_path):
    base = CSS(filename=str(base_css_path))
    tenant_css = CSS(string=brand.as_css_variables())
    return [base, tenant_css]
```

Base CSS uses `var(--brand-primary)` everywhere. The tenant override only redefines the variables. One stylesheet, every tenant.

## Charts

See `charts-for-embedding.md`. `ChartPalette.from_brand(brand)` derives a consistent palette for matplotlib so the same primary colour appears in every chart.

## Versioning brand definitions

Brand changes are breaking changes for rendered documents. Two customers opening "the same" report in January and March must see identical output unless you explicitly re-render.

Strategy:

1. Store `brand_version` on the tenant (`SemVer`).
2. Store the rendered-with version in the job's metadata and the document metadata (`wb.set_properties`, PDF `/Subject`, docx `core_properties.comments`).
3. On brand change, bump the version; do not retroactively rewrite existing files.
4. For regenerate-on-demand, always render with the CURRENT brand and stamp the new version.

```python
# Stamp the version into the file so audit can trace which brand produced which artefact.
wb.set_properties({
    "title": report_title,
    "author": tenant.name,
    "company": tenant.name,
    "keywords": f"brand={brand.version}",
    "comments": f"Generated {datetime.now(UTC).isoformat()}",
})
```

## Supplying fonts

The font declared in `brand.font_family` must be installed in the render environment:

- xlsxwriter: the font must be resolvable by Excel on the viewer's machine. If unsure, stick to widely available families (Inter — embed via the system; Arial/Calibri as safe fallbacks). Set a graceful fallback in `add_format({"font_name": brand.font_family})` — Excel will substitute silently.
- python-docx: Word falls back too. Set the font at the style level; do not fight it.
- ReportLab: register the TTFs explicitly with `pdfmetrics.registerFont`. Without this, reportlab uses Helvetica. See `pdf-reportlab.md`.
- WeasyPrint: `@font-face` directives, or install the TTFs at `/usr/share/fonts/` and let fontconfig find them.

Ship the brand fonts with your deploy. Do not rely on the OS.

## Per-tenant asset caching

```python
from functools import lru_cache

@lru_cache(maxsize=256)
def load_logo_bytes(tenant_id: int, logo_version: str) -> bytes:
    path = Tenant.load(tenant_id).logo_path
    return path.read_bytes()
```

Worker processes load each logo once, not per job. Cache key must include `logo_version` so brand updates invalidate stale bytes.

## Default palette (when a tenant has not configured brand)

```python
DEFAULT_BRAND = Brand(
    primary="#0B5FFF",
    secondary="#6B7280",
    logo_path=Path(__file__).parent / "assets" / "default_logo.png",
    footer_tagline="",
    tenant_name="",
)
```

Always have a default. A tenant who has not yet configured their brand still needs a clean artefact, not a broken one.

## Validation on save

When a tenant updates their brand via admin UI:

- hex colours must match `^#[0-9A-Fa-f]{6}$`.
- contrast between `primary` and white must be >= 4.5:1 (WCAG AA). Reject otherwise — white text on header rows will be illegible.
- logo max dimensions 1600 x 400 px; reject larger uploads server-side and auto-resize.
- `font_family` must be from a pre-approved list (the fonts you ship).

## Anti-patterns

- Passing raw hex strings through function signatures — use the `Brand` dataclass.
- Letting tenants set any font from a free-text field — pin to installed families.
- Mutating `Brand` mid-render — `frozen=True` prevents this at runtime.
- Storing only the primary colour and deriving everything else — neutrals and semantics also vary per tenant design system.
- Re-rendering old reports with the current brand without user opt-in — audit trail confusion ("this report has a different logo from last month").
- Forgetting to stamp the brand version into output metadata — makes forensic reconstruction impossible.
