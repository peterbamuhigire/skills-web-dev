# Stripe PHP Integration

Use this reference for PHP 8+ servers integrating Stripe with `stripe/stripe-php`.

## Setup

```php
<?php

use Stripe\StripeClient;

$stripe = new StripeClient($_ENV['STRIPE_SECRET_KEY']);
```

## Customer Create or Retrieve

```php
function ensureStripeCustomer(StripeClient $stripe, User $user): string
{
    if ($user->stripe_customer_id) {
        return $user->stripe_customer_id;
    }

    $customer = $stripe->customers->create([
        'email' => $user->email,
        'name' => $user->full_name,
        'metadata' => [
            'app_user_id' => (string) $user->id,
        ],
    ], [
        'idempotency_key' => 'customer-create:' . $user->id,
    ]);

    $user->stripe_customer_id = $customer->id;
    $user->save();

    return $customer->id;
}
```

## PaymentIntent Create and Confirm Flow

```php
function createPaymentIntent(StripeClient $stripe, string $customerId, int $amountCents, string $currency): array
{
    $intent = $stripe->paymentIntents->create([
        'amount' => $amountCents,
        'currency' => $currency,
        'customer' => $customerId,
        'automatic_payment_methods' => ['enabled' => true],
        'metadata' => [
            'flow' => 'setup-fee',
        ],
    ], [
        'idempotency_key' => 'pi:' . $customerId . ':' . $amountCents . ':' . $currency,
    ]);

    return [
        'payment_intent_id' => $intent->id,
        'client_secret' => $intent->client_secret,
        'status' => $intent->status,
    ];
}
```

Handle outcomes:

- `succeeded`: payment complete
- `requires_action`: collect 3DS or SCA authentication on the client
- `requires_payment_method`: tell the user the payment method failed and collect a new one

## Subscription Create

```php
function createSubscription(
    StripeClient $stripe,
    string $customerId,
    string $priceId,
    ?string $defaultPaymentMethodId = null
): \Stripe\Subscription {
    $payload = [
        'customer' => $customerId,
        'items' => [['price' => $priceId]],
        'payment_behavior' => 'default_incomplete',
        'expand' => ['latest_invoice.payment_intent'],
        'trial_period_days' => 14,
    ];

    if ($defaultPaymentMethodId) {
        $payload['default_payment_method'] = $defaultPaymentMethodId;
    }

    return $stripe->subscriptions->create($payload, [
        'idempotency_key' => 'sub-create:' . $customerId . ':' . $priceId,
    ]);
}
```

## Subscription Update with Proration

```php
function changeSubscriptionPlan(
    StripeClient $stripe,
    string $subscriptionId,
    string $subscriptionItemId,
    string $newPriceId,
    string $prorationBehavior = 'always_invoice'
): \Stripe\Subscription {
    return $stripe->subscriptions->update($subscriptionId, [
        'items' => [[
            'id' => $subscriptionItemId,
            'price' => $newPriceId,
        ]],
        'proration_behavior' => $prorationBehavior,
    ], [
        'idempotency_key' => 'sub-change:' . $subscriptionId . ':' . $newPriceId,
    ]);
}
```

## Customer Portal Session

```php
function createPortalSession(StripeClient $stripe, string $customerId, string $returnUrl): string
{
    $session = $stripe->billingPortal->sessions->create([
        'customer' => $customerId,
        'return_url' => $returnUrl,
    ], [
        'idempotency_key' => 'portal:' . $customerId,
    ]);

    return $session->url;
}
```

## Webhook Endpoint

```php
<?php

use Stripe\Exception\SignatureVerificationException;
use Stripe\Webhook;

$payload = file_get_contents('php://input');
$sigHeader = $_SERVER['HTTP_STRIPE_SIGNATURE'] ?? '';
$endpointSecret = $_ENV['STRIPE_WEBHOOK_SECRET'];

try {
    $event = Webhook::constructEvent($payload, $sigHeader, $endpointSecret);
} catch (\UnexpectedValueException $e) {
    http_response_code(400);
    exit('Invalid payload');
} catch (SignatureVerificationException $e) {
    http_response_code(400);
    exit('Invalid signature');
}

queueStripeEventForProcessing($event->id, $event->type, $payload);
http_response_code(200);
```

Important:

- use the raw request body
- verify before parsing business meaning
- store or deduplicate on `event.id`
- return `200` before slow downstream work
