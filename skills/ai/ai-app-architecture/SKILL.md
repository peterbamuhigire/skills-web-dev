---
name: ai-app-architecture
description: Use when designing or building AI-powered application systems — choosing
  architecture style, selecting components, structuring the AI stack, making build-vs-buy
  decisions, and planning multi-tenant AI module gating
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Application Architecture
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Use when designing or building AI-powered application systems — choosing architecture style, selecting components, structuring the AI stack, making build-vs-buy decisions, and planning multi-tenant AI module gating
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ai-app-architecture` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | AI architecture decision record | Markdown doc per `skill-composition-standards/references/adr-template.md` covering provider, deployment, and integration choices | `docs/ai/architecture-adr-assistant.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
- `references/practical-ai-engineering.md` - evaluation-first AI engineering, RAG quality checks, agentic workflow controls, guardrails, telemetry, and cost discipline.
- `references/ai-transformation-operating-model.md` - operating-model, adoption, governance, human-centred design, and sustainability gates distilled from supplied AI transformation source material.
<!-- dual-compat-end -->
## Overview

AI-powered apps are built on top of foundation models via APIs. You are NOT training models — you are orchestrating them. Your value lies in the application layer: context construction, prompt engineering, retrieval, guardrails, and user experience.

**Core principle:** Start with the simplest architecture that works. Evolve deliberately.

## Premier Agency Standard

Design AI systems for measurable economic value, production reliability, and long-term maintainability. Every serious AI application must connect model behavior to a business workflow, revenue lever, cost reduction, risk reduction, or service-quality improvement.

Before selecting a model or framework, define:

- **Business outcome**: the operational metric the AI feature should improve.
- **User decision/action**: what the user or system will do differently because AI exists.
- **Data advantage**: which proprietary, local, domain, or workflow data improves the result.
- **Failure cost**: what happens when the model is wrong, slow, unavailable, biased, or expensive.
- **Evaluation target**: the minimum acceptable quality, latency, cost, and safety threshold.
- **Operating owner**: who monitors, tunes, approves, and maintains the feature after launch.

Reject AI features that cannot state their economic value or decision impact.

---

## Architecture Styles (Choose One to Start)

| Style | Description | When to Use |
|---|---|---|
| **Wrap** | Your UI + prompt engineering wraps a commercial LLM API | First project, internal tools, quick wins |
| **RAG** | Retriever fetches private/fresh data, injected into prompt | Apps needing company-specific or up-to-date knowledge |
| **Workflow** | Deterministic steps call models only where judgment or language is needed | Business processes with predictable stages and audit requirements |
| **Agentic** | LLM plans and executes multi-step tasks using tools | Complex automation, multi-step workflows |
| **Fine-tuned** | Model weights adapted for domain/style | Only when brand voice or jargon cannot be achieved via prompts |

**Default path:** Wrap -> RAG -> deterministic workflow -> agents. Only fine-tune when prompts, retrieval, examples, routing, and workflow design cannot meet the target.

---

## The AI Application Stack

```
┌──────────────────────────────────┐
│   User Interface (web/mobile)    │
├──────────────────────────────────┤
│   Input Guardrail                │  ← block PII, prompt injection, off-topic
│   Router / Intent Classifier     │  ← route to right model/solution
│   Context Builder (RAG / Tools)  │  ← feature engineering for AI
│   Model Gateway                  │  ← unified API wrapper, key mgmt, fallbacks
│   LLM API (OpenAI/Codex/Gemini) │
│   Output Guardrail               │  ← catch toxicity, format failures, PII
│   Cache Layer                    │  ← exact + semantic caching
│   Streaming Handler              │  ← MANDATORY — never block on full generation
├──────────────────────────────────┤
│   Token Ledger (MANDATORY)       │  ← log every call: tenant_id, user_id, tokens
│   AI Module Gate (OFF by default)│  ← per-tenant enable/disable
└──────────────────────────────────┘
```

---

## Component Responsibilities

### Input Guardrail
- Detect and mask PII before sending to external APIs
- Block prompt injection patterns
- Enforce topic restrictions (domain scope)
- Tools: Meta Purple Llama, NVIDIA NeMo Guardrails, OpenAI Moderation API

### Router
- Classify intent → route to right model or solution
- Send simple queries to cheaper models (BERT, GPT-mini)
- Detect out-of-scope queries before wasting API calls
- Detect ambiguous queries → ask for clarification
- Pattern: `routing → retrieval → generation → scoring`

### Context Builder
- Context construction = feature engineering for AI
- Retrieve relevant chunks (RAG), live data (APIs), user profile
- This is where most quality improvement happens — invest here
- Version prompts, retrieval settings, chunking rules, schemas, and tool definitions as production configuration
- Separate tenant/user context from global knowledge to prevent cross-client data leakage

### Model Gateway
- Centralises all LLM provider calls (OpenAI, Anthropic, Google, self-hosted)
- Centralises: API key management, rate limiting, logging, fallback policies
- Enables swapping providers without touching application code
- Tools: Portkey AI Gateway, MLflow AI Gateway, Kong
- Expose common controls: request id, tenant id, model id, prompt version, timeout, retry policy, budget class, and safety profile

### Output Guardrail
- Catch format failures (invalid JSON/schema) → retry automatically
- Catch hallucinations, toxic content, brand-risk responses
- Fall back to human operators for sensitive/tricky queries
- **Note:** streaming mode complicates output guardrails — plan for partial responses

### Semantic Cache
- Exact cache: identical queries → return stored response
- Semantic cache: similar queries → return stored response (use embedding similarity)
- Cache at vector search level too (expensive embedding calls)
- Warning: improper cache can leak user-specific data — use tenant-scoped cache keys

---

## Architecture Evolution Pattern

```
Step 1 (Baseline):   Query → Model API → Response
Step 2 (Context):    Query → Retriever → [Context + Query] → Model → Response
Step 3 (Guardrails): Input Guard → Context → Model → Output Guard → Response
Step 4 (Router):     Router → [Intent-specific path] → Model(s) → Response
Step 5 (Cache):      Router → Cache → [miss: full pipeline] → Cache Store
Step 6 (Agents):     Router → Agent Loop [Plan → Tools → Reflect] → Response
```

Add each layer only when its absence is causing a real problem.

For production AI features, load `references/practical-ai-engineering.md` before finalising the architecture. It adds evaluation, RAG, agent, safety, fallback, telemetry, and cost-control gates.

## Production AI Platform Requirements

| Capability | Minimum Standard |
|---|---|
| Versioning | Version prompts, models, tools, retrieval indexes, evaluation datasets, and safety policies |
| Observability | Log quality signals, cost, latency, failures, tool calls, cache hits, and user feedback by tenant and feature |
| Evaluation | Maintain golden sets, regression tests, adversarial cases, and release thresholds before launch |
| Governance | Document data flow, retention, PII handling, model/provider choice, human approval points, and audit trail |
| Resilience | Add timeouts, retries with backoff, fallbacks, degraded UX, queueing for long work, and circuit breakers |
| Data quality | Treat data pipelines, embeddings, metadata, and retrieval filters as first-class production assets |
| Explainability | Provide citations, source snippets, confidence bands, or reasoning summaries where users must trust decisions |
| Maintenance | Assign owners for prompt updates, eval refreshes, model migrations, cost reviews, and incident response |

## Workflow vs Agent Decision

- Use a deterministic workflow when the process steps are known, regulated, auditable, or cost-sensitive.
- Use an agent when the path genuinely depends on intermediate observations, tool results, or open-ended planning.
- Keep agents on a short leash: bounded tool set, max steps, scoped memory, explicit approvals, and rollback-safe actions.
- Do not use agents for simple summarization, extraction, classification, or transformation.

## Data and ML System Design Checks

- Define online/offline data sources, freshness requirements, ownership, quality checks, and missing-data behavior.
- Choose metrics that reflect the business objective, not only model accuracy.
- Plan for distribution shift: seasonality, new user behavior, changing regulations, platform algorithm changes, and language mix.
- Store enough inputs, outputs, versions, and feedback to debug regressions without storing unnecessary sensitive data.
- Separate training/evaluation data from production data where supervised learning or fine-tuning is used.

---

## Build vs Buy Decision

| Option | Effort | Control | Cost | When |
|---|---|---|---|---|
| Commercial API (OpenAI/Codex) | Low | Low | Per-token | Default choice |
| Open source self-hosted (Llama) | High | Full | GPU infra | Data privacy requirement, high volume |
| Fine-tuned commercial | Medium | Partial | Training + inference | Brand voice, jargon control |
| Fine-tuned self-hosted | Very High | Full | High | Maximum control, regulated industries |

**Rule:** API wrap first. Justify self-hosting with actual cost/compliance numbers.

---

## AI Module Gating (MANDATORY in SaaS)

Every AI feature MUST be gated. AI costs real money per token.

```sql
-- Schema: AI module per tenant
CREATE TABLE tenant_ai_config (
  tenant_id     INT PRIMARY KEY,
  ai_enabled    BOOLEAN DEFAULT FALSE,   -- OFF by default
  monthly_budget_usd DECIMAL(10,2),      -- null = unlimited
  budget_alert_pct   INT DEFAULT 80,     -- alert at 80% of budget
  plan_name     VARCHAR(50),             -- 'basic', 'pro', 'enterprise'
  enabled_at    TIMESTAMP,
  created_at    TIMESTAMP DEFAULT NOW()
);
```

**Enforcement:** Every AI endpoint checks `tenant_ai_config.ai_enabled` before processing. Return `402 Payment Required` if disabled.

---

## Token Ledger (MANDATORY)

Log every AI API call for billing, debugging, and cost visibility.

```sql
CREATE TABLE ai_token_usage (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  tenant_id     INT NOT NULL,
  user_id       INT NOT NULL,
  feature_name  VARCHAR(100),            -- 'invoice_analysis', 'report_summary'
  model         VARCHAR(50),             -- 'gpt-4o', 'Codex-3-sonnet'
  tokens_in     INT NOT NULL,
  tokens_out    INT NOT NULL,
  cost_usd      DECIMAL(10,6),           -- calculated at log time
  latency_ms    INT,
  created_at    TIMESTAMP DEFAULT NOW(),
  INDEX idx_tenant_date (tenant_id, created_at),
  INDEX idx_user_date (user_id, created_at)
);
```

```sql
-- Usage by tenant (for invoicing)
SELECT tenant_id,
       SUM(tokens_in + tokens_out) AS total_tokens,
       SUM(cost_usd) AS total_cost_usd,
       DATE_FORMAT(created_at, '%Y-%m') AS month
FROM ai_token_usage
GROUP BY tenant_id, month;

-- Usage by user (for analytics)
SELECT user_id, feature_name,
       SUM(tokens_in + tokens_out) AS tokens,
       COUNT(*) AS calls
FROM ai_token_usage
WHERE tenant_id = ? AND created_at > DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY user_id, feature_name;
```

---

## Quota Enforcement

```php
function checkAiQuota(int $tenantId): void {
    $config = TenantAiConfig::find($tenantId);

    if (!$config || !$config->ai_enabled) {
        throw new AiModuleDisabledException('AI module not enabled for this account.');
    }

    if ($config->monthly_budget_usd !== null) {
        $spent = AiTokenUsage::currentMonthCost($tenantId);
        if ($spent >= $config->monthly_budget_usd) {
            throw new AiBudgetExceededException('Monthly AI budget reached.');
        }
        if ($spent >= $config->monthly_budget_usd * ($config->budget_alert_pct / 100)) {
            notifyTenantBudgetAlert($tenantId, $spent, $config->monthly_budget_usd);
        }
    }
}
```

---

## Infrastructure Options

| Layer | Lightweight | Production |
|---|---|---|
| LLM | OpenAI API | API + fallback provider via gateway |
| Context | In-memory / SQLite | Vector DB (Chroma, Qdrant, Pinecone) |
| Cache | Redis | Redis Cluster |
| Queue | Sync | Kafka / RabbitMQ |
| Monitoring | Log file | Prometheus + Grafana |

---

## Anti-Patterns

- **No module gating** — every user can trigger AI calls, destroying your margins
- **No token logging** — you cannot invoice clients or debug runaway costs
- **Orchestrator too early** — LangChain/LlamaIndex before you understand your pipeline adds complexity
- **Fine-tuning first** — always try prompt engineering and RAG before fine-tuning
- **Blocking on full generation** — always stream tokens to the user immediately
- **Hard-coded system prompts** — make prompts configurable, not hardcoded in code

---

## Sources
Chip Huyen — *AI Engineering* (2025); David Spuler — *Generative AI Applications* (2024); Andrea De Mauro — *AI Applications Made Easy* (2024)
## Consolidated Child References

- Load `references/routing.md` to map retired AI child skill slugs to their reference modules.

