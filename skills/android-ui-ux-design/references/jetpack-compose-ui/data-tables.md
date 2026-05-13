# Data Tables & Paginated Lists

Standard pattern for displaying tabulated data in Jetpack Compose. Applies to any report, list, or data-heavy screen. Proven across 8+ production screens without crashes.

## Design Principles

1. **Table-first for reports** -- If a report can exceed 25 rows, always render as a table (phone + tablet)
2. **Client-side pagination** -- Page through loaded items locally (25/page)
3. **Server pagination bridge** -- Fetch more from API when reaching last page
4. **Minimal rendering** -- Only render current page items, never the full list
5. **No LazyColumn items()** -- Render the table as a single `item {}` block inside `LazyColumn` to avoid nesting scrollable containers and prevent emulator crashes

## Architecture Overview

```
LazyColumn {                          // Outer scrollable container
    item { FilterSection }            // Filters (dropdowns)
    item { SummaryCards }             // KPI summary row(s)
    item {                            // ONE item block for data
        DataTable(pageItems)
    }
    item { TablePaginationBar }       // Pagination controls
    item { LoadingMoreIndicator }     // Conditional spinner
}
```

## Screen Template

````kotlin
private const val ITEMS_PER_PAGE = 25

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ReportScreen(
    onBack: () -> Unit = {},
    viewModel: ReportViewModel = hiltViewModel()
) {
    val items by viewModel.items.collectAsStateWithLifecycle()
    val isLoading by viewModel.isLoading.collectAsStateWithLifecycle()
    val isLoadingMore by viewModel.isLoadingMore.collectAsStateWithLifecycle()
    val error by viewModel.error.collectAsStateWithLifecycle()

    // Client-side pagination state
    var tablePage by remember { mutableIntStateOf(1) }
    val totalPages = maxOf(1, ceil(items.size.toDouble() / ITEMS_PER_PAGE).toInt())
    val pageItems = items.drop((tablePage - 1) * ITEMS_PER_PAGE).take(ITEMS_PER_PAGE)

    // Reset page when filter changes shrink the list
    val itemsSize = items.size
    var lastItemsSize by remember { mutableIntStateOf(0) }
    if (itemsSize != lastItemsSize && itemsSize < lastItemsSize) { tablePage = 1 }
    lastItemsSize = itemsSize

    // Error dialog
    error?.let { msg ->
        MaduukaAlertDialog(
            type = AlertType.ERROR, title = "Error", message = msg,
            onConfirm = { viewModel.dismissError() }
        )
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Report Title") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(painterResource(R.drawable.back), "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primary,
                    titleContentColor = MaterialTheme.colorScheme.onPrimary,
                    navigationIconContentColor = MaterialTheme.colorScheme.onPrimary
                )
            )
        }
    ) { padding ->
        if (isLoading) {
            Box(Modifier.fillMaxSize().padding(padding), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        } else {
            LazyColumn(
                state = rememberLazyListState(),
                modifier = Modifier.fillMaxSize().padding(padding).padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                item { Spacer(Modifier.height(4.dp)) }
                item { /* Filters go here */ }
                item { /* Summary cards go here */ }

                if (items.isNotEmpty()) {
                    item { DataTable(pageItems) }
                    item {
                        TablePaginationBar(
                            currentPage = tablePage,
                            totalPages = totalPages,
                            totalItems = items.size,
                            onPreviousPage = { if (tablePage > 1) tablePage-- },
                            onNextPage = {
                                if (tablePage < totalPages) tablePage++
                                // Bridge to server pagination
                                if (tablePage >= totalPages && !isLoadingMore) {
                                    viewModel.loadMore()
                                }
                            }
                        )
                    }
                }

                if (isLoadingMore) {
                    item {
                        Box(Modifier.fillMaxWidth().padding(16.dp), contentAlignment = Alignment.Center) {
                            CircularProgressIndicator()
                        }
                    }
                }
                item { Spacer(Modifier.height(16.dp)) }
            }
        }
    }
}

## Floating Footer Pagination (Recommended)

Use a sticky header for the table head and a floating footer for page controls.
This creates a dense, professional table with clear "mental anchors".

```kotlin
@Composable
fun TablePaginationController(
    currentPage: Int,
    totalPages: Int,
    onPageChange: (Int) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(12.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = "Page $currentPage of $totalPages",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedButton(
                onClick = { onPageChange(currentPage - 1) },
                enabled = currentPage > 1,
                contentPadding = PaddingValues(horizontal = 12.dp, vertical = 4.dp),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text("Prev", fontSize = 12.sp)
            }

            Button(
                onClick = { onPageChange(currentPage + 1) },
                enabled = currentPage < totalPages,
                contentPadding = PaddingValues(horizontal = 12.dp, vertical = 4.dp),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text("Next", fontSize = 12.sp)
            }
        }
    }
}
````

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

````

## Table Layout (Tablet >= 600dp)

The table is a `Card` with `Column` > header `Row` + data `Row` per item. No `LazyColumn` inside -- just `forEachIndexed`.

### Structure

```kotlin
@Composable
private fun DataTable(items: List<DataItem>) {
    Card(
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Column {
            // Header row
            Row(
                Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 10.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                HeaderCell("Name", Modifier.weight(2f))
                HeaderCell("Category", Modifier.weight(1.5f))
                HeaderCell("Amount", Modifier.weight(1.2f), TextAlign.End)
                HeaderCell("Status", Modifier.weight(1f), TextAlign.Center)
            }
            HorizontalDivider(color = MaterialTheme.colorScheme.outlineVariant)

            // Data rows
            items.forEachIndexed { index, item ->
                Row(
                    Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 10.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Primary column: name (bold) + subtitle (gray)
                    Column(Modifier.weight(2f)) {
                        Text(
                            item.name,
                            style = MaterialTheme.typography.bodySmall,
                            fontWeight = FontWeight.Medium,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis
                        )
                        Text(
                            item.subtitle,
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis
                        )
                    }
                    // Text column
                    Text(
                        item.category,
                        style = MaterialTheme.typography.bodySmall,
                        modifier = Modifier.weight(1.5f),
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                    // Numeric column (right-aligned)
                    Text(
                        numFmt.format(item.amount),
                        style = MaterialTheme.typography.bodySmall,
                        fontWeight = FontWeight.SemiBold,
                        modifier = Modifier.weight(1.2f),
                        textAlign = TextAlign.End
                    )
                    // Badge column (centered)
                    StatusBadge(item.status, Modifier.weight(1f))
                }
                // Divider between rows (not after last)
                if (index < items.lastIndex) {
                    HorizontalDivider(
                        Modifier.padding(horizontal = 12.dp),
                        color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f)
                    )
                }
            }
        }
    }
}
````

### Header Cell

```kotlin
@Composable
private fun HeaderCell(
    text: String,
    modifier: Modifier,
    textAlign: TextAlign = TextAlign.Start
) {
    Text(
        text,
        style = MaterialTheme.typography.labelSmall,
        fontWeight = FontWeight.Bold,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
        modifier = modifier,
        textAlign = textAlign
    )
}
```

### Column Weight Guidelines

| Column Type               | Weight   | TextAlign | Example              |
| ------------------------- | -------- | --------- | -------------------- |
| Primary (name + subtitle) | 2.0-2.5f | Start     | Item name + category |
| Text (medium)             | 1.2-1.5f | Start     | Warehouse, supplier  |
| Numeric                   | 0.8-1.2f | End       | Qty, cost, value     |
| Status badge              | 0.8-1.0f | Center    | In Stock, Pending    |
| Short text                | 0.6-0.8f | Start/End | ID, date             |

### Typography Standards

| Element                      | Style        | Weight   | Color                |
| ---------------------------- | ------------ | -------- | -------------------- |
| Header cell                  | `labelSmall` | Bold     | `onSurfaceVariant`   |
| Data cell (text)             | `bodySmall`  | Normal   | default              |
| Data cell (primary)          | `bodySmall`  | Medium   | default              |
| Data cell (emphasis)         | `bodySmall`  | SemiBold | default or `primary` |
| Subtitle (in primary column) | `labelSmall` | Normal   | `onSurfaceVariant`   |

### Spacing Standards

| Element                        | Value                               |
| ------------------------------ | ----------------------------------- |
| Row horizontal padding         | 12.dp                               |
| Row vertical padding           | 10.dp                               |
| Card elevation                 | 1.dp                                |
| Card container color           | `MaterialTheme.colorScheme.surface` |
| Header divider                 | `outlineVariant` (full opacity)     |
| Row divider                    | `outlineVariant.copy(alpha = 0.5f)` |
| Row divider horizontal padding | 12.dp                               |

## Card Layout (Phone < 600dp)

Each item rendered as a compact card with key-value pairs.

### Structure

```kotlin
@Composable
private fun DataCards(items: List<DataItem>) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        items.forEach { item ->
            Card(
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
            ) {
                Column(
                    Modifier.fillMaxWidth().padding(12.dp),
                    verticalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    // Row 1: Title (bold, weight 1f) + Status badge
                    Row(
                        Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            item.name,
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.SemiBold,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                            modifier = Modifier.weight(1f)
                        )
                        StatusBadge(item.status)
                    }

                    // Subtitle
                    Text(
                        item.subtitle,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )

                    HorizontalDivider(
                        color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f)
                    )

                    // Key-value pairs in 2-column rows
                    Row(
                        Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column {
                            Text("Label A", style = MaterialTheme.typography.labelSmall,
                                 color = MaterialTheme.colorScheme.onSurfaceVariant)
                            Text(item.valueA, style = MaterialTheme.typography.bodySmall)
                        }
                        Column(horizontalAlignment = Alignment.End) {
                            Text("Label B", style = MaterialTheme.typography.labelSmall,
                                 color = MaterialTheme.colorScheme.onSurfaceVariant)
                            Text(item.valueB, style = MaterialTheme.typography.bodySmall,
                                 fontWeight = FontWeight.Medium)
                        }
                    }
                }
            }
        }
    }
}
```

### Card Layout Rules

1. Card padding: 12.dp all sides
2. Vertical spacing between sections: 6.dp (`Arrangement.spacedBy(6.dp)`)
3. Gap between cards: 8.dp (`Arrangement.spacedBy(8.dp)`)
4. Title row: `bodyMedium` + `FontWeight.SemiBold`, status badge right-aligned
5. Subtitle: `bodySmall` + `onSurfaceVariant`
6. `HorizontalDivider` separates header from key-value pairs
7. Key-value pairs: label in `labelSmall` + `onSurfaceVariant`, value in `bodySmall`
8. Right-column values: `horizontalAlignment = Alignment.End`
9. Emphasized values: `FontWeight.SemiBold` or `FontWeight.Medium` + `MaterialTheme.colorScheme.primary`

## Status Badges

Colored inline badges for statuses, risk levels, or categories.

```kotlin
@Composable
private fun StatusBadge(status: Status, modifier: Modifier = Modifier) {
    val (color, text) = when (status) {
        Status.ACTIVE -> Color(0xFF4CAF50) to "Active"
        Status.WARNING -> Color(0xFFFF9800) to "Warning"
        Status.ERROR -> Color(0xFFF44336) to "Error"
    }
    Box(modifier = modifier, contentAlignment = Alignment.Center) {
        Box(
            Modifier
                .clip(RoundedCornerShape(4.dp))
                .background(color.copy(alpha = 0.15f))
                .padding(horizontal = 6.dp, vertical = 2.dp)
        ) {
            Text(
                text,
                style = MaterialTheme.typography.labelSmall,
                color = color,
                fontWeight = FontWeight.Bold
            )
        }
    }
}
```

### Badge Design Rules

- Corner radius: 4.dp
- Background: status color at 15% alpha (`color.copy(alpha = 0.15f)`)
- Text: `labelSmall`, `FontWeight.Bold`, full-opacity status color
- Padding: 6.dp horizontal, 2.dp vertical
- Outer `Box` with `modifier` for table column weight alignment
- In tables: pass `Modifier.weight(Xf)` as modifier
- In cards: omit modifier (natural sizing)

### Standard Color Palette

| Semantic                        | Color       | Hex          |
| ------------------------------- | ----------- | ------------ |
| Success / In Stock / Low Risk   | Green       | `0xFF4CAF50` |
| Warning / Low Stock / Medium    | Orange      | `0xFFFF9800` |
| Error / Out of Stock / Critical | Red         | `0xFFF44336` |
| High Risk                       | Deep Orange | `0xFFF57C00` |
| Medium Risk / Caution           | Amber       | `0xFFFBC02D` |
| Info / Neutral                  | Blue        | `0xFF1976D2` |

## TablePaginationBar (Shared Component)

Reusable pagination controls. Lives at `presentation/common/components/TablePaginationBar.kt`.

```kotlin
@Composable
fun TablePaginationBar(
    currentPage: Int,
    totalPages: Int,
    totalItems: Int,
    onPreviousPage: () -> Unit,
    onNextPage: () -> Unit,
    modifier: Modifier = Modifier
)
```

Shows: `"{totalItems} items"` (left) | `"< {page} / {total} >"` (right)

Buttons auto-disable at boundaries (page 1 = no previous, last page = no next).

## Pagination Flow

```
User opens screen
  └─ ViewModel loads page 1 from API → items = [1..20]
       └─ Client shows items 1-15 (page 1 of 2)
            └─ User clicks "Next" → shows items 16-20 (page 2 of 2)
                 └─ User clicks "Next" on LAST page
                      └─ viewModel.loadMore() → fetches API page 2
                           └─ items = [1..40], totalPages recalculated
                                └─ Client shows items 16-30 (still page 2, but totalPages now 3)
```

### Page Reset Rules

- Reset `tablePage = 1` when any filter changes (warehouse, status, date, etc.)
- Reset `tablePage = 1` when `items.size` shrinks (detected via `lastItemsSize` tracking)
- Never reset on `loadMore()` (items grow, user stays on current page)

## Summary Cards (Above Table)

KPI-style summary cards displayed in 2-column rows above the data table.

```kotlin
@Composable
private fun SummaryCard(
    title: String,
    value: String,
    color: Color,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = color.copy(alpha = 0.1f))
    ) {
        Column(Modifier.padding(12.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            Text(title, style = MaterialTheme.typography.bodySmall,
                 color = MaterialTheme.colorScheme.onSurfaceVariant,
                 textAlign = TextAlign.Center)
            Spacer(Modifier.height(4.dp))
            Text(value, style = MaterialTheme.typography.titleMedium,
                 fontWeight = FontWeight.Bold, color = color,
                 maxLines = 1, overflow = TextOverflow.Ellipsis)
        }
    }
}

// Usage in 2x2 grid:
Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
    SummaryCard("Total Items", "1,234", colorScheme.primary, Modifier.weight(1f))
    SummaryCard("Total Value", "UGX 5.2M", colorScheme.secondary, Modifier.weight(1f))
}
```

## Filter Section

Dropdown filters above the data, wrapped in a light card.

```kotlin
@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun FilterCard(
    warehouses: List<Warehouse>,
    selectedId: Int?,
    onSelect: (Int?) -> Unit
) {
    var expanded by remember { mutableStateOf(false) }
    ExposedDropdownMenuBox(expanded = expanded, onExpandedChange = { expanded = it }) {
        OutlinedTextField(
            value = warehouses.find { it.id == selectedId }?.name ?: "All Warehouses",
            onValueChange = {}, readOnly = true,
            label = { Text("Warehouse") },
            trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded) },
            modifier = Modifier.menuAnchor().fillMaxWidth()
        )
        ExposedDropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
            DropdownMenuItem(text = { Text("All Warehouses") },
                onClick = { onSelect(null); expanded = false })
            warehouses.forEach { wh ->
                DropdownMenuItem(text = { Text(wh.name) },
                    onClick = { onSelect(wh.id); expanded = false })
            }
        }
    }
}
```

**Note:** Use `.menuAnchor()` with no args (not `MenuAnchorType.PrimaryNotEditable` which doesn't exist in Compose BOM 2024.06.00).

## Required Imports

```kotlin
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import kotlin.math.ceil
```

## Anti-Patterns (AVOID)

| Anti-Pattern                                       | Why                                      | Do Instead                                                   |
| -------------------------------------------------- | ---------------------------------------- | ------------------------------------------------------------ |
| `LazyColumn { items(list) }` inside a `LazyColumn` | Nested scrollable crash                  | Render table as single `item {}` block with `forEachIndexed` |
| `items(allItems)` with card-per-item               | Crashes on large lists on some emulators | Client-side pagination (15/page)                             |
| `GridCells.Adaptive` for data tables               | Unpredictable column count               | `Row` with `Modifier.weight()` columns                       |
| Hardcoded dp widths for columns                    | Doesn't adapt to screen size             | `Modifier.weight(Xf)` proportional                           |
| `derivedStateOf` infinite scroll                   | Complex, hard to debug                   | Client pagination + `loadMore()` on last page                |
| Full dataset in single render                      | Memory + jank on large lists             | Paginate to 15 items per page                                |
