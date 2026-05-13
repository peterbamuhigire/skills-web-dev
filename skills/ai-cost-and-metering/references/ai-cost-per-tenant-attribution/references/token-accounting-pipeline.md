# Token Accounting Pipeline — Reference

Cross-reference: a deeper implementation copy lives in `ai-model-gateway/references/token-accounting-pipeline.md`. This file frames the pipeline from the **attribution** point of view (what each stage gives you to attribute by).

## Attribution dimensions

Every `ai_requests` row supports attribution along these dimensions:

| Dimension | Source | Used for |
|---|---|---|
| tenant_id | gateway request | per-tenant cost, COGS% |
| feature | gateway request | feature-level unit economics |
| prompt_id + version | prompt registry | regression / pricing impact of prompt changes |
| model_used | provider response | model-mix analysis |
| region | binding | residency cost variance |
| fallback_used | gateway pipeline | reliability cost |
| user_id | gateway request | per-seat cost, abuser detection |
| intent | feature code | cost per business outcome (e.g., per resolved ticket) |
| billing_dimension | feature code | maps to invoiced unit (`ai-usage-metering-and-billing`) |

Choose dimensions before you ship. Adding a new dimension later requires a backfill from the audit log.

## Materialisations

```
ai_requests (Postgres)      ← canonical, retain 90d hot then archive
   │
   ├── tenant_ai_daily      ← per-tenant per-day per-feature per-model
   ├── feature_daily        ← all-tenant per-feature
   ├── model_daily          ← all-tenant per-model
   └── prompt_version_daily ← per-prompt regression analysis
```

All views are idempotent on their key. All views are rebuildable from `ai_requests`.

## Backfill recipe

When you add a dimension (say, `intent`):

1. Ensure feature code now writes `intent` into gateway requests.
2. For historical rows where `intent` is null, run a one-shot job that hydrates `intent` from request payload S3 (if recorded) or marks `intent='__legacy__'`.
3. Rebuild `tenant_ai_daily` including the new dimension.
4. Update dashboards.

## Drift sources to watch

- **System prompts** the provider injects (some models bill them; some don't). Verify on a fixed test request monthly.
- **Tool-use tokens** charged differently — function call envelopes count toward input/output but the count rules vary.
- **Streaming** — some providers report tokens only at end; some include partial counts.
- **Retries** — provider may charge a partial output on a retried completion. Audit must record retry attempts as their own rows.

## Anti-pattern: aggregated counters only

Storing only Redis aggregates makes drilldown impossible and erasure impossible (you can't delete a specific tenant's row from a hash). Always keep `ai_requests` as the canonical row.
