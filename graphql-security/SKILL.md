---
name: graphql-security
description: Use when building or auditing GraphQL APIs — comprehensive security hardening covering introspection exposure, DoS attacks (circular queries, alias overloading, batching), injection, authorization bypass, CSRF, SSRF, WebSocket hijacking, and the...
---

# GraphQL Security Hardening

## Overview

GraphQL's single-endpoint design and client-controlled query shape create a fundamentally different attack surface than REST. Standard WAFs, request-count rate limiting, and REST security checklists are all **insufficient**. Load this skill alongside `api-design-first` for every GraphQL build.

**Cardinal rule:** Authentication at the gateway. Authorization at the business logic layer (between resolvers and DB). Never in resolvers alone — resolver-level auth is missed on alternate query paths.

---

## Attack Surface Map

```
Single endpoint /graphql
  ├── Queries        → IDOR, info disclosure, recursive DoS
  ├── Mutations      → injection, CSRF, privilege escalation
  ├── Subscriptions  → WebSocket hijacking (CSWSH)
  ├── Arguments      → SQLi, OS injection, ReDoS, SSRF
  ├── Aliases        → brute-force bypass, alias overloading DoS
  ├── Fragments      → circular fragment DoS
  ├── Directives     → directive overloading DoS
  └── Introspection  → full schema exposure
```

**Detect GraphQL:** Send `{ __typename }` — returns `{"data":{"__typename":"Query"}}` on any implementation.

---

## Attack 1: Schema Exposure via Introspection

**Risk:** All types, fields, mutations, arguments, deprecated fields — full API blueprint — returned in a single request.

**Bypass when "disabled":** Many servers block `__schema` but not `__type`. Test: `{ __type(name:"Query") { name } }` — if data returns, introspection is only partially blocked. Also test via WebSocket if HTTP is blocked.

**Defense:**
- Disable introspection in production (`introspection: false` in server config)
- Block all meta-fields: `__schema`, `__type`, `__typename` (if not needed), `__field`, `__inputvalue`
- Disable field suggestions simultaneously — they reconstruct the schema without introspection
- Apply the same config to ALL endpoints AND all transports (HTTP + WebSocket)
- Never leave staging/dev environments publicly accessible

---

## Attack 2: Schema Reconstruction (Field Suggestions)

**Risk:** `"Did you mean X?"` hints allow full schema reconstruction without introspection. Tools like `Clairvoyance` automate this with a 30,000-word wordlist.

**Defense:**
- Disable field suggestions when disabling introspection — they are the same feature
- Graphene (Python): `graphql.pyutils.did_you_mean.MAX_LENGTH = 0`

---

## Attack 3: DoS — Circular / Recursive Queries

**Risk:** Cross-referencing types (A → B → A) allow exponential server load. One deeply nested query can crash servers. Circular fragments (`fragment A { ...B }` + `fragment B { ...A }`) crash non-spec-compliant implementations.

**Real-world:** GitLab (2019) — circular introspection query DoS. CVE-2022-30288 (Agoo Ruby).

**Defense:**
```python
# Graphene (Python) — depth and cost limits
from graphene import ObjectType
from graphql import build_schema
from graphql.validation import NoCircularFragmentsRule

# graphql-ruby
max_depth 10

# graphene-django
GRAPHENE = { "MIDDLEWARE": ["graphql_auth.middleware.JWTMiddleware"] }
depth_limit_validator(max_depth=20)
```

- Set `max_depth` 10–20 levels (lower for public APIs)
- Implement query cost analysis — assign numeric cost per field type, enforce `MAX_COST`
- Apply depth and cost limits to **introspection queries** too (GitLab's mistake was not doing this)
- Set query execution timeouts (e.g., 20 seconds)

---

## Attack 4: DoS — Alias Overloading and Field Duplication

**Risk:** A single HTTP request with 500 aliased mutations = 500 operations counted as 1 for rate limiting. Field duplication (`{ content content content }` × 1000) causes CPU exhaustion — server resolves each copy but returns only one.

**Real-world:** Magento (April 2021) — unauthenticated alias-based DoS.

**Defense:**
- Custom middleware: count aliases per request document; enforce a maximum (e.g., 10)
- Custom middleware: count total field occurrences; reject excessive duplication
- Query cost analysis catches both
- HTTP body size limit at the proxy/WAF layer

---

## Attack 5: DoS — Array-Based Query Batching

**Risk:** Some servers accept `[{"query":"..."}, {"query":"..."}, ...]` — an array of queries in one HTTP request. Sending 10,000 queries in one array bypasses all request-count rate limiting.

**Real-world:** WPGraphQL (April 2021) — batching enabled by default with no controls.

**Defense:**
- Disable array batching if unused. Graphene: `batch=False`
- If needed, enforce maximum batch size (e.g., 10 queries)
- Use `GraphQL Cop` to audit: `python3 graphql-cop.py -t http://target/graphql`

---

## Attack 6: Directive Overloading

**Risk:** Stuffing thousands of non-existent directives into a query (`@a@b@c@d@e...`) exhausts the query parser — can crash servers before any resolver executes.

**Defense:**
- Enforce maximum directive count per request (custom middleware)
- Set HTTP body size limit at the reverse proxy (Nginx `client_max_body_size`)

---

## Attack 7: Authentication Bypass — Brute Force via Aliases

**Risk:** Alias batching sends hundreds of login attempts as one HTTP request, bypassing per-request rate limits.

```graphql
mutation {
  a1: login(username:"admin", password:"password1") { token }
  a2: login(username:"admin", password:"password2") { token }
  # ... 500 more
}
```

**Tool:** `CrackQL` automates alias-based brute force using CSV wordlists.

**Defense:**
- Rate-limit at the **operation level**: count auth attempts per user/IP across all aliases in one document
- Account lockout after N failed attempts
- Alias limit middleware (see Attack 4)
- Disable batching on auth endpoints entirely

---

## Attack 8: Authorization Bypass — Multiple Query Paths

**Risk:** GraphQL often exposes multiple paths to the same object type. Authorization on `pastes` doesn't protect `readAndBurn` if it returns the same `PasteObject`. Attackers use `graphql-path-enum` to find unprotected paths.

**Real-world:** GitLab (private notes via GraphQL bypassed REST restrictions, CVE-2019-15576). Shopify (staff modifying customer emails, HackerOne #980511).

**Defense:**
- Implement authorization in the **business logic layer** (between resolvers and DB) — not in individual resolvers
- Audit all paths to sensitive types: `graphql-path-enum -i introspection.json -t TargetType`
- Test with all privilege levels: anonymous, user, staff, admin — attempt cross-account access
- GraphQL Shield: set `fallbackRule` to `deny` (default is `allow` — a trap)

---

## Attack 9: SQL Injection via GraphQL Arguments

**Risk:** GraphQL type checking only validates scalar type (String/Int), not content. String arguments passed into SQL without parameterization are injectable.

**Real-world:** Apache SkyWalking (CVE-2020-9483) — `getLinearIntValues(metric:{id:"..."})`.

**Defense:**
- Parameterized queries / prepared statements only — never string-concatenate user arguments into SQL
- Validate and sanitize all resolver input before any DB operation
- Never expose raw database errors to clients

---

## Attack 10: OS Command Injection

**Risk:** Resolvers passing arguments to shell functions are exploitable. High-risk field names: `system`, `debug`, `diagnostics`, `execute`, `run`, `update`.

**Defense:**
- Never use user-controlled input in shell commands
- Use library APIs instead of shell (e.g., `psutil` not `ps`)
- Whitelist allowed characters for any argument touching system calls
- Run the application as an unprivileged OS user

---

## Attack 11: CSRF via GraphQL Mutations

**Risk:** Servers accepting mutations via POST with `application/x-www-form-urlencoded` or via GET are forgeable from any HTML page. Victim visits attacker page → form auto-submits → mutation executes as victim.

**Real-world:** GitLab (March 2021, HackerOne #1122408) — GET-based mutations bypassed X-CSRF-Token.

**Defense:**
- **Require `Content-Type: application/json`** on all GraphQL requests — reject `application/x-www-form-urlencoded` and `text/plain`
- Disable GET-based mutations
- Implement anti-CSRF tokens (also on GET requests if GET queries are enabled)
- Set `SameSite=Strict` on session cookies
- Enforce strict CORS allowed origins

---

## Attack 12: Cross-Site WebSocket Hijacking (CSWSH)

**Risk:** JavaScript can open WebSocket connections to any origin without CORS restrictions. If the server doesn't validate the `Origin` header on the WebSocket handshake, attacker pages can subscribe to real-time events using the victim's session cookies.

**Defense:**
- Validate the `Origin` header on every WebSocket handshake using **exact string match** (substring matching is bypassable: `example.com.attacker.net` contains `example.com`)
- Use JWT in the WebSocket message payload for auth — not cookies
- Include anti-CSRF tokens in the WebSocket handshake URL
- Set `SameSite=Strict` cookies

---

## Attack 13: Server-Side Request Forgery (SSRF)

**Risk:** Mutations/queries that accept URL arguments may be redirected to internal services, private IP ranges, or cloud metadata endpoints (`169.254.169.254` → AWS IAM credentials).

**High-risk argument names:** `url`, `host`, `ip`, `domain`, `site`, `fetch`, `remote_url`, `target`

**Defense:**
- Allow-list expected domains/protocols for URL arguments
- Block private IP ranges (`10.x.x.x`, `172.16.x.x`, `192.168.x.x`) in URL arguments
- Network segmentation: application server should not reach internal services unnecessarily

---

## Attack 14: Stored XSS via Mutations

**Risk:** Mutation accepting HTML/JS content stores it; when other users view the data it executes in their browser.

**Defense:**
- HTML-encode all output rendered in HTML
- Implement Content Security Policy (CSP) header
- Validate file upload content and type (magic bytes, not client `Content-Type`)
- Keep GraphQL IDE dependencies updated (CVE-2021-41249 — reflected XSS in GraphQL Playground)

---

## GraphQL-Aware Rate Limiting

Standard request-count limits are **insufficient** for GraphQL. Layer all of these:

| Control | Implementation | Limit |
|---|---|---|
| Query depth | `max_depth` server config | 10–20 levels |
| Query cost | Assign cost per field, enforce `MAX_COST` | Set per app |
| Aliases | Custom middleware: count aliases per document | ≤ 10 |
| Array batch size | Limit queries per batch array | ≤ 10 |
| Execution timeout | Server + Nginx timeout | 20–60s |
| Body size | Nginx `client_max_body_size` | 100KB–1MB |
| Auth operations | Per-user attempt count across all aliases | 5/min |

**Strongest defense: Automatic Persisted Queries (APQ)** — clients register query hashes; server only executes pre-approved queries. Unknown queries are rejected. Supported by Apollo GraphQL.

---

## Information Disclosure Controls

- Never expose raw database errors — catch and return generic messages
- Disable debug mode and stack traces in production
- Disable `extensions.tracing` (reveals per-resolver timing — useful to attackers)
- Remove or password-protect GraphQL IDE endpoints (`/graphiql`, `/playground`) in production
- Ensure ALL endpoints have the same config — developers often secure `/graphql` but forget `/api/graphql` or `/graphql/v2`
- Avoid GET-based queries: URLs appear in server logs, browser history, and `Referer` headers

---

## Security Hardening Checklist

### Schema / Introspection
- [ ] Introspection disabled in production (all meta-fields, all transports)
- [ ] Field suggestions disabled
- [ ] GraphQL IDEs (`/graphiql`, `/playground`) removed or restricted in production
- [ ] Non-production environments not publicly accessible

### Denial of Service
- [ ] Query depth limit: 10–20 levels
- [ ] Query cost analysis with `MAX_COST` threshold
- [ ] Alias limit per document (≤ 10)
- [ ] Array batching disabled or limited (≤ 10)
- [ ] Execution timeout set (server + proxy)
- [ ] HTTP body size limit at proxy
- [ ] DoS controls applied to introspection queries too

### Authentication
- [ ] JWT signature verified on every request; `alg: "none"` rejected
- [ ] No secrets in JWT payload
- [ ] Operation names NOT used as auth allow-lists (they are client-controlled)
- [ ] Auth operations rate-limited at operation level (counts across aliases)
- [ ] Account lockout after repeated auth failures

### Authorization
- [ ] Authorization in business logic layer, not resolver layer
- [ ] All paths to sensitive types audited (`graphql-path-enum`)
- [ ] Tested at all privilege levels (anonymous, user, staff, admin)
- [ ] GraphQL Shield `fallbackRule` set to `deny`

### Injection
- [ ] All resolver input validated and sanitized before DB/system operations
- [ ] Parameterized queries everywhere
- [ ] No user input in shell commands
- [ ] HTML output encoded
- [ ] File upload: type validated by content (magic bytes), not filename

### CSRF / Transport
- [ ] `Content-Type: application/json` enforced; URL-encoded POST rejected
- [ ] Mutations disabled over GET
- [ ] Anti-CSRF tokens implemented
- [ ] `SameSite=Strict` or `Lax` on session cookies
- [ ] CORS: exact origin matching (not substring)

### WebSocket (Subscriptions)
- [ ] `Origin` header validated on WebSocket handshake (exact match)
- [ ] Token-based auth for WebSocket (JWT in message, not cookies)

### Information Disclosure
- [ ] Database errors caught and suppressed before client response
- [ ] Debug mode and stack traces disabled in production
- [ ] `extensions.tracing` disabled in production
- [ ] Same config on ALL GraphQL endpoints and transports

---

## Security Testing Tools

| Tool | Purpose |
|---|---|
| **GraphQL Cop** | Automated audit (DoS, info disclosure, CSRF) |
| **InQL** | Schema extraction, query templates, circular query detection |
| **Clairvoyance** | Schema reconstruction via field suggestions |
| **CrackQL** | Alias-based brute force (passwords, IDOR, 2FA) |
| **BatchQL** | Detect array batching and CSRF exposure |
| **Graphw00f** | Fingerprint GraphQL implementation |
| **graphql-path-enum** | Enumerate all paths to a target object type |
| **Burp Suite + GraphQL Raider** | Intercept/replay GraphQL traffic |
| **SQLmap** | Automated SQL injection testing (`-r request.txt --dbms=sqlite`) |
| **DVGA** | `docker run -p 5013:5013 dvga` — local practice target |

---

## Sources

Aleks, N. & Farhi, D. — *Black Hat GraphQL* (No Starch Press, 2023); Johnson, P. — *Modern API Design* (2024) Ch.7–8; Gurbani, N. — *Mastering RESTful API Development with Go* (2024)
