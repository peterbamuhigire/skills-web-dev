# Privacy Manifest

iOS 17+ privacy manifest (`PrivacyInfo.xcprivacy`), required-reason APIs, and App Tracking Transparency alignment.

## Privacy Manifest Overview

Apple introduced the **privacy manifest** (`PrivacyInfo.xcprivacy`) so apps and third-party SDKs declare machine-readable statements about their data handling and their use of APIs that Apple classifies as privacy-sensitive. The manifest is a property list bundled at the root of the app or SDK. Apple has required it for App Store submissions since May 2024, and enforces it for a growing list of popular third-party SDKs.

The manifest is distinct from the App Store Connect Privacy Nutrition Label. The two must agree — Apple auto-generates a summary from the manifests of your app and its SDKs, and a mismatch with the declared labels is a rejection cause.

## Manifest Structure

A minimal manifest for an app that collects email addresses, does not track, and uses `UserDefaults`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>NSPrivacyTracking</key>
    <false/>
    <key>NSPrivacyTrackingDomains</key>
    <array/>
    <key>NSPrivacyCollectedDataTypes</key>
    <array>
        <dict>
            <key>NSPrivacyCollectedDataType</key>
            <string>NSPrivacyCollectedDataTypeEmailAddress</string>
            <key>NSPrivacyCollectedDataTypeLinked</key>
            <true/>
            <key>NSPrivacyCollectedDataTypeTracking</key>
            <false/>
            <key>NSPrivacyCollectedDataTypePurposes</key>
            <array>
                <string>NSPrivacyCollectedDataTypePurposeAppFunctionality</string>
            </array>
        </dict>
    </array>
    <key>NSPrivacyAccessedAPITypes</key>
    <array>
        <dict>
            <key>NSPrivacyAccessedAPIType</key>
            <string>NSPrivacyAccessedAPICategoryUserDefaults</string>
            <key>NSPrivacyAccessedAPITypeReasons</key>
            <array>
                <string>CA92.1</string>
            </array>
        </dict>
    </array>
</dict>
</plist>
```

Place this file at the root of your app target (or at the root of a resource bundle for an SDK). Xcode picks it up automatically.

## Required-Reason APIs

Apple maintains a list of APIs that can be abused for fingerprinting. If you call any of them, you must declare the category and an approved reason code in `NSPrivacyAccessedAPITypes`. The categories are:

| Category key | What it covers |
|--------------|---------------|
| `NSPrivacyAccessedAPICategoryFileTimestamp` | `getattrlist`, `stat`, `fstat`, `lstat`, `NSFileCreationDate`, `NSFileModificationDate` |
| `NSPrivacyAccessedAPICategorySystemBootTime` | `systemUptime`, `mach_absolute_time`, `clock_gettime` |
| `NSPrivacyAccessedAPICategoryDiskSpace` | `volumeAvailableCapacityKey`, `statfs`, `NSFileSystemFreeSize` |
| `NSPrivacyAccessedAPICategoryActiveKeyboards` | `UITextInputMode.activeInputModes` |
| `NSPrivacyAccessedAPICategoryUserDefaults` | `UserDefaults` reads and writes |

Each category has a handful of approved reason codes. Examples:

- `CA92.1` — "Declare this reason to access user defaults to read and write information that is only accessible to the app itself."
- `C617.1` — "Declare this reason to access the file timestamp APIs to display timestamps to the user."
- `35F9.1` — "Declare this reason to access the system boot time to measure time intervals within the app."

If you cannot find a reason that fits, you cannot use the API in a compliant app. Either change the approach or justify to Apple and accept review risk. New reason codes appear from time to time — check Apple's developer documentation before a release.

## App Tracking Transparency

App Tracking Transparency (ATT, iOS 14.5+) is separate from the privacy manifest. If your app — or any SDK inside it — uses cross-app or cross-website tracking identifiers (IDFA, email hashes used for matching, fingerprints), you must:

1. Add `NSUserTrackingUsageDescription` to `Info.plist` with a clear explanation.
2. Call `ATTrackingManager.requestTrackingAuthorization(completionHandler:)` before accessing any tracking identifier.
3. Set `NSPrivacyTracking` to `true` in the manifest and list tracking domains in `NSPrivacyTrackingDomains`.
4. For every collected data type used for tracking, set `NSPrivacyCollectedDataTypeTracking` to `true`.

```swift
import AppTrackingTransparency
import AdSupport

func requestTracking() async -> Bool {
    let status = await ATTrackingManager.requestTrackingAuthorization()
    return status == .authorized
}
```

Do not call `ASIdentifierManager.shared().advertisingIdentifier` before receiving `.authorized`. If the user declines, the API returns all-zero bytes.

## Third-Party SDK Privacy Manifests

Apple requires certain popular SDKs to ship their own `PrivacyInfo.xcprivacy` inside their bundles. Your app inherits all declared APIs and data types from every SDK you include. Before integrating an SDK:

1. Check whether the SDK ships a privacy manifest.
2. Read it — you are responsible for everything it declares.
3. Merge the data types into your App Store Connect privacy labels.
4. Confirm the SDK's declared APIs match what you actually use from the SDK.

If an SDK does not ship a manifest and Apple's list requires one for it, your submission is rejected.

## Data Collection Categories

Common collected data types:

| Category | Examples |
|----------|----------|
| Contact Info | Email, phone, physical address |
| Identifiers | User ID, device ID |
| Financial Info | Payment info, credit info |
| Location | Precise, coarse |
| Sensitive Info | Racial/ethnic, sexual orientation, health, political |
| Health & Fitness | Health records, fitness |
| Contacts | Contacts list |
| User Content | Emails, messages, photos, audio, customer support |
| Browsing History | Browsing |
| Search History | Search terms |
| Usage Data | Product interaction, advertising data, other usage |
| Diagnostics | Crash data, performance data, other diagnostic data |

Each collected data type entry in the manifest declares:

- The specific data type key.
- `NSPrivacyCollectedDataTypeLinked` — is the data linked to the user's identity?
- `NSPrivacyCollectedDataTypeTracking` — is it used for tracking?
- `NSPrivacyCollectedDataTypePurposes` — one or more of: AppFunctionality, Analytics, Advertising, ProductPersonalization, DeveloperAdvertising, ThirdPartyAdvertising, Other.

## Linked vs Unlinked

- **Linked** — the data is associated with the user's identity (user account, device ID tied to account). Crash reports attached to a user account are linked.
- **Unlinked** — the data is anonymous and cannot be associated with the user. Aggregate usage counters with no user ID are unlinked.

Marking data as unlinked when you actually tie it to an identity later is a violation. Most collected data ends up linked in practice.

## Review and Audit Workflow

1. Enumerate every SDK in the app and capture its privacy manifest.
2. Enumerate every API your own code calls that appears on Apple's required-reason list.
3. Draft `PrivacyInfo.xcprivacy` covering: tracking flag, tracking domains, collected data types (app + SDKs), accessed API types + reasons.
4. Open App Store Connect Privacy Label and mirror every declaration.
5. Run Xcode's "Privacy Report" generator (Product → Archive → Export → Generate Privacy Report) to compare your declarations to what Xcode detects.
6. Fix any mismatches before submission.

Repeat this workflow every time you add or upgrade a dependency.

## Common Violations That Cause Rejection

- Missing privacy manifest for apps or SDKs in the enforced list.
- Required-reason API called without a declaration.
- Declared reason code that does not match the actual use case.
- Data type used in the app but not declared, or declared but not used.
- App Store Connect labels diverging from the manifest.
- Tracking occurs without calling `ATTrackingManager` first.
- `NSUserTrackingUsageDescription` missing when tracking is declared.

## Anti-Patterns

- **Copy-pasting another app's manifest.** Your APIs and data types are specific to you.
- **Forgetting to update the manifest when adding a new SDK.** A new dependency can change every privacy claim.
- **Declaring APIs you do not use "to be safe".** Apple can ask you to justify the declaration and it inflates your declared surface.
- **Treating ATT as optional.** If you touch IDFA at all, you must ask.
- **Logging PII in crash reports.** Crash reports you send off-device become personal data and must be declared.
- **Hiding tracking behind "essential functionality" purpose.** Apple considers retargeting advertising, not functionality, regardless of how you label it.

## Cross-References

- `code-signing-entitlements.md` — usage descriptions live in the same Info.plist and must align with privacy declarations.
- `keychain-secure-enclave.md` — Keychain use is not on the required-reason list but telemetry about it might be.
- `ats-cert-pinning.md` — pinning failure telemetry is a collected data type and must be declared.
- `app-store-review` skill — privacy label workflow and rejection recovery.
- `uganda-dppa-compliance` skill — local data protection obligations that layer on top of Apple's requirements.
