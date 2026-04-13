---
name: ios-swift-recipes
description: Production Swift recipes from real App Store apps. Covers safe numeric
  conversion, Codable tricks, custom decoders, type-safe Dictionary extraction, ISO
  8601 dates, UIKit navigation/alerts/maps, UIView effects (shadows, gradients, blur),
  keyboard...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# iOS Swift Recipes — App Store Production Patterns

<!-- dual-compat-start -->
## Use When

- Production Swift recipes from real App Store apps. Covers safe numeric conversion, Codable tricks, custom decoders, type-safe Dictionary extraction, ISO 8601 dates, UIKit navigation/alerts/maps, UIView effects (shadows, gradients, blur), keyboard...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ios-swift-recipes` or would be better handled by a more specific companion skill.
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
Concrete, copy-pasteable Swift from *Swift Recipes for iOS Developers* (Nekrasov).

---

## 1. Safe Numeric Conversions

```swift
extension Double {
    var asInt16: Int16? { Int16(exactly: self.rounded()) }
    var asInt: Int?     { Int(exactly: self.rounded()) }
}
// Never: Int16(someDouble) — crashes on out-of-range
// Always: someDouble.asInt16 — returns nil safely

// Prices: store as Int cents, never Double
extension Int    { var asPrice: String { String(format: "%d.%02d", self/100, self%100) } }
extension Double {
    var asPrice: String {
        guard let cents = (self * 100.0).asInt else { return "" }
        return String(format: "%d.%02d", cents/100, cents%100)
    }
}
```

---

## Additional Guidance

Extended guidance for `ios-swift-recipes` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `2. Reusable NumberFormatter (Critical for scroll performance)`
- `3. ISO 8601 Date Handling`
- `4. Encodable/Decodable Universal Extensions`
- `5. Custom Decoder — Handle API Type Mismatches`
- `6. Type-Safe Dictionary Extraction`
- `7. String Validation`
- `8. SHA256 Password Hashing with Salt`
- `9. UIViewController Navigation Helpers`
- `10. UIView Visual Effects (IBDesignable)`
- `11. Keyboard Handling — Animated Layout Shift`
- `12. UITextField Real-Time Formatting`
- `13. UIImage Processing`
- Additional deep-dive sections continue in the reference file.
