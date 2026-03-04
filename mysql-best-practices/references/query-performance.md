# MySQL Query Performance Reference

Based on "Efficient MySQL Performance" by Daniel Nichter (O'Reilly, 2022).

---

## Query Response Time as North Star

Performance means one thing: **query response time**. It is the only metric end users
experience. Every other metric (CPU, IOPS, connections) is indirect.

Two categories of optimization:

| Category | What You Touch | Examples |
|----------|---------------|----------|
| **Direct** | Queries and indexes | Rewrite SQL, add covering index, remove `SELECT *` |
| **Indirect** | Data and access patterns | Partition old data, add caching layer, connection pooling |

Always start with direct optimization. Indirect optimization matters when queries
are already efficient but workload characteristics cause problems.

---

## Query Metric Sources

### Slow Query Log

The slow query log is the primary source for query metrics. Configure it to capture
**all** queries in development, or queries above a threshold in production.

```sql
-- Development: capture every query
SET GLOBAL long_query_time = 0;
SET GLOBAL slow_query_log = 'ON';

-- Production: capture queries over 1 second
SET GLOBAL long_query_time = 1;
SET GLOBAL slow_query_log = 'ON';

-- MySQL 8.0.14+: capture extra metrics (bytes sent, tmp tables, etc.)
SET GLOBAL log_slow_extra = 'ON';
```

Parse the slow log with `pt-query-digest` (Percona Toolkit) or `mysqldumpslow`.

### Performance Schema

The Performance Schema aggregates query statistics in real time without log files.

```sql
-- Top 10 queries by total execution time
SELECT
    DIGEST_TEXT,
    COUNT_STAR         AS exec_count,
    ROUND(SUM_TIMER_WAIT / 1e12, 3)    AS total_time_sec,
    ROUND(AVG_TIMER_WAIT / 1e12, 3)    AS avg_time_sec,
    SUM_ROWS_EXAMINED  AS rows_examined,
    SUM_ROWS_SENT      AS rows_sent
FROM performance_schema.events_statements_summary_by_digest
ORDER BY SUM_TIMER_WAIT DESC
LIMIT 10;
```

### Query Digest

MySQL normalizes each SQL statement into a **digest**: whitespace is collapsed,
literal values are replaced with `?`, and a SHA-256 hash is computed.

```
-- These two queries produce the SAME digest:
SELECT name FROM users WHERE id = 42;
SELECT name FROM users WHERE id = 7;

-- Digest text: SELECT `name` FROM `users` WHERE `id` = ?
```

Digests let you aggregate metrics across millions of individual executions of the
same logical query.

---

## 9 Essential Query Metrics

These are the metrics that matter for every query. Collect and monitor all nine.

| # | Metric | What It Measures |
|---|--------|-----------------|
| 1 | **Query Time** | Total wall-clock time including lock time. The single most important metric. |
| 2 | **Lock Time** | Time acquiring row/metadata locks. High values signal contention. |
| 3 | **Rows Examined** | Rows MySQL read internally. Strongest indicator of index effectiveness. |
| 4 | **Rows Sent** | Rows returned to client. Compare with rows examined. |
| 5 | **Rows Affected** | Rows modified by INSERT, UPDATE, DELETE. |
| 6 | **Select Scan** | Binary (0/1). If 1, full table scan on the first table. Red flag for large tables. |
| 7 | **Select Full Join** | Joins doing full scan on joined table. Must **always be zero**. |
| 8 | **Created Tmp Disk Tables** | Temp tables spilled to disk. Slow -- check query or `tmp_table_size`. |
| 9 | **Query Count** | Execution count. A fast query run millions of times can dominate total time. |

### Interpreting Rows Examined vs Rows Sent

| Relationship | Meaning | Action |
|-------------|---------|--------|
| `rows_sent = rows_examined` (both small) | Ideal. Index precisely targets needed rows. | None needed. |
| `rows_sent < rows_examined` | Poor selectivity. MySQL reads many rows to return few. | Improve index or rewrite query. |
| `rows_examined` is large, `rows_sent = 0` | Query examines data but returns nothing. | Check WHERE conditions and index coverage. |

### Critical Alert: Select Full Join

```sql
-- Find queries with unindexed joins (select_full_join > 0)
SELECT
    DIGEST_TEXT,
    COUNT_STAR,
    SUM_SELECT_FULL_JOIN
FROM performance_schema.events_statements_summary_by_digest
WHERE SUM_SELECT_FULL_JOIN > 0
ORDER BY SUM_SELECT_FULL_JOIN DESC;
```

**If `select_full_join > 0`: stop and fix it.** Add an index on the join column
of the joined table. This is never acceptable in production.

---

## Query Load

Query load measures how much of the server's capacity a single query digest
consumes over a period of time.

```
query_load = total_query_time / clock_time
```

| Load Value | Interpretation |
|-----------|----------------|
| `< 1.0` | Query never runs concurrently. Low impact. |
| `= 1.0` | One instance always running. Moderate. |
| `> 1.0` | Multiple concurrent executions. High impact. |
| `> 10.0` | Very high. Likely causing slowdowns across the system. |

Example: A query runs 500 times in 60 seconds, averaging 200ms each.

```
total_query_time = 500 * 0.2 = 100 seconds
query_load = 100 / 60 = 1.67
```

This means, on average, 1.67 instances of this query are running at any moment.

---

## Statistics: Average vs Percentile vs Maximum

### Why Averages Lie

```
Query times (ms): 1, 1, 1, 1, 1, 1, 1, 1, 1, 5000
Average: 500.1 ms
```

The average says 500ms, but 9 out of 10 users experienced 1ms. The average is
dominated by a single outlier and misleads you about typical performance.

### Percentiles Are Better

| Percentile | Meaning |
|-----------|---------|
| P50 (median) | Half of queries are faster than this |
| P95 | 95% of queries are faster; 5% are slower |
| P99 | 99% faster; 1% slower |
| P999 | 99.9% faster; 0.1% slower |

**Use P999 for production monitoring.** At 1,000 QPS, P999 means one query per
second is this slow or worse. That is still a meaningful number of affected users.

### Maximum Matters

The maximum is the **actual worst case a real user experienced**. Do not dismiss
it as an outlier. Investigate maximums that are orders of magnitude above P999.

```sql
-- P95 and P99 from Performance Schema (approximated via histograms in 8.0.2+)
-- For precise percentiles, use pt-query-digest on the slow query log
SELECT
    DIGEST_TEXT,
    COUNT_STAR,
    ROUND(AVG_TIMER_WAIT / 1e12, 3)    AS avg_sec,
    ROUND(MAX_TIMER_WAIT / 1e12, 3)    AS max_sec,
    ROUND(QUANTILE_95 / 1e12, 3)       AS p95_sec,
    ROUND(QUANTILE_99 / 1e12, 3)       AS p99_sec
FROM performance_schema.events_statements_summary_by_digest
ORDER BY SUM_TIMER_WAIT DESC
LIMIT 10;
```

---

## Query Profiling Workflow

Follow this repeatable process for every performance investigation.

### Step 1: Enable Metrics

```sql
-- Ensure slow query log or Performance Schema is capturing data
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';
SHOW VARIABLES LIKE 'performance_schema';
```

### Step 2: Identify Top Queries by Total Time

Sort by **total execution time** (count * average), not by average time alone.
A 1ms query running 10 million times consumes more resources than a 10s query
running once.

```bash
# Using pt-query-digest
pt-query-digest /var/log/mysql/slow.log --order-by Query_time:sum --limit 10
```

### Step 3: EXPLAIN Each Top Query

```sql
EXPLAIN FORMAT=JSON
SELECT o.id, o.total, c.name
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE o.status = 'pending'
  AND o.created_at > '2024-01-01';
```

Look for:

- `type: ALL` (full table scan -- needs index)
- `type: index` (full index scan -- often improvable)
- `rows` much larger than result set (poor selectivity)
- `Using temporary; Using filesort` (may need composite index)

### Step 4: Optimize

Apply the appropriate fix: add an index, rewrite the query, or change the access
pattern. One fix at a time.

### Step 5: Verify

Re-run EXPLAIN and compare metrics before and after. Confirm rows_examined dropped.

### Step 6: Monitor

Deploy and watch query load, P999 latency, and rows_examined in production for at
least 24 hours.

---

## Access Patterns

Access patterns determine how the workload interacts with data. Even perfectly
indexed queries can perform poorly under hostile access patterns.

### Read/Write Ratio

Know whether your workload is read-heavy (>90% SELECT) or write-heavy. This
determines replication topology, caching strategy, and isolation level choices.

### Data Age: Hot vs Cold

**Hot data** is frequently accessed recent data. **Cold data** is old, rarely
queried data.

- Hot data **must fit in the InnoDB buffer pool** for acceptable performance
- Cold data should be archived or partitioned to avoid polluting the buffer pool

```sql
-- Check buffer pool usage
SELECT
    ROUND(DATA_LENGTH / 1024 / 1024, 1) AS data_mb,
    ROUND(INDEX_LENGTH / 1024 / 1024, 1) AS index_mb,
    TABLE_NAME
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'your_database'
ORDER BY DATA_LENGTH DESC
LIMIT 20;
```

### Concurrency

High concurrency without connection pooling causes MySQL to thrash. Use a
connection pool (ProxySQL, application-level pool) to limit concurrent connections
to approximately **2-4x CPU core count**.

### Working Set Size

The working set is the subset of data actively queried. If the working set exceeds
the buffer pool, performance degrades nonlinearly due to disk I/O.

---

## Performance Destabilization

### Universal Scalability Law (USL)

Throughput does not scale linearly with load. The USL models two penalties:

| Factor | Description |
|--------|-------------|
| **Contention** | Serialization points (locks, mutexes) force threads to wait |
| **Coherency** | Maintaining consistency across cores/nodes adds overhead |

Under high load, throughput **decreases**. Adding more connections past the
inflection point makes performance worse, not better.

```
Throughput
    ^
    |        /---\
    |       /     \        <-- throughput falls under high load
    |      /       \
    |     /         \
    |    /           \
    |---/             \---
    +-----------------------> Concurrency
```

### Practical Implication

If your server handles 1,000 QPS at 20ms average latency with 50 connections,
doubling connections to 100 will **not** double throughput. It may reduce it due
to lock contention and context switching.

---

## Practical Throughput Limits

Calculate the theoretical maximum throughput for a query:

```
max_qps_per_thread = 1000 / query_time_ms
total_max_qps = max_qps_per_thread * available_threads
```

| Query Time | QPS per Thread | 8 Cores | 48 Cores |
|-----------|---------------|---------|----------|
| 1 ms | 1,000 | 8,000 | 48,000 |
| 10 ms | 100 | 800 | 4,800 |
| 100 ms | 10 | 80 | 480 |
| 1,000 ms | 1 | 8 | 48 |

**Two levers to increase throughput:**

1. **Reduce query time** (better indexes, query rewrites, caching)
2. **Increase concurrency** (more cores, read replicas, sharding)

Always prefer lever 1. Reducing a query from 100ms to 10ms gives a 10x improvement
without any infrastructure changes.

---

## Optimization Anti-Patterns

### SELECT * (Never in Production)

```sql
-- BAD: fetches all columns, prevents covering indexes
SELECT * FROM orders WHERE customer_id = 42;

-- GOOD: fetch only what you need
SELECT id, total, status, created_at
FROM orders
WHERE customer_id = 42;
```

`SELECT *` wastes network bandwidth, prevents the optimizer from using covering
indexes, and breaks when columns are added or removed.

### Large OFFSET Pagination

```sql
-- BAD: MySQL reads and discards 100,000 rows
SELECT id, name FROM products ORDER BY id LIMIT 10 OFFSET 100000;

-- GOOD: keyset pagination (seek method)
SELECT id, name FROM products
WHERE id > 100000
ORDER BY id
LIMIT 10;
```

OFFSET-based pagination degrades linearly. At OFFSET 1,000,000, MySQL examines
1,000,010 rows to return 10. Keyset pagination is O(1).

### Dynamically Varying WHERE Clauses

```sql
-- BAD: each combination creates a DIFFERENT digest and plan
-- Query A
SELECT * FROM orders WHERE status = 'pending';
-- Query B
SELECT * FROM orders WHERE status = 'pending' AND region = 'US';
-- Query C
SELECT * FROM orders WHERE region = 'US';
```

Each variant produces a different query digest, making it impossible to aggregate
performance metrics. Standardize your query shapes.

### Subqueries Where JOINs Work

```sql
-- BAD: dependent subquery, executes once per outer row
SELECT name FROM customers
WHERE id IN (SELECT customer_id FROM orders WHERE total > 1000);

-- GOOD: JOIN, executed as a single operation
SELECT DISTINCT c.name
FROM customers c
JOIN orders o ON o.customer_id = c.id
WHERE o.total > 1000;
```

MySQL 8.0 can sometimes optimize subqueries into semi-joins, but explicit JOINs
give the optimizer the clearest signal.

### Unbounded Data Growth

```sql
-- BAD: audit_log grows forever, pollutes buffer pool
INSERT INTO audit_log (action, details, created_at) VALUES (...);

-- GOOD: partition by month, drop old partitions
ALTER TABLE audit_log PARTITION BY RANGE (TO_DAYS(created_at)) (
    PARTITION p2024_01 VALUES LESS THAN (TO_DAYS('2024-02-01')),
    PARTITION p2024_02 VALUES LESS THAN (TO_DAYS('2024-03-01')),
    PARTITION p_future  VALUES LESS THAN MAXVALUE
);

-- Drop data older than 12 months instantly
ALTER TABLE audit_log DROP PARTITION p2024_01;
```

### Tuning Server Variables Before Optimizing Queries

The single most common waste of time. Adjusting `innodb_buffer_pool_size` or
`thread_cache_size` before examining the actual queries is like tuning a car
engine when the driver is taking the wrong route.

**Rule:** Optimize queries and indexes first. Tune server variables only after
queries are efficient and you have evidence that a specific variable is the
bottleneck.

---

## Quick Reference: EXPLAIN Type Rankings

From best to worst access type:

| Type | Meaning | Action |
|------|---------|--------|
| `system` | Table has one row | Perfect |
| `const` | Primary key or unique index lookup | Perfect |
| `eq_ref` | One row per join (unique index) | Ideal for joins |
| `ref` | Non-unique index lookup | Good |
| `range` | Index range scan | Good for bounded queries |
| `index` | Full index scan | Review: may be improvable |
| `ALL` | Full table scan | Add an index |

---

## Summary Checklist

- [ ] Slow query log or Performance Schema enabled and collecting data
- [ ] Top queries identified by **total** time, not average
- [ ] Every top query has been EXPLAINed
- [ ] `select_full_join = 0` for all queries (no unindexed joins)
- [ ] No `SELECT *` in application queries
- [ ] Pagination uses keyset (seek) method, not OFFSET
- [ ] Hot data fits in the InnoDB buffer pool
- [ ] Connection pooling limits concurrency to 2-4x CPU cores
- [ ] P999 latency is monitored and alerted on
- [ ] Query load is tracked per digest
