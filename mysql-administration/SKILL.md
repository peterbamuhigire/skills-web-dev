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
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Expert MySQL 8 administration: replication topology, InnoDB Cluster / Group Replication, security hardening, backup strategies with mysqldump/mydumper/xtrabackup, monitoring with Performance Schema, and production operations. Use when setting up...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `mysql-administration` or would be better handled by a more specific companion skill.
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
| Operability | Replication and backup runbook | Markdown doc per `skill-composition-standards/references/runbook-template.md` covering replication, failover, and restore-test procedure | `docs/data/mysql-runbook.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
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

## Additional Guidance

Extended guidance for `mysql-administration` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `2. GTID-Based Replication Setup`
- `3. InnoDB Cluster (MySQL 8 AdminAPI)`
- `4. Group Replication vs Async Replication`
- `5. User Security Model — Principle of Least Privilege`
- `6. Network Security`
- `7. Audit Logging`
- `8. Backup Strategy`
- `9. Point-in-Time Recovery (PITR)`
- `10. Monitoring Queries (Performance Schema)`
- `11. Table Maintenance`
- `12. Schema Changes in Production`
- `13. Connection Pooling`
- Additional deep-dive sections continue in the reference file.