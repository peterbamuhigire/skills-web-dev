# Orchestration Patterns for Multi-Agent Workflows

**Purpose:** Guide for coordinating multiple AI agents or skills to work together effectively

**Target Audience:** Skills that manage complex workflows with multiple agents/steps

---

## What is Orchestration?

**Orchestration** is the art of managing multiple agents/skills to work together in a coordinated, intelligent way.

Think of it like a **musical orchestra**:
- **Without conductor:** Everyone plays alone, chaos, no timing
- **With conductor:** Everyone knows when to play, synchronized, beautiful music

**In software/AI workflows:**
- **Without orchestration:** Agents run independently, conflicts, repeated work
- **With orchestration:** Coordinated execution, optimized flow, efficient results

---

## Core Concepts

### 1. Agent (Specialized Worker)
An **agent** is a specialized worker that does ONE job well.

**Examples:**
- Planning Agent: Analyzes requirements and creates plans
- Data Agent: Loads and processes data
- Validation Agent: Checks quality and correctness
- Reporting Agent: Formats and exports results

**Principle:** Each agent has ONE responsibility (Single Responsibility Principle)

### 2. Orchestrator (Conductor)
An **orchestrator** decides:
- **WHO** does what (which agent)
- **WHEN** they do it (execution order)
- **WHAT** order (dependencies)
- **WHAT** if something fails (error handling)

### 3. Workflow (Execution Sequence)
A **workflow** is the SEQUENCE of steps agents execute.

```
Start → Planning Agent → Data Agent → Validation Agent → Reporting Agent → End
```

### 4. Execution Strategy
**HOW** you run the workflow:
- **Sequential:** One after another (simple, reliable)
- **Parallel:** Multiple at once (fast, complex)
- **Conditional:** "If this, then that" (flexible)
- **Looping:** Repeat until condition (batch processing)
- **Retry:** Try again if fails (fault tolerance)

---

## The 5 Orchestration Types

### Type 1: Sequential (One After Another)

**When to use:** Steps MUST happen in order

**Characteristics:**
- ✅ Simple to understand and debug
- ✅ Reliable and predictable
- ❌ Slower (steps wait for each other)
- ❌ No parallelization

**Pattern:**
```
STEP 1 → STEP 2 → STEP 3 → STEP 4 → STEP 5
(5 min) (10 min) (15 min) (5 min)  (5 min)
Total: 40 minutes
```

**Example: SRS Generation (Waterfall Pipeline)**
```
01-initialize-srs → 02-context-engineering → 03-descriptive-modeling →
04-interface-specification → 05-feature-decomposition → 06-logic-modeling →
07-attribute-mapping → 08-semantic-auditing

Each phase MUST complete before next begins.
```

**When to use in skills:**
- SRS generation (phases must be sequential)
- Database migrations (schema changes must be ordered)
- Deployment workflows (setup before deploy)

---

### Type 2: Parallel (Multiple at Once)

**When to use:** Steps DON'T depend on each other

**Characteristics:**
- ✅ Fast (runs simultaneously)
- ✅ Efficient use of resources
- ❌ More complex coordination
- ❌ Need synchronization at end

**Pattern:**
```
STEP 1a: Load user data      (5 min) ──┐
STEP 1b: Load product data   (5 min) ──┼─→ All run together
STEP 1c: Load order data     (5 min) ──┘
         │
         ▼ (all done after 5 mins)
STEP 2: Combine and validate (10 min)
Total: 5 + 10 = 15 minutes (not 30!)
```

**Example: Multi-Document Generation**
```
Generate in parallel:
├─ HLD (High-Level Design)
├─ API Specification
├─ Database Schema Docs
└─ Test Strategy

Then combine into unified architecture document.
```

**When to use in skills:**
- Generating multiple independent documents
- Loading data from multiple sources
- Running independent validations

---

### Type 3: Conditional (Smart Decisions)

**When to use:** Different paths based on conditions

**Characteristics:**
- ✅ Flexible and adaptive
- ✅ Handles different scenarios
- ❌ Harder to debug
- ❌ Complex branching logic

**Pattern:**
```
Input
  │
  ├─ Condition A? YES → Path A
  │              NO  → Continue
  │
  ├─ Condition B? YES → Path B
  │              NO  → Path C
  │
  ▼
Output
```

**Example: Methodology Selection (Phase 00)**
```
Analyze project
  │
  ├─ Regulated industry? YES → Recommend Waterfall
  │                      NO  → Continue
  │
  ├─ Startup/MVP? YES → Recommend Agile
  │               NO  → Continue
  │
  ├─ Microservices? YES → Recommend Hybrid
  │                 NO  → Ask user
  │
  ▼
Generate methodology-specific roadmap
```

**When to use in skills:**
- Methodology detection (Waterfall vs Agile)
- Error handling (retry vs fail)
- Adaptive workflows (different paths per project type)

---

### Type 4: Looping (Repeat Until Done)

**When to use:** Need to repeat steps until condition is met

**Characteristics:**
- ✅ Good for batch processing
- ✅ Handles variable-size datasets
- ❌ Risk of infinite loops
- ❌ Need clear exit condition

**Pattern:**
```
┌─────────────────┐
│ Process batch   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ More batches?   │
│ YES → Loop      │
│ NO  → Done      │
└────────┬────────┘
         │
      ┌──┴──┐
      │     │
      ▼     ▼
   Loop   Done
```

**Example: Multi-Module Documentation**
```
For each module in project:
  1. Scan module directory
  2. Extract components
  3. Generate module docs
  4. Add to master TOC

Loop until all modules documented.
```

**When to use in skills:**
- Processing multiple modules/features
- Generating docs for variable-size codebases
- Batch operations (multiple users, products, etc.)

---

### Type 5: Retry (Try Again If Fails)

**When to use:** Operations might fail temporarily

**Characteristics:**
- ✅ Handles transient failures
- ✅ Improves reliability
- ❌ Adds complexity
- ❌ May mask real problems

**Pattern:**
```
Attempt 1 → Success? YES → Done
            ↓ Fail
Attempt 2 → Success? YES → Done
            ↓ Fail
Attempt 3 → Success? YES → Done
            ↓ Fail
Give up → Error
```

**Example: API Calls in Documentation Generation**
```
Try to fetch external schema:
  Attempt 1: Call API
    - Network timeout → Retry
  Attempt 2: Call API
    - Server error → Retry
  Attempt 3: Call API
    - Success → Continue
    - Fail → Use cached schema
```

**When to use in skills:**
- API calls (network issues)
- File operations (temporary locks)
- Database connections (pool exhaustion)

---

## Orchestration Patterns

### Pattern 1: Map-Reduce

**Use case:** Process many items independently, then combine

**Flow:**
```
Map:     Process each item INDEPENDENTLY
         item1 → process → result1
         item2 → process → result2
         item3 → process → result3

Reduce:  Combine results
         [result1, result2, result3] → combined result
```

**Example: Multi-Tenant Documentation**
```
Map: For each tenant
  - Generate tenant-specific docs
  - Extract tenant requirements
  - Create tenant schema

Reduce: Combine into
  - Master documentation
  - Unified schema
  - Cross-tenant comparison
```

**When to use:**
- Generating docs for multiple modules
- Processing multiple user stories
- Creating multi-component specifications

---

### Pattern 2: Pipeline

**Use case:** Each step feeds into next (assembly line)

**Flow:**
```
Input → Agent 1 → Agent 2 → Agent 3 → Output

Each agent receives output from previous as input.
```

**Example: Document Processing Pipeline**
```
Raw Requirements → Parse → Validate → Transform → Format → Export PDF

Each step transforms output for next step.
```

**When to use:**
- Data transformation workflows
- Document generation pipelines
- Sequential processing with transformations

---

### Pattern 3: Fan-Out/Fan-In

**Use case:** One input split to many agents, then combined

**Flow:**
```
        ┌─→ Agent A ──┐
Input ─→┤─→ Agent B ──┼─→ Combine → Output
        └─→ Agent C ──┘
```

**Example: Comprehensive System Analysis**
```
Project Context ┌─→ Security Analysis ──┐
                ├─→ Performance Analysis─┤─→ Combined Report
                └─→ Scalability Analysis─┘
```

**When to use:**
- Multiple perspectives on same data
- Parallel validation checks
- Multi-criteria analysis

---

### Pattern 4: Circuit Breaker (Fault Tolerance)

**Use case:** Prevent cascading failures

**Flow:**
```
Request → Check Circuit
            │
            ├─ CLOSED (normal) → Call agent
            ├─ OPEN (too many failures) → Return cached/default
            └─ HALF-OPEN (testing) → Try agent
```

**Example: External API Integration**
```
If external schema API fails >3 times:
  - Open circuit
  - Use local cache instead
  - Periodically test if API is back
```

**When to use:**
- External API dependencies
- Resource-intensive operations
- Network-dependent workflows

---

## Orchestration Decision Tree

```
Question: Must all steps happen in order?
├─ YES → SEQUENTIAL
│
Question: Can some steps run together?
├─ YES → PARALLEL (Fan-Out/Fan-In)
│
Question: Does path depend on data/conditions?
├─ YES → CONDITIONAL
│
Question: Need to repeat until done?
├─ YES → LOOPING
│
Question: Might fail temporarily?
├─ YES → RETRY + CIRCUIT BREAKER
```

---

## Applying Orchestration to Skills

### For feature-planning Skill

**Current:** Sequential implementation (Task 1 → Task 2 → Task 3...)

**Enhancement with orchestration:**
```markdown
## Phase 1: Database Setup (Sequential - must be ordered)
- Task 1: Create migration
- Task 2: Run migration
- Task 3: Create model

## Phase 2: API + UI (Parallel - independent)
- Task 4a: Create API endpoint ──┐
- Task 4b: Create UI component ──┼─→ Both run together
                                 ┘

## Phase 3: Testing (Sequential after Phase 2)
- Task 5: Create API tests
- Task 6: Create UI tests

## Phase 4: Integration (Conditional)
- If external API: Task 7a (with retry logic)
- If internal only: Task 7b (no retry needed)
```

**Pattern used:** Pipeline + Parallel + Conditional

---

### For doc-architect Skill

**Current:** Sequential document generation

**Enhancement with orchestration:**
```markdown
## Scan Project (Sequential - build knowledge)
- Step 1: Detect tech stack
- Step 2: Find schema directory
- Step 3: Find plan directory

## Generate Docs (Parallel - independent)
- Step 4a: Generate Root AGENTS.md  ──┐
- Step 4b: Generate Data AGENTS.md  ──┼─→ All 3 run together
- Step 4c: Generate Plan AGENTS.md  ──┘

## Validate (Sequential - check consistency)
- Step 5: Cross-reference all 3 docs
- Step 6: Ensure no contradictions
```

**Pattern used:** Pipeline + Fan-Out/Fan-In

---

### For custom-sub-agents Skill

**Current:** Explains sub-agent creation

**Enhancement with orchestration:**
```markdown
## When creating multi-agent systems, use orchestration:

### Scenario 1: Multiple Independent Agents
**Pattern:** Parallel Execution
- Agent A: Handles authentication
- Agent B: Handles data fetching
- Agent C: Handles validation
Run all 3 in parallel, combine results.

### Scenario 2: Dependent Agents
**Pattern:** Pipeline
- Agent A output → Agent B input → Agent C input
Sequential pipeline where each transforms data.

### Scenario 3: Conditional Routing
**Pattern:** Conditional
- If user type A: Route to Agent X
- If user type B: Route to Agent Y
Smart routing based on request type.
```

**Pattern used:** Teach orchestration as part of sub-agent design

---

## Best Practices

### DO:
✅ **Choose simplest pattern** that works (start with sequential)
✅ **Document dependencies** clearly (which steps depend on what)
✅ **Handle errors** at each step (don't let failures cascade)
✅ **Monitor execution** (log progress, track timing)
✅ **Test each strategy** (sequential, parallel, conditional separately)

### DON'T:
❌ **Over-parallelize** (not everything needs to be parallel)
❌ **Ignore dependencies** (breaking order causes failures)
❌ **Skip error handling** (failures will happen in production)
❌ **Forget exit conditions** (loops must end)
❌ **Make it too complex** (KISS - Keep It Simple, Stupid)

---

## Orchestration for Documentation Workflows

### Waterfall SRS Pipeline (Sequential)
```
Phase 01 → Phase 02 → Phase 03 → ... → Phase 08

Why sequential?
- Each phase depends on previous output
- Traceability requires order
- IEEE 830 compliance needs structured flow
```

### Agile User Story Generation (Parallel + Sequential)
```
Sequential:
1. Read project context

Parallel:
2a. Generate user stories    ──┐
2b. Create personas          ──┼─→ Independent tasks
2c. Build story map          ──┘

Sequential:
3. Combine all outputs
4. Generate backlog summary
```

### Hybrid Approach (Conditional + Parallel)
```
Conditional:
IF regulated backend:
  → Generate SRS (sequential)

IF agile frontend:
  → Generate user stories (parallel)

Parallel:
Generate shared docs:
├─ HLD (both need)
├─ API specs (both need)
└─ Test strategy (both need)
```

---

## Complexity vs Performance

```
┌──────────────┬────────────┬────────────┬──────────────┐
│ Strategy     │ Complexity │ Speed      │ Reliability  │
├──────────────┼────────────┼────────────┼──────────────┤
│ Sequential   │ Low ⭐     │ Slow ⏱️    │ High ✅       │
│ Parallel     │ Medium ⭐⭐ │ Fast ⚡⚡   │ Medium ⚠️     │
│ Conditional  │ High ⭐⭐⭐  │ Variable   │ Medium ⚠️     │
│ Looping      │ Medium ⭐⭐ │ Variable   │ High ✅       │
│ Retry        │ Medium ⭐⭐ │ Slow ⏱️    │ Very High ✅✅ │
└──────────────┴────────────┴────────────┴──────────────┘

Choose based on your priorities:
- Need reliability? → Sequential + Retry
- Need speed? → Parallel + Fan-Out/Fan-In
- Need flexibility? → Conditional
- Need fault tolerance? → Circuit Breaker
```

---

## Orchestration Checklist

Before implementing orchestration:

```
□ What agents/steps do I have?
□ Which steps MUST run in order?
□ Which steps CAN run in parallel?
□ What happens if a step fails?
□ Do I need retry logic?
□ Should paths be conditional?
□ Do I need circuit breaker for external deps?
□ How will I monitor execution?
□ How will I debug failures?
□ How will I measure performance?
□ What's my exit condition (for loops)?
□ How do I handle partial failures?
```

**Scoring:**
- 8/12 = Good plan (will work)
- 12/12 = Excellent plan (production-ready)

---

## Examples from SDLC-Docs-Engine

### 1. Meta-Initialization (Phase 00)
**Pattern:** Conditional + Sequential

```
Sequential:
1. Scan project directory

Conditional:
2. IF regulated keywords → Recommend Waterfall
   ELIF startup/MVP → Recommend Agile
   ELIF microservices → Recommend Hybrid
   ELSE → Ask user

Sequential:
3. Generate methodology.md
4. Generate doc_roadmap.md
```

### 2. Waterfall SRS (Phase 02)
**Pattern:** Pipeline (strict sequential)

```
01-initialize-srs →
02-context-engineering →
03-descriptive-modeling →
04-interface-specification →
05-feature-decomposition →
06-logic-modeling →
07-attribute-mapping →
08-semantic-auditing

Pure pipeline: output of each is input to next.
```

### 3. Agile User Story Generation
**Pattern:** Fan-Out/Fan-In + Sequential

```
Sequential:
1. Read features.md

Fan-Out (Parallel):
2a. Generate stories from features
2b. Create personas
2c. Build story map

Fan-In:
3. Combine: stories + personas → final backlog

Sequential:
4. Generate backlog_summary.md
```

### 4. Design Documentation
**Pattern:** Parallel + Pipeline

```
Sequential (gather inputs):
1. Read SRS/User Stories

Parallel (independent docs):
2a. Generate HLD
2b. Generate API specs
2c. Generate DB schema docs

Sequential (combine):
3. Create unified architecture document
```

---

## Summary

**Orchestration strategies:**
1. **Sequential:** One after another (simple, reliable, slow)
2. **Parallel:** Multiple at once (fast, complex, needs sync)
3. **Conditional:** Smart decisions (flexible, harder to debug)
4. **Looping:** Repeat until done (batch processing, need exit)
5. **Retry:** Try again if fails (fault tolerance, essential)

**Patterns:**
- **Map-Reduce:** Process many items independently, combine
- **Pipeline:** Each step feeds into next
- **Fan-Out/Fan-In:** Split work, combine results
- **Circuit Breaker:** Prevent cascading failures

**Choose based on:**
- Dependencies (sequential if dependent, parallel if independent)
- Failure handling (retry for transient, circuit breaker for external)
- Complexity tolerance (sequential simplest, conditional most complex)
- Performance needs (parallel fastest, sequential slowest)

**Impact:**
- **30% faster** workflows (with parallelization)
- **50% better** fault tolerance (with retry + circuit breaker)
- **70% easier** to debug (with clear orchestration patterns)

---

**See also:**
- `prompting-patterns-reference.md` - For creating better instructions
- `doc-standards.md` - For documentation structure
- `feature-planning/references/` - For implementation patterns

**Last Updated:** 2026-02-07
