# Charts, PivotTables & Dashboards

*Sources: Microsoft Excel 365 Bible; Excel 2025 All-in-One Step-by-Step Guide*

---

## Table of Contents

1. [Chart Type Selection](#chart-type-selection)
2. [Professional Chart Formatting](#professional-chart-formatting)
3. [Dynamic Charts](#dynamic-charts)
4. [Sparklines](#sparklines)
5. [PivotTables](#pivottables)
6. [Slicers and Timelines](#slicers-and-timelines)
7. [Dashboard Assembly](#dashboard-assembly)

---

## Chart Type Selection

Choose the chart type based on the question being answered, not aesthetic preference.

| Question type | Best chart type | Avoid |
|---|---|---|
| Comparison (categories) | Clustered Bar (horizontal) | 3D charts |
| Comparison (few items) | Clustered Column | Pie with >5 slices |
| Trend over time | Line chart | Bar for time series |
| Part-to-whole (few items) | Pie or Donut (max 5 slices) | Exploded pie |
| Part-to-whole (many items) | 100% Stacked Bar | Pie |
| Distribution | Histogram | Line for discrete data |
| Correlation / relationship | Scatter plot | Line for correlation |
| Ranking | Horizontal Bar (sorted) | 3D anything |
| KPI vs target | Bullet chart or Gauge | Speedometer |
| Geographic data | Map chart | Bar chart for regions |
| Cumulative total / Pareto | Combo (bar + line) | — |
| Waterfall (bridges) | Waterfall chart | Stacked bar |
| Hierarchy / part-of-part | Treemap or Sunburst | Pie |

**Rules:**
- Never use 3D charts in professional output — they distort values and are unreadable
- Pie charts are only acceptable with ≤5 slices; all others use a different chart type
- Sort bar/column charts by value (descending) unless the order itself is meaningful (e.g., time)

---

## Professional Chart Formatting

### The Minimum Professional Standard

Every chart delivered must have:

1. **No chart border** (Format Chart Area → No line)
2. **White or transparent background** (not grey)
3. **Clean title** — specific and informative ("Monthly Revenue by Region, Q1 2026"), not generic ("Chart 1")
4. **Axes labelled** with units where non-obvious
5. **Legend** — either remove it (label series directly) or place it at the bottom, not on the right
6. **Gridlines** — horizontal only, light grey (#D9D9D9), no vertical gridlines
7. **No chart junk** — no gradient fills, no shadows, no glows on data series
8. **Consistent colour palette** — use brand colours in order, not default rainbow

### Standard colour sequence for chart series

```
Series 1: #1F3864 (Navy)
Series 2: #4472C4 (Cornflower)
Series 3: #70AD47 (Green)
Series 4: #ED7D31 (Orange)
Series 5: #FFC000 (Yellow)
Series 6: #FF0000 (Red) — use sparingly, for negative/warning only
```

### Typography in charts

| Element | Font | Size | Style |
|---|---|---|---|
| Chart title | Calibri Light | 14pt | Bold |
| Axis titles | Calibri | 10pt | Regular |
| Axis labels | Calibri | 9pt | Regular |
| Data labels | Calibri | 9pt | Bold |
| Legend | Calibri | 10pt | Regular |

### Data labels

- Only add data labels when the precise value matters
- Position: outside end for bars/columns, above for lines
- Format data labels with the same number format as the data source
- Never show both axis AND data labels — choose one

### Chart sizing and alignment

- Charts must snap to cell grid (hold Alt while moving/resizing)
- Consistent height across a row of charts
- Typical card chart: 8–10 columns × 15–18 rows of cells
- Full-width chart: spans all data columns

---

## Dynamic Charts

### Using Table references (auto-update)

Link chart to an Excel Table — when the Table grows, the chart updates automatically.

1. Select Table data including headers
2. Insert → Chart
3. The chart source is automatically the Table column references

### OFFSET-based dynamic range (legacy approach — avoid when Tables available)

```excel
# Named range that expands with data
=OFFSET(Sheet1!$A$1, 0, 0, COUNTA(Sheet1!$A:$A), 1)
```

### FILTER-driven charts (365)

1. Use FILTER or SORT formula to build the chart data range on a helper area
2. Base the chart on the spill range of the dynamic array formula
3. Changing filter criteria updates the chart automatically

### Combo charts (bar + line, e.g., revenue + growth rate)

1. Create a clustered column chart with all series
2. Right-click the series that should be a line → Change Series Chart Type
3. Select Line → assign to Secondary Axis
4. Format secondary axis with appropriate scale

---

## Sparklines

Sparklines are mini-charts inside a single cell — ideal for KPI cards and summary tables.

### Types

| Type | Use case |
|---|---|
| Line | Trends over time |
| Column | Month-by-month comparison |
| Win/Loss | Binary outcomes (profit/loss, pass/fail) |

### Insert

Insert → Sparklines → Line/Column/Win-Loss → select data range → select location range

### Formatting sparklines

- **High/Low points:** Sparkline tab → Show → High Point (green), Low Point (red)
- **Axis scaling:** Set minimum and maximum to "Same for all sparklines" in a group — otherwise each sparkline has its own scale, making comparison misleading
- **Line weight:** 2.25pt for line sparklines in KPI cards
- **Colour:** Brand primary (#1F3864) for line; positive green / negative red for column

---

## PivotTables

PivotTables are the most powerful analysis feature in Excel. Every data analyst should use them.

### Setup requirements

The source data must:
- Have no blank rows or columns in the range
- Have unique, non-blank column headers in row 1
- Be structured as an Excel Table (strongly preferred — the Table auto-expands)

### Creating a PivotTable

1. Click inside the Table
2. Insert → PivotTable → New Worksheet
3. Arrange fields:
   - **Rows:** Category dimensions (Region, Product, Month)
   - **Columns:** Secondary dimensions (Quarter, Year) — keep narrow
   - **Values:** Numeric measures (Amount, Quantity, Count)
   - **Filters:** Global filters (not recommended — use Slicers instead)

### Value field settings (mandatory)

Always configure Value Field Settings for every measure:
- Right-click value cell → Value Field Settings
- **Number Format:** Apply the same format as the source column (currency, %, etc.)
- **Summarize by:** SUM for amounts; COUNT for IDs; AVERAGE for rates
- **Show values as:** % of Column Total, % of Row Total, Running Total, Difference From — use these for analytical views

### PivotTable design standards

| Setting | Value |
|---|---|
| Report layout | Tabular (not Compact — tabular is readable and exportable) |
| Subtotals | Top of group (or hide if not needed) |
| Grand totals | Rows and Columns |
| Row/Column labels | Repeat item labels (Design → Report Layout) |
| Blank rows | Remove (Design → Blank Rows → Remove) |
| PivotTable style | PivotStyleMedium2 (matches table style) |

### Calculated fields

```
PivotTable Analyze → Fields, Items & Sets → Calculated Field

Name: Avg Order Value
Formula: =Amount/OrderCount
```

**Never reference cell addresses in calculated field formulas** — use field names only.

### Refreshing PivotTables

- Manual: Right-click → Refresh
- On open: PivotTable Analyze → PivotTable → Options → Data → "Refresh data when opening the file"
- Programmatic: call `.RefreshAll()` or `.PivotCache.Refresh()` before saving

---

## Slicers and Timelines

### Slicers

Slicers are visual filter buttons connected to PivotTables or Tables.

**Insert:** PivotTable Analyze → Insert Slicer (or Insert → Slicer for Tables)

**Formatting standards:**
- Slicer style: SlicerStyleLight2 or create a custom style matching brand
- Columns: 1 for short lists (<8 items), 2–3 for longer lists
- Size: consistent width (e.g., 5 cm) per slicer, placed in the dashboard filter zone
- Font: Calibri 10pt

**Connect to multiple PivotTables:**
Slicer → Slicer tab → Report Connections → check all connected PivotTables

### Timelines

Purpose-built slicer for date fields.

**Insert:** PivotTable Analyze → Insert Timeline → select date field

**Granularity options:** Years / Quarters / Months / Days
- Default to Months for operational reports
- Default to Quarters for annual/strategic reports

**Formatting:** Apply Timeline Style Light 1 or matching brand style

---

## Dashboard Assembly

### Layout grid

Place all dashboard elements on a presentation sheet with no gridlines visible (View → uncheck Gridlines).

```
Row 1–3:    Title bar + company logo + date range selector
Row 4–5:    Filter zone (slicers)
Row 6–15:   KPI cards (4–6 across)
Row 16–30:  Charts row 1 (2–3 charts)
Row 31–45:  Charts row 2 (or summary table)
Row 46+:    Footnotes / data sources
```

### KPI card design (openpyxl)

```python
def add_kpi_card(ws, top_row, left_col, value, label, vs_prior=None, fmt="#,##0"):
    """Adds a 3-row × 4-column KPI card block."""
    merge_ref = f"{get_column_letter(left_col)}{top_row}:{get_column_letter(left_col+3)}{top_row+2}"
    # Value cell (row 1)
    val_cell = ws.cell(row=top_row, column=left_col, value=value)
    val_cell.number_format = fmt
    val_cell.font = Font(name="Calibri Light", size=28, bold=True, color="1F3864")
    val_cell.alignment = Alignment(horizontal="center", vertical="bottom")
    ws.row_dimensions[top_row].height = 30

    # Label (row 2)
    lbl_cell = ws.cell(row=top_row+1, column=left_col, value=label)
    lbl_cell.font = Font(name="Calibri", size=9, color="595959")
    lbl_cell.alignment = Alignment(horizontal="center", vertical="top")
    ws.row_dimensions[top_row+1].height = 14

    # vs prior period (row 3)
    if vs_prior is not None:
        arrow = "▲" if vs_prior >= 0 else "▼"
        color = "375623" if vs_prior >= 0 else "9C0006"
        trend_cell = ws.cell(row=top_row+2, column=left_col,
                             value=f"{arrow} {abs(vs_prior):.1%} vs prior")
        trend_cell.font = Font(name="Calibri", size=8, color=color)
        trend_cell.alignment = Alignment(horizontal="center")
    ws.row_dimensions[top_row+2].height = 12

    # Card border
    for r in range(top_row, top_row+3):
        for c in range(left_col, left_col+4):
            ws.cell(row=r, column=c).border = Border(
                outline=True,
                left=Side(style="medium", color="4472C4") if c==left_col else Side(style=None),
                right=Side(style="medium", color="4472C4") if c==left_col+3 else Side(style=None),
                top=Side(style="medium", color="4472C4") if r==top_row else Side(style=None),
                bottom=Side(style="medium", color="4472C4") if r==top_row+2 else Side(style=None),
            )
```

### Protecting dashboards

Lock the presentation layer so users can only interact with slicers and filters:

1. Select all cells → Format Cells → Protection → uncheck Locked
2. Select slicer/filter cells → leave Locked checked
3. Review → Protect Sheet → allow: "Select unlocked cells", "Use AutoFilter"
4. Password optional
