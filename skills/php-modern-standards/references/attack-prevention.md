# Attack Prevention Patterns

> Source: Sommerfeld — Unlock PHP 8 (Ch. 10); supplements php-security skill

For comprehensive security, load the **php-security** skill. This file covers the most critical attack patterns with concrete examples.

## Table of Contents

1. [SQL Injection](#sql-injection)
2. [XSS (Cross-Site Scripting)](#xss-cross-site-scripting)
3. [CSRF](#csrf-cross-site-request-forgery)
4. [Content Security Policy](#content-security-policy)
5. [Brute Force Protection](#brute-force-protection)
6. [Principle of Least Privilege](#principle-of-least-privilege)
7. [Production Error Display](#production-error-display)

---

## SQL Injection

### How it Works

An attacker manipulates SQL via form fields or URL parameters:

```php
// ✗ VULNERABLE — direct string interpolation
$sql = "SELECT * FROM users WHERE login='" . $_POST['username'] . "' AND password='" . $_POST['password'] . "'";

// Attacker enters: ' OR '1'='1'; --
// Resulting query: SELECT * FROM users WHERE login='' OR '1'='1'; --' AND password='...'
// Effect: Bypasses authentication entirely
```

UNION-based extraction:
```
GET /product.php?id=5 UNION SELECT username, password, NULL FROM users
```

### Prevention

```php
// ✓ Prepared statements — always
$stmt = $pdo->prepare('SELECT * FROM users WHERE login = :login AND password = :pass');
$stmt->execute([':login' => $login, ':pass' => $pass]);

// ✓ ORM (Eloquent/Doctrine) — prevents injection by default
User::where('login', $login)->first();
```

Additional defences:
- Least-privilege DB user (SELECT only where write isn't needed)
- `display_errors = Off` in production (never reveal query structure)
- Monitoring — alert on suspicious query patterns

---

## XSS (Cross-Site Scripting)

### Three Types

| Type | How | Who Affected |
|------|-----|-------------|
| **Stored** | Malicious JS saved to DB, displayed to all visitors | All users of that page |
| **Reflected** | Malicious JS in URL, reflected in response | Victim who clicks link |
| **DOM-based** | JS manipulates DOM client-side without server involvement | Victim's browser only |

### Prevention

```php
// ✓ Encode ALL user-supplied output before rendering
echo htmlspecialchars($input, ENT_QUOTES | ENT_HTML5, 'UTF-8');

// ✓ JSON output — escape HTML-special chars
echo json_encode($data, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS);

// ✓ Secure cookies — JS can't read HttpOnly cookies
setcookie('session', $token, [
    'secure'   => true,
    'httponly' => true,
    'samesite' => 'Strict',
    'path'     => '/',
]);
```

**Never mix user data directly into JavaScript strings:**
```php
// ✗ WRONG
echo "<script>var name = '{$_POST['name']}';</script>";

// ✓ CORRECT — pass via data attribute or JSON
echo '<div data-name="' . htmlspecialchars($name, ENT_QUOTES | ENT_HTML5, 'UTF-8') . '">';
```

---

## CSRF (Cross-Site Request Forgery)

### How it Works

1. User is authenticated on `bank.com` (has session cookie)
2. Attacker sends link to `evil.com` with hidden form that POSTs to `bank.com/transfer`
3. Browser auto-sends session cookie → bank processes transfer as if user did it

### Prevention — Synchronizer Token Pattern

```php
<?php

// Generate token once per session
function generateCsrfToken(): string
{
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf_token'];
}

// In form:
echo '<input type="hidden" name="csrf_token" value="' . generateCsrfToken() . '">';

// Validate on POST — use hash_equals() to prevent timing attacks
function verifyCsrfToken(): void
{
    $submitted = $_POST['csrf_token'] ?? '';
    $stored    = $_SESSION['csrf_token'] ?? '';

    if (!hash_equals($stored, $submitted)) {
        http_response_code(403);
        die('CSRF validation failed');
    }
}
```

**Rules:**
- Regenerate token per session (not per request — breaks multi-tab)
- Always `hash_equals()` — never `===` or `==` for token comparison
- API endpoints using JWT don't need CSRF (stateless auth)
- SameSite=Strict cookies also mitigate CSRF independently

---

## Content Security Policy

```php
<?php

// Allow scripts/styles from own domain only
header("Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self';");

// Report violations to your endpoint (without blocking — use for testing)
header("Content-Security-Policy-Report-Only: default-src 'self'; report-uri /csp-report");

// Allow specific external CDN
header("Content-Security-Policy: default-src 'self'; script-src 'self' https://cdn.example.com;");
```

**Test in report-only mode first.** A misconfigured CSP will break your site.

---

## Brute Force Protection

### Application Layer

```php
<?php

final class LoginThrottle
{
    private const MAX_ATTEMPTS = 5;
    private const LOCKOUT_SECONDS = 900;  // 15 min

    public function __construct(private \Memcached $cache) {}

    public function check(string $identifier): void
    {
        $key      = 'login_attempts:' . md5($identifier);
        $attempts = (int) ($this->cache->get($key) ?? 0);

        if ($attempts >= self::MAX_ATTEMPTS) {
            http_response_code(429);
            echo json_encode(['error' => 'Too many attempts. Try again later.']);
            exit;
        }
    }

    public function recordFailure(string $identifier): void
    {
        $key = 'login_attempts:' . md5($identifier);
        $current = (int) ($this->cache->get($key) ?? 0);
        if ($current === 0) {
            $this->cache->set($key, 1, self::LOCKOUT_SECONDS);
        } else {
            $this->cache->increment($key, 1);
        }
    }

    public function clearOnSuccess(string $identifier): void
    {
        $this->cache->delete('login_attempts:' . md5($identifier));
    }
}

// Usage in login handler:
$throttle = new LoginThrottle($memcached);
$throttle->check($_SERVER['REMOTE_ADDR']);

if ($loginFailed) {
    $throttle->recordFailure($_SERVER['REMOTE_ADDR']);
    throw new InvalidCredentialsException();
}

$throttle->clearOnSuccess($_SERVER['REMOTE_ADDR']);
```

**Additional strategies:**
- Incremental delay after each failure (`sleep(min($attempts, 5))`)
- CAPTCHA after N failures
- 2FA as ultimate brute-force prevention
- Server-level: `fail2ban` to block IPs at firewall

---

## Principle of Least Privilege

### Database Users

```sql
-- ✗ DON'T use root or admin for application queries

-- ✓ DO: Create role-specific users
CREATE USER 'app_reader'@'localhost' IDENTIFIED BY '...';
GRANT SELECT ON app_db.* TO 'app_reader'@'localhost';

CREATE USER 'app_writer'@'localhost' IDENTIFIED BY '...';
GRANT SELECT, INSERT, UPDATE ON app_db.* TO 'app_writer'@'localhost';

-- Only the migration user gets DROP/ALTER
CREATE USER 'app_migrate'@'localhost' IDENTIFIED BY '...';
GRANT ALL PRIVILEGES ON app_db.* TO 'app_migrate'@'localhost';
```

### File Permissions (Linux)

```bash
# PHP files — owner can read/write, webserver can read
chmod 644 /var/www/app/*.php

# Directories
chmod 755 /var/www/app/

# Sensitive config (DB credentials, .env) — owner only
chmod 600 /var/www/app/.env

# Never give web-accessible directories write permission
# unless explicitly needed for uploads (use a separate uploads dir)
```

### Remote File Inclusion

```ini
; php.ini — disable remote includes
allow_url_include = Off
allow_url_fopen   = Off  ; Disable if your app doesn't need remote file reads
```

```php
// ✗ NEVER use user input in include/require
include $_GET['page'] . '.php';

// ✓ Use a whitelist
$allowed = ['home', 'about', 'contact'];
$page = in_array($_GET['page'] ?? '', $allowed, true) ? $_GET['page'] : 'home';
include "pages/{$page}.php";
```

---

## Production Error Display

```ini
; php.ini — production
display_errors  = Off
log_errors      = On
error_reporting = E_ALL
error_log       = /var/log/php/app_errors.log
```

```php
<?php

// Override in bootstrap — never show errors to users
ini_set('display_errors', '0');
error_reporting(E_ALL);

// Sentry integration for real-time error monitoring
\Sentry\init(['dsn' => $_ENV['SENTRY_DSN']]);

// Catch unhandled exceptions
set_exception_handler(function (\Throwable $e): void {
    \Sentry\captureException($e);
    http_response_code(500);
    echo json_encode(['error' => 'Internal server error']);
});
```

**PHPStan static analysis** catches type errors before runtime:

```bash
./vendor/bin/phpstan analyse src/ --level=8
```

**Xdebug** for local debugging (disable in production):

```ini
; php.ini — development only
zend_extension = xdebug.so
xdebug.mode = debug
xdebug.start_with_request = yes
xdebug.client_host = localhost
xdebug.client_port = 9003
```

---

**Sources:** Sommerfeld, Unlock PHP 8 Ch. 10 (2024)
**Cross-reference:** php-security skill for comprehensive implementation
