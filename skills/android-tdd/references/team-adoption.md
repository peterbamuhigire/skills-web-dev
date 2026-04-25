# Team Adoption, Legacy Code & Troubleshooting

## Adopting TDD in Your Team

### Phase 1: Start Small (Weeks 1-2)

**Goal:** Build confidence with TDD on low-risk work.

- Pick a single new feature (not a bug fix in legacy code)
- Pair program: one experienced TDD practitioner + one learner
- Focus on domain/model layer tests first (easiest, fastest)
- Celebrate green tests - build positive associations

**Good first TDD targets:**
- Validators (email, phone, password rules)
- Calculators (pricing, discounts, tax)
- Formatters (date, currency, text)
- State machines (order status, workflow steps)

### Phase 2: Establish Standards (Weeks 3-4)

**Agree on conventions:**

| Standard | Example |
|----------|---------|
| Test naming | `methodName_condition_expectedResult` |
| Test structure | Given-When-Then sections |
| Test location | Mirror production package structure |
| Mock framework | Mockito-Kotlin for all mocking |
| Assertion library | JUnit + Truth for fluent assertions |

**Code review checklist for TDD:**
- Does the PR include tests for new behavior?
- Were tests written before implementation? (check commit history)
- Do tests cover happy path AND error cases?
- Are tests independent (no shared mutable state)?
- Are test names descriptive enough to serve as documentation?

### Phase 3: Scale Up (Months 2-3)

- Extend TDD to ViewModel and Repository layers
- Add integration tests for critical data flows
- Set up CI pipeline with test gates
- Track metrics (bug rate, test count, coverage trends)

### Phase 4: Full Integration (Months 3+)

- TDD is default for all new features
- UI tests for critical user journeys
- Coverage thresholds enforced in CI
- Regular test health reviews

## Handling Legacy Code

### Strategy: Characterization Tests First

Before modifying legacy code, write tests that document current behavior:

```kotlin
// Step 1: Write a test that captures CURRENT behavior (even if buggy)
@Test
fun legacyCalculateDiscount_existingBehavior() {
    val calculator = LegacyPriceCalculator()
    // Document what it actually does, not what it should do
    val result = calculator.calculateDiscount(100.0, "SAVE10")
    assertEquals(90.0, result, 0.01) // Captures current behavior
}
```

### The Strangler Pattern

Replace legacy code incrementally:

1. **Wrap:** Create a new interface around legacy code
2. **Test:** Write tests for the new interface
3. **Implement:** Build new implementation with TDD
4. **Switch:** Route traffic from legacy to new code
5. **Remove:** Delete legacy code when fully replaced

```kotlin
// Step 1: Interface wrapping legacy
interface PriceCalculator {
    fun calculateDiscount(price: Double, code: String): Double
}

// Step 2: Legacy adapter
class LegacyPriceAdapter(
    private val legacy: LegacyPriceCalculator
) : PriceCalculator {
    override fun calculateDiscount(price: Double, code: String): Double =
        legacy.calculateDiscount(price, code)
}

// Step 3: New TDD implementation
class ModernPriceCalculator : PriceCalculator {
    override fun calculateDiscount(price: Double, code: String): Double {
        // Built with TDD, fully tested
    }
}
```

### Refactoring Toward Testability

Common patterns to make legacy code testable:

**Extract dependencies to constructor:**
```kotlin
// Before (untestable)
class OrderService {
    private val api = RetrofitClient.create()
    private val db = DatabaseHelper.getInstance()
}

// After (testable)
class OrderService(
    private val api: OrderApi,
    private val db: OrderDao
)
```

**Extract method for overriding:**
```kotlin
// Before
class ReportGenerator {
    fun generate() {
        val now = System.currentTimeMillis() // Hard to test
    }
}

// After
class ReportGenerator(private val clock: Clock = Clock.systemUTC()) {
    fun generate() {
        val now = clock.millis() // Mockable
    }
}
```

## Troubleshooting Common Issues

### Tests Are Slow

| Symptom | Cause | Fix |
|---------|-------|-----|
| Suite takes >30s | Too many instrumented tests | Move logic tests to `test/` (JUnit only) |
| Individual test >1s | Real network/DB calls | Mock external dependencies |
| CI takes >10min | Running everything serially | Parallelize unit and instrumented tests |

**Quick wins:**
```kotlin
// Use UnconfinedTestDispatcher for instant coroutine execution
@get:Rule
val coroutineRule = MainCoroutineRule(UnconfinedTestDispatcher())

// Use in-memory database (no disk I/O)
Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java)
    .allowMainThreadQueries()
    .build()
```

### Tests Are Flaky

| Symptom | Cause | Fix |
|---------|-------|-----|
| Pass/fail randomly | Shared mutable state | Reset state in `@Before` |
| Timing-dependent | Race conditions | Use `runTest` with `advanceUntilIdle()` |
| Order-dependent | Test A leaves data for test B | Each test creates its own data |
| UI test flaky | Animation timing | Disable animations, use `IdlingResource` |

**Espresso IdlingResource for async operations:**
```kotlin
class ApiIdlingResource : IdlingResource {
    private var callback: IdlingResource.ResourceCallback? = null
    private var isIdle = true

    override fun getName() = "ApiIdlingResource"
    override fun isIdleNow() = isIdle
    override fun registerIdleTransitionCallback(cb: ResourceCallback) {
        callback = cb
    }

    fun setIdle(idle: Boolean) {
        isIdle = idle
        if (idle) callback?.onTransitionToIdle()
    }
}
```

### High Test Maintenance

| Symptom | Cause | Fix |
|---------|-------|-----|
| Many tests break on small changes | Testing implementation details | Test behavior and public API only |
| Repetitive setup code | No test factories | Create `*Factory` objects |
| Brittle UI tests | Hardcoded text/positions | Use `testTag`, resource IDs |
| Tests hard to read | Poor naming, large tests | One concept per test, descriptive names |

### Common Error Messages

**`java.lang.RuntimeException: Method getMainLooper not mocked`**
```kotlin
// Add to test class
@get:Rule
val instantTaskExecutorRule = InstantTaskExecutorRule()
```

**`Module with the Main dispatcher had failed to initialize`**
```kotlin
// Add MainCoroutineRule
@get:Rule
val coroutineRule = MainCoroutineRule()
```

**`No tests found`**
- Check test is in correct source set (`test/` vs `androidTest/`)
- Ensure test method has `@Test` annotation
- Verify test class is not `private` or `abstract`

**`Cannot invoke real method on mock`**
```kotlin
// Use mockito-inline for final class mocking
testImplementation("org.mockito:mockito-inline:5.2.0")
```

## Measuring TDD Success

### Key Metrics

| Metric | Target | How to Track |
|--------|--------|-------------|
| Bug escape rate | Decreasing trend | Bug tracker (before/after TDD) |
| Test count | Growing with features | `./gradlew test` output |
| Coverage | >60% (domain), >40% (overall) | JaCoCo reports |
| Test speed | Unit suite <30s | CI timing |
| Flaky test rate | <2% | CI failure analysis |

### Signs TDD is Working

- Developers refactor confidently
- Bug reports decrease over time
- New team members onboard faster (tests as docs)
- Code reviews focus on design, not correctness
- Deployments cause fewer incidents

### Signs TDD Needs Adjustment

- Tests are frequently skipped or ignored
- Test maintenance consumes >30% of dev time
- Coverage is high but bugs persist (wrong things tested)
- Tests mirror implementation instead of behavior
- Team resents writing tests (process too rigid)
