# Experiment Types

Six designs. Pick one before writing the spec. Each has a specific use, specific failure modes, and specific sample-size implications.

## A/A Test

Same variant on both arms. Purpose: calibrate the platform.

- **When to use:** before the first real experiment on a new platform; after major changes to the assignment service, the metric pipeline, or the randomisation code; quarterly as a platform health check.
- **When not to use:** as a routine companion to every A/B test (wasteful; the A/A guarantee is a platform property, not a per-experiment property).
- **Sample-size implications:** same as the equivalent A/B; the point is to verify the platform produces p ≥ 0.05 on a known-null effect.
- **Common mistakes:** running for too short a window to detect SRM; running on traffic that does not reflect real experiment traffic.
- **Scenario:** you just switched experiment platforms from PostHog to an in-house service. Run a 14-day A/A on the primary funnel metric before any A/B. If it returns a "significant" result with no real change, the platform is broken.

## A/B Test

One change, two arms. The default.

- **When to use:** discrete feature changes, copy changes, algorithm swaps with one knob.
- **When not to use:** changes with long-tail effects (use a holdout); removals of mature features (use a reverse experiment); marketplaces with supply constraints (use a switchback).
- **Sample-size implications:** computed from baseline rate, MDE, power (90% typical), confidence (95% typical).
- **Common mistakes:** too many metrics analysed without correction; peeking; novelty effects misread as sustained lift.
- **Scenario:** a new onboarding screen vs the current one, primary metric = day-7 activation rate, run 21 days.

## Holdout Group

Permanently withhold the feature from a small slice (typically 1-5%) to measure long-term cumulative effect.

- **When to use:** features whose value compounds over time — retention features, habit formation, long-term revenue mechanics.
- **When not to use:** isolated UI tweaks where the effect is one-shot.
- **Sample-size implications:** the small slice requires long run times; design for 3-6 month reads.
- **Common mistakes:** letting the holdout leak into feature exposure over time via marketing emails, notifications, or adjacent features.
- **Scenario:** a new gamified streak feature. 5% holdout for 6 months, measure day-90 and day-180 retention deltas.

## Fake Door

Ship a button or entry point for a feature that does not exist yet; log clicks as a demand signal.

- **When to use:** before committing engineering time to a feature of uncertain demand.
- **When not to use:** for features where building the real thing is cheap; for features where a fake door would damage a high-trust workflow (payments, healthcare records).
- **Sample-size implications:** smaller sample needed because click-through is the metric, not a downstream conversion.
- **Common mistakes:** leaving the fake door live longer than 14 days without disclosure; not showing a polite "coming soon" modal on click.
- **Scenario:** add an "Export to Excel" button on a reporting page that shows "Coming in Q2" on click; measure clicks per weekly active reporter to decide whether to build it.

## Reverse Experiment

Remove a feature from the treatment group (opposite of A/B) to prove it still adds value.

- **When to use:** mature features of uncertain contribution; cost-cutting reviews; deprecation decisions.
- **When not to use:** new features (use A/B); features with known regulatory or contractual obligations.
- **Sample-size implications:** often requires longer run times than the original A/B because the effect has already been baked into user behaviour.
- **Common mistakes:** not communicating the removal to support; underestimating user complaints even when the metric result is neutral.
- **Scenario:** a "Recent Activity" widget has been live for 2 years. Remove it for 5% of users for 30 days; if primary metrics and NPS are unchanged, ship the removal globally and save the maintenance load.

## Switchback

Alternate treatment and control over time (e.g., every 30 minutes) across the whole audience.

- **When to use:** marketplaces, supply-constrained systems, pricing algorithms, matching systems — any system where user-level randomisation leaks through shared supply or network effects.
- **When not to use:** features with no cross-user interaction; features where time-of-day variance is extreme and would dominate the signal.
- **Sample-size implications:** the unit of randomisation is the time window, not the user; effective sample size is the number of windows, not the number of users.
- **Common mistakes:** windows too short (bleed-over); windows too long (not enough observations); not modelling day-of-week effects.
- **Scenario:** ride-sharing surge pricing — alternate the new and old pricing algorithms every 30 minutes in a single city, measure completed-ride revenue per hour, run 4 weeks.
