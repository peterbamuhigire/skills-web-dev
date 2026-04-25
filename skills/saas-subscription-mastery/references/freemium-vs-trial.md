# Freemium vs Free Trial vs Paid vs Reverse Trial

A pricing-motion decision, not a marketing decision. The wrong motion produces a full funnel of the wrong users.

## Decision matrix

| Factor | Freemium | Free trial (time-boxed) | Paid-first | Reverse trial |
|---|---|---|---|---|
| Time-to-value | Long OK | Must be < trial length | Any | Any |
| Marginal cost per free user | Near-zero | Low (bounded by trial) | N/A | Low |
| Viral / collaboration loop | Strong fit | Weak | N/A | Moderate |
| Enterprise / procurement | Poor fit | Moderate (with POC) | Strong fit | Moderate |
| Conversion transparency | Opaque — many never pay | Forces decision at day N | Strong commitment | Forces decision at day N |
| Funnel complexity | Simple front door | Credit card at trial end adds friction | Standard | Complex lifecycle |
| Best for | Broad consumer or bottom-up B2B | Products with obvious value window | High-ACV, relationship sales | Known high-intent users |

## When to choose each

### Freemium

- Value compounds with usage (collaboration, network, data).
- The free tier is genuinely useful on its own (not a crippled demo).
- Marginal cost per free user is close to zero (no heavy compute, no human support).
- You have a monetisation lever (usage caps, team size, premium features) that kicks in predictably.
- The free tier acts as a product-led growth engine — referrals, word-of-mouth, SEO.

Examples: Slack, Notion, Figma, Canva, Zoom, GitHub.

### Free trial (time-boxed)

- Value is obvious and can be delivered within a fixed window (7–30 days).
- Scarcity / deadline pressure drives the conversion decision.
- Full product experience during trial beats a restricted free tier.
- Card-up-front trial qualifies intent — only users who will pay enter.
- Card-free trial widens the top of funnel — but conversion is lower and drop-off at card capture is painful.

### Paid-first

- High-ACV enterprise sales where procurement requires a contract.
- Product-led experimentation isn't feasible (complex onboarding, regulated industry).
- Reputation, category position or brand sells the product.
- POC / pilot model replaces the trial — paid, scoped, time-boxed.

### Reverse trial

- Start the user on the paid tier, with full features, at sign-up.
- At day N (7–14 typical), downgrade to free if no conversion.
- Best when you know the user population will mostly abandon, but you want them to see the upper-tier value first.
- Requires clear communication ("you are on Pro for 14 days, then switch to Free unless you upgrade").

Examples: Notion for teams, LinkedIn Premium, some Grammarly plans.

## Reverse trial mechanics

- Day 0 — sign-up. User is marked `plan = pro, trial_end = now + 14d`.
- Day 3 — in-app reminder of which features are Pro (so they notice what they'll lose).
- Day 10 — email + in-app: "4 days left — you've used X Pro features N times. Keep them for 10 GBP/mo."
- Day 14 — if no upgrade: auto-downgrade to free, feature gating applies. Clear, gentle messaging. Keep data.
- Day 30 — win-back offer if no upgrade after downgrade.

Key rule: never punish the downgrade. The user must remain able to keep using the free tier without friction; the conversion argument is value, not coercion.

## Usage restrictions in freemium

Pick one primary axis, at most two:

- **Quota** — X free events, projects, seats, GB.
- **Feature gates** — core is free, advanced / administrative features are paid.
- **Collaboration** — solo free, team paid.
- **Time history** — 30 days free, unlimited paid.
- **Support** — community-only free, priority paid.

Avoid mixing 4+ axes. Users can't predict when they'll hit the wall, conversion becomes noisy, pricing page bloats.

## Trial length optimisation

- Test 7, 14, 21, 30 days. Length should map to average time-to-value + a buffer of 1 week.
- Short trials (7 days) force urgency; suit products with fast TTFV.
- Long trials (30 days) suit team rollouts or products that need a full cycle (e.g. monthly reporting).
- Extensions — automatic offer of +7 days when user hasn't activated can lift conversion 10–20%; overuse encourages procrastination.
- Credit card requirement reduces top-of-funnel by 40–70% but raises trial-to-paid by 2–5x.

## A/B testing the pricing page

Variables worth testing (one at a time, not all at once):

- Plan count (2 vs 3 vs 4).
- Plan ordering (cheapest first vs highlighted middle tier).
- Annual vs monthly default toggle.
- Currency and price formatting (49 vs 50 vs 49.99).
- Feature-row emphasis vs outcome rows.
- FAQ placement.
- Social proof (logos, quotes, usage stats).
- Primary CTA text ("Start free", "Try 14 days", "Get started").

Design rules:

- Sample size: minimum 500 conversions per variant; at SMB SaaS rates that is often 4–8 weeks.
- Metric: trial-to-paid or paid-sign-up rate, not sign-up rate alone (otherwise you optimise for junk).
- Segment by traffic source — paid traffic behaves differently from organic.
- Don't run A/B pricing changes during launch, rebrand, or outage weeks.

## Mixing motions

The default rule is: pick one. Mix only when segments are clearly different:

- SMB self-serve freemium + enterprise sales-led paid-first is a common dual motion.
- Consumer freemium + prosumer paid trial can work if the flows are separate (distinct pricing pages).
- Never show all three on one page — it confuses conversion.

## Cross-references

- `pricing-model-decisions.md` — flat vs seat vs usage vs tiered.
- `activation-onboarding.md` — how to make trials convert.
- `software-pricing-strategy` — value-based pricing principles.
