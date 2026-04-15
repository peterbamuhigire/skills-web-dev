# Fastify Backend (TypeScript-first)

Cross-ref: `typescript-effective` for strict-mode idioms; `nodejs-development` for
runtime patterns; `reliability-engineering` for shutdown, timeouts, retries.

## Why Fastify over Express

- First-class JSON Schema validation — no separate middleware.
- Hooks typed by lifecycle (`onRequest`, `preHandler`, `onSend`, `onError`, `onClose`).
- Plugin encapsulation — scoped decorators, no global middleware mutation.
- Logger built in (pino); structured JSON logs by default.
- ~2x the throughput of Express on identical work; matters above ~5k rps.

## Bootstrap

`apps/api/src/server.ts`:

```ts
import { buildApp } from "./app.js";

const app = await buildApp({ logger: { level: process.env.LOG_LEVEL ?? "info" } });

const port = Number(process.env.PORT ?? 3000);
const host = process.env.HOST ?? "0.0.0.0";

try {
  await app.listen({ port, host });
} catch (err) {
  app.log.fatal({ err }, "failed to start");
  process.exit(1);
}

const shutdown = async (signal: string) => {
  app.log.info({ signal }, "shutdown start");
  try {
    await app.close();
    process.exit(0);
  } catch (err) {
    app.log.error({ err }, "shutdown failed");
    process.exit(1);
  }
};

process.once("SIGTERM", () => void shutdown("SIGTERM"));
process.once("SIGINT", () => void shutdown("SIGINT"));
```

`apps/api/src/app.ts`:

```ts
import Fastify, { FastifyInstance, FastifyServerOptions } from "fastify";
import { TypeBoxTypeProvider } from "@fastify/type-provider-typebox";
import sensible from "@fastify/sensible";
import helmet from "@fastify/helmet";
import cors from "@fastify/cors";
import rateLimit from "@fastify/rate-limit";
import underPressure from "@fastify/under-pressure";
import { userRoutes } from "./routes/users.js";
import { errorHandler } from "./plugins/error-handler.js";
import { authPlugin } from "./plugins/auth.js";

export async function buildApp(opts: FastifyServerOptions = {}): Promise<FastifyInstance> {
  const app = Fastify({
    trustProxy: true,
    disableRequestLogging: false,
    requestIdLogLabel: "reqId",
    ajv: { customOptions: { removeAdditional: "all", useDefaults: true, coerceTypes: false } },
    ...opts,
  }).withTypeProvider<TypeBoxTypeProvider>();

  await app.register(helmet, { contentSecurityPolicy: false });
  await app.register(cors, { origin: process.env.CORS_ORIGIN?.split(",") ?? false });
  await app.register(sensible);
  await app.register(rateLimit, { max: 300, timeWindow: "1 minute" });
  await app.register(underPressure, {
    maxEventLoopDelay: 1000,
    maxHeapUsedBytes: 1024 * 1024 * 512,
    exposeStatusRoute: "/health",
  });

  await app.register(errorHandler);
  await app.register(authPlugin);
  await app.register(userRoutes, { prefix: "/v1/users" });

  return app;
}
```

## Validation — two choices

### TypeBox (preferred when you want zero runtime on the hot path)

```ts
import { Type, Static } from "@sinclair/typebox";
import type { FastifyPluginAsyncTypebox } from "@fastify/type-provider-typebox";

const UserParams = Type.Object({ id: Type.String({ format: "uuid" }) });
const UserBody = Type.Object({
  email: Type.String({ format: "email" }),
  name: Type.String({ minLength: 1, maxLength: 100 }),
});
type UserBody = Static<typeof UserBody>;

export const userRoutes: FastifyPluginAsyncTypebox = async (app) => {
  app.get("/:id", {
    schema: { params: UserParams, response: { 200: Type.Unknown() } },
    handler: async (req) => app.db.user.findUniqueOrThrow({ where: { id: req.params.id } }),
  });

  app.post("/", {
    schema: { body: UserBody, response: { 201: Type.Unknown() } },
    handler: async (req, reply) => {
      const created = await app.db.user.create({ data: req.body });
      return reply.code(201).send(created);
    },
  });
};
```

### Zod (preferred when schemas are shared with the frontend)

```ts
import { z } from "zod";
import { serializerCompiler, validatorCompiler, ZodTypeProvider } from "fastify-type-provider-zod";
import { UserCreate } from "@acme/schemas";

export const userRoutes = async (app: FastifyInstance) => {
  app.setValidatorCompiler(validatorCompiler);
  app.setSerializerCompiler(serializerCompiler);

  const typed = app.withTypeProvider<ZodTypeProvider>();

  typed.post("/", { schema: { body: UserCreate } }, async (req) => {
    return app.db.user.create({ data: req.body });
  });
};
```

Decision rule: TypeBox when API is internal and perf-sensitive; Zod when the same
schema is consumed by React Hook Form and tRPC.

## Hooks — the important five

```ts
app.addHook("onRequest", async (req) => {
  req.startTime = process.hrtime.bigint();
});

app.addHook("preHandler", async (req) => {
  if (req.routeOptions.config.auth !== false) {
    await req.jwtVerify();
  }
});

app.addHook("onResponse", async (req, reply) => {
  const dur = Number(process.hrtime.bigint() - req.startTime) / 1e6;
  req.log.info({ url: req.url, statusCode: reply.statusCode, ms: dur }, "req done");
});

app.addHook("onError", async (req, _reply, err) => {
  req.log.error({ err, reqId: req.id }, "request failed");
});

app.addHook("onClose", async () => {
  await app.db.$disconnect();
});
```

## Error handling plugin

```ts
import fp from "fastify-plugin";
import { ZodError } from "zod";
import { Prisma } from "@prisma/client";

export const errorHandler = fp(async (app) => {
  app.setErrorHandler((err, req, reply) => {
    if (err instanceof ZodError) {
      return reply.code(400).send({ error: "validation_error", issues: err.issues });
    }
    if (err instanceof Prisma.PrismaClientKnownRequestError && err.code === "P2002") {
      return reply.code(409).send({ error: "conflict", target: err.meta?.target });
    }
    if (err.statusCode && err.statusCode < 500) {
      return reply.code(err.statusCode).send({ error: err.message });
    }
    req.log.error({ err, reqId: req.id }, "unhandled");
    return reply.code(500).send({ error: "internal_error", reqId: req.id });
  });

  app.setNotFoundHandler((req, reply) =>
    reply.code(404).send({ error: "not_found", path: req.url })
  );
});
```

Rule: never leak the raw error message to clients on 5xx — reply with `reqId` and
have operators trace logs. Do surface 4xx messages; they're user-actionable.

## Logger discipline

```ts
// GOOD — structured fields, no string interpolation
req.log.info({ userId, orgId }, "user deleted");

// BAD — loses searchability, breaks log aggregation
req.log.info(`user ${userId} deleted in org ${orgId}`);
```

Redact secrets at logger construction:

```ts
Fastify({
  logger: {
    redact: {
      paths: ["req.headers.authorization", "req.headers.cookie", "*.password", "*.token"],
      censor: "[REDACTED]",
    },
  },
});
```

## OpenAPI generation

With Zod:

```ts
import { fastifySwagger } from "@fastify/swagger";
import { fastifySwaggerUi } from "@fastify/swagger-ui";
import { jsonSchemaTransform } from "fastify-type-provider-zod";

await app.register(fastifySwagger, {
  openapi: { info: { title: "Acme API", version: "1.0.0" } },
  transform: jsonSchemaTransform,
});
await app.register(fastifySwaggerUi, { routePrefix: "/docs" });
```

Snapshot the spec in CI; see `rest-plus-openapi.md`.

## Graceful shutdown

- Stop accepting new connections (`fastify.close` does this).
- Drain in-flight requests up to a deadline (default 500ms; bump for long handlers).
- Close DB pool, Redis, queue consumers — in that order.
- Kubernetes: `terminationGracePeriodSeconds: 60`, `preStop` sleep 10s so the
  load balancer deregisters before shutdown begins.

```ts
const shutdown = async () => {
  const timer = setTimeout(() => process.exit(1), 30_000).unref();
  await app.close();          // drains HTTP
  await app.db.$disconnect(); // closes DB
  await app.redis.quit();
  clearTimeout(timer);
};
```

## Anti-patterns

- `app.listen` without awaiting — masks startup errors.
- Registering plugins after routes — scope violations, silent overrides.
- Using Express-style `app.use(middleware)` — Fastify hooks are scoped; use them.
- `console.log` in handlers — bypasses structured logger and redaction.
- Catching and swallowing errors in handlers — let Fastify's error handler respond.
- Returning `reply.send()` and also returning a value — undefined behaviour; pick one.

## Decision rules

```text
Need RPC-style internal API     -> tRPC on top of Fastify
Need REST + public SDK          -> ts-rest contracts + Fastify handlers
High throughput (>5k rps/node)  -> TypeBox validator, avoid Zod on hot path
Background jobs alongside API   -> separate worker process; do not block event loop
WebSockets                      -> @fastify/websocket; budget memory for N connections
```
