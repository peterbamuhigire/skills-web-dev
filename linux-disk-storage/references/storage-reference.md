# Storage Reference

## Cleanup Targets (Priority Order)

| Target | Safe? | Command |
|--------|-------|---------|
| APT cache | Always | `sudo apt clean && sudo apt autoremove` |
| Journal (old) | Yes | `sudo journalctl --vacuum-time=14d` |
| Temp files (old) | Yes | `find /tmp -mtime +7 -delete` |
| Old backup .gpg | Yes if >7d | `find ~/backups -name "*.gpg" -mtime +7 -delete` |
| node_modules | Yes after build | `rm -rf <site>/node_modules` |
| Core dumps | Yes | `sudo find / -name "core" -type f -delete` |
| Old kernel images | Check first | `sudo apt autoremove` |

## Disk Usage Commands

```bash
# Sorted by size, human-readable
du -sh /var/www/* | sort -rh
du -sh /var/log/* 2>/dev/null | sort -rh
du -sh /* 2>/dev/null | sort -rh | head -15

# Find files larger than X:
find / -type f -size +500M 2>/dev/null
find / -type f -size +100M 2>/dev/null | grep -v proc

# Files modified recently (last 24h) — find what changed:
touch /tmp/.ts && find / -type f -newer /tmp/.ts 2>/dev/null
```

## logrotate Config Template

```
/var/log/<service>/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        systemctl reload <service> > /dev/null 2>&1 || true
    endscript
}
```

## LVM Basics (If Server Uses LVM)

```bash
# Check if LVM is in use:
sudo pvs 2>/dev/null     # physical volumes
sudo vgs 2>/dev/null     # volume groups
sudo lvs 2>/dev/null     # logical volumes

# Extend a logical volume (if VG has free space):
sudo lvextend -L +10G /dev/<vg>/<lv>
sudo resize2fs /dev/<vg>/<lv>     # ext4
# or: sudo xfs_growfs /dev/<vg>/<lv>  # xfs
```
