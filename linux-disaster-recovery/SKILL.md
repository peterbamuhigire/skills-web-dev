---
name: linux-disaster-recovery
description: Restore from GPG-encrypted backups on Ubuntu/Debian servers. Covers MySQL database restore (single DB or full), app file restore, and emergency recovery checklist. Backups are AES256 GPG encrypted, stored locally and on Google Drive via rclone. Always confirms before any destructive restore.
---
# Disaster Recovery

**Always confirm before restoring.** A restore overwrites existing data.

---

## Step 1: Assess First

```bash
# Is this a service crash (restart only) or actual data loss?
sudo systemctl status nginx mysql postgresql php8.3-fpm

# When did it happen?
sudo journalctl --since "2 hours ago" | grep -iE "error|fail|crash" | head -20
```

Service crash → restart it (`linux-service-management`), no restore needed.
Data loss/corruption → proceed below.

## Step 2: Find The Right Backup

```bash
# Local backups (7-day retention)
ls -lth ~/backups/mysql/*.gpg 2>/dev/null | head -10

# Google Drive (3-day retention for MySQL)
rclone ls gdrive:<backup-folder> 2>/dev/null | sort | tail -10

# If rclone token expired:
rclone config reconnect gdrive:
```

Choose the backup **closest to before the incident**.

## Step 3: Restore

Full restore procedure (decrypt → extract → import):
See `references/restore-procedures.md`

## Emergency Checklist

```bash
# 1. Stop affected service to prevent further damage
sudo systemctl stop <service>

# 2. Find best backup (Step 2 above)

# 3. Decrypt → restore → verify (references/restore-procedures.md)

# 4. Restart all services
sudo systemctl start nginx mysql php8.3-fpm apache2

# 5. Re-run security audit
sudo check-server-security

# 6. Clean up
rm -rf ~/restore/
```

## Demo/Dev Reset (Git-Tracked SQL Dump Pattern)

Some apps ship a git-tracked SQL dump as the demo DB source of truth.
A reset script drops and recreates from that dump:

```bash
ls /usr/local/bin/reset-*           # find available reset scripts
sudo reset-<app>-from-git           # requires typing YES
ls /var/backups/<app>/              # safety backup always created first
```
