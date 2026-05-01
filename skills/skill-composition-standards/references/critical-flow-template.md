# Critical-Flow Template

The list of user journeys (or system flows) the system must complete reliably. Produced by `system-architecture-design`, consumed by `observability-monitoring` (to set SLOs), `advanced-testing-strategy` (to scope E2E tests), and `reliability-engineering` (to prioritise failure mitigation).

## Template

```markdown
# Critical Flows — <system name>

**As of:** YYYY-MM-DD

## Flow inventory

| ID | Flow | Trigger | Outcome | Owner |
|---|---|---|---|---|
| CF-01 | User signs in | user submits credentials | valid session cookie + redirect | identity |
| CF-02 | User adds item to cart | user clicks Add | cart row persisted, count updated | commerce |
| CF-03 | User checks out | user clicks Place Order | order created, payment authorised, confirmation sent | checkout |
| CF-04 | Order fulfilled | warehouse scans parcel | order status = shipped, tracking URL visible | fulfilment |
| ... | ... | ... | ... | ... |

## Targets per flow

| ID | Latency p50 | Latency p95 | Latency p99 | Availability | Peak QPS | Notes |
|---|---|---|---|---|---|---|
| CF-01 | 200ms | 500ms | 1s | 99.95% | 50 | auth is on the critical path for all others |
| CF-02 | 100ms | 300ms | 800ms | 99.9% | 200 | read-heavy; hits cache |
| CF-03 | 1s | 3s | 5s | 99.95% | 10 | involves external payment call |
| CF-04 | 300ms | 800ms | 2s | 99.5% | 5 | tolerant to brief unavailability |
| ... | ... | ... | ... | ... | ... | ... |

## Failure impact

| ID | Impact if fully down | Tolerance (minutes before P1) | Degradation allowed |
|---|---|---|---|
| CF-01 | users cannot sign in | 5 | no |
| CF-02 | users cannot add to cart | 15 | yes — show cached state |
| CF-03 | users cannot buy | 2 | no |
| CF-04 | warehouse blocked | 30 | yes — batch process later |

## Non-critical flows

<List flows that exist but are not on the critical list, so observability and testing know not to prioritise them.>

- Admin reports generation
- Retrospective analytics exports
- ...

## Revision log

| Date | Change | Author |
|---|---|---|
| YYYY-MM-DD | initial | ... |
```

## Rules

1. Every critical flow has measurable latency and availability targets.
2. Every flow has an owning team.
3. Tolerance (time before P1) forces the team to set realistic severity.
4. Non-critical flows are listed explicitly so nothing accidentally falls off the radar.

## Common failures

- **Every flow is critical.** If everything is critical, nothing is. Typical healthy systems have 3–10 truly critical flows.
- **Targets without measurement.** Targets must be observable (SLIs must exist or be planned).
- **Owner = "ops".** That is not an owner. Name the product team.
- **Missing peak QPS.** Capacity planning and load-test design depend on it.
