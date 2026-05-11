---
name: saas-rate-limiting-and-quotas
description: Use when designing per-tenant rate limits and quotas — algorithm choice (token bucket, sliding window, leaky bucket, fixed window), where to enforce (edge, gateway, service, DB connection pool, queue), per-plan / per-tier limits, soft vs hard caps, fair-queueing for noisy neighbors, headers and error responses, and how to expose quota usage to the tenant.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# SaaS Rate Limiting and Quotas
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Designing per-tenant rate limits for a pooled or mixed-mode SaaS to prevent noisy-neighbor degradation.
- Adding plan-aware quotas (Pro gets 100k API calls/month; Enterprise gets unlimited).
- Implementing fair-queueing so a single heavy tenant doesn't starve the shared worker pool.
- Surfacing quota usage to the tenant (`X-RateLimit-Remaining`, in-product usage panel).
- Coordinating limits across multiple enforcement points (edge, gateway, service, DB pool, queue).
- Designing the response contract when limits are hit (status codes, headers, error body).

## Do Not Use When

- The task is general application performance — use `frontend-performance` / backend perf skills.
- The task is the entitlements engine itself (what limits exist per plan) — use `saas-entitlements-and-plan-gating`. This skill is the *enforcement* runtime.
- The task is queue-based fair scheduling alone — use queue-specific skills.

## Required Inputs

- Plan × limit catalogue from `saas-entitlements-and-plan-gating`.
- Deployment model (pool vs mixed vs silo) from `saas-deployment-models` — affects where enforcement lives.
- Tenant-count and request-volume estimates — drives algorithm + storage choice.
- Existing edge/gateway/proxy in front of the app (Cloudflare, ALB, Nginx, Envoy, Kong).

## Workflow

1. Read this `SKILL.md`.
2. Inventory what to limit (§2) — request-rate, concurrency, monthly-quota, per-resource quota.
3. Pick the algorithm per limit type (§3) — token bucket / sliding window / fixed window / leaky bucket.
4. Pick the enforcement layer (§4) — edge / gateway / app / DB / queue.
5. Pick the storage (§5) — Redis is default; vendor-managed for huge scale.
6. Design the response contract (§6) — status codes, headers, body, retry-after.
7. Add fair-queueing for shared resources (§7) — heavy tenants don't starve light ones.
8. Surface usage to the tenant (§8) — UI panel + API endpoint.
9. Apply anti-patterns (§9).

## Quality Standards

- Limits enforced **before** the resource is consumed (gate first, work second).
- Atomic check-and-increment — no race condition that allows over-limit slip-through.
- Limit decisions cached close to the request — typically Redis, sub-millisecond.
- Response includes `Retry-After`, `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.
- Per-tenant fair-queueing in shared async workers prevents one tenant starving others.
- Every limit hit emits an event for analytics and lifecycle email (`usage.approaching_limit` / `usage.limit_hit`).

## Anti-Patterns

- Per-IP rate limiting only — multiple tenants behind a corporate NAT share IP; one bad tenant penalises others.
- Per-API-key rate limiting only — tenant has multiple keys; aggregate limit isn't enforced.
- SELECT count + INSERT race condition — between check and increment, multiple requests slip through.
- App-only enforcement when edge could shed the load — wastes resources processing requests destined to be 429'd.
- No fair-queueing — one big tenant's batch report dominates the worker pool and breaks SLA for everyone else.
- No tenant-facing usage panel — customers have no idea why they're being limited.

## Outputs

- Limit inventory + algorithm + enforcement-layer per limit.
- Storage architecture (Redis cluster / vendor).
- Response contract (status, headers, body).
- Fair-queueing design for async work.
- Tenant-facing usage panel + API.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Architecture | Rate-limit + quota inventory | Markdown table | `docs/saas/rate-limits.md` |
| Release evidence | Response contract spec | Markdown doc with examples | `docs/saas/rate-limit-response.md` |
| Operability | Limit hit + denial dashboard | Dashboard link | `docs/saas/quota-dashboard.md` |

## References

- `references/algorithms.md` — token bucket, sliding window, leaky bucket, fixed window — when each fits.
- `references/fair-queueing-patterns.md` — per-tenant queues, weighted fair queueing, DRR.
- `references/redis-implementation.md` — atomic Lua scripts for token bucket + sliding window.
- Companion: `saas-entitlements-and-plan-gating`, `saas-deployment-models`, `multi-tenant-saas-architecture`, `observability-monitoring`, `microservices-resilience`.

<!-- dual-compat-end -->

## §1 The Four Things to Limit

| Type | Example | Time horizon |
|---|---|---|
| **Request rate** | 100 req/sec per tenant | seconds |
| **Concurrency** | Max 50 in-flight requests per tenant | instantaneous |
| **Period quota** | 100k API calls per month | rolling month |
| **Per-resource quota** | 10 active workflows per tenant | always-on (entitlement) |

Most SaaS need all four.

## §2 The Limit Inventory

For every SaaS, list:

| Limit | Type | Per-plan values | Enforcement layer | Storage |
|---|---|---|---|---|
| API requests | rate | free 10/s, pro 100/s, enterprise 1000/s | gateway | Redis |
| API requests | period | free 1k/mo, pro 100k/mo, enterprise unlimited | gateway | Redis + DB |
| Concurrent requests | concurrency | free 5, pro 50, enterprise 500 | gateway | Redis |
| Webhook deliveries | rate | 100/s per tenant | worker | Redis |
| DB connections | concurrency | per-tenant pool size | DB pool | PgBouncer / pg pooler |
| Heavy reports | concurrency | free 1, pro 5, enterprise 20 | worker | Redis |
| AI token budget | period | per AI plan | service | DB |
| Login attempts | rate | 5/min per IP+email | app | Redis |

## §3 Algorithm Choice

### Token Bucket
- **Best for:** request-rate with burst tolerance.
- Refills at fixed rate; allows burst up to bucket size.
- Use for: API request rate limits.

### Sliding Window
- **Best for:** strict rolling-window enforcement, smooths over burst boundaries.
- Tracks request timestamps; counts in window.
- Use for: per-month quota with rolling window.

### Fixed Window
- **Best for:** simple, low-cost; OK if boundary-burst is acceptable.
- Reset at period boundary.
- Use for: per-day / per-month counters where boundary burst is benign.

### Leaky Bucket
- **Best for:** smoothing — work drains at fixed rate.
- Use for: queue-based work scheduling.

### Concurrency Limit
- **Best for:** in-flight request gate.
- Atomic INCR on entry; DECR on exit; reject if > limit.
- Use for: max concurrent requests, max concurrent reports.

**Default recommendation:** token bucket for rate, sliding window for period quotas, atomic counter for concurrency.

## §4 Enforcement Layer

```
Edge / CDN (Cloudflare, Fastly, CloudFront)
  ↓
Gateway (Kong, Envoy, Tyk, AWS API Gateway, ALB)
  ↓
Application / service
  ↓
Database connection pool (PgBouncer / pgpool / RDS Proxy)
  ↓
Async worker (with per-tenant queues)
```

Enforce as close to the edge as possible. Reasons:
- The closer to the edge, the less wasted work.
- Edge can return 429 in < 5ms; app can't.
- Edge integrates with WAF and DDoS protection.

**Pattern:**
- Edge: coarse rate limits (per-IP DDoS protection, simple plan-tier global rate).
- Gateway: per-tenant rate + concurrency limits (most enforcement).
- App: per-feature-specific limits that need business logic.
- DB pool: per-tenant connection cap.
- Worker: per-tenant queue partitioning + fair-queueing.

## §5 Storage

| Storage | Latency | Capacity | Use case |
|---|---|---|---|
| Redis (single) | < 1ms | up to ~50k ops/sec | Default for most SaaS |
| Redis cluster | < 1ms | millions ops/sec | At scale |
| Cloudflare Rate Limiting Rules / WAF | < 1ms | unlimited (their infra) | DDoS + simple per-IP/per-route |
| AWS API Gateway throttling | < 5ms | scaled | If on API Gateway already |
| In-memory (per-process) | sub-µs | scoped to one process | NOT for multi-instance; only for local rate limits |
| DB (Postgres counter) | 1-5ms | ops/sec | For period quotas reconciled periodically |

**Default:** Redis (managed: ElastiCache / Upstash / Redis Cloud) with atomic Lua scripts.

### Atomic token-bucket in Redis (Lua)

```lua
-- KEYS[1] = bucket key (e.g., "rl:tenant:123")
-- ARGV[1] = capacity, ARGV[2] = refill_per_second, ARGV[3] = now_ms, ARGV[4] = cost
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now_ms = tonumber(ARGV[3])
local cost = tonumber(ARGV[4])

local b = redis.call('HMGET', KEYS[1], 'tokens', 'last_ms')
local tokens = tonumber(b[1]) or capacity
local last_ms = tonumber(b[2]) or now_ms

local elapsed = math.max(0, now_ms - last_ms)
tokens = math.min(capacity, tokens + (elapsed / 1000) * refill_rate)

local allowed = 0
if tokens >= cost then
    tokens = tokens - cost
    allowed = 1
end

redis.call('HMSET', KEYS[1], 'tokens', tokens, 'last_ms', now_ms)
redis.call('PEXPIRE', KEYS[1], math.ceil(capacity / refill_rate * 1000 * 2))
return {allowed, tokens}
```

## §6 Response Contract

**HTTP 429 Too Many Requests** for rate / concurrency violations.

**HTTP 402 Payment Required** or **HTTP 403 Forbidden** for plan-quota violations (the user needs to upgrade, not just wait).

**Headers (always include):**
- `X-RateLimit-Limit: 100` — total in window.
- `X-RateLimit-Remaining: 0` — current remaining.
- `X-RateLimit-Reset: 1746576000` — unix timestamp when window resets.
- `Retry-After: 30` — seconds to wait (only on 429).

**Body:**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "You have exceeded 100 requests/minute. Retry in 30 seconds.",
    "retry_after_seconds": 30,
    "limit_type": "api_rate_per_minute",
    "tenant_id": "ten_123"
  }
}
```

For quota (period or plan):
```json
{
  "error": {
    "code": "QUOTA_EXCEEDED",
    "message": "Monthly API call limit of 100,000 reached. Upgrade your plan to continue.",
    "limit_type": "api_calls_monthly",
    "current_usage": 100000,
    "limit_value": 100000,
    "upgrade_url": "https://app.example.com/billing/upgrade?context=api_quota"
  }
}
```

## §7 Fair-Queueing for Shared Workers

Without fair-queueing, one tenant's 10,000-job batch saturates the worker pool. Patterns:

### Per-tenant queues + round-robin dispatcher
```
Producers → push to per-tenant queue (e.g., Redis Lists keyed `q:tenant:123`)
Dispatcher → round-robins across active tenant queues; pushes one job to shared worker pool per turn
Workers → consume from shared pool
```

### Weighted fair queueing
- Each tenant has a weight (often `weight = ceil(plan_seats / 10)` or `weight = tier_factor`).
- Dispatcher gives bigger tenants more turns per cycle; smaller tenants never starve.

### Per-tenant concurrency cap
- Per-tenant counter; max concurrent jobs = function of plan.
- Heavy tenant's overflow waits in their own queue; doesn't enter shared pool.

### Engines that help
- **Sidekiq Pro/Enterprise**: concurrency groups, rate limits.
- **Temporal**: per-namespace concurrency limits.
- **Celery**: per-queue routing + concurrency.
- **Custom**: Redis-backed per-tenant queues + a dispatcher process.

## §8 Surface Usage to the Tenant

Tenants who don't know they're being limited are angry tenants.

- **In-product panel:** "API calls this month: 87,432 / 100,000 (87%)".
- **API endpoint:** `GET /api/v1/me/quota` returns current usage + limits per metered dimension.
- **Approaching-limit emails:** 70% → soft, 90% → strong, 100% → block-message email (see `saas-lifecycle-email-orchestration`).
- **Per-request headers** on every API call: `X-RateLimit-*`.
- **Webhook on threshold:** for enterprise tenants, send a webhook when they cross 80%/90%/100% so their ops team knows.

## §9 Anti-Patterns

- **Per-IP rate limit only.** Corporate NAT means one bad employee blocks the whole company; or one bad cluster blocks one customer.
- **Synchronous quota check via SQL `SELECT COUNT(*)` per request.** Slow + race-prone. Fix: Redis counter.
- **No fair-queueing in shared workers.** One tenant's batch destroys SLA for the rest.
- **No 429 + Retry-After.** Clients hammer the API blindly.
- **No quota panel for the tenant.** Mystery throttling = support tickets + churn.
- **Quota counters never reset on period rollover.** Accidental permanent block.
- **Burst capacity too low.** Cron-driven clients submit 1k jobs at the top of the hour; legitimate burst is rate-limited.
- **No emission of `usage.approaching_limit` event.** Lifecycle email can't trigger; expansion revenue lost.

## §10 Read Next

- `saas-entitlements-and-plan-gating` — defines what limits exist per plan.
- `saas-deployment-models` — drives where enforcement lives.
- `multi-tenant-saas-architecture` — tenant context drives the bucket keys.
- `microservices-resilience` — circuit breakers, bulkheads (complementary to rate limits).
- `observability-monitoring` — surface limits + denials in dashboards.
- `saas-lifecycle-email-orchestration` — emit approaching-limit events for upgrade triggers.

## AI Quotas Addendum

AI features introduce distinct quota dimensions beyond generic API rate limits:

| AI dimension | Type | Per-plan example | Enforcement layer |
|---|---|---|---|
| AI tokens / minute | rate | Free 1k/m, Pro 100k/m, Enterprise 1M/m | LLM gateway (Redis token bucket) |
| AI generations / day | period | Free 50, Starter 500, Pro 5k | LLM gateway (sliding window) |
| AI tokens / month | period | Free 100k, Pro 20M | LLM gateway + DB |
| AI USD / month | period (currency) | Free $0, Pro $50, Enterprise custom | LLM gateway |
| Concurrent agent sessions | concurrency | Free 0, Business 5, Enterprise 50 | gateway + worker |
| Agent steps per session | per-resource | Free 0, Business 20, Enterprise 50 | agent runtime |
| KB pages ingested | period | Starter 500, Pro 10k | KB service |
| Embedding-jobs / hour per tenant | rate | tier-specific | ingestion dispatcher |

Where enforced:
- **LLM gateway** is the chokepoint for token, generation, USD caps.
- **Agent runtime** enforces step caps and concurrent agent sessions.
- **KB service** enforces ingestion-rate and total-pages caps.

## Agent Quotas (Detailed)

Agentic features need a richer quota set than single-shot AI. The dimensions:

| Quota | Algorithm | Default — Pro | Default — Enterprise | Enforcement |
|---|---|---|---|---|
| Concurrent agent sessions per tenant | concurrency counter (atomic INCR/DECR in Redis) | 3 | 20 | Runtime task-create handler |
| Agent steps per tenant per day | sliding window | 500 | 10,000 | Runtime step-enter handler |
| Agent tasks per user per hour | token bucket | 20 | 100 | Runtime task-create handler |
| Long-running tasks (wallclock > 5 min) in-flight per tenant | concurrency counter | 1 | 10 | Runtime task-create handler |
| Per-task wallclock cap | budget (`ai-agent-cost-and-step-budgets`) | 5 min | 30 min | Runtime budget check |
| Per-task cost cap (USD) | budget | $1 | $10 | Runtime budget check |
| Standing approvals invocations per tenant per day | counter | 100 | unlimited | Approval runtime |

### Concurrency Counter Pattern

```python
def claim_agent_session(tenant_id: int, max_concurrent: int) -> bool:
    key = f"agent:concurrent:{tenant_id}"
    val = redis.incr(key)
    redis.expire(key, 86400, nx=True)
    if val > max_concurrent:
        redis.decr(key)
        return False
    return True

def release_agent_session(tenant_id: int):
    redis.decr(f"agent:concurrent:{tenant_id}")
```

`release` is called on every task terminal transition (`COMPLETED`, `FAILED`, `KILLED`, `BUDGET_EXCEEDED`, `ABANDONED`). A janitor reconciles drift by counting actual in-flight tasks vs counter every 5 minutes.

### Response on Limit Hit

```json
{
  "error": "agent_concurrency_limit",
  "code": "AGENT_CONCURRENCY_LIMIT",
  "current": 3,
  "limit": 3,
  "plan": "pro",
  "retry_after_seconds": 60,
  "upgrade_url": "/billing/upgrade?plan=enterprise&context=agent_concurrency"
}
```

The user sees: "You've reached your concurrent-agent limit (3). Wait for an active task to finish, or upgrade for 20 concurrent."

### Cross-Plane Quotas

Quotas are declared in `ai-entitlements-and-feature-gating` (catalogue) and enforced in the agent runtime (this skill's runtime layer). The two skills hold the contract:
- Entitlements: which keys exist, per-plan values, per-tenant overrides.
- Rate limiting: which algorithms enforce them, which storage, which response shape.

Cross-references:
- `ai-agent-runtime-architecture` — where agent quotas are enforced.
- `ai-agent-cost-and-step-budgets` — per-task budgets (the inner quota layer).
- `ai-entitlements-and-feature-gating` — agent quota catalogue.
- `ai-model-gateway` — implements per-tenant token+USD caps.
- `ai-cost-per-tenant-attribution` — soft/hard ceilings with comms.
- `ai-rag-multi-tenant` — KB-side caps.
- `ai-on-saas-architecture` — overall architecture.
