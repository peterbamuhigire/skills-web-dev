---
name: ai-on-saas-architecture
description: Use when building AI features (RAG, agents, copilots, LLM analytics, autocomplete, summarisation, classification, AI search) inside a multi-tenant SaaS — the unifying architecture skill that binds control-plane services (LLM gateway, prompt registry, knowledge-base service, eval harness, AI audit log) to application-plane features, with per-tenant model/prompt/KB/eval bindings. Distinct from `ai-app-architecture` (single-tenant architecture style) and `multi-tenant-saas-architecture` (transactional-data isolation).
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI on Multi-Tenant SaaS — Unifying Architecture
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Designing AI features for a multi-tenant SaaS product where every request must be tenant-scoped, cost-attributed, observable, gated, safe, and evaluated.
- Auditing an existing SaaS where AI features were added but ignored multi-tenancy — shared prompts, shared vector index, shared model selection, no per-tenant cost — and need to be hardened before enterprise rollout.
- Splitting AI responsibilities cleanly: which services belong in the **control plane** (LLM gateway, prompt registry, KB service, eval harness, AI audit log) and which in the **application plane** (the feature itself).
- Onboarding a new AI feature: deciding per-tenant binding contracts (model? prompt version? KB partition? eval dataset?) before code is written.

## Do Not Use When

- The task is a single AI feature's prompt design — use `ai-feature-spec` and `ai-prompt-engineering`.
- The task is the LLM client wrapper itself — use `ai-llm-integration` for direct provider calls; use `ai-model-gateway` for the multi-tenant routing service.
- The task is transactional-data tenant isolation — use `multi-tenant-saas-architecture`.
- The task is general AI architecture for a single-tenant app — use `ai-app-architecture`.

## Required Inputs

- Tenancy and deployment model from `multi-tenant-saas-architecture` and `saas-deployment-models`.
- Plan / tier catalogue from `subscription-billing` and `saas-entitlements-and-plan-gating`.
- The list of AI features in scope and the data each touches.
- Data residency requirements per tenant (region, sovereignty).
- Target SLA for AI responses (latency, availability, quality).

## Workflow

1. Read this `SKILL.md` end-to-end before any architecture decision.
2. Apply the **AI two-halves model** (§1): split AI services into control plane vs application plane.
3. Inventory the **six AI control-plane services** (§2): LLM gateway, prompt registry, knowledge-base service, eval harness, AI audit log, agent runtime. Mark each `v1 / v2 / v3 / not-needed`.
4. Define the **per-tenant AI binding** (§3): `tenant_ai_binding` table — model tier, prompt version pin, KB partition id, eval dataset id, region.
5. Define the **AI request envelope** (§4): the tenant-tagged, cost-attributed, traceable shape every AI request takes inside the SaaS.
6. Wire the **AI lifecycle events** (§5): `ai.request.started`, `ai.request.completed`, `ai.cost.recorded`, `ai.eval.failed`, `ai.injection.detected`, `ai.kill_switched`.
7. Apply the **decision matrix** (§6): silo vs pool for vector stores, fine-tunes, prompts, eval data.
8. Apply the **anti-pattern checklist** (§8).
9. Hand off to specialist skills: `ai-model-gateway`, `ai-tenant-isolation-patterns`, `ai-rag-multi-tenant`, `ai-eval-harness`, `ai-cost-per-tenant-attribution`, `ai-prompt-injection-and-tenant-safety`, `ai-observability-and-debugging`.

## Quality Standards

- Every AI request carries the **tenant context** end-to-end: tenant id, plan tier, region, request id, parent trace id. No code path strips it.
- AI control-plane services are **separate deployments** from application-plane features, with their own release cadence and on-call rotation.
- Every AI request is **cost-attributable to one tenant** at write time — never reconciled retroactively from provider invoices.
- Every AI request is **observable as a trace** that spans retrieval, generation, post-processing, and audit.
- Every AI feature has a **per-tenant kill switch** the back-office console can flip in < 1 minute.
- The LLM gateway is the **only** outbound surface to LLM providers. Direct SDK calls from feature code are an architecture violation.

## Anti-Patterns

- Application-plane code calling OpenAI / Anthropic / Gemini SDKs directly. Fix: route through `ai-model-gateway`.
- Single shared vector index for all tenants with no `tenant_id` filter or cryptographic partitioning. Fix: `ai-tenant-isolation-patterns`.
- Per-tenant cost reconciled from provider invoices monthly. Fix: real-time token accounting via gateway (see `ai-cost-per-tenant-attribution`).
- No prompt versioning, prompts hard-coded in feature code. Fix: prompt registry control-plane service.
- "It works for our flagship tenant" — no eval harness, no goldens per tenant, no regression gate. Fix: `ai-eval-harness`.
- Hallucination rate is unknown / unmeasured. Fix: `ai-hallucination-slo-and-grounding`.
- No per-tenant rate limits on AI; one tenant exhausts provider rate limits for everyone. Fix: `saas-rate-limiting-and-quotas` AI quotas section + gateway enforcement.

## Outputs

- AI control-plane service inventory mapped to v1/v2/v3.
- `tenant_ai_binding` schema and seeding rules.
- AI request envelope spec (HTTP / event / trace schema).
- AI lifecycle event taxonomy.
- Silo-vs-pool decision per AI asset class (vector store, fine-tune, prompt, eval data).
- Per-tenant AI kill-switch design and back-office UX hand-off.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Architecture | AI control-plane service inventory | Markdown doc with v1/v2/v3 columns | `docs/ai/ai-control-plane-services.md` |
| Architecture | `tenant_ai_binding` schema | SQL DDL + readme | `docs/ai/tenant-ai-binding.md` |
| Architecture | AI request envelope spec | OpenAPI fragment + trace schema | `docs/ai/ai-request-envelope.md` |
| Operability | Per-tenant kill-switch design | Markdown + admin-console wireframe | `docs/ai/ai-kill-switch.md` |

## References

- `references/llm-gateway-design.md` — full design of the LLM gateway as a control-plane service.
- `references/control-plane-ai-services.md` — the five AI control-plane services in detail.
- Companion: `ai-model-gateway`, `ai-tenant-isolation-patterns`, `ai-rag-multi-tenant`, `ai-eval-harness`, `ai-cost-per-tenant-attribution`, `ai-usage-metering-and-billing`, `ai-entitlements-and-feature-gating`, `ai-hallucination-slo-and-grounding`, `ai-prompt-injection-and-tenant-safety`, `ai-feature-rollout-and-experimentation`, `ai-observability-and-debugging`, `ai-agent-runtime-architecture`, `ai-agent-tool-catalogue-and-action-gating`, `ai-agent-cost-and-step-budgets`, `ai-agent-observability-and-replay`, `ai-agent-safety-and-red-team`, `saas-control-plane-engineering`, `multi-tenant-saas-architecture`.

<!-- dual-compat-end -->

## §1 The AI Two-Halves Model

Golding's control-plane / application-plane split applies one level deeper for AI:

- **AI application plane** — the feature code: a copilot panel, a RAG endpoint, an autocomplete worker, a classification job. Owned by the feature team. Calls into the AI control plane through stable contracts.
- **AI control plane** — the cross-cutting services every AI feature consumes: the LLM gateway, the prompt registry, the knowledge-base service, the eval harness, the AI audit log. Owned by the platform / AI infra team. Releases independently. Has stricter SLA.

Skipping the AI control plane regresses to **AI sprawl**: every feature picks its own model, hard-codes its own prompts, builds its own retrieval, audits nothing. The first enterprise prospect's security questionnaire kills the deal.

## §2 The Six AI Control-Plane Services

| # | Service | Owns | Minimum v1 surface |
|---|---|---|---|
| 1 | **LLM Gateway** | provider abstraction, model selection, fallback, retries, rate limit, request signing, audit, cost capture | HTTP service + SDK; see `ai-model-gateway` |
| 2 | **Prompt Registry** | versioned prompts, per-tenant pinning, A/B variants, rollback | CRUD API + storage; see §3 + `ai-prompt-engineering` |
| 3 | **Knowledge-Base Service** | per-tenant ingestion, chunking, embedding, vector storage, retrieval | API + ingestion workers; see `ai-rag-multi-tenant` |
| 4 | **Eval Harness** | golden datasets, prompt regression, judge runs, CI gate, drift detection | Service + CLI + CI integration; see `ai-eval-harness` |
| 5 | **AI Audit Log** | every prompt, model, retrieval, output, cost, decision, denial | Append-only ledger; see §5 + `ai-observability-and-debugging` |
| 6 | **Agent Runtime** | agent loop state machine, durable execution, per-task budgets, tool registry, approval workflow, replay | Workflow engine + tool registry; see `ai-agent-runtime-architecture`, `ai-agent-tool-catalogue-and-action-gating`, `ai-agent-cost-and-step-budgets` |

`v1` for an early-stage SaaS adding AI: services 1, 2, 5 minimum. Add 3 when launching RAG. Add 4 before the first enterprise eval. Add 6 when the first agentic feature ships.

The **Agent Runtime** deserves status as its own control-plane service for the same reasons as the LLM Gateway: it owns cross-cutting concerns (budgets, idempotency, kill-switches, durable execution, audit) that every agentic feature otherwise re-implements badly. Treating "agent code" as feature-plane code produces the same sprawl the gateway prevents at the provider boundary.

## §3 Per-Tenant AI Binding

The single table that ties every AI decision back to a tenant:

```sql
CREATE TABLE tenant_ai_binding (
    tenant_id              BIGINT UNSIGNED PRIMARY KEY,
    model_tier             VARCHAR(32) NOT NULL,        -- 'free', 'pro', 'enterprise', 'custom'
    primary_model           VARCHAR(64) NOT NULL,        -- e.g. 'claude-3.7-sonnet'
    fallback_model          VARCHAR(64),                 -- e.g. 'claude-3-haiku'
    region                  VARCHAR(32) NOT NULL,        -- 'us-east-1', 'eu-west-1', etc.
    kb_partition_id         VARCHAR(64),                 -- vector store partition
    prompt_pack_version     VARCHAR(32),                 -- pinned prompt registry version
    eval_dataset_id         VARCHAR(64),                 -- pinned golden dataset
    monthly_token_cap       BIGINT,                      -- hard cap; gateway enforces
    monthly_usd_cap         DECIMAL(10,2),               -- hard cap; gateway enforces
    ai_enabled              BOOLEAN NOT NULL DEFAULT TRUE,
    kill_switch_reason      VARCHAR(255),
    last_updated_at         DATETIME NOT NULL,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);
```

Every gateway request resolves this row. Every billing event references this row. Every eval run reads this row. Every back-office kill-switch flips `ai_enabled`.

## §4 The AI Request Envelope

Every AI request inside the SaaS — whether from a copilot endpoint, a worker, or a webhook — carries this envelope:

```jsonc
{
  "request_id": "ai_req_01HXY...",          // ulid; correlation id
  "parent_trace_id": "trc_01HXY...",        // upstream trace
  "tenant_id": 8421,
  "user_id": 990012,                        // null for system-initiated
  "feature": "support-copilot.answer",      // namespaced feature id
  "intent": "answer_question",              // semantic intent for analytics
  "model_tier": "pro",                      // resolved from binding
  "model_requested": "claude-3.7-sonnet",   // before fallback
  "region": "eu-west-1",
  "kb_partition_id": "kb_t8421",
  "prompt_id": "support.answer.v17",
  "input_summary": "<512-char redacted summary>",
  "timestamp": "2026-05-11T08:14:22Z"
}
```

The gateway returns a matching response envelope with `model_used`, `tokens_in`, `tokens_out`, `usd_cost`, `latency_ms`, `fallback_used`, `eval_passed`, `citations`, `guardrail_findings`.

## §5 AI Lifecycle Events

The event bus carries:

| Event | Payload highlights | Consumers |
|---|---|---|
| `ai.request.started` | request envelope | tracing, rate-limit-watch |
| `ai.request.completed` | response envelope | cost ledger, analytics, eval sampler |
| `ai.cost.recorded` | tenant_id, usd, tokens | `ai-cost-per-tenant-attribution`, billing |
| `ai.eval.failed` | request_id, eval_dataset_id, failure | on-call, `ai-eval-harness` |
| `ai.injection.detected` | request_id, signal, classifier_score | `ai-prompt-injection-and-tenant-safety`, on-call |
| `ai.hallucination.detected` | request_id, grounding_score | SLO error budget, on-call |
| `ai.kill_switched` | tenant_id, actor, reason | back-office, support |
| `ai.budget.threshold` | tenant_id, percent | tenant admin email, sales-assist |

## §6 Silo vs Pool Decision Matrix for AI Assets

| Asset | Default | When to silo per tenant | When to pool with tenant_id filter |
|---|---|---|---|
| Vector store | pool | regulated industry, large tenant, sovereignty | most cases |
| Fine-tune | pool with adapters | enterprise tenant pays for it; > 50k examples | always start here |
| Prompts | pool, versioned | tenant requires custom voice / brand strings | nearly always |
| Eval dataset | per tenant | always — every tenant's traffic distribution differs | never; pooling kills signal |
| Conversation logs | per tenant store key | always for PII; pool only for derived metrics | only metrics, never raw |
| Model selection | per tenant binding | always — tier and region differ | never |

See `ai-tenant-isolation-patterns/references/vector-store-partitioning-tradeoffs.md` for the full tradeoff analysis.

## §7 Where Each Specialist Skill Fits

```
                    +--------------------+
                    |  ai-on-saas-       |
                    |  architecture (you)|
                    +---------+----------+
                              |
        +---------------------+----------------------+
        |                     |                      |
+-------+-------+     +------+------+        +-------+--------+
| AI control    |     | AI app      |        | AI quality &   |
| plane         |     | plane       |        | safety         |
+---------------+     +-------------+        +----------------+
| ai-model-     |     | ai-feature- |        | ai-eval-       |
| gateway       |     | spec        |        | harness        |
| ai-rag-multi- |     | ai-prompt-  |        | ai-halluc-     |
| tenant        |     | engineering |        | ination-slo    |
| ai-tenant-    |     | ai-output-  |        | ai-prompt-     |
| isolation     |     | design      |        | injection      |
| ai-cost-per-  |     | ai-agents-  |        | ai-feature-    |
| tenant        |     | tools       |        | rollout        |
| ai-usage-     |     |             |        | ai-observ-     |
| metering      |     |             |        | ability        |
+---------------+     +-------------+        +----------------+
                              |
                    +---------+----------+
                    | ai-entitlements-   |
                    | and-feature-gating |
                    | (binds plan → AI)  |
                    +--------------------+
```

## §8 Anti-Patterns

- **No control plane.** Each feature calls OpenAI directly. Fix: introduce gateway day 1; ban direct SDK use via lint rule.
- **Tenant id only in HTTP layer.** Workers, webhooks, and scheduled jobs lose the tenant id. Fix: tenant context propagation library; every queue envelope carries it; every gateway call requires it.
- **One shared vector index.** A bug in retrieval returns another tenant's chunks. Fix: see `ai-tenant-isolation-patterns`.
- **No prompt registry.** Prompts hard-coded; no rollback; no A/B; no per-tenant override. Fix: build the registry as a v1 control-plane service.
- **No eval harness.** Regressions ship to production. Fix: `ai-eval-harness` with CI gate.
- **No kill switch.** When a tenant's AI misbehaves, the only fix is a code deploy. Fix: `tenant_ai_binding.ai_enabled` flag flippable from back-office in < 1 minute.
- **Cost reconciled from provider invoice.** Tenant cost attribution is monthly and approximate. Fix: capture cost per request in the gateway.

## §9 Read Next

- `ai-model-gateway` — the LLM gateway design in detail.
- `ai-tenant-isolation-patterns` — vector stores, prompts, fine-tunes, eval data.
- `ai-rag-multi-tenant` — multi-tenant RAG end-to-end.
- `ai-cost-per-tenant-attribution` — operational pipeline.
- `ai-eval-harness` — golden datasets and CI gate.
- `ai-hallucination-slo-and-grounding` — citation grounding + SLO math.
- `ai-prompt-injection-and-tenant-safety` — threat model + red team.
- `ai-observability-and-debugging` — traces and replays.
- `ai-feature-rollout-and-experimentation` — flags and canaries.
- `ai-entitlements-and-feature-gating` — plan-tier binding.
- `ai-usage-metering-and-billing` — turning tokens into billable units.
- `saas-control-plane-engineering` — broader control-plane context.
