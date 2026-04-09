---
name: linux-system-monitoring
description: Monitor system health on Ubuntu/Debian production servers. CPU load, memory, disk I/O, network connections, process inspection. Covers htop, iostat, vmstat, ss, and backup health verification. Includes what warning signs to watch for. Reference-style — outputs commands and how to read them.
---
# System Monitoring

## Quick Health Check

```bash
echo "=LOAD=" && uptime && \
echo "=MEMORY=" && free -h && \
echo "=DISK=" && df -h && \
echo "=SERVICES=" && \
  for s in nginx mysql php8.3-fpm apache2 fail2ban; do
    printf "%-20s %s\n" $s $(systemctl is-active $s 2>/dev/null)
  done && \
echo "=LAST BACKUP=" && ls -lt ~/backups/ 2>/dev/null | head -3
```

---

## CPU & Load

```bash
uptime                    # load: 1m 5m 15m — concern if sustained > nproc
nproc                     # CPU core count
htop                      # P=CPU sort, M=memory sort, q=quit
top -bn1 | head -20       # non-interactive snapshot
ps aux --sort=-%cpu | head -10
```

## Memory

```bash
free -h
# No swap = OOM kill fires when available → 0
ps aux --sort=-%mem | head -10
```

## Disk I/O

```bash
iostat -x 1 5             # %util > 80% = bottleneck, await > 50ms = slow disk
sudo iotop -bod 5         # per-process I/O (requires: apt install iotop)
```

## Network

```bash
ss -tunapl                # all connections with process
ss -tan | awk '{print $1}' | sort | uniq -c | sort -rn   # count by state
ss -tlnp                  # listening services
```

## Backup Health

```bash
crontab -l | grep -i backup                      # backup cron present?
find ~/backups -name "*.gpg" -mtime -3 2>/dev/null | wc -l  # backups in 3 days
rclone about gdrive: 2>/dev/null | head -2       # remote reachable?
```

Full command reference with output interpretation: `references/monitoring-commands.md`
