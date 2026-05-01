# PHP Development Tools Setup and Usage

Complete guide for setting up and using PHP development tools in SaaS projects.

## Overview

Every PHP project should have these development tools installed:

- **PHPStan** - Static analysis (level 8+)
- **PHP CS Fixer** - PSR-12 code formatting
- **PHPUnit** or **Pest** - Testing framework
- **Psalm** - Optional alternative static analysis

## Installation

### Check Existing Tools

```bash
# Check if tools are already installed
composer show | grep -E "(phpstan|phpunit|pest|php-cs-fixer)"
```

### Install PHPStan (Static Analysis)

```bash
composer require --dev phpstan/phpstan
```

**Create `phpstan.neon` configuration:**

```neon
parameters:
    level: 8
    paths:
        - src
        - public
    excludePaths:
        - vendor
        - tests
    checkMissingIterableValueType: false
```

**Verify installation:**

```bash
vendor/bin/phpstan --version
```

### Install PHP CS Fixer (Code Formatting)

```bash
composer require --dev friendsofphp/php-cs-fixer
```

**Create `.php-cs-fixer.php` configuration:**

```php
<?php

$finder = PhpCsFixer\Finder::create()
    ->in(__DIR__)
    ->exclude('vendor')
    ->exclude('node_modules')
    ->name('*.php')
    ->notName('*.blade.php');

return (new PhpCsFixer\Config())
    ->setRules([
        '@PSR12' => true,
        'strict_param' => true,
        'array_syntax' => ['syntax' => 'short'],
        'ordered_imports' => ['sort_algorithm' => 'alpha'],
        'no_unused_imports' => true,
        'single_quote' => true,
        'trailing_comma_in_multiline' => true,
    ])
    ->setFinder($finder);
```

**Verify installation:**

```bash
vendor/bin/php-cs-fixer --version
```

### Install Testing Framework

**Option 1: PHPUnit (Traditional)**

```bash
composer require --dev phpunit/phpunit
```

**Create `phpunit.xml` configuration:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<phpunit xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:noNamespaceSchemaLocation="vendor/phpunit/phpunit/phpunit.xsd"
         bootstrap="vendor/autoload.php"
         colors="true"
         executionOrder="depends,defects"
         failOnWarning="true"
         failOnRisky="true"
         beStrictAboutOutputDuringTests="true">
    <testsuites>
        <testsuite name="Unit">
            <directory suffix="Test.php">tests/Unit</directory>
        </testsuite>
        <testsuite name="Feature">
            <directory suffix="Test.php">tests/Feature</directory>
        </testsuite>
    </testsuites>
    <coverage processUncoveredFiles="true">
        <include>
            <directory suffix=".php">src</directory>
        </include>
    </coverage>
</phpunit>
```

**Option 2: Pest (Modern - Recommended)**

```bash
composer require --dev pestphp/pest --with-all-dependencies

# For Laravel projects
composer require --dev pestphp/pest-plugin-laravel
```

**Create `tests/Pest.php` bootstrap:**

```php
<?php

uses()->in(__DIR__);

// Custom helpers
function createUser(array $attributes = []): User
{
    // Helper implementation
}
```

**Verify installation:**

```bash
vendor/bin/phpunit --version  # or
vendor/bin/pest --version
```

### Optional: Install Psalm

```bash
composer require --dev vimeo/psalm

# Initialize configuration
vendor/bin/psalm --init
```

## Composer Scripts Setup

Add these scripts to `composer.json` for convenience:

```json
{
    "scripts": {
        "test": "pest",
        "test:unit": "pest --testsuite=Unit",
        "test:feature": "pest --testsuite=Feature",
        "test:coverage": "pest --coverage --min=80",
        "stan": "phpstan analyse --memory-limit=2G",
        "cs-fix": "php-cs-fixer fix",
        "cs-check": "php-cs-fixer fix --dry-run --diff",
        "quality": [
            "@cs-check",
            "@stan",
            "@test"
        ],
        "quality-fix": [
            "@cs-fix",
            "@stan",
            "@test"
        ]
    },
    "scripts-descriptions": {
        "test": "Run all tests",
        "test:unit": "Run unit tests only",
        "test:feature": "Run feature tests only",
        "test:coverage": "Run tests with coverage report",
        "stan": "Run static analysis",
        "cs-fix": "Fix code style issues",
        "cs-check": "Check code style without fixing",
        "quality": "Run all quality checks",
        "quality-fix": "Fix code style and run quality checks"
    }
}
```

## Usage Guide

### PHPStan - Static Analysis

**What it does:**
- Catches bugs without running code
- Finds type mismatches
- Detects undefined variables/properties
- Identifies dead code
- Prevents null pointer exceptions

**Basic usage:**

```bash
# Analyze entire project
composer stan

# Analyze specific directory
vendor/bin/phpstan analyse src/Auth --level 8

# Analyze with more memory
vendor/bin/phpstan analyse --memory-limit=2G

# Generate baseline (ignore existing errors)
vendor/bin/phpstan analyse --generate-baseline
```

**Common issues PHPStan catches:**

```php
// Type mismatch
function getUserId(): int
{
    return $_SESSION['user_id']; // Warning: might be string
}

// Correct
function getUserId(): int
{
    return (int) $_SESSION['user_id'];
}

// Undefined property
echo $user->nonExistentProperty; // Error

// Potential null pointer
$user = findUser($id);
echo $user->name; // Warning: $user might be null

// Correct
$user = findUser($id);
if ($user !== null) {
    echo $user->name;
}
```

**PHPStan Levels:**

- **Level 0-3**: Basic checks
- **Level 4-6**: Stricter type checking
- **Level 7**: Very strict
- **Level 8**: Maximum strictness (recommended)
- **Level 9**: Bleeding edge rules

### PHP CS Fixer - Code Formatting

**What it does:**
- Formats code to PSR-12 standard
- Fixes indentation and spacing
- Organizes imports
- Adds trailing commas
- Standardizes quotes

**Basic usage:**

```bash
# Check formatting (dry-run)
composer cs-check

# Fix formatting automatically
composer cs-fix

# Fix specific directory
vendor/bin/php-cs-fixer fix src/

# Fix with diff preview
vendor/bin/php-cs-fixer fix --dry-run --diff
```

**What gets fixed automatically:**

```php
// Before
<?php
namespace App\Services;
use App\Models\User;
use Exception;
use DateTime;

class UserService {
    private $users;

    function getUserById($id) {
        return $this->users[$id];
    }
}

// After
<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\User;
use DateTime;
use Exception;

final class UserService
{
    private array $users;

    public function getUserById(int $id): ?User
    {
        return $this->users[$id] ?? null;
    }
}
```

### Testing with PHPUnit/Pest

**What to test:**

✅ **Critical functionality:**
- Authentication and authorization
- Franchise isolation (franchise_id filtering)
- Permission checks
- Password hashing/verification
- Session management
- Input validation
- Business logic

❌ **Don't test:**
- Framework code
- Third-party libraries
- Simple getters/setters
- Database queries (use integration tests)

**PHPUnit example:**

```php
<?php

namespace Tests\Unit;

use PHPUnit\Framework\TestCase;
use App\Auth\PasswordHasher;

final class PasswordHasherTest extends TestCase
{
    public function test_password_can_be_hashed(): void
    {
        $hasher = new PasswordHasher();
        $password = 'SecurePassword123!';

        $hash = $hasher->hash($password);

        $this->assertNotEquals($password, $hash);
        $this->assertTrue($hasher->verify($password, $hash));
    }

    public function test_invalid_password_fails_verification(): void
    {
        $hasher = new PasswordHasher();
        $hash = $hasher->hash('correct');

        $this->assertFalse($hasher->verify('wrong', $hash));
    }
}
```

**Pest example (same test, cleaner syntax):**

```php
<?php

use App\Auth\PasswordHasher;

it('can hash a password', function () {
    $hasher = new PasswordHasher();
    $password = 'SecurePassword123!';

    $hash = $hasher->hash($password);

    expect($hash)->not->toBe($password);
    expect($hasher->verify($password, $hash))->toBeTrue();
});

it('fails verification with invalid password', function () {
    $hasher = new PasswordHasher();
    $hash = $hasher->hash('correct');

    expect($hasher->verify('wrong', $hash))->toBeFalse();
});
```

**Run tests:**

```bash
# Run all tests
composer test

# Run specific test file
vendor/bin/pest tests/Unit/PasswordHasherTest.php

# Run tests with coverage
vendor/bin/pest --coverage

# Run tests with minimum coverage requirement
vendor/bin/pest --coverage --min=80

# Run only unit tests
composer test:unit

# Run only feature tests
composer test:feature
```

## Pre-Commit Workflow

**ALWAYS run these checks before committing:**

```bash
# 1. Format code
composer cs-fix

# 2. Run static analysis
composer stan

# 3. Run tests
composer test

# 4. Review changes
git diff

# 5. Commit
git commit -m "feat: add user authentication"
```

**Or run all at once:**

```bash
composer quality-fix && git add . && git commit -m "feat: description"
```

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/quality.yml`:

```yaml
name: Quality Checks

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  quality:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup PHP
        uses: shivammathur/setup-php@v2
        with:
          php-version: '8.2'
          extensions: mbstring, pdo, pdo_mysql
          coverage: xdebug

      - name: Install dependencies
        run: composer install --prefer-dist --no-progress

      - name: Check code style
        run: composer cs-check

      - name: Run static analysis
        run: composer stan

      - name: Run tests
        run: composer test

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

### GitLab CI

Create `.gitlab-ci.yml`:

```yaml
image: php:8.2

stages:
  - test

before_script:
  - apt-get update -yqq
  - apt-get install -yqq git libzip-dev
  - docker-php-ext-install zip
  - curl -sS https://getcomposer.org/installer | php
  - php composer.phar install

quality:
  stage: test
  script:
    - php composer.phar cs-check
    - php composer.phar stan
    - php composer.phar test
```

## IDE Integration

### VS Code

Install extensions:
- **PHPStan** - `swordev.phpstan`
- **PHP CS Fixer** - `junstyle.php-cs-fixer`
- **PHPUnit Test Explorer** - `recca0120.vscode-phpunit`

**Settings (`.vscode/settings.json`):**

```json
{
    "php-cs-fixer.executablePath": "${workspaceFolder}/vendor/bin/php-cs-fixer",
    "php-cs-fixer.onsave": true,
    "phpstan.path": "${workspaceFolder}/vendor/bin/phpstan",
    "phpstan.enableStatusBar": true,
    "phpunit.php": "php",
    "phpunit.phpunit": "${workspaceFolder}/vendor/bin/phpunit"
}
```

### PhpStorm

1. **PHPStan:**
   - Go to: Settings → PHP → Quality Tools → PHPStan
   - Configuration file: `phpstan.neon`
   - Enable: "Run PHPStan on changed files"

2. **PHP CS Fixer:**
   - Go to: Settings → PHP → Quality Tools → PHP CS Fixer
   - Configuration file: `.php-cs-fixer.php`
   - Enable: "Run on save"

3. **PHPUnit/Pest:**
   - Go to: Settings → PHP → Test Frameworks
   - Add: PHPUnit by Composer Autoloader
   - Path: `vendor/autoload.php`

## Troubleshooting

### PHPStan Out of Memory

```bash
# Increase memory limit
vendor/bin/phpstan analyse --memory-limit=4G

# Or set in phpstan.neon
parameters:
    tmpDir: var/cache/phpstan
```

### PHP CS Fixer Conflicts

```bash
# Clear cache
vendor/bin/php-cs-fixer fix --clear-cache

# Check specific file
vendor/bin/php-cs-fixer fix src/Auth/Auth.php --dry-run --diff
```

### Tests Not Running

```bash
# Clear cache
vendor/bin/pest --clear-cache

# Check configuration
vendor/bin/pest --init
```

## Best Practices

### PHPStan

✅ **DO:**
- Start at level 0 and gradually increase
- Use baseline for existing codebases
- Fix errors before committing
- Add type hints everywhere

❌ **DON'T:**
- Ignore errors with `@phpstan-ignore-next-line` unless necessary
- Lower the level to make errors go away
- Commit code with PHPStan errors

### PHP CS Fixer

✅ **DO:**
- Run before every commit
- Use in CI/CD pipelines
- Customize rules per project
- Auto-fix on save (IDE)

❌ **DON'T:**
- Manually format code
- Commit unformatted code
- Skip formatting checks

### Testing

✅ **DO:**
- Write tests for critical paths
- Test edge cases and error conditions
- Aim for 80%+ coverage on business logic
- Use descriptive test names
- Keep tests fast and isolated

❌ **DON'T:**
- Test framework code
- Skip tests to "save time"
- Write flaky tests
- Test implementation details

## Summary Checklist

**Initial Setup:**
- [ ] Install PHPStan
- [ ] Install PHP CS Fixer
- [ ] Install PHPUnit or Pest
- [ ] Create configuration files
- [ ] Add composer scripts
- [ ] Configure IDE integration

**Before Every Commit:**
- [ ] Run `composer cs-fix`
- [ ] Run `composer stan`
- [ ] Run `composer test`
- [ ] Review changes

**CI/CD:**
- [ ] Add GitHub Actions or GitLab CI
- [ ] Run quality checks on every push
- [ ] Block merges if checks fail
- [ ] Track code coverage

**Ongoing:**
- [ ] Write tests for new features
- [ ] Maintain 80%+ code coverage
- [ ] Fix PHPStan errors immediately
- [ ] Keep dependencies updated
