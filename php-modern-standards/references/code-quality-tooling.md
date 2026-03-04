# PHP Code Quality & Tooling Reference

Comprehensive configuration guide for PHP static analysis, code style, testing, and CI/CD pipelines. All configurations target PHP 8.1+ and follow modern best practices.

## PHPStan Configuration

PHPStan performs static analysis to find bugs before runtime. Level 9 is maximum strictness.

### Installation

```bash
composer require --dev phpstan/phpstan
composer require --dev larastan/larastan  # Laravel projects
```

### phpstan.neon (Full Configuration)

```neon
includes:
    # - vendor/larastan/larastan/extension.neon  # Uncomment for Laravel
    - phpstan-baseline.neon

parameters:
    level: 9
    paths:
        - app
        - src
        - config
        - database
        - routes
    excludePaths:
        - vendor
        - storage
        - bootstrap/cache
    tmpDir: .phpstan-cache
    checkMissingIterableValueType: true
    checkGenericClassInNonGenericObjectType: false
    reportUnmatchedIgnoredErrors: false
    treatPhpDocTypesAsCertain: false
    ignoreErrors:
        - '#Call to an undefined method Illuminate\\Database\\Eloquent\\Builder#'
```

### Baseline Management for Legacy Code

Generate a baseline to suppress existing errors and enforce zero new errors:

```bash
./vendor/bin/phpstan analyse --generate-baseline --memory-limit=3g
./vendor/bin/phpstan analyse --memory-limit=3g
```

The `--memory-limit=3g` flag prevents out-of-memory crashes on large codebases.

### Custom Rule Example

```php
<?php declare(strict_types=1);

namespace App\PHPStan\Rules;

use PhpParser\Node;
use PhpParser\Node\Expr\FuncCall;
use PHPStan\Analyser\Scope;
use PHPStan\Rules\Rule;
use PHPStan\Rules\RuleErrorBuilder;

/** @implements Rule<FuncCall> */
final class ForbidDumpRule implements Rule
{
    public function getNodeType(): string { return FuncCall::class; }

    /** @return list<\PHPStan\Rules\RuleError> */
    public function processNode(Node $node, Scope $scope): array
    {
        if (! $node->name instanceof \PhpParser\Node\Name) {
            return [];
        }
        $forbidden = ['dd', 'dump', 'var_dump', 'print_r'];
        if (in_array($node->name->toString(), $forbidden, strict: true)) {
            return [RuleErrorBuilder::message(
                sprintf('Call to forbidden function %s().', $node->name->toString())
            )->build()];
        }

        return [];
    }
}
```

## Laravel Pint / PHP CS Fixer

Laravel Pint wraps PHP CS Fixer with sensible defaults. PSR-12 is the base preset.

### pint.json (Complete Configuration)

```json
{
    "preset": "psr12",
    "rules": {
        "final_class": true,
        "strict_comparison": true,
        "declare_strict_types": true,
        "mb_str_functions": true,
        "modernize_strpos": true,
        "protected_to_private": true,
        "no_unused_imports": true,
        "single_quote": true,
        "array_syntax": { "syntax": "short" },
        "ordered_imports": {
            "sort_algorithm": "natural",
            "imports_order": ["const", "class", "function"]
        },
        "trailing_comma_in_multiline": {
            "elements": ["arguments", "arrays", "match", "parameters"]
        },
        "blank_line_before_statement": { "statements": ["return"] },
        "class_attributes_separation": {
            "elements": { "const": "one", "method": "one", "property": "one" }
        }
    }
}
```

### Risky Rules Explanation

Rules marked **risky** may change code behavior:

| Rule | Risk | Why Use It |
|------|------|------------|
| `strict_comparison` | Changes `==` to `===` | Prevents type juggling bugs |
| `declare_strict_types` | Adds `declare(strict_types=1)` | Enforces type safety at runtime |
| `mb_str_functions` | Replaces `strlen` with `mb_strlen` | Fixes multibyte string handling |
| `modernize_strpos` | Replaces `strstr()` with `str_contains()` | Uses PHP 8.0+ functions |
| `protected_to_private` | Changes `protected` to `private` | Tighter encapsulation when no subclass |
| `final_class` | Adds `final` to classes | Enforces composition over inheritance |

### Running Pint

```bash
./vendor/bin/pint              # Fix all files
./vendor/bin/pint --test       # Dry run (check only, no changes)
./vendor/bin/pint app/Services # Fix specific directory
./vendor/bin/pint -v           # Show diff of changes
```

## PestPHP

Pest is an expressive testing framework built on PHPUnit.

### Installation and Setup

```bash
composer require --dev pestphp/pest pestphp/pest-plugin-type-coverage pestphp/pest-plugin-arch
./vendor/bin/pest --init
```

### Architecture Testing

```php
<?php declare(strict_types=1);

arch('models should be readonly')->expect('App\Models')->toBeReadonly();
arch('all classes should be final')->expect('App')->toBeFinal()->ignoring('App\Models');
arch('controllers should have suffix')->expect('App\Http\Controllers')->toHaveSuffix('Controller');
arch('no debugging statements')->expect(['dd', 'dump', 'var_dump', 'ray'])->not->toBeUsed();
arch('services should not depend on controllers')
    ->expect('App\Services')->not->toDependOn('App\Http\Controllers');
```

### Type Coverage and Parallel Testing

```bash
./vendor/bin/pest --type-coverage --min=100   # Type coverage
./vendor/bin/pest --parallel                   # Parallel testing
./vendor/bin/pest --coverage --min=80          # Coverage report
./vendor/bin/pest --parallel --coverage --min=80  # Combined
```

### Pest vs PHPUnit Comparison

| Feature | PHPUnit | Pest |
|---------|---------|------|
| Syntax | Class-based | Closure-based |
| Architecture tests | No | Yes (built-in) |
| Type coverage | No | Yes (plugin) |
| Parallel testing | No (needs ParaTest) | Yes (built-in) |
| Assertions | `$this->assert*()` | `expect()->toBe*()` |
| Data providers | Static methods | `with()` chaining |
| Runs PHPUnit tests | N/A | Yes (fully compatible) |

## PHPUnit Patterns

### AAA Pattern (Arrange-Act-Assert)

```php
<?php declare(strict_types=1);

test('calculate order total with discount', function (): void {
    // Arrange
    $order = new Order(items: [
        new OrderItem(price: 100_00, quantity: 2),
        new OrderItem(price: 50_00, quantity: 1),
    ]);
    $discount = new PercentageDiscount(percent: 10);

    // Act
    $total = $order->calculateTotal(discount: $discount);

    // Assert
    expect($total)->toBe(225_00);
});
```

### Data Providers

```php
<?php declare(strict_types=1);

dataset('valid emails', [
    'standard' => ['user@example.com'],
    'with plus' => ['user+tag@example.com'],
    'subdomain' => ['user@sub.example.com'],
]);

dataset('invalid emails', [
    'no at sign' => ['userexample.com'],
    'no domain' => ['user@'],
    'empty'     => [''],
]);

test('validates email correctly', function (string $email): void {
    expect(isValidEmail($email))->toBeTrue();
})->with('valid emails');

test('rejects invalid email', function (string $email): void {
    expect(isValidEmail($email))->toBeFalse();
})->with('invalid emails');
```

### Mocking and Test Doubles

```php
<?php declare(strict_types=1);

test('sends notification on order completion', function (): void {
    $notifier = Mockery::mock(NotificationService::class);
    $notifier->shouldReceive('send')->once()->with(Mockery::type(OrderCompleted::class));

    $service = new OrderService(notifier: $notifier);
    $service->complete(orderId: 42);
});

test('exception on invalid order', function (): void {
    $service = new OrderService(notifier: Mockery::mock(NotificationService::class));

    expect(fn () => $service->complete(orderId: -1))
        ->toThrow(InvalidArgumentException::class, 'Order ID must be positive');
});
```

### Test Doubles Summary

| Type | Purpose | Example Use |
|------|---------|-------------|
| **Mock** | Verifies interactions (method calls) | Assert `send()` was called once |
| **Stub** | Returns predetermined responses | Return fake API response |
| **Spy** | Records calls for later assertion | Check call count after execution |
| **Fake** | Working simplified implementation | In-memory repository |

### Test Organization

```
tests/
├── Unit/              # Isolated, no I/O, fast
│   ├── Models/
│   └── Services/
├── Feature/           # HTTP tests, middleware, full stack
│   ├── Api/
│   └── Web/
├── Integration/       # Database, external services
│   └── Repositories/
├── Architecture/      # Pest arch tests
│   └── ArchTest.php
├── Pest.php           # Global test configuration
└── TestCase.php       # Base test case
```

## TDD Cycle

### Red-Green-Refactor

1. **Red:** Write a failing test that defines expected behavior
2. **Green:** Write the minimal code to make the test pass
3. **Refactor:** Clean up code while keeping tests green

```php
<?php declare(strict_types=1);

// Step 1 - RED: Test first (fails because class doesn't exist)
test('money can be added', function (): void {
    $a = Money::fromCents(100);
    $b = Money::fromCents(250);
    expect($a->add($b)->cents())->toBe(350);
});

// Step 2 - GREEN: Minimal implementation
final readonly class Money
{
    private function __construct(private int $cents) {}

    public static function fromCents(int $cents): self { return new self($cents); }

    public function add(self $other): self { return new self($this->cents + $other->cents); }

    public function cents(): int { return $this->cents; }
}
// Step 3 - REFACTOR: Add validation, formatting (tests stay green)
```

### When to Break the Cycle

- **Spike/prototype:** Exploring unknowns where you discard code after
- **Trivial code:** Simple getters, DTOs, value objects (test after)
- **Generated code:** Migrations, configs (validate via integration tests)

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: PHP Quality

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  quality:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        php: ['8.2', '8.3', '8.4']

    steps:
      - uses: actions/checkout@v4

      - name: Setup PHP
        uses: shivammathur/setup-php@v2
        with:
          php-version: ${{ matrix.php }}
          coverage: xdebug

      - name: Cache Composer dependencies
        uses: actions/cache@v4
        with:
          path: vendor
          key: composer-${{ matrix.php }}-${{ hashFiles('composer.lock') }}
          restore-keys: composer-${{ matrix.php }}-

      - name: Install dependencies
        run: composer install --no-interaction --prefer-dist

      - name: Code style (Pint)
        run: ./vendor/bin/pint --test

      - name: Static analysis (PHPStan)
        run: ./vendor/bin/phpstan analyse --memory-limit=3g

      - name: Tests (Pest)
        run: ./vendor/bin/pest --type-coverage --coverage --min=80
```

### Composer Scripts

```json
{
    "scripts": {
        "stan": ["./vendor/bin/phpstan analyse --memory-limit=3g"],
        "pint": ["./vendor/bin/pint"],
        "pint:check": ["./vendor/bin/pint --test"],
        "test": ["./vendor/bin/pest --type-coverage"],
        "test:coverage": ["./vendor/bin/pest --coverage --min=80"],
        "check": ["@stan", "@pint:check", "@test"]
    }
}
```

Run all checks before committing: `composer check`

### Pre-Commit Hooks (CaptainHook)

```bash
composer require --dev captainhook/captainhook
vendor/bin/captainhook install
```

```json
{
    "pre-commit": {
        "actions": [
            { "action": "composer pint:check", "conditions": [] },
            { "action": "composer stan", "conditions": [] },
            { "action": "composer test", "conditions": [] }
        ]
    }
}
```

## Rector (Automated Refactoring)

Rector automatically upgrades PHP code and removes dead code.

```bash
composer require --dev rector/rector
```

### rector.php Configuration

```php
<?php declare(strict_types=1);

use Rector\Config\RectorConfig;
use Rector\DeadCode\Rector\ClassMethod\RemoveUnusedPrivateMethodRector;
use Rector\DeadCode\Rector\Property\RemoveUnusedPrivatePropertyRector;
use Rector\Set\ValueObject\SetList;
use Rector\TypeDeclaration\Rector\ClassMethod\AddVoidReturnTypeWhereNoReturnRector;
use Rector\TypeDeclaration\Rector\ClassMethod\ReturnTypeFromStrictNativeCallRector;

return RectorConfig::configure()
    ->withPaths([__DIR__ . '/app', __DIR__ . '/src', __DIR__ . '/config', __DIR__ . '/database', __DIR__ . '/routes'])
    ->withSkip([__DIR__ . '/vendor', __DIR__ . '/storage'])
    ->withPhpSets(php82: true)
    ->withSets([SetList::DEAD_CODE, SetList::CODE_QUALITY, SetList::TYPE_DECLARATION])
    ->withRules([
        AddVoidReturnTypeWhereNoReturnRector::class,
        ReturnTypeFromStrictNativeCallRector::class,
        RemoveUnusedPrivateMethodRector::class,
        RemoveUnusedPrivatePropertyRector::class,
    ]);
```

### Running Rector

```bash
./vendor/bin/rector process --dry-run    # Preview changes
./vendor/bin/rector process              # Apply changes
./vendor/bin/rector process app/Services # Process specific path
```

### Rector + PHPStan Workflow

Run Rector first to auto-fix, then PHPStan to verify:

```bash
./vendor/bin/rector process && ./vendor/bin/phpstan analyse --memory-limit=3g
```

---

*Sources: Generating Efficient PHP (php[architect] 2023), PHP: The Right Way*
