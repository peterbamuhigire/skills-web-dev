# Input Validation & Output Encoding Reference

Comprehensive PHP patterns for validating input and encoding output by context.

**Parent skill:** php-security

## Input Validation Functions

### filter_var() Quick Reference

| Filter | Usage | Example |
|--------|-------|---------|
| `FILTER_VALIDATE_EMAIL` | Email format | `filter_var($email, FILTER_VALIDATE_EMAIL)` |
| `FILTER_VALIDATE_URL` | URL format | `filter_var($url, FILTER_VALIDATE_URL)` |
| `FILTER_VALIDATE_INT` | Integer with range | `filter_var($id, FILTER_VALIDATE_INT, ['options' => ['min_range' => 1]])` |
| `FILTER_VALIDATE_FLOAT` | Decimal number | `filter_var($price, FILTER_VALIDATE_FLOAT)` |
| `FILTER_VALIDATE_IP` | IP address | `filter_var($ip, FILTER_VALIDATE_IP)` |
| `FILTER_VALIDATE_BOOLEAN` | Boolean-like | `filter_var($flag, FILTER_VALIDATE_BOOLEAN, FILTER_NULL_ON_FAILURE)` |
| `FILTER_VALIDATE_DOMAIN` | Domain name | `filter_var($domain, FILTER_VALIDATE_DOMAIN)` |
| `FILTER_SANITIZE_STRING` | Strip tags | Deprecated in PHP 8.1 — use htmlspecialchars() |
| `FILTER_SANITIZE_EMAIL` | Remove illegal chars | `filter_var($email, FILTER_SANITIZE_EMAIL)` |
| `FILTER_SANITIZE_URL` | Remove illegal URL chars | `filter_var($url, FILTER_SANITIZE_URL)` |
| `FILTER_SANITIZE_NUMBER_INT` | Remove non-digits | `filter_var($num, FILTER_SANITIZE_NUMBER_INT)` |

### Validation Pattern: Validate Then Use

```php
declare(strict_types=1);

final readonly class RequestValidator
{
    public static function validateCreateUser(array $data): array
    {
        $errors = [];

        // Required string with length
        $name = trim($data['name'] ?? '');
        if ($name === '' || mb_strlen($name) > 100) {
            $errors['name'] = 'Name is required (max 100 characters)';
        }

        // Email
        $email = filter_var($data['email'] ?? '', FILTER_VALIDATE_EMAIL);
        if ($email === false) {
            $errors['email'] = 'Valid email is required';
        }

        // Integer with range
        $age = filter_var($data['age'] ?? null, FILTER_VALIDATE_INT, [
            'options' => ['min_range' => 13, 'max_range' => 120],
        ]);
        if ($age === false) {
            $errors['age'] = 'Age must be between 13 and 120';
        }

        // Enum / whitelist
        $role = $data['role'] ?? '';
        if (!in_array($role, ['staff', 'member', 'owner'], true)) {
            $errors['role'] = 'Invalid role';
        }

        // Date
        $dob = $data['date_of_birth'] ?? '';
        if (!preg_match('/^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/', $dob)
            || strtotime($dob) === false) {
            $errors['date_of_birth'] = 'Valid date (YYYY-MM-DD) required';
        }

        // Phone (international)
        $phone = $data['phone'] ?? '';
        if ($phone !== '' && !preg_match('/^\+?[1-9]\d{6,14}$/', $phone)) {
            $errors['phone'] = 'Invalid phone number format';
        }

        return $errors;
    }
}
```

### Validation for Different Data Types

```php
// Boolean
$isActive = filter_var($input, FILTER_VALIDATE_BOOLEAN, FILTER_NULL_ON_FAILURE);
if ($isActive === null) { /* invalid */ }

// Decimal/monetary
$amount = filter_var($input, FILTER_VALIDATE_FLOAT);
if ($amount === false || $amount < 0 || $amount > 999999.99) { /* invalid */ }

// UUID v4
$isUuid = preg_match('/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i', $input);

// Slug
$isSlug = preg_match('/^[a-z0-9]+(?:-[a-z0-9]+)*$/', $input);

// Hex color
$isColor = preg_match('/^#[0-9a-fA-F]{6}$/', $input);

// JSON
function isValidJson(string $input): bool
{
    json_decode($input);
    return json_last_error() === JSON_ERROR_NONE;
}
```

### File Input Validation

```php
// File extension whitelist
$allowedExtensions = ['jpg', 'jpeg', 'png', 'gif', 'pdf'];
$ext = strtolower(pathinfo($filename, PATHINFO_EXTENSION));
if (!in_array($ext, $allowedExtensions, true)) { /* reject */ }

// MIME type via magic bytes (not user-supplied Content-Type)
$finfo = new finfo(FILEINFO_MIME_TYPE);
$mimeType = $finfo->file($filePath);
$allowedMimes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'];
if (!in_array($mimeType, $allowedMimes, true)) { /* reject */ }

// File size
if ($file['size'] > 5 * 1024 * 1024) { /* reject: exceeds 5MB */ }

// Image dimensions (prevents decompression bombs)
$info = getimagesize($filePath);
if ($info === false || $info[0] > 4096 || $info[1] > 4096) { /* reject */ }
```

## Output Encoding by Context

### Context Map

| Context | Function | Example |
|---------|----------|---------|
| HTML body | `htmlspecialchars()` | `<p><?= htmlspecialchars($text, ENT_QUOTES \| ENT_HTML5, 'UTF-8') ?></p>` |
| HTML attribute | `htmlspecialchars()` | `<input value="<?= htmlspecialchars($val, ENT_QUOTES \| ENT_HTML5, 'UTF-8') ?>">` |
| JavaScript | `json_encode()` | `<script>var x = <?= json_encode($val, JSON_HEX_TAG \| JSON_HEX_AMP) ?>;</script>` |
| URL parameter | `rawurlencode()` | `<a href="/search?q=<?= rawurlencode($query) ?>">` |
| CSS value | Whitelist only | Strip all non-alphanumeric except `#`, `.`, `%`, `-` |
| SQL | Prepared statements | `$stmt->execute([$val])` — NOT encoding |

### HTML Context Details

```php
// ALWAYS use all three parameters
function e(string $input): string
{
    return htmlspecialchars($input, ENT_QUOTES | ENT_HTML5, 'UTF-8');
}

// Usage in templates
echo '<p>' . e($userComment) . '</p>';
echo '<input type="text" value="' . e($userName) . '">';
echo '<a href="/profile/' . e($userId) . '">' . e($displayName) . '</a>';

// Common mistake: forgetting ENT_QUOTES allows attribute breakout
// <input value="<?= htmlspecialchars($input) ?>">
// If $input = '" onmouseover="alert(1)', the attribute breaks out
// ENT_QUOTES encodes both ' and " to prevent this
```

### JavaScript Context Details

```php
// Safe: json_encode with flags
$safeJs = json_encode($data, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT);

// In template:
echo '<script>var config = ' . $safeJs . ';</script>';

// NEVER do this:
echo '<script>var name = "' . $userName . '";</script>'; // XSS!

// For data attributes (read via JavaScript):
echo '<div data-config="' . e(json_encode($config)) . '"></div>';
// JS: JSON.parse(element.dataset.config)
```

### URL Context Details

```php
// Path segment
$url = '/users/' . rawurlencode($username) . '/profile';

// Query parameter
$url = '/search?' . http_build_query(['q' => $query, 'page' => $page]);

// Full URL validation before redirect
function safeRedirect(string $url, array $allowedHosts = []): void
{
    $parsed = parse_url($url);

    // Only allow relative URLs or whitelisted hosts
    if (isset($parsed['host'])) {
        if (!in_array($parsed['host'], $allowedHosts, true)) {
            $url = '/'; // Fallback to home
        }
    }

    // Only allow http/https
    if (isset($parsed['scheme']) && !in_array($parsed['scheme'], ['http', 'https'], true)) {
        $url = '/';
    }

    header('Location: ' . $url);
    exit;
}
```

## Common Validation Mistakes

### 1. Client-Side Only Validation

```php
// WRONG: Relying on JavaScript validation
// The form has maxlength="100" in HTML — but attacker bypasses it

// CORRECT: Always validate server-side
$name = trim($_POST['name'] ?? '');
if (mb_strlen($name) > 100) {
    $errors[] = 'Name too long';
}
```

### 2. Validating After Use

```php
// WRONG: Use data, then validate
$stmt->execute([$_POST['email']]);
if (!filter_var($_POST['email'], FILTER_VALIDATE_EMAIL)) { /* too late! */ }

// CORRECT: Validate first, use validated data
$email = filter_var($_POST['email'] ?? '', FILTER_VALIDATE_EMAIL);
if ($email === false) {
    return ['error' => 'Invalid email'];
}
$stmt->execute([$email]);
```

### 3. Encoding for Wrong Context

```php
// WRONG: Using htmlspecialchars in JavaScript context
echo '<script>var x = "' . htmlspecialchars($data) . '";</script>';
// Doesn't prevent: \n, \r, or Unicode escapes in JS

// CORRECT: Use json_encode for JavaScript context
echo '<script>var x = ' . json_encode($data, JSON_HEX_TAG | JSON_HEX_AMP) . ';</script>';
```

### 4. Double Encoding

```php
// WRONG: Encoding before storage AND on output
$name = htmlspecialchars($_POST['name']); // Encoded
$stmt->execute([$name]); // Stored encoded
echo htmlspecialchars($name); // Double-encoded: &amp;lt; instead of &lt;

// CORRECT: Store raw, encode on output
$name = trim($_POST['name']); // Raw
$stmt->execute([$name]); // Store raw
echo htmlspecialchars($name, ENT_QUOTES | ENT_HTML5, 'UTF-8'); // Encode on output
```

## Validation Checklist

- [ ] All form inputs validated server-side
- [ ] Email validated with FILTER_VALIDATE_EMAIL
- [ ] Integers validated with FILTER_VALIDATE_INT and range
- [ ] Strings trimmed and length-checked
- [ ] Enum values checked against whitelist
- [ ] File uploads checked by magic bytes, not extension alone
- [ ] URLs validated and scheme-restricted to http/https
- [ ] Dates validated with regex AND strtotime
- [ ] Output encoded based on context (HTML, JS, URL, CSS)
- [ ] No double encoding (store raw, encode on output)
- [ ] Redirect URLs validated against whitelist
- [ ] JSON input parsed with error checking
