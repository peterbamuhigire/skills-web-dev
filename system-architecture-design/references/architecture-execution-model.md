# Architecture Execution Model

Use this reference when architecture must be shippable, diagnosable, and maintainable in production.

## Required Artifacts

- context map: bounded contexts, ownership, and integration pressure
- critical-flow table: actor, trigger, invariants, dependencies, failure modes, rollback or compensation
- dependency view: synchronous calls, async flows, data ownership, and external systems
- release strategy notes: rollout constraints, feature flags, migration order, contract overlap
- telemetry plan: logs, metrics, traces, audit events, release markers

## Boundary Rules

- Prefer boundaries that reduce cognitive load and release risk together.
- Avoid shared-database shortcuts that bypass ownership and versioning.
- Extract services only when scaling, ownership, isolation, or release control clearly benefit.
- Keep architecture reversible where the business or team is still learning.
