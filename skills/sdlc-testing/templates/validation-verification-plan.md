# Software Validation & Verification Plan (SVVP) -- Template & Guide

**Back to:** [SDLC Testing Skill](../SKILL.md)

## Purpose

Defines the approach for **verifying** (built right) and **validating** (built the right thing) the software. Covers static analysis, code reviews, unit/integration testing, UAT, beta testing, and compliance audits.

## Audience

QA managers, project managers, compliance officers, tech leads.

## When to Create

After the SRS and SDD are approved. Updated as the V&V process evolves.

---

## Template

```markdown
# [Project Name] -- Software Validation & Verification Plan

**Document ID:** SVVP-[PROJECT]-001
**Version:** 1.0
**Date:** YYYY-MM-DD
**Author:** [Name]
**Status:** Draft | Under Review | Approved
**References:** [Link to SRS], [Link to SDD], [Link to STP]

---

## 1. Introduction

### 1.1 Purpose
This document defines the verification and validation approach for [Project Name].
It ensures the system is both built correctly (verification) and meets user needs
(validation).

### 1.2 Definitions

**Verification:** Are we building the product RIGHT?
- Does the code match the design (SDD)?
- Does the design match the requirements (SRS)?
- Are coding standards followed?

**Validation:** Are we building the RIGHT product?
- Does the product meet user needs?
- Do stakeholders accept the deliverables?
- Is the user experience satisfactory?

### 1.3 Referenced Documents
| Document | ID | Relationship |
|----------|-----|-------------|
| SRS | SRS-[PROJECT]-001 | Requirements to validate against |
| SDD | SDD-[PROJECT]-001 | Design to verify against |
| STP | STP-[PROJECT]-001 | Test strategy and cases |
| QA Plan | QAP-[PROJECT]-001 | Quality standards |

---

## 2. Verification Activities

### 2.1 Code Reviews (PR-Based)

**Process:**
1. Developer creates PR with description and linked requirements
2. At least 1 reviewer assigned (2 for merges to main)
3. Reviewer uses tech-stack checklist (see Peer Review Report template)
4. All findings addressed before merge
5. CI pipeline must pass before merge is allowed

**Review Scope:**
| Review Type | Trigger | Minimum Reviewers |
|------------|---------|-------------------|
| Feature PR | PR to develop | 1 |
| Release PR | PR to main | 2 |
| Hotfix PR | PR to main (urgent) | 1 + post-merge review |
| Architecture change | Any PR changing core structure | Tech Lead required |

### 2.2 Static Analysis

**PHP:**
| Tool | Check | When |
|------|-------|------|
| `php -l` | Syntax validation | Every commit (CI) |
| PHPStan (level 6+) | Type checking, dead code, logic errors | Every PR (CI) |
| PHPCS (PSR-12) | Code style compliance | Every PR (CI) |

**Kotlin/Android:**
| Tool | Check | When |
|------|-------|------|
| Detekt | Code smells, complexity, naming | Every PR (CI) |
| Android Lint | Android-specific issues, deprecated APIs | Every PR (CI) |
| Kotlin compiler | Type safety, null safety | Every build |

**SQL/Database:**
| Tool | Check | When |
|------|-------|------|
| Schema diff | Migration files match schema.sql | Before deploy |
| EXPLAIN audit | No full table scans on core queries | Per feature |
| Collation check | All tables use utf8mb4_general_ci | Per migration |

**Markdown:**
| Tool | Check | When |
|------|-------|------|
| `markdown-lint-cleanup` skill | Headings, blank lines, code fences | Before commit |
| Line count | All .md files under 500 lines | Before commit |

### 2.3 Unit Testing (Per-Layer Verification)

**PHP Layers:**
| Layer | What to Verify | Framework |
|-------|---------------|-----------|
| Services | Business logic, calculations, rules | PHPUnit |
| Validators | Input validation, format checks | PHPUnit |
| Helpers | Utility functions, formatters | PHPUnit |
| Middleware | Auth checks, RBAC enforcement | PHPUnit |

**Android Layers:**
| Layer | What to Verify | Framework |
|-------|---------------|-----------|
| ViewModels | State management, event handling | JUnit 5 + MockK + Turbine |
| UseCases | Business logic orchestration | JUnit 5 + MockK |
| Repositories | Data source coordination | JUnit 5 + MockK |
| Mappers/DTOs | Data transformation correctness | JUnit 5 |

### 2.4 Integration Testing

| Integration Point | Method | Framework |
|-------------------|--------|-----------|
| API contract | Request/response matches ICD | PHPUnit + curl |
| Database ops | CRUD against real test DB | PHPUnit + MySQL test DB |
| Room + API sync | Local cache vs remote data | Room in-memory + MockWebServer |
| Auth flow E2E | Login -> token -> protected resource | PHPUnit integration suite |
| Stored procedures | Call with test data, verify results | PHPUnit + MySQL |

### 2.5 Design Compliance Checks

| Check | Method | Frequency |
|-------|--------|-----------|
| Clean Architecture adherence | No cross-layer imports (domain depends on nothing) | Every PR review |
| Multi-tenant isolation | Every query has franchise_id WHERE clause | Every PR review |
| Security patterns | Auth on endpoints, prepared statements, output encoding | Every PR review |
| API consistency | Endpoints follow naming conventions, response format | Per API change |
| Error handling | Try/catch in controllers, typed error responses | Every PR review |

### 2.6 Build Verification

| Platform | Command | Pass Criteria |
|----------|---------|---------------|
| PHP | `php -l` on all changed files | Zero syntax errors |
| PHP | Full test suite | All tests pass |
| Android | `./gradlew assembleDevDebug` | Build succeeds |
| Android | `./gradlew testDevDebugUnitTest` | All unit tests pass |
| CI | GitHub Actions pipeline | All stages green |

---

## 3. Validation Activities

### 3.1 User Acceptance Testing (UAT)

**Environment:** Staging server (Ubuntu VPS with production-like config)

**UAT Setup:**
1. Deploy release candidate to staging
2. Seed staging with representative test data
3. Distribute UAT test scenarios to participants
4. Set UAT window (typically 1-2 weeks)
5. Collect results and feedback

**UAT Scenarios (mapped to user stories from SRS):**
| Scenario | User Role | SRS Ref | Accept Criteria |
|----------|-----------|---------|----------------|
| Complete a sale | Staff | FR-SALE-001 | Invoice created, stock updated, receipt printed |
| View dashboard | Owner | FR-DASH-001 | KPIs correct, data refreshes |
| Manage users | Super Admin | FR-USR-001 | CRUD operations, RBAC enforced |
| Generate report | Manager | FR-RPT-001 | Report renders, PDF exports, data accurate |
| [Scenario] | [Role] | [Ref] | [Criteria] |

**UAT Participants:**
| Role | Count | Selection Criteria |
|------|-------|-------------------|
| Super Admin | 1 | System administrator perspective |
| Owner | 2 | Business decision-maker perspective |
| Staff | 3-5 | Daily user perspective, varying tech skill |
| External (beta) | 5-10 | Fresh eyes, no prior system knowledge |

**UAT Sign-off Criteria:**
- [ ] All P0 scenarios pass
- [ ] >= 90% of P1 scenarios pass
- [ ] No Critical defects open
- [ ] All Major defects have workarounds documented
- [ ] UAT participants sign acceptance form

### 3.2 Beta Testing

**Internal Beta (Closed Testing):**
- Deploy to Google Play internal testing track
- Limited to team members and select stakeholders
- Duration: 1-2 weeks
- Focus: Crash reporting, UX feedback, edge cases

**External Beta (Staged Rollout):**
- Deploy to Google Play open testing track or staged rollout (10% -> 50% -> 100%)
- Monitor crash rate, ANR rate, user feedback
- Rollback threshold: crash rate > 1% or ANR rate > 0.5%

**Feedback Collection:**
| Channel | Tool | Triage Frequency |
|---------|------|-----------------|
| Play Store reviews | Play Console | Daily |
| In-app feedback | Custom form -> API | Daily |
| Crash reports | Firebase Crashlytics | Real-time |
| Support email | help@[domain].com | Daily |

### 3.3 Stakeholder Demos

**Sprint Demo Format:**
1. Recap sprint goals (2 min)
2. Live demo of completed features (15-20 min)
3. Show test results and coverage (5 min)
4. Q&A and feedback capture (10 min)
5. Next sprint preview (3 min)

**Feature Walkthrough Checklist:**
- [ ] Feature demonstrated on both web and mobile (if applicable)
- [ ] Happy path shown with real-looking data
- [ ] Error handling demonstrated (what happens when things go wrong)
- [ ] Multi-tenant isolation verified live (switch tenants, confirm isolation)
- [ ] Performance acceptable (no visible lag during demo)

### 3.4 Usability Testing

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Task completion rate | >= 90% | Observed user sessions |
| Error rate | < 10% per task | Count errors during session |
| Time-on-task | Within 2x expert time | Timed observation |
| User satisfaction (SUS) | >= 70 | System Usability Scale survey |

---

## 4. V&V Matrix

| Requirement ID | Verification Method | Validation Method | V-Status | V-Status |
|---------------|--------------------|--------------------|----------|----------|
| FR-AUTH-001 | Unit test + code review | UAT scenario: login | [ ] | [ ] |
| FR-SALE-001 | Unit + integration test | UAT scenario: sale | [ ] | [ ] |
| NFR-PERF-001 | Performance test suite | User feedback on speed | [ ] | [ ] |
| NFR-SEC-001 | Security test suite | Penetration test | [ ] | [ ] |
| NFR-MT-001 | Isolation test suite | Multi-tenant UAT | [ ] | [ ] |
| [Req-ID] | [V-method] | [V-method] | [ ] | [ ] |

**Rule:** Every requirement in the SRS must appear in this matrix with both a verification method and a validation method assigned.

---

## 5. Non-Functional Verification

### 5.1 Performance Benchmarks

| Metric | Target | Tool | Frequency |
|--------|--------|------|-----------|
| API P95 response | < 500ms | curl timing / load test | Per release |
| Web page load (FCP) | < 2s | Lighthouse | Per release |
| Android cold start | < 3s | Android Profiler | Per release |
| DB query P95 | < 100ms | MySQL slow query log | Weekly |
| Memory (Android) | No leaks in 30min session | LeakCanary | Per release |
| APK size | < 30MB | Gradle output | Per release |

### 5.2 Security Audit

| Check | Method | Reference |
|-------|--------|-----------|
| OWASP Top 10 | Automated scan + manual review | `vibe-security-skill` |
| Tenant isolation | Automated cross-tenant tests | TC-MT-* test cases |
| Auth bypass | Token manipulation tests | TC-AUTH-SEC-* |
| Injection attacks | Parameterized query audit | TC-SEC-* |
| Secret exposure | Code scan for hardcoded secrets | CI static analysis |

### 5.3 Accessibility

| Standard | Target | Method |
|----------|--------|--------|
| WCAG 2.1 AA (web) | Compliance | Lighthouse accessibility audit |
| Android TalkBack | Functional | Manual testing with screen reader |
| Color contrast | >= 4.5:1 ratio | Contrast checker tool |
| Touch targets | >= 48dp | Android Lint / manual check |

### 5.4 Compatibility Matrix

**Android:**
| API Level | OS Version | Status |
|-----------|-----------|--------|
| 26 | Android 8.0 | [ ] Tested |
| 29 | Android 10 | [ ] Tested |
| 33 | Android 13 | [ ] Tested |
| 34 | Android 14 | [ ] Tested |
| 35 | Android 15 | [ ] Tested |

**Web Browsers:**
| Browser | Versions | Status |
|---------|----------|--------|
| Chrome | Latest 2 | [ ] Tested |
| Firefox | Latest 2 | [ ] Tested |
| Safari | Latest 2 | [ ] Tested |
| Edge | Latest 2 | [ ] Tested |

---

## 6. V&V Schedule

| Activity | Start | End | Dependencies |
|----------|-------|-----|-------------|
| Static analysis setup | Week 1 | Week 2 | CI pipeline ready |
| Code review process | Week 1 | Ongoing | Team onboarded |
| Unit test coverage | Week 3 | Week 12 | Development in progress |
| Integration testing | Week 8 | Week 14 | APIs implemented |
| Security audit | Week 12 | Week 14 | Integration tests pass |
| Performance testing | Week 13 | Week 15 | System test environment ready |
| UAT | Week 15 | Week 17 | System testing complete |
| Beta rollout | Week 17 | Week 19 | UAT approved |

## 7. Sign-off Authority

| Activity | Approver | Sign-off Criteria |
|----------|---------|-------------------|
| Code review | Tech Lead | Checklist complete, CI green |
| Unit test coverage | Dev Lead | >= 70% coverage met |
| Integration testing | QA Lead | All P0/P1 integration tests pass |
| Security audit | Tech Lead + QA | Zero Critical findings |
| UAT | Product Owner | UAT sign-off criteria met |
| Release approval | PM + Sponsor | All V&V activities complete |
```

---

## Section-by-Section Guidance

### Verification vs Validation
Verification is internal-facing (does code match specs?). Validation is external-facing (does the product satisfy users?). Both are required for every requirement.

### Code Reviews
Define the review process clearly. Use the checklists from the Peer Review Report template. Enforce in CI where possible (block merge without approval).

### UAT Planning
Select UAT participants who represent actual end users. Include varying levels of technical skill. African SaaS users may range from tech-savvy managers to staff with basic smartphone skills.

### Non-Functional Verification
Set numeric targets, not vague goals. "Fast" is not measurable. "API P95 < 500ms" is measurable.

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Verification only, no validation | Product works but nobody wants it | Include UAT and stakeholder demos |
| Validation only, no verification | Users like it but code is fragile | Include static analysis and code reviews |
| No V&V matrix | Can't track coverage | Map every requirement to V&V methods |
| UAT with developers only | Developers know workarounds | Use real end users for UAT |
| Skipping accessibility | Excludes users with disabilities | Include WCAG and TalkBack testing |
| No sign-off authority | Unclear who approves release | Define approvers for each activity |

## Quality Checklist

- [ ] Both verification and validation defined for every requirement
- [ ] Static analysis tools configured for PHP, Kotlin, SQL
- [ ] Code review process documented with checklist references
- [ ] UAT scenarios mapped to SRS user stories
- [ ] UAT participants selected (diverse roles, skill levels)
- [ ] Performance benchmarks have numeric targets
- [ ] Security audit references `vibe-security-skill`
- [ ] Compatibility matrix covers target devices and browsers
- [ ] V&V matrix covers all SRS requirements
- [ ] Sign-off authority defined for each V&V activity
- [ ] Document stays under 500 lines

---

**Back to:** [SDLC Testing Skill](../SKILL.md)
**Previous:** [Test Case Specifications](test-case-specifications.md)
**Next:** [Validation Test Report](validation-test-report.md)
