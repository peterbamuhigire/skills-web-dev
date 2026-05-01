# Word Features for Professional Output

*Sources: Wempen — Advanced Microsoft Word 2016; Vic — Microsoft Word 2022; Jordan — ICDL Word*

---

## Table of Contents

1. [Styles System](#styles-system)
2. [Headers and Footers](#headers-and-footers)
3. [Table of Contents (TOC)](#table-of-contents-toc)
4. [Tables](#tables)
5. [Images and Figures](#images-and-figures)
6. [Section Breaks and Page Layout](#section-breaks-and-page-layout)
7. [Cover Pages](#cover-pages)
8. [Watermarks](#watermarks)
9. [SmartArt and Diagrams](#smartart-and-diagrams)
10. [Document Finishing](#document-finishing)

---

## Styles System

### The Core Rule

> "Every visual property — font, size, colour, spacing, border — should live in a named style. Direct formatting is the enemy of consistency." — *Advanced Microsoft Word 2016*

### Three Types of Styles

| Type | Affects | Example |
|---|---|---|
| Paragraph style | Entire paragraph + text within | Normal, Heading 1, Body Text |
| Character style | Selected text only | Verbatim Char, Strong, Emphasis |
| Linked style | Both paragraph and character context | Most Heading styles |

### Working with the Styles Pane

- Open via Home → Styles → arrow (bottom-right of Styles group)
- **Modify a style:** Right-click → Modify → change font, colour, spacing → OK
- When you modify a style, **every paragraph using that style updates instantly**
- **New style from selection:** Format a paragraph manually → right-click → "Save Selection as New Quick Style"
- **Clear all formatting:** Select text → Home → Clear All Formatting (eraser icon)

### Style Sets

- Design tab → Document Formatting group → Style Sets
- Changing the style set changes ALL styled elements simultaneously
- Use style sets to provide quick theme variations (corporate, minimal, academic)

### Priority Order for Styles

1. Character style overrides paragraph style overrides document default
2. Direct formatting overrides all styles — this is why direct formatting is dangerous

### Page Flow Properties (mandatory for all heading styles)

These paragraph-level settings control how content flows across pages. They must be configured in reference.docx — not applied manually per document.

**Where to set in Word:** Select text using the style → Paragraph dialog (bottom-right arrow in Paragraph group) → Line and Page Breaks tab.

| Setting | What it does |
|---|---|
| **Page break before** | Forces a page break immediately before the paragraph |
| **Keep with next** | Prevents a page break between this paragraph and the one that follows |
| **Keep lines together** | Prevents a page break within the paragraph itself |
| **Widow/Orphan control** | Prevents isolated first/last lines from appearing at page edges |

**Required configuration per style:**

| Style | Page break before | Keep with next | Keep lines together | Widow/Orphan |
|---|---|---|---|---|
| Heading 1 | **ON** | ON | — | — |
| Heading 2 | OFF | **ON** | **ON** | — |
| Heading 3 | OFF | **ON** | **ON** | — |
| Heading 4 | OFF | ON | ON | — |
| Normal | OFF | OFF | **ON** | **ON** |
| Body Text | OFF | OFF | **ON** | **ON** |

**python-docx implementation in create-reference-docx.py:**

```python
# Heading 1: always starts a new page, never orphaned
h1 = doc.styles['Heading 1']
h1.paragraph_format.page_break_before = True
h1.paragraph_format.keep_with_next = True

# Heading 2 and 3: glued to their first paragraph; both move if they don't fit
for name in ['Heading 2', 'Heading 3', 'Heading 4']:
    s = doc.styles[name]
    s.paragraph_format.keep_with_next = True
    s.paragraph_format.keep_together = True

# Body paragraphs: never split mid-paragraph
for name in ['Normal', 'Body Text']:
    s = doc.styles[name]
    s.paragraph_format.keep_together = True
    s.paragraph_format.widow_control = True
```

**Why this matters:** Without these settings, Word may place a Heading 2 at the very bottom of a page with its content on the next — visually broken. A document with correct page flow settings reads as if it was typeset, not generated.

---

## Headers and Footers

### Purpose

Headers and footers appear on every page. They provide document identity without consuming body content space.

### Standard Professional Configuration

**Header (top margin):**
- Left: Company logo or name (optional)
- Centre: Document title (use field: Insert → Field → Title)
- Right: Project code or classification
- Bottom rule: thin grey horizontal line (0.5pt, colour #BBBBBB)

**Footer (bottom margin):**
- Left: Confidentiality notice (e.g., "Confidential — Internal Use Only")
- Centre: Page X of Y (use fields: PAGE and NUMPAGES)
- Right: Date (use field: DATE with fixed format)

### Implementation in python-docx / Pandoc

```python
# python-docx: set different first page
section = document.sections[0]
section.different_first_page_header_footer = True
# First page header/footer is separate from body header/footer
```

### Critical Settings

- **Different First Page:** Hides header/footer on the cover page. Always enable for documents with a cover.
- **Link to Previous:** When ON, section inherits previous section's header/footer. Turn OFF when you need different content.
- **Page numbering restart:** In Section properties, set "Start at: 1" for each major section if needed.

### Field Codes for Dynamic Content

| Purpose | Field code |
|---|---|
| Document title | `{ TITLE }` |
| Current page number | `{ PAGE }` |
| Total page count | `{ NUMPAGES }` |
| Auto-update date | `{ DATE \@ "d MMMM yyyy" }` |
| Author name | `{ AUTHOR }` |
| Filename | `{ FILENAME \p }` |

---

## Table of Contents (TOC)

### Requirements

A TOC only works correctly when headings use **Heading 1, Heading 2, Heading 3 paragraph styles** — not bold text, not manually sized text.

### Insert a TOC

References tab → Table of Contents → Choose a style, or → Custom Table of Contents

### TOC Configuration Options

- **Show levels:** Set to 3 for most documents (H1, H2, H3). Set to 2 for shorter documents.
- **Tab leader:** .......... (dots) is standard for formal documents. Use none for minimal/modern look.
- **Page number alignment:** Always right-align page numbers.
- **Formats:** "Formal" or "Modern" styles render well in professional documents.

### Updating the TOC

Right-click the TOC → Update Field → Update entire table (always choose "entire table" to capture heading text changes).

### Manual TOC Entry

For appendices or items not using heading styles: References → Add Text → set level, or use TC field codes.

---

## Tables

### The Designer's Approach to Tables

Tables are not just data containers — they are visual elements. A poorly formatted table degrades the document's professionalism as much as bad typography.

### Table Style Configuration

After inserting a table: Table Design tab →
- **Header Row:** ON — applies distinct formatting to row 1
- **Banded Rows:** ON — alternating row shading improves scannability
- **First Column:** ON only if the first column contains row labels

### Professional Table Style Stack

| Element | Specification |
|---|---|
| Header row fill | #1F3864 (Navy) or brand primary |
| Header row text | White, 10pt Bold |
| Banded row fill | #F2F7FD (very light blue) / white alternating |
| Body text | 10pt Regular, #262626 |
| Border (outside) | 1pt solid, #1F3864 |
| Border (inside) | 0.5pt solid, #BBBBBB |
| Cell padding | 0.1 cm top/bottom, 0.2 cm left/right |

### Table Layout Rules

- **Column widths** should be proportional to content, not equal. A "Name" column needs less width than a "Description" column.
- **Never let Word auto-fit to window** for complex tables — set fixed column widths via Table Layout → Cell Size.
- **Avoid merging cells gratuitously** — merged cells break sort operations and confuse screen readers.
- **Caption below every table:** "Table 1: [Description]" — use the Caption paragraph style.
- **Long tables:** Repeat header row on every page. Table Layout → Properties → Row → "Repeat as header row at the top of each page."

### Converting Text to Table

Select text separated by tabs → Insert → Table → Convert Text to Table → set column count = number of tabs per line.

---

## Images and Figures

### Placement Rules

- **Inline with text** for figures that are referenced in the body ("as shown in Figure 1")
- **Floating with tight wrap** for decorative or supplementary visuals
- **Behind text** only for page background effects, never for informational content

### Image Quality

- Minimum 150 DPI for print documents; 72–96 DPI acceptable for screen-only
- Use PNG for diagrams with text or sharp edges (lossless)
- Use JPEG for photographs (compressed)
- Never stretch images — maintain aspect ratio. Use corner handles, not side handles.

### Caption System

Every figure in a formal document requires a caption:
- References → Insert Caption → choose "Figure" label
- Caption text: "Figure 1: [Descriptive title]"
- Style: Caption paragraph style (9pt, grey, italic)

### Image Borders

A subtle 1pt border (#CCCCCC) around figures prevents images from floating visually in white space.

---

## Section Breaks and Page Layout

### When to Use Section Breaks

| Need | Section break type |
|---|---|
| New page with independent header/footer | Next Page |
| Landscape page within portrait document | Next Page (both before and after) |
| Restart page numbering | Next Page |
| Two-column section within one-column document | Continuous |

### Landscape Pages

1. Position cursor before the page that should be landscape
2. Insert → Break → Next Page
3. Layout → Orientation → Landscape
4. Position cursor after the last landscape page
5. Insert → Break → Next Page
6. Layout → Orientation → Portrait
7. In each section, unlink the header/footer from the previous section

---

## Cover Pages

### Using Built-in Cover Pages

Insert → Pages → Cover Page → choose from gallery. These are fully editable and professionally designed.

### Custom Cover Page Elements

A world-class custom cover page includes:

1. **Company branding block** — logo (top-left), brand colour bar (full width, 1.5cm height, primary colour)
2. **Document title block** — large title (28pt+), subtitle, date
3. **Classification / ownership table** — structured metadata
4. **Version and status** — visible on cover, not buried in footer
5. **Background graphic or texture** — subtle, must not compete with text

### Cover Page Typography

- Title: 28–36pt, Light weight, white or near-white on dark background (or brand primary on white)
- Subtitle: 13–14pt, Regular or Italic
- All metadata (date, version, owner): 10–11pt Regular

### No Header/Footer on Cover

Always enable: Header & Footer → Different First Page = True. The cover page contains its own structured information; a page number on a cover page looks unprofessional.

---

## Watermarks

### When to Use

- **DRAFT** — on documents not yet approved (red or grey diagonal text)
- **CONFIDENTIAL** — on sensitive documents
- **SAMPLE** — on specimen documents
- **INTERNAL USE ONLY** — on restricted-distribution documents

### Watermark Specifications

- **Angle:** 45° diagonal (standard) or horizontal for readability
- **Transparency:** 50–65% — visible but not competing with content
- **Font:** Calibri or Arial, 80–100pt, Semi-bold
- **Colour:** Grey (#BBBBBB) for most. Red (#C00000) only for DRAFT on legal/financial documents.

### Insert via

Design tab → Page Background → Watermark → Custom Watermark → Text watermark.

---

## SmartArt and Diagrams

### When to Use SmartArt

Replace text-only lists or process descriptions when:
- Showing a workflow or process (use Process layout)
- Showing an organisation hierarchy (use Hierarchy layout)
- Showing a cycle or loop (use Cycle layout)
- Comparing items (use Matrix layout)

### SmartArt Quality Rules

- **Maximum 7 items** in any single SmartArt shape. More than 7 creates visual clutter.
- **Use the Text Pane** (left panel) to enter text — do not click directly into shapes.
- **Colour scheme:** Change Colors → choose a scheme based on your document's primary colour.
- **Style:** Use "Flat" or "Subtle Effect" styles for print. Avoid 3D effects in formal documents.
- **Font size:** SmartArt auto-sizes text. If text becomes too small (below 9pt), reduce content volume.

---

## Document Finishing

### Before Delivery Checklist Actions

1. **Update all fields:** Ctrl+A → F9 (updates TOC, page numbers, dates, cross-references)
2. **Check spelling and grammar:** Review → Spelling & Grammar
3. **Run Document Inspector:** File → Info → Check for Issues → Inspect Document
   - Remove: comments, tracked changes, hidden text, personal information
4. **Print Preview:** File → Print → preview every page
   - Check for widows/orphans (single lines at top/bottom of pages)
   - Check for blank pages
5. **Verify page numbering** is correct across all sections
6. **Save as .docx** for editable delivery; **Export to PDF** for final distribution

### Widows and Orphans

- A **widow** is the last line of a paragraph appearing alone at the top of a page
- An **orphan** is the first line of a paragraph appearing alone at the bottom of a page
- Fix via: Paragraph → Line and Page Breaks → Widow/Orphan control (always ON)
- For heading orphans: Paragraph → Line and Page Breaks → Keep with next (ON for all heading styles)

### PDF Export Settings

File → Export → Create PDF/XPS:
- **Standard** for screen/email distribution
- **Minimum size** for web upload
- Enable: "Document structure tags for accessibility"
- Disable: "Open file after publishing" (speeds up export on large documents)
