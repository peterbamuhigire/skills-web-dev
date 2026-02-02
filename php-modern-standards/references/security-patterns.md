# PHP Security Patterns

Comprehensive security patterns for PHP applications covering input validation, SQL injection prevention, XSS protection, CSRF defense, secure password handling, session security, and file upload security.

## Overview

Security is paramount in PHP applications as they often handle sensitive user data, authentication, and financial transactions. PHP's flexibility creates opportunities for vulnerabilities if security best practices aren't followed.

**Common PHP Vulnerabilities:**
- SQL Injection
- Cross-Site Scripting (XSS)
- Cross-Site Request Forgery (CSRF)
- Insecure Password Storage
- Session Hijacking
- File Inclusion Attacks
- File Upload Vulnerabilities
- Command Injection

## Input Validation and Sanitization

Input validation ensures data meets expected formats before processing, while sanitization removes or encodes potentially dangerous content.

### Email Validation

```php
<?php

declare(strict_types=1);

function validateEmail(string $email): bool
{
    return filter_var($email, FILTER_VALIDATE_EMAIL) !== false;
}

// Example usage
$email = $_POST['email'] ?? '';
if (!validateEmail($email)) {
    throw new InvalidEmailException('Invalid email address');
}
```

### URL Validation

```php
<?php

declare(strict_types=1);

function validateUrl(string $url): bool
{
    return filter_var($url, FILTER_VALIDATE_URL) !== false;
}

// Validate with specific schemes
function validateHttpUrl(string $url): bool
{
    if (!filter_var($url, FILTER_VALIDATE_URL)) {
        return false;
    }

    $scheme = parse_url($url, PHP_URL_SCHEME);
    return in_array($scheme, ['http', 'https'], true);
}
```

### Integer Validation with Range

```php
<?php

declare(strict_types=1);

function validateInt(
    mixed $value,
    int $min = PHP_INT_MIN,
    int $max = PHP_INT_MAX
): ?int {
    $int = filter_var($value, FILTER_VALIDATE_INT, [
        'options' => [
            'min_range' => $min,
            'max_range' => $max,
        ],
    ]);

    return $int !== false ? $int : null;
}

// Example usage
$age = validateInt($_POST['age'] ?? null, 13, 120);
if ($age === null) {
    throw new ValidationException('Age must be between 13 and 120');
}
```

### String Sanitization

```php
<?php

declare(strict_types=1);

function sanitizeString(string $input): string
{
    // Remove null bytes (prevents null byte injection)
    $sanitized = str_replace("\0", '', $input);

    // Remove control characters
    $sanitized = preg_replace('/[\x00-\x1F\x7F]/u', '', $sanitized);

    return trim($sanitized);
}

// Username validation example
function validateUsername(string $username): bool
{
    $sanitized = sanitizeString($username);

    // Alphanumeric and underscore only, 3-20 characters
    return preg_match('/^[a-zA-Z0-9_]{3,20}$/', $sanitized) === 1;
}
```

### HTML Sanitization (Output Encoding)

```php
<?php

declare(strict_types=1);

function sanitizeHtml(string $input): string
{
    return htmlspecialchars($input, ENT_QUOTES | ENT_HTML5, 'UTF-8');
}

// For HTML attributes
function sanitizeHtmlAttribute(string $input): string
{
    return htmlspecialchars($input, ENT_QUOTES, 'UTF-8');
}

// For JSON in HTML context
function sanitizeJson(mixed $data): string
{
    return json_encode(
        $data,
        JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_THROW_ON_ERROR
    );
}
```

### Complete Validation Example

```php
<?php

declare(strict_types=1);

final readonly class UserValidator
{
    private array $errors = [];

    public function validate(array $data): ValidationResult
    {
        $errors = [];

        // Validate email
        if (!isset($data['email']) || !$this->validateEmail($data['email'])) {
            $errors['email'] = 'Invalid email address';
        }

        // Validate age
        $age = $this->validateInt($data['age'] ?? null, 13, 120);
        if ($age === null) {
            $errors['age'] = 'Age must be between 13 and 120';
        }

        // Validate username
        $username = $this->sanitizeString($data['username'] ?? '');
        if (!preg_match('/^[a-zA-Z0-9_]{3,20}$/', $username)) {
            $errors['username'] = 'Username must be 3-20 alphanumeric characters or underscores';
        }

        // Validate password strength
        if (!$this->validatePasswordStrength($data['password'] ?? '')) {
            $errors['password'] = 'Password must be at least 8 characters with uppercase, lowercase, number, and special character';
        }

        // Validate phone (optional)
        if (isset($data['phone']) && !preg_match('/^\+?[0-9]{10,15}$/', $data['phone'])) {
            $errors['phone'] = 'Invalid phone number format';
        }

        return new ValidationResult($errors);
    }

    private function validateEmail(string $email): bool
    {
        return filter_var($email, FILTER_VALIDATE_EMAIL) !== false;
    }

    private function validateInt(mixed $value, int $min, int $max): ?int
    {
        $int = filter_var($value, FILTER_VALIDATE_INT, [
            'options' => ['min_range' => $min, 'max_range' => $max],
        ]);

        return $int !== false ? $int : null;
    }

    private function sanitizeString(string $input): string
    {
        $sanitized = str_replace("\0", '', $input);
        return trim(preg_replace('/[\x00-\x1F\x7F]/u', '', $sanitized));
    }

    private function validatePasswordStrength(string $password): bool
    {
        // At least 8 characters, 1 uppercase, 1 lowercase, 1 number, 1 special char
        return preg_match('/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$/', $password) === 1;
    }
}

final readonly class ValidationResult
{
    public function __construct(
        private array $errors = [],
    ) {
    }

    public function isValid(): bool
    {
        return empty($this->errors);
    }

    public function getErrors(): array
    {
        return $this->errors;
    }
}
```

## SQL Injection Prevention

SQL injection is one of the most dangerous vulnerabilities. Always use prepared statements with parameterized queries.

### Using PDO with Prepared Statements

```php
<?php

declare(strict_types=1);

final readonly class UserRepository
{
    public function __construct(
        private \PDO $pdo,
    ) {
    }

    // ✓ CORRECT: Prepared statement with positional parameters
    public function findByEmail(string $email): ?User
    {
        $stmt = $this->pdo->prepare('SELECT * FROM users WHERE email = ?');
        $stmt->execute([$email]);

        $row = $stmt->fetch(\PDO::FETCH_ASSOC);

        return $row ? $this->hydrate($row) : null;
    }

    // ✓ CORRECT: Prepared statement with named parameters
    public function findByEmailAndTenant(string $email, int $tenantId): ?User
    {
        $stmt = $this->pdo->prepare(
            'SELECT * FROM users WHERE email = :email AND tenant_id = :tenant_id'
        );

        $stmt->execute([
            'email' => $email,
            'tenant_id' => $tenantId,
        ]);

        $row = $stmt->fetch(\PDO::FETCH_ASSOC);

        return $row ? $this->hydrate($row) : null;
    }

    // ✓ CORRECT: Prepared statement with IN clause
    public function findByIds(array $ids): array
    {
        if (empty($ids)) {
            return [];
        }

        // Validate all IDs are integers
        $ids = array_map('intval', $ids);

        // Build placeholders
        $placeholders = implode(',', array_fill(0, count($ids), '?'));

        $stmt = $this->pdo->prepare(
            "SELECT * FROM users WHERE id IN ($placeholders)"
        );

        $stmt->execute($ids);

        return array_map(
            fn (array $row) => $this->hydrate($row),
            $stmt->fetchAll(\PDO::FETCH_ASSOC)
        );
    }

    // ✗ WRONG: String concatenation (VULNERABLE!)
    public function findByEmailVulnerable(string $email): ?User
    {
        $query = "SELECT * FROM users WHERE email = '$email'";
        $stmt = $this->pdo->query($query); // SQL INJECTION RISK!

        $row = $stmt->fetch(\PDO::FETCH_ASSOC);

        return $row ? $this->hydrate($row) : null;
    }

    private function hydrate(array $row): User
    {
        return new User(
            id: (int) $row['id'],
            email: $row['email'],
            name: $row['name']
        );
    }
}
```

### Dynamic Table Names (Use Whitelist)

```php
<?php

declare(strict_types=1);

final readonly class ReportGenerator
{
    private const ALLOWED_TABLES = [
        'users',
        'orders',
        'products',
        'invoices',
    ];

    public function __construct(
        private \PDO $pdo,
    ) {
    }

    public function generateReport(string $tableName): array
    {
        // ✓ CORRECT: Whitelist validation
        if (!in_array($tableName, self::ALLOWED_TABLES, true)) {
            throw new InvalidArgumentException('Invalid table name');
        }

        // Safe to use in query since it's whitelisted
        $query = "SELECT * FROM $tableName WHERE created_at > ?";
        $stmt = $this->pdo->prepare($query);
        $stmt->execute([date('Y-m-d', strtotime('-30 days'))]);

        return $stmt->fetchAll(\PDO::FETCH_ASSOC);
    }
}
```

## Cross-Site Scripting (XSS) Prevention

XSS allows attackers to inject malicious scripts into web pages. Always escape output based on context.

### HTML Context Escaping

```php
<?php

declare(strict_types=1);

// ✓ CORRECT: Escape for HTML body
echo htmlspecialchars($userInput, ENT_QUOTES | ENT_HTML5, 'UTF-8');

// ✓ CORRECT: Escape for HTML attributes
<input type="text" value="<?= htmlspecialchars($userInput, ENT_QUOTES, 'UTF-8') ?>">

// ✗ WRONG: Unescaped output
<div><?= $userInput ?></div> // VULNERABLE!
```

### JavaScript Context Escaping

```php
<?php

declare(strict_types=1);

// ✓ CORRECT: JSON encoding for JavaScript
<script>
const userData = <?= json_encode($user, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT) ?>;
</script>

// ✗ WRONG: Direct output in JavaScript
<script>
const name = "<?= $userName ?>"; // VULNERABLE!
</script>
```

### URL Context Escaping

```php
<?php

declare(strict_types=1);

// ✓ CORRECT: URL encoding
$safeUrl = 'https://example.com/search?q=' . urlencode($searchQuery);

// ✓ CORRECT: For href attributes, also escape HTML
<a href="<?= htmlspecialchars($safeUrl, ENT_QUOTES, 'UTF-8') ?>">Search</a>

// ✗ WRONG: Unencoded URL parameter
$url = "https://example.com/search?q=$searchQuery"; // VULNERABLE!
```

### Content Security Policy (CSP)

```php
<?php

declare(strict_types=1);

// Set CSP header to prevent inline scripts
header("Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-$nonce'; style-src 'self' 'nonce-$nonce'");

// In HTML, use nonce for inline scripts
<script nonce="<?= $nonce ?>">
  // Safe inline script
</script>
```

## Cross-Site Request Forgery (CSRF) Prevention

CSRF attacks trick users into performing unwanted actions. Implement CSRF tokens for all state-changing requests.

### CSRF Token Generation and Validation

```php
<?php

declare(strict_types=1);

final readonly class CsrfProtection
{
    private const TOKEN_LENGTH = 32;

    public function generateToken(): string
    {
        $token = bin2hex(random_bytes(self::TOKEN_LENGTH));
        $_SESSION['csrf_token'] = $token;
        $_SESSION['csrf_token_time'] = time();

        return $token;
    }

    public function validateToken(string $token): bool
    {
        if (!isset($_SESSION['csrf_token'])) {
            return false;
        }

        // Token expires after 2 hours
        if (time() - ($_SESSION['csrf_token_time'] ?? 0) > 7200) {
            unset($_SESSION['csrf_token'], $_SESSION['csrf_token_time']);
            return false;
        }

        // Use hash_equals to prevent timing attacks
        return hash_equals($_SESSION['csrf_token'], $token);
    }

    public function requireValidToken(): void
    {
        $token = $_POST['csrf_token'] ?? $_SERVER['HTTP_X_CSRF_TOKEN'] ?? '';

        if (!$this->validateToken($token)) {
            throw new CsrfTokenException('Invalid or expired CSRF token');
        }
    }
}

// Usage in form
$csrf = new CsrfProtection();
$token = $csrf->generateToken();
?>

<form method="POST" action="/update-profile">
    <input type="hidden" name="csrf_token" value="<?= htmlspecialchars($token, ENT_QUOTES, 'UTF-8') ?>">
    <!-- form fields -->
    <button type="submit">Update</button>
</form>

<?php
// In the POST handler
$csrf->requireValidToken();
// Process form...
```

### Double Submit Cookie Pattern

```php
<?php

declare(strict_types=1);

final readonly class CsrfDoubleSubmit
{
    public function generateToken(): string
    {
        $token = bin2hex(random_bytes(32));

        // Set as HTTP-only cookie
        setcookie(
            name: 'csrf_token',
            value: $token,
            expires_or_options: [
                'expires' => time() + 7200,
                'path' => '/',
                'domain' => '',
                'secure' => true,
                'httponly' => true,
                'samesite' => 'Strict',
            ]
        );

        return $token;
    }

    public function validateToken(string $token): bool
    {
        $cookieToken = $_COOKIE['csrf_token'] ?? '';

        return hash_equals($cookieToken, $token);
    }
}
```

## Secure Password Handling

Never store passwords in plain text. Always use strong hashing algorithms.

### Password Hashing (Argon2id)

```php
<?php

declare(strict_types=1);

final readonly class PasswordHasher
{
    // Use Argon2id (most secure as of 2026)
    public function hash(string $plainPassword): string
    {
        return password_hash($plainPassword, PASSWORD_ARGON2ID, [
            'memory_cost' => 65536, // 64MB
            'time_cost' => 4,       // 4 iterations
            'threads' => 3,         // 3 parallel threads
        ]);
    }

    public function verify(string $plainPassword, string $hashedPassword): bool
    {
        return password_verify($plainPassword, $hashedPassword);
    }

    public function needsRehash(string $hashedPassword): bool
    {
        return password_needs_rehash($hashedPassword, PASSWORD_ARGON2ID, [
            'memory_cost' => 65536,
            'time_cost' => 4,
            'threads' => 3,
        ]);
    }

    // Complete authentication flow
    public function authenticate(string $email, string $plainPassword): ?User
    {
        $user = $this->userRepository->findByEmail($email);

        if ($user === null) {
            // Prevent timing attacks: still hash even if user not found
            $this->hash('dummy_password');
            return null;
        }

        if (!$this->verify($plainPassword, $user->hashedPassword)) {
            return null;
        }

        // Check if password needs rehash (algorithm or cost changed)
        if ($this->needsRehash($user->hashedPassword)) {
            $newHash = $this->hash($plainPassword);
            $this->userRepository->updatePassword($user->id, $newHash);
        }

        return $user;
    }
}
```

### Password Policy Enforcement

```php
<?php

declare(strict_types=1);

final readonly class PasswordPolicy
{
    private const MIN_LENGTH = 12;
    private const MAX_LENGTH = 128;

    public function validate(string $password): ValidationResult
    {
        $errors = [];

        // Length check
        $length = mb_strlen($password);
        if ($length < self::MIN_LENGTH) {
            $errors[] = sprintf('Password must be at least %d characters', self::MIN_LENGTH);
        }

        if ($length > self::MAX_LENGTH) {
            $errors[] = sprintf('Password must not exceed %d characters', self::MAX_LENGTH);
        }

        // Complexity checks
        if (!preg_match('/[a-z]/', $password)) {
            $errors[] = 'Password must contain at least one lowercase letter';
        }

        if (!preg_match('/[A-Z]/', $password)) {
            $errors[] = 'Password must contain at least one uppercase letter';
        }

        if (!preg_match('/[0-9]/', $password)) {
            $errors[] = 'Password must contain at least one number';
        }

        if (!preg_match('/[^a-zA-Z0-9]/', $password)) {
            $errors[] = 'Password must contain at least one special character';
        }

        // Check against common passwords (basic example)
        if ($this->isCommonPassword($password)) {
            $errors[] = 'Password is too common, please choose a stronger password';
        }

        return new ValidationResult($errors);
    }

    private function isCommonPassword(string $password): bool
    {
        // In production, check against haveibeenpwned.com API or local database
        $commonPasswords = [
            'password123',
            'admin123',
            'Password1!',
            // ... add more common passwords
        ];

        return in_array(strtolower($password), array_map('strtolower', $commonPasswords), true);
    }
}
```

## Session Security

Secure session management prevents session hijacking and fixation attacks.

### Secure Session Configuration

```php
<?php

declare(strict_types=1);

// Configure session settings (place in bootstrap/initialization)
ini_set('session.cookie_httponly', '1'); // Prevent JavaScript access
ini_set('session.cookie_secure', '1');   // HTTPS only
ini_set('session.cookie_samesite', 'Strict'); // CSRF protection
ini_set('session.use_strict_mode', '1'); // Reject uninitialized session IDs
ini_set('session.use_only_cookies', '1'); // No URL-based sessions
ini_set('session.cookie_lifetime', '0'); // Session cookie (expires on browser close)
ini_set('session.gc_maxlifetime', '3600'); // 1 hour server-side expiration

session_start([
    'cookie_lifetime' => 0,
    'cookie_httponly' => true,
    'cookie_secure' => true,
    'cookie_samesite' => 'Strict',
    'use_strict_mode' => true,
    'use_only_cookies' => true,
]);
```

### Session Regeneration

```php
<?php

declare(strict_types=1);

final readonly class SessionManager
{
    // Regenerate session ID after login to prevent session fixation
    public function regenerateAfterLogin(): void
    {
        session_regenerate_id(true); // Delete old session
        $_SESSION['user_id'] = $userId;
        $_SESSION['login_time'] = time();
        $_SESSION['ip_address'] = $_SERVER['REMOTE_ADDR'];
        $_SESSION['user_agent'] = $_SERVER['HTTP_USER_AGENT'];
    }

    // Validate session on each request
    public function validateSession(): bool
    {
        // Check session age
        if (!isset($_SESSION['login_time'])) {
            return false;
        }

        // Session timeout: 1 hour
        if (time() - $_SESSION['login_time'] > 3600) {
            $this->destroy();
            return false;
        }

        // Validate IP address (optional, can break with proxies)
        if (($_SESSION['ip_address'] ?? '') !== $_SERVER['REMOTE_ADDR']) {
            $this->destroy();
            return false;
        }

        // Validate user agent
        if (($_SESSION['user_agent'] ?? '') !== $_SERVER['HTTP_USER_AGENT']) {
            $this->destroy();
            return false;
        }

        // Regenerate ID periodically (every 15 minutes)
        if (!isset($_SESSION['last_regeneration'])) {
            $_SESSION['last_regeneration'] = time();
        } elseif (time() - $_SESSION['last_regeneration'] > 900) {
            session_regenerate_id(true);
            $_SESSION['last_regeneration'] = time();
        }

        return true;
    }

    public function destroy(): void
    {
        $_SESSION = [];

        if (ini_get('session.use_cookies')) {
            $params = session_get_cookie_params();
            setcookie(
                session_name(),
                '',
                [
                    'expires' => time() - 42000,
                    'path' => $params['path'],
                    'domain' => $params['domain'],
                    'secure' => $params['secure'],
                    'httponly' => $params['httponly'],
                    'samesite' => $params['samesite'],
                ]
            );
        }

        session_destroy();
    }
}
```

## File Upload Security

File uploads are a common attack vector. Validate file types, names, and contents.

### Secure File Upload Handler

```php
<?php

declare(strict_types=1);

final readonly class FileUploadHandler
{
    private const MAX_FILE_SIZE = 5242880; // 5MB
    private const ALLOWED_TYPES = [
        'image/jpeg',
        'image/png',
        'image/gif',
        'application/pdf',
    ];
    private const ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'pdf'];

    public function __construct(
        private string $uploadDirectory,
    ) {
    }

    public function handleUpload(array $file): UploadResult
    {
        // Check for upload errors
        if ($file['error'] !== UPLOAD_ERR_OK) {
            return UploadResult::error($this->getUploadErrorMessage($file['error']));
        }

        // Validate file size
        if ($file['size'] > self::MAX_FILE_SIZE) {
            return UploadResult::error('File size exceeds maximum allowed (5MB)');
        }

        // Validate MIME type
        $finfo = new \finfo(FILEINFO_MIME_TYPE);
        $mimeType = $finfo->file($file['tmp_name']);

        if (!in_array($mimeType, self::ALLOWED_TYPES, true)) {
            return UploadResult::error('Invalid file type');
        }

        // Validate file extension
        $extension = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
        if (!in_array($extension, self::ALLOWED_EXTENSIONS, true)) {
            return UploadResult::error('Invalid file extension');
        }

        // Generate safe filename (remove all special characters)
        $safeFilename = $this->generateSafeFilename($extension);

        // Move file to upload directory
        $destination = $this->uploadDirectory . DIRECTORY_SEPARATOR . $safeFilename;

        if (!move_uploaded_file($file['tmp_name'], $destination)) {
            return UploadResult::error('Failed to move uploaded file');
        }

        // Set restrictive permissions
        chmod($destination, 0644);

        return UploadResult::success($safeFilename);
    }

    private function generateSafeFilename(string $extension): string
    {
        // Use random filename to prevent directory traversal and collisions
        return bin2hex(random_bytes(16)) . '.' . $extension;
    }

    private function getUploadErrorMessage(int $errorCode): string
    {
        return match ($errorCode) {
            UPLOAD_ERR_INI_SIZE, UPLOAD_ERR_FORM_SIZE => 'File size exceeds maximum allowed',
            UPLOAD_ERR_PARTIAL => 'File was only partially uploaded',
            UPLOAD_ERR_NO_FILE => 'No file was uploaded',
            UPLOAD_ERR_NO_TMP_DIR => 'Missing temporary folder',
            UPLOAD_ERR_CANT_WRITE => 'Failed to write file to disk',
            UPLOAD_ERR_EXTENSION => 'File upload stopped by extension',
            default => 'Unknown upload error',
        };
    }
}

final readonly class UploadResult
{
    private function __construct(
        private bool $success,
        private ?string $filename = null,
        private ?string $error = null,
    ) {
    }

    public static function success(string $filename): self
    {
        return new self(success: true, filename: $filename);
    }

    public static function error(string $error): self
    {
        return new self(success: false, error: $error);
    }

    public function isSuccess(): bool
    {
        return $this->success;
    }

    public function getFilename(): ?string
    {
        return $this->filename;
    }

    public function getError(): ?string
    {
        return $this->error;
    }
}
```

### Image Validation (Additional Security)

```php
<?php

declare(strict_types=1);

final readonly class ImageValidator
{
    public function validateImage(string $filePath): bool
    {
        // Verify it's actually an image
        $imageInfo = getimagesize($filePath);

        if ($imageInfo === false) {
            return false;
        }

        // Check image dimensions (prevent DoS via large images)
        [$width, $height] = $imageInfo;
        if ($width > 5000 || $height > 5000) {
            return false;
        }

        // Verify MIME type
        $allowedTypes = [IMAGETYPE_JPEG, IMAGETYPE_PNG, IMAGETYPE_GIF];
        if (!in_array($imageInfo[2], $allowedTypes, true)) {
            return false;
        }

        return true;
    }

    // Re-encode image to strip metadata and potential malicious code
    public function sanitizeImage(string $sourcePath, string $destinationPath): bool
    {
        $imageInfo = getimagesize($sourcePath);

        if ($imageInfo === false) {
            return false;
        }

        // Load image based on type
        $image = match ($imageInfo[2]) {
            IMAGETYPE_JPEG => imagecreatefromjpeg($sourcePath),
            IMAGETYPE_PNG => imagecreatefrompng($sourcePath),
            IMAGETYPE_GIF => imagecreatefromgif($sourcePath),
            default => false,
        };

        if ($image === false) {
            return false;
        }

        // Save as new image (strips metadata)
        $success = match ($imageInfo[2]) {
            IMAGETYPE_JPEG => imagejpeg($image, $destinationPath, 90),
            IMAGETYPE_PNG => imagepng($image, $destinationPath, 9),
            IMAGETYPE_GIF => imagegif($image, $destinationPath),
            default => false,
        };

        imagedestroy($image);

        return $success;
    }
}
```

## Command Injection Prevention

Never pass user input directly to shell commands.

```php
<?php

declare(strict_types=1);

// ✓ CORRECT: Use PHP functions instead of shell commands
function getFileSize(string $filename): int
{
    // Validate filename
    if (!preg_match('/^[a-zA-Z0-9._-]+$/', $filename)) {
        throw new InvalidArgumentException('Invalid filename');
    }

    return filesize($filename);
}

// ✗ WRONG: Shell command with user input
function getFileSizeVulnerable(string $filename): string
{
    return shell_exec("ls -lh $filename"); // COMMAND INJECTION!
}

// If shell command is absolutely necessary, use escapeshellarg
function safeShellCommand(string $userInput): string
{
    // Escape the argument
    $safe = escapeshellarg($userInput);

    // Use with safe command
    return shell_exec("ls -lh $safe");
}
```

## Security Headers

Implement security headers to protect against various attacks.

```php
<?php

declare(strict_types=1);

function setSecurityHeaders(): void
{
    // Prevent clickjacking
    header('X-Frame-Options: DENY');

    // XSS protection
    header('X-Content-Type-Options: nosniff');
    header('X-XSS-Protection: 1; mode=block');

    // Content Security Policy
    header("Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;");

    // HTTPS enforcement
    header('Strict-Transport-Security: max-age=31536000; includeSubDomains; preload');

    // Referrer policy
    header('Referrer-Policy: strict-origin-when-cross-origin');

    // Permissions policy
    header('Permissions-Policy: geolocation=(), microphone=(), camera=()');
}

// Call early in application bootstrap
setSecurityHeaders();
```

## Security Checklist

**Input Validation:**
- ✅ Validate all user input (email, URL, integers, strings)
- ✅ Use filter_var() for built-in validation
- ✅ Sanitize strings (remove control characters, null bytes)
- ✅ Apply whitelist validation when possible
- ✅ Validate file uploads (type, size, extension, content)

**SQL Injection:**
- ✅ Always use prepared statements with PDO
- ✅ Never concatenate user input into SQL queries
- ✅ Whitelist table/column names if dynamic

**XSS Prevention:**
- ✅ Escape all output with htmlspecialchars()
- ✅ Use JSON encoding for JavaScript context
- ✅ URL-encode for URL context
- ✅ Implement Content Security Policy

**CSRF Protection:**
- ✅ Generate and validate CSRF tokens
- ✅ Use SameSite cookie attribute
- ✅ Implement token expiration

**Password Security:**
- ✅ Use Argon2id for password hashing
- ✅ Implement strong password policy
- ✅ Rehash passwords when algorithm changes
- ✅ Prevent timing attacks in authentication

**Session Security:**
- ✅ Use secure, HTTP-only, SameSite cookies
- ✅ Regenerate session ID after login
- ✅ Implement session timeout
- ✅ Validate session integrity

**File Upload Security:**
- ✅ Validate file type, size, extension
- ✅ Use MIME type detection
- ✅ Generate random filenames
- ✅ Store uploads outside webroot when possible
- ✅ Set restrictive file permissions

**Headers:**
- ✅ Set all security headers (CSP, HSTS, X-Frame-Options, etc.)

## References

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- PHP Security Guide: https://phpsecurity.readthedocs.io/
- OWASP PHP Security Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/PHP_Configuration_Cheat_Sheet.html
