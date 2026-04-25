# VPN Patterns for Self-Managed Debian/Ubuntu SaaS

Remote admin access, site-to-site interconnect, and private service mesh using
WireGuard, OpenVPN, IPsec (strongSwan), and SSL VPN (ocserv) on Debian/Ubuntu.

## Purpose

VPN technology selection and production deployment patterns for a self-managed
multi-tenant SaaS platform. Focus on WireGuard as the default and legacy
options only where compatibility demands them.

## Use cases

| Use case | Who connects | Recommended tech |
| --- | --- | --- |
| Remote admin access to VPS | Engineers, ops | WireGuard |
| Site-to-site between two VPS networks | Routers at each end | WireGuard or IPsec |
| Site-to-site with a corporate partner | Corporate router | IPsec IKEv2 |
| Private service-to-service mesh | Backend services | WireGuard mesh |
| Client access to internal web apps | Office users | WireGuard or ocserv |
| Hostile network (captive portals, DPI) | Travelling users | ocserv over 443 |

Rule of thumb: if you control both ends, use WireGuard. If you have to talk
to a legacy box, use what the other end supports.

## VPN technology comparison

| Feature | WireGuard | OpenVPN | IPsec (IKEv2) | ocserv |
| --- | --- | --- | --- | --- |
| Year | 2015 | 2001 | 1998 | 2013 |
| Lines of code | ~4k | ~100k | ~400k | ~40k |
| Default transport | UDP | UDP (or TCP) | UDP 500/4500 + ESP | TCP/UDP 443 |
| Crypto | ChaCha20-Poly1305, X25519, BLAKE2s | Configurable (default AES-GCM) | Configurable | Configurable |
| Kernel module | Yes (Linux 5.6+) | No (userspace) | Yes (XFRM) | No |
| Config complexity | Minimal | Moderate | High | Moderate |
| Mobile clients | Excellent (iOS/Android native) | Good | Excellent (native on both) | Good (AnyConnect clients) |
| NAT traversal | Natural (UDP) | Natural | Requires NAT-T | Natural (runs on 443) |
| Firewall friendly | Poor (UDP often blocked) | Medium | Poor | Excellent (443) |
| Speed | Fastest | Slow | Fast (kernel) | Medium |
| Compliance footprint | Growing | FIPS-ready builds exist | Strong FIPS support | Medium |

## WireGuard — recommended default

Why WireGuard first:

- Tiny codebase, small audit surface.
- Fixed modern crypto suite — no negotiation, no downgrade.
- In-kernel on Debian 12 and Ubuntu 22.04+ (no DKMS needed).
- Roaming by default (peer IP can change, session survives).
- Configuration is one INI file per endpoint.

Install on Debian 12 / Ubuntu 24.04:

```bash
sudo apt update
sudo apt install -y wireguard qrencode
```

Key generation on the server:

```bash
sudo mkdir -p /etc/wireguard
sudo chmod 700 /etc/wireguard
cd /etc/wireguard
umask 077
wg genkey | tee server_private.key | wg pubkey > server_public.key
cat server_public.key   # record this — you need it in every client
```

Generate a preshared key for a peer (optional but recommended — adds a
symmetric second layer, mitigates future quantum attacks on the asymmetric
exchange):

```bash
wg genpsk > peer1_preshared.key
```

Server config at `/etc/wireguard/wg0.conf`:

```ini
[Interface]
# VPN subnet 10.77.0.0/24 — server is .1
Address = 10.77.0.1/24
ListenPort = 51820
PrivateKey = SERVER_PRIVATE_KEY_HERE
SaveConfig = false

# Peer 1 — engineer laptop
[Peer]
PublicKey = CLIENT1_PUBLIC_KEY
PresharedKey = CLIENT1_PRESHARED_KEY
AllowedIPs = 10.77.0.10/32

# Peer 2 — site-to-site to other VPS
[Peer]
PublicKey = SITE2_PUBLIC_KEY
PresharedKey = SITE2_PRESHARED_KEY
AllowedIPs = 10.77.0.20/32, 10.88.0.0/24
Endpoint = site2.example.com:51820
PersistentKeepalive = 25
```

Key points:

- `AllowedIPs` on the server side restricts which source IPs this peer is
  allowed to use. Do not use `0.0.0.0/0` here — that lets any peer impersonate
  any IP.
- `PersistentKeepalive` only on the side behind NAT (usually the client) —
  keeps the NAT mapping alive.
- `SaveConfig = false` prevents `wg-quick down` from overwriting your config.

Enable IP forwarding (only if this host is routing for peers):

```bash
echo 'net.ipv4.ip_forward=1' | sudo tee /etc/sysctl.d/99-wg-forward.conf
sudo sysctl --system
```

NAT masquerade with nftables (the modern Debian default):

```bash
sudo tee /etc/nftables.d/wg.nft > /dev/null <<'EOF'
table inet wg_nat {
    chain postrouting {
        type nat hook postrouting priority 100;
        oifname "eth0" ip saddr 10.77.0.0/24 masquerade
    }
    chain forward {
        type filter hook forward priority 0;
        iifname "wg0" accept
        oifname "wg0" ct state established,related accept
    }
}
EOF
# Load at boot
sudo tee -a /etc/nftables.conf > /dev/null <<'EOF'
include "/etc/nftables.d/wg.nft"
EOF
sudo systemctl enable --now nftables
```

Enable and start the tunnel:

```bash
sudo systemctl enable --now wg-quick@wg0
sudo wg show                # should list peers
```

Open UDP 51820 at the cloud-provider firewall.

### Client config — engineer laptop

On the client:

```bash
umask 077
wg genkey | tee client_private.key | wg pubkey > client_public.key
```

Send the `client_public.key` to the server admin, who adds it as a new `[Peer]`
and runs `sudo systemctl reload wg-quick@wg0` (or `sudo wg syncconf wg0
<(wg-quick strip wg0)` for no-downtime updates).

Client `wg0.conf`:

```ini
[Interface]
PrivateKey = CLIENT_PRIVATE_KEY
Address = 10.77.0.10/32
DNS = 10.77.0.1            # if server also runs internal DNS

[Peer]
PublicKey = SERVER_PUBLIC_KEY
PresharedKey = CLIENT_PRESHARED_KEY
Endpoint = vpn.example.com:51820
AllowedIPs = 10.77.0.0/24, 10.88.0.0/24    # split tunnel — only these go via VPN
# AllowedIPs = 0.0.0.0/0, ::/0             # full tunnel alternative
PersistentKeepalive = 25
```

### Mobile client via QR code

On the server, generate a mobile config and render a QR:

```bash
qrencode -t ansiutf8 < /etc/wireguard/clients/alice.conf
# Or save as PNG
qrencode -t png -o alice.png < /etc/wireguard/clients/alice.conf
```

The official WireGuard mobile apps on iOS and Android scan the QR directly.

### Peer management pattern

Store peer configs under `/etc/wireguard/clients/<name>.conf` with `chmod 600`
owned by root. A small script to add a peer:

```bash
#!/bin/bash
set -euo pipefail
NAME="$1"
NEXT_IP="$2"    # e.g. 10.77.0.11
SERVER_PUBKEY=$(cat /etc/wireguard/server_public.key)
SERVER_ENDPOINT="vpn.example.com:51820"

umask 077
cd /etc/wireguard/clients
wg genkey | tee "${NAME}_priv.key" | wg pubkey > "${NAME}_pub.key"
wg genpsk > "${NAME}_psk.key"

cat > "${NAME}.conf" <<EOF
[Interface]
PrivateKey = $(cat ${NAME}_priv.key)
Address = ${NEXT_IP}/32
DNS = 10.77.0.1

[Peer]
PublicKey = ${SERVER_PUBKEY}
PresharedKey = $(cat ${NAME}_psk.key)
Endpoint = ${SERVER_ENDPOINT}
AllowedIPs = 10.77.0.0/24
PersistentKeepalive = 25
EOF

# Add peer live, no restart
wg set wg0 peer "$(cat ${NAME}_pub.key)" \
  preshared-key "${NAME}_psk.key" \
  allowed-ips "${NEXT_IP}/32"

# Persist to config file too
cat >> /etc/wireguard/wg0.conf <<EOF

[Peer]
# ${NAME}
PublicKey = $(cat ${NAME}_pub.key)
PresharedKey = $(cat ${NAME}_psk.key)
AllowedIPs = ${NEXT_IP}/32
EOF

echo "Peer ${NAME} added, client config at /etc/wireguard/clients/${NAME}.conf"
```

Revoke a peer:

```bash
sudo wg set wg0 peer <PEER_PUBKEY> remove
# Then edit wg0.conf to delete the [Peer] block
```

### Key rotation runbook

Rotate server keys every 12 months, client keys every 90 days, PSKs every 90
days.

1. Generate new keys in `/etc/wireguard/next/`.
2. For server key rotation: create a second wg interface `wg1` with the new
   key, add peers there, roll peers one at a time, then remove `wg0`.
3. For client key rotation: generate new client keys, issue new config, have
   user import it, remove the old peer entry from the server.
4. Verify with `wg show wg0` — check `latest handshake` is recent for every
   active peer.

## OpenVPN — legacy compatibility

When to use: you must connect to an existing OpenVPN deployment, or the
network blocks all UDP so you need OpenVPN over TCP 443.

```bash
sudo apt install -y openvpn easy-rsa
make-cadir ~/openvpn-ca
# Follow easy-rsa init-pki, build-ca, gen-dh, server cert, client certs
```

Template server config at `/etc/openvpn/server/server.conf`:

```text
port 1194
proto udp
dev tun
ca   /etc/openvpn/server/ca.crt
cert /etc/openvpn/server/server.crt
key  /etc/openvpn/server/server.key
dh   /etc/openvpn/server/dh.pem
server 10.8.0.0 255.255.255.0
keepalive 10 120
cipher AES-256-GCM
auth SHA256
tls-version-min 1.2
tls-cipher TLS-ECDHE-RSA-WITH-AES-256-GCM-SHA384
user nobody
group nogroup
persist-key
persist-tun
verb 3
```

`systemctl enable --now openvpn-server@server`.

UDP vs TCP trade-off: UDP is the default and only sane choice for real use
(lower latency, no TCP-meltdown on packet loss). TCP mode (`proto tcp-server`)
is only for punching through hostile firewalls that block everything except
443/TCP, and the performance is terrible under any packet loss — TCP inside
TCP causes retransmit storms.

## IPsec site-to-site with strongSwan

When you need to interconnect with a corporate partner's router, IPsec IKEv2
is usually the only option they will accept.

Install:

```bash
sudo apt install -y strongswan strongswan-pki libcharon-extra-plugins
```

`/etc/ipsec.conf` for site-to-site with PSK:

```text
config setup
    charondebug = "ike 1, knl 1, cfg 0"
    uniqueids = no

conn %default
    keyexchange = ikev2
    ike = aes256gcm16-sha384-ecp384!
    esp = aes256gcm16-ecp384!
    dpdaction = restart
    dpddelay = 30s
    closeaction = restart

conn corp-to-saas
    left  = 198.51.100.10      # our public IP
    leftsubnet = 10.50.0.0/16  # our internal net
    leftid = @saas.example.com
    right = 203.0.113.20       # corporate public IP
    rightsubnet = 10.200.0.0/16
    rightid = @corp.partner.com
    authby = secret
    auto = start
```

`/etc/ipsec.secrets`:

```text
@saas.example.com @corp.partner.com : PSK "LONG_RANDOM_SHARED_SECRET_HERE"
```

Use certificate auth instead of PSK whenever the other side supports it.
Replace `authby = secret` with `authby = pubkey`, point at a CA, and issue
certs for both ends.

```bash
sudo systemctl enable --now strongswan-starter
sudo ipsec statusall       # verify SA is up
```

PSK vs certificate: PSKs are acceptable for a trial or a single peer. For
anything touching production or more than 2 peers, use certificate auth —
revoking a cert is faster than rotating a shared secret across every peer.

When IPsec is mandatory: corporate VPN concentrators (Cisco ASA, Palo Alto,
Fortinet), some compliance regimes (FedRAMP controls often cite IPsec),
cloud-provider managed site-to-site offerings (AWS VPC S2S, Azure VPN
Gateway, GCP Cloud VPN).

## SSL VPN (ocserv)

ocserv speaks the Cisco AnyConnect protocol over TCP and UDP on port 443.
Useful when clients are stuck behind hotel/airport firewalls that only let 443
out.

```bash
sudo apt install -y ocserv
# Config at /etc/ocserv/ocserv.conf — template ships with sensible defaults
```

Feed it TLS certs from Let's Encrypt. Clients connect with any AnyConnect-
compatible client (OpenConnect on Linux, official Cisco AnyConnect on Windows
/mac/iOS). Feels like a normal VPN from the user perspective.

Trade-off: TCP-on-443 is great for reachability, bad for throughput. Keep it
as a fallback only.

## Split-tunnel vs full-tunnel

| Mode | What goes via VPN | Pros | Cons | Use when |
| --- | --- | --- | --- | --- |
| Split | Only corporate subnets | Fast, low VPN bandwidth, user keeps local internet | User traffic to the public web is not protected by your logging/filtering | Trusted users, admin access, developer access to internal nets |
| Full | All traffic | Uniform egress IP, monitoring and DLP work, safer on hostile WiFi | VPN becomes bandwidth bottleneck, needs capacity planning | Untrusted networks (hotels, coffee shops), compliance requires egress logging |

Threat-model rule: if the user is an engineer with admin access, split tunnel
is fine, their laptop is the hardened asset. If the user is handling regulated
data (health, finance) on an untrusted network, full tunnel.

## WireGuard mesh for microservices

Pattern: every backend service gets a WireGuard interface and a `10.99.x.y`
address. Services only listen on their WireGuard IP. No service port is ever
exposed on the public internet or even on `eth0`.

Benefits:

- No need for mTLS between services — WireGuard already authenticates both
  ends.
- Firewall rules become trivial: drop everything except `wg0`.
- A leaked internal port is no longer automatically exploitable.
- Moving a service to another VPS does not break anything — the IP lives on
  the WG interface, not the host.

Topology: hub-and-spoke for small setups (one gateway, all services peer with
it). Full mesh for larger (every service peers with every other — config can
be generated from an inventory file like Ansible). Or use a small control
plane like `wg-portal` or `netbird` / `tailscale` (tailscale is not self-
managed but uses WireGuard underneath).

Listen binding:

```ini
# php-fpm pool, listen only on WG address
listen = 10.99.0.5:9000
```

```nginx
# upstream also uses WG IPs
upstream backend {
    server 10.99.0.5:9000;
    server 10.99.0.6:9000;
}
```

## Observability

Built-in status:

```bash
sudo wg show
sudo wg show wg0 latest-handshakes
sudo wg show wg0 transfer
```

A peer is "alive" when its latest handshake is within the last ~3 minutes.

Prometheus exporter — `prometheus-wireguard-exporter`:

```bash
# Download binary, systemd unit, scrape on port 9586
sudo prometheus-wireguard-exporter --single_subnet_per_field \
  --config_file_names=/etc/wireguard/wg0.conf
```

Scrape in Prometheus:

```yaml
- job_name: 'wireguard'
  static_configs:
    - targets: ['localhost:9586']
```

Alert rule — peer stale for > 5 minutes:

```yaml
- alert: WireGuardPeerStale
  expr: time() - wireguard_latest_handshake_seconds > 300
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "WG peer {{ $labels.friendly_name }} stale"
```

## Anti-patterns

- Long-lived PSKs (years). Rotate every 90 days, automate it.
- Not setting `AllowedIPs` tight on the server peer — allows IP spoofing
  between peers.
- Using the same WireGuard private key on multiple devices. Handshakes will
  collide, connections will flap. One key per device.
- OpenVPN over TCP as a default. Only use TCP when you must, and know that
  throughput will suffer.
- Treating the VPN as the only authentication. VPN gets you to the network
  — the application must still authenticate the user (JWT, session, mTLS).
- Running site-to-site IPsec with `authby=secret` shared between 5 sites.
  Move to certificates.
- No observability. You will not know the VPN is down until a user
  complains.
- Exposing WireGuard on a well-known port without the public key of the
  peer pre-installed — WireGuard is silent to unauthorised connections,
  which is a feature, but it also means operators cannot easily see if the
  port is reachable. Test from outside with `wg` after setup.
- Full-tunnel mode without capacity planning. Suddenly 50 users route all
  their Netflix through your VPS.

## Cross-references

- `references/tls-pki.md` for certificate-auth IPsec and ocserv TLS setup
- `references/crypto-fundamentals.md` for why WireGuard's crypto choices are
  safe
- `cicd-devsecops` skill for securing the pipeline that deploys VPN configs
- `microservices-communication` skill for the service mesh context
- `multi-tenant-saas-architecture` skill for tenant isolation boundaries
