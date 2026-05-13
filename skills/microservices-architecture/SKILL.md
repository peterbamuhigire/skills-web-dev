---
name: microservices-architecture
description: Use when designing, reviewing, or refactoring microservice boundaries, communication, service ownership, deployment independence, resilience, and distributed data flows. Load absorbed microservices fundamentals, models, communication, and resilience references as needed.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Microservices Architecture
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

Use this parent skill as the active microservices entrypoint. It should help decide whether microservices are justified, then shape service boundaries and operating contracts when they are.

<!-- dual-compat-start -->
## Use When

- Defining service boundaries, ownership, API contracts, data ownership, deployment independence, or migration from a monolith.
- Reviewing synchronous and asynchronous service communication, reliability, retries, idempotency, and failure isolation.
- Creating a target architecture for teams that need multiple independently deployable backend services.

## Do Not Use When

- The task is unrelated to this parent skill or is better handled by a narrower active parent named in the workflow.
- The request only needs a trivial answer and no reference module needs to be loaded.

## Required Inputs

- Gather the concrete system, repository, environment, constraints, and deliverable before loading references.
- Identify which absorbed reference file is needed; do not load every migrated reference by default.
## Workflow

1. Start with `system-architecture-design` and `distributed-systems-patterns` for context, constraints, and failure modes.
2. Load only the needed reference:
   - `references/microservices-fundamentals.md` for core principles and when not to split.
   - `references/microservices-architecture-models.md` for decomposition and ownership models.
   - `references/microservices-communication.md` for API, event, queue, and contract patterns.
   - `references/microservices-resilience.md` for retries, circuit breakers, idempotency, and graceful degradation.
3. Pair with `api-design-first`, `database-design-engineering`, `deployment-release-engineering`, and `observability-monitoring` for implementation contracts.

## Quality Standards

- Do not split services without a clear ownership, deployment, data, and reliability reason.
- Every service boundary must define source of truth, API contract, failure mode, observability, and rollback path.
- Prefer fewer services until team topology, data ownership, and release cadence justify more.

## Anti-Patterns

- Treating absorbed reference files as active skills or separate routing entrypoints.
- Loading every migrated child reference instead of the one that matches the task.
- Producing generic advice without constraints, evidence, or next verification steps.
## Outputs

- Service map, boundary decision, API/event contract notes, migration plan, or architecture review.

## References

- Load only the eferences/<old-skill>.md files named in the workflow when their depth is required.
<!-- dual-compat-end -->
