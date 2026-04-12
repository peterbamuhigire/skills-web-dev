---
name: observability-monitoring
description: Use when designing or reviewing logs, metrics, traces, alerts, SLOs, dashboards, audit events, or production telemetry for web apps, APIs, SaaS platforms, mobile backends, and AI systems. Covers instrumentation strategy, diagnosis-first telemetry, alert quality, and operational visibility.
---

# Observability Monitoring

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

### 3. Design Correlation

Every request, job, and workflow should have:

- request or trace ID
- actor or service identity
- tenant or ownership context where applicable
- environment and version metadata

Without correlation, telemetry becomes noise.

### 4. Define SLOs And Alerts

Use SLOs for user-facing reliability, not for every internal metric.

Define:

- success metric
- time window
- target threshold
- error budget implications

Alerts should page only when immediate action is required.

### 5. Build Dashboards For Diagnosis

Dashboards should answer:

- what is broken?
- who is affected?
- where is the bottleneck?
- what changed recently?

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

Prefer percentiles and rates over averages.

### Traces

Trace:

- requests crossing service or process boundaries
- expensive background workflows
- external dependencies
- AI or retrieval pipelines with multiple stages

### Audit Events

Audit events are required for:

- auth and role changes
- financial or ledger-affecting actions
- entitlement changes
- exports, deletions, and approvals
- AI actions with external or privileged side effects

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

## Review Checklist

- [ ] Critical flows have explicit telemetry.
- [ ] IDs and tenant context are correlated across logs, metrics, and traces.
- [ ] Alerts map to operator action, not mere curiosity.
- [ ] SLOs reflect user impact, not internal implementation trivia.
- [ ] Audit events are defined for material actions.
- [ ] Sensitive data is excluded or redacted from telemetry.

## References

- [references/alert-design.md](references/alert-design.md): Alert severity and routing rules.
- [references/slo-template.md](references/slo-template.md): SLO template and service questions.
