# Grokking Web Application Security — Developer Fundamentals

Foundation reference covering the core web security concepts every developer must know.
Sourced from Grokking Web Application Security (Manning); written for the defender, not the attacker.

## Purpose

Use this when starting a new web application, onboarding an engineer, or reviewing a feature for security. It summarises the mental models, vulnerability classes, defences, headers, and habits that separate a merely working app from a defensible one.

## 1. Threat model basics

Every web security conversation reduces to four linked words: **asset**, **threat**, **vulnerability**, **control**.

- **Asset** — something valuable to protect: user data, credentials, payment details, reputation, uptime.
- **Threat** — a scenario where an asset is harmed: data theft, account takeover, service outage, fraud.
- **Vulnerability** — a weakness an attacker can exploit to realise a threat: missing validation, weak password policy, outdated library.
- **Control** — a defence that reduces the probability or impact of exploitation: parameterised queries, MFA, WAF rules, monitoring.

### STRIDE — a shared vocabulary for threats

| Letter | Meaning | Example in a SaaS app |
|---|---|---|
| S | Spoofing | Attacker logs in as another user using a stolen session |
| T | Tampering | Attacker changes a hidden form field to alter a price |
| R | Repudiation | User denies performing an action; no audit log exists |
| I | Information disclosure | Sensitive data leaked via an API endpoint |
| D | Denial of service | Expensive endpoint abused to exhaust database connections |
| E | Elevation of privilege | Regular user accesses an admin-only route |

### Core principles

- **Defence in depth.** Assume every single control will eventually fail; layer them so the next one catches the miss.
- **Least privilege.** Every process, service, user, and token gets the minimum access it needs to do its job.
- **Fail secure.** When something breaks, the default state must deny access, not allow it.
- **Assume breach.** Design as though an attacker is already inside; log and segment accordingly.
- **Keep secrets out of code and logs.** The most common breach is a leaked credential that was never supposed to exist on disk.
- **Minimise attack surface.** Fewer endpoints, fewer ports, fewer features means less to defend.

## 2. The security triad (CIA)

| Property | What it means | SaaS example |
|---|---|---|
| Confidentiality | Only authorised parties can see the data | A tenant cannot read another tenant's invoices |
| Integrity | Data cannot be altered without detection | An invoice total cannot be silently mutated in transit |
| Availability | The service is up when legitimate users need it | Rate limits and quotas stop one client from crashing the API |

Every feature should answer: "What is the confidentiality, integrity, and availability requirement here?" Most design mistakes are missed answers to one of those three questions.

## 3. Trust boundaries

A trust boundary is any place where data crosses from a less-trusted zone into a more-trusted zone. The rule is simple and absolute: **validate at every boundary**.

Typical boundaries in a web SaaS:

1. **Browser to web server.** Untrusted input enters via URL, query string, body, headers, cookies, and files.
2. **Web server to application layer.** Frameworks add structure, but validation is still on you.
3. **Application to database.** Use parameterised queries; never concatenate user input into SQL.
4. **Application to external services.** Validate and sanitise before forwarding; treat every API response as potentially hostile.
5. **Application to filesystem.** Never let user input choose a file path without canonicalisation and allow-listing.
6. **Multi-tenant boundary.** Every query must be scoped to the current tenant id; no shared-state leakage.

If you cannot name the trust boundary your code is defending, you are not yet writing secure code.

## 4. The OWASP Top 10 — practical summaries

### A01 Broken access control

The most common high-impact flaw. Users can access resources or actions they should not. PHP defence: centralise permission checks in middleware that runs before every controller; check ownership on every fetch-by-id; never rely on hidden UI to hide admin actions.

### A02 Cryptographic failures

Sensitive data transmitted in clear text, weak algorithms, or hardcoded keys. PHP defence: force HTTPS; use `password_hash()` with Argon2id; store encryption keys in Vault or environment variables; never roll your own crypto.

### A03 Injection

User input interpreted as code: SQL, NoSQL, command, LDAP, expression language. PHP defence: prepared statements (`PDO` with real prepares), parameterised queries, never `exec` with user input, escape when using legacy mysqli; validate type and length on ingest.

### A04 Insecure design

Flaws in logic rather than code — a password reset flow that asks easily-guessable questions, or a promo code that can be redeemed multiple times. Defence: threat model during design, write security acceptance criteria into user stories, and test the logic with adversarial scenarios.

### A05 Security misconfiguration

Default credentials, verbose error pages, missing headers, open cloud buckets, debug mode in production. PHP defence: harden `php.ini` (`display_errors=Off`, `expose_php=Off`), disable directory listings, remove sample code, automate configuration in code.

### A06 Vulnerable and outdated components

Old libraries with known CVEs. PHP defence: use Composer with lockfiles, run `composer audit` and `npm audit` in CI, subscribe to a CVE feed for your stack, patch on a defined SLA.

### A07 Identification and authentication failures

Weak password policies, no rate limiting, no MFA, predictable session ids, user enumeration in error messages. Defence: strong hashing, per-IP and per-account rate limiting, forced MFA for admins, generic error messages.

### A08 Software and data integrity failures

Unsigned updates, build systems that allow code injection, CI/CD with over-privileged tokens, deserialising untrusted data. Defence: sign artefacts, pin dependencies, verify checksums, avoid `unserialize()` on untrusted input.

### A09 Security logging and monitoring failures

You cannot respond to what you cannot see. Defence: log auth events (success and failure), log privilege changes, log data exports, ship logs off-host, alert on suspicious patterns (many failed logins, sudden spike in error rate).

### A10 Server-side request forgery (SSRF)

Your server makes a request on the attacker's behalf to a URL they control. PHP defence: allow-list outbound hosts and schemes, reject private and link-local IP ranges, use a metadata-service blocklist on cloud hosts, require an explicit proxy.

## 5. Core defences every web app must have

Priority-ordered. If you can only ship five of these, ship the first five — they block the majority of real attacks.

1. **HTTPS everywhere with TLS 1.3.** No plaintext, no exceptions, even internally. HSTS preloaded.
2. **Strong password hashing — Argon2id.** PHP: `password_hash($pw, PASSWORD_ARGON2ID)`. Never MD5, SHA-1, or plain SHA-256.
3. **Session cookies: HttpOnly, Secure, SameSite=Lax or Strict.** Prevents JavaScript access and cross-site sending.
4. **CSRF tokens on all state-changing requests.** A per-session token in a hidden form field, verified on POST/PUT/PATCH/DELETE.
5. **Parameterised queries — no string concatenation into SQL.** Always. Even for integer ids. Even for admin-only endpoints.
6. **Output encoding by context.** HTML, attribute, JavaScript, URL, and CSS contexts each need their own encoder. Never manually "escape".
7. **Content Security Policy.** Start strict, tighten over time. CSP blocks most XSS even when you miss encoding.
8. **Access control checks on every endpoint.** Authenticate, then authorise. Default-deny; explicit allow per action.
9. **Dependency updates on a schedule.** Automated PRs; patch high and critical within 7 days.
10. **Logging and alerting.** Auth events, admin actions, payment events, abnormal error rates. Alerts route to a human.

## 6. Cryptography basics (for developers, not cryptographers)

- **Use well-known, audited libraries.** Never implement cryptographic primitives yourself. In PHP, use `libsodium` (built-in from PHP 7.2). In JavaScript, use Web Crypto or libsodium-wrappers. In Python, use `cryptography`.
- **Symmetric encryption.** AES-256-GCM (or ChaCha20-Poly1305) for data at rest and in transit between internal services. Always authenticated (AEAD); never ECB, never unauthenticated CBC.
- **Asymmetric encryption and signing.** Ed25519 for signing, X25519 for key exchange, RSA-2048+ where mandated.
- **Hashing.** SHA-256 or SHA-3 for integrity and fingerprints. For passwords: Argon2id, or bcrypt with cost 12+. Never MD5 or SHA-1.
- **HMAC for message authentication.** `hash_hmac('sha256', ...)` when you need a keyed MAC.
- **Randomness.** `random_bytes()` / `random_int()` in PHP; `crypto.randomBytes` in Node; never `mt_rand` or `Math.random` for security.
- **Key management.** Never hardcode keys. Store them in Vault, AWS KMS, or environment variables injected at deploy time. Rotate on a schedule. Separate keys per environment.
- **Do not confuse encoding and encryption.** Base64 is not encryption. Obfuscation is not encryption.

## 7. Session management

- Use your framework's session handling; homegrown sessions are almost always broken.
- Session ids must be cryptographically random, at least 128 bits.
- **Regenerate session id on login and on privilege change.** Prevents session fixation.
- **Invalidate on logout, on password change, and on suspicious activity.**
- Set an idle timeout (e.g. 30 minutes) and an absolute timeout (e.g. 12 hours).
- Cookie flags: `HttpOnly`, `Secure`, `SameSite=Lax` (or Strict if no cross-site nav needed).
- In PHP, set session cookie params before `session_start()`; never mutate the id after the response starts.
- Do not store secrets in the session; store a minimal, server-side-only reference.

## 8. Defending a login form — the hardest thing to get right

Login is the single most attacked page in any app. Assume an adversary is running thousands of attempts per minute.

- **Hash passwords with Argon2id** (PHP: `password_hash($pw, PASSWORD_ARGON2ID)`). Use `password_verify()` for checks; it handles timing safely.
- **Rate limit per IP and per account.** A sliding window (e.g. 5 failures in 5 minutes from a given IP, 10 per hour per account). Use Redis or a dedicated store; do not rely on process-local state.
- **No enumeration in error messages.** Always return the same message for "no such user" and "wrong password".
- **Constant-time comparisons.** `hash_equals()` in PHP for comparing secret strings.
- **Log every failure with enough context** (IP, user agent, timestamp, the account targeted) but never the password.
- **Alert on patterns:** credential stuffing (many accounts, low per-account rate), brute force (one account, high rate), impossible travel.
- **MFA on admin accounts (non-negotiable) and on user accounts (strongly recommended).** TOTP via authenticator app; recovery codes; WebAuthn for higher-value accounts.
- **Account lockouts must be reversible and must not enable account-locking attacks.** Prefer exponential backoff and MFA challenges to hard locks.
- **CAPTCHA is a last-resort rate limiter, not a primary control.** Invisible variants (hCaptcha Enterprise, Turnstile) hurt users the least.
- **Password-reset flows are login flows.** Rate limit, generic messages, expire reset tokens quickly (15 minutes), one-use only.

## 9. Defending a form that accepts user input

Every form is an attack surface. The pipeline is: **authenticate → authorise → validate → sanitise → persist → respond with encoded output**.

- **Validate on the server.** Client-side validation is for UX, not security.
- **Type and range checks first.** Is it the right kind of thing? Is the length within bounds? Is it in the allowed set?
- **Allow-list, not deny-list.** It is easier to enumerate valid input than to enumerate all malicious input.
- **Canonicalise before comparing.** Normalise Unicode, lowercase, decode URL encoding once and only once.
- **Sanitise only if you must retain raw input.** For user-provided HTML, use a vetted purifier (HTML Purifier, DOMPurify) — do not roll your own regex-based sanitiser.
- **Output encoding is context-specific.** HTML body, HTML attribute, JavaScript string, JSON, URL query, and CSS each need their own encoder. Your template engine should do this by default.
- **CSRF token on every state-changing request.** Verify on every POST/PUT/PATCH/DELETE.
- **File uploads:** allow-list MIME types AND extensions; store outside the web root; rename to a UUID; scan with ClamAV; limit size per request and per account; never execute.
- **JSON inputs:** validate against a schema; reject unknown keys (or ignore them); enforce numeric ranges and string lengths.
- **Log validation failures.** Repeated bad input from one source is a probing signal.

## 10. Defending an API endpoint

- **Authenticate with a bearer token** — OAuth2 access token or signed JWT. Do not accept credentials on API calls other than the token exchange endpoint.
- **Rate limit per token, per IP, and per endpoint.** Different limits for read vs write.
- **Validate the input schema.** Use JSON Schema, OpenAPI, or a validation library. Reject anything that does not match.
- **Authorise on the resource, not just the route.** "Can this token read THIS order?" is different from "Can this token read orders?"
- **Return only the fields the caller is allowed to see.** Scope the response by role. Never rely on the client to filter.
- **Use explicit versioning** (`/v1/...`) so you can evolve without breaking.
- **Use idempotency keys on state-changing calls** to make retries safe.
- **Errors must not leak internals.** Map exceptions to a generic error format before returning.
- **CORS is not a security control** — it is a browser enforcement hint. Do not rely on it for authorisation.
- **Log the token id (not the secret), the action, and the outcome.**

## 11. Security headers every app should set

| Header | Value | Why |
|---|---|---|
| Strict-Transport-Security | `max-age=63072000; includeSubDomains; preload` | Force HTTPS even if the user typed `http://` |
| Content-Security-Policy | Strict policy with nonces or hashes | Block most XSS and data exfiltration |
| X-Content-Type-Options | `nosniff` | Stop browsers guessing MIME types |
| X-Frame-Options | `DENY` (or use CSP `frame-ancestors`) | Prevent clickjacking |
| Referrer-Policy | `strict-origin-when-cross-origin` | Limit URL leakage to third parties |
| Permissions-Policy | Disable unused APIs (camera, mic, geolocation) | Reduce attack surface of embedded scripts |
| Cross-Origin-Opener-Policy | `same-origin` | Isolate browsing context |
| Cross-Origin-Resource-Policy | `same-origin` | Prevent cross-origin leaks |

Serve these from a central middleware so every response gets them. Verify with an external scanner (Mozilla Observatory, securityheaders.com) on every deploy.

## 12. The security mindset — how to think like a defender

When you design or review a feature, keep five questions running in the back of your mind:

1. **"What could go wrong?"** List the failure modes, not the happy path.
2. **"What am I trusting?"** Every input, every header, every cookie, every upstream service — trace it to its source.
3. **"What assumption could be violated?"** Assumptions about ordering, size, uniqueness, user identity, network latency.
4. **"How would I attack this?"** Try to break it before the attacker does. Think like the adversary, defend like an engineer.
5. **"What is the worst case?"** If this fails, does it leak data, allow takeover, or crash the service? Which is worst?

The best defenders are the ones who keep asking these even when the feature "looks fine".

## 13. Common cognitive traps

These are the thoughts that precede breaches. Recognise them in yourself and your team.

- **"It's behind a firewall."** Firewalls are perimeters; attackers get through them. Defence in depth beats perimeter hope.
- **"No one knows about this endpoint."** Scanners crawl every path. Hidden is not a security property.
- **"Only admins can access this."** Who checks? Where? On every request? Can the check be bypassed by URL manipulation?
- **"It works in testing."** Test environments are friendlier than production; attackers are not.
- **"The framework handles it."** Frameworks help, but misuse is easy. Know what the framework does and does not do.
- **"We will add authentication later."** No, you will not. Ship with auth or do not ship.
- **"The user would never do that."** A user under attack, confused, or malicious will do exactly that.
- **"It is just an internal tool."** Internal tools become external the moment a credential leaks.
- **"We encrypted it."** Encrypted with what? Stored where? Who holds the keys? "Encrypted" without those answers is not encrypted.
- **"Our logs will tell us."** Only if you look at them, alert on them, and can read them when compromised.
- **"It is too obscure to exploit."** Obscurity is a speed bump, not a control.
- **"We passed the pen test last year."** Pen tests are a snapshot. Code changed. Threats changed. Posture changed.

## 14. Anti-patterns to avoid

- Security bolted on at the end of the project. Security must live in the design, the backlog, the tests, and the deploy pipeline.
- Checklist-only thinking. A feature can pass every checklist item and still be insecure if the threat model was wrong.
- Black-box tools without review. SAST, DAST, and SCA are useful only when someone acts on their output.
- Ignoring warnings. Compiler warnings, linter warnings, and scanner warnings accumulate until one of them becomes a breach.
- Logging sensitive data. Passwords, tokens, full card numbers, and national IDs must never appear in logs.
- Over-trusting the browser. Every client-side check must be repeated on the server.
- Writing your own auth, session, or crypto. Use the framework's primitives.
- Bypassing the ORM with raw SQL "just this once". This is how most SQLi gets in.
- Deploying debug mode to production. Error pages are a goldmine for attackers.
- Dumping stack traces to the user. Return a generic error; log the trace server-side with a correlation id.
- Keeping secrets in environment variables that are printed in process listings or phpinfo.
- Leaving default accounts, sample data, or admin endpoints from the framework in place.
- Treating compliance as security. Compliance sets a floor; real security is ongoing engineering.
- Running pen tests you never fix. A pen-test report unchanged after 90 days is wasted budget.

## Cross-references

- `appsec-principles-97.md` — higher-level organisational and process principles that complement these developer fundamentals.
- `owasp-mapping.md` — detailed OWASP Top 10 mapping used by this skill.
- `authentication-security.md` — expanded guidance for login, sessions, and MFA.
- `access-control.md` — authorisation patterns and RBAC in multi-tenant apps.
- `server-side-security.md` — hardening, headers, and configuration details.
- `client-side-security.md` — CSP, DOM XSS defences, and browser-side hardening.
- `file-upload-security.md` — file upload pipeline and defences.
- Skills: `vibe-security-skill`, `php-security`, `web-app-security-audit`, `code-safety-scanner`, `network-security`, `linux-security-hardening`, `llm-security`, `api-design-first`, `graphql-security`.
