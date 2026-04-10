# Network Segmentation

Design and enforce network tiers on a self-managed Debian/Ubuntu VPS so that a
compromised component cannot reach assets it has no business touching.

## Why segment

A flat network is a single blast radius. Once an attacker lands on any host they
can probe every other host, pivot into the database, and exfiltrate at will.
Segmentation constrains lateral movement and makes containment tractable.

- **Blast radius containment.** A compromise of the public web tier should not
  grant unfiltered access to the database.
- **Lateral movement limits.** Unrelated services cannot see each other.
- **Compliance drivers.** PCI-DSS requires the cardholder data environment (CDE)
  to be isolated. HIPAA-adjacent workloads benefit from similar isolation.
- **Operational clarity.** Segmentation forces you to document every flow, which
  is invaluable during incident response.

## Segmentation layers

Segmentation is not a single decision. It is a stack of decisions at several
layers, each contributing defence in depth.

| Layer | Mechanism | Typical use |
|---|---|---|
| Physical | Separate NICs, separate switches | Bare-metal tier isolation |
| VLAN | 802.1Q tagging on a shared link | Collapsing multi-tier onto one trunk |
| Subnet | IP routing boundaries | Directing traffic through a firewall |
| Host firewall | nftables/UFW rules | Per-host policy, last line of defence |
| Network namespace | Linux `ip netns` | Per-process isolation on one host |
| Container network | Docker bridge/overlay | Per-service isolation |
| Service mesh | mTLS + policy | Microsegmentation at the identity layer |

## Public / DMZ / private three-tier layout

A pragmatic VPS topology for SaaS.

```text
            Internet
              |
        [ edge firewall / WAF ]
              |
  +-----------+------------+
  |           |            |
10.0.1.0/24  10.0.2.0/24  10.0.3.0/24
  PUBLIC      APP          DATA
  nginx,      PHP/Node,    MySQL/Postgres,
  reverse     workers,     Redis,
  proxy       APIs         internal queues
```

Traffic rules:

- `Internet -> PUBLIC`: HTTPS/443 only, WAF in front.
- `PUBLIC -> APP`: specific app ports (8080, 9000), default deny elsewhere.
- `APP -> DATA`: database ports (3306, 5432, 6379), default deny elsewhere.
- `DATA -> APP`: deny by default (databases do not initiate connections).
- `* -> Internet`: egress filter, allow-list of package mirrors, Let's Encrypt,
  payment providers; drop the rest.

## Linux network namespaces

Network namespaces provide kernel-level network isolation for processes on the
same host. Useful for sandboxing a risky daemon or running a background worker
with its own egress posture.

```bash
sudo ip netns add isolated
sudo ip link add veth0 type veth peer name veth1
sudo ip link set veth1 netns isolated
sudo ip addr add 10.200.0.1/24 dev veth0
sudo ip link set veth0 up
sudo ip netns exec isolated ip addr add 10.200.0.2/24 dev veth1
sudo ip netns exec isolated ip link set veth1 up
sudo ip netns exec isolated ip route add default via 10.200.0.1

# Run a service inside the namespace
sudo ip netns exec isolated sudo -u appuser /opt/worker/run.sh
```

The worker now sees only the veth link and whatever NAT/forwarding the host
allows, giving you a chokepoint to filter its egress traffic independently.

## Docker networks

Docker provides four useful network drivers. Choosing the right one is the
difference between meaningful isolation and a flat network dressed up.

| Driver | When to use | Isolation |
|---|---|---|
| `bridge` (default) | Single-host multi-container app | Per-network; containers on other networks cannot reach each other |
| `host` | Max performance, kernel bypass | None, container shares host net stack (avoid) |
| `overlay` | Multi-host Swarm clusters | Encrypted VXLAN between nodes |
| `macvlan` | Container needs its own MAC/IP on LAN | Appears as a separate physical device |

A `docker-compose.yml` that isolates tiers on one host:

```yaml
services:
  web:
    image: nginx:stable
    networks: [frontend]
    ports: ["443:443"]
  api:
    image: ghcr.io/example/api:1.0
    networks: [frontend, backend]
  db:
    image: mysql:8
    networks: [backend]
    volumes: ["db:/var/lib/mysql"]
networks:
  frontend:
    driver: bridge
    internal: false
  backend:
    driver: bridge
    internal: true   # no outbound Internet from the db network
volumes: { db: {} }
```

`internal: true` on the backend network removes the NAT gateway, so the database
container has no path to the Internet. The api is the only service bridging
both networks.

## nftables per-tier rules

Host-level firewall that complements the docker/namespace topology. Example:
block writes from outside the app tier to the db tier.

```bash
sudo nft add table inet segments
sudo nft add chain inet segments forward '{ type filter hook forward priority 0; policy drop; }'
# Allow established
sudo nft add rule inet segments forward ct state established,related accept
# APP -> DATA (mysql)
sudo nft add rule inet segments forward ip saddr 10.0.2.0/24 ip daddr 10.0.3.0/24 tcp dport 3306 accept
# PUBLIC -> APP
sudo nft add rule inet segments forward ip saddr 10.0.1.0/24 ip daddr 10.0.2.0/24 tcp dport { 8080, 9000 } accept
# Everything else drops
```

## Cloud-agnostic "security groups" pattern

Hyperscaler security groups are just per-host stateful firewalls with a friendly
UI. On a VPS you reproduce them with **nftables sets** keyed by role.

```bash
sudo nft add set inet filter role_app '{ type ipv4_addr; flags interval; }'
sudo nft add element inet filter role_app '{ 10.0.2.10, 10.0.2.11 }'
sudo nft add rule inet filter input ip saddr @role_app tcp dport 3306 accept
```

Adding a new app node is `nft add element`, no rule duplication required.

## Bastion / jump host topology

Administrative access should not flow directly to every host. A bastion
(jump host) sits in its own small subnet, is the only host with public SSH, and
internal hosts only accept SSH from the bastion's private IP.

See `ssh-bastion.md` for the full configuration including ProxyJump, match
blocks, and Fail2ban.

## Management plane isolation

Admin interfaces (database consoles, monitoring, CI runners, SSH) must not share
a wire with customer traffic.

- Dedicated WireGuard tunnel (`wg0`) for ops.
- Bind admin listeners to the `wg0` IP only, not `0.0.0.0`.
- Block inbound admin ports on the public interface via nftables.
- Require a separate SSO/MFA on admin endpoints.

```text
# /etc/mysql/mysql.conf.d/mysqld.cnf
[mysqld]
bind-address = 10.8.0.1   # WireGuard peer, not the public IP
```

## VLANs on bare-metal

When you do own the hardware, 802.1Q VLAN tags let you split a single NIC into
logical tiers carried over one trunk port.

```bash
sudo apt install vlan
sudo modprobe 8021q
sudo ip link add link eth0 name eth0.10 type vlan id 10
sudo ip addr add 10.0.10.1/24 dev eth0.10
sudo ip link set eth0.10 up
```

The upstream switch port must be configured as a trunk that allows the chosen
VLAN IDs; otherwise the tagged frames are dropped silently at the switch.

## Microsegmentation with service mesh

Subnet firewalls are coarse. Microsegmentation pushes policy down to the
service-to-service identity layer using mTLS. Rather than "the app subnet can
reach the db subnet", the rule becomes "the `orders` service can call the
`payments` service, verified by certificate". See `zero-trust.md`.

## Anti-patterns

- Flat network: one `/24`, every host reachable from every host.
- One firewall rule set copy-pasted onto every tier with no customisation.
- Administrative ports (3306, 5432, 6379, 9200) bound to `0.0.0.0`.
- Allowing arbitrary outbound from a DMZ subnet ("it's only outbound, how bad
  can it be?" — bad, because exfiltration and reverse shells use outbound).
- Docker containers on `--network host` for "performance".
- WireGuard peer allow-lists that use `0.0.0.0/0`, defeating the point of the
  peer isolation.
- Database credentials that are valid from any source IP inside the org.

## Cross-references

- `firewall-strategy.md` for nftables base rules and boilerplate.
- `ssh-bastion.md` for jump host configuration.
- `zero-trust.md` for identity-based microsegmentation and mTLS.
- `ids-logging.md` for detecting traffic that crosses tier boundaries in
  unexpected ways.
- `audit-checklist.md` for segmentation verification items.
