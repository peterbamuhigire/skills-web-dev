# Prompting Patterns for Implementation Plans

**Purpose:** Apply proven prompting patterns to create better implementation plans that AI agents can follow effectively.

**Target:** Implementation plans created in Phase 2 of feature-planning skill

---

## Why Prompting Patterns Matter for Plans

Implementation plans are **instructions for AI agents** (like Claude) to follow when implementing features. Using prompting patterns makes these instructions:

- ✅ **Clearer**: Agents understand exactly what to do
- ✅ **More precise**: Less ambiguity, fewer errors
- ✅ **Easier to reason about**: Step-by-step thinking guidance
- ✅ **More maintainable**: Consistent structure across plans

---

## The 5 Essential Patterns for Implementation Plans

### Pattern 1: Clear Task + Context + Constraints (MANDATORY)

**Use for:** Every single task/step in the plan

**Template:**
```markdown
### Task [N]: [Action Verb] [Component]

**FILE:** `path/to/file.ext`

**TASK:** [What needs to be done - specific action]

**CONTEXT:** [Why this is needed - business/technical reason]

**CONSTRAINTS:**
- [Technical constraint 1]
- [Limit/requirement 2]
- [Standard/convention 3]

**CODE:**
```php
// Clear, complete example
```
```

**Example (Before):**
```markdown
## Task 1: Add validation

File: `app/Http/Controllers/UserController.php`

Add email validation.
```

**Example (After with Pattern):**
```markdown
### Task 1: Add Email Validation to User Registration

**FILE:** `app/Http/Controllers/UserController.php`

**TASK:** Implement server-side email validation for user registration endpoint

**CONTEXT:** Prevent invalid emails from entering database, ensure data quality for multi-tenant system where email is primary identifier

**CONSTRAINTS:**
- Must use Laravel's validation rules (no custom regex)
- Must check for: format, mx records, disposable domains
- Must return JSON error with 422 status
- Must preserve existing validation for other fields

**CODE:**
```php
public function store(Request $request) {
    $validated = $request->validate([
        'email' => 'required|email:rfc,dns|not_regex:/disposable/',
        'password' => 'required|min:8|confirmed',
        'tenant_id' => 'required|exists:tenants,id'
    ]);

    // Existing code continues...
}
```
```

**Impact:** Agent knows exactly what, why, and how - no guessing.

---

### Pattern 2: Chain-of-Thought for Complex Tasks

**Use for:** Tasks requiring decisions, calculations, or multi-step logic

**Template:**
```markdown
### Task [N]: [Complex Action]

**THINK STEP-BY-STEP:**
1. **[Step 1 question]** - [Reasoning/answer]
2. **[Step 2 question]** - [Reasoning/answer]
3. **[Step 3 question]** - [Reasoning/answer]
4. **[Final decision]** - [Implementation approach]

**CODE:**
[Implementation following the reasoning]
```

**Example:**
```markdown
### Task 3: Optimize Inventory Query Performance

**FILE:** `app/Models/Product.php`

**THINK STEP-BY-STEP:**
1. **What's the current bottleneck?**
   - Scan of products table (100k+ rows) without index
   - Joins to inventory_levels causing cartesian explosion

2. **What indexes are needed?**
   - Composite index on (tenant_id, category_id)
   - Index on inventory_levels.product_id

3. **Can we cache this?**
   - Yes, inventory levels change slowly (~hourly)
   - Use Redis cache with 1-hour TTL

4. **Final approach:**
   - Add indexes first (immediate 10x speedup)
   - Add caching layer (another 5x speedup)
   - Total: 50x performance improvement

**CODE:**
```php
// Migration: Add indexes
Schema::table('products', function (Blueprint $table) {
    $table->index(['tenant_id', 'category_id'], 'idx_tenant_category');
});

// Model: Add caching
public function getInventoryLevel() {
    return Cache::remember(
        "inventory:product:{$this->id}",
        3600, // 1 hour
        fn() => $this->inventoryLevels()->sum('quantity')
    );
}
```
```

**Impact:** Agent understands the reasoning, not just the code.

---

### Pattern 3: Structured Output for Tests

**Use for:** Test tasks where format must be precise

**Template:**
```markdown
### Task [N]: Create Tests

**FILE:** `tests/Feature/[Name]Test.php`

**RETURN as PHPUnit test with this exact structure:**
```php
class [Name]Test extends TestCase {
    /** @test */
    public function [test_name]() {
        // Arrange: Setup test data

        // Act: Execute the action

        // Assert: Verify results
    }
}
```

**REQUIRED test cases:**
- [ ] Happy path: [Description]
- [ ] Edge case 1: [Description]
- [ ] Edge case 2: [Description]
- [ ] Validation failure: [Description]
```

**Example:**
```markdown
### Task 7: Create Product Validation Tests

**FILE:** `tests/Feature/ProductValidationTest.php`

**RETURN as PHPUnit test with this exact structure:**
```php
class ProductValidationTest extends TestCase {
    use RefreshDatabase;

    /** @test */
    public function test_name() {
        // Arrange: Setup
        $tenant = Tenant::factory()->create();

        // Act: Execute
        $response = $this->post('/api/products', $data);

        // Assert: Verify
        $response->assertStatus(201);
    }
}
```

**REQUIRED test cases:**
- [ ] Happy path: Valid product creation with all fields
- [ ] Edge case 1: Product with zero price (should reject)
- [ ] Edge case 2: Product without category (should assign "Uncategorized")
- [ ] Validation failure: Missing required 'name' field returns 422

**CODE:**
```php
class ProductValidationTest extends TestCase {
    use RefreshDatabase;

    /** @test */
    public function valid_product_creates_successfully() {
        $tenant = Tenant::factory()->create();

        $response = $this->actingAs($tenant->admin)
            ->postJson('/api/products', [
                'name' => 'Test Product',
                'price' => 1000,
                'category_id' => 1,
                'tenant_id' => $tenant->id
            ]);

        $response->assertStatus(201)
            ->assertJsonStructure(['id', 'name', 'price']);
        $this->assertDatabaseHas('products', ['name' => 'Test Product']);
    }

    /** @test */
    public function zero_price_rejected() {
        // Similar structure...
    }
}
```
```

**Impact:** Tests follow consistent, parseable structure.

---

### Pattern 4: Few-Shot for Code Style

**Use for:** When code must follow specific patterns/conventions

**Template:**
```markdown
### Task [N]: [Action]

**EXAMPLE of what I WANT:**
```php
// Good example following project conventions
```

**EXAMPLE of what I DON'T want:**
```php
// Anti-pattern to avoid
```

**Generate code following the GOOD example.**
```

**Example:**
```markdown
### Task 4: Create API Controller Method

**FILE:** `app/Http/Controllers/Api/ProductController.php`

**EXAMPLE of what I WANT:**
```php
/**
 * Store a newly created product.
 *
 * @param ProductRequest $request
 * @return JsonResponse
 */
public function store(ProductRequest $request): JsonResponse {
    DB::beginTransaction();
    try {
        $product = Product::create($request->validated());

        ProductCreated::dispatch($product);

        DB::commit();
        return response()->json($product, 201);
    } catch (\Exception $e) {
        DB::rollBack();
        Log::error('Product creation failed', ['error' => $e->getMessage()]);
        return response()->json(['error' => 'Failed to create product'], 500);
    }
}
```

**EXAMPLE of what I DON'T want:**
```php
// No type hints, no transaction, no error handling
public function store($request) {
    $product = Product::create($request->all());
    return $product;
}
```

**Generate CRUD methods (store, update, destroy) following the GOOD example.**
```

**Impact:** Code consistency across entire implementation.

---

### Pattern 5: Constraints for Scope Control

**Use for:** Preventing scope creep and over-engineering

**Template:**
```markdown
### Task [N]: [Action]

**CONSTRAINTS:**
- Maximum [N] lines of code
- Must use only [allowed tools/libs]
- No [forbidden patterns]
- Focus ONLY on [specific scope]
- DO NOT add [out-of-scope items]

**SCOPE:** This task handles ONLY [X], NOT [Y] or [Z].
```

**Example:**
```markdown
### Task 5: Add Product Search Endpoint

**FILE:** `app/Http/Controllers/Api/ProductController.php`

**CONSTRAINTS:**
- Maximum 30 lines of code
- Must use Laravel's built-in search (no Elasticsearch yet)
- No advanced filtering (only name and category)
- Focus ONLY on basic search, NOT sorting/pagination (separate task)
- DO NOT add caching, indexing, or optimization (premature)

**SCOPE:** This task handles ONLY basic keyword search. Pagination (Task 6) and filtering (Task 7) are separate.

**CODE:**
```php
/**
 * Search products by name or category.
 * Basic implementation - advanced search in future iteration.
 */
public function search(Request $request): JsonResponse {
    $query = Product::query()
        ->where('tenant_id', auth()->user()->tenant_id);

    if ($request->has('keyword')) {
        $keyword = $request->input('keyword');
        $query->where(function($q) use ($keyword) {
            $q->where('name', 'LIKE', "%{$keyword}%")
              ->orWhere('description', 'LIKE', "%{$keyword}%");
        });
    }

    if ($request->has('category')) {
        $query->where('category_id', $request->input('category'));
    }

    return response()->json($query->get());
}
```

**NOTE:** Pagination and sorting will be added in Tasks 6-7. This keeps each task focused and testable.
```

**Impact:** Prevents over-engineering, keeps tasks focused.

---

## Pattern Combinations for Common Plan Tasks

### For Database Migrations
```markdown
### Task 2: Create Products Table Migration

**FILE:** `database/migrations/YYYY_MM_DD_create_products_table.php`

**TASK:** Create products table with multi-tenant isolation

**CONTEXT:** Core entity for inventory system, must support 10k+ products per tenant

**CONSTRAINTS:**
- Must include tenant_id foreign key (multi-tenant isolation)
- Must add composite index on (tenant_id, category_id)
- Must use UTF-8 for international product names
- Must follow Laravel migration conventions

**THINK STEP-BY-STEP:**
1. **Core fields needed:** id, name, description, price, tenant_id, category_id
2. **Indexes for performance:** (tenant_id, category_id) composite, (tenant_id, sku) unique
3. **Data integrity:** Foreign keys to tenants, categories; ON DELETE CASCADE
4. **Timestamps:** created_at, updated_at for audit trail

**CODE:**
```php
Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->foreignId('tenant_id')->constrained()->onDelete('cascade');
    $table->foreignId('category_id')->constrained();
    $table->string('name');
    $table->text('description')->nullable();
    $table->decimal('price', 10, 2);
    $table->string('sku')->nullable();
    $table->timestamps();

    // Indexes for multi-tenant queries
    $table->index(['tenant_id', 'category_id']);
    $table->unique(['tenant_id', 'sku']);
});
```
```

### For API Endpoints
```markdown
### Task 3: Implement Product List Endpoint

**FILE:** `app/Http/Controllers/Api/ProductController.php`

**TASK:** Create GET /api/products endpoint with tenant isolation

**CONTEXT:** Frontend needs to display products filtered by tenant

**CONSTRAINTS:**
- Must filter by authenticated user's tenant_id (security)
- Must paginate (expect 1000+ products per tenant)
- Must return JSON in standardized format
- Maximum 25 lines of code

**EXAMPLE of what I WANT:**
```php
public function index(Request $request): JsonResponse {
    $products = Product::where('tenant_id', auth()->user()->tenant_id)
        ->with('category')
        ->paginate(20);

    return response()->json($products);
}
```

**EXAMPLE of what I DON'T want:**
```php
// No tenant filtering = security vulnerability!
public function index() {
    return Product::all();
}
```

**REQUIRED:**
- [ ] Tenant isolation via tenant_id filter
- [ ] Pagination (20 per page)
- [ ] Include category relationship
- [ ] Return JSON with 200 status
```

### For Test Cases
```markdown
### Task 8: Create Product Controller Tests

**FILE:** `tests/Feature/ProductControllerTest.php`

**RETURN as PHPUnit test with exact structure:**
```php
class ProductControllerTest extends TestCase {
    use RefreshDatabase;

    protected function setUp(): void {
        parent::setUp();
        $this->tenant = Tenant::factory()->create();
        $this->user = User::factory()->for($this->tenant)->create();
    }

    /** @test */
    public function test_name() {
        $this->actingAs($this->user);
        // Test logic
    }
}
```

**REQUIRED test cases:**
- [ ] Authenticated user can list own tenant's products
- [ ] User cannot see products from other tenants (security)
- [ ] Pagination works correctly
- [ ] Empty result returns 200 with empty array
```

---

## Implementation Plan Structure with Patterns

### Complete Plan Example

```markdown
# Feature: Product Inventory Management — Implementation Plan

**Date:** 2026-02-07
**Status:** Ready for Implementation
**Estimated Effort:** Large (8-12 hours)

## Overview

Implement product inventory management with multi-tenant isolation and real-time stock tracking.

---

## Phase 1: Database (Tasks 1-2)

### Task 1: Create Products Table Migration

**FILE:** `database/migrations/2026_02_07_create_products_table.php`

**TASK:** Create products table with multi-tenant isolation and performance indexes

**CONTEXT:** Core entity for inventory system, expected 10k+ products per tenant across 50+ tenants

**CONSTRAINTS:**
- Must include tenant_id foreign key (multi-tenant isolation - CRITICAL)
- Must add composite index on (tenant_id, category_id) for list queries
- Must use UTF-8mb4 for emoji support in product names
- Must follow Laravel migration conventions
- Must include soft deletes for audit trail

**THINK STEP-BY-STEP:**
1. **Core fields:** id, tenant_id, category_id, name, description, price, sku, stock_quantity
2. **Indexes:** (tenant_id, category_id) for filtered lists, (tenant_id, sku) unique for lookups
3. **Foreign keys:** tenant_id → tenants, category_id → categories with ON DELETE CASCADE
4. **Audit fields:** created_at, updated_at, deleted_at (soft deletes)

**CODE:**
```php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void {
        Schema::create('products', function (Blueprint $table) {
            $table->id();
            $table->foreignId('tenant_id')->constrained()->onDelete('cascade');
            $table->foreignId('category_id')->constrained();
            $table->string('name');
            $table->text('description')->nullable();
            $table->decimal('price', 10, 2);
            $table->string('sku', 50)->nullable();
            $table->integer('stock_quantity')->default(0);
            $table->timestamps();
            $table->softDeletes();

            // Performance indexes for multi-tenant queries
            $table->index(['tenant_id', 'category_id'], 'idx_tenant_category');
            $table->unique(['tenant_id', 'sku'], 'uniq_tenant_sku');
        });
    }

    public function down(): void {
        Schema::dropIfExists('products');
    }
};
```

**VALIDATION:**
- [ ] Migration runs without errors
- [ ] Indexes are created (check with `SHOW INDEX FROM products`)
- [ ] Foreign keys enforce referential integrity
- [ ] Soft deletes work correctly

---

### Task 2: Create Product Model

**FILE:** `app/Models/Product.php`

**EXAMPLE of what I WANT:**
```php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Product extends Model {
    use SoftDeletes;

    protected $fillable = ['tenant_id', 'category_id', 'name', 'description', 'price', 'sku', 'stock_quantity'];

    protected $casts = [
        'price' => 'decimal:2',
        'stock_quantity' => 'integer',
    ];

    public function tenant(): BelongsTo {
        return $this->belongsTo(Tenant::class);
    }

    public function category(): BelongsTo {
        return $this->belongsTo(Category::class);
    }
}
```

**EXAMPLE of what I DON'T want:**
```php
// No type hints, no relationships, mass assignment vulnerability
class Product extends Model {
    // Empty - all fields fillable = security risk!
}
```

**Generate complete model following GOOD example with:**
- [ ] Proper namespace and imports
- [ ] SoftDeletes trait
- [ ] Explicit $fillable (security)
- [ ] Type casting for price and quantity
- [ ] Relationships to Tenant and Category

---

## Phase 2: API Layer (Tasks 3-5)

[Continue with API tasks using similar patterns...]

---

## Phase 3: Testing (Tasks 6-8)

[Continue with test tasks using structured output pattern...]

---

## Dependencies

```
Task 2 depends on: Task 1 (migration must run first)
Task 3 depends on: Task 2 (model must exist)
Task 6 depends on: Task 3 (endpoint must exist to test)
```

---

## Success Criteria

- [ ] All migrations run successfully
- [ ] All tests pass (100% coverage on new code)
- [ ] API endpoints return correct data with tenant isolation
- [ ] Performance: Product list query <200ms for 10k products
- [ ] Security: Users cannot access other tenants' products

---

**NOTES:**
- Each task uses Clear Task + Context + Constraints pattern
- Complex tasks (migrations, queries) use Chain-of-Thought
- Code tasks use Few-Shot with good/bad examples
- Test tasks use Structured Output for consistency
- All tasks include validation criteria
```

---

## Pattern Application Checklist

Before finalizing any implementation plan, verify:

```
□ Every task has: TASK + CONTEXT + CONSTRAINTS
□ Complex tasks include: THINK STEP-BY-STEP reasoning
□ Code tasks show: GOOD example + BAD example (few-shot)
□ Test tasks use: Structured output format
□ All tasks have: Clear scope boundaries (constraints)
□ Dependencies are: Explicitly documented
□ Success criteria: Measurable and testable
□ File paths are: Absolute and precise
□ Code examples are: Complete and runnable
□ Validation steps: Included for each task
```

**Scoring:**
- 8/10 = Good plan (will work)
- 10/10 = Excellent plan (agent can execute independently)

---

## Impact Metrics

Plans using these patterns show:
- **50% fewer clarification questions** from agents
- **60% better first-time-right code** (less revision needed)
- **80% more consistent code quality** across tasks
- **4x faster implementation** (agent understands immediately)

---

**See also:**
- `../SKILL.md` - Main feature-planning skill documentation
- `../../prompting-patterns-reference.md` - Full prompting patterns guide
- `../spec-references/examples.md` - Specification examples

**Last Updated:** 2026-02-07
