# ios-tdd Deep Dive

This file contains the extended guidance moved out of [../SKILL.md](../SKILL.md) so the skill entrypoint stays under the repository size limit.

## Included Sections

- `The Red-Green-Refactor Cycle`
- `Test Pyramid (70/20/10)`
- `TDD Workflow for iOS Features`
- `Swift Testing Framework`
- `Protocol-Based Mocking`
- `Testing @Observable ViewModels`
- `URLProtocol for Network Mocking`
- `SwiftData / Core Data Testing`
- `XCUITest for Critical Flows`
- `Test Naming Convention`
- `Patterns and Anti-Patterns`
- `Integration with Other Skills`
- `CI Pipeline`
- `TDD Checklist`
- `References`
- `Advanced Patterns`

## The Red-Green-Refactor Cycle

```
1. RED    → Write a failing test for desired behavior
2. GREEN  → Write MINIMUM code to make it pass
3. REFACTOR → Clean up while keeping tests green
4. REPEAT → Next behavior
```

**Critical Rules:**

- Never skip the Red phase (verify the test actually fails)
- Never write more code than needed in Green phase
- Never refactor with failing tests
- Each cycle should take minutes, not hours

## Test Pyramid (70/20/10)

```
        /  UI  \        10% - XCUITest, end-to-end flows
       /--------\
      / Integra- \      20% - ViewModel+Repository, persistence, API
     /  tion      \
    /--------------\
   /   Unit Tests   \   70% - Pure Swift, fast, isolated
  /==================\
```

| Type            | Speed       | Scope                  | Target          | Tools                        |
| --------------- | ----------- | ---------------------- | --------------- | ---------------------------- |
| **Unit**        | <1ms each   | Single class/method    | App test target | Swift Testing, XCTest        |
| **Integration** | ~100ms each | Component interactions | App test target | Swift Testing, URLProtocol   |
| **UI**          | ~1s each    | User flows             | UI test target  | XCUITest                     |

## TDD Workflow for iOS Features

### Step 1: Define the Requirement

Start with a clear user story or acceptance criteria:

> _As a user, I want to add items to my cart so I can purchase them later._

### Step 2: Write the Failing Test (Red)

```swift
import Testing

@Test("Adding item to empty cart gives count of 1")
func addItemToCart_increasesCartCount() {
    let cart = ShoppingCart()
    cart.addItem(Product(name: "Phone", price: 999.99))
    #expect(cart.itemCount == 1)
}
```

Run it. It must fail (class doesn't exist yet).

### Step 3: Write Minimal Code (Green)

```swift
struct Product {
    let name: String
    let price: Double
}

class ShoppingCart {
    private var items: [Product] = []
    func addItem(_ product: Product) { items.append(product) }
    var itemCount: Int { items.count }
}
```

Run test. It passes. Stop writing code.

### Step 4: Add Next Test, Then Refactor

```swift
@Test("Multiple items calculates correct total")
func addMultipleItems_calculatesTotal() {
    let cart = ShoppingCart()
    cart.addItem(Product(name: "Phone", price: 999.99))
    cart.addItem(Product(name: "Case", price: 29.99))
    #expect(abs(cart.totalPrice - 1029.98) < 0.01)
}
```

Implement `totalPrice`, then refactor both test and production code.

## Swift Testing Framework

Swift Testing is the modern, preferred test framework for iOS (Xcode 16+). Use `@Test` macro and `#expect` macro instead of XCTest assertions.

### Basic Structure

```swift
import Testing

@Test("Description of expected behavior")
func descriptiveTestName() {
    // Arrange
    let sut = MyClass()

    // Act
    let result = sut.doSomething()

    // Assert
    #expect(result == expectedValue)
}
```

### Async Testing

```swift
@Test("Login with valid credentials returns tokens")
func loginSuccess() async throws {
    let mockAPI = MockAuthAPI(shouldSucceed: true)
    let viewModel = LoginViewModel(api: mockAPI)

    await viewModel.login(email: "test@example.com", password: "password")

    #expect(viewModel.isAuthenticated == true)
    #expect(viewModel.error == nil)
}

@Test("Login with invalid credentials shows error")
func loginFailure() async throws {
    let mockAPI = MockAuthAPI(shouldSucceed: false)
    let viewModel = LoginViewModel(api: mockAPI)

    await viewModel.login(email: "test@example.com", password: "wrong")

    #expect(viewModel.isAuthenticated == false)
    #expect(viewModel.error != nil)
}
```

### Parameterised Tests

```swift
@Test("Discount calculation for tiers", arguments: [
    (100.0, 0.0),   // No discount under threshold
    (500.0, 25.0),  // 5% discount
    (1000.0, 100.0) // 10% discount
])
func discountCalculation(price: Double, expectedDiscount: Double) {
    let discount = PricingEngine.calculateDiscount(for: price)
    #expect(abs(discount - expectedDiscount) < 0.01)
}
```

### Testing Errors

```swift
@Test("Withdraw more than balance throws insufficient funds")
func overdraftThrows() {
    let account = BankAccount(balance: 100)
    #expect(throws: BankError.insufficientFunds) {
        try account.withdraw(150)
    }
}
```

## Protocol-Based Mocking

iOS TDD uses **protocol-based dependency injection** — no mocking library needed. Define protocols for all external boundaries, then create lightweight mock conformances for tests.

### Define the Protocol

```swift
protocol AuthAPIProtocol {
    func login(email: String, password: String) async throws -> TokenResponse
    func refreshToken(_ token: String) async throws -> TokenResponse
}

// Production implementation
class AuthAPI: AuthAPIProtocol {
    func login(email: String, password: String) async throws -> TokenResponse { /* real call */ }
    func refreshToken(_ token: String) async throws -> TokenResponse { /* real call */ }
}
```

### Create the Mock

```swift
class MockAuthAPI: AuthAPIProtocol {
    var shouldSucceed: Bool
    var loginCallCount = 0
    init(shouldSucceed: Bool = true) { self.shouldSucceed = shouldSucceed }

    func login(email: String, password: String) async throws -> TokenResponse {
        loginCallCount += 1
        if shouldSucceed { return TokenResponse(access: "mock-token", refresh: "mock-refresh") }
        throw APIError.unauthorized
    }
    func refreshToken(_ token: String) async throws -> TokenResponse {
        if shouldSucceed { return TokenResponse(access: "new-token", refresh: "new-refresh") }
        throw APIError.tokenExpired
    }
}
```

### Inject via Initialiser

```swift
@Observable
class LoginViewModel {
    var isAuthenticated = false
    var error: Error?
    private let api: AuthAPIProtocol
    init(api: AuthAPIProtocol) { self.api = api }

    func login(email: String, password: String) async {
        do {
            _ = try await api.login(email: email, password: password)
            isAuthenticated = true
        } catch { self.error = error }
    }
}
```

## Testing @Observable ViewModels

`@Observable` ViewModels (iOS 17+) can be tested directly — no special framework needed. Property changes are immediate and synchronous after `await`.

```swift
@Test("Dashboard loads stats successfully")
func dashboardLoadsStats() async {
    let mockRepo = MockDashboardRepository(stats: .sample)
    let viewModel = DashboardViewModel(repository: mockRepo)

    await viewModel.loadStats()

    #expect(viewModel.stats != nil)
    #expect(viewModel.isLoading == false)
    #expect(viewModel.error == nil)
}

@Test("Dashboard handles load failure")
func dashboardLoadFailure() async {
    let mockRepo = MockDashboardRepository(shouldFail: true)
    let viewModel = DashboardViewModel(repository: mockRepo)

    await viewModel.loadStats()

    #expect(viewModel.stats == nil)
    #expect(viewModel.error != nil)
}
```

## URLProtocol for Network Mocking

Use `URLProtocol` subclass for integration tests that verify real networking code paths without hitting actual servers.

```swift
class MockURLProtocol: URLProtocol {
    static var requestHandler: ((URLRequest) throws -> (HTTPURLResponse, Data))?

    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }

    override func startLoading() {
        guard let handler = Self.requestHandler else {
            fatalError("No request handler set")
        }
        do {
            let (response, data) = try handler(request)
            client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
            client?.urlProtocol(self, didLoad: data)
            client?.urlProtocolDidFinishLoading(self)
        } catch {
            client?.urlProtocol(self, didFailWithError: error)
        }
    }

    override func stopLoading() {}
}
```

### Using in Tests

```swift
@Test("API service parses user response correctly")
func fetchUser() async throws {
    let config = URLSessionConfiguration.ephemeral
    config.protocolClasses = [MockURLProtocol.self]
    let session = URLSession(configuration: config)
    MockURLProtocol.requestHandler = { request in
        let json = #"{"id": 1, "name": "Alice"}"#.data(using: .utf8)!
        let response = HTTPURLResponse(
            url: request.url!, statusCode: 200, httpVersion: nil, headerFields: nil)!
        return (response, json)
    }
    let service = APIService(session: session)
    let user = try await service.fetchUser(id: 1)
    #expect(user.name == "Alice")
    #expect(user.id == 1)
}
```

## SwiftData / Core Data Testing

```swift
@Test("Saving item persists to store")
func saveItem() throws {
    let config = ModelConfiguration(isStoredInMemoryOnly: true)
    let container = try ModelContainer(for: Item.self, configurations: config)
    let context = container.mainContext
    let item = Item(name: "Test Item", quantity: 5)
    context.insert(item)
    try context.save()
    let items = try context.fetch(FetchDescriptor<Item>())
    #expect(items.count == 1)
    #expect(items.first?.name == "Test Item")
}
```

## XCUITest for Critical Flows

Use XCUITest **only** for critical user journeys: login, main navigation, purchase flows. Keep UI tests minimal (10% of suite).

```swift
final class LoginUITests: XCTestCase {
    let app = XCUIApplication()

    override func setUpWithError() throws {
        continueAfterFailure = false
        app.launchArguments = ["--uitesting"]
        app.launch()
    }

    func test_loginFlow_validCredentials_showsDashboard() {
        app.textFields["Email"].tap()
        app.textFields["Email"].typeText("test@example.com")
        app.secureTextFields["Password"].tap()
        app.secureTextFields["Password"].typeText("password123")
        app.buttons["Sign In"].tap()
        XCTAssertTrue(app.tabBars.firstMatch.waitForExistence(timeout: 5))
    }

    func test_loginFlow_invalidCredentials_showsError() {
        app.textFields["Email"].tap()
        app.textFields["Email"].typeText("test@example.com")
        app.secureTextFields["Password"].tap()
        app.secureTextFields["Password"].typeText("wrong")
        app.buttons["Sign In"].tap()
        XCTAssertTrue(app.staticTexts["Invalid credentials"].waitForExistence(timeout: 3))
    }
}
```

## Test Naming Convention

**Swift Testing (preferred):** Use the `@Test` description string for human-readable names.

```swift
@Test("Adding duplicate item increases quantity instead of duplicating")
func addDuplicateItem() { ... }
```

**XCTest (UI tests):** Use `test_methodUnderTest_condition_expectedResult` pattern.

```swift
func test_checkout_emptyCart_showsEmptyState() { ... }
func test_addToCart_fromProductDetail_updatesCartBadge() { ... }
func test_login_validCredentials_navigatesToDashboard() { ... }
```

## Patterns and Anti-Patterns

### DO

- Write tests first (always Red before Green)
- Keep tests small and focused (one assertion per concept)
- Use descriptive test names that document behavior
- Use test data factories for complex objects
- Test edge cases and error conditions
- Refactor tests alongside production code
- Prefer Swift Testing over XCTest for new tests
- Use protocol-based injection for every external dependency

### DON'T

- Test implementation details (test behavior, not internals)
- Test SwiftUI view body directly (test the ViewModel instead)
- Test Apple frameworks (URLSession, SwiftData internals)
- Chase 100% coverage at expense of test quality
- Write slow, flaky, or order-dependent tests
- Skip the Red phase (you won't catch false positives)
- Use third-party mocking libraries (protocols are sufficient)
- Put business logic in Views (untestable — keep Views thin)

## Integration with Other Skills

```
feature-planning → Define specs & acceptance criteria
      ↓
ios-tdd → Write tests first, then implement (THIS SKILL)
      ↓
[ios-development] → Follow MVVM + Swift architecture standards
      ↓
ai-error-handling → Validate AI-generated implementations
      ↓
vibe-security-skill → Security review
```

**Key Integrations:** feature-planning (acceptance criteria as test scenarios), ai-error-handling (validate AI output), ux-psychology/laws-of-ux (inform UI test scenarios).

## CI Pipeline

### GitHub Actions

```yaml
name: iOS TDD
on: [push, pull_request]
jobs:
  test:
    runs-on: macos-15
    steps:
      - uses: actions/checkout@v4
      - name: Select Xcode
        run: sudo xcode-select -s /Applications/Xcode_16.app
      - name: Unit & Integration Tests
        run: |
          xcodebuild test \
            -scheme MyApp \
            -destination 'platform=iOS Simulator,name=iPhone 16' \
            -resultBundlePath TestResults.xcresult
      - name: Upload Results
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: TestResults.xcresult
```

### Xcode Cloud

Configure via **Product > Xcode Cloud > Create Workflow**: trigger on PR/push to main, run all tests, notify on failure.

**CI Rules:** All tests pass before merge. 70% coverage for ViewModels, 50% overall. Unit and UI tests run as separate schemes for parallelism.

## TDD Checklist

- [ ] Write test BEFORE implementation (Red-Green-Refactor)
- [ ] Use Swift Testing (`@Test`) for new unit and integration tests
- [ ] Use XCTest only for UI tests (XCUITest)
- [ ] Protocol-based dependency injection for all external dependencies
- [ ] Mock APIs with protocol conformance (no mocking library)
- [ ] Test `@Observable` ViewModels directly (no special framework needed)
- [ ] `URLProtocol` for network mocking in integration tests
- [ ] In-memory `ModelContainer` for SwiftData tests
- [ ] XCUITest for login, main navigation, critical purchase flows only
- [ ] 70/20/10 test pyramid ratio maintained
- [ ] Descriptive test names that document behavior
- [ ] No business logic in SwiftUI Views

## References

- **Swift Testing**: developer.apple.com/documentation/testing/definingtests
- **WWDC24 Swift Testing**: developer.apple.com/videos/play/wwdc2024/10179

## Advanced Patterns

For expert-level patterns see [references/advanced-tdd-patterns.md](references/advanced-tdd-patterns.md):
- Precise test double hierarchy (Stub/Fake/Mock/Partial Mock/Spy)
- Protocol injection for hardware frameworks (CMPedometer, CLLocationManager)
- XCTestExpectation: inverted, ordered, filtered, predicate-based
- Legacy code characterization tests + breaking circular dependencies
- Sprouting methods pattern for untouchable legacy code
