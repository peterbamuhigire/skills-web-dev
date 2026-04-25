# DDoS Defence

Practical DDoS mitigation for multi-tenant SaaS on Debian 12 / Ubuntu 24.04,
covering kernel, firewall, reverse proxy, and edge layers.

## 1. Attack taxonomy

DDoS attacks fall into three broad layers. Each needs a different defence.

| Layer | Examples                                              | Unit of damage            | Who must defend       |
|-------|-------------------------------------------------------|---------------------------|-----------------------|
| L3 (volumetric) | UDP flood, DNS/NTP/Memcached amplification, ICMP flood | Gbps of traffic           | Your upstream / edge  |
| L4 (protocol)   | SYN flood, ACK flood, RST flood, sockstress            | Packets per second, conn table | Kernel + firewall |
| L7 (application)| Slowloris, HTTP GET/POST flood, expensive queries, API abuse | Requests per second, backend CPU | Reverse proxy + app |

The cardinal rule: **you cannot absorb a 500 Gbps flood on a single VPS**.
That is what anycast edges (Cloudflare, Fastly, AWS Shield, GCP Armor) exist
for. At the origin, your job is L4 protocol hygiene and L7 application
hygiene — plus keeping the origin IP secret.

## 2. What you can defend at origin vs at the edge

| Layer                 | At origin (your VPS) | At the edge (CDN/WAF) |
|-----------------------|----------------------|-----------------------|
| Volumetric (L3)       | Limited — pipe size  | Yes (anycast absorbs) |
| Protocol (L4 SYN)     | Yes (syncookies)     | Yes                   |
| Slowloris             | Yes (timeouts)       | Yes                   |
| HTTP flood            | Yes (rate limit)     | Yes (JS challenge)    |
| Expensive queries     | Yes (app logic)      | Partial (WAF rules)   |
| DNS amplification     | No (you are victim)  | Yes                   |

## 3. Kernel sysctls for L3/L4 defence

Write to `/etc/sysctl.d/99-ddos.conf`:

```conf
# TCP SYN flood protection
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 4096
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_syn_retries = 3

# Generic connection backlog
net.core.somaxconn = 4096
net.core.netdev_max_backlog = 16384

# Reverse path filter (anti-spoof)
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# Ignore ICMP broadcast and bogus responses (Smurf defence)
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.icmp_ignore_bogus_error_responses = 1

# Rate-limit ICMP responses
net.ipv4.icmp_ratelimit = 100
net.ipv4.icmp_ratemask = 88089

# Disable source routing and redirects
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv6.conf.all.accept_redirects = 0

# Time-wait bucket, FIN timeout
net.ipv4.tcp_fin_timeout = 15
net.ipv4.tcp_max_tw_buckets = 1440000

# Log martian packets
net.ipv4.conf.all.log_martians = 1
```

Apply immediately without reboot:

```bash
sudo sysctl --system
sudo sysctl -p /etc/sysctl.d/99-ddos.conf
```

Verify:

```bash
sudo sysctl net.ipv4.tcp_syncookies net.ipv4.tcp_max_syn_backlog net.core.somaxconn
```

## 4. nftables rate limiting for DDoS

Complement the kernel sysctls with a firewall rate-limit layer.

```nft
table inet filter {
    # Dynamic set tracks offenders for 10 minutes
    set syn_offenders {
        type ipv4_addr
        size 65535
        flags dynamic, timeout
        timeout 10m
    }

    chain input {
        type filter hook input priority 0; policy drop;

        iif "lo" accept
        ct state invalid drop
        ct state { established, related } accept

        # Per-source SYN rate limit on web ports
        tcp flags syn tcp dport { 80, 443 } \
            add @syn_offenders { ip saddr limit rate over 50/second burst 100 packets } \
            log prefix "syn-flood: " drop

        # Cap concurrent connections per source to 100
        tcp dport { 80, 443 } ct count over 100 drop

        # Global new-connection rate
        tcp dport { 80, 443 } ct state new limit rate 2000/second accept

        tcp dport { 80, 443 } accept
        counter drop
    }
}
```

## 5. Nginx L7 defences

Nginx is the primary gate for HTTP-layer attacks. Three tools: timeouts,
rate limits, and connection caps.

```nginx
http {
    # Rate limit zones — one per use case
    limit_req_zone $binary_remote_addr zone=global:20m  rate=100r/s;
    limit_req_zone $binary_remote_addr zone=login:10m   rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api:10m     rate=30r/s;
    limit_conn_zone $binary_remote_addr zone=perip:10m;
    limit_conn_zone $server_name        zone=perserver:10m;

    # Slowloris defences — aggressive timeouts
    client_body_timeout    10s;
    client_header_timeout  10s;
    send_timeout           10s;
    keepalive_timeout      15s;
    keepalive_requests     100;
    reset_timedout_connection on;

    # Cap header and body sizes
    client_header_buffer_size   1k;
    large_client_header_buffers 2 4k;
    client_max_body_size        10m;

    server {
        # Global req cap per IP
        limit_req  zone=global burst=200 nodelay;
        limit_conn perip 50;
        limit_conn perserver 5000;

        location = /api/login {
            limit_req zone=login burst=5 nodelay;
            proxy_pass http://backend;
        }

        location /api/ {
            limit_req zone=api burst=60 delay=30;
            proxy_pass http://backend;
        }
    }
}
```

Reload: `sudo nginx -t && sudo systemctl reload nginx`.

Key directive notes:

- `burst=N nodelay` — allow short bursts, reject immediately beyond the burst
  instead of queuing. Use `nodelay` for APIs where latency matters.
- `delay=N` — queue up to N over the limit, reject beyond. Use for browser
  workloads where a short wait is acceptable.
- `limit_conn perip 50` — more than 50 simultaneous connections from one IP
  is almost certainly abuse.

## 6. HAProxy stick-tables (alternative or companion)

If HAProxy fronts your stack, stick-tables give fine-grained L7 tracking.

```haproxy
frontend web
    bind *:443 ssl crt /etc/haproxy/certs/
    mode http

    # Track clients by source IP for 10m, keep counters
    stick-table type ip size 1m expire 10m store conn_cur,conn_rate(10s),http_req_rate(10s),gpc0

    # Flag abusers in gpc0
    http-request track-sc0 src
    http-request deny if { sc_http_req_rate(0) gt 200 }
    http-request deny if { sc_conn_rate(0) gt 100 }
    http-request deny if { sc_conn_cur(0) gt 50 }

    # Persistent bad-actor list
    acl abuser sc_get_gpc0(0) gt 0
    http-request deny if abuser

    default_backend app
```

Monitor the table live:

```bash
echo "show table web" | sudo socat stdio /run/haproxy/admin.sock
```

## 7. Slowloris defence

Slowloris keeps thousands of connections open by sending HTTP headers one
byte at a time, exhausting worker pools. Defence:

- **`client_header_timeout` <= 10s** (Nginx) — rejects slow headers.
- **`client_body_timeout` <= 10s** — rejects slow bodies.
- **`reset_timedout_connection on`** — hard-close dead sockets.
- **`limit_conn perip <= 50`** — one host cannot hold thousands of slots.
- **Run behind Nginx / HAProxy, not bare Apache prefork**. Event-driven
  servers absorb idle connections cheaply; prefork Apache dies at hundreds.
- **Use HTTP/2 with keepalive_requests cap** — prevents a single connection
  from dominating.

## 8. Cloudflare / Fastly / AWS Shield as edge

When to engage an anycast edge:

- You can be targeted at the network layer (public-facing SaaS, community
  signup forms, news-worthy domains).
- You cannot tolerate minutes of downtime during mitigation.
- Your upstream link is smaller than plausible attack volume (most VPS = yes).

What the edge gives you:

- **Anycast absorption** — attack traffic is distributed across dozens of
  global PoPs; no single origin sees it.
- **JS challenge / Turnstile** — browsers pass silently, scripts fail.
- **"Under attack" mode** — presents an interstitial for a few seconds on
  first visit; devastating to naive HTTP floods.
- **Bot management** — heuristics on UA, JA3/JA4 fingerprint, behaviour.
- **Rate limiting rules** — configured at the edge, effective before traffic
  ever enters your pipe.

Limits and costs:

- Managed rules are partly opaque.
- Bandwidth is metered on paid tiers.
- TLS is terminated at the edge — a data sovereignty decision.
- Origin IP leaks (via DNS history, certificate transparency logs, email
  headers, misconfigured subdomains) let attackers bypass the edge.

## 9. Anycast basics and origin hiding

If you use Cloudflare or similar, your origin IP must never be publicly
reachable. Lock it down:

```bash
# Fetch and pin Cloudflare IP ranges
curl -s https://www.cloudflare.com/ips-v4 -o /etc/nftables/cf-v4.list
curl -s https://www.cloudflare.com/ips-v6 -o /etc/nftables/cf-v6.list
```

Then in nftables, only accept 443 from that set:

```nft
set cloudflare_v4 { type ipv4_addr; flags interval; elements = { ... } }
tcp dport 443 ip saddr @cloudflare_v4 accept
tcp dport 443 drop
```

Checklist for origin hiding:

- No public A/AAAA record for the origin; proxy everything through the edge.
- `mail.yourdomain.com` on a separate IP (mail servers leak origin via SPF).
- Scrub historic DNS records on a passive-DNS check.
- Use `X-Forwarded-For` or `CF-Connecting-IP` for real client IP, not
  `$remote_addr`, which will be a Cloudflare IP.
- Automate refresh of the CF IP list with a systemd timer — Cloudflare
  publishes occasional updates.

## 10. Monitoring for DDoS

If you cannot see it, you cannot respond. Minimum instrumentation:

| Signal                       | Tool                               | Healthy baseline -> alert rule |
|------------------------------|------------------------------------|--------------------------------|
| Inbound bandwidth            | `iftop -nP`, `bmon`, node_exporter | Rate of change > 5x p50 in 1m  |
| New conns / sec              | `ss -s`, conntrack                 | > 2x baseline for 30s          |
| conntrack table fill         | `/proc/sys/net/netfilter/nf_conntrack_count` | > 80% of `_max`      |
| HTTP 4xx/5xx per second      | Nginx log pipe to Prometheus       | 5xx rate > 1% sustained 1m     |
| TCP retransmits              | `ss -i`, node_exporter             | Retransmit rate > 2%           |
| Backend latency p99          | App metrics                        | > 3x baseline                  |

Node exporter on Debian:

```bash
sudo apt install prometheus-node-exporter
sudo systemctl enable --now prometheus-node-exporter
```

Live quick-look during an attack:

```bash
sudo iftop -nP -i eth0                # top talkers
sudo ss -s                            # socket summary
sudo conntrack -C                     # active connections
sudo tail -f /var/log/nginx/access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head
```

## 11. Response runbook

A ten-minute mental model when an attack starts.

1. **Detect.** Alert fires (latency, 5xx, bandwidth). Confirm from two
   independent signals before declaring incident.
2. **Identify layer.**
   - Bandwidth saturated but conn table stable -> L3 volumetric. Escalate
     to edge / upstream.
   - Conn table full, half-open sockets high -> L4 SYN flood. Check
     `syncookies` and enable `nft` per-IP SYN caps.
   - 200-series traffic, high req/s, few sources -> HTTP flood. Engage
     Nginx `limit_req`, add to block list.
   - Long-held connections, low bandwidth, workers starved -> Slowloris.
     Shorten timeouts, kill idle connections.
3. **Mitigate.** Apply the narrowest rule that stops the attack. Prefer
   rate limits over blanket bans; prefer specific IPs/subnets over whole
   ASNs.
4. **Observe.** Watch dashboards. If the attacker adapts, widen the rule.
   If mitigation causes collateral damage, narrow it.
5. **Communicate.** Post status to status page. Tell support. If payments
   or SLA-critical customers are affected, notify them directly.
6. **Escalate.** If origin pipe is saturated, contact upstream / engage
   edge provider's emergency mode.
7. **Post-mortem.** Within 48 hours write up: timeline, root cause,
   mitigation, false positives, lessons. File tickets for gaps.

## 12. Anti-patterns

- **DDoS protection as a checkbox.** "We have Cloudflare" is not a plan.
  Test your runbook. Know how to enable "under attack" mode in the dark.
- **Trusting user IP behind a proxy.** `$remote_addr` is the proxy. Use
  `CF-Connecting-IP` or `X-Forwarded-For` with `set_real_ip_from` set to
  your trusted proxy CIDRs. Otherwise rate limits key on the wrong address
  and either ban the proxy or ban nobody.
- **Alerting on raw packet count, not rate of change.** Baselines shift
  daily. Alert on deviation from moving average, not absolute thresholds.
- **Banning whole countries or ASNs as first response.** Collateral damage
  and usually ineffective. Rate-limit first, block specific sources second,
  ASN-level only as last resort.
- **Forgetting conntrack.** A full conntrack table silently drops all new
  connections — your firewall becomes the DoS. Monitor
  `nf_conntrack_count / nf_conntrack_max` and raise the ceiling before it
  saturates.
- **Running mitigation in log-only mode forever.** Log-only is for
  baselining, not production. Commit to thresholds and flip to enforce.
- **Exposing origin through mail, staging, or dev subdomains.** If anything
  on the apex domain has an A record bypassing the edge, the origin is
  public.
- **Single-node architecture for the public entrypoint.** If you care about
  DDoS survival, run at least two ingress nodes behind an upstream LB — even
  if they are both on the same provider.

## 13. Cross-references

- `./firewalls.md` — nftables baseline and stateful rules referenced here
- `./waf.md` — ModSecurity + Nginx limit_req complementing DDoS defence
- `../SKILL.md` — Parent network-security skill
- `realtime-systems/` — WebSocket and SSE systems have their own DDoS surface
- `microservices-resilience/` — Circuit breakers and bulkheads as back-pressure
- `cicd-devsecops/` — Shipping mitigation changes through a controlled pipeline
