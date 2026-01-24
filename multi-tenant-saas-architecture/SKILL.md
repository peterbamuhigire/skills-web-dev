---
name: multi-tenant-saas-architecture
description: "Comprehensive multi-tenant SaaS platform architecture with security, compliance, and scalability built-in. Covers three-panel separation (tenant app, admin panel, customer portal), tenant isolation patterns, authentication/authorization, error handling, mobile-first design, monitoring, and industry-specific implementations. Use when designing system architecture, implementing authentication/permissions, building multi-tenant features, ensuring compliance, or deploying to production. Includes concrete code patterns, database schemas, testing strategies, and common pitfalls to avoid."
---

# Multi-Tenant SaaS Architecture

## Quick Start: Which Panel Am I Building?

Before writing any code, identify which panel this feature belongs to:

| Panel | Purpose | Users | Data Scope | Key Constraint |
|---|---|---|---|---|
| **Tenant App** | Daily operations | Staff, employees | Single tenant, full CRUD | Must enforce tenant isolation |
| **Admin Panel** | Platform management | Platform staff | Multi-tenant, limited | Must check super admin assignments |
| **Customer Portal** | End-user access | Students, clients, consumers | Own data only | Minimal scope, maximum security |

**Critical Rule**: Every feature must start with "Which panel?" before implementation.

---

## System Architecture Overview

### Three-Panel Separation Model

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

### Design Principles

1. **Zero Trust Architecture**: Every request is authenticated, authorized, and validated
2. **Tenant Isolation by Default**: No data access without explicit tenant context
3. **Least Privilege Access**: Permissions are granular, explicit, and auditable
4. **Defense in Depth**: Multiple security layers prevent privilege escalation
5. **Audit Everything**: All privileged operations create immutable audit trails

---

## Multi-Tenant Isolation Model

### Core Rule: Tenant Context is Mandatory

**Every database query that touches tenant data must include the tenant identifier.** This is not optional. It is enforced through three mechanisms:

### 1. Middleware Layer

Tenant context is injected at request processing time:

```php
class TenantContextMiddleware {
    public function handle(Request $request, Closure $next) {
        $tenantId = $this->resolveTenant($request);
        
        if (!$tenantId && $this->requiresTenant($request)) {
            throw new UnauthorizedException('Tenant context required');
        }
        
        // Inject into request context
        $request->setTenantContext($tenantId);
        
        // Set global scope (automatic query filtering)
        TenantScope::set($tenantId);
        
        return $next($request);
    }
}
```

### 2. Repository Pattern

All data access is wrapped in repositories that enforce tenant scoping:

```php
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

Every tenant-scoped table includes tenant_id as part of the primary key strategy:

```sql
-- Every tenant-scoped table
CREATE TABLE orders (
    id BIGINT PRIMARY KEY,
    tenant_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    created_at TIMESTAMP,
    
    -- Composite indexes for performance
    INDEX idx_tenant_created (tenant_id, created_at),
    INDEX idx_tenant_user (tenant_id, user_id),
    
    -- Foreign key enforcement
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Non-tenant-scoped tables (shared across platform)
CREATE TABLE tenants (
    id BIGINT PRIMARY KEY,
    slug VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    plan VARCHAR(50),
    created_at TIMESTAMP
);
```

---

## Authentication & Authorization

### Authentication Layers

#### Layer 1: Tenant App (Session-Based)
```php
// Sessions stored in database or Redis
// Lifetime: 24-48 hours for web, 30 days for remember-me
class SessionController {
    public function login(Request $request) {
        $user = User::where('email', $request->email)->first();
        
        if (!Hash::check($request->password, $user->password)) {
            throw new AuthenticationException('Invalid credentials');
        }
        
        // Create session with tenant context
        session([
            'user_id' => $user->id,
            'tenant_id' => $user->tenant_id,
            'permissions' => $user->getPermissions()
        ]);
        
        Log::info('User logged in', ['user_id' => $user->id, 'tenant_id' => $user->tenant_id]);
    }
}
```

#### Layer 2: Admin Panel (JWT + Multi-Tenant Assignment)
```php
// JWT tokens include tenant assignments
class AdminAuthController {
    public function login(Request $request) {
        $admin = User::where('email', $request->email)
                    ->where('role', 'super_admin')
                    ->first();
        
        if (!Hash::check($request->password, $admin->password)) {
            throw new AuthenticationException('Invalid credentials');
        }
        
        // Get assigned tenants
        $assignedTenants = $admin->assignedTenants()
                                ->pluck('id')
                                ->toArray();
        
        $token = JWT::encode([
            'sub' => $admin->id,
            'role' => 'super_admin',
            'assigned_tenants' => $assignedTenants,
            'permissions' => $admin->getPermissions(),
            'iss' => config('app.url'),
            'exp' => now()->addHours(24)->timestamp
        ], config('app.secret'));
        
        return ['token' => $token];
    }
}
```

#### Layer 3: Customer Portal (Magic Links or OAuth)
```php
// Low-friction auth for end users
class CustomerAuthController {
    public function requestMagicLink(Request $request) {
        $user = User::where('email', $request->email)->first();
        
        if (!$user) {
            // Don't reveal if user exists
            return response()->json(['message' => 'Check your email']);
        }
        
        $token = bin2hex(random_bytes(32));
        Cache::put("magic_link:{$token}", $user->id, minutes: 15);
        
        Mail::send(new MagicLinkEmail($user, $token));
        
        return response()->json(['message' => 'Check your email']);
    }
    
    public function useMagicLink(Request $request) {
        $userId = Cache::pull("magic_link:{$request->token}");
        
        if (!$userId) {
            throw new AuthenticationException('Link expired or invalid');
        }
        
        $user = User::find($userId);
        
        // Create short-lived session (30 minutes)
        session(['user_id' => $user->id, 'tenant_id' => $user->tenant_id]);
        
        return redirect('/dashboard');
    }
}
```

### Permission Model: Granular and Explicit

```php
class User {
    public function hasPermission(string $permission): bool {
        // Check role-based permissions first (cached)
        if ($this->role === 'root_admin') {
            return true;  // Root has all permissions
        }
        
        // Check explicit permission assignments
        return $this->permissions()
                   ->where('code', $permission)
                   ->exists();
    }
    
    public function can(string $permission): bool {
        // Also check permission context (tenant, resource owner, etc.)
        return $this->hasPermission($permission) && 
               $this->isContextuallyAllowed($permission);
    }
}

// Usage in controllers
class OrderController {
    public function delete(Order $order) {
        $user = auth()->user();
        
        // Server-side permission check (not just UI)
        if (!$user->can('order.delete')) {
            abort(403, 'Insufficient permissions');
        }
        
        // Verify tenant isolation
        if ($order->tenant_id !== TenantContext::current()) {
            abort(403, 'Resource not found or access denied');
        }
        
        // Audit log
        Log::info('Order deleted', [
            'user_id' => $user->id,
            'order_id' => $order->id,
            'tenant_id' => $order->tenant_id
        ]);
        
        $order->delete();
    }
}
```

### Permission Categories for Admin Panel

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

---

## Error Handling & Response Consistency

### Tenant App: User-Friendly Errors

```php
// Tenant app returns helpful, user-centric errors
class OrderController {
    public function store(StoreOrderRequest $request) {
        try {
            // Business logic
        } catch (ValidationException $e) {
            return response()->json([
                'success' => false,
                'error' => [
                    'code' => 'VALIDATION_ERROR',
                    'message' => 'Please fix the following errors',
                    'details' => $e->errors()  // Per-field errors
                ]
            ], 400);
        } catch (Exception $e) {
            return response()->json([
                'success' => false,
                'error' => [
                    'code' => 'SERVER_ERROR',
                    'message' => 'Something went wrong',
                    'request_id' => request()->id()  // For support
                ]
            ], 500);
        }
    }
}

// Response format
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Please fix the following errors",
    "details": {
      "email": ["Email is already in use"],
      "phone": ["Phone number is invalid"]
    }
  },
  "request_id": "req_xyz123"
}
```

### Admin Panel: Detailed Context

```php
// Admin panel shows more detail for debugging
class TenantController {
    public function suspend(Tenant $tenant) {
        $user = auth()->user();
        
        if (!$user->hasPermission('tenant.suspend')) {
            return response()->json([
                'success' => false,
                'error' => [
                    'code' => 'PERMISSION_DENIED',
                    'message' => 'User lacks permission',
                    'missing_permission' => 'tenant.suspend',
                    'required_for' => "Suspending tenant {$tenant->slug}",
                    'suggested_action' => 'Request root admin to grant permission',
                    'audit_id' => 'audit_xyz'
                ]
            ], 403);
        }
    }
}
```

### Customer Portal: Minimal Information

```php
// Customer portal reveals nothing
class CustomerPortalController {
    public function getProfile() {
        try {
            // Logic
        } catch (Exception $e) {
            return response()->json([
                'success' => false,
                'error' => [
                    'code' => 'NOT_FOUND',
                    'message' => 'Item not found or access denied'
                ]
            ], 404);  // Also use 404 for auth failures to avoid enumeration
        }
    }
}
```

### Critical: Never Expose in Errors
- Tenant IDs or user IDs
- System internals or stack traces
- Database structure
- Third-party service details
- API implementation details

---

## Rate Limiting & DDoS Protection

### By Panel

```php
// Tenant App: Moderate limits (legitimate business users)
class RateLimitMiddleware {
    protected function limits() {
        return [
            'login' => '5 per minute per ip',
            'api' => '1000 per hour per user',
            'file_upload' => '100 per day per user',
            'search' => '30 per minute per user',
        ];
    }
}

// Admin Panel: Strict limits (fewer users, higher value)
class AdminRateLimitMiddleware {
    protected function limits() {
        return [
            'login' => '3 per minute per ip',
            'api' => '2000 per hour per admin',
            'sensitive_operations' => '10 per hour per admin',  // tenant.create, user.suspend
        ];
    }
}

// Customer Portal: Very strict (public exposure)
class CustomerRateLimitMiddleware {
    protected function limits() {
        return [
            'login' => '5 per minute per email',
            'api' => '100 per hour per user',
            'search' => '10 per minute per user',
        ];
    }
}

// Implementation with Redis
class RateLimiter {
    public function check($identifier, $limit) {
        $key = "rate_limit:{$identifier}";
        $count = Cache::increment($key);
        
        if ($count === 1) {
            Cache::expire($key, 60);  // Reset after 1 minute
        }
        
        if ($count > $limit) {
            return response()->json([
                'error' => 'Rate limit exceeded',
                'retry_after' => Cache::ttl($key)
            ], 429);
        }
    }
}
```

### Response Headers
```
RateLimit-Limit: 1000
RateLimit-Remaining: 999
RateLimit-Reset: 1735000000
```

---

## Caching Strategy

### Query Cache (Redis)

```php
// Cache expensive queries
$monthlyReport = Cache::remember(
    "tenant:{$tenantId}:monthly_report:{$month}",
    3600,  // 1 hour TTL
    fn() => $this->generateMonthlyReport($tenantId, $month)
);

// Invalidate on data change
event(new OrderCreated($order));

// In listener
class UpdateCacheOnOrderCreated {
    public function handle(OrderCreated $event) {
        Cache::forget("tenant:{$event->order->tenant_id}:monthly_report:*");
    }
}
```

### Permission Cache

```php
// Cache user permissions (invalidate on change)
$permissions = Cache::remember(
    "user:{$userId}:permissions",
    300,  // 5 minutes
    fn() => $this->loadPermissions($userId)
);

// Invalidate immediately on change
class PermissionGranted {
    public function handle($event) {
        Cache::forget("user:{$event->user->id}:permissions");
    }
}
```

### HTTP Cache

```php
// Cache public tenant data
return response()
    ->json($data)
    ->header('Cache-Control', 'public, max-age=300')  // 5 minutes
    ->header('ETag', md5(json_encode($data)));
```

### Cache Key Naming Convention
```
Format: {entity_type}:{entity_id}:{operation}
Example: tenant:123:monthly_report:2025-01
Always include tenant_id to prevent cross-tenant cache hits
```

---

## Event System & Notifications

### Event Types

```php
// User Events
event(new UserCreated($user, $tenant));       // Send welcome email
event(new UserSuspended($user));              // Revoke sessions
event(new PermissionGranted($user, $permission));  // Notify user

// Tenant Events
event(new TenantCreated($tenant));            // Initialize resources
event(new TenantSuspended($tenant));          // Disable access
event(new TenantDeleted($tenant));            // Archive data

// Data Events
event(new OrderPlaced($order));               // Send confirmation
event(new PaymentProcessed($payment));        // Update subscription
event(new QuotaExceeded($tenant));           // Notify admin
```

### Event Processing

```php
// Dispatch event
event(new UserCreated($user, $tenant));

// Listen asynchronously
class SendWelcomeEmail implements ShouldQueue {
    public function handle(UserCreated $event) {
        // Tenant context must be explicit
        Mail::send(new UserWelcomeEmail(
            $event->user,
            $event->tenant  // Critical: include tenant
        ));
    }
}

// Critical: Include tenant_id in all events
class UserCreated {
    public function __construct(
        public User $user,
        public Tenant $tenant  // Mandatory
    ) {}
}
```

### Notification Channels

- Email (primary)
- In-app notifications (dashboard)
- Webhooks (for integrations)
- SMS (for critical alerts)

### Audit Event Logging

All events are logged immediately:

```php
Log::info('Event processed', [
    'event_type' => UserCreated::class,
    'user_id' => $user->id,
    'tenant_id' => $tenant->id,
    'timestamp' => now(),
    'triggered_by' => auth()->id()
]);
```

---

## Mobile-First & Offline Considerations

**Critical for African markets with intermittent connectivity**

### Network Challenges to Handle

- Intermittent connectivity (not on/off, but fluctuating)
- Slow connections (3G, 2G in rural areas)
- High latency (200-500ms)
- Limited bandwidth

### Design Implications

1. **Minimize payloads**: Return only essential data
2. **Compress responses**: gzip by default, < 50KB per request
3. **Batch operations**: Allow bulk uploads when online
4. **Optimistic updates**: Assume success, sync later for UX
5. **Sync queue**: Queue all changes locally, sync when online

### Offline-First Database (SQLite)

```sql
-- Local SQLite mirrors server schema
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    tenant_id INTEGER,
    name TEXT,
    price REAL,
    sync_status TEXT DEFAULT 'synced',  -- synced, pending, error
    last_sync TIMESTAMP,
    local_version INTEGER
);

CREATE TABLE sync_queue (
    id INTEGER PRIMARY KEY,
    entity_type TEXT,
    entity_id INTEGER,
    operation TEXT,      -- create, update, delete
    payload JSON,
    timestamp TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending'  -- pending, synced, failed
);
```

### Sync Strategy

```javascript
// On app startup
async function syncWithServer() {
    if (!hasConnection()) return;
    
    // 1. Upload pending changes
    const queue = await getSyncQueue();
    for (const item of queue) {
        try {
            await POST(`/api/sync`, item.payload);
            await markSynced(item.id);
        } catch (e) {
            // Retry with exponential backoff
            await incrementRetry(item.id);
            if (item.retry_count > 3) {
                await markFailed(item.id);
            }
        }
    }
    
    // 2. Download latest data
    const lastSync = await getLastSyncTime();
    const updates = await GET(
        `/api/changes-since?timestamp=${lastSync}`
    );
    await applyUpdates(updates);
    
    // 3. Mark sync complete
    await setLastSyncTime(now());
}

// When user creates something while offline
async function createOrder(data) {
    // 1. Create locally
    const localId = await db.insert('orders', {
        ...data,
        sync_status: 'pending'
    });
    
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
