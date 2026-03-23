# API Integration Patterns Reference

Patterns for bridging an existing web SaaS backend to a native Android client. Covers API contract design, response handling, pagination, offline queue, and conflict resolution.

[Back to SKILL.md](../SKILL.md)

---

## 1. Standard API Response Envelope

Every endpoint must return this structure. Document it in `api-contract/01-overview.md`.

```json
{
  "success": true,
  "data": { /* payload */ },
  "message": "Optional human-readable message",
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

**Error envelope:**

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The given data was invalid.",
    "details": {
      "email": ["The email field is required."],
      "password": ["Password must be at least 8 characters."]
    }
  }
}
```

## 2. Kotlin DTOs Matching the Envelope

```kotlin
@JsonClass(generateAdapter = true)
data class ApiResponse<T>(
    val success: Boolean,
    val data: T?,
    val message: String?,
    val meta: PaginationMeta?
)

@JsonClass(generateAdapter = true)
data class ApiError(
    val code: String,
    val message: String,
    val details: Map<String, List<String>>?
)

@JsonClass(generateAdapter = true)
data class PaginationMeta(
    val page: Int,
    val per_page: Int,
    val total: Int,
    val total_pages: Int
)
```

## 3. Safe API Call Wrapper

```kotlin
suspend fun <T> safeApiCall(call: suspend () -> T): Resource<T> {
    return try {
        Resource.Success(call())
    } catch (e: HttpException) {
        val errorBody = e.response()?.errorBody()?.string()
        val apiError = try {
            Moshi.Builder().build().adapter(ApiError::class.java).fromJson(errorBody ?: "")
        } catch (_: Exception) { null }
        Resource.Error(apiError?.message ?: "HTTP ${e.code()}: ${e.message()}")
    } catch (e: IOException) {
        Resource.Error("Network error. Check your connection.")
    } catch (e: Exception) {
        Resource.Error(e.message ?: "Unknown error")
    }
}
```

## 4. Pagination Patterns

### Offset-Based (most PHP backends)

```kotlin
interface ProductService {
    @GET("api/v1/products")
    suspend fun getProducts(
        @Query("page") page: Int = 1,
        @Query("per_page") perPage: Int = 20,
        @Query("search") query: String? = null,
        @Query("sort") sort: String = "name",
        @Query("order") order: String = "asc"
    ): ApiResponse<List<ProductDto>>
}
```

### Cursor-Based (for infinite scroll with real-time data)

```kotlin
interface ActivityService {
    @GET("api/v1/activities")
    suspend fun getActivities(
        @Query("cursor") cursor: String? = null,
        @Query("limit") limit: Int = 20
    ): ApiResponse<List<ActivityDto>>
    // Response meta includes: { "next_cursor": "abc123" }
}
```

### Paging 3 Integration

```kotlin
class ProductPagingSource(
    private val api: ProductService,
    private val query: String?
) : PagingSource<Int, Product>() {

    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, Product> {
        val page = params.key ?: 1
        return try {
            val response = api.getProducts(page = page, perPage = params.loadSize, query = query)
            LoadResult.Page(
                data = response.data?.map { it.toDomain() } ?: emptyList(),
                prevKey = if (page == 1) null else page - 1,
                nextKey = if (page >= (response.meta?.total_pages ?: 0)) null else page + 1
            )
        } catch (e: Exception) {
            LoadResult.Error(e)
        }
    }

    override fun getRefreshKey(state: PagingState<Int, Product>): Int? {
        return state.anchorPosition?.let { anchor ->
            state.closestPageToPosition(anchor)?.prevKey?.plus(1)
                ?: state.closestPageToPosition(anchor)?.nextKey?.minus(1)
        }
    }
}
```

## 5. Authentication Flow

### JWT Auth Sequence

```
┌──────────┐          ┌──────────┐          ┌──────────┐
│  Android  │          │   API    │          │   DB     │
└─────┬────┘          └─────┬────┘          └─────┬────┘
      │  POST /auth/login    │                     │
      │─────────────────────>│  Validate creds     │
      │                      │────────────────────>│
      │                      │<────────────────────│
      │  { access, refresh } │                     │
      │<─────────────────────│                     │
      │                      │                     │
      │  Store in Encrypted  │                     │
      │  SharedPreferences   │                     │
      │                      │                     │
      │  GET /resource       │                     │
      │  Authorization:      │                     │
      │  Bearer <access>     │                     │
      │─────────────────────>│                     │
      │                      │                     │
      │  401 Token Expired   │                     │
      │<─────────────────────│                     │
      │                      │                     │
      │  POST /auth/refresh  │                     │
      │  { refresh_token }   │                     │
      │─────────────────────>│                     │
      │  { new access,       │                     │
      │    new refresh }     │                     │
      │<─────────────────────│                     │
      │                      │                     │
      │  Retry original      │                     │
      │  GET /resource       │                     │
      │─────────────────────>│                     │
```

### Tenant Context Header

For multi-tenant SaaS, inject tenant/shop context:

```kotlin
class TenantInterceptor @Inject constructor(
    private val sessionManager: SessionManager
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val tenantId = sessionManager.getCurrentTenantId()
        val shopId = sessionManager.getCurrentShopId()
        val request = chain.request().newBuilder().apply {
            tenantId?.let { header("X-Tenant-ID", it) }
            shopId?.let { header("X-Shop-ID", it) }
        }.build()
        return chain.proceed(request)
    }
}
```

## 6. Offline Sync Queue

### Queue Entity

```kotlin
@Entity(tableName = "sync_queue")
data class SyncQueueEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val operation: String,         // "CREATE", "UPDATE", "DELETE"
    val endpoint: String,          // "/api/v1/sales"
    val method: String,            // "POST", "PUT", "DELETE"
    val payload: String,           // JSON string of request body
    val localRefId: String,        // Local ID of the entity (for linking)
    val status: Int = 0,           // 0=pending, 1=processing, 2=sent, 3=failed
    val attempts: Int = 0,
    val lastError: String? = null,
    val createdAt: Long = System.currentTimeMillis()
)
```

### Queue Processor

```kotlin
class SyncQueueProcessor @Inject constructor(
    private val dao: SyncQueueDao,
    private val okHttpClient: OkHttpClient,
    private val baseUrl: String
) {
    suspend fun processQueue() {
        val pending = dao.getPending()
        for (item in pending) {
            dao.markProcessing(item.id)
            try {
                val request = Request.Builder()
                    .url("$baseUrl${item.endpoint}")
                    .method(item.method, item.payload.toRequestBody("application/json".toMediaType()))
                    .build()
                val response = okHttpClient.newCall(request).execute()
                if (response.isSuccessful) {
                    dao.markSent(item.id)
                    // Update local entity with server-assigned ID if CREATE
                    if (item.operation == "CREATE") {
                        val serverData = response.body?.string()
                        updateLocalEntity(item.localRefId, serverData)
                    }
                } else {
                    dao.markFailed(item.id, "HTTP ${response.code}", item.attempts + 1)
                }
            } catch (e: Exception) {
                dao.markFailed(item.id, e.message ?: "Unknown", item.attempts + 1)
            }
        }
    }
}
```

## 7. Conflict Resolution Strategies

Use this table in `sds/04-offline-sync.md`:

| Strategy | When to Use | Example |
|----------|-------------|---------|
| **Server Wins** | Reference data (products, prices) | Product catalog updated by admin |
| **Client Wins** | User-authored data (notes, preferences) | User's custom settings |
| **Last Write Wins** | Timestamped records where latest is correct | Customer address update |
| **Merge** | Non-conflicting fields can coexist | Two users update different fields |
| **Manual Resolution** | Business-critical data requiring human review | Inventory count discrepancy |

### Conflict Detection

```kotlin
data class SyncResponse(
    val accepted: List<String>,      // IDs accepted by server
    val conflicts: List<ConflictItem> // Items with conflicts
)

data class ConflictItem(
    val localId: String,
    val serverId: String,
    val serverVersion: Long,         // Server's updatedAt
    val localVersion: Long,          // Client's updatedAt
    val resolution: String           // "server_wins" | "merge" | "manual"
)
```

## 8. Staleness Budget Table

Include in `sds/04-offline-sync.md`:

| Data Type | Max Staleness | Refresh Trigger | Fallback |
|-----------|--------------|-----------------|----------|
| Product catalog | 24 hours | App foreground, pull-to-refresh | Show cached + "Last updated X ago" |
| Prices | 4 hours | Before sale, periodic sync | Show cached + staleness warning |
| Stock levels | 1 hour | Before sale, periodic sync | Show cached + "may be outdated" |
| Customer list | 12 hours | Customer screen open, search | Show cached |
| User permissions | On login | Login, token refresh | Use cached permissions |
| App config | 24 hours | App start | Use cached config |

## 9. Bootstrap vs Delta Sync

### Bootstrap (First Login)

```
1. User logs in → receives JWT
2. App calls GET /sync/bootstrap
3. Server returns: products, customers, settings, permissions
4. App stores all data in Room
5. App records lastSyncTimestamp
6. Dashboard loads from local data
```

### Delta Sync (Subsequent)

```
1. App sends GET /sync/delta?since={lastSyncTimestamp}
2. Server returns only changed records since timestamp
3. App upserts changed records into Room
4. App processes outbound sync queue
5. App updates lastSyncTimestamp
```

## 10. API Endpoint Documentation Checklist

When documenting each endpoint, verify:

- [ ] HTTP method and full path
- [ ] Authentication requirement (yes/no)
- [ ] Required request headers (Authorization, X-Tenant-ID, Content-Type)
- [ ] Request body with ALL fields, types, and validation rules
- [ ] Complete JSON request example with realistic data
- [ ] Success response with complete JSON example
- [ ] All possible error responses with status codes and error codes
- [ ] Rate limiting (if applicable)
- [ ] Pagination parameters (if list endpoint)
- [ ] Sort/filter parameters (if applicable)
- [ ] Notes on offline behavior (can this be queued?)

## 11. Mapping Web Endpoints to Mobile

When auditing the existing web app, create this mapping table:

| Web Endpoint | Mobile Equivalent | Changes Needed | Priority |
|-------------|-------------------|---------------|----------|
| GET /api/v1/products | Same | Add cursor pagination | P0 |
| POST /api/v1/sales | Same | Add offline queue support | P0 |
| GET /pages/dashboard.php | GET /api/v1/dashboard/summary | **New endpoint needed** | P0 |
| GET /pages/reports.php | GET /api/v1/reports/{type} | **New endpoint needed** | P2 |
| POST /ajax/upload.php | POST /api/v1/files | Standardize response | P1 |

**Common gaps when porting web to mobile:**
1. Dashboard endpoints — web may render server-side, mobile needs JSON API
2. Report endpoints — web may use HTML tables, mobile needs structured JSON
3. File upload — web may use form multipart, mobile prefers standard REST
4. Real-time — web may use polling, mobile prefers WebSocket or FCM
5. Search — web may use server-side rendering, mobile needs search API endpoint

## 12. Certificate Pinning

```kotlin
val certificatePinner = CertificatePinner.Builder()
    .add("api.yoursaas.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
    .add("api.yoursaas.com", "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=")
    .build()

val client = OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .build()
```

**Note:** Always pin at least 2 certificates (primary + backup). Document the pin hashes and expiry dates in the SDS security section.

## 13. Build Variants

```kotlin
// app/build.gradle.kts
android {
    buildTypes {
        debug {
            buildConfigField("String", "BASE_URL", "\"https://dev-api.yoursaas.com/\"")
            buildConfigField("Boolean", "ENABLE_LOGGING", "true")
        }
        create("staging") {
            buildConfigField("String", "BASE_URL", "\"https://staging-api.yoursaas.com/\"")
            buildConfigField("Boolean", "ENABLE_LOGGING", "true")
        }
        release {
            buildConfigField("String", "BASE_URL", "\"https://api.yoursaas.com/\"")
            buildConfigField("Boolean", "ENABLE_LOGGING", "false")
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
}
```

## 14. CI/CD Release Pipeline Template

```yaml
name: Release
on:
  push:
    tags: ['v*']

jobs:
  build-release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }

      - name: Decode keystore
        run: echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 -d > app/release.keystore

      - name: Build signed AAB
        run: ./gradlew bundleRelease
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}

      - name: Upload to Play Store (internal track)
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.PLAY_SERVICE_ACCOUNT }}
          packageName: com.company.app
          releaseFiles: app/build/outputs/bundle/release/app-release.aab
          track: internal
          status: completed
```
