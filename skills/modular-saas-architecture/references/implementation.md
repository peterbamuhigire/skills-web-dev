# Modular SaaS — Full Implementation Reference

## Module Lifecycle Management

### Enabling a Module

```php
public function enableModule(int $franchiseId, string $moduleCode): array {
    $moduleConfig = $this->moduleRegistry->getModule($moduleCode);
    if (!$moduleConfig) return ['success' => false, 'message' => 'Module not found'];

    // Check dependencies
    foreach ($moduleConfig['requires'] as $requiredModule) {
        if (!$this->isModuleEnabled($franchiseId, $requiredModule)) {
            return ['success' => false, 'message' => "Requires {$requiredModule} module first"];
        }
    }

    $this->runModuleMigrations($moduleCode);

    $stmt = $this->db->prepare('
        INSERT INTO tbl_franchise_modules (franchise_id, module_code, is_enabled)
        VALUES (?, ?, 1)
        ON DUPLICATE KEY UPDATE is_enabled = 1, enabled_at = CURRENT_TIMESTAMP
    ');
    $stmt->execute([$franchiseId, $moduleCode]);

    $this->createTrialSubscription($franchiseId, $moduleCode);
    auditLog('MODULE_ENABLED', ['franchise_id' => $franchiseId, 'module_code' => $moduleCode]);
    return ['success' => true, 'message' => 'Module enabled'];
}
```

### Disabling a Module

```php
public function disableModule(int $franchiseId, string $moduleCode): array {
    $dependentModules = $this->getDependentModules($franchiseId, $moduleCode);
    if (!empty($dependentModules)) {
        return ['success' => false, 'message' => 'Required by: ' . implode(', ', $dependentModules)];
    }

    // Disable access only — NEVER delete data
    $stmt = $this->db->prepare('
        UPDATE tbl_franchise_modules
        SET is_enabled = 0, disabled_at = CURRENT_TIMESTAMP
        WHERE franchise_id = ? AND module_code = ?
    ');
    $stmt->execute([$franchiseId, $moduleCode]);
    $this->cancelSubscription($franchiseId, $moduleCode);
    auditLog('MODULE_DISABLED', ['franchise_id' => $franchiseId, 'module_code' => $moduleCode]);
    return ['success' => true, 'message' => 'Module disabled'];
}
```

### Module Subscriptions

```sql
CREATE TABLE tbl_franchise_module_subscriptions (
    id                BIGINT AUTO_INCREMENT PRIMARY KEY,
    franchise_id      BIGINT NOT NULL,
    module_code       VARCHAR(50) NOT NULL,
    status            ENUM('trial','active','cancelled','expired') DEFAULT 'trial',
    trial_ends_at     TIMESTAMP NULL,
    next_billing_date DATE,
    price_monthly     DECIMAL(10,2),
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (franchise_id) REFERENCES tbl_franchises(id),
    FOREIGN KEY (module_code)  REFERENCES tbl_modules(module_code)
);
```

---

## Module Marketplace UI

```php
// modules-marketplace.php
requirePermissionGlobal('MANAGE_BILLING');
$availableModules = getAvailableModules();
$enabledModules = getEnabledModules($_SESSION['franchise_id']);
?>
<h2>Available Modules</h2>
<?php foreach ($availableModules as $code => $module):
    $isEnabled = in_array($code, array_column($enabledModules, 'module_code')); ?>
    <div class="module-card <?= $isEnabled ? 'enabled' : '' ?>">
        <i class="<?= $module['icon'] ?>"></i>
        <h3><?= $module['name'] ?></h3>
        <p><?= $module['description'] ?></p>
        <?php if ($module['pricing']['type'] === 'core'): ?>
            <span class="badge bg-blue">Included</span>
        <?php else: ?>
            <p class="price">$<?= $module['pricing']['price_monthly'] ?>/month</p>
        <?php endif; ?>
        <?php if (!$isEnabled): ?>
            <button onclick="enableModule('<?= $code ?>')">
                Enable (<?= $module['pricing']['trial_days'] ?> day trial)
            </button>
        <?php else: ?>
            <button disabled>Enabled</button>
            <button onclick="disableModule('<?= $code ?>')" class="btn-danger">Disable</button>
        <?php endif; ?>
    </div>
<?php endforeach; ?>
```

---

## Testing Patterns

### Module Isolation Test

```php
class AdvancedInventoryModuleTest extends TestCase {
    public function testModuleWorksIndependently() {
        $this->enableModule('ADV_INV');
        $this->disableModule('RESTAURANT');
        $stockItem = $this->createStockItem(['name' => 'Test Item']);
        $this->assertNotNull($stockItem);
    }

    public function testModuleAccessControl() {
        $this->disableModule('ADV_INV');
        $response = $this->get('/advanced-inventory-uom.php');
        $this->assertRedirect('/module-not-available.php');
    }

    public function testDataPreservedAfterDisable() {
        $this->enableModule('ADV_INV');
        $item = $this->createStockItem(['name' => 'Tomato']);
        $this->disableModule('ADV_INV');
        $this->enableModule('ADV_INV');
        $this->assertDatabaseHas('tbl_stock_items', ['id' => $item->id]);
    }
}
```

### Cross-Module Integration Test

```php
public function testRestaurantWithInventoryIntegration() {
    $this->enableModule('RESTAURANT');
    $this->enableModule('ADV_INV');
    $stockItem = $this->createStockItem(['name' => 'Tomato', 'quantity' => 10]);
    $order = $this->createRestaurantOrder(['items' => [['stock_item_id' => $stockItem->id, 'qty' => 2]]]);
    $this->assertEquals(8, $this->getStockQuantity($stockItem->id));
}

public function testRestaurantWithoutInventory() {
    $this->enableModule('RESTAURANT');
    $this->disableModule('ADV_INV');
    $order = $this->createRestaurantOrder(['items' => [['product_id' => 1, 'qty' => 2]]]);
    $this->assertNotNull($order);  // Should use basic inventory fallback
}
```

---

## Anti-Patterns

### ❌ Hard Dependencies (crashes when module disabled)

```php
// BAD
class RestaurantOrderService {
    public function createOrder($data) {
        $inventory = new AdvancedInventoryService(); // Crashes if ADV_INV disabled!
        $inventory->decrementStock($data['items']);
    }
}

// GOOD
class RestaurantOrderService {
    public function createOrder($data) {
        if (hasModuleAccess('ADV_INV')) {
            (new AdvancedInventoryService())->decrementStock($data['items']);
        } else {
            $this->decrementBasicStock($data['items']);
        }
    }
}
```

### ❌ Circular Dependencies (use events instead)

```php
// BAD: Module A depends on B, Module B depends on A
// GOOD: Use EventDispatcher — modules fire events, others listen optionally

// Module A fires:
EventDispatcher::dispatch('order.created', $order);

// Module B listens (only if enabled):
if (hasModuleAccess('ADV_INV')) {
    EventDispatcher::listen('order.created', fn($data) => (new InventoryService())->decrementStock($data));
}
```

### ❌ Deleting data on disable

```php
// BAD: User loses all data permanently
DELETE FROM tbl_stock_items WHERE franchise_id = $franchiseId;

// GOOD: Soft disable — data preserved for re-enable
UPDATE tbl_franchise_modules SET is_enabled = 0 WHERE franchise_id = ? AND module_code = ?;
```

### ❌ Hard FK constraints for optional modules

```sql
-- BAD: Breaks if Restaurant module not installed
ALTER TABLE tbl_sales ADD FOREIGN KEY (restaurant_table_id) REFERENCES tbl_restaurant_tables(id);

-- GOOD: Nullable column, validate at application level
restaurant_table_id BIGINT NULL  -- check at app layer: if (hasModuleAccess('RESTAURANT') && $tableId)
```
