---
name: deployment-release-engineering
description: Use when designing or reviewing deployment pipelines, rollout strategies, release gates, rollback plans, migration-safe releases, and post-deploy verification for production systems. Covers build promotion, environment strategy, release evidence, and operational safety.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Deployment Release Engineering
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Use when designing or reviewing deployment pipelines, rollout strategies, release gates, rollback plans, migration-safe releases, and post-deploy verification for production systems. Covers build promotion, environment strategy, release evidence, and operational safety.

## Do Not Use When

- The task is local development setup with no shared environment, promotion, or production-change concern.
- The request is an incident response already in progress; follow the incident runbook first and use this skill for the corrective release after stabilization.

## Required Inputs

| Input | Required | Why it matters |
|---|---|---|
| Release artifact and change inventory | yes | Establishes exactly what is being promoted |
| Environment and pipeline topology | yes | Identifies gates, credentials, dependencies, and drift risk |
| Migration and compatibility requirements | conditional | Determines safe sequencing across mixed application versions |
| Rollback triggers, owner, and observation signals | yes | Makes reversal an executable decision rather than a promise |

## Workflow

Classify release risk, bind the release to an immutable artifact, define promotion gates, sequence migrations and rollout, rehearse rollback where risk warrants it, deploy, then verify critical journeys and telemetry through the observation window.

## Quality Standards

The deployed artifact is the tested artifact. Evidence identifies commit and artifact digest, approvals, migration state, rollout status, verification results, and rollback decision. Destructive data changes require a separate recovery plan.

## Outputs

| Output | Consumer | Acceptance condition |
|---|---|---|
| Release plan | Release owner and implementers | Defines artifact, environments, gates, rollout, migration sequence, owners, and schedule |
| Rollback plan | On-call and change approvers | Names triggers, decision authority, executable steps, data consequences, and verification |
| Release evidence record | Operations and auditors | Captures artifact identity, approvals, deployment events, checks, observations, and final disposition |

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Release evidence | Release plan | Markdown doc per `skill-composition-standards/references/release-plan-template.md` | `docs/releases/2026-04-16-release-plan.md` |
| Release evidence | Rollback plan | Markdown doc per `skill-composition-standards/references/rollback-plan-template.md` | `docs/releases/2026-04-16-rollback-plan.md` |
| Release evidence | Change record | PR range or tagged commit list | `docs/releases/2026-04-16-change-record.md` |

## Degraded mode
If staging, telemetry, or rollback execution is unavailable, produce a read-only release plan and mark deployment verification incomplete.

## Decision rules
| Condition | Action |
|---|---|
| Rollback unsafe | Use tested roll-forward mitigation |
| Migration breaks old code | Apply expand-contract first |
| Guardrail regresses | Halt or reverse rollout |

## Domain Anti-Patterns
- Rebuilding artifacts per environment. Fix: promote one digest.
- Releasing incompatible schema and code together. Fix: stage compatibility.
- Using process exit as health proof. Fix: test outcomes.
- Rolling out without abort thresholds. Fix: define guardrails.
- Declaring success before observation. Fix: require a post-deploy window.

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Use this skill when shipping software to real users. It turns implementation output into releasable output. The focus is safe deployment, fast rollback, and evidence-based release decisions.

## Load Order

1. Load `world-class-engineering`.
2. Load this skill when a change affects deployment, migrations, operational risk, or production rollout.
3. Pair it with `observability-monitoring` and `advanced-testing-strategy`.
4. Pair it with `docker-development` when shipping, tagging, scanning, or promoting container images.

## Release Workflow

### DevOps Source Lens

Apply the DevOps operating model in [references/devops-book-patterns.md](references/devops-book-patterns.md) when the release touches production, operations, CI/CD, PHP runtime, infrastructure, Kubernetes, GitOps, observability, or incident response. Use the source lens to test flow, feedback, and learning before choosing tooling.

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
- For Docker delivery, promote the tested image by immutable digest; human-readable tags are labels, not the release source of truth.

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

### Pull-Time Migration Wrapper

For web applications with a live database, include a repo-root script that can be run after `git pull` on demo, staging, and similar shared environments. The script must:

- read database connection details from the project's normal environment configuration;
- inspect tracked migration files and the live database migration history;
- apply only missing migrations through the project's checksum-aware migration runner;
- exclude all seed files, seed directories, demo data, fixtures, and production seed bundles by default;
- support a dry-run or status mode before applying changes.

Treat this wrapper as deployment plumbing, not application seed setup. Seeds require an explicit, separate operator action.

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
- [references/devops-book-patterns.md](references/devops-book-patterns.md): Value-stream, pipeline, observability, DevSecOps, PHP, cloud-native, and GitOps patterns from the supplied DevOps books.
- [references/delivery-feedback-evidence.md](references/delivery-feedback-evidence.md): Book-derived release hypotheses, model lineage, independent verification, guardrails, and post-release learning.
- [../docker-development/references/php-python-js-container-delivery.md](../docker-development/references/php-python-js-container-delivery.md): Docker image, Compose, CI, registry, and runtime promotion standards for PHP, Python, and JavaScript services.
