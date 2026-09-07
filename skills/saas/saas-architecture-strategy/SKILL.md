---
name: saas-architecture-strategy
description: Use when architecting or evaluating a cloud SaaS product — including choosing multi-tenant patterns, mapping deployment to IaaS, planning scaling and blast-radius isolation, aligning architecture to business capabilities, and reconciling multi-enterprise consumption requirements with operating-model constraints.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# SaaS Architecture Strategy
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
- Designing a new cloud SaaS product or migrating a hosted product to a true SaaS model.
- Selecting tenancy patterns (pooled, siloed, bridge) for a specific business capability.
- Sizing IaaS deployment for a SaaS workload across enterprise tiers (large, mid, SME, long tail).
- Planning scaling and blast-radius containment for production traffic.
- Reconciling residency, isolation, or custom-integration demands from enterprise tenants with a shared platform.
- Aligning the SaaS technical architecture with the operating model (support tiers, on-call, billing, sales motion).

## Do Not Use When
- The product is internal-only with a single tenant — use generic application architecture guidance.
- The work is a single component refactor with no tenancy, residency, or consumption-model implication.
- The decision is a vendor selection without architectural commitment; defer until a target architecture is shaped.

## Required Inputs
- The business capabilities the SaaS will serve, named and prioritised.
- The enterprise consumption profile: tenant size distribution, residency requirements, integration surface, regulatory regime.
- The operating model: support tiers, deployment cadence, who runs production, billing/metering granularity.
- Constraints: cloud provider commitments, data sovereignty, compliance frameworks, existing licences.
- Scaling expectations: peak concurrency, throughput, growth curve, latency targets per tenant tier.

## Workflow
1. **Map business capabilities first.** Before any tenancy decision, list the capabilities the SaaS delivers and rank them by differentiation, regulatory weight, and shared-vs-bespoke pressure. See `references/architecture-to-business-capability-map.md`.
2. **Pick tenancy pattern per capability, not per product.** Use the pooled / siloed / bridge tradeoff matrix; expect a heterogeneous answer across capabilities. See `references/multi-tenant-consumption-models.md`.
3. **Segment tenants into consumption tiers.** Long tail, SME, mid-market, large enterprise / vertical — each tier has different defaults for isolation, residency, integration, and SLA.
4. **Surface IaaS assumptions explicitly.** Hypervisor behaviour, auto-provisioning, load balancing, and auto-scaling are not free; map each architectural building block to its minimum deployment configuration. See `references/deployment-mapping-and-iaas-assumptions.md`.
5. **Plan scaling and blast radius together.** Capacity, throughput, isolation boundaries, and failure containment are one design problem, not four. See `references/scaling-and-blast-radius.md`.
6. **Align operating model to architecture.** A pooled architecture with a per-tenant support model collapses on contact with reality; resolve the mismatch before launch.
7. **Run the anti-pattern audit.** Check the design against `references/saas-strategy-anti-patterns.md` before committing — most SaaS architectures fail on a small set of recurring mistakes.
8. **Document the tradeoffs.** Produce a one-page decision record per capability stating tenancy pattern, isolation level, residency stance, and the named cost of each choice.

## Quality Standards
- Every architectural building block traces to at least one named business capability.
- Tenancy decisions are made per capability, justified, and revisable independently.
- IaaS deployment configuration is sized from the architecture, not guessed.
- Blast radius is bounded and named; a single tenant cannot silently degrade all others.
- Residency, isolation, and integration surface are specified per tenant tier, not as global toggles.
- The operating model can actually run the architecture at the planned scale and tier mix.

## Anti-Patterns
- One-size-fits-all tenancy across all capabilities.
- Treating SaaS as a hosted single-tenant product with shared marketing.
- Designing for the largest tenant and discovering the long tail is unprofitable to serve.
- Pretending IaaS auto-scaling absolves the architecture of capacity planning.
- Bespoke integrations promised to enterprise tenants without an isolation boundary that contains the bespoke code.
- Confusing logical multi-tenancy (shared schema with tenant ID) with operational multi-tenancy (shared on-call, shared deployment, shared SLO).
- Letting sales commitments to one large tenant rewrite the platform's tenancy model after launch.

## Outputs
- A capability-to-architecture map naming the building blocks (ABBs / SBBs) per capability.
- Per-capability tenancy decisions (pooled / siloed / bridge) with named tradeoffs.
- A consumption tier matrix specifying isolation, residency, integration, and SLA per tier.
- An IaaS deployment plan with minimum and target configurations per building block.
- A scaling and blast-radius plan with isolation boundaries and failure containment rules.
- A tradeoff matrix used to defend each decision in review.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Release evidence | SaaS architecture strategy memo | Markdown with tenancy, scaling, consumption model, and operating model | `docs/architecture/saas-strategy.md` |
| Security | Tenant isolation decision record | ADR or markdown table covering isolation boundary and data access controls | `docs/architecture/tenant-isolation-adr.md` |
| Performance | Scaling and blast-radius checklist | Markdown checklist with load, elasticity, cell, and failure-domain decisions | `docs/architecture/scaling-checklist.md` |
| Operability | SaaS operations assumptions | Markdown runbook section for upgrades, support, usage, and maintenance windows | `docs/ops/saas-ops-assumptions.md` |

## References
- references/multi-tenant-consumption-models.md — pooled, siloed, bridge patterns; tenant tiers; consumption-model selection rules.
- references/deployment-mapping-and-iaas-assumptions.md — translating architecture building blocks into IaaS configuration; what hypervisors and auto-scalers actually guarantee.
- references/scaling-and-blast-radius.md — sizing capacity and throughput while containing failure; isolation boundary design.
- references/architecture-to-business-capability-map.md — mapping capabilities to architecture building blocks; differentiation versus shared-platform pressure.
- references/saas-strategy-anti-patterns.md — recurring SaaS architectural failures and how to detect them on paper.
<!-- dual-compat-end -->
