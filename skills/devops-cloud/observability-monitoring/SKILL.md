---
name: observability-monitoring
description: Use when designing or reviewing logs, metrics, traces, alerts, SLOs, dashboards, audit events, or production telemetry for web apps, APIs, SaaS platforms, mobile backends, and AI systems. Covers instrumentation strategy, diagnosis-first telemetry, alert quality, and operational visibility.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Observability Monitoring
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Use when designing or reviewing logs, metrics, traces, alerts, SLOs, dashboards, audit events, or production telemetry for web apps, APIs, SaaS platforms, mobile backends, and AI systems. Covers instrumentation strategy, diagnosis-first telemetry, alert quality, and operational visibility.

## Do Not Use When

- The request is business analytics without a production diagnosis, service-level, audit, or operator-response requirement.
- The task only asks to install a monitoring product; first define the operational questions and service outcomes this skill requires.

## Required Inputs

| Input | Required | Why it matters |
|---|---|---|
| Critical user and system flows | yes | Determines what must be observable |
| Service ownership and escalation paths | yes | Connects signals to accountable action |
| Architecture, dependencies, and async boundaries | yes | Defines correlation and trace coverage |
| Data sensitivity, retention, and cost limits | conditional | Constrains event fields, sampling, and storage |

## Workflow

Start from critical flows and operator questions, define service outcomes and SLOs, map logs, metrics, traces, and audit events, set correlation and cardinality rules, create actionable alerts and dashboards, then test diagnosis using a known failure.

## Quality Standards

Every page has a named owner, user-impact rationale, and first action. Signals carry enough version, environment, tenant, and dependency context to diagnose safely, while secrets and sensitive payloads remain excluded or redacted.

## Outputs

| Output | Consumer | Acceptance condition |
|---|---|---|
| Telemetry map | Developers and operators | Links each critical flow and failure mode to logs, metrics, traces, audit events, and correlation fields |
| SLO and alert catalogue | Service owner and on-call team | Defines measurement, target, window, severity, owner, runbook, and paging action |
| Diagnostic dashboard and verification record | Incident responders | Answers impact, location, change, and next-action questions during an injected or known failure |

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Operability | SLO record | Markdown doc per `skill-composition-standards/references/slo-template.md` | `docs/slo/checkout-service.md` |
| Operability | Observability wiring note | Markdown doc listing logs, metrics, traces, and dashboards wired | `docs/observability/checkout-wiring.md` |
| Operability | Alert catalogue | Markdown doc listing alert name, threshold, and runbook link | `docs/observability/checkout-alerts.md` |

## Capability contract
Inspect telemetry read-only by default. Deploy collectors, change retention, create paging rules, or access sensitive logs only with explicit authority.

## Decision rules
| Condition | Action |
|---|---|
| Signal has no operator action | Do not page |
| Label cardinality is unbounded | Remove or aggregate it |
| SLO absent | Define service outcome first |

## Domain Anti-Patterns
- Logging secrets. Fix: redact at collection.
- Paging on CPU alone. Fix: alert on user impact.
- Using request IDs as metric labels. Fix: keep them in traces.
- Building ownerless dashboards. Fix: assign a decision and owner.
- Treating missing telemetry as healthy. Fix: alert on collection gaps.

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
- Load `references/observability-platform.md` when the task is platform buildout, SigNoz/OpenTelemetry stack design, collector topology, storage, retention, or dashboard infrastructure.
<!-- dual-compat-end -->
Use this skill when a system must be diagnosable in production. It covers operational telemetry, not just analytics. The goal is to make failures understandable, actionable, and bounded.

## Load Order

1. Load `world-class-engineering`.
2. Load this skill before finalizing architecture, APIs, jobs, or release design.
3. Pair it with `deployment-release-engineering` for rollout and incident visibility.

## Observability Workflow

### 1. Identify Critical Flows

For each critical flow define:

- trigger
- expected success outcome
- known failure modes
- business impact if degraded
- operator action if it fails

Instrument the highest-impact flows first.

### 2. Define Telemetry By Question

For every important signal, ask:

- what question will this answer?
- who needs the answer?
- how quickly must they see it?

Use this mapping:

- logs for detailed forensic context
- metrics for trend, rate, saturation, and alerting
- traces for multi-hop latency and dependency diagnosis
- audit events for material business or security actions
- profiles when CPU, memory, lock, or cost behavior matters

### 3. Design Correlation

Every request, job, and workflow should have:

- request or trace ID
- actor or service identity
- tenant or ownership context where applicable
- environment and version metadata
- release marker or deploy version
- dependency identity for important downstream calls

Without correlation, telemetry becomes noise.

### 4. Design High-Context Events

- Prefer structured events with useful dimensions over sparse text strings.
- Keep personally sensitive or secret fields out, but do not strip away the context needed to debug.
- Be deliberate about cardinality. High-cardinality dimensions can be valuable when they answer real debugging questions.
- Emit state transitions for long-running jobs and workflows so operators can reconstruct partial failure.

### 5. Define SLOs And Alerts

Use SLOs for user-facing reliability, not for every internal metric.

Define:

- success metric
- time window
- target threshold
- error budget implications

Alerts should page only when immediate action is required.

### 6. Build Dashboards For Diagnosis

Dashboards should answer:

- what is broken?
- who is affected?
- where is the bottleneck?
- what changed recently?
- what should the operator do next?

Do not create vanity dashboards that cannot guide action.

## Telemetry Standards

### Logs

- Use structured logs.
- Include IDs, actor context, tenant context, route or job name, and result.
- Log failures with enough context to debug, but never leak secrets or sensitive payloads.
- Separate business audit logs from application diagnostics.

### Metrics

Track:

- request rate
- error rate
- latency percentiles
- resource saturation
- queue depth and lag
- retry and fallback counts
- cache hit rates where relevant
- cost or token usage where relevant
- saturation signals for pools, workers, rate limits, or thread usage

Prefer percentiles and rates over averages.

### Traces

Trace:

- requests crossing service or process boundaries
- expensive background workflows
- external dependencies
- AI or retrieval pipelines with multiple stages
- deploy markers and notable async transitions when the platform supports them

### Audit Events

Audit events are required for:

- auth and role changes
- financial or ledger-affecting actions
- entitlement changes
- exports, deletions, and approvals
- AI actions with external or privileged side effects

### AI And Cost-Aware Telemetry

For AI-enabled systems, capture:

- model, prompt version, and tool path
- retrieval stages and source counts
- token, latency, and cost budgets
- eval outcomes or quality checks where available
- fallback, refusal, and validation failures

## Alert Design Rules

- Page on symptoms that require immediate human action.
- Ticket on trends or degradations that can wait.
- Dashboard everything else.
- Avoid alerts without a runbook path.
- Include environment, service, version, impact, and likely first checks.

See [references/alert-design.md](references/alert-design.md).

## Deliverables

For significant systems, produce:

- telemetry map for critical flows
- SLO definitions
- alert list with severity and owner
- dashboard outline
- audit event list
- trace and correlation ID strategy
- cardinality and sensitive-data guardrails

## Review Checklist

- [ ] Critical flows have explicit telemetry.
- [ ] IDs and tenant context are correlated across logs, metrics, and traces.
- [ ] Events contain enough context to debug without unsafe data leakage.
- [ ] Alerts map to operator action, not mere curiosity.
- [ ] SLOs reflect user impact, not internal implementation trivia.
- [ ] Audit events are defined for material actions.
- [ ] Sensitive data is excluded or redacted from telemetry.

## References

- [references/alert-design.md](references/alert-design.md): Alert severity and routing rules.
- [references/diagnosis-first-observability.md](references/diagnosis-first-observability.md): Event design, cardinality, release markers, and AI telemetry.
- [references/slo-template.md](references/slo-template.md): SLO template and service questions.
