# Security Audit — Layer Command Reference

Complete commands for each of the 10 security analysis layers.

## Layer 1: System & Kernel

```bash
uname -r
sysctl kernel.randomize_va_space        # expect 2
sysctl kernel.dmesg_restrict            # expect 1
sysctl kernel.kptr_restrict             # expect 2
sysctl net.ipv4.tcp_syncookies          # expect 1
sysctl net.ipv4.conf.all.accept_redirects  # expect 0
sysctl net.ipv4.conf.all.send_redirects    # expect 0
sysctl net.ipv4.conf.all.rp_filter         # expect 1
apt list --upgradable 2>/dev/null | grep -i security | wc -l
systemctl is-enabled unattended-upgrades 2>/dev/null
```

CRITICAL: ASLR=0 | HIGH: >20 security updates | MEDIUM: unattended-upgrades off

## Layer 2: Users & Authentication

```bash
awk -F: '$3 == 0 {print $1}' /etc/passwd        # UID-0 (only root expected)
sudo awk -F: '$2 == "" {print $1}' /etc/shadow  # empty passwords
grep ^sudo /etc/group                            # sudo members
grep -rh "^PermitRootLogin\|^PasswordAuthentication\|^MaxAuthTries\|^X11Forwarding" \
    /etc/ssh/sshd_config /etc/ssh/sshd_config.d/ 2>/dev/null
find /home /root -name authorized_keys 2>/dev/null -exec echo "=== {} ===" \; -exec cat {} \;
```

CRITICAL: extra UID-0 or empty passwords |
HIGH: PasswordAuthentication yes | HIGH: PermitRootLogin not 'no'

## Layer 3: Network Exposure

```bash
ss -tulnp
ss -tlnp | grep -E ':3306|:5432|:6379|:27017'  # must all be 127.0.0.1
ss -tlnp | grep ":::"                           # IPv6 listeners
```

CRITICAL: MySQL/PostgreSQL/Redis on 0.0.0.0

## Layer 4: Firewall

```bash
sudo ufw status verbose
sudo ufw status verbose | grep "Default:"       # must be 'deny (incoming)'
```

CRITICAL: UFW inactive | HIGH: default not deny | MEDIUM: unexpected ALLOW rules

## Layer 5: Web Server Security

```bash
sudo nginx -T 2>/dev/null | grep -E "server_tokens|ssl_protocols"
sudo certbot certificates 2>/dev/null
openssl s_client -connect localhost:443 -tls1 2>&1 | grep -E "handshake|alert"
php -r "echo ini_get('expose_php');"           # must be empty
php -r "echo ini_get('display_errors');"       # must be 0/empty
php -r "echo ini_get('allow_url_include');"    # must be empty
php -r "echo ini_get('session.cookie_secure');" # must be 1
php -r "echo ini_get('disable_functions');"    # must have entries
```

CRITICAL: cert expires <7 days | HIGH: TLSv1.0/1.1 accepted | HIGH: PHP exposes version

## Layer 6: Database Security

```bash
grep -E "^bind-address" /etc/mysql/mysql.conf.d/mysqld.cnf \
    /etc/mysql/mariadb.conf.d/50-server.cnf 2>/dev/null
mysql -e "SELECT user,host FROM mysql.user WHERE user='';" 2>/dev/null
mysql -e "SHOW DATABASES;" 2>/dev/null | grep "^test$"
grep -E "^bind|^requirepass" /etc/redis/redis.conf 2>/dev/null
grep -v "^#\|^$" /etc/postgresql/*/main/pg_hba.conf 2>/dev/null | head -10
```

CRITICAL: databases on 0.0.0.0 | HIGH: anon MySQL users | HIGH: Redis no password

## Layer 7: File System

```bash
find /var/www -type f -perm -0002 2>/dev/null
find / -perm /6000 -type f 2>/dev/null | \
    grep -vE "(sudo|passwd|su|mount|umount|ping|crontab|at|newgrp|chsh|chfn|gpasswd)"
stat -c "%a %n" ~/.mysql-backup.cnf ~/.backup-encryption-key \
    ~/.config/rclone/rclone.conf 2>/dev/null
stat -c "%a %n" /etc/shadow /etc/gshadow /etc/passwd /etc/ssh/sshd_config
find /var/www /home /etc -nouser -nogroup 2>/dev/null | head -10
```

HIGH: world-writable /var/www files | HIGH: cred files not 600 | MEDIUM: unexpected SUID

## Layer 8: Intrusion Detection & Monitoring

```bash
systemctl is-active fail2ban
sudo fail2ban-client status 2>/dev/null | grep -E "Number of jail|Jail list"
command -v aide >/dev/null 2>&1 && echo "AIDE installed" || echo "AIDE missing"
ls /var/lib/aide/aide.db 2>/dev/null || echo "AIDE DB not initialised"
systemctl is-active auditd 2>/dev/null
dpkg -l 2>/dev/null | grep -E "logwatch|logcheck"
```

HIGH: fail2ban not running | MEDIUM: AIDE not installed | MEDIUM: <3 jails

## Layer 9: Backup Integrity

```bash
crontab -l 2>/dev/null | grep -iE "backup|rclone"
sudo crontab -l 2>/dev/null | grep -iE "backup|rclone"
find ~/backups -name "*.gpg" -mtime -1 2>/dev/null | wc -l
rclone about gdrive: 2>/dev/null | head -2 || echo "rclone: cannot connect"
for f in ~/.mysql-backup.cnf ~/.backup-encryption-key ~/.config/rclone/rclone.conf; do
    [ -f "$f" ] && echo "EXISTS $f" || echo "MISSING $f"
done
```

HIGH: no backup in 24h | HIGH: backup creds missing | MEDIUM: rclone unreachable

## Layer 10: Packages & Software

```bash
apt list --upgradable 2>/dev/null | tail -n +2 | wc -l
systemctl list-units --type=service --state=running | \
    grep -vE "nginx|apache|mysql|postgresql|php|redis|fail2ban|ssh|cron|ufw|certbot|systemd|dbus|network"
command -v lynis >/dev/null 2>&1 && \
    sudo lynis audit system --quick 2>/dev/null | grep -E "Hardening index|Warning" | head -10
```

MEDIUM: >10 upgradable packages | INFO: unexpected running services
