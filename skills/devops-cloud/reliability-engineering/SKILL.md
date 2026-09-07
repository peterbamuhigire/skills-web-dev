---
name: reliability-engineering
description: Use when designing or reviewing production reliability for APIs, SaaS platforms, background jobs, distributed workflows, mobile backends, or AI-enabled systems. Covers timeout and retry policy, degradation, queue safety, incident readiness, and recovery-aware design.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Reliability Engineering
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Use when designing or reviewing production reliability for APIs, SaaS platforms, background jobs, distributed workflows, mobile backends, or AI-enabled systems. Covers timeout and retry policy, degradation, queue safety, incident readiness, and recovery-aware design.

## Do Not Use When

- The system has no meaningful uptime, recovery, data-loss, dependency, or asynchronous-work risk.
- The task is active incident command; use the applicable incident procedure, then apply this skill to remediation and prevention.

## Required Inputs

| Input | Required | Why it matters |
|---|---|---|
| Critical workflows and impact tiers | yes | Focuses protection on costly failures |
| Dependency and asynchronous processing map | yes | Exposes timeout, retry, queue, and partial-failure boundaries |
| Availability, latency, RPO, and RTO expectations | conditional | Makes reliability decisions measurable |
| Current telemetry and incident evidence | conditional | Grounds improvements in observed failure behavior |

## Workflow

Classify workflow criticality, enumerate failure modes, allocate timeout and retry budgets, design idempotency and degradation, define recovery ownership, then exercise duplicate, overload, dependency-loss, queue-replay, and rollback scenarios.

## Quality Standards

Reliability claims use user-visible outcomes and tested recovery behavior. Retries are bounded and safe, queues have overload and poison-message policies, degraded states are explicit, and every critical recovery path has an owner and evidence.

## Outputs

| Output | Consumer | Acceptance condition |
|---|---|---|
| Reliability model | Architecture and service owners | Ranks workflows and maps failure modes to prevention, detection, degradation, and recovery |
| Policy set | Implementers | Specifies timeout, retry, idempotency, queue, load-shedding, and replay rules |
| Exercise and remediation record | Operations and delivery leaders | Captures scenario, safety bounds, observations, recovery timing, gaps, owners, and follow-up verification |

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Operability | Runbook | Markdown doc per `skill-composition-standards/references/runbook-template.md` | `docs/runbooks/payment-failures.md` |
| Operability | Rollback plan | Markdown doc per `skill-composition-standards/references/rollback-plan-template.md` | `docs/releases/2026-04-16-rollback.md` |
| Operability | Failure-mode catalogue | Markdown doc listing known failure modes and mitigations | `docs/reliability/failure-modes-checkout.md` |

## Decision rules
| Condition | Action |
|---|---|
| Retry safety unknown | Do not retry automatically |
| Dependency exceeds latency budget | Time out and degrade |
| Error budget exhausted | Pause risky releases |

## Domain Anti-Patterns
- Retrying every failure. Fix: classify errors.
- Aligning all retry intervals. Fix: add backoff and jitter.
- Queueing without bounds. Fix: set overload policy.
- Defining SLOs from host uptime. Fix: measure user outcomes.
- Running drills without abort controls. Fix: set safety limits.

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
- AI incidents: AI-specific failures (hallucination spike, prompt drift, model regression, retrieval drift, jailbreak, cost runaway, agent-action, tool-vendor outage, eval drift) need AI-shaped detection, mitigation, evidence capture, and postmortems. Do not extend this skill's generic runbook to cover them. See the AI incident stack: `ai-incident-detection-and-triage`, `ai-incident-response-runbook`, `ai-incident-evidence-capture`, `ai-incident-customer-comms`, `ai-incident-postmortem`, `ai-rca-taxonomy`, `ai-incident-recovery-and-rollback`, `ai-incident-drill-and-game-day`.
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
