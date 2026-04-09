---
name: linux-troubleshooting
description: Systematic incident diagnosis for Ubuntu/Debian production servers. Ask for the symptom then follow the matching diagnosis branch — high CPU/load, OOM kill, disk full, service crashed, 502/504 errors, slow site, MySQL issues, SSL expired, backup failed, site down after git update.
---
# Troubleshooting

Ask: "What's the symptom?" then follow the branch in `references/diagnosis-tree.md`.

## Symptom Index

| Symptom | Branch |
|---------|--------|
| High CPU or load average | → Branch 1 |
| Out of memory / OOM kill | → Branch 2 |
| Disk full | → Branch 3 |
| Service crashed / won't start | → Branch 4 |
| 502 or 504 from Nginx | → Branch 5 |
| Site is slow | → Branch 6 |
| MySQL problems | → Branch 7 |
| SSL expired or renewal failed | → Branch 8 |
| Backup failed | → Branch 9 |
| Site down after update-all-repos | → Branch 10 |

Full diagnosis commands for each: `references/diagnosis-tree.md`

---

## Quick Triage (Run First For Any Issue)

```bash
# System health snapshot
uptime && free -h && df -h

# Failed services
sudo systemctl list-units --type=service --state=failed

# Recent errors across all services
sudo journalctl -p err --since "1 hour ago" --no-pager | head -30

# Nginx error log
sudo tail -20 /var/log/nginx/error.log
```

---

## Most Common Fixes

```bash
# Service crashed → restart it
sudo systemctl restart <service>

# Nginx config broken → find and fix
sudo nginx -t

# Disk full → clear apt cache
sudo apt clean && sudo journalctl --vacuum-size=500M

# 502 → restart the upstream
sudo systemctl restart php8.3-fpm
sudo systemctl restart apache2

# SSL expired → force renew
sudo certbot renew --force-renewal
```
