---
name: subscription-billing
description: Use when designing or reviewing subscription billing strategy, plan lifecycle,
  dunning, metered billing, tax handling, churn recovery, and SaaS revenue metrics.
  Covers trial-to-paid conversion, upgrades, downgrades, pauses, cancellations, usage
  pricing, and revenue recognition fundamentals.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Subscription Billing

<!-- dual-compat-start -->

## Use When

- Use when designing or reviewing subscription billing strategy, plan lifecycle, dunning, metered billing, tax handling, churn recovery, and SaaS revenue metrics. Covers trial-to-paid conversion, upgrades, downgrades, pauses, cancellations, usage pricing, and revenue recognition fundamentals.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `subscription-billing` or would be better handled by a more specific companion skill.
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
| Release evidence | Subscription billing configuration record | Markdown doc capturing plans, dunning policy, metered billing, tax handling, and chargeback procedure | `docs/billing/subscription-config-2026-04-16.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.

<!-- dual-compat-end -->

Use this skill when recurring revenue must be intentional rather than incidental. The goal is to design plans, lifecycle transitions, recovery workflows, and finance signals that support retention, predictable revenue, and trustworthy customer experience.

## Load Order

1. Load `world-class-engineering`.
2. Load `stripe-payments` for Stripe mechanics and webhook integration.
3. Load this skill for plan design, lifecycle, dunning, metering, tax, and reporting.

## Subscription Economy Fundamentals

Recurring revenue compounds where one-time transactions cannot: a customer acquired in month 1 produces revenue in months 2 through N until churn, so small retention gains compound. Lifetime value (LTV) exceeds transactional margin because acquisition cost amortises across many cycles.

- Predictable revenue enables hiring plans, multi-year infrastructure commitments, and defensible capital raises.
- Net Revenue Retention (NRR) above 100% means the installed base grows faster than new-logo churn.
- A 5% monthly churn rate caps the business below a finite revenue ceiling regardless of acquisition spend.
- Payback period (months to recover CAC from gross margin) determines whether growth is self-funding.

## Subscription States State Machine

Every subscription occupies exactly one state. Transitions are driven by explicit events and recorded in an audit log.

```text
     none
      |
      | checkout w/ trial
      v
   trialing ----------------------------+
      |                                 |
      | trial ends & card charged       | trial ends & card fails
      v                                 v
    active <------- reactivate ----- past_due
      |  ^                               |
      |  | resume                        | retries exhausted
      v  |                               v
    paused                             unpaid
      |                                 |
      | cancel from pause               | cancel after grace
      v                                 v
    cancelled <---------------------- cancelled
```

Allowed transitions:

- `none -> trialing` on checkout with trial days; `none -> active` on immediate paid checkout.
- `trialing -> active` on first successful charge; `trialing -> past_due` on failed charge; `trialing -> cancelled` on user cancel during trial.
- `active -> past_due` on failed renewal; `active -> paused` on user pause; `active -> cancelled` on user cancel (effective period end).
- `past_due -> active` on successful retry; `past_due -> unpaid` after retries exhausted.
- `unpaid -> active` on card update; `unpaid -> cancelled` after unpaid grace expires.
- `paused -> active` on resume (user or auto-date); `paused -> cancelled` on cancel while paused.
- `cancelled -> trialing` or `cancelled -> active` on reactivation (new subscription, preserved customer history).

Entitlement rules: `trialing`, `active`, `past_due` grant full access; `paused` degrades to read-only; `unpaid` blocks writes; `cancelled` ends access at period end.

## Trial-to-Paid Conversion

Trial length rules:

- B2C consumer apps: 7-14 days. Short trials pressure activation and reduce leakage.
- B2B SaaS: 14-30 days. Buyers need time to involve teammates and secure budget.
- Enterprise: prefer a CSM-led pilot over a time-boxed self-serve trial.

Email sequence during trial:

- Day 1: welcome + fastest-path-to-first-value checklist; one primary CTA, no upsell.
- Day 7 (or midpoint): usage summary, social proof, feature spotlight tailored to what is unused.
- Day (end minus 2): "Your trial ends in 2 days" with plan comparison and one-click payment capture.
- Day 0 (trial end): conversion confirmation and receipt, or retention offer if lapsed.

Paywall strategy:

- Soft paywall (feature-gate): account stays; premium features disabled with inline upgrade prompts. Preserves data and relationship.
- Hard paywall (full lockout): account read-only or locked until payment. Higher pressure; damages goodwill when value is already proven.
- Default to soft paywall for B2B and collaborative tools; hard paywall only when trial abuse is a material revenue leak.

## Plan Upgrade Flow

Proration formula for an immediate mid-cycle upgrade:

```text
credit_from_old = old_plan_amount * (days_remaining / days_in_cycle)
charge_for_new  = new_plan_amount * (days_remaining / days_in_cycle)
immediate_charge = charge_for_new - credit_from_old
```

Offer two timing options explicitly:

- Immediate with proration: new entitlements unlock now; prorated difference charged today; next invoice resets to full plan on the next anchor.
- Next cycle: new plan takes effect on renewal; no immediate charge; no entitlement change until the anchor date.

Upgrade confirmation UI copy must disclose the immediate charge, the new recurring amount, and the next billing date. Example: "You'll be charged USD 42.33 today to upgrade to Pro. Starting 2026-05-01 you'll be billed USD 99.00 per month."

Emit a `subscription.upgraded` event with previous plan, new plan, proration amount, effective date, and actor. Finance uses it for expansion-MRR classification; product uses it to trigger new-tier onboarding.

## Plan Downgrade Flow

Downgrades are scheduled for end-of-cycle by default. The customer keeps the paid-for entitlement until the anchor date, no refund is issued, and the new plan activates on renewal. Immediate-with-refund is reserved for explicit support exceptions.

Retention offer at the point of downgrade:

- Present "Save 50% for 3 months to stay" before confirming the downgrade.
- Offer pause as an alternative when the reason is "too expensive right now" or "not using it lately".
- Accept the downgrade without friction if the user declines.

Feature-loss warning must enumerate exactly what will be lost and when: "On 2026-05-01 your plan changes to Starter. You will lose API access, 3 team seats (keeping 1), and CSV export. Your data and projects are preserved."

Log the downgrade reason code. Emit `subscription.downgrade_scheduled` for contraction-MRR accounting at the anchor date.

## Cancellation Flow

The cancellation flow is the single highest-leverage retention surface. Design it as a conversation.

Exit intent modal structure:

1. Acknowledge the decision without guilt-tripping.
2. Ask a structured reason-code question (radio list + optional free text).
3. Present one targeted save offer conditional on the reason code.
4. Confirm cancellation or accept the save offer.
5. Send a confirmation email with reactivation link and data-export instructions.

Save offers matched to reason codes:

- "Too expensive" -> 30-50% discount for 3 months, or downgrade suggestion.
- "Not using it" -> pause for 1-3 months with auto-resume.
- "Missing feature X" -> record the feature request, notify when shipped, extend higher-tier trial.
- "Found alternative" -> accept gracefully, ask optional "what did they do better".
- "Project ended" -> accept, offer archive-mode or low-cost maintenance plan.

Reason codes must be a closed list so the data is analyzable. Free text is always optional. Cancellation is effective at period end; entitlement continues until then; a "Resume subscription" button stays visible through the remaining period.

## Pause & Resume

Pause is a first-class lifecycle state. In Stripe, set `pause_collection.behavior: keep_as_draft` to stop invoice generation while preserving the subscription.

- Allowed pause durations: 1, 2, or 3 months (cap at 3 to force a resume/cancel decision).
- Auto-resume date is computed at pause time and stored on the subscription.
- No charges occur while paused; the period does not advance; the anchor is preserved on resume.

Paused UI state: a persistent dashboard banner "Your subscription is paused until 2026-07-01" with a primary "Resume now" button and secondary "Cancel instead" link. Premium features are visibly disabled with the same banner copy, not silent failures.

Resume notifications: email 3 days before auto-resume ("resumes on 2026-07-01; card ending 4242 will be charged USD 99.00") and a second email on the resume day with the invoice receipt.

## Billing Anchors

Cycle anchor day determines when each subscription renews:

- Anniversary billing: anchor is the calendar day the subscription started. Spreads renewal load evenly; matches customer expectations.
- Calendar billing: anchor is the 1st of every month regardless of signup day. Simplifies finance reconciliation but prorates every first partial period.

Proration implications: anniversary billing prorates only on mid-cycle plan changes; calendar billing prorates every new subscription's first period. Annual plans anchor to signup anniversary unless enterprise terms set a fiscal-year anchor. Document the chosen model in the billing configuration record.

## Revenue Recognition

Cash collection and revenue recognition are separate ledgers. An annual plan paid in advance generates cash on day 1 but must be recognised ratably across 12 months (ASC 606 / IFRS 15).

Deferred revenue for a USD 1,200 annual plan invoiced on 2026-01-01:

| Month | Cash Received | Revenue Recognised | Deferred Balance |
|-------|---------------|-------------------|------------------|
| 2026-01 | 1,200 | 100 | 1,100 |
| 2026-02 | 0 | 100 | 1,000 |
| 2026-06 | 0 | 100 | 600 |
| 2026-12 | 0 | 100 | 0 |

Rules: monthly plans recognise in the month of service; annual plans recognise 1/12 per month for 12 months; mid-cycle cancellation stops future recognition but does not reverse recognised revenue; refunds reverse recognised revenue in the period issued.

## MRR Calculation

Normalise annual subscriptions to a monthly equivalent to produce a single MRR across intervals:

```sql
SELECT
  SUM(
    CASE billing_interval
      WHEN 'year' THEN plan_amount_cents / 12.0
      ELSE plan_amount_cents
    END
  ) / 100.0 AS mrr_usd
FROM subscriptions
WHERE status IN ('active', 'trialing', 'past_due')
  AND (cancelled_at IS NULL OR cancelled_at > CURRENT_DATE);
```

MRR movements (report each separately for a full waterfall):

- New MRR: subscriptions that moved from `none` to `active` this period.
- Expansion MRR: net increase from upgrades, seat additions, or metered overage.
- Contraction MRR: net decrease from downgrades, seat removals, or discounts.
- Churn MRR: MRR lost from subscriptions that transitioned to `cancelled`.
- Reactivation MRR: MRR recovered from previously cancelled customers starting new subscriptions.

Net New MRR = New + Expansion + Reactivation - Contraction - Churn. NRR = (Starting + Expansion + Reactivation - Contraction - Churn) / Starting; target above 100%.

## Cohort Retention Analysis

Group customers by signup month and track active status in each subsequent month. The curve reveals product-market fit stability and onboarding effectiveness.

```sql
WITH cohorts AS (
  SELECT customer_id, DATE_TRUNC('month', created_at) AS cohort_month
  FROM subscriptions
  WHERE started_at IS NOT NULL
),
activity AS (
  SELECT
    c.customer_id,
    c.cohort_month,
    DATE_TRUNC('month', m.month_date) AS active_month,
    EXTRACT(MONTH FROM AGE(m.month_date, c.cohort_month)) AS months_since_signup
  FROM cohorts c
  CROSS JOIN (
    SELECT generate_series(
      DATE_TRUNC('month', NOW()) - INTERVAL '12 months',
      DATE_TRUNC('month', NOW()),
      '1 month'
    ) AS month_date
  ) m
  JOIN subscriptions s
    ON s.customer_id = c.customer_id
   AND s.status IN ('active', 'trialing', 'past_due')
   AND s.started_at <= m.month_date
   AND (s.cancelled_at IS NULL OR s.cancelled_at > m.month_date)
)
SELECT cohort_month, months_since_signup, COUNT(DISTINCT customer_id) AS active_customers
FROM activity
GROUP BY cohort_month, months_since_signup
ORDER BY cohort_month, months_since_signup;
```

Output pivots into a triangular table (cohort month rows, months-since-signup columns). A healthy SaaS curve flattens at or above 80% by month 6; a continuous decline signals a product or onboarding problem.

## Dunning Email Sequences

When a renewal charge fails, treat the event as recoverable. Standard 21-day dunning timeline:

```text
Day 0 (payment fails) -> soft email: "Update your card"
Day 3                 -> reminder email with 1-click card update link
Day 7                 -> warning email: "Service will be limited in 3 days"
Day 10                -> subscription paused: feature access degraded
Day 14                -> final warning: "Subscription will cancel in 7 days"
Day 21                -> subscription cancelled; retention email with winback offer
```

Email content rules:

- Day 0 is a notification, not an accusation. Assume an expired card, not a deadbeat.
- Day 3 and Day 7 include a secure 1-click link that opens the billing portal pre-authenticated.
- Day 10 degradation matches the `past_due` entitlement rules; communicate it explicitly.
- Day 14 states the exact cancellation date and the exact action required to prevent it.
- Day 21 winback preserves the email relationship after cancellation; include reactivation discount and data-preservation assurance.

Payment retry schedule aligns with the timeline: retry on days 1, 3, 5, 7, 14. Stripe Smart Retries adapts this via decline-code machine learning; override only when business policy demands exact predictability.

## Refund & Dispute Handling

Refund policy matrix:

- Full refund: billing error, double charge, confirmed outage covering the billed period.
- Partial refund: mid-cycle cancellation with support approval; unused metered overage.
- Prorated refund: downgrade-with-refund exceptions; unused days on an annual plan per contract terms.

Stripe refund API flow: confirm charge ID and amount in cents; call `POST /v1/refunds` with `charge`, `amount`, `reason`; record the refund in the internal ledger before success; reverse recognised revenue if the refund spans already-recognised months; send a confirmation email with the 5-10 business-day settlement window.

Chargeback process: a chargeback is a network dispute, not a refund. The merchant loses by default if no evidence is submitted before the issuer deadline. Collect evidence immediately (signed terms, usage logs, IPs, communication history, refund-offer records) and submit through Stripe Dashboard or the Disputes API within 7-21 days. Above 1% dispute rate triggers network monitoring programs.

Fraud prevention:

- Enable Stripe Radar defaults; tune from real false-positive and false-negative data over the first 90 days.
- Velocity checks: block more than N signup attempts from the same IP, email domain, or card BIN within a window.
- 3D Secure 2 on high-risk markets; accept the conversion drop for liability shift.
- Manual review queue for borderline transactions; never auto-reject without a clear signal.

## Billing Portal Customisation

Stripe Customer Portal is the default self-serve billing surface. Configure deliberately rather than accepting defaults.

Features to enable:

- Cancel subscription (with the configured cancellation reason survey).
- Update payment method (card, bank debit where applicable).
- View and download invoice history.
- Update billing address and tax ID.
- Switch plan only if self-serve upgrade/downgrade is safe.

Branding: logo at production resolution; primary and secondary colours matching product brand tokens; custom domain for the portal URL to preserve brand trust.

Legal and policy: terms of service required for every jurisdiction served; privacy policy required where applicable (GDPR, DPPA, CCPA); support email or help-centre link visible on every portal page. Audit quarterly; feature toggles drift as Stripe ships new capabilities.

## Usage-Based Billing

Usage pricing works only when the customer understands and can predict the billed unit. Seats, API calls, storage GB, messages, and reports generated are good candidates; opaque composite units are not.

Pricing structures:

- Pure metered: zero base fee, pay per unit. High discovery friction, low low-usage friction.
- Tiered with included units: base fee covers N units; overage billed above N. Standard SaaS pattern.
- Volume-discounted tiers: per-unit price decreases at higher brackets. Rewards expansion.
- Commit-and-burn: customer prepays a discounted unit bucket that decrements with usage.

Threshold alerts: 50% informational; 80% warning (in-app banner + email with upgrade path); 100% degrade gracefully to overage or block when overage is not permitted; 120% escalate to account owner with overage-cost projection.

End-of-cycle reconciliation: aggregate usage records for the closed period; append overage as invoice line items with a usage-summary link; reset counters at the cycle anchor; preserve raw usage logs for audit. Stripe Metered Billing automates this when configured; never rely on in-memory counters across restarts.

## Multi-Tenant Billing

Multi-tenant SaaS requires billing architecture that matches tenant isolation.

Per-seat pricing via Stripe Subscription Items: one subscription per tenant; one subscription item per billable add-on (seats, storage, premium modules); quantity changes on the seat item trigger prorated charges on the next invoice; each item has its own price object and metered behaviour.

Per-tenant billing accounts: one Stripe Customer per tenant, not per user. The tenant is the legal payer. The tenant admin is the billing contact; other users have read-only invoice access through the app UI. Customer metadata stores the internal tenant ID for webhook reconciliation.

Consolidated invoicing for enterprise: some tenants require one invoice covering multiple workspaces or subsidiaries. Use Stripe Invoice Items with a single Customer across workspaces, generated at month close rather than per-subscription. Include a line-item breakdown by workspace with seat counts and metered usage. Terms: Net 30 or contract-specified; collection method `send_invoice`.

Isolation rules: never share a Stripe Customer across tenants even when the same human administers multiple tenants; webhook handlers must resolve the internal tenant ID from customer metadata before touching tenant data; every billing-event log line must include the tenant ID for multi-tenant compliance review.

## Billing Workflow

### 1. Design the Plan Hierarchy

Use a small, understandable set of tiers: Freemium, Starter, Pro, Enterprise. Tie pricing to delivered value, not internal implementation cost; keep downgrade paths real; keep feature gates explicit and machine-enforceable; avoid too many tiers.

### 2. Model the Subscription Lifecycle

Support these transitions deliberately: free trial to paid, paid renewal, immediate upgrade, downgrade now or at renewal, pause or grace period, cancel at period end, reactivate or win-back. Keep entitlement state aligned to subscription state and billing dates.

### 3. Choose Proration and Change Timing

- Prorate upgrades when the user expects immediate extra value.
- Avoid surprise charges on downgrades or plan experimentation.
- Offer "upgrade now" versus "switch at next renewal" when that choice matters.

### 4. Design Dunning and Recovery

- Treat payment failure as a recoverable lifecycle step, not instant cancellation.
- Define grace periods, retries, in-app warnings, and account restrictions.
- Support, product, and finance must agree on exact suspension and cancellation thresholds.

### 5. Add Metered Billing Only When It Matches Value

Use usage pricing only when the customer understands and can monitor the unit (seats, API calls, storage, messages, reports). Never meter units the customer cannot predict or audit.

### 6. Handle Currency and Tax Deliberately

Keep the account billing currency explicit; use per-currency Prices rather than undocumented guessing; choose between Stripe Tax and controlled manual tax rates by footprint and compliance maturity; treat East Africa VAT and withholding tax as finance and legal controls, not just API fields.

### 7. Measure Revenue Health

Track MRR, ARR, churn rate, NRR, trial conversion rate, and failed-payment recovery rate with definitions that are consistent over time.

## Standards

- Billing transitions must be understandable before the charge happens.
- Cancelled users must not keep paid access beyond the billed period unless policy says so explicitly.
- Separate cash collection from revenue recognition; subscription, invoice, and entitlement ledgers must reconcile.
- Revenue metrics must be reproducible from raw billing data, not spreadsheet folklore.

## Review Checklist

- [ ] Plan tiers are understandable and tied to value.
- [ ] Subscription lifecycle transitions are explicit and entitlement-safe.
- [ ] Proration behavior matches user expectations and business policy.
- [ ] Failed-payment dunning and grace periods are encoded clearly.
- [ ] Metered billing uses units customers can understand and monitor.
- [ ] Currency and tax handling are explicit for each target market.
- [ ] MRR, ARR, churn, and NRR definitions are documented consistently.

## Companion Skills

- [../stripe-payments/SKILL.md](../stripe-payments/SKILL.md): Stripe integration, PaymentIntents, subscriptions, portal, and webhooks.
- [../saas-accounting-system/SKILL.md](../saas-accounting-system/SKILL.md): Double-entry accounting, deferred revenue ledgers, and billing-to-GL reconciliation.
- [../saas-business-metrics/SKILL.md](../saas-business-metrics/SKILL.md): SaaS metrics framework covering MRR/ARR, CAC/LTV, cohort retention, and growth efficiency.
- [../software-pricing-strategy/SKILL.md](../software-pricing-strategy/SKILL.md): Value-based pricing, B2B vs B2C differences, and plan architecture decisions.

## References

- [references/dunning-management.md](references/dunning-management.md): Payment-failure recovery flows and suspension logic.
- [references/metered-billing.md](references/metered-billing.md): Usage pricing models, reporting patterns, and billing-cycle resets.
- [references/revenue-recognition.md](references/revenue-recognition.md): Deferred revenue, ratable recognition, and ASC 606 or IFRS 15 basics.
- [../stripe-payments/SKILL.md](../stripe-payments/SKILL.md): Stripe integration, PaymentIntents, subscriptions, portal, and webhooks.
- [../ai-saas-billing/SKILL.md](../ai-saas-billing/SKILL.md): Module-gating and add-on billing alignment for paid capabilities.
