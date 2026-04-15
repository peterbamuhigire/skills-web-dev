---
name: ios-swift-design-patterns
description: Swift-idiomatic design patterns for iOS — VC containment to eliminate
  Massive ViewController, hand-rolled MVVM Observable binding without RxSwift, delegation
  naming conventions, associative storage for extension properties, constrained protocol...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# iOS Swift Design Patterns

<!-- dual-compat-start -->
## Use When

- Swift-idiomatic design patterns for iOS — VC containment to eliminate Massive ViewController, hand-rolled MVVM Observable binding without RxSwift, delegation naming conventions, associative storage for extension properties, constrained protocol...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ios-swift-design-patterns` or would be better handled by a more specific companion skill.
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

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
**Source:** Swift Design Patterns — Paul Hudson, Hacking with Swift
**Use when:** Designing iOS app architecture, refactoring large VCs, choosing communication patterns, inheritance vs composition decisions.

---

## SECTION 1: Eliminating Massive ViewController

Root cause: one VC conforming to 5+ protocols simultaneously. Four fixes:

### Fix 1: VC Containment (preferred for sub-screens)

```swift
@nonobjc extension UIViewController {
    func add(_ child: UIViewController, frame: CGRect? = nil) {
        addChild(child)
        if let frame = frame { child.view.frame = frame }
        view.addSubview(child.view)
        child.didMove(toParent: self)
    }

    func remove() {
        willMove(toParent: nil)
        view.removeFromSuperview()
        removeFromParent()
    }
}

class DashboardViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        let stats = StatsViewController()
        add(stats, frame: CGRect(x: 0, y: 0, width: view.bounds.width, height: 200))
    }
}
```

### Fix 2: Dedicated Delegate/DataSource Objects

```swift
class ContactsDataSource: NSObject, UITableViewDataSource {
    var contacts: [Contact] = []

    func tableView(_ tableView: UITableView,
                   numberOfRowsInSection section: Int) -> Int { contacts.count }

    func tableView(_ tableView: UITableView,
                   cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "Cell", for: indexPath)
        cell.textLabel?.text = contacts[indexPath.row].name
        return cell
    }
}

class ContactsViewController: UIViewController {
    private let dataSource = ContactsDataSource()
    @IBOutlet weak var tableView: UITableView!

    override func viewDidLoad() {
        super.viewDidLoad()
        tableView.dataSource = dataSource
    }
}
```

### Fix 3: Move Layout into UIView Subclasses

```swift
// Override loadView() — not viewDidLoad() — to set a custom view
class ProfileViewController: UIViewController {
    override func loadView() {
        view = ProfileView()        // all layout lives in ProfileView
    }
    var profileView: ProfileView { view as! ProfileView }
}
```

### Fix 4: Never Put Shared Resources in AppDelegate

Use a singleton hidden behind a protocol instead (see Section 6).

---

## Additional Guidance

Extended guidance for `ios-swift-design-patterns` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `SECTION 2: Hand-Rolled MVVM Binding (No RxSwift Required)`
- `SECTION 3: Delegation — Correct Swift Naming`
- `SECTION 4: Stored Properties in Extensions (Associative Storage)`
- `SECTION 5: Protocol-Oriented Composition`
- `SECTION 6: Singleton — Swifty Implementation`
- `SECTION 7: Initializer Patterns`
- `SECTION 8: Keypath Adapter Pattern`
- `SECTION 9: Safe Iterator with defer`
- `SECTION 10: Responder Chain — Traversal + Custom Chain`
- `SECTION 11: Copy-on-Write Flyweight`
- `SECTION 12: Swift Anti-Patterns`
- `Quick Decision Guide`
