# Linux Systems Hardening

Hardening reference for Debian/Ubuntu hosts running Jenkins controllers, agents, and production application servers. Every parameter below is the exact `sysctl.conf` line or command to execute.

## sysctl Hardening

Concrete lines for `/etc/sysctl.d/99-hardening.conf`:

```conf
# Address Space Layout Randomisation
kernel.randomize_va_space = 2

# Ignore source-routed packets
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0

# Ignore ICMP redirects
net.ipv4.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv4.conf.all.secure_redirects = 0

# Send redirects off
net.ipv4.conf.all.send_redirects = 0

# Reverse-path filtering
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# SYN flood protection
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 4096
net.ipv4.tcp_synack_retries = 2

# TIME_WAIT socket reuse
net.ipv4.tcp_tw_reuse = 1

# IP spoofing / martians
net.ipv4.conf.all.log_martians = 1

# Disable IPv6 forwarding
net.ipv6.conf.all.forwarding = 0
```

Apply with `sudo sysctl --system`. Verify with `sudo sysctl -a | grep <key>`.

## cgroups v2 Resource Limits

- Enable unified hierarchy (Debian 12+ default): confirm with `mount | grep cgroup2`
- Service limits via systemd: `/etc/systemd/system/myapp.service.d/limits.conf`:

```ini
[Service]
MemoryMax=2G
MemoryHigh=1800M
CPUWeight=500
IOWeight=500
TasksMax=512
```

- Reload: `sudo systemctl daemon-reload && sudo systemctl restart myapp`

## auditd

- Install: `sudo apt install auditd audispd-plugins`
- Rules in `/etc/audit/rules.d/hardening.rules`:

```conf
-w /etc/passwd -p wa -k passwd_changes
-w /etc/shadow -p wa -k shadow_changes
-w /etc/sudoers -p wa -k sudoers
-w /etc/ssh/sshd_config -p wa -k sshd_config
-a always,exit -F arch=b64 -S execve -F euid=0 -k root_exec
-a always,exit -F arch=b64 -S unlink -S rename -F dir=/var/log -k log_tamper
-e 2
```

- Reload: `sudo augenrules --load`
- Search: `sudo ausearch -k root_exec --start today`
- Log forwarding to SIEM via rsyslog imuxsock or Fluent Bit

## AppArmor Profiles

- Status: `sudo aa-status`
- Nginx profile example (`/etc/apparmor.d/usr.sbin.nginx`):

```apparmor
#include <tunables/global>
/usr/sbin/nginx {
  #include <abstractions/base>
  #include <abstractions/nameservice>
  capability dac_override,
  capability setuid,
  capability setgid,
  capability net_bind_service,
  /etc/nginx/** r,
  /var/log/nginx/* w,
  /var/www/** r,
  /run/nginx.pid rw,
}
```

- Load: `sudo apparmor_parser -r /etc/apparmor.d/usr.sbin.nginx`
- MySQL and Node.js profiles — Debian ships templates in `/etc/apparmor.d/`. Place app in enforce mode via `sudo aa-enforce /etc/apparmor.d/usr.sbin.mysqld`.

## fail2ban

- Install: `sudo apt install fail2ban`
- SSH jail (`/etc/fail2ban/jail.d/ssh.conf`):

```ini
[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600
```

- Nginx jail for 401/404 floods (`/etc/fail2ban/jail.d/nginx.conf`):

```ini
[nginx-noscript]
enabled = true
port = http,https
filter = nginx-noscript
logpath = /var/log/nginx/access.log
maxretry = 6
bantime = 86400
```

- Reload: `sudo fail2ban-client reload`. Status: `sudo fail2ban-client status sshd`.

## Network Stack Tuning

- Enable BBR congestion control:

```conf
net.core.default_qdisc = fq
net.ipv4.tcp_congestion_control = bbr
```

- SO_REUSEPORT: application-level (node/nginx) — `net.ipv4.ip_local_port_range = 10000 65535`
- TCP keepalive (detect dead peers):

```conf
net.ipv4.tcp_keepalive_time = 120
net.ipv4.tcp_keepalive_intvl = 30
net.ipv4.tcp_keepalive_probes = 8
```

- Verify BBR active: `sysctl net.ipv4.tcp_congestion_control` should show `bbr`.
