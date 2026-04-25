---
name: android-room
description: Comprehensive Room database skill for Android — entities, DAOs, relations,
  migrations, conflict resolution, FTS4, views, paging, SQLCipher, and testing. Built
  from Mark Murphy's "Elements of Android Room". Use alongside android-data-persistence
  for full offline-first architecture.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Android Room Database
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Comprehensive Room database skill for Android — entities, DAOs, relations, migrations, conflict resolution, FTS4, views, paging, SQLCipher, and testing. Built from Mark Murphy's "Elements of Android Room". Use alongside android-data-persistence for full offline-first architecture.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `android-room` or would be better handled by a more specific companion skill.
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
| Data safety | Room schema migration plan | Markdown doc per `skill-composition-standards/references/migration-plan-template.md` | `docs/android/room-migration-2026-04-16.md` |
| Correctness | Room DAO test plan | Markdown doc covering DAO, Flow, and migration tests | `docs/android/room-tests-orders.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
## 1. Overview

Three core components:

```
@Entity (data classes) → @Dao (SQL + suspend/Flow) → @Database (registry + builder)
        ↓                          ↑
   TypeConverters          @Transaction wrappers
```

Room generates SQLite boilerplate at compile time via KSP. All writes are `suspend`; reactive reads return `Flow`.

## 2. Gradle Dependencies

```kotlin
val roomVersion = "2.6.1"
implementation("androidx.room:room-runtime:$roomVersion")
implementation("androidx.room:room-ktx:$roomVersion")
ksp("androidx.room:room-compiler:$roomVersion")           // KSP, NOT kapt
implementation("androidx.room:room-paging:$roomVersion")  // optional, Paging 3
testImplementation("androidx.room:room-testing:$roomVersion")
testImplementation("app.cash.turbine:turbine:1.1.0")      // Flow testing
// Plugin: id("com.google.devtools.ksp") version "2.0.0-1.0.21"
// Schema: ksp { arg("room.schemaLocation", "$projectDir/schemas") }
```

## Additional Guidance

Extended guidance for `android-room` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `3. Entities`
- `4. TypeConverters`
- `5. DAOs`
- `6. Database Class`
- `7. Relations`
- `8. Transactions`
- `9. Conflict Resolution`
- `10. Migrations`
- `11. Full-Text Search (FTS4)`
- `12. Database Views`
- `13. Paging 3`
- `14. Pre-Populated Databases`
- Additional deep-dive sections continue in the reference file.