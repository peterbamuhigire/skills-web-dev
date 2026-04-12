---
name: database-design-engineering
description: Use when designing or reviewing relational or document-backed data architecture for SaaS platforms, ERP systems, APIs, analytics stores, or mobile sync. Covers domain modeling, tenancy, indexing, migrations, integrity, retention, and performance tradeoffs.
---

# Database Design Engineering

Use this skill when schema choices will shape correctness, performance, or future maintainability. It complements vendor-specific database skills by focusing on design logic that survives framework changes.

## Load Order

1. Load `world-class-engineering`.
2. Load this skill to design the data model and lifecycle.
3. Load engine-specific skills such as `mysql-best-practices` or PostgreSQL skills afterward.

## Database Workflow

### 1. Model the Domain

Define:

- Core entities and their lifecycles.
- Ownership and tenancy boundaries.
- Transactional invariants.
- Reporting and audit requirements.
- Retention, archival, and deletion rules.

Model events and states, not just forms and screens.

### 2. Choose the Storage Shape

Prefer relational design when:

- Consistency matters.
- Multi-table invariants exist.
- Reporting and joins are central.

Prefer document or key-value structures for:

- Flexible metadata.
- Cached projections.
- Denormalized read models or unstructured payloads.

Do not use schemaless storage as a substitute for undecided modeling.

### 3. Define Table Boundaries

- One table should represent one durable business concept or event stream.
- Separate current state from append-only history when auditability matters.
- Distinguish master data, transactions, and derived projections.
- Avoid overloading one table with mutually exclusive concepts.

### 4. Design for Scale and Safety

- Add tenant or ownership keys early.
- Design indexes around real query predicates and sort order.
- Keep writes idempotent where retries are possible.
- Plan archival, purging, and partitioning before large-volume tables arrive.
- Use expand-contract migrations for live systems.

## Core Standards

### Integrity

- Enforce invariants at the strongest reasonable layer: schema, transaction, application, worker.
- Use foreign keys where ownership is mandatory and module boundaries permit it.
- Use append-only ledgers for financial and audit-critical domains.
- Never encode important business rules only in UI validation.

### Tenancy

- Every tenant-scoped table must carry the tenant key.
- Every tenant-scoped query must constrain by tenant key.
- Every unique constraint must reflect tenancy where appropriate.
- Cross-tenant analytics should use controlled derived datasets, not raw shared queries.

### Indexing

- Index for the access path, not for column popularity.
- Prefer composite indexes that match filter plus sort order.
- Remove duplicate or low-value indexes that tax writes.
- Validate index usefulness against actual queries and execution plans.

### Migrations

- Make every migration forward-safe and observable.
- Prefer additive changes, backfills, then cutovers, then cleanup.
- Keep application code compatible across deployment overlap where possible.
- Rehearse destructive or high-volume changes before production.

## Decision Heuristics

Normalize when:

- Data duplication would create correctness risk.
- Multiple workflows update the same fact.

Denormalize when:

- Read performance or query simplicity clearly outweighs duplication cost.
- The source of truth remains obvious.
- Refresh or reconciliation strategy is explicit.

Use soft delete when:

- Recovery, auditability, or legal hold matters.

Use hard delete when:

- Data minimization or cost pressure is stronger and downstream references are safely handled.

## Deliverables

For substantive database work, produce:

- Entity and lifecycle summary.
- Table or collection design.
- Index plan.
- Migration strategy.
- Data retention and audit plan.
- Top 5 critical queries or access patterns.

## Review Checklist

- [ ] Domain entities reflect real business concepts.
- [ ] Tenant and ownership boundaries are explicit.
- [ ] Invariants are protected at durable layers.
- [ ] Indexes match real access paths.
- [ ] Migrations support live deployment safety.
- [ ] Audit, retention, and archival rules are documented.
- [ ] Reporting needs do not distort the transactional model without justification.

## References

- [references/data-review-checklist.md](references/data-review-checklist.md): Schema and migration review prompts.
- [../world-class-engineering/references/source-patterns.md](../world-class-engineering/references/source-patterns.md): Source-derived patterns for design quality and website/data analysis.
