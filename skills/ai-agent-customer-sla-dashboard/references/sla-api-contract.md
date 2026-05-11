# Public SLA API — Contract

A per-tenant, authenticated, rate-limited API that exposes the same numbers the dashboard shows. Pro+ read-only; Enterprise can subscribe to webhook events.

## Authentication

Bearer token, scoped to `sla:read`. Tokens are tenant-bound, expirable, revocable. Created from the admin console.

```
Authorization: Bearer <opaque-token>
```

Per-tenant rate limit: 60 RPM (Pro), 600 RPM (Business), negotiated (Enterprise). Rate limits enforced via `saas-rate-limiting-and-quotas`.

## Versioning

URL-pathed: `/v1/sla/...`. Breaking changes ship as `/v2/`. We deprecate with 12 months notice.

## Endpoints

### `GET /v1/sla/status`

Returns the current period status, identical to the dashboard widget payload (see `widget-embed.md` for the shape).

```http
GET /v1/sla/status
Accept: application/json

200 OK
{
  "sla_class": "class-A",
  "plan": "Pro",
  "features": [
    {
      "feature": "support_copilot",
      "metrics": {
        "resolution_rate_30d": {"value": 0.87, "floor": 0.85, "status": "met"},
        "intervention_rate_30d": {"value": 0.18, "ceiling": 0.25, "status": "met"},
        "irreversible_count_30d": {"value": 0, "target": 0, "status": "met"},
        "ttr_p95_seconds": {"value": 134, "target": 180, "status": "met"},
        "availability_month": {"value": 0.997, "target": 0.995, "status": "met"}
      },
      "exclusions_30d": [...]
    }
  ],
  "credits": {"pending_cents": 0, "last_invoice_cents": 750, "currency": "USD"},
  "generated_at": "2026-05-11T08:14:23Z"
}
```

### `GET /v1/sla/credits`

```http
GET /v1/sla/credits?from=2026-01-01&to=2026-05-11&page_size=50

200 OK
{
  "credits": [
    {
      "decision_id": "01HXYZ...",
      "sla_id": "pro.support_copilot.resolution_rate",
      "metric": "resolution_rate",
      "breach_window_start": "2026-04-17T00:00:00Z",
      "breach_window_end": "2026-04-23T23:59:59Z",
      "amount_cents": 750,
      "currency": "USD",
      "decided_at": "2026-04-24T08:14:23Z",
      "evidence_url": "https://app.example.com/sla/evidence/01HXYZ.../signed"
    }
  ],
  "page": {"has_more": false, "next_cursor": null}
}
```

### `GET /v1/sla/exclusions`

```http
GET /v1/sla/exclusions?from=2026-04-01&to=2026-05-11

200 OK
{
  "exclusions": [
    {
      "start": "2026-05-04T09:00:00Z",
      "end":   "2026-05-04T11:00:00Z",
      "kind":  "provider_outage_ack",
      "summary": "Anthropic upstream outage",
      "evidence_url": "https://app.example.com/status/2026-05-04",
      "features_affected": ["support_copilot","log_investigator"]
    }
  ]
}
```

### `GET /v1/sla/incidents`

```http
GET /v1/sla/incidents?from=2026-01-01

200 OK
{
  "incidents": [
    {
      "incident_id": "INC-2026-04-23-002",
      "started_at": "2026-04-23T14:02:00Z",
      "ended_at":   "2026-04-23T15:11:00Z",
      "severity": "sev2",
      "classes": ["model-regression"],
      "features_affected": ["support_copilot"],
      "rca_published_url": "https://app.example.com/postmortems/INC-2026-04-23-002"
    }
  ]
}
```

### `GET /v1/sla/evidence/{decision_id}`

Returns the signed evidence pack JSON. Tenant-scoped — 404 for non-owned decision_ids.

```http
GET /v1/sla/evidence/01HXYZ.../signed

200 OK
{
  "version": "2026-05.1",
  "tenant_id": <hashed>,
  "sla_id": "pro.support_copilot.resolution_rate",
  "metric": "resolution_rate",
  "window": {"start": "...", "end": "..."},
  "counter_snapshot": {...},
  "evidence_refs": ["trace://..."],
  "eligibility": {...},
  "credit": {...},
  "signature": "ed25519:..."
}
```

The `signature` lets the tenant cryptographically verify the bundle against the platform's public key, which is published at a stable URL.

## Webhooks (Enterprise)

Tenant configures a callback URL. We POST signed payloads on these events:

```
sla.breach.detected
sla.credit.issued
sla.exclusion.posted
sla.incident.opened
sla.incident.closed
refund.issued
```

Payload signed with HMAC-SHA256; secret rotated via admin console.

Retry policy: exponential backoff, up to 24h, then dead-letter with email to webhook owner.

```json
POST <webhook_url>
X-SLA-Signature: t=1715425000,v1=...
X-SLA-Event: sla.credit.issued

{
  "event": "sla.credit.issued",
  "tenant_id": <hashed>,
  "decision_id": "01HXYZ...",
  "sla_id": "pro.support_copilot.resolution_rate",
  "amount_cents": 750,
  "currency": "USD",
  "evidence_url": "https://app.example.com/sla/evidence/01HXYZ.../signed"
}
```

## Errors

| Code | Meaning |
|---|---|
| 401 | Missing / invalid token |
| 403 | Token does not have `sla:read` scope or tenant mismatch |
| 404 | Resource not found / not owned |
| 429 | Rate limit (with `Retry-After`) |
| 500 | Internal error (with `X-Request-Id`) |
| 503 | Temporarily unavailable (with `Retry-After`) |

Errors follow the platform's `api-error-handling` skill format.

## CORS

`/v1/sla/...` rejects CORS from browsers by default (server-to-server intent). For the JS widget SDK, a different domain serves the cached widget payload and has CORS configured for the tenant's allowed origins.

## Caching

`Cache-Control: private, max-age=300` on `/status`. `Cache-Control: private, max-age=60` on lists. Evidence packs are immutable; `Cache-Control: private, max-age=31536000`.

## Tenant Data Isolation

Every endpoint pre-filters by `tenant_id` from the token. No query parameter can override. Test coverage is mandatory: any handler that doesn't apply the tenant filter is a release blocker.

## OpenAPI

Spec lives at `docs/sla/sla-api.yaml`. Generated SDKs in TypeScript, Python, Go from CI.

## Anti-Patterns

- Token scopes that bundle `sla:read` with broader permissions. Use a single-purpose scope.
- Endpoints that accept `tenant_id` query param. Open invitation to cross-tenant leak.
- Webhook payloads with raw PII (task content). Use refs to signed bundles.
- No idempotency on webhook retries (consumer-side). Document the de-dupe key.
- API version "v1" never deprecated. Breaking changes inside v1 are betrayal.
