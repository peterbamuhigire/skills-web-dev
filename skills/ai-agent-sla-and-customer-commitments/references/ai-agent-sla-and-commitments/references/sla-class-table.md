# SLA Class Table — Per Tier, Per Feature

This is the canonical reference for SLA tiers. Treat numbers as **defaults**; Enterprise contracts override per-tenant in `tenant_sla_overrides`.

## Tier Summary

| Tier | SLA Class | Credit eligible | Public dashboard | Bespoke overrides |
|---|---|---|---|---|
| Free | none | no | display-only | no |
| Starter | class-B | no | full | no |
| Pro | class-A | yes (capped) | full | no |
| Business | class-AA | yes (capped, higher) | full | optional |
| Enterprise | bespoke | yes (per contract) | full + API + custom | yes |

## Per-Feature Floors and Ceilings (defaults)

### support_copilot (autonomous customer-support agent)

| Metric | Free | Starter (B) | Pro (A) | Business (AA) | Enterprise |
|---|---|---|---|---|---|
| Resolution rate (30d) | — | ≥ 70% display | ≥ 85% credit-bound | ≥ 90% credit-bound | negotiated, typically ≥ 92% |
| Intervention rate ceiling | — | ≤ 40% display | ≤ 25% credit-bound | ≤ 15% credit-bound | negotiated |
| Irreversible off-script | — | 0 / 30d | 0 / 30d (firm) | 0 / 30d (firm) | 0 / 30d (firm) |
| Time-to-resolve p95 | — | ≤ 5 min display | ≤ 3 min display | ≤ 2 min credit-bound | negotiated |
| Availability (start success) | — | 99.0% | 99.5% | 99.9% | 99.95% |
| Kill-switch latency | n/a | n/a | ≤ 60s | ≤ 60s | ≤ 30s |
| Approval notify p95 | n/a | n/a | ≤ 60s | ≤ 30s | ≤ 15s |

### log_investigator (multi-step diagnostic agent)

| Metric | Free | Starter (B) | Pro (A) | Business (AA) | Enterprise |
|---|---|---|---|---|---|
| Resolution rate (30d) | n/a | n/a | ≥ 70% display | ≥ 80% credit-bound | ≥ 85% credit-bound |
| Intervention rate ceiling | n/a | n/a | n/a (high-intervention by design) | ≤ 40% display | negotiated |
| Irreversible off-script | n/a | n/a | 0 / 30d (firm) | 0 / 30d (firm) | 0 / 30d (firm) |
| Time-to-resolve p95 | n/a | n/a | ≤ 30 min display | ≤ 15 min credit-bound | negotiated |
| Availability | n/a | n/a | 99.0% | 99.5% | 99.9% |

Difficult features have lower floors. A 90% resolution rate on a log investigator is exceptional; on a support copilot it is table-stakes.

### code_change_agent (writes/edits code, opens PRs)

| Metric | Pro (A) | Business (AA) | Enterprise |
|---|---|---|---|
| Resolution rate (30d, defined as PR-merged-without-revert) | ≥ 50% display | ≥ 60% credit-bound | ≥ 65% |
| Intervention rate ceiling | n/a (HITL required) | ≤ 80% display | negotiated |
| Irreversible off-script | 0 / 30d (firm) | 0 / 30d (firm) | 0 / 30d (firm) |
| Revert-within-7-days rate | display | ≤ 15% display | ≤ 10% credit-bound |
| Availability | 99.0% | 99.5% | 99.9% |

Notice resolution-rate definition shifts per feature. For code-change agents, "resolved" means "PR merged and not reverted within 7 days" — eval-gated.

## Credit Formulas (defaults)

```yaml
class-A (Pro):
  resolution_rate_breach: 0.05 * monthly_fee per breach_event
  availability_breach: 0.05 * monthly_fee per 0.1pp below floor
  irreversible_offscript: 1.0 * monthly_fee per incident
  cap_per_month: 0.30 * monthly_fee
  
class-AA (Business):
  resolution_rate_breach: 0.10 * monthly_fee per breach_event
  ttr_p95_breach: 0.05 * monthly_fee per breach_event
  availability_breach: 0.10 * monthly_fee per 0.1pp below floor
  irreversible_offscript: 1.5 * monthly_fee per incident (no cap)
  cap_per_month: 0.50 * monthly_fee (except irreversible)
  
bespoke (Enterprise):
  per contract; stored in tenant_sla_overrides
```

Notes:
- `breach_event` is one continuous breach window, not per-day. A 14-day breach is one event.
- Irreversible incidents never sit under the cap. They are operationally severe and a refund signal.
- Credits are issued as Stripe credit notes, not cash refunds (see `ai-agent-sla-credit-automation`).

## Window Definitions

| Window | Definition |
|---|---|
| 30d rolling | last 30 calendar days from time of evaluation |
| calendar month | from 00:00 UTC on day 1 to 23:59:59 UTC on last day |
| 7 consecutive days | a breach must persist for 7 day-buckets in a row to qualify |

Most metrics use rolling 30d. Availability uses calendar month for Stripe-period alignment.

## Exclusions Applied per Tier

| Exclusion | Pro | Business | Enterprise |
|---|---|---|---|
| force_majeure | yes | yes | yes (with 24h notice requirement) |
| provider_outage_ack | yes | yes | yes (must show in our status page) |
| customer_caused | yes | yes | yes |
| scheduled_maintenance | yes (auto-applied) | yes | yes (negotiated window) |
| beta_feature | yes | yes | yes (unless GA'd in contract) |
| abuse_protection_engaged | yes | yes | yes |

## Default Public-Page Snippet (handed to proposal engine)

```markdown
Pro SLA (class-A):
- We commit to a resolution rate of at least 85% over any rolling 30-day window for each agent feature you use.
- We commit to zero off-script irreversible actions over any rolling 30-day window.
- We commit to 99.5% availability for agent feature task creation each calendar month.
- If we miss any of these commitments, you receive an automatic service credit on your next invoice.
- Credits are 5% of your monthly fee per breach event, capped at 30% per month, applied automatically without you needing to claim.
- Exclusions: force majeure, acknowledged upstream provider outages, customer configuration errors, scheduled maintenance announced ≥ 7 days in advance.
```

The exact contract wording is owned by the proposal engine.
