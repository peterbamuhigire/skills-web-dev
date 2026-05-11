---
name: ai-agent-sla-and-commitments
description: Use when defining what an agentic SaaS product commits to in writing — task-success-rate floor, intervention-rate ceiling, irreversible-incident zero target, time-to-resolve p95, kill-switch SLA, availability — and turning those commitments into per-tier SLA classes, measurable counters, and breach definitions that engineering can enforce and finance can credit against. Distinct from generic platform SLA (uptime only) by being agent-shaped (resolution, intervention, irreversibility).
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Agent SLA and Commitments
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Writing the SLA section of a Pro/Business/Enterprise contract for an agent product and you need clauses that engineering can actually measure.
- Designing the **SLA-class table** per plan tier — Free has none, Pro has soft, Business has hard, Enterprise has bespoke.
- Choosing the **commitment surface** for a new agent feature: do we promise *availability*, *resolution rate*, *time-to-resolve*, or *all three*?
- Auditing whether an existing SLA is enforceable (every committed number has a counter; every counter has an alert; every alert has a credit formula).
- Coordinating with the **proposal engine** (which owns the contract language) and the **business-plan engine** (which owns the credit economics).

## Do Not Use When

- The task is **measuring** success on production traffic — `ai-agent-task-success-tracking`.
- The task is **issuing the credit** when a breach is detected — `ai-agent-sla-credit-automation`.
- The task is the **customer-facing dashboard** — `ai-agent-customer-sla-dashboard`.
- The task is **generic platform uptime** SLAs — `reliability-engineering` plus `observability-monitoring`.
- The task is **internal SLOs** (engineering targets that are tighter than SLAs) — `observability-monitoring`.

## Required Inputs

- Agent feature catalogue (which features ship to which tiers) — from `ai-entitlements-and-feature-gating`.
- Production task-success measurements (even rough) — from `ai-agent-eval` and `ai-agent-task-success-tracking`.
- Plan-tier commercial frame — from `software-pricing-strategy` and the business-plan engine.
- Mitigation primitives and their actual measured response times — from `ai-incident-response-runbook`.
- Customer-comms posture — from `ai-incident-customer-comms`.

## Workflow

1. Read this `SKILL.md`.
2. Pick the **commitment dimensions** (§1) for each agent feature: resolution rate, intervention rate, irreversible-incident count, time-to-resolve, kill-switch response time, availability.
3. Set the **floor / ceiling / zero-target** per tier (§2). See `references/sla-class-table.md`.
4. Apply the **measurability test** to every clause (§3) — if you can't show a counter and a query, delete the clause. See `references/sla-design-principles.md`.
5. Bind each commitment to an **enforcement path** (§4): counter → alert → credit formula → audit row.
6. Define **exclusions and force majeure** (§5) — narrow, written, audited.
7. Wire the **per-tier SLA class** into entitlements and the customer dashboard (§6).
8. Apply anti-patterns (§7).

## Quality Standards

- Every SLA clause has a numeric threshold, a measurement window, a counter name, and a credit formula. No qualitative commitments survive review.
- Every committed number is measured by a counter that lives in production *before* the SLA is offered to a customer.
- Irreversible-incident commitments are **zero-target**: no acceptable non-zero floor. Any irreversible off-script action is a breach by definition.
- SLA-class tables are **per-tier and per-feature**, not platform-wide. Different agent features have different difficulty floors.
- Exclusions are **enumerated** (force-majeure, customer-caused, provider-outage-acknowledged-in-status-page) — not "at vendor discretion".
- Time-to-resolve is reported as p50 and p95, never as a single number that hides the tail.
- Availability is *agent-feature* availability (can the customer start a task?), not raw API uptime.

## Anti-Patterns

- "Best-effort" SLA. Either it is committed or it isn't; "best effort" is a marketing word, not a contract clause.
- Single-number availability SLA on an agent product. Availability is necessary but never sufficient — a 100%-up agent that fails 60% of tasks is a worse buy than a 99.5%-up agent that resolves 90%.
- Resolution-rate clause with no measurement spec. Customer dispute opens, engineering cannot reproduce.
- Same SLA across all tiers. Removes pricing power; punishes Pro for not paying Enterprise prices.
- Time-to-resolve **average** instead of **p95**. Tail-blind.
- Force-majeure clause without an enumerated list. Becomes a black hole.
- SLA committed before the counter exists. First breach is uncountable.
- Irreversible-incident *acceptable rate > 0*. Encodes that some customer harm is allowed.

## Outputs

- SLA-class table per tier, per feature (Markdown).
- Per-clause measurement spec: counter name, window, query, credit formula.
- Exclusions list (force-majeure, customer-caused, provider-outage).
- SLA → entitlements binding (`sla_class` on tenant + tenant_feature rows).
- Public SLA page text (handed to the proposal engine for contract language).

## Evidence Produced

| Category | Artifact | Format | Example |
|---|---|---|---|
| Commercial | SLA-class table per tier | Markdown | `docs/sla/agent-sla-tiers.md` |
| Architecture | Counter → credit-formula map | YAML | `ops/sla/agent-sla-counters.yaml` |
| Release evidence | SLA-readiness checklist | Markdown | `docs/sla/sla-readiness-checklist.md` |
| Compliance | Exclusions enumeration | Markdown | `docs/sla/agent-sla-exclusions.md` |

## References

- `references/sla-class-table.md` — full per-tier × per-feature SLA-class table with thresholds.
- `references/sla-design-principles.md` — what is a good SLA, what is a measurable SLA, what should never be in an SLA.
- Companion: `ai-agent-task-success-tracking`, `ai-agent-sla-credit-automation`, `ai-agent-customer-sla-dashboard`, `ai-agent-eval`, `ai-incident-response-runbook`, `software-pricing-strategy`, `it-proposal-writing`, `subscription-billing`.

<!-- dual-compat-end -->

## §1 Commitment Dimensions

An agent SLA is built from these primitives. Not every product commits to every one; choose by feature.

| Dimension | What it commits to | Counter | Typical breach trigger |
|---|---|---|---|
| **Task-success / resolution rate** | % of attempted tasks that reach `RESOLVED` and pass success verdict | `agent.resolution.rate.30d` per feature, per tenant | < floor for 7 consecutive days |
| **Intervention rate ceiling** | % of tasks that required HITL approval (lower is better for autonomous agents) | `agent.intervention.rate.30d` | > ceiling for 7 consecutive days |
| **Irreversible-incident count** | Off-script irreversible actions | `agent.irreversible.offscript.count.30d` | > 0 in any rolling window |
| **Time-to-resolve p95** | Wallclock from `agent.task.started` to `agent.resolution.completed`, p95 | `agent.time_to_resolve.p95.30d` per feature | > ceiling for 7 consecutive days |
| **Kill-switch response time** | Time from operator click → in-flight tasks paused | `agent.killswitch.latency.p95` | > 60s on any production deployment |
| **Availability** | % of agent feature start-attempts that succeeded to `QUEUED` | `agent.feature.availability.30d` | < floor in any calendar month |
| **Approval-queue latency** (HITL features) | Time from `awaiting_approval` to user notification | `agent.approval.notify.latency.p95` | > 30s |
| **Data-residency adherence** (regulated) | % of tasks that ran in the contracted region | `agent.residency.adherence` | < 100% |

The first three are the **agent-specific** ones; nothing else in the SaaS catalogue captures them. The rest layer on top of standard reliability SLAs.

## §2 SLA Classes per Tier

Encode the table per-tier. Floors / ceilings are per-feature.

```
TIER         SLA CLASS    RESOLUTION RATE      INTERVENTION RATE     IRREVERSIBLE     TTR p95         AVAILABILITY    KILL-SWITCH    CREDIT FORMULA
Free         none         best-effort (display only)                                                                                  none
Starter      class-B      ≥ 75% (informational; no credit)                                                            99.0%          n/a            none
Pro          class-A      ≥ 85% / 30d         ≤ 25%                  0 / 30d          ≤ feature * 1.5  99.5%          ≤ 60s          5% of monthly fee per breach event
Business     class-AA     ≥ 90% / 30d         ≤ 15%                  0 / 30d          ≤ feature * 1.2  99.9%          ≤ 60s          10% / breach, capped 30% / month
Enterprise   bespoke      negotiated           negotiated             0 / 30d (firm)   negotiated       99.95%         ≤ 30s          per contract
```

Full table with per-feature floors in `references/sla-class-table.md`.

Rules:
- Free and Starter never receive SLA credit. Display-only metrics keep them honest.
- Pro+ has soft commitments (informational dashboard) and one or two hard commitments (resolution + irreversible).
- Business adds hard time-to-resolve.
- Enterprise customizes per-feature, per-intent.

## §3 Measurability Test

Every clause survives only if you can answer all five questions in writing:

1. **What is the counter?** Name, type (gauge / counter / histogram), where it lives (Redis / TSDB / database).
2. **What is the window?** Rolling 30d? Calendar month? Per-feature?
3. **What is the breach threshold?** Numeric, not adjectival.
4. **What is the credit formula?** Fixed % / sliding scale / capped.
5. **What is the evidence pack?** Which trace IDs, which audit-log rows, which judge-cascade verdicts prove the breach?

If any answer is "we'll figure it out when it happens" the clause is deleted.

Full rubric in `references/sla-design-principles.md`.

## §4 Enforcement Binding

Every SLA clause produces this YAML:

```yaml
sla_id: pro.support_copilot.resolution_rate
clause: "Pro: ≥ 85% resolution rate over rolling 30 days per feature."
counter: agent.resolution.rate.30d
counter_query: |
  SELECT sum(resolved_count) / nullif(sum(attempted_count), 0)
  FROM agent_resolution_daily
  WHERE tenant_id = :tenant AND feature = 'support_copilot'
    AND day >= NOW() - INTERVAL 30 DAY
floor: 0.85
window_days: 30
breach_definition: "value < floor for 7 consecutive days"
exclusions:
  - force_majeure
  - provider_outage_acknowledged
  - customer_caused (tenant set wrong tool entitlements)
credit_formula: "0.05 * monthly_fee per breach_event"
credit_cap_per_period: "0.30 * monthly_fee"
notification_targets:
  - tenant_owner_email
  - sla_dashboard
  - audit_log
hooks:
  on_breach: trigger.sla_credit_pipeline
```

`hooks.on_breach` calls into `ai-agent-sla-credit-automation` which does the issuance.

## §5 Exclusions and Force Majeure

Exclusions are **enumerated**. Each exclusion has its own counter so the dashboard shows raw vs. SLA-adjusted numbers.

```
EXCLUSION CLASS              EVIDENCE REQUIRED                                   CUSTOMER-VISIBLE?
force_majeure                external incident report                            yes
provider_outage_ack          ai-incident status page entry + provider's RCA      yes
customer_caused              tenant configuration change in audit log            yes (with explanation)
scheduled_maintenance        published in advance, ≥ 7 days notice              yes
beta_feature                 feature.flag indicates beta = true                  on opt-in
abuse_protection_engaged     rate-limit-engaged event                            yes (with explanation)
```

Anything not on this list is **not** an exclusion. A failed model upgrade we shipped is not force majeure — that's an SLA breach we own.

## §6 Per-Tier Binding to Entitlements

```sql
ALTER TABLE tenants ADD COLUMN sla_class
  ENUM('none','class-B','class-A','class-AA','bespoke') NOT NULL DEFAULT 'none';

CREATE TABLE tenant_sla_overrides (
  tenant_id      BIGINT NOT NULL,
  feature        VARCHAR(64) NOT NULL,
  metric         VARCHAR(64) NOT NULL,    -- e.g., 'resolution_rate'
  floor_or_ceil  DECIMAL(6,4) NOT NULL,
  window_days    INT NOT NULL,
  credit_formula JSON NOT NULL,
  effective_from DATE NOT NULL,
  effective_to   DATE NULL,
  contract_ref   VARCHAR(64) NOT NULL,     -- proposal/contract document id
  PRIMARY KEY (tenant_id, feature, metric, effective_from)
);
```

Bespoke (Enterprise) overrides live here. Class-A / AA defaults live in a YAML catalogue checked into the repo.

## §7 Anti-Patterns

- Single platform-wide SLA. Removes pricing power and over-promises on cheap tiers.
- Availability-only SLA on an agent product.
- Time-to-resolve as an average.
- Force-majeure clause with no list.
- Resolution-rate clause with no counter shipped.
- Irreversible-incident "acceptable rate" > 0.
- SLA class stored as free text in a contract PDF only — engineering can never query it.
- Per-tenant overrides scattered across Slack threads — not in `tenant_sla_overrides`.
