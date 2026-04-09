# Restore Procedures

## MySQL Restore (GPG-Encrypted Backup)

### Download From Google Drive

```bash
mkdir -p ~/restore
rclone ls gdrive:<backup-folder> | sort | tail -10    # find backup name
rclone copy gdrive:<backup-folder>/mysql-backup_TIMESTAMP.tar.gz.gpg ~/restore/
```

### Decrypt

```bash
gpg --batch \
    --passphrase-file ~/.backup-encryption-key \
    -d ~/restore/mysql-backup_TIMESTAMP.tar.gz.gpg \
    > ~/restore/mysql-backup_TIMESTAMP.tar.gz

ls -lh ~/restore/mysql-backup_TIMESTAMP.tar.gz      # verify
```

If GPG fails:
```bash
cat ~/.backup-encryption-key          # must not be empty
ls -la ~/.backup-encryption-key       # must be mode 600
```

### Extract

```bash
tar xzf ~/restore/mysql-backup_TIMESTAMP.tar.gz -C ~/restore/
ls ~/restore/dump_*/                  # shows available databases
```

### Restore Single Database

```bash
# Confirm: this overwrites the existing database
mysql -u root -p <database_name> < ~/restore/dump_TIMESTAMP/<database_name>.sql
# Or using credentials file:
mysql --defaults-file=~/.mysql-backup.cnf <db_name> < ~/restore/dump_TIMESTAMP/<db>.sql
```

### Restore All Databases (Full System)

```bash
# Confirm: this overwrites ALL databases
mysql -u root -p < ~/restore/dump_TIMESTAMP/all-databases.sql
```

### Verify

```bash
mysql -e "SHOW DATABASES;" 2>/dev/null
mysql -e "SELECT COUNT(*) FROM <db>.<key_table>;" 2>/dev/null
sudo systemctl status mysql
```

---

## App File Restore

Apps with their own backup scripts store archives in `/backups/<app>/`:

```bash
# Decrypt:
gpg --batch --passphrase-file ~/.backup-encryption-key \
    -d /backups/<app>/backup_TIMESTAMP.tar.gz.gpg \
    > /tmp/app-restore.tar.gz

# Extract and copy back:
mkdir -p /tmp/app-restore
tar xzf /tmp/app-restore.tar.gz -C /tmp/app-restore/
sudo rsync -av /tmp/app-restore/<files>/ /var/www/html/<app>/
```

---

## Restore From Local Backup (If Drive Unavailable)

```bash
ls -lth ~/backups/mysql/*.gpg | head -5    # local archives
# Same decrypt → extract → restore process above
```

---

## Cleanup

```bash
rm -rf ~/restore/ /tmp/app-restore/
# Keep .gpg archive until you confirm the restore is stable
```
