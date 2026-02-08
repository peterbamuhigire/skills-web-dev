# Testing Standards

Comprehensive testing patterns for ViewModels, Use Cases, and Compose UI.

**References:** See [Architecture Samples](https://github.com/android/architecture-samples) for shared test implementations (unit + integration + E2E) and [JetNews](https://github.com/android/compose-samples/tree/main/JetNews) for Compose UI testing patterns.

## Test Structure

```
app/src/
├── test/                          # Unit tests (JVM)
│   └── kotlin/com/company/
│       ├── core/
│       │   └── usecases/
│       │       └── GetUserUseCaseTest.kt
│       ├── presentation/
│       │   └── viewmodels/
│       │       └── UserViewModelTest.kt
│       └── data/
│           └── repositories/
│               └── UserRepositoryImplTest.kt
└── androidTest/                   # Instrumentation tests
    └── kotlin/com/company/
        └── presentation/
            └── screens/
                └── UserProfileScreenTest.kt
```

## ViewModel Tests

```kotlin
class UserProfileViewModelTest {

    // Replace Dispatchers.Main with test dispatcher
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val getUserUseCase: GetUserUseCase = mockk()
    private val updateUserUseCase: UpdateUserUseCase = mockk()
    private val savedStateHandle = SavedStateHandle(mapOf("userId" to "user-123"))

    private lateinit var viewModel: UserProfileViewModel

    @Before
    fun setup() {
        viewModel = UserProfileViewModel(
            getUserUseCase = getUserUseCase,
            updateUserUseCase = updateUserUseCase,
            savedStateHandle = savedStateHandle
        )
    }

    @Test
    fun `loadUserProfile emits loading then success`() = runTest {
        // Arrange
        val testUser = User(id = "user-123", name = "John Doe", email = "john@test.com")
        coEvery { getUserUseCase("user-123") } returns Result.success(testUser)

        // Act & Assert with Turbine
        viewModel.uiState.test {
            // Initial state
            val initial = awaitItem()
            assertThat(initial.isLoading).isFalse()

            // Trigger load
            viewModel.loadUserProfile("user-123")

            // Loading state
            val loading = awaitItem()
            assertThat(loading.isLoading).isTrue()

            // Success state
            val success = awaitItem()
            assertThat(success.isLoading).isFalse()
            assertThat(success.user).isEqualTo(testUser)
            assertThat(success.error).isNull()
        }
    }

    @Test
    fun `loadUserProfile emits error on failure`() = runTest {
        // Arrange
        coEvery { getUserUseCase("user-123") } returns
            Result.failure(RuntimeException("Network error"))

        // Act & Assert
        viewModel.uiState.test {
            awaitItem() // Initial

            viewModel.loadUserProfile("user-123")
            awaitItem() // Loading

            val error = awaitItem()
            assertThat(error.isLoading).isFalse()
            assertThat(error.error).isEqualTo("Network error")
        }
    }

    @Test
    fun `updateProfile sends success side effect`() = runTest {
        // Arrange
        val user = User(id = "user-123", name = "John", email = "john@test.com")
        coEvery { getUserUseCase("user-123") } returns Result.success(user)
        coEvery { updateUserUseCase(any()) } returns Result.success(Unit)

        viewModel.loadUserProfile("user-123")

        // Act & Assert
        viewModel.sideEffects.test {
            viewModel.updateProfile("Jane", "jane@test.com")

            val effect = awaitItem()
            assertThat(effect).isInstanceOf(SideEffect.ShowMessage::class.java)
        }
    }
}
```

### Main Dispatcher Rule

```kotlin
class MainDispatcherRule(
    private val testDispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : TestWatcher() {

    override fun starting(description: Description) {
        Dispatchers.setMain(testDispatcher)
    }

    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}
```

## Use Case Tests

```kotlin
class GetUserUseCaseTest {

    private val userRepository: UserRepository = mockk()
    private val useCase = GetUserUseCase(userRepository)

    @Test
    fun `invoke returns user from repository`() = runTest {
        // Arrange
        val expected = User(id = "1", name = "Test", email = "test@test.com")
        coEvery { userRepository.getUser("1") } returns Result.success(expected)

        // Act
        val result = useCase("1")

        // Assert
        assertThat(result.isSuccess).isTrue()
        assertThat(result.getOrNull()).isEqualTo(expected)
        coVerify(exactly = 1) { userRepository.getUser("1") }
    }

    @Test
    fun `invoke propagates repository errors`() = runTest {
        // Arrange
        coEvery { userRepository.getUser("1") } returns
            Result.failure(NetworkException("Offline"))

        // Act
        val result = useCase("1")

        // Assert
        assertThat(result.isFailure).isTrue()
        assertThat(result.exceptionOrNull()).isInstanceOf(NetworkException::class.java)
    }
}
```

## Repository Tests

```kotlin
class UserRepositoryImplTest {

    private val apiService: UserApiService = mockk()
    private val userDao: UserDao = mockk(relaxed = true)
    private val tokenManager: TokenManager = mockk()
    private val testDispatcher = StandardTestDispatcher()

    private val repository = UserRepositoryImpl(
        apiService = apiService,
        userDao = userDao,
        tokenManager = tokenManager,
        ioDispatcher = testDispatcher
    )

    @Test
    fun `getUser returns mapped domain model on success`() = runTest(testDispatcher) {
        // Arrange
        every { tokenManager.getToken() } returns "test-token"
        coEvery { apiService.getUser("1", "Bearer test-token") } returns ApiResponse(
            success = true,
            data = UserDto(userId = "1", fullName = "Test", email = "t@t.com")
        )

        // Act
        val result = repository.getUser("1")

        // Assert
        assertThat(result.isSuccess).isTrue()
        assertThat(result.getOrNull()?.name).isEqualTo("Test")
        coVerify { userDao.insertUser(any()) } // Cached locally
    }

    @Test
    fun `getUser falls back to cache on network error`() = runTest(testDispatcher) {
        // Arrange
        every { tokenManager.getToken() } returns "test-token"
        coEvery { apiService.getUser(any(), any()) } throws IOException("No network")
        coEvery { userDao.getUserById("1") } returns UserEntity(
            id = "1", name = "Cached", email = "c@c.com"
        )

        // Act
        val result = repository.getUser("1")

        // Assert
        assertThat(result.isSuccess).isTrue()
        assertThat(result.getOrNull()?.name).isEqualTo("Cached")
    }
}
```

## Compose UI Tests

```kotlin
@HiltAndroidTest
class UserProfileScreenTest {

    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun displayLoadingState() {
        composeTestRule.setContent {
            SaasAppTheme {
                UserProfileScreen(
                    userId = "test-123",
                    onNavigateBack = {},
                    onEditProfile = {}
                )
            }
        }

        composeTestRule
            .onNodeWithTag("loading_indicator")
            .assertIsDisplayed()
    }

    @Test
    fun displayUserDataAfterLoad() {
        composeTestRule.setContent {
            SaasAppTheme {
                UserProfileScreen(
                    userId = "test-123",
                    onNavigateBack = {},
                    onEditProfile = {}
                )
            }
        }

        composeTestRule.waitUntil(5000) {
            composeTestRule
                .onAllNodesWithTag("loading_indicator")
                .fetchSemanticsNodes().isEmpty()
        }

        composeTestRule.onNodeWithText("John Doe").assertIsDisplayed()
    }

    @Test
    fun displayErrorWithRetry() {
        // Inject error-producing repository via Hilt test module

        composeTestRule.setContent {
            SaasAppTheme {
                UserProfileScreen(
                    userId = "invalid",
                    onNavigateBack = {},
                    onEditProfile = {}
                )
            }
        }

        composeTestRule.waitUntil(5000) {
            composeTestRule
                .onAllNodesWithText("Retry")
                .fetchSemanticsNodes().isNotEmpty()
        }

        composeTestRule.onNodeWithText("Retry").assertIsDisplayed()
        composeTestRule.onNodeWithText("Retry").performClick()
    }
}
```

## Testing Libraries

| Library | Purpose |
|---------|---------|
| JUnit 4 | Test framework |
| MockK | Kotlin-native mocking |
| Turbine | Flow testing |
| Truth / AssertJ | Assertions |
| Coroutines Test | `runTest`, test dispatchers |
| Compose Test | UI testing with `ComposeTestRule` |
| Hilt Testing | DI in tests |

## Testing Rules

1. **Test behavior, not implementation** - focus on observable outcomes
2. **One assertion per test** (ideally) - clear failure messages
3. **Descriptive test names** - use backtick notation: `` `loads user on init` ``
4. **Arrange-Act-Assert** pattern consistently
5. **Mock at boundaries** - repositories for ViewModels, API for repositories
6. **Use Turbine** for all Flow assertions
7. **Test error paths** - not just happy paths
8. **Semantics tags** for Compose test node selection
