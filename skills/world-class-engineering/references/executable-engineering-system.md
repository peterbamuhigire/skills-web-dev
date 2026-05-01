# Executable Engineering System

Use this reference when a team needs more than principles. It turns the baseline into an operating loop that can be executed repeatedly.

## Core Operating Loop

1. Slice the work into a change that can be reviewed, tested, and rolled back.
2. Integrate to trunk or a releasable branch quickly.
3. Run a fast commit stage that proves the change is fit for deeper validation.
4. Promote the same artifact through richer verification stages.
5. Release with explicit telemetry, rollback criteria, and observation ownership.
6. Learn from failures, flakes, and slowdowns by simplifying the system.

## Required Artifacts For Meaningful Changes

Produce these explicitly:

- change summary: user value, business value, risk class, affected flows
- critical-flow table: trigger, invariants, dependencies, failure modes, operator actions
- release plan: rollout strategy, migration order, rollback path, post-deploy checks
- telemetry plan: service level indicators, alert conditions, trace boundaries, audit events
- verification plan: commit-stage checks, integration checks, manual checks, residual risk
- ownership map: code owner, deploy owner, alert owner, incident owner

## Batch Size Rules

- Prefer changes that fit inside one coherent review and one coherent rollback story.
- Break large migrations or refactors into expand, migrate, contract phases.
- Use feature flags or dark launches when implementation can finish before exposure should.
- Do not hide unfinished integration behind long-lived branches if a safer slice can be merged incrementally.

## Delivery-System Rules

- The pipeline is the normal route to production, not an optional convenience.
- Build once and promote the same artifact through environments.
- Keep cheap checks early and expensive checks later, but do not skip the checks that guard real risk.
- Stop and repair red pipelines, flaky tests, and broken release automation quickly.
- Keep environment differences in config and secrets, not in code or rebuilt artifacts.

## Quality Feedback Rules

- Use deployment frequency, lead time, change failure rate, and recovery time to evaluate delivery health.
- Use failed deploys, long-lived branches, and chronic hotfixes as evidence of system problems, not as isolated events.
- Use telemetry and release markers to connect incidents to code and configuration changes.
- Use post-incident review to remove structural causes and recurring toil.

## Architecture Implications

- Prefer architectures that support low-risk releases, fast diagnosis, and clear ownership.
- Avoid coupling releases to big-bang schema, config, or data migrations.
- Keep the domain model stable while making infrastructure, transport, and delivery mechanisms replaceable.
- Extract services only when deployment independence, team boundaries, or risk isolation clearly justify them.

## Team Behaviors

- Make hidden work visible: pipeline debt, slow tests, manual runbooks, and repeated firefighting count as backlog.
- Share operational knowledge broadly enough that recovery does not depend on one person.
- Review for risk, correctness, migration safety, and operability before style concerns.
- Prefer automation for repeated mechanics and human judgment for ambiguous decisions.
