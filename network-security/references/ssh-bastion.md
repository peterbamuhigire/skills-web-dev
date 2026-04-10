# SSH Hardening and Bastion Host Patterns

Production SSH hardening for self-managed Debian/Ubuntu SaaS hosts. Covers `sshd_config`, key management, bastion topology, session recording, Fail2ban, and MFA.

## SSH threat model

SSH is the highest-value target on any Linux server. Realistic threats:

- **Brute force and credential stuffing** — automated bots hammering port 22 with leaked password lists. Visible in `/var/log/auth.log` within minutes of a new public host.
- **Credential theft** — stolen developer laptops with unprotected private keys, phishing for passphrases, malware on a dev workstation.
- **Session hijack** — attacker on the same LAN as an active session, or a compromised bastion reading live terminal buffers.
- **Agent forwarding abuse** — when you SSH with `-A` into a host, that host can silently sign with your local key for any other host the attacker pivots to.
- **Lateral movement** — one shared SSH key reused across 50 servers means one compromise gives the whole fleet.

Assume port 22 is being scanned continuously. Assume any host you SSH into may be compromised. Design accordingly.

## sshd_config hardening

Edit `/etc/ssh/sshd_config`. Back up first: `cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak`.

```conf
# /etc/ssh/sshd_config — production baseline (2026)

# Port — 22 is fine. Moving to a high port is security theatre against
# targeted attackers (they scan all 65535 ports) but does reduce noise
# in logs from dumb bots. Only move it if your monitoring benefits.
Port 22
AddressFamily inet
ListenAddress 0.0.0.0

# Protocol 2 is implicit in modern OpenSSH but leave it documented.
Protocol 2

# Never allow root over SSH. Use a regular user + sudo.
PermitRootLogin no

# Passwords are banned. Keys only.
PasswordAuthentication no
PermitEmptyPasswords no
ChallengeResponseAuthentication no
KbdInteractiveAuthentication no

# Public keys are the only accepted method.
PubkeyAuthentication yes
AuthenticationMethods publickey

# Per-user key file location.
AuthorizedKeysFile .ssh/authorized_keys

# Restrict logins to an explicit allow list. Add a group, not a huge
# user list. Every new engineer gets added to the ssh-users group.
AllowGroups ssh-users

# Brute-force mitigation.
MaxAuthTries 3
MaxSessions 4
LoginGraceTime 30

# Idle session timeout — disconnect after 5 minutes of silence.
ClientAliveInterval 300
ClientAliveCountMax 0

# Strong modern crypto (OpenSSH 9.x defaults, pinned explicitly).
KexAlgorithms sntrup761x25519-sha512@openssh.com,curve25519-sha256,curve25519-sha256@libssh.org
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com,umac-128-etm@openssh.com
HostKeyAlgorithms ssh-ed25519,rsa-sha2-512,rsa-sha2-256

# Disable forwarding features unless explicitly needed.
X11Forwarding no
AllowTcpForwarding no
AllowAgentForwarding no
PermitTunnel no
GatewayPorts no
PermitUserEnvironment no

# Separate privilege and log aggressively.
UsePAM yes
LogLevel VERBOSE
SyslogFacility AUTH

# No banners that leak software version.
DebianBanner no
```

### Match blocks for per-user overrides

Add at the end of the file. Example: allow agent forwarding only from the bastion user group, allow TCP forwarding only for a tunnelling user.

```conf
Match Group bastion-ops
    AllowAgentForwarding yes
    AllowTcpForwarding yes

Match User tunnel-svc
    AllowTcpForwarding yes
    ForceCommand /usr/sbin/nologin
    PermitOpen localhost:5432
```

Validate and reload:

```bash
sudo sshd -t                   # syntax check — no output means OK
sudo systemctl reload ssh      # Debian 12+
sudo systemctl reload sshd     # older releases
```

## Key management

### Generate Ed25519 keys

```bash
# On the developer workstation, not the server.
ssh-keygen -t ed25519 -a 100 -C "alice@example.com-2026-04"
# -a 100 increases KDF rounds — slows offline passphrase brute force.
# Always set a strong passphrase when prompted. Empty passphrase is
# equivalent to leaving the key on disk in plaintext.
```

Legacy RSA? If you must, use `ssh-keygen -t rsa -b 4096 -a 100`. Prefer Ed25519 for all new keys.

### Deploy keys correctly

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub alice@prod-web
# or, manually:
cat ~/.ssh/id_ed25519.pub | ssh alice@prod-web 'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys'
```

Permissions matter. A loose mode will cause sshd to silently reject the key:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
chown -R alice:alice ~/.ssh
```

### Key rotation and removal

Every engineer who leaves gets their keys removed the same day. Automate with config management (Ansible, a `users` module seeded from an LDAP group). Manual check:

```bash
# Audit authorized_keys across all user homes.
sudo awk -F: '$6 ~ /^\/home/ {print $1}' /etc/passwd | \
  xargs -I{} sudo cat /home/{}/.ssh/authorized_keys 2>/dev/null
```

## SSH certificate authority

Once you pass roughly 50 hosts, `authorized_keys` distribution becomes a maintenance burden. Use an SSH CA: a trusted signing key issues short-lived user certificates, servers trust the CA instead of individual keys.

```bash
# Generate the CA (keep offline, HSM-protected in production).
ssh-keygen -t ed25519 -f ca_user_key -C "user-ca-2026"

# Sign a user's public key with a 1-hour validity window.
ssh-keygen -s ca_user_key \
  -I "alice@example.com" \
  -n alice \
  -V +1h \
  alice.pub
# Produces alice-cert.pub — ship that to the user.
```

On every server, add to `/etc/ssh/sshd_config`:

```conf
TrustedUserCAKeys /etc/ssh/ca_user_key.pub
```

Now users present certs (not raw keys) and the server never needs per-user files. Revocation is free — the cert just expires. Tools like HashiCorp Vault and Smallstep `step-ca` issue SSH certs with OAuth/OIDC on the front.

## Bastion / jump host topology

Rule: no production host has a public SSH port. Everything SSH goes through one (or two for HA) hardened bastion hosts.

```
[ engineer laptop ]
        |
        |  ssh -J bastion.example.com prod-web
        v
[ bastion.example.com ]  (only host with public :22)
        |
        v
[ prod-web ] [ prod-db ] [ prod-worker ]   (SSH listens on 10.0.0.0/16 only)
```

Use ProxyJump, not the old `ProxyCommand` with netcat. Configure once in `~/.ssh/config`:

```conf
Host bastion
    HostName bastion.example.com
    User alice
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes

Host prod-*
    User alice
    ProxyJump bastion
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
```

Now `ssh prod-web` transparently jumps through the bastion. No agent forwarding required.

On the bastion itself: strip to the minimum. No compilers, no docker, no kubectl. Auditd on, aggressive log shipping, no outbound internet except to the private subnet. A compromised bastion must not become a foothold.

## Session recording with tlog

For audit/compliance, record every shell session on the bastion.

```bash
sudo apt install tlog
# Configure system-wide in /etc/tlog/tlog-rec-session.conf:
#   "writer": "journal"
#   "log": { "input": true, "output": true, "window": true }

# Make tlog-rec-session the login shell for audited users:
sudo usermod -s /usr/bin/tlog-rec-session alice
```

Sessions now stream to the journal. Ship to a central log store and replay with `tlog-play`.

## Fail2ban for SSH

Fail2ban watches `auth.log` and temporarily bans IPs that fail auth too many times. It is not a substitute for disabling passwords, but it reduces log noise and slows aggressive scanners.

```bash
sudo apt install fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
```

Create `/etc/fail2ban/jail.d/sshd.local`:

```ini
[sshd]
enabled  = true
port     = 22
filter   = sshd
backend  = systemd
maxretry = 3
findtime = 10m
bantime  = 24h
ignoreip = 127.0.0.1/8 10.0.0.0/8
```

Reload and verify:

```bash
sudo systemctl restart fail2ban
sudo fail2ban-client status sshd
```

## MFA with pam_google_authenticator

For bastions accessed from the public internet, layer TOTP on top of keys.

```bash
sudo apt install libpam-google-authenticator

# Each user runs this once and scans the QR code:
google-authenticator -t -d -f -r 3 -R 30 -W
```

Edit `/etc/pam.d/sshd`, add at the top:

```pam
auth required pam_google_authenticator.so nullok
```

Edit `/etc/ssh/sshd_config`:

```conf
KbdInteractiveAuthentication yes
AuthenticationMethods publickey,keyboard-interactive
```

Now login requires a valid key AND a valid 6-digit TOTP. `nullok` lets users without a configured token still log in while you roll it out; remove once everyone is enrolled.

## Agent forwarding dangers

`ssh -A` (or `ForwardAgent yes`) exposes your local SSH agent socket on the remote host. Anyone root on that remote — or any process that reads `$SSH_AUTH_SOCK` — can use your key to authenticate to any other server for the lifetime of the session. They cannot read the key, but they can sign as you.

Rules:

- Never set `ForwardAgent yes` in `~/.ssh/config` globally.
- Prefer ProxyJump (jumps are transparent and do not forward the agent).
- If you genuinely need forwarding (e.g. pushing to a git remote from the server), use `-A` per invocation and only to hosts you fully trust.
- Use `ssh-add -c` for local keys so every signing prompts a confirmation dialog.

## Anti-patterns

Avoid these at all costs:

- **Permitting root over SSH.** Use a named user and sudo. Root login erases accountability in logs.
- **Password authentication on any public host.** Keys only, always. Brute force wins eventually.
- **Port obscurity as the only defence.** Moving to port 2222 does not stop a targeted attacker who scans all ports.
- **Shared keys across a team.** One key leaks, you rotate for everyone. Issue per-engineer keys (or SSH certs).
- **Agent forwarding into untrusted shells.** Especially into shared multi-user servers or anything running third-party code.
- **Leaving authorized_keys entries for former employees.** Automate offboarding or audit weekly.
- **Public SSH on every host.** Use a bastion. One hardened entry point is cheaper to defend than fifty.
- **No idle timeout.** Forgotten terminal on a cafe laptop is the easiest lateral movement vector.

## Cross-references

- `references/firewall-fundamentals.md` — nftables rules restricting port 22 to bastion source IPs
- `references/ids-ips.md` — Fail2ban in the broader IDS context
- `references/zero-trust.md` — replacing the bastion with identity-aware proxy and WireGuard mesh
- `SKILL.md` — network-security skill overview
- `linux-security-hardening` skill — auditd, AppArmor, kernel hardening on the bastion
- `cicd-devsecops` skill — secrets rotation including SSH CA keys
