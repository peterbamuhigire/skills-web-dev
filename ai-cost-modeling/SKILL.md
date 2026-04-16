---
name: ai-cost-modeling
description: Token economics for AI-powered features — estimate raw token cost per
  user and per tenant, compare providers, model retail pricing, and calculate margin.
  Invoke before committing any AI feature and when designing the AI module pricing
  tier.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Cost Modeling

<!-- dual-compat-start -->
## Use When

- Token economics for AI-powered features — estimate raw token cost per user and per tenant, compare providers, model retail pricing, and calculate margin. Invoke before committing any AI feature and when designing the AI module pricing tier.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ai-cost-modeling` or would be better handled by a more specific companion skill.
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
| Performance | Per-tenant token cost projection | Markdown doc with token-usage estimates by feature and tenant tier | `docs/ai/cost-projection-2026-04-16.md` |
| Release evidence | AI feature go/no-go cost gate | Markdown doc declaring the per-tenant unit-economics decision before release | `docs/ai/cost-gate-2026-04-16.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Purpose

Before implementing any AI feature, calculate the full token cost so you can:
1. Choose the cheapest model that meets quality requirements.
2. Set a per-tenant budget cap that protects your margins.
3. Price the AI module add-on profitably for your client.
4. Advise the client on expected monthly AI spend per user.

---

## Provider Pricing Reference (2025–2026)

All prices in USD per 1 million tokens.

| Provider & Model | Input ($/1M) | Output ($/1M) | Context Window | Best For |
|-----------------|-------------|--------------|----------------|---------|
| **Claude Haiku 4.5** | $0.80 | $4.00 | 200K | High-volume, fast tasks |
| **Claude Sonnet 4.6** | $3.00 | $15.00 | 200K | Complex reasoning, long docs |
| **GPT-4o mini** | $0.15 | $0.60 | 128K | Cost-critical, simple tasks |
| **GPT-4o** | $2.50 | $10.00 | 128K | Balanced quality + cost |
| **DeepSeek V3** | $0.27 | $1.10 | 64K | Ultra-low cost, good quality |
| **Gemini 2.0 Flash** | $0.10 | $0.40 | 1M | Cheapest option, large context |
| **Gemini 1.5 Pro** | $1.25 | $5.00 | 2M | Very large document analysis |

*Verify current pricing at provider dashboards before quoting clients. Prices change frequently.*

---

## Token Estimation by Feature Pattern

Typical token ranges per single AI call:

| Feature Pattern | Input Tokens | Output Tokens | Notes |
|----------------|-------------|--------------|-------|
| Summarisation (1 record) | 300–800 | 100–300 | Scale with record length |
| Summarisation (batch 10) | 2,000–5,000 | 500–1,500 | |
| Classification (single) | 200–500 | 10–50 | Few-shot adds ~300 |
| Anomaly detection (daily log) | 1,000–3,000 | 100–300 | |
| Predictive alert | 500–2,000 | 100–400 | Depends on history injected |
| Natural language report | 1,000–4,000 | 500–2,000 | |
| Decision support | 800–3,000 | 200–600 | |
| Conversational assistant (turn) | 400–1,500 | 150–500 | Grows with history |
| Document extraction (1 page) | 800–2,000 | 200–600 | Image = higher |
| Semantic search query | 100–300 | 200–800 | Embedding = separate |

---

## Per-User Monthly Cost Calculator

### Formula

```
tokens_per_call     = input_tokens + output_tokens
calls_per_user_day  = [estimated from use case]
tokens_per_user_day = tokens_per_call × calls_per_user_day
tokens_per_user_month = tokens_per_user_day × 30

input_cost_per_user  = (input_tokens × calls/day × 30) / 1,000,000 × input_price
output_cost_per_user = (output_tokens × calls/day × 30) / 1,000,000 × output_price
total_cost_per_user  = input_cost_per_user + output_cost_per_user
```

### Example — POS Daily Sales Summary (Haiku 4.5)

```
Input:  1,500 tokens (day's transactions injected)
Output:   400 tokens (narrative summary)
Calls:    1 per user per day

Monthly input  = 1,500 × 1 × 30 / 1,000,000 × $0.80 = $0.036
Monthly output =   400 × 1 × 30 / 1,000,000 × $4.00 = $0.048
Total/user/month = $0.08
```

### Example — School At-Risk Student Alert (Sonnet 4.6, run weekly)

```
Input:  3,000 tokens (student history)
Output:   500 tokens (risk report)
Calls:    4 per user per month (weekly)

Monthly input  = 3,000 × 4 / 1,000,000 × $3.00 = $0.036
Monthly output =   500 × 4 / 1,000,000 × $15.00 = $0.030
Total/user/month = $0.07
```

### Example — In-App Chat Assistant (Haiku 4.5, active user)

```
Input:    800 tokens per turn (context + query)
Output:   250 tokens per turn
Turns:    10 per user per day

Monthly input  = 800 × 10 × 30 / 1,000,000 × $0.80 = $0.19
Monthly output = 250 × 10 × 30 / 1,000,000 × $4.00 = $0.30
Total/user/month = $0.49
```

---

## Per-Tenant (Franchise) Aggregation

```
tenant_monthly_cost = Σ (cost_per_user × active_users_in_tenant)

Example — 50-user tenant with mixed AI features:
  40 users × $0.08 (POS summary)    = $3.20
  10 users × $0.49 (chat assistant) = $4.90
  Tenant total                       = $8.10/month raw token cost
```

Track this via the token ledger (see `ai-metering-billing`).

---

## Retail Pricing — AI Module Add-On

### Pricing Strategy

Apply a **5–10× markup** over raw token cost. This covers:
- API overhead and retry costs (~20% buffer)
- Your engineering and support margin
- Client's unpredictable usage spikes
- Future model price changes

### Suggested Tier Structure

| Tier | Included Features | Token Budget/Tenant/Month | Suggested Price (UGX) |
|------|------------------|--------------------------|----------------------|
| **Starter AI** | Summarisation + Classification | 2M tokens | 50,000–80,000 |
| **Growth AI** | + Alerts + Reports + Search | 10M tokens | 150,000–250,000 |
| **Enterprise AI** | All features + Chat + Doc Intel | 50M tokens | 500,000–800,000 |

*Adjust based on number of users per tenant. For large tenants (> 50 users), price per user.*

### Per-User Pricing Alternative

If the client prefers per-user pricing:

| Tier | Price/User/Month (UGX) | Minimum Users |
|------|----------------------|---------------|
| AI Starter | 8,000–15,000 | 5 |
| AI Growth | 20,000–35,000 | 5 |
| AI Enterprise | 50,000–80,000 | 10 |

---

## Cost Optimisation Strategies

Apply these to reduce raw token cost before pricing:

1. **Cache frequent responses** — Daily summaries, weekly reports: cache for 24h. Reduces repeat calls by 60–80%.
2. **Batch calls** — Run nightly batch jobs instead of on-demand where latency is acceptable.
3. **Pre-filter data** — Send only the 10 most relevant rows, not 1,000. Use SQL `WHERE` and `LIMIT` before injecting.
4. **Use the cheapest adequate model** — Run Haiku/GPT-4o mini for classification; only escalate to Sonnet for complex reasoning.
5. **Compress context** — Summarise long histories before re-injecting them in conversational features.
6. **Set hard `max_tokens`** — Cap output tokens on every call. A $0.05 call becomes $2.00 if output runs uncapped.
7. **Streaming vs batch** — Streaming has the same token cost but better perceived performance; use it for chat.
8. **Prompt compression** — Remove verbose instructions after testing. Each token in the system prompt is paid on every call.

---

## Budget Cap Calculation (per tenant)

```
hard_cap_usd   = tier_price_usd × 0.60   ← your cost ceiling (preserves 40% margin)
soft_warning   = hard_cap_usd × 0.80     ← alert tenant admin at 80%
overage_rate   = $0.05 per 1,000 tokens  ← optional metered overage above hard cap
```

Store `hard_cap_usd` in the tenant AI module configuration. Enforce via Budget Guard middleware (see `ai-architecture-patterns`).

---

## Cost Model Output Template

```
## AI Cost Model — [Project] — [Feature Name] — [Date]

Model selected:         [name + reason]
Input tokens/call:      [n]
Output tokens/call:     [n]
Calls/user/day:         [n]
Raw cost/user/month:    $[n]
Tenant size (users):    [n]
Raw cost/tenant/month:  $[n]
Recommended tier:       [Starter / Growth / Enterprise]
Suggested price (UGX):  [n]
Gross margin:           [%]
Caching savings est.:   [%]
Budget hard cap (USD):  $[n]
```

---

**See also:**
- `ai-feature-spec` — Token estimates per feature
- `ai-metering-billing` — Token ledger and budget enforcement
- `ai-architecture-patterns` — Budget Guard middleware implementation
- `ai-opportunity-canvas` — Feature prioritisation by cost tier
