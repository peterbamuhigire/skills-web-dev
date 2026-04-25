# ETL From External APIs

Stripe, payment gateways, bank feeds, tax portals, government APIs. Every external API needs pagination, rate limiting, auth refresh, retries, and a correlation ID.

## Stripe — cursor-based incremental sync

Stripe paginates with `starting_after` (object ID cursor). It also exposes `created[gte]` and `created[lte]` filters. Use both together: window by `created`, paginate by cursor.

```python
from datetime import datetime, UTC, timedelta
from uuid import uuid4
import structlog
from stripe import StripeClient
from pydantic import BaseModel, Field, ValidationError
from typing import Literal

log = structlog.get_logger()

class StripeInvoice(BaseModel):
    id: str = Field(pattern=r"^in_[A-Za-z0-9]+$")
    customer: str
    amount_due: int = Field(ge=0)
    currency: str = Field(pattern=r"^[a-z]{3}$")
    status: Literal["draft", "open", "paid", "uncollectible", "void"]
    created: int
    model_config = {"extra": "ignore"}

def sync_stripe_invoices(tenant_id: int) -> SyncResult:
    run_id = uuid4()
    logger = log.bind(tenant_id=tenant_id, pipeline="stripe.invoices", run_id=str(run_id))
    watermark = load_watermark(tenant_id, "stripe.invoices") or datetime(1970, 1, 1, tzinfo=UTC)
    client = StripeClient(api_key=secrets.for_tenant(tenant_id).stripe_api_key)

    starting_after: str | None = None
    total = ok = failed = 0
    last_created = int(watermark.timestamp())

    while True:
        params = {
            "created": {"gte": int(watermark.timestamp())},
            "limit": 100,
        }
        if starting_after:
            params["starting_after"] = starting_after

        page = client.invoices.list(params)
        if not page.data:
            break

        for raw in page.data:
            total += 1
            try:
                model = StripeInvoice.model_validate(raw)
                upsert_invoice(tenant_id, model)
                ok += 1
                last_created = max(last_created, model.created)
            except ValidationError as e:
                send_to_dlq(tenant_id, "stripe.invoices", raw.id, raw, str(e))
                failed += 1

        if not page.has_more:
            break
        starting_after = page.data[-1].id

    save_watermark(tenant_id, "stripe.invoices", datetime.fromtimestamp(last_created, UTC))
    logger.info("stripe_sync_done", total=total, ok=ok, failed=failed)
    return SyncResult(total=total, ok=ok, failed=failed)
```

Key rules:

- Advance the watermark from the **last successfully loaded** `created`, not from `datetime.now()`. Protects against clock skew.
- Use `has_more` to stop. Do not rely on page size alone.
- Use one Stripe client per tenant. Sharing a client between tenants is a credential-bleed bug waiting to happen.

## Generic REST paginated sync

For bank feeds, payment gateways, and tax portals that are REST + JSON. Three pagination styles dominate: `page/limit`, `offset/limit`, `next_cursor`. Prefer cursor.

```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type

class RateLimitError(Exception): pass
class TransientError(Exception): pass

@retry(
    stop=stop_after_attempt(6),
    wait=wait_exponential_jitter(initial=1, max=60),
    retry=retry_if_exception_type((RateLimitError, TransientError, httpx.ConnectError)),
    reraise=True,
)
def fetch_page(client: httpx.Client, url: str, params: dict) -> dict:
    r = client.get(url, params=params, timeout=30.0)
    if r.status_code == 429:
        # Respect Retry-After if present
        raise RateLimitError(r.headers.get("Retry-After", "1"))
    if 500 <= r.status_code < 600:
        raise TransientError(str(r.status_code))
    r.raise_for_status()
    return r.json()

def sync_paginated(tenant_id: int, endpoint: str) -> SyncResult:
    run_id = str(uuid4())
    correlation_id = f"{tenant_id}:{run_id}"
    headers = {
        "Authorization": f"Bearer {current_access_token(tenant_id)}",
        "X-Correlation-ID": correlation_id,
    }
    cursor: str | None = None
    ok = failed = total = 0
    with httpx.Client(base_url="https://api.gateway.example", headers=headers) as client:
        while True:
            params = {"limit": 200}
            if cursor:
                params["cursor"] = cursor
            data = fetch_page(client, endpoint, params)
            for raw in data["items"]:
                total += 1
                try:
                    process_record(tenant_id, raw)
                    ok += 1
                except ValidationError as e:
                    send_to_dlq(tenant_id, endpoint, raw.get("id"), raw, str(e))
                    failed += 1
            cursor = data.get("next_cursor")
            if not cursor:
                break
    return SyncResult(total=total, ok=ok, failed=failed)
```

Rules:

- Always set a correlation ID in the request header and in every log line for the run. Makes tracing across our server and the vendor's server viable when they help debug.
- Set read and connect timeouts explicitly (30s read is a reasonable default).
- Retry only idempotent methods (`GET`, `PUT`, `DELETE`). **Never auto-retry `POST`** unless the API supports idempotency keys.

## Bank feed formats

Three formats dominate:

- **OFX / QFX** (Open Financial Exchange). SGML-style XML-ish. Use the `ofxparse` library. Common for Western retail banks.
- **MT940** (SWIFT). Line-oriented, positional, fixed-length tag-based. Use `mt-940` library. Common for European corporate banking.
- **CSV** (proprietary). Most East African banks. Different layout per bank. Need a per-bank adapter.

```python
# OFX example
from ofxparse import OfxParser

with open(path, "rb") as f:
    ofx = OfxParser.parse(f)

for txn in ofx.account.statement.transactions:
    yield BankTransaction(
        tenant_id=tenant_id,
        account_id=ofx.account.account_id,
        external_id=txn.id,              # FITID; unique per account
        posted_at=txn.date,
        amount=Decimal(str(txn.amount)),
        currency=ofx.account.statement.currency,
        memo=txn.memo,
    )
```

Rules:

- Bank files are append-only history. Use the bank's `FITID` (OFX) or equivalent natural key for idempotency.
- Handle duplicate downloads — the same file may be fetched twice. Dedupe by `(tenant_id, account_id, external_id)`.
- Keep the raw file. Store a SHA-256 of the file + a pointer to blob storage. Regulatory audit will want it.

## Rate limiting

Per-tenant token bucket stored in Redis. Prevents one tenant exhausting an API quota for everyone.

```python
import time
import redis

class TokenBucket:
    def __init__(self, r: redis.Redis, key: str, capacity: int, refill_rate: float):
        self.r = r
        self.key = key
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second

    def try_acquire(self, tokens: int = 1) -> bool:
        # Lua script for atomic refill + take
        script = """
        local bucket = redis.call('HMGET', KEYS[1], 'tokens', 'ts')
        local now = tonumber(ARGV[1])
        local cap = tonumber(ARGV[2])
        local rate = tonumber(ARGV[3])
        local need = tonumber(ARGV[4])
        local tokens = tonumber(bucket[1]) or cap
        local ts = tonumber(bucket[2]) or now
        tokens = math.min(cap, tokens + (now - ts) * rate)
        if tokens < need then
          redis.call('HMSET', KEYS[1], 'tokens', tokens, 'ts', now)
          redis.call('EXPIRE', KEYS[1], 3600)
          return 0
        end
        tokens = tokens - need
        redis.call('HMSET', KEYS[1], 'tokens', tokens, 'ts', now)
        redis.call('EXPIRE', KEYS[1], 3600)
        return 1
        """
        return bool(self.r.eval(script, 1, self.key, time.time(), self.capacity, self.refill_rate, tokens))

def bucket_for(tenant_id: int, api: str) -> TokenBucket:
    return TokenBucket(redis_conn, f"rate:{api}:{tenant_id}", capacity=100, refill_rate=5)
```

If `try_acquire` returns `False`, sleep for `1 / rate` and retry. Log rate-limit waits — they are a signal of either a noisy tenant or an undersized quota.

## Auth refresh (OAuth 2)

Never refresh tokens inside the retry loop. Separate the concerns: a `TokenManager` that owns refresh; the HTTP client asks for a token and retries **once** on 401.

```python
from dataclasses import dataclass
from datetime import datetime, UTC, timedelta
import threading

@dataclass
class Token:
    access: str
    expires_at: datetime
    refresh: str

class TokenManager:
    def __init__(self, tenant_id: int):
        self.tenant_id = tenant_id
        self._lock = threading.Lock()
        self._token: Token | None = None

    def current(self) -> str:
        with self._lock:
            if not self._token or self._token.expires_at <= datetime.now(UTC) + timedelta(seconds=60):
                self._refresh()
            return self._token.access

    def _refresh(self) -> None:
        stored = secrets.get(self.tenant_id, "oauth")
        resp = httpx.post(TOKEN_URL, data={
            "grant_type": "refresh_token",
            "refresh_token": stored.refresh,
            "client_id": stored.client_id,
            "client_secret": stored.client_secret,
        }, timeout=15.0)
        resp.raise_for_status()
        body = resp.json()
        self._token = Token(
            access=body["access_token"],
            refresh=body.get("refresh_token", stored.refresh),
            expires_at=datetime.now(UTC) + timedelta(seconds=body["expires_in"]),
        )
        secrets.put(self.tenant_id, "oauth", self._token)
```

On `401`, call `TokenManager.current()` to force a refresh and retry the request once. If it 401s again, the refresh token is dead — fail the run and alert, do not loop.

## Exponential backoff with jitter

Use `tenacity`. The jitter is not optional — without it, retries thunder onto a recovering server.

```python
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

@retry(
    stop=stop_after_attempt(6),
    wait=wait_exponential_jitter(initial=1, max=60, jitter=2),
)
def call_api(...): ...
```

Total wait for 6 attempts with `initial=1, max=60`: ~1 + 2 + 4 + 8 + 16 + 32 = ~63s plus jitter. Past that, fail the run.

## Correlation IDs

Every outbound call gets `X-Correlation-ID: {tenant_id}:{run_id}:{seq}`. Log it on every log line for that request. Persist it in the DLQ record. When a vendor escalates a bug, correlation IDs save hours.

## Anti-patterns

- One shared HTTP client with hard-coded auth for all tenants.
- Retrying POSTs without idempotency keys.
- No `timeout=` on the request — will hang forever on network issues.
- Refreshing tokens inside the retry decorator — infinite refresh loops.
- Rate limiting in app memory instead of Redis — fails in a multi-worker deployment.
- Saving watermark from `datetime.now()` instead of the last record's timestamp.
