---
name: multi-tenant-saas-architecture
description: Use when designing or reviewing a multi-tenant SaaS platform — tenant
  isolation model, three-panel separation (super admin, franchise admin, end user),
  zero-trust enforcement, audit trails, and per-tenant permission overrides. Unlike
  `modular-saas-architecture` which focuses on pluggable business modules, this skill
  defines the tenancy and auth boundaries that every module inherits.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Multi-Tenant SaaS Architecture

<!-- dual-compat-start -->
## Use When

- Designing tenancy for a new SaaS, or hardening an existing SaaS against cross-tenant leakage.
- Splitting a SaaS into three panels (super admin, tenant/franchise admin, end user) with distinct scopes.
- Designing per-tenant role overrides, permission priority ordering, and audit trails for privileged access.
- Planning the session, JWT, and `tenant_id` plumbing that downstream database, API, security, and delivery skills rely on.

## Do Not Use When

- The task is a single-tenant app with no plan for tenancy — this skill's constraints add overhead with no benefit.
- The work is about business-module composition rather than tenant boundaries — use `modular-saas-architecture`.
- The work is pure schema shaping inside an already-defined tenant model — use `database-design-engineering` and `mysql-best-practices`.

## Required Inputs

- Context map and critical-flow table from `system-architecture-design`.
- Access-pattern list from `database-design-engineering` (so isolation model matches real queries).
- Threat model / abuse cases from `vibe-security-skill`.
- Panel and user-type list from product requirements (super admin, tenant admin, end user, and their sub-types).

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the tenant-isolation map, panel layout, permission model, and audit plan as the deliverables named in Outputs.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- Tenant-isolation map, panel definitions, permission priority model, and audit plan (see the Outputs table below).
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
- Use the `documentation/` directory for supporting implementation detail or migration notes.
<!-- dual-compat-end -->

Production-grade multi-tenant SaaS architecture with three-panel separation, zero-trust enforcement, strict tenant isolation, and comprehensive audit trails. This skill defines the tenant and auth boundaries that every downstream module, API, and data query inherits.

## Prerequisites

Load these first, in order:

1. `world-class-engineering` — repository-wide quality bar.
2. `system-architecture-design` — produces the context map and critical flows this skill consumes.
3. `database-design-engineering` — produces the access-pattern list that shapes the isolation model.
4. `vibe-security-skill` — produces the threat model and auth rules this skill encodes.

## When this skill applies

- Designing tenancy for a new SaaS from scratch.
- Converting a single-tenant app to multi-tenant (see `documentation/migration.md`).
- Auditing an existing SaaS for cross-tenant leakage, missing `tenant_id` filters, or un-audited admin actions.
- Planning the three-panel file and route layout (`/`, `/adminpanel/`, `/memberpanel/`).
- Designing the permission priority ladder (user deny > user grant > tenant override > role > default deny).
- Defining what actions must be audited and how long audit records are retained.

## Inputs

| Artifact | Produced by | Required? | Why |
|---|---|---|---|
| Context map | `system-architecture-design` | required | defines services, panels, ownership |
| Critical-flow table | `system-architecture-design` | required | shapes auth and session boundaries |
| Access-pattern list | `database-design-engineering` | required | chooses shared-DB-with-`tenant_id` vs DB-per-tenant |
| Threat model | `vibe-security-skill` | required | informs audit rules and abuse cases |
| Panel and user-type list | product requirements | required | determines role and scope per panel |

## Outputs

| Artifact | Consumed by | Template |
|---|---|---|
| Tenant-isolation map (isolation model + `tenant_id` rules per table) | `database-design-engineering`, `api-design-first` | inline (this skill) |
| Panel definitions (super admin, tenant admin, end user) | `api-design-first`, `kubernetes-saas-delivery` | inline |
| Permission priority model (user/tenant override/role/default deny) | `vibe-security-skill`, `api-design-first` | inline + `references/permission-model.md` |
| Session and JWT plan (prefixing, lifetimes, rotation) | `api-design-first`, `vibe-security-skill` | inline |
| Audit event set and retention policy | `observability-monitoring`, `reliability-engineering` | inline |
| Migration plan (single-tenant to multi-tenant) | `database-design-engineering`, `deployment-release-engineering` | `documentation/migration.md` |

## Non-negotiables

- Every franchise/tenant-scoped table has `tenant_id` (or `franchise_id`) `NOT NULL` with a foreign key to `tenants`.
- Every query on a tenant-scoped table includes `tenant_id` in the `WHERE` clause.
- `tenant_id` is always extracted from session or JWT — never from client input (body, query, header).
- Default authorisation decision is deny. Every action requires an explicit permission check.
- Every super-admin action that touches tenant data is audited with actor, target tenant, and justification.
- Cross-tenant access that should not exist returns `404 Not Found`, never `403 Forbidden` (403 confirms the resource exists).

## Decision rules

### Isolation model

```text
Tenants share data schema AND tenants < ~10k AND regulated data not tenant-partitioned
    -> Shared DB, row-level tenant_id (default choice for this skill)

Strong regulatory boundary (HIPAA/PCI) per tenant
    -> Schema-per-tenant OR DB-per-tenant; app injects connection by tenant

Single very large tenant needs isolation from the rest
    -> Hybrid: shared DB for small tenants, dedicated DB for large tenant

Wrong choice failure modes:
- Shared DB without tenant_id discipline -> data leakage, impossible to audit
- DB-per-tenant at small scale -> migration and operational cost explodes
- Schema-per-tenant without tooling -> migrations drift across schemas
```

### Panel placement of a new feature

```text
Feature controls platform config, billing, tenant lifecycle, or impersonation
    -> /adminpanel/ (super_admin only, audited)

Feature is tenant-admin workspace (manage own tenant, staff, catalogue)
    -> /public/ root (tenant owners/staff, scoped by tenant_id)

Feature is self-service for end user (customer/member/student/patient)
    -> /memberpanel/ (own records only, scoped by tenant_id AND user_id)

Wrong choice failure modes:
- Admin feature in /public/ -> tenant users see platform levers
- Tenant feature in /memberpanel/ -> end users escalate to admin-only data
- End-user feature in /public/ -> collides with tenant admin routes
```

### Permission resolution priority

```text
1. actor is super_admin            -> ALLOW (always audit)
2. user_permissions.denied match   -> DENY
3. user_permissions.granted match  -> ALLOW
4. tenant_role_overrides match     -> ALLOW/DENY per is_enabled
5. role -> permission via template -> ALLOW
6. no match                        -> DENY

Wrong ordering failure mode: if role is checked before user deny, an
explicit revocation never takes effect. Always deny-before-grant at each tier.
```

### Session prefix vs no prefix

```text
One SaaS codebase hosts multiple apps on the same origin  -> prefix required
Only one app on origin AND no shared subdomain sessions   -> prefix optional
SSO / impersonation across apps planned                   -> prefix required

Without a prefix, two SaaS apps on the same host collide in $_SESSION and the
bug only appears in production when both apps are logged in.
```

## Three-panel architecture

```text
+-------------------------------------------------------------+
|                Shared Infrastructure Layer                  |
|  Data (tenant isolated) | Business Logic | Session system   |
+-------------------------------------------------------------+
         |                       |                    |
+--------v--------+    +---------v------+   +---------v-------+
|   /public/      |    |  /adminpanel/  |   |  /memberpanel/  |
| (ROOT)          |    |                |   |                 |
| Tenant Admin    |    |  Super Admin   |   |  End User       |
|  Workspace      |    |  System        |   |  Portal         |
| owner, staff    |    |  super_admin   |   |  member/student |
+-----------------+    +----------------+   +-----------------+
```

Important: `/public/` root is the tenant-admin workspace, not an end-user panel. Confusing the two is the most common mistake.

File layout:

```text
public/
  index.php           # Landing
  sign-in.php         # Login
  dashboard.php       # Tenant admin dashboard
  adminpanel/         # Super admin panel
    includes/
  memberpanel/        # End user portal
    includes/
  includes/           # Shared includes
  assets/
```

### Panel definitions

| Panel | Path | Users | Scope | Notes |
|---|---|---|---|---|
| Tenant Admin | `/public/` | owner, staff | single tenant | all queries include `tenant_id = ?`; cannot touch platform config |
| Super Admin | `/public/adminpanel/` | super_admin | cross-tenant | `tenant_id` may be NULL; every action audited |
| End User | `/public/memberpanel/` | member, student, customer, patient | own records within tenant | queries scoped by `tenant_id AND user_id` |

## Tenant isolation model

### `tenant_id` rules per user type

| User type | `tenant_id` column |
|---|---|
| super_admin | nullable |
| tenant owner | required, NOT NULL |
| tenant staff | required, NOT NULL |
| member / student / customer / patient | required, NOT NULL |

### Table pattern

```sql
CREATE TABLE students (
    id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tenant_id     BIGINT UNSIGNED NOT NULL,
    first_name    VARCHAR(100) NOT NULL,
    last_name     VARCHAR(100) NOT NULL,
    email         VARCHAR(100),
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    INDEX idx_tenant (tenant_id),
    INDEX idx_tenant_email (tenant_id, email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

Composite indexes lead with `tenant_id`. `utf8mb4_unicode_ci` everywhere. Match file case exactly (Linux file systems are case-sensitive).

### Query enforcement

```php
// Extract tenant from session/JWT. Never from client input.
$tenantId = getSession('tenant_id');

// Regular users: filter by tenant_id
$stmt = $db->prepare('SELECT * FROM students WHERE tenant_id = ? AND id = ?');
$stmt->execute([$tenantId, $studentId]);

// Super admin: cross-tenant access is allowed but always audited
if (getSession('user_type') === 'super_admin') {
    auditLog('CROSS_TENANT_ACCESS', [
        'admin_user_id'      => getSession('user_id'),
        'target_tenant_id'   => $requestedTenantId,
        'action'             => 'VIEW_STUDENTS',
        'justification'      => $request['justification'] ?? null,
    ]);
}
```

## Session and JWT plan

### Session prefix system

```php
define('SESSION_PREFIX', 'saas_app_');  // e.g. 'school_', 'restaurant_'

setSession('user_id', $userId);      // writes $_SESSION['saas_app_user_id']
$userId = getSession('user_id');     // reads $_SESSION['saas_app_user_id']
```

### Session cookie settings

| Setting | Value |
|---|---|
| HttpOnly | true |
| Secure | auto-detect HTTPS (port 443 or `$_SERVER['HTTPS']`) |
| SameSite | Strict |
| Lifetime | 30 min idle |
| Regeneration | on login and on privilege change |

```php
$isHttps = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off')
    || (int) $_SERVER['SERVER_PORT'] === 443;
ini_set('session.cookie_secure', $isHttps ? '1' : '0');
```

### JWT for mobile and API

| Setting | Value |
|---|---|
| Access token lifetime | 15 min |
| Refresh token lifetime | 30 days |
| Rotation | on every refresh |
| Revocation | persisted table keyed by jti |

## Permission model

Priority (highest first): user deny > user grant > tenant override > role permission > default deny. See `references/permission-model.md` for full schema, resolution algorithm, caching strategy, and seed data.

```javascript
function hasPermission(userId, tenantId, permission) {
  if (user.type === 'super_admin') {
    auditLog('PERMISSION_BYPASS', { userId, permission });
    return true;
  }
  if (userPermissions.denied(userId, tenantId, permission)) return false;
  if (userPermissions.granted(userId, tenantId, permission)) return true;
  for (const role of getUserRoles(userId, tenantId)) {
    const override = tenantRoleOverride(tenantId, role.id, permission);
    if (override !== null) return override.isEnabled;
    if (roleHasPermission(role, permission)) return true;
  }
  return false; // default deny
}
```

## Zero-trust checklist

- `tenant_id` in every query on a tenant-scoped table (except super_admin with audit).
- Prepared statements only — no string concatenation into SQL.
- Permission check before every mutating operation.
- MFA required for super-admin access.
- Passwords stored as Argon2ID with per-user salt (32 chars) and server-wide pepper (64+ chars).
- Account lockout after 5 failed attempts with exponential backoff.
- Rate limiting: tenant 1000 req/min, user 100 req/min.
- HTTPS + HSTS on all panels.
- Super-admin actions audited with justification.
- Cross-tenant access returns 404, not 403.

## API design

```text
# Tenant-scoped (default)
GET    /api/v1/orders          # list within tenant
POST   /api/v1/orders          # create within tenant
GET    /api/v1/orders/{id}     # show; 404 if wrong tenant
DELETE /api/v1/orders/{id}     # delete; 404 if wrong tenant

# Super admin (cross-tenant, audited)
GET    /api/v1/admin/tenants
POST   /api/v1/admin/impersonate
```

Response envelope:

```json
{ "success": true, "data": {}, "meta": { "page": 1, "total": 100 } }
```

Error envelope:

```json
{ "success": false, "error": { "code": "PERMISSION_DENIED", "message": "..." } }
```

## Audit and compliance

Always audit: all super-admin actions, impersonation, permission changes, tenant creation/suspension, data exports, failed auth, cross-tenant access attempts.

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
  "changes": { "before": {}, "after": {} }
}
```

Retention: security logs 1 year, audit trails 7 years, operational logs 90 days.

## Monitoring alerts

- Cross-tenant access attempt (target = zero).
- Super-admin login from new IP.
- Failed auth spike > 100/min.
- Database query without `tenant_id` on a tenant-scoped table.
- API error rate > 5%.

## Tenant lifecycle

```text
PENDING -> ACTIVE -> SUSPENDED -> ARCHIVED
```

Archival is reversible until a configured retention cut-off; archived tenants are then hard-deleted via cascade.

## Anti-patterns

- **Client-supplied tenant identifier.** `$franchiseId = $_POST['franchise_id'];` — any user can set this to another tenant. Fix: always `getSession('tenant_id')` or read from the verified JWT claim.
- **Missing tenant scope on a query.** `SELECT * FROM students WHERE id = ?` — returns any student across any tenant. Fix: `SELECT * FROM students WHERE tenant_id = ? AND id = ?` and treat a missing row as 404.
- **Super-admin mutation without audit.** `deleteStudent($studentId);` run from the super-admin panel with no log. Fix: wrap every super-admin mutation with `auditLog('ADMIN_DELETE_STUDENT', [...])` capturing actor, target tenant, and justification.
- **Returning 403 for cross-tenant access.** Confirms the resource exists and enables tenant-ID enumeration. Fix: map cross-tenant misses to 404 so the existence of the resource is hidden.
- **`tenant_id` nullable on a business table.** `tenant_id BIGINT NULL` — allows rows with no owner, which every tenant query then excludes silently. Fix: `tenant_id BIGINT UNSIGNED NOT NULL` with a foreign key; backfill before flipping NOT NULL.
- **Session keys without a prefix in a multi-app host.** Two apps on the same origin overwrite each other's `$_SESSION['user_id']`. Fix: `SESSION_PREFIX` per app, always go through `setSession()` / `getSession()`.
- **Index order `(status, tenant_id)` instead of `(tenant_id, status)`.** Query planner cannot use the composite index to isolate one tenant's slice. Fix: lead every composite index with `tenant_id`.
- **Big-bang migration of every table at once.** Raises rollback risk and produces hours of downtime. Fix: migrate one domain at a time with the six-step pattern in `documentation/migration.md` and verify no NULL `tenant_id` before flipping the column to NOT NULL.

## Read next

- `database-design-engineering` — schema, indexes, migration discipline once the isolation model is chosen.
- `api-design-first` — REST conventions, auth model, and error envelope that this skill's panels depend on.
- `vibe-security-skill` — threat modelling, abuse cases, and auth/authz matrix that feed this skill.
- `kubernetes-saas-delivery` — per-tenant deploy, namespace isolation, and progressive rollout on top of this model.
- `modular-saas-architecture` — when the platform also composes pluggable business modules inside the tenancy defined here.
- `mysql-best-practices` — MySQL engine-specific execution of the schema patterns here.

## References

- `references/database-schema.md` — tenant, user, audit, and tenant-scoped table schemas with indexes and partitioning.
- `references/permission-model.md` — RBAC schema, permission resolution algorithm, caching, middleware, hierarchical and conditional permissions.
- `documentation/migration.md` — adding `tenant_id` safely, zero-downtime migration, single-to-multi-tenant phases, rollback.
