# Professional Word Document — Quality Checklist

Use this checklist before delivering any .docx or PDF. A document passes only when every item is confirmed.

---

## Heading Flow & Page Breaks (mandatory)

- [ ] Heading 1 style has **Page break before = ON** — every H1 starts a new page
- [ ] Heading 2 style has **Keep with next = ON** and **Keep lines together = ON**
- [ ] Heading 3 style has **Keep with next = ON** and **Keep lines together = ON**
- [ ] Normal / Body Text style has **Keep lines together = ON** — no paragraph split across pages
- [ ] Normal / Body Text style has **Widow/Orphan control = ON**
- [ ] No Heading 2 or Heading 3 appears stranded at the bottom of a page with its content on the next
- [ ] Scanning through the document: every H1 is at the top of a fresh page

## Design & Layout

- [ ] Document uses a named reference.docx or Word template — no direct formatting applied to body paragraphs
- [ ] Maximum two typefaces used (heading font + body font)
- [ ] Heading 1 has a visual anchor (coloured left border or distinct colour treatment)
- [ ] Heading hierarchy is consistent: H1 → H2 → H3 (no skipped levels)
- [ ] Body text line spacing is 1.15× or 1.5× — never 1.0× for long-form reading
- [ ] Paragraph spacing is controlled by style (space-after), not blank Enter presses
- [ ] Margins are appropriate for document type (2.54 cm standard; 3 cm left for bound documents)
- [ ] Colour palette limited to 3 colours (primary, secondary, neutral)
- [ ] No pure black (#000000) body text — use near-black (#262626 or #1A1A1A)
- [ ] All colour-coded information also has a non-colour differentiator (bold, pattern, etc.)

## Content Structure

- [ ] YAML front matter / cover page present with: Title, Subtitle, Date, Version, Status
- [ ] Ownership/metadata table on or immediately after cover page
- [ ] Table of Contents present for documents longer than 5 pages
- [ ] TOC updated (Ctrl+A → F9) after final content edits
- [ ] All headings use ATX style (#) — not underline setext style
- [ ] All sections have a clear opening topic sentence
- [ ] No orphaned single-sentence paragraphs
- [ ] Logical connectors used at paragraph transitions
- [ ] Conclusion present and does not introduce new information

## Tables

- [ ] Every table has a caption: "Table N: Description" using Caption style
- [ ] Header row distinct (fill colour, white bold text)
- [ ] Banded rows enabled for tables with 5+ rows
- [ ] Column widths are proportional to content (not equal)
- [ ] Header row set to repeat on every page for long tables
- [ ] No merged cells unless structurally necessary
- [ ] All tables have outside border (1pt, primary colour) and inside grid (0.5pt, grey)

## Images & Figures

- [ ] Every figure has a caption: "Figure N: Description" using Caption style
- [ ] Images are at minimum 150 DPI for print, 96 DPI for screen-only
- [ ] Aspect ratio preserved (no stretching)
- [ ] Images are inline or properly wrapped — not floating randomly
- [ ] Subtle 1pt grey border applied to framed figures

## Headers, Footers & Page Numbers

- [ ] Header contains document title (via field code, not typed text)
- [ ] Footer contains "Page X of Y" centred
- [ ] Cover page has no header/footer (Different First Page = ON)
- [ ] Page numbers correct and consistent across all sections
- [ ] Confidentiality notice in footer (if applicable)

## Writing Quality

- [ ] Document objective is clear from the first paragraph
- [ ] No AI-slop vocabulary: delve, leverage, robust, seamlessly, in today's landscape, it is worth noting
- [ ] No vague adjectives without metrics (fast, powerful, advanced, intuitive)
- [ ] All acronyms defined on first use
- [ ] Consistent terminology throughout (no alternating synonyms for the same concept)
- [ ] Active voice used for instructions and key claims
- [ ] Sentences average 15–20 words
- [ ] Numbered lists for sequential steps; bullet lists for unordered items
- [ ] Maximum 2 levels of nested lists

## Technical Word / Pandoc

- [ ] All headings use `#` ATX style (not setext/underline style)
- [ ] All bullet lists use `-` not `*`
- [ ] No raw HTML in Markdown source
- [ ] No code blocks inside table cells
- [ ] All tables have a header separator row (`|---|`)

## Finishing

- [ ] All fields updated: Ctrl+A → F9
- [ ] Spelling and grammar checked
- [ ] Document Inspector run — comments, tracked changes, and hidden text removed
- [ ] No widows or orphans (single lines isolated at page top/bottom)
- [ ] Print preview reviewed — no unexpected blank pages
- [ ] Watermark applied if document is DRAFT or CONFIDENTIAL
- [ ] Saved as .docx for editable delivery; PDF exported for final distribution
- [ ] PDF exported with accessibility tags enabled
- [ ] File named according to convention: `ProjectName_DocumentType_v1.0_YYYY-MM-DD.docx`
