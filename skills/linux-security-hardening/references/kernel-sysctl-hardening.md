# Kernel and Sysctl Hardening on Debian/Ubuntu

Runtime kernel tunables, module blacklists, and boot-time flags for hardening
self-managed Debian 12 and Ubuntu 24.04 servers.

## sysctl basics

`sysctl` exposes runtime-tunable parameters under `/proc/sys/`. Settings made
with `sysctl -w key=value` are lost at reboot. Persistent settings live in
drop-in files under `/etc/sysctl.d/*.conf` (preferred) or the single file
`/etc/sysctl.conf` (legacy). Files are applied in lexical order, so a file
numbered `99-hardening.conf` wins over distro defaults.

Apply all drop-ins at once without a reboot:

```bash
sudo sysctl --system
```

Apply a single file:

```bash
sudo sysctl -p /etc/sysctl.d/99-hardening.conf
```

Read the current value of a key:

```bash
sysctl net.ipv4.tcp_syncookies
# or
cat /proc/sys/net/ipv4/tcp_syncookies
```

List every key and its value (useful for diffing against a baseline):

```bash
sudo sysctl -a | sort > /tmp/sysctl-current.txt
```

## Categories

Kernel tunables fall into a small number of namespaces. Each has a different
set of concerns:

| Namespace | Controls | Primary security concern |
|---|---|---|
| `net.ipv4.*`, `net.ipv6.*` | TCP/IP stack | DDoS, spoofing, redirects |
| `net.core.*` | Socket buffers, BPF | BPF JIT attacks, buffer exhaustion |
| `kernel.*` | Kernel behaviour | ASLR, info leaks, kexec, ptrace |
| `fs.*` | Filesystem | SUID dumps, link exploits, tmp races |
| `vm.*` | Memory manager | OOM behaviour, overcommit |

## Recommended baseline

Save the following as `/etc/sysctl.d/99-hardening.conf`. Values assume a
standard SaaS web/app server that does NOT act as a router.

```ini
# =========================================================================
# Network layer (see also network-security/SKILL.md for firewall rules)
# =========================================================================

# Accept SYN cookies when the SYN backlog overflows — defends against SYN flood
net.ipv4.tcp_syncookies = 1

# Larger backlog absorbs burst traffic before SYN cookies kick in
net.ipv4.tcp_max_syn_backlog = 4096

# Reverse path filtering — drop packets whose source address is unreachable
# via the interface they arrived on (anti-spoofing, strict mode)
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# Ignore source-routed packets (an attacker specifies the return path)
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0
net.ipv6.conf.default.accept_source_route = 0

# Ignore ICMP redirects (an attacker can change your routing table otherwise)
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv6.conf.default.accept_redirects = 0

# Do not send ICMP redirects (we are not a router)
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0

# Ignore secure redirects too (only "trusted" gateways)
net.ipv4.conf.all.secure_redirects = 0
net.ipv4.conf.default.secure_redirects = 0

# Log packets with impossible source addresses (spoofing attempts)
net.ipv4.conf.all.log_martians = 1
net.ipv4.conf.default.log_martians = 1

# Don't reply to broadcast ICMP (Smurf amplification defence)
net.ipv4.icmp_echo_ignore_broadcasts = 1

# Drop bogus ICMP error responses (avoids polluting logs)
net.ipv4.icmp_ignore_bogus_error_responses = 1

# Don't route traffic between interfaces (this host is not a router)
net.ipv4.ip_forward = 0
net.ipv6.conf.all.forwarding = 0

# Don't accept IPv6 router advertisements — we use static config / DHCP
net.ipv6.conf.all.accept_ra = 0
net.ipv6.conf.default.accept_ra = 0

# TCP timestamps reveal uptime; disable on public hosts
net.ipv4.tcp_timestamps = 0

# Larger TIME_WAIT bucket under heavy HTTP load
net.ipv4.tcp_max_tw_buckets = 1440000

# =========================================================================
# Kernel
# =========================================================================

# Address Space Layout Randomization — full (stack, heap, mmap, vDSO)
kernel.randomize_va_space = 2

# Hide kernel pointers from /proc and dmesg for everyone
kernel.kptr_restrict = 2

# Only privileged users can read dmesg
kernel.dmesg_restrict = 1

# ptrace only allowed on direct children (blocks /proc/<pid>/mem abuse)
kernel.yama.ptrace_scope = 2

# Disable kexec_load — prevents booting an unsigned kernel at runtime
kernel.kexec_load_disabled = 1

# Block unprivileged eBPF programs (historic source of CVEs)
kernel.unprivileged_bpf_disabled = 1

# Harden the BPF JIT against spectre-style exploits
net.core.bpf_jit_harden = 2

# Core dumps include the PID in the filename (simpler forensics)
kernel.core_uses_pid = 1

# Restrict perf_event_open to CAP_PERFMON only
kernel.perf_event_paranoid = 3

# Auto-reboot 10 seconds after a kernel panic (don't hang)
kernel.panic = 10
kernel.panic_on_oops = 1

# Disable the magic SysRq key on production servers
kernel.sysrq = 0

# =========================================================================
# Filesystem
# =========================================================================

# Do not dump core from setuid binaries
fs.suid_dumpable = 0

# Protect against /tmp hardlink race conditions (CVE-2023-*, CVE-2022-*)
fs.protected_hardlinks = 1
fs.protected_symlinks = 1

# Regular files and FIFOs in world-writable dirs can only be opened by owner
fs.protected_fifos = 2
fs.protected_regular = 2
```

Apply immediately:

```bash
sudo sysctl --system
```

## Per-category deep dive

### Network

- **tcp_syncookies** — the classic defence against SYN flood. When the backlog
  fills, the kernel starts answering SYNs with cryptographic cookies instead of
  allocating state. Turning this off on a public SaaS host is an operational
  mistake.
- **rp_filter=1** — strict reverse-path filter. Drops packets arriving on an
  interface that would not be the correct outbound interface for the source.
  Stops most address-spoofing attacks. Turn off only on multi-homed routers
  with asymmetric routing.
- **accept_source_route=0** — source routing lets the sender dictate the path
  and bypass routing controls. No legitimate modern workload uses it.
- **accept_redirects=0, send_redirects=0** — an attacker on-link can use ICMP
  redirects to inject routes. Servers should neither accept nor emit them.
- **log_martians=1** — logs packets with impossible source addresses to
  dmesg/syslog. Useful signal for intrusion detection.
- **icmp_echo_ignore_broadcasts=1** — prevents the host being used as a Smurf
  amplifier. Essential for public-internet hosts.
- **ip_forward=0** — keep forwarding off unless the host is a NAT, VPN, or
  container host. Containers using bridge networking flip this to 1 — that is
  fine; leave it off on hosts that do not need it.

### Kernel

- **randomize_va_space=2** — full ASLR: stack, brk heap, mmap segment, vDSO,
  libraries. Any lower value weakens exploit mitigations dramatically.
- **kptr_restrict=2** — hides kernel pointers from `/proc/kallsyms`,
  `/proc/<pid>/stack`, and netlink interfaces. Without this, a leaked kernel
  pointer lets an attacker bypass KASLR.
- **dmesg_restrict=1** — prevents non-root users reading the kernel ring
  buffer, which often contains KASLR-revealing addresses.
- **ptrace_scope=2** — only processes with `CAP_SYS_PTRACE` can use ptrace.
  Prevents post-exploitation credential stealing via `/proc/<pid>/mem`.
  Setting to 3 disables ptrace entirely; production users debugging with
  `strace`/`gdb` will need an out-of-process mechanism.
- **kexec_load_disabled=1** — disables in-kernel kexec. Once set it cannot be
  cleared without a reboot. Prevents an attacker with root from replacing the
  running kernel without a visible reboot.
- **unprivileged_bpf_disabled=1** — blocks non-root eBPF. The list of
  eBPF-related CVEs is long; disable unless you actively need BCC/BPF tools.
- **perf_event_paranoid=3** — restricts performance counters, which can be
  used as side-channels for speculation attacks.

### Filesystem

- **suid_dumpable=0** — if a setuid binary crashes, do not write a core dump.
  Core files from setuid processes leak secrets.
- **protected_hardlinks/symlinks=1** — the standard Debian protection against
  symlink and hardlink race conditions in world-writable directories like
  `/tmp` and `/var/tmp`.
- **protected_fifos=2, protected_regular=2** — extends the link protection to
  cover FIFO and regular file races. Required by recent CIS benchmarks.

## Verify settings took effect

```bash
# Query individual keys
sudo sysctl net.ipv4.tcp_syncookies kernel.randomize_va_space fs.suid_dumpable

# Compare current state against your config file
for k in $(grep -v '^#' /etc/sysctl.d/99-hardening.conf | grep '=' | cut -d= -f1 | xargs); do
  printf '%-40s ' "$k"
  sudo sysctl -n "$k" 2>/dev/null || echo 'MISSING'
done
```

A missing key usually means the feature is not compiled into your kernel
(common in minimal cloud images). Remove or comment the line if so.

## Kernel module blacklisting

Rare filesystems and network protocols ship as loadable modules. Disable
anything you do not need — modules are common attack surface.

Create `/etc/modprobe.d/blacklist-hardening.conf`:

```ini
# Rare filesystems that SaaS servers do not need — remove any you actually use
install cramfs /bin/false
install freevxfs /bin/false
install jffs2 /bin/false
install hfs /bin/false
install hfsplus /bin/false
install udf /bin/false

# squashfs is used by snap; leave it enabled if you use snap
# install squashfs /bin/false

# Rare network protocols
install dccp /bin/false
install sctp /bin/false
install rds /bin/false
install tipc /bin/false

# Bluetooth and firewire — no physical peripherals on cloud VMs
install bluetooth /bin/false
install firewire-core /bin/false

# USB storage on servers where removable media is never expected
# install usb-storage /bin/false
```

`install <module> /bin/false` is more robust than `blacklist <module>` because
it also blocks manual `modprobe` attempts. After editing:

```bash
# Rebuild initramfs so the blacklist takes effect on early-boot modules
sudo update-initramfs -u

# Verify a blocked module cannot be loaded at runtime
sudo modprobe dccp 2>&1   # should print: install /bin/false ... failed

# Show currently loaded modules
lsmod
```

## GRUB boot hardening

Boot-time kernel parameters are set in `/etc/default/grub`
(`GRUB_CMDLINE_LINUX` / `GRUB_CMDLINE_LINUX_DEFAULT`). After editing, run
`sudo update-grub`.

### Enable AppArmor (Ubuntu default) or SELinux

```ini
GRUB_CMDLINE_LINUX="apparmor=1 security=apparmor audit=1 audit_backlog_limit=8192"
```

The `audit=1` and `audit_backlog_limit=8192` parameters ensure auditd can
capture events from very early boot without losing them to a full buffer.

### Lockdown mode

Linux has an optional lockdown mode that restricts even root from modifying
the running kernel:

```ini
GRUB_CMDLINE_LINUX="lockdown=integrity"
```

Use `integrity` on servers (blocks /dev/mem, kexec, MSRs). Use `confidentiality`
only if you have tested compatibility — it disables many debug features.

### Password-protect the GRUB menu

On physical or colocated hardware, set a GRUB password so an attacker with
console access cannot boot into single-user mode. Use `grub-mkpasswd-pbkdf2`
and add the hash to `/etc/grub.d/40_custom`. Not required on cloud VMs where
the hypervisor owns the boot process.

## Disabling IPv6 (if not used)

If your infrastructure is IPv4-only, disable IPv6 to shrink the attack surface.
There are two approaches:

### Kernel cmdline (preferred — fully disables the stack)

Edit `/etc/default/grub`:

```ini
GRUB_CMDLINE_LINUX="ipv6.disable=1"
```

Then `sudo update-grub && sudo reboot`.

### Sysctl (runtime, partial)

```ini
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
net.ipv6.conf.lo.disable_ipv6 = 1
```

This stops IPv6 on configured interfaces but the module stays loaded. The
cmdline approach is cleaner.

## Lynis audit

Lynis scans sysctl values, module blacklists, boot parameters, and many other
settings against its built-in baseline. Run it after each hardening change.

```bash
sudo apt install -y lynis
sudo lynis audit system

# Just the hardening summary
sudo lynis audit system --quick | grep -E 'Hardening|WARNING|SUGGESTION'
```

Lynis exit code is 0 on clean runs, non-zero when warnings exist — useful in
CI for nightly drift checks. The report file is `/var/log/lynis.log` and
machine-readable output is in `/var/log/lynis-report.dat`.

## Anti-patterns

- **Disabling ASLR** (`kernel.randomize_va_space=0` or `1`). Almost always a
  symptom of a broken legacy binary; fix the binary instead.
- **Setting `suid_dumpable=2`**. Allows setuid processes to write core dumps
  that contain privileged memory.
- **Blindly copying CIS values**. The CIS benchmark is a starting point. Some
  settings (e.g. disabling `usb-storage` on a workstation) break real use
  cases. Understand each setting before applying it.
- **Turning off `ptrace_scope` in production**. Sometimes done to "fix"
  debuggers. The correct fix is to run the debugger as root or temporarily
  lower it on the dev host, not production.
- **Leaving `ip_forward=1` on a non-router**. Turns the host into a free
  intermediate hop for attacker traffic.
- **Settings in `/etc/sysctl.conf` AND `/etc/sysctl.d/`**. Confusing and
  order-dependent. Pick one and stick with it (drop-ins are cleaner).
- **Forgetting `update-initramfs -u` after modprobe blacklist changes**.
  Blacklist only takes effect after the initramfs is rebuilt for any module
  that loads during early boot.

## Cross-references

- `linux-security-hardening/SKILL.md` — top-level hardening workflow
- `linux-security-hardening/references/auditd-logging.md` — pairs with `audit=1`
  kernel cmdline
- `linux-security-hardening/references/rootkit-detection.md` — many kernel
  rootkits are blocked by `kexec_load_disabled` and module blacklists
- `network-security/SKILL.md` — nftables/UFW rules that complement network sysctls
- `cicd-devsecops/SKILL.md` — automating Lynis in CI for drift detection
