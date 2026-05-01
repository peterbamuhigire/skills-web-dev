# Observability

Logs, metrics, traces, and correlation IDs for the Python sidecar and workers, aligned with the PHP app so incidents are reconstructable end to end.

## Principles

1. Every log line is structured JSON.
2. Every log line carries `correlation_id`, `tenant_id`, and — if applicable — `job_id` or `request_id`.
3. Metrics live on a `/metrics` Prometheus endpoint; scraped every 15 s.
4. Traces are optional; correlation IDs are mandatory.
5. Alerts fire on symptoms (error rate, latency, queue depth), not causes.

## Logging: structlog to journald

structlog emits JSON to stdout; systemd captures stdout into journald; a log shipper (Vector or Promtail) ships journald entries to Loki/Elasticsearch.

### Configuration

```python
# src/service_name/logging.py
import logging, sys
import structlog

def configure_logging(level: str, env: str) -> None:
    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)
    shared = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    structlog.configure(
        processors=shared + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper()),
        ),
        logger_factory=structlog.PrintLoggerFactory(sys.stdout),
        cache_logger_on_first_use=True,
    )

    # Route stdlib logging (uvicorn, sqlalchemy, boto) through structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level.upper(),
    )
    for name in ("uvicorn", "uvicorn.access", "sqlalchemy.engine", "botocore"):
        logging.getLogger(name).handlers.clear()
        logging.getLogger(name).propagate = True
```

### Required fields

Every log line has:

```json
{
  "timestamp": "2026-04-15T10:30:00.123Z",
  "level": "info",
  "event": "kpi.computed",
  "service": "myapp-sidecar",
  "env": "prod",
  "version": "2026.04.15-abc123",
  "correlation_id": "uuid",
  "tenant_id": "t_01HF...",
  "request_id": "uuid",
  "duration_ms": 145
}
```

Bind `service`, `env`, and `version` once at startup via `structlog.contextvars.bind_contextvars(...)`.

### What to log

- Every incoming request: method, path, status, duration, caller.
- Every job start and end: name, id, duration, outcome.
- Every external call (DB, Redis, S3, HTTP): target, duration, outcome. Especially on failure.
- Business events: "report.generated", "score.computed". These feed product analytics separately from ops logs.

Do not log request bodies or response bodies in production. PII leak risk and log volume cost. Log sizes and counts.

## Correlation ID propagation

PHP generates one UUID v4 per inbound HTTP request — that is the `correlation_id`. It travels everywhere.

```text
User request -> PHP (generate UUID)
             -> HTTP call to sidecar (X-Correlation-Id header)
             -> sidecar logs with correlation_id bound
             -> PHP enqueues a job, payload.correlation_id = same UUID
             -> worker logs with correlation_id bound
             -> if worker calls sidecar, passes same header
```

PHP adds the header to every client call:

```php
$headers[] = 'X-Correlation-Id: ' . Context::correlationId();
```

FastAPI middleware binds it:

```python
class CorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        cid = request.headers.get("x-correlation-id") or str(uuid.uuid4())
        structlog.contextvars.bind_contextvars(correlation_id=cid)
        response = await call_next(request)
        response.headers["x-correlation-id"] = cid
        return response
```

Worker wrapper binds it from the job payload (see `tenant-isolation.md` for the same pattern with `tenant_id`).

## Metrics: Prometheus

### Endpoint

`prometheus-client` exposes `/metrics`. For the sidecar, mount it:

```python
from prometheus_client import make_asgi_app, Counter, Histogram

http_requests = Counter(
    "http_requests_total",
    "HTTP requests",
    ["method", "path_template", "status"],
)
http_request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    ["method", "path_template", "status"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
)

app.mount("/metrics", make_asgi_app())
```

Middleware records the metrics:

```python
class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        path_template = request.scope.get("route").path if request.scope.get("route") else "unknown"
        http_requests.labels(request.method, path_template, response.status_code).inc()
        http_request_duration.labels(request.method, path_template, response.status_code).observe(duration)
        return response
```

**Use `path_template`, not `path`.** `/v1/users/{id}` not `/v1/users/42` — otherwise cardinality explodes.

### Worker metrics

Workers do not have an HTTP server by default. Two options:

1. **Pushgateway** — workers push metrics after each job. Simple; the pushgateway is a SPOF but acceptable.
2. **Sidecar exporter** — each worker binds a tiny HTTP server on a unique port and Prometheus scrapes. Prefer this.

```python
from prometheus_client import start_http_server, Histogram, Counter, Gauge
import os

job_duration = Histogram(
    "job_duration_seconds",
    "Job duration",
    ["job_name", "status"],
)
job_failures = Counter(
    "job_failures_total",
    "Job failures",
    ["job_name", "reason"],
)
queue_depth = Gauge(
    "queue_depth",
    "Queue depth",
    ["queue"],
)

def main():
    # Port offset by worker index to avoid collisions
    port = 9100 + int(os.environ.get("WORKER_INDEX", "1"))
    start_http_server(port, addr="127.0.0.1")
    ...
```

Queue depth is polled from a short-lived "metrics" worker that LLENs every queue every 10 s — not every worker doing it, which is noisy.

### Key metrics (minimum set)

| Metric | Type | Labels | Alert when |
|---|---|---|---|
| `http_request_duration_seconds` | histogram | method, path, status | p95 > SLO for 10 min |
| `http_requests_total` | counter | method, path, status | 5xx rate > 1% for 5 min |
| `job_duration_seconds` | histogram | name, status | p95 > SLO |
| `job_failures_total` | counter | name, reason | rate > 0 for 5 min (most jobs should always succeed) |
| `queue_depth` | gauge | queue | depth > threshold for 10 min |
| `queue_oldest_job_age_seconds` | gauge | queue | age > SLA |
| `worker_heartbeat_age_seconds` | gauge | worker | age > 60 |

## OpenTelemetry

Use when the PHP app is already sending traces or when you need request-level causality beyond logs. Otherwise correlation IDs are enough.

### Setup

```python
# src/service_name/telemetry.py
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

def configure_tracing(app, engine, service_name: str, version: str):
    resource = Resource.create({
        "service.name": service_name,
        "service.version": version,
        "deployment.environment": settings.env,
    })
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument(engine=engine)
    RedisInstrumentor().instrument()
```

### Custom spans for jobs

```python
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

@app.task
def build_sales_report(tenant_id, params, idempotency_key):
    with tracer.start_as_current_span("job.build_sales_report") as span:
        span.set_attribute("tenant_id", tenant_id)
        span.set_attribute("idempotency_key", idempotency_key)
        ...
```

PHP passes `traceparent` / `tracestate` headers; OTel propagators pick them up automatically if `FastAPIInstrumentor` is on.

### Sampling

- Prod: 5-10% head sampling for normal traffic; 100% for errors (tail sampling at the collector).
- Staging: 100%.
- Dev: 0% unless debugging.

High cardinality traces drown collectors and budgets. Tune before turning traces on for real traffic.

## Log shipper

### Vector (recommended)

`/etc/vector/vector.toml`:

```toml
[sources.journald]
type = "journald"
current_boot_only = true
include_units = [
  "myapp-sidecar.service",
  "myapp-worker@1.service",
  "myapp-worker@2.service",
]

[transforms.parse_json]
type = "remap"
inputs = ["journald"]
source = '''
  parsed, err = parse_json(.message)
  if err == null {
    . = merge!(., parsed)
  }
'''

[sinks.loki]
type = "loki"
inputs = ["parse_json"]
endpoint = "https://loki.internal:3100"
labels = { service = "{{ service }}", env = "{{ env }}", level = "{{ level }}" }
encoding = { codec = "json" }
```

Labels are low cardinality (service, env, level). Tenant IDs and correlation IDs are in the body, searchable via LogQL's `|= "tenant_id"` pattern.

## Dashboards and alerts

Minimum production dashboard:

- Request rate, error rate, p50/p95/p99 latency per path.
- Job throughput, error rate, p95 duration per job.
- Queue depth and oldest-job age per queue.
- Worker heartbeats (one row per worker, green/red).
- External dependency health: DB, Redis, S3 round-trip.

Alerts wire into PagerDuty / Opsgenie. Every alert has a runbook URL in its annotations. No alert without a runbook.

## Anti-patterns

- Logging secrets or the raw request body.
- Labels with unbounded cardinality (tenant_id, user_id, correlation_id as a metric label).
- Logging inside a hot loop. Aggregate, then log once.
- Swallowing exceptions silently — always log `exception="..."` before degrading.
- Separate log format between sidecar and workers. Unify; incident response depends on it.
