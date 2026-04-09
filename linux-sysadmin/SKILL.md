---
name: linux-sysadmin
description: Linux server management hub for Ubuntu/Debian production servers. Use for any server management task — security analysis, hardening, services, deployment, monitoring, troubleshooting, disaster recovery. Routes to the right specialist skill.
---
# Linux Server Admin Hub

## Server Context

This context applies to the primary managed server. Update when working on a
different server.

```
OS:        Ubuntu/Debian production server
Web:       Nginx (80/443) → PHP-FPM | Apache (8080) | Node.js services
DBs:       MySQL 8 | PostgreSQL 15 | Redis
Security:  UFW (22/80/443 only), fail2ban, SSH keys-only, certbot ECDSA certs
Backups:   Cron → backup-alert.sh → GPG AES256 → rclone → Google Drive
           Local: 7 days | Remote: 3 days | Credentials: mode 600
Deployment:/usr/local/bin/update-all-repos (git reset --hard + optional build)
Admin:     /home/administrator | Web: /var/www/html/ and /var/www/
Nginx cfg: /etc/nginx/sites-available/*.conf | snippets: /etc/nginx/snippets/
```

## What Do You Need To Do?

```
Linux Server Management
═══════════════════════════════════════
  1.  Set up a new server (from scratch)
  2.  Security analysis  (deep read-only audit + severity report)
  3.  Security hardening (apply fixes interactively)
  4.  Manage users & access control
  5.  Firewall & SSL certificates
  6.  Intrusion detection (fail2ban, AIDE, auditd)
  7.  Manage services (nginx, mysql, php-fpm, cron…)
  8.  Disk & storage management
  9.  Monitor system health
 10.  Web stack (Nginx, Apache, PHP-FPM, Node.js)
 11.  Log management & analysis
 12.  Troubleshoot an issue
 13.  Disaster recovery & restore from backup
 14.  Deploy a new website
═══════════════════════════════════════
```

## Routing Table

| Choice | Skill |
|--------|-------|
| 1 | linux-server-provisioning |
| 2 | linux-security-analysis |
| 3 | linux-server-hardening |
| 4 | linux-access-control |
| 5 | linux-firewall-ssl |
| 6 | linux-intrusion-detection |
| 7 | linux-service-management |
| 8 | linux-disk-storage |
| 9 | linux-system-monitoring |
| 10 | linux-webstack |
| 11 | linux-log-management |
| 12 | linux-troubleshooting |
| 13 | linux-disaster-recovery |
| 14 | linux-site-deployment |

## Standing Rules

- All skills work on any Ubuntu/Debian server — no product names in guidance
- Confirm before every destructive operation (restore, drop, reset, delete)
- Run `sudo nginx -t` before every Nginx reload — never skip
- Every new repo on the server MUST be registered in `/usr/local/bin/update-all-repos`
- `update-all-repos` runs `git reset --hard` — local changes are destroyed on pull
- Backup credential files must always be mode 600
