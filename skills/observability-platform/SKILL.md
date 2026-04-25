---
name: observability-platform
description: Use when building production observability for a SaaS platform — SigNoz self-hosted stack,
  OpenTelemetry instrumentation for Node.js/PHP/Android/iOS, Prometheus + Grafana RED dashboards,
  alerting rules, distributed tracing with Jaeger, Sentry for errors, SLO/SLI design, error budget
  burn-rate alerts, runbooks, and blameless postmortems.
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

- Use when building production observability for a SaaS platform — SigNoz self-hosted stack, OpenTelemetry instrumentation for Node.js/PHP/Android/iOS, Prometheus + Grafana RED dashboards, alerting rules, distributed tracing with Jaeger, Sentry for errors, SLO/SLI design, error budget burn-rate alerts, runbooks, and blameless postmortems.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

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

Retention — set ClickHouse TTLs in Settings → Retention: traces `15d`, logs `30d`, metrics `90d`. Disk is the dominant cost; shorter TTL beats sampling. First dashboard: Services → pick `billing-api` → Save Panel → pin to `Service Health`. SigNoz auto-derives RED from spans — do this before writing custom PromQL.

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

## OpenTelemetry Android

```kotlin
// build.gradle.kts
dependencies {
    implementation(platform("io.opentelemetry:opentelemetry-bom:1.38.0"))
    implementation("io.opentelemetry.android:android-agent:0.8.0-alpha")
}
// MyApp.kt
class MyApp : Application() {
    lateinit var rum: OpenTelemetryRum
    override fun onCreate() {
        super.onCreate()
        rum = OpenTelemetryRum.builder(this, OtelRumConfig())
            .setEndpoint("https://otel.acme.io")
            .addInstrumentation(AnrInstrumentation())
            .addInstrumentation(CrashReporterInstrumentation())
            .build()
    }
}
// Compose screen tracking via CompositionLocal
val LocalTracer = staticCompositionLocalOf<Tracer> { error("no tracer") }
@Composable fun ScreenSpan(name: String, content: @Composable () -> Unit) {
    val tracer = LocalTracer.current
    DisposableEffect(name) {
        val span = tracer.spanBuilder("screen.$name").startSpan()
        onDispose { span.end() }
    }; content()
}
```

ANR detector correlates frozen frames with active `trace_id` — a jank spike in Grafana resolves to the Compose frame that blocked the main thread.

## OpenTelemetry iOS

SPM: add `https://github.com/open-telemetry/opentelemetry-swift` at `1.10.1`.

```swift
import OpenTelemetryApi
import OpenTelemetrySdk
import OpenTelemetryProtocolExporterHttp
import URLSessionInstrumentation

func bootstrapOtel() {
    let resource = Resource(attributes: ["service.name": .string("ios-app"), "deployment.environment": .string("prod")])
    let exporter = OtlpHttpTraceExporter(endpoint: URL(string: "https://otel.acme.io/v1/traces")!)
    let provider = TracerProviderBuilder()
        .add(spanProcessor: BatchSpanProcessor(spanExporter: exporter))
        .with(resource: resource).build()
    OpenTelemetry.registerTracerProvider(tracerProvider: provider)
    URLSessionInstrumentation(configuration: URLSessionInstrumentationConfiguration())
}
struct TracedScreen<Content: View>: View {
    let name: String
    @Environment(\.scenePhase) private var phase
    @ViewBuilder let content: () -> Content
    @State private var span: Span?
    var body: some View {
        content()
            .onAppear { span = OpenTelemetry.instance.tracerProvider.get(instrumentationName: "ui").spanBuilder(spanName: "screen.\(name)").startSpan() }
            .onDisappear { span?.end() }
            .onChange(of: phase) { if $0 == .background { span?.end(); span = nil } }
    }
}
```

## Prometheus Metrics

Four types — **Counter** (monotonic increments, use `rate()`), **Gauge** (up and down), **Histogram** (bucketed, aggregate with `histogram_quantile()`), **Summary** (client-side quantiles — avoid, they do not merge across instances).

RED naming plus latency buckets covering 5 ms to 10 s:

```text
http_requests_total{service,method,route,status}
http_request_duration_seconds_bucket{service,route,le}
http_requests_in_flight{service}
LatencyBuckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
```

Never use high-cardinality labels (`user_id`, `request_id`). 10 k tenants × 50 routes = 500 k series = Prometheus OOM.

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

Burn rate = (error ratio over window) / (1 − SLO). Multi-window multi-burn-rate (Google SRE Workbook Ch. 5):

- **Fast burn** — 1h window, 14.4× rate → 2% of monthly budget burns in 1h → **page on-call**.
- **Slow burn** — 6h window, 6× rate → 5% in 6h → **ticket**, no page.

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

Four dashboards every SaaS needs — **Service Health** (RED per service), **Infrastructure** (host CPU/memory/disk/network), **Business KPIs** (MRR, active users, signups, churn), **SLO Tracker** (current SLO % vs target, budget remaining per service). Pin all four to the on-call TV.

```promql
# Service Health
sum(rate(http_requests_total[5m])) by (service)
sum(rate(http_requests_total{status=~"5.."}[5m])) by (service) / sum(rate(http_requests_total[5m])) by (service)
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service))
# Infrastructure
1 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) by (instance)
node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes
(node_filesystem_size_bytes - node_filesystem_avail_bytes) / node_filesystem_size_bytes
# Business KPIs
sum(business_mrr_usd)
sum(increase(business_signups_total[1d]))
sum(active_users_gauge{window="24h"})
sum(increase(business_churn_total[30d])) / sum(business_customers_gauge offset 30d)
# SLO Tracker — availability % and budget remaining
sum(rate(http_requests_total{status!~"5.."}[28d])) by (service)
  / sum(rate(http_requests_total[28d])) by (service)
1 - (sum(rate(http_requests_total{status=~"5.."}[28d])) by (service)
     / sum(rate(http_requests_total[28d])) by (service)) / 0.001
```

During an incident, responders should not hunt dashboards — they should read them.

## Companion Skills

- `observability-monitoring` — foundational logs/metrics/traces — load first
- `reliability-engineering` — toil elimination, risk quantification, incident response
- `database-reliability` — database SLIs, replication lag tracking
- `kubernetes-platform` — K8s pod/node metrics, PodMonitor for Prometheus
- `cicd-pipelines` — deployment alerts tied to releases

## Sources

- *Observability Engineering* — Majors, Fong-Jones, Miranda (O'Reilly); *Site Reliability Engineering* — Google (free at `sre.google/books`)
- SigNoz `signoz.io/docs`; OpenTelemetry `opentelemetry.io/docs`; Prometheus `prometheus.io/docs`; Grafana `grafana.com/docs/grafana`; Sentry `docs.sentry.io`