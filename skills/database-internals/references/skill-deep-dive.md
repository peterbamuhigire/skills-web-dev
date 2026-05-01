# database-internals Deep Dive

This file contains the extended guidance moved out of [../SKILL.md](../SKILL.md) so the skill entrypoint stays under the repository size limit.

## Included Sections

- `2. Page Structure — The 16 KB Unit of All I/O`
- `3. Write-Ahead Log (WAL / Redo Log)`
- `4. Buffer Pool Mechanics — The Memory Manager`
- `5. MVCC — Consistent Reads Without Locking`
- `6. Transaction Isolation Levels — What Each Actually Does`
- `7. Lock Types and Interactions`
- `8. LSM Trees vs B-Trees — The Core Tradeoff`
- `9. Distributed Systems Concepts Applied to MySQL`
- `10. Index Structures Beyond B-Trees`
- `11. Write Amplification — Why SSDs Matter`
- `12. MySQL vs PostgreSQL Internals — Key Architectural Differences`
- `13. Design Rules Derived from Internals`
- `Quick-Reference: The 10 Mental Model Checklist`

## 2. Page Structure — The 16 KB Unit of All I/O

InnoDB's fundamental I/O unit is a **16 KB page** (configurable, rarely changed).
Every read and write, no matter how small, transfers a full page.

Pages use the **slotted page** format:
```
[Page Header | Cell offsets (sorted by key) --> free space <-- Cell data]
```
- Cell offsets are kept sorted for binary search.
- Actual cell data is appended in insertion order.
- Deleted rows leave garbage cells until vacuum/compaction.

**Overflow pages:** When a VARCHAR/TEXT/BLOB value exceeds ~1/2 of the page size,
InnoDB stores the prefix inline and the rest in separate overflow pages
(`ROW_FORMAT=DYNAMIC` stores only a 20-byte pointer inline).

**So what:**
- `SELECT *` on a wide table with large TEXT/BLOB columns forces InnoDB to follow
  overflow page pointers — multiple extra I/Os per row.
- `SELECT COUNT(*) FROM big_table` must read every leaf page of the clustered index;
  there is no shortcut (unlike MyISAM). Use a separate counter table or Redis for
  frequently-needed counts.
- Keep rows narrow. Normalise large blobs into a separate table.

---

## 3. Write-Ahead Log (WAL / Redo Log)

**The rule:** Every write goes to the redo log **before** the data page is modified.
This is the WAL guarantee — the log is the source of truth, not the page.

```
Client COMMIT
    │
    ▼
Redo log write (sequential, fast)
    │
    ▼
ACK to client   ←── durability point
    │
    ▼
Data page write (async, background)
```

InnoDB's `innodb_flush_log_at_trx_commit` controls when the redo log is fsynced:

| Value | Behaviour | Data loss on crash | Speed |
|-------|-----------|-------------------|-------|
| `1`   | fsync on every COMMIT | None | Slowest (safe) |
| `2`   | Write to OS buffer on COMMIT; fsync every second | Up to 1 second | Faster |
| `0`   | Write to InnoDB buffer every second; fsync every second | Up to 1 second + process crash | Fastest |

**The doublewrite buffer** prevents torn page writes (partial 16 KB writes on crash).
InnoDB writes pages to the doublewrite buffer first, then to their actual location.
If a crash occurs mid-write, the complete copy is recovered from the doublewrite buffer.

**Log Sequence Number (LSN):** A global monotonically increasing counter that represents
the total write position in the redo log. Used for recovery, replication coordination,
and backup consistency points. Monitoring LSN growth rate directly measures write
throughput.

**So what:**
- Production SaaS: keep `innodb_flush_log_at_trx_commit=1`. The performance
  difference is mostly irrelevant on NVMe SSDs and losing a second of transactions is
  never worth it.
- For batch import jobs, temporarily set `=2` to gain throughput, then reset.
- Monitor `SHOW ENGINE INNODB STATUS` for LSN growth to detect write bottlenecks.

---

## 4. Buffer Pool Mechanics — The Memory Manager

The **buffer pool** (page cache) is InnoDB's in-memory cache of disk pages. All reads
and writes go through it. The goal is to keep hot pages in memory and avoid disk I/O.

**LRU with midpoint insertion** prevents full table scans from evicting hot data:
```
[New sublist (5/8 of pool)] | midpoint | [Old sublist (3/8 of pool)]
```
- Pages newly loaded from disk enter at the **midpoint** (head of the old sublist).
- Pages accessed more than once are promoted to the **new sublist** (hot zone).
- Pages that are only accessed once (e.g., a full table scan) age out of the old sublist
  without ever polluting the new sublist.

`innodb_old_blocks_time` (default 1000ms): a page must be accessed again within this
window after its initial load to qualify for promotion. This prevents sequential scan
pollution.

**Buffer pool warming after restart:** After a MySQL restart, the buffer pool is cold.
InnoDB can save and restore the list of recently-used page IDs
(`innodb_buffer_pool_dump_at_shutdown=ON`, `innodb_buffer_pool_load_at_startup=ON`).

**So what:**
- Size `innodb_buffer_pool_size` to hold your working set — typically 70–80% of
  available RAM on a dedicated DB server.
- A `SELECT COUNT(*) FROM big_table` or a reporting query that scans the whole table
  will thrash the buffer pool unless `innodb_old_blocks_time` keeps it quarantined.
- After maintenance restarts, expect degraded performance for 10–30 minutes until the
  buffer pool re-warms. Schedule restarts before off-peak periods.

---

## 5. MVCC — Consistent Reads Without Locking

**Multi-Version Concurrency Control** gives each transaction a consistent snapshot of
the database at a point in time, without holding read locks.

Every InnoDB row has hidden system columns:
- `DB_TRX_ID`: the transaction ID that last modified this row version.
- `DB_ROLL_PTR`: pointer into the undo log to reconstruct the previous version.

When a transaction reads a row, InnoDB checks if the row's `DB_TRX_ID` is visible in
the transaction's **read view** (snapshot). If the row was modified by a newer
transaction, InnoDB follows `DB_ROLL_PTR` through the undo log to find the
appropriate older version.

```
Current row: TRX_ID=500, value='B'
    ↓ DB_ROLL_PTR
Undo log: TRX_ID=300, value='A'   ← transaction with read view at TRX_ID=400 sees this
    ↓
Undo log: TRX_ID=100, value='X'
```

**History List Length (HLL):** The number of undo log pages that have not yet been
purged. Long-running transactions hold a read view that prevents the purge thread
from discarding old undo log versions — even if those rows were deleted by other
committed transactions. HLL grows unboundedly until the long transaction finishes.

**So what:**
- Keep transactions short. An open transaction on a replica (or a reporting query)
  that runs for hours will bloat the undo log and degrade performance for everyone.
- Monitor `SHOW ENGINE INNODB STATUS` → `History list length`. Healthy: < 1000.
  Growing past 100,000 indicates a stuck long-running transaction.
- Never hold a transaction open across a user-facing HTTP request waiting for input.

---

## 6. Transaction Isolation Levels — What Each Actually Does

MySQL's default is `REPEATABLE READ`. The four levels and their real behaviour:

| Level | Snapshot | Dirty read | Non-repeatable read | Phantom read |
|-------|----------|-----------|---------------------|--------------|
| READ UNCOMMITTED | None | Yes | Yes | Yes |
| READ COMMITTED | Per-statement | No | Yes | Yes |
| REPEATABLE READ | Per-transaction | No | No | No (for SELECT) |
| SERIALIZABLE | Per-transaction + locks | No | No | No |

**READ COMMITTED:** Each SELECT within the transaction gets a fresh snapshot of
committed data. Good for analytical/reporting queries that run long and should see
recent commits. Eliminates gap locks entirely, reducing deadlock risk.

**REPEATABLE READ (MySQL default):** The snapshot is taken on the **first read** of the
transaction. All subsequent reads in the same transaction see the same data. Phantom
reads are prevented for `SELECT` (MVCC snapshot) but `INSERT`/`UPDATE`/`DELETE`
can still encounter new rows — handled by gap locks.

**SERIALIZABLE:** Converts all plain SELECTs into `SELECT ... FOR SHARE`. Every read
acquires a shared lock. Guaranteed no anomalies but terrible throughput under
concurrency. Avoid for SaaS applications.

**So what:**
- Leave the default `REPEATABLE READ` for OLTP transactions.
- Switch to `READ COMMITTED` at the session level for long-running reporting queries:
  `SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;`
- Never use `SERIALIZABLE` in a multi-tenant SaaS. It will deadlock under normal load.

---

## 7. Lock Types and Interactions

InnoDB has a layered locking system:

**Intention locks** (table-level, lightweight):
- `IS` (Intention Shared): a transaction wants shared locks on some rows.
- `IX` (Intention Exclusive): a transaction wants exclusive locks on some rows.
- Allow concurrent row-level locking while blocking full table operations.

**Row-level locks** (leaf node of the B-tree):
- **Record lock:** locks a single existing index record.
- **Gap lock:** locks the *gap* between two index records (no actual row). Prevents
  INSERT of new rows into the gap. Only exists in `REPEATABLE READ`.
- **Next-key lock:** record lock + gap lock on the preceding gap. Default for most
  row-level locking in `REPEATABLE READ`.

**Key insight:** Gap locks and next-key locks exist solely to prevent phantom reads in
`REPEATABLE READ`. Switching to `READ COMMITTED` eliminates all gap locks, which
is the primary fix for gap-lock deadlocks.

```sql
-- Acquires an exclusive record lock (plus gap locks in REPEATABLE READ)
SELECT * FROM orders WHERE id = 42 FOR UPDATE;

-- Acquires a shared lock — allows other shared locks, blocks exclusive
SELECT * FROM orders WHERE id = 42 FOR SHARE;
```

**INSERT and gap locks:** An INSERT acquires an **insert intention lock** (a special gap
lock) before inserting. Two INSERTs into the same gap will wait for each other only if
they would insert at the same position — they are otherwise compatible.

**Deadlock detection:** InnoDB automatically detects deadlocks using a waits-for graph.
It kills the transaction with the least undo log (cheapest to roll back) and returns
error 1213. The application must retry.

**So what:**
- If you have frequent deadlocks on INSERT-heavy tables, switch those sessions to
  `READ COMMITTED` to eliminate gap locks.
- Always design retry logic for error 1213 in application code.
- For `SELECT ... FOR UPDATE` patterns (e.g., pessimistic locking a queue), ensure
  the WHERE clause uses an indexed column — a full table scan would lock the entire
  table via next-key locks.

---

## 8. LSM Trees vs B-Trees — The Core Tradeoff

Understanding both structures informs when to choose MySQL InnoDB (B-tree) vs
alternatives like RocksDB/Cassandra (LSM):

```
B-Tree (InnoDB)                    LSM Tree (RocksDB/Cassandra)
─────────────────────────────────  ─────────────────────────────
In-place updates                   Append-only, immutable files
Random writes → random I/O         Sequential writes → sequential I/O
Read: 1-3 I/Os (tree height)       Read: may scan multiple sorted runs
Write amplification: medium         Write amplification: high (compaction)
Space amplification: low-medium     Space amplification: medium (tombstones)
Good for: OLTP read/write mix      Good for: write-heavy, time-series
```

**RUM Conjecture:** You cannot simultaneously optimise for Read overhead, Update
overhead, and Memory overhead. Every storage structure makes a tradeoff between these.
B-trees favour reads; LSM trees favour writes.

**So what:**
- For standard SaaS OLTP (mixed reads and writes, row updates in place), InnoDB
  B-trees are the right default.
- For high-ingest append-only workloads (audit logs, metrics, IoT), consider
  partitioning the table or using a dedicated time-series/LSM store.
- `OPTIMIZE TABLE` on an InnoDB table rewrites it as a fresh B-tree: reduces
  fragmentation but holds a table lock. Use `ALTER TABLE ... ALGORITHM=INPLACE` or
  pt-online-schema-change for production.

---

## 9. Distributed Systems Concepts Applied to MySQL

**CAP Theorem in practice:**
- MySQL InnoDB Cluster (Group Replication) is **CP**: it sacrifices availability to
  maintain consistency during a network partition. The minority partition refuses
  writes.
- MySQL async replication is **AP**: replicas continue serving reads even if they lag
  behind the primary, trading consistency for availability.

**Why 3 nodes minimum for Group Replication:**
Consensus (Paxos-based) requires a **quorum majority** to commit. With 3 nodes,
2/3 must agree. This means one node can fail and the cluster continues. With 2 nodes,
a single failure means no quorum — the cluster stops accepting writes.

```
3-node cluster: quorum = 2  → tolerates 1 failure
5-node cluster: quorum = 3  → tolerates 2 failures
2-node cluster: quorum = 2  → tolerates 0 failures (useless for HA)
```

**Replica lag and eventual consistency:**
Async replication means replicas may be seconds (or minutes) behind the primary.
A read from a replica may return stale data. This is **eventual consistency** — the
replica will converge, but not immediately.

The **read-your-writes consistency problem:** A user writes data to the primary, then
their next request reads from a replica that hasn't received the write yet. The user
sees their own write disappear. Solution: route writes and immediately-following reads
to the primary (sticky sessions), or use semi-sync replication.

**So what:**
- For user-facing reads after a write (e.g., "show me the record I just saved"), always
  read from the primary or wait for replica acknowledgment.
- Monitor replica lag with `SHOW REPLICA STATUS` → `Seconds_Behind_Source`.
  Alert if > 30 seconds.
- Always deploy MySQL replication in 3-node minimum for production HA.
  A 2-node setup offers no real fault tolerance.

---

## 10. Index Structures Beyond B-Trees

InnoDB supports several index types built on different structures:

| Index type | Internal structure | Supports range? | Use case |
|------------|-------------------|-----------------|----------|
| B-tree (default) | B+-tree | Yes | All general queries |
| Full-text | Inverted index | No (keyword match) | MATCH AGAINST queries |
| Spatial | R-tree | No (containment/proximity) | GIS, geometry columns |
| Adaptive Hash Index | Hash table | No | Auto-managed by InnoDB |

**Adaptive Hash Index (AHI):** InnoDB automatically builds an in-memory hash index
on top of the B-tree for frequently accessed index pages. It is not user-controllable.
Do not confuse with MySQL's unsupported HASH index type (only available in MEMORY
engine).

**Why hash indexes cannot do range queries:** A hash function distributes keys uniformly
— adjacent keys produce completely unrelated hash values. There is no ordering
preserved, so `WHERE age > 30` cannot be answered without scanning every bucket.

**So what:**
- Do not attempt to create HASH indexes on InnoDB tables — the engine will silently
  use B-tree anyway.
- For FULLTEXT search, use InnoDB FULLTEXT indexes for simple cases; migrate to
  Elasticsearch for complex relevance scoring.
- For geographic queries (distance, containment), use spatial indexes with GEOMETRY
  columns rather than storing lat/lng as floats and computing distance in PHP.

---

## 11. Write Amplification — Why SSDs Matter

A single user-visible write to MySQL triggers multiple physical writes:

```
1. Redo log write         (sequential, fast)
2. Doublewrite buffer     (sequential, crash safety)
3. Actual data page write (random, expensive)
4. Binary log write       (sequential, replication)
5. Undo log write         (for MVCC rollback)
```

This is **write amplification** — one logical write becomes 3–5 physical writes.
On spinning HDDs, random writes #3 are the bottleneck (seek time ~5ms).
On NVMe SSDs, random write latency drops to ~50µs, making the difference negligible.

**Compaction/fragmentation amplification:** After heavy UPDATE/DELETE activity, InnoDB
pages accumulate garbage cells. `OPTIMIZE TABLE` rewrites the entire table. For large
tables, use `ALTER TABLE ... ENGINE=InnoDB` with `innodb_online_alter_algorithm=INPLACE`
to avoid locking.

**So what:**
- Always run MySQL on SSDs in production. The write amplification model is designed
  assuming fast random I/O.
- Monitor I/O wait (`iostat -x 1`) — if `%iowait` is consistently above 20%, the
  buffer pool is too small or you need faster storage.
- For write-heavy workloads, ensure `innodb_io_capacity` and
  `innodb_io_capacity_max` are tuned to your SSD's actual IOPS capability.

---

## 12. MySQL vs PostgreSQL Internals — Key Architectural Differences

| Aspect | MySQL InnoDB | PostgreSQL |
|--------|-------------|------------|
| MVCC storage | Undo log (old versions separate) | Heap (old versions in-table) |
| Vacuum/cleanup | Background purge thread (automatic) | Explicit VACUUM needed |
| Secondary index | Stores PK (double traversal) | Stores heap tuple ID (direct) |
| Full-text quality | Adequate for basic use | Better with ts_vector/ts_query |
| JSON support | JSON type, limited indexing | JSONB with full GIN indexing |
| Isolation default | REPEATABLE READ | READ COMMITTED |

**MVCC implementation difference matters:**
- InnoDB keeps the "current" version in the main page; old versions in the undo log.
  Long transactions bloat the undo log.
- PostgreSQL keeps all versions in the heap. Old versions bloat the table itself.
  VACUUM reclaims them. Without regular VACUUM, tables grow indefinitely (table bloat).

**So what:**
- When evaluating PostgreSQL for a project, factor in the operational requirement for
  `autovacuum` tuning. Without it, tables degrade significantly.
- MySQL's automatic undo purge is simpler operationally but watch the History List
  Length for signs of purge lag.

---

## 13. Design Rules Derived from Internals

These rules flow directly from the mental models above. Apply them to every schema
and query design decision.

**Schema design:**

| Rule | Reason (from internals) |
|------|------------------------|
| Use `BIGINT AUTO_INCREMENT` PK | Sequential inserts, no B-tree fragmentation |
| Keep PK as small as possible | Secondary indexes store the full PK; large PKs bloat all secondary indexes |
| Avoid `SELECT *` | Wide rows + overflow pages = unnecessary I/O |
| Normalise large BLOBs into a separate table | Overflow pages cause extra I/Os on every row read |
| Add covering indexes for hot queries | Eliminates the second clustered index traversal |

**Transaction design:**

| Rule | Reason (from internals) |
|------|------------------------|
| Keep transactions short | Long transactions bloat undo log (MVCC HLL) |
| Never hold TX open across network I/O | MVCC snapshot held, HLL grows, connections blocked |
| Use `READ COMMITTED` for reporting queries | Fresh snapshots, no gap locks, faster |
| Design retry logic for deadlock (error 1213) | InnoDB auto-detects and kills one TX |

**Operational signals to monitor:**

```sql
-- MVCC health: undo log bloat
SHOW ENGINE INNODB STATUS;  -- look for "History list length"
-- Healthy: < 1000. Alert: > 50,000

-- Replication health
SHOW REPLICA STATUS\G       -- look for "Seconds_Behind_Source"

-- Buffer pool efficiency
SELECT (1 - (innodb_buffer_pool_reads / innodb_buffer_pool_read_requests)) * 100
  AS buffer_pool_hit_rate
FROM information_schema.global_status
WHERE variable_name IN ('innodb_buffer_pool_reads', 'innodb_buffer_pool_read_requests');
-- Target: > 99%

-- I/O pressure
SHOW GLOBAL STATUS LIKE 'innodb_data_reads';
SHOW GLOBAL STATUS LIKE 'innodb_data_writes';
```

---

## Quick-Reference: The 10 Mental Model Checklist

Before finalising any schema or query:

1. **PK choice** — Is it sequential (AUTO_INCREMENT)? Small enough to not bloat secondary indexes?
2. **Row width** — Any large columns that should be in a separate table?
3. **Secondary indexes** — Do hot queries need covering indexes to avoid double traversal?
4. **Transaction length** — Will this TX stay open across network calls? Can it be shortened?
5. **Isolation level** — Is `REPEATABLE READ` appropriate, or would `READ COMMITTED` reduce lock contention?
6. **Gap locks** — Is this an INSERT-heavy table prone to gap-lock deadlocks? Consider `READ COMMITTED`.
7. **MVCC pressure** — Are there long-running queries that hold read views and bloat HLL?
8. **Replication reads** — After a write, does the app read from a replica (stale data risk)?
9. **Buffer pool fit** — Will the working set fit in the configured `innodb_buffer_pool_size`?
10. **Write amplification** — Is this a write-heavy workload that needs SSD I/O tuning?

---

*Source: Database Internals — Alex Petrov (O'Reilly, 2019). Applied to MySQL InnoDB.*
