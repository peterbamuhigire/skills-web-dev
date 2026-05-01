# Mandatory Access Control: AppArmor, SELinux and Systemd Hardening

Reference for adding a MAC layer on top of Debian 12 / Ubuntu 24.04. Covers
AppArmor (the pragmatic default), SELinux (brief), Linux capabilities, and
systemd unit hardening.

## 1. MAC vs DAC

Discretionary Access Control (DAC — the `rwx` model) trusts the file owner
to decide who may read or write. That is fine until a privileged process is
exploited: a compromised `nginx` worker running as `www-data` can read every
file `www-data` owns, plus every world-readable file — which usually means
far more than the web root.

Mandatory Access Control (MAC) sits on top of DAC. Even if DAC allows an
operation, the kernel asks the MAC layer whether this specific process is
permitted this specific access. A properly confined nginx cannot read
`/etc/shadow` even if it somehow ended up running as root.

MAC is not a replacement for file permissions, firewalls, or patching. It is
a containment wall: when something does get exploited, MAC limits the blast
radius.

## 2. AppArmor vs SELinux

| Dimension       | AppArmor                                     | SELinux                                    |
|-----------------|----------------------------------------------|--------------------------------------------|
| Default on      | Debian, Ubuntu, SUSE                          | RHEL, Fedora, Rocky, Alma, Oracle          |
| Policy style    | Path-based (`/usr/bin/nginx`)                 | Label/type-based (`httpd_t`)               |
| Learning curve  | Hours                                         | Days                                       |
| Granularity     | Good for per-binary confinement               | Finer, type transitions, MCS/MLS           |
| Tooling         | `aa-*`, text profiles                          | `semanage`, `audit2allow`, contexts        |
| SaaS fit        | Excellent on Debian/Ubuntu                     | Excellent on RHEL family                   |

Rule: **run one, not both**. On Debian 12 / Ubuntu 24.04, AppArmor is the
default, integrated with the kernel build, and has profiles shipped for most
packages. Choose AppArmor unless you have a policy or compliance reason to
run SELinux on Debian (rare and painful).

## 3. AppArmor deep dive

### 3.1 Install and enable

```bash
sudo apt install apparmor apparmor-utils apparmor-profiles apparmor-profiles-extra
sudo systemctl enable --now apparmor
sudo aa-status
```

`aa-status` output tells you:

- How many profiles are loaded.
- How many are in **enforce** mode (kernel blocks denied actions).
- How many are in **complain** mode (kernel logs denials but allows them).
- How many running processes are confined by a profile.

### 3.2 Profile modes

| Mode        | Behaviour                                           | Use when                       |
|-------------|-----------------------------------------------------|--------------------------------|
| `enforce`   | Block and log anything outside the profile.        | Production.                    |
| `complain`  | Log but do not block. Feeds `aa-logprof`.          | Profiling and tuning.          |
| `disabled`  | Profile loaded but does nothing.                   | Never in production.           |
| `unconfined`| No profile attached to the binary.                  | Before writing a profile.      |

Switch modes with `aa-utils`:

```bash
sudo aa-enforce  /etc/apparmor.d/usr.sbin.nginx
sudo aa-complain /etc/apparmor.d/usr.sbin.nginx
sudo aa-disable  /etc/apparmor.d/usr.sbin.nginx
```

### 3.3 Profile files

Profiles live in `/etc/apparmor.d/`. Filenames encode the path of the
binary they protect, replacing `/` with `.`:

```text
/etc/apparmor.d/usr.sbin.nginx
/etc/apparmor.d/usr.sbin.mysqld
/etc/apparmor.d/usr.sbin.sshd
/etc/apparmor.d/abstractions/   # reusable rule fragments
/etc/apparmor.d/tunables/       # #include'd variables like @{HOME}
```

## 4. Reading an AppArmor profile

A trimmed example profile for `nginx`:

```text
#include <tunables/global>

/usr/sbin/nginx {
  #include <abstractions/base>
  #include <abstractions/nameservice>
  #include <abstractions/openssl>

  capability dac_override,
  capability net_bind_service,
  capability setgid,
  capability setuid,

  network inet  stream,
  network inet6 stream,

  /etc/nginx/**            r,
  /etc/ssl/certs/**        r,
  /etc/ssl/private/**      r,
  /var/log/nginx/*.log     w,
  /var/cache/nginx/**      rw,
  /run/nginx.pid           rw,
  /usr/share/nginx/**      r,
  /srv/www/**              r,

  # deny anything writable into the web root
  deny /srv/www/** w,

  # subprocess
  /usr/sbin/nginx          rmix,
  /bin/dash                rmix,
}
```

Rule syntax reminders:

- `r` read, `w` write, `a` append, `x` execute, `m` mmap-executable,
  `k` file locking, `l` create hard link, `i` inherit profile on exec,
  `u` run unconfined on exec, `ix` child inherits, `Px` child gets its
  own named profile.
- `deny` rules override allow rules and are logged.
- `capability` lines whitelist Linux capabilities the process may use.
- `network` lines restrict socket families.
- Globs: `*` matches within a segment, `**` matches recursively.

## 5. Writing a custom profile

Workflow: run the app in **complain** mode, exercise every code path, then
convert logs into allow rules.

```bash
# Step 1: generate a starting profile
sudo aa-genprof /usr/local/bin/myapp
# In another terminal, exercise the app (start it, hit every feature).
# Back in aa-genprof, press 'S' to scan logs; answer A/D/G/I for each rule.

# Step 2: iterate
sudo aa-logprof                 # pull in new denials since last pass

# Step 3: move to enforcement
sudo aa-enforce /etc/apparmor.d/usr.local.bin.myapp
sudo systemctl restart myapp
sudo aa-status | grep myapp
```

Keep the profile under version control and deploy it through configuration
management, not by hand.

## 6. Debugging denials

```bash
# Live kernel messages
sudo journalctl -k -f | grep -i apparmor

# Just audit messages
sudo dmesg | grep -i apparmor
sudo grep apparmor /var/log/kern.log

# Desktop notification of denies (dev workstations)
sudo aa-notify -s 1 -v

# Generate rules from recent denials
sudo aa-logprof
```

A typical denial line:

```text
apparmor="DENIED" operation="open" profile="/usr/sbin/nginx"
  name="/home/attacker/.ssh/id_rsa" pid=1234 comm="nginx"
  requested_mask="r" denied_mask="r" fsuid=33 ouid=1000
```

It shows the profile, the operation, the target path, and the requested
permission mask. This is exactly what `aa-logprof` turns into rules.

## 7. Per-application sandboxing examples

### 7.1 Web scraper confined to a single target

```text
/usr/local/bin/scraper {
  #include <abstractions/base>
  #include <abstractions/nameservice>
  #include <abstractions/ssl_certs>

  # Read-only code and config
  /usr/local/bin/scraper      r,
  /etc/scraper/**             r,

  # Writable scratch and output
  owner /var/lib/scraper/**   rw,
  owner /tmp/scraper-*        rw,

  # Network: DNS and HTTPS only
  network inet  stream,
  network inet6 stream,
  deny  network inet  dgram,
  deny  network inet6 dgram,

  deny /etc/shadow r,
  deny /root/** rwx,
}
```

### 7.2 Hardened PHP-FPM pool

```text
/usr/sbin/php-fpm8.2 {
  #include <abstractions/base>
  #include <abstractions/nameservice>
  #include <abstractions/php>

  /usr/sbin/php-fpm8.2     r,
  /etc/php/8.2/**          r,
  /etc/apache2/**          r,
  /var/lib/php/sessions/   rw,
  /var/lib/php/sessions/** rwk,

  /srv/www/*/code/**       r,     # application code is read-only
  owner /srv/www/*/storage/** rw, # only storage dir is writable

  deny /srv/www/*/code/**  w,
  deny /etc/shadow         r,
  deny /root/**            rwx,

  capability setgid,
  capability setuid,
}
```

## 8. SELinux overview (brief)

Concepts you will see if you open an SELinux host:

- **Context** — every process and every file has one, formatted as
  `user:role:type:level` e.g. `system_u:system_r:httpd_t:s0`.
- **Type enforcement** — the `httpd_t` process type may only access files
  whose type policy lists (like `httpd_sys_content_t`).
- **Modes** — `Enforcing`, `Permissive`, `Disabled`. Never ship `Disabled`.

```bash
getenforce
sudo setenforce 1
sudo vi /etc/selinux/config           # SELINUX=enforcing
ls -Z /var/www/html                    # show contexts
sudo semanage fcontext -a -t httpd_sys_content_t "/srv/www(/.*)?"
sudo restorecon -Rv /srv/www
sudo ausearch -m avc -ts recent       # recent denials
sudo audit2allow -a -M my-local       # turn denials into a module
sudo semodule -i my-local.pp
```

SELinux on Debian is technically possible (`selinux-basics`, `selinux-policy-default`)
but unpolished: most package maintainer scripts target AppArmor, you end up
running in permissive forever, and you lose the main benefit. Stay with
AppArmor unless a compliance regime specifically requires SELinux.

## 9. Container sandboxing intersection

MAC composes with other sandboxing layers. On Debian hosts running Docker:

- Docker loads a default AppArmor profile (`docker-default`) onto every
  container unless you pass `--security-opt apparmor=unconfined`.
- You can attach a custom profile per container:
  `--security-opt apparmor=my-nginx-profile`.
- `seccomp` filters (syscall allow/deny lists) run alongside AppArmor.
  Docker's default seccomp profile blocks about 40 dangerous syscalls.
- `systemd-nspawn` containers honour both AppArmor profiles and systemd
  unit hardening directives.

Rule: never run `--privileged`, never `--cap-add=ALL`, and never disable
AppArmor on production containers "just to make it work".

## 10. Linux capabilities

`root` historically had 100 % of kernel privilege. Capabilities slice that
privilege into ~40 named units. A binary or service can be granted exactly
the capabilities it needs without ever becoming real root.

Common capabilities:

| Capability               | Allows                                           |
|--------------------------|--------------------------------------------------|
| `CAP_NET_BIND_SERVICE`   | Bind to ports below 1024.                        |
| `CAP_NET_ADMIN`          | Interface/route changes, sockets with `SO_BROADCAST`. |
| `CAP_NET_RAW`            | Raw sockets (ICMP, custom protocols).            |
| `CAP_SYS_ADMIN`          | Catch-all "small root". Avoid; it is almost root.|
| `CAP_DAC_OVERRIDE`       | Bypass file read/write permission checks.        |
| `CAP_CHOWN`              | Change file ownership.                           |
| `CAP_SYS_PTRACE`         | Attach to other processes.                       |

```bash
# Inspect
getcap /usr/bin/ping
# /usr/bin/ping cap_net_raw=ep

# Add a capability (modern alternative to setuid)
sudo setcap cap_net_bind_service=+ep /usr/local/bin/myapp

# Remove
sudo setcap -r /usr/local/bin/myapp
```

Prefer capabilities over setuid for new software. For services started by
systemd, prefer `AmbientCapabilities=` so you do not need to patch the
binary at all.

## 11. Systemd unit hardening

systemd ships rich sandboxing directives. You can apply them to any unit
without recompiling the service. Use a drop-in file rather than editing the
shipped unit so package upgrades do not overwrite you.

```bash
sudo systemctl edit nginx.service
# creates /etc/systemd/system/nginx.service.d/override.conf
```

Key directives:

| Directive                  | Effect                                                      |
|----------------------------|-------------------------------------------------------------|
| `NoNewPrivileges=true`      | No setuid/setgid escalation below this process.             |
| `ProtectSystem=strict`      | `/`, `/usr`, `/boot`, `/etc` are read-only.                 |
| `ProtectHome=true`          | `/home`, `/root`, `/run/user` invisible.                    |
| `PrivateTmp=true`           | Per-service `/tmp` and `/var/tmp` namespaces.               |
| `PrivateDevices=true`       | Only `/dev/null`, `/dev/zero`, `/dev/random` etc.           |
| `ProtectKernelTunables=true`| `/proc/sys`, `/sys` read-only.                              |
| `ProtectKernelModules=true` | Cannot load/unload modules.                                 |
| `ProtectKernelLogs=true`    | No `dmesg`.                                                 |
| `ProtectControlGroups=true` | `/sys/fs/cgroup` read-only.                                 |
| `LockPersonality=true`      | Cannot change execution domain.                             |
| `MemoryDenyWriteExecute=true` | No W+X mappings (breaks some JIT).                        |
| `RestrictRealtime=true`     | No realtime scheduling.                                     |
| `RestrictNamespaces=true`   | Cannot create new namespaces (blocks container escape).    |
| `RestrictSUIDSGID=true`     | Cannot create setuid/setgid files.                          |
| `CapabilityBoundingSet=`    | Whitelist only the capabilities needed.                     |
| `AmbientCapabilities=`      | Pass named capabilities into the process at start.          |
| `SystemCallFilter=`         | Seccomp syscall allow list (e.g. `@system-service`).        |
| `SystemCallArchitectures=native` | Block x86 syscalls on an amd64 host.                  |
| `ReadOnlyPaths=` / `ReadWritePaths=` | Explicit path ACL overriding ProtectSystem.        |
| `PrivateNetwork=true`       | No network at all (nice for backup tools).                 |
| `IPAddressAllow=` / `IPAddressDeny=` | Per-service egress firewall.                      |

## 12. Example: hardening nginx

`/etc/systemd/system/nginx.service.d/hardening.conf`:

```ini
[Service]
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
PrivateDevices=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectKernelLogs=true
ProtectControlGroups=true
LockPersonality=true
MemoryDenyWriteExecute=true
RestrictRealtime=true
RestrictNamespaces=true
RestrictSUIDSGID=true
RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX
SystemCallArchitectures=native
SystemCallFilter=@system-service
SystemCallFilter=~@privileged @resources

CapabilityBoundingSet=CAP_NET_BIND_SERVICE CAP_CHOWN CAP_SETUID CAP_SETGID
AmbientCapabilities=CAP_NET_BIND_SERVICE

ReadWritePaths=/var/log/nginx /var/lib/nginx /var/cache/nginx /run
```

Apply and verify:

```bash
sudo systemctl daemon-reload
sudo systemctl restart nginx
sudo systemctl status nginx
```

## 13. Verify hardening score

systemd ships a scorer that rates a unit out of 10:

```bash
sudo systemd-analyze security nginx.service
# shows every directive and colours missing ones
sudo systemd-analyze security --no-pager | sort -k2 -n | tail
```

Anything scoring `UNSAFE` or `EXPOSED` is worth reviewing. A well-hardened
production service should land in `OK` or `HARDENED`.

## 14. Anti-patterns

- **`sudo aa-disable` to "make it work".** You just turned off the safety
  net. Switch to complain mode and write rules instead.
- **Running complain mode forever.** Complain mode is a development tool.
  Enforce, or remove the profile and admit it.
- **Disabling AppArmor on containers.** Turns a container from a strong
  jail into a loose chroot.
- **`SELINUX=permissive` permanently.** Same mistake, different label.
- **`CAP_SYS_ADMIN` as a shortcut.** Sysadmin is basically root with
  extra steps. Read the specific capability you need.
- **`PrivateNetwork=true` on a web server.** Seems obvious, but people
  copy-paste hardening blocks without thinking.
- **Not profiling custom apps.** Distro profiles cover `nginx`, `sshd`,
  `mysqld`. Your `myapp` has no profile by default — it runs unconfined.
  Write a profile, or at least a systemd hardening override.
- **Hand-editing vendor unit files.** Upgrades overwrite them. Always use
  `systemctl edit` and keep overrides under config management.
- **Mixing AppArmor and SELinux on the same host.** The kernel only loads
  one LSM as the primary. Pick one and stick to it.

## Cross-references

- `references/users-groups-sudo.md` — sudo logging, least privilege
- `references/file-permissions-acls.md` — DAC layer beneath MAC
- `references/pam-authentication.md` — login stack, lockout, MFA
- `references/kernel-hardening.md` — sysctl, `/proc/sys/kernel`, KASLR
- `network-security` skill — egress firewalling pairs with `IPAddressDeny=`
- `cicd-devsecops` skill — container hardening, Trivy image scans
- `mysql-administration` skill — `mysqld.service` hardening drop-in
