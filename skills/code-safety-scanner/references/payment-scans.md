# Payment Safety Scan Patterns (Check 14)

Detailed analysis for Category C: Payment misconfigurations and duplicate charge prevention.

## Check 14: Duplicate Charge Risk

### The Attack Scenario

1. User clicks "Pay Now"
2. Request is slow (network, server load)
3. User clicks again (or browser retries)
4. Two payment intents created, user charged twice
5. Refund process needed, customer trust damaged

### Client-Side Scan

#### Button State Management

```
# Look for payment submit buttons WITHOUT disable logic
<button.*pay|submit.*payment|place.*order|checkout
onClick.*pay|handlePayment|submitPayment|processPayment

# GOOD patterns (should exist):
disabled={loading}|disabled={processing}|disabled={submitting}
setLoading(true)|setProcessing(true)|setSubmitting(true)
btn.disabled = true|button.disabled = true
preventDefault().*disabled

# BAD patterns (missing protection):
# Payment handler that doesn't set loading state
# Form without onSubmit handler (allows multiple submits)
# No spinner/loading indicator during payment
```

#### Form Resubmission

```
# HTML forms posting to payment endpoints
<form.*action.*pay|charge|checkout|order
# Check: is there JavaScript preventing double submit?
# Check: does the form use POST-redirect-GET pattern?

# React/Vue/Svelte forms
onSubmit|handleSubmit|@submit
# Check: is there loading state preventing resubmission?
```

### Server-Side Scan

#### Idempotency Keys

```
# Stripe - CRITICAL check
stripe.*create\(|stripe.*charges.*create|stripe.*paymentIntents.*create
# Must include: idempotency_key or idempotencyKey parameter
# Pattern: Idempotency-Key header or idempotency_key in options

# PayPal
paypal.*create|paypal.*execute
# Check for order ID deduplication

# Generic payment APIs
/api.*(pay|charge|checkout|transaction).*POST
# Check: is there an idempotency mechanism?
```

#### Server-Side Deduplication

```
# Good pattern: check for existing payment before creating
SELECT.*FROM.*(payments|transactions|charges|orders).*WHERE
# Should check: same user + similar amount + recent time window

# Good pattern: unique constraint on payment reference
UNIQUE.*payment_ref|UNIQUE.*idempotency_key|UNIQUE.*transaction_id

# Good pattern: status check before processing
if.*status.*==.*('pending'|'processing'|'completed')
WHERE.*status.*=.*'pending'
```

#### Transaction Atomicity

```
# Payment + order creation should be atomic
BEGIN|START TRANSACTION|transaction\(|\.transaction\(
# Check: does payment creation + order update happen in same transaction?

# Bad pattern: payment created, then order update can fail
await stripe.*create
await db.*update     # if this fails, payment exists but order doesn't

# Good pattern: wrap in transaction
await db.transaction(async (trx) => {
    // create order
    // create payment
    // update inventory
})
```

#### Webhook Deduplication

```
# Webhook handlers for payment events
webhook|stripe.*event|payment.*hook|ipn
# Check: is event ID stored and checked for duplicates?

# Good patterns:
# - Store processed event IDs in DB
# - Check IF NOT EXISTS before processing
# - Use unique constraint on event_id

# Bad patterns:
# - Process webhook without checking if already processed
# - No idempotent handling of repeated webhook deliveries
```

### Stack-Specific Patterns

#### PHP

```php
// Stripe PHP - check for idempotency
$stripe->paymentIntents->create([
    'amount' => $amount,
    'currency' => 'usd',
    // MUST HAVE: 'idempotency_key' => $key
], ['idempotency_key' => $uniqueKey]);

// Database deduplication
$existing = $pdo->prepare("SELECT id FROM payments WHERE idempotency_key = ?");
// Process only if no existing record
```

#### Node.js

```javascript
// Stripe Node - check for idempotency
const paymentIntent = await stripe.paymentIntents.create({
    amount: amount,
    currency: 'usd',
}, {
    idempotencyKey: uniqueKey,  // MUST HAVE
});

// Express - rate limiting on payment endpoint
app.post('/api/pay', rateLimiter, async (req, res) => {
    // Should also check for duplicate in DB
});
```

#### Python

```python
# Stripe Python - check for idempotency
stripe.PaymentIntent.create(
    amount=amount,
    currency='usd',
    idempotency_key=unique_key,  # MUST HAVE
)
```

### Severity Classification

| Finding | Severity |
|---------|----------|
| No idempotency key on payment API calls | CRITICAL |
| No client-side button disable | HIGH |
| No server-side deduplication | CRITICAL |
| No webhook deduplication | HIGH |
| Missing transaction around payment + order | HIGH |
| No loading state during payment | MEDIUM |
| No POST-redirect-GET after payment | MEDIUM |

### Remediation Checklist

1. Add idempotency key to every payment API call
2. Disable submit button on click, show loading spinner
3. Store idempotency key in DB with unique constraint
4. Check for existing payment before creating new one
5. Wrap payment + order in database transaction
6. Store webhook event IDs, check before processing
7. Implement POST-redirect-GET after successful payment
8. Add rate limiting on payment endpoints
