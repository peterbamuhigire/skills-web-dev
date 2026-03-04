---
name: php-security
description: "Use when building or reviewing PHP web applications for security vulnerabilities. Covers session hardening, input validation, output encoding, SQL injection prevention, XSS/CSRF protection, file upload security, php.ini hardening, PHP-specific vulnerabilities (type juggling, object injection), error handling, and cryptographic best practices."
---

# PHP Security

Production-grade PHP security patterns for web applications. Bridges gaps between vibe-security-skill (conceptual OWASP), php-modern-standards (code patterns), and dual-auth-rbac (authentication).

**Core Principle:** Validate all input, encode all output, harden all configuration, trust nothing from the client.

**Cross-references:** Use alongside **vibe-security-skill** (OWASP mapping), **php-modern-standards** (code quality), **dual-auth-rbac** (auth system).

**See references/ for:** `session-hardening.md`, `input-output-security.md`, `php-ini-security-checklist.md`, `security-code-patterns.md`

## When to Use

- Building or auditing PHP web applications
- Configuring php.ini for production
- Implementing session management
- Handling file uploads securely
- Reviewing code for PHP-specific vulnerabilities

## Session Security

### php.ini Session Hardening

```ini
; Use cookies only — never pass session ID in URL
session.use_only_cookies = 1
session.use_cookies = 1
session.use_trans_sid = 0

; Cookie security flags
session.cookie_httponly = 1
session.cookie_samesite = Strict
; session.cookie_secure = 1  ; Enable when using HTTPS

; Session ID entropy
session.sid_length = 48
session.sid_bits_per_character = 6

; Strict mode — reject uninitialized session IDs
session.use_strict_mode = 1

; Garbage collection
session.gc_maxlifetime = 1800
session.gc_probability = 1
session.gc_divisor = 100

; Store sessions securely
session.save_handler = files
session.save_path = "/var/lib/php/sessions"
```

### Session Fixation & Hijacking Prevention

📖 **See `references/security-code-patterns.md` for complete SecureSession, InputValidator, OutputEncoder, CsrfGuard, and SecureUpload class implementations.**

```php
// Key patterns (full classes in references/security-code-patterns.md):
SecureSession::start();                      // Secure session init
SecureSession::regenerate();                 // On login/privilege change
SecureSession::destroy();                    // On logout
SecureSession::checkTimeout(1800);           // 30-min idle timeout
session_regenerate_id(true);                 // Delete old session file
validateSessionFingerprint();                // Bind to user agent
```

## Input Validation

### Server-Side Validation (Never Trust Client)

```php
// Full InputValidator class in references/security-code-patterns.md
InputValidator::email($input);               // filter_var FILTER_VALIDATE_EMAIL
InputValidator::integer($input, 0, 1000);    // filter_var FILTER_VALIDATE_INT with range
InputValidator::url($input);                 // Validate URL + restrict to http/https
InputValidator::string($input, 255);         // Trim + length limit
InputValidator::oneOf($input, $allowed);     // Whitelist validation

// Regex patterns
preg_match('/^\+?[1-9]\d{6,14}$/', $phone);                            // Phone
preg_match('/^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/', $date); // Date
preg_match('/^[a-zA-Z0-9_]{3,30}$/', $username);                       // Username
```

## Output Encoding

### Context-Specific Encoding

```php
// Full OutputEncoder class in references/security-code-patterns.md
OutputEncoder::html($input);   // htmlspecialchars(ENT_QUOTES | ENT_HTML5, 'UTF-8')
OutputEncoder::js($input);     // json_encode(JSON_HEX_TAG | JSON_HEX_AMP | ...)
OutputEncoder::url($input);    // rawurlencode()
OutputEncoder::attr($input);   // htmlspecialchars() for attributes
OutputEncoder::css($input);    // Strip unsafe chars
```

**Rule:** Always encode output based on WHERE it appears, not WHAT the data is.

## SQL Injection Prevention

### Prepared Statements (PDO)

```php
// Named parameters (preferred for clarity)
$stmt = $pdo->prepare('SELECT * FROM users WHERE email = :email AND status = :status');
$stmt->execute(['email' => $email, 'status' => 'active']);

// Dynamic column names — WHITELIST only
function orderBy(PDO $pdo, string $column, string $direction): PDOStatement
{
    $allowedColumns = ['name', 'email', 'created_at'];
    $allowedDirections = ['ASC', 'DESC'];

    if (!in_array($column, $allowedColumns, true)) {
        throw new InvalidArgumentException("Invalid column: {$column}");
    }
    if (!in_array(strtoupper($direction), $allowedDirections, true)) {
        $direction = 'ASC';
    }

    // Safe: values are from whitelist, not user input
    return $pdo->query("SELECT * FROM users ORDER BY {$column} {$direction}");
}

// IN clause with dynamic placeholders
function findByIds(PDO $pdo, array $ids): PDOStatement
{
    $ids = array_filter($ids, 'is_int');
    $placeholders = implode(',', array_fill(0, count($ids), '?'));
    $stmt = $pdo->prepare("SELECT * FROM users WHERE id IN ({$placeholders})");
    $stmt->execute($ids);
    return $stmt;
}
```

## XSS Prevention

### Content Security Policy

```php
header("Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'");
```

### Output in Templates

```php
<!-- HTML context -->
<p><?= OutputEncoder::html($userComment) ?></p>

<!-- Attribute context -->
<input value="<?= OutputEncoder::attr($userName) ?>">

<!-- JavaScript context -->
<script>var data = <?= OutputEncoder::js($userData) ?>;</script>

<!-- URL context -->
<a href="/search?q=<?= OutputEncoder::url($query) ?>">Search</a>
```

## CSRF Protection

```php
// Full CsrfGuard class in references/security-code-patterns.md
CsrfGuard::generate();              // bin2hex(random_bytes(32)) → session
CsrfGuard::validate($token, 7200);  // hash_equals + time check
CsrfGuard::field();                 // Hidden input HTML

// In forms:
echo CsrfGuard::field();
// On submit:
if (!CsrfGuard::validate($_POST['csrf_token'])) { die('CSRF validation failed'); }
```

## File Upload Security

```php
// Full SecureUpload class in references/security-code-patterns.md
$errors = SecureUpload::validate($_FILES['upload']);  // Magic bytes + size + extension
$filename = SecureUpload::store($_FILES['upload'], '/var/uploads/');  // Random filename
```

**Rules:** Store files outside webroot. Serve via PHP script with auth checks. Never use original filename. Validate magic bytes (`finfo`), not just extension. Max 5MB default.

## PHP-Specific Vulnerabilities

### Type Juggling

```php
// DANGER: Loose comparison (==) causes type juggling
"0e123" == "0e456"   // true! Both are 0 in scientific notation
"0" == false          // true!
"" == null            // true!
"php" == 0            // true in PHP 7! (fixed in PHP 8)

// ALWAYS use strict comparison
$token === $expectedToken  // Correct
hash_equals($expected, $actual)  // Timing-safe for secrets
```

### Object Injection / Insecure Deserialization

```php
// NEVER unserialize untrusted data
$data = unserialize($_POST['data']); // VULNERABLE!

// Use JSON instead
$data = json_decode($_POST['data'], true, 512, JSON_THROW_ON_ERROR);

// If unserialize is unavoidable, restrict allowed classes
$data = unserialize($input, ['allowed_classes' => [AllowedClass::class]]);
```

### Dangerous Functions (Disable or Avoid)

```php
// NEVER use with user input
eval($userInput);           // Code execution
exec($userInput);           // Command execution
system($userInput);         // Command execution
passthru($userInput);       // Command execution
shell_exec($userInput);     // Command execution
preg_replace('/e', ...);    // Code execution (removed in PHP 7)

// If command execution is needed, use escapeshellarg()
$safe = escapeshellarg($userInput);
exec("convert {$safe} output.png");
```

## Error Handling & Information Disclosure

### Production Configuration

```ini
; php.ini — PRODUCTION
display_errors = Off
display_startup_errors = Off
log_errors = On
error_log = /var/log/php/error.log
error_reporting = E_ALL
expose_php = Off
```

### Custom Error Handler

```php
// Full error/exception handlers in references/security-code-patterns.md
// Key pattern: log details server-side, show generic message to users
set_error_handler(function (int $errno, string $errstr, string $errfile, int $errline): bool {
    error_log("[{$errno}] {$errstr} in {$errfile}:{$errline}");
    if ($errno === E_USER_ERROR) {
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => 'Internal server error']);
        exit(1);
    }
    return true;
});
```

## Cryptographic Best Practices

```php
// Full encrypt/decrypt functions in references/security-code-patterns.md
$token = bin2hex(random_bytes(32));                       // 64-char hex token
$hash = password_hash($pw, PASSWORD_ARGON2ID, [           // Argon2id (ALWAYS)
    'memory_cost' => 65536, 'time_cost' => 4, 'threads' => 3,
]);
$cipher = encrypt($plaintext, $key);                      // AES-256-GCM
$plain = decrypt($cipher, $key);                          // AES-256-GCM
$sig = hash_hmac('sha256', $payload, $secret);            // HMAC integrity
hash_equals($expected, $sig);                             // Timing-safe compare
```

## Security Checklist

### Every PHP Application

- [ ] `display_errors = Off` in production
- [ ] `expose_php = Off`
- [ ] Session cookies: HttpOnly, Secure, SameSite=Strict
- [ ] `session.use_only_cookies = 1`
- [ ] `session.use_strict_mode = 1`
- [ ] Session regeneration on auth state change
- [ ] All input validated server-side
- [ ] All output encoded by context
- [ ] Prepared statements for all SQL
- [ ] CSRF tokens on all state-changing forms
- [ ] File uploads validated by magic bytes
- [ ] Files stored outside webroot
- [ ] Strict comparison (`===`) everywhere
- [ ] No `eval()`, `unserialize()` on user input
- [ ] Error logging to file, not display
- [ ] Security headers set (CSP, HSTS, X-Content-Type-Options)

### Dependency Management

- [ ] Run `composer audit` regularly
- [ ] Lock file committed (`composer.lock`)
- [ ] Review new dependencies before adding
- [ ] Pin major versions in `composer.json`

## Anti-Patterns

```php
// NEVER: String concatenation in queries
$sql = "SELECT * FROM users WHERE id = " . $_GET['id'];

// NEVER: Unvalidated redirects
header("Location: " . $_GET['url']);

// NEVER: Direct file inclusion from user input
include $_GET['page'] . '.php';

// NEVER: Loose comparison for auth
if ($token == $expected) { } // Type juggling!

// NEVER: md5/sha1 for passwords
$hash = md5($password); // Cracked in seconds

// NEVER: Display raw errors to users
ini_set('display_errors', '1'); // In production
```

**References:**
- PHP Security: https://www.php.net/manual/en/security.php
- OWASP PHP: https://cheatsheetseries.owasp.org/cheatsheets/PHP_Configuration_Cheat_Sheet.html
- php.ini: https://www.php.net/manual/en/ini.list.php
