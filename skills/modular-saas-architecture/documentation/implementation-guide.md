# Modular SAAS Implementation Guide

## Step-by-Step Implementation

### Phase 1: Core Infrastructure Setup

#### 1.1 Create Module Registry Database

```bash
# Run migration
mysql -u root -p maduuka_db < migrations/001_create_module_tables.sql
```

```sql
-- migrations/001_create_module_tables.sql
-- See references/database-schema.md for complete schema
CREATE TABLE tbl_modules (...);
CREATE TABLE tbl_franchise_modules (...);
CREATE TABLE tbl_module_dependencies (...);
CREATE TABLE tbl_module_permissions (...);
CREATE TABLE tbl_module_pricing (...);
CREATE TABLE tbl_franchise_module_subscriptions (...);
```

#### 1.2 Create Module Registry Service

```php
// src/ModuleRegistry.php
<?php
declare(strict_types=1);

namespace App;

use PDO;

class ModuleRegistry {
    private PDO $db;
    private array $cache = [];

    public function __construct(PDO $db) {
        $this->db = $db;
    }

    public function isModuleEnabled(int $franchiseId, string $moduleCode): bool {
        $cacheKey = "{$franchiseId}:{$moduleCode}";

        if (isset($this->cache[$cacheKey])) {
            return $this->cache[$cacheKey];
        }

        $stmt = $this->db->prepare('
            SELECT is_enabled
            FROM tbl_franchise_modules
            WHERE franchise_id = ? AND module_code = ?
        ');
        $stmt->execute([$franchiseId, $moduleCode]);

        $enabled = (bool) $stmt->fetchColumn();
        $this->cache[$cacheKey] = $enabled;

        return $enabled;
    }

    public function getEnabledModules(int $franchiseId): array {
        $stmt = $this->db->prepare('
            SELECT m.module_code, m.name, m.description, m.icon
            FROM tbl_franchise_modules fm
            JOIN tbl_modules m ON fm.module_code = m.module_code
            WHERE fm.franchise_id = ? AND fm.is_enabled = 1
        ');
        $stmt->execute([$franchiseId]);
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function enableModule(int $franchiseId, string $moduleCode): array {
        // Check dependencies
        $deps = $this->getModuleDependencies($moduleCode);
        foreach ($deps as $dep) {
            if (!$this->isModuleEnabled($franchiseId, $dep['requires_module_code'])) {
                return [
                    'success' => false,
                    'message' => "Module requires {$dep['requires_module_code']} to be enabled first"
                ];
            }
        }

        // Enable module
        $stmt = $this->db->prepare('
            INSERT INTO tbl_franchise_modules (franchise_id, module_code, is_enabled)
            VALUES (?, ?, 1)
            ON DUPLICATE KEY UPDATE
                is_enabled = 1,
                enabled_at = CURRENT_TIMESTAMP
        ');
        $stmt->execute([$franchiseId, $moduleCode]);

        // Clear cache
        unset($this->cache["{$franchiseId}:{$moduleCode}"]);

        return ['success' => true, 'message' => 'Module enabled successfully'];
    }

    private function getModuleDependencies(string $moduleCode): array {
        $stmt = $this->db->prepare('
            SELECT requires_module_code, is_required
            FROM tbl_module_dependencies
            WHERE module_code = ?
        ');
        $stmt->execute([$moduleCode]);
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
}
```

#### 1.3 Add Module Access Helpers

```php
// src/config/auth.php (add these functions)

/**
 * Require module access (redirect if disabled)
 */
function requireModuleAccess(string $moduleCode): void {
    if (!isLoggedIn()) {
        header('Location: ./sign-in.php');
        exit();
    }

    $franchiseId = (int) $_SESSION['franchise_id'];

    $db = (new \App\Config\Database())->getConnection();
    $registry = new \App\ModuleRegistry($db);

    if (!$registry->isModuleEnabled($franchiseId, $moduleCode)) {
        header('Location: ./module-not-available.php?module=' . urlencode($moduleCode));
        exit();
    }
}

/**
 * Check if module is enabled (non-blocking)
 */
function hasModuleAccess(string $moduleCode): bool {
    if (!isLoggedIn()) {
        return false;
    }

    $franchiseId = (int) $_SESSION['franchise_id'];

    $db = (new \App\Config\Database())->getConnection();
    $registry = new \App\ModuleRegistry($db);

    return $registry->isModuleEnabled($franchiseId, $moduleCode);
}

/**
 * Get all enabled modules for current tenant
 */
function getEnabledModules(): array {
    if (!isLoggedIn()) {
        return [];
    }

    $franchiseId = (int) $_SESSION['franchise_id'];

    $db = (new \App\Config\Database())->getConnection();
    $registry = new \App\ModuleRegistry($db);

    return $registry->getEnabledModules($franchiseId);
}
```

### Phase 2: Protect Existing Pages

#### 2.1 Add Module Checks to Pages

**Before:**
```php
// advanced-inventory-uom.php
<?php
require_once 'src/config/auth.php';

if (!isLoggedIn()) {
    header('Location: ./sign-in.php');
    exit();
}

requirePermissionGlobal('VIEW_INVENTORY');
?>
```

**After:**
```php
// advanced-inventory-uom.php
<?php
require_once 'src/config/auth.php';

if (!isLoggedIn()) {
    header('Location: ./sign-in.php');
    exit();
}

// CRITICAL: Add module check
requireModuleAccess('ADV_INV');
requirePermissionGlobal('VIEW_INVENTORY');
?>
```

#### 2.2 Batch Update Script

```bash
#!/bin/bash
# scripts/add-module-protection.sh

# Add module protection to all Advanced Inventory pages
for file in advanced-inventory-*.php stock-items-*.php stock-transfers-*.php; do
    if [ -f "$file" ]; then
        # Add requireModuleAccess after isLoggedIn check
        sed -i "/requirePermissionGlobal/i requireModuleAccess('ADV_INV');" "$file"
        echo "Updated: $file"
    fi
done

# Add module protection to all Restaurant pages
for file in restaurant-*.php table-*.php; do
    if [ -f "$file" ]; then
        sed -i "/requirePermissionGlobal/i requireModuleAccess('RESTAURANT');" "$file"
        echo "Updated: $file"
    fi
done
```

### Phase 3: Dynamic Navigation

#### 3.1 Update Top Navigation

```php
// includes/topbar.php
<?php
$enabledModules = getEnabledModules();
$moduleMap = array_column($enabledModules, 'name', 'module_code');
?>

<nav class="navbar">
    <!-- Core navigation (always visible) -->
    <a href="/dashboard.php">
        <i class="bi bi-house-door"></i> Dashboard
    </a>

    <!-- Module-specific navigation -->
    <?php if (hasModuleAccess('RETAIL')): ?>
        <div class="dropdown">
            <a href="#"><i class="bi bi-shop"></i> Retail</a>
            <ul>
                <li><a href="/pos-sales.php">POS Sales</a></li>
                <li><a href="/invoices.php">Invoices</a></li>
            </ul>
        </div>
    <?php endif; ?>

    <?php if (hasModuleAccess('ADV_INV')): ?>
        <div class="dropdown">
            <a href="#"><i class="bi bi-boxes"></i> Inventory</a>
            <ul>
                <li><a href="/stock-items-catalog.php">Stock Items</a></li>
                <li><a href="/advanced-inventory-uom.php">UOM Conversions</a></li>
                <li><a href="/stock-transfers.php">Stock Transfers</a></li>
            </ul>
        </div>
    <?php endif; ?>

    <?php if (hasModuleAccess('RESTAURANT')): ?>
        <div class="dropdown">
            <a href="#"><i class="bi bi-cup-hot"></i> Restaurant</a>
            <ul>
                <li><a href="/restaurant-orders.php">Orders</a></li>
                <li><a href="/tables.php">Tables</a></li>
                <li><a href="/reservations.php">Reservations</a></li>
            </ul>
        </div>
    <?php endif; ?>

    <!-- Settings (always visible) -->
    <a href="/settings.php">
        <i class="bi bi-gear"></i> Settings
    </a>
</nav>
```

### Phase 4: Module Marketplace

#### 4.1 Create Module Marketplace Page

```php
// modules-marketplace.php
<?php
require_once 'src/config/auth.php';

if (!isLoggedIn()) {
    header('Location: ./sign-in.php');
    exit();
}

requirePermissionGlobal('MANAGE_BILLING');  // Only owners can manage modules

$db = (new \App\Config\Database())->getConnection();
$registry = new \App\ModuleRegistry($db);

$franchiseId = (int) $_SESSION['franchise_id'];
$availableModules = $registry->getAvailableModules();
$enabledModules = $registry->getEnabledModules($franchiseId);
$enabledCodes = array_column($enabledModules, 'module_code');
?>
<!DOCTYPE html>
<html>
<head>
    <?php include './includes/head.php'; ?>
    <style>
        .module-card {
            border: 1px solid #e6e8eb;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        .module-card.enabled {
            border-color: #206bc4;
            background: #e6f2ff;
        }
        .module-card .icon {
            font-size: 3rem;
            color: #206bc4;
        }
    </style>
</head>
<body>
    <div class="page">
        <?php include './includes/topbar.php'; ?>

        <div class="page-wrapper">
            <div class="page-header">
                <div class="container-xl">
                    <h2 class="page-title">Module Marketplace</h2>
                    <p class="text-muted">Enable modules to unlock new features</p>
                </div>
            </div>

            <div class="page-body">
                <div class="container-xl">
                    <div class="row row-cards">
                        <?php foreach ($availableModules as $code => $module): ?>
                            <?php if ($module['is_core']) continue; ?>
                            <?php $isEnabled = in_array($code, $enabledCodes); ?>

                            <div class="col-md-6 col-lg-4">
                                <div class="module-card <?= $isEnabled ? 'enabled' : '' ?>">
                                    <div class="text-center mb-3">
                                        <i class="<?= $module['icon'] ?> icon"></i>
                                    </div>

                                    <h3><?= htmlspecialchars($module['name']) ?></h3>
                                    <p class="text-muted"><?= htmlspecialchars($module['description']) ?></p>

                                    <div class="mt-3">
                                        <p class="h3">$<?= number_format($module['price_monthly'], 2) ?>/mo</p>
                                        <small class="text-muted"><?= $module['trial_days'] ?> day free trial</small>
                                    </div>

                                    <?php if (!$isEnabled): ?>
                                        <button class="btn btn-primary w-100 mt-3"
                                                onclick="enableModule('<?= $code ?>')">
                                            <i class="bi bi-plus-circle"></i> Enable Module
                                        </button>
                                    <?php else: ?>
                                        <button class="btn btn-success w-100 mt-3" disabled>
                                            <i class="bi bi-check-circle"></i> Enabled
                                        </button>
                                        <button class="btn btn-outline-danger w-100 mt-2"
                                                onclick="disableModule('<?= $code ?>')">
                                            Disable
                                        </button>
                                    <?php endif; ?>
                                </div>
                            </div>
                        <?php endforeach; ?>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <?php include './includes/foot.php'; ?>

    <script>
        async function enableModule(moduleCode) {
            const result = await Swal.fire({
                title: 'Enable Module?',
                text: 'Start your free trial',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Enable'
            });

            if (!result.isConfirmed) return;

            try {
                const res = await fetch('./api/modules.php?action=enable', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ module_code: moduleCode })
                });

                const data = await res.json();

                if (data.success) {
                    Swal.fire('Enabled!', data.message, 'success').then(() => {
                        window.location.reload();
                    });
                } else {
                    Swal.fire('Error', data.message, 'error');
                }
            } catch (error) {
                Swal.fire('Error', error.message, 'error');
            }
        }

        async function disableModule(moduleCode) {
            const result = await Swal.fire({
                title: 'Disable Module?',
                text: 'Your data will be preserved',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Disable',
                confirmButtonColor: '#d33'
            });

            if (!result.isConfirmed) return;

            try {
                const res = await fetch('./api/modules.php?action=disable', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ module_code: moduleCode })
                });

                const data = await res.json();

                if (data.success) {
                    Swal.fire('Disabled', data.message, 'success').then(() => {
                        window.location.reload();
                    });
                } else {
                    Swal.fire('Error', data.message, 'error');
                }
            } catch (error) {
                Swal.fire('Error', error.message, 'error');
            }
        }
    </script>
</body>
</html>
```

#### 4.2 Create Module API

```php
// api/modules.php
<?php
declare(strict_types=1);

require_once '../src/config/auth.php';
require_once '../src/config/database.php';

header('Content-Type: application/json');

if (!isLoggedIn()) {
    http_response_code(401);
    echo json_encode(['success' => false, 'message' => 'Unauthorized']);
    exit();
}

requirePermissionGlobal('MANAGE_BILLING');

$db = (new \App\Config\Database())->getConnection();
$registry = new \App\ModuleRegistry($db);
$franchiseId = (int) $_SESSION['franchise_id'];

$input = json_decode(file_get_contents('php://input'), true) ?? [];
$action = $_GET['action'] ?? $input['action'] ?? '';

try {
    switch ($action) {
        case 'list':
            $modules = $registry->getAvailableModules();
            echo json_encode(['success' => true, 'modules' => $modules]);
            break;

        case 'enabled':
            $modules = $registry->getEnabledModules($franchiseId);
            echo json_encode(['success' => true, 'modules' => $modules]);
            break;

        case 'enable':
            $moduleCode = $input['module_code'] ?? '';
            $result = $registry->enableModule($franchiseId, $moduleCode);
            echo json_encode($result);
            break;

        case 'disable':
            $moduleCode = $input['module_code'] ?? '';
            $result = $registry->disableModule($franchiseId, $moduleCode);
            echo json_encode($result);
            break;

        default:
            http_response_code(400);
            echo json_encode(['success' => false, 'message' => 'Invalid action']);
    }
} catch (\Exception $e) {
    error_log('Module API Error: ' . $e->getMessage());
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => $e->getMessage()]);
}
```

### Phase 5: Module Not Available Page

```php
// module-not-available.php
<?php
require_once 'src/config/auth.php';

if (!isLoggedIn()) {
    header('Location: ./sign-in.php');
    exit();
}

$moduleCode = $_GET['module'] ?? 'UNKNOWN';
$moduleName = getModuleName($moduleCode);

function getModuleName(string $code): string {
    $names = [
        'ADV_INV' => 'Advanced Inventory',
        'RESTAURANT' => 'Restaurant Management',
        'PHARMACY' => 'Pharmacy Management',
        'RETAIL' => 'Retail POS',
    ];
    return $names[$code] ?? 'Unknown Module';
}
?>
<!DOCTYPE html>
<html>
<head>
    <?php include './includes/head.php'; ?>
</head>
<body>
    <div class="page">
        <?php include './includes/topbar.php'; ?>

        <div class="page-wrapper">
            <div class="page-body">
                <div class="container-xl d-flex flex-column justify-content-center">
                    <div class="empty">
                        <div class="empty-icon">
                            <i class="bi bi-lock-fill" style="font-size: 4rem;"></i>
                        </div>
                        <p class="empty-title">Module Not Available</p>
                        <p class="empty-subtitle text-muted">
                            The <strong><?= htmlspecialchars($moduleName) ?></strong> module is not enabled for your account.
                        </p>
                        <div class="empty-action">
                            <a href="./modules-marketplace.php" class="btn btn-primary">
                                <i class="bi bi-shop"></i> View Module Marketplace
                            </a>
                            <a href="./dashboard.php" class="btn btn-secondary">
                                <i class="bi bi-house-door"></i> Back to Dashboard
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <?php include './includes/foot.php'; ?>
</body>
</html>
```

## Testing Your Implementation

### Test 1: Module Access Control

```php
// tests/ModuleAccessTest.php
class ModuleAccessTest extends TestCase {
    public function testDisabledModuleRedirects() {
        $this->disableModule('ADV_INV');

        $response = $this->get('/advanced-inventory-uom.php');

        $this->assertRedirect('/module-not-available.php?module=ADV_INV');
    }

    public function testEnabledModuleAllowsAccess() {
        $this->enableModule('ADV_INV');

        $response = $this->get('/advanced-inventory-uom.php');

        $this->assertStatus(200);
    }
}
```

### Test 2: Module Dependencies

```php
public function testCannotEnableModuleWithoutDependencies() {
    $this->disableModule('CORE');

    $result = $this->enableModule('ADV_INV');

    $this->assertFalse($result['success']);
    $this->assertStringContainsString('requires CORE', $result['message']);
}
```

### Test 3: Navigation Visibility

```php
public function testNavigationHidesDisabledModules() {
    $this->disableModule('RESTAURANT');

    $response = $this->get('/dashboard.php');

    $this->assertStringNotContainsString('restaurant-orders.php', $response);
}
```

## Rollout Strategy

### Option 1: Gradual Migration (Recommended)

1. **Week 1:** Add module infrastructure (database, helpers)
2. **Week 2:** Enable all modules for all existing tenants (no changes to UX)
3. **Week 3:** Add module protection to 50% of pages
4. **Week 4:** Complete module protection, add marketplace
5. **Week 5:** Launch module marketplace to new tenants only
6. **Week 6:** Allow existing tenants to opt-in to modular pricing

### Option 2: Big Bang Migration

1. Add all infrastructure
2. Enable all modules for all tenants
3. Add module protection to all pages
4. Launch marketplace
5. Migrate billing

## Common Issues and Solutions

### Issue: Circular Dependencies

**Problem:** Module A requires Module B, Module B requires Module A

**Solution:**
```php
// Check dependencies recursively
private function checkCircularDependencies(string $moduleCode, array $checked = []): bool {
    if (in_array($moduleCode, $checked)) {
        return true;  // Circular dependency detected
    }

    $checked[] = $moduleCode;
    $deps = $this->getModuleDependencies($moduleCode);

    foreach ($deps as $dep) {
        if ($this->checkCircularDependencies($dep['requires_module_code'], $checked)) {
            return true;
        }
    }

    return false;
}
```

### Issue: Performance with Many Module Checks

**Problem:** Every page checks module access, slowing down requests

**Solution:** Cache module access in session
```php
function hasModuleAccess(string $moduleCode): bool {
    if (!isset($_SESSION['enabled_modules'])) {
        $_SESSION['enabled_modules'] = getEnabledModules();
    }

    return in_array($moduleCode, array_column($_SESSION['enabled_modules'], 'module_code'));
}
```

### Issue: Billing Integration Complexity

**Problem:** Need to bill for multiple modules, handle prorations, etc.

**Solution:** Use Stripe Subscriptions with multiple items
```php
// Create subscription with multiple modules
$subscription = \Stripe\Subscription::create([
    'customer' => $stripeCustomerId,
    'items' => [
        ['price' => 'price_adv_inv'],  // Advanced Inventory
        ['price' => 'price_restaurant'],  // Restaurant
    ],
]);
```

## Next Steps

1. Review `references/database-schema.md` for complete schema
2. Implement Phase 1 (core infrastructure)
3. Test module access control
4. Roll out to staging environment
5. Migrate existing tenants
6. Launch module marketplace
