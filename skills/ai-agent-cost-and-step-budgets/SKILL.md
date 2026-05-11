---
name: ai-agent-cost-and-step-budgets
description: Use when engineering the budget enforcement layer for agent tasks — step budget (max iterations), token budget, wallclock budget, tool-cost budget, per-tenant-tier overrides, refusal-on-budget UX, and the cost-per-completed-task attribution that integrates with `ai-cost-per-tenant-attribution`. Distinct from `saas-rate-limiting-and-quotas` (request-rate caps) by being task-shaped.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Agent Cost and Step Budgets
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Wiring the budget layer into the agent runtime so a runaway task cannot spend $40k overnight.
- Designing per-tier budgets: Free 5 steps / $0.05; Pro 20 steps / $1.00; Enterprise 100 steps / $10.00.
- Implementing **refusal-on-budget**: when budget hits, the agent stops cleanly, summarises progress, and asks the user.
- Computing **cost-per-completed-task** (sum of LLM + tool costs / count of `COMPLETED` tasks) and attributing it to the tenant in `ai-cost-per-tenant-attribution`.
- Detecting cost anomalies *at the task level* (a single task spending 50× the median).

## Do Not Use When

- The task is the platform cost-attribution pipeline — `ai-cost-per-tenant-attribution`. This skill is the per-task enforcement; that skill is the rollup.
- The task is general SaaS quotas / rate limiting — `saas-rate-limiting-and-quotas`.
- The task is tool side-effect budgets (count of emails, etc.) — `ai-agent-tool-catalogue-and-action-gating`.
- The task is plan-tier entitlements — `ai-entitlements-and-feature-gating` (this skill enforces *runtime budgets*; that skill enforces *eligibility*).

## Required Inputs

- Agent runtime (`ai-agent-runtime-architecture`).
- LLM gateway emitting per-call cost (`ai-model-gateway`).
- Plan / tier catalogue with agent budgets (`ai-entitlements-and-feature-gating`).
- Cost attribution pipeline (`ai-cost-per-tenant-attribution`).

## Workflow

1. Read this `SKILL.md`.
2. Define the **four budget dimensions** (§1): step, token, wallclock, tool-cost.
3. Map **plan tiers → budgets** (§2).
4. Implement the **enforcement pipeline** (§3). See `references/budget-enforcement-pipeline.md`.
5. Implement **refusal-on-budget** UX (§4): clean stop, summarise, ask.
6. Wire **cost-per-completed-task** attribution (§5).
7. Implement **anomaly detection at task level** (§6).
8. Apply anti-patterns (§7).

## Quality Standards

- Every agent task has all four budgets set before it starts. No nulls.
- Budgets are **checked before each state transition** in the runtime loop, not after.
- A task that breaches any budget transitions cleanly to `BUDGET_EXCEEDED`, emits an event, summarises progress, and informs the user.
- Cost-per-completed-task is computed and stored on the task row; rolled up daily into `ai-cost-per-tenant-attribution`.
- Per-tenant overrides are time-boxed, audited, and surfaced in the admin console.
- Task-level anomaly detector catches a 10× median spike within < 5 minutes.
- The Free tier has hard budgets; Pro has soft + hard; Enterprise has soft + hard with notification escalation.

## Anti-Patterns

- "Step budget = 50, just to be safe." A budget that never bites isn't a budget.
- Budgets enforced as advisory in the prompt ("don't use more than 10 steps"). Trivially ignored.
- Cost budget checked **after** each step completes, not before. One step can be $20.
- Wallclock budget without a worker SIGINT. Worker happily runs forever.
- No per-task COGS rollup. Cost-per-tenant view is the only signal; can't tell which tasks were expensive.
- Budget exceeded leaves the task in `ACTING`. Approval queue thinks it's pending. Customer sees "in progress" forever.
- Tier budgets that don't differentiate by feature. Same Pro budget for "draft an email" and "investigate 3 days of logs".

## Outputs

- Four-dimension budget schema on `agent_tasks`.
- Plan-tier × feature × budget catalogue.
- Enforcement pipeline implementation.
- Refusal-on-budget UX components.
- Cost-per-task COGS pipeline.
- Anomaly detector rules.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Architecture | Budget enforcement design | Markdown | `docs/ai/agent-budgets.md` |
| Correctness | Budget enforcement tests | CI report | `tests/ai/agent_budgets_test.py` |
| Operability | Cost-per-task dashboard | Dashboard link | `docs/ai/dashboards/cost-per-task.md` |
| Operability | Task-level anomaly runbook | Markdown | `docs/runbooks/agent-cost-anomaly.md` |

## References

- `references/budget-enforcement-pipeline.md` — implementation, including atomic Redis counters + DB persistence.
- Companion: `ai-agent-runtime-architecture`, `ai-cost-per-tenant-attribution`, `ai-model-gateway`, `ai-entitlements-and-feature-gating`, `ai-usage-metering-and-billing`, `saas-rate-limiting-and-quotas`, `ai-agent-eval`.

<!-- dual-compat-end -->

## §1 Four Budget Dimensions

| Budget | What it caps | Why |
|---|---|---|
| **Step budget** | Number of `PLANNING → ACTING → OBSERVING` cycles | Compound-accuracy decay; runaway loops |
| **Token budget** | Sum of input + output tokens across all LLM calls in the task | LLM cost cap |
| **Wallclock budget** | Real elapsed seconds | Async tasks must not run forever |
| **Tool-cost budget** | Sum of usd cost from tools that bill (e.g., paid third-party APIs) | Non-LLM cost cap |

All four are required. A task without all four is rejected at creation.

## §2 Plan-Tier × Feature Budget Catalogue

Budgets vary by **feature** as well as tier. A "draft an email" task has very different complexity than "investigate 30 days of logs".

```yaml
feature: support_copilot
default_budgets:
  free:        { step: 5,  token: 8000,   wallclock_s: 30,  tool_cost_usd: 0.02 }
  pro:         { step: 12, token: 24000,  wallclock_s: 120, tool_cost_usd: 0.20 }
  enterprise:  { step: 20, token: 60000,  wallclock_s: 300, tool_cost_usd: 1.00 }

feature: log_investigator
default_budgets:
  free:        { agent_disabled: true }
  pro:         { step: 25, token: 80000,  wallclock_s: 600,  tool_cost_usd: 1.00 }
  enterprise:  { step: 60, token: 200000, wallclock_s: 1800, tool_cost_usd: 5.00 }
```

Per-tenant overrides live in `tenant_agent_budget_overrides` with `expires_at` and `reason`.

## §3 Enforcement Pipeline (Outline)

```
1. Task created:
   - resolve_budgets(tenant, feature) -> 4 values
   - store on agent_tasks row
   - charge step=0, tokens=0, wallclock=0, tool_cost=0 to running counters in Redis

2. Before PLANNING:
   - check step_used < step_budget
   - check elapsed_seconds < wallclock_budget
   - if breach: transition BUDGET_EXCEEDED, exit

3. After LLM call (in PLANNING or in tool-arg generation):
   - tokens_in/out from gateway response
   - usd_cost from gateway response
   - increment counters
   - if tokens_used >= token_budget OR usd_cost_used >= LLM cost cap: BUDGET_EXCEEDED

4. Before ACTING (tool call):
   - check tool_cost_used + tool_price_estimate < tool_cost_budget
   - if breach (deterministic): BUDGET_EXCEEDED

5. After ACTING:
   - persist exact tool cost
   - re-check budgets

6. On terminal state:
   - finalize cost-per-task row
   - emit agent.task.cost_recorded with {step_used, tokens, usd_cost, wallclock}
```

Full implementation in `references/budget-enforcement-pipeline.md`.

## §4 Refusal-on-Budget UX

When a budget breaches, the agent **never** silently stops. It:

1. Transitions to `BUDGET_EXCEEDED`.
2. Generates a final summary using a small additional cost (configurable; default $0.01 ceiling).
3. Returns to the user:
   ```
   I've used my safety limit for this task. Here's what I found before stopping:
   • <progress summary>
   
   To continue: [Add more budget]   [Restart with adjusted scope]   [Hand off to a human]
   ```
4. Emits `agent.task.budget_exceeded` event.
5. Appears in the agent inbox with a "resume" affordance if the tier allows.

The "Add more budget" affordance only appears for Pro and Enterprise; Free hard-stops.

## §5 Cost-Per-Completed-Task

On `COMPLETED`, write:

```sql
INSERT INTO agent_task_cost_ledger
  (task_id, tenant_id, feature, model_pin, terminal_state,
   step_used, tokens_in, tokens_out, usd_llm_cost, usd_tool_cost, usd_total,
   wallclock_seconds, completed_at)
VALUES (...);
```

Daily rollup feeds `ai-cost-per-tenant-attribution`:
- Per-tenant `usd_per_completed_task` (median, p90).
- Per-tenant `tasks_completed / tasks_attempted` (success rate).
- Per-tenant cost share = (sum of agent task cost) / (tenant's total AI cost).

## §6 Task-Level Anomaly Detection

```sql
-- Median task cost per (feature, tenant_plan) in the last 7 days
SELECT feature, tenant_plan, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY usd_total) AS median
FROM agent_task_cost_ledger
WHERE completed_at > NOW() - INTERVAL 7 DAY
GROUP BY feature, tenant_plan;
```

Alert when a single task's `usd_total > 10 × median(feature, plan)`. The dashboard surfaces top-10 task cost in last hour.

## §7 Anti-Patterns

- Step budget = 50 "to be safe" — high enough to never bite; effectively no budget.
- Budgets set globally rather than per-feature. Inflates the cap for cheap features, breaks expensive ones.
- Token budget without wallclock budget. A slow task with low token rate runs for hours.
- Budget exceeded leaves the task `ACTING` forever. Agent inbox lies about state.
- "We'll add a budget later." First runaway loop is in production within a week.
- Cost-per-task missing from the cost dashboard. Cannot find which tasks are expensive.
- Per-tenant override granted by a SQL UPDATE with no audit row.
