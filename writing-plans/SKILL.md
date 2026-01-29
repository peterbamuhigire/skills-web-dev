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
- **Skill mapping** - Explicitly state which skills from `skills/` apply to each plan section and why
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
