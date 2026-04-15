# Excel: openpyxl vs xlsxwriter

Choose per use case. Both libraries are production-ready. They solve different problems.

## Feature matrix

| Capability | openpyxl | xlsxwriter |
|---|---|---|
| Read existing `.xlsx` | Yes | No |
| Modify existing `.xlsx` in place | Yes | No |
| Write new `.xlsx` from scratch | Yes | Yes |
| Memory-efficient streaming write | `write_only=True` | `constant_memory=True` |
| Rich native charts | Limited set | Full set, closest to Excel |
| Conditional formatting | Yes | Yes, more rule types |
| Data validation (dropdowns) | Yes | Yes |
| Pivot tables | Read-only | No |
| Tables (listObjects) | Yes | Yes |
| Formulas | Yes | Yes (array formulas supported) |
| Images | Yes | Yes, richer scaling options |
| Sparklines | Limited | Yes |
| Named ranges | Yes | Yes |
| Cell protection / sheet protection | Yes | Yes |
| VBA passthrough | `keep_vba=True` | `add_vba_project()` |
| Write speed, 100k+ rows | Slower | Faster |
| Peak memory on large writes | Higher | Lower with constant_memory |
| Chart sheets | Yes | Yes |
| Defined print areas / titles | Yes | Yes |

## Decision rules

```text
Need to READ or MODIFY an existing .xlsx           -> openpyxl
Writing a NEW dashboard with charts + formatting   -> xlsxwriter
Workbook > 50,000 rows OR > 50 MB expected         -> xlsxwriter with constant_memory=True
Need pivot tables in output                        -> openpyxl (read/preserve) or template-based
Client provided an .xlsx template to populate      -> openpyxl
Need VBA macros preserved                          -> openpyxl with keep_vba=True
Heavy chart count (> 20 charts)                    -> xlsxwriter (faster native chart engine)
```

## Pros and cons

### openpyxl

Pros:

- Round-trips existing workbooks. The only option when a client, auditor, or finance team hands you a pre-designed `.xlsx` and you must inject data without breaking their formulas, macros, pivot tables, or conditional formatting.
- `write_only=True` streams rows without holding the worksheet in memory.
- Access to full OOXML via the underlying model when you need to poke at cell XML directly.

Cons:

- Chart styling is thinner than xlsxwriter. Some Excel-native chart options must be set via low-level XML.
- Slower on large writes in the default (non-write_only) mode.
- `write_only=True` forbids random access to cells — you must append rows in order.

### xlsxwriter

Pros:

- Chart API mirrors Excel options closely. `set_style`, `set_legend`, `set_plotarea`, trendlines, error bars, data labels — all first-class.
- `constant_memory=True` keeps memory flat regardless of row count. Required for huge exports.
- Richer conditional formatting rule set (data bars, icon sets, colour scales with midpoints).
- Faster, cleaner format object model via `add_format(dict)`.

Cons:

- Cannot read or modify existing files. Write-only, always.
- No pivot tables.
- `constant_memory=True` forbids writing rows out of order and disables some operations (e.g., `merge_range` after subsequent row writes).

## Migrating between them

You rarely migrate — you pick per artefact. When you do:

```python
# openpyxl -> xlsxwriter
# openpyxl uses tuple-of-tuples for styles; xlsxwriter uses a format dict.
# Rule of thumb: re-declare formats. Don't try to translate styles mechanically.

# xlsxwriter -> openpyxl
# Usually happens when you now need to MODIFY the file post-generation.
# Generate with xlsxwriter, then reopen with openpyxl load_workbook(keep_vba=False).
```

Common gotcha: cell coordinates. Both use A1 notation and zero-indexed `(row, col)`, but xlsxwriter's `write` accepts either; openpyxl prefers `ws["A1"]` or `ws.cell(row, column)` (both 1-indexed).

## Hybrid pattern — read with openpyxl, write with xlsxwriter

When a client gives you a designed template you must populate and you also need to add new sheets with heavy formatting, use both.

```python
from pathlib import Path
import openpyxl
import xlsxwriter

def populate_template_and_append_dashboard(
    template_path: Path,
    output_path: Path,
    raw_rows: list[dict],
    kpis: dict,
    brand,
):
    # 1. Open the template, write raw data into a known sheet.
    wb = openpyxl.load_workbook(template_path, keep_vba=True)
    raw_ws = wb["RawData"]
    raw_ws.delete_rows(2, raw_ws.max_row)  # keep header row
    for i, row in enumerate(raw_rows, start=2):
        raw_ws.cell(row=i, column=1, value=row["date"])
        raw_ws.cell(row=i, column=2, value=row["amount"])
    wb.save(output_path)
    wb.close()

    # 2. Reopen via xlsxwriter is NOT possible — xlsxwriter cannot modify.
    # Instead: write the NEW dashboard sheets into a SEPARATE workbook,
    # then merge by copying values back via openpyxl.
    #
    # Easier production pattern: generate the full workbook in xlsxwriter
    # using the template's formulas and layout replicated in code.
```

In practice, the cleanest hybrid is:

1. Use openpyxl for any file that MUST retain the client's template.
2. Use xlsxwriter for any file you generate end-to-end.
3. Do not try to merge two generated workbooks at runtime. Instead, keep the template's design in code and regenerate with xlsxwriter.

## Streaming writers

```python
# openpyxl write_only — large exports without formatting
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell

wb = Workbook(write_only=True)
ws = wb.create_sheet("Transactions")
header = ["id", "date", "amount", "tenant_id"]
ws.append(header)
for row in stream_rows_from_db():
    ws.append([row["id"], row["date"], row["amount"], row["tenant_id"]])
wb.save(path)
```

```python
# xlsxwriter constant_memory — large exports WITH formatting
import xlsxwriter

wb = xlsxwriter.Workbook(path, {"constant_memory": True, "default_date_format": "yyyy-mm-dd"})
ws = wb.add_worksheet("Transactions")
hdr = wb.add_format({"bold": True, "bg_color": "#0B5FFF", "font_color": "white"})
ws.write_row(0, 0, ["id", "date", "amount", "tenant_id"], hdr)
for r, row in enumerate(stream_rows_from_db(), start=1):
    ws.write_row(r, 0, [row["id"], row["date"], row["amount"], row["tenant_id"]])
wb.close()
```

Rule: in `constant_memory` mode, once you leave a row, you cannot go back to it. Plan row order before you start writing.

## Version pinning

Pin both in `pyproject.toml`. Minor releases have introduced subtle behaviour changes (e.g., openpyxl 3.1's handling of `datetime.date` vs `datetime.datetime`). Lock to tested versions:

```toml
[project]
dependencies = [
  "openpyxl==3.1.5",
  "xlsxwriter==3.2.0",
]
```

## Testing guidance

- Unit-test the data layer (what rows, what totals). Do not unit-test the visual layer.
- For regression, open the generated file with `openpyxl.load_workbook()` and assert cell values, not styles.
- Smoke test: open the file in Excel on a clean machine and confirm charts render and formulas evaluate without errors.

## Anti-patterns

- Loading a 200 MB `.xlsx` with openpyxl in default mode — read-only mode or streaming is required.
- Calling `wb.close()` on xlsxwriter inside a `try` without a `finally` — half-written files leak to disk.
- Writing rows out of order in `constant_memory` or `write_only` mode — silent data loss or exceptions.
- Mixing formula strings and pre-computed numbers inconsistently — Excel will recalc some but not others.
- Trusting xlsxwriter's `strings_to_numbers=True` — explicit typing is safer.
