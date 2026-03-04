# MySQL Database Skill Design

**Date:** 2026-03-04
**Sources:** Efficient MySQL Performance (Nichter), Mastering MySQL Administration (Kumar et al.), Leveling Up with SQL (Simon)

## Problem

Existing `mysql-best-practices` skill covers basic schema design and multi-tenant patterns but lacks:
- Deep query performance analysis (EXPLAIN mastery, query metrics, profiling)
- InnoDB internals (buffer pool, B-tree behavior, page flushing)
- Advanced indexing (covering indexes, ICP, leftmost prefix deep dive)
- Transaction isolation deep dive (gap locks, next-key locks, MVCC, deadlocks)
- High availability (replication, InnoDB Cluster, failover)
- Security hardening (TDE, SSL/TLS, audit, firewall, RBAC)
- Advanced SQL patterns (window functions, CTEs, recursive queries, pivots)
- Comprehensive server tuning (my.cnf configuration)
- Backup and recovery strategies
- Sharding patterns

## Solution

### Replace `mysql-best-practices/SKILL.md` (~490 lines)

Complete rewrite incorporating content from all three books. Covers:

| Section | Topics |
|---------|--------|
| Schema Design | Data types, normalization, denormalization, character set, InnoDB |
| Indexing | ESR, leftmost prefix, covering indexes, ICP, access types |
| Query Performance | EXPLAIN, query metrics, optimization workflow, anti-patterns |
| Security | Users, privileges, TDE, SSL, parameterized queries, tenant isolation |
| Transactions | Isolation levels, gap/next-key locks, deadlock prevention, MVCC |
| Advanced SQL | CTEs, window functions, aggregation (ROLLUP), recursive queries |
| Server Tuning | Buffer pool, redo log, critical my.cnf variables |
| Operations | Backup, monitoring, replication basics, migrations |

### 8 Reference Documents (`references/`)

| File | Content | Source |
|------|---------|--------|
| `query-performance.md` | Query response time, 9 essential metrics, profiling workflow, query load | Nichter Ch1,4 |
| `indexing-deep-dive.md` | B-tree internals, leftmost prefix, ICP, covering indexes, all access types | Nichter Ch2 |
| `server-tuning-mycnf.md` | 70+ metrics in 11 spectrums, buffer pool, redo log, complete my.cnf template | Nichter Ch6, Kumar Ch11 |
| `security-hardening.md` | TDE, SSL/TLS, RBAC, audit, firewall, post-install hardening, authentication | Kumar Ch10 |
| `high-availability.md` | Replication (binlog/GTID), InnoDB Cluster/ClusterSet, failover, lag mitigation | Nichter Ch7, Kumar Ch5-6 |
| `advanced-sql-patterns.md` | Window functions, CTEs, recursive queries, pivots, ROLLUP/CUBE, subqueries | Simon Ch5,7-9 |
| `backup-recovery.md` | mysqldump, XtraBackup, MEB, point-in-time recovery, backup strategies | Kumar Ch8-9 |
| `transaction-locking.md` | MVCC, gap/next-key locks, isolation levels, deadlocks, undo log/HLL | Nichter Ch8 |

### Keep Existing References

- `stored-procedures.sql` — Still valid
- `triggers.sql` — Still valid
- `partitioning.sql` — Still valid

## Implementation Order

1. Replace `mysql-best-practices/SKILL.md` with comprehensive rewrite
2. Create `references/query-performance.md`
3. Create `references/indexing-deep-dive.md`
4. Create `references/server-tuning-mycnf.md`
5. Create `references/security-hardening.md`
6. Create `references/high-availability.md`
7. Create `references/advanced-sql-patterns.md`
8. Create `references/backup-recovery.md`
9. Create `references/transaction-locking.md`
10. Update `CLAUDE.md` and `README.md`
