# Firewalls on Debian/Ubuntu

Practical reference for designing and operating firewalls on self-managed
Debian 12 / Ubuntu 24.04 VPS hosts running multi-tenant SaaS workloads.

## 1. Firewall types

A firewall is a policy enforcement point between networks. Four implementation
styles dominate production deployments, and most real estates use more than one
at different tiers (edge, host, application).

| Type              | Inspects                    | State aware | Strengths                                    | Weaknesses                         |
|-------------------|-----------------------------|-------------|----------------------------------------------|------------------------------------|
| Packet filter     | IP, port, protocol flags    | No          | Fast, simple, low memory                     | Blind to sessions; easy to evade   |
| Stateful          | Above + connection state    | Yes         | Correct return-traffic handling, RELATED     | CPU/RAM scales with conn table     |
| Application proxy | Full L7 payload, terminates | Yes         | Deep inspection, protocol validation         | Latency, per-protocol proxy needed |
| NGFW              | L3-L7 + IDS/IPS + app ID    | Yes         | Identity + app awareness, TLS inspect, URLs  | Cost, complexity, licence lock-in  |

For a single-VPS SaaS, **host stateful filter (nftables) + reverse-proxy WAF**
is the baseline. Commercial NGFW appliances are typically overkill until you
have a multi-node edge network.

## 2. OSI layer mapping

```text
L7  Application  -> Application proxy, WAF, NGFW app-ID
L6  Presentation -> (TLS terminators sit here, not "firewalls" strictly)
L5  Session      -> Circuit-level gateways (SOCKS)
L4  Transport    -> Stateful filters (TCP/UDP, flags, state)
L3  Network      -> Packet filters (IP, ICMP, routing)
L2  Data link    -> ebtables / bridge filter (rare)
L1  Physical     -> Air gap, port disable
```

The higher the layer, the more context the firewall has, and the more CPU it
burns per packet. Defence in depth means stacking: L3/L4 stateful at the host,
L7 WAF in the reverse proxy, and (optionally) L7 at the CDN/edge.

## 3. Debian/Ubuntu firewall stack

Modern Debian/Ubuntu ships three interfaces to the kernel's Netfilter
subsystem. Understand which one you are using — **do not mix them**.

| Tool         | Package              | Notes                                                  |
|--------------|----------------------|--------------------------------------------------------|
| **nftables** | `nftables`           | Default on Debian 11+ and Ubuntu 22.04+. Successor to iptables. Single binary (`nft`). Unified IPv4/IPv6. |
| iptables     | `iptables`           | Legacy. On Debian 12, `iptables` is a compatibility shim that writes to `iptables-nft`. Avoid for new deployments. |
| UFW          | `ufw`                | Friendly wrapper. Under the hood it generates iptables/nftables rules. Good for small hosts, limited for complex policy. |
| firewalld    | `firewalld`          | Zone-based wrapper popular on RHEL. Works on Debian but not default. |

Rule of thumb: **UFW for simple hosts**, **raw nftables for anything with DMZ,
rate limiting, or multi-interface routing**.

Check which is active:

```bash
sudo systemctl status nftables
sudo systemctl status ufw
sudo nft list ruleset | head
sudo iptables -S          # empty output on a pure nftables system
```

Disable legacy tooling if you are going pure nftables:

```bash
sudo apt purge iptables-persistent ufw
sudo systemctl enable --now nftables
```

## 4. UFW quickstart

UFW is appropriate for a single-purpose VPS (web, bastion). Five commands get
you to a sane default:

```bash
sudo apt install ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw limit 22/tcp comment 'SSH with brute-force throttle'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw logging medium
sudo ufw enable
sudo ufw status verbose
```

`ufw limit` applies a crude rate cap (6 connections / 30s per source) which is
enough to blunt unauthenticated SSH brute force. For real rate control, drop
down to nftables.

Delete a rule by number:

```bash
sudo ufw status numbered
sudo ufw delete 3
```

Logs go to `/var/log/ufw.log` and `journalctl -u ufw`.

## 5. nftables baseline ruleset

Drop-in `/etc/nftables.conf` for a public web host. Save, then
`sudo systemctl reload nftables`.

```nft
#!/usr/sbin/nft -f
flush ruleset

table inet filter {
    # Named sets for readable allow-lists
    set admin_ips {
        type ipv4_addr
        elements = { 203.0.113.10, 198.51.100.22 }
    }

    chain input {
        type filter hook input priority 0; policy drop;

        # 1. Loopback is always trusted
        iif "lo" accept
        ip saddr 127.0.0.0/8 iif != "lo" drop comment "anti-spoof loopback"

        # 2. Drop obviously invalid packets
        ct state invalid drop
        tcp flags & (fin|syn|rst|ack) != syn ct state new drop

        # 3. Allow return traffic for our outbound connections
        ct state { established, related } accept

        # 4. ICMP (rate-limited) — do not black-hole, Path MTU needs it
        ip protocol icmp icmp type { echo-request, destination-unreachable, time-exceeded, parameter-problem } limit rate 10/second accept
        ip6 nexthdr icmpv6 icmpv6 type { echo-request, nd-neighbor-solicit, nd-neighbor-advert, nd-router-advert, packet-too-big, time-exceeded, parameter-problem, destination-unreachable } accept

        # 5. SSH — admin IPs only, plus brute-force throttle
        tcp dport 22 ip saddr @admin_ips ct state new limit rate 5/minute accept
        tcp dport 22 ct state new log prefix "nft-ssh-drop: " drop

        # 6. Web
        tcp dport { 80, 443 } ct state new accept

        # 7. Everything else: log a sample and drop
        limit rate 5/second log prefix "nft-drop: " flags all
        counter drop
    }

    chain forward {
        type filter hook forward priority 0; policy drop;
    }

    chain output {
        type filter hook output priority 0; policy accept;
    }
}
```

Validate and reload:

```bash
sudo nft -c -f /etc/nftables.conf   # check syntax, do not apply
sudo systemctl reload nftables
sudo nft list ruleset
```

## 6. Stateful rules: ct state

Connection tracking (`ct`) is what makes nftables stateful. Every packet is
classified into one of these states:

| State         | Meaning                                                  | Action                |
|---------------|----------------------------------------------------------|-----------------------|
| `new`         | First packet of a new session (e.g. TCP SYN)             | Evaluate against policy |
| `established` | Part of an existing tracked session                      | Accept without re-eval  |
| `related`     | New session logically tied to an existing one (FTP data, ICMP errors) | Accept carefully |
| `invalid`     | Packet the kernel cannot classify                        | Drop immediately      |
| `untracked`   | Explicitly bypassed `notrack`                            | Rare                  |

Without stateful rules, you would need matching rules for return traffic in
both directions — tedious and error-prone. The two lines you should never omit
in an `input` chain are:

```nft
ct state invalid drop
ct state { established, related } accept
```

Monitor the conntrack table:

```bash
sudo conntrack -L | wc -l
sudo sysctl net.netfilter.nf_conntrack_count
sudo sysctl net.netfilter.nf_conntrack_max
```

If `count` approaches `max`, new connections will be dropped. Raise `max` and
lower TCP timeouts if you operate a busy front-door.

## 7. Rate limiting

nftables supports per-rule, per-source, and per-set rate limits using `limit`
and `meter` / `ct count`.

### SSH brute-force throttle (per source IP)

```nft
table inet filter {
    set ssh_flood {
        type ipv4_addr
        size 65535
        flags dynamic, timeout
        timeout 10m
    }

    chain input {
        # ...
        tcp dport 22 ct state new add @ssh_flood { ip saddr limit rate 5/minute burst 5 packets } accept
        tcp dport 22 ct state new drop
    }
}
```

### HTTP connection cap per source

```nft
tcp dport { 80, 443 } ct count over 100 drop
tcp dport { 80, 443 } meter http_rate { ip saddr limit rate 50/second burst 100 packets } accept
tcp dport { 80, 443 } drop
```

Host-level rate limiting is a blunt instrument. For accurate per-endpoint
shaping, use Nginx `limit_req_zone` (see `ddos.md`). Firewall rate limits are
for absorbing floods before they reach userspace.

## 8. DMZ architecture

A screened subnet (DMZ) isolates public-facing services from your internal
network. Even on a single-cloud deployment, you can implement the same logic
with VPC subnets and host firewalls.

```text
                  +------------------+
 Internet ----->  |  Edge firewall   |   (cloud SG, WAF, L3/L4 filter)
                  +---------+--------+
                            |
             +--------------+--------------+
             |                             |
        +----v-----+                  +----v-----+
        |  DMZ     |                  | Private  |
        | (web,    |                  | (DB,     |
        |  reverse |                  |  worker, |
        |  proxy)  |                  |  cache)  |
        +----+-----+                  +----+-----+
             |                             |
             +-------------+---------------+
                           |
                    (internal subnet / VPC peering)
```

Rules:

- **DMZ hosts cannot talk to each other** unless explicitly required.
- **Private subnet rejects inbound from the internet entirely** — no public IP.
- **DMZ -> private is whitelist-only**: web -> app on 8080, app -> db on 3306.
- **Private -> DMZ is forbidden** (prevents db exfiltration through web tier).
- **No host in any tier allows outbound to the full internet** without a proxy
  or documented allow-list.

## 9. Hardening templates

### (a) Public web server — DMZ facing

Inbound: 22 (from bastion only), 80, 443. Outbound: DNS, NTP, package repos.

```nft
chain input {
    type filter hook input priority 0; policy drop;
    iif "lo" accept
    ct state invalid drop
    ct state { established, related } accept
    tcp dport 22 ip saddr 10.0.0.5 accept              # bastion only
    tcp dport { 80, 443 } accept
    ip protocol icmp icmp type echo-request limit rate 5/second accept
    counter drop
}
```

### (b) Database server — private subnet

Inbound: 3306 from app server IPs only. Nothing else. No internet egress
except to the package mirror during patch windows.

```nft
table inet filter {
    set app_servers {
        type ipv4_addr
        elements = { 10.0.1.11, 10.0.1.12, 10.0.1.13 }
    }

    chain input {
        type filter hook input priority 0; policy drop;
        iif "lo" accept
        ct state invalid drop
        ct state { established, related } accept
        tcp dport 22 ip saddr 10.0.0.5 accept
        tcp dport 3306 ip saddr @app_servers accept
        log prefix "db-drop: " counter drop
    }

    chain output {
        type filter hook output priority 0; policy drop;
        oif "lo" accept
        ct state { established, related } accept
        udp dport 53 accept                            # DNS
        udp dport 123 accept                           # NTP
        tcp dport { 80, 443 } ip daddr @app_servers accept
        # Package mirror allow-list applied during maintenance
    }
}
```

### (c) Application server

Inbound from web tier on 8080, outbound to database on 3306 and AI providers
on 443.

```nft
chain input {
    type filter hook input priority 0; policy drop;
    iif "lo" accept
    ct state invalid drop
    ct state { established, related } accept
    tcp dport 22 ip saddr 10.0.0.5 accept
    tcp dport 8080 ip saddr 10.0.2.0/24 accept         # web tier subnet
    counter drop
}
```

## 10. Logging

nftables logs via `nflog` (netlink) or the classic `kmsg` facility. The `log`
statement with a prefix is what you want for greppable output:

```nft
log prefix "nft-drop: " flags all
```

Logs land in:

- `/var/log/kern.log`
- `journalctl -k | grep nft-drop`

For high-volume sinks, pipe to `ulogd2`:

```bash
sudo apt install ulogd2
sudo systemctl enable --now ulogd2
```

Then use `log group N` in nft rules to route to a specific ulogd instance
writing structured JSON. This is the recommended path for shipping firewall
logs to a SIEM.

## 11. iptables -> nftables cheat sheet

| iptables                                       | nftables                                           |
|------------------------------------------------|----------------------------------------------------|
| `iptables -L -n -v`                            | `nft list ruleset`                                 |
| `iptables -A INPUT -p tcp --dport 22 -j ACCEPT`| `nft add rule inet filter input tcp dport 22 accept`|
| `iptables -P INPUT DROP`                       | `chain input { policy drop; }`                     |
| `-m state --state ESTABLISHED,RELATED`         | `ct state { established, related }`                |
| `-m limit --limit 5/min`                       | `limit rate 5/minute`                              |
| `ipset create`                                 | `set name { type ipv4_addr; ... }`                 |
| `iptables-save > rules.v4`                     | `nft list ruleset > /etc/nftables.conf`            |
| `iptables-restore < rules.v4`                  | `nft -f /etc/nftables.conf`                        |

Convert an existing iptables ruleset with `iptables-restore-translate`:

```bash
sudo iptables-save > /tmp/v4.rules
iptables-restore-translate -f /tmp/v4.rules > /tmp/v4.nft
```

Review the output carefully — the translator is mechanical and will not
idiomatically use sets, meters, or ct helpers.

## 12. Common mistakes

- **OUTPUT policy left at ACCEPT**. A compromised app can exfiltrate or join a
  botnet. Lock OUTPUT down to a whitelist, especially on database and bastion
  hosts.
- **Forgetting loopback**. `iif "lo" accept` must be the first rule in input,
  or half your services will mysteriously fail.
- **Mixing iptables and nftables on the same host**. The rules execute in
  separate chains and you will get split-brain behaviour. Pick one.
- **Not persisting rules**. `nft add rule ...` at the CLI is volatile. Write
  to `/etc/nftables.conf` and reload the service.
- **Blocking all ICMP**. Path MTU Discovery needs `destination-unreachable`
  type 3 code 4. Rate-limit instead of drop.
- **Relying on SSH rate-limit alone**. Always pair with `fail2ban`, keys-only
  auth, and ideally a bastion host.
- **No monitoring on the drop counters**. `nft list ruleset` shows counters —
  graph them so a sudden 10x jump alerts you to an attack.
- **Trusting cloud security groups as your only firewall**. They are good but
  single-layer. Always run a host firewall as defence in depth.

## 13. Cross-references

- `./waf.md` — Application-layer filtering with ModSecurity and CRS
- `./ddos.md` — Volumetric and application-flood mitigation
- `../SKILL.md` — Parent network-security skill
- `vibe-security-skill/` — Secure web application coding baseline
- `web-app-security-audit/` — Full web application security audit workflow
- `cicd-devsecops/` — Hardening the CI/CD pipeline around these hosts
