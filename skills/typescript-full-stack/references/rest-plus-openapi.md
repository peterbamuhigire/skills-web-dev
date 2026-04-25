# REST + OpenAPI with ts-rest and zod-to-openapi

Cross-ref: `api-design-first` for REST conventions; `typescript-effective` for type
discipline; `advanced-testing-strategy` for contract snapshot tests.

Use this stack when the API is consumed by external partners, non-TS clients, or
needs an SDK. Internal TS-only clients should prefer tRPC (see `trpc-end-to-end.md`).

## Two supported approaches

1. `ts-rest` — contract-first with Zod. Same contract object powers server, client,
   OpenAPI, and tests. Preferred for new services.
2. `zod-to-openapi` — annotate existing Zod schemas and emit OpenAPI. Preferred when
   migrating a Zod-heavy codebase without re-expressing every route as a contract.

## ts-rest contract

`packages/contracts/src/user.ts`:

```ts
import { initContract } from "@ts-rest/core";
import { z } from "zod";
import { User, UserCreate, UserUpdate } from "@acme/schemas";

const c = initContract();

const ProblemDetails = z.object({
  type: z.string().url(),
  title: z.string(),
  status: z.number().int(),
  detail: z.string().optional(),
  instance: z.string().optional(),
});

export const userContract = c.router(
  {
    list: {
      method: "GET",
      path: "/users",
      query: z.object({
        cursor: z.string().uuid().optional(),
        limit: z.coerce.number().int().min(1).max(100).default(25),
      }),
      responses: {
        200: z.object({ items: z.array(User), nextCursor: z.string().uuid().nullable() }),
      },
      summary: "List users (cursor-paginated)",
    },
    get: {
      method: "GET",
      path: "/users/:id",
      pathParams: z.object({ id: z.string().uuid() }),
      responses: { 200: User, 404: ProblemDetails },
    },
    create: {
      method: "POST",
      path: "/users",
      body: UserCreate,
      responses: { 201: User, 400: ProblemDetails, 409: ProblemDetails },
    },
    update: {
      method: "PATCH",
      path: "/users/:id",
      pathParams: z.object({ id: z.string().uuid() }),
      body: UserUpdate,
      responses: { 200: User, 404: ProblemDetails },
    },
    remove: {
      method: "DELETE",
      path: "/users/:id",
      pathParams: z.object({ id: z.string().uuid() }),
      body: c.noBody(),
      responses: { 204: c.noBody(), 404: ProblemDetails },
    },
  },
  {
    pathPrefix: "/v1",
    commonResponses: { 401: ProblemDetails, 429: ProblemDetails },
  }
);
```

## Fastify server implementation

`apps/api/src/routes/user.ts`:

```ts
import { initServer } from "@ts-rest/fastify";
import { userContract } from "@acme/contracts";
import type { FastifyInstance } from "fastify";

const s = initServer();

export const userRouter = s.router(userContract, {
  list: async ({ query, request }) => {
    const items = await request.server.db.user.findMany({
      take: query.limit + 1,
      cursor: query.cursor ? { id: query.cursor } : undefined,
      orderBy: { id: "asc" },
    });
    const hasMore = items.length > query.limit;
    return {
      status: 200,
      body: {
        items: items.slice(0, query.limit),
        nextCursor: hasMore ? items[query.limit - 1]!.id : null,
      },
    };
  },

  get: async ({ params, request }) => {
    const user = await request.server.db.user.findUnique({ where: { id: params.id } });
    if (!user) {
      return { status: 404, body: { type: "https://acme/err/not-found", title: "Not found", status: 404 } };
    }
    return { status: 200, body: user };
  },

  create: async ({ body, request }) => {
    try {
      const user = await request.server.db.user.create({ data: body });
      return { status: 201, body: user };
    } catch (err: any) {
      if (err.code === "P2002") {
        return { status: 409, body: { type: "https://acme/err/conflict", title: "Email in use", status: 409 } };
      }
      throw err;
    }
  },

  update: async ({ params, body, request }) => {
    const user = await request.server.db.user.update({ where: { id: params.id }, data: body });
    return { status: 200, body: user };
  },

  remove: async ({ params, request }) => {
    await request.server.db.user.delete({ where: { id: params.id } });
    return { status: 204, body: undefined };
  },
});

export async function registerRoutes(app: FastifyInstance) {
  const { registerRouter } = await import("@ts-rest/fastify");
  registerRouter(userContract, userRouter, app, {
    requestValidationErrorHandler: (err, _req, reply) => {
      reply.code(400).send({
        type: "https://acme/err/validation",
        title: "Validation failed",
        status: 400,
        detail: err.message,
      });
    },
  });
}
```

The handler's return type is checked against the contract's `responses`. A
misformatted body is a compile error.

## Generated client

```ts
import { initClient } from "@ts-rest/core";
import { userContract } from "@acme/contracts";

export const api = initClient(userContract, {
  baseUrl: process.env.API_URL ?? "https://api.acme.io",
  baseHeaders: {},
  throwOnUnknownStatus: true,
});

// call site — fully typed, discriminated by status
const res = await api.get({ params: { id } });
if (res.status === 200) {
  res.body; // User
} else {
  res.body; // ProblemDetails
}
```

## OpenAPI emission

```ts
// scripts/emit-openapi.ts
import { generateOpenApi } from "@ts-rest/open-api";
import { userContract } from "@acme/contracts";
import { writeFileSync } from "node:fs";

const doc = generateOpenApi(
  userContract,
  {
    info: { title: "Acme API", version: "1.0.0" },
    servers: [{ url: "https://api.acme.io" }],
    components: {
      securitySchemes: {
        bearer: { type: "http", scheme: "bearer", bearerFormat: "JWT" },
      },
    },
    security: [{ bearer: [] }],
  },
  { setOperationId: true, jsonQuery: true }
);

writeFileSync("openapi.json", JSON.stringify(doc, null, 2));
```

Serve Swagger UI from Fastify:

```ts
import swagger from "@fastify/swagger";
import swaggerUi from "@fastify/swagger-ui";

await app.register(swagger, { mode: "static", specification: { path: "./openapi.json", baseDir: "." } });
await app.register(swaggerUi, { routePrefix: "/docs" });
```

## zod-to-openapi (alternative path)

```ts
import { OpenAPIRegistry, OpenApiGeneratorV31 } from "@asteasolutions/zod-to-openapi";
import { z } from "zod";
import { extendZodWithOpenApi } from "@asteasolutions/zod-to-openapi";

extendZodWithOpenApi(z);

export const UserSchema = z.object({
  id: z.string().uuid().openapi({ example: "018f0c02-..." }),
  email: z.string().email(),
  name: z.string(),
}).openapi("User");

const registry = new OpenAPIRegistry();
registry.registerPath({
  method: "get",
  path: "/v1/users/{id}",
  request: { params: z.object({ id: z.string().uuid() }) },
  responses: {
    200: { description: "ok", content: { "application/json": { schema: UserSchema } } },
    404: { description: "not found" },
  },
});

const doc = new OpenApiGeneratorV31(registry.definitions).generateDocument({
  openapi: "3.1.0",
  info: { title: "Acme API", version: "1.0.0" },
});
```

## OpenAPI snapshot test

Catch unintentional contract drift in PRs.

```ts
// apps/api/test/openapi.snapshot.test.ts
import { describe, it, expect } from "vitest";
import { generateOpenApi } from "@ts-rest/open-api";
import { userContract } from "@acme/contracts";

describe("openapi", () => {
  it("matches the committed spec", () => {
    const doc = generateOpenApi(userContract, {
      info: { title: "Acme API", version: "1.0.0" },
    });
    expect(JSON.stringify(doc, null, 2)).toMatchFileSnapshot("./__snapshots__/openapi.json");
  });
});
```

Rule: the snapshot is reviewed on every PR. A red diff is a conscious API change —
add a changelog entry and consider versioning.

## Versioning

- Path prefix (`/v1`, `/v2`) for breaking changes.
- Additive changes (new optional fields, new endpoints) go into the current version.
- Never remove fields without a deprecation window (minimum 90 days for external
  consumers). Document in `deprecated: true` in the OpenAPI extension.

## Error body — Problem Details (RFC 9457)

```json
{
  "type": "https://acme.io/errors/insufficient-funds",
  "title": "Insufficient funds",
  "status": 402,
  "detail": "Wallet has 12.50, requested 100.00.",
  "instance": "/v1/wallets/018f.../debit",
  "code": "E_INSUFFICIENT_FUNDS"
}
```

Consistent error envelope → SDK generators, retries, and monitoring all work.

## Anti-patterns

- Hand-written OpenAPI YAML alongside hand-written handlers. Inevitably drifts.
- Returning 200 with `{ success: false }` — breaks HTTP semantics and caching.
- Leaking stack traces into the error body.
- Wildcards in CORS on authenticated endpoints.
- Skipping the snapshot test "just this once".

## Decision rules

```text
Greenfield public API with TS codebase       -> ts-rest contract
Migrating Zod-only backend, keep handlers    -> zod-to-openapi
Need multi-language SDKs                     -> OpenAPI -> openapi-generator or Speakeasy
Internal-only, all clients TS                -> switch to tRPC
gRPC or Connect shop                         -> this skill does not apply; use Connect
```
