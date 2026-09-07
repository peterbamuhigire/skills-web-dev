---
name: ios-development
description: Use when building or reviewing native iOS applications with Swift, SwiftUI, structured concurrency, security, tests, and performance gates; use focused iOS skills for persistence, release, or monetisation.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | iOS feature test plan | Markdown doc covering unit, UI, and snapshot tests | `docs/ios/feature-tests-checkout.md` |
| UX quality | Accessibility audit | Markdown doc covering VoiceOver, Dynamic Type, and contrast | `docs/ios/a11y-checkout.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
- `references/ios-project-setup.md` for Xcode project structure, SPM, schemes, build settings, and environment configuration.
- `references/ios-swift-recipes.md` for production Swift recipes, safe conversions, dates, Codable, hashing, and validation.
- `references/apple-platform-compatibility-wwdc26.md` for Xcode 27, Swift 6.4, iOS/iPadOS/macOS 27 SDK, Device Hub, coding agents, availability gates, and macOS/Safari watch items.
<!-- dual-compat-end -->
## Load Order

1. Load `world-class-engineering` for shared production gates.
2. Load `system-architecture-design` when the app participates in broader service or module architecture.
3. Load this skill for iOS implementation details.
4. Load `ios-ui-ux-design` for every user-facing iOS/iPadOS screen, especially premium, dashboard, onboarding, reporting, form, or revenue-critical flows.
5. Load `ios-security-and-rbac`, `ios-platform-capabilities`, or other focused parent skills as needed.

Production-grade Apple-platform development standards for AI-assisted implementation. Swift-first with SwiftUI, latest-SDK aware, and availability-gated for older deployment targets.

**Current Toolchain:** Xcode 27 on Apple Silicon | Swift 6.4 | latest iOS/iPadOS/macOS SDKs
**Core Stack:** Swift 6.4-ready | SwiftUI (default UI) | MVVM + Clean Architecture | Swift Concurrency
**Deployment Policy:** project-specific floor; iOS 17+ remains acceptable only when the app must support that fleet
**Compatibility:** Must run on both the declared minimum deployment target and the latest Apple OS, with availability gates for SDK-only features
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

## Decision Rules

| Condition | Choice |
|---|---|
| New interface on supported OS versions | SwiftUI |
| Legacy UIKit surface with stable behaviour | Wrap and migrate by feature, not by file |
| Concurrent mutable resource | Actor ownership or MainActor for UI state |
| Unsupported OS capability | Explicit availability branch and useful fallback |

## Degraded Mode

Without Xcode or devices, return code plus an execution matrix for compile, Swift Testing, UI, accessibility, Instruments, and oldest-supported-OS checks. Static review is not release evidence.

## Domain Anti-Patterns

- Launching unstructured tasks without ownership. Fix: bind work to a lifecycle or actor.
- Force-unwrapping external data. Fix: validate and expose typed failure states.
- Blocking the main actor with I/O. Fix: isolate work and measure UI responsiveness.
- Hiding availability failures. Fix: render an explicit supported fallback.
- Treating simulator success as device readiness. Fix: exercise the physical-device matrix.

Extended guidance for `ios-development` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `Swift Language Standards`
- `Architecture: MVVM + Clean Architecture`
- `Project Structure`
- `State Management (iOS 17+ — No Legacy Patterns)`
- `Networking Layer`
- `Build Configuration (3 Environments)`
- `WWDC26 Apple Platform Compatibility`
- `Security Standards`
- `Testing Strategy`
- `Performance Rules`
- `Release Gate`
- `Navigation (iOS 17+)`
- `Minimum Requirements`
- Additional deep-dive sections continue in the reference file.

For screen quality, visual polish, native interaction, Dynamic Type, VoiceOver, iPad adaptation, and premium UX gates, load `ios-ui-ux-design` alongside this implementation skill.
## Inputs
| Artefact | Required? | Purpose |
|---|---|---|
| iOS requirements, supported OS/devices, architecture, UX, and service contracts | yes | Bound implementation |
## Outputs
- Produce iOS code or design with lifecycle, accessibility, tests, performance, and release evidence.
## Capability contract
Read/search and local builds follow task scope; signing, provisioning, TestFlight/App Store publication, and destructive data operations require explicit authority.
