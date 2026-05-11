---
name: ai-entitlements-and-feature-gating
description: Use when designing how AI features are unlocked by plan tier — which model tier (flagship vs distilled), context-length limits, generations/day, tools available to the agent, KB ingestion size, gated AI features (per-feature toggle by plan). Covers entitlement schema, gateway enforcement, upgrade UX, and the contract with `saas-entitlements-and-plan-gating` for the catalogue.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Entitlements and Feature Gating
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Mapping plans to AI capabilities: Free → distilled model + 100 generations/day; Pro → flagship + 20k/month + tools; Enterprise → custom + agent + KB.
- Adding a new AI feature and deciding which tiers see it.
- Letting Sales offer per-tenant overrides (one Pro customer gets the agent feature without upgrading) without code changes.
- Enforcing entitlements at the gateway, not in feature code.

## Do Not Use When

- The task is the platform-wide entitlement engine itself — that lives in `saas-entitlements-and-plan-gating`. This skill is the AI-specific contract on top of it.
- The task is metering / billing of AI use — `ai-usage-metering-and-billing`.
- The task is internal cost control — `ai-cost-per-tenant-attribution`.

## Required Inputs

- The platform entitlement schema from `saas-entitlements-and-plan-gating`.
- The list of AI features in the product.
- The plan catalogue with target unit economics.
- The model tier catalogue (flagship / mid / distilled).

## Workflow

1. Read this `SKILL.md`.
2. Define the **AI entitlement keys** (§1) — what the gateway checks.
3. Map **plans × AI entitlements** (§2).
4. Implement **gateway enforcement** (§3) — every request resolves entitlements first.
5. Design the **upgrade UX** (§4) — when blocked, where to go.
6. Implement **per-tenant overrides** (§5) — Sales / Success can grant features.
7. Apply anti-patterns (§6).

## Quality Standards

- Every AI request resolves entitlements **before** the provider is called.
- Adding an AI entitlement is **no code change** in the gateway — it's a catalogue update.
- A blocked request returns a structured error with `upgrade_url` containing context for the upgrade page.
- Per-tenant overrides have an `expires_at`, a `reason`, and an `actor`.
- The entitlement catalogue is the single source of truth — back-office, billing, gateway, marketing all read it.

## Anti-Patterns

- AI entitlements scattered across feature flags, env vars, and `if plan == 'pro'` strings. Drift everywhere.
- Hard-coded model selection in feature code (`if plan == 'pro': model = 'sonnet'`). Should be a binding lookup.
- Free-tier with no enforced limits — abuse vector.
- Block-page that doesn't tell the user what to upgrade to, or how much it costs.
- Per-tenant override granted via SQL `UPDATE` with no audit, no expiry, no reason.

## Outputs

- AI entitlement key catalogue.
- Plan × entitlement matrix.
- Gateway enforcement contract.
- Upgrade UX patterns and copy.
- Per-tenant override surface in back-office.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Commercial | AI entitlements catalogue | Markdown table | `docs/ai/ai-entitlements.md` |
| Architecture | Gateway entitlement check spec | Markdown / code | `docs/ai/entitlement-enforcement.md` |
| UX | Upgrade UX patterns | Markdown + screenshots | `docs/ai/upgrade-ux.md` |

## References

- Companion: `saas-entitlements-and-plan-gating`, `ai-on-saas-architecture`, `ai-model-gateway`, `ai-usage-metering-and-billing`, `ai-cost-per-tenant-attribution`, `ai-feature-rollout-and-experimentation`.

<!-- dual-compat-end -->

## §1 AI Entitlement Keys

Keys the gateway checks. Names are stable; values are per-plan.

| Key | Type | Example |
|---|---|---|
| `ai.feature.<feature_id>.enabled` | bool | `ai.feature.support-copilot.enabled = true` |
| `ai.model_tier` | enum | `flagship` / `mid` / `distilled` |
| `ai.context_max_tokens` | int | 8192 / 32k / 128k / 200k |
| `ai.max_output_tokens` | int | 512 / 2048 / 8192 |
| `ai.generations_per_day` | int | 100 / 1000 / 100000 / unlimited |
| `ai.tokens_per_month` | int | 100k / 2M / 20M / unlimited |
| `ai.tools.enabled` | bool | gated agent tools at higher tiers |
| `ai.tools.allowed` | list | `["web_search","code_exec","sql"]` |
| `ai.kb.max_pages` | int | 100 / 10k / unlimited |
| `ai.kb.embedding_tier` | enum | `small` / `large` |
| `ai.agent.max_steps` | int | 5 / 20 / 50 |
| `ai.agent.concurrent_sessions` | int | 1 / 5 / 50 |
| `ai.region` | enum | tenant-bound region |
| `ai.fine_tune.enabled` | bool | Enterprise only |
| `ai.byok.enabled` | bool | Enterprise only |

Adding a feature usually adds an `ai.feature.<id>.enabled` row and possibly a per-feature variant of the limits above.

## §2 Plan × Entitlement Matrix

```
                              Free      Starter    Pro        Business   Enterprise
ai.feature.support-copilot    on        on         on         on         on
ai.feature.agent              off       off        off        on         on
ai.feature.knowledge-base     off       on         on         on         on
ai.feature.fine-tune          off       off        off        off        on
ai.model_tier                 distilled distilled  flagship   flagship   custom
ai.context_max_tokens         8k        32k        128k       200k       custom
ai.max_output_tokens          512       2048       4096       8192       custom
ai.generations_per_day        50        500        5000       unlimited  unlimited
ai.tokens_per_month           100k      2M         20M        unlimited  unlimited
ai.tools.enabled              off       off        on         on         on
ai.tools.allowed              []        []         [search]   [search,exec] custom
ai.kb.max_pages               -         500        10k        100k       unlimited
ai.kb.embedding_tier          -         small      large      large      large
ai.agent.max_steps            -         -          -          20         50
ai.agent.concurrent_sessions  -         -          -          5          50
ai.region                     any       any        any        tenant     tenant
ai.fine_tune.enabled          off       off        off        off        on
ai.byok.enabled               off       off        off        off        on
```

## §3 Gateway Enforcement

The gateway's entitlement stage (`ai-model-gateway` §2) runs after binding resolution. Pseudocode:

```python
def enforce_entitlements(ctx):
    e = ctx.entitlements    # resolved from plan + per-tenant overrides
    feature_key = f"ai.feature.{ctx.feature}.enabled"
    if not e.get_bool(feature_key):
        raise NotEntitled(feature_key, upgrade_context=ctx.feature)

    # context length
    if ctx.estimated_tokens_in > e.get_int("ai.context_max_tokens"):
        raise NotEntitled("ai.context_max_tokens")

    # output cap
    if ctx.max_tokens_out > e.get_int("ai.max_output_tokens"):
        ctx.max_tokens_out = e.get_int("ai.max_output_tokens")  # clip silently

    # tool gate
    if ctx.uses_tools and not e.get_bool("ai.tools.enabled"):
        raise NotEntitled("ai.tools.enabled")
    if ctx.uses_tools:
        allowed = set(e.get_list("ai.tools.allowed"))
        for t in ctx.tools_requested:
            if t not in allowed:
                raise NotEntitled(f"ai.tools.allowed:{t}")

    # model tier → resolved model already from binding
```

The entitlement object is materialised per request from:
1. Plan catalogue defaults.
2. Plan overrides (e.g., legacy plan grandfathering).
3. Per-tenant overrides (`tenant_ai_entitlement_override`).

## §4 Upgrade UX

When the gateway returns `NotEntitled`, the response shape:

```json
{
  "error": {
    "code": "AI_NOT_ENTITLED",
    "key": "ai.feature.agent.enabled",
    "message": "The agent feature is included from the Business plan.",
    "current_plan": "pro",
    "required_plan": "business",
    "upgrade_url": "https://app.example.com/billing/upgrade?context=agent_feature",
    "feature_id": "agent.run"
  }
}
```

UI patterns:
- **Inline upsell**: the locked feature shows a CTA card not a 403 page.
- **Compare** plans inline; one-click upgrade.
- **Soft prompt** when approaching a quota (90%) — proactive, not reactive.
- **Self-serve override** for trial: 14-day trial of higher tier feature, single-click.

Copy patterns: lead with the value (what the user can do), not the lock; show the price.

## §5 Per-Tenant Overrides

Schema:

```sql
CREATE TABLE tenant_ai_entitlement_override (
    tenant_id       BIGINT UNSIGNED NOT NULL,
    key             VARCHAR(64) NOT NULL,
    value           JSON NOT NULL,
    reason          VARCHAR(255) NOT NULL,
    actor_user_id   BIGINT UNSIGNED NOT NULL,
    expires_at      DATETIME,
    created_at      DATETIME NOT NULL,
    PRIMARY KEY (tenant_id, key)
);
```

Rules:
- Override always wins over plan defaults.
- `expires_at` recommended; on expiry, falls back to plan.
- `actor_user_id` is the staff user; `reason` is required.
- Every change emits `ai.entitlement.override.set` / `.expired` events.
- Back-office UI exposes the override grid with filter + bulk apply.

## §6 Anti-Patterns

- Plan-name string-comparisons in feature code (`if plan == 'pro'`). Use entitlement keys.
- Entitlement check after the provider call. Wastes money on a refused request.
- Cap-hit returns 403 without `upgrade_url`. Hostile.
- Permanent overrides for everyone "temporarily" — drift.
- Tools allowed list managed in code. Should be entitlement-driven.
- Per-tenant overrides with no audit. Compliance gap.
- Different entitlement results between gateway and back-office display. Source-of-truth split.

## §7 Agent Entitlements — First-Class Keys

Agentic features need entitlement keys distinct from single-shot AI. The minimum set:

| Key | Type | Meaning | Default by tier (illustrative) |
|---|---|---|---|
| `ai.agent.enabled` | bool | Tenant can use agents at all | Free: false, Pro: true, Ent: true |
| `ai.agent.features` | list[string] | Agent features unlocked (`support_copilot`, `log_investigator`, ...) | per tier |
| `ai.agent.allowed_tools` | list[string] | Tool names this tenant's agents may use | per tier |
| `ai.agent.max_steps` | int | Step budget per task | Pro: 12, Ent: 25 |
| `ai.agent.max_wallclock_minutes` | int | Wallclock budget per task | Pro: 5, Ent: 30 |
| `ai.agent.max_cost_usd_per_task` | float | Cost budget per task | Pro: 1.00, Ent: 10.00 |
| `ai.agent.max_concurrent_sessions` | int | Concurrent in-flight agent tasks per tenant | Pro: 3, Ent: 20 |
| `ai.agent.max_steps_per_day` | int | Aggregate step quota | Pro: 500, Ent: 10000 |
| `ai.agent.memory_mode` | enum | `off` / `prompt` / `auto` (`ai-agent-memory` §6) | Free: off, Pro: prompt, Ent: auto |
| `ai.agent.multi_agent_enabled` | bool | Can spawn supervisor/worker topologies | Ent only |
| `ai.agent.standing_approvals_enabled` | bool | Power-user pre-approvals | Ent only |
| `ai.agent.long_running_enabled` | bool | Tasks longer than 5 min allowed | Pro + Ent |

### Enforcement points

| Key | Enforced by |
|---|---|
| `ai.agent.enabled`, `ai.agent.features` | API / UI — feature cannot be launched |
| `ai.agent.allowed_tools` | Tool registry resolution (`ai-agent-tool-catalogue-and-action-gating` §3) |
| `ai.agent.max_steps`, `max_wallclock_minutes`, `max_cost_usd_per_task` | Runtime budgets (`ai-agent-cost-and-step-budgets`) |
| `ai.agent.max_concurrent_sessions` | Runtime task queue + `saas-rate-limiting-and-quotas` agent section |
| `ai.agent.max_steps_per_day` | Rate-limiting counter, per-tenant per-day |
| `ai.agent.memory_mode` | `ai-agent-memory` write-gate |
| `ai.agent.multi_agent_enabled` | Runtime — supervisor task creation refused |
| `ai.agent.standing_approvals_enabled` | Approval UX — standing-approval form hidden if disabled |
| `ai.agent.long_running_enabled` | Runtime — refuse task creation with `wallclock_budget > 300s` if disabled |

### Catalogue example

```yaml
plans:
  free:
    ai.agent.enabled: false
  pro:
    ai.agent.enabled: true
    ai.agent.features: [support_copilot]
    ai.agent.allowed_tools: [kb_search, customer_lookup, invoice_create_draft, invoice_send_for_approval]
    ai.agent.max_steps: 12
    ai.agent.max_wallclock_minutes: 5
    ai.agent.max_cost_usd_per_task: 1.00
    ai.agent.max_concurrent_sessions: 3
    ai.agent.max_steps_per_day: 500
    ai.agent.memory_mode: prompt
    ai.agent.multi_agent_enabled: false
    ai.agent.long_running_enabled: false
  enterprise:
    ai.agent.enabled: true
    ai.agent.features: [support_copilot, log_investigator, deal_drafter]
    ai.agent.allowed_tools: ["*"]
    ai.agent.max_steps: 25
    ai.agent.max_wallclock_minutes: 30
    ai.agent.max_cost_usd_per_task: 10.00
    ai.agent.max_concurrent_sessions: 20
    ai.agent.max_steps_per_day: 10000
    ai.agent.memory_mode: auto
    ai.agent.multi_agent_enabled: true
    ai.agent.standing_approvals_enabled: true
    ai.agent.long_running_enabled: true
```

### Sales-grantable overrides

Common Sales / Customer Success overrides:
- Grant `log_investigator` to a Pro tenant for 30 days (POV).
- Raise `max_steps_per_day` to 5,000 for a Pro tenant for one billing cycle.
- Enable `multi_agent_enabled` for Pro for a contract pilot.

All overrides written through the back-office with `reason`, `expires_at`, `actor`.

### Upgrade page contract for agent-blocked requests

```json
{
  "error": "upgrade_required",
  "blocked_key": "ai.agent.max_concurrent_sessions",
  "current_value": 3,
  "current_plan": "pro",
  "upgrade_path": [
    { "plan": "enterprise", "would_allow": 20, "upgrade_url": "/billing/upgrade?plan=enterprise&context=agent_concurrency" }
  ]
}
```

Block pages show the specific reason and which plan unblocks it.

## §8 Read Next

- `ai-agent-runtime-architecture` — the runtime that consumes agent entitlements.
- `ai-agent-cost-and-step-budgets` — runtime budgets derived from entitlements.
- `ai-agent-tool-catalogue-and-action-gating` — per-tenant tool allow-list resolution.
- `saas-rate-limiting-and-quotas` — agent quotas (concurrent sessions, steps/day) enforcement.
- `saas-entitlements-and-plan-gating` — the platform-wide engine and the catalogue.
- `ai-on-saas-architecture` — where this fits.
- `ai-model-gateway` — enforces this.
- `ai-usage-metering-and-billing` — meters what entitlement allows.
- `ai-feature-rollout-and-experimentation` — for soft launches that override entitlement temporarily.
