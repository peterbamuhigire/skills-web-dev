# Advanced UIKit Interactions

Load when implementing drawing surfaces, physics animations, or adaptive iPad layouts.

## Table of Contents

1. [Touch Prediction & Coalescing (Drawing Apps)](#1-touch-prediction--coalescing-drawing-apps)
2. [UIKit Dynamics (Physics Simulation)](#2-uikit-dynamics-physics-simulation)
3. [iPad Size Class Transitions](#3-ipad-size-class-transitions)
4. [Adaptive Layouts for Multitasking](#4-adaptive-layouts-for-multitasking)

---

## 1. Touch Prediction & Coalescing (Drawing Apps)

Standard `touchesMoved` only fires once per frame (60Hz). At high speed, strokes look jagged. UIKit provides two systems to fix this.

### Coalesced Touches — Sub-Frame Accuracy

```swift
override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
    guard let touch = touches.first, let event else { return }

    // coalescedTouches provides ALL touch samples between frames — not just the last one.
    // Use for drawing: every intermediate point is included.
    let coalescedTouches = event.coalescedTouches(for: touch) ?? [touch]
    for coalescedTouch in coalescedTouches {
        let point = coalescedTouch.location(in: self)
        let force = coalescedTouch.force   // Apple Pencil / 3D Touch
        currentPath.addLine(to: point)
    }
    setNeedsDisplay()
}
```

### Predicted Touches — Latency Compensation

```swift
override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
    guard let touch = touches.first, let event else { return }

    // predictedTouches gives UIKit's best guess for where the finger will be next frame.
    // Draw these in a separate "prediction" layer with lower opacity.
    // Erase and redraw with real coalesced touches on the next frame.
    let predicted = event.predictedTouches(for: touch) ?? []
    drawPredictionLayer(predicted)
}
```

**Rules:**
- Use `coalescedTouches` for the committed stroke layer (permanent, accurate)
- Use `predictedTouches` for a transient prediction layer (ephemeral, erased each frame)
- Always check `touch.estimationUpdateIndex` for Apple Pencil — force and azimuth can arrive after the touch event via `touchesEstimatedPropertiesUpdated`

---

## 2. UIKit Dynamics (Physics Simulation)

`UIDynamicAnimator` applies physics behaviours to any `UIDynamicItem` (usually `UIView`).

```swift
class PhysicsViewController: UIViewController {
    var animator: UIDynamicAnimator!
    var snap: UISnapBehavior?

    override func viewDidLoad() {
        super.viewDidLoad()
        animator = UIDynamicAnimator(referenceView: view)
        setupPhysics()
    }

    func setupPhysics() {
        let card = cardView

        // Gravity — pulls card downward
        let gravity = UIGravityBehavior(items: [card])
        gravity.magnitude = 0.8
        animator.addBehavior(gravity)

        // Collision — card bounces off the safe area edges
        let collision = UICollisionBehavior(items: [card])
        collision.translatesReferenceBoundsIntoBoundary = true
        animator.addBehavior(collision)

        // Item behaviour — elasticity and friction
        let item = UIDynamicItemBehavior(items: [card])
        item.elasticity = 0.6   // bounce: 0 = no bounce, 1 = perfectly elastic
        item.friction = 0.2
        item.resistance = 0.1   // linear damping
        item.angularResistance = 0.4
        animator.addBehavior(item)
    }

    // Snap to a specific point (e.g., after drag release)
    func snapCard(to point: CGPoint) {
        if let existing = snap { animator.removeBehavior(existing) }
        snap = UISnapBehavior(item: cardView, snapTo: point)
        snap!.damping = 0.6
        animator.addBehavior(snap!)
    }

    // Throw with velocity — attach to pan gesture
    @objc func handlePan(_ gesture: UIPanGestureRecognizer) {
        let location = gesture.location(in: view)
        let velocity = gesture.velocity(in: view)

        switch gesture.state {
        case .changed:
            cardView.center = location
            animator.updateItem(usingCurrentState: cardView)

        case .ended:
            let push = UIPushBehavior(items: [cardView], mode: .instantaneous)
            push.pushDirection = CGVector(dx: velocity.x / 100, dy: velocity.y / 100)
            push.magnitude = 0.5
            animator.addBehavior(push)

        default: break
        }
    }
}
```

**Available Behaviours:**

| Behaviour | Purpose |
|---|---|
| `UIGravityBehavior` | Constant directional force |
| `UICollisionBehavior` | Boundary and item-to-item collisions |
| `UIAttachmentBehavior` | Spring/rope link between two items |
| `UISnapBehavior` | Spring-snap to a point |
| `UIPushBehavior` | One-shot or continuous force vector |
| `UIDynamicItemBehavior` | Per-item properties: elasticity, density, friction |

**Performance note**: `UIDynamicAnimator` uses a physics timestep, not the display link — it self-throttles. No need to stop it manually unless you want to freeze the simulation.

---

## 3. iPad Size Class Transitions

iPad multitasking (Split View, Slide Over, Stage Manager) changes the app's size class dynamically. Handle in two callbacks:

```swift
// Fires when the trait collection changes (size class, appearance, etc.)
override func willTransition(to newCollection: UITraitCollection,
                              with coordinator: UIViewControllerTransitionCoordinator) {
    super.willTransition(to: newCollection, with: coordinator)

    coordinator.animate { _ in
        // Reconfigure layout based on new horizontal size class
        if newCollection.horizontalSizeClass == .compact {
            self.switchToSingleColumn()
        } else {
            self.switchToTwoColumn()
        }
        self.view.layoutIfNeeded()
    }
}

// Fires when the view's bounds change (e.g., drag resize in multitasking)
override func viewWillTransition(to size: CGSize,
                                  with coordinator: UIViewControllerTransitionCoordinator) {
    super.viewWillTransition(to: size, with: coordinator)

    coordinator.animate { _ in
        // Recalculate compositional layout for new width
        self.collectionView.collectionViewLayout.invalidateLayout()
        self.view.layoutIfNeeded()
    }
}
```

**Both must be implemented**: `willTransition(to:with:)` fires for trait changes; `viewWillTransition(to:with:)` fires for size changes. Drag-resizing in Stage Manager triggers `viewWillTransition` but not necessarily a trait change.

---

## 4. Adaptive Layouts for Multitasking

```swift
// Read current size class in layout code — do NOT cache it
func configureLayout() {
    let isCompact = traitCollection.horizontalSizeClass == .compact

    // Compositional layout adapts using environment (no size class check needed)
    let columns = traitCollection.horizontalSizeClass == .regular ? 3 : 2

    // NSLayoutConstraint activation/deactivation based on size class
    if isCompact {
        NSLayoutConstraint.deactivate(regularConstraints)
        NSLayoutConstraint.activate(compactConstraints)
    } else {
        NSLayoutConstraint.deactivate(compactConstraints)
        NSLayoutConstraint.activate(regularConstraints)
    }
}

override func traitCollectionDidChange(_ previousTraitCollection: UITraitCollection?) {
    super.traitCollectionDidChange(previousTraitCollection)
    guard traitCollection.horizontalSizeClass != previousTraitCollection?.horizontalSizeClass else { return }
    configureLayout()
}
```

**Opting out of multitasking** — only valid when the app requires full screen (video recording, AR):
Add `UIRequiresFullScreen = YES` to `Info.plist`. This disables Split View and Slide Over for your app. Apple may reject this for apps where it is not justified.
