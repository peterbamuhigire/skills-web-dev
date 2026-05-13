# ASC 606 / IFRS 15 for Agent Products

This reference applies ASC 606 (US-GAAP) and IFRS 15 (IFRS) revenue recognition principles to agent product revenue. Both standards converge on a five-step model.

## The five-step model

1. Identify the contract with a customer.
2. Identify the performance obligations.
3. Determine the transaction price.
4. Allocate the price to performance obligations.
5. Recognize revenue when (or as) each performance obligation is satisfied.

For agent products, step 2 and step 5 are the interesting ones.

## Step 2 — Identifying Performance Obligations

For a typical agent SaaS, the customer's contract bundles several obligations:

| Obligation | Typical recognition |
|---|---|
| Access to the platform (subscription base) | over-time, ratably |
| A specific bucket of included agent resolutions | over-time as consumed, capped by period |
| Overage resolutions | point-in-time per resolution |
| Prepaid task-credit packs (separately sold) | over-time as credits consumed |
| Custom onboarding or training services | over-time as services performed |
| Bespoke SLA commitments | typically not a separate obligation; affects variable consideration |

The platform subscription and the agent resolutions are **distinct** when the customer could plausibly use one without the other (e.g., low-resolution customers value access; heavy-resolution customers value the resolutions). When they cannot be separated (e.g., free platform with mandatory per-resolution), they are combined.

## Step 3 — Determining the Transaction Price

Components:

- **Fixed consideration:** the base subscription fee.
- **Variable consideration:** the resolutions, attempted-only bills, intervention discounts, SLA credits, abandonment refunds.

Variable consideration must be estimated and **constrained** — the standards require us to estimate only what is "highly probable" not to reverse.

In practice:
- Estimate expected resolutions per period per tenant from history.
- Estimate expected refund rate per class.
- Estimate expected SLA credit rate per tier.
- Apply the constraint: floor the estimate to the 80th-percentile-conservative number.

The constraint matters because over-aggressive estimates lead to revenue reversals later.

## Step 5 — Recognition Timing per Feature

### Synchronous one-shot resolution (e.g., support_copilot, classification agent)

- **Recognition:** point-in-time at `agent.resolution.completed` (verdict='resolved').
- **Reasoning:** the customer obtains control of the outcome at the moment of resolution.
- **Cutoff treatment:** late verdicts (after period cutoff) post to the prior period if within the 3-business-day allowance; otherwise to the current.

### Long-running diagnostic (e.g., log_investigator)

- **Recognition:** point-in-time at `agent.resolution.completed`.
- **Reasoning:** intermediate progress does not have standalone value to the customer; only the final diagnosis does.

### Multi-milestone tasks (rare)

- **Recognition:** over-time, milestone-based.
- **Reasoning:** if the customer receives standalone value from each milestone (e.g., partial deliverables they can act on), recognize per milestone.
- Implementation: success contracts can declare `milestone_recognized` steps; the runtime emits `agent.milestone.completed` events that the revenue pipeline subscribes to.

### Code change agent (PR opened → merged → 7-day quiet period)

- **Recognition:** point-in-time at `final verdict`. The tentative verdict is not the recognition trigger because revert-within-7-days flips the verdict.
- **Reasoning:** control transfers when the outcome is confirmed (not reverted).
- **Implementation:** revenue postings wait for the final verdict event from the success-tracking pipeline.

### Subscription with included resolutions

- **Base subscription:** over-time, ratably, allocated across the period.
- **Included resolutions:** over-time, recognized as consumed within the included bucket.
- **Overage:** point-in-time per resolution.
- **Implementation:** the close pipeline allocates the subscription portion ratably; consumption draws from the included bucket first; overage events post at resolution.

### Prepaid task-credit packs

- **At sale:** deferred revenue (liability).
- **At resolution that consumes credits:** recognized point-in-time per resolution.
- **At end of credit-pack TTL (if any):** subject to breakage policy.
- **Implementation:** see `deferred-revenue-and-refund-reserves.md`.

## SLA Credits

SLA credits are **variable consideration adjustments**, not expenses. They reduce the transaction price for the affected period.

- At the breach event: estimate the credit due (if not already calculable) and adjust revenue (or refund reserve if booked).
- At the credit-note issuance: confirm the adjustment; reconcile the estimate.
- Materiality: in any one period, SLA credits typically run < 1% of agent revenue; if material, they appear on the financials with disclosure.

## Refunds (Abandonment-Triggered)

Refunds for technical / out-of-scope abandonment are revenue reversals when the original revenue was already recognized. For user-abort and budget-exceeded (no refund), there's no accounting impact beyond the original billing not having occurred.

Refund reserve accounting:

```
At booking of resolution:
  DR Refund expense (estimate)  $X
  CR Refund reserve (liability) $X

At actual refund:
  DR Refund reserve             $Y
  CR Cash / customer balance    $Y
  
True-up:
  DR / CR Refund reserve to align estimate vs. actual
```

The reserve is a balance-sheet liability that wobbles around the actual refund rate. Auditors will examine the sizing methodology.

## Contract Modifications

Mid-period plan changes, contract renewals, and bespoke amendments are **contract modifications**. ASC 606 / IFRS 15 distinguish:

- Modification adds distinct goods/services at stand-alone selling price → treat as separate contract.
- Modification changes the price for remaining obligations → prospective adjustment.
- Modification both changes existing and adds new → split.

In practice for agent SaaS, tier changes follow a clean prospective model; bespoke SLA amendments adjust variable-consideration estimates going forward.

## IFRS 15 vs ASC 606 — Differences to Watch

| Topic | ASC 606 | IFRS 15 |
|---|---|---|
| Variable consideration constraint | same conceptual basis | same |
| Onerous contracts | follow ASC 605-35 or new guidance | IAS 37 still applies |
| Licensing | distinct guidance for symbolic vs functional IP | unified guidance |
| Distinct goods | similar tests; differences in collectibility threshold | similar |
| Disclosures | extensive | similar but framed differently |

For multi-jurisdiction SaaS, document both stances in the policy doc.

## Disclosure

Annual statements should disclose:
- Disaggregation of agent revenue by feature and by contract type (subscription / prepaid / overage).
- Contract balances (deferred revenue, refund reserve).
- Remaining performance obligations.
- Significant judgments (constraints on variable consideration, allocation policy).
- Policy for SLA credits and refunds.

Engage the disclosure-writing process with finance / IR at least 60 days before publication.

## Documented Judgments

Three judgments require written rationale in the policy doc:

1. **Allocation:** how the price is allocated between the platform subscription and the per-resolution component when bundled.
2. **Constraint:** how we conservatively estimate variable consideration (refund rate, SLA credit rate).
3. **Distinct services:** which agent features are distinct from each other and from the base platform.

Auditors will read these. Each judgment cites internal data (past 12 months) and is re-signed annually.

## When To Engage The Auditor

- 60 days before the first audited close on the new policy.
- Whenever a new agent feature ships with a non-standard revenue pattern (e.g., true multi-milestone).
- Whenever the constraint estimate moves materially (e.g., refund rate doubles).
- Annual re-signing of the policy doc.

## Common Pitfalls

- Treating SLA credits as marketing expense rather than variable consideration. Mis-classifies operating expense.
- Recognizing prepaid credits at sale. Defers no revenue; auditor finding likely.
- Recognizing revenue on runtime claim (not verdict). Variable consideration not properly estimated; tax/audit risk.
- Ignoring the 3-business-day late-verdict allowance, then booking late verdicts into wrong periods.
- Not engaging the auditor until close week.
