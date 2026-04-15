---
name: python-saas-integration
description: Use when integrating Python services into a PHP + Android + iOS SaaS
  — covers FastAPI sidecar architecture, background job workers (RQ/Celery), PHP↔Python
  contract, multi-tenant isolation, deployment on Debian/Ubuntu, observability, and
  failure-mode handling.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Python SaaS Integration

<!-- dual-compat-start -->
## Use When

- Use when integrating Python services into a PHP + Android + iOS SaaS — covers FastAPI sidecar architecture, background job workers (RQ/Celery), PHP↔Python contract, multi-tenant isolation, deployment on Debian/Ubuntu, observability, and failure-mode handling.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `python-saas-integration` or would be better handled by a more specific companion skill.
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
How Python fits into a PHP-backed SaaS without disrupting the existing architecture. Covers the two patterns we use (FastAPI sidecar and background worker), the contract between PHP and Python, and the operational baseline on Debian/Ubuntu.

**Prerequisite:** Load `python-modern-standards` before this skill.

## When this skill applies

- Adding Python capability to a PHP SaaS (analytics, document generation, ML, OCR, ETL).
- Deciding between synchronous (sidecar) and asynchronous (worker) for a new feature.
- Setting up the first Python service in a project.
- Establishing the PHP ↔ Python contract (auth, errors, file handoff).
- Deploying Python services alongside PHP on the same Debian/Ubuntu hosts.

## Integration patterns

We use two complementary patterns. Same codebase, chosen per use case.

### Pattern A — FastAPI sidecar (synchronous)

A Python HTTP service on `127.0.0.1:8001` (internal only), called by PHP when it needs a computed result in the same request cycle.

**Use when:**
- Response time budget is under ~2 seconds.
- Output is small (JSON, small Excel/PDF < 2MB).
- User is waiting on the result.
- Example: compute KPIs for a dashboard widget, score a single record with an ML model, render a one-page branded receipt.

### Pattern C — Background worker (asynchronous)

PHP enqueues a job to Redis (RQ or Celery queue). A Python worker process picks it up, runs the task, writes output to storage, notifies the user.

**Use when:**
- Task takes more than a few seconds.
- Output is large (multi-tab Excel, multi-page PDF, bulk scoring).
- Task is periodic (ETL syncs, scheduled reports).
- User can wait (email/notification on completion, or poll for status).
- Example: generate a 50-tab sales dashboard, bulk score 10,000 customers for churn, sync Stripe invoices nightly.

### Decision rule

```text
Output size < 2MB AND expected duration < 2s   -> Pattern A (sidecar)
Output size >= 2MB OR expected duration >= 2s  -> Pattern C (worker)
Triggered on a schedule (no user request)       -> Pattern C (worker)
User polls / gets notified later                -> Pattern C (worker)
```

Ambiguous cases default to Pattern C — it's more forgiving at scale.

## Architecture overview

```text
+---------------------+        +----------------------+
|   PHP SaaS (nginx)  |------->|  FastAPI sidecar     |   Pattern A
|                     |   HTTP |  127.0.0.1:8001      |
|                     |        +----------------------+
|                     |
|                     |        +----------------------+
|                     |  RPUSH |  Redis (jobs queue)  |   Pattern C
|                     |------->|                      |
|                     |        +----------+-----------+
|                     |                   |
|                     |                   v
|                     |        +----------------------+
|                     |        |  Python worker(s)    |
|                     |        |  (RQ or Celery)      |
|                     |        +----------+-----------+
|                     |                   |
|                     |<------------------+
|                     |   status / file via storage + webhook
+---------------------+
        |
        | serves file to web / Android / iOS clients
        v
   +------------+
   |  Storage   |  (local disk / S3)
   +------------+
```

Both patterns share the same Python codebase (`src/service_name/api/` + `src/service_name/workers/`), the same domain logic, and the same configuration.

See `references/fastapi-sidecar.md` and `references/background-workers.md` for full project skeletons.

## PHP ↔ Python contract

Keep the contract tight. Both sides change independently; the contract is the safety net.

### Authentication (internal-only service)

Bind sidecar to `127.0.0.1` only. Never expose publicly. Even so, authenticate every request with an HMAC-signed token:

- PHP signs: `HMAC-SHA256(shared_secret, timestamp + path + body)`.
- Sends `X-Internal-Signature` and `X-Internal-Timestamp` headers.
- Python rejects requests with timestamp skew > 60 seconds or invalid signature.

If a host-level attacker can reach localhost, you have bigger problems — but defense in depth.

### Request/response envelope

Every sidecar endpoint returns:

```json
{ "ok": true, "data": { ... } }
```

or

```json
{ "ok": false, "error": { "code": "INVALID_INPUT", "message": "...", "details": {...} } }
```

Worker job payloads use the same `{ok, data, error}` shape for results. PHP knows how to parse it from both paths.

### Idempotency

Every job or sidecar call that mutates state must accept an `idempotency_key`. Workers deduplicate by key for at least 24 hours. PHP retries are safe.

See `references/php-python-contract.md` for the HMAC implementation, error-code catalog, idempotency patterns, and versioning strategy.

## Multi-tenant safety

Every request and every job carries `tenant_id`. Python services:

- Validate `tenant_id` against the caller (HMAC payload binds to tenant when possible).
- Scope every DB query by `tenant_id` — use SQLAlchemy events or explicit WHERE clauses, never assume.
- Never cache data across tenants without namespacing the cache key by tenant.
- Log `tenant_id` on every log line (via structlog contextvars).
- Worker concurrency: one Python worker may process jobs for many tenants; never carry tenant state between jobs in module-level variables.

See `references/tenant-isolation.md`.

## File handoff (for large outputs)

Python generates a file → writes to storage → returns URL to PHP → PHP delivers to client.

**Storage options:**
- **S3 (or S3-compatible):** preferred for multi-host deployments. Python writes with server-side encryption; PHP generates signed URL with short TTL.
- **Shared local disk:** acceptable for single-host deployments. Write to `/var/app/storage/tenant_{id}/reports/...` with strict permissions (`0640`, owner `app`, group `nginx`). nginx serves with `X-Accel-Redirect` (internal) so PHP controls authorization.

Always include tenant_id in the storage path. Never trust the filename alone for access control.

**Cleanup:** temp files expire after 24–72 hours depending on use case. A scheduled sweep job removes expired files. Never rely on "someone will clean it up."

See `references/file-handoff.md`.

## Deployment on Debian/Ubuntu

Python runs as a systemd service, using a project-local venv managed by uv.

### systemd unit — FastAPI sidecar

```ini
# /etc/systemd/system/myapp-sidecar.service
[Unit]
Description=MyApp Python Sidecar
After=network.target

[Service]
Type=exec
User=app
Group=app
WorkingDirectory=/var/www/myapp-sidecar
Environment="PATH=/var/www/myapp-sidecar/.venv/bin"
EnvironmentFile=/etc/myapp/sidecar.env
ExecStart=/var/www/myapp-sidecar/.venv/bin/uvicorn service_name.main:app \
    --host 127.0.0.1 --port 8001 --workers 2 --log-config /etc/myapp/log_config.json
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

### systemd unit — RQ worker

```ini
[Unit]
Description=MyApp Python Worker
After=network.target redis.service

[Service]
Type=exec
User=app
Group=app
WorkingDirectory=/var/www/myapp-sidecar
Environment="PATH=/var/www/myapp-sidecar/.venv/bin"
EnvironmentFile=/etc/myapp/sidecar.env
ExecStart=/var/www/myapp-sidecar/.venv/bin/rq worker high default low \
    --url ${REDIS_URL}
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

### nginx proxy (if sidecar needs to be reachable from PHP across hosts)

Usually PHP and Python share a host, so `127.0.0.1:8001` suffices. When they don't:

```nginx
location /internal/py/ {
    allow 10.0.0.0/8;  # internal network only
    deny all;
    proxy_pass http://10.0.0.5:8001/;
    proxy_set_header Host $host;
}
```

Never expose the sidecar to the public internet.

See `references/deployment-debian.md` for venv strategies, secrets management, log rotation, zero-downtime restarts, and blue-green sidecar deployment.

## Observability

Align Python logs with PHP logs so a single incident can be traced end-to-end.

- **Logs:** structlog → JSON → journald → log shipper (Promtail/Vector) → Loki/Elasticsearch.
- **Correlation ID:** PHP generates a UUID per request, passes as `X-Correlation-ID` header or job field. Python binds it to structlog contextvars for the duration of the request/job.
- **Metrics:** Prometheus scrapes `/metrics` on each sidecar/worker. Standard histograms: `http_request_duration_seconds`, `job_duration_seconds`, `job_failures_total`.
- **Traces:** OpenTelemetry if the team already uses it; otherwise correlation IDs are enough to start.
- **Health checks:** `GET /health` on sidecar (liveness), `GET /ready` (readiness — checks DB/Redis). Workers expose a heartbeat key in Redis.

See `references/observability.md`.

## Failure modes

Plan for Python being down, slow, or misbehaving.

- **Sidecar down:** PHP gets connection refused. Handler should degrade gracefully (feature flag off, cached value, friendly error). Never cascade into a 500 across the whole app.
- **Sidecar slow:** PHP client has a strict timeout (configurable, default 5s). Circuit breaker after N consecutive failures in 60s.
- **Worker queue backing up:** alert when queue depth > threshold, when oldest job age > SLA. Dead-letter queue for jobs that fail N times.
- **Poison messages:** workers catch exceptions per job, log, send to DLQ, continue processing. Never crash the worker on a single bad payload.
- **Idempotency:** all retries are safe because workers dedupe by `idempotency_key`.

See `references/failure-modes.md`.

## Versioning + rollouts

- **Sidecar:** semantic versioning. Blue-green deploy (run new sidecar on :8002, flip nginx/PHP config, stop old). Zero-downtime.
- **Workers:** drain and restart. New workers start processing new jobs; old workers finish their current job then exit. Use SIGTERM with a 60-second grace period.
- **Schema changes:** additive only across versions. Never remove a field PHP still sends. Deprecate → warn → remove across two releases minimum.

## Read next

- `python-data-analytics` — for workloads that compute KPIs / analytics.
- `python-document-generation` — for Excel/Word/PDF output workflows.
- `python-ml-predictive` — for forecasting or classification features.
- `python-data-pipelines` — for ETL, OCR, image processing.

## References

- `references/fastapi-sidecar.md`
- `references/background-workers.md`
- `references/php-python-contract.md`
- `references/file-handoff.md`
- `references/tenant-isolation.md`
- `references/deployment-debian.md`
- `references/observability.md`
- `references/failure-modes.md`
