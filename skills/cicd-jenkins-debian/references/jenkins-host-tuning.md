# Jenkins Host Hardening and Performance Tuning (Debian/Ubuntu)

Jenkins-specific overlay on top of the generic `linux-systems-hardening.md`. The controller and a build agent have different load shapes — controller carries long-lived TCP connections to UI clients and SCMs; agent does short-lived heavy I/O and many parallel artefact pulls. Keep two distinct profiles.

Cross-reference: `linux-security-hardening` (sibling skill) for the OS-wide baseline. This file is the Jenkins-on-Debian/Ubuntu specific angle.

---

## 1. CIS Benchmark Baseline

Pick the CIS Benchmark version that matches the deployed OS, treat it as the baseline, and document deviations explicitly. Do not paraphrase clause numbers from secondary sources — read the benchmark PDF.

CIS Benchmarks page: https://www.cisecurity.org/cis-benchmarks (download routes through https://learn.cisecurity.org/benchmarks).

Versions confirmed available (fetched 2026-05-01):

- Debian Linux — Debian 13 (1.0.0), Debian 12 (1.1.0), Debian 11 (2.0.0), Debian 10 (2.0.0).
- Ubuntu Linux — Ubuntu 24.04 LTS (1.0.0), Ubuntu 22.04 LTS (3.0.0), Ubuntu 20.04 LTS (3.0.0).

Pin the exact version in your hardening deviation register (one row per CIS clause you intentionally accept differently).

Vendor references:

- Debian Hardening wiki: https://wiki.debian.org/Hardening
- Ubuntu Security: https://ubuntu.com/security

---

## 2. sysctl Profiles — Controller vs Agent

Common to both (in addition to the generic baseline in `linux-systems-hardening.md`):

```conf
# /etc/sysctl.d/70-jenkins-common.conf
vm.swappiness = 10
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2
net.ipv4.tcp_syncookies = 1
net.ipv4.conf.all.rp_filter = 1
```

### Controller profile

Controller is mostly long-lived TCP connections to UI clients, SCM webhooks, and agents. Bound connection counts to the configured Jenkins thread pool.

```conf
# /etc/sysctl.d/71-jenkins-controller.conf
net.core.somaxconn = 4096
net.ipv4.tcp_max_syn_backlog = 4096
net.ipv4.tcp_keepalive_time = 300
net.ipv4.tcp_keepalive_intvl = 30
net.ipv4.tcp_keepalive_probes = 5
fs.file-max = 524288
```

Match `nofile` ulimits in the systemd unit (see §4).

### Agent profile

Agents do heavy parallel I/O — Maven/npm dep pulls, Docker layer pulls, artefact uploads.

```conf
# /etc/sysctl.d/71-jenkins-agent.conf
net.core.somaxconn = 16384
net.ipv4.tcp_max_syn_backlog = 16384
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.netfilter.nf_conntrack_max = 524288
fs.file-max = 1048576
```

Apply: `sudo sysctl --system`. Verify: `sysctl net.core.somaxconn` returns the new value. Pattern, not values — exact numbers come from the CIS benchmark and observed traffic.

---

## 3. cgroups v2 Resource Isolation

Debian 12+ and Ubuntu 22.04+ ship cgroups v2 unified hierarchy. Confirm with `mount | grep cgroup2`.

A rogue compiler fork can starve sibling builds. Bound CPU and memory per agent service or per build slice.

```ini
# /etc/systemd/system/jenkins-agent.service.d/limits.conf
[Service]
CPUQuota=400%
MemoryMax=8G
MemoryHigh=6G
IOWeight=200
TasksMax=4096
```

For container build workers, rely on the runtime's cgroup mapping. Verify either way:

```bash
systemctl show jenkins-agent.service --property=CPUQuotaPerSecUSec,MemoryMax
systemd-cgls /system.slice/jenkins-agent.service
cat /sys/fs/cgroup/system.slice/jenkins-agent.service/cpu.max
cat /sys/fs/cgroup/system.slice/jenkins-agent.service/memory.max
```

Pair every limit change with a load test that confirms enforcement (e.g., a `stress-ng` job that should be throttled).

---

## 4. systemd Unit Hardening and ulimits

Drop-in for the controller unit `/etc/systemd/system/jenkins.service.d/hardening.conf`:

```ini
[Service]
# File handles for many parallel SCM/agent connections
LimitNOFILE=65536
LimitNPROC=8192

# Sandbox the controller
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
PrivateDevices=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictSUIDSGID=true
RestrictRealtime=true
LockPersonality=true
SystemCallArchitectures=native

# Writable paths Jenkins legitimately needs
ReadWritePaths=/var/lib/jenkins /var/log/jenkins /var/cache/jenkins
```

Do not add `ProtectSystem=strict` without `ReadWritePaths` — Jenkins will fail to write `JENKINS_HOME`. After editing run `systemctl daemon-reload && systemctl restart jenkins`.

Agent units get the same shape with `ReadWritePaths=/home/jenkins`.

---

## 5. AppArmor / seccomp

Debian and Ubuntu ship AppArmor enabled by default. For Jenkins:

- Confirm enforcement: `aa-status` lists profiles.
- Container build agents: Docker applies its default seccomp + AppArmor profile (`docker-default`). Do not run `--privileged` for normal builds; if a build legitimately needs raw devices, isolate it on a dedicated agent label.
- Custom profile: when running native build tooling on the host (not in Docker), write an AppArmor profile that denies write outside `/home/jenkins`, `/tmp`, and `/var/lib/jenkins`. Test in `complain` mode (`aa-complain`) before promoting to `enforce`.

---

## 6. auditd — Evidence Trail

auditd produces the kernel-level audit trail used as ISO 27001 / PCI-DSS evidence. Cross-ref `cicd-devsecops` evidence sections.

`/etc/audit/rules.d/50-jenkins.rules`:

```
# Buffer
-b 8192
-f 1

# Identity files
-w /etc/passwd      -p wa -k identity
-w /etc/shadow      -p wa -k identity
-w /etc/sudoers     -p wa -k identity
-w /etc/sudoers.d/  -p wa -k identity

# Jenkins config
-w /var/lib/jenkins/config.xml         -p wa -k jenkins-config
-w /var/lib/jenkins/credentials.xml    -p wa -k jenkins-secrets
-w /var/lib/jenkins/secrets/           -p wa -k jenkins-secrets
-w /etc/default/jenkins                -p wa -k jenkins-config

# Vault / agent binaries (if installed)
-w /usr/bin/vault   -p x  -k vault-exec

# Privilege escalation
-a always,exit -F arch=b64 -S execve -F euid=0 -k root-exec
```

Log rotation in `/etc/audit/auditd.conf`:

```
max_log_file = 50
num_logs = 10
max_log_file_action = ROTATE
space_left = 200
space_left_action = SYSLOG
admin_space_left_action = SUSPEND
```

Forward to a SIEM/log aggregator. Local logs alone are insufficient for evidence integrity.

`-f 2` (panic on audit failure) only for the strictest evidence regimes — the operator must understand that an audit subsystem failure will halt the host.

Verify: `auditctl -l` lists every rule; trigger a test event (`touch /etc/sudoers; ausearch -k identity`) and confirm a record appears.

---

## 7. journald

Bound journald so a runaway agent log cannot fill the disk:

```ini
# /etc/systemd/journald.conf.d/jenkins.conf
[Journal]
Storage=persistent
SystemMaxUse=2G
SystemKeepFree=1G
RuntimeMaxUse=200M
MaxRetentionSec=2week
ForwardToSyslog=no
```

Apply: `systemctl restart systemd-journald`. Forward Jenkins build logs to the SIEM via the agent log shipper, not journald, so build logs and audit logs stay on independent retention schedules.

---

## 8. fail2ban

Even behind Nginx, expose only TLS — and run fail2ban for SSH and Nginx auth failures.

`/etc/fail2ban/jail.d/jenkins.conf`:

```ini
[sshd]
enabled  = true
maxretry = 4
findtime = 10m
bantime  = 1h

[nginx-jenkins-auth]
enabled  = true
filter   = nginx-jenkins-auth
logpath  = /var/log/nginx/jenkins-access.log
maxretry = 6
findtime = 5m
bantime  = 30m
```

Define the filter to match `401`/`403` against the Jenkins login URL. Do not ban the agent subnet — whitelist it under `ignoreip`.

---

## 9. unattended-upgrades

Security patches apply automatically; everything else stays on the change-window schedule.

```bash
sudo apt install -y unattended-upgrades apt-listchanges
sudo dpkg-reconfigure -plow unattended-upgrades
```

`/etc/apt/apt.conf.d/52unattended-upgrades-jenkins`:

```
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};
Unattended-Upgrade::Package-Blacklist {
    "jenkins";
    "openjdk-17-jdk";
};
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Mail "ops@yourcompany.example";
```

Keep `jenkins` itself on the manual change window — surprise restarts mid-build are unwelcome.

---

## 10. Verification Harness

Every hardening change pairs with a check. Run as a CI job that asserts runtime values and fails on drift.

| Change | Check |
|---|---|
| sysctl key | `sysctl <key>` matches expected; file persists in `/etc/sysctl.d/` |
| auditd rule | `auditctl -l` shows the rule; a test event produces an audit record |
| cgroup limit | `systemctl show <unit>` shows the property; load test confirms enforcement |
| TCP buffers | `ss -tmi` shows the tuned socket buffer values |
| systemd hardening | `systemd-analyze security <unit>` score within target band |
| AppArmor | `aa-status` shows profile in `enforce` |
| fail2ban | `fail2ban-client status <jail>` reports active |
| Unattended-upgrades | `unattended-upgrade --dry-run --debug` exits clean |
| CIS deviation | Entry exists in the hardening deviation register |

Candidate tooling for the harness: `lynis audit system`, OpenSCAP SSG (`oscap`), and a custom shell asserter that diffs `sysctl -a` against an expected baseline file. Pick one and pin it; do not run all three.

---

## 11. Hardening Deviation Register

Maintain `docs/ci/hardening-deviations.md` per environment with rows:

| CIS clause | Deployed value | Expected value | Reason | Owner | Review date |
|---|---|---|---|---|---|

Every deviation has a named owner and a review date. The verification harness reads this file and accepts listed deviations as expected; an undocumented deviation fails the build.
