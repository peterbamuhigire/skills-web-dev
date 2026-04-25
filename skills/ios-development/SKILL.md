---
name: ios-development
description: iOS development standards for AI agent implementation. Swift-first, SwiftUI,
  MVVM + Clean Architecture, async/await, comprehensive security, testing, and performance
  patterns. Use when building or reviewing iOS applications, generating Swift...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# iOS Development Standards
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- iOS development standards for AI agent implementation. Swift-first, SwiftUI, MVVM + Clean Architecture, async/await, comprehensive security, testing, and performance patterns. Use when building or reviewing iOS applications, generating Swift...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ios-development` or would be better handled by a more specific companion skill.
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
| Correctness | iOS feature test plan | Markdown doc covering unit, UI, and snapshot tests | `docs/ios/feature-tests-checkout.md` |
| UX quality | Accessibility audit | Markdown doc covering VoiceOver, Dynamic Type, and contrast | `docs/ios/a11y-checkout.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
## Load Order

1. Load `world-class-engineering` for shared production gates.
2. Load `system-architecture-design` when the app participates in broader service or module architecture.
3. Load this skill for iOS implementation details.
4. Load `ios-app-security`, `ios-networking-advanced`, or other focused skills as needed.

Production-grade iOS development standards for AI-assisted implementation. Swift-first with SwiftUI, following modern Apple platform best practices.

**Core Stack:** Swift 6.0+ | SwiftUI (default UI) | MVVM + Clean Architecture | Swift Concurrency
**Min Deployment:** iOS 17+ | **IDE:** Xcode 16+
**Compatibility:** Must run flawlessly on both the minimum deployment target AND the latest iOS release
**Reference App:** Apple's sample code gallery and WWDC sessions — canonical examples of modern SwiftUI patterns

## Backend Environments

iOS apps connect to a PHP/MySQL backend deployed across three environments:

| Environment | Base URL Pattern | Database | Notes |
|---|---|---|---|
| **Development** | `http://{LAN_IP}:{port}/DMS_web/api/` | MySQL 8.4.7 (Windows WAMP) | Use host machine LAN IP |
| **Staging** | `https://staging.{domain}/api/` | MySQL 8.x (Ubuntu VPS) | For QA and TestFlight |
| **Production** | `https://{domain}/api/` | MySQL 8.x (Debian VPS) | App Store release |

Configure base URLs using Xcode build configurations and `.xcconfig` files so each scheme targets the correct backend. All backends use `utf8mb4_unicode_ci` collation and MySQL 8.x.

## Additional Guidance

Extended guidance for `ios-development` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `Swift Language Standards`
- `Architecture: MVVM + Clean Architecture`
- `Project Structure`
- `State Management (iOS 17+ — No Legacy Patterns)`
- `Networking Layer`
- `Build Configuration (3 Environments)`
- `Security Standards`
- `Testing Strategy`
- `Performance Rules`
- `Release Gate`
- `Navigation (iOS 17+)`
- `Minimum Requirements`
- Additional deep-dive sections continue in the reference file.