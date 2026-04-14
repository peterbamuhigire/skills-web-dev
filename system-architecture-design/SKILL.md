---
name: system-architecture-design
description: Use when defining or reviewing software architecture for web apps, mobile
  backends, SaaS platforms, APIs, distributed systems, or major features. Covers bounded
  contexts, module decomposition, contracts, failure handling, ADRs, and scalability
  tradeoffs.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# System Architecture Design

<!-- dual-compat-start -->
## Use When

- Use when defining or reviewing software architecture for web apps, mobile backends, SaaS platforms, APIs, distributed systems, or major features. Covers bounded contexts, module decomposition, contracts, failure handling, ADRs, and scalability tradeoffs.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `system-architecture-design` or would be better handled by a more specific companion skill.
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
- [../world-class-engineering/references/source-patterns.md](../world-class-engineering/references/source-patterns.md): Architecture review patterns derived from the supplied books.
