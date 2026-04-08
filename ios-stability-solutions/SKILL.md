---
name: ios-stability-solutions
description: Crash-prevention and production stability patterns for iOS. Use when hardening an app, designing features for stability, or building a TDD safety net around critical business logic.
---

# iOS Stability Solutions Guide

Patterns for creating stable, crash-free iOS apps. Synthesised from
*iOS Developer Solutions Guide* (Narendar Singh Saini).

---

## 1. The Three Error Classes — Prevent Each Differently

The book classifies all iOS bugs into three classes with distinct prevention strategies:

### Class 1 — Syntax / Compile-time Errors
**Prevention:** Master the language. Gaps in Swift knowledge directly cause compile errors.
Key areas: functional operators (`map`, `filter`, `flatMap`, `reduce`, `compactMap`),
all initialiser types (designated, convenience, required, failable `init?`, throwable `init throws`),
property types (stored, lazy stored, computed, observers, wrappers), optional unwrapping
hierarchy, protocols, generics, async/await.

### Class 2 — Logical Errors (Silent, Dangerous)
**Prevention:** TDD. These compile and run but produce wrong output. They survive manual
QA. Users report them after release. Only unit test cases reliably catch them.

### Class 3 — Runtime Errors (Crashes, Business-Critical)
**Prevention:** Optional safety + throwable functions + do-catch coverage (see Section 2).

---

## 2. Optional Safety Hierarchy — Eliminate Force Unwrap

Never force-unwrap (`!`) in production paths. Use this hierarchy:

```swift
// LEVEL 1: if-let — for branching on presence
if let url = URL(string: userInput) {
    // url is safe here
} else {
    // handle nil path
}

// LEVEL 2: guard-let — for early exits (preferred in functions)
guard let url = URL(string: userInput) else {
    // handle and return/throw
    return
}
// url is available for the rest of the function scope

// LEVEL 3: nil-coalescing — for providing safe defaults
let url = URL(string: userInput) ?? URL(string: "https://fallback.com")!

// LEVEL 4: optional chaining — for nested optionals
if let city = person.address?.city {
    print(city)
}
// Never: person.address!.city! — double crash risk

// LEVEL 5: pattern matching on Optional enum
switch person {
case let p?: print(p)      // .some
case nil:   print("none")  // .none
}
```

**Key insight:** Optional is `enum Optional<Wrapped> { case none; case some(Wrapped) }`.
It is not magic — it is a type. Treating it as a type (switch, pattern match) removes
entire classes of unexpected crashes.

### Failable Initialisers — The Safe Constructor Pattern

```swift
// Declare with init? when construction can legitimately fail
init?(string: String) { ... }

// Usage — safe, never crashes
if let obj = MyType(string: rawInput) {
    // use obj
}
```

### Throwable Initialisers — When You Need Error Detail

```swift
enum ConstructionError: Error {
    case emptyInput
    case invalidFormat
}

init(string: String) throws {
    guard !string.isEmpty else { throw ConstructionError.emptyInput }
    guard isValid(string) else { throw ConstructionError.invalidFormat }
}

// Usage
do {
    let obj = try MyType(string: rawInput)
} catch ConstructionError.emptyInput {
    // specific recovery
} catch {
    // general recovery
}
```

**Many Apple APIs are throwable for this reason:** `JSONDecoder.decode`, `NSManagedObjectContext.save`,
`Data.write(toFile:options:)`, `AVAudioPlayer(contentsOf:)`. Always wrap in do-catch.

---

## 3. Throwable Functions for Error Propagation

Use enum-backed errors for readable, extensible error handling:

```swift
enum DivisionError: Error {
    case divisionByZero
    case overflow
    case negativeResult
}

func divide(_ a: Double, by b: Double) throws -> Double {
    guard b != 0 else { throw DivisionError.divisionByZero }
    let result = a / b
    guard result >= 0 else { throw DivisionError.negativeResult }
    return result
}

// Generic throwable — works across types
func divide<T: BinaryFloatingPoint>(_ a: T, by b: T) throws -> T {
    guard b != 0 else { throw DivisionError.divisionByZero }
    return a / b
}
```

**Anti-pattern:** Returning -1 or "" as sentinel error values — callers ignore them silently.
Throwable functions force callers to acknowledge failure paths.

---

## 4. Dependency Injection — The Core of Testable, Stable Code

Tight coupling causes instability: a change in one class causes unexpected breakage in
another. DI is the primary tool for decoupling.

### Constructor Injection (Preferred)
```swift
class ViewModel {
    private let network: NetworkProtocol
    private let storage: StorageProtocol

    init(network: NetworkProtocol, storage: StorageProtocol) {
        self.network = network
        self.storage = storage
    }
}

// Production
let vm = ViewModel(network: URLSessionNetwork(), storage: CoreDataStorage())

// Tests — swap in fakes with no code change
let vm = ViewModel(network: MockNetwork(), storage: MockStorage())
```

### Method Injection
```swift
func showParsedData(_ parser: ParserProtocol) {
    parser.doParsing()
}
// Caller decides JSON or XML — ViewModel is unchanged
```

### Property Injection (Use sparingly — optional dependencies only)
```swift
class ViewController {
    var analytics: AnalyticsProtocol?   // optional, inject after init
}
```

**Stability rule:** If a class creates its own dependencies internally with `let x = ConcreteType()`,
it is tightly coupled and cannot be tested in isolation. Every untestable class is a
future crash that test cases cannot catch.

---

## 5. SOLID Principles as Stability Rules

### Single Responsibility — One Reason to Change
Each module: Network, Persistence, Validation, Logger, Navigation, Style, Localisation —
must be isolated. A change to Persistence must not affect Network. Modules that mix
responsibilities have more reasons to break.

```swift
// WRONG — ViewController does networking AND parsing AND storage
class LoginViewController: UIViewController {
    func loginTapped() {
        let data = URLSession... // network
        let user = try? JSONDecoder()... // parse
        UserDefaults.standard.set(user.id, forKey: "userId") // store
    }
}

// RIGHT — isolated modules, each testable alone
class LoginViewController: UIViewController {
    let viewModel: LoginViewModel
    func loginTapped() { viewModel.login(email: email, password: password) }
}
```

### Open/Closed — Extend Without Modifying
Add new behaviours through protocols rather than modifying existing classes:
```swift
protocol Shape { var area: Double { get } }
struct Circle: Shape { var area: Double { return .pi * radius * radius } }
struct Triangle: Shape { var area: Double { return 0.5 * base * height } }

class AreaCalculator {
    func calculate(_ shape: Shape) -> Double { shape.area }
    // Never touched again as new shapes are added
}
```

### Interface Segregation — Small Protocols Prevent Forced Implementation
```swift
// Fat protocol — forces BrainGame to implement setNumberOfPlayers it does not need
protocol Game { func start(); func stop(); func pause(); func saveData(); func setNumberOfPlayers(_ n: Int) }

// Segregated — each class confirms only what it needs
protocol Playable    { func start(); func stop(); func pause() }
protocol Persistable { func saveData(); func restoreData() }
protocol Configurable{ func setNumberOfPlayers(_ n: Int) }

class BrainGame: Playable { /* only implements what it needs */ }
```

Forcing classes to implement methods they do not need creates dead code that fails silently.

---

## 6. TDD Safety Net — Red-Green-Refactor

Test-Driven Development creates a permanent safety net. Without it, every code change
risks undiscovered regression.

### The Cycle

```
1. RED   — Write a FAILING test for the behaviour you are about to write
2. GREEN — Write minimum code to make the test pass
3. REFACTOR — Improve code, run tests, confirm still green
4. REPEAT
```

### Test Double Hierarchy

| Type  | Purpose                                              |
|-------|------------------------------------------------------|
| Dummy | Placeholder — fills required parameters, unused      |
| Stub  | Returns pre-defined fake data to the SUT             |
| Spy   | Records how it was called, for assertion later        |
| Mock  | Defines expectations; fails test if not met          |
| Fake  | Real implementation but unsuitable for production     |

### What to Test — and What Not To

**Test:**
- Business logic (calculations, transformations, rule evaluation)
- Domain-specific operations (billing, discounts, interest, access control)
- State management logic

**Do not test:**
- Auto-generated code
- Third-party SDKs / frameworks
- Compiler warnings / errors
- 100% line coverage — focus on business logic, not every line

### Key Shortcuts
- `Cmd + U` — run all tests
- `G` — re-run previous test (critical for bug-fixing loops)
- Diamond icon next to test — run single test case

### Stability Proof
```swift
// The calculate() function has a subtle off-by-one bug:
func calculate(items: [Double]) -> Double {
    var total = 1.0  // BUG: should be 0.0
    for item in items { total += item }
    return total
}

// Without TDD: ships to production. Users see wrong totals.
// With TDD: test immediately fails with "Expected 600, got 601" — caught before commit
```

---

## 7. Architecture for Stability — MVVM Over Massive ViewController

Massive ViewControllers (MVC misuse) cause instability because:
- Multiple concerns in one file create multiple reasons to break
- Tight coupling prevents isolated testing
- Code conflicts in large ViewController files during team development cause merge bugs

### MVVM Isolation Model

```
Model      — Data structs, business logic, network, persistence
ViewModel  — Glue: formats model data for view, processes view input
ViewController — Owns view + ViewModel, routes user events to ViewModel
View       — UIView subclasses, XIB/Storyboard/SwiftUI — dumb, no logic
```

### ViewModel Rules for Stability
- Never import UIKit or SwiftUI in ViewModel
- ViewModel owns all business logic — makes it independently testable
- View layer is fully replaceable (UIKit → SwiftUI) with zero ViewModel changes

### Data Binding Options (Weakest to Strongest Decoupling)
1. Property observers (`didSet`) — simple, synchronous
2. Delegation — clear ownership, testable
3. Closures / completion handlers — async-safe
4. Combine framework — reactive, cancellable
5. KVO — legacy, Objective-C heritage
6. RxSwift — third-party FRP

Choose the simplest binding that meets your needs. Overcomplicated bindings introduce
their own bugs.

---

## 8. Over-Engineering as a Stability Risk

Applying all patterns everywhere creates instability: new developers cannot understand
the flow and make unsafe changes; deeply nested abstractions make stack traces unreadable.

| Project Size  | Risk               | Action                                    |
|---------------|--------------------|-------------------------------------------|
| Small / solo  | Over-engineering   | Keep MVC, direct objects, no DI unless needed |
| Medium / team | Massive controllers| Apply MVVM, isolate modules, use protocols|
| Large / scale | Coupling, testability | Full SOLID, DI containers, TDD required  |

---

## 9. UI Approach and Crash Surface Area

The UI creation approach affects runtime crash likelihood directly:

### XIB/Storyboard Crash Risks
- **IBOutlet not connected** — runtime crash on `nil` forced-unwrap of outlet
- **IBAction not connected** — silent failure (button does nothing) or crash
- **Merge conflicts in storyboard** — corrupted XML causes build failure or runtime crash
- **Reuse identifier mismatch** — `dequeueReusableCell` returns wrong type → crash

**Mitigation for XIB:**
- Use XIB for simple, fixed-position UIs only
- Multiple XIB files per screen prevent multi-developer merge conflicts
- Always verify IBOutlet connections before running

### Storyboard-Specific Risks
- Single storyboard + multiple developers = guaranteed merge conflicts
- Conflicts in storyboard XML are often unresolvable → revert and redo = regression risk
- **Rule:** Multiple storyboards (iOS 9.0+) or XIB per screen for teams

### Programmatic Code (Safest for Dynamic UI)
- No hidden connections to break at runtime
- Constraints set in code are explicit and auditable
- No merge conflicts on UI files between developers

### SwiftUI for Dynamic UI
- No IBOutlet/IBAction = eliminates that entire crash class
- Live preview catches layout errors before runtime
- iOS 13.0+ only — confirm minimum deployment target first

---

## 10. Framework Access Levels — Public API Hardening

Public API surface is attack surface. Minimise it:

```swift
// WRONG — exposes internals unnecessarily
public class EmailValidator {
    public var regexPattern: String     // should be private
    public var lastValidatedEmail: String  // internal detail, not public
    public init() {}
    public func isValid(_ email: String) -> Bool { ... }
}

// RIGHT — minimal public surface
public class EmailValidator {
    private let regexPattern = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"
    private var lastValidated: String = ""

    public init() {}   // Required: public init for external instantiation

    public func isValid(_ email: String) throws -> Bool { ... }
}
```

### Swift Access Levels for Framework Stability

| Level       | Accessible From                              |
|-------------|----------------------------------------------|
| `open`      | Anywhere, including subclassing outside module|
| `public`    | Anywhere, cannot subclass outside module     |
| `internal`  | Same module only (default)                   |
| `fileprivate`| Same file only                              |
| `private`   | Enclosing declaration only                   |

**Rule:** Default everything to `private`. Promote to `internal` or `public` only when
external access is explicitly required. Every unnecessary `public` member is a surface
that external code can call in unexpected ways.

---

## 11. Backend-Driven UI — Zero-Downtime Bug Mitigation

A UI bug in production normally requires: archive → TestFlight → App Store review →
user update (hours to days). SDUI breaks this cycle — change the JSON, UI updates instantly
with no new build.

### SDUI Stability Requirements

```swift
// Safe component protocol
protocol Component: Decodable {
    var uniqueId: String { get }
    func renderView() -> AnyView
}

// Unknown-component safety — nil not crash
final class AnyComponent: Decodable {
    let component: Component?
    required init(from decoder: Decoder) throws {
        do {
            let type = try container.decode(ComponentIdentifier.self, forKey: .identifier)
            self.component = try type.metatype.init(from: decoder)
        } catch { self.component = nil }
    }
}

// compactMap drops nils safely
self.components = try container.decode([AnyComponent].self, forKey: .components)
    .compactMap { $0.component }
```

**Rules:** Cache last-good JSON for offline use. Only works with SwiftUI or programmatic
code — not XIB or Storyboard.

---

## 12. DRY Principle — Prevent Inconsistency Bugs

Duplicate code creates inconsistency bugs: you fix one copy and miss the other.

```swift
// RIGHT — single source of truth, testable once, trusted everywhere
enum AppInfo {
    static var version: String {
        Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? ""
    }
    static var versionString: String { "Version \(version)" }
}
```

---

## 13. Bug Prevention Checklist

Before shipping any feature, verify:

- [ ] No force-unwraps (`!`) in non-test code
- [ ] All optional chains use `if let` / `guard let`
- [ ] All Apple throwable APIs wrapped in `do-catch`
- [ ] All injected dependencies use protocols, not concrete types
- [ ] Business logic in ViewModel/Model — not in ViewController
- [ ] Unit tests written for all business logic before or alongside feature
- [ ] No duplicate business logic across files (DRY)
- [ ] UI approach matches team skill level and dynamic/static nature of UI
- [ ] IBOutlet and IBAction connections verified (if using XIB/Storyboard)
- [ ] Single storyboard NOT used on a multi-developer project
- [ ] Framework public API minimised to only what callers need
- [ ] All access levels explicitly declared (nothing left at default `internal` by accident)
- [ ] SDUI components handle unknown type gracefully (nil, not crash)
- [ ] Offline state handled in SDUI (cached JSON fallback)
