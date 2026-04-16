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

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | iOS architecture decision record | Markdown doc per `skill-composition-standards/references/adr-template.md` covering DI container, navigation, and module boundaries | `docs/ios/adr-architecture-checkout.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
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

## Additional Guidance

Extended guidance for `ios-architecture-advanced` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `2. Model-Driven Navigation`
- `3. Use Case Pattern`
- `4. Observer Element Pattern`
- `5. Redux / Unidirectional Data Flow`
- `6. Architecture Selection Guide`
- `7. Build Time as Architecture Concern`
- `Anti-Patterns`
- `Quick Decision Checklist`
