---
name: mysql-administration
description: 'Expert MySQL 8 administration: replication topology, InnoDB Cluster
  / Group Replication, security hardening, backup strategies with mysqldump/mydumper/xtrabackup,
  monitoring with Performance Schema, and production operations. Use when setting
  up...'
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# MySQL Administration — Expert Reference

<!-- dual-compat-start -->
## Use When

- Expert MySQL 8 administration: replication topology, InnoDB Cluster / Group Replication, security hardening, backup strategies with mysqldump/mydumper/xtrabackup, monitoring with Performance Schema, and production operations. Use when setting up...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `mysql-administration` or would be better handled by a more specific companion skill.
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
## 1. my.cnf Production Baseline

```ini
[mysqld]
# --- Identity ---
server-id                        = 1          # unique per node
report_host                      = mysql-a    # used by InnoDB Cluster

# --- Character set ---
character_set_server             = utf8mb4
collation_server                 = utf8mb4_unicode_ci

# --- InnoDB memory ---
innodb_buffer_pool_size          = 10G        # 70% of available RAM
innodb_buffer_pool_instances     = 8          # 1 per GB of pool; reduces contention
innodb_log_buffer_size           = 48M        # larger for heavy write workloads

# --- InnoDB redo log (MySQL 8.0.30+) ---
innodb_redo_log_capacity         = 2G         # replaces innodb_log_file_size
# Legacy (pre-8.0.30): innodb_log_file_size=512M  innodb_log_files_in_group=2

# --- InnoDB durability ---
innodb_flush_log_at_trx_commit   = 1          # 1=ACID-safe; 2=faster, 1s risk
innodb_flush_method              = O_DIRECT   # bypass OS cache; avoids double-buffer
innodb_file_per_table            = ON         # one .ibd file per table
innodb_doublewrite               = ON         # crash-safe page writes (default)

# --- Connections ---
max_connections                  = 500
thread_cache_size                = 50
wait_timeout                     = 600        # idle non-interactive connection TTL
interactive_timeout              = 600

# --- Slow query log ---
slow_query_log                   = 1
slow_query_log_file              = /var/log/mysql-slow.log
long_query_time                  = 1          # seconds; lower in latency-sensitive systems
log_queries_not_using_indexes    = OFF        # enable when diagnosing index gaps

# --- Binary log (required for replication) ---
log-bin                          = mysql-bin
log-bin-index                    = mysql-bin.index
binlog_format                    = ROW        # safest for replication; required for GR
sync_binlog                      = 1          # flush binlog per commit; ACID-safe
expire_logs_days                 = 7

# --- GTID ---
gtid_mode                        = ON
enforce_gtid_consistency         = ON

# --- Network ---
bind-address                     = 127.0.0.1  # restrict to localhost; override for cluster
```

**Key trade-offs:**
- `innodb_flush_log_at_trx_commit=2` improves throughput ~5-10x but risks up to 1s data loss on OS crash — replicas only
- `innodb_dedicated_server=ON` (8.0.30+): auto-sizes buffer pool and redo log — dedicated servers only

---

## 2. GTID-Based Replication Setup

**Why GTID over position-based:** failover does not require knowing the exact binlog file and position. A new replica can auto-position from any member in the topology.

Source adds to my.cnf: `log-bin=mysql-bin`, `binlog-format=ROW`, `sync-binlog=1`, `gtid_mode=ON`, `enforce_gtid_consistency=ON`.

Replicas add: unique `server-id`, `relay-log=relay-mysql-X`, `skip-slave-start`, same GTID vars.

### Create replication user on source
```sql
CREATE USER 'replication_user'@'192.168.2.%' IDENTIFIED BY 'StrongPass#1';
GRANT REPLICATION SLAVE ON *.* TO 'replication_user'@'192.168.2.%';
FLUSH PRIVILEGES;
```

### Configure replica with GTID auto-positioning
```sql
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST='192.168.2.15',
  SOURCE_USER='replication_user',
  SOURCE_PASSWORD='StrongPass#1',
  SOURCE_AUTO_POSITION=1,          -- key: no file/pos needed
  GET_SOURCE_PUBLIC_KEY=1;

START REPLICA;
SHOW REPLICA STATUS\G              -- 8.0.22+ syntax
```

### Verify replication lag
```sql
SHOW REPLICA STATUS\G
-- Check: Seconds_Behind_Source = 0
-- Check: Replica_IO_Running = Yes
-- Check: Replica_SQL_Running = Yes
-- Check: Auto_Position = 1
```

---

## 3. InnoDB Cluster (MySQL 8 AdminAPI)

InnoDB Cluster = Group Replication + MySQL Router + mysqlsh AdminAPI.

### Minimum viable cluster: 3 nodes (quorum requires majority = 2 of 3)

### Bootstrap cluster on primary node
```js
// mysqlsh -u mysqlclusteradmin -p
dba.checkInstanceConfiguration('mysqlclusteradmin@localhost:3306')

var cluster = dba.createCluster("myCluster")

cluster.addInstance('mysqlclusteradmin@mysql-b:3306')
// Choose [C]lone when prompted — copies data from primary

cluster.addInstance('mysqlclusteradmin@mysql-c:3306')

cluster.status()
// "status": "OK" — tolerates 1 failure
```

### Day-2 operations
```js
var cluster = dba.getCluster()        // reconnect to existing cluster
cluster.status()
cluster.status({extended: 1})        // shows fenceSysVars, GTID sets

// Graceful primary switchover
cluster.setPrimaryInstance('mysql-b:3306')

// Add MySQL Router for transparent failover
mysqlrouter --bootstrap mysqlclusteradmin@mysql-a:3306 --user=mysqlrouter
// Router ports: 6446 RW, 6447 RO, 6448 RW X, 6449 RO X, 6450 RW-Split
```

### InnoDB ClusterSet (cross-DC DR)
```js
var cs = dba.createClusterSet('myclusterset')
cs.createReplicaCluster('mysqlclusteradmin@mysql-d:3306', 'mydrcluster')
cs.status({extended: 1})

// Role switch (planned)
cs.setPrimaryCluster('mydrcluster', {dryrun: true})
cs.setPrimaryCluster('mydrcluster')

// Emergency failover (primary unreachable)
cs.forcePrimaryCluster('mydrcluster')

// Recover from complete outage
dba.rebootClusterFromCompleteOutage()
```

---

## 4. Group Replication vs Async Replication

| Criterion | Group Replication (InnoDB Cluster) | Async Replication |
|-----------|-----------------------------------|-------------------|
| Consistency | Synchronous (Paxos-based) | Eventual |
| Write conflicts | Detected and rolled back | Silent divergence risk |
| Failover | Automatic via Router | Manual or orchestrated |
| Overhead | Higher (certification step) | Minimal |
| Min nodes | 3 for HA | 1 source + 1 replica |
| Use case | OLTP HA, no data loss | Read scaling, DR lag acceptable |

**`super_read_only`**: set automatically on Group Replication secondaries. Prevents accidental writes. If you see it in `fenceSysVars` in `cluster.status()`, that secondary is correctly protected.

**When to use async:** large datasets where clone/sync overhead is prohibitive, analytics read replicas, cross-region DR with acceptable lag.

---

## 5. User Security Model — Principle of Least Privilege

```sql
-- Application user: DML only, no schema changes
CREATE USER 'app_user'@'10.0.0.%' IDENTIFIED WITH caching_sha2_password BY 'AppPass#1';
GRANT SELECT, INSERT, UPDATE, DELETE ON myapp.* TO 'app_user'@'10.0.0.%';

-- Migration user: add DDL, revoke after migration
CREATE USER 'migration_user'@'localhost' IDENTIFIED BY 'MigPass#1';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX
  ON myapp.* TO 'migration_user'@'localhost';
-- After migration: DROP USER 'migration_user'@'localhost';

-- Monitoring user: read performance_schema only
CREATE USER 'monitor_user'@'localhost' IDENTIFIED BY 'MonPass#1';
GRANT SELECT ON performance_schema.* TO 'monitor_user'@'localhost';
GRANT PROCESS ON *.* TO 'monitor_user'@'localhost';

-- Replication user: replication only
CREATE USER 'replication_user'@'192.168.%.%' IDENTIFIED BY 'ReplPass#1';
GRANT REPLICATION SLAVE ON *.* TO 'replication_user'@'192.168.%.%';
```

**Authentication defaults:** MySQL 8.0+ uses `caching_sha2_password` by default (server-side cache for performance). `mysql_native_password` deprecated in 8.0.34, removed in 9.0. Never connect application code as `root`.

---

## 6. Network Security

```ini
# /etc/my.cnf
[mysqld]
bind-address              = 127.0.0.1     # local only; for cluster use actual IP
require_secure_transport  = ON            # reject non-TLS connections

# TLS certificate paths
ssl_ca   = /opt/app/certs/ca-cert.pem
ssl_cert = /opt/app/certs/server-cert.pem
ssl_key  = /opt/app/certs/server-key.pem
```

**TLS version support** (MySQL 8.0.28+): TLSv1.2 and TLSv1.3 only (TLSv1 and TLSv1.1 removed).

**Generate production certificates:**
```bash
# Use organisation CA, not MySQL auto-generated certs
openssl req -batch -config config.txt -out hostname.com.csr
# Submit CSR to CA, install returned cert
# Or use mysql_ssl_rsa_setup for dev environments
```

**Enforce X.509 for a user:**
```sql
ALTER USER 'mysqluser'@'%' REQUIRE X509;
```

**SSH tunnel for remote admin (no exposed 3306):**
```bash
ssh -L 3307:localhost:3306 user@db-server
mysql -h 127.0.0.1 -P 3307 -u root -p
```

---

## 7. Audit Logging

MySQL Enterprise Audit (Enterprise Edition only) — avoids the noise of `general_log`.

```ini
# /etc/my.cnf — make persistent
[mysqld]
audit-log = FORCE_PLUS_PERMANENT
```

```bash
# Install (MySQL 8.0.34+)
mysql -u root -p -D mysql < /usr/share/mysql-8.0/audit_log_filter_linux_install.sql
```

```sql
-- Verify plugin active
SELECT PLUGIN_NAME, PLUGIN_STATUS FROM INFORMATION_SCHEMA.PLUGINS
WHERE PLUGIN_NAME LIKE 'audit%';

-- Enable logging for all users (rule-based, default is OFF)
SELECT audit_log_filter_set_filter('log_all', '{ "filter": { "log": true } }');
SELECT audit_log_filter_set_user('%', 'log_all');

-- Audit log location
SELECT @@datadir, @@audit_log_file;  -- default: /var/lib/mysql/audit.log
```

**What to log:** failed logins, DDL statements (CREATE/ALTER/DROP), privilege changes (GRANT/REVOKE). The XML audit log records TIMESTAMP, USER, HOST, COMMAND_CLASS, SQLTEXT.

**Community alternative:** `general_log` captures everything but creates extreme I/O; use only for short troubleshooting windows.

---

## 8. Backup Strategy

### Rule selection by database size

| Size | Tool | Lock behaviour |
|------|------|----------------|
| < 10GB | `mysqldump` | No lock with `--single-transaction` (InnoDB) |
| 10-100GB | `mydumper` | Parallel, consistent snapshot |
| > 100GB / prod | Percona XtraBackup | True hot backup, zero lock |

### mysqldump — safe InnoDB backup
```bash
mysqldump --single-transaction --routines --triggers --events \
  --set-gtid-purged=OFF --all-databases \
  > /backup/full-$(date +%Y%m%d).sql
mysql -u root -p < /backup/full-20260401.sql          # restore
# Encrypted: pipe through gzip | openssl enc -aes-256-cbc -k "$KEY"
```

### mydumper — parallel logical backup
```bash
mydumper --host=localhost --user=root --password="$PASS" \
  --outputdir=/backup/mydumper --rows=50000 --threads=4 -G -E -R
myloader --host=localhost --user=root --password="$PASS" \
  --directory=/backup/mydumper --threads=4 --overwrite-tables
```

### Percona XtraBackup — hot physical backup
```bash
xtrabackup --user=root --password="$PASS" --backup --target-dir=/var/lib/backup/
xtrabackup --backup --target-dir=/var/lib/incr/ --incremental-basedir=/var/lib/backup/
xtrabackup --prepare --target-dir=/var/lib/backup/
xtrabackup --copy-back --target-dir=/var/lib/backup/ && chown -R mysql:mysql /var/lib/mysql
```

XtraBackup records `binlog_pos` in `xtrabackup_info` — use this for PITR after restore.

### 3-2-1 rule applied to MySQL
- **3** copies: primary + replica + offsite backup
- **2** different media: disk + object storage (S3/GCS)
- **1** offsite: separate data center or cloud region

---

## 9. Point-in-Time Recovery (PITR)

```bash
# Step 1: Restore full backup
mysql -u root -p < /backup/full-20260401.sql

# Step 2: Replay binary logs to target datetime
mysqlbinlog \
  --start-datetime="2026-04-01 00:00:00" \
  --stop-datetime="2026-04-01 14:30:00" \
  /var/lib/mysql/binlog.000042 \
  /var/lib/mysql/binlog.000043 \
  | mysql -u root -p

# Alternative: stop at a specific GTID
mysqlbinlog --exclude-gtids="uuid:1-N" binlog.* | mysql -u root -p
```

**Recovery runbook:**
1. Identify failure time from application logs and `SHOW REPLICA STATUS`
2. Restore most recent full backup to target server
3. Identify first binlog file after the backup using `xtrabackup_info` or `--master-data`
4. Replay binlogs up to (but not including) the erroneous transaction
5. Verify row counts and checksums against a known-good replica
6. Point application traffic at restored server

---

## 10. Monitoring Queries (Performance Schema)

```sql
-- Current slow queries (timer_wait in picoseconds; 1s = 1,000,000,000,000ps)
SELECT thread_id, sql_text, timer_wait/1e12 AS wait_seconds
FROM performance_schema.events_statements_current
WHERE timer_wait > 1000000000000
ORDER BY timer_wait DESC;

-- Top slow queries by total latency
SELECT digest_text, count_star, avg_timer_wait/1e9 AS avg_ms,
       sum_timer_wait/1e12 AS total_sec
FROM performance_schema.events_statements_summary_by_digest
ORDER BY sum_timer_wait DESC LIMIT 10;

-- Replication lag
SHOW REPLICA STATUS\G
-- Key field: Seconds_Behind_Source

-- InnoDB buffer pool hit rate (aim for > 99%)
SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool%';
-- Hit rate = Innodb_buffer_pool_read_requests / (read_requests + reads)

-- Lock waits (active transactions holding locks)
SELECT trx_id, trx_state, trx_started, trx_query
FROM information_schema.INNODB_TRX
ORDER BY trx_started;

-- Blocking locks
SELECT r.trx_id waiting_id, r.trx_query waiting_query,
       b.trx_id blocking_id, b.trx_query blocking_query
FROM information_schema.INNODB_TRX b
JOIN information_schema.INNODB_TRX r
  ON b.trx_id = r.trx_wait_started;

-- Memory by user
SELECT user, current_memory FROM sys.user_summary ORDER BY current_memory DESC;

-- Tables with most I/O waits
SELECT object_schema, object_name, sum_timer_wait/1e12 AS total_wait_sec
FROM performance_schema.table_io_waits_summary_by_table
ORDER BY sum_timer_wait DESC LIMIT 10;
```

---

## 11. Table Maintenance

| Operation | Lock | When to use |
|-----------|------|-------------|
| `ANALYZE TABLE t` | Read lock | After bulk DML; refreshes optimizer statistics |
| `OPTIMIZE TABLE t` | Table lock | Reclaim space after large DELETEs — avoid on large tables |
| `CHECK TABLE t EXTENDED` | Read lock | Integrity check after crash or corruption |
| `CHECKSUM TABLE t` | Read lock | Quick comparison checksum |

`OPTIMIZE TABLE` on InnoDB triggers a full recreate+analyze — effectively an `ALTER TABLE`. Use `pt-online-schema-change` or `gh-ost` on large tables to avoid blocking.

---

## 12. Schema Changes in Production

Never run `ALTER TABLE` directly on tables > 1M rows — full table lock for the duration.

```bash
# pt-online-schema-change (Percona Toolkit)
pt-online-schema-change \
  --alter="ADD COLUMN status TINYINT DEFAULT 0" \
  --execute D=myapp,t=orders,u=root,p="$PASS"

# gh-ost (GitHub) — triggers-free, safer on replicas
gh-ost --user=root --password="$PASS" --host=localhost \
  --database=myapp --table=orders \
  --alter="ADD COLUMN status TINYINT DEFAULT 0" --execute
```

Both create a shadow table, copy rows in batches, tail binlogs for live changes, then do an atomic swap.

---

## 13. Connection Pooling

| Option | Use case |
|--------|----------|
| MySQL Router | InnoDB Cluster; automatic RW/RO failover routing |
| ProxySQL | Query routing, read/write split, connection multiplexing |
| PDO persistent | Small PHP apps; risk of stale state between requests |

Each MySQL thread uses ~1-2MB. A server with 16GB MySQL-available RAM supports ~500-800 connections.

```sql
SHOW STATUS LIKE 'Threads_connected';   -- active connections
SHOW STATUS LIKE 'Connection_errors%';  -- refused connections (pool exhaustion)
```

---

## 14. Disaster Recovery Checklist

**Immediate (first 5 min):** `SHOW REPLICA STATUS\G` → verify `Seconds_Behind_Source=0`. InnoDB Cluster auto-fails over via Router; check `cluster.status()`.

**Manual async failover:**
```sql
-- Promote replica to primary
STOP REPLICA;
RESET SLAVE ALL;
SET GLOBAL super_read_only = OFF;

-- Re-point remaining replicas
CHANGE REPLICATION SOURCE TO SOURCE_HOST='new-primary', SOURCE_AUTO_POSITION=1;
START REPLICA;
```

**InnoDB Cluster full outage:**
```js
dba.rebootClusterFromCompleteOutage()
cluster.rejoinInstance('mysql-b:3306')
```

**Accidental DROP / corruption:**
1. `SET GLOBAL super_read_only=ON` on all nodes — stop writes
2. Identify last good GTID from replica binlogs
3. Restore full backup to isolated server; replay binlogs to just before incident
4. `mysqldump --tables --single-transaction db affected_table` → import to prod
5. Verify row counts, re-enable writes

**Critical files to include in backups:** `/etc/my.cnf`, `/var/lib/mysql/auto.cnf` (server UUID), SSL certs, `~/.mylogin.cnf`.

---

## 15. Anti-Patterns to Avoid

- Connecting application code as `root` — use least-privilege app user
- `ALTER TABLE` directly on large tables — use pt-osc or gh-ost
- `general_log=ON` in production — extreme I/O overhead; use slow query log
- `innodb_flush_log_at_trx_commit=0` — data loss on any mysqld crash
- Position-based replication — GTID is mandatory for reliable failover
- Omitting `--single-transaction` from mysqldump — inconsistent backup
- Hard-coding passwords in backup scripts — use `mysql_config_editor`
- `bind-address=0.0.0.0` without firewall — exposes port 3306 to internet
- Never rotating the InnoDB master encryption key — rotate on any suspicion of compromise

---

*Source: Mastering MySQL Administration — High Availability, Security, Performance (Apress, 2024)*
