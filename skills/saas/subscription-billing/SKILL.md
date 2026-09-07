---
name: subscription-billing
description: Use when designing or reviewing recurring subscription lifecycle on Stripe Billing — plans/Prices, trials, proration, upgrades/downgrades, cancel/pause, Smart Retries dunning, metered usage, automatic tax, multi-currency, and the strategy choice between subscription vs perpetual and monthly vs annual.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Subscription Billing


## Required Inputs

| Input | Required | Use |
|---|---|---|
| Tenant, product, and lifecycle scope | yes | Bound the SaaS decision |
| Current architecture, plans, policies, and constraints | yes | Preserve enforceable behaviour |
| Production data or verified evidence | conditional | Validate thresholds and migrations |

## Capability and permission contract

Default to read-only analysis. Change configuration, billing, identity, tenant data, infrastructure, or customer communications only with explicit authority, least-privilege credentials, tenant scope, rollback, and auditable approval. Never expose secrets or cross tenant boundaries.

## Degraded mode

If production access, policy, telemetry, or authoritative records are unavailable, produce a labelled design or dry-run plan. Do not claim deployment, reconciliation, deletion, delivery, or measured outcomes; list missing evidence and verification.

## Decision rules

| Condition | Action | Stop condition |
|---|---|---|
| Tenant isolation, money, identity, or deletion is affected | Require approval and rollback evidence | Scope or authority is ambiguous |
| Evidence supports a reversible change | Stage, test, and record it | Acceptance checks fail |
| Only partial context is available | Return assumptions and validation | A production claim cannot be verified |

## Domain Anti-Patterns

- Applying one tenant's policy or data to another. Fix: enforce tenant scope at every boundary.
- Mutating production from an advisory request. Fix: remain read-only until authority is explicit.
- Inventing limits, prices, metrics, or compliance claims. Fix: use authoritative records or mark them unresolved.
- Shipping without rollback and audit evidence. Fix: stage and retain before/after proof.
- Treating a missing dependency as successful. Fix: name the blocked verification.


<!-- dual-compat-start -->

## Use When

- The system charges customers on a recurring schedule and you need to model the subscription lifecycle (create, trial, upgrade, downgrade, cancel, pause, resume, dunning) on Stripe Billing.
- You are choosing proration behaviour, Smart Retries policy, end-of-dunning disposition, metered pricing, automatic tax, or multi-currency Prices.
- You need a defensible recommendation on subscription vs perpetual licence, or monthly vs annual billing cadence.

## Do Not Use When

- The work is one-time payments, webhook signature verification, or 3DS/SCA primitives — use `stripe-payments`.
- The work is revenue recognition, deferred-revenue ledger entries, or ASC-606 categorisation — use `saas-accounting-system`.
- The work is cohort retention dashboards, MRR/ARR analytics, or growth experimentation — use `saas-growth-metrics`.

## Required Inputs

- Plan catalogue intent: tier names, included features, billing intervals, target currencies.
- Lifecycle policy: trial length, upgrade/downgrade timing, cancellation grace, pause allowance.
- Recovery policy: retry window, end-of-dunning disposition (cancel / unpaid / past_due).
- Tax footprint: jurisdictions where the business has nexus and registration status.

## Workflow

1. Read this `SKILL.md` end-to-end; load `stripe-payments` for primitives the lifecycle relies on (PaymentIntents, webhook signatures, 3DS).
2. Decide plan catalogue and Price strategy (§1, §9, §11) before writing API calls.
3. Implement creation, trial, mid-cycle change, and cancel paths against the Stripe contracts (§3–§6).
4. Configure Smart Retries and end-of-dunning disposition (§7) before launch; wire all webhook events.
5. Add tax (§10) and metered pricing (§8) only when scope demands them.
6. Validate against §13 production checklist; load `references/` only for the specific deep dive needed.

## Quality Standards

- Stripe is the system of record for subscription state; the local mirror is eventual.
- Every `subscriptions.update` call sets `proration_behavior` explicitly — never rely on defaults silently.
- Plan catalogue is reproducible across environments (Terraform Stripe provider or seed scripts); Prices are append-only by convention.
- Webhooks are the only trustworthy state-transition signal; UI optimism does not replace `customer.subscription.updated`.

## Anti-Patterns

- Editing a Price to change its amount instead of creating a new Price and migrating subscriptions.
- Treating `incomplete` as failure — the subscription has 23 hours to complete first payment.
- Cancelling immediately when the customer paid through period end (use `cancel_at_period_end`).
- Inventing meter aggregation enums or endpoint names instead of pulling them from Stripe's reference before coding.
- Duplicating revenue-recognition logic here instead of delegating to `saas-accounting-system`.

## Outputs

- Plan and Price catalogue captured as code, with currency and interval matrix.
- Documented lifecycle policy mapping each transition to a `proration_behavior` choice.
- Smart Retries configuration record, including end-of-dunning disposition.
- Webhook handler inventory covering the lifecycle events listed in §7.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Release evidence | Subscription billing configuration record | Markdown doc capturing plans, Prices, dunning policy, metered config, tax handling, and webhook map | `docs/billing/subscription-config-2026-04-16.md` |

## References

- `references/dunning-management.md`, `references/metered-billing.md`, `references/revenue-recognition.md` for deep detail.
- Companion skills: `stripe-payments` (primitives), `saas-subscription-mastery` (broader lifecycle/retention playbook), `saas-accounting-system` (revenue recognition), `saas-growth-metrics` (MRR cohorting).

<!-- dual-compat-end -->

Use this skill when recurring revenue must be intentional rather than incidental. The goal is to design plans, lifecycle transitions, recovery workflows, and finance signals that support retention, predictable revenue, and trustworthy customer experience.

## Load Order

1. Load `world-class-engineering`.
2. Load `stripe-payments` for Stripe payment primitives, webhook verification, and SCA flow.
3. Load this skill for plan design, lifecycle, dunning, metering, tax, and reporting on Stripe Billing.
4. Load `saas-accounting-system` and `saas-growth-metrics` when the task crosses into revenue recognition or growth analytics.

## §1 The Subscription Data Model

Stripe Billing's core entities, with one-line gloss from the Stripe Billing subscriptions overview:

- **Customer** — stores the information needed for recurring charges (default payment method, billing address, tax IDs).
- **Product** — the offering customers subscribe to. The SKU. Example: "Pro plan".
- **Price** — the pricing configuration for a Product: amount, currency, billing interval, billing scheme. Example: `$29 USD / month`.
- **Subscription** — the recurring payment agreement between a Customer and the business.
- **SubscriptionItem** — an individual line item within a Subscription. One per billable component (base seat, add-on, metered usage).
- **Invoice** — the billing document generated for each subscription cycle.

Modelling rule: a Product is the SKU; a Price is the price-point + currency + interval. To raise the price, create a new Price and migrate subscriptions onto it — Prices are append-only by convention. Each SubscriptionItem references one Price; mixed billing schemes (flat seat fee + metered overage) live in the same Subscription as separate items.

## §2 Subscription Statuses

The full enum (verbatim meaning from the Stripe Billing overview):

| Status | Meaning |
|--------|---------|
| `trialing` | Subscription is in a trial period; safe to provision the product. |
| `active` | Subscription is in good standing. |
| `incomplete` | Customer must make a successful payment within 23 hours to activate. |
| `incomplete_expired` | Payment failed and the customer didn't complete payment within 23 hours. |
| `past_due` | Payment on the latest finalized invoice failed or wasn't attempted. |
| `unpaid` | Latest invoice hasn't been paid but the subscription remains in place. |
| `canceled` | Terminal state; cannot be updated. |
| `paused` | Trial ended without a payment method; awaiting payment details to resume. |

Entitlement rules: `trialing`, `active`, `past_due` grant full access; `paused` and `unpaid` degrade access according to dunning policy; `canceled` ends access at period end. Wire each status to a webhook path in §7.

## §3 Creating a Subscription

Required parameters on `POST /v1/subscriptions`:

- `customer` — the Customer ID being subscribed.
- `items` — a list of up to 20 subscription items, each with an attached `price` (or `price_data` for ad-hoc).

Key optional parameters:

- `trial_period_days` — days before the first charge.
- `payment_behavior` — one of `allow_incomplete`, `default_incomplete`, `error_if_incomplete`.
- `automatic_tax` — object enabling automatic tax calculation.
- `proration_behavior` — defaults to `create_prorations`.
- `cancel_at_period_end` — boolean, defaults to `false`.
- `collection_method` — `charge_automatically` (default) or `send_invoice`.

cURL:

```bash
curl https://api.stripe.com/v1/subscriptions \
  -u "<<YOUR_SECRET_KEY>>:" \
  -d customer={{CUSTOMER_ID}} \
  -d "items[0][price]={{PRICE_ID}}"
```

PHP (`stripe-php`):

```php
$subscription = $stripe->subscriptions->create([
    'customer' => $customer->id,
    'items' => [['price' => $priceId]],
    'payment_behavior' => 'default_incomplete',
    'expand' => ['latest_invoice.payment_intent'],
]);
```

Node.js (`stripe-node`):

```javascript
const subscription = await stripeClient.subscriptions.create({
  customer: customer.id,
  items: [{ price: priceId }],
  payment_behavior: 'default_incomplete',
  expand: ['latest_invoice.payment_intent'],
});
```

Use `payment_behavior: 'default_incomplete'` when the front-end must confirm the first PaymentIntent (and handle 3DS) before the subscription transitions out of `incomplete`. The expanded `latest_invoice.payment_intent.client_secret` is what the browser SDK confirms; see `stripe-payments` for the SCA flow.

## §4 Trials

**Classic trial.** Pass `trial_period_days` on create. When the trial ends, the subscription moves to `active` and Stripe charges the customer's default payment method.

**Modern trial offers** (configured via `trial_settings` and trial offer objects):

- `duration.type = relative` — trial length is set in billing intervals.
- `duration.type = timestamp` — trial ends on an absolute date.
- `end_behavior` — controls the price the subscription transitions to at trial end (the regular price or another configured price).
- If a subscription contains only trial offers and all trial offer prices are `0`, the subscription status is `trialing`. Paid trials result in `active`, `incomplete`, or `past_due`.
- Constraint: trial offers cannot be combined with Stripe Checkout or the legacy `trial_end` parameter — pick one path.

**Trial-end notification.** The `customer.subscription.trial_will_end` webhook is sent 3 days before the trial ends (or immediately if the trial is shorter than 3 days). Wire it to the transactional email pipeline so the customer sees a reminder with a one-click payment-method capture link.

**Trial length defaults.**

- B2C: 7–14 days. Short trials force activation.
- B2B self-serve: 14 days, no card up-front.
- Sales-assisted POCs: longer custom durations driven by a CSM.

## §5 Mid-Cycle Changes — Proration

Worked example from Stripe's prorations documentation: upgrading from a `$10/month` plan to a `$20/month` plan halfway through the cycle generates `-5 USD` for unused time on the initial price and `+10 USD` for remaining time on the new price.

`proration_behavior` enum:

1. `create_prorations` (default) — creates proration invoice items when applicable; only invoiced immediately under specific conditions.
2. `always_invoice` — calculates the proration and immediately generates an invoice.
3. `none` — no proration; customers are billed the full new amount when the next invoice generates.

Direction rules:

- Upgrades generate positive prorations (additional charges).
- Downgrades create credit prorations.
- Negative prorations are not automatically refunded — handle manually depending on classic vs flexible billing mode.

Decision table:

| Transition | Recommended `proration_behavior` | Rationale |
|------------|----------------------------------|-----------|
| Upgrade (immediate value delivered) | `always_invoice` | Bill the difference now while the new entitlement unlocks. |
| Downgrade (effective at period end) | `none` + `cancel_at_period_end`-style swap | Avoid issuing an unintended credit. |
| Quantity bump on a metered seat | `create_prorations` | Roll prorations into the next invoice. |
| Plan rename only (same price) | `none` | Nothing to charge. |

Upgrade confirmation copy must disclose the immediate charge, the new recurring amount, and the next billing date. Example: "You'll be charged USD 42.33 today to upgrade to Pro. Starting 2026-05-01 you'll be billed USD 99.00 per month."

Downgrade copy must enumerate exactly what will be lost and when: "On 2026-05-01 your plan changes to Starter. You will lose API access, 3 team seats (keeping 1), and CSV export. Your data and projects are preserved."

## §6 Cancel, Pause, Resume

**Cancellation timing.**

- Default — immediate: cancellation takes effect immediately and invoices are no longer generated for canceled subscriptions.
- At period end: set `cancel_at_period_end = true`; the subscription completes the duration the customer has already paid for.
- Mid-cycle proration: pass `prorate` to prorate the cancellation. If you set a custom cancellation date, you cannot provide a refund — a credit proration is always generated.
- Period-end cancels: any pending prorations are left in place and still collected at the end of the period.

The cancellation flow is the highest-leverage retention surface. Design an exit-intent modal that (1) acknowledges without guilt-tripping, (2) asks a structured reason-code question, (3) presents one targeted save offer matched to the reason code, (4) confirms the cancellation, and (5) sends a confirmation email with reactivation link and data-export instructions. Reason codes must be a closed list so the data is analyzable.

**Pause and resume.** The Stripe-managed `paused` status is the state when a trial ends without a payment method. Programmatic pause is performed via the `pause_collection` parameter on subscription update. Confirm the exact `pause_collection.behavior` enum (e.g. `keep_as_draft`, `mark_uncollectible`, `void`) against the Stripe subscription update reference before publishing handler code.

Operational rules for self-serve pause:

- Allow 1, 2, or 3 months; cap at 3 to force a resume/cancel decision.
- Compute and store the auto-resume date at pause time.
- Email 3 days before auto-resume and again on the resume day with the invoice receipt.
- Surface a persistent dashboard banner ("Your subscription is paused until 2026-07-01") with a primary "Resume now" action.

## §7 Dunning with Smart Retries

Smart Retries uses AI to choose the best times to retry failed payment attempts and increase the chance of successful collection.

**Schedule options.** Retry within a chosen window: 1 week, 2 weeks, 3 weeks, 1 month, or 2 months. Stripe's recommended default is **8 tries within 2 weeks**. Disabling Smart Retries lets you set custom rules with up to three retries, each with a specific number of days after the previous attempt.

**End-of-dunning disposition** — pick one when configuring revenue recovery:

1. **Cancel** — subscription transitions to `canceled` after the maximum number of days defined in the retry schedule.
2. **Mark unpaid** — subscription transitions to `unpaid` after the maximum number of days; invoices continue to be generated and stay in draft.
3. **Leave past_due** — subscription remains in `past_due` after the maximum number of days.

Pick `cancel` for self-serve B2C, `unpaid` for B2B where collections will follow up out-of-band, and `past_due` only when finance has a manual intervention process.

**Webhook events to wire** (verbatim event names): `invoice.payment_failed` (each failed attempt), `customer.subscription.updated` (transitions to `past_due` / `unpaid` / `canceled`), `invoice.paid` (recovery success). Handlers must be idempotent — see `stripe-payments`.

**Dunning email cadence** is captured in `references/dunning-management.md`. Standard pattern: notification on Day 0, soft reminder on Day 3, warning on Day 7, degradation at Day 10, final warning at Day 14, end-of-dunning action at Day 21 with a winback message.

## §8 Metered / Usage-Based Pricing

Usage-based billing charges customers based on their consumption of the product or service. Three operational components:

1. Record customer usage data into Stripe so the right amount is billed.
2. Apply billing credits for prepaid or promotional usage.
3. Set up alerts when a customer exceeds a usage threshold.

Recording methods:

1. The Stripe API (meter events).
2. Dashboard CSV upload.
3. Amazon S3 bulk submission.

Stripe processes meter events asynchronously, so aggregated usage in meter event summaries and on upcoming invoices may not immediately reflect recently received events. Reconcile at end-of-cycle, not mid-cycle.

Until the exact endpoint and payload shape (`event_name`, `payload.stripe_customer_id`, `payload.value`, `timestamp`) are confirmed against the Stripe Billing meter-event API reference, this skill keeps §8 narrative-only — do not invent endpoint names, parameter keys, or aggregation enum strings in code samples. The aggregation modes are configured on the meter (not on each event); confirm the canonical enum on the meter object reference before publishing the comparison table.

Usage rules that hold regardless:

- Meter the unit the customer can predict and audit (seats, API calls, storage GB, messages, reports).
- Threshold alerts: 50% informational, 80% warning, 100% degrade or block, 120% escalate to account owner with overage projection.
- Never rely on in-memory counters — meter events must be persisted before being submitted to Stripe.

Operational depth lives in `references/metered-billing.md`.

## §9 Pricing Models

Stripe Prices support several recurring billing schemes. The named families: `per_unit`, `tiered` (with `tiers_mode` of `graduated` or `volume`). Confirm the exact `billing_scheme` and `tiers_mode` enum strings on the Stripe Price object reference before publishing code that branches on them.

Decision matrix:

| Scheme | When to use | Example |
|--------|-------------|---------|
| Flat recurring (per_unit, quantity 1) | Single-tier SaaS plan | "Pro: $29/month" |
| Per-seat (per_unit, quantity N) | B2B seat-based plans | "$10/seat × 12 seats" |
| Graduated tiers | Per-unit price drops as usage grows, only above each tier's threshold | "First 1k API calls free, next 9k @ $0.001, then $0.0005" |
| Volume tiers | One unit price applies across all units, based on the highest tier reached | "If usage > 10k, every call billed @ $0.0005" |
| Metered + tiered | Pay-as-you-go with quantity discounts | OpenAI-style API billing |

Use a small, understandable set of plan tiers (Freemium / Starter / Pro / Enterprise). Tie pricing to delivered value, not internal implementation cost. Keep feature gates explicit and machine-enforceable.

## §10 Tax on Subscriptions

Enable automatic tax on a subscription:

```bash
curl https://api.stripe.com/v1/subscriptions \
  -u "<<YOUR_SECRET_KEY>>:" \
  -d "automatic_tax[enabled]=true"
```

Validate customer location at the moment of the call by adding `-d "tax[validate_location]=immediately"`.

**Tax IDs on the Customer.** Stripe supports over 200 specific tax ID types organised by country code (`eu_vat`, `gb_vat`, `au_abn`, etc.). To update a tax ID, delete the old one and create another — tax IDs are not edited in place.

**Strategy note.** Stripe Tax tracks sales against local registration thresholds and alerts when tax obligations may exist. This does not absolve the merchant of registering in jurisdictions where required; treat threshold alerts as input into a finance and legal workflow, not as compliance itself. East Africa VAT and withholding tax are finance and legal controls, not just API fields.

## §11 Multi-Currency Subscriptions

A Subscription's currency is fixed at creation, and a Price has a single currency, so a multi-currency catalogue means **multiple Prices per Product** — one per currency. Stripe supports charging in over 135 currencies. Presentment-vs-settlement and zero-decimal rules from `stripe-payments` apply identically.

Confirm the shape of `currency_options` on the Price object (which lets a single Price ID present in multiple currencies) against the Stripe Price object reference before relying on it as an alternative to one-Price-per-currency.

## §12 Strategy — Subscription vs Perpetual, Monthly vs Annual

Strategic framing only; the technical guidance above stands on Stripe documentation.

Durable software companies treat the **customer relationship**, not the transaction, as the primary asset. The implications:

- Subscription pricing aligns vendor and customer incentives by making churn (not point-of-sale resistance) the primary loss mechanism.
- Annual prepay reduces churn frequency and accelerates cash-in, but costs revenue if discounted aggressively.
- Monthly billing exposes more frequent retention signals; pair it with cohort analysis from `saas-growth-metrics`.

Recommendation table:

| Decision | Default | Trigger to revisit |
|----------|---------|--------------------|
| Subscription vs perpetual licence | Subscription for SaaS | Specialised on-prem or regulated deployments. |
| Monthly vs annual | Offer both; default new customers to monthly | Sales-led B2B with negotiated annual terms. |
| Discount on annual | Offered to incentivise prepayment | Specific percentage is a pricing decision; do not assert a typical range without a sourced benchmark. A/B test via experiment-engineering. |
| Trials | 14 days, no card up-front for self-serve | Sales-assisted POCs use longer custom durations. |

## §13 Production Checklist & Cross-References

- [ ] Webhook subscriptions for the full lifecycle event set (§7) wired to idempotent handlers (cross-ref `stripe-payments`).
- [ ] Plan catalogue stored as code (Terraform Stripe provider or seed scripts) so Prices are reproducible across environments.
- [ ] `proration_behavior` chosen explicitly on every `subscriptions.update` call — no defaults left implicit.
- [ ] Smart Retries configured; end-of-dunning disposition matches the account-recovery playbook.
- [ ] `automatic_tax[enabled]=true` on every subscription where the business has nexus; Tax IDs collected in supported regions.
- [ ] `customer.subscription.trial_will_end` triggers the transactional email pipeline.
- [ ] Subscription state mirror in MySQL is eventual — Stripe is the source of truth; reconciliation job runs nightly.
- [ ] Revenue recognition handled in `saas-accounting-system`, not duplicated here.
- [ ] Cohort retention dashboards live in `saas-growth-metrics`.
- [ ] Plan tiers tied to value, not to internal implementation cost.
- [ ] Cancellation flow uses a closed reason-code list with one save offer per code.
- [ ] Multi-currency catalogue uses one Price per currency unless `currency_options` has been verified for the use case.

## Standards

- Billing transitions must be understandable to the customer **before** the charge happens.
- Cancelled users must not keep paid access beyond the billed period unless policy says so explicitly.
- Cash collection and revenue recognition are separate ledgers; subscription, invoice, and entitlement state must reconcile.
- Revenue metrics must be reproducible from raw billing data, not spreadsheet folklore.

## Agent Line-Item Patterns (Enhancement)

When the subscription drives an agent product, four line-item patterns appear on the invoice. Engineer them as **named, distinct** Stripe price IDs — not as opaque "Usage" lines — so finance, dispute teams, and customers can reconcile them.

### Pattern 1 — Per-resolution price

- Stripe `Price` model: `usage_type='metered', aggregate_usage='sum'`.
- Meter: `agent_resolutions_completed_{feature}`.
- Reported by `ai-usage-metering-and-billing` on `agent.resolution.completed` (verdict='resolved').
- Invoice line label: `"{Feature} — Resolutions (completed)"`.

### Pattern 2 — Attempted-only price

- Separate `Price` from Pattern 1, typically 20–40% of the resolution unit price.
- Meter: `agent_tasks_attempted_only_{feature}`.
- Reported on `agent.task.attempted` when the tier's pricing policy bills for attempts (see `ai-agent-attempted-vs-completed-billing/references/attempt-classification.md`).
- Invoice line label: `"{Feature} — Attempted (no resolution)"`.

### Pattern 3 — SLA credit

- Stripe **credit note**, not a negative invoice line.
- Issued by the SLA-credit pipeline (`ai-agent-sla-credit-automation`).
- Reason text on the credit note carries the breach metadata: `"SLA breach: resolution_rate_floor — period 2026-05 — eligible_amount $X"`.
- Reconciles to the `4920 SLA Credits Issued — Agent` contra-revenue account (see `ai-agent-revenue-recognition/references/deferred-revenue-and-refund-reserves.md`).

### Pattern 4 — Abandonment refund

- Stripe **refund** against the original PaymentIntent (or invoice credit for net-30 customers).
- Issued by the abandonment-and-refund pipeline (`ai-agent-abandonment-and-refund-policy`).
- Reason text: `"Abandonment refund — class={technical|out-of-scope} — task={task_id}"`.
- Reconciles via the refund reserve.

### Don't conflate the four

A common anti-pattern is one negative line "Discount". The four patterns have **different ledger accounts**, **different auditor scrutiny**, and **different customer-comms templates**. They must remain distinguishable in the billing system, the GL, and the customer invoice.

### Cross-links

- `ai-agent-pricing-engine` — resolves which Price ID applies per event.
- `ai-agent-attempted-vs-completed-billing` — defines pattern 1 vs pattern 2 selection.
- `ai-agent-sla-credit-automation` — issues pattern 3.
- `ai-agent-abandonment-and-refund-policy` — issues pattern 4.
- `ai-agent-revenue-recognition` — booking of all four patterns.

## Companion Skills

- [../stripe-payments/SKILL.md](../stripe-payments/SKILL.md): Stripe primitives — PaymentIntents, webhook signature verification, 3DS / SCA, idempotency.
- `saas-architecture-strategy`: Broader lifecycle and platform strategy.
- [../saas-accounting-system/SKILL.md](../saas-accounting-system/SKILL.md): Double-entry accounting, deferred revenue ledgers, and billing-to-GL reconciliation.
- [../saas-business-metrics/SKILL.md](../saas-business-metrics/SKILL.md): MRR/ARR, NRR, cohort retention, churn analysis.
- [../../product-business/software-pricing-strategy/SKILL.md](../../product-business/software-pricing-strategy/SKILL.md): Value-based pricing and plan architecture.

## References

- [references/dunning-management.md](references/dunning-management.md): Failed-payment recovery flows, retry cadence, suspension logic.
- [references/metered-billing.md](references/metered-billing.md): Usage pricing models, recording patterns, billing-cycle resets.
- [references/revenue-recognition.md](references/revenue-recognition.md): Deferred revenue mechanics handed off to `saas-accounting-system`.
