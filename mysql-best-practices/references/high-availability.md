# MySQL High Availability Reference

> Sources: "Efficient MySQL Performance" (Nichter, 2022) Ch7;
> "Mastering MySQL Administration" (Kumar et al., 2024) Ch5-6

---

## Replication Fundamentals

MySQL replication copies data from a **source** (formerly master) to one or more
**replicas** (formerly slave). Replication is **required** for high availability.

**Data flow:**

```
Source → Binary Log → [network] → I/O Thread → Relay Log → SQL Thread (Applier) → Replica Data
```

- **Binary log (binlog):** Records all changes on the source.
- **I/O thread:** Runs on the replica, reads binlog events from source.
- **Relay log:** Local copy of binlog events on the replica.
- **SQL thread (applier):** Replays relay log events to apply changes.

---

## Binlog-Position vs GTID Replication

| Aspect | Binlog-Position | GTID |
|---|---|---|
| Tracking | Log file name + numeric position | Global Transaction Identifier |
| Failover | Manual log/position coordination | Automatic position resolution |
| Complexity | Higher operational burden | Simpler topology changes |
| Recommendation | Legacy only | **Use for all new deployments** |

**GTID format:** `source_uuid:transaction_id` (e.g., `3E11FA47-71CA-11E1-9E33-C80AA9429562:23`)

GTID eliminates the need to track binlog file names and positions. When a replica
connects with `SOURCE_AUTO_POSITION=1`, it tells the source which GTIDs it already
has, and the source sends only the missing ones.

---

## Replication Setup -- GTID (Recommended)

### Source Configuration (my.cnf)

```ini
[mysqld]
server-id                      = 1
log-bin                        = mysql-bin
binlog-format                  = ROW
gtid_mode                      = ON
enforce_gtid_consistency       = ON
innodb-flush-log-at-trx-commit = 1
sync-binlog                    = 1
binlog-expire-logs-seconds     = 604800   # 7 days
```

### Replica Configuration (my.cnf)

```ini
[mysqld]
server-id                  = 2
relay-log                  = relay-bin
read-only                  = ON
super-read-only            = ON
skip-slave-start           = ON
gtid_mode                  = ON
enforce_gtid_consistency   = ON
log-bin                    = mysql-bin       # enables replica to be a source later
log-slave-updates          = ON
replica_parallel_workers   = 4
replica_parallel_type      = LOGICAL_CLOCK
```

### SQL Commands

```sql
-- On SOURCE: create dedicated replication user
CREATE USER 'repl_user'@'%' IDENTIFIED BY 'Strong!Pass#2024';
GRANT REPLICATION SLAVE ON *.* TO 'repl_user'@'%';
FLUSH PRIVILEGES;

-- On REPLICA: point to source with GTID auto-positioning
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST     = 'source_host',
  SOURCE_PORT     = 3306,
  SOURCE_USER     = 'repl_user',
  SOURCE_PASSWORD = 'Strong!Pass#2024',
  SOURCE_AUTO_POSITION = 1,
  GET_SOURCE_PUBLIC_KEY = 1;
START REPLICA;

-- Verify: Replica_IO_Running = Yes, Replica_SQL_Running = Yes
SHOW REPLICA STATUS\G
```

---

## Replication Types

### Asynchronous (Default)

Source commits and returns to client immediately. Replica fetches changes
independently. **Risk:** Transactions may be lost if source crashes before
replica receives them.

### Semi-Synchronous

Source waits for **at least one** replica to acknowledge receipt. No committed
data loss (acknowledged transactions exist on at least 2 nodes).

```sql
-- Source
INSTALL PLUGIN rpl_semi_sync_source SONAME 'semisync_source.so';
SET GLOBAL rpl_semi_sync_source_enabled = 1;
SET GLOBAL rpl_semi_sync_source_timeout = 5000;  -- ms, fallback to async

-- Replica
INSTALL PLUGIN rpl_semi_sync_replica SONAME 'semisync_replica.so';
SET GLOBAL rpl_semi_sync_replica_enabled = 1;
STOP REPLICA; START REPLICA;
```

### Group Replication

Consensus-based (Paxos): all members agree on transaction ordering. Supports
single-primary or multi-primary modes. Foundation layer for InnoDB Cluster.

---

## Multi-Threaded Replication

Single-threaded replication is the primary bottleneck for replica lag.

```ini
[mysqld]
replica_parallel_workers = 4              # number of applier threads
replica_parallel_type   = LOGICAL_CLOCK   # parallelism strategy
replica_preserve_commit_order = ON        # maintain source commit order
```

### Parallelism Types

| Type | Description | Performance |
|---|---|---|
| `DATABASE` | Parallel across different databases only | Limited |
| `LOGICAL_CLOCK` | Parallel for transactions that overlapped on source | Better |
| `WRITESET` (8.0.27+) | Parallel if no row conflicts (best) | **Best** |

**WRITESET setup (MySQL 8.0.27+):**

```ini
# Source
binlog_transaction_dependency_tracking = WRITESET
transaction_write_set_extraction       = XXHASH64
# Replica
replica_parallel_type    = LOGICAL_CLOCK
replica_parallel_workers = 8
```

---

## Replication Lag

### Why Seconds_Behind_Source Is Unreliable

`Seconds_Behind_Source` from `SHOW REPLICA STATUS` measures the difference between
the timestamp of the event being applied and the current time. It does **not**
account for events waiting in the relay log, network delays, or I/O thread lag.
It can show 0 while the replica is minutes behind.

### Accurate Measurement: pt-heartbeat

```bash
# On source (writes heartbeat rows every second)
pt-heartbeat --update --database percona --create-table \
  --host=source_host --user=monitor --password=pass

# On replica (reads heartbeat and computes actual delay)
pt-heartbeat --monitor --database percona \
  --host=replica_host --user=monitor --password=pass
```

### Common Causes and Mitigation

**Causes:** Source throughput exceeds replica apply capacity, large transactions
serialize on replica, network latency, slower replica disk I/O, single-threaded
replication.

**Mitigation:** Enable multi-threaded replication (WRITESET), break large
transactions into batches, use `READ COMMITTED` isolation on replicas, ensure
replica hardware matches source, optimize source queries to reduce binlog volume.

---

## InnoDB Cluster

### Architecture

```
                  ┌─────────────────┐
                  │  MySQL Router    │  ← Client connections
                  └────────┬────────┘
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
    │ Member 1│      │ Member 2│      │ Member 3│
    │ PRIMARY │◄────►│ REPLICA │◄────►│ REPLICA │
    └─────────┘      └─────────┘      └─────────┘
         Group Replication (consensus)
```

- **Minimum 3 instances** for fault tolerance (tolerates 1 failure).
- 5 instances tolerate 2 failures; 7 tolerate 3.
- Built-in automatic failover when primary becomes unavailable.

### Setup with MySQL Shell

```javascript
shell.connect('admin@mysql1:3306');

// Configure all instances
dba.configureInstance('admin@mysql1:3306');
dba.configureInstance('admin@mysql2:3306');
dba.configureInstance('admin@mysql3:3306');

// Create cluster and add members
var cluster = dba.createCluster('prodCluster');
cluster.addInstance('admin@mysql2:3306');
cluster.addInstance('admin@mysql3:3306');

// Check status (key fields: status, topologyMode, primary, memberState)
cluster.status({extended: 1});
```

---

## InnoDB ClusterSet

For **disaster recovery across data centers**. Links a primary InnoDB Cluster
to one or more replica clusters via asynchronous replication.

```
  Data Center A                    Data Center B
┌─────────────────┐           ┌─────────────────┐
│ Primary Cluster │──async──►│ Replica Cluster  │
│ (read-write)    │  repl    │ (read-only)      │
│ 3+ members      │           │ 3+ members       │
└─────────────────┘           └─────────────────┘
```

### Setup and Management

```javascript
// Create ClusterSet from existing cluster
var cluster = dba.getCluster();
var cs = cluster.createClusterSet('globalSet');

// Create replica cluster in second DC
cs.createReplicaCluster('admin@dc2-mysql1:3306', 'replicaCluster');
var rc = dba.getCluster('replicaCluster');
rc.addInstance('admin@dc2-mysql2:3306');
rc.addInstance('admin@dc2-mysql3:3306');
cs.status({extended: 1});

// Planned switchover (zero data loss)
cs.setPrimaryCluster('replicaCluster');

// Emergency failover (potential data loss, primary is DOWN)
cs.forcePrimaryCluster('replicaCluster');
```

---

## MySQL Router

Provides transparent client routing to the correct cluster member.

### Bootstrap and Ports

```bash
mysqlrouter --bootstrap admin@mysql1:3306 \
  --directory /opt/mysqlrouter \
  --account mysqlrouter_user
```

| Port | Purpose |
|---|---|
| 6446 | Read-write (routes to primary) |
| 6447 | Read-only (routes to replicas, round-robin) |
| 64460 | Read-write (X Protocol) |
| 64470 | Read-only (X Protocol) |

```bash
mysql -u app_user -p -h router_host -P 6446   # writes
mysql -u app_user -p -h router_host -P 6447   # reads
```

---

## Failover Scenarios

**1. Primary Instance Failure (InnoDB Cluster):** Automatic. Group Replication
elects a new primary. MySQL Router detects the change and routes connections
to the new primary. No manual intervention required.

**2. Controlled Switchover (ClusterSet):** `cs.setPrimaryCluster('replicaCluster')`
waits for replication to catch up, then switches roles. Zero data loss.

**3. Complete Outage Recovery:** After all members restart, run
`dba.rebootClusterFromCompleteOutage('prodCluster')`. Selects the member with
the most recent data as primary.

---

## Clone Plugin

Fast provisioning of new replicas by copying a full data snapshot from a donor.

```sql
-- Install on both donor and recipient
INSTALL PLUGIN clone SONAME 'mysql_clone.so';

-- On donor: create clone user
CREATE USER 'clone_user'@'%' IDENTIFIED BY 'ClonePass!2024';
GRANT BACKUP_ADMIN ON *.* TO 'clone_user'@'%';

-- On recipient: set donor list and clone
SET GLOBAL clone_valid_donor_list = 'donor_host:3306';
CLONE INSTANCE FROM 'clone_user'@'donor_host':3306
  IDENTIFIED BY 'ClonePass!2024';
-- Instance restarts automatically after clone completes
```

InnoDB Cluster uses clone automatically when adding instances whose data
diverges too much for incremental recovery.

---

## Scaling Reads

- Route **read queries** to replicas via MySQL Router port 6447.
- Route **write queries** to source via MySQL Router port 6446.
- **Critical reads** (read-after-write consistency) must go to source.

```php
// PHP example: dual-connection pattern
$write_db = new PDO('mysql:host=router;port=6446;dbname=app', $user, $pass);
$read_db  = new PDO('mysql:host=router;port=6447;dbname=app', $user, $pass);

// Use $write_db for INSERT, UPDATE, DELETE
// Use $read_db for SELECT (non-critical)
// Use $write_db for SELECT when read-after-write is needed
```

**Eventual consistency warning:** Replicas may lag behind the source. If a user
writes data and immediately reads it back, the replica may not have it yet.
Solution: read from source for a short window after writes.

---

## Sharding (When Single Server Is Not Enough)

### When to Shard

Single MySQL server practical limit: **~1 TB** for average workloads, **~2 TB**
optimized. Beyond this, consider sharding or distributed databases.

### Shard Key Properties

1. **High cardinality** -- many distinct values.
2. **References a core entity** -- typically tenant_id or user_id.
3. **Small data type** -- INT or BIGINT, not VARCHAR.

### Strategies

| Strategy | How It Works | Pros | Cons |
|---|---|---|---|
| Hash | `shard = hash(key) % N` | Even distribution | Resharding is hard |
| Range | Key ranges per shard | Simple, range queries | Hotspots possible |
| Directory | Lookup table maps key to shard | Flexible | Lookup table is SPOF |

### Challenges

- **No cross-shard transactions** -- each shard is independent.
- **No cross-shard JOINs** -- application must merge results.
- **Schema changes** must be applied to every shard.
- **Resharding** (adding shards) requires data migration.

### Alternatives to Manual Sharding

| System | Type | Notes |
|---|---|---|
| Vitess | MySQL sharding middleware | YouTube-proven, open source |
| TiDB | Distributed SQL (MySQL compat) | Auto-sharding, HTAP |
| CockroachDB | Distributed SQL (PG wire) | Geo-distributed |
| PlanetScale | Managed Vitess | Serverless MySQL |

---

## Troubleshooting Replication

### Error 1032: Row Not Found on Replica

```sql
-- Skip the problematic transaction (use with caution)
STOP REPLICA;
SET GLOBAL sql_slave_skip_counter = 1;
START REPLICA;

-- With GTID: inject an empty transaction for the failing GTID
STOP REPLICA;
SET GTID_NEXT = 'source_uuid:failing_txn_id';
BEGIN; COMMIT;
SET GTID_NEXT = 'AUTOMATIC';
START REPLICA;
```

### Duplicate Server UUID

If replicas were cloned from the same image, they share `auto.cnf`.

```bash
rm /var/lib/mysql/auto.cnf
systemctl restart mysqld
```

### Binlog Disk Full

```sql
PURGE BINARY LOGS BEFORE NOW() - INTERVAL 3 DAY;
SET GLOBAL binlog_expire_logs_seconds = 259200;  -- 3 days
```

### No Primary Key (Group Replication Requirement)

Group Replication requires every table to have a primary key.

```sql
-- Find tables without primary keys
SELECT t.TABLE_SCHEMA, t.TABLE_NAME
FROM information_schema.TABLES t
LEFT JOIN information_schema.TABLE_CONSTRAINTS c
  ON t.TABLE_SCHEMA = c.TABLE_SCHEMA
  AND t.TABLE_NAME = c.TABLE_NAME
  AND c.CONSTRAINT_TYPE = 'PRIMARY KEY'
WHERE c.CONSTRAINT_NAME IS NULL
  AND t.TABLE_SCHEMA NOT IN ('mysql','information_schema','performance_schema','sys')
  AND t.TABLE_TYPE = 'BASE TABLE';

-- Fix: add surrogate PK
ALTER TABLE schema_name.table_name
  ADD COLUMN id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY;
```

### Replica Stopped with Error

```sql
SHOW REPLICA STATUS\G
-- Look at: Last_SQL_Errno, Last_SQL_Error

-- Common fix: skip and investigate root cause
STOP REPLICA;
SET GLOBAL sql_slave_skip_counter = 1;
START REPLICA;
```

---

## Quick Checklist

- [ ] GTID mode ON for all new replication setups
- [ ] ROW-based binlog format (not STATEMENT or MIXED)
- [ ] Multi-threaded replication enabled on all replicas
- [ ] Semi-synchronous replication for data safety
- [ ] pt-heartbeat for accurate lag monitoring (not Seconds_Behind_Source)
- [ ] MySQL Router for transparent failover
- [ ] Clone plugin installed for fast provisioning
- [ ] All tables have primary keys (required for Group Replication)
- [ ] super-read-only ON for replicas (prevents accidental writes)
- [ ] Binlog expiry configured to prevent disk fill
