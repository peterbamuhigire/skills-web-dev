# Modular SAAS Database Schema

## Module Registry Tables

### tbl_modules
Stores metadata for all available modules in the system.

```sql
CREATE TABLE tbl_modules (
    module_code VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(20) NOT NULL,
    is_core BOOLEAN DEFAULT 0 COMMENT 'Core modules cannot be disabled',
    icon VARCHAR(100),
    author VARCHAR(255),
    min_php_version VARCHAR(10) DEFAULT '8.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_is_core (is_core)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Seed core modules
INSERT INTO tbl_modules (module_code, name, description, version, is_core) VALUES
('CORE', 'Core System', 'Essential system functionality', '1.0.0', 1),
('AUTH', 'Authentication', 'User authentication and authorization', '1.0.0', 1),
('BILLING', 'Billing System', 'Subscription and payment management', '1.0.0', 1);

-- Seed business modules
INSERT INTO tbl_modules (module_code, name, description, version, is_core, icon) VALUES
('ADV_INV', 'Advanced Inventory', 'Multi-location inventory with UOM conversions', '1.0.0', 0, 'bi-boxes'),
('RESTAURANT', 'Restaurant Management', 'Table management, orders, and kitchen display', '1.0.0', 0, 'bi-cup-hot'),
('PHARMACY', 'Pharmacy Management', 'Prescription management and drug database', '1.0.0', 0, 'bi-heart-pulse'),
('RETAIL', 'Retail POS', 'Point of sale and invoicing', '1.0.0', 0, 'bi-shop'),
('HOSPITALITY', 'Hospitality', 'Room booking and guest management', '1.0.0', 0, 'bi-building');
```

### tbl_franchise_modules
Tracks which modules are enabled for each tenant (franchise).

```sql
CREATE TABLE tbl_franchise_modules (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    franchise_id BIGINT UNSIGNED NOT NULL,
    module_code VARCHAR(50) NOT NULL,
    is_enabled BOOLEAN DEFAULT 1,
    enabled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    disabled_at TIMESTAMP NULL,
    config JSON COMMENT 'Module-specific configuration',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uk_franchise_module (franchise_id, module_code),
    FOREIGN KEY (franchise_id) REFERENCES tbl_franchises(id) ON DELETE CASCADE,
    FOREIGN KEY (module_code) REFERENCES tbl_modules(module_code) ON DELETE CASCADE,

    INDEX idx_franchise_enabled (franchise_id, is_enabled),
    INDEX idx_module (module_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### tbl_module_dependencies
Defines dependencies between modules (e.g., Restaurant requires Inventory).

```sql
CREATE TABLE tbl_module_dependencies (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    module_code VARCHAR(50) NOT NULL COMMENT 'Module that has the dependency',
    requires_module_code VARCHAR(50) NOT NULL COMMENT 'Module that is required',
    is_required BOOLEAN DEFAULT 1 COMMENT 'Hard requirement vs optional',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uk_module_dependency (module_code, requires_module_code),
    FOREIGN KEY (module_code) REFERENCES tbl_modules(module_code) ON DELETE CASCADE,
    FOREIGN KEY (requires_module_code) REFERENCES tbl_modules(module_code) ON DELETE CASCADE,

    INDEX idx_module (module_code),
    INDEX idx_requires (requires_module_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Example dependencies
INSERT INTO tbl_module_dependencies (module_code, requires_module_code, is_required) VALUES
('ADV_INV', 'CORE', 1),  -- Advanced Inventory requires Core
('RESTAURANT', 'CORE', 1),  -- Restaurant requires Core
('RESTAURANT', 'ADV_INV', 0);  -- Restaurant optionally uses Advanced Inventory
```

### tbl_module_permissions
Maps permissions to modules.

```sql
CREATE TABLE tbl_module_permissions (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    module_code VARCHAR(50) NOT NULL,
    permission_code VARCHAR(100) NOT NULL,
    permission_name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uk_module_permission (module_code, permission_code),
    FOREIGN KEY (module_code) REFERENCES tbl_modules(module_code) ON DELETE CASCADE,

    INDEX idx_module (module_code),
    INDEX idx_permission (permission_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Example permissions
INSERT INTO tbl_module_permissions (module_code, permission_code, permission_name, description) VALUES
('ADV_INV', 'VIEW_INVENTORY', 'View Inventory', 'View stock items and inventory levels'),
('ADV_INV', 'MANAGE_STOCK', 'Manage Stock', 'Create, edit, and delete stock items'),
('ADV_INV', 'APPROVE_TRANSFERS', 'Approve Transfers', 'Approve stock transfers between locations'),
('RESTAURANT', 'VIEW_ORDERS', 'View Orders', 'View restaurant orders'),
('RESTAURANT', 'MANAGE_TABLES', 'Manage Tables', 'Configure table layouts and assignments'),
('PHARMACY', 'MANAGE_PRESCRIPTIONS', 'Manage Prescriptions', 'Create and dispense prescriptions');
```

## Module Subscription & Billing Tables

### tbl_module_pricing
Defines pricing for each module.

```sql
CREATE TABLE tbl_module_pricing (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    module_code VARCHAR(50) NOT NULL,
    tier ENUM('free', 'basic', 'premium', 'enterprise') DEFAULT 'basic',
    price_monthly DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    price_yearly DECIMAL(10, 2) NULL COMMENT 'Annual pricing (discounted)',
    trial_days INT UNSIGNED DEFAULT 14,
    features_limit JSON COMMENT 'Feature limits for this tier',
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uk_module_tier (module_code, tier),
    FOREIGN KEY (module_code) REFERENCES tbl_modules(module_code) ON DELETE CASCADE,

    INDEX idx_module (module_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Example pricing
INSERT INTO tbl_module_pricing (module_code, tier, price_monthly, price_yearly, trial_days) VALUES
('ADV_INV', 'basic', 29.99, 299.90, 14),
('ADV_INV', 'premium', 59.99, 599.90, 14),
('RESTAURANT', 'basic', 49.99, 499.90, 14),
('PHARMACY', 'basic', 39.99, 399.90, 14);
```

### tbl_franchise_module_subscriptions
Tracks subscription status for each module per tenant.

```sql
CREATE TABLE tbl_franchise_module_subscriptions (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    franchise_id BIGINT UNSIGNED NOT NULL,
    module_code VARCHAR(50) NOT NULL,
    tier ENUM('free', 'basic', 'premium', 'enterprise') DEFAULT 'basic',
    status ENUM('trial', 'active', 'past_due', 'cancelled', 'expired') DEFAULT 'trial',
    trial_ends_at TIMESTAMP NULL,
    current_period_start DATE NOT NULL,
    current_period_end DATE NOT NULL,
    next_billing_date DATE,
    price_monthly DECIMAL(10, 2) NOT NULL,
    billing_cycle ENUM('monthly', 'yearly') DEFAULT 'monthly',
    auto_renew BOOLEAN DEFAULT 1,
    cancelled_at TIMESTAMP NULL,
    cancellation_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uk_franchise_module_sub (franchise_id, module_code),
    FOREIGN KEY (franchise_id) REFERENCES tbl_franchises(id) ON DELETE CASCADE,
    FOREIGN KEY (module_code) REFERENCES tbl_modules(module_code) ON DELETE CASCADE,

    INDEX idx_franchise_status (franchise_id, status),
    INDEX idx_module (module_code),
    INDEX idx_next_billing (next_billing_date),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### tbl_module_usage_logs
Tracks module usage for billing and analytics.

```sql
CREATE TABLE tbl_module_usage_logs (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    franchise_id BIGINT UNSIGNED NOT NULL,
    module_code VARCHAR(50) NOT NULL,
    feature_used VARCHAR(255),
    usage_count INT UNSIGNED DEFAULT 1,
    usage_date DATE NOT NULL,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uk_usage_log (franchise_id, module_code, feature_used, usage_date),
    FOREIGN KEY (franchise_id) REFERENCES tbl_franchises(id) ON DELETE CASCADE,
    FOREIGN KEY (module_code) REFERENCES tbl_modules(module_code) ON DELETE CASCADE,

    INDEX idx_franchise_date (franchise_id, usage_date),
    INDEX idx_module_date (module_code, usage_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## Audit Tables for Module Management

### tbl_module_audit_log
Tracks all module enable/disable actions.

```sql
CREATE TABLE tbl_module_audit_log (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    franchise_id BIGINT UNSIGNED NOT NULL,
    module_code VARCHAR(50) NOT NULL,
    action ENUM('enabled', 'disabled', 'upgraded', 'downgraded', 'cancelled') NOT NULL,
    performed_by BIGINT UNSIGNED NOT NULL COMMENT 'User ID who performed action',
    reason TEXT,
    metadata JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (franchise_id) REFERENCES tbl_franchises(id) ON DELETE CASCADE,
    FOREIGN KEY (module_code) REFERENCES tbl_modules(module_code) ON DELETE CASCADE,
    FOREIGN KEY (performed_by) REFERENCES tbl_users(id) ON DELETE CASCADE,

    INDEX idx_franchise (franchise_id),
    INDEX idx_module (module_code),
    INDEX idx_action (action),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## Example Module Tables

### Advanced Inventory Module Tables

```sql
-- Stock Items (owned by Advanced Inventory module)
CREATE TABLE tbl_stock_items (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    franchise_id BIGINT UNSIGNED NOT NULL,
    code VARCHAR(100),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category_id BIGINT UNSIGNED,
    unit_id BIGINT UNSIGNED NOT NULL COMMENT 'Base unit',
    cost_price DECIMAL(15, 2) DEFAULT 0.00,
    reorder_level DECIMAL(15, 4) DEFAULT 0.0000,
    image_path VARCHAR(255),
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uk_franchise_code (franchise_id, code),
    FOREIGN KEY (franchise_id) REFERENCES tbl_franchises(id) ON DELETE CASCADE,

    INDEX idx_franchise_active (franchise_id, is_active),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- UOM Conversions (owned by Advanced Inventory module)
CREATE TABLE tbl_stock_item_uoms (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    stock_item_id BIGINT UNSIGNED NOT NULL,
    unit_id BIGINT UNSIGNED NOT NULL,
    conversion_factor DECIMAL(15, 6) NOT NULL DEFAULT 1.000000,
    is_default BOOLEAN DEFAULT 0 COMMENT 'Base unit for this stock item',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uk_stock_item_unit (stock_item_id, unit_id),
    FOREIGN KEY (stock_item_id) REFERENCES tbl_stock_items(id) ON DELETE CASCADE,

    INDEX idx_stock_item (stock_item_id),
    INDEX idx_is_default (is_default)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Restaurant Module Tables

```sql
-- Restaurant Tables (owned by Restaurant module)
CREATE TABLE tbl_restaurant_tables (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    franchise_id BIGINT UNSIGNED NOT NULL,
    branch_id BIGINT UNSIGNED,
    table_number VARCHAR(50) NOT NULL,
    capacity INT UNSIGNED DEFAULT 4,
    status ENUM('available', 'occupied', 'reserved', 'maintenance') DEFAULT 'available',
    location VARCHAR(100) COMMENT 'Indoor, outdoor, etc.',
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY uk_franchise_table (franchise_id, branch_id, table_number),
    FOREIGN KEY (franchise_id) REFERENCES tbl_franchises(id) ON DELETE CASCADE,

    INDEX idx_franchise_status (franchise_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## Helper Views

### vw_franchise_enabled_modules
Convenient view to see all enabled modules per tenant.

```sql
CREATE OR REPLACE VIEW vw_franchise_enabled_modules AS
SELECT
    fm.franchise_id,
    f.name AS franchise_name,
    m.module_code,
    m.name AS module_name,
    m.description,
    m.version,
    m.is_core,
    fm.is_enabled,
    fm.enabled_at,
    fms.status AS subscription_status,
    fms.tier,
    fms.trial_ends_at,
    fms.next_billing_date
FROM tbl_franchise_modules fm
JOIN tbl_franchises f ON fm.franchise_id = f.id
JOIN tbl_modules m ON fm.module_code = m.module_code
LEFT JOIN tbl_franchise_module_subscriptions fms
    ON fm.franchise_id = fms.franchise_id AND fm.module_code = fms.module_code
WHERE fm.is_enabled = 1;
```

### vw_module_revenue
View for reporting module revenue.

```sql
CREATE OR REPLACE VIEW vw_module_revenue AS
SELECT
    m.module_code,
    m.name AS module_name,
    COUNT(DISTINCT fms.franchise_id) AS active_subscriptions,
    SUM(fms.price_monthly) AS monthly_revenue,
    fms.tier
FROM tbl_modules m
LEFT JOIN tbl_franchise_module_subscriptions fms
    ON m.module_code = fms.module_code
WHERE fms.status = 'active'
GROUP BY m.module_code, m.name, fms.tier;
```

## Database Migration Notes

### Adding Module Support to Existing System

1. **Create module registry tables** (run once)
2. **Migrate existing tenants** (enable relevant modules based on current usage)
3. **No data migration needed** (existing tables stay as-is)
4. **Add module checks to pages** (wrap pages with `requireModuleAccess()`)

### Example Migration Script

```sql
-- Step 1: Create module tables (see above)

-- Step 2: Enable relevant modules for existing franchises
INSERT INTO tbl_franchise_modules (franchise_id, module_code, is_enabled)
SELECT id, 'CORE', 1 FROM tbl_franchises;  -- Enable Core for all

INSERT INTO tbl_franchise_modules (franchise_id, module_code, is_enabled)
SELECT id, 'ADV_INV', 1 FROM tbl_franchises
WHERE id IN (SELECT DISTINCT franchise_id FROM tbl_stock_items);  -- Enable Adv Inv if they have stock items

-- Step 3: Create trial subscriptions
INSERT INTO tbl_franchise_module_subscriptions
    (franchise_id, module_code, tier, status, trial_ends_at, current_period_start, current_period_end, price_monthly)
SELECT
    fm.franchise_id,
    fm.module_code,
    'basic',
    'trial',
    DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 14 DAY),
    CURDATE(),
    DATE_ADD(CURDATE(), INTERVAL 1 MONTH),
    mp.price_monthly
FROM tbl_franchise_modules fm
JOIN tbl_module_pricing mp ON fm.module_code = mp.module_code AND mp.tier = 'basic'
WHERE fm.is_enabled = 1 AND fm.module_code != 'CORE';
```

## Indexes for Performance

### Critical Indexes

```sql
-- Fast module access checks
CREATE INDEX idx_franchise_module_enabled ON tbl_franchise_modules(franchise_id, module_code, is_enabled);

-- Fast permission checks
CREATE INDEX idx_module_permission ON tbl_module_permissions(module_code, permission_code);

-- Fast billing queries
CREATE INDEX idx_subscription_next_billing ON tbl_franchise_module_subscriptions(status, next_billing_date);

-- Fast analytics queries
CREATE INDEX idx_usage_franchise_date ON tbl_module_usage_logs(franchise_id, module_code, usage_date);
```

## Data Retention Policies

- **Module audit logs**: Retain 7 years (compliance)
- **Usage logs**: Retain 2 years (analytics)
- **Subscription history**: Retain indefinitely (legal)
- **Disabled module data**: Retain 90 days after disable, then archive
