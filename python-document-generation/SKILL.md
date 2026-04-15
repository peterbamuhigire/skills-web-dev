---
name: python-document-generation
description: Use when generating downloadable Excel dashboards, Word documents, or
  PDF reports from Python for end users of web, Android, and iOS SaaS apps — designer-grade
  branded output with charts, tables, formulas, conditional formatting, and multi-page
  layouts.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Python Document Generation

<!-- dual-compat-start -->
## Use When

- Use when generating downloadable Excel dashboards, Word documents, or PDF reports from Python for end users of web, Android, and iOS SaaS apps — designer-grade branded output with charts, tables, formulas, conditional formatting, and multi-page layouts.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `python-document-generation` or would be better handled by a more specific companion skill.
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

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
How we produce beautiful, branded, downloadable Excel / Word / PDF files from Python. These are end-user artifacts — professional enough to send to clients, file with auditors, or hand to executives.

**Prerequisites:** Load `python-modern-standards` and `python-saas-integration` before this skill. Load `python-data-analytics` when the input is a DataFrame.

## When this skill applies

- Generating multi-sheet Excel dashboards, financial statements, audit exports.
- Producing branded Word documents: reports, proposals, certificates, letters.
- Producing PDF reports: executive summaries, invoices, statements, audit trails.
- Embedding charts and tables in downloadable files.
- Delivering files to web, Android, and iOS clients with signed URLs.

## Output strategy — sync vs async

```text
File < 500KB AND < 1s to generate   -> Sidecar, return file bytes or stream
File 500KB – 5MB                     -> Sidecar, write to storage, return signed URL
File > 5MB OR > 2s to generate       -> Worker, enqueue job, notify on completion
Scheduled / recurring reports        -> Worker
```

Sync path: FastAPI endpoint returns `FileResponse` or a signed URL to a just-written file.

Async path: PHP enqueues job → worker generates file → worker writes to storage → worker notifies PHP via webhook or DB flag → PHP emails user or marks as ready.

See `python-saas-integration` → `references/file-handoff.md` for the full delivery pattern.

## Excel — openpyxl vs xlsxwriter

Both libraries are good. Pick per use case:

| Feature | openpyxl | xlsxwriter |
|---|---|---|
| Read existing .xlsx | Yes | No |
| Modify existing .xlsx | Yes | No |
| Write new .xlsx | Yes | Yes |
| Charts | Basic | Rich, Excel-like |
| Conditional formatting | Yes | Yes (more features) |
| Pivot tables | Read only | No |
| Write speed (large files) | Slower | Faster (memory-optimized mode) |
| Formulas | Yes | Yes |
| Images | Yes | Yes |

**Rule:** `xlsxwriter` for new multi-sheet dashboards with heavy formatting. `openpyxl` when you need to read/modify a template the client provided or when you need pivot tables.

## Excel dashboard patterns

A well-designed dashboard workbook has a consistent structure:

1. **Cover sheet** — tenant logo, report title, reporting period, generation timestamp.
2. **Summary KPIs** — the 5–10 numbers that matter, with conditional formatting (red/amber/green).
3. **Detail sheets** — one per entity (customers, products, regions) with sortable/filterable tables.
4. **Chart sheets** — trends over time, comparisons, breakdowns.
5. **Raw data sheet** — hidden or last; contains the underlying data so the user can audit.

Skeleton (xlsxwriter):

```python
import xlsxwriter

wb = xlsxwriter.Workbook(path, {"constant_memory": True, "default_date_format": "yyyy-mm-dd"})
brand = Brand.from_tenant(tenant)   # see branding-system.md

fmt_title = wb.add_format({"bold": True, "font_size": 18, "font_color": brand.primary, "font_name": "Inter"})
fmt_kpi_label = wb.add_format({"bold": True, "font_color": "#555", "font_size": 10})
fmt_kpi_value = wb.add_format({"bold": True, "font_size": 24, "font_color": brand.primary, "num_format": "#,##0"})
fmt_header = wb.add_format({"bold": True, "bg_color": brand.primary, "font_color": "white", "border": 1})
fmt_currency = wb.add_format({"num_format": "#,##0.00"})
fmt_percent = wb.add_format({"num_format": "0.0%"})

cover = wb.add_worksheet("Cover")
cover.hide_gridlines(2)
cover.insert_image("B2", logo_path, {"x_scale": 0.5, "y_scale": 0.5})
cover.write("B8", f"{tenant.name} — Sales Dashboard", fmt_title)
cover.write("B9", f"Period: {period_start:%b %Y} – {period_end:%b %Y}", fmt_kpi_label)
cover.write("B10", f"Generated {datetime.now(UTC):%Y-%m-%d %H:%M UTC}", fmt_kpi_label)
cover.set_column("B:B", 50)
```

Full multi-sheet dashboard template (KPIs, charts, conditional formatting, formulas, pivots when openpyxl, protection) in `references/excel-dashboard-patterns.md`.

## Word — python-docx with branded letterhead

python-docx is the standard. It gives fine control over paragraphs, runs, tables, and sections, but some things (page borders, complex headers) are set via direct OXML.

Structure of a branded report:

1. **Header** with logo + tenant name on every page.
2. **Footer** with page numbers + report metadata.
3. **Title page** (first page different) — title, subtitle, date.
4. **Body sections** — headings styled consistently (heading levels mapped to your brand type scale).
5. **Tables** — branded header row, zebra striping via row shading.
6. **Embedded images/charts** — rendered via matplotlib PNG export.

See `references/word-python-docx.md` for the letterhead template, style setup, and the helpers we use to avoid fighting with OXML for common needs.

## PDF — reportlab or weasyprint

Two philosophies:

- **reportlab (platypus):** programmatic canvas / flowables. Full control, pixel-perfect, best for financial statements, audit trails, anything tabular where layout precision matters.
- **weasyprint:** render HTML + CSS to PDF. Best when your report looks like a web page, when designers give you HTML, or when you want print styles that mirror your web dashboard.

**Pick weasyprint when:** marketing/brand-heavy layouts, designer-provided HTML, reusing existing CSS. Requires Cairo/Pango system libs on the server.

**Pick reportlab when:** data-dense financial output, fine-grained paginated tables, no system dependencies.

Minimal reportlab example:

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)

doc = SimpleDocTemplate(path, pagesize=A4,
                        leftMargin=20*mm, rightMargin=20*mm,
                        topMargin=25*mm, bottomMargin=20*mm)

styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Heading1"], textColor=colors.HexColor(brand.primary), fontName="Helvetica-Bold")

story = [
    Image(logo_path, width=40*mm, height=15*mm),
    Spacer(1, 10*mm),
    Paragraph(f"{tenant.name} — Monthly Report", h1),
    Paragraph(f"Period: {period}", styles["Normal"]),
    Spacer(1, 8*mm),
    Table(table_data, style=TableStyle([...]), repeatRows=1),
]
doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
```

See `references/pdf-reportlab.md` and `references/pdf-weasyprint.md`.

## Charts for embedding

Static PNG/SVG from matplotlib (for clarity, use a limited palette aligned to brand; set figure DPI to 150+ for print quality).

```python
import matplotlib
matplotlib.use("Agg")   # no GUI backend — critical on servers
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(7, 3.5), dpi=150)
ax.plot(df.index, df["mrr"], color=brand.primary, linewidth=2)
ax.fill_between(df.index, df["mrr"], color=brand.primary, alpha=0.1)
ax.set_title("MRR trend", pad=12)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(png_path, dpi=150, bbox_inches="tight")
plt.close(fig)   # always close — leaks otherwise
```

**Never use pyplot stateful API in a worker.** Always create explicit `fig, ax`. Always `plt.close(fig)` — matplotlib leaks memory otherwise and workers will OOM after a few hundred charts.

See `references/charts-for-embedding.md` for plotly static export and the style guide for chart brand consistency.

## Branding system

One source of truth for brand across all output types.

```python
@dataclass(frozen=True)
class Brand:
    primary: str           # hex, e.g., "#0B5FFF"
    secondary: str
    text: str = "#111827"
    muted: str = "#6B7280"
    success: str = "#059669"
    danger: str = "#DC2626"
    warning: str = "#D97706"
    font_family: str = "Inter"
    logo_path: Path
    footer_tagline: str = ""

    @classmethod
    def from_tenant(cls, tenant: Tenant) -> "Brand":
        return cls(
            primary=tenant.brand_color_primary or "#0B5FFF",
            secondary=tenant.brand_color_secondary or "#6B7280",
            logo_path=tenant.logo_path,
            footer_tagline=tenant.footer_tagline or "",
        )
```

Reuse the same `Brand` object in Excel (format colors), Word (style colors, logo), and PDF (reportlab colors, weasyprint CSS vars). See `references/branding-system.md`.

## Delivery to web / Android / iOS

- **MIME types:**
  - xlsx: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
  - docx: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
  - pdf: `application/pdf`
- **Filenames:** use `Content-Disposition: attachment; filename*=UTF-8''<url-encoded>.xlsx`. Support non-ASCII tenant names.
- **Signed URLs:** short-TTL (5–30 min), single-use where possible. Authorization is the URL itself.
- **Mobile handoff:** Android `DownloadManager` / iOS `URLSession` both handle signed URLs fine. For in-app preview, return a PDF (both platforms have native previewers); Excel/Word require a system app.
- **Filename convention:** `<tenant-slug>_<report-type>_<period>_<timestamp>.<ext>` — always include period and timestamp so users can keep multiple versions.

See `references/delivery-and-downloads.md`.

## Async generation flow (worker)

```text
1. PHP user requests report (clicks Generate)
2. PHP enqueues job with payload + idempotency_key
   -> responds 202 Accepted with job_id
3. Client polls /jobs/{id} every 3s OR PHP sends push/email when ready
4. Worker picks up job:
   a. Loads data (pandas / SQL)
   b. Generates file (xlsxwriter / python-docx / reportlab)
   c. Writes to storage under tenant_id/reports/{job_id}/...
   d. Updates job status: completed, file_url=signed_url
5. Client downloads the file
```

Always write the file to a temp path first, then atomic-rename on success. Never expose partial files.

## Performance

- **Stream when possible:** xlsxwriter `constant_memory=True` for > 100K rows. openpyxl has `write_only=True` mode.
- **Pre-compute totals in pandas**, write numbers (not formulas) for huge workbooks — formulas kill open time in Excel.
- **Charts are expensive:** generate in parallel only if `matplotlib.use("Agg")` + a process pool. Threads won't help for matplotlib.
- **Memory cap:** worker processes should have RLIMIT_AS (Linux) or systemd `MemoryMax=` set. Kill runaway jobs rather than swap.
- **Cache brand assets:** load logo bytes once per worker process, not per job.

See `references/performance.md`.

## Anti-patterns

- Generating a 10,000-row Excel inside a web request — use the worker.
- Embedding raw bytes of a huge image per row — link to external resource or resize to thumbnail.
- Not closing matplotlib figures — OOM after many jobs.
- Using pyplot global state in async/threaded code — race conditions, garbled charts.
- Building PDF pages by hand with `canvas.Canvas` when platypus flowables would do — fragile.
- Mixing date types in one column — Excel will auto-interpret badly. Keep dtypes consistent.
- Storing generated files indefinitely — enforce TTL + cleanup.
- Using tenant-supplied filename unsanitized — directory traversal risk.

## References

- `references/excel-openpyxl-vs-xlsxwriter.md`
- `references/excel-dashboard-patterns.md`
- `references/word-python-docx.md`
- `references/pdf-reportlab.md`
- `references/pdf-weasyprint.md`
- `references/charts-for-embedding.md`
- `references/branding-system.md`
- `references/delivery-and-downloads.md`
- `references/performance.md`

## See also

- `excel-spreadsheets` skill — design principles for professional Excel output (complements the Python implementation here).
- `professional-word-output` skill — design principles for Word documents.
- `data-visualization` skill — Knaflic's storytelling principles; apply these to every chart.
- `report-print-pdf` skill — HTML/mPDF counterpart in PHP.
