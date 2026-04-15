# Tenant Observability

Per-tenant logs, metrics, traces, and alerting that do not destroy
Prometheus cardinality or leak tenant data across dashboards. Read after
`SKILL.md`. Cross-reference `observability-monitoring` for SLO method
and `multi-tenant-saas-architecture` for identity scoping.

## Label strategy (the cardinality problem)

A `tenant` label on every metric will kill Prometheus. Ten thousand
tenants times a hundred metrics times ten histograms buckets equals ten
million active series — most Prometheus single nodes stop responding
past 2-5 million.

### Rule

- Only put `tenant` on a small set of high-value metrics — SLO metrics
  and top-level business KPIs.
- Never put `tenant` on high-cardinality internal metrics (per-
  endpoint histograms, per-query timings).
- For deep per-tenant debugging, use traces (sampled), not metrics.

### Allow-list of metrics that carry `tenant`

```text
http_requests_total{tenant,status}
http_request_duration_seconds_bucket{tenant,route}  # routes, not URIs
app_errors_total{tenant,class}
app_feature_usage_total{tenant,feature}
billing_events_total{tenant,event}
```

### Deny-list (never add tenant to these)

```text
go_*, process_*, node_*, container_*, kube_*
any metric already exposed by Prometheus exporters
any metric that has >20 label values on other dimensions
```

## kube-state-metrics with tenant relabeling

Propagate the namespace label `tenant` into metrics via
PodMonitor/ServiceMonitor relabeling rules.

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata: { name: app, namespace: tenant-acme }
spec:
  selector: { matchLabels: { app: api } }
  endpoints:
    - port: http
      interval: 30s
      relabelings:
        - action: replace
          sourceLabels: [__meta_kubernetes_namespace]
          regex: "tenant-(.+)"
          replacement: "$1"
          targetLabel: tenant
```

## Grafana folders per tenant

Grafana folders + RBAC give tenant admins access to only their own
dashboards.

```text
Grafana
  Platform (internal staff only)
  Tenants/
    acme/       [viewer: acme-admins group]
    globex/     [viewer: globex-admins group]
```

Dashboards are templated with a `$tenant` variable defaulted from the
folder name. Queries enforce the filter:

```text
sum by (status) (
  rate(http_requests_total{tenant="$tenant"}[5m])
)
```

Never rely on the UI alone to filter. If a metric exposes another
tenant's data without a `tenant` filter, the dashboard is broken.

## Alertmanager routing by tenant label

```yaml
route:
  receiver: platform-default
  group_by: [alertname, tenant]
  routes:
    - matchers: [ 'tenant=~".+"' ]
      receiver: tenant-fanout
      continue: true
  inhibit_rules: []
receivers:
  - name: platform-default
    slack_configs: [{ channel: '#alerts-platform' }]
  - name: tenant-fanout
    webhook_configs:
      - url: http://tenant-router.platform/alerts
        send_resolved: true
```

`tenant-router` looks up the tenant from the alert labels and dispatches
to the customer-chosen channel (email, Slack webhook, PagerDuty). Keep
the router idempotent and rate-limited.

## Loki with tenant header

Loki natively supports multi-tenancy via `X-Scope-OrgID`. Either:

- Hard multi-tenancy: one tenant per Loki tenant, each with its own
  quota and retention — strong isolation, highest cost.
- Single Loki tenant with `tenant` label on every log line — cheaper,
  enforce filtering in dashboards and LogQL.

### Promtail / Alloy relabel config

```yaml
scrape_configs:
  - job_name: kubernetes-pods
    kubernetes_sd_configs: [{ role: pod }]
    relabel_configs:
      - action: replace
        source_labels: [__meta_kubernetes_namespace]
        regex: "tenant-(.+)"
        replacement: "$1"
        target_label: tenant
      - action: keep
        source_labels: [tenant]
        regex: ".+"
```

### LogQL filter rule

```logql
{tenant="acme", app="api"} |= "error"
  | json
  | line_format "{{.ts}} {{.level}} {{.msg}}"
```

## Traces per tenant

- Add `tenant.id` as a resource attribute on every span.
- Sample aggressively at the collector; keep 100% for errors and a
  low percentage for successes (head-based + tail-based for errors).
- Split tenant traces into tenant-scoped projects in the backend
  (Tempo, Honeycomb, Datadog) if the backend supports it.

## SLO per tier (example)

```text
Free tier        99.0% monthly availability, 1s p95 latency
Business tier    99.5% monthly availability, 500ms p95 latency
Enterprise tier  99.9% monthly availability, 300ms p95 latency
```

Compute SLI per tenant from the allow-list metrics; compute error
budget burn per tenant cohort; alert on burn rate, not instantaneous
thresholds.

## Cardinality controls

- `--storage.tsdb.max-block-chunks` and `--storage.tsdb.retention.size`
  bounded.
- Recording rules drop raw histogram buckets into pre-aggregated
  series with fewer labels.
- Prometheus `metric_relabel_configs` that drop metrics above a
  cardinality threshold.
- Regular cardinality report (`/api/v1/status/tsdb`) reviewed weekly.

## Anti-patterns

- Putting `user_id` or `request_id` as Prometheus labels — that is
  what tracing and logs are for.
- Grafana dashboards without a `tenant` query filter — tenant A sees
  tenant B.
- One Loki tenant per customer when you have 5,000 customers — chunk
  count explodes; cost is silent until the first bill.
- Alert rules that fire per tenant with no deduplication — on-call
  gets 500 pages at 03:00 for a single shared outage.
- Mixing internal platform alerts and tenant-visible alerts in one
  Alertmanager route tree — one misroute leaks internal
  diagnostics to customers.
