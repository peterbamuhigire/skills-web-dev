# Execution Loop — Detailed Per-Task Patterns

## Task Execution Flow

Every task from the plan follows this exact sequence. No shortcuts.

### 1. Pre-Task Checks

Before touching any code for a task:

```
[PRE-CHECK] Task N: {Task Name}
  Dependencies met?     {list completed dependencies}
  Files to create:      {list new files}
  Files to modify:      {list existing files}
  Tests to write:       {list test cases}
  Acceptance criteria:  {list from plan}
```

**Dependency verification:**

| Check | Action if Failed |
|-------|-----------------|
| Required table doesn't exist | Execute migration task first |
| Required service not created | Execute service task first |
| Required config missing | Create config with defaults |
| Required package not installed | Install and document |

### 2. RED Phase — Write Failing Tests

Write tests BEFORE implementation. Every test must fail initially.

**Test structure by layer:**

```
tests/
├── Unit/
│   ├── Models/           # Entity/model logic
│   ├── Services/         # Business rules
│   └── Validators/       # Input validation
├── Feature/
│   ├── Api/              # Endpoint integration
│   └── Auth/             # Authentication flows
└── E2E/                  # Full user journeys (if applicable)
```

**Test naming convention:**

```
methodUnderTest_condition_expectedResult

Examples:
createInvoice_validData_returnsInvoiceWithId()
createInvoice_missingCustomerId_throwsValidationException()
createInvoice_duplicateNumber_returns409Conflict()
calculateTotal_multipleLineItems_returnsSumWithTax()
login_expiredToken_returns401()
```

**Minimum test cases per task:**

| Test Type | Required | Example |
|-----------|----------|---------|
| Happy path | Always | Valid input returns expected output |
| Invalid input | Always | Missing/malformed data returns error |
| Edge case | When applicable | Empty list, max values, boundaries |
| Auth/permission | When endpoint | Unauthorized user gets 401/403 |
| Tenant isolation | When multi-tenant | User A cannot see User B data |

**Verify RED:**

```
Run tests → All NEW tests FAIL → Proceed to GREEN
          → Any new test PASSES → Test is wrong (not testing new behavior)
```

### 3. GREEN Phase — Minimum Implementation

Write the minimum code to make all tests pass. No extras.

**Rules:**

- Implement ONLY what the tests require
- Don't add features not covered by tests
- Don't optimize prematurely
- Don't add error handling beyond what tests verify
- Use existing project patterns (check nearby files for conventions)

**Convention discovery:**

Before writing code, check the project for existing patterns:

```
# How are controllers structured?
Read existing controller → Match pattern

# How are models defined?
Read existing model → Match fields, relationships, traits

# How are routes registered?
Read routes file → Match group, prefix, middleware pattern

# How are responses formatted?
Read existing endpoint → Match response envelope
```

### 4. VALIDATE Phase — 5-Layer Stack

Run the full validation stack. Reference: `ai-error-handling` skill.

**Layer 1: Syntax**

```bash
# PHP
php -l app/Http/Controllers/NewController.php

# Kotlin
kotlinc -script app/src/main/java/NewFile.kt

# JavaScript/TypeScript
node --check src/newFile.js
npx tsc --noEmit src/newFile.ts
```

**Layer 2: Requirements Matching**

```
For each acceptance criterion in the plan:
  ✅ Criterion met — evidence: {test name or code line}
  ❌ Criterion NOT met — gap: {what's missing}
```

**Layer 3: Test Execution**

```bash
# Run only this task's tests (fast feedback)
php artisan test --filter=NewControllerTest
./gradlew test --tests="*.NewViewModelTest"
npm test -- --testPathPattern="new-feature"

# Run full suite (catch regressions)
php artisan test
./gradlew test
npm test
```

**Layer 4: Security Checklist**

| Check | Status |
|-------|--------|
| SQL injection safe (parameterized queries) | ✅/❌ |
| XSS safe (output encoding) | ✅/❌ |
| Auth middleware on endpoint | ✅/❌ |
| Tenant scoping enforced (franchise_id) | ✅/❌ |
| Input validation present | ✅/❌ |
| No secrets in code | ✅/❌ |
| CSRF protection (web routes) | ✅/❌ |

**Layer 5: Documentation**

```
Function has docblock:     ✅/❌
Parameters documented:     ✅/❌
Return type documented:    ✅/❌
Complex logic commented:   ✅/❌
```

### 5. REFACTOR Phase

With all tests passing, clean up:

- Extract duplicated code into helpers/services
- Improve variable/method names for clarity
- Simplify complex conditionals
- Ensure consistent formatting with project style
- Remove debug statements

**Rule:** Run tests after EVERY refactor change. If tests break, revert.

### 6. LOG & UPDATE Phase

```
[TASK N] COMPLETED ✅
  Tests:    {passed}/{total}
  Score:    {score}/100
  Duration: {time}
  Files:    {list of created/modified files}
```

Update the plan file with completion status (see Plan Status Format in SKILL.md).

### 7. NEXT Phase

Check dependency graph → Identify unlocked tasks → Start next task immediately.

```
[NEXT] Task N complete. Checking dependencies...
  Task N+1: Dependencies met ✅ → Starting...
  Task N+2: Blocked by Task N+3 ⏳ → Skipping for now
  Task N+3: Dependencies met ✅ → Queued after N+1
```

## Multi-File Task Patterns

When a task requires multiple files:

### Database-First Pattern (Backend Features)

```
1. Migration file        → Schema definition
2. Model/Entity class    → Data representation
3. Repository/DAO        → Data access
4. Service/UseCase       → Business logic
5. Controller/Handler    → HTTP interface
6. Route registration    → URL mapping
7. Tests for each layer  → Verification
```

### UI-First Pattern (Frontend Features)

```
1. Component/Screen      → Visual structure
2. State management      → ViewModel/Store
3. API client call       → Data fetching
4. Navigation wiring     → Route/screen registration
5. Tests                 → UI + integration
```

### Full-Stack Pattern (End-to-End Features)

```
1. Migration + Model     → Data layer
2. API endpoint + tests  → Backend
3. UI component + tests  → Frontend
4. Integration test      → Full flow
```

## Parallel Execution Opportunities

Identify and execute independent tasks simultaneously:

```
SEQUENTIAL (must be ordered):
  Migration → Model → Repository → Controller

PARALLEL (can run together):
  ├── Frontend component (independent of backend tests)
  ├── Seed data creation (independent of business logic)
  └── Documentation updates (independent of code)
```

## Handling Large Files

When generating files that may exceed output limits:

1. **Split by section** — Generate one class/function at a time
2. **Verify completeness** — Check no methods are missing
3. **If truncated** — User replies with continuation prompt (see SKILL.md)
4. **Never restart** — Resume from exact cutoff point
