# Security Hardening

**Linux hardening, SSH, UFW, fail2ban, automatic updates, Nginx headers**

Run this checklist on every new VPS within 30 minutes of provisioning.

---

## Step 1 — First Login (as root)

```bash
# Update everything immediately
apt update && apt upgrade -y

# Install essentials
apt install -y ufw fail2ban unattended-upgrades curl git vim htop

# Create a non-root user for all future work
adduser peter
usermod -aG sudo peter

# Copy SSH key to new user
rsync --archive --chown=peter:peter ~/.ssh /home/peter
```

Log out. Log back in as `peter`, not root.

---

## Step 2 — SSH Hardening

```bash
sudo vim /etc/ssh/sshd_config
```

Set these values:

```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
X11Forwarding no
AllowUsers peter
MaxAuthTries 3
LoginGraceTime 60
```

Restart SSH:
```bash
sudo systemctl restart sshd
```

**Before closing your current session:** open a second terminal and verify you
can still SSH in. Only then close the first. Locking yourself out is a common mistake.

---

## Step 3 — UFW Firewall

```bash
# Default: deny all incoming, allow all outgoing
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (restrict to your IP if possible)
sudo ufw allow from YOUR.IP.ADDRESS to any port 22
# OR if IP is dynamic:
sudo ufw allow 22/tcp

# Allow web traffic
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable
sudo ufw enable
sudo ufw status verbose
```

**For DB VPS (no public web traffic):**
```bash
sudo ufw default deny incoming
sudo ufw allow from 10.x.x.x to any port 3306  # Web VPS private IP only
sudo ufw allow from YOUR.IP.ADDRESS to any port 22
sudo ufw enable
```

MySQL should NEVER be accessible from the public internet.

---

## Step 4 — fail2ban

Automatically bans IPs with repeated failed login attempts.

```bash
# Create local config (override defaults without editing original)
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo vim /etc/fail2ban/jail.local
```

Edit the `[sshd]` section:

```ini
[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 5
bantime = 3600    # 1 hour ban
findtime = 600    # within 10 minutes
```

Add Nginx protection (for brute force on login forms):

```ini
[nginx-http-auth]
enabled = true
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
maxretry = 5
bantime = 3600
```

Start fail2ban:
```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Check status
sudo fail2ban-client status sshd
```

---

## Step 5 — Automatic Security Updates

```bash
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

Edit `/etc/apt/apt.conf.d/50unattended-upgrades`:

```
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
};
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Mail "your-email@domain.com";
```

Setting `Automatic-Reboot "false"` means kernel updates need a manual reboot.
Schedule this during your maintenance window. Check `sudo needrestart` weekly.

---

## Step 6 — Nginx Security Headers

Add to every server block (or to `nginx.conf` http block for all sites):

```nginx
# Prevent clickjacking
add_header X-Frame-Options "SAMEORIGIN" always;

# Prevent MIME sniffing
add_header X-Content-Type-Options "nosniff" always;

# Referrer policy
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# HSTS — force HTTPS for 1 year
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

# Permissions policy — disable unused browser features
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;

# Remove Nginx version from headers
server_tokens off;
```

For Content Security Policy (CSP) — set per-application, not globally, as it
depends on which CDNs/scripts each app loads:

```nginx
# Example for a PHP app with no external scripts:
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';" always;
```

Validate your headers at securityheaders.com after deployment.

---

## Step 7 — PHP Hardening (in docker-compose or php.ini)

```ini
; php.ini or Docker PHP config
expose_php = Off               ; Don't reveal PHP version in headers
display_errors = Off           ; Never show errors to users in production
log_errors = On
error_log = /var/log/php_errors.log
max_execution_time = 30
memory_limit = 128M
upload_max_filesize = 10M
post_max_size = 12M
allow_url_fopen = Off          ; Prevent remote file inclusion
allow_url_include = Off
disable_functions = exec,passthru,shell_exec,system,proc_open,popen
```

---

## Step 8 — MySQL Hardening

Run after installation:

```bash
sudo mysql_secure_installation
```

This will:
- Set root password
- Remove anonymous users
- Disable remote root login
- Remove test database

Then verify:
```sql
-- Check for any users with empty passwords
SELECT user, host, authentication_string FROM mysql.user WHERE authentication_string = '';

-- Check for wildcard hosts
SELECT user, host FROM mysql.user WHERE host = '%';

-- Both queries should return empty results in production
```

---

## Monthly Security Checklist

Run these monthly:

```bash
# Check for failed SSH attempts
grep "Failed password" /var/log/auth.log | tail -20

# Check currently banned IPs
sudo fail2ban-client status sshd

# Check for large error log files
sudo du -sh /var/log/*

# Check pending security updates
sudo apt list --upgradable 2>/dev/null | grep -i security

# Check disk space (full disk = service outage)
df -h

# Check memory usage
free -h

# Check which ports are listening
sudo ss -tlnp
```

---

## Security Monitoring — Minimal Setup

### Uptime + SSL monitoring (free)

Use UptimeRobot (free plan):
- HTTP/HTTPS checks every 5 minutes
- SSL certificate expiry alerts
- Email + Telegram alerts on downtime

### Log monitoring

```bash
# Install and configure logwatch for daily email summaries
sudo apt install -y logwatch
sudo logwatch --output mail --mailto your@email.com --detail high
```

### Simple intrusion detection

```bash
# Install rkhunter — scans for rootkits
sudo apt install -y rkhunter
sudo rkhunter --update
sudo rkhunter --check
```

Run `rkhunter --check` weekly via cron:
```bash
# Add to crontab (crontab -e)
0 3 * * 0 /usr/bin/rkhunter --check --skip-keypress --report-warnings-only | mail -s "RKHunter Report" your@email.com
```
