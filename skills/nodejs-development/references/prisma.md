# Prisma Reference

**Sources:** *Next.js 13 + Prisma* (Lim, Greg) + Prisma official docs patterns

---

## 1. Setup

```bash
npm install prisma @prisma/client
npx prisma init --datasource-provider postgresql
# Creates: prisma/schema.prisma  +  .env
```

`.env`:
```env
DATABASE_URL="postgresql://user:pass@localhost:5432/mydb?schema=public"
```

---

## 2. Schema (`prisma/schema.prisma`)

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        String   @id @default(uuid())
  email     String   @unique
  name      String?
  role      Role     @default(USER)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  posts     Post[]
  profile   Profile?
}

model Profile {
  id     String @id @default(uuid())
  bio    String?
  user   User   @relation(fields: [userId], references: [id], onDelete: Cascade)
  userId String @unique
}

model Post {
  id         String   @id @default(uuid())
  title      String
  content    String?
  published  Boolean  @default(false)
  author     User     @relation(fields: [authorId], references: [id])
  authorId   String
  tags       Tag[]
  createdAt  DateTime @default(now())
}

model Tag {
  id    String @id @default(uuid())
  name  String @unique
  posts Post[]
}

enum Role {
  USER
  ADMIN
}
```

**Key annotations:**
| Annotation | Purpose |
|-----------|---------|
| `@id` | Primary key |
| `@default(uuid())` | Auto UUID |
| `@default(now())` | Timestamp on create |
| `@updatedAt` | Auto-update timestamp |
| `@unique` | Unique constraint |
| `@relation` | FK definition |
| `onDelete: Cascade` | Cascade delete |

---

## 3. Migrations

```bash
npx prisma migrate dev --name init        # create + apply (dev)
npx prisma migrate deploy                 # apply in production
npx prisma migrate reset                  # drop + recreate (dev only)
npx prisma db push                        # sync schema without migration file
npx prisma generate                       # regenerate Prisma Client after schema change
npx prisma studio                         # GUI browser for your data
```

---

## 4. Prisma Client — Singleton (Node.js + Next.js safe)

```typescript
// lib/prisma.ts
import { PrismaClient } from '@prisma/client'

const globalForPrisma = globalThis as unknown as { prisma: PrismaClient }

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({ log: ['query', 'error', 'warn'] })

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma
```

**Why globalThis:** Hot-reload in dev creates new PrismaClient instances each time,
exhausting the DB connection pool. Attaching to `globalThis` prevents duplicates.

---

## 5. CRUD Operations

### findMany / findUnique / findFirst

```typescript
// All users
const users = await prisma.user.findMany()

// With filter, sort, pagination
const users = await prisma.user.findMany({
  where: { role: 'ADMIN', name: { contains: 'ali', mode: 'insensitive' } },
  orderBy: { createdAt: 'desc' },
  skip: 0,
  take: 20,
  select: { id: true, email: true, name: true },
})

// Single — throws if not found
const user = await prisma.user.findUniqueOrThrow({ where: { id } })

// First match
const user = await prisma.user.findFirst({ where: { email } })
```

### create

```typescript
const user = await prisma.user.create({
  data: {
    email: 'alice@example.com',
    name: 'Alice',
    profile: { create: { bio: 'Developer' } },  // nested create
  },
  include: { profile: true },
})
```

### update / upsert

```typescript
const user = await prisma.user.update({
  where: { id },
  data: { name: 'Alice Updated' },
})

const user = await prisma.user.upsert({
  where: { email: 'alice@example.com' },
  update: { name: 'Alice' },
  create: { email: 'alice@example.com', name: 'Alice' },
})
```

### delete / deleteMany

```typescript
await prisma.user.delete({ where: { id } })
await prisma.post.deleteMany({ where: { published: false } })
```

### count / aggregate

```typescript
const total = await prisma.user.count({ where: { role: 'ADMIN' } })

const stats = await prisma.post.aggregate({
  _count: true,
  _avg: { views: true },
  where: { published: true },
})
```

---

## 6. Relations

### Include (eager load)

```typescript
const user = await prisma.user.findUnique({
  where: { id },
  include: {
    posts: { where: { published: true }, orderBy: { createdAt: 'desc' } },
    profile: true,
  },
})
```

### Select (shape the response)

```typescript
const user = await prisma.user.findUnique({
  where: { id },
  select: {
    id: true,
    email: true,
    posts: { select: { id: true, title: true } },
  },
})
```

### Nested writes

```typescript
// Create post + connect to existing tags + create new tag
const post = await prisma.post.create({
  data: {
    title: 'Hello',
    author: { connect: { id: userId } },
    tags: {
      connectOrCreate: [
        { where: { name: 'nodejs' }, create: { name: 'nodejs' } },
      ],
    },
  },
})
```

---

## 7. Filtering Operators

```typescript
where: {
  name: { contains: 'ali', mode: 'insensitive' },
  email: { startsWith: 'a', endsWith: '.com' },
  createdAt: { gte: new Date('2024-01-01'), lte: new Date() },
  role: { in: ['ADMIN', 'USER'] },
  NOT: { email: { contains: 'spam' } },
  AND: [{ published: true }, { views: { gt: 100 } }],
  OR:  [{ name: null }, { name: '' }],
}
```

---

## 8. Pagination

### Offset pagination

```typescript
const PAGE_SIZE = 20
const page = parseInt(req.query.page) || 1

const [items, total] = await prisma.$transaction([
  prisma.post.findMany({ skip: (page - 1) * PAGE_SIZE, take: PAGE_SIZE }),
  prisma.post.count(),
])
```

### Cursor pagination (efficient for large datasets)

```typescript
const posts = await prisma.post.findMany({
  take: 20,
  skip: cursor ? 1 : 0,
  cursor: cursor ? { id: cursor } : undefined,
  orderBy: { createdAt: 'asc' },
})
const nextCursor = posts[posts.length - 1]?.id
```

---

## 9. Transactions

```typescript
// Sequential (interactive)
const [user, post] = await prisma.$transaction([
  prisma.user.create({ data: { email: 'a@b.com' } }),
  prisma.post.create({ data: { title: 'Hi', authorId: '...' } }),
])

// Interactive (full control)
await prisma.$transaction(async (tx) => {
  const user = await tx.user.create({ data: { email: 'a@b.com' } })
  await tx.profile.create({ data: { userId: user.id, bio: 'Dev' } })
  if (!user) throw new Error('rollback')  // automatic rollback on throw
})
```

---

## 10. Raw Queries

```typescript
// Type-safe tagged template
const users = await prisma.$queryRaw<User[]>`
  SELECT * FROM "User" WHERE role = ${role}
`

// Execute (INSERT/UPDATE/DELETE)
const count = await prisma.$executeRaw`
  UPDATE "User" SET "updatedAt" = NOW() WHERE id = ${id}
`
```

---

## 11. TypeScript Integration

```typescript
import { Prisma } from '@prisma/client'

// Input types (auto-generated)
type UserCreateInput = Prisma.UserCreateInput
type UserUpdateInput = Prisma.UserUpdateInput
type UserWhereInput  = Prisma.UserWhereInput

// Payload types (with relations)
type UserWithPosts = Prisma.UserGetPayload<{
  include: { posts: true }
}>

// Result type helper
function exclude<T, K extends keyof T>(obj: T, keys: K[]): Omit<T, K> {
  return Object.fromEntries(
    Object.entries(obj as any).filter(([k]) => !keys.includes(k as K))
  ) as Omit<T, K>
}
const safeUser = exclude(user, ['password'])
```

---

## 12. Error Handling

```typescript
import { Prisma } from '@prisma/client'

try {
  await prisma.user.create({ data: { email } })
} catch (e) {
  if (e instanceof Prisma.PrismaClientKnownRequestError) {
    if (e.code === 'P2002') {
      // Unique constraint violation — e.meta.target has the field name
      throw new AppError(`${e.meta?.target} already exists`, 409)
    }
    if (e.code === 'P2025') {
      throw new AppError('Record not found', 404)
    }
  }
  throw e
}
```

**Common error codes:**
| Code | Meaning |
|------|---------|
| P2002 | Unique constraint failed |
| P2003 | FK constraint failed |
| P2025 | Record not found |
| P2016 | Query interpretation error |

---

## 13. Seeding

```typescript
// prisma/seed.ts
import { PrismaClient } from '@prisma/client'
const prisma = new PrismaClient()

async function main() {
  await prisma.user.upsert({
    where: { email: 'admin@example.com' },
    update: {},
    create: { email: 'admin@example.com', name: 'Admin', role: 'ADMIN' },
  })
}

main().catch(console.error).finally(() => prisma.$disconnect())
```

`package.json`:
```json
"prisma": { "seed": "ts-node prisma/seed.ts" }
```

```bash
npx prisma db seed
```

---

## 14. Connection to Fastify

```typescript
// plugins/prisma.ts
import fp from 'fastify-plugin'
import { PrismaClient } from '@prisma/client'

export default fp(async (fastify) => {
  const prisma = new PrismaClient()
  await prisma.$connect()

  fastify.decorate('prisma', prisma)

  fastify.addHook('onClose', async () => {
    await prisma.$disconnect()
  })
})

declare module 'fastify' {
  interface FastifyInstance { prisma: PrismaClient }
}
```

```typescript
// In a route handler
fastify.get('/users', async (req, reply) => {
  const users = await fastify.prisma.user.findMany()
  return users
})
```

---

## Anti-Patterns

- **Never** create `new PrismaClient()` inside a request handler (connection pool exhaustion)
- **Never** expose Prisma model objects directly — select only required fields
- **Avoid** `findMany()` without `take` on large tables (always paginate)
- **Use** `$transaction` for any operation that must be atomic
- **Always** call `$disconnect()` on process exit or in plugin `onClose` hook
