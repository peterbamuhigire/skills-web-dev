# OpenAPI Spec-First Workflow

Back to [../SKILL.md](../SKILL.md).

The spec is the contract. Code implements the spec, never the other way around. The OpenAPI document is the artifact this skill produces — see the canonical template in `skill-composition-standards/references/openapi-contract.md`.

## Six-step design workflow

1. Define consumers, latency expectations, and trust boundaries.
2. Model resources and actions around business concepts, not controller names.
3. Write the OpenAPI contract, including auth, validation, errors, and pagination.
4. Prove tenancy, authorisation, and idempotency rules before implementation.
5. Design observability: request IDs, audit events, deprecation path, and rate-limit telemetry.
6. Validate that the API can evolve without breaking current consumers.

## OpenAPI 3.1 minimal skeleton

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

## Spec completeness checklist

The spec is complete when every item below is present:

- every endpoint lists its auth requirement (or documents `security: []` for public)
- every request body has a `schema` with `required` fields
- every response has content schemas for 2xx, 4xx, and 5xx outcomes
- every error response uses the shared error schema (not ad hoc objects)
- every endpoint lists rate-limit headers in its response headers
- examples are filled in (not placeholder `string` / `0` values)
- deprecated endpoints carry `deprecated: true` and a `x-sunset` extension

## Versioning

Rule: version in URL path. Never in headers for public-facing APIs.

```text
/api/v1/invoices   <- current stable
/api/v2/invoices   <- new version (breaking changes only)
```

### Breaking vs non-breaking changes

| Non-breaking (safe)            | Breaking (requires new version)  |
|--------------------------------|----------------------------------|
| Adding new optional fields     | Removing fields                  |
| Adding new endpoints           | Renaming fields                  |
| Adding new optional query params | Changing field types           |
| Adding new enum values         | Changing response structure      |
| Bug fixes                      | Changing required params         |

Deprecation headers on old versions:

```php
<?php
header('Deprecation: true');
header('Sunset: Thu, 01 Jan 2027 00:00:00 GMT');
header('Link: <https://api.example.com/v2/invoices>; rel="successor-version"');
```

Policy: support N-1 versions. Email consumers 6 months before sunset.

## HATEOAS links

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

Only include actions the current user is permitted to take — links act as implicit authorisation hints.

## HTTP caching (ETags)

```php
<?php
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

Cache-Control choice:

| Resource type                  | Header                                |
|--------------------------------|---------------------------------------|
| Public, rarely-changing        | `Cache-Control: public, max-age=3600` |
| Private / user-specific        | `Cache-Control: private, max-age=300` |
| Sensitive / mutable            | `Cache-Control: no-store`             |

## GraphQL vs REST decision

| Situation                                  | Use                   |
|--------------------------------------------|-----------------------|
| Mobile needs flexible field selection      | GraphQL               |
| Multiple clients with different data needs | GraphQL               |
| Simple CRUD operations                     | REST                  |
| File uploads                               | REST                  |
| Public API / webhooks                      | REST                  |
| Real-time subscriptions                    | GraphQL subscriptions |

Decision rule: start REST. Add GraphQL only when client field flexibility becomes a real maintenance burden. Load `graphql-security` skill whenever building or auditing GraphQL APIs.
