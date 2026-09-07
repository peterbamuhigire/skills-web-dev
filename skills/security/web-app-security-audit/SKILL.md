---
name: web-app-security-audit
description: Use when auditing a PHP/JavaScript/HTML web application for security vulnerabilities. Covers configuration, authentication, authorization, input validation, XSS, API security, HTTP headers, and dependency scanning. Produces a severity-rated audit...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Web Application Security Audit
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Use when auditing a PHP/JavaScript/HTML web application for security vulnerabilities. Covers configuration, authentication, authorization, input validation, XSS, API security, HTTP headers, and dependency scanning. Produces a severity-rated audit...

## Required Inputs

- Project context, constraints, and concrete problem; load `references` only as needed.
- Confirm desired deliverable: audit report, remediation plan, or targeted review.

## Workflow

- Read this `SKILL.md`, then load only the referenced deep-dive files needed for the task.
- Apply the ordered guidance and decision rules; do not cherry-pick snippets.
- State assumptions, risks, and follow-ups when they matter.

## Quality Standards

- Outputs are execution-oriented, concise, and aligned with repository engineering standards.
- Preserve project conventions unless this skill requires a stronger standard.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit and failure modes.
- Loading every reference by default instead of progressive disclosure.

## Outputs

- A concrete result fitting the task: audit report, remediation plan, or review findings.
- Explicit assumptions, tradeoffs, or unresolved gaps when context is incomplete.
- References, companion skills, or follow-ups when they materially improve execution.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Security | Web application audit report | Markdown doc covering config, auth, input validation, and session handling findings | `docs/security/web-audit-2026-04-16.md` |
| Security | Remediation plan | Markdown doc listing findings, owners, and due dates | `docs/security/web-remediation-2026-04-16.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Systematic security audit for PHP/JavaScript/HTML web applications. Scans 8 security layers, produces a structured report with severity-rated findings and actionable fix recommendations that Codex can apply.

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

```
1. App structure: entry points (public/*.php, api/*.php), config (.env, config/, php.ini, .htaccess), routes, middleware.
2. Auth flows: login/logout/register, sessions (session_start, JWT), password handling.
3. Data flows: DB queries (PDO, mysqli), external APIs (curl), uploads, output points (echo, templates).
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

## Layer 9: Network-Layer Security (Audit View)

The auditor is reviewing controls, not building them. Build/operate detail (UFW commands, iptables rate-limit, ModSecurity install, WireGuard setup, TLS lifecycle) lives in [references/network-security-layer.md](references/network-security-layer.md). Audit-focused detail with checklist and severities lives in [references/network-security-audit.md](references/network-security-audit.md).

Stack assumption: Debian/Ubuntu VPS, self-host preferred (Nginx + ModSecurity or Coraza + OWASP CRS), Vault for secrets and PKI, optional managed WAF (Cloudflare, AWS WAF). Out of scope: service mesh, DDoS deep-dive beyond WAF rate-limit basics.

### §N1 Host firewall

```
Inbound default policy not DROP/deny                → CRITICAL
SSH exposed without rate-limit                      → HIGH
Database/admin ports public (not VPN-only or lo)    → CRITICAL
No egress allow-list                                → MEDIUM (HIGH for regulated)
Live rules drift from declared rules in source ctrl → HIGH
```

Tool choice: ufw for simple single-host, nftables for new deployments, iptables only on legacy. Egress allow-list: mirrors, DNS, NTP, egress proxy or API gateway, metrics. Deny everything else to contain lateral movement.

### §N2 Web Application Firewall

```
No WAF in blocking mode at edge or reverse proxy    → HIGH
CRS version not pinned, no upgrade cadence          → MEDIUM
Blanket disables of whole rule categories           → HIGH (need compensating control)
False-positive log not reviewed in last 30 days     → MEDIUM
No rate-limit on auth and password-reset endpoints  → HIGH
```

Managed (AWS WAF, Cloudflare) vs self-hosted (ModSecurity or Coraza + OWASP CRS) matrix in the reference. CRS tuning: paranoia level 1 in detection-only, replay traffic, write targeted exclusions per URI/parameter (never blanket disables), promote to blocking once false positives are under threshold, re-tune each CRS release. Prefer Coraza for new self-hosted deployments; ModSecurity v3 still supported on existing Nginx.

### §N3 Zero-trust architecture (NIST SP 800-207)

```
Internal service-to-service traffic in plaintext    → HIGH
Long-lived service credentials in env files         → HIGH
Internal apps reachable on LAN with no identity check → CRITICAL
"VPN means trusted" assumption documented anywhere  → HIGH
No device-posture signal in IdP                     → MEDIUM
```

Core idea (NIST SP 800-207, August 2020): no implicit trust based on physical or network location, or asset ownership; authn and authz are discrete functions performed before every session. Concrete controls: mTLS service-to-service, identity-aware proxies (Cloudflare Access, Pomerium, Tailscale serve), short-lived workload identities via SPIFFE/SPIRE, WireGuard for the management plane. Seven foundational tenets are in §2.1 of the PDF; quote directly when writing findings.

### §N4 VPN and remote access

```
Static long-lived WireGuard peer keys, no rotation  → HIGH
No mapping from peer key to human identity          → HIGH
Shared admin VPN key used by multiple operators     → CRITICAL
SSH password auth still permitted on bastion        → HIGH
Bastion without session recording                   → MEDIUM
VPN audit log retention < 1 year (or contractual)   → MEDIUM/HIGH
```

WireGuard is the recommended default. Key distribution is explicitly out of scope of WireGuard itself — solve via Vault PKI (short-lived peer keys) or Ansible (rotated `[Peer]` blocks). Every session must map to a human identity, via an identity-aware proxy or by correlating handshake events with the IdP in the SIEM.

### §N5 Auditor evidence checklist

Verify, with evidence: default-deny inbound on every public host (rule export attached); egress filter present with allow-list in source control; WAF in blocking mode at edge OR ModSecurity/Coraza + CRS at reverse proxy with CRS pinned and upgrade cadence documented; WAF false-positive log reviewed in last 30 days; mTLS between any two services crossing a host boundary OR explicit accepted-risk record; all ops access via identity-aware proxy or session-logged bastion; WireGuard peer keys rotate at least quarterly OR are short-lived from PKI; VPN audit log retention at least one year (or contractual minimum). Full reference, severity rubric, and citations: `references/network-security-audit.md`.

## Quick Start

When user invokes this skill:
1. Ask: "Which project directory should I audit?"
2. Run Discovery phase
3. Launch all 8 layer scans
4. Generate report
5. Ask: "Ready to start fixing? I'll begin with [N] CRITICAL findings."
## Degraded mode

Fallback without execution or a runnable environment: complete static review, mark dynamic checks unverified, and provide exact reproduction steps.

## Decision rules

| Finding | Release decision | Evidence required |
|---|---|---|
| Auth bypass, injection, cross-tenant access, secret, or exploitable XSS | block | Reproduction and passing remediation test |
| High-risk dependency or configuration exposure | block or documented exception | Version/configuration proof |
| Defence-in-depth gap without exploit path | conditional | Owner and remediation date |
