# Security Patterns — Cross-Reference

This skill delegates all security patterns to the dedicated **php-security** skill.

## Where to Find Security Patterns

| Pattern | Location |
|---------|----------|
| Session hardening (SecureSession) | `php-security` skill + `php-security/references/security-code-patterns.md` |
| Input validation (InputValidator) | `php-security` skill + `php-security/references/security-code-patterns.md` |
| Output encoding (OutputEncoder) | `php-security` skill + `php-security/references/security-code-patterns.md` |
| CSRF protection (CsrfGuard) | `php-security` skill + `php-security/references/security-code-patterns.md` |
| File upload security (SecureUpload) | `php-security` skill + `php-security/references/security-code-patterns.md` |
| Password hashing (Argon2id) | `php-security` skill + `php-security/references/security-code-patterns.md` |
| Encryption (AES-256-GCM) | `php-security` skill + `php-security/references/security-code-patterns.md` |
| Error/exception handlers | `php-security` skill + `php-security/references/security-code-patterns.md` |
| php.ini hardening | `php-security/references/php-ini-security-checklist.md` |
| Session configuration | `php-security/references/session-hardening.md` |
| Input/output patterns | `php-security/references/input-output-security.md` |

## Quick Security Essentials

For inline security patterns, see the **Security (Essentials)** section in `SKILL.md`.

For comprehensive security implementation, load the **php-security** skill.

---

**Previously:** This file contained 1,108 lines of security code patterns that duplicated the `php-security` skill. Those patterns now live exclusively in `php-security/references/security-code-patterns.md`.
