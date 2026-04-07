---
name: api-design-first
description: Use when designing or building APIs — REST conventions, OpenAPI 3 spec-first workflow, versioning strategies, GraphQL decision guide, authentication patterns, rate limiting, and pagination. Covers PHP backend API patterns for multi-tenant SaaS.
---

# API Design First

## Overview

Design-first means writing the OpenAPI spec BEFORE writing code. The spec is the contract — it drives client SDKs, documentation, and server validation simultaneously.

**Core principle:** The spec is the source of truth. Code is the implementation of the spec, never the other way around.

---

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
GET    /api/v1/invoices/{id}/items   # Invoice line items
POST   /api/v1/invoices/{id}/items

# Actions (verbs only when they don't fit CRUD)
POST   /api/v1/invoices/{id}/send    # Send invoice by email
POST   /api/v1/invoices/{id}/void    # Void invoice
POST   /api/v1/payments/{id}/refund  # Refund payment
```

### HTTP Status Codes

| Code | When |
|---|---|
| 200 | Successful GET, PATCH, PUT |
| 201 | Successful POST (resource created) |
| 204 | Successful DELETE (no body) |
| 400 | Validation error (bad input) |
| 401 | Not authenticated |
| 403 | Authenticated but not authorised |
| 404 | Resource not found (or wrong tenant — use 404 not 403 to avoid enumeration) |
| 409 | Conflict (duplicate resource, optimistic lock failure) |
| 422 | Unprocessable entity (semantic validation failure) |
| 429 | Rate limit exceeded |
| 500 | Server error |

### Standard Response Envelope

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
    "fields": {
      "amount": ["The amount field is required."],
      "due_date": ["Must be a future date."]
    }
  }
}
```

---

## OpenAPI 3.1 Spec-First

### Minimal Working Spec

```yaml
openapi: 3.1.0
info:
  title: SaaS Platform API
  version: 1.0.0
  description: Multi-tenant SaaS REST API

servers:
  - url: https://api.example.com/v1
  - url: http://localhost/api/v1
    description: Local development

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
      required: [id, franchise_id, amount, status]
      properties:
        id:
          type: integer
          example: 1001
        franchise_id:
          type: integer
          example: 42
        amount:
          type: number
          format: decimal
          example: 1500.00
        status:
          type: string
          enum: [draft, sent, paid, void]
        created_at:
          type: string
          format: date-time

    Error:
      type: object
      properties:
        success:
          type: boolean
          example: false
        error:
          type: object
          properties:
            code:
              type: string
            message:
              type: string

paths:
  /invoices:
    get:
      summary: List invoices
      tags: [Invoices]
      parameters:
        - name: status
          in: query
          schema:
            type: string
            enum: [draft, sent, paid, void]
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: per_page
          in: query
          schema:
            type: integer
            default: 25
            maximum: 100
      responses:
        '200':
          description: Invoice list
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/Invoice'
        '401':
          description: Unauthorised
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

    post:
      summary: Create invoice
      tags: [Invoices]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [customer_id, amount, due_date]
              properties:
                customer_id:
                  type: integer
                amount:
                  type: number
                due_date:
                  type: string
                  format: date
      responses:
        '201':
          description: Invoice created
        '422':
          description: Validation error
```

---

## API Versioning

**Rule:** Version in URL path. Never in headers for public APIs (hard to test in browsers).

```
/api/v1/invoices   ← Current stable
/api/v2/invoices   ← New version (breaking changes)
```

### Versioning Strategy

```php
// routes.php — separate route files per version
require 'routes/v1.php';
require 'routes/v2.php';

// v2 adds new fields; v1 response stays unchanged
// Never remove fields from existing version without a new major version
```

**Deprecation policy:**
- Support N-1 versions (keep v1 alive when v2 launches)
- Add `Deprecation: true` and `Sunset: 2027-01-01` headers to deprecated endpoints
- Email API consumers 6 months before sunset

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
    $stmt->execute([hash('sha256', $key)]);
    return $stmt->fetch() ?: null;
}
```

```sql
CREATE TABLE api_keys (
    id           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    franchise_id BIGINT UNSIGNED NOT NULL,
    name         VARCHAR(100) NOT NULL,           -- "Mobile App", "Zapier Integration"
    key_hash     VARCHAR(64) NOT NULL UNIQUE,     -- SHA-256 of raw key; never store raw
    scopes       JSON,                             -- ["invoices:read", "payments:write"]
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
        return (array) $payload;
    } catch (\Exception $e) {
        return null;
    }
}
```

---

## Rate Limiting

```php
function checkRateLimit(int $franchiseId, int $userId, string $endpoint): void {
    $key = "rl:{$franchiseId}:{$userId}:" . date('YmdHi'); // Per minute
    $count = $redis->incr($key);
    if ($count === 1) $redis->expire($key, 60);

    if ($count > 100) {  // 100 req/min per user
        header('X-RateLimit-Limit: 100');
        header('X-RateLimit-Remaining: 0');
        header('Retry-After: ' . (60 - (time() % 60)));
        http_response_code(429);
        echo json_encode(['success' => false, 'error' => ['code' => 'RATE_LIMITED']]);
        exit;
    }

    header('X-RateLimit-Limit: 100');
    header('X-RateLimit-Remaining: ' . (100 - $count));
}
```

---

## Pagination

Standard offset pagination (see `api-pagination` skill for full patterns):

```php
// GET /api/v1/invoices?page=2&per_page=25
$page = max(1, (int) ($_GET['page'] ?? 1));
$perPage = min(100, max(1, (int) ($_GET['per_page'] ?? 25)));
$offset = ($page - 1) * $perPage;

$total = (int) $db->query("SELECT COUNT(*) FROM tbl_invoices WHERE franchise_id = $franchiseId")->fetchColumn();

$stmt = $db->prepare("SELECT * FROM tbl_invoices WHERE franchise_id = ? LIMIT ? OFFSET ?");
$stmt->execute([$franchiseId, $perPage, $offset]);
$data = $stmt->fetchAll();

echo json_encode([
    'success' => true,
    'data' => $data,
    'meta' => [
        'page' => $page,
        'per_page' => $perPage,
        'total' => $total,
        'last_page' => (int) ceil($total / $perPage),
    ]
]);
```

---

## GraphQL: When to Use vs REST

| Situation | Use |
|---|---|
| Mobile app needs flexible field selection | GraphQL |
| Multiple clients (web + mobile + third-party) with different data needs | GraphQL |
| Simple CRUD operations | REST |
| File uploads | REST |
| Public API / webhooks | REST |
| Real-time subscriptions alongside queries | GraphQL (subscriptions) |

**Decision rule:** Start with REST. Add GraphQL only when client field flexibility becomes a real maintenance burden (not hypothetical).

---

## PHP API Controller Pattern

```php
// api/v1/invoices.php
header('Content-Type: application/json');
header('X-Content-Type-Options: nosniff');

// 1. Auth
$user = authenticateRequest();
if (!$user) { http_response_code(401); echo json_encode(errorResponse('UNAUTHORIZED')); exit; }

// 2. Franchise scope — NEVER from request body
$franchiseId = $user['franchise_id'];

// 3. Route
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

function successResponse(mixed $data, array $meta = [], int $status = 200): void {
    http_response_code($status);
    echo json_encode(['success' => true, 'data' => $data, 'meta' => $meta]);
}

function errorResponse(string $code, string $message = '', int $status = 400): void {
    http_response_code($status);
    echo json_encode(['success' => false, 'error' => compact('code', 'message')]);
}
```

---

## Implementation Checklist

- [ ] OpenAPI spec written before code
- [ ] URL: plural nouns, versioned (`/api/v1/`)
- [ ] Response envelope: `{success, data, meta}` for success; `{success, error{code,message}}` for errors
- [ ] Tenant isolation: `franchise_id` from auth token, never from request
- [ ] 404 for wrong-tenant records (not 403 — prevents enumeration)
- [ ] Rate limiting headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After`
- [ ] Pagination: `page`, `per_page` (max 100), `meta.total`, `meta.last_page`
- [ ] API keys hashed (SHA-256) — raw key never stored
- [ ] Versioning: URL path, N-1 support, deprecation headers on sunset
- [ ] `Content-Type: application/json` and `X-Content-Type-Options: nosniff` on all responses
