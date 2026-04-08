---
name: ios-development
description: iOS development standards for AI agent implementation. Swift-first, SwiftUI, MVVM + Clean Architecture, async/await, comprehensive security, testing, and performance patterns. Use when building or reviewing iOS applications, generating Swift...
---

## Required Plugins

**Superpowers plugin:** MUST be active for all work using this skill.

# iOS Development Standards

Production-grade iOS development standards for AI-assisted implementation. Swift-first with SwiftUI, following modern Apple platform best practices.

**Core Stack:** Swift 6.0+ | SwiftUI (default UI) | MVVM + Clean Architecture | Swift Concurrency
**Min Deployment:** iOS 17+ | **IDE:** Xcode 16+
**Compatibility:** Must run flawlessly on both the minimum deployment target AND the latest iOS release
**Reference App:** Apple's sample code gallery and WWDC sessions — canonical examples of modern SwiftUI patterns

## Backend Environments

iOS apps connect to a PHP/MySQL backend deployed across three environments:

| Environment | Base URL Pattern | Database | Notes |
|---|---|---|---|
| **Development** | `http://{LAN_IP}:{port}/DMS_web/api/` | MySQL 8.4.7 (Windows WAMP) | Use host machine LAN IP |
| **Staging** | `https://staging.{domain}/api/` | MySQL 8.x (Ubuntu VPS) | For QA and TestFlight |
| **Production** | `https://{domain}/api/` | MySQL 8.x (Debian VPS) | App Store release |

Configure base URLs using Xcode build configurations and `.xcconfig` files so each scheme targets the correct backend. All backends use `utf8mb4_unicode_ci` collation and MySQL 8.x.

## Swift Language Standards

- **Swift 6.0+** with strict concurrency checking enabled
- **Value types preferred** — use structs over classes unless reference semantics are required
- **Protocol-oriented programming** — define capabilities via protocols, implement with extensions
- **`async/await`** for all asynchronous work (NOT Combine for networking)
- **`Codable`** for all JSON/API models with `CodingKeys` for snake_case mapping
- **Guard-early-return** pattern — validate preconditions early, keep the happy path unindented
- **Access control:** `private` by default, expose only what's needed (`internal` or `public`)
- **No force unwrapping** in production code — use `guard let`, `if let`, or nil coalescing
- **Sealed hierarchies:** Use `enum` with associated values for UI state modeling
- **Extension functions** for utility code — extend existing types rather than creating utility classes

```swift
// UI State — sealed enum pattern (mirrors Kotlin sealed class)
enum DashboardState {
    case idle, loading
    case success(DashboardStats)
    case error(String)
}

// Codable with snake_case mapping
struct User: Codable, Identifiable {
    let id: Int
    let fullName: String
    let emailAddress: String
    enum CodingKeys: String, CodingKey {
        case id, fullName = "full_name", emailAddress = "email_address"
    }
}

// Guard-early-return
func process(order: Order?) throws -> Receipt {
    guard let order else { throw AppError.missingOrder }
    guard !order.items.isEmpty else { throw AppError.emptyOrder }
    return try generateReceipt(for: order)
}
```

## Architecture: MVVM + Clean Architecture

Three layers mapping 1:1 from Android:

```
Android                    iOS
────────────────────────────────────────────────
presentation/              Features/{Name}/Views/
  screens/                   {Name}View.swift
  viewmodels/                {Name}ViewModel.swift
domain/                    Features/{Name}/Models/
  model/                     {Model}.swift
  usecase/                   {UseCase}.swift
data/                      Core/Network/ + Core/Persistence/
  remote/                    APIClient.swift
  local/                     SwiftData models
  repository/                {Name}Repository.swift
```

### Layer Rules

1. **Presentation** depends on Domain only
2. **Domain** has no UIKit/SwiftUI dependencies (pure Swift)
3. **Data** implements Domain interfaces, handles API/persistence

## Project Structure

```
{AppName}/
├── App/
│   ├── {AppName}App.swift          # @main entry point
│   └── ContentView.swift           # Root navigation container
├── Core/
│   ├── Network/
│   │   ├── APIClient.swift         # URLSession + async/await
│   │   ├── APIError.swift          # Typed error enum
│   │   ├── APIEnvelope.swift       # Generic response wrapper
│   │   ├── AuthInterceptor.swift   # JWT token injection
│   │   └── TokenManager.swift      # Keychain-backed token storage
│   ├── Persistence/
│   │   └── SwiftData models
│   ├── Security/
│   │   └── KeychainHelper.swift    # Keychain Services wrapper
│   └── Utils/
│       ├── CurrencyUtils.swift
│       └── DateUtils.swift
├── Features/
│   ├── Auth/  (Views/, AuthViewModel, AuthService)
│   ├── Dashboard/  (Views/, DashboardViewModel, DashboardRepository)
│   ├── POS/
│   └── Reports/
├── Shared/
│   ├── Components/                 # Reusable UI components
│   ├── Extensions/                 # Swift type extensions
│   └── Theme/AppTheme.swift        # Colors, fonts, spacing tokens
├── Resources/Assets.xcassets
└── Tests/ (UnitTests/, UITests/)
```

## State Management (iOS 17+ — No Legacy Patterns)

Use the `@Observable` macro. Do NOT use `ObservableObject` + `@Published`.

```swift
// ViewModel — @Observable macro (NOT ObservableObject)
@Observable
class DashboardViewModel {
    private(set) var stats: DashboardStats?
    private(set) var isLoading = false
    private(set) var error: String?

    private let repository: DashboardRepository

    init(repository: DashboardRepository) {
        self.repository = repository
    }

    func loadStats() async {
        isLoading = true
        error = nil
        do {
            stats = try await repository.fetchStats()
        } catch {
            self.error = error.localizedDescription
        }
        isLoading = false
    }
}

// View — use @State for ViewModel, no @ObservedObject needed
struct DashboardView: View {
    @State private var viewModel = DashboardViewModel(repository: .live)

    var body: some View {
        Group {
            if viewModel.isLoading {
                ProgressView()
            } else if let stats = viewModel.stats {
                StatsContent(stats: stats)
            } else if let error = viewModel.error {
                ErrorView(message: error, retry: { Task { await viewModel.loadStats() } })
            }
        }
        .task { await viewModel.loadStats() }
    }
}
```

### Property Wrapper Decision Guide

| Wrapper | When | Example |
|---|---|---|
| `@State` | View-local value types + ViewModel | `@State private var viewModel = VM()` |
| `@Binding` | Child view needs parent's state | `@Binding var isPresented: Bool` |
| `@Environment(\.key)` | System values | `@Environment(\.dismiss) var dismiss` |
| `@Environment(Type.self)` | Injected @Observable objects | `@Environment(AuthService.self) var auth` |

**Never use:** `@ObservedObject`, `@StateObject`, `@EnvironmentObject` — these are pre-iOS 17 patterns.

## Networking Layer

```swift
actor APIClient {
    private let session: URLSession
    private let baseURL: String
    private let tokenManager: TokenManager

    init(baseURL: String, tokenManager: TokenManager, session: URLSession = .shared) {
        self.baseURL = baseURL
        self.tokenManager = tokenManager
        self.session = session
    }

    func request<T: Decodable>(
        _ endpoint: String,
        method: String = "GET",
        body: (any Encodable)? = nil
    ) async throws -> T {
        var request = URLRequest(url: URL(string: "\(baseURL)/\(endpoint)")!)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        if let token = await tokenManager.accessToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        if let body {
            let encoder = JSONEncoder()
            encoder.keyEncodingStrategy = .convertToSnakeCase
            request.httpBody = try encoder.encode(body)
        }

        let (data, response) = try await session.data(for: request)
        guard let http = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        switch http.statusCode {
        case 200...299:
            let decoder = JSONDecoder()
            decoder.keyDecodingStrategy = .convertFromSnakeCase
            return try decoder.decode(T.self, from: data)
        case 401: throw APIError.unauthorized
        case 403: throw APIError.forbidden
        case 422: throw APIError.validationFailed(data)
        default: throw APIError.serverError(http.statusCode)
        }
    }
}

enum APIError: Error, LocalizedError {
    case invalidResponse
    case unauthorized
    case forbidden
    case validationFailed(Data)
    case serverError(Int)

    var errorDescription: String? {
        switch self {
        case .invalidResponse: "Invalid server response"
        case .unauthorized: "Session expired. Please log in again."
        case .forbidden: "You do not have permission for this action."
        case .validationFailed: "Validation error"
        case .serverError(let code): "Server error (\(code))"
        }
    }
}
```

## Build Configuration (3 Environments)

Every iOS app MUST have exactly 3 build schemes. This is non-negotiable.

```
Xcode Schemes: Dev / Staging / Production
Each scheme uses a different .xcconfig file:

Dev.xcconfig:     API_BASE_URL = http://$(LAN_IP):8080/api
Staging.xcconfig: API_BASE_URL = https://staging.domain.com/api
Prod.xcconfig:    API_BASE_URL = https://domain.com/api
```

| Scheme | Purpose | Distribution | Optimised |
|---|---|---|---|
| **Dev** | Local development | Xcode direct install | No |
| **Staging** | QA / pre-production | TestFlight (internal) | Yes |
| **Production** | App Store release | TestFlight + App Store | Yes |

**Rules:**
1. **User must provide** staging and production API URLs per project
2. **Never hardcode API URLs** — read from `Info.plist` or `.xcconfig`
3. **Dev** always points to local dev server via LAN IP
4. **Staging** uses TestFlight internal testing for QA
5. **Production** requires App Store Connect review

## Security Standards

### Mandatory

- **Keychain Services** for tokens and credentials — NEVER `UserDefaults`
- **Certificate pinning** for production (via `URLSession` delegate or `Info.plist` pinning)
- **App Transport Security (ATS)** enabled — HTTPS only in staging/production
- **Biometric auth** via `LocalAuthentication` framework (Face ID / Touch ID)
- **No sensitive data in logs** — use `os.Logger` with appropriate levels
- **No hardcoded secrets** — use `.xcconfig` or build settings

### Keychain Helper Pattern

```swift
final class KeychainHelper {
    static let shared = KeychainHelper()

    func save(_ data: Data, for key: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key, kSecValueData as String: data
        ]
        SecItemDelete(query as CFDictionary)  // Remove existing before add
        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else { throw KeychainError.saveFailed(status) }
    }

    func read(for key: String) throws -> Data? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true, kSecMatchLimit as String: kSecMatchLimitOne
        ]
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        guard status == errSecSuccess else { return nil }
        return result as? Data
    }

    func delete(for key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword, kSecAttrAccount as String: key
        ]
        SecItemDelete(query as CFDictionary)
    }
}
```

## Testing Strategy

### Test Pyramid: 70% Unit / 20% Integration / 10% UI

| Layer | Framework | What to Test |
|---|---|---|
| **Unit** | Swift Testing (`@Test`) | ViewModels, Services, Repositories, Utils |
| **Integration** | XCTest | API client with mock server, SwiftData queries |
| **UI** | XCUITest | Critical user journeys (login, purchase, etc.) |

**Key rules:**
- Use **Swift Testing** (`@Test` macro) for all new unit tests
- `@Observable` ViewModels are testable without SwiftUI — just call methods and assert state
- Mock repositories via protocols — inject test doubles in ViewModel init
- Use `XCTest` for integration tests that need setup/teardown lifecycle

```swift
import Testing

@Test("Dashboard loads stats successfully")
func dashboardLoadsStats() async {
    let vm = DashboardViewModel(repository: MockDashboardRepository(stats: .sample))
    await vm.loadStats()
    #expect(vm.stats != nil)
    #expect(vm.isLoading == false)
    #expect(vm.error == nil)
}

@Test("Dashboard handles network error")
func dashboardHandlesError() async {
    let vm = DashboardViewModel(repository: MockDashboardRepository(error: .serverError(500)))
    await vm.loadStats()
    #expect(vm.stats == nil)
    #expect(vm.error != nil)
}
```

## Performance Rules

- **`LazyVStack`/`LazyHStack`** for all scrollable content — never plain `VStack` for dynamic lists
- **`.task {}`** for async work on view appear — auto-cancelled on disappear (never `.onAppear`)
- **`@State` as cache** for expensive computed objects
- **Preserve view identity** — use ternary not `if/else` for same content type
- **`.drawingGroup()`** for complex animated views (offloads to Metal)
- **Stable `id` in `ForEach`** — use model identity, never array index
- **Profile with Instruments** — Time Profiler, Allocations, SwiftUI view body evaluation

## Navigation (iOS 17+)

Use `NavigationStack` with type-safe navigation. Never use `NavigationView`.

```swift
enum AppRoute: Hashable {
    case dashboard, settings
    case orderDetail(orderId: Int)
}

struct ContentView: View {
    @State private var path = NavigationPath()
    var body: some View {
        NavigationStack(path: $path) {
            DashboardView()
                .navigationDestination(for: AppRoute.self) { route in
                    switch route {
                    case .dashboard: DashboardView()
                    case .orderDetail(let id): OrderDetailView(orderId: id)
                    case .settings: SettingsView()
                    }
                }
        }
    }
}
```

## Minimum Requirements

| Requirement | Value |
|---|---|
| **iOS Deployment Target** | 17.0+ |
| **Swift Version** | 6.0+ |
| **Xcode** | 16+ |
| **UI Framework** | SwiftUI-first (UIKit only via `UIViewRepresentable`) |
| **Concurrency** | `async/await` + actors (strict concurrency) |
| **Persistence** | SwiftData (Core Data only for migration) |
| **Observation** | `@Observable` macro (not `ObservableObject`) |

## Phase 1 Bootstrap (SaaS Apps)

Always start: JWT Auth + Dashboard + Empty Tabs. Proves the full vertical slice (SwiftUI → ViewModel → Repository → APIClient → PHP → MySQL), establishes reusable patterns, uncovers integration issues early. Delivers 30+ unit tests. See `mobile-saas-planning` for the full plan template.

## Custom PNG Icons (Required)

- Use custom PNG icons only; do not use SF Symbols or icon libraries
- Use `Image("icon_name")` from asset catalogue
- Maintain `PROJECT_ICONS.md` in the project root

Follow the `mobile-custom-icons` skill for naming, directory rules, and tracking.

## Report Tables (25+ Rows)

- Any report that can exceed 25 rows must render as a table, not cards
- Follow the `mobile-report-tables` skill for table-first patterns

## KMP Projects

If this is a **Kotlin Multiplatform** project, this skill governs the
`iosApp/` module (SwiftUI UI and platform integration). The `shared/` module
is governed by the `kmp-development` skill. The shared framework is consumed
as a regular iOS framework or via CocoaPods/SPM. Install SKIE for better
Swift interop with sealed classes and Flows. Use `kmp-tdd` for shared tests.

## Anti-Patterns

| Anti-Pattern | Correct Approach |
|---|---|
| `ObservableObject` + `@Published` | `@Observable` macro |
| `NavigationView` | `NavigationStack` |
| Combine for networking | `async/await` |
| Tokens in `UserDefaults` | Keychain Services |
| Blocking main thread with sync I/O | `async/await` on background |
| `.onAppear` for data loading | `.task {}` modifier |
| `@StateObject` / `@ObservedObject` | `@State` with `@Observable` |
| `@EnvironmentObject` | `@Environment(Type.self)` |
| Hardcoded colours/sizes | Design tokens in `AppTheme` |
| Business logic in Views | Move to ViewModel or UseCase |

## Accessibility (App Store Requirement)

All iOS apps submitted to the App Store must support VoiceOver and Dynamic Type.

**Dynamic Type** — use text styles, never hardcoded sizes:
```swift
// SwiftUI — always use named styles
Text("Invoice Total").font(.headline)
Text("Amount").font(.custom("Georgia", size: 17, relativeTo: .body))

// UIKit — always set adjustsFontForContentSizeCategory
label.font = UIFont.preferredFont(forTextStyle: .body)
label.adjustsFontForContentSizeCategory = true
label.numberOfLines = 0   // allow wrapping at large text sizes
```

**VoiceOver labels** — every meaningful image and icon-only button needs one:
```swift
Image("invoice_icon").accessibilityLabel("Invoice")
Image("bg_texture").accessibilityHidden(true)       // decorative
Button { share() } label: { Image(systemName: "square.and.arrow.up") }
    .accessibilityLabel("Share invoice")
    .accessibilityHint("Opens share sheet")
VStack { Text("Order #1042"); Text("UGX 85,000") }
    .accessibilityElement(children: .combine)       // reads as one element
```

See [references/accessibility.md](references/accessibility.md) for full patterns, UIKit equivalents, and the App Store approval checklist.

## Integration with Other Skills

| Skill | When to Use |
|---|---|
| `swiftui-pro-patterns` | Layout mechanics, identity, animation, performance |
| `mobile-saas-planning` | Planning documentation for SaaS companion apps |
| `mobile-custom-icons` | PNG icon standards (no SF Symbols) |
| `mobile-report-tables` | Table patterns for 25+ rows |
| `mobile-reports` | Report screens, data visualisation, export |
| `api-pagination` | Infinite scroll patterns |
| `dual-auth-rbac` | JWT authentication and RBAC |
| `form-ux-design` | Cross-platform form UX patterns |
