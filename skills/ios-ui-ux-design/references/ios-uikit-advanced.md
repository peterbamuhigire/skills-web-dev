---
name: ios-uikit-advanced
description: Advanced UIKit for production iOS apps — UICollectionViewDiffableDataSource
  with NSDiffableDataSourceSnapshot, UICollectionViewCompositionalLayout (sections
  with orthogonal scrolling, badges, headers), UIViewControllerTransitioningDelegate
  for...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# iOS UIKit Advanced
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Advanced UIKit for production iOS apps — UICollectionViewDiffableDataSource with NSDiffableDataSourceSnapshot, UICollectionViewCompositionalLayout (sections with orthogonal scrolling, badges, headers), UIViewControllerTransitioningDelegate for...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ios-uikit-advanced` or would be better handled by a more specific companion skill.
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
| Correctness | UIKit diffable data source test plan | Markdown doc covering snapshot updates, identifier stability, and cell reuse tests | `docs/ios/uikit-tests.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Production-grade UIKit patterns for polished, crash-free iOS interfaces. No placeholder patterns — every section is ready to ship.

---

## SECTION 1: Diffable Data Source — Eliminating Index-Out-of-Bounds Crashes

The old `beginUpdates/endUpdates` pattern crashes when data changes occur during animation. Diffable data source computes diffs automatically and applies them safely.

```swift
enum Section { case main, featured }

struct Item: Hashable {
    let id: UUID
    let title: String
    // Hashable identity is all diffable needs — diff is computed automatically
}

class ContactsViewController: UIViewController {
    private var dataSource: UITableViewDiffableDataSource<Section, Item>!

    override func viewDidLoad() {
        super.viewDidLoad()
        configureDataSource()
    }

    private func configureDataSource() {
        dataSource = UITableViewDiffableDataSource<Section, Item>(
            tableView: tableView
        ) { tableView, indexPath, item in
            let cell = tableView.dequeueReusableCell(withIdentifier: "Cell", for: indexPath)
            var config = cell.defaultContentConfiguration()
            config.text = item.title
            cell.contentConfiguration = config
            return cell
        }
    }

    func applySnapshot(items: [Item], animatingDifferences: Bool = true) {
        var snapshot = NSDiffableDataSourceSnapshot<Section, Item>()
        snapshot.appendSections([.main])
        snapshot.appendItems(items, toSection: .main)
        dataSource.apply(snapshot, animatingDifferences: animatingDifferences)
    }

    // Reload specific items without full reload (iOS 15+)
    func updateItem(_ item: Item) {
        var snapshot = dataSource.snapshot()
        snapshot.reconfigureItems([item])  // preserves cell height animation
        dataSource.apply(snapshot, animatingDifferences: true)
    }
}
```

**Multi-section snapshots:**

```swift
var snapshot = NSDiffableDataSourceSnapshot<Section, Item>()
snapshot.appendSections([.featured, .main])
snapshot.appendItems(featuredItems, toSection: .featured)
snapshot.appendItems(regularItems, toSection: .main)
// Move items between sections:
snapshot.moveItem(item, afterItem: otherItem)
snapshot.moveSection(.featured, afterSection: .main)
dataSource.apply(snapshot)
```

---

## Additional Guidance

Extended guidance for `ios-uikit-advanced` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `SECTION 2: Compositional Layout — Complex Collection Layouts`
- `SECTION 3: Custom View Controller Transitions`
- `SECTION 4: UIViewPropertyAnimator — Interruptible Animations`
- `SECTION 5: Context Menus`
- `SECTION 6: Bottom Sheets with UISheetPresentationController`
- `SECTION 7: NSFetchedResultsController with Diffable Data Source`
- `SECTION 8: Prefetching for Smooth Scrolling`
- `SECTION 9: Production Anti-Patterns`
- `SECTION 10: Advanced Interactions Reference`
- `Quick-Reference Checklist`