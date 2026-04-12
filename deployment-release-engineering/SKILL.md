---
name: deployment-release-engineering
description: Use when designing or reviewing deployment pipelines, rollout strategies, release gates, rollback plans, migration-safe releases, and post-deploy verification for production systems. Covers build promotion, environment strategy, release evidence, and operational safety.
---

# Deployment Release Engineering

Use this skill when shipping software to real users. It turns implementation output into releasable output. The focus is safe deployment, fast rollback, and evidence-based release decisions.

## Load Order

1. Load `world-class-engineering`.
2. Load this skill when a change affects deployment, migrations, operational risk, or production rollout.
3. Pair it with `observability-monitoring` and `advanced-testing-strategy`.

## Release Workflow

### 1. Classify The Release

Identify whether the release includes:

- schema changes
- auth or permission changes
- financial or workflow-critical logic
- infrastructure or dependency changes
- high-traffic path changes
- AI behavior or prompt changes

Higher-risk releases need narrower rollout and stronger verification.

### 2. Build Once, Promote Safely

- Build artifacts once.
- Promote the same artifact through environments.
- Keep environment differences in configuration and secrets, not source or binaries.
- Do not rebuild separately for staging and production.

### 3. Choose A Rollout Strategy

Use the simplest safe option:

- rolling for low-risk or capacity-constrained changes
- blue-green for quick rollback and clean cutover
- canary for risky changes where partial exposure gives useful feedback

### 4. Protect Live Data

- Use expand-contract migrations where live compatibility matters.
- Sequence migrations, code rollout, backfills, and cleanup deliberately.
- Never tie rollback to a destructive schema assumption unless explicitly planned.

### 5. Verify The Release

Post-deploy verification should confirm:

- health endpoints
- critical user journeys
- telemetry and alert behavior
- migration success
- no unexpected error spike

See [references/release-checklist.md](references/release-checklist.md).

## Release Standards

### Environment Strategy

- Development for fast iteration
- Staging for production-like verification
- Production for controlled rollout

Environment parity matters most for:

- dependencies
- secrets and config shape
- data migration behavior
- auth integrations
- performance-sensitive infrastructure

### Rollback

Every meaningful release needs:

- rollback trigger conditions
- rollback owner
- rollback method
- data compatibility assessment

Rollback must be designed before release, not improvised during incident response.

### Post-Deploy Window

For risky releases, define:

- observation period
- dashboards to watch
- alerts to treat as rollback triggers
- freeze on follow-up changes until stability is confirmed

## Deliverables

For significant releases, produce:

- release classification
- rollout strategy
- migration sequence
- rollback plan
- post-deploy verification checklist
- monitoring watch list

## Review Checklist

- [ ] Artifact promotion avoids rebuild drift.
- [ ] Rollout strategy matches release risk.
- [ ] Migration sequence is safe for overlapping versions.
- [ ] Rollback path is explicit and realistic.
- [ ] Post-deploy verification is defined.
- [ ] Monitoring and alert watch list is attached to the release.

## References

- [references/release-checklist.md](references/release-checklist.md): Pre-deploy and post-deploy checks.
- [references/rollout-selection.md](references/rollout-selection.md): Choosing rolling, blue-green, or canary.
