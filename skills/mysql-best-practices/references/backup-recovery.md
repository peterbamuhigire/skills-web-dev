# MySQL Backup and Recovery Reference

Based on "Mastering MySQL Administration" by Kumar et al. (Packt, 2024), Chapters 8-9.

---

## Backup Strategy Overview

Every backup strategy answers two questions:

| Metric | Question | Example Target |
|--------|----------|----------------|
| **RPO** (Recovery Point Objective) | How much data can you afford to lose? | 1 hour of transactions |
| **RTO** (Recovery Time Objective) | How long can you afford to be down? | 30 minutes |

RPO determines backup frequency. RTO determines backup method.

### Full vs Incremental vs Differential

| Type | What It Captures | Restore Complexity | Storage Cost |
|------|------------------|--------------------|--------------|
| **Full** | Entire database at a point in time | Low (single file) | High |
| **Incremental** | Changes since last backup (any type) | High (chain of files) | Low |
| **Differential** | Changes since last **full** backup | Medium (full + one diff) | Medium |

**Recommendation:** Full weekly + incremental daily. Add binlog archival for PITR.

### Logical vs Physical Backups

| Aspect | Logical (mysqldump, mydumper) | Physical (XtraBackup, MEB) |
|--------|-------------------------------|----------------------------|
| Format | SQL statements or CSV | Raw data files (ibdata, .ibd) |
| Speed | Slow on large datasets | Fast (file copy) |
| Portability | Cross-platform, cross-version | Same major version, same OS |
| Granularity | Database/table level | Full instance or tablespace |
| Best for | < 50 GB, schema migrations | > 50 GB, disaster recovery |

### Hot vs Warm vs Cold Backups

| Mode | Locking | Engine Support |
|------|---------|----------------|
| **Hot** | No locks, no downtime | InnoDB with `--single-transaction` |
| **Warm** | Global read lock briefly | MyISAM, mixed engines |
| **Cold** | Server stopped | Any engine |

**Rule:** Always use hot backups for InnoDB production databases.

---

## mysqldump (Primary Logical Backup Tool)

### Common Commands

```bash
# Single database — consistent snapshot for InnoDB
mysqldump -u root -p --single-transaction database_name > backup.sql

# All databases with routines, triggers, and events
mysqldump -u root -p \
  --single-transaction --routines --triggers --events \
  --all-databases > full_backup.sql

# Specific tables only
mysqldump -u root -p --single-transaction \
  database_name table1 table2 > tables_backup.sql

# Schema only (no data) — useful for version control
mysqldump -u root -p --no-data database_name > schema_only.sql

# Data only (no schema) — useful for data migration
mysqldump -u root -p --no-create-info database_name > data_only.sql

# Compressed backup
mysqldump -u root -p --single-transaction database_name | gzip > backup.sql.gz

# With binlog position recorded (for PITR baseline)
mysqldump -u root -p --single-transaction --source-data=2 \
  database_name > backup_with_pos.sql
```

### Critical Options Reference

| Option | Purpose | When to Use |
|--------|---------|-------------|
| `--single-transaction` | Consistent snapshot without locking | **Always** for InnoDB |
| `--routines` | Include stored procedures and functions | Always (not included by default) |
| `--triggers` | Include triggers | Default ON since MySQL 5.x |
| `--events` | Include scheduled events | Always (not included by default) |
| `--set-gtid-purged=OFF` | Omit GTID metadata from dump | Non-replication restores |
| `--source-data=2` | Record binlog filename/position as comment | PITR baseline backups |
| `--lock-all-tables` | Global read lock for MyISAM consistency | **Only** for MyISAM tables |
| `--add-drop-database` | Add DROP DATABASE before each CREATE | Full instance restore |
| `--hex-blob` | Dump binary columns as hex | Tables with BLOB/BINARY data |
| `--max-allowed-packet` | Set max packet size for large rows | Tables with large TEXT/BLOB |
| `--column-statistics=0` | Disable column stats queries | MySQL 8.0 dumping older servers |

### Restore from mysqldump

```bash
# Restore full backup
mysql -u root -p < full_backup.sql

# Restore single database
mysql -u root -p database_name < single_db_backup.sql

# Restore compressed backup
gunzip < backup.sql.gz | mysql -u root -p database_name

# Faster restore: disable checks temporarily
mysql -u root -p -e "
  SET GLOBAL foreign_key_checks = 0;
  SET GLOBAL unique_checks = 0;
  SOURCE /path/to/backup.sql;
  SET GLOBAL foreign_key_checks = 1;
  SET GLOBAL unique_checks = 1;
"
```

---

## Percona XtraBackup (Physical Backup -- Open Source)

Best for large databases (> 50 GB). Performs hot backups of InnoDB without locking.

### Full Backup Cycle

```bash
# Take full backup
xtrabackup --backup --user=root --password=secret --target-dir=/backup/full

# Prepare backup (apply redo logs, roll back uncommitted txns)
xtrabackup --prepare --target-dir=/backup/full
```

### Incremental Backup Cycle

```bash
# Full backup as base
xtrabackup --backup --target-dir=/backup/full

# First incremental (based on full)
xtrabackup --backup --target-dir=/backup/inc1 --incremental-basedir=/backup/full

# Second incremental (based on first incremental)
xtrabackup --backup --target-dir=/backup/inc2 --incremental-basedir=/backup/inc1

# Prepare: apply incrementals to full (in order)
xtrabackup --prepare --apply-log-only --target-dir=/backup/full
xtrabackup --prepare --apply-log-only --target-dir=/backup/full \
  --incremental-dir=/backup/inc1
xtrabackup --prepare --target-dir=/backup/full \
  --incremental-dir=/backup/inc2
# Note: omit --apply-log-only on last incremental
```

### Restore from XtraBackup

```bash
systemctl stop mysqld
rm -rf /var/lib/mysql/*                          # DANGEROUS — verify backup first
xtrabackup --copy-back --target-dir=/backup/full
chown -R mysql:mysql /var/lib/mysql
systemctl start mysqld
```

---

## MySQL Enterprise Backup (MEB) -- Enterprise Edition

```bash
# Full backup to single image file
mysqlbackup --user=root --password=secret \
  --backup-image=/backup/full.mbi --backup-dir=/backup/tmp backup-to-image

# Incremental with history-based tracking
mysqlbackup --user=root --password=secret \
  --incremental --incremental-base=history:last_backup \
  --backup-dir=/backup/inc1 backup

# Encrypted backup
mysqlbackup --user=root --password=secret \
  --encrypt --key-file=/secure/backup.key --backup-dir=/backup/encrypted backup

# Cloud backup (S3)
mysqlbackup --user=root --password=secret \
  --cloud-service=s3 --cloud-bucket=my-backups \
  --cloud-object-key=full-backup.mbi --backup-image=- backup-to-image
```

---

## MyDumper/MyLoader (Parallel Logical Backup)

Multi-threaded alternative to mysqldump. Scales linearly with threads.

```bash
# Parallel backup with 4 threads
mydumper --user=root --password=secret --database=production_db \
  --outputdir=/backup/mydumper --threads=4 --compress \
  --triggers --events --routines

# Parallel restore with 4 threads
myloader --user=root --password=secret --database=production_db \
  --directory=/backup/mydumper --threads=4 --overwrite-tables

# Backup specific tables
mydumper --user=root --password=secret --database=production_db \
  --tables-list=orders,order_items,customers \
  --outputdir=/backup/selected_tables --threads=4
```

**Choose MyDumper over mysqldump when:** database > 10 GB, multi-core available,
or you need per-table files for selective restore.

---

## Binary Log for Point-in-Time Recovery (PITR)

Binary logs record every data change. Combined with a full backup, they enable
recovery to any point in time.

### Configuration (my.cnf)

```ini
[mysqld]
log_bin                          = mysql-bin
server_id                        = 1
binlog_format                    = ROW        # Safest for replication and recovery
binlog_expire_logs_seconds       = 604800     # 7 days
sync_binlog                      = 1          # Durability guarantee
innodb_flush_log_at_trx_commit   = 1          # Crash-safe recovery
```

### Managing Binary Logs

```sql
SHOW BINARY LOGS;                                          -- List all binlog files
SHOW BINARY LOG STATUS;                                    -- Current file and position
PURGE BINARY LOGS BEFORE '2024-01-01 00:00:00';           -- Purge by date
PURGE BINARY LOGS TO 'mysql-bin.000010';                   -- Purge by filename
```

### Point-in-Time Recovery Steps

**Scenario:** Database corrupted at 14:30. Last full backup at 02:00.

```bash
# Step 1: Restore full backup (taken at 02:00)
mysql -u root -p < full_backup_0200.sql

# Step 2: Identify binlog position from backup header
head -30 full_backup_0200.sql | grep "CHANGE"
# -- CHANGE MASTER TO MASTER_LOG_FILE='mysql-bin.000005', MASTER_LOG_POS=154;

# Step 3: Apply binlogs up to just before corruption
mysqlbinlog --start-position=154 \
  mysql-bin.000005 mysql-bin.000006 mysql-bin.000007 \
  --stop-datetime="2024-01-15 14:29:59" | mysql -u root -p

# Alternative: stop at a specific position (more precise)
mysqlbinlog --start-position=154 \
  mysql-bin.000005 mysql-bin.000006 \
  --stop-position=98765 | mysql -u root -p
```

### Inspecting Binary Logs

```bash
# Human-readable format
mysqlbinlog --verbose mysql-bin.000005 | less

# Decode ROW events to SQL-like output
mysqlbinlog --verbose --base64-output=DECODE-ROWS mysql-bin.000005

# Filter by database or time range
mysqlbinlog --database=production_db mysql-bin.000005
mysqlbinlog --start-datetime="2024-01-15 12:00:00" \
  --stop-datetime="2024-01-15 14:00:00" mysql-bin.000005
```

---

## Secure Backup Practices

### Credential Management

```bash
# Store credentials securely (NEVER use plaintext in scripts)
mysql_config_editor set --login-path=backup_user \
  --host=localhost --user=backup_admin --password
# Stored encrypted in ~/.mylogin.cnf

# Use in backup scripts
mysqldump --login-path=backup_user --single-transaction --all-databases > backup.sql
```

### Encrypted Backups

```bash
# Encrypt with OpenSSL
mysqldump --login-path=backup_user --single-transaction --all-databases \
  | openssl enc -aes-256-cbc -salt -pass file:/secure/passphrase -out backup.sql.enc

# Decrypt for restore
openssl enc -d -aes-256-cbc -pass file:/secure/passphrase \
  -in backup.sql.enc | mysql --login-path=backup_user
```

### Backup Verification

```bash
# Restore to test server and validate (run monthly minimum)
mysql -u root -p test_restore_db < backup.sql
mysqlcheck -u root -p --check test_restore_db
mysql -u root -p -e "SELECT COUNT(*) FROM test_restore_db.critical_table;"
```

---

## Backup Automation

### Daily Backup Script

```bash
#!/bin/bash
# /usr/local/bin/mysql_daily_backup.sh
BACKUP_DIR="/backup/mysql/daily"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=14
LOG="/var/log/mysql_backup.log"

echo "[$DATE] Starting daily backup..." >> "$LOG"

mysqldump --login-path=backup_user \
  --single-transaction --routines --triggers --events \
  --all-databases | gzip > "${BACKUP_DIR}/full_${DATE}.sql.gz"

if [ $? -eq 0 ]; then
    echo "[$DATE] Backup completed successfully." >> "$LOG"
else
    echo "[$DATE] ERROR: Backup failed!" >> "$LOG"
    exit 1  # Trigger alerting
fi

find "$BACKUP_DIR" -name "*.sql.gz" -mtime +${RETENTION_DAYS} -delete
echo "[$DATE] Old backups cleaned (>${RETENTION_DAYS} days)." >> "$LOG"
```

```bash
# Cron schedule
0 2 * * 1-6 /usr/local/bin/mysql_daily_backup.sh
0 1 * * 0   /usr/local/bin/mysql_weekly_full_backup.sh
```

### Retention Policy

| Tier | Frequency | Retention | Storage |
|------|-----------|-----------|---------|
| Daily incremental | Every night | 14 days | Local SSD |
| Weekly full | Every Sunday | 8 weeks | Local + remote |
| Monthly archive | 1st of month | 12 months | Off-site / cloud |

---

## Recovery Procedures

### Procedure 1: Full Restore from mysqldump

```bash
gunzip -t backup.sql.gz                                    # 1. Verify integrity
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS target_db;"  # 2. Create DB
gunzip < backup.sql.gz | mysql -u root -p target_db        # 3. Restore
mysql -u root -p -e "SELECT COUNT(*) FROM target_db.orders;"   # 4. Verify
```

### Procedure 2: Full + Incremental Restore (XtraBackup)

```bash
xtrabackup --prepare --apply-log-only --target-dir=/backup/full
xtrabackup --prepare --apply-log-only --target-dir=/backup/full \
  --incremental-dir=/backup/inc1
xtrabackup --prepare --target-dir=/backup/full --incremental-dir=/backup/inc2
systemctl stop mysqld && rm -rf /var/lib/mysql/*
xtrabackup --copy-back --target-dir=/backup/full
chown -R mysql:mysql /var/lib/mysql && systemctl start mysqld
```

### Procedure 3: Point-in-Time Recovery (Binlog)

```bash
mysql -u root -p < full_backup.sql                         # 1. Restore base
head -50 full_backup.sql | grep -i "MASTER_LOG"            # 2. Find binlog pos
mysqlbinlog --verbose mysql-bin.000010 | grep -B5 "DROP"   # 3. Find bad event
mysqlbinlog --start-position=154 \
  mysql-bin.000008 mysql-bin.000009 mysql-bin.000010 \
  --stop-position=56789 | mysql -u root -p                 # 4. Replay to safe point
```

### Procedure 4: Single Table Restore

```bash
# From mysqldump: extract one table
sed -n '/^-- Table structure for table `orders`/,/^-- Table structure for table `/p' \
  full_backup.sql > orders_only.sql
mysql -u root -p database_name < orders_only.sql

# From MyDumper: restore single table
myloader --user=root --password=secret --database=production_db \
  --directory=/backup/mydumper --tables-list=orders --threads=2 --overwrite-tables
```

---

## Backup Checklist

### Setup

- [ ] Binary logging enabled (`log_bin`, `server_id`)
- [ ] `binlog_format = ROW` and `sync_binlog = 1` configured
- [ ] `innodb_flush_log_at_trx_commit = 1` for durability
- [ ] Dedicated backup user with minimal privileges created
- [ ] Credentials stored via `mysql_config_editor` (no plaintext)

### Execution

- [ ] Full backup runs on schedule (weekly minimum)
- [ ] Incremental or binlog archival runs daily
- [ ] Backup scripts check exit codes and alert on failure
- [ ] Backups are compressed and encrypted at rest

### Verification

- [ ] Restore tested on non-production server monthly
- [ ] Row counts compared after test restore
- [ ] Binary log continuity verified (no gaps)

### Storage and Retention

- [ ] Backups on separate disk/volume from data
- [ ] Off-site copy maintained (cloud, remote datacenter)
- [ ] Retention policy enforced with automatic purge

### Documentation

- [ ] RPO and RTO targets documented and agreed upon
- [ ] Recovery procedures written, tested, and accessible to on-call team

---

## Troubleshooting

### Common Backup Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Access denied; need RELOAD privilege` | Missing privileges | `GRANT RELOAD, PROCESS, LOCK TABLES, REPLICATION CLIENT ON *.* TO 'backup_user'@'localhost';` |
| `Got packet bigger than max_allowed_packet` | Large BLOB/TEXT rows | Add `--max-allowed-packet=512M` |
| `Lock wait timeout exceeded` | Long-running transaction | Use `--single-transaction` or schedule during low traffic |
| `Unknown table 'column_statistics'` | MySQL 8 client, older server | Add `--column-statistics=0` |
| `GTID_PURGED can only be set when empty` | GTID dump to non-empty server | Use `--set-gtid-purged=OFF` or `RESET MASTER` first |
| `Disk full` during backup | Insufficient storage | Monitor disk; compress inline with gzip pipe |

### Common Restore Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Foreign key constraint fails` | Tables restored out of order | Add `SET FOREIGN_KEY_CHECKS=0;` at top of dump |
| Restore extremely slow | Indexes rebuilt per row | `ALTER TABLE t DISABLE KEYS;` before load |
| `Duplicate entry` errors | Restoring into existing data | Use `--add-drop-table` or truncate first |
| Binlog replay skips events | `--database` filter mismatch | Ensure `USE db;` in binlog; use `--rewrite-db` |

### Backup User Privileges (Minimum Required)

```sql
CREATE USER 'backup_admin'@'localhost' IDENTIFIED BY 'strong_password_here';

GRANT SELECT, SHOW VIEW, TRIGGER, LOCK TABLES,
      RELOAD, PROCESS, REPLICATION CLIENT, EVENT
  ON *.* TO 'backup_admin'@'localhost';

-- For XtraBackup, also grant:
GRANT BACKUP_ADMIN ON *.* TO 'backup_admin'@'localhost';

FLUSH PRIVILEGES;
```

---

*Reference: Kumar et al., "Mastering MySQL Administration" (Packt, 2024), Ch. 8-9.*