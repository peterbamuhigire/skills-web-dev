# Word Documents with python-docx

Branded letterhead reports, proposals, certificates, and audit exports. `python-docx` covers most needs; a small set of OXML helpers covers the rest.

## Library scope

```python
from docx import Document
from docx.shared import Pt, Cm, Mm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION, WD_ORIENTATION
from docx.oxml.ns import qn, nsmap
from docx.oxml import OxmlElement
```

`python-docx` exposes paragraphs, runs, tables, sections, headers, footers, styles, and images directly. For page borders, complex headers, table cell shading, and watermarks, drop to OXML via `element` / `_element`.

## Document skeleton

```python
def build_report(path, tenant, brand, data):
    doc = Document()
    configure_styles(doc, brand)
    configure_page(doc)
    build_header_footer(doc, tenant, brand)
    build_title_page(doc, tenant, brand, data)
    doc.add_page_break()
    build_body(doc, brand, data)
    doc.save(path)
```

## Page setup

```python
def configure_page(doc):
    for section in doc.sections:
        section.page_height = Mm(297)
        section.page_width = Mm(210)
        section.orientation = WD_ORIENTATION.PORTRAIT
        section.top_margin = Mm(25)
        section.bottom_margin = Mm(22)
        section.left_margin = Mm(22)
        section.right_margin = Mm(22)
        section.header_distance = Mm(10)
        section.footer_distance = Mm(10)
        section.different_first_page_header_footer = True
```

`different_first_page_header_footer = True` enables the first-page-different behaviour used by letterheads (no page number on the cover).

## Styles setup

Map your brand type scale onto Word styles. Do this once per document; reuse by name from body code.

```python
def configure_styles(doc, brand):
    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = brand.font_family
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor.from_string(brand.text.lstrip("#"))
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.35

    for level, size in [(1, 20), (2, 15), (3, 12)]:
        s = styles[f"Heading {level}"]
        s.font.name = brand.font_family
        s.font.size = Pt(size)
        s.font.bold = True
        s.font.color.rgb = RGBColor.from_string(brand.primary.lstrip("#"))
        s.paragraph_format.space_before = Pt(16 if level == 1 else 12)
        s.paragraph_format.space_after = Pt(6)
        s.paragraph_format.keep_with_next = True

    caption = styles["Caption"]
    caption.font.name = brand.font_family
    caption.font.size = Pt(9)
    caption.font.italic = True
    caption.font.color.rgb = RGBColor.from_string(brand.muted.lstrip("#"))
```

## Header with logo + tenant name

```python
def build_header_footer(doc, tenant, brand):
    section = doc.sections[0]

    # Main header (pages 2+).
    header = section.header
    p = header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run()
    run.add_picture(str(brand.logo_path), height=Mm(10))
    tab = p.add_run(f"\t{tenant.name}")
    tab.font.name = brand.font_family
    tab.font.size = Pt(9)
    tab.font.color.rgb = RGBColor.from_string(brand.muted.lstrip("#"))
    _set_bottom_border(p, brand.primary)

    # First-page header empty (letterhead style).
    first = section.first_page_header
    first.paragraphs[0].clear()

    # Footer: left tagline, right "Page X of Y".
    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r1 = fp.add_run(brand.footer_tagline)
    r1.font.size = Pt(8)
    r1.font.color.rgb = RGBColor.from_string(brand.muted.lstrip("#"))
    fp.add_run("\t\t")
    _append_page_field(fp)
```

### Page number field (PAGE of NUMPAGES)

python-docx exposes fields via OXML only.

```python
def _append_page_field(paragraph):
    run = paragraph.add_run()
    run.font.size = Pt(8)
    _add_field(run, "PAGE")
    run2 = paragraph.add_run(" of ")
    run2.font.size = Pt(8)
    run3 = paragraph.add_run()
    run3.font.size = Pt(8)
    _add_field(run3, "NUMPAGES")

def _add_field(run, instr: str):
    fld_char_begin = OxmlElement("w:fldChar")
    fld_char_begin.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = instr
    fld_char_end = OxmlElement("w:fldChar")
    fld_char_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char_begin)
    run._r.append(instr_text)
    run._r.append(fld_char_end)
```

### Header bottom border

```python
def _set_bottom_border(paragraph, hex_color: str):
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "8")          # quarter-points
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), hex_color.lstrip("#"))
    pBdr.append(bottom)
    pPr.append(pBdr)
```

## Title page

```python
def build_title_page(doc, tenant, brand, data):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run()
    run.add_picture(str(brand.logo_path), height=Mm(18))

    for _ in range(4):
        doc.add_paragraph()

    title = doc.add_paragraph(data["title"], style="Heading 1")
    title.paragraph_format.space_before = Pt(0)

    sub = doc.add_paragraph(f"{tenant.name} — {data['period']}")
    sub.runs[0].font.size = Pt(13)
    sub.runs[0].font.color.rgb = RGBColor.from_string(brand.muted.lstrip("#"))

    meta = doc.add_paragraph()
    meta.add_run(f"Prepared by: {data['author']}").font.size = Pt(10)
    meta.add_run(f"\nDate: {data['date']:%d %B %Y}").font.size = Pt(10)
```

## Body patterns

### Paragraph of body text

```python
doc.add_paragraph("Executive summary paragraph explaining the reporting period...")
```

### Bullet and numbered lists

python-docx does not expose a list API. Use the built-in `List Bullet` and `List Number` styles.

```python
for point in ["Revenue grew 8.2%", "Churn held at 2.1%", "NPS moved from 41 to 46"]:
    doc.add_paragraph(point, style="List Bullet")

for step in ["Extract", "Validate", "Load", "Reconcile"]:
    doc.add_paragraph(step, style="List Number")
```

### Hyperlinks

OXML helper (no native API).

```python
def add_hyperlink(paragraph, url: str, text: str, brand):
    part = paragraph.part
    r_id = part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)
    new_run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), brand.primary.lstrip("#"))
    rPr.append(color)
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rPr.append(u)
    new_run.append(rPr)
    t = OxmlElement("w:t")
    t.text = text
    new_run.append(t)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)
```

## Tables with header shading

```python
def add_data_table(doc, brand, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Light Grid Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.autofit = False

    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        c = hdr_cells[i]
        c.text = ""
        p = c.paragraphs[0]
        run = p.add_run(h)
        run.bold = True
        run.font.color.rgb = RGBColor.from_string("FFFFFF")
        run.font.size = Pt(10)
        _shade_cell(c, brand.primary)
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    for r_idx, row in enumerate(rows, start=1):
        cells = table.rows[r_idx].cells
        for c_idx, val in enumerate(row):
            cells[c_idx].text = str(val)
            if r_idx % 2 == 0:
                _shade_cell(cells[c_idx], "F3F4F6")  # zebra
    return table

def _shade_cell(cell, hex_color: str):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color.lstrip("#"))
    tcPr.append(shd)
```

Autofit rules of thumb: set column widths explicitly on the first row's cells (`cell.width = Cm(...)`), then lock `table.autofit = False`. Word will honour your widths if no cell content overflows.

## Embedding matplotlib charts

```python
def insert_chart(doc, png_path, caption_text, brand):
    doc.add_picture(str(png_path), width=Mm(160))
    last = doc.paragraphs[-1]
    last.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap = doc.add_paragraph(caption_text, style="Caption")
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
```

Render with matplotlib at `dpi=200` for print crispness. See `charts-for-embedding.md`.

## Section breaks

```python
def add_landscape_section(doc):
    section = doc.add_section(WD_SECTION.NEW_PAGE)
    section.orientation = WD_ORIENTATION.LANDSCAPE
    section.page_width, section.page_height = section.page_height, section.page_width
    return section
```

Used for wide tables or full-width charts inside an otherwise portrait report.

## Page borders (OXML only)

python-docx has no API for page borders. Use OXML:

```python
def set_page_border(section, hex_color: str, size_quarterpt: int = 8):
    sectPr = section._sectPr
    pgBorders = OxmlElement("w:pgBorders")
    pgBorders.set(qn("w:offsetFrom"), "page")
    for side in ("top", "left", "bottom", "right"):
        b = OxmlElement(f"w:{side}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), str(size_quarterpt))
        b.set(qn("w:space"), "24")
        b.set(qn("w:color"), hex_color.lstrip("#"))
        pgBorders.append(b)
    sectPr.append(pgBorders)
```

## Watermark

Also OXML. Typically easier to render a faint diagonal text via a `v:shape` element inside the header. Most production reports skip watermarks and use a footer string ("Confidential — <tenant>") instead. Simpler, equally effective, renders reliably everywhere.

## Field refresh on open

Fields (`PAGE`, `NUMPAGES`, TOC) show "0" until Word refreshes. Force update-on-open:

```python
def _force_update_fields_on_open(doc):
    settings = doc.settings.element
    update = OxmlElement("w:updateFields")
    update.set(qn("w:val"), "true")
    settings.append(update)
```

## Anti-patterns

- Building everything as `add_paragraph().add_run()` without using styles — a format change becomes a 200-edit chore.
- Writing the same header code for every section — wrap it in a helper keyed to `Brand`.
- Using images at native 4000 px width — bloats the file. Resize to 1600 px max before `add_picture`.
- Assuming `table.autofit = True` will produce Excel-like column sizing — it rarely does. Set widths.
- Relying on Word to open fine everywhere — test in Word (Windows + macOS) and LibreOffice. OXML quirks surface here.
