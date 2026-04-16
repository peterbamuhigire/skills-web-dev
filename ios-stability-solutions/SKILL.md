---
name: ios-stability-solutions
description: Crash-prevention and production stability patterns for iOS. Use when
  hardening an app, designing features for stability, or building a TDD safety net
  around critical business logic.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# iOS Stability Solutions Guide

<!-- dual-compat-start -->
## Use When

- Crash-prevention and production stability patterns for iOS. Use when hardening an app, designing features for stability, or building a TDD safety net around critical business logic.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ios-stability-solutions` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Operability | iOS crash and stability runbook | Markdown doc per `skill-composition-standards/references/runbook-template.md` covering crash triage, symbolication, and rollback | `docs/ios/stability-runbook.md` |
| Correctness | Crash regression test plan | Markdown doc listing reproduction steps and assertions for previously-fixed crashes | `docs/ios/crash-regression-tests.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Patterns for creating stable, crash-free iOS apps. Synthesised from
*iOS Developer Solutions Guide* (Narendar Singh Saini).

---

## 1. The Three Error Classes — Prevent Each Differently

The book classifies all iOS bugs into three classes with distinct prevention strategies:

### Class 1 — Syntax / Compile-time Errors
**Prevention:** Master the language. Gaps in Swift knowledge directly cause compile errors.
Key areas: functional operators (`map`, `filter`, `flatMap`, `reduce`, `compactMap`),
all initialiser types (designated, convenience, required, failable `init?`, throwable `init throws`),
property types (stored, lazy stored, computed, observers, wrappers), optional unwrapping
hierarchy, protocols, generics, async/await.

### Class 2 — Logical Errors (Silent, Dangerous)
**Prevention:** TDD. These compile and run but produce wrong output. They survive manual
QA. Users report them after release. Only unit test cases reliably catch them.

### Class 3 — Runtime Errors (Crashes, Business-Critical)
**Prevention:** Optional safety + throwable functions + do-catch coverage (see Section 2).

---

## Additional Guidance

Extended guidance for `ios-stability-solutions` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `2. Optional Safety Hierarchy — Eliminate Force Unwrap`
- `3. Throwable Functions for Error Propagation`
- `4. Dependency Injection — The Core of Testable, Stable Code`
- `5. SOLID Principles as Stability Rules`
- `6. TDD Safety Net — Red-Green-Refactor`
- `7. Architecture for Stability — MVVM Over Massive ViewController`
- `8. Over-Engineering as a Stability Risk`
- `9. UI Approach and Crash Surface Area`
- `10. Framework Access Levels — Public API Hardening`
- `11. Backend-Driven UI — Zero-Downtime Bug Mitigation`
- `12. DRY Principle — Prevent Inconsistency Bugs`
- `13. Bug Prevention Checklist`
