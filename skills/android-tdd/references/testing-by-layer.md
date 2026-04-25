# Testing by Layer: Android Architecture

## Layer Overview

```
┌─────────────────────────┐
│   UI Layer (Espresso)   │  10% - Screen flows, user interactions
├─────────────────────────┤
│ ViewModel (JUnit+Mock)  │  20% - State management, business logic
├─────────────────────────┤
│  Repository (JUnit)     │  Integration - Data coordination
├─────────────────────────┤
│  Database (Room Test)   │  Integration - Persistence
├─────────────────────────┤
│  Network (MockWebServer)│  Integration - API calls
├─────────────────────────┤
│  Domain/Models (JUnit)  │  70% - Pure logic, no Android deps
└─────────────────────────┘
```

## 1. Domain / Model Layer (Unit Tests)

**Location:** `app/src/test/`
**Speed:** <1ms per test
**Dependencies:** None (pure Kotlin)

```kotlin
class ShoppingCartTest {
    private lateinit var cart: ShoppingCart

    @Before
    fun setup() {
        cart = ShoppingCart()
    }

    @Test
    fun addItem_emptyCart_hasOneItem() {
        cart.addItem(Product("Phone", 999.99))
        assertEquals(1, cart.itemCount)
    }

    @Test
    fun addMultipleItems_calculatesCorrectTotal() {
        cart.addItem(Product("Phone", 999.99))
        cart.addItem(Product("Case", 29.99))
        assertEquals(1029.98, cart.totalPrice, 0.01)
    }

    @Test
    fun removeItem_decreasesCount() {
        val product = Product("Phone", 999.99)
        cart.addItem(product)
        cart.removeItem(product)
        assertEquals(0, cart.itemCount)
    }

    @Test
    fun emptyCart_totalIsZero() {
        assertEquals(0.0, cart.totalPrice, 0.01)
    }
}
```

**Rules:**
- No mocking needed (pure logic)
- No Android framework references
- Fastest tests in the suite
- Test every business rule and edge case

## 2. ViewModel Layer (Unit + Integration)

**Location:** `app/src/test/`
**Speed:** ~10ms per test
**Dependencies:** Mocked repository, coroutine test dispatcher

```kotlin
class UserViewModelTest {
    @get:Rule
    val instantTaskExecutorRule = InstantTaskExecutorRule()

    @get:Rule
    val coroutineRule = MainCoroutineRule()

    private lateinit var repository: UserRepository
    private lateinit var viewModel: UserViewModel

    @Before
    fun setup() {
        repository = mock()
        viewModel = UserViewModel(repository)
    }

    @Test
    fun fetchUsers_success_updatesUiState() = runTest {
        val users = listOf(User("Alice"), User("Bob"))
        whenever(repository.getUsers()).thenReturn(Result.success(users))

        viewModel.fetchUsers()

        assertEquals(UiState.Success(users), viewModel.uiState.value)
    }

    @Test
    fun fetchUsers_error_showsErrorState() = runTest {
        whenever(repository.getUsers())
            .thenReturn(Result.failure(IOException("Network error")))

        viewModel.fetchUsers()

        assertTrue(viewModel.uiState.value is UiState.Error)
    }

    @Test
    fun fetchUsers_setsLoadingState() = runTest {
        val states = mutableListOf<UiState>()
        viewModel.uiState.observeForever { states.add(it) }

        viewModel.fetchUsers()

        assertTrue(states.contains(UiState.Loading))
    }
}
```

**MainCoroutineRule helper:**
```kotlin
class MainCoroutineRule(
    private val dispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : TestWatcher() {
    override fun starting(description: Description) {
        Dispatchers.setMain(dispatcher)
    }
    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}
```

## 3. Repository Layer (Integration)

**Location:** `app/src/test/`
**Speed:** ~50ms per test

```kotlin
class UserRepositoryTest {
    private lateinit var apiService: ApiService
    private lateinit var userDao: UserDao
    private lateinit var repository: UserRepository

    @Before
    fun setup() {
        apiService = mock()
        userDao = mock()
        repository = UserRepositoryImpl(apiService, userDao)
    }

    @Test
    fun getUsers_fetchesFromApiAndCachesLocally() = runTest {
        val apiUsers = listOf(UserDto("Alice"))
        whenever(apiService.getUsers()).thenReturn(apiUsers)

        repository.getUsers()

        verify(userDao).insertAll(any())
    }

    @Test
    fun getUsers_apiFailure_fallsBackToCache() = runTest {
        whenever(apiService.getUsers()).thenThrow(IOException())
        val cachedUsers = listOf(UserEntity("Bob"))
        whenever(userDao.getAll()).thenReturn(cachedUsers)

        val result = repository.getUsers()

        assertEquals(1, result.getOrNull()?.size)
    }
}
```

## 4. Database Layer (Instrumented)

**Location:** `app/src/androidTest/`
**Speed:** ~100ms per test
**Key:** Use in-memory database

```kotlin
@RunWith(AndroidJUnit4::class)
class UserDaoTest {
    private lateinit var database: AppDatabase
    private lateinit var dao: UserDao

    @Before
    fun setup() {
        database = Room.inMemoryDatabaseBuilder(
            ApplicationProvider.getApplicationContext(),
            AppDatabase::class.java
        ).allowMainThreadQueries().build()
        dao = database.userDao()
    }

    @After
    fun teardown() {
        database.close()
    }

    @Test
    fun insertAndRetrieve_returnsCorrectUser() = runTest {
        val user = UserEntity(id = 1, name = "Alice")
        dao.insert(user)

        val result = dao.getById(1)

        assertEquals("Alice", result?.name)
    }

    @Test
    fun deleteAll_clearsTable() = runTest {
        dao.insert(UserEntity(id = 1, name = "Alice"))
        dao.deleteAll()

        val result = dao.getAll()

        assertTrue(result.isEmpty())
    }
}
```

## 5. Network Layer (Unit/Integration)

**Location:** `app/src/test/`
**Speed:** ~50ms per test
**Key:** MockWebServer for realistic HTTP testing

```kotlin
class UserApiServiceTest {
    private lateinit var mockWebServer: MockWebServer
    private lateinit var apiService: UserApiService

    @Before
    fun setup() {
        mockWebServer = MockWebServer()
        apiService = Retrofit.Builder()
            .baseUrl(mockWebServer.url("/"))
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(UserApiService::class.java)
    }

    @After
    fun teardown() {
        mockWebServer.shutdown()
    }

    @Test
    fun getUsers_returnsUserList() = runTest {
        mockWebServer.enqueue(
            MockResponse()
                .setBody("""[{"id":1,"name":"Alice"}]""")
                .setResponseCode(200)
        )

        val users = apiService.getUsers()

        assertEquals(1, users.size)
        assertEquals("Alice", users[0].name)
    }

    @Test
    fun getUsers_serverError_throwsException() = runTest {
        mockWebServer.enqueue(MockResponse().setResponseCode(500))

        assertThrows(HttpException::class.java) {
            runBlocking { apiService.getUsers() }
        }
    }
}
```

## 6. UI Layer (Espresso / Compose)

**Location:** `app/src/androidTest/`
**Speed:** ~1s per test

### Espresso (View-based)

```kotlin
@RunWith(AndroidJUnit4::class)
class LoginScreenTest {
    @get:Rule
    val activityRule = ActivityScenarioRule(LoginActivity::class.java)

    @Test
    fun emptyEmail_showsError() {
        onView(withId(R.id.loginButton)).perform(click())
        onView(withId(R.id.emailError))
            .check(matches(withText("Email is required")))
    }

    @Test
    fun validLogin_navigatesToHome() {
        onView(withId(R.id.emailInput)).perform(typeText("user@test.com"))
        onView(withId(R.id.passwordInput)).perform(typeText("password123"))
        onView(withId(R.id.loginButton)).perform(click())

        onView(withId(R.id.homeScreen)).check(matches(isDisplayed()))
    }
}
```

### Compose Testing

```kotlin
class LoginScreenComposeTest {
    @get:Rule
    val composeRule = createComposeRule()

    @Test
    fun emptyEmail_showsError() {
        composeRule.setContent { LoginScreen() }

        composeRule.onNodeWithTag("loginButton").performClick()
        composeRule.onNodeWithText("Email is required").assertIsDisplayed()
    }
}
```

## TDD Order by Layer

When building a feature with TDD, work **inside-out**:

1. **Domain models** - Pure logic, fastest feedback
2. **Use cases** - Business rules
3. **Repository** - Data coordination
4. **ViewModel** - State management
5. **UI** - User interactions (last, fewest tests)
