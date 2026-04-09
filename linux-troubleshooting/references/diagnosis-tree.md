# Diagnosis Tree — Full Branches

## Branch 1: High CPU / Load Average

```bash
uptime                              # load: 1m 5m 15m — concern if > nproc
nproc                               # CPU core count
htop                                # P = sort by CPU; identify top process
ps aux --sort=-%cpu | head -10
```

Fix: `sudo systemctl restart <service>` | `kill -9 <pid>` (last resort)

## Branch 2: OOM Kill

```bash
free -h                             # check available memory
sudo dmesg | grep -i "oom\|killed process" | tail -10
sudo journalctl -k --since "1 hour ago" | grep -i oom
ps aux --sort=-%mem | head -10
```

Fix: restart the killed service | add swapfile (`linux-disk-storage`) |
reduce `innodb_buffer_pool_size` if MySQL is the culprit

## Branch 3: Disk Full

```bash
df -h
du -sh /var/www/* | sort -rh | head -10
du -sh /var/log/* 2>/dev/null | sort -rh | head -10
sudo find / -type f -size +100M 2>/dev/null | head -10
```

Quick wins:
```bash
sudo apt clean
sudo journalctl --vacuum-size=500M
sudo find /tmp /var/tmp -type f -mtime +7 -delete
```

## Branch 4: Service Crashed

```bash
sudo systemctl status <service> --no-pager
sudo journalctl -u <service> --since "10 min ago" --no-pager
sudo nginx -t                        # for nginx
sudo apache2ctl configtest           # for apache2
sudo ss -tlnp | grep <port>          # port conflict?
```

## Branch 5: 502 / 504 Bad Gateway

```bash
sudo tail -20 /var/log/nginx/error.log
sudo systemctl status php8.3-fpm     # PHP sites
sudo systemctl status apache2        # Apache-proxied sites
ls -la /run/php/php8.3-fpm.sock      # FPM socket exists?

# Fix:
sudo systemctl restart php8.3-fpm
sudo systemctl restart apache2
```

## Branch 6: Slow Site

```bash
curl -w "\nTime: %{time_total}s\n" -o /dev/null -s https://<domain>
uptime && free -h                    # server load OK?
mysql -e "SHOW PROCESSLIST;" 2>/dev/null   # slow queries?
ps aux | grep php-fpm | wc -l       # FPM workers maxed?
sudo awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head
```

## Branch 7: MySQL Issues

```bash
sudo systemctl status mysql
sudo journalctl -u mysql --since "10 min ago" --no-pager
ss -tlnp | grep 3306                 # is it running?
mysql -e "SHOW STATUS LIKE 'Threads_connected';" 2>/dev/null
df -h /var/lib/mysql                 # disk space for MySQL?
```

## Branch 8: SSL Expired / Renewal Failed

```bash
sudo certbot certificates            # check all expiry dates
sudo certbot renew --dry-run         # test renewal
sudo certbot renew --force-renewal   # force if needed
sudo grep "acme-challenge" /etc/nginx/sites-enabled/*.conf  # challenge path present?
sudo journalctl -u certbot --no-pager | tail -20
```

## Branch 9: Backup Failed

```bash
tail -50 ~/backups/mysql/cron.log    # did script run?
rclone about gdrive: 2>/dev/null     # rclone token OK?
rclone config reconnect gdrive:      # if token expired
ls -la ~/.backup-encryption-key      # GPG key present and mode 600?
# Test backup manually:
~/mysql-backup.sh
```

## Branch 10: Site Down After update-all-repos

```bash
sudo systemctl status nginx
sudo nginx -t                        # config broken by update?
sudo tail -20 /var/log/nginx/error.log

# Roll back to previous commit:
cd /var/www[/html]/<folder>
sudo git log --oneline -5
sudo git reset --hard <good-commit-hash>
sudo npm run build                   # if Astro site
sudo nginx -t && sudo systemctl reload nginx
```
