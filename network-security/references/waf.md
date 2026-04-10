# Web Application Firewall (WAF)

Deploying and tuning a WAF on Debian 12 / Ubuntu 24.04 in front of multi-tenant
SaaS web applications — ModSecurity 3 on Nginx with the OWASP CRS.

## 1. What a WAF does

A WAF is an HTTP-aware filter that inspects requests (and optionally responses)
before they reach the application. Its job is to block known attack patterns
that represent the OWASP Top 10:

- SQL injection
- Cross-site scripting (XSS)
- Remote/local file inclusion
- Command injection
- Path traversal
- Insecure deserialisation, SSRF, XXE
- Credential stuffing and session abuse

Beyond signature blocking, a WAF gives you:

- **Virtual patching** — block a known CVE before the app team can deploy a
  code fix (hours, not days).
- **Rate limiting** — per-IP, per-endpoint, per-session throttles.
- **Bot and scraper control** — User-Agent, JA3, cookie-challenge heuristics.
- **Request logging** — centralised HTTP audit trail separate from app logs.

A WAF is **not** a substitute for secure code. It is a safety net and a
rapid-response lever.

## 2. WAF placement

Three common deployment points. You can combine them.

| Placement           | Example                            | Strengths                                | Trade-offs                            |
|---------------------|------------------------------------|------------------------------------------|---------------------------------------|
| Edge / CDN          | Cloudflare, Fastly, AWS WAF        | Absorbs DDoS, global anycast, easy setup | Managed rules opaque, egress cost, data sovereignty |
| Reverse proxy (self-hosted) | Nginx + ModSecurity, HAProxy + Coraza | Full control, low latency, audit access | You own tuning and updates            |
| In-application      | Coraza in Go, naxsi, app libs      | Zero extra hop, tight app context        | Bypassed if request reaches app another way |

For a self-managed SaaS on Debian/Ubuntu, the canonical stack is:

```text
Client -> (optional) Cloudflare -> Nginx + ModSecurity 3 + CRS -> PHP-FPM / Node / Go app
```

## 3. ModSecurity 3 on Nginx — install

ModSecurity 3 (libmodsecurity) is the modern rewrite. Use it, not the legacy
mod_security2 Apache module.

### Path A: Debian package (simplest)

Debian 12 and Ubuntu 24.04 ship the connector as a dynamic Nginx module:

```bash
sudo apt update
sudo apt install nginx libnginx-mod-http-modsecurity
```

Confirm the module is loaded:

```bash
nginx -V 2>&1 | tr ' ' '\n' | grep -i modsecurity
ls /etc/nginx/modules-enabled/ | grep modsecurity
```

If the package set is not available on your release, fall back to Path B.

### Path B: Manual build (when you need latest CRS or custom features)

```bash
sudo apt install -y git build-essential autoconf automake libtool \
    libcurl4-openssl-dev liblua5.3-dev libfuzzy-dev libssl-dev \
    libpcre2-dev libxml2-dev libyajl-dev pkg-config wget zlib1g-dev

# libmodsecurity core
cd /opt
sudo git clone --depth 1 -b v3/master https://github.com/owasp-modsecurity/ModSecurity
cd ModSecurity
sudo git submodule init && sudo git submodule update
sudo ./build.sh && sudo ./configure && sudo make -j$(nproc) && sudo make install

# Nginx connector
cd /opt
sudo git clone --depth 1 https://github.com/owasp-modsecurity/ModSecurity-nginx

# Rebuild Nginx with dynamic module
NGX_VER=$(nginx -v 2>&1 | awk -F/ '{print $2}')
wget https://nginx.org/download/nginx-${NGX_VER}.tar.gz
tar xf nginx-${NGX_VER}.tar.gz && cd nginx-${NGX_VER}
./configure --with-compat --add-dynamic-module=/opt/ModSecurity-nginx
make modules
sudo cp objs/ngx_http_modsecurity_module.so /etc/nginx/modules/
```

### Directory layout

```text
/etc/nginx/
├── modules-enabled/
│   └── 50-mod-http-modsecurity.conf   # load_module directive
├── modsec/
│   ├── main.conf                      # includes the below
│   ├── modsecurity.conf               # base config (from recommended)
│   ├── crs-setup.conf                 # CRS tuning
│   └── crs/                           # Core Rule Set repo
│       └── rules/*.conf
└── nginx.conf
```

### Base `modsecurity.conf`

Start from the upstream recommended file:

```bash
sudo mkdir -p /etc/nginx/modsec
sudo wget -O /etc/nginx/modsec/modsecurity.conf \
    https://raw.githubusercontent.com/owasp-modsecurity/ModSecurity/v3/master/modsecurity.conf-recommended
sudo wget -O /etc/nginx/modsec/unicode.mapping \
    https://raw.githubusercontent.com/owasp-modsecurity/ModSecurity/v3/master/unicode.mapping
```

Edit the critical directives:

```apache
# /etc/nginx/modsec/modsecurity.conf
SecRuleEngine              On          # DetectionOnly while tuning, then On
SecRequestBodyAccess       On
SecRequestBodyLimit        13107200    # 12.5 MB
SecRequestBodyNoFilesLimit 131072      # 128 KB for non-file fields
SecResponseBodyAccess      On
SecResponseBodyMimeType    text/plain text/html text/xml application/json
SecResponseBodyLimit       524288
SecAuditEngine             RelevantOnly
SecAuditLogRelevantStatus  "^(?:5|4(?!04))"
SecAuditLogParts           ABIJDEFHZ
SecAuditLogType            Serial
SecAuditLog                /var/log/nginx/modsec_audit.log
SecTmpDir                  /var/cache/modsecurity/tmp
SecDataDir                 /var/cache/modsecurity/data
SecDebugLog                /var/log/nginx/modsec_debug.log
SecDebugLogLevel           0
```

Create the cache directories:

```bash
sudo mkdir -p /var/cache/modsecurity/{tmp,data}
sudo chown -R www-data:www-data /var/cache/modsecurity
```

## 4. OWASP Core Rule Set (CRS 4)

The CRS is a free, community-maintained ruleset maintained by the OWASP CRS
project. It targets ModSecurity-compatible engines (ModSecurity 3, Coraza).

Install into the modsec directory:

```bash
cd /etc/nginx/modsec
sudo git clone --depth 1 -b v4.0/main https://github.com/coreruleset/coreruleset crs
sudo cp crs/crs-setup.conf.example crs-setup.conf
```

Write `/etc/nginx/modsec/main.conf` to chain everything together:

```apache
# Base engine config
Include /etc/nginx/modsec/modsecurity.conf

# CRS setup (must come before rules)
Include /etc/nginx/modsec/crs-setup.conf

# Site-specific exclusions BEFORE rules
Include /etc/nginx/modsec/exclusions-before.conf

# Core rules
Include /etc/nginx/modsec/crs/rules/*.conf

# Site-specific exclusions AFTER rules
Include /etc/nginx/modsec/exclusions-after.conf
```

### Paranoia levels

CRS rules are tagged PL1 through PL4. Higher paranoia = more rules active =
more false positives.

| PL | Intent                                | Typical false-positive rate |
|----|---------------------------------------|-----------------------------|
| 1  | Safe default, no tuning required      | Very low                    |
| 2  | Moderate; blocks common attack variations | Low to moderate           |
| 3  | Strict; for regulated / high-value apps | Moderate; requires tuning |
| 4  | Bank-grade; every request inspected aggressively | High; mandatory tuning programme |

Set in `crs-setup.conf`:

```apache
SecAction \
 "id:900000,\
  phase:1,\
  nolog,\
  pass,\
  t:none,\
  setvar:tx.blocking_paranoia_level=2,\
  setvar:tx.detection_paranoia_level=2"
```

Start at PL1, move to PL2 after a week of clean logs, then evaluate PL3 per
high-sensitivity route (admin, payment).

### Anomaly scoring model

CRS does not block per-rule by default. Each rule adds to an anomaly score.
Once the total crosses a threshold, the request is blocked. This lets you
surface the cumulative risk across many small signals.

```apache
setvar:tx.inbound_anomaly_score_threshold=5
setvar:tx.outbound_anomaly_score_threshold=4
```

Lower thresholds block faster but produce more false positives. Start at 5/4
(default) and only lower if you have strong tuning.

## 5. Nginx server block

```nginx
# /etc/nginx/sites-available/app.example.com
server {
    listen 443 ssl http2;
    server_name app.example.com;

    ssl_certificate     /etc/letsencrypt/live/app.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.example.com/privkey.pem;

    modsecurity          on;
    modsecurity_rules_file /etc/nginx/modsec/main.conf;

    # Real client IP behind Cloudflare (if used)
    set_real_ip_from 173.245.48.0/20;
    real_ip_header   CF-Connecting-IP;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Test and reload:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Verify ModSecurity is processing requests:

```bash
curl -sI "https://app.example.com/?id=1%27%20OR%201=1--"
# Expect 403 and an entry in /var/log/nginx/modsec_audit.log
```

## 6. Tuning false positives

The workflow is: **DetectionOnly -> review audit log -> write exclusions ->
flip to On**.

### Read the audit log

```bash
sudo tail -f /var/log/nginx/modsec_audit.log | less
```

Each transaction has parts A (headers), B (request body), H (audit summary),
and Z (terminator). Look for `Message:` lines and their `[id "NNNNNN"]` tags.

### Write a targeted exclusion

Exclude rule 942100 (SQLi libinjection) from the parameter `search` on the
`/catalog` endpoint only. Place in `exclusions-before.conf`:

```apache
SecRule REQUEST_URI "@beginsWith /catalog" \
    "id:1000,phase:1,pass,nolog,ctl:ruleRemoveTargetById=942100;ARGS:search"
```

To remove an entire rule globally (use sparingly):

```apache
SecRuleRemoveById 920350
```

To remove a rule tag (e.g. all of attack-rfi):

```apache
SecRuleRemoveByTag "attack-rfi"
```

### Exclude a whole known-good user

```apache
SecRule REMOTE_ADDR "@ipMatch 10.0.0.0/8" \
    "id:1010,phase:1,pass,nolog,ctl:ruleEngine=DetectionOnly"
```

## 7. Custom rules

ModSecurity rule grammar: `SecRule VARIABLES OPERATOR ACTIONS`.

### Block a specific SQLi payload

```apache
SecRule ARGS "@rx (?i:union\s+select)" \
    "id:100100,phase:2,deny,status:403,log,msg:'Custom SQLi union select',\
     tag:'attack-sqli'"
```

### Block a bad bot by User-Agent

```apache
SecRule REQUEST_HEADERS:User-Agent "@rx (?i:semrushbot|ahrefsbot|mj12bot)" \
    "id:100200,phase:1,deny,status:429,log,msg:'Aggressive crawler blocked'"
```

### Virtual patch for a CVE (example: path traversal in /legacy/)

```apache
SecRule REQUEST_URI "@contains /legacy/" \
    "id:100300,phase:1,chain,deny,status:403,msg:'Virtual patch CVE-2024-XXXX'"
    SecRule ARGS "@rx \.\./"
```

Rule IDs should follow the convention: your custom rules in 100000-199999, CRS
rules are 900000+.

## 8. Rate limiting in Nginx (complement to WAF)

ModSecurity does not replace Nginx's native rate limiting. Use both.

```nginx
http {
    limit_req_zone $binary_remote_addr zone=login:10m  rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api:10m    rate=30r/s;
    limit_conn_zone $binary_remote_addr zone=addr:10m;

    server {
        location = /api/login {
            limit_req  zone=login burst=5 nodelay;
            limit_conn addr 10;
            proxy_pass http://app_backend;
        }

        location /api/ {
            limit_req  zone=api burst=60 delay=30;
            limit_conn addr 50;
            proxy_pass http://app_backend;
        }
    }
}
```

`rate=5r/m` means five requests per minute per client IP. `burst` allows short
spikes, `nodelay` rejects beyond the burst rather than queuing, and `delay=N`
queues up to N before rejecting.

## 9. Coraza (Go alternative)

Coraza is a drop-in ModSecurity-compatible WAF written in Go. It runs CRS
rules natively and can be embedded in Go apps or used with Caddy and HAProxy.

When to consider Coraza:

- Your proxy is Caddy or HAProxy (no Nginx connector dependency).
- Your app is already Go and you want an in-process WAF without an external
  proxy hop.
- You want a memory-safe implementation in production.

Embedded example:

```go
import (
    "github.com/corazawaf/coraza/v3"
    coraza_http "github.com/corazawaf/coraza/v3/http"
)

waf, _ := coraza.NewWAF(coraza.NewWAFConfig().
    WithDirectivesFromFile("/etc/coraza/main.conf"))
handler := coraza_http.WrapHandler(waf, appHandler)
```

CRS files copy over unchanged. Coraza is under active development and covers
the majority of ModSecurity directives but not 100% — test your rule set
before switching.

## 10. Cloudflare WAF (edge)

Cloudflare WAF sits at the anycast edge. Benefits:

- Absorbs volumetric DDoS before it reaches your origin.
- Global managed rulesets (OWASP, Cloudflare, exploit DB) maintained for you.
- Bot management, JS challenge, Turnstile for human verification.
- Zero infrastructure to run.

Trade-offs:

- Managed rules are partly opaque — tuning means using their dashboard, not
  rule source.
- Egress bandwidth is metered on Business/Enterprise tiers.
- Data sovereignty: requests are decrypted at their edge, which may conflict
  with Uganda DPPA or EU GDPR residency requirements.
- If origin IP leaks, attackers bypass the edge entirely. Lock origin firewall
  to Cloudflare IPs only.

Origin firewall for Cloudflare-fronted sites:

```bash
# Fetch current IPs
curl -s https://www.cloudflare.com/ips-v4 | sudo tee /etc/nftables/cf-v4.list
```

Then in nftables, allow 443 only from that set.

## 11. Anti-patterns

- **Disabling rules you do not understand.** "Fixing" a false positive by
  turning off SQLi detection defeats the purpose. Write a targeted exclusion.
- **Running with `SecRuleEngine DetectionOnly` forever.** You are producing
  noise, not protection.
- **Paranoia level 1 with no follow-up.** PL1 only catches the crudest
  attacks. Plan to move to PL2 within 30 days.
- **No audit log monitoring.** If nothing ingests `modsec_audit.log`, you
  have a WAF but not a signal. Ship to a SIEM or at least a daily report.
- **WAF as substitute for secure code.** A WAF is a safety net. Input
  validation, parameterised queries, output encoding, and CSRF tokens still
  apply in the application.
- **Forgetting to update the CRS.** Pull `git pull` in the crs directory on a
  monthly schedule, or pin to a release tag and update quarterly.
- **Logging request bodies without PII redaction.** Audit logs may contain
  passwords and card numbers. Mask sensitive fields with
  `SecAction "phase:2,nolog,pass,ctl:hashEnforcement=On"` or redact at
  ingestion.
- **Trusting `X-Forwarded-For` without `set_real_ip_from`.** Otherwise rate
  limiting and rule exclusions key on the wrong address.

## 12. Cross-references

- `./firewalls.md` — L3/L4 host firewall sitting beneath the WAF
- `./ddos.md` — Volumetric and application flood mitigation layered with WAF
- `../SKILL.md` — Parent network-security skill
- `web-app-security-audit/` — Full web application security audit methodology
- `vibe-security-skill/` — Secure coding practices the WAF backstops
- `php-security/` — Application-layer hardening for PHP
- `llm-security/` — Prompt-injection and LLM-specific request filtering
