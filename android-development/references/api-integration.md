# API Integration Standards

Retrofit-based API integration with standardized error handling and repository pattern.

## API Service Interface

```kotlin
interface UserApiService {

    @GET("users/{userId}")
    suspend fun getUser(
        @Path("userId") userId: String,
        @Header("Authorization") token: String
    ): ApiResponse<UserDto>

    @GET("users")
    suspend fun getUsers(
        @Query("page") page: Int = 1,
        @Query("per_page") perPage: Int = 20,
        @Query("search") search: String? = null,
        @Header("Authorization") token: String
    ): ApiResponse<PaginatedResponse<UserDto>>

    @POST("users")
    suspend fun createUser(
        @Body request: CreateUserRequest,
        @Header("Authorization") token: String
    ): ApiResponse<UserDto>

    @PUT("users/{userId}")
    suspend fun updateUser(
        @Path("userId") userId: String,
        @Body request: UpdateUserRequest,
        @Header("Authorization") token: String
    ): ApiResponse<UserDto>

    @DELETE("users/{userId}")
    suspend fun deleteUser(
        @Path("userId") userId: String,
        @Header("Authorization") token: String
    ): ApiResponse<Unit>

    @Multipart
    @POST("users/{userId}/avatar")
    suspend fun uploadAvatar(
        @Path("userId") userId: String,
        @Part file: MultipartBody.Part,
        @Header("Authorization") token: String
    ): ApiResponse<AvatarResponse>
}
```

## Standard API Response Wrapper

```kotlin
data class ApiResponse<T>(
    @Json(name = "success") val success: Boolean,
    @Json(name = "data") val data: T? = null,
    @Json(name = "message") val message: String? = null,
    @Json(name = "errors") val errors: List<ApiError>? = null,
    @Json(name = "meta") val meta: PaginationMeta? = null
)

data class ApiError(
    @Json(name = "field") val field: String? = null,
    @Json(name = "message") val message: String
)

data class PaginationMeta(
    @Json(name = "current_page") val currentPage: Int,
    @Json(name = "last_page") val lastPage: Int,
    @Json(name = "per_page") val perPage: Int,
    @Json(name = "total") val total: Int
)

data class PaginatedResponse<T>(
    @Json(name = "items") val items: List<T>,
    @Json(name = "pagination") val pagination: PaginationMeta
)
```

## DTO and Domain Mapping

```kotlin
// Data Transfer Object (matches API JSON)
data class UserDto(
    @Json(name = "user_id") val userId: String,
    @Json(name = "full_name") val fullName: String,
    @Json(name = "email_address") val email: String,
    @Json(name = "phone_number") val phone: String?,
    @Json(name = "avatar_url") val avatarUrl: String?,
    @Json(name = "created_at") val createdAt: String
) {
    fun toDomain() = User(
        id = userId,
        name = fullName,
        email = email,
        phone = phone,
        avatarUrl = avatarUrl
    )
}

// Domain model (used in app)
data class User(
    val id: String,
    val name: String,
    val email: String,
    val phone: String? = null,
    val avatarUrl: String? = null
)

// Request DTOs
data class CreateUserRequest(
    @Json(name = "full_name") val name: String,
    @Json(name = "email_address") val email: String,
    @Json(name = "phone_number") val phone: String?
)
```

## Repository Implementation with Error Handling

```kotlin
class UserRepositoryImpl @Inject constructor(
    private val apiService: UserApiService,
    private val userDao: UserDao,
    private val tokenManager: TokenManager,
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher
) : UserRepository {

    override suspend fun getUser(userId: String): Result<User> =
        withContext(ioDispatcher) {
            safeApiCall {
                val token = requireToken()
                val response = apiService.getUser(userId, "Bearer $token")
                handleResponse(response) { it.toDomain() }
            }
        }

    override suspend fun getUsers(
        page: Int,
        search: String?
    ): Result<PaginatedResult<User>> =
        withContext(ioDispatcher) {
            safeApiCall {
                val token = requireToken()
                val response = apiService.getUsers(
                    page = page, search = search, token = "Bearer $token"
                )
                handleResponse(response) { paginated ->
                    PaginatedResult(
                        items = paginated.items.map { it.toDomain() },
                        currentPage = paginated.pagination.currentPage,
                        lastPage = paginated.pagination.lastPage,
                        total = paginated.pagination.total
                    )
                }
            }
        }

    private fun requireToken(): String {
        return tokenManager.getToken()
            ?: throw AuthException("Not authenticated")
    }

    private fun <T, R> handleResponse(
        response: ApiResponse<T>,
        mapper: (T) -> R
    ): Result<R> {
        return if (response.success && response.data != null) {
            Result.success(mapper(response.data))
        } else {
            val errorMessage = response.errors?.firstOrNull()?.message
                ?: response.message
                ?: "Unknown error"
            Result.failure(ApiException(errorMessage))
        }
    }
}
```

## Safe API Call Utility

```kotlin
suspend fun <T> safeApiCall(block: suspend () -> Result<T>): Result<T> {
    return try {
        block()
    } catch (e: HttpException) {
        when (e.code()) {
            401 -> Result.failure(AuthException("Session expired. Please login again."))
            403 -> Result.failure(PermissionException("You don't have permission."))
            404 -> Result.failure(NotFoundException("Resource not found."))
            422 -> {
                val errorBody = e.response()?.errorBody()?.string()
                val message = parseValidationErrors(errorBody)
                Result.failure(ValidationException(message))
            }
            in 500..599 -> Result.failure(ServerException("Server error. Try again later."))
            else -> Result.failure(ApiException("HTTP error: ${e.code()}"))
        }
    } catch (e: IOException) {
        Result.failure(NetworkException("No internet connection."))
    } catch (e: AuthException) {
        Result.failure(e)
    } catch (e: Exception) {
        Result.failure(UnexpectedException("Something went wrong: ${e.message}"))
    }
}
```

## Custom Exception Hierarchy

```kotlin
sealed class AppException(message: String) : Exception(message)

class AuthException(message: String) : AppException(message)
class NetworkException(message: String) : AppException(message)
class ApiException(message: String) : AppException(message)
class ValidationException(message: String) : AppException(message)
class PermissionException(message: String) : AppException(message)
class NotFoundException(message: String) : AppException(message)
class ServerException(message: String) : AppException(message)
class UnexpectedException(message: String) : AppException(message)
```

## File Upload

```kotlin
suspend fun uploadAvatar(userId: String, imageUri: Uri): Result<String> =
    withContext(ioDispatcher) {
        safeApiCall {
            val token = requireToken()

            val contentResolver = context.contentResolver
            val inputStream = contentResolver.openInputStream(imageUri)
                ?: return@safeApiCall Result.failure(ApiException("Cannot read file"))

            val bytes = inputStream.readBytes()
            inputStream.close()

            val requestBody = bytes.toRequestBody("image/*".toMediaType())
            val part = MultipartBody.Part.createFormData(
                "avatar", "avatar.jpg", requestBody
            )

            val response = apiService.uploadAvatar(userId, part, "Bearer $token")
            handleResponse(response) { it.url }
        }
    }
```

## API Integration Rules

1. **DTOs separate from domain models** - always map at repository boundary
2. **Token injection via interceptor** preferred over manual header passing
3. **Typed exception hierarchy** - catch specific errors in ViewModel
4. **Pagination support** via standard `PaginatedResult` wrapper
5. **File uploads** via `MultipartBody.Part`
6. **No raw Retrofit calls in ViewModels** - always go through repository
7. **Offline fallback** - cache API responses in Room when appropriate
