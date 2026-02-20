# Quality Assurance Plan — Template & Guide

**Back to:** [SDLC Planning Skill](../SKILL.md)

## Purpose

Defines the **processes, standards, and metrics** to ensure the software meets quality requirements. Covers testing strategy, code review, static analysis, performance, security, accessibility, and defect management.

## Audience

QA team, developers, project managers, technical leads.

## When to Create

After the SDP and SRS are drafted. The QA Plan operationalizes quality requirements from the SRS.

---

## Template

```markdown
# [Project Name] — Quality Assurance Plan

**Version:** 1.0
**Date:** YYYY-MM-DD
**Author:** [Name]
**Status:** Draft | Under Review | Approved
**References:** [Link to SRS], [Link to SDP], [Link to Risk Plan]

---

## 1. Quality Objectives & Standards

### 1.1 Quality Objectives
- Deliver software that meets all functional requirements in the SRS
- Achieve defined performance, security, and usability targets
- Minimize defects reaching production (target: < 2 critical defects per release)
- Maintain code quality through automated checks and peer review
- Ensure multi-tenant data isolation is verifiable and verified

### 1.2 Standards & References
| Standard | Application |
|----------|------------|
| PSR-12 | PHP coding style |
| Material 3 Design Guidelines | Android UI/UX |
| WCAG 2.1 AA | Web accessibility |
| OWASP Top 10 | Security baseline |
| `vibe-security-skill` | Security quality gates (mandatory) |
| `mysql-best-practices` skill | Database quality standards |

## 2. QA Roles & Responsibilities

| Role | Responsibilities |
|------|-----------------|
| QA Lead | Test planning, defect triage, quality metrics reporting |
| QA Engineer | Test case design, execution, regression testing |
| Developer | Unit testing (TDD), code review participation, bug fixes |
| Tech Lead | Code review approval, architecture quality, security review |
| PM | Defect prioritization, release quality sign-off |

## 3. Quality Metrics & Targets

| Metric | Target | Measurement | Frequency |
|--------|--------|-------------|-----------|
| Unit Test Coverage | >= 80% (backend), >= 70% (Android) | Coverage tools | Per PR |
| Defect Density | < 5 defects per KLOC | Defect tracker | Per release |
| Critical Defects in Prod | < 2 per release | Production incident log | Per release |
| Code Review Turnaround | < 24 hours | PR metrics | Weekly |
| Build Success Rate | >= 95% | CI/CD dashboard | Weekly |
| Test Pass Rate | >= 98% before release | Test execution report | Per sprint |
| API Response Time (p95) | < 500ms | APM monitoring | Continuous |
| Web Page Load Time | < 2 seconds | Lighthouse/PageSpeed | Per release |
| Android Cold Start | < 3 seconds | Android Profiler | Per release |
| MTTR (Mean Time to Resolve) | < 4 hours (critical) | Incident log | Monthly |

## 4. Testing Strategy Overview

### 4.1 Test Pyramid

| Level | Proportion | Scope | Tools |
|-------|-----------|-------|-------|
| Unit Tests | 60% | Individual functions, classes | PHPUnit, JUnit 5 + MockK |
| Integration Tests | 25% | Module interactions, API + DB | PHPUnit, MockWebServer + Room |
| System Tests | 10% | End-to-end workflows | Selenium/Cypress, Compose UI Tests |
| Exploratory/Manual | 5% | UX, edge cases, usability | Manual testing checklists |

### 4.2 Test Types

| Test Type | Purpose | When Run |
|-----------|---------|----------|
| Unit | Verify individual logic | Every commit (TDD) |
| Integration | Verify module interactions | Every PR |
| API | Verify endpoint contracts | Every PR |
| UI (Web) | Verify web interface | Per sprint |
| UI (Android) | Verify Compose screens | Per sprint |
| Regression | Verify no regressions | Before each release |
| Performance | Verify speed/load targets | Before each release |
| Security | Verify security controls | Before each release |
| Multi-Tenant Isolation | Verify franchise_id filtering | Before each release |
| Accessibility | Verify WCAG compliance | Before each release |

### 4.3 Testing by Platform

**PHP Backend:**
- PHPUnit for unit and integration tests
- `php -l` syntax check on every changed file
- API testing via curl/Postman/automated scripts
- Database migration testing on staging before production

**Android:**
- JUnit 5 + MockK for unit tests (ViewModel, UseCase, Repository)
- Turbine for Flow testing
- Compose UI Testing for screen tests
- MockWebServer for API integration tests
- Room in-memory database for persistence tests

**Web UI:**
- Manual testing with checklists (primary)
- Browser DevTools for performance and accessibility
- Cross-browser testing (Chrome, Firefox, Safari, Edge)

**Reference:** `sdlc-testing` skill (future) for detailed test cases and execution plans.

## 5. Code Review Process

### 5.1 Review Requirements

| Target Branch | Reviewers Required | Review Focus |
|--------------|-------------------|-------------|
| `develop` | 1 reviewer | Logic correctness, standards, tests |
| `main` | 2 reviewers | Above + security, performance, tenant isolation |

### 5.2 Review Checklist

**Functionality:**
- [ ] Code implements the requirement correctly
- [ ] Edge cases handled
- [ ] Error handling is appropriate

**Quality:**
- [ ] Follows coding standards (PSR-12 for PHP, Kotlin conventions)
- [ ] No code duplication (DRY principle)
- [ ] Functions/methods are focused and testable

**Security (reference vibe-security-skill):**
- [ ] No SQL injection (prepared statements only)
- [ ] Input validation on all user inputs
- [ ] franchise_id filtering present in all data queries
- [ ] No sensitive data in logs or error messages

**Testing:**
- [ ] Unit tests included for new logic
- [ ] Tests pass locally before PR
- [ ] Edge cases have test coverage

## 6. Static Analysis & Linting

| Tool | Language | What It Checks | When Run |
|------|----------|---------------|----------|
| `php -l` | PHP | Syntax errors | Every commit |
| PHP_CodeSniffer | PHP | PSR-12 compliance | CI pipeline |
| Android Lint | Kotlin | Android best practices, accessibility | CI pipeline |
| Detekt | Kotlin | Code smells, complexity | CI pipeline |
| markdownlint | Markdown | Documentation formatting | CI pipeline |

## 7. Security Quality Gates

**Reference:** `vibe-security-skill` — mandatory for all web application work.

### 7.1 Security Checklist (per PR)

- [ ] No hardcoded credentials or API keys
- [ ] All SQL queries use prepared statements
- [ ] All user input validated and sanitized
- [ ] franchise_id present in every data access query
- [ ] RBAC permissions checked before data access
- [ ] Sensitive data encrypted at rest (EncryptedSharedPreferences on Android)
- [ ] JWT tokens validated with signature verification
- [ ] No sensitive data in URL parameters

### 7.2 Security Testing (per Release)

- [ ] OWASP Top 10 vulnerability scan
- [ ] Multi-tenant isolation verification (cross-tenant data access attempts)
- [ ] Auth bypass testing (expired tokens, invalid tokens, missing tokens)
- [ ] RBAC permission enforcement testing
- [ ] SQL injection testing on all input fields
- [ ] XSS testing on all output fields

## 8. Performance Standards

| Component | Metric | Target | Tool |
|-----------|--------|--------|------|
| PHP API | Response time (p95) | < 500ms | APM, curl timing |
| PHP API | Throughput | 100+ requests/sec | Load testing tool |
| Web Pages | First Contentful Paint | < 1.5s | Lighthouse |
| Web Pages | Total Page Load | < 2s | Lighthouse |
| Android App | Cold start time | < 3s | Android Profiler |
| Android App | Screen transition | < 300ms | Manual measurement |
| Database | Query execution | < 100ms (simple), < 500ms (complex) | MySQL EXPLAIN |
| Database | Index usage | No full table scans on large tables | EXPLAIN ANALYZE |

## 9. Accessibility Standards

### 9.1 Web (WCAG 2.1 AA)
- Color contrast ratio >= 4.5:1 for normal text
- All images have alt text
- All forms have labels
- Keyboard navigation works for all interactive elements
- Screen reader compatible (semantic HTML)

### 9.2 Android
- ContentDescription on all clickable elements
- Minimum touch target size 48dp x 48dp
- Support for TalkBack screen reader
- Text scalable via system font size settings
- Sufficient color contrast in Material 3 theme

## 10. Documentation Quality Standards

**Reference:** `doc-standards.md` in skills repository.

- All markdown files stay under 500 lines
- Two-tier structure (index + deep dive docs)
- Code examples are complete and runnable
- No vague or ambiguous language
- All domain terms defined in glossary

## 11. Defect Management Process

### 11.1 Severity Levels

| Severity | Definition | Response SLA | Resolution SLA |
|----------|-----------|-------------|---------------|
| S1 — Critical | System down, data loss, security breach | 1 hour | 4 hours |
| S2 — Major | Key feature broken, no workaround | 4 hours | 24 hours |
| S3 — Moderate | Feature degraded, workaround exists | 24 hours | 1 week |
| S4 — Minor | Cosmetic, minor inconvenience | 1 week | Next release |

### 11.2 Defect Lifecycle
```
New → Triaged → Assigned → In Progress → Fixed → Verified → Closed
                                          ↓
                                     Reopened → Assigned → ...
```

### 11.3 Triage Process
- Daily triage for S1/S2 defects
- Weekly triage for S3/S4 defects
- PM + QA Lead + Tech Lead participate in triage
- Every defect must have: severity, steps to reproduce, expected vs actual

## 12. Continuous Improvement

- Sprint retrospectives identify quality process improvements
- Monthly quality metrics review with trends analysis
- Quarterly QA Plan review and update
- Root cause analysis for all S1/S2 production defects
- Test automation coverage reviewed and expanded each sprint

## 13. Compliance Requirements

### 13.1 Data Privacy
- Personal data handling per GDPR/local data protection laws
- Data retention policies enforced (automated purging where required)
- User data export and deletion capabilities

### 13.2 Multi-Tenant Isolation Verification
- Automated tests verify franchise_id filtering on all data queries
- Quarterly manual audit of cross-tenant data access (no data leakage)
- Tenant isolation is a release-blocking quality gate
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| "We'll test later" | Defects compound exponentially | TDD from day one |
| No quality metrics | Cannot measure or improve quality | Define metrics with targets |
| Skipping security gates | Vulnerabilities reach production | Security checklist per PR |
| Manual-only testing | Slow, inconsistent, not repeatable | Automate test pyramid (60/25/10/5) |
| No defect severity levels | Everything is "urgent" | Define severity with SLAs |
| Ignoring multi-tenant testing | Data leakage between tenants | Automated tenant isolation tests |
| No code review process | Inconsistent quality | Mandatory PR reviews with checklists |
| Performance testing only at end | Performance issues are expensive to fix late | Continuous performance monitoring |

## Quality Checklist

- [ ] Quality objectives are specific and measurable
- [ ] QA roles and responsibilities assigned
- [ ] Quality metrics have numeric targets and measurement methods
- [ ] Test pyramid defined with proportions and tools
- [ ] Code review process documented with checklists
- [ ] Security quality gates reference `vibe-security-skill`
- [ ] Performance standards defined for all platforms (API, web, Android)
- [ ] Accessibility standards specified (WCAG 2.1 AA, Android a11y)
- [ ] Defect severity levels defined with response and resolution SLAs
- [ ] Multi-tenant isolation is a release-blocking quality gate
- [ ] Continuous improvement process defined (retros, metrics review)
- [ ] Document stays under 500 lines

---

**Back to:** [SDLC Planning Skill](../SKILL.md)
**Previous:** [Configuration Management Plan](configuration-management-plan.md)
**Next:** [Risk Management Plan](risk-management-plan.md)
