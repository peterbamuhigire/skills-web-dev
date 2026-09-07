---
name: professional-word-output
description: Use when generating or validating a professionally structured and visually intentional Microsoft Word DOCX document.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Professional Word Output
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.


## Required Inputs

| Input | Required | Use |
|---|---|---|
| Decision, audience, and deliverable | yes | Bound the business outcome |
| Source evidence, constraints, and owner | yes | Ground recommendations and accountability |
| Approved budget, customer data, or production artefacts | conditional | Support high-impact execution |

## Capability and permission contract

Default to read-only analysis and drafting. Do not publish, send, price, promise, alter customer records, commit budget, or modify production artefacts without explicit authority and a named approver. Minimise confidential data, preserve provenance, and keep reversible copies.

## Degraded mode

If evidence, stakeholder decisions, specialist tooling, or authoritative commercial data are unavailable, deliver a labelled draft, checklist, or decision memo. State what was not verified and do not claim approval, publication, financial accuracy, or customer acceptance.

## Decision rules

| Condition | Action | Stop condition |
|---|---|---|
| Output creates a commercial, customer, or delivery commitment | Obtain named approval before release | Authority or terms are unclear |
| Evidence supports a reversible draft | Produce it with assumptions and owner | Required evidence conflicts |
| Tooling or data is incomplete | Specify validation | A final executable artefact is expected |

## Domain Anti-Patterns

- Inventing customer evidence, prices, benchmarks, or approvals. Fix: cite the source or mark the gap.
- Publishing or sending a draft without authority. Fix: retain draft status and name the approver.
- Hiding assumptions inside polished prose. Fix: expose them beside each affected decision.
- Polishing presentation while the decision remains unclear. Fix: resolve audience, owner, and acceptance criteria.
- Treating unavailable tooling as passed validation. Fix: record the unassessed check.


<!-- dual-compat-start -->
## Use When

- Generate world-class, professionally designed Microsoft Word (.docx) documents that look like a designer and communications specialist worked on them together — not AI output. Use when producing any .docx file: reports, proposals, manuals...

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Release evidence | Generated Word document | Branded .docx artefact compliant with the professional-word-output design standard | `docs/output/report-2026-04-16.docx` |

## References

- [English output standard](../../../docs/continuous-improvement/english-output-standard-2026-09-02.md) for human-facing prose, collocation, register, terminology, and proof.

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Two things kill document quality equally: bad design and bad writing. A document must pass **both** tests. This skill addresses both.

**Reference files (read when needed):**
- `references/typography-layout.md` — fonts, spacing, margins, colour palettes, visual hierarchy
- `references/written-communication.md` — structure, clarity, tone, anti-patterns
- `references/word-features.md` — styles, TOC, tables, images, sections, cover pages, watermarks
- `references/quality-checklist.md` — pre-delivery checklist (run before every delivery)

---

## The Standard

Every document produced must pass this bar: **a professional communications specialist and a document designer would both be satisfied**. This means:

1. Every typographic decision is intentional and consistent
2. The writing is clear, structured, and free of AI-slop vocabulary
3. Navigation elements (TOC, headers/footers, page numbers) are complete and correct
4. Visual hierarchy guides the reader without effort
5. The document looks the same on any machine (styles, not direct formatting)

---

## Production Pipeline

Documents are produced via **Pandoc + python-docx + reference.docx template**:

```
Markdown source (structured content)
    ↓ pandoc --reference-doc=templates/reference.docx
.docx (styles applied from reference.docx)
    ↓ manual python-docx post-processing (cover page, TOC, header/footer)
Final .docx → PDF export
```

Before using LibreOffice for a background PDF export or render, load `document-spreadsheet-tooling-readiness` and follow its isolated-profile, cross-platform conversion contract. Do not construct a raw `soffice` command or reuse the interactive user's LibreOffice profile.

### Project export contract

Every project that generates `.docx` deliverables must include these project-root paths:

- `projects/<ProjectName>/export/`
- `projects/<ProjectName>/export-docs.ps1`
- `projects/<ProjectName>/export-docs.sh`

Build `.docx` files in their canonical phase folders first. Then run the project export script so `export/` contains a flat copy of every generated Word deliverable, excluding files already inside `export/`.

### Build commands

```bash
# Single document
pandoc source.md -o output.docx --reference-doc=templates/reference.docx

# With table of contents
pandoc source.md -o output.docx --reference-doc=templates/reference.docx --toc --toc-depth=3

# Rebuild reference.docx from scratch
python scripts/create-reference-docx.py
```

---

## Style System

Pandoc maps Markdown elements to named Word styles in reference.docx. **Never bypass this with direct formatting.**

| Markdown element | Word style |
|---|---|
| `# Heading` | Heading 1 |
| `## Heading` | Heading 2 |
| `### Heading` | Heading 3 |
| `#### Heading` | Heading 4 |
| Body paragraph | Normal |
| `` ```code block``` `` | Source Code / Verbatim |
| `` `inline code` `` | Verbatim Char |
| `> blockquote` | Block Text |
| Table | Table Grid |
| YAML `title:` | Title |
| YAML `subtitle:` | Subtitle |
| `*Caption*` below figure/table | Caption |

**If a style needs to change, change it in reference.docx — never in the document directly.**

---

## Heading Flow & Page Break Rules

These rules are **mandatory**. They determine how the document breathes across pages and whether the reader can follow the structure without effort.

### Rule 1 — Heading 1 always starts a new page

Every `# Heading 1` forces a page break before it. Major sections never share a page with the section that precedes them. This makes the document scannable: readers flipping through pages immediately see where each chapter/section begins.

**Word setting:** Paragraph → Line and Page Breaks → **Page break before = ON**

**python-docx:**
```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

h1 = doc.styles['Heading 1']
h1.paragraph_format.page_break_before = True
h1.paragraph_format.keep_with_next = True   # heading never orphaned alone
```

### Rule 2 — Heading 2 and Heading 3 stay with their first paragraph

If the heading plus its first following paragraph do not **entirely fit** on the current page, the whole unit moves to the next page. A heading that appears at the bottom of a page with its content on the next page is a design failure.

**Word settings on Heading 2 and Heading 3:**
- Paragraph → Line and Page Breaks → **Keep with next = ON**
- Paragraph → Line and Page Breaks → **Keep lines together = ON**

**Word setting on Normal / body paragraphs:**
- Paragraph → Line and Page Breaks → **Keep lines together = ON**

This combination means: the heading is glued to the paragraph that follows it, and that paragraph will not be split across pages. If the pair doesn't fit, both move to the next page.

**python-docx:**
```python
for style_name in ['Heading 2', 'Heading 3']:
    style = doc.styles[style_name]
    style.paragraph_format.keep_with_next = True
    style.paragraph_format.keep_together = True

# Body paragraphs: never split mid-paragraph
doc.styles['Normal'].paragraph_format.keep_together = True
```

### Rule 3 — Widow and orphan control is always on

No paragraph's first line appears alone at the bottom of a page (orphan), and no paragraph's last line appears alone at the top of a page (widow).

**Word setting:** Paragraph → Line and Page Breaks → **Widow/Orphan control = ON** (this is the Word default but must be confirmed in reference.docx).

```python
doc.styles['Normal'].paragraph_format.widow_control = True
```

### Summary table — paragraph flow settings per style

| Style | Page break before | Keep with next | Keep lines together | Widow/orphan |
|---|---|---|---|---|
| Heading 1 | **ON** | ON | — | — |
| Heading 2 | OFF | **ON** | **ON** | — |
| Heading 3 | OFF | **ON** | **ON** | — |
| Heading 4 | OFF | ON | ON | — |
| Normal | OFF | OFF | **ON** | **ON** |
| Body Text | OFF | OFF | **ON** | **ON** |
| Caption | OFF | OFF | OFF | OFF |

### What this looks like in the document

- Opening a document and scanning: each major section (H1) occupies its own visual territory — top of a fresh page
- Reading through body content: the eye never arrives at an H2/H3 sitting stranded at the bottom of a page; the heading is always above its content
- Short paragraphs never lose their first or last line to a page break
- The result is a document that reads like it was **typeset**, not generated

---

## Typography Specification

Read `references/typography-layout.md` for full font stacks and spacing tables. The standard corporate stack:

| Element | Font | Size | Colour |
|---|---|---|---|
| Title | Calibri Light | 28pt Bold | #1F3864 |
| Heading 1 | Calibri Light | 16pt Bold | #1F3864 |
| Heading 2 | Calibri Light | 13pt Bold | #2E5D8A |
| Heading 3 | Calibri | 11pt Bold | #4472C4 |
| Body / Normal | Calibri | 11pt Regular | #262626 |
| Code | Consolas | 9.5pt Regular | #1A1A1A |
| Caption | Calibri | 9pt Regular | #595959 |
| Header/Footer | Calibri | 9pt Regular | #595959 |

**Heading 1 visual anchor:** 4.5pt navy left border bar — applied via style paragraph border, not manual formatting.

---

## Spacing Rules

**Never press Enter twice to create space.** Use style space-after settings.

| Style | Before | After | Line |
|---|---|---|---|
| Heading 1 | 20pt | 6pt | Single |
| Heading 2 | 14pt | 4pt | Single |
| Heading 3 | 10pt | 3pt | Single |
| Normal | 0pt | 6pt | 1.15× |

---

## Document Structure (every document)

### 1. Cover Page

```yaml
---
title: "Project Name — Document Title"
subtitle: "Document Type — Category"
date: "YYYY-MM-DD"
version: "1.0"
status: "Draft | Review | Final"
---
```

Followed immediately by an ownership table:

```markdown
| | |
|---|---|
| **Project** | Project Name |
| **Owner** | Organisation Name |
| **Author** | Author Name |
| **Version** | 1.0 Draft |
| **Date** | 2026-04-05 |
| **Classification** | Confidential — Internal Use Only |
```

Cover page has no header/footer (set `different_first_page_header_footer = True`).

### 2. Table of Contents

Required for all documents longer than 5 pages. Generated automatically from Heading 1/2/3 styles.

### 3. Body Content

Three-part structure at every level:
- **Introduction** — context and purpose (what this section covers)
- **Development** — main content, evidence, detail
- **Conclusion** — key takeaway or next action

### 4. Headers and Footers

**Header:** Document title (field) right-aligned, thin grey rule below.

**Footer:** "Page X of Y" centred, confidentiality notice left, print date right.

---

## Table Design

Tables must look designed, not dumped. Read `references/word-features.md` → Tables section.

```markdown
| Column A | Column B | Column C |
|---|---|---|
| Data | Data | Data |
```

**Standard table spec:**
- Header row: Navy fill (#1F3864), white bold 10pt text
- Banded rows: light blue tint (#F2F7FD) / white alternating
- Outside border: 1pt, #1F3864
- Inside grid: 0.5pt, #BBBBBB
- Caption below every table: "Table N: Description"
- Header row repeats on every page for tables spanning multiple pages

---

## Images and Figures

- Every figure needs a caption below: "Figure N: Description" (Caption style)
- Apply a 1pt grey border (#CCCCCC) to framed figures
- Minimum 150 DPI for print documents
- Use PNG for diagrams; JPEG for photographs
- Never stretch images — use corner handles only

---

## Written Communication Standards

Read `references/written-communication.md` for full guidance. Core rules:

**Structure:** Inverted pyramid — most important information first, at every level (document, section, paragraph, sentence).

**Sentences:** 15–20 words average. One idea per sentence. Active voice.

**Never use:**
- "Delve into", "leverage", "robust", "seamlessly", "in today's landscape"
- Vague adjectives without metrics ("fast", "powerful", "intuitive")
- Passive voice for instructions ("The button should be clicked" → "Click the button")
- Undefined acronyms on first use
- Numbered lists for non-sequential items
- Bullet lists for sequential steps

**Always include:**
- Clear topic sentence opening every section
- Logical connectors at paragraph transitions
- Examples to illustrate abstract claims
- Measurable specifics in place of vague adjectives

---

## Cover Page Design Principles

A professional cover page contains:

1. **Brand bar** — full-width colour block (1.5–2 cm height), primary brand colour
2. **Company logo** — top-left or centred within brand bar
3. **Document title** — 28–36pt, Light weight, high contrast against background
4. **Subtitle and metadata** — version, date, status
5. **Ownership table** — structured metadata block
6. **No header/footer** — the cover page IS the identifier

---

## Watermarks

Apply when document status requires it:
- **DRAFT** — grey diagonal, 50% transparency, 80pt Calibri Semi-Bold
- **CONFIDENTIAL** — grey diagonal, same spec
- **INTERNAL USE ONLY** — same spec

Insert: Design → Page Background → Watermark → Custom Watermark.

---

## Markdown Source Quality Rules

These patterns degrade Word output — do not use them:

| Bad pattern | Why | Fix |
|---|---|---|
| `*` for bullet lists | Inconsistent in some Pandoc builds | Use `-` only |
| Setext headings (`---` underline) | Ambiguous, not parsed correctly | Use `#` ATX only |
| Code blocks inside table cells | Breaks table rendering | Move code outside tables |
| Raw HTML tags | Does not render in .docx | Use Markdown equivalents |
| `**bold**` + `*italic*` combined | Inconsistent output | Use one or the other |
| Blank lines instead of spacing | Creates erratic spacing | Let styles handle space |

---

## Pre-Delivery

Before every delivery, run `references/quality-checklist.md` in full. The minimum final actions:

1. `Ctrl+A → F9` — update all fields (TOC, page numbers, dates)
2. Review → Spelling & Grammar — fix all issues
3. File → Info → Inspect Document — remove comments, tracked changes, metadata
4. File → Print → verify print preview (no widows, no blank pages)
5. Export PDF with accessibility tags enabled
6. Name file: `ProjectName_DocumentType_v1.0_YYYY-MM-DD.docx`

When the PDF was produced by LibreOffice, retain the readiness result and conversion diagnostics with the delivery evidence, then inspect the rendered output rather than assuming the DOCX layout survived export.

---

## Customisation Reference

To change global document styling, edit `scripts/create-reference-docx.py`:

| What to change | Location in script |
|---|---|
| Heading colours | `NAVY`, `STEEL`, `ACCENT` constants |
| Body/heading font | `FONT_BODY`, `FONT_HEADING` constants |
| Code font | `FONT_CODE` constant |
| Heading 1 border weight | `sz` attribute in `pBdr` block |
| Footer content | `footer` section |
| Page size and margins | `section.left_margin` etc. |

Rebuild after changes:
```bash
python scripts/create-reference-docx.py
bash scripts/build-doc.sh <doc-dir> <output-name>
```
## Quality Standards

Release only after semantic structure, fields, tables, headers, pagination, accessibility, and final rendered pages have been inspected in the target format.

## Outputs

| Artefact | Consumer | Acceptance condition |
|---|---|---|
| Render-verified DOCX and validation note | Named document recipient | Styles are semantic, pagination and tables survive rendering, accessibility properties are present, and no placeholder or hidden revision ships |
