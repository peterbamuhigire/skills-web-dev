---
name: linux-security-hardening
description: Use when hardening a Debian/Ubuntu server — user/group/sudo hardening,
  file permission audits, PAM password policy + MFA, AppArmor mandatory access control,
  auditd system call logging, kernel sysctl hardening, file integrity monitoring (AIDE),
  rootkit detection (rkhunter/chkrootkit), unattended security patching, GRUB + UEFI
  + LUKS boot security, and CIS benchmark compliance.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Linux Security Hardening
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Use when hardening a Debian/Ubuntu server — user/group/sudo hardening, file permission audits, PAM password policy + MFA, AppArmor mandatory access control, auditd system call logging, kernel sysctl hardening, file integrity monitoring (AIDE), rootkit detection (rkhunter/chkrootkit), unattended security patching, GRUB + UEFI + LUKS boot security, and CIS benchmark compliance.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `linux-security-hardening` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Security | Server hardening checklist | Markdown doc covering user/sudo, file permissions, PAM/MFA, and auditd findings | `docs/server/hardening-checklist.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Defensive hardening for Debian 12 / Ubuntu 24.04 servers running multi-tenant SaaS. Covers the OS layer — users, permissions, PAM, mandatory access control, kernel, integrity, patching, and compliance.

**Core principle:** A fresh Debian install is not production-ready. Every server that accepts traffic needs hardening. Do it once with automation, audit it forever.

**Scope:** Linux OS security on your own servers. For network-layer defence use `network-security`. For secrets/CI hardening use `cicd-devsecops`. For app-code vulnerabilities use `web-app-security-audit`.

**Cross-references:** `network-security`, `cicd-devsecops`, `cicd-jenkins-debian`, `database-reliability`, `web-app-security-audit`

**See `references/` for:** `users-groups-sudo.md`, `file-permissions-acls.md`, `pam-authentication.md`, `selinux-apparmor.md`, `auditd-logging.md`, `kernel-sysctl-hardening.md`, `file-integrity.md`, `rootkit-detection.md`, `patch-management.md`, `boot-security.md`, `cis-benchmark-checklist.md`

## When to Use

- Before putting a fresh VPS into production
- During quarterly security audit cadence
- After a CVE affecting a library on your server
- When onboarding a new server into the fleet
- When a compliance requirement (SOC 2, ISO 27001, PCI-DSS) demands baseline hardening
- After an incident — to verify baseline still holds
- When migrating from one cloud/VPS provider to another

## Threat Model + Attack Surface

**Attack surface on a typical Debian server:**

| Layer | Attack vector | Primary defence |
|-------|---------------|-----------------|
| Boot | Single-user mode, evil maid, kernel tampering | GRUB password, Secure Boot, LUKS |
| Kernel | Privilege escalation via syscall, unsigned module | sysctl, lockdown mode, MAC, module signing |
| Filesystem | Path traversal, setuid abuse, world-writable | perms, ACLs, mount options (nosuid,noexec) |
| Users | Brute force, privilege abuse, shared accounts | PAM, sudo least-priv, MFA, password policy |
| Services | Unpatched CVE, default creds, exposed port | unattended-upgrades, service minimization |
| Process | Arbitrary code execution in an app | AppArmor, systemd sandboxing, capabilities |
| Monitoring | Attacker erases logs | auditd off-host, FIM, log integrity |

**Assume breach.** Layer defences so a single failure does not equal game over.

## The 10 Hardening Domains

| # | Domain | Reference |
|---|--------|-----------|
| 1 | Users, groups, sudo | `references/users-groups-sudo.md` |
| 2 | File permissions + ACLs | `references/file-permissions-acls.md` |
| 3 | PAM authentication | `references/pam-authentication.md` |
| 4 | Mandatory Access Control (AppArmor) | `references/selinux-apparmor.md` |
| 5 | auditd + system logging | `references/auditd-logging.md` |
| 6 | Kernel sysctl hardening | `references/kernel-sysctl-hardening.md` |
| 7 | File integrity monitoring | `references/file-integrity.md` |
| 8 | Rootkit detection | `references/rootkit-detection.md` |
| 9 | Patch management | `references/patch-management.md` |
| 10 | Boot security (GRUB, UEFI, LUKS) | `references/boot-security.md` |

Compliance: `references/cis-benchmark-checklist.md` (~60 items aligned to CIS Debian 12 benchmark).

## Baseline Hardening Checklist

Run this against every fresh Debian 12 / Ubuntu 24.04 server before accepting production traffic.

### 1. System baseline

```bash
apt update && apt full-upgrade -y
apt install -y \
  ufw nftables fail2ban \
  auditd audispd-plugins \
  unattended-upgrades needrestart apt-listchanges \
  libpam-pwquality libpam-google-authenticator \
  rkhunter chkrootkit aide aide-common \
  apparmor apparmor-utils apparmor-profiles \
  lynis debsecan
```

Enable unattended security updates with auto-reboot at a quiet hour (see `references/patch-management.md`).

### 2. Disable unused services and kernel modules

```bash
# Disable services
for svc in avahi-daemon cups rpcbind nfs-server bluetooth; do
  systemctl disable --now "$svc" 2>/dev/null || true
done

# Blacklist rare filesystem / network modules
cat > /etc/modprobe.d/blacklist-hardening.conf <<EOF
install cramfs /bin/true
install freevxfs /bin/true
install jffs2 /bin/true
install hfs /bin/true
install hfsplus /bin/true
install udf /bin/true
install dccp /bin/true
install sctp /bin/true
install rds /bin/true
install tipc /bin/true
EOF
update-initramfs -u
```

### 3. User and sudo hardening

```bash
passwd -l root                              # disable root password login
# Add each admin to sudo group; no shared accounts.
usermod -aG sudo deploy
# Edit sudoers to require pty and log IO
visudo  # add: Defaults use_pty, log_input, log_output
```

Full detail: `references/users-groups-sudo.md`

### 4. File permissions

```bash
chmod 640 /etc/shadow /etc/gshadow
chmod 644 /etc/passwd /etc/group
chmod 700 /root
# Find unexpected setuid binaries
find / -xdev -type f -perm -4000 2>/dev/null
# Find world-writable
find / -xdev -type f -perm -0002 2>/dev/null
```

Set `umask 027` globally via `/etc/login.defs`. Mount `/tmp`, `/var/tmp`, `/dev/shm` with `nodev,nosuid,noexec`. Detail: `references/file-permissions-acls.md`.

### 5. PAM password policy + lockout

Edit `/etc/security/pwquality.conf`:

```ini
minlen = 12
dcredit = -1
ucredit = -1
lcredit = -1
ocredit = -1
retry = 3
enforce_for_root
```

Enable faillock in `/etc/pam.d/common-auth` and `/etc/security/faillock.conf` (deny=5, unlock_time=900). Full stack: `references/pam-authentication.md`.

### 6. AppArmor enforce

```bash
systemctl enable --now apparmor
aa-status                                   # check active profiles
# Put any complain-mode profiles into enforce
for p in /etc/apparmor.d/*; do
  aa-enforce "$p" 2>/dev/null
done
```

Custom profiles for your own apps: see `references/selinux-apparmor.md`.

### 7. auditd rules

```bash
systemctl enable --now auditd
# Load CIS-style rules (edit to /etc/audit/rules.d/audit.rules)
augenrules --load
auditctl -l                                 # verify loaded
```

Reference ruleset covering identity changes, sudo, SSH config, kernel module loads, and mount operations: `references/auditd-logging.md`.

### 8. Kernel hardening

Write `/etc/sysctl.d/99-hardening.conf` with the baseline from `references/kernel-sysctl-hardening.md`, then:

```bash
sysctl --system
```

Key values:

```ini
kernel.randomize_va_space = 2
kernel.kptr_restrict = 2
kernel.dmesg_restrict = 1
kernel.yama.ptrace_scope = 2
kernel.unprivileged_bpf_disabled = 1
net.core.bpf_jit_harden = 2
fs.suid_dumpable = 0
fs.protected_hardlinks = 1
fs.protected_symlinks = 1
```

### 9. File integrity baseline

```bash
aideinit                                    # build baseline DB
mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db
# Schedule daily checks via systemd timer
```

Ship output off-host. Detail: `references/file-integrity.md`.

### 10. Rootkit baseline

```bash
rkhunter --propupd                          # build baseline
rkhunter --update                           # update signature DB
chkrootkit                                  # initial clean scan
```

Schedule daily + alert on INFECTED. Detail: `references/rootkit-detection.md`.

### 11. Patch automation

```bash
dpkg-reconfigure -plow unattended-upgrades
systemctl status unattended-upgrades
```

Configure security-only updates + auto-reboot at 02:00. Detail: `references/patch-management.md`.

### 12. Verify with Lynis

```bash
lynis audit system --profile /etc/lynis/default.prf
# Target: hardening index >= 80 at Level 1
```

## Compliance Mapping (Brief)

| Control family | CIS | ISO 27001 | PCI-DSS | Primary reference |
|----------------|-----|-----------|---------|--------------------|
| Access control | 5.x | A.9 | 7, 8 | `users-groups-sudo.md`, `pam-authentication.md` |
| Cryptography | - | A.10 | 3, 4 | `boot-security.md`, `network-security/tls-pki.md` |
| Operations security | 4.x | A.12 | 6 | `patch-management.md`, `file-integrity.md` |
| Communications security | 3.x | A.13 | 1 | `network-security/*` |
| Logging / monitoring | 4.x | A.12.4 | 10 | `auditd-logging.md`, `rootkit-detection.md` |
| System acquisition / dev | - | A.14 | 6 | `cicd-devsecops` |

Full CIS Debian 12 checklist: `references/cis-benchmark-checklist.md`.

## Audit Runbook

Weekly or quarterly, run this sequence on each production host:

1. `lynis audit system` — quick hardening score
2. `debsecan --only-fixed` — list unpatched CVEs
3. `rkhunter --check --skip-keypress` — rootkit scan
4. `aide --check` — file integrity delta
5. `aureport --summary` — audit log summary
6. `fail2ban-client status` — see active jails and bans
7. `last -a | head -20` — recent logins
8. `sudo grep -i 'COMMAND' /var/log/auth.log | tail -50` — recent privileged commands
9. `systemctl --failed` — failed services
10. `apt list --upgradable` — pending updates

Log findings and track remediation in a ticket.

## Anti-Patterns

**Do not:**

- Rely on DAC (`rwx`) alone — add AppArmor for any internet-facing daemon.
- Disable AppArmor "to make the app work" — write a profile instead.
- Run services as root when a system user and `DynamicUser=true` in systemd would suffice.
- Skip patching because "uptime is important" — schedule maintenance windows with live kernel patching where needed.
- Edit `/etc/sudoers` directly without `visudo` — syntax errors lock you out.
- Use `NOPASSWD: ALL` in sudoers — the whole point of sudo is the audit trail.
- Give every admin the same SSH key — per-person keys enable revocation and accountability.
- Treat AIDE / rkhunter as checkboxes — they must alert off-host, or they are paperweights.
- Disable auditd because "logs fill the disk" — rotate, ship, don't disable.
- Leave AppArmor profiles in `complain` mode forever — tune and enforce.
- Leave `umask 0022` in `/etc/login.defs` — use `027` so others can't read new files by default.
- Forget `/boot` — it often ends up 755 and world-readable.
- Leave `kernel.dmesg_restrict=0` — kernel messages leak addresses useful for exploitation.
- Skip the post-upgrade AIDE re-baseline — every legit update generates false positives until rebased.
- Run Lynis once, fix nothing, forget. Track hardening score as a metric over time.

## References Index

**Domain references:**

- `references/users-groups-sudo.md` — account model, sudo hardening, password aging
- `references/file-permissions-acls.md` — DAC, setuid audit, ACLs, mount options
- `references/pam-authentication.md` — PAM stack, pwquality, faillock, MFA
- `references/selinux-apparmor.md` — MAC, AppArmor profiles, systemd sandboxing
- `references/auditd-logging.md` — rules, ausearch, off-host shipping
- `references/kernel-sysctl-hardening.md` — sysctls, modprobe blacklist, lockdown
- `references/file-integrity.md` — AIDE baseline, alerting, re-baselining
- `references/rootkit-detection.md` — rkhunter, chkrootkit, incident runbook
- `references/patch-management.md` — unattended-upgrades, debsecan, CVE SLAs
- `references/boot-security.md` — GRUB password, Secure Boot, LUKS, TPM

**Compliance:**

- `references/cis-benchmark-checklist.md` — ~60-item CIS-aligned audit checklist

**Related skills:**

- `network-security` — firewall, WAF, TLS, VPN, IDS (network layer)
- `cicd-devsecops` — secrets, dependency scanning, pipeline hardening
- `cicd-jenkins-debian` — Debian server provisioning for CI/CD
- `database-reliability` — DB-specific hardening, backup, failover
- `web-app-security-audit` — application-layer vulnerabilities