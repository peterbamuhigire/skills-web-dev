# HTTP Security Headers Reference

Complete reference for HTTP security headers that web applications must implement. Based on OWASP recommendations and modern browser security mechanisms.

**Parent skill:** web-app-security-audit

## Required Headers

### Strict-Transport-Security (HSTS)

Forces browsers to use HTTPS for all future requests to the domain.

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `max-age` | `31536000` (1 year) | How long browser remembers to use HTTPS |
| `includeSubDomains` | Present | Apply to all subdomains |
| `preload` | Present | Eligible for browser preload list |

**PHP implementation:**

```php
// Set in PHP (or .htaccess / nginx config)
header('Strict-Transport-Security: max-age=31536000; includeSubDomains; preload');
```

**Audit check:** Missing HSTS = HIGH severity. Users can be downgraded to HTTP.

### Content-Security-Policy (CSP)

Controls which resources the browser is allowed to load. Primary defense against XSS.

**Recommended policy:**

```
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'
```

| Directive | Recommended | Purpose |
|-----------|-------------|---------|
| `default-src` | `'self'` | Fallback for all resource types |
| `script-src` | `'self'` | Where scripts can load from |
| `style-src` | `'self' 'unsafe-inline'` | Where styles can load from |
| `img-src` | `'self' data: https:` | Where images can load from |
| `font-src` | `'self'` | Where fonts can load from |
| `connect-src` | `'self'` | Where AJAX/fetch can connect |
| `frame-ancestors` | `'none'` | Who can embed this page (anti-clickjacking) |
| `base-uri` | `'self'` | Restricts `<base>` tag |
| `form-action` | `'self'` | Where forms can submit |

**Strict CSP with nonces (recommended for apps with inline scripts):**

```php
$nonce = base64_encode(random_bytes(16));
header("Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-{$nonce}' 'strict-dynamic'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; frame-ancestors 'none'");

// In HTML:
echo "<script nonce=\"{$nonce}\">/* safe inline script */</script>";
```

**Red flags in CSP:**
- `'unsafe-inline'` in script-src = HIGH (allows XSS payloads)
- `'unsafe-eval'` = HIGH (allows eval-based attacks)
- `*` wildcard in script-src = CRITICAL
- No CSP at all = MEDIUM

**Report-Only mode (for testing):**

```
Content-Security-Policy-Report-Only: [same policy]; report-uri /csp-report
```

### X-Content-Type-Options

Prevents browsers from MIME-sniffing responses away from declared content-type.

```
X-Content-Type-Options: nosniff
```

**Audit check:** Missing = LOW severity. Prevents MIME confusion attacks.

### X-Frame-Options

Prevents the page from being embedded in iframes (anti-clickjacking).

```
X-Frame-Options: DENY
```

| Value | Effect |
|-------|--------|
| `DENY` | Page cannot be embedded anywhere |
| `SAMEORIGIN` | Only same-origin pages can embed |

**Note:** `frame-ancestors` in CSP supersedes this header, but include both for older browser support.

**Audit check:** Missing = MEDIUM severity.

### Referrer-Policy

Controls how much referrer information is sent with requests.

```
Referrer-Policy: strict-origin-when-cross-origin
```

| Value | Behavior |
|-------|----------|
| `no-referrer` | Never send referrer |
| `same-origin` | Only send for same-origin requests |
| `strict-origin` | Send origin only, and only over HTTPS |
| `strict-origin-when-cross-origin` | Full URL for same-origin, origin only for cross-origin |

**Audit check:** Missing = LOW severity.

### Cache-Control (Sensitive Pages)

Prevent caching of authenticated or sensitive content.

```
Cache-Control: no-store, no-cache, must-revalidate, private
Pragma: no-cache
```

**Apply to:** Login pages, account pages, API responses with sensitive data.

**Audit check:** Missing on authenticated pages = MEDIUM severity.

## Headers to Remove

### X-Powered-By

Reveals technology stack (e.g., `X-Powered-By: PHP/8.2.0`).

```php
// Remove in php.ini
expose_php = Off

// Or remove in PHP
header_remove('X-Powered-By');
```

**Audit check:** Present = LOW severity.

### Server Version

```
# Apache .htaccess
ServerTokens Prod
ServerSignature Off

# Nginx
server_tokens off;
```

**Audit check:** Version info present = LOW severity.

## CORS Headers

Cross-Origin Resource Sharing headers control which domains can make requests to your API.

### Secure CORS Configuration

```php
$allowedOrigins = [
    'https://app.example.com',
    'https://admin.example.com',
];

$origin = $_SERVER['HTTP_ORIGIN'] ?? '';

if (in_array($origin, $allowedOrigins, true)) {
    header("Access-Control-Allow-Origin: {$origin}");
    header('Access-Control-Allow-Credentials: true');
    header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
    header('Access-Control-Allow-Headers: Content-Type, Authorization, X-CSRF-Token');
    header('Access-Control-Max-Age: 86400');
}

// Handle preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}
```

**Red flags:**
- `Access-Control-Allow-Origin: *` with credentials = CRITICAL
- `Access-Control-Allow-Origin: *` on authenticated endpoints = HIGH
- Reflecting any origin without whitelist = HIGH

## Complete PHP Header Setup

```php
function setSecurityHeaders(): void
{
    // Transport security
    header('Strict-Transport-Security: max-age=31536000; includeSubDomains; preload');

    // Content security
    header("Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'");

    // Anti-clickjacking
    header('X-Frame-Options: DENY');

    // MIME sniffing prevention
    header('X-Content-Type-Options: nosniff');

    // Referrer control
    header('Referrer-Policy: strict-origin-when-cross-origin');

    // Remove server info
    header_remove('X-Powered-By');
}

// Call early in every request (e.g., in bootstrap/middleware)
setSecurityHeaders();

// For sensitive/authenticated pages, also add:
header('Cache-Control: no-store, no-cache, must-revalidate, private');
header('Pragma: no-cache');
```

## .htaccess Implementation

```apache
# HSTS
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"

# CSP
Header always set Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; frame-ancestors 'none'"

# Anti-clickjacking
Header always set X-Frame-Options "DENY"

# MIME sniffing
Header always set X-Content-Type-Options "nosniff"

# Referrer
Header always set Referrer-Policy "strict-origin-when-cross-origin"

# Remove server info
Header unset X-Powered-By
ServerSignature Off
```

## Audit Severity Summary

| Header | Missing Severity | Misconfigured Severity |
|--------|-----------------|----------------------|
| HSTS | HIGH | MEDIUM (short max-age) |
| CSP | MEDIUM | HIGH (unsafe-inline/eval) |
| X-Content-Type-Options | LOW | N/A |
| X-Frame-Options | MEDIUM | LOW (SAMEORIGIN when DENY possible) |
| Referrer-Policy | LOW | LOW |
| Cache-Control (auth pages) | MEDIUM | LOW |
| X-Powered-By (present) | LOW | N/A |
| CORS (wildcard) | HIGH | CRITICAL (with credentials) |

## Testing Tools

```bash
# Check headers on a URL
curl -I https://yourapp.com/

# Check specific header
curl -sI https://yourapp.com/ | grep -i content-security-policy

# Online scanners
# securityheaders.com -- grades your headers A-F
# observatory.mozilla.org -- comprehensive scan
```
