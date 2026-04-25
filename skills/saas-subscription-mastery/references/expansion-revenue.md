# Expansion Revenue

Expansion — upsell, cross-sell, usage growth — is cheaper than acquisition, compounds faster, and is the only path to net revenue retention (NRR) above 100%. World-class SaaS companies hit 120–140% NRR; public SaaS median hovers near 110%.

## NRR targets

```text
NRR = (Start MRR + Expansion - Contraction - Churn) / Start MRR
```

Benchmark bands:

| NRR | Band | Characterisation |
|---|---|---|
| < 90% | Poor | Business shrinking from the base. |
| 90–100% | Fragile | Net retention negative; new bookings must cover gap. |
| 100–110% | Acceptable | Steady state; SMB median. |
| 110–120% | Strong | Mid-market / enterprise ceiling for most. |
| 120–130% | Excellent | Best-in-class. |
| > 130% | Elite | Typically usage-based products with PLG. |

Also track GRR (Gross Revenue Retention) — the same calculation without expansion. GRR shows base stability; NRR shows total health. GRR < 90% means there's a leak expansion is masking.

## Expansion mechanisms

### Usage-based overage

- Customer pays for a baseline, overage above that.
- Works for API calls, compute, storage, rows processed, transactions, messages.
- Pros: aligned with value, natural expansion, low conversation overhead.
- Cons: unpredictable customer bills, harder to forecast revenue, billing complexity.
- Key mechanics: clear dashboard of usage, alerting when customer approaches limit, easy upgrade path.

### Seats

- Per-user pricing, team grows = bill grows.
- Works for collaboration products (design, comms, project management).
- Pros: simple to understand, predictable.
- Cons: customers share logins to avoid seats (mitigate with activity-based licence audits), caps team growth.
- Key mechanics: self-serve seat adds, automated proration, seat-count dashboard for admins.

### Tiering

- Features, limits, or support level differ between tiers.
- Upgrades triggered by feature need (SSO, audit log, advanced analytics).
- Pros: high-margin, sells well to larger accounts.
- Cons: gates can feel punitive; requires roadmap discipline to keep upper tiers valuable.
- Key mechanics: feature-flag infrastructure, self-serve upgrade, in-app upgrade prompts on gated features.

### Add-ons

- Complementary products or modules. Examples: priority support, advanced reports, sandbox, additional regions.
- Pros: high-attach, frictionless for buyers.
- Cons: fragments pricing page, sales complexity.
- Key mechanics: addable from billing settings, separate SKU, clear value story per add-on.

### Price increases

- Compounding lever for existing customers.
- Grandfather vs migrate decision:
  - **Grandfather** — existing customers keep old price indefinitely. Low churn risk, slow impact.
  - **Grandfather with sunset** — existing customers on old price for N months, then move. Balanced.
  - **Migrate with notice** — all customers move to new price at contract anniversary + 60 days notice. Higher churn risk, fast impact.
- Typical annual price increase: 3–8%. Announce with value recap.

### Multi-year contracts

- Enterprise: 2–3 year deals with annual escalators (5–7%).
- Lock NRR, reduce sales cycle, improve cash flow.
- Downside: harder to reprice during the term.

## Expansion playbook by tier

### SMB self-serve

- In-product upgrade prompts when user hits limits.
- Automated emails when approaching seat / usage thresholds.
- Annual price review with 60-day notice.
- Self-serve add-on shop.

### Mid-market

- Quarterly CSM check-in with usage review.
- Expansion budget from customer's owner / champion.
- Formal QBR (Quarterly Business Review) showing ROI and expansion paths.
- Account plan updated quarterly.

### Enterprise

- Executive sponsor relationship.
- Annual NRR target per account.
- Multi-year renewal + escalator built into contract.
- Cross-sell from product A to product B via integrated bundle.
- Expansion tied to customer's own business growth (seats grow with their headcount).

## Price-increase mechanics

1. Analyse cohort sensitivity to price — historical churn at past price changes.
2. Benchmark willingness-to-pay (5–10 customer interviews).
3. Pick the scope: new customers only, grandfather, migrate with notice.
4. Draft the customer message: reason, value added since last increase, effective date, how to renew at old price if applicable.
5. Sequence: announce 60–90 days out. Press, blog, emails, CSM calls for high-value accounts.
6. Monitor cancel requests daily for the 30 days post-announcement.
7. Offer annual prepay at old price as a save option — converts many would-be cancels.
8. Review churn at 30 / 60 / 90 days post-effective.

## Instrumentation

- Revenue retention dashboard: NRR, GRR, logo retention, by cohort and segment.
- Expansion pipeline alongside new-logo pipeline.
- Feature-gate impression metrics — who hits upgrade prompts, who converts.
- Usage alerts to CSMs: account crossed 80% of plan limit.
- Renewal forecast 90 / 60 / 30 days out with risk and expansion potential flagged.

## Common expansion mistakes

- Treating expansion as sales's job only — CS owns the account, CS sees the signals first.
- No usage-visibility UI — customers don't know they're close to a limit; either overpay silently or hit wall angrily.
- Overly complex pricing — customers can't self-serve expand.
- Raising prices without a value story — sends churn spike.
- Grandfathering forever — legacy customers become a growing deadweight.
- Upsells disconnected from outcomes — "upgrade to Premium" isn't a reason; "save 5 hours per week with automation" is.
- Aggressive auto-upgrades that surprise customers — destroys trust and triggers chargebacks.

## Success metrics

- NRR and GRR (monthly, quarterly cohorts).
- Expansion MRR / ARR.
- Attach rate of add-ons.
- Seat growth rate per account.
- Time from initial contract to first expansion.
- Revenue per logo over time.

## Cross-references

- `pricing-model-decisions.md` — the pricing structure that makes expansion easy.
- `churn-prevention.md` — expansion depends on retention.
- `saas-sales-organization` — who owns expansion, account-management org.
- `metrics-quick-reference.md` — NRR / GRR formulas.
