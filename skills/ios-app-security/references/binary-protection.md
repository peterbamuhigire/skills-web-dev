# Binary Protection

Reducing what attackers can learn and change when they have your `.ipa` on disk.

## What Attackers Can Do to Your IPA

An `.ipa` is a zipped app bundle containing a Mach-O binary, resources, and metadata. On a jailbroken device, or after decryption with off-the-shelf tools, the binary is fully inspectable. Typical reverse-engineering tooling:

- **`class-dump`** — lists Objective-C classes, selectors, properties, and protocol conformances. For any class bridged through Obj-C, the full method list is visible.
- **Hopper, Ghidra, IDA Pro** — disassemble Mach-O, reconstruct function boundaries, annotate cross-references. Skilled users can recognise Swift name-mangled symbols and rebuild call graphs.
- **`nm`, `otool`, `objdump`** — list exported symbols, imported symbols, linked libraries, and segments.
- **`strings`** — grep the binary for printable strings, which surfaces API hostnames, error messages, and any secret you typed as a literal.
- **Runtime tracing (Frida, lldb)** — attach to a running process, log method calls, replace implementations.

Design under the assumption that an attacker will run all of these. Your job is to make their findings less useful.

## Symbol Stripping

Unstripped Swift and Objective-C binaries contain function name symbols that line up directly with your source. Strip them in release builds so a reverser sees `sub_10004120` instead of `TokenVault.decryptMasterKey(with:)`.

In Xcode Build Settings for the Release configuration:

| Setting | Value |
|---------|-------|
| `DEPLOYMENT_POSTPROCESSING` | `YES` |
| `STRIP_INSTALLED_PRODUCT` | `YES` |
| `STRIP_STYLE` | `all` |
| `COPY_PHASE_STRIP` | `YES` |
| `STRIP_SWIFT_SYMBOLS` | `YES` |
| `DEAD_CODE_STRIPPING` | `YES` |
| `LLVM_LTO` | `YES` (or `Incremental`) |

Keep the generated `.dSYM` for crash symbolication — upload it to your crash reporter (App Store Connect, Firebase Crashlytics, Sentry) so your own crash reports remain readable, but the binary shipped to users is stripped.

## String Obfuscation

Literals in your source become plaintext strings in the `__TEXT,__cstring` section. A `strings` dump finds them in seconds. Mitigations:

- **Do not store secrets as strings.** API keys, encryption keys, and signing keys must not be literal strings in your code at all. Fetch them from the backend after authentication, or derive them from a user secret.
- **Simple XOR obfuscation for non-secret identifiers.** For strings like jailbreak probe paths, a tiny XOR with a per-string key raises the bar against casual grep:

```swift
enum Obf {
    // Expected plaintext recovered at runtime.
    static func decode(_ bytes: [UInt8], key: UInt8) -> String {
        String(bytes: bytes.map { $0 ^ key }, encoding: .utf8) ?? ""
    }
}

// Example: "/bin/bash" XOR 0x5A
private let binBash = Obf.decode([0x75, 0x38, 0x33, 0x34, 0x75, 0x38, 0x3b, 0x33, 0x38], key: 0x5A)
```

This defeats `strings`. It does not defeat a reverser who steps through `Obf.decode` in lldb. Use obfuscation to protect identifiers and error messages, not to hide keys.

## Swift vs Objective-C Exposure

Swift name-mangled symbols are less self-describing than Objective-C selectors. `class-dump` cannot enumerate Swift types the way it can Obj-C. The practical implication: **write security-sensitive code in pure Swift** (no `@objc`, no NSObject subclassing) so the names and layout are harder to recover.

- Mark security-sensitive Swift classes `final` and do not inherit from `NSObject`.
- Avoid `@objc` exposure on sensitive methods. If a selector is required for Cocoa interop, put it on a thin adapter layer and keep the real logic in pure Swift.
- Use `internal` or `private` access modifiers so the Swift access control machinery reduces surface even further.

## Compiler Flags

For any C or C++ code you bundle:

- `-fvisibility=hidden` — default to hidden symbol visibility; export only what needs to be.
- `-fstack-protector-strong` — stack canaries on non-trivial frames.
- `-D_FORTIFY_SOURCE=2` — compile-time buffer overflow checks where applicable.

Swift has no direct equivalent to `-fvisibility`, but access modifiers and whole-module optimisation serve a similar role.

## Dead Code Elimination

Enable `DEAD_CODE_STRIPPING = YES` to remove unused functions, classes, and resources from the final binary. This reduces the attack surface directly — attackers cannot exploit code that is not in the binary. Combined with LTO, dead-strip eliminates whole functions the optimiser can prove unreachable.

## Bitcode

Apple deprecated Bitcode in Xcode 14. New apps cannot submit Bitcode. Old guidance about disabling Bitcode for security-sensitive apps is obsolete — the flag is gone. If your project still has `ENABLE_BITCODE` in its settings, set it to `NO` and remove associated guidance from your build docs.

## Protection Against class-dump

`class-dump` walks the Objective-C runtime metadata sections in the Mach-O to list every class, category, and selector. You cannot prevent this for Obj-C code, but you can:

- Minimise the Obj-C surface — write new code in Swift.
- Bridge only what is necessary through `@objc`.
- Give security-sensitive classes and methods nondescript names (`Vault`, `Authority`) instead of `TokenDecryptionManager`.

A `class-dump` output of mostly SwiftUI views and view models is less informative than a tree of explicit security class names.

## Protection Against Runtime Inspection

See `runtime-tamper-detection.md` for the runtime defences: `ptrace(PT_DENY_ATTACH)`, sysctl `P_TRACED`, Frida detection. Binary protection and runtime protection work together — symbol stripping hides where to look, runtime checks punish attempting to look while the app is running.

## Anti-Tampering Hash

Compute a SHA-256 of your Mach-O `__TEXT` segment during a build phase script and embed the result in a resource or constant. At launch, hash the segment again and compare. A mismatch means the binary was modified. Respond by refusing to load secrets and reporting telemetry.

Implementation notes:

- The hash must be computed over a region that is stable post-linking. `__TEXT` is a reasonable choice; avoid `__DATA` which the loader will mutate.
- Inline the verification code. A named `verifyBinaryHash()` function is the first thing a patcher NOP's out.
- Store the expected hash obfuscated in `__DATA` rather than as a bare constant.

## Commercial Obfuscators

If you ship a banking, payment, or high-value target app, consider a commercial obfuscator. Options include:

- **Guardsquare iXGuard** — iOS-specific obfuscation, anti-tampering, runtime application self-protection.
- **Promon SHIELD** — in-app protection focused on banking and fintech.
- **Appdome** — no-code mobile app protection added at build time.

These tools rename symbols, flatten control flow, insert anti-debug checks throughout, and encrypt code segments. They add binary size, complicate crash symbolication, and cost real money. Use them when the threat model justifies them — do not reach for them on a consumer app.

## Resource Encryption

If you bundle sensitive non-code resources (a proprietary ML model, a configuration file, a cryptographic material blob), encrypt them at build time and decrypt into memory at use time. The decryption key can be derived from a backend response so the resource is unusable without a valid session.

Build phase script (conceptual):

```bash
# Encrypts a model file before it is copied into the bundle.
openssl enc -aes-256-gcm \
  -in Resources/model.mlpackage \
  -out Resources/model.enc \
  -K "$MODEL_KEY" -iv "$MODEL_IV"
```

At runtime, load the ciphertext, decrypt into a buffer, and feed the buffer to CoreML. Zeroise the buffer after use (`runtime-tamper-detection.md`).

Do not store the decryption key in the binary — fetch it from your backend or derive it from a user secret.

## Anti-Patterns

- **Hardcoded API keys**, even XOR-obfuscated. If the app can recover the key, so can the attacker.
- **Assuming the App Store encryption (FairPlay) is enough.** Tools exist to dump decrypted Mach-Os from memory on jailbroken devices.
- **Leaving debug-only strings in release.** "DEBUG: logging request to..." tells a reverser exactly where to hook.
- **Relying on Swift alone for secrecy.** Swift is less self-describing than Obj-C but it is not opaque.
- **Not stripping symbols**, leaving Swift demangled names visible to `nm`.
- **Obfuscating everything** at the cost of crash symbolication and build time — spend obfuscation budget on the few sensitive paths that matter.

## Cross-References

- `runtime-tamper-detection.md` — anti-debug and code integrity work with symbol stripping.
- `jailbreak-detection.md` — hides jailbreak probe strings from `strings` dumps via obfuscation.
- `ats-cert-pinning.md` — hides pinned hashes as bytes, not base64 strings, inside the binary.
- `code-signing-entitlements.md` — stripped, signed, entitlement-minimised binaries are the target end state.
- `ios-project-setup` skill — where these build settings actually live in Xcode and xcconfigs.
