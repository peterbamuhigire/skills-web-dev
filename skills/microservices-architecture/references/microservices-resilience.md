# Absorbed Skill: microservices-resilience

Original entrypoint: `skills/microservices-resilience/SKILL.md`
Active parent skill: `skills/microservices-architecture/SKILL.md`
Status: Absorbed as reference material; this file preserves the old skill content for progressive disclosure.

---
name: microservices-resilience
description: Resilience patterns for microservices — circuit breaker (full implementation),
  health check endpoint design, load balancing algorithms, retry with backoff, bulkhead,
  timeout, graceful degradation, slowstart recovery, and stale cache fallback...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Microservices Resilience
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Resilience patterns for microservices — circuit breaker (full implementation), health check endpoint design, load balancing algorithms, retry with backoff, bulkhead, timeout, graceful degradation, slowstart recovery, and stale cache fallback...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `microservices-resilience` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Operability | Circuit-breaker and health-check configuration | Markdown doc covering thresholds, half-open behaviour, and health endpoint contract | `docs/services/resilience-config-orders.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Core Principle

*"Failure will occur. Design for it."* — Stetson, NGINX MRA

In a microservices architecture, the service graph is deep and every network hop is a failure opportunity. Resilience is not added after the fact — it is designed in from the start.

---

## The Circuit Breaker Pattern

*Popularised by Martin Fowler; implemented by Netflix Hystrix and NGINX Plus.*

### What It Solves

Without a circuit breaker, a failing service causes a cascade: all callers wait, exhaust connection pools, and fail too. A circuit breaker detects the failing service and stops calling it, allowing it to recover.

### The Three States

```
              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
              │         CLOSED              │
              │   Normal operation          │
              │   All requests pass through │
              └──────────┬──────────────────┘
                         │ failures > threshold
                         ▼
              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
              │          OPEN               │
              │   Service is failing        │
              │   All requests blocked      │
              │   Fallback served           │
              └──────────┬──────────────────┘
                         │ after timeout, try again
                         ▼
              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
              │       HALF-OPEN             │
              │   One probe request allowed │
              │   Success → CLOSED          │
              │   Failure → OPEN again      │
              └─────────────────────────────┘
```

### /health Endpoint — Required for Active Circuit Breaking

Every service MUST expose a `/health` endpoint. Passive health checks (detecting failure only after a request fails) are too late. Active checks probe before failure.

**Health endpoint contract:**
```json
GET /health
→ 200 OK (healthy)
{
  "status": "healthy",
  "checks": {
    "database": "ok",
    "memory_used_pct": 62,
    "queue_lag_ms": 45
  }
}

→ 503 Service Unavailable (unhealthy)
{
  "status": "unhealthy",
  "checks": {
    "database": "connection_failed",
    "memory_used_pct": 87
  }
}
```

**What to check in `/health`:**
- Database connection (attempt a `SELECT 1`)
- Memory usage (fail if > 80%)
- Disk space (fail if < 10% free)
- Queue lag (warn/fail if backing up)
- Dependent service reachability (optional — avoid chain reactions)

**PHP/Laravel `/health` implementation:**
```php
Route::get('/health', function () {
    $checks = [];
    $healthy = true;

    // DB check
    try {
        DB::selectOne('SELECT 1');
        $checks['database'] = 'ok';
    } catch (\Exception $e) {
        $checks['database'] = 'connection_failed';
        $healthy = false;
    }

    // Memory check
    $memUsedPct = round((memory_get_usage(true) / ini_parse_quantity(ini_get('memory_limit'))) * 100);
    $checks['memory_used_pct'] = $memUsedPct;
    if ($memUsedPct > 80) $healthy = false;

    return response()->json([
        'status' => $healthy ? 'healthy' : 'unhealthy',
        'checks' => $checks,
    ], $healthy ? 200 : 503);
});
```

### NGINX Plus Circuit Breaker Configuration

```nginx
upstream resizer_service {
    zone resizer 64k;
    server resizer-1.internal:8080;
    server resizer-2.internal:8080;
    server resizer-3.internal:8080;

    # Circuit breaker: mark unhealthy after 1 failed health check
    # Slowstart: recovering instance ramps to full traffic over 30s
}

# Active health check location (internal — not publicly accessible)
location @health_check_resizer {
    internal;
    health_check uri=/health match=service_healthy fails=1 interval=3s;
    proxy_pass http://resizer_service;
    proxy_ssl_session_reuse on;
}

# Health check response matcher
match service_healthy {
    status 200;
    header Content-Type ~ application/json;
    body ~ '"status":"healthy"';
}
```

### Fallback Options (in priority order)

| Option | Use When | How |
|--------|---------|-----|
| Redirect to healthy instances | Other instances available | NGINX upstream failover |
| Serve stale cached response | Read-only service, data freshness not critical | `proxy_cache_use_stale` in NGINX |
| Alternative data source | Degraded but usable alternative exists | Secondary upstream or static response |
| Rate limit + queue | Overload (not failure) | `limit_req` + async queue |
| Graceful error | No alternative | Return structured error with retry guidance |

**Stale cache fallback in NGINX:**
```nginx
proxy_cache_use_stale error timeout updating http_503;
proxy_cache_background_update on;
```

**Slowstart for recovering instances:**
```nginx
# Add to server line in upstream — ramp to full traffic over 30 seconds
server resizer-1.internal:8080 slow_start=30s;
```

---

## Load Balancing Algorithms

| Algorithm | How | Best For |
|-----------|-----|---------|
| **Round Robin** (default) | Rotate through instances equally | Uniform request weight |
| **Least Connections** | Send to instance with fewest active connections | Variable request duration |
| **Least Time** | Send to fastest-responding instance | Latency-sensitive services |
| **IP Hash** | Same client always goes to same instance | Session persistence (avoid if possible — prefer Redis) |
| **Random** | Random selection, optionally with `two` (pick best of 2 random) | High-scale, uniform load |

**NGINX upstream with Least Time:**
```nginx
upstream ai_service {
    least_time last_byte;  # route to fastest based on last complete response
    server ai-1.internal:5000;
    server ai-2.internal:5000;
}
```

---

## Retry with Exponential Backoff

Retry transient failures (network blip, service restart). Never retry:
- Non-idempotent writes (POST that creates records)
- Business logic errors (validation failure, not-found)

```php
// Retry helper for idempotent service calls
function callWithRetry(callable $fn, int $maxAttempts = 3, int $baseDelayMs = 100): mixed
{
    $attempt = 0;
    while (true) {
        try {
            return $fn();
        } catch (ServiceUnavailableException $e) {
            $attempt++;
            if ($attempt >= $maxAttempts) throw $e;
            $delayMs = $baseDelayMs * (2 ** ($attempt - 1)); // 100ms, 200ms, 400ms
            usleep($delayMs * 1000);
        }
    }
}
```

---

## Bulkhead Pattern

Isolate failure by partitioning resources. Prevent one service's failures from consuming all connection pool slots.

```php
// Separate connection pools per downstream service
// In Laravel config/database.php — separate connections per service
'connections' => [
    'enrollment_db' => [...],   // pool for enrollment-service
    'finance_db'    => [...],   // pool for finance-service — isolated
]
```

In a Kubernetes context: assign resource limits (`requests`/`limits`) per service container so one runaway service cannot starve others.

---

## Timeout Design

Every inter-service call MUST have a timeout. Never make an open-ended call.

| Call Type | Recommended Timeout |
|-----------|-------------------|
| Synchronous API call (read) | 500ms – 2s |
| Synchronous API call (write/transaction) | 2s – 5s |
| AI API call (non-streaming) | 8s – 15s |
| Async job dispatch | 200ms (just enqueue, don't wait) |
| Health check probe | 1s |

```php
// Laravel HTTP client with timeout
$response = Http::timeout(2)->get('http://enrollment-service/api/v1/students/42');
```

---

## Resilience Design Checklist

For every inter-service dependency, verify:

- [ ] Downstream service exposes `/health` with active status
- [ ] Upstream caller has a timeout configured
- [ ] Circuit breaker configured at gateway or caller level
- [ ] Fallback behaviour defined (cache / alternative / graceful error)
- [ ] Retries only on idempotent calls, with exponential backoff
- [ ] Separate connection pools per downstream (bulkhead)
- [ ] Slowstart configured for recovering instances
- [ ] Load balancing algorithm chosen for the request profile
- [ ] Alerts configured for circuit breaker state transitions

---

**See also:**
- `microservices-architecture-models` — NGINX circuit breaker implementation in each model
- `microservices-communication` — Health check propagation and service discovery
- `microservices-ai-integration` — AI service resilience and async job fallback
- `ai-ux-patterns` — User-facing error states when downstream service is unavailable
