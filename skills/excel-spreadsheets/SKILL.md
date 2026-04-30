---
name: excel-spreadsheets
description: 'Generate world-class, professionally designed Microsoft Excel spreadsheets
  and handle all Excel/spreadsheet workflows. Use when: generating .xlsx files from
  apps or scripts (openpyxl, xlsxwriter, PhpSpreadsheet, pandas), importing or parsing...'
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Excel Spreadsheets Skill
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Generate world-class, professionally designed Microsoft Excel spreadsheets and handle all Excel/spreadsheet workflows. Use when: generating .xlsx files from apps or scripts (openpyxl, xlsxwriter, PhpSpreadsheet, pandas), importing or parsing...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `excel-spreadsheets` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Release evidence | Generated Excel workbook | Branded .xlsx artefact compliant with the excel-spreadsheets design standard | `docs/output/dashboard-2026-04-16.xlsx` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Excel done right looks like a financial analyst and a graphic designer collaborated on it. Done wrong, it's a wall of unformatted data nobody trusts. This skill covers both the code that generates Excel files and the design standards that make them world-class.

**Reference files (read when needed):**
- `references/design-standards.md` — layout, colour palettes, typography, table structure, conditional formatting, print setup
- `references/formulas-functions.md` — XLOOKUP, dynamic arrays, LET, LAMBDA, SUMIFS, MAXIFS/MINIFS, essential formula patterns
- `references/programmatic-generation.md` — openpyxl, xlsxwriter, PhpSpreadsheet, pandas — code patterns for generating professional Excel from apps
- `references/charts-pivot.md` — chart types, professional chart formatting, PivotTables, slicers, dashboards
- `references/financial-modeling.md` — PMT, PV, FV, NPV, IRR; Goal Seek, Data Tables, Scenario Manager, Solver; modeling golden rules; formula debugging
- `references/finance-accounting-workbooks.md` — bookkeeping ledgers, trial balance, AR/AP aging, bank reconciliation, fixed assets, budgets, cost accounting, statement checks, and finance dashboards
- `references/python-automation.md` — Excel–Python–Excel workflow, advanced read_excel(), 6-step export, pivot_table/merge/crosstab, email automation, =PY() function, xlwings
- `references/vba-macros.md` — recording/running macros, VBA golden rules, common patterns, keyboard shortcuts reference
- `references/quality-checklist.md` — pre-delivery checklist

*Sources: Microsoft Excel 365 Bible (Walkenbach/Alexander); Microsoft Excel Bible 2026; Ultimate Excel Formula & Function Reference Guide; Excel 2025 All-in-One; Excel 2019 Advanced Topics (George); Advanced Excel for Productivity (Urban); Automate Excel with Python (Wengler, 2026); Python in Excel Advanced (Van Der Post)*

---

## The Standard

Every spreadsheet produced must pass: **a data analyst and a designer would both be satisfied.** Specifically:

1. Data lives in a properly structured **Excel Table** — never raw ranges
2. Every number has an intentional format (currency, %, dates — never General)
3. Visual hierarchy is clear: header rows are distinct, data rows are readable
4. Formulas are correct, efficient, and use structured references where possible
5. The file opens correctly on any machine, in any regional locale

---

## Core Architecture Rules

### Rule 1 — Always use Excel Tables

Convert every data range to an Excel Table (`Ctrl+T`) immediately. Tables give you:
- Structured references: `=Table1[Amount]` instead of `=$C$2:$C$100`
- Auto-expansion when new rows are added
- Built-in filter arrows
- Automatic banded rows
- Named reference for programmatic access

**Programmatic:** In openpyxl, xlsxwriter, and PhpSpreadsheet, always add a `Table` (ListObject) definition over data ranges. See `references/programmatic-generation.md`.

### Rule 2 — One table per sheet, one topic per sheet

Never mix multiple unrelated datasets on one sheet. Use separate sheets with clear names. Sheet names: PascalCase or Title Case, max 20 characters, no spaces (use underscores if needed).

### Rule 3 — Separate data from presentation

- **Data sheets** — raw data in Tables, no decorative formatting, no merged cells
- **Report/Dashboard sheets** — formulas pulling from data sheets, full formatting treatment
- **Configuration sheets** (hidden) — lookup lists, parameters, constants

### Rule 4 — Never merge cells in data ranges

Merged cells break sorting, filtering, PivotTables, and programmatic reading. For visual centering of headers, use **Center Across Selection** instead (Format Cells → Alignment → Horizontal: Center Across Selection).

---

## Excel Table Design

Read `references/design-standards.md` for full colour palettes and formatting specs.

**Standard table anatomy:**

```
Row 1:  Sheet title / document header   ← merged+centred, large font, brand colour
Row 2:  Subtitle / date / filter info   ← smaller, grey
Row 3:  [blank spacer row]
Row 4:  Table header row                ← Excel Table header (bold, brand fill, white text)
Row 5+: Data rows                       ← banded, 11pt, left/right aligned by type
Last:   Totals row                      ← bold, top border, SUM/AVERAGE via Table totals row
```

**Column alignment rules:**
- Text columns → left-aligned
- Number/currency columns → right-aligned
- Date columns → right-aligned or centred
- Status/category columns → centred
- Header row → match column alignment (not always centred)

---

## Number Formats (critical — never leave as General)

| Data type | Format code | Example output |
|---|---|---|
| Currency (UGX/KES/TZS) | `#,##0` | 1,250,000 |
| Currency with decimals | `#,##0.00` | 1,250,000.00 |
| USD | `"$"#,##0.00` | $1,250.00 |
| Percentage | `0.00%` | 12.50% |
| Percentage (whole) | `0%` | 13% |
| Date (display) | `DD MMM YYYY` | 05 Apr 2026 |
| Date (ISO sort) | `YYYY-MM-DD` | 2026-04-05 |
| Large numbers | `#,##0.0,,"M"` | 1.3M |
| Negative red | `#,##0.00;[Red]-#,##0.00` | -500.00 (red) |
| Integer | `#,##0` | 42,000 |
| Duration (hours) | `[h]:mm` | 37:30 |

**Custom format anatomy:** `positive;negative;zero;text`

---

## Essential Formulas

Read `references/formulas-functions.md` for full formula patterns. Core rules:

**Use structured references in Tables:**
```excel
=SUMIFS(Sales[Amount], Sales[Region], [@Region], Sales[Status], "Paid")
```

**XLOOKUP over VLOOKUP always:**
```excel
=XLOOKUP([@ID], Products[ID], Products[Price], "Not found", 0)
```

**Dynamic arrays for reports:**
```excel
=FILTER(Sales[#All], (Sales[Region]="East")*(Sales[Month]=B2))
=SORT(UNIQUE(Sales[Category]))
=SEQUENCE(12, 1, DATE(2026,1,1), 30)  ← 12 monthly dates
```

**LET for complex formulas (readability + performance):**
```excel
=LET(
  data, FILTER(Sales[Amount], Sales[Status]="Paid"),
  avg, AVERAGE(data),
  IF(avg>100000, "Above target", "Below target")
)
```

---

## Data Validation

Every user-input column must have data validation. Never let free-form text corrupt a data column.

**Dropdown from a Table column:**
- Source: `=INDIRECT("Table1[Category]")` or a named range
- Input message: "Select a category from the list"
- Error alert: Stop — "Invalid entry. Please select from the list."

**Date range validation:**
- Allow: Date, Between, `=TODAY()-365`, `=TODAY()+365`

**Whole number range:**
- Allow: Whole number, Between, 0, 1000000

---

## Conditional Formatting

Apply to entire Table columns, not fixed ranges (so it auto-expands with the Table).

**Standard patterns:**
- **Heat map (numeric):** 3-colour scale, low=white, mid=yellow, high=brand colour
- **Above/below average:** Green fill for above, red fill for below
- **Status column:** Formula-based — `=[@Status]="Paid"` → green; `=[@Status]="Overdue"` → red
- **Data bars:** For ranking/comparison columns — no border, solid fill, brand colour
- **Duplicate detection:** `=COUNTIF(Table1[Email],[@Email])>1` → orange fill

---

## Professional Finishing

Read `references/design-standards.md` → Professional Finishing section.

**Freeze panes:** Always freeze the header row (and optionally the first column for wide tables). View → Freeze Panes → Freeze Top Row.

**Print setup (every sheet intended for printing):**
- Page Layout → Page Setup:
  - Orientation: Landscape for wide tables
  - Scale to fit: 1 page wide, auto tall
  - Print titles: Row 1 (and Table header row) to repeat on every page
  - Margins: Narrow (0.64 cm) for data tables; Normal for reports
  - Header: Document name left, date centre, page number right
  - Footer: "Page &P of &N" centred, confidential notice if needed

**Workbook hygiene:**
- Delete all unused sheets (Sheet1, Sheet2, Sheet3)
- Name every sheet clearly
- Set the first sheet as the active sheet on open
- Remove all #REF!, #VALUE!, #NAME? errors before delivery

---

## Programmatic Generation

Read `references/programmatic-generation.md` for full code patterns per language/library.

**Library selection:**

| Use case | Library | Language |
|---|---|---|
| Full formatting + charts | openpyxl | Python |
| Large data, max performance | xlsxwriter | Python |
| PHP apps | PhpSpreadsheet | PHP |
| Data analysis output | pandas + openpyxl | Python |
| Node.js apps | exceljs | JavaScript |

**Non-negotiable programmatic rules:**
1. Always define a `Table` (add_table / addTableStyleInfo) over data — never just write raw rows
2. Always set column widths — auto-width from content, with min 8 and max 60 characters
3. Always apply number formats to numeric columns — never leave as default
4. Always freeze the header row
5. Always set a tab colour per sheet for multi-sheet workbooks
6. Always use a professional table style (TableStyleMedium2 or equivalent)

---

## Import / Parsing Patterns

When reading Excel files in applications:

**Always:**
- Read with `header=0` (first row is headers) unless the file has multi-row headers
- Strip whitespace from string columns after reading
- Validate expected columns exist before processing — fail early with clear error messages
- Parse date columns explicitly (don't rely on auto-detection)
- Handle merged header cells by forward-filling merged values

**Never:**
- Assume column order — always reference by column name, not index
- Assume data starts at row 1 — check for title rows above the table
- Trust data types — validate and coerce explicitly

**Python pattern:**
```python
import pandas as pd

df = pd.read_excel("file.xlsx", sheet_name="Sales", header=0)
df.columns = df.columns.str.strip()  # remove whitespace from headers
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
df = df.dropna(subset=["ID"])  # drop rows with no ID
```

---

## Financial Functions Quick Reference

Read `references/financial-modeling.md` for full formulas, examples, and What-If tools. Read `references/finance-accounting-workbooks.md` when the workbook is a ledger, trial balance, aging report, reconciliation, financial model, budget, forecast, cost model, or finance dashboard.

| Function | Use case | Key rule |
|---|---|---|
| `=PMT(rate, nper, pv)` | Monthly loan/mortgage payment | Rate and nper must match time unit (÷12 for monthly) |
| `=PV(rate, nper, pmt)` | Present value of an annuity | Cash inflows = positive, outflows = negative |
| `=FV(rate, nper, pmt)` | Future value of savings/investment | pmt is negative (cash going out) |
| `=NPV(rate, cashflows)` | Net present value | Add period-0 investment separately outside NPV() |
| `=IRR(cashflows)` | Internal rate of return | First value should be negative (initial outlay) |

**What-If tools:**
- **Goal Seek** — find the input that achieves a target output (Data → What-If Analysis → Goal Seek)
- **Scenario Manager** — store and compare named sets of input values (Base/Optimistic/Pessimistic)
- **Data Tables** — calculate output across a range of input values (1-variable or 2-variable)
- **Solver** — optimise across multiple variables with constraints (requires Solver add-in)

---

## VBA Macros

Read `references/vba-macros.md` for full VBA patterns and keyboard shortcuts.

**Record a macro:** View → Macros → Record Macro (or status bar button bottom-left)
**Run a macro:** `Alt+F8` or assigned shortcut key
**Edit a macro:** `Alt+F11` opens the VBA editor

**Critical shortcuts:**
- `Ctrl+Arrow` — jump to end of data range
- `F2` — edit mode with colour-coded cell references
- `F4` — toggle `$A$1` → `A$1` → `$A1` → `A1` (absolute/relative)
- `Ctrl+Shift+Enter` — legacy array formula (prefer dynamic arrays)
- `Alt+H+O+I` — auto-fit column width

---

## Customisation Quick Reference

| What to change | Where |
|---|---|
| Table colour palette | `references/design-standards.md` → Colour Palettes |
| Formula patterns | `references/formulas-functions.md` |
| openpyxl/xlsxwriter code | `references/programmatic-generation.md` |
| Chart types and formatting | `references/charts-pivot.md` |
| Financial functions & What-If | `references/financial-modeling.md` |
| Finance/accounting workbooks | `references/finance-accounting-workbooks.md` |
| Python automation & =PY() | `references/python-automation.md` |
| VBA macros & keyboard shortcuts | `references/vba-macros.md` |
| Pre-delivery checks | `references/quality-checklist.md` |
