# REST Conventions

Back to [../SKILL.md](../SKILL.md).

Concrete URL, method, status-code, and envelope rules for every REST API this repository produces.

## URL structure

```text
# Resource naming: plural nouns, kebab-case
GET    /api/v1/invoices              # List
POST   /api/v1/invoices              # Create
GET    /api/v1/invoices/{id}         # Show
PUT    /api/v1/invoices/{id}         # Full replace
PATCH  /api/v1/invoices/{id}         # Partial update
DELETE /api/v1/invoices/{id}         # Delete

# Nested resources (max 2 levels deep)
GET    /api/v1/invoices/{id}/items

# Actions (verbs only when they do not fit CRUD)
POST   /api/v1/invoices/{id}/send
POST   /api/v1/invoices/{id}/void
POST   /api/v1/payments/{id}/refund
```

URI rules: plural nouns, lowercase, hyphens not underscores, no trailing slashes, no verbs in path unless the action does not fit CRUD.

## HTTP methods

| Method  | Idempotent | Safe | Use                               |
|---------|------------|------|-----------------------------------|
| GET     | yes        | yes  | Read                              |
| POST    | no         | no   | Create                            |
| PUT     | yes        | no   | Full replace                      |
| PATCH   | no         | no   | Partial update                    |
| DELETE  | yes        | no   | Delete                            |
| HEAD    | yes        | yes  | Check existence (no body)         |
| OPTIONS | yes        | yes  | CORS preflight, discover methods  |

## HTTP status codes

| Code | When                                                                                        |
|------|---------------------------------------------------------------------------------------------|
| 200  | Successful GET, PATCH, PUT                                                                  |
| 201  | Successful POST (resource created)                                                          |
| 204  | Successful DELETE (no body)                                                                 |
| 304  | Not Modified (ETag match — no body)                                                         |
| 400  | Malformed request, missing/invalid params                                                   |
| 401  | Not authenticated                                                                           |
| 403  | Authenticated but not authorised                                                            |
| 404  | Resource not found (use 404 not 403 for wrong-tenant — prevents enumeration)                |
| 405  | Method not allowed                                                                          |
| 406  | Content negotiation failure (unsupported Accept type)                                       |
| 409  | Conflict (duplicate resource, optimistic lock failure)                                      |
| 422  | Semantic validation failure (valid JSON, invalid business rules)                            |
| 429  | Rate limit exceeded                                                                         |
| 500  | Server error                                                                                |
| 503  | Service unavailable (maintenance, overload) + `Retry-After` header                          |

## Standard response envelope (RFC 7807-inspired)

```json
{
  "success": true,
  "data": { "id": 123, "name": "Acme Corp" },
  "meta": { "page": 1, "per_page": 25, "total": 142 }
}
```

```json
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

The error envelope is the canonical shape produced by this skill. Downstream frontend, mobile, and SDK skills consume it. See `error-model.md`.

## Pagination

```php
<?php
// GET /api/v1/invoices?page=2&per_page=25
$page    = max(1, (int) ($_GET['page'] ?? 1));
$perPage = min(100, max(1, (int) ($_GET['per_page'] ?? 25)));
$offset  = ($page - 1) * $perPage;
// See api-pagination skill for cursor-based (large datasets)
```

Response meta must always include `page`, `per_page`, `total`, `last_page`.

## Middleware order

Apply in this sequence for every request:

```text
Logging -> Panic Recovery -> CORS -> Request ID -> Auth -> Authorisation -> Rate Limit -> Handler
```

Add observability inside the handler path for critical writes:

```text
... -> Validation -> Business Logic -> Audit/Event Emit -> Response
```

## Health check endpoint

Expose `/health` and `/api/health` — used by load balancers and Kubernetes probes.

```php
<?php
// GET /health — returns 200 or 503
$checks = [
    'database' => checkDatabase(),
    'cache'    => checkRedis(),
];
$healthy = !in_array(false, $checks, true);
http_response_code($healthy ? 200 : 503);
echo json_encode(['status' => $healthy ? 'ok' : 'degraded', 'checks' => $checks]);
```

## PHP API controller pattern

```php
<?php
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
