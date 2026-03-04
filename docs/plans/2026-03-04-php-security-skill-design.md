# PHP Security Skill + Enhancements Design

**Date:** 2026-03-04
**Source:** PHP Security and Session Management 2022 Guide (Ray Dinwiddie) + gap analysis of existing skills

## Problem

Existing skills cover PHP security partially:

- **vibe-security-skill**: OWASP Top 10 conceptual coverage, no PHP-specific implementation
- **php-modern-standards**: Basic input validation/XSS/CSRF, no session security
- **dual-auth-rbac**: Auth system, but no session hardening directives
- **api-error-handling**: Error formatting, no security error patterns

No dedicated PHP security skill exists.

## Solution

### 1. New Skill: `php-security/SKILL.md` (~450 lines)

Covers PHP-specific security patterns:

| Section | Topics |
|---------|--------|
| Session Security | php.ini hardening, hijacking prevention, fixation, regeneration, timeouts, cookie flags |
| Input Validation | filter_var(), type checking, whitelist validation, regex patterns |
| Output Encoding | htmlspecialchars() by context (HTML/JS/URL/CSS), strip_tags() |
| SQL Injection | PDO prepared statements, parameterized queries, whitelist column names |
| XSS Prevention | Reflected/stored/DOM, Content-Security-Policy headers |
| CSRF Protection | Token generation, validation, SameSite cookies, double-submit |
| File Upload Security | Magic byte validation, extension whitelist, storage outside webroot |
| PHP Vulnerabilities | Type juggling, object injection, deserialization, eval() |
| php.ini Hardening | Complete security checklist with recommended values |
| Error Handling | display_errors off, custom handlers, secure logging |
| Cryptography | random_bytes(), password_hash(Argon2id), openssl_encrypt() |

### 2. Reference Docs: `php-security/references/`

- `session-hardening.md` — All session php.ini directives with secure values
- `input-output-security.md` — Validation/encoding patterns by context
- `php-ini-security-checklist.md` — Full php.ini security audit

### 3. Enhance Existing Skills

**vibe-security-skill** — Add PHP session cross-ref, CSRF PHP patterns, file upload guidance
**php-modern-standards** — Add session management, error handling security, file upload validation
**dual-auth-rbac** — Add session fixation prevention, config hardening, cookie security

### 4. Update CLAUDE.md and README.md

Add php-security to repo structure and cross-references.

## Implementation Order

1. Create `php-security/SKILL.md`
2. Create `php-security/references/` docs (3 files)
3. Enhance `vibe-security-skill/SKILL.md`
4. Enhance `php-modern-standards/SKILL.md`
5. Enhance `dual-auth-rbac/SKILL.md`
6. Update `CLAUDE.md` and `README.md`
