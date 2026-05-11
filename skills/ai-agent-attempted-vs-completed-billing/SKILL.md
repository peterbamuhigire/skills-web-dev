---
name: ai-agent-attempted-vs-completed-billing
description: Use when engineering the billing pipeline that distinguishes attempted from completed agent tasks. Eval-gated counting — a task counts as "completed" only when the success-tracking verdict is `resolved`. Defines billing treatment per terminal state, intervention-shared-credit, abandonment refunds, and reversibility of bills on dispute. Distinct from `ai-usage-metering-and-billing` (tokens / credits / generations) by being task-level and outcome-conditional.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Agent Attempted-vs-Completed Billing
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Designing the billing pipeline for **per-resolution** or **per-outcome** priced agent products.
- Wiring the **eval-gated counter** — only `success_verdict='resolved'` counts as completed; everything else is attempted-only.
- Setting **per-terminal-state billing treatment** (COMPLETED → full | partial | none; FAILED → none | partial; BUDGET_EXCEEDED → partial; KILLED → none; ABANDONED → none; etc.).
- Handling **HITL intervention sharing** — a heavily-intervened task is not billed at full rate.
- Wiring **dispute reversal** so an overturned verdict reverses the bill.
- Producing the **billing event family** (`agent.resolution.completed`, `agent.resolution.unresolved`, `agent.intervention.recorded`).

## Do Not Use When

- The task is tokens / credits / generations metering — `ai-usage-metering-and-billing`.
- The task is the resolver from event to invoice line item amount — `ai-agent-pricing-engine`.
- The task is the verdict pipeline that decides resolved vs unresolved — `ai-agent-task-success-tracking`.
- The task is refund execution mechanics — `ai-agent-abandonment-and-refund-policy`.
- The task is revenue recognition (when revenue is *earned*) — `ai-agent-revenue-recognition`.

## Required Inputs

- Per-feature success contract with `billing_treatment_on_*` fields (`ai-agent-task-success-tracking`).
- Verdict pipeline emitting `agent.resolution.completed` / `agent.resolution.unresolved` (`ai-agent-task-success-tracking`).
- Pricing engine with per-feature price rules (`ai-agent-pricing-engine`).
- Stripe (or analog) billing wired (`subscription-billing`).
- Agent runtime emitting terminal-state events with HITL summary (`ai-agent-runtime-architecture`, `ai-agent-action-approval-and-hitl`).

## Workflow

1. Read this `SKILL.md`.
2. Map every **terminal state** to a billing treatment (§1). See `references/attempt-classification.md`.
3. Wire the **eval gate** between runtime completion and the billing event (§2). See `references/eval-gated-counting.md`.
4. Build the **end-to-end billing pipeline** (§3). See `references/billing-pipeline.md`.
5. Wire **intervention sharing** (§4) — light intervention vs heavy intervention discounts.
6. Wire **dispute reversal** (§5) — overturned verdict → billing reversal.
7. Wire **partial-bill copy** (§6) — invoice line items must be readable.
8. Apply anti-patterns (§7).

## Quality Standards

- A task is **never** billed at full rate based on the runtime's own `COMPLETED` state. The bill waits for the verdict.
- Billing events are **idempotent on `task_id`** end-to-end.
- Every billed task has a verdict reference; auditors can trace bill → verdict → trace → tool I/O in < 5 minutes.
- Partial bills (attempted-only, intervention-shared) appear as separate invoice line items, not as a discount on a "completed" line.
- Tentative verdicts (e.g., "resolved pending 72h reopen window") *do not* trigger immediate billing unless the contract opts in (rare; explicit per-feature).
- Disputed-overturned verdicts trigger reversal within 1 business day.
- Per-tenant monthly bill is reproducible from `billing_events` rows — no spreadsheet adjustments.

## Anti-Patterns

- Billing on `state == COMPLETED` from the runtime. The agent decided it succeeded; we have to verify.
- Single billing event regardless of terminal state. Customers pay for failed attempts at full rate.
- Charging tentative verdicts. Customer disputes, partial refund chaos.
- Intervention discount applied as a manual post-process. Easy to miss; impossible to audit.
- Reversal pipeline that adjusts old invoices in-place. Use proper credit notes; auditors object to mutated invoices.
- Partial-bill line items labeled as "Discount" (negative line) rather than a distinct "Attempted-only" line (positive, lower).
- Bill on the runtime claim, then "true up" on verdict. Customer sees two charges; second looks like a surprise.

## Outputs

- Terminal-state × billing-treatment matrix.
- Eval-gated counting pipeline (Python).
- Billing event family schema.
- Intervention-sharing logic.
- Dispute reversal pipeline.
- Invoice line-item copy patterns.

## Evidence Produced

| Category | Artifact | Format | Example |
|---|---|---|---|
| Architecture | Terminal-state billing matrix | Markdown | `docs/billing/agent-attempt-classification.md` |
| Release evidence | Eval-gate idempotency tests | CI | `tests/billing/eval_gate_test.py` |
| Operability | Bill-to-trace lookup runbook | Markdown | `docs/runbooks/agent-bill-audit.md` |
| Compliance | Verdict→bill audit chain | DB | `billing_events`+`task_success_verdicts` |

## References

- `references/billing-pipeline.md` — end-to-end pipeline from `agent.resolution.completed` to invoice line item.
- `references/eval-gated-counting.md` — eval gate semantics, tentative vs final, idempotency.
- `references/attempt-classification.md` — every terminal state mapped to billing treatment.
- Companion: `ai-agent-task-success-tracking`, `ai-agent-pricing-engine`, `ai-agent-abandonment-and-refund-policy`, `ai-agent-revenue-recognition`, `ai-usage-metering-and-billing`, `subscription-billing`, `ai-agent-runtime-architecture`, `ai-agent-action-approval-and-hitl`.

<!-- dual-compat-end -->

## §1 Terminal State → Billing Treatment

```
TERMINAL STATE       VERDICT      INTERVENTION   BILL TREATMENT
COMPLETED            resolved     none/light     full
COMPLETED            resolved     heavy          partial(intervention_share)
COMPLETED            unresolved   any            partial(attempted_unresolved)
FAILED               n/a          any            none (or partial; per feature)
BUDGET_EXCEEDED      n/a          any            partial(budget_exceeded_share)
KILLED               n/a          any            none
ABANDONED (user)     n/a          any            none
ABANDONED (tech)     n/a          any            none + refund check
```

Full matrix per feature in `references/attempt-classification.md`. The matrix is per-feature because expensive features may charge a small fee even on FAILED.

## §2 Eval Gate

The runtime emits `agent.task.completed` on reaching the COMPLETED terminal. **This is not the billing trigger.**

The trigger is `agent.resolution.completed`, emitted by the verdict pipeline once the success contract has decided `verdict='resolved'`. If unresolved: `agent.resolution.unresolved`. If indeterminate: `agent.resolution.indeterminate` (very rare; investigate).

```
runtime emits     agent.task.completed
                       │
                       ▼
                  judge cascade  (ai-agent-task-success-tracking)
                       │
              ┌────────┼────────┐
              ▼        ▼        ▼
          resolved  unresolved  indeterminate
              │        │            │
              ▼        ▼            ▼
agent.resolution.completed  /  .unresolved  /  .indeterminate (no bill)
              │        │
              ▼        ▼
       billing event consumer
```

Tentative verdicts (`no-reopen-within-72h`, `not-reverted-within-7d`) wait until final unless feature opts into tentative billing. See `references/eval-gated-counting.md`.

## §3 Pipeline (sketch)

```python
def on_resolution_completed(event):
    contract = success_contracts[event.feature]
    feature_price = pricing_engine.resolve(event)
    intervention = event.intervention_summary   # light | heavy | none
    treatment = contract.billing_treatment_resolved(intervention)
    units = compute_units(treatment, feature_price)
    write_billing_event(
        task_id=event.task_id,
        tenant_id=event.tenant_id,
        feature=event.feature,
        verdict='resolved',
        units=units,
        line_item_kind=treatment.line_item_kind,
        idem_key=f"bill:{event.task_id}",
    )

def on_resolution_unresolved(event):
    contract = success_contracts[event.feature]
    treatment = contract.billing_treatment_attempted_unresolved
    if treatment == 'none':
        return
    units = compute_partial_units(treatment, pricing_engine.resolve(event))
    write_billing_event(
        task_id=event.task_id,
        tenant_id=event.tenant_id,
        feature=event.feature,
        verdict='unresolved',
        units=units,
        line_item_kind='attempted_only',
        idem_key=f"bill:{event.task_id}",
    )
```

Full pipeline in `references/billing-pipeline.md`.

## §4 Intervention Sharing

A task with HITL intervention is not billed at full rate. The treatment is per-feature.

| Intervention class | Definition | Default share |
|---|---|---|
| none | No HITL approvals or edits | full (1.00) |
| light | Approval given without edits, ≤ 1 approval | 0.85 |
| heavy | Plan edited, or > 1 approval | 0.30 |
| user_completed | User finished the task themselves after agent gave up | 0.00 |

Defaults overridable per feature in the success contract.

Rationale: customers should not pay full price for a task that became a copilot rather than an agent. This is also a **dogfood signal** — features with rising intervention rates lose revenue, which forces engineering attention.

The runtime captures intervention summary on every task via `ai-agent-action-approval-and-hitl`.

## §5 Dispute Reversal

When a verdict is overturned (`ai-agent-task-success-tracking` dispute resolution):

```python
def on_verdict_overturned(event):
    original = billing_events.find(task_id=event.task_id, verdict=event.original_verdict)
    if not original:
        return
    # Original bill stays for audit; issue reversal event
    write_billing_event(
        task_id=event.task_id,
        tenant_id=event.tenant_id,
        feature=event.feature,
        verdict=event.new_verdict,
        units=-original.units,
        line_item_kind='reversal',
        idem_key=f"bill:reversal:{event.task_id}:{event.dispute_id}",
        reason_ref=event.dispute_id,
    )
    # Trigger credit-note on next invoice
    stripe.invoice.create_pending_credit_for(
        customer_id=tenant.stripe_customer_id,
        amount=original.amount_for_reversal(),
        memo=f"Dispute reversal — task {event.task_id}",
        idempotency_key=f"reversal:{event.task_id}:{event.dispute_id}",
    )
```

Reversal does **not** mutate the original `billing_events` row. It appends a negative-units event linked by `task_id`. Auditors see the full history.

## §6 Invoice Line-Item Copy

Customer-facing invoice should read in plain language:

```
Pro plan – May 2026                                                $149.00
Agent resolutions – support_copilot – 142 tasks @ $1.20            $170.40
Agent attempted-only – support_copilot – 18 tasks @ $0.12           $2.16
Agent resolutions (heavy intervention) – 7 tasks @ $0.36            $2.52
Service credit per SLA (support_copilot resolution rate breach)    -$7.50
Dispute reversal – task 8821 (refunded $1.20)                      -$1.20
                                                          Total   $315.38
```

Notes:
- Each line maps to one billing-event kind.
- Heavy-intervention tasks appear separately, not as a discount.
- SLA credits appear with the breaching SLA id (matches dashboard).
- Reversals appear with the task ID; customer can drill into the evidence pack.

## §7 Anti-Patterns

- Billing on runtime claim only.
- Single event regardless of terminal state.
- Charging tentative verdicts.
- Intervention discount as a manual post-process.
- Mutating original billing rows on reversal.
- Negative line items labelled "Discount" instead of named precisely.
- Tentative-bill then true-up. Customer sees double charge.
- Eval gate not idempotent. Re-running the consumer double-bills.
