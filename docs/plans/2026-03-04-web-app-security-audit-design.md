# Web App Security Audit Skill Design

**Date:** 2026-03-04
**Sources:** Web Application Security 2nd Ed (Hoffman), WASEC (Nadalin), PHP Security (Dinwiddie)

## Problem

No systematic way for Claude to audit web application security across all layers. Existing skills provide patterns but no structured audit workflow.

## Solution

### New Skill: `web-app-security-audit/SKILL.md`

**Scope:** PHP, JavaScript, HTML web applications. NOT Android or database (separate skills).

**Workflow:** Discovery > Scan (8 layers) > Report > Fix

**8 Audit Layers:**

1. Configuration — php.ini, .env, .htaccess, debug mode, secrets
2. Auth & Sessions — Session hardening, passwords, auth flows
3. Authorization — RBAC, tenant isolation, IDOR, route guards
4. Input Validation — Forms, APIs, file uploads, raw input usage
5. Output & XSS — Template encoding, CSP, DOM injection
6. API Security — CSRF, rate limiting, error disclosure, CORS
7. HTTP Headers — HSTS, CSP, X-Frame-Options, Referrer-Policy
8. Dependencies — composer audit, CDN SRI, outdated packages

**Report:** `docs/security-audit/YYYY-MM-DD-audit.md` with severity-rated findings

### Reference Docs

- `references/audit-checklist-detailed.md` — Full checklist with grep patterns
- `references/security-headers-reference.md` — HTTP headers audit
- `references/report-template.md` — Report template

### Cross-Skill References

| Fix Category | Skill |
|-------------|-------|
| PHP security patterns | php-security |
| OWASP mapping | vibe-security-skill |
| Auth/session system | dual-auth-rbac |
| Code quality | php-modern-standards |
| Error handling | api-error-handling |

## Implementation Order

1. Create `web-app-security-audit/SKILL.md`
2. Create `references/audit-checklist-detailed.md`
3. Create `references/security-headers-reference.md`
4. Create `references/report-template.md`
5. Update CLAUDE.md with new skill entry
