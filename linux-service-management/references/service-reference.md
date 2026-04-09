# Per-Service Operations Reference

## nginx

```bash
sudo nginx -t                              # test config (ALWAYS before reload)
sudo nginx -t && sudo systemctl reload nginx
sudo systemctl restart nginx               # full restart (brief downtime)
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

## apache2

```bash
sudo apache2ctl configtest                 # test config
sudo apache2ctl configtest && sudo systemctl reload apache2
sudo tail -f /var/log/apache2/error.log
```

## mysql

```bash
sudo systemctl restart mysql
sudo journalctl -u mysql --since "5 min ago" --no-pager
mysql -e "SHOW STATUS LIKE 'Threads_connected';" 2>/dev/null
mysql -e "SHOW PROCESSLIST;" 2>/dev/null
```

## postgresql

```bash
sudo systemctl reload postgresql           # re-reads postgresql.conf
sudo journalctl -u postgresql --since "5 min ago" --no-pager
sudo -u postgres psql -c "\l"             # list databases
```

## php8.3-fpm

```bash
sudo php-fpm8.3 -t                        # test config
sudo systemctl reload php8.3-fpm
# Tune workers:
sudo nano /etc/php/8.3/fpm/pool.d/www.conf
# Key: pm.max_children, pm.start_servers
sudo tail -f /var/log/php8.3-fpm.log
```

## redis

```bash
sudo systemctl restart redis
redis-cli ping                             # should return PONG
redis-cli -a <password> info server
```

## fail2ban

```bash
sudo systemctl reload fail2ban
sudo fail2ban-client status
sudo tail -f /var/log/fail2ban.log
```

## certbot.timer

```bash
sudo systemctl status certbot.timer
sudo certbot renew --dry-run               # test renewal
sudo certbot certificates                  # check expiry
```

## msmtp (test alert email)

```bash
echo "Subject: Test\n\nTest from $(hostname)" | \
    msmtp --debug --account=default <your@email.com>
cat /etc/msmtprc 2>/dev/null || cat ~/.msmtprc 2>/dev/null
```

## cron

```bash
crontab -l                                 # current user cron jobs
sudo crontab -l                            # root cron jobs
sudo systemctl restart cron
sudo journalctl -u cron --since "1 hour ago" --no-pager
```
