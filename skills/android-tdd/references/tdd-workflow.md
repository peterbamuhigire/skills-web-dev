# TDD Workflow: Red-Green-Refactor in Detail

## The Cycle

Every feature follows this strict sequence:

### Phase 1: RED (Write Failing Test)

**Purpose:** Define expected behavior before any implementation.

1. Identify the next small behavior to implement
2. Write a test that asserts that behavior
3. Run the test - confirm it **fails**
4. If it passes, the test is wrong or the behavior already exists

```kotlin
@Test
fun saveNewItem_addsItemToWishlist() {
    val viewModel = DetailViewModel()
    val wishlist = Wishlist("Friends", emptyList(), 1)

    viewModel.saveNewItem(wishlist, "Android Phone")

    assertEquals(listOf("Android Phone"), wishlist.items)
}
```

**Common mistakes in Red phase:**
- Writing too many tests at once
- Writing tests that are too large
- Not running the test to verify it fails
- Testing multiple behaviors in one test

### Phase 2: GREEN (Minimal Implementation)

**Purpose:** Make the test pass with the simplest possible code.

1. Write only enough code to make the failing test pass
2. Don't optimize, don't handle edge cases, don't refactor
3. Run the test - confirm it **passes**
4. Run ALL tests - confirm nothing else broke

```kotlin
class DetailViewModel {
    fun saveNewItem(wishlist: Wishlist, item: String) {
        wishlist.items = wishlist.items + item
    }
}
```

**Common mistakes in Green phase:**
- Writing more code than needed
- Adding error handling not required by a test
- Refactoring while implementing
- Skipping the "run all tests" step

### Phase 3: REFACTOR (Clean Up)

**Purpose:** Improve code quality without changing behavior.

1. Look for duplication, poor naming, or design issues
2. Apply SOLID principles and design patterns
3. Run ALL tests after every change
4. Stop when the code is clean

**What to refactor:**
- Remove duplication (DRY)
- Improve variable and method names
- Extract methods or classes
- Apply appropriate design patterns
- Simplify complex expressions

**What NOT to do:**
- Add new behavior (that needs a new test first)
- Change test assertions
- Skip running tests between changes

## Sizing Your TDD Steps

### Too Small (Tedious)

```kotlin
// Test 1: Cart class exists
// Test 2: Cart has addItem method
// Test 3: addItem accepts Product
```

### Just Right (Behavioral)

```kotlin
// Test 1: Adding item increases count
// Test 2: Adding items calculates total
// Test 3: Removing item decreases count
```

### Too Large (Risky)

```kotlin
// Test 1: Full checkout flow with payment and confirmation
```

**Rule of thumb:** Each test should take 1-5 minutes to make pass.

## Sample TDD Session

### Feature: User Login Validation

**Iteration 1:**
```kotlin
@Test
fun emptyEmail_returnsInvalidEmail() {
    val validator = LoginValidator()
    val result = validator.validate("", "password123")
    assertEquals(ValidationResult.INVALID_EMAIL, result)
}
```

Implementation:
```kotlin
class LoginValidator {
    fun validate(email: String, password: String): ValidationResult {
        if (email.isEmpty()) return ValidationResult.INVALID_EMAIL
        return ValidationResult.VALID
    }
}
```

**Iteration 2:**
```kotlin
@Test
fun malformedEmail_returnsInvalidEmail() {
    val validator = LoginValidator()
    val result = validator.validate("notanemail", "password123")
    assertEquals(ValidationResult.INVALID_EMAIL, result)
}
```

**Iteration 3:**
```kotlin
@Test
fun shortPassword_returnsInvalidPassword() {
    val validator = LoginValidator()
    val result = validator.validate("user@email.com", "123")
    assertEquals(ValidationResult.INVALID_PASSWORD, result)
}
```

**Iteration 4:**
```kotlin
@Test
fun validCredentials_returnsValid() {
    val validator = LoginValidator()
    val result = validator.validate("user@email.com", "password123")
    assertEquals(ValidationResult.VALID, result)
}
```

**Refactor:** Extract email regex, password rules, add constants.

## When to Break the Cycle

The only acceptable reasons to skip TDD:
- Spike/prototype code (thrown away after learning)
- Auto-generated code (Room DAOs, Hilt modules)
- Simple data classes with no logic
- Configuration files (XML, Gradle)

**Even then**, write tests afterward for critical paths.

## Test Structure: Given-When-Then

Organize every test with three clear sections:

```kotlin
@Test
fun fetchUsers_networkError_showsErrorState() {
    // Given: Repository that returns an error
    val repository = mock<UserRepository>()
    whenever(repository.getUsers()).thenReturn(Result.failure(IOException()))
    val viewModel = UserViewModel(repository)

    // When: ViewModel fetches users
    viewModel.fetchUsers()

    // Then: Error state is shown
    assertEquals(UiState.Error("Network error"), viewModel.uiState.value)
}
```

## Tracking TDD Discipline

Ask yourself after each cycle:
- Did I write the test BEFORE the code?
- Did I verify the test FAILED first?
- Did I write ONLY enough code to pass?
- Did I refactor with ALL tests green?
- Is each test focused on ONE behavior?
