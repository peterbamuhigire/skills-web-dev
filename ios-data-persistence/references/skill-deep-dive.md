# ios-data-persistence Deep Dive

This file contains the extended guidance moved out of [../SKILL.md](../SKILL.md) so the skill entrypoint stays under the repository size limit.

## Included Sections

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

## 2. UserDefaults (Simple Preferences Only)

```swift
@AppStorage("selectedEnvironment") private var environment = "production"
@AppStorage("itemsPerPage") private var perPage = 30

// Programmatic access
UserDefaults.standard.set("value", forKey: "key")
let value = UserDefaults.standard.string(forKey: "key")

// App Groups (sharing with extensions/widgets)
let shared = UserDefaults(suiteName: "group.com.company.app")
shared?.set(true, forKey: "widgetEnabled")
```

**Rules:** NEVER store tokens, passwords, sensitive data, large objects, images, or unbounded arrays. Acceptable: booleans, small strings, integers, enums (via RawRepresentable).

---

## 3. Keychain Services (Security-Critical Data)

```swift
actor KeychainHelper {
    static let shared = KeychainHelper()

    func save(_ data: Data, for key: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data
        ]
        SecItemDelete(query as CFDictionary)
        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else { throw KeychainError.saveFailed(status) }
    }

    func read(for key: String) throws -> Data? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecMatchLimit as String: kSecMatchLimitOne,
            kSecReturnData as String: true
        ]
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        guard status == errSecSuccess else { return nil }
        return result as? Data
    }

    func delete(for key: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]
        SecItemDelete(query as CFDictionary)
    }
}

enum KeychainError: Error { case saveFailed(OSStatus), readFailed(OSStatus) }

actor TokenManager {
    private let keychain = KeychainHelper.shared

    var accessToken: String? {
        get async {
            guard let data = try? await keychain.read(for: "access_token") else { return nil }
            return String(data: data, encoding: .utf8)
        }
    }

    func saveTokens(access: String, refresh: String) async throws {
        try await keychain.save(Data(access.utf8), for: "access_token")
        try await keychain.save(Data(refresh.utf8), for: "refresh_token")
    }

    func clearTokens() async throws {
        try await keychain.delete(for: "access_token")
        try await keychain.delete(for: "refresh_token")
    }
}
```

---

## 4. SwiftData (Primary Local Storage — iOS 17+)

> **Deep Reference:** See the **`ios-swiftdata`** skill for full API coverage.

### 4.1 Model Definition

```swift
import SwiftData

@Model
class Product {
    #Unique([\.stockItemId])          // iOS 18+; for iOS 17 use @Attribute(.unique)
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

### 4.2 Container Setup

```swift
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup { ContentView() }
            .modelContainer(for: [Product.self, Order.self, Customer.self])
    }
}

// Custom configuration (migrations, in-memory for previews)
let schema = Schema([Product.self, Order.self])
let config = ModelConfiguration(isStoredInMemoryOnly: false)
let container = try ModelContainer(for: schema, configurations: [config])
```

### 4.3 Querying

```swift
struct ProductListView: View {
    @Query(sort: \Product.itemName) private var products: [Product]
    @Query(filter: #Predicate<Product> { $0.balance > 0 },
           sort: \Product.itemName) private var inStockProducts: [Product]
    @Environment(\.modelContext) private var context

    var body: some View { List(products) { ProductRow(product: $0) } }
}

// Programmatic fetch with FetchDescriptor
func searchProducts(query: String, in context: ModelContext) throws -> [Product] {
    let descriptor = FetchDescriptor<Product>(
        predicate: #Predicate { $0.itemName.localizedStandardContains(query) },
        sortBy: [SortDescriptor(\.itemName)])
    return try context.fetch(descriptor)
}

// Pagination
func fetchPage(offset: Int, limit: Int, in context: ModelContext) throws -> [Product] {
    var descriptor = FetchDescriptor<Product>(sortBy: [SortDescriptor(\.itemName)])
    descriptor.fetchOffset = offset
    descriptor.fetchLimit = limit
    return try context.fetch(descriptor)
}
```

### 4.4 CRUD Operations

```swift
context.insert(Product(stockItemId: 1, itemCode: "A001",
    itemName: "Widget", sellingPrice: 5000, balance: 100))  // Create
product.sellingPrice = 15000.0   // Update — auto-tracked
context.delete(product)          // Delete
try context.save()               // Explicit save (usually automatic)
```

### 4.5 Relationships

```swift
@Model
class Order {
    var invoiceNumber: String
    var customerName: String
    var createdAt: Date
    @Relationship(deleteRule: .cascade) var items: [OrderItem] = []
    init(invoiceNumber: String, customerName: String) {
        self.invoiceNumber = invoiceNumber; self.customerName = customerName; self.createdAt = Date()
    }
}

@Model
class OrderItem {
    var quantity: Double
    var unitPrice: Double
    var productName: String
    @Relationship(inverse: \Order.items) var order: Order?
    init(quantity: Double, unitPrice: Double, productName: String) {
        self.quantity = quantity; self.unitPrice = unitPrice; self.productName = productName
    }
}
```

Delete rules: `.cascade`, `.nullify`, `.deny`, `.noAction`.

### 4.6 Schema Migration

```swift
enum ProductSchemaV1: VersionedSchema {
    static var versionIdentifier = Schema.Version(1, 0, 0)
    static var models: [any PersistentModel.Type] { [Product.self] }
    @Model class Product { var stockItemId: Int; var itemName: String; var sellingPrice: Double }
}

enum ProductSchemaV2: VersionedSchema {
    static var versionIdentifier = Schema.Version(2, 0, 0)
    static var models: [any PersistentModel.Type] { [Product.self] }
    @Model class Product { var stockItemId: Int; var itemName: String; var sellingPrice: Double; var itemCode: String }
}

enum ProductMigrationPlan: SchemaMigrationPlan {
    static var schemas: [any VersionedSchema.Type] { [ProductSchemaV1.self, ProductSchemaV2.self] }
    static var stages: [MigrationStage] { [migrateV1toV2] }
    static let migrateV1toV2 = MigrationStage.lightweight(
        fromVersion: ProductSchemaV1.self, toVersion: ProductSchemaV2.self)
}
```

---

## 5. Repository Pattern (API-Backed Sync)

```swift
protocol ProductRepository {
    func getProducts(page: Int) async throws -> [Product]
    func getCachedProducts() async throws -> [Product]
    func syncProducts() async throws
}

final class ProductRepositoryImpl: ProductRepository {
    private let apiClient: APIClient
    private let modelContext: ModelContext

    init(apiClient: APIClient, modelContext: ModelContext) {
        self.apiClient = apiClient; self.modelContext = modelContext
    }

    /// Remote-first with local cache fallback
    func getProducts(page: Int) async throws -> [Product] {
        do {
            let response: PaginatedResponse<ProductDTO> =
                try await apiClient.get("products/list?page=\(page)")
            let models = response.items.map { $0.toSwiftDataModel() }
            for model in models { modelContext.insert(model) }
            try modelContext.save()
            return models
        } catch {
            return try await getCachedProducts()
        }
    }

    func getCachedProducts() async throws -> [Product] {
        try modelContext.fetch(FetchDescriptor<Product>(sortBy: [SortDescriptor(\.itemName)]))
    }

    func syncProducts() async throws {
        var page = 1; var hasMore = true
        while hasMore {
            let response: PaginatedResponse<ProductDTO> =
                try await apiClient.get("products/list?page=\(page)")
            for dto in response.items { upsert(dto) }
            try modelContext.save()
            hasMore = page < response.pagination.totalPages; page += 1
        }
    }

    private func upsert(_ dto: ProductDTO) {
        let descriptor = FetchDescriptor(predicate: #Predicate<Product> { $0.stockItemId == dto.stockItemId })
        if let existing = try? modelContext.fetch(descriptor).first {
            existing.itemName = dto.itemName; existing.sellingPrice = dto.sellingPrice
            existing.balance = dto.balance; existing.lastSynced = Date()
        } else { modelContext.insert(dto.toSwiftDataModel()) }
    }
}
```

---

## 6. Offline-First Architecture

### 6.1 Pending Operations Queue

```swift
@Model
class PendingOperation {
    var idempotencyKey: String
    var endpoint: String
    var httpMethod: String
    var payload: Data
    var createdAt: Date
    var retryCount: Int
    var lastError: String?

    init(endpoint: String, method: String, payload: Data) {
        self.idempotencyKey = UUID().uuidString; self.endpoint = endpoint
        self.httpMethod = method; self.payload = payload
        self.createdAt = Date(); self.retryCount = 0
    }
}
```

### 6.2 Sync Engine

```swift
final class SyncEngine {
    private let apiClient: APIClient
    private let modelContext: ModelContext

    func processPendingOperations() async {
        let descriptor = FetchDescriptor<PendingOperation>(
            predicate: #Predicate { $0.retryCount < 5 },
            sortBy: [SortDescriptor(\.createdAt)])
        guard let pending = try? modelContext.fetch(descriptor) else { return }
        for op in pending {
            do {
                try await apiClient.send(endpoint: op.endpoint, method: op.httpMethod,
                    body: op.payload, idempotencyKey: op.idempotencyKey)
                modelContext.delete(op)
            } catch { op.retryCount += 1; op.lastError = error.localizedDescription }
        }
        try? modelContext.save()
    }
}
```

### 6.3 Background Task Scheduling

```swift
import BackgroundTasks

func registerBackgroundSync() {
    BGTaskScheduler.shared.register(forTaskWithIdentifier: "com.app.sync", using: nil) { task in
        handleSync(task: task as! BGProcessingTask)
    }
}

func scheduleSync() {
    let request = BGProcessingTaskRequest(identifier: "com.app.sync")
    request.requiresNetworkConnectivity = true
    request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60)
    try? BGTaskScheduler.shared.submit(request)
}

func handleSync(task: BGProcessingTask) {
    Task { await SyncEngine(/* deps */).processPendingOperations(); task.setTaskCompleted(success: true) }
    task.expirationHandler = { task.setTaskCompleted(success: false) }
    scheduleSync()
}
```

### 6.4 Network Monitor

Use `NWPathMonitor` wrapped in an `@Observable` class. Update `isConnected` on `pathUpdateHandler` via `@MainActor`. Start on a background `DispatchQueue`. Cancel in `deinit`.

---

## 7. DTO / Domain Model Mapping

```swift
struct ProductDTO: Codable {
    let stockItemId: Int
    let itemCode: String
    let itemName: String
    let sellingPrice: Double
    let balance: Double

    enum CodingKeys: String, CodingKey {
        case stockItemId = "stock_item_id", itemCode = "item_code"
        case itemName = "item_name", sellingPrice = "selling_price", balance
    }

    func toSwiftDataModel() -> Product {
        Product(stockItemId: stockItemId, itemCode: itemCode,
                itemName: itemName, sellingPrice: sellingPrice, balance: balance)
    }
}

struct PaginatedResponse<T: Codable>: Codable {
    let items: [T]
    let pagination: PaginationInfo
}

struct PaginationInfo: Codable {
    let currentPage: Int, totalPages: Int, totalItems: Int
    enum CodingKeys: String, CodingKey {
        case currentPage = "current_page", totalPages = "total_pages", totalItems = "total_items"
    }
}
```

---

## 8. File Storage (Images, PDFs, Exports)

```swift
enum FileStorage {
    static var documentsDirectory: URL {
        FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
    }

    static func save(data: Data, filename: String, subdirectory: String? = nil) throws -> URL {
        var dir = documentsDirectory
        if let sub = subdirectory {
            dir = dir.appendingPathComponent(sub)
            try FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        }
        let url = dir.appendingPathComponent(filename)
        try data.write(to: url)
        return url
    }

    static func saveImage(_ image: UIImage, named filename: String) throws -> URL {
        guard let data = image.jpegData(compressionQuality: 0.8) else { throw StorageError.compressionFailed }
        return try save(data: data, filename: filename, subdirectory: "images")
    }

    static func delete(at url: URL) throws {
        guard FileManager.default.fileExists(atPath: url.path) else { return }
        try FileManager.default.removeItem(at: url)
    }
}
```

---

## 9. iCloud Sync Options

See [references/icloud-sync.md](references/icloud-sync.md) for full patterns. Quick decision:

| Need | Solution |
|---|---|
| Sync preferences across devices (< 1 MB) | `NSUbiquitousKeyValueStore` |
| User documents (iCloud Drive, conflict resolution) | `UIDocument` subclass |
| Shared structured/relational data between users | CloudKit (`CKRecord`, `CKDatabase`) |

Enable iCloud capabilities: Xcode → Signing & Capabilities → iCloud.

---

## 10. URLCache / NSCache (Temporary Caching)

Configure `URLCache.shared` at launch: `URLCache(memoryCapacity: 50_000_000, diskCapacity: 200_000_000)`. For in-memory object caching, wrap `NSCache` with typed accessors and set `countLimit` / `totalCostLimit`.

---

## 11. Cross-Skill References

| Skill | Relevance |
|---|---|
| `dual-auth-rbac` | Token storage lifecycle, refresh flow |
| `api-pagination` | Offset pagination with local caching |
| `vibe-security-skill` | TLS pinning, secure storage audits |

---

## 12. Anti-Patterns

| Anti-Pattern | Correct Approach |
|---|---|
| Storing tokens in UserDefaults | Keychain Services |
| Ignoring offline state in repository | Fallback to cache on network error |
| Heavy queries on MainActor | `ModelActor` for background work |
| Missing idempotency keys on retries | UUID per pending op |
