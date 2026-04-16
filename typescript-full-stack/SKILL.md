---
name: typescript-full-stack
description: Use when building end-to-end TypeScript applications — Node backend (Fastify),
  React/Next frontend, shared types via tRPC or Zod, monorepo with turborepo/nx, Prisma/Drizzle
  data layer, end-to-end type safety.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Full-Stack TypeScript

<!-- dual-compat-start -->
## Use When

- Use when building end-to-end TypeScript applications — Node backend (Fastify), React/Next frontend, shared types via tRPC or Zod, monorepo with turborepo/nx, Prisma/Drizzle data layer, end-to-end type safety.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `typescript-full-stack` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | Full-stack contract test plan | Markdown doc covering Fastify route + tRPC router + Prisma schema contract tests | `docs/ts/full-stack-tests.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Build and maintain apps where the same types flow from database to backend to frontend to mobile. Zero runtime type drift between layers.

**Prerequisites:** Load `typescript-effective` for production idioms. Load `typescript-mastery` for type-system depth.

## When this skill applies

- Greenfield TypeScript web app (React + Node).
- Unifying a split JS frontend + JS backend under TypeScript.
- Refactoring an Express/JS backend into a typed Fastify/TS backend while keeping the frontend running.
- Setting up a monorepo with shared types across packages.

## Architecture baseline

```text
+----------------------------------+
|  apps/web         (Next.js)      |
|  apps/mobile      (Expo RN)      |
|  apps/api         (Fastify)      |
|  packages/schemas (Zod)          |---> source of truth for types
|  packages/api-client (tRPC / fetch)
|  packages/db      (Prisma client)
|  packages/ui      (shadcn-like components)
|  packages/config  (tsconfig, eslint, prettier)
+----------------------------------+
```

- **Zod schemas** are the single source of truth; TS types are inferred.
- **tRPC** for internal APIs (no OpenAPI needed — types flow).
- **REST + OpenAPI** only when external clients consume the API. Use `ts-rest` or `zod-to-openapi`.
- **Prisma** for SQL-first data layer; **Drizzle** when you want SQL in view and finer control.
- **Auth** via Lucia, better-auth, or Clerk — not rolling your own.

## Monorepo with turborepo

```text
pnpm init -w
pnpm add -D turbo
```

`turbo.json` defines pipeline (`build`, `test`, `lint`, `type-check`) with caching. Remote cache on Vercel or self-hosted.

Rule: every package has its own `tsconfig.json` extending `packages/config/tsconfig.base.json`. Project references enable incremental typecheck.

See `references/monorepo-turborepo.md`.

## Fastify backend (TS-first)

```ts
import Fastify from "fastify";
import { z } from "zod";

const app = Fastify({ logger: true });

const Params = z.object({ id: z.string().uuid() });

app.get("/users/:id", async (req, reply) => {
  const { id } = Params.parse(req.params);
  const user = await db.user.findUnique({ where: { id } });
  if (!user) return reply.code(404).send({ error: "not_found" });
  return user;
});
```

Fastify beats Express for TS: first-class hooks, schema validation, plugin system, lifecycle typing. See `references/fastify-backend.md`.

## tRPC — end-to-end types without OpenAPI

```ts
// packages/api/src/router.ts
import { initTRPC } from "@trpc/server";
import { z } from "zod";

const t = initTRPC.create();

export const appRouter = t.router({
  user: t.router({
    byId: t.procedure
      .input(z.object({ id: z.string().uuid() }))
      .query(async ({ input }) => db.user.findUnique({ where: { id: input.id } })),
    create: t.procedure
      .input(UserCreate)
      .mutation(async ({ input }) => db.user.create({ data: input })),
  }),
});

export type AppRouter = typeof appRouter;
```

Frontend imports `AppRouter` type only. Runtime is fetch; types flow at compile time. Zero duplication. See `references/trpc-end-to-end.md`.

**When tRPC vs REST:**

```text
All clients are your own code, no public API            -> tRPC
External partners, third-party integrations, public SDK -> REST + OpenAPI
Mobile on old TS versions / no TS                       -> REST
GraphQL ecosystem in the org                            -> GraphQL (not covered here)
```

## REST + OpenAPI (when needed)

Use `ts-rest` or `zod-to-openapi` — define schemas once, generate OpenAPI spec automatically.

```ts
import { initContract } from "@ts-rest/core";

const c = initContract();

export const userContract = c.router({
  getUser: {
    method: "GET",
    path: "/users/:id",
    pathParams: z.object({ id: z.string().uuid() }),
    responses: { 200: UserSchema, 404: z.object({ error: z.literal("not_found") }) },
  },
});
```

See `references/rest-plus-openapi.md`.

## Data layer — Prisma or Drizzle

**Prisma:** schema-first, Prisma Client is fully typed, great DX. Ships with migration tool. Best for teams.

**Drizzle:** SQL-first, TypeScript-first. Queries look like SQL, no hidden abstractions. Best when you love SQL and want explicit control.

Decision rule:

```text
Want schema.prisma as source of truth, good migrations, team of mixed SQL skill -> Prisma
Want SQL-in-code visibility, complex queries, performance-critical               -> Drizzle
Postgres-only with advanced features (arrays, ranges, custom types)              -> Drizzle
MySQL primary, migrations managed alongside PHP app                              -> Prisma
```

See `references/prisma-vs-drizzle.md`.

## Zod schemas as the shared layer

```ts
// packages/schemas/src/user.ts
import { z } from "zod";

export const UserCreate = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  role: z.enum(["admin", "member", "viewer"]),
}).strict();

export const User = UserCreate.extend({
  id: z.string().uuid(),
  createdAt: z.coerce.date(),
});

export type UserCreate = z.infer<typeof UserCreate>;
export type User = z.infer<typeof User>;
```

Consumed by: API validation, Prisma custom types, React Hook Form, tRPC input, test fixtures. See `references/zod-shared-schemas.md`.

## Auth

- **Lucia** — session-based, database-backed, flexible. Good for first-party apps.
- **better-auth** — newer, feature-rich (MFA, OAuth, magic links).
- **Clerk** — hosted auth; trade cost for speed. Great for MVPs.
- **NextAuth/Auth.js** — incumbent; fine but DX can be rough.

Never roll password hashing, session storage, or OAuth flows yourself. See `references/auth-patterns.md`.

## Testing the full stack

- **Unit:** vitest in each package.
- **Integration:** vitest + test database (Testcontainers or pg-lite).
- **E2E:** Playwright for the web app.
- **Contract tests:** if you expose REST, snapshot the OpenAPI spec — breaking changes fail CI.
- **Type tests:** `expectTypeOf` for API client usage.

See `references/testing-full-stack.md`.

## Deployment — Docker for Node

Multi-stage Dockerfile, node-slim base, non-root user, pnpm deploy for prod-only deps:

```dockerfile
FROM node:22-slim AS base
RUN corepack enable && corepack prepare pnpm@latest --activate
WORKDIR /app

FROM base AS deps
COPY pnpm-lock.yaml pnpm-workspace.yaml package.json ./
COPY apps/api/package.json ./apps/api/
COPY packages/ ./packages/
RUN pnpm install --frozen-lockfile

FROM deps AS build
COPY . .
RUN pnpm --filter api build

FROM base AS prod
ENV NODE_ENV=production
USER node
WORKDIR /app
COPY --from=build --chown=node:node /app/apps/api/dist ./dist
COPY --from=deps --chown=node:node /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

See `references/docker-node-production.md`.

## Anti-patterns

- Duplicating types between frontend and backend ("I'll just type it again here").
- Trusting API responses without Zod validation on the client.
- Running migrations in app startup — run in CI or a separate migrate step.
- Sharing Prisma client across edge + Node runtime without a driver adapter.
- Importing server code into client code (mark server-only with `"use server"` or a runtime guard).
- Monorepo without remote build cache on CI — slow feedback.
- `any` on API boundaries.

## Read next

- `typescript-effective` — idioms.
- `typescript-mastery` — type system depth.
- `react-development` / `nextjs-app-router` — frontend.
- `nodejs-development` — Node runtime patterns.
- `postgresql-fundamentals` / `mysql-best-practices` — data layer specifics.

## References

- `references/monorepo-turborepo.md`
- `references/fastify-backend.md`
- `references/trpc-end-to-end.md`
- `references/rest-plus-openapi.md`
- `references/prisma-vs-drizzle.md`
- `references/zod-shared-schemas.md`
- `references/auth-patterns.md`
- `references/testing-full-stack.md`
- `references/docker-node-production.md`
