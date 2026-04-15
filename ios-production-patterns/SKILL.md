---
name: ios-production-patterns
description: Production-grade iOS patterns that separate good apps from great apps
  — UIViewController lifecycle gotchas, sensor lifecycle management, delegate pattern
  implementation, keyboard dismissal, Core Data migration, UIImagePickerController
  dismissal...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# iOS Production Patterns

<!-- dual-compat-start -->
## Use When

- Production-grade iOS patterns that separate good apps from great apps — UIViewController lifecycle gotchas, sensor lifecycle management, delegate pattern implementation, keyboard dismissal, Core Data migration, UIImagePickerController dismissal...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ios-production-patterns` or would be better handled by a more specific companion skill.
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
Expert-level, ship-it details that tutorials skip. Each pattern reflects a real
production bug or App Store rejection that could have been avoided.

---

## 1. ViewController Lifecycle — The Exact Sequence

```swift
override func viewDidLoad() {
    super.viewDidLoad()
    // Called ONCE. Wire outlets, configure appearance, set initial data.
    // Never start sensors, timers, or location here.
}

override func viewWillAppear(_ animated: Bool) {
    super.viewWillAppear(animated)
    // Called EVERY time screen is shown.
    // Refresh data from external sources here.
    locationManager.startUpdatingLocation()
}

override func viewDidAppear(_ animated: Bool) {
    super.viewDidAppear(animated)
    // Animation complete. Start timers here.
}

override func viewWillDisappear(_ animated: Bool) {
    super.viewWillDisappear(animated)
    // Stop sensors BEFORE leaving. Save state.
    locationManager.stopUpdatingLocation()
}

override func viewDidDisappear(_ animated: Bool) {
    super.viewDidDisappear(animated)
    // Release non-persistent resources.
}
```

**Critical rules:**
- Start `CLLocationManager`, sensors, timers in `viewWillAppear` — never `viewDidLoad`
- Stop them in `viewWillDisappear` — never `viewDidDisappear` (too late for some sensors)
- Refresh data in `viewWillAppear` so it's current every time the screen is visible

---

## Additional Guidance

Extended guidance for `ios-production-patterns` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `2. Delegate Pattern — Full Implementation (6 Steps)`
- `3. Sensor Lifecycle — Location`
- `4. Camera Integration — Four Gotchas`
- `5. Keyboard Dismissal`
- `6. Gesture Recognizer State Guard`
- `7. Core Data Lightweight Migration (Mandatory Before Any Schema Change)`
- `8. Programmatic UI Constraints — Two Rules`
- `9. HealthKit — Partial Permissions Pattern`
- `10. Core ML on Background Thread`
- `11. SwiftUI / UIKit Integration`
- `12. SwiftUI vs UIKit Decision`
- `13. App Store Submission Checklist`
- Additional deep-dive sections continue in the reference file.
