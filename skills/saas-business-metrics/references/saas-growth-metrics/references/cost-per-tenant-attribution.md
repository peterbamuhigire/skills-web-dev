# Cost-Per-Tenant Attribution — Reference

You cannot compute gross margin, identify whales, or price intelligently without **cost per tenant per month**. This is a hard requirement from day one in any SaaS the engine ships.

## Two Worlds

### Silo (easy)
The cloud provider already tags each silo's resources. Use:
- AWS Cost Allocation Tags (`tenant_id` on every resource).
- GCP Labels.
- Azure Tags.
- Cloud cost management tools (CloudHealth, Vantage, Kubecost, Infracost).

Daily / monthly cost falls out of the cloud bill grouped by `tenant_id` tag.

### Pool (harder — apportionment)
Shared compute, shared DB, shared storage. You need to **apportion** shared spend across tenants by usage signal.

## Apportionment Algorithm

For each shared resource, pick a usage signal that proxies that resource's consumption:

| Resource | Usage signal | Apportion by |
|---|---|---|
| Shared API compute (ECS / K8s) | Request count + duration | `tenant_request_seconds / total_request_seconds` |
| Shared DB (RDS) | Query time + storage bytes | `tenant_query_seconds / total_query_seconds` + `tenant_storage_bytes / total_storage_bytes` weighted |
| Shared object storage | Storage bytes + egress bytes | Per-tenant prefix → cloud bill columns |
| Async workers | Job count + job duration | `tenant_job_seconds / total_job_seconds` |
| AI / LLM | Token count | Already metered per tenant (see `ai-saas-billing`) |
| Egress bandwidth | Bytes per tenant | Per-tenant outbound log |

Sum per tenant: `cost_per_tenant_monthly = sum(apportioned_cost_per_resource)`.

## Instrumentation

Emit a `usage` event per request / per job with:
```json
{
  "tenant_id": "ten_456",
  "resource": "api",                  // or 'db', 'worker', 'ai'
  "duration_ms": 423,
  "storage_bytes_used": 1048576,
  "tokens": 1240,
  "egress_bytes": 234567,
  "occurred_at": "..."
}
```

Aggregate nightly into `tenant_resource_usage_daily`.

Join with the cloud bill (downloaded daily via CUR / Billing Export):
```sql
WITH cloud_costs AS (
  SELECT service, day, cost_usd
  FROM cloud_billing_export
  WHERE day = TARGET_DAY
),
tenant_signals AS (
  SELECT tenant_id, resource, SUM(duration_ms) AS dur, SUM(storage_bytes_used) AS sb, SUM(tokens) AS tok
  FROM tenant_resource_usage_daily
  WHERE day = TARGET_DAY
  GROUP BY tenant_id, resource
),
total_signals AS (
  SELECT resource, SUM(dur) AS dur_total, SUM(sb) AS sb_total, SUM(tok) AS tok_total
  FROM tenant_signals
  GROUP BY resource
)
SELECT
  ts.tenant_id,
  SUM(
    cc.cost_usd * (
      CASE ts.resource
        WHEN 'api' THEN ts.dur / NULLIF(t.dur_total, 0)
        WHEN 'db' THEN (ts.dur / NULLIF(t.dur_total, 0)) * 0.6 + (ts.sb / NULLIF(t.sb_total, 0)) * 0.4
        ELSE ts.dur / NULLIF(t.dur_total, 0)
      END
    )
  ) AS cost_per_tenant_usd
FROM tenant_signals ts
JOIN total_signals t ON ts.resource = t.resource
JOIN cloud_costs cc ON cc.service = mapping(ts.resource)
GROUP BY ts.tenant_id;
```

## Mixed-Mode

For mixed-mode SaaS, sum silo costs (from cloud tags) and pool apportionment per tenant.

## Output Dashboards

- `cost_per_tenant_monthly_usd` per tenant.
- `gross_margin_per_tenant = (mrr - cost_per_tenant) / mrr`.
- Margin distribution: percentile (p10 / p50 / p90).
- Negative-margin tenants flagged (whales-as-loss-leaders, abuse, mispriced plans).
- Top 10% cost contributors vs top 10% MRR contributors — Pareto check.

## Anti-Patterns

- Allocating shared cost evenly by tenant count — distorts everything; a 1-user tenant pays the same as a 1000-user tenant.
- Not instrumenting per-tenant usage signals — apportionment is impossible.
- Including engineering salaries in COGS — they're OPEX. COGS is **infrastructure + per-customer-variable** (hosting, third-party APIs called for that customer, support tools per seat).
- Recomputing apportionment every report instead of materialising — slow + inconsistent.

## See Also

- `saas-metrics-event-contract.md` — the MRR side; cost joins to this for margin.
- `multi-tenant-saas-architecture` — tenant context that drives all the usage signals.
- `kubernetes-saas-delivery` — K8s-specific cost allocation (Kubecost).
