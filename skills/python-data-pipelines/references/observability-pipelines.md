# Pipeline Observability

A pipeline you cannot see is a pipeline you cannot operate. Every run writes a row, emits metrics, and raises alerts on lag or DLQ growth.

## The run-tracking table

One row per run, per pipeline, per tenant. The authoritative record of what happened.

```sql
CREATE TABLE pipeline_runs (
  id              CHAR(36)         NOT NULL,
  tenant_id       BIGINT UNSIGNED  NOT NULL,
  pipeline        VARCHAR(128)     NOT NULL,
  started_at      DATETIME(3)      NOT NULL,
  finished_at     DATETIME(3),
  status          ENUM('running','succeeded','failed','partial') NOT NULL DEFAULT 'running',
  records_in      INT UNSIGNED     NOT NULL DEFAULT 0,
  records_ok      INT UNSIGNED     NOT NULL DEFAULT 0,
  records_dlq     INT UNSIGNED     NOT NULL DEFAULT 0,
  records_skipped INT UNSIGNED     NOT NULL DEFAULT 0,
  watermark_before VARCHAR(64),
  watermark_after  VARCHAR(64),
  error_class     VARCHAR(128),
  error_message   TEXT,
  host            VARCHAR(64),
  PRIMARY KEY (id),
  KEY ix_tenant_pipeline_started (tenant_id, pipeline, started_at),
  KEY ix_pipeline_started (pipeline, started_at),
  KEY ix_status_started (status, started_at)
) ENGINE=InnoDB;
```

Write pattern — two statements per run:

```python
def start_run(conn, run_id, tenant_id, pipeline, watermark_before):
    conn.execute(text("""
        INSERT INTO pipeline_runs
            (id, tenant_id, pipeline, started_at, status, watermark_before, host)
        VALUES (:id, :t, :p, UTC_TIMESTAMP(3), 'running', :wb, :host)
    """), {"id": run_id, "t": tenant_id, "p": pipeline, "wb": watermark_before, "host": HOSTNAME})

def finish_run(conn, run_id, status, records_in, records_ok, records_dlq, watermark_after, error=None):
    conn.execute(text("""
        UPDATE pipeline_runs
        SET finished_at = UTC_TIMESTAMP(3),
            status = :s,
            records_in = :ri, records_ok = :ro, records_dlq = :rd,
            watermark_after = :wa,
            error_class = :ec, error_message = :em
        WHERE id = :id
    """), {
        "id": run_id, "s": status,
        "ri": records_in, "ro": records_ok, "rd": records_dlq,
        "wa": watermark_after,
        "ec": type(error).__name__ if error else None,
        "em": str(error)[:4000] if error else None,
    })
```

Wrap the whole pipeline so `finish_run` executes even on crashes:

```python
def run_with_tracking(tenant_id: int, pipeline: str, handler):
    run_id = str(uuid4())
    wb = current_watermark(tenant_id, pipeline)
    start_run(conn, run_id, tenant_id, pipeline, wb)
    try:
        result = handler(tenant_id, run_id)
        status = "succeeded" if result.records_dlq == 0 else "partial"
        finish_run(conn, run_id, status, result.records_in, result.records_ok, result.records_dlq, result.watermark_after)
    except Exception as e:
        finish_run(conn, run_id, "failed", 0, 0, 0, wb, error=e)
        raise
```

## Standard Prometheus metrics

Four metrics cover most needs. Define them once, use them everywhere.

```python
from prometheus_client import Counter, Gauge, Histogram

pipeline_run_total = Counter(
    "pipeline_run_total",
    "Total pipeline runs",
    ["pipeline", "tenant", "status"],   # status: succeeded | failed | partial
)

pipeline_records_total = Counter(
    "pipeline_records_total",
    "Records processed",
    ["pipeline", "tenant", "outcome"],  # outcome: ok | failed | skipped
)

pipeline_duration_seconds = Histogram(
    "pipeline_duration_seconds",
    "Pipeline run duration",
    ["pipeline", "tenant"],
    buckets=(1, 5, 15, 30, 60, 120, 300, 600, 1800, 3600),
)

pipeline_lag_seconds = Gauge(
    "pipeline_lag_seconds",
    "Seconds since the last successful run",
    ["pipeline", "tenant"],
)

pipeline_dlq_depth = Gauge(
    "pipeline_dlq_depth",
    "Current DLQ depth by pipeline/tenant/status",
    ["pipeline", "tenant", "status"],
)
```

Usage:

```python
with pipeline_duration_seconds.labels(pipeline=p, tenant=str(t)).time():
    result = run_pipeline(t)
pipeline_run_total.labels(pipeline=p, tenant=str(t), status=result.status).inc()
pipeline_records_total.labels(pipeline=p, tenant=str(t), outcome="ok").inc(result.records_ok)
pipeline_records_total.labels(pipeline=p, tenant=str(t), outcome="failed").inc(result.records_dlq)
```

### Cardinality budget

`tenant` label is high-cardinality. In a Prometheus setup with thousands of tenants, split by tier or sample:

- Record all counters at `(pipeline, tier)` level for dashboards.
- Record `(pipeline, tenant)` histograms only for paid tiers.
- Use a separate timeseries DB (VictoriaMetrics, Mimir) or push detailed per-tenant rollups to the DB instead.

## Freshness SLA

For each pipeline, define:

- **Expected interval.** How often should it run? (e.g. 24h.)
- **Freshness SLA.** How old can the destination be before the tenant is impacted? (e.g. 30h.)

The `pipeline_lag_seconds` gauge is refreshed by a background job:

```python
def refresh_lag_gauges():
    rows = conn.execute(text("""
        SELECT pipeline, tenant_id,
               TIMESTAMPDIFF(SECOND, MAX(finished_at), UTC_TIMESTAMP()) AS lag
        FROM pipeline_runs
        WHERE status = 'succeeded' OR status = 'partial'
        GROUP BY pipeline, tenant_id
    """)).mappings().all()
    for r in rows:
        pipeline_lag_seconds.labels(pipeline=r["pipeline"], tenant=str(r["tenant_id"])).set(r["lag"] or 0)
```

Run this every minute; it is cheap if the index is on `(pipeline, tenant_id, finished_at)`.

## Alert rules

### No success in > 2× expected interval

```yaml
- alert: PipelineStalled
  expr: pipeline_lag_seconds > 2 * 86400          # 24h expected, alert at 48h
  for: 10m
  labels:
    severity: page
  annotations:
    summary: "Pipeline {{ $labels.pipeline }} stalled for tenant {{ $labels.tenant }}"
```

### DLQ growing fast

```yaml
- alert: PipelineDlqBurst
  expr: sum by (pipeline, tenant) (rate(pipeline_records_total{outcome="failed"}[15m])) > 1
  for: 15m
  labels:
    severity: page
  annotations:
    summary: "DLQ burst on {{ $labels.pipeline }} / {{ $labels.tenant }} (>1/sec)"
```

### DLQ depth too high

```yaml
- alert: PipelineDlqDepth
  expr: pipeline_dlq_depth{status="new"} > 50
  for: 30m
  labels:
    severity: ticket
```

### Lag over SLA

```yaml
- alert: PipelineLagOverSla
  expr: pipeline_lag_seconds > on(pipeline) group_left pipeline_lag_sla_seconds
  for: 5m
  labels:
    severity: page
```

You can record `pipeline_lag_sla_seconds{pipeline="..."}` as a static series via a config or a `recording_rules.yml` — one value per pipeline.

### Run duration regression

```yaml
- alert: PipelineDurationRegression
  expr: histogram_quantile(0.95, sum(rate(pipeline_duration_seconds_bucket[30m])) by (pipeline, le))
        > on(pipeline) (avg_over_time(...[7d]) * 2)
  for: 30m
```

## Grafana dashboard layout

One dashboard, five rows:

1. **Overview** — sparkline per pipeline: `sum by (pipeline) (rate(pipeline_run_total[1h]))`. Green/red by most recent status.
2. **Lag** — heatmap of `pipeline_lag_seconds` per pipeline × tier. Red above SLA.
3. **Throughput** — records in/ok/dlq per pipeline over the last 24h.
4. **Duration** — p50 / p95 / p99 histograms per pipeline.
5. **DLQ** — current `pipeline_dlq_depth{status="new"}` per pipeline × tenant (top 20).

Add template variables for `pipeline` and `tenant` so operators can drill in. Per-tenant drill-downs are essential for customer-success conversations.

## Structured logs — the diagnosis layer

Metrics tell you *that* something is wrong. Logs tell you *what*. Every pipeline uses `structlog` with contextvars:

```python
import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars

def run_pipeline(tenant_id: int, pipeline: str):
    clear_contextvars()
    bind_contextvars(
        tenant_id=tenant_id,
        pipeline=pipeline,
        run_id=str(uuid4()),
        host=HOSTNAME,
    )
    log = structlog.get_logger()
    log.info("pipeline.start")
    ...
    log.info("pipeline.batch", batch_index=i, records=len(batch), elapsed_ms=elapsed)
    ...
    log.info("pipeline.done", records_in=n, records_ok=o, records_dlq=d)
```

Require these fields on every event:

- `tenant_id`
- `pipeline`
- `run_id`
- `event` (short verb.noun)
- `ts` (ISO 8601 UTC)

Stream into ELK / Loki / CloudWatch with structured parsing enabled.

## Traces

For any pipeline that fans out across sub-steps or services, emit OpenTelemetry traces. Each pipeline run is a trace; each batch is a span; each external API call is a child span.

```python
from opentelemetry import trace

tracer = trace.get_tracer("saas.pipelines")

with tracer.start_as_current_span("pipeline.run", attributes={"tenant_id": tenant_id, "pipeline": pipeline}) as span:
    with tracer.start_as_current_span("extract"):
        ...
    with tracer.start_as_current_span("validate"):
        ...
    with tracer.start_as_current_span("load", attributes={"batch_size": n}):
        ...
    span.set_attribute("records_ok", ok)
    span.set_attribute("records_dlq", dlq)
```

Rules:

- Sample aggressively (1–5%) in production; full sampling on failed runs.
- Propagate the trace ID into external API headers (`traceparent`) so vendor traces can be correlated when they offer it.

## Per-pipeline SLO

For each pipeline, declare:

| SLO | Target |
|---|---|
| Run success rate (excluding `partial` from due to bad data) | ≥ 99% over 30 days |
| Freshness SLA (lag < X) | ≥ 99% of minutes over 30 days |
| DLQ resolution | Median time-to-replay ≤ 24h for `new` records |

Publish on the internal status page. Review quarterly.

## Runbook linking

Every alert links to a runbook that answers:

1. What does this alert mean in business terms?
2. What does the operator check first (dashboard link, log query)?
3. Known causes and their fixes.
4. Escalation path if the fix is not obvious.

Runbooks live in the same repo as the pipeline code and are reviewed in the PR that ships the pipeline.

## Anti-patterns

- Logging without `tenant_id` — cannot answer "what happened for tenant X?"
- Metrics without a cardinality budget — Prometheus OOMs at 100k tenants.
- Tracking runs only in application memory — lose everything on restart.
- "It ran, we logged it." Without a counter/gauge, alerts cannot fire.
- Alerts without runbooks — on-call paged, nobody knows what to do.
- Dashboards with no per-tenant drill-down — customer success cannot self-serve.
- Alerts on every failed record — noise. Alert on **rates**, not events.
