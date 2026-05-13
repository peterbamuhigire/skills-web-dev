# Intervention Credit Logic

When a human had to intervene in an agent task, the customer should pay less. This file defines how much less, per intervention class.

## Defaults (configurable per feature)

| Class | Definition | Multiplier |
|---|---|---|
| none | No HITL events on the task | 1.00 |
| light | Exactly one approval, no edits to args, no rejections | 0.85 |
| heavy | Plan edited before approval, OR > 1 approval, OR a rejection that the agent recovered from | 0.30 |
| user_completed | User finished the task manually after agent stopped | 0.00 |

## Source of Truth

The intervention class is computed by the runtime at terminal state, from the HITL audit log (`ai-agent-action-approval-and-hitl`). The classifier:

```python
def classify_intervention(task) -> str:
    hitl_events = audit_log.events_for_task(task.task_id, kinds=[
        'approval.requested', 'approval.approved', 'approval.rejected',
        'approval.edited', 'approval.expired', 'task.user_completed_offline',
    ])

    if any(e.kind == 'task.user_completed_offline' for e in hitl_events):
        return 'user_completed'

    edits = sum(1 for e in hitl_events if e.kind == 'approval.edited')
    rejects = sum(1 for e in hitl_events if e.kind == 'approval.rejected')
    approvals = sum(1 for e in hitl_events if e.kind == 'approval.approved')

    if edits >= 1 or rejects >= 1 or approvals > 1:
        return 'heavy'
    if approvals == 1:
        return 'light'
    return 'none'
```

The classification appears once on the terminal-state event and is immutable thereafter (disputes can re-classify via the dispute flow).

## Per-Feature Overrides

Some features have higher intrinsic HITL expectations (e.g., a `code_change_agent` always requires merge approval). The defaults are wrong for them.

Example override:

```yaml
feature: code_change_agent
intervention_credit:
  none: 1.00              # impossible in practice
  light: 1.00             # one merge approval is the expected flow
  heavy: 0.50
  user_completed: 0.00
```

For `code_change_agent`, the customer paid for an agent that opens reviewable PRs. A clean PR with a single approval is *not* an intervention discount — that's the product.

Example for a high-autonomy feature where any HITL is rare:

```yaml
feature: support_copilot
intervention_credit:
  none: 1.00
  light: 0.80              # any HITL is a noticeable deviation
  heavy: 0.20
  user_completed: 0.00
```

Per-feature overrides live in the **success contract** (so the SLA dashboard and the billing engine see the same values).

## Pricing Math

```
final_unit_price = base_unit_price * volume_multiplier * intervention_factor
```

All factors are multiplied; the result rounds to nearest cent.

Example:
- `support_copilot` Pro base = $1.20.
- Volume tier 2 (101–500) = 0.90.
- Intervention `heavy` = 0.30.
- final_unit_price = $1.20 * 0.90 * 0.30 = $0.324 → $0.32.

The billing event records the full trace.

## Disclosure on the Customer Dashboard

The SLA dashboard shows intervention rate over time. A separate column shows:

```
This 30d:
  Resolved without intervention:    132 tasks  ($158.40)
  Resolved (light intervention):     12 tasks  ($12.24)
  Resolved (heavy intervention):      8 tasks  ($2.88)
  Total billed for resolution:                 $173.52
```

Customers can audit how the discount applies. No magic numbers.

## When Heavy Intervention is Persistent

If a tenant's `heavy` intervention rate trends above 30% for a feature, the SLA dashboard surfaces a contextual recommendation:

```
Your team intervenes heavily in support_copilot tasks (32%). This may
suggest the agent's configuration could be tuned for your workflow.
[Schedule a tune-up]
```

Heavy intervention rate is also an internal alert: the product team has signal that the feature is not working at your tenant's data shape.

## Dispute Re-classification

If a customer disputes the intervention class (e.g., "you said heavy but I didn't edit anything"), the dispute reviewer can re-classify. The billing event is updated through the standard reversal pipeline.

Re-classifications are tracked; a high re-classification rate alerts product to fix the classifier or the audit-log emission.

## Anti-Patterns

- Hard-coding intervention factors in billing code. Use the success-contract values.
- Different factors on the dashboard vs in the billing pipeline.
- Discount only applied at month-end. Should appear on every billing event.
- "User-completed" class never used because product doesn't capture the signal. The runtime *must* emit `task.user_completed_offline` when applicable.
- Intervention class re-computed in two places (runtime classifier and dispute classifier diverge).
- Treating `light` as no-discount because "one approval is expected" — leaks pricing power; instead set the per-feature override.
