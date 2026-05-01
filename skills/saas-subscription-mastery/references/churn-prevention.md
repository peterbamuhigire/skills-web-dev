# Churn Prevention

Churn is the tax that compounds against every growth lever. Every 1% of monthly churn prevented is roughly 12% more annual revenue retained. Prevention is cheaper than acquisition by an order of magnitude.

## Types of churn

- **Voluntary churn** — user chooses to cancel, downgrade, or lapse.
- **Involuntary churn** — payment fails, card expires, no update. Often 20–40% of total; see `subscription-billing` dunning.
- **Logo churn** — customer accounts lost.
- **Revenue churn** — MRR / ARR lost (can differ sharply from logo churn when customers downgrade but don't cancel).
- **Gross churn** — before expansion.
- **Net churn** — after expansion; negative net churn means expansion > churn (target).

## Early-warning signals

Track these as account-level signals with a weighted health score.

### Usage signals

- Login frequency drop vs the account's own 4-week baseline (not vs global average).
- Active-user count drop (seat usage down).
- Feature breadth reduction — core feature not used in 14+ days.
- Integration disconnect — SSO, data source, webhook failures.
- Export / data-download spike — classic pre-cancellation move.

### Support signals

- Ticket spike, especially tickets mentioning "cancel", "refund", "competitor".
- NPS / CSAT drop (detractor).
- Explicit feature request that matches a competitor differentiator.

### Commercial signals

- Invoice unpaid past 7 days.
- Card about to expire with no update.
- Seat reductions at renewal without prior discussion.
- Champion / primary contact changed roles or left (LinkedIn signal).
- Contract downgrade request.

### Behavioural signals

- Help-centre searches for "cancel", "delete account", "export data".
- Login from new geography or IP pattern (account-takeover risk, not churn per se).

## Health score design

A simple additive model:

```text
score = w1*usage + w2*feature_breadth + w3*tickets + w4*nps + w5*billing_health
```

- Normalise each input to 0–100.
- Weights calibrated from cohort analysis — run the same inputs on customers who later churned vs retained, pick weights that maximise separation.
- Bucket into Green / Amber / Red.
- Review weekly; trigger CS outreach on Amber, executive outreach on Red.

## Intervention stack

Ordered from lightest-touch to heaviest:

| Tier | Trigger | Intervention |
|---|---|---|
| 1 | 7 days silent | Automated "we miss you" email with the last thing they did |
| 2 | Stalled on activation | In-app tip, 2-minute loom link, chat offer |
| 3 | Health amber | CSM check-in (SMB) or email-only outreach |
| 4 | Health red | Executive / CSM call, roadmap preview |
| 5 | Ticket mentions cancel | Immediate save flow triggered, high-touch response |
| 6 | Enterprise at-risk | Executive sponsor call, on-site visit, contract restructure |

## Cancel flow design

The cancel flow is the highest-ROI piece of product you'll ever ship. It captures intent exactly once; after that the customer is lost.

Recommended structure:

1. **Ask why** — 5–7 reason buckets (too expensive, missing feature, not using, switching, project ended, other). Free-text optional.
2. **Offer pause** — 1–3 months pause, billing paused, data retained.
3. **Offer downgrade** — cheaper tier, preserve core value.
4. **Offer discount** — bounded (once per account, expires).
5. **Offer assisted migration** — "schedule 20 minutes with a specialist".
6. **Confirm cancel** — clear, one-click confirm. No dark patterns.
7. **Retention follow-up** — at month 1 send a "we've changed X, come back" email.

Rules:

- Never hide the cancel button. FTC and consumer laws increasingly require easy cancel.
- Record every step; the funnel is a goldmine.
- Pause > discount > downgrade as a preference order; discount trains customers to threaten cancel.
- Enterprise cancel flows are contractual and should route to CS immediately.

## Exit surveys

- Ask once, at cancel confirmation.
- Category + free-text, not a 20-question form.
- Forward results to Product, CS, and Marketing weekly.
- Use top-3 reasons to adjust roadmap and onboarding.

## Win-back campaigns

### Segmentation

- By churn reason (price, fit, competitor, champion-left, project-ended).
- By cohort (time since churn).
- By prior ACV / tier.

### Messaging

- "What's new since you left" — product changes that address their reason.
- Time-bound offer (30 days, new plan, migration help).
- Personal outreach for high-ACV accounts.
- Re-onboarding flow that assumes rust, not zero knowledge.

### Timing

- Trigger 30 days, 90 days, 6 months post-cancel.
- Avoid more than 3 touches; past that you're spam.
- Pause win-back if competitor acquisition is public (they've just migrated; wait).

### Success metric

- Win-back rate (percent of churned accounts reactivated in N days).
- Target: 5–15% depending on segment and reason. B2B SMB is usually on the higher side.
- Watch second-churn rate — if won-back customers re-churn within 90 days, the root cause was not addressed.

## Involuntary churn playbook

Detailed in `subscription-billing`, but the basics:

- Pre-expiry email 30 / 14 / 7 days before card expires.
- Retry schedule (smart retries via Stripe / Braintree).
- Dunning email cadence at 0 / 3 / 5 / 7 days past fail.
- In-app banner during grace period.
- Account Updater services (Stripe, Adyen) to catch new card numbers.
- Downgrade to free / paused state on day N+1, don't hard-cancel immediately.

## Anti-patterns

- "Just ship more features" as the churn strategy — usually wrong.
- Cancel flow buried in settings with a phone-only cancellation path.
- No exit survey — lost signal forever.
- Offering a discount as the first save lever — trains customers to threaten cancel.
- No win-back programme — you've paid CAC twice if you reacquire later.
- Treating involuntary churn as a finance problem, not a product problem.

## Cross-references

- `subscription-billing` — dunning, payment retries, grace periods, account updater.
- `retention-point.md`, `activation-onboarding.md` — churn prevention starts at day 1.
- `engagement-loops.md` — active users don't cancel.
