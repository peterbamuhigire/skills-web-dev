---
name: reliability-engineering
description: Use when designing or reviewing production reliability for APIs, SaaS
  platforms, background jobs, distributed workflows, mobile backends, or AI-enabled
  systems. Covers timeout and retry policy, degradation, queue safety, incident readiness,
  and recovery-aware design.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Reliability Engineering

<!-- dual-compat-start -->
## Use When

- Use when designing or reviewing production reliability for APIs, SaaS platforms, background jobs, distributed workflows, mobile backends, or AI-enabled systems. Covers timeout and retry policy, degradation, queue safety, incident readiness, and recovery-aware design.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `reliability-engineering` or would be better handled by a more specific companion skill.
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
Use this skill when correctness under ideal conditions is not enough. The goal is to keep important workflows safe, available enough, diagnosable, and recoverable under load, dependency failure, stale state, and operator error.

## Load Order

1. Load `world-class-engineering`.
2. Load this skill when the system has external dependencies, background processing, scale risk, or meaningful uptime expectations.
3. Pair it with `observability-monitoring`, `deployment-release-engineering`, and `distributed-systems-patterns` when services or queues are involved.

## Reliability Workflow

### 1. Classify Criticality

For each important workflow, define:

- user and business impact if it fails
- maximum acceptable downtime or degradation
- data-loss tolerance
- financial, compliance, or trust consequences
- recovery time expectation
- acceptable operator effort or toil

Not every path needs the same reliability level.

### 2. Map Failure Modes

Explicitly list:

- dependency timeout or outage
- partial write or partial side effect
- duplicate delivery or replay
- stale reads or cache inconsistency
- concurrency conflict
- operator or configuration error
- overload, backpressure, or queue growth
- release-induced regression

If a failure mode is plausible and unhandled, the design is incomplete.

### 3. Design Protection Mechanisms

Choose deliberate policies for:

- timeout budgets
- retries and backoff
- idempotency and deduplication
- circuit breaking or load shedding
- queues, dead-letter handling, and replay
- graceful degradation or fallback behavior
- concurrency limits and admission control
- reconciliation jobs for eventually consistent workflows

### 4. Design Recovery

For every critical flow, define:

- how to detect failure
- who owns the first response
- whether to retry, compensate, reconcile, or roll back
- what can be replayed safely
- what manual tooling or runbook is needed
- how recent deployments or config changes will be ruled in or out quickly

### 5. Verify Reliability

Before production claims, produce evidence for:

- timeout and retry behavior
- degraded-state behavior
- queue recovery or replay
- duplicate-request safety
- alert and runbook usefulness
- overload or backpressure behavior
- staged recovery drills or game-day exercises for the highest-cost failures

## Reliability Standards

### Retries and Timeouts

- Retries without idempotency are usually a bug.
- Timeouts must be shorter than user patience and upstream collapse thresholds.
- Use bounded retries with jitter for transient failures.
- Do not retry validation failures, authorization failures, or deterministic business rejections.

### Queues and Jobs

- Every job needs an idempotency strategy or deduplication key.
- Poison messages need dead-letter or quarantine behavior.
- Replay must be safe, observable, and permissioned.
- Long-running jobs need progress or heartbeat signals.
- Queues need saturation and age monitoring, not only failure counts.

### Degradation

- Define what the user sees when a dependency is slow or unavailable.
- Prefer reduced capability over total failure where business risk allows.
- Fail closed for privileged or security-sensitive paths.
- Fail open only with deliberate justification and bounded blast radius.

### Incident Readiness

- Alerts need an owner and a first action.
- Correlate incidents to release version, tenant, actor, and dependency.
- Keep recovery tools safe for operators under stress.
- Write runbooks for high-cost incidents before the incident happens.
- Rehearse at least the top failure scenarios often enough that the response is not theoretical.

## Deliverables

For meaningful reliability work, produce:

- criticality table
- failure-mode table
- timeout and retry policy
- degradation and fallback notes
- queue and replay strategy
- incident ownership and recovery outline
- reliability verification or exercise plan

## Review Checklist

- [ ] Critical workflows have explicit reliability targets or expectations.
- [ ] Retries, timeouts, and idempotency rules are coherent.
- [ ] Duplicate, replay, and partial-failure cases are handled safely.
- [ ] Degradation behavior is defined for dependency failures.
- [ ] Recovery paths and owners are explicit.
- [ ] Reliability claims are backed by tests, simulations, or staged evidence.

## References

- [references/reliability-patterns.md](references/reliability-patterns.md): Design rules for timeouts, retries, queues, and degradation.
- [references/incident-readiness.md](references/incident-readiness.md): Incident preparation and recovery prompts.
- [references/reliability-verification.md](references/reliability-verification.md): Reliability drills, overload checks, and evidence expectations.
