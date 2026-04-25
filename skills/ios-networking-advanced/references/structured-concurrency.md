# Structured Concurrency Patterns for Networking

Modern Swift concurrency patterns for iOS networking. Load when using async-let parallel requests, task groups for fan-out, or structured task management.

## Table of Contents

1. [async-let — Parallel Independent Requests](#1-async-let--parallel-independent-requests)
2. [Task Groups — Dynamic Fan-Out](#2-task-groups--dynamic-fan-out)
3. [Data Race Prevention in Task Groups](#3-data-race-prevention-in-task-groups)
4. [Task Priorities and Detached Tasks](#4-task-priorities-and-detached-tasks)
5. [Cancellation Propagation](#5-cancellation-propagation)

---

## 1. async-let — Parallel Independent Requests

`async-let` starts an async function immediately without suspending. The `await` is deferred until the value is first used — enabling true parallelism within a single function.

```swift
// Sequential (slow — waits for each before starting next)
let user    = try await client.request(.user(id: userId))
let orders  = try await client.request(.orders(userId: userId))
let stats   = try await client.request(.stats(userId: userId))
// Total: t(user) + t(orders) + t(stats)

// Parallel with async-let (fast — all three start concurrently)
async let user    = client.request(.user(id: userId)) as UserProfile
async let orders  = client.request(.orders(userId: userId)) as [Order]
async let stats   = client.request(.stats(userId: userId)) as DashboardStats

// Awaited together — waits for the slowest, not the sum
let (profile, orderList, dashboard) = try await (user, orders, stats)
// Total: max(t(user), t(orders), t(stats))
```

**Rule**: Use `async-let` when requests are independent (no output of one is input to another). If either throws, Swift cancels all remaining `async-let` bindings automatically.

---

## 2. Task Groups — Dynamic Fan-Out

Use when the number of concurrent tasks is not known at compile time (e.g., fetch N items in parallel).

```swift
func fetchProfiles(for userIds: [String]) async throws -> [UserProfile] {
    try await withThrowingTaskGroup(of: UserProfile.self) { group in
        for id in userIds {
            group.addTask { try await self.client.request(.user(id: id)) }
        }
        // Collect results — order is NOT guaranteed
        var profiles: [UserProfile] = []
        for try await profile in group {
            profiles.append(profile)
        }
        return profiles
    }
}

// Bounded concurrency — avoid hammering the server with 1000 simultaneous requests
func fetchProfilesBounded(ids: [String], maxConcurrent: Int = 10) async throws -> [UserProfile] {
    try await withThrowingTaskGroup(of: UserProfile.self) { group in
        var profiles: [UserProfile] = []
        var pending = ids.makeIterator()

        // Seed up to maxConcurrent tasks
        for _ in 0..<min(maxConcurrent, ids.count) {
            if let id = pending.next() { group.addTask { try await self.client.request(.user(id: id)) }
            }
        }
        // As each completes, add the next one
        for try await profile in group {
            profiles.append(profile)
            if let id = pending.next() { group.addTask { try await self.client.request(.user(id: id)) } }
        }
        return profiles
    }
}
```

---

## 3. Data Race Prevention in Task Groups

**Critical**: Never mutate shared state from inside `addTask` closures. The closure runs on its own Task — mutations are data races.

```swift
// WRONG — race condition: multiple tasks write to shared dict simultaneously
var profileMap: [String: UserProfile] = [:]
group.addTask {
    let profile = try await self.client.request(.user(id: id))
    profileMap[id] = profile  // ← DATA RACE
    return profile
}

// CORRECT — return values, collect via for-await sequentially
var profileMap: [String: UserProfile] = [:]
group.addTask { (id, try await self.client.request(.user(id: id))) }

for try await (id, profile) in group {
    profileMap[id] = profile  // ← safe, runs sequentially in the parent task
}
```

**Rule**: Design task groups to `return` values. Build shared state *outside* the group body, *after* `for await`.

---

## 4. Task Priorities and Detached Tasks

```swift
// Unstructured Task — inherits actor context + priority from parent
Task {
    await analytics.log(.pageViewed)  // runs on same actor as caller
}

// Detached Task — inherits NOTHING: no actor, no priority, no task-local values
Task.detached(priority: .background) {
    // Safe for: background logging, cache writes, telemetry
    // Never captures UI state — it may run after the calling view is gone
    await telemetry.flush()
}

// Priority values (hints to the scheduler, not guarantees)
// .userInteractive — animations, immediate response (main thread)
// .userInitiated   — user-triggered async work (default for Task { })
// .utility         — progress indicators, data feeds
// .background      — prefetch, cleanup, non-urgent sync
```

**When to use detached**: work that must survive the calling context being cancelled (e.g., analytics event should fire even if the VC that triggered it is dismissed).

---

## 5. Cancellation Propagation

```swift
// Structured cancellation — cancelling a TaskGroup cancels all children
func loadDashboard() async throws -> Dashboard {
    try await withThrowingTaskGroup(of: DashboardSection.self) { group in
        group.addTask { try await self.fetchHeader() }
        group.addTask { try await self.fetchFeed() }
        group.addTask { try await self.fetchSidebar() }

        var sections: [DashboardSection] = []
        do {
            for try await section in group { sections.append(section) }
        } catch {
            group.cancelAll()  // cancel remaining on first failure
            throw error
        }
        return Dashboard(sections: sections)
    }
}

// Cooperative cancellation — check periodically in long loops
for item in largeDataset {
    try Task.checkCancellation()  // throws CancellationError if cancelled
    await process(item)
}

// Task.yield() — hints system to run higher-priority tasks before continuing
for chunk in chunks {
    await Task.yield()
    await processChunk(chunk)
}
```

**Rule**: Long loops must call `Task.checkCancellation()` or `Task.yield()` to remain responsive to cancellation. Pure CPU loops that never suspend never cooperate with the scheduler.
