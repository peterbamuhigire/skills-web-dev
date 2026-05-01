# Phase 02: Revenue Infrastructure

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the payment collection and subscription billing skills that convert deployed SaaS products into recurring revenue.

**Architecture:** Two new skill directories (`stripe-payments`, `subscription-billing`). Both must be dual-compatible — portable execution contract, no platform-specific blockers. `stripe-payments` covers integration mechanics; `subscription-billing` covers the full lifecycle including dunning, metered billing, and revenue recognition.

**Tech Stack:** Stripe Billing API, Stripe Webhooks, Stripe Customer Portal, PHP + Node.js SDK examples, idempotency keys, multi-currency, VAT/GST tax handling.

---

## Dual-Compatibility Contract

Same contract as Phase 01. Every `SKILL.md` must include:

```
Use When → Do Not Use When → Required Inputs →
Workflow → Quality Standards → Anti-Patterns → Outputs → References
```

Frontmatter:
```yaml
metadata:
  portable: true
  compatible_with: [claude-code, codex]
```

Optional Claude Code helpers in **Platform Notes** only — not as blockers.

Validate:
```bash
python -X utf8 skill-writing/scripts/quick_validate.py <skill-directory>
```

---

## Task 1: Create `stripe-payments` skill

**Files:**
- Create: `stripe-payments/SKILL.md`
- Create: `stripe-payments/references/stripe-php-integration.md`
- Create: `stripe-payments/references/stripe-nodejs-integration.md`
- Create: `stripe-payments/references/webhook-handling.md`

**Step 1:** Write `stripe-payments/SKILL.md` covering:

- Stripe account setup: Products, Prices (one-time and recurring), Payment Links
- Customer object: create, retrieve, attach payment methods, default source
- Payment Intents: create, confirm, 3DS/SCA handling, `payment_intent.succeeded` flow
- Subscriptions: create with trial, `billing_cycle_anchor`, proration modes (immediate, none, always_invoice)
- Customer Portal: configuration, return URL, allow plan changes / cancellations
- Idempotency: `Idempotency-Key` header on every mutation — prevents duplicate charges
- Webhook security: `stripe.webhooks.constructEvent()`, signature verification, raw body requirement
- Test mode: test card numbers, clock advancement for subscription testing
- Error handling: card declined, insufficient funds, authentication required — what to show the user

Anti-Patterns: not verifying webhook signatures, no idempotency keys, storing raw card data, treating webhook delivery as guaranteed exactly-once.

**Step 2:** Write `references/stripe-php-integration.md` — complete PHP 8+ integration using `stripe/stripe-php`: Customer create/retrieve, PaymentIntent, Subscription CRUD, webhook endpoint, idempotency.

**Step 3:** Write `references/stripe-nodejs-integration.md` — same coverage in Node.js/TypeScript using `stripe` npm package with async/await.

**Step 4:** Write `references/webhook-handling.md` — full webhook event catalogue for SaaS: `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.payment_succeeded`, `invoice.payment_failed`, `payment_intent.succeeded`, `charge.refunded`. Include idempotent database update pattern for each.

**Step 5:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py stripe-payments
git add stripe-payments/
git commit -m "feat: add stripe-payments skill (Stripe API, webhooks, PHP + Node.js)"
```

---

## Task 2: Create `subscription-billing` skill

**Files:**
- Create: `subscription-billing/SKILL.md`
- Create: `subscription-billing/references/dunning-management.md`
- Create: `subscription-billing/references/metered-billing.md`
- Create: `subscription-billing/references/revenue-recognition.md`

**Step 1:** Write `subscription-billing/SKILL.md` covering:

- Subscription lifecycle: free trial → converting to paid → upgrade → downgrade → pause → cancel → reactivate
- Proration: when to prorate, when not to (UX impact of surprise charges), upgrade-now vs. upgrade-at-renewal
- Plan hierarchy: Freemium, Starter, Pro, Enterprise — design principles, feature gates per tier
- Usage-based / metered billing: `UsageRecord` API, reporting usage, pay-as-you-go pricing
- Multi-currency: `currency` on Price object, Stripe automatic currency detection
- Tax: Stripe Tax (automatic) vs. manual tax_rate objects; VAT for EU customers; East Africa VAT/WHT
- Cancellation flows: exit survey, pause offer, downgrade offer, win-back email trigger
- Revenue metrics: MRR, ARR, churn rate, NRR — how to calculate from Stripe data

Anti-Patterns: letting cancelled users retain access beyond period end, no grace period on failed payments, not surfacing upgrade prompts at the right moment.

**Step 2:** Write `references/dunning-management.md` — full dunning sequence: Day 0 (payment failed email), Day 3 (retry + email), Day 7 (retry + in-app banner), Day 14 (account suspension warning), Day 21 (subscription cancelled). Stripe Smart Retries vs. manual retry schedule.

**Step 3:** Write `references/metered-billing.md` — usage record reporting patterns, reset behaviour at billing cycle, per-seat vs. per-unit vs. per-API-call pricing models with Stripe examples.

**Step 4:** Write `references/revenue-recognition.md` — deferred revenue concept, when to recognise SaaS subscription revenue (ratable over subscription period), ASC 606 / IFRS 15 basics, journal entries for prepaid subscriptions.

**Step 5:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py subscription-billing
git add subscription-billing/
git commit -m "feat: add subscription-billing skill (lifecycle, dunning, metered, revenue recognition)"
```

---

## Success Gate

- [ ] `stripe-payments` passes validator, SKILL.md ≤ 500 lines, portable metadata present
- [ ] `subscription-billing` passes validator, SKILL.md ≤ 500 lines, portable metadata present
- [ ] Both reference the `ai-saas-billing` skill in their References section (module gating integration)
- [ ] No `Required Plugins` blockers — Platform Notes only

---

## Reading Material

| Priority | Resource | Format | Cost | Unlocks |
|----------|----------|--------|------|---------|
| 1 | Stripe Billing documentation | Free (stripe.com/docs/billing) | Free | Core `stripe-payments` content |
| 2 | Stripe Webhooks guide | Free (stripe.com/docs/webhooks) | Free | Webhook handling reference |
| 3 | *Subscribed* — Tien Tzuo | Book | ~$25 | Subscription economics, churn psychology |
| 4 | Stripe Developer Blog | Free (stripe.dev/blog) | Free | Production edge cases and patterns |
| 5 | Stripe Tax documentation | Free (stripe.com/docs/tax) | Free | Multi-currency and VAT coverage |

**Read first:** Stripe Billing docs (free, authoritative, excellent) — read the full Billing section before writing any code examples in the skill.

---

*Next → `phase-03-platform-engineering.md`*
