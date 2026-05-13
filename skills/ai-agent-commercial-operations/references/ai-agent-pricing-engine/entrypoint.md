> Consolidated from skills/ai-agent-pricing-engine/SKILL.md into ai-agent-commercial-operations on 2026-05-13. Load this through skills/ai-agent-commercial-operations/SKILL.md, not as an active skill entrypoint.

# AI Agent Pricing Engine
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Engineering the resolver that turns a billing event (`agent.resolution.completed`, etc.) into a numeric `unit_price_cents`.
- Designing the **price-rule catalogue** per feature, per tier, per region.
- Implementing **intervention-credit logic** (heavy intervention discounts the rate).
- Implementing **vendor-cost-pass-through** with markup (third-party API costs flowed through with margin).
- Implementing **FX corridor** rules for multi-currency.
- Handling **volume tiers** at the resolution level (not just credits).
- Wiring the resolver to the billing pipeline (`ai-agent-attempted-vs-completed-billing`).

## Do Not Use When

- The task is the commercial pricing decision (what numbers to charge) — `software-pricing-strategy`. This engine is the implementation.
- The task is metering of tokens / credits / generations — `ai-usage-metering-and-billing`.
- The task is revenue recognition — `ai-agent-revenue-recognition`.
- The task is the SLA credit calculator — `ai-agent-sla-credit-automation`.

## Required Inputs

- Per-feature commercial price points (from `software-pricing-strategy` + business-plan engine).
- Per-tenant plan tier (`ai-entitlements-and-feature-gating`).
- Tenant invoice currency and FX policy.
- Per-feature vendor cost mix (LLM + tool API costs) from cost attribution (`ai-cost-per-tenant-attribution`).
- Success contract per feature (intervention discount factors).

## Workflow

1. Read this `SKILL.md`.
2. Define the **price-rule schema** (§1) — feature × tier × dimension → unit price.
3. Implement the **resolver** (§2). See `references/price-rule-resolver.md`.
4. Apply **intervention credit** logic (§3). See `references/intervention-credit-logic.md`.
5. Apply **vendor cost pass-through** (§4). See `references/vendor-cost-pass-through.md`.
6. Handle **FX corridor** (§5).
7. Wire **volume tiers** (§6).
8. Apply anti-patterns (§7).

## Quality Standards

- The resolver is **pure and deterministic** — same inputs give the same output. No clock-dependent behavior except for tier history.
- Every price rule is **versioned** (`pricing_rule_version`). Old billing events resolve against the version effective at their `occurred_at`.
- Rule changes ship via PR with a *price-impact analysis* (replay last 30 days, show per-tenant delta).
- The resolver returns a `(unit_price_cents, currency, rule_version, calculation_trace)`. The trace is what auditors / customers see if they ask "how was this priced?".
- Vendor pass-through pricing has a clear markup floor; pass-through-at-cost is never the default.
- FX corridor: tenant invoice currency is locked at the contract start; the resolver never silently re-converts.
- Volume tiers apply per billing period; the resolver knows the running count and discounts at boundaries.

## Anti-Patterns

- Pricing logic embedded in the billing consumer. Couples pricing to billing; rule changes require shipping the consumer.
- Vendor cost pass-through at cost (no markup). One bad upstream price hike wipes margin.
- Pricing rule changes without replay analysis. Surprise customer invoices.
- "Bespoke pricing" hard-coded in tenant rows. No version, no audit, no portability.
- FX re-conversion at invoice time. Customer sees a different price than the one shown in-product.
- Volume tier applied per task instead of per period. Either over-discounts (giving cheap rate to first task of month) or under-discounts.
- Intervention credit applied at billing-event time but computed differently from the SLA dashboard. Disputes.

## Outputs

- Price-rule catalogue (YAML + DB).
- Resolver (Python or TS).
- Intervention-credit factor mapping.
- Vendor pass-through formula with markup.
- FX corridor policy.
- Volume-tier engine.
- Replay tool for price-impact analysis.

## Evidence Produced

| Category | Artifact | Format | Example |
|---|---|---|---|
| Architecture | Price-rule schema + catalogue | YAML | `docs/billing/pricing-rules.yaml` |
| Release evidence | Replay analysis on rule change | Markdown | `docs/billing/replays/2026-04-rate-change.md` |
| Operability | Resolver-trace audit log | DB | `pricing_resolutions` |
| Commercial | Public price list per tier | Markdown | `docs/billing/public-prices.md` |

## References

- `references/price-rule-resolver.md` — resolver implementation in Python + TS.
- `references/intervention-credit-logic.md` — light/heavy/user-completed credit mapping.
- `references/vendor-cost-pass-through.md` — markup, FX, threshold rules.
- Companion: `ai-agent-attempted-vs-completed-billing`, `ai-agent-task-success-tracking`, `ai-usage-metering-and-billing`, `ai-cost-per-tenant-attribution`, `software-pricing-strategy`, `subscription-billing`, `stripe-payments`.

<!-- dual-compat-end -->

## §1 Price-Rule Schema

```yaml
rule:
  id: pricing.support_copilot.resolved.pro.usd
  feature: support_copilot
  tier: pro
  region: global             # or 'eu', 'na', 'apac' etc.
  currency: USD
  dimension: resolved_task   # what we charge per
  base_unit_price_cents: 120
  effective_from: 2026-05-01
  effective_to: null          # open-ended; closed when superseded
  volume_tiers:
    - up_to: 100, multiplier: 1.00
    - up_to: 500, multiplier: 0.90
    - up_to: 2000, multiplier: 0.80
    - up_to: null, multiplier: 0.70
  intervention_credit:
    none: 1.00
    light: 0.85
    heavy: 0.30
    user_completed: 0.00
  vendor_pass_through:
    enabled: false        # for hybrid features only; see vendor-cost-pass-through.md
  ttl_advisory_for_engineering: 2026-11-01    # remind us to re-evaluate
  superseded_by: null
  replay_evidence: docs/billing/replays/2026-04-support-copilot.md
```

Rules live in `pricing_rules` table and in a versioned YAML catalogue. Order of resolution:

1. Tenant-specific override in `tenant_pricing_overrides` (bespoke).
2. Per-region, per-tier, per-feature, per-dimension rule.
3. Per-tier, per-feature, per-dimension fallback.
4. Per-feature default.

## §2 Resolver

```python
def resolve(feature, tenant_id, dimension, when, intervention='none',
            running_period_count=None) -> ResolvedPrice:
    tenant = tenants[tenant_id]
    rule = price_rules.find_active(
        feature=feature,
        tier=tenant.plan_tier,
        region=tenant.region,
        currency=tenant.invoice_currency,
        dimension=dimension,
        as_of=when,
    )
    rule = apply_tenant_override(rule, tenant_id, when)

    unit_cents = rule.base_unit_price_cents
    multiplier = volume_tier_multiplier(rule, running_period_count or 0)
    unit_cents = int(round(unit_cents * multiplier))

    intervention_factor = rule.intervention_credit.get(intervention, 1.0)
    final_unit_cents = int(round(unit_cents * intervention_factor))

    return ResolvedPrice(
        unit_price_cents=final_unit_cents,
        currency=rule.currency,
        rule_version=rule.id,
        calculation_trace={
            "base_unit_cents": rule.base_unit_price_cents,
            "volume_multiplier": multiplier,
            "intervention_factor": intervention_factor,
            "running_period_count": running_period_count,
        },
    )
```

Resolver is **pure** (no side effects, no DB writes). The billing consumer persists the resolved price via the calculation trace on the `billing_events` row.

Full implementation in `references/price-rule-resolver.md`.

## §3 Intervention Credit

A heavily-intervened task is not a full agent resolution. The customer pays less.

Defaults from the success contract:

| Intervention | Multiplier |
|---|---|
| none | 1.00 |
| light | 0.85 |
| heavy | 0.30 |
| user_completed | 0.00 (no bill) |

Per-feature overrides in `references/intervention-credit-logic.md`.

## §4 Vendor Cost Pass-Through

For features where the variable cost is dominated by a third-party (e.g., an agent that calls an external paid search API), pricing can be hybrid: a fixed per-resolution base + pass-through of vendor cost with markup.

```
final_price = base + (vendor_cost * (1 + markup_pct))
```

Markup floor (default): 25%. Markup may not drop below 15% without finance sign-off.

Full rules in `references/vendor-cost-pass-through.md`.

## §5 FX Corridor

Each tenant has an `invoice_currency` locked at contract signing. The resolver:

- Never converts to a different currency at billing time.
- Looks up the price rule whose `currency == tenant.invoice_currency`. Each rule may have currency-specific equivalents.
- For new tenants in a not-yet-priced currency, an `fx_corridor` rule converts from a base (USD) using a contract-locked exchange rate, with a quarterly review.

```yaml
fx_corridor:
  base_currency: USD
  contracts:
    - currency: EUR
      rate: 0.92            # 1 USD = 0.92 EUR, locked
      effective_from: 2026-01-01
      effective_to: 2026-12-31
      reviewed_quarterly: true
```

This prevents the customer from seeing a different price each month due to spot-FX movement.

## §6 Volume Tiers

Volume tiers apply per billing period (per tenant). The running count is the tenant's resolved-task count *in the current period* for this feature.

```
TIER             RESOLVED THIS PERIOD       MULTIPLIER
1                up to 100                  1.00
2                101–500                    0.90
3                501–2000                   0.80
4                > 2000                     0.70
```

Important: graduated-style application, not volume-style. Tasks 1–100 are priced at 1.00; tasks 101–500 at 0.90; etc. This matches the customer's intuition of "I bought more, the extras get cheaper" without retroactively re-pricing earlier tasks.

For Stripe Prices: model as graduated tiers on the Price object.

## §7 Anti-Patterns

- Pricing in the consumer. Pricing is its own service.
- Pass-through at cost. Loses margin to upstream price hikes.
- Rule changes without replay. Surprise invoices.
- "Bespoke" hard-coded in app code. Not portable, not auditable.
- FX re-conversion mid-cycle. Customers see drift.
- Volume tier per task instead of per period. Inconsistent customer-side math.
- Intervention credit computed differently from the SLA dashboard. Disputes.
- No `pricing_rule_version` on the billing event row. Future audit fails.


