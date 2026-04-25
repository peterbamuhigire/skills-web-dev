# Advanced SQL Patterns Reference (MySQL 8.0+)

Based on "Leveling Up with SQL" by Mark Simon (Apress, 2023).

---

## Common Table Expressions (CTEs)

CTEs define named temporary result sets for the duration of a single statement.
They improve readability and allow logical decomposition of complex queries.

### Basic CTE

```sql
WITH monthly_sales AS (
    SELECT DATE_FORMAT(ordered, '%Y-%m') AS month,
           SUM(total) AS revenue, COUNT(*) AS order_count
    FROM sales WHERE tenant_id = 1 GROUP BY month
)
SELECT month, revenue, order_count FROM monthly_sales ORDER BY month;
```

### CTEs as Variables (Constants via Cross Join)

Define reusable constants in a CTE. Cross join makes them available to every row.

```sql
WITH vars AS (
    SELECT 0.1 AS tax_rate, 0.05 AS discount_rate, 100.00 AS free_shipping_threshold
)
SELECT p.id, p.name, p.price,
    ROUND(p.price * v.tax_rate, 2) AS tax,
    ROUND(p.price * (1 - v.discount_rate), 2) AS discounted_price,
    CASE WHEN p.price >= v.free_shipping_threshold
         THEN 'Free' ELSE 'Standard' END AS shipping
FROM products p, vars v WHERE p.tenant_id = 1;
```

### Multiple Chained CTEs

Each CTE can reference previously defined CTEs. Example: finding duplicate records.

```sql
WITH duplicates AS (
    SELECT email, tenant_id, COUNT(*) AS cnt
    FROM customers WHERE tenant_id = 1
    GROUP BY email, tenant_id HAVING cnt > 1
),
duplicate_details AS (
    SELECT c.id, c.email, c.name, c.created_at,
           ROW_NUMBER() OVER (PARTITION BY c.email ORDER BY c.created_at) AS rn
    FROM customers c
    JOIN duplicates d ON c.email = d.email AND c.tenant_id = d.tenant_id
)
SELECT id, email, name, created_at,
       CASE WHEN rn = 1 THEN 'KEEP' ELSE 'DUPLICATE' END AS action
FROM duplicate_details ORDER BY email, rn;
```

### Recursive CTEs

Two parts: the **anchor** (base case) and the **recursive member**, joined by `UNION ALL`.

**Sequence generation:**

```sql
WITH RECURSIVE seq (n) AS (
    SELECT 1 UNION ALL SELECT n + 1 FROM seq WHERE n < 100
)
SELECT n FROM seq;
```

**Date gap filling** (fills missing dates with zero):

```sql
WITH RECURSIVE dates (d) AS (
    SELECT DATE('2024-01-01')
    UNION ALL
    SELECT d + INTERVAL 1 DAY FROM dates WHERE d < '2024-12-31'
)
SELECT dates.d AS sale_date, COALESCE(s.total, 0) AS daily_total
FROM dates
LEFT JOIN daily_sales s ON dates.d = s.sale_date AND s.tenant_id = 1
ORDER BY dates.d;
```

**Hierarchy traversal** (employee org chart):

```sql
WITH RECURSIVE org AS (
    SELECT id, name, supervisor_id, 1 AS depth, CAST(name AS CHAR(1000)) AS path
    FROM employees WHERE supervisor_id IS NULL AND tenant_id = 1
    UNION ALL
    SELECT e.id, e.name, e.supervisor_id, o.depth + 1, CONCAT(o.path, ' > ', e.name)
    FROM employees e JOIN org o ON e.supervisor_id = o.id
)
SELECT id, name, depth, path FROM org ORDER BY depth, name;
```

---

## Window Functions (MySQL 8.0+)

Window functions calculate across a set of rows related to the current row without
collapsing the result set (unlike GROUP BY).

### Aggregate Windows

```sql
-- Running total
SELECT ordered_date, daily_total,
    SUM(daily_total) OVER (ORDER BY ordered_date ROWS UNBOUNDED PRECEDING) AS running_total
FROM daily_sales WHERE tenant_id = 1;

-- Moving average (7-day)
SELECT ordered_date, daily_total,
    ROUND(AVG(daily_total) OVER (ORDER BY ordered_date ROWS 6 PRECEDING), 2) AS moving_avg_7d
FROM daily_sales WHERE tenant_id = 1;

-- Compare each row to the group average
SELECT id, name, amount,
    ROUND(AVG(amount) OVER (), 2) AS group_avg,
    ROUND(amount - AVG(amount) OVER (), 2) AS diff_from_avg
FROM orders WHERE tenant_id = 1;
```

### PARTITION BY

Divides the window into independent groups processed separately.

```sql
-- Subtotals within groups
SELECT category, product_name, amount,
    SUM(amount) OVER (PARTITION BY category) AS category_total,
    ROUND(amount / SUM(amount) OVER (PARTITION BY category) * 100, 1) AS pct_of_category
FROM sales WHERE tenant_id = 1;

-- Running totals within partitions
SELECT department, employee_name, salary,
    SUM(salary) OVER (
        PARTITION BY department ORDER BY employee_name ROWS UNBOUNDED PRECEDING
    ) AS dept_running_total
FROM employees WHERE tenant_id = 1;
```

### Ranking Functions

| Function | Ties | Gaps | Use Case |
|----------|------|------|----------|
| `ROW_NUMBER()` | Arbitrary (unique) | No | Unique sequential numbering |
| `RANK()` | Same rank for ties | Yes (skips next) | Competition ranking |
| `DENSE_RANK()` | Same rank for ties | No (consecutive) | Dense ranking, top-N |
| `NTILE(n)` | Divides into n groups | N/A | Quartiles, deciles, percentiles |

```sql
SELECT name, total,
    ROW_NUMBER() OVER (ORDER BY total DESC) AS row_num,
    RANK()       OVER (ORDER BY total DESC) AS rnk,
    DENSE_RANK() OVER (ORDER BY total DESC) AS dense_rnk,
    NTILE(4)     OVER (ORDER BY total DESC) AS quartile
FROM orders WHERE tenant_id = 1;
```

**Top-N per group** (top 3 products per category):

```sql
WITH ranked AS (
    SELECT category, name, total,
           ROW_NUMBER() OVER (PARTITION BY category ORDER BY total DESC) AS rn
    FROM products WHERE tenant_id = 1
)
SELECT category, name, total FROM ranked WHERE rn <= 3;
```

### LAG and LEAD

Access values from previous or subsequent rows without a self-join.

```sql
SELECT ordered_date, daily_total,
    LAG(daily_total, 1)  OVER (ORDER BY ordered_date) AS prev_day,
    LEAD(daily_total, 1) OVER (ORDER BY ordered_date) AS next_day,
    daily_total - LAG(daily_total, 1) OVER (ORDER BY ordered_date) AS day_change
FROM daily_sales WHERE tenant_id = 1;
```

**Week-over-week comparison:**

```sql
SELECT ordered_date, daily_total,
    LAG(daily_total, 7) OVER (ORDER BY ordered_date) AS same_day_last_week,
    ROUND(
        (daily_total - LAG(daily_total, 7) OVER (ORDER BY ordered_date))
        / NULLIF(LAG(daily_total, 7) OVER (ORDER BY ordered_date), 0) * 100,
    1) AS wow_pct_change
FROM daily_sales WHERE tenant_id = 1;
```

### Framing Clause (ROWS vs RANGE)

The frame defines which rows within the partition the window function operates on.

**Syntax:** `function OVER ([PARTITION BY col] ORDER BY col {ROWS|RANGE} BETWEEN <start> AND <end>)`

**Frame borders:**

| Border | Meaning |
|--------|---------|
| `UNBOUNDED PRECEDING` | First row of the partition |
| `n PRECEDING` | n rows before current row |
| `CURRENT ROW` | The current row |
| `n FOLLOWING` | n rows after current row |
| `UNBOUNDED FOLLOWING` | Last row of the partition |

**ROWS vs RANGE:** `ROWS` counts physical rows (predictable, recommended). `RANGE`
groups rows with the same ORDER BY value (unexpected results with duplicates).

```sql
-- ROWS: previous 2 rows + current row (3-row window)
SUM(amount) OVER (ORDER BY ordered_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)
-- RANGE: all rows with ORDER BY values within 2 days of current
SUM(amount) OVER (ORDER BY ordered_date RANGE BETWEEN INTERVAL 2 DAY PRECEDING AND CURRENT ROW)
-- Full partition (all rows): default when ORDER BY is absent
SUM(amount) OVER ()
-- Cumulative from start to current row
SUM(amount) OVER (ORDER BY ordered_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
-- Centered 5-row window
AVG(amount) OVER (ORDER BY ordered_date ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING)
```

---

## Subquery Patterns

### Scalar Subqueries (in SELECT)

Return a single value per row. Useful for inline lookups.

```sql
SELECT o.id, o.total,
    (SELECT c.name FROM customers c WHERE c.id = o.customer_id) AS customer_name,
    (SELECT COUNT(*) FROM order_items oi WHERE oi.order_id = o.id) AS item_count
FROM orders o WHERE o.tenant_id = 1;
```

### List Subqueries (in WHERE with IN)

```sql
SELECT id, name FROM products
WHERE category_id IN (SELECT id FROM categories WHERE department = 'Electronics')
AND tenant_id = 1;
```

### Table Subqueries (in FROM)

Return a derived table. **Must be aliased in MySQL.**

```sql
SELECT s.month, s.revenue, s.order_count
FROM (
    SELECT DATE_FORMAT(created_at, '%Y-%m') AS month,
           SUM(total) AS revenue, COUNT(*) AS order_count
    FROM orders WHERE tenant_id = 1 GROUP BY month
) AS s
WHERE s.revenue > 10000 ORDER BY s.month;
```

### Correlated vs Non-Correlated

**Non-correlated** (evaluated once, result reused -- efficient):

```sql
SELECT name, salary FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees WHERE tenant_id = 1)
AND tenant_id = 1;
```

**Correlated** (re-evaluated per outer row -- expensive, prefer JOINs):

```sql
-- Correlated: runs inner query once per outer row
SELECT e.name, e.salary, e.department_id FROM employees e
WHERE e.salary > (
    SELECT AVG(e2.salary) FROM employees e2 WHERE e2.department_id = e.department_id
) AND e.tenant_id = 1;

-- Better: rewrite with CTE + JOIN
WITH dept_avg AS (
    SELECT department_id, AVG(salary) AS avg_salary
    FROM employees WHERE tenant_id = 1 GROUP BY department_id
)
SELECT e.name, e.salary, e.department_id FROM employees e
JOIN dept_avg d ON e.department_id = d.department_id
WHERE e.salary > d.avg_salary AND e.tenant_id = 1;
```

### WHERE EXISTS / NOT EXISTS

Preferred over `IN` / `NOT IN` for NULL safety and clarity.

```sql
-- Find authors WITH published books
SELECT a.id, a.name FROM authors a
WHERE EXISTS (SELECT 1 FROM books b WHERE b.author_id = a.id AND b.status = 'published')
AND a.tenant_id = 1;

-- Find authors WITHOUT any books (NULL-safe, unlike NOT IN)
SELECT a.id, a.name FROM authors a
WHERE NOT EXISTS (SELECT 1 FROM books b WHERE b.author_id = a.id)
AND a.tenant_id = 1;
```

**Why NOT EXISTS over NOT IN:** If the subquery in `NOT IN` returns any NULL value,
the entire condition evaluates to UNKNOWN and returns zero rows. `NOT EXISTS` handles
NULLs correctly.

---

## Aggregation Patterns

### GROUP BY with ROLLUP

Generates subtotals and a grand total row automatically.

```sql
SELECT
    COALESCE(region, 'ALL REGIONS') AS region,
    COALESCE(category, 'ALL CATEGORIES') AS category,
    SUM(amount) AS total, COUNT(*) AS order_count
FROM sales WHERE tenant_id = 1
GROUP BY region, category WITH ROLLUP;
```

Use `GROUPING()` to distinguish real NULLs from ROLLUP-generated NULLs:

```sql
SELECT
    IF(GROUPING(region), 'ALL REGIONS', region) AS region,
    IF(GROUPING(category), 'ALL CATEGORIES', category) AS category,
    SUM(amount) AS total
FROM sales WHERE tenant_id = 1
GROUP BY region, category WITH ROLLUP;
```

### Conditional Aggregation (Pivot)

Transform rows into columns using CASE inside aggregate functions.

```sql
SELECT DATE_FORMAT(created_at, '%Y-%m') AS month,
    SUM(CASE WHEN status = 'completed' THEN total ELSE 0 END) AS completed_revenue,
    SUM(CASE WHEN status = 'pending'   THEN total ELSE 0 END) AS pending_revenue,
    SUM(CASE WHEN status = 'cancelled' THEN total ELSE 0 END) AS cancelled_revenue,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) AS completed_count,
    COUNT(CASE WHEN status = 'pending'   THEN 1 END) AS pending_count
FROM orders WHERE tenant_id = 1 GROUP BY month ORDER BY month;
```

### GROUP_CONCAT

Aggregate values into a delimited string.

```sql
SELECT c.name AS category, COUNT(p.id) AS product_count,
    GROUP_CONCAT(p.name ORDER BY p.name SEPARATOR ', ') AS product_list
FROM categories c JOIN products p ON p.category_id = c.id
WHERE c.tenant_id = 1 GROUP BY c.id, c.name;
```

Default max length is 1024 bytes. Increase with `SET SESSION group_concat_max_len = 65535;`

### Statistical Functions

```sql
SELECT category, COUNT(*) AS cnt,
    ROUND(AVG(price), 2) AS mean_price,
    ROUND(STDDEV_SAMP(price), 2) AS std_dev,
    MIN(price) AS min_price, MAX(price) AS max_price
FROM products WHERE tenant_id = 1 GROUP BY category;
```

**Median** (MySQL has no built-in MEDIAN; use a subquery approach):

```sql
WITH ordered AS (
    SELECT price, ROW_NUMBER() OVER (ORDER BY price) AS rn, COUNT(*) OVER () AS total
    FROM products WHERE tenant_id = 1 AND category = 'Electronics'
)
SELECT ROUND(AVG(price), 2) AS median_price FROM ordered
WHERE rn IN (FLOOR((total + 1) / 2), CEIL((total + 1) / 2));
```

---

## Data Transformation

### CAST and Type Conversion

```sql
SELECT CAST('2024-06-15' AS DATE) AS date_val,
    CAST('123.45' AS DECIMAL(10, 2)) AS decimal_val,
    CAST(12345 AS CHAR) AS string_val,
    CAST('2024-06-15 14:30:00' AS DATETIME) AS datetime_val;
```

### COALESCE for NULL Handling

Returns the first non-NULL argument. Preferred over IFNULL for portability.

```sql
SELECT id,
    COALESCE(nickname, first_name, email) AS display_name,
    COALESCE(phone, 'N/A') AS phone_display,
    COALESCE(discount_rate, 0) AS effective_discount
FROM customers WHERE tenant_id = 1;
```

### CASE Expression

**Simple CASE** (compares a single expression):

```sql
SELECT id, status,
    CASE status
        WHEN 'active' THEN 'Active' WHEN 'suspended' THEN 'Suspended'
        WHEN 'closed' THEN 'Closed' ELSE 'Unknown'
    END AS status_label
FROM accounts WHERE tenant_id = 1;
```

**Searched CASE** (evaluates independent conditions):

```sql
SELECT id, total,
    CASE
        WHEN total >= 10000 THEN 'Platinum' WHEN total >= 5000 THEN 'Gold'
        WHEN total >= 1000  THEN 'Silver'   ELSE 'Bronze'
    END AS tier
FROM customers WHERE tenant_id = 1;
```

### Date Functions

```sql
SELECT NOW() AS current_datetime, CURDATE() AS current_date_only,
    DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s') AS formatted,
    DATE_FORMAT(NOW(), '%W, %M %d, %Y') AS human_readable,
    DATE_ADD(CURDATE(), INTERVAL 30 DAY) AS thirty_days_out,
    DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AS one_month_ago,
    DATEDIFF(NOW(), '2024-01-01') AS days_since_jan1,
    LAST_DAY(CURDATE()) AS end_of_month,
    EXTRACT(YEAR FROM NOW()) AS current_year,
    DAYOFWEEK(CURDATE()) AS dow_number, DAYNAME(CURDATE()) AS dow_name;
```

---

## Performance Notes for Advanced SQL

- **CTEs are not cached in MySQL.** Each reference re-evaluates the query. For CTEs
  referenced multiple times, consider a temporary table instead.
- **Window functions vs correlated subqueries:** Window functions are generally more
  efficient (single pass over sorted data) versus correlated subqueries (re-execute per row).
- **ROWS framing is more predictable than RANGE.** Use `ROWS` unless you specifically
  need `RANGE` semantics. `RANGE` produces unexpected results with duplicate ORDER BY values.
- **Recursive CTE depth limit:** MySQL defaults to `cte_max_recursion_depth = 1000`.
  Increase for deep hierarchies: `SET SESSION cte_max_recursion_depth = 5000;`
- **Indexing for window functions:** Create indexes matching `PARTITION BY` + `ORDER BY`
  columns. Without a matching index, MySQL must sort the entire result set.
  Example: `KEY idx_tenant_created (tenant_id, created_at);`

---

**Source:** Leveling Up with SQL (Mark Simon, Apress 2023)
**Last Updated:** 2026-03-04
**Maintained by:** Peter Bamuhigire
