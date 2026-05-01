# Code Documentation Standards -- Template & Guide

**Back to:** [SDLC Design Skill](../SKILL.md)

## Purpose

Establishes **mandatory standards** for inline comments, docstrings, file headers, and code-level documentation across all languages in the stack. These standards ensure code is understandable, maintainable, and reviewable by all team members.

## Audience

All developers (PHP, Kotlin, SQL, JavaScript), code reviewers, QA engineers.

## When to Create

- At project kickoff, before any code is written
- When onboarding new team members
- When standardizing an existing codebase

## Typical Length

10-20 pages.

---

## Template

```markdown
# [Project Name] -- Code Documentation Standards

**Version:** 1.0
**Date:** YYYY-MM-DD
**Author:** [Name]
**Status:** Draft | Under Review | Approved

---

## 1. Documentation Philosophy

### Core Principles

1. **Explain "why", not "what"** -- Code shows WHAT it does. Comments explain WHY.
2. **Self-documenting code first** -- Use descriptive names, small functions, clear structure.
3. **Document the contract** -- Every public interface gets a docblock (parameters, return, throws).
4. **Keep docs near code** -- Documentation that lives with the code stays current.
5. **Update with every change** -- Stale comments are worse than no comments.

### When to Comment

**Yes (docblock/comment):** Public classes/methods, complex business logic, non-obvious algorithms, workarounds (link ticket), configuration values.
**No:** Simple getters/setters, obvious loops/conditionals, self-documenting code.

---

## 2. PHP Documentation Standards

### 2.1 File Headers

Every PHP file MUST start with a file-level docblock:

```php
<?php
declare(strict_types=1);

/**
 * Product management service for CRUD operations.
 *
 * Handles product creation, updates, retrieval, and deletion
 * with franchise-scoped data access.
 *
 * @package    App\Services
 * @author     [Name]
 * @created    YYYY-MM-DD
 * @since      1.0.0
 */
```

### 2.2 Class Docblocks

```php
/**
 * Manages product inventory across warehouse locations.
 *
 * Provides stock level calculations, movement tracking, and
 * reorder alerts for franchise-scoped products.
 *
 * @package App\Services\Inventory
 * @since   1.0.0
 * @see     ProductRepository For data access layer
 * @see     mysql-best-practices skill For database standards
 */
final class StockService
{
    // ...
}
```

### 2.3 Method Docblocks

```php
/**
 * Calculate current stock level for a product at a warehouse.
 *
 * Computes: opening_balance + total_in - total_out.
 * Triggers reorder alert if level falls below reorder threshold.
 *
 * @param int $productId   Product to check
 * @param int $franchiseId Tenant scope (from auth, never from client)
 * @param int $warehouseId Warehouse location
 *
 * @return StockLevelResult Contains current level and reorder flag
 *
 * @throws StockNegativeException If calculated level is below zero
 * @throws ProductNotFoundException If product does not exist
 */
public function calculateLevel(
    int $productId,
    int $franchiseId,
    int $warehouseId
): StockLevelResult {
    // ...
}
```

### 2.4 Inline Comments (PHP)

```php
// Good: explains WHY
// Franchise ID comes from JWT token, never from request body,
// to prevent tenant impersonation attacks.
$franchiseId = $auth->getFranchiseId();

// Good: explains business rule
// Discount capped at 30% per company policy (see BR-SALES-012)
$maxDiscount = min($requestedDiscount, 30.0);

// Bad: explains WHAT (code already says this)
// Get the user
$user = $userRepo->find($userId);

// Bad: commented-out code (remove it; use git history)
// $oldPrice = $product->getOriginalPrice();
```

### 2.5 PHPDoc Type References

| Annotation | Usage | Example |
|-----------|-------|---------|
| @param | Every method parameter | @param int $productId |
| @return | Return type (even void) | @return StockLevelResult |
| @throws | Every exception that can be thrown | @throws NotFoundException |
| @see | Cross-reference to related code | @see ProductRepository |
| @since | Version when added | @since 1.2.0 |
| @deprecated | Mark for removal | @deprecated 2.0.0 Use newMethod() |
| @todo | Planned improvements | @todo Add caching (JIRA-123) |

---

## 3. Kotlin Documentation Standards

### 3.1 KDoc Format

```kotlin
/**
 * Manages product data synchronization between remote API and local Room database.
 *
 * Implements offline-first strategy: reads from Room, syncs with API on connectivity.
 * All operations are franchise-scoped via the authenticated user's token.
 *
 * @property apiService Remote API client (Retrofit)
 * @property dao Local database access (Room)
 * @property connectivity Network state monitor
 *
 * @see ProductApiService For API contract
 * @see ProductDao For local database queries
 */
class ProductRepositoryImpl @Inject constructor(
    private val apiService: ProductApiService,
    private val dao: ProductDao,
    private val connectivity: ConnectivityMonitor
) : ProductRepository {
    // ...
}
```

### 3.2 Function Documentation

```kotlin
/**
 * Fetches paginated product list, preferring local cache when offline.
 *
 * Online: fetches from API, caches to Room, returns API data.
 * Offline: returns cached Room data with a stale-data indicator.
 *
 * @param page Page number (1-based)
 * @param perPage Items per page (default 25, max 100)
 * @return [Result] containing [PaginatedProducts] or error
 * @throws UnauthorizedException if token is expired and refresh fails
 */
suspend fun getProducts(page: Int, perPage: Int = 25): Result<PaginatedProducts>
```

### 3.3 Compose Component Documentation

```kotlin
/**
 * Product list screen with pull-to-refresh and infinite scroll.
 *
 * Displays products in a LazyColumn with shimmer loading states.
 * Handles empty state, error state, and offline indicator.
 *
 * @param viewModel Manages product list state and pagination
 * @param onProductClick Navigation callback when a product is tapped
 * @param modifier Layout modifier for parent composition
 *
 * @sample ProductListScreenPreview
 */
@Composable
fun ProductListScreen(
    viewModel: ProductListViewModel = hiltViewModel(),
    onProductClick: (productId: Int) -> Unit,
    modifier: Modifier = Modifier
) {
    // ...
}
```

### 3.4 ViewModel Documentation

```kotlin
/**
 * ViewModel for the product list screen.
 *
 * **State:** [ProductListUiState] -- loading, data, error, empty
 * **Events:** [ProductListEvent] -- refresh, load next page, search
 * **Side Effects:** Navigation to product detail, error toasts
 *
 * @param getProductsUseCase Fetches paginated products
 * @param deleteProductUseCase Deletes a product with confirmation
 */
@HiltViewModel
class ProductListViewModel @Inject constructor(
    private val getProductsUseCase: GetProductsUseCase,
    private val deleteProductUseCase: DeleteProductUseCase
) : ViewModel() {
    // ...
}
```

### 3.5 Package-Level Documentation

Create `package-info.kt` in each major package:

```kotlin
/**
 * Product management feature module.
 *
 * Contains presentation (screens, viewmodels), domain (use cases, models),
 * and data (repository, API service, DAO) layers for the Products module.
 *
 * Architecture: MVVM + Clean Architecture with Hilt DI.
 */
package com.example.app.features.products
```

---

## 4. SQL Documentation Standards

### 4.1 Stored Procedure Headers

```sql
-- ============================================================
-- Procedure: sp_create_invoice
-- Purpose:   Create invoice with line items in a single transaction
-- Parameters:
--   p_franchise_id  INT UNSIGNED  - Tenant identifier (from auth)
--   p_customer_id   INT UNSIGNED  - Customer placing the order
--   p_cashier_id    INT UNSIGNED  - User recording the sale
--   p_items         JSON          - Array: [{product_id, qty, unit_price}]
-- Returns:   INT - New invoice ID (or -1 on failure)
-- Business Rules:
--   - Stock levels must be sufficient for all items
--   - Invoice number auto-generated per franchise sequence
--   - Audit trail entry created automatically (via trigger)
-- Example:
--   CALL sp_create_invoice(1, 42, 5,
--     '[{"product_id":1,"qty":2,"unit_price":25.00}]');
-- Author:    [Name]
-- Created:   2026-02-20
-- Modified:  2026-02-20 - Initial creation
-- ============================================================
DELIMITER //
CREATE PROCEDURE sp_create_invoice(...)
BEGIN
    -- Implementation
END //
DELIMITER ;
```

### 4.2 Trigger Documentation

```sql
-- ============================================================
-- Trigger:      tr_invoices_audit_insert
-- Table:        invoices
-- Event:        INSERT
-- Timing:       AFTER
-- Purpose:      Record invoice creation in audit_trail table
-- Side Effects: 1 INSERT into audit_trail per invoice created
-- Dependencies: audit_trail table must exist
-- Author:       [Name]
-- ============================================================
```

### 4.3 Migration File Headers

```sql
-- ============================================================
-- Migration: 2026-02-20-add-sku-to-products.sql
-- Author:    [Name]
-- Purpose:   Add SKU column for barcode scanning feature (FR-INV-015)
-- Idempotent: Yes (uses IF NOT EXISTS)
-- Destructive: No
-- Rollback:  DROP COLUMN sku (see commented section at bottom)
-- Tested On: Dev (2026-02-20), Staging (2026-02-20)
-- ============================================================
```

### 4.4 Inline SQL Comments

```sql
-- Good: explains WHY the index exists
CREATE INDEX idx_invoices_franchise_date
ON invoices (franchise_id, created_at DESC);
-- Optimizes dashboard "recent sales" query which filters by franchise
-- and sorts by date. Without this, full table scan on 500K+ rows.

-- Good: explains business rule
WHERE status != 'voided'  -- Voided invoices excluded from revenue reports (BR-FIN-003)
```

---

## 5. JavaScript Documentation Standards

### 5.1 Function Documentation (JSDoc)

```javascript
/**
 * Submit the product form via AJAX and handle response.
 *
 * Validates form fields client-side before submission.
 * Shows SweetAlert2 success/error message on completion.
 *
 * @param {HTMLFormElement} form - The product form element
 * @param {string} action - API action: 'create' or 'update'
 * @returns {Promise<Object>} API response data
 * @throws {Error} If network request fails
 */
async function submitProductForm(form, action) {
    // ...
}
```

### 5.2 Module-Level Documentation

```javascript
/**
 * Product Management Module
 *
 * Handles DataTable initialization, form submission, delete confirmation,
 * and real-time search for the products page.
 *
 * Dependencies: jQuery, DataTables, SweetAlert2, Flatpickr
 * API Endpoints: /api/products/*.php
 */
```

---

## 6. README Standards

### 6.1 Module-Level READMEs

Each major module directory should have a README.md with: Purpose, Directory Structure, Setup, API Endpoints (table with Method/Endpoint/Auth/Permission/Description), Database Tables, and Configuration sections.

---

## 7. Documentation Maintenance

### 7.1 When to Update Documentation

| Trigger | What to Update |
|---------|---------------|
| New public method/class | Add docblock immediately |
| Method signature change | Update @param, @return, @throws |
| Business rule change | Update inline comment referencing the rule |
| Bug fix with non-obvious cause | Add comment explaining the fix and why |
| API endpoint change | Update README and API docs |
| Database schema change | Update Database Design Document |

### 7.2 Stale Documentation Detection

- PR reviews MUST check that documentation matches code changes
- Any method with a "last modified" date > 6 months should be reviewed
- Automated: PHPDoc and KDoc generators flag undocumented public methods

### 7.3 Documentation in PR Process

- [ ] All new public methods have docblocks
- [ ] All changed method signatures have updated docblocks
- [ ] Complex logic has inline comments explaining "why"
- [ ] No commented-out code (use git history instead)
- [ ] README updated if API endpoints or setup steps changed
- [ ] Migration files have proper headers

---

## 8. Tools & Automation

| Tool | Language | Purpose | Command |
|------|----------|---------|---------|
| PHPDoc | PHP | Generate API documentation from docblocks | `phpdoc run` |
| Dokka | Kotlin | Generate KDoc documentation | `./gradlew dokkaHtml` |
| Markdownlint | All | Lint markdown files | `markdownlint '**/*.md'` |
| PHP-CS-Fixer | PHP | Enforce docblock formatting | `php-cs-fixer fix` |
| Detekt | Kotlin | Flag missing KDoc on public APIs | `./gradlew detekt` |
```

---

## Section-by-Section Guidance

| Section | Key Guidance |
|---------|-------------|
| Philosophy | Establish "why not what" principle before any standards. |
| PHP Standards | Follow PSR-5 PHPDoc conventions. Every public method gets a docblock. |
| Kotlin Standards | Use KDoc format. Document state, events, side effects for ViewModels. |
| SQL Standards | Every stored procedure and trigger gets a header block. |
| JavaScript | Use JSDoc for public functions. Document module dependencies. |
| READMEs | One per major module directory. Keep endpoint table current. |
| Maintenance | Integrate doc checks into PR review process. |
| Tools | Set up automation early; fix incrementally. |

## Anti-Patterns

| Anti-Pattern | Why It Fails | Do This Instead |
|-------------|-------------|-----------------|
| Over-commenting obvious code | Noise; developers ignore all comments | Comment only non-obvious logic |
| Outdated comments | Misleading; worse than no comments | Update comments with code changes |
| Commented-out code | Clutters codebase; use version control | Delete it; use git history |
| No docblocks on public APIs | Consumers must read implementation | Docblock every public method |
| Comments that say "what" not "why" | Redundant with the code itself | Explain business rules and rationale |
| Giant comment blocks before simple code | Distracting, low signal | Short 1-line comments for simple clarifications |
| Documentation in separate wiki only | Goes stale immediately | Keep docs near the code |
| @todo without ticket reference | Never gets done | Always link to issue tracker: @todo (JIRA-123) |

## Quality Checklist

- [ ] Documentation philosophy established and communicated
- [ ] PHP docblock standards defined with examples
- [ ] Kotlin KDoc standards defined with examples
- [ ] SQL documentation standards defined with examples
- [ ] JavaScript documentation standards defined with examples
- [ ] README template provided for module directories
- [ ] Documentation maintenance triggers defined
- [ ] PR review checklist includes documentation verification
- [ ] Automated tools configured (PHPDoc, Dokka, linters)
- [ ] No example uses "what" comments -- all demonstrate "why"
- [ ] Commented-out code policy: zero tolerance, use git history

---

**Back to:** [SDLC Design Skill](../SKILL.md) | **Related:** [Technical Specification](technical-specification.md) | [API Documentation](api-documentation.md)
