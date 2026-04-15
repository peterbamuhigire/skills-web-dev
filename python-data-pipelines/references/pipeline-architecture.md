# Pipeline Architecture

Every pipeline in this SaaS obeys the same five invariants. Deviate only with a written reason.

## The five invariants

1. **Idempotent.** Running the pipeline twice with the same input produces the same end state. No duplicate rows, no doubled emails, no doubled ledger entries. Enforced by a natural key or an explicit `idempotency_key` at the load step.
2. **Resumable.** If the process dies at record 4,823 of 10,000, the next run continues from where it stopped. Enforced by a watermark or checkpoint persisted **before** the crash could occur (i.e., per-batch, not at the end).
3. **Observable.** Every run emits a start event, progress heartbeats, and a terminal event. Every run writes a row into the `pipeline_runs` table. Metrics: records in, records ok, records DLQ, duration, lag.
4. **Validated.** Inputs flow through Pydantic at the boundary. Per-record failures go to the dead-letter queue. Batch-level failures (schema drift, auth failure) stop the run and raise an alert.
5. **Multi-tenant-safe.** Every record carries `tenant_id`. Every step validates it. Credentials are fetched per tenant. Logs are tagged with `tenant_id` on every line.

## Canonical shape

```text
Source  ->  Extract  ->  Validate  ->  Transform  ->  Load  ->  Verify
               |                                                   ^
               v                                                   |
         Dead-letter  <----  validation failures                   |
                                                                   |
                             Reconciliation  <---------------------+
```

Each stage has one responsibility. Do not collapse them.

- **Extract** — pull raw bytes/rows from the source. No parsing, no mapping. Emit a stream of `(tenant_id, raw_payload, source_id)` tuples.
- **Validate** — Pydantic model per record. Failures routed to DLQ with the original payload intact.
- **Transform** — map validated input to the domain shape. Decimals for money, UTC for timestamps, canonical enum values.
- **Load** — upsert into the destination (MySQL). Transactional per batch, not per run.
- **Verify** — counts match, totals match, hash check where applicable.
- **Reconciliation** — separate job, runs on a slower cadence, compares source-of-truth to what we loaded.

## Watermarks and checkpoints

A **watermark** is the high-water mark from the source: the latest `updated_at`, the latest Stripe `created` timestamp, the last cursor token. Stored per `(tenant_id, pipeline_name)`.

A **checkpoint** is a mid-run position saved so resumption can skip already-loaded batches. Stored per `(tenant_id, pipeline_name, run_id)`.

### Rules

- Save the watermark **after** a successful batch commit, never before.
- Use `SELECT ... FOR UPDATE` on the watermark row during reads inside the run to prevent two schedulers racing.
- Always store watermarks as timezone-aware UTC timestamps or opaque cursor strings. Never use naive local time.
- Overlap the query window by a safety margin (e.g. `watermark - 5 minutes`) because source systems often publish events slightly out of order. Rely on upserts to dedupe.

### Schema

```sql
CREATE TABLE pipeline_watermarks (
  tenant_id        BIGINT UNSIGNED NOT NULL,
  pipeline_name    VARCHAR(128) NOT NULL,
  watermark_value  VARCHAR(64) NOT NULL,   -- ISO8601 or opaque cursor
  watermark_ts     DATETIME(3) NOT NULL,   -- parsed UTC
  updated_at       DATETIME(3) NOT NULL,
  PRIMARY KEY (tenant_id, pipeline_name)
) ENGINE=InnoDB;

CREATE TABLE pipeline_checkpoints (
  run_id         BINARY(16) NOT NULL,
  tenant_id      BIGINT UNSIGNED NOT NULL,
  pipeline_name  VARCHAR(128) NOT NULL,
  batch_index    INT UNSIGNED NOT NULL,
  cursor         VARCHAR(256) NOT NULL,
  saved_at       DATETIME(3) NOT NULL,
  PRIMARY KEY (run_id, batch_index)
) ENGINE=InnoDB;
```

### Reading and writing

```python
from datetime import datetime, UTC, timedelta
from sqlalchemy import text

SAFETY_WINDOW = timedelta(minutes=5)

def load_watermark(conn, tenant_id: int, pipeline: str) -> datetime | None:
    row = conn.execute(
        text("""
            SELECT watermark_ts FROM pipeline_watermarks
            WHERE tenant_id=:t AND pipeline_name=:p
            FOR UPDATE
        """),
        {"t": tenant_id, "p": pipeline},
    ).first()
    return (row.watermark_ts - SAFETY_WINDOW) if row else None

def save_watermark(conn, tenant_id: int, pipeline: str, value: datetime) -> None:
    conn.execute(
        text("""
            INSERT INTO pipeline_watermarks
                (tenant_id, pipeline_name, watermark_value, watermark_ts, updated_at)
            VALUES (:t, :p, :v, :v, UTC_TIMESTAMP(3))
            ON DUPLICATE KEY UPDATE
                watermark_value=VALUES(watermark_value),
                watermark_ts=VALUES(watermark_ts),
                updated_at=UTC_TIMESTAMP(3)
        """),
        {"t": tenant_id, "p": pipeline, "v": value.isoformat()},
    )
```

## Batch commits

Commit every 1,000–10,000 rows. Pick based on row size and the destination engine's write throughput.

Rules:

- One row = no batching; commit per row. Rarely right.
- < 1k rows per run = one transaction. Fine.
- 1k–100k rows per run = batches of 1k–10k.
- Bulk loads (>100k) = consider bulk load tools or `LOAD DATA INFILE` with staging tables.

```python
BATCH_SIZE = 2_000

def load_batched(conn, tenant_id: int, records: Iterable[DomainModel]) -> LoadResult:
    batch: list[DomainModel] = []
    ok = 0
    for rec in records:
        batch.append(rec)
        if len(batch) >= BATCH_SIZE:
            ok += _commit_batch(conn, tenant_id, batch)
            batch.clear()
    if batch:
        ok += _commit_batch(conn, tenant_id, batch)
    return LoadResult(ok=ok)

def _commit_batch(conn, tenant_id: int, batch: list[DomainModel]) -> int:
    with conn.begin():
        conn.execute(upsert_stmt(tenant_id), [r.model_dump() for r in batch])
    return len(batch)
```

Batch boundaries are natural checkpoints. Save the cursor **inside** the same transaction where you commit the batch, so the checkpoint and the data move together. If that is not possible (two separate stores), always write the checkpoint **after** the data, and design the load to be idempotent so re-running the batch is safe.

## Reconciliation jobs

Reconciliation is a distinct pipeline that compares source totals to what we loaded. It runs on a slower cadence (daily, hourly for financial data) than the sync itself.

A reconciliation record asks: "Does the source say we have X, and do we have X?" If not, open a reconciliation issue.

```python
def reconcile_stripe_invoices(tenant_id: int, day: date) -> ReconciliationResult:
    source_total = stripe_total_for_day(tenant_id, day)          # sum amount_due
    local_total  = db_invoice_total_for_day(tenant_id, day)
    diff = source_total - local_total
    if abs(diff) > 0:
        raise_reconciliation_issue(
            tenant_id=tenant_id,
            pipeline="stripe.invoices",
            day=day,
            source_total=source_total,
            local_total=local_total,
            diff=diff,
        )
    return ReconciliationResult(tenant_id, day, source_total, local_total, diff)
```

Design rules:

- Reconciliation must never write to the main tables. It only reports.
- Reconciliation windows should be closed (e.g. "yesterday" not "today") so late-arriving events do not create false alarms.
- Small tolerances are acceptable for currency conversion rounding but must be explicit (e.g. `abs(diff) <= 1` for cents). Never a percentage.

## Rollback strategy

Define a rollback path for every destructive pipeline **before** shipping it.

Options, in order of preference:

1. **Idempotent upsert with version field.** Replay the source for the affected window; the upsert heals the bad rows. Preferred. Requires the source to be re-queryable.
2. **Quarantine + replay.** Mark affected rows as `quarantined=1`, then rerun. Downstream code must ignore quarantined rows.
3. **Staging table swap.** Load into a staging table, verify counts and totals, then `RENAME TABLE` atomically. Strong guarantee but heavy for incremental work.
4. **Point-in-time restore.** Last resort. Requires DBA and coordinated downtime.

Document the rollback in the pipeline's runbook: what triggers it, the exact command, and the verification step.

## Failure classes and responses

| Failure | Scope | Response |
|---|---|---|
| Invalid record | Single row | DLQ it, continue |
| Transient API error (429, 5xx) | Request | Retry with backoff + jitter |
| Auth expired | Run | Refresh token, retry once, then fail the run |
| Schema drift (new required field) | Run | Fail fast, alert, do not update watermark |
| DB constraint violation | Batch | Rollback batch, DLQ the batch, continue |
| Destination unavailable | Run | Fail, preserve watermark, alert |

## Pipeline state machine

```text
pending -> running -> (succeeded | failed | partial)
                       |
                       +-- partial: some records loaded, some DLQ'd; watermark advanced
                       +-- failed:  nothing persisted OR error before watermark save; watermark NOT advanced
                       +-- succeeded: all records loaded; watermark advanced
```

`partial` is a success in terms of advancing the pipeline; operators still need to drain the DLQ, but the pipeline itself is healthy.

## Anti-patterns

- Saving the watermark before the commit, "to avoid forgetting."
- One transaction for the whole run. Lock contention, huge undo log, all-or-nothing.
- Running reconciliation against today's data.
- Skipping DLQ because "we'll just log it." Silent data loss.
- Sharing a single watermark row across tenants.
- Reading the watermark without `FOR UPDATE` in a multi-worker setup.
