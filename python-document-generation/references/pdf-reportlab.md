# PDF Generation with ReportLab

Use reportlab (platypus) when layout precision matters: financial statements, audit trails, invoices, statements, any data-dense paginated report. No system dependencies beyond Python.

## Platypus mental model

`platypus` = Page Layout and Typography Using Scripts. A `SimpleDocTemplate` (or `BaseDocTemplate`) holds page templates. You hand it a list of `Flowable` objects ("story"). ReportLab paginates them, invoking your `onFirstPage` / `onLaterPages` callbacks to draw chrome (header, footer, logo).

Core flowables:

- `Paragraph(text, style)` — styled text, handles wrapping.
- `Spacer(width, height)` — vertical whitespace.
- `Image(path, width, height)` — raster or vector.
- `Table(data, colWidths, rowHeights, style)` — tabular data with cell styling.
- `PageBreak()` — forces new page.
- `KeepTogether(flowables)` — forbids page break inside a group.
- `KeepInFrame(maxW, maxH, content)` — scale or clip if oversized.
- `PageBreakIfNotEnough(height)` — conditional break.

## Document skeleton

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def build_pdf(path, brand, tenant, data):
    register_fonts(brand)
    doc = BaseDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=28*mm, bottomMargin=20*mm,
        title=data["title"],
        author=tenant.name,
        subject=data["subject"],
        creator="MySaaS Report Engine",
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        id="body", showBoundary=0,
    )
    doc.addPageTemplates([
        PageTemplate(id="first", frames=[frame], onPage=_cover_chrome(brand, tenant)),
        PageTemplate(id="later", frames=[frame], onPage=_body_chrome(brand, tenant)),
    ])
    story = build_story(brand, tenant, data)
    doc.build(story)
```

`BaseDocTemplate` with named page templates is preferred over `SimpleDocTemplate` — it gives independent first-page and later-page chrome without relying on `onFirstPage`/`onLaterPages` switches that are harder to reuse.

To force the body template after the cover:

```python
from reportlab.platypus import NextPageTemplate

story = [
    # ... cover flowables ...
    NextPageTemplate("later"),
    PageBreak(),
    # ... body flowables ...
]
```

## Font registration

System fonts are not portable. Ship your brand's TTFs with the app.

```python
def register_fonts(brand):
    base = Path(__file__).parent / "fonts"
    pdfmetrics.registerFont(TTFont(brand.font_family,          str(base / "Inter-Regular.ttf")))
    pdfmetrics.registerFont(TTFont(f"{brand.font_family}-B",   str(base / "Inter-Bold.ttf")))
    pdfmetrics.registerFont(TTFont(f"{brand.font_family}-I",   str(base / "Inter-Italic.ttf")))
    pdfmetrics.registerFont(TTFont(f"{brand.font_family}-BI",  str(base / "Inter-BoldItalic.ttf")))
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    registerFontFamily(
        brand.font_family,
        normal=brand.font_family,
        bold=f"{brand.font_family}-B",
        italic=f"{brand.font_family}-I",
        boldItalic=f"{brand.font_family}-BI",
    )
```

Do this once per process, not per document.

## Paragraph styles

```python
def build_styles(brand):
    base = getSampleStyleSheet()
    s = {}
    primary = colors.HexColor(brand.primary)
    text = colors.HexColor(brand.text)
    muted = colors.HexColor(brand.muted)

    s["title"]   = ParagraphStyle("title", parent=base["Heading1"],
                                   fontName=f"{brand.font_family}-B",
                                   fontSize=22, leading=26, textColor=primary,
                                   spaceAfter=6)
    s["subtitle"]= ParagraphStyle("subtitle", parent=base["Heading2"],
                                   fontName=brand.font_family,
                                   fontSize=12, leading=16, textColor=muted,
                                   spaceAfter=18)
    s["h2"]      = ParagraphStyle("h2", parent=base["Heading2"],
                                   fontName=f"{brand.font_family}-B",
                                   fontSize=14, leading=18, textColor=primary,
                                   spaceBefore=14, spaceAfter=6, keepWithNext=True)
    s["body"]    = ParagraphStyle("body", parent=base["BodyText"],
                                   fontName=brand.font_family,
                                   fontSize=10, leading=14, textColor=text,
                                   spaceAfter=6, alignment=0)
    s["small"]   = ParagraphStyle("small", parent=s["body"],
                                   fontSize=8, leading=11, textColor=muted)
    s["num"]     = ParagraphStyle("num", parent=s["body"], alignment=2)  # right-aligned
    return s
```

## Page chrome callbacks

```python
def _body_chrome(brand, tenant):
    def draw(canvas, doc):
        canvas.saveState()
        # Header bar
        canvas.setFillColor(colors.HexColor(brand.primary))
        canvas.rect(0, A4[1]-20*mm, A4[0], 20*mm, stroke=0, fill=1)
        # Logo left
        canvas.drawImage(str(brand.logo_path), 18*mm, A4[1]-17*mm,
                         width=30*mm, height=10*mm,
                         preserveAspectRatio=True, mask="auto")
        # Tenant name right
        canvas.setFillColor(colors.white)
        canvas.setFont(f"{brand.font_family}-B", 9)
        canvas.drawRightString(A4[0]-18*mm, A4[1]-12*mm, tenant.name)
        # Footer
        canvas.setFillColor(colors.HexColor(brand.muted))
        canvas.setFont(brand.font_family, 8)
        canvas.drawString(18*mm, 12*mm, brand.footer_tagline or "")
        canvas.drawRightString(A4[0]-18*mm, 12*mm, f"Page {doc.page}")
        canvas.restoreState()
    return draw

def _cover_chrome(brand, tenant):
    def draw(canvas, doc):
        # Minimal: logo centered high, no header bar.
        canvas.saveState()
        canvas.drawImage(str(brand.logo_path), A4[0]/2 - 25*mm, A4[1]-45*mm,
                         width=50*mm, height=20*mm,
                         preserveAspectRatio=True, mask="auto")
        canvas.restoreState()
    return draw
```

## Financial statement table

The canonical reportlab table. Right-aligned numbers, sub-totals with rules, total row with double rule, striped body, repeatable header row.

```python
def financial_table(rows, brand, s):
    data = [["Account", "This Period", "Prior Period", "Variance", "%"]]
    data.extend(rows)

    col_widths = [70*mm, 25*mm, 25*mm, 25*mm, 15*mm]
    t = Table(data, colWidths=col_widths, repeatRows=1)

    primary = colors.HexColor(brand.primary)
    grid = colors.HexColor("#E5E7EB")
    zebra = colors.HexColor("#F9FAFB")

    style = TableStyle([
        # Header row
        ("BACKGROUND",  (0,0), (-1,0), primary),
        ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
        ("FONTNAME",    (0,0), (-1,0), f"{brand.font_family}-B"),
        ("FONTSIZE",    (0,0), (-1,0), 9),
        ("ALIGN",       (1,0), (-1,0), "RIGHT"),
        ("BOTTOMPADDING", (0,0), (-1,0), 6),
        ("TOPPADDING",    (0,0), (-1,0), 6),
        # Body
        ("FONTNAME",    (0,1), (-1,-1), brand.font_family),
        ("FONTSIZE",    (0,1), (-1,-1), 9),
        ("ALIGN",       (1,1), (-1,-1), "RIGHT"),
        ("LINEBELOW",   (0,0), (-1,-1), 0.25, grid),
        # Zebra striping on even rows
        *[("BACKGROUND", (0, r), (-1, r), zebra) for r in range(2, len(data), 2)],
        # Total row (last)
        ("FONTNAME",    (0,-1), (-1,-1), f"{brand.font_family}-B"),
        ("LINEABOVE",   (0,-1), (-1,-1), 1.0, colors.black),
        ("LINEBELOW",   (0,-1), (-1,-1), 1.5, colors.black),
        ("TOPPADDING",  (0,-1), (-1,-1), 6),
    ])
    t.setStyle(style)
    return t
```

Format numbers before you hand them to the `Table` — reportlab has no number-formatter. Use `f"{value:,.2f}"` or `f"{value:+,.2f}"` for variance columns.

## Multi-column layout

Two frames side by side on a single page (for long narrative text, glossaries, dense specs).

```python
from reportlab.platypus import Frame, PageTemplate

def _two_col_template(doc, brand, tenant):
    gap = 8*mm
    col_w = (doc.width - gap) / 2
    left = Frame(doc.leftMargin, doc.bottomMargin, col_w, doc.height, id="left")
    right = Frame(doc.leftMargin + col_w + gap, doc.bottomMargin, col_w, doc.height, id="right")
    return PageTemplate(id="twocol", frames=[left, right], onPage=_body_chrome(brand, tenant))
```

Flowables will fill the left frame first, then the right, then page-break.

## KeepTogether

Stop orphan table headers, split-image captions, broken KPI blocks.

```python
block = KeepTogether([
    Paragraph("Revenue breakdown", s["h2"]),
    Spacer(1, 4),
    financial_table(rows, brand, s),
    Spacer(1, 3),
    Paragraph("Source: general ledger, close of period.", s["small"]),
])
story.append(block)
```

Rule: any chart + caption pair, any table + immediate summary paragraph, any subtitle + following content — wrap in `KeepTogether`.

## Bookmarks and outlines

```python
from reportlab.platypus import Paragraph

class BookmarkedPara(Paragraph):
    def __init__(self, text, style, bookmark=None, level=0):
        super().__init__(text, style)
        self.bookmark = bookmark
        self.level = level

    def draw(self):
        super().draw()
        if self.bookmark:
            key = self.bookmark
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(self.bookmark, key, level=self.level, closed=False)
```

Then use `BookmarkedPara("Executive Summary", s["h2"], bookmark="sec_exec", level=0)` to produce a navigable outline (sidebar bookmarks in Acrobat).

## Images

```python
from PIL import Image as PILImage

def fit_image(path, max_w_mm, max_h_mm):
    with PILImage.open(path) as im:
        w, h = im.size
    ratio = min(max_w_mm*mm / w, max_h_mm*mm / h)
    return Image(str(path), width=w*ratio, height=h*ratio, mask="auto")
```

Always `mask="auto"` for PNGs with alpha. Without it, transparent areas render black.

## Links and anchors

```python
from reportlab.lib import utils

# External link.
p = Paragraph('<link href="https://example.com" color="blue">See terms</link>', s["body"])

# Internal link to a bookmarked page.
p = Paragraph('<a href="#sec_exec" color="blue">Executive Summary</a>', s["body"])
```

## Performance rules

- Pre-build `TableStyle` once and reuse across tables — avoids re-allocating style commands.
- Register fonts once per process; re-registration leaks memory.
- For a 100-page audit report, pass `repeatRows=1` and avoid custom flowables that call `Paragraph` in `wrap()`.
- Use `Image` with pre-sized PNGs; do not hand a 4000 px raster to ReportLab and let it downsample.

## Anti-patterns

- Dropping to raw `canvas.Canvas` for a whole report — fragile, fights pagination.
- Rendering a huge table as one `Table` flowable on a single page — use `repeatRows=1` so ReportLab paginates for you.
- Setting global state in `onPage` (e.g., changing default font) — callbacks run per page and drift.
- Embedding 2 MB logos per report — cache the `Image` or pre-resize.
- Using `Paragraph` for every table cell — slow. Use plain strings and a `TableStyle`.
- Forgetting `canvas.saveState()` / `restoreState()` in chrome callbacks — stroke colour leaks into body content.
