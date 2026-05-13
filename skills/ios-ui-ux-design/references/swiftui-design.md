---
name: swiftui-design
description: SwiftUI UI standards for beautiful, sleek, minimalistic iOS apps. Enforces
  modern SwiftUI patterns, consistent theming, smooth animations, and performance.
  Use when building or reviewing SwiftUI code to ensure modern, user-friendly interfaces...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# SwiftUI UI Standards
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- SwiftUI UI standards for beautiful, sleek, minimalistic iOS apps. Enforces modern SwiftUI patterns, consistent theming, smooth animations, and performance. Use when building or reviewing SwiftUI code to ensure modern, user-friendly interfaces...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `swiftui-design` or would be better handled by a more specific companion skill.
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
| UX quality | SwiftUI screen audit | Markdown doc reviewing layout, spacing, theming, and accessibility findings | `docs/ios/swiftui-audit-checkout.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
## Design Philosophy

**Goal:** Every screen should feel beautiful, sleek, fast, and effortless to use.

### Core Design Principles

1. **Minimalism over decoration** — Content first, chrome last. Remove anything that doesn't serve the user.
2. **Consistency over novelty** — Same patterns across every app screen.
3. **Visible affordances** — Controls must read as tappable without relying on animation, discovery, or overly subtle styling.
4. **Whitespace is a feature** — Generous spacing creates visual breathing room, not waste.
5. **Speed is UX** — If it feels slow, it's broken regardless of how it looks.
6. **Content-first hierarchy** — Important information is immediately visible.
7. **Touch-friendly targets** — Minimum 44pt for all interactive elements (Apple HIG).
8. **SF Symbols for icons** — Use SF Symbols for system icons unless custom icons are required per `mobile-custom-icons`.
9. **iOS 26 Liquid Glass** — For apps recompiled against iOS 26 SDK, adopt the Liquid Glass design language for translucent materials and depth.

### Visual Standards

| Element | Standard |
|---|---|
| **Corner radius** | 12pt cards, 8pt inputs, continuous corners via `.clipShape(RoundedRectangle(cornerRadius:, style: .continuous))` |
| **Card elevation** | Use `.shadow(radius: 2, y: 1)` — subtle, never heavy |
| **Content padding** | 16pt horizontal, 8-16pt vertical between items |
| **Screen padding** | 16pt compact, 20pt regular |
| **Touch targets** | Minimum 44pt height/width (Apple HIG) |
| **Icon size** | SF Symbols: 17pt body, 22pt title, 48pt empty states |
| **Typography** | Use system `Font` API exclusively |

## Additional Guidance

Extended guidance for `swiftui-design` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `Navigation Architecture (iOS 16+)`
- `TabView Architecture`
- `Modal Presentations`
- `Lists and Grids`
- `Theming System`
- `Animation Standards`
- `Loading / Empty / Error States`
- `Form Design`
- `Swift Charts (iOS 16+)`
- `Data Flow Pattern`
- `Performance Rules`
- `Patterns and Anti-Patterns`
- Additional deep-dive sections continue in the reference file.