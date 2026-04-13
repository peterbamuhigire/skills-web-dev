---
name: ios-rbac
description: Role-Based Access Control for iOS apps integrating with a multi-tenant
  SaaS backend. Covers permission fetching, Keychain caching, SwiftUI permission gates
  (PermissionGate, ModuleGate), module-gated TabView, navigation guards, offline-capable...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---


## Platform Notes

- Claude Code: use Superpowers or similar helpers when they are available and materially useful.
- Codex: apply this skill normally; do not treat optional plugins as a prerequisite.

# iOS RBAC - Permission System

<!-- dual-compat-start -->
## Use When

- Role-Based Access Control for iOS apps integrating with a multi-tenant SaaS backend. Covers permission fetching, Keychain caching, SwiftUI permission gates (PermissionGate, ModuleGate), module-gated TabView, navigation guards, offline-capable...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ios-rbac` or would be better handled by a more specific companion skill.
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
## Architecture Overview

Mobile RBAC uses a **hybrid client+server** approach:

1. **Backend enforces** - Every API call checked by PermissionMiddleware (returns 403 if denied)
2. **Client gates UI** - Cached permissions control button/tab/screen visibility for UX
3. **Fail-secure** - If permissions unknown, deny access (never grant)
4. **Offline-capable** - Cached permissions work without network

**Backend Environments:** Dev (Windows/MySQL 8.4.7), Staging (Ubuntu/MySQL 8.x), Production (Debian/MySQL 8.x). Permission APIs must behave identically across all environments. Use Xcode build configurations and schemes for environment-specific base URLs.

```
Login → Fetch Permissions → Cache in Keychain → UI Gates
         ↕ (refresh)                              ↕ (403 fallback)
     Backend always enforces ←────────────────────┘
```

## Core Principles

### 1. Two-Layer Gating

| Layer               | What It Controls | When Hidden/Disabled                  |
| ------------------- | ---------------- | ------------------------------------- |
| **Module Gate**     | TabView tabs     | Franchise hasn't subscribed to module |
| **Permission Gate** | Views, buttons   | User's role lacks the permission      |

**Rule:** Modules HIDE tabs entirely. Permissions DISABLE or HIDE individual actions.

### 2. Permission Resolution (Backend)

Backend resolves permissions using 5-tier priority: User Denial → User Grant → Franchise Override → Role Permission → Super Admin/Owner. The iOS client **never resolves permissions locally**. It receives the resolved set from `GET /user/permissions` and uses it as-is.

### 3. Storage: Keychain Services

Permissions are a flat set of ~20-50 string codes. Stored securely in the Keychain.

```
"user_permissions"    → Set<String> {"POS_CREATE_SALE", "DASHBOARD_VIEW", ...}
"user_modules"        → Set<String> {"POS", "INVENTORY", ...}
"user_roles"          → Set<String> {"CASHIER", ...}
"user_type"           → String "staff"
"permissions_updated" → TimeInterval (epoch seconds)
```

**Never use UserDefaults for permissions.** Keychain data survives app reinstalls and is encrypted at rest by the OS.

### 4. Refresh Strategy

| Trigger              | Action                        |
| -------------------- | ----------------------------- |
| After login          | Fetch immediately             |
| App startup (cold)   | Fetch if > 15 min stale       |
| App foreground (warm) | Fetch if > 15 min stale      |
| 403 from backend     | Fetch immediately, then retry |
| Pull-to-refresh      | Fetch immediately             |

Use `ScenePhase` to detect app foreground transitions for staleness checks.

### 5. Offline Behaviour

- Use cached permissions (last known good)
- If no cache exists (fresh install), deny all
- Never allow more access offline than last sync granted

## PermissionManager (@Observable)

The central permission store, injected via `@Environment`:

```swift
import Observation

@Observable
class PermissionManager {
    private(set) var permissions: Set<String> = []
    private(set) var modules: Set<String> = []
    private(set) var roles: Set<String> = []
    private(set) var userType: String = ""
    private(set) var lastFetched: Date?

    private let apiClient: APIClient
    private let keychain: KeychainHelper

    var isStale: Bool {
        guard let lastFetched else { return true }
        return Date().timeIntervalSince(lastFetched) > 900 // 15 min
    }

    // MARK: - Checks

    func hasPermission(_ code: String) -> Bool {
        guard !isOwner && !isSuperAdmin else { return true }
        return permissions.contains(code)
    }

    func hasAnyPermission(_ codes: [String]) -> Bool {
        guard !isOwner && !isSuperAdmin else { return true }
        return codes.contains { permissions.contains($0) }
    }

    func hasAllPermissions(_ codes: [String]) -> Bool {
        guard !isOwner && !isSuperAdmin else { return true }
        return codes.allSatisfy { permissions.contains($0) }
    }

    func hasModule(_ code: String) -> Bool { modules.contains(code) }
    var isOwner: Bool { userType == "owner" }
    var isSuperAdmin: Bool { userType == "super_admin" }

    // MARK: - Fetch & Cache

    func fetchPermissions() async throws {
        let response = try await apiClient.get("/user/permissions")
        permissions = Set(response.data.permissions)
        modules = Set(response.data.modules
            .filter { $0.isEnabled }
            .map { $0.code })
        roles = Set(response.data.roles.map { $0.code })
        userType = response.data.userType
        lastFetched = Date()
        saveTokeychain()
    }

    func loadCached() {
        guard let data = keychain.read(key: "rbac_permissions") else { return }
        guard let cached = try? JSONDecoder().decode(CachedPermissions.self, from: data) else { return }
        permissions = cached.permissions
        modules = cached.modules
        roles = cached.roles
        userType = cached.userType
        lastFetched = cached.lastFetched
    }

    func clearAll() {
        permissions = []
        modules = []
        roles = []
        userType = ""
        lastFetched = nil
        keychain.delete(key: "rbac_permissions")
    }

    private func saveTokeychain() {
        let cached = CachedPermissions(
            permissions: permissions, modules: modules,
            roles: roles, userType: userType, lastFetched: lastFetched
        )
        guard let data = try? JSONEncoder().encode(cached) else { return }
        keychain.save(key: "rbac_permissions", data: data)
    }
}

struct CachedPermissions: Codable {
    let permissions: Set<String>
    let modules: Set<String>
    let roles: Set<String>
    let userType: String
    let lastFetched: Date?
}
```

**Owner and Super Admin bypass all permission checks.** Check `userType` first.

## UI Patterns

### Pattern 1: PermissionGate (ViewModifier — Show/Hide)

```swift
struct PermissionGateModifier: ViewModifier {
    let permission: String
    @Environment(PermissionManager.self) private var permissionManager

    func body(content: Content) -> some View {
        if permissionManager.hasPermission(permission) {
            content
        }
        // Hidden when no permission — no placeholder
    }
}

extension View {
    func requiresPermission(_ permission: String) -> some View {
        modifier(PermissionGateModifier(permission: permission))
    }
}
```

**Use for:** Buttons, cards, sections that should vanish when permission is absent.

```swift
Button("Create Purchase Order") { showCreatePO = true }
    .requiresPermission("INVENTORY_PO_CREATE")

Section("Credit Management") { ... }
    .requiresPermission("CREDIT_VIEW")
```

### Pattern 2: PermissionGate with Denied Content

```swift
struct PermissionGateView<Granted: View, Denied: View>: View {
    let permission: String
    @ViewBuilder let granted: () -> Granted
    @ViewBuilder let denied: () -> Denied
    @Environment(PermissionManager.self) private var permissionManager

    var body: some View {
        if permissionManager.hasPermission(permission) {
            granted()
        } else {
            denied()
        }
    }
}
```

```swift
PermissionGateView(permission: "INVENTORY_PO_APPROVE") {
    Button("Approve") { viewModel.approve() }
} denied: {
    Button("Approve") { }
        .disabled(true)
        .help("You don't have approval permission")
}
```

### Pattern 3: Module-Gated TabView

```swift
struct MainTabView: View {
    @Environment(PermissionManager.self) private var permissions

    var body: some View {
        TabView {
            NavigationStack { DashboardView() }
                .tabItem { Label("Home", systemImage: "house") }

            if permissions.hasModule("POS") {
                NavigationStack { SalesView() }
                    .tabItem { Label("Sales", systemImage: "cart") }
            }

            if permissions.hasModule("INVENTORY") {
                NavigationStack { InventoryView() }
                    .tabItem { Label("Inventory", systemImage: "shippingbox") }
            }

            if permissions.hasModule("REPORTS") {
                NavigationStack { ReportsView() }
                    .tabItem { Label("Reports", systemImage: "chart.bar") }
            }

            NavigationStack { SettingsView() }
                .tabItem { Label("Settings", systemImage: "gearshape") }
        }
    }
}
```

### Pattern 4: Navigation Guard

```swift
struct GuardedView<Content: View>: View {
    let permission: String
    @ViewBuilder let content: () -> Content
    @Environment(PermissionManager.self) private var permissionManager

    var body: some View {
        if permissionManager.hasPermission(permission) {
            content()
        } else {
            PermissionDeniedView(
                message: "You don't have access to this feature."
            )
        }
    }
}

// Usage in NavigationStack:
NavigationStack {
    List { ... }
        .navigationDestination(for: Route.self) { route in
            switch route {
            case .createPO:
                GuardedView(permission: "INVENTORY_PO_CREATE") {
                    CreatePurchaseOrderView()
                }
            }
        }
}
```

### Pattern 5: PermissionDeniedView

```swift
struct PermissionDeniedView: View {
    let message: String
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        ContentUnavailableView {
            Label("Access Denied", systemImage: "lock.fill")
        } description: {
            Text(message)
        } actions: {
            Button("Go Back") { dismiss() }
                .buttonStyle(.bordered)
        }
    }
}
```

## App Lifecycle Integration

### Foreground Staleness Check

```swift
@main
struct MyApp: App {
    @State private var permissionManager = PermissionManager(
        apiClient: APIClient.shared,
        keychain: KeychainHelper.shared
    )
    @Environment(\.scenePhase) private var scenePhase

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(permissionManager)
                .onChange(of: scenePhase) { _, newPhase in
                    if newPhase == .active && permissionManager.isStale {
                        Task { try? await permissionManager.fetchPermissions() }
                    }
                }
        }
    }
}
```

### App Startup

```swift
// In your root view or app delegate
.task {
    permissionManager.loadCached()
    if permissionManager.isStale {
        try? await permissionManager.fetchPermissions()
    }
}
```

## 403 Auto-Refresh

Handle 403 responses in your API client to trigger automatic permission refresh:

```swift
func handle403(requiredPermission: String?) async {
    // 1. Refresh permissions from backend
    try? await permissionManager.fetchPermissions()

    // 2. Check if permission now exists (admin may have just granted it)
    if let perm = requiredPermission,
       permissionManager.hasPermission(perm) {
        // Retry the original request
    } else {
        // Still denied — show user-friendly message
        showToast("Your permissions have been updated")
    }
}
```

### Backend Response Format

```json
{
    "success": true,
    "data": {
        "user_id": 10014, "franchise_id": 3, "user_type": "staff",
        "roles": [{"code": "CASHIER", "name": "Cashier"}],
        "permissions": ["DASHBOARD_VIEW", "POS_CREATE_SALE"],
        "modules": [{"code": "POS", "name": "Point of Sale", "is_enabled": true}]
    }
}
```

**403 error** includes `error.required_permission` for targeted refresh handling.

## Keychain Helper

Minimal wrapper for Keychain Services using `kSecClassGenericPassword`:

```swift
final class KeychainHelper {
    static let shared = KeychainHelper()

    func save(key: String, data: Data) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data
        ]
        SecItemDelete(query as CFDictionary)
        SecItemAdd(query as CFDictionary, nil)
    }

    func read(key: String) -> Data? { /* SecItemCopyMatching with kSecReturnData */ }
    func delete(key: String) { /* SecItemDelete by kSecAttrAccount */ }
}
```

## UX Guidelines

| Scenario                               | UX Pattern                     | Why                       |
| -------------------------------------- | ------------------------------ | ------------------------- |
| Tab the user can't access              | **Hide tab**                   | Clean nav, no confusion   |
| Button the user can't use              | **Disable + grey + help text** | User knows feature exists |
| Card/section user can't see            | **Hide**                       | Clean layout              |
| Screen via deep link without access    | **PermissionDeniedView**       | Graceful block            |
| 403 from server (stale cache)          | Auto-refresh perms, show toast | Transparent recovery      |
| Offline with cached perms              | Use cached perms normally      | Seamless offline          |
| Offline with no cached perms           | Deny all, show offline banner  | Fail-secure               |

## Security Rules

1. **Never trust client-only checks** - Backend ALWAYS validates permissions
2. **Keychain storage only** - Never use UserDefaults for permission data
3. **Clear on logout** - `permissionManager.clearAll()` in logout flow
4. **Franchise isolation** - Permissions scoped to franchise_id in JWT
5. **No permission codes in logs** - Don't log full permission sets
6. **Client permissions are for UI gating only** - Show/hide, never authorise

## Integration with Other Skills

```
dual-auth-rbac (backend) → Defines permission tables, resolution logic, middleware
      ↓
ios-rbac (THIS SKILL)    → iOS-specific permission caching, UI gates, offline
      ↓
SwiftUI patterns         → PermissionGate modifiers follow platform conventions
      ↓
mobile-rbac (Android)    → Equivalent Android implementation (sister skill)
```

## Anti-Patterns

| Don't                                       | Do Instead                                    |
| ------------------------------------------- | --------------------------------------------- |
| Resolve permissions locally from roles      | Fetch resolved set from backend               |
| Store permissions in UserDefaults            | Use Keychain Services                         |
| Check permissions only on client             | Backend MUST enforce (defence in depth)        |
| Grant access when offline with no cache      | Deny all (fail-secure)                        |
| Hardcode role names (`if role == "ADMIN"`)   | Check permission codes                        |
| Create separate permission check per screen  | Use reusable `.requiresPermission()` modifier |
| Hide buttons without explanation             | Show disabled state with help text            |
| Skip permission refresh after 403            | Auto-refresh and re-evaluate                  |
| Use @AppStorage for sensitive permission data | Use Keychain via KeychainHelper              |

## Implementation Checklist

- [ ] `PermissionManager` as `@Observable` with `@Environment` injection
- [ ] Keychain caching for offline access via `KeychainHelper`
- [ ] `.requiresPermission()` ViewModifier for button/view gating
- [ ] `PermissionGateView` for granted/denied content variants
- [ ] Module-gated `TabView` tabs
- [ ] `PermissionDeniedView` using `ContentUnavailableView`
- [ ] `GuardedView` for navigation-level permission checks
- [ ] 403 auto-refresh trigger in API client
- [ ] 15-minute staleness check via `ScenePhase` on app foreground
- [ ] Clear all permissions on logout
- [ ] Owner/Super Admin bypass in all permission checks
- [ ] Backend enforces every permission (client is UI-only)
