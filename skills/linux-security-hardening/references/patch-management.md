# Patch Management (Debian 12 / Ubuntu 24.04)

Purpose: Define a reliable, automated patching workflow for self-managed Debian
and Ubuntu servers so security updates land quickly without human babysitting.

## Why patch automation matters

Unpatched known CVEs remain the number-one root cause of server breaches year
after year. Attackers weaponise public vulnerabilities within hours of
disclosure, long before most teams finish their manual change-control cycles.
In that race speed beats perfection: a server patched within 24 hours to an
imperfect state is far safer than one that is "properly scheduled" two weeks
out. Automation removes the human bottleneck and makes patching the default
rather than the exception.

## APT basics

```bash
# Refresh the package index (no changes to installed packages)
sudo apt update

# Install upgrades that do not require removing or adding packages
sudo apt upgrade -y

# Install upgrades, including ones that add/remove dependencies
sudo apt full-upgrade -y
```

- `apt upgrade` is safe for unattended use; it never removes packages.
- `apt full-upgrade` (same as `dist-upgrade`) can remove packages to resolve
  dependency conflicts. Use it deliberately; do not put it on a cron job
  without monitoring.
- Never run `do-release-upgrade` unattended; major version jumps need a
  maintenance window and a backup.
- Always run apt inside `screen` or `tmux` over SSH so a dropped connection
  cannot leave dpkg mid-transaction.

## unattended-upgrades: install and configure

```bash
sudo apt install -y unattended-upgrades apt-listchanges
sudo dpkg-reconfigure -plow unattended-upgrades
```

The `dpkg-reconfigure` step writes a minimal `/etc/apt/apt.conf.d/20auto-upgrades`
that enables periodic updates.

Edit `/etc/apt/apt.conf.d/50unattended-upgrades` and enable the security and
regular update origins, auto-fix interrupted dpkg state, and schedule an
automatic reboot at 02:00:

```conf
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}";
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
    "${distro_id}:${distro_codename}-updates";
};

Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-New-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "true";
Unattended-Upgrade::Automatic-Reboot-Time "02:00";
Unattended-Upgrade::Mail "ops@example.com";
Unattended-Upgrade::MailReport "on-change";
```

Set `/etc/apt/apt.conf.d/20auto-upgrades` to run the periodic jobs daily:

```conf
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
```

Dry-run before trusting the config:

```bash
sudo unattended-upgrade --dry-run -d
```

## Reboot coordination

Library updates (glibc, openssl, systemd) require a reboot or a targeted
service restart to take effect. Running kernels and services continue to use
the old binaries from memory until they restart.

```bash
# Interactive tool that detects services still using deleted libraries
sudo apt install -y needrestart
sudo needrestart
```

Configure needrestart to run automatically on package install by ensuring
`/etc/needrestart/needrestart.conf` has `$nrconf{restart} = 'a';` for fully
automatic service restart.

Check whether a reboot is pending:

```bash
# File exists when a package (usually kernel) requires a reboot
[ -f /var/run/reboot-required ] && cat /var/run/reboot-required
```

On Debian, combine `needrestart` with unattended-upgrades so that after every
apt run, restartable services are restarted and the `reboot-required` flag
triggers the scheduled 02:00 reboot.

## Live kernel patching

Live kernel patching applies critical kernel CVE fixes to a running kernel
without rebooting.

- Ubuntu (LTS): Canonical Livepatch is the supported path.

  ```bash
  sudo snap install canonical-livepatch
  sudo canonical-livepatch enable <TOKEN>
  sudo canonical-livepatch status
  ```

  Free tier covers up to 5 machines on Ubuntu Pro.

- Debian: no official live patching. `kpatch` exists but requires building
  patches yourself; in practice most Debian shops accept a short scheduled
  reboot window instead.

Live patching reduces unplanned reboots for urgent CVEs but it is not a
substitute for full reboots during regular maintenance windows — some fixes
(initramfs, systemd, glibc) still need a real reboot.

## Pinning and holding packages

Hold a package at its current version (for example, a database server in the
middle of a change freeze):

```bash
sudo apt-mark hold mysql-server
sudo apt-mark showhold
sudo apt-mark unhold mysql-server
```

Risks:

- Held packages stop receiving security fixes silently.
- The hold must be documented in the runbook and have an expiry date.
- Track held packages in configuration management (Ansible) so they are
  visible across the fleet.

## Security-only updates

If the appetite for automatic change is low, restrict unattended-upgrades to
the security pocket only:

```conf
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};
```

This keeps security CVEs patched automatically while leaving bugfix updates
for manual review.

## Monitoring for missing patches

```bash
# List packages with newer versions available
apt list --upgradable

# CVE scanner for Debian packages
sudo apt install -y debsecan
sudo debsecan --suite bookworm --only-fixed --format report

# Ubuntu equivalent (shows support status, ESM coverage)
ubuntu-security-status --thorough

# Debian support status
debian-security-support
```

Pipe the output into your monitoring stack (Prometheus textfile collector,
Wazuh, or a nightly email) so missing patches become alerts, not surprises.

## CI/CD for patching

For anything beyond a handful of servers use Ansible (or your config manager)
to centralise the workflow — see the `cicd-devsecops` skill for secrets and
gating, and `cicd-jenkins-debian` for scheduled job patterns. A typical
pipeline:

1. Jenkins nightly job runs an Ansible playbook against the fleet.
2. Playbook runs `apt update && apt upgrade -y` in batches of 10% of hosts.
3. Each batch runs `needrestart -r a` and reboots if `reboot-required` exists.
4. Health check (HTTP 200 on /health) before moving to the next batch.
5. Slack/email report on success, page on failure.

## Compliance — patch SLAs

Typical SOC 2 / ISO 27001 / PCI-DSS expectations:

| Severity | SLA from disclosure |
|----------|---------------------|
| Critical (CVSS 9.0+) | 48 hours |
| High (CVSS 7.0–8.9)  | 7 days   |
| Medium               | 30 days  |
| Low                  | 90 days  |

Record the SLA in your Information Security Policy and measure against it
monthly. Auditors will ask for evidence.

## Anti-patterns

- Running `apt upgrade` over SSH without `screen` or `tmux` — a dropped
  connection during dpkg leaves the system in an inconsistent state.
- Skipping `needrestart` and assuming libraries have been reloaded.
- Bragging about uptime and never rebooting — kernel CVEs accumulate.
- Ignoring `W:` warnings from apt about missing signatures or held packages.
- Setting `Unattended-Upgrade::Automatic-Reboot "true"` without a maintenance
  window, and then blaming apt when the database restarts at peak hours.
- Using `apt-mark hold` without an expiry date or owner.
- Enabling unattended-upgrades but never reading the email reports.

## Cross-references

- `network-security/references/firewall-architecture.md` — limit who can
  reach the apt proxy and ssh management plane.
- `cicd-devsecops/SKILL.md` — centralised patching pipelines with Ansible.
- `cicd-jenkins-debian/SKILL.md` — Jenkins scheduled job patterns.
- `linux-security-hardening/references/boot-security.md` — reboot behaviour
  and secure boot verification.
- `linux-security-hardening/references/cis-benchmark-checklist.md` — audit
  controls that expect a working patch process.
