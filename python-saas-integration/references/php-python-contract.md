# PHP to Python Contract

The wire contract both sides implement. PHP is the caller for sidecar requests and the producer for worker jobs. Python validates and honours the contract on both paths.

## Headers (every request)

| Header | Purpose | Required |
|---|---|---|
| `X-Internal-Signature` | HMAC-SHA256 of canonical string | yes |
| `X-Internal-Timestamp` | Unix seconds when the signature was produced | yes |
| `X-Tenant-Id` | Tenant scope, bound into the signature | yes |
| `X-Correlation-Id` | UUID v4 propagated from PHP request | yes |
| `X-Idempotency-Key` | Client-chosen key for mutating calls | when mutating |
| `X-Api-Version` | Contract version, e.g. `v1` | yes |
| `Content-Type` | `application/json` | yes |

## HMAC scheme

Canonical string:

```text
{timestamp}\n{method}\n{path}\n{tenant_id}\n{sha256(body_bytes)}
```

Always lowercase the method and the hex digest. Include the query string in `path` exactly as sent (percent-encoded, not re-encoded).

### PHP signer

```php
<?php
final class InternalSigner
{
    public function __construct(private readonly string $secret) {}

    public function sign(
        string $method,
        string $path,
        string $tenantId,
        string $body,
    ): array {
        $timestamp = (string) time();
        $bodyHash = hash('sha256', $body);
        $canonical = implode("\n", [
            $timestamp,
            strtolower($method),
            $path,
            $tenantId,
            $bodyHash,
        ]);
        $signature = hash_hmac('sha256', $canonical, $this->secret);
        return [
            'X-Internal-Timestamp' => $timestamp,
            'X-Internal-Signature' => $signature,
            'X-Tenant-Id'          => $tenantId,
        ];
    }
}
```

### Python verifier

```python
# src/service_name/security.py
import hmac, hashlib, time
from fastapi import HTTPException, Request, status
from .settings import settings

SKEW_SECONDS = 60

async def verify_hmac(signature: str, timestamp: str, request: Request) -> None:
    try:
        ts = int(timestamp)
    except ValueError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "bad_timestamp")

    if abs(time.time() - ts) > SKEW_SECONDS:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "timestamp_skew")

    body = await request.body()
    body_hash = hashlib.sha256(body).hexdigest()
    tenant_id = request.headers.get("x-tenant-id", "")
    canonical = "\n".join([
        timestamp,
        request.method.lower(),
        request.url.path + (f"?{request.url.query}" if request.url.query else ""),
        tenant_id,
        body_hash,
    ])
    expected = hmac.new(
        settings.internal_secret.encode(),
        canonical.encode(),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "bad_signature")
```

Notes:

- Always use `hmac.compare_digest` / `hash_equals` — never `==`. Prevents timing attacks.
- Read the body once; cache it. FastAPI's `Request.body()` is cached after the first read.
- The tenant is part of the signed payload. A leaked secret for tenant A cannot be replayed against tenant B.
- Rotate secrets by supporting two secrets during a rollover window: try primary, then secondary.

## Response envelope

Every sidecar response — success or error, 2xx or 4xx — returns the same shape.

### Success

```json
{
  "ok": true,
  "data": { "...": "..." },
  "meta": { "version": "v1", "generated_at": "2026-04-15T09:30:00Z" }
}
```

### Error

```json
{
  "ok": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "period_start must be before period_end",
    "details": { "field": "period_start" }
  },
  "meta": { "version": "v1", "correlation_id": "..." }
}
```

Worker results reuse the same shape. Store `result` in Redis / DB using this envelope so PHP has one parser.

## Error code catalog

Codes are stable contract items. Never reuse, never rename. PHP switches on `code`, not on `message`.

| Code | HTTP | Meaning | PHP behaviour |
|---|---|---|---|
| `INVALID_INPUT` | 400 | Request failed validation | Show validation error |
| `UNAUTHENTICATED` | 401 | HMAC check failed | Page on-call; likely config drift |
| `FORBIDDEN_TENANT` | 403 | Tenant mismatch between header and payload | Log + 500 to user |
| `NOT_FOUND` | 404 | Entity not found | Show empty/404 |
| `CONFLICT` | 409 | Idempotency collision or state conflict | Fetch prior result |
| `PAYLOAD_TOO_LARGE` | 413 | Body > limit | Suggest async path |
| `UNPROCESSABLE` | 422 | Semantic validation failed | Show validation |
| `RATE_LIMITED` | 429 | Per-tenant limit hit | Back off per `Retry-After` |
| `DEPENDENCY_DOWN` | 503 | DB/Redis/upstream unreachable | Circuit breaker open, degrade |
| `INTERNAL_ERROR` | 500 | Unhandled | Degrade + alert |
| `TIMEOUT` | 504 | Upstream timed out | Degrade + alert |

Job-only codes (set in `result.error.code`):

- `POISON_MESSAGE` — the job payload cannot be processed ever. Routed to DLQ.
- `TRANSIENT_DEPENDENCY` — retryable. The worker retries with backoff before surfacing it.
- `CANCELLED` — caller cancelled before execution (Celery revoke).

## Idempotency

Every mutating sidecar call and every worker job accepts `X-Idempotency-Key` (header) or `idempotency_key` (payload field). Rules:

1. Client generates a UUID v4 per logical operation, stable across retries.
2. Server stores `(tenant_id, idempotency_key) -> result` in Redis for 24 hours.
3. On replay within TTL, return the stored result. Do not re-execute.
4. On replay *outside* TTL, return `409 CONFLICT` with code `IDEMPOTENCY_EXPIRED` — safer than silently re-running a potentially charged operation.

```python
# src/service_name/idempotency.py
from typing import Any
import json, redis.asyncio as redis

class IdempotencyStore:
    TTL = 24 * 3600

    def __init__(self, r: redis.Redis):
        self.r = r

    def _key(self, tenant_id: str, idem_key: str) -> str:
        return f"idem:{tenant_id}:{idem_key}"

    async def get(self, tenant_id: str, idem_key: str) -> Any | None:
        raw = await self.r.get(self._key(tenant_id, idem_key))
        return json.loads(raw) if raw else None

    async def put(self, tenant_id: str, idem_key: str, envelope: dict) -> None:
        await self.r.set(
            self._key(tenant_id, idem_key),
            json.dumps(envelope),
            ex=self.TTL,
            nx=True,
        )
```

Store only the envelope, never the raw entity. Envelope is already small and immutable.

## Versioning

- Path-based: `/v1/...`, `/v2/...`. Breaking changes move to a new path.
- `X-Api-Version` header is echoed back in `meta.version`. PHP asserts the echoed version matches what it asked for; mismatch means misconfigured proxy or mixed deployment.
- **Additive rule.** New optional fields in requests and responses do not break callers. Making a field required, renaming it, or changing its type is a breaking change that needs a new major version.
- Run two versions in parallel during migration. Log `v1_deprecated_hit_total` so you can see who still calls the old path.

## 429 and Retry-After

When the sidecar rate-limits (per tenant, per endpoint, per minute), it returns:

```text
HTTP/1.1 429 Too Many Requests
Retry-After: 12
Content-Type: application/json

{"ok": false, "error": {"code": "RATE_LIMITED", "message": "..."}}
```

PHP client honours `Retry-After` — it is seconds, not milliseconds. Randomise by ±20% before sleeping to avoid thundering herds.

## Worker job envelope

When PHP enqueues a job, the payload on Redis is:

```json
{
  "job": "reports.build_sales_report",
  "version": "v1",
  "tenant_id": "t_01HF...",
  "idempotency_key": "2026-04-15-sales-report-daily",
  "correlation_id": "uuid",
  "enqueued_at": "2026-04-15T09:30:00Z",
  "params": { "period_start": "...", "period_end": "..." }
}
```

The job signature in Python accepts only the fields it needs plus the three envelope fields (`tenant_id`, `idempotency_key`, `correlation_id`). Extra fields are ignored — forward-compatible.

## Contract tests

Both sides run the same suite against recorded fixtures:

- `tests/contract/fixtures/*.json` — canonical request/response pairs.
- PHP CI runs a fixture sender against the Python service in docker-compose.
- Python CI runs a recorded PHP client against the live sidecar.

A green contract test means the wire is intact. A red one fails the PR on whichever side introduced the drift.
