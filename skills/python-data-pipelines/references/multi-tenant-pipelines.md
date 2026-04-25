# Multi-Tenant Pipeline Design

Every pipeline in this SaaS is multi-tenant. `tenant_id` is not a field — it is part of the pipeline's identity. Every credential, every rate limit, every log line is scoped by tenant.

## Per-tenant credentials

External integrations (Stripe, bank APIs, tax portals) use **tenant-owned** credentials. Never share a vendor account across tenants.

### Storage options

| Option | When | Trade-offs |
|---|---|---|
| **HashiCorp Vault** (KV v2) | Serious security posture; you already run Vault | Operational overhead (unseal, HA, token rotation); strong audit, lease-based access, crypto keys never hit app memory long-term |
| **AWS Secrets Manager** | AWS-first stack | Per-secret cost at scale; IAM-integrated; rotation lambdas are first-class |
| **GCP Secret Manager** | GCP-first stack | Simple; IAM-integrated; limited metadata |
| **Encrypted column in DB** | Single-host, small-scale, no cloud-vendor secret service | Cheap; requires you to manage the KEK; auditing is your problem |
| **`.env` per tenant** | Never | No rotation, no audit, leaks via backups and logs |

### Access pattern — abstract the store

```python
from abc import ABC, abstractmethod

class SecretStore(ABC):
    @abstractmethod
    def get(self, tenant_id: int, integration: str) -> dict: ...

    @abstractmethod
    def put(self, tenant_id: int, integration: str, value: dict) -> None: ...

class VaultSecretStore(SecretStore):
    def __init__(self, client): self.client = client
    def get(self, tenant_id, integration):
        path = f"saas/tenants/{tenant_id}/{integration}"
        return self.client.secrets.kv.v2.read_secret_version(path=path)["data"]["data"]
    def put(self, tenant_id, integration, value):
        path = f"saas/tenants/{tenant_id}/{integration}"
        self.client.secrets.kv.v2.create_or_update_secret(path=path, secret=value)

class DbEncryptedSecretStore(SecretStore):
    # AES-GCM with a KEK from KMS / environment; per-tenant DEK stored alongside ciphertext
    ...
```

Rules:

- One abstraction, multiple implementations. Makes moving from DB-encrypted to Vault a config change, not a rewrite.
- Secrets are **never** logged, not even at DEBUG. Wrap in a `SecretStr` type that redacts in `__repr__`.
- Cache in memory for the duration of a single pipeline run; do not cache across runs.
- On credential fetch failure, fail the run — do **not** fall back to a shared credential.

### Rotation

- Every integration supports rotation. Design the pipeline to use `TokenManager.current()` which transparently refreshes.
- A rotation event invalidates the in-memory cache. Use pub/sub (Redis channel) to notify long-running workers.

## Per-tenant rate limiting

A noisy tenant must not starve others. Rate-limit per tenant, not globally.

```python
# Token bucket per (tenant_id, integration)
def bucket_key(tenant_id: int, integration: str) -> str:
    return f"rate:{integration}:{tenant_id}"

# capacity and refill depend on tier
def bucket_config(tenant: Tenant, integration: str) -> tuple[int, float]:
    if tenant.tier == "enterprise":
        return (200, 10.0)     # 200 tokens, 10/s
    if tenant.tier == "pro":
        return (100, 5.0)
    return (30, 1.0)           # free
```

See `etl-external-apis.md` for the atomic Lua token bucket implementation.

Rules:

- Key by tenant + integration, not just tenant. A busy bank sync should not throttle Stripe.
- Never rate-limit globally by integration. If Stripe's global limit is the bottleneck, that's an upstream capacity problem; do not share it across tenants unfairly.
- Capacity values should be **below** the vendor's per-API-key limit, with headroom. If Stripe allows 100 req/s per key, cap the tenant at 80.

## Concurrency budget per tenant

Separate from rate limit: how many pipeline runs can this tenant have in-flight at once?

```python
# Redis counter, atomic inc/dec; call pattern:
# try to inc; if > budget, don't start the run
def acquire_concurrency_slot(tenant_id: int, budget: int) -> bool:
    key = f"concurrency:{tenant_id}"
    lua = """
    local v = redis.call('INCR', KEYS[1])
    redis.call('EXPIRE', KEYS[1], 3600)
    if v > tonumber(ARGV[1]) then
      redis.call('DECR', KEYS[1])
      return 0
    end
    return 1
    """
    return bool(redis_conn.eval(lua, 1, key, budget))

def release_concurrency_slot(tenant_id: int) -> None:
    redis_conn.decr(f"concurrency:{tenant_id}")
```

Budget by tier:

| Tier | Concurrency budget |
|---|---|
| Free | 1 |
| Pro | 3 |
| Enterprise | 10 |

Use this around the whole pipeline run, not per API call. A run that fans out to 10 API calls still counts as one slot.

## Per-tenant priority

When queueing background jobs, higher-tier tenants get a higher-priority queue.

```python
# RQ queue per tier
QUEUES = {
    "enterprise": Queue("pipeline_hi", connection=redis_conn),
    "pro":        Queue("pipeline_md", connection=redis_conn),
    "free":       Queue("pipeline_lo", connection=redis_conn),
}

def enqueue(tenant: Tenant, func, *args, **kwargs):
    q = QUEUES[tenant.tier]
    q.enqueue(func, tenant.id, *args, **kwargs)

# Workers dequeue with weighted priority:
# rq worker pipeline_hi pipeline_md pipeline_lo
```

Rules:

- Workers always check the highest-priority queue first.
- Never let low-tier jobs be starved indefinitely — add a dedicated low-priority worker pool sized to guarantee a minimum throughput.
- Do not use priority to silently de-prioritise paying tenants; the tiers must be published.

## Tenant ID propagation in logs

Use `structlog` with `contextvars`. Bind `tenant_id` at the start of every run; every log line inherits it.

```python
import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars

def run_pipeline(tenant_id: int, pipeline: str):
    clear_contextvars()
    bind_contextvars(tenant_id=tenant_id, pipeline=pipeline, run_id=str(uuid4()))
    log = structlog.get_logger()
    log.info("pipeline_start")
    try:
        _do_work(tenant_id)
        log.info("pipeline_done")
    except Exception:
        log.exception("pipeline_failed")
        raise
```

Rules:

- Every log line in pipeline code includes `tenant_id`. Grep-able, filterable, dashboardable.
- **Never log another tenant's data inside a given tenant's run.** If you enrich from a lookup table, confirm the join was scoped to the current `tenant_id` — otherwise a bug can leak a competitor's customer email into the wrong log.
- Clear contextvars between runs to prevent leakage across jobs in the same worker process.

## Tenant-scoped DB access

Always filter by `tenant_id`. Two patterns:

1. **Repository that takes `tenant_id`** — explicit at every call:

```python
class InvoiceRepo:
    def upsert(self, conn, tenant_id: int, invoice: DomainInvoice) -> None:
        conn.execute(UPSERT_SQL, {"tenant_id": tenant_id, **invoice.model_dump()})
    def get_by_external_id(self, conn, tenant_id: int, ext_id: str):
        return conn.execute(SELECT_SQL, {"tenant_id": tenant_id, "ext_id": ext_id}).first()
```

2. **Row-level security** via `@tenant_id = X` session variable + enforced views. Defence in depth, not a substitute for filtered queries.

Never trust `tenant_id` from the record payload — always inject it from the run context.

## Isolation tests

Write tests that prove tenants cannot see each other's data. One canonical test per repository:

```python
def test_invoice_repo_is_tenant_isolated(conn):
    repo = InvoiceRepo()
    repo.upsert(conn, tenant_id=1, invoice=sample_invoice(ext_id="in_A"))
    repo.upsert(conn, tenant_id=2, invoice=sample_invoice(ext_id="in_A"))

    a = repo.get_by_external_id(conn, tenant_id=1, ext_id="in_A")
    b = repo.get_by_external_id(conn, tenant_id=2, ext_id="in_A")
    assert a.id != b.id
    assert repo.get_by_external_id(conn, tenant_id=1, ext_id="in_A").tenant_id == 1
    assert repo.count_for_tenant(conn, tenant_id=99) == 0
```

Pipeline-level isolation test:

```python
def test_stripe_sync_uses_tenant_credentials(mocker):
    mock_store = mocker.Mock()
    mock_store.get.return_value = {"stripe_api_key": "sk_test_TENANT1"}
    run_sync(tenant_id=1, secret_store=mock_store)
    mock_store.get.assert_called_with(1, "stripe")
    # verify no call with any other tenant id
    assert all(c.args[0] == 1 for c in mock_store.get.call_args_list)
```

## Per-tenant quotas and cost caps

For pipelines that cost money (cloud OCR, LLM calls, SMS), add a per-tenant quota.

```python
def check_quota(tenant_id: int, resource: str, amount: int = 1) -> None:
    month = datetime.now(UTC).strftime("%Y-%m")
    key = f"quota:{resource}:{tenant_id}:{month}"
    used = int(redis_conn.get(key) or 0)
    limit = quota_for(tenant_id, resource)
    if used + amount > limit:
        raise QuotaExceeded(tenant_id, resource, used, limit)
    redis_conn.incrby(key, amount)
    redis_conn.expire(key, 60 * 60 * 24 * 45)    # keep 45 days for reconciliation
```

Rules:

- Quotas alert at 80% — gives ops time to reach out before the tenant hits the wall.
- Quotas reject at 100% with a clear error code (`quota_exceeded`) the frontend can render.
- Always make quotas overridable by an operator for emergency relief.

## Multi-tenant anti-patterns

- One Stripe API client shared by all tenants' runs. One tenant's credential in memory gets used for another's query. **Catastrophic.**
- Rate limiting globally: one noisy tenant exhausts the whole pool.
- Logging tenant data without binding `tenant_id` — cannot answer "did we leak data for tenant X?"
- Per-tenant scheduled jobs all scheduled for `02:00 UTC` exactly. Stagger by hash.
- Secrets in environment variables, keyed per tenant. Leaks via `ps`, core dumps, error reporters.
- No budget for cloud OCR / LLM calls per tenant — one tenant's 10k document upload bankrupts the pipeline.
- Not testing isolation — assume it until a bug proves otherwise.
