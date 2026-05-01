# File Permissions, ACLs and Filesystem Hardening

Reference for locking down files and filesystems on Debian 12 / Ubuntu 24.04.
Covers the classic `rwx` model, POSIX ACLs, xattrs, and mount-level defences.

## 1. The Linux DAC model

Discretionary Access Control on Linux is owner-centric: each file has
exactly one owning user, one owning group, and three permission triplets.

```text
-rwxr-x---  1 jdoe  deploy  12345  Mar 10 14:02  deploy.sh
 ^^^^^^^^^
 |||||||++- other  (none)
 ||||+++--- group  deploy  (r-x)
 |+++------ owner  jdoe    (rwx)
 +--------- file type  (- regular, d dir, l symlink, c/b device)
```

Numeric (octal) values:

| Perm | Value | Meaning on a file        | Meaning on a directory              |
|------|-------|--------------------------|-------------------------------------|
| r    | 4     | Read file contents       | List entries                        |
| w    | 2     | Modify file contents     | Create/delete/rename entries        |
| x    | 1     | Execute                  | Enter (cd into) and access entries  |

Common combinations:

- `0644` — world readable, owner writable. Default for regular files.
- `0600` — owner-only. Use for secrets, SSH keys, `.env` files.
- `0755` — world executable, owner writable. Default for binaries and dirs.
- `0750` — group-readable, world-denied. Use for project directories.
- `0700` — owner-only directory. Use for `~/.ssh`, `/root`.

```bash
chmod 640 /etc/myapp/config.yml
chmod u=rw,g=r,o= /etc/myapp/config.yml  # same thing, symbolic
chown root:myapp   /etc/myapp/config.yml
```

## 2. Special bits: setuid, setgid, sticky

| Bit       | Octal  | On a file                                           | On a directory                                       |
|-----------|--------|-----------------------------------------------------|------------------------------------------------------|
| setuid    | 4000   | Runs as file **owner**, regardless of caller        | (Ignored on Linux)                                   |
| setgid    | 2000   | Runs as file **group**                              | New files inherit the directory's **group**         |
| sticky    | 1000   | (Ignored)                                           | Only the owner may delete their own files (`/tmp`) |

Dangers:

- A setuid-root binary with a bug gives local root. Minimise them.
- Shell scripts ignore setuid on Linux (kernel safety), so attackers must
  find a vulnerable C binary. Still: do not set the bit yourself.
- setgid on a directory is useful for shared project folders so that all
  new files land in the project group.

```bash
# Set setgid on a shared directory so new files inherit 'devs'
sudo chgrp devs /srv/project
sudo chmod 2775 /srv/project
```

## 3. Default umask

`umask` subtracts from `0777` (dirs) or `0666` (files). Tight prod default:
`027` — files become `640`, directories become `750`, other users get nothing.

```text
# /etc/login.defs
UMASK           027
USERGROUPS_ENAB no     # don't auto-create per-user groups
```

```bash
# /etc/profile.d/umask.sh  — belt-and-braces
umask 027
```

Per-user override via `~/.bashrc` is fine for developers but production
service accounts should inherit the system default.

## 4. Dangerous setuid binaries

Audit all setuid/setgid programs on the host regularly. Anything unexpected
is a red flag.

```bash
# Every setuid file
sudo find / -xdev -type f -perm -4000 -ls 2>/dev/null

# setgid files
sudo find / -xdev -type f -perm -2000 -ls 2>/dev/null

# Both, combined
sudo find / -xdev -type f \( -perm -4000 -o -perm -2000 \) -ls 2>/dev/null
```

Expected on a minimal Debian 12 server (baseline — vary the list per host):

```text
/usr/bin/chfn        /usr/bin/chsh        /usr/bin/gpasswd
/usr/bin/mount       /usr/bin/newgrp      /usr/bin/passwd
/usr/bin/su          /usr/bin/sudo        /usr/bin/umount
/usr/lib/openssh/ssh-keysign
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
```

Checksum this list, ship it to your config management, and alarm on diffs.

Strip setuid from a binary you do not need:

```bash
sudo chmod u-s /usr/bin/chsh
```

Mount partitions `nosuid` wherever setuid is not legitimately needed:

```text
# /etc/fstab
UUID=...  /tmp         ext4  defaults,nodev,nosuid,noexec   0 2
UUID=...  /var         ext4  defaults,nodev,nosuid          0 2
UUID=...  /home        ext4  defaults,nodev,nosuid          0 2
UUID=...  /var/tmp     ext4  defaults,nodev,nosuid,noexec   0 2
UUID=...  /dev/shm     tmpfs defaults,nodev,nosuid,noexec   0 0
```

## 5. World-writable files

World-writable files let any local user overwrite them. On a shared box
this is an instant escalation vector.

```bash
# Find and list world-writable files (excluding sticky-bit dirs like /tmp)
sudo find / -xdev -type f -perm -0002 -ls 2>/dev/null

# World-writable directories without sticky bit (bad)
sudo find / -xdev -type d -perm -0002 ! -perm -1000 -ls 2>/dev/null
```

Fix:

```bash
sudo chmod o-w /path/to/file
```

## 6. Orphan files (no owner / no group)

When a user is deleted but their files remain, the filesystem holds raw
UIDs with no name. These are perfect hiding places for attacker data.

```bash
sudo find / -xdev \( -nouser -o -nogroup \) -ls 2>/dev/null
```

Assign them to a specific audit group or delete them, depending on policy.

## 7. chmod and chown patterns

Recursive changes are dangerous. Use `find` to apply different modes to
directories and files:

```bash
# Directories: 750, files: 640
sudo find /srv/app -type d -exec chmod 750 {} +
sudo find /srv/app -type f -exec chmod 640 {} +

# Ownership: owner root, group www-data
sudo chown -R root:www-data /srv/app
```

Never use a blind `chmod -R 777`. It breaks SSH (`~/.ssh` must be `700`),
breaks sudo (`sudoers.d` must be `440`), and opens every file to the world.

## 8. POSIX ACLs (setfacl / getfacl)

When the three-triplet model is not enough — for example, "the `www-data`
user needs read access to a file owned by `deploy:deploy` without joining
the `deploy` group" — use POSIX ACLs.

Ext4 on Debian/Ubuntu has `acl` enabled by default; verify with
`tune2fs -l /dev/sda1 | grep -i options`.

```bash
# Grant www-data read on a single file
sudo setfacl -m u:www-data:r /srv/app/config.yml
getfacl /srv/app/config.yml

# Grant a group rwx on a directory
sudo setfacl -R -m g:devs:rwx /srv/project

# Inheritance: any file created in here inherits these ACLs
sudo setfacl -R -d -m g:devs:rwx /srv/project
sudo setfacl -R -d -m u:deploy:rx /srv/project

# Remove
sudo setfacl -x u:www-data /srv/app/config.yml
sudo setfacl -b /srv/app/config.yml      # wipe all ACLs
```

An `+` in `ls -l` indicates extended ACLs are present:

```text
-rw-r-----+ 1 deploy deploy 512 Mar 10 14:02 config.yml
```

ACL mask: the `mask::` line in `getfacl` output caps every non-owner entry.
If the mask is `r--`, a `u:www-data:rwx` entry is effectively `r--`.

## 9. Extended attributes (chattr / lsattr)

Ext4 supports file flags beyond ACLs. The most important security flag is
`i` — immutable: the file cannot be modified, renamed, deleted, or linked
until the flag is removed. Useful for critical config.

```bash
sudo chattr +i /etc/resolv.conf
lsattr /etc/resolv.conf
# ----i---------e------- /etc/resolv.conf

# Remove immutability when you need to edit
sudo chattr -i /etc/resolv.conf
```

Other flags of interest:

- `a` — append-only. For log files that must never be rewritten.
- `A` — no atime updates. Performance win, not a security win.
- `u` — undelete tracking (rarely used in production).

Immutability is a speed bump, not a wall: root can always remove the flag.
It prevents accidental deletion, mis-typed `rm`, and a certain class of
automated malware that does not escalate capabilities properly.

## 10. Securing /tmp

`/tmp` is the single most-abused directory on any Linux host. Protections:

1. Give it its own partition (or a tmpfs mount).
2. Mount it with `nodev,nosuid,noexec`.
3. Enforce the sticky bit so users can only delete their own files.

```text
# /etc/fstab — tmpfs option
tmpfs  /tmp  tmpfs  defaults,nodev,nosuid,noexec,size=2G,mode=1777  0 0
```

```bash
sudo systemctl daemon-reload
sudo mount -o remount /tmp
mount | grep ' /tmp '
```

Some package installers temporarily need executable `/tmp`; remount rw
for the duration of the upgrade, not permanently.

## 11. Securing system directories

| Path           | Mode  | Owner       | Notes                           |
|----------------|-------|-------------|---------------------------------|
| `/etc/passwd`  | 0644  | root:root   | World-readable by design.       |
| `/etc/shadow`  | 0640  | root:shadow | Password hashes. Never world r. |
| `/etc/gshadow` | 0640  | root:shadow | Group passwords.                |
| `/etc/group`   | 0644  | root:root   | World-readable by design.       |
| `/etc/sudoers` | 0440  | root:root   | Read-only, even for root.       |
| `/etc/sudoers.d/*` | 0440 | root:root | Same.                           |
| `/root`        | 0700  | root:root   | Root's home.                    |
| `/boot`        | 0700  | root:root   | Or mount read-only via fstab.   |
| `/etc/ssh/sshd_config` | 0600 | root:root | SSH daemon config.          |
| `/var/log`     | 0755  | root:root   | Individual logs often 0640.     |

Verify and auto-fix:

```bash
sudo chown root:root   /etc/passwd /etc/group /etc/sudoers
sudo chown root:shadow /etc/shadow /etc/gshadow
sudo chmod 644 /etc/passwd /etc/group
sudo chmod 640 /etc/shadow /etc/gshadow
sudo chmod 440 /etc/sudoers
sudo chmod 700 /root
```

## 12. Filesystem-level encryption

- **LUKS (full-disk).** Enable at install for any host running off-site.
  Protects against a thief walking off with the disk, not against a live
  compromise. Unlock with a password at boot, or use TPM2 auto-unlock
  via `systemd-cryptenroll` on modern Debian.
- **`fscrypt` / `ecryptfs`** for per-user `/home` directories. Useful on
  laptops, rarely on servers.
- **Application-level encryption** (MySQL TDE, file-level `age`, or GPG)
  for individual secrets at rest on shared machines.

```bash
# LUKS status (existing volume)
sudo cryptsetup status cryptroot
sudo cryptsetup luksDump /dev/nvme0n1p3

# Enroll a TPM2 slot so the disk auto-unlocks at boot on the same hardware
sudo systemd-cryptenroll --tpm2-device=auto /dev/nvme0n1p3
```

## 13. Anti-patterns

- **`chmod -R 777 /path`.** Lazy, catastrophic. Never do this.
- **Recursive chmod on system dirs.** Breaks setuid bits, breaks `/root`.
- **Writable `/etc`, writable `/boot`.** Turns any RCE into a persistent root.
- **Leaving setuid on custom binaries.** Use capabilities or a systemd
  service instead (see `selinux-apparmor.md` §11).
- **Editing secrets with `sudo vi` under a loose umask.** The file ends up
  world-readable. Set `umask 027` first, or edit via `sudoedit`.
- **Storing `.env` at mode `0644`.** Must be `0640` or tighter, and never
  owned by a web-accessible user.
- **Ignoring ACL mask.** You set `u:www-data:rwx`, but the mask is `r--`,
  so the effective permission is `r--`. Check `getfacl` output.

## Cross-references

- `references/users-groups-sudo.md` — account creation and `umask` defaults
- `references/pam-authentication.md` — `pam_umask` enforcement at login
- `references/selinux-apparmor.md` — MAC complements DAC, see §1
- `references/kernel-hardening.md` — mount options, `hidepid`, sysctls
- `mysql-administration` skill — datadir permissions and mode
- `network-security` skill — TLS certificate file modes (`0600`)
