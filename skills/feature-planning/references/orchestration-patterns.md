# Orchestration Patterns for Implementation Plans

**Purpose:** Apply orchestration strategies to create implementation plans that coordinate multiple agents/tasks effectively

**Applies to:** Feature implementation plans that involve multiple components, phases, or agents

---

## Why Orchestration Matters for Implementation Plans

Implementation plans are **instructions for coordinating work**. Using orchestration patterns makes plans:

- ✅ **More efficient**: Identifies what can run in parallel
- ✅ **More reliable**: Handles dependencies and failures
- ✅ **Easier to execute**: Clear sequencing and coordination
- ✅ **Better coordinated**: Multiple developers/agents work together smoothly

---

## The 5 Orchestration Strategies for Plans

### 1. Sequential Orchestration

**Use when:** Tasks MUST happen in specific order

**Pattern:**
```markdown
## Phase 1: Foundation (Sequential - Order Matters)

### Task 1: Create Database Migration
**FILE:** `database/migrations/YYYY_MM_DD_create_table.php`
**MUST complete before Task 2** (model needs table to exist)

### Task 2: Create Model
**FILE:** `app/Models/Product.php`
**DEPENDS ON:** Task 1 (table must exist)
**MUST complete before Task 3** (controller needs model)

### Task 3: Create Controller
**FILE:** `app/Http/Controllers/ProductController.php`
**DEPENDS ON:** Task 2 (needs model)
```

**Key indicator:** Each task DEPENDS on previous output

**Example: Database Setup**
```markdown
Sequential flow (cannot parallelize):
1. Create migration → Must complete first
2. Run migration → Needs migration file
3. Create model → Needs table to exist
4. Create seeder → Needs model
5. Run seeder → Needs seeder file
```

---

### 2. Parallel Orchestration

**Use when:** Tasks DON'T depend on each other

**Pattern:**
```markdown
## Phase 2: API + UI (Parallel - Independent Work)

### Task 4a: Create API Endpoint
**FILE:** `app/Http/Controllers/Api/ProductController.php`
**CAN RUN IN PARALLEL** with Task 4b

### Task 4b: Create UI Component
**FILE:** `resources/js/components/ProductList.vue`
**CAN RUN IN PARALLEL** with Task 4a

### Task 4c: Create Documentation
**FILE:** `docs/api/products.md`
**CAN RUN IN PARALLEL** with Tasks 4a and 4b

---

**SYNC POINT:** All 3 tasks must complete before Task 5

### Task 5: Integration Testing
**FILE:** `tests/Feature/ProductIntegrationTest.php`
**DEPENDS ON:** Tasks 4a + 4b + 4c (all must be done)
```

**Key indicator:** Multiple tasks can execute simultaneously

**Example: Multi-Component Feature**
```markdown
Parallel execution (30% faster):
├─ Backend: Create API endpoint (5 min)
├─ Frontend: Create UI component (5 min)
└─ Docs: Write API documentation (5 min)

Total time: 5 minutes (not 15!)

Then sequential:
→ Integration testing (after all 3 done)
```

**Benefits:**
- **Faster**: Multiple developers work simultaneously
- **Efficient**: No waiting for unrelated tasks
- **Scalable**: Can assign to different team members

---

### 3. Conditional Orchestration

**Use when:** Different paths based on conditions

**Pattern:**
```markdown
## Phase 3: Data Handling (Conditional - Depends on Data Source)

### Task 6: Determine Data Source

**IF** external API is available:
  → **Task 6a:** Integrate External API
  **FILE:** `app/Services/ExternalProductApi.php`
  **INCLUDE:** Retry logic (API might be down)

**ELSE IF** CSV import needed:
  → **Task 6b:** Create CSV Importer
  **FILE:** `app/Services/CsvProductImporter.php`
  **INCLUDE:** Batch processing (for large files)

**ELSE** (manual entry only):
  → **Task 6c:** Enhanced Manual Entry Form
  **FILE:** `resources/js/components/ProductForm.vue`
  **INCLUDE:** Validation and auto-save

**SYNC POINT:** Only ONE of these paths executes
```

**Key indicator:** "IF/ELSE" logic based on requirements

**Example: Payment Integration**
```markdown
Conditional flow (different paths):

IF (in Africa):
  ├─ Integrate M-Pesa (Kenya)
  ├─ Integrate Mobile Money (Uganda)
  └─ Include offline payment mode

ELSE IF (in US/Europe):
  ├─ Integrate Stripe
  └─ Include credit card processing

ELSE:
  └─ Manual invoice generation

Different implementation based on market.
```

---

### 4. Looping Orchestration

**Use when:** Need to repeat for multiple items

**Pattern:**
```markdown
## Phase 4: Multi-Module Setup (Looping - Repeat for Each Module)

**FOR EACH** module in [Sales, Inventory, Finance, HR]:

  ### Task 7.{module}: Setup {Module} Module

  **FILES:**
  - `database/migrations/YYYY_MM_DD_create_{module}_tables.php`
  - `app/Models/{Module}/*.php`
  - `app/Http/Controllers/{Module}Controller.php`
  - `resources/js/components/{Module}/*.vue`

  **PROCESS:**
  1. Create migration for {module}
  2. Create models for {module}
  3. Create controller for {module}
  4. Create UI components for {module}
  5. Run tests for {module}

  **REPEAT** until all modules complete

**EXIT CONDITION:** All 4 modules (Sales, Inventory, Finance, HR) are set up
```

**Key indicator:** "FOR EACH" or "REPEAT UNTIL"

**Example: Multi-Tenant Setup**
```markdown
Looping flow (for each tenant):

FOR EACH tenant in system:
  1. Create tenant database
  2. Run migrations for tenant
  3. Seed initial data for tenant
  4. Create admin user for tenant
  5. Configure tenant settings

Loop until all tenants processed.
```

---

### 5. Retry Orchestration

**Use when:** Operations might fail temporarily

**Pattern:**
```markdown
## Phase 5: External Integration (Retry - Handle Failures)

### Task 8: Fetch External Schema

**FILE:** `app/Services/SchemaFetcher.php`

**WITH RETRY LOGIC:**
- **Attempt 1:** Try to fetch schema from external API
  - **On success:** Continue to Task 9
  - **On failure:** Wait 2 seconds, retry

- **Attempt 2:** Try again
  - **On success:** Continue to Task 9
  - **On failure:** Wait 5 seconds, retry

- **Attempt 3:** Final attempt
  - **On success:** Continue to Task 9
  - **On failure:** Use cached schema (fallback)

**FALLBACK:** If all retries fail, use local cached schema

**CODE:**
```php
public function fetchSchema() {
    $maxRetries = 3;
    $attempt = 0;

    while ($attempt < $maxRetries) {
        try {
            return $this->api->getSchema();
        } catch (NetworkException $e) {
            $attempt++;
            if ($attempt < $maxRetries) {
                sleep(2 * $attempt); // Exponential backoff
            }
        }
    }

    // Fallback to cache
    return Cache::get('schema_backup');
}
```
```

**Key indicator:** "TRY/RETRY" with fallback

**Example: Database Connection**
```markdown
Retry flow (handle transient failures):

Task: Connect to Database

Attempt 1: Connect
  → Timeout? Retry

Attempt 2: Connect (2s delay)
  → Timeout? Retry

Attempt 3: Connect (5s delay)
  → Timeout? Fail with error

Critical for production reliability.
```

---

## Orchestration Patterns for Common Scenarios

### Pattern A: Database-First Feature

```markdown
# Feature: Product Management

## Phase 1: Database (Sequential - Must be ordered)
1. Create products table migration
2. Create categories table migration
3. Run migrations
4. Create Product model
5. Create Category model

## Phase 2: Business Logic (Sequential after Phase 1)
6. Create ProductService
7. Create CategoryService

## Phase 3: Interfaces (Parallel - Independent)
8a. Create API endpoint ──┐
8b. Create UI component ──┼─→ Can run together
8c. Write API docs      ──┘

## Phase 4: Testing (Sequential after Phase 3)
9. Create unit tests
10. Create integration tests
```

**Orchestration used:** Sequential → Sequential → Parallel → Sequential

---

### Pattern B: API-First Feature

```markdown
# Feature: External Data Integration

## Phase 1: Research (Sequential)
1. Analyze external API
2. Document endpoints
3. Create API client

## Phase 2: Integration (Retry + Sequential)
4. Connect to API (with retry logic)
5. Transform data format
6. Store in local database

## Phase 3: Validation (Conditional)
IF data quality is low:
  → Add data cleansing step
ELSE:
  → Proceed to storage

## Phase 4: Consumption (Parallel)
7a. Expose via our API ──┐
7b. Create admin UI     ──┼─→ Independent
7c. Add to reports      ──┘
```

**Orchestration used:** Sequential → Retry → Conditional → Parallel

---

### Pattern C: Multi-Module Feature

```markdown
# Feature: Complete CRM System

## Phase 1: Core Setup (Sequential)
1. Setup base architecture
2. Create shared models
3. Configure routing

## Phase 2: Module Implementation (Looping + Parallel)
FOR EACH module in [Customers, Leads, Opportunities, Quotes]:

  Parallel per module:
  ├─ Create database schema
  ├─ Create models
  ├─ Create API endpoints
  └─ Create UI components

  Sequential per module:
  → Run module tests

## Phase 3: Integration (Sequential after all modules)
5. Connect modules (Leads → Opportunities → Quotes)
6. Add cross-module reporting
7. Full integration testing
```

**Orchestration used:** Sequential → Looping(with Parallel) → Sequential

---

## Orchestration Decision Matrix

| Scenario | Best Strategy | Why |
|----------|---------------|-----|
| **Database migrations** | Sequential | Order matters (table dependencies) |
| **API + UI development** | Parallel | Independent components |
| **Payment integration** | Conditional | Different methods per region |
| **Multi-tenant setup** | Looping | Repeat same process per tenant |
| **External API calls** | Retry | Network failures are common |
| **Test suite** | Parallel | Tests are independent |
| **Deployment** | Sequential | Steps must be ordered |
| **Data import** | Looping + Retry | Process batches, handle failures |

---

## Best Practices

### DO:
✅ **Identify dependencies first** - Know what depends on what
✅ **Parallelize when possible** - Speeds up execution 30-50%
✅ **Add retry for external deps** - Networks fail, plan for it
✅ **Use conditionals wisely** - Don't overcomplicate
✅ **Document sync points** - Where parallel tasks must wait
✅ **Plan for failures** - What happens if task fails?

### DON'T:
❌ **Parallelize dependent tasks** - Causes race conditions
❌ **Forget exit conditions** - Loops must end
❌ **Skip error handling** - Production will have failures
❌ **Over-orchestrate simple plans** - Sequential is fine for simple features
❌ **Ignore resource limits** - Can't run 100 things in parallel

---

## Implementation Plan Template with Orchestration

```markdown
# Feature: [Feature Name] — Implementation Plan

**Date:** YYYY-MM-DD
**Estimated Effort:** [Small/Medium/Large]
**Orchestration Strategy:** [Sequential/Parallel/Hybrid]

---

## Orchestration Overview

**Critical Path:** [List tasks that must be sequential]
**Parallel Opportunities:** [List tasks that can run simultaneously]
**Retry Points:** [List tasks that need retry logic]
**Conditional Branches:** [List decision points]

---

## Phase 1: [Phase Name] - [Orchestration Type]

**Strategy:** Sequential | Parallel | Conditional | Looping | Retry

### Task 1: [Task Name]

**FILE:** `path/to/file`

**ORCHESTRATION:**
- **Type:** Sequential | Parallel | Conditional | Looping | Retry
- **Depends on:** [Task IDs] or "None" or "Phase N complete"
- **Blocks:** [Task IDs] or "None"
- **Can run in parallel with:** [Task IDs] or "None"

**TASK:** [Clear action]

**CONTEXT:** [Why needed]

**CODE:**
```language
// Implementation
```

**VALIDATION:**
- [ ] Criteria 1
- [ ] Criteria 2

---

## Execution Order

**Sequential Path:**
```
Task 1 → Task 2 → Task 5 → Task 9
(30 min total)
```

**Parallel Opportunities:**
```
Task 3 ──┐
Task 4 ──┼─→ (5 min together, not 10 min sequential)
```

**Conditional Branches:**
```
IF condition A:
  → Task 6a (10 min)
ELSE:
  → Task 6b (5 min)
```

**Total Estimated Time:**
- **If all sequential:** 60 minutes
- **With orchestration:** 35 minutes (42% faster)

---

## Dependencies Graph

```
Task 1 (Foundation)
  ↓
Task 2 (Depends on Task 1)
  ↓
┌────────┬────────┐
Task 3  Task 4  Task 5  (All parallel)
└────────┴────────┘
  ↓
Task 6 (Depends on Tasks 3, 4, 5)
```

---

## Failure Handling

**Task 3 fails:**
- Tasks 4 and 5 continue (independent)
- Task 6 waits for Task 3 to be fixed

**Task 5 fails (external API):**
- Retry up to 3 times
- If all fail, use cached data
- Continue to Task 6 with degraded data

---

## Success Criteria

- [ ] All sequential tasks complete in order
- [ ] Parallel tasks complete within expected time
- [ ] Retry logic handles transient failures
- [ ] Conditional branches work correctly
- [ ] No race conditions in parallel execution
```

---

## Real-World Example: User Authentication Feature

```markdown
# Feature: User Authentication with Social Login

## Orchestration Overview

**Critical Path:** Database → Models → Core Auth → Testing
**Parallel Opportunities:** Social providers (Google, Facebook, GitHub)
**Retry Points:** External OAuth APIs
**Conditional Branches:** If social login fails, fallback to email

---

## Phase 1: Foundation (Sequential)

### Task 1: Create Database Tables
**FILE:** `database/migrations/2026_02_07_create_users_auth.php`
**DEPENDS ON:** None
**BLOCKS:** Task 2, 3

### Task 2: Create User Model
**FILE:** `app/Models/User.php`
**DEPENDS ON:** Task 1
**BLOCKS:** Task 3

### Task 3: Core Authentication Service
**FILE:** `app/Services/AuthService.php`
**DEPENDS ON:** Task 2
**BLOCKS:** Phase 2

---

## Phase 2: Social Providers (Parallel)

### Task 4a: Google OAuth
**FILE:** `app/Services/GoogleAuthProvider.php`
**DEPENDS ON:** Task 3
**CAN RUN IN PARALLEL WITH:** Task 4b, 4c
**WITH RETRY:** OAuth API might fail

### Task 4b: Facebook OAuth
**FILE:** `app/Services/FacebookAuthProvider.php`
**DEPENDS ON:** Task 3
**CAN RUN IN PARALLEL WITH:** Task 4a, 4c
**WITH RETRY:** OAuth API might fail

### Task 4c: GitHub OAuth
**FILE:** `app/Services/GitHubAuthProvider.php`
**DEPENDS ON:** Task 3
**CAN RUN IN PARALLEL WITH:** Task 4a, 4b
**WITH RETRY:** OAuth API might fail

**SYNC POINT:** All 3 providers must complete before Task 5

---

## Phase 3: Conditional Fallback

### Task 5: Fallback Strategy (Conditional)

**IF** social provider fails after retries:
  → **Task 5a:** Email/password authentication
  **FILE:** `app/Services/EmailAuthProvider.php`
  **FALLBACK:** Always available

**IF** all methods fail:
  → **Task 5b:** Show maintenance message

---

## Phase 4: Testing (Sequential after all above)

### Task 6: Create Tests
**FILE:** `tests/Feature/AuthTest.php`
**DEPENDS ON:** Phase 1, 2, 3 complete
**TESTS:** All auth paths including retries and fallbacks

---

## Execution Timeline

**Without orchestration:**
- Task 1-3: 15 minutes (sequential)
- Task 4a-c: 30 minutes (if sequential)
- Task 5: 10 minutes
- Task 6: 15 minutes
**Total: 70 minutes**

**With orchestration:**
- Task 1-3: 15 minutes (must be sequential)
- Task 4a-c: 10 minutes (parallel!)
- Task 5: 10 minutes
- Task 6: 15 minutes
**Total: 50 minutes (29% faster)**
```

---

## Summary

**Orchestration strategies for plans:**
1. **Sequential:** Use for dependent tasks (database → model → controller)
2. **Parallel:** Use for independent tasks (API + UI + docs)
3. **Conditional:** Use for different paths (external API vs CSV vs manual)
4. **Looping:** Use for repeated processes (multi-module, multi-tenant)
5. **Retry:** Use for unreliable operations (external APIs, network calls)

**Benefits:**
- **30-50% faster** execution (with parallelization)
- **Better coordination** (clear dependencies)
- **More reliable** (retry + fallback strategies)
- **Easier to execute** (agents/developers know what to do when)

**Impact:**
- Plans are **clearer** (orchestration makes flow explicit)
- Execution is **faster** (parallel where possible)
- Failures are **handled** (retry + fallback built-in)
- Teams are **coordinated** (know who does what when)

---

**See also:**
- `../../orchestration-patterns-reference.md` - Complete orchestration guide
- `prompting-patterns.md` - For creating better task instructions
- `../SKILL.md` - Feature planning skill documentation

**Last Updated:** 2026-02-07
