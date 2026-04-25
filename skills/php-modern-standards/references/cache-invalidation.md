# Cache Invalidation Strategies for PHP

"There are only two hard things in Computer Science: cache invalidation and naming things." — Phil Karlton

Production patterns for write strategies, invalidation methods, and multi-tier cache architecture.

**Source:** Garcia (2023) Ch9 identified this gap; implementations based on production patterns.

---

## Write Strategy Comparison

| Strategy | Consistency | Latency | Complexity | Best For |
|----------|------------|---------|------------|----------|
| **Cache-Aside** | Eventual | Low reads | Low | General purpose (default) |
| **Write-Through** | Strong | Higher writes | Medium | Data that must stay consistent |
| **Write-Behind** | Eventual | Low writes | High | Write-heavy workloads |
| **Read-Through** | Eventual | Low reads | Medium | ORM-integrated caching |

---

## Cache-Aside (Lazy Loading) — Default Strategy

Application manages the cache directly. Most common and simplest pattern.

```php
<?php
declare(strict_types=1);

final class CacheAside
{
    public function __construct(private \Redis $redis, private \PDO $pdo) {}

    public function getUser(int $tenantId, int $userId): array
    {
        $key = "t:{$tenantId}:user:{$userId}";
        $cached = $this->redis->get($key);
        if ($cached !== false) {
            return json_decode($cached, true, 512, JSON_THROW_ON_ERROR);
        }

        $stmt = $this->pdo->prepare('SELECT * FROM users WHERE tenant_id = ? AND id = ?');
        $stmt->execute([$tenantId, $userId]);
        $user = $stmt->fetch(\PDO::FETCH_ASSOC);

        if ($user) {
            $this->redis->setex($key, 3600, json_encode($user, JSON_THROW_ON_ERROR));
        }
        return $user ?: [];
    }

    public function updateUser(int $tenantId, int $userId, array $data): void
    {
        $this->pdo->prepare('UPDATE users SET name = ?, email = ? WHERE tenant_id = ? AND id = ?')
            ->execute([$data['name'], $data['email'], $tenantId, $userId]);
        // Invalidate — next read will repopulate
        $this->redis->del("t:{$tenantId}:user:{$userId}");
    }
}
```

**Weakness:** Cache miss storm after invalidation. Mitigate with stampede prevention (see `performance-efficiency.md` RedisCache::rememberWithLock).

---

## Write-Through — Strong Consistency

Write to cache and database simultaneously. Cache is always current.

```php
<?php
declare(strict_types=1);

final class WriteThrough
{
    public function __construct(private \Redis $redis, private \PDO $pdo) {}

    public function updateProduct(int $tenantId, int $productId, array $data): void
    {
        $this->pdo->beginTransaction();
        try {
            $this->pdo->prepare('UPDATE products SET price = ?, stock = ? WHERE tenant_id = ? AND id = ?')
                ->execute([$data['price'], $data['stock'], $tenantId, $productId]);

            $key = "t:{$tenantId}:product:{$productId}";
            // Write to cache atomically with DB commit
            $product = array_merge(['id' => $productId, 'tenant_id' => $tenantId], $data);
            $this->redis->setex($key, 3600, json_encode($product, JSON_THROW_ON_ERROR));

            $this->pdo->commit();
        } catch (\Throwable $e) {
            $this->pdo->rollBack();
            // Invalidate cache on failure — let next read repopulate
            $this->redis->del("t:{$tenantId}:product:{$productId}");
            throw $e;
        }
    }
}
```

**Trade-off:** Higher write latency (two writes per mutation) but reads are always fresh.

---

## Write-Behind (Write-Back) — Async Write

Write to cache immediately, flush to database asynchronously. Lowest write latency.

```php
<?php
declare(strict_types=1);

final class WriteBehind
{
    public function __construct(private \Redis $redis) {}

    public function updateCounter(int $tenantId, string $metric, int $value): void
    {
        $key = "t:{$tenantId}:counter:{$metric}";
        $this->redis->incrBy($key, $value);
        // Queue a flush job — database write happens async
        $this->redis->rPush('flush:counters', json_encode([
            'tenant_id' => $tenantId,
            'metric'    => $metric,
            'value'     => $value,
            'timestamp' => time(),
        ], JSON_THROW_ON_ERROR));
    }
}

// Worker flushes to DB periodically (see message-queues.md)
```

**Risk:** Data loss if Redis crashes before flush. Use only for non-critical data (analytics, counters, view counts).

---

## Tag-Based (Label) Invalidation

Group cache entries by tags for bulk purge. Essential for multi-tenant apps where one change affects many cache entries.

```php
<?php
declare(strict_types=1);

final class TaggedCache
{
    public function __construct(private \Redis $redis) {}

    /**
     * Store a value with one or more tags for grouped invalidation.
     */
    public function set(string $key, mixed $value, int $ttl, array $tags): void
    {
        $pipe = $this->redis->multi(\Redis::PIPELINE);
        $pipe->setex($key, $ttl, json_encode($value, JSON_THROW_ON_ERROR));
        foreach ($tags as $tag) {
            $pipe->sAdd("tag:{$tag}", $key);
            $pipe->expire("tag:{$tag}", $ttl + 60); // Tag outlives entries slightly
        }
        $pipe->exec();
    }

    public function get(string $key): mixed
    {
        $data = $this->redis->get($key);
        return $data !== false ? json_decode($data, true, 512, JSON_THROW_ON_ERROR) : null;
    }

    /**
     * Invalidate all cache entries with a given tag.
     * Example: invalidateTag("tenant:42:products") purges all product caches for tenant 42.
     */
    public function invalidateTag(string $tag): int
    {
        $tagKey = "tag:{$tag}";
        $keys = $this->redis->sMembers($tagKey);
        $count = 0;
        if (!empty($keys)) {
            $count = $this->redis->del($keys);
        }
        $this->redis->del($tagKey);
        return $count;
    }
}
```

**Usage:**
```php
$cache = new TaggedCache($redis);
// Cache a product list, tagged by tenant and category
$cache->set("t:42:products:electronics", $products, 3600, [
    'tenant:42:products',
    'tenant:42:category:electronics',
]);
// When any product changes in tenant 42:
$cache->invalidateTag('tenant:42:products'); // Purges ALL product caches for this tenant
```

---

## Versioned Cache Keys

Instead of deleting cache entries, increment a version number. Old entries expire naturally.

```php
<?php
declare(strict_types=1);

final class VersionedCache
{
    public function __construct(private \Redis $redis) {}

    public function get(string $entity, int $tenantId, int $entityId): mixed
    {
        $version = (int) $this->redis->get("ver:{$entity}:t:{$tenantId}");
        $key = "{$entity}:t:{$tenantId}:{$entityId}:v{$version}";
        $data = $this->redis->get($key);
        return $data !== false ? json_decode($data, true, 512, JSON_THROW_ON_ERROR) : null;
    }

    public function set(string $entity, int $tenantId, int $entityId, mixed $value, int $ttl): void
    {
        $version = (int) $this->redis->get("ver:{$entity}:t:{$tenantId}");
        $key = "{$entity}:t:{$tenantId}:{$entityId}:v{$version}";
        $this->redis->setex($key, $ttl, json_encode($value, JSON_THROW_ON_ERROR));
    }

    /** Bump version — all old keys become orphaned and expire via TTL */
    public function invalidateAll(string $entity, int $tenantId): void
    {
        $this->redis->incr("ver:{$entity}:t:{$tenantId}");
    }
}
```

**Advantage:** No need to find and delete individual keys. Just bump version; old entries expire naturally.

---

## Stale-While-Revalidate

Serve stale data immediately while refreshing in the background. Best user experience.

```php
<?php
declare(strict_types=1);

final class StaleWhileRevalidate
{
    public function __construct(private \Redis $redis) {}

    /**
     * @param int $freshTtl  Seconds data is considered fresh
     * @param int $staleTtl  Seconds stale data can be served while refreshing
     */
    public function get(string $key, int $freshTtl, int $staleTtl, callable $loader): mixed
    {
        $data = $this->redis->hGetAll("swr:{$key}");
        if (!empty($data)) {
            $storedAt = (int) $data['stored_at'];
            $age = time() - $storedAt;

            if ($age < $freshTtl) {
                return json_decode($data['value'], true, 512, JSON_THROW_ON_ERROR); // Fresh
            }
            if ($age < $freshTtl + $staleTtl) {
                // Stale but serveable — trigger background refresh
                $this->triggerRefresh($key, $loader, $freshTtl, $staleTtl);
                return json_decode($data['value'], true, 512, JSON_THROW_ON_ERROR); // Serve stale
            }
        }
        // Cache miss or expired — synchronous load
        return $this->refresh($key, $loader, $freshTtl, $staleTtl);
    }

    private function refresh(string $key, callable $loader, int $freshTtl, int $staleTtl): mixed
    {
        $value = $loader();
        $this->redis->hMSet("swr:{$key}", [
            'value'     => json_encode($value, JSON_THROW_ON_ERROR),
            'stored_at' => time(),
        ]);
        $this->redis->expire("swr:{$key}", $freshTtl + $staleTtl + 60);
        return $value;
    }

    private function triggerRefresh(string $key, callable $loader, int $freshTtl, int $staleTtl): void
    {
        $lockKey = "swr:lock:{$key}";
        if ($this->redis->set($lockKey, '1', ['NX', 'EX' => 10])) {
            // Only one process refreshes — queue async or refresh inline
            $this->refresh($key, $loader, $freshTtl, $staleTtl);
            $this->redis->del($lockKey);
        }
    }
}
```

---

## Multi-Tier Cache Architecture

```
Request → [L1: APCu] → [L2: Redis] → [L3: MySQL] → Response
             ~0.01ms       ~0.5ms        ~5-50ms
```

| Layer | Tool | Scope | TTL | Best For |
|-------|------|-------|-----|----------|
| L1 | APCu | Per-server | 60-300s | Config, permissions, tenant settings |
| L2 | Redis | Shared | 300-3600s | User sessions, computed data, API responses |
| L3 | MySQL | Source of truth | N/A | Persistent data |

```php
<?php
declare(strict_types=1);

final class TieredCache
{
    public function __construct(private \Redis $redis) {}

    public function get(string $key, int $l1Ttl, int $l2Ttl, callable $loader): mixed
    {
        // L1: APCu (local, fastest)
        $data = apcu_fetch($key, $hit);
        if ($hit) { return $data; }

        // L2: Redis (shared)
        $cached = $this->redis->get($key);
        if ($cached !== false) {
            $data = json_decode($cached, true, 512, JSON_THROW_ON_ERROR);
            apcu_store($key, $data, $l1Ttl); // Promote to L1
            return $data;
        }

        // L3: Database (source of truth)
        $data = $loader();
        $this->redis->setex($key, $l2Ttl, json_encode($data, JSON_THROW_ON_ERROR));
        apcu_store($key, $data, $l1Ttl);
        return $data;
    }

    public function invalidate(string $key): void
    {
        apcu_delete($key);
        $this->redis->del($key);
    }
}
```

---

## Invalidation Decision Guide

```
Data changed — which invalidation?
├─ Single entity updated? → Delete key (cache-aside)
├─ Category/group updated? → Tag-based invalidation
├─ Schema or bulk change? → Version bump
├─ Non-critical, high-traffic? → Stale-while-revalidate
└─ Write-heavy counters? → Write-behind + periodic flush
```

---

## Anti-Patterns

- **No TTL** — cache entries live forever; stale data accumulates silently.
- **Cache everything** — low-value data wastes memory and evicts hot data.
- **Delete on write without stampede protection** — 1000 concurrent requests all miss and hit DB.
- **Inconsistent key naming** — use pattern: `{entity}:t:{tenant_id}:{id}` everywhere.
- **No monitoring** — track hit rate, miss rate, eviction rate. Alert when hit rate drops below 95%.

---

*Reference for php-modern-standards skill. Source: Garcia (2023) gap analysis.*
