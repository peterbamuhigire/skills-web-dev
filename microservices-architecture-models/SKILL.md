---
name: microservices-architecture-models
description: The three NGINX Microservices Reference Architecture networking models
  — Proxy, Router Mesh, and Fabric — with a model selection decision tree, API gateway
  design, and service discovery patterns. Invoke during HLD for any microservices-based...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Microservices Architecture Models

<!-- dual-compat-start -->
## Use When

- The three NGINX Microservices Reference Architecture networking models — Proxy, Router Mesh, and Fabric — with a model selection decision tree, API gateway design, and service discovery patterns. Invoke during HLD for any microservices-based...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `microservices-architecture-models` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | Networking model decision record | Markdown doc per `skill-composition-standards/references/adr-template.md` covering Proxy / Router Mesh / Fabric pick | `docs/services/networking-model-adr.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Source

Stetson, C. (2017). *NGINX Microservices Reference Architecture*. NGINX Inc. — Three progressive networking models with source code (the Ingenious photosharing demo app).

---

## The Three Models at a Glance

The NGINX MRA defines three networking models that form a progression. Start with the Proxy Model and move up as your needs grow.

| Model | Complexity | Best For | NGINX Instances |
|-------|-----------|---------|----------------|
| **Proxy** | Low | Simple apps, monolith migration start | 1 cluster (ingress) |
| **Router Mesh** | Medium | Robust new apps, moderate-complexity legacy migration | 2 clusters (ingress + routing hub) |
| **Fabric** | High | Large secure apps, SSL/TLS everywhere, high-performance | 1 per container + ingress |

---

## Model 1: Proxy Model

**Architecture:**
```
Client → [NGINX Plus — API Gateway + Reverse Proxy] → Service Instances
```

**Capabilities:**
- Caching (static files + microcaching of dynamic content)
- Load balancing across service instances
- SSL/TLS termination (decrypts at gateway, plain HTTP internally)
- HTTP/2 support — multiplexes requests over a single TCP connection
- Rate limiting — DDoS protection, abuse prevention
- Dynamic service discovery via DNS (queries Consul/etcd/K8s/ZooKeeper)
- Active health checks (marks unhealthy instances out of pool)
- API gateway role — protocol translation, request aggregation

**When to use:**
- Starting a new microservices app.
- Converting a monolith to microservices (put NGINX in front of the monolith first, then extract services one by one).
- Simple to moderately complex applications.
- When inter-service load balancing at scale is not yet required.

**When to move up:**
- Heavy inter-service traffic needing efficient load balancing.
- Need for circuit breaker across all services.

**Implementation checklist:**
- [ ] Deploy NGINX Plus (or NGINX + Lua) as ingress controller
- [ ] Configure DNS resolver pointing to service registry
- [ ] Set `valid` parameter on resolver to control refresh rate (not DNS TTL)
- [ ] Define upstream blocks per service with health_check directive
- [ ] Configure SSL/TLS termination at gateway
- [ ] Enable rate limiting per IP and per tenant
- [ ] Set up microcaching for read-heavy endpoints

---

## Model 2: Router Mesh Model

**Architecture:**
```
Client → [NGINX Cluster 1 — Reverse Proxy] → [NGINX Cluster 2 — Router Mesh Hub] → Service Instances
```

**How it differs from Proxy Model:**
Cluster 1 handles external traffic (caching, SSL, rate limiting). Cluster 2 is a dedicated routing hub for inter-service communication — it handles service discovery, load balancing, health checks, and circuit breaking for all services.

**Capabilities (additional beyond Proxy):**
- Dedicated routing hub: a central communications point for all inter-service calls
- Active circuit breaker for every service passing through the hub
- Inter-service caching at the routing layer
- Works with Docker Swarm, Mesos DC/OS, and Kubernetes

**When to use:**
- Robust new application designs requiring efficient inter-service load balancing.
- Converting complex monolithic apps to microservices.
- When circuit breaking for all services is required but per-container NGINX is too complex.

**Implementation steps:**
1. Set up Cluster 1 (proxy server) as per Proxy Model.
2. Deploy Cluster 2 container as router mesh hub with orchestration adapter (K8s/Swarm/Mesos).
3. Tag services for load balancing: `LB_SERVICE=true` in container definition.
4. Configure services to route inter-service requests through the hub.
5. Hub auto-discovers services via registry events and updates routing table.

---

## Model 3: Fabric Model

**Architecture:**
```
Client → [NGINX Plus — Ingress] → [Container: NGINX Plus sidecar + Service] ←→ [Container: NGINX Plus sidecar + Service]
```

**The key difference:** NGINX Plus runs *inside every container*, acting as both forward and reverse proxy for each service. Services talk to `localhost` for all outbound requests; the local NGINX Plus instance handles service discovery, load balancing, and SSL/TLS.

**The persistent SSL/TLS mini-VPN effect:**
- First request between two service instances: full SSL/TLS handshake (9-step process).
- All subsequent requests: reuse the persistent connection.
- **Result:** In one production test, only 300 SSL/TLS handshakes for 100,000 inter-service transactions — 99.7% reduction in handshake overhead.

**Capabilities (additional beyond Router Mesh):**
- SSL/TLS encryption for *all* inter-service traffic, not just external
- Service discovery as a background task — endpoints available before request arrives (not per-request DNS lookup)
- Least Time load balancing — routes to fastest-responding instance
- Circuit breaker is a network property, not a code property — works across all languages uniformly
- Slowstart: recovering instances ramp up gradually, not overwhelmed

**Comparison — Normal Process vs Fabric Model:**

| Step | Normal Process | Fabric Model |
|------|---------------|-------------|
| Service discovery | Per request — wait for DNS | Background task — instant |
| Load balancing | Primitive DNS round-robin | Advanced (Least Time, session persistence) |
| SSL handshake | Every request (9 steps) | Once per pair, then persistent |
| Resilience | Manual per service | Built into network |

**When to use:**
- Government, healthcare, or financial apps (security mandate).
- High-load applications (> 100K daily inter-service transactions).
- Any app where inter-service SSL/TLS is required.
- Large apps with many service pairs communicating at high frequency.

**Service discovery flow in Fabric Model:**
```
Service A needs to call Service B
→ Service A sends request to localhost
→ Local NGINX Plus looks up Service B in its internal table
→ Table was built by async DNS resolver querying service registry (Consul/etcd/K8s/ZooKeeper)
→ NGINX Plus sends to Service B via persistent SSL connection (or creates one if first time)
→ Response returned directly
```

---

## Model Selection Decision Tree

```
Start here: How many services do you have?

1-5 services and simple inter-service calls?
  → Proxy Model

6-20 services with active circuit breaking needed?
  → Router Mesh Model

20+ services OR security mandate for inter-service SSL/TLS?
  → Fabric Model

Still on a monolith?
  → Start with Proxy Model in front of monolith, then use Strangler Fig
    to extract services and promote to Router Mesh as you grow
```

---

## API Gateway Design

In all three models, the ingress NGINX instance acts as the API gateway. Responsibilities:

| Responsibility | Implementation |
|---------------|---------------|
| SSL/TLS termination | NGINX `ssl_certificate` + `ssl_protocols TLSv1.2 TLSv1.3` |
| Rate limiting | `limit_req_zone` per IP and per tenant |
| Authentication | JWT validation at gateway (pass `X-User-Id` header downstream) |
| Routing | `location` blocks per service, or `proxy_pass` with service name |
| Load balancing | `upstream` block with `least_conn` or `least_time` |
| Caching | `proxy_cache_path` for static and microcached responses |
| HTTP/2 | `listen 443 ssl http2` |
| Health checks | `health_check uri=/health interval=3s` |
| Circuit breaker | `max_fails=1 fail_timeout=10s` in upstream block |
| Request aggregation | Lua module for multi-service fan-out + combine |

---

## Service Registry Options

| Registry | Protocol | Best For |
|----------|---------|---------|
| **Consul** | DNS + HTTP | Multi-datacenter, health checks built in |
| **etcd** | gRPC / HTTP | Kubernetes native, key-value |
| **Kubernetes DNS** | DNS (CoreDNS) | K8s-native deployments |
| **ZooKeeper** | TCP | Legacy Java/JVM ecosystems |

**NGINX DNS resolver config:**
```nginx
resolver 127.0.0.1:8600 valid=1s;  # Consul DNS on port 8600
# valid=1s means NGINX re-queries every second, ignoring DNS TTL
```

---

## Reverse Proxy & API Gateway Operations

### Nginx as Reverse Proxy

Complete production `server` block example:

```nginx
upstream api_backend {
    least_conn;
    server 10.0.1.10:3000 max_fails=3 fail_timeout=30s;
    server 10.0.1.11:3000 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate     /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_stapling on;
    ssl_stapling_verify on;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location / {
        proxy_pass http://api_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
        proxy_read_timeout 60s;
        proxy_send_timeout 60s;

        limit_req zone=api_rl burst=20 nodelay;
    }
}
```

### Nginx Rate Limiting

Zone definition (in `http` context, above server blocks):

```nginx
limit_req_zone $binary_remote_addr zone=api_rl:10m rate=10r/s;
limit_req_status 429;
```

Interpretation:

- `10m` zone — about 160,000 IP entries in memory
- `rate=10r/s` — 10 requests per second per IP sustained
- `burst=20 nodelay` — allow a burst of 20 queued requests, served immediately; excess returns 429

### Nginx SSL Termination

Let's Encrypt with Certbot: `sudo certbot --nginx -d api.example.com --agree-tos --email ops@example.com`. Auto-renewal via systemd timer `certbot.timer` (installed by the Certbot package).

HSTS and OCSP stapling directives already shown above. TLS 1.3 enabled by `ssl_protocols TLSv1.2 TLSv1.3`. Test rating with `ssllabs.com/ssltest` — target grade A+.

### Nginx Cache Configuration

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m
                 max_size=1g inactive=60m use_temp_path=off;

server {
    location /public/ {
        proxy_pass http://api_backend;
        proxy_cache api_cache;
        proxy_cache_valid 200 302 10m;
        proxy_cache_valid 404 1m;
        proxy_cache_bypass $http_cache_control;
        add_header X-Cache-Status $upstream_cache_status;
    }
}
```

Check cache hit rate via `X-Cache-Status` header (`HIT` / `MISS` / `BYPASS` / `EXPIRED`).

### Nginx Zero-Downtime Reload

- Validate config first: `sudo nginx -t` — exits non-zero on error
- Reload without dropping connections: `sudo nginx -s reload`
- Binary upgrade with no downtime: `kill -USR2 <master-pid>` to start a new master alongside, `kill -QUIT <old-master-pid>` once new workers are healthy
- Verify: `curl -I https://api.example.com` during reload; expect 100% success

### Kong API Gateway

Kong follows a service → route → plugin model. Declarative config (`deck` / `kong.yaml` format):

```yaml
_format_version: "3.0"
services:
  - name: user-service
    url: http://user-service:3000
    routes:
      - name: user-api
        paths:
          - /api/users
        strip_path: false
    plugins:
      - name: jwt
        config:
          claims_to_verify: [exp]
      - name: rate-limiting
        config:
          minute: 60
          policy: redis
          redis_host: redis
      - name: prometheus
```

Apply: `deck sync --state kong.yaml --kong-addr http://kong-admin:8001`.

### Traefik as Alternative

Traefik is Docker-native with automatic TLS. Example `docker-compose.yml` labels on a service:

```yaml
services:
  api:
    image: myorg/api:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`api.example.com`)"
      - "traefik.http.routers.api.entrypoints=websecure"
      - "traefik.http.routers.api.tls.certresolver=letsencrypt"
      - "traefik.http.middlewares.api-ratelimit.ratelimit.average=50"
      - "traefik.http.routers.api.middlewares=api-ratelimit"
```

Choice: Kong for full plugin ecosystem and enterprise features; Traefik for Docker/K8s-native auto-discovery; Nginx for raw throughput and low memory.

### HAProxy for TCP/HTTP Load Balancing

Example `haproxy.cfg` backend with health checks and sticky sessions:

```
backend app_backend
    balance leastconn
    cookie SERVERID insert indirect nocache
    option httpchk GET /health
    http-check expect status 200
    default-server inter 2s fall 3 rise 2
    server app1 10.0.1.10:3000 check cookie app1
    server app2 10.0.1.11:3000 check cookie app2

listen stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 10s
    stats auth admin:changeme
```

Stats page at `:8404/stats` shows live backend state — put it behind auth and a firewall.

---

**See also:**
- `microservices-fundamentals` — When to choose microservices, decomposition patterns
- `microservices-resilience` — Circuit breaker implementation, health check design
- `microservices-communication` — Service discovery deep dive, sync vs async
- `microservices-ai-integration` — AI gateway layered on top of this architecture
