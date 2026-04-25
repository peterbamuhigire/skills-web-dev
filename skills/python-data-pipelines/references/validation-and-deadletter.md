# Validation and Dead-Letter Queue

Every pipeline has exactly one validation boundary and exactly one DLQ. Records are either valid (flow onward) or DLQ'd (replayable later). No third path.

## Pydantic at the boundary

Validate once, at ingestion. Downstream code sees only validated domain models.

### Two modes, two rules

| Source | `extra` | `strict` | Why |
|---|---|---|---|
| Third-party API response (Stripe, bank) | `"ignore"` | No | Vendors add fields frequently. Silent-ignore keeps the pipeline stable across minor API changes. |
| User-uploaded file (CSV, Excel, JSON) | `"forbid"` | Yes | Any extra column is operator error or an attack. Fail loudly. |
| Webhook from a vendor | `"ignore"` | No | Same reason as API — but verify signature first. |
| Internal queue message | `"forbid"` | Yes | Same team ships both sides. Schema drift is a bug. |

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal
from decimal import Decimal
from datetime import datetime

# External API — tolerant
class StripeInvoice(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(pattern=r"^in_[A-Za-z0-9]+$")
    customer: str
    amount_due: int = Field(ge=0)
    currency: str = Field(pattern=r"^[a-z]{3}$")
    status: Literal["draft", "open", "paid", "uncollectible", "void"]
    created: int

# Tenant upload — strict
class UploadedInvoiceRow(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    invoice_number: str = Field(min_length=1, max_length=64)
    customer_email: str
    amount: Decimal = Field(gt=Decimal("0"))
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    issued_at: datetime
```

### Money is `Decimal`, never `float`

```python
from decimal import Decimal
from pydantic import BaseModel, field_validator

class Amount(BaseModel):
    value: Decimal
    currency: str = Field(pattern=r"^[A-Z]{3}$")

    @field_validator("value", mode="before")
    @classmethod
    def parse_money(cls, v):
        # Strings like "1,234.50" from CSVs
        if isinstance(v, str):
            return Decimal(v.replace(",", ""))
        return v
```

Stripe amounts arrive as integer cents. Bank feeds vary. Pick one canonical representation (e.g. `Decimal` of major units with 4 dp of precision) and convert at the boundary.

### Times are timezone-aware UTC

```python
from datetime import datetime, UTC
from pydantic import BaseModel, field_validator

class Event(BaseModel):
    at: datetime

    @field_validator("at")
    @classmethod
    def tz_aware(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        return v.astimezone(UTC)
```

Reject naive datetimes. Convert everything to UTC at the boundary.

## Dead-letter queue record shape

One canonical shape across all pipelines:

```python
from pydantic import BaseModel
from datetime import datetime

class DeadLetterRecord(BaseModel):
    id: str                       # uuid4
    tenant_id: int
    pipeline: str                 # e.g. "stripe.invoices"
    source_id: str | None         # natural key from source (for dedupe on retry)
    run_id: str                   # the run that produced this DLQ entry
    payload: dict                 # full original payload, serialised
    error_class: str              # e.g. "ValidationError"
    error_message: str
    first_seen: datetime          # first time this record failed
    last_seen: datetime           # most recent failure
    retry_count: int              # manual replay attempts
    replayed_at: datetime | None  # when a human marked it fixed and replayed
    status: str                   # "new" | "triaged" | "replayed" | "abandoned"
```

### Storage

MySQL table for auditability + queryability:

```sql
CREATE TABLE pipeline_dlq (
  id             CHAR(36) NOT NULL,
  tenant_id      BIGINT UNSIGNED NOT NULL,
  pipeline       VARCHAR(128) NOT NULL,
  source_id      VARCHAR(256),
  run_id         CHAR(36) NOT NULL,
  payload        JSON NOT NULL,
  error_class    VARCHAR(128) NOT NULL,
  error_message  TEXT NOT NULL,
  first_seen     DATETIME(3) NOT NULL,
  last_seen      DATETIME(3) NOT NULL,
  retry_count    INT UNSIGNED NOT NULL DEFAULT 0,
  replayed_at    DATETIME(3),
  status         ENUM('new','triaged','replayed','abandoned') NOT NULL DEFAULT 'new',
  PRIMARY KEY (id),
  UNIQUE KEY uq_tenant_pipeline_source (tenant_id, pipeline, source_id),
  KEY ix_tenant_pipeline_status (tenant_id, pipeline, status),
  KEY ix_first_seen (first_seen)
) ENGINE=InnoDB;
```

The `UNIQUE` on `(tenant_id, pipeline, source_id)` deduplicates re-DLQ: if the same bad record fails again, bump `last_seen` and `retry_count` via `ON DUPLICATE KEY UPDATE` rather than inserting a second row.

## Writing to the DLQ

```python
from uuid import uuid4
from datetime import datetime, UTC
import json
from sqlalchemy import text

def send_to_dlq(
    conn,
    *,
    tenant_id: int,
    pipeline: str,
    source_id: str | None,
    run_id: str,
    payload: dict,
    error: Exception,
) -> None:
    now = datetime.now(UTC)
    conn.execute(text("""
        INSERT INTO pipeline_dlq
            (id, tenant_id, pipeline, source_id, run_id, payload,
             error_class, error_message, first_seen, last_seen, status)
        VALUES
            (:id, :t, :p, :s, :r, :payload, :ec, :em, :now, :now, 'new')
        ON DUPLICATE KEY UPDATE
            last_seen = VALUES(last_seen),
            retry_count = retry_count + 1,
            error_class = VALUES(error_class),
            error_message = VALUES(error_message),
            run_id = VALUES(run_id)
    """), {
        "id": str(uuid4()),
        "t": tenant_id,
        "p": pipeline,
        "s": source_id,
        "r": run_id,
        "payload": json.dumps(payload, default=str),
        "ec": type(error).__name__,
        "em": str(error)[:4000],
        "now": now,
    })

    # Metric
    DLQ_WRITES.labels(pipeline=pipeline, tenant=str(tenant_id)).inc()
```

Rules:

- Always store the **original payload**, not the partially-transformed one. Replay must have enough information to re-run validation from scratch.
- Truncate `error_message` to fit the column. Full traceback goes to structured logs.
- Emit a metric on every DLQ write so dashboards can alert on bursts.

## Replay

Replay is a human-supervised action, not automatic.

```python
def replay_dlq_record(conn, dlq_id: str) -> ReplayResult:
    row = conn.execute(text("""
        SELECT * FROM pipeline_dlq WHERE id = :id FOR UPDATE
    """), {"id": dlq_id}).mappings().first()
    if not row:
        raise NotFound(dlq_id)
    if row["status"] in ("replayed", "abandoned"):
        raise InvalidState(row["status"])

    payload = json.loads(row["payload"])
    handler = get_pipeline_handler(row["pipeline"])

    try:
        handler.process_one(tenant_id=row["tenant_id"], payload=payload, source="dlq-replay")
    except Exception as e:
        conn.execute(text("""
            UPDATE pipeline_dlq
            SET last_seen=:now, retry_count=retry_count+1, error_message=:em
            WHERE id=:id
        """), {"id": dlq_id, "now": datetime.now(UTC), "em": str(e)[:4000]})
        raise

    conn.execute(text("""
        UPDATE pipeline_dlq
        SET status='replayed', replayed_at=:now
        WHERE id=:id
    """), {"id": dlq_id, "now": datetime.now(UTC)})
    return ReplayResult(ok=True)
```

Replay rules:

- `FOR UPDATE` — prevents two operators replaying the same record.
- Successful replay marks the record `replayed`. It stays in the table for audit; do not delete.
- Failed replay increments `retry_count`, keeps `status='new'`.
- An operator can mark a record `abandoned` — e.g. the tenant deleted the source data. Abandoned records are excluded from DLQ-depth alerts.

## Bulk replay

When the root cause is fixed (e.g. a new required field was added to the Pydantic model but was optional in reality), you may have hundreds of records to replay. Provide a CLI:

```bash
uv run python -m tools.dlq_replay \
    --tenant 42 \
    --pipeline stripe.invoices \
    --status new \
    --since 2026-04-01 \
    --dry-run
```

Rules:

- Always offer `--dry-run`. Lists records and what would happen.
- Default `--limit 100` to guard against a typo replaying 10,000 records at once.
- Run replays through the same lock/mutex as normal pipeline runs.

## Alerting

Two alerts per pipeline per tenant:

1. **DLQ depth** — count of `status='new'` records exceeds a threshold.

```promql
# Prometheus alert
count by (pipeline, tenant) (pipeline_dlq_depth{status="new"}) > 50
```

2. **DLQ growth rate** — rate of new DLQ writes over 1h exceeds a threshold.

```promql
rate(pipeline_dlq_writes_total[1h]) > 10
```

Paging rules:

- Slow growth, low depth → ticket the next business day.
- Sharp burst (100 in an hour) → page immediately; probably a schema-drift bug.
- Single tenant spike → probably a bad upload; notify tenant success, not on-call.

## Manual triage workflow

When an operator sees DLQ records:

1. Open the top N by `last_seen`. Group by `error_class` / `error_message`.
2. For each group, decide:
   - **Fix in code** — bug in the validator. Ship the fix, then bulk-replay the group.
   - **Fix the source** — bad data on the vendor side. Contact vendor, mark records `triaged` with a note.
   - **Abandon** — data is irrecoverable. Mark `abandoned` with a reason.
3. After bulk-replay, verify `pipeline_dlq_depth` goes to zero for that group.
4. Add a test for the regression that created the group.

## Anti-patterns

- Try/except `pass` around `model.validate()` — silent data loss. The DLQ is the only acceptable sink.
- Storing the transformed record in the DLQ instead of the raw payload — replay becomes impossible after a transform bug.
- Deleting DLQ rows after replay — loses the audit trail of how often a given record failed before being fixed.
- Automatic infinite replay — the same record fails 10,000 times per hour. Replay must be human-initiated or strictly bounded.
- One DLQ table per pipeline — makes cross-pipeline alerts awkward. One table, `pipeline` as a column.
- No dedupe — same bad record shows up as 500 rows over a week.
