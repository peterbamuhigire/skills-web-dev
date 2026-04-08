# Async Patterns — Deep Dive

## Event Loop Priority

```
process.nextTick()   → microtask, before ANY I/O in current tick
Promise.then()       → microtask, after nextTick
setImmediate()       → macrotask, after I/O in current loop cycle
setTimeout(fn, 0)    → macrotask, next loop cycle (slightly slower than setImmediate)
```

Use `process.nextTick()` to guarantee a callback is always async:
```js
function consistentAsync(value, cb) {
  if (cache.has(value)) {
    process.nextTick(() => cb(null, cache.get(value)))  // defer sync path
  } else {
    fetchAsync(value, (err, result) => {
      if (!err) cache.set(value, result)
      cb(err, result)
    })
  }
}
```

## TaskQueue — Limited Parallel Execution

```js
export class TaskQueue {
  #concurrency; #running = 0; #queue = []

  constructor(concurrency) { this.#concurrency = concurrency }

  runTask(task) {
    return new Promise((resolve, reject) => {
      this.#queue.push(async () => {
        try { resolve(await task()) }
        catch (err) { reject(err) }
        finally { this.#running--; this.#next() }
      })
      this.#next()
    })
  }

  #next() {
    while (this.#running < this.#concurrency && this.#queue.length) {
      const task = this.#queue.shift()
      this.#running++
      task()
    }
  }
}

// Usage
const queue = new TaskQueue(5)  // max 5 concurrent
await Promise.all(urls.map(url => queue.runTask(() => fetch(url))))
```

## Producer-Consumer with async/await

```js
export class TaskQueuePC {
  #taskQueue = []; #consumerQueue = []

  constructor(concurrency) {
    for (let i = 0; i < concurrency; i++) this.#consumer()
  }

  async #consumer() {
    while (true) {
      try {
        const task = await this.#getNextTask()
        await task()
      } catch (err) { console.error(err) }
    }
  }

  #getNextTask() {
    return new Promise(resolve => {
      if (this.#taskQueue.length) return resolve(this.#taskQueue.shift())
      this.#consumerQueue.push(resolve)  // sleep consumer until task arrives
    })
  }

  runTask(task) {
    return new Promise((resolve, reject) => {
      const wrapper = () => {
        const p = task()
        p.then(resolve, reject)
        return p
      }
      if (this.#consumerQueue.length) {
        this.#consumerQueue.shift()(wrapper)  // wake sleeping consumer
      } else {
        this.#taskQueue.push(wrapper)
      }
    })
  }
}
```

## Request Batching (deduplicate concurrent identical requests)

```js
const inFlight = new Map()

async function fetchUser(id) {
  if (inFlight.has(id)) return inFlight.get(id)
  const promise = db.findById(id).finally(() => inFlight.delete(id))
  inFlight.set(id, promise)
  return promise
}
// Multiple callers requesting same user ID → only one DB query fires
```

## Promisification

```js
import { promisify } from 'util'
const readFile = promisify(fs.readFile)

// Manual promisify
function promisifyCallback(fn) {
  return (...args) => new Promise((resolve, reject) => {
    fn(...args, (err, result) => err ? reject(err) : resolve(result))
  })
}

// Promisify all methods of an object
import { promisifyAll } from 'bluebird'
const dbAsync = promisifyAll(db)
```

## Async Generators (infinite data streams)

```js
async function* paginate(fetchPage) {
  let page = 1
  while (true) {
    const items = await fetchPage(page++)
    if (!items.length) return
    yield* items
  }
}

for await (const item of paginate(p => api.getItems({ page: p }))) {
  await process(item)
}
```

## Cancellation with AbortController

```js
const controller = new AbortController()
const { signal } = controller

setTimeout(() => controller.abort(), 5000)  // cancel after 5s

try {
  const response = await fetch(url, { signal })
  const data = await response.json()
} catch (err) {
  if (err.name === 'AbortError') console.log('Request cancelled')
  else throw err
}
```
