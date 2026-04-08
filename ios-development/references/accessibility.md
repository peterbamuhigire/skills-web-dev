# iOS Accessibility Standards

**App Store Requirement.** Apple's App Review Guidelines require apps to work with VoiceOver and support Dynamic Type. Accessibility bugs are among the most common App Review rejections.

## Table of Contents

1. [Dynamic Type — Text Scaling](#1-dynamic-type--text-scaling)
2. [VoiceOver Labels & Traits](#2-voiceover-labels--traits)
3. [SwiftUI Accessibility Modifiers](#3-swiftui-accessibility-modifiers)
4. [UIKit Accessibility](#4-uikit-accessibility)
5. [Testing Accessibility](#5-testing-accessibility)

---

## 1. Dynamic Type — Text Scaling

All text must scale with the user's preferred text size (Settings → Accessibility → Larger Text).

**SwiftUI** — use text styles, never hardcoded sizes:

```swift
// CORRECT — scales with Dynamic Type
Text("Invoice Total")
    .font(.headline)            // .largeTitle, .title, .body, .caption, etc.

Text("UGX 450,000")
    .font(.title2)
    .fontWeight(.bold)

// CORRECT — custom font that scales
Text("Amount")
    .font(.custom("Georgia", size: 17, relativeTo: .body))

// WRONG — fixed size, fails accessibility audit
Text("Label")
    .font(.system(size: 14))   // ← never hardcode sizes
```

**UIKit**:
```swift
// CORRECT
label.font = UIFont.preferredFont(forTextStyle: .body)
label.adjustsFontForContentSizeCategory = true  // REQUIRED

// CORRECT — custom font that scales
label.font = UIFontMetrics(forTextStyle: .body)
    .scaledFont(for: UIFont(name: "Georgia", size: 17)!)
label.adjustsFontForContentSizeCategory = true
```

**Layout for large text:**
```swift
// Allow labels to wrap — never truncate body text
label.numberOfLines = 0
label.lineBreakMode = .byWordWrapping

// SwiftUI: use .dynamicTypeSize to handle extreme sizes
Text("Invoice")
    .dynamicTypeSize(.small ... .accessibility3)  // limit if layout breaks at extremes
```

---

## 2. VoiceOver Labels & Traits

VoiceOver reads `accessibilityLabel` when a user touches an element. Without it, VoiceOver reads the raw value (e.g., "Button" or a filename), which is meaningless.

**Elements requiring labels:**
- Images that convey meaning
- Buttons with icon-only content
- Custom views
- Graphics and charts

**Elements that must be hidden** (decorative/redundant):
- Background images
- Icons next to labelled text

---

## 3. SwiftUI Accessibility Modifiers

```swift
// Image — describe what it shows, not "icon" or "image"
Image("invoice_icon")
    .accessibilityLabel("Invoice")
    .accessibilityHidden(false)

// Decorative image — screen reader skips it entirely
Image("background_texture")
    .accessibilityHidden(true)

// Button with icon only
Button { shareAction() } label: {
    Image(systemName: "square.and.arrow.up")
}
.accessibilityLabel("Share invoice")
.accessibilityHint("Opens share sheet")

// Group elements into a single readable unit
VStack(alignment: .leading) {
    Text("Order #1042")
    Text("UGX 85,000")
    Text("Pending")
}
.accessibilityElement(children: .combine)
// VoiceOver reads: "Order #1042, UGX 85,000, Pending"

// Custom actions (VoiceOver swipe actions)
ProductRow(product: product)
    .accessibilityAction(named: "Delete") { deleteProduct(product) }
    .accessibilityAction(named: "Add to cart") { addToCart(product) }

// Traits — describe the role and state
Toggle("Dark mode", isOn: $darkMode)
    .accessibilityAddTraits(.isButton)

Text(isExpanded ? "Collapse" : "Expand")
    .accessibilityAddTraits(isExpanded ? .isSelected : [])

// Chart / data display
Chart(data) { item in
    BarMark(x: .value("Month", item.month), y: .value("Sales", item.sales))
}
.accessibilityChartDescriptor(SalesChartDescriptor(data: data))
```

---

## 4. UIKit Accessibility

```swift
// Custom UIView — override accessibilityLabel
class PriceCell: UITableViewCell {
    override var accessibilityLabel: String? {
        get { "\(productName), \(formattedPrice)" }
        set { super.accessibilityLabel = newValue }
    }

    override var accessibilityHint: String? {
        get { "Double tap to view product details" }
        set { super.accessibilityHint = newValue }
    }
}

// UIButton with icon only
iconButton.accessibilityLabel = "Filter results"
iconButton.accessibilityTraits = .button

// Decorative image
backgroundImageView.isAccessibilityElement = false

// UIAccessibility.post — announce dynamic changes
UIAccessibility.post(notification: .announcement,
                     argument: "Order saved successfully")

// Screen changed — focus VoiceOver on new content
UIAccessibility.post(notification: .screenChanged,
                     argument: successLabel)
```

---

## 5. Testing Accessibility

**Xcode Accessibility Inspector** (Xcode menu → Open Developer Tool → Accessibility Inspector):
- Audit tab: scans for accessibility issues automatically
- Inspection: select any element to see its label, hint, traits, value
- Run on simulator for every new screen

**Automated accessibility tests:**
```swift
func test_productList_hasAccessibilityLabels() {
    let cell = app.cells.firstMatch
    XCTAssertFalse(cell.label.isEmpty, "Cell must have an accessibility label")
}

// SwiftUI accessibility identifier for XCUITest
ProductRow(product: product)
    .accessibilityIdentifier("product_row_\(product.id)")
```

**VoiceOver manual testing:**
1. Settings → Accessibility → VoiceOver → On
2. Navigate through every screen with swipes only
3. Every interactive element must be reachable and clearly labelled
4. Every form field must announce its label before the current value

**Minimum requirements for App Store approval:**
- [ ] All images have `accessibilityLabel` or `accessibilityHidden(true)`
- [ ] All icon-only buttons have `accessibilityLabel`
- [ ] All text uses Dynamic Type text styles (no hardcoded sizes)
- [ ] `adjustsFontForContentSizeCategory = true` on all UILabels
- [ ] `numberOfLines = 0` on all body text UILabels
- [ ] No essential information conveyed by color alone
