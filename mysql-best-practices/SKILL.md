---
name: mysql-best-practices
description: "MySQL 8.x best practices for high-performance SaaS applications. Use when designing database schemas, optimizing queries, implementing multi-tenant isolation, ensuring data integrity, or building scalable African SaaS platforms. Covers character sets, indexing, normalization, stored procedures, triggers, concurrency, security, and performance."
---

# MySQL Best Practices for SaaS

Production-grade MySQL patterns for high-performance, secure, scalable SaaS applications.

**Core Principle:** Design for performance, security, and multi-tenant isolation from day one.

**See subdirectories for:** `references/` (detailed examples), `examples/` (complete schemas)

## When to Use

✅ Designing MySQL schemas for SaaS
✅ Optimizing slow queries and indexes
✅ Implementing multi-tenant isolation
✅ Building transactional systems
✅ Ensuring data integrity
✅ Scaling for high concurrency

❌ NoSQL databases
❌ OLAP/data warehouses

## Character Set

Always use UTF-8 MB4:

```sql
CREATE DATABASE saas_platform
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE TABLE users (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=DYNAMIC;
```

Supports African languages, emojis, international characters.

## Storage Engine

Always specify InnoDB for ACID compliance, row-level locking, crash recovery.

## Table Design

### Primary Keys

Use auto-increment surrogate keys (sequential, cache-friendly):

```sql
CREATE TABLE tenants (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  UNIQUE KEY uk_name (name)
) ENGINE=InnoDB;
```

### Data Types

```sql
tenant_id INT UNSIGNED NOT NULL,           -- Most FKs
amount DECIMAL(13, 2) NOT NULL,            -- Financial (never FLOAT)
currency CHAR(3) NOT NULL DEFAULT 'UGX',   -- Fixed codes
status ENUM('pending', 'completed') NOT NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
```

**Rules:** `TINYINT` (0-255), `SMALLINT` (0-65K), `INT` (0-4B), `BIGINT` (>2B), `DECIMAL` for money, `CHAR` for fixed-length.

**Timestamps:** Store in UTC, convert at application layer.

## Normalization

### 1NF: Atomic Values

```sql
-- ✗ WRONG: items VARCHAR(500) -- "item1,item2"
-- ✓ CORRECT: Separate order_items table
```

### 2NF: Depend on Entire Key

```sql
-- ✗ WRONG: item_name depends on item_id, not whole PK
-- ✓ CORRECT: item_name in items table
```

### 3NF: Depend Only on PK

```sql
-- ✗ WRONG: department_name depends on department_id
-- ✓ CORRECT: Separate departments table
```

### Strategic Denormalization

For performance when normalization is costly. Keep in sync via triggers.

## Indexing

### Index Types

```sql
-- PRIMARY KEY - Clustered (contains row data)
id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY

-- UNIQUE KEY - Uniqueness + fast lookup
UNIQUE KEY uk_registration (registration_number)

-- Regular KEY - WHERE, JOIN, ORDER BY
KEY idx_tenant_customer (tenant_id, customer_id)

-- FULLTEXT - Text search
FULLTEXT INDEX ft_search (title, content)
```

### Composite Indexes (ESR)

**Equality, Sort, Range:**

```sql
-- Query: WHERE tenant_id = ? AND status = ? ORDER BY order_date DESC
KEY idx_esr (tenant_id, status, order_date DESC)
```

### Best Practices

```sql
-- ✓ DO: Specific
KEY idx_active (is_active, created_at DESC)

-- ✗ DON'T: Redundant
KEY idx_tenant (tenant_id)
KEY idx_tenant_dup (tenant_id) -- Redundant

-- Left-most prefix: KEY (a, b, c) works for a | a+b | a+b+c

-- ✗ DON'T: Low cardinality
KEY idx_deleted (is_deleted) -- Only 2 values

-- Monitor unused
SELECT object_name FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE count_read = 0 AND index_name != 'PRIMARY';
```

## Foreign Keys

```sql
CREATE TABLE organizations (
  id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  tenant_id INT UNSIGNED NOT NULL,
  FOREIGN KEY fk_tenant (tenant_id) REFERENCES tenants(id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  KEY idx_tenant_id (tenant_id)
);
```

**Strategies:**
- `RESTRICT` - Prevent deletion if children exist
- `CASCADE` - Delete children when parent deleted
- `SET NULL` - Set FK to NULL
- `UPDATE CASCADE` - Update FK (rare with auto-increment)

## Stored Procedures

**See `references/stored-procedures.sql`**

```sql
CREATE PROCEDURE sp_process(IN p_id BIGINT, OUT p_success BOOLEAN)
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; SET p_success = FALSE; END;
  START TRANSACTION;
  SELECT id INTO @v FROM table WHERE id = p_id FOR UPDATE;
  COMMIT;
  SET p_success = TRUE;
END;
```

## Triggers

**See `references/triggers.sql`**

```sql
-- Audit trail
CREATE TRIGGER tr_audit AFTER UPDATE ON customers FOR EACH ROW
BEGIN
  INSERT INTO audit_log (table_name, record_id, old_values, new_values)
  VALUES ('customers', NEW.id, JSON_OBJECT('email', OLD.email), JSON_OBJECT('email', NEW.email));
END;

-- Data consistency
CREATE TRIGGER tr_total AFTER INSERT ON order_items FOR EACH ROW
BEGIN
  UPDATE orders SET total = (SELECT SUM(qty * price) FROM order_items WHERE order_id = NEW.order_id)
  WHERE id = NEW.order_id;
END;
```

## Concurrency

```sql
-- Isolation level
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- Row-level locking (consistent order prevents deadlocks)
START TRANSACTION;
SELECT * FROM accounts WHERE id = LEAST(100, 200) FOR UPDATE;
SELECT * FROM accounts WHERE id = GREATEST(100, 200) FOR UPDATE;
COMMIT;
```

## Security

### User Privileges

```sql
-- Application user (never root)
CREATE USER 'saas_app'@'%' IDENTIFIED BY 'strong_password';
GRANT SELECT, INSERT, UPDATE ON saas_platform.* TO 'saas_app'@'%';
REVOKE FILE, PROCESS, SHUTDOWN ON *.* FROM 'saas_app'@'%';
```

### Encryption

```sql
-- TDE (my.cnf): default-table-encryption = ON
-- SSL (my.cnf): require_secure_transport = ON
-- Application-level: phone_encrypted VARBINARY(255) -- AES-256 at app layer
```

### SQL Injection

```sql
-- ✗ DON'T: SET @q = CONCAT('SELECT * FROM users WHERE id = ', p_id);
-- ✓ DO: Parameterized
PREPARE stmt FROM 'SELECT * FROM users WHERE id = ? AND tenant_id = ?';
EXECUTE stmt USING p_user_id, p_tenant_id;
DEALLOCATE PREPARE stmt;
```

### Multi-Tenant Isolation

Always include `tenant_id` in WHERE clauses. Never allow queries without tenant filter.

## Performance

### Query Optimization

```sql
-- 1. EXPLAIN to analyze
EXPLAIN FORMAT=JSON SELECT * FROM orders WHERE tenant_id = 1;

-- 2. Covering indexes (index-only queries)
KEY idx_covering (tenant_id, status, created_at DESC)
SELECT tenant_id, status, created_at FROM orders WHERE tenant_id = 1;

-- 3. Avoid SELECT *
-- 4. LIMIT with indexed ORDER BY
-- 5. JOIN instead of subqueries
```

### Statistics

```sql
ANALYZE TABLE customers, orders;
SET GLOBAL innodb_stats_persistent = ON;
SET GLOBAL innodb_stats_auto_recalc = ON;
```

### Slow Query Log

```sql
-- my.cnf: slow_query_log = 1, long_query_time = 2, log_queries_not_using_indexes = 1
```

### Partitioning

**See `references/partitioning.sql`**

```sql
-- By tenant: PARTITION BY HASH(tenant_id) PARTITIONS 10;
-- By date: PARTITION BY RANGE(YEAR(created_at))
```

## Backup

```sql
-- Binary logging (my.cnf): log_bin = mysql-bin, binlog_format = ROW
-- Full: mysqldump --single-transaction --all-databases > backup.sql
-- Point-in-time: mysqlbinlog mysql-bin.000003 --stop-datetime="2024-01-15 12:00" | mysql
```

## Monitoring

```sql
SHOW STATUS LIKE 'Threads%';
SELECT table_name, data_free FROM information_schema.tables WHERE data_free > 0;
OPTIMIZE TABLE customers, orders; -- Low-traffic periods
SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_reads%';
```

## Connection Pooling

```sql
SET GLOBAL max_connections = 1000;
SET GLOBAL wait_timeout = 28800;
-- Pool size: 30-50 per app server, 50-100 for high concurrency
```

## Checklist

**Schema:**
- [ ] UTF8MB4 + InnoDB + ROW_FORMAT=DYNAMIC
- [ ] Auto-increment PKs, appropriate data types
- [ ] 3NF normalized

**Indexes:**
- [ ] ESR composite indexes
- [ ] No redundant indexes
- [ ] Regular ANALYZE TABLE

**Integrity:**
- [ ] Explicit foreign keys
- [ ] Audit triggers

**Multi-Tenant:**
- [ ] tenant_id in all queries

**Concurrency:**
- [ ] Row-level locking, consistent ordering

**Security:**
- [ ] Application user (not root)
- [ ] Minimal privileges
- [ ] Parameterized queries
- [ ] TDE + SSL encryption

**Performance:**
- [ ] Connection pooling
- [ ] Slow query logging
- [ ] EXPLAIN on critical queries

**Operations:**
- [ ] Binary logging
- [ ] Backup testing
- [ ] Monitoring

## Summary

1. UTF8MB4 + InnoDB always
2. Size data types appropriately
3. Normalize to 3NF, denormalize strategically
4. ESR composite indexes
5. Tenant isolation everywhere
6. Parameterized queries only
7. Encrypt sensitive data
8. Monitor continuously

**Remember:** Design for multi-tenant isolation, security, and performance from day one.
