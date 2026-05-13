# Absorbed Skill: observability-platform

Original entrypoint: `skills/observability-platform/SKILL.md`
Active parent skill: `skills/observability-monitoring/SKILL.md`
Status: Absorbed as reference material; this file preserves the old skill content for progressive disclosure.

---
name: observability-platform
description: Use when building or operating a production observability platform — SigNoz self-hosted (OTel-native, ClickHouse-backed) primary stack, OpenTelemetry instrumentation for PHP/Node.js/Android/iOS, Prometheus or VictoriaMetrics for metrics with cardinality discipline, Grafana dashboards and notification policies, distributed tracing with head- vs tail-based sampling, Sentry for client and server error monitoring, SLO/SLI/SLA design with multi-window multi-burn-rate alerts, AI-workload signals, runbooks, and blameless postmortems.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Observability Platform
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Building or operating a self-hosted observability platform across web, API, and mobile.
- Choosing the right pillar (log, metric, trace) for a given diagnostic question and wiring correlation between them.
- Designing SLOs, error budgets, and multi-window multi-burn-rate alerts that route through Grafana to PagerDuty or OpsGenie.
- Instrumenting a polyglot stack (PHP, Node.js, Android, iOS) through OpenTelemetry without locking into a vendor SDK.
- Adding AI-workload signals (embedding latency, retrieval recall, index freshness) to the same backend.

This skill is the platform-build/operate angle; for foundational concepts and day-to-day diagnosis discipline load `observability-monitoring` first.

## Do Not Use When

- The task is unrelated to `observability-platform` or would be better handled by a more specific companion skill.
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

## Three Pillars of Observability

**Logs** answer what happened at time `T`. **Metrics** answer how often and how much over a window. **Traces** answer why a request was slow or failing across services. Correlation is the whole point — every log line, metric exemplar, and span must share a `trace_id` so a Grafana alert links to SigNoz traces that link to logs.

Rule of thumb: emit a metric for what you must watch 24/7, a log for what you investigate after an alert, a span for what crosses a service boundary.

## Structured JSON Logging

Schema — every line must include `timestamp` (ISO-8601 UTC), `level`, `service`, `trace_id`, `span_id`, `user_id`, `tenant_id`, `msg`, plus event fields. Levels: `FATAL` (process exiting; page immediately), `ERROR` (request failed unrecovered; ticket or page by volume), `WARN` (recovered degradation; trend only), `INFO` (business events like `order.created`; default prod level), `DEBUG` (off in prod, on per-request via header), `TRACE` (local or short debugging only).

Node.js (`pino`):

```ts
import pino from "pino";
import { trace, context } from "@opentelemetry/api";
export const logger = pino({
  level: process.env.LOG_LEVEL ?? "info",
  formatters: {
    level: (label) => ({ level: label.toUpperCase() }),
    log: (obj) => {
      const ctx = trace.getSpan(context.active())?.spanContext();
      return ctx ? { ...obj, trace_id: ctx.traceId, span_id: ctx.spanId } : obj;
    },
  },
  base: { service: process.env.SERVICE_NAME ?? "api" },
  timestamp: pino.stdTimeFunctions.isoTime,
});
```

PHP (`monolog`):

```php
$log = new Monolog\Logger('billing-api');
$h = new Monolog\Handler\StreamHandler('php://stdout', Monolog\Logger::INFO);
$h->setFormatter(new Monolog\Formatter\JsonFormatter());
$log->pushHandler($h);
$log->pushProcessor(function (array $r): array {
    $ctx = \OpenTelemetry\API\Globals::tracerProvider()->getTracer('app')->getCurrentSpan()->getContext();
    $r['extra']['trace_id'] = $ctx->getTraceId();
    $r['extra']['span_id']  = $ctx->getSpanId();
    return $r;
});
$log->info('invoice.paid', ['tenant_id' => 'acme', 'invoice_id' => 'inv_42']);
```

## SigNoz Setup

OpenTelemetry-native APM with ClickHouse storage — a self-hosted alternative to Datadog you actually own.

```yaml
version: "3.9"
services:
  clickhouse:
    image: clickhouse/clickhouse-server:24.1.2
    volumes: ["./ch-data:/var/lib/clickhouse"]
    ulimits: { nofile: { soft: 262144, hard: 262144 } }
  query-service:
    image: signoz/query-service:0.47.0
    environment: { ClickHouseUrl: tcp://clickhouse:9000, STORAGE: clickhouse }
    depends_on: [clickhouse]
  frontend:
    image: signoz/frontend:0.47.0
    environment: { FRONTEND_API_ENDPOINT: http://query-service:8080 }
    ports: ["3301:3301"]
  otel-collector:
    image: signoz/signoz-otel-collector:0.102.1
    volumes: ["./otel-collector.yaml:/etc/otel-collector-config.yaml:ro"]
    ports: ["4317:4317", "4318:4318"]
```

Retention — set ClickHouse TTLs in Settings → Retention. Defaults are project-specific; size them against SLO query windows and disk budget rather than copying numbers. Common starting points: traces 15 d, logs 30 d, metrics 90 d, but confirm with the platform team before committing. Disk is the dominant cost; shorter TTL beats sampling. First dashboard: Services → pick `billing-api` → Save Panel → pin to `Service Health`. SigNoz auto-derives RED from spans — do this before writing custom PromQL.

Why SigNoz primary — one self-hosted deployable replaces Prometheus + Jaeger + a logs backend, is OpenTelemetry-native end-to-end ("supports OpenTelemetry as the primary way to instrument applications"), and stores everything in ClickHouse. Apps emit OTLP only — SigNoz appears in code as the collector URL, so swapping to Tempo + Loki + VictoriaMetrics later costs zero code change. Keep Prometheus or VictoriaMetrics in parallel only when host/infra metrics need a dedicated TSDB.

## OpenTelemetry Node.js

Install `@opentelemetry/sdk-node @opentelemetry/auto-instrumentations-node @opentelemetry/exporter-trace-otlp-http`. Require `otel.js` before app code:

```ts
import { NodeSDK } from "@opentelemetry/sdk-node";
import { getNodeAutoInstrumentations } from "@opentelemetry/auto-instrumentations-node";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import { Resource } from "@opentelemetry/resources";
import { TraceIdRatioBasedSampler } from "@opentelemetry/sdk-trace-base";
import { trace, SpanStatusCode } from "@opentelemetry/api";

new NodeSDK({
  resource: new Resource({
    "service.name": "billing-api",
    "deployment.environment": process.env.NODE_ENV ?? "dev",
    "service.version": process.env.GIT_SHA ?? "0.0.0",
  }),
  traceExporter: new OTLPTraceExporter({ url: "http://otel-collector:4318/v1/traces" }),
  sampler: new TraceIdRatioBasedSampler(0.1),
  instrumentations: [getNodeAutoInstrumentations()],
}).start();

const tracer = trace.getTracer("billing");
export async function chargeInvoice(id: string) {
  return tracer.startActiveSpan("billing.chargeInvoice", async (span) => {
    span.setAttribute("invoice.id", id);
    try { return await stripe.charges.create({ /* ... */ }); }
    catch (e) { span.recordException(e as Error); span.setStatus({ code: SpanStatusCode.ERROR }); throw e; }
    finally { span.end(); }
  });
}
```

## OpenTelemetry PHP

`composer require open-telemetry/sdk open-telemetry/exporter-otlp open-telemetry/opentelemetry-auto-slim`. Bootstrap loaded by `composer.json` `autoload.files`:

```php
use OpenTelemetry\SDK\Sdk;
use OpenTelemetry\SDK\Trace\TracerProvider;
use OpenTelemetry\SDK\Trace\SpanProcessor\BatchSpanProcessor;
use OpenTelemetry\Contrib\Otlp\{SpanExporter, OtlpHttpTransportFactory};

$exporter = new SpanExporter((new OtlpHttpTransportFactory())
    ->create('http://otel-collector:4318/v1/traces', 'application/x-protobuf'));
$provider = TracerProvider::builder()->addSpanProcessor(new BatchSpanProcessor($exporter))->build();
Sdk::builder()->setTracerProvider($provider)->setAutoShutdown(true)->buildAndRegisterGlobal();
```

Slim route spans are auto-captured. Use semantic attribute names: `http.method`, `http.route`, `http.status_code`, `db.system`, `db.statement` — Grafana and SigNoz panels key off the spec; do not invent variants.

## OpenTelemetry Mobile (Android, iOS)

For mobile, OpenTelemetry ships RUM agents — `io.opentelemetry.android:android-agent` and the `opentelemetry-swift` SPM package. Both expose OTLP/HTTP and pair with Sentry mobile SDKs (§ Sentry Setup) for crash capture; OTel handles RUM and the cross-service trace. Bootstrap on the main thread as early as possible (Application.onCreate / didFinishLaunchingWithOptions). The Android agent's ANR detector correlates frozen frames with the active `trace_id`, so a jank spike in Grafana resolves to the Compose frame that blocked the main thread.

Verify the latest stable BOM/SPM line at integration time — both lines have shipped on alpha tags. Full bootstrap snippets (Android Application + Compose `ScreenSpan`, iOS `TracedScreen` SwiftUI wrapper, `URLSessionInstrumentation`): `references/mobile-otel-bootstrap.md`.

## Prometheus Metrics

Four types — **Counter** (monotonic increments, use `rate()`), **Gauge** (up and down), **Histogram** (bucketed, aggregate with `histogram_quantile()`), **Summary** (client-side quantiles — avoid, they do not merge across instances).

RED naming plus latency buckets covering 5 ms to 10 s:

```text
http_requests_total{service,method,route,status}
http_request_duration_seconds_bucket{service,route,le}
http_requests_in_flight{service}
LatencyBuckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
```

Naming rules from `prometheus.io/docs/practices/naming/` — metrics "SHOULD have a suffix describing the unit, in plural form" (e.g. `_seconds`, `_bytes`, `_total`); use base units only ("always use bytes, even where bits appear more common"); differentiate variants by labels, not metric names (`api_http_requests_total{operation="create"}`, never `api_http_requests_total_create`).

Cardinality discipline (same source) — "every unique combination of key-value label pairs represents a new time series, which can dramatically increase the amount of data stored." Never label with `user_id`, `email`, `request_id`, `trace_id`. 10 k tenants x 50 routes = 500 k series = Prometheus OOM. When cardinality breaches 10M active series, switch the metrics tier to VictoriaMetrics — it ships a cardinality explorer and limiter and stays Prometheus-compatible at the query layer.

Recording rules precompute expensive expressions (`job:request_latency_seconds:mean5m`) so dashboards and alerts read cheap series. The alerting `for:` clause holds the alert "pending" through one-bucket noise — use it on every paging rule.

## Grafana Dashboards

Commit dashboard JSON to `ops/grafana/dashboards/service-health.json`:

```json
{
  "title": "Service Health — RED",
  "templating": { "list": [
    { "name": "service", "type": "query", "query": "label_values(http_requests_total, service)", "includeAll": true, "multi": true },
    { "name": "env", "type": "custom", "query": "prod,staging,dev" }
  ]},
  "panels": [
    { "title": "Request Rate", "targets": [{ "expr": "sum(rate(http_requests_total{service=~\"$service\"}[5m])) by (service)" }] },
    { "title": "Error Ratio", "targets": [{ "expr": "sum(rate(http_requests_total{service=~\"$service\",status=~\"5..\"}[5m])) / sum(rate(http_requests_total{service=~\"$service\"}[5m]))" }] },
    { "title": "Latency P95", "targets": [{ "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{service=~\"$service\"}[5m])) by (le, service))" }] }
  ]
}
```

Rule: one RED dashboard per service family, not per instance. Use `$service` so the dashboard scales.

Grafana alerting model — **contact points** specify "where notifications are sent" (email, Slack, webhook, PagerDuty, Grafana IRM); **notification policies** route by "label matching through a tree structure" rooted at the Default policy and decide both contact point and timing. Route critical alerts to PagerDuty, warnings to OpsGenie tickets:

```yaml
# grafana provisioning/alerting/policies.yaml
policies:
  - receiver: default-email
    group_by: [alertname, service]
    routes:
      - { receiver: pagerduty, matchers: ["severity = critical"], continue: false }
      - { receiver: opsgenie-ticket, matchers: ["severity = warning"], group_wait: 1m }
contactPoints:
  - name: pagerduty
    type: pagerduty
    settings: { integrationKey: $PD_ROUTING_KEY, severity: critical }
  - name: opsgenie-ticket
    type: opsgenie
    settings: { apiKey: $OG_API_KEY, priority: P3 }
```

On-call hygiene — rotate weekly with primary + secondary; run a written hand-off ritual (open alerts, in-flight changes, known-broken dashboards). Every page must link to a runbook; pages without runbooks are a defect logged against the alert. Post-incident, ask if the alert was actionable — if not, raise the threshold or delete it.

## Alerting Rules

```yaml
groups:
- name: api-red
  interval: 30s
  rules:
  - alert: ApiHighErrorRate
    expr: |
      sum(rate(http_requests_total{service="billing-api",status=~"5.."}[5m]))
      / sum(rate(http_requests_total{service="billing-api"}[5m])) > 0.02
    for: 5m
    labels: { severity: critical, team: platform }
    annotations:
      summary: "billing-api 5xx above 2% for 5m"
      description: "Error ratio {{ $value | humanizePercentage }} — check recent deploy."
      runbook_url: "https://runbooks.acme.io/billing-api/high-error-rate"
  - alert: ApiLatencyP95High
    expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{service="billing-api"}[5m])) by (le)) > 0.5
    for: 10m
    labels: { severity: warning, team: platform }
    annotations: { summary: "billing-api P95 > 500 ms", runbook_url: "https://runbooks.acme.io/billing-api/latency" }
```

Severity — `critical` pages on-call, `warning` opens a ticket, `info` is dashboard-only. Alertmanager routing:

```yaml
route:
  receiver: default
  group_by: [alertname, service]
  routes:
    - { matchers: [severity="critical"], receiver: pagerduty }
    - { matchers: [severity="warning"], receiver: opsgenie-ticket }
inhibit_rules:
  - source_matchers: [severity="critical"]
    target_matchers: [severity="warning"]
    equal: [service]
receivers:
  - { name: pagerduty, pagerduty_configs: [{ routing_key: "${PD_ROUTING_KEY}" }] }
  - { name: opsgenie-ticket, opsgenie_configs: [{ api_key: "${OG_API_KEY}", priority: P3 }] }
```

Inhibition suppresses `warning` when `critical` for the same service is firing — one incident, one page.

## Distributed Tracing with Jaeger

W3C trace context header — every service MUST propagate `traceparent: 00-<trace-id>-<parent-span-id>-<flags>`, e.g. `00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01` (flags `01` = sampled).

Sampling — **head-based** `TraceIdRatioBased(0.1)` at first hop is cheap but drops errors; **tail-based** at the collector retains them. SigNoz `tail_sampling` config:

```yaml
processors:
  tail_sampling:
    decision_wait: 30s
    policies:
      - { name: errors, type: status_code, status_code: { status_codes: [ERROR] } }
      - { name: slow,   type: latency,     latency: { threshold_ms: 1000 } }
      - { name: sample, type: probabilistic, probabilistic: { sampling_percentage: 5 } }
```

Analysis workflow: alert fires → open SigNoz → filter `service.name` and `status=error` in the alert window → sort by duration → open longest trace. The bottleneck span is almost always a DB query or a serial loop of HTTP calls.

## Sentry Setup

Next.js `sentry.client.config.ts`:

```ts
import * as Sentry from "@sentry/nextjs";
Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NEXT_PUBLIC_APP_ENV,
  tracesSampleRate: 0.1,
  replaysSessionSampleRate: 0.1, replaysOnErrorSampleRate: 1.0,
  integrations: [Sentry.replayIntegration({ maskAllText: true, blockAllMedia: true })],
});
```

`sentry.server.config.ts` mirrors this with `tracesSampleRate: 0.2` and `profilesSampleRate: 0.1`. Upload source maps via `withSentryConfig` in `next.config.js` with `SENTRY_AUTH_TOKEN`; without this, stack traces are minified noise.

- iOS: `SentrySDK.start { $0.dsn = ...; $0.tracesSampleRate = 0.2; $0.enableAutoPerformanceTracing = true }`.
- Android: `SentryAndroid.init(this) { it.dsn = BuildConfig.SENTRY_DSN; it.tracesSampleRate = 0.2; it.isAttachScreenshot = true }`.

Triage: new issue → on-call triages within 24h → assign owner and label `triage → in-progress → resolved` or `ignored` with written reason. Never leave `in-progress` past a sprint.

## SLO/SLI Design

An SLI is a measurement; an SLO is a promise; an SLA is the contract with consequences. Write the SLI in PromQL first.

```promql
# Availability SLI
sum(rate(http_requests_total{service="billing-api",status!~"5.."}[5m])) / sum(rate(http_requests_total{service="billing-api"}[5m]))
# Latency SLI — P95 under 500 ms
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{service="billing-api"}[5m])) by (le)) < 0.5
```

SLO — **99.9% availability over a rolling 28-day window**. Error budget: `(1 - 0.999) × 28d × 24h × 60min = 40.32 minutes of bad traffic per 28d`. Publish the SLO in Grafana alongside current burn. When the budget is spent, freeze feature releases and spend the next sprint on reliability — error budgets make the trade-off explicit instead of tribal.

## Error Budget Burn Rate

Burn rate = (error ratio over window) / (1 − SLO). Two conditions must hold to fire — error rate exceeds threshold over a long window AND a short window 1/12 the duration. Recommended starting parameters for a 99.9% SLO (Google SRE Workbook, "Alerting on SLOs"):

| Severity | Long window | Short window | Burn rate | Budget consumed |
|----------|-------------|--------------|-----------|-----------------|
| Page     | 1 hour      | 5 minutes    | 14.4      | 2%              |
| Page     | 6 hours     | 30 minutes   | 6         | 5%              |
| Ticket   | 3 days      | 6 hours      | 1         | 10%             |

```yaml
- alert: SloFastBurn
  expr: |
    (sum(rate(http_requests_total{service="billing-api",status=~"5.."}[1h]))
     / sum(rate(http_requests_total{service="billing-api"}[1h]))) > (14.4 * 0.001)
    and
    (sum(rate(http_requests_total{service="billing-api",status=~"5.."}[5m]))
     / sum(rate(http_requests_total{service="billing-api"}[5m]))) > (14.4 * 0.001)
  for: 2m
  labels: { severity: critical, slo: availability }
  annotations: { summary: "billing-api SLO fast burn (14.4x)", runbook_url: "https://runbooks.acme.io/slo/fast-burn" }
- alert: SloSlowBurn
  expr: |
    (sum(rate(http_requests_total{service="billing-api",status=~"5.."}[6h]))
     / sum(rate(http_requests_total{service="billing-api"}[6h]))) > (6 * 0.001)
  for: 15m
  labels: { severity: warning, slo: availability }
```

The `and` between 1h and 5m windows prevents stale firing — the short window must still be bad for the page to be valid.

## Real User Monitoring (RUM)

Core Web Vitals at P75 from real browsers — **LCP** ≤ 2.5 s, **INP** ≤ 200 ms, **CLS** ≤ 0.1. Sentry Performance captures these on `@sentry/nextjs`. Session replay — modest sample rates, aggressive masking:

```ts
Sentry.init({
  replaysSessionSampleRate: 0.1, replaysOnErrorSampleRate: 1.0,
  integrations: [Sentry.replayIntegration({
    maskAllText: true, maskAllInputs: true, blockAllMedia: true, blockClass: "sensitive",
  })],
});
```

Privacy — replays must mask all PII by default. An unmasked DOB or IBAN on a support agent screen is a DPPA breach. Add `class="sensitive"` to elements rendering personal data.

## On-Call Runbooks

Every paging alert must have a `runbook_url`. Keep the runbook to one page with these sections:

1. **Symptom** — exact alert text and Grafana panel link.
2. **Impact** — which users see what, whether revenue is blocked.
3. **First checks** — three dashboards and two log queries for the first 5 minutes.
4. **Known causes** — ranked by frequency with remediation steps.
5. **Escalation** — who to wake when step 4 fails.

Severity ladder — **SEV1** revenue-impacting outage (page primary within 5 min), **SEV2** major degradation beyond SLO (page within 15 min), **SEV3** minor, workaround exists (ticket next business day), **SEV4** cosmetic or internal-only (backlog).

Escalation — primary on-call → secondary after 15 min no-ack → engineering manager after 30 min → VP Eng after 60 min. Status page updates every 30 min during SEV1–SEV2 even if "no new information." Silence is the second incident.

## Blameless Postmortem

Write one within 5 business days of every SEV1 and SEV2.

1. **Timeline** — reconstructed from `trace_id`s, log timestamps, chat logs. Absolute UTC, not "around 3 pm."
2. **Root cause (5-why)** — never stop at the first "why." Deploy broke API → config key misnamed → typo not caught in CI → schema test disabled → no one owned it.
3. **Impact** — users affected, revenue lost, error budget spent.
4. **Went well / went poorly** — no names; focus on systems and signals.
5. **Action items** — each a JIRA ticket with owner and due date. No vague "improve monitoring"; write "add alert `KafkaLagHigh` threshold 5000 by 2026-05-01, owner @dee."

Publish internally. Anonymise and publish externally for customer-impacting SEV1s — it builds more trust than any marketing page.

## Production Dashboards

Four dashboards every SaaS needs — **Service Health** (RED per service), **Infrastructure** (host CPU/memory/disk/network), **Business KPIs** (MRR, active users, signups, churn), **SLO Tracker** (current SLO % vs target, budget remaining per service). Pin all four to the on-call TV. During an incident, responders should not hunt dashboards — they should read them. PromQL recipes and recording-rule patterns: `references/dashboards-and-promql.md`.

## AI-Workload Signals

Treat AI features as production services with their own SLIs. Emit through the same OTel pipeline; cross-reference `vector-databases` and `ai-rag-patterns` for measurement methodology.

| Metric | Type | What it measures | Why it matters |
|--------|------|------------------|----------------|
| `embedding_write_latency_seconds` | histogram | time to embed + upsert one document | regressions break ingest pipelines silently |
| `query_recall_at_k` | gauge | fraction of golden-set queries returning the expected chunk in top-K | the only safety net against silent retrieval drift |
| `index_freshness_seconds` | gauge | `now() - max(doc.indexed_at)` per tenant | tells you when the index has fallen behind |
| `rag_context_relevance` | gauge (sampled) | RAGAS-style score over a daily golden-set sample | end-to-end answer quality |

Do not hardcode SLO targets — they are workload-specific. Build the golden set with domain experts, run it nightly, and alert on **trend regression** (recall drop ≥ 5 pp week-over-week) rather than absolute thresholds.

## Companion Skills

- `observability-monitoring` — foundational logs/metrics/traces and diagnosis discipline — load first
- `reliability-engineering` — toil elimination, risk quantification, incident response
- `database-reliability` — database SLIs, replication lag tracking
- `kubernetes-platform` — K8s pod/node metrics, PodMonitor for Prometheus
- `cicd-pipelines` — deployment alerts tied to releases
- `vector-databases`, `ai-rag-patterns` — methodology for the AI-workload signals above

## Sources

- *Observability Engineering* — Majors, Fong-Jones, Miranda (O'Reilly).
- *Site Reliability Engineering* and *The Site Reliability Workbook* — Google, free at `sre.google/books` (chapters: Service Level Objectives, Implementing SLOs, Alerting on SLOs).
- SigNoz docs `signoz.io/docs/introduction/`; OpenTelemetry concepts and language guides `opentelemetry.io/docs/`; Prometheus naming + alerting rules `prometheus.io/docs/practices/naming/` and `/configuration/alerting_rules/`; VictoriaMetrics `docs.victoriametrics.com/`; Grafana alerting fundamentals `grafana.com/docs/grafana/latest/alerting/fundamentals/`; Sentry platforms `docs.sentry.io/platforms/`; W3C Trace Context `w3.org/TR/trace-context/`.
