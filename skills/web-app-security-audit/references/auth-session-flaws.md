# Authentication and Session Flaws — Defender's Guide

Purpose: identify common authentication and session-management vulnerabilities in PHP/JS
web apps and apply defensive patterns that hold up under real attack.

## The authentication surface

Authentication is never one endpoint. Every one of the following is part of the attack
surface, and a single weak component can undermine the rest:

- Login (password, SSO, OAuth, WebAuthn)
- Logout
- Registration / signup
- Email verification
- Password reset (request + confirm)
- Email change (current email → new email)
- Remember-me / persistent login
- Multi-factor enrolment and verification
- Recovery codes / backup codes
- Session introspection ("logged in as…") and active-session list
- API token / personal access token management

A threat model that only covers the login form misses the most commonly exploited paths:
password reset, email change, and remember-me cookies. All of these must be audited
together.

## Password-based login flaws

### Weak passwords

- Enforce minimum length of 12 characters (NIST SP 800-63B). Do not force arbitrary
  composition rules (uppercase, symbol) — length matters more.
- Reject the top 10,000 common passwords at minimum.
- Check against the Have I Been Pwned (Pwned Passwords) API using the k-anonymity
  range endpoint — send only the first 5 hex characters of the SHA-1 hash, never the
  full hash or the password itself.
- Prevent users reusing their previous N passwords (if you store history, store only
  hashes).

### User enumeration

Enumeration flaws leak whether a given username / email exists. Common leaks:

- Different error messages: "Unknown user" vs "Wrong password"
- Different HTTP status codes
- Different response times (user lookup + hash compare is much slower than early exit)
- Different redirect destinations
- Different response sizes
- Signup form that rejects existing emails with "Email already registered"
- Password reset form confirming "We sent a link" only if the email exists
- Account lockout message only shown for real accounts

**Defence:**

- Return a single generic response: "If those credentials are valid, you will be logged in"
- On password reset request, always respond "If an account exists with that email, we have
  sent a reset link" — regardless of whether the email exists
- Always perform the password hash comparison even when the user does not exist (compute
  a dummy verify to equalise timing)
- Use `hash_equals()` for any string comparison involving secrets (constant-time)

```php
function loginAttempt(string $email, string $password): ?int {
    $user = findUserByEmail($email);
    // Always run a hash verify to equalise timing
    $hash = $user['password_hash'] ?? '$argon2id$v=19$m=65536,t=4,p=1$dummy$dummy';
    $ok   = password_verify($password, $hash);
    if ($user === null || !$ok) {
        return null;
    }
    return (int) $user['id'];
}
```

### Brute force and credential stuffing

- Rate limit per account (e.g. 5 failures / 15 minutes) AND per IP (e.g. 20 failures /
  15 minutes). Both limits — either alone is bypassable.
- Progressive delay: add 1s, 2s, 4s, 8s to response time on successive failures.
- CAPTCHA after 3-5 failures on an account or IP.
- Account lockout is risky (it becomes a DoS vector). Prefer rate limiting + CAPTCHA.
- Alert on anomalous patterns: many accounts tried from one IP, many IPs against one
  account, logins from new geographies, logins from known breach-dump IP ranges.
- Device fingerprinting (UA + Accept-Language + IP reputation) to require step-up auth
  on unfamiliar devices.
- Check submitted passwords against the Pwned Passwords range API to block known-breached
  credential pairs.

## Password storage

Use only modern, memory-hard password hashes:

| Algorithm | Use? | Notes |
|-----------|------|-------|
| Argon2id  | Yes (default) | Winner of PHC, memory-hard, PHP `PASSWORD_ARGON2ID` |
| bcrypt    | Acceptable fallback | Widely supported, cost ≥ 12 |
| scrypt    | Acceptable | Memory-hard, less common in PHP |
| PBKDF2    | Only with very high iterations; avoid if possible |
| SHA-256 / SHA-512 / MD5 / SHA-1 | NEVER for passwords — too fast |

**PHP password handling:**

```php
// Hashing at signup / password change
$hash = password_hash($password, PASSWORD_ARGON2ID, [
    'memory_cost' => 65536,  // 64 MB
    'time_cost'   => 4,
    'threads'     => 1,
]);

// Verification at login
if (!password_verify($password, $user['password_hash'])) {
    // fail — use generic message
    return;
}

// Transparent upgrade path for old hashes
if (password_needs_rehash($user['password_hash'], PASSWORD_ARGON2ID)) {
    $newHash = password_hash($password, PASSWORD_ARGON2ID);
    updateUserPasswordHash($user['id'], $newHash);
}
```

**Never:**

- Log passwords (not in access logs, not in error logs, not in debug output)
- Email passwords to users (neither on signup nor on reset)
- Store passwords in a form that can be decrypted ("for recovery")
- Send passwords over unencrypted channels
- Include passwords in URLs or query strings

## Password reset flaws

### Token generation

Reset tokens must be cryptographically random and unguessable:

```php
$token = bin2hex(random_bytes(32));  // 64 hex chars, 256 bits of entropy
```

Never use `uniqid()`, `mt_rand()`, `rand()`, timestamps, user ID hashes, or sequential
identifiers. Store the SHA-256 hash of the token in the database, not the token itself,
so a database leak does not expose active reset tokens.

### Token lifetime

- Short expiry — 15 to 60 minutes is typical
- One-time use — invalidate immediately after successful reset
- Invalidate on any change to the account (password change, email change)
- Bind to the user ID server-side — never trust a user ID in the reset URL

### Avoiding enumeration on the reset endpoint

Always respond the same way whether or not the email exists:

```php
function requestPasswordReset(string $email): void {
    $user = findUserByEmail($email);
    if ($user !== null) {
        $token = bin2hex(random_bytes(32));
        storeResetToken($user['id'], hash('sha256', $token), time() + 900);
        sendResetEmail($user['email'], $token);
    }
    // Always return the same generic response regardless
}
```

Response: "If an account exists with that email, we have sent a reset link."

### Reset link hygiene

- Deliver the token via POST body on the confirmation page, not in the URL of the page
  that performs the reset (prevents referer leakage)
- Or use a single-use GET URL that immediately redirects to a POST form with the token
  in a hidden field and a fresh anti-CSRF token
- Set `Referrer-Policy: same-origin` or `no-referrer` on reset pages
- Strip query parameters from referer headers outbound

## Remember-me cookie flaws

The persistent login cookie is a second credential and must be as carefully guarded as the
session cookie itself. Common flaws:

- Storing user ID or email directly — trivially forgeable
- Using a short random token — brute-forceable
- No rotation on use — stolen cookie valid indefinitely
- No invalidation on password change

**Secure pattern:**

1. On "remember me" checkbox at login: generate 32-byte random token, store in DB with
   `user_id`, `sha256(token)`, `expires_at`, `created_ip`, `user_agent_fingerprint`.
2. Set cookie `remember=<selector>.<token>` with `HttpOnly`, `Secure`, `SameSite=Lax`,
   path `/`, expiry 30 days.
3. On each request where no session exists, verify the token with `hash_equals()`.
4. On successful auto-login, rotate the token (issue a new one, invalidate the old).
5. On password change, email change, or MFA enrolment: invalidate ALL remember-me tokens
   for that user.
6. Provide a "log out all devices" control.

## Multi-factor authentication

- **TOTP (RFC 6238)** — preferred broadly-supported second factor. Store the secret
  encrypted. Allow ±1 step drift (90s window). Generate 10 one-time backup codes at
  enrolment, store hashed, cross off on use.
- **WebAuthn / passkeys** — the 2026 default for high-value accounts. Resistant to
  phishing because the challenge is bound to the origin.
- **SMS OTP** — discouraged (SIM swap, SS7) but acceptable as a fallback where nothing
  else is available to the user.
- **Email OTP** — weakest; use only as an account recovery fallback.

**Enforcement:**

- All admin and super-admin accounts must have MFA enrolled (enforce at login; do not
  allow admin login without MFA)
- Prompt regular users to enrol MFA during onboarding
- Require MFA re-verification for sensitive actions (password change, email change,
  payment method change, API token issuance, data export)

## Session management flaws

### Session fixation

An attacker sets the user's session ID before they log in, then reuses it after. Defence:
regenerate the session ID on every authentication boundary (login, privilege change,
MFA verification).

```php
// At successful login
session_regenerate_id(true);  // true = delete the old session file
$_SESSION['user_id']    = $user['id'];
$_SESSION['logged_in_at'] = time();
$_SESSION['ip']         = $_SERVER['REMOTE_ADDR'];
$_SESSION['ua_hash']    = hash('sha256', $_SERVER['HTTP_USER_AGENT'] ?? '');
```

### Session hijacking

- `HttpOnly` prevents JavaScript from reading the session cookie
- `Secure` ensures the cookie is sent only over HTTPS
- `SameSite=Lax` (or `Strict` for high-value apps) blocks most cross-site attachment
- Short inactivity timeout (15-60 minutes for sensitive apps)
- Absolute maximum lifetime (8-24 hours, then force re-login)
- Optional: bind loosely to IP `/24` and UA hash — alert on change, do not hard-fail
  (mobile networks rotate IPs)

### Predictable session IDs

Never roll your own session ID. Use the framework. PHP's native session module uses
256-bit random IDs by default — fine. If you migrate to a JWT or custom token, use
`random_bytes(32)`.

### Concurrent sessions

Decide the policy explicitly and enforce it:

- **Allow multiple sessions** — user can be logged in on phone and desktop at once (most
  consumer apps)
- **Single session** — logging in anywhere logs out everywhere else (some banking apps)
- **List and revoke** — show the user their active sessions with device / location and
  let them revoke individually

Whichever policy you pick, server-side logout must invalidate the session in the backing
store, not merely delete the cookie.

### Server-side logout

```php
function logout(): void {
    $_SESSION = [];
    if (ini_get('session.use_cookies')) {
        $p = session_get_cookie_params();
        setcookie(session_name(), '', time() - 42000,
            $p['path'], $p['domain'], $p['secure'], $p['httponly']);
    }
    session_destroy();
}
```

## CSRF — Cross-Site Request Forgery

CSRF works because a browser automatically attaches cookies to cross-origin requests.
If a user is logged into your app and visits an attacker's page, that page can submit a
form to your app and the user's session cookie goes along.

**Primary defence — synchronizer token pattern:**

```php
// Token generation (once per session, or per-form)
function csrfToken(): string {
    if (empty($_SESSION['csrf'])) {
        $_SESSION['csrf'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf'];
}

// Token verification middleware for all state-changing requests
function verifyCsrf(): void {
    if (!in_array($_SERVER['REQUEST_METHOD'], ['POST','PUT','PATCH','DELETE'], true)) {
        return;
    }
    $sent = $_POST['_csrf'] ?? $_SERVER['HTTP_X_CSRF_TOKEN'] ?? '';
    if (!isset($_SESSION['csrf']) || !hash_equals($_SESSION['csrf'], $sent)) {
        http_response_code(419);
        exit('CSRF token mismatch');
    }
}

// In every form
echo '<input type="hidden" name="_csrf" value="' . htmlspecialchars(csrfToken()) . '">';
```

**Layered defences:**

- `SameSite=Lax` on the session cookie — blocks most cross-site POSTs at the browser
- Double-submit cookie pattern for stateless APIs
- Origin / Referer header check for state-changing requests (reject if neither matches
  your app's origin)
- Require re-authentication for the most sensitive actions regardless of CSRF defence

## Cookie security directives

```php
session_set_cookie_params([
    'lifetime' => 0,               // session cookie, closes with browser
    'path'     => '/',
    'domain'   => 'app.example.com',
    'secure'   => true,            // HTTPS only
    'httponly' => true,            // inaccessible to JS
    'samesite' => 'Lax',           // or 'Strict' for admin apps
]);
ini_set('session.use_strict_mode', '1');  // reject unknown session IDs
ini_set('session.use_only_cookies', '1');
session_name('__Host-sid');                // __Host- prefix: path=/, Secure, no domain
session_start();
```

The `__Host-` cookie prefix enforces that the cookie was set with `Secure`, `Path=/`,
and without a `Domain` attribute — a strong binding that prevents subdomain takeover
from stealing the session.

## OAuth / OIDC pitfalls (brief)

- **`state` parameter** — always include a cryptographically random `state` on the
  authorisation request and verify it on callback. Protects against CSRF on the redirect.
- **PKCE** — mandatory for public clients (SPAs, mobile). Prefer PKCE even for confidential
  clients.
- **Validate `aud` and `iss`** on ID tokens — the token must be issued by the expected
  provider and intended for your client ID.
- **Verify signatures** against the provider's JWKS — never accept unsigned tokens, never
  trust the token "alg" field without an allow-list (guard against `alg: none`).
- **Validate `exp`, `iat`, `nbf`** and reject tokens outside a small clock skew window.
- **Never log ID tokens** — they are bearer credentials.
- **Nonce** — include a nonce on the authorisation request and verify it on the ID token
  for replay protection.

## Account takeover attack chains

Attackers chain small weaknesses into full account takeover. Watch for these compound
flaws:

1. **Password reset + no re-authentication on email change:** attacker finds a reset token
   leak path (GitHub public commit, log file, referer), changes the email, then uses
   password reset to claim the account.
2. **Reset link shared via email:** reset tokens forwarded in email threads to help desks
   then stored in ticketing systems.
3. **Session not invalidated on password change:** old session cookies keep working.
4. **MFA bypass via "lost phone" recovery flow** with weak verification.

**Defences:**

- Require the current password to change email OR require clicking a link sent to the
  old email with a short-lived confirm token
- Notify the old email address when an email change occurs, with a cancel-this-change link
- Enforce a cool-down period (e.g. 24 hours) between email changes
- Invalidate ALL sessions on password change except the one that did it
- Invalidate all remember-me tokens on password change and on MFA enrolment
- Notify via email on every sensitive change: password, email, MFA method, new API token

## Defender's checklist — auth/session audit

- [ ] Passwords hashed with Argon2id (or bcrypt cost ≥ 12)
- [ ] Password minimum length ≥ 12; breached passwords rejected (HIBP k-anonymity)
- [ ] No user enumeration on login, signup, or password reset endpoints
- [ ] Login response timing is constant regardless of user existence
- [ ] Rate limiting on login per-account AND per-IP, with CAPTCHA escalation
- [ ] MFA enforced for all admin accounts; TOTP or WebAuthn preferred
- [ ] Session ID regenerated on login, MFA, and privilege change
- [ ] Session cookies set with `HttpOnly`, `Secure`, `SameSite=Lax` or `Strict`
- [ ] Consider `__Host-` cookie prefix for session cookie
- [ ] Idle and absolute session timeouts enforced
- [ ] Logout destroys session server-side, not just the cookie
- [ ] CSRF tokens on every state-changing request; verified with `hash_equals()`
- [ ] Origin / Referer header validation as secondary CSRF defence
- [ ] Password reset tokens: 256-bit random, hashed at rest, single-use, short-lived
- [ ] Reset flow does not leak referer containing the token
- [ ] Email change requires current password OR confirm link to old email
- [ ] All sensitive changes trigger an email notification to the account owner
- [ ] Remember-me tokens are random, rotated on use, invalidated on password change
- [ ] OAuth callback verifies `state` and (for OIDC) `nonce`
- [ ] JWTs verified with an allow-listed algorithm and a known JWKS

## Anti-patterns — never do these

- Roll your own session management, cookie format, or token signing
- Roll your own password hash ("I XOR the salt…")
- Use `MD5`, `SHA1`, `SHA256` or unsalted hashes for passwords
- Store secrets (API keys, JWT signing keys, DB passwords) in source control
- Trust `$_SERVER['HTTP_X_FORWARDED_FOR']` or `X-Real-IP` without knowing your proxy chain
- Trust client-side validation for any security decision
- Use `==` or `strcmp` to compare tokens, HMACs, or hashes — always `hash_equals()`
- Email passwords on signup or password reset
- Expose reset tokens in GET URLs that stay in browser history
- Accept `alg: none` JWTs or accept the algorithm field without an allow-list
- Use the same secret for signing sessions and for CSRF tokens
- Skip CSRF on "read-only" GET endpoints that actually change state
- Allow unlimited login attempts
- Leave debug/dev authentication backdoors in production code

## Cross-references

- `wahh-attack-patterns.md` — full attack taxonomy including XSS, injection, SSRF
- `input-validation-patterns.md` — input validation principles
- `access-control-flaws.md` — horizontal/vertical authorisation flaws after login
- `security-headers-reference.md` — `Set-Cookie` attributes, CSP, HSTS
- `audit-checklist-detailed.md` — full audit checklist
- `../SKILL.md` — entry point for web app security audit
- Related skills: `php-security`, `dual-auth-rbac`, `vibe-security-skill`, `llm-security`
