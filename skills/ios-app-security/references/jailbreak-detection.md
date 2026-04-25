# Jailbreak Detection

Heuristics for detecting a compromised iOS environment, composed checks, telemetry strategy, and response patterns.

## What Jailbreak Detection Is and Is Not

Jailbreak detection raises the cost of attacking your app on a compromised device. It does not make attack impossible. Every detection technique has a documented bypass, and bypass tweaks (Liberty Lite, Shadow, A-Bypass) are a routine part of the jailbreak community toolchain. Treat detection as a **speed bump against the casual attacker and a signal for your security telemetry**, never as a guarantee.

The goals are:

- Discourage casual tinkerers.
- Refuse to load your most sensitive material on a known-compromised device.
- Provide signal to your backend so it can step up authentication or block high-risk transactions.

## When to Use

Worth the investment for:

- Banking, payment, and financial services apps.
- Health apps handling regulated data (HIPAA, DPPA, GDPR health-sensitive).
- Enterprise apps distributing sensitive documents.
- Apps with non-trivial license/entitlement value to piracy.

Not worth it for:

- Ordinary consumer apps where the sensitive data is on the server and client state is replaceable.
- Games — where jailbreak detection annoys legitimate power users and barely slows cheaters.
- Apps where a false positive would block a significant legitimate user base.

## Detection Heuristics

Use several heuristics from different categories. A single check is a single point of patch-out. The goal is that a patcher has to find and defeat all of them, and at least some of them should not look like jailbreak checks.

### 1. File existence

Common jailbreak artefacts leave recognisable files. Check for a handful:

- `/Applications/Cydia.app`
- `/Applications/Sileo.app`
- `/Applications/Zebra.app`
- `/private/var/lib/apt/`
- `/private/var/lib/cydia`
- `/private/var/tmp/cydia.log`
- `/bin/bash`
- `/usr/sbin/sshd`
- `/etc/apt`
- `/usr/libexec/cydia/firmware.sh`

Use `FileManager.default.fileExists(atPath:)` and also try `stat(2)` directly because `FileManager` can be hooked more easily than the lower-level syscall.

### 2. URL scheme probe

Jailbreak stores register URL schemes:

```swift
if let url = URL(string: "cydia://package/com.example.package"),
   UIApplication.shared.canOpenURL(url) {
    // Cydia or a descendant is installed.
}
```

This requires the scheme to be declared in `LSApplicationQueriesSchemes` in `Info.plist`, which is itself a hint during reverse engineering. Use it as one of several checks, not as the only one.

### 3. Sandbox integrity probe

A stock app cannot write outside its container. On a jailbroken device, sandbox escape is often possible. Try writing to a path outside your container:

```swift
let probePath = "/private/jailbreak_probe.txt"
do {
    try "probe".write(toFile: probePath, atomically: true, encoding: .utf8)
    try? FileManager.default.removeItem(atPath: probePath)
    return true // We were allowed to write — suspicious.
} catch {
    return false
}
```

The most conclusive test that is also easy to implement.

### 4. Dynamic library inspection

Walk the loaded image table and look for injected libraries. Frida, Cycript, MobileSubstrate, and Substitute all announce themselves as images:

```swift
import MachO

func suspiciousDylibs() -> [String] {
    let suspicious = [
        "MobileSubstrate", "Substitute", "SubstrateLoader",
        "FridaGadget", "frida", "cycript", "TweakInject", "CydiaSubstrate"
    ]
    var matches: [String] = []
    let count = _dyld_image_count()
    for i in 0..<count {
        if let name = _dyld_get_image_name(i) {
            let path = String(cString: name)
            if suspicious.contains(where: { path.localizedCaseInsensitiveContains($0) }) {
                matches.append(path)
            }
        }
    }
    return matches
}
```

### 5. Symbolic link checks

`/Library` on a stock device is a real directory. Some jailbreak tools replace parts of the root filesystem with symlinks into writable partitions:

```swift
var statBuf = stat()
if lstat("/Library", &statBuf) == 0 && (statBuf.st_mode & S_IFLNK) != 0 {
    return true
}
```

### 6. Fork check

A sandboxed iOS app cannot call `fork(2)` — the sandbox returns -1. A jailbroken app with the sandbox relaxed can. Call `fork()`, and if the return value is non-negative, reap the child and flag the result:

```swift
let pid = fork()
if pid >= 0 {
    if pid > 0 { waitpid(pid, nil, 0) }
    return true
}
return false
```

Be careful — calling `fork` in a production app is a yellow flag for some App Review passes. Wrap it behind `#if !APPSTORE` or omit it for apps where App Review scrutiny is a concern.

## Composed Swift Helper

Compose the checks and report a confidence score rather than a boolean. Multiple independent positives raise confidence.

```swift
struct IntegrityReport {
    enum Signal {
        case suspiciousFile(String)
        case urlSchemeCydia
        case sandboxEscape
        case dylibInjected(String)
        case symlinkLibrary
        case forkAllowed
    }
    let signals: [Signal]
    var isSuspicious: Bool { !signals.isEmpty }
    var confidence: Double {
        // Two or more independent signals give high confidence.
        return min(1.0, Double(signals.count) * 0.4)
    }
}

enum IntegrityInspector {
    static func run() -> IntegrityReport {
        var signals: [IntegrityReport.Signal] = []

        // Deliberately inline these; do not use a single "checkFiles" function
        // that a patcher can locate by string search.
        for path in Self.watchedPaths where access(path, F_OK) == 0 {
            signals.append(.suspiciousFile(path))
            break
        }

        if let url = URL(string: "\u{0063}ydia://"),
           UIApplication.shared.canOpenURL(url) {
            signals.append(.urlSchemeCydia)
        }

        if Self.canEscapeSandbox() {
            signals.append(.sandboxEscape)
        }

        let dylibs = suspiciousDylibs()
        if let first = dylibs.first {
            signals.append(.dylibInjected(first))
        }

        return IntegrityReport(signals: signals)
    }

    private static let watchedPaths = [
        "/Applications/Cydia.app", "/Applications/Sileo.app",
        "/private/var/lib/apt/", "/bin/bash", "/etc/apt"
    ]

    private static func canEscapeSandbox() -> Bool {
        let path = "/private/.probe.\(UUID().uuidString)"
        guard (try? "x".write(toFile: path, atomically: true, encoding: .utf8)) != nil else {
            return false
        }
        try? FileManager.default.removeItem(atPath: path)
        return true
    }
}
```

## Obfuscation Tips

- Never name the entry point `isJailbroken()`.
- Split strings (`"\u{0063}ydia"`) so a `strings` dump does not reveal them.
- Inline checks rather than calling helper functions whose symbols a reverser can list.
- Mix in some security-adjacent functions (such as integrity hash checks) so that the jailbreak logic is not a clean island in your binary.

## Telemetry First, Blocking Second

Report the `IntegrityReport` to your backend alongside a per-user identifier and a timestamp. Let the server decide response policy:

- **Low confidence:** allow, but raise the risk score for that session.
- **Medium confidence:** require step-up authentication, disable high-value transactions.
- **High confidence:** refuse to load sensitive endpoints.

Never hard-crash the app on detection. Crashing looks like a bug to the user and tells the attacker exactly where to patch.

## Bypass Awareness

The usual bypass workflow is:

1. Attacker installs a jailbreak.
2. Attacker installs a bypass tweak targeting your app or general detection methods.
3. Tweak hooks `NSFileManager -fileExistsAtPath:` and related calls to lie about the presence of jailbreak files.
4. Tweak hooks `canOpenURL:` to refuse `cydia://`.
5. Your detection reports clean.

Counter-measures:

- Use low-level syscalls (`access`, `stat`, `lstat`) alongside Foundation APIs. Tweaks that hook Foundation often leave syscalls alone.
- Mix in checks that do not look like jailbreak tests (code hash, debugger check).
- Add a backend check: if the device reports clean but other signals look odd, escalate.

## Commercial Solutions

If the app's threat model justifies it, commercial libraries provide hardened detection plus runtime attestation: Guardsquare iXGuard, Promon SHIELD, OneSpan, Appdome. They add binary size and cost, and require regular updates to stay ahead of bypass authors. Consider them for banking, payment, or heavily targeted apps, but accept that even commercial products lose eventually.

## Anti-Patterns

- **Single check with an obvious name.** First thing a patcher defeats.
- **Hard crash on detection.** Ruins UX for legitimate users, tells attackers where to patch.
- **Storing the detection result in `UserDefaults`.** `UserDefaults` is plaintext and trivially tampered with.
- **Blocking in the simulator.** Use `#if targetEnvironment(simulator)` to short-circuit; otherwise development is painful.
- **Not reporting to the backend.** Detection without telemetry is self-deception.
- **Relying on jailbreak detection instead of sound server-side authorisation.** The server must enforce its own rules.

## Cross-References

- `runtime-tamper-detection.md` — anti-debugging and Frida detection complete the picture.
- `ats-cert-pinning.md` — pinning + jailbreak detection together defeat Kill Switch-style bypasses.
- `binary-protection.md` — symbol stripping and obfuscation hide the orchestration of checks.
- `keychain-secure-enclave.md` — refuse to load high-value Keychain items when detection fires.
