# Vendor Cost Pass-Through

For agent features whose variable cost is dominated by a third-party (paid search APIs, premium data sources, premium LLM models on demand), the pricing model can flow the vendor cost through to the customer with a markup.

## When To Use

Use vendor pass-through when **all** of these hold:

1. The vendor cost per resolution is *highly variable* across customers / use cases (so a flat per-resolution price would be unfair or unsustainable).
2. The vendor cost is *transparent and metered* per task by the gateway (`ai-model-gateway`).
3. The feature's product value is clearly above the bare vendor cost (so we have margin to add).
4. The customer's contract allows pass-through pricing (Pro+ tiers; Free / Starter never).

If the variable cost is small and stable, prefer a flat per-resolution price. Pass-through adds complexity; only adopt when the alternative is worse.

## Formula

```
final_price_cents = base_cents + ceil(vendor_cost_cents * (1 + markup_pct))
```

Where:

- `base_cents` is the fixed per-resolution component (can be 0 in pure pass-through; typically not).
- `vendor_cost_cents` is the actual vendor cost on this resolution (from `ai-cost-per-tenant-attribution`).
- `markup_pct` is the contract markup. Default 25%. Floor 15% (with finance sign-off).

Volume multipliers apply only to `base_cents`, not to `vendor_cost_cents`. Pass-through is at-cost-plus-markup throughout the period.

Intervention credit applies to `base_cents` only by default (per-feature override available). Pass-through cost is the cost regardless of intervention.

## Worked Example

Feature: `research_agent` (calls a paid premium search API).

```
base_cents:         150        ($1.50)
vendor_cost_cents:  47         (this specific task's API spend; from cost attribution)
markup_pct:         0.30       (30%, contract Enterprise)
```

`final = 150 + ceil(47 * 1.30) = 150 + 62 = 212` → $2.12.

If the same task had no intervention and was within volume tier 1 (multiplier 1.00), `final = $2.12`.

If heavy intervention (factor 0.30 on base only): `final = ceil(150 * 0.30) + 62 = 45 + 62 = $1.07`.

## Markup Discipline

| Tier | Default markup | Floor (with finance approval) |
|---|---|---|
| Pro | 30% | 25% |
| Business | 25% | 20% |
| Enterprise | 25% | 15% |

Floors exist because vendor prices change and we need a cushion. A 0% markup is **never** acceptable — that turns a profitable feature into a break-even feature on the first vendor price hike.

## Vendor Price Volatility Protection

Vendors do increase prices. Pass-through with markup absorbs small shocks gracefully:

```
markup decay:
  vendor increase 20% → margin decay (e.g., 30% → 25%, still profitable)
  vendor increase 50% → margin compresses; finance reviews; price re-base
```

Trigger: when the rolling 30d weighted vendor cost increases > 25%, finance opens a price review. Re-base options:
- Increase the markup.
- Increase the base.
- Move customers to a higher-tier model with absorbed cost.

A pure cost-pass-through (markup = 0) would force a customer-facing price increase on every vendor hike. The markup buys time.

## Disclosure on Invoice

Vendor pass-through must be itemized:

```
Agent resolutions – research_agent – 42 tasks                         $63.00
  • Base (42 × $1.50)                                                  $63.00
  • Vendor pass-through (sum of per-task costs × 1.30 markup)          $24.62
                                                            Subtotal   $87.62
```

Some customers will object to seeing the markup. Two answers:
- The markup covers operational risk on vendor pricing.
- We can offer a *flat* per-resolution price as an alternative (with a higher base that internalizes the risk). Their choice.

## FX Considerations

Vendor cost is typically incurred in the vendor's currency (often USD). If the tenant invoice currency is different, the resolver converts the vendor cost using the **same FX corridor** rate as the base price (see SKILL.md §5). Do not use spot-FX mid-period.

```python
def vendor_cost_in_tenant_currency(vendor_cost, vendor_currency, tenant):
    if vendor_currency == tenant.invoice_currency:
        return vendor_cost
    rate = fx_corridor.rate(vendor_currency, tenant.invoice_currency, as_of=tenant.contract_start)
    return int(round(vendor_cost * rate))
```

The contract documents the corridor and the quarterly review cadence.

## Auditability

Every billing event with pass-through stores in its calculation trace:

```json
{
  "base_cents": 150,
  "vendor_cost_cents_raw": 47,
  "vendor_currency": "USD",
  "vendor_cost_cents_converted": 47,
  "markup_pct": 0.30,
  "pass_through_cents": 62,
  "volume_multiplier": 1.00,
  "intervention_factor": 1.00,
  "final_unit_cents": 212
}
```

Customer dispute or finance audit can reach the exact vendor cost from cost attribution within 5 minutes.

## Combining With Volume Tiers

Volume tiers apply to `base_cents`. Pass-through is per-task and not discounted by volume (we pay the vendor full price per task regardless of how many you run).

This is sometimes a source of customer confusion. The invoice disclosure makes it clear: the base discounts; the pass-through does not.

## Special Case: Negative Markup (Loss-Leader)

Some markets justify a negative or zero markup for short periods (introductory pricing, market entry). Allowed only:
- For a fixed-duration period (≤ 6 months).
- With explicit finance + CEO sign-off.
- With an audit row in `pricing_rules` showing the rationale and end date.
- With a public "introductory pricing" notice.

After expiry, the markup defaults to floor; customers receive 60-day advance notice.

## Anti-Patterns

- Pass-through at cost. First vendor hike destroys the unit economics.
- Hiding the markup on the invoice. Customers find out and lose trust; this is a defensive disclosure, not aggressive.
- Volume tier applied to vendor cost. Discounts something we don't control; loses money.
- Mid-period FX re-conversion. Customer sees drift.
- Pass-through enabled by default for all features. Adds complexity where simple flat pricing would do.
- No alert on rising vendor cost. We discover the margin compression at quarter-end, not in real time.
