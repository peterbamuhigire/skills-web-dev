# Logging with structlog

Expands the **Logging** section of `SKILL.md`. Covers setup, JSON vs plain renderers, request-scoped context via contextvars, correlation IDs, and integration with the stdlib logging module.

## Why structlog

Structured logs are queryable. `print("order 42 failed")` is noise; `logger.error("order_failed", order_id=42, tenant_id=7, reason="timeout")` is a filterable JSON document. In production we ship to Loki / CloudWatch / ELK — all of which expect JSON with consistent field names.

Rules:

- Never use `print()` in application code. It bypasses levels, filters, formatters, and goes to stdout without context.
- Never use f-strings inside log messages (`logger.info(f"processed {n}")`). The message becomes a unique string per n value, defeating grouping. Pass structured kwargs.
- Log events (verb-noun, snake_case) as the first positional arg: `logger.info("invoice_created", ...)`.

## Setup

```python
# src/service_name/logging_config.py
from __future__ import annotations

import logging
import sys
from typing import Any

import structlog
from structlog.contextvars import merge_contextvars
from structlog.processors import (
    CallsiteParameter,
    CallsiteParameterAdder,
    JSONRenderer,
    TimeStamper,
    add_log_level,
    dict_tracebacks,
    format_exc_info,
)
from structlog.stdlib import BoundLogger, LoggerFactory, ProcessorFormatter

from service_name.config import settings


def configure_logging() -> None:
    """Configure stdlib logging and structlog. Call once at startup."""
    timestamper = TimeStamper(fmt="iso", utc=True)

    shared_processors: list[structlog.types.Processor] = [
        merge_contextvars,             # pulls request-scoped context
        add_log_level,                 # "level": "info"
        timestamper,                   # "timestamp": "2025-..."
        CallsiteParameterAdder(
            parameters=[
                CallsiteParameter.MODULE,
                CallsiteParameter.FUNC_NAME,
                CallsiteParameter.LINENO,
            ]
        ),
    ]

    if settings.environment == "development":
        renderer: structlog.types.Processor = structlog.dev.ConsoleRenderer(colors=True)
    else:
        renderer = JSONRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.filter_by_level,
            format_exc_info,
            renderer,
        ],
        logger_factory=LoggerFactory(),
        wrapper_class=BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Route stdlib logs (uvicorn, httpx, sqlalchemy) through structlog too
    formatter = ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            ProcessorFormatter.remove_processors_meta,
            dict_tracebacks,
            renderer,
        ],
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(settings.log_level)

    # Tame noisy libraries
    for noisy in ("uvicorn.access", "botocore", "urllib3", "httpx"):
        logging.getLogger(noisy).setLevel("WARNING")
```

Call `configure_logging()` once from the entrypoint (FastAPI app factory, worker bootstrap). Do not reconfigure in tests — use a fixture that swaps the logger for a capturing one.

## Usage

```python
import structlog

logger = structlog.get_logger(__name__)

def pay_invoice(invoice: Invoice) -> None:
    log = logger.bind(invoice_id=invoice.id, tenant_id=invoice.tenant_id)
    log.info("invoice_payment_started", amount=str(invoice.amount))
    try:
        gateway.charge(invoice)
    except GatewayError as e:
        log.exception("invoice_payment_failed", reason=str(e))
        raise
    log.info("invoice_payment_succeeded")
```

Patterns:

- Bind once at the top of a function, reuse the bound logger. Avoid re-binding the same fields at every call.
- Use `.exception(...)` inside `except` — it captures the traceback.
- Use `.info` / `.warning` / `.error` for levels. Never log success at WARNING or higher.
- Decimal values must be stringified (`str(amount)`) — JSON doesn't know Decimal.

## Request-scoped context — contextvars

We want every log line inside one request to carry `tenant_id`, `request_id`, and `user_id` without threading them through every function. `structlog.contextvars` does this using Python's `contextvars` module, which is per-task (so it works correctly in asyncio).

```python
# src/service_name/api/middleware.py
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        clear_contextvars()
        # Accept an inbound correlation ID (from PHP app, mobile app) or generate
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response


# Later, inside a handler after authentication:
from structlog.contextvars import bind_contextvars
bind_contextvars(tenant_id=current_tenant.id, user_id=current_user.id)
```

Every `logger.info(...)` inside that request automatically includes the bound fields because `merge_contextvars` is in the processor chain.

For workers:

```python
# src/service_name/workers/jobs.py
from structlog.contextvars import bound_contextvars

def process_job(job: Job) -> None:
    with bound_contextvars(job_id=job.id, tenant_id=job.tenant_id, queue=job.queue):
        logger.info("job_started", kind=job.kind)
        ...
        logger.info("job_completed")
```

`bound_contextvars` is a context manager — binds on enter, clears on exit. Use this per job so contexts don't bleed between jobs.

## Correlation IDs across services

Our SaaS runs PHP frontends, Python workers, mobile apps. A single user action can touch several services. Propagate one correlation ID so logs from every service can be joined.

Rules:

- Inbound HTTP: accept `X-Request-ID` header. Honour it if present, else generate.
- Outbound HTTP (httpx): always emit `X-Request-ID` with the bound value.
- Queue payloads: include `request_id` in the payload, re-bind it in the worker.
- Mobile apps: send their own `X-Request-ID`. We keep it.

```python
# Outbound httpx with correlation ID injection
from contextvars import ContextVar
from structlog.contextvars import get_contextvars
import httpx

def make_client() -> httpx.AsyncClient:
    async def inject_request_id(request: httpx.Request) -> None:
        ctx = get_contextvars()
        if rid := ctx.get("request_id"):
            request.headers.setdefault("x-request-id", rid)

    return httpx.AsyncClient(
        event_hooks={"request": [inject_request_id]},
        timeout=httpx.Timeout(10.0, connect=5.0),
    )
```

## JSON vs plain output

- `development`: `ConsoleRenderer(colors=True)` — readable on a terminal, colored levels, traceback rendering.
- `staging`, `production`: `JSONRenderer()` — one line per log, consumed by the log pipeline.

The environment-based switch in `configure_logging()` is the only place to make this decision. Do not let individual modules choose their own renderer.

## Sensitive data

Never log:

- Passwords, password hashes, API keys, session tokens.
- Raw webhook bodies from payment providers (may contain card metadata).
- PII beyond what your DPIA permits.

Patterns:

- Redact at the source: use `SecretStr` from Pydantic so `repr()` doesn't leak.
- For structured payloads, add a processor that redacts known keys:

```python
SENSITIVE = {"password", "token", "secret", "authorization", "cookie", "api_key"}

def redact_sensitive(
    _: structlog.types.WrappedLogger, __: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    for key in list(event_dict):
        if any(s in key.lower() for s in SENSITIVE):
            event_dict[key] = "***"
    return event_dict
```

Add this processor before the renderer.

## Integrating with stdlib logging

Many libraries (sqlalchemy, httpx, boto3, uvicorn) use stdlib `logging`. The `ProcessorFormatter` block in `configure_logging()` above routes them through the same processor chain so their logs also come out as JSON in production with the same fields.

For libraries whose logs are noisy even at INFO, set their level higher explicitly:

```python
logging.getLogger("sqlalchemy.engine").setLevel("WARNING")  # unless debugging queries
logging.getLogger("uvicorn.access").setLevel("WARNING")     # we log access ourselves
```

## Performance

- `cache_logger_on_first_use=True` avoids rebuilding the logger on every call. Always enable.
- JSON renderer is fast (~100k logs/sec on modern hardware). It is not a bottleneck.
- Building a bound logger is cheap; calling `.bind` in a hot loop is fine.
- Avoid logging inside tight loops. If you need to, sample (e.g. every 100th iteration) or log the aggregate afterwards.

## Anti-patterns

- Using `logging` directly with f-strings: `logging.info(f"tenant {tid} failed")`. Loses the structure.
- Logging exceptions with `logger.error(str(e))`. Loses the traceback. Use `logger.exception(...)`.
- Binding `request_id` manually in every function. Use contextvars.
- Having two loggers in a file (`log = logger.bind(...)` at module level then rebinding). Get a logger per function.
- Logging "started" / "completed" without the key identifiers (`tenant_id`, `job_id`). Logs without IDs are unsearchable.

## Cross-references

- Correlation ID propagation: `python-saas-integration` skill for FastAPI + PHP + mobile.
- Observability strategy: `observability-monitoring` skill.
- Error handling: `error-handling.md` (every raised error should log once at the boundary).
