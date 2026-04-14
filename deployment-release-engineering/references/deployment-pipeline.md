# Deployment Pipeline

Use this reference when a team needs an explicit release path rather than general rollout advice.

## Canonical Stage Model

1. Commit stage: build, unit tests, lint, static checks, packaging.
2. Application confidence stage: integration, contract, or acceptance checks.
3. Nonfunctional stage: performance, resilience, security, migration rehearsal as needed.
4. Release readiness review: notes, approvals, rollback, observation plan.
5. Controlled rollout: rolling, blue-green, canary, or dark launch.
6. Observation window: dashboards, alerts, critical journeys, and rollback triggers.

## Release Packet

For meaningful releases, attach:

- release summary and affected flows
- migration or data-change sequence
- rollout method and blast-radius limit
- rollback and feature-disable path
- dashboards, alerts, and release markers to watch
- observation owner and duration

## Release Design Rules

- Prefer releases that are reversible at the deployment layer.
- Use feature flags to control exposure, not to avoid finishing testing forever.
- Use expand-contract for schemas and overlapping-version support where live traffic is involved.
- Keep rollback criteria concrete enough that operators can act quickly.
