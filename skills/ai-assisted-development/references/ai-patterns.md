# AI Orchestration Patterns

**Purpose:** Learn AI-specific orchestration patterns for coordinating multiple AI agents

**Parent Skill:** ai-assisted-development

---

## What Are AI Orchestration Patterns?

**AI orchestration patterns** are proven ways to coordinate multiple AI agents to work together on software development tasks.

Think of them as **design patterns**, but for AI workflows instead of code structure.

---

## The 3 Core AI Patterns

### Pattern 1: Agent Handoff (Pipeline Pattern)

**Use case:** One AI agent completes work, passes output to next AI agent

**Flow:**
```
Agent A → Output (becomes input) → Agent B → Output → Agent C → Done
```

**Example: Feature Development Pipeline**

**Agent 1: Requirements Agent**
```markdown
Prompt: "Analyze these user requests and create formal requirements document."

Input: User interviews, feature requests
Output: docs/requirements.md
```

**Agent 2: Specification Agent** (receives Agent 1 output)
```markdown
Prompt: "Using the requirements document, create technical specification.

FILE TO READ: docs/requirements.md

CONTEXT: Transform requirements into implementable spec with:
- Data model
- API endpoints
- UI wireframes"

Input: docs/requirements.md (from Agent 1)
Output: docs/specs/feature-spec.md
```

**Agent 3: Implementation Agent** (receives Agent 2 output)
```markdown
Prompt: "Implement the feature using the specification.

FILE TO READ: docs/specs/feature-spec.md

CONTEXT: Write complete, production-ready code following spec exactly."

Input: docs/specs/feature-spec.md (from Agent 2)
Output: Code files
```

**Key principle:** Each agent's output is the next agent's input (like a factory assembly line)

**Benefits:**
- Clear separation of concerns
- Each agent focused on ONE job
- Easy to debug (check output at each step)
- Traceable (spec → code → tests all linked)

---

### Pattern 2: Fan-Out/Fan-In (Parallel + Combine)

**Use case:** Split work across multiple AI agents, then combine results

**Flow:**
```
                ┌─→ Agent A ──┐
Input (split) ──┼─→ Agent B ──┼─→ Combine → Output
                └─→ Agent C ──┘
```

**Example: Multi-Component Documentation**

**Fan-Out Phase:**

**Agent A: Database Docs**
```markdown
"Generate database schema documentation.

SCAN: database/migrations/
OUTPUT: docs/database.md

ORCHESTRATION: Part of parallel fan-out (with Agents B and C)"
```

**Agent B: API Docs**
```markdown
"Generate API endpoint documentation.

SCAN: app/Http/Controllers/
OUTPUT: docs/api.md

ORCHESTRATION: Part of parallel fan-out (with Agents A and C)"
```

**Agent C: UI Docs**
```markdown
"Generate UI component documentation.

SCAN: resources/js/components/
OUTPUT: docs/ui.md

ORCHESTRATION: Part of parallel fan-out (with Agents A and B)"
```

**All 3 agents run in parallel (no dependencies between them)**

**Fan-In Phase:**

**Agent D: Combiner**
```markdown
"Combine all documentation into unified architecture document.

FILES TO READ:
- docs/database.md (Agent A output)
- docs/api.md (Agent B output)
- docs/ui.md (Agent C output)

ORCHESTRATION: Fan-in phase (waits for all 3 agents to complete).

GENERATE:
- Master architecture document
- Cross-reference links
- Unified glossary"
```

**Timing:**
- **Parallel:** All 3 agents run simultaneously = 10 minutes
- **Sequential would be:** 10 + 10 + 10 = 30 minutes
- **Savings:** 67% faster

**Benefits:**
- Massive speedup (run in parallel)
- Independent work (no coordination needed)
- Combine at end (unified output)

---

### Pattern 3: Human-in-the-Loop (Gated Approval)

**Use case:** AI agents generate work, human approves before continuing

**Flow:**
```
Agent 1 → Output → [HUMAN REVIEW] → Approved? YES → Agent 2
                                                 ↓ NO
                                              Revise (loop back to Agent 1)
```

**Example: Spec → Code → Deploy with Approval Gates**

**Phase 1: AI Planning**

**Agent: Planning Agent**
```markdown
"Create feature specification for payment processing.

OUTPUT: docs/specs/payment-spec.md"
```

**Output:** Spec document

**[GATE 1: Human Review]**
- Human reads spec
- Checks: Business logic correct? Security concerns? Edge cases?
- Decision: ✅ Approve → Continue | ❌ Reject → Revise spec

---

**Phase 2: AI Implementation (only if Phase 1 approved)**

**Agent: Implementation Agent**
```markdown
"Implement payment processing using approved spec.

FILE TO READ: docs/specs/payment-spec.md (APPROVED by human)

ORCHESTRATION: Phase 2 (gated - only runs after human approval)"
```

**Output:** Code files

**[GATE 2: Human Review]**
- Human reviews code
- Checks: Follows spec? Security ok? Tests exist?
- Decision: ✅ Approve → Continue | ❌ Reject → Fix code

---

**Phase 3: AI Testing (only if Phase 2 approved)**

**Agent: Testing Agent**
```markdown
"Create tests for payment processing.

FILES TO READ:
- docs/specs/payment-spec.md (approved spec)
- app/Services/PaymentService.php (approved code)

ORCHESTRATION: Phase 3 (gated - only runs after code approved)"
```

**Output:** Test files

**[GATE 3: Human Review]**
- Human reviews tests
- Checks: Coverage sufficient? Edge cases tested?
- Decision: ✅ Approve → Deploy | ❌ Reject → Add more tests

**Benefits:**
- **Safety:** Human oversight at critical points
- **Quality control:** Catch issues before they cascade
- **Learning:** AI learns from human feedback
- **Compliance:** Some industries require human approval

**When to use gates:**
- Security-critical features (payment, auth, data access)
- High-risk changes (database migrations, API breaking changes)
- Compliance requirements (financial, healthcare, legal)
- Learning phase (train AI on your patterns)

---

## Combining Patterns

**Real-world AI workflows combine multiple patterns.**

**Example: Complete Feature Development with All 3 Patterns**

```
┌─────────────────────────────────────────────────┐
│ Pattern 1: Agent Handoff (Pipeline)             │
│                                                  │
│ Agent 1: Planning → docs/specs/feature.md       │
│                          ↓                       │
│         [GATE 1: Human Review] ← Pattern 3      │
│                          ↓ (approved)            │
├─────────────────────────────────────────────────┤
│ Pattern 2: Fan-Out (Parallel)                   │
│                                                  │
│ Agent 2a: Database ──┐                          │
│ Agent 2b: API ───────┼─→ All run in parallel    │
│ Agent 2c: UI ────────┘                          │
│                          ↓                       │
│ Pattern 2: Fan-In (Combine)                     │
│                          ↓                       │
│ Agent 3: Integration → Combine all components   │
│                          ↓                       │
│         [GATE 2: Human Review] ← Pattern 3      │
│                          ↓ (approved)            │
├─────────────────────────────────────────────────┤
│ Pattern 1: Agent Handoff (Pipeline continues)   │
│                                                  │
│ Agent 4: Testing → Create comprehensive tests   │
│                          ↓                       │
│         [GATE 3: Human Review] ← Pattern 3      │
│                          ↓ (approved)            │
│ Agent 5: Deployment → Ship to production        │
└─────────────────────────────────────────────────┘
```

**Patterns used:**
- ✅ Agent Handoff (planning → implementation → testing → deployment)
- ✅ Fan-Out/Fan-In (parallel database + API + UI work)
- ✅ Human-in-the-Loop (3 approval gates)

**Result:** Fast, safe, high-quality feature delivery

---

## Pattern Selection Guide

| Pattern             | Use When                                    | Benefit                     |
|---------------------|---------------------------------------------|-----------------------------|
| Agent Handoff       | Each agent builds on previous work          | Clear pipeline, traceable   |
| Fan-Out/Fan-In      | Independent components can be parallelized  | 50-70% faster execution     |
| Human-in-the-Loop   | High-risk or critical features              | Safety, quality control     |

**Combine patterns** for complex workflows to get benefits of all.

---

## Advanced: Meta-Orchestration

**Meta-orchestration** = AI agent that coordinates other AI agents

**Pattern:**
```
Meta-Agent (Orchestrator)
    │
    ├─→ Spawns Agent A for task 1
    ├─→ Spawns Agent B for task 2
    ├─→ Waits for both to complete
    └─→ Combines results
```

**Example: Self-Orchestrating Documentation System**

**Meta-Agent: Documentation Orchestrator**
```markdown
"Analyze this codebase and generate complete documentation.

ORCHESTRATION TASK (not implementation):
1. Scan project to determine type
2. Identify what docs are needed
3. Spawn appropriate specialist agents
4. Coordinate their work
5. Combine outputs

THINK:
- What type of project is this?
- What documentation gaps exist?
- Which agents should I spawn?
- What order should they run?
- Can any run in parallel?

RETURN:
- Orchestration plan
- List of agents to spawn
- Execution order
- Expected outputs"
```

**Output:** Orchestration plan that spawns other agents

**Then Meta-Agent executes the plan:**
- Spawns Database Docs Agent
- Spawns API Docs Agent
- Spawns UI Docs Agent
- Waits for all 3 (parallel)
- Spawns Combiner Agent
- Returns final docs

**Benefits:**
- AI decides best orchestration strategy
- Adapts to project type
- No manual coordination needed
- Scales to complex projects

**When to use:**
- Very complex projects (20+ components)
- Variable project types (needs smart routing)
- Repeatable workflows (meta-agent learns patterns)

---

## Error Handling Patterns

### Pattern: Graceful Degradation

**If agent fails, don't stop everything. Provide partial results.**

```markdown
Agent A: Complete Docs
  ↓ [FAIL: API down]
Fallback: Generate partial docs with TODOs
  → User gets 80% complete docs + manual steps
```

### Pattern: Retry with Context

**If agent fails, retry with error context.**

```markdown
Attempt 1: Agent generates code
  ↓ [FAIL: Syntax error]
Attempt 2: "Fix syntax error at line 42"
  ↓ [FAIL: Logic error]
Attempt 3: "Fix logic error in validation"
  ↓ [SUCCESS]
```

**Each retry includes context from previous failure.**

---

## Best Practices

### DO:
✅ **Use Agent Handoff** for sequential dependencies
✅ **Use Fan-Out/Fan-In** when parallelization possible
✅ **Add Human Gates** for high-risk work
✅ **Provide clear context** to each agent
✅ **Log all agent interactions** for debugging
✅ **Set max retries** to prevent infinite loops
✅ **Have fallback plans** for critical agents

### DON'T:
❌ **Don't parallelize dependent work** (causes race conditions)
❌ **Don't skip human review** on critical features
❌ **Don't assume agents understand context** (be explicit)
❌ **Don't forget error handling** (agents will fail sometimes)
❌ **Don't over-orchestrate simple tasks** (use one agent when possible)

---

## Summary

**The 3 Core AI Patterns:**

1. **Agent Handoff:** One agent → next agent (pipeline)
2. **Fan-Out/Fan-In:** Parallel work → combine (50-70% faster)
3. **Human-in-the-Loop:** AI work → human review → continue (safety)

**Combine patterns** for real-world projects.

**Meta-orchestration:** AI agent that coordinates other AI agents (advanced)

**Error handling:** Graceful degradation + retry with context

**Key principle:** Right agent for the job, clear handoffs, human oversight when needed

---

**See also:**
- `../SKILL.md` - Main AI-assisted development skill
- `orchestration-strategies.md` - The 5 orchestration strategies
- `practical-examples.md` - Real-world MADUUKA and BRIGHTSOMA examples
- `../../orchestration-patterns-reference.md` - General orchestration guide
- `../../prompting-patterns-reference.md` - Better AI prompts

**Last Updated:** 2026-02-07
