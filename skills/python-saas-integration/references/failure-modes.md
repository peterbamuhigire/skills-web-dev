# Failure Modes

Plan for Python being down, slow, or misbehaving. The PHP app stays up either way. This file is the playbook — patterns, code, thresholds.

## Failure taxonomy

| Failure | Impact on PHP | Mitigation |
|---|---|---|
| Sidecar down (TCP refused) | Feature unavailable | Circuit breaker open, degrade |
| Sidecar slow | Thread exhaustion, user waits | Strict timeout + breaker |
| Sidecar returns 5xx | Feature broken | Degrade on specific codes |
| Sidecar returns 429 | Throttled | Back off per Retry-After |
| Worker queue backing up | Jobs delayed, not lost | Scale workers, alert on depth |
| Worker OOM | Job dies mid-run | systemd restart, idempotent retry |
| Poison message | Worker stuck looping | DLQ after N retries |
| Redis down | Both patterns dead | Sidecar `/ready` fails, PHP degrades |
| DB down | Everything fails | Out of scope here — app-wide incident |

## Circuit breaker in PHP

Wrap every sidecar call. The breaker has three states: closed (normal), open (skip the call), half-open (one probe request to check recovery).

```php
<?php
final class SidecarBreaker
{
    private const FAILURE_THRESHOLD = 5;       // consecutive failures
    private const OPEN_FOR_SECONDS  = 30;
    private const PROBE_TIMEOUT_MS  = 2000;

    public function __construct(
        private readonly \Redis $redis,
        private readonly string $name = 'sidecar',
    ) {}

    public function allow(): bool
    {
        $state = $this->redis->hGetAll("cb:{$this->name}");
        if (($state['state'] ?? 'closed') === 'closed') return true;
        if ((int)($state['open_until'] ?? 0) > time()) return false;
        // Flip to half-open: allow one probe
        $this->redis->hSet("cb:{$this->name}", 'state', 'half_open');
        return true;
    }

    public function onSuccess(): void
    {
        $this->redis->del("cb:{$this->name}");
    }

    public function onFailure(): void
    {
        $fails = $this->redis->hIncrBy("cb:{$this->name}", 'fails', 1);
        if ($fails >= self::FAILURE_THRESHOLD) {
            $this->redis->hMSet("cb:{$this->name}", [
                'state'      => 'open',
                'open_until' => time() + self::OPEN_FOR_SECONDS,
            ]);
        }
    }
}
```

Usage:

```php
if (!$breaker->allow()) {
    return $this->degraded();  // serve cached value or feature-off UI
}
try {
    $result = $this->client->call('/v1/kpis', $payload, timeout: 5.0);
    $breaker->onSuccess();
    return $result;
} catch (TimeoutException | ConnectionException | ServerErrorException $e) {
    $breaker->onFailure();
    return $this->degraded();
} catch (ClientErrorException $e) {
    // 4xx - breaker should NOT open; the client is wrong, not Python
    throw $e;
}
```

**Do not count 4xx as breaker failures.** A validation error is not a sign the service is unhealthy. Only connection errors, timeouts, and 5xx count.

### Thresholds (starting point)

- Failure threshold: 5 consecutive failures in 60 seconds.
- Open duration: 30 seconds.
- Half-open probe: single request; if it succeeds, close; if it fails, re-open for 60 seconds (exponential up to 5 minutes).

Tune based on SLO. A noisier service wants higher thresholds; a critical dependency wants lower.

## Timeout configuration

Every network call has an explicit timeout. Defaults are set per client type:

### PHP HTTP client (to sidecar)

```php
// Guzzle
$client = new Client([
    'base_uri'       => 'http://127.0.0.1:8001',
    'timeout'        => 5.0,    // total wall clock
    'connect_timeout'=> 1.0,
    'http_errors'    => false,  // check status manually
]);
```

### Python outbound (from worker or sidecar to external APIs)

```python
import httpx

async with httpx.AsyncClient(
    timeout=httpx.Timeout(connect=2.0, read=10.0, write=5.0, pool=2.0),
    limits=httpx.Limits(max_connections=50, max_keepalive_connections=10),
    transport=httpx.AsyncHTTPTransport(retries=0),  # we handle retries
) as client:
    ...
```

### SQLAlchemy

```python
engine = create_async_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=5,
    pool_timeout=5,        # wait for a free connection
    pool_recycle=1800,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 3},
)
```

### Redis

```python
redis = redis.Redis(
    socket_connect_timeout=2.0,
    socket_timeout=5.0,
    health_check_interval=30,
)
```

Rule: **every** timeout is explicit. A library default is an incident waiting to happen.

## Dead-letter queue (DLQ)

Failed jobs go to a DLQ after N retries. Never delete them silently.

### RQ

RQ already has a `FailedJobRegistry`. The DLQ is that registry; the operator inspects it.

```python
# Operator view
from rq.registry import FailedJobRegistry
reg = FailedJobRegistry(queue=q_default)
for job_id in reg.get_job_ids()[:10]:
    job = Job.fetch(job_id, connection=redis_conn)
    print(job.exc_info, job.args, job.kwargs)
```

Wrap the job body so the failure is stored with enough context:

```python
def safe(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except PoisonMessage:
            # Don't retry - straight to DLQ
            raise
        except TransientError:
            # RQ retries per Retry policy
            raise
        except Exception:
            logger.exception("job.failed", args=args, kwargs=kwargs)
            raise
    return inner
```

### Celery

Celery has no built-in DLQ; you build one with a task failure handler.

```python
@app.task(bind=True, max_retries=3)
def my_task(self, tenant_id, params, idempotency_key):
    try:
        return _do_work(tenant_id, params, idempotency_key)
    except TransientError as e:
        raise self.retry(exc=e, countdown=2 ** self.request.retries * 10)
    except PoisonMessage as e:
        _push_to_dlq(self.request, str(e))
        return {"ok": False, "error": {"code": "POISON_MESSAGE", "message": str(e)}}

def _push_to_dlq(req, reason):
    redis_conn.lpush("dlq:jobs", json.dumps({
        "task": req.task,
        "args": req.args,
        "kwargs": req.kwargs,
        "reason": reason,
        "correlation_id": req.correlation_id if hasattr(req, 'correlation_id') else None,
        "ts": time.time(),
    }))
```

DLQ policy:

- Depth alert at > 10.
- Age alert at oldest > 1 hour.
- Operator replays after fixing. Never replay blind — understand why it failed first.

## Poison message handling

A poison message is one that *cannot* succeed no matter how many times you retry. Examples: corrupt JSON, nonexistent tenant, schema violation.

Detection rule: if a job fails for the same reason on retry #3 with the same input, it is poison. Send to DLQ immediately.

```python
class PoisonMessage(Exception):
    """Raised when the job can never succeed with this input."""

# In the wrapper
def tenant_scoped(fn):
    @wraps(fn)
    def inner(tenant_id, *args, **kwargs):
        tenant = load_tenant(tenant_id)
        if tenant is None:
            raise PoisonMessage(f"unknown tenant {tenant_id}")
        if not tenant.is_active:
            raise PoisonMessage(f"inactive tenant {tenant_id}")
        ...
```

Raise `PoisonMessage` from validation errors. The outer retry logic catches it and skips retries.

## Idempotency and replay

Every retry — automatic or manual — passes the original `idempotency_key`. The worker checks the idempotency store first:

```python
async def execute_job(tenant_id, params, idempotency_key):
    cached = await idem_store.get(tenant_id, idempotency_key)
    if cached is not None:
        logger.info("idempotent.replay", key=idempotency_key)
        return cached
    result = await _do_work(tenant_id, params)
    await idem_store.put(tenant_id, idempotency_key, result)
    return result
```

This lets you safely:

- Retry automatically on transient errors without duplicating the side effect.
- Replay a DLQ job manually without fear.
- Recover from a worker crash after the work completed but before the result was written back.

## Graceful degradation in PHP

When the sidecar is down, the PHP app must not cascade into a 500. Define the degraded path per feature:

```php
public function dashboardKpis(Tenant $tenant): DashboardKpis
{
    if (!$this->breaker->allow()) {
        return $this->cachedKpis($tenant) ?? DashboardKpis::empty();
    }
    try {
        return $this->client->kpis($tenant);
    } catch (SidecarUnavailable) {
        $this->breaker->onFailure();
        return $this->cachedKpis($tenant) ?? DashboardKpis::empty();
    }
}
```

Degradation strategies, by feature class:

| Feature | Degraded behaviour |
|---|---|
| Dashboard metrics | Show cached values with "Updated N minutes ago" badge |
| Report generation | Queue anyway — user sees "We'll email when ready" |
| ML scoring | Skip the score, show input fields; do not block the form |
| Search | Fall back to SQL LIKE, cap results |
| File conversion | Return original file with a notice |

Cache TTL for degradation is longer than the happy path: 15 minutes vs 60 seconds. A stale dashboard beats a 500 page.

## Backpressure signalling

When the worker queue is backing up, PHP should know. Two channels:

1. **Sync 429**: sidecar `/v1/jobs/enqueue` endpoint returns 429 when `queue_depth > threshold`. PHP shows a "we are busy, try in a few minutes" banner.
2. **Async flag**: a Redis key `queue:busy` is set by a monitoring worker when depth exceeds threshold. PHP checks it before presenting heavy-workload UI (e.g. hides "Export all 50k customers" button).

```python
# Set the backpressure flag from a monitor loop
async def monitor():
    while True:
        depth = await redis.llen("rq:queue:default")
        if depth > 500:
            await redis.set("queue:busy", "1", ex=120)
        await asyncio.sleep(10)
```

Better to refuse work than to accept it and never get to it.

## Worker OOM and restart loops

systemd restarts the worker on exit. If the worker OOMs processing a specific job:

1. Worker dies mid-job.
2. With `task_acks_late=True` (Celery) or equivalent RQ config, the job is requeued.
3. On retry #3 with the same input the wrapper detects it and sends to DLQ as `POISON_MESSAGE: likely_oom`.
4. Operator inspects the job, runs it with memory profiling, fixes the code or splits the input.

Never auto-retry forever. `max_retries=3` is the default; `max_retries=5` when the flakiness is genuinely transient.

## Redis outage

Both patterns depend on Redis. Behaviour during outage:

- Sidecar: `/ready` fails. nginx / PHP's health check removes it from rotation. PHP circuit breaker opens.
- Workers: `rq worker` loops retrying the connection. Celery workers do the same. Nothing is lost; jobs stay in the broker.
- PHP: enqueue call fails. Either queue the job locally (in MySQL, with a sweeper that moves to Redis when back) or return 503 to user.

Recovery: Redis comes back, sidecar `/ready` passes, workers resume. Because jobs were in Redis-with-AOF, minimal loss. If Redis lost data, the idempotency keys protect replays.

## Incident checklist

When Python goes sideways:

1. `systemctl status myapp-sidecar myapp-worker@*` — processes alive?
2. `journalctl -u myapp-sidecar -n 200` — recent errors?
3. `curl http://127.0.0.1:8001/ready` — deps reachable?
4. `redis-cli LLEN rq:queue:default` and `LLEN dlq:jobs` — backlog?
5. Prometheus: error rate, latency p95, queue depth — trending?
6. If immediate: roll back to previous release (see `deployment-debian.md`).
7. File the post-mortem. What failed, why, what changed, what prevents recurrence.
