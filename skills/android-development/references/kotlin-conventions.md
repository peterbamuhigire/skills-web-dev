# Kotlin Coding Conventions

Standard Kotlin and Jetpack Compose coding style for consistent, readable code.

## Local Development Networking (WAMP)

- On local Windows/Ubuntu dev machines, the Android emulator must reach the backend via the host machine's static LAN IP, not `localhost`.
- Ensure firewall rules allow inbound access to the WAMP HTTP port.

## Language Standards

- **Kotlin 100%** for all new code
- Follow [Kotlin official style guide](https://kotlinlang.org/docs/coding-conventions.html)
- Use Kotlin-specific idioms over Java patterns

## Import Organization

```kotlin
// Standard ordering: Android, Compose, third-party, project
package com.company.feature.presentation.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.company.core.models.User
import com.company.feature.presentation.viewmodels.UserViewModel
```

## Composable Function Standards

```kotlin
/**
 * Screen documentation - describe purpose and key behaviors.
 *
 * @param userId The unique identifier for the user
 * @param onNavigateBack Callback for back navigation
 */
@Composable
fun UserProfileScreen(
    userId: String,
    onNavigateBack: () -> Unit,
    modifier: Modifier = Modifier,          // Always accept modifier
    viewModel: UserViewModel = hiltViewModel()
) {
    // 1. State collection
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    // 2. Side effects
    LaunchedEffect(userId) {
        viewModel.loadUser(userId)
    }

    // 3. UI structure
    Scaffold(
        topBar = {
            StandardTopBar(
                title = "User Profile",
                onBackClick = onNavigateBack
            )
        }
    ) { paddingValues ->
        UserProfileContent(
            uiState = uiState,
            modifier = modifier.padding(paddingValues)
        )
    }
}
```

### Composable Rules

1. **Stateless by default** - hoist state to ViewModel
2. **`Modifier` as last default param** - always accept, always pass down
3. **Split large composables** - extract sub-composables for readability
4. **Private sub-composables** - use `private` for screen-internal components
5. **No side effects in composition** - use `LaunchedEffect`, `DisposableEffect`

## State Modeling with Sealed Classes

```kotlin
sealed interface UserUiState {
    object Loading : UserUiState
    data class Success(val user: User) : UserUiState
    data class Error(val message: String) : UserUiState
}

// Usage in composable
@Composable
private fun UserProfileContent(
    uiState: UserUiState,
    modifier: Modifier = Modifier
) {
    when (uiState) {
        is UserUiState.Loading -> LoadingIndicator()
        is UserUiState.Error -> ErrorMessage(uiState.message)
        is UserUiState.Success -> UserDetails(user = uiState.user)
    }
}
```

## Coroutines and Flow

```kotlin
// ViewModel - use StateFlow, not mutableStateOf
@HiltViewModel
class UserViewModel @Inject constructor(
    private val getUserUseCase: GetUserUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow<UserUiState>(UserUiState.Loading)
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _uiState.value = UserUiState.Loading
            getUserUseCase(userId).fold(
                onSuccess = { _uiState.value = UserUiState.Success(it) },
                onFailure = { _uiState.value = UserUiState.Error(it.message ?: "Error") }
            )
        }
    }
}
```

### Async Rules

- **Coroutines + Flow** for all async work (never callbacks)
- **`viewModelScope`** for ViewModel coroutines (auto-cancelled)
- **`StateFlow`** for UI state (not `LiveData` in new code)
- **`collectAsStateWithLifecycle()`** in Compose (lifecycle-aware)
- **Dispatcher injection** for testability:

```kotlin
class UserRepositoryImpl @Inject constructor(
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher
) : UserRepository {
    override suspend fun getUser(id: String): Result<User> =
        withContext(ioDispatcher) { /* ... */ }
}
```

## Kotlin Idioms

### Use `Result` for Error Handling

```kotlin
suspend fun getUser(id: String): Result<User>

// Calling code
getUser(id).fold(
    onSuccess = { user -> /* handle success */ },
    onFailure = { error -> /* handle error */ }
)
```

### Use Extension Functions

```kotlin
// Good: extension for utility
fun String.toFormattedPhone(): String {
    return "+${take(3)} ${drop(3).take(3)} ${drop(6)}"
}

// Good: Compose modifier extension
fun Modifier.standardPadding() = this.padding(DesignSystem.Spacing.md)
```

### Use `sealed interface` Over `sealed class`

```kotlin
// Preferred: sealed interface (more flexible)
sealed interface NavigationEvent {
    data class GoToDetail(val id: String) : NavigationEvent
    object GoBack : NavigationEvent
}
```

### Data Classes for DTOs and Models

```kotlin
data class User(
    val id: String,
    val name: String,
    val email: String,
    val avatarUrl: String? = null
)

// DTO with mapping
data class UserDto(
    @SerializedName("user_id") val userId: String,
    @SerializedName("full_name") val fullName: String,
    val email: String
) {
    fun toDomain() = User(
        id = userId,
        name = fullName,
        email = email
    )
}
```

### Null Safety

```kotlin
// Use safe calls and Elvis operator
val displayName = user?.name ?: "Unknown"

// Use let for null checks with operations
user?.let { saveToDatabase(it) }

// Avoid !! - use requireNotNull with message if truly needed
val token = requireNotNull(authManager.getToken()) {
    "Authentication token must not be null"
}
```

## Naming Conventions

| Element            | Convention           | Example                         |
| ------------------ | -------------------- | ------------------------------- |
| Classes            | PascalCase           | `UserViewModel`                 |
| Functions          | camelCase            | `loadUserProfile()`             |
| Properties         | camelCase            | `val userName`                  |
| Constants          | SCREAMING_SNAKE      | `const val MAX_RETRIES = 3`     |
| Composables        | PascalCase           | `UserProfileScreen()`           |
| Packages           | lowercase            | `com.company.feature`           |
| Backing properties | underscore prefix    | `private val _uiState`          |
| Boolean properties | is/has/should prefix | `val isLoading`, `val hasError` |

## Documentation

```kotlin
/**
 * Brief one-line description.
 *
 * Longer description if needed - explain WHY, not WHAT.
 *
 * @param userId Unique user identifier
 * @return User profile or error result
 * @throws IllegalStateException if not authenticated
 */
```

- Document public APIs and complex logic
- Skip obvious documentation (getters, simple composables)
- Use `@param`, `@return`, `@throws` for public functions
