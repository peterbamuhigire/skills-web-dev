# Test Case Specifications -- Template & Guide

**Back to:** [SDLC Testing Skill](../SKILL.md)

## Purpose

Defines **detailed test steps, inputs, and expected results** for individual test cases. Provides naming conventions, categorized examples, test data fixtures, and traceability to SRS requirements.

## Audience

Test engineers, developers writing tests, QA leads.

## When to Create

After the Software Test Plan is approved. Updated continuously as features are developed.

---

## Template

### Test Case Identification

**Naming Convention:** `TC-[MODULE]-[TYPE]-[###]`

| Component | Values | Example |
|-----------|--------|---------|
| MODULE | AUTH, USR, DASH, SALE, INV, RPT, SET | TC-AUTH-... |
| TYPE | UNIT, INT, UI, SEC, PERF | TC-AUTH-UNIT-... |
| ### | Sequential number, zero-padded | TC-AUTH-UNIT-001 |

**Priority Levels:**

| Priority | Meaning | Release Gate |
|----------|---------|-------------|
| P0 | Critical -- system unusable without it | Must pass 100% |
| P1 | High -- core functionality affected | Must pass >= 95% |
| P2 | Medium -- secondary functionality | Must pass >= 80% |

---

### Test Case Template

```markdown
## TC-[MODULE]-[TYPE]-[###]: [Descriptive Title]

**Related Requirement:** FR-[MODULE]-[###] or NFR-[CATEGORY]-[###]
**Test Level:** Unit | Integration | UI/E2E | Security | Performance
**Priority:** P0 | P1 | P2
**Automated:** Yes | No | Partial

### Preconditions
- [What must be true before this test can run]
- [Environment state, data state, user state]

### Test Steps
| Step | Action | Input Data | Expected Result |
|------|--------|-----------|----------------|
| 1 | [Action description] | [Specific input] | [Expected output/state] |
| 2 | [Action description] | [Specific input] | [Expected output/state] |
| 3 | [Action description] | [Specific input] | [Expected output/state] |

### Test Data
- [Specific values used in this test]
- [Reference to fixtures if applicable]

### Expected Results
[Clear, unambiguous statement of the expected outcome]

### Actual Results
[Filled during execution -- leave blank in template]

### Pass/Fail
[ ] Pass  [ ] Fail  [ ] Blocked

### Notes
[Edge cases, known issues, dependencies on other tests]
```

---

## Test Case Categories & Examples

### 1. Authentication Test Cases

```markdown
## TC-AUTH-UNIT-001: Login with valid credentials

**Related Requirement:** FR-AUTH-001
**Test Level:** Unit
**Priority:** P0
**Automated:** Yes

### Preconditions
- Test user exists: test@example.com / hashed("TestPass123!")
- User belongs to franchise_id = 1

### Test Steps
| Step | Action | Input Data | Expected Result |
|------|--------|-----------|----------------|
| 1 | Call login endpoint | email: test@example.com, password: TestPass123! | 200 OK |
| 2 | Verify response body | -- | Contains access_token, refresh_token, user object |
| 3 | Verify token payload | Decode JWT | Contains user_id, franchise_id, role |
| 4 | Verify audit log | Query audit_logs table | Login event recorded |

### Expected Results
User receives valid JWT tokens. Session created. Audit trail logged.
```

```markdown
## TC-AUTH-SEC-001: Login attempt with SQL injection payload

**Related Requirement:** NFR-SEC-001
**Test Level:** Security
**Priority:** P0
**Automated:** Yes

### Preconditions
- Login endpoint is accessible

### Test Steps
| Step | Action | Input Data | Expected Result |
|------|--------|-----------|----------------|
| 1 | Call login endpoint | email: "' OR '1'='1' --", password: "anything" | 401 Unauthorized |
| 2 | Verify no data leak | Inspect response body | Generic error message only |
| 3 | Check DB integrity | Query users table | No records altered |

### Expected Results
Injection payload rejected. No SQL execution. No data exposure.
```

```markdown
## TC-AUTH-INT-001: Multi-tenant login isolation

**Related Requirement:** NFR-MT-001
**Test Level:** Integration
**Priority:** P0
**Automated:** Yes

### Preconditions
- User A exists in franchise_id = 1
- User B exists in franchise_id = 2

### Test Steps
| Step | Action | Input Data | Expected Result |
|------|--------|-----------|----------------|
| 1 | Login as User A | User A credentials | Token with franchise_id = 1 |
| 2 | Request User B's data | GET /api/users/{userB_id} with User A's token | 404 Not Found |
| 3 | Verify query log | Check executed SQL | WHERE franchise_id = 1 present |

### Expected Results
User A cannot access User B's data. franchise_id enforced at query level.
```

### 2. CRUD Test Cases

```markdown
## TC-INV-UNIT-001: Create product with valid data

**Related Requirement:** FR-INV-001
**Test Level:** Unit
**Priority:** P0
**Automated:** Yes

### Preconditions
- franchise_id = 1 active
- User has "inventory.create" permission

### Test Steps
| Step | Action | Input Data | Expected Result |
|------|--------|-----------|----------------|
| 1 | Call create product | name: "Widget A", sku: "WGT-001", price: 29.99 | 201 Created |
| 2 | Verify response | -- | Contains product ID, all fields |
| 3 | Verify franchise_id | Query product record | franchise_id = 1 set automatically |

### Expected Results
Product created with correct franchise_id. All fields persisted.
```

```markdown
## TC-INV-UNIT-002: Create product with invalid data

**Related Requirement:** FR-INV-001
**Test Level:** Unit
**Priority:** P1
**Automated:** Yes

### Test Steps
| Step | Action | Input Data | Expected Result |
|------|--------|-----------|----------------|
| 1 | Empty name | name: "", sku: "WGT-002" | 422: "Name is required" |
| 2 | Duplicate SKU | name: "Widget B", sku: "WGT-001" | 409: "SKU already exists" |
| 3 | Negative price | name: "Widget C", price: -5.00 | 422: "Price must be positive" |
| 4 | Exceeds max length | name: [256 chars], sku: "X" | 422: "Name exceeds 255 characters" |
```

### 3. Multi-Tenant Isolation Test Cases

```markdown
## TC-MT-INT-001: Cross-tenant data access denied

**Related Requirement:** NFR-MT-002
**Test Level:** Integration
**Priority:** P0
**Automated:** Yes

### Test Steps
| Step | Action | Input Data | Expected Result |
|------|--------|-----------|----------------|
| 1 | Create record in tenant 1 | franchise_id = 1, name: "Tenant 1 Item" | 201 Created, record ID returned |
| 2 | Login as tenant 2 user | Tenant 2 credentials | Token with franchise_id = 2 |
| 3 | GET the record from step 1 | GET /api/items/{id} with tenant 2 token | 404 Not Found |
| 4 | List all items as tenant 2 | GET /api/items with tenant 2 token | Empty list or tenant 2 items only |

### Expected Results
Tenant 2 cannot see, access, or modify tenant 1's data. No error message reveals
the record exists (return 404, not 403).
```

### 4. API Test Cases

```markdown
## TC-API-INT-001: Pagination returns correct structure

**Related Requirement:** NFR-API-001
**Test Level:** Integration
**Priority:** P1
**Automated:** Yes

### Test Steps
| Step | Action | Input Data | Expected Result |
|------|--------|-----------|----------------|
| 1 | Request page 1 | GET /api/products?page=1&per_page=10 | 200 OK |
| 2 | Verify response structure | -- | data[], meta{current_page, total, per_page, last_page} |
| 3 | Verify data count | -- | data array has <= 10 items |
| 4 | Request beyond last page | GET /api/products?page=999 | 200 OK, empty data array |
```

### 5. Mobile UI Test Cases

```markdown
## TC-DASH-UI-001: Dashboard renders with data

**Related Requirement:** FR-DASH-001
**Test Level:** UI
**Priority:** P1
**Automated:** Yes (Compose Testing)

### Preconditions
- ViewModel injected with mock repository returning known KPI data

### Test Steps
| Step | Action | Input Data | Expected Result |
|------|--------|-----------|----------------|
| 1 | Render DashboardScreen | KPIs: revenue=50000, orders=120 | Screen displays without crash |
| 2 | Verify KPI cards | -- | "50,000" and "120" visible on screen |
| 3 | Pull to refresh | Swipe down gesture | Loading indicator appears, data refreshes |
| 4 | Verify offline state | Network unavailable | Cached data shown, offline banner visible |
```

### 6. Performance Test Cases

```markdown
## TC-PERF-001: API response time under load

**Related Requirement:** NFR-PERF-001
**Test Level:** Performance
**Priority:** P1
**Automated:** Yes

### Test Steps
| Step | Action | Input Data | Expected Result |
|------|--------|-----------|----------------|
| 1 | Single request baseline | GET /api/dashboard | Response < 200ms |
| 2 | 50 concurrent requests | 50x GET /api/dashboard | P95 < 500ms |
| 3 | 100 concurrent requests | 100x GET /api/dashboard | P95 < 1000ms, zero errors |
| 4 | Database query check | EXPLAIN on dashboard query | Uses indexes, no full table scan |
```

### 7. Security Test Cases

```markdown
## TC-SEC-001: CSRF protection on mutations

**Related Requirement:** NFR-SEC-003
**Test Level:** Security
**Priority:** P0
**Automated:** Yes

### Test Steps
| Step | Action | Input Data | Expected Result |
|------|--------|-----------|----------------|
| 1 | POST without CSRF token | POST /api/users (no token) | 403 Forbidden |
| 2 | POST with invalid token | POST /api/users (wrong token) | 403 Forbidden |
| 3 | POST with valid token | POST /api/users (correct token) | 201 Created |
```

---

## Test Data Fixtures

### Standard Test Tenants

| Fixture | franchise_id | Name | Purpose |
|---------|-------------|------|---------|
| tenant_primary | 1 | Test Company A | Primary test tenant |
| tenant_secondary | 2 | Test Company B | Cross-tenant isolation tests |
| tenant_empty | 3 | Empty Corp | Empty-state testing |

### Test Users Per Role

| Fixture | Role | franchise_id | Email |
|---------|------|-------------|-------|
| user_super_admin | super_admin | NULL (all) | super@test.com |
| user_owner | owner | 1 | owner@test.com |
| user_manager | manager | 1 | manager@test.com |
| user_staff | staff | 1 | staff@test.com |
| user_member | member | 1 | member@test.com |
| user_other_tenant | owner | 2 | other@test.com |

### Edge Case Data

| Fixture | Value | Purpose |
|---------|-------|---------|
| empty_string | "" | Required field validation |
| max_length_255 | "A" x 255 | VARCHAR boundary |
| max_length_256 | "A" x 256 | VARCHAR overflow |
| special_chars | "O'Brien & Co <script>" | XSS + apostrophe handling |
| unicode_text | "Kampala" | UTF-8 handling |
| zero_amount | 0.00 | Zero-value calculations |
| negative_amount | -100.00 | Negative value rejection |
| max_decimal | 99999999.99 | DECIMAL(10,2) boundary |

---

## Traceability Matrix

| Test Case ID | Requirement ID | Test Level | Priority | Status |
|-------------|---------------|-----------|----------|--------|
| TC-AUTH-UNIT-001 | FR-AUTH-001 | Unit | P0 | [ ] |
| TC-AUTH-SEC-001 | NFR-SEC-001 | Security | P0 | [ ] |
| TC-AUTH-INT-001 | NFR-MT-001 | Integration | P0 | [ ] |
| TC-INV-UNIT-001 | FR-INV-001 | Unit | P0 | [ ] |
| TC-INV-UNIT-002 | FR-INV-001 | Unit | P1 | [ ] |
| TC-MT-INT-001 | NFR-MT-002 | Integration | P0 | [ ] |
| TC-API-INT-001 | NFR-API-001 | Integration | P1 | [ ] |
| TC-DASH-UI-001 | FR-DASH-001 | UI | P1 | [ ] |
| TC-PERF-001 | NFR-PERF-001 | Performance | P1 | [ ] |
| TC-SEC-001 | NFR-SEC-003 | Security | P0 | [ ] |

**Rule:** Every functional requirement (FR-xxx) must have at least one test case. Every non-functional requirement (NFR-xxx) must have at least one test case.

---

## Test Suite Organization

### By Module

| Suite | Test Cases | Priority Mix |
|-------|-----------|-------------|
| auth-suite | TC-AUTH-* | Mostly P0 |
| user-suite | TC-USR-* | P0 + P1 |
| dashboard-suite | TC-DASH-* | P1 |
| sales-suite | TC-SALE-* | P0 + P1 |
| inventory-suite | TC-INV-* | P0 + P1 |
| reports-suite | TC-RPT-* | P2 |

### By Type (CI Pipeline Order)

| Suite | When to Run | Duration Target |
|-------|------------|----------------|
| unit-suite | Every commit | < 30 seconds |
| integration-suite | Every PR | < 5 minutes |
| security-suite | Every PR + release | < 10 minutes |
| ui-suite | Merge to develop | < 10 minutes |
| performance-suite | Release candidate | < 15 minutes |

### By Priority (Smoke Test Selection)

| Suite | Content | When |
|-------|---------|------|
| P0 smoke tests | All P0 test cases across modules | Post-deploy to production |
| P1 regression | All P0 + P1 test cases | Pre-release |
| Full suite | All P0 + P1 + P2 test cases | Merge to develop |

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Test cases without expected results | Can't determine pass/fail | Always state expected outcome explicitly |
| No traceability to requirements | Can't prove coverage | Map every TC to FR-xxx or NFR-xxx |
| Brittle tests (tied to implementation) | Break on refactor | Test behavior, not internal structure |
| No edge case testing | Bugs in boundary conditions | Include negative, boundary, overflow tests |
| Copy-paste test cases | Maintenance nightmare | Use parameterized tests and data fixtures |
| No test data fixtures | Inconsistent test state | Define standard fixtures, reset per suite |
| Unnamed test data ("test123") | Hard to debug failures | Use descriptive, realistic fixture data |

## Quality Checklist

- [ ] Naming convention TC-[MODULE]-[TYPE]-[###] used consistently
- [ ] Every test case has Related Requirement (FR-xxx or NFR-xxx)
- [ ] Every test case has explicit Expected Results
- [ ] Test data uses franchise_id-scoped fixtures
- [ ] Edge cases covered (empty, max length, special chars, Unicode)
- [ ] Security test cases reference OWASP categories
- [ ] Multi-tenant isolation test cases included
- [ ] Traceability matrix covers all SRS requirements
- [ ] Test suites organized by module, type, and priority
- [ ] Performance test cases have numeric targets
- [ ] Document stays under 500 lines

---

**Back to:** [SDLC Testing Skill](../SKILL.md)
**Previous:** [Software Test Plan](software-test-plan.md)
**Next:** [Validation & Verification Plan](validation-verification-plan.md)
