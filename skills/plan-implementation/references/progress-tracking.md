# Progress Tracking — Logging, Status Updates, Completion Reports

## Real-Time Progress Logging

Every action during execution is logged with this format:

```
[PHASE X/4] {Phase Name}
  [TASK Y/N] {Task Name}
    [STEP] {Action}... {RESULT}
```

### Log Level Guide

| Level | When | Example |
|-------|------|---------|
| **PHASE** | Starting a new execution phase | `[PHASE 2/4] DATABASE & MODELS` |
| **TASK** | Starting a new plan task | `[TASK 3/12] User Authentication` |
| **STEP** | Each action within a task | `[RED] Writing test...` |
| **RESULT** | Outcome of a step | `PASS`, `FAIL`, `SKIP`, `DONE` |
| **ERROR** | Something went wrong | `[ERROR] Migration failed: table exists` |
| **FIX** | Recovery action taken | `[FIX] Using ALTER instead of CREATE` |
| **SCORE** | Validation score | `[SCORE] 92/100 — ACCEPTED` |
| **STATUS** | Task completion | `[STATUS] Task 3: COMPLETED ✅` |

### Example Full Log

```
[PHASE 1/4] SCAFFOLD & SETUP
  [TASK 1/12] Create Directory Structure
    [STEP] Creating app/Services/Invoice/... DONE
    [STEP] Creating app/Models/Invoice.php stub... DONE
    [STEP] Creating tests/Feature/InvoiceTest.php stub... DONE
    [STATUS] Task 1: COMPLETED ✅

[PHASE 2/4] DATABASE & MODELS
  [TASK 2/12] Invoice Migration
    [STEP] Creating migration 2026_02_21_create_invoices_table... DONE
    [STEP] Defining columns (id, franchise_id, customer_id, ...)... DONE
    [STEP] Adding indexes (franchise_id, customer_id, invoice_date)... DONE
    [STEP] Adding foreign keys... DONE
    [STATUS] Task 2: COMPLETED ✅

  [TASK 3/12] Invoice Model
    [RED] Writing test: createInvoice_validData_returnsInvoice... DONE
    [RED] Writing test: createInvoice_missingCustomer_throwsError... DONE
    [RED] Running tests → 2 FAILED (expected) ✅
    [GREEN] Implementing Invoice model with relationships... DONE
    [GREEN] Running tests → 2 PASSED ✅
    [VALIDATE] Layer 1 (Syntax): PASS
    [VALIDATE] Layer 2 (Requirements): PASS
    [VALIDATE] Layer 3 (Tests): PASS (2/2)
    [VALIDATE] Layer 4 (Security): PASS
    [VALIDATE] Layer 5 (Docs): PASS
    [SCORE] 95/100 — ACCEPTED
    [STATUS] Task 3: COMPLETED ✅
```

## Plan File Status Updates

Update the plan's markdown file in-place as tasks complete.

### Status Markers

| Marker | Meaning |
|--------|---------|
| `⬜ NOT STARTED` | Task not yet begun |
| `🔄 IN PROGRESS` | Currently executing |
| `✅ COMPLETED` | Done, tests passing, validated |
| `⚠️ COMPLETED WITH NOTES` | Done but with assumptions/deviations |
| `❌ BLOCKED` | Cannot proceed, needs human input |
| `⏭️ SKIPPED` | Intentionally skipped (not applicable) |

### Per-Task Status Block

Add this block after each task in the plan file:

```markdown
**Execution Status:**
- Status: ✅ COMPLETED
- Tests: 5/5 passing
- Quality Score: 92/100
- Files Created: `app/Http/Controllers/InvoiceController.php`
- Files Modified: `routes/api.php`
- Assumptions: None
- Errors Recovered: 1 (migration conflict, used ALTER)
```

## Completion Report

Generate at the end of all plan execution.

### Report Template

```markdown
# Plan Implementation — Completion Report

**Plan:** {plan file path}
**Executed:** {date}
**Duration:** {total time or task count}

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | {N} |
| Completed | {N} ✅ |
| With Notes | {N} ⚠️ |
| Blocked | {N} ❌ |
| Skipped | {N} ⏭️ |
| Completion Rate | {X}% |

## Test Results

| Suite | Tests | Pass | Fail | Skip |
|-------|-------|------|------|------|
| Unit | {N} | {N} | {N} | {N} |
| Feature/Integration | {N} | {N} | {N} | {N} |
| E2E | {N} | {N} | {N} | {N} |
| **Total** | **{N}** | **{N}** | **{N}** | **{N}** |

## Quality Scores

| Task | Score | Status |
|------|-------|--------|
| Task 1: {name} | {N}/100 | ✅ |
| Task 2: {name} | {N}/100 | ✅ |
| ... | ... | ... |
| **Average** | **{N}/100** | — |

## Files Created

| File | Type | Task |
|------|------|------|
| {path} | Controller | Task 3 |
| {path} | Migration | Task 2 |
| ... | ... | ... |

## Files Modified

| File | Change | Task |
|------|--------|------|
| {path} | Added route | Task 4 |
| ... | ... | ... |

## Error Recovery Log

| Task | Error | Severity | Resolution |
|------|-------|----------|------------|
| Task 2 | Migration conflict | Minor | Used ALTER |
| ... | ... | ... | ... |

## Assumptions Made

| Task | Assumption | Rationale |
|------|-----------|-----------|
| Task 5 | Used Argon2ID for hashing | Per dual-auth-rbac skill |
| ... | ... | ... |

## Remaining Work

{If any tasks blocked or skipped}

| Task | Reason | Action Needed |
|------|--------|---------------|
| Task 10 | Missing API spec | Need API contract document |

## Recommended Next Steps

1. Run `implementation-status-auditor` to verify completeness
2. {Any manual verification needed}
3. {Any deployment preparation}
```

## Progress Dashboard (For Long Plans)

For plans with 10+ tasks, output a progress dashboard periodically:

```
═══════════════════════════════════════════
  PLAN EXECUTION PROGRESS: 7/12 tasks
═══════════════════════════════════════════
  Phase 1: SCAFFOLD     ████████████ 100%
  Phase 2: DATABASE      ████████████ 100%
  Phase 3: BUSINESS      ██████░░░░░░  50%
  Phase 4: UI            ░░░░░░░░░░░░   0%
═══════════════════════════════════════════
  Tests: 23 pass / 0 fail
  Avg Score: 91/100
  Errors Recovered: 2
═══════════════════════════════════════════
```

## Integration with Auditor

After the completion report, recommend running the `implementation-status-auditor` skill:

```
[FINAL] Plan execution complete.
  Recommendation: Run implementation-status-auditor to verify
  against the original plan and identify any remaining gaps.

  Output directory: docs/implementation/review-{date}/
```

This creates a feedback loop:

```
feature-planning (creates plan)
    ↓
plan-implementation (executes plan) ← THIS SKILL
    ↓
implementation-status-auditor (verifies results)
    ↓
plan-implementation (fixes gaps, if any)
```
