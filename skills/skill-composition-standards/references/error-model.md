# Error Model Template

The canonical error-shape artifact produced by `api-design-first`. Consumed by frontend, mobile, SDK, and observability skills.

## Envelope

```json
{
  "code": "INVALID_INPUT",
  "message": "email is not a valid address",
  "details": {
    "field": "email",
    "value": "not-an-email"
  },
  "correlation_id": "req_01HXYZ...",
  "documentation_url": "https://docs.example.com/errors/INVALID_INPUT"
}
```

Required fields: `code`, `message`.
Recommended fields: `details`, `correlation_id`.
Optional: `documentation_url`.

## Code set

| HTTP | Code | Meaning | Retry safe? |
|---|---|---|---|
| 400 | `INVALID_INPUT` | request body failed validation | no |
| 401 | `UNAUTHORISED` | missing or invalid credentials | no (re-auth first) |
| 403 | `FORBIDDEN` | authenticated but not allowed | no |
| 404 | `NOT_FOUND` | resource does not exist | no |
| 409 | `CONFLICT` | state conflict (version, duplicate) | no — read + retry |
| 422 | `UNPROCESSABLE` | body is valid but business rules reject | no |
| 429 | `RATE_LIMITED` | rate limit exceeded; see Retry-After | yes with backoff |
| 500 | `INTERNAL` | server bug | yes with backoff |
| 502 | `UPSTREAM_ERROR` | downstream dependency failed | yes with backoff |
| 503 | `UNAVAILABLE` | service temporarily unavailable | yes with backoff |
| 504 | `UPSTREAM_TIMEOUT` | downstream timed out | yes with backoff |

## Rules

1. Every non-2xx response uses this envelope. No exceptions.
2. `code` is a stable identifier; its meaning never changes.
3. `message` is a one-line human-readable summary. It may change; clients must not parse it.
4. `details` is a structured object for programmatic use.
5. `correlation_id` is always included on 5xx; optional on 4xx.
6. Rate-limit responses include `Retry-After` header in seconds.

## Client-side handling rule

Clients match on `code`, not on `message` or HTTP status alone.

```ts
function handle(err: ApiError): void {
  switch (err.code) {
    case 'INVALID_INPUT':
      showValidationError(err.details);
      return;
    case 'UNAUTHORISED':
      signOutAndRedirect();
      return;
    case 'RATE_LIMITED':
      backoffAndRetry();
      return;
    case 'CONFLICT':
      reloadAndRetry();
      return;
    default:
      showGenericError(err.correlation_id);
  }
}
```

## Observability coupling

Every error response must be emitted as a structured log with:

- `error_code`
- `http_status`
- `correlation_id`
- `path`
- `method`
- `tenant_id` (if applicable)

`observability-monitoring` uses these fields to compute error-rate SLOs.

## Common failures

- **Stringly-typed error types** in message text — clients regex-parse and break.
- **Code overloaded with HTTP status** (`ERR_400`) — loses semantic meaning.
- **Missing correlation_id on 5xx** — support cannot trace reports.
- **Different envelopes per endpoint** — clients need per-endpoint handling.
- **No documented retry guidance** — clients either hammer or give up.
