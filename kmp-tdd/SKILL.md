---
name: kmp-tdd
description: Kotlin Multiplatform Test-Driven Development standards for shared module
  testing. Covers Red-Green-Refactor in commonTest, kotlin.test + Kotest + Turbine
  + Mokkery, test doubles (fakes/stubs/mocks), unit tests for use cases and ViewModels...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# KMP Test-Driven Development Standards

<!-- dual-compat-start -->
## Use When

- Kotlin Multiplatform Test-Driven Development standards for shared module testing. Covers Red-Green-Refactor in commonTest, kotlin.test + Kotest + Turbine + Mokkery, test doubles (fakes/stubs/mocks), unit tests for use cases and ViewModels...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `kmp-tdd` or would be better handled by a more specific companion skill.
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
## Overview

Testing shared KMP code is critical -- a bug in `commonMain` impacts **all
platforms simultaneously**. This skill enforces Red-Green-Refactor discipline
for the shared module. Platform-specific UI testing follows the respective
platform TDD skill (android-tdd for composeApp/, ios-tdd for iosApp/).

## Test Pyramid for KMP

```text
        /  UI Tests  \        <- Platform-specific (android-tdd / ios-tdd)
       / Integration  \       <- Shared + infrastructure (Ktor, SQLDelight)
      /   Unit Tests    \     <- Shared business logic (commonTest)
```

| Type | Ratio | Location | What to Test |
|---|---|---|---|
| Unit | 70% | commonTest | Use cases, repositories, ViewModels, utilities |
| Integration | 20% | commonTest | Ktor + SQLDelight with test doubles |
| UI | 10% | Platform tests | Compose/SwiftUI (see platform TDD skills) |

## Red-Green-Refactor Cycle

1. **RED**: Write a failing test in `commonTest` for the next behaviour
2. **GREEN**: Write the minimum shared code to make the test pass
3. **REFACTOR**: Clean up while tests stay green
4. **VERIFY**: Run `./gradlew :shared:allTests` to confirm all platforms pass

Never skip the verify step. Code that passes on JVM may fail on Kotlin/Native.

## Additional Guidance

Extended guidance for `kmp-tdd` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `Test Configuration`
- `Test Doubles: When to Use Each`
- `Unit Tests`
- `Integration Tests`
- `DI in Tests with Koin`
- `Running Tests`
- `Coverage with Kover`
- `Best Practices`
- `Anti-Patterns`
