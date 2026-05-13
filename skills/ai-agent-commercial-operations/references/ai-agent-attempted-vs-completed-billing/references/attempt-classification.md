# Attempt Classification — Terminal State → Billing Treatment

Every terminal state, every verdict, every intervention class produces exactly one billing treatment. This is the canonical table.

## Default Matrix

| Runtime terminal | Verdict       | Intervention   | Treatment                | Line-item kind |
|---|---|---|---|---|
| COMPLETED        | resolved      | none           | full                     | resolved_full |
| COMPLETED        | resolved      | light          | partial(0.85)            | resolved_full (annotated) |
| COMPLETED        | resolved      | heavy          | partial(0.30)            | resolved_heavy_intervention |
| COMPLETED        | resolved      | user_completed | none                     | (no row) |
| COMPLETED        | unresolved    | any            | partial(per-feature)     | attempted_only |
| COMPLETED        | indeterminate | any            | none (investigate)       | (no row + queue) |
| FAILED           | n/a           | any            | none (default)           | (no row) |
| FAILED           | n/a           | any            | partial (some features)  | attempted_only |
| BUDGET_EXCEEDED  | tentative resolved* | any      | partial(0.50)            | budget_exceeded_partial |
| BUDGET_EXCEEDED  | unresolved    | any            | none + refund check      | (no row) |
| KILLED           | n/a           | any            | none                     | (no row) |
| ABANDONED (user) | n/a           | any            | none                     | (no row) |
| ABANDONED (tech) | n/a           | any            | none + refund check      | (no row + refund queue) |
| ABANDONED (out-of-scope) | n/a   | any            | none + refund check      | (no row + refund queue) |

*BUDGET_EXCEEDED can still produce useful output; the verdict pipeline judges if the partial output was resolved enough to bill partially.

## Per-Feature Overrides

The default matrix is overridden by the feature's success contract `billing_treatment_*` block.

Example: `code_change_agent` overrides `billing_treatment_on_attempted_unresolved: none` because an unmerged PR has zero customer value.

Example: `log_investigator` overrides `billing_treatment_on_attempted_unresolved: partial(0.20)` because exploratory diagnostic work has some value even without a fix.

## Intervention Class Definitions

From `ai-agent-action-approval-and-hitl`:

| Class | Rule |
|---|---|
| none | No HITL approvals issued |
| light | One or zero approvals, no edits to args |
| heavy | Args edited before approval, OR > 1 approval, OR plan rejected once |
| user_completed | User abandoned the plan and finished manually (closing without approve) |

The runtime emits intervention class with the terminal event. Disputes can re-classify (rare).

## Refund-Check Triggers

Three terminal states route through the refund-check pipeline (`ai-agent-abandonment-and-refund-policy`):

1. ABANDONED (tech) — system failed. Refund any prepaid task credits used.
2. ABANDONED (out-of-scope) — task should have been refused. Refund + comms.
3. BUDGET_EXCEEDED with no resolved output — refund the cost of the failed attempt if the customer was prepaid.

Refund != partial bill. The refund-check pipeline decides if money flows back; the partial-bill mechanism handles the *invoice* side.

## Worked Examples

### Support copilot, easy task

- Runtime: COMPLETED, 4 steps, no HITL.
- Verdict: resolved (judge confidence 0.92).
- Intervention: none.
- Result: `resolved_full`, 1.00 × $1.20 = $1.20.

### Support copilot, heavy intervention

- Runtime: COMPLETED, 6 steps, agent's plan was edited twice.
- Verdict: resolved.
- Intervention: heavy.
- Result: `resolved_heavy_intervention`, 1.00 × $1.20 × 0.30 = $0.36.

### Support copilot, judge says unresolved

- Runtime: COMPLETED, 5 steps, no HITL.
- Verdict: unresolved (response did not address intent).
- Result: `attempted_only`, 1.00 × $1.20 × 0.10 = $0.12.

### Support copilot, customer reopens within 72h

- Runtime: COMPLETED 60h ago, tentative resolved.
- Customer re-opens at +60h with the same intent.
- Verdict updates: unresolved (final).
- If billed already (tentative-bill opt-in): reversal entry written.
- If not yet billed: regular `attempted_only` entry.

### Code-change agent, PR merged then reverted in 5 days

- Runtime: COMPLETED on PR-merge, tentative resolved.
- Revert at day 5: heuristic flips signal.
- Verdict updates: unresolved (final).
- Billing: `attempted_only` with `treatment=none` → **no bill at all** (contract says unresolved → none for this feature).
- If tentative-billed: reversal.

### Log investigator, budget exceeded

- Runtime: BUDGET_EXCEEDED at step 60.
- Final response includes partial findings.
- Verdict: tentative "resolved" possible if findings meet contract.
- If verdict resolved: `budget_exceeded_partial` at partial(0.50) of full price.
- If verdict unresolved: no bill + refund check.

### Killed by operator

- Runtime: KILLED by support staff during incident.
- Result: no bill regardless of verdict.
- The kill audit row links to the billing audit: "no bill due to operator kill at <ts>, ticket <id>".

## State Machine of the Bill

```
                       runtime emits
                            │
                            ▼
           ┌────────────────┴────────────────┐
           ▼                                 ▼
       COMPLETED                  FAILED/KILLED/ABANDONED/BUDGET_EXCEEDED
           │                                 │
           ▼                                 ▼
      judge cascade               classification (with refund check)
           │                                 │
           ▼                                 ▼
  resolved / unresolved /            terminal-state-default
  indeterminate                              │
           │                                 ▼
           ▼                          billing event (none/partial)
   billing event (full/partial/none)         │
           │                                 ▼
           ▼                          (if tech/abandoned: refund queue)
   (if late dispute: reversal)
```

## Customer-Facing Disclosure

The customer SLA dashboard must explain this matrix in plain language:

```
Billing for agent tasks:
- A task we resolved end-to-end is billed at full rate.
- A task where you had to intervene heavily is billed at 30% rate.
- A task we attempted but didn't resolve is billed at 10% rate.
- A task we failed, abandoned, or you killed: not billed.
- A task that exceeded its budget without resolving: not billed; you may be refunded for prepaid credits.
- If you dispute a verdict and we agree, the bill is reversed.
```

This wording is part of the SLA page, written once with legal review, and reused.

## Anti-Patterns

- Different teams using different matrices. Lock the canonical table in the repo.
- Per-feature overrides scattered across code. Keep in success contracts only.
- "Compensatory" line items invented by a CSM at quarter-end. Disrupts the math; ship a contract change instead.
- Treating BUDGET_EXCEEDED as always-failure or always-partial. The verdict still decides.
- Refund-check pipeline downstream of billing rather than alongside. Causes double-handling.
