---
name: ios-tdd
description: iOS Test-Driven Development standards. Enforces Red-Green-Refactor cycle,
  test pyramid (70/20/10), layer-specific testing strategies with XCTest and Swift
  Testing, and CI integration. Use when building or reviewing iOS apps with TDD methodology.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# iOS Test-Driven Development (TDD)

<!-- dual-compat-start -->
## Use When

- iOS Test-Driven Development standards. Enforces Red-Green-Refactor cycle, test pyramid (70/20/10), layer-specific testing strategies with XCTest and Swift Testing, and CI integration. Use when building or reviewing iOS apps with TDD methodology.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ios-tdd` or would be better handled by a more specific companion skill.
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

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
## Overview

TDD is a development process where you write tests **before** feature code, following the **Red-Green-Refactor** cycle. Every feature starts with a failing test, gets minimal implementation, then is refined.

**Core Principle:** No production code without a failing test first.

**Preferred Framework:** Swift Testing (`@Test` macro) for all new unit and integration tests. Use XCTest only for UI tests (XCUITest) and legacy test suites.

**Dependency Injection:** Protocol-based injection — no DI framework required. Define protocols for all external dependencies, inject via initialiser parameters.

## Quick Reference

| Topic                   | Section                                  | Covers                                            |
| ----------------------- | ---------------------------------------- | ------------------------------------------------- |
| **TDD Workflow**        | [Red-Green-Refactor](#the-red-green-refactor-cycle) | Step-by-step cycle with Swift examples   |
| **Test Pyramid**        | [Test Pyramid](#test-pyramid-702010)     | Unit, integration, UI split                       |
| **Swift Testing**       | [Swift Testing](#swift-testing-framework) | @Test macro, #expect, async testing              |
| **Mocking**             | [Protocol Mocking](#protocol-based-mocking) | Protocol-based mocks, no library needed        |
| **Network Mocking**     | [URLProtocol Mock](#urlprotocol-for-network-mocking) | URLProtocol subclass for API tests      |
| **UI Tests**            | [XCUITest](#xcuitest-for-critical-flows) | End-to-end UI testing                             |
| **CI Setup**            | [CI Pipeline](#ci-pipeline)              | Xcode Cloud, GitHub Actions                       |

## Additional Guidance

Extended guidance for `ios-tdd` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `The Red-Green-Refactor Cycle`
- `Test Pyramid (70/20/10)`
- `TDD Workflow for iOS Features`
- `Swift Testing Framework`
- `Protocol-Based Mocking`
- `Testing @Observable ViewModels`
- `URLProtocol for Network Mocking`
- `SwiftData / Core Data Testing`
- `XCUITest for Critical Flows`
- `Test Naming Convention`
- `Patterns and Anti-Patterns`
- `Integration with Other Skills`
- Additional deep-dive sections continue in the reference file.
