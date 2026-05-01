# TLS and PKI for Self-Managed Debian/Ubuntu SaaS

Production-grade TLS termination, certificate lifecycle, and PKI patterns for
multi-tenant SaaS hosted on Debian 12 / Ubuntu 22.04 and 24.04.

## Purpose

Hardened TLS configuration, certificate issuance, and PKI hierarchy for public
edge nginx and for internal service-to-service mTLS.

## TLS version landscape (2026)

By 2026, TLS 1.2 and 1.3 are the only acceptable versions on the public edge.
SSLv2, SSLv3, TLS 1.0 and TLS 1.1 are all formally deprecated (RFC 8996) and
must be disabled.

| Version | Status 2026 | Notes |
| --- | --- | --- |
| SSLv2 / SSLv3 | Forbidden | POODLE, weak crypto |
| TLS 1.0 / 1.1 | Forbidden | RFC 8996, PCI-DSS bans since 2018 |
| TLS 1.2 | Acceptable fallback | Only with AEAD suites and PFS |
| TLS 1.3 | Preferred default | Mandatory PFS, AEAD only, faster |
| TLS 1.3 + PQ hybrid | Emerging | X25519+ML-KEM, enable if clients support |

Policy: serve TLS 1.3 first, fall back to TLS 1.2 only for legacy clients, and
only with AEAD cipher suites. Any system still requiring TLS 1.0/1.1 must be
isolated behind a separate gateway, never on the main tenant edge.

## TLS 1.3 handshake — what actually happens

TLS 1.3 handshakes complete in 1 round trip (1-RTT) instead of 2 for TLS 1.2.
High-level sequence:

1. Client sends `ClientHello` containing supported TLS versions, supported
   cipher suites, supported key-exchange groups, and one or more ephemeral
   public keys (X25519 typically) — a guess at which group the server will
   pick.
2. Server replies with `ServerHello` which picks the group, sends its own
   ephemeral public key, and from that point every following message is
   already encrypted with the derived handshake key. The server also sends
   its certificate chain, a signature over the handshake, and `Finished`.
3. Client verifies the chain, sends `Finished`, and application data starts
   flowing. That is the entire handshake in one round trip.

0-RTT (early data) lets the client send application data in the very first
flight using a PSK from a previous session. It is fast but replayable — only
enable it for idempotent GET requests, never for state changes, logins, or
anything financial. On most SaaS edges leave 0-RTT off.

TLS 1.3 drops every non-AEAD cipher, drops RSA key transport, drops static
Diffie-Hellman, and enforces forward secrecy on every connection. You cannot
misconfigure it into something weak the way TLS 1.2 allowed.

## Cipher suites

TLS 1.3 suites (nginx accepts all of these by default, listed for clarity):

```text
TLS_AES_256_GCM_SHA384
TLS_CHACHA20_POLY1305_SHA256
TLS_AES_128_GCM_SHA256
```

TLS 1.2 fallback suites (forward secrecy + AEAD only):

```text
ECDHE-ECDSA-AES256-GCM-SHA384
ECDHE-RSA-AES256-GCM-SHA384
ECDHE-ECDSA-CHACHA20-POLY1305
ECDHE-RSA-CHACHA20-POLY1305
ECDHE-ECDSA-AES128-GCM-SHA256
ECDHE-RSA-AES128-GCM-SHA256
```

Never enable: anything with `CBC`, `RC4`, `3DES`, `DES`, `NULL`, `EXPORT`,
`aNULL`, `eNULL`, `MD5`, `PSK` (on public edge), `SRP`, or static RSA.

## Certificate types

| Type | What it proves | Use case |
| --- | --- | --- |
| DV (Domain Validated) | Applicant controls the DNS name | Default for SaaS, Let's Encrypt |
| OV (Organisation Validated) | Legal entity exists | Corporate, rarely needed |
| EV (Extended Validation) | Deep legal vetting | Legacy, no browser UI benefit in 2026 |

| Scope | Covers | Note |
| --- | --- | --- |
| Single-domain | Exactly one FQDN | Cheapest, simplest |
| SAN (multi-domain) | Up to N explicit FQDNs | List every hostname |
| Wildcard | `*.example.com` | One level only, requires DNS-01 |

DV is fine for SaaS. Browsers no longer show any visual difference between DV
and EV since Chrome 77 and Firefox 70. Do not pay for EV in 2026.

## PKI hierarchy and chain validation

A real PKI has three tiers:

```text
Root CA  (offline, self-signed, 20 year key, trusted by browsers)
  |
  +-- Intermediate CA  (online, 5-10 year, issues leaves)
        |
        +-- Leaf certificate  (90 day, what your server serves)
```

A client validates by walking up the chain: each certificate's signature must
verify against the public key of its issuer, until it reaches a root the
client already trusts. The server must present the leaf plus all intermediates;
it must not send the root (browsers already trust the root, and sending it
wastes bytes).

Let's Encrypt in 2026 issues from ISRG Root X1 (RSA) and ISRG Root X2 (ECDSA),
with intermediates named like E5, E6, R10, R11. Always let certbot pick the
chain — do not hardcode an intermediate.

## Let's Encrypt with certbot on Debian

Install:

```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx python3-certbot-dns-cloudflare
```

Single-domain cert, nginx plugin (easiest):

```bash
sudo certbot --nginx \
  -d app.example.com \
  -d www.example.com \
  --agree-tos \
  --email ops@example.com \
  --redirect \
  --hsts \
  --no-eff-email
```

Wildcard cert via DNS-01 with Cloudflare:

```bash
# 1. Create API token in Cloudflare with Zone:DNS:Edit on the zone
sudo mkdir -p /etc/letsencrypt/secrets
sudo tee /etc/letsencrypt/secrets/cloudflare.ini > /dev/null <<'EOF'
dns_cloudflare_api_token = REPLACE_WITH_TOKEN
EOF
sudo chmod 600 /etc/letsencrypt/secrets/cloudflare.ini

# 2. Issue the wildcard
sudo certbot certonly \
  --dns-cloudflare \
  --dns-cloudflare-credentials /etc/letsencrypt/secrets/cloudflare.ini \
  -d 'example.com' -d '*.example.com' \
  --preferred-challenges dns-01 \
  --agree-tos --email ops@example.com --no-eff-email
```

Auto-renewal is installed by the Debian package as a systemd timer. Verify and
dry-run:

```bash
systemctl list-timers | grep certbot
sudo certbot renew --dry-run
```

Add a deploy hook so nginx reloads only when a cert actually renewed:

```bash
sudo tee /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh > /dev/null <<'EOF'
#!/bin/bash
systemctl reload nginx
EOF
sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
```

## Alternative: acme.sh (lightweight, bash-only)

Useful when you do not want Python dependencies, or you are inside a minimal
container. acme.sh is a single bash script.

```bash
curl https://get.acme.sh | sh -s email=ops@example.com
source ~/.bashrc

# Set Cloudflare token
export CF_Token="REPLACE_WITH_TOKEN"

# Issue
~/.acme.sh/acme.sh --issue --dns dns_cf \
  -d example.com -d '*.example.com' \
  --server letsencrypt

# Install
~/.acme.sh/acme.sh --install-cert -d example.com \
  --key-file       /etc/nginx/ssl/example.com.key \
  --fullchain-file /etc/nginx/ssl/example.com.fullchain.pem \
  --reloadcmd      "systemctl reload nginx"
```

acme.sh installs its own cron entry for daily renewal checks.

## Nginx TLS config — production grade

Full server block (place under `/etc/nginx/sites-available/app.example.com`):

```nginx
# Shared TLS settings — put once in /etc/nginx/conf.d/ssl-hardening.conf
ssl_protocols TLSv1.3 TLSv1.2;
ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
ssl_prefer_server_ciphers off;      # TLS 1.3 decides, client picks for 1.2
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;
ssl_session_tickets off;            # off unless rotating ticket keys hourly
ssl_ecdh_curve X25519:secp384r1;

# OCSP stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 1.1.1.1 9.9.9.9 valid=300s;
resolver_timeout 5s;

# Per-site server block
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;
    server_name app.example.com;

    ssl_certificate     /etc/letsencrypt/live/app.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.example.com/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/app.example.com/chain.pem;

    # HSTS — 2 years, include subdomains, preload
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    root /var/www/app;
    index index.php;

    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php8.3-fpm.sock;
    }
}

# Force redirect from HTTP
server {
    listen 80;
    listen [::]:80;
    server_name app.example.com;
    return 301 https://$host$request_uri;
}
```

`ssl_dhparam` is no longer required in TLS 1.3 and with ECDHE-only suites in
TLS 1.2. Only generate one if you enable `DHE-*` suites, which you should not.

Reload and verify:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

## OCSP stapling

OCSP stapling means the server fetches its own revocation status from the CA
and attaches it to the TLS handshake, instead of the browser going to the CA
every connection. Faster, preserves user privacy.

Verify stapling is working:

```bash
echo | openssl s_client -connect app.example.com:443 -servername app.example.com -status 2>/dev/null | grep -A 17 'OCSP response'
```

Look for `OCSP Response Status: successful` and a `Cert Status: good`. If you
see `no response sent`, nginx could not reach the OCSP responder — check
`resolver` directive and outbound firewall to port 80 (OCSP runs over HTTP).

## HSTS and preload

HSTS tells browsers: "for the next N seconds, only talk to me over HTTPS, no
exceptions." Preload bakes your domain into the browser source code so even
the very first visit is forced to HTTPS.

Header format:

```text
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
```

Preload submission:

1. Serve the header on the apex and every subdomain, for at least 14 days.
2. Ensure every subdomain actually has a working cert (preload breaks any
   subdomain without HTTPS — including legacy `mail.`, `ftp.`, staging).
3. Submit at `https://hstspreload.org`.
4. Removal from preload takes months. Test thoroughly first.

Gotchas: any http-only internal dashboard under the domain will become
unreachable. Mixed content (http images on https pages) breaks. Do not preload
until you are certain.

## mTLS for internal services

Mutual TLS means the server also verifies the client's certificate. Use this
for machine-to-machine calls between internal services — never for end users.

Nginx config fragment to require client certs:

```nginx
server {
    listen 8443 ssl;
    server_name internal-api.svc.local;

    ssl_certificate     /etc/nginx/mtls/server.crt;
    ssl_certificate_key /etc/nginx/mtls/server.key;

    ssl_client_certificate /etc/nginx/mtls/ca.crt;   # your internal CA
    ssl_verify_client on;
    ssl_verify_depth 2;

    location / {
        proxy_set_header X-Client-DN "$ssl_client_s_dn";
        proxy_pass http://backend_upstream;
    }
}
```

Generate client certs with openssl (one-time, for testing; use step-ca for
production — see next section):

```bash
# Assume you already have ca.crt / ca.key
openssl genrsa -out client.key 4096
openssl req -new -key client.key -out client.csr \
    -subj "/CN=worker-01/O=InternalSaaS"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out client.crt -days 90 -sha256 \
    -extfile <(printf "extendedKeyUsage=clientAuth")
```

Clients present `client.crt` + `client.key` when calling the service. Keep
client key files `chmod 600`, owned by the service user.

## Internal CA with step-ca

step-ca from smallstep gives you a real internal CA with ACME support — so
internal services can auto-renew just like Let's Encrypt.

Install on Debian:

```bash
wget https://dl.smallstep.com/cli/docs-ca-install/latest/step-cli_amd64.deb
wget https://dl.smallstep.com/certificates/docs-ca-install/latest/step-ca_amd64.deb
sudo dpkg -i step-cli_amd64.deb step-ca_amd64.deb
```

Initialise the CA (interactive — choose hostname, set strong password, store
the provisioner password outside the box):

```bash
step ca init \
  --name "InternalSaaS CA" \
  --dns ca.internal.example.com \
  --address :8443 \
  --provisioner admin@example.com
```

Run step-ca as a systemd service (the installer usually sets this up).

Enable ACME provisioner:

```bash
step ca provisioner add acme --type ACME
systemctl restart step-ca
```

Internal services then issue certs with certbot or acme.sh pointing at
`https://ca.internal.example.com/acme/acme/directory`, with the step-ca root
added to their trust store.

Issue a cert directly (non-ACME path):

```bash
step ca certificate worker-01.internal.example.com worker.crt worker.key \
  --not-after 90m
```

## Cert expiry monitoring

Use Prometheus `blackbox_exporter` with the `tls_connect` module.

`/etc/prometheus/blackbox.yml` module:

```yaml
modules:
  tls_connect:
    prober: tcp
    timeout: 5s
    tcp:
      tls: true
      tls_config:
        insecure_skip_verify: false
```

Scrape config in `prometheus.yml`:

```yaml
- job_name: 'tls_expiry'
  metrics_path: /probe
  params:
    module: [tls_connect]
  static_configs:
    - targets:
        - app.example.com:443
        - api.example.com:443
        - tenant1.example.com:443
  relabel_configs:
    - source_labels: [__address__]
      target_label: __param_target
    - source_labels: [__param_target]
      target_label: instance
    - target_label: __address__
      replacement: 127.0.0.1:9115
```

Alert rules:

```yaml
groups:
- name: tls_expiry
  rules:
  - alert: TLSCertExpiringSoon
    expr: (probe_ssl_earliest_cert_expiry - time()) / 86400 < 14
    for: 1h
    labels:
      severity: warning
    annotations:
      summary: "TLS cert for {{ $labels.instance }} expires in <14 days"

  - alert: TLSCertExpiringCritical
    expr: (probe_ssl_earliest_cert_expiry - time()) / 86400 < 3
    for: 10m
    labels:
      severity: critical
    annotations:
      summary: "TLS cert for {{ $labels.instance }} expires in <3 days"
```

## Cert rotation runbook

Zero-downtime rotation (certbot handles this for Let's Encrypt automatically
— this is the manual process if you need it):

1. Obtain the new cert to a staging path, not the live path.
2. Validate chain: `openssl verify -CAfile chain.pem newcert.pem`.
3. Copy new files atomically: `install -m 644 new.crt /etc/nginx/ssl/live.crt`
   and `install -m 600 new.key /etc/nginx/ssl/live.key`.
4. Test nginx config: `nginx -t`.
5. Reload, not restart: `systemctl reload nginx`. Reload keeps existing TCP
   connections alive.

Verify after reload:

```bash
echo | openssl s_client -connect app.example.com:443 -servername app.example.com 2>/dev/null \
  | openssl x509 -noout -dates -subject
```

## Anti-patterns

- Self-signed certs on production anything users see. Browsers will reject
  them and users will be trained to click through warnings.
- Wildcard certs shared across tenants where each tenant has their own
  subdomain and compromise of one equals compromise of all. Prefer per-tenant
  certs via ACME automation.
- Disabling certificate verification in HTTP clients (`curl -k`, Python
  `verify=False`, Node `rejectUnauthorized: false`) anywhere in production
  code. Fix the trust store instead.
- Long-lived internal certs (5+ years). If the key leaks, you cannot rotate
  in time. Keep internal certs under 90 days and automate renewal.
- No monitoring. Certs silently expire at 2am on Sunday.
- Copying private keys via email, Slack, unencrypted S3, or anything that is
  not an airgapped secure transfer. Regenerate instead.
- Running TLS termination on the application process when an edge proxy
  (nginx, HAProxy, Caddy) is already available — application should get
  plain HTTP on localhost, the edge handles TLS.

## Cross-references

- `references/vpn.md` for site-to-site and client VPN patterns
- `references/crypto-fundamentals.md` for cipher and hash algorithm guidance
- `cicd-devsecops` skill for secret management in the pipeline
- `multi-tenant-saas-architecture` skill for per-tenant cert strategy
- `nextjs-app-router` and `php-modern-standards` for app-layer HTTPS
  assumptions behind the edge proxy
