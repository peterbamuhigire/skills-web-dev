# Software Test Plan (STP) -- Template & Guide

**Back to:** [SDLC Testing Skill](../SKILL.md)

## Purpose

Defines the **overall testing strategy**, objectives, scope, resources, environments, tools, schedule, and reporting for the project. Based on IEEE 829, adapted for modern TDD/agile workflows.

## Audience

QA leads, test engineers, project managers, development leads.

## When to Create

After the SRS is approved and the SDD is drafted or in progress.

---

## Template

```markdown
# [Project Name] -- Software Test Plan

**Document ID:** STP-[PROJECT]-001
**Version:** 1.0
**Date:** YYYY-MM-DD
**Author:** [Name]
**Status:** Draft | Under Review | Approved
**References:** [Link to SRS], [Link to SDD], [Link to QA Plan]

---

## 1. Introduction

### 1.1 Purpose
[Describe the purpose of this test plan. Reference the project and its scope.]

This document defines the testing strategy, scope, resources, and schedule for
[Project Name]. It ensures systematic verification that the system meets all
requirements defined in the SRS (doc ref) and conforms to the architecture
described in the SDD (doc ref).

### 1.2 Scope
[What is being tested. Reference module boundaries from SRS.]

### 1.3 Referenced Documents
| Document | ID | Location |
|----------|----|----------|
| Software Requirements Spec | SRS-[PROJECT]-001 | docs/planning/03-srs.md |
| Software Design Document | SDD-[PROJECT]-001 | docs/design/01-sdd.md |
| Quality Assurance Plan | QAP-[PROJECT]-001 | docs/planning/06-qa-plan.md |
| Risk Management Plan | RMP-[PROJECT]-001 | docs/planning/07-risk-plan.md |

### 1.4 Definitions & Acronyms
| Term | Definition |
|------|-----------|
| STP | Software Test Plan |
| SRS | Software Requirements Specification |
| SDD | Software Design Document |
| TDD | Test-Driven Development |
| P0 | Critical priority (must pass for release) |
| P1 | High priority (should pass, workaround acceptable) |
| P2 | Medium priority (nice to have, defer if needed) |

---

## 2. Test Strategy

### 2.1 Testing Levels

| Level | Distribution | Scope | Speed |
|-------|-------------|-------|-------|
| Unit | 70% | Single class/method in isolation | <1ms each |
| Integration | 20% | Component interactions (DB, API, auth) | ~100ms each |
| System/E2E | 10% | Full user flows end-to-end | ~1s each |
| Acceptance | Per UAT plan | Business scenarios per stakeholder | Manual |

### 2.2 Test Pyramid Distribution

**Android (Kotlin + Compose):**
- 70% Unit: JUnit 5 + MockK + Turbine (ViewModels, UseCases, Repositories)
- 20% Integration: Room in-memory DB, MockWebServer, Hilt test modules
- 10% UI: Compose Testing, Espresso (critical user flows)

**Web Backend (PHP 8+):**
- 70% Unit: PHPUnit (services, validators, helpers, business logic)
- 20% Integration: PHPUnit + real MySQL test DB (API endpoints, stored procs)
- 10% E2E: Browser testing (CRUD workflows, auth flows, multi-tenant scenarios)

### 2.3 TDD Workflow Integration
All development follows Red-Green-Refactor:
1. **Red:** Write a failing test that defines the expected behavior
2. **Green:** Write the minimum code to make the test pass
3. **Refactor:** Clean up code and tests while keeping everything green
4. **Commit:** Commit after each green cycle

Reference: `android-tdd` skill for implementation details.

### 2.4 Regression Testing Strategy
- Full regression suite runs on every PR merge to `develop`
- Smoke test subset runs on production deployment
- Regression scope expands as new features are added
- Flaky tests are quarantined and fixed within 48 hours

---

## 3. Test Scope

### 3.1 Features to be Tested
[Map each feature to SRS requirement IDs.]

| Feature Area | SRS References | Priority | Test Types |
|-------------|----------------|----------|------------|
| Authentication | FR-AUTH-001 to FR-AUTH-010 | P0 | Unit, Int, E2E, Security |
| User Management | FR-USR-001 to FR-USR-008 | P0 | Unit, Int, E2E |
| Dashboard | FR-DASH-001 to FR-DASH-005 | P1 | Unit, Int, UI |
| [Module Name] | FR-MOD-001 to FR-MOD-NNN | P1 | Unit, Int |
| Reports | FR-RPT-001 to FR-RPT-NNN | P2 | Unit, Int |

### 3.2 Features NOT to be Tested
[List with justification for each exclusion.]

| Feature | Justification |
|---------|--------------|
| Third-party SDK internals | Vendor responsibility (Retrofit, Room, Hilt) |
| OS-level functionality | Android/browser platform responsibility |
| [Feature] | [Justification] |

---

## 4. Test Environment

### 4.1 Environment Matrix

| Environment | OS | Database | PHP | Purpose |
|------------|-----|----------|-----|---------|
| Dev | Windows 11 WAMP | MySQL 8.4.x | 8.x | Local dev + unit tests |
| Staging | Ubuntu VPS | MySQL 8.x | 8.x | Integration + E2E tests |
| Production | Debian VPS | MySQL 8.x | 8.x | Smoke tests only |

### 4.2 Android Test Environment

| Config | Value |
|--------|-------|
| Min API Level | 26 (Android 8.0) |
| Target API Level | 35 (Android 15) |
| Test Devices | Pixel 7 (emulator), Samsung Galaxy (physical) |
| Build Variants | devDebug (unit tests), stagingDebug (integration) |
| CI Runner | Ubuntu (GitHub Actions) with Android SDK |

### 4.3 CI/CD Pipeline Test Stages

| Stage | Trigger | Tests | Timeout |
|-------|---------|-------|---------|
| Pre-commit | git push | PHP lint, Kotlin lint | 2 min |
| PR Validation | PR opened/updated | Unit + integration | 10 min |
| Merge Build | PR merged to develop | Full suite + coverage | 20 min |
| Release | Tag created | Full + security + perf | 30 min |
| Post-deploy | Production deploy | Smoke tests | 5 min |

---

## 5. Test Tools & Frameworks

### 5.1 Android
| Tool | Purpose | Version |
|------|---------|---------|
| JUnit 5 | Unit test framework | 5.10+ |
| MockK | Kotlin mocking library | 1.13+ |
| Turbine | Flow testing | 1.0+ |
| Compose Testing | UI component tests | BOM 2024.06+ |
| Espresso | E2E UI tests | 3.5+ |
| MockWebServer | API response mocking | 4.12+ |

### 5.2 PHP
| Tool | Purpose | Version |
|------|---------|---------|
| PHPUnit | Unit + integration test framework | 10+ |
| php -l | Syntax validation | 8.x |
| PHPStan/Psalm | Static analysis | Latest |

### 5.3 Security Testing
| Tool | Purpose |
|------|---------|
| OWASP ZAP | Automated vulnerability scanning |
| Manual checklist | Penetration testing per `vibe-security-skill` |
| Custom scripts | Multi-tenant isolation verification |

### 5.4 Performance
| Tool | Purpose |
|------|---------|
| Android Profiler | Memory leaks, CPU, battery |
| curl timing | API response time benchmarks |
| MySQL slow query log | Query performance analysis |
| Lighthouse | Web page load metrics |

---

## 6. Test Data Management

### 6.1 Test Fixtures
- **Standard test tenant:** franchise_id = 1 (primary), franchise_id = 2 (cross-tenant)
- **Test users per role:** super_admin, owner, manager, staff, member
- **Fixture reset:** Before each test suite, not between individual tests

### 6.2 Test Data Isolation
- Unit tests: In-memory data, no DB dependency
- Integration tests: Test database (separate from dev DB), reset per suite
- E2E tests: Seeded staging database with known state
- **Never use production data for testing**

### 6.3 Sensitive Data
- Test passwords: Use bcrypt-hashed known values
- Test tokens: Use deterministic JWT secrets (test env only)
- PII: Use obviously fake data (test@example.com, "Test User")
- EncryptedSharedPreferences: Use test master key in androidTest

---

## 7. Entry & Exit Criteria

### 7.1 Entry Criteria (testing can begin)
- [ ] SRS approved and requirement IDs assigned
- [ ] Code compiles without errors (PHP lint, Gradle build)
- [ ] Unit tests pass locally before pushing
- [ ] Test environment provisioned and accessible
- [ ] Test data seeded in staging

### 7.2 Exit Criteria (testing is complete)
- [ ] All P0 test cases pass (100%)
- [ ] P1 test cases pass (>= 95%)
- [ ] No open Critical or Major defects
- [ ] Code coverage >= 70% (unit), >= 50% (overall)
- [ ] Security test suite passes with zero Critical findings
- [ ] Performance benchmarks met (API < 500ms, page load < 2s)
- [ ] Multi-tenant isolation verified (zero cross-tenant access)

---

## 8. Schedule & Milestones

| Milestone | Target Date | Dependencies |
|-----------|-------------|-------------|
| Test Plan approved | YYYY-MM-DD | SRS + SDD approved |
| Test cases written | YYYY-MM-DD | Test Plan approved |
| Unit test coverage target met | YYYY-MM-DD | Development 80% complete |
| Integration testing complete | YYYY-MM-DD | All APIs implemented |
| Security testing complete | YYYY-MM-DD | Integration testing done |
| UAT complete | YYYY-MM-DD | System testing done |
| Test report delivered | YYYY-MM-DD | All testing complete |

## 9. Resource Allocation

| Resource | Role | Allocation |
|----------|------|-----------|
| [Name] | QA Lead (test planning, reporting) | 100% |
| [Name] | Test Engineer (test case design, execution) | 100% |
| [Name] | Dev (unit tests, bug fixes) | 50% (testing), 50% (dev) |
| Staging server | Integration + E2E testing | Shared |
| Android devices | Device testing | 2 physical, 3 emulators |

## 10. Defect Management

### 10.1 Severity Levels
| Severity | Definition | Response Time |
|----------|-----------|--------------|
| Critical | System crash, data loss, security breach | Fix within 4 hours |
| Major | Feature broken, no workaround | Fix within 24 hours |
| Minor | Feature works with workaround | Fix within sprint |
| Cosmetic | Visual/text issue, no functional impact | Fix when convenient |

### 10.2 Defect Workflow
```
Open -> Assigned -> In Progress -> Fixed -> Verified -> Closed
                                      \-> Reopened (if fix fails)
```

## 11. Reporting

| Report | Frequency | Audience | Content |
|--------|-----------|----------|---------|
| Daily test status | Daily | Dev team | Tests run, pass/fail, blockers |
| Sprint test summary | Bi-weekly | PM, stakeholders | Coverage, defects, trends |
| Release readiness | Per release | PM, sponsor | Go/No-Go recommendation |
| Coverage report | Per PR merge | Dev team | JaCoCo / PHPUnit coverage |

## 12. Approvals

| Role | Name | Date | Signature |
|------|------|------|-----------|
| QA Lead | [Name] | YYYY-MM-DD | __________ |
| Dev Lead | [Name] | YYYY-MM-DD | __________ |
| Project Manager | [Name] | YYYY-MM-DD | __________ |
```

---

## Section-by-Section Guidance

### Test Strategy
Be specific about the 70/20/10 split. Document which frameworks handle which test level. Reference `android-tdd` for implementation patterns.

### Test Scope
Map every feature to SRS requirement IDs. If a feature is excluded from testing, document why. This traceability is critical for audits.

### Test Environment
Document exact differences between environments. Include cross-platform notes (Windows paths vs Linux, case sensitivity, collation).

### Test Data
Always use franchise_id-scoped fixtures. Never share test data between tenants. Reset state between test suites.

### Entry/Exit Criteria
These are non-negotiable gates. Testing cannot begin without entry criteria met. Release cannot happen without exit criteria met.

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Testing only in production | Users find bugs | Test in staging first |
| No test data strategy | Flaky, unpredictable tests | Define fixtures and reset procedures |
| Skipping regression testing | Old bugs reappear | Run full suite on every merge |
| No coverage thresholds | Coverage silently drops | Set and enforce minimums in CI |
| Manual-only testing | Slow, inconsistent, expensive | Automate 70%+ of tests |
| Ignoring flaky tests | Erode trust in test suite | Quarantine and fix within 48 hours |

## Quality Checklist

- [ ] Test strategy covers all levels (unit, integration, system, acceptance)
- [ ] Test pyramid distribution documented with framework mapping
- [ ] Every feature in scope mapped to SRS requirement IDs
- [ ] All 3 environments documented with exact configurations
- [ ] Test tools listed with version numbers
- [ ] Test data strategy includes tenant isolation (franchise_id)
- [ ] Entry and exit criteria are measurable (numeric thresholds)
- [ ] Defect severity levels defined with response times
- [ ] Reporting cadence and audience documented
- [ ] Approval chain defined
- [ ] Document stays under 500 lines

---

**Back to:** [SDLC Testing Skill](../SKILL.md)
**Next:** [Test Case Specifications](test-case-specifications.md)
