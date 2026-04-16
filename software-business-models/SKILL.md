---
name: software-business-models
description: Business model frameworks for software companies. Covers products vs
  services vs hybrid models, platform business models, subscription vs perpetual licensing,
  open source strategies, the services-to-product transition, and startup survival...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Software Business Models

<!-- dual-compat-start -->
## Use When

- Business model frameworks for software companies. Covers products vs services vs hybrid models, platform business models, subscription vs perpetual licensing, open source strategies, the services-to-product transition, and startup survival...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `software-business-models` or would be better handled by a more specific companion skill.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Release evidence | Business model decision record | Markdown doc per `skill-composition-standards/references/adr-template.md` covering chosen model (product/service/platform/hybrid) and key assumptions | `docs/business/business-model-adr.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
Based on Cusumano, M. A. (2004). *The Business of Software*. Free Press / Simon & Schuster.

## When to Use

- Choosing a business model for a new software product or company
- Evaluating whether to pivot from services to products (or vice versa)
- Designing a revenue strategy that balances recurring income and services income
- Advising a client on how to position their software business for growth or acquisition
- Deciding whether to open-source part of your technology stack

---

## 1. The Three Business Models

Every software company sits somewhere on a spectrum between two extremes, or tries to occupy
a hybrid position.

### Model A — Pure Products

Sell software licences or subscriptions with minimal human services involvement.

**Characteristics:**
- Revenue is recurring and scalable; marginal cost per additional customer is near zero.
- High upfront investment in R&D; long payback period.
- Success requires large markets and strong distribution.
- Gross margins: 70–90%.

**When it works:** When the problem is common enough that one solution serves thousands of
customers with minimal customisation; when distribution can scale without proportionally
scaling headcount.

**Examples:** Microsoft Office, Salesforce CRM (standard tiers), Slack, GitHub.

**Risks:** Competition can commoditise the product; without services, customer success is
entirely dependent on product quality. Churn is invisible until the renewal conversation.

### Model B — Pure Services

Deliver value through human expertise: custom development, consulting, integration, managed services.

**Characteristics:**
- Revenue scales linearly with headcount; gross margins 20–40%.
- Lower risk than products — you are paid before you build.
- Highly cash-generative in early stages.
- Ceiling: headcount limits growth; difficult to scale without sacrificing quality.

**When it works:** When each customer's problem is sufficiently unique to require bespoke work;
when relationships and domain expertise are the primary value (not replicable code).

**Examples:** Custom software houses, IT consultancies, system integrators, implementation partners.

**Risks:** Revenue is non-recurring; key-person dependency; no compounding advantage over time.

### Model C — Hybrid (Products + Services)

Combine a software product with services that accelerate adoption, customise the product, or
extend its value.

**Characteristics:**
- Product provides recurring revenue floor; services provide growth revenue ceiling.
- Gross margins: 50–70% blended.
- Services can fund product R&D in early stages.
- Risk: Services can cannibalise product investment if not actively managed.

**When it works:** For enterprise software where standardised software meets 80% of need and
services fill the remaining 20%; when implementation complexity requires expert guidance.

**Examples:** SAP, Oracle, Workday (product + implementation services), Salesforce + consulting
partners, most African enterprise software companies.

---

## 2. The Services-to-Products Transition

The most dangerous and most valuable journey in software business is transitioning from a
services company to a products company.

### Why It Is Attractive

- Products scale without proportional headcount growth.
- Recurring revenue is more predictable and more valuable at acquisition.
- Product IP is defensible; services expertise walks out the door.

### Why It Is Hard

- Services revenue pays salaries now; product revenue pays future salaries.
- The incentive is to take every services engagement, even those that compete with product investment.
- Services customers want customisation; products require standardisation. These forces are opposed.

### Cusumano's Transition Framework

1. **Identify the repeatable core.** Look for the service you deliver repeatedly with the same
   approach. That pattern is the product kernel.
2. **Build the product alongside services, not instead of services.**
   Use services revenue to fund product R&D. Do not cut services before the product generates
   comparable revenue.
3. **Set a explicit product revenue target.** "When product revenue reaches 40% of total revenue,
   we begin to decline new bespoke services engagements."
4. **Create separation.** Separate the services team from the product team to prevent services
   pressure from reshaping the product roadmap.
5. **Sign reference customers on the product.** Get 3–5 customers to use the standardised product
   before building more custom features. Their success stories are the proof the market needs.

---

## 3. Platform Business Models

A platform creates value by facilitating interactions between two or more distinct user groups
(producers and consumers). The platform does not own the value created — it enables it.

### Two-Sided Platform Mechanics

- **Network effects:** Each additional participant increases the platform's value for all
  participants. Facebook is worthless with 10 users; invaluable with 1 billion.
- **Cross-side network effects:** More sellers attract more buyers; more buyers attract more sellers.
- **Same-side network effects:** More developers on a platform makes it more attractive to other
  developers (more libraries, tools, and shared knowledge).

### The Cold Start Problem

A platform with no participants on either side has zero value. Strategies to solve it:

- **Seed one side:** Acquire sellers/producers with subsidies, partnerships, or direct recruitment
  before launching to buyers/consumers.
- **Single-player mode:** Design the product so it delivers value to one user before the network
  exists. Dropbox was valuable to a single user (storage) before it had any network effect (sharing).
- **Constrained launch:** Launch in a single city, university, or industry vertical. Build density
  before breadth.

### Platform Governance

Once a platform reaches scale, governance becomes the hardest problem:
- Who is allowed to participate?
- What can participants build or sell on the platform?
- How are disputes between participants resolved?
- How does the platform extract revenue without undermining participant trust?

*A platform that extracts too much revenue from its ecosystem destroys the ecosystem that
makes it valuable. See Apple/Epic, Amazon Marketplace, and Google Play controversies.*

---

## 4. Licensing Models

### Perpetual Licence

Customer pays once for the right to use the software version purchased. Optional annual
maintenance fee (typically 18–22% of licence price) for updates and support.

**Pros:** Large upfront cash inflows; customers feel ownership.
**Cons:** Revenue is lumpy and non-recurring; customers stay on old versions to avoid upgrade costs;
support burden grows as version fragmentation increases.

*Perpetual licences are declining. Most software companies have migrated or are migrating to
subscription models.*

### Subscription

Customer pays a recurring fee (monthly or annual) for access to the latest version plus support.

**Pros:** Predictable recurring revenue; customers are always on the latest version; natural
customer success touchpoints at renewal.
**Cons:** Customers can cancel at any time; cash flow ramps slowly compared to perpetual upfront payments.

**Rule:** Annual subscriptions paid upfront are strongly preferable to monthly subscriptions.
They reduce churn, improve cash flow, and increase LTV:CAC ratios.

---

## 5. Open Source Strategies

Open source is a go-to-market strategy, not a charitable act.

### Open Core Model

The core product is open source (free, community-maintained). Advanced features — enterprise
authentication, compliance tools, admin controls, SLA support — are proprietary and paid.

**Examples:** GitLab, HashiCorp Vault, Elasticsearch (before Elastic re-licenced), MongoDB Community.

**Why it works:** The open source core builds trust, community, and distribution at near-zero
marketing cost. Enterprise features monetise the segment that can pay.

**Risk:** The boundary between open core and proprietary features must be drawn carefully.
Too little open source and the community does not form. Too much open source and there is
nothing to sell.

### Open Source as Distribution

Release the product freely to build adoption, then monetise with hosting, support, or enterprise
services. The product itself is the marketing.

**Examples:** Linux (Red Hat), WordPress (Automattic/WP Engine), Android (Google services).

### When NOT to Open Source

- Your competitive advantage is the code itself (not the distribution or the brand).
- You have not yet found product/market fit — open sourcing before validation disperses attention.
- Your team cannot manage a community in addition to product development.

---

## 6. Startup Survival Patterns

From Cusumano's analysis of software startup outcomes:

### The 5 Essential Elements of a Software Startup

1. **Founders who understand both technology and business.** Pure technologists build great
   demos; pure business people build great decks. You need both in the founding team.

2. **A product that solves a real, painful problem.** Not a problem the founders find interesting —
   a problem a specific set of customers would pay to solve today.

3. **A go-to-market motion that matches the product.** Enterprise software requires direct sales.
   Consumer software requires viral growth or performance marketing. The wrong motion burns runway
   without traction.

4. **Unit economics that work at scale.** A business that loses money on every customer does not
   become profitable at volume — it loses money faster. Validate unit economics at 100 customers,
   not 10,000.

5. **A business model that generates recurring revenue.** One-off project revenue is a consulting
   business. A scalable software company needs recurring, compounding revenue.

### The Cash Flow Trap

Services revenue is cash-generative now. Product revenue is cash-generative later. Many software
companies delay the product transition because services cover payroll. The correct response:

- Set a 3-year product revenue target with quarterly milestones.
- Ring-fence a product development team that is not pulled into services engagements.
- Raise external capital if necessary to fund the transition without starving the product.

---

## 7. Choosing Your Business Model

Use this decision framework:

```
1. Is your solution standardisable?
   → Yes: Products or Hybrid
   → No (each customer is unique): Services

2. How large is your target market?
   → Large (> 1,000 potential customers with similar problems): Products or SaaS
   → Small or niche (< 100 customers, high willingness to pay): Services or Hybrid

3. What are your capital constraints?
   → Low capital, need early revenue: Services first, product over time
   → External capital available: Product from day one

4. What is your competitive moat?
   → Code and data: Products
   → Network effects: Platform
   → Domain expertise and relationships: Services or Hybrid
   → Distribution: Open Source as distribution tool
```

---

## Sources

- Cusumano, M. A. (2004). *The Business of Software: What Every Manager, Programmer, and
  Entrepreneur Must Know to Thrive and Survive in Good Times and Bad.* Free Press.

## Cross-References

- **Upstream:** `product-strategy-vision` (strategy determines which model to pursue), `competitive-analysis-pm` (market structure influences model viability)
- **Downstream:** `software-pricing-strategy` (model choice constrains pricing options), `saas-business-metrics` (metrics differ by model), `it-proposal-writing` (services model requires winning proposals)
- **Related:** `multi-tenant-saas-architecture` (SaaS product model architecture), `modular-saas-architecture` (product extensibility for hybrid models)
