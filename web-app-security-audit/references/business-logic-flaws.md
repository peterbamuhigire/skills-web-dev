# Business Logic Flaws

Purpose: a defender's reference for threat-modelling, detecting and preventing business logic vulnerabilities in PHP/JS/HTML SaaS apps.
Covers workflow bypasses, race conditions, price tampering, state machines and idempotency.

## 1. What Business Logic Flaws Are

Business logic flaws are not classical code defects. The syntax compiles, the parameters validate, the authentication is correct, the authorization check passes. Yet the attacker still walks away with money, data, or privileges they were never meant to have.

The root cause is that the application allows a sequence of operations which, individually, are all legal — but which collectively violate the intended workflow. Getting refunded without having made a purchase. Applying a single-use coupon twice. Receiving a product at a negative quantity that credits the account. Skipping the payment step of a plan upgrade.

These bugs are almost invisible to automated scanners because no syntactic rule is broken. They need human threat modelling: **what does the application assume about the order and frequency of steps, and what happens if those assumptions fail?**

## 2. Common Categories

- **Missing state transition validation** — moving from state A to state C without going through B.
- **Race conditions in multi-step flows** — two or more requests exploit a window between check and commit.
- **Price and quantity tampering** — the client submits values the server should have computed.
- **Coupon reuse or stacking** — applying single-use discounts multiple times or combining exclusive ones.
- **Workflow skipping** — hitting step N directly without completing step N-1.
- **Time-of-check / time-of-use (TOCTOU)** — a value is checked, then used, and the value has changed in between.
- **Negative and zero edge cases** — quantity `-1`, price `0`, timestamp `0`.
- **Integer overflow and underflow** — summing large values wraps past the max.
- **Replay of one-shot actions** — resubmitting a completed workflow token.
- **Forgotten admin backdoors** — "just in case" overrides left in production.

## 3. E-Commerce Examples

### Client-Side Price Tampering

A product page submits `POST /checkout` with `price=99.99`. The server stores that price in the order. An attacker changes it to `0.01`.

Defence: **the server computes the price from the product id and the current price list**. The client's price is never trusted.

```php
// WRONG — trusts client
$order->price = (float) $_POST['price'];

// RIGHT — look it up
$product = $productRepo->find((int) $_POST['product_id']);
if ($product === null) { throw new NotFoundException(); }
$order->price = $product->currentPrice;
```

### Single-Use Coupon Reused Concurrently

Two browser tabs submit the same coupon code in parallel. Each request checks "has this coupon been used?", both see "no", and both apply the discount.

Defence: unique constraint on `(coupon_id, order_id)` or `(coupon_id, user_id)` at the database, plus a transactional claim:

```php
$pdo->beginTransaction();
$pdo->prepare('SELECT id FROM coupons WHERE code = :c AND used_at IS NULL FOR UPDATE')
    ->execute(['c' => $code]);
$row = /* fetch */;
if ($row === false) {
    $pdo->rollBack();
    throw new CouponAlreadyUsedException();
}
$pdo->prepare('UPDATE coupons SET used_at = NOW(), used_by = :u WHERE id = :id')
    ->execute(['u' => $userId, 'id' => $row['id']]);
$pdo->commit();
```

`SELECT ... FOR UPDATE` locks the row; the second transaction waits, then sees `used_at` is set and rolls back.

### Negative Quantities

`POST /cart { quantity: -2 }`. If `total = price * quantity` is allowed to go negative, the order "credits" the user.

Defence: quantity validation at the boundary — `FILTER_VALIDATE_INT` with `min_range: 1`. Plus invariants at the checkout step.

### Cart Manipulation During Checkout

The user adds items, starts checkout, then in another tab modifies the cart while payment is in progress. The payment ends up for an unrelated amount.

Defence: **snapshot the cart** at the moment payment starts. The cart_snapshot row is what gets paid; later cart edits do not affect it. A unique `checkout_token` ties payment to snapshot.

### Refund Without Purchase

An endpoint `/api/refund` accepts an order id and issues credit. The ownership check was forgotten, or the order-state check was forgotten, and any id gets a refund.

Defences stack:

- Authorization check: the user owns the order (or is support staff).
- State check: the order is in state `paid`, not `refunded`, not `draft`.
- Idempotency: the same refund request cannot fire twice.
- Audit log: every refund is recorded with actor, target, and amount.

## 4. Account Lifecycle Exploits

- **Skipping email verification**: after signup, some endpoints should be unavailable until email is verified. If the check is in the UI only, attackers hit the endpoints directly.
- **Reusing a signup token**: a one-time token for password reset is valid a second time.
- **Upgrading a plan without payment confirmation**: the webhook from the payment provider is simulated or skipped, and the plan is upgraded on the "success redirect" URL (which the attacker can call directly).
- **Downgrading to retain paid features**: cancelling the subscription should schedule the downgrade at the end of the billing period; if the features are already pre-provisioned for the new period, they should be revoked on cancel.
- **Invite reuse**: an invitation link to an organisation is used by an outsider after the intended recipient has joined.

### Payment Webhook Defence

```php
// /webhook/stripe
$payload = file_get_contents('php://input');
$sig = $_SERVER['HTTP_STRIPE_SIGNATURE'] ?? '';

try {
    $event = Stripe\Webhook::constructEvent($payload, $sig, $webhookSecret);
} catch (Throwable $e) {
    http_response_code(400);
    exit;
}

// Only the webhook upgrades the plan.
// The /success redirect URL only displays a thank-you page.
```

Business state changes driven by payment must happen only on the signed webhook, never on a client-controlled redirect.

## 5. Race Condition Defences

Race conditions appear whenever "check then act" is not atomic. Classic shape:

```php
// RACE
$balance = $repo->getBalance($userId);
if ($balance >= $amount) {
    $repo->debit($userId, $amount);
    $repo->credit($otherUserId, $amount);
}
```

Two simultaneous calls both see sufficient balance and both debit, taking the account negative.

### Pessimistic Lock

```php
$pdo->beginTransaction();
$stmt = $pdo->prepare('SELECT balance FROM accounts WHERE user_id = :u FOR UPDATE');
$stmt->execute(['u' => $userId]);
$balance = (int) $stmt->fetchColumn();
if ($balance < $amount) {
    $pdo->rollBack();
    throw new InsufficientFundsException();
}
$pdo->prepare('UPDATE accounts SET balance = balance - :a WHERE user_id = :u')
    ->execute(['a' => $amount, 'u' => $userId]);
$pdo->commit();
```

### Optimistic Lock With Version Column

```sql
ALTER TABLE orders ADD COLUMN version INT NOT NULL DEFAULT 0;
```

```php
$updated = $pdo->prepare('
    UPDATE orders
    SET status = :new, version = version + 1
    WHERE id = :id AND version = :v
')->execute([
    'new' => 'shipped',
    'id' => $id,
    'v' => $expectedVersion,
]);
if ($pdo->rowCount() === 0) {
    throw new StaleStateException();
}
```

Optimistic locking suits high-read low-write workloads; pessimistic locking suits the opposite.

### Idempotency Keys

The client generates a UUID per logical operation and sends it as a header:

```http
POST /payments
Idempotency-Key: 8f2e0e4c-...
```

The server caches the response keyed by `(user, key)` for a TTL. Retries return the cached result. Duplicate submissions are safe.

### Single-Flight

Deduplicate in-flight work by a key; simultaneous requests wait on a single execution.

## 6. State Machines as Explicit Data

Scattered `if ($order->status === 'paid')` checks are bug magnets. Make the state machine an explicit data structure.

```php
final class OrderState
{
    public const DRAFT = 'draft';
    public const PENDING_PAYMENT = 'pending_payment';
    public const PAID = 'paid';
    public const SHIPPED = 'shipped';
    public const DELIVERED = 'delivered';
    public const CANCELLED = 'cancelled';
    public const REFUNDED = 'refunded';

    /** @var array<string, list<string>> */
    public const TRANSITIONS = [
        self::DRAFT => [self::PENDING_PAYMENT, self::CANCELLED],
        self::PENDING_PAYMENT => [self::PAID, self::CANCELLED],
        self::PAID => [self::SHIPPED, self::REFUNDED],
        self::SHIPPED => [self::DELIVERED],
        self::DELIVERED => [self::REFUNDED],
        self::CANCELLED => [],
        self::REFUNDED => [],
    ];

    public static function canTransition(string $from, string $to): bool
    {
        return in_array($to, self::TRANSITIONS[$from] ?? [], true);
    }
}
```

Every state change goes through a single function that consults `canTransition`. Illegal transitions return an error. The state machine is testable in isolation, and adding a new state forces explicit review of where it fits.

## 7. Numeric Edge Cases

- **Negative quantity**: reject at input validation with explicit `min_range`.
- **Zero quantity**: might be legitimate (display only) or a bug (line items with zero). Decide explicitly.
- **Maximum values**: `PHP_INT_MAX` is almost never a real business limit. Cap at a sensible value.
- **Floating-point money**: `0.1 + 0.2 !== 0.3`. Use BCMath (`bcadd`) or integer minor units (cents).
- **Currency conversion**: round once at commit time, not at each arithmetic step, or rounding errors accumulate.
- **Order of operations**: `(price * quantity) - discount` vs `price * (quantity - discount)` — pick one and encode it.
- **Integer overflow**: `2^31 - 1` in a 32-bit column breaks abruptly. Use `BIGINT` for sums; unsigned if negative is impossible.

## 8. Workflow Re-Entry Attacks

A multi-step flow (wizard, checkout, onboarding) passes the user through URLs A → B → C. The attacker directly POSTs to C without completing A and B.

Defence: the state of the flow lives in a server-side workflow token (not in a hidden form field, not in localStorage). Each step reads the token, checks the current step, and only advances if the request matches.

```php
final class WorkflowToken
{
    public function __construct(
        public readonly string $id,
        public readonly int $userId,
        public string $currentStep,
        public readonly int $expiresAt,
    ) {}
}
```

Expire short. Rotate after use. Bind to the user. Never trust the client to tell you which step it is on.

## 9. Idempotency

Any endpoint that changes state must be safe to call twice. That is not optional for payment flows — network retries are a fact of life, and duplicate charges are both illegal and reputation-ending.

Idempotency strategies:

- **Natural idempotency**: `PUT /profile { email: "..." }` is idempotent by shape. `POST /orders` is not.
- **Idempotency key**: the client supplies a unique key per logical action. The server caches `(key → response)` for a retention window.
- **Dedup by business identifier**: if each order has a client-assigned `reference`, `INSERT ... ON DUPLICATE KEY UPDATE` handles retries.
- **Request signature**: hash the request body and reject if seen within N seconds.

Client-side: prevent double submission (disable button, optimistic UI) but **never rely on the client**. Idempotency is a server contract.

## 10. Threat Modelling for Business Logic

Automated tools cannot discover these bugs. You need a structured human exercise.

### STRIDE Per Workflow

For each critical flow (signup, login, checkout, refund, password reset, plan change, invite), walk through:

- **S**poofing — can an attacker pretend to be someone else?
- **T**ampering — can they modify data in transit or state?
- **R**epudiation — can they deny an action they performed?
- **I**nformation disclosure — can they read data not theirs?
- **D**enial of service — can they block legitimate users?
- **E**levation of privilege — can they gain rights they should not have?

### Abuse Case Questions

- What if the user does step X twice?
- What if they skip step X?
- What if two users do step X at the same time?
- What if a value is negative, zero, or the maximum?
- What if they close the browser mid-step?
- What if the session expires between steps?
- What if the webhook never arrives?
- What if the webhook arrives twice?
- What if the third-party API returns an error after debit?

Each question is a candidate test case.

## 11. Testing Business Logic

- **Happy-path tests** are the starting point, not the end.
- **Negative-path tests**: every illegal state transition should be tested and asserted to fail.
- **Chaotic order tests**: run the steps of a workflow in every wrong order and verify rejection.
- **Concurrency tests**: fire N concurrent requests at the same resource. Count successes. Must match invariants.
- **Property-based testing**: generate random sequences and assert invariants (account balance never negative, total quantity equals sum of line items).
- **Load testing with race detection**: run stress tests under realistic concurrency and inspect for double-commits.

## 12. Logging and Alerting for Business Anomalies

Security logging is not just for intrusion detection. Business logic misuse leaves a behavioural fingerprint.

Alert on:

- Refunds above a threshold or outside normal hours.
- Rapid plan changes for the same account.
- Coupon usage spikes (one code redeemed hundreds of times in minutes).
- New accounts created from the same IP block in a short window.
- Abnormal time between signup and first purchase.
- Unusual ratios: refund amount / purchase amount, login count / session count.

An append-only audit log on every critical action (actor, target, before, after, timestamp, IP, user agent) makes post-incident forensics possible.

## 13. Anti-Patterns

- **Trusting client-side state**. The cart total on the page is a display; the authoritative total is computed server-side.
- **Using timestamps as identifiers**. Timestamps collide and are guessable.
- **"It will never happen in practice."** It will, on day one of a busy sale.
- **No audit log on money-moving actions**. You cannot investigate what you did not record.
- **Single-check idempotency** (just a "have I seen this request" cache with no TTL discipline, cache eviction and race on the cache itself).
- **Enforcing business rules only in the UI**. The UI is untrusted input; every rule must be re-checked on the server.
- **"Soft" state transitions** where illegal moves are merely logged, not blocked.
- **Sharing transaction boundaries across services**. Each service should own its transaction and compensate on failure.
- **Webhook handlers without signature verification**. Any attacker with the URL can simulate success.
- **Decisions based on the HTTP Referer**. Referer is spoofable and often absent.

## Cross-References

- `access-control-flaws.md` — authorization is the other half of business logic defence
- `input-validation-patterns.md` — input validation is the first gate before logic runs
- `audit-checklist-detailed.md` — parent skill's master audit checklist
- `api-design-first` skill — idempotency keys and REST conventions
- `saas-accounting-system` skill — double-entry accounting provides natural invariants
- `database-reliability` skill — transactions, expand-contract migrations, backup verification
- `dual-auth-rbac` skill — authorization patterns that back up logic checks
- OWASP Top 10: A04 Insecure Design
- OWASP Web Security Testing Guide: Business Logic Testing
