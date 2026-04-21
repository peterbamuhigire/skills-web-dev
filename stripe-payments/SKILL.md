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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | Stripe webhook + flow test plan | Markdown doc covering checkout, subscription lifecycle, customer portal, and webhook signature verification tests | `docs/billing/stripe-tests.md` |
| Security | Stripe key handling note | Markdown doc covering API key storage, webhook secret rotation, and per-environment configuration | `docs/billing/stripe-key-handling.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Use this skill when Stripe is the payment and billing backbone. The goal is to make payment flows safe, retriable, webhook-driven, and compatible with recurring SaaS billing instead of treating Stripe as a synchronous charge API.

## Load Order

1. Load `world-class-engineering`.
2. Load `deployment-release-engineering`, `advanced-testing-strategy`, and `vibe-security-skill` for release, test, and security controls.
3. Load this skill for Stripe mechanics.
4. Load `subscription-billing` for pricing tiers, dunning, metering, and revenue operations.

## Stripe Object Model

```text
 Customer ──► PaymentMethod
    │
    │   Product ◄── Price ──┐
    │                       │
    └── Subscription ── items ──► Invoice ──► PaymentIntent ──► Charge
```

- `Product` is the sellable unit; `Price` is amount, currency, recurrence.
- `Customer` owns payment methods, subscriptions, invoices, tax IDs.
- `Subscription` binds a customer to Prices via `subscription_items`.
- `Invoice` generates per period; `PaymentIntent` settles it.

## Setup

Two keys per environment: `publishable` (client-side) and `secret` (server only). Never commit secret keys. Use restricted keys (`rak_*`) for read-only integrations. Env vars: `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_ACCOUNT_COUNTRY`.

```bash
composer require stripe/stripe-php
npm install stripe
```

```php
<?php
require __DIR__ . '/vendor/autoload.php';
\Stripe\Stripe::setApiKey(getenv('STRIPE_SECRET_KEY'));
\Stripe\Stripe::setApiVersion('2024-06-20');
\Stripe\Stripe::setAppInfo('MyApp', '1.0.0', 'https://example.com');
```

```ts
import Stripe from 'stripe';
export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY as string,
  { apiVersion: '2024-06-20', maxNetworkRetries: 2 });
```

## Products & Prices API

Products are created once per SKU; Prices are versioned amounts attached to that Product. Use `lookup_key` so application code references stable identifiers rather than `price_*` IDs.

```ts
const product = await stripe.products.create({
  name: 'Pro Plan', metadata: { plan_code: 'pro' },
});
await stripe.prices.create({ product: product.id, currency: 'usd', unit_amount: 4900,
  recurring: { interval: 'month' }, lookup_key: 'pro_monthly_usd' });
await stripe.prices.create({ product: product.id, currency: 'usd', unit_amount: 49000,
  recurring: { interval: 'year' }, lookup_key: 'pro_annual_usd' });
await stripe.prices.create({ product: product.id, currency: 'usd', unit_amount: 9900,
  lookup_key: 'pro_setup_fee' });
const resolved = await stripe.prices.list({
  lookup_keys: ['pro_monthly_usd'], expand: ['data.product'],
});
```

- One-time Prices omit `recurring`; use them for setup fees, credits, add-ons.
- To change an amount, archive the old Price and create a new one with the same `lookup_key`.

## Checkout Sessions

Stripe Checkout is the hosted payment page; it handles SCA, 3DS, and card routing. Use `mode: 'subscription'` for recurring; `mode: 'payment'` for one-time.

```ts
const session = await stripe.checkout.sessions.create({
  mode: 'subscription', customer: customerId,
  line_items: [{ price: 'price_ABC123', quantity: 1 }],
  success_url: 'https://app.example.com/billing/success?session_id={CHECKOUT_SESSION_ID}',
  cancel_url: 'https://app.example.com/billing/cancel',
  allow_promotion_codes: true, automatic_tax: { enabled: true },
  subscription_data: { trial_period_days: 14, metadata: { tenant_id: tenantId } },
  metadata: { tenant_id: tenantId, initiated_by: userId },
});
```

- Pre-create the Customer before opening Checkout so the Stripe customer ID is already linked to your tenant.
- `metadata` propagates to the Subscription and Invoice; webhook handlers resolve the tenant from it.
- Never pass `customer_email` and `customer` together; Stripe rejects it.

## Customer Portal

Stripe-hosted self-service for plan changes, invoice downloads, payment-method updates, and cancellations. Configure once in Dashboard; reuse configuration IDs for branded variants.

```ts
const portal = await stripe.billingPortal.sessions.create({
  customer: customerId,
  return_url: 'https://app.example.com/settings/billing',
  configuration: 'bpc_1NrXYZ...',
});
```

- Use separate configurations for self-serve tiers (allow cancel + plan switch) versus enterprise (read-only invoice access).
- The portal emits the same webhook events as any other surface; no special handling needed.

## Webhook Architecture

Webhooks are the durable source of truth for billing state. Polling is a bug; every state transition must be driven by a verified webhook event.

- Register one HTTPS endpoint per environment; each has its own `whsec_*`.
- Verify every event using `Stripe-Signature` and the raw request body.
- Store `event.id` in a `stripe_processed_events` table with a unique index; insert before handling so replays become no-ops.
- Return `2xx` within 10 seconds; queue heavy work.

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

## Critical Webhook Events

| Event | Action |
|-------|--------|
| `customer.subscription.created` | Activate account features; provision entitlements; write plan code to the tenant record. |
| `customer.subscription.updated` | Compare `previous_attributes.items` vs current items; apply upgrade/downgrade; adjust seat counts. |
| `customer.subscription.deleted` | Revoke paid features; move tenant to free tier; enqueue retention email and data-export grace notice. |
| `invoice.payment_succeeded` | Extend billing period; refresh usage quota; emit revenue-recognized event for accounting. |
| `invoice.payment_failed` | Start dunning sequence; record failure count; schedule Smart Retry; email the billing contact. |
| `customer.subscription.trial_will_end` | Send upgrade email with payment-method collection link three days before trial expiry. |

## Subscription States

```text
incomplete ──► trialing ──► active ──► paused
                              │
                              ▼ (payment fails)
                           past_due ──► unpaid ──► cancelled
```

- `trialing → active`: first `invoice.payment_succeeded` after trial.
- `active → past_due`: latest invoice `open` after failed payment; usable during grace.
- `past_due → unpaid`: Smart Retries exhausted with `charge_automatically`.
- `unpaid → cancelled`: auto-cancel per subscription settings or manual cancel.
- `active → paused`: administrative pause; no invoices generate until resumed.

## Dunning Management

Enable Smart Retries in Dashboard for `charge_automatically` subscriptions; set max retry window to 21 days for SaaS. Custom Automations schedule: day 0 initial attempt; day 3 retry + failure email; day 7 retry + pause warning; day 14 retry + final notice; day 21 downgrade to free with 30-day data preservation.

```ts
function entitlementFor(sub: Stripe.Subscription, graceDays = 7) {
  if (sub.status === 'active' || sub.status === 'trialing') return 'paid';
  if (sub.status === 'past_due') {
    const graceEnd = sub.current_period_end * 1000 + graceDays * 86_400_000;
    return Date.now() < graceEnd ? 'paid_grace' : 'free';
  }
  return 'free';
}
```

## Tax Handling

Stripe Tax auto-calculates VAT, GST, and US sales tax based on customer address and product tax code. Enable per Price or on the account default; collect address at Checkout.

```ts
await stripe.checkout.sessions.create({
  mode: 'subscription', customer: customerId,
  line_items: [{ price: 'price_ABC123', quantity: 1 }],
  automatic_tax: { enabled: true },
  customer_update: { address: 'auto', name: 'auto' },
  tax_id_collection: { enabled: true },
  success_url: '...', cancel_url: '...',
});
await stripe.customers.createTaxId(customerId, { type: 'eu_vat', value: 'DE123456789' });
```

- Invoice line items include `tax_amounts` with jurisdiction, rate, and inclusive/exclusive treatment.
- For B2B customers with a valid tax ID, Stripe applies reverse-charge automatically where applicable.

## Multi-Currency

`currency` is immutable on a Price. Presentment currency (customer-facing) is chosen at Checkout; settlement currency is determined by your Stripe account country.

```ts
await stripe.prices.create({ product: pid, currency: 'usd', unit_amount: 4900,
  recurring: { interval: 'month' }, lookup_key: 'pro_monthly_usd' });
await stripe.prices.create({ product: pid, currency: 'kes', unit_amount: 650000,
  recurring: { interval: 'month' }, lookup_key: 'pro_monthly_kes' });
await stripe.prices.create({ product: pid, currency: 'ugx', unit_amount: 18500000,
  recurring: { interval: 'month' }, lookup_key: 'pro_monthly_ugx' });
function resolvePriceFor(country: string) {
  if (country === 'KE') return 'pro_monthly_kes';
  if (country === 'UG') return 'pro_monthly_ugx';
  return 'pro_monthly_usd';
}
```

- UGX is zero-decimal in Stripe; `unit_amount` is the actual amount, not cents.
- USD settlement from non-USD Prices incurs a 1% FX spread.

## Metered Billing

```ts
const priced = await stripe.prices.create({
  product: productId, currency: 'usd',
  recurring: { interval: 'month', usage_type: 'metered', aggregate_usage: 'sum' },
  billing_scheme: 'tiered', tiers_mode: 'graduated',
  tiers: [
    { up_to: 1000, unit_amount: 0 },
    { up_to: 10000, unit_amount: 5 },
    { up_to: 'inf', unit_amount: 3 },
  ],
  lookup_key: 'api_calls_metered',
});

await stripe.subscriptionItems.createUsageRecord(subscriptionItemId, {
  quantity: 1247, timestamp: Math.floor(Date.now() / 1000), action: 'increment',
});

await stripe.billing.alerts.create({
  title: 'Usage over 80% of budget', filter: { customer: customerId },
  usage_threshold_config: { gte: 80000, meter: 'mtr_api_calls', recurrence: 'one_time' },
});
```

- Use `action: 'increment'` for append-only usage; `action: 'set'` for absolute snapshots (rarely correct).
- Batch usage records; a billing cron at 00:05 UTC covers most reporting needs.

## Testing

Test cards: `4242 4242 4242 4242` (success), `4000 0025 0000 3155` (3DS required), `4000 0000 0000 0002` (decline), `4000 0000 0000 9995` (insufficient funds), `4000 0000 0000 0341` (attach succeeds, first charge fails).

```bash
stripe login
stripe listen --forward-to localhost:3000/stripe/webhook
stripe trigger invoice.payment_failed
```

```ts
const clock = await stripe.testHelpers.testClocks.create({
  frozen_time: Math.floor(Date.now() / 1000), name: 'renewal-test' });
const customer = await stripe.customers.create({ test_clock: clock.id, email: 'c@x.com' });
await stripe.testHelpers.testClocks.advance(clock.id,
  { frozen_time: Math.floor(Date.now() / 1000) + 31 * 86400 });
```

## Security

Stripe's redirect and hosted-field model keeps card data off your servers, which limits PCI scope to SAQ A.

- Use Stripe Checkout, Payment Links, or Stripe Elements with iframe isolation. Never post raw card numbers to your server.
- Enforce TLS 1.2+; reject non-HTTPS webhook delivery.
- Store secret keys in a secrets manager (AWS Secrets Manager, Vault); never in committed `.env`.
- Rotate webhook secret on suspected leak: create new endpoint secret, deploy both old and new for 24 hours, remove old.
- Issue restricted API keys for integrations that only read data; scope to specific resources (e.g., `charges:read`).
- Log every Stripe request ID and signature verification outcome for audit trails.
- Never log full API keys or full webhook payloads at info level; they contain PAN last-four and email addresses.

## PHP Integration Pattern

Complete runnable example: checkout creation endpoint and webhook handler with signature verification and idempotent DB updates on `invoice.payment_succeeded`.

```php
<?php
// public/billing/create-checkout.php
declare(strict_types=1);
require __DIR__ . '/../../vendor/autoload.php';
\Stripe\Stripe::setApiKey(getenv('STRIPE_SECRET_KEY'));
\Stripe\Stripe::setApiVersion('2024-06-20');
header('Content-Type: application/json');
$payload = json_decode(file_get_contents('php://input'), true);
$tenantId = $payload['tenant_id'] ?? null;
$lookupKey = $payload['price_lookup_key'] ?? 'pro_monthly_usd';
if (!$tenantId) { http_response_code(400); exit(json_encode(['error' => 'tenant_id required'])); }
$db = new PDO(getenv('DB_DSN'), getenv('DB_USER'), getenv('DB_PASS'));
$stmt = $db->prepare('SELECT stripe_customer_id, email FROM tenants WHERE id = ?');
$stmt->execute([$tenantId]);
$tenant = $stmt->fetch(PDO::FETCH_ASSOC);
if (!$tenant['stripe_customer_id']) {
    $customer = \Stripe\Customer::create(
        ['email' => $tenant['email'], 'metadata' => ['tenant_id' => $tenantId]],
        ['idempotency_key' => 'customer-create-' . $tenantId]);
    $db->prepare('UPDATE tenants SET stripe_customer_id = ? WHERE id = ?')
       ->execute([$customer->id, $tenantId]);
    $tenant['stripe_customer_id'] = $customer->id;
}
$prices = \Stripe\Price::all(['lookup_keys' => [$lookupKey], 'limit' => 1]);
$session = \Stripe\Checkout\Session::create([
    'mode' => 'subscription', 'customer' => $tenant['stripe_customer_id'],
    'line_items' => [['price' => $prices->data[0]->id, 'quantity' => 1]],
    'success_url' => getenv('APP_URL') . '/billing/success?session_id={CHECKOUT_SESSION_ID}',
    'cancel_url' => getenv('APP_URL') . '/billing/cancel',
    'automatic_tax' => ['enabled' => true],
    'subscription_data' => ['metadata' => ['tenant_id' => $tenantId]],
    'metadata' => ['tenant_id' => $tenantId],
], ['idempotency_key' => 'checkout-' . $tenantId . '-' . time()]);
echo json_encode(['url' => $session->url]);
```

```php
<?php
// public/billing/webhook.php
declare(strict_types=1);
require __DIR__ . '/../../vendor/autoload.php';
\Stripe\Stripe::setApiKey(getenv('STRIPE_SECRET_KEY'));
$payload = file_get_contents('php://input');
$sig = $_SERVER['HTTP_STRIPE_SIGNATURE'] ?? '';
try {
    $event = \Stripe\Webhook::constructEvent($payload, $sig, getenv('STRIPE_WEBHOOK_SECRET'));
} catch (\Stripe\Exception\SignatureVerificationException $e) {
    http_response_code(400); exit('invalid signature');
}
$db = new PDO(getenv('DB_DSN'), getenv('DB_USER'), getenv('DB_PASS'));
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$ins = $db->prepare('INSERT IGNORE INTO stripe_processed_events (event_id, event_type, payload_hash) VALUES (?, ?, ?)');
$ins->execute([$event->id, $event->type, hash('sha256', $payload)]);
if ($ins->rowCount() === 0) { http_response_code(200); exit(json_encode(['duplicate' => true])); }
if ($event->type === 'invoice.payment_succeeded') {
    $inv = $event->data->object;
    $tenantId = $inv->subscription_details->metadata->tenant_id ?? null;
    if ($tenantId) {
        $db->prepare('UPDATE tenants SET billing_period_end = FROM_UNIXTIME(?), subscription_status = ?, last_paid_invoice_id = ? WHERE id = ?')
           ->execute([$inv->lines->data[0]->period->end, 'active', $inv->id, $tenantId]);
    }
} elseif ($event->type === 'customer.subscription.deleted') {
    $sub = $event->data->object;
    $tenantId = $sub->metadata->tenant_id ?? null;
    if ($tenantId) {
        $db->prepare('UPDATE tenants SET subscription_status = ? WHERE id = ?')->execute(['cancelled', $tenantId]);
    }
}
$db->prepare('UPDATE stripe_processed_events SET processed_at = NOW() WHERE event_id = ?')->execute([$event->id]);
http_response_code(200); echo json_encode(['received' => true]);
```

## Node.js Integration Pattern

Complete runnable example: Fastify route with raw body for signature verification, idempotency check on `event.id`, and async handler dispatch.

```ts
// src/server.ts
import Fastify from 'fastify';
import Stripe from 'stripe';
import { Pool } from 'pg';
import { createHash } from 'crypto';
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY as string,
  { apiVersion: '2024-06-20', maxNetworkRetries: 2 });
const db = new Pool({ connectionString: process.env.DATABASE_URL });
const fastify = Fastify({ logger: true });
fastify.addContentTypeParser('application/json', { parseAs: 'buffer' },
  (_req, body, done) => done(null, body));
fastify.post('/stripe/webhook', async (request, reply) => {
  const rawBody = request.body as Buffer;
  const signature = request.headers['stripe-signature'] as string;
  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(rawBody, signature,
      process.env.STRIPE_WEBHOOK_SECRET as string);
  } catch (err) {
    request.log.warn({ err }, 'signature verification failed');
    return reply.status(400).send('invalid signature');
  }
  const hash = createHash('sha256').update(rawBody).digest('hex');
  const ins = await db.query(
    `INSERT INTO stripe_processed_events (event_id, event_type, payload_hash)
     VALUES ($1, $2, $3) ON CONFLICT (event_id) DO NOTHING`,
    [event.id, event.type, hash]);
  if (ins.rowCount === 0) return reply.status(200).send({ duplicate: true });
  reply.status(200).send({ received: true });
  handleEventAsync(event).catch((err) =>
    request.log.error({ err, eventId: event.id }, 'handler failed'));
});
async function handleEventAsync(event: Stripe.Event) {
  if (event.type === 'invoice.payment_succeeded') {
    const inv = event.data.object as Stripe.Invoice;
    const tenantId = inv.subscription_details?.metadata?.tenant_id;
    if (!tenantId) return;
    await db.query(
      `UPDATE tenants SET subscription_status = 'active',
         billing_period_end = to_timestamp($1), last_paid_invoice_id = $2 WHERE id = $3`,
      [inv.lines.data[0]?.period?.end, inv.id, tenantId]);
  } else if (event.type === 'customer.subscription.deleted') {
    const sub = event.data.object as Stripe.Subscription;
    const tenantId = sub.metadata?.tenant_id;
    if (tenantId) {
      await db.query(`UPDATE tenants SET subscription_status = 'cancelled' WHERE id = $1`, [tenantId]);
    }
  }
  await db.query('UPDATE stripe_processed_events SET processed_at = NOW() WHERE event_id = $1', [event.id]);
}
fastify.listen({ port: 3000, host: '0.0.0.0' });
```

## Standards

Security: never store raw card data; use Stripe-hosted collection or Elements; keep secret keys server-side only; verify every webhook signature and reject unsigned payloads.

Data and state: Stripe object IDs must map to internal customer, plan, and entitlement records; access follows invoice and subscription state derived from verified events; refunds, cancellations, pauses, and plan changes update entitlements through durable state transitions.

UX: tell the user whether payment is pending, requires action, failed, or complete; avoid surprise prorations on upgrade or downgrade; offer self-service payment-method updates and billing history.

Operations: log Stripe request IDs, webhook event IDs, and internal correlation IDs together; keep a replay-safe webhook processor and a manual reprocessing path; emit release markers around billing-flow changes.

## Review Checklist

- [ ] Products, Prices, and internal entitlements are mapped explicitly.
- [ ] Customers and payment methods are stored by reference, not raw card data.
- [ ] PaymentIntents handle `requires_action` and asynchronous completion states.
- [ ] Subscription creation, trialing, and proration behavior are deliberate.
- [ ] Customer portal settings match the business rules for plan changes and cancellations.
- [ ] Every Stripe mutation uses idempotency.
- [ ] Webhooks verify signatures against the raw body and are replay-safe.
- [ ] Test mode covers SCA, decline, renewal, cancellation, and webhook failure paths.

## Companion Skills

- `subscription-billing` — pricing tiers, dunning strategy, revenue recognition, metered billing operations.
- `saas-accounting-system` — double-entry posting of Stripe settlements, refunds, and FX conversions.
- `ai-saas-billing` — AI module gating, per-tenant token metering, and overage billing on top of Stripe.
- `web-app-security-audit` — audit checklist for payment endpoints, webhook handlers, and key-handling posture.

## Sources

- [references/stripe-php-integration.md](references/stripe-php-integration.md): PHP 8+ integration patterns for Customers, PaymentIntents, subscriptions, and webhooks.
- [references/stripe-nodejs-integration.md](references/stripe-nodejs-integration.md): Node.js and TypeScript integration patterns for the same Stripe workflows.
- [references/webhook-handling.md](references/webhook-handling.md): SaaS webhook catalogue, deduplication rules, and idempotent state updates.
- [../subscription-billing/SKILL.md](../subscription-billing/SKILL.md): Subscription lifecycle, dunning, metered billing, and revenue operations.
- [../saas-accounting-system/SKILL.md](../saas-accounting-system/SKILL.md): Double-entry accounting integration for Stripe settlements.
- [../ai-saas-billing/SKILL.md](../ai-saas-billing/SKILL.md): Module gating and billing-pattern alignment for paid add-ons.
- [../web-app-security-audit/SKILL.md](../web-app-security-audit/SKILL.md): Web application security audit framework covering payment endpoints.
