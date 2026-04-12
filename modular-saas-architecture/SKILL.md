---
name: modular-saas-architecture
description: Build SAAS platforms with pluggable business modules (Advanced Inventory, Restaurant, Pharmacy, etc.) that can be enabled/disabled per tenant without breaking the system. Use when designing modular SAAS features, implementing module toggles...
---

# Modular SAAS Architecture

## Load Alongside

- `world-class-engineering` for release gates and output standards.
- `saas-erp-system-design` when modules encode significant business workflows.
- `database-design-engineering` for schema ownership, tenancy, and migration safety.
- `vibe-security-skill` for security review.

## Overview

Architecture pattern for building SaaS platforms where business modules (Advanced Inventory, Restaurant, Pharmacy, Retail, etc.) can be independently enabled, disabled, or added without affecting other parts of the system.

**Core Principles:**
- **Module Independence**: Each module is self-contained with minimal dependencies
- **Graceful Degradation**: Disabling a module doesn't break dependent features
- **Per-Tenant Control**: Each tenant can enable only the modules they need
- **Zero Breaking Changes**: Adding/removing modules preserves existing functionality

**Security Baseline (Required):** Always load and apply the **Vibe Security Skill** for any web app, API, or module implementation work.

📖 **See `references/implementation.md`** for full lifecycle code, testing patterns, and anti-patterns.

## When to Use

✅ Multi-tenant SaaS platforms with diverse customer needs
✅ Systems serving different industries (retail, healthcare, hospitality)
✅ Platforms with optional premium features
❌ Single-tenant applications or tightly coupled monolithic systems

## Module Architecture Pattern

```
┌─────────────────────────────────────────────────┐
│                CORE SYSTEM                       │
│  Authentication, Multi-tenant, Users, Billing,   │
│  Audit Logs, Module Registry & Feature Flags     │
└───────────────────┬─────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ 🏪 Retail│  │🍽️ Restaurant│  │💊 Pharmacy│
│ POS Sales│  │Table Mgmt │  │Rx Mgmt   │
│ Inventory│  │Orders     │  │Drug DB   │
│ Invoicing│  │Kitchen    │  │Scripts   │
└──────────┘  └──────────┘  └──────────┘

Per-Tenant Config:
  Tenant A: Retail + Adv. Inventory (enabled)
  Tenant B: Restaurant + Hospitality (enabled)
  Tenant C: Pharmacy only (enabled)
```

## Module Anatomy

```
modules/
└── advanced-inventory/
    ├── module.config.php    # Module metadata, features, permissions, menu
    ├── permissions.php
    ├── routes.php
    ├── database/
    │   └── schema.sql       # Module tables (all franchise-scoped)
    ├── services/            # Business logic
    ├── models/
    └── tests/
```

## Module Configuration

```php
// modules/advanced-inventory/module.config.php
return [
    'module_code' => 'ADV_INV',
    'name'        => 'Advanced Inventory',
    'description' => 'Multi-location inventory with UOM conversions and transfers',
    'version'     => '1.0.0',
    'requires'    => [],           // Empty = no dependencies
    'features'    => ['stock_items', 'uom_conversions', 'stock_transfers'],
    'permissions' => ['VIEW_INVENTORY', 'MANAGE_STOCK', 'APPROVE_TRANSFERS'],
    'tables'      => ['tbl_stock_items', 'tbl_stock_item_uoms', 'tbl_stock_transfers'],
    'menu'        => [
        ['label' => 'Inventory', 'icon' => 'bi-boxes', 'items' => [
            ['label' => 'Stock Items', 'url' => '/stock-items-catalog.php'],
            ['label' => 'UOM Conversions', 'url' => '/advanced-inventory-uom.php'],
            ['label' => 'Stock Transfers', 'url' => '/stock-transfers.php'],
        ]]
    ],
    'pricing' => ['type' => 'addon', 'price_monthly' => 29.99, 'trial_days' => 14],
];
```

## Module Registry & Access Control

```php
class ModuleRegistry {
    public function getEnabledModules(int $franchiseId): array {
        $stmt = $this->db->prepare('
            SELECT module_code, config FROM tbl_franchise_modules
            WHERE franchise_id = ? AND is_enabled = 1
        ');
        $stmt->execute([$franchiseId]);
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function isModuleEnabled(int $franchiseId, string $moduleCode): bool {
        $stmt = $this->db->prepare('
            SELECT is_enabled FROM tbl_franchise_modules
            WHERE franchise_id = ? AND module_code = ?
        ');
        $stmt->execute([$franchiseId, $moduleCode]);
        return (bool) $stmt->fetchColumn();
    }
}

// Blocking check — redirects if module disabled
function requireModuleAccess(string $moduleCode): void {
    if (!isLoggedIn()) { header('Location: ./sign-in.php'); exit(); }
    $stmt = $this->db->prepare('SELECT is_enabled FROM tbl_franchise_modules WHERE franchise_id = ? AND module_code = ?');
    $stmt->execute([$_SESSION['franchise_id'], $moduleCode]);
    if (!$stmt->fetchColumn()) {
        header('Location: ./module-not-available.php?module=' . urlencode($moduleCode)); exit();
    }
}

// Non-blocking check — for conditional UI
function hasModuleAccess(string $moduleCode): bool {
    if (!isLoggedIn()) return false;
    $stmt = $this->db->prepare('SELECT is_enabled FROM tbl_franchise_modules WHERE franchise_id = ? AND module_code = ?');
    $stmt->execute([$_SESSION['franchise_id'], $moduleCode]);
    return (bool) $stmt->fetchColumn();
}
```

## Page-Level Protection

```php
// On every module page — at the top, before any output
requireModuleAccess('ADV_INV');
requirePermissionGlobal('VIEW_INVENTORY');
```

## Module Independence Patterns

### Pattern 1: Optional Dependencies

```php
// Check before using an optional module
class OrderService {
    public function createOrder(array $data) {
        $order = $this->saveOrder($data);
        // Use Advanced Inventory if enabled, else fallback
        if (hasModuleAccess('ADV_INV')) {
            (new AdvancedInventoryService())->updateInventory($order);
        } else {
            $this->updateBasicStock($order);
        }
    }
}
```

### Pattern 2: Interface-Based Integration

```php
interface InventoryProvider {
    public function checkStock(int $itemId, float $qty): bool;
    public function decrementStock(int $itemId, float $qty): void;
}

class InventoryFactory {
    public static function create(): InventoryProvider {
        return hasModuleAccess('ADV_INV')
            ? new AdvancedInventory()
            : new BasicInventory();
    }
}
```

### Pattern 3: Event-Driven Communication

```php
// Module A fires event — Module B optionally listens
class SalesModule {
    public function completeSale(Sale $sale) {
        $this->saveSale($sale);
        EventDispatcher::dispatch('sale.completed', ['sale' => $sale]);
    }
}

// modules/advanced-inventory/bootstrap.php
if (hasModuleAccess('ADV_INV')) {
    EventDispatcher::listen('sale.completed', function($data) {
        (new InventoryService())->decrementStock($data['sale']);
    });
}
```

## Database Design

```sql
-- Module registry tables (core — always present)
CREATE TABLE tbl_modules (
    module_code VARCHAR(50) PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    is_core     BOOLEAN DEFAULT 0
);

CREATE TABLE tbl_franchise_modules (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    franchise_id BIGINT NOT NULL,
    module_code  VARCHAR(50) NOT NULL,
    is_enabled   BOOLEAN DEFAULT 1,
    enabled_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    disabled_at  TIMESTAMP NULL,
    config       JSON,
    UNIQUE KEY (franchise_id, module_code),
    FOREIGN KEY (franchise_id) REFERENCES tbl_franchises(id),
    FOREIGN KEY (module_code)  REFERENCES tbl_modules(module_code)
);

-- Module tables: always include franchise_id for tenant isolation
CREATE TABLE tbl_stock_items (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    franchise_id BIGINT NOT NULL,
    name         VARCHAR(255) NOT NULL,
    FOREIGN KEY (franchise_id) REFERENCES tbl_franchises(id)
);

-- Cross-module FK: use NULL + application-level check (no hard FK to optional module)
CREATE TABLE tbl_sales (
    id                  BIGINT AUTO_INCREMENT PRIMARY KEY,
    franchise_id        BIGINT NOT NULL,
    restaurant_table_id BIGINT NULL           -- Nullable! No FK to optional module table
);
```

## Dynamic Navigation

```php
// Menu constraints: max 5 submenus, max 6 items each, Bootstrap Icons on all entries
<nav>
    <a href="/dashboard.php">Dashboard</a>
    <?php if (hasModuleAccess('RETAIL')): ?>
        <a href="/pos-sales.php">POS</a>
    <?php endif; ?>
    <?php if (hasModuleAccess('ADV_INV')): ?>
        <div class="dropdown"><a href="#">Inventory</a>
            <ul>
                <li><a href="/stock-items-catalog.php">Stock Items</a></li>
                <li><a href="/advanced-inventory-uom.php">UOM Conversions</a></li>
            </ul>
        </div>
    <?php endif; ?>
</nav>
```

## Module Lifecycle (Summary)

```php
// Enable: validate dependencies → run migrations → insert row → create trial subscription → audit log
// Disable: check dependents → UPDATE is_enabled=0 → cancel subscription → audit log
// NEVER delete module data on disable — user may re-enable
UPDATE tbl_franchise_modules SET is_enabled = 0, disabled_at = NOW() WHERE franchise_id = ? AND module_code = ?;
```

## Best Practices

**DO:**
- Keep modules self-contained (own tables, own logic)
- Always include `franchise_id` in module tables
- Use `hasModuleAccess()` for optional dependencies
- Keep data when module is disabled (soft disable only)
- Use nullable FKs for cross-module references
- Define audit events for enable, disable, pricing, and role-sensitive actions

**DON'T:**
- Hard-code module dependencies (check at runtime)
- Delete data when module is disabled
- Share tables between modules
- Use hard FK constraints for optional modules
- Show disabled module navigation to users
- Fork module behavior per tenant in code when configuration or policy can express it

## Implementation Checklist

- [ ] Module config file with metadata, features, permissions, menu
- [ ] `requireModuleAccess()` on every module page
- [ ] `hasModuleAccess()` for optional dependency checks
- [ ] Module registry in database (`tbl_franchise_modules`)
- [ ] Trial/subscription billing rows on enable
- [ ] Dynamic navigation using `hasModuleAccess()`
- [ ] Fallback logic when optional modules disabled
- [ ] Audit log for enable/disable events
- [ ] Isolation tests + integration tests

📖 See `references/implementation.md` for full lifecycle code, testing patterns, anti-patterns.
