# iCloud Sync Patterns

## iCloud Key-Value Store (Preferences, < 1 MB)

Sync small preference data across the user's devices. Enable: Xcode → Signing & Capabilities → iCloud → Key-value storage.

```swift
let kvStore = NSUbiquitousKeyValueStore.default

// Write
kvStore.set("compact", forKey: "preferredLayout")
kvStore.set(true, forKey: "notificationsEnabled")
kvStore.synchronize()  // hint to push — iOS decides actual timing

// Read
let layout = kvStore.string(forKey: "preferredLayout") ?? "standard"

// React to changes pushed from another device
NotificationCenter.default.addObserver(
    forName: NSUbiquitousKeyValueStore.didChangeExternallyNotification,
    object: kvStore, queue: .main
) { notification in
    let keys = notification.userInfo?[NSUbiquitousKeyValueStoreChangedKeysKey] as? [String]
    // Reload only changed keys — not the entire UI
    keys?.forEach { self.handleExternalChange(for: $0) }
}
```

**Limits:** 1 MB total, 1,024 keys. Not for user documents, images, or large data sets.

---

## UIDocument (User Documents, iCloud Drive)

Subclass `UIDocument` for automatic iCloud Drive sync, conflict resolution, undo manager, and autosave. Best for per-user document-centric apps.

```swift
class InvoiceDocument: UIDocument {
    var invoice: Invoice?

    // Serialise to Data when saving
    override func contents(forType typeName: String) throws -> Any {
        guard let invoice else { throw DocumentError.empty }
        return try JSONEncoder().encode(invoice)
    }

    // Deserialise on load
    override func load(fromContents contents: Any, ofType typeName: String?) throws {
        guard let data = contents as? Data else { throw DocumentError.invalid }
        invoice = try JSONDecoder().decode(Invoice.self, from: data)
    }
}

// Open a document from iCloud Drive
let containerURL = FileManager.default.url(forUbiquityContainerIdentifier: nil)!
let docURL = containerURL.appendingPathComponent("Documents/Invoice-001.json")
let doc = InvoiceDocument(fileURL: docURL)
await doc.open()
// doc.invoice is now populated; edits go through doc.undoManager

// Saving — UIDocument autosaves on resign active; force save if needed
try await doc.save(to: docURL, for: .forOverwriting)
```

**Key UIDocument benefits:**
- Automatic conflict resolution via `NSFileVersion`
- Undo/redo managed by `UIDocument.undoManager`
- `.autosavesDrafts` policy handles background saves
- Works with `UIDocumentBrowserViewController` for file pickers

---

## CloudKit (Shared / Collaborative Data)

Use for structured relational data shared between users (team workspaces, shared calendars, collaborative lists).

```swift
import CloudKit

let container = CKContainer.default()
let database  = container.privateCloudDatabase  // per-user; or .publicCloudDatabase (shared)

// Create a record
let record = CKRecord(recordType: "Invoice")
record["invoiceNumber"] = "INV-001"
record["amount"]        = 450000.0
record["status"]        = "pending"

// Attach a binary file (PDF, image)
let asset = CKAsset(fileURL: pdfURL)
record["attachment"] = asset

// Save
database.save(record) { saved, error in
    guard let saved, error == nil else { return }
    print("Saved: \(saved.recordID)")
}

// Query
let predicate = NSPredicate(format: "status == %@", "pending")
let query = CKQuery(recordType: "Invoice", predicate: predicate)
let (results, _) = try await database.records(matching: query)
```

**CloudKit record types:**
- `CKRecord` — dictionary-like row with typed fields
- `CKReference` — relationship between records (cascade delete optional)
- `CKAsset` — binary file stored as a URL reference (not in-record data)
- `CKSubscription` — push notification when records matching a predicate change

**When to use CloudKit vs SwiftData + CloudKit sync:**
- `NSPersistentCloudKitContainer` (Core Data) or SwiftData's built-in iCloud sync = private per-user data with automatic sync, zero CloudKit code
- Direct `CKDatabase` API = shared/public data, cross-user collaboration, server-side queries

---

## Choosing the Right iCloud Mechanism

| Scenario | Mechanism |
|---|---|
| App settings sync (theme, language) | `NSUbiquitousKeyValueStore` |
| Per-user document (invoice PDF, note) | `UIDocument` + iCloud Drive |
| Private structured data (orders, contacts) | SwiftData + iCloud (`NSPersistentCloudKitContainer`) |
| Multi-user shared workspace | CloudKit `CKDatabase` directly |
| Large file (video, backup) | `CKAsset` via CloudKit |
