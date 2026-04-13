---
name: ios-project-setup
description: 'iOS project setup with Xcode: project structure, SPM dependencies, build
  schemes (Dev/Staging/Prod), xcconfig files, Info.plist configuration, code signing,
  provisioning profiles, and deployment preparation. Use when creating a new iOS project
  or...'
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# iOS Project Setup

<!-- dual-compat-start -->
## Use When

- iOS project setup with Xcode: project structure, SPM dependencies, build schemes (Dev/Staging/Prod), xcconfig files, Info.plist configuration, code signing, provisioning profiles, and deployment preparation. Use when creating a new iOS project or...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ios-project-setup` or would be better handled by a more specific companion skill.
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
> Xcode project configuration, build schemes, code signing, provisioning,
> and deployment preparation for SwiftUI apps.

## Companion Skills

| Skill | When to Load |
|-------|-------------|
| `android-development` | Cross-platform reference (equivalent Android patterns) |
| `multi-tenant-saas-architecture` | Backend API that the iOS app connects to |
| `vibe-security-skill` | Security baseline for API communication |
| `dual-auth-rbac` | Authentication and role-based access |
| `image-compression` | Client-side image handling before upload |
| `healthcare-ui-design` | Clinical-grade UI when building health apps |

---

## 1. Creating a New Project

**Xcode > File > New > Project > App**

| Setting | Value |
|---------|-------|
| Interface | SwiftUI |
| Language | Swift |
| Storage | SwiftData (if persistence needed) |
| Testing | Include Tests + Include UI Tests |
| Bundle ID | `com.{company}.{appname}` |
| Minimum deployment | iOS 17.0 |

**Bundle ID is permanent.** You cannot change it after shipping to the App Store.
Choose carefully: `com.companyname.appname` (lowercase, no special characters).

### Recommended Directory Structure

```
MyApp/
├── App/
│   ├── MyApp.swift              # @main entry point
│   └── RootView.swift           # Auth routing
├── Core/
│   ├── Network/
│   │   ├── APIClient.swift
│   │   ├── APIEndpoints.swift
│   │   └── NetworkMonitor.swift
│   ├── Auth/
│   │   ├── AuthService.swift
│   │   ├── KeychainHelper.swift
│   │   └── TokenManager.swift
│   ├── Storage/
│   │   └── ModelContainer+App.swift
│   └── Config/
│       └── AppEnvironment.swift
├── Features/
│   ├── Login/
│   ├── Dashboard/
│   ├── Sales/
│   └── Settings/
├── Shared/
│   ├── Components/
│   ├── Extensions/
│   ├── Models/
│   └── Utilities/
├── Resources/
│   ├── Assets.xcassets/
│   ├── Localizable.strings
│   └── Info.plist
├── Config/
│   ├── Dev.xcconfig
│   ├── Staging.xcconfig
│   └── Prod.xcconfig
├── Tests/
│   └── MyAppTests/
└── UITests/
    └── MyAppUITests/
```

---

## 2. Swift Package Manager Dependencies

**Philosophy:** Prefer Apple frameworks. Only add SPM packages when built-in
solutions are genuinely insufficient.

```swift
// Built-in — no packages needed:
// SwiftUI        — UI framework
// SwiftData      — persistence
// URLSession     — networking
// Keychain       — secure storage
// MapKit         — maps
// CoreLocation   — GPS
// AVFoundation   — camera
// PhotosUI       — photo picker

// Optional SPM packages (add only if justified):
// Kingfisher     — image loading/caching (if AsyncImage insufficient)
// KeychainAccess — simplified Keychain API (if raw Keychain too verbose)
```

**Adding a package:** File > Add Package Dependencies > paste repository URL.

**Do NOT add packages for:**

- JSON parsing (Codable is built-in)
- Networking wrappers (URLSession + async/await is sufficient)
- UI component libraries (build your own with SwiftUI)
- Analytics (use Apple's App Analytics first)

---

## 3. Build Schemes and xcconfig Files

Create three `.xcconfig` files in the `Config/` directory at project root.

### Dev.xcconfig

```
// Dev.xcconfig
API_BASE_URL = http:\/\/$(LAN_IP):8080/$(PROJECT_NAME)/api
PRODUCT_BUNDLE_IDENTIFIER = com.company.app.dev
DISPLAY_NAME = AppName Dev
SWIFT_ACTIVE_COMPILATION_CONDITIONS = $(inherited) DEV
```

### Staging.xcconfig

```
// Staging.xcconfig
API_BASE_URL = https:\/\/staging.domain.com/api
PRODUCT_BUNDLE_IDENTIFIER = com.company.app.staging
DISPLAY_NAME = AppName Staging
SWIFT_ACTIVE_COMPILATION_CONDITIONS = $(inherited) STAGING
```

### Prod.xcconfig

```
// Prod.xcconfig
API_BASE_URL = https:\/\/domain.com/api
PRODUCT_BUNDLE_IDENTIFIER = com.company.app
DISPLAY_NAME = AppName
SWIFT_ACTIVE_COMPILATION_CONDITIONS = $(inherited) PROD
```

### Connecting xcconfig to Build Configurations

1. Project > Info > Configurations
2. Rename Debug/Release or add new configurations:
   - **Debug-Dev** — uses `Dev.xcconfig`
   - **Debug-Staging** — uses `Staging.xcconfig`
   - **Release-Prod** — uses `Prod.xcconfig`
3. Set each configuration's xcconfig file in the dropdown

### Creating Schemes

Create three Xcode schemes (Product > Scheme > Manage Schemes):

| Scheme | Build Configuration | Use Case |
|--------|-------------------|----------|
| **App Dev** | Debug-Dev | Simulator + device via LAN |
| **App Staging** | Debug-Staging | QA testing against staging server |
| **App Production** | Release-Prod | Archive and App Store submission |

### Accessing Config Values in Code

**Info.plist entry:**

```xml
<key>API_BASE_URL</key>
<string>$(API_BASE_URL)</string>
```

**Swift access:**

```swift
enum AppEnvironment {
    static var apiBaseURL: String {
        guard let url = Bundle.main.infoDictionary?["API_BASE_URL"] as? String else {
            fatalError("API_BASE_URL not set in Info.plist")
        }
        return url
    }

    static var isDev: Bool {
        #if DEV
        return true
        #else
        return false
        #endif
    }
}
```

---

## 4. Info.plist Configuration

### Privacy Permission Descriptions

Add **only** the permissions your app actually uses. Apple rejects apps that
request permissions without justification.

```xml
<!-- Camera -->
<key>NSCameraUsageDescription</key>
<string>Take photos of receipts and products</string>

<!-- Photo Library -->
<key>NSPhotoLibraryUsageDescription</key>
<string>Select photos for products and profile</string>

<!-- Location -->
<key>NSLocationWhenInUseUsageDescription</key>
<string>Track delivery locations and nearby branches</string>

<!-- Bluetooth (thermal printers) -->
<key>NSBluetoothAlwaysUsageDescription</key>
<string>Connect to Bluetooth thermal printers</string>
```

### Network Security

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <false/>
    <!-- Dev-only exception for local server -->
    <key>NSExceptionDomains</key>
    <dict>
        <key>192.168.0.0/16</key>
        <dict>
            <key>NSTemporaryExceptionAllowsInsecureHTTPLoads</key>
            <true/>
        </dict>
    </dict>
</dict>
```

**Production builds must use HTTPS only.** The ATS exception above is for
development against a local WAMP/LAMP server on LAN.

### Encryption Compliance

```xml
<key>ITSAppUsesNonExemptEncryption</key>
<false/>
```

Set to `false` if you only use HTTPS (standard TLS). Set to `true` only if
your app implements custom encryption algorithms.

---

## 5. Code Signing

### Development (Automatic — Recommended)

1. Signing & Capabilities > check **Automatically manage signing**
2. Select your Apple Developer team from the dropdown
3. Xcode generates development certificates and provisioning profiles

This is sufficient for Simulator testing and on-device development.

### Distribution (App Store)

**Option A — Automatic (recommended):**

Xcode handles everything when you select "Automatically manage signing" and
archive with Product > Archive. No manual certificate or profile management.

**Option B — Manual (when required):**

1. **Generate CSR:** Keychain Access > Certificate Assistant > Request a
   Certificate from a Certificate Authority
2. **Create Distribution Certificate:** developer.apple.com > Certificates >
   iOS Distribution
3. **Register App ID:** Identifiers > App IDs (must match bundle ID exactly)
4. **Create Provisioning Profile:** Profiles > App Store > select certificate
   and App ID
5. **Download and install:** Double-click the `.mobileprovision` file

### Common Signing Issues

| Problem | Fix |
|---------|-----|
| "No signing certificate" | Xcode > Settings > Accounts > Download certificates |
| Profile mismatch | Ensure bundle ID matches between xcconfig and profile |
| Expired certificate | Revoke old, create new at developer.apple.com |
| Team not showing | Add Apple ID in Xcode > Settings > Accounts |

---

## 6. Asset Catalog Setup

```
Assets.xcassets/
├── AccentColor.colorset/          # App-wide tint colour
├── AppIcon.appiconset/            # 1024x1024 single icon (Xcode 15+)
├── Colors/
│   ├── PrimaryColor.colorset/     # Brand primary (light + dark variants)
│   ├── SecondaryColor.colorset/
│   ├── SurfaceColor.colorset/     # Background surfaces
│   └── ErrorColor.colorset/
├── Icons/
│   ├── home.imageset/             # Custom PNG icons
│   ├── sales.imageset/
│   └── settings.imageset/
└── Images/
    ├── onboarding-1.imageset/
    └── logo.imageset/
```

**Colour sets:** Always define both Light and Dark appearances in the asset
catalog. Use `Color("PrimaryColor")` in SwiftUI.

**App icon:** Xcode 15+ requires a single 1024x1024 PNG. Xcode auto-generates
all required sizes.

---

## 7. Localisation Setup

For East African markets, support English, Swahili, and French at minimum.

### String Catalogs (Xcode 15+)

Use `Localizable.xcstrings` (the modern approach) instead of `.strings` files.
Xcode auto-discovers `Text()` strings and adds them to the catalog.

### Legacy .strings Files

```
// en.lproj/Localizable.strings
"login_title" = "Sign In";
"dashboard_title" = "Dashboard";

// sw.lproj/Localizable.strings
"login_title" = "Ingia";
"dashboard_title" = "Dashibodi";

// fr.lproj/Localizable.strings
"login_title" = "Se Connecter";
"dashboard_title" = "Tableau de Bord";
```

### Usage in SwiftUI

```swift
// Automatic localisation (Text looks up key automatically)
Text("login_title")

// Programmatic access
let title = String(localized: "login_title")

// With interpolation
Text("welcome_message \(userName)")
// In .strings: "welcome_message %@" = "Welcome, %@";
```

---

## 8. App Entry Point

```swift
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            RootView()
        }
        .modelContainer(for: [Product.self, Order.self])
    }
}
```

```swift
struct RootView: View {
    @State private var authService = AuthService()

    var body: some View {
        Group {
            if authService.isAuthenticated {
                MainTabView()
            } else {
                LoginView()
            }
        }
        .environment(authService)
        .task {
            await authService.checkStoredToken()
        }
    }
}
```

---

## 9. Development Network

| Scenario | Base URL |
|----------|----------|
| Simulator on Mac | `http://localhost:8080/api` or LAN IP |
| Real device on same Wi-Fi | `http://192.168.x.x:8080/api` (Mac LAN IP) |
| Staging server | `https://staging.domain.com/api` |
| Production | `https://domain.com/api` |

**Note:** iOS Simulator CAN use `localhost` (unlike Android emulator). Real devices need Mac's LAN IP.

---

## 10. Archive and Upload

- [ ] Production scheme selected
- [ ] Version set (e.g., `1.0.0`), build number incremented (unique per upload)
- [ ] `ITSAppUsesNonExemptEncryption` is `false` (if no custom encryption)
- [ ] All privacy usage descriptions present for used permissions
- [ ] No `NSAllowsArbitraryLoads = true` in production config
- [ ] App icon is set (1024x1024)

### Archive Steps

1. Product > Archive (must have a real device or "Any iOS Device" selected)
2. Organizer opens automatically when archive completes
3. Distribute App > App Store Connect > Upload
4. Wait approximately 30 minutes for processing
5. Configure listing in App Store Connect (screenshots, description, pricing)

---

## 11. TestFlight

| Type | Max Testers | Apple Review | Setup |
|------|-------------|-------------|-------|
| Internal | 100 | Not required | Add team members in App Store Connect |
| External | 10,000 | First build reviewed | Create public link or invite by email |

Testers install TestFlight app, accept invite. Builds expire after 90 days.

---

## 12. New Project Setup Checklist

### Initial Configuration

- [ ] Create Xcode project (SwiftUI, Swift, SwiftData)
- [ ] Set minimum deployment target to iOS 17.0
- [ ] Set bundle ID (`com.company.appname`) — this is permanent
- [ ] Enable automatic code signing, select team

### Build Environment

- [ ] Create `Config/Dev.xcconfig`
- [ ] Create `Config/Staging.xcconfig`
- [ ] Create `Config/Prod.xcconfig`
- [ ] Create three build schemes (Dev, Staging, Production)
- [ ] Add `API_BASE_URL` to Info.plist
- [ ] Create `AppEnvironment.swift` to read config values

### Resources

- [ ] Set up Asset Catalog (AccentColor, AppIcon, brand colours)
- [ ] Add privacy permission descriptions (only used permissions)
- [ ] Set `ITSAppUsesNonExemptEncryption` to `false`
- [ ] Configure ATS exceptions for dev (remove before shipping)

### Project Structure

- [ ] Create directory structure (App/, Core/, Features/, Shared/, Resources/)
- [ ] Set up `RootView` with auth routing
- [ ] Create `APIClient` with environment-aware base URL
- [ ] Add localisation files if multi-language

### Pre-Submission

- [ ] Test on real device (not just Simulator)
- [ ] Test all three schemes (Dev, Staging, Prod)
- [ ] Archive with Production scheme
- [ ] Upload to TestFlight for beta testing
- [ ] Prepare App Store Connect listing

## Anti-Patterns

| Avoid | Do Instead |
|-------|-----------|
| Hardcoded API URLs | xcconfig + Info.plist |
| Single build scheme | Three schemes: Dev/Staging/Prod |
| `NSAllowsArbitraryLoads = true` in prod | HTTPS only; ATS exceptions for dev |
| SPM packages for built-in capabilities | Use Apple frameworks first |
| Manual provisioning for dev | Automatic signing |
| Changing bundle ID post-release | Choose carefully at creation |
| Unused privacy permissions | Add only what you use |
