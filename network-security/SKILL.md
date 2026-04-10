---
name: network-security
description: Use when designing, hardening, or auditing network-layer security for self-managed Debian/Ubuntu SaaS infrastructure — firewalls (nftables/UFW), WAF (ModSecurity + OWASP CRS), VPN (WireGuard, OpenVPN, IPsec), TLS/PKI ops, IDS/IPS (Suricata, Fail2ban), zero-trust, SSH hardening, DDoS mitigation, DNS security. Complements web-app-security-audit (app layer) and cicd-devsecops (secrets/CI).
---

# Network Security

Defensive network architecture for self-managed Debian/Ubuntu SaaS infrastructure. Covers layers 3/4/7 — from nftables rules up to zero-trust identity-aware proxies.

**Core principle:** Defense in depth. No single control is a silver bullet. Firewall, WAF, TLS, IDS, segmentation, identity — every layer fails safely when the next one still holds.

**Scope:** Network-layer security on your own servers. For app-code vulnerabilities use `web-app-security-audit`. For secrets/CI hardening use `cicd-devsecops`. For Linux OS hardening beyond network use `linux-security-hardening`.

**Cross-references:** `web-app-security-audit`, `cicd-devsecops`, `cicd-jenkins-debian`, `linux-security-hardening`, `microservices-architecture-models`, `realtime-systems`

**See `references/` for:** `firewalls.md`, `waf.md`, `tls-pki.md`, `vpn.md`, `ssh-bastion.md`, `ids-ips.md`, `ddos.md`, `dns-security.md`, `zero-trust.md`, `crypto-fundamentals.md`, `network-segmentation.md`, `audit-checklist.md`, `incident-runbook.md`

## When to Use

- Before provisioning a new production VPS
- Before exposing a service to the public internet
- After a network-reachable CVE is disclosed
- Quarterly as a standing audit cadence
- During incident response
- When designing a new tier of infrastructure (microservice plane, DB replica, CDN origin)
- When migrating from perimeter-based to zero-trust model

## Threat Model First

Before configuring a single rule, know what you are defending against.

**Primary adversaries:**

| Adversary | Motivation | Typical vectors |
|-----------|------------|-----------------|
| External opportunist | Resource theft, crypto-mining, spam relay | Exposed services, default creds, unpatched CVEs |
| Targeted attacker | Data exfil, ransomware, espionage | Phishing, supply chain, 0-day, credential theft |
| Insider | Data theft, sabotage | Abuse of legitimate access |
| Lateral attacker | Privilege escalation after initial foothold | Weak internal segmentation, shared creds |

**Defense layers (outside → in):**

1. Edge — Cloudflare/Fastly (optional): DDoS absorption, bot filtering
2. Network perimeter — nftables/UFW firewall on every host
3. Transport — TLS 1.3 with strong ciphers on all external traffic
4. Application gate — WAF (ModSecurity + OWASP CRS) at reverse proxy
5. Identity — oauth2-proxy / Keycloak / Authelia for admin surfaces
6. Service-to-service — mTLS or WireGuard mesh for internal calls
7. Runtime — Suricata IDS, Fail2ban, auditd monitoring

## The 9 Network Security Domains

| # | Domain | Reference |
|---|--------|-----------|
| 1 | Host firewall (nftables/UFW) | `references/firewalls.md` |
| 2 | Edge WAF (ModSecurity + OWASP CRS) | `references/waf.md` |
| 3 | TLS/PKI operations | `references/tls-pki.md` |
| 4 | VPN (WireGuard, OpenVPN, IPsec) | `references/vpn.md` |
| 5 | SSH hardening + bastion | `references/ssh-bastion.md` |
| 6 | IDS/IPS + Fail2ban | `references/ids-ips.md` |
| 7 | DDoS mitigation | `references/ddos.md` |
| 8 | DNS security | `references/dns-security.md` |
| 9 | Zero-trust architecture | `references/zero-trust.md` |

Supporting reference material: `references/crypto-fundamentals.md` (primitives), `references/network-segmentation.md` (topology), `references/audit-checklist.md` (50-point audit), `references/incident-runbook.md` (5 response playbooks).

## Phase 1: Baseline Network Hardening Checklist

Run this against every fresh Debian 12 / Ubuntu 24.04 VPS before it serves production traffic.

### 1.1 System baseline

```bash
apt update && apt upgrade -y
apt install -y nftables ufw fail2ban unattended-upgrades auditd rkhunter
systemctl enable --now unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

Edit `/etc/apt/apt.conf.d/50unattended-upgrades` to include security updates and enable automatic reboot at a quiet hour.

### 1.2 Firewall (UFW quickstart)

```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp   comment 'ssh'
ufw allow 80/tcp   comment 'http'
ufw allow 443/tcp  comment 'https'
ufw logging on
ufw enable
ufw status verbose
```

For production-grade stateful rules, migrate to nftables — see `references/firewalls.md` for a full `/etc/nftables.conf` template.

### 1.3 Kernel network sysctls

Create `/etc/sysctl.d/99-network-hardening.conf`:

```ini
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 4096
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.icmp_ignore_bogus_error_responses = 1
net.ipv4.conf.all.log_martians = 1
net.core.somaxconn = 4096
net.ipv6.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_source_route = 0
```

Apply: `sysctl --system`

### 1.4 SSH hardening (minimum viable)

Edit `/etc/ssh/sshd_config`:

```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
LoginGraceTime 30
ClientAliveInterval 300
ClientAliveCountMax 2
X11Forwarding no
AllowAgentForwarding no
AllowUsers deploy admin
```

Then `systemctl reload ssh`. Full hardening in `references/ssh-bastion.md`.

### 1.5 Fail2ban

```bash
cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
```

In `/etc/fail2ban/jail.local` set `bantime = 1h`, `findtime = 10m`, `maxretry = 5`, enable `[sshd]` jail with `nftables` backend. Reload: `systemctl restart fail2ban`.

### 1.6 TLS certificates

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d example.com -d www.example.com --redirect --hsts --staple-ocsp
```

Certbot installs a systemd timer that renews automatically. Verify: `systemctl list-timers | grep certbot`.

### 1.7 Disable unused services

```bash
systemctl list-unit-files --state=enabled
systemctl disable --now <service>
```

Kill defaults you do not use: avahi-daemon, cups, rpcbind, postfix (unless you actually send mail).

### 1.8 Verification

```bash
ss -tlnp              # which services listen on which ports
nft list ruleset      # current firewall state
sshd -T | grep -iE 'permitroot|password|pubkey'
fail2ban-client status sshd
certbot certificates
```

## Phase 2: Service-Specific Hardening

### Nginx as reverse proxy

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_protocols TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;

    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header Referrer-Policy strict-origin-when-cross-origin always;
    add_header Content-Security-Policy "default-src 'self'" always;

    # ModSecurity
    modsecurity on;
    modsecurity_rules_file /etc/nginx/modsec/main.conf;

    # Rate limit
    limit_req zone=api burst=20 nodelay;
    limit_conn addr 10;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Full WAF setup and rule tuning: `references/waf.md`.

### PostgreSQL / MySQL

Bind to loopback or WireGuard interface only:

```ini
# postgresql.conf
listen_addresses = '127.0.0.1,10.10.0.1'

# my.cnf
bind-address = 127.0.0.1
```

Lock down `pg_hba.conf` with `hostssl ... md5` from app tier CIDR only. Require TLS at the server level (`ssl = on`, `ssl_cert_file`, `ssl_key_file`). For multi-tenant rules, see `mysql-best-practices` and `postgresql-administration`.

### Redis

```conf
bind 127.0.0.1
protected-mode yes
requirepass <strong-password>
rename-command CONFIG ""
rename-command FLUSHALL ""
rename-command FLUSHDB ""
```

Never expose Redis to the internet. If distributed access is needed, route via WireGuard or `stunnel`.

## Phase 3: Zero-Trust Layer

Once the perimeter is hardened, replace implicit "internal network = trusted" with explicit verification.

**Minimum viable zero-trust in 3 steps:**

1. **Identity-aware proxy for admin panels** — oauth2-proxy in front of every admin surface, enforced via nginx `auth_request` directive.
2. **mTLS between internal services** — issue short-lived client certs from an internal CA (step-ca), rotate daily.
3. **WireGuard private mesh** — give every service a private `10.x` address reachable only via WG peer; bind all non-public services to the WG interface.

Full migration roadmap and config examples: `references/zero-trust.md`.

## Phase 4: Monitoring and Detection

**Install Suricata as IDS:**

```bash
apt install -y suricata
suricata-update
systemctl enable --now suricata
```

Configure `/etc/suricata/suricata.yaml` with your external interface and `HOME_NET`. Alerts land in `/var/log/suricata/eve.json` as JSON.

**Ship logs off-host** to SigNoz / Loki / OpenSearch via Filebeat or Vector. Local-only logs disappear when the host is compromised.

**Alert triggers to set:**

- SSH brute force (Fail2ban jail hit threshold)
- New outbound destination not in allow list (Suricata custom rule)
- Certificate expiring in < 14 days (blackbox_exporter)
- Large outbound volume from DB host
- Process with a reverse shell fingerprint (auditd rule)

Full configuration: `references/ids-ips.md`.

## Phase 5: Incident Response Runbook

When an incident is in progress:

1. **Detect** — confirm via logs, IDS alerts, user reports
2. **Contain** — block at the firewall set, isolate host, revoke creds
3. **Preserve** — capture memory, disk, logs before reboot
4. **Eradicate** — remove malware, patch vuln, rotate secrets
5. **Recover** — restore from clean backup, monitor closely
6. **Review** — blameless postmortem within 72 hours

Five step-by-step playbooks (SSH brute force, data exfil, DDoS in progress, cert compromise, lateral movement): `references/incident-runbook.md`.

## Audit Checklist (Summary)

The full 50-point audit is in `references/audit-checklist.md`. Headline items:

- [ ] Firewall default deny inbound with logging
- [ ] SSH: key-only, root disabled, Fail2ban active
- [ ] All public traffic on TLS 1.3 with HSTS and OCSP stapling
- [ ] Cert expiry monitored with alerts at 14 and 3 days
- [ ] WAF (ModSecurity + CRS) on all public web surfaces
- [ ] Suricata or equivalent IDS, logs shipped off-host
- [ ] Kernel sysctls: SYN cookies, rp_filter, martians logged
- [ ] DB and Redis bound to loopback or WG interface only
- [ ] DNSSEC on authoritative zones, CAA records present
- [ ] Automatic security updates enabled with reboot cron
- [ ] Admin surfaces behind identity-aware proxy, not public
- [ ] Incident runbook tested within last 6 months

## Anti-Patterns

**Do not:**

- Treat "we have a firewall" as sufficient. A firewall is a minimum, not a strategy.
- Run services as root. Every daemon needs its own unprivileged user and systemd `DynamicUser=true` when possible.
- Use self-signed certificates in production for public-facing services.
- Disable HTTPS certificate verification in client code "temporarily."
- Expose Redis, MongoDB, Elasticsearch, memcached, or any database to the public internet.
- Deploy a WAF at paranoia level 1 and never revisit the tuning.
- Use SSH port 22 change as the primary defense (it is security theatre).
- Share SSH keys across team members — use per-person keys and SSH CA.
- Trust the internal network ("east-west is fine, nothing listens there"). Assume breach.
- Forget cert expiry — outages from expired certs outnumber outages from compromised certs.
- Allow unlimited outbound from sensitive tiers. Database servers rarely need to reach the public internet.
- Mix legacy `iptables` and `nftables` on the same host — pick one.
- Use wildcard TLS certificates across multi-tenant subdomains without SNI isolation.
- Log drop events to disk forever without rotation — fills the disk during an attack.
- Treat zero-trust as a product purchase. It is an architecture migration.

## References Index

**Domain references:**

- `references/firewalls.md` — nftables, UFW, stateful rules, DMZ, hardening templates
- `references/waf.md` — ModSecurity 3, OWASP CRS, tuning, Nginx integration
- `references/tls-pki.md` — TLS 1.3, Let's Encrypt, internal CA, mTLS, monitoring
- `references/vpn.md` — WireGuard, OpenVPN, IPsec, site-to-site, mesh patterns
- `references/ssh-bastion.md` — sshd_config hardening, bastion topology, MFA
- `references/ids-ips.md` — Suricata, Fail2ban, log shipping, alert triage
- `references/ddos.md` — L3/L4/L7 attack taxonomy, sysctls, edge mitigation
- `references/dns-security.md` — DNSSEC, DoH/DoT, split-horizon, CAA records
- `references/zero-trust.md` — BeyondCorp, IAP, mTLS, migration roadmap

**Supporting references:**

- `references/crypto-fundamentals.md` — 2026 primitive recommendations
- `references/network-segmentation.md` — 3-tier topology, namespaces, VLANs
- `references/audit-checklist.md` — 50-point VPS audit
- `references/incident-runbook.md` — 5 response playbooks

**Related skills:**

- `web-app-security-audit` — app-layer vulnerabilities (XSS, SQLi, auth flaws)
- `cicd-devsecops` — secrets management, dependency scanning, supply chain
- `cicd-jenkins-debian` — Debian server provisioning and Jenkins hardening
- `linux-security-hardening` — OS-level hardening beyond network
- `microservices-architecture-models` — service mesh, gateway patterns
- `realtime-systems` — WSS/TLS for WebSocket connections
- `dual-auth-rbac` — session + JWT authentication patterns
