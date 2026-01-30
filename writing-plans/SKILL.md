---
name: writing-plans
description: Create comprehensive, bite-sized implementation plans for multi-step features using TDD workflow. Use when planning complex features, multi-file changes, or tasks requiring step-by-step guidance (examples: new authentication system, API endpoint with tests, database migration, refactoring). Generates detailed plans with exact file paths, complete code, test-driven workflow, and frequent commits.
---

# Writing Plans

Create comprehensive implementation plans for multi-step tasks. Each plan breaks work into bite-sized tasks (2-5 minutes each) with exact file paths, complete code, and test-driven development workflow.

**Standard plan directory (required):** `/docs/plans/`

**Save plan index to:** `docs/plans/YYYY-MM-DD-<feature-name>.md`

**Save plan sections to:** `docs/plans/<feature-name>/` (multi-file plans)

**Plan directory index (required):** Update `docs/plans/AGENTS.md` whenever a plan is added or its status changes.

## Standard Plan Structure (Required)

Use the following canonical structure for all plans:

```
docs/plans/
    AGENTS.md                              # Plans directory index (must stay current)
    YYYY-MM-DD-<feature-name>.md           # Index file linking all sections
    <feature-name>/
        00-overview-and-scope.md
        01-...
        02-...
```

### Index File Requirements

The index file in `plans/` must:

- Declare the plan goal and scope.
- Link to every section file with relative links.
- State the standard directory rule: all plan files live under `/docs/plans/`.

### Section File Requirements

Each section file in `plans/<feature-name>/` must:

- Start with a section title and goal.
- Use the task template below.
- Include status tracking per task.
- Reference exact file paths and commands.

## Architectural Decision Framework

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
- **Code analysis** (linting, validation)

✅ **Example Use Cases:**

- File creation and editing
- Running terminal commands
- Code searching and analysis
- Basic refactoring operations
- Documentation generation
- Test execution

### When to Use Dynamic Sub-Agents

✅ **Perfect for:**

- **Complex business logic** (custom algorithms, ML models)
- **Evolving requirements** (frequent changes needed)
- **Specialized domains** (industry-specific knowledge)
- **Scalable systems** (many similar but different agents)
- **Experimental features** (A/B testing, rapid prototyping)
- **Third-party integrations** (APIs, databases, external services)
- **Heavy computations** (data processing, analysis)

✅ **Example Use Cases:**

- Custom code generators
- Data analysis and visualization
- API integrations and workflows
- Machine learning model serving
- Business rule engines
- Complex refactoring tools
- Domain-specific assistants

### Token Cost Analysis

**Static Skills:**

- **Initial Cost**: High (loaded with VS Code)
- **Per-Use Cost**: Very Low (~10-50 tokens)
- **Total Cost**: Low for frequent use
- **Break-even**: After ~100 uses

**Dynamic Sub-Agents:**

- **Initial Cost**: Low (loaded on demand)
- **Per-Use Cost**: Medium (~100-500 tokens)
- **Total Cost**: Scales with usage
- **Break-even**: Immediate for specialized tasks

### Plan Enhancement Requirements

**For Static Skills Plans:**

- Focus on performance optimization
- Minimize initialization overhead
- Ensure VS Code extension compatibility
- Plan for infrequent updates

**For Dynamic Sub-Agents Plans:**

- Include configuration management
- Plan for registry integration
- Add monitoring and analytics
- Design for scalability and updates
- Reference: `skills/custom-sub-agents/references/`

**Required in Every Plan:**

- **Architecture Declaration**: State whether using skills or sub-agents and why
- **Token Cost Analysis**: Include estimated token usage and break-even analysis
- **Skill References**: Link to relevant skills in `skills/` directory
- **Migration Path**: If converting between approaches, include migration steps

## Bite-Sized Task Granularity

Break each feature into one-action steps (2-5 minutes):

- Write failing test → step
- Run to verify failure → step
- Implement minimal code → step
- Run to verify pass → step
- Commit → step

## Plan Document Header

Start every plan with this header:

```markdown
# [Feature Name] Implementation Plan

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

## Task Structure Template

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

```

## Plan Essentials

Include in every plan:
- **Architecture Declaration**: State whether using static skills or dynamic sub-agents and provide justification based on the decision matrix
- **Token Cost Analysis**: Include estimated token usage, break-even analysis, and performance implications
- **Skill References**: Link to relevant skills in `skills/` directory and explain why they apply
- **Exact file paths** - Never "add validation to the file"
- **Complete code** - Full implementations, not placeholders
- **Exact commands** - With expected output
- **Test-first** - Write test, verify fail, implement, verify pass
- **Frequent commits** - After each passing test
- **Testability** - Ensure all changes can be tested later (add hooks, APIs, fixtures, or logs where needed)
- **PHP syntax check** - For any PHP files touched, include a `php -l <file>` step after changes
- **Schema adherence** - Verify all SQL aligns to `database/schema/*.sql` and update schema files, procedures, and triggers as needed
- **Cross-layer completeness** - Explicitly cover database, stored procedures, triggers, UI, APIs, services, middleware, and any other impacted layers
- **Verification steps** - Add concrete checks that confirm schema alignment and functional correctness
- **Multi-file plans** - If the plan is large, split into multiple markdown files and provide an index file that links to each section
- **Status tracking** - Include a status section (not-started/in-progress/completed) per task and keep it updated during implementation
- **Self-updating plans** - If implementation decisions change or new optional steps are discovered, update the plan files immediately so progress is always current

## Best Practices

**DO:**
- Break into 2-5 minute tasks
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
```
