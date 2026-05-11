---
name: ai-model-gateway
description: Use when designing or building the LLM gateway — the single outbound surface from the SaaS to all LLM providers. Covers provider abstraction, model selection per tenant tier, fallback chains, retries, per-tenant rate limiting and token caps, request signing, audit logging, regional routing for data residency, cost capture at write time, kill-switch enforcement, and the SDK/HTTP contract feature teams consume.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Model Gateway
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Designing or implementing the LLM gateway as a control-plane service for a multi-tenant SaaS.
- Replacing direct OpenAI / Anthropic / Bedrock SDK calls in feature code with a routed, audited, cost-attributed path.
- Adding multi-provider fallback to an existing AI feature (Anthropic → Bedrock → OpenAI).
- Enforcing per-tenant token caps, regional routing, and audit at one chokepoint instead of scattered library calls.

## Do Not Use When

- The task is the wider AI architecture — start with `ai-on-saas-architecture`.
- The task is direct provider API exploration / spike — `ai-llm-integration` is the bare-metal SDK skill.
- The task is the prompt design — use `ai-prompt-engineering`.

## Required Inputs

- The model tier catalogue (Free → distilled; Pro → mid-tier; Enterprise → flagship).
- The provider list, their SLAs, their regions, and contract limits.
- The `tenant_ai_binding` schema from `ai-on-saas-architecture`.
- Cost ceiling policy per plan (hard caps vs soft caps).
- Residency commitments per tenant region.

## Workflow

1. Read this `SKILL.md`.
2. Define the **internal gateway contract** (§1) — HTTP + SDK shape, request envelope, response envelope.
3. Implement the **request pipeline** (§2): auth → model resolve → rate limit → safety in → provider call → safety out → cost capture → audit → respond.
4. Build the **provider adapter layer** (§3) so adding a provider is a < 200-LOC change.
5. Add **fallback chains** (§4) per tier.
6. Add **per-tenant token/USD ceilings** (§5).
7. Add **regional routing** (§6) for residency.
8. Wire **audit + cost capture** (§7) at write time.
9. Implement the **kill-switch path** (§8).
10. Document **SLA and ops** (§9).
11. Apply anti-patterns (§10).

## Quality Standards

- Adding a new feature requires **zero** code in the gateway beyond a prompt-id registration.
- Adding a new provider requires < 200 LOC and zero feature-code changes.
- Hot-path overhead added by the gateway < 50ms p95 over raw provider call.
- 100% of AI requests are audited and cost-attributed at request close — never reconciled from invoices.
- Kill-switch flip propagates in < 60 seconds.
- Gateway is the **only** outbound path; a lint rule rejects PRs that import provider SDKs outside the gateway repo.

## Anti-Patterns

- Gateway with feature-specific code paths inside it (gateway becomes a god service).
- No fallback chain — primary provider 429 brings the whole product down.
- Cost computed nightly from logs instead of at request close — tenants get billed days late.
- Rate limit only at the provider layer — one tenant exhausts the global key and noises everyone.
- Audit log writes are best-effort (lost on crash) — compliance and billing diverge.
- Hard caps without a degraded-mode option — tenants hit the cap and the whole product breaks.
- Gateway leaks provider-specific error shapes to feature code — re-coupling.

## Outputs

- Gateway HTTP contract + SDK in N languages used by feature teams.
- Provider adapter set with capability matrix.
- Fallback policy per tier.
- Token / USD ceiling policy per plan.
- Region routing table.
- Audit log + cost ledger schema (lives in audit skill).
- Kill-switch UX + back-office wiring (`saas-admin-backoffice-tooling`).

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Architecture | Gateway contract | OpenAPI doc | `docs/ai/gateway-api.yaml` |
| Architecture | Provider capability matrix | Markdown table | `docs/ai/provider-matrix.md` |
| Release evidence | Fallback policy per tier | Markdown doc | `docs/ai/fallback-policy.md` |
| Operability | Gateway SLO + on-call runbook | Markdown runbook | `docs/runbooks/llm-gateway.md` |

## References

- `references/llm-gateway-design.md` — full design (canonical copy lives in `ai-on-saas-architecture/references/`).
- `references/token-accounting-pipeline.md` — how token-in / token-out / cost rolls up.
- Companion: `ai-on-saas-architecture`, `ai-cost-per-tenant-attribution`, `ai-usage-metering-and-billing`, `ai-entitlements-and-feature-gating`, `ai-prompt-injection-and-tenant-safety`, `ai-observability-and-debugging`, `saas-rate-limiting-and-quotas`.
- Incident primitives: the gateway is the surface that exposes the **operator primitives** an on-call uses during an incident — kill-switch (feature/agent task), model-pin, prompt-pin, gateway routing pin, per-tenant feature pause, quota cap. Each primitive must propagate in < 60s, log to `ai_incident_mitigation_log` with `(actor, ts, primitive, scope, reason, ticket_id)`, and be invocable from a back-office UI **without writing code or SQL**. See `ai-incident-response-runbook` §3 for the full primitive contract and `ai-incident-recovery-and-rollback/references/rollback-patterns.md` for the un-pin contract.

<!-- dual-compat-end -->

## §1 Internal Gateway Contract

A single endpoint that feature teams call:

```
POST /v1/generate
Authorization: Bearer <service-jwt>     # signed by internal auth
X-Tenant-Id: 8421                       # required
X-Feature-Id: support-copilot.answer    # namespaced
X-Trace-Id: trc_01HXY...                # propagate

{
  "prompt_id": "support.answer",
  "prompt_version": "latest",          // or pinned e.g. "v17"
  "variables": { "user_question": "...", "kb_partition_id": "kb_t8421" },
  "retrieval": {                       // optional; gateway can call KB service
    "do_retrieve": true,
    "top_k": 6
  },
  "intent": "answer_question",
  "user_id": 990012,
  "max_tokens_out": 800,
  "temperature": 0.2,
  "stream": false
}
```

Response:

```json
{
  "request_id": "ai_req_01HXY...",
  "model_used": "claude-3.7-sonnet",
  "region": "eu-west-1",
  "text": "...",
  "tokens_in": 1840,
  "tokens_out": 412,
  "usd_cost": 0.013824,
  "latency_ms": 1923,
  "fallback_used": false,
  "safety_findings": [],
  "grounding_score": 0.91,
  "citations": [{"chunk_id": "...", "source": "...", "score": 0.83}],
  "eval_sampled": false
}
```

A streaming variant uses Server-Sent Events. The final SSE event carries the full envelope (cost, latency, model, audit id).

## §2 Request Pipeline

```
1. Authn (service JWT)        — verify signature; resolve calling service
2. Authz (tenant + feature)   — service is allowed to act for this tenant on this feature
3. Resolve binding            — read tenant_ai_binding for tenant
4. Entitlement check          — tenant's plan permits this feature/model
5. Kill-switch check          — ai_enabled = false → 403 fast
6. Rate limit                 — Redis token bucket per tenant per feature
7. Cap check                  — monthly USD/token cap not exceeded
8. Resolve prompt             — prompt registry returns (template, model_hint)
9. Render prompt              — template + variables (sanitised)
10. Safety in                 — prompt-injection classifier on user-supplied variables
11. (optional) Retrieval      — call KB service with tenant_id (no other path)
12. Provider call             — primary; retry once on transient
13. Safety out                — PII scrub, jailbreak detect, grounding check
14. Cost compute              — tokens × price table → usd_cost
15. Audit write               — synchronous; row in ai_requests
16. Cost event                — ai.cost.recorded onto event bus
17. Eval sample               — N% of requests written to eval queue
18. Respond                   — envelope to caller
```

The pipeline is the gateway. Each stage has a hard timeout; stage failures emit `gateway.stage.failed` traces.

## §3 Provider Adapter Layer

```python
class Provider(Protocol):
    name: str
    models: list[ModelDescriptor]
    regions: list[str]

    async def generate(self, req: NormalizedRequest) -> NormalizedResponse: ...

class AnthropicProvider:
    name = "anthropic"
    models = [
        ModelDescriptor("claude-3.7-sonnet", ctx=200_000,
                        in_price=3e-6, out_price=15e-6),
        ModelDescriptor("claude-3-haiku", ctx=200_000,
                        in_price=0.25e-6, out_price=1.25e-6),
    ]
    regions = ["us-east-1", "eu-west-1"]

    async def generate(self, req): ...
```

Adapter responsibilities:
- Translate normalised request → provider SDK call.
- Translate provider response/error → normalised response/error.
- Surface model capability flags (vision, tools, JSON-mode, streaming).
- Report region routing options.

Anything else (rate limit, retries with backoff, cost compute, audit) lives in the **pipeline**, not the adapter.

## §4 Fallback Chains

Per tier, an ordered list of (provider, model, region) candidates.

```yaml
tiers:
  enterprise:
    primary:     [anthropic, claude-3.7-sonnet, region:tenant]
    fallback_1:  [bedrock,   anthropic.claude-3-5-sonnet, region:tenant]
    fallback_2:  [openai,    gpt-4o, region:tenant_or_us]
  pro:
    primary:     [anthropic, claude-3.7-sonnet, region:tenant]
    fallback_1:  [anthropic, claude-3-5-haiku, region:tenant]
  free:
    primary:     [anthropic, claude-3-haiku, region:any]
    fallback_1:  [openai,    gpt-4o-mini, region:any]
```

Triggering fallback:
- 5xx, timeout, or `RateLimitError` after one retry on primary.
- 429 with `Retry-After > slo_budget`.
- Model deprecation event.
- A **safety vote** from the in-line classifier (rare).

Record `fallback_used=true` in the audit row; alert when fallback ratio for a tier exceeds threshold.

## §5 Per-Tenant Token / USD Ceilings

The gateway enforces caps at the *atomic* check-and-increment level using Redis (`saas-rate-limiting-and-quotas` algorithms). Three ceilings:

- **Hard USD cap** per month (`tenant_ai_binding.monthly_usd_cap`). On hit: 429 + `quota:ai_usd`. Upgrade path link in response.
- **Hard token cap** per day (rate-shaped). On hit: 429 + `quota:ai_tokens_day`.
- **Soft cap** at 80% — fires `ai.budget.threshold` event for in-product banner and sales-assist email; no enforcement.

For enterprise tenants on a true-up model, replace the hard cap with a *paging* threshold instead.

## §6 Regional Routing

`tenant_ai_binding.region` drives:
- The provider region called (must match for residency).
- The region of the KB partition called.
- The S3 bucket of the audit payload.

When a region's preferred model is unavailable, the gateway consults a region policy:
- `strict`: 503 if the region cannot serve. Used for sovereignty.
- `degraded`: allow cross-region with a `region_breach=true` flag in audit; emit alert.
- `permissive`: allow cross-region silently (default for low-sensitivity tenants).

## §7 Audit + Cost Capture

Synchronous, in-pipeline, atomic with the response. The gateway returns ONLY after the `ai_requests` row is committed and the `ai.cost.recorded` event has been published (or rolled back).

Two writes:
1. Postgres `ai_requests` row (the legal/compliance record).
2. Redis tenant cost counter increment (the realtime billing view).

A reconciliation job nightly compares Postgres rollups vs Redis to detect drift.

See `references/token-accounting-pipeline.md`.

## §8 Kill-Switch Path

The gateway reads `tenant_ai_binding.ai_enabled` from a Redis-cached binding (TTL 30s; invalidated by `ai.kill_switched` event).

On `ai_enabled = false`:
```json
{
  "error": {
    "code": "AI_DISABLED",
    "message": "AI features are disabled for this tenant. Contact support.",
    "kill_switch_reason": "tenant requested temporary disable"
  }
}
```

The back-office UI (`saas-admin-backoffice-tooling`) exposes the toggle plus a feature-scoped variant (`tenant_ai_feature_disable` table).

## §9 SLA & Ops

| Metric | Target |
|---|---|
| Gateway availability | 99.95% |
| Hot-path overhead | < 50ms p95 |
| Audit-write success | 100% (any failure = reject request) |
| Time to roll a new provider | < 1 week from contract to traffic |
| Time to flip kill-switch | < 60 seconds |
| Fallback ratio (enterprise tier) | < 1% sustained |

Dashboards: gateway QPS, p50/p95/p99 latency by stage, error rate by stage, fallback ratio by tier, cost burn by tenant top-20.

## §10 Anti-Patterns

- Building per-feature gateway routes — turns the gateway into a feature factory.
- Streaming responses that don't emit a final envelope event — cost + audit lost on disconnect.
- Async audit writes via best-effort queue — failures cause compliance and billing drift.
- Rate limiting only at the provider — noisy tenants block others.
- Logging full prompts and responses unfiltered — PII exposure; encrypt audit payloads at rest.
- One provider, one model — first outage = total outage.
- Adapter logic leaking into the pipeline (provider-specific `if anthropic: ...` branches).

## §11 Read Next

- `ai-on-saas-architecture` — broader context.
- `ai-cost-per-tenant-attribution` — what the gateway feeds.
- `ai-usage-metering-and-billing` — how the ledger turns into invoices.
- `ai-prompt-injection-and-tenant-safety` — the safety-in/safety-out logic the pipeline runs.
- `ai-observability-and-debugging` — traces, replays, debugging.
- `saas-rate-limiting-and-quotas` — algorithms the gateway uses.
