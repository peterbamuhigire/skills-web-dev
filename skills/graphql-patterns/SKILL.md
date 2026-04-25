---
name: graphql-patterns
description: Use when designing, building, or operating GraphQL APIs with Apollo Server +
  TypeScript — covers schema-first SDL design, resolver architecture, DataLoader, JWT and
  directive-based authz, Relay cursor pagination, typed error payloads, federation v2,
  graphql-codegen, and production hardening (depth/complexity limits, timeouts, persisted
  queries). Pair with graphql-security for hostile-input defence.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# GraphQL Patterns (Apollo + TypeScript)
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Designing a new GraphQL API or migrating from REST
- Building Apollo Server + TypeScript with typed resolvers and clients
- Adopting Relay pagination, DataLoader, directive auth, or federation
- Hardening a GraphQL service for production

## Do Not Use When

- Pure REST/gRPC — use `api-design-first`
- Threat-modelling GraphQL against malicious input — load `graphql-security` first
- Single canonical UI shape, CDN caching dominant — REST is simpler

## Required Inputs

Domain entities + UI shapes; auth model (JWT/roles/tenants); federation needs; target clients and pagination style.

## Workflow

1. Draft SDL against real UI shapes before resolvers.
2. Model relationships in the schema, not in resolvers.
3. Wire `context` (auth + loaders) before the first resolver.
4. Add depth + complexity `validationRules` before the first public client.
5. Add graphql-codegen to CI before the schema has a second consumer.
6. Ship with `formatError` masking production stack traces.

## Quality Standards

- Lists are `[T!]!` unless partial failure is legal.
- Every mutation takes `input: XxxInput!` and returns a payload type.
- Every resolver is pure: reads `context`, calls services/loaders, returns the schema shape.
- Every relationship crossing uses DataLoader — no direct DB calls in nested resolvers.
- Production always has depth limit, complexity limit, error masking.

## Anti-Patterns

Monolithic `schema.js`/`index.js`; mixed auth patterns across resolvers; client-supplied `userId` trusted; introspection on with no cost analysis; bare `throw new Error`; `String` for dates.

## Outputs

`schema.graphql` + operations + generated TS; Apollo Server bootstrap; per-request DataLoader factory; `codegen.yml`; security baseline (depth/complexity/introspection/CORS/helmet).

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | GraphQL schema decision record | Markdown doc per `skill-composition-standards/references/adr-template.md` covering SDL design, resolver patterns, and N+1 mitigations | `docs/graphql/schema-adr.md` |
| Performance | Resolver performance budget | Markdown doc covering per-resolver latency budget and DataLoader strategy | `docs/graphql/resolver-budget.md` |

## References

- *Fullstack GraphQL* (TS + Apollo + React); *JavaScript Everywhere* — Adam D. Scott (O'Reilly, 2020).
- Apollo Server + Federation v2 docs; Relay cursor connection spec (`relay.dev/graphql/connections.htm`).
- Companion skills: `api-design-first`, `graphql-security`, `typescript-full-stack`, `nodejs-development`.
<!-- dual-compat-end -->

## Overview

GraphQL inverts REST: the client declares the shape, the server resolves. This kills endpoint proliferation at the cost of new problems (N+1, depth attacks, typed error plumbing). This skill prescribes a production-grade Apollo + TypeScript baseline that avoids those pitfalls by construction.

**Cardinal rule:** The schema is the contract. Design it first; every other layer derives from it.

---

## 1. Schema-First Design (SDL)

Order of work: UI shape → SDL types → DB model → resolvers. Never reverse this.

```graphql
scalar DateTime

type Note {
  id: ID!
  content: String!
  author: User!
  createdAt: DateTime!
  favoritedBy: [User!]!
}

type User {
  id: ID!
  username: String!
  notes(first: Int = 20, after: String): NoteConnection!
}

input CreateNoteInput { content: String! }
type CreateNotePayload { note: Note, errors: [UserError!]! }
type UserError { field: String, message: String! }

type Query {
  me: User
  note(id: ID!): Note
}

type Mutation {
  createNote(input: CreateNoteInput!): CreateNotePayload!
}
```

**Non-null rules:**

- `Note!` — never null. `[Note!]!` — list never null, no null elements (the default for collection queries).
- `[Note]` only when partial results are legal.
- Nullable-string like `description: String` is right when the domain allows absence; everywhere else a null is a latent bug.

**Input types are mandatory once a mutation has >2 scalar args.** Wrapping in an `input` lets you add fields later without changing the call site.

**Mutation payload types never return the bare entity.** Return `CreateNotePayload { note, errors }` so clients can surface validation errors as typed data (see §6).

**Interface vs union:**

- `interface` when variants share fields: `interface RepositoryOwner { login: String! }` → `User`, `Organization` both implement.
- `union` when variants share nothing: `union SearchResult = Issue | PullRequest | Repository`.

Clients discriminate with `__typename` + inline fragments — always request `__typename` on interface/union queries or Apollo client cache normalisation breaks.

**Custom scalars** — never `String` for dates. Bind `graphql-iso-date`'s `GraphQLDateTime` to the `DateTime` scalar. The resolver then receives a real `Date`, not an unvalidated string.

---

## 2. Resolvers

Canonical signature: `(parent, args, context, info)` — `parent` from parent resolver, `args` schema-typed, `context` per-request (built once), `info` AST (use for projection/cost, never for routing).

**Split resolvers per type.** One file per `Query.ts`, `Mutation.ts`, `Note.ts` (relationships), `User.ts`, `scalars.ts`.

```ts
// src/resolvers/Note.ts
import { NoteResolvers } from '../__generated__/graphql';
export const Note: NoteResolvers = {
  author:      (note, _a, { loaders }) => loaders.userById.load(note.author_id),
  favoritedBy: (note, _a, { loaders }) => loaders.usersByNoteId.load(note.id),
};
```

Thin root resolvers, relationship resolvers on the type. Apollo calls relationship resolvers *only when the client selects the field* — this is what makes "pay only for what you select" real.

---

## 3. Context Construction (where auth + loaders live)

```ts
// src/context.ts
import { readJwt } from './auth';
import { makeLoaders } from './loaders';

export type Context = {
  user: { id: string; roles: string[] } | null;
  loaders: ReturnType<typeof makeLoaders>;
  db: Db;
};

export async function buildContext({ req }: { req: IncomingMessage }): Promise<Context> {
  const user = readJwt(req.headers.authorization);
  return { user, loaders: makeLoaders(db), db };
}
```

Decode the JWT exactly once, then every resolver reads `context.user`. Never trust `args.userId`.

---

## 4. N+1 and DataLoader

**The problem:** `notes { author { username } }` hits the DB once per note. Logs show `SELECT user WHERE id = 1`, `... = 2`, `... = 2`, `... = 3`.

**The fix:** one `DataLoader` per join, per request.

```ts
// src/loaders.ts
import DataLoader from 'dataloader';

export function makeLoaders(db: Db) {
  return {
    userById: new DataLoader<string, User>(async (ids) => {
      const rows = await db.users.findByIds([...ids]);
      const map = new Map(rows.map((r) => [r.id, r]));
      return ids.map((id) => map.get(id)!); // ORDER MUST MATCH INPUT
    }),
    usersByNoteId: new DataLoader<string, User[]>(async (noteIds) => {
      const rows = await db.noteFavorites.findByNoteIds([...noteIds]);
      const grouped = groupBy(rows, 'noteId');
      return noteIds.map((id) => grouped[id] ?? []);
    }),
  };
}
```

**Two rules:** (1) the returned array must match the keys array by index; (2) the loader must be built per-request — sharing across requests leaks data between tenants.

**Per-request caching is the second win.** In circular traversals (notes → author → notes) the `Map`-backed cache means each `userById.load('u1')` hits the DB once.

**When not to use DataLoader:**

- After a mutation that needs fresh data — call `loaders.userById.clear(id)` or bypass.
- Non-ID-keyed lookups (filter + sort combinations) — the loader key space becomes combinatorial; prefer a thin service layer.
- Multi-gigabyte value shapes — the `Map` blows heap; move caching to Redis.

DataLoader is a *per-request* optimisation. It does not replace HTTP or Redis caching.

---

## 5. Auth and Authz

**JWT in the header, decoded once in `context`.** Both web and mobile clients set `Authorization: Bearer <token>`. Never sessions for a public GraphQL API — they collapse under mobile clients.

**Field-level authorisation — two patterns, pick one and hold it.**

**Code-based:**

```ts
import { AuthenticationError, ForbiddenError } from 'apollo-server-errors';
export const Mutation: MutationResolvers = {
  deleteNote: async (_, { id }, { user, db }) => {
    if (!user) throw new AuthenticationError('Session invalid');
    const note = await db.notes.byId(id);
    if (String(note.author_id) !== user.id) throw new ForbiddenError('Not your note');
    await db.notes.delete(id);
    return { ok: true };
  },
};
```

**Directive-based (declarative):**

```graphql
directive @auth(role: Role) on FIELD_DEFINITION | INPUT_FIELD_DEFINITION
type Mutation {
  publishNote(id: ID!, published: Boolean! @auth(role: ADMIN)): Note @auth
}
```

A custom `@auth` schema directive wraps `defaultFieldResolver`, inspects `context.user.roles`, and throws or proceeds. Put the directive implementation in one file; grep-readers see the rule on the field itself.

**Pitfalls:**

- Mixing both patterns → some paths are checked twice, some missed.
- `AuthenticationError` (unauthenticated) vs `ForbiddenError` (authenticated, not allowed) map to distinct UX — clients route on `extensions.code`.
- Normalise email on signup (`.trim().toLowerCase()`). Hash passwords with bcrypt, 10+ salt rounds.

---

## 6. Pagination (Relay Cursor Connection)

Offset pagination is simple and scales poorly. Use cursors for production.

```graphql
type NoteConnection {
  edges: [NoteEdge!]!
  nodes: [Note!]!
  pageInfo: PageInfo!
  totalCount: Int
}
type NoteEdge { cursor: String!, node: Note! }
type PageInfo {
  startCursor: String
  endCursor: String
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
}
type Query { feed(first: Int = 20, after: String): NoteConnection! }
```

```ts
// src/resolvers/Query.ts
export const Query: QueryResolvers = {
  feed: async (_, { first = 20, after }, { db }) => {
    const limit = Math.min(first!, 100);
    const rows = await db.notes.page({ after, limit: limit + 1 });
    const hasNextPage = rows.length > limit;
    if (hasNextPage) rows.pop();
    return {
      edges: rows.map((n) => ({ cursor: encode(n.id), node: n })),
      nodes: rows,
      pageInfo: {
        startCursor: rows.length ? encode(rows[0].id) : null,
        endCursor:   rows.length ? encode(rows.at(-1)!.id) : null,
        hasNextPage,
        hasPreviousPage: false,
      },
    };
  },
};
```

Cursors are **opaque** — base64-encode them so clients do not parse IDs and so you can change the underlying ordering without breaking anyone. `totalCount` is expensive on large tables — make it nullable and only compute when asked.

---

## 7. Error Handling

Apollo ships typed error classes: `AuthenticationError`, `ForbiddenError`, `UserInputError`, `ApolloError`. Each sets `extensions.code` to a stable machine-readable string (`UNAUTHENTICATED`, `FORBIDDEN`, `BAD_USER_INPUT`). Clients route on code, not on message.

```ts
import { UserInputError } from 'apollo-server-errors';
if (!email.includes('@')) throw new UserInputError('Invalid email', { field: 'email' });
```

**Prefer errors-as-data for field-level validation.** Return them in the payload type so the UI renders per-field messages without reading the top-level `errors[]`:

```graphql
type CreateNotePayload { note: Note, errors: [UserError!]! }
type UserError { field: String, message: String!, code: String! }
```

**Mask in production.** Stack traces and upstream messages leak internals. Use `formatError`:

```ts
new ApolloServer({
  formatError: (err) => {
    logger.error(err);
    if (err.extensions?.code === 'INTERNAL_SERVER_ERROR') {
      return new Error('Internal server error');
    }
    return err;
  },
});
```

---

## 8. Apollo Server Setup

```ts
import { ApolloServer } from '@apollo/server';
import { expressMiddleware } from '@apollo/server/express4';
import { ApolloServerPluginLandingPageProductionDefault } from '@apollo/server/plugin/landingPage/default';
import depthLimit from 'graphql-depth-limit';
import { createComplexityLimitRule } from 'graphql-validation-complexity';

const server = new ApolloServer<Context>({
  typeDefs, resolvers,
  introspection: process.env.NODE_ENV !== 'production',
  validationRules: [
    depthLimit(7),
    createComplexityLimitRule(1000, { onCost: (c) => metrics.queryCost.observe(c) }),
  ],
  plugins: [ApolloServerPluginLandingPageProductionDefault()],
  formatError,
});
await server.start();
app.use('/graphql', helmet(), cors(corsOpts), express.json(), expressMiddleware(server, { context: buildContext }));
```

Middleware order matters: `helmet` → `cors` → `json` → Apollo. Validation rules run *before* execution — that is the correct layer for depth and complexity guards, not resolvers.

---

## 9. Subscriptions (graphql-ws)

Transport is `graphql-ws` (not deprecated `subscriptions-transport-ws`). Auth the `connection_init` frame, not every message.

```ts
useServer({
  schema,
  context: async (ctx) => {
    const user = readJwt(`Bearer ${ctx.connectionParams?.authToken}`);
    if (!user) throw new Error('unauthenticated');
    return { user, loaders: makeLoaders(db), db };
  },
}, new WebSocketServer({ server: httpServer, path: '/graphql' }));

Subscription: {
  noteAdded: {
    subscribe: withFilter(
      () => pubsub.asyncIterator('NOTE_ADDED'),
      (payload, _a, ctx) => payload.noteAdded.tenant_id === ctx.user.tenant_id,
    ),
  },
},
```

In a multi-node deploy use Redis-backed PubSub (`graphql-redis-subscriptions`) so events fan out across instances.

---

## 10. Federation v2

Apollo Federation v2 composes multiple subgraph schemas into one supergraph served by a router. Each team owns a subgraph.

```graphql
# users subgraph
type User @key(fields: "id") {
  id: ID!
  username: String!
}

# notes subgraph — extends User with a shareable field
type Note @key(fields: "id") {
  id: ID!
  content: String!
  author: User!
}
type User @key(fields: "id") {
  id: ID! @external
  notes: [Note!]!
}
```

**Directives to know:**

- `@key(fields: "...")` — identifies the entity; the router uses it to stitch.
- `@external` — a field is declared here but owned elsewhere.
- `@shareable` — the field can be resolved by multiple subgraphs (router picks one).
- `@requires(fields: "...")` — this resolver needs fields from another subgraph before it can run.
- `@provides(fields: "...")` — this resolver already returns fields from another subgraph, no need to fetch.

Entity resolution happens in the subgraph that owns the `@key`:

```ts
Query: {
  _entities: (_, { representations }, { loaders }) =>
    representations.map((rep) => loaders.userById.load(rep.id)),
},
```

Composition runs in CI (`rover supergraph compose`); the router (Apollo Router or `@apollo/gateway`) serves the composed schema. Do not write supergraph schemas by hand.

---

## 11. TypeScript End-to-End (graphql-codegen)

```yaml
# codegen.yml
schema: src/schema.graphql
documents: 'src/**/*.graphql'
generates:
  src/__generated__/graphql.ts:
    plugins: [typescript, typescript-operations, typescript-resolvers]
    config: { contextType: '../context#Context', useIndexSignature: true }
```

`typescript` generates schema types. `typescript-operations` generates one type *per query* matching exactly the fields that query selects — the anti-hallucination safeguard. `typescript-resolvers` types the resolver maps against the schema. Add `typescript-react-apollo` on the client for typed `useFeedQuery()` hooks.

Run `yarn generate` on every schema/operation change; CI fails if generated files drift. Without this discipline, TypeScript silently lies.

---

## 12. File Uploads

Apollo Server 4 does not ship uploads — use `graphql-upload-minimal` with the multipart request spec.

```ts
app.use('/graphql', graphqlUploadExpress({ maxFileSize: 10_000_000, maxFiles: 3 }));
// scalar Upload; type Mutation { uploadAvatar(file: Upload!): String! }
```

Resolver receives `{ createReadStream, filename, mimetype }`. Stream directly to S3 — never buffer the full file. Enforce size at middleware *and* reverse proxy. If binary traffic is heavy, keep a plain HTTP POST endpoint and let the mutation return only a reference.

---

## 13. Testing

**Unit:** resolvers are just functions — call them directly with a faked context. `await Query.feed!({}, { first: 5 }, ctx as any, {} as any)`.

**Integration:** `@apollo/server` exposes `server.executeOperation({ query, variables }, { contextValue })` to run the pipeline in-process — preferred over hitting HTTP.

**Mocked schema** via `addMocksToSchema` (`@graphql-tools/mock`) for frontend dev without a backend.

**Schema snapshot tests** — `printSchema(schema)` → golden file. Any accidental breaking change fails CI before a resolver runs.

---

## 14. Production Hardening

Mandatory for any public endpoint: **depth limit** (`depthLimit(7)`); **complexity/cost analysis** (`graphql-cost-analysis` — cap per request, record score for rate-limiting and metering); **introspection off** in production (GitLab's 2019 DoS was unlimited introspection); **persisted queries** (APQ + whitelist — reject unknown hashes in strict mode); **timeouts** (HTTP 30 s at proxy, resolver `AbortController` on downstream); **disable batching array requests** unless used (bypasses per-request rate limits); **CORS allow-list** — never `*`; **helmet + TLS** at the edge; **tracing** (OpenTelemetry → Jaeger/Tempo + Apollo Studio).

Load `graphql-security` for the adversarial checklist (alias/directive overloading, SSRF via argument fields, CSRF on mutations).

---

## 15. When Not to Use GraphQL

- Single canonical client, HTTP caching dominates, no N+1 pain → REST is cheaper.
- Heavy binary uploads or server-sent file streams → HTTP native.
- Public API where CDN edge caching is business-critical → GraphQL's POST-only default defeats it.
- One team, one service, <10 endpoints → the tooling weight does not pay back.

**Hybrid default:** GraphQL as a BFF over REST microservices — REST for webhooks and file upload, GraphQL for client-shaped reads of relational UIs. Pairs naturally with `microservices-communication`.