---
name: ios-at-scale
description: Production iOS engineering for large teams and apps — modular architecture (RIBLETS, ComponentKit), Buck/Bazel build systems, trunk-based development, CI/CD pipeline design with coverage-based test selection, feature flags as release...
---

# iOS Development at Scale

Production-grade iOS engineering for large teams and apps. Distilled from Uber, Meta, Airbnb engineering decisions and iOS 18 fundamentals.

## Contents

1. [Modular Architecture](#1-modular-architecture)
2. [Build Systems](#2-build-systems)
3. [Trunk-Based Development](#3-trunk-based-development)
4. [Feature Flags as Infrastructure](#4-feature-flags-as-infrastructure)
5. [CI/CD Pipeline Design](#5-cicd-pipeline-design)
6. [Performance at Scale](#6-performance-at-scale)
7. [Swift Concurrency at Scale](#7-swift-concurrency-at-scale)
8. [iOS 18 Key Changes](#8-ios-18-key-changes)
9. [Anti-Patterns at Scale](#9-anti-patterns-at-scale)

---

## 1. Modular Architecture

### Why Monoliths Fail at Scale

Correct Gang-of-Four patterns still fail at scale if everything lives in one framework. A monolith means:
- Any change triggers a full module recompile
- Teams cannot evolve features independently
- Internal types bleed across domains — no enforcement possible
- CI build time scales linearly with codebase size

**Swift module boundaries are architectural enforcement**: internal types cannot cross module boundaries. Designing modules correctly makes it structurally impossible for teams to accidentally couple domains.

### RIBLETS (Uber)

After monolith collapse, Uber created RIBLETS: **R**outer, **I**nteractor, **B**uilder, optional **L**eaf, **E**xtension, **S**egue.

Each RIBLET is a self-contained module:
- **Builder**: creates the RIBLET and its dependencies (DI root)
- **Router**: owns child attachment/detachment (navigation tree)
- **Interactor**: pure business logic; consumes immutable model streams from a service layer
- **View/Presenter** (optional): stateless rendering

Unidirectional data flow — Interactor → Presenter → View — prevents state corruption across features. Service layer streams are immutable; Interactors cannot mutate shared state directly.

### ComponentKit (Meta/Facebook)

Modularising the UI rendering layer into its own framework let a dedicated team optimise independently.

Results:
- 70% reduction in rendering code
- Flatter view hierarchies
- Better scroll performance
- Async layout off the main thread (only possible because rendering was an isolated module)

**Pattern**: Large-scale UI optimisation requires isolating the rendering layer before optimising it. You cannot optimise what you cannot isolate.

---

## 2. Build Systems

### Decision Matrix

| System | Caching | Parallel Builds | Scales To |
|--------|---------|-----------------|-----------|
| CocoaPods | None | No | Small teams |
| SPM | Limited | No | Mid-size teams |
| Buck/Bazel | Remote + distributed | Yes | 100+ engineers |

CocoaPods rebuilds full modules on any change. SPM improves dependency management but lacks build caching. At scale, both are too slow.

### Buck/Bazel Key Capabilities

- **Remote artifact caching**: a colleague's compiled output is reused on your machine — no duplicate work
- **Incremental builds**: only affected targets and their dependents rebuild, not the full module tree
- **Build graph query interface**: analyse dependency chains, find circular dependencies, measure impact of a change
- **Multi-core parallelism**: multiple independent modules compile simultaneously

**Airbnb result**: flat directory structure caused 1-2 minute Xcode workspace load times. After adopting Buck, CI build times dropped 50%.

### Module Boundary Design Principles

1. **One team per module** — ownership is unambiguous
2. **Depend inward, not outward** — feature modules depend on core; core never depends on features
3. **No circular dependencies** — enforce with build graph queries in CI
4. **Expose protocols, not implementations** — cross-module contracts are minimal interfaces

---

## 3. Trunk-Based Development

Explicitly recommended over long-running feature branches. At 100+ PRs/hour, long branches produce compounding merge conflicts that become their own engineering workstream.

**The contract**: every commit to `main` must be production-safe. Feature flags gate unreleased work — not branches.

### Four-Stage CI Pipeline

| Stage | Trigger | Feedback Latency | Cost |
|-------|---------|-----------------|------|
| PR Submitted | Per PR | Earliest | Highest per-unit |
| Pre-Merge | At merge time | Early | High |
| Post-Commit | After landing on main | Delayed | High |
| Continuous | Scheduled (nightly) | Latest | Low |

Running the full test suite on every PR is prohibitively expensive. Fast snapshot tests run on PR submission; broader integration tests run at merge; full suite runs on schedule. This is not a compromise — it is a deliberate cost/signal tradeoff.

### Oncall Rotation for Main Branch

Engineers rotate responsibility for monitoring CI failures and reverting offending commits. Required because pre-merge tests will occasionally miss real failures. Without this rotation, a broken main becomes normalised.

### Signal-to-Noise Discipline (Non-Negotiable)

A flaky test must be fixed or deleted. No exceptions.

Engineers who bypass failing tests because "it's probably flaky" destroy the entire CI culture. The degradation is exponential:
- 1 flaky test/week: mild distrust
- 10 flaky tests/week: engineers stop treating CI red as a signal
- CI without trust is worse than no CI — it creates false confidence

---

## 4. Feature Flags as Infrastructure (Not Optional)

Feature flags are the enabling infrastructure for trunk-based development and safe releases. Treat them as a first-class platform concern, not a per-feature convenience.

### What Feature Flags Enable

| Capability | Description |
|------------|-------------|
| Safe trunk landings | Land features on main behind a flag — main is always shippable |
| Dogfooding | Internal employees → QA → limited external users |
| Phased rollout | 1% → 10% → 50% → 100% — observe metrics at each threshold |
| Kill switches | Disable any feature in production within minutes, no App Store submission |
| A/B testing | Hold out a cohort to confirm metric gains causally |

### Backtesting Pattern

After full rollout, hold out a small cohort (e.g. 2%) with the feature still disabled. Compare metrics. This confirms the feature caused the improvement rather than concurrent changes. Without this, you cannot distinguish causation from coincidence.

### Why Mobile Release Is Permanently Slower Than Web

- Cannot roll back a shipped binary — bad release requires a new App Store submission
- App Store review: 1-7 days, uncontrollable
- Device fragmentation requires broader test coverage

Feature flags plus phased rollout are the mobile answer to web's instant rollback. There is no other mechanism.

---

## 5. CI/CD Pipeline Design

Tool-agnostic principles. Works with Xcode Cloud, GitHub Actions, Fastlane, Bitrise.

### Coverage-Based Test Selection

Only run tests for modules actually affected by the diff. A UI module change must not trigger the full networking module test suite.

Implementation: build a dependency graph (Buck/Bazel provides this natively). For each PR, compute the set of affected modules, run only their associated test targets.

### Correlation Detection

If two tests always pass or fail together, they are testing the same code path. Run only one per diff. Over thousands of PRs per week, this meaningfully reduces CI cost without reducing coverage signal.

### Three CI Metrics to Track

| Metric | Definition | Target |
|--------|-----------|--------|
| **Reliability** | % of PRs that pass CI without a false failure | >99% |
| **Correctness** | How often main breaks after a green CI run | <0.5% |
| **Time-to-signal** | Minutes engineers wait for feedback | <10 min |

A CI system where engineers routinely bypass failures is worse than no CI at all — it creates the illusion of safety without the substance.

### Fastlane Integration

Use Fastlane for automation regardless of primary CI system:
- Code signing (`match` for certificate/provisioning profile management)
- Build number management (auto-increment on CI)
- TestFlight distribution
- App Store submission

Integrate Fastlane lanes into Buck/Bazel build definitions so CI and local builds use identical pipelines.

---

## 6. Performance at Scale

### Percentile Thinking (Critical)

Never evaluate performance using averages. Track P50, P90, P99.

- **P50**: median user experience
- **P90**: experience for users on older hardware or slow networks
- **P99**: reveals systematic problems — specific device models, geographic regions, network conditions

Dismissing P99 as "only 1% of users" is a business mistake. That cohort may be your highest-value or most loyal segment. P99 regressions also predict future P90 regressions as usage grows.

**Funnel logging**: instrument time at each pipeline stage for every user-facing operation:
```
Network request sent → Response received → Data parsed → First frame rendered
```
When a percentile degrades, the funnel tells you which stage regressed.

### Application Startup Optimisation

Apple target: first frame in ≤400ms.

**Profiling environment**: oldest supported device, release build, after reboot, airplane mode with network mocked. Never profile on a developer machine with a debug build — results are not meaningful.

**Startup optimisation checklist:**
```
□ Move non-essential initialisation out of UIApplicationDelegate
□ Replace +load with +initialize (lazy — called only when class first used)
□ Remove all unused linked frameworks (each adds DYLD3 linker cost)
□ Hard-link all dependencies (DYLD3 gains full visibility for pre-linking)
□ Lazy-load views not visible at launch
□ Push all non-critical work to background queues during startup
□ Replace String(describing:) with ObjectIdentifier for type identification
```

`String(describing:)` performs a protocol conformance check at runtime. `ObjectIdentifier` uses the type's memory address — O(1), no conformance lookup.

DoorDash engineering data: replacing `String(describing:)` gave 11% faster startup; hash value redesign added a further 29%.

**Profiling tools:**
- Instruments: App Launch template, Static Initializer Calls instrument
- MetricKit: production device aggregates — launch time, hang rate, memory
- Xcode Organizer: aggregate hang rate from production fleet
- Emerge Tools: deeper granularity than Instruments for binary size and startup

### Death by a Thousand Cuts

50 engineers each adding a "minor" feature with "no performance impact" produces severe regression over 2-3 years. Hardware improvements mask it until a new device generation stops arriving.

**Performance lifecycle (non-negotiable from day one):**

1. Background threads for all network/I/O — basic hygiene, not premature optimisation
2. Profile on real device before every release
3. Automated performance tests using `XCTestMetric`
4. MetricKit monitoring during beta/TestFlight
5. MetricKit + Xcode Organizer in production
6. Alert on threshold breaches; investigate with funnel logging

---

## 7. Swift Concurrency at Scale

### Actors Replace Serial GCD Queues

```swift
actor UserSessionStore {
    private var sessions: [String: UserSession] = [:]

    func store(_ session: UserSession, for userID: String) {
        sessions[userID] = session
    }

    func session(for userID: String) -> UserSession? {
        sessions[userID]
    }
}
```

**Actor advantage over GCD serial queues**: priority-based re-ordering. Swift actors avoid priority inversion — a high-priority task is not forced to wait behind a low-priority task queued earlier on the same serial queue.

### Structured Task Groups with Automatic Cancellation

```swift
Task.detached(priority: .background) {
    await withTaskGroup(of: Void.self) { group in
        group.addTask { await writeToCache(objects) }
        group.addTask { await logResult() }
    }
}
// Cancelling the top-level task automatically cancels all child tasks.
// Child tasks inherit parent priority — no manual priority propagation needed.
```

Structured concurrency makes the task tree explicit. Cancellation propagates downward automatically — no dangling async work after a parent completes.

### await Breaks Atomicity

`await` is an explicit suspension point. The thread running the async function may change after each `await`. Never hold a lock across an `await` — this violates the Swift runtime's forward progress contract and can deadlock.

```swift
// WRONG — lock held across suspension point
actor BrokenActor {
    var lock = NSLock()
    func dangerousMethod() async {
        lock.lock()
        await someAsyncWork()  // thread may change here; lock held by wrong thread
        lock.unlock()
    }
}

// CORRECT — actors provide implicit mutual exclusion; no explicit lock needed
actor CorrectActor {
    func safeMethod() async {
        await someAsyncWork()  // suspension is safe; actor serialises access
    }
}
```

**Architecture principle**: encapsulate concurrency at the library boundary. Callers of your module's API should not need to manage concurrent access — that is the module's responsibility, not the caller's.

---

## 8. iOS 18 Key Changes

### SwiftData — Production Patterns

```swift
@Model class JournalEntry {
    var date: Date
    var title: String
    @Attribute(.externalStorage) var photoData: Data?
    // Stores binary in adjacent file, not inline in the model store.
    // Without this, large blobs slow every fetch query for that model type.
}
```

SwiftData does not support `UIImage` directly — convert to `Data` for storage; decode asynchronously with `Task`. Inline blob storage is the single most common SwiftData performance mistake.

WWDC 2024 additions:
- Custom data stores: bring your own backing format (JSON, SQLite wrapper, etc.)
- Transaction history API: observe what changed and when
- Compound uniqueness constraints: multi-column uniqueness enforcement

### Swift Testing Framework

```swift
import Testing
@testable import MyApp

struct MyTests {
    @Test func validInitializationSucceeds() {
        let entry = JournalEntry(rating: 3, title: "Test")
        #expect(entry != nil)
        // #expect shows actual values in failures — not just "assertion failed"
        // Dramatically reduces time spent diagnosing failures in CI
    }

    @Test("Rejects out-of-range ratings", arguments: [-1, 0, 6, 100])
    func rejectsInvalidRating(rating: Int) {
        #expect(JournalEntry(rating: rating, title: "x") == nil)
    }
}
```

- Tests are structs (value types) — no `setUp`/`tearDown` lifecycle required
- `#expect` macro provides rich diagnostics with actual and expected values
- Parameterised tests via `arguments:` eliminate boundary-condition boilerplate
- Mix with XCTest in the same target during migration — no flag day required

### Apple Intelligence Integration (iOS 18)

Writing Tools appear automatically in `UITextView`. Handle delegate callbacks to prevent data consistency issues during AI transformation:

```swift
func textViewWritingToolsWillBegin(_ textView: UITextView) {
    textView.isEditable = false  // prevent data corruption during AI transformation
}
func textViewWritingToolsDidEnd(_ textView: UITextView) {
    textView.isEditable = true
}

// Opt out entirely for fields where AI transformation is inappropriate:
textView.writingToolsBehavior = .none
// e.g. code editors, password fields, structured data entry forms
```

### NavigationStack — Correct Modern SwiftUI Routing

```swift
@State private var navigationPath = NavigationPath()

NavigationStack(path: $navigationPath) {
    ContentView()
        .navigationDestination(for: Item.self) { item in
            DetailView(item: item)
            // Type-safe routing: destination determined by value type, not string tag
        }
        .navigationDestination(for: SettingsRoute.self) { route in
            SettingsView(route: route)
        }
}

// Programmatic navigation — type-safe, decoupled from view hierarchy:
navigationPath.append(selectedItem)

// Deep link: replace entire stack programmatically
navigationPath = NavigationPath([rootItem, childItem])
```

`NavigationStack` replaces deprecated `NavigationView`. The `path` binding enables deep linking and programmatic stack manipulation — essential for feature-flag-controlled onboarding flows and push notification routing.

---

## 9. Anti-Patterns at Scale

| Anti-Pattern | Why It Fails | Correct Approach |
|-------------|-------------|-----------------|
| Monolithic app target | Full recompile on any change; no team isolation | Modular framework graph with Buck/Bazel |
| Average-based performance metrics | Hides P99 cohort problems | Track P50/P90/P99 with funnel logging |
| Releases without feature flags | Any regression requires new App Store submission | Feature flags on everything; phased rollout |
| Long-running feature branches | Compound merge conflicts at 100+ PRs/day | Trunk-based development; flags gate dark code |
| Tolerating flaky tests | Engineers stop trusting CI; pipeline becomes theatre | Fix or delete; zero tolerance policy |
| `+load` methods | Eager class initialisation at startup adds unmeasured latency | Replace with `+initialize` (lazy) |
| `String(describing:)` for type identification | Protocol conformance check on every call | Use `ObjectIdentifier` (pointer equality, O(1)) |
| NSLock across `await` | Violates forward progress contract; potential deadlock | Use actors for mutual exclusion |
| Inline blob storage in SwiftData | Slows all model fetches | `@Attribute(.externalStorage)` for all `Data` |
| Manual certificate management in CI | Brittle, breaks on rotation | Fastlane `match` with shared certificate repo |

---

## References

- *iOS Development at Scale* — Eric Vennaro (modular architecture, RIBLETS, build systems, CI/CD)
- *iOS 18 Programming for Beginners* — SwiftData, Swift Testing, Apple Intelligence, NavigationStack
- Uber Engineering Blog: RIBs architecture
- Meta Engineering Blog: ComponentKit
- Airbnb Engineering Blog: Buck build system adoption
- Apple WWDC 2024: SwiftData enhancements, Swift Testing framework
- DoorDash Engineering: startup time optimisation case study
