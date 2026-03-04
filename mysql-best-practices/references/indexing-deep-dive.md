# MySQL Indexing Deep Dive

Comprehensive indexing reference for InnoDB (MySQL 8.0+).
Sources: "Efficient MySQL Performance" (Nichter, 2022), "Mastering MySQL Administration" (Kumar et al., 2024).

---

## InnoDB B-Tree Internals

**Core truth: In InnoDB, a table IS an index.**

- The **primary key** is the **clustered index** -- row data lives in PK B-tree leaf nodes. No separate heap file.
- If no PK is defined, InnoDB uses the first `UNIQUE NOT NULL` index, or generates a hidden 6-byte row ID.
- **Secondary indexes** store their columns **plus the PK value** appended at the rightmost end. Lookup is two-step: traverse secondary B-tree, then use PK to fetch the full row from the clustered index.
- InnoDB pages are **16 KB** (`innodb_page_size`). Wider indexes = fewer keys per page = taller trees = more I/O.

```
Secondary index (tenant_id, status):
Leaf node stores: [tenant_id | status | id]   ← hidden PK appended

Lookup: secondary index → finds id=42 → clustered index lookup → full row
```

**Implication:** Keep PKs short (INT/BIGINT). A 36-byte UUID PK is appended to EVERY secondary index.

---

## Leftmost Prefix Requirement

**MySQL can ONLY use a composite index starting from its leftmost column.**

Given `idx_abc (a, b, c)`:

| WHERE Clause | Index Used? | Columns Used |
|---|---|---|
| `WHERE a = 1` | Yes | a |
| `WHERE a = 1 AND b = 2` | Yes | a, b |
| `WHERE a = 1 AND b = 2 AND c = 3` | Yes | a, b, c |
| `WHERE b = 2` | **No** | None |
| `WHERE b = 2 AND c = 3` | **No** | None |
| `WHERE a = 1 AND c = 3` | Partial | a only (c skipped) |

### Verifying with key_len

```sql
-- Index: idx_abc (a INT, b INT, c INT) — each INT = 4 bytes; nullable adds 1
EXPLAIN SELECT * FROM t WHERE a = 1;           -- key_len: 4  (a only)
EXPLAIN SELECT * FROM t WHERE a = 1 AND b = 2; -- key_len: 8  (a, b)
EXPLAIN SELECT * FROM t WHERE a = 1 AND b = 2 AND c = 3; -- key_len: 12 (all)
EXPLAIN SELECT * FROM t WHERE b = 2;           -- key: NULL (not used)
```

**Extends to GROUP BY and ORDER BY.** `ORDER BY b, c` cannot use `idx_abc` unless `a` is pinned by equality in WHERE.

---

## ESR Rule (Equality, Sort, Range)

Optimal column order in a composite index:

1. **E -- Equality** first (`=`, `IN`, `IS NULL`)
2. **S -- Sort** next (`ORDER BY`)
3. **R -- Range** last (`<`, `>`, `BETWEEN`, `LIKE 'prefix%'`)

**A range condition on column N stops index use for columns N+1 and beyond.**

```sql
-- BAD: range on one column, sort on another
SELECT id, total FROM orders
WHERE tenant_id = 5 AND amount > 100 ORDER BY created_at DESC;

-- BAD index: (tenant_id, amount, created_at)
-- amount range STOPS index → created_at sort causes filesort

-- GOOD index (ESR): (tenant_id, created_at, amount)
-- E: tenant_id=5 (equality), S: created_at DESC (no filesort), R: amount>100 (filtered after)
```

**Rule of thumb:** `Using filesort` + range predicate + ORDER BY on different columns = check ESR order.

---

## EXPLAIN Plan Deep Dive

### Access Types (best to worst)

| Type | Meaning | Rows Read |
|---|---|---|
| `const` | PK/unique, single row | 1 |
| `eq_ref` | Join via PK/unique, one row per join | 1 per |
| `ref` | Non-unique index, equality | Few |
| `range` | Index range scan (BETWEEN, <, >, IN) | Subset |
| `index` | Full index scan (every entry) | All index |
| `ALL` | **Full table scan -- no index** | **All rows** |

### Key Fields

- **key**: Index used (NULL = none) | **key_len**: Bytes of index used (how many columns matched)
- **rows**: Estimated rows to examine | **filtered**: % remaining after WHERE
- **Extra**: Critical details (below)

### Extra Column Values

| Value | Meaning | Action |
|---|---|---|
| `Using index` | Covering index -- no row lookup | Good |
| `Using index condition` | ICP -- engine filters via index | Good |
| `Using where` | Server filters after engine read | Check if index can help |
| `Using filesort` | Extra sort pass | Add index for ORDER BY |
| `Using temporary` | Temp table (GROUP BY, DISTINCT) | Add index or restructure |
| `Using join buffer` | No index on join column | **Add join index** |

### Red Flags

- `type=ALL` + `key=NULL` = full table scan. Add an index.
- `Select_full_join > 0` (from `SHOW GLOBAL STATUS`) = join without index. Find and fix.
- `Using filesort` on 500K+ rows = apply ESR rule.

### EXPLAIN ANALYZE (8.0.18+)

```sql
EXPLAIN ANALYZE SELECT o.id, c.name FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE o.tenant_id = 5 AND o.status = 'active';
-- Shows actual time/rows vs estimates. Large discrepancies → run ANALYZE TABLE.
```

---

## Covering Indexes

Index contains ALL columns the query reads. Engine returns results from index alone.

```sql
SELECT tenant_id, status, COUNT(*) FROM orders WHERE tenant_id = 5 GROUP BY status;
-- Covering index: ADD INDEX idx_cover (tenant_id, status);
-- EXPLAIN Extra: Using index ← confirmed
```

**When practical:** Narrow queries (few columns), SELECT list within index.
**When NOT to force:** Don't bloat indexes to cover `SELECT *`. Write amplification outweighs benefit.

---

## Index Condition Pushdown (ICP)

Storage engine evaluates WHERE conditions on indexed columns **before** reading full rows (since MySQL 5.6).

```sql
-- Index: (last_name, first_name)
SELECT * FROM people WHERE last_name LIKE 'Sm%' AND first_name LIKE 'J%';
-- Without ICP: reads every 'Sm%' row, server filters first_name
-- With ICP: engine checks first_name in index first, skips non-matches
-- EXPLAIN Extra: Using index condition
```

Automatic when applicable. Reduces random I/O on range scans with additional indexed column filters.

---

## Index Types in MySQL

| Type | Structure | Use Case | Example |
|---|---|---|---|
| Primary | B-tree (clustered) | Row identity, joins | `PRIMARY KEY (id)` |
| Unique | B-tree | Enforce uniqueness | `UNIQUE KEY (email)` |
| Regular | B-tree | General lookups | `INDEX (status)` |
| Compound | B-tree | Multi-column filters | `INDEX (tenant_id, status)` |
| Prefix | B-tree | Long text columns | `INDEX (description(50))` |
| Fulltext | Inverted index | Text search | `FULLTEXT (body)` |
| Spatial | R-tree | GIS data | `SPATIAL INDEX (location)` |
| Descending | B-tree (desc) | DESC sorts (8.0+) | `INDEX (created_at DESC)` |
| Functional | B-tree on expr | Computed values (8.0.13+) | `INDEX ((LOWER(email)))` |
| Invisible | B-tree (hidden) | Test removal (8.0+) | `ALTER INDEX idx INVISIBLE` |
| Hash | Hash table | MEMORY engine only | Exact match, no range |

```sql
-- Descending index
ALTER TABLE events ADD INDEX idx_created_desc (created_at DESC);
-- Functional index
ALTER TABLE users ADD INDEX idx_email_lower ((LOWER(email)));
-- Invisible index (test dropping safely)
ALTER TABLE orders ALTER INDEX idx_old_status INVISIBLE;
-- Monitor, then DROP or set VISIBLE
```

---

## ORDER BY Optimization

MySQL avoids filesort when the index delivers rows in requested order.

**1. ORDER BY uses leftmost prefix:**

```sql
-- Index: (a, b, c)
SELECT * FROM t ORDER BY a, b;    -- No filesort
SELECT * FROM t ORDER BY b, c;    -- Filesort (skips a)
```

**2. Hold leftmost constant, order by next:**

```sql
-- Index: (tenant_id, created_at)
SELECT * FROM orders WHERE tenant_id = 5 ORDER BY created_at DESC; -- No filesort
```

**3. Hidden PK at end of secondary index:**

```sql
-- Index: (status) → internally (status, id)
SELECT * FROM orders WHERE status = 'active' ORDER BY id; -- No filesort
```

**Mixed directions (8.0+):** `ORDER BY a ASC, b DESC` requires `INDEX (a ASC, b DESC)`.

---

## GROUP BY Optimization

```sql
-- Index: (tenant_id, status)
EXPLAIN SELECT tenant_id, status, COUNT(*) FROM orders GROUP BY tenant_id, status;
-- Extra: Using index for group-by ← loose index scan, reads one entry per group
```

**Requirements:** GROUP BY columns = leftmost prefix of index. Aggregates: MIN, MAX, COUNT, SUM, AVG.

```sql
-- Works: GROUP BY a       with index (a, b)
-- Works: GROUP BY a, b    with index (a, b, c)
-- Fails: GROUP BY b       with index (a, b)     ← skips leftmost
-- Fails: GROUP BY a, c    with index (a, b, c)  ← skips b
```

---

## Join Optimization

### Nested Loop Join (NLJ) -- Default

For each outer row, looks up inner table via index. **Every JOIN column MUST be indexed.**

```sql
SELECT o.id, c.name FROM orders o
JOIN customers c ON c.id = o.customer_id;
-- customers.id: PRIMARY KEY (indexed)
-- orders.customer_id: needs INDEX idx_customer (customer_id)
-- EXPLAIN inner table should show eq_ref or ref, NOT ALL
```

### Hash Join (8.0.18+)

Auto-used when no index on join column. Better than block NLJ but **slower than indexed NLJ**. Fix: add the missing index.

### Join Rules

1. Every JOIN column indexed on the inner table
2. Same data type and collation on both sides (mismatches prevent index use)
3. Multi-tenant: use compound join indexes `(tenant_id, foreign_key)`

---

## Index Maintenance

### Update Statistics and Rebuild

```sql
ANALYZE TABLE orders;  -- Refresh cardinality estimates

-- Rebuild (locks table — maintenance window only):
OPTIMIZE TABLE orders;
-- Online alternative:
ALTER TABLE orders ENGINE=InnoDB;
```

### Find Unused Indexes

```sql
SELECT s.TABLE_SCHEMA, s.TABLE_NAME, s.INDEX_NAME
FROM information_schema.STATISTICS s
LEFT JOIN performance_schema.table_io_waits_summary_by_index_usage w
  ON s.TABLE_SCHEMA = w.OBJECT_SCHEMA
  AND s.TABLE_NAME = w.OBJECT_NAME
  AND s.INDEX_NAME = w.INDEX_NAME
WHERE w.INDEX_NAME IS NULL
  AND s.INDEX_NAME != 'PRIMARY'
  AND s.TABLE_SCHEMA NOT IN ('mysql', 'sys', 'performance_schema');
```

### Find Redundant Indexes

```sql
-- idx_a(a) is redundant if idx_ab(a, b) exists (leftmost prefix overlap)
SELECT t.TABLE_SCHEMA, t.TABLE_NAME,
       t.INDEX_NAME AS redundant_index, t.COLUMNS AS redundant_columns,
       t2.INDEX_NAME AS covering_index, t2.COLUMNS AS covering_columns
FROM (
  SELECT TABLE_SCHEMA, TABLE_NAME, INDEX_NAME,
         GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) AS COLUMNS
  FROM information_schema.STATISTICS GROUP BY TABLE_SCHEMA, TABLE_NAME, INDEX_NAME
) t
JOIN (
  SELECT TABLE_SCHEMA, TABLE_NAME, INDEX_NAME,
         GROUP_CONCAT(COLUMN_NAME ORDER BY SEQ_IN_INDEX) AS COLUMNS
  FROM information_schema.STATISTICS GROUP BY TABLE_SCHEMA, TABLE_NAME, INDEX_NAME
) t2 ON t.TABLE_SCHEMA = t2.TABLE_SCHEMA AND t.TABLE_NAME = t2.TABLE_NAME
  AND t.INDEX_NAME != t2.INDEX_NAME AND t2.COLUMNS LIKE CONCAT(t.COLUMNS, ',%');
```

---

## Index Anti-Patterns

### 1. Over-Indexing (Write Amplification)

```sql
-- BAD: 8 single-column indexes — each INSERT updates ALL 8
-- BETTER: 2-3 targeted compound indexes based on actual query patterns
ALTER TABLE orders ADD INDEX idx_tenant_status_created (tenant_id, status, created_at);
ALTER TABLE orders ADD INDEX idx_tenant_customer (tenant_id, customer_id);
```

### 2. Low-Cardinality Solo Indexes

```sql
-- BAD: Boolean alone — 50% selectivity, optimizer may ignore
ALTER TABLE orders ADD INDEX idx_active (is_active);
-- BETTER: Lead with high-cardinality column
ALTER TABLE orders ADD INDEX idx_tenant_active (tenant_id, is_active);
```

### 3. Redundant Indexes

`idx_a(a)` is redundant when `idx_ab(a, b)` exists. Drop `idx_a`.

### 4. Missing Join Indexes

`type=ALL` on joined table in EXPLAIN = missing join index. Add it.

### 5. Indexing Every Column Individually

```sql
-- BAD: Three single-column indexes; MySQL picks ONE or does slow index_merge
ALTER TABLE orders ADD INDEX (tenant_id);
ALTER TABLE orders ADD INDEX (status);
ALTER TABLE orders ADD INDEX (created_at);
-- GOOD: One compound index
ALTER TABLE orders ADD INDEX (tenant_id, status, created_at);
```

### 6. Functions Defeating Indexes

```sql
-- BAD: Function on column prevents index use
SELECT * FROM users WHERE YEAR(created_at) = 2024;
-- FIX: Range instead
SELECT * FROM users WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01';

-- BAD: Implicit type conversion (phone is VARCHAR, literal is INT)
SELECT * FROM users WHERE phone = 5551234;
-- FIX: Correct type
SELECT * FROM users WHERE phone = '5551234';

-- 8.0.13+ alternative: functional index
ALTER TABLE users ADD INDEX ((YEAR(created_at)));
```

---

## Quick Decision Guide

```
Optimize a SELECT?
├─ EXPLAIN first
│  ├─ type=ALL → Add index (WHERE, JOIN, ORDER BY columns)
│  ├─ Using filesort → Apply ESR rule
│  └─ Using temporary → GROUP BY must match index prefix
├─ New index design?
│  ├─ ESR column ordering from query pattern
│  ├─ Check existing indexes to extend
│  └─ Verify with EXPLAIN + EXPLAIN ANALYZE
└─ Review existing indexes?
   ├─ Unused → performance_schema query
   ├─ Redundant → leftmost prefix overlap
   └─ >5-6 per table → audit for consolidation
```

---

*Reference document for mysql-best-practices skill.*
