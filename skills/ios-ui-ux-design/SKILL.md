---
name: ios-ui-ux-design
description: Specialized iOS UI/UX design skill for premium SwiftUI apps. Use alongside ios-development when iPhone or iPad screens must be beautiful, native, usable, accessible, and commercially credible.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# iOS UI/UX Design
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Designing or reviewing iOS/iPadOS screens, SwiftUI components, navigation, dashboards, forms, onboarding, or settings.
- The user asks for native iOS polish, premium UX, pleasantness, or App Store-quality experience.
- A business app must feel trustworthy, fast, accessible, and Apple-native.

## Do Not Use When

- The task is not iOS, iPadOS, or Apple-platform adjacent.
- The work is backend-only and has no user-facing iOS surface.

## Required Inputs

- Target screens, user task, device classes, brand/product context, backend constraints, and any existing screenshots or SwiftUI components.
- Confirm whether the deliverable is design guidance, implementation, review, QA, or documentation.

## Workflow

1. Load `ios-development` for implementation standards.
2. Load `premium-ui-ux-design` and specifically `references/mobile-android-ios-premium-ux.md`.
3. Define the primary iOS task, top-level destinations, navigation hierarchy, and device classes.
4. Choose SwiftUI-native patterns before custom controls.
5. Model every screen state: loading, content, empty, error, offline, permission denied, and syncing.
6. Apply the iOS mobile quality gate before implementation or review sign-off.

## iOS UX Standards

- Use SwiftUI, platform-native navigation stacks, tab bars, sheets, forms, lists, menus, and toolbars.
- Minimum touch target is 44 pt.
- Preserve swipe-back and native gesture expectations.
- Support Dynamic Type, VoiceOver, Reduce Motion, Increase Contrast, Dark Mode, and SF Symbols consistency.
- Use sheets for focused tasks; avoid full-screen covers unless the workflow truly requires takeover.
- Avoid Android-style components, web-like navigation, and cramped desktop tables on phones.
- For iPad, use split views, sidebars, and multi-column layouts where they improve productivity.

## Quality Standards

- iOS screens feel native to SwiftUI and Apple platform conventions.
- Navigation, state handling, touch targets, Dynamic Type, VoiceOver, and iPad adaptations are verified where applicable.
- Premium UX gate categories must score at least 8/10 before sign-off.

## Anti-Patterns

- Squeezing web layouts into a phone UI.
- Copying Android component patterns into iOS.
- Ignoring VoiceOver, Dynamic Type, swipe-back, offline states, or sheet/navigation conventions.

## Outputs

- iOS UI brief, SwiftUI component guidance, navigation model, state matrix, accessibility notes, or review findings.

## References

- `../premium-ui-ux-design/references/mobile-android-ios-premium-ux.md`
- `../premium-ui-ux-design/references/premium-ui-ux-gate.md`
- `../ios-development/references/skill-deep-dive.md`
- `references/swiftui-design.md` for SwiftUI-native layout, navigation, forms, accessibility, and visual polish.
- `references/swiftui-pro-patterns.md` for advanced SwiftUI layout, identity, animation, and performance patterns.
- `references/ios-uikit-advanced.md` for UIKit diffable data sources, compositional layout, custom transitions, and UIKit interop.
<!-- dual-compat-end -->
