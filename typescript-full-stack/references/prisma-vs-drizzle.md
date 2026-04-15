# Prisma vs Drizzle

Cross-ref: `database-design-engineering` for schema design; `postgresql-fundamentals`
and `mysql-best-practices` for engine-specific tuning; `typescript-mastery` for
Drizzle's heavy use of conditional inference.

Both are first-class TypeScript ORMs. Choose per service based on team, complexity,
and perf needs — mixing inside one service is rarely worth the cognitive cost.

## At a glance

| Concern | Prisma | Drizzle |
| --- | --- | --- |
| Source of truth | `schema.prisma` | TS schema files |
| SQL visibility | hidden unless `$queryRaw` | SQL-shaped API |
| Migrations | first-class, integrated | `drizzle-kit generate` + apply |
| Transactions | nested callback | callback or async (transactional) |
| Relations API | eager via `include` | `with` clause or explicit joins |
| Type inference cost | moderate | heavy — slows large schemas |
| Runtime size | bigger (query engine) | smaller (pure TS) |
| Edge runtimes | driver adapter required | first-class |
| Raw SQL escape hatch | `$queryRaw` template | core API is SQL |
| Introspect existing DB | `prisma db pull` | `drizzle-kit pull` |

## Schema definition

### Prisma

`packages/db/prisma/schema.prisma`:

```prisma
generator client {
  provider = "prisma-client-js"
  previewFeatures = ["driverAdapters"]
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        String   @id @default(uuid()) @db.Uuid
  email     String   @unique
  name      String
  role      Role     @default(member)
  orgId     String   @db.Uuid
  org       Org      @relation(fields: [orgId], references: [id], onDelete: Cascade)
  posts     Post[]
  createdAt DateTime @default(now())

  @@index([orgId, createdAt(sort: Desc)])
}

model Org {
  id    String  @id @default(uuid()) @db.Uuid
  name  String
  users User[]
}

model Post {
  id       String @id @default(uuid()) @db.Uuid
  title    String
  authorId String @db.Uuid
  author   User   @relation(fields: [authorId], references: [id])
}

enum Role {
  admin
  member
  viewer
}
```

### Drizzle

`packages/db/src/schema/user.ts`:

```ts
import { pgTable, pgEnum, uuid, text, timestamp, index, uniqueIndex } from "drizzle-orm/pg-core";
import { relations } from "drizzle-orm";

export const roleEnum = pgEnum("role", ["admin", "member", "viewer"]);

export const orgs = pgTable("orgs", {
  id: uuid("id").defaultRandom().primaryKey(),
  name: text("name").notNull(),
});

export const users = pgTable(
  "users",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    email: text("email").notNull(),
    name: text("name").notNull(),
    role: roleEnum("role").notNull().default("member"),
    orgId: uuid("org_id").notNull().references(() => orgs.id, { onDelete: "cascade" }),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => ({
    emailIdx: uniqueIndex("users_email_key").on(t.email),
    orgCreatedIdx: index("users_org_created_idx").on(t.orgId, t.createdAt.desc()),
  })
);

export const usersRelations = relations(users, ({ one, many }) => ({
  org: one(orgs, { fields: [users.orgId], references: [orgs.id] }),
  posts: many(posts),
}));
```

Rule for both: primary keys are UUIDv7 or UUIDv4 (db-generated); avoid bigint IDs in
multi-tenant SaaS because they leak volume and ordering.

## Queries

### Prisma

```ts
import { db } from "@acme/db";

const user = await db.user.findUnique({
  where: { id },
  include: { posts: { where: { published: true }, take: 10, orderBy: { createdAt: "desc" } } },
});

const paginated = await db.user.findMany({
  where: { orgId, createdAt: { gt: new Date("2026-01-01") } },
  orderBy: { createdAt: "desc" },
  take: 25,
});

// Complex: falls back to raw
const hot = await db.$queryRaw<Array<{ id: string; count: bigint }>>`
  SELECT author_id AS id, count(*)::bigint AS count
  FROM post
  WHERE created_at > now() - interval '7 days'
  GROUP BY author_id
  ORDER BY count DESC
  LIMIT 10
`;
```

### Drizzle

```ts
import { db } from "@acme/db";
import { users, posts } from "@acme/db/schema";
import { and, eq, desc, gt, sql } from "drizzle-orm";

const user = await db.query.users.findFirst({
  where: eq(users.id, id),
  with: {
    posts: {
      where: eq(posts.published, true),
      orderBy: desc(posts.createdAt),
      limit: 10,
    },
  },
});

const paginated = await db
  .select()
  .from(users)
  .where(and(eq(users.orgId, orgId), gt(users.createdAt, new Date("2026-01-01"))))
  .orderBy(desc(users.createdAt))
  .limit(25);

const hot = await db
  .select({ id: posts.authorId, count: sql<number>`count(*)::int` })
  .from(posts)
  .where(sql`${posts.createdAt} > now() - interval '7 days'`)
  .groupBy(posts.authorId)
  .orderBy(desc(sql`count(*)`))
  .limit(10);
```

The Drizzle version reads as SQL — you see the joins, the aliases, the ordering. The
Prisma version reads as object manipulation — faster to write, harder to predict.

## Transactions

### Prisma

```ts
const result = await db.$transaction(
  async (tx) => {
    const user = await tx.user.create({ data: { email, name, orgId } });
    await tx.auditLog.create({ data: { actorId: user.id, action: "user.created" } });
    return user;
  },
  { isolationLevel: "Serializable", timeout: 10_000, maxWait: 5_000 }
);
```

### Drizzle

```ts
const result = await db.transaction(async (tx) => {
  const [user] = await tx.insert(users).values({ email, name, orgId }).returning();
  await tx.insert(auditLogs).values({ actorId: user.id, action: "user.created" });
  return user;
}, { isolationLevel: "serializable" });
```

Both support nested transactions via savepoints. Keep transactions short — long
transactions multiply lock contention. Never include an external HTTP call inside a
transaction.

## Migrations

### Prisma

```bash
pnpm prisma migrate dev --name add_user_role
pnpm prisma migrate deploy       # production
pnpm prisma migrate resolve --applied 20260101_drift_fix
```

Prisma's shadow DB catches destructive changes in dev. Production runs `migrate
deploy` in a separate Kubernetes Job before rolling out the API.

### Drizzle

```bash
pnpm drizzle-kit generate        # emit SQL from schema diff
pnpm drizzle-kit migrate         # apply pending migrations
```

`drizzle-kit` emits plain SQL files. Review them as SQL (and commit them). This is
both the benefit and the cost — you own the DDL.

## Performance considerations

- Prisma's query engine (Rust binary) adds ~50 MB to a container image; driver
  adapters (`@prisma/adapter-pg`) remove it at the cost of some features.
- Drizzle is pure TS — ships in a few hundred KB.
- Drizzle is typically 2-5x faster on simple reads because it maps rows directly;
  Prisma pipes through a language boundary.
- For very large schemas (>200 tables), Drizzle's type inference can slow `tsc`. Use
  project references to isolate.
- Prisma's `select` projections are mandatory for perf on wide rows; relying on
  defaults ships entire rows across the wire.

## Edge runtime

Prisma on edge (Vercel, Cloudflare): `PrismaClient({ adapter: new PrismaPg({ ... }) })`
with `@prisma/adapter-pg` or `-neon`. The query engine is removed.

Drizzle on edge: works out of the box with `drizzle-orm/neon-http`,
`drizzle-orm/planetscale-serverless`, and `drizzle-orm/d1`.

For Cloudflare Workers D1 / Hyperdrive, Drizzle has the lower-friction path.

## Multi-tenancy row filtering

Both ORMs lack native tenant-scoping. Approaches:

1. Wrap the client in a factory that injects `where: { orgId }` — brittle.
2. Use Postgres RLS and set `SET LOCAL app.org_id = $1` per transaction — strongest
   isolation. Works with both.
3. Prisma extensions (`$extends`) to auto-inject — lives in user land.

For SaaS with regulated tenants, pair the ORM with RLS. See
`multi-tenant-saas-architecture`.

## Decision rules

```text
Team comfortable with SQL, want it visible in code            -> Drizzle
Team mixed SQL skill, want safer DX, less SQL expertise        -> Prisma
Cloudflare Workers, Neon, D1, edge-first                       -> Drizzle
Big existing Prisma codebase, no pain                          -> stay Prisma
>200 tables, tsc slow with Drizzle                             -> Prisma or split schemas
Postgres-heavy features (arrays, ranges, tsvector, ltree)      -> Drizzle
MySQL with Prisma team skills                                  -> Prisma
Need a graph of eager-loaded relations with minimal code       -> Prisma
Read-heavy reporting queries                                   -> Drizzle (SQL ergonomics)
```

## Migration between them

Going Prisma → Drizzle:

1. `drizzle-kit introspect:pg` against the existing DB — emits schema.
2. Hand-reconcile naming conventions (snake_case in DB, camelCase in TS).
3. Replace one router's data access at a time; run both clients in parallel during
   the cutover.
4. Ensure migrations stay in one tool — don't let both own DDL concurrently.

Going Drizzle → Prisma:

1. `prisma db pull` from the DB; inspect diff vs Drizzle schema.
2. Re-create migration baseline (`prisma migrate resolve --applied`).
3. Replace query call sites; Prisma typings make this largely mechanical.

## Anti-patterns

- Two ORMs in one service, "to try Drizzle incrementally". Pick one per deployable.
- Running `prisma migrate dev` in production.
- `$queryRaw` without template-literal binding — SQL injection risk.
- Drizzle `sql` fragments without parameter binding — same risk.
- `findMany()` with no `take` — unbounded reads.
- `include` five levels deep — produces N+M queries or mega-joins; denormalise or
  use a view.
