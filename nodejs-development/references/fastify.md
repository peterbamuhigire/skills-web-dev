# Fastify Reference

**Source:** *Accelerating Server-Side Development with Fastify* — Manuel Spigolon (Packt)

---

## Why Fastify over Express

| Concern | Express | Fastify |
|---------|---------|---------|
| Request throughput | ~15k req/s | ~30–76k req/s |
| JSON serialization | `JSON.stringify` | `fast-json-stringify` (2–3× faster) |
| Schema validation | Manual / middleware | JSON Schema built-in (AJV) |
| TypeScript support | Partial | First-class |
| Plugin system | Middleware chain | Encapsulated scope tree |
| Logging | Requires morgan/winston | Pino built-in |

---

## 1. Server Setup

```typescript
import Fastify from 'fastify'

const fastify = Fastify({
  logger: {
    level: 'info',
    transport: process.env.NODE_ENV !== 'production'
      ? { target: 'pino-pretty' }
      : undefined,
  },
  trustProxy: true,               // X-Forwarded-For behind Nginx
  requestTimeout: 30_000,
  bodyLimit: 1_048_576,           // 1 MB
})

await fastify.listen({ port: 3000, host: '0.0.0.0' })
```

### Graceful shutdown

```typescript
const signals = ['SIGINT', 'SIGTERM']
signals.forEach(signal => {
  process.on(signal, async () => {
    await fastify.close()         // drains connections, fires onClose hooks
    process.exit(0)
  })
})
```

---

## 2. Routing

```typescript
// Verbose form — full options
fastify.route({
  method: 'POST',
  url: '/users',
  schema: { body: userCreateSchema, response: { 201: userSchema } },
  preHandler: [authenticate],
  handler: async (request, reply) => {
    const user = await userService.create(request.body)
    reply.code(201)
    return user
  },
})

// Shorthand methods
fastify.get('/users/:id', handler)
fastify.post('/users', { schema, preHandler }, handler)
fastify.put('/users/:id', handler)
fastify.delete('/users/:id', handler)
fastify.patch('/users/:id', handler)

// Route params / query / body
request.params.id
request.query.page
request.body
request.headers['authorization']
```

---

## 3. JSON Schema Validation

Fastify validates and **serializes** via JSON Schema — invalid input is rejected
before it reaches your handler; response objects are serialized faster than
`JSON.stringify`.

```typescript
import { Type, Static } from '@sinclair/typebox'   // TypeBox — preferred

const UserCreate = Type.Object({
  email: Type.String({ format: 'email' }),
  name:  Type.String({ minLength: 1, maxLength: 100 }),
  age:   Type.Optional(Type.Integer({ minimum: 0 })),
})
type UserCreateType = Static<typeof UserCreate>

const UserResponse = Type.Object({
  id:    Type.String(),
  email: Type.String(),
  name:  Type.String(),
})

fastify.post<{ Body: UserCreateType }>('/users', {
  schema: {
    body: UserCreate,
    response: { 201: UserResponse },
  },
  handler: async (req, reply) => {
    const user = await prisma.user.create({ data: req.body })
    reply.code(201)
    return user          // only fields in UserResponse are serialized
  },
})
```

**Raw JSON Schema (no TypeBox):**
```typescript
const schema = {
  body: {
    type: 'object',
    required: ['email'],
    properties: {
      email: { type: 'string', format: 'email' },
      name:  { type: 'string' },
    },
    additionalProperties: false,
  },
}
```

---

## 4. Plugin System

Fastify's killer feature: **scope encapsulation**. Each `register()` call creates
a child scope. Decorators, hooks, and routes registered inside are invisible outside.

```typescript
// plugins/db.ts — using fastify-plugin to BREAK encapsulation (share upward)
import fp from 'fastify-plugin'

export default fp(async (fastify) => {
  const prisma = new PrismaClient()
  fastify.decorate('prisma', prisma)
  fastify.addHook('onClose', () => prisma.$disconnect())
}, { name: 'prisma-plugin' })
```

```typescript
// routes/users.ts — scoped plugin
export default async function userRoutes(fastify: FastifyInstance) {
  fastify.get('/users', async () => fastify.prisma.user.findMany())
  fastify.post('/users', { schema }, async (req) => {
    return fastify.prisma.user.create({ data: req.body })
  })
}
```

```typescript
// app.ts — wire everything together
import Fastify from 'fastify'
import dbPlugin from './plugins/db'
import userRoutes from './routes/users'

const fastify = Fastify({ logger: true })

await fastify.register(dbPlugin)
await fastify.register(userRoutes, { prefix: '/api/v1' })

export default fastify
```

**Rule:** Use `fp()` for infrastructure plugins (DB, auth, config) that must be
visible to all routes. Omit `fp()` for route plugins that should be isolated.

---

## 5. Decorators

```typescript
// Extend the Fastify instance
fastify.decorate('config', { secret: process.env.JWT_SECRET })

// Extend request object
fastify.decorateRequest('user', null)

// Extend reply object
fastify.decorateReply('sendError', function (code: number, msg: string) {
  this.code(code).send({ error: msg })
})

// TypeScript augmentation
declare module 'fastify' {
  interface FastifyInstance { config: { secret: string } }
  interface FastifyRequest  { user: UserPayload | null }
}
```

---

## 6. Hooks (Lifecycle)

```
Incoming → onRequest → preParsing → preValidation → preHandler → handler
                                                                      ↓
Reply ← onSend ← onResponse                              onError (on throw)
```

```typescript
// Global hook
fastify.addHook('onRequest', async (request, reply) => {
  request.log.info({ url: request.url }, 'incoming')
})

// Per-route auth hook
async function authenticate(request: FastifyRequest, reply: FastifyReply) {
  try {
    await request.jwtVerify()
  } catch (err) {
    reply.code(401).send({ error: 'Unauthorized' })
  }
}

fastify.get('/protected', { preHandler: [authenticate] }, handler)

// Error hook
fastify.addHook('onError', async (request, reply, error) => {
  request.log.error(error)
})
```

---

## 7. Error Handling

```typescript
import createError from '@fastify/error'

const NotFound = createError('NOT_FOUND', 'Resource not found', 404)
const Conflict  = createError('CONFLICT', '%s already exists', 409)

// Throw in handlers
throw new NotFound()
throw new Conflict('Email')

// Global error handler
fastify.setErrorHandler(async (error, request, reply) => {
  request.log.error(error)

  if (error.validation) {
    return reply.code(400).send({ error: 'Validation failed', details: error.validation })
  }
  const statusCode = error.statusCode ?? 500
  reply.code(statusCode).send({ error: error.message })
})
```

---

## 8. Authentication with @fastify/jwt

```typescript
import jwt from '@fastify/jwt'

await fastify.register(jwt, { secret: process.env.JWT_SECRET! })

// Sign a token
const token = fastify.jwt.sign({ userId: user.id, role: user.role }, { expiresIn: '7d' })

// Verify hook
async function authenticate(req: FastifyRequest, reply: FastifyReply) {
  await req.jwtVerify()   // throws 401 if invalid; populates req.user
}

// Access payload
const { userId } = req.user as { userId: string }
```

---

## 9. Common Plugins

```bash
npm install @fastify/cors @fastify/helmet @fastify/rate-limit
npm install @fastify/multipart @fastify/static @fastify/cookie
npm install @fastify/jwt @fastify/swagger @fastify/swagger-ui
```

```typescript
import cors    from '@fastify/cors'
import helmet  from '@fastify/helmet'
import rateLimit from '@fastify/rate-limit'

await fastify.register(cors, { origin: process.env.ALLOWED_ORIGIN })
await fastify.register(helmet)
await fastify.register(rateLimit, { max: 100, timeWindow: '1 minute' })
```

---

## 10. Logging (Pino built-in)

```typescript
// In handlers — structured logging
request.log.info({ userId: req.user?.id }, 'user fetched')
fastify.log.error(err, 'database error')

// Redact sensitive fields
const fastify = Fastify({
  logger: {
    redact: ['req.headers.authorization', 'req.body.password'],
    level: process.env.LOG_LEVEL || 'info',
  },
})
```

---

## 11. Testing

```typescript
import { build } from '../app'             // factory that returns fastify instance

describe('POST /users', () => {
  let app: FastifyInstance

  beforeAll(async () => { app = await build({ logger: false }) })
  afterAll(async () => { await app.close() })

  it('creates a user', async () => {
    const res = await app.inject({
      method: 'POST',
      url: '/api/v1/users',
      payload: { email: 'alice@example.com', name: 'Alice' },
    })
    expect(res.statusCode).toBe(201)
    expect(res.json()).toMatchObject({ email: 'alice@example.com' })
  })
})
```

`fastify.inject()` fires requests in-process — no real HTTP, no port needed. Fast.

---

## 12. Project Structure (Book Recommendation)

```
src/
├── app.ts              # Fastify factory: register plugins + routes
├── server.ts           # listen() + graceful shutdown
├── plugins/
│   ├── prisma.ts       # fp() DB plugin
│   ├── jwt.ts          # fp() auth plugin
│   └── config.ts       # fp() env/config plugin
├── routes/
│   ├── users/
│   │   ├── index.ts    # register sub-routes
│   │   ├── list.ts
│   │   └── create.ts
│   └── health.ts
├── schemas/
│   └── user.ts         # TypeBox schemas shared across routes
└── services/
    └── user.service.ts # business logic, uses fastify.prisma
```

**App factory pattern (testable):**
```typescript
// app.ts
export async function buildApp(opts = {}) {
  const fastify = Fastify(opts)
  await fastify.register(configPlugin)
  await fastify.register(prismaPlugin)
  await fastify.register(jwtPlugin)
  await fastify.register(userRoutes, { prefix: '/api/v1' })
  return fastify
}
```

---

## 13. Swagger / OpenAPI

```typescript
import swagger from '@fastify/swagger'
import swaggerUi from '@fastify/swagger-ui'

await fastify.register(swagger, {
  openapi: {
    info: { title: 'My API', version: '1.0.0' },
    components: {
      securitySchemes: {
        bearerAuth: { type: 'http', scheme: 'bearer' },
      },
    },
  },
})
await fastify.register(swaggerUi, { routePrefix: '/docs' })
// Schemas attached to routes auto-populate the Swagger UI
```

---

## Anti-Patterns

- **Avoid** `reply.send()` + `return` together — pick one (prefer `return`)
- **Never** share a Fastify instance between tests — use the factory pattern
- **Don't** skip response schemas — you lose fast-json-stringify serialization
- **Don't** use `fastify-plugin` on route plugins — routes should be encapsulated
- **Avoid** mutating `request.body` — treat it as immutable
