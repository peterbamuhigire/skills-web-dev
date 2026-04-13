---
name: php-modern-standards
description: Modern PHP development standards for maintainable, testable, object-oriented
  code. Use when writing PHP 8+ applications, implementing OOP patterns, ensuring
  security, following PSR standards, optimizing performance, or building Laravel...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# PHP Modern Standards

<!-- dual-compat-start -->
## Use When

- Modern PHP development standards for maintainable, testable, object-oriented code. Use when writing PHP 8+ applications, implementing OOP patterns, ensuring security, following PSR standards, optimizing performance, or building Laravel...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `php-modern-standards` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references, examples` only as needed.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
- Use the `examples/` directory for concrete patterns when implementation shape matters.
<!-- dual-compat-end -->
Production-grade PHP patterns for maintainable, testable, secure, high-performance applications.

**Core Principle:** Write type-safe, secure, performant PHP code following PSR standards with modern PHP 8+ features.

**References:**
- `references/performance-efficiency.md` — generators, OPcache, profiling, Fibers deep dive
- `references/code-quality-tooling.md` — PHPStan, Pint config, CI/CD patterns
- `references/rate-limiting.md` — rate limiting patterns
- `references/message-queues.md` — queue patterns
- `references/cache-invalidation.md` — cache invalidation patterns
- `references/resilience-patterns.md` — circuit breakers, retries
- `references/restful-api-patterns.md` — cURL client, Attribute routing, JWT, API versioning, testing
- `references/database-orm-patterns.md` — PDO, QueryBuilder, Active Record Model, soft delete, ORM concepts
- `references/attack-prevention.md` — SQL injection, XSS, CSRF, CSP, brute force, least privilege

**Examples:** `examples/modern-php-patterns.php`, `examples/laravel-patterns.php`
**Security:** Use **php-security** skill for comprehensive security patterns.

✅ PHP 8+ ✅ OOP ✅ Security ✅ Testing ✅ Performance ✅ Laravel | ❌ Legacy PHP (<7.4) ❌ WordPress

---

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

- **Class files:** PascalCase matching class name (`StaffService.php`)
- **Config dirs:** lowercase (`src/config/`, `src/lang/`)
- **Module dirs:** PascalCase matching namespace (`src/HR/Services/`)
- **require/include:** Must match EXACT case on disk
- **Paths:** Use `/` (forward slash). Never hardcode `C:\`. Use `sys_get_temp_dir()` for temp files.

---

## Type System

### Strict Typing (Required)

```php
declare(strict_types=1); // Always — every file

function calculateTotal(int $quantity, float $price): float { }
function getUser(int $id): ?User { }        // Nullable
function log(string $msg): void { }          // Void
function terminate(): never { throw new RuntimeException(); }  // Never (8.1+)
```

### Modern Types

```php
// Union types (PHP 8.0+)
function process(int|float $value): string|int { }

// Intersection types (PHP 8.1+)
function handle(Countable&Traversable $collection): void { }

// Readonly classes (PHP 8.2+)
final readonly class Money
{
    public function __construct(
        public float $amount,
        public string $currency,
    ) {
    }
}
```

### Constructor Promotion (Required for DTOs/Value Objects)

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

---

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

### Named Arguments + Nullsafe Operator

```php
new User(id: 1, email: 'user@example.com', name: 'John');

$country = $user?->getAddress()?->getCountry();
```

### Attributes (PHP 8.0+)

```php
#[\Attribute(\Attribute::TARGET_METHOD)]
final readonly class Route
{
    public function __construct(
        public string $path,
        public string $method = 'GET',
    ) {
    }
}
```

### Fibers (PHP 8.1+) — Concurrency

```php
$fiber = new Fiber(function (): void {
    $value = Fiber::suspend('paused');
    echo "Resumed with: $value";
});

$result = $fiber->start();   // 'paused'
$fiber->resume('hello');     // Resumed with: hello
```

**Decision rule:** Use **Generators** for iterative data processing. Use **Fibers** for concurrent task management (async I/O, multiple waiting tasks).

---

## Performance

**The #1 performance lever is database queries, not PHP code.** If PHP is the bottleneck, you have other problems.

📖 **See `references/performance-efficiency.md` for generators deep dive, OPcache, profiling, Fibers**

### Generators (Memory-Efficient Iteration)

```php
// Process large files without loading into memory
function readCsv(string $path): \Generator
{
    $fh = fopen($path, 'r');
    while (($row = fgetcsv($fh, 1024)) !== false) {
        yield $row;
    }
    fclose($fh);
}

foreach (readCsv('large.csv') as $row) {
    processLine($row);  // Only 1 row in memory at a time
}

// Generator for database results — fetch one at a time
function fetchAll(\PDO $pdo, string $sql): \Generator
{
    $stmt = $pdo->query($sql);
    while ($row = $stmt->fetch(\PDO::FETCH_ASSOC)) {
        yield $row;
    }
}
```

### Built-in Functions Rule (CRITICAL)

**PHP's C-implemented built-in functions are ~100x faster than userland equivalents.**

```php
// ✓ DO: Use built-in sort() — 0.003ms for 10K elements
sort($array);

// ✗ DON'T: Implement your own — 0.306ms for 10K elements (100x slower)
function userQuicksort(array &$list): void { /* ... */ }

// ✓ DO: Use str_contains() (PHP 8.0+) not strpos
str_contains($haystack, $needle);

// ✓ DO: Use array_map/array_filter not foreach for transforms
$names = array_map(fn (User $u) => $u->name, $users);
```

### OPcache (Required in Production)

```ini
; php.ini — production
opcache.enable = 1
opcache.memory_consumption = 256
opcache.max_accelerated_files = 20000
opcache.validate_timestamps = 0     ; Disable in production (deploy script should clear)
opcache.jit = 1255                   ; JIT compilation (PHP 8.0+)
opcache.jit_buffer_size = 128M
```

### SPL Data Structures

```php
$queue = new \SplQueue();         // FIFO
$stack = new \SplStack();         // LIFO
$heap = new \SplMinHeap();        // Priority queue
$fixed = new \SplFixedArray(100); // Fixed-size (less memory than array)
```

---

## SOLID Principles

### Single Responsibility

```php
final readonly class UserValidator { }  // Validation only
final readonly class UserRepository { } // Data access only
```

### Open/Closed + Dependency Inversion

```php
interface PaymentGateway { public function charge(Money $amount): PaymentResult; }
final readonly class StripeGateway implements PaymentGateway { /* ... */ }

// Depend on interface, not concrete class
public function __construct(private PaymentGateway $gateway) { }
```

### Class Design Rules

```php
final class Example
{
    // 1. Constants → 2. Properties → 3. Constructor → 4. Public → 5. Private
    private const MAX = 3;
    private string $name;

    public function __construct(int $id) { }
    public function getName(): string { }
    private function helper(): void { }
}
```

**Use `final` by default.** Forces composition over inheritance. Only use `abstract` when explicitly designing for extension.

---

## Control Flow

### Early Returns (Happy Path Last)

```php
public function process(Order $order): void
{
    if (!$order->isValid()) {
        throw new InvalidOrderException();
    }
    // Happy path continues...
    $this->fulfillment->process($order);
}
```

### Strict Comparison (Always)

```php
if ($status === 'active') { }                    // ✓ CORRECT
if (in_array($role, $roles, true)) { }           // ✓ strict third param
hash_equals($expected, $actual);                  // ✓ timing-safe for secrets
```

---

## Security (Essentials)

**For comprehensive security patterns, use the `php-security` skill.** Key essentials:

```php
// Input validation
filter_var($email, FILTER_VALIDATE_EMAIL);
filter_var($age, FILTER_VALIDATE_INT, ['options' => ['min_range' => 13, 'max_range' => 120]]);

// SQL injection prevention — ALWAYS prepared statements
$stmt = $pdo->prepare('SELECT * FROM users WHERE email = ?');
$stmt->execute([$email]);

// XSS protection — encode output by context
echo htmlspecialchars($input, ENT_QUOTES | ENT_HTML5, 'UTF-8');
echo json_encode($data, JSON_HEX_TAG | JSON_HEX_AMP);

// Password hashing — ALWAYS Argon2id
$hash = password_hash($password, PASSWORD_ARGON2ID, [
    'memory_cost' => 65536, 'time_cost' => 4, 'threads' => 3,
]);

// Session — secure init
ini_set('session.use_strict_mode', '1');
ini_set('session.cookie_httponly', '1');
ini_set('session.cookie_samesite', 'Strict');
session_start();
session_regenerate_id(true); // On auth state change

// Cryptography — use Libsodium (PHP 7.2+ core), not OpenSSL
sodium_crypto_secretbox($message, $nonce, $key);  // Symmetric
sodium_crypto_box($message, $nonce, $keypair);     // Asymmetric
```

---

## Testing

📖 **See `references/code-quality-tooling.md` for PHPStan, Pint config, CI/CD patterns**

### AAA Pattern (Arrange-Act-Assert)

```php
public function testCalculateSubtotal(): void
{
    // Arrange
    $cart = new ShoppingCart();
    $items = [['price' => 10, 'quantity' => 2], ['price' => 5, 'quantity' => 4]];

    // Act
    $subtotal = $cart->calculateSubtotal($items);

    // Assert
    $this->assertEquals(40, $subtotal);
}
```

### Data Providers

```php
/** @dataProvider additionProvider */
public function testAddition(int $a, int $b, int $expected): void
{
    $this->assertEquals($expected, add($a, $b));
}

public static function additionProvider(): array
{
    return [[1, 2, 3], [0, 0, 0], [-1, 1, 0]];
}
```

### Mocking Dependencies

```php
$mockDb = $this->createMock(Database::class);
$mockDb->expects($this->once())
    ->method('query')
    ->willReturn($fakeData);
```

### Exception Testing

```php
public function testDivideByZeroThrows(): void
{
    $this->expectException(DivisionByZeroError::class);
    divide(10, 0);
}
```

---

## Laravel Conventions

### Routes + Controllers

```php
// URLs: kebab-case, Names: camelCase
Route::get('/open-source', [OpenSourceController::class, 'index'])->name('openSource');

// Plural controllers, singular for single resources
final class PostsController extends Controller
{
    public function index(): Response { }
    public function store(StorePostRequest $request): Response { }
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
        return ['email_verified_at' => 'datetime', 'is_active' => 'boolean'];
    }

    public function posts(): HasMany { return $this->hasMany(Post::class); }
}
```

---

## Code Quality Tooling

📖 **See `references/code-quality-tooling.md` for complete configs**

```json
{
    "scripts": {
        "stan": ["./vendor/bin/phpstan analyse --memory-limit=3g"],
        "pint": ["./vendor/bin/pint"],
        "test": ["./vendor/bin/pest --type-coverage"]
    }
}
```

**Required tools:**
- **PHPStan** level 8+ (level 9 for strict projects)
- **Laravel Pint** or **PHP CS Fixer** (PSR-12 base + `final_class`, `strict_comparison`, `declare_strict_types`)
- **PHPUnit** or **PestPHP** with type-coverage

---

## PSR Standards

| Standard | Purpose |
|----------|---------|
| PSR-1 | Basic coding |
| PSR-4 | Autoloading |
| PSR-7 | HTTP messages |
| PSR-11 | Container |
| PSR-12 | Code style |
| PSR-15 | Request handlers |

---

## Anti-Patterns

```php
function process($data) { }              // ✗ No types
if ($value == 1) { }                     // ✗ Loose comparison (use ===)
switch ($status) { }                     // ✗ Use match instead
$GLOBALS['config'] = [];                 // ✗ No globals
$data = file('huge.csv');                // ✗ Use generators!
/** @param string $name */               // ✗ Redundant docblock
public function setName(string $name): void { }
function myQuicksort(array &$list): void { }  // ✗ Use built-in sort()
```

## Checklist

**Code Quality:** ✅ `declare(strict_types=1)` ✅ Full type hints ✅ Readonly for immutable ✅ Final by default ✅ Match over switch ✅ Enums for fixed values ✅ Early returns ✅ Strict comparison ✅ PSR-12 compliant

---
> **Note:** Content trimmed to 500-line standard. Move overflow content to `references/` for on-demand loading.
