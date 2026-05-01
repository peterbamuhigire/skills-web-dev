# SLO Template

Service Level Objectives per critical flow. Produced by `observability-monitoring`. Consumed by `reliability-engineering` and `deployment-release-engineering`.

## Template

```markdown
# SLOs — <service name>

**Owner:** <team>
**Window:** 28 rolling days (unless noted)

## SLO summary

| ID | Flow | SLI | Target | Window | Alert at |
|---|---|---|---|---|---|
| SLO-01 | CF-01 sign-in | availability (non-5xx / total) | 99.95% | 28d | burn-rate 2% in 1h OR 5% in 6h |
| SLO-02 | CF-01 sign-in | p95 latency | < 500ms | 28d | sustained breach for 10m |
| SLO-03 | CF-03 checkout | availability | 99.95% | 28d | burn-rate 2% in 1h |
| SLO-04 | CF-03 checkout | p99 latency | < 5s | 28d | sustained breach for 15m |
| ... | ... | ... | ... | ... | ... |

## Per-SLO detail

### SLO-01 — Sign-in availability

- **SLI:** proportion of /auth/login requests returning non-5xx within 5s
- **Target:** 99.95% over 28 rolling days
- **Error budget:** 0.05% = ~20 minutes per 28d
- **Measurement:**
  - numerator: count of responses where status < 500 and duration < 5s
  - denominator: count of all responses
  - source: Prometheus + `http_request_duration_seconds` histogram
- **Alerting:**
  - page: burn-rate > 14.4 over 1h (2% budget burn) — severe
  - page: burn-rate > 6 over 6h (5% budget burn) — sustained
  - ticket: burn-rate > 1 over 3d — drift
- **Runbook:** `runbooks/sign-in-availability.md`

### SLO-02 — Sign-in p95 latency

- **SLI:** p95 of /auth/login duration, excluding 5xx
- **Target:** p95 < 500ms over 28 rolling days
- **Measurement:** histogram_quantile(0.95, rate(...))
- **Alerting:**
  - ticket: sustained breach > 600ms for 10m
  - ticket: sustained breach > 1s for 2m
- **Runbook:** `runbooks/sign-in-latency.md`

...
```

## Rules

1. Every critical flow from the flow inventory has at least one SLO.
2. Availability SLOs use a proportion (non-5xx / total), not a raw count.
3. Latency SLOs specify the percentile and window.
4. Every SLO has a linked runbook; alerts point at the runbook.
5. Every SLO has an error budget expressed in time.
6. Alerting uses burn-rate (multi-window multi-burn-rate where possible), not raw threshold.

## Burn-rate cheatsheet

For a 28-day window and an X% availability target:

| Burn-rate × budget | Budget burned in 1h | Page window |
|---|---|---|
| 14.4 × | 2% | 1 hour |
| 6 × | 5% | 6 hours |
| 1 × | 10% | 3 days |

Two-window alerts reduce false positives: alert only when both a fast-burn window AND a slow-burn window breach.

## Common failures

- **No error budget stated.** Without a budget, no basis to trade off reliability work vs features.
- **Threshold-based alerts instead of burn-rate.** Flaps on minor noise; misses slow burns.
- **Latency SLO without percentile specified.** "Fast" is not a target.
- **SLO on every endpoint.** Only critical flows deserve SLOs. Others get ad-hoc metrics.
- **Runbook link missing.** On-call is paged with no guidance.
- **SLIs measured client-side only.** Server-side SLI is authoritative; client-side adds colour.
