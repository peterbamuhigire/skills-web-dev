---
name: deployment-release-engineering
description: Use when designing or reviewing deployment pipelines, rollout strategies,
  release gates, rollback plans, migration-safe releases, and post-deploy verification
  for production systems. Covers build promotion, environment strategy, release evidence,
  and operational safety.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Deployment Release Engineering

<!-- dual-compat-start -->
## Use When

- Use when designing or reviewing deployment pipelines, rollout strategies, release gates, rollback plans, migration-safe releases, and post-deploy verification for production systems. Covers build promotion, environment strategy, release evidence, and operational safety.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `deployment-release-engineering` or would be better handled by a more specific companion skill.
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
| Release evidence | Release plan | Markdown doc per `skill-composition-standards/references/release-plan-template.md` | `docs/releases/2026-04-16-release-plan.md` |
| Release evidence | Rollback plan | Markdown doc per `skill-composition-standards/references/rollback-plan-template.md` | `docs/releases/2026-04-16-rollback-plan.md` |
| Release evidence | Change record | PR range or tagged commit list | `docs/releases/2026-04-16-change-record.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
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
- feature-flag or config-controlled exposure
- rollback-hostile data changes

Higher-risk releases need narrower rollout and stronger verification.

### 2. Build Once, Promote Safely

- Build artifacts once.
- Promote the same artifact through environments.
- Keep environment differences in configuration and secrets, not source or binaries.
- Do not rebuild separately for staging and production.
- Keep pipeline definition in version control so release mechanics are reviewable.

### 3. Use A Deployment Pipeline, Not Ad Hoc Stages

For meaningful changes, define these stages explicitly:

- commit stage: fast build, unit checks, static analysis, packaging
- automated acceptance or workflow stage
- deeper integration, contract, and nonfunctional stages as risk requires
- production readiness gate: release notes, migration review, rollback review
- rollout and observation window

### 4. Choose A Rollout Strategy

Use the simplest safe option:

- rolling for low-risk or capacity-constrained changes
- blue-green for quick rollback and clean cutover
- canary for risky changes where partial exposure gives useful feedback
- dark launch or feature-flag exposure when deployment should finish before user release

### 5. Protect Live Data

- Use expand-contract migrations where live compatibility matters.
- Sequence migrations, code rollout, backfills, and cleanup deliberately.
- Never tie rollback to a destructive schema assumption unless explicitly planned.
- Separate deployment rollback from business-data correction when side effects have already escaped.

### 6. Verify The Release

Post-deploy verification should confirm:

- health endpoints
- critical user journeys
- telemetry and alert behavior
- migration success
- no unexpected error spike
- no unexpected saturation, queue growth, or cost surge
- release markers visible in dashboards and traces

See [references/release-checklist.md](references/release-checklist.md).

### 7. Learn From The Release

- Record what slowed release preparation, deployment, rollback confidence, or verification.
- Convert repeated manual steps into pipeline or runbook improvements.
- Treat failed rollbacks, unclear ownership, and weak telemetry as release-system defects.

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
- feature-flag disable path when applicable

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
- deployment pipeline stage map
- rollout strategy
- migration sequence
- rollback plan
- post-deploy verification checklist
- monitoring watch list

## Review Checklist

- [ ] Artifact promotion avoids rebuild drift.
- [ ] Pipeline stages match change risk and are defined before release day.
- [ ] Rollout strategy matches release risk.
- [ ] Migration sequence is safe for overlapping versions.
- [ ] Rollback path is explicit and realistic.
- [ ] Post-deploy verification is defined.
- [ ] Monitoring and alert watch list is attached to the release.

## References

- [references/deployment-pipeline.md](references/deployment-pipeline.md): Stage model, release packet, and rollout heuristics.
- [references/release-checklist.md](references/release-checklist.md): Pre-deploy and post-deploy checks.
- [references/rollout-selection.md](references/rollout-selection.md): Choosing rolling, blue-green, or canary.
