# Diagnosis-First Observability

Use this reference when you need telemetry that can answer unfamiliar production questions, not only predefined dashboard checks.

## Event Design Rules

- Emit structured events with stable names and useful dimensions.
- Include actor, tenant, environment, version, request or trace ID, and operation name where those dimensions matter.
- Record state transitions for async jobs and long workflows.
- Keep business audit events separate from diagnostic application logs.

## Cardinality Rules

- High-cardinality fields are acceptable when they materially improve debugging.
- Avoid unbounded dimensions that add cost without helping diagnosis.
- Prefer sampled or filtered high-cardinality data over removing all rich dimensions.

## Release Correlation

- Emit release or deploy markers into your telemetry system.
- Tag metrics, traces, and logs with version metadata when the platform allows it.
- Make dashboards answer "what changed recently?" without manual archaeology.

## AI Telemetry Rules

- Capture model, prompt version, tool sequence, retrieval counts, and token or cost usage.
- Log validation failures and fallback paths separately from model output content.
- Use eval outputs and safety checks as telemetry where quality risk matters.

## Dashboard Rules

- Prefer dashboards that support diagnosis over KPI-only views.
- Pair symptom panels with dependency, saturation, and recent-change context.
- Link alerts to the dashboard or query that helps the responder act first.
