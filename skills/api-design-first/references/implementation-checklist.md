# Implementation Checklist and Observability Notes

Back to [../SKILL.md](../SKILL.md).

Pre-merge checklist for every new or modified API, plus the observability contract this skill hands to `observability-monitoring`.

## Implementation checklist

- [ ] OpenAPI spec written before code
- [ ] Consumers, latency budget, and trust boundaries defined
- [ ] URL: plural nouns, versioned (`/api/v1/`), no verbs
- [ ] Response envelope: `{success, data, meta}` / `{success, error{code,message,documentation_url}}`
- [ ] Tenant isolation: `franchise_id` (or equivalent) from auth token, never from request
- [ ] 404 for wrong-tenant records (not 403 — prevents enumeration)
- [ ] Security headers on every response (HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy)
- [ ] CORS: specific origins only — never wildcard with credentials
- [ ] ETags on cacheable resources; `304 Not Modified` on match
- [ ] Rate-limiting headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After`
- [ ] Pagination: `page`, `per_page` (max 100), `meta.total`, `meta.last_page`
- [ ] API keys hashed (SHA-256) — raw key never stored
- [ ] JWT: validate `iss`, `aud`, `exp`; short-lived tokens; no secrets in payload
- [ ] Versioning: URL path, N-1 support, `Deprecation` + `Sunset` headers on sunset
- [ ] HATEOAS `_links` on resources (only permitted actions)
- [ ] Breaking change? Bump major version — never modify existing version
- [ ] `/health` endpoint for load balancer / Kubernetes probes
- [ ] Middleware order: Logging -> Recovery -> CORS -> Auth -> Rate Limit -> Handler
- [ ] Idempotency strategy defined for retries on critical POST endpoints
- [ ] Audit events emitted for security-sensitive or financially material actions
- [ ] Observability fields declared per endpoint (see below)

## Observability notes (handed to observability-monitoring)

For every endpoint the OpenAPI spec must pin the following, typically as `x-observability` extensions:

| Field                | Meaning                                                   | Example                                        |
|----------------------|-----------------------------------------------------------|------------------------------------------------|
| `span_name`          | Tracing span name used in APM                             | `POST /invoices`                               |
| `slo_class`          | Critical-flow bucket from architecture                    | `critical-write`, `critical-read`, `standard`  |
| `latency_budget_ms`  | P99 target for this endpoint                              | `250`                                          |
| `error_budget_burn`  | Which error codes count against availability vs ignored   | `>=500 counts; 4xx ignored`                    |
| `log_fields`         | Fields required on every structured log line              | `request_id, tenant_id, user_id, endpoint_id`  |
| `audit_event`        | Name of audit event emitted, if any                       | `invoice.created`                              |
| `pii_redaction`      | Fields redacted from logs                                 | `email, phone, payload.payment.card_number`    |
| `metrics`            | Custom metrics emitted on this endpoint                   | `invoice_total_amount{currency=}`              |

`observability-monitoring` consumes this table to build:

- alerts on SLO burn rates
- dashboards segmented by `slo_class`
- per-service runbooks referencing `audit_event` names

## Hand-offs to other skills

| Artifact produced           | Downstream consumer                             | What they do with it                                                       |
|-----------------------------|-------------------------------------------------|----------------------------------------------------------------------------|
| OpenAPI contract            | frontend, mobile, SDK skills                    | generate typed clients, mock servers, contract tests                       |
| Error model                 | frontend, mobile, `advanced-testing-strategy`   | unify error UX, build contract tests                                       |
| Auth model                  | `vibe-security-skill`, `mobile-rbac`, `ios-rbac`| feed threat model, wire client-side permission gates                       |
| Idempotency map             | `reliability-engineering`, `stripe-payments`    | drive retry/backoff logic, prove safety for payment replays                |
| Observability notes         | `observability-monitoring`                      | build SLOs, alerts, dashboards, runbooks                                   |
