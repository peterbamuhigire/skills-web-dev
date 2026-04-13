---
name: ai-error-handling
description: Validation and error handling for AI-generated code. Use when verifying
  AI output, building production code, or ensuring code correctness. Enforces automatic
  quality checks and validation loops.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---


## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# AI Error Handling & Validation

<!-- dual-compat-start -->
## Use When

- Validation and error handling for AI-generated code. Use when verifying AI output, building production code, or ensuring code correctness. Enforces automatic quality checks and validation loops.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ai-error-handling` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## When to Use This Skill

Use when:
- Claude generates code (always validate)
- Building production code (quality gates required)
- Reviewing AI output (systematic verification)
- Ensuring code correctness (automated checks)

**This skill automatically enforces validation patterns.**

---

## The 5-Layer Validation Stack

Every AI-generated code MUST pass through all 5 layers:

```
Layer 1: Syntax Check ─→ Can it parse?
    ↓
Layer 2: Requirement Check ─→ Does it meet specs?
    ↓
Layer 3: Test Check ─→ Do tests pass?
    ↓
Layer 4: Security Check ─→ Any vulnerabilities?
    ↓
Layer 5: Documentation Check ─→ Can Claude explain it?
    ↓
APPROVED ✓
```

---

## Additional Guidance

Extended guidance for `ai-error-handling` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `Layer 1: Syntax Validation`
- `Layer 2: Requirement Validation`
- `Layer 3: Test Validation`
- `Layer 4: Security Validation`
- `Input Validation`
- `SQL Injection Prevention`
- `XSS Prevention`
- `Authentication & Authorization`
- `Data Exposure`
- `Error Handling`
- `Layer 5: Documentation Validation`
- `The Validation Loop`
- Additional deep-dive sections continue in the reference file.
