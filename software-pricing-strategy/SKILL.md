---
name: software-pricing-strategy
description: Pricing strategy for software products and SaaS. Covers value-based pricing,
  the 3 pricing principles, B2B vs B2C differences, pricing models (per-seat, usage,
  freemium, tiered, flat-rate), packaging strategy, negotiation frameworks, discounting...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Software Pricing Strategy

<!-- dual-compat-start -->
## Use When

- Pricing strategy for software products and SaaS. Covers value-based pricing, the 3 pricing principles, B2B vs B2C differences, pricing models (per-seat, usage, freemium, tiered, flat-rate), packaging strategy, negotiation frameworks, discounting...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `software-pricing-strategy` or would be better handled by a more specific companion skill.
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

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
Based on Dash (2025) *Mastering Software Product Management*, Chapter 5: Pricing.

## When to Use

- Setting initial pricing for a new product or SaaS tier
- Redesigning pricing after a period of growth or competitive pressure
- Evaluating whether current pricing is leaving revenue on the table
- Preparing a pricing conversation with a large enterprise customer
- Designing an upgrade path from free to paid

**The core principle of software pricing:** *Pricing is not about offering the cheapest price.
It is about creating a value perception and then claiming your rightful share of that perception.*

A customer who perceives UGX 10,000,000 in value from your product is not harmed by paying
UGX 2,000,000 for it. They capture UGX 8,000,000 in value. Your job is to make the value visible,
quantifiable, and credible — then price accordingly.

---

## 1. The 3 Principles of Software Pricing

Every sustainable software pricing decision satisfies all three conditions simultaneously.

1. **The customer perceives value.** The customer can articulate why the price is worth it.
   If they cannot, the price is wrong — not the product.

2. **The pricing is competitive.** Not cheapest. *Competitive* means your price is defensible
   given what the market offers. Competitors anchor customer expectations; ignore them at your peril.

3. **You do not make a loss.** Price below your cost structure and you fund your own destruction.
   Know your unit economics (see `saas-business-metrics`) before setting price.

*When all three conditions match, you provide the best sustainable price over the long run.*

---

## 2. Value-Based Pricing

Value-based pricing sets price relative to the value delivered to the customer, not relative to
cost or competitor prices.

### Quantifying Customer Value

1. Identify the business outcome your product enables (cost savings, revenue increase, risk reduction,
   time savings, regulatory compliance).
2. Estimate the financial magnitude of that outcome for a typical customer.
3. Set your price as a fraction of that value (typically 10–30%, depending on competition and
   switching costs).

**Example (from Dash, 2025):** A cybersecurity product reduces a bank's data breach exposure from
100M USD to 10M USD, saving 90M USD in potential losses and 900,000 USD in insurance premiums.
A pricing of 100,000–300,000 USD captures 0.1–0.3% of the value delivered. The customer captures
99.7–99.9%. The price is easy to justify.

### Value Drivers for Software

- **Cost reduction:** Fewer staff hours, fewer manual errors, lower infrastructure costs.
- **Revenue enablement:** Faster sales cycles, higher conversion rates, new revenue channels.
- **Risk reduction:** Compliance fines avoided, security breaches prevented, downtime reduced.
- **Time savings:** Hours per user per week × number of users × loaded hourly cost.
- **Strategic value:** Competitive advantage, market speed, customer satisfaction improvements.

*Document the value driver in writing before the pricing conversation. A PM who cannot
articulate value in numbers will lose every pricing negotiation to a procurement department.*

---

## 3. Pricing Models

Choose the model that aligns your revenue growth with your customers' value growth.

### Per-Seat (Per-User) Pricing

Revenue grows as customers add users. Predictable, easy to explain.

**Best for:** Collaboration tools, productivity software, CRMs where every user is an active seat.
**Risk:** Customers avoid adding users to control costs, limiting adoption and value delivery.

### Usage-Based (Consumption) Pricing

Customers pay for what they use: API calls, records processed, GB stored, transactions processed.

**Best for:** Infrastructure, APIs, platforms where usage is a natural proxy for value.
**Risk:** Revenue is unpredictable; customers may reduce usage in cost-cutting cycles.
**Hybrid:** Offer a base commitment + overage pricing to stabilise revenue.

### Freemium

A permanent free tier with reduced functionality. Converts to paid when users hit limits or
need premium features.

**Best for:** Products with viral or network-effect growth potential; B2C or B2SMB markets.
**Risk:** Free users create support cost without revenue. Only sustainable if < 5% of engineering
and support resources serve free users, or if free-to-paid conversion rate > 2–5%.

### Tiered Pricing (Good / Better / Best)

3–4 tiers targeting different customer segments: Starter → Professional → Business → Enterprise.

**Best for:** Most SaaS products. Allows different-sized customers to find appropriate entry points
while creating a natural upgrade path.
**Design rule:** Each tier should increase value delivered by at least 3× relative to cost increase.
If the jump from Starter to Professional is 3× the price, it must deliver > 3× the value.

### Flat-Rate Pricing

One price for unlimited usage, one product configuration.

**Best for:** Simple products with a clearly defined user base; early-stage products where
simplicity reduces friction.
**Risk:** Leaves revenue on the table from large customers; no upgrade path.

### Per-Outcome Pricing

Price tied to a specific measurable outcome: % of revenue generated, % of cost saved.

**Best for:** Products with easily measurable business outcomes; high-trust customer relationships.
**Risk:** Complex to implement; requires instrumentation and trust in measurement.

---

## 4. B2B vs B2C Pricing Differences

| Dimension | B2B | B2C |
|-----------|-----|-----|
| **Decision process** | Multiple stakeholders; economic justification required | Individual impulse or considered purchase |
| **Price transparency** | Often negotiated privately; enterprise quotes | Typically public and fixed |
| **Price sensitivity** | Rational — based on ROI and budget cycles | Emotional and comparative |
| **Volume discounts** | Expected and negotiated | Rarely applicable |
| **Payment terms** | 30–90 day invoicing common | Immediate or monthly subscription |
| **Discounting pressure** | High from procurement departments | Low — take it or leave it |

*In B2B, the person using the product is rarely the person paying for it. Price for the budget
holder's ROI, not the end user's preference.*

---

## 5. Packaging Strategy

Packaging determines *which* features are in *which* tier. Poor packaging reduces willingness
to pay even when pricing is correct.

### Packaging Principles

1. **Put your most valuable feature in the tier you most want customers to buy.**
   Do not bury your best differentiator in the highest tier — that tier will sell poorly.

2. **Design the free or entry tier to create demand for paid, not to satisfy it.**
   The free tier shows value; it does not deliver full value.

3. **Identify your expansion trigger** — the usage or business event that naturally prompts
   a customer to upgrade. Design the tier boundary around that trigger.

4. **Add-ons vs bundling:** Add-ons capture revenue from specific use cases without complicating
   the main pricing table. Bundles simplify the decision and reduce churn by increasing switching cost.

5. **Avoid too many tiers.** More than 4 tiers creates decision paralysis. Hick's Law: the more
   options presented, the longer the decision takes and the higher the abandonment rate.

---

## 6. Negotiation Discipline

### The Discount Anti-Pattern

Discounting trains customers to wait for discounts. A customer who received 20% off last year
will not renew at full price this year. Discount once; discount forever.

### Principled Negotiation Framework

1. **Anchor on value, not price.** "Our product reduces your payroll processing from 3 days to
   4 hours — that is 200 staff-hours per month at your average cost. Our price is a fraction of
   that." The customer who is thinking about value is not thinking about discount.

2. **Trade, do not give.** Every concession must be matched: "I can reduce the price by 15% if
   you commit to a 2-year contract and pay annually upfront."

3. **Know your floor.** Before entering any negotiation, know the minimum price below which the
   deal is unprofitable or sets a dangerous market precedent. Do not cross it.

4. **Silence is a negotiation tool.** After presenting your price, stop talking. The first person
   to speak after a price is stated gives ground.

5. **Say no to deals that destroy value.** A large client at an unprofitable price is worse than
   no deal — they consume disproportionate support and set a low anchor for every future renewal.

---

## 7. Expansion Revenue Design

The most profitable growth in SaaS comes from existing customers. Design for expansion from day one.

### Expansion Levers

| Lever | Mechanism | Example |
|-------|----------|---------|
| **Seat expansion** | More users added as company grows | CRM: new sales reps added each quarter |
| **Usage expansion** | More consumption as product becomes critical | Storage: as data volume grows |
| **Feature upsell** | Customer outgrows current tier | Reporting: basic → advanced analytics |
| **Cross-sell** | Adjacent product or module | HR tool adds payroll module |
| **Multi-year renewal premium** | Reward commitment with lock-in | 2-year deal at 5% premium over monthly |

*Design the product so that success creates expansion. A customer who is winning with your product
naturally grows into higher tiers and more seats.*

---

## 8. Price Change Management

### Rules for Raising Prices

1. Give existing customers 90 days notice minimum.
2. Grandfather existing customers at their current price for 12 months.
3. Communicate the reason: product improvements delivered, cost increases, market alignment.
4. Raise for new customers first; observe churn before applying to existing customers.
5. A price increase that results in < 5% customer loss and > 20% revenue increase was overdue.

---

## Sources

- Dash, S. K. (2025). *Mastering Software Product Management*. Orange Education.

## Cross-References

- **Upstream:** `competitive-analysis-pm` (buyer power and rivalry inform pricing strategy), `saas-business-metrics` (LTV:CAC and unit economics set pricing floor)
- **Downstream:** `it-proposal-writing` (pricing framing in proposals), `software-business-models` (model choice constrains pricing options)
- **Related:** `product-strategy-vision` (pricing signals strategic positioning), `lean-ux-validation` (pricing page A/B testing and willingness-to-pay testing)
