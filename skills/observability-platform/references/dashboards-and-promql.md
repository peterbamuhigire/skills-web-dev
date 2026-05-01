# Production Dashboards and PromQL Cookbook

Companion to `SKILL.md`. Four dashboards every SaaS needs — Service Health (RED per service), Infrastructure (host CPU/memory/disk/network), Business KPIs (MRR, active users, signups, churn), SLO Tracker (current SLO % vs target, budget remaining per service). Pin all four to the on-call TV. During an incident, responders should not hunt dashboards — they should read them.

## Service Health

```promql
sum(rate(http_requests_total[5m])) by (service)
sum(rate(http_requests_total{status=~"5.."}[5m])) by (service) / sum(rate(http_requests_total[5m])) by (service)
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service))
```

## Infrastructure

```promql
1 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) by (instance)
node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes
(node_filesystem_size_bytes - node_filesystem_avail_bytes) / node_filesystem_size_bytes
```

## Business KPIs

```promql
sum(business_mrr_usd)
sum(increase(business_signups_total[1d]))
sum(active_users_gauge{window="24h"})
sum(increase(business_churn_total[30d])) / sum(business_customers_gauge offset 30d)
```

## SLO Tracker — availability % and budget remaining (99.9% SLO over 28d)

```promql
sum(rate(http_requests_total{status!~"5.."}[28d])) by (service)
  / sum(rate(http_requests_total[28d])) by (service)
1 - (sum(rate(http_requests_total{status=~"5.."}[28d])) by (service)
     / sum(rate(http_requests_total[28d])) by (service)) / 0.001
```

## Recording-rule pattern

Pre-aggregate expensive expressions so dashboards and alerts read cheap series:

```yaml
groups:
- name: api-precompute
  interval: 30s
  rules:
  - record: job:http_request_duration_seconds:p95_5m
    expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service))
  - record: job:http_requests:error_ratio_5m
    expr: |
      sum(rate(http_requests_total{status=~"5.."}[5m])) by (service)
      / sum(rate(http_requests_total[5m])) by (service)
```
