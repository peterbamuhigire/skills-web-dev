---
name: growth-telemetry-pipeline
description: Use when building the telemetry infrastructure that powers growth analytics
  and experimentation — the 5-stage pipeline (ingestion to transformation to storage
  to serving to visualization), logs/metrics/events/traces quartet, instrumentation
  priority-setting, data-lake vs data-warehouse choice, pipeline-health alerting,
  and growth-specific anti-patterns (GUID cookies, measuring absence, over-instrumentation,
  PII leakage). Distinct from observability-monitoring (system health) and
  python-data-pipelines (generic ETL) — this is growth-purpose instrumentation. Based
  on Okonkwo, *Growth Engineering* (Wiley, 2025).
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Growth Telemetry Pipeline

Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Use when building the telemetry infrastructure that powers growth analytics and experimentation — the 5-stage pipeline (ingestion to transformation to storage to serving to visualization), logs/metrics/events/traces quartet, instrumentation priority-setting, data-lake vs data-warehouse choice, pipeline-health alerting, and growth-specific anti-patterns.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is observability for system health (use `observability-monitoring` instead).
- The task is generic ETL for non-growth data (use `python-data-pipelines` instead).
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- The product's North Star metric or the business question the pipeline must answer.
- The existing data stack (warehouse, streaming, BI tool) or the greenfield choice.
- Privacy and compliance constraints (PII, DPPA, GDPR) that shape ingestion.

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

- Instrumentation plan — what to instrument for which business question.
- Event schema registry.
- Pipeline architecture diagram (ascii or mermaid).
- Alerting runbook for pipeline health.
- Dashboard ownership list.

## References

- `references/instrumentation-plan-template.md` — question-driven instrumentation template.
- `references/event-schema-registry.md` — event envelope, naming, versioning.
- `references/pipeline-health-runbook.md` — the 5 mandatory alerts and responses.
- `references/anti-patterns-catalog.md` — expanded anti-patterns with failure stories.
<!-- dual-compat-end -->

## The Three Foundational Questions

Before instrumenting anything, answer:

1. Why does this product exist? (defines the North Star)
2. Who is it serving? (defines the user cohorts worth tracking)
3. What is its role in the business? (defines which commercial signals matter)

Instrumentation priorities flow from the answers. Skipping this step is the root cause of dashboards-no-one-looks-at. A 200-event taxonomy built without a North Star produces storage cost and no decisions. A 20-event taxonomy aligned to a specific North Star produces every decision the growth team needs for a year.

## The Telemetry Quartet

Every growth system needs all four. They are not substitutes.

- **Logs** — discrete text records of events. Use for debugging and audit trails.
- **Metrics** — numeric time-series (counters, gauges). Use for alerting and dashboards.
- **Events** — user or system actions with structured properties. Use for funnels, cohorts, and experiments. *This is the core growth data type.*
- **Traces** — request paths across services with latency per hop. Use to debug slow conversions.

Growth teams that conflate logs and events end up with structured events buried in free-text log lines, un-queryable. Teams that conflate metrics and events end up with pre-aggregated counters and no way to slice by user cohort after the fact.

## The 5-Stage Pipeline

Reference architecture. Every stage needs a health check.

- **Ingestion** — SDK or server-side collectors batch events into a stream (Kafka, Kinesis, Pub/Sub). Target: event received to stream within 1 second.
- **Transformation** — validate schema, enrich with user/session context, normalise identifiers, strip PII. Target: stream to transformed within 1 minute.
- **Storage** — raw events to data lake (S3/GCS Parquet); modelled tables to warehouse (BigQuery/Snowflake/Redshift).
- **Serving** — materialised views, feature flags API, cohort API, experiment-scorecard jobs.
- **Visualisation** — dashboards (Metabase, Looker, Superset, Mode), self-serve analytics, scheduled scorecards.

Each stage needs a health check. A silent ingestion failure drops data invisibly; the product team "sees" a flat metric on a dashboard that is actually a broken pipe.

## Data Lake vs Data Warehouse

- **Lake** — cheap, schema-on-read, raw, flexible, slow.
- **Warehouse** — expensive, schema-on-write, modelled, fast.

Run both. Lake holds raw events for historical reprocessing and ML feature generation; warehouse holds modelled aggregates for dashboards and experiment scorecards. Rule of thumb: raw events land in the lake within 5 minutes; modelled aggregates land in the warehouse within 30 minutes. If an event cannot be reprocessed from the lake 6 months later, you built a warehouse-only pipeline and will regret it the first time a metric definition changes.

## Pipeline-Health Alerting

Mandatory, not optional. These must page on-call. See `references/pipeline-health-runbook.md` for response procedures.

- **Ingestion lag** — end-to-end lag from client event to warehouse table > 10 minutes. Page.
- **Row-count deviation** — today's daily row count vs the 7-day median by more than ±20%. Page.
- **Schema violation rate** — rejected events > 0.1% of total. Page.
- **Null identifier rate** — `user_id` or `session_id` null on > 1% of events. Page.
- **Backfill job failure** — any failure. Page.

Silent pipeline failures look like flat metrics on dashboards; the product team interprets stagnation that is actually data loss. The cost of not paging is weeks of wrong decisions; the cost of paging is one on-call ack.

## Instrumentation Anti-Patterns

Covered in detail in `references/anti-patterns-catalog.md`. Summary:

- **Over-instrumentation** — logging every hover, blowing up cloud bill without insight. Rule: every event must map to a question on a roadmap document.
- **Inconsistent identifiers** — logged-in `user_id` on page A, GUID cookie on page B, device ID on mobile. Funnels break. Adopt one canonical identifier hierarchy: `user_id > anonymous_id > device_id`, with explicit stitching at login.
- **Logging PII in event properties** — emails, names, raw addresses written to engineering storage. Hash or tokenise at ingestion; never log payment details.
- **Measuring outputs without measuring absence** — you log clicks but not impressions, so you cannot compute click-through rate. Always log the denominator.
- **Dashboards without owners** — a dashboard that no named engineer maintains is legacy within 3 months.
- **Alert fatigue** — 50 alerts/day means 0 alerts. Tier alerts by impact.

## Chart-Type Selection

Pick the chart from the question, not the data shape.

- **Line** — trends over time (DAU, conversion rate).
- **Bar** — cohort comparisons (activation rate by acquisition channel).
- **Funnel** — sequential conversion (signup → activation → retention).
- **Heatmap** — retention-by-week-since-signup.
- **Scatter** — correlation exploration (not for dashboards; for one-off analysis).
- **Pie** — only for 4 or fewer categories that sum to a whole (rare; most "pie-appropriate" data is better as a stacked bar).

## Growth Data Contract

The pipeline must guarantee:

- Every event has `event_name`, `event_timestamp`, `user_id` OR `anonymous_id`, `session_id`, `event_properties`, `context` (device, locale, app version).
- Schema registry is versioned; breaking changes require a new event name, not silent mutation of the existing name.
- Event arrival order is not guaranteed; all queries must handle late-arriving events up to 7 days.

See `references/event-schema-registry.md` for the canonical envelope and naming rules.

## Companion Skills

- `observability-monitoring` — system-health telemetry (logs, traces, SLOs for services).
- `python-data-pipelines` — the generic ETL mechanics used inside the transformation stage.
- `saas-growth-metrics` — the analytics consumers of this pipeline.
- `experiment-engineering` — trigger events and counterfactual logging ride on this pipeline.
- `uganda-dppa-compliance` — PII handling requirements for Uganda-regulated products.

## Sources

- *Growth Engineering* — Joseph Okonkwo (Wiley, 2025).
