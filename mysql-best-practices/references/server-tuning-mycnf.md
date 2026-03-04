# MySQL Server Tuning and my.cnf Configuration Reference

> Sources: "Efficient MySQL Performance" (Nichter, 2022), "Mastering MySQL Administration" (Kumar et al., 2024)

---

## Philosophy: Don't Tune Randomly

**The single most important principle:** optimize queries and indexes, NOT server variables.

- MySQL defaults are well-tuned by decades of expert optimization across millions of deployments
- "MySQL tuning is laboratory work" -- only experts should modify most variables, and only with benchmarks to prove the change helps
- Changing random variables without measurement is cargo-cult tuning and often makes things worse
- **innodb_buffer_pool_size is THE single most important server variable** -- if you tune only one thing, tune this
- After buffer pool sizing, your time is 100x better spent on query optimization than server tuning
- Use `innodb_dedicated_server=ON` (MySQL 8.0.14+) to auto-configure the big three: buffer pool, redo log, flush method

---

## Critical Server Variables

### InnoDB Storage Engine

| Variable | Default | Recommendation | Notes |
|---|---|---|---|
| `innodb_buffer_pool_size` | 128MB | **70-80% of server RAM** | THE most critical variable. Caches data + indexes in memory. Undersizing causes disk reads on every query. |
| `innodb_buffer_pool_instances` | 8 | 8-24 | Reduces contention on buffer pool mutex. Use 1 instance per GB of buffer pool (up to 24). Only matters when buffer pool > 1GB. |
| `innodb_redo_log_capacity` | 100MB | 1-4GB | **MySQL 8.0.30+ only.** Replaces `innodb_log_file_size * innodb_log_files_in_group`. Controls total redo log space. Larger = better write throughput but longer crash recovery. |
| `innodb_log_file_size` | 48MB | 512MB-1GB | **Pre-8.0.30 only.** Size of each redo log file. Multiply by `innodb_log_files_in_group` for total redo capacity. |
| `innodb_log_files_in_group` | 2 | 2 | **Pre-8.0.30 only.** Number of redo log files. Total redo = this * `innodb_log_file_size`. |
| `innodb_log_buffer_size` | 16MB | 16-48MB | In-memory buffer for redo log writes. Increase if `Innodb_log_waits > 0`. Rarely needs tuning. |
| `innodb_flush_log_at_trx_commit` | 1 | **1** (ACID) | 1 = flush to disk every commit (safest). 2 = flush to OS cache (1s data loss risk). 0 = flush every second (fastest, up to 1s data loss). Never use 0 in production. |
| `innodb_dedicated_server` | OFF | **ON** (if dedicated) | MySQL 8.0.14+. Auto-configures buffer pool size, redo log capacity, and flush method based on detected RAM. Use this instead of manual tuning when MySQL owns the whole server. |
| `innodb_file_per_table` | ON | **ON** | Each table gets its own .ibd file. Enables reclaiming space after DROP/TRUNCATE. OFF stores everything in ibdata1 which never shrinks. |
| `innodb_doublewrite` | ON | **ON** | Prevents torn-page corruption during crash. 2-5% write overhead. Never disable unless filesystem guarantees atomic writes (ZFS, some SSDs). |
| `innodb_flush_method` | fsync | **O_DIRECT** (Linux) | O_DIRECT bypasses OS file cache, avoids double-buffering with buffer pool. Use on Linux with fast local storage. Leave default on Windows or network storage. |
| `innodb_lock_wait_timeout` | 50 | 50 (default is fine) | Seconds a transaction waits for a **row lock** before aborting. Per-row, not per-query. Lower (10-30s) for interactive apps to fail fast. |

### Connection and Thread Management

| Variable | Default | Recommendation | Notes |
|---|---|---|---|
| `max_connections` | 151 | **500-1000** (production) | Set based on actual peak concurrent connections + headroom. Each idle connection uses ~1MB RAM. Use connection pooling to keep active connections low. |
| `wait_timeout` | 28800 | 300-600 | Seconds before closing an idle connection. 8 hours is too long for web apps. 5-10 minutes prevents connection pile-up. |
| `interactive_timeout` | 28800 | 300-600 | Same as wait_timeout but for interactive clients (mysql CLI). |

### Per-Session Buffers (Caution: Multiplied by Connections)

| Variable | Default | Recommendation | Notes |
|---|---|---|---|
| `sort_buffer_size` | 256KB | 256KB-2MB | Allocated per-session for ORDER BY. Larger is NOT always better -- oversizing wastes RAM (multiplied by max_connections). Only increase if `Sort_merge_passes` is high. |
| `join_buffer_size` | 256KB | 256KB-4MB | Used for joins without indexes (block nested loop). Fix missing indexes first. Increase only for unavoidable full-table joins. |
| `read_buffer_size` | 128KB | 128KB-256KB | Sequential scan buffer. Rarely needs tuning. Fix queries doing full scans instead. |

### Transaction Behavior

| Variable | Default | Recommendation | Notes |
|---|---|---|---|
| `autocommit` | ON | **ON** | Default ON means each statement is its own transaction. Application frameworks manage BEGIN/COMMIT explicitly. Never set OFF globally -- causes accidental long-running transactions. |
| `transaction_isolation` | REPEATABLE-READ | **READ-COMMITTED** (SaaS) | READ-COMMITTED reduces gap locking, improves concurrency for web apps. REPEATABLE-READ is safer for complex transactions. Change at session level if needed. |

### Slow Query Logging

| Variable | Default | Recommendation | Notes |
|---|---|---|---|
| `slow_query_log` | OFF | **ON** | Always enable in production. Zero meaningful performance impact. |
| `long_query_time` | 10 | **1** (or 0.5) | Seconds. Default 10s misses most problematic queries. Set to 1s to catch slow queries early. For aggressive monitoring, use 0.1-0.5. |
| `log_slow_extra` | OFF | **ON** | MySQL 8.0.14+. Logs additional fields: Rows_examined, Query_plan, etc. Essential for diagnosis. |
| `log_queries_not_using_indexes` | OFF | **ON** | Logs queries that perform full table scans. Helps find missing indexes. Can be noisy on small tables -- combine with `min_examined_row_limit`. |
| `min_examined_row_limit` | 0 | 1000 | Used with `log_queries_not_using_indexes` to suppress logging for small-table scans. |

---

## 11 Metric Spectrums (Nichter, Chapter 6)

These spectrums provide a complete picture of MySQL server health.

### 1. Response Time

The most important metric. Measure query response time at the application level. Use slow query log and Performance Schema `events_statements_summary_by_digest` for per-query latency percentiles (P95, P99).

### 2. Rate (QPS)

Monitor `Questions` (client-issued), `Com_select`, `Com_insert`, `Com_update`, `Com_delete`. Establish a baseline. Sudden drops or spikes indicate problems. Calculate per-second rates over 1-minute intervals.

### 3. Utilization

- **`Threads_running`** -- CRITICAL. Number of threads actively executing queries. Should be low (< CPU cores). If consistently > 2x cores, the server is overloaded.
- **`Threads_connected`** -- Total connected threads (active + idle). High values with low `Threads_running` = connection pool too large.

### 4. Errors

- `Connection_errors_max_connections` -- Hitting max_connections limit. Increase or use pooling.
- `Connection_errors_internal` -- Server-side errors. Investigate immediately.
- `Aborted_connects` -- Failed authentication or protocol errors.
- `Aborted_clients` -- Clients disconnected without proper close (timeout, crash).

### 5. Access Patterns

- `Handler_read_rnd_next` -- Full table scans. High values = missing indexes.
- `Handler_read_key` -- Index lookups. Should be the dominant handler.
- `Sort_merge_passes` -- If > 0, sort_buffer_size may be too small or query returns too many rows.
- `Created_tmp_disk_tables` -- Temp tables spilling to disk. Check `tmp_table_size` / `max_heap_table_size` or optimize queries.

### 6. InnoDB Buffer Pool

- `Innodb_buffer_pool_pages_total` -- Total pages in buffer pool.
- `Innodb_buffer_pool_pages_data` -- Pages containing data.
- `Innodb_buffer_pool_pages_free` -- Free pages. Zero = buffer pool full (not necessarily bad if hit rate is high).
- `Innodb_buffer_pool_pages_dirty` -- Modified pages not yet flushed.
- **Hit rate formula:** `read_requests / (read_requests + reads) * 100` -- Must be > 99%.
- `Innodb_buffer_pool_wait_free` -- **Must be 0.** Any value > 0 means buffer pool is too small.

### 7. InnoDB Data I/O

- `Innodb_data_reads` -- Physical read operations from disk.
- `Innodb_data_writes` -- Physical write operations to disk.
- High data_reads with good buffer pool hit rate = working set changed or cold start.

### 8. InnoDB Row Operations

- `Innodb_rows_read` -- Total rows read (including scanned-but-not-returned rows).
- `Innodb_rows_inserted`, `Innodb_rows_updated`, `Innodb_rows_deleted` -- DML operation counts.
- Large `rows_read` relative to actual result sets = inefficient queries scanning too many rows.

### 9. InnoDB Locking

- **`Innodb_row_lock_waits`** -- Should be near zero. Any significant value = lock contention.
- **`Innodb_row_lock_time`** -- Total ms spent waiting for row locks. Should be near zero.
- High values indicate long-running transactions, missing indexes on UPDATE/DELETE, or deadlock-prone patterns.

### 10. InnoDB Redo Log

- **`Innodb_log_waits`** -- Should be 0. Any value > 0 means redo log buffer is too small. Increase `innodb_log_buffer_size`.
- **`Innodb_os_log_pending_writes`** -- Should be 0. Pending = disk cannot keep up with redo writes. Check storage performance.
- **`Innodb_os_log_pending_fsyncs`** -- Should be 0. Pending fsyncs = storage bottleneck.

### 11. InnoDB Page Flushing

- Adaptive flushing automatically adjusts flush rate based on redo log fill level.
- Monitor `Innodb_buffer_pool_pages_dirty` -- should stay well below total pages.
- Flushing spikes can cause latency spikes. Ensure redo log capacity is large enough to allow smooth flushing.

---

## Key Performance Indicators (KPIs)

Focus monitoring dashboards on these four KPIs:

1. **Response time** -- P95/P99 query latency. The metric users feel.
2. **Errors** -- Connection errors, aborted connections, query errors. Should trend to zero.
3. **Throughput (QPS)** -- Queries per second. Establishes baseline and detects anomalies.
4. **Utilization** -- `Threads_running` relative to CPU cores. The server saturation signal.

---

## Buffer Pool Deep Dive

The buffer pool is InnoDB's most critical data structure. It caches table data and index pages in RAM.

**Hit Rate Calculation:**

```
Hit Rate = Innodb_buffer_pool_read_requests /
           (Innodb_buffer_pool_read_requests + Innodb_buffer_pool_reads) * 100
```

| Hit Rate | Status | Action |
|---|---|---|
| > 99% | Healthy | Working set fits in memory |
| 95-99% | Warning | Monitor trends, consider increase |
| < 95% | Critical | Working set exceeds buffer pool, expect degraded performance |

**Key rules:**

- `Innodb_buffer_pool_wait_free > 0` = buffer pool definitively too small. Increase immediately.
- Size to 70-80% of total RAM on a dedicated MySQL server.
- On shared servers, calculate: total RAM - OS needs (~1GB) - per-connection buffers (max_connections * ~1MB) - other processes. Allocate 60-70% of the remainder.
- After resizing, allow 10-15 minutes for warmup before measuring hit rate.

---

## Complete my.cnf Templates

### Template 1: Small/Mid Database (Dedicated Server, Auto-Tuned)

```ini
# my.cnf -- Small/Mid Production (MySQL 8.0.30+)
# For dedicated MySQL servers with 8-32GB RAM
# innodb_dedicated_server handles buffer pool, redo log, flush method

[mysqld]
# --- Auto-Tuning (handles the big three) ---
innodb_dedicated_server          = ON

# --- InnoDB Core ---
innodb_file_per_table            = ON
innodb_doublewrite               = ON
innodb_flush_log_at_trx_commit   = 1
innodb_log_buffer_size           = 32M
innodb_buffer_pool_instances     = 8

# --- Connections ---
max_connections                  = 500
wait_timeout                     = 300
interactive_timeout              = 300

# --- Transaction ---
transaction_isolation            = READ-COMMITTED
autocommit                       = ON
innodb_lock_wait_timeout         = 30

# --- Slow Query Logging ---
slow_query_log                   = ON
long_query_time                  = 1
log_slow_extra                   = ON
log_queries_not_using_indexes    = ON
min_examined_row_limit           = 1000

# --- Per-Session Buffers (conservative) ---
sort_buffer_size                 = 512K
join_buffer_size                 = 512K
read_buffer_size                 = 256K

# --- Character Set ---
character_set_server             = utf8mb4
collation_server                 = utf8mb4_0900_ai_ci

# --- Binary Logging (replication/PITR) ---
server_id                        = 1
log_bin                          = mysql-bin
binlog_expire_logs_seconds       = 604800
binlog_format                    = ROW
```

### Template 2: Large Production Database (Manual Tuning)

```ini
# my.cnf -- Large Production (MySQL 8.0.30+)
# For dedicated MySQL servers with 64-256GB RAM
# Manual tuning for maximum control

[mysqld]
# --- InnoDB Buffer Pool ---
# 70-80% of total RAM. Example: 128GB server -> 96GB buffer pool
innodb_buffer_pool_size          = 96G
innodb_buffer_pool_instances     = 24

# --- InnoDB Redo Log (8.0.30+) ---
# Larger = better write throughput, longer crash recovery
innodb_redo_log_capacity         = 4G
innodb_log_buffer_size           = 48M

# --- InnoDB Durability ---
innodb_flush_log_at_trx_commit   = 1
innodb_doublewrite               = ON
innodb_file_per_table            = ON
innodb_flush_method              = O_DIRECT

# --- Connections ---
max_connections                  = 1000
wait_timeout                     = 300
interactive_timeout              = 300

# --- Transaction ---
transaction_isolation            = READ-COMMITTED
autocommit                       = ON
innodb_lock_wait_timeout         = 30

# --- Slow Query Logging ---
slow_query_log                   = ON
long_query_time                  = 0.5
log_slow_extra                   = ON
log_queries_not_using_indexes    = ON
min_examined_row_limit           = 1000

# --- Per-Session Buffers ---
sort_buffer_size                 = 2M
join_buffer_size                 = 2M
read_buffer_size                 = 256K

# --- Character Set ---
character_set_server             = utf8mb4
collation_server                 = utf8mb4_0900_ai_ci

# --- Binary Logging ---
server_id                        = 1
log_bin                          = mysql-bin
binlog_expire_logs_seconds       = 604800
binlog_format                    = ROW
sync_binlog                      = 1

# --- Performance Schema (enabled by default in 8.0) ---
performance_schema               = ON
```

---

## Monitoring Queries

```sql
-- Buffer pool hit rate (should be > 99%)
SELECT
  ROUND(
    (1 - (
      (SELECT VARIABLE_VALUE FROM performance_schema.global_status
       WHERE VARIABLE_NAME = 'Innodb_buffer_pool_reads') /
      (SELECT VARIABLE_VALUE FROM performance_schema.global_status
       WHERE VARIABLE_NAME = 'Innodb_buffer_pool_read_requests')
    )) * 100, 2
  ) AS buffer_pool_hit_rate_pct;

-- Thread utilization (Threads_running should be < CPU cores)
SELECT * FROM performance_schema.global_status
WHERE VARIABLE_NAME IN (
  'Threads_running', 'Threads_connected', 'Threads_created', 'Max_used_connections'
);

-- Lock contention (row_lock_waits and row_lock_time should be near zero)
SELECT * FROM performance_schema.global_status
WHERE VARIABLE_NAME IN (
  'Innodb_row_lock_waits', 'Innodb_row_lock_time',
  'Innodb_row_lock_time_avg', 'Innodb_deadlocks'
);

-- Connection status and errors
SELECT * FROM performance_schema.global_status
WHERE VARIABLE_NAME LIKE 'Connection_errors%'
   OR VARIABLE_NAME LIKE 'Aborted%'
   OR VARIABLE_NAME = 'Max_used_connections';

-- Redo log health (log_waits should be 0)
SELECT * FROM performance_schema.global_status
WHERE VARIABLE_NAME IN (
  'Innodb_log_waits', 'Innodb_os_log_pending_writes',
  'Innodb_os_log_pending_fsyncs'
);

-- Top queries by total latency (Performance Schema)
SELECT
  DIGEST_TEXT,
  COUNT_STAR AS exec_count,
  ROUND(SUM_TIMER_WAIT / 1e12, 2) AS total_latency_sec,
  ROUND(AVG_TIMER_WAIT / 1e12, 4) AS avg_latency_sec,
  SUM_ROWS_EXAMINED,
  SUM_ROWS_SENT
FROM performance_schema.events_statements_summary_by_digest
ORDER BY SUM_TIMER_WAIT DESC
LIMIT 10;

-- Table maintenance
ANALYZE TABLE your_table;          -- Update index statistics
OPTIMIZE TABLE your_table;         -- Reclaim space (locks table, use pt-online-schema-change instead)
CHECK TABLE your_table;            -- Verify table integrity
```

---

## Monitoring Tools

| Tool | Purpose | When to Use |
|---|---|---|
| **pt-query-digest** (Percona Toolkit) | Analyze slow query log, identify top queries by response time | First tool for query optimization. Parse slow log weekly. |
| **Percona Monitoring and Management (PMM)** | Full MySQL dashboard with all 11 metric spectrums | Production monitoring. Free, open-source. |
| **Performance Schema** | Built-in instrumentation tables | Always-on metrics. Query `events_statements_summary_by_digest` for query analysis. |
| **SHOW ENGINE INNODB STATUS** | InnoDB internals snapshot (locks, buffer pool, redo log, transactions) | Debugging lock contention, deadlocks, or InnoDB performance issues. |
| **mysqldumpslow** | Summarize slow query log (ships with MySQL) | Quick slow log analysis when pt-query-digest is unavailable. |
| **EXPLAIN / EXPLAIN ANALYZE** | Query execution plan | Before and after every query optimization. Non-negotiable. |

---

## Do NOT Tune These (Common Mistakes)

| Variable | Why Not |
|---|---|
| `query_cache_*` | **Removed in MySQL 8.0.** Was a scalability bottleneck. If you see advice about query cache, the source is outdated. |
| `key_buffer_size` | MyISAM only. InnoDB does not use it. Default 8MB is fine unless you have MyISAM system tables (rare in 8.0). |
| `thread_cache_size` | Auto-tuned in MySQL 8.0. Manual values are ignored or counterproductive. |
| `innodb_io_capacity` | Default (200) works for most SSDs. Only experts with benchmarks should change this. Wrong values cause flushing storms or stalls. |
| `innodb_io_capacity_max` | Same as above. Leave at default (2000) unless you have proven your storage can handle more. |
| `table_open_cache` | Auto-sized in 8.0. Rarely needs tuning. Oversizing wastes file descriptors. |
| `innodb_thread_concurrency` | Default 0 (unlimited) lets InnoDB manage threads adaptively. Manual limits usually reduce throughput. |
| `tmp_table_size` / `max_heap_table_size` | Increasing these just delays the spill to disk. Fix the queries creating large temp tables instead. |

---

## Quick Decision Checklist

1. Is MySQL on a dedicated server? Set `innodb_dedicated_server=ON` and stop tuning.
2. Shared server? Set `innodb_buffer_pool_size` to 60-70% of available RAM.
3. Enable slow query log with `long_query_time=1`.
4. Set `transaction_isolation=READ-COMMITTED` for SaaS workloads.
5. Run `pt-query-digest` on the slow log weekly.
6. Monitor `Threads_running` -- if consistently > CPU cores, optimize queries first.
7. Check buffer pool hit rate -- if < 99%, investigate before adding RAM.
8. Everything else: leave at defaults until benchmarks prove a change helps.
