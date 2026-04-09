# Hardening Checklist — Full Commands

## SSH Hardening

```bash
sudo nano /etc/ssh/sshd_config.d/99-hardening.conf
```
```
PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication no
PermitEmptyPasswords no
X11Forwarding no
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 3
AllowAgentForwarding no
```
```bash
sudo sshd -t && sudo systemctl restart sshd
```

## UFW Firewall

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status verbose
```

## Kernel Hardening (sysctl)

```bash
sudo nano /etc/sysctl.d/99-security.conf
```
```ini
net.ipv4.tcp_syncookies = 1
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.all.log_martians = 1
net.ipv4.icmp_echo_ignore_broadcasts = 1
kernel.randomize_va_space = 2
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2
kernel.sysrq = 0
```
```bash
sudo sysctl --system
```

## Nginx Security

```nginx
# In /etc/nginx/nginx.conf http block:
server_tokens off;
```
```bash
# Verify dotfile blocking in all vhosts:
sudo grep -r "security-dotfiles" /etc/nginx/sites-enabled/
# Verify security headers:
sudo grep -r "X-Frame-Options\|X-Content-Type" /etc/nginx/sites-enabled/ \
    /etc/nginx/conf.d/ /etc/nginx/snippets/
```

## PHP-FPM Security

```bash
sudo nano /etc/php/8.3/fpm/php.ini
```
```ini
expose_php = Off
display_errors = Off
log_errors = On
allow_url_include = Off
session.cookie_httponly = 1
session.cookie_secure = 1
session.use_strict_mode = 1
session.cookie_samesite = Lax
disable_functions = exec,passthru,shell_exec,system,proc_open,popen,parse_ini_file,show_source
```
```bash
sudo systemctl restart php8.3-fpm
```

## MySQL Security

```bash
# Bind to localhost:
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
# Set: bind-address = 127.0.0.1
sudo systemctl restart mysql
ss -tlnp | grep 3306   # must show 127.0.0.1:3306

# Secure installation (removes anon users, test DB):
sudo mysql_secure_installation
```

## Redis Security

```bash
sudo nano /etc/redis/redis.conf
# Ensure: bind 127.0.0.1 -::1
# Ensure: requirepass <strong-password>
# Add:
# rename-command FLUSHDB ""
# rename-command FLUSHALL ""
# rename-command CONFIG ""
# rename-command DEBUG ""
sudo systemctl restart redis
ss -tlnp | grep 6379   # must show 127.0.0.1:6379
```

## File Permissions

```bash
sudo chmod 640 /etc/shadow /etc/gshadow
sudo chmod 644 /etc/passwd /etc/group
chmod 600 ~/.mysql-backup.cnf ~/.backup-encryption-key
chmod 600 ~/.config/rclone/rclone.conf
chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys
sudo find /var/www -type f -perm -0002 -exec chmod o-w {} \;
```

## Automatic Updates

```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades   # select Yes
cat /etc/apt/apt.conf.d/20auto-upgrades     # verify
```
