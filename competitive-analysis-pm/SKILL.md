---
name: competitive-analysis-pm
description: Competitive analysis toolkit for product managers. Covers Porter's Five Forces applied to software product decisions, win/loss analysis, competitor teardown template, market positioning map, Jobs-to-be-Done competitive lens, and Red Ocean vs Blue...
---

# Competitive Analysis for Product Managers

Based on Dash (2025) *Mastering Software Product Management* (Porter's Five Forces applied to PM)
and standard competitive intelligence practice.

## When to Use

- Entering a new market or product category
- Updating a product roadmap with market context
- Preparing for a pricing or packaging decision
- Responding to a new competitor or a competitor's new product
- Conducting a quarterly strategy review

**The PM's role in competitive analysis is not to track competitors obsessively — it is to
understand the structural forces shaping the market and make better product decisions as a result.**

---

## 1. Porter's Five Forces Applied to Software Product Decisions

Michael Porter's Five Forces framework identifies the five structural forces that determine the
profitability and attractiveness of any market. For software PMs, each force translates directly
into a product and strategy decision.

### Force 1 — Competitive Rivalry

*How intense is competition among existing players?*

**High rivalry signals:** Many competitors of similar size; low switching costs; undifferentiated
products; slow market growth forcing competitors to fight for share.

**PM response:**
- Differentiate on dimensions competitors have not invested in (not just features — UX, pricing
  model, onboarding speed, specific industry depth).
- Invest in switching costs: deep integrations, proprietary data formats, workflow habits.
- Avoid feature races — they commoditise every player. Compete on *who you serve best*, not
  on *how many features you have*.

### Force 2 — Threat of New Entrants

*How easily can new competitors enter your market?*

**High threat signals:** Low capital requirements; no regulatory barriers; no network effects;
existing customers are not locked in; technology is replicable.

**PM response:**
- Build a moat early: network effects, proprietary data, ecosystem integrations.
- Increase switching costs before you have to defend against a new entrant.
- Move down-market (into SMB or individual segments) before a new entrant does — new entrants
  typically start there.

### Force 3 — Threat of Substitutes

*Can customers solve their problem without your product category at all?*

**High threat signals:** Customers can achieve the outcome manually (spreadsheets, paper),
with a simpler tool, or with a competitor in an adjacent category.

**PM response:**
- Compete on the job-to-be-done, not on features. Understand what outcome the customer is
  hiring your product to achieve — then make your product the only credible way to achieve it.
- Monitor adjacent categories. A BI tool is not just competing with other BI tools; it is
  competing with Excel, Notion, and a spreadsheet that "already works."

### Force 4 — Buyer Power

*How much leverage do customers have in pricing negotiations?*

**High buyer power signals:** A small number of large customers generate most revenue; customers
are price-sensitive and informed; switching costs are low; products are perceived as commodities.

**PM response:**
- Expand your customer base so no single buyer represents > 20% of revenue.
- Create pricing tiers that reward commitment (annual contracts, volume deals) without
  undermining value perception.
- Build features that make customers more successful — customer success reduces churn and
  reduces buyer leverage in renewal negotiations.
- See `software-pricing-strategy` for detailed pricing responses to buyer power.

### Force 5 — Supplier Power

*How much leverage do your vendors and technology providers have over you?*

**High supplier power signals:** Few alternative vendors; switching vendors is expensive;
suppliers can integrate forward and become competitors; you are dependent on a single cloud
provider, API, or data source.

**PM response:**
- Abstract critical integrations behind an interface layer so providers can be swapped.
- Maintain a "build vs buy vs partner" framework for every critical capability.
- Avoid single-vendor lock-in for infrastructure that would be catastrophically expensive
  to migrate (cloud provider, payment processor, authentication provider).

---

## 2. Win/Loss Analysis Framework

Win/Loss analysis is the most direct source of competitive intelligence available to a PM.

### Data Sources

- Post-sale interviews with won customers: "Why did you choose us over the alternatives?"
- Post-loss interviews with lost prospects: "What made you choose the competitor?"
- Sales team debrief notes (structured template, not anecdotes).
- Churned customer exit interviews: "What caused you to leave?"

### Win/Loss Interview Template

Ask these questions in every post-decision interview:

1. What alternatives did you evaluate before making a decision?
2. What were the top three criteria you used to evaluate options?
3. Which product performed best on each criterion — and why?
4. What almost made you choose the other option?
5. What would have to change for you to consider switching?

### Analysing the Data

- Tag each response with the decision criterion (price, feature, UX, trust, support, integration).
- Track win rate by competitor, by segment, and by deal size.
- A pattern of losses on a single criterion (e.g., pricing) points to a product or go-to-market
  decision, not a sales problem.

---

## 3. Competitor Product Teardown Template

Use this template when evaluating a direct competitor's product.

```
## Competitor: [Name]
**Founded:** [Year] | **Funding/Revenue:** [If known] | **Target Segment:** [Who they serve]

### Positioning
- Tagline / value proposition:
- Primary differentiator (their claimed advantage):
- Weaknesses they do not publicly address:

### Pricing Model
- Structure: [per seat / usage-based / flat rate / freemium]
- Entry price: [lowest paid tier]
- Enterprise price: [if known]
- Free tier: [yes/no — what it includes]

### Feature Comparison
| Capability | Us | Competitor | Gap |
|-----------|----|-----------|----|
| [Feature 1] | | | |
| [Feature 2] | | | |

### UX Assessment
- Onboarding: [Easy / Moderate / Hard — evidence]
- Learning curve: [Low / Medium / High]
- Mobile experience: [Native app / Responsive / None]

### Strengths (honest assessment)
-
-

### Weaknesses (honest assessment)
-
-

### Strategic Threat Level: Low / Medium / High
**Reason:**
```

---

## 4. Market Positioning Map

A 2-axis canvas that visualises where each player in the market sits relative to two dimensions
that matter most to your target customers.

### How to Build It

1. Identify the top two decision criteria for your target segment (e.g., Price vs Depth of Features,
   Ease of Use vs Breadth of Integrations, Industry Specificity vs General Purpose).
2. Plot every significant competitor on the 2×2 grid.
3. Identify the open quadrant — where no strong competitor sits.
4. Ask: Is this quadrant open because no one wants to be there, or because no one has gone there yet?

*The open quadrant is only valuable if customers want to be served there. Confirm with discovery
before positioning your product there.*

---

## 5. Jobs-to-be-Done Competitive Lens

Customers do not buy products — they hire them to do a job. Understanding the job reveals
competitors you might otherwise overlook.

### Framework

1. **What job is the customer trying to get done?** (Functional, emotional, social dimensions.)
2. **What are they currently hiring to do that job?** (This is your real competition — including
   non-consumption, manual workarounds, and adjacent products.)
3. **Why are they dissatisfied with the current hire?**
4. **What would the ideal hire look like?**

**Example:** A school administrator looking for a student performance tracker might currently
"hire" a spreadsheet. The competition is not other performance-tracking software — it is Excel,
teacher intuition, and doing nothing. Winning against Excel requires being dramatically better
at the *job*, not just adding features.

---

## 6. Red Ocean vs Blue Ocean

*From Kim & Mauborgne (2005), referenced in competitive strategy context.*

| | Red Ocean | Blue Ocean |
|--|-----------|-----------|
| **Space** | Known market, defined boundaries | New or uncontested market space |
| **Competition** | Outperform rivals on existing metrics | Make competition irrelevant |
| **Demand** | Fight for existing demand | Create new demand |
| **Value/Cost** | Trade-off (low cost OR differentiation) | Simultaneous value innovation + cost reduction |

**PM application:** Most products start in red oceans. Blue Ocean thinking is useful when:
- Your differentiation is eroding in a crowded market.
- You are building for an underserved segment with no strong incumbent.
- Customer discovery reveals a job-to-be-done that no current product addresses.

*Blue Ocean framing is a strategic lens, not a guarantee. Validate the new space with discovery
before investing in it.*

---

## 7. Competitive Intelligence Ethics

- Never misrepresent yourself to obtain competitor information.
- Do not use confidential information shared by candidates or employees from competitors.
- Rely on public sources: product websites, pricing pages, G2/Capterra reviews, job postings
  (job postings reveal strategic direction), customer case studies, conference talks.
- Treat competitor intelligence as perishable — refresh quarterly.

---

## Sources

- Dash, S. K. (2025). *Mastering Software Product Management*. Orange Education.
- Porter, M. E. (1980). *Competitive Strategy*. Free Press.
- Kim, W. C., & Mauborgne, R. (2005). *Blue Ocean Strategy*. Harvard Business School Press.

## Cross-References

- **Upstream:** `product-strategy-vision` — Five Forces findings feed directly into strategy
- **Downstream:** `software-pricing-strategy` (buyer/rivalry forces drive pricing decisions), `product-discovery` (competitive gaps are discovery opportunities)
- **Related:** `saas-business-metrics` (win rate and churn data are competitive intelligence inputs)
