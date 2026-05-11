# Abandonment Taxonomy

Four classes. Mutually exclusive. Deterministically assignable from terminal-state event metadata.

## Class 1: technical

**Definition:** The platform, the agent runtime, or an upstream tool/model failed. The customer expected the agent to be able to complete and we couldn't deliver.

**Triggers (any):**

- `state == KILLED` and `killed_by == operator` and `kill_reason ∈ {incident, kill_switch_engaged, irreversible_action_prevented}`.
- `state == FAILED` and `failure_kind ∈ {provider_outage, tool_unrecoverable, runtime_crash, gateway_timeout, infra_error}`.
- `state == ABANDONED` and `reason == worker_crash_unrecovered`.

**Fault:** platform.

**Refund:** full prepaid units + full fixed fee.

**Customer comms:** apologetic, factual. Reference the trace ID for follow-up.

**Special:** Enterprise tenants get an RCA (root-cause analysis) if the same task class fails repeatedly (`technical / same provider_outage / 3x in 30d` → RCA mandatory).

## Class 2: user-abort

**Definition:** The user (or someone acting on the tenant's behalf) ended the task or let an approval expire.

**Triggers:**

- `state == KILLED` and `killed_by == tenant_user`.
- `state == ABANDONED` and `reason == approval_expired` (user didn't approve in time).
- `state == ABANDONED` and `reason == user_cancelled_in_ui`.

**Fault:** user.

**Refund:** none by default.

**Override:** per-feature contract can opt into partial refund (rare; usually only for tasks that didn't begin substantive work).

**Customer comms:** neutral. Link to policy. No apology — apology in a no-fault scenario reads as weak.

**Edge case:** if the user-abort happened because of misleading UX (e.g., the user thought "cancel" meant "pause"), that's a UX bug, not a refund question. Fix the UX.

## Class 3: out-of-scope

**Definition:** The task should have been refused at intake. The agent attempted, found it couldn't help, and abandoned. The customer paid (or had units deducted) for a task that was never the right tool for the job.

**Triggers:**

- `state == FAILED` and `failure_kind == unsupported_intent`.
- `state == ABANDONED` and `reason == tenant_disabled_required_tool` (intake should have detected the missing tool).
- `state == ABANDONED` and `reason == required_data_unavailable` AND we should have known at intake.

**Fault:** platform (intake).

**Refund:** full prepaid + full fixed fee.

**Customer comms:** apologetic + educational. Explain why the task was out of scope and what feature *would* have handled it (if any).

**Loop fix:** every out-of-scope abandonment is a candidate for an intake-rule fix. Track them per feature; > 2% triggers an intake-rule review.

## Class 4: budget-exceeded

**Definition:** The task hit a step, wallclock, token, or tool-cost budget. The agent stopped cleanly.

**Triggers:**

- `state == BUDGET_EXCEEDED`.

**Sub-classification (matters for refund):**

| Sub-state | Refund |
|---|---|
| Produced no useful partial output | refund prepaid (full) |
| Produced useful partial output | no refund; partial bill via attempted-vs-completed |

"Useful partial output" is judged by the same judge-cascade used for resolution (see `ai-agent-task-success-tracking`); if the partial output passes the contract's `partial_output_useful` check, treat as partial bill, not refund.

**Fault:** shared. Platform sets limits; customer chose to spend up to them.

**Customer comms:** advisory. If they're often hitting the budget, the upgrade prompt should appear.

**Special:** if the tenant had recently lowered their budget (via `tenant_agent_budget_overrides`) and the task would have completed under the previous budget, that is a *customer-caused* situation — no refund.

## Classification Decision Tree

```
terminal_state?
├── COMPLETED → not abandonment; defer to verdict pipeline
├── KILLED
│   ├── killed_by == operator → technical
│   └── killed_by == tenant_user → user-abort
├── FAILED
│   ├── failure_kind ∈ infrastructure-set → technical
│   ├── failure_kind == unsupported_intent → out-of-scope
│   └── failure_kind == other → technical (with `unclassified_review_needed`)
├── BUDGET_EXCEEDED
│   ├── partial_output_useful → not abandonment; partial bill
│   └── else → budget-exceeded
└── ABANDONED
    ├── reason == approval_expired → user-abort
    ├── reason == user_cancelled_in_ui → user-abort
    ├── reason == worker_crash_unrecovered → technical
    ├── reason == tenant_disabled_required_tool → out-of-scope
    ├── reason == required_data_unavailable → out-of-scope (review)
    └── reason == other → technical (with `unclassified_review_needed`)
```

## Worked Examples

### A — Provider outage mid-task

- State: FAILED, failure_kind: provider_outage.
- Class: technical.
- Refund: full prepaid + full fixed fee.
- Comms: "We refunded you because our upstream provider had an outage between <a> and <b>. Trace: <id>."

### B — User waited 6h to approve, didn't

- State: ABANDONED, reason: approval_expired.
- Class: user-abort.
- Refund: none.
- Comms: "Your approval expired. We didn't proceed. To pick up where the agent left off, <link>."

### C — Customer asked the support copilot to write code

- State: FAILED, failure_kind: unsupported_intent.
- Class: out-of-scope.
- Refund: full.
- Comms: "Our support copilot doesn't write code. <Code-change agent> would handle this kind of task."

### D — Log investigator hit 60-step budget; produced no rooted-cause

- State: BUDGET_EXCEEDED, partial_output_useful: false.
- Class: budget-exceeded.
- Refund: full prepaid units.
- Comms: "The task reached its safety limit without finding the root cause. You weren't charged. For deeper investigations, consider the Business tier's larger limits."

### E — Log investigator hit 60-step budget; produced useful root cause

- State: BUDGET_EXCEEDED, partial_output_useful: true.
- Class: not abandonment (treated as resolved via verdict pipeline).
- Refund: none; partial bill via `budget_exceeded_partial` line item.
- Comms: standard success notification with note that the budget was reached.

### F — Operator killed mid-task during incident

- State: KILLED, killed_by: operator, kill_reason: incident.
- Class: technical.
- Refund: full prepaid + full fixed fee.
- Comms: "We stopped your task during a platform incident. We refunded you. Status: <link>."

## Per-Tenant Cumulative Cap

Total refunds (technical + out-of-scope, the platform-caused classes) per tenant per month should not exceed a **safety cap** without manual review. Default: 25% of monthly invoice.

Reaching the cap doesn't *block* further refunds; it routes them through finance pre-approval and opens an investigation (is the tenant being abused by a feature regression? is the tenant abusing refund discovery?).

## Anti-Patterns

- "FAILED → always technical" rule. Misses out-of-scope.
- "BUDGET_EXCEEDED → no refund ever". Misses the "no useful output" case.
- "User-abort gets refund if customer asks nicely". Inconsistent.
- "Unclassified" silently routing to technical. Inflates refund volume; corrupts COGS data.
- Classifier rules embedded in code with no tests. First change of `failure_kind` enum drops the classifier.
- Classifier rules implemented per service. Drift inevitable.
