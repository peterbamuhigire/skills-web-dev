# Realtime — Deep Dive

## WebSockets with `ws`

```js
import { WebSocketServer } from 'ws'

const wss = new WebSocketServer({ port: 8080 })

wss.on('connection', (ws, req) => {
  const ip = req.socket.remoteAddress
  console.log(`Client connected: ${ip}`)

  ws.on('message', (data) => {
    const msg = JSON.parse(data.toString())
    // Broadcast to all connected clients
    wss.clients.forEach(client => {
      if (client.readyState === ws.OPEN) {
        client.send(JSON.stringify({ ...msg, from: ip }))
      }
    })
  })

  ws.on('close', () => console.log(`Client disconnected: ${ip}`))
  ws.on('error', err => console.error('WS error:', err))

  // Heartbeat: detect zombie connections
  ws.isAlive = true
  ws.on('pong', () => { ws.isAlive = true })
})

// Ping all clients every 30s; terminate if no pong received
const interval = setInterval(() => {
  wss.clients.forEach(ws => {
    if (!ws.isAlive) return ws.terminate()
    ws.isAlive = false
    ws.ping()
  })
}, 30_000)

wss.on('close', () => clearInterval(interval))
```

## WebSocket Client

```js
import WebSocket from 'ws'

const ws = new WebSocket('ws://localhost:8080')

ws.on('open', () => ws.send(JSON.stringify({ type: 'hello' })))
ws.on('message', data => console.log(JSON.parse(data.toString())))
ws.on('error', err => console.error(err))
ws.on('close', (code, reason) => {
  console.log(`Closed: ${code} ${reason}`)
  // Reconnect with exponential backoff
  setTimeout(connect, 2000)
})
```

## Exponential Backoff Reconnection

```js
class ReconnectingWS {
  #url; #ws; #delay = 1000; #maxDelay = 30_000; #listeners = {}

  constructor(url) { this.#url = url; this.#connect() }

  #connect() {
    this.#ws = new WebSocket(this.#url)
    this.#ws.on('open', () => {
      this.#delay = 1000  // reset on success
      this.#listeners.open?.()
    })
    this.#ws.on('message', data => this.#listeners.message?.(data))
    this.#ws.on('close', () => {
      setTimeout(() => this.#connect(), this.#delay)
      this.#delay = Math.min(this.#delay * 2, this.#maxDelay)
    })
    this.#ws.on('error', err => this.#listeners.error?.(err))
  }

  on(event, handler) { this.#listeners[event] = handler; return this }
  send(data) { this.#ws.send(JSON.stringify(data)) }
}
```

## Server-Sent Events (SSE)

```js
// Server — Express SSE endpoint
app.get('/events', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream')
  res.setHeader('Cache-Control', 'no-cache')
  res.setHeader('Connection', 'keep-alive')
  res.flushHeaders()  // send headers immediately

  let seq = 0
  const timer = setInterval(() => {
    res.write(`id: ${seq++}\n`)
    res.write(`event: update\n`)
    res.write(`data: ${JSON.stringify({ time: Date.now() })}\n\n`)
  }, 1000)

  req.on('close', () => {
    clearInterval(timer)
    res.end()
  })
})
```

```js
// Client — browser EventSource
const es = new EventSource('/events')
es.addEventListener('update', e => {
  const data = JSON.parse(e.data)
  console.log('Received:', data)
})
es.onerror = () => {
  // Browser auto-reconnects; implement custom logic here if needed
  console.log('SSE error — browser will reconnect')
}
```

## SSE vs WebSocket Decision

| Factor | SSE | WebSocket |
|--------|-----|-----------|
| Direction | Server → Client only | Bidirectional |
| Protocol | HTTP/1.1 | WS (upgrade) |
| Auto-reconnect | Built into browser | Manual |
| Proxy/firewall | Works through standard HTTP | May be blocked |
| Use case | Live feeds, notifications | Chat, gaming, collaboration |

**Rule:** Use SSE when you only need server-push. Use WebSocket for interactive, bidirectional communication.

## Multi-Tenant Channel Isolation

```js
// Room-based isolation (Socket.IO-style with raw ws)
const rooms = new Map()  // roomId → Set<WebSocket>

function joinRoom(ws, roomId) {
  if (!rooms.has(roomId)) rooms.set(roomId, new Set())
  rooms.get(roomId).add(ws)
  ws.roomId = roomId
}

function broadcastToRoom(roomId, message, excludeWs = null) {
  const room = rooms.get(roomId)
  if (!room) return
  const payload = JSON.stringify(message)
  room.forEach(client => {
    if (client !== excludeWs && client.readyState === WebSocket.OPEN) {
      client.send(payload)
    }
  })
}

function leaveRoom(ws) {
  const room = rooms.get(ws.roomId)
  if (room) {
    room.delete(ws)
    if (room.size === 0) rooms.delete(ws.roomId)
  }
}

// Wire up on connection
wss.on('connection', (ws, req) => {
  const tenantId = extractTenantFromToken(req)  // from JWT or cookie
  joinRoom(ws, tenantId)

  ws.on('message', data => {
    const msg = JSON.parse(data.toString())
    broadcastToRoom(ws.roomId, msg, ws)  // broadcast to tenant peers
  })

  ws.on('close', () => leaveRoom(ws))
})
```

## Socket.IO (higher-level)

```js
import { Server } from 'socket.io'
import { createServer } from 'http'

const httpServer = createServer(app)
const io = new Server(httpServer, {
  cors: { origin: process.env.CLIENT_ORIGIN }
})

// Middleware for auth
io.use((socket, next) => {
  const token = socket.handshake.auth.token
  try {
    socket.user = verifyJwt(token)
    next()
  } catch (err) {
    next(new Error('Unauthorized'))
  }
})

io.on('connection', (socket) => {
  // Auto-join tenant room
  socket.join(`tenant:${socket.user.tenantId}`)

  socket.on('chat:message', (msg) => {
    // Emit to everyone in room (including sender)
    io.to(`tenant:${socket.user.tenantId}`).emit('chat:message', {
      ...msg,
      from: socket.user.name,
      at: new Date().toISOString()
    })
  })

  socket.on('disconnect', () => {
    console.log(`User ${socket.user.id} disconnected`)
  })
})

httpServer.listen(3000)
```

## Live Dashboard Pattern

```js
// Emit changes from any part of the app by importing io
// Decouple via EventEmitter

import { EventEmitter } from 'events'
export const appEvents = new EventEmitter()

// In business logic layer:
appEvents.emit('order:created', { id, tenantId, total })

// In socket layer:
appEvents.on('order:created', ({ id, tenantId, total }) => {
  io.to(`tenant:${tenantId}`).emit('dashboard:update', {
    type: 'NEW_ORDER',
    payload: { id, total }
  })
})
```

## WebSocket with Express Upgrade

```js
import { createServer } from 'http'
import { WebSocketServer } from 'ws'

const app = express()
const server = createServer(app)
const wss = new WebSocketServer({ noServer: true })

// Manually handle upgrade — allows auth before WS handshake
server.on('upgrade', (req, socket, head) => {
  const token = new URL(req.url, 'http://x').searchParams.get('token')
  if (!verifyJwt(token)) {
    socket.write('HTTP/1.1 401 Unauthorized\r\n\r\n')
    socket.destroy()
    return
  }
  wss.handleUpgrade(req, socket, head, ws => {
    wss.emit('connection', ws, req)
  })
})

server.listen(3000)
```
