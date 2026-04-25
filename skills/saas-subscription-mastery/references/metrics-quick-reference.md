# Subscription Metrics Quick Reference

Formulas and target bands. For the full framework — inputs, pitfalls, dashboard design — see `saas-business-metrics`.

British English convention: use consistent period (monthly or annual), one currency, and disclose cohort basis.

## Revenue

### MRR (Monthly Recurring Revenue)

```text
MRR = sum of (active subscription monthly amounts)
```

- Include: subscription fees, seat fees, recurring add-ons.
- Exclude: one-time setup, services, non-recurring overages (debatable — track separately as "usage MRR").
- Decompose: New MRR + Expansion MRR - Contraction MRR - Churn MRR = Net New MRR.

### ARR (Annual Recurring Revenue)

```text
ARR = MRR * 12
```

- Only meaningful if customer contracts support it (annual commits, stable MRR base).
- Prefer ARR for enterprise SaaS, MRR for monthly-billed SMB.

### ARPU (Average Revenue Per User/Account)

```text
ARPU = MRR / active_accounts
```

- At account level is more useful than at user level for B2B.
- Rising ARPU + flat account count = successful expansion or upsell.
- Falling ARPU = discounting, downgrades, or SMB mix shift.

### ACV (Annual Contract Value)

```text
ACV per customer = annualised contract amount (single year basis)
```

- Used in sales forecasting and CAC payback calculations.
- Total Contract Value (TCV) = ACV * years + one-time fees (not the same as ACV).

## Retention

### Gross Revenue Retention (GRR)

```text
GRR = (Start MRR - Churn MRR - Contraction MRR) / Start MRR
```

- Ceiling is 100% (no expansion counted).
- Target bands: 80–85% SMB, 90%+ mid-market, 95%+ enterprise.
- Shows base stability without expansion masking.

### Net Revenue Retention (NRR)

```text
NRR = (Start MRR - Churn MRR - Contraction MRR + Expansion MRR) / Start MRR
```

- Can exceed 100% (negative net churn).
- Target bands: 100–110% acceptable, 110–120% strong, 120%+ excellent, 130%+ elite.

### Logo churn (customer churn)

```text
Logo churn = customers_lost_in_period / customers_at_start_of_period
```

- Different from revenue churn; a product can have 5% logo churn and 2% revenue churn if departing customers are small.
- Track monthly for SMB, quarterly / annually for enterprise.

### Revenue churn

```text
Revenue churn = Churn MRR / Start MRR
```

- Negative revenue churn = expansion exceeds churn and contraction.

## Unit economics

### CAC (Customer Acquisition Cost)

```text
CAC = sales_and_marketing_spend / new_customers_acquired
```

- Include: salaries, commissions, ad spend, tools, events, agencies.
- Exclude: customer success (that's retention), brand-only ROI (hard to attribute).
- Blended CAC vs paid CAC: track both; paid is tunable, blended is honest.
- Segment by channel and persona.

### LTV (Lifetime Value)

Basic form:

```text
LTV = ARPU * gross_margin / customer_churn_rate
```

More accurate (NRR-weighted):

```text
LTV = ARPU * gross_margin / (1 - NRR_retention_rate)
```

- Use net revenue retention in the denominator when NRR > 100% (expansion extends customer lifetime value).
- Cap the lifetime assumption at 3–5 years for conservatism; "infinite LTV" from NRR > 100% is arithmetically true but strategically naive.

### LTV : CAC

```text
LTV : CAC ratio
```

- Target: > 3 healthy, > 5 excellent.
- Below 1: losing money on every customer.
- Above 10: likely underinvesting in growth.

### CAC payback

```text
CAC payback = CAC / (ARPU * gross_margin per month)
```

- Target: < 12 months healthy, < 18 months acceptable, > 24 months alarming.
- Enterprise tolerates longer payback because retention is higher.
- SMB self-serve should be < 9 months.

## Growth health

### Quick Ratio

```text
Quick Ratio = (New MRR + Expansion MRR) / (Churn MRR + Contraction MRR)
```

- Target: > 4 healthy (growth 4x faster than losses).
- Below 1: shrinking.
- 1–4: growing but inefficient.
- Indicator of engine efficiency; early warning when it drops even if top-line still grows.

### Rule of 40

```text
Rule of 40 = YoY revenue growth % + operating margin %
```

- Target: >= 40%.
- Early stage: 50–80% growth -20% margin can still pass.
- Mature SaaS: 20% growth + 20% margin = 40%, passing.
- Used by investors to balance growth vs profitability.

### Burn multiple

```text
Burn multiple = net_burn / net_new_ARR
```

- < 1 excellent, 1–2 good, 2–3 mediocre, > 3 poor.
- Capital efficiency; dominant metric in fundraising from 2023 onward.

## Engagement (non-revenue but critical)

### DAU / MAU

```text
DAU / MAU ratio
```

- 20%+ = habitual use.
- 50%+ = rare / exceptional.
- B2B products used daily-by-role: 40–70% is normal.

### Activation rate

```text
Activation rate = activated_users / signed_up_users
```

- Define activation via cohort analysis (see `retention-point.md`).
- Target bands depend on product; set your own baseline.

## Cash flow

### CAC recovery via annual prepay

- Annual prepay customers have CAC recovered on day 1 of contract (cash basis).
- Accounting basis: recognise revenue monthly; cash is received upfront.
- Huge working-capital benefit; SaaS scales on this mechanic.

### Deferred revenue

```text
Deferred revenue = cash_received - revenue_recognised_to_date
```

- Liability on balance sheet until earned.
- Growing deferred revenue alongside cash = healthy annual-prepay business.

## Reporting cadence

| Metric | Review cadence |
|---|---|
| MRR / ARR, churn, NRR, GRR | Weekly ops review |
| CAC, LTV, payback | Monthly exec review |
| Quick Ratio, Rule of 40, burn multiple | Monthly / quarterly board review |
| Cohort curves | Monthly |
| Activation rate | Weekly by cohort |
| DAU/MAU | Weekly product review |

## Common mistakes

- Conflating bookings with revenue.
- Counting services / one-time fees in MRR.
- Not separating new vs expansion vs churn MRR (the decomposition is where insight lives).
- Single-number LTV without gross margin.
- LTV:CAC ratio presented without CAC payback (they can disagree).
- Annualised metrics compared against companies reporting differently.
- Using list ACV instead of effective ACV after discounts.

## Cross-references

- `saas-business-metrics` — the full framework.
- `expansion-revenue.md` — NRR / GRR detail.
- `churn-prevention.md` — churn-metric interpretation.
- `retention-point.md` — activation-metric definition.
