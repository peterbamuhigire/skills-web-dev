---
name: ios-swift-design-patterns
description: Swift-idiomatic design patterns for iOS — VC containment to eliminate Massive ViewController, hand-rolled MVVM Observable binding without RxSwift, delegation naming conventions, associative storage for extension properties, constrained protocol...
---

# iOS Swift Design Patterns

**Source:** Swift Design Patterns — Paul Hudson, Hacking with Swift
**Use when:** Designing iOS app architecture, refactoring large VCs, choosing communication patterns, inheritance vs composition decisions.

---

## SECTION 1: Eliminating Massive ViewController

Root cause: one VC conforming to 5+ protocols simultaneously. Four fixes:

### Fix 1: VC Containment (preferred for sub-screens)

```swift
@nonobjc extension UIViewController {
    func add(_ child: UIViewController, frame: CGRect? = nil) {
        addChild(child)
        if let frame = frame { child.view.frame = frame }
        view.addSubview(child.view)
        child.didMove(toParent: self)
    }

    func remove() {
        willMove(toParent: nil)
        view.removeFromSuperview()
        removeFromParent()
    }
}

class DashboardViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        let stats = StatsViewController()
        add(stats, frame: CGRect(x: 0, y: 0, width: view.bounds.width, height: 200))
    }
}
```

### Fix 2: Dedicated Delegate/DataSource Objects

```swift
class ContactsDataSource: NSObject, UITableViewDataSource {
    var contacts: [Contact] = []

    func tableView(_ tableView: UITableView,
                   numberOfRowsInSection section: Int) -> Int { contacts.count }

    func tableView(_ tableView: UITableView,
                   cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "Cell", for: indexPath)
        cell.textLabel?.text = contacts[indexPath.row].name
        return cell
    }
}

class ContactsViewController: UIViewController {
    private let dataSource = ContactsDataSource()
    @IBOutlet weak var tableView: UITableView!

    override func viewDidLoad() {
        super.viewDidLoad()
        tableView.dataSource = dataSource
    }
}
```

### Fix 3: Move Layout into UIView Subclasses

```swift
// Override loadView() — not viewDidLoad() — to set a custom view
class ProfileViewController: UIViewController {
    override func loadView() {
        view = ProfileView()        // all layout lives in ProfileView
    }
    var profileView: ProfileView { view as! ProfileView }
}
```

### Fix 4: Never Put Shared Resources in AppDelegate

Use a singleton hidden behind a protocol instead (see Section 6).

---

## SECTION 2: Hand-Rolled MVVM Binding (No RxSwift Required)

```swift
class Observable<T> {
    private var _value: T?
    var valueChanged: ((T?) -> ())?

    var value: T? {
        get { _value }
        set { _value = newValue; valueChanged?(_value) }
    }

    // Skips observer — prevents two-way binding loops
    func bindingChanged(to newValue: T) { _value = newValue }

    init(_ value: T) { _value = value }
}

class BoundTextField: UITextField {
    private var changedClosure: (() -> ())?

    func bind(to observable: Observable<String>) {
        addTarget(self, action: #selector(valueChanged), for: .editingChanged)
        changedClosure = { [weak self] in
            observable.bindingChanged(to: self?.text ?? "")
        }
        observable.valueChanged = { [weak self] newValue in
            self?.text = newValue
        }
    }

    @objc private func valueChanged() { changedClosure?() }
}

class UserViewModel {
    var name  = Observable("Peter")
    var email = Observable("peter@example.com")
}

// In ViewController — two-way bind text field
let viewModel = UserViewModel()
nameField.bind(to: viewModel.name)

// One-way: VM → UI label
viewModel.name.valueChanged = { [weak self] name in
    self?.nameLabel.text = name
}
```

**Why not KVO?** Requires `NSObject` + `@objc dynamic` — un-Swifty. Use `Observable<T>` or `@Published` + `Combine` instead.

---

## SECTION 3: Delegation — Correct Swift Naming

```swift
// Protocol: TypeDelegate (always AnyObject for weak support)
protocol CalendarDelegate: AnyObject {
    // Single param: func sourceShouldVerb(_ source: Source) -> Bool
    func calendarShouldChangeYear(_ calendar: Calendar) -> Bool

    // Multi-param: func source(_ source: Source, verbSubject param: Type)
    func calendar(_ calendar: Calendar, didSelect date: Date)
}

class Calendar {
    weak var delegate: CalendarDelegate?    // ALWAYS weak

    func selectDate(_ date: Date) {
        let shouldChange = delegate?.calendarShouldChangeYear(self) ?? true
        guard shouldChange else { return }
        delegate?.calendar(self, didSelect: date)
    }
}
```

**Rules:**
- Single delegate property → name it `delegate`
- Multiple → append context: `uiDelegate`, `navigationDelegate`
- Always `weak var delegate` — mark protocol `AnyObject` to enable it
- Pass `self` (sender) as first parameter in every delegate method
- Optional bool methods → nil-coalesce to a safe default

---

## SECTION 4: Stored Properties in Extensions (Associative Storage)

Extensions cannot store properties. Workaround via `objc_setAssociatedObject`:

```swift
private var associatedKey = "myKey"

extension UIView {
    var identifier: String? {
        get { objc_getAssociatedObject(self, &associatedKey) as? String }
        set { objc_setAssociatedObject(self, &associatedKey, newValue,
                                       .OBJC_ASSOCIATION_RETAIN_NONATOMIC) }
    }
}

someView.identifier = "header"
print(someView.identifier ?? "none")
```

**Association policies:**
- `.OBJC_ASSOCIATION_RETAIN_NONATOMIC` — objects (most common)
- `.OBJC_ASSOCIATION_COPY_NONATOMIC` — value types / strings
- `.OBJC_ASSOCIATION_ASSIGN` — weak refs (unsafe: no zeroing weak)

---

## SECTION 5: Protocol-Oriented Composition

```swift
// Vertical (inheritance) — fragile base class problem
class Animal  { func eat() {} }
class Dog: Animal { func bark() {} }
class GuideDog: Dog { func guide() {} }   // inherits everything — fragile

// Horizontal (POP) — compose only what's needed
protocol Eatable  { func eat() }
protocol Barkable { func bark() }
protocol Guidable { func guide() }

struct GuideDog: Eatable, Barkable, Guidable {
    func eat()   {}
    func bark()  {}
    func guide() {}
}
```

**Constrained extensions (the real POP power):**

```swift
extension Array where Element: Numeric {
    var total: Element { reduce(0, +) }
}
// More-constrained extension wins over less-constrained one
```

**Default implementations replace `@objc optional`:**

```swift
protocol KeyboardObserverDelegate: AnyObject {
    func keyboardWillShow(frame: CGRect)
    func keyboardWillHide()
}
extension KeyboardObserverDelegate {
    func keyboardWillShow(frame: CGRect) {}   // no-op default
    func keyboardWillHide() {}
}
// Conformers only implement what they care about — no crash on unimplemented methods
```

**`@objc` protocol limitation:** Cannot provide extension defaults, cannot be used with structs/enums. Prefer pure Swift protocols with extension defaults.

---

## SECTION 6: Singleton — Swifty Implementation

```swift
final class Analytics {
    static let shared = Analytics()    // lazy + thread-safe automatically
    private init() {}                  // prevent external instantiation
    func track(_ event: String) { /* ... */ }
}
```

**Hide singletons behind protocols** to decouple and enable testing:

```swift
protocol Trackable {
    func track(_ event: String)
}
extension Trackable {
    func track(_ event: String) { Analytics.shared.track(event) }
}

struct CheckoutViewController: Trackable {
    func purchase() {
        track("purchase_completed")    // never references Analytics.shared directly
    }
}
// In tests: conform a mock struct to Trackable and override track()
```

---

## SECTION 7: Initializer Patterns

**Preserve memberwise initializer when adding custom init:**

```swift
struct Person {
    var name: String
    var age: Int
}
extension Person {
    // Custom init in extension — preserves generated Person(name:age:)
    init(name: String) { self.name = name; self.age = 0 }
}
// Person(name:age:) still works — extension doesn't remove it
// Defining init in the struct body would remove memberwise init
```

**Override failable with nonfailable:**

```swift
class Animal {
    init?(species: String) { guard !species.isEmpty else { return nil } }
}
class Dog: Animal {
    override init(species: String) {
        super.init(species: species)!   // must force-unwrap when calling up
    }
}
```

---

## SECTION 8: Keypath Adapter Pattern

Keypaths make unrelated types with different property names work generically:

```swift
protocol Identifiable {
    associatedtype ID
    static var idKey: WritableKeyPath<Self, ID> { get }
}

struct Person: Identifiable {
    static let idKey = \Person.socialSecurityNumber
    var socialSecurityNumber: String
    var name: String
}

struct Book: Identifiable {
    static let idKey = \Book.isbn
    var isbn: String
    var title: String
}

func printID<T: Identifiable>(thing: T) {
    print(thing[keyPath: T.idKey])
}

printID(thing: person)   // prints SSN
printID(thing: book)     // prints ISBN
```

---

## SECTION 9: Safe Iterator with defer

```swift
struct FibonacciIterator: IteratorProtocol, Sequence {
    var previous = 0, current = 1

    mutating func next() -> Int? {
        defer {
            let next = previous + current
            previous = current
            current = next
        }
        return current   // captured BEFORE defer executes — this is the trick
    }
}

for fib in FibonacciIterator().prefix(10) {
    print(fib)   // 1, 1, 2, 3, 5, 8, 13, 21, 34, 55
}
```

**Key insight:** `defer` advances state after the return value is captured. Without `defer`, state advances before the return — the value would be one step ahead.

---

## SECTION 10: Responder Chain — Traversal + Custom Chain

```swift
// Walk UIKit responder chain to find parent VC from any view
extension UIView {
    func findViewController() -> UIViewController? {
        var responder: UIResponder? = self
        while let next = responder?.next {
            if let vc = next as? UIViewController { return vc }
            responder = next
        }
        return nil
    }
}

// Custom responder chain (Chain of Responsibility)
protocol Chainable: AnyObject {
    var nextHandler: Chainable? { get set }
    func handle(event: String) -> Bool
}

class LogHandler: Chainable {
    var nextHandler: Chainable?
    func handle(event: String) -> Bool {
        print("Log: \(event)")
        return nextHandler?.handle(event: event) ?? false
    }
}

class AuthHandler: Chainable {
    var nextHandler: Chainable?
    func handle(event: String) -> Bool {
        guard event != "unauthorized" else { return false }
        return nextHandler?.handle(event: event) ?? true
    }
}
```

---

## SECTION 11: Copy-on-Write Flyweight

Swift structs with COW make flyweight largely unnecessary. For classes sharing partial immutable data:

```swift
class VehicleBase {
    let manufacturer: String    // shared immutable — must be let
    let engineType: String
    init(manufacturer: String, engineType: String) {
        self.manufacturer = manufacturer
        self.engineType = engineType
    }
}

struct Vehicle {
    let base: VehicleBase       // shared via reference
    var color: String           // per-instance mutable data
    var licensePlate: String
}

let base = VehicleBase(manufacturer: "Toyota", engineType: "V6")
let car1 = Vehicle(base: base, color: "Red",  licensePlate: "AAA-001")
let car2 = Vehicle(base: base, color: "Blue", licensePlate: "BBB-002")
// base object shared — only struct overhead per Vehicle instance
```

`UIFont.systemFont(ofSize:)` returns the same instance for identical sizes — verify with `===`.

---

## SECTION 12: Swift Anti-Patterns

| Anti-Pattern | Why It's Wrong | Swift Alternative |
|---|---|---|
| Subclassing as default design | Tightest coupling; fragile base class problem | Protocol composition |
| One VC, 5+ protocol conformances | Massive ViewController | VC containment + dedicated objects |
| AppDelegate as global state | Impossible to test; accessed everywhere | Singleton behind protocol |
| `AnyObject` for heterogeneous collections | Implicit unwrapping; ObjC `id` danger | `Any` or define a protocol |
| `NSClassFromString()` in own code | Runtime dynamic creation; typos crash silently | Static type system |
| `@objc dynamic` KVO in Swift | Requires NSObject subclass; un-Swifty | `@Published` or `Observable<T>` |
| Global variable disguised as singleton | No initializer control; mutable by all | `private init()` + `static let shared` |
| Ravioli code | Over-abstraction into 100s of tiny classes | Abstract only what varies |
| Flyweight for Swift structs | COW already makes it free | Just use value types |
| `@objc` optional protocol methods | No protocol extension defaults possible | Protocol extension with default impl |

---

## Quick Decision Guide

| Scenario | Pattern |
|---|---|
| VC getting large | VC containment (Fix 1) or dedicated datasource (Fix 2) |
| UI ↔ ViewModel sync | `Observable<T>` binding or `@Published` + Combine |
| One-to-one callbacks | Delegation with `weak var delegate` |
| One-to-many events | `NotificationCenter` or `Combine` publishers |
| Shared service access | Singleton behind protocol |
| Adding data to `UIView` subclass | `objc_setAssociatedObject` in extension |
| Type hierarchy flexibility | Protocol composition over inheritance |
| Adapting different property names | Keypath adapter pattern |
