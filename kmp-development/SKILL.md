---
name: kmp-development
description: Kotlin Multiplatform shared module development standards for sharing
  business logic across Android and iOS while keeping native UI. Covers project structure
  (shared/composeApp/iosApp), source sets, targets, expect/actual, DI (Koin)...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Kotlin Multiplatform Development Standards

<!-- dual-compat-start -->
## Use When

- Kotlin Multiplatform shared module development standards for sharing business logic across Android and iOS while keeping native UI. Covers project structure (shared/composeApp/iosApp), source sets, targets, expect/actual, DI (Koin)...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `kmp-development` or would be better handled by a more specific companion skill.
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
## Strategy: Shared Logic, Native UI

KMP shares business logic (domain, data, networking) across platforms. Each
platform keeps its native UI framework: Jetpack Compose for Android, SwiftUI
for iOS. This preserves the best user experience on each platform while
eliminating business logic duplication.

## Module-to-Skill Mapping

| Module | Governs | Skill |
|---|---|---|
| `shared/` | Business logic, data, networking | **This skill** (kmp-development) |
| `composeApp/` | Android UI, platform integration | android-development |
| `iosApp/` | iOS UI, platform integration | ios-development |

## Project Structure

Every KMP project has three modules:

```text
project-root/
  shared/                    # Shared Kotlin module (this skill governs)
    src/
      commonMain/            # Shared code (domain, data, use cases)
        kotlin/
        resources/
      androidMain/           # Android-specific implementations
        kotlin/
        AndroidManifest.xml
      iosMain/               # iOS-specific implementations
        kotlin/
      commonTest/            # Shared tests
      androidUnitTest/       # Android-specific tests
      iosTest/               # iOS-specific tests
    build.gradle.kts         # KMP Gradle config
  composeApp/                # Android app (follow android-development skill)
    src/main/
    build.gradle.kts
  iosApp/                    # iOS Xcode project (follow ios-development skill)
    iosApp/
    iosApp.xcodeproj
  build.gradle.kts           # Root build file
  gradle/libs.versions.toml  # Version catalog
```

## Additional Guidance

Extended guidance for `kmp-development` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `Technology Stack`
- `Source Sets and Targets`
- `Architecture: Clean Architecture in Shared Module`
- `Expect/Actual Pattern`
- `Dependency Injection with Koin`
- `Networking with Ktor`
- `Database with SQLDelight`
- `Modularization`
- `Native Library Integration`
- `Tooling`
- `Mandatory Rules`
- `Anti-Patterns`
