> Consolidated from skills/ai-agent-customer-sla-dashboard/SKILL.md into ai-agent-sla-and-customer-commitments on 2026-05-13. Load this through skills/ai-agent-sla-and-customer-commitments/SKILL.md, not as an active skill entrypoint.

# AI Agent Customer SLA Dashboard
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Designing the **per-tenant SLA panel** in the customer dashboard.
- Building the **embeddable widget** that tenants can drop into their own admin app (B2B trust signal).
- Designing the **public SLA API** (`GET /v1/sla/...`) for Enterprise tenants who want to scrape into their own observability.
- Wiring the **SLA-credit balance** display so customers see issued credits before the invoice arrives.
- Coordinating with `ai-agent-sla-and-commitments` (commitments shown), `ai-agent-task-success-tracking` (verdict numbers), `ai-agent-sla-credit-automation` (credit balance).

## Do Not Use When

- The task is the internal ops dashboard — `saas-admin-backoffice-tooling` plus `ai-agent-observability-and-replay`.
- The task is the SLA commitment definition itself — `ai-agent-sla-and-commitments`.
- The task is the metric pipeline — `ai-agent-task-success-tracking`.
- The task is generic SaaS analytics dashboards — `ai-analytics-dashboards`.

## Required Inputs

- Per-tenant resolution rollups (`agent_resolution_30d`, `agent_resolution_daily`).
- SLA-class binding per tenant (`tenant.sla_class`, `tenant_sla_overrides`).
- Credit-decision ledger (`sla_credit_decisions`).
- Exclusion log (force-majeure, provider-outage, maintenance).
- Public design system (`premium-ui-ux-design`, `practical-ui-design`).

## Workflow

1. Read this `SKILL.md`.
2. Design the **dashboard panel layout** (§1). See `references/dashboard-spec.md`.
3. Specify the **metrics shown** (§2) and their query source (must match credit-decision queries).
4. Design the **embeddable widget** (§3). See `references/widget-embed.md`.
5. Specify the **public API** (§4). See `references/sla-api-contract.md`.
6. Wire **exclusion disclosure** (§5) — every excluded period is visible.
7. Wire **credit-balance display + notifications** (§6).
8. Apply anti-patterns (§7).

## Quality Standards

- Every number on the dashboard is the same number used by the credit pipeline. Single source of truth.
- The dashboard explicitly shows **raw** rate and **SLA-adjusted** rate (after exclusions).
- Excluded periods are listed with start, end, class, link to evidence.
- The customer can hover any number and see "computed from <N> tasks, in window <a>–<b>".
- Time-to-resolve is shown as p50 and p95, never as a single average.
- Credit balance reflects credits issued but not yet invoiced, separately from credits already applied.
- The widget loads in < 200ms p95 from cached server-rendered data.
- The public API rate-limits at the tenant level and never leaks cross-tenant data.

## Anti-Patterns

- "SLA dashboard" that is the marketing landing page. Display numbers, with no per-tenant data.
- Dashboard numbers that don't match invoice credits. Customer files dispute.
- Hidden exclusions. Customer sees the breach but no credit; thinks we're cheating.
- Single "uptime %". Tells the customer nothing about agent value.
- Average time-to-resolve. Tail-blind.
- Widget that requires SDK installation and 200KB of JS. Use server-rendered HTML iframe.
- Public API with no rate limit, no auth. Either we leak data or someone weaponizes it.
- "Coming soon" tile in the dashboard. Either ship the metric or hide it.

## Outputs

- Dashboard panel design (Figma + Markdown).
- Metric → query → display mapping.
- Embeddable widget (HTML iframe + JS variant).
- Public API contract.
- Exclusion disclosure UI.
- SLA-credit-balance widget.

## Evidence Produced

| Category | Artifact | Format | Example |
|---|---|---|---|
| Design | Dashboard panel spec | Markdown + screenshots | `docs/sla/customer-dashboard.md` |
| Design | Embeddable widget spec | Markdown | `docs/sla/sla-widget.md` |
| Architecture | Public SLA API spec | OpenAPI | `docs/sla/sla-api.yaml` |
| UX | Exclusion disclosure UX | Markdown + screenshots | `docs/sla/exclusion-disclosure.md` |

## References

- `references/dashboard-spec.md` — panel layout, metric details, drill-downs.
- `references/widget-embed.md` — embeddable widget contract (iframe + signed token).
- `references/sla-api-contract.md` — public SLA API contract.
- Companion: `ai-agent-sla-and-commitments`, `ai-agent-task-success-tracking`, `ai-agent-sla-credit-automation`, `ai-agent-attempted-vs-completed-billing`, `ai-agent-abandonment-and-refund-policy`, `practical-ui-design`, `premium-ui-ux-design`.

<!-- dual-compat-end -->

## §1 Panel Layout (summary)

```
┌─ Your AI Agent SLA — Pro (class-A) ───────────────────────────────────┐
│                                                                       │
│  ✓ Resolution rate (30d): 87%      (floor: 85%)                       │
│    142 of 163 attempted tasks resolved                                │
│    Adjusted for excluded periods: 88%                                 │
│                                                                       │
│  ✓ Intervention rate (30d): 18%    (ceiling: 25%)                     │
│                                                                       │
│  ✓ Irreversible off-script (30d): 0   (target: 0)                     │
│                                                                       │
│  ✓ Time-to-resolve p95: 2m 14s     (target: ≤ 3m)                     │
│                                                                       │
│  ✓ Availability (May 2026): 99.7%   (target: 99.5%)                   │
│                                                                       │
│  Excluded periods this window:                                        │
│    • 2026-05-04 09:00–11:00 UTC — provider outage (status: link)      │
│    • 2026-05-08 22:00–23:00 UTC — scheduled maintenance               │
│                                                                       │
│  SLA credit balance:                                                  │
│    • $0.00 outstanding (no breach this period)                        │
│    • Previous credits applied (last 90 days): $7.50                   │
│                                                                       │
│  [View full SLA history]  [Download evidence pack]                    │
└───────────────────────────────────────────────────────────────────────┘
```

Detailed spec in `references/dashboard-spec.md`.

## §2 Metrics and Sources

Each metric on the dashboard has exactly one source query. Same query feeds the credit pipeline.

| Metric | Source | Window |
|---|---|---|
| Resolution rate | `agent_resolution_30d` | rolling 30d |
| Tasks attempted | `agent_resolution_daily` sum | 30d (also 7d, today) |
| Tasks resolved | `agent_resolution_daily` sum | as above |
| Intervention rate | `agent_resolution_30d.intervention_rate` | rolling 30d |
| Irreversible off-script | `agent_resolution_30d.offscript_count` | rolling 30d |
| Time-to-resolve p50 / p95 | `agent_resolution_daily` percentiles | rolling 30d |
| Availability | gateway/runtime availability rollup | calendar month |
| Kill-switch latency p95 | incident mitigation log | trailing 30d |
| SLA credit (issued, not yet invoiced) | `sla_credit_decisions` | open period |
| SLA credits applied last 90d | `sla_credit_decisions` | trailing 90d |
| Refunds applied last 90d | `agent_refunds` | trailing 90d |

## §3 Embeddable Widget

For B2B tenants who want to show their own customers a trust badge or for Enterprise tenants who want to embed into their internal admin app.

Two variants:
- **iframe**: server-rendered HTML, signed token in URL. No JS required.
- **JS**: small SDK that injects a div. Required for live updates.

```
<iframe src="https://app.example.com/sla/widget?token=eyJ..." 
        style="width:100%;height:240px;border:0"></iframe>
```

The token is per-tenant, signed, scoped to widget read access. Token TTL 12h to enable caching.

Full spec in `references/widget-embed.md`.

## §4 Public SLA API

Authenticated, per-tenant, rate-limited.

```
GET /v1/sla/status
GET /v1/sla/credits?from=...&to=...
GET /v1/sla/exclusions?from=...&to=...
GET /v1/sla/incidents?from=...&to=...
GET /v1/sla/evidence/{decision_id}
```

Returns JSON. Available to Pro+ (read-only); Enterprise gets webhook subscriptions for breach / credit / exclusion events.

Full contract in `references/sla-api-contract.md`.

## §5 Exclusion Disclosure UX

Every exclusion appears with:

- Start / end timestamps (tenant's timezone, with UTC label).
- Class (force-majeure, provider-outage, scheduled-maintenance, etc.).
- Short summary in plain language.
- Link to evidence (provider status page, our status page, audit-log row).

When a metric was *affected* by an exclusion but the exclusion *cleared* the breach, the dashboard shows:

```
Resolution rate (raw): 82%        (below floor 85%)
Excluded period: 2026-05-04 09:00–11:00 UTC (provider outage)
Resolution rate (SLA-adjusted): 87%   ✓ meets your SLA
```

The customer sees both numbers; we don't hide the raw.

## §6 Credit Balance + Notifications

The credit balance widget shows:

- Credits issued this billing period, not yet applied.
- Credits applied last invoice.
- Total credits last 12 months.
- Refunds last 90 days.

When a credit is issued, the dashboard adds a banner above the panel: "We issued $X SLA credit for <reason>. <Link to evidence>." Banner dismissable; the credit stays in the ledger.

## §7 Anti-Patterns

- Numbers that don't match credits.
- Hidden exclusions.
- Single-number availability tile only.
- Average TTR.
- Widget that needs JS framework setup.
- API with no rate limit.
- "Coming soon" placeholder tiles.
- Dashboard updates only at month-end. Trust is built daily.


