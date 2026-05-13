---
name: android-ui-ux-design
description: Specialized Android UI/UX design skill for premium Jetpack Compose apps. Use alongside android-development when Android screens must be beautiful, native, usable, accessible, and commercially credible.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Android UI/UX Design
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Designing or reviewing Android app screens, Compose components, navigation, dashboards, forms, onboarding, or settings.
- The user asks for native Android UI polish, premium UX, mobile ergonomics, Material 3, or app pleasantness.
- An Android app is connected to a business backend and must feel trustworthy enough for real customers.

## Do Not Use When

- The task is not Android or Android-adjacent.
- The work is backend-only and has no user-facing Android surface.

## Required Inputs

- Target screens, user task, device classes, brand/product context, backend constraints, and any existing screenshots or Compose components.
- Confirm whether the deliverable is design guidance, implementation, review, QA, or documentation.

## Workflow

1. Load `android-development` for implementation standards.
2. Load `premium-ui-ux-design` and specifically `references/mobile-android-ios-premium-ux.md`.
3. Define the primary mobile task, top-level destinations, and device classes.
4. Choose Material 3 components and adaptive navigation before custom patterns.
5. Model every Compose screen state: loading, content, empty, error, offline, permission denied, and syncing.
6. Apply the Android mobile quality gate before implementation or review sign-off.

## Android UX Standards

- Use Material 3, Compose, semantic tokens, and adaptive layout by default.
- Use bottom navigation for 3-5 primary destinations on compact screens; use navigation rail or pane layouts on larger screens.
- Minimum touch target is 48 dp.
- Respect edge-to-edge layout, system bars, back navigation, and platform permission flows.
- Use `WindowSizeClass`, not hardcoded tablet checks.
- Business reports over 25 rows should use table-first or dense list patterns, not endless cards.
- Every primary workflow must work offline or fail with a clear recovery path when the domain requires field use.
- Support TalkBack, font scaling, dark mode, contrast, and reduced motion.

## Quality Standards

- Android screens feel native to Material 3 and the app's domain.
- Navigation, state handling, touch targets, typography, and accessibility are verified on compact and expanded layouts where applicable.
- Premium UX gate categories must score at least 8/10 before sign-off.

## Anti-Patterns

- Squeezing web layouts into a phone UI.
- Building card walls for dense reports.
- Ignoring TalkBack, font scaling, offline states, or Android back behavior.

## Outputs

- Android UI brief, Compose component guidance, navigation model, state matrix, accessibility notes, or review findings.

## References

- `../premium-ui-ux-design/references/mobile-android-ios-premium-ux.md`
- `../premium-ui-ux-design/references/premium-ui-ux-gate.md`
- `../android-development/references/ui-design-system.md`
- `references/jetpack-compose-ui.md` for Compose-specific Material 3, layout, animation, navigation, and component patterns.
<!-- dual-compat-end -->
