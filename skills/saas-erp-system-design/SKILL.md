---
name: saas-erp-system-design
description: Use when designing configurable SaaS or ERP platforms with multi-step
  business workflows, domain modules, approvals, auditability, pricing and entitlements,
  operational reporting, and tenant-specific variation. Covers domain boundaries,
  workflow states, extension points, and control design.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# SaaS ERP System Design
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Use when designing configurable SaaS or ERP platforms with multi-step business workflows, domain modules, approvals, auditability, pricing and entitlements, operational reporting, and tenant-specific variation. Covers domain boundaries, workflow states, extension points, and control design.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `saas-erp-system-design` or would be better handled by a more specific companion skill.
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

## References

- [references/domain-modeling.md](references/domain-modeling.md): Core entities, controls, and workflow review prompts.
- Load `modular-saas-architecture`, `multi-tenant-saas-architecture`, and `database-design-engineering` when implementing the design.