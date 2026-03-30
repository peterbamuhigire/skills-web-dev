# Rate Limiting Algorithms for PHP

Production-grade rate limiting patterns using Redis. Choose the right algorithm, implement it correctly, integrate as middleware.

**Source:** Garcia (2023) Ch10 identified this gap; implementations based on Redis documentation and production patterns.

---

## Algorithm Comparison

| Algorithm | Burst Tolerance | Memory | Precision | Best For |
|-----------|----------------|--------|-----------|----------|
| **Fixed Window** | High at boundaries | Low | Low | Simple quotas |
| **Sliding Window** | Smooth | Medium | High | API rate limits |
| **Token Bucket** | Configurable burst | Low | Medium | User-facing APIs |
| **Leaky Bucket** | None (constant rate) | Low | High | Background job throttling |

---

## Fixed Window Counter

Simplest approach. Counts requests per fixed time window (e.g., per minute). Weakness: burst at window boundary allows 2x the limit.

```php
<?php
declare(strict_types=1);

final class FixedWindowLimiter
{
    public function __construct(private \Redis $redis) {}

    public function attempt(string $key, int $maxRequests, int $windowSeconds): bool
    {
        $windowKey = "rl:fw:{$key}:" . (int)(time() / $windowSeconds);
        $current = (int) $this->redis->incr($windowKey);
        if ($current === 1) {
            $this->redis->expire($windowKey, $windowSeconds);
        }
        return $current <= $maxRequests;
    }
}
```

---

## Sliding Window Log

Tracks each request timestamp. Most precise but highest memory usage. Good for low-volume, high-value endpoints.

```php
<?php
declare(strict_types=1);

final class SlidingWindowLimiter
{
    public function __construct(private \Redis $redis) {}

    public function attempt(string $key, int $maxRequests, int $windowSeconds): bool
    {
        $now = microtime(true);
        $windowStart = $now - $windowSeconds;
        $sortedSetKey = "rl:sw:{$key}";

        $pipe = $this->redis->multi(\Redis::PIPELINE);
        $pipe->zRemRangeByScore($sortedSetKey, '-inf', (string) $windowStart);
        $pipe->zAdd($sortedSetKey, $now, "{$now}:" . random_int(0, PHP_INT_MAX));
        $pipe->zCard($sortedSetKey);
        $pipe->expire($sortedSetKey, $windowSeconds);
        $results = $pipe->exec();

        $count = (int) $results[2];
        if ($count > $maxRequests) {
            $this->redis->zRemRangeByRank($sortedSetKey, -1, -1);
            return false;
        }
        return true;
    }

    /** Seconds until next request is allowed */
    public function retryAfter(string $key, int $maxRequests, int $windowSeconds): float
    {
        $sortedSetKey = "rl:sw:{$key}";
        $oldest = $this->redis->zRange($sortedSetKey, 0, 0, true);
        if (empty($oldest)) {
            return 0.0;
        }
        $oldestTime = (float) array_values($oldest)[0];
        return max(0.0, $oldestTime + $windowSeconds - microtime(true));
    }
}
```

---

## Token Bucket (Recommended for APIs)

Allows controlled bursts up to bucket capacity, then enforces steady rate. Best balance of flexibility and fairness.

```php
<?php
declare(strict_types=1);

final class TokenBucketLimiter
{
    public function __construct(private \Redis $redis) {}

    /**
     * @param string $key      Unique identifier (e.g., "tenant:42" or "ip:1.2.3.4")
     * @param int    $capacity Maximum tokens (burst size)
     * @param float  $refillRate Tokens added per second
     * @param int    $cost     Tokens consumed per request (default 1)
     */
    public function attempt(string $key, int $capacity, float $refillRate, int $cost = 1): array
    {
        $bucketKey = "rl:tb:{$key}";
        $now = microtime(true);

        // Atomic Lua script — no race conditions
        $lua = <<<'LUA'
            local key = KEYS[1]
            local capacity = tonumber(ARGV[1])
            local refill_rate = tonumber(ARGV[2])
            local now = tonumber(ARGV[3])
            local cost = tonumber(ARGV[4])

            local data = redis.call('HMGET', key, 'tokens', 'last_refill')
            local tokens = tonumber(data[1]) or capacity
            local last_refill = tonumber(data[2]) or now

            -- Refill tokens based on elapsed time
            local elapsed = math.max(0, now - last_refill)
            tokens = math.min(capacity, tokens + (elapsed * refill_rate))

            local allowed = 0
            local retry_after = 0
            if tokens >= cost then
                tokens = tokens - cost
                allowed = 1
            else
                retry_after = (cost - tokens) / refill_rate
            end

            redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
            redis.call('EXPIRE', key, math.ceil(capacity / refill_rate) + 1)

            return {allowed, tostring(tokens), tostring(retry_after)}
        LUA;

        $result = $this->redis->eval($lua, [$bucketKey, $capacity, $refillRate, $now, $cost], 1);
        return [
            'allowed'     => (bool) $result[0],
            'remaining'   => (int) floor((float) $result[1]),
            'retry_after' => round((float) $result[2], 2),
        ];
    }
}
```

**Usage:**
```php
$limiter = new TokenBucketLimiter($redis);
// 100 requests max, refill 10 tokens/sec (sustained 10 req/s, burst to 100)
$result = $limiter->attempt("tenant:{$tenantId}", 100, 10.0);
if (!$result['allowed']) {
    http_response_code(429);
    header("Retry-After: {$result['retry_after']}");
    exit;
}
```

---

## Leaky Bucket (Constant Rate)

Processes requests at a fixed rate regardless of arrival pattern. Smooths traffic completely — no bursts.

```php
<?php
declare(strict_types=1);

final class LeakyBucketLimiter
{
    public function __construct(private \Redis $redis) {}

    /**
     * @param string $key      Unique identifier
     * @param int    $capacity Queue size (max pending requests)
     * @param float  $leakRate Requests processed per second
     */
    public function attempt(string $key, int $capacity, float $leakRate): array
    {
        $bucketKey = "rl:lb:{$key}";
        $now = microtime(true);

        $lua = <<<'LUA'
            local key = KEYS[1]
            local capacity = tonumber(ARGV[1])
            local leak_rate = tonumber(ARGV[2])
            local now = tonumber(ARGV[3])

            local data = redis.call('HMGET', key, 'water', 'last_leak')
            local water = tonumber(data[1]) or 0
            local last_leak = tonumber(data[2]) or now

            -- Leak water based on elapsed time
            local elapsed = math.max(0, now - last_leak)
            water = math.max(0, water - (elapsed * leak_rate))

            local allowed = 0
            if water < capacity then
                water = water + 1
                allowed = 1
            end

            redis.call('HMSET', key, 'water', water, 'last_leak', now)
            redis.call('EXPIRE', key, math.ceil(capacity / leak_rate) + 1)

            return {allowed, tostring(water), tostring(capacity - water)}
        LUA;

        $result = $this->redis->eval($lua, [$bucketKey, $capacity, $leakRate, $now], 1);
        return [
            'allowed'   => (bool) $result[0],
            'queue_size' => (int) floor((float) $result[1]),
            'remaining' => (int) floor((float) $result[2]),
        ];
    }
}
```

---

## PSR-15 Middleware Integration

```php
<?php
declare(strict_types=1);

final class RateLimitMiddleware
{
    public function __construct(
        private TokenBucketLimiter $limiter,
        private int $capacity = 60,
        private float $refillRate = 1.0,
    ) {}

    public function handle(Request $request, callable $next): Response
    {
        $key = $this->resolveKey($request);
        $result = $this->limiter->attempt($key, $this->capacity, $this->refillRate);

        if (!$result['allowed']) {
            return new Response(429, [
                'Retry-After'           => (string) $result['retry_after'],
                'X-RateLimit-Limit'     => (string) $this->capacity,
                'X-RateLimit-Remaining' => '0',
            ], 'Too Many Requests');
        }

        $response = $next($request);
        return $response->withHeaders([
            'X-RateLimit-Limit'     => (string) $this->capacity,
            'X-RateLimit-Remaining' => (string) $result['remaining'],
        ]);
    }

    private function resolveKey(Request $request): string
    {
        // Prefer authenticated tenant/user, fall back to IP
        if ($tenantId = $request->getAttribute('tenant_id')) {
            return "tenant:{$tenantId}";
        }
        return 'ip:' . ($request->getServerParams()['REMOTE_ADDR'] ?? 'unknown');
    }
}
```

---

## Algorithm Decision Guide

```
Need rate limiting?
├─ Simple daily/monthly quota? → Fixed Window
├─ API endpoint protection?
│  ├─ Want to allow bursts? → Token Bucket ← RECOMMENDED DEFAULT
│  └─ Want smooth constant rate? → Leaky Bucket
└─ Need precise per-second control? → Sliding Window
```

**Multi-tenant SaaS:** Use Token Bucket with per-tenant keys and configurable limits per subscription tier.

---

## Response Headers (Standard)

Always include these headers on rate-limited endpoints:

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Max requests in the window |
| `X-RateLimit-Remaining` | Requests left in current window |
| `X-RateLimit-Reset` | Unix timestamp when limit resets |
| `Retry-After` | Seconds until next request allowed (on 429 only) |

---

*Reference for php-modern-standards skill. Source: Garcia (2023) gap analysis.*
