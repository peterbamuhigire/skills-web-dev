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
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | PHP test plan | Markdown doc per `skill-composition-standards/references/test-plan-template.md` covering unit, integration, and contract tests | `docs/php/test-plan-checkout.md` |
| Operability | PHP-FPM operations note | Markdown doc covering opcache, request lifecycle, and OPcache reset procedure | `docs/php/fpm-ops-note.md` |

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

## Additional Guidance

Extended guidance for `php-modern-standards` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

### PHP DevOps Runtime Discipline

When PHP work affects deployment or production operations, pair this skill with `deployment-release-engineering` and apply the PHP delivery notes in `../deployment-release-engineering/references/devops-book-patterns.md`:

- keep Composer lockfiles and dependency installation reproducible;
- run static analysis, coding standards, and tests in CI before packaging;
- manage `.env` and secrets outside version control;
- document PHP-FPM pool settings, OPcache reset or warm-up, queue worker restart, cache clear/warm, and file-permission steps;
- include database migration order, backup, verification queries, and rollback or compensating actions;
- verify server updates, unattended security updates, web server config, and backup/restore for uploaded files.

Use that deep dive for:
- `Type System`
- `Modern Features`
- `Performance`
- `SOLID Principles`
- `Control Flow`
- `Security (Essentials)`
- `Testing`
- `Laravel Conventions`
- `Code Quality Tooling`
- `PSR Standards`
- `Anti-Patterns`
- `Checklist`
