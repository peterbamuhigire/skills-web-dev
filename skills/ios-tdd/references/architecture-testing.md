# Architecture Pattern Testing

Testing patterns for the Observer element and Use Case patterns from `ios-architecture-advanced`. Load when testing ViewControllers that use Observer injection or Use Case objects.

---

## 1. Observer Element Isolation

When a ViewController uses the Observer element pattern, inject a no-op observer in tests so no Combine subscriptions or NotificationCenter observers fire during the test. Trigger events directly by calling `EventResponder` methods on the VC.

```swift
// No-op observer — implements Observer protocol but does nothing
class NullObserver: Observer {
    func startObserving() {}
    func stopObserving() {}
}

// In tests: inject NullObserver so no subscriptions interfere
func test_signIn_success_updatesState() {
    let vc = SignInViewController(
        observer: NullObserver(),        // ← no Combine, no NotificationCenter
        useCaseFactory: mockFactory
    )
    vc.loadViewIfNeeded()

    // Simulate the event directly — as if the observer received it
    vc.received(newViewState: .signedIn(session: .sample))

    XCTAssertEqual(vc.titleLabel.text, "Welcome")
}
```

**Rule:** `EventResponder` protocol methods should have default no-op implementations via protocol extension (not `@objc optional`). This lets test doubles implement only the methods under test.

```swift
// Default no-op implementations — conformers only override what they need
protocol SignInEventResponder: AnyObject {
    func received(newViewState: SignInViewState)
    func keyboardWillHide()
}

extension SignInEventResponder {
    func keyboardWillHide() {}  // default no-op
}
```

**Testing Observer composition:**
```swift
// Verify each observer's behavior independently — not via ObserverComposition
func test_keyboardObserver_notifiesResponder() {
    let responder = MockKeyboardResponder()
    let observer = KeyboardObserver(eventResponder: responder)
    observer.startObserving()

    NotificationCenter.default.post(
        name: UIResponder.keyboardWillHideNotification, object: nil)

    XCTAssertTrue(responder.didReceiveKeyboardHide)
    observer.stopObserving()
}
```

---

## 2. Use Case Testing

Use cases (one user task = one object) are the most testable layer. Zero UIKit dependencies, protocol dependencies injected via init. Always started on the main thread.

```swift
@Test("Sign in success saves session and calls onComplete")
func signInSuccess() async {
    var completedWith: SignInUseCaseResult?
    let fakeAPI = FakeAuthRemoteAPI(willSucceed: true)
    let fakeStore = FakeUserSessionDataStore()

    let useCase = SignInUseCase(
        username: "alice@example.com",
        password: Secret("secret"),
        remoteAPI: fakeAPI,
        dataStore: fakeStore,
        onStart: {},
        onComplete: { completedWith = $0 }
    )

    useCase.start()
    try await Task.sleep(for: .milliseconds(10))

    #expect(fakeStore.savedSession != nil)
    #expect(completedWith == .success(fakeStore.savedSession!))
}

@Test("Sign in failure does not save session")
func signInFailure() async {
    var completedWith: SignInUseCaseResult?

    let useCase = SignInUseCase(
        username: "alice@example.com",
        password: Secret("wrong"),
        remoteAPI: FakeAuthRemoteAPI(willSucceed: false),
        dataStore: FakeUserSessionDataStore(),
        onStart: {},
        onComplete: { completedWith = $0 }
    )

    useCase.start()
    try await Task.sleep(for: .milliseconds(10))

    if case .failure = completedWith { /* pass */ } else {
        Issue.record("Expected failure result")
    }
}
```

**Protocol-conforming fakes (no mocking framework needed):**

```swift
// Fake — implements real logic on test data
struct FakeAuthRemoteAPI: AuthRemoteAPI {
    let willSucceed: Bool

    func signIn(username: String, password: Secret) async throws -> UserSession {
        if willSucceed { return UserSession(token: "fake-token", userId: "1") }
        throw AuthError.invalidCredentials
    }
}

struct FakeUserSessionDataStore: UserSessionDataStore {
    private(set) var savedSession: UserSession?

    mutating func save(userSession: UserSession) async throws {
        savedSession = userSession
    }
}
```

**Key insight:** Use cases designed with zero UIKit dependencies test at unit test speed — no simulator, no `XCTestExpectation` latency. The whole `SignInUseCase` test suite can run in milliseconds.

**Cancelable use case testing:**

```swift
@Test("Cancelled use case does not call onComplete")
func cancellationPreventsCompletion() async {
    var completionCalled = false
    let useCase = SearchUseCase(
        query: "test",
        remoteAPI: SlowFakeAPI(delay: 0.5),
        onComplete: { _ in completionCalled = true }
    )

    useCase.start()
    useCase.cancel()
    try await Task.sleep(for: .milliseconds(600))

    #expect(completionCalled == false)
}
```

---

*Source: Advanced iOS App Architecture (Cacheaux & Berlin, Ray Wenderlich Press)*
