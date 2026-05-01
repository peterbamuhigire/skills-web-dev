# FastAPI Sidecar

How to structure, run, and operate a FastAPI service that lives on `127.0.0.1:8001` next to the PHP app. Assumes you know FastAPI basics; focuses on the production integration.

## Project skeleton (src layout)

```text
myapp-sidecar/
|-- pyproject.toml
|-- uv.lock
|-- .python-version
|-- src/
|   `-- service_name/
|       |-- __init__.py
|       |-- main.py              # FastAPI app factory + lifespan
|       |-- settings.py          # pydantic-settings, env-driven
|       |-- deps.py              # Depends() wiring: db, redis, auth
|       |-- security.py          # HMAC verification
|       |-- logging.py           # structlog config
|       |-- api/
|       |   |-- __init__.py
|       |   |-- router.py        # top-level APIRouter assembly
|       |   |-- health.py        # /health + /ready
|       |   `-- v1/
|       |       |-- __init__.py
|       |       |-- kpis.py
|       |       `-- scoring.py
|       |-- domain/              # pure logic, no FastAPI imports
|       |-- db/
|       |   |-- session.py       # SQLAlchemy async engine
|       |   `-- models.py
|       `-- workers/             # shared with RQ/Celery pattern C
`-- tests/
```

Keep `api/`, `workers/`, and `domain/` as separate layers. Routers import from `domain/`; workers import from `domain/`. Never call domain logic through HTTP from a worker in the same process.

## App factory and lifespan

Use an `asynccontextmanager` lifespan — the deprecated `@app.on_event` handlers do not compose well with dependency overrides in tests.

```python
# src/service_name/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .settings import settings
from .logging import configure_logging
from .db.session import engine, dispose_engine
from .api.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(settings.log_level, settings.env)
    # Pre-warm DB pool so first request does not pay the cost.
    async with engine.connect() as conn:
        await conn.execute("SELECT 1")
    yield
    await dispose_engine()

def create_app() -> FastAPI:
    app = FastAPI(
        title="service_name sidecar",
        version=settings.version,
        docs_url=None if settings.env == "prod" else "/docs",
        redoc_url=None,
        openapi_url=None if settings.env == "prod" else "/openapi.json",
        lifespan=lifespan,
    )
    app.include_router(api_router)
    return app

app = create_app()
```

`docs_url` and `openapi_url` are disabled in production. The sidecar is internal, so there is no consumer that needs the schema at runtime — publish it to the repo instead.

## CORS

Do not enable CORS. The sidecar is bound to `127.0.0.1`; PHP calls it server-to-server. Every `Access-Control-*` header you add is one more surface that a misconfigured reverse proxy can leak. If a browser ever hits the sidecar, that is a bug upstream.

## Dependency injection

Use `Depends()` for every cross-cutting concern: DB session, Redis, authenticated caller, tenant context. This keeps routes testable and keeps the auth check impossible to skip.

```python
# src/service_name/deps.py
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from .db.session import SessionLocal
from .security import verify_hmac

async def db_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

async def authenticated_caller(
    x_internal_signature: str = Header(...),
    x_internal_timestamp: str = Header(...),
    x_tenant_id: str = Header(...),
    x_correlation_id: str = Header(...),
) -> "CallerContext":
    await verify_hmac(x_internal_signature, x_internal_timestamp)
    return CallerContext(
        tenant_id=x_tenant_id,
        correlation_id=x_correlation_id,
    )
```

Every v1 router should depend on `authenticated_caller`. Do it at the router level, not per endpoint:

```python
# src/service_name/api/v1/__init__.py
from fastapi import APIRouter, Depends
from ...deps import authenticated_caller
from . import kpis, scoring

v1 = APIRouter(prefix="/v1", dependencies=[Depends(authenticated_caller)])
v1.include_router(kpis.router)
v1.include_router(scoring.router)
```

The health router is included separately without the auth dependency.

## Health checks

Two endpoints, different jobs.

- `GET /health` — **liveness**. Returns 200 if the process is up. No I/O. systemd and the load balancer use this to decide whether to restart.
- `GET /ready` — **readiness**. Returns 200 only if DB and Redis are reachable. Use this from PHP's circuit breaker and from nginx's upstream health checks.

```python
# src/service_name/api/health.py
from fastapi import APIRouter, Depends
from sqlalchemy import text
from ..deps import db_session, redis_client

router = APIRouter()

@router.get("/health")
async def health():
    return {"ok": True}

@router.get("/ready")
async def ready(db=Depends(db_session), redis=Depends(redis_client)):
    await db.execute(text("SELECT 1"))
    await redis.ping()
    return {"ok": True}
```

Never return 200 from `/ready` when a downstream is down. Fail loudly.

## Running: uvicorn vs gunicorn + uvicorn workers

Rule:

- **Single host, 1-4 cores, simple deployments:** `uvicorn` directly with `--workers N`. Simpler, fewer moving parts, systemd handles restarts.
- **Need graceful worker recycling, max-requests, or pre-fork semantics:** `gunicorn` with `uvicorn.workers.UvicornWorker`. Pays its way when you want `--max-requests` to bound memory growth.

Default choice: uvicorn directly. Move to gunicorn only when you have a reason.

```bash
# uvicorn direct (systemd ExecStart)
/var/www/myapp-sidecar/.venv/bin/uvicorn service_name.main:app \
  --host 127.0.0.1 --port 8001 \
  --workers 2 \
  --proxy-headers \
  --forwarded-allow-ips='127.0.0.1' \
  --timeout-keep-alive 5 \
  --log-config /etc/myapp/log_config.json
```

Worker count: start with `min(2, CPU_cores)` for I/O-bound sidecars, `CPU_cores` for CPU-bound. Measure, do not guess.

## Graceful shutdown

systemd sends `SIGTERM` on `systemctl restart`. Uvicorn stops accepting new connections, lets in-flight requests finish, then exits. Two things to configure:

1. `TimeoutStopSec=30` in the systemd unit — gives uvicorn time to drain. Longer if a single request can legitimately take 20 seconds.
2. `--timeout-graceful-shutdown 25` on uvicorn — must be slightly less than `TimeoutStopSec` so systemd does not `SIGKILL` a draining worker.

In the lifespan, close pooled resources on shutdown (the engine, the redis client). Never rely on the interpreter's atexit — it runs after the event loop is already stopped.

## OpenAPI hardening

Even though OpenAPI is disabled in production, the one you publish from CI must be clean:

- No request examples with real tenant IDs or PII.
- Every endpoint declares `response_model` — this shapes the schema and strips unexpected fields.
- Every error path declares `responses={400: {"model": ErrorEnvelope}, 401: ...}` so the PHP client knows every shape it may see.
- `operation_id` is stable across versions — PHP code generators key on it.

## Error handling

One exception handler, one envelope. Never leak tracebacks.

```python
from fastapi import Request
from fastapi.responses import JSONResponse
from .errors import AppError

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.http_status,
        content={"ok": False, "error": {
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
        }},
    )

@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    logger.exception("unhandled", path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"ok": False, "error": {
            "code": "INTERNAL_ERROR",
            "message": "Internal error",
        }},
    )
```

## Request-scoped context

Bind `tenant_id`, `correlation_id`, and `request_id` to `structlog.contextvars` in middleware so every log line from that request carries them without the handler having to pass the context around.

```python
import structlog
from starlette.middleware.base import BaseHTTPMiddleware

class ContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            correlation_id=request.headers.get("x-correlation-id"),
            tenant_id=request.headers.get("x-tenant-id"),
            path=request.url.path,
            method=request.method,
        )
        return await call_next(request)

app.add_middleware(ContextMiddleware)
```

## What not to do

- Do not mount static files. The sidecar serves JSON. Assets go through nginx.
- Do not run migrations on startup. Migrations are a separate systemd oneshot unit run during deploy.
- Do not cache in module-level dicts. Use Redis and namespace every key by `tenant_id`.
- Do not `print()`. Every log goes through structlog so journald sees structured JSON.
