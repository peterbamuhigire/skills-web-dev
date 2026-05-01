# Observability Stack — Prometheus, Grafana, Loki, Tempo, OTEL

The production stack: metrics (Prometheus), logs (Loki), traces (Tempo), dashboards (Grafana), alerting (Alertmanager), and a common ingestion layer (OpenTelemetry Collector). Golden signals drive what you watch, not "install every exporter".

## Architecture

```text
    app Pods ----(OTLP)----> OTEL Collector ----> Tempo (traces)
                                              |-> Prometheus Remote-Write (metrics)
                                              |-> Loki (logs)

    kube-state-metrics --+
    node-exporter -------+--> Prometheus --scrape-- ServiceMonitor/PodMonitor
    kubelet cAdvisor ----+

    Grafana reads all three datasources. Alertmanager routes Prometheus alerts.
```

## kube-prometheus-stack — the baseline install

Ships Prometheus, Alertmanager, Grafana, kube-state-metrics, node-exporter, plus the Prometheus Operator CRDs.

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm upgrade --install kps prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  --version 62.3.0 \
  -f values-kps.yaml
```

### Key values-kps.yaml excerpts

```yaml
prometheus:
  prometheusSpec:
    retention: 15d                       # local retention
    retentionSize: "45GB"
    resources:
      requests: { cpu: 500m, memory: 4Gi }
      limits:   { cpu: 2,    memory: 8Gi }
    storageSpec:
      volumeClaimTemplate:
        spec:
          storageClassName: gp3
          accessModes: [ReadWriteOnce]
          resources: { requests: { storage: 100Gi } }
    remoteWrite:                         # ship to Mimir/Thanos/Cortex for long-term
      - url: https://mimir.internal/api/v1/push
    serviceMonitorSelectorNilUsesHelmValues: false
    podMonitorSelectorNilUsesHelmValues: false
    ruleSelectorNilUsesHelmValues: false
alertmanager:
  alertmanagerSpec:
    storage:
      volumeClaimTemplate:
        spec: { accessModes: [ReadWriteOnce], resources: { requests: { storage: 10Gi } } }
grafana:
  admin:
    existingSecret: grafana-admin
  persistence: { enabled: true, size: 10Gi, storageClassName: gp3 }
  sidecar:
    dashboards: { enabled: true, searchNamespace: ALL }
    datasources: { enabled: true, searchNamespace: ALL }
```

## ServiceMonitor — scrape via Service

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: api
  namespace: production
  labels: { release: kps }               # must match Prometheus `serviceMonitorSelector`
spec:
  selector:
    matchLabels: { app.kubernetes.io/name: api }
  namespaceSelector:
    matchNames: [production]
  endpoints:
    - port: metrics                      # named port on the Service
      path: /metrics
      interval: 30s
      scrapeTimeout: 10s
      relabelings:
        - sourceLabels: [__meta_kubernetes_pod_label_app_kubernetes_io_version]
          targetLabel: version
```

## PodMonitor — scrape Pods directly (no Service required)

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata: { name: worker, namespace: production, labels: { release: kps } }
spec:
  selector: { matchLabels: { app.kubernetes.io/name: worker } }
  podMetricsEndpoints:
    - port: metrics
      path: /metrics
      interval: 30s
```

Use PodMonitor when workload has no Service (Jobs, headless workers).

## PrometheusRule — alerts as code

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata: { name: api-alerts, namespace: production, labels: { release: kps } }
spec:
  groups:
    - name: api.slo
      interval: 30s
      rules:
        - alert: ApiHighErrorRate
          expr: |
            sum(rate(http_requests_total{job="api",status=~"5.."}[5m]))
              / sum(rate(http_requests_total{job="api"}[5m])) > 0.01
          for: 10m
          labels: { severity: page, team: platform }
          annotations:
            summary: "API 5xx rate > 1% for 10m"
            runbook: https://runbooks.internal/api-5xx
        - alert: ApiHighLatency
          expr: |
            histogram_quantile(0.99,
              sum(rate(http_request_duration_seconds_bucket{job="api"}[5m])) by (le)
            ) > 0.5
          for: 10m
          labels: { severity: page }
```

## Golden signals (RED + USE)

For every service, dashboard these four:

| Signal | What | PromQL sketch |
|---|---|---|
| **Latency** | Request duration p50/p95/p99 | `histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))` |
| **Traffic** | Requests per second | `sum(rate(http_requests_total[1m]))` |
| **Errors** | Error rate | `sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))` |
| **Saturation** | Resource pressure | CPU throttling, memory near limit, queue depth |

For every node/host: Utilisation, Saturation, Errors (USE).

## Loki + log collection

### Install Loki (SimpleScalable)

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm upgrade --install loki grafana/loki \
  -n monitoring \
  --set deploymentMode=SimpleScalable \
  --set backend.replicas=3 \
  --set read.replicas=3 \
  --set write.replicas=3 \
  --set loki.storage.type=s3 \
  --set loki.storage.bucketNames.chunks=loki-chunks-prod \
  --set loki.storage.s3.region=eu-west-1
```

### Collection: Promtail (easy) or Vector / Grafana Alloy (better)

Grafana Alloy (successor to Grafana Agent) is now the recommended collector:

```yaml
# alloy-config.river
discovery.kubernetes "pods" { role = "pod" }
discovery.relabel "pods" {
  targets = discovery.kubernetes.pods.targets
  rule { source_labels = ["__meta_kubernetes_namespace"]; target_label = "namespace" }
  rule { source_labels = ["__meta_kubernetes_pod_name"];  target_label = "pod" }
}
loki.source.kubernetes "pods" {
  targets    = discovery.relabel.pods.output
  forward_to = [loki.write.default.receiver]
}
loki.write "default" {
  endpoint { url = "http://loki-gateway.monitoring/loki/api/v1/push" }
}
```

Vector is a strong alternative when you need heavy log parsing/enrichment on the way through.

### Label discipline — the one thing that kills Loki

Loki is fast when labels are **low cardinality** (namespace, app, level) and slow when they are high cardinality (user_id, request_id, traceID). High-cardinality fields belong in the log *line*, not as labels.

## Tempo — distributed tracing

```bash
helm upgrade --install tempo grafana/tempo-distributed \
  -n monitoring \
  --set storage.trace.backend=s3 \
  --set storage.trace.s3.bucket=tempo-traces-prod \
  --set storage.trace.s3.region=eu-west-1
```

Grafana datasource configured to Tempo with trace-to-logs correlation (click a span → see its logs in Loki).

## OpenTelemetry Collector — the common gateway

One OTEL Collector per cluster (Deployment) plus optional DaemonSet for host metrics. Apps export OTLP; Collector fan-outs to backends.

```yaml
apiVersion: opentelemetry.io/v1beta1
kind: OpenTelemetryCollector
metadata: { name: otel, namespace: monitoring }
spec:
  mode: deployment
  replicas: 2
  config:
    receivers:
      otlp:
        protocols:
          grpc: { endpoint: 0.0.0.0:4317 }
          http: { endpoint: 0.0.0.0:4318 }
    processors:
      batch: { timeout: 10s, send_batch_size: 8192 }
      memory_limiter: { limit_mib: 1500, check_interval: 2s }
      k8sattributes: {}                  # auto-enrich with pod/namespace labels
      resource:
        attributes:
          - { key: deployment.environment, value: production, action: upsert }
    exporters:
      otlphttp/tempo:  { endpoint: http://tempo-distributor:4318 }
      loki:            { endpoint: http://loki-gateway/loki/api/v1/push }
      prometheusremotewrite:
        endpoint: http://kps-prometheus:9090/api/v1/write
    service:
      pipelines:
        traces:  { receivers: [otlp], processors: [memory_limiter, k8sattributes, batch], exporters: [otlphttp/tempo] }
        metrics: { receivers: [otlp], processors: [memory_limiter, k8sattributes, batch], exporters: [prometheusremotewrite] }
        logs:    { receivers: [otlp], processors: [memory_limiter, k8sattributes, batch], exporters: [loki] }
```

## Alertmanager routing

```yaml
route:
  receiver: default
  group_by: [alertname, severity, cluster]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - matchers: [severity="page"]
      receiver: pagerduty
      continue: true
    - matchers: [severity="ticket"]
      receiver: jira
    - matchers: [severity="info"]
      receiver: slack-noise
receivers:
  - name: pagerduty
    pagerduty_configs:
      - routing_key_file: /etc/alertmanager/pd/key
        severity: '{{ .GroupLabels.severity }}'
  - name: slack-noise
    slack_configs:
      - api_url_file: /etc/alertmanager/slack/url
        channel: "#alerts-noise"
```

Routing rules:
- Pages go to on-call rotation; tickets go to backlog; noise goes to a channel nobody is required to read.
- Use `group_by` to collapse storms.
- `inhibit_rules` to suppress downstream alerts when an upstream failure is already paging.

## Dashboards — what to put on the wall

Per cluster:
- Cluster overview: node CPU/mem, Pod restarts, pending Pods, API server latency.
- Namespace overview: CPU/mem by workload, restarts, OOMKills in last 24h.

Per service:
- RED (rate, errors, duration) at p50/p95/p99.
- Resource saturation (CPU throttling, memory vs limit).
- Dependencies (DB query rate/latency, cache hit rate, queue depth).
- Error budget burn-down if SLOs are defined.

## Long-term storage

Prometheus local is 2–3 weeks. Ship to:
- **Grafana Mimir** — horizontally scalable, S3-backed.
- **Thanos** — sidecar + object storage, long-established.
- **Cortex** — similar to Mimir, Mimir is now the active fork.
- **VictoriaMetrics** — different code base, excellent compression.

## Review checklist

- [ ] `kube-prometheus-stack` installed with persistent storage
- [ ] `ServiceMonitor` / `PodMonitor` for every workload exposing metrics
- [ ] RED metrics (rate, errors, duration) per service
- [ ] Alerts have runbook annotations
- [ ] Alertmanager routes by severity with inhibit rules
- [ ] Loki installed with object storage and low-cardinality labels
- [ ] OTEL Collector receives OTLP; apps use OTLP SDK
- [ ] Tempo configured with trace-to-logs correlation
- [ ] Long-term metric storage (Mimir/Thanos/VictoriaMetrics)
- [ ] Grafana dashboards cover cluster, namespace, and per-service views
- [ ] SLOs defined for tier-1 services with error-budget burn alerts
