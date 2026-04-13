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

<!-- dual-compat-start -->
## Use When

- Advanced SwiftUI patterns from Pro SwiftUI (Hudson, 2022). Deep layout mechanics, identity, animation, custom layouts, environment/preferences, drawing, and performance.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `swiftui-pro-patterns` or would be better handled by a more specific companion skill.
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

## 2. View Identity (Critical for Performance)

### Structural vs Explicit Identity

- **Structural:** SwiftUI infers identity from position in the view hierarchy
- **Explicit:** We assign identity with `.id()` or `Identifiable` conformance

### The _ConditionalContent Problem

`if/else` in `@ViewBuilder` creates `_ConditionalContent` -- SwiftUI treats true/false branches as DIFFERENT views.

```swift
// BAD: Destroys state, kills animations, recreates platform views
if scaleUp {
    ExampleView(scale: 2)
} else {
    ExampleView(scale: 1)
}

// GOOD: Single view, preserves identity, smooth animation
ExampleView(scale: scaleUp ? 2 : 1)
```

**Rule:** Always prefer ternary operators over if/else in view builders.

### Extracting from @ViewBuilder to Preserve Identity

Moving conditional logic to a computed property WITHOUT `@ViewBuilder` removes `_ConditionalContent`:

```swift
// Identity preserved because both branches return same type
var exampleView: some View {
    if scaleUp {
        return ExampleView(scale: 2)
    } else {
        return ExampleView(scale: 1)
    }
}
```

### Hidden Modifier Trap

```swift
// BAD: hidden() lacks a Bool parameter, forces if/else
extension View {
    func hidden(_ hidden: Bool) -> some View {
        self.opacity(hidden ? 0 : 1) // Preserves identity
    }
}
```

### Intentionally Discarding Identity

Use `.id(UUID())` to force SwiftUI to treat views as new, gaining control over transitions:

```swift
List(items, id: \.self) { Text("Item \($0)") }
    .id(UUID())
    .transition(.asymmetric(insertion: .move(edge: .trailing),
                            removal: .move(edge: .leading)))
```

## 3. Animation Patterns

### Animatable Protocol (Animate Anything)

Create a `ViewModifier` conforming to `Animatable` to animate non-animatable properties:

```swift
struct AnimatableZIndexModifier: ViewModifier, Animatable {
    var index: Double
    var animatableData: Double {
        get { index }
        set { index = newValue }
    }
    func body(content: Content) -> some View {
        content.zIndex(index)
    }
}

extension View {
    func animatableZIndex(_ index: Double) -> some View {
        self.modifier(AnimatableZIndexModifier(index: index))
    }
}
```

### Animatable Views (Not Just Modifiers)

```swift
struct CountingText: View, Animatable {
    var value: Double
    var animatableData: Double {
        get { value }
        set { value = newValue }
    }
    var body: some View {
        Text(value.formatted(.number.precision(.fractionLength(2))))
    }
}
```

### Custom Timing Curves

```swift
extension Animation {
    static var easeInOutBack: Animation {
        .timingCurve(0.5, -0.5, 0.5, 1.5)
    }
    static func easeInOutBack(duration: TimeInterval = 0.2) -> Animation {
        .timingCurve(0.5, -0.5, 0.5, 1.5, duration: duration)
    }
}
```

### Animation Override Hierarchy

```swift
// 1. Respect Reduce Motion globally
func withMotionAnimation<Result>(_ animation: Animation? = .default,
    _ body: () throws -> Result) rethrows -> Result {
    if UIAccessibility.isReduceMotionEnabled {
        return try body()
    } else {
        return try withAnimation(animation, body)
    }
}

// 2. Disable implicit animation on demand
func withoutAnimation<Result>(_ body: () throws -> Result) rethrows -> Result {
    var transaction = Transaction()
    transaction.disablesAnimations = true
    return try withTransaction(transaction, body)
}

// 3. Override implicit animation with explicit
func withHighPriorityAnimation<Result>(_ animation: Animation? = .default,
    _ body: () throws -> Result) rethrows -> Result {
    var transaction = Transaction(animation: animation)
    transaction.disablesAnimations = true
    return try withTransaction(transaction, body)
}
```

### Per-View Transaction Overrides

```swift
// Delay animation per-circle for wave effect (leaf views only!)
Circle()
    .fill(useRedFill ? .red : .blue)
    .frame(height: 64)
    .transaction { $0.animation = $0.animation?.delay(Double(i) / 10) }
```

**Warning:** Apple strongly recommends `transaction()` on leaf views only, not containers.

## 4. Environment and Preferences

### Custom Environment Keys (Prefer Over @EnvironmentObject)

```swift
struct FormElementIsRequiredKey: EnvironmentKey {
    static var defaultValue = false
}
extension EnvironmentValues {
    var required: Bool {
        get { self[FormElementIsRequiredKey.self] }
        set { self[FormElementIsRequiredKey.self] = newValue }
    }
}
extension View {
    func required(_ makeRequired: Bool = true) -> some View {
        environment(\.required, makeRequired)
    }
}
```

### Why @Environment > @EnvironmentObject

| Feature | @Environment | @EnvironmentObject |
|---------|-------------|-------------------|
| Default value | Required (safe) | None (crashes if missing) |
| Granularity | Per-key path | Entire object |
| Refresh scope | Only views using that key | ALL views observing the object |

**Key insight:** `@Environment(\.theme.strokeWidth)` watches only that sub-path. An `@EnvironmentObject` refreshes for ANY published property change.

### transformEnvironment for Relative Overrides

```swift
// Instead of overriding the font entirely:
Image(systemName: "sun.max")
    .transformEnvironment(\.font) { font in
        font = font?.weight(.black)
    }
```

### Preference Keys (Child-to-Parent Data Flow)

```swift
struct WidthPreferenceKey: PreferenceKey {
    static let defaultValue = 0.0
    static func reduce(value: inout Double, nextValue: () -> Double) {
        value = nextValue() // Last value wins
    }
}
// Sum all values: value += nextValue()
// First value only: leave reduce body empty (never call nextValue)
```

### Anchor Preferences (Geometry Across Coordinate Spaces)

Use `anchorPreference` + `overlayPreferenceValue` + `GeometryProxy` to resolve opaque anchors into usable frames. Pattern: animated underline bar (Airbnb-style category selector).

## 5. Custom Layouts (Layout Protocol)

### Required Methods

```swift
struct MyLayout: Layout {
    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews,
                      cache: inout Void) -> CGSize {
        proposal.replacingUnspecifiedDimensions() // Take offered space
    }
    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize,
                       subviews: Subviews, cache: inout Void) {
        for (index, subview) in subviews.enumerated() {
            let viewSize = subview.sizeThatFits(.unspecified)
            subview.place(at: point, anchor: .center, proposal: .unspecified)
        }
    }
}
```

### AnyLayout for Animated Layout Switching

```swift
let layouts = [AnyLayout(VStackLayout()), AnyLayout(HStackLayout()),
               AnyLayout(ZStackLayout()), AnyLayout(GridLayout())]
// Switch with animation -- preserves state, platform views, and animations
withAnimation { currentLayout = (currentLayout + 1) % layouts.count }
```

### Layout Priority for Relative Widths

Hijack `layoutPriority()` to specify proportional widths in a custom `RelativeHStack`.

### Subview Spacing Queries

```swift
let distance = subviews[index].spacing.distance(
    to: subviews[index + 1].spacing, along: .horizontal)
```

## 6. Drawing and Effects

### Canvas + TimelineView for Particle Systems

```swift
TimelineView(.animation) { timeline in
    Canvas { ctx, size in
        ctx.blendMode = .plusLighter
        ctx.addFilter(.blur(radius: 10))
        for particle in particleSystem.particles {
            ctx.opacity = particle.deathDate - timelineDate
            ctx.fill(Circle().path(in: rect), with: .color(.cyan))
        }
    }
}
```

**Key:** Use a plain class (not ObservableObject) with `@State` for particle systems -- avoids change-tracking overhead.

## 7. Performance Patterns

### Debouncing with Combine

```swift
class Debouncer<T>: ObservableObject {
    @Published var input: T
    @Published var output: T
    private var debounce: AnyCancellable?

    init(initialValue: T, delay: Double = 1) {
        self.input = initialValue
        self.output = initialValue
        debounce = $input
            .debounce(for: .seconds(delay), scheduler: DispatchQueue.main)
            .sink { [weak self] in self?.output = $0 }
    }
}
```

### Task-Based Debouncing (No Combine)

```swift
class ViewModel: ObservableObject {
    private var refreshTask: Task<Void, Error>?
    func scheduleWork() {
        refreshTask?.cancel()
        refreshTask = Task {
            try await Task.sleep(until: .now + .seconds(3), clock: .continuous)
            doWorkNow()
        }
    }
}
```

### @State for Expensive Non-Observable Objects

```swift
// CIContext is expensive to create -- use @State as a cache
@State private var context = CIContext()
// NOT @StateObject (would watch for changes we don't need)
// NOT let (would recreate every body invocation)
```

### onFirstAppear (Run Once)

```swift
struct OnFirstAppearModifier: ViewModifier {
    @State private var hasLoaded = false
    var perform: () -> Void
    func body(content: Content) -> some View {
        content.onAppear {
            guard hasLoaded == false else { return }
            hasLoaded = true
            perform()
        }
    }
}
extension View {
    func onFirstAppear(perform: @escaping () -> Void) -> some View {
        modifier(OnFirstAppearModifier(perform: perform))
    }
}
```

### Diagnosing Unnecessary Redraws

```swift
// 1. Random background color to visualize redraws
extension ShapeStyle where Self == Color {
    static var random: Color {
        Color(red: .random(in: 0...1), green: .random(in: 0...1), blue: .random(in: 0...1))
    }
}

// 2. _printChanges() in body
var body: some View {
    let _ = Self._printChanges()
    Text("Example")
}

// 3. Debug helpers compiled out in release
extension View {
    func debugPrint(_ value: @autoclosure () -> Any) -> some View {
        #if DEBUG
        print(value())
        #endif
        return self
    }
}
```

### Platform-Specific Modifiers

```swift
public extension View {
    func watchOS<Content: View>(_ modifier: @escaping (Self) -> Content) -> some View {
        #if os(watchOS)
        modifier(self)
        #else
        self
        #endif
    }
}
// Usage: Text("Hello").watchOS { $0.padding(0) }
```

### SwiftUI Lifecycle Rules

1. `@State` properties are created BEFORE `init()` runs
2. `init()` is called far more often than `onAppear()` -- never do slow work there
3. `onAppear()` runs before `task()`
4. DetailView.init() runs even before the view is shown (NavigationLink pre-creates)
5. `body` can be reinvoked at any time -- keep it fast

## Anti-Patterns Summary

| Anti-Pattern | Why It Hurts | Fix |
|-------------|-------------|-----|
| `if/else` for styling variants | Destroys state, breaks animation | Ternary operator |
| `@EnvironmentObject` for simple values | Refreshes all observers on any change | `@Environment` with custom keys |
| Slow work in `init()` | Called repeatedly by SwiftUI | Move to `onAppear()` or `task()` |
| `.animation()` without `value:` | Deprecated; animates everything | Always provide `value:` parameter |
| `AnyView` for type erasure | Destroys identity | Use `@ViewBuilder` or `AnyLayout` |
| `hidden()` via `if/else` | _ConditionalContent destroys state | `.opacity(hidden ? 0 : 1)` |
| Network calls in `init()` | View struct recreated frequently | Use `task()` or `onAppear()` |
