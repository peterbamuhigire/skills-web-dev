# Scheduling

Pick the simplest scheduler that meets the need. Do not reach for Celery because you read about it somewhere.

## Decision matrix

| Scheduler | Use when | Avoid when |
|---|---|---|
| **system cron + `uv run script.py`** | Single host, once-a-day jobs, ops already manages crontabs | Multiple hosts; dynamic schedules; jobs that need in-process state |
| **APScheduler** | Python-only stack, want schedules defined in code, single process is enough | Need true distribution across many workers |
| **Celery beat** | Already running Celery for workers, jobs hand off to the worker pool | No existing Celery — don't adopt Celery just for scheduling |
| **rq-scheduler** | Already running RQ for workers | No existing RQ |
| **Kubernetes CronJobs** | Kubernetes-native deployment, want cluster to manage mutex/retry | Bare-metal / single VM |
| **Temporal / Airflow** | Complex DAGs with dependencies, backfills, long-running workflows | Nightly Stripe sync — overkill |

Rule: if you have one host and four nightly jobs, cron is the right answer. Do not add infrastructure.

## System cron

```cron
# /etc/cron.d/saas-pipelines
# m h dom mon dow user  command
0 2 * * *  app  cd /srv/app && /usr/bin/flock -n /var/run/saas-stripe.lock uv run -- python -m pipelines.stripe_sync >> /var/log/saas/stripe.log 2>&1
30 2 * * * app  cd /srv/app && /usr/bin/flock -n /var/run/saas-bank.lock   uv run -- python -m pipelines.bank_feed   >> /var/log/saas/bank.log   2>&1
```

Rules:

- Always `flock -n` to prevent overlap.
- Redirect stdout and stderr to a log file; cron will email you otherwise.
- Use absolute paths for `uv`, the working directory, and logs. Cron has an empty `PATH`.
- Set `CRON_TZ` at the top of the crontab to pin the timezone:

```cron
CRON_TZ=UTC
```

Run all pipelines in UTC. Local-time cron crosses daylight-saving boundaries and will either run twice or not at all on DST days. The dashboard can render in the user's timezone; the scheduler stays in UTC.

## APScheduler

In-process scheduler. Good when your Python service is already running and you want cron-like schedules without a system dependency.

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

def start_scheduler() -> BackgroundScheduler:
    sched = BackgroundScheduler(timezone=pytz.UTC)
    sched.add_job(
        run_stripe_sync_for_all_tenants,
        trigger=CronTrigger(hour=2, minute=0),
        id="stripe.invoices",
        max_instances=1,            # no overlap
        coalesce=True,              # if 3 runs were missed, execute once
        misfire_grace_time=60 * 30, # run within 30 min of schedule
    )
    sched.start()
    return sched
```

Rules:

- `max_instances=1` — prevents two runs overlapping.
- `coalesce=True` — if the service was down and three runs were missed, catch up with one run, not three.
- `misfire_grace_time` — if the scheduler wakes up late (process was stopped), run anyway if within grace. Beyond grace, skip.

## Mutex — Redis lock

Even with `flock` or `max_instances=1`, you need a cross-host lock when more than one machine runs the same pipeline (e.g. two API servers with a background thread each).

```python
import redis
import uuid

class RedisLock:
    def __init__(self, r: redis.Redis, key: str, ttl_seconds: int):
        self.r = r
        self.key = key
        self.ttl = ttl_seconds
        self.token = str(uuid.uuid4())

    def acquire(self) -> bool:
        return bool(self.r.set(self.key, self.token, nx=True, ex=self.ttl))

    def release(self) -> None:
        # only delete if still ours
        script = """
        if redis.call('GET', KEYS[1]) == ARGV[1] then
          return redis.call('DEL', KEYS[1])
        else
          return 0
        end
        """
        self.r.eval(script, 1, self.key, self.token)

    def __enter__(self):
        if not self.acquire():
            raise LockBusy(self.key)
        return self

    def __exit__(self, *exc):
        self.release()
```

Usage:

```python
with RedisLock(redis_conn, "pipeline:stripe.invoices:tenant:42", ttl_seconds=1800):
    sync_stripe_invoices(tenant_id=42)
```

Rules:

- `SET NX EX` is a single atomic operation. `SETNX` + `EXPIRE` separately is wrong — a crash between the two leaks a permanent lock.
- TTL must exceed the maximum realistic runtime, ideally 2× the p99. Too short = two runs overlap; too long = a crashed run holds the lock.
- The release uses a token check so a slow run doesn't delete a newer run's lock.
- For critical pipelines, extend the TTL periodically inside the job (a "heartbeat").

## Skipped runs — catch up or skip?

Decision rule per pipeline:

| Pipeline type | Missed-run behaviour |
|---|---|
| Incremental sync with watermark | **Skip missed runs, run once now.** The next run covers the gap via the watermark. Use APScheduler `coalesce=True`. |
| Full reconciliation for a specific day | **Run one job per missed day.** Queue one reconciliation job per date in the gap. |
| Nightly report email | **Skip.** Yesterday's email is stale; don't send three at 9am. |
| Scheduled reminders (e.g. invoice dunning) | **Skip, then re-evaluate from current state.** The dunning engine re-asks "what should we send today?" |

Make this explicit in the pipeline's design doc.

## Cron expression gotchas

- **Timezone.** Always pin via `CRON_TZ=UTC` or the scheduler's `timezone=` argument. Never assume.
- **Day-of-month + day-of-week together.** Cron treats `0 2 1 * 1` as "2am if either it's the 1st OR a Monday", not both.
- **`*/5`** means "every 5 minutes starting at 0". Not "every 5 minutes from now." So `*/7` runs at :00, :07, :14, :21, :28, :35, :42, :49, :56 — note the uneven gap between :56 and :00.
- **Midnight UTC on DST days.** UTC has no DST, so running in UTC eliminates this class of bug. Do it.
- **February 29.** Schedules like `0 0 29 2 *` fire only on leap years. Rarely what you want — use `L` (last day) or avoid date-specific schedules.

## Alerting on missed runs

The scheduler should record every intended run, not just every executed run. Compare:

```sql
-- how many runs of this pipeline happened yesterday?
SELECT COUNT(*) FROM pipeline_runs
WHERE pipeline_name = 'stripe.invoices'
  AND tenant_id = :t
  AND started_at >= CURDATE() - INTERVAL 1 DAY
  AND started_at <  CURDATE();
```

If the count is less than expected (e.g. daily schedule expects 1), alert.

Prometheus approach — a `pipeline_lag_seconds` gauge:

```text
pipeline_lag_seconds{pipeline="stripe.invoices",tenant="42"} = time_since_last_success
```

Alert when `pipeline_lag_seconds > 2 * expected_interval`.

## Per-tenant scheduling

Two approaches for pipelines that run per-tenant:

1. **Fan-out in one job** — one scheduled job that loops over tenants. Simplest; fine for a few dozen tenants.

```python
def run_stripe_sync_for_all_tenants():
    for tenant_id in active_tenant_ids():
        try:
            enqueue_sync_job(tenant_id)
        except Exception:
            log.exception("enqueue_failed", tenant_id=tenant_id)
```

2. **Per-tenant schedule** — one schedule per tenant, staggered. Required when tenants pay for different cadences or you need to spread load.

```python
for tenant in tenants:
    offset_minutes = hash(tenant.id) % 60
    sched.add_job(
        sync_stripe_invoices,
        args=(tenant.id,),
        trigger=CronTrigger(hour=tenant.sync_hour, minute=offset_minutes),
        id=f"stripe.invoices:{tenant.id}",
        max_instances=1,
    )
```

Stagger by hashing tenant ID into a minute offset — avoids every tenant hitting Stripe at exactly `02:00`.

## Always-idempotent

A scheduled job that is not idempotent is a bug waiting to happen. Before shipping a scheduled job, verify:

- Two back-to-back executions produce the same end state.
- An execution mid-way through that crashes and restarts produces the same end state.
- An execution that overlaps with the previous one (lock failed) does no harm — the lock acquire should be `SET NX`, and if it fails, log and exit cleanly.

## Anti-patterns

- `while True: time.sleep(3600); run_job()`. No mutex, no observability, no catch-up logic. Use a real scheduler.
- Scheduling in local time across DST.
- No mutex on scheduled jobs; two workers run the same job at the same time.
- Relying on cron emails for alerts. Use proper alerting on metrics.
- Scheduling hundreds of per-tenant jobs all at `02:00` and wondering why the database load spikes.
- Silent misfires — the job was supposed to run, didn't, and nothing noticed.
