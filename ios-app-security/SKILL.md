---
name: ios-app-security
description: Use when securing an iOS app — Keychain best practices with Secure Enclave,
  Data Protection classes for files, App Transport Security, certificate pinning via
  URLSession delegate, jailbreak detection, runtime tamper detection, binary protection
  (anti-debugging, anti-hooking), code signing and entitlements hygiene, and iOS 17+
  privacy manifest. Complements ios-development (general standards), ios-stability-solutions
  (crash patterns), and ios-biometric-login (LocalAuthentication).
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# iOS App Security

<!-- dual-compat-start -->
## Use When

- Use when securing an iOS app — Keychain best practices with Secure Enclave, Data Protection classes for files, App Transport Security, certificate pinning via URLSession delegate, jailbreak detection, runtime tamper detection, binary protection (anti-debugging, anti-hooking), code signing and entitlements hygiene, and iOS 17+ privacy manifest. Complements ios-development (general standards), ios-stability-solutions (crash patterns), and ios-biometric-login (LocalAuthentication).
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ios-app-security` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Security | iOS app threat model | Markdown doc per `skill-composition-standards/references/threat-model-template.md` covering Keychain, Data Protection, ATS, jailbreak | `docs/ios/threat-model-2026-04-16.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
## Purpose

Defensive security patterns for iOS apps built in Swift. Covers data-at-rest, data-in-transit, runtime integrity, binary protection, code signing hygiene, and privacy compliance so teams can ship apps that resist realistic attacks without over-investing in unwinnable battles.

## When to Use

Load this skill when:

- Starting a new iOS app that handles any sensitive data (tokens, PII, health, financial).
- Hardening an existing app ahead of a security review or penetration test.
- Preparing a banking, payment, health, or regulated app for App Store submission.
- Responding to a security incident or a red-team finding.
- Reviewing third-party SDKs and their impact on the app's attack surface.

Do not load this skill for:

- General Swift style questions (use `ios-development`).
- Crash prevention (use `ios-stability-solutions`).
- Adding a biometric gate alone (use `ios-biometric-login`).

## iOS Security Model Overview

The iOS security model is a defence-in-depth stack. An app on a stock, passcode-protected device is wrapped by several independent layers:

- **Secure Boot Chain.** Each stage of boot verifies the next stage's signature up to the kernel. This means unsigned kernels and root filesystems will not run on retail hardware unless the chain is broken (i.e. the device is jailbroken).
- **Code Signing.** Every executable page in memory must be signed by a valid Apple-issued certificate. Apps are signed with a developer certificate, which is itself signed by Apple. The kernel enforces this at page-fault time, which is why injected native code fails on non-jailbroken devices.
- **App Sandbox.** Each app runs inside a container with its own filesystem root. By default an app cannot read another app's files, cannot read most system files, and cannot open arbitrary network ports. Entitlements explicitly grant capabilities beyond the default.
- **Entitlements.** Signed claims attached to the app binary declaring which privileged APIs and shared containers the app may use. Treat every entitlement as a liability.
- **System Integrity Protection (SIP) / Sealed System Volume.** The system volume is cryptographically sealed and read-only. Apps cannot tamper with system binaries.
- **Data Protection.** Per-file encryption keyed from the device passcode and the hardware UID, rooted in the Secure Enclave.
- **Keychain.** A separate encrypted database for small secrets with its own access-control rules, including hardware-backed and biometric-gated items.
- **Secure Enclave Processor (SEP).** A dedicated coprocessor that generates and holds private keys that never leave the chip. Keys can be gated on biometrics or device passcode.

Your job as an app developer is not to reinvent these layers but to opt in correctly: store secrets in the right container, declare the minimum entitlements, turn on the strictest file protection class that still works for your use case, and add extra friction (pinning, tamper detection) only where the threat model justifies it.

## The 8 Security Domains

| # | Domain | Reference |
|---|--------|-----------|
| 1 | Keychain and Secure Enclave | `references/keychain-secure-enclave.md` |
| 2 | Data Protection Classes | `references/data-protection-classes.md` |
| 3 | ATS and Certificate Pinning | `references/ats-cert-pinning.md` |
| 4 | Jailbreak Detection | `references/jailbreak-detection.md` |
| 5 | Runtime Tamper Detection | `references/runtime-tamper-detection.md` |
| 6 | Binary Protection | `references/binary-protection.md` |
| 7 | Code Signing and Entitlements | `references/code-signing-entitlements.md` |
| 8 | Privacy Manifest | `references/privacy-manifest.md` |

## Data-at-Rest Security

The first question for any piece of data you persist is: **where does it belong?** There are three viable buckets on iOS:

- **UserDefaults** — for non-sensitive, non-secret preferences only. Treat it as plaintext. An attacker with physical access and a mounted backup can read it.
- **File system with Data Protection class** — for user documents, cached data, offline records. Pick the protection class based on whether the file must be readable while the device is locked.
- **Keychain** — for secrets: auth tokens, refresh tokens, API keys issued to this user, encryption keys for app-managed databases, cryptographic identities.

The rule of thumb is one sentence: **if losing it would embarrass you or harm the user, it belongs in the Keychain or in a file with at least `.complete` protection**. See `references/keychain-secure-enclave.md` and `references/data-protection-classes.md` for the implementation details.

Keychain items should always specify an accessibility attribute. The default on modern iOS is `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` for new apps, but you should pass it explicitly in code so reviewers can see the choice. The `ThisDeviceOnly` suffix is important: it prevents the item from being restored onto a different device from a backup, which is usually what you want for auth material.

For the highest bar, generate a signing key in the Secure Enclave and use it for challenge-response authentication against your backend. The private key never leaves the SEP, and you can gate its use on Face ID/Touch ID, so a stolen device with an unknown passcode cannot complete the handshake.

## Data-in-Transit Security

iOS enforces **App Transport Security (ATS)** by default: HTTPS only, TLS 1.2 or higher, strong ciphers, forward secrecy. Any exception you add to `Info.plist` is a gap you must justify. For new apps, add zero exceptions. If you must connect to a legacy system, scope the exception tightly to a single domain and file a ticket to remove it.

For high-value endpoints (authentication, payments, personal data) add **certificate pinning** on top of ATS. Pin the public key hash (SPKI hash), not the full certificate, so you can rotate certificates without pushing an app update. Implement pinning in your `URLSessionDelegate`'s `urlSession(_:didReceive:completionHandler:)` method; `WKWebView` requires its own pinning via `WKNavigationDelegate`. Pin two keys (current and next) so you can rotate without downtime.

Pinning is not absolute. A jailbroken device running SSL Kill Switch or a Frida hook will bypass your check. If your threat model requires resilience against that level of attacker, combine pinning with jailbreak detection and runtime integrity checks. See `references/ats-cert-pinning.md`.

## Runtime Protection

Runtime protection is about making your app unpleasant to modify while it is running, not about making modification impossible. Expect a determined attacker with a jailbroken device to win eventually. Your goal is to raise the cost and catch the casual attacker.

- **Jailbreak detection** combines several heuristics (file existence, URL schemes, sandbox probes, loaded dylib inspection). No single check is reliable, but a handful of independent checks used together make trivial bypass difficult. See `references/jailbreak-detection.md`.
- **Tamper detection** checks your own binary for modification, watches for injected dylibs (Frida, Cycript), detects method swizzling on security-critical selectors, and observes debugger presence. See `references/runtime-tamper-detection.md`.
- **Response strategy.** Prefer telemetry and graceful degradation over hard crashes. Report the finding, refuse to load secrets, disable sensitive features, and let the user know something is wrong. A hard crash ruins UX for the 0.01 % of users on a jailbroken device who are not attacking you.

## Binary Protection

Once an `.ipa` is on disk, it can be decrypted, disassembled, and examined. Assume attackers can read your Objective-C class list, your string literals, and your Swift symbol names. Plan accordingly:

- **Strip symbols.** Build Settings → `DEPLOYMENT_POSTPROCESSING=YES`, `STRIP_INSTALLED_PRODUCT=YES`, `STRIP_STYLE=all`. Keep the dSYM for crash symbolication.
- **Do not hardcode secrets.** API keys, signing keys, and encryption keys in the binary will be found. If you need a per-install secret, fetch it from your backend after authentication.
- **Obfuscate sparingly.** String obfuscation raises the bar against `strings` but does not stop a determined reverse engineer. Spend obfuscation budget on the two or three most sensitive functions, not on everything.
- **Prefer Swift over Objective-C** for security-sensitive code — Swift symbols are less self-describing than Objective-C selectors exposed by `class-dump`.

See `references/binary-protection.md`.

## Code Signing and Entitlements

Entitlements are capabilities. Each one you add is something an attacker, a buggy library, or a compromised credential can abuse. Apply the principle of least privilege ruthlessly:

- Only request entitlements you actually use today. Remove unused ones.
- Justify each Info.plist usage description (`NSCameraUsageDescription`, etc.) in human terms the user will see on the permission prompt.
- Never set `NSAllowsArbitraryLoads` to `true` in a release build.
- Prefer Universal Links over custom URL schemes — schemes can be claimed by other apps on the device.
- Use `App Attest` on iOS 14+ to have your backend verify the app binary is genuine before granting sensitive endpoints.

Keep signing keys out of your repository. CI should use app-specific signing identities stored in a secure keychain, not committed `.p12` files. See `references/code-signing-entitlements.md`.

## Privacy Compliance

As of May 2024, Apple requires every app and SDK that uses a "required reason" API to ship a **privacy manifest** (`PrivacyInfo.xcprivacy`). The manifest declares:

- Whether the app tracks users across apps and websites.
- Which data types the app collects, whether the data is linked to identity, whether it is used for tracking, and for what purposes.
- Which required-reason APIs the app calls (`UserDefaults`, file timestamp APIs, system boot time APIs, disk space APIs, active keyboard APIs) and why.

Your App Store Connect privacy labels must match the manifest. A mismatch is a common rejection cause. If you use third-party SDKs, you inherit their declared APIs and data types — review them before integrating.

App Tracking Transparency (ATT) is separate: if you use the `IDFA` or any cross-app tracking identifier, call `ATTrackingManager.requestTrackingAuthorization` and provide a usage description. See `references/privacy-manifest.md`.

## Security Audit Checklist

Run through this before every release. Every unchecked box is a finding to fix or an acknowledged risk to document.

### Data at rest

- [ ] No secret, token, or PII stored in `UserDefaults`.
- [ ] All auth tokens stored in Keychain with `...WhenUnlockedThisDeviceOnly` or stricter.
- [ ] No `kSecAttrAccessibleAlways` anywhere in the codebase.
- [ ] Keychain items removed on logout.
- [ ] Database files use at least `.complete` protection, or `.completeUntilFirstUserAuthentication` with documented justification.
- [ ] Cache directory does not contain sensitive data; if it must, protection is explicit.
- [ ] Secure Enclave used for device-bound signing keys where supported.

### Data in transit

- [ ] ATS enabled, no arbitrary loads exception in release.
- [ ] All exceptions scoped to specific domains with expiry dates.
- [ ] Certificate pinning on authentication and payment endpoints.
- [ ] SPKI hash pinning, not full certificate pinning.
- [ ] Two pins in place (current and next) for rotation.
- [ ] Pinning delegate covers `URLSession` and any `WKWebView`.

### Runtime and binary

- [ ] Jailbreak detection runs at launch for high-sensitivity apps.
- [ ] Jailbreak response is telemetry + degrade, not hard crash.
- [ ] `ptrace(PT_DENY_ATTACH)` enabled in release builds.
- [ ] Sensitive views blurred on `willResignActive`.
- [ ] Clipboard cleared on leaving screens that display secrets.
- [ ] `UIScreen.main.isCaptured` checked before rendering secrets.
- [ ] Symbols stripped in release build settings.
- [ ] No hardcoded API keys in the binary.

### Code signing and entitlements

- [ ] Only required entitlements present in provisioning profile.
- [ ] All usage description strings present and user-friendly.
- [ ] Universal Links configured; no reliance on custom URL schemes for auth.
- [ ] App Attest integrated with server for sensitive endpoints.
- [ ] Signing certificates stored in CI's secure keychain, not in git.

### Privacy

- [ ] `PrivacyInfo.xcprivacy` present and matches App Store Connect labels.
- [ ] All required-reason APIs declared with correct reason codes.
- [ ] Third-party SDK privacy manifests reviewed.
- [ ] `ATTrackingManager` prompt implemented if any tracking is used.
- [ ] No PII in crash logs or analytics events.

## Anti-Patterns

- **Storing auth tokens in UserDefaults.** UserDefaults is a plist in the app container. Treat it as plaintext.
- **Using `kSecAttrAccessibleAlways`.** Lets the item be read even while the device is locked. Almost never the right answer.
- **Disabling ATS globally with `NSAllowsArbitraryLoads`.** Removes the entire TLS baseline. Fix the endpoint instead.
- **Pinning a full certificate.** Certificate rotation will break your app. Pin the SPKI hash.
- **Single jailbreak check with an obvious name.** A `isJailbroken()` function is the first thing a reverser patches. Compose many independent checks and hide the orchestration.
- **Hard-crashing on jailbreak detection.** Ruins UX for legitimate users with exotic setups and tells attackers exactly where to patch.
- **Hardcoded API keys.** Every hardcoded secret will be extracted. Fetch secrets after authenticating.
- **Copy-pasting another app's privacy manifest.** Your data types, reason codes, and tracking status are specific to your app. A mismatch with App Store Connect is a rejection.
- **Entitlement sprawl.** Adding entitlements "just in case". Each one is a capability an attacker can misuse.
- **One weak third-party SDK.** A single closed-source analytics SDK can reverse every protection you added.

## References Index

- `references/keychain-secure-enclave.md` — Keychain classes, accessibility, Secure Enclave key generation, access control flags, sharing across app groups.
- `references/data-protection-classes.md` — The four protection classes, defaults, file APIs, `isProtectedDataAvailable`, Core Data options.
- `references/ats-cert-pinning.md` — ATS configuration, URLSession delegate SPKI pinning, rotation strategy, WKWebView pinning, bypass mitigation.
- `references/jailbreak-detection.md` — File, URL scheme, sandbox, dylib, and fork-based heuristics with a composed Swift helper and telemetry strategy.
- `references/runtime-tamper-detection.md` — `ptrace`, sysctl, code hash self-check, Frida detection, screen capture, pasteboard hygiene.
- `references/binary-protection.md` — Symbol stripping, string obfuscation trade-offs, compiler flags, resource encryption, commercial obfuscators.
- `references/code-signing-entitlements.md` — Chain of trust, provisioning profiles, entitlement review list, App Attest, CI signing key hygiene.
- `references/privacy-manifest.md` — `PrivacyInfo.xcprivacy` schema, required-reason APIs, ATT, SDK manifests, App Store Connect alignment.

## Cross-References

- **`ios-development`** — general Swift and architecture standards; this skill layers defensive patterns on top.
- **`ios-stability-solutions`** — crash prevention; stability and security are complementary (a crash is often a security bug, and a locked-down app that crashes constantly is not secure in practice).
- **`ios-biometric-login`** — `LAContext`, Face ID/Touch ID integration; cross-referenced from Keychain access control and Secure Enclave key gating.
- **`ios-networking-advanced`** — production `URLSession` client where pinning is wired in; this skill specifies the pinning policy, that skill shows where it plugs in.
- **`ios-data-persistence`** — repository pattern over SwiftData/SQLite; this skill specifies the protection class those stores must use.
- **`app-store-review`** — Review Guidelines, privacy labels, TestFlight; the privacy manifest and ATT material here aligns with the review skill's checklist.
- **`ios-project-setup`** — Xcode build settings, xcconfig, code signing; where the binary protection and stripping flags actually live.
