---
name: python-data-pipelines
description: Use when building ETL jobs, document intelligence pipelines, OCR, PDF/Excel
  ingestion, image/media processing, or external-API sync pipelines in Python — idempotent
  scheduled jobs with validation, dead-letter queues, and multi-tenant isolation.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Python Data Pipelines

<!-- dual-compat-start -->
## Use When

- Use when building ETL jobs, document intelligence pipelines, OCR, PDF/Excel ingestion, image/media processing, or external-API sync pipelines in Python — idempotent scheduled jobs with validation, dead-letter queues, and multi-tenant isolation.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `python-data-pipelines` or would be better handled by a more specific companion skill.
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
Bring data into the SaaS from outside systems and unstructured inputs — APIs, files, images, PDFs — and transform it for downstream use. Every pipeline here is idempotent, validated, and observable.

**Prerequisites:** Load `python-modern-standards` and `python-saas-integration` before this skill.

## When this skill applies

- Syncing data from external APIs: Stripe, payment gateways, bank feeds, tax portals, government APIs.
- Extracting structured data from uploaded receipts, invoices, IDs (OCR).
- Parsing PDFs or Excel files uploaded by tenants.
- Processing uploaded images: resize, optimize, thumbnail, watermark.
- Scheduled jobs that transform data between stores.
- Reconciliation jobs that compare our records against external source-of-truth.

## Pipeline architecture principles

Every pipeline enforces the same five properties:

1. **Idempotent** — same input twice = same end state. No duplicate records, no doubled side effects. Deduplicate by natural key or `idempotency_key`.
2. **Resumable** — interrupted midway, the next run picks up where it left off (via cursor, watermark, or checkpoint).
3. **Observable** — every run emits a start event, progress events, and a terminal event (success/failure/partial). Metrics for rows in/out, duration, lag.
4. **Validated** — inputs parsed through Pydantic at ingestion. Invalid records go to a dead-letter queue, not to /dev/null.
5. **Multi-tenant-safe** — every record carries `tenant_id`; every pipeline step validates it.

See `references/pipeline-architecture.md`.

## The canonical pipeline shape

```text
Source  ->  Extract  ->  Validate  ->  Transform  ->  Load  ->  Verify
               |                                                   ^
               v                                                   |
         Dead-letter  <----  validation failures                   |
                                                                   |
                             Reconciliation  <---------------------+
```

- **Extract** — pull data from the source (API, file, queue).
- **Validate** — Pydantic model per record. Fail fast on a malformed batch; per-record failures go to DLQ.
- **Transform** — map to domain shape. Decimal for money, UTC for timestamps, canonical enums.
- **Load** — upsert into MySQL (or destination). Transactional per tenant or per batch.
- **Verify** — count checks, hash checks, reconciliation against source totals.

## ETL / external API sync

Typical pattern — nightly Stripe invoice sync:

```python
from datetime import datetime, UTC
import structlog
from stripe import StripeClient
from sqlalchemy import text
from .checkpoints import load_watermark, save_watermark

log = structlog.get_logger()

def sync_stripe_invoices(tenant_id: int) -> SyncResult:
    watermark = load_watermark(tenant_id, "stripe.invoices") or datetime(1970, 1, 1, tzinfo=UTC)
    client = StripeClient(api_key=secrets.for_tenant(tenant_id).stripe_api_key)

    total, ok, failed = 0, 0, 0
    for page in client.invoices.list({"created": {"gte": int(watermark.timestamp())}, "limit": 100}):
        for raw in page.data:
            total += 1
            try:
                model = StripeInvoice.model_validate(raw)   # Pydantic, strict
                upsert_invoice(tenant_id, model)            # ON DUPLICATE KEY UPDATE
                ok += 1
            except ValidationError as e:
                send_to_dlq(tenant_id, "stripe.invoices", raw.id, str(e))
                failed += 1

    save_watermark(tenant_id, "stripe.invoices", datetime.now(UTC))
    log.info("stripe_sync_done", tenant_id=tenant_id, total=total, ok=ok, failed=failed)
    return SyncResult(total=total, ok=ok, failed=failed)
```

Key features:
- **Watermark-based incremental** — only fetches new data since last run.
- **Upsert, not insert** — reruns don't duplicate.
- **Per-record DLQ** — one bad record doesn't kill the batch.
- **Per-tenant credentials** — pulled from secrets vault by tenant.

Rate limits, pagination, auth refresh: all in `references/etl-external-apis.md`.

## Document intelligence — OCR

Tesseract is the default. For machine-printed receipts and invoices it's accurate enough. For handwriting or low-quality scans, consider Google Vision / AWS Textract, but budget the cost.

```python
import pytesseract
from PIL import Image, ImageOps
import cv2

def ocr_receipt(path: Path) -> str:
    img = cv2.imread(str(path))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Adaptive threshold for uneven lighting
    proc = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    text = pytesseract.image_to_string(proc, lang="eng", config="--psm 6")
    return text
```

Preprocessing dominates accuracy:

1. Grayscale, then denoise.
2. Adaptive threshold (not global).
3. Deskew (hough lines).
4. Upscale 2×–3× for small fonts.
5. Remove borders/shadows.

See `references/ocr-tesseract.md` for multi-language, PSM modes, confidence extraction, and the decision table for when to use a cloud OCR service.

## PDF extraction

Two tools, different jobs:

- **pdfplumber** — text PDFs (born-digital). Extracts text with position info, and tables when the layout is regular.
- **camelot** — tables in PDFs, better than pdfplumber for complex grids.
- **ocrmypdf** — wraps Tesseract to OCR scanned PDFs in place, producing a searchable PDF.

```python
import pdfplumber

with pdfplumber.open(path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        tables = page.extract_tables(table_settings={"vertical_strategy": "lines"})
```

Never trust uploaded PDFs — validate MIME type, size, and run through a scanner if doing anything beyond text extraction. See `references/pdf-extraction.md`.

## Image / media processing

Pillow for most work. For heavy resizing / format conversion, add `pillow-simd` for a speed bump.

```python
from PIL import Image, ImageOps

def make_thumbnail(src: Path, dst: Path, size: tuple[int, int] = (400, 400)) -> None:
    with Image.open(src) as img:
        img = ImageOps.exif_transpose(img)   # honor rotation EXIF
        img.thumbnail(size, Image.LANCZOS)
        img = img.convert("RGB")
        img.save(dst, "WEBP", quality=85, method=6)
```

**Always strip EXIF** on user uploads before serving publicly — GPS coordinates leak. Use `Image.open(src); data = list(img.getdata()); new = Image.new(img.mode, img.size); new.putdata(data)` or `piexif.remove`.

**Watermarking:** render over a corner; scale watermark to image width. See `references/image-processing-pillow.md`.

## Scheduling

Three options:

- **cron + uv run script.py** — simplest. Great for once-daily jobs on a single host.
- **APScheduler** — in-process scheduler. Good when you want Python-managed cron-ish behavior without system cron.
- **Celery beat** — if you already run Celery for workers, use beat for schedules.
- **RQ Scheduler** (rq-scheduler) — if you use RQ.

**Rule:** use the simplest one that meets the need. Don't adopt Celery for one nightly job.

Always make scheduled jobs:
- Mutex against themselves (Redis lock with TTL) — long jobs can't overlap.
- Idempotent — safe to rerun.
- Tolerant of skipped runs — if Monday's job missed, Tuesday's should still do the right thing.

See `references/scheduling.md`.

## Validation & dead-letter queue

Pydantic at the boundary, always:

```python
class StripeInvoice(BaseModel):
    id: str = Field(..., pattern=r"^in_[a-zA-Z0-9]+$")
    customer: str
    amount_due: int = Field(..., ge=0)
    currency: str = Field(..., pattern=r"^[a-z]{3}$")
    status: Literal["draft", "open", "paid", "uncollectible", "void"]
    created: int
    model_config = {"extra": "ignore"}   # tolerate new fields from the API
```

DLQ design:
- Same Redis/DB as main queue, different namespace.
- Record: `{tenant_id, pipeline, source_id, payload, error, first_seen, retry_count}`.
- Human replay tool: mark fixed → re-enqueue into main flow.
- Alert when DLQ depth > threshold per tenant.

See `references/validation-and-deadletter.md`.

## Multi-tenant pipelines

- **Per-tenant credentials** — every external source may have different API keys/tokens per tenant. Store in a vault (Hashicorp Vault, AWS Secrets Manager, or encrypted in DB) keyed by `(tenant_id, integration_name)`.
- **Rate limit per tenant** — one noisy tenant shouldn't starve others. Use a token-bucket keyed by `tenant_id`.
- **Concurrency budget per tenant** — cap at N parallel jobs per tenant.
- **Isolation in logs** — log `tenant_id` on every line. Never log another tenant's data in a given tenant's job context.

See `references/multi-tenant-pipelines.md`.

## Observability for pipelines

Every pipeline run should answer these questions from a dashboard:

- When did it last run?
- Did it succeed, partially succeed, or fail?
- How many records in / out / DLQ?
- How long did it take?
- What's the lag between source and destination (freshness)?

Standard metrics (Prometheus):
- `pipeline_run_total{pipeline, tenant, status}`
- `pipeline_records_total{pipeline, tenant, outcome}`  (outcome = ok | failed | skipped)
- `pipeline_duration_seconds{pipeline, tenant}` (histogram)
- `pipeline_lag_seconds{pipeline, tenant}`        (gauge — how stale is the destination)

Alerts:
- No successful run in > 2x expected interval.
- DLQ growth rate > threshold.
- Lag > SLA.

See `references/observability-pipelines.md`.

## Anti-patterns

- **Full reloads instead of incremental** — wastes time, hammers the source. Use watermarks unless the source is tiny.
- **One giant transaction for a 100K-row batch** — lock contention + all-or-nothing rollback. Batch in 1,000–10,000 row chunks, commit between.
- **Swallowing exceptions per record without DLQ** — silent data loss. Always route failures somewhere.
- **Scheduling in app code with `while True: time.sleep(3600)`** — use a real scheduler.
- **Storing external raw responses and the transformed record in the same row** — mix of concerns. Store raw in a staging/audit table, transformed in the canonical table.
- **Using the same Stripe client across tenants** — cross-tenant credential bleed. One client per tenant.
- **No rollback plan for bad sync data** — build a "quarantine last N hours" path before you need it.

## Read next

- `python-data-analytics` — to analyze the data once loaded.
- `python-document-generation` — to produce reports from pipeline outputs.
- `photo-management` — for the web/mobile upload side of image pipelines.

## References

- `references/pipeline-architecture.md`
- `references/etl-external-apis.md`
- `references/ocr-tesseract.md`
- `references/pdf-extraction.md`
- `references/image-processing-pillow.md`
- `references/scheduling.md`
- `references/validation-and-deadletter.md`
- `references/multi-tenant-pipelines.md`
- `references/observability-pipelines.md`
