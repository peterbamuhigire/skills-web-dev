# Code Signing and Entitlements

Chain of trust, provisioning profiles, entitlement hygiene, App Attest, and CI signing key handling.

## Code Signing Overview

iOS code signing is a chain of trust rooted in Apple.

1. **Apple Root CA** is the ultimate trust anchor, pre-installed on every iOS device.
2. **Apple Developer Relations CA** issues certificates to developer accounts.
3. **Developer certificate** is your team's public key, signed by Apple. Private key lives in your keychain.
4. **App signature** is produced at build time by signing the Mach-O with the developer private key.
5. **Provisioning profile** bundles the signing certificate, declared entitlements, allowed devices (for development), and the app ID. It is itself signed by Apple.
6. **Device** verifies the app signature at install time and on every launch. Gatekeeper on macOS is the equivalent mechanism on Mac apps; iOS enforces signing via the kernel and the trust cache.

If any link breaks — certificate expired, entitlements modified post-signing, binary tampered — the app fails to launch. That is the baseline the rest of this guide builds on.

## Provisioning Profiles

A provisioning profile encodes:

- **Signing certificate identity** — which developer is allowed to sign this app.
- **App ID** — the reverse-DNS identifier (`com.example.myapp`), exact or wildcard.
- **Entitlements** — the capabilities the app is allowed to use.
- **Devices** — for development profiles, the UDIDs of devices allowed to run the build. Not present for App Store profiles.
- **Expiry date** — profiles expire and must be renewed.

Types:

- **Development** — for testing on listed devices via Xcode.
- **Ad Hoc** — distribute to listed devices outside the App Store.
- **App Store** — submission to the App Store.
- **Enterprise** — in-house distribution via the Apple Developer Enterprise Program.

Only the App Store path and controlled TestFlight/Enterprise paths are appropriate for production.

## Entitlements and Least Privilege

Entitlements grant your app capabilities beyond the default sandbox. Every entitlement is a promise, a risk, and a reviewer scrutiny point. The rule is blunt: **request only what you actively use**. A stale entitlement from an abandoned feature is a liability waiting to be exploited by a supply-chain attacker or a compromised developer credential.

### High-scrutiny entitlements

| Entitlement | What it does | Why to be careful |
|-------------|--------------|-------------------|
| `com.apple.developer.associated-domains` | Universal Links, web credentials | Must own the associated domain and serve AASA |
| `com.apple.developer.networking.vpn.api` | Network Extension VPN | Heavy review, must justify |
| `com.apple.developer.networking.HotspotConfiguration` | Join Wi-Fi programmatically | Attack vector if misused |
| `keychain-access-groups` | Share Keychain across targets | Every entry widens data sharing |
| `com.apple.developer.usernotifications.filtering` | Intercept notifications | Privacy implications |
| `com.apple.security.application-groups` | Shared container across targets | Bypasses per-target sandboxing |
| `com.apple.developer.in-app-payments` | Apple Pay | Requires merchant setup and review |
| `com.apple.developer.healthkit` | Read/write health data | Separate review, privacy labels |
| `com.apple.developer.icloud-services` | CloudKit containers | Be explicit about which containers |
| `com.apple.developer.devicecheck.appattest-environment` | App Attest | Gate behind backend verification |

Strip anything on this list you are not actually using before every release.

## App Groups and Shared Containers

App Groups let multiple targets (your main app, extensions, a sibling app) share a filesystem container and `UserDefaults` suite. Convenient for widgets that need to read cached data. The trade-off: anything in the shared container is accessible to every member of the group. A bug in your widget reading a token with lax handling leaks the token from the main app.

Mitigations:

- Use App Groups only for data that genuinely must be shared.
- Lock down tokens behind a Keychain access group instead of putting them in the shared `UserDefaults`.
- Apply Data Protection classes to files in the shared container.
- Audit extensions: each extension is a potential leak path.

## Universal Links vs URL Schemes

Custom URL schemes (`myapp://`) are **not authenticated**. Any app on the device can register the same scheme, and the system's resolution order is first-come. A hostile app can hijack `myapp://login/callback` and harvest tokens from an OAuth redirect.

Universal Links (`https://myapp.example.com/...`) are authenticated via the Apple App Site Association (AASA) file served over HTTPS from the domain. Only apps whose Team ID + bundle ID are listed in the AASA file can claim the link. Use Universal Links for anything security-sensitive, especially authentication callbacks.

The migration is usually:

1. Configure Associated Domains entitlement with `applinks:myapp.example.com`.
2. Host `/.well-known/apple-app-site-association` on the domain.
3. Switch your login flow to return a Universal Link.
4. Delete the custom URL scheme, or keep it only for non-sensitive deep links.

## Keychain Sharing Groups

See `keychain-secure-enclave.md` for code. The entitlement lives here:

```xml
<key>keychain-access-groups</key>
<array>
    <string>$(AppIdentifierPrefix)app.shared</string>
</array>
```

The `$(AppIdentifierPrefix)` placeholder expands to your Team ID at signing time, which binds the group to your team so other developers cannot read it.

## Info.plist Keys That Matter for Security

- **Usage descriptions** — every sensitive API (camera, microphone, location, contacts, photos, HealthKit, Bluetooth) requires a usage description string. Apple rejects apps missing these. Write user-facing copy, not engineering notes: "To let you scan payment cards" rather than "NSCameraUsageDescription".
- **`NSAllowsArbitraryLoads`** — must be `false` in production. If it is `true` anywhere in your release plist, treat it as a security incident.
- **`LSSupportsOpeningDocumentsInPlace`** — exposes files to other apps. Only enable if your app is genuinely a document editor.
- **`LSApplicationQueriesSchemes`** — lists URL schemes the app can probe with `canOpenURL`. Minimise; every entry is a hint to reverse engineers about what the app integrates with.
- **`UIFileSharingEnabled`** — exposes the Documents directory over iTunes/Finder. Only enable for apps that explicitly want this.

## App Attest

Apple's **App Attest** (iOS 14+) gives your backend cryptographic proof that a request came from a genuine instance of your app on an unmodified device. It pairs with a Secure Enclave key generated by the OS, not by your app, and Apple vouches for the attestation.

Workflow:

1. At first launch, call `DCAppAttestService.shared.generateKey()` to get a key ID.
2. Call `attestKey(_:clientDataHash:)` to produce an attestation object containing the public key and a signature from Apple.
3. Send the attestation to your backend. Backend verifies the signature against Apple's root and stores the public key.
4. For subsequent high-value requests, sign request payloads with the App Attest key via `generateAssertion(_:clientDataHash:)` and have the backend verify.

Use App Attest to gate:

- Account creation flows (stop mass fake accounts).
- Payment submission.
- Coupon redemption, promo claim, referral credits.

App Attest is not a replacement for user authentication. It proves the client is genuine; it does not prove who the user is.

## DeviceCheck

`DCDevice` (iOS 11+) offers two bits of per-device state your app can set and read via your backend. Typical use: mark a device as "already received a free trial" so the trial cannot be claimed twice across reinstalls. The bits are opaque and persist across reinstall within the same Apple ID. DeviceCheck is narrower than App Attest but useful for abuse mitigation.

## Signing Key Hygiene

Your developer signing key is the crown jewel. If stolen, an attacker can sign malware as you. Protect it:

- **Store signing keys in a secure keychain**, never committed to git. No `.p12` files in the repo. No base64-encoded certs in environment variables visible in CI logs.
- **Use app-specific signing identities in CI**, not shared developer credentials. Xcode Cloud, Fastlane Match with a private git repo + encryption, or GitHub Actions with a secure keystore are acceptable.
- **Rotate on departure.** When a developer leaves, revoke their certificate in App Store Connect immediately.
- **Monitor provisioning profile changes** — unexpected changes in production profiles are a supply-chain red flag.
- **Enable two-factor authentication** on the Apple Developer account. The Apple ID tied to signing is a high-value target.

For teams using Fastlane Match: the git repo holding encrypted certs and profiles is itself sensitive. Use a private, access-controlled repository, and use a strong passphrase that is not committed anywhere.

## Review Checklist

Before every release, walk through this list:

- [ ] Only entitlements the app actively uses are in the profile.
- [ ] No `NSAllowsArbitraryLoads = true` in any release Info.plist.
- [ ] Every sensitive-API usage description is present and user-friendly.
- [ ] Universal Links configured; custom URL schemes are not used for auth.
- [ ] App Attest integrated for any endpoint that awards money, credits, or account state.
- [ ] DeviceCheck bits used where abuse mitigation requires device-level state.
- [ ] Keychain access groups restricted to intended targets.
- [ ] App Groups used only where genuinely needed; sensitive items use Keychain, not shared plists.
- [ ] Signing certificates stored in CI's secure keychain, not in the repo.
- [ ] Two-factor authentication enforced on the Apple Developer team.
- [ ] Provisioning profile expiry dates monitored.

## Anti-Patterns

- **Over-broad entitlements** copied from another project.
- **Leaving `NSAllowsArbitraryLoads = true`** after a quick fix.
- **Custom URL schemes for OAuth callbacks** — use Universal Links.
- **Signing certs checked into git** — even "just for CI".
- **Skipping usage descriptions** — causes rejection and is a clear signal of sloppy handling of privacy.
- **Sharing App Groups with unrelated targets** — bloats the blast radius of any single compromise.
- **Not revoking departing developers' certificates** — orphan certs are a supply-chain risk.

## Cross-References

- `keychain-secure-enclave.md` — Keychain sharing uses the group entitlement defined here.
- `privacy-manifest.md` — privacy manifest declares required-reason APIs; entitlements tell iOS which capabilities exist.
- `data-protection-classes.md` — App Groups shared containers still honour Data Protection classes.
- `ats-cert-pinning.md` — ATS config lives in the same Info.plist as usage descriptions.
- `ios-project-setup` skill — xcconfig structure, signing identities, CI wiring.
- `app-store-review` skill — Apple review mapping and rejection recovery.
