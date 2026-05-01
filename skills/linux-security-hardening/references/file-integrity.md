# File Integrity Monitoring (FIM) on Debian/Ubuntu

File Integrity Monitoring detects unauthorised changes to system binaries,
configuration, and trust stores on self-managed Debian 12 and Ubuntu 24.04 hosts.

## What FIM solves

An attacker who gains root (or even unprivileged code execution followed by a
privilege escalation) typically leaves traces:

- A modified `/usr/sbin/sshd` with a hidden backdoor password
- A new SUID binary in `/tmp` or `/var/tmp`
- A tampered CA certificate in `/etc/ssl/certs/`
- An added line in `/etc/passwd` or `/etc/sudoers.d/`
- A replaced `ls`, `ps`, or `netstat` that hides attacker artefacts

Application logs and auditd capture *events* as they happen. FIM captures
*state* — it takes a cryptographic fingerprint of every important file when
the system is known good, then periodically recomputes fingerprints and flags
any that have drifted. Together, auditd and FIM answer "who changed this" and
"what has changed since the baseline".

FIM is a compliance requirement under PCI-DSS (Requirement 11.5), HIPAA
Security Rule Technical Safeguards, and the CIS Benchmarks for all major
Linux distributions.

## Tool landscape

| Tool | Notes |
|---|---|
| **AIDE** | Default on Debian; free, lightweight, declarative config; no central console |
| **Tripwire** | Legacy, commercial; open-source edition is mostly unmaintained |
| **Samhain** | Open-source, centralised console, harder to configure |
| **Wazuh (syscheck module)** | Enterprise-grade, centralised dashboard, real-time via inotify, integrates with auditd |
| **osquery FIM pack** | Query-style FIM via SQL; good for fleet-wide spot checks |

For a single Debian/Ubuntu SaaS host, AIDE is the right default. For fleets of
10+ hosts, switch to Wazuh — the operational overhead of managing AIDE on
every host and chasing false positives becomes significant.

## AIDE — deep dive

### Install

```bash
sudo apt update
sudo apt install -y aide aide-common
```

On Debian, the `aide-common` package supplies helper scripts (`aideinit`,
`aide.wrapper`) and the default config layout under `/etc/aide/`.

### Configuration layout

```
/etc/aide/
├── aide.conf                # main config, includes everything below
├── aide.conf.d/             # drop-in rules (one file per topic)
│   ├── 10_aide_vim
│   ├── 31_aide_ssh
│   ├── 70_aide_cron
│   └── ... (many more)
└── aide.settings.d/         # per-distro tunables
```

Each drop-in file contains rules of the form:

```text
<path regex>   <rule group>
```

For example, `31_aide_ssh` will contain something like:

```text
/etc/ssh                CONF_FILES
/etc/ssh/sshd_config    CONF_FILES
```

`CONF_FILES` is a macro that expands to the set of attributes to check
(`p+i+u+g+s+c+md5+sha256` — permissions, inode, owner, group, size, ctime, MD5,
SHA-256). Debian ships several macros: `FIPSR` (strict), `NORMAL`, `DATAONLY`
(size + mtime only, for log directories).

### Initial baseline

```bash
# Build the first database — runs for 3-10 minutes on a typical VM
sudo aideinit

# aideinit puts the new DB at aide.db.new; promote it to the active DB
sudo mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db
```

### Run a check

```bash
sudo aide --check
# or via Debian's wrapper (uses the packaged config):
sudo aide.wrapper --check
```

Exit codes:

- `0` — no changes
- `1..7` — a combination of added, removed, or changed files (bitmask)

Typical output:

```text
AIDE found differences between database and filesystem!!
Summary:
  Total number of entries:   118420
  Added entries:             0
  Removed entries:           0
  Changed entries:           3
---------------------------------------------------
Changed entries:
---------------------------------------------------
f = ... p... : /etc/hostname
f = ... s... : /var/log/wtmp
f = ... mc.. : /etc/shadow
```

### What Debian's default AIDE config watches

- All files under `/bin`, `/sbin`, `/usr/bin`, `/usr/sbin`, `/usr/local/bin`,
  `/usr/local/sbin` — every binary on the `PATH`
- `/boot` — kernel images and initramfs
- `/etc` — all system configuration
- `/lib`, `/lib64`, `/usr/lib` — shared libraries and kernel modules
- `/root` — root's home directory (except hash-excluded entries)
- Log directories like `/var/log` are mostly excluded to avoid constant noise

Verify what is in scope with:

```bash
sudo aide --config-check
```

## Custom rules

Add your own rules in a new file under `/etc/aide/aide.conf.d/`. Example —
watch a custom application's code and config but not its cache:

```text
# /etc/aide/aide.conf.d/80_app_acme
/opt/acme/app/bin       FIPSR
/opt/acme/app/config    CONF_FILES
!/opt/acme/app/cache
!/opt/acme/app/tmp
!/opt/acme/app/logs
```

Rules starting with `!` exclude a path from the scan. Longest match wins.

Rebuild the DB after any rules change:

```bash
sudo aideinit && sudo mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db
```

## Running AIDE on schedule

Debian's `cron-aide` package installs a daily cron job that mails the result
to root. For servers that don't have local mail, use a systemd timer and ship
the output to syslog or a webhook instead.

`/etc/systemd/system/aide-check.service`:

```ini
[Unit]
Description=AIDE file integrity check
After=local-fs.target

[Service]
Type=oneshot
Nice=19
IOSchedulingClass=idle
ExecStart=/usr/bin/aide.wrapper --check
# Exit codes 0 and 1..7 are "normal" FIM outcomes; only real errors should fail
SuccessExitStatus=0 1 2 3 4 5 6 7
```

`/etc/systemd/system/aide-check.timer`:

```ini
[Unit]
Description=Daily AIDE integrity check

[Timer]
OnCalendar=daily
Persistent=true
RandomizedDelaySec=30m

[Install]
WantedBy=timers.target
```

Enable it:

```bash
sudo systemctl enable --now aide-check.timer
sudo systemctl list-timers | grep aide
```

## Alerting on drift

A daily report nobody reads is worthless. Route AIDE output to a channel an
on-call human will see.

### Syslog

Wrap the check in a script that pipes to `logger`:

```bash
#!/bin/bash
OUT=$(aide.wrapper --check 2>&1)
RC=$?
if [ $RC -ne 0 ]; then
  echo "$OUT" | logger -t aide -p auth.warning
fi
exit $RC
```

rsyslog (or syslog-ng) will then forward the `auth.warning` messages to the
central log aggregator you already use (Loki, Wazuh, SigNoz, etc.).

### Wazuh

Point Wazuh's `<localfile>` at AIDE output, or — better — enable Wazuh's
built-in `syscheck` module, which effectively replaces AIDE with real-time
inotify-based detection and a central dashboard. On a Wazuh-managed fleet,
most teams remove AIDE entirely.

### Ad-hoc: Slack / email webhook

On hosts without a central log pipeline, a tiny script that POSTs a summary to
a Slack incoming webhook works well:

```bash
curl -s -X POST -H 'Content-Type: application/json' \
  -d "{\"text\":\"AIDE drift on $(hostname): $(echo "$OUT" | head -20)\"}" \
  "$SLACK_WEBHOOK_URL"
```

## Baseline database integrity

The AIDE database (`/var/lib/aide/aide.db`) is the ground truth. An attacker
who modifies a system file and then runs `aide --update` can tell AIDE that
the new state is the "correct" one. Protect the DB:

1. **Read-only after baseline**. Mount `/var/lib/aide` read-only, or set the
   file immutable with `chattr +i /var/lib/aide/aide.db`. Remove the bit only
   during authorised re-baselining.
2. **Off-host copy**. After each legitimate re-baseline, copy `aide.db` to a
   known-good location (backup bucket, config management server). Compare
   periodically against the on-host copy.
3. **Hash the DB itself**. Store the DB's SHA-256 hash in a separate system
   (e.g. HashiCorp Vault, your password manager) and recompute before checks.

## Pitfalls: handling legitimate package updates

`apt upgrade` legitimately changes hundreds of files. Without a workflow, your
AIDE reports will be a wall of noise after every patch day.

The standard pre/post workflow:

```bash
# 1. Before upgrade — verify current state is clean
sudo aide.wrapper --check || { echo "AIDE reports drift; investigate before upgrading"; exit 1; }

# 2. Apply package upgrades
sudo apt update && sudo apt -y upgrade

# 3. Rebuild the baseline
sudo aideinit
sudo mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db

# 4. Refresh off-host copy
scp /var/lib/aide/aide.db backup-server:/var/backups/aide/$(hostname)-$(date +%F).db
```

Wrap this in an Ansible playbook so every patch night produces a fresh baseline
automatically. If you skip step 1, you risk baking an already-compromised
system into the "known good" DB.

## Alternative: immutable infrastructure

If your SaaS deploys via gold images or containers — build once, rotate hosts
rather than patching in place — FIM's value drops sharply. The root filesystem
of each container is read-only and its contents are hashed by the registry.
Drift detection becomes "is this container running the expected image digest",
which your Kubernetes admission controller (e.g. Kyverno, OPA) already enforces.

You still want FIM on:

- The CI/CD build hosts that produce those images
- The container host kernel and `/etc`
- Any persistent-volume mounts containing writable config

## Anti-patterns

- **Running `aide --update` blindly to "clear the noise"**. Burns your
  baseline and lets drift hide in plain sight.
- **Never re-baselining**. After six months of patch cycles, a failing check
  no longer tells you anything.
- **No alerting**. A `systemd` timer that writes to `/var/log/aide` but nobody
  reads is worse than nothing; it creates a false sense of security.
- **DB on the same host with no off-host copy**. Any attacker with root can
  rewrite the baseline and cover their tracks.
- **Watching `/var/log`, `/var/cache`, `/tmp` in detail**. Produces hundreds
  of changes per day that drown out real alerts.
- **Running AIDE during business hours on a busy DB host**. It reads every
  file in scope; on a host with large `/var/lib/mysql`, schedule it at 3am and
  use `ionice -c idle`.

## Cross-references

- `linux-security-hardening/SKILL.md` — overall hardening workflow
- `linux-security-hardening/references/auditd-logging.md` — event-time
  companion to FIM's state-time snapshots
- `linux-security-hardening/references/rootkit-detection.md` — rootkit scanners
  overlap with FIM but don't replace it
- `cicd-devsecops/SKILL.md` — image scanning as immutable-infra alternative
- `database-reliability/SKILL.md` — backup verification techniques apply to
  the AIDE baseline itself
