# Monitoring Commands Reference

## vmstat

```bash
vmstat 1 10
# Columns: r=run queue, b=blocked, si/so=swap(should be 0), wa=I/O wait
# r > nproc = CPU bottleneck | wa > 20% = disk bottleneck
```

## iostat Interpretation

```bash
iostat -x 1 5
# %util > 80% sustained = disk bottleneck
# await > 50ms = slow disk response
# r/s + w/s = operations per second
```

## Memory Deep Dive

```bash
cat /proc/meminfo | grep -E "MemTotal|MemFree|MemAvailable|Cached|Buffers|SwapTotal"
# MemAvailable = truly free for new processes (not just MemFree)

# Per-process memory
ps aux --sort=-%mem | awk 'NR<=11{printf "%-30s %s MB\n", $11, $6/1024}'
```

## Network Connection Analysis

```bash
# Connections by state
ss -tan | awk '{print $1}' | sort | uniq -c | sort -rn
# ESTABLISHED = active | TIME_WAIT = closing | CLOSE_WAIT = may leak

# Connections per IP to web ports
ss -tan 'sport = :443 or sport = :80' | awk '{print $5}' | \
    cut -d: -f1 | sort | uniq -c | sort -rn | head -10

# Open file descriptors per service
ls -l /proc/$(pgrep -f nginx | head -1)/fd 2>/dev/null | wc -l
```

## Per-Service Resource Usage

```bash
# Memory and CPU from systemd
for s in nginx apache2 mysql postgresql php8.3-fpm fail2ban; do
    mem=$(systemctl show $s --property=MemoryCurrent 2>/dev/null | \
          cut -d= -f2)
    echo "$s: $((${mem:-0}/1024/1024)) MB"
done

# Or via ps:
ps aux | grep -E "nginx|mysql|php-fpm|apache" | \
    awk '{sum[$11]+=$6} END {for(p in sum) printf "%s %s MB\n", sum[p]/1024, p}' | \
    sort -rn
```

## Disk Space Trend

```bash
df -h                              # current
du -sh /var/log/ /var/www/ ~/backups/  # top consumers
sudo find / -type f -size +500M 2>/dev/null   # very large files
```
