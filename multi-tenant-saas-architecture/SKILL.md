---
name: multi-tenant-saas-architecture
description: "Production-grade multi-tenant SaaS platform architecture with three-panel separation, zero-trust security, strict tenant isolation, and comprehensive audit trails. Use for designing multi-tenant systems, implementing tenant-scoped permissions, ensuring data isolation, and building scalable SaaS platforms."
---

# Multi-Tenant SaaS Platform Architecture

## Overview

Production-grade multi-tenant SaaS architecture with strict tenant isolation, zero-trust security, and three-panel separation.

**Core Principles:**
- Zero-trust: Every request authenticated, authorized, validated
- Tenant isolation by default: No cross-tenant data access
- Least privilege: Granular, explicit, auditable permissions
- Audit everything: Immutable audit trails for privileged operations

**See subdirectories for:**
- `references/` - Database schemas (database-schema.md), permission models (permission-model.md)
- `documentation/` - Migration patterns (migration.md)

## When to Use

✅ Multi-tenant SaaS platforms
✅ Strict tenant data isolation required
✅ Role-based permissions with admin oversight
✅ Compliance and audit trail requirements
✅ Multiple user types (internal staff, external customers)

❌ Single-tenant applications
❌ Simple CRUD apps without isolation needs
❌ Internal tools with flat permission models

## Three-Panel Architecture

```
┌──────────────────────────────────────────────────┐
│          Shared Infrastructure                   │
│  ┌───────────┬─────────────┬─────────────┐      │
│  │   Data    │  Business   │ Integration │      │
│  │  (Tenant  │   Logic     │   Layer     │      │
│  │ Isolated) │ (Scoped)    │  (External) │      │
│  └───────────┴─────────────┴─────────────┘      │
└──────────────────────────────────────────────────┘
      │              │              │
┌─────▼─────┐  ┌────▼────┐  ┌──────▼──────┐
│  Tenant   │  │  Admin  │  │  Customer   │
│    App    │  │  Panel  │  │   Portal    │
│           │  │         │  │             │
│ Daily Ops │  │Platform │  │  External   │
│ (Scoped)  │  │  Mgmt   │  │   Access    │
└───────────┘  └─────────┘  └─────────────┘
```

### 1. Tenant App
**Purpose:** Daily operations within a single tenant
**Users:** Tenant owners, managers, staff
**Auth:** Session-based (web), JWT (mobile/API)
**Scope:** Single tenant only, cannot access other tenants

**Key Constraints:**
- All queries include `WHERE tenant_id = ?`
- Cannot modify platform settings
- Cannot create/suspend other tenants
- All operations logged for tenant audit

### 2. Admin Panel
**Purpose:** Platform management and oversight
**Users:** Super admins, platform operators
**Auth:** MFA required, IP restrictions
**Scope:** Cross-tenant with audit trails

**Capabilities:**
- Create/suspend tenants
- Manage platform users
- Impersonate tenant users (logged)
- View cross-tenant analytics
- Configure platform settings

**Critical Rules:**
- Every action creates audit log
- Impersonation requires justification
- Production data access logged
- All changes require approval workflow

### 3. Customer Portal
**Purpose:** External customer self-service
**Users:** End customers (outside tenant org)
**Auth:** Email/phone verification, social login
**Scope:** Own records only, read-mostly

**Examples:**
- Order tracking
- Invoice viewing
- Support ticket submission
- Account management

## Tenant Isolation Model

### Database-Level Isolation

**Option 1: Shared Database (Row-Level Tenant ID)**
```sql
-- Every table has tenant_id
CREATE TABLE orders (
    id BIGINT PRIMARY KEY,
    tenant_id BIGINT NOT NULL,
    -- other fields
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    INDEX idx_tenant (tenant_id)
);

-- ALL queries MUST include tenant_id
SELECT * FROM orders WHERE tenant_id = ? AND id = ?;
```

**Option 2: Schema-Per-Tenant**
```sql
-- PostgreSQL: Separate schema per tenant
CREATE SCHEMA tenant_123;
CREATE TABLE tenant_123.orders (...);
```

**Option 3: Database-Per-Tenant** (High isolation, ops overhead)

**Recommendation:** Start with Option 1 (row-level), migrate to Option 2 for large/regulated tenants.

### Application-Level Enforcement

**Middleware pattern:**
```javascript
// Extract tenant context from auth
function extractTenantContext(req) {
  const token = verifyJWT(req.headers.authorization);
  return {
    userId: token.sub,
    tenantId: token.tenant_id,
    userType: token.user_type
  };
}

// Enforce tenant scope on all queries
function scopeQuery(query, tenantId) {
  if (!tenantId) throw new Error('Missing tenant context');
  return query.where('tenant_id', tenantId);
}
```

**Critical: Never trust client-provided tenant_id**
```javascript
// BAD - Client controls tenant_id
const tenantId = req.body.tenant_id; // ❌

// GOOD - Server extracts from auth token
const tenantId = req.user.tenant_id; // ✅
```

## Authentication & Authorization

### User Types
- `super_admin` - Platform management, cross-tenant
- `tenant_owner` - Full control within tenant
- `tenant_manager` - Operational permissions
- `tenant_staff` - Limited permissions
- `customer` - External, read-only access

### Permission Model

**See `references/permission-model.md` for complete schema**

```javascript
// Permission resolution priority:
// 1. User denial (explicit deny) → DENY
// 2. User grant (explicit allow) → ALLOW
// 3. Franchise override → ALLOW/DENY
// 4. Role permission → ALLOW
// 5. Default → DENY

function hasPermission(userId, tenantId, permission) {
  // Super admin bypass
  if (user.type === 'super_admin') return true;

  // Check explicit denials
  if (userPermissions.denied(userId, tenantId, permission)) return false;

  // Check explicit grants
  if (userPermissions.granted(userId, tenantId, permission)) return true;

  // Check role-based permissions
  const roles = getUserRoles(userId, tenantId);
  for (const role of roles) {
    if (roleHasPermission(role, permission, tenantId)) return true;
  }

  return false; // Default deny
}
```

### Session Management

**Web (Session-based):**
```
HttpOnly: true
Secure: true
SameSite: Strict
Lifetime: 30 minutes
Regenerate on login
```

**API (JWT-based):**
```
Access token: 15 minutes
Refresh token: 30 days
Rotation on refresh
Revocation table for logout
```

## Security Architecture

### Zero-Trust Checklist

**Authentication:**
- [ ] MFA for admin access
- [ ] Password: Argon2ID + salt + pepper
- [ ] Account lockout after 5 failures
- [ ] Session timeout (30 min idle)
- [ ] Token rotation on refresh

**Authorization:**
- [ ] Tenant context in every request
- [ ] Permission check before every operation
- [ ] Super admin actions audited
- [ ] Impersonation logged with justification

**Data Access:**
- [ ] `tenant_id` in WHERE clause (ALWAYS)
- [ ] Prepared statements (no SQL injection)
- [ ] Input validation at API boundary
- [ ] Output encoding (XSS prevention)

**API Security:**
- [ ] Rate limiting (per tenant, per user)
- [ ] CORS whitelist (no wildcards)
- [ ] Request size limits
- [ ] HTTPS only (HSTS enabled)

### Common Security Mistakes

❌ **Trusting client-provided tenant_id**
```javascript
const tenantId = req.body.tenant_id; // Client controls!
```
✅ **Extract from server-side auth**
```javascript
const tenantId = req.user.tenant_id; // From JWT/session
```

❌ **Missing tenant_id in queries**
```sql
SELECT * FROM orders WHERE id = ?; -- Missing tenant check!
```
✅ **Always include tenant scope**
```sql
SELECT * FROM orders WHERE tenant_id = ? AND id = ?;
```

❌ **Super admin without audit**
```javascript
if (user.type === 'super_admin') { doAction(); }
```
✅ **Super admin WITH audit**
```javascript
if (user.type === 'super_admin') {
  auditLog('ADMIN_ACTION', {user, action, tenant});
  doAction();
}
```

## API Design Principles

### Tenant Context in Requests

**Option 1: Subdomain**
```
https://tenant-slug.yourapp.com/api/v1/orders
```

**Option 2: Path parameter**
```
https://api.yourapp.com/v1/tenants/{tenant_id}/orders
```

**Option 3: Header**
```
X-Tenant-ID: 123
Authorization: Bearer <token>
```

**Recommendation:** Use JWT with `tenant_id` claim (no client input).

### RESTful Conventions

```
GET    /api/v1/orders          → List (tenant-scoped)
POST   /api/v1/orders          → Create (tenant-scoped)
GET    /api/v1/orders/{id}     → Show (tenant-scoped)
PUT    /api/v1/orders/{id}     → Update (tenant-scoped)
DELETE /api/v1/orders/{id}     → Delete (tenant-scoped)

// Admin endpoints (cross-tenant)
GET    /api/v1/admin/tenants         → List all tenants
POST   /api/v1/admin/tenants         → Create tenant
GET    /api/v1/admin/analytics       → Cross-tenant analytics
POST   /api/v1/admin/impersonate     → Start impersonation
```

### Response Format

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "page": 1,
    "per_page": 25,
    "total": 100
  }
}
```

**Error format:**
```json
{
  "success": false,
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "You do not have permission to access this resource",
    "details": {}
  }
}
```

## Audit & Compliance

### What to Audit

**Always log:**
- Super admin actions (ALL)
- Impersonation start/end
- Permission changes
- Tenant creation/suspension
- Data exports
- Failed auth attempts
- Cross-tenant access attempts (should be 0)

**Audit record format:**
```json
{
  "id": "uuid",
  "timestamp": "2025-01-23T10:30:00Z",
  "actor_user_id": 123,
  "actor_type": "super_admin",
  "action": "IMPERSONATE_USER",
  "target_tenant_id": 456,
  "target_user_id": 789,
  "justification": "Customer support request #12345",
  "ip_address": "203.0.113.1",
  "user_agent": "...",
  "changes": { "before": {...}, "after": {...} }
}
```

**Retention:**
- Security logs: 1 year minimum
- Audit trails: 7 years (compliance)
- Operational logs: 90 days

## Operational Safeguards

### Tenant Lifecycle

```
PENDING → ACTIVE → SUSPENDED → ARCHIVED
```

- **PENDING**: Created, not yet activated
- **ACTIVE**: Normal operations
- **SUSPENDED**: Payment failure, ToS violation (data retained)
- **ARCHIVED**: Deleted (data purged after retention period)

### Data Protection

**Backups:**
- Daily automated backups
- Point-in-time recovery (30 days)
- Test restore quarterly
- Tenant-level restore capability

**Encryption:**
- At rest: AES-256
- In transit: TLS 1.3
- Sensitive fields: Application-level encryption (PII, payment)

### Rate Limiting

```
Per tenant: 1000 req/min
Per user: 100 req/min
Per IP: 500 req/min
Admin endpoints: 50 req/min
```

### Monitoring Alerts

**Critical:**
- Cross-tenant access attempt
- Super admin login from new IP
- Failed auth spike (>100/min)
- Database query without tenant_id
- API error rate >5%

## Development Guidelines

### Code Review Checklist

**Every feature must:**
- [ ] Include `tenant_id` in all queries
- [ ] Validate permissions before operations
- [ ] Create audit log for privileged actions
- [ ] Test cross-tenant isolation
- [ ] Handle tenant suspension state
- [ ] Document permission requirements

### Testing Requirements

```javascript
describe('Order API', () => {
  it('prevents cross-tenant data access', async () => {
    const tenant1Order = await createOrder(tenant1);
    const tenant2User = await authenticateAs(tenant2.user);

    const response = await tenant2User.get(`/orders/${tenant1Order.id}`);
    expect(response.status).toBe(404); // Not 403 (info leak)
  });

  it('requires permission for operation', async () => {
    const user = await authenticateAs(limitedUser);
    const response = await user.delete('/orders/123');
    expect(response.status).toBe(403);
    expect(response.body.error.code).toBe('PERMISSION_DENIED');
  });
});
```

### Migration Patterns

**See `documentation/migration.md` for adding tenant_id to existing tables**

## Summary

**Critical Implementation Rules:**

1. **Tenant Isolation**: `tenant_id` in EVERY query
2. **Auth Token**: Extract tenant from JWT/session (never client input)
3. **Permissions**: Check before EVERY operation
4. **Audit**: Log ALL privileged actions
5. **Super Admin**: Audit + MFA + IP restrictions
6. **Testing**: Cross-tenant isolation tests mandatory
7. **Monitoring**: Alert on cross-tenant access attempts

**Architecture Patterns:**
- Three-panel separation (Tenant App, Admin Panel, Customer Portal)
- Zero-trust security model
- Row-level tenant isolation (start here)
- Role-based permissions with overrides
- Immutable audit trails

**See Also:**
- `references/database-schema.md` - Complete database design, indexes, partitioning
- `references/permission-model.md` - RBAC implementation, caching, middleware
- `documentation/migration.md` - Adding tenant_id, zero-downtime migrations, rollback

**Remember:** Security failures in multi-tenant systems affect ALL tenants. Test isolation exhaustively.
