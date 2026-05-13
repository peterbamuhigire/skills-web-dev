# ATS and Certificate Pinning

App Transport Security baseline, SPKI-hash certificate pinning on `URLSession`, pin rotation, and WebView pinning.

## App Transport Security

ATS is iOS's HTTPS baseline. Unless you opt out, `URLSession`, `WKWebView`, and any Foundation networking API refuse plain HTTP and weak TLS configurations. The baseline includes:

- TLS 1.2 or higher.
- Forward secrecy via ECDHE key exchange.
- Strong symmetric ciphers (AES-128 or AES-256 with GCM or CCM).
- SHA-2 certificate signatures.
- No self-signed or CA-pinned-but-untrusted root certificates.

For a new app targeting a modern backend, ATS needs zero configuration — it just works. Every exception you add widens the attack surface, so treat the default as sacrosanct.

## ATS Configuration

`Info.plist` exceptions live under `NSAppTransportSecurity`. Use them sparingly and scope them tightly.

Good — exception scoped to one legacy domain that you own and plan to retire:

```xml
<key>NSAppTransportSecurity</key>
<dict>
  <key>NSExceptionDomains</key>
  <dict>
    <key>legacy.example.com</key>
    <dict>
      <key>NSExceptionMinimumTLSVersion</key>
      <string>TLSv1.2</string>
      <key>NSIncludesSubdomains</key>
      <false/>
    </dict>
  </dict>
</dict>
```

Bad — blanket disable:

```xml
<key>NSAppTransportSecurity</key>
<dict>
  <key>NSAllowsArbitraryLoads</key>
  <true/>
</dict>
```

If a release build ships with `NSAllowsArbitraryLoads = true`, assume any attacker on the network can read and modify traffic.

For media content specifically, `NSAllowsArbitraryLoadsInMedia` and `NSAllowsArbitraryLoadsInWebContent` exist. Prefer not to use them; if you must, document the rationale in a code comment.

## Why Pin

TLS establishes a chain of trust from your server's certificate back to a root certificate in the device trust store. If any link in that chain is compromised — a mis-issued certificate, a rogue CA, a state-level MITM, a corporate proxy — the client will still accept the connection as valid. Certificate pinning hardcodes (in your app binary) an expected identity for specific hosts, so that an attacker with a valid-but-wrong certificate for your domain cannot impersonate your backend.

Pin only the endpoints that matter: authentication, payments, personal data. Pinning every image CDN adds operational pain without much marginal security.

## What to Pin

Pin the **Subject Public Key Info (SPKI) hash**, not the full certificate. The SPKI is the public key plus its algorithm identifier; the SHA-256 hash of the encoded SPKI is a 32-byte value that stays stable across certificate renewals as long as the same key pair is used.

| Pin target | Stable across renewal? | Compromise recovery |
|-----------|------------------------|---------------------|
| Full leaf certificate | No | Requires app update |
| Intermediate CA | Partially | Depends on your CA choices |
| SPKI hash (recommended) | Yes | Only rotate when key changes |

A cautious approach pins two SPKI hashes: the current production key and a backup key (the "next" key) whose certificate is pre-issued but not yet deployed. On rotation day, swap the backup to current and issue a new backup. Because both pins are already in the app, rotation is invisible to users.

## URLSession Delegate Pinning

The canonical place to implement pinning is `URLSessionDelegate.urlSession(_:didReceive:completionHandler:)` with an `NSURLAuthenticationMethodServerTrust` challenge. Validate the system trust first (so certificate expiry, hostname mismatches, and revocation still fail), then check the SPKI hash.

```swift
import CryptoKit
import Foundation

final class PinningDelegate: NSObject, URLSessionDelegate {
    // SHA-256 hashes of the SPKI of the pinned keys. Two entries for rotation.
    private let pinnedSPKIHashes: Set<Data> = [
        Data(base64Encoded: "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")!,
        Data(base64Encoded: "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=")!,
    ]
    private let pinnedHosts: Set<String> = ["api.example.com"]

    func urlSession(_ session: URLSession,
                    didReceive challenge: URLAuthenticationChallenge,
                    completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        guard challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust,
              let serverTrust = challenge.protectionSpace.serverTrust else {
            completionHandler(.performDefaultHandling, nil)
            return
        }

        let host = challenge.protectionSpace.host
        guard pinnedHosts.contains(host) else {
            // Not pinned — fall back to system trust evaluation.
            completionHandler(.performDefaultHandling, nil)
            return
        }

        // Step 1: verify the standard chain.
        var cfError: CFError?
        guard SecTrustEvaluateWithError(serverTrust, &cfError) else {
            logPinningFailure(host: host, reason: "system trust failed")
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        // Step 2: extract the leaf certificate and its public key.
        guard let chain = SecTrustCopyCertificateChain(serverTrust) as? [SecCertificate],
              let leaf = chain.first,
              let publicKey = SecCertificateCopyKey(leaf),
              let externalRep = SecKeyCopyExternalRepresentation(publicKey, nil) as Data? else {
            logPinningFailure(host: host, reason: "cannot extract SPKI")
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        // Step 3: hash and compare.
        let hash = Data(SHA256.hash(data: externalRep))
        if pinnedSPKIHashes.contains(hash) {
            completionHandler(.useCredential, URLCredential(trust: serverTrust))
        } else {
            logPinningFailure(host: host, reason: "SPKI mismatch")
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }

    private func logPinningFailure(host: String, reason: String) {
        // Forward to your security telemetry. Do not include full certificate bytes.
    }
}
```

Note: `SecKeyCopyExternalRepresentation` returns the raw key bytes, not a fully-formed SPKI (which includes an ASN.1 AlgorithmIdentifier prefix). For interoperability with server-side SPKI pinning tools, you may need to prepend the correct ASN.1 header per key type. Decide on one representation and stick to it across the app and tooling.

Wire the delegate into your `URLSession`:

```swift
let session = URLSession(configuration: .ephemeral,
                         delegate: PinningDelegate(),
                         delegateQueue: nil)
```

## Pin Rotation Strategy

A safe rotation runs like this:

1. Today's app has pins `[A, B]` where `A` is the live key and `B` is the planned next key.
2. Generate key `B` in advance, obtain a certificate for it, but keep it offline.
3. On rotation day, deploy the new certificate (with key `B`) on the backend.
4. Users on the current app continue to work because `B` is already in the pin set.
5. In the next app release, pins become `[B, C]` where `C` is the new planned next key.

Never ship with a single pin — an emergency rotation will lock every user out.

## Alamofire

If you already use Alamofire, it has a `ServerTrustManager` with `PublicKeysTrustEvaluator` and `PinnedCertificatesTrustEvaluator`:

```swift
let evaluators: [String: ServerTrustEvaluating] = [
    "api.example.com": PublicKeysTrustEvaluator(performDefaultValidation: true,
                                                 validateHost: true)
]
let trustManager = ServerTrustManager(evaluators: evaluators)
let session = Session(configuration: .default, serverTrustManager: trustManager)
```

Alamofire reads the pinned public keys from certificates bundled in the app at specified paths. Same rotation rules apply: bundle two certificates covering current and next keys.

## Debug Builds

Certificate pinning will block Charles Proxy, mitmproxy, and similar dev tools because those tools present their own root certificate. Allow pinning to be switched off in debug builds:

```swift
#if DEBUG
private let pinningEnabled = false
#else
private let pinningEnabled = true
#endif
```

Gate the pinning branch in your delegate on this flag. Make sure release builds compile out the debug branch entirely.

## WKWebView Pinning

`WKWebView` does not use your `URLSession`, so the delegate above does not protect web content. Implement `WKNavigationDelegate.webView(_:didReceive:completionHandler:)` for server-trust challenges and apply the same SPKI check:

```swift
func webView(_ webView: WKWebView,
             didReceive challenge: URLAuthenticationChallenge,
             completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
    // Same SPKI check as PinningDelegate.
}
```

Be aware: WKWebView runs content in a separate process (`WebContent.app`). Some navigations (subframes, ad trackers) may not trigger your delegate. Treat web-view pinning as best-effort and avoid rendering high-sensitivity content inside a web view when you can use a native screen instead.

## Bypass Risks

On a jailbroken device, MITM tools like SSL Kill Switch and Frida hooks can patch out the `SecTrustEvaluateWithError` call or your SPKI comparison, then feed any certificate through. Pinning alone cannot prevent this. Mitigations:

- Combine pinning with jailbreak detection (`jailbreak-detection.md`) and runtime tamper detection (`runtime-tamper-detection.md`).
- Compute and check the hash of your pinning code at startup and compare to a known value.
- For very high-stakes apps, call out to a native C function for the comparison and obfuscate the function name.

Acknowledge that a root-level attacker will win eventually. Your job is to make it expensive.

## Logging Pin Failures

A pin failure is either a real attack or a misconfiguration. Either way you want to know. Forward failed pin attempts to your security monitoring with: timestamp, host, client app version, OS version, geolocation accuracy (country only), and the reason code. Never include the raw certificate bytes in the log, and never include the user's credentials or request payload.

## Anti-Patterns

- **Disabling ATS globally** to get a single integration working. Scope the exception.
- **Leaving ATS exceptions in release** that were only needed in development.
- **Pinning a full certificate**, then facing an emergency rotation with a 7-day TestFlight review delay.
- **Pinning without a backup key**, with no way to rotate without bricking live users.
- **Ignoring pin failures in telemetry** — you lose the only warning signal that your backend was attacked.
- **Trusting pinning alone** on jailbroken devices.
- **Implementing pinning without calling `SecTrustEvaluateWithError` first** — you lose expiry and hostname validation.
- **Pinning the CA certificate** instead of the SPKI — tempting because the CA changes less often, but if the CA changes, all your downstream options disappear.

## Cross-References

- `jailbreak-detection.md` — rooting invalidates pinning; combine the two.
- `runtime-tamper-detection.md` — detect Frida hooks that patch out the pinning check.
- `ios-networking-advanced` skill — the production `URLSession` client where this delegate plugs in.
- `keychain-secure-enclave.md` — for storing the SPKI hashes themselves if you load them from a remote config.
- `privacy-manifest.md` — any telemetry you send for pin failures counts toward your collected data types.
