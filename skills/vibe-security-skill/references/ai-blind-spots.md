# AI Code Generation Blind Spots

Parent: [../SKILL.md](../SKILL.md).

The six defects AI-generated code reliably produces. Review every generated feature against this file before merge.

## 1. IDOR and missing tenant scope

Almost every AI-generated feature allows a logged-in user to access other users' data by changing an id in the URL. The route is authenticated; the data access is not authorised.

Vulnerable:

```php
// Route::middleware('auth')->get('/orders/{id}', [OrderController::class, 'show']);
public function show($id) {
    return Order::find($id);
}
```

Fix — scope to tenant + user, 404 on miss (not 403, to prevent enumeration):

```php
public function show($id) {
    return Order::where('id', $id)
        ->where('tenant_id', auth()->user()->tenant_id)
        ->where('user_id', auth()->id())
        ->firstOrFail();
}
```

For multi-tenant SaaS, scope every query by `tenant_id`. For regulated data, pair application filters with PostgreSQL row-level security.

```sql
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON orders
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

Test: authenticate as user A and attempt to read user B's id. Expected: 404.

## 2. Webhook handlers without signature verification

Vulnerable:

```js
app.post('/webhook/stripe', (req, res) => {
  if (req.body.type === 'checkout.session.completed') {
    grantAccess(req.body.data.object.customer_email);
  }
  res.sendStatus(200);
});
```

Attacker:

```bash
curl -X POST https://yourapp.com/webhook/stripe \
  -H "Content-Type: application/json" \
  -d '{"type":"checkout.session.completed","data":{"object":{"customer_email":"attacker@x.com"}}}'
```

Fix — verify with the provider SDK against the raw body:

```js
app.post('/webhook/stripe', express.raw({type: 'application/json'}), (req, res) => {
  let event;
  try {
    event = stripe.webhooks.constructEvent(
      req.body,
      req.headers['stripe-signature'],
      process.env.STRIPE_WEBHOOK_SECRET,
    );
  } catch (err) {
    return res.sendStatus(400);
  }
  // idempotency
  if (await seenEvent(event.id)) return res.sendStatus(200);
  await recordEvent(event.id);
  // handle event
  res.sendStatus(200);
});
```

## 3. Secrets in the frontend bundle

Vulnerable exposure points:

- `NEXT_PUBLIC_*` or `REACT_APP_*` variables are shipped to the client. Never put server secrets behind them.
- Secret keys returned by server in JSON responses then cached client-side.
- `.map` source-map files served in production, exposing inlined env.

Fix — server actions or server-only routes:

```ts
// client — publishable key only
const stripe = await loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);

// server — secret stays on server
'use server';
import Stripe from 'stripe';
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);
export async function createCheckoutSession() { /* ... */ }
```

Check before deploy:

```bash
# grep the built bundle for leaked secrets
grep -r 'sk_live\|sk_test\|AKIA\|xoxb-' .next/
```

## 4. Plain-text or weak password storage + no rate limit

Vulnerable:

```php
$hash = md5($_POST['password']);
$user = DB::selectOne("SELECT * FROM users WHERE email=? AND password=?", [$email, $hash]);
// no lockout, no rate limit
```

Fix — Argon2id (or bcrypt cost 12+) plus dual-axis rate limit:

```php
// registration
$hash = password_hash($password, PASSWORD_ARGON2ID, [
    'memory_cost' => 65536, 'time_cost' => 4, 'threads' => 1,
]);

// login
if (!RateLimiter::attempt("login:$ip", 5, fn() => null, 900) ||
    !RateLimiter::attempt("login:$email", 5, fn() => null, 900)) {
    return response('Too many attempts', 429);
}
$user = User::where('email', $email)->first();
if (!$user || !password_verify($password, $user->password_hash)) {
    Log::warning('login_failed', ['email' => $email, 'ip' => $ip]);
    return response('Invalid credentials', 401);
}
// regenerate session id on login
session_regenerate_id(true);
```

Add breach-password check against HaveIBeenPwned k-anonymity API on registration and password change.

## 5. SQL built by string concatenation

Vulnerable:

```py
cursor.execute(f"SELECT * FROM orders WHERE user_id = {user_id} AND status = '{status}'")
```

Fix — parameters only, with tenancy:

```py
cursor.execute(
    """
    SELECT * FROM orders
    WHERE tenant_id = %s AND user_id = %s AND status = %s
    """,
    (tenant_id, user_id, status),
)
```

Linter rule: ban f-string SQL in CI. For Node, ban template-literal SQL unless wrapped in a safe-SQL tag.

## 6. Verbose errors leaking internals

Vulnerable response:

```json
{"error": "SQLSTATE[42S02]: Base table or view not found: orders_v2 at /srv/app/OrderRepo.php:147"}
```

Fix — split outward-facing message from server-side log:

```json
{"error": {"code": "ORDER_LOOKUP_FAILED", "message": "We could not process your request.", "request_id": "req_01J..."}}
```

Server-side logger captures stack trace, request id, tenant id. Client receives only the stable code and request id.

## Prompting hygiene

Weak prompt: "Create a login API."

Strong prompt: "Create a login API with Argon2id password verification, rate limit 5 per 15 min per IP and per email with 429 on exceed, CSRF protection if cookie-based, session regenerate on success, generic error messages, and an authz check that verifies resource ownership on the /me route."

## Review checklist before merging AI-generated code

- [ ] Every authenticated data endpoint filters by tenant/owner.
- [ ] Every webhook verifies the provider signature.
- [ ] No server secret appears in any file that ships to the client.
- [ ] Login, password reset, and registration are rate-limited by IP and by identifier.
- [ ] Every SQL statement is parameterised.
- [ ] Errors return a code + request id, not a stack trace.
- [ ] Sessions regenerate on auth state change.
- [ ] Output encoding matches the render context (HTML vs attribute vs JS vs URL).

## Test snippets

```bash
# IDOR
curl -H "Authorization: Bearer USER_A_TOKEN" https://api.example.com/orders/USER_B_ORDER_ID
# Expect: 404.

# Rate limit
for i in {1..20}; do curl -s -o /dev/null -w "%{http_code}\n" \
  -X POST https://api.example.com/login -d "email=test@x.com&password=wrong"; done
# Expect: 200...200 then 429.

# Webhook signature
curl -X POST https://api.example.com/webhook/stripe \
  -H "Content-Type: application/json" \
  -d '{"type":"checkout.session.completed"}'
# Expect: 400.

# XSS reflection
curl -s "https://api.example.com/search?q=%3Cscript%3Ealert(1)%3C%2Fscript%3E" | grep -o '<script>'
# Expect: empty (encoded).
```
