---
name: code-safety-scanner
description: Scan any codebase for 14 critical safety issues across security vulnerabilities,
  server stability (500 errors), and payment misconfigurations. Use when auditing
  code before deployment, reviewing AI-generated code for production readiness, or...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Code Safety Scanner

<!-- dual-compat-start -->
## Use When

- Scan any codebase for 14 critical safety issues across security vulnerabilities, server stability (500 errors), and payment misconfigurations. Use when auditing code before deployment, reviewing AI-generated code for production readiness, or...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `code-safety-scanner` or would be better handled by a more specific companion skill.
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
Systematic 14-point safety scan for web applications. Covers security, stability, and payment safety across PHP, Node.js/JS/TS, and Python stacks.

## Two Modes

**Automated Scan** (default): Run all 14 checks, produce structured report.
**Checklist Mode**: Reference checks passively during code review. State which mode at start.

## Scan Procedure

### Step 1: Detect Stack

Identify the project's tech stack by checking for:

- `composer.json` / `*.php` = PHP
- `package.json` / `*.js` / `*.ts` = Node.js/JS/TS
- `requirements.txt` / `*.py` = Python
- Frontend files: `*.html`, `*.jsx`, `*.tsx`, `*.vue`, `*.svelte`

Load the appropriate scan patterns from references/ based on detected stack.

### Step 2: Run All 14 Checks

Execute checks in order. For each check, use Grep/Glob to find patterns, then analyze context to confirm true positives. Rate each finding:

| Severity | Meaning |
|----------|---------|
| CRITICAL | Exploitable now, data loss or unauthorized access possible |
| HIGH | Likely exploitable, requires specific conditions |
| MEDIUM | Defense-in-depth gap, not immediately exploitable |
| LOW | Best practice violation, minimal risk |
| PASS | No issues found for this check |

### Step 3: Generate Report

Use this exact format:

```markdown
# Code Safety Scan Report
**Project:** [name] | **Date:** [date] | **Stack:** [detected]

## Category A: Security Vulnerabilities

| # | Check | Severity | Findings |
|---|-------|----------|----------|
| 1 | Hardcoded API Keys | ... | ... |
| 2 | Inverted Auth Logic | ... | ... |
| 3 | Open Admin Endpoints | ... | ... |
| 4 | Missing Signup/Login Auth | ... | ... |
| 5 | Missing Row-Level Security | ... | ... |

## Category B: Server Stability (500 Error Risks)

| # | Check | Severity | Findings |
|---|-------|----------|----------|
| 6 | Unhandled Runtime Exceptions | ... | ... |
| 7 | Misconfigured Env Variables | ... | ... |
| 8 | Misconfigured File Paths | ... | ... |
| 9 | Database Connection Problems | ... | ... |
| 10 | Infinite Loops/Recursion | ... | ... |
| 11 | Memory Leaks | ... | ... |
| 12 | Concurrency Issues | ... | ... |
| 13 | Data Race Conditions | ... | ... |

## Category C: Payment Safety

| # | Check | Severity | Findings |
|---|-------|----------|----------|
| 14 | Duplicate Charge Risk | ... | ... |

## Summary
- **CRITICAL:** X | **HIGH:** X | **MEDIUM:** X | **LOW:** X | **PASS:** X
- **Top Priority Fixes:** [numbered list of most urgent items]
```

## The 14 Checks

### Category A: Security Vulnerabilities

**Check 1 - Hardcoded API Keys in Frontend**

Scan frontend files for exposed secrets: API keys, tokens, connection strings.

Grep patterns: `(sk_live|sk_test|pk_live|STRIPE|SUPABASE|apiKey|api_key|secret|token|password|firebase|AWS_)` in `*.js`, `*.ts`, `*.jsx`, `*.tsx`, `*.vue`, `*.svelte`, `*.html`, `*.env.local`

Red flags:

- Any `sk_live_`, `sk_test_` prefixed strings in client code
- Supabase `service_role` key in frontend (anon key is OK)
- Firebase config with database rules set to `true` for all
- `Authorization: Bearer` with hardcoded token values
- `.env` files committed to git (check `.gitignore`)

For detailed patterns per stack, see **references/security-scans.md**.
Remediation: Cross-ref **vibe-security-skill** (Section 4).

**Check 2 - Inverted Authentication Logic**

Scan auth middleware/guards for logic that accidentally inverts access control.

Look for:

- `if (!authenticated)` granting access instead of blocking
- `if (role !== 'admin')` allowing admin routes
- Middleware that calls `next()` in the rejection branch
- Auth checks that return `true` on failure
- `allowList` / `denyList` logic reversed

Read every auth middleware file fully. Trace the logic path for both authenticated and unauthenticated users.

For detailed patterns, see **references/security-scans.md**.
Remediation: Cross-ref **web-app-security-audit** (Layer 3).

**Check 3 - Open Admin Endpoints**

Scan for routes/endpoints with admin functionality that lack auth middleware.

Grep patterns: `(admin|dashboard|bulk|delete-all|manage|users/list|export-all|import|migrate|seed|reset)` in route files.

Check each matched route for:

- Missing auth middleware attachment
- Missing role/permission check
- Public accessibility (no session/token requirement)

Remediation: Cross-ref **web-app-security-audit** (Layer 3).

**Check 4 - Missing User Auth on Signup/Login**

Scan auth endpoints for missing verification and validation.

Check for:

- Email verification missing after signup
- No rate limiting on login/signup endpoints
- No CAPTCHA or bot protection
- Password stored without hashing (check for plaintext storage)
- No input validation on email/username fields
- Missing CSRF protection on auth forms
- No account lockout after failed attempts

Remediation: Cross-ref **vibe-security-skill** (Section 2).

**Check 5 - Missing Row-Level Security**

Scan database queries for missing tenant/user isolation.

Grep patterns: `(SELECT|UPDATE|DELETE|INSERT)` in query files, then check for:

- Queries without `WHERE user_id =` or `WHERE tenant_id =`
- Direct use of user-supplied IDs without ownership validation
- API endpoints that accept record IDs without verifying ownership
- Missing RLS policies (Supabase: check `alter table...enable row level security`)
- Bulk operations without scope filtering

For detailed ORM patterns, see **references/security-scans.md**.
Remediation: Cross-ref **vibe-security-skill** (Section 6).

### Category B: Server Stability (500 Error Risks)

For all detailed scan patterns per stack, see **references/stability-scans.md**.

**Check 6 - Unhandled Runtime Exceptions**

Scan for code paths that can throw without catch/error handling:

- JSON parsing without try-catch (`JSON.parse`, `json_decode`, `json.loads`)
- File operations without error handling
- External API calls without try-catch
- Missing global error handler / uncaught exception handler
- Null/undefined access on optional data (missing null checks)
- Type coercion errors (PHP loose comparisons, JS type juggling)

**Check 7 - Misconfigured Environment Variables**

Scan for env var usage without validation:

- `process.env.X` / `$_ENV['X']` / `os.environ['X']` used without fallback or validation
- Missing `.env.example` file documenting required variables
- No startup validation that required env vars are present
- Hardcoded fallback values that mask missing config (e.g., `|| 'localhost'`)
- Different env var names between code and `.env.example`

**Check 8 - Misconfigured File Paths**

Scan for fragile file path references:

- Hardcoded absolute paths (`/home/user/`, `C:\Users\`)
- Relative paths that assume CWD (`./uploads/`, `../config/`)
- Missing existence checks before file operations
- Path construction without `path.join` / `realpath` / `os.path.join`
- User-supplied paths without sanitization (path traversal risk)

**Check 9 - Database Connection Problems**

Scan for connection pool and lifecycle issues:

- Missing connection pooling (new connection per request)
- No connection limit configuration
- Missing connection error handling / retry logic
- Connections opened but never closed (missing `finally` / destructor)
- No connection timeout configured
- Multiple database connections created in loops

**Check 10 - Infinite Loops/Recursion**

Scan for unbounded iteration:

- `while(true)` / `while(1)` without break conditions
- Recursive functions without base case or depth limit
- Retry logic without max attempt cap
- Event listeners that trigger themselves
- `setInterval` without `clearInterval`
- Recursive database queries (e.g., tree traversal without depth limit)

**Check 11 - Memory Leaks**

Scan for resource accumulation patterns:

- Growing arrays/lists in long-running processes
- Event listeners added but never removed
- Cache without size limits or TTL
- Large file reads into memory without streaming
- Unclosed streams, cursors, or connections
- Global variable accumulation in request handlers

**Check 12 - Concurrency Issues**

Analyze for concurrent access problems:

- Shared mutable state across requests (global variables in web servers)
- File writes without locking
- Counter increments without atomic operations (`count++` in concurrent context)
- Session data modified by parallel requests
- Missing database transaction isolation

**Check 13 - Data Race Conditions**

Analyze for specific race condition patterns:

- Read-then-write without atomicity (check balance then deduct)
- TOCTOU (time-of-check-to-time-of-use) on file or DB operations
- Optimistic updates without version checking
- Missing `SELECT ... FOR UPDATE` on read-modify-write sequences
- Async operations sharing mutable variables

Cross-ref **mysql-best-practices** (references/transaction-locking.md) for DB-level fixes.

### Category C: Payment Safety

For detailed patterns, see **references/payment-scans.md**.

**Check 14 - Duplicate Charge Risk**

Scan payment flows for double-charge vulnerabilities:

- Missing idempotency key on payment API calls
- No client-side button disable after click
- No server-side deduplication (same amount + user + time window)
- Missing payment status check before creating new charge
- No webhook deduplication (processing same event twice)
- Stripe: missing `idempotency_key` parameter
- Missing database transaction around payment + order creation
- No loading/spinner state preventing resubmit

## Cross-Reference Skills

For deeper remediation guidance on Category A findings:

| Check | Skill | Section |
|-------|-------|---------|
| Hardcoded API Keys | vibe-security-skill | Section 4: Hardcoded secrets |
| Inverted Auth | web-app-security-audit | Layer 3: Authorization |
| Open Endpoints | web-app-security-audit | Layer 3: Access Control |
| Missing Auth | vibe-security-skill | Section 2: Authentication |
| Missing RLS | vibe-security-skill | Section 6: Row-Level Security |
| Race Conditions | mysql-best-practices | references/transaction-locking.md |

## Checklist Mode

When used passively during code review, check each file against relevant items:

- **Route files** -> Checks 2, 3, 4
- **Frontend files** -> Check 1
- **Database queries** -> Checks 5, 9, 12, 13
- **API handlers** -> Checks 6, 7, 8
- **Payment code** -> Check 14
- **Long-running processes** -> Checks 10, 11
- **Async/concurrent code** -> Checks 12, 13
