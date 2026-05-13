# LLM Gateway Design — Reference

The LLM gateway is the single outbound surface from the SaaS to every LLM provider. It is a control-plane service: separate deployment, separate on-call rotation, stricter SLA than the feature code that consumes it. This reference complements `ai-model-gateway/SKILL.md` from the architecture point of view.

## Responsibilities

1. **Provider abstraction.** One internal contract; many backend providers (Anthropic, OpenAI, Google, Bedrock, self-hosted vLLM/TGI). Feature code never imports a provider SDK.
2. **Model selection.** Resolves `tenant → tier → primary/fallback model` from `tenant_ai_binding`.
3. **Regional routing.** Pin model + region per tenant when residency matters (EU tenants on EU endpoints).
4. **Rate limiting.** Per-tenant tokens/min and requests/min before provider rate limits are exhausted.
5. **Retries + fallback chain.** Transient failure → retry primary; persistent → fallback model; total failure → cached/degraded response.
6. **Cost capture.** Token counts × price table → `ai.cost.recorded` event written before the response is returned.
7. **Audit log.** Every prompt, response, model, retrieval ids, cost.
8. **Safety hooks.** Input scan (prompt injection), output scan (PII, jailbreak), guardrail findings attached to response.
9. **Eval sampling.** N% of requests written to eval queue for offline scoring.
10. **Kill-switch enforcement.** Reads `tenant_ai_binding.ai_enabled`; denies fast.

## Topology

```
Feature code ──HTTP/gRPC──> LLM Gateway ──HTTPS──> Provider APIs
                                │
                                ├──> Redis (rate limit, dedup)
                                ├──> Postgres (audit, cost ledger, prompt registry)
                                ├──> Event bus (ai.* events)
                                └──> Trace exporter (OTel)
```

Two deployment modes:

- **Sidecar SDK + central gateway**: SDK in each service handles retries/tracing; calls the central gateway. Central gateway handles rate limit, audit, cost, model resolution. Recommended.
- **Pure central proxy**: feature code calls gateway HTTP only. Simpler ops, slightly higher latency.

## Hot/cold separation

- **Hot path** (per request): rate-limit check, model resolution, provider call, cost compute, audit write. Must be < 50ms overhead.
- **Cold path** (background): eval sampling write, cost aggregation, anomaly detection, drift alerts.

## Failure modes

| Failure | Behaviour |
|---|---|
| Primary model 429 | Retry with backoff once; then fallback model |
| Primary model 5xx | Fallback model immediately |
| All providers down | Return `503 ai_unavailable`; emit `ai.provider.outage` |
| Tenant token cap exceeded | `429 ai_token_cap` with upgrade URL |
| Tenant kill-switched | `403 ai_disabled` |
| Region unavailable | Fall back to nearest allowed region per tenant policy |

## What does NOT belong in the gateway

- Business logic of the AI feature (that's the application plane).
- Prompt content (live in prompt registry, referenced by id).
- Retrieval (KB service handles it; gateway sees retrieved chunks as input only).
- UI / citation rendering (`ai-output-design`).

## v1 minimum

- One model per tier hard-coded; no fallback yet.
- Per-tenant token bucket in Redis.
- Audit log to Postgres.
- Cost compute from a checked-in price table.
- Kill-switch read from `tenant_ai_binding`.

Everything else is v2/v3.
