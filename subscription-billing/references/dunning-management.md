# Dunning Management

Use this reference when payment failures need a deliberate recovery sequence instead of ad hoc support intervention.

## Example Dunning Sequence

- Day 0: `invoice.payment_failed` received, send payment-failed email and in-app warning
- Day 3: retry automatically, send reminder with update-payment-method link
- Day 7: retry again, show stronger in-app banner and restrict high-cost actions if policy requires
- Day 14: send suspension warning and customer-success outreach for higher-value accounts
- Day 21: cancel or suspend according to policy if payment remains unresolved

## Smart Retries vs Manual Policy

- Smart Retries can improve recovery for many card-failure scenarios.
- Manual schedules are useful when contractual, operational, or customer-success requirements are stricter than Stripe defaults.
- Whatever you choose, document the entitlement state at each day in the sequence.

## State Model

- `active`: all features available
- `past_due`: service active with payment warnings
- `grace`: service active or partially restricted, high-visibility warnings
- `suspended`: access restricted pending payment update
- `canceled`: recurring access removed, win-back sequence may start

## What to Communicate

- what happened
- whether service is still active
- what date access changes if unresolved
- the exact next action the customer should take
