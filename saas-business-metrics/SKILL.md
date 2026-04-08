---
name: saas-business-metrics
description: Complete SaaS metrics framework covering revenue (MRR/ARR/ARPU), growth (CAC/LTV/payback), retention (churn/NRR/GRR), engagement, customer satisfaction (NPS/CSAT/CES), unit economics, the Rule of 40, and SaaS finance basics. Use when measuring...
---

# SaaS Business Metrics

Based on *A Quick Guide to Software as a Service* (Indocan Publications, 2022)
and Dash (2025) *Mastering Software Product Management*.

## When to Use

- Establishing a metrics dashboard for a new SaaS product
- Diagnosing why growth has stalled or churn has increased
- Preparing a board deck or investor update
- Setting measurable Key Results for product team OKRs
- Evaluating the health of a product before a pricing or packaging change

**The first principle of SaaS metrics:** Measure outcomes, not activities. The number of features
shipped, lines of code written, or support tickets closed are activities. MRR growth, churn rate,
and NPS are outcomes.

---

## 1. Revenue Metrics

### Monthly Recurring Revenue (MRR)

MRR = Sum of all normalised monthly subscription revenue from active customers.

- **New MRR:** Revenue from customers acquired this month.
- **Expansion MRR:** Additional revenue from existing customers (upgrades, add-ons, seat additions).
- **Contraction MRR:** Revenue lost from existing customers (downgrades, seat reductions).
- **Churned MRR:** Revenue lost from customers who cancelled entirely.
- **Net New MRR** = New MRR + Expansion MRR − Contraction MRR − Churned MRR

*A healthy SaaS business has Expansion MRR > Churned MRR (negative net churn).*

### Annual Recurring Revenue (ARR)

ARR = MRR × 12. Used for annual planning, valuations, and investor reporting.

*Only include recurring subscription revenue. One-off implementation fees and professional
services revenue are excluded from ARR.*

### Average Revenue Per User (ARPU)

ARPU = MRR ÷ Total Active Customers

- Rising ARPU indicates successful upselling or movement upmarket.
- Falling ARPU indicates a shift toward smaller customers or aggressive discounting.

---

## 2. Growth Metrics

### Customer Acquisition Cost (CAC)

CAC = Total Sales & Marketing Spend (period) ÷ New Customers Acquired (period)

- Calculate separately for each acquisition channel (paid, organic, referral, outbound).
- Include fully-loaded cost: salaries, tools, agency fees, and ad spend.

### CAC Payback Period

CAC Payback = CAC ÷ (ARPU × Gross Margin %)

- Measures how many months of revenue are needed to recover the cost of acquiring one customer.
- Target: < 12 months for self-serve SaaS; < 18 months for enterprise SaaS.
- > 24 months payback is a warning sign — the business is burning cash to grow.

### Customer Lifetime Value (LTV / CLV)

LTV = ARPU × Gross Margin % × Average Customer Lifetime

Average Customer Lifetime (months) = 1 ÷ Monthly Churn Rate

**Example:** ARPU = UGX 150,000/month; Gross Margin = 70%; Monthly Churn = 2%
- Average Lifetime = 1 ÷ 0.02 = 50 months
- LTV = 150,000 × 0.70 × 50 = UGX 5,250,000

### LTV:CAC Ratio

LTV:CAC = LTV ÷ CAC

| Ratio | Interpretation |
|-------|---------------|
| < 1:1 | Destroying value — each customer costs more than they will ever generate |
| 1:1 – 3:1 | Marginal — sustainable only if growth is very fast |
| 3:1 | Healthy benchmark for established SaaS |
| > 5:1 | Strong — may indicate underinvestment in growth (room to spend more on acquisition) |

---

## 3. Retention Metrics

Retention is the most important SaaS metric. Acquisition without retention fills a leaky bucket.

### Logo Churn Rate (Customer Churn)

Logo Churn = Customers Lost ÷ Customers at Start of Period

**Monthly target:** < 2% for B2B SaaS; < 5% for B2C SaaS.

### Revenue Churn Rate

Revenue Churn = MRR Lost from Churned + Contracted Customers ÷ MRR at Start of Period

Revenue churn is more important than logo churn when customers have different-sized contracts.

### Net Revenue Retention (NRR)

NRR = (Starting MRR + Expansion MRR − Contraction MRR − Churned MRR) ÷ Starting MRR × 100%

| NRR | Interpretation |
|-----|---------------|
| < 100% | Business shrinks even without losing a single customer |
| 100% | Flat — churn exactly offset by expansion |
| > 100% | Negative churn — existing customers generate more revenue than you lose |
| > 120% | World-class — seen in top enterprise SaaS companies |

### Gross Revenue Retention (GRR)

GRR = (Starting MRR − Contraction MRR − Churned MRR) ÷ Starting MRR × 100%

GRR excludes expansion revenue. It measures purely how well you retain existing revenue.
GRR can never exceed 100%.

---

## 4. Engagement Metrics

### DAU / MAU Ratio (Stickiness)

Stickiness = Daily Active Users ÷ Monthly Active Users

- > 20%: Good engagement for most B2B tools.
- > 50%: Exceptional — product is used daily by most monthly users (messaging, task management).
- Benchmark against your product category, not the global average.

### Feature Adoption Rate

Feature Adoption = Users who used feature at least once ÷ Total Active Users

- Tracks whether discovery is translating to usage.
- Low adoption on a high-investment feature is a strong signal to investigate (usability problem,
  awareness problem, or wrong feature for the market).

### Time-to-First-Value (TTFV)

The elapsed time from account creation to the moment a new user experiences the core value of
the product. Minimising TTFV is the single most impactful lever for improving early retention.

---

## 5. Customer Satisfaction Metrics

### Net Promoter Score (NPS)

NPS asks one question: "On a scale of 0–10, how likely are you to recommend [product] to a
colleague?"

- **Promoters (9–10):** Loyal advocates. They generate referrals.
- **Passives (7–8):** Satisfied but indifferent. Vulnerable to competitor offers.
- **Detractors (0–6):** Unhappy customers. At risk of churning and leaving negative reviews.

NPS = % Promoters − % Detractors

| NPS Range | Benchmark |
|-----------|----------|
| < 0 | Poor — more detractors than promoters |
| 0–29 | Average |
| 30–69 | Good |
| ≥ 70 | World-class |

*Always follow up NPS with an open-ended "Why did you give that score?" NPS alone tells you
what; the open question tells you why.*

### Customer Satisfaction Score (CSAT)

CSAT asks: "How satisfied were you with [interaction/product]?" on a 1–5 or 1–10 scale.
Calculated as % of respondents who gave a positive score (4 or 5 on a 5-point scale).

CSAT is transactional (measures a specific interaction). NPS is relational (measures overall loyalty).

### Customer Effort Score (CES)

CES asks: "How easy was it to [complete the task]?" on a 1–7 scale.

Low effort = high loyalty. CES is the strongest predictor of customer churn in support contexts.
Every time a customer must work hard to use your product, churn probability increases.

---

## 6. Unit Economics

Unit economics measure the per-customer profitability of the business model.

### Gross Margin

Gross Margin % = (Revenue − Cost of Goods Sold) ÷ Revenue × 100%

For SaaS, COGS includes: hosting, third-party APIs, customer support costs directly tied to
delivering the service. It does not include sales, marketing, or R&D.

**Healthy SaaS Gross Margin:** 70–85%. Below 60% indicates a services-heavy model or
infrastructure inefficiency.

### Contribution Margin

Contribution Margin = Revenue − Variable Costs (per customer)

Used to evaluate whether adding one more customer increases or decreases profitability.

---

## 7. The Rule of 40

A single metric used to evaluate the overall health of a SaaS business.

**Rule of 40 Score = Revenue Growth Rate % + Profit Margin %**

Where Profit Margin is typically measured as EBITDA margin or Free Cash Flow margin.

| Score | Interpretation |
|-------|---------------|
| < 20 | Concern — either growth is slow or the business is burning cash unsustainably |
| 20–40 | Acceptable for early-stage; concerning for mature SaaS |
| ≥ 40 | Healthy — used by investors as a benchmark for SaaS quality |
| > 60 | Exceptional |

**Example:** 60% revenue growth rate + (−15%) EBITDA margin = 45. Healthy.
**Example:** 10% revenue growth rate + 5% EBITDA margin = 15. Concerning.

*The Rule of 40 is an investor heuristic, not an operational target. Use it for external
communication and strategic health checks, not for weekly product decisions.*

---

## 8. SaaS Finance Basics

### Bookings vs Billings vs Revenue

| Term | Definition |
|------|-----------|
| **Bookings** | Total contract value signed (including future periods not yet billed) |
| **Billings** | Cash invoiced to customers in the period |
| **Revenue** | Cash recognised under accounting rules (deferred for prepaid annual contracts) |

*An annual contract signed in December is a Booking and a Billing, but only 1/12 is recognised
as Revenue in December.*

### Deferred Revenue

When a customer pays for a 12-month subscription upfront, the unearned portion sits on the
balance sheet as Deferred Revenue. It is a liability (you owe the service), not income.
As each month passes, 1/12 is recognised as Revenue.

---

## 9. Metrics Hierarchy and Anti-Patterns

### Leading vs Lagging Indicators

| Type | Characteristic | Examples |
|------|---------------|---------|
| **Lagging** | Confirms what happened; cannot be acted on in real time | MRR, ARR, Churn Rate |
| **Leading** | Predicts future outcomes; actionable now | TTFV, Feature Adoption, Onboarding Completion |

Build your operational dashboard around leading indicators. Report lagging indicators to
leadership and investors.

### Vanity Metrics to Avoid

| Vanity Metric | Why It Is Misleading |
|--------------|---------------------|
| Total registered users | Includes inactive accounts; inflates perceived traction |
| App downloads | Tells you nothing about usage or retention |
| Page views | Traffic without conversion is not a business |
| Features shipped | Output metric; does not measure customer or business outcome |
| Support tickets closed | Closing tickets faster does not mean fewer problems |

### The Metric Gaming Anti-Pattern

If a metric is used as a performance target, it will be gamed. (Goodhart's Law.)
Pair every KPI metric with a counter-metric to detect gaming.

**Example:** Pair "Average ticket close time" with "Customer re-open rate."
If close time drops and re-open rate rises, support agents are closing tickets prematurely.

---

## Sources

- Indocan Publications (2022). *A Quick Guide to Software as a Service (SaaS): Beginner Insight.*
- Dash, S. K. (2025). *Mastering Software Product Management*. Orange Education.

## Cross-References

- **Upstream:** `product-strategy-vision` (OKR Key Results should be drawn from leading metrics)
- **Downstream:** `software-pricing-strategy` (MRR and churn data drive pricing decisions)
- **Related:** `competitive-analysis-pm` (win rate and churn by segment are competitive intelligence), `lean-ux-validation` (metrics design for UX experiments)
