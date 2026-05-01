# tRPC v11 End-to-End

Cross-ref: `typescript-effective` for inference discipline; `typescript-mastery` for
conditional-type tricks used in router merging; `react-development` for React Query
companion patterns.

## Why tRPC

Types flow from server to client without a schema file, codegen step, or transport
contract. The client imports only the `AppRouter` type — runtime remains plain HTTP.
Refactoring a procedure signature instantly surfaces every caller as a type error.

Use when all clients are yours and the TS build chain reaches them. Do not use for
public APIs, partner integrations, or non-TS clients; see `rest-plus-openapi.md`.

## Server setup

`packages/api/src/trpc.ts`:

```ts
import { initTRPC, TRPCError } from "@trpc/server";
import superjson from "superjson";
import { ZodError } from "zod";
import type { Context } from "./context.js";

const t = initTRPC.context<Context>().create({
  transformer: superjson,
  errorFormatter: ({ shape, error }) => ({
    ...shape,
    data: {
      ...shape.data,
      zodError: error.cause instanceof ZodError ? error.cause.flatten() : null,
    },
  }),
});

export const router = t.router;
export const publicProcedure = t.procedure;
export const mergeRouters = t.mergeRouters;

const isAuthed = t.middleware(({ ctx, next }) => {
  if (!ctx.session?.userId) throw new TRPCError({ code: "UNAUTHORIZED" });
  return next({ ctx: { ...ctx, session: ctx.session, userId: ctx.session.userId } });
});

export const authedProcedure = publicProcedure.use(isAuthed);

export const adminProcedure = authedProcedure.use(({ ctx, next }) => {
  if (ctx.session.role !== "admin") throw new TRPCError({ code: "FORBIDDEN" });
  return next();
});
```

## Context

`packages/api/src/context.ts`:

```ts
import type { FastifyRequest, FastifyReply } from "fastify";
import type { CreateFastifyContextOptions } from "@trpc/server/adapters/fastify";
import { db } from "@acme/db";
import { validateSession } from "./auth.js";

export async function createContext({ req, res }: CreateFastifyContextOptions) {
  const token = req.headers.authorization?.replace(/^Bearer\s+/i, "") ?? null;
  const session = token ? await validateSession(token) : null;
  return { req, res, db, session, requestId: req.id };
}

export type Context = Awaited<ReturnType<typeof createContext>>;
```

## Routers — feature-based, then merged

```ts
// packages/api/src/routers/user.ts
import { z } from "zod";
import { UserCreate, UserUpdate } from "@acme/schemas";
import { authedProcedure, publicProcedure, router } from "../trpc.js";
import { TRPCError } from "@trpc/server";

export const userRouter = router({
  byId: authedProcedure
    .input(z.object({ id: z.string().uuid() }))
    .query(async ({ ctx, input }) => {
      const user = await ctx.db.user.findUnique({ where: { id: input.id } });
      if (!user) throw new TRPCError({ code: "NOT_FOUND" });
      return user;
    }),

  list: authedProcedure
    .input(z.object({ cursor: z.string().uuid().nullish(), take: z.number().min(1).max(100).default(25) }))
    .query(async ({ ctx, input }) => {
      const items = await ctx.db.user.findMany({
        take: input.take + 1,
        cursor: input.cursor ? { id: input.cursor } : undefined,
        orderBy: { id: "asc" },
      });
      const hasMore = items.length > input.take;
      return { items: items.slice(0, input.take), nextCursor: hasMore ? items[input.take - 1]?.id : null };
    }),

  create: authedProcedure.input(UserCreate).mutation(async ({ ctx, input }) => {
    return ctx.db.user.create({ data: input });
  }),

  update: authedProcedure
    .input(z.object({ id: z.string().uuid(), patch: UserUpdate }))
    .mutation(async ({ ctx, input }) => {
      return ctx.db.user.update({ where: { id: input.id }, data: input.patch });
    }),
});
```

`packages/api/src/root.ts`:

```ts
import { router } from "./trpc.js";
import { userRouter } from "./routers/user.js";
import { orgRouter } from "./routers/org.js";
import { billingRouter } from "./routers/billing.js";

export const appRouter = router({
  user: userRouter,
  org: orgRouter,
  billing: billingRouter,
});

export type AppRouter = typeof appRouter;
```

Rule: export only the type, never the value, from the shared package consumed by the
client. The import `import type { AppRouter } from "@acme/api"` must tree-shake to
zero runtime bytes.

## Fastify adapter

```ts
import { fastifyTRPCPlugin } from "@trpc/server/adapters/fastify";
import { appRouter } from "@acme/api";
import { createContext } from "@acme/api/context";

await app.register(fastifyTRPCPlugin, {
  prefix: "/trpc",
  trpcOptions: {
    router: appRouter,
    createContext,
    onError: ({ error, path, ctx }) => {
      ctx?.req.log.error({ err: error, path }, "trpc error");
    },
  },
});
```

## Client — React with React Query

`packages/api-client/src/react.ts`:

```ts
import { createTRPCReact } from "@trpc/react-query";
import type { AppRouter } from "@acme/api";

export const trpc = createTRPCReact<AppRouter>();
```

Provider (in `apps/web`):

```tsx
"use client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { httpBatchLink, loggerLink } from "@trpc/client";
import superjson from "superjson";
import { useState } from "react";
import { trpc } from "@acme/api-client/react";

export function Providers({ children }: { children: React.ReactNode }) {
  const [qc] = useState(() => new QueryClient({
    defaultOptions: { queries: { staleTime: 30_000, retry: 1 } },
  }));
  const [client] = useState(() => trpc.createClient({
    links: [
      loggerLink({ enabled: (op) => process.env.NODE_ENV !== "production" || op.direction === "down" && op.result instanceof Error }),
      httpBatchLink({
        url: "/trpc",
        transformer: superjson,
        headers: () => {
          const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
          return token ? { authorization: `Bearer ${token}` } : {};
        },
      }),
    ],
  }));
  return (
    <trpc.Provider client={client} queryClient={qc}>
      <QueryClientProvider client={qc}>{children}</QueryClientProvider>
    </trpc.Provider>
  );
}
```

## Calling from components

```tsx
"use client";
import { trpc } from "@acme/api-client/react";

export function UserPage({ id }: { id: string }) {
  const user = trpc.user.byId.useQuery({ id });
  const update = trpc.user.update.useMutation({
    onSuccess: () => user.refetch(),
  });

  if (user.isPending) return <div>Loading</div>;
  if (user.isError) return <div>Error: {user.error.message}</div>;

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      update.mutate({ id, patch: { name: "Jane" } });
    }}>
      <div>{user.data.name}</div>
      <button disabled={update.isPending}>Rename</button>
    </form>
  );
}
```

## SuperJSON — when and why

SuperJSON preserves `Date`, `Map`, `Set`, `BigInt`, `undefined`, and `RegExp` across
the wire. Without it, `Date` becomes a string on the client and every consumer must
call `new Date(x)`. Cost: ~2x payload overhead for small responses. Accept it unless
measurements say otherwise.

## Subscriptions

For real-time use `wss://` with the `wsLink`:

```ts
// server
import { observable } from "@trpc/server/observable";
import { EventEmitter } from "node:events";

const ee = new EventEmitter();
export const eventRouter = router({
  onUserCreated: publicProcedure.subscription(() =>
    observable<{ id: string }>((emit) => {
      const on = (u: { id: string }) => emit.next(u);
      ee.on("user.created", on);
      return () => ee.off("user.created", on);
    })
  ),
});
```

```ts
// client
import { createWSClient, splitLink, wsLink, httpBatchLink } from "@trpc/client";

const wsClient = createWSClient({ url: "wss://api/trpc" });
links: [
  splitLink({
    condition: (op) => op.type === "subscription",
    true: wsLink({ client: wsClient, transformer: superjson }),
    false: httpBatchLink({ url: "/trpc", transformer: superjson }),
  }),
];
```

For high fan-out (thousands of clients), back subscriptions with Redis pub/sub or a
dedicated event bus. An in-process `EventEmitter` only scales to one node.

## Error handling patterns

```ts
const create = trpc.user.create.useMutation({
  onError: (err) => {
    if (err.data?.code === "CONFLICT") toast.error("Email already in use");
    else if (err.data?.zodError) setFormErrors(err.data.zodError.fieldErrors);
    else toast.error("Unexpected error");
  },
});
```

Server-side, throw `TRPCError` with the `code` appropriate to the semantics
(`BAD_REQUEST`, `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`, `CONFLICT`,
`TOO_MANY_REQUESTS`, `INTERNAL_SERVER_ERROR`).

## Anti-patterns

- Exporting the runtime router to the client package — ship only the type.
- Using `z.any()` on inputs — loses the whole point of tRPC.
- One giant router — split by feature, merge at the root.
- Procedures that both query and mutate — pick one; mutations must be idempotent-
  safe on the client's optimistic path.
- Calling tRPC from server components via the React hook — use `createCaller` with
  the server-side context to bypass HTTP.

## Decision rules

```text
Browser only, single backend                        -> httpBatchLink
Browser + mobile (RN)                               -> same, share the api-client pkg
Real-time updates (notifications, presence)        -> splitLink with wsLink
Streaming LLM responses                             -> httpBatchStreamLink
Server Components need to prefetch                  -> createCaller + hydrate
```
