# Practical AI Orchestration Examples

**Purpose:** Real-world examples of AI agent orchestration using actual student projects

**Parent Skill:** ai-assisted-development

---

## Overview

This guide shows **real AI orchestration** applied to two actual applications:

1. **MADUUKA:** Franchise inventory synchronization system
2. **BRIGHTSOMA:** AI-powered exam generation platform

Both examples use multiple AI agents coordinated through orchestration patterns.

---

## Example 1: MADUUKA - Franchise Inventory Sync

**Project:** Multi-tenant franchise inventory management
**Challenge:** Sync inventory across multiple franchise locations
**AI Orchestration Used:** Sequential + Parallel + Human-in-the-Loop

### Business Context

**Problem:**
- Multiple franchise locations
- Each has own inventory
- Need to sync stock levels across locations
- Handle conflicts (same item updated at 2 locations)
- Track inventory movements between franchises

**Technical Requirements:**
- Multi-tenant database (tenant isolation)
- Real-time sync (webhooks or polling)
- Conflict resolution (last-write-wins vs manual)
- Audit trail (who moved what when)
- API for mobile app

### AI Orchestration Workflow

#### Agent 1: Requirements Agent (Sequential)
**Prompt:**
```markdown
"Analyze franchise inventory sync requirements and create technical specification.

BUSINESS CONTEXT:
- Multi-tenant SaaS (each franchise = tenant)
- Inventory items have: SKU, quantity, location_id, tenant_id
- Sync scenarios:
  1. Location A updates quantity → sync to central DB
  2. Location B requests item → check all locations
  3. Transfer: Location A → Location B (decrement A, increment B)

TECHNICAL CONSTRAINTS:
- MySQL 8.x with tenant_id in all tables
- Laravel 10 backend
- Real-time sync (max 5 second delay)
- Conflict resolution: last-write-wins + log conflicts

OUTPUT: Create structured spec with:
- Data model (tables, columns, indexes, relationships)
- Sync algorithm (step-by-step logic)
- API endpoints (routes, requests, responses)
- Conflict resolution rules
- Audit trail requirements

FILE: docs/specs/inventory-sync-spec.md"
```

**Output:** `docs/specs/inventory-sync-spec.md` (comprehensive specification)

**Time:** 15 minutes

**[GATE 1: Human Review]**
- **Check:** Is the data model correct? Tenant isolation enforced?
- **Check:** Does sync algorithm handle conflicts properly?
- **Decision:** ✅ Approved (or ❌ Revise spec)

---

#### Agents 2a, 2b, 2c: Implementation (Parallel)

**Now that spec is approved, spawn 3 agents to work in parallel:**

##### Agent 2a: Database Agent
**Prompt:**
```markdown
"Create database schema for inventory sync.

READ: docs/specs/inventory-sync-spec.md

FOCUS: Database layer only (migrations, models, stored procedures)

ORCHESTRATION: This runs in PARALLEL with Agents 2b and 2c

CREATE:
1. Migration: inventory_items table
   - Columns: id, tenant_id, sku, name, quantity, location_id, updated_at
   - Indexes: (tenant_id, sku), (location_id), (updated_at)
   - Constraints: quantity >= 0, foreign keys

2. Migration: inventory_movements table (audit trail)
   - Columns: id, tenant_id, item_id, from_location_id, to_location_id, quantity, moved_by, moved_at
   - Indexes: (tenant_id, moved_at), (item_id)

3. Model: InventoryItem.php (with tenant scope)
4. Model: InventoryMovement.php (with tenant scope)
5. Stored procedure: sp_transfer_inventory (atomic transfer)

CONSTRAINTS:
- Tenant isolation (tenant_id in all queries)
- Foreign keys with CASCADE
- Timestamps for audit trail

FILES:
- database/migrations/YYYY_MM_DD_create_inventory_tables.php
- app/Models/InventoryItem.php
- app/Models/InventoryMovement.php
- database/procedures/sp_transfer_inventory.sql"
```

**Time:** 20 minutes

---

##### Agent 2b: API Agent
**Prompt:**
```markdown
"Create API endpoints for inventory sync.

READ: docs/specs/inventory-sync-spec.md

FOCUS: API layer only (controllers, routes, requests, validation)

ORCHESTRATION: This runs in PARALLEL with Agents 2a and 2c

CREATE:
1. POST /api/inventory/sync
   - Receives inventory updates from franchise location
   - Validates tenant_id, location_id, SKU, quantity
   - Detects conflicts (compare updated_at)
   - Logs conflict if detected
   - Updates inventory
   - Returns success/conflict response

2. GET /api/inventory/availability/{sku}
   - Returns item availability across all locations for tenant
   - Aggregates quantity from all locations
   - Returns per-location breakdown

3. POST /api/inventory/transfer
   - Transfers inventory between locations
   - Validates: from_location has sufficient quantity
   - Uses sp_transfer_inventory (atomic)
   - Creates audit trail (inventory_movements)
   - Returns success/failure

CONSTRAINTS:
- Tenant isolation (all queries scoped to tenant_id)
- Input validation (Laravel FormRequest)
- JSON responses (consistent format)
- Error handling (422 for validation, 409 for conflicts)

FILES:
- app/Http/Controllers/Api/InventoryController.php
- app/Http/Requests/InventorySyncRequest.php
- app/Http/Requests/InventoryTransferRequest.php
- routes/api.php (register routes)"
```

**Time:** 20 minutes

---

##### Agent 2c: Testing Agent
**Prompt:**
```markdown
"Create comprehensive tests for inventory sync.

READ: docs/specs/inventory-sync-spec.md

FOCUS: Tests only (unit + integration)

ORCHESTRATION: This runs in PARALLEL with Agents 2a and 2b

CREATE:
1. Unit tests for InventoryItem model
   - Test tenant scoping
   - Test relationships
   - Test validation rules

2. Unit tests for InventoryMovement model
   - Test audit trail creation
   - Test relationships

3. Integration tests for inventory sync API
   - Test scenario: Location A syncs quantity → DB updated
   - Test scenario: Conflict detected → logged + last-write-wins
   - Test scenario: Transfer A → B → quantities updated atomically
   - Test scenario: Availability check → correct aggregation
   - Test scenario: Tenant isolation → Tenant A cannot see Tenant B data

4. Test edge cases
   - Negative quantity (should fail)
   - Transfer more than available (should fail)
   - Concurrent updates (conflict resolution)
   - Non-existent SKU (should create or fail based on spec)

CONSTRAINTS:
- Use Laravel factories for test data
- Use database transactions (rollback after each test)
- Test both success and failure paths
- Assert: HTTP status codes, JSON structure, database state

FILES:
- tests/Unit/Models/InventoryItemTest.php
- tests/Unit/Models/InventoryMovementTest.php
- tests/Feature/Api/InventorySyncTest.php
- database/factories/InventoryItemFactory.php"
```

**Time:** 20 minutes

---

**Parallel Execution:**
- All 3 agents (2a, 2b, 2c) run simultaneously
- Total time: **20 minutes** (not 60!)
- **Speedup:** 67% faster than sequential

---

#### Agent 3: Testing Agent (Sequential after Agent 2)
**Prompt:**
```markdown
"Run all tests and verify inventory sync implementation.

ORCHESTRATION: This runs AFTER Agents 2a, 2b, 2c complete (sequential).

TASK:
1. Run migrations: php artisan migrate
2. Run all tests: php artisan test --filter=Inventory
3. Check coverage: php artisan test --coverage
4. Verify: All tests pass, >80% coverage

IF tests fail:
  - Report failures to human
  - Human reviews and decides: fix or revise spec

IF tests pass:
  - Generate test report
  - Mark phase complete

FILE: docs/reports/inventory-sync-test-report.md"
```

**Time:** 10 minutes

**[GATE 2: Human Review]**
- **Check:** All tests passing? Coverage sufficient?
- **Check:** Edge cases handled correctly?
- **Decision:** ✅ Approved for production | ❌ Fix issues

---

#### Agent 4: Review Agent (Sequential after Agent 3)
**Prompt:**
```markdown
"Review entire inventory sync implementation for quality and security.

READ:
- docs/specs/inventory-sync-spec.md (requirements)
- database/migrations/ (database implementation)
- app/Models/ (models)
- app/Http/Controllers/Api/InventoryController.php (API)
- tests/ (test coverage)
- docs/reports/inventory-sync-test-report.md (test results)

ORCHESTRATION: This is final review phase (sequential after all work done).

CHECK:
1. Spec compliance: Does code match spec?
2. Tenant isolation: Is tenant_id enforced everywhere?
3. Security: SQL injection risks? XSS? CSRF?
4. Performance: Are indexes correct? N+1 queries?
5. Error handling: All edge cases handled?
6. Code quality: PSR-12? Type hints? Docblocks?
7. Tests: Coverage sufficient? Edge cases tested?

RETURN:
- Compliance report (spec vs implementation)
- Security findings (critical, high, medium, low)
- Performance recommendations
- Code quality score (0-100)
- Approval: YES/NO with rationale

FILE: docs/reports/inventory-sync-review-report.md"
```

**Time:** 15 minutes

**[GATE 3: Final Human Review]**
- **Check:** Review agent findings acceptable?
- **Decision:** ✅ Ship to production | ❌ Address critical findings

---

### Total Time Breakdown

| Phase                  | Strategy    | Time       | Notes                          |
|------------------------|-------------|------------|--------------------------------|
| Agent 1: Requirements  | Sequential  | 15 min     | Must complete before Phase 2   |
| [GATE 1: Human Review] | -           | 5 min      | Approve spec                   |
| Agents 2a, 2b, 2c      | Parallel    | 20 min     | All run simultaneously         |
| Agent 3: Testing       | Sequential  | 10 min     | After Phase 2 complete         |
| [GATE 2: Human Review] | -           | 5 min      | Approve tests                  |
| Agent 4: Review        | Sequential  | 15 min     | Final quality check            |
| [GATE 3: Human Review] | -           | 5 min      | Final approval                 |
| **TOTAL**              | -           | **75 min** | 1 hour 15 minutes              |

**If all sequential:** 15 + 20 + 20 + 20 + 10 + 15 = 100 minutes + 15 min reviews = **115 minutes**

**With orchestration:** **75 minutes**

**Savings:** 40 minutes (35% faster)

---

## Example 2: BRIGHTSOMA - AI Exam Question Generation

**Project:** AI-powered exam generation for teachers
**Challenge:** Generate high-quality exam questions from curriculum content
**AI Orchestration Used:** Looping + Retry + Human-in-the-Loop

### Business Context

**Problem:**
- Teachers need exam questions based on curriculum
- Questions must be: relevant, appropriate difficulty, no duplicates
- Support multiple question types (MCQ, True/False, Short Answer, Essay)
- Questions must be tagged (topic, difficulty, bloom's taxonomy level)
- Generate answer keys and rubrics

**Technical Requirements:**
- AI generates questions (GPT-4, Claude, or Gemini)
- Quality validation (relevance, grammar, difficulty)
- Deduplication (no repeated questions)
- Export to PDF (formatted exam + answer key)

### AI Orchestration Workflow

#### Agent 1: Question Generator (Looping)
**Prompt:**
```markdown
"Generate exam questions from curriculum content.

CONTEXT:
- Subject: Biology
- Topic: Cell Biology (Mitosis and Meiosis)
- Target: Grade 10 students
- Difficulty: Medium
- Question types: 10 MCQ + 5 Short Answer + 2 Essay

READ: curriculum/biology/cell-biology.md

ORCHESTRATION: Looping agent (generate questions iteratively until quality threshold met)

FOR EACH question type:
  1. Read curriculum content
  2. Generate question + answer + rubric
  3. Tag: topic, difficulty (1-5), bloom's level (Remember/Understand/Apply/Analyze)
  4. Check quality (Agent 2 validates)
  5. IF quality < 80% → regenerate (max 3 attempts)
  6. IF quality >= 80% → accept and continue

CONSTRAINTS:
- No duplicate questions (check against existing)
- Questions must reference specific curriculum concepts
- MCQ: 4 options, 1 correct
- Short Answer: 2-3 sentence expected answer
- Essay: Clear rubric (5 points breakdown)

OUTPUT:
- questions.json (structured format)
- Contains: question_id, type, question_text, options (MCQ), correct_answer, rubric, tags

QUALITY CRITERIA:
- Relevance: Does question test curriculum concept? (Yes/No)
- Clarity: Is question unambiguous? (Yes/No)
- Difficulty: Matches target level? (Yes/No)
- Grammar: No errors? (Yes/No)

Quality = (Relevance + Clarity + Difficulty + Grammar) / 4 * 100%
Accept if >= 80%"
```

**Looping Execution:**

```
Iteration 1: Generate Question 1
  → Send to Agent 2 (Validator)
  → Quality = 90% → ACCEPT

Iteration 2: Generate Question 2
  → Send to Agent 2 (Validator)
  → Quality = 65% (poor clarity) → REJECT
  → Regenerate with feedback: "Improve clarity - question is ambiguous"
  → Quality = 85% → ACCEPT

... (continue for all 17 questions)

Exit conditions:
- All 17 questions accepted (quality >= 80%), OR
- Max 3 regeneration attempts per question, OR
- Human intervention requested (if quality consistently low)
```

**Time:** 30 minutes (with looping iterations)

---

#### Agent 2: Validator (Quality Check)
**Prompt:**
```markdown
"Validate exam question quality.

ORCHESTRATION: Validation agent called by Agent 1 (looping pattern)

INPUT: Single question (JSON)

VALIDATE:
1. Relevance: Check question against curriculum/biology/cell-biology.md
   - Does it test a concept from curriculum? (Yes/No)
   - Which concept? (name it)

2. Clarity: Analyze question text
   - Is wording clear and unambiguous? (Yes/No)
   - Any confusing phrasing? (list issues if any)

3. Difficulty: Estimate difficulty
   - Is it appropriate for Grade 10? (Yes/No)
   - Estimated difficulty: 1-5 (where 3 = medium)
   - Does it match target difficulty (medium)? (Yes/No)

4. Grammar: Check for errors
   - Any grammar/spelling errors? (Yes/No)
   - List errors if found

5. For MCQ: Check options
   - Are all 4 options plausible? (Yes/No)
   - Is correct answer actually correct? (Yes/No)
   - Are distractors reasonable? (Yes/No)

SCORING:
- Relevance: 25 points
- Clarity: 25 points
- Difficulty match: 25 points
- Grammar: 25 points
Total: 0-100

RETURN:
{
  "quality_score": 85,
  "passed": true,  // true if >= 80
  "feedback": {
    "relevance": "Tests mitosis phases - GOOD",
    "clarity": "Slightly ambiguous wording in option C",
    "difficulty": "Appropriate for Grade 10",
    "grammar": "No errors"
  },
  "action": "ACCEPT" // or "REVISE"
}"
```

**Time:** 2 minutes per question

---

#### Exit Conditions:

**WHEN to stop looping:**

1. **Success:** All questions meet quality threshold (>= 80%)
2. **Max attempts:** Question regenerated 3 times but still < 80% → flag for human review
3. **Human intervention:** Human manually reviews flagged questions and decides (accept/reject/edit)

---

#### Agent 3: Rubric Generator (Sequential)
**Prompt:**
```markdown
"Generate grading rubrics for short answer and essay questions.

READ: questions.json (Agent 1 output - accepted questions only)

ORCHESTRATION: Sequential (runs AFTER Agent 1 complete)

FOR EACH short answer question:
  CREATE rubric:
  - 2 points: Correct concept identified
  - 1 point: Partial understanding
  - 0 points: Incorrect or missing

FOR EACH essay question:
  CREATE detailed rubric (5 points total):
  - 1 point: Introduction (clear thesis)
  - 2 points: Body (supporting arguments with evidence)
  - 1 point: Conclusion (summary + insights)
  - 1 point: Grammar and organization

OUTPUT: rubrics.json"
```

**Time:** 10 minutes

---

#### Agent 4: PDF Generator (Sequential)
**Prompt:**
```markdown
"Generate formatted exam and answer key as PDFs.

READ:
- questions.json (all questions)
- rubrics.json (grading rubrics)

ORCHESTRATION: Sequential (runs AFTER Agents 1, 2, 3 complete)

GENERATE:
1. exam.pdf:
   - Header: School name, subject, date, student name field
   - Questions grouped by type (MCQ, Short Answer, Essay)
   - Clear numbering
   - Space for answers
   - Professional formatting

2. answer_key.pdf:
   - All correct answers
   - Rubrics for subjective questions
   - Point allocation
   - Marking guidance

CONSTRAINTS:
- Use LaTeX for formatting
- Professional layout (margins, fonts, spacing)
- Print-friendly (black and white)

OUTPUT:
- exams/biology-cell-biology-exam.pdf
- exams/biology-cell-biology-answer-key.pdf"
```

**Time:** 5 minutes

---

### Error Handling (Retry Strategy)

**What if AI model fails or times out?**

```
Attempt 1: Call AI API to generate question
  → Timeout (30 seconds elapsed)

  RETRY (wait 5 seconds)

Attempt 2: Call AI API again
  → API rate limit exceeded (429 error)

  RETRY (wait 30 seconds - longer backoff)

Attempt 3: Call AI API again
  → Success! Question generated

IF all 3 attempts fail:
  FALLBACK: Use template-based question generation
  - Less sophisticated, but guarantees output
  - Flag questions as "template-generated" for human review
```

---

### Total Time Breakdown

| Phase                 | Strategy    | Time       | Notes                              |
|-----------------------|-------------|------------|------------------------------------|
| Agent 1: Generator    | Looping     | 30 min     | 17 questions with quality loops    |
| Agent 2: Validator    | (embedded)  | -          | Called by Agent 1 (included above) |
| Agent 3: Rubrics      | Sequential  | 10 min     | After questions finalized          |
| Agent 4: PDF Export   | Sequential  | 5 min      | Final output generation            |
| **TOTAL**             | -           | **45 min** | Includes retries and iterations    |

**Manual (teacher creates questions):** 2-3 hours

**With AI orchestration:** 45 minutes

**Savings:** 135 minutes (75% faster) + higher quality (validated)

---

## Key Takeaways from Both Examples

### MADUUKA (Inventory Sync)
**Orchestration strategies used:**
- ✅ Sequential (Requirements → Implementation → Testing → Review)
- ✅ Parallel (Database + API + Tests simultaneously)
- ✅ Human-in-the-Loop (3 approval gates)

**Result:** 75 minutes (vs 115 sequential) = **35% faster**

### BRIGHTSOMA (Exam Generation)
**Orchestration strategies used:**
- ✅ Looping (Generate questions until quality threshold met)
- ✅ Retry (Handle AI API failures gracefully)
- ✅ Sequential (Generator → Rubrics → PDF)

**Result:** 45 minutes (vs 180 manual) = **75% faster** + higher quality

---

## Practical Tips

### When Orchestrating AI Agents:

1. **Break work into focused agents:** Each agent does ONE job well
2. **Parallelize when possible:** Database + API + Tests = 3x faster
3. **Add quality loops:** Don't accept poor output, regenerate
4. **Include human gates:** High-risk work needs human approval
5. **Handle failures gracefully:** Retry with backoff, have fallbacks
6. **Provide clear context:** Each agent gets spec, input files, orchestration info
7. **Log everything:** Agent interactions, decisions, outputs

### Common Pitfalls:

❌ **Over-orchestrating simple tasks:** Sometimes 1 agent is enough
❌ **Parallelizing dependent work:** Causes race conditions and errors
❌ **No quality validation:** Accepting poor AI output
❌ **Infinite loops:** Always set max iterations and exit conditions
❌ **No fallback plans:** When AI fails, have degraded mode

---

## Summary

**Real-world AI orchestration delivers:**
- **30-75% faster** development (parallelization + automation)
- **Higher quality** output (validation loops, human gates)
- **Better consistency** (AI follows patterns reliably)
- **Reduced errors** (validation catches issues early)

**Key principle:** Right agent, right task, clear coordination, human oversight

---

**See also:**
- `../SKILL.md` - Main AI-assisted development skill
- `orchestration-strategies.md` - The 5 orchestration strategies
- `ai-patterns.md` - AI-specific orchestration patterns
- `../../feature-planning/SKILL.md` - Creating implementation plans
- `../../prompting-patterns-reference.md` - Better AI prompts

**Last Updated:** 2026-02-07
