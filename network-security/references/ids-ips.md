# Intrusion Detection and Prevention Systems

IDS/IPS patterns for self-managed Debian/Ubuntu SaaS hosts. Covers Suricata, Fail2ban, Wazuh, rule tuning, EVE JSON logs, and alert triage workflow.

## Purpose of IDS/IPS

An IDS watches traffic and logs for known-bad patterns or anomalies and raises alerts. An IPS does the same thing but actively drops or resets the offending traffic. Together, they form the second ring of defence after firewalls: firewalls decide who gets in at all, IDS/IPS decide what to do when someone who was allowed in starts behaving badly.

## IDS vs IPS

| Aspect | IDS | IPS |
|---|---|---|
| Action | Detect, log, alert | Detect and block in real time |
| Deployment | Passive (span port, af-packet capture) | Inline (bridge, nfqueue) |
| Failure mode | Fails open (traffic still flows) | Fails closed by default (traffic drops) if mis-configured |
| Latency impact | None | Small but real |
| Best for | Visibility, forensics | Active defence against known attacks |

**Network-based (NIDS/NIPS)** inspect packets on a network interface. **Host-based (HIDS)** inspect log files, file integrity, and process behaviour on a single server. A production stack usually runs both — Suricata at the edge for network-level detection, Wazuh or OSSEC on each host for file integrity and log correlation.

## Tool landscape

- **Suricata** — the primary recommendation. Multi-threaded, supports IDS and IPS modes, protocol-aware (HTTP, TLS, DNS, SMB), rich JSON logging. Active development. Use this by default.
- **Snort** — the older sibling. Single-threaded (Snort 2) or rewritten (Snort 3). Large rule ecosystem but Suricata is simpler to operate in multi-core environments.
- **Zeek (formerly Bro)** — not quite an IDS; it is a scriptable network monitor that produces rich connection, protocol, and flow logs. Pair it with Suricata for deeper forensic capability.
- **Wazuh / OSSEC** — host-based: watches file integrity (similar to Tripwire), parses syslog for patterns, performs rootkit checks, forwards alerts to a central manager. Wazuh is the actively maintained fork.
- **Fail2ban** — lightweight log-based reactive blocker. Reads log files with regex filters and temporarily bans offending IPs via nftables/iptables. Not a full IDS but very cheap and effective for brute-force scenarios.
- **Tripwire / AIDE** — classic file integrity monitors. Run from cron; compare current filesystem hashes against a signed baseline.

## Suricata installation on Debian

```bash
# Install from the official Debian repository.
sudo apt update
sudo apt install suricata suricata-update jq

# Disable the auto-start while you configure.
sudo systemctl stop suricata
```

Key config file: `/etc/suricata/suricata.yaml`. Essential tuning for a single-NIC SaaS server:

```yaml
# /etc/suricata/suricata.yaml — excerpt
vars:
  address-groups:
    HOME_NET: "[10.0.0.0/8,192.168.0.0/16]"
    EXTERNAL_NET: "!$HOME_NET"
    HTTP_SERVERS: "$HOME_NET"

af-packet:
  - interface: eth0
    threads: auto
    cluster-id: 99
    cluster-type: cluster_flow
    defrag: yes
    use-mmap: yes

outputs:
  - eve-log:
      enabled: yes
      filetype: regular
      filename: /var/log/suricata/eve.json
      types:
        - alert:
            payload: yes
            payload-printable: yes
            http: yes
            tls: yes
            metadata: yes
        - http
        - dns
        - tls
        - flow
        - stats:
            interval: 60

default-rule-path: /var/lib/suricata/rules
rule-files:
  - suricata.rules
```

Download rules and start:

```bash
sudo suricata-update                       # fetches ET Open by default
sudo suricata -T -c /etc/suricata/suricata.yaml -i eth0   # test config
sudo systemctl enable --now suricata
```

## Running modes

### Passive IDS (AF_PACKET)

Default and simplest. Suricata listens on `eth0` in promiscuous mode and generates alerts without touching traffic. Works with a single NIC and zero network reconfiguration.

### Inline IPS (nfqueue)

Suricata sits on the forwarding path via netfilter. Packets are sent to a userspace queue, Suricata inspects them and returns a verdict (accept/drop). Add to nftables:

```bash
sudo nft add rule inet filter forward counter queue num 0 bypass
```

Run Suricata with `-q 0` and enable inline rules. The `bypass` flag is critical: if Suricata crashes, traffic flows normally rather than the whole server going dark.

### AF_PACKET bridging (transparent IPS)

Two NICs bridged in software. Traffic enters eth0, Suricata inspects and forwards to eth1. No IP on either interface — completely transparent. Ideal for a dedicated sensor box in front of app servers.

## Ruleset selection

- **ET Open** — free rules from Emerging Threats (Proofpoint). Large, well-maintained, noisy out of the box. Start here. Update with `suricata-update`.
- **ET Pro** — the commercial upgrade. Faster rule delivery, more malware family coverage. Worth the subscription for regulated environments.
- **Snort Talos** — Cisco's commercial ruleset. Convert with `suricata-update` or use Snort-native.
- **Local rules** — drop custom rules into `/etc/suricata/rules/local.rules` and add to `rule-files:`. Use for protecting your specific stack (e.g. blocking known-bad user-agents hitting your admin panel).

Example custom rule to alert on any plaintext HTTP POST to an admin path:

```suricata
alert http $EXTERNAL_NET any -> $HTTP_SERVERS any ( \
    msg:"LOCAL Admin panel accessed over plaintext HTTP"; \
    flow:to_server,established; \
    http.method; content:"POST"; \
    http.uri; content:"/admin/"; \
    classtype:policy-violation; sid:1000001; rev:1;)
```

Refresh after adding rules:

```bash
sudo suricata-update
sudo kill -USR2 $(pidof suricata)    # hot reload without dropping connections
```

## Rule tuning — killing alert fatigue

Out of the box, ET Open will generate thousands of alerts per day, most of them noise. A sensor with untuned rules is worse than no sensor: engineers stop reading alerts. Tuning workflow:

1. **Baseline for a week.** Let it run. Count alerts per SID.
2. **Sort top-N noisy SIDs.**

   ```bash
   sudo jq -r 'select(.event_type=="alert") | .alert.signature_id' \
     /var/log/suricata/eve.json | sort | uniq -c | sort -rn | head -20
   ```

3. **Suppress or disable per sensor.** Edit `/etc/suricata/disable.conf`:

   ```text
   2012647
   2016149
   re:SURICATA STREAM.*
   ```

4. **Threshold noisy-but-valuable rules.** Edit `/etc/suricata/threshold.config`:

   ```text
   # Alert at most 1 time per source IP per 60 seconds for SID 2019401
   threshold gen_id 1, sig_id 2019401, type limit, track by_src, count 1, seconds 60
   ```

5. **Regenerate and reload.**

   ```bash
   sudo suricata-update
   sudo kill -USR2 $(pidof suricata)
   ```

6. **Repeat weekly** until noise is below the level an on-call engineer can actually read.

## EVE JSON log format

All Suricata output goes into a single structured JSON file, one event per line. Example alert:

```json
{
  "timestamp": "2026-04-10T10:23:17.432891+0000",
  "event_type": "alert",
  "src_ip": "203.0.113.42",
  "src_port": 54821,
  "dest_ip": "10.0.1.15",
  "dest_port": 443,
  "proto": "TCP",
  "alert": {
    "action": "allowed",
    "signature_id": 2013028,
    "rev": 6,
    "signature": "ET WEB_SERVER Possible SQL Injection UNION SELECT",
    "category": "Web Application Attack",
    "severity": 1
  },
  "http": {
    "hostname": "app.example.com",
    "url": "/search?q=union+select",
    "http_user_agent": "sqlmap/1.7.12"
  }
}
```

Query quickly with `jq`:

```bash
# Recent alerts grouped by signature
jq -r 'select(.event_type=="alert") | .alert.signature' /var/log/suricata/eve.json \
  | sort | uniq -c | sort -rn

# DNS queries for suspicious TLDs
jq -r 'select(.event_type=="dns" and .dns.rrname | endswith(".xyz"))' \
  /var/log/suricata/eve.json

# TLS handshakes with expired certs
jq 'select(.event_type=="tls" and .tls.notafter != null)' /var/log/suricata/eve.json
```

## Log shipping

A single server's `eve.json` is useful; a fleet-wide aggregated view is essential. Ship to Loki, OpenSearch, or SigNoz.

**Filebeat → Elasticsearch/OpenSearch**:

```yaml
# /etc/filebeat/filebeat.yml
filebeat.inputs:
  - type: filestream
    id: suricata-eve
    paths:
      - /var/log/suricata/eve.json
    parsers:
      - ndjson:
          keys_under_root: true
          expand_keys: true

output.elasticsearch:
  hosts: ["https://logs.internal:9200"]
  username: "suricata-writer"
  password: "${FILEBEAT_PASSWORD}"
```

**Vector → Loki**:

```toml
[sources.suricata]
type = "file"
include = ["/var/log/suricata/eve.json"]

[transforms.parse]
type = "remap"
inputs = ["suricata"]
source = ". = parse_json!(.message)"

[sinks.loki]
type = "loki"
inputs = ["parse"]
endpoint = "https://loki.internal:3100"
labels = {job = "suricata", host = "{{ host }}"}
```

## Sample alert scenarios

- **SQL injection hit** — `sid:2013028 "Possible SQL Injection UNION SELECT"` fires on POST to `/search`. Action: check app logs for the same timestamp; if the WAF missed it, tighten input validation.
- **DNS tunnelling** — high-entropy subdomain queries (e.g. `a7f9d2...hex.example.xyz`). ET Open rules catch most DNS covert channels. Action: block the parent domain at the resolver.
- **TLS with expired or self-signed cert** — `tls.notafter` in the past on an outbound connection. Often malware phoning home via a cheap C2.
- **Outbound to known C2** — ET Open includes IP reputation lists. Any hit needs immediate investigation; assume the host is compromised until proven otherwise.
- **Port scan from internal host** — internal IP hitting dozens of ports on a peer. Probably a legitimate engineer, but you should know — whitelist their jumpbox IP, not the whole internal range.

## Fail2ban as a lightweight IDS

Fail2ban is not a signature IDS, but for log-based brute-force and known-bad-actor blocking it is unbeatable on resource budget. Ships with Debian.

```bash
sudo apt install fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
```

Enable jails for services you run. Example `/etc/fail2ban/jail.d/saas.local`:

```ini
[DEFAULT]
bantime  = 1h
findtime = 10m
maxretry = 5
backend  = systemd
banaction = nftables-multiport

[sshd]
enabled = true

[nginx-http-auth]
enabled = true
port    = http,https
logpath = /var/log/nginx/error.log

[postfix]
enabled = true

[recidive]
enabled  = true
bantime  = 1w
findtime = 1d
maxretry = 5
```

Custom filter example for a PHP login endpoint — `/etc/fail2ban/filter.d/saas-login.conf`:

```ini
[Definition]
failregex = ^<HOST> -.*"POST /login.*" 401
ignoreregex =
```

And the jail:

```ini
[saas-login]
enabled = true
filter  = saas-login
logpath = /var/log/nginx/access.log
port    = http,https
maxretry = 10
findtime = 5m
bantime  = 1h
```

Control and inspect:

```bash
sudo fail2ban-client status
sudo fail2ban-client status sshd
sudo fail2ban-client set sshd unbanip 203.0.113.42
```

## Wazuh / OSSEC briefly

Wazuh is a HIDS platform — agents run on each server, the manager collects events centrally. It complements Suricata by watching what the network sensor cannot: file changes, user activity, rootkits, log patterns not visible on the wire (especially after TLS decryption).

Deploy Wazuh when you need:

- **File integrity monitoring** — detect changes to `/etc/`, web roots, or config files.
- **Log correlation** — rules that fire when multiple small events align (e.g. failed login + new cron job + outbound connection).
- **Compliance reporting** — PCI, HIPAA, or ISO 27001 control mapping.
- **Rootkit and anomaly detection** — agent-level checks.

Install on Debian from the Wazuh APT repo. Keep the manager on its own host; do not colocate with the servers it monitors.

## Alert triage workflow

Write this down as a runbook. Rehearse it.

**Severity tiers:**

1. **Critical (red)** — confirmed compromise, active data exfiltration, C2 beacon, ransomware indicator. On-call pager within 5 minutes.
2. **High (orange)** — targeted exploit attempt that may have succeeded (SQLi with unusual response size, new admin user, unexpected SSH login). Investigate within 30 minutes.
3. **Medium (yellow)** — probing, failed exploit, policy violations. Reviewed daily.
4. **Low (blue)** — noise candidates. Reviewed weekly to decide whether to suppress.

**Response playbook for a high-severity alert:**

1. **Acknowledge** — claim the alert so a second engineer does not double-respond.
2. **Triage** — correlate with app logs, auth logs, and flow logs. Is it a true positive?
3. **Contain** — block the source IP at the firewall; if compromise confirmed, isolate the host from the network (drop all egress except to the forensics VLAN).
4. **Preserve** — `sudo dd` a memory snapshot, copy `/var/log` to a write-only bucket.
5. **Eradicate** — rebuild from a known-good image; never "clean in place" a compromised host.
6. **Recover** — restore service with rotated credentials.
7. **Post-mortem** — blameless, document within 48 hours, add detection rules for the specific TTP you saw.

## Anti-patterns

- **Deploying IDS without tuning.** Alert fatigue is real; untuned Suricata will generate enough noise that real alerts get missed within a week.
- **IPS without logging.** Drops without visibility mean you cannot debug when legitimate traffic gets blocked — and it will.
- **Blocking silently.** Always log what was dropped, with enough context to reproduce.
- **Ignoring low-severity alerts indefinitely.** Low-sev accumulates patterns; a sudden spike often precedes a high-sev incident.
- **Blocking internal scanning engineers.** Whitelist pentest and vuln-scan sources or your own security team becomes the noisiest attacker.
- **Single-host IDS with local-only logs.** One `rm -rf` from a successful attacker erases the only evidence. Ship logs off-box always.
- **Shared secret passwords for rule updates or log shipping.** Use per-host tokens and rotate.
- **Tripwire without regular baseline updates.** A baseline that never changes is a baseline that goes stale, and engineers start ignoring every alert as "probably legitimate".

## Cross-references

- `references/firewall-fundamentals.md` — the first-ring defence that feeds packets to Suricata
- `references/ssh-bastion.md` — Fail2ban configuration for SSH
- `references/zero-trust.md` — why network-level IDS still matters even with mTLS everywhere
- `SKILL.md` — network-security skill overview
- `linux-security-hardening` skill — auditd and file integrity on the host
- `cicd-devsecops` skill — container image scanning and supply-chain detection
