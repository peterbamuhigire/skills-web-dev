# Excel Dashboard Patterns

Production recipes for multi-sheet branded dashboards. All code assumes a `Brand` object from `branding-system.md` and `xlsxwriter` unless noted.

## Canonical workbook structure

```text
Cover            tenant logo, title, period, generation timestamp
Summary          KPI tiles, trend sparklines, status
<Entity sheets>  detail tables (customers, products, regions, periods)
<Chart sheets>   full-page charts
RawData          underlying rows (hidden or last)
```

Every sheet: gridlines off, tab colour set to brand, print setup configured, first row frozen.

## Workbook skeleton

```python
import xlsxwriter
from datetime import datetime, UTC

wb = xlsxwriter.Workbook(path, {
    "constant_memory": False,  # turn on for > 50k rows; off to allow chart sheets and merge_range
    "default_date_format": "yyyy-mm-dd",
    "remove_timezone": True,
})

fmt = register_formats(wb, brand)   # see below

cover = wb.add_worksheet("Cover")
summary = wb.add_worksheet("Summary")
customers = wb.add_worksheet("Customers")
products = wb.add_worksheet("Products")
trends = wb.add_chartsheet("Trends")
raw = wb.add_worksheet("RawData")

for ws in (cover, summary, customers, products, raw):
    ws.hide_gridlines(2)
    ws.set_tab_color(brand.primary)

raw.hide()  # optional: keep but conceal the raw sheet
wb.close()
```

## Named format registry

Centralise formats — a dashboard uses 15–25 and they must be reused, not re-declared per cell.

```python
def register_formats(wb, brand):
    f = {}
    base = {"font_name": brand.font_family}

    f["title"]       = wb.add_format({**base, "bold": True, "font_size": 20, "font_color": brand.primary})
    f["subtitle"]    = wb.add_format({**base, "font_size": 11, "font_color": brand.muted})
    f["h2"]          = wb.add_format({**base, "bold": True, "font_size": 14, "font_color": brand.text})
    f["kpi_label"]   = wb.add_format({**base, "font_size": 10, "font_color": brand.muted, "bold": True})
    f["kpi_value"]   = wb.add_format({**base, "font_size": 22, "bold": True, "font_color": brand.primary, "num_format": "#,##0"})
    f["kpi_money"]   = wb.add_format({**base, "font_size": 22, "bold": True, "font_color": brand.primary, "num_format": "#,##0.00"})
    f["kpi_pct"]     = wb.add_format({**base, "font_size": 22, "bold": True, "font_color": brand.primary, "num_format": "0.0%"})
    f["header"]      = wb.add_format({**base, "bold": True, "bg_color": brand.primary, "font_color": "#FFFFFF", "border": 1, "align": "left", "valign": "vcenter"})
    f["cell"]        = wb.add_format({**base, "border": 1, "border_color": "#E5E7EB"})
    f["cell_num"]    = wb.add_format({**base, "border": 1, "border_color": "#E5E7EB", "num_format": "#,##0"})
    f["cell_money"]  = wb.add_format({**base, "border": 1, "border_color": "#E5E7EB", "num_format": "#,##0.00"})
    f["cell_pct"]    = wb.add_format({**base, "border": 1, "border_color": "#E5E7EB", "num_format": "0.0%"})
    f["cell_date"]   = wb.add_format({**base, "border": 1, "border_color": "#E5E7EB", "num_format": "yyyy-mm-dd"})
    f["total"]       = wb.add_format({**base, "bold": True, "top": 2, "num_format": "#,##0.00"})
    f["good"]        = wb.add_format({**base, "font_color": brand.success, "bold": True})
    f["bad"]         = wb.add_format({**base, "font_color": brand.danger, "bold": True})
    f["warn"]        = wb.add_format({**base, "font_color": brand.warning, "bold": True})
    return f
```

## Cover sheet

```python
def write_cover(ws, brand, tenant, period_start, period_end, logo_path, f):
    ws.set_column("A:A", 2)
    ws.set_column("B:B", 60)
    ws.insert_image("B2", str(logo_path), {"x_scale": 0.5, "y_scale": 0.5, "x_offset": 2})
    ws.write("B8", f"{tenant.name}", f["title"])
    ws.write("B9", "Sales Performance Dashboard", f["h2"])
    ws.write("B11", f"Period: {period_start:%d %b %Y} to {period_end:%d %b %Y}", f["subtitle"])
    ws.write("B12", f"Generated: {datetime.now(UTC):%Y-%m-%d %H:%M UTC}", f["subtitle"])
    ws.write("B14", brand.footer_tagline or "", f["subtitle"])
    ws.set_row(7, 30)
    ws.hide_gridlines(2)
```

## KPI tile block

```python
def write_kpi_tiles(ws, f, kpis: dict, row_start=2, col_start=1):
    # kpis: {"MRR": {"value": 125000, "format": "money", "delta": 0.082}, ...}
    ws.set_row(row_start, 22)
    ws.set_row(row_start + 1, 36)
    for i, (label, k) in enumerate(kpis.items()):
        col = col_start + i * 3
        ws.set_column(col, col + 1, 16)
        ws.merge_range(row_start, col, row_start, col + 1, label.upper(), f["kpi_label"])
        value_fmt = {"money": f["kpi_money"], "pct": f["kpi_pct"]}.get(k["format"], f["kpi_value"])
        ws.merge_range(row_start + 1, col, row_start + 1, col + 1, k["value"], value_fmt)
        if (delta := k.get("delta")) is not None:
            d_fmt = f["good"] if delta >= 0 else f["bad"]
            arrow = "▲" if delta >= 0 else "▼"
            ws.write(row_start + 2, col, f"{arrow} {delta:+.1%} vs prior", d_fmt)
```

## Data table with conditional formatting

```python
def write_table(ws, f, headers: list[str], rows: list[list], start_row=2, start_col=1, name="tbl_customers"):
    for c, h in enumerate(headers):
        ws.write(start_row, start_col + c, h, f["header"])
    for r, row in enumerate(rows, start=start_row + 1):
        for c, val in enumerate(row):
            fmt = pick_cell_format(headers[c], f)
            ws.write(r, start_col + c, val, fmt)
    # Excel table (listObject) — gives filters, sorts, banding.
    last_row = start_row + len(rows)
    last_col = start_col + len(headers) - 1
    ws.add_table(start_row, start_col, last_row, last_col, {
        "name": name,
        "columns": [{"header": h} for h in headers],
        "style": "Table Style Light 1",
    })
    autofit_columns(ws, headers, rows, start_col)
```

## Conditional formatting recipes

```python
# Red/amber/green colour scale on a column of numbers (revenue).
ws.conditional_format("D3:D1000", {
    "type": "3_color_scale",
    "min_color": "#F87171",  # red
    "mid_color": "#FDE68A",  # amber
    "max_color": "#34D399",  # green
})

# Data bars with brand colour.
ws.conditional_format("E3:E1000", {
    "type": "data_bar",
    "bar_color": brand.primary,
    "bar_only": False,
})

# Icon set: thresholds on a growth column (%).
ws.conditional_format("F3:F1000", {
    "type": "icon_set",
    "icon_style": "3_arrows",
    "icons": [
        {"criteria": ">=", "type": "number", "value": 0.05},
        {"criteria": ">=", "type": "number", "value": 0.00},
    ],
})

# Formula-driven: highlight overdue rows (date in column B < TODAY()).
ws.conditional_format("B3:B1000", {
    "type": "formula",
    "criteria": "=AND($B3<>\"\",$B3<TODAY())",
    "format": f["bad"],
})
```

## Formulas

```python
# Sum across a table range.
ws.write_formula("D1001", "=SUBTOTAL(109,D3:D1000)", f["total"])

# Growth rate referencing another sheet.
ws.write_formula("E3", "=IFERROR(Customers!D3/Customers!D2-1,0)", f["cell_pct"])

# Dynamic arrays (Excel 365+). Declare once, spills.
ws.write_dynamic_array_formula("H3:H1000", "=UNIQUE(Customers!B3:B1000)")
```

Pre-compute totals in pandas for huge workbooks. Each formula recalculated at open slows Excel. Rule: under 1,000 rows you can use formulas freely; over 50,000 rows write values only.

## Sparklines

```python
# One sparkline per row of a weekly trend.
for r in range(start_row + 1, last_row + 1):
    ws.add_sparkline(r, sparkline_col, {
        "range": f"Customers!J{r+1}:T{r+1}",
        "type": "line",
        "markers": True,
        "series_color": brand.primary,
        "negative_color": brand.danger,
    })
```

## Charts (xlsxwriter)

```python
chart = wb.add_chart({"type": "line"})
chart.add_series({
    "name":       "MRR",
    "categories": ["RawData", 1, 0, 24, 0],
    "values":     ["RawData", 1, 1, 24, 1],
    "line":       {"color": brand.primary, "width": 2.25},
    "marker":     {"type": "circle", "size": 5, "fill": {"color": brand.primary}},
})
chart.set_title({"name": "MRR — last 24 months", "name_font": {"name": brand.font_family, "size": 12, "bold": True}})
chart.set_x_axis({"num_font": {"size": 9}})
chart.set_y_axis({"num_font": {"size": 9}, "num_format": "#,##0"})
chart.set_legend({"none": True})
chart.set_chartarea({"border": {"none": True}})
chart.set_plotarea({"border": {"none": True}})
ws.insert_chart("B18", chart, {"x_scale": 1.2, "y_scale": 1.2})
```

For a full-page chart, prefer `wb.add_chartsheet("Trends")` and `chartsheet.set_chart(chart)`.

## Data validation (dropdowns)

```python
ws.data_validation("C3:C1000", {
    "validate":   "list",
    "source":     ["Active", "Churned", "Paused"],
    "input_title": "Status",
    "input_message": "Pick a lifecycle state",
})

# Reference-based list (better for long lists).
ws.data_validation("D3:D1000", {"validate": "list", "source": "=Lists!$A$1:$A$50"})
```

## Cell protection

```python
ws.protect("a-strong-password-here", {
    "select_locked_cells": True,
    "select_unlocked_cells": True,
    "sort": True,
    "autofilter": True,
})

# Unlock the input cells so users can type but not edit formulas/headers.
unlock = wb.add_format({"locked": False})
ws.write("B5", "", unlock)
```

Do not rely on protection for security. Excel file protection is trivial to bypass. Use it for accidental-edit prevention only.

## Freeze panes

```python
ws.freeze_panes(start_row + 1, start_col)   # freeze header row and left key column
```

## Column width auto-fit

xlsxwriter has no true auto-fit. Estimate from content:

```python
def autofit_columns(ws, headers, rows, start_col=0, max_width=40, min_width=8, padding=2):
    for i, h in enumerate(headers):
        longest = max([len(str(h))] + [len(str(r[i])) for r in rows if i < len(r)])
        width = max(min_width, min(max_width, longest + padding))
        ws.set_column(start_col + i, start_col + i, width)
```

openpyxl 3.1+ has `ws.column_dimensions["A"].best_fit = True` but it is advisory — Excel computes on open, unreliably.

## Print setup

```python
ws.set_landscape()
ws.set_paper(9)                         # A4
ws.set_margins(left=0.5, right=0.5, top=0.7, bottom=0.7)
ws.fit_to_pages(1, 0)                   # 1 page wide, any height
ws.repeat_rows(start_row, start_row)    # repeat header row on every page
ws.set_header(f"&L{tenant.name}&C{report_title}&R&P of &N")
ws.set_footer(f"&LGenerated {datetime.now():%Y-%m-%d}&R&A")
```

## Pivot tables — openpyxl only

xlsxwriter does not write pivot tables. Options:

1. Put the pivot into a pre-authored template, use openpyxl to refresh the data range, and let Excel recalc on open.
2. Build the pivot output yourself with pandas (`df.pivot_table`) and write the result as a normal table. This is what most production dashboards do — it avoids the pivot engine entirely and gives you full format control.

```python
pv = df.pivot_table(index="region", columns="product", values="revenue", aggfunc="sum", fill_value=0)
pv.loc["Total"] = pv.sum()
pv["Total"] = pv.sum(axis=1)
write_table(ws, f, ["Region", *pv.columns.tolist()], pv.reset_index().values.tolist())
```

## Anti-patterns

- 15 columns all set to default width — the dashboard looks amateur. Always set widths.
- Gridlines left on — dashboards feel like ledgers. Hide them.
- Mixing fonts across sheets — pick one from `brand.font_family` and stay there.
- Embedding the logo 10 times at full resolution — load once, resize to thumbnail, reuse.
- Conditional formatting on a whole column (`A:A`) in a big workbook — Excel slows dramatically. Scope ranges.
- Huge formula chains with volatile functions (`NOW`, `TODAY`, `OFFSET`) — recalc storms.
