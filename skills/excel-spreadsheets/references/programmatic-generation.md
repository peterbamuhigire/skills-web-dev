# Programmatic Excel Generation

*Sources: Microsoft Excel 365 Bible; Excel 2025 All-in-One Step-by-Step Guide*

---

## Table of Contents

1. [Library Selection](#library-selection)
2. [openpyxl (Python)](#openpyxl-python)
3. [xlsxwriter (Python)](#xlsxwriter-python)
4. [PhpSpreadsheet (PHP)](#phpspreadsheet-php)
5. [pandas Export](#pandas-export)
6. [ExcelJS (Node.js/JavaScript)](#exceljs-nodejs)
7. [Import / Parsing Patterns](#import--parsing-patterns)
8. [Universal Non-Negotiables](#universal-non-negotiables)

---

## Library Selection

| Need | Library | Language | Notes |
|---|---|---|---|
| Full control: formatting, charts, tables | openpyxl | Python | Best for rich output |
| Large data (100k+ rows), max performance | xlsxwriter | Python | Write-only, no reading |
| PHP web apps | PhpSpreadsheet | PHP | Full-featured |
| Data science output | pandas + openpyxl | Python | ExcelWriter handles multiple sheets |
| Node.js / TypeScript apps | exceljs | JS/TS | Full read/write support |
| Simple CSV-like output | csv module | Any | Use only when formatting is irrelevant |

---

## openpyxl (Python)

### Complete professional workbook template

```python
from openpyxl import Workbook
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side, numbers
)
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import ColorScaleRule, DataBarRule, FormulaRule

# ── Colour constants ──────────────────────────────────────────
NAVY       = "1F3864"
STEEL      = "2E5D8A"
ACCENT     = "4472C4"
ICE        = "D6E4F7"
NEAR_BLACK = "262626"
MID_GREY   = "595959"
LIGHT_GREY = "BFBFBF"
GREEN_FILL = "E2EFDA"
GREEN_TEXT = "375623"
RED_FILL   = "FFC7CE"
RED_TEXT   = "9C0006"
AMBER_FILL = "FFEB9C"
AMBER_TEXT = "7D6608"

def make_fill(hex_color): return PatternFill("solid", fgColor=hex_color)
def make_font(bold=False, color=NEAR_BLACK, size=10, italic=False):
    return Font(name="Calibri", bold=bold, color=color, size=size, italic=italic)
def make_border(style="thin", color=LIGHT_GREY):
    s = Side(style=style, color=color)
    return Border(left=s, right=s, top=s, bottom=s)
def auto_width(ws, min_w=8, max_w=60):
    for col in ws.columns:
        max_len = max((len(str(c.value or "")) for c in col), default=0)
        ws.column_dimensions[col[0].column_letter].width = min(max(max_len + 2, min_w), max_w)

# ── Build workbook ────────────────────────────────────────────
def build_report(data: list[dict], title: str, filename: str):
    wb = Workbook()
    ws = wb.active
    ws.title = "Sales Report"
    ws.sheet_properties.tabColor = NAVY

    headers = list(data[0].keys()) if data else []
    n_cols  = len(headers)
    n_rows  = len(data)
    last_col = get_column_letter(n_cols)

    # Row 1: title
    ws.row_dimensions[1].height = 36
    ws.merge_cells(f"A1:{last_col}1")
    ws["A1"].value     = title
    ws["A1"].font      = make_font(bold=True, color="FFFFFF", size=16)
    ws["A1"].fill      = make_fill(NAVY)
    ws["A1"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    # Row 2: subtitle
    ws.row_dimensions[2].height = 20
    ws.merge_cells(f"A2:{last_col}2")
    from datetime import date
    ws["A2"].value     = f"Generated: {date.today().strftime('%d %b %Y')}"
    ws["A2"].font      = make_font(color=MID_GREY, size=10, italic=True)
    ws["A2"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[3].height = 6   # spacer

    # Row 4: Table headers
    ws.row_dimensions[4].height = 24
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=4, column=col_idx, value=header)
        cell.font      = make_font(bold=True, color="FFFFFF", size=11)
        cell.fill      = make_fill(NAVY)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border    = make_border(color=STEEL)

    for row_idx, row_data in enumerate(data, start=5):
        ws.row_dimensions[row_idx].height = 18
        for col_idx, key in enumerate(headers, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=row_data.get(key))
            cell.font   = make_font()
            cell.border = make_border(style="hair")
            h_align = "right" if isinstance(row_data.get(key), (int, float)) else "left"
            cell.alignment = Alignment(horizontal=h_align, vertical="center")

    table_ref = f"A4:{last_col}{4 + n_rows}"
    tbl = Table(displayName="ReportData", ref=table_ref)
    tbl.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2", showRowStripes=True,
        showFirstColumn=False, showLastColumn=False, showColumnStripes=False,
    )
    ws.add_table(tbl)
    auto_width(ws)
    ws.freeze_panes                = "A5"
    ws.page_setup.orientation      = "landscape"
    ws.page_setup.fitToWidth       = 1
    ws.page_setup.fitToPage        = True
    ws.print_title_rows            = "4:4"
    ws.sheet_view.showGridLines    = True
    wb.save(filename)
    return filename
```

### Applying number formats

```python
# Number format constants
FMT_CURRENCY    = '#,##0'
FMT_CURRENCY_2  = '#,##0.00'
FMT_USD         = '"$"#,##0.00'
FMT_PERCENT     = '0.00%'
FMT_DATE        = 'DD MMM YYYY'
FMT_DATE_ISO    = 'YYYY-MM-DD'
FMT_INT         = '#,##0'
FMT_NEG_RED     = '#,##0.00;[Red]-#,##0.00'

cell.number_format = FMT_CURRENCY
```

### Conditional formatting (openpyxl)

```python
from openpyxl.formatting.rule import (
    ColorScaleRule, DataBarRule, FormulaRule, CellIsRule
)
from openpyxl.styles import PatternFill

data_range = f"C5:C{4 + n_rows}"  # amount column

# 3-colour scale heat map
ws.conditional_formatting.add(data_range, ColorScaleRule(
    start_type="min",  start_color="FFFFFF",
    mid_type="percentile", mid_value=50, mid_color=ICE,
    end_type="max",   end_color=NAVY
))

# Traffic light (formula-based, status column)
status_range = f"E5:E{4 + n_rows}"
for value, fill_hex, font_hex in [
    ("Paid",    GREEN_FILL, GREEN_TEXT),
    ("Pending", AMBER_FILL, AMBER_TEXT),
    ("Overdue", RED_FILL,   RED_TEXT),
]:
    ws.conditional_formatting.add(status_range, FormulaRule(
        formula=[f'$E5="{value}"'],
        fill=PatternFill("solid", fgColor=fill_hex),
        font=Font(color=font_hex)
    ))
```

### Multiple sheets

```python
# Tab colours
ws_summary = wb.create_sheet("Summary")
ws_summary.sheet_properties.tabColor = "1F3864"  # navy

ws_data = wb.create_sheet("Data")
ws_data.sheet_properties.tabColor = "4472C4"  # accent

ws_config = wb.create_sheet("Config")
ws_config.sheet_properties.tabColor = "595959"  # grey
ws_config.sheet_state = "hidden"

# Reorder: Summary first
wb.move_sheet("Summary", offset=-len(wb.worksheets))
```

---

## xlsxwriter (Python)

Best for large datasets. Write-only — cannot read existing files.

```python
import xlsxwriter
from datetime import date

wb = xlsxwriter.Workbook("report.xlsx")
ws = wb.add_worksheet("Sales Report")
ws.set_tab_color("#1F3864")

# ── Formats ───────────────────────────────────────────────────
hdr_fmt = wb.add_format({
    "bold": True, "font_name": "Calibri", "font_size": 11,
    "font_color": "#FFFFFF", "bg_color": "#1F3864",
    "align": "center", "valign": "vcenter",
    "border": 1, "border_color": "#2E5D8A"
})
data_fmt = wb.add_format({
    "font_name": "Calibri", "font_size": 10,
    "border": 1, "border_color": "#BFBFBF", "valign": "vcenter"
})
currency_fmt = wb.add_format({
    "font_name": "Calibri", "font_size": 10,
    "num_format": "#,##0.00", "align": "right",
    "border": 1, "border_color": "#BFBFBF"
})
date_fmt = wb.add_format({
    "num_format": "DD MMM YYYY", "align": "right",
    "font_name": "Calibri", "font_size": 10
})
title_fmt = wb.add_format({
    "bold": True, "font_name": "Calibri Light", "font_size": 16,
    "font_color": "#FFFFFF", "bg_color": "#1F3864",
    "align": "left", "valign": "vcenter", "indent": 1
})

# ── Title row ─────────────────────────────────────────────────
ws.set_row(0, 36)
ws.merge_range("A1:G1", "Sales Report — Q1 2026", title_fmt)

# ── Headers ───────────────────────────────────────────────────
headers = ["ID", "Date", "Customer", "Product", "Qty", "Unit Price", "Amount"]
ws.set_row(3, 24)
for col, h in enumerate(headers):
    ws.write(3, col, h, hdr_fmt)

# ── Data ──────────────────────────────────────────────────────
for row_idx, row in enumerate(data, start=4):
    ws.set_row(row_idx, 18)
    ws.write(row_idx, 0, row["id"],         data_fmt)
    ws.write_datetime(row_idx, 1, row["date"], date_fmt)
    ws.write(row_idx, 2, row["customer"],   data_fmt)
    ws.write(row_idx, 3, row["product"],    data_fmt)
    ws.write(row_idx, 4, row["qty"],        data_fmt)
    ws.write(row_idx, 5, row["unit_price"], currency_fmt)
    ws.write(row_idx, 6, row["amount"],     currency_fmt)

# ── Column widths ─────────────────────────────────────────────
widths = [10, 14, 25, 20, 8, 14, 14]
for col, w in enumerate(widths):
    ws.set_column(col, col, w)

# ── Freeze header ─────────────────────────────────────────────
ws.freeze_panes(4, 0)

# ── Table ─────────────────────────────────────────────────────
ws.add_table(3, 0, 3 + len(data), len(headers) - 1, {
    "style": "Table Style Medium 2",
    "columns": [{"header": h} for h in headers],
})

# ── Print setup ───────────────────────────────────────────────
ws.set_landscape()
ws.fit_to_pages(1, 0)
ws.repeat_rows(3)

wb.close()
```

---

## PhpSpreadsheet (PHP)

```php
use PhpOffice\PhpSpreadsheet\Spreadsheet;
use PhpOffice\PhpSpreadsheet\Writer\Xlsx;
use PhpOffice\PhpSpreadsheet\Style\{Fill, Font, Alignment, Border, Color};

$spreadsheet = new Spreadsheet();
$ws = $spreadsheet->getActiveSheet();
$ws->setTitle('Sales Report');
$ws->getTabColor()->setRGB('1F3864');

// Title row
$ws->setCellValue('A1', 'Sales Report — Q1 2026');
$ws->mergeCells('A1:G1');
$ws->getRowDimension(1)->setRowHeight(36);
$ws->getStyle('A1')->applyFromArray([
    'font'      => ['name'=>'Calibri Light','size'=>16,'bold'=>true,'color'=>['rgb'=>'FFFFFF']],
    'fill'      => ['fillType'=>Fill::FILL_SOLID,'startColor'=>['rgb'=>'1F3864']],
    'alignment' => ['horizontal'=>Alignment::HORIZONTAL_LEFT,'vertical'=>Alignment::VERTICAL_CENTER,'indent'=>1],
]);

// Header row (row 4)
$headers = ['ID','Date','Customer','Product','Qty','Unit Price','Amount'];
$cols    = range('A', 'G');
foreach ($headers as $i => $header) {
    $cell = $cols[$i] . '4';
    $ws->setCellValue($cell, $header);
    $ws->getStyle($cell)->applyFromArray([
        'font'      => ['bold'=>true,'color'=>['rgb'=>'FFFFFF'],'size'=>11],
        'fill'      => ['fillType'=>Fill::FILL_SOLID,'startColor'=>['rgb'=>'1F3864']],
        'alignment' => ['horizontal'=>Alignment::HORIZONTAL_CENTER,'vertical'=>Alignment::VERTICAL_CENTER],
        'borders'   => ['allBorders'=>['borderStyle'=>Border::BORDER_THIN,'color'=>['rgb'=>'2E5D8A']]],
    ]);
}
$ws->getRowDimension(4)->setRowHeight(24);

// Data rows
foreach ($data as $rowIdx => $row) {
    $excelRow = $rowIdx + 5;
    $ws->setCellValue("A$excelRow", $row['id']);
    $ws->setCellValue("B$excelRow", $row['date']);
    $ws->getStyle("B$excelRow")->getNumberFormat()->setFormatCode('DD MMM YYYY');
    $ws->setCellValue("C$excelRow", $row['customer']);
    $ws->setCellValue("D$excelRow", $row['product']);
    $ws->setCellValue("E$excelRow", $row['qty']);
    $ws->setCellValue("F$excelRow", $row['unit_price']);
    $ws->getStyle("F$excelRow")->getNumberFormat()->setFormatCode('#,##0.00');
    $ws->setCellValue("G$excelRow", $row['amount']);
    $ws->getStyle("G$excelRow")->getNumberFormat()->setFormatCode('#,##0.00');
    $ws->getRowDimension($excelRow)->setRowHeight(18);
}

// Auto column widths
foreach (range('A', 'G') as $col) {
    $ws->getColumnDimension($col)->setAutoSize(true);
}

// Freeze header
$ws->freezePane('A5');

// Print settings
$ws->getPageSetup()->setOrientation(\PhpOffice\PhpSpreadsheet\Worksheet\PageSetup::ORIENTATION_LANDSCAPE);
$ws->getPageSetup()->setFitToPage(true);
$ws->getPageSetup()->setFitToWidth(1);
$ws->getPageSetup()->setRowsToRepeatAtTopByStartAndEnd(4, 4);

// Output
$writer = new Xlsx($spreadsheet);
$writer->save('report.xlsx');

// Stream to browser
header('Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
header('Content-Disposition: attachment; filename="report.xlsx"');
$writer->save('php://output');
```

---

## pandas Export

```python
import pandas as pd
from openpyxl import load_workbook

# Write multiple sheets
with pd.ExcelWriter("report.xlsx", engine="openpyxl") as writer:
    df_sales.to_excel(writer, sheet_name="Sales",    index=False, startrow=3)
    df_summary.to_excel(writer, sheet_name="Summary", index=False, startrow=3)

    # Post-process with openpyxl for formatting
    wb = writer.book
    for sheet_name in writer.sheets:
        ws = writer.sheets[sheet_name]
        # Add title row above the data
        ws.insert_rows(1, amount=3)
        ws["A1"] = sheet_name
        # ... apply styles as per openpyxl patterns above
```

---

## ExcelJS (Node.js)

Apply the same structure as openpyxl: title row → subtitle → spacer → table header → data rows → Table definition.

```javascript
const ExcelJS = require('exceljs');
const wb = new ExcelJS.Workbook();
const ws = wb.addWorksheet('Sales Report', { properties: { tabColor: { argb: 'FF1F3864' } } });

// Title (row 1), headers (row 4), data rows, then Table definition
const headers = ['ID', 'Date', 'Customer', 'Amount'];
ws.getRow(1).height = 36;
ws.mergeCells('A1:D1');
Object.assign(ws.getCell('A1'), {
  value: 'Sales Report',
  font: { name: 'Calibri Light', size: 16, bold: true, color: { argb: 'FFFFFFFF' } },
  fill: { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F3864' } },
  alignment: { vertical: 'middle', horizontal: 'left', indent: 1 },
});
ws.getRow(4).height = 24;
headers.forEach((h, i) => {
  const cell = ws.getRow(4).getCell(i + 1);
  cell.value = h;
  cell.font  = { bold: true, color: { argb: 'FFFFFFFF' }, size: 11 };
  cell.fill  = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F3864' } };
  cell.alignment = { vertical: 'middle', horizontal: 'center' };
});
data.forEach(row => {
  const r = ws.addRow([row.id, row.date, row.customer, row.amount]);
  r.height = 18;
  r.getCell(4).numFmt = '#,##0.00';
});
ws.addTable({ name: 'SalesData', ref: 'A4',
  style: { theme: 'TableStyleMedium2', showRowStripes: true },
  columns: headers.map(h => ({ name: h })),
  rows: data.map(r => [r.id, r.date, r.customer, r.amount]) });
ws.columns = [{ width: 10 }, { width: 14 }, { width: 25 }, { width: 14 }];
ws.views   = [{ state: 'frozen', ySplit: 4 }];
await wb.xlsx.writeFile(filename);
```

---

## Import / Parsing Patterns

### Python (pandas)

```python
import pandas as pd

def read_excel_safe(filepath: str, sheet: str = 0) -> pd.DataFrame:
    df = pd.read_excel(filepath, sheet_name=sheet, header=0)
    df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)

    # Validate expected columns
    required = {"ID", "Date", "Amount", "Status"}
    missing  = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # Type coercion
    df["Date"]   = pd.to_datetime(df["Date"],   dayfirst=True,  errors="coerce")
    df["Amount"] = pd.to_numeric(df["Amount"],  errors="coerce").fillna(0)
    df["ID"]     = df["ID"].astype(str).str.strip()
    df["Status"] = df["Status"].str.strip().str.title()

    # Drop rows with no ID
    df = df.dropna(subset=["ID"]).reset_index(drop=True)
    return df
```

### PHP (PhpSpreadsheet)

```php
$reader = \PhpOffice\PhpSpreadsheet\IOFactory::createReaderForFile($path);
$reader->setReadDataOnly(true);
$spreadsheet = $reader->load($path);
$ws   = $spreadsheet->getActiveSheet();
$rows = $ws->toArray(null, true, true, false);

$headers = array_shift($rows);  // first row = headers
$data    = [];
foreach ($rows as $row) {
    if (array_filter($row) === []) continue;  // skip blank rows
    $record = array_combine($headers, $row);
    $record['amount'] = (float) str_replace([',', '$'], '', $record['amount'] ?? 0);
    $record['date']   = \PhpOffice\PhpSpreadsheet\Shared\Date::excelToDateTimeObject($record['date']);
    $data[] = $record;
}
```

---

## Universal Non-Negotiables

1. **Always define a Table** over every data range — never just write rows
2. **Always set column widths** — auto-width with min 8, max 60
3. **Always apply number formats** to numeric columns — never leave as General
4. **Always freeze the header row** — users must see column names while scrolling
5. **Always set sheet tab colours** in multi-sheet workbooks
6. **Always set document properties** — Title, Author, Company
7. **Always validate incoming data** when reading Excel — strip whitespace, coerce types, fail on missing required columns
8. **Never output .xls** — always .xlsx (OOXML format)
9. **Never use merged cells in data rows** — only in title/header presentation rows
10. **Always test with real data** before production — especially date format and decimal separator locale issues
