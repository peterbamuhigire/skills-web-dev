---
name: ios-biometric-login
description: "Optional biometric (Face ID/Touch ID) gate on iOS app launch using LocalAuthentication framework. Covers BiometricHelper utility, splash screen integration, settings toggle with verification, Keychain-backed preference storage, and graceful fallback. Use when adding biometric authentication to any iOS app."
---

## Required Plugins

**Superpowers plugin:** MUST be active for all work using this skill. Use throughout the entire build pipeline — design decisions, code generation, debugging, quality checks, and any task where it offers enhanced capabilities. If superpowers provides a better way to accomplish something, prefer it over the default approach.

# iOS Biometric Login

Add optional Face ID / Touch ID authentication as a gate on app launch. Uses the `LocalAuthentication` framework (`LAContext`). The feature is opt-in: users enable it in Settings, and it triggers on every app launch from the splash screen.

## Overview

**Flow:** App launch → Splash → Check biometric pref → LAContext prompt → Success (Main) or Failure (Login screen).

**Key principles:**
- **Optional, not mandatory** — users choose to enable via a Settings toggle
- **Verify before enabling** — require biometric auth to turn the feature ON (prevents unauthorised enabling)
- **Graceful degradation** — if device has no biometric hardware, hide the toggle entirely
- **Survive logout** — biometric preference persists across logout/re-login (stored in Keychain)
- **No custom UI** — use the system biometric dialog (consistent UX, handles retries)

## Framework

No third-party dependencies. Uses Apple's built-in `LocalAuthentication` framework.

```swift
import LocalAuthentication
```

No CocoaPods, SPM packages, or Cartfile entries needed.

## Architecture

```
Core/Auth/
  BiometricHelper.swift   — Actor: biometricType + authenticate()
  KeychainHelper.swift    — Keychain read/write for biometric preference
  AuthManager.swift       — Stores auth state, delegates biometric pref to Keychain

Features/Splash/
  SplashView.swift        — Checks pref + triggers prompt on app launch

Features/Settings/
  SettingsView.swift      — Toggle with verify-before-enable
  SettingsViewModel.swift — Delegates to AuthManager
```

## Step 1: BiometricHelper (Actor)

A lightweight `actor` with two responsibilities: detect biometric type and authenticate. Thread-safe by design.

```swift
import LocalAuthentication

actor BiometricHelper {

    enum BiometricType {
        case faceID, touchID, none

        var displayName: String {
            switch self {
            case .faceID:  return "Face ID"
            case .touchID: return "Touch ID"
            case .none:    return "Biometrics"
            }
        }

        var systemImage: String {
            switch self {
            case .faceID:  return "faceid"
            case .touchID: return "touchid"
            case .none:    return "lock.shield"
            }
        }
    }

    enum BiometricError: Error, LocalizedError {
        case notAvailable
        case notEnrolled
        case failed(String)
        case cancelled
        case lockedOut

        var errorDescription: String? {
            switch self {
            case .notAvailable: return "Biometric authentication is not available on this device."
            case .notEnrolled:  return "No biometrics are enrolled. Go to Settings > Face ID & Passcode."
            case .failed(let msg): return msg
            case .cancelled:    return "Authentication was cancelled."
            case .lockedOut:    return "Biometrics are locked. Use your passcode to unlock."
            }
        }
    }

    // MARK: - Detection

    /// Returns the biometric type available on this device.
    nonisolated func biometricType() -> BiometricType {
        let context = LAContext()
        var error: NSError?
        guard context.canEvaluatePolicy(
            .deviceOwnerAuthenticationWithBiometrics, error: &error
        ) else {
            return .none
        }
        switch context.biometryType {
        case .faceID:       return .faceID
        case .touchID:      return .touchID
        case .opticID:      return .faceID // Vision Pro — treat as Face ID
        @unknown default:   return .none
        }
    }

    /// Returns true if biometric authentication is available and enrolled.
    nonisolated func canAuthenticate() -> Bool {
        return biometricType() != .none
    }

    // MARK: - Authentication

    /// Presents the system biometric prompt. Returns true on success.
    /// Throws BiometricError on failure or cancellation.
    func authenticate(reason: String) async throws -> Bool {
        let context = LAContext()
        context.localizedFallbackTitle = "Use Passcode"
        context.localizedCancelTitle = "Cancel"

        do {
            let success = try await context.evaluatePolicy(
                .deviceOwnerAuthenticationWithBiometrics,
                localizedReason: reason
            )
            return success
        } catch let error as LAError {
            switch error.code {
            case .userCancel, .appCancel, .systemCancel:
                throw BiometricError.cancelled
            case .biometryLockout:
                throw BiometricError.lockedOut
            case .biometryNotAvailable:
                throw BiometricError.notAvailable
            case .biometryNotEnrolled:
                throw BiometricError.notEnrolled
            default:
                throw BiometricError.failed(error.localizedDescription)
            }
        }
    }
}
```

### Key Decisions

- **`actor` not `class`** — thread-safe without manual locking; safe to call from any context.
- **`nonisolated` for detection** — `biometricType()` and `canAuthenticate()` create their own `LAContext` and are safe to call synchronously from the main thread.
- **No `deviceOwnerAuthentication` fallback** — we use `deviceOwnerAuthenticationWithBiometrics` only. Passcode fallback is handled by navigating to login, not by the system passcode screen.
- **`async throws`** — native Swift concurrency; no completion handlers or Combine publishers needed.

## Step 2: KeychainHelper for Preference Storage

Store the biometric-enabled flag in the Keychain. Unlike `UserDefaults`, Keychain data survives app reinstall and is encrypted at rest.

```swift
import Foundation
import Security

enum KeychainHelper {

    /// Save a boolean value to the Keychain.
    static func setBool(_ value: Bool, forKey key: String) {
        let data = Data([value ? 1 : 0])
        let query: [String: Any] = [
            kSecClass as String:       kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String:   data,
            kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlock
        ]
        // Delete existing, then add
        SecItemDelete(query as CFDictionary)
        SecItemAdd(query as CFDictionary, nil)
    }

    /// Read a boolean value from the Keychain. Returns nil if not found.
    static func getBool(forKey key: String) -> Bool? {
        let query: [String: Any] = [
            kSecClass as String:       kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String:  true,
            kSecMatchLimit as String:  kSecMatchLimitOne
        ]
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        guard status == errSecSuccess, let data = result as? Data, !data.isEmpty else {
            return nil
        }
        return data[0] == 1
    }

    /// Remove a value from the Keychain.
    static func remove(forKey key: String) {
        let query: [String: Any] = [
            kSecClass as String:       kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]
        SecItemDelete(query as CFDictionary)
    }
}
```

### AuthManager Integration

```swift
class AuthManager: ObservableObject {

    private static let biometricKey = "biometric_login_enabled"

    @Published var isLoggedIn: Bool = false

    var isBiometricEnabled: Bool {
        KeychainHelper.getBool(forKey: Self.biometricKey) ?? false
    }

    func setBiometricEnabled(_ enabled: Bool) {
        KeychainHelper.setBool(enabled, forKey: Self.biometricKey)
        objectWillChange.send()
    }

    func logout() {
        // Biometric preference is in Keychain — NOT cleared on logout
        // Only clear session tokens, user data, etc.
        isLoggedIn = false
    }
}
```

**Key insight:** `logout()` does NOT clear the biometric preference. The Keychain entry persists independently of session state.

## Step 3: Splash Screen with Biometric Gate

The splash screen is the single integration point. Uses `@State` to track authentication status and `.task` for async biometric check.

```swift
import SwiftUI

struct SplashView: View {

    @EnvironmentObject var authManager: AuthManager
    @State private var isCheckingAuth = true
    @State private var authPassed = false

    private let biometricHelper = BiometricHelper()

    var body: some View {
        Group {
            if isCheckingAuth {
                splashContent
            } else if authPassed {
                MainTabView()
            } else {
                LoginView()
            }
        }
        .task {
            // Brief splash display
            try? await Task.sleep(for: .seconds(1.5))
            await checkAuthentication()
        }
    }

    private var splashContent: some View {
        ZStack {
            Color.accentColor.ignoresSafeArea()
            Image("AppLogo").resizable().scaledToFit().frame(width: 120, height: 120)
        }
    }

    private func checkAuthentication() async {
        guard authManager.isLoggedIn else {
            authPassed = false
            isCheckingAuth = false
            return
        }

        let biometricEnabled = authManager.isBiometricEnabled
        let canAuth = biometricHelper.canAuthenticate()

        if biometricEnabled && canAuth {
            do {
                let success = try await biometricHelper.authenticate(
                    reason: "Verify your identity to access the app"
                )
                authPassed = success
            } catch {
                // Cancelled, locked out, or failed — go to login
                authPassed = false
            }
        } else {
            // No biometric gate — pass through
            authPassed = true
        }

        isCheckingAuth = false
    }
}
```

## Step 4: Settings Toggle with Verify-Before-Enable

The toggle is conditionally rendered — only shown if the device supports biometrics. Enabling requires biometric verification first.

```swift
import SwiftUI

struct BiometricSettingsRow: View {

    @EnvironmentObject var authManager: AuthManager
    @State private var isEnabled: Bool = false
    @State private var isAuthenticating = false

    private let biometricHelper = BiometricHelper()

    var body: some View {
        let type = biometricHelper.biometricType()

        if type != .none {
            Toggle(isOn: $isEnabled) {
                Label {
                    VStack(alignment: .leading, spacing: 2) {
                        Text("\(type.displayName) Login")
                        Text("Use \(type.displayName) to unlock the app")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                } icon: {
                    Image(systemName: type.systemImage)
                        .foregroundStyle(.blue)
                }
            }
            .disabled(isAuthenticating)
            .onChange(of: isEnabled) { oldValue, newValue in
                handleToggle(newValue: newValue)
            }
            .onAppear {
                isEnabled = authManager.isBiometricEnabled
            }
        }
        // If type == .none, nothing is rendered
    }

    private func handleToggle(newValue: Bool) {
        if newValue {
            // Verify identity before enabling
            isAuthenticating = true
            Task {
                do {
                    let success = try await biometricHelper.authenticate(
                        reason: "Authenticate to enable \(biometricHelper.biometricType().displayName)"
                    )
                    await MainActor.run {
                        if success {
                            authManager.setBiometricEnabled(true)
                        } else {
                            isEnabled = false // Revert toggle
                        }
                        isAuthenticating = false
                    }
                } catch {
                    await MainActor.run {
                        isEnabled = false // Revert toggle
                        isAuthenticating = false
                    }
                }
            }
        } else {
            // Disabling does NOT require verification
            authManager.setBiometricEnabled(false)
        }
    }
}
```

### Usage in SettingsView

```swift
struct SettingsView: View {
    var body: some View {
        Form {
            Section("Security") {
                BiometricSettingsRow()
                // ... other security settings
            }
        }
        .navigationTitle("Settings")
    }
}
```

## Step 5: Info.plist Configuration

Face ID requires a usage description in `Info.plist`. Touch ID does NOT require one.

```xml
<key>NSFaceIDUsageDescription</key>
<string>Use Face ID to unlock the app quickly</string>
```

**Without this key:** The app will crash on the first Face ID prompt. This is a hard requirement from Apple — the App Store will reject apps that use Face ID without this key.

**Touch ID note:** Touch ID uses the fingerprint sensor API which predates the usage-description requirement. No Info.plist key is needed for Touch ID-only devices.

## Flow Diagram

```
App Launch
  ↓
[Splash Screen] — 1.5s delay
  ↓
isLoggedIn?
  ├─ NO → Login Screen
  └─ YES
      ↓
      isBiometricEnabled && canAuthenticate()?
        ├─ YES → System Biometric Prompt
        │   ├─ Success → Main Screen
        │   └─ Failure/Cancel → Login Screen
        └─ NO → Main Screen (skip biometric)
```

## Patterns & Anti-Patterns

### DO
- Use `LAContext.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics)` for biometric-only auth
- Require biometric verification when the user turns the feature ON
- Preserve biometric preference across logout (Keychain is independent of session)
- Use `actor` for `BiometricHelper` — thread-safe by default
- Hide the toggle entirely on devices without biometric hardware
- Show the biometric type name dynamically ("Face ID" / "Touch ID")
- Add `NSFaceIDUsageDescription` to Info.plist
- Use `async/await` — no completion handler pyramids

### DON'T
- Don't use `deviceOwnerAuthentication` (with passcode fallback) — defeats the biometric gate purpose
- Don't store biometric data yourself — the Secure Enclave handles enrollment and matching
- Don't show biometric prompt on the login screen — only on splash (user is already authenticated)
- Don't require biometric for disabling the feature — that traps users who cannot authenticate
- Don't use `UserDefaults` for the biometric preference — it is not encrypted and is wiped on reinstall
- Don't use deprecated `TouchID` APIs — use `LocalAuthentication` framework only
- Don't force-unwrap `LAContext` results — always handle errors gracefully
- Don't forget to handle `.biometryLockout` — the user needs to unlock with their device passcode first

## Edge Cases

| Scenario | Behaviour |
|----------|-----------|
| No biometric hardware | Settings toggle hidden, splash skips biometric |
| Biometrics enrolled then removed | `canAuthenticate()` returns false, splash skips |
| User cancels prompt | `.cancelled` error → navigate to Login |
| Too many failed attempts (lockout) | `.biometryLockout` → navigate to Login |
| Force password change + biometric | Biometric first, then redirect to ChangePassword |
| App killed during prompt | Next launch starts fresh from splash |
| App goes to background during prompt | System cancels the prompt (`.systemCancel`) |
| Device has no passcode set | Biometrics unavailable — `canAuthenticate()` returns false |
| Multiple accounts on device | Biometric pref is per-app (Keychain scoped to app bundle) |
| Keychain shared via App Group | Use a unique key prefix per app if sharing a Keychain group |

## Integration with Other Skills

```
ios-biometric-login
  ├── dual-auth-rbac          (JWT auth, AuthManager, token storage)
  ├── vibe-security-skill     (secure coding, Keychain best practices)
  └── webapp-gui-design       (settings UI patterns, toggle UX)
```

**Key integrations:**
- `dual-auth-rbac`: BiometricHelper works alongside JWT auth — biometric gates app access, JWT gates API access
- `vibe-security-skill`: Keychain storage follows secure coding patterns — `kSecAttrAccessibleAfterFirstUnlock` for background availability

## Checklist

- [ ] Import `LocalAuthentication` framework
- [ ] Create `BiometricHelper` actor with `biometricType()` + `authenticate()`
- [ ] Create `KeychainHelper` for biometric preference storage
- [ ] Add biometric preference to `AuthManager` (persists across logout)
- [ ] Add `NSFaceIDUsageDescription` to Info.plist
- [ ] Integrate biometric check in `SplashView` with `async/await`
- [ ] Add Settings toggle with verify-before-enable (`BiometricSettingsRow`)
- [ ] Show dynamic label ("Face ID" / "Touch ID") based on device capability
- [ ] Handle all `LAError` codes (cancel, lockout, not enrolled, not available)
- [ ] Test on Face ID device, Touch ID device, and Simulator
- [ ] Test: enable toggle requires authentication, disable does not
- [ ] Test: preference survives app reinstall (Keychain) and logout
