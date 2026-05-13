# Customer SLA Dashboard — Layout and Metric Specifications

## Panel: "Your AI Agent SLA"

Visible to tenant owners and tenant billing-admins by default. Custom roles configurable per-feature.

### Top Strip (always visible)

```
┌──────────────────────────────────────────────────────────────────────┐
│ Your AI Agent SLA  •  Plan: Pro (class-A)  •  Effective from: 2026-01-15 │
└──────────────────────────────────────────────────────────────────────┘
```

Shows:
- SLA class with link to public SLA page.
- Plan name.
- Date the current SLA terms began.

### Feature Selector

```
[ Support copilot ▼ ]   [ Log investigator ]   [ Code change agent (beta) ]
```

Beta features show a "beta" label and explanatory tooltip about non-credit-bound metrics.

### Metric Tiles

Each tile shows:

```
┌─ Resolution rate (30d) ─────────────────────────┐
│                                                 │
│  87%      ↑ +2pp vs last 30d                    │
│                                                 │
│  ✓ Above your SLA floor of 85%                  │
│                                                 │
│  142 of 163 attempted tasks resolved            │
│  Adjusted for excluded periods: 88%             │
│                                                 │
│  [ View details ]                               │
└─────────────────────────────────────────────────┘
```

Tile states (visual cues):
- Green check: above floor / below ceiling — SLA met.
- Amber: within 5pp of floor / ceiling — at risk.
- Red: in breach (after exclusions).

Hover/click expands to a 30-day spark line + per-day table.

### Metrics Shown (and queries)

#### Resolution rate (30d)

Query (must match credit pipeline):
```sql
SELECT SUM(resolved_count) / NULLIF(SUM(attempted_count), 0)
FROM agent_resolution_daily
WHERE tenant_id = :tenant
  AND feature = :feature
  AND day >= CURRENT_DATE - INTERVAL 30 DAY
```

Drill-down: per-day table with attempted, resolved, intervened, irreversibles. Click a day → list of tasks (each linking to a *redacted* trace view).

#### Intervention rate (30d)

Query:
```sql
SELECT SUM(intervened_count) / NULLIF(SUM(attempted_count), 0)
FROM agent_resolution_daily
WHERE tenant_id = :tenant AND feature = :feature
  AND day >= CURRENT_DATE - INTERVAL 30 DAY
```

Tooltip explains: "How often a human had to intervene. Lower is better; means the agent worked more autonomously."

#### Irreversible off-script (30d)

Query:
```sql
SELECT SUM(irreversibles_offscript)
FROM agent_resolution_daily
WHERE tenant_id = :tenant AND feature = :feature
  AND day >= CURRENT_DATE - INTERVAL 30 DAY
```

Target is **0**. Any value > 0 shows the tile in red with a link to incident details.

#### Time-to-resolve p50/p95

Query (per day, then aggregate over window):
```sql
SELECT
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ttr_p50_seconds) AS p50,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ttr_p95_seconds) AS p95
FROM agent_resolution_daily
WHERE tenant_id = :tenant AND feature = :feature
  AND day >= CURRENT_DATE - INTERVAL 30 DAY
```

(Aggregating percentiles by averaging daily percentiles is a known approximation — acceptable for display; the credit pipeline uses an exact percentile over the full task list.)

#### Availability (calendar month)

Source: gateway/runtime task-creation success rate per feature. Counted by attempts.

```sql
SELECT SUM(start_success) / NULLIF(SUM(start_attempts), 0)
FROM agent_feature_availability_daily
WHERE tenant_id = :tenant AND feature = :feature
  AND day >= DATE_TRUNC('month', CURRENT_DATE)
```

#### Kill-switch latency p95 (last 30d, if any incidents)

If no kill-switch events: tile reads "No incidents this period — kill-switch ready."

If incidents: shows p95 latency + a list of events. Each event links to the incident postmortem if published.

### Exclusion Strip

Always visible below the tiles:

```
┌─ Excluded periods this window ──────────────────────────────────────┐
│ • 2026-05-04 09:00–11:00 UTC — provider outage (anthropic-2026-05-04)│
│ • 2026-05-08 22:00–23:00 UTC — scheduled maintenance (notice 05-01) │
│                                                                      │
│ Raw rate: 82%   |   SLA-adjusted rate (excludes above): 87%          │
└──────────────────────────────────────────────────────────────────────┘
```

Hover any exclusion → details. Click → status page or audit row.

### SLA Credit Balance

```
┌─ SLA credit balance ──────────────────────────────────────────────────┐
│                                                                       │
│ This period (not yet invoiced):  $0.00                                │
│ Last invoice applied:            $7.50  (May 2026)                    │
│ Last 12 months:                  $42.00                               │
│                                                                       │
│ Refunds last 90 days:            $3.60  (3 refunds, see history)      │
│                                                                       │
│ [ View credit history ]   [ Download statement ]                      │
└───────────────────────────────────────────────────────────────────────┘
```

Credit history shows every `sla_credit_decisions` row: date, sla_id, amount, evidence link.

### Action Buttons

- **Download evidence pack** — current period bundled, signed.
- **View full SLA history** — all-time list of credits, refunds, exclusions.
- **Set up SLA webhook** — Enterprise only.

## Plain-Language SLA Definitions

Below the panel, the customer-readable SLA text:

```
Your Pro SLA includes:
• At least 85% resolution rate over any rolling 30 days, per feature you use.
• At most 25% intervention rate (we want the agent to handle it).
• Zero off-script irreversible actions.
• Time-to-resolve p95 ≤ 3 minutes (advisory; no automatic credit at this tier).
• 99.5% availability per calendar month.

If we miss any of these, we automatically issue you a service credit.

Read the full SLA: <link>
```

This is the same text the proposal engine produces — single source.

## Mobile Layout

Stacks the tiles vertically. The exclusion strip becomes an expandable card. Drill-downs open in full-screen sheets.

## Theming

Inherits the host application's design system. Premium tier uses `premium-ui-ux-design`. Color usage follows status semantics:
- Green = met SLA.
- Amber = at risk (within 5pp of floor / ceiling).
- Red = breach detected.
- Grey = excluded period.

## Performance Targets

- Initial render ≤ 200ms p95 from server cache.
- Cache refresh every 5 minutes (data freshness sufficient for SLA).
- Spark lines lazy-loaded on first scroll.
- Drill-downs paginated; default page 50 tasks.

## Accessibility

- All numbers also surface in screen-reader-readable text (not just visual tiles).
- Color is never the only signal — green tiles also carry the "✓ Above floor" text.
- Drill-down tables are keyboard navigable.

## Snapshots for Audit

Customers can download a signed snapshot of the dashboard for any past month. The snapshot is the evidence pack: numbers + queries + exclusions + credits. PDF + JSON.

## Anti-Patterns

- Numbers that don't match the credit pipeline.
- Drill-downs that leak cross-tenant data (paranoid checks in every query).
- "Customer support insights" mixed into the SLA panel (different mental model; clutter).
- "Coming soon" placeholders.
- Dashboard auto-refreshes every 5 seconds for visual effect.
