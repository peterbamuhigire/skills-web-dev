# Migration Patterns for Multi-Tenant SaaS

## Adding tenant_id to Existing Tables

### Safe Migration Process

```sql
-- Step 1: Add column (nullable, no default)
ALTER TABLE orders ADD COLUMN tenant_id BIGINT NULL;

-- Step 2: Backfill data from related table
UPDATE orders SET tenant_id = (
  SELECT tenant_id FROM users WHERE users.id = orders.user_id
);

-- Step 3: Verify no NULLs remain
SELECT COUNT(*) FROM orders WHERE tenant_id IS NULL;
-- Must return 0 before proceeding

-- Step 4: Make NOT NULL
ALTER TABLE orders MODIFY tenant_id BIGINT NOT NULL;

-- Step 5: Add index (critical for performance)
CREATE INDEX idx_orders_tenant ON orders(tenant_id);

-- Step 6: Add foreign key constraint
ALTER TABLE orders
  ADD CONSTRAINT fk_orders_tenant
  FOREIGN KEY (tenant_id) REFERENCES tenants(id)
  ON DELETE CASCADE;
```

### Zero-Downtime Migration (Large Tables)

For tables with millions of rows:

```sql
-- Step 1: Add column with default (uses metadata-only change in MySQL 8.0.13+)
ALTER TABLE large_table ADD COLUMN tenant_id BIGINT NULL;

-- Step 2: Batch backfill (avoid locking entire table)
DO $$
DECLARE
    batch_size INT := 1000;
    last_id BIGINT := 0;
BEGIN
    LOOP
        UPDATE large_table
        SET tenant_id = (
            SELECT tenant_id FROM users WHERE users.id = large_table.user_id
        )
        WHERE id > last_id AND id <= last_id + batch_size
          AND tenant_id IS NULL;

        EXIT WHEN NOT FOUND;
        last_id := last_id + batch_size;
        COMMIT; -- Release locks between batches
        PERFORM pg_sleep(0.1); -- Throttle to avoid overwhelming DB
    END LOOP;
END $$;

-- Step 3-6: Same as above
```

### Application Code Migration

**Before (no tenant isolation):**
```javascript
// ❌ Dangerous: No tenant filter
const order = await db.orders.findOne({id: orderId});
```

**After (tenant-scoped):**
```javascript
// ✅ Safe: Tenant context required
const order = await db.orders.findOne({
  id: orderId,
  tenant_id: req.user.tenant_id
});
```

### Migration Verification

**Test checklist:**
1. All tables have tenant_id column
2. All queries include tenant_id filter
3. Cross-tenant access returns 404 (not 403)
4. Foreign keys cascade properly
5. Indexes exist on tenant_id
6. No NULL tenant_id values

**Query to find missing tenant_id columns:**
```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'your_db'
  AND table_type = 'BASE TABLE'
  AND table_name NOT IN (
    SELECT table_name
    FROM information_schema.columns
    WHERE column_name = 'tenant_id'
  )
  AND table_name NOT IN ('tenants', 'migrations', 'system_tables');
```

## Migrating from Single-Tenant to Multi-Tenant

### Phase 1: Add Tenant Model

```sql
CREATE TABLE tenants (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    slug VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    status ENUM('PENDING', 'ACTIVE', 'SUSPENDED', 'ARCHIVED') DEFAULT 'ACTIVE',
    settings JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create first tenant for existing data
INSERT INTO tenants (slug, name, status) VALUES ('default', 'Default Tenant', 'ACTIVE');
```

### Phase 2: Add tenant_id to Users

```sql
ALTER TABLE users ADD COLUMN tenant_id BIGINT NULL;

-- Assign all existing users to default tenant
UPDATE users SET tenant_id = (SELECT id FROM tenants WHERE slug = 'default');

ALTER TABLE users MODIFY tenant_id BIGINT NOT NULL;
CREATE INDEX idx_users_tenant ON users(tenant_id);
ALTER TABLE users ADD FOREIGN KEY (tenant_id) REFERENCES tenants(id);
```

### Phase 3: Cascade to All Tables

Repeat migration process for each table that needs tenant isolation.

**Dependency order:**
```
1. Core entities (users, roles)
2. Transactional data (orders, invoices)
3. Reference data (products, categories)
4. Audit/logs (optional, can be global)
```

### Phase 4: Update Application Code

**Add tenant middleware:**
```javascript
app.use((req, res, next) => {
  if (!req.user?.tenant_id) {
    return res.status(401).json({error: 'Missing tenant context'});
  }
  req.tenantId = req.user.tenant_id;
  next();
});
```

**Update query builder:**
```javascript
class TenantRepository {
  constructor(tenantId) {
    this.tenantId = tenantId;
  }

  find(conditions) {
    return db.query({
      ...conditions,
      tenant_id: this.tenantId  // Always inject
    });
  }
}
```

### Phase 5: Testing Migration

**Critical tests:**
```javascript
describe('Tenant Isolation', () => {
  it('prevents cross-tenant data access', async () => {
    const tenant1Order = await createOrder(tenant1);
    const tenant2User = authenticate(tenant2.user);

    const response = await tenant2User.get(`/orders/${tenant1Order.id}`);
    expect(response.status).toBe(404); // Not found (not 403)
  });

  it('requires tenant context', async () => {
    const userWithoutTenant = {id: 123}; // No tenant_id
    expect(() => getOrders(userWithoutTenant)).toThrow('Missing tenant context');
  });
});
```

## Rolling Back Migrations

**Emergency rollback procedure:**

```sql
-- 1. Remove foreign key
ALTER TABLE orders DROP FOREIGN KEY fk_orders_tenant;

-- 2. Remove index
DROP INDEX idx_orders_tenant ON orders;

-- 3. Drop column
ALTER TABLE orders DROP COLUMN tenant_id;

-- 4. Restore from backup if data corruption
-- (Always test rollback in staging first!)
```

**Safer: Feature flag rollback**

Instead of dropping columns, use application-level feature flags:

```javascript
const ENABLE_TENANT_ISOLATION = process.env.ENABLE_TENANT_ISOLATION === 'true';

function scopeQuery(query, user) {
  if (ENABLE_TENANT_ISOLATION && user.tenant_id) {
    return query.where('tenant_id', user.tenant_id);
  }
  return query; // Old behavior
}
```

## Common Migration Mistakes

❌ **Forgetting to verify no NULLs before making column NOT NULL**
```sql
ALTER TABLE orders MODIFY tenant_id BIGINT NOT NULL;
-- Error: Column contains NULL values!
```

❌ **Not adding indexes**
```sql
-- Missing index = slow queries
SELECT * FROM orders WHERE tenant_id = 123; -- Full table scan!
```

❌ **Trusting client-provided tenant_id during migration**
```javascript
// ❌ Client could fake tenant_id
const tenantId = req.body.tenant_id;

// ✅ Always from auth token
const tenantId = req.user.tenant_id;
```

❌ **Migrating all tables at once**
```
// BAD: Big bang migration
Migrate 50 tables overnight → High risk

// GOOD: Gradual rollout
Migrate 5 tables per week → Low risk, easier rollback
```
