# Room Advanced: Relations, Migrations, Testing, Performance

## Relations

### One-to-Many

```kotlin
// Parent entity
@Entity(tableName = "categories")
data class CategoryEntity(
    @PrimaryKey val categoryId: String,
    val name: String
)

// Child entity (has foreign key)
@Entity(
    tableName = "products",
    foreignKeys = [ForeignKey(
        entity = CategoryEntity::class,
        parentColumns = ["categoryId"],
        childColumns = ["category_id"],
        onDelete = ForeignKey.CASCADE
    )],
    indices = [Index("category_id")]
)
data class ProductEntity(
    @PrimaryKey val productId: String,
    @ColumnInfo(name = "category_id") val categoryId: String,
    val name: String,
    val price: Double
)

// Relation data class
data class CategoryWithProducts(
    @Embedded val category: CategoryEntity,
    @Relation(
        parentColumn = "categoryId",
        entityColumn = "category_id"
    )
    val products: List<ProductEntity>
)

// DAO query (must use @Transaction)
@Dao
interface CategoryDao {
    @Transaction
    @Query("SELECT * FROM categories")
    fun getCategoriesWithProducts(): Flow<List<CategoryWithProducts>>

    @Transaction
    @Query("SELECT * FROM categories WHERE categoryId = :id")
    suspend fun getCategoryWithProducts(id: String): CategoryWithProducts?
}
```

### One-to-One

```kotlin
data class UserWithProfile(
    @Embedded val user: UserEntity,
    @Relation(
        parentColumn = "userId",
        entityColumn = "user_id"
    )
    val profile: ProfileEntity?
)
```

### Many-to-Many (Junction Table)

```kotlin
// Junction/cross-reference table
@Entity(
    tableName = "order_products",
    primaryKeys = ["order_id", "product_id"],
    foreignKeys = [
        ForeignKey(entity = OrderEntity::class, parentColumns = ["orderId"], childColumns = ["order_id"]),
        ForeignKey(entity = ProductEntity::class, parentColumns = ["productId"], childColumns = ["product_id"])
    ]
)
data class OrderProductCrossRef(
    @ColumnInfo(name = "order_id") val orderId: String,
    @ColumnInfo(name = "product_id") val productId: String,
    val quantity: Int
)

// Relation
data class OrderWithProducts(
    @Embedded val order: OrderEntity,
    @Relation(
        parentColumn = "orderId",
        entityColumn = "productId",
        associateBy = Junction(OrderProductCrossRef::class)
    )
    val products: List<ProductEntity>
)
```

### Nested Relations

```kotlin
data class OrderWithItemsAndProducts(
    @Embedded val order: OrderEntity,
    @Relation(
        entity = OrderItemEntity::class,
        parentColumn = "orderId",
        entityColumn = "order_id"
    )
    val items: List<OrderItemWithProduct>
)

data class OrderItemWithProduct(
    @Embedded val orderItem: OrderItemEntity,
    @Relation(
        parentColumn = "product_id",
        entityColumn = "productId"
    )
    val product: ProductEntity
)
```

## Migrations

### Migration Strategy

1. **Change entity** (add/remove/modify columns)
2. **Increment database version**
3. **Write migration SQL**
4. **Register migration in builder**
5. **Test the migration**

### Common Migration Patterns

```kotlin
object Migrations {
    // Add a column
    val MIGRATION_1_2 = object : Migration(1, 2) {
        override fun migrate(db: SupportSQLiteDatabase) {
            db.execSQL(
                "ALTER TABLE products ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1"
            )
        }
    }

    // Add a new table
    val MIGRATION_2_3 = object : Migration(2, 3) {
        override fun migrate(db: SupportSQLiteDatabase) {
            db.execSQL("""
                CREATE TABLE IF NOT EXISTS categories (
                    categoryId TEXT NOT NULL PRIMARY KEY,
                    name TEXT NOT NULL
                )
            """)
            // Add foreign key column to existing table
            db.execSQL("""
                ALTER TABLE products ADD COLUMN category_id TEXT DEFAULT NULL
            """)
            db.execSQL("""
                CREATE INDEX IF NOT EXISTS index_products_category_id
                ON products(category_id)
            """)
        }
    }

    // Rename a column (SQLite doesn't support RENAME COLUMN before 3.25)
    val MIGRATION_3_4 = object : Migration(3, 4) {
        override fun migrate(db: SupportSQLiteDatabase) {
            // Create new table with correct schema
            db.execSQL("""
                CREATE TABLE products_new (
                    productId TEXT NOT NULL PRIMARY KEY,
                    product_name TEXT NOT NULL,
                    price REAL NOT NULL,
                    category_id TEXT
                )
            """)
            // Copy data
            db.execSQL("""
                INSERT INTO products_new (productId, product_name, price, category_id)
                SELECT productId, name, price, category_id FROM products
            """)
            // Drop old, rename new
            db.execSQL("DROP TABLE products")
            db.execSQL("ALTER TABLE products_new RENAME TO products")
        }
    }
}
```

### Auto-Migrations (Room 2.4+)

For simple changes, Room can generate migrations automatically:

```kotlin
@Database(
    entities = [UserEntity::class],
    version = 3,
    autoMigrations = [
        AutoMigration(from = 1, to = 2),
        AutoMigration(from = 2, to = 3, spec = Migration2To3::class)
    ]
)
abstract class AppDatabase : RoomDatabase()

// Spec for renames or deletes
@RenameColumn(tableName = "users", fromColumnName = "name", toColumnName = "full_name")
class Migration2To3 : AutoMigrationSpec
```

### Testing Migrations

```kotlin
@RunWith(AndroidJUnit4::class)
class MigrationTest {
    @get:Rule
    val helper = MigrationTestHelper(
        InstrumentationRegistry.getInstrumentation(),
        AppDatabase::class.java
    )

    @Test
    fun migrate1To2() {
        // Create database at version 1
        helper.createDatabase("test_db", 1).apply {
            execSQL("INSERT INTO products VALUES ('1', 'Phone', 999.99)")
            close()
        }

        // Run migration and validate
        val db = helper.runMigrationsAndValidate("test_db", 2, true, Migrations.MIGRATION_1_2)

        val cursor = db.query("SELECT * FROM products WHERE productId = '1'")
        assertTrue(cursor.moveToFirst())
        assertEquals(1, cursor.getInt(cursor.getColumnIndex("is_active")))
        cursor.close()
    }
}
```

## Testing Room

### In-Memory Database Tests

```kotlin
@RunWith(AndroidJUnit4::class)
class ProductDaoTest {
    private lateinit var database: AppDatabase
    private lateinit var dao: ProductDao

    @Before
    fun setup() {
        database = Room.inMemoryDatabaseBuilder(
            ApplicationProvider.getApplicationContext(),
            AppDatabase::class.java
        ).allowMainThreadQueries().build()
        dao = database.productDao()
    }

    @After
    fun teardown() { database.close() }

    @Test
    fun insertAndRetrieve() = runTest {
        val product = ProductEntity("1", "Phone", 999.99, "electronics", System.currentTimeMillis())
        dao.insertAll(listOf(product))

        val result = dao.getByIdOnce("1")
        assertNotNull(result)
        assertEquals("Phone", result?.name)
    }

    @Test
    fun getAllProducts_returnsFlowOfProducts() = runTest {
        dao.insertAll(listOf(
            ProductEntity("1", "Phone", 999.99, "electronics"),
            ProductEntity("2", "Laptop", 1499.99, "electronics")
        ))

        val products = dao.getAllProducts().first()
        assertEquals(2, products.size)
    }

    @Test
    fun deleteProduct_removesFromDatabase() = runTest {
        val product = ProductEntity("1", "Phone", 999.99, "electronics")
        dao.insertAll(listOf(product))
        dao.delete(product)

        val result = dao.getByIdOnce("1")
        assertNull(result)
    }

    @Test
    fun replaceOnConflict_updatesExisting() = runTest {
        dao.insertAll(listOf(ProductEntity("1", "Phone", 999.99, "electronics")))
        dao.insertAll(listOf(ProductEntity("1", "Phone Updated", 899.99, "electronics")))

        val result = dao.getByIdOnce("1")
        assertEquals("Phone Updated", result?.name)
        assertEquals(899.99, result?.price)
    }
}
```

## Performance Best Practices

### Indexing Strategy

```kotlin
// Index columns used in WHERE, JOIN, ORDER BY
@Entity(
    tableName = "orders",
    indices = [
        Index("customer_id"),           // Foreign key lookups
        Index("order_date"),            // Date range queries
        Index("status", "order_date"),  // Composite for filtered + sorted
        Index(value = ["email"], unique = true)  // Unique constraint
    ]
)
```

### Pagination with Paging 3

```kotlin
@Dao
interface ProductDao {
    @Query("SELECT * FROM products ORDER BY name ASC")
    fun getProductsPaginated(): PagingSource<Int, ProductEntity>
}

// In ViewModel
val products: Flow<PagingData<Product>> = Pager(
    config = PagingConfig(pageSize = 20, enablePlaceholders = false)
) {
    productDao.getProductsPaginated()
}.flow.map { pagingData ->
    pagingData.map { it.toDomain() }
}.cachedIn(viewModelScope)
```

### Batch Operations

```kotlin
// Insert in batches for large datasets
suspend fun insertProducts(products: List<ProductEntity>) {
    products.chunked(500).forEach { batch ->
        productDao.insertAll(batch)
    }
}
```

### Query Optimization

```kotlin
// BAD: Fetching all columns when you only need a few
@Query("SELECT * FROM products")

// GOOD: Projection for specific columns
@Query("SELECT product_id, name FROM products")
fun getProductNames(): Flow<List<ProductNameTuple>>

data class ProductNameTuple(
    @ColumnInfo(name = "product_id") val productId: String,
    @ColumnInfo(name = "name") val name: String
)
```

### Schema Export for CI

Enable schema export for migration verification:

```kotlin
// build.gradle.kts
kapt {
    arguments {
        arg("room.schemaLocation", "$projectDir/schemas")
    }
}
```

Add `schemas/` directory to version control for migration testing.
