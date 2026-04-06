# Database & ORM Patterns

> Source: Sommerfeld — Unlock PHP 8 (Ch. 7–8); Martin — PHP Advanced (Ch. 1–2)

## Table of Contents

1. [PDO Patterns](#pdo-patterns)
2. [QueryBuilder](#querybuilder)
3. [Base Model (Active Record)](#base-model-active-record)
4. [Soft Delete](#soft-delete)
5. [ORM Concepts](#orm-concepts)
6. [DB Optimization Rules](#db-optimization-rules)

---

## PDO Patterns

### Connection (Singleton)

```php
<?php

final class Database
{
    private static ?self $instance = null;
    private \PDO $connection;

    private function __construct()
    {
        $dsn = sprintf(
            'mysql:host=%s;dbname=%s;charset=utf8mb4',
            $_ENV['DB_HOST'],
            $_ENV['DB_NAME'],
        );
        $this->connection = new \PDO($dsn, $_ENV['DB_USER'], $_ENV['DB_PASS'], [
            \PDO::ATTR_ERRMODE            => \PDO::ERRMODE_EXCEPTION,
            \PDO::ATTR_DEFAULT_FETCH_MODE => \PDO::FETCH_OBJ,
            \PDO::ATTR_EMULATE_PREPARES   => false,
        ]);
    }

    public static function instance(): static
    {
        if (static::$instance === null) {
            static::$instance = new static();
        }
        return static::$instance;
    }

    public function connection(): \PDO
    {
        return $this->connection;
    }
}
```

### CRUD with Prepared Statements

```php
<?php

$pdo = Database::instance()->connection();

// INSERT
$stmt = $pdo->prepare('INSERT INTO users (name, email, password) VALUES (:name, :email, :password)');
$stmt->execute([
    ':name'     => $name,
    ':email'    => $email,
    ':password' => password_hash($plain, PASSWORD_ARGON2ID),
]);
$newId = (int) $pdo->lastInsertId();

// SELECT
$stmt = $pdo->prepare('SELECT * FROM users WHERE id = :id');
$stmt->execute([':id' => $id]);
$user = $stmt->fetch();          // PDO::FETCH_OBJ (default)
$users = $stmt->fetchAll();

// UPDATE
$stmt = $pdo->prepare('UPDATE users SET name = :name WHERE id = :id');
$stmt->execute([':name' => $name, ':id' => $id]);
$affected = $stmt->rowCount();

// DELETE
$stmt = $pdo->prepare('DELETE FROM users WHERE id = :id');
$stmt->execute([':id' => $id]);
```

### Transactions

```php
<?php

$pdo = Database::instance()->connection();

try {
    $pdo->beginTransaction();

    $pdo->prepare('UPDATE accounts SET balance = balance - :amount WHERE id = :from')
        ->execute([':amount' => $amount, ':from' => $fromId]);

    $pdo->prepare('UPDATE accounts SET balance = balance + :amount WHERE id = :to')
        ->execute([':amount' => $amount, ':to' => $toId]);

    $pdo->commit();
} catch (\Throwable $e) {
    $pdo->rollBack();
    throw $e;
}
```

**Rules:**
- Always `PDO::ERRMODE_EXCEPTION` — never silent failures
- Always `PDO::ATTR_EMULATE_PREPARES => false` — real prepared statements
- Always use named parameters (`:name`) not positional (`?`) for clarity
- Use `FETCH_OBJ` for data display, `FETCH_ASSOC` when building arrays

---

## QueryBuilder

Builds parameterized SQL from method chains. Used internally by the Base Model.

```php
<?php

final class QueryBuilder
{
    public array $bindings = [];
    private int $paramIndex = 0;

    public function buildSelect(string $table, array $conditions): string
    {
        $sql = "SELECT * FROM `{$table}`";
        if (!empty($conditions)) {
            $parts = [];
            foreach ($conditions as [$column, $operator, $value]) {
                $key = ':param' . $this->paramIndex++;
                $parts[] = "`{$column}` {$operator} {$key}";
                $this->bindings[$key] = $value;
            }
            $sql .= ' WHERE ' . implode(' AND ', $parts);
        }
        return $sql;
    }

    public function buildInsert(string $table, array $data): string
    {
        $columns  = implode(', ', array_map(fn($c) => "`{$c}`", array_keys($data)));
        $placeholders = implode(', ', array_map(fn($c) => ":{$c}", array_keys($data)));
        return "INSERT INTO `{$table}` ({$columns}) VALUES ({$placeholders})";
    }

    public function buildUpdate(string $table, array $data, array $conditions): string
    {
        $sets = implode(', ', array_map(fn($c) => "`{$c}` = :{$c}", array_keys($data)));
        $sql  = "UPDATE `{$table}` SET {$sets}";

        foreach ($data as $key => $value) {
            $this->bindings[":{$key}"] = $value;
        }

        if (!empty($conditions)) {
            $parts = [];
            foreach ($conditions as [$column, $operator, $value]) {
                $param = ':cond' . $this->paramIndex++;
                $parts[] = "`{$column}` {$operator} {$param}";
                $this->bindings[$param] = $value;
            }
            $sql .= ' WHERE ' . implode(' AND ', $parts);
        }
        return $sql;
    }

    public function buildDelete(string $table, array $conditions): string
    {
        $sql = "DELETE FROM `{$table}`";
        if (!empty($conditions)) {
            $parts = [];
            foreach ($conditions as [$column, $operator, $value]) {
                $param = ':cond' . $this->paramIndex++;
                $parts[] = "`{$column}` {$operator} {$param}";
                $this->bindings[$param] = $value;
            }
            $sql .= ' WHERE ' . implode(' AND ', $parts);
        }
        return $sql;
    }

    public function reset(): void
    {
        $this->bindings = [];
        $this->paramIndex = 0;
    }
}
```

---

## Base Model (Active Record)

Extend this to create any model. Methods are chainable.

```php
<?php

abstract class Model
{
    public string $table;
    public bool $softDelete = false;

    private \PDO $db;
    private QueryBuilder $queryBuilder;
    private array $conditions = [];

    public function __construct()
    {
        $this->db = Database::instance()->connection();
        $this->queryBuilder = new QueryBuilder();
    }

    // ── Conditions ───────────────────────────────────────

    public function where(string $column, string $operator, mixed $value): static
    {
        $this->conditions[] = [$column, $operator, $value];
        return $this;
    }

    // ── Reads ─────────────────────────────────────────────

    public function all(): array
    {
        $sql  = $this->queryBuilder->buildSelect($this->table, $this->conditions);
        $stmt = $this->db->prepare($sql);
        $stmt->execute($this->queryBuilder->bindings);
        $this->reset();
        return $stmt->fetchAll();
    }

    public function first(): ?object
    {
        $sql  = $this->queryBuilder->buildSelect($this->table, $this->conditions);
        $stmt = $this->db->prepare($sql);
        $stmt->execute($this->queryBuilder->bindings);
        $this->reset();
        return $stmt->fetch() ?: null;
    }

    public function find(int $id): ?object
    {
        return $this->where('id', '=', $id)->first();
    }

    // ── Writes ────────────────────────────────────────────

    public function create(array $data): bool
    {
        $sql  = $this->queryBuilder->buildInsert($this->table, $data);
        $stmt = $this->db->prepare($sql);
        return $stmt->execute($data);
    }

    public function update(array $data): bool
    {
        $sql  = $this->queryBuilder->buildUpdate($this->table, $data, $this->conditions);
        $stmt = $this->db->prepare($sql);
        $result = $stmt->execute($this->queryBuilder->bindings);
        $this->reset();
        return $result;
    }

    public function delete(): bool
    {
        if ($this->softDelete) {
            return $this->logicDelete();
        }
        $sql  = $this->queryBuilder->buildDelete($this->table, $this->conditions);
        $stmt = $this->db->prepare($sql);
        $result = $stmt->execute($this->queryBuilder->bindings);
        $this->reset();
        return $result;
    }

    // ── Helpers ───────────────────────────────────────────

    private function logicDelete(): bool
    {
        return $this->update(['deleted_at' => date('Y-m-d H:i:s')]);
    }

    private function reset(): void
    {
        $this->conditions = [];
        $this->queryBuilder->reset();
    }
}
```

### Concrete Model Examples

```php
<?php

// User model — with soft delete
final class User extends Model
{
    public string $table = 'users';
    public bool $softDelete = true;
}

// Task model — with domain methods
final class Task extends Model
{
    public string $table = 'tasks';
    public bool $softDelete = true;

    public function createTask(array $data): bool
    {
        return $this->create($data);
    }

    public function markCompleted(int $id): bool
    {
        return $this->where('id', '=', $id)->update(['is_concluded' => 1]);
    }

    public function deleteById(int $id): bool
    {
        return $this->where('id', '=', $id)->delete();
    }
}
```

### Usage (Fluent API)

```php
// Fetch all tasks for current user
$tasks = (new Task())
    ->where('user_id', '=', $userId)
    ->where('is_concluded', '=', 0)
    ->all();

// Get single user
$user = (new User())->find($id);

// Create
(new User())->create([
    'name'     => $name,
    'login'    => $login,
    'password' => password_hash($pass, PASSWORD_ARGON2ID),
]);

// Update with condition
(new Task())->where('id', '=', $taskId)->update(['title' => $newTitle]);

// Soft delete
(new User())->where('id', '=', $userId)->delete();
// → sets deleted_at, does NOT remove row
```

---

## Soft Delete

When `$softDelete = true`, `delete()` sets `deleted_at` timestamp instead of removing the row.

```php
// Add to migration:
$table->timestamp('deleted_at')->nullable();

// Exclude soft-deleted from queries (add to all() or create scope):
public function active(): array
{
    return $this->where('deleted_at', 'IS', null)->all();
}

// Show deleted records:
public function withTrashed(): array
{
    // Don't add deleted_at condition
    return $this->all();
}
```

---

## ORM Concepts

| Concept | What It Means |
|---------|--------------|
| **Active Record** | Model wraps DB row — has CRUD methods + business logic |
| **Repository** | Separates data access from domain logic (preferred in DDD) |
| **Lazy Loading** | Relations loaded only when accessed (`$user->posts`) |
| **Eager Loading** | Relations pre-fetched in initial query (`with(['posts'])`) |
| **N+1 Problem** | Lazy loading in a loop causes 1 + N queries — use eager loading |
| **Migration** | Version-controlled DB schema changes (never edit past migrations) |

**In Laravel/Eloquent:**

```php
// Eager load to avoid N+1
$users = User::with(['posts', 'profile'])->get();

// Scopes
public function scopeActive(Builder $query): Builder
{
    return $query->whereNull('deleted_at');
}
User::active()->get();
```

---

## DB Optimization Rules

From Sommerfeld Ch. 7:

```php
// ✗ DON'T: SELECT *
$stmt = $pdo->query('SELECT * FROM users');

// ✓ DO: Select only needed columns
$stmt = $pdo->query('SELECT id, name, email FROM users');

// ✗ DON'T: Function on WHERE column — kills index
$pdo->query('SELECT * FROM orders WHERE YEAR(created_at) = 2026');

// ✓ DO: Range condition — index-friendly
$pdo->query("SELECT * FROM orders WHERE created_at BETWEEN '2026-01-01' AND '2026-12-31'");

// ✓ DO: LIMIT on large tables
$pdo->query('SELECT id, name FROM products ORDER BY name LIMIT 50');
```

**Index rules:**
- Index every foreign key column
- Index every column used in `WHERE`, `ORDER BY`, `GROUP BY`
- Use composite indexes when multiple columns always queried together
- Never index columns with low cardinality (boolean, gender)

**Cache strategy with Memcached:**

```php
$key  = 'query:' . md5($sql . serialize($params));
$data = $memcached->get($key);

if ($data === false) {
    $stmt = $pdo->prepare($sql);
    $stmt->execute($params);
    $data = $stmt->fetchAll();
    $memcached->set($key, $data, 3600);  // 1-hour TTL
}

return $data;
```

---

**Sources:** Sommerfeld, Unlock PHP 8 Ch. 7–8 (2024); Martin, PHP Advanced Ch. 1–2 (2023)
