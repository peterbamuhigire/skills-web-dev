---
name: system-architecture-design
description: Use when defining or reviewing software architecture for web apps, mobile backends, SaaS platforms, APIs, distributed systems, or major features. Covers bounded contexts, module decomposition, contracts, failure handling, ADRs, and scalability tradeoffs.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# System Architecture Design
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Use when defining or reviewing software architecture for web apps, mobile backends, SaaS platforms, APIs, distributed systems, or major features. Covers bounded contexts, module decomposition, contracts, failure handling, ADRs, and scalability tradeoffs.

## Do Not Use When

- The request is limited to an isolated endpoint, query, UI component, or deployment script with no system-level trade-off.
- The architecture is already decided and the task only needs implementation; use the relevant engineering skill and preserve recorded decisions.

## Required Inputs

| Input | Required | Why it matters |
|---|---|---|
| Business capabilities and critical journeys | yes | Anchors boundaries in real system responsibilities |
| Quality attributes with measurable scenarios | yes | Makes performance, security, availability, and changeability testable |
| Constraints and existing-system context | yes | Prevents an unbuildable greenfield design |
| Scale, data, integration, and deployment assumptions | conditional | Supports sizing and topology decisions |

## Workflow

Clarify drivers and constraints, model context and containers, assign data and responsibility boundaries, compare viable options, record decisions, then test the design against failure, evolution, security, and operational scenarios.

## Quality Standards

Decisions link a driver to a chosen option, rejected alternatives, consequences, and verification evidence. Diagrams and prose agree on ownership, trust boundaries, data flow, and deployment topology.

## Outputs

| Output | Consumer | Acceptance condition |
|---|---|---|
| Architecture description | Engineering stakeholders | Includes context, responsibilities, data ownership, integrations, trust boundaries, and deployment view |
| Decision records | Future maintainers | Capture rationale, alternatives, consequences, and revisit triggers |
| Quality-attribute verification plan | Delivery and operations teams | Maps each material scenario to a test, measurement, or operational check |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
- [references/practical-architecture-knowledge.md](references/practical-architecture-knowledge.md) - book-distilled checks for DDD boundaries, scalability, architecture metrics, and executable architecture documentation.
<!-- dual-compat-end -->
Use this skill when the problem is bigger than a single component. Start here before committing to frameworks, service boundaries, data ownership, or integration patterns.

## Load Order

1. Load `world-class-engineering`.
2. Use this skill to shape the architecture.
3. Load stack-specific skills only after the structural decisions are clear.

## Architecture Workflow

### 1. Define the System Boundary

Capture:

- Actors and primary user journeys.
- Business capabilities and invariants.
- External systems and integration points.
- Read/write paths, async flows, and operational jobs.
- Non-functional constraints: latency, availability, compliance, team size, release cadence.
- The business events, policies, and failure consequences that make the system expensive to get wrong.
- The release shape: expected batch size, deployment frequency, rollback expectations, and who operates the system.

### 2. Decompose by Capability

Split the system by business capability first, technical layer second.

- Each module owns its rules, contracts, and data responsibilities.
- Shared modules should expose narrow stable interfaces.
- Avoid "core" dumping grounds with mixed responsibilities.
- If a module changes for unrelated reasons, split it.
- Prefer boundaries that support independent understanding and low-risk releases before chasing deployment independence.

### 3. Choose the Runtime Shape

Use the simplest viable shape:

- Modular monolith for most early and mid-stage systems.
- Service extraction only when scaling, deployability, team boundaries, or isolation justify the extra cost.
- Event-driven workflows only when loose coupling, resilience, or asynchronous processing clearly matter.
- Feature flags, dark launches, or canaries when exposure control matters more than runtime separation.

Default rule: prefer a well-structured monolith before microservices.

### 4. Design Critical Flows

For each critical flow, define:

- Entry point and authentication mode.
- Validation rules.
- Transaction boundary.
- Side effects and idempotency strategy.
- Failure and retry behavior.
- Audit and observability events.

Also define:

- consistency requirement: immediate, eventual, or compensating
- ownership of downstream effects
- rollback or reconciliation path when dependencies disagree
- release evidence needed before exposing the flow broadly

For domain-heavy or scale-sensitive systems, load [references/practical-architecture-knowledge.md](references/practical-architecture-knowledge.md) and apply its bounded-context, scalable-systems, and architecture-metric checks.

### 5. Record Decisions

Use ADR logic for decisions that are expensive to reverse:

- Context
- Options considered
- Decision
- Tradeoffs
- Consequences

Use the template in [references/adr-template.md](references/adr-template.md).

### 6. Produce Executable Architecture Artifacts

For non-trivial systems, produce:

- context map and ownership map
- critical-flow table with invariants, dependency failures, and operator actions
- deployment and rollback assumptions
- telemetry and audit requirements by flow
- migration and contract-evolution notes for live systems

## Structural Standards

### Bounded Contexts

- Keep domain language consistent inside each context.
- Do not let one module write another module's tables directly.
- Exchange data through APIs, commands, events, or well-defined internal interfaces.

### Contracts

- Version externally consumed contracts.
- Keep domain DTOs separate from persistence models where churn differs.
- Make schemas explicit for requests, events, jobs, and database writes.

### Failure Design

- Treat timeouts, retries, duplicate messages, and partial writes as first-class design cases.
- Prefer idempotency keys for financial, provisioning, and integration-heavy workflows.
- Use compensating actions when atomic transactions cannot span the workflow.

### Operability

- Every critical workflow needs logs, metrics, and traceable IDs.
- Every background processor needs dead-letter or replay strategy.
- Every external dependency needs timeout, retry, and degradation rules.
- Every architecture proposal should show how recent changes will be correlated to failures in production.

### Release-Aware Architecture

- Prefer designs that can be shipped in small batches.
- Avoid boundaries that force big-bang database, contract, or traffic cutovers without a strong reason.
- Keep overlapping-version compatibility where staging and production may run different revisions briefly.
- Make feature-flag and migration strategy explicit when architecture depends on phased rollout.

### Team and Dependency Boundaries

- Align service or module boundaries with ownership where possible.
- Prefer interfaces that allow teams to move independently without hidden schema coupling.
- Do not extract services just to mirror org charts if operational cost outweighs benefit.

## Decision Heuristics

Choose a modular monolith when:

- One team owns most of the system.
- Transactions span multiple capabilities often.
- Deployment independence is not yet a bottleneck.

Choose service boundaries when:

- Independent scaling profiles are proven.
- Teams need separate release control.
- Fault isolation or compliance isolation is mandatory.

Choose synchronous communication when:

- The caller needs an immediate answer.
- Consistency must be confirmed before UX can proceed.

Choose asynchronous communication when:

- Work is slow, bursty, or integration-heavy.
- Temporary unavailability must not block the user flow.
- The operation is naturally eventually consistent.

Split a service or module when:

- its change cadence, scaling profile, or compliance boundary is materially different
- ownership confusion is causing delivery friction
- failure isolation or release independence produces clear operational value

## Architecture Review Checklist

- [ ] Capabilities are separated by business meaning.
- [ ] Data ownership is explicit for every module.
- [ ] Critical paths include failure and observability design.
- [ ] The runtime shape supports low-risk release and rollback, not only clean decomposition.
- [ ] Service boundaries are justified by evidence, not fashion.
- [ ] Contracts are explicit and evolution-safe.
- [ ] Background work is idempotent and retry-safe.
- [ ] Security and tenant boundaries align with module boundaries.
- [ ] Consistency model and compensation strategy are explicit where workflows cross boundaries.
- [ ] Architecture deliverables include context map, critical-flow table, and dependency view.

## References

- [references/adr-template.md](references/adr-template.md): Decision record format and architecture review prompts.
- [references/architecture-execution-model.md](references/architecture-execution-model.md): Architecture artifacts, release-aware boundaries, and flow design.
- [references/platform-as-product-feedback.md](references/platform-as-product-feedback.md): Platform-as-product ownership, decision rights, consumer feedback, and sustainability checks.
- [../../sdlc-meta/world-class-engineering/references/source-patterns.md](../../sdlc-meta/world-class-engineering/references/source-patterns.md): Architecture review patterns derived from the supplied books.

## Inputs
| Input | Required | Purpose |
|---|---|---|
| Capabilities and quality attributes | yes | Set drivers |
| Current topology and constraints | yes | Ground design |
| Workload and failure assumptions | yes | Test choices |

## Degraded mode
If workload evidence or stakeholder decisions are unavailable, return read-only options with assumptions and proposed ADRs; do not present a target as approved.

## Domain Anti-Patterns
- Choosing technology before drivers. Fix: rank quality attributes first.
- Drawing components without contracts. Fix: specify interfaces and owners.
- Ignoring failure paths. Fix: model timeouts and recovery.
- Treating estimates as measured capacity. Fix: label and test assumptions.
- Approving irreversible change without an ADR. Fix: record consequences.
