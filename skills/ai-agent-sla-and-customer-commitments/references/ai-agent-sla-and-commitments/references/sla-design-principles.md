# SLA Design Principles for Agent Products

## A good SLA does three things

1. **Aligns vendor and customer incentives.** The vendor is paid for outcomes the customer values; missed outcomes cost the vendor money.
2. **Is enforceable without legal argument.** Numbers, counters, queries. A breach is computable, not arguable.
3. **Tells the customer what to expect, in their language, before they sign.** Resolution rate, time-to-resolve, "the agent won't do irreversible things off-script" — not API uptime.

## The five questions every clause must answer

| Question | Failure mode if unanswered |
|---|---|
| What is the counter? | "We thought we had it; we don't." Breach uncountable. |
| What is the window? | Rolling 30d vs. calendar month vs. lifetime — credit math differs by orders of magnitude. |
| What is the breach threshold? | Disagreement on first call; arbitration. |
| What is the credit formula? | Finance writes a number under pressure. |
| What is the evidence pack? | Customer disputes; we have no proof. |

If any answer is missing, **delete the clause** until the answer is shipped.

## The hierarchy of agent commitments

From lowest-trust to highest-trust:

1. **Availability** — "the door opens". Necessary, not sufficient. A 100%-up agent that resolves 60% is worse than a 99%-up agent that resolves 90%.
2. **Time-to-respond / time-to-acknowledge** — easy to measure, easy to game (a polite stall passes).
3. **Time-to-resolve** — meaningful only if "resolve" is defined.
4. **Resolution rate** — the headline metric for an agent product.
5. **Intervention rate ceiling** — autonomy claim; lower is better.
6. **Irreversible-incident count** — trust claim; zero target.

Premium agents commit at the top of the hierarchy. Commodity agents commit at the bottom.

## Per-tier discipline

| Tier | What it should commit to | What it should not commit to |
|---|---|---|
| Free | nothing | anything |
| Starter | availability + display-only resolution | credit-bound resolution rate |
| Pro | availability + resolution + irreversible (zero) | bespoke intent SLAs |
| Business | + time-to-resolve p95 | per-customer intent guarantees |
| Enterprise | bespoke per intent, per data residency, per agent feature | a generic global commitment |

Tier differentiation **must** show up in the SLA, not only in the feature list. Otherwise the SLA is a cost center, not a pricing lever.

## "Display-only" is a feature

Show the customer the resolution rate even when you do not credit on breach. Two reasons:
1. Builds trust through transparency.
2. Trains the buyer to expect numbers; this is how you move them up-tier.

A Starter customer who sees "your support copilot resolved 72% this month" with a tooltip "Pro commits to 85% with automatic credit" is converting themselves.

## What never goes in an SLA

- **Adjectives.** "Reasonable", "best-effort", "industry-standard", "robust", "appropriate".
- **Vendor discretion clauses.** "Excluded at vendor discretion" makes the SLA a marketing device.
- **Open-ended force-majeure.** Enumerate or delete.
- **Single-number averages where p95 exists.** Tail-blind.
- **Commitments to internal quality.** "Our model will be the best available" is unmeasurable.
- **Promises that contradict the runtime.** If `agent.task.budget_exceeded` is a normal terminal state, the SLA cannot promise 100% resolution.

## Hard rule: no SLA before the counter ships

The order is:
1. Counter ships to production.
2. Counter accumulates 30 days of clean data.
3. Engineering measures distribution; sets a defensible floor at p50 or above.
4. Finance computes credit liability against that floor.
5. Proposal engine drafts contract language using the SLA-class table.
6. SLA goes on the public page.

Reversing this order means the first customer to invoke the SLA finds an empty database.

## Bespoke (Enterprise) discipline

Enterprise SLAs are negotiated. Discipline:

- All bespoke clauses follow the same five-question test.
- All bespoke clauses land in `tenant_sla_overrides`, never in a side-letter that engineering cannot read.
- All bespoke clauses are referenced by `contract_ref` to the proposal/contract document for audit.
- Bespoke ≠ vague. A bespoke clause is **more specific** than a generic clause, not less.

Bad bespoke: "99% support copilot accuracy."
Good bespoke: "≥ 92% resolution rate on intent class `refund-inquiry` over rolling 30 days, measured by judge-cascade verdict, eu-west-1 region, eval golden set rev 2026-04. Credit: 12% of MRR per breach event, no cap."

## Common failure modes

- **The "round number" SLA.** Numbers like 99.9% chosen because they look serious, with no measurement-distribution data behind them.
- **The "match the competitor" SLA.** Mirrors a competitor's number without their cost structure; first breach wipes margin.
- **The "we'll set it after launch" SLA.** Launches without SLA. Enterprise deals stall. Finance refuses to model COGS.
- **The "100% irreversible" SLA without a tool catalogue.** Promises zero off-script irreversibles before tool gating exists.

## Cross-engine handoff summary

- **Proposal engine** receives: `sla-class-table.md`, public-page snippets, per-tier credit formulas. Writes the contract language.
- **Business-plan engine** receives: per-tier credit cap, expected breach frequency from production data, contribution-margin impact. Models SLA cost into pricing.
- **This engine** owns: counters, queries, breach detection, credit pipeline, dashboard.

If the three engines diverge — e.g., proposal commits to a number this engine cannot measure — the discrepancy is a launch-blocker, not a doc fix.
