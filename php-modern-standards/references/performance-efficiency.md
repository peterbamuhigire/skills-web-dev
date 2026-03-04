# PHP Performance & Efficiency Reference

Patterns for PHP 8.1+ covering generators, OPcache, built-in function optimization, memory, Fibers, profiling, and caching.

## Generators Deep Dive

Generators yield values one at a time, keeping memory constant regardless of dataset size.

### File Processing Generators

```php
<?php
declare(strict_types=1);

// CSV — one row in memory at a time, with associative keys
function readCsv(string $path, string $sep = ','): \Generator {
    $fh = fopen($path, 'r') ?: throw new \RuntimeException("Cannot open: $path");
    try {
        $header = fgetcsv($fh, 0, $sep);
        while (($row = fgetcsv($fh, 0, $sep)) !== false) {
            yield array_combine($header, $row);
        }
    } finally { fclose($fh); }
}

// Large text — line by line
function readLines(string $path): \Generator {
    $fh = fopen($path, 'r');
    while (($line = fgets($fh)) !== false) { yield rtrim($line, "\r\n"); }
    fclose($fh);
}
```

### Database Result Generators

```php
<?php
declare(strict_types=1);

// Fetch rows one at a time — constant memory for millions of rows
function fetchRows(\PDO $pdo, string $sql, array $params = []): \Generator {
    $stmt = $pdo->prepare($sql);
    $stmt->execute($params);
    while ($row = $stmt->fetch(\PDO::FETCH_ASSOC)) { yield $row; }
    $stmt->closeCursor();
}

// Chunked batch processing — avoids LIMIT/OFFSET performance cliff
function fetchInChunks(\PDO $pdo, string $table, int $chunk = 1000): \Generator {
    $lastId = 0;
    do {
        $stmt = $pdo->prepare("SELECT * FROM {$table} WHERE id > :id ORDER BY id LIMIT :lim");
        $stmt->bindValue(':id', $lastId, \PDO::PARAM_INT);
        $stmt->bindValue(':lim', $chunk, \PDO::PARAM_INT);
        $stmt->execute();
        $count = 0;
        while ($row = $stmt->fetch(\PDO::FETCH_ASSOC)) {
            $lastId = (int) $row['id'];
            yield $row;
            $count++;
        }
    } while ($count === $chunk);
}
```

### Bidirectional Generators and Delegation

```php
<?php
declare(strict_types=1);

// send() — pass values INTO a running generator
function accumulator(): \Generator {
    $total = 0;
    while (true) {
        $value = yield $total;    // Suspend, return total, receive value
        if ($value === null) { break; }
        $total += $value;
    }
    return $total;                // Generator return value via getReturn()
}
$gen = accumulator();
$gen->current();                  // Init — returns 0
$gen->send(10);                   // Returns 10
$gen->send(20);                   // Returns 30
$gen->send(null);                 // Terminates
$final = $gen->getReturn();       // 30

// yield from — delegate to sub-generators
function inner(): \Generator { yield 'a'; yield 'b'; return 'done'; }
function outer(): \Generator {
    $result = yield from inner();         // Delegates, captures return
    yield "inner returned: $result";
    yield from [1, 2, 3];                 // Works with arrays too
}
```

### Iterator vs Generator Decision Table

| Criteria | Iterator (class) | Generator (function) |
|---|---|---|
| Memory | Constant | Constant |
| Rewindable | Yes (implement rewind()) | No (single-pass) |
| State complexity | High (multiple methods) | Low (single function) |
| Bidirectional data | No | Yes (send/getReturn) |
| Composable | Via IteratorAggregate | Via yield from |
| Best for | Reusable collections | One-off streams, ETL |

**Rule:** Use generators by default. Use Iterator only when you need rewind or complex state machines.

---

## OPcache Configuration

### Development Settings

```ini
; php.ini — DEVELOPMENT
opcache.enable=1
opcache.enable_cli=1
opcache.memory_consumption=128
opcache.interned_strings_buffer=16
opcache.max_accelerated_files=10000
opcache.validate_timestamps=1          ; Check file changes every request
opcache.revalidate_freq=0              ; Always revalidate (dev only)
opcache.save_comments=1                ; Keep docblocks for reflection
opcache.jit=off                        ; Disable JIT for accurate Xdebug
opcache.jit_buffer_size=0
```

### Production Settings

```ini
; php.ini — PRODUCTION
opcache.enable=1
opcache.enable_cli=0
opcache.memory_consumption=256
opcache.interned_strings_buffer=32
opcache.max_accelerated_files=20000
opcache.validate_timestamps=0          ; NEVER check — deploy script clears cache
opcache.save_comments=0                ; Strip docblocks (saves memory)
opcache.jit=1255                       ; Tracing JIT (see below)
opcache.jit_buffer_size=128M
opcache.preload=/app/preload.php       ; Preload framework classes (PHP 7.4+)
opcache.preload_user=www-data
```

### JIT Modes (`opcache.jit = CRTO`)

| Digit | Meaning | Value | Notes |
|---|---|---|---|
| C (CPU) | AVX instructions | 1 | Always 1 |
| R (Register) | Global allocation | 2 | Always 2 |
| T (Trigger) | Compilation trigger | 5 | Tracing JIT (best for web) |
| O (Optimization) | Level | 5 | All optimizations |

`1255` = tracing JIT, full optimization. Use `1205` (function JIT) if tracing causes issues.

### Preloading (PHP 7.4+)

```php
<?php // preload.php — loaded once at server start, shared across all requests
declare(strict_types=1);
$files = [...glob(__DIR__ . '/src/Domain/**/*.php'), __DIR__ . '/src/Kernel.php'];
foreach ($files as $file) { if (is_file($file)) { opcache_compile_file($file); } }
```

### Monitoring OPcache

```php
<?php
declare(strict_types=1);
function getOpcacheReport(): array {
    $s = opcache_get_status(false);
    return [
        'memory_used_mb'  => round($s['memory_usage']['used_memory'] / 1048576, 2),
        'memory_free_mb'  => round($s['memory_usage']['free_memory'] / 1048576, 2),
        'hit_rate'        => round($s['opcache_statistics']['opcache_hit_rate'], 2) . '%',
        'cached_scripts'  => $s['opcache_statistics']['num_cached_scripts'],
        'cache_full'      => $s['cache_full'],
        'jit_enabled'     => $s['jit']['enabled'] ?? false,
    ];
}
```

**Cache invalidation:** Call `opcache_reset()` in deploy scripts or expose a protected HTTP endpoint.

---

## Built-in Function Performance

| Operation | Built-in | Userland | Speedup |
|---|---|---|---|
| Sort 10K elements | sort() 0.003ms | quicksort() 0.306ms | **100x** |
| String search | str_contains() | manual loop | **50x+** |
| Array filter | array_filter() | foreach + if | **10-30x** |
| JSON encode | json_encode() | manual serialization | **200x+** |

### String Functions (PHP 8.0+)

```php
<?php
declare(strict_types=1);
str_contains($haystack, 'needle');           // Replaces strpos() !== false
str_starts_with($url, 'https://');           // Replaces substr() === ...
str_ends_with($file, '.php');                // Replaces substr() === ...
// Prefer mb_ functions for user input
$len = mb_strlen($input, 'UTF-8');
$lower = mb_strtolower($input, 'UTF-8');
```

### Array Functions Quick Reference

```php
<?php
declare(strict_types=1);
// Transform
$names = array_map(fn(User $u): string => $u->name, $users);
// Filter
$active = array_filter($users, fn(User $u): bool => $u->isActive());
// Reduce
$total = array_reduce($items, fn(float $s, Item $i): float => $s + $i->price, 0.0);
// Search — ALWAYS pass strict=true
$found = in_array($needle, $haystack, true);
// Key check: array_key_exists (true if null), isset (false if null, faster)
// Column extraction
$emails = array_column($users, 'email');
$indexed = array_column($users, null, 'id');  // Re-index by id
// Merge — spread is faster in PHP 8.1+
$merged = [...$array1, ...$array2];
```

---

## Memory Optimization

### SPL Data Structures

```php
<?php
declare(strict_types=1);
// SplFixedArray — 40-60% less memory than array for known sizes
$fixed = new \SplFixedArray(10000);
for ($i = 0; $i < 10000; $i++) { $fixed[$i] = $i * 2; }

// SplQueue (FIFO), SplStack (LIFO)
$queue = new \SplQueue();
$queue->enqueue('task1'); $queue->enqueue('task2');
$first = $queue->dequeue();  // 'task1'

// SplMinHeap — priority queue (smallest first)
$heap = new class extends \SplMinHeap {
    protected function compare(mixed $a, mixed $b): int {
        return $b['priority'] <=> $a['priority'];
    }
};
$heap->insert(['task' => 'urgent', 'priority' => 1]);
$heap->insert(['task' => 'low', 'priority' => 10]);
$next = $heap->extract();  // urgent (priority 1)
```

### WeakMap (PHP 8.0+)

```php
<?php
declare(strict_types=1);
// Keys are objects, auto garbage-collected when no other references exist
$cache = new \WeakMap();
function computeExpensive(object $entity, \WeakMap $cache): string {
    if (isset($cache[$entity])) { return $cache[$entity]; }
    $result = expensiveOperation($entity);
    $cache[$entity] = $result;  // Auto-removed when $entity is destroyed
    return $result;
}
```

### Memory Profiling

```php
<?php
declare(strict_types=1);
function measureMemory(callable $fn): array {
    $before = memory_get_usage(true);
    $result = $fn();
    return [
        'result'    => $result,
        'used_mb'   => round((memory_get_usage(true) - $before) / 1048576, 3),
        'peak_mb'   => round(memory_get_peak_usage(true) / 1048576, 3),
    ];
}
// Free large variables immediately after use
$data = loadData(); processData($data); unset($data);
```

---

## Fibers (PHP 8.1+)

Cooperative multitasking: a function suspends itself and is resumed later. Lifecycle: `create -> start() -> [running] -> suspend() -> [suspended] -> resume() -> [running] -> return -> [terminated]`

### Concurrent I/O Example

```php
<?php
declare(strict_types=1);
function httpGet(string $url): \Fiber {
    return new \Fiber(function () use ($url): array {
        $ch = curl_init($url);
        curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 10]);
        \Fiber::suspend(['status' => 'waiting', 'url' => $url]);
        $response = curl_exec($ch);
        $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        return ['url' => $url, 'code' => $code, 'body' => $response];
    });
}

$fibers = [
    httpGet('https://api.example.com/users'),
    httpGet('https://api.example.com/orders'),
];
foreach ($fibers as $f) { $f->start(); }
$results = [];
foreach ($fibers as $f) {
    if ($f->isSuspended()) { $f->resume(); }
    if ($f->isTerminated()) { $results[] = $f->getReturn(); }
}
```

### Error Handling in Fibers

```php
<?php
declare(strict_types=1);
$fiber = new \Fiber(function (): void {
    try {
        $value = \Fiber::suspend('checkpoint');
    } catch (\Throwable $e) {
        error_log("Fiber error: " . $e->getMessage());
    }
});
$fiber->start();
if ($fiber->isSuspended()) {
    $fiber->throw(new \RuntimeException('Cancelled'));  // Inject error
}
```

### Fiber vs Generator Decision Matrix

| Use Case | Fiber | Generator |
|---|---|---|
| Iterate large datasets | No | **Yes** |
| Concurrent I/O (HTTP, DB) | **Yes** | No |
| Pause/resume execution | **Yes** | **Yes** |
| Bidirectional data | resume($val) | send($val) |
| Async frameworks (Revolt, ReactPHP) | **Yes** | No |
| Simple data pipelines | No | **Yes** |
| Multiple simultaneous tasks | **Yes** | No |

**When NOT to use Fibers:** CPU-bound computation (no parallelism), simple iteration (use generators), when Revolt/ReactPHP already manages the event loop.

---

## Profiling Tools

### Built-in Benchmark Function

```php
<?php
declare(strict_types=1);
function benchmark(callable $fn, int $iterations = 1000): array {
    $times = [];
    for ($i = 0; $i < $iterations; $i++) {
        $start = hrtime(true);
        $fn();
        $times[] = hrtime(true) - $start;
    }
    sort($times);
    return [
        'iterations' => $iterations,
        'avg_ms'     => round(array_sum($times) / count($times) / 1e6, 4),
        'min_ms'     => round($times[0] / 1e6, 4),
        'p95_ms'     => round($times[(int)(count($times) * 0.95)] / 1e6, 4),
        'p99_ms'     => round($times[(int)(count($times) * 0.99)] / 1e6, 4),
    ];
}
```

### Xdebug Profiling

```ini
; php.ini — profiling (NEVER enable in production)
xdebug.mode=profile
xdebug.output_dir=/tmp/xdebug
xdebug.profiler_output_name=cachegrind.out.%t.%p
xdebug.start_with_request=trigger     ; Use XDEBUG_TRIGGER cookie/param
```

Analyze with **KCacheGrind** (Linux), **QCacheGrind** (Windows/macOS), or **Webgrind** (browser). For production profiling, use **Blackfire.io** (`blackfire run php script.php` or `blackfire curl URL`).

---

## Caching Strategies

### APCu (Userland In-Memory Cache)

```php
<?php
declare(strict_types=1);
// Single-server, fastest option for config/small lookups
function cachedQuery(string $key, callable $loader, int $ttl = 3600): mixed {
    $cached = apcu_fetch($key, $success);
    if ($success) { return $cached; }
    $data = $loader();
    apcu_store($key, $data, $ttl);
    return $data;
}
// Pattern-based invalidation
$iter = new \APCUIterator('/^tenant_42_/');
apcu_delete($iter);
```

### Redis (Distributed Cache with Stampede Prevention)

```php
<?php
declare(strict_types=1);
final class RedisCache {
    public function __construct(private \Redis $redis) {}

    public function remember(string $key, int $ttl, callable $loader): mixed {
        $cached = $this->redis->get($key);
        if ($cached !== false) {
            return json_decode($cached, true, 512, JSON_THROW_ON_ERROR);
        }
        $data = $loader();
        $this->redis->setex($key, $ttl, json_encode($data, JSON_THROW_ON_ERROR));
        return $data;
    }

    // Atomic lock prevents cache stampede (thundering herd)
    public function rememberWithLock(string $key, int $ttl, callable $loader): mixed {
        $cached = $this->redis->get($key);
        if ($cached !== false) {
            return json_decode($cached, true, 512, JSON_THROW_ON_ERROR);
        }
        $lockKey = "lock:{$key}";
        if ($this->redis->set($lockKey, '1', ['NX', 'EX' => 10])) {
            try {
                $data = $loader();
                $this->redis->setex($key, $ttl, json_encode($data, JSON_THROW_ON_ERROR));
                return $data;
            } finally { $this->redis->del($lockKey); }
        }
        usleep(50000);
        return $this->remember($key, $ttl, $loader);
    }

    public function invalidateByPrefix(string $prefix): int {
        $keys = $this->redis->keys("{$prefix}*");
        return $keys ? $this->redis->del($keys) : 0;
    }
}
```

### HTTP Caching Headers from PHP

```php
<?php
declare(strict_types=1);
function setCacheHeaders(string $content, int $maxAge = 3600, bool $private = false): void {
    $dir = $private ? 'private' : 'public';
    header("Cache-Control: {$dir}, max-age={$maxAge}");
    header('ETag: "' . md5($content) . '"');
}
function handleConditional(string $etag, int $lastMod): bool {
    if (($_SERVER['HTTP_IF_NONE_MATCH'] ?? '') === $etag) { http_response_code(304); return true; }
    $since = strtotime($_SERVER['HTTP_IF_MODIFIED_SINCE'] ?? '');
    if ($since && $since >= $lastMod) { http_response_code(304); return true; }
    return false;
}
```

### Cache Strategy Selection

| Layer | Tool | Scope | Latency | Best For |
|---|---|---|---|---|
| Bytecode | OPcache | Per-server | 0 | Always on |
| In-memory | APCu | Per-server | ~0.01ms | Config, small lookups |
| Distributed | Redis | Multi-server | ~0.5ms | Sessions, shared state |
| HTTP | Cache-Control | Client/CDN | 0 | Static assets, API responses |

---

**Sources:** Generating Efficient PHP (php[architect] 2023), PHP: The Right Way
