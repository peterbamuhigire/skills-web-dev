---
name: mobile-report-tables
description: 'Report UI rule for mobile apps: any report with potential for more than
  25 rows must render as a table, not cards. Includes decision rules, Android Compose
  patterns, and iOS SwiftUI patterns.'
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---


## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# Mobile Report Tables (25+ Rows)

<!-- dual-compat-start -->
## Use When

- Report UI rule for mobile apps: any report with potential for more than 25 rows must render as a table, not cards. Includes decision rules, Android Compose patterns, and iOS SwiftUI patterns.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `mobile-report-tables` or would be better handled by a more specific companion skill.
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
When a report can exceed **25 rows**, it must be rendered as a **table**, not card lists. This prevents scroll fatigue and preserves scanability for business data. Applies to both Android (Jetpack Compose) and iOS (SwiftUI).

## Scope

**Use for:** Reports, analytics lists, financial summaries, inventory reports, audit logs, and any dataset likely to exceed 25 rows.

**Do not use:** Small datasets (<=25 rows) or highly visual summaries where cards communicate state better.

## Rule (Mandatory)

- If a report **can** exceed 25 rows, use a **table layout**.
- Cards are acceptable only when the dataset is **guaranteed <=25 rows**.

---

## Android: Jetpack Compose Patterns

### Existing ReportTable Composable

The project has a reusable `ReportTable<T>` at `core/ui/components/ReportTable.kt`:

```kotlin
ReportTable(
    columns = listOf(
        TableColumn(header = "#", weight = 0.4f) { "#${it.rank}" },
        TableColumn(header = "Name", weight = 1.5f) { it.fullName ?: "-" },
        TableColumn(header = "Inv", weight = 0.4f) { it.totalInvoices.toString() },
        TableColumn(header = "Amount", weight = 1.2f) { "$currency ${fmt.format(it.totalAmount)}" }
    ),
    rows = report.rows,
    onRowClick = { /* optional */ },
    pageSize = 25
)
```

Features:
- Generic `<T>` with `TableColumn<T>` definitions (header, weight, value lambda)
- Built-in client-side pagination (25/page default)
- Header row with `surfaceVariant` background
- `Modifier.weight()` for proportional column sizing
- Empty state with string resource

### Android Date Display (Mandatory)

**All dates in report tables MUST be human-readable.** Never display raw API dates like `2026-02-14`. Always format to short readable form: **`d MMM yyyy`** (e.g., `14 Feb 2026`).

```kotlin
val apiDateFmt = remember { SimpleDateFormat("yyyy-MM-dd", Locale.US) }
val displayDateFmt = remember { SimpleDateFormat("d MMM yyyy", Locale.US) }
val formatDate: (String) -> String = { raw ->
    try { displayDateFmt.format(apiDateFmt.parse(raw)!!) } catch (_: Exception) { raw }
}

// Usage in TableColumn:
TableColumn("Date", minWidth = 100.dp) { formatDate(it.date) }
TableColumn("Oldest", minWidth = 100.dp) { it.oldestDate?.let { formatDate(it) } ?: "-" }
```

### Android Pull-to-Refresh (Mandatory)

**Every screen that displays reports, statistics, or data** MUST support pull-to-refresh.

```kotlin
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MyReportScreen(viewModel: MyViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsState()
    var isRefreshing by remember { mutableStateOf(false) }

    LaunchedEffect(uiState.loading) {
        if (!uiState.loading) isRefreshing = false
    }

    PullToRefreshBox(
        isRefreshing = isRefreshing,
        onRefresh = { isRefreshing = true; viewModel.reload() },
        modifier = Modifier.fillMaxSize()
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(16.dp)
        ) {
            // Report content
        }
    }
}
```

### Android Pull-to-Refresh Rules
- ViewModel MUST expose a public `reload()` / `refresh()` function
- Hub screens (Sales Hub, Network Hub, etc.) refresh their statistics/charts
- Report screens refresh their data (re-fetch from API)
- Dashboard refreshes KPI cards
- Use `PullToRefreshBox` (simpler API than the older `PullToRefreshContainer`)

### Android Screen Structure Pattern

Report screens with tables should use a scrollable `Column` (not `LazyColumn`), since `ReportTable` is not a lazy composable. Wrap in `PullToRefreshBox`:

```kotlin
PullToRefreshBox(
    isRefreshing = isRefreshing,
    onRefresh = { isRefreshing = true; viewModel.reload() },
    modifier = Modifier.fillMaxSize().padding(paddingValues)
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Filters
        // Summary cards
        // ReportTable (handles its own pagination)
    }
}
```

---

## iOS: SwiftUI Patterns

### iOS SwiftUI Table Pattern

```swift
struct ReportTableView<T: Identifiable>: View {
    let columns: [TableColumnDef<T>]
    let rows: [T]
    let pageSize: Int
    var onRowTap: ((T) -> Void)? = nil

    @State private var currentPage = 1

    private var totalPages: Int {
        max(1, Int(ceil(Double(rows.count) / Double(pageSize))))
    }

    private var pagedRows: [T] {
        let start = (currentPage - 1) * pageSize
        let end = min(start + pageSize, rows.count)
        return Array(rows[start..<end])
    }

    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack(spacing: 0) {
                ForEach(columns) { col in
                    Text(col.header)
                        .font(.caption)
                        .fontWeight(.semibold)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.vertical, 8)
                        .padding(.horizontal, 4)
                }
            }
            .background(Color(.systemGray6))

            Divider()

            // Rows
            ForEach(pagedRows) { row in
                HStack(spacing: 0) {
                    ForEach(columns) { col in
                        Text(col.value(row))
                            .font(.body)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.vertical, 6)
                            .padding(.horizontal, 4)
                    }
                }
                .contentShape(Rectangle())
                .onTapGesture { onRowTap?(row) }
                Divider()
            }

            // Pagination
            if totalPages > 1 {
                HStack {
                    Button("Previous") { currentPage -= 1 }
                        .disabled(currentPage <= 1)
                    Spacer()
                    Text("Page \(currentPage) of \(totalPages)")
                        .font(.caption)
                    Spacer()
                    Button("Next") { currentPage += 1 }
                        .disabled(currentPage >= totalPages)
                }
                .padding(.vertical, 8)
            }
        }
    }
}

struct TableColumnDef<T>: Identifiable {
    let id = UUID()
    let header: String
    let value: (T) -> String
}
```

### iOS Date Display Pattern

```swift
private let apiFormatter: DateFormatter = {
    let f = DateFormatter()
    f.dateFormat = "yyyy-MM-dd"
    f.locale = Locale(identifier: "en_US_POSIX")
    return f
}()

private let displayFormatter: DateFormatter = {
    let f = DateFormatter()
    f.dateFormat = "d MMM yyyy"
    return f
}()

func formatDate(_ raw: String) -> String {
    guard let date = apiFormatter.date(from: raw) else { return raw }
    return displayFormatter.string(from: date)
}
```

### iOS Pull-to-Refresh

```swift
struct MyReportView: View {
    @StateObject private var viewModel = ReportViewModel()

    var body: some View {
        ScrollView {
            VStack(spacing: 12) {
                // Filters, summary cards, table...
            }
            .padding(16)
        }
        .refreshable {
            await viewModel.reload()
        }
    }
}
```

---

## Portrait Responsiveness Standards

### Column Priority (Phone Portrait)
- **3-4 columns max** for portrait without horizontal scroll
- Abbreviate headers: "#" not "Rank", "Inv" not "Invoices", "Amt" not "Amount", "Bal" not "Balance"
- Android: use `weight` ratios; iOS: use `frame(maxWidth:)` with proportional values

### Weight Guidelines (Android) / Proportional Sizing (iOS)
| Column Type | Android Weight | Examples |
|-------------|---------------|----------|
| Index/Rank | 0.3-0.5f | #, Rank |
| Short text | 0.4-0.6f | Code, Qty, Inv |
| Name/Description | 1.3-1.5f | Product, Distributor |
| Currency amount | 1.0-1.2f | Amount, Balance, Due |
| Date | 0.8-1.0f | Date |

### Horizontal Scroll (5+ columns)
When a table needs 5+ columns and cannot fit in portrait:

**Android:**
```kotlin
Column(Modifier.horizontalScroll(rememberScrollState())) {
    ReportTable(columns = ..., rows = ...)
}
```

**iOS:**
```swift
ScrollView(.horizontal) {
    ReportTableView(columns: columns, rows: rows, pageSize: 25)
}
```

### String Resources
- **Android:** Always use `stringResource(R.string.report_col_*)` for table headers. Never hardcode header text.
- **iOS:** Always use `NSLocalizedString` or String Catalogs for table headers. Never hardcode header text.

## Cards vs Tables Decision Matrix

| Criteria | Use Cards | Use Table |
|----------|-----------|-----------|
| Max rows <= 25 guaranteed | Yes | Optional |
| Max rows > 25 possible | No | **Required** |
| DPCs (5-20 items) | Yes | Optional |
| Daily summary (7 days) | Yes | Optional |
| Distributor lists | No | **Required** |
| Product lists | No | **Required** |
| Invoice lists | No | **Required** |
| Debtors lists | No | **Required** |
| Top 100 rankings | No | **Required** |

## Pagination Guidance

- Default to **client-side pagination** for up to a few hundred rows (25 per page).
- Android: `ReportTable` handles pagination internally — no need for ViewModel pagination.
- iOS: `ReportTableView` handles pagination internally via `@State` page tracking.
- For larger datasets (1000+), use server pagination via API offset/limit params.

## Date Display Rules

- API sends dates as `yyyy-MM-dd` — this is for transport only, never for display
- Tables, cards, summaries, and any user-facing text must use `d MMM yyyy`
- Chart axes may use shorter formats like `MMM d` (e.g., `Feb 14`) for space
- Nullable dates: format if present, show `-` if null

## Checklist

- [ ] If report can exceed 25 rows, use table (ReportTable on Android, ReportTableView on iOS)
- [ ] Limit to 3-4 columns for portrait, abbreviate headers
- [ ] Use proportional sizing (weight on Android, frame maxWidth on iOS)
- [ ] Use localized strings for header text
- [ ] Pull-to-refresh on every screen with reports or statistics
- [ ] Date display: `d MMM yyyy` format, never raw API dates
