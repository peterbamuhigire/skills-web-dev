> Consolidated from skills/ai-agent-revenue-recognition/SKILL.md into ai-agent-commercial-operations on 2026-05-13. Load this through skills/ai-agent-commercial-operations/SKILL.md, not as an active skill entrypoint.

# AI Agent Revenue Recognition
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Engineering the **revenue recognition pipeline** for per-resolution / per-outcome agent revenue.
- Setting **point-in-time vs. over-time** policy per agent feature.
- Modeling **deferred revenue** for prepaid task-credit packs.
- Sizing the **refund reserve** for technical / out-of-scope abandonment.
- Wiring **revenue de-recognition** on disputed-overturn or post-bill refund.
- Standing up the **month-end close pipeline** that produces the agent-revenue journal entries.
- Coordinating with finance / external auditors on agent-revenue policy under ASC 606 (US-GAAP) and IFRS 15 (IFRS).

## Do Not Use When

- The task is generic SaaS subscription revenue recognition — `saas-accounting-system`.
- The task is the *pricing* itself — `ai-agent-pricing-engine`.
- The task is *issuing* an SLA credit — `ai-agent-sla-credit-automation`.
- The task is double-entry primitives, GL structure, statutory reporting — `saas-accounting-system` / `accounting-finance-controller`.

## Required Inputs

- Billing event ledger with `verdict_ref` (`ai-agent-attempted-vs-completed-billing`).
- Pricing-resolution trace (`ai-agent-pricing-engine`).
- Refund decisions (`ai-agent-abandonment-and-refund-policy`).
- SLA credit decisions (`ai-agent-sla-credit-automation`).
- Stripe invoice + payment data.
- Existing chart of accounts (`saas-accounting-system`).
- Auditor's view on agent revenue (often new territory; engage early).

## Workflow

1. Read this `SKILL.md`.
2. Decide **point-in-time vs over-time** per agent feature (§1). See `references/asc-606-for-agents.md`.
3. Model **deferred revenue** for prepaid task credits (§2). See `references/deferred-revenue-and-refund-reserves.md`.
4. Size the **refund reserve** (§2 cont.).
5. Wire **revenue de-recognition** on dispute / refund (§3).
6. Stand up the **month-end close pipeline** (§4). See `references/month-end-close-pipeline.md`.
7. Engage **auditor review** (§5) — most agent-revenue models are new and auditors must sign off.
8. Apply anti-patterns (§6).

## Quality Standards

- Every agent-revenue dollar maps to a specific resolved task or attempted-only task; auditors can reach the task in < 5 minutes.
- Deferred revenue balance reconciles with prepaid-credit balance to within 0.5% per tenant per period.
- Refund reserve is sized from a rolling 90-day refund rate per class; underweight reserve triggers an alert at 80% utilization.
- Revenue de-recognition events are idempotent; never double-derecognize.
- Month-end close completes for agent revenue within 3 business days of period end.
- Auditor sign-off recorded on the revenue policy doc; re-signed annually or on material change.
- Revenue policy is documented per feature, version-pinned, and stored alongside the pricing rules.

## Anti-Patterns

- Booking revenue on `agent.task.completed` (runtime claim). Tax/audit risk.
- Booking revenue on Stripe charge.succeeded. Cash basis on an accrual-required model.
- Recognizing prepaid credit packs as revenue at sale. Defers no revenue.
- No refund reserve. P&L is overstated; first refund spike causes a restatement.
- Different revenue policy in two systems (e.g., legacy GL + new agent pipeline). Reconciliation impossible.
- "We'll let the accountants figure it out at year-end." Engages auditors after-the-fact; audit finding likely.
- Per-feature policy invented by engineering without finance review.
- Forgetting IFRS 15 differs from ASC 606 in some details when both apply (multi-jurisdiction SaaS).

## Outputs

- Per-feature revenue policy (point-in-time vs over-time, recognition trigger, deferral logic).
- Deferred revenue ledger schema.
- Refund reserve sizing formula.
- Revenue de-recognition handlers.
- Month-end close pipeline.
- Auditor-facing policy document.

## Evidence Produced

| Category | Artifact | Format | Example |
|---|---|---|---|
| Compliance | Revenue policy per feature | Markdown | `docs/finance/agent-revenue-policy.md` |
| Architecture | Deferred revenue + reserve schema | SQL | `docs/finance/agent-revenue-schema.md` |
| Operability | Month-end close pipeline | Markdown + code | `docs/runbooks/agent-revenue-month-end.md` |
| Audit | Auditor sign-off record | Signed doc | `docs/finance/auditor-signoff-2026.pdf` |

## References

- `references/asc-606-for-agents.md` — ASC 606 / IFRS 15 application to agent products.
- `references/deferred-revenue-and-refund-reserves.md` — schema, ledger postings, refund reserve sizing.
- `references/month-end-close-pipeline.md` — close steps, reconciliations, journal entries.
- Companion: `saas-accounting-system`, `accounting-finance-controller`, `subscription-billing`, `ai-agent-attempted-vs-completed-billing`, `ai-agent-pricing-engine`, `ai-agent-abandonment-and-refund-policy`, `ai-agent-sla-credit-automation`, `stripe-payments`.

<!-- dual-compat-end -->

## §1 Point-in-Time vs Over-Time

ASC 606 / IFRS 15 require revenue to be recognized when (or as) the entity transfers control of a good or service to the customer.

For agent products, the default per-feature default is:

| Feature pattern | Recognition | Reasoning |
|---|---|---|
| Synchronous one-shot resolution (support_copilot) | point-in-time at `agent.resolution.completed` | Control transfers when the customer receives the resolved outcome. |
| Long-running multi-hour task (log_investigator) | point-in-time at `agent.resolution.completed` | Final deliverable is the diagnosis; intermediate progress has no standalone value. |
| Multi-hour task with milestone deliverables | over-time, milestone-based | If the customer receives intermediate value (e.g., a partial report), recognize per milestone. |
| Code change agent (PR opened, merged, monitored 7d) | point-in-time at `final verdict` (after 7d revert window) | Control transfers when the resolution is confirmed (not reverted). |
| Subscription with included resolutions | over-time (subscription) for the base; point-in-time for overage | The subscription provides standby capacity; recognized ratably. Overage is point-in-time. |
| Prepaid task credits | over-time as credits are consumed → at resolution | Deferred at sale; recognized as resolutions consume credits. |

Detailed framework in `references/asc-606-for-agents.md`.

## §2 Deferred Revenue and Refund Reserves

### Deferred revenue

Prepaid task-credit packs sit as a liability until consumed:

```
DR Cash $99    CR Deferred revenue (agent credits) $99
```

On resolution that consumes credits:

```
DR Deferred revenue $5    CR Agent revenue (resolved) $5
```

Schema and reconciliation in `references/deferred-revenue-and-refund-reserves.md`.

### Refund reserve

Sized from rolling 90-day refund rate per class, weighted by class severity. Updated monthly.

```
reserve_pct = sum(class_refund_rate * class_weight)
```

Posting at booking:

```
DR Refund expense (estimate) $X    CR Refund reserve (liability) $X
```

When a refund is issued, the reserve is consumed; the difference between actual and estimate is a true-up.

## §3 Revenue De-Recognition on Dispute / Refund

When a verdict is overturned, or an abandonment refund is issued for a previously-booked resolution:

1. Identify the original revenue posting (via `billing_events.verdict_ref` or `agent_refunds.task_id`).
2. Determine if the revenue was already recognized (point-in-time → yes; over-time → check schedule).
3. Post a reversal entry. Idempotent on `(task_id, reversal_reason)`.
4. Update the refund reserve true-up.

```
On dispute overturned (resolved → unresolved):
DR Agent revenue (resolved)  $X    CR Refund payable $X
DR Refund payable            $X    CR Cash / customer balance $X
```

The pipeline implementation lives in the close service (§4).

## §4 Month-End Close Pipeline

End-to-end pipeline that runs at period close:

1. Freeze the close cutoff at 23:59:59 of the last day of the period (UTC).
2. Snapshot all `billing_events`, `agent_refunds`, `sla_credit_decisions`, `pricing_resolutions` rows with `occurred_at < cutoff`.
3. Process **late verdicts**: if a verdict for a task in the period lands within 3 business days after cutoff, post into the closed period; after that, post to the open period with a note.
4. Compute aggregate journal entries by feature, by class, by currency.
5. Update deferred revenue balance (drained or accrued).
6. Compute refund reserve true-up.
7. Post journal entries to the GL.
8. Run reconciliations (Stripe vs. ledger; resolution count vs. revenue; refund cash vs. reserve).
9. Publish the close package: trial balance for agent revenue, per-feature breakdown, audit hooks.
10. Auditor preview report generated for material variances.

Detailed steps in `references/month-end-close-pipeline.md`.

## §5 Auditor Engagement

Agent revenue is **new territory** for most external auditors. Engage early:

- Share the per-feature policy doc 60 days before first audited close.
- Walk through one resolved task end-to-end: contract → task → verdict → bill → revenue posting → refund reserve → close JE.
- Document the auditor's reasoning in writing; re-sign annually.
- For multi-jurisdiction tenants, confirm both ASC 606 (US-GAAP) and IFRS 15 stances; details differ on variable consideration estimation.

Findings to expect (typical):
- Verdict gate latency could affect cutoff. Define a 3-business-day allowance and document it.
- Refund reserve sizing methodology must be defensible.
- Prepaid-credit deferral schedule must reconcile per tenant.
- SLA credits must be classified as variable consideration adjustment (not marketing expense).

## §6 Anti-Patterns

- Recognizing revenue on runtime claim.
- Recognizing prepaid credit packs at sale.
- No refund reserve.
- Revenue policy invented by engineering only.
- "Cash basis on accrual books" mismatch.
- Late verdict ignored or silently overwriting closed period.
- Two systems (legacy + agent pipeline) with different policies.
- Mixing ASC 606 and IFRS 15 logic in one code path without clear documentation.
- Auditor engaged 2 weeks before close.


