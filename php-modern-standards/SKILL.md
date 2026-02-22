---
name: php-modern-standards
description: "Modern PHP development standards for maintainable, testable, object-oriented code. Use when writing PHP 8+ applications, implementing OOP patterns, ensuring security, following PSR standards, optimizing performance, or building Laravel applications. Covers strict typing, modern features, SOLID principles, security patterns, testing, and 2026 international programming standards."
---

## Required Plugins

**Superpowers plugin:** MUST be active for all work using this skill. Use throughout the entire build pipeline — design decisions, code generation, debugging, quality checks, and any task where it offers enhanced capabilities. If superpowers provides a better way to accomplish something, prefer it over the default approach.

# PHP Modern Standards

Production-grade PHP patterns for maintainable, testable, secure, high-performance applications.

**Core Principle:** Write type-safe, secure, performant PHP code following PSR standards with modern PHP 8+ features.

**See subdirectories:** `references/security-patterns.md`, `examples/modern-php-patterns.php`, `examples/laravel-patterns.php`

## When to Use

✅ PHP 8+ applications ✅ OOP architecture ✅ Code security ✅ Testable systems ✅ Performance optimization ✅ Laravel conventions

## File Structure

```php
<?php

declare(strict_types=1);

namespace App\Domain\User;

use App\Domain\Shared\ValueObject;

final readonly class User
{
    public function __construct(
        private int $id,
        private string $email,
    ) {
    }
}
```

**Rules:** Always `declare(strict_types=1)`, one class per file, namespace = directory, import all dependencies.

### Cross-Platform File Naming (MANDATORY)

Code runs on Windows (dev), Ubuntu (staging), and Debian (production). Linux is case-sensitive:

- **Directories:** Use lowercase for config/utility dirs (`src/config/`, `src/lang/`). Use PascalCase for module dirs matching namespace (`src/HR/Services/`, `src/Auth/`).
- **Class files:** PascalCase matching class name (`StaffService.php`, `EmailService.php`).
- **require/include:** Must match EXACT case on disk. `../src/Config/database.php` will fail on Linux if dir is `config/`.
- **Paths:** Use `/` (forward slash) in PHP code. Never hardcode `C:\...` in application logic. Use `DIRECTORY_SEPARATOR` or `/` which PHP handles cross-platform.
- **Temp files:** Use `sys_get_temp_dir()`, not hardcoded paths.

## Type System

### Strict Typing (Required)

```php
declare(strict_types=1); // Always

function calculateTotal(int $quantity, float $price): float { }
function getUser(int $id): ?User { } // Nullable
function log(string $msg): void { } // Void
```

### Modern Types

```php
// Union types (PHP 8.0+)
function process(int|float $value): string|int { }

// Intersection types (PHP 8.1+)
function handle(Countable&Traversable $collection): void { }

// Never type (PHP 8.1+)
function terminate(): never { throw new RuntimeException(); }

// Short nullable (?Type not Type|null)
function getName(): ?string // ✓ CORRECT
```

### Typed Properties (Required)

```php
final class User
{
    private int $id;
    private string $email;
    private ?string $nickname = null;
    private array $roles = [];
}
```

### Constructor Promotion

```php
final readonly class User
{
    public function __construct(
        private int $id,
        private string $email,
        private ?string $nickname = null,
    ) {
    }
}
```

### Readonly (PHP 8.1+)

```php
final readonly class Money
{
    public function __construct(
        public float $amount,
        public string $currency,
    ) {
    }
}
```

## Modern Features

### Enums (PHP 8.1+)

```php
enum Status: string
{
    case Pending = 'pending';
    case Active = 'active';

    public function label(): string
    {
        return match ($this) {
            self::Pending => 'Pending',
            self::Active => 'Active',
        };
    }
}
```

### Match (PHP 8.0+)

```php
$status = match ($code) {
    200, 201 => 'success',
    400, 422 => 'error',
    default => 'unknown',
};
```

### Named Arguments

```php
new User(
    id: 1,
    email: 'user@example.com',
    name: 'John',
);
```

### Nullsafe Operator

```php
$country = $user?->getAddress()?->getCountry();
```

### Attributes

```php
#[\Attribute]
final readonly class Route
{
    public function __construct(
        public string $path,
        public string $method = 'GET',
    ) {
    }
}
```

## SOLID Principles

### Single Responsibility

```php
final readonly class UserValidator { }
final readonly class UserRepository { }
```

### Open/Closed

```php
interface PaymentGateway { }
final readonly class StripeGateway implements PaymentGateway { }
```

### Dependency Inversion

```php
public function __construct(
    private PaymentGateway $gateway, // Interface, not concrete
) {
}
```

## Control Flow

### Happy Path Last

```php
public function process(Order $order): void
{
    if (!$order->isValid()) {
        throw new InvalidOrderException();
    }

    // Happy path
    $this->fulfillment->process($order);
}
```

### Avoid `else`

```php
if (!$user->isActive()) {
    return null;
}

return $user->process();
```

### Strict Comparison

```php
if ($status === 'active') { } // ✓ CORRECT
if ($count !== 0) { }
if (in_array($role, $roles, true)) { }
```

## Security

**See `references/security-patterns.md` for complete guide.**

### Input Validation

```php
final readonly class UserValidator
{
    public function validate(array $data): ValidationResult
    {
        $errors = [];

        if (!filter_var($data['email'] ?? '', FILTER_VALIDATE_EMAIL)) {
            $errors['email'] = 'Invalid email';
        }

        $age = filter_var($data['age'] ?? null, FILTER_VALIDATE_INT, [
            'options' => ['min_range' => 13, 'max_range' => 120],
        ]);
        if ($age === false) {
            $errors['age'] = 'Invalid age';
        }

        return new ValidationResult($errors);
    }
}
```

### SQL Injection Prevention

```php
// ✓ CORRECT
$stmt = $pdo->prepare('SELECT * FROM users WHERE email = ?');
$stmt->execute([$email]);

// ✗ WRONG
$query = "SELECT * FROM users WHERE email = '$email'"; // VULNERABLE!
```

### XSS Protection

```php
echo htmlspecialchars($userInput, ENT_QUOTES | ENT_HTML5, 'UTF-8');
echo json_encode($data, JSON_HEX_TAG | JSON_HEX_AMP);
```

### Password Handling

```php
// Hash (Argon2id)
$hash = password_hash($plainPassword, PASSWORD_ARGON2ID, [
    'memory_cost' => 65536,
    'time_cost' => 4,
    'threads' => 3,
]);

// Verify
if (password_verify($plainPassword, $hash)) {
    if (password_needs_rehash($hash, PASSWORD_ARGON2ID)) {
        $newHash = password_hash($plainPassword, PASSWORD_ARGON2ID);
    }
}
```

### CSRF Protection

```php
final readonly class CsrfProtection
{
    public function generateToken(): string
    {
        $token = bin2hex(random_bytes(32));
        $_SESSION['csrf_token'] = $token;
        $_SESSION['csrf_token_time'] = time();
        return $token;
    }

    public function validateToken(string $token): bool
    {
        if (!isset($_SESSION['csrf_token'])) {
            return false;
        }

        if (time() - ($_SESSION['csrf_token_time'] ?? 0) > 7200) {
            return false;
        }

        return hash_equals($_SESSION['csrf_token'], $token);
    }
}
```

## Performance

### Generators

```php
function readLargeFile(string $path): \Generator
{
    $handle = fopen($path, 'r');
    while (($line = fgets($handle)) !== false) {
        yield trim($line);
    }
    fclose($handle);
}

foreach (readLargeFile('large.csv') as $line) {
    processLine($line);
}
```

### SPL Data Structures

```php
$queue = new \SplQueue();
$queue->enqueue('task');
$task = $queue->dequeue();

$pq = new \SplPriorityQueue();
$pq->insert('low', 1);
$pq->insert('high', 10);
```

## Laravel Conventions

### Routes

```php
// URLs: kebab-case, Names: camelCase, Params: camelCase
Route::get('/open-source', [OpenSourceController::class, 'index'])
    ->name('openSource');
```

### Controllers

```php
// Plural for resources
final class PostsController extends Controller
{
    public function index(): Response { }
    public function show(Post $post): Response { }
    public function store(StorePostRequest $request): Response { }
}

// Singular for single resources
final class ProfileController extends Controller
{
    public function show(): Response { }
}
```

### Models

```php
final class User extends Model
{
    protected $fillable = ['name', 'email'];
    protected $hidden = ['password'];

    protected function casts(): array
    {
        return [
            'email_verified_at' => 'datetime',
            'is_active' => 'boolean',
        ];
    }

    public function posts(): HasMany
    {
        return $this->hasMany(Post::class);
    }
}
```

## Class Design

### Use `final` by Default

```php
final readonly class User { } // Default
abstract class BaseController { } // Only when needed
```

### Class Structure Order

```php
final class Example
{
    // 1. Constants
    private const MAX = 3;

    // 2. Properties (public → protected → private)
    public readonly int $id;
    private string $name;

    // 3. Constructor
    public function __construct(int $id) { }

    // 4. Public methods
    public function getName(): string { }

    // 5. Private methods
    private function helper(): void { }
}
```

### Traits (Sparingly)

```php
// One trait per line
final class Article
{
    use Timestampable;
    use Publishable;
}
```

## Anti-Patterns (Avoid)

```php
// ✗ No types
function process($data) { }

// ✗ Loose comparison
if ($value == 1) { }

// ✗ Switch for values
switch ($status) { }

// ✗ Globals
$GLOBALS['config'] = [];

// ✗ Redundant docblocks
/** @param string $name */
public function setName(string $name): void { }
```

## PSR Standards

- **PSR-1:** Basic coding
- **PSR-12:** Style guide (follow this)
- **PSR-4:** Autoloading
- **PSR-7:** HTTP messages
- **PSR-11:** Container
- **PSR-15:** Request handlers

## Tooling

- **PHPStan:** Static analysis (level 8+)
- **PHP CS Fixer:** PSR-12 formatting
- **PHPUnit/Pest:** Testing

## Checklist

✅ `declare(strict_types=1)`
✅ Full type hints
✅ Readonly for immutable
✅ Final by default
✅ Match over switch
✅ Enums for fixed values
✅ Early returns
✅ Strict comparison (===)
✅ Input validation
✅ Prepared statements
✅ Output escaping
✅ Argon2id passwords
✅ Generators for large data
✅ PSR-12 compliant

**References:**
- PHP: https://www.php.net/manual/
- PSR: https://www.php-fig.org/psr/
- Modern PHP: https://phptherightway.com/
