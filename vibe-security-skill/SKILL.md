---
name: vibe-security-skill
description: Use when designing or reviewing security for a web application, API, or multi-tenant SaaS — produces threat model, abuse case list, auth/authz matrix, and secret handling plan; covers OWASP Top 10 2025 and the AI-code-generation blind spots. Neighbours — api-design-first owns auth model fields, deployment-release-engineering owns secret rotation choreography, ai-security and llm-security own model-specific threats.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Vibe Security Skill

Baseline web-application and SaaS security skill. Produces the four contract artifacts — threat model, abuse case list, auth/authz matrix, secret handling plan — that downstream specialist skills (api-design-first, deployment-release-engineering, observability-monitoring, ai-security, llm-security) consume.

<!-- dual-compat-start -->
## Use When

- Designing a new feature or service that handles authenticated users, personal data, money, or privileged actions.
- Reviewing a web application, REST or GraphQL API, webhook handler, or multi-tenant SaaS for security defects before release.
- Auditing AI-generated code for the blind spots it reliably creates (IDOR, plain-text secrets, missing webhook signatures, no rate limiting).
- Producing the threat model, abuse cases, auth/authz matrix, or secret plan that downstream design, delivery, and ops skills depend on.

## Do Not Use When

- The feature is purely cosmetic with no data, auth, or privileged action — apply `practical-ui-design` instead.
- The security concern is LLM-specific (prompt injection, context exfiltration, tool abuse) — load `llm-security` or `ai-security`.
- The task is CI/CD hardening (SBOM, scanner gates, runner isolation) — load `cicd-devsecops`.
- The task is full audit of an existing application — load `web-app-security-audit`, which uses this skill's artifacts as inputs.

## Required Inputs

- Context map and critical-flow table from `system-architecture-design`.
- Auth model fields from `api-design-first` (or accept that this skill will define them).
- Access-pattern list from `database-design-engineering` (to scope tenancy and IDOR checks).

## Workflow

- Read this `SKILL.md` first; load only the references needed for the feature in scope.
- Produce the four artifacts in the contract, not prose notes.
- Run the decision tables against the design before writing code.

## Quality Standards

- Every high-risk threat has a mitigation owner and target date.
- Auth/authz matrix is exhaustive (every resource × role) and default-deny.
- Secrets plan names storage, rotation cadence, audit path, and incident-compromise procedure.
- Anti-patterns identified with concrete before/after code, not principles.

## Anti-Patterns

- See the full Anti-patterns section below.

## Prerequisites

Load `world-class-engineering` and `system-architecture-design` first. For web-specific depth, pair with `api-design-first`, `php-security`, `graphql-security`, or `network-security` as the stack demands.

## When this skill applies

- New feature design — threat model before code.
- Pre-release review of any web, API, or SaaS change that touches auth, data, payments, or admin.
- AI-generated code review — the blind-spot table catches the common failures.
- Multi-tenant isolation review — verifying tenant scoping on every query and endpoint.
- Webhook, payment, and third-party integration design.
- Incident post-mortem — refreshing the threat model when reality proved the old one wrong.

## Inputs

| Artifact | Produced by | Required? | Why |
|---|---|---|---|
| Context map | `system-architecture-design` | required | identifies trust boundaries and assets |
| Critical-flow table | `system-architecture-design` | required | scopes STRIDE analysis to real user journeys |
| Access-pattern list | `database-design-engineering` | required | drives IDOR, tenancy, and row-scope checks |
| Auth model fields | `api-design-first` | optional | this skill defines them if absent |
| Failure-mode list | `system-architecture-design` | optional | informs denial-of-service threats |
| Release plan | `deployment-release-engineering` | optional | aligns secret rotation with rollout |

If no upstream context map exists, produce one first (via `system-architecture-design`) rather than guessing boundaries.

## Outputs

| Artifact | Consumed by | Template |
|---|---|---|
| Threat model | `api-design-first`, `observability-monitoring`, `deployment-release-engineering` | `skill-composition-standards/references/threat-model-template.md` |
| Abuse case list | `advanced-testing-strategy`, `observability-monitoring` | inline (see `references/abuse-cases.md`) |
| Auth/authz matrix | `api-design-first`, `advanced-testing-strategy` | inline in threat model template |
| Secret handling plan | `deployment-release-engineering`, `cicd-devsecops`, `observability-monitoring` | inline (see `references/secret-handling.md`) |

Artifacts must be produced in the template format, not free-form prose.

## Non-negotiables

- Default-deny on every authorisation decision. A missing rule is a denial, not an allowance.
- Server-side validation on every input. Client-side validation is UX, not security.
- Parameterised queries for every database call. String concatenation is a defect.
- Webhook endpoints verify signatures before any side effect.
- Secrets never ship to the client bundle, logs, or error messages.
- Rate limiting on every auth, password-reset, and expensive endpoint.
- Return 404 for unauthorised resource access, not 403 (prevents enumeration).
- Regenerate session identifiers after authentication state changes.

## Decision rules

### When to treat a threat as high-risk

```text
Likelihood high AND Impact >= high                       -> H (must mitigate before release)
Likelihood medium AND Impact critical                    -> H (must mitigate before release)
Likelihood medium AND Impact medium                      -> M (mitigation planned, tracked)
Likelihood low AND Impact <= medium                      -> L (document, accept, or monitor)
Likelihood low AND Impact critical                       -> M (compensating control required)
```

Wrong-choice failure: rating by impact alone produces a backlog of "criticals" that never ships; rating by likelihood alone ignores catastrophic blast radius.

### Authentication method selection

```text
Internal service-to-service, same trust zone             -> mTLS + short-lived SPIFFE/JWT
Public API, partner integration                          -> OAuth 2.1 client credentials + audience check
Browser session, same-origin app                         -> session cookie (HttpOnly + Secure + SameSite=Lax or Strict)
Browser session, third-party context (embed, OAuth)     -> OAuth 2.1 authorisation code + PKCE
Mobile app to API                                         -> OAuth 2.1 authorisation code + PKCE, refresh token in Keychain/Keystore
High-value action (payments, admin, data export)         -> step-up auth (WebAuthn or TOTP) on top of session
```

Wrong-choice failure: shipping bearer tokens in LocalStorage for a first-party app invites XSS theft; using cookies for a mobile API forces CSRF machinery that adds no value.

### Tenant scoping enforcement layer

```text
Single-tenant app                                         -> owner_id filter in application query
Multi-tenant SaaS, low sensitivity                       -> tenant_id filter + code-review rule + SQL linter
Multi-tenant SaaS, regulated data (health, finance)      -> tenant_id filter + row-level security (RLS) + connection-time SET tenant
Multi-tenant SaaS, data isolation contractual            -> per-tenant schema or database + pooled connection per tenant
```

Wrong-choice failure: relying on application filters alone means one missing WHERE clause leaks every tenant; RLS without connection-time SET means `SET LOCAL` gets bypassed by ORM query rewriting.

### Secret rotation cadence

```text
Long-lived cloud provider API key (AWS, Stripe, etc.)    -> 90 days + immediate on suspected compromise
Internal service-to-service shared secret                 -> 30 days if static; ideal: replace with mTLS or workload identity
Database credential                                       -> 90 days (user), 24h (dynamic secret via Vault)
OAuth client secret                                       -> annually + on personnel change
JWT signing key                                           -> 90-day overlap rotation (publish kid; never drop old until tokens expire)
TLS private key                                           -> certificate lifetime (Let's Encrypt 90d; ACME automated)
```

Wrong-choice failure: hot-rotating a JWT key without `kid` overlap invalidates every live session; rotating a database password without a Vault dynamic secret breaks every pod until redeploy.

### Rate limit shape per endpoint class

```text
Login / password reset                                    -> 5 per 15 min per IP AND per username; CAPTCHA after 3
Registration                                              -> 3 per hour per IP; email verification required
Read API, authenticated                                   -> 1000/min per user, 10k/min per tenant
Write API, authenticated                                  -> 100/min per user; quota by plan
Expensive endpoint (search, export, AI)                  -> cost-weighted quota (token budget, not request count)
Public unauthenticated endpoint                           -> per-IP + CAPTCHA/Turnstile after threshold
Webhook intake                                            -> per-sender signature; reject unsigned within 1 second
```

Wrong-choice failure: per-IP-only limits get bypassed by distributed abusers; per-user-only limits let credential-stuffing race across unknown accounts.

## Core content

### Produce the threat model first

Follow `skill-composition-standards/references/threat-model-template.md`. Do not cherry-pick OWASP items; walk STRIDE across the real critical flows from the context map. Every threat gets a likelihood, impact, and risk rating; every H-risk gets a mitigation owner and date.

### AI-code-generation blind spots

AI-generated code reliably fails on a small, predictable set of defects. Review every generated feature against these before merge — this is where real incidents come from, not exotic attacks. Full before/after code in `references/ai-blind-spots.md`.

The six blind spots, in order of observed frequency:

1. IDOR and missing tenant scope (`GET /api/orders/124` returns anyone's order).
2. Webhook handlers with no signature verification.
3. Secret keys in the frontend bundle, source maps, or `NEXT_PUBLIC_*`.
4. Password storage via MD5/SHA-1 or plain text; no rate limit on login.
5. SQL built by string concatenation; no parameterised queries.
6. Verbose error responses exposing stack traces, file paths, or query internals.

### OWASP Top 10 2025 alignment

Full mapping with code examples in `references/owasp-mapping.md`. The four contract artifacts cover Top 10 coverage:

- Threat model addresses A01, A04, A05, A06, A08, A10.
- Abuse cases address A06, A08, A09.
- Auth/authz matrix addresses A01, A07.
- Secret handling plan addresses A02, A04.

### Stack-specific depth

- Authentication mechanics — `references/authentication-security.md`.
- Access control and tenancy — `references/access-control.md`.
- Server-side injection (SQL, SSRF, XXE, path traversal, command) — `references/server-side-security.md`.
- Client-side (XSS, CSRF, secret exposure, CSP, headers) — `references/client-side-security.md`.
- File upload (magic bytes, polyglot, storage isolation) — `references/file-upload-security.md`.
- OWASP Top 10 2025 full map — `references/owasp-mapping.md`.
- 97 Things baseline principles — `references/appsec-principles-97.md`.
- Secret handling detail — `references/secret-handling.md`.
- Abuse case catalogue — `references/abuse-cases.md`.
- AI-blind-spots with full code — `references/ai-blind-spots.md`.
- Security headers reference — `references/security-headers.md`.

### Cross-platform considerations

Apps deploy across Windows (dev), Ubuntu (staging), Debian (production). File permissions, case-sensitive filesystems, and MySQL `utf8mb4` collation all affect security — details in `references/server-side-security.md`.

## Anti-patterns

Concrete before/after examples. Each names the defect, shows the bad code, and shows the fix.

### 1. IDOR via route-only authorisation

Bad — authorisation stops at the route; the data access does not verify ownership:

```php
// routes/api.php: Route::middleware('auth')->get('/orders/{id}', [OrderController::class, 'show']);
public function show($id) {
    return Order::find($id); // returns ANY order
}
```

Fix — scope the query to the authenticated principal and return 404 on miss:

```php
public function show($id) {
    $order = Order::where('id', $id)
        ->where('tenant_id', auth()->user()->tenant_id)
        ->where('user_id', auth()->id())
        ->firstOrFail(); // 404, not 403
    return $order;
}
```

### 2. Webhook handler without signature verification

Bad — trusts the payload because it hit the webhook URL:

```js
app.post('/webhook/stripe', (req, res) => {
  if (req.body.type === 'checkout.session.completed') {
    grantAccess(req.body.data.object.customer_email); // anyone can curl this
  }
  res.sendStatus(200);
});
```

Fix — verify with provider SDK against the raw body and the webhook secret:

```js
app.post('/webhook/stripe', express.raw({type: 'application/json'}), (req, res) => {
  let event;
  try {
    event = stripe.webhooks.constructEvent(req.body, req.headers['stripe-signature'], process.env.STRIPE_WEBHOOK_SECRET);
  } catch (err) { return res.sendStatus(400); }
  if (event.type === 'checkout.session.completed') {
    grantAccess(event.data.object.customer_email);
  }
  res.sendStatus(200);
});
```

### 3. Password storage and brute-force window

Bad — MD5 plus no rate limit:

```php
$hash = md5($_POST['password']);
$user = DB::selectOne("SELECT * FROM users WHERE email=? AND password=?", [$email, $hash]);
```

Fix — Argon2id plus per-IP and per-username rate limit with lockout:

```php
// registration
$hash = password_hash($password, PASSWORD_ARGON2ID, ['memory_cost' => 65536, 'time_cost' => 4]);
// login
RateLimiter::attempt("login:$ip", 5, fn() => null, 900); // 5 per 15 min per IP
RateLimiter::attempt("login:$email", 5, fn() => null, 900); // 5 per 15 min per username
if (!password_verify($password, $user->password_hash)) { /* log + generic error */ }
```

### 4. Secret key in the frontend bundle

Bad — server key reachable via View Source:

```js
// next.config.js
env: { STRIPE_SECRET_KEY: process.env.STRIPE_SECRET_KEY } // ships to client
// or
const NEXT_PUBLIC_STRIPE_SECRET = process.env.NEXT_PUBLIC_STRIPE_SECRET;
```

Fix — publishable keys only on the client; server actions call Stripe with the secret:

```ts
// client: Stripe.js with publishable key
const stripe = await loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);
// server action (not shipped to browser)
'use server';
import Stripe from 'stripe';
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!); // server-only env
```

### 5. SQL built by string concatenation

Bad — classic SQLi:

```py
cursor.execute(f"SELECT * FROM orders WHERE user_id = {user_id} AND status = '{status}'")
```

Fix — parameterised plus tenancy scope:

```py
cursor.execute(
    "SELECT * FROM orders WHERE tenant_id = %s AND user_id = %s AND status = %s",
    (tenant_id, user_id, status),
)
```

### 6. Verbose error response leaking internals

Bad — production returns the stack:

```json
{"error": "SQLSTATE[42S02]: Base table or view not found: orders_v2 at /srv/app/OrderRepo.php:147"}
```

Fix — generic outward, detailed in server logs only:

```json
{"error": {"code": "ORDER_LOOKUP_FAILED", "message": "We could not process your request.", "request_id": "req_01J..."}}
```

Logger records the full exception, correlation id, and tenant id server-side.

### 7. Session identifier not regenerated after login

Bad — session fixation vector; attacker preseeds the session id:

```php
session_start();
if (login($email, $password)) { $_SESSION['user_id'] = $user->id; }
```

Fix — regenerate on authentication state change:

```php
session_start();
if (login($email, $password)) {
    session_regenerate_id(true); // invalidate old id
    $_SESSION['user_id'] = $user->id;
}
```

### 8. Tenant scoping via application filter alone in a regulated context

Bad — one missing `->where('tenant_id', ...)` leaks every tenant's data.

Fix — row-level security as the floor; application filter stays for performance:

```sql
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON orders
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
-- application connection pool sets: SET app.tenant_id = '...' on each checkout
```

## Read next

- `api-design-first` — consumes the auth/authz matrix and threat model into the OpenAPI spec and error model.
- `deployment-release-engineering` — consumes the secret handling plan into release + rollback choreography.
- `ai-security` — prompt injection, model output validation, PII scrubbing for AI-powered features.
- `llm-security` — OWASP LLM Top 10, trust boundaries and tool abuse specific to LLM-integrated endpoints.
- `web-app-security-audit` — uses this skill's artifacts as inputs when auditing an existing application end-to-end.
- `php-security`, `graphql-security`, `network-security`, `cicd-devsecops`, `linux-security-hardening` — stack-specific companions.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Security | Threat model | Markdown doc per `skill-composition-standards/references/threat-model-template.md` | `docs/security/threat-model-checkout.md` |
| Security | Abuse-case catalogue | Markdown doc listing misuse scenarios and mitigations | `docs/security/abuse-cases-checkout.md` |

## References

- `references/owasp-mapping.md` — OWASP Top 10 2025 complete map with code.
- `references/access-control.md` — IDOR, tenancy, authorisation patterns.
- `references/authentication-security.md` — password hashing, MFA, session, JWT, OAuth.
- `references/server-side-security.md` — SQLi, SSRF, XXE, path traversal, command injection.
- `references/client-side-security.md` — XSS, CSRF, CSP, secret exposure.
- `references/file-upload-security.md` — magic bytes, polyglot, storage isolation.
- `references/ai-blind-spots.md` — the six AI-generated-code blind spots with full code.
- `references/abuse-cases.md` — abuse-case catalogue for common SaaS patterns.
- `references/secret-handling.md` — secret storage, rotation, audit, incident response.
- `references/security-headers.md` — CSP, HSTS, and the full header reference.
- `references/appsec-principles-97.md` — 97 Things Every Application Security Professional Should Know condensed.
- `references/grokking-fundamentals.md` — fundamentals primer.
<!-- dual-compat-end -->
