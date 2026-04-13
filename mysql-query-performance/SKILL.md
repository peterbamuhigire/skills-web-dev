---
name: mysql-query-performance
description: 'Expert MySQL 8 query performance tuning: EXPLAIN analysis, index design,
  optimizer hints, slow query diagnosis, and profiling. Use when optimizing slow queries,
  designing indexes, analyzing EXPLAIN output, or diagnosing MySQL performance problems.'
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# MySQL Query Performance — Expert Reference

<!-- dual-compat-start -->
## Use When

- Expert MySQL 8 query performance tuning: EXPLAIN analysis, index design, optimizer hints, slow query diagnosis, and profiling. Use when optimizing slow queries, designing indexes, analyzing EXPLAIN output, or diagnosing MySQL performance problems.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `mysql-query-performance` or would be better handled by a more specific companion skill.
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
**Sources:** MySQL 8 Query Performance Tuning (Krogh, Apress 2020) + Efficient MySQL Performance (Nichter, O'Reilly 2022)

## 1. EXPLAIN ANALYZE vs EXPLAIN FORMAT=JSON

`EXPLAIN ANALYZE` (MySQL 8.0.18+) **executes** the query and returns actual measured statistics alongside estimates. This is the single most important diagnostic upgrade over plain EXPLAIN.

```sql
-- Standard EXPLAIN: estimates only, query NOT executed
EXPLAIN FORMAT=JSON SELECT * FROM orders WHERE customer_id = 42;

-- EXPLAIN ANALYZE: executes query, returns actual vs estimated
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 42;
```

**Reading EXPLAIN ANALYZE output — key fields:**

```
-> Index lookup on orders using idx_customer (customer_id=42)
   (cost=18.50 rows=41)
   (actual time=0.134..2.847 rows=38 loops=1)
```

- `cost=18.50 rows=41` — optimizer's **estimate** before execution
- `actual time=0.134..2.847` — real elapsed ms (first row .. last row)
- `rows=38 loops=1` — actual rows returned, loop count for nested joins
- When `rows` (estimated) diverges greatly from `actual rows`, index statistics are stale or a histogram is needed
- `loops=N` on an inner table means the entire sub-operation ran N times — multiply `actual time` by `loops` for total cost

**EXPLAIN FORMAT=JSON** shows the cost model breakdown without executing:

```sql
EXPLAIN FORMAT=JSON SELECT o.id, c.name
FROM orders o JOIN customers c ON o.customer_id = c.id
WHERE o.status = 'pending'\G
```

Look for `"cost_info"` → `"read_cost"` + `"eval_cost"` to understand why the optimizer chose a plan. The `"chosen"` boolean inside `"considered_execution_plans"` reveals rejected alternatives.

**EXPLAIN FOR CONNECTION** — get the live plan of a running query without re-running it (critical when index stats may have changed): `EXPLAIN FOR CONNECTION 42;`

---

## 2. Index Selection — Why MySQL Ignores Your Index

The optimizer uses a **cost model**, not just cardinality. It estimates whether an index lookup + primary key fetch costs less than a full table scan.

**MySQL ignores an index when:**
- Estimated rows to read exceed ~20-30% of the table (full scan becomes cheaper due to sequential I/O)
- Index statistics are stale (sampled pages give wrong cardinality)
- Column type mismatch prevents index use (e.g., `WHERE int_col = '42'` — implicit cast)
- Function wraps the indexed column: `WHERE YEAR(created_at) = 2024` (non-sargable)

**Index hints — use sparingly, as a last resort:**

```sql
SELECT * FROM orders USE INDEX (idx_status) WHERE status = 'pending';    -- suggest
SELECT * FROM orders FORCE INDEX (idx_customer) WHERE customer_id = 42;  -- enforce
SELECT * FROM orders IGNORE INDEX (idx_bad) WHERE status = 'pending';    -- exclude
```

Prefer **optimizer hints** (Section 7) over index hints in MySQL 8 — they are comment-based and query-block scoped, not syntax-embedded.

---

## 3. Covering Index Strategy and ICP

A **covering index** means MySQL reads only the index — no back-to-table lookup. EXPLAIN shows `Using index` in the Extra column (not `Using where; Using index`).

**Column ordering rule for composite indexes:**
1. Equality predicates first (highest selectivity first among equals)
2. Range predicate last (only one range column can be used for index access)
3. SELECT columns added after range (for covering, if range is the last filter)

```sql
-- Query: WHERE status = 'active' AND created_at > '2024-01-01' ORDER BY created_at
-- Correct index: (status, created_at)  -- equality first, range second
-- Wrong index:   (created_at, status)  -- range blocks status from being used

ALTER TABLE orders ADD INDEX idx_status_created (status, created_at);

-- Covering index — also include columns from SELECT:
ALTER TABLE orders ADD INDEX idx_cov (status, created_at, customer_id, amount);
-- Now SELECT customer_id, amount WHERE status=? AND created_at>? needs no row lookup
```

**Index Condition Pushdown (ICP)** — pushes extra WHERE conditions into the storage engine so non-matching rows are filtered before the full row is read. Appears as `Using index condition` in EXPLAIN Extra. Automatic — most valuable on range conditions on the first index column combined with equality on later columns.

**Primary key is appended to every secondary index.** Index `(status, created_at)` is really `(status, created_at, id)`. This means `ORDER BY id` can sometimes avoid filesort when filtering by status + created_at.

---

## 4. Index Merge — Usually a Warning Sign

Index merge occurs when MySQL combines multiple single-column indexes. EXPLAIN shows `type: index_merge` and `Using intersect(...)` / `Using union(...)` in Extra.

```sql
-- This may trigger index_merge if both idx_staff_id and idx_customer_id exist
SELECT * FROM payment WHERE staff_id = 1 AND customer_id = 75;

-- EXPLAIN output when index_merge fires:
-- type: index_merge
-- key: idx_fk_customer_id,idx_fk_staff_id
-- Extra: Using intersect(idx_fk_customer_id,idx_fk_staff_id); Using where
```

**Index merge algorithms:**

| Algorithm | Trigger | Extra column |
|-----------|---------|-------------|
| Intersection | AND between indexed cols | `Using intersect(idx1,idx2)` |
| Union | OR between indexed cols | `Using union(idx1,idx2)` |
| Sort-Union | OR with range conditions | `Using sort_union(idx1,idx2)` |

**Index merge is almost always slower than one well-designed composite index.** Each single-index scan returns row IDs that must be merged and deduplicated, then each row is fetched individually (random I/O). Replace with a composite index:

```sql
-- Instead of index_merge on (staff_id) + (customer_id):
ALTER TABLE payment ADD INDEX idx_staff_customer (staff_id, customer_id);

-- To disable index merge for a specific query:
SELECT /*+ NO_INDEX_MERGE(payment) */ * FROM payment WHERE staff_id = 1 AND customer_id = 75;
```

---

## 5. Invisible Index Trick

Before dropping an index, make it invisible. MySQL maintains it (no data loss) but the optimizer ignores it. If performance degrades, make it visible again instantly — no rebuild.

```sql
-- Make invisible (optimizer ignores, index still maintained)
ALTER TABLE orders ALTER INDEX idx_old_status INVISIBLE;

-- Test: run your queries, check EXPLAIN, monitor performance

-- If no regression after a week, drop it
ALTER TABLE orders DROP INDEX idx_old_status;

-- Emergency rollback — instant, no rebuild needed
ALTER TABLE orders ALTER INDEX idx_old_status VISIBLE;

-- Force a single session to use invisible indexes (testing)
SET SESSION optimizer_switch = 'use_invisible_indexes=on';
```

This is the safest way to test index removal on production — zero risk of permanent data loss during the evaluation period.

---

## 6. Histogram Statistics

Histograms fix optimizer mistakes on **non-indexed columns**. Without a histogram, the optimizer guesses ~33% of rows match a range condition, and ~1/N for equality (where N is number of distinct enum values).

```sql
-- Create/update histogram with 100 buckets
ANALYZE TABLE orders UPDATE HISTOGRAM ON status WITH 100 BUCKETS;
ANALYZE TABLE orders UPDATE HISTOGRAM ON created_at WITH 200 BUCKETS;

-- Multiple columns at once
ANALYZE TABLE film UPDATE HISTOGRAM ON length, rating WITH 256 BUCKETS;

-- Drop histogram
ANALYZE TABLE orders DROP HISTOGRAM ON status;

-- Inspect histogram data
SELECT
  COLUMN_NAME,
  HISTOGRAM->>'$."histogram-type"' AS histogram_type,
  JSON_LENGTH(HISTOGRAM->'$.buckets') AS bucket_count,
  CAST(HISTOGRAM->>'$."sampling-rate"' AS DECIMAL(4,2)) AS sampling_rate
FROM information_schema.COLUMN_STATISTICS
WHERE TABLE_SCHEMA = 'mydb' AND TABLE_NAME = 'orders';
```

**When to use histograms:** non-indexed column in WHERE/JOIN; skewed distribution; EXPLAIN shows wildly wrong `rows`/`filtered` estimates; wrong join driving table.

MySQL auto-selects: **singleton** (one bucket per distinct value, low-cardinality cols like `status`) vs **equi-height** (equal-frequency ranges, continuous data like `amount`).

---

## 7. Optimizer Hints (MySQL 8.0)

Optimizer hints are **query-block scoped** comment-embedded directives. They override `optimizer_switch` for a single query without session side-effects.

```sql
-- Force join order
SELECT /*+ JOIN_ORDER(orders, customers, products) */
  o.id, c.name, p.title
FROM orders o JOIN customers c ON o.customer_id = c.id
              JOIN products p ON o.product_id = p.id;

-- Prevent hash join (force nested loop)
SELECT /*+ NO_HASH_JOIN(o, c) */
  o.id FROM orders o JOIN customers c ON o.customer_id = c.id;

-- Force specific index usage
SELECT /*+ INDEX(o idx_status_created) */
  * FROM orders o WHERE o.status = 'active';

-- Disable index merge
SELECT /*+ NO_INDEX_MERGE(payment) */
  * FROM payment WHERE staff_id = 1 AND customer_id = 75;

-- Set session variable for one query only (MySQL 8.0.12+)
SELECT /*+ SET_VAR(join_buffer_size=8388608) SET_VAR(sort_buffer_size=4194304) */
  * FROM large_table ORDER BY col1, col2;

-- Name a subquery block for cross-reference
SELECT /*+ NO_INDEX_MERGE(@payment_block payment) */
  * FROM orders WHERE order_id IN (
    /*+ QB_NAME(payment_block) */
    SELECT order_id FROM payment WHERE staff_id = 1
  );
```

**Key hints:** `JOIN_ORDER(t1,t2,t3)` — force join sequence | `JOIN_FIXED_ORDER` — same as STRAIGHT_JOIN | `NO_HASH_JOIN(t1,t2)` / `HASH_JOIN(t1,t2)` — toggle hash join | `INDEX(t idx)` — force index | `NO_INDEX_MERGE(t)` — disable index merge | `BKA(t)` / `NO_BKA(t)` — batched key access | `SET_VAR(var=val)` — per-query variable override | `QB_NAME(name)` — name a query block for cross-reference.

---

## 8. Derived Table Materialization

When a subquery appears in FROM (a derived table), MySQL either **merges** it into the outer query or **materializes** it (executes it into a temp table first).

```sql
-- This derived table may be merged OR materialized depending on optimizer
SELECT ci.Name, co.Name AS Country
FROM (
  SELECT Code, Name FROM country WHERE Continent = 'Europe' ORDER BY SurfaceArea LIMIT 10
) co JOIN city ci ON ci.CountryCode = co.Code;
```

EXPLAIN shows `<derived2>` in the `table` column when materialization occurs. The `select_type` of the subquery will be `DERIVED`.

**Materialization signals in EXPLAIN:** `table: <derived2>`, `Extra: Using temporary` on the subquery row, JSON `"materialized_from_subquery": { "using_temporary_table": true }`.

```sql
-- Force materialization when optimizer incorrectly merges a subquery
SELECT /*+ NO_MERGE(co) */ ci.Name, co.Name
FROM (SELECT Code, Name FROM country WHERE Continent = 'Europe') co
JOIN city ci ON ci.CountryCode = co.Code;
-- Or: SET SESSION optimizer_switch = 'derived_merge=off';
```

Materialization is better when the derived table filters heavily and is joined multiple times. Merging suits simple pass-through subqueries.

---

## 9. Slow Query Log Analysis

```sql
-- Log ALL queries then analyse with pt-query-digest
SET GLOBAL long_query_time = 0;
SET GLOBAL slow_query_log = ON;
SELECT @@GLOBAL.slow_query_log_file;
-- pt-query-digest /var/lib/mysql/slow.log  → ranked profile by total time
```

**Performance Schema digest queries** — authoritative, survives log rotation:

```sql
-- Top 10 slowest queries by total execution time
SELECT
  DIGEST_TEXT,
  COUNT_STAR AS exec_count,
  ROUND(SUM_TIMER_WAIT/1e12, 3) AS total_sec,
  ROUND(AVG_TIMER_WAIT/1e12, 6) AS avg_sec,
  ROUND(MAX_TIMER_WAIT/1e12, 6) AS max_sec,
  SUM_ROWS_EXAMINED,
  SUM_ROWS_SENT,
  ROUND(SUM_ROWS_EXAMINED / NULLIF(SUM_ROWS_SENT, 0), 1) AS examine_ratio
FROM performance_schema.events_statements_summary_by_digest
WHERE SCHEMA_NAME = 'mydb'
ORDER BY SUM_TIMER_WAIT DESC
LIMIT 10;

-- Full table scans (no index used at all)
SELECT DIGEST_TEXT, COUNT_STAR, SUM_NO_INDEX_USED, SUM_NO_GOOD_INDEX_USED
FROM performance_schema.events_statements_summary_by_digest
WHERE SUM_NO_INDEX_USED > 0
ORDER BY SUM_NO_INDEX_USED DESC
LIMIT 10;

-- Queries creating temp tables on disk (memory overflow)
SELECT DIGEST_TEXT, COUNT_STAR, SUM_CREATED_TMP_DISK_TABLES, SUM_CREATED_TMP_TABLES
FROM performance_schema.events_statements_summary_by_digest
WHERE SUM_CREATED_TMP_DISK_TABLES > 0
ORDER BY SUM_CREATED_TMP_DISK_TABLES DESC
LIMIT 10;
```

The DIGEST is a SHA-256 of the normalised SQL (values replaced with `?`). Identical queries with different values hash to the same digest.

---

## 10. Essential Performance Schema Queries

```sql
-- 1. Unused indexes
SELECT object_schema, object_name, index_name FROM sys.schema_unused_indexes
WHERE object_schema NOT IN ('performance_schema','mysql','information_schema','sys');

-- 2. Lock wait time by table
SELECT object_schema, object_name, SUM_TIMER_WAIT/1e12 AS total_wait_sec
FROM performance_schema.table_lock_waits_summary_by_table
WHERE object_schema NOT IN ('performance_schema','mysql','sys')
ORDER BY SUM_TIMER_WAIT DESC LIMIT 10;

-- 3. InnoDB row lock waits (currently blocking)
SELECT r.trx_query AS waiting_query, b.trx_query AS blocking_query,
  r.trx_mysql_thread_id AS waiting_thread, b.trx_mysql_thread_id AS blocking_thread
FROM information_schema.innodb_lock_waits w
JOIN information_schema.innodb_trx r ON r.trx_id = w.requesting_trx_id
JOIN information_schema.innodb_trx b ON b.trx_id = w.blocking_trx_id;

-- 4. Temp table disk spill rate (disk/total > 10% → increase tmp_table_size)
SELECT VARIABLE_NAME, VARIABLE_VALUE FROM performance_schema.global_status
WHERE VARIABLE_NAME IN ('Created_tmp_tables','Created_tmp_disk_tables');

-- 5. Redundant indexes
SELECT * FROM sys.schema_redundant_indexes
WHERE table_schema NOT IN ('performance_schema','mysql','sys');
```

---

## 11. InnoDB Buffer Pool

The buffer pool caches data pages and index pages. It is the single most impactful memory allocation in MySQL.

```sql
-- Size: ~80% of available RAM for dedicated servers
-- innodb_buffer_pool_size = 12G  (for 16 GB RAM)

-- Multiple instances reduce mutex contention (one per GB of pool, max 64)
-- innodb_buffer_pool_instances = 8  (for 8+ GB pool)

-- Monitor hit rate — should be > 99%
-- (Innodb_buffer_pool_read_requests - Innodb_buffer_pool_reads) / read_requests * 100

-- Warm-up: innodb_buffer_pool_dump_at_shutdown=ON + innodb_buffer_pool_load_at_startup=ON
```

**Warm-up:** After restart the pool is empty and first queries are slow. With dump/load enabled, InnoDB saves the page list on shutdown and reloads on startup — warm in seconds. `innodb_dedicated_server = ON` (MySQL 8.0.3+) auto-configures pool size and redo log from detected RAM (dedicated servers only).

---

## 12. Sort Optimisation (filesort vs Index Sort)

`filesort` appears in EXPLAIN Extra when MySQL cannot use an index to satisfy ORDER BY. The name is misleading — it uses memory first (`sort_buffer_size`), only spilling to disk when the sort buffer is too small.

```sql
-- filesort uses sort_buffer_size (per-query allocation)
-- Default: 256KB — increase only for the session when needed
SET SESSION sort_buffer_size = 4 * 1024 * 1024;  -- 4MB for this query only

-- Better: use SET_VAR optimizer hint
SELECT /*+ SET_VAR(sort_buffer_size=4194304) */
  * FROM large_table ORDER BY non_indexed_col;
```

**Three ways ORDER BY avoids filesort:** (1) index on ORDER BY column directly; (2) WHERE equality on leading index columns + ORDER BY on trailing: `INDEX(a,b)` + `WHERE a=? ORDER BY b`; (3) the hidden PK appended to every secondary index — `INDEX(status)` supports `ORDER BY id` for free.

**Detect disk spill:** `SELECT VARIABLE_VALUE FROM performance_schema.global_status WHERE VARIABLE_NAME = 'Sort_merge_passes';` — non-zero means sort_buffer_size is too small for some queries.

---

## 13. JOIN Algorithms

**Block Nested Loop (BNL)** — pre-8.0.18 default for joins without indexes. Buffers rows from the outer table and scans the inner table once per buffer fill. `Using join buffer (Block Nested Loop)` in EXPLAIN Extra.

**Hash Join** (MySQL 8.0.18+) — builds a hash table from the smaller table in memory, then probes it with rows from the larger table. Dramatically faster than BNL for large unindexed joins.

```sql
-- EXPLAIN shows: Extra: Using join buffer (hash join)
-- Force/prevent: /*+ HASH_JOIN(o, c) */ or /*+ NO_HASH_JOIN(o, c) */
-- Increase join buffer for large unindexed joins (default 256KB is too small):
SET SESSION join_buffer_size = 8 * 1024 * 1024;
```

**Key join insight:** On a 3-table join with 100 rows each and no indexes, rows examined = 100 × 100 × 100 = 1,000,000. The index on the join column is the critical fix, not buffer size.

---

## 14. Partitioning for Performance

Range partitioning for time-series data enables **partition pruning** — MySQL skips entire partitions that cannot contain matching rows.

```sql
CREATE TABLE events (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  created_at DATETIME NOT NULL,
  payload JSON,
  PRIMARY KEY (id, created_at)  -- partition key must be in PK for InnoDB
) ENGINE=InnoDB
PARTITION BY RANGE (UNIX_TIMESTAMP(created_at)) (
  PARTITION p2024_01 VALUES LESS THAN (UNIX_TIMESTAMP('2024-02-01')),
  PARTITION p2024_02 VALUES LESS THAN (UNIX_TIMESTAMP('2024-03-01')),
  PARTITION p2024_03 VALUES LESS THAN (UNIX_TIMESTAMP('2024-04-01')),
  PARTITION p_future  VALUES LESS THAN MAXVALUE
);

-- EXPLAIN shows which partitions are accessed
EXPLAIN SELECT * FROM events WHERE created_at BETWEEN '2024-02-01' AND '2024-02-28'\G
-- partitions: p2024_02   (only one partition scanned — pruning works)
```

**Partition overhead traps:**
- Do not partition tables under 1M rows — overhead exceeds benefit
- The partition key must be in every unique index (including the PK)
- Index lookups that don't include the partition key scan ALL partitions
- `ALTER TABLE ... ADD PARTITION` is fast (metadata only); `REORGANIZE PARTITION` rebuilds data

---

## 15. Query Rewrite Patterns

### Non-sargable predicates (cannot use index)

```sql
-- BAD: function on indexed column blocks index
WHERE YEAR(created_at) = 2024
-- GOOD: range on the column directly
WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'

-- BAD: implicit type cast
WHERE int_id = '42'      -- varchar compared to int
-- GOOD: match types
WHERE int_id = 42

-- BAD: leading wildcard
WHERE name LIKE '%smith'  -- cannot use B-tree index
-- GOOD: use FULLTEXT index, or rewrite to suffix search with reversed column
WHERE name LIKE 'smith%'  -- can use index
```

### Correlated subquery → JOIN

```sql
-- BAD: correlated subquery — re-executes for every outer row
SELECT * FROM orders o
WHERE o.customer_id IN (SELECT customer_id FROM customers WHERE country = 'UG');

-- GOOD: semi-join rewrite — executes once
SELECT o.* FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE c.country = 'UG';
```

### COUNT(*) vs COUNT(col)

```sql
COUNT(*)      -- counts all rows including NULLs — uses index optimisation
COUNT(col)    -- counts non-NULL values — cannot always use index optimisation
COUNT(1)      -- equivalent to COUNT(*) — no difference in MySQL 8
```

### LIMIT with ORDER BY on non-indexed column

```sql
-- BAD: filesort entire result, then limit — O(N log N)
SELECT * FROM orders ORDER BY total_amount DESC LIMIT 10;
-- GOOD: index on total_amount lets MySQL read 10 rows directly, no sort
ALTER TABLE orders ADD INDEX idx_total (total_amount);
```

**DISTINCT vs GROUP BY:** equivalent in MySQL — both use the same index. Prefer `GROUP BY` for clarity when aggregates are involved.

---

## 16. Anti-Patterns Quick Reference

| Anti-Pattern | Consequence | Fix |
|---|---|---|
| `WHERE FUNCTION(col) = val` | Index unusable | Rewrite as range on raw column |
| `WHERE col LIKE '%prefix'` | Full scan | Use FULLTEXT or reverse the column |
| `SELECT *` on large tables | Over-fetches columns, hurts covering index | Select only needed columns |
| `IN (SELECT ...)` correlated | Re-runs subquery per row | Rewrite as JOIN |
| `ORDER BY rand()` | Full filesort every time | Application-side shuffle or keyset pagination |
| Index merge instead of composite | 2x random I/O + sort-merge | Create composite index |
| No primary key | Hidden 6-byte global counter, no replication key | Always define explicit PK |
| Many indexes on write-heavy table | Insert/update overhead; optimizer confusion | Audit with `sys.schema_unused_indexes` |
| `long_query_time = 1` | Misses 900ms queries | Set to `0.1` or `0` for profiling |
| Partitioning small tables | Management overhead exceeds benefit | Only partition > 1M rows with time-based access |
| `COUNT(col)` where `COUNT(*)` intended | NULL rows not counted | Use `COUNT(*)` for row counts |
| `JOIN` without index on join column | Full scan per outer row | Add index on the join column |

---

## Sources

- *MySQL 8 Query Performance Tuning*, Jesper Wisborg Krogh (Apress, 2020) — Chapters 14–17, 19–20, 23–24
- *Efficient MySQL Performance*, Daniel Nichter (O'Reilly, 2022) — Chapters 1–3, 6, 8
