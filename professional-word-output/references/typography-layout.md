# Typography & Layout Reference

*Sources: Wempen — Advanced Microsoft Word 2016; Vic — Microsoft Word 2022 for Beginners & Pros*

---

## Table of Contents

1. [Typography Principles](#typography-principles)
2. [Recommended Font Specifications](#recommended-font-specifications)
3. [Spacing & White Space](#spacing--white-space)
4. [Page Layout & Margins](#page-layout--margins)
5. [Colour in Professional Documents](#colour-in-professional-documents)
6. [Visual Hierarchy](#visual-hierarchy)

---

## Typography Principles

- **Never apply direct formatting to individual paragraphs.** Every typographic decision must live inside a named Word style. Direct formatting creates inconsistency the moment content is edited or reused.
- Use a **maximum of two typefaces** per document: one for headings (display), one for body. Three typefaces signals amateur work.
- **Serif vs. sans-serif:** sans-serif (Calibri, Aptos, Arial) reads well on screens and in short documents. Serif (Georgia, Times New Roman) is preferred for long-form print documents above 15 pages.
- **Avoid decorative or novelty fonts** in any professional context. They undermine credibility before the reader reads a single word.
- **Size hierarchy must be consistent:** each heading level should differ by at least 2pt from the level below it.
- Never use ALLCAPS in body text — use small caps (character formatting) if emphasis is required.

---

## Recommended Font Specifications

### Corporate / Business Document Stack

| Element | Font | Size | Weight | Colour |
|---|---|---|---|---|
| Document Title | Calibri Light | 28pt | Bold | #1F3864 (Navy) |
| Subtitle | Calibri | 13pt | Italic | #595959 (Mid-grey) |
| Heading 1 | Calibri Light | 16pt | Bold | #1F3864 (Navy) |
| Heading 2 | Calibri Light | 13pt | Bold | #2E5D8A (Steel) |
| Heading 3 | Calibri | 11pt | Bold | #4472C4 (Accent blue) |
| Heading 4 | Calibri | 11pt | Bold Italic | #262626 (Near-black) |
| Body / Normal | Calibri | 11pt | Regular | #262626 |
| Code / Verbatim | Consolas | 9.5pt | Regular | #1A1A1A |
| Block Quote | Calibri | 11pt | Italic | #595959 |
| Caption | Calibri | 9pt | Regular | #595959 |
| Footer / Header | Calibri | 9pt | Regular | #595959 |

### Academic / Formal Report Stack

| Element | Font | Size |
|---|---|---|
| Title | Georgia | 24pt Bold |
| Heading 1 | Georgia | 16pt Bold |
| Heading 2 | Georgia | 13pt Bold |
| Body | Georgia | 12pt Regular |
| Notes/Caption | Georgia | 10pt Italic |

---

## Spacing & White Space

> "Nothing is more discouraging than text without spaces and line breaks." — *Clear Written Communication*

White space is not wasted space — it signals confidence and readability.

### Paragraph Spacing (apply via styles, never via blank lines)

| Style | Space Before | Space After | Line Spacing |
|---|---|---|---|
| Heading 1 | 20pt | 6pt | Single |
| Heading 2 | 14pt | 4pt | Single |
| Heading 3 | 10pt | 3pt | Single |
| Normal / Body | 0pt | 6pt | 1.15× |
| Body Text (long-form) | 0pt | 8pt | 1.15× |
| Block Quote | 6pt | 6pt | 1.15× |
| Caption | 4pt | 8pt | Single |

**Rule:** Press Enter once between paragraphs. The space-after setting on the style handles the gap. Never press Enter twice to create spacing.

### Line Spacing

- **1.0** — dense, for tables, footnotes, code blocks
- **1.15** — standard body text, most professional documents
- **1.5** — long-form reading documents, academic papers
- **2.0** — draft documents requiring annotation/mark-up room

---

## Page Layout & Margins

### Standard Document Sizes

| Document Type | Page Size | Margins |
|---|---|---|
| Corporate reports, proposals | A4 (21 × 29.7 cm) | 2.54 cm all sides |
| US business documents | Letter (21.6 × 27.9 cm) | 1 inch all sides |
| Executive summary (one-pager) | A4 | 1.5 cm sides, 2 cm top/bottom |
| Formal legal / tender documents | A4 | 3 cm left (binding), 2 cm others |

### Multi-Column Layouts

- **Two-column layout:** appropriate for newsletters, brochures, reference sheets
- **Single-column:** standard for reports, proposals, manuals
- Use column breaks (Layout → Breaks → Column) to force content positioning
- Never use manual tabs to simulate columns — use actual column layout or tables

### Section Breaks for Layout Control

Use section breaks to apply different formatting to different parts of the same document:
- **Cover page** (no header/footer, different margins)
- **Landscape page** for wide tables/charts within a portrait document
- **Front matter** (Roman page numbering: i, ii, iii)
- **Body content** (Arabic page numbering: 1, 2, 3)

Insert via: Layout → Breaks → Section Breaks

---

## Colour in Professional Documents

### Colour Rules

1. **Establish a 3-colour palette max:** primary (brand/heading), secondary (accents), neutral (body text, captions).
2. **Never use colour as the only differentiator** — readers who print in greyscale lose all meaning. Use colour plus pattern/weight.
3. **Body text must always be near-black** (#262626 not #000000 — pure black is harsh on screen).
4. **Accent colour** for callout boxes, table headers, divider lines — not for body text.
5. **Avoid red for anything other than warnings/errors** in professional documents.

### Recommended Palette (Corporate Navy)

| Purpose | Colour | Hex |
|---|---|---|
| Primary headings, borders | Navy | #1F3864 |
| Secondary headings | Steel blue | #2E5D8A |
| Accent / highlights | Cornflower | #4472C4 |
| Body text | Near-black | #262626 |
| Secondary text (captions, headers) | Mid-grey | #595959 |
| Table header fills | Light navy tint | #D6E4F7 |
| Callout box background | Very light grey | #F2F2F2 |

### Greyscale-Safe Palette (formal tenders, legal)

| Purpose | Colour | Hex |
|---|---|---|
| Primary headings | Black | #000000 |
| Body text | Near-black | #1A1A1A |
| Secondary text | Dark grey | #404040 |
| Table header fills | Light grey | #D9D9D9 |
| Borders | Medium grey | #999999 |

---

## Visual Hierarchy

A reader scanning your document in 5 seconds must immediately understand:

1. What the document is (Title)
2. What the main sections are (Heading 1)
3. Where to find specific details (Heading 2/3)

**Hierarchy signals — use all of these, not just size:**

| Signal | Strong usage |
|---|---|
| Size | Larger = more important |
| Weight | Bold = emphasis |
| Colour | Branded colour = section anchor |
| Space | More space before = new major idea |
| Position | Left-indent = subordinate |
| Border | Left bar on Heading 1 = visual anchor |

**The left-border rule (Heading 1):** A 4–5pt coloured left border on every H1 paragraph provides a strong vertical rhythm that makes section divisions obvious at a glance. Apply via Paragraph → Borders → Left border, using the primary brand colour.
