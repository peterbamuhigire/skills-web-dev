# MySQL Transaction and Locking Reference

Deep reference for InnoDB transactions, locking, MVCC, and deadlock prevention.
Based on "Efficient MySQL Performance" by Daniel Nichter (O'Reilly, 2022), Chapter 8.

---

## ACID Properties

Every InnoDB transaction guarantees four properties:

- **Atomicity** -- All statements succeed or none do. No partial commits.
- **Consistency** -- Valid state transitions only. Constraints enforced at commit.
- **Isolation** -- Concurrent transactions do not interfere. Degree depends on isolation level.
- **Durability** -- Committed data survives crashes. Redo log + doublewrite buffer ensure this. Requires `innodb_flush_log_at_trx_commit = 1` (default).

---

## Transaction Isolation Levels

Default is REPEATABLE READ. **READ COMMITTED is recommended for SaaS.**

| Level | Gap Locks | Consistent Snapshot | Non-repeatable Reads | Phantom Rows |
|---|---|---|---|---|
| READ UNCOMMITTED | No | No | Yes | Yes |
| READ COMMITTED | No | Per-statement | Yes | Yes |
| **REPEATABLE READ** (default) | Yes | Per-transaction | No | No (InnoDB) |
| SERIALIZABLE | Yes | Full serialization | No | No |

**READ UNCOMMITTED:** Reads dirty (uncommitted) data. Never use in production.

**READ COMMITTED (Recommended for SaaS):** Each SELECT sees a fresh snapshot of committed data as of that statement's start. No gap locks -- only record locks.

```sql
-- Set globally (my.cnf)
[mysqld]
transaction-isolation = READ-COMMITTED

-- Set per session
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

**Why RC is recommended for SaaS apps:**

1. **Less locking** -- No gap locks; UPDATE/DELETE lock only rows they modify.
2. **Better concurrency** -- Less contention between tenants and API requests.
3. **Fewer deadlocks** -- Gap locks are the primary source; eliminating them removes an entire class.
4. **Predictable behavior** -- Locking only touched rows matches developer mental models.
5. **Industry standard** -- PostgreSQL, Oracle, SQL Server all default to RC.

**Trade-off:** Non-repeatable reads possible (a second SELECT may see new committed data). Rarely a problem for short SaaS transactions.

**REPEATABLE READ (MySQL Default):** Snapshot at first read. All subsequent reads see same snapshot. Uses next-key locks (record + gap) -- prevents phantoms but increases contention.

**SERIALIZABLE:** All SELECTs become `SELECT ... FOR SHARE`. Extremely poor concurrency -- avoid.

---

## InnoDB Lock Types (Deep Dive)

InnoDB locks index records, not table rows. If no index exists, uses hidden clustered index (GEN_CLUST_INDEX).

| Lock Type | Abbreviation | What It Locks |
|---|---|---|
| Record lock | `REC_NOT_GAP` | Single index record only |
| Gap lock | `GAP` | Gap before a record (range between two records) |
| Next-key lock | `X` or `S` | Record AND the gap before it (default in RR) |
| Insert intention lock | `INSERT_INTENTION` | Allows INSERT into a gap |

### Record Lock (REC_NOT_GAP)

Locks a single index record. The only lock type used in READ COMMITTED.

```sql
UPDATE orders SET status = 'shipped' WHERE id = 42;
-- data_locks: lock_mode: X,REC_NOT_GAP | lock_data: 42
```

### Gap Lock (GAP)

Locks the gap between two index records. Only in RR and SERIALIZABLE.

```sql
-- Index has records 10, 20, 30:
-- Gap lock on 20 locks range (10, 20) -- no inserts of 11-19
-- data_locks: lock_mode: X,GAP | lock_data: 20
```

### Next-Key Lock (Default in RR)

Record lock + gap lock combined. Locks the record AND gap before it.

```sql
-- Index has 10, 20, 30:
-- Next-key lock on 20 locks (10, 20] -- gap plus record
-- data_locks: lock_mode: X | lock_data: 20  (no suffix = next-key)
```

### Insert Intention Lock

Signals intent to insert. Multiple transactions can hold insert intention locks on the same gap if inserting at different positions.

---

## Critical Locking Behaviors

### 1. RR Uses Next-Key Locks (Locks More Than You Expect)

```sql
-- REPEATABLE READ: UPDATE locks records AND gaps on traversed indexes
UPDATE orders SET status = 'processed'
WHERE tenant_id = 5 AND status = 'pending';
-- Locks every traversed index record, gaps between them, AND corresponding PK records
-- Can block INSERTs from OTHER tenants
```

### 2. RC Uses Record Locks Only

```sql
-- READ COMMITTED: Same query locks ONLY matching rows
-- No gap locks, no blocking of other tenants' inserts
-- Rows examined but not modified are unlocked immediately
```

### 3. BETWEEN vs IN: Locking Implications

```sql
-- BETWEEN traverses a range -> next-key locks on every record (in RR)
UPDATE orders SET status = 'archived' WHERE id BETWEEN 100 AND 200;

-- IN does point lookups -> record locks only (even in RR for unique indexes)
UPDATE orders SET status = 'archived' WHERE id IN (100, 150, 200);
```

**Rule:** Prefer `IN()` over `BETWEEN` when you know exact values -- fewer locks, fewer deadlocks.

### 4. Low-Selectivity Secondary Indexes

```sql
-- status has 3 distinct values -- locks HUGE range of the index
UPDATE orders SET updated_at = NOW() WHERE status = 'pending';
-- Better: narrow with tenant_id
UPDATE orders SET updated_at = NOW() WHERE tenant_id = 5 AND status = 'pending';
```

### 5. SELECT ... FOR SHARE on Zero Rows

Even matching ZERO rows, `FOR SHARE` acquires gap locks in RR, blocking inserts.

```sql
SELECT * FROM orders WHERE id = 999 FOR SHARE;
-- No rows match, but blocks INSERT of id = 999 until COMMIT
```

### 6. InnoDB Locks EVERY Row It Accesses

Not just rows it writes -- every row examined during the write operation.

```sql
-- Without index on (tenant_id, status): type: ALL -> locks ENTIRE table
EXPLAIN UPDATE orders SET status = 'done' WHERE tenant_id = 5 AND status = 'pending';
-- With composite index: type: range -> locks only matching rows
```

---

## MVCC (Multi-Version Concurrency Control)

Each InnoDB row has hidden fields: **trx_id** (last modifying transaction) and **roll_pointer** (previous version in undo log).

When a row is modified: (1) current version copied to undo log, (2) row updated in-place, (3) trx_id set to current transaction, (4) roll_pointer set to undo entry.

### Snapshot Behavior

- **RR:** Snapshot at first read in transaction. All reads see same snapshot.
- **RC:** Snapshot at each statement. Each SELECT sees latest committed data.

| Operation | Locks? | Sees |
|---|---|---|
| `SELECT` (plain) | No | Snapshot (committed data) |
| `SELECT ... FOR SHARE` | Shared lock | Latest committed version |
| `SELECT ... FOR UPDATE` | Exclusive lock | Latest committed version |
| `UPDATE` / `DELETE` | Exclusive lock | Latest committed version |

Plain SELECTs never acquire or wait for locks. They read from the MVCC snapshot -- fast even under heavy write load.

---

## Undo Log and History List Length

The undo log stores old row versions for MVCC (consistent snapshots) and rollback.

**History List Length (HLL):** Unmerged undo records. InnoDB purges in the background.

| HLL Value | Status | Action |
|---|---|---|
| < 1,000 | Normal | No action needed |
| 1,000 - 100,000 | Elevated | Investigate long-running transactions |
| 100,000 - 1,000,000 | Concerning | Find and kill stalled transactions |
| > 1,000,000 | Critical | MySQL struggling to purge; performance degrading |

**Why HLL grows:** Long-running transactions hold snapshots open, preventing purge of undo records created after the snapshot.

```sql
-- This prevents undo purge:
BEGIN;
SELECT * FROM config WHERE key = 'version';
-- Developer forgets to COMMIT... HLL climbs to 2,000,000+
```

**Monitoring HLL:**

```sql
SHOW ENGINE INNODB STATUS\G  -- Look for "History list length"

SELECT count FROM information_schema.innodb_metrics
WHERE name = 'trx_rseg_history_len';
```

---

## Deadlock Prevention

### 1. Lock Rows in Consistent Order

```sql
-- BAD: Tx A locks 1 then 2; Tx B locks 2 then 1 -> DEADLOCK
-- GOOD: Use LEAST/GREATEST to enforce ascending PK order
SET @first = LEAST(1, 2), @second = GREATEST(1, 2);
UPDATE t SET v = 1 WHERE id = @first;
UPDATE t SET v = 1 WHERE id = @second;
```

### 2. Keep Transactions Short

```sql
-- BAD: Lock held during application logic (network round-trip)
BEGIN;
SELECT balance FROM accounts WHERE id = 5 FOR UPDATE;
-- ... app calculates ...
UPDATE accounts SET balance = 150.00 WHERE id = 5;
COMMIT;

-- GOOD: Single atomic statement
UPDATE accounts SET balance = balance + 50.00 WHERE id = 5;
```

### 3. Use IN() Instead of BETWEEN

Fewer gap locks. See "BETWEEN vs IN" above.

### 4. Use READ COMMITTED

Eliminates gap locks entirely -- prevents the majority of SaaS deadlocks.

### 5. Avoid SELECT ... FOR UPDATE/FOR SHARE

```sql
-- BAD: Pessimistic locking
BEGIN;
SELECT * FROM inventory WHERE product_id = 10 FOR UPDATE;
UPDATE inventory SET quantity = quantity - 1 WHERE product_id = 10;
COMMIT;

-- GOOD: Optimistic atomic UPDATE
UPDATE inventory SET quantity = quantity - 1
WHERE product_id = 10 AND quantity > 0;
-- affected_rows: 1 = success, 0 = out of stock
```

### 6. InnoDB Auto-Detects Deadlocks

Rolls back the transaction with fewest undo records. App receives error 1213:

```
ERROR 1213 (40001): Deadlock found when trying to get lock
```

**Application retry pattern (PHP):**

```php
$maxRetries = 3;
for ($attempt = 1; $attempt <= $maxRetries; $attempt++) {
    try {
        $pdo->beginTransaction();
        // ... execute statements ...
        $pdo->commit();
        break;
    } catch (PDOException $e) {
        $pdo->rollBack();
        if ($e->getCode() == '40001' && $attempt < $maxRetries) {
            usleep(100000 * $attempt); // backoff: 100ms, 200ms, 300ms
            continue;
        }
        throw $e;
    }
}
```

---

## Common Transaction Problems

### 1. Large Transactions

Lock many rows, cause replication lag (row-based replication replays as single event).

```sql
-- BAD: Update 1M rows in one transaction
UPDATE orders SET archived = 1 WHERE created_at < '2024-01-01';

-- GOOD: Batch in chunks
REPEAT
  UPDATE orders SET archived = 1
  WHERE created_at < '2024-01-01' AND archived = 0 LIMIT 1000;
UNTIL ROW_COUNT() = 0 END REPEAT;
```

### 2. Long-Running Transactions

Prevent undo purge, HLL grows. Even idle transactions hold snapshots open.

### 3. Stalled Transactions

`BEGIN` without `COMMIT`/`ROLLBACK`. Common with connection pooling when exceptions skip cleanup.

```sql
-- Find stalled transactions (running > 60s with no current query)
SELECT trx_id, trx_started, trx_state,
       TIMESTAMPDIFF(SECOND, trx_started, NOW()) AS age_seconds
FROM information_schema.innodb_trx
WHERE trx_state = 'RUNNING'
  AND TIMESTAMPDIFF(SECOND, trx_started, NOW()) > 60;
```

### 4. Lock Wait Timeout

`innodb_lock_wait_timeout` defaults to 50s. Per row, not per transaction.

```sql
SHOW VARIABLES LIKE 'innodb_lock_wait_timeout';
SET GLOBAL innodb_lock_wait_timeout = 10;  -- Fail fast for SaaS
```

### 5. Lost Updates

Concurrent overwrites. Solutions:

```sql
-- Atomic update (no read-modify-write cycle)
UPDATE accounts SET balance = balance - 50 WHERE id = 5 AND balance >= 50;

-- Optimistic locking with version column
UPDATE orders SET status = 'shipped', version = version + 1
WHERE id = 100 AND version = 3;
-- affected_rows = 0 means concurrent modification
```

---

## Transaction Monitoring

### Active Transactions

```sql
SELECT trx_id, trx_state, trx_started,
       TIMESTAMPDIFF(SECOND, trx_started, NOW()) AS age_sec,
       trx_rows_locked, trx_rows_modified, trx_query
FROM information_schema.innodb_trx ORDER BY trx_started;
```

### Data Locks (MySQL 8.0.16+)

```sql
SELECT engine_transaction_id, index_name,
       lock_type, lock_mode, lock_status, lock_data
FROM performance_schema.data_locks
WHERE object_schema = 'mydb' AND object_name = 'orders';
```

Sample output:

```
engine_transaction_id | index_name | lock_type | lock_mode     | lock_status | lock_data
281479959840512       | PRIMARY    | RECORD    | X,REC_NOT_GAP | GRANTED     | 42
281479959840512       | idx_status | RECORD    | X,REC_NOT_GAP | GRANTED     | 'pending', 42
```

### Lock Waits (MySQL 8.0.16+)

```sql
SELECT r.trx_id AS waiting_trx, r.trx_query AS waiting_query,
       b.trx_id AS blocking_trx, b.trx_query AS blocking_query
FROM performance_schema.data_lock_waits w
JOIN information_schema.innodb_trx r ON r.trx_id = w.requesting_engine_transaction_id
JOIN information_schema.innodb_trx b ON b.trx_id = w.blocking_engine_transaction_id;
```

### SHOW ENGINE INNODB STATUS

Key fields in the TRANSACTIONS section:

- **History list length** -- HLL (should be < 1,000)
- **ACTIVE n sec** -- Transaction age
- **lock struct(s)** / **row lock(s)** -- Lock counts
- **WAITING FOR THIS LOCK TO BE GRANTED** -- Lock wait details

---

## Best Practices Summary

| Practice | Why |
|---|---|
| Use READ COMMITTED for SaaS | Less locking, better concurrency, fewer deadlocks |
| Keep transactions short | Fewer locks held, lower HLL, less replication lag |
| Never BEGIN without COMMIT/ROLLBACK | Stalled transactions grow HLL and block purge |
| Lock in consistent order | Prevents deadlocks |
| Prefer IN() over BETWEEN | Fewer gap locks, less contention |
| Monitor HLL | Catches stalled transactions before performance degrades |
| Handle deadlocks in application | Retry with backoff (error 1213 / SQLSTATE 40001) |
| Use explicit transactions | Multi-statement ops need atomicity guarantees |
| Use atomic UPDATE expressions | Prevents lost updates without pessimistic locking |
| Batch large writes | Reduces lock duration and replication lag |
| Set innodb_lock_wait_timeout = 10 | Fail fast in SaaS; retry at application layer |
| Index write-path queries | InnoDB locks every row it accesses during writes |

---

*Reference: "Efficient MySQL Performance" by Daniel Nichter, O'Reilly, 2022.*
*Applicable to: MySQL 8.0+ with InnoDB storage engine.*
