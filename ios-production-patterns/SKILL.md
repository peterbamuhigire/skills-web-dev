---
name: ios-production-patterns
description: Production-grade iOS patterns that separate good apps from great apps
  — UIViewController lifecycle gotchas, sensor lifecycle management, delegate pattern
  implementation, keyboard dismissal, Core Data migration, UIImagePickerController
  dismissal...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# iOS Production Patterns

<!-- dual-compat-start -->
## Use When

- Production-grade iOS patterns that separate good apps from great apps — UIViewController lifecycle gotchas, sensor lifecycle management, delegate pattern implementation, keyboard dismissal, Core Data migration, UIImagePickerController dismissal...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ios-production-patterns` or would be better handled by a more specific companion skill.
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
Expert-level, ship-it details that tutorials skip. Each pattern reflects a real
production bug or App Store rejection that could have been avoided.

---

## 1. ViewController Lifecycle — The Exact Sequence

```swift
override func viewDidLoad() {
    super.viewDidLoad()
    // Called ONCE. Wire outlets, configure appearance, set initial data.
    // Never start sensors, timers, or location here.
}

override func viewWillAppear(_ animated: Bool) {
    super.viewWillAppear(animated)
    // Called EVERY time screen is shown.
    // Refresh data from external sources here.
    locationManager.startUpdatingLocation()
}

override func viewDidAppear(_ animated: Bool) {
    super.viewDidAppear(animated)
    // Animation complete. Start timers here.
}

override func viewWillDisappear(_ animated: Bool) {
    super.viewWillDisappear(animated)
    // Stop sensors BEFORE leaving. Save state.
    locationManager.stopUpdatingLocation()
}

override func viewDidDisappear(_ animated: Bool) {
    super.viewDidDisappear(animated)
    // Release non-persistent resources.
}
```

**Critical rules:**
- Start `CLLocationManager`, sensors, timers in `viewWillAppear` — never `viewDidLoad`
- Stop them in `viewWillDisappear` — never `viewDidDisappear` (too late for some sensors)
- Refresh data in `viewWillAppear` so it's current every time the screen is visible

---

## 2. Delegate Pattern — Full Implementation (6 Steps)

The delegate pattern is iOS's primary mechanism for child-to-parent communication.

```swift
// Step 1: Define protocol in child controller
protocol DatePickerDelegate: AnyObject {
    func dateSelected(_ date: Date)
}

// Step 2: Weak delegate property in child (weak = no retain cycle)
class DatePickerViewController: UIViewController {
    weak var delegate: DatePickerDelegate?

    func confirmTapped() {
        delegate?.dateSelected(selectedDate)
        navigationController?.popViewController(animated: true)
    }
}

// Step 3: Parent declares conformance + implements
class ContactsViewController: UIViewController, DatePickerDelegate {
    func dateSelected(_ date: Date) {
        contact.birthday = date
        tableView.reloadData()
    }

    // Step 4: Wire delegate before presenting
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        if let vc = segue.destination as? DatePickerViewController {
            vc.delegate = self
        }
    }
}
```

**Always `weak var delegate`** — strong reference creates a retain cycle. Child and parent
hold each other permanently in memory until the app is killed.

**Forward passing (parent → child):** Property assignment in `prepare(for:segue:)` or before
`pushViewController`. No protocol needed for forward passing.

---

## 3. Sensor Lifecycle — Location

```swift
class MapViewController: UIViewController, CLLocationManagerDelegate {
    let locationManager = CLLocationManager()

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        locationManager.delegate = self
        locationManager.desiredAccuracy = kCLLocationAccuracyBest
        locationManager.requestWhenInUseAuthorization()
        locationManager.startUpdatingLocation()
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        locationManager.stopUpdatingLocation()  // battery savings when not visible
    }

    // Handle ALL authorization states — not just .authorized
    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        switch manager.authorizationStatus {
        case .authorizedWhenInUse, .authorizedAlways:
            manager.startUpdatingLocation()
        case .denied, .restricted:
            showLocationDeniedAlert()  // guide user to Settings
        case .notDetermined:
            break
        @unknown default: break
        }
    }
}
```

**Request only what you need:**
- `requestWhenInUseAuthorization()` — foreground only
- `requestAlwaysAuthorization()` — background updates. Apple reviewers scrutinise this.
  Requires explicit justification. Expect follow-up questions in App Review.

---

## 4. Camera Integration — Four Gotchas

```swift
class CameraViewController: UIViewController,
    UIImagePickerControllerDelegate, UINavigationControllerDelegate {

    func openCamera() {
        // Gotcha 1: Always check availability — iPads may lack a camera
        guard UIImagePickerController.isSourceTypeAvailable(.camera) else {
            showAlert("Camera not available")
            return
        }

        let picker = UIImagePickerController()
        picker.sourceType = .camera
        picker.allowsEditing = true
        picker.delegate = self
        present(picker, animated: true)
    }

    func imagePickerController(_ picker: UIImagePickerController,
        didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {

        // Gotcha 2: Use .editedImage when allowsEditing = true
        let image = info[.editedImage] as? UIImage ?? info[.originalImage] as? UIImage

        // Gotcha 3: Dismiss explicitly — picker does NOT self-dismiss
        dismiss(animated: true) {
            // Gotcha 4: Present share dialogs INSIDE the completion handler
            self.processImage(image)
        }
    }
}
```

**Storing images in SwiftData/Core Data:**
```swift
// Store as compressed Data, never as UIImage directly
let imageData = image?.jpegData(compressionQuality: 0.8)

// Decode async on retrieval — never on main thread
Task.detached(priority: .userInitiated) {
    if let data = entry.photoData, let image = UIImage(data: data) {
        await MainActor.run { self.imageView.image = image }
    }
}
```

---

## 5. Keyboard Dismissal

iOS does NOT auto-dismiss keyboard on tap outside. Three-step fix:

```swift
// Storyboard approach:
// Step 1: Change root UIView class to UIControl in Identity Inspector
// Step 2: Wire Touch Down (not Touch Up Inside) to this action
@IBAction func backgroundTapped(_ sender: Any) {
    view.endEditing(true)
}
```

Use **Touch Down**, not Touch Up Inside. Touch Down fires immediately on contact.
Touch Up Inside fires on finger release — causes timing issues with keyboard animations.

**Programmatic alternative:**
```swift
override func viewDidLoad() {
    super.viewDidLoad()
    let tap = UITapGestureRecognizer(target: self, action: #selector(dismissKeyboard))
    tap.cancelsTouchesInView = false  // lets other taps pass through
    view.addGestureRecognizer(tap)
}

@objc func dismissKeyboard() { view.endEditing(true) }
```

---

## 6. Gesture Recognizer State Guard

Long press gestures fire continuously while held. Always guard state:

```swift
@objc func handleLongPress(_ gesture: UILongPressGestureRecognizer) {
    // Without this guard, action fires dozens of times per second
    guard gesture.state == .began else { return }

    let point = gesture.location(in: tableView)
    if let indexPath = tableView.indexPathForRow(at: point) {
        performAction(at: indexPath)
    }
}
```

---

## 7. Core Data Lightweight Migration (Mandatory Before Any Schema Change)

```swift
// In AppDelegate or Core Data stack setup
let options = [
    NSMigratePersistentStoresAutomaticallyOption: true,
    NSInferMappingModelAutomaticallyOption: true
]
try coordinator.addPersistentStore(
    ofType: NSSQLiteStoreType,
    configurationName: nil,
    at: storeURL,
    options: options
)
```

**Without migration**: Adding a field to an existing entity crashes production users with
"Can't find model for source store" on next launch. Unfixable without a new App Store
submission — users are stranded until they update.

**What Lightweight Migration handles:** Adding fields (with default values), renaming entities,
renaming attributes.

**Breaking changes** (removing fields, changing types): Require explicit mapping models in
Xcode's data model editor (.xcmappingmodel).

**Dev shortcut**: Delete and reinstall app during development to reset the database.
NEVER attempt this in production.

---

## 8. Programmatic UI Constraints — Two Rules

```swift
let label = UILabel()
label.translatesAutoresizingMaskIntoConstraints = false  // Rule 1: ALWAYS set this first
view.addSubview(label)

NSLayoutConstraint.activate([  // Rule 2: activate() in one batch, not addConstraint() one-by-one
    label.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 16),
    label.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
    label.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20)
])
```

Forgetting `translatesAutoresizingMaskIntoConstraints = false` is one of the most common
silent failures. The view disappears or jumps to wrong position with no error or warning.

---

## 9. HealthKit — Partial Permissions Pattern

```swift
class HealthKitManager {
    let healthStore = HKHealthStore()

    func requestPermissions(completion: @escaping (Bool) -> Void) {
        // Check availability first — iPads without Health app return false
        guard HKHealthStore.isHealthDataAvailable() else {
            completion(false)
            return
        }

        let typesToRead: Set<HKObjectType> = [
            HKObjectType.quantityType(forIdentifier: .stepCount)!,
            HKObjectType.quantityType(forIdentifier: .activeEnergyBurned)!
        ]
        let typesToWrite: Set<HKSampleType> = [
            HKObjectType.quantityType(forIdentifier: .activeEnergyBurned)!
        ]

        healthStore.requestAuthorization(toShare: typesToWrite, read: typesToRead) { success, _ in
            DispatchQueue.main.async { completion(success) }
        }
    }

    // Use HKStatisticsQuery for aggregates — never fetch all samples and sum manually
    func fetchStepCount(for date: Date, completion: @escaping (Double) -> Void) {
        let stepType = HKQuantityType.quantityType(forIdentifier: .stepCount)!
        let startOfDay = Calendar.current.startOfDay(for: date)
        let predicate = HKQuery.predicateForSamples(withStart: startOfDay, end: date)

        let query = HKStatisticsQuery(quantityType: stepType,
            quantitySamplePredicate: predicate, options: .cumulativeSum) { _, result, _ in
            let steps = result?.sumQuantity()?.doubleValue(for: .count()) ?? 0
            DispatchQueue.main.async { completion(steps) }
        }
        healthStore.execute(query)
    }
}
```

**Design for partial permissions.** User can grant steps but deny weight. Each feature
must work independently — never assume all requested permissions were granted.

**Required Info.plist keys** (missing = App Store rejection):
- `NSHealthShareUsageDescription`
- `NSHealthUpdateUsageDescription`

---

## 10. Core ML on Background Thread

```swift
class ImageClassifier {
    private let model: VNCoreMLModel

    init() throws {
        let config = MLModelConfiguration()
        config.computeUnits = .all  // GPU + Neural Engine + CPU
        let coreMLModel = try MyClassifier(configuration: config)
        self.model = try VNCoreMLModel(for: coreMLModel.model)
    }

    func classify(image: UIImage, completion: @escaping (String, Float) -> Void) {
        guard let ciImage = CIImage(image: image) else { return }  // Vision needs CIImage

        // Core ML compiles on first run — NEVER run on main thread
        DispatchQueue.global(qos: .userInitiated).async {
            let request = VNCoreMLRequest(model: self.model) { request, _ in
                guard let results = request.results as? [VNClassificationObservation],
                      let top = results.first else { return }
                DispatchQueue.main.async {
                    completion(top.identifier, top.confidence)
                }
            }
            let handler = VNImageRequestHandler(ciImage: ciImage)
            try? handler.perform([request])
        }
    }
}
```

---

## 11. SwiftUI / UIKit Integration

```swift
// Embed SwiftUI view in UIKit navigation stack
let hostingController = UIHostingController(rootView: MySwiftUIView())
navigationController?.pushViewController(hostingController, animated: true)

// Embed UIKit view in SwiftUI
struct MapViewWrapper: UIViewRepresentable {
    func makeUIView(context: Context) -> MKMapView { MKMapView() }
    func updateUIView(_ uiView: MKMapView, context: Context) {}
}
```

**Migration strategy**: Add SwiftUI screens incrementally via `UIHostingController`. Never
rewrite all UIKit at once. Each new screen can be SwiftUI; existing screens stay UIKit until
there's a reason to migrate them.

---

## 12. SwiftUI vs UIKit Decision

| Scenario | Use |
|---|---|
| New app, iOS 16+ minimum | SwiftUI |
| Must support iOS 15 and below | UIKit |
| Complex custom drawing (`CALayer`, `drawRect`) | UIKit |
| Cross-platform (macOS / watchOS / tvOS) | SwiftUI |
| Large existing UIKit codebase | UIKit + incremental SwiftUI |
| Rapid prototyping with live preview | SwiftUI |
| SwiftData ORM integration | SwiftUI (`@Query` macro) |

**SwiftData vs Core Data:**
- SwiftData (iOS 17+): Swift-native, `@Model` macro, works natively with SwiftUI `@Query`.
  Use for new apps targeting iOS 17+.
- Core Data: Mature, battle-tested, supports iOS 13+. Required when supporting older OS or
  when complex migration scripts are already in place.
- Never mix both in the same app targeting the same entity graph.

---

## 13. App Store Submission Checklist

```
□ App icon: 1024×1024 in Asset Catalog — no alpha channel (transparent icons rejected)
□ Screenshots: required for every supported device size class
□ Version string: user-facing (1.2.3), semantic
□ Build number: always increment — never reuse a build number for the same version
□ Export compliance: declare whether app uses cryptography (HTTPS = yes)
□ Info.plist usage strings: every permission key must be descriptive and accurate
    NSLocationWhenInUseUsageDescription
    NSCameraUsageDescription
    NSPhotoLibraryUsageDescription
    NSHealthShareUsageDescription
    NSHealthUpdateUsageDescription
    NSBluetoothAlwaysUsageDescription
□ Validate archive in Xcode Organizer before submitting (catches cert/provisioning mismatches)
□ Test on minimum supported device in release build (not simulator)
□ Test on latest iOS version
□ Test every permission denial path — location denied, camera not available, HealthKit off
□ Core Data migration in place if schema changed since last release
□ Third-party SDK licences included if their terms require it
□ TestFlight external testing complete (at least one non-developer tester)
```

**Top rejection reasons:**
1. Vague or missing Info.plist permission description strings
2. App crashes in reviewer's environment — test on oldest supported device in release mode
3. UI not adapted for latest device sizes (Dynamic Island, notch variations)
4. Broken features when using the test account credentials provided to reviewer

**iOS beta timing**: Apple releases iOS betas at WWDC (June). Test against betas before
September public release. Most iOS users update within weeks of GA — an untested app loses
users on release day.

---

## 14. Production Anti-Patterns

| Anti-Pattern | Consequence | Fix |
|---|---|---|
| Start sensors in `viewDidLoad` | Sensors run off-screen, drain battery | Move to `viewWillAppear` |
| `strong var delegate` | Retain cycle — permanent memory leak | Always `weak var delegate` |
| No Core Data migration options | Production crash on schema change | Always add Lightweight Migration |
| No camera availability check | Crash on iPad without camera | Guard with `isSourceTypeAvailable` |
| No gesture state guard | Action fires dozens of times per hold | `guard gesture.state == .began` |
| Core ML inference on main thread | Frozen UI on first run | Always use background queue |
| Forgetting picker dismiss | Camera UI stuck on screen permanently | `dismiss(animated:completion:)` |
| `translatesAutoresizingMaskIntoConstraints` not set to `false` | View silently disappears | Set before `NSLayoutConstraint.activate` |
| Assuming all HealthKit permissions granted | Feature crashes when permission partial | Guard each type independently |
| Reusing build number | App Store Connect upload rejection | Always increment before archive |
