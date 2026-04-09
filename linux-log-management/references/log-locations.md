# Log File Locations

## System Logs

| Log | Location | View Command |
|-----|----------|-------------|
| systemd journal | `journalctl` | `sudo journalctl -u <service>` |
| kernel messages | `journalctl -k` | `sudo dmesg` |
| auth/sudo | `/var/log/auth.log` | `sudo tail -f /var/log/auth.log` |
| syslog | `/var/log/syslog` | `sudo tail -f /var/log/syslog` |

## Web Server Logs

| Log | Location |
|-----|----------|
| Nginx access | `/var/log/nginx/access.log` |
| Nginx error | `/var/log/nginx/error.log` |
| Nginx per-domain | `/var/log/nginx/<domain>-*.log` (if configured) |
| Apache error | `/var/log/apache2/error.log` |
| Apache access | `/var/log/apache2/access.log` |
| Apache per-domain | `/var/log/apache2/<domain>-*.log` |

## Application Logs

| Log | Location |
|-----|----------|
| PHP-FPM | `/var/log/php8.3-fpm.log` |
| PHP errors | `/var/log/php_errors.log` or per app.ini |
| MySQL error | `/var/log/mysql/error.log` |
| MySQL slow query | `/var/log/mysql/mysql-slow.log` |
| PostgreSQL | `/var/log/postgresql/postgresql-*.log` |
| Redis | `/var/log/redis/redis-server.log` |

## Security Logs

| Log | Location |
|-----|----------|
| fail2ban | `/var/log/fail2ban.log` |
| UFW | `/var/log/ufw.log` |
| auditd | `/var/log/audit/audit.log` |

## Backup Logs

| Log | Location |
|-----|----------|
| MySQL backup cron | `~/backups/mysql/cron.log` |
| App backup cron | `/backups/<app>/cron.log` |

## logrotate Configs

```bash
ls /etc/logrotate.d/      # all rotation configs
cat /etc/logrotate.conf   # global defaults
```

Force rotation for a service:
```bash
sudo logrotate -f /etc/logrotate.d/<service>
sudo logrotate -f /etc/logrotate.d/nginx
```

Add a new log to rotation: copy the template from `linux-disk-storage`
references/storage-reference.md logrotate section.
