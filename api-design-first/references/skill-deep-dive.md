# api-design-first Deep Dive

This file contains the extended guidance moved out of [../SKILL.md](../SKILL.md) so the skill entrypoint stays under the repository size limit.

## Included Sections

- `REST Conventions`
- `Security Headers (Mandatory on All Responses)`
- `OpenAPI 3.1 Spec-First`
- `API Versioning`
- `HTTP Caching (ETags)`
- `HATEOAS Links`
- `Authentication Patterns`
- `Rate Limiting`
- `Pagination`
- `Middleware Order`
- `Health Check Endpoint`
- `GraphQL: When to Use vs REST`
- `PHP API Controller Pattern`
- `Implementation Checklist`

## REST Conventions

### URL Structure

```
# Resource naming: plural nouns, kebab-case
GET    /api/v1/invoices              # List
POST   /api/v1/invoices              # Create
GET    /api/v1/invoices/{id}         # Show
PUT    /api/v1/invoices/{id}         # Full replace
PATCH  /api/v1/invoices/{id}         # Partial update
DELETE /api/v1/invoices/{id}         # Delete

# Nested resources (max 2 levels deep)
GET    /api/v1/invoices/{id}/items

# Actions (verbs only when they don't fit CRUD)
POST   /api/v1/invoices/{id}/send
POST   /api/v1/invoices/{id}/void
POST   /api/v1/payments/{id}/refund
```

**URI rules:** plural nouns, lowercase, hyphens not underscores, no trailing slashes, no verbs in path.

### HTTP Methods

| Method | Idempotent | Safe | Use |
|---|---|---|---|
| GET | ✅ | ✅ | Read |
| POST | ❌ | ❌ | Create |
| PUT | ✅ | ❌ | Full replace |
| PATCH | ❌ | ❌ | Partial update |
| DELETE | ✅ | ❌ | Delete |
| HEAD | ✅ | ✅ | Check existence (no body) |
| OPTIONS | ✅ | ✅ | CORS preflight, discover methods |

### HTTP Status Codes

| Code | When |
|---|---|
| 200 | Successful GET, PATCH, PUT |
| 201 | Successful POST (resource created) |
| 204 | Successful DELETE (no body) |
| 304 | Not Modified (ETag match — no body) |
| 400 | Malformed request, missing/invalid params |
| 401 | Not authenticated |
| 403 | Authenticated but not authorised |
| 404 | Resource not found (use 404 not 403 for wrong-tenant — prevents enumeration) |
| 405 | Method not allowed |
| 406 | Content negotiation failure (unsupported Accept type) |
| 409 | Conflict (duplicate resource, optimistic lock failure) |
| 422 | Semantic validation failure (valid JSON, invalid business rules) |
| 429 | Rate limit exceeded |
| 500 | Server error |
| 503 | Service unavailable (maintenance, overload) + `Retry-After` header |

### Standard Response Envelope (RFC 7807-inspired)

```json
// Success
{
  "success": true,
  "data": { "id": 123, "name": "Acme Corp" },
  "meta": { "page": 1, "per_page": 25, "total": 142 }
}

// Error
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The amount field is required.",
    "documentation_url": "https://api.example.com/errors#VALIDATION_ERROR",
    "fields": { "amount": ["Required"], "due_date": ["Must be future"] }
  }
}
```

---

## Security Headers (Mandatory on All Responses)

```php
header('Content-Type: application/json');
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: DENY');
header('Strict-Transport-Security: max-age=31536000; includeSubDomains');
header('Cache-Control: no-store');          // default; override per endpoint
header('Referrer-Policy: no-referrer');
```

**CORS — never use `*` with credentials:**
```php
$allowedOrigins = ['https://app.example.com', 'https://admin.example.com'];
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
if (in_array($origin, $allowedOrigins, true)) {
    header("Access-Control-Allow-Origin: {$origin}");
    header('Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS');
    header('Access-Control-Allow-Headers: Authorization, Content-Type, X-Request-ID');
    header('Access-Control-Allow-Credentials: true');
}
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}
```

---

## OpenAPI 3.1 Spec-First

Define every endpoint, schema, and error response in the spec before writing code.

```yaml
openapi: 3.1.0
info:
  title: SaaS Platform API
  version: 1.0.0
servers:
  - url: https://api.example.com/v1
  - url: http://localhost/api/v1
security:
  - bearerAuth: []
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  schemas:
    Invoice:
      type: object
      required: [id, tenant_id, amount, status]
      properties:
        id:          { type: integer, example: 1001 }
        tenant_id:   { type: integer, example: 42 }
        amount:      { type: number, format: decimal, example: 1500.00 }
        status:      { type: string, enum: [draft, sent, paid, void] }
        _links:      { $ref: '#/components/schemas/Links' }
    Links:
      type: object
      properties:
        self:    { type: object, properties: { href: { type: string } } }
        actions: { type: array, items: { type: object } }
paths:
  /invoices/{id}:
    get:
      parameters:
        - { name: id, in: path, required: true, schema: { type: integer } }
        - { name: If-None-Match, in: header, schema: { type: string } }
      responses:
        '200':
          headers:
            ETag:          { schema: { type: string } }
            Cache-Control: { schema: { type: string } }
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Invoice' }
        '304': { description: Not Modified }
        '404': { description: Not found }
```

---

## API Versioning

**Rule:** Version in URL path. Never in headers for public-facing APIs.

```
/api/v1/invoices   ← current stable
/api/v2/invoices   ← new version (breaking changes only)
```

### Breaking vs Non-Breaking Changes

| Non-Breaking (safe) | Breaking (requires new version) |
|---|---|
| Adding new optional fields | Removing fields |
| Adding new endpoints | Renaming fields |
| Adding new optional query params | Changing field types |
| Adding new enum values | Changing response structure |
| Bug fixes | Changing required params |

**Deprecation headers on old versions:**
```php
header('Deprecation: true');
header('Sunset: Thu, 01 Jan 2027 00:00:00 GMT');
header('Link: <https://api.example.com/v2/invoices>; rel="successor-version"');
```

**Policy:** Support N-1 versions. Email consumers 6 months before sunset.

---

## HTTP Caching (ETags)

```php
function sendWithEtag(array $data): void {
    $etag = '"' . md5(json_encode($data)) . '"';
    $clientEtag = $_SERVER['HTTP_IF_NONE_MATCH'] ?? '';

    if ($clientEtag === $etag) {
        http_response_code(304);
        header("ETag: {$etag}");
        exit;
    }

    header("ETag: {$etag}");
    header('Cache-Control: private, max-age=300');
    http_response_code(200);
    echo json_encode(['success' => true, 'data' => $data]);
}
```

Public, rarely-changing resources: `Cache-Control: public, max-age=3600`
Private / user-specific: `Cache-Control: private, max-age=300`
Never cache: `Cache-Control: no-store`

---

## HATEOAS Links

Include hypermedia links so clients discover available actions without hardcoding URLs:

```json
{
  "id": 1001,
  "status": "sent",
  "_links": {
    "self":    { "href": "/api/v1/invoices/1001" },
    "void":    { "href": "/api/v1/invoices/1001/void",    "method": "POST" },
    "payment": { "href": "/api/v1/invoices/1001/payments","method": "POST" },
    "items":   { "href": "/api/v1/invoices/1001/items",   "method": "GET" }
  }
}
```

Only include actions the current user is permitted to take — links act as implicit authorization hints.

---

## Authentication Patterns

### API Key (Server-to-Server)

```php
// Header: X-API-Key: sk_live_abc123
function authenticateApiKey(string $key): ?array {
    $stmt = $db->prepare('
        SELECT ak.*, f.id AS franchise_id
        FROM api_keys ak
        JOIN tbl_franchises f ON ak.franchise_id = f.id
        WHERE ak.key_hash = ? AND ak.is_active = 1
          AND (ak.expires_at IS NULL OR ak.expires_at > NOW())
    ');
    $stmt->execute([hash('sha256', $key)]);  // NEVER store raw key
    return $stmt->fetch() ?: null;
}
```

```sql
CREATE TABLE api_keys (
    id           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    franchise_id BIGINT UNSIGNED NOT NULL,
    name         VARCHAR(100) NOT NULL,
    key_hash     VARCHAR(64) NOT NULL UNIQUE,   -- SHA-256 of raw key
    scopes       JSON,                           -- ["invoices:read","payments:write"]
    last_used_at DATETIME,
    expires_at   DATETIME,
    is_active    TINYINT(1) DEFAULT 1,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### JWT (User Sessions / Mobile)

```php
// Authorization: Bearer <jwt>
function authenticateJwt(string $token): ?array {
    try {
        $payload = JWT::decode($token, new Key(JWT_SECRET, 'HS256'));
        if ($payload->exp < time()) return null;
        if ($payload->iss !== 'api.example.com') return null;  // Validate issuer
        return (array) $payload;
    } catch (\Exception $e) {
        return null;
    }
}
```

**JWT rules:** Short-lived access tokens (15–60 min) + long-lived refresh tokens. Never store secrets in payload. Always validate `iss`, `aud`, `exp`.

### OAuth2 Grant Flows

| Flow | Use Case |
|---|---|
| Authorization Code | Web apps requiring user consent |
| Client Credentials | Server-to-server (no user involved) |
| Resource Owner Password | Only when no other option; avoid |
| Implicit | Deprecated — do not use |

---

## Rate Limiting

```php
function checkRateLimit(int $franchiseId, int $userId): void {
    $key = "rl:{$franchiseId}:{$userId}:" . date('YmdHi');
    $count = $redis->incr($key);
    if ($count === 1) $redis->expire($key, 60);

    header('X-RateLimit-Limit: 100');
    header('X-RateLimit-Remaining: ' . max(0, 100 - $count));

    if ($count > 100) {
        header('Retry-After: ' . (60 - (time() % 60)));
        http_response_code(429);
        echo json_encode(['success' => false, 'error' => ['code' => 'RATE_LIMITED']]);
        exit;
    }
}
```

**Algorithms:** Token Bucket (allows bursts), Leaky Bucket (strict rate), Sliding Window (smooth + accurate). Use Redis for distributed rate state.

---

## Pagination

```php
// GET /api/v1/invoices?page=2&per_page=25
$page    = max(1, (int) ($_GET['page'] ?? 1));
$perPage = min(100, max(1, (int) ($_GET['per_page'] ?? 25)));
$offset  = ($page - 1) * $perPage;

// See api-pagination skill for cursor-based (large datasets)
```

**Response meta:** always include `page`, `per_page`, `total`, `last_page`.

---

## Middleware Order

Apply in this sequence for every request:

```
Logging → Panic Recovery → CORS → Request ID → Auth → Authorisation → Rate Limit → Handler
```

Add observability inside the handler path for critical writes:

```text
... → Validation → Business Logic → Audit/Event Emit → Response
```

---

## Health Check Endpoint

Expose `/health` and `/api/health` — used by load balancers and Kubernetes probes:

```php
// GET /health — returns 200 or 503
$checks = [
    'database' => checkDatabase(),
    'cache'    => checkRedis(),
];
$healthy = !in_array(false, $checks, true);
http_response_code($healthy ? 200 : 503);
echo json_encode(['status' => $healthy ? 'ok' : 'degraded', 'checks' => $checks]);
```

---

## GraphQL: When to Use vs REST

| Situation | Use |
|---|---|
| Mobile needs flexible field selection | GraphQL |
| Multiple clients with different data needs | GraphQL |
| Simple CRUD operations | REST |
| File uploads | REST |
| Public API / webhooks | REST |
| Real-time subscriptions | GraphQL (subscriptions) |

**Decision rule:** Start REST. Add GraphQL only when client field flexibility becomes a real maintenance burden.
**Security:** Load `graphql-security` skill whenever building or auditing GraphQL APIs.

---

## PHP API Controller Pattern

```php
header('Content-Type: application/json');
header('X-Content-Type-Options: nosniff');

$user = authenticateRequest();
if (!$user) { http_response_code(401); echo json_encode(errorResponse('UNAUTHORIZED')); exit; }

$franchiseId = $user['franchise_id'];   // NEVER from request body
$method = $_SERVER['REQUEST_METHOD'];
$id = $_GET['id'] ?? null;

match ([$method, $id !== null]) {
    ['GET',    false] => listInvoices($franchiseId),
    ['GET',    true]  => showInvoice($franchiseId, $id),
    ['POST',   false] => createInvoice($franchiseId),
    ['PATCH',  true]  => updateInvoice($franchiseId, $id),
    ['DELETE', true]  => deleteInvoice($franchiseId, $id),
    default           => httpError(405, 'METHOD_NOT_ALLOWED')
};
```

---

## Implementation Checklist

- [ ] OpenAPI spec written before code
- [ ] Consumers, latency budget, and trust boundaries defined
- [ ] URL: plural nouns, versioned (`/api/v1/`), no verbs
- [ ] Response envelope: `{success, data, meta}` / `{success, error{code,message,documentation_url}}`
- [ ] Tenant isolation: `franchise_id` from auth token, never from request
- [ ] 404 for wrong-tenant records (not 403 — prevents enumeration)
- [ ] Security headers on every response (HSTS, X-Content-Type-Options, X-Frame-Options)
- [ ] CORS: specific origins only — never wildcard with credentials
- [ ] ETags on cacheable resources; `304 Not Modified` on match
- [ ] Rate limiting headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After`
- [ ] Pagination: `page`, `per_page` (max 100), `meta.total`, `meta.last_page`
- [ ] API keys hashed (SHA-256) — raw key never stored
- [ ] JWT: validate `iss`, `aud`, `exp`; short-lived tokens; no secrets in payload
- [ ] Versioning: URL path, N-1 support, `Deprecation` + `Sunset` headers on sunset
- [ ] HATEOAS `_links` on resources (only permitted actions)
- [ ] Breaking change? Bump major version — never modify existing version
- [ ] `/health` endpoint for load balancer / Kubernetes probes
- [ ] Middleware order: Logging → Recovery → CORS → Auth → Rate Limit → Handler
- [ ] Idempotency strategy defined for retries on critical POST endpoints
- [ ] Audit events emitted for security-sensitive or financially material actions
