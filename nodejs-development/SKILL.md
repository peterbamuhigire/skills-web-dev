---
name: nodejs-development
description: Production Node.js development — async patterns, streams, design patterns, HTTP APIs, testing, scaling, and deployment. Synthesised from Node.js Design Patterns (Casciaro & Mammino 3rd ed.), Node.js Recipes (Gackenheimer), Fullstack Node.js (Murray), and Node.js Fundamentals. Use when building scalable servers, REST APIs, CLI tools, real-time systems, or fullstack JavaScript applications.
---

# Node.js Development Skill

## Core Philosophy (The Node Way)

- **Small core** — minimal built-ins, rich userland via npm
- **Small modules** — each module does one thing well (Unix philosophy)
- **Small surface area** — expose minimal API, prefer functions over classes
- **Simplicity > perfection** — ship pragmatic code, iterate fast

Node.js uses the **reactor pattern** via libuv: a single-threaded event loop
demultiplexes async I/O events and dispatches them to callbacks. Never block
the event loop with CPU-heavy synchronous work.

---

## 1. Module System

```js
// CommonJS (legacy — still dominant)
module.exports = { greet }
const { greet } = require('./greet')

// ESM (modern — prefer for new code)
export function greet(name) { return `Hello ${name}` }
import { greet } from './greet.js'   // .js extension required

// Dynamic import
const { default: heavy } = await import('./heavy.js')

// ESM __dirname equivalent
import { fileURLToPath } from 'url'
import { dirname } from 'path'
const __dirname = dirname(fileURLToPath(import.meta.url))
```

**Decision:** New project → ESM (`"type": "module"` in package.json). Existing
CJS codebase → keep CJS. Public library → dual CJS+ESM.

**Singleton via module cache:**
```js
// db.js — exported instance is cached; importers always get the same object
export const db = new Database(process.env.DB_URL)
```

---

## 2. Async Patterns

### Callback convention (error-first, callback last)
```js
function readJSON(filename, callback) {
  fs.readFile(filename, 'utf8', (err, data) => {
    if (err) return callback(err)
    try { callback(null, JSON.parse(data)) }
    catch (e) { callback(e) }
  })
}
```

**Anti-pattern — Zalgo:** never invoke a callback sync in some paths and async
in others. Use `process.nextTick(() => cb(...))` to defer sync paths.

### async/await (preferred)
```js
async function getUser(id) {
  try {
    const user = await db.findById(id)
    if (!user) throw new AppError('Not found', 404)
    return user
  } catch (err) {
    logger.error(err); throw err
  }
}

// NEVER forEach with await — use for...of or Promise.all
for (const item of items) { await process(item) }           // sequential
await Promise.all(items.map(item => process(item)))          // parallel
```

**Infinite loop — avoid recursive promise chains (memory leak):**
```js
// LEAKS
async function tick() { await delay(1); return tick() }

// SAFE
async function tick() { while (true) { await delay(1); doWork() } }
```

### EventEmitter (Observer pattern — repeated events)
```js
import { EventEmitter } from 'events'

class FileWatcher extends EventEmitter {
  watch(files) {
    for (const file of files) {
      fs.readFile(file, 'utf8', (err, data) => {
        if (err) return this.emit('error', err)
        this.emit('file', file)
        data.match(/TODO/g)?.forEach(m => this.emit('match', file, m))
      })
    }
    return this
  }
}

watcher.on('match', (file, text) => console.log(`${file}: ${text}`))
watcher.on('error', err => console.error(err))
// Always remove listeners to prevent memory leaks:
emitter.removeListener('event', handler)   // or use .once()
```

**Choose EventEmitter when:** events repeat, multiple listeners needed, or
event types differ. Use callbacks for single async results.

---

## 3. Streams

```js
import { pipeline } from 'stream/promises'
import { createReadStream, createWriteStream } from 'fs'
import { createGzip } from 'zlib'

// PREFER pipeline() over .pipe() — proper error propagation
await pipeline(
  createReadStream('big.csv'),
  createGzip(),
  createWriteStream('big.csv.gz')
)

// Async iterator (cleanest way to consume)
for await (const chunk of readableStream) {
  process(chunk)
}

// Custom Transform stream
import { Transform } from 'stream'
class UpperCase extends Transform {
  _transform(chunk, enc, cb) { this.push(chunk.toString().toUpperCase()); cb() }
}
```

**Rules:** Stream files > ~1 MB. Backpressure: `write()` returns `false` when
buffer full — wait for `drain` event. Object mode: `{ objectMode: true }`.

See `references/streams.md` for advanced patterns (forking, merging, mux/demux).

---

## 4. HTTP Patterns

```js
// Minimal server
import { createServer } from 'http'
const server = createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'application/json' })
  res.end(JSON.stringify({ status: 'ok' }))
})
server.listen(process.env.PORT || 3000)

// Static file via stream
const stream = createReadStream(filepath)
stream.on('error', err => { res.statusCode = 404; res.end() })
res.writeHead(200, { 'Content-Type': getMime(filepath) })
stream.pipe(res)

// HTTP client (POST)
const req = request({ hostname, path: '/api', method: 'POST',
  headers: { 'Content-Type': 'application/json' } }, handleResponse)
req.write(JSON.stringify(payload))
req.end()
```

**Express middleware pattern:**
```js
app.use((req, res, next) => { req.startTime = Date.now(); next() })
app.use((err, req, res, next) => {   // error handler — 4 args
  res.status(err.statusCode || 500).json({ error: err.message })
})
```

---

## 5. Design Patterns

### Factory — decouple creation from implementation
```js
function createLogger(env) {
  return env === 'production' ? new FileLogger() : new ConsoleLogger()
}
```

### Builder — fluent interface for complex objects
```js
const query = new QueryBuilder()
  .from('users').where('active = 1').limit(10).build()
```

### Proxy — intercept and control access
```js
const observed = new Proxy(target, {
  set(obj, prop, value) {
    onChange(prop, obj[prop], value)
    obj[prop] = value; return true
  }
})
```

### Middleware — chain of responsibility
```js
class Pipeline {
  #steps = []
  use(fn) { this.#steps.push(fn); return this }
  async run(ctx) {
    const go = async (i) => this.#steps[i]?.(ctx, () => go(i + 1))
    await go(0)
  }
}
```

### Strategy — swap algorithms at runtime
```js
class Exporter {
  constructor(strategy) { this.strategy = strategy }
  export(data) { return this.strategy.serialize(data) }
}
```

See `references/design-patterns.md` for Decorator, Adapter, Singleton, DI,
Revealing Constructor, Iterators/Generators.

---

## 6. Error Handling

```js
class AppError extends Error {
  constructor(message, code, statusCode = 500) {
    super(message); this.code = code; this.statusCode = statusCode
  }
}

// Global handlers — always exit after uncaughtException
process.on('uncaughtException', err => { logger.fatal(err); process.exit(1) })
process.on('unhandledRejection', (reason) => { logger.error(reason); process.exit(1) })
```

---

## 7. Testing

```js
// assert/strict (built-in)
assert.deepEqual(result, expected)
assert.rejects(async () => fn(), { code: 'NOT_FOUND' })

// Mocha + Chai (BDD)
describe('UserService', () => {
  it('creates a user', async () => {
    const user = await service.create({ name: 'Alice' })
    expect(user).to.have.property('id')
  })
})
```

Test layout: `*.test.js` collocated with source for unit tests; `test/integration/`
for API tests with real HTTP; `test/e2e/` for end-to-end flows.

---

## 8. Scaling

```js
// Cluster — one worker per CPU core
import cluster from 'cluster'
import { cpus } from 'os'

if (cluster.isPrimary) {
  cpus().forEach(() => cluster.fork())
  cluster.on('exit', (w, code) => {
    if (code !== 0 && !w.exitedAfterDisconnect) cluster.fork()  // restart crashed
  })
} else {
  createServer(handler).listen(8080)
}

// Worker threads — CPU-bound tasks
import { Worker } from 'worker_threads'
const w = new Worker('./compute.js', { workerData: input })
w.on('message', result => handleResult(result))
```

**Scaling decisions:**
- Single machine → `cluster` (one worker per core)
- Multi-machine → Nginx/HAProxy reverse proxy + multiple processes
- Stateful sessions → shared Redis store (never sticky sessions)
- CPU-bound → `worker_threads`

---

## 9. Security Essentials

```js
// Path traversal prevention
import { basename } from 'path'
const safeFile = basename(req.headers['x-filename'])

// AES-256-GCM encryption
import { createCipheriv, randomBytes } from 'crypto'
const iv = randomBytes(16)
const cipher = createCipheriv('aes-256-gcm', key, iv)

// Password hashing
import bcrypt from 'bcrypt'
const hash = await bcrypt.hash(password, 12)

// Environment-based secrets
if (!process.env.JWT_SECRET && process.env.NODE_ENV === 'production') {
  throw new Error('JWT_SECRET required in production')
}
```

---

## 10. Production Deployment

```bash
# package.json
"engines": { "node": ">=18" }
"scripts": { "start": "node src/server.js" }

# Health check endpoint
GET /health → { status: 'ok', uptime: process.uptime() }

# Process management
pm2 start src/server.js --instances max --name myapp
# OR systemd with Restart=on-failure

# Zero-downtime: SIGUSR2 → rolling restart of cluster workers
```

**Deployment options:**
| Option | When to use |
|--------|------------|
| VPS + Nginx + pm2 | Full control, high-traffic production |
| Heroku / Render | Fast iteration, low-ops overhead |
| AWS Lambda | Stateless APIs, spiky traffic |
| Docker + K8s | Multi-service, horizontal scaling |

---

## Quick Reference: Decision Rules

| Situation | Choice |
|-----------|--------|
| New project | ESM modules |
| Single async result | async/await |
| Repeated events | EventEmitter |
| Large file I/O | Streams + pipeline() |
| CPU-bound work | worker_threads |
| Parallel I/O | Promise.all() |
| Limited concurrency | mapWithConcurrency() |
| Scale one machine | cluster module |
| Scale multi-machine | Nginx reverse proxy |
| Password storage | bcrypt (factor 12+) |
| Encryption | AES-256-GCM |

---

## Deep-Dive References

- `references/async-patterns.md` — callbacks, promises, TaskQueue, producer-consumer
- `references/streams.md` — backpressure, Transform, merge, fork, mux/demux
- `references/design-patterns.md` — all creational/structural/behavioural patterns
- `references/scaling.md` — cluster, worker_threads, messaging (AMQP, Redis Streams)
- `references/mongodb-mongoose.md` — schema design, validation, relationships, populate
- `references/realtime.md` — WebSockets, SSE, Socket.IO
- `references/testing.md` — Mocha/Chai, mocking, integration testing
- `references/fastify.md` — Fastify server, plugins, hooks, JWT, TypeBox, Swagger, testing
- `references/prisma.md` — schema, migrations, CRUD, relations, transactions, TypeScript types
- `references/bullmq.md` — queues, workers, retries, cron, FlowProducer, Bull Board, Redis

---

## Sources

- *Node.js Design Patterns* 3rd ed. — Casciaro & Mammino (Packt, 2020)
- *Node.js Recipes* — Cory Gackenheimer (Apress, 2013)
- *Fullstack Node.js* — Nate Murray (Leanpub, 2019)
- *Node.js Fundamentals* — Machine Learning
- *Accelerating Server-Side Development with Fastify* — Manuel Spigolon (Packt)
- *Next.js 13 + Prisma* — Greg Lim
