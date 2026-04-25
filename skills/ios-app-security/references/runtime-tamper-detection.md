# Runtime Tamper Detection

Defences against debuggers, hooks, memory scraping, screen capture, and clipboard leaks on iOS.

## Threat Model

The attacker has physical access to the device, possibly root, and wants to:

- Attach a debugger and pause your app at a sensitive point to read memory.
- Inject a dynamic library that swizzles critical methods or intercepts function calls.
- Read your process memory to extract keys or PII.
- Capture the screen or clipboard while your app shows sensitive information.
- Modify the running binary to disable checks.

Runtime tamper detection hardens the app against these steps. None of the defences are absolute, but each one raises the effort required.

## Anti-Debugging: ptrace PT_DENY_ATTACH

`ptrace(PT_DENY_ATTACH)` is a historical BSD call that asks the kernel to refuse debugger attachment to the current process. When a debugger tries to `ptrace` the process later, the kernel kills the target. Apple preserved the behaviour for iOS apps.

Because `ptrace` is not exposed in the public iOS SDK, call it through `dlsym` at runtime. Wrap in a guard so development builds stay debuggable.

```swift
import Darwin

enum AntiDebug {
    typealias PtraceFn = @convention(c) (_ req: CInt, _ pid: pid_t, _ addr: caddr_t?, _ data: CInt) -> CInt
    static let PT_DENY_ATTACH: CInt = 31

    static func denyAttach() {
        #if DEBUG
        return
        #else
        guard let handle = dlopen(nil, RTLD_NOW) else { return }
        defer { dlclose(handle) }
        guard let sym = dlsym(handle, "ptrace") else { return }
        let ptrace = unsafeBitCast(sym, to: PtraceFn.self)
        _ = ptrace(PT_DENY_ATTACH, 0, nil, 0)
        #endif
    }
}
```

Call `AntiDebug.denyAttach()` as early as possible in your `@main` app initialiser.

## sysctl P_TRACED Check

As a second line, ask the kernel whether the `P_TRACED` flag is set on your own process. A debugger session sets this bit. Checking it periodically catches a debugger that attached after launch or bypassed `PT_DENY_ATTACH`.

```swift
func isBeingDebugged() -> Bool {
    var info = kinfo_proc()
    var size = MemoryLayout<kinfo_proc>.stride
    var mib: [Int32] = [CTL_KERN, KERN_PROC, KERN_PROC_PID, getpid()]
    let result = mib.withUnsafeMutableBufferPointer { buffer in
        sysctl(buffer.baseAddress, UInt32(buffer.count), &info, &size, nil, 0)
    }
    guard result == 0 else { return false }
    return (info.kp_proc.p_flag & P_TRACED) != 0
}
```

Call this at security-critical moments (before decrypting secrets, before signing a transaction), not in a tight loop.

## Anti-Hooking and Runtime Integrity

### Method swizzling detection

Objective-C exposes `class_getMethodImplementation` so you can read the current IMP of a selector. At launch, record the IMPs for your critical selectors. Later, compare the current IMP to the recorded one — a mismatch means something was swizzled.

```swift
import ObjectiveC

final class ImpGuard {
    private var baseline: [String: IMP] = [:]

    func record(_ cls: AnyClass, _ selector: Selector) {
        if let method = class_getInstanceMethod(cls, selector) {
            baseline["\(cls).\(selector)"] = method_getImplementation(method)
        }
    }

    func check(_ cls: AnyClass, _ selector: Selector) -> Bool {
        guard let method = class_getInstanceMethod(cls, selector),
              let expected = baseline["\(cls).\(selector)"] else { return true }
        return method_getImplementation(method) == expected
    }
}
```

Record baselines for your security-sensitive classes (token manager, network delegate) at launch, then verify before use.

### Loaded image check

Walk loaded dynamic libraries with `_dyld_image_count` and `_dyld_get_image_name` (as in `jailbreak-detection.md`) and fail open if an unexpected image is present. In release builds, compile a whitelist of the images you legitimately load.

## Code Integrity Check

Compute a SHA-256 hash of your Mach-O `__TEXT` segment at build time (post-processing build phase) and bake it into the binary. At runtime, hash the same segment and compare. If an attacker patches your binary, the hashes diverge.

Outline (pseudocode; full implementation is platform-specific):

1. Locate your own image with `dladdr` on a known function.
2. Find the `__TEXT` segment via `getsegbyname("__TEXT")`.
3. Hash the bytes between `vmaddr` and `vmaddr + vmsize`.
4. Compare against the expected hash.

Because this requires Mach-O introspection, inline the code rather than calling a named helper. Keep the expected hash obfuscated.

## Memory Protection for Secrets

Plaintext secrets in Swift `String` or `Data` live in the heap until ARC releases them. An attacker with memory access can scrape them. Mitigations:

- Keep secrets as `Data`, not `String` — strings have extra allocations and you cannot zero them reliably.
- Overwrite buffers as soon as you finish with them. Use `memset_s` to defeat dead-store elimination:

```swift
import Darwin

extension Data {
    mutating func zeroize() {
        let count = self.count
        self.withUnsafeMutableBytes { ptr in
            guard let base = ptr.baseAddress else { return }
            memset_s(base, count, 0, count)
        }
    }
}

var secret = Data(/* sensitive bytes */)
defer { secret.zeroize() }
// ... use secret ...
```

- Avoid logging secrets. Use custom `CustomStringConvertible` conformances that redact.

## Frida / Cycript Detection

Frida and Cycript leave distinctive footprints:

- Files under `/tmp/.frida-*`, `/var/mobile/Library/Caches/.frida-*`.
- A listening TCP socket on port 27042 (Frida's default).
- Loaded images containing `FridaGadget`, `frida-agent`, `libcycript`.
- Threads with recognisable names (`gum-js-loop`, `gmain`).

Check for several of these at startup and periodically. Expect attackers to rename Frida, change ports, and hide threads — the checks catch the lazy attacker and generate telemetry for the rest.

## Simulator and Emulator Detection

For apps that do not make sense in the Simulator (face-recognition, biometrics, hardware-bound features), reject the Simulator at compile time:

```swift
#if targetEnvironment(simulator)
#error("This target cannot run on the Simulator")
#endif
```

For release builds you may want a softer runtime check that warns and disables sensitive features, without blocking development:

```swift
#if targetEnvironment(simulator)
let runningOnSimulator = true
#else
let runningOnSimulator = false
#endif
```

## Screen Capture and Mirroring

iOS exposes `UIScreen.main.isCaptured` (Boolean) and `UIScreen.capturedDidChangeNotification` when the screen is being recorded or mirrored. React in two ways:

- Observe the notification and blur or replace sensitive views while capture is active.
- Gate decryption of secrets on `isCaptured == false`.

SwiftUI makes the first pattern straightforward with `.redacted(reason: .placeholder)` or a custom modifier:

```swift
struct CaptureAwareModifier: ViewModifier {
    @State private var captured = UIScreen.main.isCaptured
    func body(content: Content) -> some View {
        content
            .redacted(reason: captured ? .placeholder : [])
            .onReceive(NotificationCenter.default.publisher(for: UIScreen.capturedDidChangeNotification)) { _ in
                captured = UIScreen.main.isCaptured
            }
    }
}
```

## Screenshot Prevention

iOS does not let apps block screenshots outright. You can hide content during the brief window between the user invoking the app switcher and the screenshot being taken by observing `willResignActiveNotification`:

```swift
private var blurView: UIVisualEffectView?

NotificationCenter.default.addObserver(
    forName: UIApplication.willResignActiveNotification,
    object: nil, queue: .main
) { [weak self] _ in
    let blur = UIVisualEffectView(effect: UIBlurEffect(style: .systemMaterial))
    blur.frame = self?.view.bounds ?? .zero
    self?.view.addSubview(blur)
    self?.blurView = blur
}

NotificationCenter.default.addObserver(
    forName: UIApplication.didBecomeActiveNotification,
    object: nil, queue: .main
) { [weak self] _ in
    self?.blurView?.removeFromSuperview()
    self?.blurView = nil
}
```

This also removes sensitive content from the app switcher snapshot that iOS caches for the multitasking thumbnail.

## Pasteboard Hygiene

Sensitive data on the clipboard is readable by any app the user next switches to. Clear it proactively and use expiring items on iOS 14+.

Clear on view disappear:

```swift
func viewDidDisappear(_ animated: Bool) {
    super.viewDidDisappear(animated)
    UIPasteboard.general.items = []
}
```

Write with expiry:

```swift
UIPasteboard.general.setItems(
    [["public.plain-text": "sensitive-token"]],
    options: [
        .expirationDate: Date().addingTimeInterval(30),
        .localOnly: true
    ]
)
```

`.localOnly` prevents Universal Clipboard sync to nearby Apple devices. `.expirationDate` removes the item after the given time.

On iOS 14 and later, iOS shows a banner whenever your app reads the clipboard. Be deliberate — only read the pasteboard in direct response to user action.

## Composed Runtime Check

Glue the pieces together at sensitive moments:

```swift
enum RuntimeGuard {
    static func allowSensitiveAction() -> Bool {
        if isBeingDebugged() { return false }
        if UIScreen.main.isCaptured { return false }
        let report = IntegrityInspector.run()
        if report.confidence >= 0.5 { return false }
        return true
    }
}
```

Call before any action that exposes high-value data. Fail silently and degrade, or trigger step-up auth, rather than crashing.

## Response Strategy

1. **Telemetry first.** Always report signals to the backend. It is the only way to learn what is happening in the wild.
2. **Degrade second.** Disable sensitive features while allowing the rest of the app to function.
3. **Block last.** Reserve hard refusal for high-confidence, high-stakes scenarios (wire transfers, prescription submission).

## Anti-Patterns

- **Single check.** Any single defence is trivial to bypass.
- **Obvious function names.** `checkDebugger`, `isJailbroken`, `hasFrida` are all searchable strings.
- **Hard-crashing on detection.** Ruins UX and points attackers at the exact code to patch.
- **Blocking in Simulator without `#if DEBUG`.** Development becomes painful.
- **Skipping memory zeroing.** Secrets linger on the heap until overwritten.
- **Relying on tamper detection instead of server-side controls.** The server must enforce the real rules.

## Cross-References

- `jailbreak-detection.md` — environment detection; combine the two for layered defence.
- `binary-protection.md` — symbol stripping hides the orchestration of these checks.
- `ats-cert-pinning.md` — tamper checks help detect Frida hooks on the pinning path.
- `keychain-secure-enclave.md` — gate Keychain reads on `RuntimeGuard`.
