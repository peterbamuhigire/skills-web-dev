# Network Security Layer

Network and perimeter security patterns for a SaaS VPS. Load this reference after the core security-audit skill when hardening the network layer or preparing for a penetration test.

## UFW Firewall Rules

Minimum viable firewall for a public-facing SaaS VPS on Debian/Ubuntu. Run these commands in order — the default-deny comes last to avoid locking yourself out:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing

sudo ufw allow 22/tcp comment 'SSH (consider changing port)'
sudo ufw allow 80/tcp comment 'HTTP (for Let''s Encrypt only; redirect to HTTPS)'
sudo ufw allow 443/tcp comment 'HTTPS'

sudo ufw limit 22/tcp comment 'Rate-limit SSH brute force'

sudo ufw --force enable
sudo ufw status verbose
```

Pair with SSH key-only auth in `/etc/ssh/sshd_config`: `PasswordAuthentication no`, `PermitRootLogin no`, `AllowUsers deploy`.

## iptables for Advanced Rules

UFW wraps iptables but some patterns need direct rules. Example: rate-limit HTTPS connections per source IP using `hashlimit`:

```bash
sudo iptables -A INPUT -p tcp --dport 443 -m conntrack --ctstate NEW \
  -m hashlimit --hashlimit-above 30/sec --hashlimit-burst 50 \
  --hashlimit-mode srcip --hashlimit-name https-flood \
  -j DROP
```

Log dropped packets to `/var/log/iptables.log` (requires rsyslog rule):

```bash
sudo iptables -A INPUT -m limit --limit 5/min -j LOG --log-prefix "iptables DROP: " --log-level 4
```

Persist rules across reboots via `iptables-persistent` (Debian/Ubuntu).

## Cloudflare WAF

Managed rule group activation in Cloudflare dashboard:

- Cloudflare Managed Ruleset — enable in simulate mode first for 72 hours to catch false positives
- OWASP Core Rule Set — paranoia level 1 (default), raise to 2 only after tuning
- Exposed Credentials Check — block login attempts with known-leaked creds

Custom rules to add:

- Block by country if product does not serve that geography: `(ip.geoip.country in {"RU" "KP"})`
- IP allowlist for `/admin/*`: `(not ip.src in {1.2.3.4 5.6.7.8}) and (http.request.uri.path contains "/admin")`
- Rate limit `/api/auth/*` to 10 requests per minute per IP

## ModSecurity (self-hosted WAF)

When Cloudflare is not an option, run ModSecurity with Nginx:

```bash
sudo apt install libmodsecurity3 modsecurity-crs
```

Main config `/etc/nginx/modsec/modsecurity.conf`:

- `SecRuleEngine On` (after tuning phase with `DetectionOnly`)
- `SecAuditLogParts ABIJDEFHZ`
- Paranoia level in `/etc/modsecurity-crs/crs-setup.conf`: start at `PL=1`, raise to `PL=2` after a week of clean logs
- Tune false positives via `SecRuleRemoveById` for specific rule IDs that hit legitimate traffic

Check ModSecurity blocks in `/var/log/nginx/modsec_audit.log`. Monitor false positive rate — anything above 5% of blocks means paranoia is too high.

## Zero-Trust Principles

- Never trust network location — being inside the VPC does not imply identity
- Verify identity on every request (short-lived JWT, mTLS between services)
- Least-privilege by default — expand only when justified
- Audit everything — unchangeable log of access decisions and data reads
- Microsegmentation — each service has its own security group, egress rules listed explicitly

Implementation primitives: SPIFFE/SPIRE for service identity, Tailscale or Cloudflare Access for human access, Vault for short-lived credentials, OPA for authorisation decisions.

## WireGuard VPN for Remote Team Access

Server config `/etc/wireguard/wg0.conf`:

```ini
[Interface]
Address = 10.100.0.1/24
ListenPort = 51820
PrivateKey = <server-private-key>
PostUp   = ufw route allow in on wg0 out on eth0
PostDown = ufw route delete allow in on wg0 out on eth0

[Peer]
# engineer-alice
PublicKey = <alice-public-key>
AllowedIPs = 10.100.0.2/32
```

Alice's client config:

```ini
[Interface]
Address = 10.100.0.2/24
PrivateKey = <alice-private-key>
DNS = 1.1.1.1

[Peer]
PublicKey = <server-public-key>
Endpoint = vpn.example.com:51820
AllowedIPs = 10.0.0.0/8    # split tunnel: only corp traffic
PersistentKeepalive = 25
```

Split tunnelling via `AllowedIPs` — route only the corporate CIDR, not all traffic. Full tunnel = `0.0.0.0/0`.

Generate keys with `wg genkey | tee privatekey | wg pubkey > publickey`.

## DDoS Mitigation

Layered approach:

- Cloudflare in front of origin — absorbs volumetric attacks at CDN layer
- Cloudflare Magic Transit for larger network-level attacks (enterprise tier)
- Per-IP rate limiting at CDN (Cloudflare Rate Limiting Rules) or origin (Nginx `limit_req`)
- SYN flood protection: `net.ipv4.tcp_syncookies = 1` in sysctl (also see `cicd-jenkins-debian` references)
- Origin IP never exposed — only CDN IPs in DNS, origin firewalled to accept only Cloudflare IP ranges

Validate monthly: fetch Cloudflare IP list (`cloudflare.com/ips-v4`) and update UFW rules:

```bash
for ip in $(curl -s https://www.cloudflare.com/ips-v4); do
  sudo ufw allow from $ip to any port 443 proto tcp
done
```

## TLS Certificate Lifecycle

- Let's Encrypt via Certbot: `sudo certbot --nginx -d example.com --agree-tos --email ops@example.com`
- Auto-renewal: `certbot.timer` systemd unit, runs twice daily, renews within 30 days of expiry
- HSTS: `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload` (only after confirming all subdomains are HTTPS)
- HSTS Preload submission: `hstspreload.org` — once submitted, cannot easily roll back
- Certificate Transparency monitoring: subscribe to `crt.sh` RSS for your domain to detect rogue certs

Test grade at `ssllabs.com/ssltest` — target A+ rating. Disable TLS 1.0 and 1.1 in `/etc/nginx/nginx.conf`: `ssl_protocols TLSv1.2 TLSv1.3`.
