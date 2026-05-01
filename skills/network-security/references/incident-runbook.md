# Network Incident Runbook

Step-by-step response procedures for five common network security incidents on
a self-managed Debian/Ubuntu VPS hosting multi-tenant SaaS.

## General response framework

Every incident flows through the same five phases. Do not skip phases under
pressure; shortcuts cost evidence and extend dwell time.

1. **Detect.** Confirm the signal is a real incident, not a false positive.
2. **Contain.** Stop the bleeding without destroying evidence.
3. **Eradicate.** Remove attacker access and the root cause.
4. **Recover.** Restore service on known-clean infrastructure.
5. **Lessons learned.** Post-incident review within five business days.

## Evidence preservation

Do **not** reboot the host as a first action. A reboot destroys memory-resident
artefacts that are often the only record of how the attacker moved.

Capture in this order:

```bash
# 1. Memory (live) - use avml or lime
sudo avml /mnt/evidence/$(hostname)-$(date +%s).mem

# 2. Volatile state
sudo ss -tupn > /mnt/evidence/sockets.txt
sudo ps auxfww > /mnt/evidence/processes.txt
sudo lsof -n > /mnt/evidence/lsof.txt
sudo iptables-save > /mnt/evidence/iptables.txt
sudo nft list ruleset > /mnt/evidence/nftables.txt

# 3. Logs (archive, don't edit in place)
sudo tar czf /mnt/evidence/logs.tgz /var/log

# 4. Disk image (offline, after power down or snapshot)
```

Record a chain-of-custody note: who collected what, when, SHA256 of each file,
where it is stored, and which incident ticket it belongs to. Store evidence on
a separate volume, preferably encrypted.

## Runbook 1: SSH brute-force in progress

**Detect**

```bash
sudo journalctl -u ssh -f | grep -i 'failed\|invalid'
sudo fail2ban-client status sshd
sudo lastb | head -n 50
```

Look for a high rate of failed logins from one or a small set of IPs, or a slow
distributed attack across many IPs (low-and-slow credential stuffing).

**Contain**

```bash
# Ensure a blacklist set exists, then add the attacker
sudo nft add set inet filter blacklist '{ type ipv4_addr; flags interval; }'  2>/dev/null
sudo nft add rule  inet filter input ip saddr @blacklist drop                 2>/dev/null
sudo nft add element inet filter blacklist '{ 203.0.113.42 }'

# Tighten Fail2ban temporarily
sudo sed -i 's/^findtime.*/findtime = 60/'  /etc/fail2ban/jail.local
sudo sed -i 's/^bantime.*/bantime = 86400/' /etc/fail2ban/jail.local
sudo systemctl reload fail2ban
```

**Eradicate and verify**

```bash
# Confirm no successful login from the attacker window
sudo grep 'Accepted' /var/log/auth.log | awk '{print $1,$2,$3,$9,$11}'
# Check for unexpected authorized_keys
sudo find /home /root -name authorized_keys -exec ls -l {} \;
```

If a login succeeded, assume full host compromise and jump to Runbook 5. Rotate
any SSH keys that were present on the attacker's source list. File an abuse
report with the origin ISP using WHOIS contact.

## Runbook 2: Suspected data exfiltration

**Detect**

```bash
sudo ss -tupn | grep -v 127.0.0.1
sudo iftop -nNP                 # live top-talkers
sudo journalctl -u suricata | grep -i 'exfil\|tunnel'
```

Signals: an application host opening long-running outbound TCP to an unusual
destination, a steep rise in outbound bytes, DNS queries to a single parent
zone with high-entropy labels.

**Contain without tipping off the attacker**

```bash
# Capture a packet sample first (for forensics)
sudo tcpdump -i eth0 -w /mnt/evidence/exfil.pcap host 198.51.100.77 &
sleep 120
sudo pkill -f 'tcpdump.*exfil.pcap'

# Block the destination at the edge
sudo nft add element inet filter blackhole '{ 198.51.100.77 }'
```

If the host is confirmed compromised, isolate it entirely. Prefer removing the
WireGuard peer or revoking the public SG rule rather than `ip link set eth0
down`, because hard-downing the interface can lose the console.

**Preserve and investigate**

```bash
sudo avml /mnt/evidence/$(hostname).mem
sudo tar czf /mnt/evidence/logs.tgz /var/log
```

Enumerate data that left the host: `ausearch -f /var/lib/app` for reads,
`find / -newermt '2 hours ago' -type f` for recently touched files. Notify
legal and the DPO; data breach notification timers start now.

## Runbook 3: DDoS in progress

**Detect and classify**

```bash
sudo bmon -p eth0                    # interface pps/bps
sudo iftop -n                        # top talkers
sudo nstat -a | grep -i 'synrecv\|drop'
```

Classify before acting:

- **Volumetric**: interface saturated, many source IPs, UDP/amplified.
- **SYN flood**: high SYN_RECV count, few payloads.
- **L7**: normal bandwidth but nginx workers exhausted, many 200/429 responses.

**Contain**

```bash
# SYN flood sysctl tuning
sudo sysctl -w net.ipv4.tcp_syncookies=1
sudo sysctl -w net.ipv4.tcp_max_syn_backlog=8192
sudo sysctl -w net.core.somaxconn=8192

# nginx: tighten rate limiting (reload, don't restart)
sudo sed -i 's/rate=100r\/s/rate=20r\/s/' /etc/nginx/conf.d/ratelimit.conf
sudo nginx -s reload
```

For volumetric attacks on an undersized uplink, the only effective mitigation
is upstream: enable Cloudflare "under attack" mode, or request the VPS provider
null-route the attack sources. Document whom you called and when.

**Post-incident**

Build a timeline from NetFlow/iftop/nginx logs. Capacity-plan headroom so the
next attack of the same size does not impact users.

## Runbook 4: Certificate compromise

**Detect**

Triggers include: a private key leaked in a repo or backup, a suspected HSM/KMS
breach, or a CT log entry for a cert you did not request.

**Contain and rotate**

```bash
# Revoke via Let's Encrypt
sudo certbot revoke \
  --cert-path /etc/letsencrypt/live/example.com/cert.pem \
  --reason keyCompromise

# Reissue with a fresh key
sudo certbot certonly --nginx -d example.com --force-renewal \
  --key-type ecdsa --elliptic-curve secp384r1
sudo nginx -s reload
```

Update pinned fingerprints in mobile apps, CDN configuration, and any service
that pins certificates. Flush intermediate caches if OCSP stapling is enabled.

**Eradicate exposure source**

Audit how the key leaked:

```bash
# Was the key committed anywhere?
git log --all --full-history -- '*privkey*' '*.key'
# Are keys in backups unencrypted?
sudo find /var/backups -name '*.key' -o -name 'privkey*'
```

Remove from git history with `git filter-repo`, rotate GPG-encrypt backups, and
rotate any secrets that rode over TLS sessions signed with the compromised key
(session tokens, API credentials in POST bodies).

## Runbook 5: Lateral movement detected

**Detect**

Signals: auditd reports a service account executing a shell, Wazuh flags an
unexpected SSH session between internal hosts, or unusual east-west traffic.

```bash
sudo ausearch -k lateral -ts recent
sudo wazuh-logtest
sudo journalctl | grep -i 'sudo.*COMMAND\|ssh.*Accepted'
```

**Contain**

```bash
# Isolate compromised host (WireGuard peer revoke)
sudo wg set wg0 peer <PUBKEY> remove
sudo systemctl restart wg-quick@wg0

# Or block at the central nftables gateway
sudo nft add element inet filter quarantine '{ 10.0.2.17 }'
```

**Eradicate**

Assume all secrets that lived on the compromised host are burnt. Rotate:

- Service-account API keys that host carried.
- Database users the host used.
- Internal mTLS client cert for that host.
- Any OAuth refresh tokens cached on the host.

Review audit logs for **what** the attacker touched, not just how they got in.
For every service reached from the compromised host, check data access logs.

**Recover**

Do not attempt to "clean" the host. Rebuild it from a known-good base image
with current patches, restore application state from a backup taken **before**
first-known-bad, and reintroduce to the mesh only after integrity verification.

## Common tools reference

| Tool | Purpose | Example |
|---|---|---|
| `tcpdump` | Packet capture | `sudo tcpdump -i eth0 -w evidence.pcap host 1.2.3.4` |
| `tshark` | CLI packet analysis | `sudo tshark -r evidence.pcap -Y 'http.request'` |
| `ss` | Socket state | `sudo ss -tupn state established` |
| `iftop` | Top talkers, live | `sudo iftop -nNP -i eth0` |
| `bmon` | Bandwidth monitor | `sudo bmon -p eth0` |
| `lsof` | Open files and sockets | `sudo lsof -iTCP -sTCP:ESTABLISHED` |
| `strace` | Live syscall trace | `sudo strace -p <pid> -e trace=network` |
| `auditd` | Kernel audit events | `sudo ausearch -k exec -ts today` |
| `journalctl` | Systemd journal | `sudo journalctl -u nginx --since '1 hour ago'` |
| `fail2ban-client` | Jail status and bans | `sudo fail2ban-client status sshd` |

## Post-incident report template

Every incident produces a written report within five business days, structured:

1. **Timeline.** UTC-timestamped narrative from detection to closure.
2. **Impact.** Affected tenants, data types, user-facing symptoms, SLA breach.
3. **Root cause.** The single condition that, if absent, would have prevented
   the incident. Not "human error" on its own.
4. **Containment actions.** What was done during the incident, and when.
5. **Permanent fix.** The code or configuration change that closes the gap,
   with a ticket and an owner.
6. **Prevention.** Detection and process improvements so an attack of the same
   shape is caught earlier next time. Update `audit-checklist.md` if the gap
   was not previously covered.

## Cross-references

- `firewall-strategy.md` for the nftables sets and rules referenced above.
- `ddos-protection.md` for sustained DDoS mitigation beyond acute response.
- `ids-logging.md` for Suricata, Wazuh, and journald-remote configuration.
- `tls-cert-management.md` for cert revocation and rotation detail.
- `zero-trust.md` for mTLS posture that makes lateral movement detectable.
- `audit-checklist.md` for the items whose absence enabled each runbook.
