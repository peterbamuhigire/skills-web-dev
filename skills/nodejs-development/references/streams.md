# Streams — Deep Dive

## Stream Types

| Type | Class | Abstract methods | Use case |
|------|-------|-----------------|----------|
| Readable | `stream.Readable` | `_read(size)` | File read, HTTP req body |
| Writable | `stream.Writable` | `_write(chunk, enc, cb)` | File write, HTTP res |
| Duplex | `stream.Duplex` | `_read()` + `_write()` | TCP socket |
| Transform | `stream.Transform` | `_transform(chunk, enc, cb)`, `_flush(cb)` | Compression, encryption, parsing |
| PassThrough | subclass of Transform | none | Observing a pipeline |

## Custom Readable

```js
import { Readable } from 'stream'

class RangeStream extends Readable {
  constructor(start, end, options) {
    super({ objectMode: false, ...options })
    this._start = start; this._end = end; this._current = start
  }
  _read() {
    if (this._current > this._end) {
      this.push(null)   // signal end of stream
    } else {
      this.push(String(this._current++))
    }
  }
}

// Quick readable from iterable
import { Readable } from 'stream'
const r = Readable.from(['chunk1', 'chunk2', 'chunk3'])
```

## Custom Writable

```js
import { Writable } from 'stream'

class ToUpperCaseFile extends Writable {
  constructor(filename) {
    super()
    this._dest = fs.createWriteStream(filename)
  }
  _write(chunk, enc, callback) {
    this._dest.write(chunk.toString().toUpperCase(), callback)
  }
  _final(callback) {
    this._dest.end(callback)
  }
}
```

## Custom Transform

```js
import { Transform } from 'stream'

class ReplaceStream extends Transform {
  constructor(searchValue, replaceValue) {
    super()
    this._search = searchValue; this._replace = replaceValue
    this._tail = ''
  }
  _transform(chunk, enc, callback) {
    const pieces = (this._tail + chunk).split(this._search)
    this._tail = pieces[pieces.length - 1]
    const toOutput = pieces.slice(0, -1).join(this._replace)
    if (toOutput) this.push(toOutput)
    callback()
  }
  _flush(callback) {
    this.push(this._tail)
    callback()
  }
}
```

## Pipeline (preferred over .pipe())

```js
import { pipeline } from 'stream/promises'

// File gzip + encrypt pipeline
await pipeline(
  fs.createReadStream('data.csv'),
  createGzip(),
  createCipheriv('aes-256-gcm', key, iv),
  fs.createWriteStream('data.csv.gz.enc')
)

// With error handling
try {
  await pipeline(source, transform, dest)
} catch (err) {
  console.error('Pipeline failed:', err)
  // All streams are automatically destroyed on error
}
```

## Backpressure

```js
// Writable signals backpressure via write() return value
const readable = createReadStream('big-file.csv')
const writable = createWriteStream('output.csv')

readable.on('data', chunk => {
  const canContinue = writable.write(chunk)
  if (!canContinue) {
    readable.pause()                         // stop reading
    writable.once('drain', () => readable.resume())  // resume when buffer clears
  }
})
readable.on('end', () => writable.end())
// NOTE: pipeline() handles backpressure automatically — prefer it
```

## Parallel Transform Streams

```js
import { Transform } from 'stream'

class ParallelTransform extends Transform {
  constructor(concurrency, transform) {
    super({ objectMode: true })
    this._concurrency = concurrency
    this._transform = transform
    this._running = 0
    this._terminateCb = null
  }
  _transform(chunk, enc, done) {
    this._running++
    this._transformFn(chunk, (err, result) => {
      this._running--
      if (err) return this.emit('error', err)
      this.push(result)
      if (this._terminateCb && this._running === 0) this._terminateCb()
    })
    if (this._running < this._concurrency) done()   // accept more input
    else this._transformDone = done                  // pause input
  }
  _flush(done) {
    if (this._running > 0) this._terminateCb = done
    else done()
  }
}
```

## Forking Streams

```js
// Read once, write to multiple destinations
import { PassThrough } from 'stream'

const source = fs.createReadStream('input.dat')
const fork1 = new PassThrough()
const fork2 = new PassThrough()

source.pipe(fork1)
source.pipe(fork2)

fork1.pipe(createGzip()).pipe(fs.createWriteStream('output.gz'))
fork2.pipe(sha256Stream()).pipe(fs.createWriteStream('output.sha'))
```

## Merging Streams

```js
import { PassThrough } from 'stream'

function merge(...streams) {
  const passThrough = new PassThrough({ objectMode: true })
  let ended = 0
  for (const stream of streams) {
    stream.pipe(passThrough, { end: false })
    stream.on('end', () => {
      if (++ended === streams.length) passThrough.end()
    })
  }
  return passThrough
}

const merged = merge(stream1, stream2, stream3)
merged.pipe(dest)
```

## Object Mode Streams

```js
// Object streams emit JS objects instead of Buffers
const transform = new Transform({
  objectMode: true,
  transform(record, enc, cb) {
    // record is a plain object, not a Buffer
    this.push({ ...record, processed: true })
    cb()
  }
})

// CSV → objects → filter → JSON
await pipeline(
  fs.createReadStream('data.csv'),
  new CSVParserTransform(),       // objectMode output
  new FilterTransform(r => r.age > 18),  // objectMode in+out
  new JSONStringifyTransform(),   // objectMode input, Buffer output
  fs.createWriteStream('adults.json')
)
```
