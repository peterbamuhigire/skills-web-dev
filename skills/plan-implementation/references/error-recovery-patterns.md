# Error Recovery Patterns — Autonomous Failure Handling

## Recovery Philosophy

Failures are expected. The executor must handle them autonomously without stopping to ask the user. Follow this escalation ladder:

```
Attempt fix (3 tries) → Workaround → Flag & continue → Block & report
```

## Error Classification

| Severity | Definition | Action |
|----------|-----------|--------|
| **Trivial** | Typo, import, formatting | Fix inline, no logging needed |
| **Minor** | Test logic error, wrong assertion | Fix and re-run, log the fix |
| **Major** | Architecture mismatch, missing dependency | Attempt workaround, document assumption |
| **Critical** | Breaks other tasks, data corruption risk | Stop this task, flag for human, continue others |

## Common Failure Patterns and Recovery

### 1. Test Fails After Implementation

**Symptom:** GREEN phase test run shows failures.

**Recovery:**

```
Step 1: Read the error message carefully
Step 2: Identify root cause:
  - Wrong assertion?     → Fix the test expectation
  - Wrong implementation? → Fix the code
  - Missing dependency?  → Add the missing piece
Step 3: Fix and re-run
Step 4: If still failing after 3 attempts → log the failure with full error, move on
```

**Example:**

```
[TASK 5] Test Failure (Attempt 1/3)
  Test: createOrder_validItems_calculatesTotal
  Expected: 150.00
  Actual: 148.50
  Root cause: Tax calculation not including service fee
  Fix: Added service fee to total calculation
  Re-running... PASS ✅
```

### 2. Dependency Not Found

**Symptom:** Import/require fails, class not found, table doesn't exist.

**Recovery:**

```
Step 1: Check if dependency is in a prior uncompleted task
  YES → Execute that task first (re-order), then resume
  NO  → Continue to Step 2

Step 2: Check if dependency exists in codebase but different location
  YES → Fix the import path
  NO  → Continue to Step 3

Step 3: Create the dependency with sensible defaults
  - Document the assumption in a code comment
  - Add a note to the plan file
```

### 3. Migration Conflict

**Symptom:** Migration fails due to existing table/column.

**Recovery:**

```
Step 1: Check if table already exists with correct schema → Skip migration
Step 2: Check if table exists with different schema → Create ALTER migration
Step 3: Check for naming collision → Rename with prefix
Step 4: Document the resolution in plan notes
```

### 4. Route/Endpoint Conflict

**Symptom:** Route already registered, URL collision.

**Recovery:**

```
Step 1: Check existing route — is it the same feature? → Update instead of create
Step 2: Different feature owns the route? → Use alternative URL pattern
Step 3: Document the conflict and resolution
```

### 5. Validation Loop Stuck (3 Failures)

**Symptom:** Code fails validation 3 times on the same layer.

**Recovery:**

```
[VALIDATION STUCK] Task N failed Layer {X} 3 times
  Error pattern: {repeated error}

  Action: Flagging for human review
  Continuing with next independent task...

  Human action needed:
  - Review: {file path}
  - Issue: {specific problem}
  - Attempts: {what was tried}
```

### 6. Existing Tests Break (Regression)

**Symptom:** New code causes previously passing tests to fail.

**Recovery:**

```
Step 1: Identify which existing tests broke
Step 2: Determine if breakage is:
  a) Expected (API changed intentionally) → Update existing tests
  b) Unexpected (bug introduced) → Fix new code to not break existing behavior
Step 3: Run full test suite after fix
Step 4: If can't fix without changing plan → Document as plan deviation
```

### 7. Output Truncation (Token Limit)

**Symptom:** Code generation stops mid-file.

**Recovery by user:**

> "Continue exactly where you left off, starting from the line `[last line generated]`."

**Executor rules on resume:**

- Do NOT repeat any previously generated code
- Do NOT apologize or summarize
- Do NOT restart the file
- Start from the exact line indicated
- Continue generating remaining code seamlessly
- After completing the file, continue with the next task

### 8. Missing Project Convention

**Symptom:** No existing code to match patterns against (new module).

**Recovery:**

```
Step 1: Check CLAUDE.md / AGENTS.md for documented conventions
Step 2: Check skills (webapp-gui-design, php-modern-standards, etc.)
Step 3: Use industry standard patterns for the tech stack
Step 4: Document the convention chosen in a code comment
```

### 9. Ambiguous Plan Requirement

**Symptom:** Plan task description is vague or contradictory.

**Recovery:**

```
Step 1: Check acceptance criteria — often more specific than description
Step 2: Check related tasks — context clues
Step 3: Check design docs (sdlc-design outputs)
Step 4: Use best engineering judgment
Step 5: Document assumption:
  // ASSUMPTION: Plan says "handle payments" — interpreted as recording
  // payment transactions against invoices, not integrating a payment gateway.
```

## Escalation Matrix

| Situation | Autonomous Action | Escalate to Human |
|-----------|-------------------|-------------------|
| Test fails, obvious fix | Fix it | Never |
| Test fails 3 times | Try 3 fixes | After 3rd failure |
| Missing import | Add it | Never |
| Missing table | Create migration | If schema unclear |
| Security vulnerability found | Fix immediately | If architectural |
| Plan contradicts existing code | Follow existing code | Document deviation |
| Performance concern | Note it, continue | After completion |
| Unknown framework pattern | Research, best guess | If critical path |

## Post-Error Documentation

Every error that required recovery must be documented:

```markdown
### Error Recovery Log — Task N

**Error:** {description}
**Severity:** Minor | Major | Critical
**Root Cause:** {why it happened}
**Resolution:** {what was done}
**Assumption:** {if any inference was made}
**Impact:** None | {affected tasks}
**Prevention:** {how to avoid in future}
```

This log goes into the completion report at the end of execution.
