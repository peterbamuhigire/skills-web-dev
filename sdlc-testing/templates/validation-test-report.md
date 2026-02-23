# Software Validation Test Report (SVTR) -- Template & Guide

**Back to:** [SDLC Testing Skill](../SKILL.md)

## Purpose

Documents the **results of validation testing**, issues found, resolutions, and provides a **Go/No-Go release recommendation**. This is the primary evidence document for release decisions.

## Audience

Project managers, stakeholders, QA leads, compliance officers.

## When to Create

After all planned testing is complete, before the release decision. Updated for each release cycle.

---

## Template

```markdown
# [Project Name] -- Software Validation Test Report

**Report ID:** SVTR-[PROJECT]-[RELEASE]-001
**Version:** 1.0
**Date:** YYYY-MM-DD
**Project Name:** [Project Name]
**Release Version:** v[X.Y.Z]
**Testing Period:** YYYY-MM-DD to YYYY-MM-DD
**Report Author:** [Name]
**Approvers:** [QA Lead], [Dev Lead], [Product Owner]

---

## 1. Executive Summary

### 1.1 Overall Status
**Result:** PASS | CONDITIONAL PASS | FAIL

### 1.2 Key Findings
- [Finding 1: e.g., "All P0 test cases pass. System is release-ready."]
- [Finding 2: e.g., "2 Minor defects deferred to next sprint (cosmetic issues)."]
- [Finding 3: e.g., "Performance meets all benchmarks except report export (P2)."]

### 1.3 Recommendation
**RELEASE** | **CONDITIONAL RELEASE** (with noted exceptions) | **HOLD** (blocking issues)

[1-2 sentence justification for the recommendation.]

---

## 2. Test Execution Summary

### 2.1 Overall Metrics

| Metric | Planned | Executed | Passed | Failed | Blocked | Skipped |
|--------|---------|----------|--------|--------|---------|---------|
| Total Test Cases | NNN | NNN | NNN | NNN | NNN | NNN |
| P0 (Critical) | NNN | NNN | NNN | NNN | NNN | NNN |
| P1 (High) | NNN | NNN | NNN | NNN | NNN | NNN |
| P2 (Medium) | NNN | NNN | NNN | NNN | NNN | NNN |

### 2.2 Pass Rate

| Category | Pass Rate | Target | Status |
|----------|-----------|--------|--------|
| Overall | XX% | >= 95% | PASS/FAIL |
| P0 Tests | XX% | 100% | PASS/FAIL |
| P1 Tests | XX% | >= 95% | PASS/FAIL |
| P2 Tests | XX% | >= 80% | PASS/FAIL |

### 2.3 Coverage by Module

| Module | Total TCs | Passed | Failed | Blocked | Coverage % |
|--------|-----------|--------|--------|---------|-----------|
| Authentication | NNN | NNN | NNN | NNN | XX% |
| User Management | NNN | NNN | NNN | NNN | XX% |
| Dashboard | NNN | NNN | NNN | NNN | XX% |
| Sales | NNN | NNN | NNN | NNN | XX% |
| Inventory | NNN | NNN | NNN | NNN | XX% |
| Reports | NNN | NNN | NNN | NNN | XX% |
| **TOTAL** | **NNN** | **NNN** | **NNN** | **NNN** | **XX%** |

### 2.4 Breakdown by Test Type

| Test Type | Total | Passed | Failed | Pass Rate |
|-----------|-------|--------|--------|-----------|
| Unit | NNN | NNN | NNN | XX% |
| Integration | NNN | NNN | NNN | XX% |
| UI/E2E | NNN | NNN | NNN | XX% |
| Security | NNN | NNN | NNN | XX% |
| Performance | NNN | NNN | NNN | XX% |

---

## 3. Detailed Test Results

### 3.1 Failed Test Cases

| TC-ID | Description | Expected | Actual | Severity | Root Cause | Status |
|-------|------------|----------|--------|----------|-----------|--------|
| TC-XXX-YYY-NNN | [Brief description] | [Expected result] | [Actual result] | Critical/Major/Minor | [Root cause] | Fixed/Open/Deferred |
| TC-XXX-YYY-NNN | [Brief description] | [Expected result] | [Actual result] | Critical/Major/Minor | [Root cause] | Fixed/Open/Deferred |

### 3.2 Blocked Test Cases

| TC-ID | Description | Blocker | Resolution Plan | Target Date |
|-------|------------|---------|----------------|-------------|
| TC-XXX-YYY-NNN | [Brief description] | [What blocked execution] | [How to unblock] | YYYY-MM-DD |

---

## 4. Defect Summary

### 4.1 Defect Statistics

| Metric | Count |
|--------|-------|
| Total defects found | NNN |
| Fixed and verified | NNN |
| Open (to be fixed) | NNN |
| Deferred (next release) | NNN |
| Won't Fix (by design) | NNN |

### 4.2 Severity Distribution

| Severity | Found | Fixed | Open | Deferred |
|----------|-------|-------|------|----------|
| Critical | NNN | NNN | NNN | NNN |
| Major | NNN | NNN | NNN | NNN |
| Minor | NNN | NNN | NNN | NNN |
| Cosmetic | NNN | NNN | NNN | NNN |

### 4.3 Top Defect Categories

| Category | Count | % of Total | Example |
|----------|-------|-----------|---------|
| Validation errors | NNN | XX% | Missing input validation on [field] |
| Multi-tenant isolation | NNN | XX% | franchise_id not enforced on [query] |
| UI rendering | NNN | NNN% | Layout broken on [screen/device] |
| API response format | NNN | XX% | Missing field in [endpoint] response |
| Performance | NNN | XX% | Slow query on [table] |

### 4.4 Defect Trend

| Sprint/Phase | Found | Fixed | Net Open |
|-------------|-------|-------|----------|
| Sprint 1 | NNN | NNN | NNN |
| Sprint 2 | NNN | NNN | NNN |
| Sprint 3 | NNN | NNN | NNN |
| Sprint N | NNN | NNN | NNN |

[Trend should show net open defects decreasing over time. If increasing, flag as risk.]

---

## 5. Code Coverage Report

### 5.1 Overall Coverage

| Platform | Line Coverage | Branch Coverage | Target | Status |
|----------|-------------|----------------|--------|--------|
| PHP (PHPUnit) | XX% | XX% | >= 70% | PASS/FAIL |
| Android (JaCoCo) | XX% | XX% | >= 70% | PASS/FAIL |
| Combined | XX% | XX% | >= 70% | PASS/FAIL |

### 5.2 Per-Module Coverage

| Module | Line % | Branch % | Uncovered Areas |
|--------|--------|----------|----------------|
| Auth | XX% | XX% | [List uncovered classes/methods] |
| Sales | XX% | XX% | [List uncovered classes/methods] |
| Inventory | XX% | XX% | [List uncovered classes/methods] |
| Reports | XX% | XX% | [List uncovered classes/methods] |

### 5.3 Uncovered Areas Justification

| Area | Reason for Low Coverage | Risk Assessment |
|------|------------------------|----------------|
| [Class/Module] | [Generated code / third-party wrapper] | Low risk |
| [Class/Module] | [Complex legacy code, scheduled for refactor] | Medium risk |

---

## 6. Non-Functional Test Results

### 6.1 Performance Results

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| API P95 response time | < 500ms | NNNms | PASS/FAIL |
| Web page load (FCP) | < 2s | N.Ns | PASS/FAIL |
| Android cold start | < 3s | N.Ns | PASS/FAIL |
| DB query P95 | < 100ms | NNNms | PASS/FAIL |
| Report generation | < 5s (50 pages) | N.Ns | PASS/FAIL |

### 6.2 Security Test Results

| Test Area | Findings | Severity | Status |
|-----------|----------|----------|--------|
| SQL Injection | NNN found | [Severity] | All fixed / N open |
| XSS | NNN found | [Severity] | All fixed / N open |
| CSRF | NNN found | [Severity] | All fixed / N open |
| Auth bypass | NNN found | [Severity] | All fixed / N open |
| Tenant isolation | NNN found | [Severity] | All fixed / N open |
| OWASP ZAP scan | NNN alerts | [Severity] | All fixed / N open |

**Security gate:** Zero Critical or Major security findings must be open for release.

### 6.3 Multi-Tenant Isolation Results

| Test | franchise_id 1 | franchise_id 2 | Cross-Access | Status |
|------|---------------|---------------|-------------|--------|
| User data | Isolated | Isolated | Denied (404) | PASS/FAIL |
| Sales data | Isolated | Isolated | Denied (404) | PASS/FAIL |
| Reports | Scoped | Scoped | Denied (404) | PASS/FAIL |
| API endpoints | Filtered | Filtered | Denied (404) | PASS/FAIL |

### 6.4 Accessibility Results

| Check | Target | Result | Status |
|-------|--------|--------|--------|
| WCAG 2.1 AA (web) | Compliant | [Result] | PASS/FAIL |
| Color contrast | >= 4.5:1 | [Ratio] | PASS/FAIL |
| Android TalkBack | Functional | [Result] | PASS/FAIL |
| Touch targets | >= 48dp | [Result] | PASS/FAIL |

### 6.5 Compatibility Results

| Platform/Device | Version | Test Status | Issues |
|----------------|---------|-------------|--------|
| Android API 26 | 8.0 | [ ] Pass/Fail | [Issues if any] |
| Android API 34 | 14 | [ ] Pass/Fail | [Issues if any] |
| Chrome (latest) | NNN | [ ] Pass/Fail | [Issues if any] |
| Firefox (latest) | NNN | [ ] Pass/Fail | [Issues if any] |
| Safari (latest) | NNN | [ ] Pass/Fail | [Issues if any] |

---

## 7. Environment Details

| Environment | Config |
|------------|--------|
| Test server OS | Ubuntu XX.XX LTS |
| Database | MySQL 8.x (utf8mb4_general_ci) |
| PHP version | 8.x.x |
| Android build | devDebug variant, API 34 emulator |
| Test data | Seeded via [seeder script], NNN records per tenant |
| Test tools | PHPUnit NNN, JUnit 5.x, MockK NNN, Compose Testing NNN |

---

## 8. Issues & Risks

### 8.1 Open Issues

| ID | Description | Severity | Mitigation | Target Fix |
|----|------------|----------|-----------|-----------|
| ISS-001 | [Description] | Major/Minor | [Workaround] | vX.Y.Z+1 |
| ISS-002 | [Description] | Minor | [Workaround] | vX.Y.Z+1 |

### 8.2 Known Defects Shipping with Release

| Defect ID | Description | Severity | Justification |
|-----------|------------|----------|---------------|
| DEF-NNN | [Description] | Minor | [Why it's acceptable to ship] |

### 8.3 Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| [Risk 1] | Low/Med/High | Low/Med/High | [Mitigation plan] |
| [Risk 2] | Low/Med/High | Low/Med/High | [Mitigation plan] |

---

## 9. Lessons Learned

### 9.1 What Went Well
- [Positive finding 1]
- [Positive finding 2]

### 9.2 What Needs Improvement
- [Improvement area 1]
- [Improvement area 2]

### 9.3 Process Changes for Next Cycle
- [Change 1: e.g., "Add automated tenant isolation tests to CI pipeline"]
- [Change 2: e.g., "Increase integration test coverage for stored procedures"]

---

## 10. Sign-Off

### 10.1 Release Decision

**Decision:** GO | NO-GO | CONDITIONAL GO
**Date:** YYYY-MM-DD
**Conditions (if conditional):** [List conditions that must be met]

### 10.2 Approval Signatures

| Role | Name | Decision | Date | Signature |
|------|------|----------|------|-----------|
| QA Lead | [Name] | GO/NO-GO | YYYY-MM-DD | __________ |
| Development Lead | [Name] | GO/NO-GO | YYYY-MM-DD | __________ |
| Product Owner | [Name] | GO/NO-GO | YYYY-MM-DD | __________ |
| Project Manager | [Name] | GO/NO-GO | YYYY-MM-DD | __________ |

---

## Appendices

### Appendix A: Full Test Case Execution Log
[Reference: Link to test management tool export or separate file]

### Appendix B: Complete Defect List
[Reference: Link to issue tracker export or separate file]

### Appendix C: Coverage Report Data
[Reference: Link to JaCoCo/PHPUnit coverage HTML reports]
```

---

## Section-by-Section Guidance

### Executive Summary
Write this LAST, after all other sections are complete. It should be readable in 30 seconds and give a clear recommendation. Decision makers may only read this section.

### Test Execution Summary
Use real numbers. Every cell should have an actual count. If a test was not executed, explain why in the Blocked section. Never leave cells as "TBD" in a final report.

### Defect Trend
The trend should show net open defects decreasing over sprints. If the trend is flat or increasing, this is a red flag that must be called out in the risk section.

### Non-Functional Results
Report actual measured values against numeric targets. "Meets expectations" is not acceptable -- use "245ms vs target of 500ms."

### Sign-Off
All listed approvers must provide their decision. A single NO-GO from any approver blocks the release. Conditional GO requires conditions to be met and verified before deployment.

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| No executive summary | Decision makers skip the report | Write a clear 3-point summary with recommendation |
| Missing severity classification | Can't prioritize fix efforts | Classify every defect by severity |
| No sign-off section | Unclear who approved release | Require explicit Go/No-Go from each approver |
| Vague results ("mostly passing") | Can't assess quality objectively | Use exact numbers and percentages |
| No lessons learned | Repeat same mistakes | Document what worked and what to improve |
| Shipping Critical defects | Production incidents | Zero Critical defects for release |
| No trend analysis | Can't assess quality trajectory | Show defect counts per sprint |

## Quality Checklist

- [ ] Executive summary has clear recommendation (Release/Conditional/Hold)
- [ ] All test execution numbers are actual (no TBD, no estimates)
- [ ] Pass rates calculated and compared against targets
- [ ] Every failed test case has root cause and status
- [ ] Defect summary includes severity distribution
- [ ] Code coverage numbers reported per platform and module
- [ ] Performance results show actual values vs numeric targets
- [ ] Security results show zero Critical/Major open findings
- [ ] Multi-tenant isolation explicitly verified and reported
- [ ] Known shipping defects justified with risk assessment
- [ ] Lessons learned include actionable improvements
- [ ] All approvers listed with Go/No-Go decision
- [ ] Document stays under 500 lines

---

**Back to:** [SDLC Testing Skill](../SKILL.md)
**Previous:** [Validation & Verification Plan](validation-verification-plan.md)
**Next:** [Peer Review / Inspection Report](peer-review-report.md)
