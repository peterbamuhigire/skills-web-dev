---
name: ios-swiftdata
description: Comprehensive SwiftData API reference (iOS 17+) — @Model, @Attribute,
  @Relationship, ModelContainer, ModelContext, FetchDescriptor, @Query, schema migrations,
  ModelActor for background work, CloudKit requirements, testing, and 10 anti-patterns.
  Use alongside ios-data-persistence for offline-first sync engine.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# iOS SwiftData

<!-- dual-compat-start -->
## Use When

- Comprehensive SwiftData API reference (iOS 17+) — @Model, @Attribute, @Relationship, ModelContainer, ModelContext, FetchDescriptor, @Query, schema migrations, ModelActor for background work, CloudKit requirements, testing, and 10 anti-patterns. Use alongside ios-data-persistence for offline-first sync engine.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ios-swiftdata` or would be better handled by a more specific companion skill.
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
**iOS 17+, Swift 5.9+.** Primary local storage layer — built on Core Data with modern Swift macros.

## Required Companion Skills

| Skill | When to Apply |
|---|---|
| `ios-data-persistence` | Offline-first sync engine, repository pattern, pending ops queue |
| `ios-development` | MVVM architecture, SwiftUI integration, `references/concurrency.md` |

---

## 1. Core 4-Part Architecture

```
@Model  ──→  ModelContainer  ──→  ModelContext  ──→  View (@Query)
defines          stores              operates          displays
```

- **`@Model`** — Macro that defines a persistent class. Also makes it `@Observable`.
- **`ModelContainer`** — Manages schema + storage config. `Sendable` — safe across actors.
- **`ModelContext`** — In-memory workspace: insert, fetch, delete, save, rollback. NOT `Sendable`.
- **`@Query`** — SwiftUI property wrapper for reactive, always-fresh data. MainActor-bound.

---

## Additional Guidance

Extended guidance for `ios-swiftdata` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `2. @Model Macro`
- `3. @Attribute Options`
- `4. @Relationship`
- `5. ModelContainer Setup`
- `6. ModelContext Full API`
- `7. FetchDescriptor`
- `8. @Query`
- `9. Schema Migration`
- `10. ModelActor (Background Work)`
- `11. Testing`
- `12. CloudKit Requirements`
- `13. Anti-Patterns & Gotchas`
