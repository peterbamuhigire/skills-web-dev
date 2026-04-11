---
name: android-room
description: Comprehensive Room database skill for Android — entities, DAOs, relations,
  migrations, conflict resolution, FTS4, views, paging, SQLCipher, and testing. Built
  from Mark Murphy's "Elements of Android Room". Use alongside android-data-persistence
  for full offline-first architecture.
---

# Android Room Database

## 1. Overview

Three core components:

```
@Entity (data classes) → @Dao (SQL + suspend/Flow) → @Database (registry + builder)
        ↓                          ↑
   TypeConverters          @Transaction wrappers
```

Room generates SQLite boilerplate at compile time via KSP. All writes are `suspend`; reactive reads return `Flow`.

## 2. Gradle Dependencies

```kotlin
val roomVersion = "2.6.1"
implementation("androidx.room:room-runtime:$roomVersion")
implementation("androidx.room:room-ktx:$roomVersion")
ksp("androidx.room:room-compiler:$roomVersion")           // KSP, NOT kapt
implementation("androidx.room:room-paging:$roomVersion")  // optional, Paging 3
testImplementation("androidx.room:room-testing:$roomVersion")
testImplementation("app.cash.turbine:turbine:1.1.0")      // Flow testing
// Plugin: id("com.google.devtools.ksp") version "2.0.0-1.0.21"
// Schema: ksp { arg("room.schemaLocation", "$projectDir/schemas") }
```

## 3. Entities

```kotlin
@Entity(
    tableName = "products",
    indices = [
        Index("category_id"),
        Index("server_updated_at"),
        Index("is_active"),
        Index(value = ["product_id"], unique = true)
    ],
    foreignKeys = [ForeignKey(
        entity = CategoryEntity::class,
        parentColumns = ["category_id"],
        childColumns = ["category_id"],
        onDelete = ForeignKey.CASCADE
    )]
)
data class ProductEntity(
    @PrimaryKey val productId: String = UUID.randomUUID().toString(),
    val name: String,
    val price: BigDecimal,
    val categoryId: String,
    @ColumnInfo(name = "is_active", defaultValue = "1") val isActive: Boolean = true,
    val version: Int = 0,                                         // optimistic locking
    @ColumnInfo(name = "server_updated_at") val serverUpdatedAt: Long = 0L,  // delta sync cursor
    @ColumnInfo(name = "last_synced_at") val lastSyncedAt: Long = 0L
)
```

### @Embedded — multi-column address properties

```kotlin
data class Address(val street: String, val city: String, val country: String)

@Entity(tableName = "orders")
data class OrderEntity(
    @PrimaryKey val orderId: String = UUID.randomUUID().toString(),
    @Embedded(prefix = "billing_") val billingAddress: Address,
    @Embedded(prefix = "shipping_") val shippingAddress: Address
)
```

### Partial Entity Update

```kotlin
data class ProductStatusUpdate(val productId: String, val isActive: Boolean)

// In DAO:
@Update(entity = ProductEntity::class)
suspend fun updateStatus(update: ProductStatusUpdate)
```

## 4. TypeConverters

```kotlin
class Converters {
    @TypeConverter fun fromTimestamp(value: Long?): Date? = value?.let { Date(it) }
    @TypeConverter fun dateToTimestamp(date: Date?): Long? = date?.time

    // Use unit separator (\u001F) to avoid corruption if list values contain commas
    @TypeConverter fun fromStringList(value: List<String>): String = value.joinToString("\u001F")
    @TypeConverter fun toStringList(value: String?): List<String> =
        if (value.isNullOrBlank()) emptyList() else value.split("\u001F")

    @TypeConverter fun fromEnum(value: OrderStatus): String = value.name
    @TypeConverter fun toEnum(value: String): OrderStatus = OrderStatus.valueOf(value)

    @TypeConverter fun fromBigDecimal(value: BigDecimal?): String? = value?.toPlainString()
    @TypeConverter fun toBigDecimal(value: String?): BigDecimal? = value?.let { BigDecimal(it) }
}
// Register at @Database level: @TypeConverters(Converters::class)
```

## 5. DAOs

```kotlin
@Dao
interface ProductDao {
    // Reactive — Flow for UI observation
    @Query("SELECT product_id, name, price FROM products WHERE is_active = 1 ORDER BY name")
    fun observeAll(): Flow<List<ProductSummary>>

    @Query("SELECT * FROM products WHERE product_id = :id")
    fun observeById(id: String): Flow<ProductEntity?>

    // One-shot suspend
    @Query("SELECT * FROM products WHERE product_id = :id")
    suspend fun getById(id: String): ProductEntity?

    @Query("SELECT COUNT(*) FROM products WHERE is_active = 1")
    suspend fun count(): Int

    // Sync cursor
    @Query("SELECT MAX(server_updated_at) FROM products")
    suspend fun getLatestSyncCursor(): Long?

    @Query("SELECT category_id, COUNT(*) as total, SUM(price) as totalValue FROM products GROUP BY category_id")
    fun observeCategoryStats(): Flow<List<CategoryStats>>

    // Writes
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(entity: ProductEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertAll(entities: List<ProductEntity>)

    @Update
    suspend fun update(entity: ProductEntity)

    @Delete
    suspend fun delete(entity: ProductEntity)

    @Query("DELETE FROM products WHERE product_id = :id")
    suspend fun deleteById(id: String)

    @Query("DELETE FROM products")
    suspend fun deleteAll()
}

// Projection data classes (avoid SELECT *)
data class ProductSummary(val productId: String, val name: String, val price: BigDecimal)
data class CategoryStats(val categoryId: String, val total: Int, val totalValue: BigDecimal)
```

## 6. Database Class

```kotlin
@Database(
    entities = [
        ProductEntity::class, OrderEntity::class, CategoryEntity::class,
        PendingActionEntity::class, SyncCursorEntity::class
    ],
    version = 3,
    exportSchema = true,
    autoMigrations = [
        AutoMigration(from = 1, to = 2),
        AutoMigration(from = 2, to = 3, spec = Migration2To3::class)
    ]
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun productDao(): ProductDao
    abstract fun orderDao(): OrderDao
}
```

### Hilt Module

```kotlin
@Module @InstallIn(SingletonComponent::class)
object DatabaseModule {
    @Provides @Singleton
    fun provideDatabase(@ApplicationContext ctx: Context): AppDatabase =
        Room.databaseBuilder(ctx, AppDatabase::class.java, "app.db")
            .addMigrations(MIGRATION_1_2, MIGRATION_2_3)   // Register all manual migrations here
            .build()

    @Provides fun provideProductDao(db: AppDatabase): ProductDao = db.productDao()
    @Provides fun provideOrderDao(db: AppDatabase): OrderDao = db.orderDao()
    // DAOs are intentionally unscoped — they are lightweight wrappers around the
    // Singleton database. Hilt creates a new instance per injection point, which is fine.
}
```

## 7. Relations

### One-to-Many

```kotlin
data class CategoryWithProducts(
    @Embedded val category: CategoryEntity,
    @Relation(parentColumn = "category_id", entityColumn = "category_id")
    val products: List<ProductEntity>
)

@Dao interface CategoryDao {
    @Transaction
    @Query("SELECT * FROM categories")
    fun observeWithProducts(): Flow<List<CategoryWithProducts>>
}
```

### Many-to-Many (Junction Table)

```kotlin
@Entity(primaryKeys = ["order_id", "product_id"])
data class OrderProductCrossRef(val orderId: String, val productId: String)

data class OrderWithProducts(
    @Embedded val order: OrderEntity,
    @Relation(
        parentColumn = "order_id",
        entityColumn = "product_id",
        associateBy = Junction(OrderProductCrossRef::class)
    )
    val products: List<ProductEntity>
)
```

### Nested Relations

```kotlin
// @Relation only works with @Entity types. For nested relations, load separately and join in Repository.

// Step 1: Load order items
data class OrderWithItems(
    @Embedded val order: OrderEntity,
    @Relation(
        parentColumn = "orderId",
        entityColumn = "order_id"
    )
    val items: List<OrderItemEntity>    // @Relation works on @Entity types only
)

// Step 2: Manually join with products in Repository
// val products = productDao.getByIds(items.map { it.productId })
```

## 8. Transactions

```kotlin
@Dao interface OrderDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE) suspend fun insertOrder(order: OrderEntity)
    @Insert(onConflict = OnConflictStrategy.REPLACE) suspend fun insertItems(items: List<OrderItemEntity>)

    @Transaction
    suspend fun placeOrder(order: OrderEntity, items: List<OrderItemEntity>) {
        insertOrder(order)
        insertItems(items)
    }
}
```

## 9. Conflict Resolution

| Strategy   | Behaviour                              | When to Use                         |
|------------|----------------------------------------|-------------------------------------|
| `ABORT`    | Throws exception, rolls back statement | User-created data — check first     |
| `FAIL`     | Throws exception, keeps prior changes  | Partial batch inserts OK            |
| `IGNORE`   | Silently skips conflicting row         | Append-only logs, idempotent insert |
| `REPLACE`  | Deletes old row, inserts new           | API-synced data with server ID      |
| `ROLLBACK` | Throws exception, rolls back tx        | Strict atomic blocks                |

Rules:
- API-synced data → `REPLACE` (server is source of truth)
- User-created offline → `ABORT` + query first
- Append-only event/log tables → `IGNORE`

## 10. Migrations

### Manual Migration

```kotlin
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(db: SupportSQLiteDatabase) {
        db.execSQL("ALTER TABLE products ADD COLUMN barcode TEXT")
    }
}
// Rename column requires table rebuild:
// CREATE TABLE products_new (...), INSERT INTO ... SELECT ..., DROP TABLE products, ALTER TABLE products_new RENAME TO products
```

### AutoMigration

```kotlin
// Correct: @AutoMigration belongs in @Database autoMigrations array (see Section 6)
// The spec class only carries the operation annotation, not @AutoMigration
@DeleteTable.Entries(DeleteTable(tableName = "legacy_table"))
class Migration2To3 : AutoMigrationSpec
// Other spec annotations: @RenameColumn, @DeleteColumn, @RenameTable
```

**Never use `fallbackToDestructiveMigration()` in production** — silent data loss.

## 11. Full-Text Search (FTS4)

```kotlin
@Entity(tableName = "products") data class ProductEntity(...)

@Fts4(contentEntity = ProductEntity::class)
@Entity(tableName = "products_fts") data class ProductFtsEntity(val name: String, val description: String)

// Both entities in @Database entities array
@Dao interface SearchDao {
    @Query("SELECT * FROM products WHERE rowid IN (SELECT rowid FROM products_fts WHERE products_fts MATCH :query)")
    fun search(query: String): Flow<List<ProductEntity>>
    // IMPORTANT: Sanitize user input before passing to MATCH — raw strings with
    // quotes or operators (OR, AND, NOT) cause SQLiteException at runtime.
    // Sanitize in Repository: val safe = query.trim().replace(Regex("[^a-zA-Z0-9 ]"), "") + "*"

    @Query("SELECT snippet(products_fts) FROM products_fts WHERE products_fts MATCH :query")
    suspend fun getSnippets(query: String): List<String>
}
```

## 12. Database Views

```kotlin
@DatabaseView(
    viewName = "order_summaries",
    value = """
        SELECT o.order_id, o.created_at, COUNT(i.item_id) as item_count, SUM(i.price * i.qty) as total
        FROM orders o LEFT JOIN order_items i ON o.order_id = i.order_id
        GROUP BY o.order_id
    """
)
data class OrderSummaryView(val orderId: String, val createdAt: Long, val itemCount: Int, val total: BigDecimal)

// In @Database: views = [OrderSummaryView::class]
@Dao interface OrderSummaryDao {
    @Query("SELECT * FROM order_summaries ORDER BY created_at DESC")
    fun observeAll(): Flow<List<OrderSummaryView>>
}
```

## 13. Paging 3

```kotlin
@Dao interface ProductDao {
    @Query("SELECT * FROM products WHERE is_active = 1 ORDER BY name")
    fun pagingSource(): PagingSource<Int, ProductEntity>
}

// ViewModel
val products: Flow<PagingData<ProductDomain>> = Pager(
    config = PagingConfig(pageSize = 30, enablePlaceholders = false)
) { productDao.pagingSource() }
    .flow
    .map { pagingData -> pagingData.map { it.toDomain() } }
    .cachedIn(viewModelScope)
```

## 14. Pre-Populated Databases

```kotlin
Room.databaseBuilder(ctx, AppDatabase::class.java, "app.db")
    .createFromAsset("databases/seed.db")   // from assets/
    // OR:
    .createFromFile(File(ctx.filesDir, "seed.db"))
    .build()
```

## 15. SQLCipher Encryption

```kotlin
class PassphraseRepository(private val ctx: Context) {
    private val keyAlias = "room_passphrase_key"
    private val file = File(ctx.filesDir, "db.key")
    private val masterKey = MasterKey.Builder(ctx, keyAlias)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build()
    private val encryptedFile = EncryptedFile.Builder(
        ctx, file, masterKey, EncryptedFile.FileEncryptionScheme.AES256_GCM_HKDF_4KB
    ).build()

    fun getOrCreatePassphrase(): ByteArray {
        return try {
            if (file.exists()) {
                encryptedFile.openFileInput().use { it.readBytes() }
                    .takeIf { it.size == 32 } ?: generateAndSave()
            } else generateAndSave()
        } catch (e: Exception) {
            generateAndSave()   // Re-generate if file is corrupt or unreadable
        }
    }

    private fun generateAndSave(): ByteArray = generatePassphrase().also { passphrase ->
        encryptedFile.openFileOutput().use { it.write(passphrase) }
    }

    private fun generatePassphrase(): ByteArray {
        val bytes = ByteArray(32)
        SecureRandom().nextBytes(bytes)
        return bytes
        // Note: null-byte filtering is NOT needed for ByteArray passphrases in Kotlin/JVM.
        // SQLCipher accepts null bytes in ByteArray passphrases.
    }
}

// In builder:
val passphrase = passphraseRepo.getOrCreatePassphrase()
val factory = SupportFactory(passphrase)
Room.databaseBuilder(ctx, AppDatabase::class.java, "app.db")
    .openHelperFactory(factory).build()
```

## 16. Room Testing

```kotlin
@RunWith(AndroidJUnit4::class)
class ProductDaoTest {
    private lateinit var db: AppDatabase
    private lateinit var dao: ProductDao

    @Before fun setUp() {
        db = Room.inMemoryDatabaseBuilder(
            ApplicationProvider.getApplicationContext(), AppDatabase::class.java
        ).allowMainThreadQueries().build()
        dao = db.productDao()
    }
    @After fun tearDown() = db.close()

    @Test fun upsertAndObserve() = runTest {
        val product = ProductEntity(productId = "p1", name = "Widget", price = BigDecimal("9.99"), categoryId = "c1")
        dao.upsert(product)
        val result = dao.observeById("p1").first()
        assertThat(result?.name).isEqualTo("Widget")
    }

    @Test fun upsertReplaces_noDuplicates() = runTest {
        val product = ProductEntity(productId = "p1", name = "Widget", price = BigDecimal("9.99"), categoryId = "c1")
        dao.upsert(product)
        dao.upsert(product.copy(name = "Widget v2"))
        assertThat(dao.count()).isEqualTo(1)
    }

    @Test fun observeAll_emitsOnChange() = runTest {
        dao.observeAll().test {       // Requires app.cash.turbine:turbine dependency
            assertTrue(awaitItem().isEmpty())
            dao.upsert(ProductEntity("p1", "Phone", BigDecimal("999.00"), "elec", true, 1, 0L, 0L))
            assertEquals(1, awaitItem().size)
            cancel()
        }
    }
}

// Migration test
class MigrationTest {
    @get:Rule val helper = MigrationTestHelper(
        InstrumentationRegistry.getInstrumentation(),
        AppDatabase::class.java
    )
    @Test fun migrate1To2() {
        helper.createDatabase("test.db", 1).close()
        helper.runMigrationsAndValidate("test.db", 2, true, MIGRATION_1_2)
    }
}
```

## 17. Performance Rules

- **Index** foreign keys, date columns, status columns — always
- **Avoid SELECT \*** — use projection `data class` on list screens
- **Batch inserts** in chunks of 500: `entities.chunked(500).forEach { dao.upsertAll(it) }`
- **@Transaction** for all multi-table writes — prevents partial state
- **Export schema** (`exportSchema = true`) and commit `schemas/` directory to git
- **WAL mode** — add callback to `databaseBuilder`: `db.execSQL("PRAGMA journal_mode=WAL")` in `onCreate`

## 18. Integration

```
android-room          → all Room API patterns (this skill)
      ↓
android-data-persistence → offline sync engine on top
      ↓
android-development   → Clean Architecture, Hilt DI wiring
      ↓
android-tdd           → DAO, migration, Repository tests
```

Use `android-room` when you need deep Room API detail. Use `android-data-persistence` for the full sync + repository layer architecture.
