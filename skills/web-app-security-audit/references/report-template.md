# Security Audit Report Template

Template for generating audit reports. Claude fills in findings from the 8-layer scan.

**Parent skill:** web-app-security-audit

## Template

Use this structure for every audit report. Save to `docs/security-audit/YYYY-MM-DD-audit.md`.

---

```markdown
# Security Audit Report

**Project:** [Project Name]
**Date:** [YYYY-MM-DD]
**Auditor:** Claude + [User Name]
**Scope:** Web application (PHP, JavaScript, HTML)

## Executive Summary

[2-3 sentence overview: what was audited, key findings, overall security posture]

## Findings Summary

| Severity | Count | Fixed | Remaining |
|----------|-------|-------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 0 | 0 | 0 |
| INFO | 0 | 0 | 0 |

## Findings by Layer

### Layer 1: Configuration

#### [SEVERITY] Finding Title

- **Location:** `path/to/file.php:line`
- **Finding:** Description of the vulnerability
- **Impact:** What an attacker could exploit
- **Fix:** Specific remediation steps
- **Reference:** [skill-name] > [section]
- **Status:** Open | Fixed | Accepted Risk

---

### Layer 2: Authentication & Sessions

[Same format per finding]

### Layer 3: Authorization & Access Control

[Same format per finding]

### Layer 4: Input Validation

[Same format per finding]

### Layer 5: Output Encoding & XSS

[Same format per finding]

### Layer 6: API Security

[Same format per finding]

### Layer 7: HTTP Security Headers

[Same format per finding]

### Layer 8: Dependencies & Supply Chain

[Same format per finding]

## Recommendations Priority

### Immediate (CRITICAL)

1. [Finding title] -- [one-line fix description]

### Short-term (HIGH)

1. [Finding title] -- [one-line fix description]

### Medium-term (MEDIUM)

1. [Finding title] -- [one-line fix description]

### Long-term (LOW/INFO)

1. [Finding title] -- [one-line fix description]

## Audit Metadata

- **Files scanned:** [count]
- **Entry points identified:** [count]
- **Config files reviewed:** [count]
- **Dependencies checked:** [count]
- **Duration:** [time]
- **Skills referenced:** php-security, vibe-security-skill, dual-auth-rbac, api-error-handling
```

---

## Usage Notes

- Fill `Status` as findings are addressed: `Open` > `Fixed` > verified
- Update the summary table counts after each fix session
- Keep report as living document until all CRITICAL and HIGH items are Fixed
- Archive completed reports in `docs/security-audit/archive/`
