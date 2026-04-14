---
name: database-design-engineering
description: Use when designing or reviewing relational or document-backed data architecture
  for SaaS platforms, ERP systems, APIs, analytics stores, or mobile sync. Covers
  domain modeling, tenancy, indexing, migrations, integrity, retention, and performance
  tradeoffs.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Database Design Engineering

<!-- dual-compat-start -->
## Use When

- Use when designing or reviewing relational or document-backed data architecture for SaaS platforms, ERP systems, APIs, analytics stores, or mobile sync. Covers domain modeling, tenancy, indexing, migrations, integrity, retention, and performance tradeoffs.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `database-design-engineering` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
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
- The release and migration constraints for live data.

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
- Separate transactional truth from projections, integrations, and analytical read models.
- Design test-data and backfill strategies for major schema evolution before the first risky migration.

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
- Tag migrations with rollback posture: reversible, compensating-only, or forward-fix-only.

### Operable Data Systems

- Emit release markers and migration identifiers into logs and dashboards where possible.
- Track replication lag, queue lag, backfill progress, and lock or saturation risk on critical stores.
- Treat long-running migrations and backfills as operational workflows with owners and stop conditions.
- Document how data correctness will be verified after migration, replay, or recovery.

### Scale, Replication, and Change Data

- Know which queries must read current truth and which can tolerate replica lag.
- Design outbox, CDC, or projection pipelines so integration needs do not corrupt the transactional model.
- Budget storage, index, and retention cost for hot tables before volume becomes painful.
- Validate the hottest access paths with execution plans, cardinality assumptions, and realistic filters.

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
- Data verification and rollback posture.
- Data retention and audit plan.
- Top 5 critical queries or access patterns.
- Projection, outbox, or replication notes where external reads or integrations exist.

## Review Checklist

- [ ] Domain entities reflect real business concepts.
- [ ] Tenant and ownership boundaries are explicit.
- [ ] Invariants are protected at durable layers.
- [ ] Indexes match real access paths.
- [ ] Migrations support live deployment safety.
- [ ] Migration verification and rollback posture are explicit.
- [ ] Audit, retention, and archival rules are documented.
- [ ] Reporting needs do not distort the transactional model without justification.
- [ ] Replica lag, projections, or CDC assumptions are explicit where they matter.

## References

- [references/data-review-checklist.md](references/data-review-checklist.md): Schema and migration review prompts.
- [references/live-data-evolution.md](references/live-data-evolution.md): Expand-contract, backfills, verification, and rollback posture.
- [../world-class-engineering/references/source-patterns.md](../world-class-engineering/references/source-patterns.md): Source-derived patterns for design quality and website/data analysis.
