# Testing — Deep Dive

## Built-in `assert` Module

```js
import assert from 'assert/strict'

// Equality
assert.strictEqual(add(2, 3), 5)
assert.deepStrictEqual({ a: 1 }, { a: 1 })

// Errors
assert.throws(() => parseAge(-1), { message: /must be positive/ })
await assert.rejects(fetchUser(-1), { name: 'AppError' })
```

## Mocha + Chai (BDD Style)

```js
import { describe, it, before, after, beforeEach, afterEach } from 'mocha'
import { expect } from 'chai'
import sinon from 'sinon'

describe('UserService', () => {
  let service, mockDb

  before(() => { /* one-time setup */ })
  after(() => { /* one-time teardown */ })

  beforeEach(() => {
    mockDb = { findById: sinon.stub(), save: sinon.stub() }
    service = new UserService(mockDb)
  })

  afterEach(() => sinon.restore())

  it('returns user by id', async () => {
    mockDb.findById.resolves({ id: 1, name: 'Alice' })
    const user = await service.getUser(1)
    expect(user.name).to.equal('Alice')
    expect(mockDb.findById.calledWith(1)).to.be.true
  })

  it('throws NOT_FOUND when user missing', async () => {
    mockDb.findById.resolves(null)
    await expect(service.getUser(99))
      .to.be.rejectedWith('Not found')
  })
})
```

**Run:**
```bash
npx mocha --recursive test/
npx mocha --watch --recursive test/unit/
```

## Project Layout

```
project/
├── src/
│   ├── services/userService.js
│   └── routes/users.js
└── test/
    ├── unit/
    │   └── services/userService.test.js    # isolated, no I/O
    └── integration/
        └── routes/users.test.js            # HTTP + real DB
```

**Unit tests:** Mock all I/O, no network/DB calls. Fast, deterministic.
**Integration tests:** Spin up real (test) DB, use supertest for HTTP.

## Sinon — Stubs, Spies, Mocks

```js
import sinon from 'sinon'

// Stub: replace function, control return value
const stub = sinon.stub(db, 'findById').resolves({ id: 1 })

// Spy: wrap function, record calls without changing behaviour
const spy = sinon.spy(mailer, 'send')
await service.createUser(data)
expect(spy.calledOnce).to.be.true
expect(spy.firstCall.args[0]).to.include({ to: 'alice@example.com' })

// Fake timers
const clock = sinon.useFakeTimers()
setTimeout(() => result = 42, 1000)
clock.tick(1000)
expect(result).to.equal(42)
clock.restore()

// Always restore in afterEach
afterEach(() => sinon.restore())
```

## Supertest — HTTP Integration Tests

```js
import request from 'supertest'
import app from '../src/app.js'
import mongoose from 'mongoose'

before(async () => {
  await mongoose.connect(process.env.MONGO_TEST_URI)
})

after(async () => {
  await mongoose.connection.dropDatabase()
  await mongoose.disconnect()
})

describe('POST /api/users', () => {
  it('creates a user and returns 201', async () => {
    const res = await request(app)
      .post('/api/users')
      .send({ name: 'Bob', email: 'bob@example.com' })
      .expect(201)
      .expect('Content-Type', /json/)

    expect(res.body).to.have.property('id')
    expect(res.body.name).to.equal('Bob')
  })

  it('returns 400 on missing name', async () => {
    await request(app)
      .post('/api/users')
      .send({ email: 'bad@example.com' })
      .expect(400)
  })
})
```

## Testing Streams

```js
import { pipeline } from 'stream/promises'
import { Readable } from 'stream'

it('transforms data correctly', async () => {
  const chunks = []
  const source = Readable.from(['hello world'])
  const dest = new Writable({
    write(chunk, enc, cb) { chunks.push(chunk.toString()); cb() }
  })

  await pipeline(source, new MyTransform(), dest)

  expect(chunks.join('')).to.equal('HELLO WORLD')
})
```

## Testing EventEmitters

```js
it('emits "data" event on publish', done => {
  const emitter = new MyEventEmitter()

  emitter.once('data', (payload) => {
    expect(payload).to.deep.equal({ msg: 'hello' })
    done()
  })

  emitter.publish({ msg: 'hello' })
})

// Async version
it('emits "data" event', async () => {
  const emitter = new MyEventEmitter()
  const [payload] = await once(emitter, 'data')
  // trigger in parallel...
  emitter.publish({ msg: 'hello' })
  expect(payload).to.deep.equal({ msg: 'hello' })
})
```

## Testing Async Error Paths

```js
// Test that promise rejects with correct shape
it('rejects on DB error', async () => {
  mockDb.save.rejects(new Error('Connection lost'))
  try {
    await service.create({ name: 'X' })
    assert.fail('Should have thrown')
  } catch (err) {
    expect(err.message).to.equal('Connection lost')
  }
})

// Chai-as-promised (cleaner)
import chaiAsPromised from 'chai-as-promised'
chai.use(chaiAsPromised)

await expect(service.create({}))
  .to.be.rejectedWith('Validation failed')
```

## Code Coverage (c8 / Istanbul)

```bash
# c8 wraps Node.js built-in V8 coverage
npx c8 mocha --recursive test/

# With thresholds (fail CI if below)
npx c8 --lines 80 --functions 80 --branches 70 mocha test/
```

```json
// package.json scripts
{
  "scripts": {
    "test": "mocha --recursive test/",
    "test:watch": "mocha --watch --recursive test/unit/",
    "test:integration": "mocha --recursive test/integration/",
    "coverage": "c8 --lines 80 npm test"
  }
}
```

## Test Data Factories

```js
// Avoid repetitive test setup — factory functions
function buildUser(overrides = {}) {
  return {
    id: cuid(),
    name: 'Alice Test',
    email: `test-${Date.now()}@example.com`,
    role: 'user',
    ...overrides
  }
}

// In tests:
const admin = buildUser({ role: 'admin' })
const inactive = buildUser({ active: false })
```

## Environment Isolation

```js
// .env.test (loaded by dotenv in test setup)
NODE_ENV=test
MONGO_URI=mongodb://localhost:27017/myapp_test
PORT=3001

// test/setup.js (mocha --require test/setup.js)
import 'dotenv/config'
process.env.NODE_ENV = 'test'
```

## Anti-patterns

```js
// BAD: test depends on execution order
it('test 2 relies on state from test 1')  // brittle

// BAD: no assertion — test always passes
it('calls save', async () => { await service.create(data) })

// BAD: testing implementation instead of behaviour
it('calls db.findById exactly 3 times')  // too brittle

// GOOD: test observable behaviour
it('returns enriched user with role label')
```
