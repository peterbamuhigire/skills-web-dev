> Consolidated from skills/ai-usage-metering-and-billing/SKILL.md into ai-cost-and-metering on 2026-05-13. Load this through skills/ai-cost-and-metering/SKILL.md, not as an active skill entrypoint.

# AI Usage Metering and Billing
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Pricing an AI feature usage-based — pay-per-generation, pay-per-1k-tokens, pay-per-agent-run, pay-per-resolved-ticket.
- Adding overage on top of a plan's included allowance (Pro plan includes 1M AI tokens / month, then $X / 1M after).
- Implementing prepaid credit packs that drain as usage occurs.
- Wiring `ai.cost.recorded` events into Stripe Meters / Stripe usage records.
- Handling pro-ration, mid-cycle plan changes, and refunds on AI usage.

## Do Not Use When

- The task is internal cost attribution to control unit economics — `ai-cost-per-tenant-attribution`.
- The task is the boolean gate of which features the plan unlocks — `ai-entitlements-and-feature-gating`.
- The task is non-AI metered billing — `saas-entitlements-and-plan-gating` plus generic `subscription-billing` skills.

## Required Inputs

- Pricing model from product: per-token? per-call? per-generation? per-tool-use? Hybrid?
- Plan catalogue with included allowance and overage rate per dimension.
- Stripe (or alternative) account with Meters / usage records configured.
- `ai_requests` ledger with `billing_dimension` and `units` per row (or rule to derive them).

## Workflow

1. Read this `SKILL.md`.
2. Choose **billable dimensions** (§1) — what the customer pays for.
3. Define the **unit normalisation** (§2) — tokens → "credits"? Pure tokens? Per generation?
4. Map plans to **included allowance + overage tier** (§3).
5. Implement the **credit ledger** (§4) — drains real-time as usage occurs.
6. Wire to **Stripe Meters / usage records** (§5) with idempotency and reconciliation.
7. Design the **tenant-facing usage panel** (§6) and **invoice copy** (§7).
8. Handle **proration, mid-cycle, refunds, disputes** (§8).
9. Apply anti-patterns (§9).

## Quality Standards

- Every billable event is **idempotent on `request_id`** — replay-safe end-to-end.
- Stripe meter records reconcile with `ai_requests` within 0.5% on each cycle.
- Tenant usage panel matches the invoice to the cent.
- Credit drains atomic against the gateway — never overdraw, never double-debit.
- Disputes resolvable from the audit log in < 15 minutes per case.

## Anti-Patterns

- "Tokens" as the customer-facing unit. Customers don't understand tokens; sales can't price them.
- Billing on raw provider cost + margin without abstraction. Provider price drop = lost revenue with no win for the customer.
- Stripe usage_record without idempotency key — duplicate charges on retry.
- Async billing event that can fail silently. Use durable queue + retry + dead-letter.
- Overage that surprises the customer (no notice, no panel, no per-day cap).
- Including unlimited usage on Free or low tiers without rate / token caps elsewhere.

## Outputs

- Billable dimension list + unit definitions.
- Plan × allowance × overage tier table.
- Credit ledger schema + drain code.
- Stripe Meters configuration + reconciliation runbook.
- Usage panel + invoice copy.
- Proration policy.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Commercial | Pricing model card | Markdown | `docs/pricing/ai-pricing-model.md` |
| Architecture | Credit ledger schema | SQL DDL | `docs/ai/credit-ledger.md` |
| Release evidence | Stripe Meters wiring | Markdown + code | `docs/ai/stripe-meters.md` |
| Operability | Reconciliation runbook | Runbook | `docs/runbooks/ai-billing-recon.md` |

## References

- `references/stripe-metered-billing-for-ai.md` — Stripe Meters and usage record integration recipe.
- Companion: `ai-cost-per-tenant-attribution`, `ai-entitlements-and-feature-gating`, `ai-model-gateway`, `saas-entitlements-and-plan-gating`, `saas-rate-limiting-and-quotas`, `subscription-billing`.

<!-- dual-compat-end -->

## §1 Billable Dimensions

Pick one or two; resist more. Options:

| Dimension | When to use | Pitfall |
|---|---|---|
| Tokens (raw) | Pure platform/API SaaS | Customer can't reason about it |
| AI Credits (abstracted) | Most B2B SaaS | Requires conversion rate maintenance |
| Generations (1 call = 1 unit) | UI-driven AI features | Hides cost variance across long/short responses |
| Resolved outcomes (e.g., tickets answered) | Outcome-priced verticals | Requires resolution signal pipeline |
| Agent runs / agent steps | Agent products | Variance is huge; needs caps |
| Documents indexed / KB pages | RAG-heavy products | One-time signal; not great for recurring |

**Default for a B2B SaaS:** AI Credits + per-feature multiplier. Customers see "X credits"; internally tokens × multiplier = credits. Multiplier hides provider price volatility.

## §2 Unit Normalisation

Conversion table example:

| Feature | 1 Credit equals |
|---|---|
| `support-copilot.answer` (Sonnet) | 4k input + 1k output tokens |
| `support-copilot.summary` (Haiku) | 20k input + 2k output tokens |
| `analytics.sql-from-question` | 1 generation regardless of size |
| `agent.run` | per agent step × 1 credit each |
| `kb.ingest` | 100 pages = 1 credit (one-time) |

`units = ceil(tokens / divisor)` or `units = 1` per generation, etc. Stored on every `ai_requests` row.

## §3 Plans × Allowance × Overage

```
PLAN          MONTHLY $   AI CREDITS INCLUDED   OVERAGE
Free               0          100 credits        blocked at cap
Starter           29        2,000 credits        $0.02 / credit
Pro              149       20,000 credits        $0.015 / credit
Business         499      100,000 credits        $0.012 / credit
Enterprise       custom   negotiated             negotiated tier
```

Rules:
- Free tier hard-blocks at cap; no overage.
- Paid tiers default to allow overage with a per-tenant cap (default 200% of plan; configurable up).
- Volume discounts kick in monthly (each step down at higher tiers).
- Annual plans give 20% more credits at the same price.

## §4 Credit Ledger

```sql
CREATE TABLE ai_credit_ledger (
    tenant_id        BIGINT UNSIGNED NOT NULL,
    request_id       CHAR(26) NOT NULL,
    feature          VARCHAR(64) NOT NULL,
    units_charged    INT NOT NULL,                 -- credits (signed; refunds = negative)
    source           ENUM('included','overage','prepaid_pack','refund','adjustment') NOT NULL,
    period           CHAR(7) NOT NULL,             -- '2026-05'
    ts               DATETIME(3) NOT NULL,
    idempotency_key  VARCHAR(64) NOT NULL,         -- (tenant, request_id, 'charge')
    PRIMARY KEY (tenant_id, request_id),
    INDEX (tenant_id, period),
    UNIQUE (idempotency_key)
);

CREATE TABLE ai_credit_balance (
    tenant_id            BIGINT UNSIGNED PRIMARY KEY,
    included_remaining   INT NOT NULL,
    prepaid_remaining    INT NOT NULL,
    overage_used_period  INT NOT NULL,
    period               CHAR(7) NOT NULL,
    updated_at           DATETIME(3) NOT NULL
);
```

Drain order on each `ai.cost.recorded`:
1. Drain `included_remaining` first.
2. Then `prepaid_remaining` (oldest pack first).
3. Then `overage_used_period` increments.

If `overage_cap` hit → gateway returns `QUOTA_EXCEEDED:ai_overage`.

Atomic with Lua:

```lua
-- KEYS[1]=balance hash, ARGV[1]=units, ARGV[2]=overage_cap
local r = redis.call('HMGET', KEYS[1], 'included', 'prepaid', 'overage', 'cap_hit')
local included = tonumber(r[1])
local prepaid  = tonumber(r[2])
local overage  = tonumber(r[3])
local units    = tonumber(ARGV[1])
local cap      = tonumber(ARGV[2])

if included >= units then included = included - units
elseif included + prepaid >= units then
  prepaid = prepaid - (units - included); included = 0
else
  local need = units - included - prepaid
  if overage + need > cap then return {0, 'cap_hit'} end
  overage = overage + need; included = 0; prepaid = 0
end
redis.call('HMSET', KEYS[1], 'included', included, 'prepaid', prepaid, 'overage', overage)
return {1, 'ok'}
```

## §5 Stripe Meters / Usage Records

Per dimension, a Stripe Meter. The `event_name` for AI credits could be `ai_credits_overage`.

```python
import stripe

def report_overage(tenant_id, units, request_id):
    stripe.billing.MeterEvent.create(
        event_name="ai_credits_overage",
        payload={"value": str(units), "stripe_customer_id": customer_id_for(tenant_id)},
        identifier=request_id,        # idempotency key — Stripe dedups
    )
```

Use Stripe's `identifier` field as the idempotency key (`request_id`). Stripe dedups on identifier; replays are safe.

Reconciliation (monthly):
- Sum `ai_credit_ledger` rows where `source = 'overage'` for the period per tenant.
- Pull Stripe `meter.summary` for the same period.
- Diff per tenant; > 0.5% → investigate.

See `references/stripe-metered-billing-for-ai.md` for the full recipe.

## §6 Tenant Usage Panel

The customer must see:

- Credits remaining this period (included + prepaid).
- Credits used today and this month (sparkline).
- Per-feature breakdown (top 5 features by credit use).
- Overage spend so far this month with the projected cycle total.
- Buttons: upgrade plan, buy prepaid pack, set overage cap.
- Webhook subscriptions for usage thresholds (60/80/100%).

Live data from Redis `ai_credit_balance`. Reconciled view from the ledger.

## §7 Invoice Copy

The invoice line items must read in plain language:

```
Pro plan – May 2026                                     $149.00
AI credits overage – 3,240 credits @ $0.015              $48.60
Prepaid pack purchased May 12 – 10,000 credits           $99.00
                                              Total    $296.60
```

Behind each line, a link to a usage drilldown that matches the credit ledger.

## §8 Proration, Mid-Cycle, Refunds

- **Plan upgrade mid-cycle**: new included allowance is granted **net of credits already consumed at current tier** (or pro-rated for the rest of the cycle, depending on policy). Document which.
- **Plan downgrade mid-cycle**: take effect at next cycle; current period rules apply until rollover.
- **Refund of usage**: write a negative-units row to `ai_credit_ledger` with `source='refund'`; emit a corresponding negative meter event in Stripe (or credit memo).
- **Disputes**: pull `ai_requests` rows for the request_ids in question; produce a CSV from the audit log; this is the evidence.
- **Failed AI requests**: by policy, *not* charged. Gateway only emits `ai.cost.recorded` on success (or partial success with a `partial=true` flag; partial responses charged half).

## §9 Anti-Patterns

- Billing tokens directly to customers. They can't budget.
- One-way meter writes with no idempotency. Retries cause double charges.
- Credits drained outside the gateway. Inconsistency between gate (deny) and meter (charge).
- Overage with no cap. Mid-month $50k surprise.
- Free tier with no per-tenant token cap. Abuse vector.
- Cannot reproduce a single line on an invoice from the ledger. Lose the dispute.
- Pricing per-credit identical at every tier. No volume incentive.

## §10 Read Next

- `ai-cost-per-tenant-attribution` — the source data.
- `ai-entitlements-and-feature-gating` — what's gated vs metered.
- `ai-model-gateway` — emits `ai.cost.recorded`.
- `saas-rate-limiting-and-quotas` — runtime enforcement of overage caps.
- `subscription-billing` — broader billing context.


