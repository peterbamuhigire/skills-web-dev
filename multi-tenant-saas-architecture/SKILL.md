---
name: multi-tenant-saas-architecture
description: Production-grade multi-tenant SaaS platform architecture with three-panel separation, zero-trust security, strict tenant isolation, and comprehensive audit trails. Use for designing multi-tenant systems, implementing tenant-scoped permissions...
---

# Multi-Tenant SaaS Platform Architecture

## Overview

Production-grade multi-tenant SaaS with strict tenant isolation, zero-trust security, and three-panel separation.

**Core Principles:** Zero-trust, Tenant isolation by default, Least privilege, Audit everything.

**Security Baseline (Required):** Load and apply the **Vibe Security Skill** for all web app/API work.
**Database Standards (Required):** All database work MUST follow **mysql-best-practices** skill patterns.

**Environments:**

| Environment | OS | Database | Web Root |
|---|---|---|---|
| Development | Windows 11 (WAMP) | MySQL 8.4.7 | `C:\wamp64\www\{project}\` |
| Staging/Production | Ubuntu/Debian VPS | MySQL 8.x | `/var/www/html/{project}/` |

Cross-platform: `utf8mb4_unicode_ci` everywhere. Match file case exactly (Linux is case-sensitive).

## Three-Tier Panel Architecture (CORE CONCEPT)

```
┌──────────────────────────────────────────────────────────────┐
│              Shared Infrastructure Layer                      │
│  Data (Tenant Isolated) | Business Logic | Session System    │
└──────────────────────────────────────────────────────────────┘
         │                       │                    │
┌────────▼────────┐    ┌─────────▼──────┐   ┌────────▼────────┐
│   /public/      │    │  /adminpanel/  │   │  /memberpanel/  │
│ (ROOT)          │    │                │   │                 │
│ Franchise Admin │    │  Super Admin   │   │  End User       │
│  Workspace      │    │  System        │   │  Portal         │
│ owner, staff    │    │  super_admin   │   │  member/student │
└─────────────────┘    └────────────────┘   └─────────────────┘
```

**CRITICAL:** `/public/` root = Franchise admin workspace — NOT a member panel!

## File Structure Convention

```
public/
├── index.php           # Landing page
├── sign-in.php         # Login
├── dashboard.php       # Franchise admin dashboard
├── adminpanel/         # Super admin panel
│   └── includes/
├── memberpanel/        # End user portal
│   └── includes/
├── includes/           # Shared includes
└── assets/
```

## Panel Definitions

### 1. Franchise Admin Panel (`/public/` root) — THE MAIN WORKSPACE
**Users:** owner, staff | **Scope:** Single franchise only
- All queries include `WHERE franchise_id = ?`
- Cannot modify platform settings or access other franchises

### 2. Super Admin Panel (`/public/adminpanel/`)
**Users:** super_admin | **Scope:** Cross-franchise with audit trails
- Can create/suspend franchises; view cross-franchise analytics
- `franchise_id` CAN be NULL for super admins
- Every action creates an audit log entry

### 3. End User Portal (`/public/memberpanel/`)
**Users:** member, student, customer, patient | **Scope:** Own records only
- Self-service: view grades, orders, appointments, medical records

## Franchise Isolation Model

**User Type → franchise_id rule:**
```
super_admin  → franchise_id CAN be NULL
owner        → franchise_id REQUIRED, NOT NULL
staff        → franchise_id REQUIRED, NOT NULL
member/student/customer/patient → franchise_id REQUIRED, NOT NULL
```

### Database-Level Isolation (Default: Shared DB with Row-Level franchise_id)

```sql
-- Every franchise-scoped table has franchise_id
CREATE TABLE students (
    id           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    franchise_id BIGINT UNSIGNED NOT NULL,
    first_name   VARCHAR(100) NOT NULL,
    last_name    VARCHAR(100) NOT NULL,
    email        VARCHAR(100),
    FOREIGN KEY (franchise_id) REFERENCES tbl_franchises(id) ON DELETE CASCADE,
    INDEX idx_franchise (franchise_id),
    INDEX idx_franchise_email (franchise_id, email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ALL queries MUST include franchise_id
SELECT * FROM students WHERE franchise_id = ? AND id = ?;
```

### Application-Level Enforcement

```php
// Session Prefix System (CRITICAL — prevents collisions in multi-tenant sessions)
define('SESSION_PREFIX', 'saas_app_');  // Customize per SaaS: 'school_', 'restaurant_', etc.

setSession('user_id', $userId);          // Sets $_SESSION['saas_app_user_id']
$userId = getSession('user_id');         // Gets $_SESSION['saas_app_user_id']

// ALWAYS extract franchise from session — NEVER from user input
$franchiseId = getSession('franchise_id');  // ✅
// $franchiseId = $_POST['franchise_id'];   // ❌ NEVER

// Regular users: filter by franchise_id
$stmt = $db->prepare("SELECT * FROM students WHERE franchise_id = ? AND id = ?");
$stmt->execute([getSession('franchise_id'), $studentId]);

// Super admin: allowed cross-franchise access, but ALWAYS log it
if (getSession('user_type') === 'super_admin') {
    auditLog('CROSS_FRANCHISE_ACCESS', [
        'admin_user_id' => getSession('user_id'),
        'target_franchise_id' => $requestedFranchiseId,
        'action' => 'VIEW_STUDENTS'
    ]);
}
```

## Authentication & Sessions

```php
// HTTPS auto-detection (CRITICAL for localhost development)
$isHttps = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') || $_SERVER['SERVER_PORT'] == 443;
ini_set('session.cookie_secure', $isHttps ? '1' : '0');
```

**Session settings:** HttpOnly: true | SameSite: Strict | Lifetime: 30 min | Regenerate on login

**JWT (mobile/API):** Access token: 15 min | Refresh token: 30 days | Rotation on refresh | Revocation table

## Permission Model

```javascript
// Priority: User deny > User grant > Franchise override > Role permission > Default DENY
function hasPermission(userId, tenantId, permission) {
  if (user.type === 'super_admin') return true;
  if (userPermissions.denied(userId, tenantId, permission)) return false;
  if (userPermissions.granted(userId, tenantId, permission)) return true;
  const roles = getUserRoles(userId, tenantId);
  for (const role of roles) {
    if (roleHasPermission(role, permission, tenantId)) return true;
  }
  return false; // Default deny
}
```

## Security Architecture

### Zero-Trust Checklist
- [ ] `franchise_id` in every query (except super_admin with audit)
- [ ] Prepared statements (no SQL injection)
- [ ] Permission check before every operation
- [ ] MFA for admin access
- [ ] Password: Argon2ID + salt + pepper
- [ ] Account lockout after 5 failures
- [ ] Rate limiting: tenant 1000 req/min | user 100 req/min
- [ ] HTTPS + HSTS
- [ ] Super admin actions audited with justification

### Common Mistakes

```php
// ❌ Client-controlled franchise_id
$franchiseId = $_POST['franchise_id'];

// ✅ Server-side session (with prefix)
$franchiseId = getSession('franchise_id');

// ❌ Missing franchise scope (data leakage)
$stmt = $db->prepare("SELECT * FROM students WHERE id = ?");

// ✅ Always franchise-scoped
$stmt = $db->prepare("SELECT * FROM students WHERE franchise_id = ? AND id = ?");
$stmt->execute([getSession('franchise_id'), $studentId]);

// ❌ Super admin without audit
deleteStudent($studentId);

// ✅ Super admin WITH audit
auditLog('ADMIN_DELETE_STUDENT', ['admin_user_id' => getSession('user_id'), ...]);
deleteStudent($studentId);
```

## API Design

```
# RESTful conventions (all tenant-scoped)
GET    /api/v1/orders          → List (tenant-scoped)
POST   /api/v1/orders          → Create (tenant-scoped)
GET    /api/v1/orders/{id}     → Show (tenant-scoped, 404 if wrong tenant — not 403)
DELETE /api/v1/orders/{id}     → Delete (tenant-scoped)

# Admin (cross-tenant)
GET    /api/v1/admin/tenants   → List all tenants
POST   /api/v1/admin/impersonate → Impersonate (logged)
```

**Response format:** `{"success": true, "data": {...}, "meta": {"page": 1, "total": 100}}`
**Error format:** `{"success": false, "error": {"code": "PERMISSION_DENIED", "message": "..."}}`

## Audit & Compliance

**Always audit:** All super_admin actions | Impersonation | Permission changes | Tenant creation/suspension | Data exports | Failed auth attempts | Cross-tenant access attempts

```json
{
  "id": "uuid",
  "timestamp": "2026-04-07T10:30:00Z",
  "actor_user_id": 123,
  "actor_type": "super_admin",
  "action": "IMPERSONATE_USER",
  "target_tenant_id": 456,
  "justification": "Support request #12345",
  "ip_address": "203.0.113.1",
  "changes": {"before": {...}, "after": {...}}
}
```

**Retention:** Security logs: 1 year | Audit trails: 7 years | Operational logs: 90 days

## Monitoring Alerts

**Critical alerts:**
- Cross-tenant access attempt (should be zero)
- Super admin login from new IP
- Failed auth spike > 100/min
- Database query without tenant_id
- API error rate > 5%

## Tenant Lifecycle

```
PENDING → ACTIVE → SUSPENDED → ARCHIVED
```

## Implementation Checklist

- [ ] `franchise_id` in ALL franchise-scoped tables
- [ ] Session prefix defined and used via `setSession()`/`getSession()`
- [ ] Three-panel structure (/, /adminpanel/, /memberpanel/)
- [ ] `franchise_id` extracted from session/JWT — NEVER from client input
- [ ] Permission check before every operation
- [ ] Super admin audit log on every action
- [ ] Cross-franchise isolation tests
- [ ] HTTPS auto-detection for local dev
- [ ] Rate limiting per tenant + per user
- [ ] Audit retention policy configured

**SaaS Seeder Specifics:** Password: Argon2ID + salt(32 chars) + pepper(64+ chars) | Use `super-user-dev.php` to create admin users | Collation: `utf8mb4_unicode_ci`

**See Also:**
- `references/database-schema.md` — Complete database design, indexes, partitioning
- `references/permission-model.md` — RBAC implementation, caching, middleware
- `documentation/migration.md` — Adding franchise_id, zero-downtime migrations
