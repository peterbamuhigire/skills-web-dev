---
name: swiftui-pro-patterns
description: Advanced SwiftUI patterns from Pro SwiftUI (Hudson, 2022). Deep layout
  mechanics, identity, animation, custom layouts, environment/preferences, drawing,
  and performance.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# SwiftUI Pro Patterns
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Advanced SwiftUI patterns from Pro SwiftUI (Hudson, 2022). Deep layout mechanics, identity, animation, custom layouts, environment/preferences, drawing, and performance.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `swiftui-pro-patterns` or would be better handled by a more specific companion skill.
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
| Correctness | SwiftUI advanced pattern test plan | Markdown doc covering identity, custom layouts, and animation regression tests | `docs/ios/swiftui-advanced-tests.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Advanced patterns for experienced SwiftUI developers. Covers the internals that make SwiftUI tick.

## 1. Layout System Deep Dive

### The Three-Step Layout Process

1. Parent proposes a size to its child
2. Child chooses its own size -- parent MUST respect it
3. Parent positions the child in its coordinate space

### Six Sizing Values (Every View Has These)

| Value | Purpose |
|-------|---------|
| **minWidth / minHeight** | Least space accepted; below this the view "leaks" out |
| **maxWidth / maxHeight** | Most space accepted; excess is ignored |
| **idealWidth / idealHeight** | Preferred size (like UIKit intrinsicContentSize) |

**Key insight:** `fixedSize()` promotes ideal size to be both min and max size.

```swift
// fixedSize on one axis -- text wraps horizontally but grows vertically
Text("Long text here")
    .fixedSize(horizontal: false, vertical: true)

// Make two HStack children the same height
HStack {
    Text("Short").padding().frame(maxHeight: .infinity).background(.yellow)
    Text("Much longer text").padding().frame(maxHeight: .infinity).background(.cyan)
}
.fixedSize(horizontal: false, vertical: true)
```

### Layout Neutrality

Views that adapt to whatever space is available. `Color.red` fills all space; as a background it shrinks to its child.

```swift
// Color in ScrollView gets nominal 10pt height (replacingUnspecifiedDimensions default)
ScrollView { Color.red } // Only 10pt tall

// Fix: provide explicit ideal height
ScrollView {
    Color.red.frame(idealHeight: 400, maxHeight: 400)
}
```

### ModifiedContent and Modifier Stacking

Every modifier (mostly) creates a new `ModifiedContent` wrapper view. Modifiers do NOT mutate the original view.

```swift
// Two frames = two separate wrapper views (fixed + flexible)
Text("Hello")
    .frame(width: 250)      // Fixed width wrapper
    .frame(minHeight: 400)  // Flexible height wrapper
```

**Anti-pattern:** Thinking `frame()` changes the text itself. It wraps it.

## Additional Guidance

Extended guidance for `swiftui-pro-patterns` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `2. View Identity (Critical for Performance)`
- `3. Animation Patterns`
- `4. Environment and Preferences`
- `5. Custom Layouts (Layout Protocol)`
- `6. Drawing and Effects`
- `7. Performance Patterns`
- `Anti-Patterns Summary`