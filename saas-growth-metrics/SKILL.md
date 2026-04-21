---
name: saas-growth-metrics
description: Use when building growth analytics for a SaaS — AARRR funnel, cohort retention
  tables, A/B testing framework, North Star metric selection, feature usage analytics, revenue
  forecasting, and growth-meeting cadence. Complements saas-business-metrics (which covers
  MRR/LTV/CAC financial definitions).
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# SaaS Growth Metrics

<!-- dual-compat-start -->
## Use When

- Use when building growth analytics for a SaaS — AARRR funnel, cohort retention tables, A/B testing framework, North Star metric selection, feature usage analytics, revenue forecasting, and growth-meeting cadence. Complements saas-business-metrics (which covers MRR/LTV/CAC financial definitions).
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `saas-growth-metrics` or would be better handled by a more specific companion skill.
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

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->

## The SaaS Metrics Framework (AARRR)

Dave McClure's AARRR framework (also called *Pirate Metrics*) organises the entire user lifecycle into five sequential stages. Each stage has a leading metric, a cohort lens, and a distinct owner on the growth team.

- **Acquisition** — how users find the product. Leading metrics: visits, sign-ups, cost per visitor, channel attribution. Owner: marketing.
- **Activation** — first value moment (the "aha"). Leading metrics: activation rate, time-to-value, percentage reaching the activation event within 7 days. Owner: product and onboarding.
- **Retention** — users keep coming back. Leading metrics: W1/W4/W12 retention, DAU/MAU stickiness, rolling 28-day active users. Owner: product.
- **Revenue** — users convert to paid and expand. Leading metrics: free-to-paid conversion, ARPU, expansion MRR. Owner: product plus sales.
- **Referral** — users invite more users. Leading metrics: K-factor (invites × conversion), viral cycle time, NPS promoter share. Owner: growth and marketing.

Treat AARRR as a diagnostic funnel: the lowest-converting stage is the current bottleneck, and growth investment should target that stage before tuning stages downstream. A 40% improvement at a 2% activation rate is worth more than a 40% improvement at a 20% paid-conversion rate.

## MRR & ARR

For authoritative MRR, ARR, and NRR definitions, see `saas-business-metrics`. This skill focuses on the analytics layer — how to compute these metrics from raw subscription tables and present them as movement dashboards.

MRR movements break MRR change into five components each month: **new** (new customers), **expansion** (upgrades, seat adds), **reactivation** (churned customers returning), **contraction** (downgrades), and **churn** (cancellations). Ending MRR = Starting MRR + New + Expansion + Reactivation − Contraction − Churn. ARR = MRR × 12 for monthly plans, or annual contract value summed for annual plans.

Complete MRR SQL query from a `subscriptions` table:

```sql
WITH monthly_mrr AS (
  SELECT
    date_trunc('month', period_start) AS month,
    customer_id,
    CASE
      WHEN billing_interval = 'month' THEN amount_cents / 100.0
      WHEN billing_interval = 'year'  THEN amount_cents / 100.0 / 12.0
    END AS mrr
  FROM subscriptions
  WHERE status = 'active'
)
SELECT
  month,
  SUM(mrr)                                                   AS total_mrr,
  COUNT(DISTINCT customer_id)                                AS active_customers,
  SUM(mrr) / NULLIF(COUNT(DISTINCT customer_id), 0)          AS arpu,
  SUM(mrr) * 12                                              AS arr
FROM monthly_mrr
GROUP BY month
ORDER BY month;
```

Render MRR movements as a waterfall chart. Bar order: Starting MRR, +New, +Expansion, +Reactivation, −Contraction, −Churn, Ending MRR. This is the single chart an exec will read first in every board meeting.

## Net Revenue Retention (NRR)

NRR measures whether existing customer revenue grows on its own, independent of new acquisition. Formula:

$$NRR = \frac{\text{Start MRR} + \text{Expansion} - \text{Contraction} - \text{Churn}}{\text{Start MRR}}$$

NRR above 100% means the existing base is a growth engine — even with zero new sales, revenue rises. Best-in-class SaaS benchmarks:

- Bottom quartile: 90–95%
- Median: 100–105%
- Top quartile: 110–120%
- Best-in-class: 120%+ (Snowflake, Datadog, Twilio publicly report in this band)

Track NRR as a trailing 12-month cohort metric, not a single-month snapshot. Pair it with **Gross Revenue Retention (GRR)** — same formula without the expansion term — to separate true retention from expansion-masked churn. If NRR is 115% but GRR is 82%, the business is leaking customers and papering over it with upsells.

## Customer Lifetime Value (LTV)

Simple LTV formula: `LTV = ARPU / monthly churn rate`. For a $50 ARPU with 2% monthly churn, LTV = $2,500.

Segment LTV by acquisition channel — organic, paid search, referral, and outbound sales cohorts have dramatically different LTVs even at identical ARPUs. A customer acquired by referral typically exhibits 30–50% lower churn than a paid-search customer at the same price point.

- **Gross LTV** — top-line revenue over customer lifetime, unadjusted.
- **Net LTV** — gross LTV multiplied by gross margin (typically 70–85% for pure SaaS, lower for SaaS with hosted compute or transaction fees).

Always use Net LTV when computing LTV:CAC ratios. Gross LTV flatters the ratio by ignoring the cost of serving the customer. If gross margin is 75%, a 3:1 LTV:CAC on gross numbers is actually 2.25:1 on net — below the healthy threshold.

## Customer Acquisition Cost (CAC)

Fully-loaded CAC must include every dollar spent to acquire customers over the period:

- Marketing spend (paid channels, content production, events, tools)
- Sales salaries and commissions (SDRs, AEs, sales engineering)
- Marketing salaries (growth, demand gen, content)
- Sales and marketing tools (CRM, marketing automation, intent data, enrichment)
- Allocated overhead for those teams

Compute CAC per channel: `channel_spend / new_customers_from_channel`. Blended CAC is the weighted average — useful for board reporting, misleading for channel decisions.

LTV:CAC ratio targets:

- Below 1:1 — burning money on every customer; stop scaling immediately.
- 1:1 to 3:1 — marginal; optimise before scaling.
- 3:1 — healthy; the industry benchmark.
- 5:1+ — under-invested in growth; you could spend more and still be profitable.

CAC payback period target: under 12 months for SMB (high-velocity, low ACV), under 24 months for mid-market, under 36 months for enterprise. Longer payback requires a stronger balance sheet.

## Churn Analysis

Two orthogonal churn metrics must both be tracked:

- **Logo churn** — count of customers lost over the period. Treats a $10/month customer and a $10,000/month customer identically.
- **Revenue churn** — MRR lost. Weighted by contract size.

A healthy business has revenue churn lower than logo churn — small customers churn faster than large ones, which is the expected pattern. If revenue churn exceeds logo churn, large customers are disproportionately leaving and that is an existential threat.

Compute churn by cohort (signup month) rather than by calendar month alone. Calendar churn mixes tenure effects; cohort churn isolates them and reveals whether a recent product change hurt early-stage retention.

Early warning signals — monitor these 30–60 days before the churn event:

- Declining feature usage (DAU drop of 30%+ versus the customer's baseline)
- Rising support ticket volume, especially tickets tagged "confusion" or "billing"
- NPS score dropping below 7 in a survey or quarterly review
- Key power user leaving the customer's org (admin seat reassigned)
- Invoice payment delays or payment method failures

Pipe these into a customer health score and trigger CS outreach automatically.

## Expansion Revenue

Expansion is the single highest-leverage growth vector because it compounds on an already-qualified customer base. Three expansion motions:

- **Upsell (tier up)** — customer moves from Starter to Pro, or Pro to Enterprise. Drivers: usage limits hit, advanced features needed, compliance requirements (SOC 2, SSO).
- **Cross-sell (new product)** — customer adds a second product from the same vendor. Drivers: adjacent use case, bundled pricing, vendor consolidation.
- **Seat expansion** — customer adds users to an existing subscription. Drivers: team growth, rollout to additional departments, usage-based pricing on active seats.

In Stripe, track expansion via `subscription_item` change events: any `quantity` increase, any `price_id` change to a higher-tier price, or any new item added to an existing subscription. The webhook events `customer.subscription.updated` with diffable item arrays are the authoritative source.

Expansion-dedicated CS or account management typically drives 2–3× the expansion rate of a reactive model. Bake expansion quotas into CSM compensation.

## Funnel Analytics

Standard PLG funnel: **Visit → Signup → Activation → Paid**. Measure conversion rate at every step, not just end-to-end. End-to-end visit-to-paid is a vanity metric; step-level conversion reveals where the funnel actually breaks.

PostHog funnel query example:

```sql
SELECT
  countIf(step_0)                                           AS visited,
  countIf(step_0 AND step_1)                                AS signed_up,
  countIf(step_0 AND step_1 AND step_2)                     AS activated,
  countIf(step_0 AND step_1 AND step_2 AND step_3)          AS paid,
  signed_up / visited                                       AS visit_to_signup,
  activated / signed_up                                     AS signup_to_activation,
  paid      / activated                                     AS activation_to_paid
FROM (
  SELECT
    person_id,
    max(event = '$pageview'        AND url LIKE '%/landing%') AS step_0,
    max(event = 'user signed up')                             AS step_1,
    max(event = 'activation event')                           AS step_2,
    max(event = 'subscription created')                       AS step_3
  FROM events
  WHERE timestamp >= now() - INTERVAL 30 DAY
  GROUP BY person_id
);
```

Benchmarks for a PLG SaaS:

- Visit → signup: 2–5% (cold traffic), 10–20% (warm traffic)
- Signup → activation: 40%+ is healthy; below 25% is a red flag
- Activation → paid: 5–10% for PLG self-serve; 20–40% if sales-assisted
- End-to-end visit → paid: 0.1–0.5% for PLG cold traffic

Activation is the most leveraged step. A 10-point improvement in signup-to-activation typically compounds into a 20–30% revenue lift over six months.

## Cohort Retention Table

The cohort retention table is the single most important retention artifact. Rows are signup-month cohorts; columns are months-since-signup; cells are the percentage of the cohort still active in that month. A retention curve that flattens indicates product-market fit; a curve that keeps declining indicates leaky retention.

Complete cohort retention SQL:

```sql
WITH cohorts AS (
  SELECT
    user_id,
    date_trunc('month', created_at) AS cohort_month
  FROM users
),
activity AS (
  SELECT
    user_id,
    date_trunc('month', event_timestamp) AS activity_month
  FROM events
  WHERE event_name = 'app_opened'
  GROUP BY user_id, activity_month
),
joined AS (
  SELECT
    c.cohort_month,
    c.user_id,
    (extract(year  FROM a.activity_month) - extract(year  FROM c.cohort_month)) * 12
    + (extract(month FROM a.activity_month) - extract(month FROM c.cohort_month))
      AS months_since_signup
  FROM cohorts c
  LEFT JOIN activity a ON a.user_id = c.user_id
)
SELECT
  cohort_month,
  months_since_signup,
  COUNT(DISTINCT user_id) AS active_users,
  COUNT(DISTINCT user_id) * 1.0 /
    FIRST_VALUE(COUNT(DISTINCT user_id)) OVER (
      PARTITION BY cohort_month ORDER BY months_since_signup
    ) AS retention_rate
FROM joined
WHERE months_since_signup >= 0
GROUP BY cohort_month, months_since_signup
ORDER BY cohort_month, months_since_signup;
```

Pivot the output so cohorts are rows and `months_since_signup` are columns. Colour-code the cells (darker = higher retention) to make the flattening visually obvious.

## Feature Usage Analytics

Feature usage is measured across three orthogonal dimensions. Track all three per feature; any one alone is misleading.

- **Usage frequency** — daily, weekly, or monthly active users per feature. A feature used by 80% of MAU is core; a feature used by 5% of MAU is niche or broken.
- **Feature breadth** — average number of distinct features a user touches per period. Wider breadth correlates with retention; a single-feature user is a churn risk.
- **Feature depth** — events-per-feature-per-user per period. A user who fires a feature's core event 50 times per month is qualitatively different from one who fires it twice.

**Stickiness = DAU / MAU**, measured at the product level and per feature. Targets:

- B2B productivity tool: 0.2+ (users return most work weeks)
- B2B daily tool (CRM, helpdesk): 0.5+ (users return most work days)
- Consumer social or communication: 0.5+ (daily habit formed)
- Consumer content: 0.3+

Track the distribution, not just the average. A stickiness of 0.3 with 60% of MAU at near-zero DAU is structurally different from 0.3 evenly distributed — the first is a power-user product with a dormant long tail.

## A/B Testing Framework

Every experiment must have a written hypothesis before it launches. Format: *"If we change X, then Y will improve by Z%, because of causal reason W."* No hypothesis, no experiment.

Sample size calculator inputs: baseline conversion rate, minimum detectable effect (MDE) you care about, statistical power (90% standard), and confidence level (95% standard). Rough formula for two-proportion tests:

$$n = \frac{2 \cdot (z_{\alpha/2} + z_{\beta})^2 \cdot p \cdot (1 - p)}{(\text{MDE})^2}$$

For a 10% baseline conversion and a 1-point MDE (detecting a move from 10% to 11%), you need ~17,000 users per variant at 90% power and 95% confidence. Plug numbers into Evan Miller's calculator or PostHog's built-in sizing before running anything.

Minimum runtime: one full business cycle, typically two weeks. Never call a winner from a 3-day test — weekday-weekend effects, payroll cycles, and novelty effects will mislead you.

Tool examples by stack fit:

- **PostHog Experiments** — free tier, built into product analytics, great for PLG SaaS with existing PostHog instrumentation.
- **GrowthBook** — open-source, SQL-native, strong for teams already running a data warehouse.
- **Optimizely** — enterprise-grade, mature stats engine, best for high-traffic consumer apps.
- **Statsig** — mid-market sweet spot, fast time-to-first-experiment.

## Revenue Forecasting

Three forecasting models, in order of sophistication. Use all three; disagreement between them exposes risk.

- **Simple linear** — `next_month_MRR = current_MRR × (1 + monthly_growth_rate)`. Only honest over a 1–3 month horizon and only when growth rate is genuinely stable. Breaks at inflection points.
- **Cohort-based** — sum of each existing cohort's expected residual revenue plus expected revenue from future cohorts. Each cohort follows its own retention and expansion curve; total forecast is the integral across cohorts. This is the serious method.
- **Scenario modelling** — bull, base, and bear cases with explicitly different assumptions for churn, expansion rate, new customer acquisition, and ARPU. Board presentations show all three bands.

Annual planning must start with the cohort forecast. Take the existing cohorts, apply their empirical retention and expansion curves, project forward 12 months, then layer new acquisition on top with channel-specific assumptions. Simple linear projection for an annual plan is planning malpractice.

Reconcile bookings-based forecasts (what sales commits) against cohort-based forecasts (what retention and expansion actually produce). The gap is your risk.

## Metrics Dashboard Design

Separate dashboards by audience and decision cadence. One dashboard for everyone is always the wrong answer.

- **Exec dashboard** — weekly review, 5 metrics maximum. MRR, NRR, CAC, LTV, active customers. Show trend deltas (week-over-week, month-over-month) as coloured arrows. No cohort detail, no funnel detail. Fits on one screen.
- **Growth dashboard** — reviewed in the weekly growth meeting. Funnel conversion at every step, activation rate, K-factor, NPS, experiment queue status. One scroll screen, all funnel stages visible simultaneously.
- **Product dashboard** — reviewed weekly by PMs. Feature adoption rates, DAU/MAU stickiness, median session length, retention curve (rolling), time-to-activation. Per-feature drill-downs one click away.

Tool choice by stack:

- **PostHog** — all-in-one product analytics, feature flags, experiments; best for startups that want one tool.
- **Metabase** — open-source BI on top of the production database or warehouse; best when data already lives in Postgres/MySQL and you want SQL-native flexibility.
- **Amplitude** — mature product analytics, strong cohort and path analysis; best for scale-ups and enterprise.
- **Mixpanel** — similar to Amplitude, historically strong on event flexibility.

## North Star Metric

The North Star Metric (NSM) is the single metric that best captures product value delivered to users. Every team aligns to it. Pick one.

Canonical examples:

- **Airbnb** — nights booked (not signups, not revenue)
- **Slack** — messages sent in a paid team (not seats, not DAU)
- **Figma** — files with two or more editors (captures the collaboration value prop)
- **Spotify** — time spent listening
- **Zoom** — weekly hosted meeting minutes

NSM selection criteria:

- **Predicts long-term revenue** — improvements in NSM lead revenue by 1–3 quarters.
- **User-centric** — measures value users receive, not internal vanity (signups, pageviews).
- **Actionable** — teams can move the metric through product, engineering, or growth work. A metric no team can influence is not a North Star.
- **Measurable now** — defined in events you already instrument, not aspirational.
- **Single** — two North Stars means no North Star. Pick one; add supporting metrics around it.

## Growth Meeting Cadence

A 45-minute weekly growth meeting keeps experiments moving and prevents the funnel from rotting between quarterly reviews. Template:

- **0–5 min: dashboard review** — what moved this week on the growth dashboard; any metric outside its normal band. Surface-level only; no debate.
- **5–20 min: hypothesis review** — results of experiments that concluded this week. Winners, losers, inconclusive. What did we learn? What does the learning imply for the roadmap?
- **20–35 min: next bets prioritisation** — proposed experiments for the coming 2–4 weeks. Score each on ICE (Impact, Confidence, Ease) or PIE (Potential, Importance, Ease). Kill low-scoring proposals; do not debate them further.
- **35–45 min: experiment assignments** — for each greenlit experiment, assign owner, target launch date, and target read-out date. Owner is one person, not a team.

Attendees: PM, engineering lead, marketing lead, designer, customer success lead. Optional: data analyst. Not optional: a decision-maker empowered to kill or greenlight experiments on the spot. A growth meeting where every decision is "we'll discuss offline" is worse than no meeting.

Rotate the facilitator monthly to avoid single-person bottlenecks, and maintain a persistent experiment backlog document (Notion, Linear, Airtable) so the meeting is reviewing artifacts, not generating them live.

## Companion Skills

- `saas-business-metrics` — authoritative MRR/ARR/NRR/LTV/CAC/churn definitions
- `product-led-growth` — PLG motions that drive these metrics
- `habit-forming-products` — user behaviour loops that improve retention
- `lean-ux-validation` — hypothesis validation before committing engineering time
- `python-data-analytics` — custom cohort and funnel calculations in pandas/Polars
- `observability-platform` — RUM and in-app instrumentation

## Sources

- *Hacking Growth* — Ellis & Brown (Currency)
- *Lean Analytics* — Croll & Yoskovitz (O'Reilly)
- PostHog documentation — `posthog.com/docs`
- Metabase documentation — `metabase.com/docs`
- Baremetrics Open Benchmarks — `baremetrics.com/open`
