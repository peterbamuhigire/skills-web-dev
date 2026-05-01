# Background Workers (RQ and Celery)

Pattern C: PHP enqueues a job to Redis, Python worker processes it, writes output, notifies. This file covers both RQ and Celery setups, the choice between them, and queue topology.

## Decision matrix: RQ vs Celery

| Signal | Pick |
|---|---|
| Simple queues, few job types, Redis already the broker | RQ |
| Jobs are mostly "run this function with these args" | RQ |
| Team is small, operating budget for the queue is low | RQ |
| Need scheduled/cron-like periodic jobs (beat) | Celery |
| Need chained workflows, groups, chords, canvas primitives | Celery |
| Need a broker other than Redis (RabbitMQ, SQS) later | Celery |
| Need per-task rate limits and complex routing | Celery |
| Need task revocation after dispatch | Celery |

Default: RQ. Upgrade to Celery when the complexity earns it. Never run both in the same codebase — pick one.

## RQ setup

### Queue topology

Three queues, priority-ordered. The worker drains high before default before low.

```python
# src/service_name/workers/rq_app.py
import redis
from rq import Queue
from ..settings import settings

redis_conn = redis.from_url(settings.redis_url)
q_high = Queue("high", connection=redis_conn)
q_default = Queue("default", connection=redis_conn)
q_low = Queue("low", connection=redis_conn)
```

Routing rule:

- `high` — user-visible work with SLA < 30 s (single-record scoring, small PDF).
- `default` — standard jobs (multi-tab Excel, bulk scoring under 10k rows).
- `low` — bulk/ETL/nightly work that can wait if the queue is busy.

### Job definition

Jobs are plain functions in `workers/`. Keep them thin — delegate to `domain/`.

```python
# src/service_name/workers/jobs/reports.py
from rq import get_current_job
from ...domain.reports import build_sales_report
from ...db.session import sync_session
from ...logging import bind_job_context

def build_sales_report_job(tenant_id: str, params: dict, idempotency_key: str):
    job = get_current_job()
    bind_job_context(
        job_id=job.id,
        tenant_id=tenant_id,
        idempotency_key=idempotency_key,
    )
    with sync_session() as db:
        url = build_sales_report(db, tenant_id, params)
    return {"ok": True, "data": {"url": url}}
```

Return the `{ok, data}` envelope. RQ stores it in Redis for `result_ttl` seconds — PHP polls or the worker calls the webhook.

### Enqueue from PHP, consume in Python

PHP RPUSHes to the same structure RQ expects, or (cleaner) exposes a tiny Python CLI that PHP `exec()`s — but the cleanest path is PHP writing directly to Redis using the documented RQ payload format. For most teams, a thin HTTP "enqueue" endpoint on the sidecar is the easiest bridge. See `php-python-contract.md`.

### Worker invocation

```bash
/var/www/myapp-sidecar/.venv/bin/rq worker high default low \
  --url "$REDIS_URL" \
  --name "worker-$(hostname)-$$" \
  --with-scheduler \
  --max-jobs 500 \
  --worker-ttl 420
```

- `--with-scheduler` — runs rq-scheduler inline; good enough for small cron needs.
- `--max-jobs 500` — worker exits after 500 jobs; systemd restarts it. Bounds memory leaks in third-party libs (common with pandas/pillow).
- `--worker-ttl 420` — heartbeat TTL; must exceed `job_timeout` of the longest job.

### Concurrency

RQ workers are single-process, one job at a time. For concurrency, run more worker units. systemd template unit:

```ini
# /etc/systemd/system/myapp-worker@.service
[Service]
ExecStart=/var/www/myapp-sidecar/.venv/bin/rq worker default low --url ${REDIS_URL} --name worker-%i
```

Then `systemctl enable --now myapp-worker@1 myapp-worker@2 myapp-worker@3`.

Sizing rule:

- I/O-bound jobs (network, DB): `2 * CPU_cores` workers.
- CPU-bound (pandas aggregations, PDF render): `CPU_cores` workers.
- Memory-bound: constrain by RAM / per-worker peak, not CPU.

### Timeouts

Every enqueue sets `job_timeout` explicitly. Never rely on the default.

```python
q_default.enqueue(
    build_sales_report_job,
    tenant_id, params, idempotency_key,
    job_timeout=600,       # 10 minutes
    result_ttl=3600,       # keep result 1h for PHP to fetch
    failure_ttl=86400,     # keep failure 24h for DLQ inspection
    retry=Retry(max=3, interval=[10, 60, 300]),
)
```

## Celery setup

### App config

```python
# src/service_name/workers/celery_app.py
from celery import Celery
from ..settings import settings

app = Celery(
    "service_name",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["service_name.workers.jobs"],
)

app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_default_queue="default",
    task_queues={
        "high": {"exchange": "high", "routing_key": "high"},
        "default": {"exchange": "default", "routing_key": "default"},
        "low": {"exchange": "low", "routing_key": "low"},
    },
    task_routes={
        "service_name.workers.jobs.reports.*": {"queue": "default"},
        "service_name.workers.jobs.scoring.*": {"queue": "high"},
        "service_name.workers.jobs.etl.*": {"queue": "low"},
    },
    broker_transport_options={"visibility_timeout": 3600},
    result_expires=3600,
    timezone="UTC",
    enable_utc=True,
)
```

**Critical settings for correctness:**

- `task_acks_late=True` + `task_reject_on_worker_lost=True` — a crashed worker returns the job to the queue instead of losing it. Combined with idempotency keys, this gives at-least-once delivery that is safe to retry.
- `worker_prefetch_multiplier=1` — one task per worker at a time. Prevents long tasks blocking short ones when workers have prefetched ahead.
- `visibility_timeout` — must exceed the longest job duration, or the broker will redeliver mid-run.

### Task definition

```python
# src/service_name/workers/jobs/reports.py
from ..celery_app import app
from ...domain.reports import build_sales_report

@app.task(
    bind=True,
    name="reports.build_sales_report",
    autoretry_for=(TransientError,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    max_retries=3,
)
def build_sales_report(self, tenant_id, params, idempotency_key):
    ...
```

### Celery worker invocation

```bash
/var/www/myapp-sidecar/.venv/bin/celery -A service_name.workers.celery_app worker \
  --loglevel=info \
  --queues=high,default,low \
  --concurrency=4 \
  --max-tasks-per-child=200 \
  --hostname=worker-%h-%n
```

- `--concurrency` — prefork processes. Same sizing rule as RQ.
- `--max-tasks-per-child` — recycle after N tasks to bound memory.
- Prefer prefork over gevent/eventlet unless every dependency is green-thread safe.

### Celery beat

Separate systemd unit, single instance only (never two beats — duplicate schedules).

```bash
/var/www/myapp-sidecar/.venv/bin/celery -A service_name.workers.celery_app beat \
  --loglevel=info \
  --pidfile=/run/myapp/celerybeat.pid \
  --schedule=/var/lib/myapp/celerybeat-schedule
```

Use `redbeat` as the scheduler when you need leader election for HA. Plain filesystem beat is a SPOF.

## Redis tuning (both RQ and Celery)

In `/etc/redis/redis.conf`:

```text
maxmemory 512mb
maxmemory-policy noeviction
appendonly yes
appendfsync everysec
tcp-keepalive 60
timeout 0
save ""
```

Rules:

- `maxmemory-policy noeviction` — a job queue must never lose messages to eviction. If Redis fills up, fail fast and page someone.
- `appendonly yes` with `everysec` — durable enough for job queues on a single host.
- Disable RDB snapshots (`save ""`) — AOF is sufficient and the fork stalls hurt latency.
- Separate Redis instance for jobs vs cache when traffic grows. Different eviction policies, different tuning.

### Connection pooling

Both RQ and Celery reuse a single `redis.Redis` connection per worker. Set `socket_keepalive=True`. Do not spin up a new client per job.

## Observability for workers

- Heartbeat: every worker updates a Redis key `worker:{name}:heartbeat` every 30s. Monitoring alerts if the key disappears.
- Queue depth: scrape `LLEN` on each RQ list or Celery queue name. Alert when depth > threshold or oldest-job age > SLA.
- Per-job histogram: emit `job_duration_seconds{name, status}` and `job_failures_total{name, reason}` from the wrapper.

## Anti-patterns

- Mixing RQ and Celery. Pick one per project.
- Using the same Redis DB for cache and jobs. Use separate databases or separate instances.
- Running Celery beat on two hosts simultaneously without leader election.
- Enqueueing jobs with large inline payloads. If the payload is > 256 KB, write it to S3/local storage and pass the URL.
- Catching all exceptions inside the task and returning "ok". Let the task raise so Celery/RQ's retry machinery can see it.
