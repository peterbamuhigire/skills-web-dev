# Architecture & Code Patterns Reference

Production-ready Kotlin patterns for the SDS document. Use these as templates when generating architecture code examples.

[Back to SKILL.md](../SKILL.md)

---

## 1. MVVM + Clean Architecture Layers

```
┌─────────────────────────────────────────┐
│          Presentation Layer             │
│  Compose UI ← ViewModel ← UiState      │
├─────────────────────────────────────────┤
│            Domain Layer                 │
│  UseCases ← Repository Interfaces       │
├─────────────────────────────────────────┤
│             Data Layer                  │
│  Repository Impl → Remote + Local       │
│  Retrofit Services    Room DAOs         │
└─────────────────────────────────────────┘
```

## 2. Project Structure Template

```
com.company.app/
├── data/
│   ├── api/          # Retrofit service interfaces
│   ├── db/           # Room database, entities, DAOs
│   ├── dto/          # Network DTOs (request/response)
│   ├── mapper/       # DTO ↔ Entity ↔ Domain mappers
│   └── repository/   # Repository implementations
├── domain/
│   ├── model/        # Domain models (pure Kotlin)
│   ├── repository/   # Repository interfaces
│   └── usecase/      # Business logic use cases
├── presentation/
│   ├── auth/         # Login, register, biometric
│   ├── dashboard/    # Home screen, KPIs
│   ├── [module]/     # Feature-specific screens
│   ├── components/   # Shared UI components
│   ├── navigation/   # NavGraph, routes
│   └── theme/        # Colors, typography, shapes
├── di/               # Hilt modules
├── sync/             # SyncWorker, SyncManager
└── util/             # Extensions, helpers, constants
```

## 3. Hilt Network Module

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(
        authInterceptor: AuthInterceptor,
        tenantInterceptor: TenantInterceptor
    ): OkHttpClient = OkHttpClient.Builder()
        .addInterceptor(authInterceptor)
        .addInterceptor(tenantInterceptor)
        .addInterceptor(HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BODY
                    else HttpLoggingInterceptor.Level.NONE
        })
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .authenticator(TokenRefreshAuthenticator(/* deps */))
        .build()

    @Provides
    @Singleton
    fun provideRetrofit(client: OkHttpClient): Retrofit = Retrofit.Builder()
        .baseUrl(BuildConfig.BASE_URL)
        .client(client)
        .addConverterFactory(MoshiConverterFactory.create())
        .build()

    @Provides @Singleton
    fun provideAuthService(retrofit: Retrofit): AuthService =
        retrofit.create(AuthService::class.java)

    // One @Provides per Retrofit service interface
}
```

## 4. Auth Interceptor

```kotlin
class AuthInterceptor @Inject constructor(
    private val tokenManager: TokenManager
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        val token = tokenManager.getAccessToken()
        return if (token != null) {
            chain.proceed(
                request.newBuilder()
                    .header("Authorization", "Bearer $token")
                    .build()
            )
        } else {
            chain.proceed(request)
        }
    }
}
```

## 5. Token Refresh Authenticator (Thread-Safe)

```kotlin
class TokenRefreshAuthenticator @Inject constructor(
    private val tokenManager: TokenManager,
    private val authService: Lazy<AuthService>
) : Authenticator {
    private val mutex = Mutex()

    override fun authenticate(route: Route?, response: Response): Request? {
        return runBlocking {
            mutex.withLock {
                // Check if another thread already refreshed
                val currentToken = tokenManager.getAccessToken()
                val requestToken = response.request.header("Authorization")
                    ?.removePrefix("Bearer ")

                if (currentToken != requestToken && currentToken != null) {
                    // Already refreshed by another thread
                    return@runBlocking response.request.newBuilder()
                        .header("Authorization", "Bearer $currentToken")
                        .build()
                }

                // Attempt refresh
                val refreshToken = tokenManager.getRefreshToken() ?: return@runBlocking null
                try {
                    val refreshResponse = authService.get()
                        .refreshToken(RefreshRequest(refreshToken))
                    if (refreshResponse.isSuccessful && refreshResponse.body() != null) {
                        val newTokens = refreshResponse.body()!!.data
                        tokenManager.saveTokens(newTokens.accessToken, newTokens.refreshToken)
                        response.request.newBuilder()
                            .header("Authorization", "Bearer ${newTokens.accessToken}")
                            .build()
                    } else {
                        tokenManager.clearTokens()
                        null // Force re-login
                    }
                } catch (e: Exception) {
                    null
                }
            }
        }
    }
}
```

## 6. Repository Pattern with Offline Fallback

```kotlin
class ProductRepository @Inject constructor(
    private val api: ProductService,
    private val dao: ProductDao,
    private val networkMonitor: NetworkMonitor
) {
    fun getProducts(query: String?): Flow<Resource<List<Product>>> = flow {
        emit(Resource.Loading())

        // Always emit cached data first
        val cached = dao.searchProducts(query ?: "")
        if (cached.isNotEmpty()) {
            emit(Resource.Success(cached.map { it.toDomain() }))
        }

        // Fetch fresh data if online
        if (networkMonitor.isOnline()) {
            try {
                val response = api.getProducts(query = query)
                if (response.success) {
                    dao.upsertAll(response.data.map { it.toEntity() })
                    val fresh = dao.searchProducts(query ?: "")
                    emit(Resource.Success(fresh.map { it.toDomain() }))
                }
            } catch (e: Exception) {
                if (cached.isEmpty()) emit(Resource.Error(e.message ?: "Network error"))
            }
        } else if (cached.isEmpty()) {
            emit(Resource.Error("No internet and no cached data"))
        }
    }
}
```

## 7. ViewModel Pattern

```kotlin
@HiltViewModel
class ProductListViewModel @Inject constructor(
    private val getProductsUseCase: GetProductsUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(ProductListUiState())
    val uiState: StateFlow<ProductListUiState> = _uiState.asStateFlow()

    init { loadProducts() }

    fun loadProducts(query: String? = null) {
        viewModelScope.launch {
            getProductsUseCase(query).collect { result ->
                _uiState.update { state ->
                    when (result) {
                        is Resource.Loading -> state.copy(isLoading = true)
                        is Resource.Success -> state.copy(
                            isLoading = false,
                            products = result.data ?: emptyList(),
                            error = null
                        )
                        is Resource.Error -> state.copy(
                            isLoading = false,
                            error = result.message
                        )
                    }
                }
            }
        }
    }
}

data class ProductListUiState(
    val isLoading: Boolean = false,
    val products: List<Product> = emptyList(),
    val error: String? = null
)
```

## 8. Compose Screen Pattern

```kotlin
@Composable
fun ProductListScreen(
    viewModel: ProductListViewModel = hiltViewModel(),
    onProductClick: (String) -> Unit
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Scaffold(
        topBar = { /* TopAppBar */ }
    ) { padding ->
        when {
            uiState.isLoading && uiState.products.isEmpty() -> LoadingState(Modifier.padding(padding))
            uiState.error != null && uiState.products.isEmpty() -> ErrorState(
                modifier = Modifier.padding(padding),
                message = uiState.error!!,
                onRetry = { viewModel.loadProducts() }
            )
            else -> ProductList(
                modifier = Modifier.padding(padding),
                products = uiState.products,
                onProductClick = onProductClick
            )
        }
    }
}
```

## 9. Room Entity + DAO Pattern

```kotlin
@Entity(
    tableName = "products",
    indices = [
        Index(value = ["tenant_id"]),
        Index(value = ["name"]),
        Index(value = ["barcode"], unique = true)
    ]
)
data class ProductEntity(
    @PrimaryKey val id: String,
    @ColumnInfo(name = "tenant_id") val tenantId: String,
    val name: String,
    val barcode: String?,
    val price: Double,
    @ColumnInfo(name = "stock_quantity") val stockQuantity: Int,
    @ColumnInfo(name = "sync_status") val syncStatus: Int = 0, // 0=synced, 1=pending
    @ColumnInfo(name = "updated_at") val updatedAt: Long = System.currentTimeMillis()
)

@Dao
interface ProductDao {
    @Query("SELECT * FROM products WHERE name LIKE '%' || :query || '%' ORDER BY name")
    suspend fun searchProducts(query: String): List<ProductEntity>

    @Upsert
    suspend fun upsertAll(products: List<ProductEntity>)

    @Query("SELECT * FROM products WHERE sync_status = 1")
    suspend fun getPendingSync(): List<ProductEntity>

    @Query("UPDATE products SET sync_status = 0 WHERE id = :id")
    suspend fun markSynced(id: String)
}
```

## 10. SyncWorker Pattern

```kotlin
@HiltWorker
class SyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val syncManager: SyncManager
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            syncManager.syncAll()
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) Result.retry() else Result.failure()
        }
    }
}

// Schedule periodic sync
val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()
    )
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
    .build()

WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "periodic_sync", ExistingPeriodicWorkPolicy.KEEP, syncRequest
)
```

## 11. Secure Storage

```kotlin
class SecurePreferences @Inject constructor(@ApplicationContext context: Context) {
    private val prefs = EncryptedSharedPreferences.create(
        context, "secure_prefs",
        MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build(),
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    var accessToken: String?
        get() = prefs.getString("access_token", null)
        set(value) = prefs.edit().putString("access_token", value).apply()

    var refreshToken: String?
        get() = prefs.getString("refresh_token", null)
        set(value) = prefs.edit().putString("refresh_token", value).apply()

    fun clearAll() = prefs.edit().clear().apply()
}
```

## 12. Network Monitor

```kotlin
class NetworkMonitor @Inject constructor(@ApplicationContext context: Context) {
    private val connectivityManager =
        context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager

    val isOnline: StateFlow<Boolean> = callbackFlow {
        val callback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) { trySend(true) }
            override fun onLost(network: Network) { trySend(false) }
        }
        connectivityManager.registerDefaultNetworkCallback(callback)
        // Emit initial state
        trySend(connectivityManager.activeNetwork != null)
        awaitClose { connectivityManager.unregisterNetworkCallback(callback) }
    }.stateIn(CoroutineScope(Dispatchers.IO), SharingStarted.Eagerly, false)

    fun isOnline(): Boolean = isOnline.value
}
```

## 13. Result Wrapper

```kotlin
sealed class Resource<T>(val data: T? = null, val message: String? = null) {
    class Success<T>(data: T) : Resource<T>(data)
    class Error<T>(message: String, data: T? = null) : Resource<T>(data, message)
    class Loading<T>(data: T? = null) : Resource<T>(data)
}
```

## 14. Test Patterns

### ViewModel Test with Turbine

```kotlin
@Test
fun `loadProducts emits success state`() = runTest {
    val products = listOf(Product(id = "1", name = "Widget"))
    coEvery { getProductsUseCase(any()) } returns flowOf(Resource.Success(products))

    val viewModel = ProductListViewModel(getProductsUseCase)

    viewModel.uiState.test {
        val state = awaitItem()
        assertFalse(state.isLoading)
        assertEquals(1, state.products.size)
        assertEquals("Widget", state.products[0].name)
    }
}
```

### Compose UI Test

```kotlin
@Test
fun productList_displaysItems() {
    composeTestRule.setContent {
        ProductListScreen(
            viewModel = fakeViewModel(products = listOf(testProduct)),
            onProductClick = {}
        )
    }
    composeTestRule.onNodeWithText("Widget").assertIsDisplayed()
}
```

### Room DAO Test

```kotlin
@Test
fun searchProducts_returnsMatchingResults() = runTest {
    val db = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java).build()
    val dao = db.productDao()
    dao.upsertAll(listOf(
        ProductEntity(id = "1", tenantId = "t1", name = "Widget", price = 10.0, stockQuantity = 5),
        ProductEntity(id = "2", tenantId = "t1", name = "Gadget", price = 20.0, stockQuantity = 3)
    ))
    val results = dao.searchProducts("Wid")
    assertEquals(1, results.size)
    assertEquals("Widget", results[0].name)
}
```

### MockWebServer API Test

```kotlin
@Test
fun login_sendsCorrectRequest() = runTest {
    val mockServer = MockWebServer()
    mockServer.enqueue(MockResponse().setBody("""{"success":true,"data":{"access_token":"tok"}}"""))
    val api = Retrofit.Builder()
        .baseUrl(mockServer.url("/"))
        .addConverterFactory(MoshiConverterFactory.create())
        .build()
        .create(AuthService::class.java)

    val response = api.login(LoginRequest("user@test.com", "pass123"))
    assertTrue(response.success)

    val request = mockServer.takeRequest()
    assertEquals("POST", request.method)
    assertEquals("/auth/login", request.path)
}
```
