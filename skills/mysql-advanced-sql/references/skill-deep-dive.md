# mysql-advanced-sql Deep Dive

This file contains the extended guidance moved out of [../SKILL.md](../SKILL.md) so the skill entrypoint stays under the repository size limit.

## Included Sections

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
- `Quick Decision Guide`

## 2. Recursive CTEs

MySQL 8.0 requires the `RECURSIVE` keyword. Anchor + recursive members joined by `UNION ALL`.

Set the session depth limit when needed: `SET SESSION cte_max_recursion_depth = 10000;`

### Organisation chart / category tree
```sql
WITH RECURSIVE hierarchy AS (
  SELECT id, name, parent_id,
    0 AS depth,
    CAST(name AS CHAR(1000)) AS path
  FROM categories
  WHERE parent_id IS NULL

  UNION ALL

  SELECT c.id, c.name, c.parent_id,
    h.depth + 1,
    CONCAT(h.path, ' > ', c.name)
  FROM categories c
  JOIN hierarchy h ON c.parent_id = h.id
  WHERE h.depth < 10           -- depth guard against cycles / bad data
)
SELECT * FROM hierarchy ORDER BY path;
```

### Generate a date series and fill gaps
```sql
WITH RECURSIVE dates AS (
  SELECT CURDATE() - INTERVAL 29 DAY AS dt
  UNION ALL
  SELECT dt + INTERVAL 1 DAY FROM dates WHERE dt < CURDATE()
)
SELECT dt, COALESCE(COUNT(o.id), 0) AS orders
FROM dates
LEFT JOIN orders o ON DATE(o.created_at) = dt
GROUP BY dt
ORDER BY dt;
```

---

## 3. Pivoting Data

MySQL has no native `PIVOT` syntax. Use conditional aggregation or dynamic SQL.

### Static pivot with MAX(CASE WHEN)
```sql
SELECT
  product_id,
  MAX(CASE WHEN month = 1  THEN revenue END) AS jan,
  MAX(CASE WHEN month = 2  THEN revenue END) AS feb,
  MAX(CASE WHEN month = 3  THEN revenue END) AS mar,
  MAX(CASE WHEN month = 12 THEN revenue END) AS dec
FROM monthly_sales
GROUP BY product_id;
```

### Dynamic pivot using prepared statements
```sql
SET @sql = NULL;

SELECT GROUP_CONCAT(
  DISTINCT CONCAT(
    'MAX(CASE WHEN month = ', month,
    ' THEN revenue END) AS m', month
  )
  ORDER BY month
) INTO @sql
FROM monthly_sales;

SET @sql = CONCAT(
  'SELECT product_id, ', @sql,
  ' FROM monthly_sales GROUP BY product_id'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
```

---

## 4. JSON Operations

MySQL 8 has mature JSON support. `JSON_TABLE` is the most powerful feature -- it shreds JSON into relational rows.

### Path operators
```sql
-- -> returns JSON type; ->> returns unquoted string
SELECT
  metadata->'$.customer.name'  AS name_json,
  metadata->>'$.customer.name' AS name_text,
  JSON_LENGTH(metadata->'$.tags') AS tag_count
FROM orders;
```

### JSON_TABLE -- flatten a JSON array into rows
```sql
SELECT jt.*
FROM products,
JSON_TABLE(
  products.attributes,
  '$[*]' COLUMNS (
    attr_name  VARCHAR(50)  PATH '$.name',
    attr_value VARCHAR(100) PATH '$.value',
    attr_unit  VARCHAR(20)  PATH '$.unit' DEFAULT 'null' ON EMPTY
  )
) AS jt;
```

### Generated column to index a JSON field
```sql
ALTER TABLE orders
  ADD COLUMN customer_email VARCHAR(255)
    AS (JSON_UNQUOTE(metadata->>'$.customer.email')) STORED,
  ADD INDEX idx_customer_email (customer_email);
-- WHERE customer_email = 'x@y.com' now uses the index
```

### Build JSON aggregates from rows
```sql
SELECT JSON_OBJECTAGG(config_key, config_value) FROM app_config;

SELECT JSON_ARRAYAGG(
  JSON_OBJECT('id', id, 'name', name, 'price', price)
) FROM products WHERE active = 1;
```

---

## 5. Gaps and Islands

### Find gaps in a numeric sequence
```sql
SELECT a.id + 1 AS gap_start, MIN(b.id) - 1 AS gap_end
FROM invoices a
JOIN invoices b ON a.id < b.id
WHERE NOT EXISTS (SELECT 1 FROM invoices c WHERE c.id = a.id + 1)
GROUP BY a.id
HAVING gap_start <= gap_end;
```

### Island detection: group consecutive dates
```sql
SELECT
  MIN(dt) AS island_start,
  MAX(dt) AS island_end,
  COUNT(*) AS days
FROM (
  SELECT dt,
    dt - INTERVAL (ROW_NUMBER() OVER (ORDER BY dt)) DAY AS grp
  FROM active_days
) t
GROUP BY grp;
```

---

## 6. Deduplication

### Delete duplicates keeping the lowest id
```sql
WITH ranked AS (
  SELECT id,
    ROW_NUMBER() OVER (PARTITION BY email ORDER BY id) AS rn
  FROM users
)
DELETE FROM users WHERE id IN (SELECT id FROM ranked WHERE rn > 1);
```

### UPSERT -- INSERT ... ON DUPLICATE KEY UPDATE
```sql
INSERT INTO product_stats (product_id, view_count, last_viewed)
VALUES (42, 1, NOW())
ON DUPLICATE KEY UPDATE
  view_count  = view_count + 1,
  last_viewed = NOW();
```

> `REPLACE INTO` performs DELETE + INSERT, fires triggers twice, and resets auto-increment. Always prefer `ON DUPLICATE KEY UPDATE`.

---

## 7. Triggers

### Audit trigger (AFTER UPDATE)
```sql
DELIMITER //
CREATE TRIGGER orders_audit_after_update
AFTER UPDATE ON orders
FOR EACH ROW
BEGIN
  IF OLD.status != NEW.status THEN
    INSERT INTO orders_audit
      (order_id, old_status, new_status, changed_at, changed_by)
    VALUES (OLD.id, OLD.status, NEW.status, NOW(), NEW.updated_by);
  END IF;
END //
DELIMITER ;
```

### Soft-delete archive trigger (BEFORE DELETE)
```sql
DELIMITER //
CREATE TRIGGER sales_before_delete
BEFORE DELETE ON sales
FOR EACH ROW
BEGIN
  INSERT INTO deleted_sales (sale_id, customer_id, ordered, archived_at)
  VALUES (OLD.id, OLD.customer_id, OLD.ordered, NOW());
END //
DELIMITER ;
```

### Trigger rules
- A trigger **cannot modify the same table** it is attached to.
- `NEW` is available in INSERT/UPDATE; `OLD` in UPDATE/DELETE.
- Use `BEFORE` to validate or transform; `AFTER` to log or cascade.
- Triggers fire **per row** -- bulk DML fires once per affected row.
- DML, DDL, and logon trigger types exist; DML is most common.

---

## 8. Stored Procedures and Error Handling

### Transaction with EXIT HANDLER and RESIGNAL
```sql
DELIMITER //
CREATE PROCEDURE transfer_funds(
  IN from_id INT,
  IN to_id   INT,
  IN amount  DECIMAL(10,2)
)
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;  -- re-throw to caller; never silently swallow errors
  END;

  START TRANSACTION;

  UPDATE accounts SET balance = balance - amount WHERE id = from_id;
  IF ROW_COUNT() = 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Source account not found';
  END IF;

  UPDATE accounts SET balance = balance + amount WHERE id = to_id;
  IF ROW_COUNT() = 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Destination account not found';
  END IF;

  COMMIT;
END //
DELIMITER ;
```

### Dynamic SQL -- always use ? placeholders
```sql
SET @sql = CONCAT('SELECT * FROM `', tbl, '` WHERE `', col, '` = ?');
SET @val = :user_input;
PREPARE stmt FROM @sql;
EXECUTE stmt USING @val;
DEALLOCATE PREPARE stmt;
-- Never concatenate user input directly -- SQL injection risk
```

### CTE as query-level constant
```sql
WITH vars AS (SELECT 0.16 AS tax_rate, 0.05 AS discount_rate)
SELECT p.id, p.price, p.price * v.tax_rate AS tax
FROM products p, vars v WHERE p.active = 1;
```

---

## 9. Conditional Aggregation

### Multi-metric single-pass query
```sql
SELECT
  DATE_FORMAT(created_at, '%Y-%m')                              AS month,
  COUNT(*)                                                       AS total_orders,
  SUM(CASE WHEN status = 'completed' THEN 1    ELSE 0 END)      AS completed,
  SUM(CASE WHEN status = 'refunded'  THEN total ELSE 0 END)     AS refunded_amount,
  AVG(CASE WHEN status = 'completed' THEN total END)            AS avg_completed_value,
  SUM(total)                                                     AS gross_revenue,
  ROUND(
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END)
    / COUNT(*) * 100, 2
  )                                                              AS completion_rate_pct
FROM orders
GROUP BY DATE_FORMAT(created_at, '%Y-%m')
ORDER BY month;
```

---

## 10. Advanced GROUP BY

### ROLLUP for subtotals and grand total
```sql
SELECT
  COALESCE(region,       'TOTAL') AS region,
  COALESCE(product_line, 'ALL')   AS product_line,
  SUM(revenue)                    AS revenue
FROM sales
GROUP BY region, product_line WITH ROLLUP;
```

### GROUP_CONCAT with ordering and length awareness
```sql
-- Default max is 1024 bytes; raise for larger data
SET SESSION group_concat_max_len = 65536;

SELECT
  customer_id,
  GROUP_CONCAT(product_name ORDER BY order_date SEPARATOR ', ') AS products_ordered
FROM order_items oi
JOIN products p ON oi.product_id = p.id
GROUP BY customer_id;
```

---

## 11. Subqueries and CTEs as Variables

### EXISTS vs NOT IN with NULLs
```sql
-- SAFE: NOT EXISTS handles NULLs correctly
SELECT * FROM orders o
WHERE NOT EXISTS (SELECT 1 FROM returns r WHERE r.order_id = o.id);

-- DANGEROUS: returns 0 rows silently if subquery has any NULL
-- WHERE id NOT IN (SELECT order_id FROM returns)
```

### Lateral join (MySQL 8.0.14+)
```sql
SELECT c.id, c.name, recent.order_date, recent.total
FROM customers c
JOIN LATERAL (
  SELECT order_date, total FROM orders
  WHERE customer_id = c.id
  ORDER BY order_date DESC LIMIT 1
) AS recent ON TRUE;
```

---

## 12. Views and Sargable Date Patterns

### Date and time -- sargable patterns
```sql
-- Sargable: index on created_at is used
WHERE created_at >= NOW() - INTERVAL 30 DAY

-- NOT sargable: function on column prevents index use
-- WHERE DATE(created_at) >= CURDATE() - INTERVAL 30 DAY

-- Timezone conversion
SELECT CONVERT_TZ(created_at, '+00:00', 'Africa/Nairobi') AS local_time FROM events;
```

---

## 13. Anti-Patterns Reference

| Anti-Pattern | Problem | Correct Pattern |
|---|---|---|
| `WHERE YEAR(col) = 2024` | Function on column disables index | `WHERE col >= '2024-01-01' AND col < '2025-01-01'` |
| Correlated subquery in `SELECT` list | Executes once per row (N+1 in SQL) | Rewrite as `LEFT JOIN` with aggregation |
| `SELECT *` on wide table | Pulls all columns including BLOBs | Explicit column list |
| `HAVING` without `GROUP BY` | Filters post-scan instead of pre-scan | Use `WHERE` for row-level filters |
| `INSERT INTO ... SELECT` without index | Full scan + lock escalation | Add index to source filter columns first |
| String comparison on numeric column | Implicit cast prevents index use | Fix the column data type |
| `OR` across different columns | Cannot use composite index | Rewrite as `UNION ALL` |
| `NOT IN (subquery)` with NULLs | Returns 0 rows silently | Use `NOT EXISTS` |
| `LIMIT` without `ORDER BY` | Non-deterministic results | Always add `ORDER BY` |
| Cursor-based row iteration | 10-100x slower than set operations | Rewrite as a set-based query |
| `REPLACE INTO` for upsert | Fires triggers twice, resets auto-increment | Use `INSERT ... ON DUPLICATE KEY UPDATE` |
| `ORDER BY RAND()` on large tables | Sorts entire table -- O(n log n) | Use `WHERE id >= FLOOR(RAND() * MAX(id)) LIMIT 1` |
| Concatenating user input into dynamic SQL | SQL injection | Use `PREPARE ... EXECUTE ... USING @param` |
| Missing `DELIMITER` in stored routines | Parser error on `;` inside body | Wrap with `DELIMITER //` ... `DELIMITER ;` |

---

## Quick Decision Guide

| Task | Pattern |
|---|---|
| Latest row per group | `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)`, filter `rn=1` |
| Running total | `SUM() OVER (ORDER BY ... ROWS UNBOUNDED PRECEDING)` |
| Month-over-month diff | `LAG()` / `LEAD()` |
| Tree traversal | Recursive CTE with depth guard |
| Cross-tab report | `MAX(CASE WHEN ...)` pivot |
| Shred JSON array | `JSON_TABLE()` |
| Index a JSON field | Generated STORED column + regular index |
| Missing IDs in sequence | Gaps query with `NOT EXISTS` |
| Consecutive date groups | Island detection (ROW_NUMBER subtraction trick) |
| Bulk upsert | `INSERT ... ON DUPLICATE KEY UPDATE` |
| Auto-archive on delete | `BEFORE DELETE` trigger |
| Multi-step transaction | Stored procedure with `DECLARE EXIT HANDLER` + `RESIGNAL` |
| Subtotals + grand total | `GROUP BY ... WITH ROLLUP` |
