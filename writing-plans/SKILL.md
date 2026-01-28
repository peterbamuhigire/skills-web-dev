---
name: writing-plans
description: Create comprehensive, bite-sized implementation plans for multi-step features using TDD workflow. Use when planning complex features, multi-file changes, or tasks requiring step-by-step guidance (examples: new authentication system, API endpoint with tests, database migration, refactoring). Generates detailed plans with exact file paths, complete code, test-driven workflow, and frequent commits.
---

# Writing Plans

Create comprehensive implementation plans for multi-step tasks. Each plan breaks work into bite-sized tasks (2-5 minutes each) with exact file paths, complete code, and test-driven development workflow.

**Save plans to:** `docs/plans/YYYY-MM-DD-<feature-name>.md`

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
