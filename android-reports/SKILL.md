# Android Mobile Reports

---

name: android-reports
description: Best practices for designing mobile-optimized reports in Android apps using Jetpack Compose. Use when implementing report screens, data visualization, export functionality, or any feature that displays aggregated data, analytics, financial summaries, inventory reports, or business intelligence to users on mobile devices. Covers layout patterns, data presentation, filtering, interactivity, and export options.

---

## Overview

Mobile reports require different design considerations than desktop reports due to screen size, touch interactions, and usage patterns. This skill provides proven patterns for creating effective, readable, and performant report experiences in Android apps using Jetpack Compose and Material 3.

Android 10+ required.

**Icon Policy:** Use custom PNG icons only. Use `painterResource(R.drawable.<name>)` placeholders and update `PROJECT_ICONS.md` (see `android-custom-icons`).

**Report Table Policy:** If a report can exceed 25 rows, it must use a table layout (see `android-report-tables`).

## Core Principles

### 1. Responsive Layout with Relative Positioning

- Use `fillMaxWidth()`, `weight()`, and percentage-based sizing instead of fixed dp values
- Design layouts that adapt to both portrait and landscape orientations
- Use `LocalConfiguration.current.screenWidthDp` to adjust columns/layout based on device size
- Prefer `LazyColumn`/`LazyRow` for scrollable content over fixed containers

### 2. Progressive Disclosure

- Show summary/overview first, details on demand
- Use expandable cards or drill-down navigation for detailed data
- Implement infinite scroll pagination for large datasets
- Load data progressively (initial view fast, details on interaction)

### 3. Touch-Friendly Interactions

- Minimum tap target size: 48dp (Material 3 standard)
- Use bottom sheets for filters and actions (thumb-reachable)
- Implement swipe gestures for common actions (refresh, delete)
- Provide visual feedback for all interactions (ripple, state changes)

### 4. Readable Typography

- **Minimum font size:** 14sp for body text, 16sp preferred
- **Line spacing:** 1.5x line height for readability
- **Contrast:** Ensure WCAG AA compliance (4.5:1 for normal text)
- Limit text column width for comfortable reading (avoid full-width text on tablets)

### 5. Data Visualization

- **Charts:** Use Vico only (Kotlin-first, Compose-friendly, and actively maintained)
- **Tables:** Limit to 3-4 columns on phone, 5-6 on tablet
- **Avoid nested tables** - use grouped sections or pagination instead
- **Color coding:** Use color sparingly, ensure accessibility (not color-only indicators)

### 6. Performance Optimization

- Lazy load data with pagination (offset or cursor-based)
- Cache rendered reports/charts (remember/derivedStateOf)
- Use `key()` in LazyColumn for efficient recomposition
- Defer expensive calculations to background coroutines

## Report Layout Patterns

### Pattern 1: Summary Card + Detail List

```kotlin
@Composable
fun InventoryReportScreen(state: ReportState) {
    LazyColumn {
        // Summary section (always visible)
        item {
            SummaryCard(
                totalValue = state.totalValue,
                itemCount = state.itemCount,
                lowStock = state.lowStockCount
            )
        }

        // Filter bar (sticky)
        stickyHeader {
            FilterBar(
                selectedCategory = state.filter,
                onFilterChange = { /* ... */ }
            )
        }

        // Detail items (paginated)
        items(state.items, key = { it.id }) { item ->
            ReportItemCard(item)
        }

        // Load more trigger
        if (state.hasMore) {
            item {
                LoadMoreTrigger(onLoadMore = { /* ... */ })
            }
        }
    }
}
```

### Pattern 1b: Table-First Paginated Report (25+ Rows)

Use this when the report can exceed 25 rows. Table with sticky header and floating footer.

```kotlin
@Composable
fun PaginatedReportScreen(allData: List<ReportItem>) {
    val pageSize = 25
    var currentPage by remember { mutableIntStateOf(1) }
    val listState = rememberLazyListState()

    val totalPages = maxOf(1, ceil(allData.size.toDouble() / pageSize).toInt())
    val pagedItems = remember(currentPage, allData) {
        val start = (currentPage - 1) * pageSize
        val end = minOf(start + pageSize, allData.size)
        allData.subList(start, end)
    }

    LaunchedEffect(currentPage) {
        listState.animateScrollToItem(0)
    }

    Scaffold(
        bottomBar = {
            Column {
                HorizontalDivider(
                    thickness = 0.5.dp,
                    color = MaterialTheme.colorScheme.outlineVariant
                )
                TablePaginationController(
                    currentPage = currentPage,
                    totalPages = totalPages,
                    onPageChange = { currentPage = it }
                )
            }
        }
    ) { paddingValues ->
        LazyColumn(
            state = listState,
            modifier = Modifier.padding(paddingValues).fillMaxSize()
        ) {
            stickyHeader {
                ReportRow(
                    data = listOf("ID", "Customer", "Amount"),
                    isHeader = true,
                    weights = listOf(0.2f, 0.5f, 0.3f)
                )
            }

            items(pagedItems) { item ->
                ReportRow(
                    data = listOf(item.id, item.name, item.amount),
                    weights = listOf(0.2f, 0.5f, 0.3f)
                )
            }
        }
    }
}
```

### Pattern 2: Tab-Based Multi-Report

```kotlin
@Composable
fun ReportsScreen() {
    var selectedTab by remember { mutableStateOf(0) }
    val tabs = listOf("Sales", "Inventory", "Customers")

    Column {
        TabRow(selectedTabIndex = selectedTab) {
            tabs.forEachIndexed { index, title ->
                Tab(
                    selected = selectedTab == index,
                    onClick = { selectedTab = index },
                    text = { Text(title) }
                )
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

### Pattern 3: Filter Bottom Sheet + Results

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
        ReportContent(
            data = state.data,
            modifier = Modifier.padding(padding)
        )
    }

    if (showFilters) {
        ModalBottomSheet(onDismissRequest = { showFilters = false }) {
            FilterForm(
                currentFilters = state.filters,
                onApply = { filters ->
                    viewModel.applyFilters(filters)
                    showFilters = false
                }
            )
        }
    }
}
```

## Interactive Filtering

### Date Range Selection

```kotlin
@Composable
fun DateRangeFilter(
    startDate: LocalDate,
    endDate: LocalDate,
    onRangeChange: (LocalDate, LocalDate) -> Unit
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        OutlinedButton(
            onClick = { /* Show date picker */ },
            modifier = Modifier.weight(1f)
        ) {
            Text("From: ${startDate.format()}")
        }
        OutlinedButton(
            onClick = { /* Show date picker */ },
            modifier = Modifier.weight(1f)
        ) {
            Text("To: ${endDate.format()}")
        }
    }
}
```

### Quick Filters (Chips)

```kotlin
@Composable
fun QuickFilters(
    options: List<FilterOption>,
    selected: FilterOption?,
    onSelect: (FilterOption) -> Unit
) {
    LazyRow(
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        contentPadding = PaddingValues(horizontal = 16.dp)
    ) {
        items(options) { option ->
            FilterChip(
                selected = option == selected,
                onClick = { onSelect(option) },
                label = { Text(option.label) }
            )
        }
    }
}
```

## Table Design for Mobile

### Avoid This (Too Many Columns)

```
| SKU | Name | Category | Qty | Unit | Value | Location | Status |
```

### Do This Instead (Card-Based)

```kotlin
@Composable
fun StockItemCard(item: StockItem) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            // Primary info
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = item.name,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )
                Text(
                    text = formatCurrency(item.value),
                    style = MaterialTheme.typography.titleMedium,
                    color = MaterialTheme.colorScheme.primary
                )
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Secondary info (grid)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                InfoItem("Qty", item.quantity.toString())
                InfoItem("Category", item.category)
                InfoItem("Location", item.warehouse)
            }

            // Status badge
            StockStatusBadge(item.status)
        }
    }
}

@Composable
private fun InfoItem(label: String, value: String) {
    Column {
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium
        )
    }
}
```

## Export Functionality

### Export Format Selection

**PDF:** Best for sharing/printing formatted reports (use Android-PDF-Writer or similar)
**CSV:** Best for data analysis in spreadsheets
**Share:** Best for immediate sharing via messaging apps

```kotlin
@Composable
fun ExportMenu(
    onExportPdf: () -> Unit,
    onExportCsv: () -> Unit,
    onShare: () -> Unit
) {
    var expanded by remember { mutableStateOf(false) }

    IconButton(onClick = { expanded = true }) {
        Icon(painterResource(R.drawable.share), "Export")
    }

    DropdownMenu(
        expanded = expanded,
        onDismissRequest = { expanded = false }
    ) {
        DropdownMenuItem(
            text = { Text("Export as PDF") },
            leadingIcon = { Icon(painterResource(R.drawable.pdf), null) },
            onClick = {
                expanded = false
                onExportPdf()
            }
        )
        DropdownMenuItem(
            text = { Text("Export as CSV") },
            leadingIcon = { Icon(painterResource(R.drawable.table), null) },
            onClick = {
                expanded = false
                onExportCsv()
            }
        )
        DropdownMenuItem(
            text = { Text("Share Report") },
            leadingIcon = { Icon(painterResource(R.drawable.send), null) },
            onClick = {
                expanded = false
                onShare()
            }
        )
    }
}
```

## Chart Integration

### Using Vico (Required)

Vico is our standard charting library for business apps.

- 100% Kotlin, works with Jetpack Compose and the View system
- Compose Multiplatform support for future sharing
- Extensible, professional-grade charts and interactions
- Actively maintained with a strong release cadence

**Implementation checklist:**

- Read the official guide at guide.vico.patrykandpatrick.com for setup
- Use the Compose artifact for new screens; Views only for legacy screens
- Start from the Vico sample module to mirror production patterns

```kotlin
@Composable
fun SalesChart(data: List<SalesDataPoint>) {
    val chartEntryModel = entryModelOf(
        data.mapIndexed { index, point ->
            entryOf(index, point.amount)
        }
    )

    Card(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "Sales Trend",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold
            )
            Spacer(modifier = Modifier.height(8.dp))
            Chart(
                chart = lineChart(),
                model = chartEntryModel,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(200.dp)
            )
        }
    }
}
```

## Loading States

```kotlin
@Composable
fun ReportLoadingState() {
    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        CircularProgressIndicator()
        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = "Generating report...",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}
```

## Empty States

```kotlin
@Composable
fun ReportEmptyState(
    message: String = "No data for the selected period",
    action: (@Composable () -> Unit)? = null
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            painter = painterResource(R.drawable.report),
            contentDescription = null,
            modifier = Modifier.size(80.dp),
            tint = MaterialTheme.colorScheme.outlineVariant
        )
        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = message,
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = TextAlign.Center
        )
        if (action != null) {
            Spacer(modifier = Modifier.height(24.dp))
            action()
        }
    }
}
```

## Common Pitfalls

### ❌ Avoid

- Fixed pixel widths (breaks on different screen sizes)
- More than 4 columns in tables on phone screens
- Nested scrollable containers (LazyColumn inside LazyColumn)
- Color-only indicators without text/icons (accessibility)
- Loading entire dataset at once (performance)
- Font sizes below 14sp (readability)
- Absolute positioning (breaks responsive layouts)

### ✅ Do

- Use relative sizing (fillMaxWidth, weight, Modifier.widthIn)
- Card-based layouts for multi-column data
- Single scroll container with mixed content types
- Icons/badges + color for status indicators
- Pagination with infinite scroll
- 16sp+ for body text, 14sp minimum
- Flex layouts (Row, Column with weights)

## Report Types Reference

See [references/report-types.md](references/report-types.md) for detailed patterns for:

- Financial reports (Sales, Revenue, Expenses)
- Inventory reports (Stock levels, Movements, Valuations)
- Analytics reports (User activity, Performance metrics)
- Transaction reports (Order history, Payment logs)

## Architecture Pattern

```
presentation/reports/
├── screens/
│   ├── ReportListScreen.kt          # Report selection
│   ├── SalesReportScreen.kt         # Specific report
│   └── InventoryReportScreen.kt
├── viewmodels/
│   ├── SalesReportViewModel.kt
│   └── InventoryReportViewModel.kt
├── components/
│   ├── SummaryCard.kt               # Reusable KPI cards
│   ├── FilterBottomSheet.kt
│   ├── DateRangeSelector.kt
│   ├── ExportMenu.kt
│   └── ReportChart.kt
└── export/
    ├── PdfExporter.kt               # PDF generation
    └── CsvExporter.kt               # CSV export

domain/usecase/reports/
├── GetSalesReportUseCase.kt
├── GetInventoryReportUseCase.kt
└── ExportReportUseCase.kt

data/repository/
└── ReportsRepositoryImpl.kt         # API calls + caching
```

## Testing Considerations

- Test with real data volumes (100s of items, not just 5)
- Verify scrolling performance with large datasets
- Test landscape orientation
- Test on small phones (5" screens) and tablets
- Verify export functionality with actual file creation
- Test loading/error/empty states
- Verify filter combinations work correctly
- Test pagination edge cases (last page, refresh)

## Performance Checklist

- [ ] Pagination implemented (20-50 items per page)
- [ ] LazyColumn used for scrolling lists
- [ ] Remember/derivedStateOf for expensive calculations
- [ ] Background coroutines for data processing
- [ ] Image loading optimized (if applicable)
- [ ] Chart rendering cached
- [ ] No blocking operations on main thread
- [ ] Proper key() usage in LazyColumn items
