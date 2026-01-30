---
name: feature-planning
description: Complete feature planning from specification to implementation. Create structured specs with user stories and acceptance criteria, then generate detailed implementation plans with TDD workflow, exact file paths, and complete code examples.
---

# Feature Planning

Complete feature development planning from **specification** to **implementation**. This skill combines requirements engineering with detailed implementation planning to ensure features are both well-specified and properly implemented.

**Standard plan directory (required):** `/docs/plans/`

**Save specs to:** `docs/plans/specs/[domain]/[feature-name].md`
**Save implementation plans to:** `docs/plans/YYYY-MM-DD-[feature-name].md`
**Save multi-file plans to:** `docs/plans/[feature-name]/` (implementation details)

**Plan directory index (required):** Update `docs/plans/AGENTS.md` whenever a plan or spec is added.

## 📋 Two-Phase Planning Process

### Phase 1: Specification (Requirements)

Create structured specifications that define **WHAT** to build.

### Phase 2: Implementation Planning (How)

Create detailed implementation plans that define **HOW** to build it.

---

## 🎯 Phase 1: Specification (Spec-Driven Development)

### When to Use Specification Phase

Activate when the user says:

- "Plan a feature"
- "Write a spec"
- "New module: [name]"
- "Create requirements for [feature]"

### Specification Process

1. **Analyze Context**: Review existing codebase to understand where the feature fits
2. **Ask Clarifying Questions**: Gather business logic, edge cases, and constraints (3-5 questions)
3. **Generate Specification**: Use structured template with user stories, acceptance criteria, and technical details

### Clarifying Questions (Pick 3-5)

1. **Business Domain**: Which primary module does this belong to (sales, inventory, finance, HR, assets)?
2. **Edge Cases**: What critical edge cases or failure modes must be handled?
3. **Data Model**: Which tables/fields are involved (especially tenant isolation)?
4. **Workflow/UI**: What exact UI flow and user actions are expected?
5. **Compliance/Reporting**: Any audit, reporting, or approval requirements?

### Specification Template Structure

```markdown
# {Feature Title} — Spec

**Status:** Draft | Approved | Implemented
**Priority:** High | Medium | Low
**Domain:** {sales|inventory|finance|hr|assets}
**Estimated Effort:** {S|M|L|XL}

## User Story

As a **{role}**, I want to **{action}** so that **{value}**.

## Acceptance Criteria (Definition of Done)

- [ ] {AC1: Functional requirement}
- [ ] {AC2: Edge case handling}
- [ ] {AC3: Validation rule}
- [ ] {AC4: Integration requirement}

## Technical Constraints

- {Constraint 1: Architecture decision}
- {Constraint 2: Performance requirement}
- {Constraint 3: Security consideration}

## Data Model

- **Tables:** {list affected tables}
- **Columns:** {table.column — type — purpose}
- **Relationships:** {foreign keys, constraints}
- **Indexes:** {performance optimization needs}

## High-Level Execution Plan

1. {Task 1} — `path/to/file.ext`
2. {Task 2} — `path/to/file.ext`
3. {Task 3} — `path/to/file.ext`

## Testing Strategy

- **Unit Tests:** {what to test}
- **Integration Tests:** {cross-component testing}
- **Edge Cases:** {specific scenarios to cover}

## Rollout Strategy

- **Deployment:** {how to deploy safely}
- **Rollback:** {how to revert if needed}
- **Monitoring:** {what to monitor post-deployment}
```

### Specification Storage

**Location:** `docs/plans/specs/[domain]/[feature-name].md`

**Example:**

```
docs/plans/specs/sales/
├── user-profile-update.md
├── bulk-order-processing.md
└── commission-calculations.md

docs/plans/specs/inventory/
├── stock-adjustment-workflow.md
└── batch-expiry-alerts.md
```

---

## 🔧 Phase 2: Implementation Planning (TDD Workflow)

### When to Use Implementation Planning Phase

Activate when:

- Specification is approved and ready for implementation
- User says "implement [feature]" or "create plan for [feature]"
- Breaking down approved specs into executable tasks

### Implementation Planning Process

1. **Review Specification**: Understand requirements and constraints
2. **Decompose into Tasks**: Break into 2-5 minute bite-sized steps
3. **Apply TDD Workflow**: Test-first development with exact file paths
4. **Generate Complete Code**: Include full implementations, not placeholders
5. **Plan Testing Strategy**: Ensure all changes can be tested

### Bite-Sized Task Granularity

Break each feature into one-action steps (2-5 minutes):

- Write failing test → step
- Run to verify failure → step
- Implement minimal code → step
- Run to verify pass → step
- Commit → step

### Implementation Plan Structure

**Index File:** `docs/plans/YYYY-MM-DD-[feature-name].md`
**Section Files:** `docs/plans/[feature-name]/` (for complex features)

```
docs/plans/
├── AGENTS.md                              # Plans directory index
├── YYYY-MM-DD-user-profile-update.md      # Index file
├── user-profile-update/                   # Implementation details
│   ├── 00-overview-and-scope.md
│   ├── 01-database-schema.md
│   ├── 02-api-endpoint.md
│   ├── 03-ui-form.md
│   └── 04-testing-validation.md
```

### Task Structure Template

````markdown
### Task N: [Component Name]

**Files:**

- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Step 1: Write failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```
````

**Step 2: Run test to verify failure**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

**Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

**Step 4: Run test to verify pass**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```

````

---

## 📚 Learning Resources

### Comprehensive Guide for IT Students
For a complete understanding of what plans are and how they work, see the detailed educational guide:

**📖 [Plans: Comprehensive Guide for IT Students](references/01-what-is-a-plan.md)**

This guide covers:
- What plans are (with simple analogies)
- Core concepts (steps, dependencies, parallelization, DAGs)
- Plan execution models and code examples
- Real-world examples and CS concepts mapping

**Guide Sections:**
- [01-what-is-a-plan.md](references/01-what-is-a-plan.md) - Basic definitions and analogies
- [02-core-concepts.md](references/02-core-concepts.md) - Step, Dependency, Parallelization, DAG, Validation
- [03-plan-execution-model.md](references/03-plan-execution-model.md) - How plans work
- [04-plan-structure-code.md](references/04-plan-structure-code.md) - Code examples and structure
- [05-visualizing-dependencies.md](references/05-visualizing-dependencies.md) - DAG visualization
- [06-creating-plans-guide.md](references/06-creating-plans-guide.md) - Step-by-step creation guide
- [07-executing-plans.md](references/07-executing-plans.md) - Execution pseudocode
- [08-cs-concepts-mapping.md](references/08-cs-concepts-mapping.md) - CS concepts you should recognize
- [09-real-examples.md](references/09-real-examples.md) - Real-world examples
- [10-key-takeaways.md](references/10-key-takeaways.md) - Summary and key takeaways

---

## 🏗️ Architectural Decision Framework

**CRITICAL**: Before creating any implementation plan, evaluate whether to use **static skills** vs **dynamic sub-agents** based on the decision matrix below. This choice significantly impacts token efficiency, development velocity, and maintenance costs.

### Skills vs Sub-Agents Decision Matrix

| Factor              | Use **Static Skills**            | Use **Dynamic Sub-Agents**       |
| ------------------- | -------------------------------- | -------------------------------- |
| **Token Usage**     | Low (pre-loaded)                 | Variable (loaded on demand)      |
| **Execution Speed** | Fast (always ready)              | Slower (initialization overhead) |
| **Customization**   | Limited (static code)            | High (dynamic, configurable)     |
| **Maintenance**     | Low (infrequent updates)         | Higher (frequent iterations)     |
| **Scalability**     | Limited (VS Code extension size) | High (unlimited agents)          |
| **Complexity**      | Low (simple patterns)            | High (orchestration needed)      |
| **Collaboration**   | Easy (shared codebase)           | Complex (distributed agents)     |

### When to Use Static Skills
✅ **Perfect for:**
- **Common operations** (file editing, terminal commands, searches)
- **Stable functionality** (rarely changing requirements)
- **Performance-critical** tasks (must be fast)
- **Simple workflows** (linear, predictable)
- **Team collaboration** (shared understanding)
- **Documentation tasks** (consistent formatting)

### When to Use Dynamic Sub-Agents
✅ **Perfect for:**
- **Complex business logic** (custom algorithms, ML models)
- **Evolving requirements** (frequent changes needed)
- **Specialized domains** (industry-specific knowledge)
- **Scalable systems** (many similar but different agents)
- **Experimental features** (A/B testing, rapid prototyping)
- **Third-party integrations** (APIs, databases, external services)
- **Heavy computations** (data processing, analysis)

### Token Cost Analysis
**Static Skills:** Low initial cost, very low per-use cost
**Dynamic Sub-Agents:** Low initial cost, medium per-use cost

### Plan Enhancement Requirements
**For Static Skills Plans:** Focus on performance optimization
**For Dynamic Sub-Agents Plans:** Include configuration management and monitoring

**Required in Every Plan:**
- **Architecture Declaration**: State approach and justification
- **Token Cost Analysis**: Include estimated usage and break-even analysis
- **Skill References**: Link to relevant skills in `skills/` directory
- **Migration Path**: If converting approaches, include migration steps

---

## 📋 Plan Document Header

Start every plan with this header:

```markdown
# [Feature Name] Implementation Plan

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

**Specification:** [Link to spec if exists]

---
````

---

## ✅ Plan Essentials

Include in every plan:

- **Architecture Declaration**: State whether using skills or sub-agents and provide justification based on the decision matrix
- **Token Cost Analysis**: Include estimated token usage, break-even analysis, and performance implications
- **Skill References**: Link to relevant skills in `skills/` directory and explain why they apply
- **Exact file paths** - Never "add validation to the file"
- **Complete code** - Full implementations, not placeholders
- **Exact commands** - With expected output
- **Testability** - Ensure all changes can be tested later (add hooks, APIs, fixtures, or logs where needed)
- **PHP syntax check** - For any PHP files touched, include a `php -l <file>` step after changes
- **Schema adherence** - Verify all SQL aligns to `database/schema/*.sql` and update schema files, procedures, and triggers as needed
- **Cross-layer completeness** - Explicitly cover database, stored procedures, triggers, UI, APIs, services, middleware, and any other impacted layers
- **Verification steps** - Add concrete checks that confirm schema alignment and functional correctness
- **Multi-file plans** - If the plan is large, split into multiple markdown files and provide an index file that links to each section
- **Status tracking** - Include a status section (not-started/in-progress/completed) per task and keep it updated during implementation
- **Self-updating plans** - If implementation decisions change or new optional steps are discovered, update the plan files immediately so progress is always current

---

## 🎯 Best Practices

**DO:**

- Start with specification phase for new features
- Break implementation into 2-5 minute tasks
- Include complete code samples
- Specify exact paths and line numbers
- Follow DRY, YAGNI principles
- Test-driven development
- Commit after each green test

**DON'T:**

- Create huge monolithic tasks
- Use pseudocode or placeholders
- Skip test verification steps
- Assume context exists
- Make untested changes
- Leave PHP changes without a `php -l` syntax check
