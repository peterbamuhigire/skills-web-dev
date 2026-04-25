# Gap Analysis — Classification Methodology

## Feature Status Classification

### Complete

A feature is **Complete** only when ALL layers are verified:

| Layer | Evidence Required |
|-------|-------------------|
| Database | Tables, columns, relationships, indexes exist |
| Backend | Routes, controllers, services, validation implemented |
| Frontend | UI screens, forms, data binding functional |
| Auth | Permissions and access control enforced |
| Tests | At least unit tests exist for core logic |

**Marking rule:** If ANY layer is missing, the feature is **Partial**, not Complete.

### Partial

A feature is **Partial** when some layers exist but the feature is not end-to-end functional.

**Common partial patterns:**

| Pattern | What Exists | What's Missing |
|---------|------------|----------------|
| Schema-only | Database tables created | No API, no UI, no tests |
| Backend-only | Routes and controllers | No UI, limited tests |
| UI stub | Frontend screens exist | No backend wiring, no data |
| No auth | Feature works | No permission checks |
| No tests | Feature is functional | No test coverage |
| No validation | CRUD works | Input validation missing |

**Sub-classification for partial features:**

- **Partial (80%+)** — Minor gaps, quick to complete
- **Partial (50-79%)** — Significant work remains
- **Partial (< 50%)** — Foundation only, major build needed

### Phantom

A feature is **Phantom** when it appears in planning documents but has zero implementation footprint.

**How to detect phantoms:**

1. Extract feature name from plan/PRD
2. Search codebase for related keywords (Grep)
3. Search database schema for related tables
4. Search routes for related endpoints
5. If ALL searches return nothing → **Phantom**

**Phantom severity:**

- **Critical phantom** — Core business feature, blocks other work
- **Standard phantom** — Planned feature, not blocking
- **Nice-to-have phantom** — Enhancement, can be deferred

### Undocumented

A feature is **Undocumented** when it exists in code but has no matching requirement.

**How to detect undocumented features:**

1. Scan route files for all registered endpoints
2. Cross-reference against documented features
3. Any endpoint/controller with no matching requirement → **Undocumented**

**Undocumented classification:**

- **Intentional** — Developer added for operational needs (health checks, admin tools)
- **Scope creep** — Feature built without formal planning
- **Legacy** — Carried over from previous version, may not be needed

## Module Completion Scoring

### Calculation Method

```
Module Score = (Complete * 1.0 + Partial * weight + Phantom * 0) / Total Features * 100
```

Where partial weight is based on sub-classification:
- 80%+ partial = 0.8 weight
- 50-79% partial = 0.5 weight
- < 50% partial = 0.2 weight

### Example Scoring

| Feature | Status | Weight | Score |
|---------|--------|--------|-------|
| User CRUD | Complete | 1.0 | 1.0 |
| Reports | Partial (70%) | 0.5 | 0.5 |
| Notifications | Phantom | 0.0 | 0.0 |
| Dashboard | Partial (90%) | 0.8 | 0.8 |
| **Module Total** | | | **2.3/4 = 57.5%** |

## Evidence Collection Standards

### Database Evidence

```
Table exists: ✅ {table_name} — {column_count} columns, {row_count} rows
Table missing: ❌ {expected_table} — Referenced in {document}, not in schema
FK missing: ⚠️ {table}.{column} → {ref_table} — No constraint defined
Index missing: ⚠️ {table}.{column} — Queried in {context}, no index
```

### Code Evidence

```
Route exists: ✅ {METHOD} {path} → {Controller}@{method}
Route missing: ❌ {METHOD} {path} — Documented in {source}, not in routes
Controller exists: ✅ {Controller} — {method_count} methods
Controller empty: ⚠️ {Controller}@{method} — Method stub only, no logic
```

### Integration Evidence

```
Endpoint verified: ✅ {METHOD} {path} — Returns {status}, payload matches spec
Endpoint broken: ❌ {METHOD} {path} — Returns {error} or missing fields
Auth gap: ⚠️ {METHOD} {path} — No authentication middleware
Pagination missing: ⚠️ {METHOD} {path} — Returns unbounded result set
```

## Dependency Mapping

When building the completion blueprint, map dependencies between features:

```
Feature A ──depends on──► Feature B ──depends on──► Feature C
```

**Rules:**
- Features with no dependencies go in Phase 1
- Features depending on Phase 1 items go in Phase 2
- Circular dependencies must be flagged as **Critical Blockers**
- Shared dependencies (e.g., auth system) are always Phase 1

### Dependency Detection

Look for these dependency signals:

| Signal | Dependency Type |
|--------|----------------|
| Foreign key references | Data dependency |
| Shared middleware | Auth/infra dependency |
| Common service calls | Business logic dependency |
| UI navigation flow | UX dependency |
| Shared API response types | Contract dependency |

## Complexity Estimation

| Size | Definition | Typical Scope |
|------|-----------|---------------|
| **S** | < 2 hours | Single file change, simple CRUD, minor fix |
| **M** | 2-8 hours | Multi-file feature, new endpoint + UI |
| **L** | 1-3 days | New module, complex business logic, migrations |
| **XL** | 3+ days | Architecture change, new subsystem, major refactor |

**Estimation inputs:**
- Number of files to create/modify
- Database migrations required
- New API endpoints needed
- UI screens to build
- Test cases to write
- Integration points to wire
