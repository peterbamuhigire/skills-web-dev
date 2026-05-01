# ios-swiftdata Skill + iOS Skills Boost — Design Doc

**Date:** 2026-04-11
**Status:** Approved

---

## Goal

Build a comprehensive standalone `ios-swiftdata` skill (the iOS counterpart to `android-room`),
boost `ios-development` with full Swift concurrency patterns from *Practical Swift Concurrency*
(Donny Wals, 2025), and update `ios-data-persistence` to reference the new skill.

---

## Sources Used

| Book / Resource | Relevant Output |
|---|---|
| *SwiftData Mastery in SwiftUI* (Mark Moeykens, Big Mountain Studio, Feb 2024) | Primary source for ios-swiftdata |
| *Practical Swift Concurrency* (Donny Wals, 2025 — Swift 6.2) | Concurrency boost for ios-development |
| *iOS App Development For Beginners* (Code With Nathan) | Beginner-facing patterns + @Query usage |
| Apple SwiftData Docs (fetched from developer.apple.com/documentation/swiftdata) | Full API surface, ModelActor, History |
| SwiftyPlace CRUD Tutorial | Practical CRUD patterns, gotchas |

---

## Deliverable 1: `ios-swiftdata/SKILL.md`

### Architecture

Pure SwiftData API reference — no sync engine, no repository pattern.
Analogous to `android-room`. The offline-first sync layer stays in `ios-data-persistence`.

### Sections (14 total, target ~490 lines)

| # | Section | Key Content |
|---|---|---|
| 1 | Core 4-part flow | @Model → ModelContainer → ModelContext → View |
| 2 | @Model macro | Class-only, auto-Observable, Identifiable, Sendable, supported types |
| 3 | @Attribute options | .unique (upsert), .ephemeral, .externalStorage, .allowsCloudEncryption, originalName, .transformable |
| 4 | @Transient vs @Attribute(.ephemeral) | Comparison table: persistence, observability, predicate support |
| 5 | @Relationship | 1:1, 1:many, many:many; delete rules; min/max counts; inverse gotcha (set on ONE side only) |
| 6 | ModelContainer | Minimal, multi-model, in-memory, custom config, result handler, mock data pattern |
| 7 | ModelContext | Full API: insert, delete, delete(model:where:), fetch, fetchCount, save, rollback |
| 8 | FetchDescriptor | predicate, sortBy, fetchLimit, fetchOffset, includePendingChanges, prefetching; preview crash workaround |
| 9 | @Query | filter, sort, animation, dynamic sort/filter; vs manual fetch difference |
| 10 | Schema migration | VersionedSchema, SchemaMigrationPlan, lightweight vs custom, typealias pattern |
| 11 | ModelActor | Background work, Sendable rules table, perf (~4x faster), when to use vs not |
| 12 | Testing | In-memory container, @MainActor static var preview, #Preview crash fix |
| 13 | CloudKit requirements | Optional props, no .unique, no .deny, private DB only limitation |
| 14 | Anti-patterns & gotchas | 18 entries from all sources |

---

## Deliverable 2: `ios-development` concurrency boost

Add a new **Section: Swift Concurrency** covering:

- async/await basics, .task modifier, .task(id:), Task.yield()
- @MainActor annotation + MainActor.run
- Actors: isolation, reentrancy gotcha, nonisolated methods
- async let (parallel child tasks)
- TaskGroup (dynamic parallel, varying return types, concurrency limiting)
- Sendable protocol (what qualifies, @Sendable closures)
- Swift 6.1/6.2 isolation model (nonisolated vs @concurrent)

---

## Deliverable 3: `ios-data-persistence` update

- Update SwiftData sections (4–6) to add: "For deep SwiftData API reference, see `ios-swiftdata` skill"
- Add `ios-swiftdata` to the Required Companion Skills table

---

## Deliverable 4: CLAUDE.md registration

Add `ios-swiftdata` to the skills index under `ios-data-persistence`.

---

## Constraints

- All .md files must stay under 500 lines (doc-standards.md)
- ios-swiftdata is pure API reference only — no sync engine, no repository
- Skill must be self-contained (all examples complete and correct)
