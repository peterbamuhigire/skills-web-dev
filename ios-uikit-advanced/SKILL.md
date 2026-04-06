---
name: ios-uikit-advanced
description: Advanced UIKit for production iOS apps — UICollectionViewDiffableDataSource with NSDiffableDataSourceSnapshot, UICollectionViewCompositionalLayout (sections with orthogonal scrolling, badges, headers), UIViewControllerTransitioningDelegate for custom transitions, UIViewPropertyAnimator for interruptible animations, UIContextMenuConfiguration for context menus, UISheetPresentationController for bottom sheets, NSFetchedResultsController with diffable sources, and prefetching with UITableViewDataSourcePrefetching. Use when building polished, premium UIKit interfaces: complex collection layouts, custom animated transitions, context menus, or smooth interactive animations.
---

# iOS UIKit Advanced

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

**`reconfigureItems` vs `reloadItems`**: Use `reconfigureItems` (iOS 15+) when only cell content changes — calls `cellForItemAt` on existing cells without recreating them, preserving animations and avoiding flicker. Use `reloadItems` only when the cell type itself must change.

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

## SECTION 2: Compositional Layout — Complex Collection Layouts

```swift
func makeLayout() -> UICollectionViewLayout {
    UICollectionViewCompositionalLayout { sectionIndex, environment in
        switch sectionIndex {
        case 0: return Self.makeFeaturedSection()
        case 1: return Self.makeGridSection(environment: environment)
        case 2: return Self.makeCarouselSection()
        default: return Self.makeListSection()
        }
    }
}

// Full-width featured banner
static func makeFeaturedSection() -> NSCollectionLayoutSection {
    let item = NSCollectionLayoutItem(
        layoutSize: .init(widthDimension: .fractionalWidth(1.0),
                          heightDimension: .fractionalHeight(1.0))
    )
    let group = NSCollectionLayoutGroup.horizontal(
        layoutSize: .init(widthDimension: .fractionalWidth(1.0),
                          heightDimension: .absolute(200)),
        subitems: [item]
    )
    let section = NSCollectionLayoutSection(group: group)
    section.contentInsets = NSDirectionalEdgeInsets(top: 8, leading: 16, bottom: 8, trailing: 16)
    return section
}

// Adaptive grid — fills width, adjusts columns for iPad
static func makeGridSection(environment: NSCollectionLayoutEnvironment) -> NSCollectionLayoutSection {
    let columns = environment.container.effectiveContentSize.width > 500 ? 3 : 2
    let fraction = 1.0 / CGFloat(columns)
    let item = NSCollectionLayoutItem(
        layoutSize: .init(widthDimension: .fractionalWidth(fraction),
                          heightDimension: .fractionalWidth(fraction))
    )
    item.contentInsets = NSDirectionalEdgeInsets(top: 4, leading: 4, bottom: 4, trailing: 4)
    let group = NSCollectionLayoutGroup.horizontal(
        layoutSize: .init(widthDimension: .fractionalWidth(1.0), heightDimension: .estimated(150)),
        repeatingSubitem: item, count: columns
    )
    return NSCollectionLayoutSection(group: group)
}

// Horizontal carousel with paging snap (orthogonal scrolling)
static func makeCarouselSection() -> NSCollectionLayoutSection {
    let item = NSCollectionLayoutItem(
        layoutSize: .init(widthDimension: .fractionalWidth(1.0),
                          heightDimension: .fractionalHeight(1.0))
    )
    let group = NSCollectionLayoutGroup.horizontal(
        layoutSize: .init(widthDimension: .fractionalWidth(0.85),
                          heightDimension: .absolute(180)),
        subitems: [item]
    )
    let section = NSCollectionLayoutSection(group: group)
    section.orthogonalScrollingBehavior = .groupPagingCentered
    section.interGroupSpacing = 12
    section.contentInsets = NSDirectionalEdgeInsets(top: 8, leading: 16, bottom: 8, trailing: 16)
    return section
}

// Sticky header + badge supplementary items
static func makeSectionWithHeader() -> NSCollectionLayoutSection {
    let headerSize = NSCollectionLayoutSize(widthDimension: .fractionalWidth(1.0),
                                            heightDimension: .estimated(44))
    let header = NSCollectionLayoutBoundarySupplementaryItem(
        layoutSize: headerSize,
        elementKind: UICollectionView.elementKindSectionHeader,
        alignment: .top)
    header.pinToVisibleBounds = true  // sticky header

    let badgeSize = NSCollectionLayoutSize(widthDimension: .absolute(20),
                                           heightDimension: .absolute(20))
    let badge = NSCollectionLayoutSupplementaryItem(
        layoutSize: badgeSize,
        elementKind: "badge",
        containerAnchor: NSCollectionLayoutAnchor(
            edges: [.top, .trailing],
            absoluteOffset: CGPoint(x: 8, y: -8)
        )
    )
    let item = NSCollectionLayoutItem(
        layoutSize: .init(widthDimension: .fractionalWidth(0.5),
                          heightDimension: .absolute(120)),
        supplementaryItems: [badge]
    )
    let group = NSCollectionLayoutGroup.horizontal(
        layoutSize: .init(widthDimension: .fractionalWidth(1.0), heightDimension: .absolute(120)),
        subitems: [item]
    )
    let section = NSCollectionLayoutSection(group: group)
    section.boundarySupplementaryItems = [header]
    return section
}
```

**`orthogonalScrollingBehavior` options**: `.continuous`, `.continuousGroupLeadingBoundary`, `.paging`, `.groupPaging`, `.groupPagingCentered` — choose based on desired snapping behaviour.

---

## SECTION 3: Custom View Controller Transitions

```swift
// 1. Animator — defines the actual animation
class SlideTransitionAnimator: NSObject, UIViewControllerAnimatedTransitioning {
    let presenting: Bool
    init(presenting: Bool) { self.presenting = presenting }

    func transitionDuration(using context: UIViewControllerContextTransitioning?) -> TimeInterval { 0.35 }

    func animateTransition(using context: UIViewControllerContextTransitioning) {
        guard let toView = context.view(forKey: .to),
              let fromView = context.view(forKey: .from) else {
            context.completeTransition(false)
            return
        }
        let container = context.containerView
        let width = container.bounds.width

        if presenting {
            toView.frame = CGRect(x: width, y: 0,
                                  width: container.bounds.width,
                                  height: container.bounds.height)
            container.addSubview(toView)
            UIView.animate(withDuration: transitionDuration(using: context),
                           delay: 0, options: .curveEaseInOut) {
                toView.frame.origin.x = 0
                fromView.frame.origin.x = -width * 0.3
            } completion: { _ in
                context.completeTransition(!context.transitionWasCancelled)
            }
        } else {
            container.addSubview(toView)
            container.bringSubviewToFront(fromView)
            UIView.animate(withDuration: transitionDuration(using: context),
                           delay: 0, options: .curveEaseInOut) {
                fromView.frame.origin.x = width
                toView.frame.origin.x = 0
            } completion: { _ in
                context.completeTransition(!context.transitionWasCancelled)
            }
        }
    }
}

// 2. Transitioning delegate — vends animators
class SlideTransitionDelegate: NSObject, UIViewControllerTransitioningDelegate {
    private var interactionController: UIPercentDrivenInteractiveTransition?

    func animationController(forPresented presented: UIViewController,
                             presenting: UIViewController,
                             source: UIViewController) -> UIViewControllerAnimatedTransitioning? {
        SlideTransitionAnimator(presenting: true)
    }

    func animationController(forDismissed dismissed: UIViewController)
        -> UIViewControllerAnimatedTransitioning? {
        SlideTransitionAnimator(presenting: false)
    }

    func interactionControllerForDismissal(using animator: UIViewControllerAnimatedTransitioning)
        -> UIViewControllerInteractiveTransitioning? {
        interactionController
    }
}

// 3. Wiring — CRITICAL: retain the delegate (it is a weak reference)
class HostViewController: UIViewController {
    private var transitionDelegate: SlideTransitionDelegate?  // strong retain required

    func present(_ vc: UIViewController) {
        transitionDelegate = SlideTransitionDelegate()
        vc.modalPresentationStyle = .custom
        vc.transitioningDelegate = transitionDelegate
        present(vc, animated: true)
    }
}
```

**`transitioningDelegate` is `weak`** — if you set it inline without storing it, the transition silently falls back to the default. Always retain it as a stored property on the presenting controller.

---

## SECTION 4: UIViewPropertyAnimator — Interruptible Animations

```swift
class AnimatedViewController: UIViewController {
    private var animator: UIViewPropertyAnimator?

    func animateIn() {
        animator = UIViewPropertyAnimator(duration: 0.4, dampingRatio: 0.75) {
            self.cardView.transform = .identity
            self.cardView.alpha = 1
        }
        animator?.startAnimation()
    }

    func pauseAnimation() { animator?.pauseAnimation() }
    func reverseAnimation() {
        animator?.isReversed = true
        animator?.startAnimation()
    }
    func scrubTo(fraction: CGFloat) { animator?.fractionComplete = fraction }

    // Interactive — driven by pan gesture
    @objc func handlePan(_ gesture: UIPanGestureRecognizer) {
        switch gesture.state {
        case .began:
            // Create once in .began — never recreate during .changed
            animator = UIViewPropertyAnimator(duration: 0.4, curve: .easeInOut) {
                self.cardView.center.y -= 200
            }
            animator?.pauseAnimation()

        case .changed:
            let translation = gesture.translation(in: view)
            animator?.fractionComplete = max(0, min(1, -translation.y / 200))

        case .ended:
            let velocity = gesture.velocity(in: view)
            // Continue with velocity-adjusted duration factor
            animator?.continueAnimation(
                withTimingParameters: nil,
                durationFactor: velocity.y < 0 ? 0.3 : 0.5
            )
        default: break
        }
    }
}
```

**Key rules**: Create the animator once in `.began`. Scrub with `fractionComplete` in `.changed`. Call `continueAnimation` in `.ended` — never `startAnimation`. For spring animations, use `UISpringTimingParameters` with `initialVelocity` derived from the gesture velocity vector.

---

## SECTION 5: Context Menus

```swift
// UICollectionView delegate — iOS 13+
func collectionView(_ collectionView: UICollectionView,
                    contextMenuConfigurationForItemAt indexPath: IndexPath,
                    point: CGPoint) -> UIContextMenuConfiguration? {
    let item = items[indexPath.item]

    return UIContextMenuConfiguration(
        identifier: indexPath as NSCopying,  // identifier used to match the commit preview
        previewProvider: {
            let preview = ItemPreviewViewController(item: item)
            preview.preferredContentSize = CGSize(width: 300, height: 200)
            return preview
        },
        actionProvider: { _ in
            let share = UIAction(title: "Share",
                                 image: UIImage(systemName: "square.and.arrow.up")) { _ in
                self.shareItem(item)
            }
            let delete = UIAction(title: "Delete",
                                  image: UIImage(systemName: "trash"),
                                  attributes: .destructive) { _ in
                self.deleteItem(item)
            }
            let editMenu = UIMenu(title: "Edit", children: [
                UIAction(title: "Rename") { _ in self.renameItem(item) }
            ])
            return UIMenu(children: [share, editMenu, delete])
        }
    )
}

// Commit — called when user taps the preview
func collectionView(_ collectionView: UICollectionView,
                    willPerformPreviewActionForMenuWith configuration: UIContextMenuConfiguration,
                    animator: UIContextMenuInteractionCommitAnimating) {
    animator.preferredCommitStyle = .pop
    animator.addCompletion {
        guard let indexPath = configuration.identifier as? IndexPath else { return }
        self.navigateTo(self.items[indexPath.item])
    }
}
```

**Menu hierarchy**: Nest `UIMenu` inside `UIMenu.children` to create submenus. Mark destructive actions with `.destructive` attribute — they render in red. Use `.displayInline` on a `UIMenu` to flatten its children into the parent without a submenu chevron.

---

## SECTION 6: Bottom Sheets with UISheetPresentationController

```swift
func presentBottomSheet() {
    let sheet = FilterViewController()
    sheet.modalPresentationStyle = .pageSheet

    if let sheetController = sheet.sheetPresentationController {
        sheetController.detents = [
            .medium(),
            .large(),
            .custom(identifier: .init("third")) { context in  // iOS 16+
                return context.maximumDetentValue * 0.35
            }
        ]
        sheetController.selectedDetentIdentifier = .medium
        sheetController.largestUndimmedDetentIdentifier = .medium  // no dim at .medium
        sheetController.prefersScrollingExpandsWhenScrolledToEdge = true
        sheetController.prefersGrabberVisible = true
        sheetController.prefersEdgeAttachedInCompactHeight = true
        sheetController.widthFollowsPreferredContentSizeWhenEdgeAttached = true
    }
    present(sheet, animated: true)
}

// Animate detent change programmatically:
func expandSheet(_ sheet: UIViewController) {
    sheet.sheetPresentationController?.animateChanges {
        sheet.sheetPresentationController?.selectedDetentIdentifier = .large
    }
}
```

**`largestUndimmedDetentIdentifier`**: Set to `.medium` so the presenting view remains interactive when the sheet is at half height — essential for map + sheet layouts.

---

## SECTION 7: NSFetchedResultsController with Diffable Data Source

```swift
class CoreDataViewController: UIViewController, NSFetchedResultsControllerDelegate {
    private var frc: NSFetchedResultsController<Task>!
    private var dataSource: UITableViewDiffableDataSource<String, NSManagedObjectID>!

    func setupFRC() {
        let request = Task.fetchRequest()
        request.sortDescriptors = [NSSortDescriptor(key: "createdAt", ascending: false)]
        frc = NSFetchedResultsController(
            fetchRequest: request,
            managedObjectContext: viewContext,
            sectionNameKeyPath: "status",  // groups rows into sections by status
            cacheName: nil
        )
        frc.delegate = self
        try? frc.performFetch()
        applyCurrentSnapshot()
    }

    private func applyCurrentSnapshot() {
        var snapshot = NSDiffableDataSourceSnapshot<String, NSManagedObjectID>()
        frc.sections?.forEach { section in
            snapshot.appendSections([section.name])
            snapshot.appendItems(
                (section.objects as? [Task])?.map(\.objectID) ?? [],
                toSection: section.name
            )
        }
        dataSource.apply(snapshot, animatingDifferences: false)
    }

    // iOS 13+ bridge — FRC hands you a ready-made snapshot reference
    func controller(_ controller: NSFetchedResultsController<NSFetchRequestResult>,
                    didChangeContentWith snapshot: NSDiffableDataSourceSnapshotReference) {
        let snap = snapshot as NSDiffableDataSourceSnapshot<String, NSManagedObjectID>
        dataSource.apply(snap, animatingDifferences: true)
    }
}
```

**Why `NSManagedObjectID` as the item identifier**: Object IDs are stable, unique, and `Hashable`. Avoid using the managed object itself — equality semantics are context-dependent and can cause incorrect diffs.

---

## SECTION 8: Prefetching for Smooth Scrolling

```swift
// Register prefetch data source
tableView.prefetchDataSource = self

// UITableViewDataSourcePrefetching
extension FeedViewController: UITableViewDataSourcePrefetching {
    func tableView(_ tableView: UITableView, prefetchRowsAt indexPaths: [IndexPath]) {
        let urls = indexPaths.compactMap { items[$0.row].imageURL }
        ImagePrefetcher.shared.prefetch(urls: urls)  // Kingfisher / SDWebImage
    }

    func tableView(_ tableView: UITableView, cancelPrefetchingForRowsAt indexPaths: [IndexPath]) {
        let urls = indexPaths.compactMap { items[$0.row].imageURL }
        ImagePrefetcher.shared.cancel(urls: urls)  // cancel saves bandwidth
    }
}

// NSCache for in-memory image caching
private let imageCache: NSCache<NSURL, UIImage> = {
    let cache = NSCache<NSURL, UIImage>()
    cache.countLimit = 100
    cache.totalCostLimit = 50 * 1024 * 1024  // 50 MB
    return cache
}()
// NSCache auto-evicts under memory pressure — never use a plain Dictionary for image caches
```

**`UICollectionViewDataSourcePrefetching`** mirrors the same pattern — set `collectionView.prefetchDataSource` and implement `prefetchItemsAt` / `cancelPrefetchingForItemsAt`.

---

## SECTION 9: Production Anti-Patterns

| Anti-Pattern | Consequence | Fix |
|---|---|---|
| `beginUpdates/endUpdates` with concurrent data changes | Index-out-of-bounds crash | Diffable data source |
| Hard-coded column count in compositional layout | Broken layout on iPad / large screens | `environment.container.effectiveContentSize` |
| `transitioningDelegate` set inline without retention | Silent fallback to default transition | Store as strong property on presenter |
| `reloadItems` for content-only updates (iOS 15+) | Flicker + unwanted height animation | `reconfigureItems` |
| Creating new `UIViewPropertyAnimator` on each `.changed` event | Broken interactive scrubbing | Create once in `.began`, scrub in `.changed` |
| Skipping `previewProvider` on context menus | Generic screenshot preview (less premium) | Always provide a custom `previewProvider` |
| `UITableView` for complex multi-section + carousel layouts | Unmanageable layout code | `UICollectionViewCompositionalLayout` with list config |
| Using managed objects directly as diffable identifiers | Unstable diffs, incorrect animations | Use `NSManagedObjectID` as identifier |
| Not cancelling prefetch requests | Wasted bandwidth, unnecessary decoding | Always implement `cancelPrefetchingForRowsAt` |

---

## Quick-Reference Checklist

- [ ] Model types used as diffable items conform to `Hashable` via a stable `id` field
- [ ] `reconfigureItems` used (not `reloadItems`) for content-only cell updates on iOS 15+
- [ ] Compositional layout columns derived from `environment.container.effectiveContentSize`
- [ ] `transitioningDelegate` retained as a strong stored property
- [ ] `UIViewPropertyAnimator` created once in gesture `.began`, not `.changed`
- [ ] Context menu `previewProvider` implemented for every item-level menu
- [ ] `NSManagedObjectID` used as the diffable identifier for Core Data items
- [ ] `cancelPrefetchingForRowsAt` implemented alongside `prefetchRowsAt`
- [ ] Bottom sheet `largestUndimmedDetentIdentifier` set when presenting over interactive content
