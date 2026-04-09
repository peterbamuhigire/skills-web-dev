---
name: linux-server-hardening
description: Interactive security hardening for Ubuntu/Debian servers. Runs the audit script first, then walks through each FAIL and WARN item — asks before applying any change. Covers SSH, UFW, fail2ban, sysctl, Nginx, PHP-FPM, MySQL, Redis, file permissions, backup credential security.
---
# Linux Server Hardening

Applies security fixes interactively. Runs the audit first — never applies
a change without your confirmation.

**For a full picture first:** run `linux-security-analysis` before hardening.

---

## Step 1: Run The Audit

```bash
sudo check-server-security
# If not symlinked: sudo bash ~/linux-skills/scripts/server-audit.sh
```

Fix FAIL items first, then WARN. Use `references/hardening-checklist.md`
for the complete commands for each area.

---

## Hardening Areas (In Priority Order)

### 1. SSH
- Disable password auth, disable root login, set MaxAuthTries 3
- **WARNING:** Keep existing SSH session open. Test login in a second terminal
  before closing the first session.
- Config: `/etc/ssh/sshd_config.d/99-hardening.conf`
- Test before restart: `sudo sshd -t && sudo systemctl restart sshd`

### 2. Firewall (UFW)
- Default deny incoming, allow 22/80/443 only
- `sudo ufw status verbose` to check current state

### 3. Kernel (sysctl)
- Network stack hardening + ASLR + kernel pointer restriction
- Config: `/etc/sysctl.d/99-security.conf`
- Apply: `sudo sysctl --system`

### 4. Nginx
- `server_tokens off` in nginx.conf
- Security headers on all vhosts (or global security.conf)
- Dotfile blocking snippet included in all vhosts

### 5. PHP-FPM
- `expose_php = Off`, `display_errors = Off`, `allow_url_include = Off`
- Session cookie security settings
- `disable_functions` for dangerous functions
- Config: `/etc/php/8.3/fpm/php.ini`

### 6. MySQL
- `bind-address = 127.0.0.1` (never expose to network)
- Run `mysql_secure_installation`
- Application users: least-privilege only

### 7. Redis
- Bound to 127.0.0.1, password set, dangerous commands renamed

### 8. File Permissions
- `/etc/shadow` → 640, credential files → 600
- No world-writable files in `/var/www`
- SSH keys → 600

### 9. Automatic Updates
- `unattended-upgrades` installed and enabled

---

## Verify After Hardening

```bash
sudo check-server-security
# All previous FAIL items should now be PASS
```

Full configs and commands for each area: `references/hardening-checklist.md`
Reference guide: `~/linux-skills/notes/server-security.md`
