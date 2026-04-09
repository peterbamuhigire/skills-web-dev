# fail2ban Jail Configuration Reference

## jail.local Template

Create/edit `/etc/fail2ban/jail.local` (never edit `jail.conf`):

```ini
[DEFAULT]
bantime  = 86400
findtime = 600
maxretry = 5
ignoreip = 127.0.0.1/8 ::1

[sshd]
enabled  = true
port     = ssh
maxretry = 4
bantime  = 3600

[apache-auth]
enabled  = true
port     = http,https
logpath  = /var/log/apache2/error.log
maxretry = 5
bantime  = 1800

[apache-badbots]
enabled  = true
port     = http,https
logpath  = /var/log/apache2/access.log
bantime  = 172800

[apache-noscript]
enabled  = true
port     = http,https
logpath  = /var/log/apache2/access.log
maxretry = 6

[apache-overflows]
enabled  = true
port     = http,https
logpath  = /var/log/apache2/error.log
maxretry = 2

[php-url-fopen]
enabled  = true
port     = http,https
logpath  = /var/log/apache2/error.log
maxretry = 5

[recidive]
enabled  = true
logpath  = /var/log/fail2ban.log
bantime  = 604800
findtime = 86400
maxretry = 5
```

## WordPress Jails (For Sites With WordPress)

```ini
[wordpress-hard]
enabled  = true
port     = http,https
logpath  = /var/log/nginx/access.log
maxretry = 2
bantime  = 86400

[wordpress-xmlrpc]
enabled  = true
port     = http,https
logpath  = /var/log/nginx/access.log
maxretry = 1
bantime  = 172800
```

Requires filter files in `/etc/fail2ban/filter.d/`. Basic WordPress filter:
```ini
# /etc/fail2ban/filter.d/wordpress-hard.conf
[Definition]
failregex = ^<HOST> .* "POST .*wp-login\.php
ignoreregex =
```

## Custom SaaS API Rate Limit Jail

```ini
[saas-api-limit]
enabled  = true
port     = http,https
logpath  = /var/log/nginx/access.log
maxretry = 60
findtime = 60
bantime  = 3600
filter   = saas-api-limit
```

Filter `/etc/fail2ban/filter.d/saas-api-limit.conf`:
```ini
[Definition]
failregex = ^<HOST> .* "POST /api/
ignoreregex =
```

## Operations

```bash
# Check all bans
sudo fail2ban-client status

# Unban
sudo fail2ban-client set <jail> unbanip <ip>

# Test a filter against a log file
sudo fail2ban-regex /var/log/nginx/access.log /etc/fail2ban/filter.d/saas-api-limit.conf

# Reload after changes
sudo systemctl reload fail2ban
```
