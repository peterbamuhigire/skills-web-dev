# Scaling and Messaging — Deep Dive

## Cluster Module

```js
import cluster from 'cluster'
import { cpus } from 'os'
import { once } from 'events'

if (cluster.isPrimary) {
  const numCPUs = cpus().length
  console.log(`Starting ${numCPUs} workers`)
  for (let i = 0; i < numCPUs; i++) cluster.fork()

  // Restart crashed workers (resiliency)
  cluster.on('exit', (worker, code) => {
    if (code !== 0 && !worker.exitedAfterDisconnect) {
      console.log(`Worker ${worker.process.pid} crashed — restarting`)
      cluster.fork()
    }
  })

  // Zero-downtime restart via SIGUSR2
  process.on('SIGUSR2', async () => {
    const workers = Object.values(cluster.workers)
    for (const worker of workers) {
      worker.disconnect()
      await once(worker, 'exit')
      if (!worker.exitedAfterDisconnect) continue  // skip if crashed
      const newWorker = cluster.fork()
      await once(newWorker, 'listening')           // wait until ready
    }
    console.log('Rolling restart complete')
  })

  // Broadcast message to all workers
  // Object.values(cluster.workers).forEach(w => w.send({ type: 'config', data }))
} else {
  // Worker process
  const server = createServer(requestHandler)
  server.listen(8080)
  console.log(`Worker ${process.pid} started`)
}
```

## Worker Threads (CPU-bound)

```js
// main.js
import { Worker, isMainThread, parentPort, workerData } from 'worker_threads'

if (isMainThread) {
  function runWorker(data) {
    return new Promise((resolve, reject) => {
      const worker = new Worker('./compute.js', { workerData: data })
      worker.on('message', resolve)
      worker.on('error', reject)
      worker.on('exit', code => {
        if (code !== 0) reject(new Error(`Worker exited with code ${code}`))
      })
    })
  }

  const result = await runWorker({ input: largeDataset })
} else {
  // compute.js
  const result = heavyCompute(workerData.input)
  parentPort.postMessage(result)
}

// Shared memory between threads
const sharedBuffer = new SharedArrayBuffer(4)
const view = new Int32Array(sharedBuffer)
Atomics.add(view, 0, 1)   // atomic increment — thread-safe
```

## Child Processes

```js
import { fork, exec, spawn } from 'child_process'

// Fork another Node.js script — IPC channel included
const child = fork('./worker.js')
child.send({ type: 'task', data: payload })
child.on('message', result => console.log(result))
child.on('error', err => console.error(err))
child.on('exit', (code, signal) => console.log(`Exit: ${code} ${signal}`))

// Spawn external process — streams stdout/stderr
const ls = spawn('ls', ['-la'])
ls.stdout.pipe(process.stdout)
ls.stderr.pipe(process.stderr)

// Exec — buffers output (use for small outputs only)
import { promisify } from 'util'
const execAsync = promisify(exec)
const { stdout } = await execAsync('git log --oneline -10')
```

## Redis Pub/Sub Scaling

```js
import { createClient } from 'redis'

const pub = createClient()
const sub = createClient()

await pub.connect()
await sub.connect()

// Publisher
await pub.publish('chat:room1', JSON.stringify({ user: 'Alice', msg: 'hello' }))

// Subscriber
await sub.subscribe('chat:room1', (message) => {
  const data = JSON.parse(message)
  // broadcast to websocket clients on this server
  broadcastToClients(data)
})
```

## AMQP (RabbitMQ) Task Queue

```js
import amqp from 'amqplib'

// Producer
const conn = await amqp.connect('amqp://localhost')
const ch = await conn.createConfirmChannel()
await ch.assertQueue('tasks_queue', { durable: true })

tasks.forEach(task => {
  ch.sendToQueue('tasks_queue', Buffer.from(JSON.stringify(task)),
    { persistent: true })
})
await ch.waitForConfirms()
ch.close(); conn.close()

// Consumer (worker)
const ch = await conn.createChannel()
await ch.assertQueue('tasks_queue', { durable: true })
ch.prefetch(1)  // process one task at a time

ch.consume('tasks_queue', async (msg) => {
  const task = JSON.parse(msg.content.toString())
  try {
    const result = await processTask(task)
    await ch.sendToQueue(msg.properties.replyTo,
      Buffer.from(JSON.stringify(result)),
      { correlationId: msg.properties.correlationId })
    ch.ack(msg)
  } catch (err) {
    ch.nack(msg, false, true)  // requeue on failure
  }
})
```

## Redis Streams Consumer Groups

```js
import Redis from 'ioredis'
const redis = new Redis()

// Producer
await redis.xadd('tasks_stream', '*', 'payload', JSON.stringify(task))

// Consumer group worker
await redis.xgroup('CREATE', 'tasks_stream', 'workers', '$', 'MKSTREAM')
  .catch(() => {})  // ignore if already exists

while (true) {
  const [[, records]] = await redis.xreadgroup(
    'GROUP', 'workers', `worker-${process.pid}`,
    'BLOCK', '0', 'COUNT', '1',
    'STREAMS', 'tasks_stream', '>'
  )

  for (const [id, [, payload]] of records) {
    const result = await processTask(JSON.parse(payload))
    await redis.xadd('results_stream', '*', 'result', JSON.stringify(result))
    await redis.xack('tasks_stream', 'workers', id)
  }
}
```

## Nginx Load Balancing Config

```nginx
upstream nodeapp {
  least_conn;                        # least connections algorithm
  server 127.0.0.1:3001;
  server 127.0.0.1:3002;
  server 127.0.0.1:3003;
  server 127.0.0.1:3004;
  keepalive 32;
}

server {
  listen 80;
  location / {
    proxy_pass http://nodeapp;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
  }
}
```

## Correlation ID Pattern (request/reply over one-way channel)

```js
import { nanoid } from 'nanoid'

function createRequestChannel(channel) {
  const correlationMap = new Map()

  channel.on('message', ({ inReplyTo, data }) => {
    const resolve = correlationMap.get(inReplyTo)
    if (resolve) { correlationMap.delete(inReplyTo); resolve(data) }
  })

  return function sendRequest(data) {
    return new Promise((resolve, reject) => {
      const id = nanoid()
      const timeout = setTimeout(() => {
        correlationMap.delete(id); reject(new Error('Request timeout'))
      }, 10_000)

      correlationMap.set(id, (result) => {
        clearTimeout(timeout); resolve(result)
      })
      channel.send({ type: 'request', data, id })
    })
  }
}
```
