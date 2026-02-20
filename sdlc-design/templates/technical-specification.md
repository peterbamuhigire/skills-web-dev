# Technical Specification -- Template & Guide

**Back to:** [SDLC Design Skill](../SKILL.md)

## Purpose

Provides **deep implementation details** -- data structures, algorithms, API internals, error handling, and performance strategies. This is the developer's blueprint for building each component.

## Audience

Developers implementing the system, code reviewers, QA engineers writing test cases.

## When to Create

- After the System Design Document defines components and modules
- Before implementation begins on any module
- When a module is complex enough to require detailed design beyond the SDD

## Typical Length

20-40 pages per major module. Split into `03-tech-spec/` subdirectory files if exceeding 500 lines.

---

## Template

```markdown
# [Project Name] -- Technical Specification

**Version:** 1.0
**Date:** YYYY-MM-DD
**Author:** [Name]
**Status:** Draft | Under Review | Approved
**SDD Reference:** [Link to System Design Document]
**SRS Reference:** [Link to SRS, requirement IDs]

---

## 1. Feature/Component Overview

### 1.1 Purpose
[What this component does, which SRS requirements it satisfies.]

### 1.2 Scope
[Boundaries -- what it covers and what it does not.]

### 1.3 Dependencies
[Other modules, services, libraries this component depends on.]

| Dependency | Type | Version | Purpose |
|-----------|------|---------|---------|
| AuthMiddleware | Internal | -- | JWT/session validation |
| PDO (MySQL) | Library | PHP 8.x built-in | Database access |
| Retrofit | Library | 2.9+ | Android HTTP client |
| Room | Library | Latest BOM | Android local database |

---

## 2. Detailed Design

### 2.1 Class/Module Diagram

[Show key classes, their relationships, and responsibilities.]

+-------------------+       +---------------------+
| ProductController |------>| ProductService      |
| - list()          |       | - getAll(fId): []   |
| - create()        |       | - create(dto): Prod |
| - update()        |       | - update(id, dto)   |
| - delete()        |       | - delete(id): bool  |
+-------------------+       +----------+----------+
                                       |
                            +----------v----------+
                            | ProductRepository   |
                            | - findAll(fId): []  |
                            | - findById(id): ?   |
                            | - save(entity): id  |
                            | - delete(id): bool  |
                            +---------------------+

### 2.2 Data Structures & Models

[Define all data structures with types and constraints.]

#### PHP Model Example

| Field | Type | Nullable | Default | Constraints |
|-------|------|----------|---------|-------------|
| id | int | No | auto_increment | Primary key |
| franchise_id | int | No | -- | FK to franchises.id |
| name | string(255) | No | -- | Unique per franchise |
| sku | string(50) | Yes | null | Unique per franchise if set |
| price | decimal(15,2) | No | 0.00 | >= 0 |
| status | enum | No | 'active' | active, inactive, archived |
| created_at | datetime | No | CURRENT_TIMESTAMP | Immutable after creation |
| updated_at | datetime | No | CURRENT_TIMESTAMP | ON UPDATE CURRENT_TIMESTAMP |

#### Kotlin Data Class Example

```kotlin
data class Product(
    val id: Int,
    val franchiseId: Int,
    val name: String,
    val sku: String?,
    val price: BigDecimal,
    val status: ProductStatus,
    val createdAt: LocalDateTime,
    val updatedAt: LocalDateTime
)

enum class ProductStatus { ACTIVE, INACTIVE, ARCHIVED }
```

### 2.3 Algorithms & Business Logic

[Step-by-step logic for complex operations.]

#### Example: Stock Level Calculation

```
FUNCTION calculateStockLevel(productId, franchiseId, warehouseId):
  1. Fetch opening_balance from stock_levels table
  2. Sum all stock_movements WHERE type = 'IN' AND product_id = productId
  3. Sum all stock_movements WHERE type = 'OUT' AND product_id = productId
  4. current_level = opening_balance + total_in - total_out
  5. IF current_level < 0 THEN raise StockNegativeException
  6. IF current_level < reorder_level THEN queue ReorderAlert
  7. RETURN current_level
```

#### PHP Implementation

```php
declare(strict_types=1);

final class StockService
{
    public function calculateLevel(
        int $productId,
        int $franchiseId,
        int $warehouseId
    ): StockLevelResult {
        $opening = $this->repo->getOpeningBalance(
            $productId, $franchiseId, $warehouseId
        );
        $totalIn = $this->repo->sumMovements(
            $productId, $franchiseId, $warehouseId, 'IN'
        );
        $totalOut = $this->repo->sumMovements(
            $productId, $franchiseId, $warehouseId, 'OUT'
        );

        $current = $opening + $totalIn - $totalOut;

        if ($current < 0) {
            throw new StockNegativeException($productId, $current);
        }

        return new StockLevelResult(
            productId: $productId,
            currentLevel: $current,
            needsReorder: $current < $this->getReorderLevel($productId)
        );
    }
}
```

### 2.4 State Machines

[For stateful components, define states and transitions.]

```
[DRAFT] --submit--> [PENDING_APPROVAL]
[PENDING_APPROVAL] --approve--> [APPROVED]
[PENDING_APPROVAL] --reject--> [REJECTED]
[APPROVED] --fulfill--> [FULFILLED]
[REJECTED] --resubmit--> [PENDING_APPROVAL]
[FULFILLED] --close--> [CLOSED]

Invalid transitions raise InvalidStateTransitionException.
```

---

## 3. API Design

### 3.1 Endpoint Specifications

[Per endpoint, specify all contract details.]

#### POST /api/products/create.php

| Attribute | Value |
|-----------|-------|
| Method | POST |
| Auth | JWT (mobile) or Session (web) |
| Permission | `products.create` |
| Rate Limit | 60 requests/minute per user |
| Content-Type | application/json |

**Request Body:**
```json
{
  "name": "Widget A",
  "sku": "WDG-001",
  "price": 25.50,
  "category_id": 3,
  "status": "active"
}
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "Product created successfully",
  "data": {
    "id": 42,
    "name": "Widget A",
    "sku": "WDG-001",
    "price": 25.50,
    "created_at": "2026-02-20T10:30:00Z"
  }
}
```

**Error Responses:**

| HTTP Status | Error Code | Cause |
|------------|------------|-------|
| 400 | VALIDATION_ERROR | Missing required fields or invalid values |
| 401 | UNAUTHORIZED | Missing or expired token |
| 403 | FORBIDDEN | User lacks `products.create` permission |
| 409 | DUPLICATE_ENTRY | SKU already exists for this franchise |
| 500 | INTERNAL_ERROR | Unexpected server error |

See: `api-error-handling` skill for error response format.

### 3.2 Pagination Strategy

All list endpoints use offset-based pagination:

```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 25,
    "total": 142,
    "total_pages": 6
  }
}
```

See: `api-pagination` skill for full implementation details.

---

## 4. Database Design

### 4.1 Table Definitions

[Per table, provide complete column definitions.]

#### Table: products

| Column | Type | Nullable | Default | Constraints |
|--------|------|----------|---------|-------------|
| id | INT UNSIGNED | No | AUTO_INCREMENT | PK |
| franchise_id | INT UNSIGNED | No | -- | FK franchises(id) |
| name | VARCHAR(255) | No | -- | -- |
| sku | VARCHAR(50) | Yes | NULL | UNIQUE(franchise_id, sku) |
| price | DECIMAL(15,2) | No | 0.00 | CHECK(price >= 0) |
| status | ENUM('active','inactive','archived') | No | 'active' | -- |
| created_at | DATETIME | No | CURRENT_TIMESTAMP | -- |
| updated_at | DATETIME | No | CURRENT_TIMESTAMP | ON UPDATE |

**Indexes:**
| Name | Columns | Type | Justification |
|------|---------|------|---------------|
| PRIMARY | id | PK | Row identity |
| idx_products_franchise | franchise_id | INDEX | Tenant-scoped queries |
| uq_products_franchise_sku | franchise_id, sku | UNIQUE | SKU uniqueness per tenant |
| idx_products_status | franchise_id, status | INDEX | Filtered listing queries |

See: `mysql-best-practices` skill for indexing standards.
See: Database Design Document for complete schema.

### 4.2 Stored Procedures

| Name | Purpose | Parameters | Return |
|------|---------|-----------|--------|
| sp_create_product | Insert product with validation | p_franchise_id, p_name, p_sku, p_price | New product ID |
| sp_get_stock_level | Calculate current stock for a product | p_product_id, p_franchise_id, p_warehouse_id | Current level (INT) |
| sp_close_pos_session | Close POS session with supervisor auth | p_session_id, p_supervisor_id | Success/failure |

### 4.3 Triggers

| Trigger | Table | Event | Timing | Purpose |
|---------|-------|-------|--------|---------|
| tr_products_audit_insert | products | INSERT | AFTER | Log creation to audit_trail |
| tr_products_audit_update | products | UPDATE | AFTER | Log changes with old/new values |
| tr_stock_movement_update_level | stock_movements | INSERT | AFTER | Recalculate stock_levels |

### 4.4 Migration Script Format

```sql
-- Migration: YYYY-MM-DD-description.sql
-- Author: [Name]
-- Purpose: [What this migration does]
-- Idempotent: Yes (safe to run multiple times)
-- Destructive: No (does not delete data)

-- Pre-check: Verify table exists / does not exist
-- [SQL statements]
-- Post-check: Verify migration applied correctly
```

---

## 5. Error Handling Strategy

### 5.1 Error Categories

| Category | HTTP Range | Example | Handling |
|----------|-----------|---------|----------|
| Validation | 400 | Missing required field | Return field-specific errors |
| Authentication | 401 | Expired JWT token | Redirect to login / refresh |
| Authorization | 403 | Insufficient permissions | Show "Access Denied" message |
| Not Found | 404 | Record does not exist | Show "Not Found" message |
| Conflict | 409 | Duplicate entry | Show specific constraint violation |
| Server Error | 500 | Database connection failure | Log full details, show generic message |

### 5.2 Error Response Format

See: `api-error-handling` skill for the standardized error envelope:
```json
{
  "success": false,
  "message": "Human-readable error description",
  "error_code": "SPECIFIC_ERROR_CODE",
  "errors": { "field": ["Specific validation message"] }
}
```

---

## 6. Configuration & Environment Variables

| Variable | Dev | Staging | Prod | Purpose |
|----------|-----|---------|------|---------|
| DB_HOST | localhost | staging-db.host | prod-db.host | Database server |
| DB_NAME | project_dev | project_staging | project_prod | Database name |
| JWT_SECRET | dev-secret-key | [rotated monthly] | [rotated monthly] | JWT signing key |
| JWT_EXPIRY | 3600 | 3600 | 3600 | Access token lifetime (seconds) |
| APP_DEBUG | true | false | false | Debug mode |
| LOG_LEVEL | debug | info | warning | Logging verbosity |

---

## 7. Performance Considerations

### 7.1 Caching Strategy

| Cache Type | Technology | TTL | Use Case |
|-----------|-----------|-----|----------|
| PHP OpCache | Built-in | Until deploy | Compiled PHP bytecode |
| Query Cache | Application-level | 5 min | Frequently accessed lookups |
| Session Cache | File/Redis | 30 min | Active user sessions |
| Android Room | SQLite | Until sync | Offline data cache |

### 7.2 Query Optimization

- All WHERE clauses on franchise_id must hit an index
- Avoid SELECT * -- specify exact columns needed
- Use LIMIT for paginated queries (never fetch all rows)
- Complex reports use pre-aggregated views or stored procedures
- N+1 query prevention: use JOINs or batch fetching

### 7.3 Lazy Loading

- Android: Load list data on-demand with Paging 3 library
- Web: DataTables server-side processing for tables > 100 rows
- Images: Lazy-load below-the-fold images with loading="lazy"

---

## 8. Dependencies & Libraries

| Library | Version | Purpose | License |
|---------|---------|---------|---------|
| PHP | 8.x | Backend runtime | PHP License |
| MySQL Connector | 8.x | Database driver | GPL |
| mPDF | 8.x | PDF generation | GPL |
| Retrofit | 2.9+ | Android HTTP client | Apache 2.0 |
| Room | BOM latest | Android local database | Apache 2.0 |
| Hilt | BOM latest | Dependency injection | Apache 2.0 |
| OkHttp | 4.x | HTTP + interceptors | Apache 2.0 |
| Kotlin Coroutines | 1.7+ | Async programming | Apache 2.0 |

---

## 9. Known Limitations & Technical Debt

| Item | Description | Impact | Plan |
|------|------------|--------|------|
| [Limitation 1] | [Description] | [Impact on users/system] | [When/how to address] |
| [Limitation 2] | [Description] | [Impact on users/system] | [When/how to address] |
```

---

## Section-by-Section Guidance

| Section | Key Guidance |
|---------|-------------|
| Feature Overview | Reference specific SRS requirement IDs (FR-MOD-001). |
| Class Diagrams | Show relationships (inheritance, composition, dependency), not every method. |
| Data Structures | Include all constraints -- types, nullable, defaults, foreign keys. |
| Algorithms | Use pseudocode for logic, real code for implementation examples. |
| State Machines | Define ALL valid transitions and what happens on invalid ones. |
| API Design | Include request, success response, AND error responses for every endpoint. |
| Database | Cross-reference `mysql-best-practices`; include indexes with justification. |
| Error Handling | Cross-reference `api-error-handling`; categorize by HTTP status range. |
| Performance | Be specific: "cache for 5 minutes" not "use caching." |
| Dependencies | Pin versions. Note license compatibility. |

## Anti-Patterns

| Anti-Pattern | Why It Fails | Do This Instead |
|-------------|-------------|-----------------|
| Pseudocode only, no real code | Developers guess at implementation | Include working PHP/Kotlin examples |
| API specs without error responses | Consumers can't handle failures | Document ALL error codes per endpoint |
| No state machine for stateful entities | Invalid state transitions in production | Define states and transitions explicitly |
| "Use caching" without specifics | Nobody knows what to cache or for how long | Specify cache type, TTL, invalidation |
| Missing franchise_id in table definitions | Tenant data leakage | Always include franchise_id for tenant tables |
| Vague performance targets | Unmeasurable | Use numbers: "< 500ms p95", "< 100 rows per page" |

## Quality Checklist

- [ ] All SRS requirement IDs referenced in relevant sections
- [ ] Class/module diagrams show key relationships
- [ ] All data structures include types, constraints, and defaults
- [ ] Complex algorithms have both pseudocode and real code examples
- [ ] Stateful components have state machine diagrams
- [ ] Every API endpoint has request, success, and error response specs
- [ ] Database tables include franchise_id where tenant-scoped
- [ ] Error handling references `api-error-handling` skill
- [ ] Performance targets are numeric and measurable
- [ ] Dependencies list includes versions and licenses
- [ ] Known limitations documented with mitigation plans

---

**Back to:** [SDLC Design Skill](../SKILL.md) | **Related:** [System Design Document](system-design-document.md) | [API Documentation](api-documentation.md)
