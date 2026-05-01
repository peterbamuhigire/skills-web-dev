
# BullMQ Production Reference

BullMQ is a Node.js queue library built on Redis (evolved from Bull, 2014; BullMQ launched 2019
with full TypeScript rewrite). Outperforms RabbitMQ and Kafka in latency and resource utilisation
for microservice background jobs (IJIRT 2025 benchmark).

Sections: Installation | Core Concepts | Redis Connection | Queue | Jobs | Worker | Job API |
Lifecycle | Retries | Repeatable | Flows | Concurrency | Rate Limiting | Events | Shutdown |
Bull Board | Redis Config | Error Handling | Patterns

---

## 1. Installation

```bash
npm install bullmq ioredis
```

Requirements: Node.js 10.x+, Redis 6.2+ or Dragonfly.

---

## 2. Core Concepts

| Class | Role |
|---|---|
| `Queue` | Holds jobs; producers call `queue.add()` |
| `Worker` | Processes jobs; receives the processor function |
| `Job` | Unit of work with `.data`, `.id`, `.name`, `.opts` |
| `QueueEvents` | Cross-process event listener (completed/failed/progress) |
| `FlowProducer` | Creates parent/child dependency trees |

All state lives in Redis. Job path: `waiting → active → completed | failed`.
Delayed and repeatable jobs sit in `delayed` until scheduled.

---

## 3. Redis Connection

```typescript
import IORedis from 'ioredis';

// Worker connection — maxRetriesPerRequest MUST be null
const workerConn = new IORedis({
  host: process.env.REDIS_HOST,
  port: Number(process.env.REDIS_PORT),
  maxRetriesPerRequest: null,  // REQUIRED
  enableReadyCheck: false,
});

// Queue connection — default maxRetriesPerRequest is fine
const queueConn = { host: 'localhost', port: 6379 };
```

**Critical rules:**
- Never use ioredis `keyPrefix` — conflicts with BullMQ's internal prefixing
- `QueueEvents` and `QueueScheduler` cannot share connections (they use blocking commands)
- Redis must have `maxmemory-policy noeviction` set

---

## 4. Queue

```typescript
import { Queue } from 'bullmq';

const queue = new Queue('emailQueue', {
  connection: queueConn,
  defaultJobOptions: {
    attempts: 3,
    backoff: { type: 'exponential', delay: 1000 },
    removeOnComplete: { count: 1000 },
    removeOnFail: { count: 5000 },
  },
});

// Utility
await queue.pause();
await queue.resume();
const job    = await queue.getJob(jobId);
const counts = await queue.getJobCounts();   // { waiting, active, completed, failed, delayed }
await queue.drain();                          // remove all waiting jobs
await queue.obliterate({ force: true });      // delete queue + all data
```

---

## 5. Adding Jobs and Job Options

```typescript
// Basic
await queue.add('jobName', { userId: 42 });

// With full options
await queue.add('send-email', { to: 'a@example.com' }, {
  delay:           5000,              // ms before first attempt
  attempts:        5,
  backoff:         { type: 'exponential', delay: 2000 },
  priority:        1,                 // lower = higher priority
  jobId:           'user-42-welcome', // idempotency — no duplicate if same ID
  removeOnComplete: true,
  removeOnFail:    false,
  timeout:         30000,             // fail if processor exceeds this
  lifo:            false,             // last-in-first-out within same priority
});

// Bulk add (atomic)
await queue.addBulk([
  { name: 'send-email', data: { to: 'a@example.com' } },
  { name: 'send-email', data: { to: 'b@example.com' } },
]);
```

**Key job options:** `delay` (ms before start) | `attempts` (max tries; 1=no retry) |
`backoff` `{ type: 'exponential'|'fixed', delay, jitter }` | `priority` (1=highest) |
`lifo` (last-in-first-out) | `jobId` (idempotency key, no colons) |
`removeOnComplete` / `removeOnFail` (`bool` or `{ count, age }`) |
`timeout` (ms, fail if exceeded) | `keepLogs` (number of log entries) |
`repeat` (see §10) | `parent` (flow link, see §11) | `sizeLimit` (bytes)

---

## 6. Worker

```typescript
import { Worker, Job } from 'bullmq';

const worker = new Worker('emailQueue',
  async (job: Job, token?: string, signal?: AbortSignal) => {
    await job.updateProgress(50);
    await job.log('Sending...');
    return await sendEmail(job.data); // return value stored as returnvalue
  },
  {
    connection:      workerConn,
    concurrency:     10,       // parallel jobs per worker instance
    autorun:         true,     // false → call worker.run() manually
    lockDuration:    30000,    // ms to hold job lock; increase for slow jobs
    maxStalledCount: 1,        // retries before permanently failed
    stalledInterval: 30000,    // stalled-check interval (ms)
    limiter:         { max: 10, duration: 1000 },
  }
);

await worker.pause();
await worker.resume();
await worker.close(); // graceful — waits for active jobs

worker.on('completed', (job, rv)     => { /* ... */ });
worker.on('failed',    (job, err)    => { /* ... */ });
worker.on('active',    (job)         => { /* ... */ });
worker.on('progress',  (job, prog)   => { /* ... */ });
worker.on('stalled',   (jobId)       => { /* ... */ });
worker.on('drained',   ()            => { /* queue empty */ });
worker.on('error',     (err)         => { console.error(err); }); // MANDATORY
```

---

## 7. Job Object API

```typescript
// Available inside the processor
job.id           // Redis-assigned ID
job.name         // name passed to queue.add()
job.data         // payload object
job.attemptsMade // number of attempts so far

await job.updateProgress(42);                         // number 0-100
await job.updateProgress({ step: 'parse', pct: 75 }); // arbitrary object
await job.log('Step 1 complete');
await job.moveToFailed(new Error('Custom reason'), token);

// Flows: read return values of child jobs
const childValues = await job.getChildrenValues();
```

---

## 8. Job Lifecycle States

```
add() → waiting → active → completed
                 → failed  (retry? → delayed → waiting)

Repeatable:      completed → delayed → waiting (next scheduled run)
Flows:           waiting-children → waiting (when all children done)
Priority:        prioritized set → dequeued by ascending priority number
Paused:          new jobs enter paused instead of waiting
```

States used in API calls: `waiting` `active` `completed` `failed` `delayed`
`paused` `waiting-children` `prioritized`

---

## 9. Retries and Backoff

```typescript
// Fixed — constant delay between retries
await queue.add('job', data, {
  attempts: 3,
  backoff: { type: 'fixed', delay: 1000 },
});

// Exponential — delay = 2^(attempt-1) × delay
// attempt 1: 1000 ms | attempt 2: 2000 ms | attempt 3: 4000 ms
await queue.add('job', data, {
  attempts: 5,
  backoff: { type: 'exponential', delay: 1000 },
});

// With jitter (0–1) to avoid thundering herd
await queue.add('job', data, {
  attempts: 8,
  backoff: { type: 'exponential', delay: 3000, jitter: 0.5 },
});

// Custom backoff: pass settings.backoffStrategy to Worker, then use { type: 'custom-name' }
// Return 0 → end of waiting list. Return -1 → move to failed immediately.
```

---

## 10. Repeatable / Scheduled Jobs

```typescript
// Cron — daily at 03:15
await queue.add('daily-report', { type: 'full' }, {
  repeat: { pattern: '0 15 3 * * *' },
});

// Every N ms with execution cap
await queue.add('poll-api', { endpoint: '/status' }, {
  repeat: { every: 10000, limit: 100 },
});

// Multiple jobs with same options — distinguish with jobId
await queue.add('sync', { target: 'users' },  { repeat: { every: 60000 }, jobId: 'sync-users' });
await queue.add('sync', { target: 'orders' }, { repeat: { every: 60000 }, jobId: 'sync-orders' });

// Update existing repeatable job — use key
await queue.add('sync', { target: 'users', v: 2 }, {
  repeat: { every: 60000, key: 'sync-users' },
});

// Remove by key or name+pattern
await queue.removeRepeatableByKey(job.repeatJobKey);
await queue.removeRepeatable('task', { every: 5000 });

// List all
const jobs = await queue.getRepeatableJobs();
```

BullMQ will not add a duplicate repeatable job if name + repeat options already exist.
Missed runs while no worker is online do NOT accumulate.

---

## 11. Job Dependencies (Flows)

```typescript
import { FlowProducer } from 'bullmq';

const flowProducer = new FlowProducer({ connection });

// Fan-out: parent waits for 3 parallel children
await flowProducer.add({
  name: 'generate-invoice', queueName: 'invoices',
  children: [
    { name: 'fetch-items', data: { orderId: 1 }, queueName: 'steps' },
    { name: 'apply-tax',   data: { region: 'UG' }, queueName: 'steps' },
    { name: 'format-pdf',  data: { tpl: 'v2' }, queueName: 'steps' },
  ],
});

// Parent reads child return values
const invoiceWorker = new Worker('invoices', async (job) => {
  const results = await job.getChildrenValues(); // { childJobId: returnValue }
  const total = Object.values(results).reduce((s, v) => s + v, 0);
  await saveInvoice(total);
});

```

Notes: Parent and children can use different queues. Avoid colons in `jobId`. Deleting a parent
cascades to children. For serial chains, nest children one level deep.

---

## 12. Concurrency and Rate Limiting

```typescript
// Concurrency per worker process
const worker = new Worker('queue', processor, { connection, concurrency: 20 });

// Global rate limiter — applies across ALL worker instances
const worker = new Worker('painter', processor, {
  connection,
  limiter: { max: 10, duration: 1000 }, // 10 jobs/second globally
});

// Per-tenant rate limiting (groupKey)
const queue  = new Queue('painter',  { connection, limiter: { groupKey: 'customerId' } });
const worker = new Worker('painter', processor, {
  connection,
  limiter: { max: 10, duration: 1000, groupKey: 'customerId' },
});
await queue.add('paint', { customerId: 'cust-42' });

// Dynamic / manual rate limiting (e.g. upstream 429)
const worker = new Worker('api', async (job) => {
  const [limited, retryAfterMs] = await callApi(job.data);
  if (limited) {
    await worker.rateLimit(retryAfterMs);
    throw Worker.RateLimitError();
  }
}, { connection, limiter: { max: 1, duration: 500 } });

// Inspect / clear rate limit
const ttl = await queue.getRateLimitTtl(100);
await queue.removeRateLimitKey();
```

---

## 13. Events

```typescript
// QueueEvents — cross-process listener (attach in any service, separate connection)
import { QueueEvents } from 'bullmq';
const queueEvents = new QueueEvents('emailQueue', { connection });

queueEvents.on('completed', ({ jobId, returnvalue }) => { /* ... */ });
queueEvents.on('failed',    ({ jobId, failedReason }) => { /* ... */ });
queueEvents.on('progress',  ({ jobId, data })         => { /* ... */ });
queueEvents.on('active',    ({ jobId })                => { /* ... */ });
queueEvents.on('stalled',   ({ jobId })                => { /* ... */ });

const result = await queueEvents.waitUntilFinished(job); // tests / orchestration
```

---

## 14. Graceful Shutdown

```typescript
const gracefulShutdown = async (signal: string) => {
  await worker.close();       // stop new jobs; wait for active jobs to finish
  await queueEvents.close();
  await queue.close();
  process.exit(0);
};

process.on('SIGINT',  () => gracefulShutdown('SIGINT'));
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
```

---

## 15. Monitoring — Bull Board

```bash
npm install @bull-board/api @bull-board/express
```

```typescript
import { createBullBoard } from '@bull-board/api';
import { BullMQAdapter }   from '@bull-board/api/bullMQAdapter';
import { ExpressAdapter }  from '@bull-board/express';

const serverAdapter = new ExpressAdapter();
serverAdapter.setBasePath('/admin/queues');

createBullBoard({
  queues: [
    new BullMQAdapter(emailQueue),
    new BullMQAdapter(reportQueue),
  ],
  serverAdapter,
});

app.use('/admin/queues', serverAdapter.getRouter());
// Dashboard at http://localhost:3000/admin/queues
```

---

## 16. Production Redis Config

```typescript
const workerConn = new IORedis({
  host: process.env.REDIS_HOST,
  port: Number(process.env.REDIS_PORT),
  password: process.env.REDIS_PASSWORD,
  tls: process.env.REDIS_TLS === 'true' ? {} : undefined,
  maxRetriesPerRequest: null,   // REQUIRED for workers
  enableReadyCheck: false,
  retryStrategy: (times) => Math.min(times * 50, 2000),
});
// redis.conf: maxmemory-policy noeviction  |  appendonly yes

// Cluster
import { Cluster } from 'ioredis';
const clusterConn = new Cluster(
  [{ host: 'node1', port: 6379 }, { host: 'node2', port: 6379 }],
  { redisOptions: { maxRetriesPerRequest: null } }
);
```

---

## 17. Error Handling and DLQ

```typescript
// Always attach error listeners
worker.on('error', (err) => logger.error(err, 'Worker error'));
queue.on('error',  (err) => logger.error(err, 'Queue error'));

// Processor MUST throw Error instances, not strings
throw new Error('API returned 500');   // correct
// throw 'something went wrong';       // WRONG

// Dead-letter queue pattern
const dlq = new Queue('jobs-dlq', { connection });

worker.on('failed', async (job, err) => {
  if (job && job.attemptsMade >= (job.opts.attempts ?? 1)) {
    await dlq.add('dead', {
      originalJobId: job.id,
      data:          job.data,
      failedReason:  err.message,
      failedAt:      new Date().toISOString(),
    });
  }
});

// Manual retry of all failed jobs
const failed = await queue.getJobs(['failed']);
for (const job of failed) await job.retry();
```

---

## 18. Common Queue Patterns

| Pattern | Key options |
|---|---|
| Email queue | `concurrency: 5`, `attempts: 5`, `backoff: exponential` |
| Daily report | `repeat: { pattern: '0 0 6 * * *' }`, `concurrency: 2` |
| AI / LLM calls | `limiter: { max: 60, duration: 60000 }`, `timeout: 60000` |
| Webhook delivery | `attempts: 10`, `backoff: { type: 'exponential', jitter: 0.3 }`, `concurrency: 20` |
| Multi-step flow | `FlowProducer` with parent + children queues |

### Email worker template

```typescript
const emailQueue = new Queue('emails', {
  connection,
  defaultJobOptions: { attempts: 5, backoff: { type: 'exponential', delay: 2000 } },
});
await emailQueue.add('welcome', { to: user.email });

new Worker('emails', async (job) => {
  await job.updateProgress(10);
  const result = await mailer.send({ to: job.data.to, template: job.name, data: job.data });
  await job.log(`Sent: ${result.messageId}`);
  return { messageId: result.messageId };
}, { connection, concurrency: 5 });
```

### AI job queue (rate-limited)

```typescript
new Worker('ai-tasks', async (job) => {
  const res = await openai.chat.completions.create({ model: 'gpt-4o', messages: job.data.messages });
  await job.log(`Tokens: ${res.usage?.total_tokens}`);
  return res.choices[0].message.content;
}, { connection, concurrency: 3, limiter: { max: 60, duration: 60000 } });
```

### Webhook delivery

```typescript
new Worker('webhooks', async (job) => {
  const res = await fetch(job.data.url, { method: 'POST', body: JSON.stringify(job.data.payload),
    headers: { 'Content-Type': 'application/json' } });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return { status: res.status };
}, { connection, concurrency: 20 });
```

---

## Performance vs Alternatives (IJIRT 2025)

BullMQ + Redis: low latency, efficient resource use, high cost efficiency, excellent scalability.
RabbitMQ: limited scalability, higher resource use, higher latency under load.
Kafka: excellent throughput but high infra cost and complexity.

Recommended for Node.js microservices where latency and cost matter more than Kafka-scale throughput.
