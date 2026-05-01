# Pricing Model Decisions

Choose the pricing *shape* before setting prices. Shape is the dimensions — flat, seat, usage, tier, hybrid. Levels (the numbers) are tunable; shape is expensive to change.

## The five shapes

### Flat

- Single price, access to the product.
- Easiest to communicate; lowest billing complexity.
- Works for simple single-user or small-team products with little variance in customer size.
- Breaks when customer size varies widely (one customer uses 10x more than another at the same price).

### Per seat

- Price per user (or per active user).
- Best for collaboration products (project mgmt, design, comms, CRM).
- Aligns with team growth; predictable.
- Encourages account-sharing to avoid seats. Mitigate with active-user audits or per-collaborator pricing.

### Usage-based

- Price scales with events, API calls, compute, rows, GB, transactions.
- Aligns with customer value; natural expansion.
- Billing complexity; customer unpredictability; forecasting harder.
- Best for infrastructure, AI APIs, messaging platforms, data products.
- Usually paired with minimum commit or prepaid credits.

### Tiered

- Plans (Starter / Growth / Business / Enterprise) gate features, limits, or support.
- Drives expansion via feature-need triggers (SSO, audit log, advanced analytics).
- Requires roadmap discipline — upper tiers must stay meaningfully better.
- Combine with seat or usage for best effect.

### Hybrid

- Platform fee + usage (common in B2B infra: Twilio, AWS, Segment).
- Seat + usage (Intercom, some analytics).
- Base + add-ons.
- Powerful but complex; customers must be able to predict their bill.

## Patterns by category

| Category | Typical shape |
|---|---|
| Collaboration / productivity | Per seat + tiered |
| CRM / sales tools | Per seat + tiered + add-ons |
| Analytics / BI | Per seat (viewers vs editors) + tiered |
| Infrastructure / platform | Usage + platform fee |
| Messaging / communications | Usage (per message / per minute) |
| AI APIs | Usage (per token / per call) + tiered |
| Payments / billing | Percentage of GMV + platform fee |
| Consumer subscription | Flat or tiered (monthly / annual) |
| Freemium consumer | Tiered (Free / Pro / Family) |
| Vertical SaaS (salon, dental, etc.) | Per location + tiered |
| Marketplace SaaS | Platform fee + transaction % |

## Decision matrix

Score your product 1–5 on each dimension.

| Factor | High score favours |
|---|---|
| Customer-size variance | Usage or seat |
| Collaboration as primary value | Per seat |
| Value = volume (API calls, messages) | Usage |
| Need feature differentiation across segments | Tiered |
| Customers demand predictability | Flat or seat (avoid pure usage) |
| Enterprise procurement sophistication | Hybrid + annual contract |
| Value scales non-linearly with usage | Usage with caps / commits |
| Need for expansion lever | Seat + tiered, or usage |
| Simplicity > optimisation | Flat or single-tier |

## Annual vs monthly

- Default: offer both. Annual with 15–20% discount.
- Annual prepay improves cash flow; reduces churn mechanically (customer must act at renewal, not monthly).
- Monthly attracts SMB / self-serve; annual attracts committed customers.
- For enterprise: annual is standard, multi-year is an expansion lever.

## The too-many-dimensions anti-pattern

Avoid pricing with 4+ active dimensions. Example of bad:

```text
Base = seats * tier_price * region_multiplier
+ usage_over_quota * unit_price
+ optional_modules_selected * module_price
- volume_discount * contract_length_factor
```

Customers can't model their bill. Sales cycles extend. CS gets invoice disputes weekly. Expansion conversations stall.

Rule of thumb: at most two primary dimensions, plus optional add-ons. Everything else should be subsumed into tiers.

## Self-serve vs sales-led pricing

- **Self-serve** — price visible, self-signup, credit card. Max ACV typically 1–10k GBP/year (varies).
- **Sales-led** — "Contact sales" above a threshold; negotiated deals. Typical ACV > 10k GBP/year.
- **Hybrid** — self-serve up to a tier; sales-led for Enterprise. Most SaaS above 5m ARR has this.

When to hide prices: when buyer profile demands procurement, negotiation, or customisation; when legal/regulated; when competitors make price-matching damaging. Otherwise, show prices — opaque pricing kills conversion.

## Willingness-to-pay (WTP) discovery

Quick methods:

- **Van Westendorp Price Sensitivity Meter** — ask at what price the product is too cheap / cheap / expensive / too expensive.
- **Gabor-Granger** — ask willingness to buy at specific prices.
- **Conjoint** — trade-offs between bundles.
- **Interviews** — 10 in-depth conversations beats 100 survey responses in early stage.
- **A/B test on landing page** — only once traffic is meaningful; small samples give noise.

## Discounting discipline

- Discount structure written, not ad hoc. No > 15% discount without manager approval, > 25% without VP.
- Discount for annual prepay, multi-year commit, logo value — not for random requests.
- Never discount without a trade (longer term, case study, reference, expansion commitment).
- Track effective ACV, not list ACV; heavy discounting hides pricing problems.

## Migration to new pricing

Cover in `expansion-revenue.md` for detail, but the shapes to consider:

- New customers on new pricing, grandfather old.
- Grandfather with sunset (N months, then migrate).
- Migrate all at next renewal with 60–90 days notice.
- Offer old-price annual prepay as a save.

## Cross-references

- `freemium-vs-trial.md` — packaging decisions.
- `expansion-revenue.md` — pricing that enables expansion.
- `software-pricing-strategy` — value-based pricing and principles.
- `saas-business-metrics` — ARPU, ACV, pricing-page conversion.
