# Orchestration Strategies for AI-Assisted Development

**Purpose:** Learn the 5 core strategies for coordinating multiple AI agents in software development workflows

**Parent Skill:** ai-assisted-development

---

## Strategy 1: Sequential AI Workflow

**Use when:** Each AI agent needs previous agent's output

**Pattern:**
```
Agent 1 (Planning) → Output: Spec
    ↓
Agent 2 (Coding) → Input: Spec, Output: Code
    ↓
Agent 3 (Testing) → Input: Code, Output: Tests
    ↓
Agent 4 (Review) → Input: Spec + Code + Tests, Output: Feedback
```

**Example: Feature Development**

### Phase 1: Planning (Agent: Claude in Plan Mode)
**Prompt:**
```markdown
"Create a detailed specification for user authentication.

CONTEXT: Multi-tenant SaaS
CONSTRAINTS:
- JWT authentication
- Session management
- RBAC support

RETURN as structured spec with:
- User stories
- Acceptance criteria
- Data model
- API endpoints"
```

**Output:** `docs/specs/auth-spec.md`

### Phase 2: Implementation (Agent: Claude in Code Mode)
**Prompt:**
```markdown
"Implement user authentication using the specification.

FILE TO READ: docs/specs/auth-spec.md

CONTEXT: Read the spec and implement EXACTLY as specified.
ORCHESTRATION: This is Phase 2 of the pipeline (depends on Phase 1 spec).

CONSTRAINTS:
- Follow Laravel conventions
- Write complete code (no placeholders)
- Include error handling"
```

**Output:** Code files created per spec

### Phase 3: Testing (Agent: Claude in Test Mode)
**Prompt:**
```markdown
"Create comprehensive tests for user authentication.

FILES TO READ:
- docs/specs/auth-spec.md (what to test)
- app/Http/Controllers/AuthController.php (what code to test)

ORCHESTRATION: This is Phase 3 (depends on Phase 1 spec + Phase 2 code).

CREATE tests for:
- Registration flow
- Login flow
- Token validation
- Session management"
```

**Output:** Test files

### Phase 4: Review (Agent: Claude in Review Mode)
**Prompt:**
```markdown
"Review the authentication implementation.

FILES TO READ:
- docs/specs/auth-spec.md (requirements)
- app/Http/Controllers/AuthController.php (implementation)
- tests/Feature/AuthTest.php (tests)

ORCHESTRATION: This is Phase 4 (final review after all work done).

CHECK:
- Spec compliance
- Code quality
- Test coverage
- Security concerns"
```

**Output:** Review report with findings

**Total Time:** 60 minutes (15 + 25 + 15 + 5)

---

## Strategy 2: Parallel AI Execution

**Use when:** AI agents work on independent components

**Pattern:**
```
                ┌─→ Agent 2a: Backend Code ──┐
Agent 1 (Spec) ─┼─→ Agent 2b: Frontend Code ──┼─→ Agent 3 (Integration)
                └─→ Agent 2c: Documentation ──┘
```

**Example: Full-Stack Feature Development**

### Phase 1: Specification (Sequential)
**Agent: Planning Agent**
```markdown
"Create specification for product catalog feature.

OUTPUT: docs/specs/product-catalog.md
INCLUDE:
- Backend API endpoints
- Frontend UI requirements
- Documentation needs"
```

**Output:** Spec defining all three components

### Phase 2: Implementation (Parallel - 3x faster!)

#### Agent 2a: Database Agent (Parallel)
```markdown
"Create database schema for product catalog.

READ: docs/specs/product-catalog.md
FOCUS: Only database (tables, indexes, constraints)
ORCHESTRATION: Can run in PARALLEL with Agents 2b and 2c

OUTPUT:
- Migration file
- Model file"
```

**Time:** 20 minutes

#### Agent 2b: API Agent (Parallel)
```markdown
"Create API endpoints for product catalog.

READ: docs/specs/product-catalog.md
FOCUS: Only API layer (controllers, routes, validation)
ORCHESTRATION: Can run in PARALLEL with Agents 2a and 2c

OUTPUT:
- Controllers
- Routes
- API tests"
```

**Time:** 20 minutes

#### Agent 2c: UI Agent (Parallel)
```markdown
"Create frontend components for product catalog.

READ: docs/specs/product-catalog.md
FOCUS: Only UI components (React/Vue)
ORCHESTRATION: Can run in PARALLEL with Agents 2a and 2b

OUTPUT:
- Product list component
- Product detail component
- Add/Edit forms"
```

**Time:** 20 minutes

**Parallel Execution:** All 3 agents run simultaneously = 20 minutes total
**Sequential would be:** 20 + 20 + 20 = 60 minutes
**Savings:** 67% faster (40 minutes saved!)

### Phase 3: Integration (Sequential after Phase 2)
**Agent: Integration Agent**
```markdown
"Integrate all product catalog components.

READ:
- Database migrations (Agent 2a output)
- API controllers (Agent 2b output)
- UI components (Agent 2c output)

ORCHESTRATION: This is Phase 3 (runs AFTER all Phase 2 agents complete).

TASKS:
- Wire UI to API
- Test end-to-end flow
- Fix integration issues"
```

**Time:** 15 minutes

**Total Time:** 20 (parallel) + 15 (integration) = 35 minutes
**vs Sequential:** 60 + 15 = 75 minutes
**Improvement:** 53% faster

---

## Strategy 3: Conditional AI Routing

**Use when:** Different AI agents handle different project types

**Pattern:**
```
Analyze Project
  │
  ├─ IF (legacy codebase) → Refactoring Agent
  ├─ ELIF (greenfield) → Architecture Agent
  ├─ ELIF (API integration) → Integration Agent
  └─ ELSE → Ask human
```

**Example: Project Documentation**

### Phase 1: Project Analysis
**Agent: Analysis Agent**
```markdown
"Analyze this project and determine documentation needs.

SCAN:
- README.md
- Tech stack
- Existing docs/

RETURN:
- Project type (API, Full-Stack, CLI, Library)
- Current documentation state
- Recommended documentation strategy"
```

**Output:** Analysis report with routing decision

### Phase 2: Documentation (Conditional)

**IF project type = "API":**
```markdown
Agent: API Documentation Agent

"Generate OpenAPI/Swagger documentation.

ORCHESTRATION: Conditional path for API projects only.

SCAN:
- Routes
- Controllers
- Request/Response schemas

OUTPUT: docs/api-spec.yaml"
```

**ELIF project type = "Full-Stack":**
```markdown
Agent: Full-Stack Documentation Agent

"Generate comprehensive docs for full-stack app.

ORCHESTRATION: Conditional path for full-stack projects only.

GENERATE:
- Architecture diagram (HLD)
- Database schema docs
- API documentation
- Frontend component docs
- Deployment guide

OUTPUT: Complete docs/ directory"
```

**ELIF project type = "CLI":**
```markdown
Agent: CLI Documentation Agent

"Generate CLI tool documentation.

ORCHESTRATION: Conditional path for CLI tools only.

GENERATE:
- Command reference
- Installation guide
- Usage examples
- Troubleshooting

OUTPUT: Complete CLI manual"
```

**ELSE:**
```markdown
Human intervention: Ask user what type of documentation they need.
```

**Benefits:**
- Right agent for the job (specialized expertise)
- No wasted effort on irrelevant docs
- Faster execution (focused scope)

---

## Strategy 4: Looping AI Iteration

**Use when:** AI agent needs to refine output until quality threshold met

**Pattern:**
```
┌──────────────────┐
│ Agent generates  │
│ output           │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Quality check    │◄──┐
│ Passes? Y/N      │   │
└────────┬─────────┘   │
         │             │
    ┌────┴────┐        │
    │ NO      │ YES    │
    ▼         ▼        │
 Refine    Done     Loop back
 again               (max 3×)
    └────────────────┘
```

**Example: Code Generation with Quality Loop**

### Phase: Code Generation with Quality Loop

**Iteration 1:**
```markdown
Agent: Code Generator

"Generate user registration endpoint.

REQUIREMENTS:
- Email validation
- Password hashing
- Duplicate email check
- Return JWT token

QUALITY CRITERIA:
- PSR-12 code style
- 100% test coverage
- Zero security vulnerabilities
- Clear error messages"
```

**Quality Check (Automated):**
```bash
php -l file.php          # Syntax check
phpcs file.php           # Code style
phpstan analyze          # Static analysis
phpunit tests/           # Test coverage
```

**IF quality < 100%:**
→ Loop back to Code Generator with error feedback

**Iteration 2 (if needed):**
```markdown
Agent: Code Generator

"Fix the following issues in registration endpoint:

FAILED CHECKS:
- Code style: Missing return types
- Security: Password minimum length not enforced
- Test: Edge case missing (empty email)

REFINE the code to fix these issues."
```

**Quality Check Again:**
```bash
[Run same checks]
```

**IF quality = 100%:**
→ Done! Move to next phase

**Max iterations:** 3 (prevent infinite loops)

**Exit condition:** Quality >= 100% OR iterations >= 3

**Benefits:**
- Ensures high-quality output
- Iterative refinement (like human review)
- Automated quality gates
- Prevents shipping bad code

---

## Strategy 5: Retry with Fallback

**Use when:** AI agent might fail due to external dependencies

**Pattern:**
```
Attempt 1 → Success? YES → Done
            ↓ FAIL
Attempt 2 → Success? YES → Done
            ↓ FAIL
Attempt 3 → Success? YES → Done
            ↓ FAIL
Fallback strategy → Done (degraded mode)
```

**Example: External API Integration**

### Phase: Fetch and Document External API

**Attempt 1:**
```markdown
Agent: API Integration Agent

"Fetch OpenAPI spec from external API and generate client code.

API URL: https://api.external.com/openapi.json

ORCHESTRATION: This may fail (network/auth issues). Retry up to 3 times.

GENERATE:
- API client class
- Request/Response models
- Usage documentation"
```

**Possible failures:**
- Network timeout
- Authentication error
- Rate limit exceeded

**IF FAIL → Wait 5 seconds → Retry**

**Attempt 2:**
```markdown
[Same prompt]

RETRY CONTEXT: Previous attempt failed with [error]. Trying again with longer timeout.
```

**IF FAIL → Wait 10 seconds → Retry**

**Attempt 3:**
```markdown
[Same prompt]

RETRY CONTEXT: Second attempt failed. This is final attempt before fallback.
```

**IF FAIL → Fallback:**

**Fallback Strategy:**
```markdown
Agent: Fallback Documentation Agent

"External API fetch failed after 3 attempts.

FALLBACK TASK:
1. Use cached OpenAPI spec (if available)
2. Generate basic client code with TODOs
3. Document manual steps for user to complete

OUTPUT:
- Partial client code
- Manual integration guide
- Troubleshooting steps"
```

**Benefits:**
- Handles transient failures gracefully
- Doesn't give up immediately
- Provides degraded functionality if needed
- User still gets value (partial output + guide)

**Best Practices:**
- Exponential backoff (5s, 10s, 20s)
- Max 3 retries (prevent infinite loops)
- Always have fallback plan
- Log all attempts for debugging

---

## Combining Strategies

**Real-world projects use MULTIPLE strategies together.**

**Example: Complete Feature Development**

```
Phase 1: Planning (Sequential)
  → Agent: Planning Agent

Phase 2: Implementation (Parallel)
  ├─→ Agent 2a: Database
  ├─→ Agent 2b: API
  └─→ Agent 2c: UI

Phase 3: Quality Loop (Looping)
  → Agent: Code Review Agent
  → LOOP until quality >= 90%

Phase 4: Integration (Sequential)
  → Agent: Integration Agent

Phase 5: External Deps (Retry)
  → Agent: API Integration Agent
  → RETRY up to 3 times
  → FALLBACK if all fail

Phase 6: Documentation (Conditional)
  → IF (API project) → API Docs Agent
  → ELIF (Full-Stack) → Full-Stack Docs Agent
```

**Total strategies used:** All 5 (Sequential + Parallel + Looping + Retry + Conditional)

**Result:** Robust, efficient, high-quality AI-assisted development

---

## Summary

**The 5 Strategies:**

1. **Sequential:** One agent after another (most common, simple, reliable)
2. **Parallel:** Multiple agents simultaneously (50-70% faster)
3. **Conditional:** Different agents for different scenarios (smart routing)
4. **Looping:** Iterate until quality threshold (ensure high quality)
5. **Retry:** Handle failures gracefully (external dependencies)

**When to use each:**

| Strategy      | Use When                                          | Benefit                 |
|---------------|---------------------------------------------------|-------------------------|
| Sequential    | Each agent needs previous output                  | Simple, predictable     |
| Parallel      | Agents work on independent components             | 50-70% faster           |
| Conditional   | Different project types need different approaches | Right tool for job      |
| Looping       | Output quality must meet threshold                | High-quality output     |
| Retry         | External dependencies might fail                  | Graceful error handling |

**Combine strategies** for complex projects to get benefits of all.

---

**See also:**
- `../SKILL.md` - Main AI-assisted development skill
- `ai-patterns.md` - AI-specific orchestration patterns
- `practical-examples.md` - Real-world MADUUKA and BRIGHTSOMA examples
- `../../orchestration-patterns-reference.md` - General orchestration guide
- `../../prompting-patterns-reference.md` - Better AI prompts

**Last Updated:** 2026-02-07
