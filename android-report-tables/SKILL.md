---
name: android-report-tables
description: "Report UI rule for Android: any report with potential for more than 25 rows must render as a table, not cards. Includes decision rules and Compose patterns."
---

# Android Report Tables (25+ Rows)

When a report can exceed **25 rows**, it must be rendered as a **table**, not card lists. This prevents scroll fatigue and preserves scanability for business data.

## Scope

**Use for:** Reports, analytics lists, financial summaries, inventory reports, audit logs, and any dataset likely to exceed 25 rows.

**Do not use:** Small datasets (<=25 rows) or highly visual summaries where cards communicate state better.

## Rule (Mandatory)

- If a report **can** exceed 25 rows, use a **table layout**.
- Cards are acceptable only when the dataset is **guaranteed <=25 rows**.

## Compose Pattern (Table First)

Use the `data-tables` reference from `jetpack-compose-ui` as the baseline.

```kotlin
@Composable
fun ReportTable(
    rows: List<ReportRow>,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier.fillMaxWidth()) {
        TableHeader()
        rows.forEach { row ->
            TableRowItem(row)
        }
    }
}
```

## Pagination Guidance

- Default to **client-side pagination** for up to a few hundred rows (25 per page).
- For larger datasets, use server pagination and a paging bar.
- Prefer a **floating footer** with page controls and a sticky header for dense, professional tables.

## Mobile Adaptation

- Phone: limit to 3-4 columns, truncate text, use `Modifier.weight()` for columns.
- Tablet: 5-6 columns, allow more whitespace and wider columns.

## Checklist

- [ ] If report can exceed 25 rows, use table layout
- [ ] Use pagination for large datasets
- [ ] Avoid card lists for long reports
- [ ] Match table style to `jetpack-compose-ui` data table patterns
