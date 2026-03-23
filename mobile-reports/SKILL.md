---
name: mobile-reports
description: "Best practices for designing mobile-optimized reports in Android (Jetpack Compose) and iOS (SwiftUI) apps. Use when implementing report screens, data visualization, export functionality, or any feature that displays aggregated data, analytics, or business intelligence on mobile devices."
---

# Mobile Reports

## Required Plugins

**Superpowers plugin:** MUST be active for all work using this skill.

## Overview

Mobile reports require different design considerations than desktop reports due to screen size, touch interactions, and usage patterns. This skill provides proven patterns for creating effective, readable, and performant report experiences in **Android (Jetpack Compose / Material 3)** and **iOS (SwiftUI)**.

- **Android:** 10+ required. Use custom PNG icons only (`painterResource(R.drawable.<name>)`).
- **iOS:** iOS 16+ required. Use SF Symbols or custom assets.
- **Report Table Policy:** If a report can exceed 25 rows, use a table layout (see `android-report-tables`).

## Core Principles

### 1. Responsive Layout with Relative Positioning

- Use relative sizing instead of fixed values
- Design for both portrait and landscape orientations
- Adapt columns/layout based on device size
- Use `LazyColumn`/`LazyRow` (Android) or `List`/`ScrollView` (iOS) for scrollable content

### 2. Progressive Disclosure

- Show summary/overview first, details on demand
- Use expandable cards or drill-down navigation for detailed data
- Implement infinite scroll pagination for large datasets
- Load data progressively (initial view fast, details on interaction)

### 3. Touch-Friendly Interactions

- Minimum tap target: **48dp (Android) / 44pt (iOS)**
- Use bottom sheets for filters and actions (thumb-reachable)
- Implement swipe gestures for common actions (refresh, delete)
- Provide visual feedback for all interactions

### 4. Readable Typography

- **Minimum font size:** 14sp/pt for body text, 16sp/pt preferred
- **Line spacing:** 1.5x line height for readability
- **Contrast:** WCAG AA compliance (4.5:1 for normal text)
- Limit text column width for comfortable reading

### 5. Data Visualization

- **Charts:** Use **Vico** (Android) or **Swift Charts** (iOS)
- **Tables:** Limit to 3-4 columns on phone, 5-6 on tablet
- **Avoid nested tables** — use grouped sections or pagination
- **Color coding:** Use sparingly; never colour-only indicators

### 6. Performance Optimization

- Lazy load data with pagination (offset or cursor-based)
- Cache rendered reports/charts (`remember`/`derivedStateOf` on Android; `@State`/computed on iOS)
- Use stable keys in list items for efficient diffing
- Defer expensive calculations to background threads/coroutines

## Report Layout Patterns

### Pattern 1: Summary Card + Detail List

**Android (Jetpack Compose):**

```kotlin
@Composable
fun InventoryReportScreen(state: ReportState) {
    LazyColumn {
        item { SummaryCard(state.totalValue, state.itemCount, state.lowStockCount) }
        stickyHeader { FilterBar(state.filter, onFilterChange = { /* ... */ }) }
        items(state.items, key = { it.id }) { item -> ReportItemCard(item) }
        if (state.hasMore) {
            item { LoadMoreTrigger(onLoadMore = { /* ... */ }) }
        }
    }
}
```

**iOS (SwiftUI):**

```swift
struct InventoryReportView: View {
    @StateObject private var viewModel = ReportViewModel()

    var body: some View {
        List {
            Section { SummaryCard(state: viewModel.summary) }
            Section {
                ForEach(viewModel.items) { item in
                    ReportItemRow(item: item)
                }
            }
        }
        .refreshable { await viewModel.reload() }
        .searchable(text: $viewModel.searchText)
    }
}
```

### Pattern 1b: Table-First Paginated Report (25+ Rows)

Use when the report can exceed 25 rows. Table with sticky header and floating footer.

```kotlin
@Composable
fun PaginatedReportScreen(allData: List<ReportItem>) {
    val pageSize = 25
    var currentPage by remember { mutableIntStateOf(1) }
    val totalPages = maxOf(1, ceil(allData.size.toDouble() / pageSize).toInt())
    val pagedItems = remember(currentPage, allData) {
        val start = (currentPage - 1) * pageSize
        allData.subList(start, minOf(start + pageSize, allData.size))
    }

    Scaffold(
        bottomBar = { TablePaginationController(currentPage, totalPages) { currentPage = it } }
    ) { padding ->
        LazyColumn(modifier = Modifier.padding(padding).fillMaxSize()) {
            stickyHeader {
                ReportRow(listOf("ID", "Customer", "Amount"), isHeader = true, weights = listOf(0.2f, 0.5f, 0.3f))
            }
            items(pagedItems) { item ->
                ReportRow(listOf(item.id, item.name, item.amount), weights = listOf(0.2f, 0.5f, 0.3f))
            }
        }
    }
}
```

On iOS, use a `List` with `.listStyle(.plain)` and a custom pagination bar in a `VStack` footer.

### Pattern 2: Tab-Based Multi-Report

**Android:**

```kotlin
@Composable
fun ReportsScreen() {
    var selectedTab by remember { mutableStateOf(0) }
    val tabs = listOf("Sales", "Inventory", "Customers")
    Column {
        TabRow(selectedTabIndex = selectedTab) {
            tabs.forEachIndexed { index, title ->
                Tab(selected = selectedTab == index, onClick = { selectedTab = index }, text = { Text(title) })
            }
        }
        when (selectedTab) {
            0 -> SalesReportContent()
            1 -> InventoryReportContent()
            2 -> CustomersReportContent()
        }
    }
}
```

**iOS:**

```swift
struct ReportsView: View {
    var body: some View {
        TabView {
            SalesReportContent().tabItem { Label("Sales", image: "sales") }
            InventoryReportContent().tabItem { Label("Inventory", image: "inventory") }
            CustomersReportContent().tabItem { Label("Customers", image: "customers") }
        }
    }
}
```

### Pattern 3: Filter Bottom Sheet + Results

**Android:**

```kotlin
@Composable
fun FilterableReportScreen(viewModel: ReportViewModel) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    var showFilters by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Sales Report") },
                actions = {
                    IconButton(onClick = { showFilters = true }) {
                        Icon(painterResource(R.drawable.filter), "Filters")
                    }
                }
            )
        }
    ) { padding ->
        ReportContent(data = state.data, modifier = Modifier.padding(padding))
    }

    if (showFilters) {
        ModalBottomSheet(onDismissRequest = { showFilters = false }) {
            FilterForm(currentFilters = state.filters, onApply = { viewModel.applyFilters(it); showFilters = false })
        }
    }
}
```

**iOS:**

```swift
struct FilterableReportView: View {
    @StateObject private var viewModel = ReportViewModel()
    @State private var showFilters = false

    var body: some View {
        NavigationStack {
            ReportContent(data: viewModel.data)
                .toolbar {
                    Button { showFilters = true } label: { Image("filter") }
                }
                .sheet(isPresented: $showFilters) {
                    FilterForm(filters: $viewModel.filters)
                }
        }
    }
}
```

## Interactive Filtering

### Date Range Selection

```kotlin
@Composable
fun DateRangeFilter(startDate: LocalDate, endDate: LocalDate, onRangeChange: (LocalDate, LocalDate) -> Unit) {
    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        OutlinedButton(onClick = { /* date picker */ }, modifier = Modifier.weight(1f)) { Text("From: ${startDate.format()}") }
        OutlinedButton(onClick = { /* date picker */ }, modifier = Modifier.weight(1f)) { Text("To: ${endDate.format()}") }
    }
}
```

On iOS, use `DatePicker` with `.datePickerStyle(.compact)` in a similar two-column layout.

### Quick Filters (Chips)

```kotlin
@Composable
fun QuickFilters(options: List<FilterOption>, selected: FilterOption?, onSelect: (FilterOption) -> Unit) {
    LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp), contentPadding = PaddingValues(horizontal = 16.dp)) {
        items(options) { option ->
            FilterChip(selected = option == selected, onClick = { onSelect(option) }, label = { Text(option.label) })
        }
    }
}
```

On iOS, use a horizontal `ScrollView` with `Toggle` buttons or a segmented `Picker`.

## Table Design for Mobile

### Avoid This (Too Many Columns)

```
| SKU | Name | Category | Qty | Unit | Value | Location | Status |
```

### Do This Instead

Use **card-based layouts** that show primary info (name + value) prominently, secondary info (qty, category, location) in a grid row below, and status as a badge. This adapts naturally to any screen width. See Pattern 1 for the structural approach.

## Export Functionality

**Formats:** PDF (sharing/printing), CSV (spreadsheet analysis), Share (messaging apps).

**Android:** Use a `DropdownMenu` with export options triggered from the `TopAppBar` actions area.

```kotlin
@Composable
fun ExportMenu(onExportPdf: () -> Unit, onExportCsv: () -> Unit, onShare: () -> Unit) {
    var expanded by remember { mutableStateOf(false) }
    IconButton(onClick = { expanded = true }) { Icon(painterResource(R.drawable.share), "Export") }
    DropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
        DropdownMenuItem(text = { Text("Export as PDF") }, onClick = { expanded = false; onExportPdf() })
        DropdownMenuItem(text = { Text("Export as CSV") }, onClick = { expanded = false; onExportCsv() })
        DropdownMenuItem(text = { Text("Share Report") }, onClick = { expanded = false; onShare() })
    }
}
```

**iOS:** Use `UIActivityViewController` (via `ShareLink` in SwiftUI) for the native share sheet. For PDF generation, use `UIGraphicsPDFRenderer`.

## Chart Integration

- **Android:** Use **Vico** — 100% Kotlin, Compose-native, actively maintained. Read the official guide at `guide.vico.patrykandpatrick.com`. Use the Compose artifact for new screens.
- **iOS:** Use **Swift Charts** (iOS 16+) — Apple's native declarative charting framework. Integrates directly with SwiftUI.

Both libraries support line, bar, area, and pie charts suitable for business reports.

## Loading and Empty States

Provide clear feedback for all report states. Both platforms need:

- **Loading:** Centered spinner/progress indicator with "Generating report..." text.
- **Empty:** Large icon + message ("No data for the selected period") + optional action button (clear filters, change dates).
- **Error:** Descriptive message + retry button.

Android: Use `CircularProgressIndicator` and composable empty/error screens.
iOS: Use `ProgressView` and `ContentUnavailableView` (iOS 17+) or a custom empty view.

## Common Pitfalls

### Avoid

- Fixed pixel widths (breaks on different screen sizes)
- More than 4 columns in tables on phone screens
- Nested scrollable containers (`LazyColumn` in `LazyColumn` / `List` in `ScrollView`)
- Colour-only indicators without text or icons (accessibility)
- Loading entire dataset at once (performance)
- Font sizes below 14sp/pt (readability)

### Do

- Relative sizing (`fillMaxWidth`, `weight` / `.frame(maxWidth: .infinity)`)
- Card-based layouts for multi-column data
- Single scroll container with mixed content types
- Icons/badges + colour for status indicators
- Pagination with infinite scroll
- 16sp/pt+ for body text, 14sp/pt minimum

## Architecture Pattern

**Android:**

```
presentation/reports/
├── screens/          # ReportListScreen, SalesReportScreen, InventoryReportScreen
├── viewmodels/       # SalesReportViewModel, InventoryReportViewModel
├── components/       # SummaryCard, FilterBottomSheet, DateRangeSelector, ExportMenu, ReportChart
└── export/           # PdfExporter, CsvExporter
domain/usecase/reports/  # GetSalesReportUseCase, ExportReportUseCase
data/repository/         # ReportsRepositoryImpl (API + caching)
```

**iOS:**

```
Features/Reports/
├── Views/            # ReportListView, SalesReportView, InventoryReportView
├── ViewModels/       # SalesReportViewModel, InventoryReportViewModel
├── Components/       # SummaryCard, FilterSheet, ReportChart
└── Services/         # PdfExporter, CsvExporter
```

## Report Types Reference

See [references/report-types.md](references/report-types.md) for detailed patterns for:

- Financial reports (Sales, Revenue, Expenses)
- Inventory reports (Stock levels, Movements, Valuations)
- Analytics reports (User activity, Performance metrics)
- Transaction reports (Order history, Payment logs)

## Testing Considerations

- Test with real data volumes (100s of items, not just 5)
- Verify scrolling performance with large datasets
- Test landscape orientation
- Test on small phones (5" / iPhone SE) and tablets (iPad)
- Verify export functionality with actual file creation
- Test loading/error/empty states
- Verify filter combinations work correctly
- Test pagination edge cases (last page, refresh)

## Performance Checklist

- [ ] Pagination implemented (20-50 items per page)
- [ ] Lazy list used (`LazyColumn` / `List`)
- [ ] Expensive calculations cached (`remember`/`derivedStateOf` / `@State`/computed)
- [ ] Background processing for data (`Dispatchers.IO` / `Task { }`)
- [ ] Image loading optimised (if applicable)
- [ ] Chart rendering cached
- [ ] No blocking operations on main thread
- [ ] Stable keys in list items (`key()` / `id:`)
