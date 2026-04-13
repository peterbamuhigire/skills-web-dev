---
name: web-app-security-audit
description: Use when auditing a PHP/JavaScript/HTML web application for security
  vulnerabilities. Covers configuration, authentication, authorization, input validation,
  XSS, API security, HTTP headers, and dependency scanning. Produces a severity-rated
  audit...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Web Application Security Audit

<!-- dual-compat-start -->
## Use When

- Use when auditing a PHP/JavaScript/HTML web application for security vulnerabilities. Covers configuration, authentication, authorization, input validation, XSS, API security, HTTP headers, and dependency scanning. Produces a severity-rated audit...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `web-app-security-audit` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
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
<!-- dual-compat-end -->
Systematic security audit for PHP/JavaScript/HTML web applications. Scans 8 security layers, produces a structured report with severity-rated findings and actionable fix recommendations that Claude can apply.

**Core Principle:** Scan everything before fixing anything. Full picture first, then targeted remediation.

**Scope:** Web application code only (PHP, JS, HTML, CSS). For Android security and database security, use dedicated skills.

**Cross-references:** `php-security` (PHP patterns), `vibe-security-skill` (OWASP), `dual-auth-rbac` (auth), `api-error-handling` (API errors)

**See references/ for:** `audit-checklist-detailed.md`, `security-headers-reference.md`, `report-template.md`

## When to Use

- Before deploying a web application to production
- After implementing major features or modules
- Periodic security review (quarterly recommended)
- After discovering a vulnerability in one area (audit all areas)
- When onboarding a new project or inheriting a codebase

## Audit Workflow

### Phase 1: Discovery

Before scanning, understand the application:

```
1. Identify app structure:
   - Glob for entry points: public/*.php, api/*.php, index.php
   - Find config files: .env, config/*.php, php.ini, .htaccess
   - Map route definitions and middleware chain

2. Identify authentication flows:
   - Find login/logout/register endpoints
   - Identify session management (session_start, JWT)
   - Find password handling code

3. Identify data flows:
   - Find database queries (PDO, mysqli, raw SQL)
   - Find external API calls (curl, file_get_contents)
   - Find file upload handlers
   - Find output/rendering points (echo, print, templates)
```

### Phase 2: Scan (8 Layers)

Use parallel subagents for independent layers. Each layer produces findings with severity.

**Layer execution order:**
- Parallel batch 1: Configuration, HTTP Headers, Dependencies (no code dependencies)
- Parallel batch 2: Auth & Sessions, Authorization (auth-related)
- Parallel batch 3: Input Validation, Output & XSS, API Security (data flow)

### Phase 3: Report

Generate `docs/security-audit/YYYY-MM-DD-audit.md` using the report template.

## Severity Classification

| Severity | Criteria | Example |
|----------|----------|---------|
| CRITICAL | Exploitable now, data breach risk | SQL injection, hardcoded credentials, no auth on admin |
| HIGH | Exploitable with effort, significant impact | Missing session regeneration, weak password hashing |
| MEDIUM | Requires specific conditions to exploit | Missing CSRF on non-critical form, verbose errors |
| LOW | Minor security weakness, defense-in-depth | Missing security header, loose CORS |
| INFO | Best practice recommendation | Missing SRI on CDN, could add rate limiting |

## Layer 1: Configuration Audit

**Scan targets:** php.ini, .env, .htaccess, config files, deployment configs

**Critical checks:**

```
Grep patterns:
  display_errors\s*=\s*(On|1|true)     → CRITICAL: errors shown to users
  expose_php\s*=\s*(On|1|true)         → MEDIUM: PHP version disclosed
  allow_url_include\s*=\s*(On|1|true)  → CRITICAL: remote file inclusion

File checks:
  .env in webroot                       → CRITICAL: secrets accessible
  .env in .gitignore                    → Check: must be ignored
  phpinfo() calls                       → HIGH: full config exposed

Secret patterns:
  password\s*=\s*['"][^'"]+['"]         → HIGH: hardcoded password
  (api_key|secret|token)\s*=           → HIGH: check if in env or hardcoded
  DB_(PASSWORD|HOST|USER)               → Verify: in .env, not in code
```

**Fix reference:** php-security > php.ini Security Hardening, Error Handling

## Layer 2: Authentication & Sessions

**Scan targets:** Login/logout handlers, session configuration, password code

**Critical checks:**

```
Session security:
  session.use_strict_mode               → Must be 1
  session.cookie_httponly               → Must be 1
  session.use_only_cookies              → Must be 1
  session_regenerate_id after login     → CRITICAL if missing

Password handling:
  password_hash with PASSWORD_ARGON2ID  → Required
  password_verify usage                 → Required (not manual comparison)
  md5() or sha1() for passwords         → CRITICAL: weak hashing

Auth flow:
  Login rate limiting                   → HIGH if missing
  Account lockout mechanism             → MEDIUM if missing
  Session timeout enforcement           → HIGH if missing
  Complete session destruction on logout → MEDIUM if missing

Cryptographic practices:
  openssl_encrypt/decrypt usage           → MEDIUM: prefer Libsodium (sodium_*)
  Custom encryption (XOR, base64 "encryption") → CRITICAL: not encryption
  Hardcoded encryption keys in source     → CRITICAL: use env/vault
  random_int/random_bytes for tokens      → Required (not rand/mt_rand)
```

**Fix reference:** php-security > Session Security, Cryptographic Best Practices, dual-auth-rbac > Password Security

## Layer 3: Authorization & Access Control

**Scan targets:** Middleware, route guards, database queries, API endpoints

**Critical checks:**

```
IDOR (Insecure Direct Object Reference):
  Endpoints using $_GET['id'] without ownership check  → CRITICAL
  Queries without WHERE franchise_id = ?               → CRITICAL (multi-tenant)
  Sequential IDs exposed in URLs                       → MEDIUM

RBAC:
  Permission checks on protected routes                → HIGH if missing
  Super admin bypass properly implemented              → Check
  Cross-tenant data access prevention                  → CRITICAL if missing

Route protection:
  Admin routes without auth middleware                  → CRITICAL
  API endpoints without authentication                 → HIGH (if should be protected)
  File access without authorization                    → HIGH
```

**Fix reference:** vibe-security-skill > A01 Broken Access Control, dual-auth-rbac > RBAC

## Layer 4: Input Validation

**Scan targets:** All form handlers, API endpoints, file upload handlers

**Critical checks:**

```
Raw input usage:
  $_GET[   without filter_var/validation    → HIGH
  $_POST[  without filter_var/validation    → HIGH
  $_REQUEST[ usage                          → MEDIUM (ambiguous source)

SQL injection:
  String concatenation in SQL queries       → CRITICAL
  "SELECT.*\$_" pattern                    → CRITICAL
  "WHERE.*\$_" pattern                     → CRITICAL
  Non-parameterized queries                → CRITICAL

File uploads:
  No MIME type validation (finfo)           → HIGH
  No file size limit                        → MEDIUM
  Files stored in webroot                   → HIGH
  Original filename used for storage        → MEDIUM

Type validation:
  Integer inputs not validated              → MEDIUM
  Email inputs not validated                → LOW
  Enum values not whitelisted               → MEDIUM

PHP-specific vulnerabilities:
  == instead of === (type juggling)         → HIGH: "0e123"=="0e456" is true
  in_array() without strict 3rd param       → MEDIUM: type coercion
  unserialize() on user/external data       → CRITICAL: object injection/RCE
  eval() with any variable input            → CRITICAL: code execution
  exec/system/shell_exec/passthru           → CRITICAL: command injection
  preg_replace with /e modifier             → CRITICAL: code execution (PHP <7)
  include/require with user-controlled path → CRITICAL: file inclusion
  missing declare(strict_types=1)           → LOW: type safety gap
```

**Fix reference:** php-security > Input Validation, SQL Injection Prevention, File Upload Security, PHP-Specific Vulnerabilities

## Layer 5: Output Encoding & XSS

**Scan targets:** All output points (echo, print, templates), JavaScript embedding

**Critical checks:**

```
XSS vulnerabilities:
  echo $_GET  or echo $_POST              → CRITICAL
  echo $variable without htmlspecialchars  → HIGH (if user-sourced)
  printf with %s from user input           → HIGH

Template encoding:
  Missing ENT_QUOTES in htmlspecialchars   → MEDIUM
  Missing UTF-8 charset parameter          → LOW
  Raw output in JavaScript context         → HIGH

Content Security Policy:
  No CSP header set                        → MEDIUM
  CSP with 'unsafe-inline'                 → MEDIUM
  CSP with 'unsafe-eval'                   → HIGH
  No script-src directive                  → MEDIUM
```

**Fix reference:** php-security > Output Encoding, XSS Prevention

## Layer 6: API Security

**Scan targets:** REST API endpoints, AJAX handlers, form actions

**Critical checks:**

```
CSRF protection:
  State-changing endpoints without CSRF token → HIGH
  CSRF token not validated server-side        → CRITICAL
  Missing SameSite cookie attribute           → MEDIUM

Rate limiting:
  Login endpoint without rate limiting         → HIGH
  API endpoints without throttling             → MEDIUM
  Password reset without rate limiting         → HIGH

Error disclosure:
  Stack traces in API responses                → HIGH
  Database error messages exposed              → CRITICAL
  Internal file paths in errors                → MEDIUM

CORS:
  Access-Control-Allow-Origin: *               → HIGH
  Credentials with wildcard origin             → CRITICAL
  Missing CORS headers (if API)                → INFO

Webhook security:
  Webhook endpoints without signature verify   → CRITICAL
  No idempotency handling                      → MEDIUM
```

**Fix reference:** php-security > CSRF Protection, api-error-handling, vibe-security-skill > A02

## Layer 7: HTTP Security Headers

**Scan targets:** Response headers on all major endpoints

**Required headers checklist:**

```
Strict-Transport-Security: max-age=31536000; includeSubDomains  → HIGH if missing
Content-Security-Policy: [see CSP section]                       → MEDIUM if missing
X-Content-Type-Options: nosniff                                  → LOW if missing
X-Frame-Options: DENY (or SAMEORIGIN)                            → MEDIUM if missing
Referrer-Policy: strict-origin-when-cross-origin                 → LOW if missing
Cache-Control: no-store (on sensitive pages)                     → MEDIUM if missing
X-Powered-By: removed                                           → LOW if present
Server: version removed                                         → LOW if present
```

**Fix reference:** See references/security-headers-reference.md

## Layer 8: Dependencies & Supply Chain

**Scan targets:** composer.json, composer.lock, package.json, CDN scripts

**Critical checks:**

```
PHP dependencies:
  composer audit output                    → Severity from advisory
  Outdated packages (major versions)       → MEDIUM
  composer.lock committed                  → HIGH if missing

JavaScript:
  npm audit / yarn audit output            → Severity from advisory
  CDN scripts without SRI integrity attr   → MEDIUM
  Inline scripts from external sources     → HIGH

General:
  .env.example with real values            → HIGH
  Credentials in package configs           → CRITICAL
  Lock files in .gitignore                 → HIGH (should be committed)
```

**Fix reference:** vibe-security-skill > A03 Supply Chain

## Executing the Audit

### Step 1: Launch Discovery Subagent

```
Agent: Explore the codebase to identify:
- All PHP entry points (public/, api/, *.php in webroot)
- Configuration files (.env, config/, php.ini, .htaccess)
- Authentication code (login, session, JWT)
- Database query patterns (PDO, mysqli)
- Template/output files
- API endpoint definitions
- JavaScript files and CDN references
Return a structured map of the application.
```

### Step 2: Launch Parallel Scan Subagents

```
Batch 1 (independent):
  - Agent: Scan Layer 1 (Configuration)
  - Agent: Scan Layer 7 (HTTP Headers)
  - Agent: Scan Layer 8 (Dependencies)

Batch 2 (auth-dependent):
  - Agent: Scan Layer 2 (Auth & Sessions)
  - Agent: Scan Layer 3 (Authorization)

Batch 3 (data-flow):
  - Agent: Scan Layer 4 (Input Validation)
  - Agent: Scan Layer 5 (Output & XSS)
  - Agent: Scan Layer 6 (API Security)
```

### Step 3: Generate Report

Aggregate all findings into `docs/security-audit/YYYY-MM-DD-audit.md` using the report template. Sort by severity.

### Step 4: Fix Workflow

1. Present summary to user (counts by severity)
2. Work through CRITICAL findings first
3. For each finding: show location, explain risk, apply fix, verify
4. Move to HIGH, then MEDIUM, then LOW
5. Re-run affected layer checks after fixes
6. Update report with fix status

## Audit Subagent Prompt Template

For each layer, use this prompt structure:

```
You are auditing a web application for security vulnerabilities.

LAYER: [Layer Name]
SCOPE: [Files/patterns to scan]

For each finding, report:
- Severity: CRITICAL|HIGH|MEDIUM|LOW|INFO
- Location: file_path:line_number
- Finding: What the vulnerability is
- Impact: What an attacker could do
- Fix: Specific code change needed
- Reference: Which skill has the fix pattern

Scan these patterns:
[Layer-specific grep patterns]

Return findings as a structured list sorted by severity.
```

## Anti-Patterns

- Scanning only one layer and declaring the app secure
- Fixing issues before completing the full scan (lose context)
- Rating everything as CRITICAL (desensitizes the team)
- Ignoring INFO findings (they become vulnerabilities when combined)
- Auditing only new code without reviewing existing patterns
- Skipping the dependency audit (most common attack vector)

## Quick Start

When user invokes this skill:
1. Ask: "Which project directory should I audit?"
2. Run Discovery phase
3. Launch all 8 layer scans
4. Generate report
5. Ask: "Ready to start fixing? I'll begin with [N] CRITICAL findings."
