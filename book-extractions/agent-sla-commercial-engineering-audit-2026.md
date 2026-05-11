# AI Agent SLA + Commercial Layer Engineering Audit — May 2026

**Lens:** **SLA and commercial enforcement** for agentic SaaS products — what counts as task success, how we track it in production, how we automate SLA-credit issuance on breach, how we distinguish *attempted* from *completed* billing, how we handle abandonment and refunds, and how we expose all of this to the customer (dashboard, API, invoice line items) and to finance (revenue recognition, deferred revenue, refund reserves).

**Inputs:** the agent product stack (`ai-agent-runtime-architecture`, `ai-agent-tool-catalogue-and-action-gating`, `ai-agent-eval`, `ai-agent-observability-and-replay`, `ai-agent-cost-and-step-budgets`, `ai-agent-action-approval-and-hitl`); usage and cost (`ai-usage-metering-and-billing`, `ai-cost-per-tenant-attribution`); incidents (`ai-incident-detection-and-triage`, `ai-incident-response-runbook`, `ai-incident-customer-comms`, `ai-incident-postmortem`); plus commerce primitives (`subscription-billing`, `stripe-payments`, `saas-accounting-system`, `saas-admin-backoffice-tooling`, `saas-rate-limiting-and-quotas`).

**Prior verdict:** the agent engine has strong product-side coverage (runtime, eval, observability, budgets, approval, safety) and the AI/SaaS billing engine has strong token-and-credit coverage. But the *commercial seam* between them is missing. The current skills know how to **run** an agent and how to **meter** AI usage, but they do not know how to:

- declare a contractual commitment ("we promise ≥ 90% task success rate on Pro");
- detect breach of that commitment in production;
- automatically issue an SLA credit when breach occurs;
- bill **completed** tasks differently from **attempted** ones (and gate the count on eval);
- classify abandonment cleanly (technical / user-abort / out-of-scope / budget) and trigger the right refund;
- expose a customer-facing SLA dashboard with the same numbers used to issue credits;
- price per-resolution / per-outcome / hybrid via a deterministic resolver;
- recognize agent revenue under ASC 606 / IFRS 15 (deferred revenue, refund reserve, point-in-time vs over-time).

Without this layer, premium enterprise agent contracts are unenforceable, refunds become ad-hoc, finance cannot close the month, and customer trust is eroded the first time an agent fails silently and the bill arrives anyway.

---

## Existing Skill Audit (SLA / commercial lens)

| Skill | Coverage today | Gap for SLA + commercial |
|---|---|---|
| `ai-agent-runtime-architecture` | State machine, terminal states (COMPLETED / FAILED / BUDGET_EXCEEDED / KILLED / ABANDONED), lifecycle events | Does not define `RESOLVED` vs `ATTEMPTED` distinction; does not emit `agent.resolution.*` or `agent.intervention.*` events |
| `ai-agent-eval` | Task success rate, intervention rate, irreversible-action rate, step efficiency — at eval time | Does not feed *production* counters used for billing or SLA; no eval-gated counted-as-completed pipeline |
| `ai-agent-observability-and-replay` | Per-task trace, per-step span, replay | Does not capture *task-success evidence* as a first-class trace field |
| `ai-agent-cost-and-step-budgets` | Step / token / wallclock / tool-cost budgets; refusal-on-budget | Budget breach is silent on SLA — no auto-credit-eligibility check |
| `ai-agent-action-approval-and-hitl` | Approval UX, JIT, bulk, undo | Does not classify HITL interventions for billing (full-credit / shared / no-credit) |
| `ai-usage-metering-and-billing` | Tokens, credits, generations, prepaid pack, Stripe Meters | Has no `agent.task.*` / `agent.resolution.*` event family; no per-resolution price; no refund/credit-note pipeline tied to SLA |
| `ai-cost-per-tenant-attribution` | Cost rollups per tenant | No COGS-per-resolution or refund-reserve hook |
| `ai-incident-detection-and-triage` | Failure-class triage | No SLA-impact incident class that drives auto-credit |
| `ai-incident-response-runbook` | Mitigation primitives | No SLA-credit-issuance branch during ongoing incident |
| `subscription-billing` | Plans, Prices, proration, dunning | No agent-line-item patterns; no per-resolution Price scheme guidance |
| `saas-admin-backoffice-tooling` | Tenant ops, billing ops, audit | No SLA-credit override / dispute-resolution console |
| `saas-rate-limiting-and-quotas` | Per-tenant limits | Quota-breach has no SLA mapping (is it a service breach or expected?) |
| `saas-accounting-system` | Double-entry, deferred revenue | No agent-specific revenue policy (point-in-time at resolution vs. over-time vs. prepaid task credits) |

---

## Cross-cutting gaps

1. **No SLA-commitment skill.** What does the platform commit to? Task-success-rate floor, intervention-rate ceiling, irreversible-incident count = 0, time-to-resolve p95, kill-switch SLA, availability — none of this is encoded as an engineering surface. The proposal engine writes contract language; this engine has to *enforce* it.

2. **No production task-success tracking.** Eval measures success on goldens, not on live tenant traffic. To bill per-resolution and issue SLA credit on breach we need a heuristic + LLM-judge + human-verification *cascade* running against production tasks, with success-rate dashboards per tenant per feature.

3. **No SLA-credit-automation pipeline.** Today a breach (if anyone notices) becomes an ad-hoc finance ticket. We need: detection → eligibility check → credit calculation → Stripe credit-note → customer notification → audit log — all idempotent, all tied to the trace bundle that proves the breach.

4. **No attempted-vs-completed billing logic.** Per-resolution pricing requires a clean line between "we tried" and "we resolved". A "completed" task must pass the eval gate, not the agent's self-claim. There is no skill that says how to do this.

5. **No abandonment + refund policy.** Tasks abandon for at least four distinct reasons (technical / user-abort / out-of-scope / budget-exceeded). Each maps to a different commercial treatment. No taxonomy, no refund execution pipeline, no comms templates.

6. **No customer-facing SLA dashboard.** Customers must see the same numbers used to credit them. No spec for tasks-completed, tasks-attempted, resolution rate, time-to-resolve p50/p95, intervention rate, irreversible-incident counter (zero target), SLA-credit balance, SLA-tier.

7. **No pricing engine.** Per-resolution / per-outcome / per-step / per-agent / hybrid pricing requires a deterministic resolver: usage event → price-rule → invoice line item, with intervention-credit reduction, vendor-cost-pass-through with markup, abort-and-refund logic, FX corridor. Today this is implicit.

8. **No agent revenue recognition.** ASC 606 / IFRS 15 for per-resolution revenue is non-trivial: point-in-time vs. over-time recognition, deferred revenue for prepaid task credits, refund reserves, month-end close. The accounting skill is generic; agent-specific guidance is missing.

---

## NEW SKILLS (8)

| # | Skill | Purpose |
|---|---|---|
| 1 | `ai-agent-sla-and-commitments` | What to commit to: task-success-rate, intervention-rate ceiling, irreversible-incident zero, time-to-resolve, kill-switch SLA, availability. SLA-class table per tier. Multi-tier SLA design. |
| 2 | `ai-agent-task-success-tracking` | Defining task success objectively in production via heuristic + LLM-judge + human-verification cascade. Per-feature success contracts. Dispute resolution. Per-tenant success-rate dashboards and trending. |
| 3 | `ai-agent-sla-credit-automation` | SLA-breach → automated credit issuance pipeline: detection → eligibility check → credit calculation → Stripe credit-note → customer notification → audit log. Idempotent. Evidence-pack-backed. |
| 4 | `ai-agent-attempted-vs-completed-billing` | Bill for attempted vs completed: when do you bill? Abandonment policy; intervention-shared-credit; per-resolution billing pipeline with eval-gated counting; reversibility-of-bill on dispute. |
| 5 | `ai-agent-abandonment-and-refund-policy` | Abandonment classification (technical / user-abort / out-of-scope / budget-exceeded). Refund triggers per class. Refund execution pipeline. Finance accounting hooks. Customer comms templates. |
| 6 | `ai-agent-customer-sla-dashboard` | Per-tenant customer-facing dashboard: tasks-completed, attempted, resolution rate, time-to-resolve p50/p95, intervention rate, irreversible-incident counter, SLA-credit balance, SLA-tier. Embeddable widget + API. |
| 7 | `ai-agent-pricing-engine` | Engine for per-resolution / per-outcome / per-step / per-agent / hybrid pricing. Usage event → price-rule resolver → invoice line item. Intervention-credit reduction, vendor-cost-pass-through with markup, abort-and-refund logic, FX corridor. |
| 8 | `ai-agent-revenue-recognition` | ASC 606 / IFRS 15 for agent revenue: point-in-time at resolution, deferred revenue for prepaid task credits, refund reserves, month-end close pipeline. |

---

## ENHANCEMENTS to existing skills

| Skill | Enhancement |
|---|---|
| `ai-usage-metering-and-billing` | Add `agent.task.*`, `agent.resolution.*`, `agent.intervention.*` event family; cross-link to pricing engine. |
| `ai-agent-cost-and-step-budgets` | Budget breach → SLA-credit-eligibility check (auto-handoff to `ai-agent-sla-credit-automation`). |
| `ai-agent-eval` | Eval verdict → completed-task counter (production verdicts feed the billing gate). |
| `ai-agent-observability-and-replay` | Capture task-success evidence as a first-class trace field (`task.success.verdict`, `task.success.evidence_ref`). |
| `ai-incident-response-runbook` | SLA-impact incident class with auto-credit-issuance branch during incident. |
| `subscription-billing` | Add agent-line-item patterns (per-resolution price, abandonment refund, SLA credit). |
| `saas-admin-backoffice-tooling` | SLA-credit override + dispute-resolution console. |
| `saas-rate-limiting-and-quotas` | Map quota-breach → SLA implications (eligible breach vs. expected guard). |

---

## REFERENCE FILES (15)

| Skill | Reference | Purpose |
|---|---|---|
| `ai-agent-sla-and-commitments` | `sla-class-table.md` | SLA-class tables per tier (Free / Pro / Business / Enterprise). |
| `ai-agent-sla-and-commitments` | `sla-design-principles.md` | What is a *good* SLA, what is a *measurable* SLA, what should never be in an SLA. |
| `ai-agent-task-success-tracking` | `success-contract-spec.md` | Per-feature success-contract schema. |
| `ai-agent-task-success-tracking` | `judge-cascade-pipeline.md` | Heuristic → LLM-judge → human-verification pipeline with code. |
| `ai-agent-task-success-tracking` | `dispute-resolution.md` | Customer-disputes-a-success or disputes-a-failure flow. |
| `ai-agent-sla-credit-automation` | `credit-issuance-pipeline.md` | Stripe credit-note code, idempotency, audit log. |
| `ai-agent-sla-credit-automation` | `eligibility-rules.md` | Which breaches qualify, exclusions, blast-radius caps. |
| `ai-agent-attempted-vs-completed-billing` | `billing-pipeline.md` | End-to-end pipeline from `agent.resolution.completed` to invoice line item. |
| `ai-agent-attempted-vs-completed-billing` | `eval-gated-counting.md` | Eval verdict gate before counting a task as completed. |
| `ai-agent-attempted-vs-completed-billing` | `attempt-classification.md` | Classify every terminal state for billing. |
| `ai-agent-abandonment-and-refund-policy` | `abandonment-taxonomy.md` | Four-class taxonomy. |
| `ai-agent-abandonment-and-refund-policy` | `refund-execution.md` | Refund pipeline + comms template + accounting hooks. |
| `ai-agent-customer-sla-dashboard` | `dashboard-spec.md` | Dashboard widget layout, metrics, queries. |
| `ai-agent-customer-sla-dashboard` | `widget-embed.md` | Embeddable widget spec for tenant apps. |
| `ai-agent-customer-sla-dashboard` | `sla-api-contract.md` | Public SLA API contract (GET /v1/sla/...). |
| `ai-agent-pricing-engine` | `price-rule-resolver.md` | Resolver implementation (Python + TS). |
| `ai-agent-pricing-engine` | `intervention-credit-logic.md` | Shared-credit logic on HITL intervention. |
| `ai-agent-pricing-engine` | `vendor-cost-pass-through.md` | Pass-through with markup, FX corridor. |
| `ai-agent-revenue-recognition` | `asc-606-for-agents.md` | ASC 606 / IFRS 15 model for agent revenue. |
| `ai-agent-revenue-recognition` | `deferred-revenue-and-refund-reserves.md` | Deferred-revenue ledger and refund reserve calculation. |
| `ai-agent-revenue-recognition` | `month-end-close-pipeline.md` | Month-end close steps for agent revenue. |

---

## Cross-engine handoffs

- **Proposal engine** owns the **contract language** for SLAs: SLA-class names, breach definitions, refund formulas, force-majeure exclusions. This engine owns the **enforcement code** that turns those clauses into running counters and automatic Stripe credit-notes. Handoff artifact: `sla-class-table.md` is co-authored — proposal writes the words, this engine writes the numbers + thresholds.

- **Business-plan engine** owns the **economics**: per-resolution price points, expected COGS-per-resolution, refund-reserve %, contribution margin per agent-feature, and how SLA credits affect the P&L. This engine owns the **revenue recognition code** and **pricing resolver**. Handoff artifact: pricing tables are co-authored — business plan sets margins; this engine binds them into the resolver.

- **Customer-service engine** owns the **dispute conversation** with the customer when an SLA event fires; this engine produces the **evidence bundle** (trace, success verdict, eligibility decision, credit amount, audit log) the CS rep cites.

- **Incident-response engine** is the **trigger** for SLA-impact incidents; this engine is the **disbursement** layer (auto-credit, mass refund, comms).

---

## Critical gaps to watch after this engine ships

1. **Eval coverage drift.** If production task volume outpaces the eval golden set, the LLM-judge cascade silently degrades and we credit / bill incorrectly. Need an explicit re-golden-on-drift hook.
2. **Cross-currency SLA credit.** Stripe credit-notes are in the invoice currency; multi-currency tenants need an FX-corridor policy that doesn't change retroactively.
3. **Tenant-side abuse.** A tenant could mark every task as "failed" to trigger refunds. Dispute-resolution flow must include a *rebuttal* path with evidence and a chargeback ceiling per tenant per period.
4. **Regulator-grade audit retention.** For financial-services tenants, the success-verdict, credit decision, and refund execution must be retained 7+ years (SOX, MiFID II). Confirm retention policy in `ai-agent-observability-and-replay`.
5. **Premium-tier custom SLAs.** Enterprise tenants will negotiate bespoke SLAs (e.g., 99.9% resolution rate on a specific intent class). The schema must allow per-tenant override without code change.

---

## Recommended next sessions

1. **Tax + regional pricing engine** — VAT on per-resolution, withholding tax, reverse charge, East-African corridors (`pricing-engine` + tax skill).
2. **Agent commercial dashboard for ops** — internal-facing version of the customer dashboard, with cohort SLA, credit-burn, refund-reserve trend, agent-feature P&L.
3. **Multi-agent contribution attribution** — when two agents resolve one task, who gets billed/credited? Pairs with `ai-agent-multi-agent-coordination`.
4. **Agent insurance / vendor recourse** — when the failure is an upstream LLM provider, recover credit from the provider's SLA before issuing ours.
5. **SOC2/ISO27001 audit pack for agent SLA** — auditor-ready report that ties commitments → counters → credit decisions.
