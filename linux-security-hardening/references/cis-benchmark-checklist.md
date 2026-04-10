# CIS Benchmark Checklist (Debian 12 / Ubuntu 24.04)

Purpose: A prescriptive, CIS-aligned hardening checklist for self-managed
Debian 12 and Ubuntu 24.04 servers, with verification commands and rationale.

## About CIS benchmarks

The Center for Internet Security publishes free consensus-based hardening
benchmarks for most Linux distributions. Each control is labelled Level 1
(safe defaults that do not break typical workloads) or Level 2 (stricter,
may impact functionality — only apply where security outweighs convenience).
Benchmarks are free to download in PDF form from cisecurity.org after a
short registration. This checklist distils the controls that matter most
for self-managed SaaS servers; it is not a complete substitute for the full
benchmark. Re-run it quarterly and after every major upgrade.

## How to read this file

Each item is `- [ ]` with a one-line rationale and a verification command.
Mark done when the verification command returns the expected state. Copy
this file into your runbook and track completion per-host.

## 1. Initial setup — filesystem and partitions (10 items)

Unused filesystem kernel modules widen the attack surface. Separate mount
points let you apply `nodev`, `nosuid`, `noexec` to high-risk directories.

- [ ] `cramfs` module disabled — rarely legitimate use
  `modprobe -n -v cramfs | grep -E 'install /bin/(true|false)'`
- [ ] `freevxfs` module disabled
  `modprobe -n -v freevxfs | grep -E 'install /bin/(true|false)'`
- [ ] `jffs2` module disabled
  `modprobe -n -v jffs2 | grep -E 'install /bin/(true|false)'`
- [ ] `hfs` module disabled
  `modprobe -n -v hfs | grep -E 'install /bin/(true|false)'`
- [ ] `hfsplus` module disabled
  `modprobe -n -v hfsplus | grep -E 'install /bin/(true|false)'`
- [ ] `squashfs` module disabled unless snap is required
  `modprobe -n -v squashfs`
- [ ] `udf` module disabled
  `modprobe -n -v udf | grep -E 'install /bin/(true|false)'`
- [ ] `/tmp` on a separate mount with `nodev,nosuid,noexec`
  `findmnt /tmp`
- [ ] `/var/tmp` with `nodev,nosuid,noexec` (bind-mount to `/tmp` is common)
  `findmnt /var/tmp`
- [ ] `/home` mounted with `nodev`
  `findmnt /home`
- [ ] `/dev/shm` with `nodev,nosuid,noexec`
  `findmnt /dev/shm`

Create these mount options by editing `/etc/fstab` and rebooting.

## 2. Services — disable what you do not need (8 items)

Every listening service is a potential CVE. Disable and mask unused ones
so they cannot be restarted accidentally by a dependency.

- [ ] `avahi-daemon` disabled (mDNS broadcasts)
  `systemctl is-enabled avahi-daemon 2>/dev/null || echo "ok: not installed"`
- [ ] `cups` disabled (printer sharing)
  `systemctl is-enabled cups 2>/dev/null`
- [ ] `rpcbind` disabled unless NFS client needed
  `systemctl is-enabled rpcbind 2>/dev/null`
- [ ] `nfs-server` disabled unless serving NFS
  `systemctl is-enabled nfs-server 2>/dev/null`
- [ ] `bind9` / DNS server disabled unless authoritative
  `systemctl is-enabled bind9 2>/dev/null`
- [ ] `vsftpd` / `proftpd` disabled (use sftp over ssh instead)
  `systemctl is-enabled vsftpd 2>/dev/null`
- [ ] `apache2` / `nginx` disabled on non-web hosts
  `systemctl is-enabled apache2 2>/dev/null`
- [ ] `nis` disabled
  `systemctl is-enabled nis 2>/dev/null`
- [ ] `postfix` bound to loopback only (or `exim4` same)
  `ss -tlnp | grep ':25 '`
- [ ] `slapd` disabled unless running LDAP
  `systemctl is-enabled slapd 2>/dev/null`

Disable with `sudo systemctl disable --now <unit>` and mask with
`sudo systemctl mask <unit>`.

## 3. Network configuration (10 items)

Kernel sysctls and firewall defaults must refuse unsolicited routing,
forged sources, and redirects. See `kernel-sysctl-hardening.md` for full
sysctl values.

- [ ] IP forwarding disabled unless host is a router
  `sysctl net.ipv4.ip_forward` → `0`
- [ ] Source routed packets dropped (v4 and v6)
  `sysctl net.ipv4.conf.all.accept_source_route` → `0`
- [ ] ICMP redirects not accepted
  `sysctl net.ipv4.conf.all.accept_redirects` → `0`
- [ ] Secure ICMP redirects not accepted
  `sysctl net.ipv4.conf.all.secure_redirects` → `0`
- [ ] Martian packets logged
  `sysctl net.ipv4.conf.all.log_martians` → `1`
- [ ] Reverse path filtering enabled (strict)
  `sysctl net.ipv4.conf.all.rp_filter` → `1`
- [ ] TCP SYN cookies enabled
  `sysctl net.ipv4.tcp_syncookies` → `1`
- [ ] IPv6 router advertisements ignored (on servers)
  `sysctl net.ipv6.conf.all.accept_ra` → `0`
- [ ] IPv6 disabled entirely if unused
  `sysctl net.ipv6.conf.all.disable_ipv6` → `1`
- [ ] Firewall installed with default-deny inbound
  `sudo nft list ruleset | grep -E 'policy drop|policy reject'`
- [ ] Default deny egress except for listed destinations (Level 2)
  Review `sudo nft list ruleset` output against approved egress list.

## 4. Logging and auditing (8 items)

You cannot investigate an incident you did not log, and you cannot trust
logs the attacker could edit. Ship logs off-host within minutes.

- [ ] `rsyslog` installed and enabled
  `systemctl is-enabled rsyslog`
- [ ] `auditd` installed and enabled
  `systemctl is-enabled auditd`
- [ ] Audit rules present for user/group changes, sudo, time, network
  `sudo auditctl -l | wc -l` → non-zero
- [ ] Audit logs not world-readable (mode 0640, owner `root:adm`)
  `stat -c '%a %U:%G' /var/log/audit/audit.log`
- [ ] `logrotate` configured for `/var/log/*`
  `ls /etc/logrotate.d/`
- [ ] Persistent journald storage enabled
  `grep -E '^Storage=persistent' /etc/systemd/journald.conf`
- [ ] Logs forwarded off-host (rsyslog TLS, or journald upload)
  `grep -r 'omrelp\|@@.*:6514' /etc/rsyslog.d/`
- [ ] Time sync running (`chrony` or `systemd-timesyncd`) so log
  timestamps align across hosts
  `timedatectl | grep 'System clock synchronized: yes'`

## 5. Access, authentication, authorisation (10 items)

Covers SSH, sudo, PAM, cron, and password policy. See the
`users-groups-sudo.md` reference for the full account standard.

- [ ] `cron` ownership root:root, mode 0600 on crontabs
  `stat -c '%a %U:%G' /etc/crontab`
- [ ] `at.deny` / `cron.deny` removed; `.allow` files exist and owned root
  `ls -l /etc/cron.allow /etc/at.allow`
- [ ] SSH `PermitRootLogin no`
  `sudo sshd -T | grep -i permitrootlogin`
- [ ] SSH `PasswordAuthentication no` (keys only)
  `sudo sshd -T | grep -i passwordauthentication`
- [ ] SSH `Protocol 2` only (the default; `Protocol 1` removed in OpenSSH 7)
- [ ] SSH `MaxAuthTries` ≤ 4
  `sudo sshd -T | grep -i maxauthtries`
- [ ] SSH idle timeout set (`ClientAliveInterval 300`, `ClientAliveCountMax 0`)
  `sudo sshd -T | grep -Ei 'clientaliveinterval|clientalivecountmax'`
- [ ] `sudo` installed, `log_input,log_output` in `/etc/sudoers`
  `sudo grep -E 'log_input|log_output' /etc/sudoers /etc/sudoers.d/*`
- [ ] `sudo` requires password (no `NOPASSWD` blanket rules)
  `sudo grep -n NOPASSWD /etc/sudoers /etc/sudoers.d/*`
- [ ] Password quality enforced — `libpam-pwquality` configured with
  `minlen=14 dcredit=-1 ucredit=-1 ocredit=-1 lcredit=-1`
  `grep -E 'minlen|credit' /etc/security/pwquality.conf`
- [ ] Password aging — `PASS_MAX_DAYS 365`, `PASS_MIN_DAYS 1`,
  `PASS_WARN_AGE 7`
  `grep -E '^PASS_' /etc/login.defs`
- [ ] Lockout on failed attempts via `pam_faillock` — deny=5, unlock=900
  `grep faillock /etc/pam.d/common-auth`
- [ ] Pre-login warning banner set in `/etc/issue.net` and referenced
  in sshd_config via `Banner /etc/issue.net`
  `sudo sshd -T | grep -i banner`

## 6. System maintenance (6 items)

These guard against stale files, privilege leaks and legacy trust files.

- [ ] `/etc/passwd` mode 0644, owner root:root
  `stat -c '%a %U:%G' /etc/passwd`
- [ ] `/etc/shadow` mode 0640, owner root:shadow
  `stat -c '%a %U:%G' /etc/shadow`
- [ ] `/etc/group` mode 0644, owner root:root
  `stat -c '%a %U:%G' /etc/group`
- [ ] `/etc/gshadow` mode 0640, owner root:shadow
  `stat -c '%a %U:%G' /etc/gshadow`
- [ ] No world-writable files in system directories
  `sudo find /usr /etc /bin /sbin /lib -xdev -type f -perm -0002`
- [ ] No files with no owner or no group
  `sudo find / -xdev -nouser -o -nogroup 2>/dev/null`
- [ ] No `.rhosts` or `.netrc` in any home directory
  `sudo find /home /root -name .rhosts -o -name .netrc`
- [ ] SUID/SGID inventory matches baseline
  `sudo find / -xdev \( -perm -4000 -o -perm -2000 \) -type f > /tmp/suid.now`
  Compare `/tmp/suid.now` against the approved baseline checked into git.

## 7. Mandatory Access Control — AppArmor (3 items)

Debian and Ubuntu ship AppArmor by default. SELinux is possible but far
more work on these distributions; stick with AppArmor unless you have a
strong reason otherwise.

- [ ] AppArmor installed and `aa-status` shows a loaded profile set
  `sudo aa-status | head -5`
- [ ] AppArmor enabled in kernel
  `grep -E 'apparmor=(1|Y)' /proc/cmdline || echo "default-on"`
- [ ] All profiles in enforce mode (no `complain` or unconfined processes
  you did not expect)
  `sudo aa-status | grep -E 'profiles are in complain mode|processes are unconfined'`

## 8. Patching and updates (crosscheck)

- [ ] `unattended-upgrades` running — see `patch-management.md`
  `systemctl is-active unattended-upgrades`
- [ ] `/var/run/reboot-required` absent or within scheduled window
  `[ -f /var/run/reboot-required ] && echo "reboot pending"`
- [ ] `debsecan --only-fixed` returns no critical findings
  `sudo debsecan --suite bookworm --only-fixed | grep -c CVE`

## 9. Boot security (crosscheck)

- [ ] GRUB password set — see `boot-security.md`
  `sudo grep -E 'password_pbkdf2|set superusers' /etc/grub.d/40_custom`
- [ ] Secure Boot state confirmed
  `mokutil --sb-state`
- [ ] Lockdown mode = integrity or confidentiality
  `cat /sys/kernel/security/lockdown`
- [ ] `/boot` permissions root:root 0700 (Level 2)
  `stat -c '%a %U:%G' /boot`

## Total: roughly 60 controls

This list is shorter than the full CIS benchmark on purpose; it covers
the highest-value controls that a small ops team can realistically keep
green on every host. Layer on the remaining benchmark items as your
maturity grows.

## How to use this checklist

- **First pass** — run each verification manually on one reference host
  and fix everything red. Capture the good state.
- **Automate** — convert the fixes into an Ansible role and apply it to
  every host. Commit the role to git alongside this checklist.
- **Scan on schedule** — run `lynis audit system` weekly from cron and
  ship the report. Target a Lynis hardening index ≥ 80 at Level 1,
  ≥ 85 at Level 2.
- **Wazuh / OSSEC rules** — enable the CIS SCA (Security Configuration
  Assessment) ruleset so failing controls become SIEM alerts.
- **Quarterly audit** — re-run the full checklist and open Jira tickets
  for any regression.

## Pre-built scanners

```bash
# Lynis — runs on the host, no licence required
sudo apt install -y lynis
sudo lynis audit system --profile /etc/lynis/default.prf

# OpenSCAP — use Debian or Ubuntu SCAP content
sudo apt install -y libopenscap8 ssg-debian ssg-debderived
sudo oscap xccdf eval \
    --profile xccdf_org.ssgproject.content_profile_cis_level1_server \
    --results /tmp/oscap-results.xml \
    --report  /tmp/oscap-report.html \
    /usr/share/xml/scap/ssg/content/ssg-debian12-ds.xml

# Debsecan — CVE coverage for installed Debian packages
sudo apt install -y debsecan
sudo debsecan --suite bookworm --only-fixed --format report
```

CIS-CAT Pro (the official CIS tool) offers stronger reporting but
requires a paid CIS SecureSuite membership.

## Reporting

Produce a concise report per host:

- Header — hostname, OS version, scan date, scanner versions.
- Summary table — pass / fail / warning counts per category.
- Findings — each fail with severity, CIS control ID, remediation command.
- Trend — pass rate over the last 4 quarters.
- Sign-off — reviewed by, approved by, next scan due.

Colour coding (e.g. red for fail, amber for warning, green for pass) is
appropriate in executive summaries but the raw data shipped to SIEM should
stay machine-readable (JSON or CSV).

## Cross-references

- `linux-security-hardening/references/patch-management.md` — update
  controls referenced in section 8.
- `linux-security-hardening/references/boot-security.md` — GRUB, Secure
  Boot, LUKS controls in section 9.
- `linux-security-hardening/references/users-groups-sudo.md` — account
  and sudo standards referenced in section 5.
- `linux-security-hardening/references/kernel-sysctl-hardening.md` —
  full sysctl values for section 3.
- `network-security/references/firewall-architecture.md` — design of the
  default-deny firewall in section 3.
- `cicd-devsecops/SKILL.md` — automating Lynis/OpenSCAP scans in CI.
