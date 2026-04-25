# Resilience Patterns for PHP Services

Circuit breakers, idempotent handlers, and binary serialization for building resilient, high-throughput PHP services.

**Source:** Garcia (2023) Ch6/Ch10 identified these gaps; implementations based on production patterns.

---

## Circuit Breaker Pattern

Prevents cascading failures when an external service is down. Instead of retrying endlessly, the circuit "opens" after a threshold of failures and fails fast.

### States

```
CLOSED → (failures exceed threshold) → OPEN → (timeout expires) → HALF-OPEN
  ↑                                                                    |
  └────────── (success in half-open) ──────────────────────────────────┘
                         (failure in half-open) → OPEN
```

### Implementation

```php
<?php
declare(strict_types=1);

final class CircuitBreaker
{
    private const STATE_CLOSED    = 'closed';
    private const STATE_OPEN      = 'open';
    private const STATE_HALF_OPEN = 'half_open';

    public function __construct(
        private \Redis $redis,
        private string $service,
        private int $failureThreshold = 5,
        private int $openTimeoutSeconds = 30,
        private int $halfOpenMaxAttempts = 2,
    ) {}

    /**
     * Execute a callable through the circuit breaker.
     * @throws CircuitOpenException if circuit is open
     */
    public function call(callable $fn): mixed
    {
        $state = $this->getState();

        if ($state === self::STATE_OPEN) {
            throw new CircuitOpenException("Circuit open for service: {$this->service}");
        }

        try {
            $result = $fn();
            $this->recordSuccess();
            return $result;
        } catch (\Throwable $e) {
            $this->recordFailure();
            throw $e;
        }
    }

    /**
     * Execute with a fallback when circuit is open.
     */
    public function callWithFallback(callable $fn, callable $fallback): mixed
    {
        try {
            return $this->call($fn);
        } catch (CircuitOpenException) {
            return $fallback();
        }
    }

    private function getState(): string
    {
        $key = "cb:{$this->service}";
        $data = $this->redis->hGetAll($key);

        if (empty($data)) {
            return self::STATE_CLOSED;
        }

        $failures = (int) ($data['failures'] ?? 0);
        $openedAt = (int) ($data['opened_at'] ?? 0);
        $state = $data['state'] ?? self::STATE_CLOSED;

        if ($state === self::STATE_OPEN) {
            if (time() - $openedAt >= $this->openTimeoutSeconds) {
                return self::STATE_HALF_OPEN;
            }
            return self::STATE_OPEN;
        }

        return $state;
    }

    private function recordSuccess(): void
    {
        $key = "cb:{$this->service}";
        $this->redis->hMSet($key, [
            'failures' => 0,
            'state'    => self::STATE_CLOSED,
        ]);
        $this->redis->expire($key, 300);
    }

    private function recordFailure(): void
    {
        $key = "cb:{$this->service}";
        $failures = (int) $this->redis->hIncrBy($key, 'failures', 1);
        if ($failures >= $this->failureThreshold) {
            $this->redis->hMSet($key, [
                'state'     => self::STATE_OPEN,
                'opened_at' => time(),
            ]);
        }
        $this->redis->expire($key, 300);
    }
}

final class CircuitOpenException extends \RuntimeException {}
```

### Usage

```php
$breaker = new CircuitBreaker($redis, 'payment-gateway', failureThreshold: 3, openTimeoutSeconds: 60);

// Basic usage — throws CircuitOpenException if open
$result = $breaker->call(fn() => $paymentApi->charge($amount));

// With fallback — returns fallback value when circuit is open
$result = $breaker->callWithFallback(
    fn() => $shippingApi->getRate($address),
    fn() => ['rate' => 5.00, 'source' => 'cached_default'],
);
```

---

## Idempotent Request Handlers

Ensure that processing the same request twice produces the same result. Critical for webhooks, payment callbacks, and queue consumers.

### Database-Backed Idempotency

```php
<?php
declare(strict_types=1);

final class IdempotencyGuard
{
    public function __construct(private \PDO $pdo) {}

    /**
     * Execute a callable only once per idempotency key.
     * Returns cached result on duplicate requests.
     */
    public function once(string $key, callable $fn): array
    {
        // Check if already processed
        $stmt = $this->pdo->prepare(
            'SELECT result, status FROM idempotency_keys WHERE idempotency_key = ? FOR UPDATE'
        );
        $stmt->execute([$key]);
        $existing = $stmt->fetch(\PDO::FETCH_ASSOC);

        if ($existing && $existing['status'] === 'completed') {
            return json_decode($existing['result'], true, 512, JSON_THROW_ON_ERROR);
        }

        // Lock the key (insert or update to 'processing')
        $this->pdo->prepare(
            'INSERT INTO idempotency_keys (idempotency_key, status, created_at)
             VALUES (?, ?, NOW())
             ON DUPLICATE KEY UPDATE status = ?'
        )->execute([$key, 'processing', 'processing']);

        try {
            $result = $fn();
            $this->pdo->prepare(
                'UPDATE idempotency_keys SET status = ?, result = ?, completed_at = NOW()
                 WHERE idempotency_key = ?'
            )->execute(['completed', json_encode($result, JSON_THROW_ON_ERROR), $key]);
            return $result;
        } catch (\Throwable $e) {
            $this->pdo->prepare(
                'UPDATE idempotency_keys SET status = ?, error = ? WHERE idempotency_key = ?'
            )->execute(['failed', $e->getMessage(), $key]);
            throw $e;
        }
    }
}
```

### Schema

```sql
CREATE TABLE idempotency_keys (
    idempotency_key VARCHAR(255) PRIMARY KEY,
    status ENUM('processing', 'completed', 'failed') NOT NULL,
    result JSON DEFAULT NULL,
    error TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    KEY idx_cleanup (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cleanup old keys (run daily)
-- DELETE FROM idempotency_keys WHERE created_at < DATE_SUB(NOW(), INTERVAL 7 DAY);
```

### API Middleware Integration

```php
// Client sends: POST /api/orders  Header: Idempotency-Key: abc-123
$idempotencyKey = $request->getHeaderLine('Idempotency-Key');
if (empty($idempotencyKey)) {
    return new Response(400, body: 'Idempotency-Key header required for POST requests');
}

$guard = new IdempotencyGuard($pdo);
$result = $guard->once($idempotencyKey, function () use ($request) {
    return $this->orderService->create($request->getParsedBody());
});
return new Response(200, body: json_encode($result));
```

---

## Binary Serialization for High-Throughput APIs

When JSON overhead matters (high-frequency internal APIs, large payloads), use binary formats.

### MessagePack (Recommended for PHP)

Compact binary format, ~30% smaller than JSON, faster to encode/decode. Drop-in replacement.

```bash
# Install PHP extension
pecl install msgpack
# Or via Composer (pure PHP, slower)
composer require rybakit/msgpack
```

```php
<?php
declare(strict_types=1);

// With ext-msgpack (fastest)
$packed = msgpack_pack(['user_id' => 42, 'name' => 'John', 'roles' => ['admin', 'user']]);
$data = msgpack_unpack($packed);

// Size comparison
$jsonSize = strlen(json_encode($data));      // ~58 bytes
$msgpackSize = strlen(msgpack_pack($data));  // ~38 bytes (35% smaller)
```

### Content Negotiation Middleware

```php
<?php
declare(strict_types=1);

final class ContentNegotiationMiddleware
{
    public function handle(Request $request, callable $next): Response
    {
        $response = $next($request);
        $accept = $request->getHeaderLine('Accept');

        if (str_contains($accept, 'application/msgpack') && extension_loaded('msgpack')) {
            $data = json_decode((string) $response->getBody(), true);
            return $response
                ->withHeader('Content-Type', 'application/msgpack')
                ->withBody(new StringStream(msgpack_pack($data)));
        }

        return $response; // Default JSON
    }
}
```

### Format Comparison

| Format | Size (typical) | Encode Speed | Decode Speed | Human Readable | Schema |
|--------|---------------|-------------|-------------|----------------|--------|
| JSON | Baseline | Baseline | Baseline | Yes | No |
| MessagePack | 30-40% smaller | 2-3x faster | 2-3x faster | No | No |
| Protocol Buffers | 50-70% smaller | 5-10x faster | 5-10x faster | No | Yes (.proto) |

**Decision:** Use MessagePack for internal service-to-service APIs where you control both sides. Keep JSON for public APIs (human-debuggable, universal client support).

---

## PHP FFI (Foreign Function Interface)

Call C libraries directly from PHP without building a custom extension. PHP 7.4+.

```php
<?php
declare(strict_types=1);

// Call a C math library function
$ffi = FFI::cdef("
    double sqrt(double x);
    int abs(int j);
", "libm.so.6");  // Linux; use "msvcrt.dll" on Windows

echo $ffi->sqrt(144.0);  // 12.0
echo $ffi->abs(-42);      // 42

// Load a custom C library for compute-heavy work
$ffi = FFI::cdef("
    typedef struct { double lat; double lng; } Point;
    double haversine_distance(Point a, Point b);
", "/path/to/libgeo.so");

$a = $ffi->new("Point");
$a->lat = 0.3476;  // Kampala
$a->lng = 32.5825;
$b = $ffi->new("Point");
$b->lat = -1.2921; // Nairobi
$b->lng = 36.8219;

$distance = $ffi->haversine_distance($a, $b);
```

### When to Use FFI

| Use Case | FFI? | Why |
|----------|------|-----|
| Image processing hotspot | Yes | C is 100x+ faster for pixel manipulation |
| Cryptographic operations | **No** | Use Libsodium (already in PHP core) |
| String/array manipulation | **No** | PHP built-ins are already C-implemented |
| Machine learning inference | Yes | Call C/C++ model libraries |
| GIS distance calculations | Maybe | Only if doing millions of calculations per request |

### php.ini for FFI

```ini
; Development
ffi.enable = true
; Production (preloaded only — security best practice)
ffi.enable = preload
ffi.preload = /app/ffi/preload.php
```

---

## Anti-Patterns

- **No circuit breaker on external calls** — one slow API cascades failures across your entire system.
- **Non-idempotent POST handlers** — duplicate webhook delivery creates duplicate records.
- **Binary format for public APIs** — clients can't debug with curl; use JSON externally.
- **FFI in hot loops without preload** — `FFI::cdef()` parsing on every request is slow; preload once.
- **Ignoring Idempotency-Key header** — standard for POST/PATCH; clients expect duplicate safety.

---

*Reference for php-modern-standards skill. Source: Garcia (2023) gap analysis.*
