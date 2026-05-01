# Excel Design Standards

*Sources: Microsoft Excel 365 Bible; Excel 2025 All-in-One Guide*

---

## Table of Contents

1. [Colour Palettes](#colour-palettes)
2. [Typography](#typography)
3. [Table Styles](#table-styles)
4. [Sheet Layout](#sheet-layout)
5. [Conditional Formatting Patterns](#conditional-formatting-patterns)
6. [Professional Finishing](#professional-finishing)
7. [Dashboard Design](#dashboard-design)

---

## Colour Palettes

### Corporate Navy (default — matches professional-word-output skill)

| Role | Name | Hex | Use |
|---|---|---|---|
| Primary | Navy | #1F3864 | Table headers, sheet titles, chart series 1 |
| Secondary | Steel | #2E5D8A | Subtotals, secondary headers |
| Accent | Cornflower | #4472C4 | Highlights, chart series 2, data bars |
| Light tint | Ice blue | #D6E4F7 | Banded row light, header fill light |
| Body text | Near-black | #262626 | All data cell text |
| Secondary text | Mid-grey | #595959 | Labels, subtitles, footnotes |
| Border | Light grey | #BFBFBF | Cell borders, gridlines |
| White | White | #FFFFFF | Banded row dark (alternating with tint) |
| Positive | Green | #375623 text / #E2EFDA fill | Positive variance, "Paid", "Complete" |
| Negative | Red | #9C0006 text / #FFC7CE fill | Negative variance, "Overdue", "Failed" |
| Warning | Amber | #7D6608 text / #FFEB9C fill | Pending, warning, "Review" |

### Minimal Greyscale (formal tenders, audits, legal)

| Role | Hex |
|---|---|
| Header fill | #404040 |
| Header text | #FFFFFF |
| Banded row | #F2F2F2 / #FFFFFF |
| Border | #BFBFBF |
| Body text | #1A1A1A |

### Financial Green (accounting, finance reports)

| Role | Hex |
|---|---|
| Header fill | #1E4620 |
| Header text | #FFFFFF |
| Banded row | #EBF3EB / #FFFFFF |
| Accent | #4CAF50 |
| Negative | #C62828 |

---

## Typography

Excel's font choices affect readability and perceived professionalism significantly.

| Element | Font | Size | Weight | Colour |
|---|---|---|---|---|
| Sheet title | Calibri Light | 18pt | Bold | #1F3864 |
| Sheet subtitle | Calibri | 11pt | Regular | #595959 |
| Table header | Calibri | 11pt | Bold | #FFFFFF |
| Data row | Calibri | 10pt | Regular | #262626 |
| Totals row | Calibri | 10pt | Bold | #262626 |
| KPI / callout value | Calibri Light | 24–36pt | Bold | Brand colour |
| KPI label | Calibri | 9pt | Regular | #595959 |
| Footnote / source | Calibri | 8pt | Italic | #595959 |

**Rules:**
- Never use more than 2 typefaces in a workbook
- Calibri (default) is appropriate for most professional Excel work
- Avoid Comic Sans, Papyrus, or any decorative font
- Bold is reserved for headers, totals, and KPI values — not random emphasis
- Never underline text in cells (underline signals a hyperlink)

---

## Table Styles

### Built-in styles to use

| Context | Style name | Visual |
|---|---|---|
| Standard data table | TableStyleMedium2 | Blue header, white/light blue banded |
| Financial | TableStyleMedium9 | Dark blue header, white/grey banded |
| Minimal | TableStyleLight1 | White header with bottom border only |
| Dark dashboard | TableStyleDark1 | Black header, dark banded |

**Never use:** TableStyleLight2–6 (too pastel), any style with heavy interior borders on all cells.

### Custom table style (programmatic — openpyxl)

```python
from openpyxl.worksheet.table import Table, TableStyleInfo

table = Table(displayName="SalesData", ref="A4:G104")
style = TableStyleInfo(
    name="TableStyleMedium2",
    showFirstColumn=False,
    showLastColumn=False,
    showRowStripes=True,
    showColumnStripes=False
)
table.tableStyleInfo = style
ws.add_table(table)
```

### Column width guidelines

| Content type | Min width | Typical width | Max width |
|---|---|---|---|
| ID / code | 8 | 10 | 15 |
| Short name | 12 | 18 | 25 |
| Full name / description | 20 | 30 | 50 |
| Currency amount | 12 | 14 | 18 |
| Date | 10 | 12 | 15 |
| Status / category | 10 | 14 | 20 |
| Notes / comments | 20 | 35 | 60 |

**Auto-width in openpyxl:**
```python
for col in ws.columns:
    max_len = max(len(str(cell.value or "")) for cell in col)
    ws.column_dimensions[col[0].column_letter].width = min(max(max_len + 2, 8), 60)
```

### Row height guidelines

| Row type | Height |
|---|---|
| Title row | 30–40pt |
| Subtitle / spacer | 18pt |
| Table header row | 22–25pt |
| Data rows | 18pt (default 15pt is too cramped) |
| Totals row | 22pt |

---

## Sheet Layout

### Standard sheet structure

```
A1:  [Sheet title]              — merged across columns, brand colour fill, white bold text
A2:  [Subtitle / date / filter] — grey text, smaller
A3:  [blank spacer]
A4:  [Table header row]         — Excel Table starts here
...  [Data rows]
Last: [Totals row]              — Table totals row, bold
     [1 blank row gap]
     [Source / notes footnote]  — italics, grey
```

### Column layout rules

- **Always start data at column A** unless there is a structural reason to indent
- **Never leave columns A or B empty** as decorative margins — use cell padding (indentation) instead
- **Row 1 title** should span the full width of the data table (merge only for display headers, never in data)
- **Freeze row 4** (the table header) if using the standard layout above, or freeze row 1 if table starts at row 1

### Multiple sheets

- Sheet 1: Summary / Dashboard (user's landing page)
- Sheet 2+: Data tables
- Last sheet(s): Configuration / lookup data (optionally hidden)
- Tab colours: Assign a colour per sheet type (blue for data, green for summary, grey for config)

---

## Conditional Formatting Patterns

Apply rules to entire Table column references (e.g., `Sales[Status]`), not fixed cell ranges.

### Status column (traffic-light)

| Status value | Fill | Text colour |
|---|---|---|
| Paid / Complete / Active | #E2EFDA | #375623 |
| Pending / In Progress | #FFEB9C | #7D6608 |
| Overdue / Failed / Inactive | #FFC7CE | #9C0006 |
| Cancelled / N/A | #F2F2F2 | #595959 |

**Formula-based rule (for Table column):**
- Rule type: "Use a formula to determine which cells to format"
- Formula: `=[@Status]="Paid"` (when applied to a Table column)
- Or for fixed range starting at E5: `=$E5="Paid"`

### Data bars

- Solid fill, no border
- Minimum: Number, 0
- Maximum: Number, or "Automatic"
- Use brand accent colour (#4472C4)
- Negative bar: red (#C00000), axis position: automatic

### Icon sets

| Use case | Icon set |
|---|---|
| 3-level rating | 3 Traffic Lights |
| Up/down/flat trend | 3 Triangles |
| 5-level score | 5 Ratings |
| Pass/fail | 3 Symbols (circle check / X) |

Threshold: set percentage thresholds explicitly — never leave at default 33%/67%.

### Top/Bottom rules

- Top 10 items: brand accent fill
- Bottom 10 items: warning amber fill
- Above average: light green
- Below average: light red

---

## Professional Finishing

### Freeze panes

```
View → Freeze Panes
```
- **Always freeze the header row** of every data table
- For wide tables (15+ columns): also freeze the first column (ID/Name column)
- Freeze at the row BELOW the header: if header is row 4, click row 5 col B, then freeze

### Print setup (for every print-intended sheet)

```
Page Layout → Page Setup dialog (launcher arrow)
```

| Setting | Value |
|---|---|
| Orientation | Landscape for wide tables; Portrait for narrow |
| Scaling | Fit to: 1 page wide, [blank] tall |
| Paper size | A4 |
| Margins | Narrow: 0.64 cm all sides; or Normal for reports |
| Print titles | Rows to repeat: title row + header row |
| Gridlines | ON for data sheets; OFF for dashboards |
| Row/column headings | OFF |

**Page header:** `&L[Company Name]&C[Sheet Title]&R[Date: &D]`
**Page footer:** `&LConfidential&C&P of &N&R[Project Name]`

### Named ranges

- Name every important range: `Ctrl+Shift+F3` (from selection) or Formulas → Name Manager
- Use names in formulas instead of cell addresses: `=SUM(Revenue)` not `=SUM(C5:C104)`
- Convention: PascalCase — `SalesData`, `TaxRate`, `ReportDate`
- Scope: workbook-level unless specifically needed per-sheet

### Workbook hygiene checklist

- [ ] No Sheet1/Sheet2/Sheet3 default names remaining
- [ ] No empty/unused sheets
- [ ] All #REF!, #VALUE!, #DIV/0! errors resolved (or intentionally hidden with IFERROR)
- [ ] No stray data outside Table definitions
- [ ] Document properties set: Title, Author, Company (File → Info → Properties)
- [ ] Calculation set to Automatic (Formulas → Calculation Options → Automatic)
- [ ] File saved as .xlsx (not .xls)

---

## Dashboard Design

Dashboards are presentation layers — they display calculated results, never raw data entry.

### Layout principles

- **Top band:** Title, date range selector, key filters (dropdowns)
- **KPI row:** 3–5 large metric cards (value + label + sparkline or trend indicator)
- **Charts section:** 2–4 charts, consistent size, aligned to a grid
- **Summary table:** Condensed data table below charts
- **No scrolling:** Entire dashboard visible on screen at 100% zoom

### KPI card structure (per cell block)

```
[Merged 3×2 block]
Row 1: KPI value (24–36pt, bold, brand colour)
Row 2: KPI label (9pt, grey)
Row 3: vs prior period (small, red/green with arrow)
Background: white with thin brand-colour border
```

### Chart placement

- Charts should be aligned to cell gridlines (hold Alt while moving/resizing)
- Consistent chart sizes: all charts in a row use the same height
- No chart titles that duplicate the axis labels
- Remove chart borders (Format Chart Area → No border)
- White chart background — never grey or coloured

### Slicers (for interactive dashboards)

- Connect to PivotTable or Table via Insert → Slicer
- Style: SlicerStyleLight2 or brand-matching custom style
- Place slicers in the filter band at the top
- Size: consistent width, one column of items per slicer where possible
