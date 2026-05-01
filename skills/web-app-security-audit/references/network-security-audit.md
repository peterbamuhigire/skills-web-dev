# Network-Layer Security Audit

Audit-focused reference for the network perimeter and remote-access plane. Use alongside `network-security-layer.md` (which covers operate/build detail). This document is for the auditor: what to verify, what evidence to collect, and how to rate findings.

Stack assumption: Debian/Ubuntu VPS, self-host preferred (Nginx + ModSecurity or Coraza + OWASP CRS), Vault for secrets and PKI, optional managed WAF (Cloudflare, AWS WAF). Out of scope: service mesh (Istio/Linkerd), DDoS deep-dive beyond WAF rate-limit basics, cloud procurement comparisons.

## §N1 Host firewall policy on Debian/Ubuntu

### Toolchain decision

| Tool | When to use | Notes |
|------|-------------|-------|
| ufw | Single host, simple ruleset, ops team comfortable with high-level abstraction | Front-end to iptables/nftables; default-deny in minutes |
| iptables | Legacy systems, existing rule corpus, kernels without nftables | Being superseded; migrate with `iptables-translate` |
| nftables | New deployments on modern Debian/Ubuntu | Netfilter project's current direction; declarative, atomic rule sets |

nftables structure: a `table` is a container of chains; a `chain` is a container of rules; a `rule` is an action configured within a chain.

### Default-deny inbound nftables example

```nft
table firewall {
  chain incoming {
    type filter hook input priority 0; policy drop;

    # established/related connections
    ct state established,related accept

    # loopback interface
    iifname lo accept

    # icmp
    icmp type echo-request accept

    # open tcp ports: sshd (22), httpd (80)
    tcp dport { ssh, http } accept
  }
}
```

SaaS web tier extension: add `tcp dport https accept`; rate-limit SSH with `tcp dport ssh ct state new limit rate 5/minute accept`; deny everything else (implicit via `policy drop`).

### Egress filtering

Application servers should not reach arbitrary internet destinations. Allow-list pattern: package mirrors, DNS, NTP, the egress proxy or API gateway, the metrics endpoint. Deny everything else. This contains lateral movement after compromise.

### Audit checks

```
Inbound default policy           → CRITICAL if not DROP/deny
SSH exposed without rate-limit   → HIGH
Database/admin ports public      → CRITICAL (must be VPN-only or bound to lo)
No egress filter                 → MEDIUM (HIGH for PCI/regulated workloads)
Rule export not in source control → MEDIUM (cannot prove configuration)
Drift between declared rules and live rules → HIGH
```

## §N2 Web Application Firewall (WAF)

### Managed vs self-hosted

| Concern | Managed (AWS WAF, Cloudflare) | Self-hosted (ModSecurity / Coraza + CRS) |
|---------|-------------------------------|------------------------------------------|
| Time to first rule | Minutes | Hours to days |
| Rule update cadence | Vendor-managed | Pull from coreruleset releases |
| False-positive ownership | Shared | You own every false positive |
| Location | Edge / CDN | At your reverse proxy (Nginx + module) |
| Cost model | Per-request / WCU | Compute + ops time |

Recommendation in 2026: Coraza for new self-hosted deployments (Go, actively maintained); ModSecurity v3 still supported for existing Nginx fleets.

### OWASP Core Rule Set

CRS is a free, open-source rule collection that works with ModSecurity-compatible WAFs. It targets generic attack detection — including OWASP Top Ten coverage — with a stated goal of minimum false positives. Common rule families (verify against the actual `rules/` directory in the coreruleset repo when authoring per-deployment exclusions): SQL injection, XSS, RCE, LFI/RFI, scanner detection, session fixation, PHP attacks, Java attacks, generic protocol violation.

### Tuning loop

1. Deploy CRS at paranoia level 1 in detection-only mode.
2. Replay representative traffic; collect false positives.
3. Write rule exclusions targeting specific URI patterns and parameters, not blanket `SecRuleRemoveById` for whole categories.
4. Promote to blocking mode once false-positive rate is under the agreed threshold (commonly < 0.1 percent of legitimate requests).
5. Re-tune on every CRS release.

### AWS WAF specifics

AWS WAF monitors HTTP(S) requests forwarded to protected resources. It attaches to CloudFront, API Gateway REST APIs, Application Load Balancers, AppSync GraphQL APIs, Cognito user pools, App Runner services, Verified Access, and Amplify. Web ACLs and rule groups are the organising primitives. Confirm the current managed rule-group inventory (Core rule set, Known bad inputs, SQL database, Linux operating system, etc.) from AWS docs before sign-off.

### Audit checks

```
WAF deployed in blocking mode at edge or reverse proxy → HIGH if missing
CRS version pinned and upgrade cadence documented      → MEDIUM if missing
Paranoia level set deliberately (not default-only)     → LOW
False-positive log reviewed in last 30 days            → MEDIUM if stale
Blanket disables of whole rule categories              → HIGH (audit evidence of compensating control)
Rate-limit rules on auth and password-reset endpoints  → HIGH if missing
```

## §N3 Zero-trust architecture (NIST SP 800-207)

NIST SP 800-207 (Rose, Borchert, Mitchell, Connelly, August 2020) defines zero trust as "an evolving set of cybersecurity paradigms that move defenses from static, network-based perimeters to focus on users, assets, and resources." The central tenet: zero trust assumes there is no implicit trust granted to assets or user accounts based solely on physical or network location, or asset ownership. Authentication and authorization (subject and device) are discrete functions performed before a session to an enterprise resource is established.

The seven foundational tenets are enumerated in §2.1 of SP 800-207. Auditors must read §2.1 directly and quote it; do not paraphrase from memory.

### Concrete controls mapped to ZT principles

| Principle | Control |
|-----------|---------|
| No implicit network-based trust | mTLS between every internal service |
| Per-session authentication | Identity-aware proxy in front of every internal app (Cloudflare Access, Pomerium, Tailscale serve) |
| Continuous evaluation | Short-lived certificates from SPIFFE/SPIRE; device-posture checks via the IdP |
| Encrypt all comms | TLS at the edge, mTLS service-to-service, WireGuard for the management plane |

### Service identity

SPIFFE (Secure Production Identity Framework For Everyone) and SPIRE (its reference runtime) issue short-lived SVIDs to workloads — typically X.509 certificates or JWT-SVIDs — eliminating long-lived service credentials.

### Audit checks

```
Internal service-to-service traffic in plaintext        → HIGH
Long-lived service account credentials in env files     → HIGH (rotate to SPIFFE/SPIRE or short-lived tokens)
Internal apps reachable on the corporate LAN without identity check → CRITICAL (perimeter-based trust)
No device-posture signal in IdP                         → MEDIUM
"VPN means trusted" assumption documented anywhere      → HIGH (anti-pattern)
```

## §N4 VPN and remote access

WireGuard is the recommended default: small, fast, modern, audited. Cryptographic primitives: Noise protocol framework, Curve25519, ChaCha20, Poly1305, BLAKE2, SipHash24, HKDF.

Key-exchange model: peers exchange public keys (like SSH keys); the rest is handled transparently. The WireGuard project explicitly states key distribution and pushed configurations are out of scope of WireGuard itself — the operator must solve this. Typical solutions: Vault PKI for short-lived peer keys, or Ansible config-management push that rotates `[Peer]` blocks on a schedule.

### Topology decision

| Topology | When |
|----------|------|
| Hub-and-spoke | Few sites, central egress, simple audit |
| Full-mesh (Tailscale, Netbird, Headscale on WireGuard) | Many ops endpoints, latency-sensitive |
| Bastion host (SSH only) | Smallest surface; audit-trail limited to auditd / sshd logs |

### Identity binding

Every VPN session must be associated with an identity, not just a static peer key. Either front WireGuard with an identity-aware proxy, or ingest WireGuard handshake events into the SIEM and correlate with the IdP.

### Audit checks

```
Static long-lived WireGuard peer keys with no rotation → HIGH (target ≤ quarterly rotation, or short-lived from Vault PKI)
No mapping from peer key to human identity              → HIGH
VPN audit log retention < 1 year (or contractual minimum) → MEDIUM/HIGH depending on regime
Bastion without session recording                       → MEDIUM
SSH password auth still permitted on bastion           → HIGH
Shared admin VPN key used by multiple operators        → CRITICAL
```

## §N5 Auditor evidence checklist

The auditor must verify, with evidence, that:

- Default-deny inbound is set on every public host; the rule export is attached to the audit report.
- An egress filter is present, with the allow-list documented in source control.
- A WAF is deployed in blocking mode at the edge OR ModSecurity/Coraza + CRS sits at the reverse proxy; CRS version is pinned and the upgrade cadence is documented.
- The WAF false-positive log has been reviewed in the last 30 days.
- mTLS is in place between any two services that cross a host boundary, OR an explicit accepted-risk record exists.
- All ops access goes through an identity-aware proxy or a bastion that logs every session.
- WireGuard peer keys rotate at least quarterly OR are issued short-lived from a PKI.
- An audit log records who connected to the VPN, when, and from where; retention is at least one year (or the contractual minimum, whichever is longer).

## References

Tier 1 (canonical):

- Zero Trust Architecture — Rose, Borchert, Mitchell, Connelly. NIST SP 800-207, August 2020. csrc.nist.gov/publications/detail/sp/800-207/final
- nftables wiki — Quick Reference. wiki.nftables.org
- WireGuard project home and whitepaper — wireguard.com
- AWS WAF Developer Guide — docs.aws.amazon.com/waf/latest/developerguide/
- OWASP Core Rule Set — coreruleset.org/docs and github.com/coreruleset/coreruleset

Tier 2 (supporting):

- Cloudflare WAF — developers.cloudflare.com/waf
- ModSecurity — github.com/SpiderLabs/ModSecurity
- Coraza — github.com/corazawaf/coraza
- SPIFFE / SPIRE — spiffe.io
- Debian/Ubuntu manual pages: `man ufw`, `man iptables`, `man nft`

Tier 3 (supplementary):

- OWASP ASVS — owasp.org/www-project-application-security-verification-standard
- OWASP Top Ten — owasp.org
- NIST SP 800-57 — key management lifecycle (for VPN key-rotation cadence justification)
