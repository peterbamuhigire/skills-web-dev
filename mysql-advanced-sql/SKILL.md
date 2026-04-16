---
name: mysql-advanced-sql
description: 'Advanced MySQL 8 SQL techniques: window functions, CTEs, recursive queries,
  pivoting, JSON operations, stored procedures, triggers, and complex aggregations.
  Use when writing analytical queries, transforming data, implementing reporting SQL...'
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# MySQL Advanced SQL

<!-- dual-compat-start -->
## Use When

- Advanced MySQL 8 SQL techniques: window functions, CTEs, recursive queries, pivoting, JSON operations, stored procedures, triggers, and complex aggregations. Use when writing analytical queries, transforming data, implementing reporting SQL...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `mysql-advanced-sql` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | Advanced query test plan | Markdown doc covering window function, recursive CTE, and JSON-path test cases | `docs/data/mysql-advanced-tests.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Expert patterns for MySQL 8+ beyond basic CRUD. Drawn from *Leveling Up with SQL* (Mark Simon, Apress 2023) plus production-hardened techniques.

**Sections:** Window Functions | Recursive CTEs | Pivoting | JSON | Gaps & Islands | Deduplication | Triggers | Stored Procedures | Conditional Aggregation | GROUP BY | Subqueries | Views | Anti-Patterns

---

## 1. Window Functions

Window functions compute a value per row over a related set of rows without collapsing them into a GROUP BY summary. Introduced in MySQL 8.0.

**Syntax skeleton:**
```sql
fn() OVER (
  [PARTITION BY col, ...]   -- subgroup (like GROUP BY)
  [ORDER BY col [ASC|DESC]] -- enables cumulative / running calcs
  [ROWS|RANGE frame_clause] -- optional sliding window
)
```

### ROW_NUMBER -- latest record per group (replaces correlated subquery)
```sql
SELECT * FROM (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rn
  FROM orders
) t WHERE rn = 1;
```

### RANK vs DENSE_RANK vs ROW_NUMBER

| Function | Ties | Next rank after tie |
|---|---|---|
| `ROW_NUMBER()` | Arbitrary order | n+1 always |
| `RANK()` | Same rank | Skips (1,1,3) |
| `DENSE_RANK()` | Same rank | No skip (1,1,2) |

### Running total with explicit frame
```sql
SELECT date, amount,
  SUM(amount) OVER (
    PARTITION BY customer_id
    ORDER BY date
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS running_total,
  AVG(amount) OVER (
    ORDER BY date
    ROWS 6 PRECEDING          -- 7-day rolling average
  ) AS week_avg
FROM orders;
```

> **ROWS vs RANGE:** `ROWS` counts physical rows; `RANGE` groups rows with identical ORDER BY values. Use `ROWS` for running totals to avoid double-counting ties.

### Period-over-period comparison
```sql
SELECT month, revenue,
  LAG(revenue, 1)  OVER (ORDER BY month) AS prev_month,
  revenue - LAG(revenue, 1) OVER (ORDER BY month) AS change,
  LEAD(revenue, 1) OVER (ORDER BY month) AS next_month
FROM monthly_revenue;
```

### Quartile segmentation
```sql
SELECT customer_id, total_spend,
  NTILE(4) OVER (ORDER BY total_spend) AS quartile
FROM customer_totals;
```

> Caution: `NTILE` splits by row count, so tied values can land in different tiles. For fair grouping use `FLOOR((RANK() OVER (ORDER BY val) - 1) / bin_size) + 1`.

### Named window -- reuse across multiple functions
```sql
SELECT *,
  ROW_NUMBER() OVER w AS rn,
  SUM(amount)  OVER w AS running_total,
  AVG(amount)  OVER w AS running_avg
FROM orders
WINDOW w AS (PARTITION BY customer_id ORDER BY order_date
             ROWS UNBOUNDED PRECEDING);
```

---

## Additional Guidance

Extended guidance for `mysql-advanced-sql` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `2. Recursive CTEs`
- `3. Pivoting Data`
- `4. JSON Operations`
- `5. Gaps and Islands`
- `6. Deduplication`
- `7. Triggers`
- `8. Stored Procedures and Error Handling`
- `9. Conditional Aggregation`
- `10. Advanced GROUP BY`
- `11. Subqueries and CTEs as Variables`
- `12. Views and Sargable Date Patterns`
- `13. Anti-Patterns Reference`
- Additional deep-dive sections continue in the reference file.
