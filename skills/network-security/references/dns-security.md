# DNS Security

Hardening DNS for self-managed Debian/Ubuntu SaaS: authoritative zone signing,
resolver hygiene, amplification defence, and exfiltration detection.

## DNS attack surface

DNS is frequently treated as "plumbing" and forgotten, yet it is one of the
richest attack surfaces on a public server.

| Attack | What happens | Impact |
|---|---|---|
| Cache poisoning | Attacker injects forged records into a recursive resolver | Users routed to attacker sites |
| Spoofing | Off-path forgery of responses (Kaminsky-class) | Same as above, no compromise needed |
| Amplification DDoS | Small spoofed query elicits large response toward victim | Bandwidth flood of a third party |
| Reflection | Victim's IP used as source of queries | Victim sees unsolicited responses |
| Subdomain takeover | Dangling CNAME points to a deleted cloud asset | Attacker claims the asset, serves content on your domain |
| DNS tunneling | Data encoded in subdomain labels or TXT answers | Covert exfiltration past egress filters |
| NXDOMAIN flood | Random-label queries fill cache and hammer authoritative | Resolver or upstream exhaustion |

## DNSSEC basics

DNSSEC adds an authentication chain so that resolvers can verify responses were
produced by the zone owner and were not tampered with in flight.

- **KSK (Key Signing Key)** signs the zone's DNSKEY record set. Long-lived.
- **ZSK (Zone Signing Key)** signs every other RRset in the zone. Rotated more often.
- **RRSIG** records hold signatures for every signed RRset.
- **DS (Delegation Signer)** record is published in the **parent zone** and pins the
  KSK by hash. This is how the chain of trust walks from the root down.
- **NSEC / NSEC3** prove the non-existence of a name without leaking the full zone.

Chain of trust: `root DS -> TLD DS -> your zone KSK -> your zone ZSK -> RRsets`.

## DNSSEC signing with BIND on Debian/Ubuntu

```bash
sudo apt install bind9 bind9utils dnsutils
sudo mkdir -p /etc/bind/keys && cd /etc/bind/keys
# KSK (flag 257) and ZSK (flag 256)
sudo dnssec-keygen -a ECDSAP256SHA256 -f KSK -n ZONE example.com
sudo dnssec-keygen -a ECDSAP256SHA256        -n ZONE example.com
sudo chown -R bind:bind /etc/bind/keys
```

In `/etc/bind/named.conf.options` enable inline signing globally or per zone:

```text
options {
    dnssec-validation auto;
};
```

In `/etc/bind/named.conf.local`:

```text
zone "example.com" {
    type master;
    file "/var/lib/bind/db.example.com.signed";
    key-directory "/etc/bind/keys";
    inline-signing yes;
    auto-dnssec maintain;
    allow-transfer { none; };
};
```

`auto-dnssec maintain` tells BIND to re-sign the zone on changes and to keep
signatures fresh without operator intervention. Inspect signatures with:

```bash
sudo rndc signing -list example.com
sudo dig @127.0.0.1 example.com DNSKEY +multiline
```

## DNSSEC with Knot DNS (lighter alternative)

Knot DNS has first-class automatic signing and is often lighter on small VPS.

```bash
sudo apt install knot knot-dnsutils
sudo knotc conf-begin
sudo knotc conf-set 'policy[default].algorithm' ecdsap256sha256
sudo knotc conf-set 'policy[default].ksk-size' 256
sudo knotc conf-set 'zone[example.com].dnssec-signing' on
sudo knotc conf-commit
sudo keymgr example.com generate algorithm=ecdsap256sha256 ksk=yes
```

## Signing considerations

- Export the DS record and submit it to your **domain registrar**, not the hosting
  provider. Until the DS is published at the parent, DNSSEC is unvalidated.
- Monitor signature expiry: a lapsed RRSIG blackholes the whole zone.
- Roll ZSK routinely (quarterly is sane); KSK rolls are rarer and require a DS swap.
- Test externally: `dig +dnssec example.com SOA`, <https://dnsviz.net>, or
  Verisign's DNSSEC analyzer.

## DNS over HTTPS (DoH)

DoH encrypts stub-to-resolver queries over HTTPS/443 so on-path observers cannot
see or mutate them. For a self-hosted resolver, `dnsdist` exposes DoH cleanly:

```bash
sudo apt install dnsdist
# /etc/dnsdist/dnsdist.conf
addDOHLocal("0.0.0.0:443", "/etc/letsencrypt/live/dns.example.com/fullchain.pem",
            "/etc/letsencrypt/live/dns.example.com/privkey.pem", { "/dns-query" })
newServer({ address = "127.0.0.1:5353" })  -- unbound behind it
```

`cloudflared` is another option when you want a managed upstream.

## DNS over TLS (DoT)

DoT uses port 853 with dedicated TLS. Use `unbound` as the server side:

```text
# /etc/unbound/unbound.conf.d/dot.conf
server:
    interface: 0.0.0.0@853
    tls-service-key: "/etc/letsencrypt/live/dns.example.com/privkey.pem"
    tls-service-pem: "/etc/letsencrypt/live/dns.example.com/fullchain.pem"
    tls-port: 853
```

On Debian clients, `stubby` provides a local stub that speaks DoT upstream and
exposes plain DNS on 127.0.0.1:53 to the rest of the box.

## Authoritative vs recursive: keep them apart

Never run an authoritative server that also answers recursion for the public.
This combination is a classic amplifier. For a SaaS VPS:

- Authoritative: BIND or Knot, **recursion disabled**, bound to public IP.
- Recursive: unbound, bound to `127.0.0.1` or a private VLAN only.

```text
# BIND authoritative hardening
options {
    recursion no;
    allow-query { any; };
    allow-recursion { none; };
    version "hidden";
    minimal-responses yes;
};
```

## Rate limiting (RRL)

Response Rate Limiting caps identical responses per source and shuts down
amplification reflection abuse. BIND supports it natively:

```text
options {
    rate-limit {
        responses-per-second 10;
        window 5;
        slip 2;
        qps-scale 250;
        exempt-clients { 10.0.0.0/8; };
    };
};
```

## Split-horizon DNS

Different answers for internal and external clients. Useful for exposing a short
external name while letting internal services talk to the private interface.

```text
view "internal" {
    match-clients { 10.0.0.0/8; 127.0.0.1; };
    zone "example.com" { type master; file "/etc/bind/db.example.com.internal"; };
};
view "external" {
    match-clients { any; };
    recursion no;
    zone "example.com" { type master; file "/etc/bind/db.example.com.external"; };
};
```

## CAA records

A CAA record tells CAs which issuers may sign certs for your domain. This
contains cert-issuance abuse even if someone gains control of a DNS panel.

```text
example.com. IN CAA 0 issue "letsencrypt.org"
example.com. IN CAA 0 iodef "mailto:security@example.com"
```

Verify with `dig example.com CAA`.

## Subdomain takeover prevention

Dangling CNAMEs pointing to decommissioned cloud resources (S3 buckets, Heroku
apps, Azure sites, GitHub Pages) are routinely claimed by attackers.

- Audit quarterly: `dig +short CNAME sub.example.com` and verify the target resolves.
- Remove or repoint any CNAME whose target returns NXDOMAIN or an error page.
- Keep a central inventory of external services per subdomain.
- Tools: `subjack`, `dnsReaper`, or a cron script that greps `dig` output against
  a whitelist.

## DNS as exfiltration channel

Malware encodes stolen data into subdomain labels or TXT record queries and ships
it out through a compromised DNS path. Signals that indicate tunneling:

- High query volume to a single parent zone from one host.
- Long, high-entropy subdomain labels that do not look human.
- Unusually large TXT responses.
- Clients querying zones that no legitimate workload uses.

Detect with Suricata rules (`dns.query` length/entropy), Zeek's `dns.log`, or by
aggregating query logs from the local unbound into a SIEM. Block at egress by
forcing all DNS through the local resolver and dropping port 53 outbound from
anything else:

```bash
sudo nft add rule inet filter output meta skuid != unbound udp dport 53 drop
```

## Anti-patterns

- Running a public open recursive resolver.
- Authoritative and recursive roles on the same daemon instance.
- DNSSEC enabled in the zone but no DS record at the parent.
- No alert when RRSIG TTL drops below 48 hours.
- Dangling CNAMEs to cloud services nobody remembers deploying.
- Allowing arbitrary outbound UDP/53 from application servers.
- Logging DNS queries to disk without rotation (disk fills, service dies).

## Cross-references

- `firewall-strategy.md` for nftables egress rules that box DNS in.
- `network-segmentation.md` for where to place authoritative vs recursive.
- `ids-logging.md` for Suricata/Zeek DNS rules and centralised query logs.
- `zero-trust.md` for mTLS alternatives that remove DNS from the trust path.
- `audit-checklist.md` for DNS items in the server review.
