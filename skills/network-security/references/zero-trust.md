# Zero-Trust Networking for Self-Managed SaaS

Zero-trust architecture patterns for multi-tenant SaaS on Debian/Ubuntu. Covers BeyondCorp, NIST SP 800-207, identity-aware proxy, mTLS, SPIFFE, WireGuard mesh, and migration roadmap.

## Core principles

Zero-trust is a set of network and access design principles, not a product. The four pillars:

1. **Never trust, always verify.** Every request — whether from the public internet or from a pod two hops away inside the cluster — must prove who it is and what it is allowed to do. There is no "inside the firewall, therefore trusted" exception.
2. **Least privilege.** Every identity (user, workload, device) gets only the access required for its specific purpose, scoped in time and blast radius.
3. **Assume breach.** Design as if an attacker is already inside. The question is not "how do we keep them out" but "how do we limit what they can do once in".
4. **Verify explicitly.** Every decision uses multiple signals: identity, device posture, request context, time of day, geography, recent behaviour. A valid token alone is not enough.

## Why now

The classic perimeter model assumed a hard outer shell (the firewall) and a soft, trusted interior. That model broke under several simultaneous pressures:

- **Remote work.** Employees connect from home networks, cafes, airports. There is no single "inside" anymore.
- **Cloud and SaaS.** Workloads run on infrastructure you do not own. Data flows to Stripe, to Google, to your own AWS account — none of it is inside your firewall.
- **Microservices.** A single user request may traverse 20 internal services. If internal hops are trusted blindly, one compromised container owns everything.
- **Lateral movement attacks.** Modern breaches rarely hit their target directly. They land on a developer laptop or a neglected wiki server, then pivot for weeks. A flat internal network lets them run unchecked.

Zero-trust is a response to these: treat every hop as hostile, verify every call.

## BeyondCorp model

Google's BeyondCorp paper (2014 onwards) is the canonical zero-trust case study. Core ideas:

- **No VPN.** Remote access is not granted by IP; it is granted by identity plus device posture.
- **Device inventory and certificates.** Every device is enrolled, has a certificate, and has a continuously evaluated trust tier.
- **Access proxy** sits in front of every internal app, authenticating users and authorising based on user + device + context.
- **Access Control Engine** makes the decision using the above signals.
- **Single sign-on** with strong auth (hardware keys, not SMS).

For a small SaaS, the practical takeaway is: stop using "are they on the VPN" as an authorisation decision. Put an identity-aware proxy in front of every admin panel, staging site, and internal tool.

## NIST SP 800-207

NIST codified the architecture in Special Publication 800-207. The key components:

- **PEP (Policy Enforcement Point)** — the thing in the request path that accepts or rejects traffic. Your nginx sidecar, your proxy, your service mesh envoy.
- **PDP (Policy Decision Point)** — the brain. Given a request context, it returns allow/deny. Usually an OPA instance, a Keycloak policy engine, or a custom service.
- **PA (Policy Administrator)** — the coordinator. Talks to the PEP and the PDP, manages sessions and tokens.

In a minimal self-managed stack:

```text
user → nginx (PEP) → auth_request to oauth2-proxy (PA)
                        → OIDC handshake with Keycloak (PDP)
                        ← signed JWT
                     → upstream app if allowed
```

You do not need a boxed "zero-trust platform" product. You need these three roles clearly identified and connected.

## Identity-aware proxy pattern

The highest-value, lowest-cost zero-trust move for a self-managed SaaS: put an identity-aware proxy in front of every internal admin tool. Use `oauth2-proxy` in front of nginx with `auth_request`.

Install:

```bash
sudo apt install oauth2-proxy
```

Configure `/etc/oauth2-proxy.cfg`:

```ini
provider = "oidc"
oidc_issuer_url = "https://auth.example.com/realms/internal"
client_id = "oauth2-proxy"
client_secret = "${OIDC_CLIENT_SECRET}"
cookie_secret = "${COOKIE_SECRET_32_BYTE_BASE64}"
email_domains = ["example.com"]
http_address = "127.0.0.1:4180"
upstreams = ["static://202"]
reverse_proxy = true
cookie_secure = true
cookie_httponly = true
cookie_samesite = "lax"
set_xauthrequest = true
pass_access_token = true
```

Nginx config protecting the internal admin panel:

```nginx
server {
    listen 443 ssl http2;
    server_name admin.example.com;

    ssl_certificate     /etc/letsencrypt/live/admin.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/admin.example.com/privkey.pem;

    # oauth2-proxy callback
    location /oauth2/ {
        proxy_pass       http://127.0.0.1:4180;
        proxy_set_header Host                    $host;
        proxy_set_header X-Real-IP               $remote_addr;
        proxy_set_header X-Forwarded-For         $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto       $scheme;
    }

    location = /oauth2/auth {
        internal;
        proxy_pass       http://127.0.0.1:4180;
        proxy_set_header Host             $host;
        proxy_set_header X-Real-IP        $remote_addr;
        proxy_set_header X-Forwarded-Uri  $request_uri;
        proxy_pass_request_body off;
        proxy_set_header Content-Length "";
    }

    location / {
        auth_request /oauth2/auth;
        error_page 401 = /oauth2/sign_in;

        auth_request_set $email  $upstream_http_x_auth_request_email;
        proxy_set_header X-User  $email;

        proxy_pass http://127.0.0.1:8080;  # your internal app
    }
}
```

Every request to `admin.example.com` now forces OIDC login. The app sees a trusted `X-User` header and does not need to implement auth itself.

**SSO backends** — pick one and stick with it:

- **Keycloak** — full-featured, battle-tested, Java/heavy. Good for larger teams.
- **Authentik** — Python, modern UI, easier to operate than Keycloak.
- **Authelia** — lightweight, single-binary, excellent integration with nginx `auth_request` and Traefik forward-auth.

For a small SaaS, Authelia is the shortest path to a working IAP.

## mTLS everywhere — service to service

Every internal service presents a client certificate signed by your internal CA. Every server verifies it. Compromising one service does not grant access to any other.

Issue and rotate certs with `step-ca` (smallstep):

```bash
# Bootstrap a small internal CA
step ca init --name "Internal CA" --dns ca.internal --address :8443 \
  --provisioner admin@example.com

# Each workload fetches a cert with a short TTL
step ca certificate orders-svc.internal orders.crt orders.key \
  --not-after 24h --provisioner acme
```

Nginx upstream with client-cert verification:

```nginx
upstream orders_backend {
    server orders.internal:8443;
}

server {
    listen 8443 ssl http2;
    server_name billing.internal;

    ssl_certificate     /etc/ssl/billing.crt;
    ssl_certificate_key /etc/ssl/billing.key;
    ssl_client_certificate /etc/ssl/internal-ca.crt;
    ssl_verify_client on;
    ssl_verify_depth 2;

    location / {
        if ($ssl_client_s_dn !~ "CN=orders-svc") { return 403; }
        proxy_pass https://orders_backend;
    }
}
```

Rotate certs on a schedule (every 24 hours is fine once the automation is solid). A cert that never rotates is as bad as a cert that never expires.

**Service mesh alternative.** Istio and Linkerd offer mTLS-by-default for every pod, plus identity-based L7 policy. They are heavy — expect a significant operational commitment. For under 20 services, stick with step-ca and nginx; graduate to Linkerd (lighter than Istio) when you cross that threshold.

## SPIFFE and SPIRE

SPIFFE is a standard for workload identity. Each workload gets an **SVID** — a short-lived certificate or JWT whose subject is a SPIFFE ID like `spiffe://example.com/ns/prod/sa/orders`. SPIRE is the reference implementation that issues SVIDs to workloads, attesting them based on unforgeable signals (host TPM, Kubernetes namespace + service account, cloud instance metadata).

The value: workloads no longer carry long-lived secrets. Identity is derived from where they run and what they are, not from a password file. Use SPIFFE/SPIRE once you outgrow step-ca's simpler model, typically when you need federation between multiple clusters or clouds.

## WireGuard mesh for the private service plane

The boldest zero-trust move: **no public ports on any application server**. The only path into any app host is via WireGuard peers, and the app servers only accept WG peers listed in their config.

Install and configure:

```bash
sudo apt install wireguard

# Generate keypair on each host
wg genkey | tee privatekey | wg pubkey > publickey
```

Sample `/etc/wireguard/wg0.conf` on an app server:

```ini
[Interface]
Address    = 10.100.0.5/24
ListenPort = 51820
PrivateKey = <app_server_private_key>

# Allow only admin jumpbox and peer app servers
[Peer]
PublicKey           = <admin_jumpbox_public_key>
AllowedIPs          = 10.100.0.1/32
PersistentKeepalive = 25

[Peer]
PublicKey  = <peer_app_public_key>
AllowedIPs = 10.100.0.6/32
```

Bring it up:

```bash
sudo systemctl enable --now wg-quick@wg0
```

Combine with nftables to drop everything that is not WireGuard or 443 (for public traffic) at the edge. Admin SSH, Prometheus scrape, database connections, all internal RPC — everything happens over 10.100.0.0/24 only.

## Device posture checks

In the BeyondCorp model, the identity proxy does not only ask "who are you"; it asks "is your device currently trusted?" Device posture signals include:

- Disk encryption enabled
- OS version up to date
- Anti-malware agent running and current
- Corporate MDM profile installed
- Certificate chain rooted in your internal CA

Self-hosted tools like **Cloudflare WARP + Zero Trust** (cloud), **Tailscale + device posture policies**, or rolling your own osquery fleet that reports to a posture-aware proxy can provide these signals. For a small team, the minimum viable posture check is: does the device have a valid, current internal TLS client cert? If yes, it has been enrolled and has not yet been revoked.

## Migration path: perimeter → zero-trust

Do not attempt a full cutover. Stage it.

**Phase 1 — Identity-aware proxy on admin panels.** Put oauth2-proxy + OIDC in front of every internal tool (admin, grafana, staging, wiki). This gives you the single biggest security improvement with the least work. Weeks 1–2.

**Phase 2 — mTLS between internal services.** Stand up step-ca, issue certs to the top 5 services that handle sensitive data. Enforce client-cert verification at the nginx/ingress layer. Weeks 3–6.

**Phase 3 — WireGuard mesh for admin access.** Stop exposing SSH on any public IP. Admin access only via WG peer. Remove the public `:22` rule from the firewall. Weeks 7–8.

**Phase 4 — Short-lived creds everywhere.** Replace long-lived API keys, database passwords, and SSH keys with OIDC-issued, short-TTL tokens. Integrate with HashiCorp Vault or step-ca. Months 3–4.

**Phase 5 — Continuous verification and device posture.** Add device cert checks to the IAP. Re-evaluate session trust on a timer. Revoke based on anomaly signals (new IP, new country, impossible travel). Months 5–6.

## Cost vs benefit

Zero-trust is not free. It adds operational complexity, cert rotation automation, identity-provider uptime as a critical path, and developer friction (every internal tool needs an OIDC login).

**Worth it when:**

- Multi-tenant SaaS holding other people's data.
- Regulated industry (finance, healthcare, government).
- More than 10 services and more than 5 engineers.
- You have had a security incident or a pentest that showed lateral movement risk.
- Remote-first team with no stable office network.

**Probably overkill when:**

- Single-tenant app on one VPS with two engineers.
- Prototype stage, no real customers.
- Strict budget, small attack surface, good backup discipline.

A hybrid approach is usually right: start with Phase 1 (IAP on admin panels) regardless of size — it pays for itself within a week. Defer the other phases until the service count or compliance posture demands them.

## Anti-patterns

- **Zero-trust as a marketing checkbox.** Buying a "zero-trust platform" without changing how you design access. If your engineers still think "we are on the VPN, we are safe", you have not adopted zero-trust.
- **mTLS without rotation.** Certs that last a year are not materially different from passwords in a config file. Rotate aggressively and automatically.
- **IAP that caches "trusted" too long.** A 30-day cookie defeats the point of continuous verification. Use short sessions (1–4 hours) and silent refresh.
- **Treating the internal network as safe.** "We have a WAF at the edge" is not a zero-trust argument. Any internal service must still authenticate every call.
- **Single OIDC provider with no redundancy or break-glass.** When Keycloak goes down, your entire company loses access to every internal tool. Plan break-glass accounts stored offline.
- **Allow-listing by IP inside the cluster.** Pod IPs change, attackers spoof, and it teaches developers the wrong model.
- **Deploying Istio to a 3-service startup.** The operational cost will outweigh the benefit by an order of magnitude. Use step-ca + nginx.
- **Forgetting the people layer.** Zero-trust fails if onboarding/offboarding is manual. Tie OIDC group membership to your HR system.

## Cross-references

- `references/ssh-bastion.md` — bastion is the minimum step before WireGuard mesh replaces it
- `references/firewall-fundamentals.md` — nftables rules enforcing no-public-ports in Phase 3
- `references/ids-ips.md` — network-level IDS still needed even with mTLS
- `SKILL.md` — network-security skill overview
- `multi-tenant-saas-architecture` skill — tenant isolation principles that pair with zero-trust
- `cicd-devsecops` skill — HashiCorp Vault for short-lived credential issuance
- `microservices-communication` skill — inter-service authentication patterns
- `dual-auth-rbac` skill — application-layer authorisation that sits on top of zero-trust
