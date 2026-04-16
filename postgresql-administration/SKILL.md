---
name: postgresql-administration
description: PostgreSQL DBA operations sourced from "Introduction to PostgreSQL for
  the Data Professional" (Booz & Fritchey, 2024). Covers backup strategies (pg_dump,
  pg_basebackup, WAL archiving, PITR), replication (streaming physical, logical, replication
  slots), high availability, monitoring (pg_stat_activity, pg_stat_user_tables, error
  logs, cumulative stats system), cloud PaaS options (AWS RDS/Aurora, Azure, GCP),
  and zero-downtime schema changes. Companion to postgresql-performance and postgresql-fundamentals.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# PostgreSQL Administration

<!-- dual-compat-start -->
## Use When

- PostgreSQL DBA operations sourced from "Introduction to PostgreSQL for the Data Professional" (Booz & Fritchey, 2024). Covers backup strategies (pg_dump, pg_basebackup, WAL archiving, PITR), replication (streaming physical, logical, replication slots), high availability, monitoring (pg_stat_activity, pg_stat_user_tables, error logs, cumulative stats system), cloud PaaS options (AWS RDS/Aurora, Azure, GCP), and zero-downtime schema changes. Companion to postgresql-performance and postgresql-fundamentals.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `postgresql-administration` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
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
| Operability | Cluster and backup runbook | Markdown doc per `skill-composition-standards/references/runbook-template.md` covering replication, vacuum, and restore-test procedure | `docs/data/postgres-runbook.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
## Backup Strategy

### Choosing the Right Mechanism

| Mechanism | Tool | Use Case | Restore Time |
|---|---|---|---|
| SQL dump | `pg_dump` | Single database, schema-level portability | Medium (replay all SQL) |
| File system | `pg_basebackup` | Full cluster backup, base for PITR | Fast (file copy) |
| WAL archiving + PITR | continuous archiving | Zero data loss, point-in-time recovery | Varies |
| Cloud managed | AWS/Azure/GCP native | Managed HA, automated backups | Per-provider |

### pg_dump — Logical Backup

```bash
# Custom format (recommended — allows parallel restore and selective restore)
pg_dump -U postgres -d mydb -F c -f mydb.dump

# Plain SQL (portable, human-readable)
pg_dump -U postgres -d mydb -F p -f mydb.sql

# Compressed plain SQL
pg_dump -U postgres -d mydb | gzip > mydb.sql.gz

# Schema only (no data)
pg_dump -U postgres -d mydb --schema-only -F c -f mydb_schema.dump

# Specific tables
pg_dump -U postgres -d mydb -t orders -t order_items -F c -f orders.dump

# All databases (cluster dump)
pg_dumpall -U postgres -f cluster.sql

# Backup with connection string
pg_dump "postgresql://user:pass@host:5432/mydb" -F c -f mydb.dump
```

### pg_restore — Logical Restore

```bash
# Restore custom format
pg_restore -U postgres -d mydb -F c mydb.dump

# Parallel restore (faster for large databases)
pg_restore -U postgres -d mydb -F c -j 4 mydb.dump

# Restore to a new database
createdb -U postgres newdb
pg_restore -U postgres -d newdb -F c mydb.dump

# Restore single table
pg_restore -U postgres -d mydb -F c -t orders mydb.dump

# Plain SQL restore
psql -U postgres -d mydb -f mydb.sql
```

### pg_basebackup — Physical Backup

```bash
# Full cluster backup (used as base for streaming replication or PITR)
pg_basebackup -h localhost -U replicator -D /backup/base -P -Xs -R

# With WAL streaming included
pg_basebackup -h localhost -U replicator -D /backup/base \
    --checkpoint=fast --wal-method=stream --progress

# Compressed
pg_basebackup -h localhost -U replicator -D /backup/base \
    --format=tar --compress=9 --wal-method=fetch
```

### WAL Archiving + Point-In-Time Recovery (PITR)

```ini
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /archive/wal/%f'
# Or with AWS S3:
# archive_command = 'aws s3 cp %p s3://my-bucket/wal/%f'
restore_command = 'cp /archive/wal/%f %p'
```

```bash
# Take a base backup
pg_basebackup -D /var/lib/postgresql/pitr_base -Xs -P -R

# Create recovery target file (postgresql.conf or recovery.conf pre-v12)
# PostgreSQL 12+: add to postgresql.conf
recovery_target_time = '2026-04-07 14:30:00 UTC'
recovery_target_action = 'promote'
```

```bash
# Restore procedure:
# 1. Stop PostgreSQL
systemctl stop postgresql

# 2. Replace data directory with base backup
rm -rf /var/lib/postgresql/data
cp -a /backup/base /var/lib/postgresql/data

# 3. Ensure recovery.signal exists (PostgreSQL 12+)
touch /var/lib/postgresql/data/recovery.signal

# 4. Start — PostgreSQL replays WAL to the target time
systemctl start postgresql
```

## Replication

### Streaming Replication (Physical — Read Replica)

**Primary server setup:**

```ini
# postgresql.conf
wal_level = replica
max_wal_senders = 5
wal_keep_size = 1GB   # keep WAL for replicas that fall behind
```

```sql
-- Create replication role
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'repl_pass';
```

```
# pg_hba.conf (add entry for replica)
host  replication  replicator  192.168.1.0/24  scram-sha-256
```

**Standby server setup:**

```bash
# Create base backup on standby
pg_basebackup -h primary_host -U replicator -D $PGDATA -P -Xs -R
# -R writes postgresql.auto.conf with primary_conninfo and standby.signal

systemctl start postgresql   # starts as hot standby (read-only)
```

**Monitoring replication:**

```sql
-- On primary
SELECT client_addr, state, sent_lsn, write_lsn, flush_lsn, replay_lsn,
       (sent_lsn - replay_lsn) AS replication_lag_bytes
FROM pg_stat_replication;

-- On standby
SELECT pg_is_in_recovery();   -- returns true on standby
SELECT pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn();
```

### Logical Replication

Replicates specific tables/operations. Works across major versions and between different schemas.

**Publisher (source):**

```ini
# postgresql.conf
wal_level = logical
```

```sql
-- Create publication
CREATE PUBLICATION orders_pub FOR TABLE orders, order_items;
-- Or all tables:
CREATE PUBLICATION all_pub FOR ALL TABLES;
```

**Subscriber (destination — table must exist):**

```sql
-- Create subscription
CREATE SUBSCRIPTION orders_sub
    CONNECTION 'host=primary_host port=5432 dbname=mydb user=replicator password=repl_pass'
    PUBLICATION orders_pub;

-- Monitor
SELECT * FROM pg_stat_subscription;

-- Drop subscription
DROP SUBSCRIPTION orders_sub;
```

### Replication Slots

Replication slots ensure WAL is retained until a subscriber has consumed it. Risk: if a subscriber goes down, WAL accumulates and disk can fill.

```sql
-- Physical slot (for streaming replication)
SELECT pg_create_physical_replication_slot('replica_slot');

-- Logical slot
SELECT pg_create_logical_replication_slot('analytics_slot', 'pgoutput');

-- Monitor slot lag (CRITICAL — alert if > threshold)
SELECT slot_name, active, pg_size_pretty(
    pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)
) AS lag
FROM pg_replication_slots;

-- Drop an inactive slot to free WAL
SELECT pg_drop_replication_slot('analytics_slot');
```

## Monitoring

### Active Queries and Locks

```sql
-- Long-running queries
SELECT pid, age(clock_timestamp(), query_start) AS duration, usename, state, query
FROM pg_stat_activity
WHERE state != 'idle' AND query NOT ILIKE '%pg_stat_activity%'
ORDER BY duration DESC;

-- Cancel a query (graceful)
SELECT pg_cancel_backend(pid);

-- Terminate a connection (forceful)
SELECT pg_terminate_backend(pid);

-- Blocking locks
SELECT blocked.pid, blocked.query, blocking.pid AS blocking_pid, blocking.query AS blocking_query
FROM pg_stat_activity blocked
JOIN pg_stat_activity blocking ON blocking.pid = ANY(pg_blocking_pids(blocked.pid))
WHERE cardinality(pg_blocking_pids(blocked.pid)) > 0;
```

### Table and Index Statistics

```sql
-- Table health overview
SELECT relname,
       n_live_tup, n_dead_tup,
       last_vacuum, last_autovacuum,
       last_analyze, last_autoanalyze,
       seq_scan, idx_scan
FROM pg_stat_user_tables ORDER BY n_dead_tup DESC;

-- Database size
SELECT pg_size_pretty(pg_database_size(current_database()));

-- Table sizes
SELECT relname, pg_size_pretty(pg_total_relation_size(oid)) AS total_size
FROM pg_class WHERE relkind IN ('r', 'm')
ORDER BY pg_total_relation_size(oid) DESC LIMIT 20;

-- Index sizes and usage
SELECT indexrelname, idx_scan,
       pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes ORDER BY pg_relation_size(indexrelid) DESC;
```

### Error Logs

```ini
# postgresql.conf — structured logging
log_destination = 'csvlog'
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_size = 100MB
log_min_duration_statement = 1000   # log queries taking > 1s
log_lock_waits = on                 # log lock waits
log_checkpoints = on                # log checkpoint stats
log_connections = on
log_disconnections = on
```

### pg_stat_statements — Top Queries

```sql
-- Requires: shared_preload_libraries = 'pg_stat_statements' in postgresql.conf

SELECT query,
       calls,
       ROUND(total_exec_time::numeric, 2) AS total_ms,
       ROUND(mean_exec_time::numeric, 2) AS avg_ms,
       rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC LIMIT 20;
```

## Zero-Downtime Schema Changes

### Safe Operations

```sql
-- Adding nullable column — instant (PostgreSQL 11+: even with DEFAULT)
ALTER TABLE orders ADD COLUMN notes TEXT;

-- Adding index concurrently — no table lock
CREATE INDEX CONCURRENTLY orders_customer_idx ON orders (customer_id);

-- Dropping an index concurrently
DROP INDEX CONCURRENTLY orders_customer_idx;
```

### Risky Operations and Mitigations

```sql
-- RISKY: adding NOT NULL column on large table (full rewrite pre-PG 11)
-- SAFE pattern (expand-contract):

-- Step 1: Add nullable with default
ALTER TABLE orders ADD COLUMN priority TEXT DEFAULT 'normal';

-- Step 2: Backfill (batched)
DO $$
DECLARE batch_size INT := 1000;
BEGIN
    LOOP
        UPDATE orders SET priority = 'normal' WHERE priority IS NULL LIMIT batch_size;
        EXIT WHEN NOT FOUND;
        PERFORM pg_sleep(0.1);  -- throttle
    END LOOP;
END $$;

-- Step 3: Add constraint (validate without locking — PostgreSQL 12+)
ALTER TABLE orders ADD CONSTRAINT orders_priority_not_null
    CHECK (priority IS NOT NULL) NOT VALID;

ALTER TABLE orders VALIDATE CONSTRAINT orders_priority_not_null;

-- RISKY: renaming a column referenced by application code
-- SAFE: add new column, dual-write, migrate, drop old column
```

## Cloud PostgreSQL (PaaS)

| Provider | Service | Notes |
|---|---|---|
| **AWS** | RDS PostgreSQL | Managed, automated backups, Multi-AZ HA |
| **AWS** | Aurora PostgreSQL | Higher throughput, up to 15 read replicas, global tables |
| **Azure** | Azure Database for PostgreSQL | Flexible Server preferred over Single Server |
| **GCP** | Cloud SQL for PostgreSQL | HA via regional failover, Cloud Spanner for global scale |
| **Self-hosted** | Supabase, Neon, Timescale Cloud | PostgreSQL with extras (edge functions, branching) |

### Cloud Considerations

- Extension availability varies — check before committing to pgvector, PostGIS
- `pg_hba.conf` managed via UI/API — use SSL required connections
- `max_connections` is limited — always use PgBouncer or built-in pooling
- Automated backups handle pg_dump/PITR — verify retention period
- Major version upgrades via blue/green deployment or `pg_upgrade`

## Mandatory Rules

1. **Test backups with restores** — an untested backup is not a backup
2. **Monitor replication slot lag** — unmonitored slots can fill disk overnight
3. **Use `CONCURRENTLY` for index operations** — always in production
4. **`scram-sha-256` in pg_hba.conf** — never `md5` or `trust` for network connections
5. **Log slow queries** — `log_min_duration_statement = 1000` minimum
6. **Autovacuum tuned per table** — high-churn tables need lower thresholds
7. **WAL archiving before PITR** — ensure `archive_command` is reliable

## Anti-Patterns

- `pg_dump` as the only backup strategy for production — no PITR capability
- Replication slots without lag monitoring — silent disk exhaustion
- `VACUUM FULL` during business hours — acquires exclusive lock, blocks all DML
- Adding `NOT NULL` constraint on large tables without `NOT VALID` + `VALIDATE` pattern
- Connecting as `postgres` superuser from application — always use restricted role
- No connection pooling — PostgreSQL has per-connection overhead; use PgBouncer
- Ignoring `pg_stat_statements` — flying blind on query performance
