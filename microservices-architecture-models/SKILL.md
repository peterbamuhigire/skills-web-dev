---
name: microservices-architecture-models
description: The three NGINX Microservices Reference Architecture networking models — Proxy, Router Mesh, and Fabric — with a model selection decision tree, API gateway design, and service discovery patterns. Invoke during HLD for any microservices-based system. Source: Stetson (NGINX MRA Ch. 1–4).
---

# Microservices Architecture Models

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

**See also:**
- `microservices-fundamentals` — When to choose microservices, decomposition patterns
- `microservices-resilience` — Circuit breaker implementation, health check design
- `microservices-communication` — Service discovery deep dive, sync vs async
- `microservices-ai-integration` — AI gateway layered on top of this architecture
