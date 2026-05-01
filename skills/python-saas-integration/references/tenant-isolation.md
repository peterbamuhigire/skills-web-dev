# Tenant Isolation in Python Services

Multi-tenant SaaS means one Python process serves many tenants. One leak is catastrophic. This file covers propagation, validation, enforcement, and the traps specific to long-running worker processes.

## Rules

1. Every request and every job carries `tenant_id`.
2. `tenant_id` is bound into the HMAC signature — a PHP client for tenant A cannot forge a call for tenant B.
3. Python validates `tenant_id` exists and is active before any work.
4. Every DB query filters by `tenant_id`. No exceptions, no "internal" queries.
5. Every cache key is prefixed with `tenant_id`.
6. Every log line carries `tenant_id`.
7. No module-level, class-level, or process-level state ever holds tenant data.

Treat these as invariants. A PR that breaks any of them does not ship.

## Propagation: sidecar

From `X-Tenant-Id` header, validated against the HMAC payload (see `php-python-contract.md`), then bound to a request-scoped context.

```python
# src/service_name/tenant.py
from contextvars import ContextVar
from dataclasses import dataclass

@dataclass(frozen=True)
class TenantContext:
    tenant_id: str
    features: frozenset[str]

_current: ContextVar[TenantContext | None] = ContextVar("tenant", default=None)

def set_tenant(ctx: TenantContext) -> None:
    _current.set(ctx)

def current_tenant() -> TenantContext:
    ctx = _current.get()
    if ctx is None:
        raise RuntimeError("tenant context not set")
    return ctx
```

Always access tenant via `current_tenant()`. Never pass `tenant_id` as an optional kwarg that defaults to `None` — that is how leaks happen.

## Propagation: worker

Workers have no request scope. The job payload carries `tenant_id`; the worker wrapper binds it before calling the task body.

```python
# src/service_name/workers/wrapper.py
from functools import wraps
from ..tenant import set_tenant, TenantContext
from ..db.session import sync_session
from ..domain.tenants import load_tenant
import structlog

def tenant_scoped(fn):
    @wraps(fn)
    def inner(tenant_id, *args, **kwargs):
        with sync_session() as db:
            tenant = load_tenant(db, tenant_id)
            if tenant is None or not tenant.is_active:
                raise PoisonMessage("FORBIDDEN_TENANT", tenant_id)
        set_tenant(TenantContext(
            tenant_id=tenant.id,
            features=frozenset(tenant.features),
        ))
        structlog.contextvars.bind_contextvars(tenant_id=tenant.id)
        try:
            return fn(*args, **kwargs)
        finally:
            structlog.contextvars.unbind_contextvars("tenant_id")
    return inner
```

Apply it at every task entry point:

```python
@app.task(name="reports.build_sales_report")
@tenant_scoped
def build_sales_report(params, idempotency_key):
    ...
```

The wrapper *also* validates the tenant against the DB. Never trust the payload's `tenant_id` alone — the enqueue may have been written before the tenant was suspended.

## DB enforcement: SQLAlchemy event listeners

Belt-and-braces. Every query gets filtered even if a developer forgets.

```python
# src/service_name/db/tenant_scope.py
from sqlalchemy import event
from sqlalchemy.orm import Query
from ..tenant import current_tenant
from .models import TenantScoped  # mixin base for tenant-scoped models

@event.listens_for(Query, "before_compile", retval=True)
def _filter_by_tenant(query):
    if getattr(query, "_skip_tenant_filter", False):
        return query
    for desc in query.column_descriptions:
        entity = desc.get("entity")
        if entity and issubclass(entity, TenantScoped):
            tenant_id = current_tenant().tenant_id
            query = query.filter(entity.tenant_id == tenant_id)
    return query
```

Models that hold tenant data inherit the `TenantScoped` mixin:

```python
from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_mixin

@declarative_mixin
class TenantScoped:
    tenant_id = Column(String(32), nullable=False, index=True)
```

The `_skip_tenant_filter` escape hatch is only for cross-tenant maintenance jobs (admin analytics, tenant provisioning). Grep the codebase — it should appear fewer than ten times.

### Write-path defence

The listener filters reads. Writes need their own check. Enforce in a `before_insert` / `before_update` event:

```python
@event.listens_for(TenantScoped, "before_insert", propagate=True)
def _stamp_tenant_on_insert(mapper, connection, target):
    ctx_tenant = current_tenant().tenant_id
    if target.tenant_id and target.tenant_id != ctx_tenant:
        raise PermissionError("tenant_id mismatch on insert")
    target.tenant_id = ctx_tenant
```

## MySQL: Row-level considerations

MySQL does not have Postgres RLS. Rely on:

- Application-level filtering (above).
- Composite indexes `(tenant_id, ...)` on every table — keeps queries fast *and* reminds the reader this table is tenant-scoped.
- A read-only DB user per environment. A background report process that leaks a query against another tenant should not have permission to read the whole table — but this is hard in practice because most apps use a single user. Be honest about the limitation and double down on the app-level filter.

## Cache namespacing

Every Redis key gets the tenant prefix. Wrap the client so it is impossible to forget:

```python
class TenantRedis:
    def __init__(self, r): self.r = r
    def _k(self, key: str) -> str:
        return f"t:{current_tenant().tenant_id}:{key}"
    async def get(self, key): return await self.r.get(self._k(key))
    async def set(self, key, val, **kw): return await self.r.set(self._k(key), val, **kw)
```

Routes receive `TenantRedis` via `Depends()`, never the raw client. The raw client is available only to infrastructure code (health checks, queue management).

## Worker pitfalls — module-level state

The single biggest cross-tenant leak risk in Python workers.

**Never:**

```python
# WRONG - module-level cache leaks across tenants in the same worker
_price_cache: dict[str, float] = {}

def score(product_id):
    if product_id not in _price_cache:
        _price_cache[product_id] = load_price(product_id)
    return _price_cache[product_id]
```

A worker process handles tenant A then tenant B. `_price_cache` still holds A's data when B runs. If a `product_id` collides (often deliberate — UUID vs numeric IDs vary per tenant), B sees A's price.

**Right:**

```python
# Tenant-scoped cache
def score(product_id):
    cache_key = f"price:{product_id}"
    return redis.get(cache_key) or load_price(product_id)  # TenantRedis prefixes
```

If you must cache in-process, key every entry by `(tenant_id, ...)` and bound the size:

```python
from cachetools import LRUCache
_cache = LRUCache(maxsize=10_000)

def score(product_id):
    ctx = current_tenant()
    key = (ctx.tenant_id, product_id)
    if key not in _cache:
        _cache[key] = load_price(product_id)
    return _cache[key]
```

Other forms of module-level state to watch for:

- Default mutable arguments (`def f(items=[])`). Reset each call or use `None`.
- `functools.lru_cache` on functions that take `tenant_id` — fine. On functions that don't — leak.
- ML model warm-up: cache the model (tenant-independent). Never cache the *prediction* at module level.
- Pandas DataFrames held in globals for "performance" — forbidden.

## Logging

Every log line carries `tenant_id` via structlog contextvars. A log line without `tenant_id` is a bug.

Enforce it in the processor:

```python
def require_tenant(logger, method, event_dict):
    if "tenant_id" not in event_dict:
        event_dict["tenant_id"] = "MISSING"
        event_dict["_tenant_missing_warning"] = True
    return event_dict
```

Alert on `_tenant_missing_warning`. It surfaces code paths that bypass the wrappers.

## Tests

Two kinds:

1. **Unit:** the tenant wrapper refuses unknown or suspended tenants.
2. **Integration:** every endpoint/job run under a mocked tenant produces no queries without a `WHERE tenant_id = ...` clause. Assert by capturing SQL via `sqlalchemy.event.listen(Engine, "before_cursor_execute", ...)` in a pytest fixture and grepping the recorded statements.

The integration test is the one that catches the listener escape hatch being left on.

## Incident playbook (cross-tenant leak suspected)

1. Freeze the suspected endpoint/job: disable the feature flag, stop the worker queue.
2. Pull logs for the time range, filtered by `correlation_id` or affected `tenant_id`.
3. Identify impact scope: which tenants saw which data.
4. Notify affected tenants per your contractual obligation.
5. Patch the specific leak; do not just patch the symptom.
6. Add a regression test that would have failed before the fix.
7. Post-mortem: how did the filter miss? Usually: new table without the mixin, or a raw SQL string bypassing SQLAlchemy.
