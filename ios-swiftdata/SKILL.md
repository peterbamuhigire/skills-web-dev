---
name: ios-swiftdata
description: Comprehensive SwiftData API reference (iOS 17+) — @Model, @Attribute, @Relationship,
  ModelContainer, ModelContext, FetchDescriptor, @Query, schema migrations, ModelActor for background
  work, CloudKit requirements, testing, and 10 anti-patterns. Use alongside ios-data-persistence
  for offline-first sync engine.
---

# iOS SwiftData

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

## 2. @Model Macro

```swift
import SwiftData

@Model
class Product {
    var stockItemId: Int
    var itemCode: String
    var itemName: String
    var sellingPrice: Double
    var balance: Double
    var lastSynced: Date

    init(stockItemId: Int, itemCode: String, itemName: String,
         sellingPrice: Double, balance: Double) {
        self.stockItemId = stockItemId
        self.itemCode = itemCode
        self.itemName = itemName
        self.sellingPrice = sellingPrice
        self.balance = balance
        self.lastSynced = Date()
    }
}
```

**Rules:**
- Must be `class` — NOT struct (same reason as `@Observable`)
- Auto-conforms to `Observable`, `Identifiable`, `PersistentModel`
- Always provide an explicit `init` even when all properties have defaults
- Simple types: `Bool`, `Data`, `Date`, `Decimal`, `Double`, `Float`, `Int`, `String`, `URL`, `UUID`
- Complex types: `Array`, `Enum` (must be `Codable`), `Struct` (must be `Codable`)

**Enum property:**
```swift
extension Order {
    enum Status: String, Codable, CaseIterable {
        case pending, confirmed, fulfilled, cancelled
    }
}
@Model class Order { var status: Status = .pending }
```

---

## 3. @Attribute Options

```swift
@Model class Item {
    @Attribute(.unique) var sku: String              // upsert on duplicate insert
    @Attribute(.externalStorage) var image: Data?    // large binary outside main store
    @Attribute(.allowsCloudEncryption) var secret: String
    @Attribute(originalName: "master") var main: String  // migration rename
    @Attribute(.ephemeral) var isSelected: Bool = false  // in-memory, observable
    @Transient var tapCount: Int = 0                     // in-memory, NOT observable
}
```

| | Persisted | Observable | Usable in `#Predicate` |
|---|---|---|---|
| Default property | ✅ | ✅ | ✅ |
| `@Attribute(.unique)` | ✅ upsert | ✅ | ✅ |
| `@Attribute(.ephemeral)` | ❌ | ✅ | ⚠️ broken |
| `@Transient` | ❌ | ❌ | ❌ crashes |
| `@Attribute(.externalStorage)` | ✅ external | ✅ | ✅ |

---

## 4. @Relationship

**1-to-many with cascade:**
```swift
@Model class Manufacturer {
    var name: String
    @Relationship(deleteRule: .cascade, inverse: \Vehicle.manufacturer)
    var vehicles: [Vehicle] = []
}
@Model class Vehicle {
    var make: String
    var manufacturer: Manufacturer?  // init omitted for brevity — see Section 2 rules
}
```

**1-to-1:**
```swift
@Model class Order {
    @Relationship(inverse: \Invoice.order)  // set inverse on ONE side only
    var invoice: Invoice?
}
@Model class Invoice { var total: Double; var order: Order?  /* init omitted — see Section 2 */ }
```

**Many-to-many:**
```swift
@Model class Student {
    @Relationship(inverse: \Course.students)
    var courses: [Course] = []
}
@Model class Course { var students: [Student] = []  /* init omitted — see Section 2 */ }
```

**Delete rules:**

| Rule | Behavior |
|---|---|
| `.nullify` (default) | Related objects survive, reference → nil |
| `.cascade` | Deletes all related objects |
| `.deny` | Throws if related objects exist — wrap `save()` in do/catch |
| `.noAction` | No automatic cleanup |

**Min/max counts:**
```swift
@Relationship(minimumModelCount: 1) var items: [Item] = []
@Relationship(maximumModelCount: 5) var tags: [Tag] = []
```

---

## 5. ModelContainer Setup

**Minimal:**
```swift
@main struct MyApp: App {
    var body: some Scene {
        WindowGroup { ContentView() }
            .modelContainer(for: [Product.self, Order.self])
    }
}
```

**Custom config (in-memory for tests/previews):**
```swift
let schema = Schema([Product.self, Order.self])
let config = ModelConfiguration(isStoredInMemoryOnly: true)
let container = try ModelContainer(for: schema, configurations: [config])
```

**With migration plan:**
```swift
@MainActor var container: ModelContainer {
    do { return try ModelContainer(for: Product.self,
                                   migrationPlan: ProductMigrationPlan.self) }
    catch { fatalError("ModelContainer init failed: \(error)") }
}
```

**With mock seed data:**
```swift
.modelContainer(for: Product.self, inMemory: true) { result in
    if case .success(let container) = result {
        container.mainContext.insert(Product(stockItemId: 1, itemCode: "A001",
            itemName: "Demo Widget", sellingPrice: 5000, balance: 100))
    }
}
```

---

## 6. ModelContext Full API

```swift
@Environment(\.modelContext) private var context

// INSERT
context.insert(Product(stockItemId: 1, itemCode: "A001",
    itemName: "Widget", sellingPrice: 5000, balance: 100))

// UPDATE — direct property assignment, auto-tracked
product.sellingPrice = 6000

// DELETE by object
context.delete(product)

// DELETE by predicate (bulk)
try context.delete(model: Product.self,
    where: #Predicate { $0.balance <= 0 })

// DELETE all
try context.delete(model: Product.self)

// FETCH (snapshot)
let products = try context.fetch(
    FetchDescriptor<Product>(sortBy: [SortDescriptor(\.itemName)]))

// FETCH COUNT
let count = try context.fetchCount(FetchDescriptor<Product>())

// SAVE manually (when autosave is off)
try context.save()

// ROLLBACK (autosave must be disabled)
context.rollback()

// ENUMERATE large datasets (avoids loading all into memory)
try context.enumerate(FetchDescriptor<Product>()) { product in
    product.sellingPrice *= 1.1
}
```

**Autosave:** ON by default. SwiftUI triggers save on lifecycle events and a timer.
Disable: `.modelContainer(for:, isAutosaveEnabled: false)`

---

## 7. FetchDescriptor

```swift
var descriptor = FetchDescriptor<Product>()
descriptor.predicate = #Predicate { $0.balance > 0 }
descriptor.sortBy = [SortDescriptor(\.itemName), SortDescriptor(\.sellingPrice, order: .reverse)]
descriptor.fetchLimit = 20
descriptor.fetchOffset = 40
descriptor.includePendingChanges = true           // default — includes unsaved inserts
descriptor.relationshipKeyPathsForPrefetching = [\.orderItems]

let results = try context.fetch(descriptor)
```

**Preview crash workaround** — always extract predicate to a variable:
```swift
// CRASHES Xcode Previews:
let count = try context.fetchCount(FetchDescriptor<Product>(
    predicate: #Predicate { $0.balance > 0 }))

// SAFE:
let pred = #Predicate<Product> { $0.balance > 0 }
let count = try context.fetchCount(FetchDescriptor(predicate: pred))
```

**Pagination:**
```swift
func fetchPage(_ page: Int, size: Int = 20) throws -> [Product] {
    var d = FetchDescriptor<Product>(sortBy: [SortDescriptor(\.itemName)])
    d.fetchLimit = size
    d.fetchOffset = page * size
    return try context.fetch(d)
}
```

---

## 8. @Query

```swift
struct ProductListView: View {
    @Query(sort: \Product.itemName) var products: [Product]
    @Query(filter: #Predicate<Product> { $0.balance > 0 },
           sort: \Product.itemName) var inStock: [Product]
    @Query(sort: \Product.itemName, animation: .smooth) var animated: [Product]
}
```

**Dynamic sort/filter via init injection:**
```swift
struct ProductListView: View {
    @Query var products: [Product]

    init(search: String, ascending: Bool) {
        let pred = search.isEmpty
            ? nil
            : #Predicate<Product> { $0.itemName.localizedStandardContains(search) }
        _products = Query(filter: pred,
                          sort: \Product.itemName,
                          order: ascending ? .forward : .reverse)
    }
}
```

**@Query vs context.fetch:**
- `@Query` — reactive, SwiftUI-only, re-renders on changes, MainActor-bound
- `context.fetch()` — snapshot, use in ViewModels/actors/non-SwiftUI code

**@Bindable for two-way binding:**
```swift
struct EditView: View {
    @Bindable var product: Product
    var body: some View { TextField("Name", text: $product.itemName) }
}
```

---

## 9. Schema Migration

**Step 1 — VersionedSchema per version (never remove old ones):**
```swift
enum ProductSchemaV1: VersionedSchema {
    static var versionIdentifier = Schema.Version(1, 0, 0)
    static var models: [any PersistentModel.Type] { [Product.self] }
    @Model class Product {
        var stockItemId: Int; var itemName: String; var sellingPrice: Double
        init(stockItemId: Int, itemName: String, sellingPrice: Double) {
            self.stockItemId = stockItemId; self.itemName = itemName
            self.sellingPrice = sellingPrice
        }
    }
}

enum ProductSchemaV2: VersionedSchema {
    static var versionIdentifier = Schema.Version(2, 0, 0)
    static var models: [any PersistentModel.Type] { [Product.self] }
    @Model class Product {
        var stockItemId: Int; var itemCode: String; var itemName: String
        var sellingPrice: Double; var balance: Double = 0.0
        init(stockItemId: Int, itemCode: String, itemName: String,
             sellingPrice: Double, balance: Double) {
            self.stockItemId = stockItemId; self.itemCode = itemCode
            self.itemName = itemName; self.sellingPrice = sellingPrice
            self.balance = balance
        }
    }
}

typealias Product = ProductSchemaV2.Product  // rest of app uses unqualified name
```

**Step 2 — Migration plan:**
```swift
enum ProductMigrationPlan: SchemaMigrationPlan {
    static var schemas: [any VersionedSchema.Type] {
        [ProductSchemaV1.self, ProductSchemaV2.self]
    }
    static let migrateV1toV2 = MigrationStage.lightweight(
        fromVersion: ProductSchemaV1.self, toVersion: ProductSchemaV2.self)
    static var stages: [MigrationStage] { [migrateV1toV2] }
}
```

**Lightweight migration supports:** adding properties with defaults, deleting properties,
renaming with `@Attribute(originalName:)`, adding `.externalStorage`, changing delete rules.

**Custom migration (data transformation):**
```swift
// Declare inside ProductMigrationPlan enum:
private static var mapping: [String: String] = [:]
static let migrateV2toV3 = MigrationStage.custom(
    fromVersion: ProductSchemaV2.self, toVersion: ProductSchemaV3.self
) { context in                    // willMigrate — old context
    let items = try? context.fetch(FetchDescriptor<ProductSchemaV2.Product>())
    mapping = items?.reduce(into: [:]) { $0[$1.stockItemId.description] = $1.itemName } ?? [:]
} didMigrate: { context in        // didMigrate — new context
    // create V3 models using mapping dict
}
```

---

## 10. ModelActor (Background Work)

**When to use:** Bulk operations causing UI hangs (>250ms noticeable per Apple).
**When NOT:** Single inserts from user taps — main context serial queue is sufficient.

```swift
@ModelActor
actor BackgroundStore {
    func insertBatch(_ dtos: [ProductDTO]) async {
        for dto in dtos { modelContext.insert(dto.toSwiftDataModel()) }
        try? modelContext.save()
    }

    func deleteByIds(_ ids: [PersistentIdentifier]) async {
        for id in ids {
            guard let product = self[id, as: Product.self] else { continue }
            modelContext.delete(product)
        }
        try? modelContext.save()
    }
}
```

**Usage:**
```swift
// Extract container BEFORE entering actor — ModelContainer is Sendable
let container = modelContext.container
Task.detached(priority: .userInitiated) {
    let store = BackgroundStore(modelContainer: container)
    await store.insertBatch(dtos)
}
```

**Sendable rules:**

| Can pass INTO actor | Can pass OUT of actor |
|---|---|
| ✅ `ModelContainer` | ✅ `PersistentIdentifier` |
| ✅ `PersistentIdentifier` / array | ✅ `[PersistentIdentifier]` |
| ❌ `ModelContext` | ❌ `@Model` instances |
| ❌ `@Model` instances | ❌ `ModelContext` |

`@ModelActor` is ~4× faster than off-actor async/await for bulk inserts.

---

## 11. Testing

```swift
// Reusable in-memory container
func makeTestContainer() throws -> ModelContainer {
    try ModelContainer(for: Product.self,
        configurations: ModelConfiguration(isStoredInMemoryOnly: true))
}

// Unit test
func testInsertAndFetch() throws {
    let container = try makeTestContainer()
    let context = ModelContext(container)
    context.insert(Product(stockItemId: 1, itemCode: "A001",
        itemName: "Widget", sellingPrice: 5000, balance: 10))
    try context.save()
    let results = try context.fetch(FetchDescriptor<Product>())
    XCTAssertEqual(results.count, 1)
    XCTAssertEqual(results[0].itemName, "Widget")
}

// Preview container (requires @MainActor for mainContext)
extension Product {
    @MainActor static var previewContainer: ModelContainer {
        let c = try! ModelContainer(for: Product.self,
            configurations: ModelConfiguration(isStoredInMemoryOnly: true))
        c.mainContext.insert(Product(stockItemId: 1, itemCode: "A001",
            itemName: "Widget", sellingPrice: 5000, balance: 100))
        return c
    }
}

#Preview { ProductListView().modelContainer(Product.previewContainer) }
```

---

## 12. CloudKit Requirements

```swift
// All properties must have defaults or be optional for CloudKit
@Model class Order {
    var invoiceNumber: String = ""
    var total: Double = 0.0
    var notes: String? = nil
    // ❌ @Attribute(.unique) — not supported with CloudKit
    // ❌ @Relationship(deleteRule: .deny) — not supported
    @Relationship(deleteRule: .cascade, inverse: \OrderItem.order)
    var items: [OrderItem]? = nil     // must be optional
}
```

**Setup:** Xcode → Signing & Capabilities → iCloud → CloudKit. Add Background Modes → Remote Notifications.

**Limitation:** Private CloudKit database only (one user's own devices). No shared/public as of iOS 18.

---

## 13. Anti-Patterns & Gotchas

| Anti-Pattern | Correct Approach |
|---|---|
| `@Model` on a struct | Must be `class` |
| No `init` on `@Model` | Always provide explicit `init` |
| `@Relationship` inverse set on both sides | Set inverse on ONE side only |
| `@Transient` in `#Predicate` | Use `@Attribute(.ephemeral)` (but predicate still broken) |
| `@Transient` without default value | Always provide default — crashes on access |
| Insert then delete without saving (autosave off) | `save()` after insert before delete |
| `.deny` delete rule without try/catch | Wrap `context.save()` in do/catch |
| Passing `@Model` instance across actor | Pass `PersistentIdentifier`, re-fetch inside |
| Passing `ModelContext` across actor | Not Sendable — use `@ModelActor` |
| Inline `#Predicate` inside `fetchCount()` call | Extract predicate to variable (Xcode crash) |
