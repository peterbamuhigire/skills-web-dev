# Network Security Audit Checklist

A 50-point yes/no checklist for auditing a Debian/Ubuntu VPS that hosts a
multi-tenant SaaS. Each item includes a concrete verification command or file.

## How to use

Run this checklist top-to-bottom against a live server. Any unchecked item is a
finding. Record the evidence (command output or file path) alongside the
result. Group findings by severity at the end using the scoring rubric.

## Firewall (10 items)

- [ ] **FW-01** nftables or UFW is active with a default-deny input policy
  (`sudo nft list ruleset | grep 'hook input' | grep -i drop`).
- [ ] **FW-02** Default-deny forward policy is set
  (`sudo nft list ruleset | grep 'hook forward'`).
- [ ] **FW-03** Only the required ports are exposed on the public interface
  (`sudo ss -tulnp | grep -v 127.0.0.1`).
- [ ] **FW-04** Loopback traffic is explicitly allowed
  (`sudo nft list chain inet filter input | grep 'iifname "lo"'`).
- [ ] **FW-05** Established/related connections are accepted early
  (`sudo nft list chain inet filter input | grep 'ct state established'`).
- [ ] **FW-06** ICMP echo is rate-limited, not blanket-dropped
  (`sudo nft list chain inet filter input | grep -i icmp`).
- [ ] **FW-07** Dropped packets are logged with a prefix for alerting
  (`sudo nft list ruleset | grep 'log prefix'`).
- [ ] **FW-08** Mixed iptables/nftables rules are not present
  (`sudo iptables -S` should be empty or only contain nftables-compat rules).
- [ ] **FW-09** Firewall ruleset is loaded at boot via systemd unit
  (`systemctl is-enabled nftables`).
- [ ] **FW-10** Egress filter restricts outbound from sensitive tiers to an
  allow-list (`sudo nft list chain inet filter output`).

## SSH (8 items)

- [ ] **SSH-01** `PasswordAuthentication no` in `/etc/ssh/sshd_config`
  (`sudo grep -i ^PasswordAuthentication /etc/ssh/sshd_config`).
- [ ] **SSH-02** `PermitRootLogin no`
  (`sudo grep -i ^PermitRootLogin /etc/ssh/sshd_config`).
- [ ] **SSH-03** Only key-based authentication is allowed
  (`sudo grep -i ^PubkeyAuthentication /etc/ssh/sshd_config`).
- [ ] **SSH-04** `MaxAuthTries` is 3 or lower
  (`sudo grep -i ^MaxAuthTries /etc/ssh/sshd_config`).
- [ ] **SSH-05** Fail2ban jail for sshd is active
  (`sudo fail2ban-client status sshd`).
- [ ] **SSH-06** SSH listens on a non-standard port or only on a bastion
  (`sudo grep -i ^Port /etc/ssh/sshd_config`).
- [ ] **SSH-07** `sshd_config` permissions are `600` and owned by root
  (`sudo stat -c '%a %U' /etc/ssh/sshd_config`).
- [ ] **SSH-08** Agent forwarding is disabled by default
  (`sudo grep -i ^AllowAgentForwarding /etc/ssh/sshd_config`).

## TLS (6 items)

- [ ] **TLS-01** All public HTTP endpoints listen on TLS 1.3
  (`nmap --script ssl-enum-ciphers -p 443 example.com`).
- [ ] **TLS-02** Certificates are valid and not near expiry
  (`echo | openssl s_client -servername example.com -connect example.com:443 2>/dev/null | openssl x509 -noout -dates`).
- [ ] **TLS-03** HSTS header is sent with a sensible max-age
  (`curl -I https://example.com | grep -i strict-transport`).
- [ ] **TLS-04** OCSP stapling is enabled on nginx
  (`sudo grep -i ocsp /etc/nginx/conf.d/*.conf`).
- [ ] **TLS-05** Certificate expiry alerting is configured
  (`sudo systemctl list-timers | grep cert`).
- [ ] **TLS-06** Plain HTTP requests redirect to HTTPS
  (`curl -I http://example.com | grep -i '^location: https'`).

## WAF (4 items)

- [ ] **WAF-01** ModSecurity or equivalent WAF is active on every public web app
  (`sudo nginx -T | grep -i modsecurity`).
- [ ] **WAF-02** OWASP Core Rule Set is installed and updated within 30 days
  (`ls -l /etc/modsecurity/crs/`).
- [ ] **WAF-03** WAF audit log is shipped off-box to a central log store
  (`sudo grep -i auditlog /etc/modsecurity/modsecurity.conf`).
- [ ] **WAF-04** HTTP rate limiting is enforced per IP and per path
  (`sudo grep -i limit_req /etc/nginx/nginx.conf`).

## DDoS sysctls (4 items)

- [ ] **DDO-01** `net.ipv4.tcp_syncookies = 1`
  (`sysctl net.ipv4.tcp_syncookies`).
- [ ] **DDO-02** `net.ipv4.tcp_max_syn_backlog >= 4096`
  (`sysctl net.ipv4.tcp_max_syn_backlog`).
- [ ] **DDO-03** `net.core.somaxconn >= 4096`
  (`sysctl net.core.somaxconn`).
- [ ] **DDO-04** Reverse path filtering enabled on all interfaces
  (`sysctl net.ipv4.conf.all.rp_filter`).

## IDS and logging (5 items)

- [ ] **IDS-01** Suricata, Zeek, or equivalent NIDS is active
  (`sudo systemctl is-active suricata`).
- [ ] **IDS-02** Logs are shipped off-box (journald-remote, Vector, rsyslog)
  (`sudo systemctl is-active vector || sudo systemctl is-active rsyslog`).
- [ ] **IDS-03** Fail2ban is active with application jails beyond sshd
  (`sudo fail2ban-client status`).
- [ ] **IDS-04** `auditd` is running with relevant rules loaded
  (`sudo auditctl -l`).
- [ ] **IDS-05** Alerting triggers on SSH brute force and WAF spikes
  (check alertmanager or equivalent config).

## DNS (3 items)

- [ ] **DNS-01** Authoritative zone is DNSSEC-signed and DS is at the registrar
  (`dig +dnssec example.com SOA`, `dig example.com DS @parent`).
- [ ] **DNS-02** CAA records restrict issuing CAs
  (`dig example.com CAA +short`).
- [ ] **DNS-03** Host is not an open recursive resolver
  (`dig @public-ip google.com` from an external box).

## Segmentation (4 items)

- [ ] **SEG-01** Database ports are not reachable from the public interface
  (`sudo ss -tnlp | grep -E '3306|5432|6379'` should show loopback/private only).
- [ ] **SEG-02** Admin interfaces are on a separate plane (WireGuard, VLAN)
  (`sudo nft list ruleset | grep -E '8080|9090|15672|3306'`).
- [ ] **SEG-03** Outbound egress is filtered for app and data tiers
  (`sudo nft list chain inet filter output`).
- [ ] **SEG-04** Containers are not running on `--network host` without reason
  (`sudo docker ps --format '{{.Names}} {{.Networks}}'`).

## Patching (3 items)

- [ ] **PAT-01** `unattended-upgrades` is installed and enabled
  (`sudo systemctl is-enabled unattended-upgrades`).
- [ ] **PAT-02** Security updates have been applied within the last 7 days
  (`grep -i security /var/log/apt/history.log | tail`).
- [ ] **PAT-03** Kernel reboots are scheduled when livepatch is not used
  (`sudo needrestart -r l` or `uname -r` vs `dpkg -l linux-image-*`).

## Monitoring (3 items)

- [ ] **MON-01** Certificate expiry alerts fire at 30 and 7 days
  (check Prometheus/alertmanager or `certbot renew --dry-run`).
- [ ] **MON-02** Failed-login alerts are routed to a pager/channel
  (check alert rule for `auth.log` or Fail2ban events).
- [ ] **MON-03** Traffic baseline alerts on unusual inbound/outbound volume
  (check NetFlow/ntopng or Prometheus node_exporter rules).

## Scoring

Rate every unchecked item with the following severity guide, then compute a
pass/fail result.

| Category | Severity | Rule |
|---|---|---|
| FW-*, SSH-* | Critical | Any single miss = audit fail |
| TLS-*, WAF-* | High | Up to one miss allowed with compensating control |
| DDO-*, IDS-*, DNS-*, SEG-* | High | Up to two misses allowed |
| PAT-*, MON-* | Medium | Remediation plan required within 14 days |

**Audit pass:** Zero critical findings, no more than two high findings, and
documented remediation for all medium findings.

## Cross-references

- `firewall-strategy.md` for the source rules being audited.
- `ssh-bastion.md` for SSH hardening details.
- `tls-cert-management.md` for TLS and CAA specifics.
- `waf-modsecurity.md` for WAF verification.
- `ddos-protection.md` for sysctl defaults and rate-limiting rules.
- `ids-logging.md` for IDS tuning and log shipping.
- `dns-security.md` for DNS item details.
- `network-segmentation.md` for segmentation context.
