# PHP Security Code Patterns

Complete class implementations referenced from `SKILL.md`. Copy and adapt for your project.

---

## SecureSession

```php
class SecureSession
{
    public static function start(): void
    {
        if (session_status() === PHP_SESSION_ACTIVE) {
            return;
        }

        ini_set('session.use_only_cookies', '1');
        ini_set('session.use_strict_mode', '1');
        ini_set('session.cookie_httponly', '1');
        ini_set('session.cookie_samesite', 'Strict');
        // ini_set('session.cookie_secure', '1'); // Enable for HTTPS

        session_start();

        if (!isset($_SESSION['_created'])) {
            $_SESSION['_created'] = time();
            $_SESSION['_fingerprint'] = self::fingerprint();
        }
    }

    public static function regenerate(): void
    {
        session_regenerate_id(true); // Delete old session file
        $_SESSION['_created'] = time();
    }

    public static function destroy(): void
    {
        $_SESSION = [];

        if (ini_get('session.use_cookies')) {
            $p = session_get_cookie_params();
            setcookie(session_name(), '', time() - 42000,
                $p['path'], $p['domain'], $p['secure'], $p['httponly']
            );
        }

        session_destroy();
    }

    public static function checkTimeout(int $maxIdleSeconds = 1800): void
    {
        if (isset($_SESSION['_last_activity'])
            && (time() - $_SESSION['_last_activity']) > $maxIdleSeconds
        ) {
            self::destroy();
            throw new RuntimeException('Session expired due to inactivity');
        }
        $_SESSION['_last_activity'] = time();
    }

    private static function fingerprint(): string
    {
        return hash('sha256', ($_SERVER['HTTP_USER_AGENT'] ?? '') . (__DIR__));
    }

    public static function validateFingerprint(): bool
    {
        return isset($_SESSION['_fingerprint'])
            && hash_equals($_SESSION['_fingerprint'], self::fingerprint());
    }
}
```

---

## InputValidator

```php
class InputValidator
{
    public static function email(string $input): ?string
    {
        $clean = filter_var(trim($input), FILTER_VALIDATE_EMAIL);
        return $clean !== false ? $clean : null;
    }

    public static function integer(string $input, int $min = PHP_INT_MIN, int $max = PHP_INT_MAX): ?int
    {
        $result = filter_var($input, FILTER_VALIDATE_INT, [
            'options' => ['min_range' => $min, 'max_range' => $max],
        ]);
        return $result !== false ? $result : null;
    }

    public static function url(string $input): ?string
    {
        $clean = filter_var(trim($input), FILTER_VALIDATE_URL);
        if ($clean === false) {
            return null;
        }
        $scheme = parse_url($clean, PHP_URL_SCHEME);
        return in_array($scheme, ['http', 'https'], true) ? $clean : null;
    }

    public static function string(string $input, int $maxLength = 255): ?string
    {
        $clean = trim($input);
        return mb_strlen($clean) <= $maxLength ? $clean : null;
    }

    public static function oneOf(string $input, array $allowed): ?string
    {
        return in_array($input, $allowed, true) ? $input : null;
    }

    public static function phone(string $input): ?string
    {
        return preg_match('/^\+?[1-9]\d{6,14}$/', $input) ? $input : null;
    }

    public static function date(string $input): ?string
    {
        return preg_match('/^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/', $input) ? $input : null;
    }

    public static function username(string $input): ?string
    {
        return preg_match('/^[a-zA-Z0-9_]{3,30}$/', $input) ? $input : null;
    }
}
```

---

## OutputEncoder

```php
class OutputEncoder
{
    public static function html(?string $input): string
    {
        return htmlspecialchars($input ?? '', ENT_QUOTES | ENT_HTML5, 'UTF-8');
    }

    public static function js(mixed $input): string
    {
        return json_encode($input,
            JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_THROW_ON_ERROR
        );
    }

    public static function url(?string $input): string
    {
        return rawurlencode($input ?? '');
    }

    public static function attr(?string $input): string
    {
        return htmlspecialchars($input ?? '', ENT_QUOTES | ENT_HTML5, 'UTF-8');
    }

    public static function css(?string $input): string
    {
        // Strip everything except alphanumeric, spaces, hyphens, and basic punctuation
        return preg_replace('/[^a-zA-Z0-9\s\-_.#]/', '', $input ?? '');
    }
}
```

---

## CsrfGuard

```php
class CsrfGuard
{
    private const TOKEN_KEY = '_csrf_token';
    private const TIME_KEY  = '_csrf_time';

    public static function generate(): string
    {
        $token = bin2hex(random_bytes(32));
        $_SESSION[self::TOKEN_KEY] = $token;
        $_SESSION[self::TIME_KEY]  = time();
        return $token;
    }

    public static function validate(?string $token, int $maxAge = 7200): bool
    {
        if ($token === null || !isset($_SESSION[self::TOKEN_KEY], $_SESSION[self::TIME_KEY])) {
            return false;
        }

        $valid = hash_equals($_SESSION[self::TOKEN_KEY], $token);
        $fresh = (time() - $_SESSION[self::TIME_KEY]) <= $maxAge;

        // Single-use: regenerate after validation attempt
        unset($_SESSION[self::TOKEN_KEY], $_SESSION[self::TIME_KEY]);

        return $valid && $fresh;
    }

    public static function field(): string
    {
        $token = self::generate();
        return '<input type="hidden" name="csrf_token" value="'
            . htmlspecialchars($token, ENT_QUOTES, 'UTF-8') . '">';
    }
}
```

---

## SecureUpload

```php
class SecureUpload
{
    private const MAX_SIZE = 5 * 1024 * 1024; // 5MB

    private const ALLOWED_TYPES = [
        'image/jpeg' => ['jpg', 'jpeg'],
        'image/png'  => ['png'],
        'image/gif'  => ['gif'],
        'image/webp' => ['webp'],
        'application/pdf' => ['pdf'],
    ];

    public static function validate(array $file): array
    {
        $errors = [];

        // Check upload errors
        if ($file['error'] !== UPLOAD_ERR_OK) {
            $errors[] = 'Upload failed with error code: ' . $file['error'];
            return $errors;
        }

        // Check file size
        if ($file['size'] > self::MAX_SIZE) {
            $errors[] = 'File exceeds maximum size of ' . (self::MAX_SIZE / 1024 / 1024) . 'MB';
        }

        // Validate MIME type using magic bytes (finfo), NOT the client-provided type
        $finfo = new finfo(FILEINFO_MIME_TYPE);
        $detectedType = $finfo->file($file['tmp_name']);

        if (!isset(self::ALLOWED_TYPES[$detectedType])) {
            $errors[] = 'File type not allowed: ' . $detectedType;
            return $errors;
        }

        // Validate extension matches detected MIME
        $ext = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
        if (!in_array($ext, self::ALLOWED_TYPES[$detectedType], true)) {
            $errors[] = 'File extension does not match content type';
        }

        return $errors;
    }

    public static function store(array $file, string $uploadDir): string
    {
        // Generate random filename (never use original)
        $finfo = new finfo(FILEINFO_MIME_TYPE);
        $detectedType = $finfo->file($file['tmp_name']);
        $ext = self::ALLOWED_TYPES[$detectedType][0];
        $filename = bin2hex(random_bytes(16)) . '.' . $ext;

        $destination = rtrim($uploadDir, '/') . '/' . $filename;

        if (!move_uploaded_file($file['tmp_name'], $destination)) {
            throw new RuntimeException('Failed to move uploaded file');
        }

        // Set restrictive permissions
        chmod($destination, 0644);

        return $filename;
    }
}
```

---

## Error & Exception Handlers

```php
// Custom error handler — log details, show generic message
set_error_handler(function (int $errno, string $errstr, string $errfile, int $errline): bool {
    error_log("[{$errno}] {$errstr} in {$errfile}:{$errline}");

    if ($errno === E_USER_ERROR) {
        http_response_code(500);
        if (!headers_sent()) {
            header('Content-Type: application/json');
        }
        echo json_encode(['success' => false, 'message' => 'Internal server error']);
        exit(1);
    }

    return true; // Don't execute PHP's internal error handler
});

// Custom exception handler — catch unhandled exceptions
set_exception_handler(function (Throwable $e): void {
    error_log('Uncaught exception: ' . $e->getMessage()
        . ' in ' . $e->getFile() . ':' . $e->getLine()
        . "\nStack trace: " . $e->getTraceAsString()
    );

    http_response_code(500);
    if (!headers_sent()) {
        header('Content-Type: application/json');
    }
    echo json_encode(['success' => false, 'message' => 'Internal server error']);
    exit(1);
});
```

---

## Cryptographic Functions (AES-256-GCM)

```php
function encrypt(string $plaintext, string $key): string
{
    if (mb_strlen($key, '8bit') !== 32) {
        throw new InvalidArgumentException('Key must be 32 bytes for AES-256');
    }

    $iv = random_bytes(12); // 96-bit IV for GCM
    $tag = '';

    $ciphertext = openssl_encrypt(
        $plaintext,
        'aes-256-gcm',
        $key,
        OPENSSL_RAW_DATA,
        $iv,
        $tag,
        '',  // AAD
        16   // Tag length
    );

    if ($ciphertext === false) {
        throw new RuntimeException('Encryption failed');
    }

    // Return IV + tag + ciphertext, base64 encoded
    return base64_encode($iv . $tag . $ciphertext);
}

function decrypt(string $encoded, string $key): string
{
    if (mb_strlen($key, '8bit') !== 32) {
        throw new InvalidArgumentException('Key must be 32 bytes for AES-256');
    }

    $data = base64_decode($encoded, true);
    if ($data === false || strlen($data) < 28) { // 12 IV + 16 tag = 28 minimum
        throw new RuntimeException('Invalid ciphertext format');
    }

    $iv         = substr($data, 0, 12);
    $tag        = substr($data, 12, 16);
    $ciphertext = substr($data, 28);

    $plaintext = openssl_decrypt(
        $ciphertext,
        'aes-256-gcm',
        $key,
        OPENSSL_RAW_DATA,
        $iv,
        $tag
    );

    if ($plaintext === false) {
        throw new RuntimeException('Decryption failed — data may be tampered');
    }

    return $plaintext;
}
```

---

## Password Hashing (Argon2id)

```php
// Hash password — ALWAYS use Argon2id
function hashPassword(string $password): string
{
    return password_hash($password, PASSWORD_ARGON2ID, [
        'memory_cost' => 65536, // 64MB
        'time_cost'   => 4,
        'threads'     => 3,
    ]);
}

// Verify password — handles rehashing if defaults change
function verifyPassword(string $password, string $hash): bool
{
    if (!password_verify($password, $hash)) {
        return false;
    }

    // Rehash if algorithm/options changed
    if (password_needs_rehash($hash, PASSWORD_ARGON2ID, [
        'memory_cost' => 65536, 'time_cost' => 4, 'threads' => 3,
    ])) {
        // Store new hash (caller should update DB)
        // $newHash = hashPassword($password);
    }

    return true;
}

// HMAC for data integrity
function signData(string $payload, string $secret): string
{
    return hash_hmac('sha256', $payload, $secret);
}

// Timing-safe comparison for secrets
function verifySignature(string $expected, string $actual): bool
{
    return hash_equals($expected, $actual);
}
```

---

**Sources:**
- PHP Security: https://www.php.net/manual/en/security.php
- OWASP PHP: https://cheatsheetseries.owasp.org/cheatsheets/PHP_Configuration_Cheat_Sheet.html
