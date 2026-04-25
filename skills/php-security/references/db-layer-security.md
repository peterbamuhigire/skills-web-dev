# PHP Database Layer Security

Patterns for the PHP-to-database trust boundary: PDO configuration, prepared statements, least-privilege credentials, and safe handling of tenant context in pooled environments.

## 1. The App-DB Trust Boundary

There is exactly one rule at this boundary: **queries are code; user input is data; never mix the two**. Every SQL injection bug in history started by crossing that line — string-concatenating a variable into an SQL statement, or passing a user-controlled field name directly into `ORDER BY`.

The database has no way to tell that `1 OR 1=1` came from a form field. That judgement has to be made on the PHP side, once, in the data access layer, and enforced everywhere.

## 2. PDO Configuration for Security

Every database connection in the app uses the same hardened PDO factory. Never construct `new PDO(...)` inline with default attributes.

```php
<?php
declare(strict_types=1);

final class Db
{
    public static function connect(): PDO
    {
        $config = require __DIR__ . '/../config/db.php';

        $dsn = sprintf(
            'mysql:host=%s;port=%d;dbname=%s;charset=utf8mb4',
            $config['host'],
            $config['port'],
            $config['name']
        );

        return new PDO(
            $dsn,
            $config['user'],
            $config['pass'],
            [
                PDO::ATTR_ERRMODE              => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE   => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES     => false,
                PDO::ATTR_STRINGIFY_FETCHES    => false,
                PDO::ATTR_PERSISTENT           => false,
                PDO::MYSQL_ATTR_SSL_CA         => '/etc/ssl/certs/ca-bundle.crt',
                PDO::MYSQL_ATTR_SSL_VERIFY_SERVER_CERT => true,
                PDO::MYSQL_ATTR_INIT_COMMAND   =>
                    "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci, "
                  . "SESSION sql_mode = 'STRICT_ALL_TABLES,NO_ENGINE_SUBSTITUTION', "
                  . "SESSION MAX_EXECUTION_TIME = 5000",
            ]
        );
    }
}
```

Why these matter:

- `ERRMODE_EXCEPTION` — failures throw `PDOException` instead of silently returning `false`.
- `EMULATE_PREPARES = false` — forces the driver to send real prepared statements to the server. Emulated prepares do client-side escaping, which has had CVEs.
- `MYSQL_ATTR_SSL_VERIFY_SERVER_CERT = true` — refuses to connect to a server that cannot prove its identity. Combined with TLS on the server (see `mysql-best-practices/references/database-security-hardening.md`), this closes the last mile.
- `MAX_EXECUTION_TIME = 5000` — a slow or pathological query cannot hang the connection forever.

## 3. Prepared Statements — The Only Answer to SQL Injection

Prepared statements separate the statement from the data at the protocol level. The server never sees an executable version of user input.

Positional placeholders:

```php
$stmt = $db->prepare(
    'SELECT id, full_name, email
       FROM users
      WHERE tenant_id = ? AND status = ?
      LIMIT 50'
);
$stmt->execute([$tenantId, 'active']);
$rows = $stmt->fetchAll();
```

Named placeholders (clearer for larger statements):

```php
$stmt = $db->prepare(
    'INSERT INTO invoice (tenant_id, customer_id, total, created_at)
     VALUES (:tenant, :customer, :total, NOW())'
);
$stmt->execute([
    ':tenant'   => $tenantId,
    ':customer' => $customerId,
    ':total'    => $total,
]);
```

Type-bind when the driver needs a hint, for example to keep an `IS NULL` check:

```php
$stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
```

What prepared statements cannot parameterise:

- Table names
- Column names
- `ORDER BY` direction and column
- `LIMIT` in some old drivers

For these, use a whitelist:

```php
$allowedSort = ['created_at', 'total', 'status'];
$sort = in_array($_GET['sort'] ?? '', $allowedSort, true) ? $_GET['sort'] : 'created_at';
$dir  = ($_GET['dir'] ?? '') === 'asc' ? 'ASC' : 'DESC';

$sql = "SELECT id, total FROM invoice ORDER BY {$sort} {$dir} LIMIT 50";
```

Full SQL injection playbook: `php-security/references/injection-attack-patterns.md`.

## 4. Connection String Security

Database credentials never appear in source code, never appear in a file committed to git, and never appear in a web-accessible directory.

Directory layout:

```
/var/www/billing-app/
  public/          <- document root (only)
  config/
    db.php
  .env
  src/
```

`.env`:

```bash
DB_HOST=127.0.0.1
DB_NAME=billing
DB_USER=billing_app
DB_PASS=...
```

Permissions:

```bash
sudo chown root:www-data /var/www/billing-app/.env
sudo chmod 640 /var/www/billing-app/.env
```

`config/db.php` reads from env and falls back to a hard failure, never a default:

```php
return [
    'host' => getenv('DB_HOST') ?: throw new RuntimeException('DB_HOST missing'),
    'name' => getenv('DB_NAME') ?: throw new RuntimeException('DB_NAME missing'),
    'user' => getenv('DB_USER') ?: throw new RuntimeException('DB_USER missing'),
    'pass' => getenv('DB_PASS') ?: throw new RuntimeException('DB_PASS missing'),
    'port' => (int)(getenv('DB_PORT') ?: 3306),
];
```

For production, fetch secrets from Vault at boot and inject via environment. See `cicd-devsecops`.

## 5. Least-Privilege Database Users

One MySQL/Postgres user per bounded context. The runtime never uses a user that has DDL rights.

| Credential | Scope | Granted |
|---|---|---|
| `billing_app` | Runtime writes | SELECT, INSERT, UPDATE, DELETE |
| `billing_ro` | Reporting panel | SELECT only |
| `billing_migrate` | CI/CD deploy step | ALL on `billing_db.*` |
| `backup` | Nightly `mysqldump` | RELOAD, LOCK TABLES, SELECT |

The migration user is loaded only during the release step and is not present in the runtime `.env`. The backup user is only known to the backup cron script.

Effect: a SQL injection in a runtime endpoint cannot `DROP TABLE`, cannot `CREATE USER`, cannot `SELECT INTO OUTFILE`, and cannot read any database it was not granted access to.

## 6. Query Timeout Protection

A single slow query should not hold a connection forever. Set a per-session cap:

MySQL:

```php
$db->exec('SET SESSION MAX_EXECUTION_TIME = 5000');  // milliseconds
```

Postgres:

```php
$db->exec("SET statement_timeout = '5s'");
```

This is already in the `INIT_COMMAND` above, so every new connection gets it automatically.

## 7. Connection Pooling and Multi-Tenant Context

When the app is multi-tenant, every query must be scoped to a tenant. The cleanest pattern is a session variable set at the start of each request:

MySQL with user variables:

```php
$db->exec("SET @app_tenant_id = " . (int)$tenantId);

// Use in queries:
$db->query('SELECT * FROM invoice WHERE tenant_id = @app_tenant_id');
```

Postgres with RLS (see `postgresql-administration/references/postgres-security-hardening.md`):

```php
$stmt = $db->prepare('SELECT set_config($1, $2, true)');
$stmt->execute(['app.tenant_id', (string)$tenantId]);
```

Reset at transaction end so a pooled connection cannot carry context to the next request:

```php
try {
    $db->beginTransaction();
    $this->setTenant($tenantId);
    $result = $work();
    $db->commit();
    return $result;
} finally {
    $db->exec('SET @app_tenant_id = NULL');
}
```

PgBouncer in transaction mode invalidates session-scoped `SET` — use `SET LOCAL` inside an explicit transaction.

## 8. SELECT Result Size Limit

Every list endpoint has a `LIMIT`, even if the user "should" only have a few rows. A bug or an injection that bypasses `WHERE` must not dump the whole table.

```php
public function list(int $tenantId, int $page, int $perPage = 20): array
{
    $perPage = min(max($perPage, 1), 100);      // clamp
    $offset  = max(0, ($page - 1) * $perPage);

    $stmt = $this->db->prepare(
        'SELECT id, reference, total
           FROM invoice
          WHERE tenant_id = :tenant
          ORDER BY id DESC
          LIMIT :limit OFFSET :offset'
    );
    $stmt->bindValue(':tenant', $tenantId, PDO::PARAM_INT);
    $stmt->bindValue(':limit',  $perPage,  PDO::PARAM_INT);
    $stmt->bindValue(':offset', $offset,   PDO::PARAM_INT);
    $stmt->execute();
    return $stmt->fetchAll();
}
```

Offset pagination details: `api-pagination/SKILL.md`.

## 9. Logging Sensitive Queries

Never log full SQL statements with bound values to a shared log destination. Even the query text can leak email addresses and phone numbers from `WHERE` clauses. Redact before logging:

```php
function redactQueryForLog(string $sql, array $params): array
{
    $safeParams = [];
    foreach ($params as $k => $v) {
        $safeParams[$k] = match (true) {
            is_string($v) && str_contains($k, 'email')    => '[email]',
            is_string($v) && str_contains($k, 'phone')    => '[phone]',
            is_string($v) && str_contains($k, 'password') => '[redacted]',
            is_string($v) && strlen($v) > 64              => substr($v, 0, 32) . '...',
            default                                       => $v,
        };
    }
    return ['sql' => $sql, 'params' => $safeParams];
}
```

Do not log query results containing PII. Do not log stack traces that expose the `.env`-loaded password.

## 10. ORM Safety

Modern ORMs (Doctrine, Eloquent) parameterise by default. The danger is the escape hatches.

Safe by default:

```php
// Doctrine DBAL
$row = $conn->fetchAssociative(
    'SELECT * FROM invoice WHERE id = ?',
    [$id]
);

// Eloquent
$row = Invoice::where('tenant_id', $tenantId)->find($id);
```

Danger zones:

```php
// Eloquent
DB::raw("SELECT * FROM invoice WHERE id = $id");    // INJECTABLE
Invoice::whereRaw("total > $amount");               // INJECTABLE

// Doctrine
$qb->where("i.status = '{$status}'");               // INJECTABLE

// Hydration from untrusted JSON
Invoice::fill($_POST);                              // MASS ASSIGNMENT
```

Rules:

- `raw()`/`whereRaw()` is only acceptable with explicitly parameterised bindings.
- Mass assignment fields must be whitelisted (`$fillable`).
- Never hydrate a model directly from `$_POST` or `json_decode($body, true)`.

## 11. Schema Migration Security

Migrations are code and must be reviewed. They also must never auto-run destructive operations in production without a gate.

- All `DROP TABLE`, `DROP COLUMN`, `TRUNCATE` migrations require explicit operator approval.
- Migrations run under `billing_migrate`, which is not available to the runtime.
- Migrations are idempotent so a re-run cannot corrupt state.
- A destructive migration step splits into a deprecation release (stop writing) and a removal release (drop). Expand-then-contract.

## 12. Backup Handling in App Code

If the application triggers a backup (admin-panel "Download backup now" button), the credentials must be scoped to the backup user and must not be embedded in the runtime `.env`. Options:

- Fire an asynchronous job via a queue that the backup worker picks up. The worker runs under a separate systemd unit with its own environment.
- Call a signed webhook to an internal backup service.

Never ship the backup user password in the same `.env` that the web PHP process reads.

## 13. Defender's Checklist

- [ ] PDO uses `ERRMODE_EXCEPTION` and `EMULATE_PREPARES = false`
- [ ] TLS to the database required and certificate verified
- [ ] Credentials loaded from `.env` or Vault, never in source
- [ ] `.env` mode 640, outside document root
- [ ] Separate MySQL/Postgres users per bounded context
- [ ] Runtime user has no DDL and no `FILE`/`PROCESS` privileges
- [ ] No string concatenation into SQL — prepared statements only
- [ ] `ORDER BY`/`LIMIT` values whitelisted
- [ ] Query timeout set on every connection
- [ ] Tenant context set per request and reset on transaction end
- [ ] `LIMIT` on every list endpoint, max clamped
- [ ] Logs redact email, phone, password, token
- [ ] ORM `raw()` calls reviewed and parameterised
- [ ] Mass assignment whitelisted
- [ ] Destructive migrations gated, idempotent, and separated from deploys
- [ ] Backup credentials not present in runtime environment

## 14. Anti-Patterns

- `"SELECT * FROM users WHERE email = '$email'"` string concatenation
- `PDO::ATTR_EMULATE_PREPARES = true` to "fix driver bugs"
- One shared `app` MySQL user with `GRANT ALL` for every microservice
- `.env` committed to git, or readable by `other` on the filesystem
- `DB::raw()` with user-controlled input passed directly in
- `Invoice::fill($_POST)` with no `$fillable` list
- Logging SQL with bind values to a shared log destination
- Hardcoding credentials in `config/db.php`
- No `LIMIT` on list endpoints because "there are only a few records"
- Running migrations with the runtime credential
- Setting `app.tenant_id` once per connection with PgBouncer in transaction mode

## 15. Cross-References

- `php-security/SKILL.md` — overall PHP security standards
- `php-security/references/injection-attack-patterns.md` — SQLi in depth
- `php-security/references/input-output-security.md` — validation boundary
- `mysql-best-practices/references/database-security-hardening.md` — server side
- `postgresql-administration/references/postgres-security-hardening.md` — Postgres side
- `cicd-devsecops` — Vault-backed secrets, migration pipeline
- `api-pagination` — safe `LIMIT`/offset patterns
- `multi-tenant-saas-architecture` — tenant context lifecycle
