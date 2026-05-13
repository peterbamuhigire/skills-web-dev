---
name: ios-quality-and-release
description: iOS quality and release orchestration for TDD, debugging, stability, App Store review, crash prevention, and release evidence.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# iOS Quality And Release
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Planning, implementing, or reviewing iOS testing, TDD, debugging, stability, crash prevention, App Store readiness, or release evidence.
- The task mentions Swift Testing, XCTest, LLDB, Instruments, crash triage, regression gates, TestFlight, App Review, privacy labels, or production readiness.
- A retired iOS quality/release skill is referenced by name.

## Do Not Use When

- The task is only general implementation; use `ios-development`.
- The task is primarily security/RBAC; use `ios-security-and-rbac`.
- The task is primarily StoreKit monetization; use `ios-monetization` plus this skill only for release evidence.

## Required Inputs

- Feature scope, risk level, test targets, crash or defect context, release channel, App Store requirements, and acceptance criteria.

## Workflow

1. Load `ios-development` for baseline implementation rules.
2. Choose the quality lane: TDD, debugging, stability hardening, or App Store release.
3. Load only the matching reference.
4. Produce executable tests, triage steps, release checklist updates, or review findings with concrete evidence.

## Quality Standards

- Risky code paths need deterministic tests before sign-off.
- Debugging guidance must identify reproduction, instrumentation, suspected layer, and validation.
- Release guidance must include App Store policy, privacy, performance, accessibility, and rollback evidence where applicable.

## Anti-Patterns

- Shipping iOS features with only manual happy-path testing.
- Treating crashes as isolated stack traces without reproduction and regression tests.
- Waiting until submission day to handle privacy labels, permissions, or review notes.

## Outputs

- iOS test plan, failing/passing tests, debug notes, crash RCA, stability checklist, App Store readiness checklist, or release evidence pack.

## References

- `references/ios-tdd.md` for Swift Testing/XCTest TDD workflow and test pyramid.
- `references/ios-debugging-mastery.md` for LLDB, Instruments, watchpoints, and advanced triage.
- `references/ios-stability-solutions.md` for crash prevention and resilient production patterns.
- `references/app-store-review.md` for App Store submission, policy, metadata, privacy, and review evidence.
<!-- dual-compat-end -->
