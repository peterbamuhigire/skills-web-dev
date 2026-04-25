---
name: saas-subscription-mastery
description: Use when building, launching, or scaling a subscription business — model
  design, 29 steps to subscription mastery, retention-point strategy, onboarding/activation,
  engagement loops, churn prevention, expansion, and billing-strategy decisions. Complements
  subscription-billing (billing mechanics), saas-business-metrics (measurement), and
  software-pricing-strategy (pricing).
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# SaaS Subscription Mastery
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Use when building, launching, or scaling a subscription business — model design, 29 steps to subscription mastery, retention-point strategy, onboarding/activation, engagement loops, churn prevention, expansion, and billing-strategy decisions. Complements subscription-billing (billing mechanics), saas-business-metrics (measurement), and software-pricing-strategy (pricing).
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `saas-subscription-mastery` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Release evidence | Subscription business assessment | Markdown doc covering the 29 steps to subscription mastery applied to the current state, retention plan, and growth plan | `docs/business/subscription-assessment-2026-04-16.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
The business-side playbook for subscription businesses — how to design the model, hit the "retention point," build engagement loops, and prevent churn. Covers strategy; leaves billing mechanics to `subscription-billing` and pricing to `software-pricing-strategy`.

**Sources:** *How to Build a Subscription Business — 29 Steps to Subscription Mastery* (Hansen), *Retention Point* (Warrillow / Robbie Kellman Baxter / Rob Bell), *The Instant 2020–2021 Guide on Subscription Billing for SaaS* (John).

## When this skill applies

- Designing a new subscription business or transitioning a one-off product to subscription.
- Churn is higher than you want and you're not sure where to intervene.
- Planning activation / onboarding to drive first-month retention.
- Designing engagement loops, member value, and stickiness.
- Deciding between freemium, free trial, and paid onboarding.
- Planning expansion (upsell, cross-sell, price increase).
- Reviewing a subscription billing provider decision.

## The subscription mindset

One-off sales optimise for the transaction. Subscriptions optimise for the **relationship**:

- Revenue is recognised over time, not at sale.
- Customer value is LTV, not deal size.
- Acquisition is necessary but insufficient — retention is the product.
- Every feature, every email, every support interaction is a retention act.

See `references/subscription-mindset.md`.

## The Retention Point

Customers have a moment where they cross from "trying this" to "committed to this." That's the retention point. Before it, churn is high; after, it's low. Your onboarding job is to get users there fast.

Tactics for finding your retention point:

1. Identify the first 3–5 actions that correlate with long-term retention (cohort analysis).
2. Track each user's progress through those actions.
3. Instrument and intervene when stalls happen.
4. Shorten the path (in time and steps).
5. Make the retention point observable to the user.

Examples of retention points in the wild:

- Slack: team sends 2,000 messages.
- Dropbox: user uploads 1 file on 1 device.
- Netflix: watched a complete show.
- A B2B SaaS: imported one dataset, built one dashboard, shared one link.

See `references/retention-point.md`.

## The 29-step framework (condensed for SaaS)

Hansen's book breaks subscription mastery into 29 steps across four phases:

### Phase A — Foundation (steps 1–7)

1. Subscription fit — is this product a subscription or a purchase?
2. Value promise — what value you deliver per cycle.
3. Ideal customer — narrow to 1–3 personas.
4. Pricing model — subscription tier shape (free/trial/paid, unit vs flat).
5. Positioning — category and differentiator.
6. Brand promise — what you commit to deliver.
7. Channels — how customers find you.

### Phase B — Launch (steps 8–14)

8. Landing page + offer — what converts.
9. Onboarding — time-to-value.
10. Activation metric — the action that predicts retention.
11. Payment capture — frictionless at sign-up.
12. Early-life communication — week 1, week 2 emails.
13. Community — peers who reinforce value.
14. Customer support — response time SLA early.

### Phase C — Growth (steps 15–21)

15. Habit loops — trigger → action → reward → investment.
16. Referrals — customers invite customers.
17. Partnerships — distribution deals.
18. Content marketing — teach, then sell.
19. Expansion offers — upsell, cross-sell.
20. Price increases — compounding revenue without churn spike.
21. Win-back — reactivating churned customers.

### Phase D — Retain and scale (steps 22–29)

22. Segmentation — cohorts by behaviour.
23. Proactive churn prevention — intervene before cancel.
24. Cancel flow — offer alternatives, collect reasons.
25. Customer advisory board — loudest voices reshape the product.
26. Financial discipline — unit economics that scale.
27. Operational reviews — weekly + monthly + quarterly rhythm.
28. Team structure — who owns acquisition, retention, expansion.
29. Long-term roadmap — evolving value to keep paying.

See `references/29-steps.md`.

## Freemium vs free trial vs paid

```text
Freemium    -> value compounds with usage, low marginal cost, free tier is genuinely useful
Free trial  -> value is obvious within N days, time pressure drives decision
Paid        -> purchased on promise + reputation; most mature or enterprise motion
Reverse trial -> starts on paid tier, downgrades to free at N days if no conversion
```

Rule: pick one. Don't mix unless you have clear segments.

See `references/freemium-vs-trial.md`.

## Activation and onboarding

The first 7 days matter more than the next 90 days. Goals:

1. User completes a personally meaningful action (aha moment).
2. User invites at least one colleague or team member (when product is collaborative).
3. User sees value from the product in their workflow.

Tools:

- Product tour (Intercom, Userflow, in-app).
- Empty-state design — never show a blank screen to a new user.
- Checklist of onboarding steps.
- In-app triggers for key actions.
- Week-1 email sequence that reinforces each step.

Measure: time-to-first-value, day-1 / day-7 retention, percent hitting activation.

See `references/activation-onboarding.md`.

## Engagement and habit loops

Habit = trigger → action → reward → investment.

Apply to your product:

- **Trigger** — email, push, calendar, or internal (user opens app at 9 am).
- **Action** — the smallest useful thing to do.
- **Reward** — social, tribal, self-achievement, or informational.
- **Investment** — user adds data, preferences, connections — makes leaving costly.

Measure: daily active users / weekly active users (DAU/WAU), session frequency, feature-depth.

See `references/engagement-loops.md`.

## Churn prevention

**Voluntary churn** — user cancels.
**Involuntary churn** — payment fails. (See `subscription-billing` skill for dunning.)

Early signals of voluntary churn:

- Login frequency drop.
- Seat usage drop.
- Support tickets about core features or cancellation.
- Integration disconnected.
- NPS / CSAT drop.

Intervention playbook:

1. Automated reactivation email after 7-day silence.
2. CSM reach-out after signal fires.
3. In-app banner offering help or guide.
4. Executive sponsor call for enterprise accounts.
5. Pause-not-cancel option in cancel flow.
6. Exit interview — why you're leaving (qualitative + category).

See `references/churn-prevention.md`.

## Expansion — the second revenue lever

Expansion revenue (upsell + cross-sell) is cheaper than acquisition and compounds. Net Revenue Retention > 110% means expansion > churn; NRR > 120% is world-class.

Expansion mechanisms:

- **Usage-based overage** — they use more, they pay more.
- **Seats** — team grows, seats grow.
- **Tiering** — features unlock on upgrade.
- **Add-ons** — complementary products.
- **Price increases** — grandfather existing customers or migrate them carefully.

See `references/expansion-revenue.md`.

## Pricing model decisions

- **Flat** — simplest, easiest to communicate. Works for simple products.
- **Per seat** — aligns with customer team size. Works for collaboration.
- **Usage-based** — aligns with value delivered. Works when value varies widely.
- **Tiered** — feature packaging. Combine with any of the above.
- **Hybrid** — platform fee + usage. Most common in B2B infra.

Avoid: too-many-dimensions pricing (seats × features × usage × region × volume discount). Customers can't do the maths.

See `references/pricing-model-decisions.md` and cross-reference `software-pricing-strategy`.

## Billing provider selection

Decision drivers (most important first):

1. Tax compliance — is the provider a Merchant of Record (Paddle, Lemon Squeezy) or do you manage tax yourself (Stripe, Chargebee)?
2. Geographies — does it support your customer regions, currencies, local payment methods?
3. Subscription lifecycle complexity — prorations, mid-cycle upgrades, trials, pause, coupons.
4. Metered billing — can it handle usage-based precisely?
5. Revenue recognition — does it export RevRec-ready data?
6. Integrations — accounting, tax, CRM.
7. Fees — flat vs percentage vs hybrid.

Common picks: Stripe Billing (flexible, you handle tax), Paddle/Lemon Squeezy (MOR, handles tax), Chargebee (enterprise, mature), Orb (usage-based focus).

See `references/billing-provider-selection.md` and cross-reference `subscription-billing`.

## Financial metrics every subscription business tracks

- **MRR / ARR** — monthly / annual recurring revenue.
- **NRR / GRR** — net and gross revenue retention.
- **ARPU / ACV** — average per user / contract value.
- **CAC** — customer acquisition cost.
- **LTV** — lifetime value.
- **LTV : CAC** — target > 3; world-class > 5.
- **CAC payback** — months to recover CAC; target < 12.
- **Logo churn vs revenue churn** — revenue can be stable while logos leak.
- **Quick Ratio** — (new + expansion) / (churn + contraction); target > 4.

See `saas-business-metrics` for full framework; this skill focuses on what to do about them.

See `references/metrics-quick-reference.md`.

## Anti-patterns

- Treating sign-ups as success — churn at week 1 undoes everything.
- No activation metric — you don't know if onboarding works.
- "We'll retain users by shipping features" — usually wrong; the first feature they need is to find value in what you already have.
- Ignoring involuntary churn (payment failures) — can be 20–40% of total churn; see `subscription-billing` dunning.
- Pricing page that lists features without matching them to customer problems.
- No cancel flow — loses signal, loses save opportunity.
- No customer advisory board at scale — you're guessing.
- Price-increase without preparation — spike in churn.
- Cohort analysis ignored — you can't improve what you don't segment.

## Read next

- `subscription-billing` — billing lifecycle, dunning, tax, refunds.
- `saas-business-metrics` — full metrics framework.
- `software-pricing-strategy` — pricing principles.
- `habit-forming-products` — Nir Eyal's Hook model applied.
- `saas-sales-organization` — how sales fits alongside subscription growth.
- `lean-ux-validation` — validating retention hypotheses before building.

## References

- `references/subscription-mindset.md`
- `references/retention-point.md`
- `references/29-steps.md`
- `references/freemium-vs-trial.md`
- `references/activation-onboarding.md`
- `references/engagement-loops.md`
- `references/churn-prevention.md`
- `references/expansion-revenue.md`
- `references/pricing-model-decisions.md`
- `references/billing-provider-selection.md`
- `references/metrics-quick-reference.md`