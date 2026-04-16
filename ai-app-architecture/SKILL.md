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
<!-- dual-compat-end -->
## Overview

AI-powered apps are built on top of foundation models via APIs. You are NOT training models — you are orchestrating them. Your value lies in the application layer: context construction, prompt engineering, retrieval, guardrails, and user experience.

**Core principle:** Start with the simplest architecture that works. Evolve deliberately.

---

## Architecture Styles (Choose One to Start)

| Style | Description | When to Use |
|---|---|---|
| **Wrap** | Your UI + prompt engineering wraps a commercial LLM API | First project, internal tools, quick wins |
| **RAG** | Retriever fetches private/fresh data, injected into prompt | Apps needing company-specific or up-to-date knowledge |
| **Agentic** | LLM plans and executes multi-step tasks using tools | Complex automation, multi-step workflows |
| **Fine-tuned** | Model weights adapted for domain/style | Only when brand voice or jargon cannot be achieved via prompts |

**Default path:** Wrap → RAG → Agents. Only fine-tune when all else fails.

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
│   LLM API (OpenAI/Claude/Gemini) │
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

### Model Gateway
- Centralises all LLM provider calls (OpenAI, Anthropic, Google, self-hosted)
- Centralises: API key management, rate limiting, logging, fallback policies
- Enables swapping providers without touching application code
- Tools: Portkey AI Gateway, MLflow AI Gateway, Kong

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

---

## Build vs Buy Decision

| Option | Effort | Control | Cost | When |
|---|---|---|---|---|
| Commercial API (OpenAI/Claude) | Low | Low | Per-token | Default choice |
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
  model         VARCHAR(50),             -- 'gpt-4o', 'claude-3-sonnet'
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
