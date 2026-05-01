---
name: postgresql-performance
description: PostgreSQL query performance and storage internals sourced from "Introduction
  to PostgreSQL for the Data Professional" (Booz & Fritchey). Covers EXPLAIN ANALYZE
  (reading node types, costs, buffers), all index types (B-tree, GIN, GiST, BRIN,
  partial, functional, covering, composite), MVCC internals, VACUUM/ANALYZE configuration,
  work_mem tuning, and slow query diagnosis. Companion to postgresql-fundamentals
  and postgresql-administration.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# PostgreSQL Performance
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- PostgreSQL query performance and storage internals sourced from "Introduction to PostgreSQL for the Data Professional" (Booz & Fritchey). Covers EXPLAIN ANALYZE (reading node types, costs, buffers), all index types (B-tree, GIN, GiST, BRIN, partial, functional, covering, composite), MVCC internals, VACUUM/ANALYZE configuration, work_mem tuning, and slow query diagnosis. Companion to postgresql-fundamentals and postgresql-administration.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `postgresql-performance` or would be better handled by a more specific companion skill.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Performance | Slow-query diagnosis and tuning report | Markdown doc covering EXPLAIN ANALYZE, index, and tuning changes | `docs/data/postgres-tuning-2026-04-16.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## EXPLAIN — Reading Query Plans

Always use `EXPLAIN (ANALYZE, BUFFERS)` to see both estimated and actual costs.

```sql
-- Estimated only (safe, does not execute)
EXPLAIN SELECT * FROM orders WHERE customer_id = 42;

-- Actual execution (runs the query)
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM orders WHERE customer_id = 42;

-- Full output with format
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT ...;

-- Verbose (includes column-level output)
EXPLAIN (ANALYZE, BUFFERS, VERBOSE) SELECT ...;
```

### Reading the Output

```
Nested Loop  (cost=0.43..16.49 rows=3 width=120)
             (actual time=0.125..0.432 rows=3 loops=1)
  Buffers: shared hit=12 read=2
  ->  Index Scan using orders_customer_idx on orders
        (cost=0.43..8.45 rows=3 width=120)
        (actual time=0.115..0.210 rows=3 loops=1)
        Index Cond: (customer_id = 42)
```

| Field | Meaning |
|---|---|
| `cost=start..total` | Planner's estimated cost (arbitrary units) |
| `rows=N` | Planner's estimated row count |
| `actual time=first..last` | Real milliseconds to first/last row |
| `actual rows=N` | Real row count returned |
| `loops=N` | How many times this node ran |
| `shared hit=N` | Pages found in buffer cache |
| `shared read=N` | Pages read from disk |

**Key signals:**
- `rows` estimate vs `actual rows` wildly different → stale statistics → run `ANALYZE`
- `shared read` high → disk I/O bound → add RAM or index
- `loops` × `actual time` = total node time

### Primary Node Types

| Node | Meaning |
|---|---|
| `Seq Scan` | Full table scan — fine for small tables or large % of rows |
| `Index Scan` | Uses index, random I/O to fetch heap rows |
| `Index Only Scan` | Covers query entirely from index — no heap access |
| `Bitmap Index Scan` | Collects matching TIDs, then fetches heap in order |
| `Nested Loop` | For each outer row, probe inner — good for small sets |
| `Hash Join` | Build hash table, probe — good for larger sets |
| `Merge Join` | Sorted inputs — good when both sides already sorted |
| `Sort` | Explicit sort — check `work_mem` if spilling to disk |
| `Hash` | Hashing phase of Hash Join |

### When Sorts Spill to Disk

```
Sort  (cost=...) (actual time=...) (actual rows=...) (loops=1)
  Sort Key: created_at
  Sort Method: external merge  Disk: 48280kB    ← spilling!
```

Fix: increase `work_mem` for the session or globally:

```sql
SET work_mem = '256MB';   -- session-level
-- or in postgresql.conf for all sessions
work_mem = 64MB
```

## Auto EXPLAIN — Log Slow Plans

```sql
-- postgresql.conf or per-session
LOAD 'auto_explain';
SET auto_explain.log_min_duration = 1000;  -- log plans > 1s
SET auto_explain.log_analyze = on;
SET auto_explain.log_buffers = on;
```

## Indexes

### B-tree (Default)

Best for: equality (`=`), range (`<`, `>`, `BETWEEN`), `ORDER BY`, `LIKE 'prefix%'`.

```sql
-- Single column
CREATE INDEX orders_customer_idx ON orders (customer_id);

-- Composite (column order matters: put equality columns first)
CREATE INDEX orders_customer_status_idx ON orders (customer_id, status);

-- Covering index (avoid heap access entirely)
CREATE INDEX orders_covering_idx ON orders (customer_id)
    INCLUDE (total, created_at);

-- Descending
CREATE INDEX events_created_desc ON events (created_at DESC);

-- UNIQUE
CREATE UNIQUE INDEX users_email_uniq ON users (lower(email));
```

### Partial Index

Index only a subset of rows — smaller, faster, lower maintenance cost.

```sql
-- Only index pending orders (WHERE clause on index matches query)
CREATE INDEX orders_pending_idx ON orders (created_at)
    WHERE status = 'pending';

-- Query must have matching WHERE to use index
SELECT * FROM orders WHERE status = 'pending' ORDER BY created_at;

-- Partial unique (email unique only for active accounts)
CREATE UNIQUE INDEX users_active_email ON users (email) WHERE deleted_at IS NULL;
```

### Functional (Expression) Index

Index the result of a function or expression.

```sql
-- Case-insensitive email lookup
CREATE INDEX users_lower_email ON users (lower(email));

-- Used by:
SELECT * FROM users WHERE lower(email) = lower('User@Example.COM');

-- Index computed value
CREATE INDEX orders_year_idx ON orders (EXTRACT(YEAR FROM created_at));
```

### GIN — Generalised Inverted Index

Best for: JSONB containment, array operators, full-text search, pg_trgm.

```sql
CREATE INDEX products_tags_gin ON products USING GIN (tags);
CREATE INDEX configs_payload_gin ON configs USING GIN (payload);
CREATE INDEX articles_search_gin ON articles USING GIN (search_vector);
CREATE INDEX users_email_trgm ON users USING GIN (email gin_trgm_ops);
```

### GiST — Generalised Search Tree

Best for: geometric types, IP ranges (`inet`), range types, PostGIS geometry.

```sql
CREATE INDEX locations_geom ON locations USING GIST (geom);
CREATE INDEX bookings_period ON bookings USING GIST (daterange(start_date, end_date));
CREATE INDEX ip_log_addr ON access_log USING GIST (ip_address inet_ops);
```

### BRIN — Block Range Index

Best for: very large tables with naturally ordered data (time-series, append-only logs). Tiny size, fast build, coarse filtering.

```sql
-- Only useful when physical order correlates with query column
CREATE INDEX events_created_brin ON events USING BRIN (created_at);
```

### Index Maintenance

```sql
-- Check index usage (low idx_scan = unused index)
SELECT indexrelname, idx_scan, pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan;

-- Find missing indexes (sequential scans on large tables)
SELECT relname, seq_scan, seq_tup_read, idx_scan
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC;

-- Rebuild bloated index (online — no lock)
REINDEX INDEX CONCURRENTLY orders_customer_idx;

-- Rebuild all indexes on a table (online)
REINDEX TABLE CONCURRENTLY orders;
```

### B-tree Deduplication (PostgreSQL 13+)

Automatically enabled. Reduces index size for columns with many duplicate values (e.g., `status`, `country`). No action needed.

## MVCC — Multiversion Concurrency Control

PostgreSQL never overwrites rows in place. Every UPDATE writes a new row version (tuple); old versions remain until VACUUM removes them.

| Operation | What PostgreSQL Does |
|---|---|
| `INSERT` | Writes new tuple with `xmin = current_txn` |
| `UPDATE` | Marks old tuple as dead (`xmax = current_txn`), writes new tuple |
| `DELETE` | Marks tuple dead (`xmax = current_txn`) |
| `SELECT` | Sees only tuples where `xmin ≤ snapshot` and `xmax` not committed |

**Benefits:**
- Readers never block writers; writers never block readers
- Serialisable isolation without locking

**Cost:**
- Dead tuples accumulate → table bloat → VACUUM required

## VACUUM and ANALYZE

### VACUUM

Reclaims space from dead tuples. `VACUUM` marks space as reusable. `VACUUM FULL` rewrites the table (takes exclusive lock — avoid in production unless essential).

```sql
-- Standard VACUUM (online, no lock)
VACUUM orders;

-- With statistics update
VACUUM ANALYZE orders;

-- Verbose output
VACUUM VERBOSE ANALYZE orders;

-- Check autovacuum status per table
SELECT relname, last_vacuum, last_autovacuum, last_analyze, last_autoanalyze,
       n_dead_tup, n_live_tup
FROM pg_stat_user_tables ORDER BY n_dead_tup DESC;

-- Check bloat (dead tuples as percentage)
SELECT relname,
       n_dead_tup,
       n_live_tup,
       ROUND(n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0) * 100, 2) AS dead_pct
FROM pg_stat_user_tables
WHERE n_live_tup > 0
ORDER BY dead_pct DESC;
```

### Autovacuum Tuning

```ini
# postgresql.conf — lower thresholds for high-churn tables
autovacuum_vacuum_scale_factor = 0.05     # 5% dead tuples (default 20%)
autovacuum_analyze_scale_factor = 0.02    # 2% new rows (default 10%)
autovacuum_vacuum_cost_delay = 2ms        # less throttling

# Per-table override (storage parameters)
ALTER TABLE orders SET (
    autovacuum_vacuum_scale_factor = 0.01,
    autovacuum_vacuum_threshold = 100
);
```

### ANALYZE

Updates planner statistics. Runs automatically via autovacuum but run manually after bulk loads.

```sql
ANALYZE orders;                    -- one table
ANALYZE;                           -- entire database
ANALYZE VERBOSE;                   -- with row counts
```

### Fill Factor

Pre-allocate space on each page for in-place HOT (Heap-Only Tuple) updates — reduces index updates.

```sql
-- 70% fill factor = reserve 30% for updates
CREATE TABLE orders (...) WITH (fillfactor = 70);
ALTER TABLE orders SET (fillfactor = 70);
```

## Query-Level Tuning

### Statistics Target

More statistics = better estimates for skewed data:

```sql
-- Default is 100; increase for columns with high cardinality
ALTER TABLE orders ALTER COLUMN customer_id SET STATISTICS 500;
ANALYZE orders;
```

### Random Page Cost

Tell the planner storage speed. For SSD:

```ini
random_page_cost = 1.1   # SSD (default 4.0 is for HDD)
effective_cache_size = 12GB  # 75% of RAM — helps planner choose index scans
```

### Planner Hints via pg_hint_plan

```sql
CREATE EXTENSION pg_hint_plan;

/*+ IndexScan(orders orders_customer_idx) */
SELECT * FROM orders WHERE customer_id = 42;

/*+ SeqScan(orders) */
SELECT * FROM orders WHERE status = 'pending';
```

## pg_stat_statements — Query Analytics

```sql
CREATE EXTENSION pg_stat_statements;

-- Top queries by total time
SELECT query, calls, total_exec_time, mean_exec_time, rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC LIMIT 20;

-- Worst average time
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC LIMIT 20;

-- Reset statistics
SELECT pg_stat_statements_reset();
```

## Anti-Patterns

- Running `EXPLAIN` without `ANALYZE` then trusting cost estimates — costs are guesses
- `VACUUM FULL` in production — acquires exclusive lock, consider `pg_repack` instead
- Composite index with most-selective column last — put equality columns first
- Index on low-cardinality column without partial condition — B-tree useless for booleans
- Ignoring `actual rows` vs estimated `rows` mismatch — indicates stale stats
- Leaving `work_mem` at default 4MB for complex queries — causes disk spills
- Creating GIN index on small JSONB tables — overhead exceeds benefit