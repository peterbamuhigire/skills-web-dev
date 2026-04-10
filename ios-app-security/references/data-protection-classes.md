# Data Protection Classes

How iOS per-file encryption works and how to pick the right protection class for app files, databases, and caches.

## iOS Data Protection Overview

Data Protection is iOS's per-file encryption feature. Each protected file on disk is encrypted with a file key, which is itself wrapped by a class key derived from the device passcode and the hardware UID baked into the Secure Enclave. When the device is locked, the class key for the strictest classes is evicted from memory and the files become unreadable until the user unlocks again.

Two properties follow from this design:

- **No passcode, no protection.** A device without a passcode cannot produce strong class keys. Passcode-less devices effectively fall back to the `none` class.
- **Secure Enclave bound.** Files protected at boot cannot be read by extracting the flash chip; decryption requires the SEP to participate. This is what makes `.complete` meaningful.

## The Four Protection Classes

| Class | File API constant | Readable before first unlock? | Readable while locked? |
|-------|-------------------|-------------------------------|------------------------|
| Complete | `.completeFileProtection` | No | No |
| Complete Unless Open | `.completeFileProtectionUnlessOpen` | No | Only if file handle opened while unlocked |
| Complete Until First User Authentication | `.completeFileProtectionUntilFirstUserAuthentication` | No | Yes, after first unlock |
| None | `.noFileProtection` | Yes | Yes |

### Complete

Strongest class. The file is unreadable at all times except when the device is currently unlocked. Background tasks running while locked cannot touch the file. Use for the most sensitive personal data: medical records, identity documents, financial transaction history.

### Complete Unless Open

A relaxation for processes that must keep a file open across a lock event. If your app opens the file while the device is unlocked, the file handle remains usable after the device locks. A new open against the locked device will fail. Use for audio recorders, long uploads, or location log writers that must continue running when the screen sleeps.

### Complete Until First User Authentication

The modern default. Files are inaccessible between boot and the first unlock, but readable thereafter, including after the user re-locks. This is the right class for most application data: your SwiftData store, cached API responses, user preferences. Background tasks (Background App Refresh, background URLSession) can read these files as long as the user has unlocked at least once since boot.

### None

No encryption beyond the normal file system. Almost never the right answer. Deliberately choose `none` only for files that must be readable before first unlock for very narrow reasons (e.g. crash reports written by a crash handler that runs before the file system is unlocked).

## Setting a File's Protection Class

When creating a file:

```swift
import Foundation

func writeSensitive(_ data: Data, to url: URL) throws {
    try data.write(to: url, options: [.completeFileProtection])
}
```

The `Data.write(to:options:)` options map directly to the protection classes:

- `.completeFileProtection`
- `.completeFileProtectionUnlessOpen`
- `.completeFileProtectionUntilFirstUserAuthentication`
- `.noFileProtection`

For existing files or directories, use `FileManager`:

```swift
let attributes: [FileAttributeKey: Any] = [
    .protectionKey: FileProtectionType.complete
]
try FileManager.default.setAttributes(attributes, ofItemAtPath: url.path)
```

Setting the protection key on a directory applies it to new files created inside the directory, not to existing files. Set it both at directory creation and on each new file explicitly if you want to be sure.

## Default Protection

As of iOS 7, files created in the app's container default to `.completeFileProtectionUntilFirstUserAuthentication`. This default is sensible for most apps and you generally do not need to override it. Be explicit only when you need a stronger class or when you need `unlessOpen` semantics for background writers.

Files in `/tmp` and `Caches` follow the same default unless you opt out.

## Choosing a Class

Match the class to what has to work while the device is locked or backgrounded:

| Need | Class |
|------|-------|
| Display sensitive medical notes only while the user is looking | `.complete` |
| Log workout data while phone is in a pocket (screen locked) | `.completeUnlessOpen` (open before lock) |
| Sync API data in the background via BGTaskScheduler | `.completeUntilFirstUserAuthentication` |
| Store an encryption key file read only when the user is active | `.complete` |
| Serve widget data while locked | `.completeUntilFirstUserAuthentication` |

## Detecting Unlock State

Background code can check whether the protection class it relies on is currently available:

```swift
if UIApplication.shared.isProtectedDataAvailable {
    // Safe to read .complete files
}
```

Subscribe to lifecycle notifications to prepare for lock and unlock transitions:

```swift
NotificationCenter.default.addObserver(
    forName: UIApplication.protectedDataWillBecomeUnavailableNotification,
    object: nil,
    queue: .main
) { _ in
    // Device is about to lock — close open handles to .complete files
}

NotificationCenter.default.addObserver(
    forName: UIApplication.protectedDataDidBecomeAvailableNotification,
    object: nil,
    queue: .main
) { _ in
    // Device unlocked — safe to open .complete files again
}
```

On macOS Catalyst and visionOS, these notifications are not meaningful; gate the observers on `#if os(iOS)`.

## Core Data and Data Protection

Core Data stores inherit protection from the options passed at persistent store setup. Use the `NSPersistentStoreFileProtectionKey` option:

```swift
let description = NSPersistentStoreDescription(url: storeURL)
description.setOption(FileProtectionType.complete as NSObject,
                      forKey: NSPersistentStoreFileProtectionKey)
container.persistentStoreDescriptions = [description]
```

If you pick `.complete`, be aware that background fetches after device lock will fail until the user unlocks again.

## SQLite and SwiftData

SwiftData uses a SQLite file under the hood. Apply the protection class to the SQLite file at container setup:

```swift
let configuration = ModelConfiguration(
    "MainStore",
    schema: Schema([MyModel.self]),
    url: storeURL,
    allowsSave: true
)
// SwiftData respects the file's protection class set via FileManager.
try FileManager.default.setAttributes(
    [.protectionKey: FileProtectionType.completeUntilFirstUserAuthentication],
    ofItemAtPath: storeURL.path
)
```

For column-level encryption — e.g. encrypting a single credit card number column inside SQLite — Data Protection alone is insufficient and you should layer SQLCipher, or encrypt the specific column values with a Keychain-held key before insert.

## Caches Directory

`Caches` defaults to `.completeUntilFirstUserAuthentication` on modern iOS but is subject to purging by the system under memory pressure. Two consequences:

- Do not store anything in `Caches` you cannot rebuild. The OS can delete cache contents silently.
- If you cache sensitive data (thumbnails of private photos, decoded API responses with PII), set `.complete` explicitly and accept the background-read constraint.

## Backups

iTunes and Finder backups come in two flavours:

- **Encrypted** — the user chose a backup password; file contents are re-encrypted under that password before leaving the device.
- **Unencrypted** — file contents leave the device in the clear, though some items are still excluded (e.g. Keychain items marked `ThisDeviceOnly`).

You cannot force the user to encrypt their backups. Treat any file you write as potentially present in an unencrypted backup unless:

- It lives in a location excluded from backup (`isExcludedFromBackup` URL resource value set to `true`), or
- It is in the Keychain with a `ThisDeviceOnly` accessibility class.

To exclude a file from backup:

```swift
var url = fileURL
var values = URLResourceValues()
values.isExcludedFromBackup = true
try url.setResourceValues(values)
```

Use backup exclusion for: large caches (saves user bandwidth), derivable data (thumbnails, downloaded media), and especially sensitive files you want to stay on-device only even when combined with `.complete` protection.

## Anti-Patterns

- **Writing Documents files with `.noFileProtection`.** Never appropriate in an app that handles any personal data.
- **Assuming Data Protection defends against an attacker with root on a jailbroken device.** It does not. Data Protection protects against offline extraction from a locked device, not against a compromised OS.
- **Storing secrets in `Caches`** under the assumption the class is always `.complete`. It is not, by default, and caches can be purged.
- **Forgetting to re-apply protection on migrated files.** When you move a file from one store to another, the destination may not inherit the source's protection class. Set it explicitly.
- **Using `.complete` and then wondering why background sync fails.** Use `.completeUntilFirstUserAuthentication` for files a background task must read.
- **Relying on Data Protection for backup secrecy.** An unencrypted backup can expose protected files to a computer the device trusts. Exclude truly sensitive files from backup.

## Cross-References

- `keychain-secure-enclave.md` — for small secrets and for keys that unlock larger protected files.
- `ios-data-persistence` skill — SwiftData and repository patterns where protection classes are wired in.
- `code-signing-entitlements.md` — app groups share files across targets; protection still applies.
- `runtime-tamper-detection.md` — protection classes cannot help on a compromised OS, so pair with runtime checks on high-value apps.
