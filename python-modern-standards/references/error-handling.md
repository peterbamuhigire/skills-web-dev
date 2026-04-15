# Error Handling

Expands the **Error handling** section of `SKILL.md`. Covers the exception hierarchy template, boundary translation (infra → domain → HTTP), retry semantics, context managers, and chaining (`raise X from Y`).

## The hierarchy

Every service has one root exception class. Every deliberate failure mode subclasses it. This lets callers catch "any application error from this module" with a single `except AppError:` while still distinguishing categories where needed.

```python
# src/service_name/exceptions.py
from __future__ import annotations

class AppError(Exception):
    """Root for every intentional application error."""

# --- validation / input ---
class ValidationError(AppError):
    """The request or payload cannot be processed."""

class NotFoundError(AppError):
    """A referenced entity does not exist."""

class ConflictError(AppError):
    """State conflict — e.g. duplicate invoice number."""

# --- authz ---
class AuthenticationError(AppError):
    """Caller identity could not be established."""

class AuthorizationError(AppError):
    """Caller is known but lacks permission."""

# --- dependencies ---
class ExternalServiceError(AppError):
    """An upstream HTTP / gRPC service failed."""

class RateLimitedError(ExternalServiceError):
    """Upstream rate-limited us."""

class TimeoutError(ExternalServiceError):   # noqa: A001 — intentional shadow of builtin in this module
    """Upstream did not respond in time."""

# --- configuration ---
class ConfigurationError(AppError):
    """Missing or invalid configuration — usually fatal at startup."""

# --- domain-specific (add as needed) ---
class InsufficientFundsError(AppError):
    """Account balance too low for the requested operation."""

class TenantSuspendedError(AppError):
    """Tenant account is suspended and cannot perform this operation."""
```

Rules:

- One exception class per failure mode, named in the imperative.
- Do not stuff HTTP status codes into exception instances. Translate at the HTTP boundary (below).
- Prefer composition (a `ValidationError` with a dict of field errors) over an exception explosion.
- Domain exceptions live in `domain/exceptions.py` if they are purely business; cross-cutting ones in the top-level `exceptions.py`.

## Boundary translation

An infrastructure error should never leak to the API layer unchanged. Translate at each boundary so the caller sees a stable contract.

```
raw driver error (asyncpg.PostgresConnectionError, httpx.ReadTimeout, ...)
        |
        v   adapter layer catches, wraps
ExternalServiceError / TimeoutError / ...
        |
        v   domain use-case catches, may re-raise as domain error
InsufficientFundsError / ValidationError / ...
        |
        v   API layer catches, maps to HTTP
HTTP 4xx / 5xx with consistent error shape
```

### Adapter layer

Wrap driver-specific exceptions at the point of I/O. The domain should never import `httpx` or `asyncpg` just to catch their errors.

```python
# src/service_name/adapters/http/stripe_client.py
import httpx
from service_name.exceptions import ExternalServiceError, RateLimitedError, TimeoutError

class StripeClient:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def charge(self, amount: Decimal, token: str) -> ChargeResult:
        try:
            response = await self._http.post(
                "/v1/charges",
                json={"amount": int(amount * 100), "source": token},
            )
            response.raise_for_status()
        except httpx.TimeoutException as e:
            raise TimeoutError("stripe charge timed out") from e
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise RateLimitedError("stripe rate limit") from e
            raise ExternalServiceError(
                f"stripe returned {e.response.status_code}"
            ) from e
        return ChargeResult.model_validate(response.json())
```

Note the `from e` — this preserves the original traceback. Never swallow the cause; it is what makes production debugging tractable.

### Domain layer

Catch infrastructure errors only when the domain has a meaningful response. Otherwise let them bubble.

```python
# src/service_name/domain/payments.py
async def charge_invoice(
    invoice: Invoice, token: str, gateway: PaymentGateway
) -> Payment:
    if invoice.amount > invoice.tenant.balance_limit:
        raise InsufficientFundsError(f"exceeds tenant limit for {invoice.tenant_id}")

    # Don't catch ExternalServiceError here — the API layer maps it to 502.
    result = await gateway.charge(invoice.amount, token)
    return Payment(invoice_id=invoice.id, external_id=result.id)
```

### API layer

Exactly one place maps our errors to HTTP. Use FastAPI's exception handlers.

```python
# src/service_name/api/error_handlers.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import structlog

from service_name.exceptions import (
    AppError, AuthorizationError, ConflictError, ExternalServiceError,
    NotFoundError, RateLimitedError, TimeoutError, ValidationError,
)

logger = structlog.get_logger(__name__)

_STATUS_FOR = {
    ValidationError: 400,
    AuthorizationError: 403,
    NotFoundError: 404,
    ConflictError: 409,
    RateLimitedError: 429,
    TimeoutError: 504,
    ExternalServiceError: 502,
}

def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        status = next(
            (s for klass, s in _STATUS_FOR.items() if isinstance(exc, klass)),
            500,
        )
        log = logger.bind(path=request.url.path, status=status, exc_type=type(exc).__name__)
        if status >= 500:
            log.exception("app_error")
        else:
            log.warning("app_error", detail=str(exc))
        return JSONResponse(
            status_code=status,
            content={
                "error": {
                    "type": type(exc).__name__,
                    "message": str(exc),
                }
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_error", path=request.url.path)
        return JSONResponse(
            status_code=500,
            content={"error": {"type": "InternalError", "message": "internal error"}},
        )
```

The unhandled-exception handler should never return the exception message to the client — it often leaks implementation detail.

## Retry semantics

Only retry operations that are idempotent or carry an idempotency key. Always cap attempts and use exponential backoff with jitter.

```python
import asyncio
import random
from typing import Awaitable, Callable, TypeVar

T = TypeVar("T")

RETRYABLE = (TimeoutError, RateLimitedError, ExternalServiceError)

async def retry_with_backoff(
    op: Callable[[], Awaitable[T]],
    *,
    attempts: int = 3,
    base: float = 0.5,
    cap: float = 10.0,
) -> T:
    last_exc: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return await op()
        except RETRYABLE as e:
            last_exc = e
            if attempt == attempts:
                break
            delay = min(cap, base * (2 ** (attempt - 1)))
            delay += random.uniform(0, delay * 0.2)  # jitter
            await asyncio.sleep(delay)
    assert last_exc is not None
    raise last_exc
```

Use `tenacity` for anything beyond this — it handles retry-on-result, conditional predicates, and logging hooks better than a hand-rolled loop.

Rules:

- Never retry 4xx client errors except 408, 425, 429. A 400 doesn't become a 200 by trying again.
- Respect `Retry-After` headers on 429 and 503.
- Add the retry count to the log context so you can see which requests actually retried.

## Context managers for resources

Resources that must be released (DB sessions, file handles, HTTP clients, locks) live behind a context manager — not `try/finally` boilerplate.

```python
from contextlib import asynccontextmanager, contextmanager

@contextmanager
def db_session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@asynccontextmanager
async def http_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(timeout=httpx.Timeout(10, connect=5)) as client:
        yield client
```

Tips:

- Commit-on-success, rollback-on-failure is the universal transaction shape. Put it in one helper so every use-case gets it.
- Use `contextlib.ExitStack` / `AsyncExitStack` when you need to build a variable number of contexts dynamically.
- `suppress` is useful for "ignore NotFoundError during cleanup" but do not sprinkle it in business logic.

## raise X from Y — preserve causation

Always chain with `from` when translating an exception. This gives you "During handling of the above exception, another exception occurred" in tracebacks, which is the difference between a 30-second debug and a 30-minute debug.

```python
try:
    response = await client.get(url)
    response.raise_for_status()
except httpx.HTTPError as e:
    raise ExternalServiceError(f"GET {url} failed") from e     # keeps cause
```

Use `from None` explicitly when you deliberately want to hide the original — rare, but legitimate when the original exception is internal/uninformative and would only confuse callers.

## Logging and exceptions

One log per exception, at the boundary where the exception is handled (not at every level that sees it). `logger.exception(...)` inside an `except` captures the traceback automatically.

```python
# GOOD: the API layer handler logs once with full context
# BAD: every layer logs "failed" with partial context — floods the log
```

## Anti-patterns

- `except Exception: pass` — silences bugs. If you genuinely have nothing to do, log and re-raise.
- `except:` with no class — catches `KeyboardInterrupt` and `SystemExit`. Always use `except Exception:` at minimum.
- Catching `BaseException` — same reason.
- Re-raising with `raise e` instead of bare `raise` — truncates the traceback at the re-raise line.
- Building HTTP response objects deep inside domain code — that couples the domain to the API layer.
- Invariant failure as exception type. Use `assert` or a typed error, not `ValueError("this should never happen")`.
- Exception classes whose `__init__` does work other than storing fields — breaks pickling and logging.

## Cross-references

- HTTP layer details: `python-saas-integration` skill.
- Logging format: `logging-structlog.md`.
- Security boundary errors: `security-baseline.md`.
- Anti-patterns summary: `anti-patterns.md`.
