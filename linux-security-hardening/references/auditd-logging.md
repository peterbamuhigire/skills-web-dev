# Auditd Logging on Debian/Ubuntu

Kernel-level audit subsystem for tracking security-relevant events on self-managed
Debian 12 and Ubuntu 24.04 servers. Complements syslog; does not replace it.

## What auditd does

The Linux kernel audit subsystem can record syscalls, file accesses, and security
events as they happen. The `auditd` user-space daemon reads those events from the
kernel audit buffer and writes them to disk. Unlike syslog, which records whatever
an application chooses to log, auditd captures events at the kernel boundary, so
an attacker cannot hide activity from it by tampering with an application's logger.

Typical use cases:

- Prove *who* changed `/etc/passwd` or `/etc/sudoers` and *when*
- Detect unauthorised loading of kernel modules
- Record every invocation of `sudo` with full command line
- Meet PCI-DSS, HIPAA, ISO 27001, and CIS benchmark audit requirements
- Feed a SIEM (Wazuh, Loki, Elastic) with host-level security telemetry

Auditd is not a performance profiler. Rules are evaluated for every matching event,
so over-broad rules on busy systems add measurable CPU overhead.

## Install on Debian/Ubuntu

```bash
sudo apt update
sudo apt install -y auditd audispd-plugins
sudo systemctl enable --now auditd
sudo systemctl status auditd
```

`audispd-plugins` installs the dispatcher plugins used to forward events to syslog,
remote log hosts, or SIEM agents. `auditd` pulls in `audispd-plugins` as a
recommended package on Debian 12 and Ubuntu 24.04.

## Architecture

```
User process ──syscall──▶ Kernel (audit subsystem)
                              │
                              ▼
                         audit buffer
                              │
                              ▼
                         auditd (root)
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
  /var/log/audit/audit.log   audispd plugins   exit notifier
                              (syslog, remote, af_unix, ...)
```

Important properties:

- The kernel generates events even if auditd is not running; events accumulate in
  a ring buffer and are lost once the buffer fills. This is why `auditd` must start
  early in boot.
- `auditd` writes to `/var/log/audit/audit.log`. Only root can read it.
- Dispatch plugins live in `/etc/audit/plugins.d/` and let you fan events out to
  additional destinations without writing to disk twice.

## Rule syntax basics

Rules live in `/etc/audit/rules.d/*.rules` (one or more files, merged at load
time) and in the single compiled file `/etc/audit/audit.rules`. Prefer dropping
files into `rules.d/` so that packages can add rules without conflicting.

Two rule families:

### File watches

```text
-w <path> -p <permissions> -k <keyname>
```

- `-w` — the file or directory to watch
- `-p` — which access types to log: `r` (read), `w` (write), `x` (execute),
  `a` (attribute change). Combine as needed, e.g. `-p wa`.
- `-k` — a short key used to tag matching events so you can search later

Example — detect any change to `/etc/sudoers`:

```text
-w /etc/sudoers -p wa -k sudoers_change
```

### Syscall audit rules

```text
-a always,exit -F arch=b64 -S <syscall>[,<syscall>...] -F <filter> -k <keyname>
```

- `-a always,exit` — record the event when the syscall returns
- `-F arch=b64` — match 64-bit architecture; add a second rule with `arch=b32`
  on systems that still run 32-bit binaries
- `-S` — one or more syscall names
- `-F` — additional filters: `auid>=1000`, `auid!=unset`, `euid=0`, etc.

Example — record every call to `init_module`, `finit_module`, and `delete_module`:

```text
-a always,exit -F arch=b64 -S init_module,finit_module,delete_module -k module_load
```

### Locking rules

Append `-e 2` as the last line to make the rule set immutable until reboot.
This prevents an attacker with temporary root from silently disabling auditing.

```text
-e 2
```

Rules can still be read (`auditctl -l`) while locked, but any attempt to add or
delete rules fails with `EPERM`.

## Reference ruleset

Save this as `/etc/audit/rules.d/99-hardening.rules`. It covers identity,
authentication, SSH, kernel modules, mounts, and network config on Debian/Ubuntu.

```text
## Delete any rules loaded previously
-D

## Buffer size — increase for busy hosts
-b 8192

## Failure mode: 1 = printk, 2 = panic; prefer 1 in production
-f 1

## Ignore noisy kernel subsystems
-a never,exit -F arch=b64 -S fork,vfork,clone

## Identity changes
-w /etc/passwd       -p wa -k identity
-w /etc/shadow       -p wa -k identity
-w /etc/group        -p wa -k identity
-w /etc/gshadow      -p wa -k identity
-w /etc/sudoers      -p wa -k sudoers
-w /etc/sudoers.d/   -p wa -k sudoers

## Authentication logs
-w /var/log/auth.log -p wa -k auth_log
-w /var/log/faillog  -p wa -k auth_log
-w /var/log/lastlog  -p wa -k auth_log
-w /var/log/tallylog -p wa -k auth_log

## Successful and failed sudo (both success and failure)
-a always,exit -F arch=b64 -S execve -F path=/usr/bin/sudo -k sudo_exec
-w /var/log/sudo.log -p wa -k sudo_log

## SSH daemon configuration
-w /etc/ssh/sshd_config   -p wa -k sshd
-w /etc/ssh/sshd_config.d -p wa -k sshd

## Kernel module operations
-w /sbin/insmod   -p x -k module_tools
-w /sbin/rmmod    -p x -k module_tools
-w /sbin/modprobe -p x -k module_tools
-a always,exit -F arch=b64 -S init_module,finit_module,delete_module -k module_load

## Mount operations (detect container escape, USB attachment)
-a always,exit -F arch=b64 -S mount -F auid!=unset -F auid>=1000 -k mount

## Network and time config
-w /etc/hosts          -p wa -k network_config
-w /etc/hostname       -p wa -k network_config
-w /etc/network/       -p wa -k network_config
-w /etc/netplan/       -p wa -k network_config
-w /etc/systemd/timesyncd.conf -p wa -k time_config

## Cron and scheduled tasks
-w /etc/crontab      -p wa -k cron
-w /etc/cron.d/      -p wa -k cron
-w /etc/cron.daily/  -p wa -k cron
-w /etc/cron.hourly/ -p wa -k cron
-w /etc/cron.weekly/ -p wa -k cron
-w /etc/cron.monthly/ -p wa -k cron
-w /var/spool/cron/  -p wa -k cron

## Optional: record every execve from low-privilege users of curl and wget
## (uncomment after confirming overhead is acceptable)
# -a always,exit -F arch=b64 -S execve -F path=/usr/bin/curl -F auid>=1000 -k download
# -a always,exit -F arch=b64 -S execve -F path=/usr/bin/wget -F auid>=1000 -k download

## Lock the rule set — must come last
-e 2
```

### CIS-aligned ruleset

The CIS Debian and Ubuntu Benchmarks publish a ready-made `cis.rules` file
covering most of their audit requirements. Starting points on a fresh install:

```bash
ls /usr/share/doc/auditd/examples/rules/
# 10-base-config.rules
# 11-loginuid.rules
# 30-stig.rules   # STIG-aligned; close to CIS
# 31-privileged.rules
# 42-injection.rules
# 43-module-load.rules
```

Copy only the pieces relevant to your environment into `/etc/audit/rules.d/`.
Copying every example rule at once on a busy SaaS host produces tens of thousands
of events per minute and quickly fills the audit log partition.

## Loading and testing rules

```bash
# Compile and load rules from /etc/audit/rules.d/
sudo augenrules --load

# List currently loaded rules
sudo auditctl -l

# Show kernel audit status (enabled flag, backlog, lost events)
sudo auditctl -s

# Temporarily add an ad-hoc rule (does not survive reboot)
sudo auditctl -w /tmp/testfile -p wa -k test_watch
```

If you see `Operation not permitted` from `augenrules`, the rule set is already
locked (`-e 2`). Reboot is required.

## Searching audit logs

`ausearch` and `aureport` are the two tools you will use every day.

```bash
# Search by key
sudo ausearch -k sudoers

# User login events
sudo ausearch -m USER_LOGIN

# Everything since midnight
sudo ausearch --start today

# Narrow to a time window
sudo ausearch --start today 08:00:00 --end today 12:00:00

# All events for a specific user (by audit UID)
sudo ausearch -ua 1001

# Failed executions
sudo ausearch -sv no

# Pipe through aureport for a readable summary
sudo ausearch -k identity | aureport -f -i
```

`aureport` gives tallies:

```bash
sudo aureport --summary          # top-level counts
sudo aureport -au --summary      # authentication attempts
sudo aureport -x --summary       # executables invoked
sudo aureport -f --failed        # failed file accesses
sudo aureport -m                 # account modifications
```

The `-i` flag on `ausearch` resolves UIDs and syscall numbers into names.

## Log rotation and retention

Configured in `/etc/audit/auditd.conf`. The important keys:

| Key | Meaning | Suggested value |
|---|---|---|
| `max_log_file` | MB per log file before rotation | `100` |
| `num_logs` | How many rotated files to keep | `10` |
| `max_log_file_action` | What to do when rotation limit is hit | `ROTATE` |
| `space_left` | MB remaining before warning action | `500` |
| `space_left_action` | Warning action | `SYSLOG` or `EMAIL` |
| `admin_space_left` | MB remaining before critical action | `100` |
| `admin_space_left_action` | Critical action | `SUSPEND` or `SINGLE` |
| `disk_full_action` | Disk full behaviour | `SUSPEND` (not `HALT` in production) |
| `disk_error_action` | On write errors | `SYSLOG` |
| `flush` | Disk sync policy | `INCREMENTAL_ASYNC` |
| `freq` | Records between flushes | `50` |

Apply with `sudo systemctl restart auditd`. Do not use `kill -HUP`; auditd
rejects most signals by design.

Mount `/var/log/audit` on its own filesystem so that a flood of audit events
cannot fill the root partition and take the host down.

## Shipping audit logs off-host

Audit logs that only live on the compromised host are useless after the attacker
clears them. Ship them off the host.

### Via syslog plugin

`/etc/audit/plugins.d/syslog.conf`:

```text
active = yes
direction = out
path = /sbin/audisp-syslog
type = always
args = LOG_INFO
format = string
```

Then configure rsyslog (or syslog-ng) to forward the `local1` facility to a
remote aggregator (Loki, rsyslog relay, SigNoz otel-collector).

### Via audisp-remote plugin

`/etc/audit/plugins.d/au-remote.conf`:

```text
active = yes
direction = out
path = /sbin/audisp-remote
type = always
format = string
```

Configure the remote endpoint in `/etc/audit/audisp-remote.conf` with
`remote_server`, `port = 60`, and `transport = tcp`. Use TLS where available.

### Wazuh

The Wazuh agent reads `/var/log/audit/audit.log` natively — no plugin needed.
Deploy the agent and add a `<localfile>` block pointing at the audit log in the
agent's `ossec.conf`. This is usually the lowest-effort option for SaaS fleets.

## Performance considerations

- Every rule is evaluated per syscall. Prune rules you don't actually need.
- `-F auid>=1000` skips system accounts and dramatically reduces noise.
- Use `-a never,exit` rules at the top of the ruleset to exclude known-noisy
  paths (build pipelines, caches, large log directories).
- Watch `auditctl -s` for a rising `lost` counter — events lost because the
  buffer filled. Increase `-b` (buffer size) or prune rules.
- On 8-core web servers, a well-scoped ruleset costs under 2% CPU. A bad
  ruleset (watching every file under `/var/log`) costs 30%+.

## Anti-patterns

- **Auditing everything**. Produces gigabytes of noise, hides real events, and
  strains disk I/O. Start narrow; expand as needed.
- **No off-host storage**. An attacker who gets root can delete the local audit
  log. Ship events elsewhere.
- **No alerting**. Logs nobody reads are just disk waste. Hook ausearch into a
  daily report or forward to a SIEM with alert rules.
- **`-e 0` or missing lock line**. Leaves the rule set mutable at runtime.
  Always end with `-e 2` in production.
- **Auditing `/tmp` or `/var/tmp`**. On a busy box those directories see
  thousands of events per second. Blacklist them explicitly.
- **No log rotation on a small root partition**. One busy day will fill `/` and
  crash the host.

## Cross-references

- `linux-security-hardening/SKILL.md` — overall hardening workflow
- `linux-security-hardening/references/kernel-sysctl-hardening.md` — kernel tunables
- `linux-security-hardening/references/file-integrity.md` — AIDE/FIM integration
- `network-security/SKILL.md` — firewall and network logging
- `cicd-devsecops/SKILL.md` — shipping host logs into the CI/CD pipeline
- `claude-guides/database-standards.md` — audit tables for database events
