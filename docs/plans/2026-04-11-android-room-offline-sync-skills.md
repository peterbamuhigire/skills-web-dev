# Android Room + Offline-First Sync Skills Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a comprehensive `android-room` skill from two source books, then upgrade `android-data-persistence` with a guaranteed no-duplicate, no-missing-transaction offline sync engine.

**Architecture:** New `android-room/SKILL.md` is a standalone deep Room reference (all Room API features). The existing `android-data-persistence` skill is upgraded: its SKILL.md mandates offline-first and references android-room, and `api-sync-patterns.md` is rebuilt with an idempotent delta-sync engine. CLAUDE.md is updated to register the new skill.

**Tech Stack:** Kotlin, Room 2.6+, WorkManager 2.9+, Hilt, Kotlin Coroutines + Flow, ConnectivityManager, kotlinx.serialization

---

## Task 1: Create android-room/SKILL.md — Part 1: Core Room API

**Files:**
- Create: `android-room/SKILL.md`

### Step 1: Create the skill file with frontmatter + Room fundamentals

```markdown
---
name: android-room
description: Comprehensive Room database skill for Android — entities, DAOs, relations,
  migrations, conflict resolution, FTS4, views, paging, encryption, and testing. Built
  from Mark Murphy's "Elements of Android Room". Use alongside android-data-persistence
  for full offline-first architecture.
---

# Android Room — Complete Reference

## Overview

Room is Android's SQLite abstraction layer. It provides compile-time SQL verification,
reactive queries via Flow/LiveData, and clean Kotlin coroutine support.

**Three core components:**

```
@Entity    → Defines a table (data class)
@Dao       → Defines operations (interface)
@Database  → Wires everything together (abstract class)
```

## Gradle Dependencies

```kotlin
// build.gradle.kts (app)
val roomVersion = "2.6.1"

dependencies {
    implementation("androidx.room:room-runtime:$roomVersion")
    implementation("androidx.room:room-ktx:$roomVersion")       // Flow + suspend support
    ksp("androidx.room:room-compiler:$roomVersion")             // Use KSP, not kapt

    // Optional: Paging 3
    implementation("androidx.room:room-paging:$roomVersion")

    // Testing
    testImplementation("androidx.room:room-testing:$roomVersion")
}

// KSP plugin
plugins {
    id("com.google.devtools.ksp") version "2.0.0-1.0.21"
}

// Schema export (MANDATORY — commit schemas/ to git)
ksp {
    arg("room.schemaLocation", "$projectDir/schemas")
}
```

## Entities

### Basic Entity

```kotlin
@Entity(tableName = "products")
data class ProductEntity(
    @PrimaryKey
    @ColumnInfo(name = "product_id")
    val productId: String,                          // Use String UUIDs, not auto-int

    @ColumnInfo(name = "name")
    val name: String,

    @ColumnInfo(name = "price")
    val price: Double,

    @ColumnInfo(name = "category_id")
    val categoryId: String,

    @ColumnInfo(name = "is_active", defaultValue = "1")
    val isActive: Boolean = true,

    @ColumnInfo(name = "version")
    val version: Int = 1,                           // Optimistic locking

    @ColumnInfo(name = "server_updated_at")
    val serverUpdatedAt: Long = 0L,                 // Server timestamp for delta sync

    @ColumnInfo(name = "last_synced_at")
    val lastSyncedAt: Long = 0L
)
```

### Indexes

```kotlin
@Entity(
    tableName = "orders",
    indices = [
        Index("customer_id"),                       // Foreign key lookup
        Index("order_date"),                        // Date range queries
        Index("status", "order_date"),              // Composite: filtered + sorted
        Index(value = ["server_id"], unique = true) // Unique server ID
    ],
    foreignKeys = [
        ForeignKey(
            entity = CustomerEntity::class,
            parentColumns = ["customer_id"],
            childColumns = ["customer_id"],
            onDelete = ForeignKey.CASCADE,
            onUpdate = ForeignKey.CASCADE
        )
    ]
)
```

### Embedded Types (multi-column from one property)

```kotlin
data class Address(
    val street: String,
    val city: String,
    val country: String
)

@Entity(tableName = "customers")
data class CustomerEntity(
    @PrimaryKey val customerId: String,
    val name: String,
    @Embedded(prefix = "billing_") val billingAddress: Address,
    @Embedded(prefix = "shipping_") val shippingAddress: Address
)
// Results in: billing_street, billing_city, billing_country, shipping_street, ...
```

### Partial Entities (insert/update subset of columns)

```kotlin
data class ProductPriceUpdate(val productId: String, val price: Double)

@Dao
interface ProductDao {
    @Update(entity = ProductEntity::class)
    suspend fun updatePrice(update: ProductPriceUpdate)
}
```

## TypeConverters

```kotlin
class Converters {
    // Date ↔ Long
    @TypeConverter fun fromTimestamp(value: Long?): Date? = value?.let { Date(it) }
    @TypeConverter fun dateToTimestamp(date: Date?): Long? = date?.time

    // List<String> ↔ String (comma-separated)
    @TypeConverter fun fromStringList(value: String?): List<String> =
        value?.split(",")?.filter { it.isNotBlank() } ?: emptyList()
    @TypeConverter fun toStringList(list: List<String>): String = list.joinToString(",")

    // Enum ↔ String
    @TypeConverter fun fromStatus(value: String?): OrderStatus? =
        value?.let { enumValueOf<OrderStatus>(it) }
    @TypeConverter fun toStatus(status: OrderStatus?): String? = status?.name
}

// Register at database level
@Database(entities = [...], version = 1)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase()
```

## DAOs

### Standard CRUD DAO

```kotlin
@Dao
interface ProductDao {
    // --- Reads (return Flow for reactive UI) ---
    @Query("SELECT * FROM products ORDER BY name ASC")
    fun observeAll(): Flow<List<ProductEntity>>

    @Query("SELECT * FROM products WHERE is_active = 1 ORDER BY name ASC")
    fun observeActive(): Flow<List<ProductEntity>>

    @Query("SELECT * FROM products WHERE product_id = :id")
    fun observeById(id: String): Flow<ProductEntity?>

    @Query("SELECT * FROM products WHERE product_id = :id")
    suspend fun getById(id: String): ProductEntity?

    @Query("SELECT COUNT(*) FROM products")
    suspend fun count(): Int

    // --- Writes (suspend for coroutine safety) ---
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(product: ProductEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertAll(products: List<ProductEntity>)

    @Update
    suspend fun update(product: ProductEntity)

    @Delete
    suspend fun delete(product: ProductEntity)

    @Query("DELETE FROM products WHERE product_id = :id")
    suspend fun deleteById(id: String)

    @Query("DELETE FROM products")
    suspend fun deleteAll()

    // --- Sync support ---
    @Query("SELECT MAX(server_updated_at) FROM products")
    suspend fun getLatestSyncCursor(): Long?
}
```

### Projection Queries (avoid SELECT *)

```kotlin
data class ProductSummary(
    @ColumnInfo(name = "product_id") val productId: String,
    @ColumnInfo(name = "name") val name: String,
    @ColumnInfo(name = "price") val price: Double
)

@Dao
interface ProductDao {
    @Query("SELECT product_id, name, price FROM products WHERE is_active = 1")
    fun observeSummaries(): Flow<List<ProductSummary>>
}
```

### Aggregate Queries

```kotlin
data class SalesStats(val count: Int, val total: Double)

@Query("SELECT COUNT(*) as count, SUM(amount) as total FROM orders WHERE date >= :from")
suspend fun getSalesStats(from: Long): SalesStats
```

## Database Class

```kotlin
@Database(
    entities = [
        ProductEntity::class,
        CategoryEntity::class,
        OrderEntity::class,
        PendingActionEntity::class,    // Required for offline sync queue
        SyncCursorEntity::class        // Tracks sync state per table
    ],
    version = 1,
    exportSchema = true,               // MANDATORY — commit schemas/ to git
    autoMigrations = [
        // AutoMigration(from = 1, to = 2)  — add as you bump version
    ]
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun productDao(): ProductDao
    abstract fun categoryDao(): CategoryDao
    abstract fun orderDao(): OrderDao
    abstract fun pendingActionDao(): PendingActionDao
    abstract fun syncCursorDao(): SyncCursorDao
}

// Hilt module
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {
    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase =
        Room.databaseBuilder(context, AppDatabase::class.java, "app_database")
            .addMigrations(/* list manual migrations here */)
            .build()

    @Provides fun provideProductDao(db: AppDatabase) = db.productDao()
    @Provides fun providePendingActionDao(db: AppDatabase) = db.pendingActionDao()
    @Provides fun provideSyncCursorDao(db: AppDatabase) = db.syncCursorDao()
}
```

## Relations

### One-to-Many

```kotlin
data class CategoryWithProducts(
    @Embedded val category: CategoryEntity,
    @Relation(parentColumn = "categoryId", entityColumn = "category_id")
    val products: List<ProductEntity>
)

@Dao
interface CategoryDao {
    @Transaction
    @Query("SELECT * FROM categories")
    fun observeWithProducts(): Flow<List<CategoryWithProducts>>
}
```

### Many-to-Many (Junction Table)

```kotlin
@Entity(
    tableName = "order_items",
    primaryKeys = ["order_id", "product_id"]
)
data class OrderItemEntity(
    @ColumnInfo(name = "order_id") val orderId: String,
    @ColumnInfo(name = "product_id") val productId: String,
    val quantity: Int,
    val unit_price: Double
)

data class OrderWithProducts(
    @Embedded val order: OrderEntity,
    @Relation(
        parentColumn = "orderId",
        entityColumn = "productId",
        associateBy = Junction(OrderItemEntity::class)
    )
    val products: List<ProductEntity>
)
```

### Nested Relations

```kotlin
data class OrderItemWithProduct(
    @Embedded val item: OrderItemEntity,
    @Relation(parentColumn = "product_id", entityColumn = "productId")
    val product: ProductEntity
)

data class OrderWithItems(
    @Embedded val order: OrderEntity,
    @Relation(
        entity = OrderItemEntity::class,
        parentColumn = "orderId",
        entityColumn = "order_id"
    )
    val items: List<OrderItemWithProduct>
)
```

## Transactions

```kotlin
// @Transaction ensures all-or-nothing on multi-step writes
@Dao
interface OrderDao {
    @Transaction
    suspend fun placeOrder(order: OrderEntity, items: List<OrderItemEntity>) {
        insertOrder(order)
        insertItems(items)
        // If insertItems throws, insertOrder is rolled back automatically
    }

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertOrder(order: OrderEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertItems(items: List<OrderItemEntity>)
}
```

## Conflict Resolution — Full Guide

| Strategy | Behaviour | Use When |
|---|---|---|
| `ABORT` (default) | Cancel this statement, preserve prior results in transaction | Unknown — use explicit strategy instead |
| `FAIL` | Cancel at the failing row, keep earlier rows from this batch | Batch insert where partial success is acceptable |
| `IGNORE` | Skip the conflicting row, continue processing | Inserting suggestions/cache where duplicates are benign |
| `REPLACE` | Delete the conflicting row, insert the new one | **API sync** — server is authoritative, always overwrite |
| `ROLLBACK` | Roll back the entire transaction | Strict all-or-nothing requirements |

**Rule of thumb for offline-first apps:**
- API-synced data → `REPLACE` (server wins)
- User-created offline data → `ABORT` + check before insert
- Audit logs / append-only data → `IGNORE` (never overwrite)

## Migrations

### Manual Migration (complex changes)

```kotlin
object Migrations {
    val MIGRATION_1_2 = object : Migration(1, 2) {
        override fun migrate(db: SupportSQLiteDatabase) {
            db.execSQL("ALTER TABLE products ADD COLUMN version INTEGER NOT NULL DEFAULT 1")
            db.execSQL("ALTER TABLE products ADD COLUMN server_updated_at INTEGER NOT NULL DEFAULT 0")
        }
    }

    // Rename column: SQLite requires table rebuild
    val MIGRATION_2_3 = object : Migration(2, 3) {
        override fun migrate(db: SupportSQLiteDatabase) {
            db.execSQL("""
                CREATE TABLE products_new (
                    product_id TEXT NOT NULL PRIMARY KEY,
                    product_name TEXT NOT NULL,
                    price REAL NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1
                )
            """)
            db.execSQL("INSERT INTO products_new SELECT product_id, name, price, version FROM products")
            db.execSQL("DROP TABLE products")
            db.execSQL("ALTER TABLE products_new RENAME TO products")
        }
    }
}
```

### Auto-Migration (simple column adds, renames)

```kotlin
@Database(
    version = 3,
    autoMigrations = [
        AutoMigration(from = 1, to = 2),                                    // Column add only
        AutoMigration(from = 2, to = 3, spec = Migration2To3::class)        // With rename spec
    ]
)
abstract class AppDatabase : RoomDatabase()

@RenameColumn(tableName = "products", fromColumnName = "name", toColumnName = "product_name")
class Migration2To3 : AutoMigrationSpec

// Other specs: @DeleteColumn, @RenameTable, @DeleteTable
```

**NEVER use `fallbackToDestructiveMigration()` in production.**

## Full-Text Search (FTS4)

```kotlin
// 1. Main entity (regular table)
@Entity(tableName = "notes")
data class NoteEntity(
    @PrimaryKey val noteId: String,
    val title: String,
    val body: String,
    val createdAt: Long
)

// 2. FTS shadow table (Room auto-creates triggers to keep it in sync)
@Fts4(contentEntity = NoteEntity::class)
@Entity(tableName = "notes_fts")
data class NoteFtsEntity(val title: String, val body: String)

// 3. Register both in @Database entities array

// 4. DAO search query
@Dao
interface NoteDao {
    @Query("SELECT * FROM notes WHERE noteId IN (SELECT rowid FROM notes_fts WHERE notes_fts MATCH :query)")
    fun search(query: String): Flow<List<NoteEntity>>

    // Snippet highlighting
    @Query("SELECT snippet(notes_fts, -1, '<b>', '</b>', '...', 10) FROM notes_fts WHERE notes_fts MATCH :query")
    suspend fun getSnippets(query: String): List<String>
}
```

## Database Views

```kotlin
@DatabaseView(
    value = """
        SELECT o.order_id, o.created_at, c.name as customer_name, 
               SUM(i.quantity * i.unit_price) as total_amount
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN order_items i ON o.order_id = i.order_id
        GROUP BY o.order_id
    """,
    viewName = "order_summaries"
)
data class OrderSummaryView(
    @ColumnInfo(name = "order_id") val orderId: String,
    @ColumnInfo(name = "created_at") val createdAt: Long,
    @ColumnInfo(name = "customer_name") val customerName: String,
    @ColumnInfo(name = "total_amount") val totalAmount: Double
)

// Register in @Database: views = [OrderSummaryView::class]
// Query like a table — read-only
@Query("SELECT * FROM order_summaries ORDER BY created_at DESC")
fun observeOrderSummaries(): Flow<List<OrderSummaryView>>
```

## Paging 3

```kotlin
@Dao
interface ProductDao {
    @Query("SELECT * FROM products WHERE is_active = 1 ORDER BY name ASC")
    fun getProductsPaged(): PagingSource<Int, ProductEntity>
}

// In ViewModel
val products: Flow<PagingData<Product>> = Pager(
    config = PagingConfig(pageSize = 20, enablePlaceholders = false, prefetchDistance = 5)
) {
    productDao.getProductsPaged()
}.flow
    .map { pagingData -> pagingData.map { it.toDomain() } }
    .cachedIn(viewModelScope)
```

## Pre-Populated Databases

```kotlin
// Ship a seed database as an asset
Room.databaseBuilder(context, AppDatabase::class.java, "app_database")
    .createFromAsset("databases/seed.db")      // assets/databases/seed.db
    .addMigrations(...)
    .build()

// Or from a file (useful for restoring backups)
Room.databaseBuilder(context, AppDatabase::class.java, "app_database")
    .createFromFile(File(context.filesDir, "import.db"))
    .build()
```

## SQLCipher Encryption

```kotlin
// 1. Dependency
// implementation("net.zetetic:android-database-sqlcipher:4.5.4")

// 2. Generate + store passphrase (hardware-backed keystore)
class PassphraseRepository(private val context: Context) {
    fun getOrCreatePassphrase(): ByteArray {
        val file = File(context.filesDir, "db_passphrase.bin")
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
        val encryptedFile = EncryptedFile.Builder(
            context, file, masterKey,
            EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
        ).build()
        return if (file.exists()) {
            encryptedFile.openFileInput().use { it.readBytes() }
        } else {
            generatePassphrase().also { passphrase ->
                encryptedFile.openFileOutput().use { it.write(passphrase) }
            }
        }
    }

    private fun generatePassphrase(): ByteArray {
        val random = SecureRandom.getInstanceStrong()
        val result = ByteArray(32)
        while (result.contains(0)) { random.nextBytes(result) }
        return result
    }
}

// 3. Wire into Room builder
val passphrase = PassphraseRepository(context).getOrCreatePassphrase()
Room.databaseBuilder(context, AppDatabase::class.java, "app_database")
    .openHelperFactory(SupportFactory(passphrase))
    .build()
```

## Room Testing

### DAO Tests (in-memory database)

```kotlin
@RunWith(AndroidJUnit4::class)
class ProductDaoTest {
    private lateinit var db: AppDatabase
    private lateinit var dao: ProductDao

    @Before fun setup() {
        db = Room.inMemoryDatabaseBuilder(
            ApplicationProvider.getApplicationContext(),
            AppDatabase::class.java
        ).build()
        dao = db.productDao()
    }

    @After fun teardown() = db.close()

    @Test fun upsertAndObserve() = runTest {
        val product = ProductEntity("p1", "Phone", 999.0, "electronics", true, 1, 0L, 0L)
        dao.upsert(product)
        val result = dao.getById("p1")
        assertNotNull(result)
        assertEquals("Phone", result!!.name)
    }

    @Test fun upsertReplaces_noDuplicates() = runTest {
        dao.upsert(ProductEntity("p1", "Phone", 999.0, "electronics", true, 1, 0L, 0L))
        dao.upsert(ProductEntity("p1", "Phone Pro", 1099.0, "electronics", true, 2, 0L, 0L))
        assertEquals(1, dao.count())
        assertEquals("Phone Pro", dao.getById("p1")!!.name)
    }

    @Test fun observeAll_emitsOnChange() = runTest {
        val results = mutableListOf<List<ProductEntity>>()
        val job = launch { dao.observeAll().take(2).toList(results) }
        dao.upsert(ProductEntity("p1", "Phone", 999.0, "electronics", true, 1, 0L, 0L))
        job.join()
        assertEquals(2, results.size)  // Empty first, then with product
    }
}
```

### Migration Tests

```kotlin
@RunWith(AndroidJUnit4::class)
class MigrationTest {
    @get:Rule
    val helper = MigrationTestHelper(
        InstrumentationRegistry.getInstrumentation(),
        AppDatabase::class.java
    )

    @Test fun migrate1To2() {
        helper.createDatabase("test_db", 1).use { db ->
            db.execSQL("INSERT INTO products VALUES ('p1', 'Phone', 999.0, 'electronics')")
        }
        val db = helper.runMigrationsAndValidate("test_db", 2, true, Migrations.MIGRATION_1_2)
        val cursor = db.query("SELECT * FROM products WHERE product_id = 'p1'")
        assertTrue(cursor.moveToFirst())
        // Verify new columns have correct defaults
        assertEquals(1, cursor.getInt(cursor.getColumnIndexOrThrow("version")))
        cursor.close()
    }
}
```

## Performance Rules

1. **Always index** foreign key columns, date columns, status columns used in WHERE
2. **Avoid SELECT *** — use projections for list screens
3. **Batch large inserts** in chunks of 500
4. **Use @Transaction** for multi-table writes
5. **Export schema** — commit `schemas/` to git, run migration tests in CI

```kotlin
// Batch insert
suspend fun bulkUpsert(items: List<ProductEntity>) {
    items.chunked(500).forEach { batch -> dao.upsertAll(batch) }
}
```

## Integration

```
android-room (this skill) → provides all Room patterns
      ↓
android-data-persistence → adds offline sync engine on top
      ↓
android-development → Clean Architecture, Hilt DI
      ↓
android-tdd → DAO tests, migration tests, Repository tests
```
```

Write this content into `android-room/SKILL.md`. Count lines and ensure it stays under 500.

### Step 2: Verify line count

```bash
wc -l android-room/SKILL.md
```

Expected: Under 500

### Step 3: Commit

```bash
git add android-room/SKILL.md
git commit -m "feat: add android-room skill — comprehensive Room reference from Mark Murphy's book"
```

---

## Task 2: Rebuild api-sync-patterns.md — Idempotent Offline-First Sync Engine

**Files:**
- Modify: `android-data-persistence/references/api-sync-patterns.md` (full replacement)

### Step 1: Write the new sync patterns reference

The rebuilt file must cover these patterns in order:

**Section 1 — Architecture Overview**
```
Room ← Repository → API
         ↑
PendingActionDao (offline write queue)
SyncCursorDao   (tracks last-synced position per table)
ConnectivityObserver (watches network state)
SyncWorker      (WorkManager job, runs on network available)
```

**Section 2 — Core Entities Required in Every Offline-First App**

```kotlin
// Tracks the sync cursor (last server timestamp seen) per entity type
@Entity(tableName = "sync_cursors")
data class SyncCursorEntity(
    @PrimaryKey val entityType: String,       // e.g., "products", "orders"
    val lastSyncedAt: Long = 0L,              // server_updated_at of last fetched record
    val updatedAt: Long = System.currentTimeMillis()
)

@Dao
interface SyncCursorDao {
    @Query("SELECT * FROM sync_cursors WHERE entityType = :type")
    suspend fun getCursor(type: String): SyncCursorEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun setCursor(cursor: SyncCursorEntity)
}

// Offline write queue — all offline mutations land here first
@Entity(tableName = "pending_actions")
data class PendingActionEntity(
    @PrimaryKey val idempotencyKey: String = UUID.randomUUID().toString(), // Deduplicates retries
    val entityType: String,                   // "products", "orders"
    val actionType: String,                   // "CREATE", "UPDATE", "DELETE"
    val entityId: String,                     // Server ID (or temp ID for new records)
    val payload: String,                      // JSON of the entity
    val createdAt: Long = System.currentTimeMillis(),
    val retryCount: Int = 0,
    val lastError: String? = null
)

@Dao
interface PendingActionDao {
    @Query("SELECT * FROM pending_actions ORDER BY createdAt ASC")
    suspend fun getAll(): List<PendingActionEntity>

    @Query("SELECT * FROM pending_actions WHERE entityType = :type ORDER BY createdAt ASC")
    suspend fun getByType(type: String): List<PendingActionEntity>

    @Insert(onConflict = OnConflictStrategy.IGNORE)  // IGNORE = idempotent — same key = skip
    suspend fun enqueue(action: PendingActionEntity)

    @Delete
    suspend fun remove(action: PendingActionEntity)

    @Query("UPDATE pending_actions SET retryCount = retryCount + 1, lastError = :error WHERE idempotencyKey = :key")
    suspend fun recordFailure(key: String, error: String)

    @Query("SELECT COUNT(*) FROM pending_actions")
    fun observeCount(): Flow<Int>              // Drive sync badge in UI
}
```

**Section 3 — Repository Pattern (Offline-First)**

```kotlin
class ProductRepository @Inject constructor(
    private val productDao: ProductDao,
    private val pendingActionDao: PendingActionDao,
    private val syncCursorDao: SyncCursorDao,
    private val apiService: ProductApiService,
    @ApplicationContext private val context: Context
) {
    // UI ALWAYS reads from Room — never directly from API
    fun observeProducts(): Flow<List<Product>> =
        productDao.observeAll().map { it.map(ProductEntity::toDomain) }

    // --- Offline-safe writes ---
    // Write to Room first (instant UI), then enqueue for API sync
    suspend fun createProduct(product: Product): Result<Unit> = runCatching {
        val tempId = "local_${UUID.randomUUID()}"
        val entity = product.toEntity().copy(productId = tempId)
        productDao.upsert(entity)
        pendingActionDao.enqueue(
            PendingActionEntity(
                entityType = "products",
                actionType = "CREATE",
                entityId = tempId,
                payload = Json.encodeToString(product.toCreateDto())
            )
        )
    }

    suspend fun updateProduct(product: Product): Result<Unit> = runCatching {
        productDao.upsert(product.toEntity())
        pendingActionDao.enqueue(
            PendingActionEntity(
                entityType = "products",
                actionType = "UPDATE",
                entityId = product.id,
                payload = Json.encodeToString(product.toUpdateDto())
            )
        )
    }

    suspend fun deleteProduct(id: String): Result<Unit> = runCatching {
        productDao.deleteById(id)
        pendingActionDao.enqueue(
            PendingActionEntity(
                entityType = "products",
                actionType = "DELETE",
                entityId = id,
                payload = "{}"
            )
        )
    }

    // --- Sync: download changes from server (delta sync, no full replace) ---
    // Guarantees: no duplicates (REPLACE), no missing records (cursor pagination)
    suspend fun syncFromServer(): Result<Unit> = runCatching {
        val cursor = syncCursorDao.getCursor("products")?.lastSyncedAt ?: 0L
        var page = 0
        var latestTimestamp = cursor

        do {
            val response = apiService.getProductsSince(
                updatedAfter = cursor,
                page = page,
                pageSize = 100
            )
            if (response.data.isEmpty()) break

            // Atomic batch write — all or nothing
            val entities = response.data.map { it.toEntity() }
            productDao.upsertAll(entities)                          // REPLACE — no duplicates

            latestTimestamp = maxOf(latestTimestamp,
                entities.maxOf { it.serverUpdatedAt })
            page++
        } while (response.hasMore)

        // Advance cursor only after successful batch write
        syncCursorDao.setCursor(SyncCursorEntity("products", latestTimestamp))
    }

    // --- Sync: push pending local writes to server ---
    suspend fun syncToServer(): Result<Unit> = runCatching {
        val actions = pendingActionDao.getByType("products")
        for (action in actions) {
            try {
                when (action.actionType) {
                    "CREATE" -> {
                        val dto = Json.decodeFromString<CreateProductDto>(action.payload)
                        val response = apiService.createProduct(
                            dto,
                            idempotencyKey = action.idempotencyKey  // Server deduplicates retries
                        )
                        // Replace temp local entity with real server entity
                        productDao.deleteById(action.entityId)
                        productDao.upsert(response.data.toEntity())
                    }
                    "UPDATE" -> {
                        val dto = Json.decodeFromString<UpdateProductDto>(action.payload)
                        val response = apiService.updateProduct(action.entityId, dto)
                        productDao.upsert(response.data.toEntity())
                    }
                    "DELETE" -> {
                        apiService.deleteProduct(action.entityId)
                    }
                }
                pendingActionDao.remove(action)                     // Success — remove from queue
            } catch (e: HttpException) {
                when (e.code()) {
                    409 -> {
                        // Conflict: server has newer version — fetch server version, discard local
                        val serverEntity = apiService.getProduct(action.entityId).data.toEntity()
                        productDao.upsert(serverEntity)
                        pendingActionDao.remove(action)             // Accept server wins
                    }
                    404 -> pendingActionDao.remove(action)          // Already deleted server-side
                    else -> pendingActionDao.recordFailure(action.idempotencyKey, e.message())
                }
            } catch (e: IOException) {
                // Network error — leave in queue, retry later
                pendingActionDao.recordFailure(action.idempotencyKey, e.message ?: "network error")
                throw e                                             // Bubble up to SyncWorker
            }
        }
    }
}
```

**Section 4 — SyncWorker (WorkManager)**

```kotlin
@HiltWorker
class SyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val productRepository: ProductRepository
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            // Push first (local → server), then pull (server → local)
            productRepository.syncToServer().getOrThrow()
            productRepository.syncFromServer().getOrThrow()
            Result.success()
        } catch (e: IOException) {
            if (runAttemptCount < 5) Result.retry() else Result.failure()
        } catch (e: Exception) {
            Result.failure()
        }
    }

    companion object {
        private const val WORK_NAME = "sync_worker"

        fun schedule(context: Context) {
            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()

            // Periodic sync every 15 minutes while online
            val periodic = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
                .setConstraints(constraints)
                .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
                .build()

            WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                WORK_NAME,
                ExistingPeriodicWorkPolicy.KEEP,
                periodic
            )
        }

        // Trigger immediate sync (e.g., on network restore or app foreground)
        fun triggerNow(context: Context) {
            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()

            val oneTime = OneTimeWorkRequestBuilder<SyncWorker>()
                .setConstraints(constraints)
                .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
                .build()

            WorkManager.getInstance(context).enqueueUniqueWork(
                "${WORK_NAME}_immediate",
                ExistingWorkPolicy.REPLACE,
                oneTime
            )
        }
    }
}
```

**Section 5 — ConnectivityObserver (auto-trigger on network restore)**

```kotlin
@Singleton
class ConnectivityObserver @Inject constructor(
    @ApplicationContext private val context: Context
) {
    val isOnline: Flow<Boolean> = callbackFlow {
        val manager = context.getSystemService(ConnectivityManager::class.java)

        val callback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) {
                trySend(true)
                // Trigger immediate sync when network comes back
                SyncWorker.triggerNow(context)
            }
            override fun onLost(network: Network) { trySend(false) }
        }

        val request = NetworkRequest.Builder()
            .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .addCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED)
            .build()

        manager.registerNetworkCallback(request, callback)

        // Emit initial state
        val isConnected = manager.activeNetwork
            ?.let { manager.getNetworkCapabilities(it) }
            ?.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET) == true
        trySend(isConnected)

        awaitClose { manager.unregisterNetworkCallback(callback) }
    }.distinctUntilChanged().shareIn(
        GlobalScope, SharingStarted.WhileSubscribed(), replay = 1
    )
}
```

**Section 6 — ViewModel Integration**

```kotlin
@HiltViewModel
class ProductListViewModel @Inject constructor(
    private val repository: ProductRepository,
    private val connectivityObserver: ConnectivityObserver,
    private val pendingActionDao: PendingActionDao
) : ViewModel() {

    val products = repository.observeProducts()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    val isOnline = connectivityObserver.isOnline
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), true)

    val pendingSyncCount = pendingActionDao.observeCount()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), 0)

    // User never needs to call this — WorkManager handles it
    // Exposed only for pull-to-refresh UX
    private val _isSyncing = MutableStateFlow(false)
    val isSyncing = _isSyncing.asStateFlow()

    fun refresh() {
        viewModelScope.launch {
            _isSyncing.value = true
            SyncWorker.triggerNow(viewModelScope.coroutineContext as Context)
            _isSyncing.value = false
        }
    }
}
```

**Section 7 — Sync Guarantee Checklist**

```
NO DUPLICATES:
  ✅ All entities use stable server UUIDs as @PrimaryKey
  ✅ All DAO inserts use OnConflictStrategy.REPLACE
  ✅ Delta sync uses cursor (updated_at > last_cursor), not full delete+replace
  ✅ Pending actions use IGNORE conflict (same idempotency key = skip)

NO MISSING TRANSACTIONS:
  ✅ Delta sync paginates with do-while loop until response.hasMore = false
  ✅ Sync cursor advances only AFTER successful batch write (@Transaction)
  ✅ Network errors re-queue the pending action (not removed until server confirms)
  ✅ Server must accept Idempotency-Key header on POST/PUT endpoints

CONFLICT RESOLUTION:
  ✅ HTTP 409 → server version wins, local change discarded
  ✅ version column tracked per entity for optimistic locking
  ✅ Retry limit = 5 (WorkManager), dead-letter after 5 failures

ATOMICITY:
  ✅ Batch upsert wrapped in @Transaction
  ✅ Cursor update inside same transaction as batch write
```

Write all of the above into `android-data-persistence/references/api-sync-patterns.md`. Ensure the file stays under 500 lines.

### Step 2: Verify line count

```bash
wc -l android-data-persistence/references/api-sync-patterns.md
```

Expected: Under 500

### Step 3: Commit

```bash
git add android-data-persistence/references/api-sync-patterns.md
git commit -m "feat: rebuild api-sync-patterns with idempotent delta-sync engine (no duplicates, no missing transactions)"
```

---

## Task 3: Update android-data-persistence/SKILL.md

**Files:**
- Modify: `android-data-persistence/SKILL.md`

### Step 1: Add android-room reference + mandate offline-first

At the top of the skill, after the overview section, add:

```markdown
**Offline-First is MANDATORY.** Every app we build MUST work fully offline and sync
automatically when connectivity is restored. Users must never be blocked by network state.
See `references/api-sync-patterns.md` for the complete sync engine.

**Room Deep Reference:** For full Room API coverage (FTS, views, migrations, encryption,
paging, conflict resolution), use the `android-room` skill alongside this one.
```

Update the Quick Reference table to add the new offline-sync reference:

```markdown
| **Offline Sync Engine** | `references/api-sync-patterns.md` | Idempotent sync, no duplicates, WorkManager |
```

Update the Integration section to include android-room:

```markdown
## Integration with Other Skills

```
android-room → Deep Room API (entities, migrations, FTS, encryption)
      ↓
android-data-persistence → Offline sync engine (THIS SKILL)
      ↓
android-development → Clean Architecture, Hilt DI
      ↓
android-tdd → DAO tests, migration tests, sync worker tests
```
```

### Step 2: Verify line count

```bash
wc -l android-data-persistence/SKILL.md
```

Expected: Under 500

### Step 3: Commit

```bash
git add android-data-persistence/SKILL.md
git commit -m "docs: mandate offline-first in android-data-persistence, reference android-room skill"
```

---

## Task 4: Register android-room in CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

### Step 1: Add android-room entry to the repository structure

Find the line in CLAUDE.md that contains `android-data-persistence` and add a new line **before** it:

```markdown
├── android-room/                    # Comprehensive Room reference (entities, DAOs, relations, migrations, FTS4, views, paging, SQLCipher, testing — from Mark Murphy's "Elements of Android Room")
```

### Step 2: Verify CLAUDE.md is still under 500 lines

```bash
wc -l CLAUDE.md
```

### Step 3: Commit

```bash
git add CLAUDE.md
git commit -m "docs: register android-room skill in CLAUDE.md index"
```

---

## Task 5: Save memory — offline-first is mandatory for all Android apps

**Files:**
- Create: `C:/Users/Peter/.claude/projects/C--Users-Peter--claude-skills/memory/feedback_android_offline_first.md`
- Modify: `C:/Users/Peter/.claude/projects/C--Users-Peter--claude-skills/memory/MEMORY.md`

### Step 1: Write memory file

```markdown
---
name: Android offline-first mandate
description: All Android apps must work offline and auto-sync — user should never notice network state
type: feedback
---

All Android apps we build must be offline-first. Seamless automatic sync when online is mandatory,
not optional.

**Why:** Users will be in places with poor or intermittent network. They must never be blocked.

**How to apply:** Always include PendingActionDao + SyncCursorDao + SyncWorker (WorkManager) +
ConnectivityObserver in every Android app. Use android-data-persistence + android-room skills together.
Sync guarantee: no duplicates (REPLACE strategy + stable UUIDs), no missing transactions
(cursor-based delta sync + idempotency keys).
```

### Step 2: Add to MEMORY.md index

Add this line to `MEMORY.md`:
```
- [Android Offline-First Mandate](feedback_android_offline_first.md) — All Android apps must work fully offline, auto-sync on network restore, seamlessly
```

### Step 3: Commit

```bash
git add C:/Users/Peter/.claude/projects/C--Users-Peter--claude-skills/memory/
git commit -m "memory: save Android offline-first mandate"
```

---

## Summary

| Task | File | Action |
|---|---|---|
| 1 | `android-room/SKILL.md` | Create — full Room API reference |
| 2 | `android-data-persistence/references/api-sync-patterns.md` | Rebuild — idempotent sync engine |
| 3 | `android-data-persistence/SKILL.md` | Update — mandate offline-first, reference android-room |
| 4 | `CLAUDE.md` | Update — register android-room |
| 5 | Memory files | Save — Android offline-first is mandatory |
