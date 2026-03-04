---
name: php-security
description: "Use when building or reviewing PHP web applications for security vulnerabilities. Covers session hardening, input validation, output encoding, SQL injection prevention, XSS/CSRF protection, file upload security, php.ini hardening, PHP-specific vulnerabilities (type juggling, object injection), error handling, and cryptographic best practices."
---

# PHP Security

Production-grade PHP security patterns for web applications. Bridges gaps between vibe-security-skill (conceptual OWASP), php-modern-standards (code patterns), and dual-auth-rbac (authentication).

**Core Principle:** Validate all input, encode all output, harden all configuration, trust nothing from the client.

**Cross-references:** Use alongside **vibe-security-skill** (OWASP mapping), **php-modern-standards** (code quality), **dual-auth-rbac** (auth system).

**See references/ for:** `session-hardening.md`, `input-output-security.md`, `php-ini-security-checklist.md`

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

### Session Fixation Prevention

```php
declare(strict_types=1);

final class SecureSession
{
    public static function start(): void
    {
        if (session_status() === PHP_SESSION_ACTIVE) {
            return;
        }

        ini_set('session.use_strict_mode', '1');
        ini_set('session.cookie_httponly', '1');
        ini_set('session.cookie_samesite', 'Strict');

        $isHttps = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off')
                   || ($_SERVER['SERVER_PORT'] ?? 0) == 443;
        ini_set('session.cookie_secure', $isHttps ? '1' : '0');

        session_start();
    }

    /** Call on login, privilege change, or role switch */
    public static function regenerate(): void
    {
        session_regenerate_id(true); // true = delete old session file
    }

    /** Call on logout — complete destruction */
    public static function destroy(): void
    {
        $_SESSION = [];

        if (ini_get('session.use_cookies')) {
            $params = session_get_cookie_params();
            setcookie(
                session_name(),
                '',
                time() - 42000,
                $params['path'],
                $params['domain'],
                $params['secure'],
                $params['httponly'],
            );
        }

        session_destroy();
    }

    /** Enforce idle timeout */
    public static function checkTimeout(int $maxIdleSeconds = 1800): bool
    {
        if (isset($_SESSION['last_activity'])) {
            if (time() - $_SESSION['last_activity'] > $maxIdleSeconds) {
                self::destroy();
                return false;
            }
        }
        $_SESSION['last_activity'] = time();
        return true;
    }
}
```

### Session Hijacking Prevention

```php
// Bind session to user agent + IP subnet (not full IP — breaks mobile)
function validateSessionFingerprint(): bool
{
    $fingerprint = hash('sha256', $_SERVER['HTTP_USER_AGENT'] ?? '');

    if (!isset($_SESSION['fingerprint'])) {
        $_SESSION['fingerprint'] = $fingerprint;
        return true;
    }

    return hash_equals($_SESSION['fingerprint'], $fingerprint);
}
```

## Input Validation

### Server-Side Validation (Never Trust Client)

```php
final readonly class InputValidator
{
    /** Validate and sanitize common input types */
    public static function email(string $input): ?string
    {
        $email = filter_var(trim($input), FILTER_VALIDATE_EMAIL);
        return $email !== false ? $email : null;
    }

    public static function integer(mixed $input, int $min = 0, int $max = PHP_INT_MAX): ?int
    {
        $value = filter_var($input, FILTER_VALIDATE_INT, [
            'options' => ['min_range' => $min, 'max_range' => $max],
        ]);
        return $value !== false ? $value : null;
    }

    public static function url(string $input): ?string
    {
        $url = filter_var(trim($input), FILTER_VALIDATE_URL);
        if ($url === false) {
            return null;
        }
        // Only allow http/https schemes
        $scheme = parse_url($url, PHP_URL_SCHEME);
        return in_array($scheme, ['http', 'https'], true) ? $url : null;
    }

    public static function string(string $input, int $maxLength = 255): string
    {
        return mb_substr(trim($input), 0, $maxLength, 'UTF-8');
    }

    /** Whitelist validation for enum-like values */
    public static function oneOf(string $input, array $allowed): ?string
    {
        return in_array($input, $allowed, true) ? $input : null;
    }
}
```

### Regex Validation Patterns

```php
// Phone number (international format)
$isValid = preg_match('/^\+?[1-9]\d{6,14}$/', $phone);

// Date (YYYY-MM-DD)
$isValid = preg_match('/^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/', $date)
           && strtotime($date) !== false;

// Alphanumeric username
$isValid = preg_match('/^[a-zA-Z0-9_]{3,30}$/', $username);
```

## Output Encoding

### Context-Specific Encoding

```php
final readonly class OutputEncoder
{
    /** HTML body context */
    public static function html(string $input): string
    {
        return htmlspecialchars($input, ENT_QUOTES | ENT_HTML5, 'UTF-8');
    }

    /** JavaScript context */
    public static function js(string $input): string
    {
        return json_encode($input, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT);
    }

    /** URL parameter context */
    public static function url(string $input): string
    {
        return rawurlencode($input);
    }

    /** HTML attribute context */
    public static function attr(string $input): string
    {
        return htmlspecialchars($input, ENT_QUOTES | ENT_HTML5, 'UTF-8');
    }

    /** CSS context — only allow safe values */
    public static function css(string $input): string
    {
        return preg_replace('/[^a-zA-Z0-9\s#.,%-]/', '', $input);
    }
}
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
final readonly class CsrfGuard
{
    public static function generate(): string
    {
        $token = bin2hex(random_bytes(32));
        $_SESSION['csrf_token'] = $token;
        $_SESSION['csrf_token_time'] = time();
        return $token;
    }

    public static function validate(string $token, int $maxAge = 7200): bool
    {
        if (!isset($_SESSION['csrf_token'], $_SESSION['csrf_token_time'])) {
            return false;
        }
        if (time() - $_SESSION['csrf_token_time'] > $maxAge) {
            unset($_SESSION['csrf_token'], $_SESSION['csrf_token_time']);
            return false;
        }
        return hash_equals($_SESSION['csrf_token'], $token);
    }

    public static function field(): string
    {
        $token = self::generate();
        return '<input type="hidden" name="csrf_token" value="' . OutputEncoder::attr($token) . '">';
    }
}
```

## File Upload Security

```php
final readonly class SecureUpload
{
    private const ALLOWED_TYPES = [
        'image/jpeg' => ['jpg', 'jpeg'],
        'image/png'  => ['png'],
        'image/gif'  => ['gif'],
        'application/pdf' => ['pdf'],
    ];

    private const MAX_SIZE = 5 * 1024 * 1024; // 5MB

    public static function validate(array $file): array
    {
        $errors = [];

        if ($file['error'] !== UPLOAD_ERR_OK) {
            return ['Upload failed with error code: ' . $file['error']];
        }

        if ($file['size'] > self::MAX_SIZE) {
            $errors[] = 'File exceeds maximum size of 5MB';
        }

        // Verify MIME type using magic bytes (not user-supplied type)
        $finfo = new \finfo(FILEINFO_MIME_TYPE);
        $detectedType = $finfo->file($file['tmp_name']);

        if (!array_key_exists($detectedType, self::ALLOWED_TYPES)) {
            $errors[] = "File type '{$detectedType}' not allowed";
        }

        // Verify extension matches detected type
        $ext = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
        if (isset(self::ALLOWED_TYPES[$detectedType])
            && !in_array($ext, self::ALLOWED_TYPES[$detectedType], true)) {
            $errors[] = 'File extension does not match content type';
        }

        return $errors;
    }

    /** Store outside webroot with random filename */
    public static function store(array $file, string $uploadDir): ?string
    {
        $ext = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
        $filename = bin2hex(random_bytes(16)) . '.' . $ext;
        $destination = rtrim($uploadDir, '/') . '/' . $filename;

        if (!move_uploaded_file($file['tmp_name'], $destination)) {
            return null;
        }

        chmod($destination, 0644);
        return $filename;
    }
}
```

**Rules:** Store files outside webroot. Serve via PHP script with auth checks. Never use original filename. Validate magic bytes, not just extension.

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
set_error_handler(function (int $errno, string $errstr, string $errfile, int $errline): bool {
    error_log("[{$errno}] {$errstr} in {$errfile}:{$errline}");

    if ($errno === E_USER_ERROR) {
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => 'Internal server error']);
        exit(1);
    }

    return true;
});

set_exception_handler(function (\Throwable $e): void {
    error_log($e->getMessage() . ' in ' . $e->getFile() . ':' . $e->getLine());
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Internal server error']);
});
```

## Cryptographic Best Practices

```php
// Secure random generation
$token = bin2hex(random_bytes(32));     // 64-char hex token
$apiKey = base64_encode(random_bytes(32)); // Base64 API key

// Password hashing — ALWAYS Argon2id
$hash = password_hash($password, PASSWORD_ARGON2ID, [
    'memory_cost' => 65536,
    'time_cost' => 4,
    'threads' => 3,
]);

// Symmetric encryption — AES-256-GCM
function encrypt(string $plaintext, string $key): string
{
    $iv = random_bytes(12); // 96 bits for GCM
    $tag = '';
    $ciphertext = openssl_encrypt($plaintext, 'aes-256-gcm', $key, OPENSSL_RAW_DATA, $iv, $tag);
    return base64_encode($iv . $tag . $ciphertext);
}

function decrypt(string $encoded, string $key): string|false
{
    $data = base64_decode($encoded, true);
    if ($data === false || strlen($data) < 28) {
        return false;
    }
    $iv = substr($data, 0, 12);
    $tag = substr($data, 12, 16);
    $ciphertext = substr($data, 28);
    return openssl_decrypt($ciphertext, 'aes-256-gcm', $key, OPENSSL_RAW_DATA, $iv, $tag);
}

// HMAC for data integrity
$signature = hash_hmac('sha256', $payload, $secret);
if (!hash_equals($expectedSignature, $signature)) {
    throw new SecurityException('Invalid signature');
}
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
