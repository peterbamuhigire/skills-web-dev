# Database Standards (CRITICAL)

**MANDATORY:** All database-related work MUST reference the `mysql-best-practices` skill.

## When to Use mysql-best-practices

### ALWAYS Use For

✅ **Database migrations** (adding/dropping tables, columns)
✅ **Schema design and modifications**
✅ **Creating/updating stored procedures, triggers, views**
✅ **Adding indexes or foreign keys**
✅ **Query optimization**
✅ **Multi-tenant isolation patterns**

### Failure to Use = Production Failures

**CRITICAL:** The mysql-best-practices skill includes comprehensive standards that prevent production failures. Skipping this skill when doing database work has caused real production issues in the past.

See project MEMORY.md for examples of failures caused by not following these standards.

## Migration Checklist (MANDATORY)

This checklist MUST be followed for ALL database changes:

### Pre-Migration (Before Making Changes)

**1. Grep entire codebase for references**

Search for any references to tables/columns you're modifying:

```bash
# Search for table name
grep -r "table_name" --include="*.php" --include="*.sql"

# Search for column name
grep -r "column_name" --include="*.php" --include="*.sql"

# Search in stored procedures
grep -r "column_name" database/procedures/
```

**Why this matters:** Finding all references prevents orphaned code that will break in production.

**2. Check all stored procedures, triggers, views**

```bash
# List all procedures
SELECT ROUTINE_NAME FROM information_schema.ROUTINES
WHERE ROUTINE_SCHEMA = 'your_db';

# List all triggers
SELECT TRIGGER_NAME FROM information_schema.TRIGGERS
WHERE TRIGGER_SCHEMA = 'your_db';

# List all views
SELECT TABLE_NAME FROM information_schema.VIEWS
WHERE TABLE_SCHEMA = 'your_db';
```

**Verify each one for references to the table/column you're modifying.**

**3. Backup database**

```bash
# Full backup
mysqldump -u root -p database_name > backup_$(date +%Y%m%d_%H%M%S).sql

# Specific table backup
mysqldump -u root -p database_name table_name > table_backup_$(date +%Y%m%d_%H%M%S).sql
```

### During Migration (Executing Changes)

**4. Run migration in transaction (when possible)**

```sql
START TRANSACTION;

-- Your migration SQL here
ALTER TABLE table_name ADD COLUMN new_column VARCHAR(255);

-- Verify the change
SHOW COLUMNS FROM table_name;

-- If everything looks good:
COMMIT;

-- If something is wrong:
-- ROLLBACK;
```

**5. Test the migration on a copy first**

```bash
# Create test database
CREATE DATABASE test_database_name;

# Copy structure
mysqldump -u root -p --no-data database_name | mysql -u root -p test_database_name

# Run migration on test database first
mysql -u root -p test_database_name < migration.sql
```

### Post-Migration (After Changes)

**6. Verify no orphaned references in code**

Run the same grep commands from step 1:

```bash
# Check for old column references that no longer exist
grep -r "old_column_name" --include="*.php" --include="*.sql"
```

**If found:** Update all references to use the new column name or remove deprecated code.

**7. Test all affected endpoints**

- Identify all API endpoints that touch the modified table
- Test each endpoint manually or with automated tests
- Verify data is correctly saved and retrieved
- Check error handling still works

**8. Export updated schema**

```bash
# Export full schema
mysqldump -u root -p --no-data database_name > database/schema/full_schema.sql

# Export specific table schema
mysqldump -u root -p --no-data database_name table_name > database/schema/table_name.sql
```

**9. Document rollback procedure**

Create a rollback migration:

```sql
-- migration_rollback_YYYY_MM_DD.sql

-- Reverse your changes
ALTER TABLE table_name DROP COLUMN new_column;

-- Or restore from backup
-- SOURCE backup_20260207_143000.sql;
```

## Common Database Mistakes

### Mistake 1: Not Checking Stored Procedures

❌ **BAD:**
```
DROP TABLE old_table;
-- Oops! sp_get_inventory_report still references old_table
-- Production error: Table doesn't exist
```

✅ **GOOD:**
```bash
# Before dropping table, check all procedures
grep -r "old_table" database/procedures/

# Found: sp_get_inventory_report references it
# Update procedure first, THEN drop table
```

### Mistake 2: Not Updating Service Classes

❌ **BAD:**
```sql
ALTER TABLE users RENAME COLUMN user_name TO username;
```

```php
// src/Services/UserService.php still uses:
$stmt = $db->prepare('SELECT user_name FROM users'); // FAILS!
```

✅ **GOOD:**
```bash
# Grep for all references before renaming
grep -r "user_name" src/ database/

# Update all PHP code
# Update all SQL files
# THEN run migration
```

### Mistake 3: Not Testing Endpoints

❌ **BAD:**
```
Run migration → Deploy → Production errors
```

✅ **GOOD:**
```
Run migration → Test all affected endpoints → Verify data → Deploy
```

### Mistake 4: No Rollback Plan

❌ **BAD:**
```
Migration breaks production → Panic → Manual fixes → Data corruption
```

✅ **GOOD:**
```
Migration breaks → Execute documented rollback → Restore backup → Fix issue → Re-run migration
```

## Schema Design Standards

### Multi-Tenant Isolation

**ALWAYS include tenant_id when multi-tenant:**

```sql
CREATE TABLE inventory (
    id INT PRIMARY KEY AUTO_INCREMENT,
    tenant_id INT NOT NULL DEFAULT 1,  -- Required for multi-tenant
    item_name VARCHAR(255),

    INDEX idx_tenant (tenant_id),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);
```

**NEVER query without tenant_id filter (in multi-tenant apps):**

```sql
-- ❌ BAD: No tenant filter
SELECT * FROM inventory WHERE item_name = ?;

-- ✅ GOOD: Always filter by tenant
SELECT * FROM inventory WHERE tenant_id = ? AND item_name = ?;
```

### Naming Conventions

**Tables:**
- Use `snake_case` (plural)
- Examples: `stock_items`, `sales_orders`, `gl_accounts`

**Columns:**
- Use `snake_case` (singular)
- Examples: `item_name`, `order_date`, `account_code`

**Foreign Keys:**
- Format: `referenced_table_id`
- Examples: `customer_id`, `vendor_id`, `category_id`

**Indexes:**
- Format: `idx_table_column` or `idx_table_purpose`
- Examples: `idx_sales_customer`, `idx_inventory_tenant`

### Data Types

**Use appropriate types:**

```sql
-- ✅ GOOD: Specific types
id INT PRIMARY KEY AUTO_INCREMENT
amount DECIMAL(15,2)  -- For money
quantity DECIMAL(10,3)  -- For quantities with decimals
is_active TINYINT(1)  -- For booleans
created_at DATETIME DEFAULT CURRENT_TIMESTAMP

-- ❌ BAD: Vague types
id VARCHAR(255)  -- Waste of space, slow indexing
amount FLOAT  -- Precision errors with money
quantity INT  -- Can't handle decimal quantities
is_active VARCHAR(10)  -- Should be boolean
```

### Indexes

**Add indexes for:**
- Foreign keys
- Frequently queried columns
- Columns used in WHERE clauses
- Columns used in ORDER BY
- Columns used in JOINs

```sql
-- Foreign key indexes
INDEX idx_customer (customer_id)
INDEX idx_tenant (tenant_id)

-- Query optimization indexes
INDEX idx_status (status)
INDEX idx_date (transaction_date)
INDEX idx_composite (tenant_id, status, created_at)
```

### Constraints

**Use constraints for data integrity:**

```sql
CREATE TABLE sales_orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    status ENUM('draft', 'confirmed', 'completed', 'cancelled') DEFAULT 'draft',
    total_amount DECIMAL(15,2) NOT NULL DEFAULT 0.00,

    -- Foreign keys
    FOREIGN KEY (customer_id) REFERENCES customers(id),

    -- Check constraints
    CHECK (total_amount >= 0),
    CHECK (order_date <= CURRENT_DATE)
);
```

## Stored Procedures Standards

### Naming Conventions

**Procedures:**
- Prefix: `sp_`
- Format: `sp_action_entity`
- Examples: `sp_get_inventory_report`, `sp_post_sales_invoice`

**Functions:**
- Prefix: `fn_`
- Format: `fn_description`
- Examples: `fn_convert_uom_quantity`, `fn_get_inventory_gl_account`

### Structure

```sql
DELIMITER //

CREATE PROCEDURE sp_example_procedure(
    IN p_parameter_id INT,
    IN p_parameter_name VARCHAR(255),
    OUT p_result_id INT
)
BEGIN
    -- Declare variables
    DECLARE v_local_var INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        -- Rollback on error
        ROLLBACK;
        RESIGNAL;
    END;

    -- Start transaction
    START TRANSACTION;

    -- Procedure logic
    INSERT INTO table_name (column1, column2)
    VALUES (p_parameter_id, p_parameter_name);

    SET p_result_id = LAST_INSERT_ID();

    -- Commit
    COMMIT;
END //

DELIMITER ;
```

### Error Handling

**ALWAYS include error handlers:**

```sql
-- Generic error handler
DECLARE EXIT HANDLER FOR SQLEXCEPTION
BEGIN
    ROLLBACK;
    RESIGNAL;
END;

-- Specific error handler
DECLARE CONTINUE HANDLER FOR 1062  -- Duplicate entry
BEGIN
    -- Handle duplicate key error
    SET v_error_message = 'Duplicate entry detected';
END;
```

## Query Optimization

### Use EXPLAIN

Before writing complex queries:

```sql
EXPLAIN SELECT * FROM large_table WHERE condition;
```

Look for:
- `type: ALL` (bad - full table scan)
- `type: index` (better - index scan)
- `type: ref` (good - index lookup)
- High `rows` count (may need index)

### Avoid N+1 Queries

❌ **BAD:**
```php
$orders = $db->query('SELECT * FROM orders')->fetchAll();
foreach ($orders as $order) {
    $customer = $db->query('SELECT * FROM customers WHERE id = ' . $order['customer_id'])->fetch();
    // N+1 queries!
}
```

✅ **GOOD:**
```php
$stmt = $db->query('
    SELECT o.*, c.customer_name
    FROM orders o
    LEFT JOIN customers c ON c.id = o.customer_id
');
$orders = $stmt->fetchAll();
// Single query!
```

### Use Indexes Effectively

```sql
-- ✅ GOOD: Uses index
SELECT * FROM inventory WHERE tenant_id = 1 AND category_id = 5;
-- Needs: INDEX idx_tenant_category (tenant_id, category_id)

-- ❌ BAD: Breaks index usage
SELECT * FROM inventory WHERE YEAR(created_at) = 2026;
-- Better: created_at BETWEEN '2026-01-01' AND '2026-12-31'
```

## Migration File Naming

**Format:** `YYYY_MM_DD_description.sql`

**Examples:**
- `2026_02_07_add_batch_tracking.sql`
- `2026_02_07_alter_inventory_add_expiry.sql`
- `2026_02_07_create_sales_returns_table.sql`

## Running Migrations

### PHP Migration Scripts

```php
<?php
// database/migrations/run_migration_2026_02_07.php
require_once __DIR__ . '/../../vendor/autoload.php';
require_once __DIR__ . '/../../bootstrap/app.php';

$db = $container->get(PDO::class);

try {
    $db->beginTransaction();

    // Run migration SQL
    $sql = file_get_contents(__DIR__ . '/2026_02_07_migration.sql');
    $db->exec($sql);

    $db->commit();
    echo "Migration successful\n";
} catch (Exception $e) {
    $db->rollBack();
    echo "Migration failed: " . $e->getMessage() . "\n";
}
```

### Direct SQL Execution

```bash
# Run migration
mysql -u root -p database_name < database/migrations/2026_02_07_migration.sql

# Verify
mysql -u root -p database_name -e "SHOW TABLES"
```

## Stored Procedures Reload

After modifying procedures:

```bash
# Reload all procedures
php database/procedures/load-procedures-pdo.php
```

## Schema Export

After any schema change:

```bash
# Export full schema (no data)
mysqldump -u root -p --no-data birdc_erp > database/schema/full_schema.sql

# Export specific table
mysqldump -u root -p --no-data birdc_erp table_name > database/schema/table_name.sql
```

## Testing Database Changes

### Test Checklist

- [ ] Migration runs without errors
- [ ] Rollback script works
- [ ] All stored procedures still execute
- [ ] All triggers still fire
- [ ] All views still query
- [ ] All API endpoints still work
- [ ] No orphaned code references
- [ ] Data integrity maintained
- [ ] Indexes are used (check EXPLAIN)
- [ ] Performance is acceptable

## Summary

**MANDATORY for all database work:**

1. **Use mysql-best-practices skill** - Always
2. **Follow migration checklist** - Every time
3. **Grep before changing** - Find all references
4. **Test before deploying** - No exceptions
5. **Document rollback** - Always have a plan
6. **Export schema after** - Keep docs updated
7. **Use proper naming** - Conventions matter
8. **Add indexes** - Performance matters
9. **Handle errors** - In procedures and migrations
10. **Verify in production** - Monitor after deploy

**Failure to follow these standards WILL cause production failures.**
