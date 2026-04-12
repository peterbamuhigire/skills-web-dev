---
name: system-architecture-design
description: Use when defining or reviewing software architecture for web apps, mobile backends, SaaS platforms, APIs, distributed systems, or major features. Covers bounded contexts, module decomposition, contracts, failure handling, ADRs, and scalability tradeoffs.
---

# System Architecture Design

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

### 2. Decompose by Capability

Split the system by business capability first, technical layer second.

- Each module owns its rules, contracts, and data responsibilities.
- Shared modules should expose narrow stable interfaces.
- Avoid "core" dumping grounds with mixed responsibilities.
- If a module changes for unrelated reasons, split it.

### 3. Choose the Runtime Shape

Use the simplest viable shape:

- Modular monolith for most early and mid-stage systems.
- Service extraction only when scaling, deployability, team boundaries, or isolation justify the extra cost.
- Event-driven workflows only when loose coupling, resilience, or asynchronous processing clearly matter.

Default rule: prefer a well-structured monolith before microservices.

### 4. Design Critical Flows

For each critical flow, define:

- Entry point and authentication mode.
- Validation rules.
- Transaction boundary.
- Side effects and idempotency strategy.
- Failure and retry behavior.
- Audit and observability events.

### 5. Record Decisions

Use ADR logic for decisions that are expensive to reverse:

- Context
- Options considered
- Decision
- Tradeoffs
- Consequences

Use the template in [references/adr-template.md](references/adr-template.md).

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

## Architecture Review Checklist

- [ ] Capabilities are separated by business meaning.
- [ ] Data ownership is explicit for every module.
- [ ] Critical paths include failure and observability design.
- [ ] Service boundaries are justified by evidence, not fashion.
- [ ] Contracts are explicit and evolution-safe.
- [ ] Background work is idempotent and retry-safe.
- [ ] Security and tenant boundaries align with module boundaries.

## References

- [references/adr-template.md](references/adr-template.md): Decision record format and architecture review prompts.
- [../world-class-engineering/references/source-patterns.md](../world-class-engineering/references/source-patterns.md): Architecture review patterns derived from the supplied books.
