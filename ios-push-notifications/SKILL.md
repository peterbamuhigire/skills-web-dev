---
name: ios-push-notifications
description: APNs push notifications, rich notifications, notification extensions,
  background push, and notification categories for iOS. Use when implementing remote
  push notifications, UNUserNotificationCenter, UNNotificationServiceExtension...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# iOS Push Notifications

<!-- dual-compat-start -->
## Use When

- APNs push notifications, rich notifications, notification extensions, background push, and notification categories for iOS. Use when implementing remote push notifications, UNUserNotificationCenter, UNNotificationServiceExtension...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ios-push-notifications` or would be better handled by a more specific companion skill.
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
## 1. Registration and Permission

```swift
// AppDelegate / App init
func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
) -> Bool {
    UNUserNotificationCenter.current().delegate = self
    // Auth BEFORE registering — some iOS versions ignore register without prior auth
    Task {
        let granted = try? await UNUserNotificationCenter.current()
            .requestAuthorization(options: [.alert, .badge, .sound, .provisional])
        if granted == true {
            await MainActor.run { application.registerForRemoteNotifications() }
        }
    }
    return true
}

// Token received — send to server every launch, not just first
func application(
    _ application: UIApplication,
    didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data
) {
    let token = deviceToken.map { String(format: "%02.2hhx", $0) }.joined()
    Task { await MyPushTokenService.shared.upload(token: token) }
}

func application(
    _ application: UIApplication,
    didFailToRegisterForRemoteNotificationsWithError error: Error
) {
    // Log but never crash — simulator always fails in older Xcode
    Logger.push.error("APNs registration failed: \(error)")
}
```

## 2. Critical Non-Obvious Rules

- `registerForRemoteNotifications()` must be called on the **main thread** — always wrap in `await MainActor.run`
- Token can change after backup restore, app reinstall, or OS update — send on **every cold launch**, not once
- `.provisional` authorization delivers silently to Notification Centre without prompting user — use as a trial ramp before requesting full permission
- iOS 16+: `.timeSensitive` interruption level bypasses Focus modes; requires the `com.apple.developer.usernotifications.time-sensitive` entitlement
- APNs token is a device+app+environment tuple — simulator tokens are sandbox-only and differ from device tokens
- TestFlight and ad-hoc builds use **sandbox** APNs (`api.sandbox.push.apple.com`); App Store builds use production — mismatch silently drops pushes
- Silent push requires `UIBackgroundModes: remote-notification` in Info.plist **and** `content-available: 1` in payload; missing either means no background wake
- System rate-limits silent pushes aggressively — do not design flows that require every silent push to be delivered

## 3. Foreground Notification Handling

```swift
// Without willPresent, all notifications are silently suppressed when app is active
extension AppDelegate: UNUserNotificationCenterDelegate {
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        // Explicit options required — passing [] suppresses banner
        completionHandler([.banner, .badge, .sound])
    }

    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse,
        withCompletionHandler completionHandler: @escaping () -> Void
    ) {
        defer { completionHandler() }   // must always be called
        let userInfo = response.notification.request.content.userInfo
        // Route to correct screen — check response.actionIdentifier for action buttons
        NotificationRouter.shared.handle(userInfo: userInfo, actionID: response.actionIdentifier)
    }
}
```

**Delegate timing trap:** If `delegate` is set after a notification arrives (e.g. set inside a lazy-loaded view controller), `willPresent` is never called for that notification. Always set in `didFinishLaunching`.

## 4. Silent (Background) Push

```swift
// Payload: { "aps": { "content-available": 1 } } — no alert/sound/badge
// Info.plist: UIBackgroundModes = ["remote-notification"]
func application(
    _ application: UIApplication,
    didReceiveRemoteNotification userInfo: [AnyHashable: Any],
    fetchCompletionHandler completionHandler: @escaping (UIBackgroundFetchResult) -> Void
) {
    // Hard 30-second budget — system terminates if you exceed it
    Task {
        do {
            try await SyncCoordinator.shared.performBackgroundSync(userInfo: userInfo)
            completionHandler(.newData)
        } catch {
            completionHandler(.failed)
        }
    }
}
```

APNs header rules for silent push:
- Set `apns-priority: 5` (not `10`) — priority 10 for silent push causes delivery rejection
- Set `apns-push-type: background` — required by APNs since iOS 13; missing causes drops on newer OS

## 5. Rich Notifications — UNNotificationServiceExtension

```swift
// Separate target: File > New > Target > Notification Service Extension
// Payload must include "mutable-content": 1 — without it this extension never fires
// Extension has its own sandbox — cannot access main app's Keychain without App Groups
class NotificationService: UNNotificationServiceExtension {
    var contentHandler: ((UNNotificationContent) -> Void)?
    var bestAttemptContent: UNMutableNotificationContent?

    override func didReceive(
        _ request: UNNotificationRequest,
        withContentHandler contentHandler: @escaping (UNNotificationContent) -> Void
    ) {
        self.contentHandler = contentHandler
        bestAttemptContent = request.content.mutableCopy() as? UNMutableNotificationContent

        guard
            let urlString = request.content.userInfo["image_url"] as? String,
            let url = URL(string: urlString)
        else {
            contentHandler(request.content)
            return
        }

        URLSession.shared.downloadTask(with: url) { [weak self] tempURL, _, error in
            guard let self else { return }
            guard let tempURL, error == nil,
                  let attachment = try? UNNotificationAttachment(
                      identifier: UUID().uuidString,
                      url: tempURL,
                      options: [UNNotificationAttachmentOptionsTypeHintKey: kUTTypeJPEG]
                  )
            else {
                self.contentHandler?(self.bestAttemptContent ?? request.content)
                return
            }
            self.bestAttemptContent?.attachments = [attachment]
            self.contentHandler?(self.bestAttemptContent ?? request.content)
        }.resume()
    }

    override func serviceExtensionTimeWillExpire() {
        // ~30s budget — system calls this before killing; deliver whatever you have
        contentHandler?(bestAttemptContent ?? UNNotificationContent())
    }
}
```

**App Groups gotcha:** If the extension needs to write data the main app reads (e.g. badge counts, analytics), configure a shared App Group container. The extension runs in a separate process with its own container by default.

**Attachment file persistence:** The system moves the downloaded file to a new location after delivery. Store the attachment identifier if you need to look it up later — the original temp URL is gone.

## 6. Notification Categories and Actions

```swift
// Must be registered before any notification with that category arrives
// Best practice: register in didFinishLaunching unconditionally
func registerNotificationCategories() {
    let replyAction = UNTextInputNotificationAction(
        identifier: "REPLY",
        title: "Reply",
        options: [],
        textInputButtonTitle: "Send",
        textInputPlaceholder: "Message…"
    )

    let archiveAction = UNNotificationAction(
        identifier: "ARCHIVE",
        title: "Archive",
        options: [.destructive]   // shown in red
    )

    let viewAction = UNNotificationAction(
        identifier: "VIEW",
        title: "View",
        options: [.foreground]    // brings app to foreground
    )

    let messageCategory = UNNotificationCategory(
        identifier: "MESSAGE",
        actions: [replyAction, viewAction, archiveAction],
        intentIdentifiers: [INSendMessageIntent.intentIdentifiers],   // Siri suggestions
        options: [.customDismissAction]   // fires didReceive on dismiss too
    )

    UNUserNotificationCenter.current().setNotificationCategories([messageCategory])
}

// In didReceive response:
switch response.actionIdentifier {
case "REPLY":
    let text = (response as? UNTextInputNotificationResponse)?.userText ?? ""
    await MessageService.shared.reply(text: text, to: notificationID)
case "ARCHIVE":
    await MessageService.shared.archive(notificationID)
case UNNotificationDefaultActionIdentifier:
    // Tap on notification body
    NotificationRouter.shared.navigate(to: notificationID)
case UNNotificationDismissActionIdentifier:
    // Requires .customDismissAction option on category
    Analytics.track(.notificationDismissed)
default:
    break
}
```

## 7. UNNotificationContentExtension (Custom UI)

```swift
// Separate target: Notification Content Extension
// Info.plist keys (under NSExtension > NSExtensionAttributes):
//   UNNotificationExtensionCategory: "MESSAGE"  (or array of strings)
//   UNNotificationExtensionInitialContentSizeRatio: 0.5  (height = width * ratio)
//   UNNotificationExtensionDefaultContentHidden: true  (hides default system UI)
//   UNNotificationExtensionUserInteractionEnabled: true  (enables touches in view)

class NotificationViewController: UIViewController, UNNotificationContentExtension {
    @IBOutlet weak var titleLabel: UILabel!
    @IBOutlet weak var bodyLabel: UILabel!

    func didReceive(_ notification: UNNotification) {
        let content = notification.request.content
        titleLabel.text = content.title
        bodyLabel.text = content.body
        // Populate from content.userInfo for rich data
    }

    func didReceive(
        _ response: UNNotificationResponse,
        completionHandler completion: @escaping (UNNotificationContentExtensionResponseOption) -> Void
    ) {
        switch response.actionIdentifier {
        case "REPLY":
            // Handle inline — do not forward to app
            completion(.doNotDismiss)   // keep UI visible, update it
        default:
            // Forward to app's didReceive(_:UNNotificationResponse:)
            completion(.dismissAndForwardAction)
        }
    }
}
```

`UNNotificationContentExtensionResponseOption` values:
- `.doNotDismiss` — stay visible (update UI for inline replies)
- `.dismiss` — remove without opening app
- `.dismissAndForwardAction` — remove and call app delegate's `didReceive`

## 8. APNs Payload Structure

```json
{
    "aps": {
        "alert": {
            "title": "New message",
            "subtitle": "From Alice",
            "body": "Hey, are you free tonight?"
        },
        "badge": 3,
        "sound": "default",
        "category": "MESSAGE",
        "content-available": 1,
        "mutable-content": 1,
        "thread-id": "conversation-abc123",
        "interruption-level": "active",
        "relevance-score": 0.8
    },
    "image_url": "https://cdn.example.com/photo.jpg",
    "conversation_id": "abc123"
}
```

Key field notes:
- `mutable-content: 1` — triggers `UNNotificationServiceExtension`; without it the extension is bypassed
- `thread-id` — groups notifications in Notification Centre; use conversation or entity IDs
- `interruption-level`: `passive` (no sound/screen wake), `active` (default), `time-sensitive` (Focus bypass), `critical` (requires Apple approval, always sounds)
- `relevance-score`: 0.0–1.0; higher scores surface the notification in the notification summary
- Custom keys at the root level (not inside `aps`) are passed through in `userInfo`

## 9. Entitlements and Capabilities

| Entitlement | How to Add | When Required |
|---|---|---|
| `aps-environment: development` | Xcode auto-adds on debug | Debug/simulator builds |
| `aps-environment: production` | Xcode auto-adds on release | App Store / TestFlight |
| Push Notifications capability | Target > Signing & Capabilities | All push |
| `com.apple.developer.usernotifications.time-sensitive` | Capabilities pane | `time-sensitive` interruption level |
| `com.apple.developer.usernotifications.critical-alerts` | Apple Developer portal request | Critical alerts (requires justification) |

**Common mismatch:** Provisioning profile generated before Push Notifications capability was added will silently fail. Regenerate profile after adding the capability.

## 10. Token Lifecycle and Server Strategy

```swift
// Client: upload token with metadata
struct PushTokenPayload: Encodable {
    let token: String
    let userID: String
    let bundleID: String
    let environment: String    // "sandbox" or "production"
    let appVersion: String
    let osVersion: String
}

// Server token management rules:
// - Store: token + userID + environment + updatedAt
// - On APNs HTTP/2 response 410 (Unregistered): delete token immediately
// - On APNs HTTP/2 response 400 BadDeviceToken: log and delete — app was uninstalled
// - On APNs HTTP/2 response 400 TopicDisallowed: wrong environment endpoint
// - Never treat a token as permanent — refresh on every app launch
// - One user can have multiple tokens (multiple devices)
```

APNs HTTP/2 authentication: prefer **auth keys (.p8)** over certificates (.p12). Keys never expire, work across all App IDs in a team, and require a single key for sandbox + production.

## 11. Testing Push Notifications

**Simulator (iOS 16+):**
```bash
# Drag .apns file onto simulator, or:
xcrun simctl push booted com.example.MyApp payload.apns
```

Minimal `.apns` file:
```json
{
    "aps": { "alert": { "title": "Test", "body": "Hello" } },
    "Simulator Target Bundle": "com.example.MyApp"
}
```

**Device testing:**
- Use APNs auth key (p8) via Push Notifications Tool (Mac App Store) or Knuff
- Direct HTTP/2: `POST https://api.sandbox.push.apple.com/3/device/{token}`
- Required headers: `apns-topic` (bundle ID), `apns-push-type`, `authorization` (JWT from p8 key)

**JWT for APNs auth key:**
```
Header: { "alg": "ES256", "kid": "KEY_ID" }
Payload: { "iss": "TEAM_ID", "iat": <now> }
Signed with p8 private key — valid for 1 hour, rotate before expiry
```

## 12. Anti-Patterns

| Anti-Pattern | Consequence | Fix |
|---|---|---|
| Set `delegate` after `didFinishLaunching` | `willPresent` never fires for early notifications | Set in `didFinishLaunching`, before any push arrives |
| Register for remote notifications before auth grant | Ignored on some iOS versions | Auth first, register in auth completion |
| Store token only on first launch | Stale token when token rotates | Upload on every cold launch |
| Omit `mutable-content: 1` | Service extension never fires | Always include for rich/encrypted push |
| Skip `serviceExtensionTimeWillExpire` | Notification silently lost if download slow | Always implement with bestAttemptContent fallback |
| Use production endpoint for sandbox builds | Push never delivered; no error | Match endpoint to `aps-environment` entitlement |
| Use `apns-priority: 10` for silent push | APNs rejects or throttles | Use `apns-priority: 5` + `apns-push-type: background` |
| Ignore 410 from APNs | Server keeps sending to dead tokens, wastes quota | Delete token immediately on 410 |
| Share Keychain item without App Group | Extension cannot read main app secrets | Add App Group; use shared container |
| Forget `apns-push-type` header | Delivery drops on iOS 13+ | Always set (`alert`, `background`, `voip`, etc.) |

## 13. Checklist

- [ ] `UNUserNotificationCenter.current().delegate = self` set in `didFinishLaunching` before any notification can arrive
- [ ] `requestAuthorization` called before `registerForRemoteNotifications`
- [ ] `registerForRemoteNotifications()` wrapped in `await MainActor.run`
- [ ] Token uploaded to server on every cold launch, not just first install
- [ ] `willPresent` delegate returns `.banner` (or desired options) for foreground display
- [ ] `didReceive response` routes tap to correct screen and calls `completionHandler()`
- [ ] `mutable-content: 1` in payload for any notification using service extension
- [ ] `serviceExtensionTimeWillExpire` delivers `bestAttemptContent` fallback
- [ ] `UIBackgroundModes: remote-notification` in Info.plist for silent push
- [ ] `apns-priority: 5` and `apns-push-type: background` for silent push payloads
- [ ] `aps-environment` entitlement matches build configuration (debug = development)
- [ ] APNs 410 response triggers immediate server-side token deletion
- [ ] Notification categories registered unconditionally in `didFinishLaunching`
- [ ] App Group container configured if service extension shares data with main app
- [ ] Provisioning profile regenerated after Push Notifications capability added
