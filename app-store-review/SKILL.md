---
name: app-store-review
description: "Apple App Store compliance and review readiness for iOS apps. Use when preparing App Store Connect submissions, validating App Review Guidelines, privacy labels, permissions, In-App Purchases, store listing accuracy, TestFlight testing, and reviewer notes."
---

## Required Plugins

**Superpowers plugin:** MUST be active for all work using this skill. Use throughout the entire build pipeline — design decisions, code generation, debugging, quality checks, and any task where it offers enhanced capabilities. If superpowers provides a better way to accomplish something, prefer it over the default approach.

# Apple App Store Review Readiness

## Overview

Use this skill to ensure iOS apps meet Apple App Store policy and technical requirements before first submission or major updates. Apple uses **human review for every submission**, so focus on completeness, clarity, and compliance to avoid delays and rejections.

## Quick Reference

- App Review Guidelines: completeness, metadata accuracy, design, privacy, IAP rules
- Privacy Labels: declared data types must match actual collection in code
- Info.plist permissions: every key must have a specific, honest usage description
- App Store Connect: screenshots, metadata, URLs, age rating, category
- TestFlight: internal (100 testers) and external (10,000 testers, reviewed)
- Review notes: test credentials, special instructions, permission justifications
- Code signing: certificates, provisioning profiles, entitlements
- Export compliance: ITSAppUsesNonExemptEncryption setting

## Key Differences from Google Play

| Aspect | Google Play | Apple App Store |
|---|---|---|
| Data disclosure | Data Safety Form | App Privacy Labels |
| Console | Play Console | App Store Connect |
| Review type | Automated + manual | Human review always |
| Rollout | Staged rollout % | Phased release (7-day automatic) |
| Testing tracks | Internal / Closed / Open | TestFlight (internal / external) |
| App signing | APK/AAB signing | Code signing + provisioning profiles |
| Payment rules | Flexible in some regions | IAP required for all digital content |

## Core Instructions

1. Inventory app features and risk areas (IAP, UGC, health data, location, kids content). Map each to relevant App Review Guidelines sections.
2. Audit all data collection against App Privacy Labels. Every SDK, analytics tool, and API call that collects data must be declared.
3. Validate every Info.plist permission key has a specific, honest usage description that explains why the app needs it.
4. Confirm App Store Connect metadata is complete: screenshots match real UI, URLs are live, age rating is accurate.
5. Verify IAP flows: digital content and subscriptions use StoreKit, restore purchases works, no links to external payment.
6. Run TestFlight builds through internal testing. For first submission, prepare external TestFlight build (Apple reviews it).
7. Write thorough review notes with test credentials, steps to reach key features, and explanations for anything unusual.
8. Verify code signing, provisioning profiles, and entitlements are correct for distribution.

---

## 1. App Review Guidelines (Key Rules)

Apple's App Review Guidelines are organised into five sections. These are the rules that most commonly cause rejections:

### 1.x Safety

- **1.2 User-Generated Content:** Apps with UGC must include content filtering, a reporting mechanism, and the ability to block abusive users. Moderation is mandatory.

### 2.x Performance

- **2.1 App Completeness:** No placeholder content, broken links, lorem ipsum, or test data. Every screen must be functional. Beta labels or "coming soon" features trigger rejection.
- **2.3 Accurate Metadata:** Screenshots and previews must reflect the actual app experience. Do not show features that do not exist. Keywords must not include competitor names or irrelevant terms.
- **2.5.1 Public APIs Only:** Only use documented, public Apple APIs. Use of private or undocumented APIs is grounds for immediate rejection.

### 3.x Business

- **3.1 In-App Purchase Required:** All digital content, subscriptions, and feature unlocks sold within the app must use Apple's In-App Purchase (StoreKit). You cannot link to external payment systems for digital goods.
- **3.1.1 IAP Types:** Consumable, non-consumable, auto-renewable subscription, non-renewing subscription. Choose correctly.
- **3.1.2 Subscriptions:** Must clearly communicate what the user gets, the price, duration, and how to cancel. Free trials must disclose when billing begins.

### 4.x Design

- **4.0 Human Interface Guidelines:** App must follow basic HIG principles. No confusing navigation, broken layouts, or non-standard UI that harms usability.
- **4.2 Minimum Functionality:** Apps must provide lasting value. Simple websites wrapped in a WebView, apps with no features, or "thin" apps are rejected.

### 5.x Legal / Privacy

- **5.1 Privacy:** Must have a publicly accessible privacy policy URL. The policy must explain what data is collected and how it is used.
- **5.1.1 Data Collection Disclosure:** Data collection practices must match the App Privacy Labels exactly. Discrepancies are a common rejection reason.
- **5.1.2 Data Use and Sharing:** The purpose for each data type must be disclosed. If data is shared with third parties, this must be declared.

---

## 2. App Privacy Labels (Critical)

Privacy Labels appear on your App Store listing. They must accurately reflect all data your app collects.

### Three Categories

1. **Data Used to Track You:** Data linked to your identity and used for tracking across apps/websites owned by other companies.
2. **Data Linked to You:** Data connected to your identity but not used for cross-app tracking.
3. **Data Not Linked to You:** Data collected but not linked to your identity.

### Common Data Types to Declare

| Data Type | Examples |
|---|---|
| Contact Info | Name, email, phone, address |
| Identifiers | User ID, device ID, IDFA |
| Usage Data | Product interaction, advertising data, app launches |
| Location | Precise location, coarse location |
| Financial Info | Payment info, credit score |
| Health & Fitness | Health records, workout data |
| Diagnostics | Crash data, performance data |
| Purchases | Purchase history |

### Declaration Rules

For each data type collected, you must declare:
- **Purpose:** App functionality, analytics, advertising, product personalisation, etc.
- **Linked to identity:** Whether this data is connected to the user's account or identity.
- **Used for tracking:** Whether this data is used to track users across other companies' apps or websites.

### Common Mistakes

- Forgetting to declare analytics SDK data collection (Firebase, Mixpanel, etc.).
- Not declaring crash reporting tools (Crashlytics collects device info and diagnostics).
- Claiming "Data Not Collected" while using any third-party SDK that phones home.
- Not updating labels when adding new SDKs or features.

---

## 3. Info.plist Permissions Audit

Every permission your app requests must have a clear, specific usage description in Info.plist. Apple rejects vague or generic descriptions.

### Key Permission Keys

| Key | Purpose | Good Example |
|---|---|---|
| `NSCameraUsageDescription` | Camera access | "Take a photo of your receipt to attach to an expense report" |
| `NSPhotoLibraryUsageDescription` | Photo library read | "Select photos from your library to add to your profile" |
| `NSPhotoLibraryAddUsageDescription` | Save to photo library | "Save generated reports as images to your photo library" |
| `NSLocationWhenInUseUsageDescription` | Location while using | "Find nearby stores and show them on the map" |
| `NSLocationAlwaysAndWhenInUseUsageDescription` | Background location | "Track your delivery route in the background to provide live updates" |
| `NSBluetoothAlwaysUsageDescription` | Bluetooth | "Connect to your Bluetooth receipt printer" |
| `NSMicrophoneUsageDescription` | Microphone | "Record voice notes to attach to patient records" |
| `NSFaceIDUsageDescription` | Face ID | "Unlock the app quickly using Face ID instead of your PIN" |
| `NSContactsUsageDescription` | Contacts | "Import contacts to quickly share invoices via email" |
| `NSCalendarsUsageDescription` | Calendar | "Add appointment reminders to your calendar" |

### Rules

- **Be specific:** "This app needs camera" will be rejected. Explain exactly what the camera is used for.
- **Be honest:** The description must match actual usage. Do not claim a purpose that does not exist.
- **Remove unused keys:** If you are not using a permission, remove the key entirely. Unused permission requests trigger rejection.
- **Test denial paths:** Every permission must have a graceful fallback if the user denies access.

---

## 4. App Store Connect Configuration

### Required Metadata

- **App Name:** Up to 30 characters. Must not include generic terms or competitor names.
- **Subtitle:** Up to 30 characters. Brief value proposition.
- **Keywords:** Up to 100 characters, comma-separated. No spaces after commas. No duplicate words from app name.
- **Description:** Up to 4000 characters. First 3 lines visible without expanding.
- **What's New:** Release notes for each version update.

### Screenshots (Minimum Required)

| Device | Size | Required |
|---|---|---|
| iPhone 6.7" (15 Pro Max) | 1290 x 2796 | Yes |
| iPhone 6.5" (11 Pro Max) | 1242 x 2688 | Yes (or 6.7") |
| iPad 13" (Pro) | 2048 x 2732 | Yes (if iPad supported) |

- Screenshots must show the actual app UI. Marketing overlays are allowed but must not misrepresent functionality.
- Up to 10 screenshots per device size.
- App preview videos: up to 30 seconds, optional but recommended.

### Required URLs

- **Privacy Policy URL:** Must be live and publicly accessible. Required for all apps.
- **Support URL:** Must be live. Can be a contact page, help centre, or support email page.
- **Marketing URL:** Optional but recommended.

### Other Required Fields

- **App Icon:** 1024x1024 PNG, no alpha channel, no rounded corners (system applies them).
- **Age Rating:** Complete the questionnaire honestly. Inaccurate ratings cause rejection.
- **Category:** Primary and secondary category selection.
- **Copyright:** Format: "© 2026 Company Name"
- **Version Number:** Semantic versioning (e.g., 1.0.0). Must increment with each submission.
- **Build Number:** Must be unique for each upload. Can be integer or semantic.

---

## 5. TestFlight Testing

### Internal Testing

- Up to **100 testers** (must be App Store Connect users with at least Developer role).
- Builds available **immediately** after processing. No Apple review required.
- Use for rapid iteration and team testing.

### External Testing

- Up to **10,000 testers** via email invitation or public link.
- **First build requires Apple review** (usually 24-48 hours). Subsequent builds to the same group are auto-approved unless significant changes.
- Testers install via the TestFlight app.
- Builds expire after **90 days**.

### Best Practices

- Always run at least one full round of internal TestFlight testing before submitting for App Store review.
- Include test account credentials in the TestFlight "What to Test" field.
- Monitor crash reports in TestFlight feedback.
- Use TestFlight groups to segment testers by feature or role.

---

## 6. Review Notes (Critical for First Submission)

Review notes are your direct communication channel with the Apple reviewer. Thorough notes significantly reduce rejection risk.

### Must Include

1. **Demo/test account credentials:** Username and password for a pre-populated test account.
2. **Step-by-step instructions:** How to reach features that require setup, login, or specific conditions.
3. **Permission justifications:** Why each permission is requested and where in the app it is triggered.
4. **Content explanations:** Notes on any content that might appear to violate guidelines but has a legitimate purpose.
5. **Special hardware/setup:** If features require Bluetooth devices, specific locations, or external equipment, explain how to test without them.

### Template

```markdown
## Test Account
Email: reviewer@example.com
Password: TestReview2026!

## Key Features to Test
1. Receipt Scanner (Camera Permission)
   - Path: Home > Expenses > Add Expense > Scan Receipt
   - Camera is used to photograph paper receipts for OCR processing.
   - If camera access is denied, user can manually enter expense details.

2. Store Locator (Location Permission)
   - Path: Home > Find Stores
   - Location is used to show nearby stores on the map.
   - If location is denied, user can search by city or postcode.

3. Premium Subscription (In-App Purchase)
   - Path: Home > Settings > Upgrade to Premium
   - Uses auto-renewable subscription via StoreKit.
   - Sandbox account can be used to test purchase flow.

## Special Notes
- First launch syncs data from server (~5 seconds on first load).
- The app does not use any custom encryption (ITSAppUsesNonExemptEncryption = NO).
- All user-generated content is moderated via automated filters + manual review queue.
```

---

## 7. Common Rejection Reasons

Ranked by frequency based on Apple's published data:

1. **Crashes or bugs** — App crashes on launch or during reviewer testing.
2. **Placeholder content** — Incomplete features, "coming soon" sections, lorem ipsum.
3. **Inaccurate screenshots** — Screenshots show features or UI that do not exist.
4. **Missing privacy policy** — No URL provided or URL returns 404.
5. **Privacy label mismatch** — Declared labels do not match actual data collection.
6. **Permission requests without justification** — Requesting permissions not clearly needed.
7. **External payment links** — Linking to websites for digital purchases (bypassing IAP).
8. **Private API usage** — Using undocumented Apple APIs.
9. **Insufficient functionality** — WebView wrappers or apps with no meaningful features.
10. **Inaccurate age rating** — Mature content with low age rating.
11. **References to competing platforms** — Mentioning Android, Google Play, or other platforms.
12. **Broken links** — Support URL, privacy policy URL, or in-app links that do not work.

### If Rejected

- Read the rejection reason carefully. Apple provides specific guideline references.
- Fix only the cited issue; do not make unrelated changes that could trigger new reviews.
- Use the Resolution Centre in App Store Connect to communicate with the reviewer.
- You can appeal a rejection if you believe it is incorrect.

---

## 8. Phased Release

Phased release distributes your update gradually over 7 days:

| Day | Percentage |
|---|---|
| 1 | 1% |
| 2 | 2% |
| 3 | 5% |
| 4 | 10% |
| 5 | 20% |
| 6 | 50% |
| 7 | 100% |

### Controls

- **Pause:** Stop the rollout at the current percentage. Useful if crash reports spike.
- **Resume:** Continue the phased rollout from where it was paused.
- **Release to All:** Skip remaining phases and push to 100% immediately.
- Users who search for the app manually always get the latest version, regardless of phase.
- Phased release only affects automatic updates.

---

## 9. Export Compliance

### ITSAppUsesNonExemptEncryption

Add this key to your Info.plist:

```xml
<key>ITSAppUsesNonExemptEncryption</key>
<false/>
```

Set to `NO` if your app:
- Only uses standard HTTPS (TLS/SSL) for network calls.
- Only uses Apple's built-in encryption frameworks (CryptoKit, Security framework) for standard purposes.

Set to `YES` if your app:
- Implements custom encryption algorithms.
- Uses encryption for purposes beyond standard HTTPS.
- Ships encryption technology to countries with import restrictions.

If `YES`, you must provide export compliance documentation (CCATS or self-classification report) in App Store Connect.

### Why This Matters

If you do not set this key, App Store Connect will ask you about export compliance **every time you upload a build**. Setting it in Info.plist skips this step.

---

## 10. Code Signing and Provisioning

### Certificates

- **Development:** For running on physical devices during development.
- **Distribution:** For App Store and TestFlight builds. Created in Apple Developer portal.

### Provisioning Profiles

- **Development:** Links dev certificate + device UDIDs + App ID.
- **Distribution (App Store):** Links distribution certificate + App ID. No device list (Apple handles distribution).

### Entitlements

- Must match capabilities enabled in App ID (push notifications, HealthKit, iCloud, etc.).
- Mismatch between entitlements and provisioning profile causes build rejection.

### Best Practices

- Use **automatic signing** in Xcode for development.
- Use **manual signing** for CI/CD and distribution builds for predictable results.
- Rotate certificates before expiry (Apple certificates last 1 year).
- Never share distribution certificates via insecure channels.

---

## 11. Pre-Submission Checklist

Run through this checklist before every App Store submission:

### Content and Completeness

- [ ] All screens complete — no placeholder content, lorem ipsum, or test data
- [ ] All features functional — no "coming soon" sections or broken flows
- [ ] No crashes on launch or during core user flows
- [ ] No references to competing platforms (Android, Google Play, etc.)

### Metadata and Store Listing

- [ ] Screenshots match actual app UI on all required device sizes
- [ ] App name, subtitle, and keywords within character limits
- [ ] Description accurately represents app features
- [ ] Age rating questionnaire completed accurately
- [ ] App category selected appropriately

### Privacy and Permissions

- [ ] Privacy policy URL is live, accessible, and accurate
- [ ] App Privacy Labels match all data collection in code and SDKs
- [ ] All Info.plist permission descriptions are specific and honest
- [ ] Unused permission keys removed from Info.plist
- [ ] Denial paths tested for every permission (graceful fallback)

### Technical

- [ ] ITSAppUsesNonExemptEncryption set correctly in Info.plist
- [ ] Version number incremented from previous submission
- [ ] Build number is unique
- [ ] App icon is 1024x1024, no alpha, no rounded corners
- [ ] Code signing and provisioning profiles configured for distribution
- [ ] Entitlements match App ID capabilities

### Monetisation

- [ ] All digital purchases use StoreKit In-App Purchase
- [ ] Restore Purchases button exists and works
- [ ] Subscription terms, pricing, and cancellation clearly displayed
- [ ] No links to external payment for digital content

### Testing

- [ ] TestFlight internal testing passed on multiple devices
- [ ] Tested on oldest supported iOS version
- [ ] Tested on both iPhone and iPad (if universal)
- [ ] Network error states handled (offline, timeout, server error)

### Submission

- [ ] Support URL is live and accessible
- [ ] Review notes include test account credentials
- [ ] Review notes include steps to reach key features
- [ ] Review notes explain any permissions or content that might raise questions

---

## Common Pitfalls

- Declaring "Data Not Collected" while using Firebase Analytics, Crashlytics, or any tracking SDK.
- Requesting camera or location permission at app launch instead of at point of use.
- Including `NSLocationAlwaysAndWhenInUseUsageDescription` when only "when in use" is needed.
- Forgetting to test the restore purchases flow for IAP.
- Submitting screenshots from the simulator with debug overlays visible.
- Having a privacy policy that does not mention the specific data types collected.
- Not setting `ITSAppUsesNonExemptEncryption`, causing the export compliance prompt on every upload.
- Including test/staging server URLs in the production build.

## Examples

### Review notes template (minimal)

```markdown
## Test Account
Email: reviewer@example.com
Password: Test1234

## Sensitive Features
1. Camera permission: Used for document scanning only.
   - Path: Home -> Documents -> Scan
   - If denied, allows file upload from photo library instead.

## Special Instructions
- First launch may take ~5 seconds to sync data.
- Premium features require sandbox IAP purchase.
- App does not use custom encryption (ITSAppUsesNonExemptEncryption = NO).
```
