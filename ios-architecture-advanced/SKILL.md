---
name: ios-architecture-advanced
description: Expert iOS app architecture patterns — dependency injection containers
  with scoped lifetimes, MVVM navigation via state enums, Redux/unidirectional data
  flow, Elements architecture, use case factory protocols, and Observer composition.
  Use when...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# iOS Architecture — Advanced

<!-- dual-compat-start -->
## Use When

- Expert iOS app architecture patterns — dependency injection containers with scoped lifetimes, MVVM navigation via state enums, Redux/unidirectional data flow, Elements architecture, use case factory protocols, and Observer composition. Use when...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ios-architecture-advanced` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Root Causes of Bad Codebases

Pattern selection matters less than application. Two root causes explain virtually all architectural failure:

1. **Highly interdependent code** — concrete type coupling, global state leakage
2. **Large types** — thousands-of-line objects that resist decomposition

Fix these two and almost any pattern works. Ignore them and no pattern saves you.

---

## 1. Dependency Injection with Scoped Containers

### Object Scopes — the Critical Insight

Scope determines *when* an object is created, how long it lives, and what it knows about.

| Scope | Lifetime | Canonical examples |
|-------|----------|--------------------|
| **App** | Launch → process death | Auth store, logger, analytics |
| **User** | Sign-in → sign-out | Remote APIs, user data stores |
| **Feature** | Feature entry → exit | Anything needing one captured value |
| **Interaction** | Gesture start → end | In-flight request cancellation tokens |

**User scope eliminates `Optional` unwrapping codebase-wide.** When user-specific objects live in an App-scoped singleton, every consumer must guard against `nil`. Move them to User scope — created at sign-in, destroyed at sign-out — and `UserSession` is always non-optional inside the scope.

### Container Hierarchy

Child containers request from parents; parents never request from children.

```swift
class AppDependencyContainer {
    // App-scoped singletons: logger, analytics, keychain
    let logger: Logger
    let analyticsService: AnalyticsService

    func makeUserDependencyContainer(userSession: UserSession)
        -> UserDependencyContainer {
        UserDependencyContainer(appContainer: self, userSession: userSession)
    }
}

class UserDependencyContainer {
    private let appContainer: AppDependencyContainer
    let userSession: UserSession  // captured immutably at sign-in

    init(appContainer: AppDependencyContainer, userSession: UserSession) {
        self.appContainer = appContainer
        self.userSession = userSession
        // No Optional unwrapping for userSession anywhere in user scope
    }

    func makePickMeUpContainer(pickupLocation: Location)
        -> PickMeUpDependencyContainer {
        PickMeUpDependencyContainer(userContainer: self,
                                    pickupLocation: pickupLocation)
    }
}

class PickMeUpDependencyContainer {
    private let userContainer: UserDependencyContainer
    let pickupLocation: Location  // mutable global → immutable feature value

    init(userContainer: UserDependencyContainer, pickupLocation: Location) {
        self.userContainer = userContainer
        self.pickupLocation = pickupLocation
        // pickupLocation can never change mid-feature; race conditions eliminated
    }
}
```

**Key insight**: Capturing a mutable global in a scope constructor converts it to an immutable constant for the feature's entire lifetime. Eliminates optionals *and* race conditions in one move.

### Use Case Factory Protocol (preferred over closures)

Closures passed as dependencies become unreadable at call sites. Factory protocols restore discoverability and enable autocomplete.

```swift
protocol SignInUseCaseFactory {
    func makeSignInUseCase(
        username: String,
        password: Secret,
        onStart: @escaping () -> Void,
        onComplete: @escaping (SignInUseCaseResult) -> Void
    ) -> UseCase
}

// The container already has a method with matching signature.
// Just declare conformance — no implementation needed.
extension OnboardingDependencyContainer: SignInUseCaseFactory {}

// ViewController receives the narrowest protocol, not the full container
class SignInViewController: UIViewController {
    let useCaseFactory: SignInUseCaseFactory

    func handleSignInTapped() {
        let useCase = useCaseFactory.makeSignInUseCase(
            username: usernameField.text ?? "",
            password: Secret(passwordField.text ?? ""),
            onStart: { [weak self] in self?.showLoading() },
            onComplete: { [weak self] result in self?.handle(result) }
        )
        useCase.start()
    }
}
```

### Three DI Approaches (in complexity order)

1. **On-demand** — Consumer builds the full graph inline. Good for demos; breaks at scale.
2. **Factory class** — Stateless centralised resolution. Protocol return types let you swap implementations in one line.
3. **Container hierarchy** (recommended at scale) — Stateful, scoped, captures values at scope boundaries.

---

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
