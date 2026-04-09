# Permissions Reference

## Find Permission Issues

```bash
# World-writable files in web root (should be none)
find /var/www -type f -perm -0002 2>/dev/null

# SUID/SGID binaries (unexpected ones are suspicious)
find / -perm /6000 -type f 2>/dev/null | \
    grep -vE "(sudo|passwd|su|mount|umount|ping|crontab|at|newgrp|chsh|chfn|gpasswd)"

# Unowned files
find /var/www /home /etc -nouser -nogroup 2>/dev/null

# Credential file permissions
stat -c "%a %n" ~/.mysql-backup.cnf ~/.backup-encryption-key \
    ~/.config/rclone/rclone.conf 2>/dev/null
# All must show 600
```

## Permission Reference Table

| Path | Expected Permission | Owner |
|------|--------------------|----|
| /etc/shadow | 640 | root:shadow |
| /etc/gshadow | 640 | root:shadow |
| /etc/passwd | 644 | root:root |
| /etc/group | 644 | root:root |
| /etc/ssh/sshd_config | 644 | root:root |
| ~/.ssh/ | 700 | user:user |
| ~/.ssh/authorized_keys | 600 | user:user |
| ~/.mysql-backup.cnf | 600 | user:user |
| ~/.backup-encryption-key | 600 | user:user |
| ~/.config/rclone/rclone.conf | 600 | user:user |
| /var/www directories | 755 | www-data:www-data |
| /var/www files | 644 | www-data:www-data |

## Service Account Verification

Web processes must run as www-data, not root:

```bash
ps aux | grep "nginx: worker" | grep -v grep     # must show www-data
ps aux | grep "php-fpm" | grep "pool" | grep -v grep  # must show www-data

# nginx.conf:
grep "^user" /etc/nginx/nginx.conf               # user www-data;

# php-fpm pool:
grep "^user\|^group" /etc/php/8.3/fpm/pool.d/www.conf
```
