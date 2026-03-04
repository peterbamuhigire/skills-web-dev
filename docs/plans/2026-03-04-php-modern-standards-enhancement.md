# PHP Modern Standards Enhancement Design

**Date:** 2026-03-04
**Sources:** Generating Efficient PHP (php[architect], 2023), PHP Security and Session Management (Dinwiddie, 2022)

## Problem

Existing `php-modern-standards` skill lacks:
- Deep performance/efficiency patterns (generators, OPcache, Fibers, memory optimization)
- Code quality tooling configuration (PHPStan, Pint, PestPHP)
- Testing patterns (PHPUnit data providers, mocking, TDD cycle)
- Built-in function benchmark rules (100x performance difference)

Additionally, `references/security-patterns.md` is 1,108 lines (2x over 500-line limit) and duplicates the `php-security` skill.

## Solution

### 1. Rewrite `SKILL.md` (~480 lines)

Enhanced with performance/efficiency content. Key additions:
- Generators deep dive (file, DB, socket patterns)
- Fibers vs Generators decision rule
- OPcache configuration essentials
- Built-in function performance rule
- Code quality tooling section (PHPStan, Pint, PestPHP)
- Testing section (AAA, data providers, mocking)
- Condensed security section → cross-reference to php-security skill

### 2. Replace `references/security-patterns.md` (1,108 → ~30 lines)

Slim cross-reference pointing to `php-security` skill.

### 3. Create `references/performance-efficiency.md` (~450 lines)

Generators, OPcache, memory optimization, profiling, Fibers, caching.

### 4. Create `references/code-quality-tooling.md` (~400 lines)

PHPStan, Pint/CS Fixer rules, PHPUnit, PestPHP, CI/CD, Composer scripts.

### 5. Keep existing `.php` example files unchanged

## Implementation Order

1. Rewrite `SKILL.md`
2. Replace `security-patterns.md` with cross-reference
3. Create `references/performance-efficiency.md`
4. Create `references/code-quality-tooling.md`
5. Update CLAUDE.md and README.md
6. Commit and push
