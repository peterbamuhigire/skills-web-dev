# Advanced TDD Techniques for Android

## 1. Test Data Factories

Avoid repeating object construction across tests. Use factories:

```kotlin
object UserFactory {
    fun make(
        id: Int = Random.nextInt(),
        name: String = "User-${UUID.randomUUID().toString().take(8)}",
        email: String = "${name.lowercase()}@test.com"
    ): User = User(id = id, name = name, email = email)

    fun makeList(count: Int = 3): List<User> =
        (1..count).map { make(id = it) }
}
```

**Usage in tests:**
```kotlin
@Test
fun displayUsers_showsAllUsers() {
    val users = UserFactory.makeList(5)
    whenever(repository.getUsers()).thenReturn(Result.success(users))

    viewModel.loadUsers()

    assertEquals(5, viewModel.users.value?.size)
}
```

**Benefits:**
- Reduces test boilerplate
- Centralizes test data creation
- Makes tests more readable
- Easy to add new required fields without updating every test

## 2. Behavior Verification with Mockito

### Verify method calls

```kotlin
@Test
fun saveUser_delegatesToRepository() {
    val user = UserFactory.make()
    viewModel.saveUser(user)
    verify(repository).save(eq(user))
}
```

### Verify call count

```kotlin
@Test
fun refreshData_callsApiOnce() {
    viewModel.refresh()
    verify(repository, times(1)).fetchFromApi()
}
```

### Verify no interactions

```kotlin
@Test
fun offlineMode_doesNotCallApi() {
    viewModel.setOfflineMode(true)
    viewModel.loadData()
    verifyNoInteractions(apiService)
}
```

### Argument captors

```kotlin
@Test
fun createUser_passesCorrectData() {
    val captor = argumentCaptor<User>()

    viewModel.createUser("Alice", "alice@test.com")

    verify(repository).save(captor.capture())
    assertEquals("Alice", captor.firstValue.name)
    assertEquals("alice@test.com", captor.firstValue.email)
}
```

## 3. Testing Coroutines

### Setup

```kotlin
class CoroutineViewModelTest {
    @get:Rule
    val mainCoroutineRule = MainCoroutineRule()

    private val testDispatcher = UnconfinedTestDispatcher()

    @Test
    fun loadData_emitsStatesInOrder() = runTest {
        val states = mutableListOf<UiState>()
        val job = launch { viewModel.uiState.toList(states) }

        viewModel.loadData()

        assertEquals(UiState.Loading, states[0])
        assertTrue(states[1] is UiState.Success)
        job.cancel()
    }
}
```

### Testing Flow emissions

```kotlin
@Test
fun searchUsers_emitsFilteredResults() = runTest {
    val results = viewModel.searchResults.first()
    viewModel.search("Ali")

    val filtered = viewModel.searchResults.first()
    assertTrue(filtered.all { it.name.contains("Ali") })
}
```

### Testing delays and timeouts

```kotlin
@Test
fun debounceSearch_waitsBeforeSearching() = runTest {
    viewModel.onSearchTextChanged("A")
    viewModel.onSearchTextChanged("Al")
    viewModel.onSearchTextChanged("Ali")

    advanceTimeBy(300) // Debounce period
    runCurrent()

    verify(repository, times(1)).search("Ali")
}
```

## 4. Testing LiveData

### InstantTaskExecutorRule

Required for synchronous LiveData observation in tests:

```kotlin
@get:Rule
val instantTaskExecutorRule = InstantTaskExecutorRule()
```

### Observing LiveData changes

```kotlin
@Test
fun toggleFavorite_updatesLiveData() {
    val observer = mock<Observer<Boolean>>()
    viewModel.isFavorite.observeForever(observer)

    viewModel.toggleFavorite()

    verify(observer).onChanged(true)
}
```

### LiveData test helper

```kotlin
fun <T> LiveData<T>.getOrAwaitValue(
    time: Long = 2,
    timeUnit: TimeUnit = TimeUnit.SECONDS
): T {
    var data: T? = null
    val latch = CountDownLatch(1)
    val observer = Observer<T> { value ->
        data = value
        latch.countDown()
    }
    observeForever(observer)
    if (!latch.await(time, timeUnit)) {
        throw TimeoutException("LiveData value never set.")
    }
    removeObserver(observer)
    @Suppress("UNCHECKED_CAST")
    return data as T
}
```

**Usage:**
```kotlin
@Test
fun loadUsers_updatesLiveData() {
    viewModel.loadUsers()
    val users = viewModel.users.getOrAwaitValue()
    assertEquals(3, users.size)
}
```

## 5. Testing Hilt-Injected Components

### Setup test module

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object TestRepositoryModule {
    @Provides
    @Singleton
    fun provideUserRepository(): UserRepository = mock()
}
```

### Hilt test

```kotlin
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class UserFeatureTest {
    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    @Inject
    lateinit var repository: UserRepository

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun injectedRepository_isAvailable() {
        assertNotNull(repository)
    }
}
```

## 6. Parameterized Tests

Test multiple inputs with a single test method:

```kotlin
@RunWith(Parameterized::class)
class EmailValidatorTest(
    private val email: String,
    private val expected: Boolean
) {
    companion object {
        @JvmStatic
        @Parameterized.Parameters(name = "{0} -> {1}")
        fun data() = listOf(
            arrayOf("user@test.com", true),
            arrayOf("invalid", false),
            arrayOf("", false),
            arrayOf("user@.com", false),
            arrayOf("a@b.c", true),
        )
    }

    @Test
    fun validate_returnsExpected() {
        assertEquals(expected, EmailValidator.isValid(email))
    }
}
```

## 7. Custom Test Assertions

Create domain-specific assertions for readability:

```kotlin
fun assertUiStateIsError(state: UiState, expectedMessage: String? = null) {
    assertTrue("Expected Error state, got $state", state is UiState.Error)
    expectedMessage?.let {
        assertEquals(it, (state as UiState.Error).message)
    }
}

fun assertUserEquals(expected: User, actual: User) {
    assertEquals(expected.name, actual.name)
    assertEquals(expected.email, actual.email)
    // Skip auto-generated fields like id, createdAt
}
```

## 8. Testing Error Handling

Always test failure paths:

```kotlin
@Test
fun loadData_networkError_showsRetryOption() = runTest {
    whenever(repository.getData())
        .thenReturn(Result.failure(IOException()))

    viewModel.loadData()

    val state = viewModel.uiState.value
    assertTrue(state is UiState.Error)
    assertTrue((state as UiState.Error).canRetry)
}

@Test
fun saveUser_validationError_showsFieldErrors() {
    viewModel.saveUser(name = "", email = "invalid")

    assertEquals("Name is required", viewModel.nameError.value)
    assertEquals("Invalid email format", viewModel.emailError.value)
}
```

## 9. Snapshot Testing (Compose)

Capture and compare UI screenshots:

```kotlin
@Test
fun userCard_matchesSnapshot() {
    composeRule.setContent {
        UserCard(user = UserFactory.make(name = "Alice"))
    }
    composeRule.onNodeWithTag("userCard")
        .captureToImage()
        .assertAgainstGolden(screenshotRule, "user_card_default")
}
```

## 10. Test Organization

```
app/src/test/
├── factories/           # Test data factories
│   ├── UserFactory.kt
│   └── ProductFactory.kt
├── helpers/             # Test utilities
│   ├── MainCoroutineRule.kt
│   └── LiveDataTestUtil.kt
├── domain/              # Domain model tests
├── data/                # Repository tests
│   ├── repository/
│   └── api/
└── presentation/        # ViewModel tests

app/src/androidTest/
├── db/                  # Room DAO tests
├── ui/                  # Espresso/Compose tests
└── e2e/                 # End-to-end flows
```
