# RESTful API Patterns

> Source: Sommerfeld — Unlock PHP 8 (Ch. 9); industry best practices

## Table of Contents

1. [REST Architecture](#rest-architecture)
2. [cURL Client](#curl-client)
3. [Creating PHP APIs](#creating-php-apis)
4. [JWT Authentication](#jwt-authentication)
5. [Rate Limiting](#rate-limiting)
6. [API Versioning](#api-versioning)
7. [Testing APIs](#testing-apis)

---

## REST Architecture

Five constraints make an API RESTful:

| Constraint | Meaning |
|-----------|---------|
| **Stateless** | Each request contains all context; no server-stored session state |
| **Client-Server** | Client and server evolve independently |
| **Cacheable** | Responses declare cache policy (`Cache-Control: max-age=3600`) |
| **Layered** | Client doesn't know if hitting CDN, load balancer, or origin |
| **Uniform Interface** | Consistent URLs + HTTP methods; nouns only, no verbs |

### HTTP Methods

```
GET    /tasks          — list all (idempotent, safe)
GET    /tasks/123      — get one
POST   /tasks          — create new (non-idempotent)
PUT    /tasks/123      — replace entirely (idempotent)
PATCH  /tasks/123      — partial update (idempotent)
DELETE /tasks/123      — delete (idempotent)
```

**Never:** `GET /getAllTasks` or `POST /createTask` — verbs belong to HTTP methods, not URLs.

### Data Retrieval Conventions

```
GET /tasks?status=completed         — filter
GET /tasks?orderBy=createdAt&order=desc  — sort
GET /tasks?page=2&limit=10          — paginate (returns rows 11–20)
```

### HTTP Status Codes

| Code | When to Use |
|------|------------|
| 200 | OK — GET/PUT/PATCH success |
| 201 | Created — POST success |
| 204 | No Content — DELETE success |
| 400 | Bad Request — invalid input |
| 401 | Unauthorized — auth required |
| 403 | Forbidden — auth OK but no permission |
| 404 | Not Found |
| 422 | Unprocessable Entity — validation failed |
| 429 | Too Many Requests — rate limited |
| 500 | Internal Server Error |

---

## cURL Client

```php
<?php

class ApiClient
{
    public function get(string $url, array $headers = []): mixed
    {
        return $this->request($url, 'GET', null, $headers);
    }

    public function post(string $url, array $data, array $headers = []): mixed
    {
        return $this->request($url, 'POST', $data, $headers);
    }

    public function patch(string $url, array $data, array $headers = []): mixed
    {
        return $this->request($url, 'PATCH', $data, $headers);
    }

    private function request(string $url, string $method, ?array $data, array $headers): mixed
    {
        $ch = curl_init();

        curl_setopt_array($ch, [
            CURLOPT_URL            => $url,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_CUSTOMREQUEST  => $method,
            CURLOPT_SSL_VERIFYPEER => true,    // Always true in production
            CURLOPT_HTTPHEADER     => array_merge(
                ['Content-Type: application/json', 'Accept: application/json'],
                $headers
            ),
        ]);

        if ($data !== null) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        }

        $response = curl_exec($ch);
        $statusCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($response === false) {
            throw new \RuntimeException('cURL request failed');
        }

        return json_decode($response, true);
    }
}

// Usage with JWT:
$client = new ApiClient();
$tasks = $client->get(
    url: 'https://api.example.com/v1/tasks',
    headers: ['Authorization: Bearer ' . $jwtToken]
);
```

**Security rule:** `CURLOPT_SSL_VERIFYPEER => false` only in local dev. Never in staging or production.

---

## Creating PHP APIs

### Attribute-Based Routing (PHP 8.0+)

```php
<?php

// 1. Define Route attribute
#[\Attribute(\Attribute::TARGET_METHOD)]
final readonly class Route
{
    public function __construct(
        public string $path,
        public string $method = 'GET',
        public array $middlewares = [],
    ) {}
}

// 2. Use in controllers
final class TaskController
{
    #[Route('/api/v1/tasks', 'GET')]
    public function index(): string
    {
        return $this->responseJson($this->taskModel->all());
    }

    #[Route('/api/v1/tasks', 'POST', [AuthMiddleware::class])]
    public function store(): string
    {
        // POST with middleware applied
    }
}

// 3. Discover routes via Reflection
function getRoutesFromAttributes(array $controllers): array
{
    $routes = [];
    foreach ($controllers as $controller) {
        $reflection = new \ReflectionClass($controller);
        foreach ($reflection->getMethods() as $method) {
            $attr = $method->getAttributes(Route::class)[0] ?? null;
            if ($attr) {
                $route = $attr->newInstance();
                $routes[$route->method][$route->path] = [
                    $controller, $method->getName(), $route->middlewares
                ];
            }
        }
    }
    return $routes;
}
```

### JSON Response Helper

```php
<?php

final class Response
{
    public function __construct(
        private mixed $content = '',
        private int $statusCode = 200,
        private array $headers = [],
    ) {}

    public function withJson(array $data, int $statusCode = null): static
    {
        $this->content = json_encode($data, JSON_THROW_ON_ERROR);
        $this->headers['Content-Type'] = 'application/json';
        if ($statusCode !== null) {
            $this->statusCode = $statusCode;
        }
        return $this;
    }

    public function send(): string
    {
        http_response_code($this->statusCode);
        foreach ($this->headers as $key => $value) {
            header("{$key}: {$value}");
        }
        return $this->content;
    }
}

// In base controller:
protected function responseJson(array $data, int $statusCode = 200): string
{
    return (new Response())->withJson($data, $statusCode)->send();
}
```

### Route-level Auth Middleware

```php
<?php

final class AuthMiddleware
{
    public function handle(): void
    {
        $header = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
        if (!str_starts_with($header, 'Bearer ')) {
            http_response_code(401);
            echo json_encode(['error' => 'Unauthorized']);
            exit;
        }
        // Validate JWT...
    }
}
```

### Distinguish API Routes from Web Routes

```php
// Separate global session middleware from API routes
public function run(): mixed
{
    $router = Router::instance();
    // Skip web middleware for /api/* routes
    if (!str_starts_with($router->getCurrentPath(), '/api/')) {
        $this->applyWebMiddlewares();
    }
    return $router->run();
}
```

---

## JWT Authentication

```php
<?php

final class JWT
{
    public function __construct(
        private string $secretKey,  // Load from .env — never hardcode
    ) {}

    public function generate(array $payload): string
    {
        $header = $this->base64url(json_encode(['alg' => 'HS256', 'typ' => 'JWT']));
        $body   = $this->base64url(json_encode($payload));
        $sig    = $this->base64url(hash_hmac('sha256', "$header.$body", $this->secretKey, binary: true));
        return "$header.$body.$sig";
    }

    public function validate(string $token): ?array
    {
        $parts = explode('.', $token);
        if (count($parts) !== 3) {
            return null;
        }
        [$header, $payload, $signature] = $parts;

        $expected = $this->base64url(
            hash_hmac('sha256', "$header.$payload", $this->secretKey, binary: true)
        );

        if (!hash_equals($expected, $signature)) {  // Timing-safe comparison
            return null;
        }

        $data = json_decode(base64_decode($payload), true);

        // Check expiry
        if (isset($data['exp']) && $data['exp'] < time()) {
            return null;
        }

        return $data;
    }

    private function base64url(string $data): string
    {
        return str_replace(['+', '/', '='], ['-', '_', ''], base64_encode($data));
    }
}

// Usage:
$jwt = new JWT(secretKey: $_ENV['JWT_SECRET']);
$token = $jwt->generate(['user_id' => 42, 'exp' => time() + 3600]);
$payload = $jwt->validate($token);  // null if invalid/expired
```

**Production rules:**
- Store `JWT_SECRET` in `.env`, minimum 32 random bytes
- Always include `exp` (expiry) in payload
- Store secret keys separately per service
- Use `hash_equals()` for signature comparison — prevents timing attacks

---

## Rate Limiting

```php
<?php

final class RateLimiter
{
    private const RATE_LIMIT = 1000;  // per hour
    private const WINDOW = 3600;

    public function __construct(private \Memcached $cache) {}

    public function check(string $identifier): bool
    {
        $key = 'rate:' . md5($identifier);
        $count = (int) ($this->cache->get($key) ?? 0);

        if ($count >= self::RATE_LIMIT) {
            return false;
        }

        if ($count === 0) {
            $this->cache->set($key, 1, self::WINDOW);
        } else {
            $this->cache->increment($key, 1);
        }

        return true;
    }

    public function middleware(string $ip): void
    {
        if (!$this->check($ip)) {
            http_response_code(429);
            header('Retry-After: 3600');
            echo json_encode(['error' => 'Too many requests']);
            exit;
        }
    }
}
```

---

## API Versioning

Three approaches:

```php
// 1. URI (recommended — most visible)
GET /api/v1/tasks
GET /api/v2/tasks

// 2. Accept header
Accept: application/vnd.myapp.v2+json

// 3. Query parameter (least preferred)
GET /api/tasks?version=2
```

**Best practice:** Use URI versioning (`/api/v1/`). Include version in every route from day one. Never break existing versions — deprecate with sunset headers.

---

## Testing APIs

```php
<?php

// PHPUnit — unit test business logic
final class TaskTest extends TestCase
{
    public function testCreateTask(): void
    {
        $response = $this->http->post('/api/v1/tasks', ['title' => 'Learn PHP']);
        $this->assertEquals(201, $response->getStatusCode());
        $body = json_decode($response->getBody(), true);
        $this->assertArrayHasKey('id', $body);
    }
}
```

**Tool recommendations:**

| Tool | Best For |
|------|----------|
| PHPUnit | Business logic unit tests |
| Postman | Manual + automated endpoint testing |
| Behat | End-to-end behavior testing (BDD) |
| Swagger/OpenAPI | Interactive documentation |
| phpDocumentor | Auto-docs from source code comments |

---

**Sources:** Sommerfeld, Unlock PHP 8 Ch. 9 (2024)
