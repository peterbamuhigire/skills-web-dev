# Stripe Node.js Integration

Use this reference for Node.js or TypeScript servers integrating Stripe with the official `stripe` package.

## Setup

```ts
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2025-03-31.basil',
});
```

## Customer Create or Retrieve

```ts
export async function ensureStripeCustomer(user: {
  id: string;
  email: string;
  fullName: string;
  stripeCustomerId?: string | null;
}) {
  if (user.stripeCustomerId) return user.stripeCustomerId;

  const customer = await stripe.customers.create({
    email: user.email,
    name: user.fullName,
    metadata: { app_user_id: user.id },
  }, {
    idempotencyKey: `customer-create:${user.id}`,
  });

  return customer.id;
}
```

## PaymentIntent Create

```ts
export async function createPaymentIntent(customerId: string, amount: number, currency: string) {
  const intent = await stripe.paymentIntents.create({
    amount,
    currency,
    customer: customerId,
    automatic_payment_methods: { enabled: true },
    metadata: { flow: 'setup-fee' },
  }, {
    idempotencyKey: `pi:${customerId}:${amount}:${currency}`,
  });

  return {
    id: intent.id,
    clientSecret: intent.client_secret,
    status: intent.status,
  };
}
```

## Subscription Create

```ts
export async function createSubscription(
  customerId: string,
  priceId: string,
  defaultPaymentMethodId?: string,
) {
  return stripe.subscriptions.create({
    customer: customerId,
    items: [{ price: priceId }],
    payment_behavior: 'default_incomplete',
    expand: ['latest_invoice.payment_intent'],
    trial_period_days: 14,
    ...(defaultPaymentMethodId
      ? { default_payment_method: defaultPaymentMethodId }
      : {}),
  }, {
    idempotencyKey: `sub-create:${customerId}:${priceId}`,
  });
}
```

## Subscription Update

```ts
export async function changeSubscriptionPlan(
  subscriptionId: string,
  subscriptionItemId: string,
  newPriceId: string,
  prorationBehavior: 'always_invoice' | 'create_prorations' | 'none' = 'always_invoice',
) {
  return stripe.subscriptions.update(subscriptionId, {
    items: [{ id: subscriptionItemId, price: newPriceId }],
    proration_behavior: prorationBehavior,
  }, {
    idempotencyKey: `sub-change:${subscriptionId}:${newPriceId}`,
  });
}
```

## Customer Portal Session

```ts
export async function createPortalSession(customerId: string, returnUrl: string) {
  const session = await stripe.billingPortal.sessions.create({
    customer: customerId,
    return_url: returnUrl,
  }, {
    idempotencyKey: `portal:${customerId}`,
  });

  return session.url;
}
```

## Express Webhook Handler

```ts
import express from 'express';

const app = express();

app.post(
  '/webhooks/stripe',
  express.raw({ type: 'application/json' }),
  async (req, res) => {
    const sig = req.headers['stripe-signature'];
    const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET!;

    let event: Stripe.Event;

    try {
      event = stripe.webhooks.constructEvent(req.body, sig as string, endpointSecret);
    } catch (err) {
      res.status(400).send('Invalid signature');
      return;
    }

    await enqueueStripeEvent(event.id, event.type, req.body.toString('utf8'));
    res.status(200).send('ok');
  },
);
```

Important:

- use `express.raw`, not JSON parsing middleware
- verify with the raw body
- queue work after signature verification
- deduplicate on `event.id`

## Error Handling

- `requires_action`: client must handle SCA or 3DS
- `requires_payment_method`: tell the user to retry with a different method
- `invoice.payment_failed`: send recovery email and show in-app billing issue state
- duplicate event delivery: no duplicate state transition if event is already processed
