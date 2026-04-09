---
name: linux-intrusion-detection
description: Manage intrusion detection on Ubuntu/Debian servers. fail2ban (check jails, unban IPs, add custom jails, tune bans, read logs). AIDE file integrity monitoring (install, initialise, run checks, schedule daily). auditd system call auditing (install, watch files, read audit log).
---
# Intrusion Detection

## fail2ban

```bash
sudo fail2ban-client status                      # all jails + count
sudo fail2ban-client status <jail>               # specific jail (bans, IPs)
sudo tail -f /var/log/fail2ban.log               # live ban activity

# Unban an IP
sudo fail2ban-client set <jail> unbanip <ip>

# Reload after config change
sudo systemctl reload fail2ban
sudo fail2ban-client status                      # verify jails loaded
```

Full jail configuration templates: `references/fail2ban-jails.md`

---

## AIDE (File Integrity Monitoring)

```bash
# Install
sudo apt install aide

# Initialise (first time — takes a few minutes)
sudo aideinit
sudo cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db

# Run integrity check
sudo aide --check
# No output = no changes. Any output = files changed since last init.

# Update DB after intentional changes (e.g. after a deployment)
sudo aideinit
sudo cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db
```

### Schedule Daily AIDE Check

```bash
sudo nano /etc/cron.daily/aide-check
```
```bash
#!/bin/bash
aide --check | mail -s "AIDE Report $(hostname) $(date +%Y-%m-%d)" root
```
```bash
sudo chmod +x /etc/cron.daily/aide-check
```

---

## auditd (System Call Auditing)

```bash
sudo apt install auditd
sudo systemctl enable auditd && sudo systemctl start auditd

# Watch critical files:
sudo auditctl -w /etc/passwd -p rwxa -k passwd-changes
sudo auditctl -w /etc/shadow -p rwxa -k shadow-changes
sudo auditctl -w /etc/ssh/sshd_config -p rwxa -k ssh-config
sudo auditctl -w /var/www -p w -k webroot-writes

# Make rules permanent:
sudo nano /etc/audit/rules.d/hardening.rules
# Add the -w rules above

# Search audit log:
sudo ausearch -k passwd-changes
sudo ausearch -f /etc/passwd
sudo ausearch --start today
sudo aureport --summary
```
