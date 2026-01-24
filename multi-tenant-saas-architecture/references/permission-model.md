# RBAC Permission Model

## Database Schema

```sql
-- Global role definitions (reusable across tenants)
CREATE TABLE global_roles (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_system BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Permission definitions
CREATE TABLE permissions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    module VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_module (module)
);

-- Role → Permission mapping (global template)
CREATE TABLE global_role_permissions (
    global_role_id BIGINT NOT NULL,
    permission_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (global_role_id, permission_id),
    FOREIGN KEY (global_role_id) REFERENCES global_roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
);

-- User → Role assignments (tenant-scoped)
CREATE TABLE user_roles (
    user_id BIGINT NOT NULL,
    global_role_id BIGINT NOT NULL,
    tenant_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, global_role_id, tenant_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (global_role_id) REFERENCES global_roles(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

-- Direct user permission overrides (tenant-scoped)
CREATE TABLE user_permissions (
    user_id BIGINT NOT NULL,
    permission_id BIGINT NOT NULL,
    tenant_id BIGINT NOT NULL,
    allowed BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, permission_id, tenant_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

-- Tenant-level role permission overrides
CREATE TABLE tenant_role_overrides (
    tenant_id BIGINT NOT NULL,
    global_role_id BIGINT NOT NULL,
    permission_id BIGINT NOT NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (tenant_id, global_role_id, permission_id),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (global_role_id) REFERENCES global_roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
);
```

## Permission Resolution Algorithm

```javascript
/**
 * Check if user has permission within tenant context
 *
 * Priority:
 * 1. User denial (explicit) → DENY
 * 2. User grant (explicit) → ALLOW
 * 3. Tenant override → ALLOW/DENY
 * 4. Role permission → ALLOW
 * 5. Super admin → ALLOW
 * 6. Default → DENY
 */
async function hasPermission(userId, tenantId, permissionCode) {
  // Super admin bypass
  const user = await getUser(userId);
  if (user.type === 'super_admin') {
    await auditLog('PERMISSION_BYPASS', {userId, permissionCode, reason: 'super_admin'});
    return true;
  }

  // Check explicit user denial
  const userDenial = await db.user_permissions.findOne({
    user_id: userId,
    tenant_id: tenantId,
    permission_id: getPermissionId(permissionCode),
    allowed: false
  });
  if (userDenial) return false;

  // Check explicit user grant
  const userGrant = await db.user_permissions.findOne({
    user_id: userId,
    tenant_id: tenantId,
    permission_id: getPermissionId(permissionCode),
    allowed: true
  });
  if (userGrant) return true;

  // Get user's roles within tenant
  const roles = await getUserRoles(userId, tenantId);

  // Check role-based permissions with tenant overrides
  for (const role of roles) {
    const roleHasPermission = await checkRolePermission(role.id, permissionCode);
    if (!roleHasPermission) continue;

    // Check if tenant has overridden this permission for this role
    const tenantOverride = await db.tenant_role_overrides.findOne({
      tenant_id: tenantId,
      global_role_id: role.id,
      permission_id: getPermissionId(permissionCode)
    });

    if (tenantOverride) {
      return tenantOverride.is_enabled;
    }

    return true; // Role grants permission, no override exists
  }

  return false; // Default deny
}
```

## Permission Caching

```javascript
/**
 * Cache permissions for 15 minutes to reduce DB load
 */
class PermissionCache {
  constructor() {
    this.cache = new Map();
    this.TTL = 15 * 60 * 1000; // 15 minutes
  }

  getCacheKey(userId, tenantId) {
    return `${userId}:${tenantId}`;
  }

  async get(userId, tenantId, permissionCode) {
    const key = this.getCacheKey(userId, tenantId);
    const cached = this.cache.get(key);

    if (cached && Date.now() - cached.timestamp < this.TTL) {
      return cached.permissions.includes(permissionCode);
    }

    // Cache miss: Load from DB
    const permissions = await loadAllPermissions(userId, tenantId);
    this.cache.set(key, {
      permissions,
      timestamp: Date.now()
    });

    return permissions.includes(permissionCode);
  }

  invalidate(userId, tenantId) {
    const key = this.getCacheKey(userId, tenantId);
    this.cache.delete(key);
  }

  invalidateAll() {
    this.cache.clear();
  }
}

const permissionCache = new PermissionCache();

// Invalidate on permission changes
eventBus.on('user.role.changed', ({userId, tenantId}) => {
  permissionCache.invalidate(userId, tenantId);
});

eventBus.on('role.permission.changed', () => {
  permissionCache.invalidateAll(); // Affects all users with this role
});
```

## Seed Data

```sql
-- Insert default roles
INSERT INTO global_roles (code, name, description, is_system) VALUES
('SUPER_ADMIN', 'Super Administrator', 'Platform-wide access', TRUE),
('TENANT_OWNER', 'Tenant Owner', 'Full tenant management', TRUE),
('MANAGER', 'Manager', 'Operational management', TRUE),
('STAFF', 'Staff', 'Basic access', TRUE),
('VIEWER', 'Viewer', 'Read-only access', TRUE);

-- Insert default permissions
INSERT INTO permissions (code, name, description, module) VALUES
-- User Management
('USER_VIEW', 'View Users', 'View user list and details', 'users'),
('USER_CREATE', 'Create Users', 'Add new users', 'users'),
('USER_EDIT', 'Edit Users', 'Modify user details', 'users'),
('USER_DELETE', 'Delete Users', 'Remove users', 'users'),
('USER_ASSIGN_ROLES', 'Assign Roles', 'Manage user roles', 'users'),

-- Sales
('SALE_VIEW', 'View Sales', 'View sales transactions', 'sales'),
('SALE_CREATE', 'Create Sales', 'Process sales', 'sales'),
('SALE_VOID', 'Void Sales', 'Cancel sales', 'sales'),
('SALE_REFUND', 'Process Refunds', 'Issue refunds', 'sales'),

-- Inventory
('INVENTORY_VIEW', 'View Inventory', 'View stock levels', 'inventory'),
('INVENTORY_ADJUST', 'Adjust Inventory', 'Modify stock', 'inventory'),

-- Reports
('REPORT_SALES', 'Sales Reports', 'View sales reports', 'reports'),
('REPORT_FINANCIAL', 'Financial Reports', 'View financial reports', 'reports'),

-- Settings
('SETTINGS_VIEW', 'View Settings', 'View settings', 'settings'),
('SETTINGS_EDIT', 'Edit Settings', 'Modify settings', 'settings');

-- Assign permissions to MANAGER role
INSERT INTO global_role_permissions (global_role_id, permission_id)
SELECT r.id, p.id
FROM global_roles r
CROSS JOIN permissions p
WHERE r.code = 'MANAGER'
  AND p.code IN (
    'USER_VIEW', 'SALE_VIEW', 'SALE_CREATE', 'SALE_VOID',
    'INVENTORY_VIEW', 'REPORT_SALES', 'SETTINGS_VIEW'
  );
```

## Middleware Implementation

```javascript
/**
 * Express middleware for permission checks
 */
function requirePermission(permissionCode) {
  return async (req, res, next) => {
    const {userId, tenantId} = req.auth; // From JWT/session

    const allowed = await hasPermission(userId, tenantId, permissionCode);

    if (!allowed) {
      return res.status(403).json({
        success: false,
        error: {
          code: 'PERMISSION_DENIED',
          message: `Permission required: ${permissionCode}`
        }
      });
    }

    next();
  };
}

// Usage
app.delete('/api/v1/users/:id', requirePermission('USER_DELETE'), async (req, res) => {
  // User has permission, proceed
});
```

## Common Patterns

### Hierarchical Permissions

```javascript
// Grant higher permission implies lower
const PERMISSION_HIERARCHY = {
  'USER_DELETE': ['USER_EDIT', 'USER_VIEW'],
  'USER_EDIT': ['USER_VIEW'],
  'SALE_REFUND': ['SALE_VOID', 'SALE_VIEW'],
  'SALE_VOID': ['SALE_VIEW']
};

function hasPermissionOrHigher(userId, tenantId, permissionCode) {
  if (hasPermission(userId, tenantId, permissionCode)) {
    return true;
  }

  // Check if user has higher permission
  for (const [higher, lowers] of Object.entries(PERMISSION_HIERARCHY)) {
    if (lowers.includes(permissionCode) && hasPermission(userId, tenantId, higher)) {
      return true;
    }
  }

  return false;
}
```

### Conditional Permissions

```javascript
// Permission based on data ownership
async function canEditOrder(userId, tenantId, orderId) {
  const order = await db.orders.findOne({id: orderId, tenant_id: tenantId});
  if (!order) return false;

  // Basic permission check
  if (!await hasPermission(userId, tenantId, 'SALE_EDIT')) {
    return false;
  }

  // Own orders only (for staff role)
  const user = await getUser(userId);
  if (user.role === 'STAFF' && order.created_by !== userId) {
    return false;
  }

  return true;
}
```

## Bulk Permission Checks

```javascript
/**
 * Check multiple permissions at once (more efficient)
 */
async function hasAnyPermission(userId, tenantId, permissionCodes) {
  const permissions = await loadAllPermissions(userId, tenantId);
  return permissionCodes.some(code => permissions.includes(code));
}

async function hasAllPermissions(userId, tenantId, permissionCodes) {
  const permissions = await loadAllPermissions(userId, tenantId);
  return permissionCodes.every(code => permissions.includes(code));
}

// Usage
if (await hasAnyPermission(userId, tenantId, ['SALE_VIEW', 'SALE_CREATE'])) {
  // User can view OR create sales
}
```
