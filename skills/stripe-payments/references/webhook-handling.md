# Webhook Handling

Use this reference when mapping Stripe events into SaaS account state, entitlements, and billing recovery.

## Core Rules

- Verify signatures against the raw body before doing anything else.
- Persist event receipt with `event.id`.
- Make each event handler idempotent.
- Prefer queue-based processing and fast `2xx` responses.

## Event Catalogue

### `customer.subscription.created`

- Create or update the internal subscription record.
- Store Stripe subscription ID, plan, status, trial dates, and period dates.
- Do not grant access solely because the object exists if payment is still incomplete.

### `customer.subscription.updated`

- Reconcile plan, status, `cancel_at_period_end`, pause state, and period boundaries.
- Update entitlements only from the new subscription state.
- Use versioned state-transition logic to avoid reopening cancelled access accidentally.

### `customer.subscription.deleted`

- Mark the subscription ended.
- Schedule or apply entitlement removal according to `current_period_end`.
- Keep billing history and audit trail.

### `invoice.payment_succeeded` or `invoice.paid`

- Mark the invoice paid.
- Extend or confirm access when the linked subscription is active.
- Record revenue-side facts and send receipts or in-app confirmation if needed.

### `invoice.payment_failed`

- Mark the invoice or renewal as failed.
- Trigger dunning workflow.
- Put account into grace, warning, or restricted state according to policy.
- Never cancel immediately unless your business rules explicitly require it.

### `payment_intent.succeeded`

- Mark one-time payment or setup flow complete.
- Reconcile it to the internal order, invoice, or onboarding step.
- Avoid using this alone for subscription entitlement if invoice events provide the safer signal.

### `charge.refunded`

- Record the refund locally.
- Adjust entitlements only if the refund invalidates access.
- Keep audit records for finance and support.

## Idempotent Update Pattern

Suggested database pattern:

1. Insert webhook receipt keyed by `stripe_event_id`.
2. If duplicate key conflict occurs, acknowledge and stop.
3. Load the current business record.
4. Apply a state transition only if the incoming event moves the record forward or changes meaningful attributes.
5. Commit the transition and mark the event processed.

## What to Persist

- Stripe event ID
- event type
- related Stripe object IDs
- received timestamp
- processing status
- failure reason if processing fails
- internal correlation IDs

## Replay and Recovery

- Support safe reprocessing from stored payloads or fetched event data.
- Keep failed events visible on an operator dashboard or queue.
- Do not rely on Stripe webhook delivery being exactly once or strictly ordered.
