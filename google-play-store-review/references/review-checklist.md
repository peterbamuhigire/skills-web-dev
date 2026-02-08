# Google Play Store Review Checklist - Critical First-Submission Items

Based on shipping many apps with high first-time approval rates, these are the non-negotiable items that matter most.

## 1. Policy Compliance - Instant Reject Triggers

### Restricted Content

- No gambling or sports betting unless properly licensed and documented.
- No illegal content. Even educational apps about drugs or weapons can be flagged.
- User-generated content (UGC) requires:
  - Active moderation (reviewers test reporting flows).
  - Age gating if 18+ content is possible.
  - Blocking and filtering that actually works.
- No deceptive behavior:
  - Fake notifications ("3 people viewed your profile").
  - Misleading claims ("You won a prize!").
  - Disguised ads (buttons that look like gameplay elements).

### Ad Compliance (Common Rejection Area)

```xml
<!-- REQUIRED: Ad network declarations -->
<meta-data
    android:name="com.google.android.gms.ads.APPLICATION_ID"
    android:value="ca-app-pub-xxxxxxxxxxxxxxxx~yyyyyyyyyy"/>

<!-- Interstitial ads MUST have visible close button -->
<!-- Rewarded ads MUST show timer/remaining time -->
<!-- Native ads MUST be clearly labeled "Ad" or "Sponsored" -->
```

Reviewer behavior:

1. Redirects to Play Store without user intent -> Rejected
2. Auto-opens browser -> Rejected
3. Invisible or missing close buttons -> Rejected

## 2. Data Safety Form - Top Rejection Reason

### Common Mismatches

| Form Says | App Actually Does | Result |
| --- | --- | --- |
| "No data collected" | Uses Firebase Analytics | Rejected |
| "Data not shared" | Uses Facebook SDK | Rejected |
| "Data encrypted" | Uses HTTP calls | Rejected |

### Validation Checklist

- List every SDK that collects data (analytics, crash reporting, ads, auth).
- Match permissions to declared data types.
- Ensure privacy policy covers:
  - What data is collected
  - How it is used
  - Third parties sharing (critical)
  - How to delete data
  - Privacy contact

Privacy policy URL must be:

- Public (no login)
- Accessible (200 OK)
- Accurate (app name and behavior match)
- Linked in-app (Settings or About)

## 3. Permissions Discipline - Runtime vs Declared

### Manifest Audit

```xml
<!-- BAD - Will get rejected -->
<uses-permission android:name="android.permission.READ_SMS" />
<uses-permission android:name="android.permission.RECEIVE_SMS" />

<!-- GOOD - Properly scoped -->
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission
    android:name="android.permission.ACCESS_BACKGROUND_LOCATION"
    android:maxSdkVersion="29" />

<!-- REQUIRED for certain permissions -->
<uses-permission
    android:name="android.permission.QUERY_ALL_PACKAGES"
    tools:ignore="QueryAllPackagesPermission" />
```

### Permission Request Patterns

1. Location permission -> show in-app justification before system dialog.
2. Camera permission -> request at point of use, not on launch.
3. Background location -> requires foreground service with notification.
4. SMS or Call Log -> requires special approval (almost never granted).

Reject triggers:

- Permission requested but feature does not use it.
- Feature works without permission (implies unused data collection).
- Background permission requested without foreground service.

## 4. Target SDK and Technical Hygiene

### SDK Requirements

```gradle
android {
    compileSdk 34
    targetSdk 34

    defaultConfig {
        minSdk 23
    }
}
```

Auto-reject if targetSdk is behind current requirements.

### Background Abuse Checks

```kotlin
// BAD - Continuous background work without notification
class BadService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        doHeavyWork()
        return START_STICKY
    }
}

// GOOD - Foreground service with notification
class GoodService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(NOTIFICATION_ID, createNotification("Processing..."))
        return START_NOT_STICKY
    }
}
```

Reviewers test:

- Wakelocks and CPU usage
- Excessive background network calls
- AlarmManager abuse
- JobScheduler misuse

## 5. Store Listing Accuracy

### Screenshot Reality Check

Ensure screenshots and videos match the shipped app:

- Feature X shown in listing exists in the app.
- UI elements are in the same position.
- Premium badges match actual IAP availability.
- "Free" claims reflect reality.
- Localized screenshots match the in-app language.

Reject triggers:

- Screenshots show features not in the app.
- Video preview shows different UI.
- "Before/after" results not achievable.
- Fake device frames or mockups.

### Description Red Flags

Bad:

- "Best app ever" or "100,000 downloads" (unverifiable)
- "Lose 10kg in 3 days" (health claims)
- "Free Netflix" (copyright infringement)
- "No ads forever" (but has ads)

Good:

- "Track your workouts" (accurate)
- "Sync with Google Fit" (verifiable)
- "Premium subscription available" (clear)

## 6. Monetization Compliance - IAP and Subscriptions

### Subscription Flow Must-Haves

- Price displayed before purchase button
- Clear terms and conditions link
- Refund and cancellation path
- Grace period handled (access until end of period)
- Restore purchases working

### Free Trial Traps

Wrong:

- "Free trial" that charges immediately
- Auto-renew without clear warning
- No way to cancel before renewal
- Price changes after trial without notice

Right:

- "Free trial, then $9.99/month"
- "Cancel anytime in Play Store settings"
- Reminder email before renewal
- Same price continues after trial

## 7. Testing Coverage - The Install Test

Critical paths reviewers verify:

1. Fresh install
   - Permissions requested properly
   - Login or signup works
   - Basic functionality without payment
   - Privacy policy accessible
2. Upgrade from previous version
   - Data migration works
   - Settings preserved
   - No new forced permissions
3. Deep link handling
   - URL opens app and correct screen
   - Invalid links handled gracefully
4. Purchase flow (if applicable)
   - Price loads
   - Purchase completes
   - Item delivered
   - Receipt saved

Recommended devices:

- Android 14 (latest)
- Android 11
- Low RAM device (2 GB)
- Tablet (if supported)

## 8. Age Rating and Content

### IARC Questionnaire Pitfalls

- UGC present -> answer must be Yes.
- Location shared with other users -> answer must be Yes.
- Ads present -> answer must be Yes.

Wrong rating can lead to suspension.

### COPPA Compliance (kids apps)

- No personal data collection
- No behavioral ads
- No external links
- Parental gate for purchases
- No Google Sign-In for under 13

## 9. App Integrity and Signing

Common signing issues:

- Upload key differs from previous version
- Play App Signing not enabled
- Version code lower than previous
- Package name changed

Always:

1. Enable Play App Signing
2. Keep upload keystore safe
3. Always increase version codes
4. Never change package name

## 10. Review Notes - Make Review Fast

Include:

- Test account credentials
- Step-by-step flows for sensitive features
- Explanation of permissions and background work
- Any startup delays or required setup
- Clear markers for premium features

Do not include:

- "Please approve quickly"
- Deadlines or pressure
- Vague instructions like "Test the app"

### Review Notes Template

```markdown
## Test Account
Email: reviewer@test.com
Password: Test1234

## Sensitive Features
1. Location permission: Used only for store locator.
   - Path: Home -> Find Stores
   - If denied, show manual zip code entry.

2. Background sync: Runs every 6 hours to update prices.
   - Notification: "Updating prices..."
   - Stops when app is killed.

## Special Instructions
- First launch may take 10 seconds to download catalog.
- Premium features marked with a star icon.
```

## Pre-Submission Checklist (15 Minutes)

```bash
./gradlew assembleRelease

# APK metadata
# Adjust path if needed
# aapt dump badging app-release.apk | grep -E "(package|sdkVersion|permission)"

# Manifest scan
# grep -r "uses-permission" app/src/main/AndroidManifest.xml

# Privacy policy live test
# curl -I https://yourapp.com/privacy.html
```

## Emergency Fix Protocol (If Rejected)

1. Read the rejection email carefully.
2. Fix only the specified issue.
3. Resubmit with a clear explanation of the fix.
4. Wait 24 to 48 hours before re-submitting again.

## Proven Success Rate Boosters

1. Use Internal Testing Track first.
2. Submit on Tuesday or Wednesday for faster reviews.
3. Keep APK under 100 MB.
4. Remove unused permissions.
5. Test with a reviewer mindset.

Key idea: most of the review is automated scanning. Avoid automated flags and make the human reviewer's job easy.