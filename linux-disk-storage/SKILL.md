---
name: linux-disk-storage
description: Manage disk space on Ubuntu/Debian servers. Check usage, find space hogs, safe cleanup (apt cache, journal, old logs, old backups, node_modules), inode exhaustion, and emergency disk-full recovery. Includes swapfile creation for servers running without swap.
---
# Disk & Storage

## Check Usage

```bash
df -h                           # filesystem overview (concern: > 85% used)
df -i                           # inode usage (can be full independently)
du -sh /var/www/* | sort -rh | head -10
du -sh /var/log/* 2>/dev/null | sort -rh | head -10
du -sh ~/backups/* 2>/dev/null | sort -rh | head -5
sudo find / -type f -size +100M 2>/dev/null | head -10
```

---

## Safe Cleanup (In Order Of Safety)

```bash
# 1. APT cache (always safe)
sudo apt clean && sudo apt autoremove

# 2. Journal logs (safe, keeps recent 14 days)
sudo journalctl --vacuum-time=14d
sudo journalctl --vacuum-size=500M

# 3. Old backup files (verify retention script is running first)
find ~/backups/mysql/ -name "*.gpg" -mtime +7 -delete

# 4. Temp files
sudo find /tmp /var/tmp -type f -mtime +7 -delete

# 5. node_modules after successful Astro build
# cd /var/www[/html]/<site> && rm -rf node_modules
# (update-all-repos will reinstall on next pull)
```

---

## Emergency Disk Full

```bash
# Fast identification
df -h && du -sh /var/www/* /var/log/* ~/backups/* 2>/dev/null | sort -rh | head -10

# Immediate wins (safe):
sudo apt clean
sudo journalctl --vacuum-size=200M
sudo find /tmp /var/tmp -type f -mtime +7 -delete

# Truncate an oversize log (safer than deleting):
sudo truncate -s 0 /var/log/<oversize-log-file>
```

---

## Inode Exhaustion (df -i shows 100%)

```bash
# Find dir with most files:
sudo find / -xdev -type f 2>/dev/null | cut -d/ -f2 | sort | uniq -c | sort -rn | head

# Common causes: PHP sessions, mail spool, tiny cache files
sudo find /var/lib/php/sessions/ -type f | wc -l
sudo find /tmp -type f | wc -l
```

---

## Swapfile (Safety Net For No-Swap Servers)

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.d/99-swappiness.conf
sudo sysctl vm.swappiness=10
free -h                   # verify Swap shows 2G
```

Full cleanup targets and LVM reference: `references/storage-reference.md`
