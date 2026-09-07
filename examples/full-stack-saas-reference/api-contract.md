# FieldOps Ledger API Contract Exemplar

Last verified: 2026-07-08
Standard/version: Skills Web Dev July 2026 API exemplar
Benchmark: Google API Improvement Proposal style resource discipline and Stripe-style idempotent API behavior.

## Scope

This exemplar defines the API shape for work orders, visits, evidence, posting events, and exports. It focuses on contract quality rather than implementation framework.

## Resource Model

| Resource | Example name | Notes |
|---|---|---|
| Tenant | `tenants/tnt_123` | Control-plane resource |
| Work order | `tenants/tnt_123/workOrders/wo_456` | Tenant-scoped operational resource |
| Visit | `tenants/tnt_123/workOrders/wo_456/visits/vst_789` | Child resource with status transitions |
| Evidence object | `tenants/tnt_123/evidence/ev_101` | Immutable blob metadata |
| Export job | `tenants/tnt_123/exportJobs/exp_202` | Long-running operation resource |

## Standard Methods

| Method | Route | Notes |
|---|---|---|
| Create work order | `POST /v1/tenants/{tenant}/workOrders` | Requires `Idempotency-Key` |
| Get work order | `GET /v1/{name=tenants/*/workOrders/*}` | Strongly consistent operational read |
| List work orders | `GET /v1/tenants/{tenant}/workOrders?max_page_size=50&page_token=...` | Opaque page token; response may return fewer than requested |
| Patch work order | `PATCH /v1/{work_order.name}` | Uses update mask and resource version |
| Cancel visit | `POST /v1/{visit.name}:cancel` | Custom method because it represents a domain transition |
| Validate completion | `POST /v1/{visit.name}:validateCompletion` | Dry-run validation without side effects |
| Start export | `POST /v1/tenants/{tenant}/exportJobs` | Returns export job resource |

## Idempotency and Retry

Create and transition methods require an `Idempotency-Key`. The server stores the key, request fingerprint, response status, and expiry. A repeated request with the same key and same fingerprint returns the first result. A repeated key with a different fingerprint returns `409 idempotency_key_reuse`.

Retry guidance:

| Status | Retry? | Client behavior |
|---|---|---|
| `408`, `429`, `500`, `502`, `503`, `504` | Yes | Retry with exponential backoff and same idempotency key where applicable |
| `400`, `401`, `403`, `404`, `409`, `422` | No automatic retry | Fix request, permissions, state, or conflict |

## Pagination and Filtering

List methods use `max_page_size` and opaque `page_token`. Clients must continue until `next_page_token` is absent. Filters use explicit supported fields only:

```text
status = "OPEN" AND scheduled_at >= "2026-07-01T00:00:00Z"
```

Unsupported filter fields return `400 unsupported_filter_field`; they do not silently fall back to broad scans.

## Compatibility Policy

- Additive response fields are compatible.
- Removing fields, changing field meaning, changing default sort, or changing pagination semantics is breaking.
- New required request fields are breaking unless introduced through validation warnings and versioned rollout.
- Field units are named in the field, for example `duration_seconds`, never only in prose.

## Error Model

```json
{
  "success": false,
  "error": {
    "code": "visit_conflict",
    "message": "Visit version 7 is no longer current.",
    "target": "visit.version",
    "request_id": "req_...",
    "retryable": false,
    "details": {
      "current_version": 8
    }
  }
}
```

## Worked Edge Case

A technician submits the same completed visit twice because the mobile network drops after the first response. Both requests carry the same `Idempotency-Key` and identical evidence hashes. The first request completes the visit and emits `PostingEvent(event_id=evt_1)`. The second request returns the original success response and does not emit another posting event.

## QA Checklist

- [ ] Every create/transition operation declares idempotency behavior.
- [ ] Every list method uses pagination from the first version.
- [ ] Every field with units names the unit.
- [ ] Every long-running export exposes status, cancellation, expiry, and manifest hash.
- [ ] Every breaking-change path names migration and compatibility behavior.

See also: `architecture.md`, `security-threat-model.md`, `templates/delivery-dod/evidence-pack.md`.
