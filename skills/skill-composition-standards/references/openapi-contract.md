# OpenAPI Contract Template

The canonical API-contract artifact produced by `api-design-first`. Consumed by frontend, mobile, SDK, testing, and security skills.

## Required structure

```yaml
openapi: 3.1.0
info:
  title: <Service> API
  version: 1.0.0
  description: |
    <One paragraph on scope and ownership.>
  contact:
    name: <team>
    email: <team>@example.com

servers:
  - url: https://api.example.com/v1
    description: production
  - url: https://staging-api.example.com/v1
    description: staging

security:
  - bearerAuth: []

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    Error:
      type: object
      required: [code, message]
      properties:
        code:
          type: string
          enum: [INVALID_INPUT, NOT_FOUND, UNAUTHORISED, FORBIDDEN, RATE_LIMITED, INTERNAL]
        message: { type: string }
        details: { type: object, additionalProperties: true }

  responses:
    BadRequest:
      description: Request body failed validation
      content:
        application/json:
          schema: { $ref: '#/components/schemas/Error' }
          example: { code: INVALID_INPUT, message: "email is not a valid address" }
    Unauthorised:
      description: Missing or invalid credentials
      content: { application/json: { schema: { $ref: '#/components/schemas/Error' } } }
    RateLimited:
      description: Rate limit exceeded
      headers:
        Retry-After: { schema: { type: integer } }
      content: { application/json: { schema: { $ref: '#/components/schemas/Error' } } }

paths:
  /orders:
    post:
      summary: Create an order
      operationId: createOrder
      x-idempotent: true
      parameters:
        - name: Idempotency-Key
          in: header
          required: true
          schema: { type: string, minLength: 1, maxLength: 128 }
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: '#/components/schemas/OrderCreate' }
      responses:
        '201':
          description: Order created
          content: { application/json: { schema: { $ref: '#/components/schemas/Order' } } }
        '400': { $ref: '#/components/responses/BadRequest' }
        '401': { $ref: '#/components/responses/Unauthorised' }
        '429': { $ref: '#/components/responses/RateLimited' }
```

## Required elements

1. **Version in URL** — `/v1/...`, not just in the spec.
2. **Security scheme declared** on every non-public endpoint.
3. **Error schema referenced** from every 4xx/5xx response; never inline errors.
4. **Idempotency-Key header** required on every POST that mutates (has `x-idempotent: true` extension marker).
5. **Rate limit response documented** on every endpoint that can hit one.
6. **OperationId** present on every operation — clients use this.
7. **Examples** on every request and response schema.

## Error code set

Use exactly these codes; do not invent new ones without a cross-team review:

- `INVALID_INPUT` — 400
- `UNAUTHORISED` — 401
- `FORBIDDEN` — 403
- `NOT_FOUND` — 404
- `CONFLICT` — 409
- `RATE_LIMITED` — 429
- `INTERNAL` — 500
- `UNAVAILABLE` — 503

## Versioning policy

- Additive changes (new optional field, new endpoint) — same major version.
- Breaking changes — new major version (`/v2/...`), deprecate old for at least 6 months, document migration in the spec's `info.description`.

## Common failures

- **Inline error shapes** — every endpoint with its own bespoke error object. Clients can't normalise.
- **Unversioned URLs** — forces a big-bang migration for every change.
- **Missing idempotency** on POSTs — mobile retries double-post.
- **No rate-limit documentation** — clients can't implement backoff.
- **Security left as "see docs"** — auto-generated SDKs don't pick up the scheme.
- **OperationId collisions** — `getUser` used in 3 services; clients break.
