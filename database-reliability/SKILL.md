---
name: database-reliability
description: "Database reliability engineering: SLOs for databases, operational runbooks, change management, capacity planning, backup verification, incident response, and monitoring strategies for production MySQL. Use when setting up production database operations, defining database SLOs, planning maintenance windows, or responding to database incidents."
---

# Database Reliability Engineering

Source: *Database Reliability Engineering* — Laine Campbell & Charity Majors (O'Reilly, 2017)

## Core Philosophy

Databases are not special snowflakes. Treat every node as cattle: replaceable, automated, and monitored. The DBRE role is engineering, not firefighting. Toil (manual, repetitive, automatable work that scales linearly with growth) is the enemy — eliminate it.

---

## 1. Database SLOs

### Availability Targets

| Tier | SLO | Downtime/Year | Downtime/Week |
|------|-----|---------------|---------------|
| Standard | 99.9% | 8.7 hours | 10.08 minutes |
| High | 99.95% | 4.4 hours | 5.04 minutes |
| Critical | 99.99% | 52 minutes | 1 minute |

**Sample SLO:** 99.9% availability averaged over one week; no single incident >10.08 minutes; downtime declared when >5% of users affected; one annual 4-hour maintenance window (2 weeks notice, <10% users).

### Latency SLOs

Never use averages — they are lossy and hide tail latency. Use percentiles over 1-minute windows at 99% of requests.

```
p50 < 5ms   (pk lookups)  |  p95 < 50ms (indexed queries)
p99 < 200ms (joins/agg)   |  max 500ms  (circuit breaker)
```

### Replication and Connection SLOs

```
Replication lag:     <5s normal | alert 10s | critical 30s
Connections:         <80% of max_connections (alert), >20% headroom required
Slow query rate:     <1% of total queries
```

### Error Budget

Track weekly. 30% consumed by Tuesday → create ticket. 70% consumed with 3+ days left → freeze non-critical deployments. 99.9% SLO = 604.8 seconds budget per week.

```sql
SELECT ROUND(SUM(duration_seconds) / 604.8, 1) AS budget_pct_used
FROM downtime_log WHERE week_start = CURDATE() - INTERVAL WEEKDAY(CURDATE()) DAY;
```

---

## 2. Toil Reduction — What to Automate

| Toil Task | Automation Target |
|-----------|-------------------|
| Manual schema changes | Rolling migration tool with review gate |
| Replica rebuilds | Automated from backup on failure detection |
| Backup execution | Scheduled, self-monitoring, alerting on failure |
| Failover | MHA/Orchestrator automated promotion |
| Connection kill on exhaustion | ProxySQL kill-idle-connections rule |
| Slow query log review | Automated digest to ticketing system |
| Disk space warnings | Auto-purge old partitions or alert-to-expand |

**Rule:** If you do it more than twice a month and it takes >15 minutes, automate it.

---

## 3. Change Management for Databases

### The Expand-Contract Pattern (Zero-Downtime Schema Changes)

Never deploy code and schema changes simultaneously. Use expand-contract:

**Phase 1 — Expand (backward compatible):**
```sql
-- Add column as nullable, no constraints yet
ALTER TABLE orders ADD COLUMN customer_tier VARCHAR(20) NULL;
```

**Phase 2 — Backfill (run in batches, avoid locking):**
```sql
-- Batch backfill to avoid long lock
UPDATE orders SET customer_tier = 'standard'
WHERE customer_tier IS NULL
  AND id BETWEEN ? AND ?
LIMIT 1000;
```

**Phase 3 — Deploy new application code** (now reads/writes new column)

**Phase 4 — Contract (add constraints after code is live):**
```sql
ALTER TABLE orders MODIFY customer_tier VARCHAR(20) NOT NULL DEFAULT 'standard';
```

**Phase 5 — Drop old column** (after confirming old code paths are gone)

### Migration Rules

- Every migration MUST have a rollback (down migration)
- Never rename a column — add new, backfill, drop old
- Never change column type in-place on large tables — use pt-online-schema-change or gh-ost
- Test migrations on a clone of production data before applying
- Apply migrations before deploying code that requires them
- Store migration sequence numbers; never two engineers modifying the same object concurrently

### Change Freeze Windows

| Period | Rule |
|--------|------|
| Friday 3pm – Monday 9am | No schema changes or major config changes |
| Major product launches | 48-hour freeze before and during |
| Incident in progress | No changes until incident resolved |
| Error budget >70% consumed | Freeze non-critical changes |

---

## 4. Backup Verification Runbook

**Key principle:** Replication is NOT a backup — it cascades corruption. RAID is NOT a backup. A backup is only valid after a successful restore test.

### Backup Strategy (Three Tiers)

| Tier | Storage | Retention | Use Case |
|------|---------|-----------|----------|
| Hot | Fast SSD, local/NAS | 7 days full + hourly incremental | Node replacement, rapid failover |
| Warm | Slow block storage / S3 | 30 days full + daily incremental | Application error recovery, forensics |
| Cold | Glacier / offline tape | 1–7 years | Compliance, disaster recovery |

### Backup Verification Runbook

Run weekly on a test instance. Automate and alert on failure.

```bash
# 1. Restore latest backup to test instance
xtrabackup --prepare --apply-log-only --target-dir=/backup/latest/
xtrabackup --copy-back --target-dir=/backup/latest/
chown -R mysql:mysql /var/lib/mysql && systemctl start mysql

# 2. Verify row counts match production (alert if delta >0.1%)
mysql -e "SELECT COUNT(*) FROM orders;" restored_db

# 3. Verify checksums match production
mysql -e "CHECKSUM TABLE orders, users, products;" restored_db

# 4. Log timing and emit metrics
echo "$(date): Restore OK in ${ELAPSED}s" >> /var/log/backup-verify.log
curl -X POST "$METRICS_ENDPOINT" -d "backup.restore.duration=${ELAPSED}"
```

**Alert if:** restore fails, row count delta >0.1%, checksum mismatch, restore duration +50% above baseline.

---

## 5. Monitoring Pyramid

Four layers. Monitor bottom-up but alert top-down (business impact first).

### Layer 1 — Infrastructure

| Metric | Alert Threshold | Critical |
|--------|----------------|---------|
| `disk_usage_percent` | >80% | >90% |
| `disk_iops_utilization` | >70% provisioned | >90% |
| `cpu_usage_percent` | >80% sustained 5min | >95% |
| `memory_used_percent` | >85% | >95% |

### Layer 2 — MySQL Process

```sql
SHOW GLOBAL STATUS LIKE 'Threads_connected';     -- alert if / max_connections > 0.8
SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_read%'; -- hit rate; alert if <95%
SHOW SLAVE STATUS\G  -- Seconds_Behind_Master, Slave_IO_Running, Slave_SQL_Running
```

### Layer 3 — Query

```sql
SHOW GLOBAL STATUS LIKE 'Slow_queries';          -- alert if >1% of Questions
SHOW GLOBAL STATUS LIKE 'Created_tmp_disk_tables'; -- alert if >5% of total tmp tables
SHOW ENGINE INNODB STATUS\G                       -- TRANSACTIONS section: lock waits

-- Top slow queries (performance_schema)
SELECT digest_text, count_star, avg_timer_wait/1e12 AS avg_sec
FROM performance_schema.events_statements_summary_by_digest
ORDER BY avg_timer_wait DESC LIMIT 20;
```

### Layer 4 — Business / Data Health

```sql
-- Data freshness (alert if no new orders in 5 min during business hours)
SELECT MAX(created_at) FROM orders;

-- Row count anomaly (alert if daily delta >3x 30-day rolling stddev)
SELECT table_name, table_rows FROM information_schema.tables
WHERE table_schema = 'production';
```

---

## 6. Alert Fatigue Prevention

### Alerting Decision Matrix

| Condition | Action | Reason |
|-----------|--------|--------|
| SLO budget >70% in <half the period | Page on-call | Imminent SLO breach |
| Replication lag >30 seconds | Page on-call | Data divergence risk |
| `max_connections` >90% | Page on-call | Connection exhaustion seconds away |
| Disk usage >90% | Page on-call | Imminent crash |
| Primary failover occurred | Page on-call | Verify data integrity |
| Slow query rate spike >5x baseline | Create ticket | Degradation, not outage |
| Disk usage 80–90% | Create ticket | Trending to critical |
| Buffer pool hit rate 90–95% | Create ticket | Memory pressure building |
| Replication lag 5–30 seconds | Dashboard only | Normal catch-up |
| CPU 60–80% | Dashboard only | Not yet saturated |

### Multi-Window Burn Rate

Alert when consuming error budget faster than sustainable:

| Window | Burn Rate | Action | Meaning |
|--------|-----------|--------|---------|
| 5 min | >14x | Page immediately | SLO breach in <1 hour |
| 1 hour | >6x | Page on-call | SLO breach in <6 hours |
| 6 hours | >3x | Create ticket | SLO breach in <24 hours |

---

## 7. Capacity Planning

### Data Growth Projection

Run weekly and store results. Project: `days_to_limit = (disk_limit_mb - current_size_mb) / growth_rate_mb_day`.

```sql
SELECT table_schema, table_name,
  ROUND((data_length + index_length) / 1024 / 1024, 2) AS size_mb
FROM information_schema.tables
WHERE table_schema NOT IN ('information_schema','performance_schema','mysql')
ORDER BY size_mb DESC;
```

### When to Scale vs. Shard

| Signal | Action |
|--------|--------|
| Disk >70%, growing >5GB/day | Add storage or archive old data |
| Read IOPS saturated, writes normal | Add read replicas |
| Write throughput saturated | Scale vertically or shard |
| Single table >100GB and growing | Consider partitioning |
| Single table >500GB with heavy writes | Consider sharding |
| CPU consistently >70% | Profile queries first; scale if no low-hanging fruit |
| Connections >80% `max_connections` | Add ProxySQL pooling first |

**The boring database principle:** Prefer vertical scaling and query optimisation over architectural complexity. A well-tuned single primary + replica cluster handles most SaaS workloads under 10TB. Sharding is a last resort.

---

## 8. Incident Response Runbook

### Step 1 — Assess (first 2 minutes)

```sql
SHOW GLOBAL STATUS LIKE 'Threads_connected';  -- connection pressure?
SHOW SLAVE STATUS\G                            -- replication running?
SHOW PROCESSLIST;                              -- what is running?
```

### Step 2 — Immediate Mitigation (first 5 minutes)

```sql
-- Kill long-running blocking queries (>30s, not sleeping)
SELECT id, user, time, state, LEFT(info,100) AS query
FROM information_schema.processlist
WHERE time > 30 AND command != 'Sleep' ORDER BY time DESC;

KILL QUERY <id>;  -- kill query, keep connection
KILL <id>;        -- kill connection

SHOW ENGINE INNODB STATUS\G  -- check TRANSACTIONS for lock waits
```

### Step 3 — Diagnose (5–15 minutes)

```sql
-- Recent slow queries from performance_schema
SELECT digest_text, count_star, avg_timer_wait/1e12 AS avg_sec,
       sum_rows_examined/count_star AS avg_rows_examined
FROM performance_schema.events_statements_summary_by_digest
WHERE last_seen > NOW() - INTERVAL 1 HOUR
ORDER BY avg_timer_wait DESC LIMIT 10;

-- Also check: tail -100 /var/log/mysql/error.log
```

### Step 4 — Failover / Mitigation

```bash
orchestrator-client -c graceful-master-takeover-auto -alias mycluster
# or: masterha_master_switch --conf=/etc/mha/app.conf --master_state=dead
```

### Step 5 — Verify Recovery

```sql
CHECKSUM TABLE orders, users, products;  -- compare to pre-incident baseline
SHOW SLAVE STATUS\G                      -- Seconds_Behind_Master = 0?
CHECK TABLE orders, users EXTENDED;      -- detect corruption
```

### Step 6 — Post-Mortem Template

```
Incident ID | Date | Duration | SLO Impact (minutes) | Severity P1/P2/P3
Timeline: first signal → ack → root cause → mitigate → restore
Root Cause:
Detection Gap (why wasn't this caught earlier?):
Action Items: [ ] short-term (owner, date)  [ ] long-term (owner, date)
What went well | What went poorly
```

---

## 9. Connection Exhaustion Response

```sql
-- Immediate: generate KILL statements for idle connections >60s
SELECT CONCAT('KILL ', id, ';')
FROM information_schema.processlist
WHERE command = 'Sleep' AND time > 60;

-- Short-term: bump max_connections (each connection ~1MB RAM overhead)
SET GLOBAL max_connections = 500;
SHOW GLOBAL STATUS LIKE 'Max_used_connections';
```

**Long-term:** Deploy ProxySQL to pool many app connections into a small number of backend connections (e.g. 1000 app → 50 MySQL). Set `wait_timeout=300` and `interactive_timeout=300` to auto-kill zombie connections.

---

## 10. Replication Failure Recovery

### Identify the Failure

```sql
SHOW SLAVE STATUS\G
-- Key fields:
--   Slave_IO_Running: Yes/No
--   Slave_SQL_Running: Yes/No
--   Last_SQL_Error: error message
--   Seconds_Behind_Master: lag in seconds
--   Retrieved_Gtid_Set / Executed_Gtid_Set (for GTID replication)
```

### Duplicate Key Error (row-based replication)

```sql
-- Use sparingly; skips one event
STOP SLAVE;
SET GLOBAL SQL_SLAVE_SKIP_COUNTER = 1;
START SLAVE;
SHOW SLAVE STATUS\G
```

### GTID-Based Skip (preferred with GTID replication)

```sql
-- Get the failing GTID from Last_SQL_Error
STOP SLAVE;
SET GTID_NEXT='<source_uuid>:<transaction_id>';
BEGIN; COMMIT;  -- inject empty transaction
SET GTID_NEXT='AUTOMATIC';
START SLAVE;
```

### Rebuild Replica from Scratch

```bash
xtrabackup --backup --target-dir=/backup/replica-rebuild/
xtrabackup --prepare --target-dir=/backup/replica-rebuild/
xtrabackup --copy-back --target-dir=/backup/replica-rebuild/
chown -R mysql:mysql /var/lib/mysql

# Start MySQL with replication paused, then configure GTID
mysqld --skip-slave-start &
mysql -e "CHANGE MASTER TO MASTER_HOST='primary', MASTER_AUTO_POSITION=1; START SLAVE;"
mysql -e "SHOW SLAVE STATUS\G"
```

---

## 11. Security Incident Response

**SQL injection detected:** Enable general log, kill sessions from attacking IP, block at firewall, rotate credentials immediately.

```sql
-- Enable audit log
SET GLOBAL general_log = 'ON';
SET GLOBAL general_log_file='/var/log/mysql/general.log';

-- Rotate credentials
ALTER USER 'appuser'@'%' IDENTIFIED BY '<new-strong-password>';
FLUSH PRIVILEGES;

-- Audit for new rogue accounts
SELECT user, host, Super_priv FROM mysql.user
WHERE Super_priv = 'Y' OR File_priv = 'Y'
ORDER BY password_last_changed DESC;

-- Remove unauthorised user
REVOKE ALL PRIVILEGES ON *.* FROM 'suspicious_user'@'%';
DROP USER 'suspicious_user'@'%';
```

**Credentials exposed:** Rotate immediately, audit `mysql.general_log` for that user in past 24 hours, check for new accounts, review privilege escalation.

---

## 12. Planned Maintenance Checklist

**Pre (T-48h):**
- [ ] Notify stakeholders (2 weeks notice required per SLA for planned downtime)
- [ ] Verify backup is complete and tested; rehearse on staging clone; time it
- [ ] Document rollback procedure; designate incident commander

**During:**
- [ ] `SET GLOBAL read_only = ON;` if taking write traffic offline
- [ ] Apply changes incrementally; verify after each step
- [ ] Monitor: `tail -f /var/log/mysql/error.log`

**Post:**
- [ ] `SHOW SLAVE STATUS\G` on all replicas — confirm replication healthy
- [ ] `CHECK TABLE` on modified tables; verify application queries
- [ ] `SET GLOBAL read_only = OFF;` restore normal thresholds; update runbook

---

## 13. Chaos Engineering for Databases

GameDay exercises to test failure modes before they happen in production. Always run on staging first. Have an incident commander. Document findings.

| Exercise | Method | What to Measure |
|----------|--------|-----------------|
| Primary failover | `kill -9 $(pgrep mysqld)` | Detection time, promotion time, data loss |
| Connection saturation | `sysbench --threads=500 --time=60` | Alert trigger time, ProxySQL queue depth |
| Disk fill | `dd if=/dev/zero of=/var/lib/mysql/fill_test bs=1G` | Alert trigger, replica impact (clean up after) |
| Slow query injection | `SELECT COUNT(*) FROM orders WHERE YEAR(created_at)=2023` | Slow query alert fires within SLO threshold |
| Network partition | Block replication port between primary and replica | Replica behaviour, lag accumulation, alerting |

**GameDay cadence:** Quarterly for primary failover. Monthly for connection saturation during low-traffic periods. Never during business-critical events or when error budget is <30% remaining.

---

## 14. Anti-Patterns in Database Operations

| Anti-Pattern | Consequence |
|---|---|
| Using replication as a backup | Corruption and user errors replicate to all nodes — no recovery point |
| Manual ad hoc changes in production | Untested changes, no rollback, untracked in version control |
| Averages in latency monitoring | Hides the tail; p99 of 2 seconds invisible in a 20ms average |
| Deploying code and schema simultaneously | Cannot roll back code without breaking schema, or vice versa |
| Setting `max_connections` very high without pooling | 1000 connections = 1GB+ RAM overhead; starves buffer pool |
| No index on foreign key columns | Every DELETE/UPDATE on parent causes full table scan on child |
| Storing secrets in `mysql.user` with wildcard hosts `%` | Any network path can authenticate; blast radius is entire dataset |
| Testing backups by checking file existence | File can exist but be corrupt; only a successful restore proves backup validity |
| Running `ALTER TABLE` on large tables during peak hours | Table lock or ghost row overhead causes latency spike under load |
| Ignoring replication lag until it is critical | Replica serving stale reads; failover to a lagging replica risks data loss |

---

## Quick Reference: MySQL Ops Commands

```sql
-- Health snapshot (run first on any incident)
SHOW GLOBAL STATUS LIKE 'Threads_connected';
SHOW GLOBAL STATUS LIKE 'Slow_queries';
SHOW SLAVE STATUS\G
SHOW ENGINE INNODB STATUS\G

-- Connection audit by user
SELECT user, host, COUNT(*) AS n FROM information_schema.processlist
GROUP BY user, host ORDER BY n DESC;

-- Table sizes (top 20)
SELECT table_schema, table_name,
  ROUND((data_length+index_length)/1024/1024,1) AS size_mb
FROM information_schema.tables
WHERE table_schema NOT IN ('mysql','information_schema','performance_schema')
ORDER BY size_mb DESC LIMIT 20;

-- Unused indexes (candidates for removal)
SELECT object_schema, object_name, index_name
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE index_name IS NOT NULL AND count_star = 0
  AND object_schema NOT IN ('mysql','performance_schema');
```

---

*Source: Database Reliability Engineering, Campbell & Majors, O'Reilly 2017.*
