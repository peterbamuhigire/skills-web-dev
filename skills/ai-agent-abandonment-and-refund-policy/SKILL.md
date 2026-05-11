---
name: ai-agent-abandonment-and-refund-policy
description: Use when engineering how the platform handles abandoned agent tasks and refunds — classifying abandonment (technical / user-abort / out-of-scope / budget-exceeded), per-class refund triggers, refund execution pipeline, finance accounting hooks, and customer comms templates. Distinct from `ai-agent-sla-credit-automation` (SLA breach credits) by being about per-task abandonment, not aggregate breach.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Agent Abandonment and Refund Policy
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Engineering the **abandonment classifier** that decides why an agent task ended without success.
- Defining **per-class refund policy**: which abandonments refund, how much, on what timeline.
- Implementing the **refund execution pipeline** that flows from classification → finance accounting → Stripe refund / credit balance.
- Wiring **customer comms templates** for each abandonment class (apologetic for tech, neutral for user-abort, educational for out-of-scope, advisory for budget).
- Producing the **refund decision audit row** for finance close and dispute defense.

## Do Not Use When

- The task is aggregate SLA breach crediting — `ai-agent-sla-credit-automation`.
- The task is the runtime terminal-state classification itself — `ai-agent-runtime-architecture` (this skill *consumes* terminal states).
- The task is the bill on the attempted task — `ai-agent-attempted-vs-completed-billing`.
- The task is generic refunds outside agent context — `subscription-billing` + `stripe-payments`.

## Required Inputs

- Agent runtime terminal-state events with reason metadata (`ai-agent-runtime-architecture`).
- Tool catalogue with `scope` annotation (`ai-agent-tool-catalogue-and-action-gating`).
- Token / credit ledger to refund against (`ai-usage-metering-and-billing`).
- Stripe Billing wired (`subscription-billing`, `stripe-payments`).
- Customer-comms templates (`tabler-email-templates`).
- Customer SLA dashboard for refund display (`ai-agent-customer-sla-dashboard`).

## Workflow

1. Read this `SKILL.md`.
2. Apply the **abandonment taxonomy** (§1). See `references/abandonment-taxonomy.md`.
3. Build the **classifier** (§2) — automatic with optional human override.
4. Map class → **refund treatment** (§3).
5. Implement the **refund execution pipeline** (§4). See `references/refund-execution.md`.
6. Wire **customer comms** (§5).
7. Wire **finance accounting hooks** (§6).
8. Apply anti-patterns (§7).

## Quality Standards

- Every abandoned task has a class assigned within 60 seconds of terminal state.
- Classification is **deterministic** — re-running the classifier on the same trace yields the same class.
- Refund decisions are **idempotent on `task_id`**.
- Refunds for technical abandonment execute within 1 business day; out-of-scope within 2; user-abort and budget-exceeded follow the standard policy (often: no refund).
- The customer receives a class-specific notification, never generic "we refunded you".
- Per-tenant cumulative refund volume is visible in the back-office (abuse signal).
- Finance reconciliation: every refund row in `refunds` ties to a Stripe refund or credit-balance entry within 24 hours.

## Anti-Patterns

- Single "abandonment" bucket. Refund policy becomes either too generous (refund everything) or too stingy (refund nothing); both lose customers.
- Refund decisions made by support reps without a class. Inconsistent; auditors object.
- Refund execution via Stripe Dashboard. No audit trail; back-office UI diverges.
- Notification copy is generic. Customers can't tell whether the abandonment was their fault or ours.
- Per-task refund without an aggregate tenant cap. Abuse vector.
- Out-of-scope refunded silently. Customer doesn't learn; same task retries; refund loop.
- Technical abandonment that drops on the floor because no one looked at the queue.

## Outputs

- Abandonment taxonomy with classifier rules.
- Refund-policy table per class per tier.
- Refund execution pipeline.
- Per-class customer-comms templates.
- Finance hooks (deferred-revenue and refund-reserve).
- Operator UI for manual override.

## Evidence Produced

| Category | Artifact | Format | Example |
|---|---|---|---|
| Architecture | Abandonment classifier spec | Markdown | `docs/billing/abandonment-classifier.md` |
| Operability | Refund execution runbook | Markdown | `docs/runbooks/agent-refund-execution.md` |
| Commercial | Per-class refund policy | Markdown | `docs/billing/agent-refund-policy.md` |
| Compliance | Refund decisions audit log | DB | `agent_refunds` |

## References

- `references/abandonment-taxonomy.md` — four-class taxonomy with classification rules + worked examples.
- `references/refund-execution.md` — refund pipeline with Stripe code, comms triggers, accounting hooks.
- Companion: `ai-agent-runtime-architecture`, `ai-agent-attempted-vs-completed-billing`, `ai-agent-sla-credit-automation`, `ai-agent-tool-catalogue-and-action-gating`, `ai-agent-revenue-recognition`, `stripe-payments`, `subscription-billing`, `tabler-email-templates`.

<!-- dual-compat-end -->

## §1 Abandonment Taxonomy

Four classes, mutually exclusive, deterministically assigned.

| Class | Definition | Who is at fault | Refund posture |
|---|---|---|---|
| **technical** | Runtime / tool / provider failure caused abandonment. Customer expected the agent to be able to complete and we couldn't. | platform | full refund of prepaid units consumed |
| **user-abort** | User killed the task or revoked an approval, or the task expired waiting for HITL. | user | no refund (default); per-feature overrides allowed |
| **out-of-scope** | Task was something the agent should have refused at intake (wrong feature, unsupported intent, missing entitlement). | platform (intake) | full refund + comms (apologetic, educational) |
| **budget-exceeded** | Task hit a step / wallclock / cost budget. No usable output. | shared (limits set by platform; usage chosen by user) | refund prepaid only if no usable output AND tenant did not raise the cap |

Full classifier rules in `references/abandonment-taxonomy.md`.

## §2 Classifier

```python
def classify_abandonment(task) -> AbandonmentClass:
    if task.terminal_state == 'KILLED' and task.killed_by == 'operator':
        # Platform-side kill (incident response). Usually technical.
        return AbandonmentClass('technical', 'operator_kill')
    if task.terminal_state == 'KILLED' and task.killed_by == 'tenant_user':
        return AbandonmentClass('user-abort', 'tenant_user_kill')
    if task.terminal_state == 'ABANDONED' and task.reason == 'approval_expired':
        return AbandonmentClass('user-abort', 'approval_expired')
    if task.terminal_state == 'FAILED':
        if task.failure_kind in ('provider_outage','tool_unrecoverable','runtime_crash'):
            return AbandonmentClass('technical', task.failure_kind)
        if task.failure_kind == 'unsupported_intent':
            return AbandonmentClass('out-of-scope', task.failure_kind)
    if task.terminal_state == 'BUDGET_EXCEEDED':
        if task.partial_output_useful:
            return None        # no abandonment classification; partial bill via attempted-vs-completed
        return AbandonmentClass('budget-exceeded', task.budget_dim_breached)
    if task.terminal_state == 'ABANDONED' and task.reason == 'tenant_disabled_required_tool':
        return AbandonmentClass('out-of-scope', task.reason)  # platform should have rejected at intake
    # Default fall-through for diagnostic
    return AbandonmentClass('technical', 'unclassified_review_needed')
```

`unclassified_review_needed` routes to a human queue — never silently dropped.

## §3 Refund Treatment per Class

```
CLASS               PREPAID UNITS REFUND   FIXED FEE REFUND   PARTIAL BILL?      COMMS POSTURE
technical           full (100%)            full (100%)        no                 apologetic + plain
user-abort          none                   none               attempted-only*    neutral
out-of-scope        full (100%)            full (100%)        no                 apologetic + educational
budget-exceeded     full (if no output)    full (if no output) yes (if output)   advisory + upgrade prompt
                    none (if output)       none (if output)
```

*per-feature overrides in success contract.

Tier modifiers (Enterprise contracts can negotiate):
- Enterprise: technical refund includes an SLA-credit add-on (severity-1 RCA expected).
- Pro / Business: standard refund.
- Free / Starter: prepaid refund only if applicable; no fixed-fee refund (they pay no fixed fee tied to the task).

## §4 Refund Execution Pipeline

```
[Terminal state event]
        │
        ▼
[Classify abandonment]
        │
        ▼
[Check refund eligibility]
   - per-class policy
   - per-tenant cumulative cap
   - dispute-state on the task
        │
        ▼
[Compute refund amount]
   - prepaid units used in this task
   - fixed fee allocation if any
   - currency = tenant invoice currency
        │
        ▼
[Idempotency check on task_id]
        │
        ▼
[Stripe refund / credit-balance entry]
        │
        ▼
[Persist agent_refunds row]
        │
        ▼
[Emit agent.refund.issued event]
        │
        ▼
[Trigger customer comms + dashboard banner]
```

Full code in `references/refund-execution.md`.

## §5 Customer Comms per Class

Each class has its own email template. Examples:

- **technical**: "We're sorry — task <id> failed due to a system issue on our end. We've refunded you <amount> and the engineering team is investigating. Reference: <ticket>."
- **user-abort**: "Task <id> was cancelled by you. As noted in our policy, cancelled tasks are not refunded. <Link to policy>."
- **out-of-scope**: "We weren't able to help with <task summary> because it requires <missing capability>. We've refunded you <amount>. Consider <feature> for this kind of work."
- **budget-exceeded**: "Task <id> reached its safety limit and stopped. We've <refunded / not refunded> based on the partial result. To run larger tasks, consider <upgrade option>."

Templates live in `tabler-email-templates` (or analog). Once approved by legal, used unchanged.

## §6 Finance Hooks

Every refund writes:

1. **`agent_refunds` row** — audit + finance.
2. **Stripe refund or credit-balance entry** — money side.
3. **Revenue de-recognition** (via `ai-agent-revenue-recognition`) — if the original billing was already recognized, reverse it.
4. **Refund-reserve update** — reserve burn tracked; threshold breach alerts finance.

A nightly job reconciles `agent_refunds` totals with Stripe refund totals; mismatch > 0.5% alerts finance.

## §7 Anti-Patterns

- Single bucket "abandonment". Causes either over-refund or under-refund; both lose trust.
- Classifier silently routes to "technical" by default. Refund volume balloons; finance can't model it.
- Refund without class-specific comms. Customer doesn't learn what happened.
- Out-of-scope refunded silently, no comms — same task retries.
- No per-tenant cumulative cap on refund volume. Abuse vector.
- Stripe Dashboard refunds — bypass the audit.
- Refunds executed without revenue de-recognition. Books look healthier than reality.
- "We'll do refunds manually for now." First month: chaos.
