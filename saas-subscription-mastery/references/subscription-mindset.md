# Subscription Mindset

The mental shift from one-off sales to subscription. Everything downstream — product decisions, pricing, marketing, success, finance — changes when the customer relationship, not the transaction, is the asset.

## Core shift

| Dimension | One-off sale | Subscription |
|---|---|---|
| Revenue recognition | At delivery | Ratably over the service period |
| Customer success | Post-sale nice-to-have | Core operating function |
| Value measurement | Deal size / margin | LTV, NRR, cohort retention |
| Marketing focus | New logos | Acquisition + expansion + retention loops |
| Product cadence | Ship and move on | Continuous improvement against retention |
| Pricing leverage | Discount at close | Plan mix, expansion, price-up cycles |
| Forecasting unit | Bookings | MRR / ARR + retention curves |
| Worst failure mode | Missed quota | Compounding logo churn |

## Revenue recognition, briefly

- Bookings are contracts signed. Billings are invoices sent. Revenue is the portion recognised this period.
- Annual paid up-front = cash today, revenue recognised over 12 months. Deferred revenue sits as a liability until earned.
- ASC 606 / IFRS 15: recognise revenue when performance obligations are satisfied; for SaaS that is typically over the subscription term on a straight-line basis unless a distinct performance obligation exists (e.g. one-time onboarding).
- Cash vs revenue divergence is the single biggest confusion in early-stage subscription businesses. Cash funds operations, revenue proves the economic engine.
- Keep a clean separation: `invoice.amount` (billed), `deferred_revenue` (unearned), `revenue` (recognised). See `subscription-billing` for the billing mechanics.

## LTV is the north-star, not deal size

```text
LTV   ~=  ARPU  x  gross_margin  /  customer_churn_rate
          (with expansion factored in for NRR-weighted LTV)
```

- A 100 GBP / month customer who stays 5 years is worth an order of magnitude more than a 5000 GBP deal that churns in 6 months.
- Deal-size bias pulls the organisation towards short-term thinking: bigger discounts to close, heavier implementation promises, misfit accounts that churn in year 2.
- Use LTV:CAC > 3 and CAC payback < 12 months as the two ground-truth gates before scaling spend.

## The relationship is the product

- Every touchpoint — invoice, password reset, support ticket, release note, onboarding email — is either a retention act or a churn trigger.
- Features alone do not retain. Outcomes do. Instrument the customer outcome (shipments processed, invoices reconciled, campaigns sent) not the feature clicks.
- Treat renewal as a forecasted milestone, not a surprise. Health scores, QBRs for large accounts, auto-renewal with clear value recap emails for SMB.

## Mindset checklist (apply when setting strategy)

- [ ] We have a defined customer outcome, not just a product definition.
- [ ] Retention is owned by a named leader with a dashboard and a budget.
- [ ] Pricing is reviewed annually against willingness-to-pay, not only against competitors.
- [ ] Customer success has a tracked intervention playbook, not just a quarterly check-in.
- [ ] Finance reports deferred revenue, NRR, GRR and cohort retention, not only bookings and cash.
- [ ] Product roadmap has explicit retention and activation line items, not only new-feature work.
- [ ] Marketing measures CAC by channel and plugs churn back into payback calculations.

## Common early-stage mistakes

- Booking-led culture — leadership celebrates new-logo wins while quietly losing the base.
- Treating implementation as revenue — one-time services reported as recurring inflates ARR.
- Over-discounting annual prepay — the discount compounds for every renewal cycle.
- No cohort view — month-over-month MRR hides the leak.
- No activation definition — support and CS cannot triage because there is no baseline of "healthy".
- Pricing page written by engineering — features, not outcomes, drives low conversion.

## Relationship artefacts to build once, reuse always

- Customer health score (0–100) with weighted inputs (product usage, support load, invoice age, sentiment).
- Lifecycle map: awareness -> trial -> activation -> habit -> expansion -> advocacy -> renewal.
- Save playbook per churn reason (price, fit, champion-left, competitor, bug / outage, lifecycle end).
- Revenue-rec schedule generated from every invoice automatically, not by hand.
- Renewal risk forecast 90 / 60 / 30 days out, produced weekly.

## When to break the model

Subscription is not universal. Reject it when:

- The product is consumed once and rarely repeated (e.g. a wedding venue booking tool for couples).
- Willingness-to-pay is strongly tied to one-off events (e.g. exam prep).
- The customer's value curve decays faster than the recurring fee (you'll churn regardless).
- Compliance or procurement in the target segment prefers perpetual licences + support contracts.

In those cases a hybrid (perpetual + maintenance, or usage-based credits that never expire) is often a better fit than forcing a monthly plan.

## Cross-references

- `subscription-billing` — invoicing, dunning, tax, proration mechanics.
- `saas-business-metrics` — the full metrics framework.
- `software-pricing-strategy` — pricing principles, value-based pricing.
- `saas-sales-organization` — renewals, expansion, CS org fit.
