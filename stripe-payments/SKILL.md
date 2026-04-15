---
name: stripe-payments
description: Use when integrating Stripe payments, subscriptions, customer portal,
  and webhook-driven billing workflows in SaaS, web apps, or mobile-backed systems.
  Covers PaymentIntents, Customers, recurring billing setup, idempotency, webhook
  verification, and PHP plus Node.js implementation patterns.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Stripe Payments

<!-- dual-compat-start -->
## Use When

- Use when integrating Stripe payments, subscriptions, customer portal, and webhook-driven billing workflows in SaaS, web apps, or mobile-backed systems. Covers PaymentIntents, Customers, recurring billing setup, idempotency, webhook verification, and PHP plus Node.js implementation patterns.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `stripe-payments` or would be better handled by a more specific companion skill.
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
Use this skill when Stripe is the payment and billing backbone. The goal is to make payment flows safe, retriable, webhook-driven, and compatible with recurring SaaS billing instead of treating Stripe as a synchronous charge API.

## Load Order

1. Load `world-class-engineering`.
2. Load `deployment-release-engineering`, `advanced-testing-strategy`, and `vibe-security-skill` for release, test, and security controls.
3. Load this skill for Stripe mechanics.
4. Load `subscription-billing` for pricing tiers, dunning, metering, and revenue operations.

## Stripe Workflow

### 1. Define the Commercial Objects

Set up:

- `Product` for the thing being sold
- `Price` for each amount, billing interval, and currency
- one-time Prices where setup fees or credits are separate from subscription revenue
- recurring Prices for plans, seats, or metered components
- Payment Links only for low-customization flows; use API-driven checkout or portal sessions for most SaaS apps

Keep your application’s internal plan and entitlement model mapped to Stripe IDs explicitly.

### 2. Create and Reuse Customers

- Create a Stripe `Customer` as early as the billing relationship starts.
- Store the Stripe customer ID in your database.
- Attach payment methods through Stripe client or hosted flows, not by storing raw card data.
- Set a default payment method intentionally for subscriptions and invoice collection.

### 3. Use PaymentIntents for Direct Charges

- Use `PaymentIntent` for one-time payments or setup-related charges.
- Expect `requires_action` and 3DS or SCA flows; do not assume immediate success.
- Treat `payment_intent.succeeded` and related webhooks as the durable completion signal.
- Show the user actionable states for declined cards, insufficient funds, and authentication-required flows.

### 4. Create Subscriptions Safely

- Create subscriptions against an existing `Customer`.
- Use trials only when the trial-to-paid conversion path is explicit.
- Use `billing_cycle_anchor` deliberately when aligning renewals to contract dates or month boundaries.
- On plan changes, choose `proration_behavior` intentionally:
  - `always_invoice` when charging or crediting immediately is expected
  - `create_prorations` when Stripe should calculate proration items for the next invoice flow
  - `none` when you want the change to take effect without surprise charges

### 5. Use Customer Portal for Self-Service

- Configure the customer portal in Dashboard or API before exposing it.
- Set a `return_url` back into your product.
- Allow plan changes, payment-method updates, and cancellations only if your entitlement model can process them correctly.
- Use portal cancellation deflection and feedback collection where churn reduction matters.

### 6. Make Mutations Idempotent

- Send an idempotency key on every Stripe mutation from your server.
- Use stable request-scoped keys for retries, not fresh random keys on every retry attempt.
- Keep the application request ID and Stripe idempotency key correlated in your logs.
- Never use idempotency keys on `GET` or `DELETE`; Stripe documents them for `POST` requests.

### 7. Treat Webhooks as the Source of Truth

- Verify webhook signatures using the raw request body and the endpoint secret.
- Return `2xx` quickly, then hand off heavy work to durable job processing.
- Deduplicate event processing by Stripe event ID or a derived business idempotency key.
- Expect retries and out-of-order delivery; design your state transitions to be safe under replay.

### 8. Test the Full Lifecycle

- Use Stripe test mode and test cards for payment and SCA flows.
- Use test clocks when exercising subscription renewals, dunning, or trial expiry.
- Test failure paths, not just happy-path payment success.
- Validate webhook handling with duplicate delivery, stale delivery, and signature failure cases.

## Standards

### Security

- Never store raw card data unless you are explicitly building for PCI scope you can support.
- Use Stripe-hosted payment collection or Stripe.js elements where possible.
- Keep secret keys server-side only.
- Verify every webhook signature and reject unsigned or invalid payloads.

### Data and State

- Stripe object IDs must map to internal customer, account, plan, and entitlement records.
- Application access should follow invoice and subscription state derived from verified events.
- Refunds, cancellations, pauses, and plan changes must update entitlements through durable state transitions.

### UX

- Tell the user whether the payment is pending, requires action, failed, or complete.
- Avoid surprise prorations on upgrade or downgrade flows.
- Offer self-service payment-method updates and billing-history access where possible.
- Keep cancellation and failed-payment messaging recovery-oriented.

### Operations

- Log Stripe request IDs, webhook event IDs, and internal correlation IDs together.
- Keep a replay-safe webhook processor and a manual reprocessing path.
- Emit release markers around billing-flow changes so regressions are diagnosable.
- Keep dashboard or runbook coverage for webhook failure rate, event backlog, payment failures, and refund volume.

## Review Checklist

- [ ] Products, Prices, and internal entitlements are mapped explicitly.
- [ ] Customers and payment methods are stored by reference, not raw card data.
- [ ] PaymentIntents handle `requires_action` and asynchronous completion states.
- [ ] Subscription creation, trialing, and proration behavior are deliberate.
- [ ] Customer portal settings match the business rules for plan changes and cancellations.
- [ ] Every Stripe mutation uses idempotency.
- [ ] Webhooks verify signatures against the raw body and are replay-safe.
- [ ] Test mode covers SCA, decline, renewal, cancellation, and webhook failure paths.

## References

- [references/stripe-php-integration.md](references/stripe-php-integration.md): PHP 8+ integration patterns for Customers, PaymentIntents, subscriptions, and webhooks.
- [references/stripe-nodejs-integration.md](references/stripe-nodejs-integration.md): Node.js and TypeScript integration patterns for the same Stripe workflows.
- [references/webhook-handling.md](references/webhook-handling.md): SaaS webhook catalogue, deduplication rules, and idempotent state updates.
- [../subscription-billing/SKILL.md](../subscription-billing/SKILL.md): Subscription lifecycle, dunning, metered billing, and revenue operations.
- [../ai-saas-billing/SKILL.md](../ai-saas-billing/SKILL.md): Module gating and billing-pattern alignment for paid add-ons.
