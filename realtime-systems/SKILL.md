---
name: realtime-systems
description: Use when building real-time features — live dashboards, notifications,
  chat, collaborative editing, order tracking, or any feature requiring push updates
  from server to client. Covers WebSockets, SSE, multi-tenant channel isolation, and...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Real-Time Systems

<!-- dual-compat-start -->
## Use When

- Use when building real-time features — live dashboards, notifications, chat, collaborative editing, order tracking, or any feature requiring push updates from server to client. Covers WebSockets, SSE, multi-tenant channel isolation, and...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `realtime-systems` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Overview

Real-time features require the server to push data to clients without polling. Two primary patterns:
- **SSE** — server-to-client only; simpler, HTTP-based, auto-reconnects
- **WebSockets** — bidirectional; required for chat, collaborative editing, live input

**Core rule:** Use SSE for dashboards and notifications. Use WebSockets only when the client must also send real-time data.

---

## Pattern Selection

| Feature | Use |
|---|---|
| Live dashboard updates | SSE |
| Push notifications | SSE |
| Order/job status tracking | SSE |
| Chat / messaging | WebSocket |
| Collaborative document editing | WebSocket |
| Live bidding / multiplayer | WebSocket |
| Typing indicators | WebSocket |

---

## Server-Sent Events (PHP)

### Server Endpoint

```php
// GET /api/v1/stream/dashboard?franchise_id=...
header('Content-Type: text/event-stream');
header('Cache-Control: no-cache');
header('X-Accel-Buffering: no');  // Nginx: disable buffering

$franchiseId = getSession('franchise_id');  // NEVER from query string
if (!$franchiseId) { http_response_code(401); exit; }

// Stream loop
while (true) {
    $data = getDashboardSnapshot($franchiseId);

    echo "id: " . time() . "\n";
    echo "event: dashboard_update\n";
    echo "data: " . json_encode($data) . "\n\n";

    ob_flush(); flush();

    if (connection_aborted()) break;
    sleep(5);  // Poll interval (replace with DB trigger listener for production)
}
```

### Client Connection

```javascript
class RealtimeStream {
    constructor(endpoint) {
        this.endpoint = endpoint;
        this.reconnectDelay = 1000;
        this.connect();
    }

    connect() {
        this.source = new EventSource(this.endpoint);

        this.source.addEventListener('dashboard_update', (e) => {
            const data = JSON.parse(e.data);
            this.onUpdate(data);
        });

        this.source.onerror = () => {
            this.source.close();
            // Exponential backoff: 1s → 2s → 4s → max 30s
            setTimeout(() => this.connect(),
                Math.min(this.reconnectDelay *= 2, 30000));
        };

        this.source.onopen = () => {
            this.reconnectDelay = 1000; // Reset on success
        };
    }

    onUpdate(data) {
        document.dispatchEvent(new CustomEvent('dashboardData', { detail: data }));
    }

    disconnect() { this.source.close(); }
}

const stream = new RealtimeStream('/api/v1/stream/dashboard');
```

---

## WebSockets (PHP + JavaScript)

### PHP WebSocket Server (Ratchet)

```php
// composer require cboden/ratchet
use Ratchet\MessageComponentInterface;
use Ratchet\ConnectionInterface;

class TenantAwareSocket implements MessageComponentInterface {
    protected SplObjectStorage $clients;
    protected array $channelMap = [];  // connectionId => franchise_id

    public function __construct() {
        $this->clients = new SplObjectStorage();
    }

    public function onOpen(ConnectionInterface $conn) {
        // Authenticate via query parameter token (JWT only — no session cookies over WS)
        $query = $conn->httpRequest->getUri()->getQuery();
        parse_str($query, $params);

        $payload = verifyJwt($params['token'] ?? '');
        if (!$payload) { $conn->close(); return; }

        $this->clients->attach($conn);
        $this->channelMap[$conn->resourceId] = $payload['franchise_id'];
    }

    public function onMessage(ConnectionInterface $from, $msg) {
        $data = json_decode($msg, true);
        $franchiseId = $this->channelMap[$from->resourceId] ?? null;
        if (!$franchiseId) { $from->close(); return; }

        // Validate action
        $allowed = ['CURSOR_MOVE', 'DOC_EDIT', 'PRESENCE'];
        if (!in_array($data['type'] ?? '', $allowed)) return;

        // Broadcast only to same franchise
        $this->broadcastToFranchise($franchiseId, $msg, $from);
    }

    public function onClose(ConnectionInterface $conn) {
        $this->clients->detach($conn);
        unset($this->channelMap[$conn->resourceId]);
    }

    public function onError(ConnectionInterface $conn, \Exception $e) {
        $conn->close();
    }

    private function broadcastToFranchise(int $franchiseId, string $msg, ConnectionInterface $except): void {
        foreach ($this->clients as $client) {
            if ($client !== $except
                && ($this->channelMap[$client->resourceId] ?? null) === $franchiseId) {
                $client->send($msg);
            }
        }
    }
}
```

### JavaScript WebSocket Client

```javascript
class RealtimeSocket {
    constructor(wsUrl, token) {
        this.wsUrl = `${wsUrl}?token=${token}`;
        this.ws = null;
        this.reconnectDelay = 1000;
        this.handlers = {};
        this.connect();
    }

    connect() {
        this.ws = new WebSocket(this.wsUrl);

        this.ws.onmessage = (e) => {
            const msg = JSON.parse(e.data);
            (this.handlers[msg.type] || []).forEach(fn => fn(msg));
        };

        this.ws.onclose = () => {
            setTimeout(() => this.connect(),
                Math.min(this.reconnectDelay *= 2, 30000));
        };

        this.ws.onopen = () => {
            this.reconnectDelay = 1000;
        };
    }

    on(type, handler) {
        (this.handlers[type] ??= []).push(handler);
    }

    send(type, payload) {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type, ...payload }));
        }
    }
}

// Usage
const socket = new RealtimeSocket('wss://app.example.com/ws', userJwt);
socket.on('DOC_EDIT', ({ userId, delta }) => applyDelta(delta));
socket.send('CURSOR_MOVE', { x: 150, y: 200 });
```

---

## Multi-Tenant Channel Isolation

**Critical rule:** Clients must NEVER receive messages from other franchises.

```
Channel naming convention: {event_type}:{franchise_id}:{optional_resource_id}

Examples:
  dashboard:42           → franchise 42 dashboard
  order_status:42:1001   → franchise 42, order 1001
  doc_collab:42:99       → franchise 42, document 99
```

**Isolation checklist:**
- [ ] Authenticate on connection — close unauthenticated connections immediately
- [ ] Extract `franchise_id` from JWT/session — NEVER from client message payload
- [ ] Store `franchise_id` server-side in connection map
- [ ] Filter all broadcasts by `franchise_id` before sending
- [ ] Rate limit per connection (100 messages/minute)

---

## Database-Driven Push (Long-Polling / MySQL LISTEN)

For systems without a persistent WebSocket server, use a polling approach that reduces DB load:

```php
// Long-poll endpoint: client waits up to 30s for new data
$lastId = (int) ($_GET['last_event_id'] ?? 0);
$deadline = time() + 30;

while (time() < $deadline) {
    $stmt = $db->prepare('
        SELECT * FROM realtime_events
        WHERE franchise_id = ? AND id > ?
        ORDER BY id ASC LIMIT 50
    ');
    $stmt->execute([$franchiseId, $lastId]);
    $events = $stmt->fetchAll();

    if (!empty($events)) {
        echo json_encode(['events' => $events]);
        exit;
    }

    usleep(500_000);  // 500ms poll interval
}

echo json_encode(['events' => []]);  // Empty on timeout — client retries
```

```sql
CREATE TABLE realtime_events (
    id           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    franchise_id BIGINT UNSIGNED NOT NULL,
    event_type   VARCHAR(50) NOT NULL,
    payload      JSON NOT NULL,
    created_at   DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    INDEX idx_franchise_id (franchise_id, id)
) ENGINE=InnoDB;
```

---

## Live Collaboration Patterns

### Presence (Who Is Online)

```sql
CREATE TABLE active_sessions (
    session_key  VARCHAR(100) PRIMARY KEY,
    franchise_id BIGINT UNSIGNED NOT NULL,
    user_id      BIGINT UNSIGNED NOT NULL,
    resource     VARCHAR(100),       -- e.g. 'document:99'
    last_ping    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_franchise_resource (franchise_id, resource)
);
-- Clean up: DELETE FROM active_sessions WHERE last_ping < NOW() - INTERVAL 30 SECOND
```

### Operational Transform (Simple Last-Write-Wins)

For basic collaborative editing where conflicts are rare:

```javascript
// Client: include document version with every edit
socket.send('DOC_EDIT', {
    docId: 99,
    version: localVersion,  // Last known server version
    delta: { op: 'insert', pos: 45, text: 'hello' }
});

// Server: reject if version mismatch — client must re-fetch and retry
if (msg.version !== currentVersion) {
    from.send(JSON.stringify({ type: 'EDIT_REJECTED', docId: msg.docId }));
    return;
}
```

---

## Nginx Configuration

```nginx
# WebSocket proxy
location /ws {
    proxy_pass http://localhost:8080;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 3600s;
}

# SSE proxy
location /api/v1/stream/ {
    proxy_pass http://localhost:80;
    proxy_buffering off;
    proxy_cache off;
    proxy_set_header X-Accel-Buffering no;
}
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| `franchise_id` from client message | Tenant spoofing | Extract from JWT/session only |
| Broadcast to all connections | Data leak across tenants | Filter by `franchise_id` |
| No reconnection logic | Silent disconnects | Exponential backoff on client |
| Polling every 500ms | DB overload | SSE or long-poll with sleep |
| WebSocket for notifications | Unnecessary complexity | Use SSE |
| Unauthenticated WS connections | Anyone can connect | Auth check in `onOpen`, close if fails |

---

## Implementation Checklist

- [ ] Choose SSE vs WebSocket based on directionality
- [ ] Authenticate every connection before accepting
- [ ] Store `franchise_id` server-side in connection/channel map
- [ ] Broadcast filtered by `franchise_id` only
- [ ] Client implements exponential backoff reconnection
- [ ] Nginx configured for proxy buffering off (SSE) / upgrade (WS)
- [ ] Rate limit per connection
- [ ] Heartbeat to detect stale connections (ping every 30s)
- [ ] `realtime_events` table indexed on `(franchise_id, id)`
