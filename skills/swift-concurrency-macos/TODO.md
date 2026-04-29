# TODO: swift-concurrency-macos Skill

## Purpose

Create a skill for Swift Concurrency in macOS apps, with emphasis on actor boundaries, UI isolation, cancellation, and bridging legacy Apple APIs.

## Why GlassHub Needs It

- Git operations, GitHub API calls, repository scanning, indexing, analytics aggregation, and persistence should never block the main actor.
- AppKit and libgit2 bridges need explicit isolation rules.

## Study Before Writing

- Swift Concurrency documentation.
- Actors, `Sendable`, structured concurrency, cancellation, and task groups.
- MainActor and Observation framework.
- Bridging callback APIs to async/await.
- Swift 6 strict concurrency migration.

## Skill Should Cover

- App actor, Git actor, Network actor, Persistence actor, and Analytics actor patterns.
- Cancellation and progress reporting.
- `Sendable` model design.
- Avoiding detached task misuse.
- MainActor handoff rules.
- Testing async code deterministically.

## Starter Evidence To Collect

- Actor boundary diagram.
- Sendable review checklist.
- Async test patterns for cancellation and ordering.
