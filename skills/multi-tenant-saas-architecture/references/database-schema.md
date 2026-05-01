# Database Schema Reference

## Core Tables

### Tenants

```sql
CREATE TABLE tenants (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    slug VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    status ENUM('PENDING', 'ACTIVE', 'SUSPENDED', 'ARCHIVED') NOT NULL DEFAULT 'PENDING',
    settings JSON,
    subscription_tier VARCHAR(50),
    subscription_expires_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_status (status),
    INDEX idx_slug (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Users

```sql
CREATE TABLE users (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    tenant_id BIGINT UNSIGNED NULL COMMENT 'NULL for super_admin',
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type ENUM('super_admin', 'tenant_owner', 'tenant_manager', 'tenant_staff', 'customer') NOT NULL,
    status ENUM('active', 'inactive', 'locked', 'pending') NOT NULL DEFAULT 'pending',
    failed_login_attempts SMALLINT UNSIGNED DEFAULT 0,
    last_login DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uk_email_tenant (email, tenant_id),
    INDEX idx_tenant_status (tenant_id, status),
    INDEX idx_user_type (user_type),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Audit Logs

```sql
CREATE TABLE audit_logs (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    tenant_id BIGINT UNSIGNED NULL COMMENT 'NULL for platform-level actions',
    actor_user_id BIGINT UNSIGNED NOT NULL,
    actor_type VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    target_type VARCHAR(50),
    target_id BIGINT UNSIGNED,
    justification TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_tenant_created (tenant_id, created_at),
    INDEX idx_actor (actor_user_id, created_at),
    INDEX idx_action (action, created_at),
    FOREIGN KEY (actor_user_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## Tenant-Scoped Tables Pattern

**Every business entity table follows this pattern:**

```sql
CREATE TABLE orders (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    tenant_id BIGINT UNSIGNED NOT NULL,
    order_number VARCHAR(50) NOT NULL,
    customer_id BIGINT UNSIGNED NOT NULL,
    status ENUM('pending', 'confirmed', 'shipped', 'delivered', 'cancelled') NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uk_order_number_tenant (order_number, tenant_id),
    INDEX idx_tenant_status (tenant_id, status),
    INDEX idx_tenant_created (tenant_id, created_at),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Key patterns:**
- `tenant_id BIGINT UNSIGNED NOT NULL` on every table
- Composite unique keys include `tenant_id`
- Indexes start with `tenant_id` for query performance
- Foreign key ON DELETE CASCADE for tenant cleanup

## Indexes for Multi-Tenant Queries

```sql
-- PRIMARY pattern: (tenant_id, other_columns)
CREATE INDEX idx_tenant_status ON orders(tenant_id, status);
CREATE INDEX idx_tenant_created ON orders(tenant_id, created_at);
CREATE INDEX idx_tenant_customer ON orders(tenant_id, customer_id);

-- For queries: WHERE tenant_id = ? AND status = ?
-- Index is used efficiently

-- WRONG: (status, tenant_id) - Less efficient for multi-tenant
CREATE INDEX idx_status_tenant ON orders(status, tenant_id);
```

## Composite Primary Keys (Alternative Pattern)

```sql
-- Instead of AUTO_INCREMENT, use composite PK
CREATE TABLE order_items (
    tenant_id BIGINT UNSIGNED NOT NULL,
    order_id BIGINT UNSIGNED NOT NULL,
    item_id BIGINT UNSIGNED NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,

    PRIMARY KEY (tenant_id, order_id, item_id),
    FOREIGN KEY (tenant_id, order_id) REFERENCES orders(tenant_id, id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Advantage:** Enforces tenant isolation at PK level
**Disadvantage:** More complex foreign keys

## Data Types Best Practices

```sql
-- IDs: BIGINT UNSIGNED (never run out)
id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT

-- Slugs/Codes: VARCHAR with reasonable limits
slug VARCHAR(100)
code VARCHAR(50)

-- Money: DECIMAL (exact precision)
amount DECIMAL(10,2)  -- Up to 99,999,999.99

-- Booleans: BOOLEAN or TINYINT(1)
is_active BOOLEAN DEFAULT TRUE

-- Timestamps: TIMESTAMP (UTC storage)
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

-- JSON: JSON type (MySQL 5.7.8+)
metadata JSON

-- Enums: ENUM (predefined values)
status ENUM('active', 'inactive')
```

## Partitioning for Scale

**For very large tables (100M+ rows), partition by tenant_id:**

```sql
CREATE TABLE large_analytics_table (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    tenant_id BIGINT UNSIGNED NOT NULL,
    event_type VARCHAR(50),
    data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_tenant_created (tenant_id, created_at)
) ENGINE=InnoDB
PARTITION BY HASH(tenant_id)
PARTITIONS 16;
```

**Benefit:** Queries filtering by tenant_id only scan relevant partition

## Common Schema Mistakes

❌ **Missing tenant_id**
```sql
CREATE TABLE products (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255)
    -- Missing tenant_id!
);
```

❌ **tenant_id nullable**
```sql
tenant_id BIGINT NULL  -- Should be NOT NULL
```

❌ **Wrong index order**
```sql
CREATE INDEX idx_status_tenant ON orders(status, tenant_id);
-- Should be: (tenant_id, status)
```

❌ **No CASCADE on tenant FK**
```sql
FOREIGN KEY (tenant_id) REFERENCES tenants(id);
-- Missing: ON DELETE CASCADE
```

✅ **Correct pattern**
```sql
CREATE TABLE products (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    tenant_id BIGINT UNSIGNED NOT NULL,
    name VARCHAR(255) NOT NULL,

    INDEX idx_tenant (tenant_id),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);
```
