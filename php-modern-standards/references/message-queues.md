# Message Queues & Async Processing for PHP

Patterns for offloading work from the HTTP request cycle using queues. Keeps API responses fast, improves reliability, enables retry logic.

**Source:** Garcia (2023) Ch10 identified this gap; implementations based on production patterns.

---

## When to Use Queues

**Move to a queue if the task:**
- Takes >500ms (email, PDF generation, report building)
- Calls external APIs (payment webhooks, SMS, shipping)
- Can tolerate seconds of delay (notifications, analytics, audit logs)
- Needs retry on failure (payment processing, file uploads to S3)

**Keep synchronous if:**
- User needs the result immediately (login, data retrieval)
- Operation is <100ms and critical to the response

---

## Architecture Overview

```
[PHP App] --publish--> [Queue Broker] --consume--> [Worker Process]
                          (Redis/RabbitMQ)           (PHP CLI)
                              |
                        [Dead Letter Queue] <-- failed after max retries
```

---

## Option 1: Redis Queues (Simple, No Extra Infrastructure)

Best when you already have Redis. Use Redis Lists as FIFO queues with `RPUSH`/`BLPOP`.

### Producer (Enqueue Jobs)

```php
<?php
declare(strict_types=1);

final class RedisQueue
{
    public function __construct(
        private \Redis $redis,
        private string $queueName = 'jobs:default',
    ) {}

    public function dispatch(string $jobClass, array $payload, int $delay = 0): string
    {
        $jobId = bin2hex(random_bytes(16));
        $job = json_encode([
            'id'         => $jobId,
            'class'      => $jobClass,
            'payload'    => $payload,
            'attempts'   => 0,
            'max_retries'=> 3,
            'created_at' => time(),
        ], JSON_THROW_ON_ERROR);

        if ($delay > 0) {
            // Delayed job — sorted set scored by execute-at timestamp
            $this->redis->zAdd("{$this->queueName}:delayed", time() + $delay, $job);
        } else {
            $this->redis->rPush($this->queueName, $job);
        }
        return $jobId;
    }

    /** Move due delayed jobs to the main queue (call periodically) */
    public function migrateDelayed(): int
    {
        $now = time();
        $jobs = $this->redis->zRangeByScore("{$this->queueName}:delayed", '-inf', (string) $now);
        $count = 0;
        foreach ($jobs as $job) {
            if ($this->redis->zRem("{$this->queueName}:delayed", $job)) {
                $this->redis->rPush($this->queueName, $job);
                $count++;
            }
        }
        return $count;
    }
}
```

### Consumer (Worker Process)

```php
<?php
declare(strict_types=1);

final class QueueWorker
{
    public function __construct(
        private \Redis $redis,
        private string $queueName = 'jobs:default',
    ) {}

    /** Run forever — execute as: php worker.php */
    public function listen(): void
    {
        while (true) {
            // BLPOP blocks until a job is available (timeout 30s)
            $result = $this->redis->blPop([$this->queueName], 30);
            if ($result === false) {
                continue; // Timeout — loop and check for shutdown signals
            }
            $job = json_decode($result[1], true, 512, JSON_THROW_ON_ERROR);
            $this->process($job);
        }
    }

    private function process(array $job): void
    {
        $job['attempts']++;
        try {
            $handler = new $job['class']();
            $handler->handle($job['payload']);
        } catch (\Throwable $e) {
            error_log("[Queue] Job {$job['id']} failed: {$e->getMessage()}");
            if ($job['attempts'] < $job['max_retries']) {
                // Retry with exponential backoff
                $delay = (int)(2 ** $job['attempts']);
                $job['last_error'] = $e->getMessage();
                $this->redis->zAdd(
                    "{$this->queueName}:delayed",
                    time() + $delay,
                    json_encode($job, JSON_THROW_ON_ERROR),
                );
            } else {
                // Max retries exceeded — dead letter queue
                $this->redis->rPush(
                    "{$this->queueName}:dead",
                    json_encode($job, JSON_THROW_ON_ERROR),
                );
                error_log("[Queue] Job {$job['id']} moved to DLQ after {$job['attempts']} attempts");
            }
        }
    }
}
```

### Job Handler Interface

```php
<?php
declare(strict_types=1);

interface QueueJob
{
    public function handle(array $payload): void;
}

final class SendInvoiceEmail implements QueueJob
{
    public function handle(array $payload): void
    {
        $orderId = $payload['order_id'];
        $tenantId = $payload['tenant_id'];
        // ... send email
    }
}
```

### Usage

```php
$queue = new RedisQueue($redis);
// Dispatch immediately
$queue->dispatch(SendInvoiceEmail::class, ['order_id' => 42, 'tenant_id' => 1]);
// Dispatch with 60-second delay
$queue->dispatch(GenerateReport::class, ['report_id' => 7], delay: 60);
```

---

## Option 2: RabbitMQ (Enterprise, Multi-Consumer)

Best for: multi-service architectures, message routing, guaranteed delivery, fanout.

### Producer

```php
<?php
declare(strict_types=1);

use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Message\AMQPMessage;

final class RabbitProducer
{
    private AMQPStreamConnection $connection;

    public function __construct(string $host, int $port, string $user, string $pass)
    {
        $this->connection = new AMQPStreamConnection($host, $port, $user, $pass);
    }

    public function publish(string $queue, array $payload): void
    {
        $channel = $this->connection->channel();
        $channel->queue_declare($queue, false, true, false, false, false, [
            'x-dead-letter-exchange'    => ['S', ''],
            'x-dead-letter-routing-key' => ['S', "{$queue}.dlq"],
        ]);
        // Declare DLQ
        $channel->queue_declare("{$queue}.dlq", false, true, false, false);

        $msg = new AMQPMessage(json_encode($payload, JSON_THROW_ON_ERROR), [
            'delivery_mode' => AMQPMessage::DELIVERY_MODE_PERSISTENT,
            'content_type'  => 'application/json',
            'message_id'    => bin2hex(random_bytes(16)),
            'timestamp'     => time(),
        ]);
        $channel->basic_publish($msg, '', $queue);
        $channel->close();
    }

    public function __destruct()
    {
        $this->connection->close();
    }
}
```

### Consumer

```php
<?php
declare(strict_types=1);

use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Message\AMQPMessage;

final class RabbitConsumer
{
    public function consume(string $queue, callable $handler, int $prefetch = 10): void
    {
        $connection = new AMQPStreamConnection('localhost', 5672, 'guest', 'guest');
        $channel = $connection->channel();
        $channel->queue_declare($queue, false, true, false, false);
        $channel->basic_qos(0, $prefetch, false);

        $channel->basic_consume($queue, '', false, false, false, false,
            function (AMQPMessage $msg) use ($handler): void {
                try {
                    $payload = json_decode($msg->getBody(), true, 512, JSON_THROW_ON_ERROR);
                    $handler($payload);
                    $msg->ack();
                } catch (\Throwable $e) {
                    error_log("[RabbitMQ] Failed: {$e->getMessage()}");
                    // Reject and requeue (or nack to DLQ if retries exhausted)
                    $msg->nack(requeue: false); // Goes to DLQ
                }
            }
        );

        while ($channel->is_consuming()) {
            $channel->wait();
        }
    }
}
```

---

## Retry Strategy: Exponential Backoff

```
Attempt 1: immediate
Attempt 2: 2 seconds
Attempt 3: 4 seconds
Attempt 4: 8 seconds (max retry → DLQ)
```

Formula: `delay = min(base * 2^attempt, maxDelay)` where base=1s, maxDelay=60s.

**Jitter:** Add random jitter to prevent thundering herd on retries:
```php
$delay = min(60, (int)(2 ** $attempt)) + random_int(0, 1000) / 1000;
```

---

## Dead Letter Queue (DLQ) Management

Jobs that exhaust retries land in the DLQ. Monitor and process them:

```php
// List dead jobs
$deadJobs = $redis->lRange('jobs:default:dead', 0, -1);

// Replay a dead job (move back to main queue)
$job = $redis->lPop('jobs:default:dead');
if ($job) {
    $data = json_decode($job, true);
    $data['attempts'] = 0; // Reset attempts
    $redis->rPush('jobs:default', json_encode($data));
}
```

---

## Decision Guide

```
Choose a queue backend:
├─ Already have Redis? No multi-service routing needed?
│  → Redis Queues (simple, fast, zero new infrastructure)
├─ Need message routing, fanout, or multi-consumer groups?
│  → RabbitMQ (exchanges, bindings, guaranteed delivery)
└─ AWS environment? Want managed service?
   → SQS (zero ops, auto-scaling, built-in DLQ)
```

---

## Process Supervision

Workers must be supervised to restart on crash. Use systemd on Linux:

```ini
# /etc/systemd/system/queue-worker.service
[Unit]
Description=PHP Queue Worker
After=redis.service

[Service]
User=www-data
ExecStart=/usr/bin/php /var/www/app/worker.php
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Run multiple workers: `systemctl start queue-worker@{1..4}` (4 parallel workers).

---

## Anti-Patterns

- **No DLQ** — failed jobs vanish silently. Always configure a dead letter destination.
- **No idempotency** — jobs may be delivered twice. Design handlers to be safe on replay.
- **Unbounded retries** — infinite retry loops consume resources. Cap at 3-5 attempts.
- **Blocking the queue** — one slow job blocks all others. Use per-job timeouts.
- **No monitoring** — track queue depth, processing rate, DLQ size. Alert when DLQ grows.

---

*Reference for php-modern-standards skill. Source: Garcia (2023) gap analysis.*
