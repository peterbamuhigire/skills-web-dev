# Database Design Document -- Template & Guide

**Back to:** [SDLC Design Skill](../SKILL.md)

## Purpose

Details the **complete database schema** -- tables, relationships, indexes, stored procedures, triggers, migration strategy, and performance optimization. This is the authoritative reference for all data layer decisions.

## Audience

Database architects, backend developers, DBAs, data migration engineers.

## When to Create

- After the SDD defines the system architecture and data layer boundaries
- Before any database migration scripts are written
- When onboarding new backend developers to the data model

## Typical Length

20-40 pages. Split into `02-database/` subdirectory files if exceeding 500 lines.

## Important Cross-Reference

**Do NOT duplicate content from the `mysql-best-practices` skill.** This document describes your project's specific schema. The `mysql-best-practices` skill provides the standards and conventions you follow. Reference it; do not copy it.

---

## Template

```markdown
# [Project Name] -- Database Design Document

**Version:** 1.0
**Date:** YYYY-MM-DD
**Author:** [Name]
**Status:** Draft | Under Review | Approved
**SDD Reference:** [Link to System Design Document]
**Standards Reference:** mysql-best-practices skill

---

## 1. Database Overview

### 1.1 Database Configuration

| Attribute | Value |
|-----------|-------|
| DBMS | MySQL 8.x |
| Character Set | utf8mb4 |
| Collation | utf8mb4_general_ci |
| Storage Engine | InnoDB (all tables) |
| Timezone | UTC (stored), localized in application layer |
| Naming Convention | snake_case for tables, columns, indexes |

### 1.2 Connection Configuration

| Environment | Host | Port | Database | Max Connections |
|------------|------|------|----------|-----------------|
| Development | localhost | 3306 | [project]_dev | 20 |
| Staging | staging-db.host | 3306 | [project]_staging | 50 |
| Production | prod-db.host | 3306 | [project]_prod | 100 |

### 1.3 Database Size Estimates

| Table Group | Estimated Rows (Year 1) | Growth Rate |
|------------|------------------------|-------------|
| Core (users, franchises, roles) | 10,000 | Slow |
| Transactional (invoices, payments) | 500,000 | High |
| Reference (products, categories) | 50,000 | Medium |
| Audit (audit_trail, login_history) | 1,000,000+ | Very High |

---

## 2. Entity-Relationship Diagram

[ASCII diagram showing major entities and their relationships.]

+-------------+       +------------------+       +--------------+
| franchises  |<------| users            |------>| roles        |
| (tenants)   |  1:N  | (all panels)     |  N:M  | (RBAC)       |
+------+------+       +--------+---------+       +------+-------+
       |                       |                         |
       | 1:N                   | 1:N                     | 1:N
       v                       v                         v
+------+------+       +--------+---------+       +------+-------+
| products    |       | invoices         |       | permissions  |
| (catalog)   |       | (transactions)   |       | (RBAC)       |
+------+------+       +--------+---------+       +--------------+
       |                       |
       | 1:N                   | 1:N
       v                       v
+------+------+       +--------+---------+
| stock_levels|       | invoice_items    |
| (inventory) |       | (line items)     |
+-------------+       +------------------+

---

## 3. Table Definitions

[Repeat this block for every table. Group tables by module.]

### 3.1 Core Tables

#### Table: franchises

**Purpose:** Tenant organizations (one row per SaaS customer)
**Estimated Rows:** 100-500 (Year 1)
**Tenant-Scoped:** No (this IS the tenant table)

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | INT UNSIGNED | No | AUTO_INCREMENT | PK |
| name | VARCHAR(255) | No | -- | -- |
| code | VARCHAR(50) | No | -- | UNIQUE |
| status | ENUM('active','suspended','closed') | No | 'active' | -- |
| subscription_plan | VARCHAR(50) | Yes | NULL | -- |
| created_at | DATETIME | No | CURRENT_TIMESTAMP | -- |
| updated_at | DATETIME | No | CURRENT_TIMESTAMP | ON UPDATE |

**Indexes:**
| Name | Columns | Type | Justification |
|------|---------|------|---------------|
| PRIMARY | id | PK | Row identity |
| uq_franchises_code | code | UNIQUE | Franchise lookup by code |

#### Table: users

**Purpose:** All system users across all panels and franchises
**Estimated Rows:** 5,000-20,000 (Year 1)
**Tenant-Scoped:** Yes (franchise_id required)

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | INT UNSIGNED | No | AUTO_INCREMENT | PK |
| franchise_id | INT UNSIGNED | No | -- | FK franchises(id) |
| username | VARCHAR(100) | No | -- | UNIQUE(franchise_id, username) |
| email | VARCHAR(255) | No | -- | UNIQUE(franchise_id, email) |
| password_hash | VARCHAR(255) | No | -- | bcrypt hash |
| full_name | VARCHAR(255) | No | -- | -- |
| role_id | INT UNSIGNED | No | -- | FK roles(id) |
| panel | ENUM('public','adminpanel','memberpanel') | No | -- | -- |
| status | ENUM('active','inactive','locked') | No | 'active' | -- |
| last_login | DATETIME | Yes | NULL | -- |
| created_at | DATETIME | No | CURRENT_TIMESTAMP | -- |
| updated_at | DATETIME | No | CURRENT_TIMESTAMP | ON UPDATE |

**Indexes:**
| Name | Columns | Type | Justification |
|------|---------|------|---------------|
| PRIMARY | id | PK | Row identity |
| idx_users_franchise | franchise_id | INDEX | Tenant-scoped queries |
| uq_users_franchise_username | franchise_id, username | UNIQUE | Username uniqueness per tenant |
| uq_users_franchise_email | franchise_id, email | UNIQUE | Email uniqueness per tenant |
| idx_users_role | role_id | INDEX | Role-based filtering |

[Continue for all tables in the system...]

### 3.2 Transactional Tables

[invoices, invoice_items, payments, stock_movements, etc.]

### 3.3 Reference Tables

[products, categories, warehouses, etc.]

### 3.4 System Tables

[audit_trail, login_history, system_settings, etc.]
```

---

## 4. Multi-Tenant Data Model

### 4.1 Tenant-Scoped Tables (franchise_id REQUIRED)

| Table | franchise_id Column | Enforcement |
|-------|-------------------|-------------|
| users | Yes | FK + middleware |
| products | Yes | FK + middleware |
| invoices | Yes | FK + middleware |
| invoice_items | Via invoices.franchise_id | JOIN enforcement |
| stock_movements | Yes | FK + middleware |
| payments | Yes | FK + middleware |
| [all business data tables] | Yes | FK + middleware |

### 4.2 Global Tables (NO franchise_id)

| Table | Purpose | Access |
|-------|---------|--------|
| franchises | Tenant definitions | Super admin only |
| system_settings | Global platform config | Super admin only |
| subscription_plans | Available plans | Super admin only |
| module_definitions | Available modules | Super admin only |

### 4.3 Tenant Isolation Verification

```sql
-- VERIFICATION QUERY: Find tables missing franchise_id
-- Run this periodically to catch schema drift
SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES t
WHERE t.TABLE_SCHEMA = DATABASE()
  AND t.TABLE_NAME NOT IN (
    'franchises', 'system_settings', 'subscription_plans',
    'module_definitions', 'migrations'
    -- Add other global tables here
  )
  AND NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS c
    WHERE c.TABLE_SCHEMA = t.TABLE_SCHEMA
      AND c.TABLE_NAME = t.TABLE_NAME
      AND c.COLUMN_NAME = 'franchise_id'
  );
-- Expected result: EMPTY (no missing franchise_id columns)
```

---

## 5. Stored Procedures & Functions

### Naming Convention

- Procedures: `sp_action_entity` (e.g., `sp_create_invoice`, `sp_close_pos_session`)
- Functions: `fn_action_entity` (e.g., `fn_calculate_stock_level`)

### Procedure Inventory

| Name | Purpose | Parameters | Return |
|------|---------|-----------|--------|
| sp_create_invoice | Create invoice with line items | p_franchise_id, p_customer_id, p_items (JSON) | Invoice ID |
| sp_close_pos_session | Close POS session with supervisor auth | p_session_id, p_supervisor_id | Success boolean |
| sp_detect_receipt_gaps | Find missing receipt numbers | p_franchise_id, p_date_from, p_date_to | Result set of gaps |
| fn_calculate_stock_level | Get current stock for a product | p_product_id, p_franchise_id, p_warehouse_id | INT (stock level) |

### Procedure Documentation Format

```sql
-- ============================================================
-- Procedure: sp_create_invoice
-- Purpose:   Create a new invoice with line items atomically
-- Parameters:
--   p_franchise_id  INT     - Tenant identifier
--   p_customer_id   INT     - Customer placing the order
--   p_items         JSON    - Array of {product_id, qty, price}
-- Returns:   INT - New invoice ID
-- Example:
--   CALL sp_create_invoice(1, 42, '[{"product_id":1,"qty":2,"price":25.00}]');
-- Author:    [Name]
-- Created:   YYYY-MM-DD
-- Modified:  YYYY-MM-DD (description of change)
-- ============================================================
```

See: `mysql-best-practices` skill for stored procedure standards.

---

## 6. Triggers

### Trigger Inventory

| Trigger | Table | Event | Timing | Purpose |
|---------|-------|-------|--------|---------|
| tr_users_audit_insert | users | INSERT | AFTER | Log user creation to audit_trail |
| tr_users_audit_update | users | UPDATE | AFTER | Log user changes with old/new values |
| tr_invoices_update_stock | invoices | INSERT | AFTER | Update stock levels when invoice created |
| tr_stock_movements_level | stock_movements | INSERT | AFTER | Recalculate stock_levels entry |

### Trigger Documentation Format

```sql
-- ============================================================
-- Trigger:  tr_users_audit_insert
-- Table:    users
-- Event:    INSERT
-- Timing:   AFTER
-- Purpose:  Record user creation in audit_trail
-- Side Effects: Inserts 1 row into audit_trail
-- Author:   [Name]
-- ============================================================
```

---

## 7. Views

| View Name | Purpose | Source Tables | Panels |
|-----------|---------|-------------|--------|
| vw_daily_sales_summary | Dashboard widget data | invoices, invoice_items | /public/, /adminpanel/ |
| vw_stock_alerts | Low stock warnings | stock_levels, products | /public/ |
| vw_user_permissions | Flattened role-permission mapping | users, roles, permissions, role_permissions | All |

---

## 8. Data Migration Strategy

### 8.1 Migration File Naming

```
database/migrations/YYYY-MM-DD-description.sql
database/migrations-production/YYYY-MM-DD-description.sql
```

### 8.2 Migration Requirements

- **Idempotent:** Safe to run multiple times (use IF NOT EXISTS, IF EXISTS checks)
- **Non-destructive:** Never DROP columns/tables in production migrations
- **Reversible:** Include rollback section (commented out) for emergency use
- **Tested:** Run on staging before production
- **Documented:** Header comment with purpose, author, and date

### 8.3 Migration Template

```sql
-- Migration: YYYY-MM-DD-add-products-sku-column.sql
-- Author: [Name]
-- Purpose: Add SKU column to products table for barcode scanning
-- Idempotent: Yes
-- Destructive: No

-- Forward migration
ALTER TABLE products
ADD COLUMN IF NOT EXISTS sku VARCHAR(50) NULL DEFAULT NULL
AFTER name;

CREATE UNIQUE INDEX IF NOT EXISTS uq_products_franchise_sku
ON products (franchise_id, sku);

-- Rollback (emergency use only, commented out)
-- ALTER TABLE products DROP COLUMN IF EXISTS sku;
```

### 8.4 Production Migration Checklist

- [ ] Migration tested on local dev environment
- [ ] Migration tested on staging environment
- [ ] Backup taken before running on production
- [ ] Migration is idempotent (safe to run twice)
- [ ] Migration is non-destructive (no data loss)
- [ ] Schema files updated to reflect migration
- [ ] Database Design Document updated

---

## 9. Seed Data

### 9.1 System Seed Data (required for every installation)

| Table | Seed Data | Purpose |
|-------|-----------|---------|
| roles | Super Admin, Franchise Admin, Manager, Cashier, Member | Default role hierarchy |
| permissions | Module CRUD permissions | RBAC permission set |
| role_permissions | Role-permission mappings | Default access matrix |
| system_settings | App name, timezone, currency, default values | Platform configuration |
| module_definitions | Available business modules | Module registry |

### 9.2 Test Data Generation

- Use `saas-seeder` skill for bootstrapping the initial database
- Generate realistic test data for staging (min 3 franchises, 50 users, 1000 transactions)
- Never use production data in dev/staging without anonymization

---

## 10. Performance Optimization

### 10.1 Index Strategy

- Every foreign key column MUST be indexed
- Every `franchise_id` column MUST be the first column in composite indexes
- Composite indexes for common WHERE + ORDER BY combinations
- Covering indexes for high-frequency read queries

### 10.2 Query Performance Targets

| Query Type | Target (p95) | Monitoring |
|-----------|-------------|------------|
| Single row lookup (by PK) | < 5ms | Application logging |
| Paginated list (25 rows) | < 100ms | Application logging |
| Dashboard aggregate | < 500ms | Dashboard load time |
| Complex report | < 2s | Report generation time |
| Stored procedure | < 1s | Procedure execution log |

### 10.3 Partitioning Considerations

- Consider partitioning for tables exceeding 10M rows
- Partition by franchise_id + date range for transactional tables
- Evaluate RANGE partitioning on date columns for audit_trail

---

## 11. Backup & Recovery Strategy

| Attribute | Value |
|-----------|-------|
| Backup frequency | Daily full, hourly incremental |
| Retention | 30 days (daily), 7 days (hourly) |
| Storage | Off-site encrypted backup |
| Recovery time objective (RTO) | < 4 hours |
| Recovery point objective (RPO) | < 1 hour |
| Test restore frequency | Monthly |

---

## Section-by-Section Guidance

| Section | Key Guidance |
|---------|-------------|
| Database Overview | Specify exact MySQL version, charset, collation for every environment. |
| ER Diagram | Show major entities and relationships. Use ASCII art. |
| Table Definitions | Include ALL columns, types, constraints, indexes. Group by module. |
| Multi-Tenant Model | Explicitly list tenant-scoped vs global tables. Include verification query. |
| Stored Procedures | Document every procedure with parameters, return, and usage example. |
| Triggers | Document every trigger with event, timing, and side effects. |
| Migrations | Use idempotent, non-destructive scripts. Always test on staging first. |
| Seed Data | Define what must exist for the system to function at all. |
| Performance | Set numeric targets per query type. Index strategy is mandatory. |

## Anti-Patterns

| Anti-Pattern | Why It Fails | Do This Instead |
|-------------|-------------|-----------------|
| Missing franchise_id on business tables | Cross-tenant data leakage | Add franchise_id to every tenant-scoped table |
| No indexes on foreign keys | Slow JOINs, poor query performance | Index every FK column |
| Storing business logic in triggers only | Hard to debug, hidden side effects | Use triggers for audit/cascade only; logic in PHP |
| Destructive production migrations | Data loss, no rollback | Always non-destructive, always idempotent |
| No seed data documentation | New installations are broken | Define minimum seed data for every installation |
| SELECT * in queries | Fetches unnecessary columns, slow | Select only needed columns |
| No ER diagram | Developers guess at relationships | Always include ASCII ER diagram |

## Quality Checklist

- [ ] All tables documented with columns, types, constraints, and indexes
- [ ] Entity-relationship diagram present and accurate
- [ ] franchise_id present on all tenant-scoped tables
- [ ] Global tables explicitly listed and justified
- [ ] Tenant isolation verification query included
- [ ] All stored procedures documented with parameters and examples
- [ ] All triggers documented with event, timing, and side effects
- [ ] Migration strategy defined with naming convention and checklist
- [ ] Seed data defined for system bootstrap
- [ ] Performance targets set per query type
- [ ] Backup and recovery strategy documented
- [ ] Cross-references `mysql-best-practices` skill (not duplicating)
- [ ] Index justifications provided for every non-PK index

---

**Back to:** [SDLC Design Skill](../SKILL.md) | **Related:** [Technical Specification](technical-specification.md) | [System Design Document](system-design-document.md)
