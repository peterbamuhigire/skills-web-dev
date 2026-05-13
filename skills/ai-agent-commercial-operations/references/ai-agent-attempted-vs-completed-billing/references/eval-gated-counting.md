# Eval-Gated Counting

The principle: **the runtime's terminal state is never the billing trigger.** Only the verdict pipeline's `agent.resolution.completed` event triggers a "completed" bill.

## Why

The agent claims completion. We bill on independent verification. Without the gate:
- A confidently-wrong agent generates revenue and dispute volume.
- The "completion rate" on the dashboard is the agent's self-report — meaningless.
- SLA breach detection (which uses the verdict) and billing diverge.
- Premium pricing collapses because the customer cannot trust the number.

## States

```
                    runtime state                 verdict state
agent.task.created       QUEUED                        n/a
agent.task.started       PLANNING / ACTING ...         n/a
agent.task.completed     COMPLETED                     pending
                            │
                            ▼
                   judge cascade decides
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
   resolved            unresolved          indeterminate
   final               final               final
   (or tentative)      (or tentative)
        │                   │
        ▼                   ▼
agent.resolution     agent.resolution
   .completed          .unresolved
        │                   │
        ▼                   ▼
   full bill            partial-or-no bill
```

## Tentative vs Final

Some signals only settle after a wait:

| Signal | Wait | Used in feature |
|---|---|---|
| no_reopen_within_72h | 72h | support_copilot |
| not_reverted_within_7d | 7 days | code_change_agent |
| customer_csat_received | 7 days | any with CSAT |

Tentative behaviour:

```
tentative resolved   →   dashboard shows "pending confirmation"
                     →   billing: WAIT (default)
                              or BILL_NOW (per-feature opt-in)
                     →   on final: confirm / reverse if changed
```

The default is **wait**. Premature billing on tentative leads to "we charged you, then refunded you" UX that destroys trust.

Per-feature opt-in `bill_on_tentative: true` is allowed for short waits (≤ 24h) where the reversal rate is < 1%. The opt-in must include the reversal-rate measurement and a quarterly review.

## Indeterminate

A small fraction of tasks will get `indeterminate`. These are not billed at full or partial; they sit in an investigation queue.

Triggers:
- Heuristic and judge both abstain (low confidence on both).
- Human reviewer ticked "cannot determine".
- Trace truncated; bundle missing required signal.

Operational targets:
- Indeterminate rate < 2% steady-state.
- Above 5% in a 7-day window opens an investigation; either the contract is ambiguous or the bundle pipeline is dropping signal.

## Idempotency Semantics

`billing_event.idempotency_key = "bill:{task_id}:{PIPELINE_VERSION}"`.

A verdict can produce **at most one** active billing event per pipeline version. Reversals are linked by `task_id` and carry a different key.

Pipeline version bumps:
- Only when the billing math itself changes (e.g., new intervention class, new partial-bill share).
- Bumping the pipeline version causes the *next* verdict event for a task to write a new event (and the prior event must be explicitly voided in a migration).
- Never bumped silently.

## Late Verdicts

A judge cascade may complete hours after the runtime emits `agent.task.completed` (especially when human verification triggers). The consumer is event-driven, so the bill writes whenever the verdict arrives.

For invoice cut-off: if the verdict lands *after* the invoice period closes, the bill goes on the *next* invoice. The `occurred_at` is the verdict event time (not the runtime event time) for the purpose of period assignment.

Edge case: a task spans two invoice periods. The verdict event's `occurred_at` decides which period it bills in. Customers prefer "billed in the period the work was done", but auditors require "billed when the verdict was issued". The latter wins; document it on the SLA page.

## Combining With Token / Credit Metering

`ai-usage-metering-and-billing` continues to meter tokens / credits / generations independently. Those are about *consumption*. The attempted-vs-completed pipeline is about *outcome value*.

A typical agent invoice has both:

```
Pro plan                                                     $149.00
AI credits overage – 3,240 credits @ $0.015                   $48.60
Agent resolutions – support_copilot – 142 tasks @ $1.20      $170.40
Agent attempted-only – support_copilot – 18 tasks @ $0.12      $2.16
```

The two metering models do not conflict. They answer different questions:
- credits / tokens: "how much LLM did you use?"
- resolutions / attempts: "how much *value* did you receive?"

Premium positioning prefers the second; budget positioning prefers the first; sophisticated pricing uses both with a fairness rule (described in `ai-agent-pricing-engine`).

## Migration From Naive Billing

If currently billing on `state==COMPLETED`:

1. Ship the verdict pipeline (`ai-agent-task-success-tracking`) in shadow mode for 30 days.
2. Compare runtime-completion vs verdict-resolved rates; expect the latter to be 5–15pp lower.
3. Re-price with the new rate: target equivalent margin at the lower count, or charge a higher per-resolution price for the lower count.
4. Announce the change with the new SLA and dashboard.
5. Cut over the billing consumer to the verdict event.
6. Run reconciliation for the first two cycles; expect higher dispute volume in cycle 1 (customers notice "attempted-only" lines for the first time).
7. After cycle 2, the dispute volume should drop below the pre-migration baseline because customers see the gate is honest.

## Anti-Patterns

- Billing on the runtime claim. Loses pricing power.
- Tentative bills with later true-up. Looks chaotic.
- Indeterminate counted as either resolved or unresolved by default. Hides a real signal.
- Pipeline version not in idempotency key. Bug-fix migrations either double-bill or fail to re-bill.
- Verdict pipeline running on a separate clock from billing. Late verdicts drop on the floor.
