# Keychain and Secure Enclave

Defensive guidance for storing secrets on iOS. Covers Keychain item classes, accessibility attributes, access control flags, Secure Enclave key generation, and sharing Keychain data across app extensions.

## Where Secrets Belong

| Storage | Use For | Do Not Use For |
|---------|---------|----------------|
| `UserDefaults` / plist | Non-sensitive preferences, feature flags, UI state | Tokens, passwords, PII, encryption keys |
| File with Data Protection | User documents, cached records, attachments | Raw auth tokens (use Keychain) |
| Keychain | Auth tokens, refresh tokens, API keys, encryption keys, certificates, identities | Large blobs (use file + Keychain-held key) |
| Secure Enclave | Device-bound signing keys (ECC P-256) | Symmetric keys, large data, items needing backup sync |

Rule: tokens and credentials go in the Keychain. Large sensitive files go on disk with `.complete` protection, and the key that decrypts them goes in the Keychain. Signing material for device-bound auth goes in the Secure Enclave.

## Keychain Item Classes

The Keychain is a typed store. Pick the class that matches your use case:

- `kSecClassGenericPassword` — arbitrary secrets (most app use cases live here).
- `kSecClassInternetPassword` — web credentials with URL, port, protocol attributes.
- `kSecClassKey` — symmetric keys, asymmetric keys not stored as identities.
- `kSecClassCertificate` — X.509 certificates on their own.
- `kSecClassIdentity` — a certificate plus its private key (used for client TLS).

For auth tokens, OAuth refresh tokens, and API keys, `kSecClassGenericPassword` is almost always right.

## Accessibility Attributes

Every Keychain item carries an accessibility attribute that tells iOS when the item may be decrypted. Pass this explicitly in code even though iOS has a default; an explicit value is auditable.

| Attribute | Unlocked? | Survives restore to new device? | Notes |
|-----------|-----------|---------------------------------|-------|
| `kSecAttrAccessibleWhenUnlocked` | Only while unlocked | Yes | Background tasks after lock will fail |
| `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` | Only while unlocked | No | Recommended for auth tokens |
| `kSecAttrAccessibleAfterFirstUnlock` | After first unlock since boot | Yes | For data that must be readable by background tasks |
| `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly` | After first unlock since boot | No | Background-accessible, not restored to new device |
| `kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly` | Only with device passcode set | No | Strictest tier; item deleted if passcode removed |

Prefer `...ThisDeviceOnly` variants for auth material: a user restoring a backup to a new device should need to log in again, not inherit a live session.

The `kSecAttrAccessibleAlways` and `kSecAttrAccessibleAlwaysThisDeviceOnly` values are deprecated and must not be used.

## Storing a Token

A production-ready Keychain writer using `SecItemAdd` with an upsert pattern:

```swift
import Foundation
import Security

enum KeychainError: Error {
    case status(OSStatus)
    case invalidData
}

enum KeychainStore {
    static let defaultService = "app.auth"

    static func saveToken(_ token: String,
                          account: String = "auth_token",
                          service: String = defaultService) throws {
        guard let data = token.data(using: .utf8) else {
            throw KeychainError.invalidData
        }
        let baseQuery: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
        ]
        // Upsert: delete first, then add. Simpler than SecItemUpdate's merge rules.
        SecItemDelete(baseQuery as CFDictionary)

        var addQuery = baseQuery
        addQuery[kSecAttrAccessible as String] = kSecAttrAccessibleWhenUnlockedThisDeviceOnly
        addQuery[kSecValueData as String] = data

        let status = SecItemAdd(addQuery as CFDictionary, nil)
        guard status == errSecSuccess else { throw KeychainError.status(status) }
    }
}
```

## Retrieving, Updating, Deleting

```swift
extension KeychainStore {
    static func readToken(account: String = "auth_token",
                          service: String = defaultService) throws -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne,
        ]
        var item: CFTypeRef?
        let status = SecItemCopyMatching(query as CFDictionary, &item)
        switch status {
        case errSecSuccess:
            guard let data = item as? Data,
                  let token = String(data: data, encoding: .utf8) else {
                throw KeychainError.invalidData
            }
            return token
        case errSecItemNotFound:
            return nil
        default:
            throw KeychainError.status(status)
        }
    }

    static func deleteToken(account: String = "auth_token",
                            service: String = defaultService) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
        ]
        let status = SecItemDelete(query as CFDictionary)
        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw KeychainError.status(status)
        }
    }
}
```

On logout, always call `deleteToken`. On account switching, delete and re-add so the item keeps no stale attributes.

## Access Control with Biometrics

For secrets that should require Face ID, Touch ID, or device passcode at the moment of use, attach a `SecAccessControl` to the Keychain item instead of using the plain accessibility attribute. This binds the secret to the current enrolled biometric set and forces LocalAuthentication to prompt the user.

```swift
import LocalAuthentication

func saveHighValueSecret(_ secret: Data) throws {
    var error: Unmanaged<CFError>?
    guard let access = SecAccessControlCreateWithFlags(
        nil,
        kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly,
        [.biometryCurrentSet, .privateKeyUsage],
        &error
    ) else {
        throw error!.takeRetainedValue() as Error
    }

    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrService as String: "app.vault",
        kSecAttrAccount as String: "masterKey",
        kSecAttrAccessControl as String: access,
        kSecValueData as String: secret,
        kSecUseAuthenticationContext as String: LAContext(),
    ]
    SecItemDelete(query as CFDictionary)
    let status = SecItemAdd(query as CFDictionary, nil)
    guard status == errSecSuccess else { throw KeychainError.status(status) }
}
```

Flag choices:

- `.userPresence` — any enrolled biometric, with passcode fallback.
- `.biometryAny` — biometric only, any enrolled identity; passcode fallback allowed.
- `.biometryCurrentSet` — invalidates the item if the user adds or removes a biometric enrollment. Strongest binding for high-value secrets.
- `.devicePasscode` — passcode only.

See `ios-biometric-login` for the full LocalAuthentication flow.

## Secure Enclave Keys

The Secure Enclave Processor is a dedicated coprocessor that generates and holds ECC P-256 private keys that never leave the chip. You can sign data with the key, but you cannot export it. Pair with a challenge-response flow and the device becomes cryptographically bound to the user's account.

Why it matters: a stolen unlocked device cannot be cloned, and a stolen sealed device cannot sign without the biometric/passcode.

Limitations:

- Only ECC (`kSecAttrKeyTypeECSECPrimeRandom`) and only 256-bit keys.
- No encryption with the raw key; only `ecdsa-signature-*` and ECDH agreement.
- Not available on older devices without a SEP (practically, all shipping iOS 17 devices have one).

Generation:

```swift
enum SecureEnclaveError: Error { case create(CFError?) }

func createSigningKey(tag: String = "com.example.auth.key") throws -> SecKey {
    guard let access = SecAccessControlCreateWithFlags(
        nil,
        kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
        [.privateKeyUsage, .biometryCurrentSet],
        nil
    ) else { throw SecureEnclaveError.create(nil) }

    let attributes: [String: Any] = [
        kSecAttrKeyType as String: kSecAttrKeyTypeECSECPrimeRandom,
        kSecAttrKeySizeInBits as String: 256,
        kSecAttrTokenID as String: kSecAttrTokenIDSecureEnclave,
        kSecPrivateKeyAttrs as String: [
            kSecAttrIsPermanent as String: true,
            kSecAttrApplicationTag as String: tag.data(using: .utf8)!,
            kSecAttrAccessControl as String: access,
        ],
    ]

    var error: Unmanaged<CFError>?
    guard let key = SecKeyCreateRandomKey(attributes as CFDictionary, &error) else {
        throw SecureEnclaveError.create(error?.takeRetainedValue())
    }
    return key
}
```

Signing a backend challenge:

```swift
func sign(challenge: Data, with privateKey: SecKey) throws -> Data {
    var error: Unmanaged<CFError>?
    guard let signature = SecKeyCreateSignature(
        privateKey,
        .ecdsaSignatureMessageX962SHA256,
        challenge as CFData,
        &error
    ) as Data? else { throw error!.takeRetainedValue() as Error }
    return signature
}
```

Export the matching public key once at enrolment and send it to your backend. From then on, the backend verifies signatures and knows the caller is this device.

## Sharing Keychain Across App and Extensions

App extensions (share, widget, notification content) cannot read the container app's Keychain by default. To share a token, add a Keychain Access Group entitlement to both the app and the extensions:

1. Enable "Keychain Sharing" in the app target's Signing & Capabilities.
2. Add a group identifier, typically `$(AppIdentifierPrefix)app.shared`.
3. Add the same group to every extension target.
4. When saving, set `kSecAttrAccessGroup` to the group name.

```swift
var query: [String: Any] = [
    kSecClass as String: kSecClassGenericPassword,
    kSecAttrService as String: "app.auth",
    kSecAttrAccount as String: "auth_token",
    kSecAttrAccessGroup as String: "ABCDE12345.app.shared",
    kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly,
    kSecValueData as String: tokenData,
]
```

Note the accessibility change: a widget refreshing in the background cannot touch a `...WhenUnlocked` item after the device re-locks. Use `...AfterFirstUnlockThisDeviceOnly` for shared items that must work in the background, and accept the slightly weaker posture.

## Keychain and App Deletion

Historically, Keychain items survived app deletion, which caused stale credentials on reinstall. Modern iOS (iOS 10.3 and later) removes an app's Keychain items when the app is uninstalled, unless the items are in a shared access group used by another installed app. You should still delete items explicitly on logout — do not rely on uninstall behaviour.

Setting `kSecUseDataProtectionKeychain` to `true` places the item in the Data Protection Keychain, which is the modern default on iOS and is required for some modern attributes. New apps should pass it explicitly.

## iCloud Keychain Sync

`kSecAttrSynchronizable = true` opts an item into iCloud Keychain sync across the user's devices. For most app secrets this is the wrong choice: you usually want each device to have its own session. For items you do sync, accept that the attacker surface now includes iCloud account compromise, and never sync items that embed device-bound assumptions.

Synchronizable items must use an accessibility without `ThisDeviceOnly`.

## Migration Patterns

If you are moving from a less-secure store (`UserDefaults`, a plaintext file) to the Keychain:

1. On first launch after the upgrade, read the value from the old store.
2. If present, write it to the Keychain with the correct accessibility.
3. Delete the old store entry.
4. On subsequent launches, read only from the Keychain.

Add telemetry on migration failures; they are silent security holes otherwise.

## Anti-Patterns

- **Storing tokens in `UserDefaults`.** Plaintext in the app container.
- **Hardcoded API keys in source.** Every reverser will find them.
- **`kSecAttrAccessibleAlways`.** Deprecated. Use `...WhenUnlocked...`.
- **Omitting `ThisDeviceOnly`** on auth material that should not follow a backup restore.
- **Skipping delete-before-add.** `SecItemAdd` returns `errSecDuplicateItem` on conflict. Either handle that or delete first.
- **Storing large blobs in Keychain.** Keychain is for small secrets. Encrypt the blob, store the blob on disk with `.complete` protection, and store the key in Keychain.
- **Sharing `kSecAttrAccessibleWhenUnlocked`** items with a background extension and wondering why they fail after re-lock.
- **Leaving biometric-gated items without a fallback plan** when the user rotates biometrics — the item becomes unreadable. Wrap access and re-enrol on failure.

## Cross-References

- `data-protection-classes.md` — file-level protection for large blobs whose keys live in Keychain.
- `code-signing-entitlements.md` — Keychain Sharing entitlement and access groups.
- `ios-biometric-login` skill — LocalAuthentication flow and biometric fallbacks.
- `ios-data-persistence` skill — where repository code wires in the Keychain helpers.
