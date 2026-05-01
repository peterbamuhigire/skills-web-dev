# Authentication, Security Headers, and Rate Limiting

Back to [../SKILL.md](../SKILL.md).

Authentication method selection, headers every response must carry, CORS, and rate-limiting mechanics. The auth model produced by this skill is consumed by `vibe-security-skill` for threat modelling.

## Security headers (mandatory on every response)

```php
<?php
header('Content-Type: application/json');
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: DENY');
header('Strict-Transport-Security: max-age=31536000; includeSubDomains');
header('Cache-Control: no-store');          // default; override per endpoint
header('Referrer-Policy: no-referrer');
```

## CORS

Never use `*` with credentials.

```php
<?php
$allowedOrigins = ['https://app.example.com', 'https://admin.example.com'];
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
if (in_array($origin, $allowedOrigins, true)) {
    header("Access-Control-Allow-Origin: {$origin}");
    header('Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS');
    header('Access-Control-Allow-Headers: Authorization, Content-Type, X-Request-ID');
    header('Access-Control-Allow-Credentials: true');
}
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}
```

## Auth-method selection

| Caller shape                        | Method                        | Why                                                        |
|-------------------------------------|-------------------------------|------------------------------------------------------------|
| Server-to-server, trusted partner   | API Key (hashed)              | Long-lived, no user context, simple to rotate              |
| Web app with user consent           | OAuth2 Authorization Code     | User-facing consent, scoped tokens, refresh supported      |
| Server-to-server via OAuth          | OAuth2 Client Credentials     | Standardised scopes, short-lived tokens                    |
| First-party mobile / SPA            | JWT (access + refresh)        | Stateless verification, refresh rotates compromised tokens |
| Legacy / tightly-controlled clients | OAuth2 Resource Owner Password| Only when no other flow works — avoid when possible        |

Failure mode if wrong: long-lived JWTs for server-to-server make revocation impossible; API keys for mobile clients expose the key in the binary; implicit flow for SPAs leaks tokens in the browser URL history.

## API key (server-to-server)

```php
<?php
// Header: X-API-Key: sk_live_abc123
function authenticateApiKey(string $key): ?array {
    global $db;
    $stmt = $db->prepare('
        SELECT ak.*, f.id AS franchise_id
        FROM api_keys ak
        JOIN tbl_franchises f ON ak.franchise_id = f.id
        WHERE ak.key_hash = ? AND ak.is_active = 1
          AND (ak.expires_at IS NULL OR ak.expires_at > NOW())
    ');
    $stmt->execute([hash('sha256', $key)]);  // NEVER store raw key
    return $stmt->fetch() ?: null;
}
```

```sql
CREATE TABLE api_keys (
    id           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    franchise_id BIGINT UNSIGNED NOT NULL,
    name         VARCHAR(100) NOT NULL,
    key_hash     VARCHAR(64) NOT NULL UNIQUE,   -- SHA-256 of raw key
    scopes       JSON,                           -- ["invoices:read","payments:write"]
    last_used_at DATETIME,
    expires_at   DATETIME,
    is_active    TINYINT(1) DEFAULT 1,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## JWT (user sessions / mobile)

```php
<?php
// Authorization: Bearer <jwt>
function authenticateJwt(string $token): ?array {
    try {
        $payload = JWT::decode($token, new Key(JWT_SECRET, 'HS256'));
        if ($payload->exp < time()) return null;
        if ($payload->iss !== 'api.example.com') return null;  // Validate issuer
        return (array) $payload;
    } catch (\Exception $e) {
        return null;
    }
}
```

JWT rules: short-lived access tokens (15–60 min) plus long-lived refresh tokens. Never store secrets in payload. Always validate `iss`, `aud`, `exp`.

## OAuth2 grant flows

| Flow                     | Use case                                            |
|--------------------------|-----------------------------------------------------|
| Authorization Code       | Web apps requiring user consent                     |
| Client Credentials       | Server-to-server (no user involved)                 |
| Resource Owner Password  | Only when no other option; avoid                    |
| Implicit                 | Deprecated — do not use                             |

## Rate limiting

```php
<?php
function checkRateLimit(int $franchiseId, int $userId): void {
    global $redis;
    $key = "rl:{$franchiseId}:{$userId}:" . date('YmdHi');
    $count = $redis->incr($key);
    if ($count === 1) $redis->expire($key, 60);

    header('X-RateLimit-Limit: 100');
    header('X-RateLimit-Remaining: ' . max(0, 100 - $count));

    if ($count > 100) {
        header('Retry-After: ' . (60 - (time() % 60)));
        http_response_code(429);
        echo json_encode(['success' => false, 'error' => ['code' => 'RATE_LIMITED']]);
        exit;
    }
}
```

Algorithm selection:

| Traffic shape                                   | Algorithm         | Why                                 |
|-------------------------------------------------|-------------------|-------------------------------------|
| Bursty (webhooks, CLI batch jobs)               | Token Bucket      | Allows short bursts up to capacity  |
| Steady flow (public API, billing-critical)      | Leaky Bucket      | Strict smoothed rate                |
| Mixed, needs accurate billing caps              | Sliding Window    | Smooth + accurate over rolling span |

Use Redis for distributed rate state so horizontal replicas share the counter.

## Idempotency keys

Required on every POST that triggers a side effect — payments, refunds, emails, inventory movements.

| Endpoint class                           | Require `Idempotency-Key`? | TTL      | Scope                            |
|------------------------------------------|----------------------------|----------|----------------------------------|
| Payment, refund, charge                  | yes                        | 24 hours | per tenant + user                |
| Order/invoice creation                   | yes                        | 24 hours | per tenant + user                |
| External webhook dispatch                | yes                        | 7 days   | per destination                  |
| Inventory adjustment                     | yes                        | 24 hours | per tenant + warehouse           |
| Read-only (`GET`, `HEAD`)                | no                         | n/a      | n/a                              |
| Partial updates without external effect  | optional                   | 1 hour   | per tenant + resource            |

Failure mode if skipped: double payments, duplicated email sends, phantom inventory movement on network retries.
