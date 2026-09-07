---
name: stripe-payments
description: Use when integrating Stripe one-time payments, PaymentIntents, SetupIntents, Checkout, SCA, multi-currency, idempotency, or webhooks.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Stripe Payments


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

- Integrating Stripe for one-time payments, saved-card flows, or webhook receivers in a PHP or Node.js backend.
- Choosing between Stripe-hosted Checkout, Embedded Checkout, Payment Element, and raw Payment Intents.
- Hardening webhook handlers for signature verification, idempotency, and retry safety.
- Charging across currencies, handling SCA / 3D Secure, or wiring Stripe Tax.

## Do Not Use When

- The work is recurring billing, plan changes, dunning, proration, metered usage, or revenue recognition. Use `subscription-billing`.
- The work is Stripe Connect, marketplaces, or split payments. Out of scope.
- Tax registration strategy and filing operations. Stripe Tax docs handle this directly.

## Required Inputs

- Target stack (PHP, Node.js, or both), runtime versions, deploy target.
- UX requirements (hosted redirect, embedded form, custom UI) and PCI scope target.
- Currencies to charge, settlement country, and whether SCA-regulated regions apply.
- Where secrets live (Vault, AWS Secrets Manager, env files in dev only).

## Workflow

1. Read this `SKILL.md` end-to-end, then load referenced deep-dives only as needed.
2. Pick an integration model from §3 before writing code.
3. Implement Customer + PaymentIntent flow, then layer SetupIntent only if saving cards.
4. Stand up the webhook receiver with SDK signature verification and `event.id` idempotency.
5. Run through the production checklist before shipping.

## Quality Standards

- Every Stripe mutation uses an `Idempotency-Key`.
- Every webhook event is signature-verified against the raw body and deduplicated by `event.id`.
- Currency amounts are formatted via a `decimal_digits` helper, never hard-coded `* 100`.
- Card data never touches your servers. Use Checkout, Payment Element, or Elements with iframe isolation.

## Anti-Patterns

- Polling Stripe for state instead of consuming webhooks.
- Using the legacy `Charge` API for new code instead of `PaymentIntent`.
- Writing manual HMAC signature verification when an SDK helper exists.
- Returning `2xx` from the webhook only after heavy work completes (causes retries on timeout).
- Hard-coding `* 100` for amounts, breaking JPY, KRW, UGX, and other zero-decimal currencies.

## Outputs

- Working PHP and/or Node.js code that creates Customers and PaymentIntents.
- A signed, idempotent webhook receiver.
- A production checklist mapped to your secrets, observability, and deploy stack.

## References

- Use the `references/` directory for deep walkthroughs after reading the core workflow below.
<!-- dual-compat-end -->

Use this skill when Stripe is the payment rail. The goal is safe, retriable, webhook-driven payments that survive replays, partial failures, and SCA challenges.

## Load Order

1. `world-class-engineering`
2. `web-app-security-audit`, `api-design-first`, `cicd-devsecops` (for HTTPS, idempotent endpoints, Vault-managed keys)
3. This skill for Stripe mechanics
4. `subscription-billing` for recurring billing, dunning, metering, and revenue ops
5. `observability-monitoring` for PaymentIntent dashboards and webhook lag alerts

## §1 Why Stripe and How the Platform Is Structured

Stripe documents three primary ways to accept payments on a website:

- **Build a checkout page**: Stripe-hosted page, embedded form, or embedded components.
- **Accept payments without code**: Payment Links create a custom page without code.
- **Build an advanced integration**: embed a custom Stripe payment form using Elements.

Stripe's official guidance for new builds: prefer the **Checkout Sessions API with the Payment Element** over direct Payment Intents for most integrations. Use raw Payment Intents only when explicitly required. Source: `docs.stripe.com/payments`, `docs.stripe.com/payments/accept-a-payment`.

## §2 Core API Objects

Only the objects needed for one-time and saved-card flows. Recurring entities live in `subscription-billing`.

- **Customer** — long-lived record with email, name, default PaymentMethod, tax data. Required to save a card for off-session charges.
- **PaymentMethod** — tokenised card, bank debit, or wallet attachable to a Customer.
- **PaymentIntent** — modern object that "tracks a payment from creation through checkout, and triggers additional authentication steps when required." Provides automatic authentication handling, no double charges, and explicit SCA support.
- **SetupIntent** — saves a PaymentMethod for future use without an immediate charge.
- **Checkout Session** — wraps Hosted or Embedded Checkout; creates a PaymentIntent (or Subscription) under the hood.
- **Charge** (legacy) — present in the API and referenced from PaymentIntent; do not create directly in new code.

```text
 Customer ──► PaymentMethod
    │             │
    └── PaymentIntent / SetupIntent ──► Charge
        (Checkout Session wraps either)
```

## §3 Choosing an Integration Model

| Model | What you build | Card data lives | Complexity | Pick when |
|-------|----------------|-----------------|------------|-----------|
| Stripe-hosted Checkout | Redirect link or button | Stripe (lowest PCI scope) | 2/5 | Fastest path, standard pricing pages |
| Embedded Checkout | Stripe-hosted form mounted in your DOM | Stripe (low PCI scope) | 2/5 | Want Checkout's logic but stay on-domain |
| Checkout Sessions + Payment Element | Custom form using Stripe UI components | Stripe (PCI SAQ A) | 3/5 | Custom UX, multiple payment methods, design control |
| Payment Intents API direct | Hand-built confirmation flow | Stripe via Elements | Highest | Only when explicitly required |

Source: Stripe "Accept a payment" guide.

## §4 PHP Integration (stripe-php)

Runtime: PHP 7.2+. Install:

```bash
composer require stripe/stripe-php
```

```php
require_once 'vendor/autoload.php';
$stripe = new \Stripe\StripeClient(getenv('STRIPE_SECRET_KEY'));
```

Customer creation (verbatim shape from stripe-php README):

```php
$customer = $stripe->customers->create([
    'description' => 'example customer',
    'email' => 'email@example.com',
    'payment_method' => 'pm_card_visa',
]);
```

PaymentIntent creation. Required: `amount` (smallest currency unit) and `currency`. Common optional: `customer`, `payment_method`, `confirm`, `off_session`, `automatic_payment_methods`, `setup_future_usage`.

```php
$paymentIntent = $stripe->paymentIntents->create([
    'amount' => 1999,                   // $19.99 in smallest currency unit
    'currency' => 'usd',
    'customer' => $customer->id,
    'automatic_payment_methods' => ['enabled' => true],
], ['idempotency_key' => $uuidV4]);
```

**Save-a-card flow**: create a SetupIntent, confirm it client-side with Elements, then later create a PaymentIntent with `customer`, `payment_method` set to the saved method, plus `off_session: true` and `confirm: true`.

Full integration walkthrough: [references/stripe-php-integration.md](references/stripe-php-integration.md).

## §5 Node.js Integration (stripe-node)

Runtime: all LTS versions of Node.js 18+. Install:

```bash
npm install stripe
```

Customer creation, ESM / TypeScript (verbatim from stripe-node README):

```ts
import Stripe from 'stripe';
const stripeClient = new Stripe(process.env.STRIPE_SECRET_KEY!);

const customer = await stripeClient.customers.create({
  email: 'customer@example.com',
});
```

PaymentIntent:

```ts
const intent = await stripeClient.paymentIntents.create(
  {
    amount: 1999,
    currency: 'usd',
    customer: customer.id,
    automatic_payment_methods: { enabled: true },
  },
  { idempotencyKey: crypto.randomUUID() },
);
```

Full integration walkthrough: [references/stripe-nodejs-integration.md](references/stripe-nodejs-integration.md).

## §6 Webhooks

Webhooks are the durable source of truth for payment state. Polling is a bug.

**Endpoint requirements** (per `docs.stripe.com/webhooks`):

- Accept POST with JSON event payloads.
- Return a 2xx **before** executing complex logic that could time out.
- Register a publicly accessible HTTPS URL per environment (each gets its own `whsec_*`).

**Signature verification.** Use the SDK helper rather than implementing HMAC manually:

- PHP: `\Stripe\Webhook::constructEvent($payload, $sigHeader, $endpointSecret)`
- Node: `stripe.webhooks.constructEvent(payload, sigHeader, endpointSecret)`

The verifier needs the **raw request body**. In Express, mount `express.raw({ type: 'application/json' })` only on the webhook route. In Fastify, register a buffer parser. In PHP, read `file_get_contents('php://input')` before any framework body parsing.

**Manual verification reference** (only if no SDK):

1. Extract `t=` (timestamp) and `v1=` (signature) from the `Stripe-Signature` header.
2. Concatenate `timestamp + '.' + raw_body`.
3. HMAC-SHA256 with the endpoint secret as key.
4. Constant-time compare against the received `v1` signature.
5. Reject if timestamp skew exceeds tolerance (default 5 minutes).

**Retry semantics** (Stripe-side):

- Live mode: up to 3 days with exponential backoff.
- Sandbox: 3 retries over a few hours.
- Manual replay: up to 15 days via dashboard, 30 days via CLI.
- Manually resending an event does **not** dismiss Stripe's automatic retries.

**Idempotency at the receiver.** Persist `event.id` in MySQL with a unique index. Insert the event row and commit the side effect in the **same transaction** so replays no-op cleanly.

```sql
CREATE TABLE stripe_processed_events (
  event_id     VARCHAR(255) PRIMARY KEY,
  event_type   VARCHAR(100) NOT NULL,
  received_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  processed_at TIMESTAMP NULL,
  payload_hash CHAR(64) NOT NULL,
  INDEX idx_event_type (event_type, received_at)
);
```

Combine `event.type` with `data.object.id` to identify duplicates that span event IDs (e.g. retried charge attempts).

**Idempotency at the sender.** Send an `Idempotency-Key` HTTP header on every POST. Stripe stores the first response's status and body for that key and errors if subsequent requests arrive with mismatched parameters. Use V4 UUIDs (max 255 chars). Stripe may garbage-collect keys after 24 hours.

**Common event types** to subscribe to:

- `payment_intent.succeeded`, `payment_intent.payment_failed`, `payment_intent.requires_action`, `payment_intent.processing`, `payment_intent.canceled`
- `checkout.session.completed`
- `invoice.paid`, `invoice.payment_failed`, `invoice.finalized`, `invoice.upcoming`
- `customer.subscription.*` (delegate handling to `subscription-billing`)

Full event catalogue and handler patterns: [references/webhook-handling.md](references/webhook-handling.md).

## §7 3D Secure / SCA

Stripe requires Strong Customer Authentication in regulated regions; SCA "requires customers to use two-factor authentication like 3D Secure to verify their purchase." The Payment Intents API surfaces this via the `requires_action` status.

**PaymentIntent status enum**: `requires_payment_method`, `requires_confirmation`, `requires_action`, `processing`, `succeeded`, `canceled`.

**On-session vs off-session** (Stripe phrasing):

- **On-session**: a payment occurs while the customer is actively in your checkout flow and able to authenticate.
- **Off-session**: a payment occurs without the customer present, using previously-collected payment information.

Rules:

- For on-session flows where you intend to charge later, set `setup_future_usage: 'off_session'` on the PaymentIntent.
- For off-session flows, create the PaymentIntent with `off_session: true` and `confirm: true`.
- If Stripe returns `requires_action` on an off-session attempt, your dunning logic must email the customer back to authenticate. Hand recovery flows to `subscription-billing` when this happens inside a renewal cycle.

## §8 Multi-Currency

Stripe supports charging "in over 135 currencies."

- **Presentment currency**: the currency of the charge.
- **Settlement currency**: the currency accepted by your destination bank account.

If presentment differs from settlement, Stripe converts at deposit time, typically with a 1% FX spread.

**Zero-decimal currencies** (JPY, KRW, UGX, VND, RWF, and others): the `amount` value is the actual amount, not minor units. To charge 500 JPY, send `amount: 500`. For two-decimal currencies, multiply by 100 (10 USD → `1000`).

Ship a helper that maps ISO currency to its `decimal_digits` rather than hard-coding `* 100`:

```ts
const ZERO_DECIMAL = new Set(['BIF','CLP','DJF','GNF','JPY','KMF','KRW','MGA','PYG','RWF','UGX','VND','VUV','XAF','XOF','XPF']);
export function toMinorUnits(amount: number, currency: string): number {
  const code = currency.toUpperCase();
  return ZERO_DECIMAL.has(code) ? Math.round(amount) : Math.round(amount * 100);
}
```

## §9 Stripe Tax Basics

Stripe Tax automates "sales tax, VAT, and GST compliance on all your transactions" and "handles tax obligation monitoring, registrations, calculations, collections, and filings." It also tracks sales against local registration thresholds and alerts when obligations form.

Enable on a Checkout Session or Subscription:

```bash
curl https://api.stripe.com/v1/subscriptions \
  -u "$STRIPE_SECRET_KEY:" \
  -d "automatic_tax[enabled]=true"
```

Validate customer location at creation: `-d "tax[validate_location]=immediately"`.

**Tax IDs.** Customers can store country-specific Tax IDs (`eu_vat`, `gb_vat`, `au_abn`, and 200+ types). Collect them at Checkout via `tax_id_collection: { enabled: true }` and persist via `customers.createTaxId`. For B2B with valid IDs, Stripe applies reverse-charge automatically where applicable.

## §10 Local Testing

**Test card matrix** (success cases):

| Brand | Number | CVC |
|-------|--------|-----|
| Visa | 4242 4242 4242 4242 | any 3 digits |
| Mastercard | 5555 5555 5555 4444 | any 3 digits |
| American Express | 3782 822463 10005 | any 4 digits |
| Discover | 6011 1111 1111 1117 | any 3 digits |
| Diners Club | 3056 9300 0902 0004 | any 3 digits |
| JCB | 3566 0020 2036 0505 | any 3 digits |

All accept any future expiration date. Sandbox mode is isolated; test-key transactions don't move funds.

**Decline / authentication cards**: `4000 0025 0000 3155` (3DS required), `4000 0000 0000 0002` (generic decline), `4000 0000 0000 9995` (insufficient funds), `4000 0000 0000 0341` (attach succeeds, first off-session charge fails). Pull the full table from `docs.stripe.com/testing` when authoring decline tests.

**Stripe CLI** for local webhooks:

```bash
stripe login
stripe listen --forward-to localhost:4242/webhook
stripe trigger payment_intent.succeeded
stripe trigger invoice.payment_failed
```

The CLI prints a webhook signing secret on first run; pass it as the `endpoint_secret` argument to the SDK verification helper.

## §11 Production Checklist

- [ ] Live and test secret keys stored only in Vault (or equivalent secrets manager); rotated via the `cicd-devsecops` runbook; never in committed `.env`.
- [ ] Restricted API keys (`rak_*`) used for read-only or scoped integrations; full secret keys live only in admin operations.
- [ ] Webhook endpoint verified with the SDK helper; raw body preserved end-to-end.
- [ ] Webhook handler is idempotent: `event.id` persisted with a unique index in MySQL; side-effect commit in the same transaction.
- [ ] `Idempotency-Key` (V4 UUID) on every server-side `paymentIntents.create` call.
- [ ] PaymentIntent status transitions observed via dashboards (cross-ref `observability-monitoring`).
- [ ] Currency amounts formatted via `toMinorUnits()`, not `* 100`.
- [ ] Test-mode webhook fixtures committed to repo; Stripe CLI replay wired in CI.
- [ ] TLS 1.2+ enforced; non-HTTPS webhook delivery rejected.
- [ ] Webhook secret rotation runbook in place: create new endpoint secret, deploy with both old and new for 24h, remove old.
- [ ] Stripe request IDs and webhook event IDs logged with internal correlation IDs.
- [ ] Full API keys and full webhook payloads never logged at info level (PAN last-four and PII).

## Standards

**Security.** Never store raw card data; use Stripe-hosted collection or Elements. Keep secret keys server-side only. Verify every webhook signature and reject unsigned payloads. Stripe's redirect and hosted-field model keeps card data off your servers, limiting PCI scope to SAQ A.

**Data and state.** Stripe object IDs map to internal customer and entitlement records. Access derives from PaymentIntent and Invoice state through verified events. Refunds and cancellations update internal state through durable transitions, never optimistic writes.

**UX.** Tell the user whether payment is pending, requires action, failed, or complete. Surface SCA prompts immediately. Offer self-service payment-method updates.

**Operations.** Log Stripe request IDs, webhook event IDs, and internal correlation IDs together. Keep a replay-safe processor and a manual reprocess path. Emit release markers around payment-flow changes.

## Review Checklist

- [ ] Integration model in §3 chosen explicitly; PCI-scope target documented.
- [ ] Customers and payment methods stored by reference, not raw card data.
- [ ] PaymentIntents handle `requires_action` and async completion.
- [ ] Save-a-card flows use SetupIntent then off-session PaymentIntent with `confirm: true`.
- [ ] Every Stripe mutation uses `Idempotency-Key` (V4 UUID).
- [ ] Webhooks verify signatures against the raw body and are replay-safe via `event.id` + unique index.
- [ ] Currency math goes through a `decimal_digits` helper.
- [ ] Test mode covers SCA challenge, decline, insufficient funds, and webhook signature failure.
- [ ] Stripe Tax enabled where required; tax IDs collected for B2B.
- [ ] Production checklist completed before promoting to live keys.

## Companion Skills

- `subscription-billing` — recurring billing, plan changes, dunning, proration, metered usage, revenue recognition, customer portal.
- `saas-accounting-system` — double-entry posting of Stripe settlements, refunds, FX conversions.
- `ai-saas-billing` — AI module gating and per-tenant token metering on top of Stripe.
- `web-app-security-audit` — payment endpoints, webhook handlers, key-handling posture.
- `cicd-devsecops` — Vault-managed key rotation and secret distribution.
- `observability-monitoring` — PaymentIntent dashboards and webhook lag alerts.

## Sources

- [references/stripe-php-integration.md](references/stripe-php-integration.md) — PHP 7.2+ patterns for Customers, PaymentIntents, SetupIntents, and webhooks.
- [references/stripe-nodejs-integration.md](references/stripe-nodejs-integration.md) — Node.js 18+ / TypeScript patterns for the same flows.
- [references/webhook-handling.md](references/webhook-handling.md) — event catalogue, dedup rules, idempotent state updates.
- [../subscription-billing/SKILL.md](../subscription-billing/SKILL.md) — recurring billing, dunning, metered billing, revenue ops.
- [../saas-accounting-system/SKILL.md](../saas-accounting-system/SKILL.md) — accounting integration for Stripe settlements.
- [../../security/web-app-security-audit/SKILL.md](../../security/web-app-security-audit/SKILL.md) — security audit for payment endpoints.
- Stripe Payments overview: `docs.stripe.com/payments`
- Stripe "Accept a payment": `docs.stripe.com/payments/accept-a-payment`
- Stripe Payment Intents overview: `docs.stripe.com/payments/payment-intents`
- Stripe API — Create a PaymentIntent: `docs.stripe.com/api/payment_intents/create`
- Stripe Webhooks: `docs.stripe.com/webhooks`
- Stripe API — Idempotent Requests: `docs.stripe.com/api/idempotent_requests`
- Stripe API — Event Types: `docs.stripe.com/api/events/types`
- Stripe Currencies: `docs.stripe.com/currencies`
- Stripe Tax: `docs.stripe.com/tax` and `docs.stripe.com/tax/subscriptions`
- Stripe Customer Tax IDs: `docs.stripe.com/billing/customer/tax-ids`
- Stripe Testing: `docs.stripe.com/testing`
- stripe/stripe-php README: `github.com/stripe/stripe-php`
- stripe/stripe-node README: `github.com/stripe/stripe-node`
