# Detailed Audit Checklist with Scan Patterns

Comprehensive checklist for each audit layer with specific grep/glob patterns for Claude to use during scanning.

**Parent skill:** web-app-security-audit

## Layer 1: Configuration

### Files to Scan

```
Glob: **/.env, **/.env.*, **/config/*.php, **/php.ini, **/.htaccess
Glob: **/wp-config.php, **/settings.php, **/bootstrap.php
```

### Grep Patterns

```
# CRITICAL: Debug/error display in production
display_errors\s*=\s*(On|1|true)
error_reporting.*E_ALL.*display

# CRITICAL: Secrets in code
(password|passwd|secret|api_key|token)\s*=\s*['"][^'"]{4,}['"]
DB_(PASSWORD|HOST|USER|NAME)\s*=\s*['"][^'"]+['"]

# CRITICAL: Dangerous PHP settings
allow_url_include\s*=\s*(On|1)
allow_url_fopen\s*=\s*(On|1)

# HIGH: phpinfo exposure
phpinfo\s*\(

# HIGH: Debug output
var_dump\s*\(.*\$_(GET|POST|REQUEST|SESSION)
print_r\s*\(.*\$_(GET|POST|REQUEST)
error_log.*\$_(POST|GET).*password

# MEDIUM: Server info disclosure
expose_php\s*=\s*(On|1)
ServerSignature\s+On
```

### Checklist

- [ ] `.env` file NOT accessible from webroot
- [ ] `.env` in `.gitignore`
- [ ] No hardcoded database credentials in PHP files
- [ ] No API keys/secrets in JavaScript files
- [ ] `display_errors = Off` in production config
- [ ] `expose_php = Off`
- [ ] `allow_url_include = Off`
- [ ] No `phpinfo()` calls in production code
- [ ] `open_basedir` configured
- [ ] No debug output (var_dump, print_r) in production code
- [ ] `.htaccess` blocks access to sensitive directories

## Layer 2: Authentication & Sessions

### Files to Scan

```
Glob: **/login*.php, **/auth*.php, **/session*.php, **/register*.php
Glob: **/middleware/auth*.php, **/helpers/*auth*.php, **/helpers/*session*.php
```

### Grep Patterns

```
# CRITICAL: Weak password hashing
md5\s*\(\s*\$.*password
sha1\s*\(\s*\$.*password
sha256.*password
crypt\s*\(

# CRITICAL: Missing session regeneration
session_start.*login  (check: session_regenerate_id nearby?)

# HIGH: Session configuration
session\.use_strict_mode
session\.cookie_httponly
session\.use_only_cookies
session\.cookie_samesite

# HIGH: Password handling
password_hash\s*\(       (should use PASSWORD_ARGON2ID)
password_verify\s*\(     (should exist for login)
PASSWORD_DEFAULT          (should be PASSWORD_ARGON2ID)
PASSWORD_BCRYPT           (acceptable but prefer Argon2id)

# MEDIUM: Session timeout
session_destroy
session\.gc_maxlifetime
last_activity
```

### Checklist

- [ ] Passwords hashed with Argon2id (or bcrypt minimum)
- [ ] `password_verify()` used (not manual hash comparison)
- [ ] Session ID regenerated after login (`session_regenerate_id(true)`)
- [ ] Session cookies: HttpOnly, Secure, SameSite=Strict
- [ ] `session.use_strict_mode = 1`
- [ ] `session.use_only_cookies = 1`
- [ ] Idle timeout enforced (30 min recommended)
- [ ] Complete session destruction on logout
- [ ] Login rate limiting implemented
- [ ] Failed login attempts logged
- [ ] Account lockout after 5 failures

## Layer 3: Authorization & Access Control

### Files to Scan

```
Glob: **/middleware/*.php, **/api/**/*.php, **/controllers/*.php
Grep in all PHP: SELECT.*FROM.*WHERE (check for franchise_id/owner_id)
```

### Grep Patterns

```
# CRITICAL: Missing tenant isolation
SELECT\s+\*\s+FROM\s+\w+\s*$           (no WHERE clause)
SELECT.*FROM.*WHERE(?!.*franchise_id)   (missing tenant filter)

# CRITICAL: Direct object reference
\$_GET\s*\[\s*['"]id['"]\s*\]          (ID from URL without auth check)

# HIGH: Missing permission checks
include.*admin.*(?!.*permission|.*auth|.*check)
require.*admin.*(?!.*permission|.*auth|.*check)

# MEDIUM: Sequential IDs
AUTO_INCREMENT                          (check if exposed in URLs)
```

### Checklist

- [ ] Every data query scoped to tenant (`WHERE franchise_id = ?`)
- [ ] Resource ownership verified before access
- [ ] Permission checks on all protected routes
- [ ] Admin routes require admin authentication
- [ ] API endpoints verify authorization (not just authentication)
- [ ] Return 404 (not 403) for unauthorized resource access
- [ ] Cross-tenant access explicitly prevented
- [ ] Super admin bypass properly implemented

## Layer 4: Input Validation

### Files to Scan

```
Glob: **/*.php (all PHP files)
Focus: Files containing $_GET, $_POST, $_REQUEST, $_FILES
```

### Grep Patterns

```
# CRITICAL: SQL injection
"SELECT.*\.\s*\$_(GET|POST|REQUEST)
"INSERT.*\.\s*\$_(GET|POST|REQUEST)
"UPDATE.*\.\s*\$_(GET|POST|REQUEST)
"DELETE.*\.\s*\$_(GET|POST|REQUEST)
mysql_query\s*\(                        (deprecated, no prepared statements)
mysqli_query.*\$_                       (raw input in query)

# HIGH: Raw input usage without validation
\$_GET\s*\[(?!.*filter_var|.*htmlspecialchars|.*intval|.*trim)
\$_POST\s*\[(?!.*filter_var|.*htmlspecialchars|.*intval|.*trim)
\$_REQUEST\s*\[

# HIGH: File upload without validation
move_uploaded_file(?!.*finfo|.*mime|.*getimagesize)
\$_FILES\s*\[.*\['name'\]              (using original filename)

# MEDIUM: Missing type validation
(int)\s*\$_(GET|POST)                   (casting without validation)
```

### Checklist

- [ ] All form inputs validated server-side
- [ ] Email validated with `FILTER_VALIDATE_EMAIL`
- [ ] Integers validated with `FILTER_VALIDATE_INT` and range
- [ ] Strings trimmed and length-checked
- [ ] Enum values checked against whitelist
- [ ] File uploads validated by magic bytes (`finfo`)
- [ ] File size limits enforced
- [ ] Files stored outside webroot with random names
- [ ] No `$_REQUEST` usage (ambiguous source)
- [ ] All SQL uses prepared statements (PDO/mysqli)

## Layer 5: Output Encoding & XSS

### Files to Scan

```
Glob: **/*.php, **/*.html, **/*.js, **/templates/**
Focus: echo, print, printf statements with variables
```

### Grep Patterns

```
# CRITICAL: Direct output of user input
echo\s+\$_(GET|POST|REQUEST|COOKIE)
print\s+\$_(GET|POST|REQUEST|COOKIE)

# HIGH: Output without encoding
echo\s+\$\w+(?!.*htmlspecialchars|.*e\(|.*json_encode)
<\?=\s*\$\w+(?!.*htmlspecialchars)

# MEDIUM: Incomplete encoding
htmlspecialchars\s*\([^,]+\)$           (missing ENT_QUOTES flag)
htmlspecialchars(?!.*ENT_QUOTES)

# MEDIUM: JavaScript context
<script>.*\$\w+.*</script>             (PHP var in script tag)
var\s+\w+\s*=\s*['"].*\<\?             (PHP in JS without json_encode)

# LOW: Missing CSP header
Content-Security-Policy                 (should exist in headers)
```

### Checklist

- [ ] All user-sourced output uses `htmlspecialchars()`
- [ ] `htmlspecialchars()` called with `ENT_QUOTES | ENT_HTML5, 'UTF-8'`
- [ ] JavaScript context uses `json_encode()` with `JSON_HEX_TAG`
- [ ] URL context uses `rawurlencode()`
- [ ] No raw PHP variables in `<script>` tags
- [ ] Content-Security-Policy header set
- [ ] CSP does not use `'unsafe-inline'` for scripts
- [ ] CSP does not use `'unsafe-eval'`

## Layer 6: API Security

### Files to Scan

```
Glob: **/api/**/*.php, **/ajax*.php, **/endpoint*.php
Grep: header.*Access-Control, header.*Content-Type.*json
```

### Grep Patterns

```
# CRITICAL: CORS misconfiguration
Access-Control-Allow-Origin:\s*\*
Access-Control-Allow-Credentials.*true.*Allow-Origin.*\*

# HIGH: Missing CSRF
$_POST\[(?!.*csrf|.*token|.*_token)     (POST without CSRF check)

# HIGH: Error disclosure
catch.*Exception.*echo.*getMessage
json_encode.*exception.*message
PDOException.*echo

# MEDIUM: Missing rate limiting
(login|reset|register).*(?!.*rate|.*limit|.*throttle|.*attempt)

# MEDIUM: Insecure redirect
header\s*\(\s*['"]Location:\s*['"]?\s*\.\s*\$_(GET|POST)
```

### Checklist

- [ ] CSRF tokens on all state-changing endpoints
- [ ] CSRF tokens validated server-side with `hash_equals()`
- [ ] CORS not set to wildcard (`*`) on authenticated endpoints
- [ ] Rate limiting on login, password reset, registration
- [ ] API errors don't expose stack traces or database details
- [ ] Webhook endpoints verify signatures
- [ ] No open redirects (redirect URLs validated)
- [ ] HTTP methods restricted (no GET for state changes)

## Layer 7: HTTP Security Headers

### Check Method

For each major endpoint, verify these headers in the response:

```
# Run for each endpoint type
curl -I https://yourapp.com/ 2>/dev/null | grep -i -E "(strict-transport|content-security|x-frame|x-content-type|referrer-policy|x-powered|server:)"
```

### Checklist

- [ ] `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- [ ] `Content-Security-Policy` with restrictive policy
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `X-Frame-Options: DENY` (or SAMEORIGIN if framing needed)
- [ ] `Referrer-Policy: strict-origin-when-cross-origin`
- [ ] `Cache-Control: no-store` on authenticated pages
- [ ] `X-Powered-By` header removed
- [ ] `Server` header version info removed
- [ ] HTTPS enforced (HTTP redirects to HTTPS)

## Layer 8: Dependencies & Supply Chain

### Files to Scan

```
Glob: **/composer.json, **/composer.lock, **/package.json, **/package-lock.json
Glob: **/*.html (for CDN script tags)
```

### Grep Patterns

```
# Check CDN scripts for SRI
<script.*src=.*https://.*cdn(?!.*integrity)    (CDN without SRI)
<link.*href=.*https://.*cdn(?!.*integrity)     (CDN CSS without SRI)

# Check for known vulnerable patterns
serialize\s*\(.*\$_                            (insecure serialization)
unserialize\s*\(.*\$_(GET|POST)                (object injection)
eval\s*\(.*\$_                                 (code injection)
```

### Commands

```bash
# PHP dependency audit
composer audit 2>&1

# JavaScript dependency audit
npm audit 2>&1

# Check for outdated packages
composer outdated --direct 2>&1
```

### Checklist

- [ ] `composer audit` shows no critical vulnerabilities
- [ ] `npm audit` shows no critical vulnerabilities
- [ ] `composer.lock` committed to repository
- [ ] `package-lock.json` committed to repository
- [ ] CDN scripts include `integrity` attribute (SRI)
- [ ] CDN scripts include `crossorigin="anonymous"`
- [ ] No `eval()` or `unserialize()` on user input
- [ ] Dependencies on latest stable versions (or justified)
