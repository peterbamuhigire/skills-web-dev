---
name: swiftui-design
description: "SwiftUI UI standards for beautiful, sleek, minimalistic iOS apps. Enforces modern SwiftUI patterns, consistent theming, smooth animations, and performance. Use when building or reviewing SwiftUI code to ensure modern, user-friendly interfaces standard across all apps."
---

## Required Plugins

**Superpowers plugin:** MUST be active for all work using this skill. Use throughout the entire build pipeline — design decisions, code generation, debugging, quality checks, and any task where it offers enhanced capabilities. If superpowers provides a better way to accomplish something, prefer it over the default approach.

# SwiftUI UI Standards

## Design Philosophy

**Goal:** Every screen should feel beautiful, sleek, fast, and effortless to use.

### Core Design Principles

1. **Minimalism over decoration** — Content first, chrome last. Remove anything that doesn't serve the user.
2. **Consistency over novelty** — Same patterns across every app screen.
3. **Whitespace is a feature** — Generous spacing creates visual breathing room, not waste.
4. **Speed is UX** — If it feels slow, it's broken regardless of how it looks.
5. **Content-first hierarchy** — Important information is immediately visible.
6. **Touch-friendly targets** — Minimum 44pt for all interactive elements (Apple HIG).
7. **SF Symbols for icons** — Use SF Symbols for system icons unless custom icons are required per `mobile-custom-icons`.
8. **iOS 26 Liquid Glass** — For apps recompiled against iOS 26 SDK, adopt the Liquid Glass design language for translucent materials and depth.

### Visual Standards

| Element | Standard |
|---|---|
| **Corner radius** | 12pt cards, 8pt inputs, continuous corners via `.clipShape(RoundedRectangle(cornerRadius:, style: .continuous))` |
| **Card elevation** | Use `.shadow(radius: 2, y: 1)` — subtle, never heavy |
| **Content padding** | 16pt horizontal, 8-16pt vertical between items |
| **Screen padding** | 16pt compact, 20pt regular |
| **Touch targets** | Minimum 44pt height/width (Apple HIG) |
| **Icon size** | SF Symbols: 17pt body, 22pt title, 48pt empty states |
| **Typography** | Use system `Font` API exclusively |

## Navigation Architecture (iOS 16+)

### NavigationStack (replaces NavigationView)

```swift
NavigationStack {
    List(items) { item in
        NavigationLink(value: item) {
            ItemRow(item: item)
        }
    }
    .navigationTitle("Items")
    .navigationDestination(for: Item.self) { item in
        ItemDetailView(item: item)
    }
}
```

### NavigationSplitView for iPad multi-column

```swift
NavigationSplitView(columnVisibility: $columnVisibility) {
    SidebarView()
} content: {
    ContentView()
} detail: {
    DetailView()
}
```

### Programmatic navigation with NavigationPath

```swift
@State private var path = NavigationPath()

NavigationStack(path: $path) {
    // Push: path.append(item)
    // Pop: path.removeLast()
    // Pop to root: path = NavigationPath()
}
```

**Rule:** Always use `NavigationStack`, never `NavigationView` (deprecated).

## TabView Architecture

```swift
struct MainTabView: View {
    @State private var selectedTab = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            NavigationStack { DashboardView() }
                .tabItem { Label("Home", image: "home") }
                .tag(0)
            NavigationStack { SalesView() }
                .tabItem { Label("Sales", image: "sales") }
                .tag(1)
            // Max 5 tabs
        }
    }
}
```

**Rule:** `NavigationStack` INSIDE each tab — this keeps the tab bar visible on push navigation.

## Modal Presentations

### Sheets

```swift
// Boolean sheet
.sheet(isPresented: $showSheet) { SheetContent() }

// Item-based sheet
.sheet(item: $selectedItem) { item in DetailView(item: item) }

// Full screen cover
.fullScreenCover(isPresented: $showLogin) { LoginView() }

// Bottom sheet with detents (iOS 16+)
.sheet(isPresented: $showFilter) {
    FilterView()
        .presentationDetents([.medium, .large])
        .presentationDragIndicator(.visible)
}
```

### Alerts (modern API — NOT Alert() struct)

```swift
.alert("Delete Item?", isPresented: $showDelete) {
    Button("Delete", role: .destructive) { deleteItem() }
    Button("Cancel", role: .cancel) { }
} message: {
    Text("This cannot be undone.")
}
```

### Confirmation Dialog (replaces ActionSheet)

```swift
.confirmationDialog("Options", isPresented: $showOptions) {
    Button("Edit") { }
    Button("Delete", role: .destructive) { }
}
```

## Lists and Grids

### Standard List with Pull-to-Refresh and Search

```swift
List {
    ForEach(items) { item in
        ItemRow(item: item)
    }
}
.refreshable { await viewModel.reload() }
.searchable(text: $searchText, prompt: "Search items")
```

### Swipe Actions

```swift
.swipeActions(edge: .trailing) {
    Button(role: .destructive) { delete(item) } label: {
        Label("Delete", systemImage: "trash")
    }
}
.swipeActions(edge: .leading) {
    Button { toggleFavorite(item) } label: {
        Label("Favorite", systemImage: "star")
    }
    .tint(.yellow)
}
```

### Lazy Grids

```swift
LazyVGrid(columns: [GridItem(.adaptive(minimum: 160))], spacing: 16) {
    ForEach(items) { item in
        ItemCard(item: item)
    }
}
```

**Rule:** Use `List` for standard table content (automatic lazy loading). Use `LazyVStack`/`LazyHStack` inside `ScrollView` for custom layouts with large datasets.

## Theming System

### Central Theme Definition

```swift
enum AppTheme {
    static let cornerRadius: CGFloat = 12
    static let cardPadding: CGFloat = 16
    static let spacing: CGFloat = 8

    // Custom colors via Asset Catalog
    static let primary = Color("PrimaryColor")
    static let surface = Color("SurfaceColor")
}
```

### Consistent Card Pattern

```swift
struct CardView<Content: View>: View {
    let content: Content
    init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }

    var body: some View {
        content
            .padding(AppTheme.cardPadding)
            .background(.regularMaterial)
            .clipShape(RoundedRectangle(cornerRadius: AppTheme.cornerRadius,
                                         style: .continuous))
    }
}
```

### Spacing System (Design Tokens)

```swift
enum Spacing {
    static let xs: CGFloat = 4
    static let sm: CGFloat = 8
    static let md: CGFloat = 16
    static let lg: CGFloat = 24
    static let xl: CGFloat = 32
    static let xxl: CGFloat = 48
}
```

Use these exclusively. No arbitrary values like 13 or 19.

### Typography Hierarchy

| Style | Size | Usage |
|---|---|---|
| `.largeTitle` | 34pt | Screen titles |
| `.title` | 28pt | Section headers |
| `.title2` | 22pt | Subsection headers |
| `.headline` | 17pt semibold | Card titles, emphasis |
| `.body` | 17pt | Standard text |
| `.callout` | 16pt | Secondary text |
| `.footnote` | 13pt | Supporting details |
| `.caption` | 12pt | Metadata, timestamps |

### Spacing Reference

| Element | Size |
|---|---|
| Section gap | 24pt |
| Card padding | 16pt |
| List row padding | 12pt |
| Between related items | 8pt |

## Animation Standards

### Explicit Animation (preferred)

```swift
withAnimation(.spring(duration: 0.3)) {
    isExpanded.toggle()
}
```

### CRITICAL: Ternary for Animatable Properties

```swift
// BAD — breaks animation (creates new view identity)
if isActive { Text("Active").foregroundStyle(.green) }
else { Text("Active").foregroundStyle(.gray) }

// GOOD — preserves identity, animates smoothly
Text("Active").foregroundStyle(isActive ? .green : .gray)
```

### .animation with Explicit Value (NOT deprecated form)

```swift
.animation(.easeInOut, value: isLoading)
```

### Phase Animator (iOS 17)

```swift
PhaseAnimator([false, true]) { phase in
    content.scaleEffect(phase ? 1.1 : 1.0)
}
```

### Custom ViewModifier for Reusable Animations

```swift
struct ShakeModifier: ViewModifier {
    var shakes: CGFloat
    func body(content: Content) -> some View {
        content.offset(x: sin(shakes * .pi * 2) * 5)
    }
}
```

**Rules:** Keep animations under 300ms. Use `.spring()` for interactive elements, `.easeInOut` for state changes. Never animate on first appear unless it is a staggered list.

## Loading / Empty / Error States

Every async screen MUST handle all three states:

```swift
struct AsyncContentView<T, Content: View>: View {
    let isLoading: Bool
    let error: String?
    let data: T?
    let content: (T) -> Content

    var body: some View {
        if isLoading {
            ProgressView()
        } else if let error {
            ContentUnavailableView("Error",
                systemImage: "exclamationmark.triangle",
                description: Text(error))
        } else if let data {
            content(data)
        } else {
            ContentUnavailableView("No Data",
                systemImage: "tray",
                description: Text("Nothing to display"))
        }
    }
}
```

**Rule:** `ContentUnavailableView` (iOS 17+) is the standard for empty and error states.

## Form Design

```swift
Form {
    Section("Personal") {
        TextField("Name", text: $name)
        TextField("Email", text: $email)
            .keyboardType(.emailAddress)
            .textContentType(.emailAddress)
            .autocapitalization(.none)
    }
    Section("Preferences") {
        Picker("Role", selection: $role) {
            ForEach(Role.allCases, id: \.self) { Text($0.rawValue) }
        }
        Toggle("Notifications", isOn: $notifications)
        DatePicker("Start Date", selection: $date, displayedComponents: .date)
    }
}
```

**Rules:** Group related fields in `Section`. Use `.textContentType()` for autofill. Use appropriate `.keyboardType()` for every text field.

## Swift Charts (iOS 16+)

```swift
import Charts

Chart(salesData) { item in
    BarMark(
        x: .value("Month", item.month),
        y: .value("Revenue", item.revenue)
    )
    .foregroundStyle(by: .value("Category", item.category))
}
.chartXAxis { AxisMarks(values: .automatic) }
.frame(height: 200)
```

Use Swift Charts exclusively. Do not introduce third-party chart libraries.

## Data Flow Pattern

### @Observable (iOS 17+ — replaces ObservableObject)

```swift
@Observable
class FeatureViewModel {
    var items: [Item] = []
    var isLoading = false
    var error: String?

    func load() async {
        isLoading = true
        defer { isLoading = false }
        do {
            items = try await repository.fetchItems()
        } catch {
            self.error = error.localizedDescription
        }
    }
}

// Usage in View
struct FeatureView: View {
    @State private var viewModel = FeatureViewModel()

    var body: some View {
        List(viewModel.items) { item in
            ItemRow(item: item)
        }
        .task { await viewModel.load() }
    }
}
```

**Rule:** Use `@Observable` and `@State` for new code. Use `ObservableObject` and `@StateObject` only when targeting iOS 16.

## Performance Rules

1. **Use `LazyVStack`/`LazyHStack`** inside `ScrollView` for large datasets.
2. **`List`** for standard table content (automatic lazy loading).
3. **`.task { }`** for async loading — auto-cancels on disappear.
4. **`.drawingGroup()`** for heavy animation compositing.
5. **Never nest `ScrollView` inside `List`.**
6. **Use `.id()`** to force view recreation only when intentional.
7. **`remember` equivalents:** Use computed properties or `let` bindings for derived values. Avoid recomputing in `body` what can be cached.
8. **Stable identifiers in `ForEach`** — always provide `id:` or conform to `Identifiable`.

## Patterns and Anti-Patterns

### DO

- Use `NavigationStack` (not `NavigationView`)
- Use `@Observable` (not `ObservableObject`) for iOS 17+
- Use `.alert` ViewBuilder API (not `Alert()` struct)
- Use `.confirmationDialog` (not `ActionSheet`)
- Use `.animation(_:value:)` with explicit value binding
- Use ternary for animatable properties (not if/else)
- Use `.task {}` for async work (not `onAppear` + `Task {}`)
- Ensure 44pt minimum touch targets
- Add pull-to-refresh on all data screens
- Handle loading/empty/error states on every async screen
- Use `@ViewBuilder` for composable custom containers
- Provide `#Preview` for every public view

### DON'T

- Hardcode colors, dimensions, or font sizes
- Put business logic in Views
- Use `@State` for shared state (use `@Observable` ViewModel)
- Use `VStack`/`HStack` for long scrollable lists (use `LazyVStack`/`LazyHStack`)
- Skip empty/error states
- Use heavy animations that block the main thread
- Nest scrollable containers
- Use deprecated APIs (`NavigationView`, `Alert()`, `.animation()` without value)

## Modernisation Checklist

- [ ] `NavigationStack` (not `NavigationView`)
- [ ] `@Observable` (not `ObservableObject`) — iOS 17+
- [ ] `.alert` ViewBuilder (not `Alert()` struct)
- [ ] `.confirmationDialog` (not `ActionSheet`)
- [ ] `.animation(_:value:)` with explicit value
- [ ] Ternary for animatable properties (not if/else)
- [ ] `.task {}` for async work (not `onAppear` + `Task`)
- [ ] 44pt minimum touch targets
- [ ] Pull-to-refresh on data screens
- [ ] Loading/empty/error states on all async screens
- [ ] `ContentUnavailableView` for empty/error (iOS 17+)
- [ ] Swift Charts for data visualisation (not third-party)
- [ ] `#Preview` macro (not `PreviewProvider`)

## Integration with Other Skills

```
feature-planning  ->  Define screens, user stories, acceptance criteria
       |
swiftui-design    ->  Beautiful, consistent UI implementation (THIS SKILL)
       |
form-ux-design    ->  Cross-platform form UX patterns
       |
ux-psychology     ->  Cognitive science, design laws, accessibility
```

**Key integrations:**

- **feature-planning**: Screen specs become SwiftUI view implementations
- **form-ux-design**: Form layout, validation, and UX patterns
- **healthcare-ui-design**: Clinical-grade UI for health apps
- **ux-psychology**: Cognitive load, Fitts's Law, Hick's Law applied to iOS

## References

- **Apple HIG**: developer.apple.com/design/human-interface-guidelines
- **SwiftUI Documentation**: developer.apple.com/documentation/swiftui
- **SF Symbols**: developer.apple.com/sf-symbols
- **Swift Charts**: developer.apple.com/documentation/charts
- **WWDC Sessions**: developer.apple.com/videos (SwiftUI, Design tracks)
