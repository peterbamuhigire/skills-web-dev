# MySQL 8 Exclusive Features Reference

Deep reference for the `mysql-best-practices` skill. Covers MySQL 8.0-specific DDL
and operational features not available in earlier versions.

**Source:** Advanced MySQL 8 (Vanier et al., Packt 2019)

---

## CHECK Constraints (8.0.16+)

Enforce domain rules at the database layer. Checked on INSERT and UPDATE.

```sql
CREATE TABLE products (
  id   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  price      DECIMAL(13,2) NOT NULL,
  stock      INT NOT NULL DEFAULT 0,
  discount   DECIMAL(5,2) NOT NULL DEFAULT 0.00,
  status     ENUM('draft','active','archived') NOT NULL DEFAULT 'draft',
  CONSTRAINT chk_price_positive  CHECK (price > 0),
  CONSTRAINT chk_stock_gte_zero  CHECK (stock >= 0),
  CONSTRAINT chk_discount_range  CHECK (discount BETWEEN 0 AND 100)
);

-- Add to an existing table
ALTER TABLE orders
  ADD CONSTRAINT chk_total_positive CHECK (total >= 0);

-- NOT ENFORCED: documents intent but does not block violations
ALTER TABLE legacy_data
  ADD CONSTRAINT chk_legacy_amount CHECK (amount >= 0) NOT ENFORCED;

-- Inspect constraints
SELECT CONSTRAINT_NAME, CHECK_CLAUSE, ENFORCED
FROM information_schema.CHECK_CONSTRAINTS
WHERE CONSTRAINT_SCHEMA = DATABASE();
```

**Rules:**
- Violations raise `ER_CHECK_CONSTRAINT_VIOLATED` (error 3819), rolling back the statement.
- `NOT ENFORCED` is useful when migrating legacy data that has existing violations.
- Generated columns (`VIRTUAL`/`STORED`) can be referenced inside CHECK expressions.

---

## Invisible Columns (8.0.23+)

Columns marked `INVISIBLE` are excluded from `SELECT *` but remain fully accessible
by name. The primary use case is zero-downtime schema migration: add a column without
breaking existing `SELECT *` queries or application code.

```sql
-- Add an invisible column (does not appear in SELECT *)
ALTER TABLE users
  ADD COLUMN legacy_id BIGINT DEFAULT NULL INVISIBLE;

-- Access it explicitly
SELECT id, email, legacy_id FROM users WHERE legacy_id IS NOT NULL;

-- Make it visible when migration is complete
ALTER TABLE users MODIFY COLUMN legacy_id BIGINT DEFAULT NULL VISIBLE;

-- Create with INVISIBLE inline
CREATE TABLE events (
  id         BIGINT AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(255) NOT NULL,
  _row_hash  CHAR(64) GENERATED ALWAYS AS (SHA2(name, 256)) STORED INVISIBLE
);
```

**Rules:**
- A table must have at least one visible column at all times.
- INVISIBLE columns still participate in constraints, triggers, and indexed operations.

---

## Instant ADD COLUMN (8.0.12+)

`ALGORITHM=INSTANT` adds a column by updating only the data dictionary — no table
rebuild, no row-by-row copy, no downtime. Available for InnoDB tables.

```sql
-- Add a column in milliseconds regardless of table size
ALTER TABLE orders
  ADD COLUMN source_channel VARCHAR(50) DEFAULT NULL,
  ALGORITHM = INSTANT;

-- Check if the operation supports INSTANT (MySQL 8.0.29+)
-- instant_cols > 0 means the row format supports instant-added columns
SELECT TABLE_NAME, instant_cols
FROM information_schema.INNODB_TABLES
WHERE NAME = 'saas_platform/orders';
```

**Limitations — falls back to COPY/INPLACE if:**
- Column is added at a position other than the last (8.0.12–8.0.28 only; 8.0.29+ allows any position).
- `ROW_FORMAT=COMPRESSED` is in use.
- Adding a generated column or modifying column type.

**Anti-pattern:** After many instant-adds the row format carries extra metadata. Run `OPTIMIZE TABLE` during a maintenance window to rebuild cleanly.

---

## Lateral Derived Tables (8.0.14+)

A `LATERAL` derived table can reference columns from tables that appear earlier in
the `FROM` clause — essentially a correlated subquery expressed as a join. This is
often cleaner and more efficient than a correlated scalar subquery.

```sql
-- Last order per customer (lateral replaces correlated subquery)
SELECT c.id, c.name, last_order.total, last_order.created_at
FROM customers c
JOIN LATERAL (
    SELECT total, created_at
    FROM orders o
    WHERE o.customer_id = c.id AND o.tenant_id = c.tenant_id
    ORDER BY created_at DESC
    LIMIT 1
) AS last_order ON TRUE
WHERE c.tenant_id = 1;

-- Top-N per group using LATERAL (avoids window function CTE pattern)
SELECT p.category, top3.name, top3.revenue
FROM categories p
JOIN LATERAL (
    SELECT name, revenue
    FROM products pr
    WHERE pr.category_id = p.id
    ORDER BY revenue DESC
    LIMIT 3
) AS top3 ON TRUE;
```

**When to use LATERAL vs window functions:**
- `LATERAL` shines for `LIMIT N` per group — it avoids scanning the entire partition.
- Window functions are cleaner for ranking or aggregation over the full set.

---

## Clone Plugin (8.0.17+)

Provisions a new replica (or recover a crashed one) by cloning an online donor instance.
Faster and simpler than `mysqldump` or manual XtraBackup workflows for large datasets.

```sql
-- 1. Install on both donor and recipient
INSTALL PLUGIN clone SONAME 'mysql_clone.so';

-- 2. On the donor: create a clone user
CREATE USER 'clone_donor'@'%' IDENTIFIED BY 'strong_password';
GRANT BACKUP_ADMIN ON *.* TO 'clone_donor'@'%';

-- 3. On the recipient: grant clone privilege and run the clone
CREATE USER 'clone_user'@'localhost' IDENTIFIED BY 'strong_password';
GRANT CLONE_ADMIN ON *.* TO 'clone_user'@'localhost';

-- As clone_user on the recipient:
SET GLOBAL clone_valid_donor_list = '10.0.1.10:3306';
CLONE INSTANCE FROM 'clone_donor'@'10.0.1.10':3306
  IDENTIFIED BY 'strong_password';
```

**Behaviour:**
- The recipient instance **restarts automatically** after a remote clone.
- Clone captures a consistent snapshot; binary log position is preserved so you can
  immediately execute `CHANGE REPLICATION SOURCE TO` and start replication.
- Local clone (`CLONE LOCAL DATA DIRECTORY = '/path/to/clone'`) copies data without
  restart — useful for hot backups.

---

## Resource Groups (8.0.3+)

Assign CPU thread affinity and priority to different workload types. Useful for
preventing analytical queries from starving OLTP traffic on the same server.

```sql
-- Create a low-priority group for background/reporting queries (CPUs 0-1)
CREATE RESOURCE GROUP reporting_rg
  TYPE = USER
  VCPU = 0-1
  THREAD_PRIORITY = 10;       -- Higher number = lower priority (range: -20 to 19)

-- Create a high-priority group for OLTP (CPUs 2-7)
CREATE RESOURCE GROUP oltp_rg
  TYPE = USER
  VCPU = 2-7
  THREAD_PRIORITY = -10;

-- Assign the current session
SET RESOURCE GROUP reporting_rg;

-- Assign a specific connection by thread ID
SELECT THREAD_ID FROM performance_schema.threads WHERE PROCESSLIST_ID = CONNECTION_ID();
SET RESOURCE GROUP oltp_rg FOR THREAD = 48;

-- Inspect groups
SELECT * FROM information_schema.RESOURCE_GROUPS;
```

**Practical pattern:** Tag reporting/export jobs with `reporting_rg` at the start of
the stored procedure; this prevents a slow monthly report from blocking OLTP.

**Requirement:** The `CAP_SYS_NICE` OS capability is needed on Linux to set negative
(elevated) thread priorities. Without it, negative values are silently ignored.

---

## Descending Indexes (8.0.0+)

MySQL 8.0 is the first version to store descending indexes in descending physical order.
(In MySQL 5.x, `DESC` in an index definition was parsed but ignored — the index was still
ascending and a filesort was used for `ORDER BY col DESC`.)

```sql
-- Composite index matching a mixed-sort ORDER BY
CREATE TABLE events (
  id         BIGINT AUTO_INCREMENT PRIMARY KEY,
  tenant_id  INT UNSIGNED NOT NULL,
  severity   TINYINT NOT NULL,
  occurred_at DATETIME NOT NULL,
  KEY idx_sev_time (tenant_id, severity DESC, occurred_at DESC)
);

-- This query uses the index with NO filesort
SELECT * FROM events
WHERE tenant_id = 1
ORDER BY severity DESC, occurred_at DESC
LIMIT 25;
```

**Rule:** Match the `ASC`/`DESC` in the index definition exactly to the `ORDER BY`
direction. Mixed-direction sort (e.g., `ORDER BY a ASC, b DESC`) is the key use case —
a single-direction index cannot satisfy it without a filesort.

> Already briefly noted in the main SKILL.md Indexing section. This entry provides the
> full rationale and confirms 5.x behaviour change.

---

## MySQL Roles — Quick Reference

Full coverage is in `security-hardening.md` (Role-Based Access Control section).
Summary pattern for quick reference:

```sql
CREATE ROLE 'app_read', 'app_write';
GRANT SELECT ON db.* TO 'app_read';
GRANT INSERT, UPDATE, DELETE ON db.* TO 'app_write';
GRANT 'app_read', 'app_write' TO 'saas_app'@'%';
SET DEFAULT ROLE ALL TO 'saas_app'@'%';
```

Roles replace manual per-user `GRANT` sprawl. Revoking a role propagates to all
users who hold it. See `security-hardening.md` for full management commands.

---

## Cross-References

- **Roles (full):** `security-hardening.md` — Role-Based Access Control section
- **Window functions (full):** `advanced-sql-patterns.md` — Window Functions section
- **Instant ADD COLUMN in migrations:** main `SKILL.md` — Migrations section
- **Clone for HA provisioning:** `high-availability.md`

---

**Source:** Advanced MySQL 8 (Vanier, Garnier, Hristov — Packt, 2019)
**Last Updated:** 2026-04-06
**Maintained by:** Peter Bamuhigire
