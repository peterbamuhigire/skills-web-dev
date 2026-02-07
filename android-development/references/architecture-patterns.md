# Architecture Patterns

MVVM with Clean Architecture for scalable, testable Android applications.

**Reference:** See [Now in Android](https://github.com/android/nowinandroid) for a production example of these patterns.

## Layer Overview

```
┌─────────────────────────────────┐
│   Presentation Layer            │  Compose UI + ViewModels
│   (Android-dependent)           │
├─────────────────────────────────┤
│   Domain Layer                  │  Use Cases + Repository Interfaces
│   (Pure Kotlin - no Android)    │
├─────────────────────────────────┤
│   Data Layer                    │  Repository Impl + API + Room
│   (Android-dependent)           │
└─────────────────────────────────┘
```

## Data Layer

Pure data operations. Implements domain interfaces.

```kotlin
// Repository interface (lives in domain/core layer)
interface UserRepository {
    suspend fun getUser(userId: String): Result<User>
    suspend fun updateUser(user: User): Result<Unit>
    fun observeUser(userId: String): Flow<User>
}

// Repository implementation (lives in data layer)
class UserRepositoryImpl @Inject constructor(
    private val apiService: UserApiService,
    private val userDao: UserDao,
    private val tokenManager: TokenManager,
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher
) : UserRepository {

    override suspend fun getUser(userId: String): Result<User> =
        withContext(ioDispatcher) {
            try {
                val token = tokenManager.getToken()
                    ?: return@withContext Result.failure(AuthException("Not authenticated"))

                val response = apiService.getUser(userId, "Bearer $token")
                if (response.success && response.data != null) {
                    val user = response.data.toDomain()
                    userDao.insertUser(user.toEntity()) // Cache locally
                    Result.success(user)
                } else {
                    Result.failure(ApiException(response.message ?: "Unknown error"))
                }
            } catch (e: IOException) {
                // Fallback to cache on network error
                val cached = userDao.getUserById(userId)
                if (cached != null) Result.success(cached.toDomain())
                else Result.failure(NetworkException("Offline, no cached data"))
            }
        }

    override fun observeUser(userId: String): Flow<User> =
        userDao.observeUser(userId).map { it.toDomain() }
}
```

## Domain Layer

Business logic. No Android dependencies.

```kotlin
// Use Case - single responsibility
class GetUserUseCase @Inject constructor(
    private val repository: UserRepository
) {
    suspend operator fun invoke(userId: String): Result<User> {
        return repository.getUser(userId)
    }
}

// Use Case with business logic
class PlaceOrderUseCase @Inject constructor(
    private val orderRepository: OrderRepository,
    private val inventoryRepository: InventoryRepository
) {
    suspend operator fun invoke(order: Order): Result<OrderConfirmation> {
        // Business rule: check stock before placing order
        val stockCheck = inventoryRepository.checkStock(order.items)
        if (!stockCheck.allAvailable) {
            return Result.failure(
                InsufficientStockException(stockCheck.unavailableItems)
            )
        }

        return orderRepository.placeOrder(order)
    }
}
```

### Use Case Rules

- **One public function** per use case (`operator fun invoke`)
- **Single responsibility** - one business operation
- **No Android imports** - pure Kotlin
- **Inject repositories** - never access data sources directly
- **Return `Result<T>`** - let presentation decide how to handle errors

## Presentation Layer

UI state management and display.

```kotlin
@HiltViewModel
class UserProfileViewModel @Inject constructor(
    private val getUserUseCase: GetUserUseCase,
    private val updateUserUseCase: UpdateUserUseCase,
    savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val userId: String = checkNotNull(savedStateHandle["userId"])

    private val _uiState = MutableStateFlow(UserProfileUiState())
    val uiState: StateFlow<UserProfileUiState> = _uiState.asStateFlow()

    // Side effects channel (one-time events)
    private val _sideEffects = Channel<UserProfileSideEffect>()
    val sideEffects = _sideEffects.receiveAsFlow()

    init {
        loadUserProfile()
    }

    fun loadUserProfile() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }

            getUserUseCase(userId).fold(
                onSuccess = { user ->
                    _uiState.update {
                        it.copy(isLoading = false, user = user)
                    }
                },
                onFailure = { error ->
                    _uiState.update {
                        it.copy(isLoading = false, error = error.message)
                    }
                }
            )
        }
    }

    fun updateProfile(name: String, email: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isSaving = true) }

            val updatedUser = _uiState.value.user?.copy(name = name, email = email)
                ?: return@launch

            updateUserUseCase(updatedUser).fold(
                onSuccess = {
                    _uiState.update { it.copy(isSaving = false, user = updatedUser) }
                    _sideEffects.send(UserProfileSideEffect.ShowMessage("Profile updated"))
                },
                onFailure = { error ->
                    _uiState.update { it.copy(isSaving = false) }
                    _sideEffects.send(
                        UserProfileSideEffect.ShowMessage("Update failed: ${error.message}")
                    )
                }
            )
        }
    }

    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }
}

// UI State - immutable data class
data class UserProfileUiState(
    val isLoading: Boolean = false,
    val isSaving: Boolean = false,
    val user: User? = null,
    val error: String? = null
) {
    val isEmpty: Boolean get() = !isLoading && user == null && error == null
}

// Side Effects - one-time events
sealed interface UserProfileSideEffect {
    data class ShowMessage(val message: String) : UserProfileSideEffect
    data class NavigateTo(val route: String) : UserProfileSideEffect
}
```

## Navigation Pattern

```kotlin
// Navigation graph setup
@Composable
fun AppNavGraph(
    navController: NavHostController = rememberNavController()
) {
    NavHost(
        navController = navController,
        startDestination = "home"
    ) {
        composable("home") {
            HomeScreen(
                onNavigateToProfile = { userId ->
                    navController.navigate("profile/$userId")
                }
            )
        }

        composable(
            route = "profile/{userId}",
            arguments = listOf(navArgument("userId") { type = NavType.StringType })
        ) {
            UserProfileScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }
    }
}
```

### Navigation Rules

- **Screens receive callbacks**, not `NavController`
- **ViewModel reads `SavedStateHandle`** for navigation arguments
- **Type-safe routes** with argument definitions
- **Deep link support** via `deepLinks` parameter

## Data Flow Summary

```
User Action -> Composable -> ViewModel -> Use Case -> Repository -> API/DB
                                                          |
UI Update  <- Composable <- StateFlow <- ViewModel <- Result<T>
```
