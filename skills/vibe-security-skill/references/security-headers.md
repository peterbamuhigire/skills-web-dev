# Security Headers Reference

Parent: [../SKILL.md](../SKILL.md).

The HTTP response headers every web app must set, with rationale, failure mode if omitted, and stricter/laxer variants.

## Must-set on every response

### Strict-Transport-Security (HSTS)

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

- Forces browser to use HTTPS for one year.
- Submit to the HSTS preload list after confirming all subdomains support HTTPS.
- Failure mode: first-visit over HTTP remains MITM-vulnerable until preload.

### Content-Security-Policy (CSP)

```http
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'nonce-{RANDOM}';
  style-src 'self' 'nonce-{RANDOM}';
  img-src 'self' data: https:;
  font-src 'self';
  connect-src 'self' https://api.example.com;
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
  object-src 'none';
  upgrade-insecure-requests;
```

- Nonce-based CSP blocks inline script/style unless nonce matches. Prefer nonces over `'unsafe-inline'`.
- Report-only mode first, then enforce: add `Content-Security-Policy-Report-Only` alongside, collect violations, then migrate.
- Failure mode: XSS payloads execute; `unsafe-inline` without nonce defeats CSP's XSS mitigation.

### X-Content-Type-Options

```http
X-Content-Type-Options: nosniff
```

- Prevents MIME sniffing. Without it, a text response could be interpreted as script by IE/legacy clients.

### X-Frame-Options / frame-ancestors

```http
X-Frame-Options: DENY
```

- Prefer `frame-ancestors 'none'` in CSP. `X-Frame-Options` remains for legacy browsers.
- Failure mode: clickjacking via iframe.

### Referrer-Policy

```http
Referrer-Policy: strict-origin-when-cross-origin
```

- Prevents leaking full URL (with query params) to third parties.
- `no-referrer` is stricter; use for sensitive apps.

### Permissions-Policy

```http
Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(self)
```

- Denies features by default; grants only where needed.

### Cross-Origin-Opener-Policy / Cross-Origin-Embedder-Policy

```http
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

- Needed for SharedArrayBuffer and for defence against Spectre-class cross-origin leaks.
- Can break third-party embeds; evaluate per route.

## Authentication / session endpoints

Add:

```http
Cache-Control: no-store
Pragma: no-cache
```

- Prevents caching of authenticated responses in shared or browser caches.

## Cookies — security attributes

Session cookies:

```text
Set-Cookie: session=...; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=86400
```

- `HttpOnly` — not readable by JS; XSS cannot steal the cookie directly.
- `Secure` — only sent over HTTPS.
- `SameSite=Lax` — sent on top-level navigation but not on cross-site subresource requests; blocks most CSRF.
- `SameSite=Strict` — even top-level nav from another origin omits the cookie; use for high-value apps.
- `SameSite=None` requires `Secure`; only for intentionally cross-site cookies (embedded widgets).

CSRF token cookie (double-submit pattern):

```text
Set-Cookie: csrf_token=...; Path=/; Secure; SameSite=Strict
```

- Not `HttpOnly` (JS needs to read to echo in header).
- The header check compares the submitted value to the cookie value.

## CORS

For authenticated APIs:

```http
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
Vary: Origin
```

- Never `Access-Control-Allow-Origin: *` combined with credentials.
- Echo the `Origin` only if it matches an allow-list; otherwise reject.

## Common failures

- `script-src 'unsafe-inline' 'unsafe-eval'` — defeats CSP as XSS mitigation. Use nonces.
- `X-XSS-Protection: 1; mode=block` — deprecated; causes vulnerabilities in some browsers. Do not set.
- HSTS without HTTPS readiness — can lock users out. Ship with shorter max-age first.
- CSP in report-only forever — collect violations but never enforce.
- `SameSite=None` without `Secure` — browsers reject; cookie never set.
- `Access-Control-Allow-Origin` echoed from the request without allow-listing — defeats CORS.

## Verification

```bash
curl -sI https://example.com | grep -iE 'strict-transport|content-security|x-content|x-frame|referrer|permissions|cross-origin|cache-control'
```

Use `https://securityheaders.com/` or `https://observatory.mozilla.org/` for a report-card check.

## Platform-specific setters

- Nginx: `add_header` per server block.
- Apache: `Header always set` in VirtualHost or `.htaccess`.
- Express: `helmet` middleware.
- Laravel: middleware or `securityheaders` package.
- Next.js: `headers()` in `next.config.js`.
