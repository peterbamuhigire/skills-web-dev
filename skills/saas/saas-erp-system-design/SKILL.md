---
name: saas-erp-system-design
description: Use when designing configurable SaaS or ERP platforms with multi-step business workflows, domain modules, approvals, auditability, pricing and entitlements, operational reporting, and tenant-specific variation. Covers domain boundaries, workflow states, extension points, and control design.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# SaaS ERP System Design
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.


## Required Inputs

| Input | Required | Use |
|---|---|---|
| Tenant, product, and lifecycle scope | yes | Bound the SaaS decision |
| Current architecture, plans, policies, and constraints | yes | Preserve enforceable behaviour |
| Production data or verified evidence | conditional | Validate thresholds and migrations |

## Capability and permission contract

Default to read-only analysis. Change configuration, billing, identity, tenant data, infrastructure, or customer communications only with explicit authority, least-privilege credentials, tenant scope, rollback, and auditable approval. Never expose secrets or cross tenant boundaries.

## Degraded mode

If production access, policy, telemetry, or authoritative records are unavailable, produce a labelled design or dry-run plan. Do not claim deployment, reconciliation, deletion, delivery, or measured outcomes; list missing evidence and verification.

## Decision rules

| Condition | Action | Stop condition |
|---|---|---|
| Tenant isolation, money, identity, or deletion is affected | Require approval and rollback evidence | Scope or authority is ambiguous |
| Evidence supports a reversible change | Stage, test, and record it | Acceptance checks fail |
| Only partial context is available | Return assumptions and validation | A production claim cannot be verified |

## Domain Anti-Patterns

- Applying one tenant's policy or data to another. Fix: enforce tenant scope at every boundary.
- Mutating production from an advisory request. Fix: remain read-only until authority is explicit.
- Inventing limits, prices, metrics, or compliance claims. Fix: use authoritative records or mark them unresolved.
- Shipping without rollback and audit evidence. Fix: stage and retain before/after proof.
- Treating a missing dependency as successful. Fix: name the blocked verification.


<!-- dual-compat-start -->
## Use When

- Use when designing configurable SaaS or ERP platforms with multi-step business workflows, domain modules, approvals, auditability, pricing and entitlements, operational reporting, and tenant-specific variation. Covers domain boundaries, workflow states, extension points, and control design.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | ERP workflow decision record | Markdown doc per `skill-composition-standards/references/adr-template.md` covering domain modules, approvals, and audit-trail design | `docs/erp/workflow-adr.md` |
| Data safety | ERP module data model | Markdown doc per `skill-composition-standards/references/entity-model-template.md` covering entities, period-close, and audit columns | `docs/erp/module-data-model.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Use this skill when the system must encode real business operations, not just CRUD screens. It is optimized for multi-tenant business software where configurability, correctness, and audit trails matter.

## Design Priorities

- Domain correctness before UI convenience.
- Configurable behavior without tenant-specific forks.
- Explicit workflow states and approvals.
- Auditability for every material business change.
- Reporting models that do not corrupt transactional design.

## System Design Workflow

### 1. Map Business Capabilities

Identify bounded domains such as:

- Sales and CRM
- Procurement
- Inventory and fulfillment
- Logistics network, transportation, fleet/carrier management, and warehouse execution where physical goods move across locations
- Finance and accounting
- HR and payroll
- Operations and reporting

Keep each capability distinct even if the first release ships only a subset.

### 2. Map Business Objects and Lifecycles

For each object define:

- Draft state
- Review or approval states
- Posted or committed state
- Reversal or cancellation path
- Audit requirements

Do not model important workflows as a single status field without state transition rules.

### 3. Separate Configuration from Transactions

Use distinct models for:

- Master data
- Configuration and entitlements
- Transactions
- Ledgers or audit history
- Reporting projections

Tenant-specific behavior should come from configuration, policy, or feature flags, not code forks.

### 4. Design Control Points

Every ERP-grade workflow needs explicit controls for:

- Permissions and separation of duties
- Approval thresholds
- Posting and locking periods
- Reconciliation and correction
- Audit log and reason capture
- Policy evaluation points and rule override governance

### 5. Design for Extensions

- Use module boundaries and extension points around optional verticals.
- Keep core concepts stable: party, product, location, document, ledger, user, role, workflow.
- Add industry-specific detail in modules without corrupting the core language.
- Prefer workflow composition and policy engines over tenant-specific code paths.

## Modeling Rules

### Workflow Rules

- Important transactions are append-only or at least auditable.
- Corrections should prefer reversal plus replacement over silent mutation.
- Status transitions must be explicit and permission-checked.
- Derived totals must be reproducible from source data.

### Financial Integrity

- Never edit posted financial records in place without a traceable reversal model.
- Use document numbers, posting dates, fiscal periods, and actor attribution consistently.
- Separate operational status from accounting status when those timelines differ.

### Reporting

- Operational reports can read transactional tables only while scale permits.
- Build projections or aggregates once reporting complexity or volume grows.
- Distinguish regulatory, finance, and operational reporting needs.

### Cross-Module Workflows

- Define how documents, approvals, entitlements, accounting, and notifications interact.
- Ensure every cross-module workflow can be reconstructed from source events and audit history.
- Make downstream posting and reversal rules explicit before implementation.

## Decision Heuristics

Use configurable policies when:

- The rule differs by tenant but the workflow concept stays the same.

Use modules when:

- The feature adds new concepts, permissions, data, or pricing boundaries.

Use approval workflows when:

- Monetary, inventory, compliance, or high-risk operational consequences exist.

Avoid per-tenant code branches unless:

- Legal or contractual obligations make configuration insufficient.

## Deliverables

For major SaaS or ERP design tasks, produce:

- Domain map and module boundaries.
- Core entities and lifecycle states.
- Control and approval model.
- Entitlement and pricing model.
- Audit and reporting strategy.
- Integration map for external systems and async jobs.
- Cross-module workflow map and policy boundaries.

For ERP projects involving manufacturing, wholesale, distribution, import/export, fleet, field delivery, agriculture aggregation, or warehouse operations, pair this skill with `inventory-management` and load `inventory-management/references/cltd-logistics-inventory-patterns.md`. The ERP design should explicitly model inventory policy, in-transit stock, shipment events, carrier/fleet assignment, freight documents, customs controls where relevant, returns, claims, and logistics KPIs rather than treating fulfilment as a simple order status.

For ERP projects with billing, fees, POS, payroll, inventory valuation, grants, patient billing, school fees, donor funds, manufacturing cost, or statutory reporting, pair this skill with `saas-accounting-system` and load `saas-accounting-system/references/accounting-bookkeeping-erp-patterns.md`. The design should model GL, subledgers, control accounts, fiscal periods, posting rules, reconciliation, close, dimensions, cost centres, profit centres, tax, fixed assets, and management reporting as first-class capabilities.

## References

- [references/domain-modeling.md](references/domain-modeling.md): Core entities, controls, and workflow review prompts.
- Load the external `chwezi-accounting-doctrine` inventory and logistics skill for inventory policy, transportation, trade documentation, and shipment exception patterns.
- [../saas-accounting-system/references/accounting-bookkeeping-erp-patterns.md](../saas-accounting-system/references/accounting-bookkeeping-erp-patterns.md): Double-entry bookkeeping, subledgers, ERP finance configuration, cost accounting, controls, reconciliations, and close patterns.
- Load `modular-saas-architecture`, `multi-tenant-saas-architecture`, and `database-design-engineering` when implementing the design.
## Quality Standards

The design must expose authoritative records, valid transitions, approval segregation, tenant extensions, audit events, integration failures, and reporting ownership without shared-table ambiguity.

## Outputs

| Artefact | Consumer | Acceptance condition |
|---|---|---|
| ERP domain and workflow design | Product architects and implementation teams | Domain ownership, state transitions, approvals, extension points, tenant variation, audit events, and reporting boundaries are unambiguous |
