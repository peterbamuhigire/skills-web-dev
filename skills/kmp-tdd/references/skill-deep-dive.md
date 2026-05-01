# kmp-tdd Deep Dive

This file contains the extended guidance moved out of [../SKILL.md](../SKILL.md) so the skill entrypoint stays under the repository size limit.

## Included Sections

- `Test Configuration`
- `Test Doubles: When to Use Each`
- `Unit Tests`
- `Integration Tests`
- `DI in Tests with Koin`
- `Running Tests`
- `Coverage with Kover`
- `Best Practices`
- `Anti-Patterns`

## Test Configuration

### Dependencies

```kotlin
// shared/build.gradle.kts
sourceSets {
    commonTest.dependencies {
        implementation(kotlin("test"))
        implementation(kotlin("test-annotations-common"))
        implementation(libs.kotlinx.coroutines.test)
        implementation(libs.turbine)
        implementation(libs.kotest.framework.engine)
        implementation(libs.ktor.client.mock)
        implementation(libs.koin.test)
        implementation(libs.mokkery)
        implementation(libs.kotlinx.resources.test)
    }
    val androidUnitTest by getting {
        dependencies {
            implementation(kotlin("test-junit"))
            implementation(libs.junit)
            implementation(libs.sqldelight.jvm.driver)
        }
    }
    iosTest.dependencies {
        // iOS-specific test dependencies if needed
    }
}
```

### Directory Structure

```text
shared/src/
  commonTest/
    kotlin/
      com/example/app/
        domain/usecase/       # Unit tests for use cases
        data/repository/      # Unit tests for repositories
        data/remote/          # Integration tests for Ktor
        data/local/           # Integration tests for SQLDelight
        testdoubles/          # Fakes, stubs, shared fixtures
    resources/
      characters.json         # Test fixture data
  androidUnitTest/
    kotlin/
      TestDriverFactory.kt    # JVM SQLite driver for tests
  iosTest/
    kotlin/
      TestDriverFactory.kt    # Native SQLite driver for tests
```

## Test Doubles: When to Use Each

### Fakes

Alternative implementations that work without external dependencies.
Use for data sources that would otherwise require a database or network.

```kotlin
class InMemoryUserLocalDataSource : UserLocalDataSource {
    private val users = MutableStateFlow<List<User>>(emptyList())

    override val all: Flow<List<User>> = users.asStateFlow()

    override suspend fun save(users: List<User>) {
        this.users.value = users
    }

    fun clear() { users.value = emptyList() }
}
```

### Stubs

Fakes with configurable return values for different test scenarios.

```kotlin
class StubUserRemoteDataSource(
    private val users: MutableList<UserDto> = mutableListOf()
) : UserRemoteDataSource {

    fun setUsers(data: List<UserDto>) {
        users.clear()
        users.addAll(data)
    }

    override suspend fun getUsers(): Result<List<UserDto>> =
        runCatching { users.toList() }
}
```

### Mocks (Mokkery)

Use Mokkery for interface mocking when you need to verify interactions.
Only mock interfaces coupled to external data sources.

```kotlin
import dev.mokkery.answering.returns
import dev.mokkery.everySuspend
import dev.mokkery.mock
import dev.mokkery.verifySuspend
import dev.mokkery.matcher.exactly

val remoteDataSource = mock<UserRemoteDataSource>()

// Configure behaviour
everySuspend { remoteDataSource.getUsers() } returns Result.success(testUsers)

// Verify interaction
verifySuspend(mode = exactly(1)) { remoteDataSource.getUsers() }
```

### Decision Guide

| Need | Use |
|---|---|
| Simple in-memory replacement | Fake |
| Configurable responses per test | Stub |
| Verify method was called / interaction | Mock (Mokkery) |
| Real library with test config | Integration test double |

## Unit Tests

### Testing Use Cases

The Subject Under Test (SUT) is the use case. Repository is the boundary.
Only create test doubles for components with external dependencies.

```kotlin
class RefreshUsersTest {
    private val remoteDataSource = StubUserRemoteDataSource()
    private val localDataSource = InMemoryUserLocalDataSource()
    private val repository = UserRepository(localDataSource, remoteDataSource)
    private val refreshUsers = RefreshUsersUseCase(repository)

    @AfterTest
    fun tearDown() {
        localDataSource.clear()
    }

    @Test
    fun `refreshing users updates local storage`() = runTest {
        // Given
        remoteDataSource.setUsers(testUserDtos)

        // When
        refreshUsers()

        // Then
        localDataSource.all.test {
            val result = awaitItem()
            assertEquals(true, result.isNotEmpty())
            assertEquals(testUserDtos.size, result.size)
        }
    }

    @Test
    fun `empty remote response clears local storage`() = runTest {
        // Given
        remoteDataSource.setUsers(emptyList())

        // When
        refreshUsers()

        // Then
        localDataSource.all.test {
            assertEquals(true, awaitItem().isEmpty())
        }
    }
}
```

### Testing with Mokkery

```kotlin
class GetUsersTest {
    private val remoteDataSource = mock<UserRemoteDataSource>()
    private val localDataSource = InMemoryUserLocalDataSource()
    private val repository = UserRepository(localDataSource, remoteDataSource)
    private val getUsers = GetUsersUseCase(repository)

    @Test
    fun `fetches users from remote and caches locally`() = runTest {
        // Given
        everySuspend {
            remoteDataSource.getUsers()
        } returns Result.success(testUserDtos)

        // When
        getUsers()

        // Then
        verifySuspend(mode = exactly(1)) {
            remoteDataSource.getUsers()
        }
        localDataSource.all.test {
            assertEquals(true, awaitItem().isNotEmpty())
        }
    }
}
```

### Testing Flows with Turbine

```kotlin
@Test
fun `user list emits updates when local data changes`() = runTest {
    localDataSource.all.test {
        // Initial state
        assertEquals(emptyList(), awaitItem())

        // Trigger update
        localDataSource.save(testUsers)

        // Verify emission
        val updated = awaitItem()
        assertEquals(testUsers.size, updated.size)

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Loading Test Fixtures from JSON

```kotlin
class JsonLoader {
    private val json = Json { ignoreUnknownKeys = true }

    fun load(file: String): String {
        val resource = Resource("src/commonTest/resources/$file")
        return resource.readText()
    }

    internal inline fun <reified T : Any> loadAs(file: String): T =
        json.decodeFromString(load(file))
}

// Usage in tests
private val testUsers = JsonLoader().loadAs<UsersResponse>("users.json").results
```

## Integration Tests

### Ktor MockEngine

Test your actual Ktor data source implementation against a mock HTTP engine.

```kotlin
// Test utilities
fun testKtorClient(mockClient: MockClient = MockClient()): HttpClient {
    val engine = MockEngine { request ->
        val response = mockClient.respond(request)
        respond(
            content = ByteReadChannel(response.content),
            status = response.status,
            headers = headersOf(HttpHeaders.ContentType, "application/json")
        )
    }
    return HttpClient(engine) {
        install(ContentNegotiation) {
            json(Json {
                prettyPrint = true
                isLenient = true
                ignoreUnknownKeys = true
            })
        }
    }
}

class MockClient {
    private var responseContent: String = ""
    private var responseStatus: HttpStatusCode = HttpStatusCode.OK

    fun setResponse(content: String, status: HttpStatusCode = HttpStatusCode.OK) {
        responseContent = content
        responseStatus = status
    }

    fun respond(request: HttpRequestData) = MockResponse(responseContent, responseStatus)
}
```

### SQLDelight In-Memory Drivers

Platform-specific test drivers for database integration tests:

```kotlin
// commonTest - expect declaration
expect fun testDbDriver(): SqlDriver

// androidUnitTest
actual fun testDbDriver(): SqlDriver =
    JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY).also {
        AppDatabase.Schema.create(it)
    }

// iosTest
actual fun testDbDriver(): SqlDriver =
    inMemoryDriver(AppDatabase.Schema)
```

```kotlin
// Full integration test with real SQLDelight + mock Ktor
class RefreshUsersIntegrationTest {
    private val jsonResponse = JsonLoader().load("users.json")
    private val mockClient = MockClient()
    private val ktorClient = testKtorClient(mockClient)
    private val remoteDataSource = KtorUserRemoteDataSource(ktorClient, "https://api.test")

    private val db = createDatabase(driver = testDbDriver())
    private val localDataSource = SQLDelightUserLocalDataSource(db)

    private val repository = UserRepository(localDataSource, remoteDataSource)
    private val refreshUsers = RefreshUsersUseCase(repository)

    @Test
    fun `full refresh pipeline persists to database`() = runTest {
        // Given
        mockClient.setResponse(jsonResponse, HttpStatusCode.OK)

        // When
        refreshUsers()

        // Then
        localDataSource.all.test {
            assertEquals(true, awaitItem().isNotEmpty())
        }
    }
}
```

## DI in Tests with Koin

Reduce boilerplate by using Koin to wire test dependencies:

```kotlin
val testPlatformModule = module {
    single<SqlDriver> { testDbDriver() }
    single<MockClient> { MockClient() }
    single<HttpClient> { testKtorClient(get()) }
}

class RefreshUsersKoinTest : KoinTest {
    private val mockClient: MockClient by inject()

    @BeforeTest
    fun setUp() {
        startKoin {
            modules(testPlatformModule, sharedModule)
        }
    }

    @AfterTest
    fun tearDown() { stopKoin() }

    @Test
    fun `refresh users via Koin-injected dependencies`() = runTest {
        // Given
        val useCase = get<RefreshUsersUseCase>()
        val localDataSource = get<UserLocalDataSource>()
        mockClient.setResponse(JsonLoader().load("users.json"))

        // When
        useCase()

        // Then
        localDataSource.all.test {
            assertEquals(true, awaitItem().isNotEmpty())
        }
    }
}
```

## Running Tests

### All Platforms

```bash
./gradlew :shared:allTests
```

### Specific Platform

```bash
./gradlew :shared:testDebugUnitTest     # Android JVM tests
./gradlew :shared:iosSimulatorArm64Test # iOS simulator tests
./gradlew :shared:iosX64Test            # iOS Intel simulator
```

### IDE Execution

Click the play button next to any `@Test` function. Select the target
platform from the dropdown (Android, iOS Simulator, etc.).

## Coverage with Kover

Kover measures test coverage for JVM/Android targets. Native (iOS) coverage
is not yet supported.

```kotlin
// shared/build.gradle.kts
plugins {
    id("org.jetbrains.kotlinx.kover") version "0.7.6"
}

koverReport {
    verify {
        rule("Minimum Line Coverage") {
            isEnabled = true
            bound {
                minValue = 80
                metric = MetricType.LINE
                aggregation = AggregationType.COVERED_PERCENTAGE
            }
        }
        rule("Branch Coverage") {
            isEnabled = true
            bound {
                minValue = 70
                metric = MetricType.BRANCH
            }
        }
    }
}
```

```bash
./gradlew :shared:koverHtmlReport    # Generate HTML report
./gradlew :shared:koverVerify        # Enforce coverage thresholds
```

## Best Practices

1. **Write tests in commonTest first** -- they run on all platforms
2. **Use fakes for local data sources** -- in-memory implementations are fast
3. **Use Mokkery only for external boundaries** -- don't mock domain classes
4. **Load fixtures from JSON files** -- mirrors real API responses
5. **Given-When-Then structure** -- consistent test readability
6. **One assertion focus per test** -- clear failure messages
7. **Run allTests before committing** -- catches platform-specific failures
8. **Object Mother pattern for test data** -- centralise fixture creation
9. **Clean up state in @AfterTest** -- prevent test contamination
10. **Platform-specific tests only when necessary** -- prefer commonTest

## Anti-Patterns

- Testing only on Android JVM and skipping iOS targets
- Mocking domain classes instead of infrastructure boundaries
- Hardcoding test data instead of loading from fixture files
- Skipping integration tests for Ktor and SQLDelight
- Using `Thread.sleep()` instead of Turbine's `test {}` for Flow testing
- Not running `./gradlew :shared:allTests` before commits
- Treating 100% coverage as the goal instead of meaningful behaviour coverage
