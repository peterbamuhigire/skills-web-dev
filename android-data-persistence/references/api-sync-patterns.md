# API Sync Patterns: Offline-First with Custom Backends

## Architecture Overview

Our apps use custom REST API backends (not Firebase). The data flow:

```
API Backend ←→ Repository ←→ Room (local cache) ←→ ViewModel ←→ UI
                    ↑
            Single source of truth
```

**Principle:** Room is the single source of truth. The UI always reads from Room. The Repository syncs Room with the API.

## Repository Pattern

### Standard Repository

```kotlin
class ProductRepository @Inject constructor(
    private val productDao: ProductDao,
    private val apiService: ProductApiService,
    private val settingsRepository: SettingsRepository
) {
    // UI always observes local data
    fun getProducts(): Flow<List<Product>> =
        productDao.getAllProducts().map { entities ->
            entities.map { it.toDomain() }
        }

    fun getProductById(id: String): Flow<Product?> =
        productDao.getProductById(id).map { it?.toDomain() }

    // Sync: API → Room
    suspend fun refreshProducts(): Result<Unit> {
        return try {
            val response = apiService.getProducts()
            val entities = response.data.map { it.toEntity() }
            productDao.deleteAll()
            productDao.insertAll(entities)
            settingsRepository.updateLastSync()
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // Create: API first, then cache locally
    suspend fun createProduct(product: Product): Result<Product> {
        return try {
            val dto = product.toCreateDto()
            val response = apiService.createProduct(dto)
            val entity = response.data.toEntity()
            productDao.insertAll(listOf(entity))
            Result.success(entity.toDomain())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // Update: API first, then update local cache
    suspend fun updateProduct(product: Product): Result<Product> {
        return try {
            val dto = product.toUpdateDto()
            val response = apiService.updateProduct(product.id, dto)
            val entity = response.data.toEntity()
            productDao.update(entity)
            Result.success(entity.toDomain())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // Delete: API first, then remove from cache
    suspend fun deleteProduct(id: String): Result<Unit> {
        return try {
            apiService.deleteProduct(id)
            productDao.deleteById(id)
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

## Sync Strategies

### Strategy 1: Cache-First (Read Heavy)

Best for data that changes infrequently (product catalogs, categories).

```kotlin
class CatalogRepository @Inject constructor(
    private val dao: CatalogDao,
    private val api: CatalogApiService
) {
    fun getCategories(): Flow<List<Category>> =
        dao.getAll().map { it.map { e -> e.toDomain() } }

    suspend fun sync(): Result<Unit> {
        return try {
            val remote = api.getCategories()
            dao.replaceAll(remote.data.map { it.toEntity() })
            Result.success(Unit)
        } catch (e: Exception) {
            // Return cached data silently on network error
            Result.failure(e)
        }
    }
}

@Dao
interface CatalogDao {
    @Query("SELECT * FROM categories ORDER BY name")
    fun getAll(): Flow<List<CategoryEntity>>

    @Transaction
    suspend fun replaceAll(categories: List<CategoryEntity>) {
        deleteAll()
        insertAll(categories)
    }

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(categories: List<CategoryEntity>)

    @Query("DELETE FROM categories")
    suspend fun deleteAll()
}
```

### Strategy 2: Network-First (Write Heavy)

Best for transactional data (orders, payments). Always try API first.

```kotlin
class OrderRepository @Inject constructor(
    private val dao: OrderDao,
    private val api: OrderApiService
) {
    suspend fun createOrder(order: CreateOrderDto): Result<Order> {
        return try {
            // API first - server is source of truth for orders
            val response = api.createOrder(order)
            val entity = response.data.toEntity()
            dao.insert(entity)
            Result.success(entity.toDomain())
        } catch (e: Exception) {
            Result.failure(e) // Don't cache failed orders
        }
    }

    fun getOrders(): Flow<List<Order>> =
        dao.getAllOrders().map { it.map { e -> e.toDomain() } }

    suspend fun refreshOrders(): Result<Unit> {
        return try {
            val response = api.getOrders()
            dao.replaceAll(response.data.map { it.toEntity() })
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### Strategy 3: Offline Queue (Offline-First Writes)

Best when users must be able to create data without connectivity.

```kotlin
// Pending action entity
@Entity(tableName = "pending_actions")
data class PendingActionEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val actionType: String,         // "CREATE_ORDER", "UPDATE_PRODUCT"
    val payload: String,            // JSON serialized data
    val createdAt: Long = System.currentTimeMillis(),
    val retryCount: Int = 0
)

@Dao
interface PendingActionDao {
    @Query("SELECT * FROM pending_actions ORDER BY createdAt ASC")
    suspend fun getPendingActions(): List<PendingActionEntity>

    @Insert
    suspend fun insert(action: PendingActionEntity)

    @Delete
    suspend fun delete(action: PendingActionEntity)

    @Query("UPDATE pending_actions SET retryCount = retryCount + 1 WHERE id = :id")
    suspend fun incrementRetry(id: Long)
}

// Sync worker
class SyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val pendingActionDao: PendingActionDao,
    private val apiService: ApiService,
    private val gson: Gson
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val actions = pendingActionDao.getPendingActions()

        for (action in actions) {
            if (action.retryCount >= 5) {
                pendingActionDao.delete(action) // Give up after 5 retries
                continue
            }
            try {
                processAction(action)
                pendingActionDao.delete(action) // Success
            } catch (e: Exception) {
                pendingActionDao.incrementRetry(action.id) // Retry later
            }
        }

        return Result.success()
    }

    private suspend fun processAction(action: PendingActionEntity) {
        when (action.actionType) {
            "CREATE_ORDER" -> {
                val dto = gson.fromJson(action.payload, CreateOrderDto::class.java)
                apiService.createOrder(dto)
            }
            // ... other action types
        }
    }
}

// Schedule sync with WorkManager
fun scheduleSyncWorker(context: Context) {
    val constraints = Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .build()

    val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
        .setConstraints(constraints)
        .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
        .build()

    WorkManager.getInstance(context)
        .enqueueUniquePeriodicWork("sync", ExistingPeriodicWorkPolicy.KEEP, syncRequest)
}
```

## ViewModel Patterns for Sync

### Pull-to-Refresh

```kotlin
@HiltViewModel
class ProductListViewModel @Inject constructor(
    private val repository: ProductRepository
) : ViewModel() {

    val products = repository.getProducts()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    private val _isRefreshing = MutableStateFlow(false)
    val isRefreshing = _isRefreshing.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error = _error.asStateFlow()

    init { refresh() }

    fun refresh() {
        viewModelScope.launch {
            _isRefreshing.value = true
            _error.value = null
            repository.refreshProducts()
                .onFailure { _error.value = it.message }
            _isRefreshing.value = false
        }
    }
}
```

### Create with Optimistic UI

```kotlin
suspend fun createProduct(product: Product): Result<Product> {
    // Optimistic: save locally first for instant UI feedback
    val tempEntity = product.toEntity().copy(productId = "temp_${System.currentTimeMillis()}")
    productDao.insertAll(listOf(tempEntity))

    return try {
        val response = apiService.createProduct(product.toCreateDto())
        val realEntity = response.data.toEntity()
        // Replace temp with real
        productDao.deleteById(tempEntity.productId)
        productDao.insertAll(listOf(realEntity))
        Result.success(realEntity.toDomain())
    } catch (e: Exception) {
        // Rollback optimistic insert
        productDao.deleteById(tempEntity.productId)
        Result.failure(e)
    }
}
```

## Data Layer Mapping (Complete)

```kotlin
// --- API Layer ---
data class ProductDto(
    val id: String,
    val name: String,
    val price: Double,
    val category_id: String,
    val is_active: Boolean
)

data class CreateProductDto(val name: String, val price: Double, val category_id: String)
data class UpdateProductDto(val name: String?, val price: Double?, val category_id: String?)

data class ApiResponse<T>(val success: Boolean, val data: T, val message: String?)

// --- Database Layer ---
@Entity(tableName = "products")
data class ProductEntity(
    @PrimaryKey @ColumnInfo(name = "product_id") val productId: String,
    val name: String,
    val price: Double,
    @ColumnInfo(name = "category_id") val categoryId: String,
    @ColumnInfo(name = "is_active") val isActive: Boolean,
    @ColumnInfo(name = "last_synced") val lastSynced: Long = System.currentTimeMillis()
)

// --- Domain Layer ---
data class Product(
    val id: String,
    val name: String,
    val price: Double,
    val categoryId: String,
    val isActive: Boolean
)

// --- Mappers ---
fun ProductDto.toEntity() = ProductEntity(id, name, price, category_id, is_active)
fun ProductEntity.toDomain() = Product(productId, name, price, categoryId, isActive)
fun Product.toCreateDto() = CreateProductDto(name, price, categoryId)
fun Product.toUpdateDto() = UpdateProductDto(name, price, categoryId)
```

## Network Connectivity Awareness

```kotlin
class ConnectivityObserver @Inject constructor(
    @ApplicationContext private val context: Context
) {
    val isOnline: Flow<Boolean> = callbackFlow {
        val manager = context.getSystemService(ConnectivityManager::class.java)
        val callback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) { trySend(true) }
            override fun onLost(network: Network) { trySend(false) }
        }
        val request = NetworkRequest.Builder()
            .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .build()
        manager.registerNetworkCallback(request, callback)
        // Initial state
        trySend(manager.activeNetwork != null)
        awaitClose { manager.unregisterNetworkCallback(callback) }
    }.distinctUntilChanged()
}
```

## Checklist: Data Layer Setup

- [ ] Room entities defined for all persistent data
- [ ] DAOs use `Flow` for reactive reads, `suspend` for writes
- [ ] Repository mediates between DAOs and API service
- [ ] Data mapping: DTO -> Entity -> Domain (three separate models)
- [ ] Migrations tested for every schema change
- [ ] DataStore used for preferences (not SharedPreferences)
- [ ] API errors handled gracefully (cached data shown on failure)
- [ ] Indexes on frequently queried columns
- [ ] Hilt modules provide Database, DAOs, and Repositories
- [ ] Offline queue for critical write operations (if needed)
