# Swift Concurrency Reference

Source: *Practical Swift Concurrency* — Donny Wals, 2025 (Swift 6.2)

---

## async/await Basics

```swift
// Mark a function async — it can suspend without blocking the thread
func fetchProducts() async throws -> [Product] {
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode([Product].self, from: data)
}

// Call async from synchronous context
func onAppear() {
    Task { await loadData() }
}

// .task modifier — auto-cancelled when view disappears
.task { await loadData() }

// .task(id:) — re-runs when id changes (like onChange)
.task(id: selectedId) {
    guard let id = selectedId else { return }
    product = try? await repository.fetch(id)
}
```

**Task.yield()** — for CPU-bound loops that don't naturally suspend:
```swift
func processAll(_ items: [Item]) async {
    for item in items {
        await Task.yield()   // yields only if other work is waiting
        process(item)
    }
}
```

---

## @MainActor

```swift
// Entire class on main actor
@MainActor class ProductViewModel: ObservableObject {
    @Published var products: [Product] = []
    func load() async { products = try! await service.fetchAll() }
}

// Single function on main actor
@MainActor func updateUI(with products: [Product]) {
    self.products = products
}

// Escape to main actor from any context
await MainActor.run { self.products = loaded }
```

---

## Actors

```swift
actor ImageCache {
    private var cache: [URL: UIImage] = [:]

    func image(for url: URL) async throws -> UIImage {
        if let cached = cache[url] { return cached }
        // Suspension point — another task CAN enter here (reentrancy)
        let image = try await download(url)
        if cache[url] == nil { cache[url] = image }   // re-check after suspension
        return cache[url]!
    }

    // nonisolated — callable without await from outside actor
    nonisolated func description(for url: URL) -> String { url.lastPathComponent }
}

// External callers must await actor methods
let img = try await cache.image(for: url)
// nonisolated members need no await
let desc = cache.description(for: url)
```

**Reentrancy:** When an actor suspends on `await`, other tasks may run actor methods.
Always re-check state after any `await` inside an actor body.

---

## Structured Concurrency

**async let — parallel child tasks (known count):**
```swift
func loadDashboard() async throws -> Dashboard {
    async let user = fetchUser()       // starts immediately
    async let stats = fetchStats()     // starts immediately, parallel
    return Dashboard(user: try await user, stats: try await stats)
}
```

**TaskGroup — dynamic parallel tasks:**
```swift
func fetchAll(ids: [Int]) async throws -> [Product] {
    try await withThrowingTaskGroup(of: Product.self) { group in
        for id in ids { group.addTask { try await fetch(id: id) } }
        var results: [Product] = []
        for try await product in group { results.append(product) }
        return results
    }
}
```

**Preserve order from TaskGroup:**
```swift
try await withThrowingTaskGroup(of: (Int, Product).self) { group in
    for (i, id) in ids.enumerated() {
        group.addTask { (i, try await fetch(id: id)) }
    }
    var pairs: [(Int, Product)] = []
    for try await pair in group { pairs.append(pair) }
    return pairs.sorted { $0.0 < $1.0 }.map { $0.1 }
}
```

**Limit concurrency in TaskGroup:**
```swift
var iterator = urls.makeIterator()
// Seed initial batch
while activeTasks < maxConcurrent, let url = iterator.next() {
    group.addTask { try await fetch(url) }; activeTasks += 1
}
// Replenish as each completes
for try await result in group {
    results.append(result)
    if let url = iterator.next() { group.addTask { try await fetch(url) } }
}
```

---

## Sendable

```swift
// Structs with Sendable properties are auto-Sendable
struct Product: Sendable { let id: Int; let name: String }

// Final class with no mutable state
final class ImmutableCache: Sendable { let items: [Product] }

// @Sendable closure
func process(completion: @Sendable () -> Void) { }
```

**SwiftData Sendable rules** — see `ios-swiftdata` Section 10.

---

## Swift 6.1 / 6.2 Isolation Model

```swift
@MainActor class ViewModel {
    func load() async { }             // main actor — always

    nonisolated func decode(_ d: Data) -> Product { ... }
    // Swift 6.1: runs on global executor (never main)
    // Swift 6.2 (Approachable Concurrency): inherits caller's isolation

    @concurrent func fetchRemote() async { }  // always global executor (6.2+)
}
```

| Declaration | Swift 6.1 | Swift 6.2 + Approachable Concurrency |
|---|---|---|
| `func` in `@MainActor` class | Main actor | Main actor |
| `nonisolated func` (async) | Global executor | Inherits caller |
| `@concurrent func` (async) | N/A | Always global executor |
| `@MainActor func` | Main actor always | Main actor always |
