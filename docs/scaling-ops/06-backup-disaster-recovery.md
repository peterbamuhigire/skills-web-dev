# Backup & Disaster Recovery

**MySQL backup strategy, Backblaze B2 storage, restore procedures, RTO/RPO**

---

## The Non-Negotiable Rule

A backup you have never restored is not a backup. It is a hope.

Test a full restore every quarter. Document the time it takes. Make it a routine,
not a panic response.

---

## Recovery Targets

| Metric | Definition | Target |
|--------|-----------|--------|
| RTO (Recovery Time Objective) | How long to restore service after failure | < 4 hours |
| RPO (Recovery Point Objective) | Maximum data loss acceptable | < 1 hour |

To achieve RPO < 1 hour: daily dumps + binary logs (point-in-time recovery).
To achieve RTO < 4 hours: documented restore procedure + tested scripts.

---

## MySQL Backup Strategy

### Layer 1 — Daily Full Dump (mysqldump)

```bash
#!/bin/bash
# /srv/scripts/mysql-backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/srv/backups/mysql"
B2_BUCKET="your-bucket-name"
RETENTION_DAYS=30

mkdir -p "$BACKUP_DIR"

# Dump all databases (or list specific ones)
mysqldump \
    --user=backup_user \
    --password="$MYSQL_BACKUP_PASSWORD" \
    --all-databases \
    --single-transaction \
    --routines \
    --triggers \
    --flush-logs \
    --hex-blob \
    | gzip > "$BACKUP_DIR/full_${DATE}.sql.gz"

# Upload to Backblaze B2
/usr/local/bin/b2 upload-file \
    "$B2_BUCKET" \
    "$BACKUP_DIR/full_${DATE}.sql.gz" \
    "mysql/daily/full_${DATE}.sql.gz"

# Delete local copies older than 7 days (keep recent local + remote)
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: full_${DATE}.sql.gz"
```

Create dedicated backup user with minimal privileges:
```sql
CREATE USER 'backup_user'@'localhost' IDENTIFIED BY 'strong-password';
GRANT SELECT, RELOAD, LOCK TABLES, REPLICATION CLIENT, SHOW VIEW,
      EVENT, TRIGGER ON *.* TO 'backup_user'@'localhost';
FLUSH PRIVILEGES;
```

Schedule via cron:
```bash
# crontab -e
0 2 * * * /srv/scripts/mysql-backup.sh >> /var/log/mysql-backup.log 2>&1
```

### Layer 2 — Binary Log Backups (Point-in-Time Recovery)

Enable binary logging in `/etc/mysql/mysql.conf.d/mysqld.cnf`:

```ini
[mysqld]
log_bin = /var/log/mysql/mysql-bin.log
binlog_expire_logs_seconds = 604800  # 7 days
max_binlog_size = 100M
server-id = 1
```

Back up binary logs hourly:
```bash
#!/bin/bash
# /srv/scripts/binlog-backup.sh
DATE=$(date +%Y%m%d_%H%M)
BINLOG_DIR="/var/log/mysql"
B2_BUCKET="your-bucket-name"

# Flush and rotate binary logs
mysql -u backup_user -p"$MYSQL_BACKUP_PASSWORD" -e "FLUSH LOGS;"

# Upload recent binary logs to B2
for f in $(ls -t $BINLOG_DIR/mysql-bin.* | tail -5); do
    /usr/local/bin/b2 upload-file \
        "$B2_BUCKET" "$f" \
        "mysql/binlogs/$(basename $f)_${DATE}"
done
```

```bash
# crontab -e
0 * * * * /srv/scripts/binlog-backup.sh >> /var/log/binlog-backup.log 2>&1
```

---

## Backblaze B2 Setup

### Install B2 CLI

```bash
pip3 install b2
b2 authorize-account YOUR_KEY_ID YOUR_APP_KEY
```

### Bucket structure

```
your-studio-backups/
├── mysql/
│   ├── daily/          ← Full mysqldump files (30-day retention)
│   └── binlogs/        ← Binary logs (7-day retention)
├── medic8/             ← Healthcare data (separate bucket, 5-year retention)
│   ├── mysql/
│   └── files/
└── uploaded-files/     ← User uploads synced from VPS local storage
```

**Use separate buckets for healthcare vs non-healthcare data.**
This simplifies compliance (different retention policies, different access keys).

### Lifecycle Rules (set in B2 console)

- `mysql/daily/`: delete files older than 30 days
- `mysql/binlogs/`: delete files older than 7 days
- `medic8/mysql/`: delete files older than 5 years (compliance retention)
- `uploaded-files/`: no automatic deletion

---

## File Backup — Syncing User Uploads

If not yet on B2 (still storing files locally on VPS):

```bash
#!/bin/bash
# /srv/scripts/files-backup.sh
# Sync uploaded files to B2

b2 sync \
    /srv/uploads/ \
    b2://your-studio-backups/uploaded-files/ \
    --threads 10 \
    --compareVersions size
```

Schedule to run every 15 minutes:
```bash
# crontab -e
*/15 * * * * /srv/scripts/files-backup.sh >> /var/log/files-backup.log 2>&1
```

Once on B2 properly, this sync is replaced by direct B2 writes from the app.

---

## Hetzner Snapshot Backups

In addition to MySQL dumps, use Hetzner's built-in server snapshots:

- Enable automatic backups in Hetzner console (€0.012/GB/month — typically €0.50–1.00/month)
- Keeps last 7 daily snapshots
- Restores an entire server to a known-good state in ~15 minutes
- **Use case:** OS corruption, bad deployment, hardware failure

Snapshots complement mysqldump — they restore the whole server; mysqldump restores just data.

---

## Restore Procedures

### Scenario 1 — Single Database Restore (Most Common)

```bash
# Download backup from B2
b2 download-file-by-name your-studio-backups mysql/daily/full_20260408_020001.sql.gz /tmp/restore.sql.gz

# Decompress
gunzip /tmp/restore.sql.gz

# Restore specific database only
mysql -u root -p target_database < /tmp/restore.sql

# Or restore all databases
mysql -u root -p < /tmp/restore.sql
```

### Scenario 2 — Point-in-Time Recovery

Restore to a specific point between two full backups:

```bash
# 1. Restore the last full dump before the target time
mysql -u root -p < /tmp/restore_full.sql

# 2. Apply binary logs up to the target timestamp
mysqlbinlog \
    --start-datetime="2026-04-08 02:00:00" \
    --stop-datetime="2026-04-08 14:30:00" \
    /tmp/mysql-bin.000123 \
    /tmp/mysql-bin.000124 \
    | mysql -u root -p

# This replays all transactions between backup and target time
```

### Scenario 3 — Full Server Failure

1. Provision new Hetzner VPS (2–5 minutes)
2. Restore from Hetzner snapshot OR run server setup from scratch using `05-security-hardening.md`
3. Install MySQL, restore from mysqldump (`< 30 minutes`)
4. Apply binary logs for point-in-time recovery (`< 30 minutes`)
5. Update DNS / Cloudflare to point to new server IP (`< 5 minutes`, propagates in 60 seconds with Cloudflare)
6. Verify application is running
7. Total: **< 2 hours** (well within 4-hour RTO target)

---

## Quarterly Restore Test Procedure

Run this drill every 3 months. Document the results.

```
Date: ____________
Tested by: ____________
Backup used: ____________ (date of backup file)
Target database: ____________

Steps:
[ ] 1. Download backup from B2 to staging server
[ ] 2. Restore to staging MySQL instance
[ ] 3. Verify row counts match (SELECT COUNT(*) on key tables)
[ ] 4. Verify data integrity (spot-check 5 records)
[ ] 5. Verify application runs against restored DB

Time taken: ____________
Issues found: ____________
Actions taken: ____________

Result: PASS / FAIL
```

If it fails, fix the backup process before the next production incident.

---

## Alert When Backups Fail

```bash
#!/bin/bash
# Add to end of mysql-backup.sh

if [ $? -ne 0 ]; then
    # Send alert (use curl to your alerting webhook)
    curl -X POST "https://hooks.slack.com/services/YOUR/WEBHOOK" \
        -H 'Content-type: application/json' \
        --data '{"text":"ALERT: MySQL backup FAILED on production VPS!"}'
fi
```

Or use email:
```bash
echo "MySQL backup failed at $(date)" | mail -s "BACKUP FAILURE" your@email.com
```

A silent backup failure is worse than a known failure — you only discover it
when you need to restore and find nothing there.
