# API Sync Patterns: Idempotent Offline-First Sync Engine

## Section 1: Architecture Overview

```
UI → ViewModel → Repository → Room (always — never direct API reads)
                     ↓
              PendingActionDao    (offline write queue)
              SyncCursorDao       (last-synced position per table)
              ConnectivityObserver (network state as Flow)
              SyncWorker           (WorkManager — push then pull on network)
```

**Core invariant:** Room is always the read source. Writes go to Room first, then queue for
server push. The UI never blocks on network state.

---

## Section 2: Core Sync Entities

### SyncCursorDao + SyncDao — atomic batch commit

```kotlin
@Entity(tableName = "sync_cursors")
data class SyncCursorEntity(
    @PrimaryKey val entityType: String,
    val lastSyncedAt: Long = 0L,
    val updatedAt: Long = System.currentTimeMillis()
)

@Dao
interface SyncCursorDao {
    @Query("SELECT * FROM sync_cursors WHERE entityType = :type")
    suspend fun getCursor(type: String): SyncCursorEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun setCursor(cursor: SyncCursorEntity)
}

// @Transaction ensures cursor and data write are atomic — no partial state on crash
@Dao
interface SyncDao {
    @Transaction
    suspend fun commitSyncBatch(entities: List<ProductEntity>, cursor: SyncCursorEntity) {
        upsertProducts(entities)
        setCursor(cursor)
    }

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertProducts(entities: List<ProductEntity>)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun setCursor(cursor: SyncCursorEntity)
}
```

### PendingActionEntity — all offline mutations queue here first

```kotlin
@Entity(tableName = "pending_actions")
data class PendingActionEntity(
    @PrimaryKey val idempotencyKey: String = UUID.randomUUID().toString(),
    val entityType: String,
    val actionType: String,       // "CREATE", "UPDATE", "DELETE"
    val entityId: String,
    val payload: String,          // JSON of the DTO
    val createdAt: Long = System.currentTimeMillis(),
    val retryCount: Int = 0,
    val lastError: String? = null
)

@Dao
interface PendingActionDao {
    // Dead-letter actions (retryCount >= 5) are never re-attempted. Surface to user or purge.
    @Query("SELECT * FROM pending_actions WHERE retryCount < 5 ORDER BY createdAt ASC")
    suspend fun getAll(): List<PendingActionEntity>

    @Query("SELECT * FROM pending_actions WHERE entityType = :type AND retryCount < 5 ORDER BY createdAt ASC")
    suspend fun getByType(type: String): List<PendingActionEntity>

    @Insert(onConflict = OnConflictStrategy.IGNORE)   // IGNORE = idempotent re-enqueue
    suspend fun enqueue(action: PendingActionEntity)

    @Delete
    suspend fun remove(action: PendingActionEntity)

    @Query("""
        UPDATE pending_actions
        SET retryCount = retryCount + 1, lastError = :error
        WHERE idempotencyKey = :key
    """)
    suspend fun recordFailure(key: String, error: String)

    @Query("SELECT COUNT(*) FROM pending_actions")
    fun observeCount(): Flow<Int>

    // Dead-letter: actions that exhausted all retries — surface to user or purge
    @Query("SELECT * FROM pending_actions WHERE retryCount >= 5")
    fun observeDeadLetters(): Flow<List<PendingActionEntity>>

    @Query("DELETE FROM pending_actions WHERE retryCount >= 5")
    suspend fun purgeDeadLetters()
}
```

---

## Section 3: Offline-Safe Repository Pattern

```kotlin
class ProductRepository @Inject constructor(
    private val productDao: ProductDao,
    private val pendingActionDao: PendingActionDao,
    private val syncCursorDao: SyncCursorDao,
    private val syncDao: SyncDao,
    private val apiService: ProductApiService,
    @ApplicationContext private val context: Context
) {
    // Reads ALWAYS from Room
    fun observeProducts(): Flow<List<Product>> =
        productDao.observeAll().map { it.map(ProductEntity::toDomain) }

    // Write to Room first + enqueue — instant UI, no network block
    suspend fun createProduct(product: Product): Result<Unit> = runCatching {
        val tempId = "local_${UUID.randomUUID()}"
        productDao.upsert(product.toEntity().copy(productId = tempId))
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

    fun triggerSync() { SyncWorker.triggerNow(context) }
}
```

---

## Section 4: syncFromServer() — Delta Sync, No Duplicates, No Missing Records

Key invariants:
- Cursor `updated_at > last_cursor` — never full delete+replace
- `do-while` loop paginates until `response.hasMore == false` — no missing records
- `upsertAll()` uses `OnConflictStrategy.REPLACE` — no duplicates
- Cursor advances ONLY after successful batch write — no gaps on partial failure
- `commitSyncBatch()` is `@Transaction` — cursor and data write are atomic

```kotlin
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
        if (response.data.isNotEmpty()) {
            val entities = response.data.map { it.toEntity() }
            // @Transaction ensures cursor and data write are atomic — no partial state on crash
            val pageMax = entities.maxOf { it.serverUpdatedAt }
            latestTimestamp = maxOf(latestTimestamp, pageMax)
            syncDao.commitSyncBatch(entities, SyncCursorEntity("products", latestTimestamp))
        }
        page++
    } while (response.hasMore)
}
```

---

## Section 5: syncToServer() — Push Pending Actions

Key invariants:
- Idempotency key sent as HTTP header — server deduplicates retries
- HTTP 409 → server wins, replace local with server version, remove action
- HTTP 404 → already gone server-side, remove action
- `IOException` → leave in queue, increment retry, throw (WorkManager retries)
- `tempId` replaced with real server ID on CREATE success — wrapped in `@Transaction`

```kotlin
suspend fun syncToServer(): Result<Unit> = runCatching {
    val actions = pendingActionDao.getByType("products")
    for (action in actions) {
        try {
            when (action.actionType) {
                "CREATE" -> {
                    val dto = Json.decodeFromString<CreateProductDto>(action.payload)
                    val response = apiService.createProduct(
                        dto,
                        idempotencyKey = action.idempotencyKey
                    )
                    // @Transaction prevents data loss if process is killed between delete and insert
                    productDao.replaceLocalWithServer(action.entityId, response.data.toEntity())
                }
                "UPDATE" -> {
                    val dto = Json.decodeFromString<UpdateProductDto>(action.payload)
                    val response = apiService.updateProduct(
                        action.entityId,
                        dto,
                        idempotencyKey = action.idempotencyKey
                    )
                    productDao.upsert(response.data.toEntity())
                }
                "DELETE" -> apiService.deleteProduct(action.entityId)
            }
            pendingActionDao.remove(action)
        } catch (e: HttpException) {
            when (e.code()) {
                409 -> {
                    val serverEntity = apiService.getProduct(action.entityId).data.toEntity()
                    productDao.upsert(serverEntity)
                    pendingActionDao.remove(action)
                }
                404 -> pendingActionDao.remove(action)
                else -> pendingActionDao.recordFailure(action.idempotencyKey, e.message())
            }
        } catch (e: IOException) {
            pendingActionDao.recordFailure(action.idempotencyKey, e.message ?: "network")
            throw e
        }
    }
}
```

### ProductDao — atomic tempId swap

```kotlin
// In ProductDao:
@Transaction
suspend fun replaceLocalWithServer(tempId: String, serverEntity: ProductEntity) {
    deleteById(tempId)
    upsert(serverEntity)
}
```

---

## Section 6: SyncWorker (WorkManager)

Push first (syncToServer), then pull (syncFromServer).

```kotlin
@HiltWorker
class SyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val productRepository: ProductRepository
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
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
            val request = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
                .setConstraints(constraints)
                .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
                .build()
            WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                WORK_NAME, ExistingPeriodicWorkPolicy.KEEP, request
            )
        }

        fun triggerNow(context: Context) {
            val request = OneTimeWorkRequestBuilder<SyncWorker>()
                .setConstraints(
                    Constraints.Builder()
                        .setRequiredNetworkType(NetworkType.CONNECTED)
                        .build()
                )
                .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
                .build()
            WorkManager.getInstance(context).enqueueUniqueWork(
                "${WORK_NAME}_now", ExistingWorkPolicy.REPLACE, request
            )
        }
    }
}
```

---

## Section 7: ConnectivityObserver — Auto-Trigger on Network Restore

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
                SyncWorker.triggerNow(context)    // Auto-sync on network restore
            }
            override fun onLost(network: Network) { trySend(false) }
        }
        val request = NetworkRequest.Builder()
            .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .addCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED)
            .build()
        manager.registerNetworkCallback(request, callback)
        // Check both INTERNET and VALIDATED — captive portals have INTERNET but not VALIDATED
        val caps = manager.activeNetwork?.let { manager.getNetworkCapabilities(it) }
        val isConnected = caps?.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET) == true
            && caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED)
        trySend(isConnected)
        awaitClose { manager.unregisterNetworkCallback(callback) }
    }.distinctUntilChanged()
}
```

---

## Section 8: ViewModel Integration

```kotlin
@HiltViewModel
class ProductListViewModel @Inject constructor(
    private val repository: ProductRepository,
    private val connectivity: ConnectivityObserver,
    private val pendingActionDao: PendingActionDao
) : ViewModel() {

    val products = repository.observeProducts()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    val isOnline = connectivity.isOnline
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), true)

    // "3 changes pending sync" badge
    val pendingCount = pendingActionDao.observeCount()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), 0)

    // Trigger via repository — keeps WorkManager out of ViewModel
    fun refresh() {
        viewModelScope.launch { repository.triggerSync() }
    }
}
```

---

## Section 9: Sync Guarantees Checklist

### No Duplicates

| Rule | Implementation |
|------|----------------|
| Stable String UUIDs as `@PrimaryKey` | Never `autoGenerate = true` for synced entities |
| All sync upserts use `REPLACE` | `OnConflictStrategy.REPLACE` in `upsertAll()` |
| Delta sync (cursor-based) | Never full delete + replace |
| Re-enqueue is idempotent | `PendingActions` uses `OnConflictStrategy.IGNORE` |

### No Missing Transactions

| Rule | Implementation |
|------|----------------|
| Full page drain | Paginate until `response.hasMore == false` |
| Atomic cursor advance | Cursor + batch in same `@Transaction` via `commitSyncBatch()` |
| Network errors stay queued | Actions removed only on server confirmation |
| Server deduplication | Must accept `Idempotency-Key` header on POST/PUT |

### Conflict Resolution

| Rule | Implementation |
|------|----------------|
| HTTP 409 → server wins | Fetch server version, discard local pending action |
| Optimistic locking | `version` column on entities |
| Retry cap | Max 5 WorkManager retries, then `Result.failure()` |
| Dead-letter queue | `retryCount >= 5` actions excluded from sync; surface or purge |

### Atomicity

| Rule | Implementation |
|------|----------------|
| Batch write + cursor | `commitSyncBatch()` — single `@Transaction` |
| tempId swap on CREATE | `replaceLocalWithServer()` — `@Transaction` in `ProductDao` |

---

## Section 10: Data Layer Mapping

```kotlin
// Three distinct layers — never mix them

// API DTOs
data class ProductDto(
    val id: String,
    val name: String,
    val price: BigDecimal,
    val categoryId: String,
    val updatedAt: Long,
    val version: Int = 1
)
data class CreateProductDto(val name: String, val price: BigDecimal, val categoryId: String)
data class UpdateProductDto(val name: String?, val price: BigDecimal?, val categoryId: String?)
// Note: nullable fields = PATCH semantics (only non-null fields are updated server-side).
// Server must ignore null values. Ensure your API uses PATCH not PUT for updates.
data class ApiResponse<T>(
    val success: Boolean,
    val data: T,
    val message: String?,
    val hasMore: Boolean = false
)

// Room entity
@Entity(tableName = "products")
data class ProductEntity(
    @PrimaryKey @ColumnInfo(name = "product_id") val productId: String,
    val name: String,
    val price: BigDecimal,
    @ColumnInfo(name = "category_id") val categoryId: String,
    @ColumnInfo(name = "is_active", defaultValue = "1") val isActive: Boolean = true,
    val version: Int = 1,
    @ColumnInfo(name = "server_updated_at") val serverUpdatedAt: Long = 0L,
    @ColumnInfo(name = "last_synced_at") val lastSyncedAt: Long = 0L
)

// Domain model
data class Product(val id: String, val name: String, val price: BigDecimal, val categoryId: String)

// Mappers
fun ProductDto.toEntity() =
    ProductEntity(id, name, price, categoryId, true, version, updatedAt, System.currentTimeMillis())
fun ProductEntity.toDomain() = Product(productId, name, price, categoryId)
fun Product.toCreateDto() = CreateProductDto(name, price, categoryId)
fun Product.toUpdateDto() = UpdateProductDto(name, price, categoryId)

// IMPORTANT: BigDecimal requires a TypeConverter in AppDatabase.
// See android-room skill Converters class:
// @TypeConverter fun fromBigDecimal(v: BigDecimal?): String? = v?.toPlainString()
// @TypeConverter fun toBigDecimal(v: String?): BigDecimal? = v?.let { BigDecimal(it) }
// Alternatively use Long (cents) for monetary amounts: price stored as 99900 = $999.00
```
