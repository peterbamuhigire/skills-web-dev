# Rootkit Detection on Debian/Ubuntu

Scanning for known rootkits and post-compromise artefacts on self-managed
Debian 12 and Ubuntu 24.04 hosts, plus a runbook for confirmed infections.

## What rootkits do

A rootkit is any piece of malware designed to hide itself and maintain
privileged access. Classic rootkit behaviour:

- Hide files, directories, and processes from userspace tools (`ls`, `ps`)
- Hide network sockets from `ss`, `netstat`, `lsof`
- Install a backdoor listener bound to a high port or knock-protected
- Persist through reboots via cron, systemd units, initramfs, or kernel modules
- Intercept syscalls via a loadable kernel module (LKM rootkit)
- Intercept library calls via `LD_PRELOAD` in `/etc/ld.so.preload`
- Tamper with `/sbin/sshd`, `/bin/login`, and common admin binaries

LKM rootkits are the hardest to detect — they modify the kernel's own
data structures, so tools that ask the kernel "what is running" get lies
back. This is why rootkit detection relies on cross-checks (comparing
multiple kernel interfaces) and known-signature matching, not on a single
source of truth.

## Detection tool landscape

| Tool | Approach | Notes |
|---|---|---|
| **rkhunter** | Signature + heuristic | Debian package, cron-friendly, writes to `/var/log/rkhunter.log` |
| **chkrootkit** | Signature + cross-check | Debian package, minimal deps, runs in minutes |
| **Lynis** | Hardening audit + rootkit markers | Finds rootkits incidentally as part of general audit |
| **Wazuh** | Centralised, real-time | Combines rootcheck + syscheck + audit data |
| **ClamAV** | General AV | Catches common Linux malware, overlaps with rootkit detection |

Best practice: run **both** rkhunter and chkrootkit. They use different
signature databases and cross-checks, so a rootkit hidden from one may still
be flagged by the other.

## rkhunter — install and use

```bash
sudo apt install -y rkhunter

# Update signature database
sudo rkhunter --update

# Update file properties DB from the current (presumed clean) system
sudo rkhunter --propupd

# Run a full check
sudo rkhunter --check --skip-keypress
```

Configuration lives in `/etc/rkhunter.conf`. Key settings:

| Setting | Purpose |
|---|---|
| `MIRRORS_MODE=0` | Use any mirror for signature updates |
| `UPDATE_MIRRORS=1` | Update mirror list on each run |
| `WEB_CMD=""` | Leave empty on Debian 12 (distro-bundled curl is fine) |
| `ALLOW_SSH_ROOT_USER=no` | Warn if sshd is configured for root login |
| `ALLOWHIDDENDIR=/etc/.java` | Whitelist legitimate hidden dirs |
| `SCRIPTWHITELIST=/usr/bin/egrep` | Whitelist legitimate scripts that fail heuristics |
| `MAIL-ON-WARNING=root` | Email alerts to the specified address |

Always run `rkhunter --propupd` immediately after a fresh OS install or any
legitimate package upgrade. Without this, rkhunter complains about every
legitimately-changed file on the next scan.

Schedule via systemd timer (same pattern as AIDE):

```ini
# /etc/systemd/system/rkhunter-check.service
[Unit]
Description=rkhunter daily scan

[Service]
Type=oneshot
ExecStart=/usr/bin/rkhunter --cronjob --update --quiet
```

```ini
# /etc/systemd/system/rkhunter-check.timer
[Unit]
Description=Daily rkhunter scan
[Timer]
OnCalendar=daily
RandomizedDelaySec=30m
[Install]
WantedBy=timers.target
```

## chkrootkit — install and use

```bash
sudo apt install -y chkrootkit
sudo chkrootkit
```

Output is one line per check. Interpreting it:

- `not infected` — clean
- `INFECTED` — a known signature matched; investigate immediately
- `not tested` — check skipped (missing binary, unsupported on this arch)
- `not found` — file not present (often expected)
- `nothing found` — no suspicious entries

chkrootkit cross-checks `ps` output against `/proc`, and cross-checks `ss`
against `/proc/net/tcp`. Mismatches suggest kernel-level hiding.

Schedule it daily alongside rkhunter and forward any `INFECTED` lines to
your alert channel:

```bash
sudo chkrootkit 2>&1 | grep -E 'INFECTED|Vulnerable' | \
  logger -t chkrootkit -p auth.crit
```

## False positives

Both tools regularly flag legitimate packages as suspicious. Common causes:

- Package maintainer updates a binary between rkhunter signature releases
- A sysadmin adds a hidden `.cache` directory that trips the hidden-dir check
- Custom build of `openssh-server` changes the expected hash
- Logwatch, CUPS, and Samba all create files in locations rkhunter watches

Whitelist carefully after investigating each warning. **Do not** wholesale
whitelist a category of files; whitelist the specific file path and only
after confirming it is legitimate.

Always keep signature databases current:

```bash
sudo rkhunter --update            # rkhunter
sudo freshclam                    # ClamAV
# chkrootkit has no remote DB; update via apt
```

## Host-level red flags beyond signatures

Signature-based tools catch *known* rootkits. The experienced SaaS operator
also looks for behavioural anomalies that no signature database has yet:

### Process / memory anomalies

```bash
# Processes visible in /proc but not in `ps` — classic LKM rootkit sign
ls /proc | grep -E '^[0-9]+$' | sort -n > /tmp/proc.txt
ps -eo pid --no-headers | sort -n > /tmp/ps.txt
diff /tmp/proc.txt /tmp/ps.txt
```

### Socket anomalies

```bash
# Connections in ss but nothing owning them in /proc/<pid>/net
sudo ss -tnp
# Any listening port without an obvious service?
sudo ss -ltnp
```

### SUID binaries in unexpected locations

```bash
sudo find / -xdev -type f -perm -4000 -o -perm -2000 2>/dev/null
# SUID binaries should only live in /usr/bin, /usr/sbin, /bin, /sbin
```

### Unusual scheduled tasks

```bash
for u in $(cut -d: -f1 /etc/passwd); do sudo crontab -l -u "$u" 2>/dev/null; done
ls -la /etc/cron.* /etc/crontab /etc/systemd/system/*.timer
```

### ld.so.preload backdoor

```bash
# Should be empty or absent on a clean system
cat /etc/ld.so.preload 2>/dev/null
```

### Kernel modules

```bash
lsmod | sort
# Compare against a known-good list for this kernel version
```

### Recently changed system binaries

```bash
sudo find /bin /sbin /usr/bin /usr/sbin -xdev -mtime -7 -type f
```

## What to do when a rootkit is found

Assume the worst: if any tool reports a genuine infection, the running kernel
may be compromised. Do not trust what that kernel tells you.

### Runbook

1. **Isolate the host immediately.** Drop all network traffic at the cloud
   firewall or hypervisor level. Do not merely run `ifconfig eth0 down` on
   the host — a rootkit may intercept and lie.
2. **Preserve evidence.** Snapshot the VM disk and memory. Export the
   snapshot to read-only storage for forensics. Capture running process
   state by reading from `/proc` directly, not via `ps`.
3. **Stop trusting on-host binaries.** Use a statically-linked busybox
   or a rescue ISO with a known-good toolset. Do not run package manager
   commands on the compromised system — the rootkit may have hooked them.
4. **Identify the initial compromise vector.** Review:
   - `/var/log/auth.log` for brute-force or key-based logins
   - Web application logs for injection / upload exploits
   - Recently added user accounts and SSH keys (`/root/.ssh/authorized_keys`)
   - The timing of new files discovered above
5. **Rebuild from a known-good gold image.** Provision a fresh host. Do not
   attempt to clean the compromised one in place — rootkits can survive
   package reinstallation.
6. **Restore data from a pre-compromise backup.** Verify the backup was
   taken before the earliest known indicator of compromise.
7. **Rotate every credential the compromised host held.** SSH host keys,
   database passwords, API tokens, TLS certificates, cloud IAM keys.
8. **Post-incident review.** Write up what worked, what didn't, and which
   detection or preventive control would have caught this sooner.

## Prevention is better than detection

Detection tools are a safety net. Build the first line of defence at
install time:

- **Minimise attack surface.** Remove every package and service not strictly
  required. Each one is a potential entry point.
- **Apply Mandatory Access Control.** AppArmor (Ubuntu/Debian default) or
  SELinux confines processes so a compromised web server cannot read `/etc/shadow`.
- **Kernel module signing / lockdown.** Set `kernel.kexec_load_disabled=1`
  and boot with `lockdown=integrity` (see `kernel-sysctl-hardening.md`).
  This stops an attacker from loading an unsigned LKM rootkit.
- **Disable unused filesystem and network modules.** See the modprobe
  blacklist in `kernel-sysctl-hardening.md`.
- **Keep the system patched.** Use `unattended-upgrades` for security updates.
- **Strong SSH defaults.** Key-only auth, `PermitRootLogin no`, Fail2ban.
- **Run auditd, AIDE, rkhunter, and chkrootkit together.** Each catches
  what the others miss.

## Anti-patterns

- **Trusting tools running on an infected host.** If the kernel is owned,
  everything userspace says is suspect. Collect forensics from a rescue image.
- **Running rootkit scanners once per year.** Attackers do not schedule
  their activity around your audit calendar. Run daily via systemd timer.
- **No off-host alerting.** A rootkit that sees `rkhunter` writing a warning
  to `/var/log/rkhunter.log` will delete that log before you see it. Ship
  the warning to a central log host immediately.
- **Acting on first `INFECTED` line without verification.** False positives
  happen. Confirm with a second tool and manual cross-checks before nuking
  a production host.
- **Cleaning in place instead of rebuilding.** Rootkits are specifically
  designed to defeat in-place removal. Assume the host is unrecoverable.
- **Not re-running `rkhunter --propupd` after patch day.** Every legitimate
  apt upgrade causes a rash of warnings that mask real signals.

## Cross-references

- `linux-security-hardening/SKILL.md` — overall hardening workflow
- `linux-security-hardening/references/kernel-sysctl-hardening.md` —
  kernel-level rootkit prevention (lockdown, module signing, sysctls)
- `linux-security-hardening/references/file-integrity.md` — AIDE catches
  binary tampering before a rootkit scanner has a signature for it
- `linux-security-hardening/references/auditd-logging.md` — audit kernel
  module load events to spot LKM rootkit installation in real time
- `network-security/SKILL.md` — egress filtering to contain a compromise
- `database-reliability/SKILL.md` — backup verification for rebuild workflow
