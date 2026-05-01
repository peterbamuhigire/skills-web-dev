# ios-architecture-advanced Deep Dive

This file contains the extended guidance moved out of [../SKILL.md](../SKILL.md) so the skill entrypoint stays under the repository size limit.

## Included Sections

- `2. Model-Driven Navigation`
- `3. Use Case Pattern`
- `4. Observer Element Pattern`
- `5. Redux / Unidirectional Data Flow`
- `6. Architecture Selection Guide`
- `7. Build Time as Architecture Concern`
- `Anti-Patterns`
- `Quick Decision Checklist`

## 2. Model-Driven Navigation

Navigation driven by state enums rather than imperative `present()`/`push()` calls. The model is the source of truth; the view layer responds.

### State Enum Navigation

```swift
public enum PickMeUpView: Equatable {
    case initial
    case selectDropoffLocation
    case selectRideOption
    case confirmRequest
    case sendingRideRequest
    case final
}

// ViewController: subscribe once, respond declaratively
viewModel.$view
    .receive(on: DispatchQueue.main)
    .sink { [weak self] view in self?.present(view) }
    .store(in: &cancellables)

func present(_ view: PickMeUpView) {
    switch view {
    case .initial:                presentInitial()
    case .selectDropoffLocation:  presentDropoffPicker()
    case .selectRideOption:       presentRideOptions()
    case .confirmRequest:         presentConfirmation()
    case .sendingRideRequest:     presentSending()
    case .final:                  presentCompletion()
    }
}
```

### NavigationAction Enum — Handling System Back

The OS-driven back swipe bypasses your state machine. Fix this with a wrapper enum that distinguishes *intent* from *confirmation*:

```swift
public enum NavigationAction<T: Equatable>: Equatable {
    case present(view: T)
    case presented(view: T)  // VC calls this after transition completes
}

// UINavigationControllerDelegate syncs state when user swipes back
func navigationController(_ nav: UINavigationController,
    didShow viewController: UIViewController, animated: Bool) {
    guard viewController is WelcomeViewController else { return }
    viewModel.uiPresented(onboardingView: .welcome)
}
```

### Container View Controllers

- Container VC owns child VC lifetimes and transitions
- Children never know about each other or the parent
- Factory protocols decouple child creation from concrete types:

```swift
protocol SignedInViewControllerFactory {
    func makePickMeUpViewController(pickupLocation: Location) -> PickMeUpViewController
}
// Container VC receives this protocol; it has no import of the feature module
```

---

## 3. Use Case Pattern

One use case = one user intention. Keeps ViewModels thin; use cases are independently testable.

```swift
protocol UseCase {
    func start()
}

class SignInUseCase: UseCase {
    // All dependencies are protocol types — substitutable in tests
    let username: String
    let password: Secret
    let remoteAPI: AuthRemoteAPI
    let dataStore: UserSessionDataStore
    let onStart: () -> Void
    let onComplete: (SignInUseCaseResult) -> Void

    func start() {
        assert(Thread.isMainThread)  // always started on main
        onStart()
        Task {
            do {
                let session = try await remoteAPI.signIn(
                    username: username, password: password)
                try await dataStore.save(userSession: session)
                await MainActor.run { onComplete(.success(session)) }
            } catch {
                await MainActor.run { onComplete(.failure(ErrorMessage(error))) }
            }
        }
    }
}
```

### Cancelable Use Cases

```swift
protocol Cancelable { func cancel() }
typealias CancelableUseCase = Cancelable & UseCase

class SearchDropoffLocationsUseCase: CancelableUseCase {
    private var cancelled = false

    func cancel() {
        assert(Thread.isMainThread)
        cancelled = true
    }

    func start() {
        assert(Thread.isMainThread)
        guard !cancelled else { return }
        Task {
            let results = try await api.search(query: query)
            guard !cancelled else { return }
            await MainActor.run { onComplete(results) }
        }
    }
}
```

### Three Result Delivery Patterns

| Pattern | Mechanism | Best with |
|---------|-----------|-----------|
| **Closure (bidirectional)** | `onComplete` callback | MVVM, simple flows |
| **Database unidirectional** | Writes to DB; observers react independently | Multi-screen observing same data |
| **Redux unidirectional** | Dispatches actions to store | Redux architecture |

---

## 4. Observer Element Pattern

Decouples ViewControllers from Combine/NotificationCenter internals.

```swift
protocol Observer {
    func startObserving()
    func stopObserving()
}

class ObserverForSignIn: Observer {
    weak var eventResponder: ObserverForSignInEventResponder? {
        willSet {
            if newValue == nil { stopObserving() }  // automatic cleanup
        }
    }
    private var cancellables = Set<AnyCancellable>()

    func startObserving() {
        // All Combine subscriptions live here; VC never sees Combine
    }

    func stopObserving() {
        cancellables.removeAll()
    }
}

protocol ObserverForSignInEventResponder: AnyObject {
    func received(newViewState: SignInViewState)
    func keyboardWillHide()
    func keyboardWillChangeFrame(keyboardEndFrame: CGRect)
}
```

### Observer Composition

A ViewController manages **one observer** regardless of how many are composed underneath:

```swift
class ObserverComposition: Observer {
    let observers: [Observer]
    func startObserving() { observers.forEach { $0.startObserving() } }
    func stopObserving()  { observers.forEach { $0.stopObserving() } }
}

// In the VC:
let observer = ObserverComposition(observers: [
    ObserverForSignIn(eventResponder: self),
    KeyboardObserver(eventResponder: self)
])
observer.startObserving()
```

### Reusable Keyboard Observer

```swift
class KeyboardObserver: Observer {
    // Owns all NSValue extraction from notification userInfo
    // EventResponder protocol with default no-op implementations via extension
    // (Swift alternative to @objc optional — no @objc protocol requirements)
}

extension KeyboardObserverEventResponder {
    func keyboardWillHide() {}
    func keyboardWillChangeFrame(keyboardEndFrame: CGRect) {}
}
```

---

## 5. Redux / Unidirectional Data Flow

### State as Enum Tree — Eliminate Impossible States

```swift
public enum AppRunningState: Equatable {
    case onboarding(OnboardingState)
    case signedIn(SignedInViewControllerState, UserSession)
    // A VC showing signed-in UI while unauthenticated is a compile error, not a runtime bug
}

public enum OnboardingState: Equatable {
    case welcoming
    case signingIn(SignInViewControllerState)
    case signingUp(SignUpViewControllerState)
}
```

### ScopedState — Prevent Stale Subscriptions After Re-Auth

```swift
public enum ScopedState<T: Equatable>: Equatable {
    case outOfScope
    case inScope(T)
}
// When a VC's state enum case transitions away (e.g. user signs out),
// the subscription completes with .outOfScope.
// The VC cannot accidentally receive another user's state on re-auth.
```

### Side Effect Persistence — Separate from Business Logic

```swift
class UserSessionStatePersister {
    init(store: Store) {
        store.publisher
            .dropFirst(1)         // skip initial emission — already on disk
            .removeDuplicates()
            .sink { [weak self] state in
                self?.handle(authState: state.authenticationState)
            }
            .store(in: &cancellables)
    }

    private func handle(authState: AuthenticationState) {
        switch authState {
        case .signedIn(let session): keychain.save(session)
        case .signedOut:             keychain.deleteSession()
        }
    }
}
```

### Action Dispatcher Abstraction

```swift
protocol ActionDispatcher {
    func dispatch(_ action: Action)
}
extension Store: ActionDispatcher {}

// ViewModels receive ActionDispatcher, not Store
// They can dispatch but cannot read state — keeps them honest
class SignInViewModel {
    let dispatcher: ActionDispatcher

    func handleSignInSuccess(session: UserSession) {
        dispatcher.dispatch(SignInAction.signInSucceeded(session: session))
    }
}
```

---

## 6. Architecture Selection Guide

| Criteria | MVVM | Redux | Elements |
|----------|------|-------|----------|
| Team familiarity | High | Medium | Low |
| Multi-platform (macOS/tvOS) | Yes — no UIKit in VM | Yes | Yes |
| Time-travel debugging | No | Yes | No |
| Incremental adoption | No — full rewrite | No — full rewrite | Yes — one element at a time |
| State consistency across multiple screens | Hard | Yes — single source of truth | Medium |
| Pure function reducers (simplest tests) | No | Yes | No |
| App-to-app state sharing | No | Yes — store is serialisable | No |

**Default to MVVM** unless you need time-travel debugging or have severe cross-screen state consistency problems. Redux pays its complexity cost only at significant scale.

---

## 7. Build Time as Architecture Concern

Swift compiles an entire module when any file changes (no header files). At scale this degrades CI from minutes to tens of minutes.

- Break features into **Swift modules** (`Package.swift` or Xcode targets) — unchanged modules are skipped entirely at compile time
- Module boundaries enforce loose coupling: `internal` types cannot leak across module lines
- One squad per module = clear ownership + fast local feedback loops
- **Bazel / Pants**: distributed build cache means zero-recompile builds when a colleague already compiled the same inputs

Treat compile time as a lagging indicator of architectural health. If a single-file change recompiles 40% of the app, coupling is too high.

---

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|-------------|--------------|-----|
| Injecting concrete types | Cannot substitute in tests; violates Open/Closed | Always inject protocol types |
| App-scoped singletons for user data | Stale data survives sign-out; Optional noise everywhere | Move user objects to User scope |
| VCs referencing sibling VCs | Tight coupling; order-of-presentation bugs | Container VC manages children; siblings are blind to each other |
| Dispatching Redux actions inside state subscriptions | Infinite dispatch loops | Side effects go in middleware/persisters, not in subscribers |
| Reducers reading sub-state from other reducers | Destroys modularity; creates ordering dependencies | Each reducer owns exactly its own slice |
| Feature scope objects outliving their feature | Memory leaks; stale closures capturing stale data | Use weak references; destroy container on feature exit |

---

## Quick Decision Checklist

- [ ] Does each dependency have a protocol type? (no concrete injection)
- [ ] Are user-session objects in User scope, not App scope?
- [ ] Does each feature scope capture its required values immutably at entry?
- [ ] Does each VC receive a factory protocol, not a full container?
- [ ] Do children VCs have zero knowledge of siblings?
- [ ] Does each use case represent exactly one user intention?
- [ ] Are Redux reducers pure functions with no side effects?
- [ ] Have you measured compile time? Is it growing with the codebase?
