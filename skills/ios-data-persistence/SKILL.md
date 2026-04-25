---
name: ios-data-persistence
description: iOS data persistence standards with SwiftData as primary local storage
  and custom API backends for cloud sync. Covers UserDefaults, Keychain, SwiftData
  (models, queries, relationships, migrations), file storage, offline-first architecture,
  and...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# iOS Data Persistence
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- iOS data persistence standards with SwiftData as primary local storage and custom API backends for cloud sync. Covers UserDefaults, Keychain, SwiftData (models, queries, relationships, migrations), file storage, offline-first architecture, and...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ios-data-persistence` or would be better handled by a more specific companion skill.
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
| Data safety | Persistence model spec | Markdown doc per `skill-composition-standards/references/entity-model-template.md` covering Core Data / SwiftData entities | `docs/ios/persistence-model-orders.md` |
| Correctness | Persistence test plan | Markdown doc listing CRUD and migration test cases | `docs/ios/persistence-tests-orders.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
## Required Companion Skills

| Skill | When to Apply |
|---|---|
| `ios-swiftdata` | Deep SwiftData API — @Attribute, @Relationship, ModelActor, migrations, 10 anti-patterns |
| `dual-auth-rbac` | JWT/refresh-token storage and rotation |
| `api-pagination` | Paginated data fetching with local caching |
| `vibe-security-skill` | Security baseline for all web/API calls |
| `api-error-handling` | Consistent error handling in repository layer |

---

## 1. Storage Decision Guide

| Data Type | Storage | Example |
|---|---|---|
| User preferences | UserDefaults | Theme, language, sort order |
| Tokens / credentials | Keychain Services | JWT tokens, API keys, passwords |
| Structured app data | SwiftData (iOS 17+) | Products, orders, customers |
| Large files / images | FileManager | Photos, PDFs, exports |
| Temporary cache | URLCache / NSCache | API response caching |

**Rule of thumb:** simple flag/scalar = UserDefaults. Secret = Keychain. Relationships/querying = SwiftData. Binary blob = FileManager.

---

## Additional Guidance

Extended guidance for `ios-data-persistence` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `2. UserDefaults (Simple Preferences Only)`
- `3. Keychain Services (Security-Critical Data)`
- `4. SwiftData (Primary Local Storage — iOS 17+)`
- `5. Repository Pattern (API-Backed Sync)`
- `6. Offline-First Architecture`
- `7. DTO / Domain Model Mapping`
- `8. File Storage (Images, PDFs, Exports)`
- `9. iCloud Sync Options`
- `10. URLCache / NSCache (Temporary Caching)`
- `11. Cross-Skill References`
- `12. Anti-Patterns`