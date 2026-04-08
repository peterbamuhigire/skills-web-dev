# Advanced TDD Patterns

Expert patterns from iOS TDD by Tutorials (RayWenderlich). Load when implementing:
- Testing system frameworks (CMPedometer, CLLocationManager, AVAudioSession)
- Async test patterns beyond basic XCTestExpectation
- Legacy code characterization and refactoring for testability
- Breaking circular dependencies through testing

## Table of Contents

1. [Test Doubles — Precise Hierarchy](#1-test-doubles--precise-hierarchy)
2. [Protocol Injection for System Frameworks](#2-protocol-injection-for-system-frameworks)
3. [Testing Dispatch Queue Behaviour](#3-testing-dispatch-queue-behaviour)
4. [XCTestExpectation — Expert Patterns](#4-xctestexpectation--expert-patterns)
5. [Facade Protocol for Hardware Frameworks](#5-facade-protocol-for-hardware-frameworks)
6. [ViewModel Testing with Mock Service](#6-viewmodel-testing-with-mock-service)
7. [XCTUnwrap — Replace Forced Unwrap in Tests](#7-xctunwrap--replace-forced-unwrap-in-tests)
8. [Legacy Code: Characterization Test Pattern](#8-legacy-code-characterization-test-pattern)
9. [Breaking Circular Dependencies](#9-breaking-circular-dependencies)
10. [Test Isolation Rules](#10-test-isolation-rules)
11. [Sprouting Methods for Legacy Code](#11-sprouting-methods-for-legacy-code)

---

## 1. Test Doubles — Precise Hierarchy

Five distinct types — not interchangeable terms:

| Type | What it does | iOS Example |
|---|---|---|
| **Stub** | Returns canned responses; minimum to compile | Returns hardcoded `TokenResponse` |
| **Fake** | Real logic on test data | `SimulatorPedometer` with `Timer` firing fake steps |
| **Mock** | Records calls for assertions | Sets `started = true` in `start()` |
| **Partial mock** | Subclasses production, overrides only what's tested | Overrides `getEvents()`, rest runs normally |
| **Spy** | Captures arguments for later assertion | `lastSent` captures encoded request body |

**Critical: Why not subclass URLSession**
`URLSession.init` is deprecated and key initializers are `public` not `open` — subclassing fails silently.
Always use protocol injection instead (see Section 2).

---

## 2. Protocol Injection for System Frameworks

When a system type cannot be subclassed, extract a narrow protocol and conform the real type via extension.

```swift
protocol URLSessionProtocol: AnyObject {
    func makeDataTask(with url: URL,
        completionHandler: @escaping (Data?, URLResponse?, Error?) -> Void)
        -> URLSessionTaskProtocol
}

protocol URLSessionTaskProtocol: AnyObject { func resume() }

// Conform real types in app target
extension URLSessionTask: URLSessionTaskProtocol {}
extension URLSession: URLSessionProtocol {
    func makeDataTask(with url: URL,
        completionHandler: @escaping (Data?, URLResponse?, Error?) -> Void)
        -> URLSessionTaskProtocol {
        return dataTask(with: url, completionHandler: completionHandler)
    }
}

// Mock for tests — Spy that captures last URL and completion handler
class MockURLSession: URLSessionProtocol {
    var lastURL: URL?
    var completionHandler: ((Data?, URLResponse?, Error?) -> Void)?

    func makeDataTask(with url: URL,
        completionHandler: @escaping (Data?, URLResponse?, Error?) -> Void)
        -> URLSessionTaskProtocol {
        self.lastURL = url
        self.completionHandler = completionHandler
        return MockURLSessionTask(completionHandler: completionHandler, url: url)
    }
}
```

**Rule:** Define the protocol with only what your app needs — not every method on the system type.

---

## 3. Testing Dispatch Queue Behaviour

You cannot check which `DispatchQueue` is current. Verify main queue by checking `Thread.current.isMainThread`.

```swift
func test_getDogs_dispatchesToMainQueue() {
    mockSession.givenDispatchQueue()  // session dispatches on background queue
    var thread: Thread!
    let exp = expectation(description: "completion called")
    sut.getDogs { _, _ in
        thread = Thread.current
        exp.fulfill()
    }
    mockSession.completionHandler?(validData, response200, nil)
    waitForExpectations(timeout: 0.1)
    XCTAssertTrue(thread.isMainThread)
}
```

**Trick: call `task.cancel()` to synchronously trigger completion without a real network call:**

```swift
func test_URLSession_conformance() {
    let exp = expectation(description: "completion called")
    let task = session.makeDataTask(with: url, completionHandler: { _, _, _ in
        exp.fulfill()
    }) as! URLSessionTask
    task.cancel()  // triggers completionHandler synchronously
    waitForExpectations(timeout: 0.2)
}
```

---

## 4. XCTestExpectation — Expert Patterns

### Inverted expectation — verify something does NOT happen

```swift
let exp = expectation(forNotification: MyNotification.name, object: sut)
exp.isInverted = true  // FAILS if notification fires; PASSES on timeout
wait(for: [exp], timeout: 1)
```

### Exact count + over-fulfill guard

```swift
let exp = XCTNSNotificationExpectation(name: MyNotification.name, object: sut)
exp.expectedFulfillmentCount = 1
exp.assertForOverFulfill = true  // fails immediately if fired more than once
```

### Ordered fulfillment for multi-step async flows

```swift
wait(for: [step1Exp, step2Exp, step3Exp], timeout: 2, enforceOrder: true)
// Perfect for OAuth flows, onboarding steps — verifies correct sequence
```

### Handler-filtered notifications — only count matching ones

```swift
let exp = expectation(forNotification: MyNotification.name, object: nil) { notification in
    return notification.userInfo?["type"] as? String == "milestone"
}
```

### NSPredicateExpectation for arbitrary state

```swift
let predicate = NSPredicate { model, _ in
    (model as? AppModel)?.isLoaded ?? false
}
let exp = expectation(for: predicate, evaluatedWith: sut)
wait(for: [exp], timeout: 2)
```

### Pass `line: UInt = #line` to test helpers

Failures attribute to the calling test, not the helper function:

```swift
func verifyDispatchesToMain(line: UInt = #line) {
    // ...
    XCTAssertTrue(thread.isMainThread, line: line)  // failure points to caller
}
```

---

## 5. Facade Protocol for Hardware Frameworks

Apply to: `CMPedometer`, `CLLocationManager`, `AVAudioSession` — anything requiring hardware or permissions.

```swift
// 1. Extract narrow facade protocol
protocol Pedometer {
    var isAvailable: Bool { get }
    func start(updates: @escaping (StepData?, Error?) -> Void)
    func stop()
}

// 2. Conform real type via extension in app target
extension CMPedometer: Pedometer {
    var isAvailable: Bool { CMPedometer.isStepCountingAvailable() }
    func start(updates: @escaping (StepData?, Error?) -> Void) {
        startUpdates(from: Date()) { data, error in
            updates(data.map { StepData(steps: $0.numberOfSteps.intValue) }, error)
        }
    }
}

// 3. Platform-conditional factory
static var pedometerFactory: () -> Pedometer = {
    #if targetEnvironment(simulator)
    return SimulatorPedometer()  // Fake with Timer for Simulator builds
    #else
    return CMPedometer()
    #endif
}

// 4. MockPedometer — dispatches on background queue to simulate real CMPedometer behavior
class MockPedometer: Pedometer {
    var started = false
    var dataBlock: ((StepData?, Error?) -> Void)?

    var isAvailable: Bool { true }

    func start(updates: @escaping (StepData?, Error?) -> Void) {
        started = true
        dataBlock = updates
        DispatchQueue.global().async { updates(nil, nil) }  // simulate async dispatch
    }

    func stop() {}

    // Spy method — inject fake data directly from test
    func sendStepData(_ data: StepData) { dataBlock?(data, nil) }
}
```

**Key insight:** `MockPedometer.start` dispatches on a background queue. This forces your production code to handle the dispatch correctly — tests that pass only on main queue will fail, revealing missing `DispatchQueue.main.async` wrappers.

---

## 6. ViewModel Testing with Mock Service

```swift
protocol DogService {
    func getDogs(completion: @escaping ([Dog]?, Error?) -> Void) -> URLSessionTaskProtocol
}

class MockDogService: DogService {
    var getDogsCallCount = 0
    var getDogsCompletion: (([Dog]?, Error?) -> Void)!
    lazy var getDogsDataTask = MockURLSessionTask()

    func getDogs(completion: @escaping ([Dog]?, Error?) -> Void) -> URLSessionTaskProtocol {
        getDogsCallCount += 1
        getDogsCompletion = completion
        return getDogsDataTask
    }
}
```

In tests, manually trigger the completion to control timing:

```swift
mockService.getDogsCompletion(mockDogs, nil)
XCTAssertEqual(sut.tableView.numberOfRows(inSection: 0), mockDogs.count)
XCTAssertTrue((sut.tableView as! MockTableView).calledReloadData)
```

**Inline partial mock for UITableView** — overrides only `reloadData`:

```swift
class MockTableView: UITableView {
    var calledReloadData = false
    override func reloadData() { calledReloadData = true }
}
sut.tableView = MockTableView()
```

---

## 7. XCTUnwrap — Replace Forced Unwrap in Tests

Forced unwrap in tests crashes the entire test run, masking subsequent failures.

```swift
// Instead of:
let error = result.error as NSError?
XCTAssertNotNil(error)
XCTAssertEqual(error!.domain, expected.domain)  // crashes entire suite if nil

// Use XCTUnwrap — throws test failure if nil, execution stops gracefully:
let error = try XCTUnwrap(result.error as NSError?)
XCTAssertEqual(error.domain, expected.domain)
```

Apply everywhere you would write `!` in test code.

---

## 8. Legacy Code: Characterization Test Pattern

Use when you must add tests to code you cannot yet safely refactor.

**Four steps:**
1. Call the code under test
2. Write an assertion you expect to fail
3. Let the failure reveal the actual current behavior
4. Update the assertion to match actual — you are documenting, not fixing

```swift
func test_loadEvents_getsData() {
    let predicate = NSPredicate { _, _ in !self.sut.events.isEmpty }
    let exp = expectation(for: predicate, evaluatedWith: sut)
    sut.loadEvents()
    wait(for: [exp], timeout: 2)
    // Step 3: print(sut.events) — inspect actual values
    // Step 4: encode them as assertions to lock in current behavior
    XCTAssertEqual(sut.events.count, 3)  // whatever the run revealed
}
```

**Stabilize with a partial mock** — subclass and inject to replace the live API:

```swift
class MockAPI: API {
    var mockEvents: [Event] = []
    override func getEvents() {
        DispatchQueue.main.async { self.delegate?.eventsLoaded(self.mockEvents) }
    }
}
// VC must declare: var api: API = AppDelegate.shared.api
sut.api = MockAPI()
```

Property injection (a `var` reference on the VC) is the minimum change required to the legacy class — no initializer surgery needed.

---

## 9. Breaking Circular Dependencies

### Pattern 1: Notification decoupling

Replace a direct back-reference (`api.logout()` calls `appDelegate.showLogin()`) with a notification:

```swift
func logout() {
    token = nil
    NotificationCenter.default.post(name: .userLoggedOut, object: nil)
}
// AppDelegate observes — no import of AppDelegate in API layer
```

### Pattern 2: Command pattern — injectable action

Replace back-reference with a closure or struct the parent builds and passes down:

```swift
struct SecondaryAction {
    let title: String
    let action: () -> Void
}
// Presenter builds the action; child VC holds no reference to parent type
```

### Pattern 3: Narrowing protocol scope

Replace a large delegate with a focused protocol covering only what the conformer needs:

```swift
// Before: LoginViewController: APIDelegate  (12 methods, most unused)
// After:
protocol LoginAPI {
    func login(username: String, password: String,
               completion: @escaping (Result<String, Error>) -> Void)
}
// LoginViewController conforms only to LoginAPI
// — no coupling to other model types in the API layer
```

---

## 10. Test Isolation Rules

| Rule | Detail |
|---|---|
| Clear singleton state in **both** `setUp` AND `tearDown` | Not one or the other — `setUp` handles creation, `tearDown` handles cleanup |
| Clear notification observers in `tearDown` | Stale observers from one test contaminate the next |
| Nil out closures holding `self` | `sut.stateChangedCallback = nil` in `tearDownWithError` prevents retain cycles across tests |
| Never rely on test execution order | Each test must pass in any order — XCTest does not guarantee order |
| Create `sut` in `setUp` with fresh injection targets | Never reuse a `sut` instance across multiple tests |

```swift
override func setUp() {
    super.setUp()
    sut = MyClass(service: MockService())
}

override func tearDown() {
    sut.completionBlock = nil  // break potential retain cycle
    NotificationCenter.default.removeObserver(sut!)
    sut = nil
    super.tearDown()
}
```

---

## 11. Sprouting Methods for Legacy Code

When a class is too risky to modify before a deadline, add new functionality in a separate extension file — zero lines of the original file are touched.

```swift
// API+Analytics.swift — API.swift is untouched
extension API: AnalyticsService {
    func sendReport(_ report: Report) throws {
        var request = URLRequest(url: analyticsURL)
        request.httpBody = try JSONEncoder().encode(report)
        sender.send(request: request)  // `sender` is a lazy var on API, injectable
    }
}
```

In tests, inject `MockSender` that captures the decoded request body (Spy pattern):

```swift
class MockSender: RequestSender {
    var lastRequest: URLRequest?
    func send(request: URLRequest) { lastRequest = request }
}
let mockSender = MockSender()
sut.sender = mockSender
try sut.sendReport(testReport)
let body = try JSONDecoder().decode(Report.self, from: mockSender.lastRequest!.httpBody!)
XCTAssertEqual(body.id, testReport.id)
```

**When to use:** tight deadline, high-risk legacy class, new feature that can be cleanly separated.
**When not to use:** the new code needs to modify existing behavior — sprouting only adds, it does not change.

---

See [architecture-testing.md](architecture-testing.md) for Observer element isolation and Use Case testing patterns.

*Source: iOS TDD by Tutorials — RayWenderlich*
