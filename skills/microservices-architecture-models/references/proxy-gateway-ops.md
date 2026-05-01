# Reverse-Proxy and API-Gateway Ops — Deep Dive

Companion reference for `microservices-architecture-models`. Covers Nginx, HAProxy, Kong, and Traefik operational depth that does not fit in `SKILL.md`.

## Nginx — Reload Semantics

Verbatim, nginx.org/en/docs/beginners_guide.html (fetched 2026-05-01):

> "Once the master process receives the signal to reload configuration, it checks the syntax validity of the new configuration file and tries to apply the configuration provided in it. If this is a success, the master process starts new worker processes and sends messages to old worker processes, requesting them to shut down. Otherwise, the master process rolls back the changes and continues to work with the old configuration. Old worker processes, receiving a command to shut down, stop accepting new connections and continue to service current requests until all such requests are serviced. After that, the old worker processes exit."

Operational sequence:

1. `sudo nginx -t` — validate; non-zero exit aborts.
2. `sudo nginx -s reload` — master spawns new workers, signals old workers to drain.
3. Verify with `curl -I https://api.example.com` during the window — expect 100% success.
4. Binary upgrade: `kill -USR2 <master-pid>` to start a new master alongside; `kill -QUIT <old-master-pid>` once new workers are healthy.

## Nginx — Rate-Limit Primitives

Verbatim, nginx.org/en/docs/http/ngx_http_limit_req_module.html (fetched 2026-05-01):

```
limit_req_zone key zone=name:size rate=rate [sync];
```

Context: `http`.

```
limit_req zone=name [burst=number] [nodelay | delay=number];
```

Contexts: `http`, `server`, `location`.

Verbatim example from the same page:

```nginx
http {
    limit_req_zone $binary_remote_addr zone=one:10m rate=1r/s;

    ...

    server {

        ...

        location /search/ {
            limit_req zone=one burst=5;
        }
    }
}
```

> "This example allows not more than 1 request per second on average, with bursts not exceeding 5 requests from a single IP address."

Companion modules to consult before authoring stricter limits:

- `ngx_http_limit_conn_module` — `limit_conn_zone` / `limit_conn` for per-key concurrent-connection caps.
- `ngx_http_upstream_module` — `server ... weight= max_fails= fail_timeout=` for passive health checks.
- `ngx_http_proxy_module` — `proxy_pass`, `proxy_set_header`.
- `ngx_http_log_module` — `access_log` / `error_log`. On Debian/Ubuntu use `/etc/logrotate.d/nginx` for rotation.

## HAProxy — Section Types

Verbatim, docs.haproxy.org/3.0/configuration.html (fetched 2026-05-01): the configuration uses `frontend`, `backend`, and `listen` (frontend + backend in one block). The `global` section "must be placed before other sections, though it may be repeated if necessary."

## HAProxy — Balance Algorithms

Named in the manual (verify per-keyword at authoring time):

| Algorithm | Behaviour (synthesis) |
|-----------|-----------------------|
| `roundrobin` | Sequential distribution across servers |
| `leastconn` | Routes to the server with fewest active connections |
| `source` | Hashes client source IP for sticky routing |
| `url_param` | Routes by named URL parameter |

The manual also lists `uri`, `hdr(...)`, `random`, `first`, `static-rr`. Default behaviour when `balance` is omitted must be confirmed from the manual section directly, not assumed.

## HAProxy — ACLs and Stick Tables

Pattern (synthesis — cite specific keywords from the manual at authoring):

```
frontend fe_main
    bind *:443 ssl crt /etc/haproxy/certs/
    acl is_api path_beg /api/
    acl is_admin path_beg /admin/
    use_backend be_api    if is_api
    use_backend be_admin  if is_admin
    default_backend be_web

backend be_api
    stick-table type ip size 1m expire 10m store http_req_rate(10s)
    http-request track-sc0 src
    http-request deny if { sc_http_req_rate(0) gt 100 }
    server api1 10.0.1.10:3000 check
    server api2 10.0.1.11:3000 check
```

Stick tables back HAProxy's circuit-breaker and rate-limit patterns; quote `stick-table`, `track-sc0`, and `sc_http_req_rate` syntax from the manual page directly.

## HAProxy — Hitless Reload

HAProxy 2.x+ supports the master-worker model with `-sf` (soft-stop existing PIDs) and `-x` (transfer listening sockets via stat socket). The exact flag syntax must be quoted from the management guide before being included in shipped runbooks.

## Kong Gateway — Service Entity

Verbatim, developer.konghq.com/gateway/entities/service/ (fetched 2026-05-01):

> "Gateway Services represent the upstream services in your system. Services are the business logic components of your system that are responsible for processing and responding to requests."

Verbatim sample declarative configuration from the same page:

```yaml
_format_version: "3.0"
services:
  - name: example-service
    url: http://httpbin.konghq.com
```

## Kong Gateway — Core Entities

| Entity | Purpose |
|--------|---------|
| Service | Upstream API; holds `url`, timeouts, retries, TLS |
| Route | Match rules (paths, methods, hosts) selecting a Service |
| Plugin | Behaviour attached to Service / Route / Consumer / global |
| Consumer | Authenticated client identity |
| Upstream / Target | Load-balanced pool behind a Service |

## Kong — Plugin Families

Re-verify each name against the current Kong Hub at authoring time:

- Auth: `key-auth`, `jwt`, `oauth2`, `basic-auth`, `ldap-auth`, `openid-connect`.
- Traffic control: `rate-limiting`, `request-size-limiting`, `request-termination`, `response-ratelimiting`.
- Transformations: `request-transformer`, `response-transformer`.
- Observability: `prometheus`, `opentelemetry`, `file-log`, `http-log`.
- Security: `acl`, `bot-detection`, `cors`, `ip-restriction`.

## Kong — DB-less vs DB-backed

- DB-less: gateway loads `kong.yml` at startup; reconfigure via SIGHUP / admin endpoint. Best for git-ops.
- DB-backed: state in PostgreSQL, mutated through the Admin API.
- `deck sync --state kong.yaml --kong-addr http://kong-admin:8001` synchronises a Git-stored `kong.yml` against either mode.

Confirm the current reload mechanism (SIGHUP vs `/config` endpoint) against the latest stable Kong release before shipping runbooks. Also confirm OSS vs Enterprise plugin coverage on the Kong edition-comparison page.

## Traefik — HTTP Middlewares

Verbatim list, doc.traefik.io/traefik/reference/routing-configuration/http/middlewares/overview/ (fetched 2026-05-01):

`AddPrefix, BasicAuth, Buffering, Chain, CircuitBreaker, Compress, ContentType, DigestAuth, Errors, ForwardAuth, GrpcWeb, Headers, IPAllowList, InFlightReq, PassTLSClientCert, RateLimit, RedirectScheme, RedirectRegex, ReplacePath, ReplacePathRegex, Retry, StripPrefix, StripPrefixRegex.`

Rename note: the legacy `IPWhiteList` middleware has been renamed to `IPAllowList` in current Traefik (verbatim from the same page, fetched 2026-05-01). Use the new name in all new configs.

Verbatim from the same page:

> "middlewares that use the same protocol can be combined into chains to fit every scenario."

Premium (Traefik Hub API Gateway) middlewares, same page:

`APIKey, Distributed RateLimit, HMAC, JWT, LDAP, Token Introspection, Client Credentials, OIDC, OPA, WAF.`

## Traefik — Providers

Named providers include `file`, `KubernetesIngress`, `KubernetesCRD` (IngressRoute), `Docker`, `Consul`. Confirm provider names and CRD versions against the current providers page before authoring CRDs.

## Traefik — ACME / Let's Encrypt

Built-in resolver. Quote the `certificatesResolvers.<name>.acme` block (`email`, `storage`, `httpChallenge.entryPoint`) verbatim from doc.traefik.io/traefik/https/acme/ before including it in shipped configs.

## Decision Matrix — Kong vs Traefik vs Nginx-as-Gateway

| Concern | Nginx (as gateway) | Kong | Traefik |
|---------|--------------------|------|---------|
| Native dynamic config | Limited (modules / OpenResty) | Yes (Admin API + DB-less hot reload) | Yes (provider watch) |
| Plugin ecosystem | Lua via OpenResty | Large official + community | Built-in middleware set; Hub for premium |
| Auth (JWT / OAuth) out-of-box | Needs Lua module | Plugin | Built-in BasicAuth / DigestAuth / ForwardAuth + Hub for OIDC / JWT |
| Kubernetes ingress | nginx-ingress-controller | Kong Ingress Controller | Native (CRD / IngressRoute) |
| ACME built-in | No (use certbot) | Plugin | Built-in |
| Observability | Stub status / 3rd-party exporters | `prometheus` + `opentelemetry` plugins | Built-in Prometheus / OTel |
| Operator familiarity | Highest in industry | High in Kong shops | Growing in K8s shops |

Sizing rules:

- Single Debian VPS terminating TLS in front of a small SaaS app: Nginx wins on familiarity and footprint.
- Multi-team SaaS exposing many services with auth, rate-limit, and transformation needs: Kong (DB-less + deck) wins on plugin maturity.
- Kubernetes-first deployment with cert-manager-style automation: Traefik wins on providers and ACME.

Each row must be re-verified against the cited vendor page at authoring time.

## Open Verifications Before Shipping

1. HAProxy hitless-reload `-sf` / `-x` syntax — quote from `docs.haproxy.org/3.0/management.html`.
2. Kong DB-less reload mechanism — confirm SIGHUP vs Admin `/config` endpoint in latest stable release.
3. Traefik ACME block — quote from `doc.traefik.io/traefik/https/acme/`.
4. Kong OSS vs Enterprise plugin drift — verify against the edition-comparison page.
5. HAProxy default `balance` value — confirm from the manual section, not assumed.
