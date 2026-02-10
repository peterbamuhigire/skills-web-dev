# Common Report Types and Layouts

This document provides detailed patterns for common report types in business and SaaS applications.

## Table of Contents

1. [Financial Reports](#financial-reports)
2. [Inventory Reports](#inventory-reports)
3. [Analytics Reports](#analytics-reports)
4. [Transaction Reports](#transaction-reports)
5. [Cross-Cutting Patterns](#cross-cutting-patterns)

---

## Financial Reports

### Sales Report

**Components:**
- Total revenue (period comparison)
- Number of transactions
- Average transaction value
- Top products/categories
- Sales trend chart
- Breakdown by payment method

**Layout:**

```
┌─────────────────────────────────┐
│ Total Revenue      │  +15.3%    │
│ UGX 45,230,000    │  vs last   │
├─────────────────────────────────┤
│ Transactions: 1,234 │ Avg: 36.6k│
└─────────────────────────────────┘

[Sales Trend Line Chart - Last 30 Days]

Top Products
├─ Product A ────────── UGX 12M
├─ Product B ────────── UGX 8.5M
└─ Product C ────────── UGX 6.2M

Payment Methods
├─ Mobile Money ────── 45%
├─ Cash ───────────── 35%
└─ Credit ─────────── 20%
```

**Filters:**
- Date range (Today, Week, Month, Custom)
- Shop/Branch selector
- Payment method filter
- Category filter

### Revenue Report

**Components:**
- Total revenue
- Revenue by category
- Revenue by shop/branch
- Profit margin (if cost data available)
- Revenue trend

**Layout:**

```
[Date Range Selector: Last 30 Days]

┌─────────────────────────────────┐
│ Total Revenue                   │
│ UGX 128,450,000                │
│ ─────────────────────────────── │
│ Cost: 92.3M │ Profit: 36.1M   │
│ Margin: 28.1%                   │
└─────────────────────────────────┘

[Stacked Bar Chart - Revenue vs Cost by Category]

By Category (Cards)
┌───────────────────────┐
│ Electronics           │
│ UGX 45.2M    (35.2%) │
│ Profit: 12.8M        │
└───────────────────────┘
┌───────────────────────┐
│ Clothing              │
│ UGX 32.8M    (25.5%) │
│ Profit: 8.4M         │
└───────────────────────┘
```

---

## Inventory Reports

### Stock Levels Report

**Components:**
- Total stock value
- Item count
- Low stock alerts
- Stock by category
- Stock by warehouse
- Expandable item details

**Layout:**

```
[Category Filter] [Warehouse Filter]

┌─────────────────────────────────┐
│ Total Value    │ Items │ Alerts │
│ UGX 24.5M     │  1,234 │   23   │
└─────────────────────────────────┘

Stock Items (Cards with expansion)
┌─────────────────────────────────┐
│ Paracetamol 500mg          [⌄] │
│ UGX 450,000           │         │
│ Qty: 500  Cat: Pharma  WH: Main │
│ ⚠ Low Stock                     │
└─────────────────────────────────┘
  [Expanded Details]
  ├─ Batch: B2024-001
  ├─ Expiry: 2025-12-31
  ├─ Reorder Level: 100
  └─ Supplier: ABC Pharma

[Load More...]
```

**Filters:**
- Category
- Warehouse
- Stock status (All, Low, Out of Stock, Overstocked)
- Search by SKU/Name

### Stock Movement Report

**Components:**
- Total movements (in/out)
- Movement trend chart
- Movement list with type badges
- Grouping by date

**Layout:**

```
[Date Range: Last 7 Days]

┌─────────────────────────────────┐
│ Stock In    │ Stock Out │ Net   │
│    2,450    │   1,823   │ +627  │
└─────────────────────────────────┘

[Line Chart - Daily In/Out Movement]

Movements by Day
━━ Today ━━━━━━━━━━━━━━━━━━━━━━━
┌─────────────────────────────────┐
│ [IN] Purchase Order #1234       │
│ +150 units │ Electronics        │
│ 10:30 AM   │ Warehouse: Main    │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│ [OUT] Sale Invoice #5678        │
│ -45 units  │ Clothing           │
│ 2:15 PM    │ Shop: Downtown     │
└─────────────────────────────────┘

━━ Yesterday ━━━━━━━━━━━━━━━━━━━
[More movements...]
```

**Filters:**
- Date range
- Movement type (All, Sales, Purchases, Transfers, Adjustments)
- Warehouse
- Category

### Inventory Valuation Report

**Components:**
- Total inventory value
- Value by category
- Value by warehouse
- Valuation method indicator (FIFO/LIFO/Weighted Avg)
- Aging analysis

**Layout:**

```
Valuation Method: FIFO

┌─────────────────────────────────┐
│ Total Inventory Value           │
│ UGX 128,450,000                │
│                                 │
│ Cost │ Retail │ Potential Profit│
│ 92.3M│ 145.2M │ 52.9M (57.3%)  │
└─────────────────────────────────┘

[Pie Chart - Value by Category]

By Warehouse
┌───────────────────────┐  ┌───────────────────────┐
│ Main Warehouse        │  │ Downtown Shop         │
│ UGX 85.2M (66.3%)    │  │ UGX 28.4M (22.1%)    │
│ 856 items             │  │ 245 items             │
└───────────────────────┘  └───────────────────────┘

Aging Analysis
├─ 0-30 days ────────── 65% │ UGX 83.5M
├─ 31-60 days ───────── 20% │ UGX 25.7M
├─ 61-90 days ───────── 10% │ UGX 12.8M
└─ 90+ days (aging) ──── 5% │ UGX 6.4M
```

---

## Analytics Reports

### User Activity Report

**Components:**
- Active users
- Activity trend
- Top features used
- Peak hours chart
- User list with activity scores

**Layout:**

```
[Period: Last 30 Days]

┌─────────────────────────────────┐
│ Active Users │ Sessions │ Avg   │
│     456      │  2,145   │ 4.7/u │
└─────────────────────────────────┘

[Line Chart - Daily Active Users]

Top Features
├─ POS Sale Creation ────── 3,245 uses
├─ Stock Check ──────────── 1,892 uses
├─ Reports ──────────────── 1,234 uses
└─ Customer Search ──────── 987 uses

Peak Hours (Heatmap)
       6am  9am  12pm  3pm  6pm  9pm
Mon   [▪▪] [██] [███] [██] [▪▪] [  ]
Tue   [▪▪] [██] [███] [██] [▪] [  ]
Wed   [▪] [███] [███] [█] [▪▪] [  ]
...
```

### Performance Metrics

**Components:**
- Key performance indicators
- Comparison to previous period
- Trend indicators
- Target vs actual visualization

**Layout:**

```
[Filter: This Month vs Last Month]

KPIs Grid
┌───────────────────────┐ ┌───────────────────────┐
│ Revenue               │ │ Transactions          │
│ UGX 45.2M       ↑15% │ │ 1,234           ↑8%  │
│ Target: 40M (113%)   │ │ Target: 1,200 (103%) │
└───────────────────────┘ └───────────────────────┘

┌───────────────────────┐ ┌───────────────────────┐
│ Avg Transaction       │ │ Customer Retention    │
│ UGX 36.6k       ↑7%  │ │ 87%             ↑3%  │
│ Target: 35k (105%)   │ │ Target: 85% (102%)   │
└───────────────────────┘ └───────────────────────┘

[Multi-Line Chart - KPIs Over Time]

Targets vs Actual (Progress Bars)
Revenue     ████████████░░ 113%
Trans       ████████████░  103%
Retention   ████████████░  102%
```

---

## Transaction Reports

### Order History Report

**Components:**
- Total orders
- Order value
- Order status breakdown
- Timeline view
- Order details on tap

**Layout:**

```
[Search] [Filter: All Statuses ⌄]

┌─────────────────────────────────┐
│ Orders │ Total Value │ Avg Value│
│ 1,234  │ UGX 45.2M  │ UGX 36.6k│
└─────────────────────────────────┘

Status Breakdown
├─ Completed ────── 1,089 (88%)
├─ Pending ──────── 89 (7%)
├─ Cancelled ────── 56 (5%)

Orders (Cards)
┌─────────────────────────────────┐
│ #INV-2024-001234    [Completed] │
│ UGX 125,400                     │
│ 12 items │ Jan 15, 2024 10:30AM│
│ Customer: John Doe              │
│ Payment: Mobile Money           │
└─────────────────────────────────┘
  [Tap to expand for items list]

┌─────────────────────────────────┐
│ #INV-2024-001233    [Pending]   │
│ UGX 45,200                      │
│ 5 items  │ Jan 15, 2024 9:15AM │
│ Customer: Jane Smith            │
│ Payment: Credit                 │
└─────────────────────────────────┘
```

### Payment Log Report

**Components:**
- Total payments
- Payment method breakdown
- Failed/pending transactions
- Reconciliation summary

**Layout:**

```
[Date Range: Today]

┌─────────────────────────────────┐
│ Payments │ Amount  │ Failed │ % │
│   456    │ 45.2M   │   12   │3% │
└─────────────────────────────────┘

By Payment Method
├─ Mobile Money ─── UGX 20.4M (45%)
├─ Cash ─────────── UGX 15.8M (35%)
├─ Credit ───────── UGX 6.8M  (15%)
└─ Bank Transfer ── UGX 2.2M  (5%)

Status
├─ [✓] Completed ──── 432 (94.7%)
├─ [⏳] Pending ────── 12 (2.6%)
└─ [✗] Failed ──────── 12 (2.6%)

Transactions (Timeline)
━━ 10:00 - 11:00 ━━━━━━━━━━━━━━━
┌─────────────────────────────────┐
│ [✓] Mobile Money                │
│ UGX 125,400 │ Inv: #1234       │
│ Ref: MM240115ABCD               │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│ [✗] Mobile Money (Failed)       │
│ UGX 45,200  │ Inv: #1235       │
│ Error: Insufficient funds       │
│ [Retry]                         │
└─────────────────────────────────┘
```

---

## Cross-Cutting Patterns

### Summary-First Pattern

Always show the "answer" first (totals, key metrics) before detailed breakdowns:

```
1. Summary cards at top (2-4 KPIs)
2. Visualization (chart/graph)
3. Detailed list/table
4. Load more/pagination
```

### Comparison Pattern

For period comparisons, show:

```
┌───────────────────────────────┐
│ This Month                    │
│ UGX 45.2M                     │
│ ─────────────────────────────│
│ Last Month: 39.3M             │
│ Change: +5.9M (↑15%)         │
└───────────────────────────────┘
```

### Drill-Down Pattern

```
Summary Card (tap to expand)
└─> Detail View
    └─> Individual Items
        └─> Item Details
```

### Export Pattern

Place export button in:
- TopAppBar actions (IconButton with share icon)
- Floating Action Button (for primary action)
- Bottom Sheet menu (for multiple export options)

### Refresh Pattern

```kotlin
val pullRefreshState = rememberPullRefreshState(
    refreshing = isRefreshing,
    onRefresh = { viewModel.refresh() }
)

Box(Modifier.pullRefresh(pullRefreshState)) {
    ReportContent()
    PullRefreshIndicator(
        refreshing = isRefreshing,
        state = pullRefreshState,
        modifier = Modifier.align(Alignment.TopCenter)
    )
}
```

### Empty State Messages by Report Type

- **Sales Report:** "No sales recorded for this period"
- **Inventory Report:** "No stock items match your filters"
- **Transaction Report:** "No transactions found"
- **Analytics Report:** "Not enough data to generate insights"

Always provide:
1. Clear message
2. Possible action (Clear filters, Change date range, Add data)
3. Relevant icon

---

## Layout Adaptation by Screen Size

### Phone (< 600dp)

- 1 column layouts
- Bottom sheets for filters
- Tabs for multiple views
- 3-4 columns max in tables (prefer cards)

### Tablet (600-900dp)

- 2 column layouts where appropriate
- Side panel for filters
- Master-detail view
- 5-6 columns in tables

### Large Tablet/Landscape (> 900dp)

- 3 column layouts
- Permanent side navigation
- Split view (list + detail)
- Full tables with horizontal scroll if needed

---

## Accessibility Checklist

- [ ] All interactive elements ≥ 48dp
- [ ] Color contrast ≥ 4.5:1
- [ ] Status not indicated by color alone (use icons/text)
- [ ] Content descriptions on icons
- [ ] Semantic heading structure
- [ ] Keyboard/D-pad navigation support
- [ ] Screen reader tested
- [ ] Font scaling tested (up to 200%)
