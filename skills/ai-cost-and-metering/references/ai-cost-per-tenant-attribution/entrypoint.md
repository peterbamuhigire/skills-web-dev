> Consolidated from skills/ai-cost-per-tenant-attribution/SKILL.md into ai-cost-and-metering on 2026-05-13. Load this through skills/ai-cost-and-metering/SKILL.md, not as an active skill entrypoint.

# AI Cost Per-Tenant Attribution
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Standing up the operational AI-cost pipeline for a multi-tenant SaaS that has more than one paying tenant or more than one AI feature.
- Investigating why the AI bill spiked last month and you can't tell which tenant or feature drove it.
- Implementing per-tenant hard caps and soft thresholds before a long tail of small tenants becomes unprofitable.
- Reconciling provider invoices to internal cost ledgers and finding > 1% drift.
- Producing the cost-per-tenant chart sales needs to defend the price tier.

## Do Not Use When

- The task is *designing* the unit economics — `ai-cost-modeling`.
- The task is converting tokens to invoiced units for customers — `ai-usage-metering-and-billing`.
- The task is gateway design itself — `ai-model-gateway`.

## Required Inputs

- Gateway emits `ai.cost.recorded` events with `(tenant_id, request_id, usd_cost, tokens_in, tokens_out, feature, model_used)`.
- Plan catalogue with `cogs_target_pct` per plan (e.g., Pro plan target COGS ≤ 25% of MRR).
- `tenant_ai_binding.monthly_usd_cap` and `monthly_token_cap` populated.
- Provider invoices for at least one full month (for reconciliation).

## Workflow

1. Read this `SKILL.md`.
2. Confirm the **gateway emits cost-at-close** (§1) — if not, fix that first.
3. Build the **per-tenant cost dashboard** (§2) — top-20, p90, by feature, by model.
4. Build the **plan-COGS guardrail** (§3) — alert when any tenant's COGS exceeds plan target.
5. Build the **anomaly detector** (§4) — sudden 5x spend, runaway agent loops, retry storms.
6. Wire the **soft + hard spend ceilings** (§5) — communicate, then enforce.
7. Build the **kill-switch / degrade path** (§6) — single tenant or feature-wide.
8. Build **finance reconciliation** (§7) — match provider invoices to internal ledger.
9. Apply anti-patterns (§8).

## Quality Standards

- Cost-per-request is computed and persisted **synchronously** at the gateway. No deferred reconciliation.
- The cost-per-tenant dashboard updates with < 5-minute lag.
- Plan-COGS guardrail emits a daily report and pages on threshold breach.
- Anomaly detector catches a 10x same-day spend spike in < 15 minutes.
- Soft ceiling triggers tenant-facing communication; hard ceiling enforces.
- Internal ledger matches provider invoice within 1% on month close.

## Anti-Patterns

- Cost reconciled monthly from provider invoices. Attribution is approximate; tenant-level chargebacks are impossible.
- One shared API key across tenants, no per-request tagging. The provider can't help; the platform can't either.
- No anomaly detector. The first you hear about a $40k runaway agent is your provider bill.
- Hard cap with no soft warning. Tenants get surprised; churn spikes.
- Kill-switch as a code deploy. Means there is no kill-switch.
- Dashboard shows USD but not COGS%. Big tenants always look bad; small tenants always look fine; the question wasn't answered.

## Outputs

- Per-tenant cost dashboard (top-20, p90, by-feature, by-model, COGS%).
- Anomaly detector rules + alerts.
- Soft + hard ceiling policy with comms and enforcement.
- Reconciliation report (monthly).
- Finance close runbook.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Architecture | Cost pipeline diagram | Markdown + image | `docs/ai/cost-pipeline.md` |
| Release evidence | Per-tenant cost dashboard | Dashboard link + screenshot | `docs/ai/dashboards/per-tenant-cost.md` |
| Operability | Anomaly rule set | YAML / Markdown | `docs/ai/cost-anomaly-rules.md` |
| Compliance | Monthly reconciliation report | Markdown + CSV | `reports/ai-cost-recon/2026-04.md` |

## References

- `references/token-accounting-pipeline.md` — the data flow.
- `references/model-price-table-template.md` — price table format + ops.
- Companion: `ai-model-gateway`, `ai-usage-metering-and-billing`, `ai-cost-modeling`, `ai-on-saas-architecture`, `ai-entitlements-and-feature-gating`, `observability-monitoring`, `saas-rate-limiting-and-quotas`.
- Incident handoff: cost-anomaly signals (`tenant_cost_anomaly_z3`, `feature_cost_runaway`) are detection signals in `ai-incident-detection-and-triage`. Anomaly alert payload must include `runbook` and `failure_class_hint: cost-runaway`. See `ai-incident-response-runbook` (class `cost-runaway`) for first mitigation (per-tenant or per-feature quota cap via `ai-model-gateway`) and `ai-rca-taxonomy` for cost-class root-cause categories (commercial.provider-price-change, infra.gateway-routing-change, agent.runaway-loop, model.prompt-regression with cost lens).

<!-- dual-compat-end -->

## §1 Gateway-Emitted Cost — Non-Negotiable Prerequisite

If the gateway is not emitting cost at request close, fix this before anything else. The recipe lives in `ai-model-gateway` §7 and `references/token-accounting-pipeline.md`. Confirm:

- `ai_requests` row carries `usd_cost`, `tokens_in`, `tokens_out`, `model_used`, `feature`, `prompt_id`, `prompt_version`, `region`.
- Redis hash `ai:cost:{tenant_id}:{yyyymm}` updated atomically with the row.
- `ai.cost.recorded` event published on the bus.

Without these three, no downstream analysis is reliable.

## §2 Per-Tenant Cost Dashboard

Standard views every SaaS needs:

| View | Definition | Owner |
|---|---|---|
| Top-20 by USD this month | tenant_id, MRR, USD, COGS% | sales-finance |
| Top-20 by COGS% this month | tenants where COGS% > plan target | product |
| By feature | sum USD per feature this week vs last | product |
| By model | model_used cost mix; fallback ratio | platform |
| Per-tenant trend | last 90 days USD per tenant, top 50 | finance |
| Cost per active user | tenant_id, MAU, USD/MAU | growth |
| Cost per invoiced unit | matched to billing event | finance |
| Failed / retried cost | retries + fallbacks USD share | platform |

The dashboard updates with < 5-minute lag from the realtime counter; reconciled view from `tenant_ai_daily` for accuracy.

## §3 Plan-COGS Guardrail

Every plan has a target COGS%:

| Plan | Target COGS% | Action if breached |
|---|---|---|
| Free | 100% (gives away N free generations) | volume cap; downgrade to distilled |
| Starter | ≤ 40% | review + pricing change |
| Pro | ≤ 25% | review + tier rebalance |
| Enterprise | ≤ 15% on AI features | true-up with the AE; consider custom |

Daily cron computes per-tenant COGS% over a trailing 30-day window. Breaches go to:
- A sortable internal report.
- An email to product + finance.
- A back-office flag on the tenant record.
- Optionally, a sales-assist task for tenants worth talking to about an upgrade.

A persistent breach on a Free plan triggers an automatic shift to a cheaper model tier.

## §4 Anomaly Detector

Rules (start with five):

1. **Sudden spike**: today's USD > 5× trailing-7-day median for this tenant. Page.
2. **Runaway agent**: one tenant's agent sessions exceeded N steps each on > 50 sessions in 1h. Page.
3. **Retry storm**: gateway retry ratio for a feature > 30% over 15 minutes. Page platform.
4. **Fallback ratio spike**: fallback usage for an enterprise tenant > 5% for the day. Page.
5. **New feature, no budget**: feature seen in `ai_requests` with no `ai_cost_budget` registered. Page product.

Implement as scheduled queries against `ai_requests` + Redis; emit `ai.cost.anomaly` events; route through your incident system.

## §5 Soft + Hard Ceilings

Two layers:

- **Soft ceiling** at 80% of cap → in-product banner, email to billing contact, sales-assist task. No enforcement.
- **Soft ceiling** at 95% → stronger email; suggested upgrade URL.
- **Hard ceiling** at 100% → 429 from gateway; tenant-facing error explains the cap and links to upgrade.

For enterprise tenants on a true-up contract, replace hard with **paging-only** ceiling: AE is notified, no enforcement.

Configurable per tenant — flagship customer can opt-out of hard ceiling with a contractual amendment.

## §6 Kill-Switch / Degrade Path

Three options for the back-office operator:

1. **Pause AI for this tenant** — `tenant_ai_binding.ai_enabled = false`. Total stop.
2. **Pause a feature for this tenant** — `tenant_ai_feature_disable` row. Granular.
3. **Degrade tier for this tenant** — change `model_tier` to a cheaper model (distilled). Reduces cost without stopping the product.

All three flip in < 60s. Each writes an `ai.kill_switched` or `ai.degraded` event. Back-office operator must include a reason. Tenant receives an in-product notice within 2 minutes.

## §7 Finance Reconciliation

Monthly close:

1. Sum `ai_requests.usd_cost` for the month, grouped by provider.
2. Provider invoices arrive 24–72h after month end.
3. Diff: per provider, per region, per model.
4. Drift sources:
   - Price table out of date → bump price table, recompute affected rows, alert.
   - Token counting drift (provider reports include system tokens we didn't count) → adjust pipeline.
   - Failed-request charges (some providers bill 4xx as 0; some bill 5xx as 0 + retries) → align.
5. After reconciliation, the canonical "what each tenant cost the platform" is the Postgres ledger, not the invoice.

Acceptable drift: < 1% at month close. Beyond, root-cause and re-run the daily aggregate.

## §8 Anti-Patterns

- "We'll figure out per-tenant cost when we have time." You won't. Build the pipeline before the second paying tenant.
- Single shared OpenAI key, single PSP account, single project — no provider-side tagging for tenants. Use distinct accounts/projects per region/tier; tag every request.
- Hard cap with no upgrade path in the error. Hostile UX; churn driver.
- Soft cap email with no real number. Tenant has no way to know "70%" of what.
- COGS dashboard in USD, never as % of MRR. Misleading for tier comparison.
- Anomaly detector that only looks at platform totals. Misses single-tenant runaway agents.
- Reconciliation done by exporting CSV from Stripe and adding columns in Excel. Drift never fixed at root cause.

## §9 Agent-Step Cost Attribution

A request-level cost view is insufficient for agentic features. A single user goal ("send the invoice") may fan out into 6-30 LLM calls and 4-20 tool calls. The unit the business actually charges (and the unit cost-per-tenant should reflect) is the **completed agent task**, not the individual LLM call.

### Required additions when agents are in scope

**Per-task rollup table** (populated by `ai-agent-cost-and-step-budgets` enforcement):

```sql
CREATE TABLE agent_task_cost_ledger (
  task_id          BIGINT PRIMARY KEY,
  tenant_id        BIGINT NOT NULL,
  feature          VARCHAR(64) NOT NULL,
  model_pin        VARCHAR(64) NOT NULL,
  terminal_state   VARCHAR(32) NOT NULL,
  step_used        INT NOT NULL,
  tokens_in        BIGINT NOT NULL,
  tokens_out       BIGINT NOT NULL,
  usd_llm_cost     DECIMAL(10,4) NOT NULL,
  usd_tool_cost    DECIMAL(10,4) NOT NULL,
  usd_total        DECIMAL(10,4) NOT NULL,
  wallclock_seconds INT NOT NULL,
  created_at       DATETIME NOT NULL,
  completed_at     DATETIME NOT NULL,
  INDEX (tenant_id, completed_at, feature)
);
```

**Daily rollup includes agent metrics:**

| Metric | Definition |
|---|---|
| `tenant_id, agent_tasks_attempted` | Count of agent tasks started |
| `tenant_id, agent_tasks_completed` | Count reaching `COMPLETED` |
| `tenant_id, usd_per_completed_task_p50` | Median cost per completed task |
| `tenant_id, usd_per_completed_task_p90` | p90 cost per completed task |
| `tenant_id, agent_cost_share` | sum(agent task cost) / sum(all AI cost) |
| `tenant_id, task_success_rate` | completed / attempted |
| `tenant_id, usd_wasted_on_failed_or_abandoned` | sum of cost on non-completed terminal states |

The "USD wasted" metric is the key insight: paying tenants are charged for the value of completed tasks; the platform absorbs the cost of failures. High waste → product / agent design issue → COGS drift.

### Dashboards add

- **Cost-per-completed-task by feature × plan** (replaces "cost-per-request" for agentic features).
- **Top-10 tasks by cost in last hour** — surfaces runaway tasks before the daily report.
- **Wasted spend share per tenant** — agents that fail too often.

### Anomaly rules add

- **Task budget breach rate** for a feature > 10% in 15 min → page product.
- **Single task cost > 10× feature median** → page platform.
- **Tenant's `usd_wasted_on_failed_or_abandoned` > 30% of their AI cost** → product investigation.

### Cross-link

The runtime + enforcement is `ai-agent-cost-and-step-budgets`. This skill consumes its `agent.task.cost_recorded` events into the per-tenant pipeline.

## §10 Read Next

- `ai-agent-cost-and-step-budgets` — the per-task enforcement layer (step / token / wallclock / tool-cost budgets) that feeds the agent-task cost ledger.
- `ai-agent-runtime-architecture` — where the cost events originate.
- `ai-model-gateway` — upstream emitter.
- `ai-usage-metering-and-billing` — downstream commercial billing.
- `ai-entitlements-and-feature-gating` — defines the caps.
- `ai-cost-modeling` — sets the targets you guardrail against.
- `ai-observability-and-debugging` — anomaly investigation tools.


