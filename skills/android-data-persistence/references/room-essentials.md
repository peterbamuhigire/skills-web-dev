# Room Essentials: Entities, DAOs, Database

## Gradle Dependencies

```kotlin
// build.gradle.kts (module)
dependencies {
    val roomVersion = "2.6.1"
    implementation("androidx.room:room-runtime:$roomVersion")
    implementation("androidx.room:room-ktx:$roomVersion")  // Coroutines + Flow
    kapt("androidx.room:room-compiler:$roomVersion")
    testImplementation("androidx.room:room-testing:$roomVersion")
}
```

## Entity Patterns

### Basic Entity

```kotlin
@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey
    @ColumnInfo(name = "user_id")
    val userId: String,

    @ColumnInfo(name = "full_name")
    val fullName: String,

    @ColumnInfo(name = "email")
    val email: String,

    @ColumnInfo(name = "is_active")
    val isActive: Boolean = true,

    @ColumnInfo(name = "created_at")
    val createdAt: Long = System.currentTimeMillis(),

    @ColumnInfo(name = "last_synced")
    val lastSynced: Long = System.currentTimeMillis()
)
```

### Entity with Indexes

```kotlin
@Entity(
    tableName = "orders",
    indices = [
        Index(value = ["customer_id"]),
        Index(value = ["order_date"]),
        Index(value = ["status", "order_date"])  // Composite index
    ]
)
data class OrderEntity(
    @PrimaryKey
    @ColumnInfo(name = "order_id")
    val orderId: String,

    @ColumnInfo(name = "customer_id")
    val customerId: String,

    @ColumnInfo(name = "total_amount")
    val totalAmount: Double,

    @ColumnInfo(name = "status")
    val status: String,

    @ColumnInfo(name = "order_date")
    val orderDate: Long
)
```

### Entity with Foreign Key

```kotlin
@Entity(
    tableName = "order_items",
    foreignKeys = [
        ForeignKey(
            entity = OrderEntity::class,
            parentColumns = ["order_id"],
            childColumns = ["order_id"],
            onDelete = ForeignKey.CASCADE
        ),
        ForeignKey(
            entity = ProductEntity::class,
            parentColumns = ["product_id"],
            childColumns = ["product_id"],
            onDelete = ForeignKey.RESTRICT
        )
    ],
    indices = [
        Index("order_id"),
        Index("product_id")
    ]
)
data class OrderItemEntity(
    @PrimaryKey(autoGenerate = true)
    @ColumnInfo(name = "item_id")
    val itemId: Long = 0,

    @ColumnInfo(name = "order_id")
    val orderId: String,

    @ColumnInfo(name = "product_id")
    val productId: String,

    @ColumnInfo(name = "quantity")
    val quantity: Int,

    @ColumnInfo(name = "unit_price")
    val unitPrice: Double
)
```

### Foreign Key Actions

| Action | Behavior |
|--------|----------|
| `CASCADE` | Delete/update children when parent changes |
| `RESTRICT` | Prevent parent deletion if children exist |
| `SET_NULL` | Set foreign key to null when parent deleted |
| `SET_DEFAULT` | Set foreign key to default when parent deleted |
| `NO_ACTION` | Do nothing (may cause constraint violation) |

### Ignored Fields

```kotlin
@Entity(tableName = "products")
data class ProductEntity(
    @PrimaryKey val productId: String,
    val name: String,
    val price: Double,

    @Ignore  // Not stored in database
    val isSelected: Boolean = false
)
```

## DAO Patterns

### Complete CRUD DAO

```kotlin
@Dao
interface UserDao {
    // --- CREATE ---
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(user: UserEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(users: List<UserEntity>)

    // --- READ (reactive) ---
    @Query("SELECT * FROM users WHERE is_active = 1 ORDER BY full_name ASC")
    fun getActiveUsers(): Flow<List<UserEntity>>

    @Query("SELECT * FROM users WHERE user_id = :userId")
    fun getUserById(userId: String): Flow<UserEntity?>

    @Query("SELECT * FROM users WHERE full_name LIKE '%' || :query || '%'")
    fun searchUsers(query: String): Flow<List<UserEntity>>

    // --- READ (one-shot) ---
    @Query("SELECT * FROM users WHERE user_id = :userId")
    suspend fun getUserByIdOnce(userId: String): UserEntity?

    @Query("SELECT COUNT(*) FROM users WHERE is_active = 1")
    suspend fun getActiveUserCount(): Int

    @Query("SELECT EXISTS(SELECT 1 FROM users WHERE email = :email)")
    suspend fun emailExists(email: String): Boolean

    // --- UPDATE ---
    @Update
    suspend fun update(user: UserEntity)

    @Query("UPDATE users SET is_active = :isActive WHERE user_id = :userId")
    suspend fun setActive(userId: String, isActive: Boolean)

    // --- DELETE ---
    @Delete
    suspend fun delete(user: UserEntity)

    @Query("DELETE FROM users WHERE user_id = :userId")
    suspend fun deleteById(userId: String)

    @Query("DELETE FROM users")
    suspend fun deleteAll()
}
```

### Conflict Strategies

| Strategy | Behavior |
|----------|----------|
| `REPLACE` | Delete old row, insert new (best for API sync) |
| `IGNORE` | Skip insert if conflict exists |
| `ABORT` | Abort the transaction (default) |

### Returning Values from Inserts

```kotlin
@Insert(onConflict = OnConflictStrategy.REPLACE)
suspend fun insert(user: UserEntity): Long  // Returns row ID

@Insert(onConflict = OnConflictStrategy.REPLACE)
suspend fun insertAll(users: List<UserEntity>): List<Long>  // Returns row IDs
```

### Transaction Methods

```kotlin
@Dao
interface OrderDao {
    @Transaction
    suspend fun createOrderWithItems(order: OrderEntity, items: List<OrderItemEntity>) {
        insertOrder(order)
        insertOrderItems(items)
    }

    @Insert
    suspend fun insertOrder(order: OrderEntity)

    @Insert
    suspend fun insertOrderItems(items: List<OrderItemEntity>)
}
```

## Database Setup

### Database Class

```kotlin
@Database(
    entities = [
        UserEntity::class,
        ProductEntity::class,
        OrderEntity::class,
        OrderItemEntity::class
    ],
    version = 1,
    exportSchema = true  // Required for migration testing
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun productDao(): ProductDao
    abstract fun orderDao(): OrderDao
}
```

### TypeConverters

```kotlin
class Converters {
    @TypeConverter
    fun fromTimestamp(value: Long?): Date? = value?.let { Date(it) }

    @TypeConverter
    fun dateToTimestamp(date: Date?): Long? = date?.time

    @TypeConverter
    fun fromStringList(value: String?): List<String> =
        value?.split(",")?.filter { it.isNotBlank() } ?: emptyList()

    @TypeConverter
    fun toStringList(list: List<String>): String = list.joinToString(",")

    @TypeConverter
    fun fromOrderStatus(status: OrderStatus): String = status.name

    @TypeConverter
    fun toOrderStatus(value: String): OrderStatus = OrderStatus.valueOf(value)
}

enum class OrderStatus { PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED }
```

### Hilt Database Module

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app_database"
        )
        .addMigrations(
            Migrations.MIGRATION_1_2,
            Migrations.MIGRATION_2_3
        )
        .build()
    }

    @Provides
    fun provideUserDao(db: AppDatabase): UserDao = db.userDao()

    @Provides
    fun provideProductDao(db: AppDatabase): ProductDao = db.productDao()

    @Provides
    fun provideOrderDao(db: AppDatabase): OrderDao = db.orderDao()
}
```

## Flow vs LiveData vs Suspend

| Return Type | Use Case | Threading |
|-------------|----------|-----------|
| `Flow<List<T>>` | Reactive UI updates (preferred) | Auto background |
| `LiveData<List<T>>` | Legacy reactive updates | Auto background |
| `suspend fun`: T | One-shot reads, writes | Caller's dispatcher |

**Rule:** Use `Flow` for reads that should update the UI reactively. Use `suspend` for writes and one-time reads.

## Naming Conventions

```
Entities:     UserEntity, ProductEntity, OrderEntity
DAOs:         UserDao, ProductDao, OrderDao
Database:     AppDatabase
TypeConverters: Converters
Migrations:   Migrations.MIGRATION_1_2
Tables:       users, products, orders (plural, snake_case)
Columns:      user_id, full_name, order_date (snake_case)
```
