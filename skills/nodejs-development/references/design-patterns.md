# Node.js Design Patterns — Deep Dive

## Creational Patterns

### Factory — decouple creation from implementation
```js
function createImage(name) {
  if (name.match(/\.jpe?g$/)) return new ImageJpeg(name)
  if (name.match(/\.png$/))   return new ImagePng(name)
  throw new Error('Unsupported format')
}

// Factory for encapsulation via closures
function createPerson(name) {
  const _private = {}
  return {
    setName(n) { if (!n) throw new Error('Name required'); _private.name = n },
    getName() { return _private.name }
  }
}
```

### Builder — fluent interface
```js
class UrlBuilder {
  setProtocol(p) { this.protocol = p; return this }
  setHostname(h) { this.hostname = h; return this }
  setAuth(user, pass) { this.username = user; this.password = pass; return this }
  setPath(p) { this.pathname = p; return this }
  setQuery(q) { this.search = q; return this }
  build() {
    if (!this.protocol || !this.hostname) throw new Error('protocol and hostname required')
    let url = `${this.protocol}://`
    if (this.username) url += `${this.username}:${this.password}@`
    url += this.hostname
    if (this.pathname) url += this.pathname
    if (this.search) url += `?${this.search}`
    return url
  }
}
```

### Revealing Constructor — expose internals only at creation time
```js
// Like Promise — executor gets resolve/reject, but callers cannot modify state
class ImmutableBuffer {
  constructor(size, executor) {
    const buf = Buffer.alloc(size)
    const modifiers = {}
    for (const key in buf) {
      if (typeof buf[key] !== 'function') continue
      if (key.startsWith('write') || key.startsWith('fill') || key === 'swap') {
        modifiers[key] = buf[key].bind(buf)
      } else {
        this[key] = buf[key].bind(buf)
      }
    }
    executor(modifiers)  // consumer can only modify at creation time
  }
}

const buf = new ImmutableBuffer(4, ({ writeInt32BE }) => writeInt32BE(42, 0))
// buf.writeInt32BE is undefined — immutable after construction
```

### Singleton — module cache pattern
```js
// Safe singleton within same package
class DatabasePool {
  constructor(url) { this.url = url; this.pool = [] }
  acquire() { /* ... */ }
}
export const db = new DatabasePool(process.env.DB_URL)
// NOTE: multiple packages with different versions of this module
// may each get their own instance — use global for true singleton
```

## Structural Patterns

### Proxy — intercept object access
```js
// Object composition proxy
class LoggingWritable {
  constructor(writable) { this._writable = writable }
  write(chunk, enc, cb) {
    console.log(`Writing ${chunk.length} bytes`)
    return this._writable.write(chunk, enc, cb)
  }
  end(chunk, enc, cb) { return this._writable.end(chunk, enc, cb) }
}

// Proxy object (ES6)
function createLoggingProxy(target) {
  return new Proxy(target, {
    get(obj, prop) {
      return typeof obj[prop] === 'function'
        ? (...args) => {
            console.log(`${String(prop)}(${JSON.stringify(args)})`)
            return obj[prop].apply(obj, args)
          }
        : obj[prop]
    }
  })
}

// Change observer
function observable(target, onChange) {
  return new Proxy(target, {
    set(obj, prop, value) {
      onChange(prop, obj[prop], value)
      obj[prop] = value
      return true
    }
  })
}
```

### Decorator — add behaviour without subclassing
```js
// Composition-based decorator
class CachedLevelDB {
  constructor(db) { this._db = db; this._cache = new Map() }
  get(key) {
    if (this._cache.has(key)) return Promise.resolve(this._cache.get(key))
    return this._db.get(key).then(val => { this._cache.set(key, val); return val })
  }
  put(key, value) { this._cache.delete(key); return this._db.put(key, value) }
  del(key) { this._cache.delete(key); return this._db.del(key) }
}
```

### Adapter — incompatible interface bridge
```js
// Expose LevelDB key-value store through fs-like interface
class LevelFsAdapter {
  constructor(db) { this._db = db }
  readFile(filename, options, cb) {
    if (typeof options === 'function') { cb = options }
    this._db.get(filename, cb)
  }
  writeFile(filename, data, options, cb) {
    if (typeof options === 'function') { cb = options }
    this._db.put(filename, data, cb)
  }
}
```

## Behavioural Patterns

### Strategy — pluggable algorithms
```js
class Config {
  constructor(strategy) { this._strategy = strategy }
  load(file) {
    return fs.readFile(file, 'utf8').then(data => {
      this._data = this._strategy.deserialize(data)
    })
  }
  save(file) {
    return fs.writeFile(file, this._strategy.serialize(this._data))
  }
  get(path) { return objectPath.get(this._data, path) }
  set(path, value) { return objectPath.set(this._data, path, value) }
}

const jsonConfig = new Config({ serialize: JSON.stringify, deserialize: JSON.parse })
const iniConfig  = new Config({ serialize: ini.stringify,  deserialize: ini.parse })
```

### Template Method — define algorithm skeleton
```js
class ConfigTemplate {
  async load(file) {
    const data = await fsPromises.readFile(file, 'utf8')
    this.data = this._deserialize(data)
  }
  async save(file) {
    await fsPromises.writeFile(file, this._serialize(this.data))
  }
  _serialize() { throw new Error('Must implement _serialize()') }
  _deserialize() { throw new Error('Must implement _deserialize()') }
}

class JsonConfig extends ConfigTemplate {
  _deserialize(data) { return JSON.parse(data) }
  _serialize(data)   { return JSON.stringify(data, null, 2) }
}
```

### Command Pattern — encapsulate invocations
```js
class StatusUpdateService {
  #queue = []

  submit(command) { this.#queue.push(command) }

  async flush() {
    while (this.#queue.length) {
      const cmd = this.#queue.shift()
      try {
        await cmd.execute()
        cmd.onSuccess?.()
      } catch (err) {
        cmd.onFailure?.(err)
      }
    }
  }
}

const service = new StatusUpdateService()
service.submit({
  execute: () => db.updateStatus(userId, 'active'),
  onSuccess: () => logger.info('status updated'),
  onFailure: err => logger.error(err)
})
```

### Iterator and Generator
```js
// Custom iterable class
class Range {
  constructor(start, end) { this.start = start; this.end = end }
  [Symbol.iterator]() {
    let current = this.start
    const end = this.end
    return {
      next() {
        return current <= end
          ? { value: current++, done: false }
          : { done: true }
      }
    }
  }
}

for (const n of new Range(1, 5)) console.log(n)  // 1 2 3 4 5

// Generator as iterator
function* fibonacci() {
  let [a, b] = [0, 1]
  while (true) {
    yield a;
    [a, b] = [b, a + b]
  }
}

const fib = fibonacci()
console.log(fib.next().value)  // 0, 1, 1, 2, 3, 5...

// Async generator for paginated data
async function* paginatedFetch(url) {
  let page = 1
  while (true) {
    const res = await fetch(`${url}?page=${page++}`)
    const items = await res.json()
    if (!items.length) return
    yield* items
  }
}
```

## Dependency Injection

```js
// Constructor injection — preferred
class BlogService {
  constructor(db, mailer) {
    this._db = db
    this._mailer = mailer
  }
  async createPost(data) {
    const post = await this._db.create(data)
    await this._mailer.sendNotification(post)
    return post
  }
}

// Wire dependencies at app entry point
const db = new Database(config.dbUrl)
const mailer = new Mailer(config.smtpUrl)
const blogService = new BlogService(db, mailer)

// Easy to mock in tests
const mockDb = { create: async data => ({ id: 1, ...data }) }
const service = new BlogService(mockDb, { sendNotification: async () => {} })
```
