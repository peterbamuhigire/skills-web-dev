---
name: multi-tenant-saas-architecture
description: "Production-grade multi-tenant SaaS platform architecture with three-panel separation, zero-trust security, strict tenant isolation, auditability, and scalable operational safeguards. Includes authentication/authorization models, API design, data access patterns, compliance, and migration strategies. Use for designing multi-tenant systems, implementing permissions, ensuring isolation, and operating SaaS platforms at scale."
---

# Multi-Tenant SaaS Platform Architecture

## Executive Summary

This document describes a production-grade, multi-tenant SaaS architecture designed for security, scalability, and operational excellence. The platform implements a three-panel separation model with defense-in-depth security, comprehensive audit trails, and strict data isolation guarantees.

**Key Principles:**
- **Zero Trust Architecture**: Every request is authenticated, authorized, and validated
- **Tenant Isolation by Default**: No data access without explicit tenant context
- **Least Privilege Access**: Permissions are granular, explicit, and auditable
- **Defense in Depth**: Multiple security layers prevent privilege escalation
- **Audit Everything**: All privileged operations create immutable audit trails

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Three-Panel Architecture](#three-panel-architecture)
3. [Multi-Tenant Isolation Model](#multi-tenant-isolation-model)
4. [Authentication & Authorization](#authentication--authorization)
5. [Security Architecture](#security-architecture)
6. [API Design Principles](#api-design-principles)
7. [Data Access Patterns](#data-access-patterns)
8. [Audit & Compliance](#audit--compliance)
9. [Operational Safeguards](#operational-safeguards)
10. [Development Guidelines](#development-guidelines)
11. [Migration & Evolution Strategy](#migration--evolution-strategy)

---

## System Overview

### Architectural Philosophy

The platform follows a **separation of concerns** model where three distinct user experiences share a common backend infrastructure while maintaining strict security boundaries:

```
┌─────────────────────────────────────────────────────────────┐
│                    Shared Infrastructure                     │
│  ┌──────────────┬──────────────────┬────────────────────┐  │
│  │ Data Layer   │ Business Logic   │ Integration Layer  │  │
│  │ (Isolated)   │ (Tenant-Aware)   │ (External APIs)    │  │
│  └──────────────┴──────────────────┴────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
    ┌────▼────┐        ┌─────▼─────┐       ┌─────▼──────┐
    │ Tenant  │        │   Admin   │       │  Customer  │
    │   App   │        │   Panel   │       │   Portal   │
    │         │        │           │       │            │
    │ Daily   │        │ Platform  │       │ External   │
    │ Ops     │        │ Mgmt      │       │ Access     │
    └─────────┘        └───────────┘       └────────────┘
```

### Design Goals

1. **Security First**: Prevent unauthorized access at every layer
2. **Operational Clarity**: Clear role boundaries and responsibilities
3. **Maintainability**: Consistent patterns across all features
4. **Scalability**: Handle growth in tenants, users, and data volume
5. **Compliance Ready**: Built-in audit trails and data governance
6. **Developer Productivity**: Clear guidelines reduce cognitive load

---

## Three-Panel Architecture

### 1. Main Tenant Application

**Purpose**: Daily operations for each tenant's staff  
**Users**: Tenant owners, managers, employees  
**Scope**: Single-tenant, fully isolated  
**Security Model**: Role-based access within tenant boundaries

**Characteristics:**
- **Tenant-scoped by default**: All queries include tenant context
- **Role hierarchy**: Owner → Manager → Staff → Limited roles
- **Feature-rich**: Full CRUD operations for business entities
- **Session-based auth**: Typically cookie-based for web interfaces
- **Mobile/API support**: JWT tokens for native apps and integrations

**Example Use Cases:**
- Managing inventory, sales, or service delivery
- Processing transactions and generating reports
- Configuring tenant-specific settings
- Collaborating with team members

**Key Constraints:**
- Cannot access other tenants' data
- Cannot modify platform-level settings
- Cannot create or suspend other tenants
- All operations are logged for tenant-level audit

---

### 2. Admin Panel (Platform Operations)

**Purpose**: Platform management and cross-tenant operations  
**Users**: Platform staff (root admin, super admins)  
**Scope**: Multi-tenant with controlled access  
**Security Model**: Permission-based with explicit tenant assignments

**Characteristics:**
- **Separate entry point**: Distinct URL, routes, and UI
- **Granular permissions**: 50+ named permissions across categories
- **Tenant assignment model**: Super admins access only assigned tenants
- **Invitation-only**: No self-registration; email verification required
- **Enhanced audit**: All actions logged with full context

**Permission Categories:**
```
System Management
├── tenant.create          Create new tenants
├── tenant.suspend         Suspend/reactivate tenants
├── tenant.delete          Permanently delete tenants
└── tenant.configure       Modify tenant settings

User Management
├── superadmin.invite      Invite platform staff
├── superadmin.suspend     Suspend admin accounts
├── user.impersonate       Impersonate tenant users (high-risk)
└── user.export            Export user data

Subscription & Billing
├── subscription.create    Create subscriptions
├── subscription.modify    Change subscription plans
├── billing.view           View payment records
└── billing.refund         Process refunds

Audit & Compliance
├── audit.view             View audit logs
├── audit.export           Export audit trails
└── compliance.report      Generate compliance reports

Platform Configuration
├── config.system          Modify system settings
├── feature.toggle         Enable/disable features
└── integration.manage     Configure integrations
```

**Root vs Super Admin:**

| Capability | Root | Super Admin |
|------------|------|-------------|
| Access all tenants | ✅ | ❌ (assigned only) |
| Bypass permission checks | ✅ | ❌ |
| Create super admins | ✅ | ❌ |
| Suspend super admins | ✅ | Limited |
| Platform configuration | ✅ | Restricted |
| Audit trail exemption | ❌ | ❌ |
| Multiple instances | ❌ (single) | ✅ (many) |

**Example Use Cases:**
- Onboarding new tenant organizations
- Managing subscription lifecycle
- Investigating cross-tenant issues
- Generating platform-wide analytics
- Responding to support escalations

---

### 3. Customer Portal

**Purpose**: Self-service for tenant's end customers  
**Users**: Students, clients, members, consumers  
**Scope**: Read-heavy, limited to owned data  
**Security Model**: Minimal permissions, user-centric

**Characteristics:**
- **Public-facing**: Assumes hostile internet exposure
- **Minimal scope**: Only personal data and permitted tenant content
- **Read-heavy**: Mostly queries; limited mutations
- **Simplified auth**: Email/SMS login, magic links, or OAuth
- **No admin capabilities**: Cannot see staff, settings, or business logic

**Example Use Cases:**
- Viewing personal account details
- Tracking orders or service status
- Accessing tenant-published content (catalogs, schedules)
- Submitting feedback or requests
- Managing personal preferences

**Security Considerations:**
- Token lifetimes are short (15-60 minutes)
- Rate limiting is aggressive
- No exposure of internal identifiers
- PII is minimized in responses
- CORS policies are strict

---

## Multi-Tenant Isolation Model

### Core Principle: Tenant Context is Mandatory

**Every database query that touches tenant data must include the tenant identifier.** This is not optional. It is enforced through multiple mechanisms:

### 1. Middleware Layer
```php
// Pseudocode: Tenant context middleware
class TenantContextMiddleware {
    public function handle(Request $request, Closure $next) {
        $tenantId = $this->resolveTenant($request);
        
        if (!$tenantId && $this->requiresTenant($request)) {
            throw new UnauthorizedException('Tenant context required');
        }
        
        // Inject into request context
        $request->setTenantContext($tenantId);
        
        // Set database scope (global query filter)
        TenantScope::set($tenantId);
        
        return $next($request);
    }
}
```

### 2. Repository Pattern
```php
// All repositories enforce tenant scoping
class BaseRepository {
    protected function buildQuery() {
        $query = $this->model->newQuery();
        
        // Automatic tenant filter
        if ($this->isTenantScoped()) {
            $tenantId = TenantContext::current();
            
            if (!$tenantId) {
                throw new MissingTenantException();
            }
            
            $query->where('tenant_id', $tenantId);
        }
        
        return $query;
    }
}
```

### 3. Database Constraints
```sql
-- Every tenant-scoped table includes:
CREATE TABLE orders (
    id BIGINT PRIMARY KEY,
    tenant_id BIGINT NOT NULL,
    -- other columns
    
    -- Composite indexes for performance
    INDEX idx_tenant_created (tenant_id, created_at),
    
    -- Foreign key enforcement
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);
```

### 4. Guard Validation
```php
// Guards ensure user can access requested tenant
class TenantAccessGuard {
    public function authorize(User $user, int $tenantId): bool {
        // Root bypasses all checks
        if ($user->isRoot()) {
            return true;
        }
        
        // Super admins: check tenant assignment
        if ($user->isSuperAdmin()) {
            return $user->hasAssignedTenant($tenantId);
        }
        
        // Regular users: must belong to tenant
        return $user->tenant_id === $tenantId;
    }
}
```

### Tenant Resolution Strategy

**Priority order for determining tenant context:**

1. **Authenticated user's tenant** (for tenant app users)
2. **Explicit tenant parameter** (for admin operations, validated)
3. **Subdomain mapping** (e.g., `acme.platform.com` → tenant_slug='acme')
4. **API token metadata** (for API clients)
5. **Session override** (for impersonation, heavily audited)

### Cross-Tenant Operations

Cross-tenant queries are **prohibited in tenant and customer contexts**. They are only permitted in the admin panel with:

- Explicit permission (e.g., `reports.cross_tenant`)
- Tenant scope validation (super admins can only query assigned tenants)
- Mandatory audit logging
- Results explicitly marked as multi-tenant

```php
// Admin-only cross-tenant query
if (!$user->hasPermission('reports.cross_tenant')) {
    throw new ForbiddenException();
}

$tenantIds = $this->getAuthorizedTenants($user);

$data = DB::table('orders')
    ->whereIn('tenant_id', $tenantIds)
    ->select('tenant_id', DB::raw('COUNT(*) as order_count'))
    ->groupBy('tenant_id')
    ->get();

AuditLog::record([
    'action' => 'cross_tenant_query',
    'actor' => $user->id,
    'tenants' => $tenantIds,
    'query_type' => 'aggregate_orders'
]);
```

---

## Authentication & Authorization

### Authentication Flow by Panel

#### Tenant App Authentication
```
1. User submits credentials (email + password)
2. System validates credentials
3. System loads user + tenant association
4. Session created with tenant context
5. Session cookie issued (HttpOnly, Secure, SameSite)
6. User redirected to tenant dashboard
```

**Session Contents:**
- User ID
- Tenant ID
- Role within tenant
- Permissions cache
- Last activity timestamp
- CSRF token

#### Admin Panel Authentication
```
1. Super admin submits credentials
2. System validates + checks account status (active/suspended)
3. System loads permissions + tenant assignments
4. Enhanced session created with admin context
5. Session cookie issued with shorter timeout
6. User redirected to admin dashboard
```

**Session Contents:**
- Admin user ID
- Role (root vs super admin)
- Permission list (full enumeration)
- Assigned tenant IDs (empty for root)
- Audit context metadata
- MFA status (if enabled)

#### Customer Portal Authentication
```
1. Customer submits email or phone
2. System sends magic link or OTP
3. Customer clicks link or enters code
4. Stateless JWT token issued
5. Token includes: user_id, tenant_id, expiry
6. Frontend stores token (memory or httpOnly cookie)
```

**Token Contents (JWT):**
```json
{
  "sub": "customer_12345",
  "tenant_id": "tenant_789",
  "role": "customer",
  "exp": 1736000000,
  "iat": 1735996400,
  "scope": "portal.read"
}
```

### Authorization Model

#### Role Hierarchy
```
ROOT (platform owner)
  └── SUPER ADMIN (platform staff)
        └── (no hierarchy; flat assignment)

TENANT OWNER (tenant)
  └── TENANT ADMIN
      └── MANAGER
          └── STAFF
              └── LIMITED USER

CUSTOMER (external)
  └── (no hierarchy)
```

#### Permission Check Flow
```php
class PermissionChecker {
    public function check(User $user, string $permission, ?int $tenantId = null): bool {
        // 1. Root bypasses all checks
        if ($user->isRoot()) {
            AuditLog::logRootAccess($user, $permission);
            return true;
        }
        
        // 2. Check if user has permission
        if (!$user->hasPermission($permission)) {
            return false;
        }
        
        // 3. For tenant-scoped operations, validate tenant access
        if ($tenantId !== null) {
            if ($user->isSuperAdmin()) {
                return $user->hasAssignedTenant($tenantId);
            }
            
            return $user->tenant_id === $tenantId;
        }
        
        return true;
    }
}
```

#### Permission Storage Schema
```sql
-- Permissions table (canonical list)
CREATE TABLE permissions (
    id INT PRIMARY KEY,
    code VARCHAR(100) UNIQUE NOT NULL,  -- e.g., 'tenant.create'
    category VARCHAR(50),                -- e.g., 'Tenant Management'
    description TEXT,
    risk_level ENUM('low', 'medium', 'high', 'critical'),
    requires_mfa BOOLEAN DEFAULT FALSE
);

-- User-permission assignment
CREATE TABLE user_permissions (
    user_id BIGINT,
    permission_id INT,
    granted_by BIGINT,                   -- Who granted this permission
    granted_at TIMESTAMP,
    expires_at TIMESTAMP NULL,           -- Optional expiration
    PRIMARY KEY (user_id, permission_id)
);

-- Tenant assignments for super admins
CREATE TABLE superadmin_tenant_assignments (
    superadmin_id BIGINT,
    tenant_id BIGINT,
    assigned_by BIGINT,
    assigned_at TIMESTAMP,
    PRIMARY KEY (superadmin_id, tenant_id)
);
```

### Multi-Factor Authentication (MFA)

**Enforcement Rules:**
- Required for all root operations
- Required for high-risk permissions (configurable per permission)
- Optional but encouraged for tenant owners
- Not required for customer portal (low-privilege)

**MFA Implementation:**
```php
class MFAChecker {
    public function requiresMFA(User $user, string $action): bool {
        // Always for root
        if ($user->isRoot()) {
            return true;
        }
        
        // Check if action requires MFA
        $permission = Permission::findByAction($action);
        if ($permission && $permission->requires_mfa) {
            return true;
        }
        
        // Check if tenant requires MFA
        if ($user->tenant && $user->tenant->enforce_mfa) {
            return true;
        }
        
        return false;
    }
    
    public function validateMFA(User $user, string $code): bool {
        $secret = $user->mfa_secret;
        return GoogleAuthenticator::verify($code, $secret);
    }
}
```

---

## Security Architecture

### Defense in Depth Model

Security is enforced at **seven layers**. An attacker must bypass all layers to gain unauthorized access:

```
┌──────────────────────────────────────────────────────┐
│ Layer 7: Audit & Monitoring (Detection)             │
├──────────────────────────────────────────────────────┤
│ Layer 6: Rate Limiting (Abuse Prevention)           │
├──────────────────────────────────────────────────────┤
│ Layer 5: Input Validation (Injection Defense)       │
├──────────────────────────────────────────────────────┤
│ Layer 4: Tenant Scope Validation (Isolation)        │
├──────────────────────────────────────────────────────┤
│ Layer 3: Permission Checks (Authorization)          │
├──────────────────────────────────────────────────────┤
│ Layer 2: Role Guards (Role Verification)            │
├──────────────────────────────────────────────────────┤
│ Layer 1: Authentication (Identity Verification)     │
└──────────────────────────────────────────────────────┘
```

### Layer Details

#### Layer 1: Authentication
**What it does**: Verifies "who you are"

**Mechanisms:**
- Password hashing (bcrypt/Argon2)
- Session token validation
- JWT signature verification
- Token expiration checks
- Account status verification (active/suspended)

**Example:**
```php
if (!Auth::check()) {
    throw new UnauthenticatedException('Authentication required');
}

if (Auth::user()->status === 'suspended') {
    Auth::logout();
    throw new AccountSuspendedException();
}
```

#### Layer 2: Role Guards
**What it does**: Verifies "what type of user you are"

**Mechanisms:**
- Admin panel requires `isRoot()` or `isSuperAdmin()`
- Tenant app requires `isTenantUser()`
- Customer portal requires `isCustomer()`
- Wrong role = hard rejection (not just UI hiding)

**Example:**
```php
// Admin panel route guard
if (!$user->isRoot() && !$user->isSuperAdmin()) {
    throw new ForbiddenException('Admin access required');
}
```

#### Layer 3: Permission Checks
**What it does**: Verifies "what you're allowed to do"

**Mechanisms:**
- Permission lookup in user's permission set
- Permission required for every privileged action
- Permissions are non-inheritable (must be explicit)
- Critical permissions require MFA

**Example:**
```php
if (!$user->hasPermission('tenant.suspend')) {
    throw new ForbiddenException('Insufficient permissions');
}
```

#### Layer 4: Tenant Scope Validation
**What it does**: Verifies "which tenant you can access"

**Mechanisms:**
- Tenant ID extracted from request
- User-tenant relationship validated
- Super admins checked against assignment table
- Root bypasses (but is audited)

**Example:**
```php
$requestedTenant = $request->input('tenant_id');

if (!$user->canAccessTenant($requestedTenant)) {
    throw new TenantAccessDeniedException();
}
```

#### Layer 5: Input Validation
**What it does**: Prevents injection attacks and malformed data

**Mechanisms:**
- Schema validation for all inputs
- SQL injection prevention (parameterized queries)
- XSS prevention (output escaping)
- CSRF token validation
- File upload restrictions

**Example:**
```php
$validated = $request->validate([
    'tenant_id' => 'required|integer|exists:tenants,id',
    'name' => 'required|string|max:100',
    'email' => 'required|email|unique:users,email'
]);
```

#### Layer 6: Rate Limiting
**What it does**: Prevents abuse and brute force attacks

**Mechanisms:**
- Login attempts: 5 per 15 minutes
- API calls: 100 per minute per user
- Admin actions: 20 per minute
- Export operations: 5 per hour

**Example:**
```php
RateLimiter::attempt('login:' . $request->ip(), 5, function() {
    // Attempt login
}, 900); // 15 minutes
```

#### Layer 7: Audit & Monitoring
**What it does**: Detects anomalies and provides accountability

**Mechanisms:**
- All privileged actions logged
- Anomaly detection (unusual access patterns)
- Real-time alerts for critical operations
- Immutable audit trail

---

## API Design Principles

### RESTful Conventions

**Resource naming:**
```
GET    /api/tenants              List tenants (admin only)
POST   /api/tenants              Create tenant (admin only)
GET    /api/tenants/{id}         Get tenant details
PUT    /api/tenants/{id}         Update tenant
DELETE /api/tenants/{id}         Delete tenant (admin only)

GET    /api/v1/products          List products (tenant-scoped)
POST   /api/v1/products          Create product
GET    /api/v1/products/{id}     Get product
PUT    /api/v1/products/{id}     Update product
DELETE /api/v1/products/{id}     Delete product
```

### Standard Response Schema

**Success response:**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "name": "Product Name"
  },
  "meta": {
    "timestamp": "2025-01-22T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

**List response with pagination:**
```json
{
  "success": true,
  "data": [
    {"id": 1, "name": "Item 1"},
    {"id": 2, "name": "Item 2"}
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 20,
    "total": 150,
    "last_page": 8
  },
  "meta": {
    "timestamp": "2025-01-22T10:30:00Z",
    "request_id": "req_abc124"
  }
}
```

**Error response:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "The given data was invalid.",
    "details": {
      "email": ["The email field is required."],
      "name": ["The name must be at least 3 characters."]
    }
  },
  "meta": {
    "timestamp": "2025-01-22T10:30:00Z",
    "request_id": "req_abc125"
  }
}
```

### Error Codes

```
Authentication Errors (401)
├── AUTH_REQUIRED          No authentication provided
├── AUTH_INVALID           Invalid credentials
├── AUTH_EXPIRED           Session/token expired
└── ACCOUNT_SUSPENDED      Account is suspended

Authorization Errors (403)
├── PERMISSION_DENIED      Missing required permission
├── TENANT_ACCESS_DENIED   Cannot access this tenant
├── ROLE_REQUIRED          Wrong role for this operation
└── MFA_REQUIRED           MFA verification needed

Resource Errors (404)
├── RESOURCE_NOT_FOUND     Requested resource doesn't exist
└── TENANT_NOT_FOUND       Tenant doesn't exist

Validation Errors (422)
├── VALIDATION_FAILED      Input validation failed
├── DUPLICATE_ENTRY        Unique constraint violation
└── INVALID_STATE          Operation not allowed in current state

Rate Limiting (429)
└── RATE_LIMIT_EXCEEDED    Too many requests

Server Errors (500)
├── INTERNAL_ERROR         Unexpected server error
└── SERVICE_UNAVAILABLE    Temporary service disruption
```

### API Versioning

**URL-based versioning:**
```
/api/v1/products   (Current stable)
/api/v2/products   (New version with breaking changes)
```

**Header-based versioning (alternative):**
```
Accept: application/vnd.api+json; version=1
```

### Idempotency

**Idempotency keys for write operations:**
```bash
POST /api/v1/orders
Headers:
  Idempotency-Key: order_20250122_abc123
  
# Repeating the same request with the same key returns the original result
# Prevents duplicate orders from network retries
```

**Implementation:**
```php
class IdempotencyMiddleware {
    public function handle(Request $request, Closure $next) {
        $key = $request->header('Idempotency-Key');
        
        if ($key && $request->isMethod('POST')) {
            // Check if we've seen this key before
            $cached = Cache::get("idempotency:$key");
            
            if ($cached) {
                return response()->json($cached['response'], $cached['status']);
            }
            
            // Process request
            $response = $next($request);
            
            // Cache the response for 24 hours
            Cache::put("idempotency:$key", [
                'response' => $response->getData(),
                'status' => $response->getStatusCode()
            ], 86400);
            
            return $response;
        }
        
        return $next($request);
    }
}
```

### Tenant Context in APIs

**Option 1: Subdomain routing**
```
https://acme.platform.com/api/v1/products
→ Tenant resolved from subdomain
```

**Option 2: Header-based**
```
GET /api/v1/products
Headers:
  X-Tenant-ID: tenant_abc123
```

**Option 3: JWT metadata**
```
Authorization: Bearer <jwt>
# JWT payload contains tenant_id
```

---

## Data Access Patterns

### Repository Layer Architecture

**Base Repository (Abstract):**
```php
abstract class BaseRepository {
    protected Model $model;
    protected bool $tenantScoped = true;
    
    public function all(array $filters = []): Collection {
        return $this->buildQuery($filters)->get();
    }
    
    public function find(int $id): ?Model {
        return $this->buildQuery()->find($id);
    }
    
    public function create(array $data): Model {
        $this->validateTenantScope($data);
        return $this->model->create($data);
    }
    
    protected function buildQuery(array $filters = []): Builder {
        $query = $this->model->newQuery();
        
        // Automatic tenant scoping
        if ($this->tenantScoped) {
            $query->where('tenant_id', TenantContext::current());
        }
        
        // Apply filters
        foreach ($filters as $key => $value) {
            if (in_array($key, $this->getFilterable())) {
                $query->where($key, $value);
            }
        }
        
        return $query;
    }
    
    abstract protected function getFilterable(): array;
}
```

**Tenant-Scoped Repository Example:**
```php
class ProductRepository extends BaseRepository {
    protected $model = Product::class;
    protected $tenantScoped = true;
    
    protected function getFilterable(): array {
        return ['category_id', 'status', 'in_stock'];
    }
    
    public function findBySku(string $sku): ?Product {
        return $this->buildQuery()
            ->where('sku', $sku)
            ->first();
    }
    
    public function getLowStock(int $threshold = 10): Collection {
        return $this->buildQuery()
            ->where('stock_quantity', '<=', $threshold)
            ->where('status', 'active')
            ->get();
    }
}
```

**Cross-Tenant Repository (Admin Only):**
```php
class TenantRepository extends BaseRepository {
    protected $model = Tenant::class;
    protected $tenantScoped = false;  // Not tenant-scoped itself
    
    public function getAllWithStats(): Collection {
        // Only callable by admins (enforced by controller/service)
        return $this->model
            ->withCount(['users', 'products', 'orders'])
            ->get();
    }
    
    public function getAssignedToAdmin(int $adminId): Collection {
        return $this->model
            ->join('superadmin_tenant_assignments', 'tenants.id', '=', 'superadmin_tenant_assignments.tenant_id')
            ->where('superadmin_tenant_assignments.superadmin_id', $adminId)
            ->select('tenants.*')
            ->get();
    }
}
```

### Query Optimization

**N+1 Query Prevention:**
```php
// Bad: N+1 problem
$products = Product::all();
foreach ($products as $product) {
    echo $product->category->name;  // Separate query for each!
}

// Good: Eager loading
$products = Product::with('category')->get();
foreach ($products as $product) {
    echo $product->category->name;  // Already loaded
}
```

**Database Indexes:**
```sql
-- Tenant-scoped queries always filter by tenant_id first
CREATE INDEX idx_products_tenant_sku ON products(tenant_id, sku);
CREATE INDEX idx_orders_tenant_status ON orders(tenant_id, status, created_at);
CREATE INDEX idx_users_tenant_email ON users(tenant_id, email);

-- Admin queries across tenants
CREATE INDEX idx_tenants_status ON tenants(status);
CREATE INDEX idx_tenants_created ON tenants(created_at);
```

### Caching Strategy

**Cache Patterns:**

1. **Tenant-scoped cache keys**
```php
$cacheKey = "tenant:{$tenantId}:products:active";
$products = Cache::remember($cacheKey, 3600, function() {
    return Product::where('status', 'active')->get();
});
```

2. **Cache invalidation on mutation**
```php
public function updateProduct(int $id, array $data): Product {
    $product = $this->find($id);
    $product->update($data);
    
    // Invalidate relevant caches
    Cache::forget("tenant:{$product->tenant_id}:products:active");
    Cache::forget("tenant:{$product->tenant_id}:product:{$id}");
    
    return $product;
}
```

3. **User-specific caching**
```php
$cacheKey = "user:{$userId}:permissions";
$permissions = Cache::remember($cacheKey, 3600, function() use ($userId) {
    return User::find($userId)->permissions()->pluck('code');
});
```

---

## Audit & Compliance

### Audit Log Schema

```sql
CREATE TABLE audit_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    
    -- Who performed the action
    actor_type ENUM('root', 'super_admin', 'tenant_user', 'customer', 'system'),
    actor_id BIGINT,
    
    -- What action was performed
    action VARCHAR(100) NOT NULL,           -- e.g., 'tenant.suspend'
    resource_type VARCHAR(50),               -- e.g., 'Tenant'
    resource_id BIGINT,
    
    -- Context
    tenant_id BIGINT NULL,                   -- NULL for platform actions
    
    -- Change tracking
    old_values JSON NULL,
    new_values JSON NULL,
    metadata JSON NULL,                      -- Additional context
    
    -- Request context
    ip_address VARCHAR(45),
    user_agent TEXT,
    request_id VARCHAR(100),
    
    -- Timing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_actor (actor_type, actor_id),
    INDEX idx_action (action, created_at),
    INDEX idx_resource (resource_type, resource_id),
    INDEX idx_tenant (tenant_id, created_at)
);
```

### What Gets Audited

**Always audited:**
- All admin panel actions
- Tenant creation, modification, deletion, suspension
- User invitation, suspension, reactivation
- Permission grants and revocations
- Subscription changes
- Data exports (especially PII)
- Impersonation start/stop
- Configuration changes
- Cross-tenant queries

**Tenant-level auditing (optional, configurable):**
- User login/logout
- Critical data modifications (orders, payments)
- Settings changes
- User management within tenant

### Audit Log Implementation

```php
class AuditLogger {
    public static function log(array $params): void {
        $actor = Auth::user();
        
        DB::table('audit_logs')->insert([
            'actor_type' => self::getActorType($actor),
            'actor_id' => $actor?->id,
            'action' => $params['action'],
            'resource_type' => $params['resource_type'] ?? null,
            'resource_id' => $params['resource_id'] ?? null,
            'tenant_id' => $params['tenant_id'] ?? null,
            'old_values' => json_encode($params['old_values'] ?? null),
            'new_values' => json_encode($params['new_values'] ?? null),
            'metadata' => json_encode($params['metadata'] ?? []),
            'ip_address' => request()->ip(),
            'user_agent' => request()->userAgent(),
            'request_id' => request()->id(),
            'created_at' => now()
        ]);
    }
    
    public static function logTenantAction(string $action, Model $model, array $metadata = []): void {
        self::log([
            'action' => $action,
            'resource_type' => class_basename($model),
            'resource_id' => $model->id,
            'tenant_id' => $model->tenant_id ?? TenantContext::current(),
            'new_values' => $model->getAttributes(),
            'metadata' => $metadata
        ]);
    }
}
```

**Usage Examples:**
```php
// Suspending a tenant
AuditLogger::log([
    'action' => 'tenant.suspend',
    'resource_type' => 'Tenant',
    'resource_id' => $tenant->id,
    'tenant_id' => $tenant->id,
    'old_values' => ['status' => 'active'],
    'new_values' => ['status' => 'suspended'],
    'metadata' => ['reason' => 'Payment failure']
]);

// Granting permission to super admin
AuditLogger::log([
    'action' => 'permission.grant',
    'resource_type' => 'User',
    'resource_id' => $superAdmin->id,
    'metadata' => [
        'permission' => 'tenant.delete',
        'granted_by' => Auth::id()
    ]
]);
```

### Compliance Features

**GDPR Support:**
- Data export: Generate complete user data dump
- Right to erasure: Anonymize user records
- Audit trail: Track all data access and modifications
- Consent management: Track permission grants

**SOC 2 Readiness:**
- Immutable audit logs
- Access control documentation
- Incident response procedures
- Change management tracking

---

## Operational Safeguards

### Feature Flags

**Use Cases:**
- Gradual rollouts of new features
- A/B testing
- Emergency killswitches
- Tenant-specific feature enablement

**Implementation:**
```php
class FeatureFlag {
    public static function isEnabled(string $feature, ?int $tenantId = null): bool {
        // Check global flag
        $globalEnabled = Cache::remember("feature:$feature", 3600, function() use ($feature) {
            return DB::table('feature_flags')
                ->where('name', $feature)
                ->value('enabled') ?? false;
        });
        
        if (!$globalEnabled) {
            return false;
        }
        
        // Check tenant-specific override
        if ($tenantId) {
            return DB::table('tenant_features')
                ->where('tenant_id', $tenantId)
                ->where('feature', $feature)
                ->value('enabled') ?? true;  // Default to global setting
        }
        
        return true;
    }
}

// Usage
if (FeatureFlag::isEnabled('new_checkout_flow', $tenant->id)) {
    return $this->newCheckout($order);
} else {
    return $this->legacyCheckout($order);
}
```

### Database Migration Safety

**Migration Checklist:**
1. Test on staging with production-like data volume
2. Estimate duration for production dataset
3. Plan maintenance window or zero-downtime strategy
4. Prepare rollback script
5. Monitor query performance post-migration

**Safe Migration Patterns:**

```php
// Bad: Locking table for too long
Schema::table('products', function (Blueprint $table) {
    $table->string('new_column')->after('name');
});

// Good: Add column as nullable first, backfill later
Schema::table('products', function (Blueprint $table) {
    $table->string('new_column')->nullable()->after('name');
});

// Then backfill in chunks
DB::table('products')
    ->whereNull('new_column')
    ->chunkById(1000, function ($products) {
        foreach ($products as $product) {
            DB::table('products')
                ->where('id', $product->id)
                ->update(['new_column' => $this->computeValue($product)]);
        }
        sleep(1);  // Prevent overwhelming database
    });
```

### Monitoring & Alerting

**Critical Metrics:**
- API response times (p50, p95, p99)
- Error rates by endpoint
- Authentication failures
- Permission denials
- Database query times
- Queue depths
- Cache hit rates

**Alert Conditions:**
```yaml
alerts:
  - name: High error rate
    condition: error_rate > 5%
    duration: 5 minutes
    severity: critical
    
  - name: Slow API responses
    condition: p95_response_time > 2s
    duration: 10 minutes
    severity: warning
    
  - name: Failed authentication spike
    condition: auth_failures > 100
    duration: 5 minutes
    severity: critical
    
  - name: Permission denial spike
    condition: permission_denials > 50
    duration: 5 minutes
    severity: warning
    notify: security_team
```

### Backup & Disaster Recovery

**Backup Strategy:**
- Database: Daily full backups + continuous transaction logs
- File storage: Daily snapshots
- Audit logs: Replicated to separate storage (immutable)
- Retention: 30 days hot, 1 year cold storage

**Recovery Procedures:**
1. Detect incident
2. Assess scope (single tenant vs platform-wide)
3. Restore from backup to staging
4. Validate data integrity
5. Restore to production
6. Verify functionality
7. Communicate to affected tenants

---

## Development Guidelines

### When Adding a New Feature

**Step 1: Determine the Correct Panel**

Ask these questions:
- Who will use this feature?
  - Tenant staff → Tenant App
  - Platform staff → Admin Panel
  - End customers → Customer Portal
  
- What data does it access?
  - Single tenant data → Tenant App
  - Multiple tenants → Admin Panel (with permission checks)
  - Customer's own data → Customer Portal
  
- What permissions are needed?
  - Standard business operations → Tenant App
  - Platform management → Admin Panel
  - Read-only personal data → Customer Portal

**Step 2: Design the Permission Model**

For Admin Panel features:
```php
// Define new permissions
'feature.create'    => 'Create feature',
'feature.edit'      => 'Edit feature',
'feature.delete'    => 'Delete feature',
'feature.view_all'  => 'View all tenant features',
```

For Tenant App features:
```php
// Use role-based checks
if ($user->role === 'owner' || $user->role === 'manager') {
    // Allow action
}
```

**Step 3: Implement Data Access Layer**

```php
// Repository
class FeatureRepository extends BaseRepository {
    protected $model = Feature::class;
    protected $tenantScoped = true;  // Critical!
    
    public function findActive(): Collection {
        return $this->buildQuery()
            ->where('status', 'active')
            ->get();
    }
}

// Service
class FeatureService {
    public function create(array $data): Feature {
        // Validate tenant context
        $tenantId = TenantContext::current();
        if (!$tenantId) {
            throw new MissingTenantException();
        }
        
        // Inject tenant ID
        $data['tenant_id'] = $tenantId;
        
        // Create via repository
        $feature = $this->repository->create($data);
        
        // Audit
        AuditLogger::logTenantAction('feature.created', $feature);
        
        return $feature;
    }
}
```

**Step 4: Implement API Endpoint**

```php
class FeatureController extends Controller {
    public function __construct(
        private FeatureService $service,
        private PermissionChecker $permissions
    ) {}
    
    public function index(Request $request): JsonResponse {
        // Tenant context already injected by middleware
        $features = $this->service->getAll($request->query());
        
        return response()->json([
            'success' => true,
            'data' => $features
        ]);
    }
    
    public function store(Request $request): JsonResponse {
        // Permission check (tenant-level)
        if (!$this->permissions->check(Auth::user(), 'feature.create')) {
            return response()->json([
                'success' => false,
                'error' => ['code' => 'PERMISSION_DENIED']
            ], 403);
        }
        
        // Validate input
        $validated = $request->validate([
            'name' => 'required|string|max:100',
            'description' => 'nullable|string'
        ]);
        
        // Create
        $feature = $this->service->create($validated);
        
        return response()->json([
            'success' => true,
            'data' => $feature
        ], 201);
    }
}
```

**Step 5: Add Tests**

```php
class FeatureControllerTest extends TestCase {
    public function test_user_can_create_feature_in_own_tenant(): void {
        $tenant = Tenant::factory()->create();
        $user = User::factory()->for($tenant)->create();
        
        $this->actingAs($user)
            ->postJson('/api/v1/features', [
                'name' => 'Test Feature'
            ])
            ->assertStatus(201)
            ->assertJsonPath('data.tenant_id', $tenant->id);
    }
    
    public function test_user_cannot_create_feature_in_other_tenant(): void {
        $tenant1 = Tenant::factory()->create();
        $tenant2 = Tenant::factory()->create();
        $user = User::factory()->for($tenant1)->create();
        
        // Attempt to inject other tenant's ID
        $this->actingAs($user)
            ->postJson('/api/v1/features', [
                'name' => 'Test Feature',
                'tenant_id' => $tenant2->id  // Should be rejected
            ])
            ->assertStatus(403);  // Or stripped and uses $tenant1->id
    }
    
    public function test_super_admin_can_view_all_features(): void {
        $admin = User::factory()->superAdmin()->create();
        $tenant1 = Tenant::factory()->create();
        $tenant2 = Tenant::factory()->create();
        
        // Assign admin to both tenants
        $admin->assignedTenants()->attach([$tenant1->id, $tenant2->id]);
        
        Feature::factory()->for($tenant1)->create();
        Feature::factory()->for($tenant2)->create();
        
        $this->actingAs($admin)
            ->getJson('/admin/features')
            ->assertStatus(200)
            ->assertJsonCount(2, 'data');
    }
}
```

### Code Review Checklist

Before merging any code that touches tenant data or permissions:

- [ ] Tenant scoping is enforced in all queries
- [ ] Permission checks are present on mutations
- [ ] Input validation prevents tenant ID injection
- [ ] Audit logging is added for privileged actions
- [ ] Tests cover cross-tenant access prevention
- [ ] API responses don't leak other tenant data
- [ ] Error messages don't expose sensitive information
- [ ] Database indexes support tenant-scoped queries

---

## Migration & Evolution Strategy

### Adding a New Permission

1. Add permission to database:
```sql
INSERT INTO permissions (code, category, description, risk_level) 
VALUES ('feature.export', 'Data Management', 'Export feature data', 'medium');
```

2. Grant to existing roles (if needed):
```php
// Migration
$permission = Permission::where('code', 'feature.export')->first();
$superAdmins = User::where('role', 'super_admin')->get();

foreach ($superAdmins as $admin) {
    $admin->permissions()->attach($permission->id, [
        'granted_by' => 1,  // Root
        'granted_at' => now()
    ]);
}
```

3. Enforce in code:
```php
if (!$user->hasPermission('feature.export')) {
    abort(403);
}
```

### Migrating from Single-Tenant to Multi-Tenant

**Step 1: Add tenant_id column**
```php
Schema::table('products', function (Blueprint $table) {
    $table->unsignedBigInteger('tenant_id')->nullable()->after('id');
    $table->foreign('tenant_id')->references('id')->on('tenants');
    $table->index(['tenant_id', 'created_at']);
});
```

**Step 2: Backfill tenant associations**
```php
// Assuming you can determine tenant from existing data
$defaultTenant = Tenant::first();

DB::table('products')
    ->whereNull('tenant_id')
    ->update(['tenant_id' => $defaultTenant->id]);
```

**Step 3: Make column non-nullable**
```php
Schema::table('products', function (Blueprint $table) {
    $table->unsignedBigInteger('tenant_id')->nullable(false)->change();
});
```

**Step 4: Update queries to be tenant-scoped**
```php
// Before
Product::all();

// After
Product::where('tenant_id', TenantContext::current())->get();

// Better: Use repository pattern
$this->productRepository->all();  // Automatically tenant-scoped
```

### Decomposing into Microservices

If the platform grows to require microservices:

**Shared Authentication Service:**
- Issues JWT tokens with tenant context
- Validates tokens for all services
- Maintains user and permission data

**Tenant Isolation Per Service:**
- Each service enforces tenant scoping
- Database-per-tenant or schema-per-tenant patterns
- Message queues include tenant context in headers

**Example Token Structure:**
```json
{
  "sub": "user_12345",
  "tenant_id": "tenant_abc",
  "role": "tenant_user",
  "permissions": ["product.create", "product.edit"],
  "iss": "auth.platform.com",
  "exp": 1736000000
}
```

**Service-to-Service Communication:**
```http
POST /internal/inventory/reserve
Headers:
  Authorization: Bearer <service-token>
  X-Tenant-ID: tenant_abc
  X-Request-ID: req_xyz
  
Body:
{
  "product_id": 123,
  "quantity": 5
}
```

---

## Summary

This architecture provides:

✅ **Security by Design**: Multiple layers prevent unauthorized access  
✅ **Clear Boundaries**: Each panel has distinct purpose and security model  
✅ **Tenant Isolation**: Guaranteed data separation across organizations  
✅ **Auditability**: Complete trail of all privileged operations  
✅ **Scalability**: Patterns support growth in tenants and features  
✅ **Developer Clarity**: Consistent patterns reduce errors  
✅ **Operational Safety**: Feature flags, monitoring, and rollback capabilities  

### Key Takeaways for Developers

1. **Always identify the panel first** before writing any code
2. **Tenant scoping is mandatory** for all tenant-owned data
3. **Permission checks happen server-side**, not just in UI
4. **Audit all privileged operations** without exception
5. **Test cross-tenant access prevention** in every feature
6. **Input validation prevents injection** of tenant IDs or permissions
7. **Root access is logged**, not exempt from audit
8. **Customer portal is hostile territory** — minimal scope, maximum security

### Evolution Guidelines

As the platform grows:
- Add permissions, never remove security layers
- Introduce new panels if needed, don't blur boundaries
- Migrate features carefully with feature flags
- Test performance with production-scale data
- Monitor audit logs for anomalies
- Review and rotate root credentials regularly

This architecture is designed to protect your users, your platform, and your business as you scale from startup to enterprise.

---

## Appendix: Quick Reference

### Common Permission Codes
```
tenant.*          Tenant management (create, suspend, delete)
superadmin.*      Admin user management
subscription.*    Subscription and billing
user.impersonate  Impersonate tenant users
audit.*           Audit log access
config.system     Platform configuration
reports.cross_tenant  Cross-tenant analytics
data.export       Export tenant data
```

### Middleware Stack (Typical Request)
```
1. CORS
2. Rate Limiting
3. Authentication
4. CSRF Protection
5. Role Guard
6. Tenant Context Injection
7. Permission Check
8. Input Validation
9. Controller Action
10. Audit Logging
```

### Database Table Naming
```
tenants                      Platform tenants
users                        All users (tenants + admins + customers)
permissions                  Permission definitions
user_permissions             User-permission assignments
superadmin_tenant_assignments  Tenant access for super admins
audit_logs                   Audit trail
feature_flags                Feature flag config
tenant_features              Tenant-specific feature overrides
sessions                     User sessions
```

### Environment Variables (Example)
```env
# Security
JWT_SECRET=<random-256-bit-key>
SESSION_LIFETIME=120
MFA_REQUIRED_FOR_ROOT=true

# Tenant
DEFAULT_TENANT_QUOTA=10000
TENANT_ISOLATION_MODE=strict

# Audit
AUDIT_LOG_RETENTION_DAYS=730
AUDIT_LOG_EXPORT_PERMISSION=audit.export

# Rate Limiting
RATE_LIMIT_LOGIN=5
RATE_LIMIT_API=100
RATE_LIMIT_ADMIN=20
```

---

**Document Version**: 2.0  
**Last Updated**: January 22, 2025  
**Maintained By**: Platform Architecture Team
    // 2. Queue for sync
    await db.insert('sync_queue', {
        entity_type: 'order',
        operation: 'create',
        payload: { ...data }
    });
    
    // 3. Show to user immediately (optimistic update)
    // 4. Sync when online (background sync)
    
    return localId;
}

// Conflict resolution strategy
function resolveConflict(local, remote) {
    // Strategy 1: Last-write-wins (for simple fields)
    // Strategy 2: Custom resolution (for inventory/complex data)
    return {
        timestamp: max(local.timestamp, remote.timestamp),
        ...remote,  // Server version typically wins
    };
}
```

### Key Metrics for Mobile

- Offline duration: How long before sync required
- Sync latency: Ideally < 30 seconds
- Data freshness: Age of local data
- Battery impact: Minimize background syncing
- Cache hit rate: Reduce server requests

### Best Practices

- Don't sync on every change (batch)
- Use background sync (native APIs)
- Compress JSON payloads
- Cache images locally
- Minimize network requests
- Provide clear "syncing..." UI feedback

---

## Feature Flags & Safe Deployment

### Flag Types

```php
// Boolean: Enable/disable
Feature::isEnabled('advanced_reporting')

// Percentage: Gradual rollout (5%, 25%, 100%)
Feature::isEnabledFor('dashboard.v2', $tenant->id)

// Tenant-specific: Beta programs
Feature::isEnabledForTenant('new_feature', $tenantId)

// Role-based: Admin-only features
Feature::isEnabledForRole('export_data', 'super_admin')
```

### Database Schema

```sql
CREATE TABLE feature_flags (
    id BIGINT PRIMARY KEY,
    code VARCHAR(255) UNIQUE,
    type ENUM('boolean', 'percentage', 'tenant_specific', 'role_based'),
    enabled BOOLEAN,
    percentage_value INT,
    metadata JSON,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE feature_flag_tenants (
    feature_flag_id BIGINT,
    tenant_id BIGINT,
    enabled BOOLEAN,
    PRIMARY KEY (feature_flag_id, tenant_id)
);
```

### Rollout Strategy

1. **Phase 1**: Enable for internal testing (0%)
2. **Phase 2**: 5% of tenants (early adopters, monitor)
3. **Phase 3**: 25% of tenants (validate at scale)
4. **Phase 4**: 100% of tenants (full rollout)
5. **Phase 5**: Remove flag (cleanup)

Each phase: Monitor error rates, audit logs, support tickets

---

## Monitoring, Logging & Alerting

### Key Metrics

**Security Metrics**
- Failed auth attempts (spike = attack)
- Permission denials (unusual = misconfiguration)
- Cross-tenant access attempts (should be 0)
- Admin actions (especially impersonation)

**Performance Metrics**
- API response time (p50, p95, p99)
- Database query time
- Cache hit rate
- Sync latency

**Business Metrics**
- Active tenants/users
- Feature usage
- Support ticket volume

### Logging Format

```json
{
  "timestamp": "2025-01-23T10:30:00Z",
  "level": "ERROR",
  "service": "auth-api",
  "event": "permission_denied",
  "user_id": "user_123",
  "tenant_id": "tenant_abc",
  "request_id": "req_xyz",
  "message": "User lacks permission",
  "context": {
    "permission_required": "tenant.create",
    "user_role": "super_admin"
  }
}
```

### What to Log
✅ All auth attempts (success + failure)
✅ All permission checks (failures especially)
✅ All admin actions
✅ All data modifications (for audit)
✅ All errors with context

### What NOT to Log
❌ Passwords
❌ API keys
❌ Payment card data
❌ PII (truncate or hash)
❌ Large payloads

### Alert Thresholds

**Critical**:
- Auth service down
- Database connection lost
- Cross-tenant data access detected

**Warning**:
- Auth failures > 50/minute
- API response time > 2 seconds
- Cache hit rate < 70%

---

## Data Privacy & Retention

### For Compliance (GDPR, etc.)

#### Right to Access
- Tenants can request all data about a user
- Endpoint: `GET /api/users/{id}/export`
- Format: JSON/CSV
- Timeline: 30 days

#### Right to Deletion
- Soft delete (anonymize) vs hard delete
- Retain some data for compliance (transaction logs)
- Cannot delete audit logs

### Data Retention Policy

```
Active Tenant Data: Indefinite
├── User data: As long as tenant exists
├── Transaction data: 7 years (tax/compliance)
├── Audit logs: 2 years

Deleted Tenant Data: Per compliance
├── Anonymized user data: 30 days
├── Audit logs: 2 years
├── Transaction records: 7 years
```

### Implementation

```php
// Soft delete with anonymization
function deleteUser(User $user) {
    $user->update([
        'email' => 'deleted-' . md5($user->id) . '@example.com',
        'name' => 'Deleted User',
        'phone' => null,
        'deleted_at' => now()
    ]);
    
    // Schedule hard delete after 30 days
    DeleteUser::dispatch($user->id)->delay(now()->addDays(30));
}

// Hard delete (no recovery)
function permanentlyDeleteUser(User $user) {
    $user->orders()->delete();
    $user->sessions()->delete();
    
    // Anonymize audit records
    AuditLog::where('user_id', $user->id)
        ->update(['user_id' => null, 'user_name' => 'deleted-user']);
    
    $user->delete();
}
```

---

## Disaster Recovery & Backups

### Backup Strategy

**Frequency**: Every 6 hours (daily for small deployments)
**Storage**: Primary + secondary (off-site)
**Retention**: 30 days daily, 90 days weekly, 1 year monthly

### Recovery Objectives

| Scenario | RTO | RPO |
|---|---|---|
| Data corruption | < 1 hour | < 6 hours |
| Database failure | < 4 hours | < 6 hours |
| Regional failure | < 2 hours | < 1 hour |

### Validation

- [ ] Database restore (monthly)
- [ ] Failover procedures (quarterly)
- [ ] Data export/import (quarterly)

---

## Common Implementation Mistakes

### ❌ Mistake 1: Forgetting Tenant Scoping

```php
// WRONG: Forgets tenant scoping
$orders = Order::where('status', 'pending')->get();

// RIGHT: Includes tenant context
$orders = Order::where('tenant_id', TenantContext::current())
               ->where('status', 'pending')
               ->get();
```

**Result**: User sees another tenant's data

### ❌ Mistake 2: Validating Tenant ID from User Input

```php
// WRONG: Trusting user's tenant_id
$tenantId = $request->input('tenant_id');

// RIGHT: Using authenticated context
$tenantId = TenantContext::current();
```

**Result**: User can request any tenant's data

### ❌ Mistake 3: Permission Checks Only in UI

```php
// WRONG: Only frontend validates
if (user.canDeleteUser) showDeleteButton();

// RIGHT: Server-side mandatory
public function deleteUser(Request $request) {
    if (!$request->user()->hasPermission('user.delete')) {
        abort(403);
    }
}
```

**Result**: User accesses endpoint directly via API

### ❌ Mistake 4: Not Validating Tenant Assignments

```php
// WRONG: Assumes admin has access
$data = Tenant::find($tenantId)->data();

// RIGHT: Check assignment
if (!auth()->user()->canAccessTenant($tenantId)) {
    abort(403);
}
```

**Result**: Super admin accesses unauthorized tenants

### ❌ Mistake 5: Leaking Tenant IDs in Errors

```php
// WRONG: Reveals other tenant exists
"Tenant ABC123 not found"

// RIGHT: Generic error
"Resource not found or access denied"
```

**Result**: Information disclosure

---

## Industry-Specific Patterns

### Healthcare (Medic8)
- HIPAA-equivalent audit logs for patient data access
- Never show sensitive data in error logs
- Multi-provider roles (Doctor, Nurse, Receptionist)
- Offline prescription support

### Legal (KesiLex)
- Case confidentiality enforcement
- Lawyer-client privilege protection
- Document immutability for compliance
- Complete version history

### Education (BrightSoma)
- Special handling for minors' data
- Complex role matrix (Parent, Student, Teacher)
- Gradebook privacy (aggregate data only)
- Performance metrics with permission checks

### Franchise (Maduuka)
- Multi-location support (Branch independence)
- HQ visibility (Corporate sees all branches)
- Inventory transfers logged
- Cross-branch permission boundaries

---

## Code Review Checklist

Before merging any code touching tenant data or permissions:

- [ ] Tenant scoping enforced in all queries
- [ ] Permission checks present on mutations
- [ ] Input validation prevents tenant ID injection
- [ ] Audit logging added for privileged actions
- [ ] Tests cover cross-tenant access prevention
- [ ] API responses don't leak other tenant data
- [ ] Error messages don't expose sensitive information
- [ ] Database indexes support tenant-scoped queries
- [ ] Cache keys include tenant_id
- [ ] Rate limiting appropriate for panel
- [ ] Feature flags tested for all variations

---

## Testing Requirements

### Essential Test Cases

```php
// Permission isolation tests
public function test_user_cannot_access_other_tenant_data() {
    $user = User::factory()->for($tenant1)->create();
    $order = Order::factory()->for($tenant2)->create();
    
    $this->actingAs($user)
        ->getJson("/api/orders/{$order->id}")
        ->assertStatus(403);
}

// Cross-tenant prevention
public function test_cannot_modify_tenant_id_in_request() {
    $user = User::factory()->for($tenant1)->create();
    
    $this->actingAs($user)
        ->postJson('/api/orders', [
            'tenant_id' => $tenant2->id,  // Attempt injection
            'amount' => 100
        ])
        ->assertStatus(403);  // Rejected
}

// Admin permission tests
public function test_super_admin_can_view_assigned_tenants_only() {
    $admin = User::factory()->superAdmin()->create();
    $tenant1 = Tenant::factory()->create();
    $tenant2 = Tenant::factory()->create();
    
    // Assign to only tenant1
    $admin->assignedTenants()->attach($tenant1->id);
    
    $this->actingAs($admin)
        ->getJson("/api/tenants/{$tenant1->id}")
        ->assertStatus(200);
    
    $this->actingAs($admin)
        ->getJson("/api/tenants/{$tenant2->id}")
        ->assertStatus(403);
}
```

---

## Key Takeaways

1. **Always identify the panel first** (Tenant App, Admin Panel, Customer Portal)
2. **Tenant scoping is mandatory** for all tenant-owned data
3. **Permission checks happen server-side**, never trust UI
4. **Audit all privileged operations** without exception
5. **Test cross-tenant access prevention** in every feature
6. **Input validation prevents injection** of tenant IDs
7. **Root access is logged**, not exempt from audit
8. **Customer portal is hostile territory** — minimal scope, maximum security

---

## Next: Implementation Patterns

Use this skill as a reference when:
- Designing new feature architecture
- Implementing authentication/authorization
- Building multi-tenant features
- Ensuring compliance requirements
- Deploying to production
- Reviewing code for security

For specific database patterns, see database documentation.
For API design standards, see API documentation.
For testing strategies, see testing guide.

---

**Document Version**: 3.0 (Enhanced)
**Last Updated**: January 2025
**Applies To**: All SaaS platforms (Maduuka, Medic8, KesiLex, BrightSoma)
