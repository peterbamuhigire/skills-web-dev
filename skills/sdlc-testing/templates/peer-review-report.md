# Peer Review / Inspection Report -- Template & Guide

**Back to:** [SDLC Testing Skill](../SKILL.md)

## Purpose

Documents **findings from code reviews, design inspections, and document reviews**. Standardizes the review process with tech-stack-specific checklists, finding classification, and continuous improvement tracking.

## Audience

Development team, QA leads, tech leads.

## When to Create

Throughout the SDLC -- per PR (code review), per phase gate (design/document review), and per security audit.

---

## Review Types

| Type | Trigger | Artifacts Reviewed | Typical Duration |
|------|---------|-------------------|-----------------|
| Code Review | PR created | Source code changes (PHP, Kotlin, SQL) | 15-60 min |
| Design Review | Phase gate G1 | SDD, database schema, API design | 1-2 hours |
| Document Review | Phase gate G0 | SRS, SDP, test plans, user manuals | 30-60 min |
| Security Review | Pre-release or on demand | Code, configs, infrastructure | 2-4 hours |

---

## Review Report Template

```markdown
# Peer Review Report

**Review ID:** REV-[TYPE]-[YYYY-MM-DD]-[###]
  (e.g., REV-CODE-2026-02-20-001)
**Review Type:** Code | Design | Document | Security
**Date:** YYYY-MM-DD
**Duration:** [HH:MM]

## Participants
| Role | Name |
|------|------|
| Author | [Name -- person who created the artifact] |
| Reviewer 1 | [Name] |
| Reviewer 2 | [Name] (required for merges to main) |
| Moderator | [Name] (optional, for formal inspections) |

## Artifact Under Review
| Item | Details |
|------|---------|
| PR / Document | [PR #NNN or document name] |
| Files changed | [List file paths or "see PR diff"] |
| Lines changed | [+NNN / -NNN] |
| Scope | [Brief description of what changed] |
| Excluded | [What was explicitly NOT reviewed and why] |

---

## Findings

### Finding Template

| Field | Value |
|-------|-------|
| Finding ID | F-[###] |
| Severity | Critical | Major | Minor | Suggestion |
| Category | Logic | Security | Performance | Style | Docs | Architecture |
| Location | [file:line or document:section] |
| Description | [Clear, specific, actionable description] |
| Recommendation | [What should be done to fix it] |
| Resolution | Open | Fixed | Won't Fix (with justification) |

### Severity Definitions

| Severity | Definition | Action Required |
|----------|-----------|----------------|
| Critical | Bug, security flaw, or data loss risk | Must fix before merge |
| Major | Significant logic error or design violation | Must fix before merge |
| Minor | Code quality issue, minor bug risk | Fix recommended, may defer |
| Suggestion | Improvement idea, alternative approach | Optional, author decides |

### Category Definitions

| Category | Examples |
|----------|---------|
| Logic | Incorrect calculation, wrong condition, off-by-one |
| Security | SQL injection, XSS, missing auth check, exposed secret |
| Performance | N+1 query, missing index, unnecessary loop |
| Style | Naming convention, formatting, dead code |
| Documentation | Missing docblock, incorrect comment, outdated README |
| Architecture | Layer violation, tight coupling, wrong pattern |

---

## Example Findings

### F-001 (Critical -- Security)
**Location:** `api/users.php:45`
**Description:** SQL query uses string concatenation instead of prepared statement.
**Code:**
```php
// FOUND:
$query = "SELECT * FROM users WHERE email = '$email'";
// SHOULD BE:
$stmt = $pdo->prepare("SELECT * FROM users WHERE email = ?");
$stmt->execute([$email]);
```
**Recommendation:** Use PDO prepared statement with parameter binding.
**Resolution:** Fixed in commit abc1234.

### F-002 (Major -- Architecture)
**Location:** `LoginViewModel.kt:23`
**Description:** ViewModel directly accesses Retrofit service, bypassing Repository layer.
**Recommendation:** Inject repository via Hilt. ViewModel should only interact with UseCase or Repository.
**Resolution:** Fixed -- LoginRepository injected via constructor.

### F-003 (Minor -- Style)
**Location:** `DashboardScreen.kt:78`
**Description:** Hardcoded color `Color(0xFF1E88E5)` instead of using theme.
**Recommendation:** Use `MaterialTheme.colorScheme.primary`.
**Resolution:** Fixed.

### F-004 (Suggestion)
**Location:** `InventoryService.php:112`
**Description:** Method `getProducts()` could use early return pattern for readability.
**Recommendation:** Refactor nested if-else to guard clauses.
**Resolution:** Won't Fix -- author prefers current structure, readability acceptable.
```

---

## Tech-Stack Review Checklists

### PHP Code Review Checklist

| # | Check | Pass |
|---|-------|------|
| 1 | `declare(strict_types=1);` present at top of file | [ ] |
| 2 | All SQL uses prepared statements (no string interpolation) | [ ] |
| 3 | All user input validated and sanitized server-side | [ ] |
| 4 | Output escaping applied (htmlspecialchars for HTML output) | [ ] |
| 5 | `franchise_id` present in every tenant-scoped query | [ ] |
| 6 | Error handling with try/catch (no uncaught exceptions) | [ ] |
| 7 | PSR-12 code style followed (naming, spacing, braces) | [ ] |
| 8 | Type hints on all parameters and return types | [ ] |
| 9 | No hardcoded credentials, paths, or config values | [ ] |
| 10 | `php -l` syntax check passes | [ ] |
| 11 | PHPUnit tests exist for new/changed business logic | [ ] |
| 12 | CSRF token required on all state-changing requests | [ ] |

### Kotlin/Android Code Review Checklist

| # | Check | Pass |
|---|-------|------|
| 1 | Clean Architecture layer separation (no cross-layer imports) | [ ] |
| 2 | StateFlow used in ViewModels (not mutableStateOf or LiveData) | [ ] |
| 3 | Dependencies injected via Hilt (no manual instantiation) | [ ] |
| 4 | Coroutines use viewModelScope (no GlobalScope) | [ ] |
| 5 | Compose: state hoisting applied (stateless composables) | [ ] |
| 6 | Compose: minimal recomposition (stable params, remember) | [ ] |
| 7 | No hardcoded strings (use strings.xml) | [ ] |
| 8 | No hardcoded colors/dimensions (use theme/dimens) | [ ] |
| 9 | EncryptedSharedPreferences for sensitive data | [ ] |
| 10 | Samsung Knox crash prevention on ESP init (try/catch) | [ ] |
| 11 | Null safety handled (no !! without justification) | [ ] |
| 12 | Unit tests for ViewModel and UseCase changes | [ ] |

### SQL / Database Review Checklist

| # | Check | Pass |
|---|-------|------|
| 1 | Character set: `utf8mb4_general_ci` collation | [ ] |
| 2 | Proper indexes (composite where needed, no redundant) | [ ] |
| 3 | No `SELECT *` queries (list specific columns) | [ ] |
| 4 | Migrations are idempotent (safe to run twice) | [ ] |
| 5 | Stored procedure naming: `sp_action_entity` | [ ] |
| 6 | Foreign keys with appropriate ON DELETE action | [ ] |
| 7 | `franchise_id` column present in tenant-scoped tables | [ ] |
| 8 | `created_at`, `updated_at` columns present | [ ] |
| 9 | No low-cardinality single-column indexes (e.g., boolean) | [ ] |
| 10 | EXPLAIN run on new complex queries | [ ] |

### Security Review Checklist

| # | Check | Pass |
|---|-------|------|
| 1 | No secrets in code (API keys, passwords, tokens) | [ ] |
| 2 | CSRF protection on all mutation endpoints | [ ] |
| 3 | Session regeneration on authentication state changes | [ ] |
| 4 | Audit logging for sensitive operations (login, data changes) | [ ] |
| 5 | Rate limiting on login and sensitive endpoints | [ ] |
| 6 | Error messages don't leak system internals | [ ] |
| 7 | File uploads validated (type, size, magic bytes) | [ ] |
| 8 | HTTPS enforced (HSTS header set) | [ ] |
| 9 | Content Security Policy (CSP) header configured | [ ] |
| 10 | JWT tokens have appropriate expiry and refresh mechanism | [ ] |

Reference: `vibe-security-skill` for comprehensive OWASP Top 10 mapping.

---

## Design Review Checklist

| # | Check | Pass |
|---|-------|------|
| 1 | Architecture adheres to chosen pattern (Clean Architecture / MVVM) | [ ] |
| 2 | Multi-tenant isolation complete (franchise_id in every table) | [ ] |
| 3 | Scalability considered (horizontal scaling path documented) | [ ] |
| 4 | Error handling strategy covers all layers | [ ] |
| 5 | API contract consistent (naming, response format, versioning) | [ ] |
| 6 | Database design follows normalization (3NF minimum) | [ ] |
| 7 | Authentication model documented (Session + JWT dual auth) | [ ] |
| 8 | RBAC permissions matrix defined for all roles | [ ] |
| 9 | Offline-first strategy for mobile (Room caching) | [ ] |
| 10 | Deployment path documented (dev -> staging -> prod) | [ ] |

---

## Review Metrics

Track these metrics to measure review effectiveness:

| Metric | Formula | Target |
|--------|---------|--------|
| Defect detection rate | Findings / hours reviewed | 2-5 findings/hour |
| Review velocity | Lines of code / hours reviewed | 200-400 LOC/hour |
| Finding severity distribution | % Critical+Major vs Minor+Suggestion | < 30% Critical+Major |
| Fix turnaround time | Time from finding to resolution | < 24 hours for PRs |
| Review coverage | PRs reviewed / total PRs | 100% |
| Escape rate | Defects found in testing that review should have caught | < 10% |

---

## Review Process

### How to Request a Review

1. Create PR with clear description and linked requirement IDs
2. Self-review using the appropriate checklist above
3. Assign reviewer(s) based on expertise and availability
4. Add "Ready for Review" label

### Reviewer Selection Criteria

| Code Area | Preferred Reviewer |
|-----------|-------------------|
| PHP backend / API | Senior backend developer |
| Kotlin/Android | Senior Android developer |
| Database changes | DBA or senior backend developer |
| Security-related | Tech Lead + security-aware developer |
| Architecture changes | Tech Lead (required) |

### Review Turnaround SLA

| Priority | SLA | Escalation |
|----------|-----|-----------|
| Hotfix PR | 2 hours | Ping reviewer directly |
| Standard PR | 24 hours | Reassign if no response |
| Document review | 48 hours | Reminder at 24 hours |

### Dispute Resolution

1. Reviewer and author discuss in PR comments
2. If unresolved, Tech Lead makes final decision
3. Document the decision rationale for team learning
4. Never block a PR over style preferences (Minor/Suggestion severity)

---

## Continuous Improvement

### Common Findings to Standards

When the same finding appears 3+ times across different reviews:

1. Add it to the appropriate coding standard or skill
2. Create a linting rule or CI check if automatable
3. Add it to team onboarding materials
4. Remove from manual review checklist once automated

### Recurring Issues to Automation

| Recurring Finding | Automation |
|-------------------|-----------|
| Missing `declare(strict_types=1)` | PHPCS rule |
| Hardcoded strings in Compose | Android Lint check |
| Missing franchise_id in queries | Custom PHPStan rule or code review bot |
| `SELECT *` usage | SQL linting or PHPStan rule |
| Missing type hints | PHPStan level 6+ enforcement |

### Review Retrospectives

Hold quarterly review retrospectives to evaluate:

- Are reviews finding real bugs (not just style nits)?
- Is the review turnaround time acceptable?
- Are authors self-reviewing before requesting review?
- Which checklist items could be automated?
- Is the team improving (fewer Critical/Major findings over time)?

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Rubber-stamp reviews | Reviews provide zero value | Require at least 1 finding documented per review |
| No checklist | Reviews are inconsistent, miss key areas | Use tech-stack checklists above |
| Personal attacks | Hostile review culture, team conflict | Review the code, not the person. Be constructive. |
| Nitpicking only | Major issues missed while debating spaces | Focus on Critical/Major first, style last |
| Mega-PRs (500+ lines) | Too much to review effectively | Break into smaller, focused PRs (< 300 lines) |
| No follow-up | Findings raised but never fixed | Track resolution status, block merge until fixed |
| Author skips self-review | Reviewer wastes time on obvious issues | Require self-review checklist before requesting |

## Quality Checklist

- [ ] Review ID follows naming convention REV-[TYPE]-[DATE]-[###]
- [ ] All participants listed with roles
- [ ] Artifact under review clearly identified (PR #, files, scope)
- [ ] Findings use consistent template (ID, severity, category, location)
- [ ] Severity definitions applied correctly
- [ ] Tech-stack-specific checklist used (PHP, Kotlin, SQL, Security)
- [ ] All Critical and Major findings have resolution status
- [ ] Review metrics tracked (detection rate, velocity, turnaround)
- [ ] Dispute resolution process documented
- [ ] Continuous improvement: recurring findings flagged for automation
- [ ] Document stays under 500 lines

---

**Back to:** [SDLC Testing Skill](../SKILL.md)
**Previous:** [Validation Test Report](validation-test-report.md)
**Related:** [android-tdd](../../android-tdd/SKILL.md) | [vibe-security-skill](../../vibe-security-skill/SKILL.md) | [php-modern-standards](../../php-modern-standards/SKILL.md)
