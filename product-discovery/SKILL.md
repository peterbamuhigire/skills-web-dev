---
name: product-discovery
description: Structured product discovery process before building. Covers the 4 product
  risks, opportunity assessment, customer discovery programs, prototype spectrum,
  demand/value/feasibility testing, and discovery sprints. Use when evaluating whether
  an...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Product Discovery

<!-- dual-compat-start -->
## Use When

- Structured product discovery process before building. Covers the 4 product risks, opportunity assessment, customer discovery programs, prototype spectrum, demand/value/feasibility testing, and discovery sprints. Use when evaluating whether an...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `product-discovery` or would be better handled by a more specific companion skill.
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
| Release evidence | Product discovery report | Markdown doc covering the 4 product risks, opportunity assessment, and customer-discovery findings per feature | `docs/product/discovery-2026-04-16.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
Based on Cagan (2017) *INSPIRED: How to Create Tech Products Customers Love*, 2nd ed.

## When to Use

- Evaluating a new product idea or market opportunity
- De-risking a major feature before it enters the backlog
- Deciding whether to pivot or persevere on an existing product
- Running a time-boxed discovery sprint with a cross-functional team

**The core discipline:** *Separate discovery (figuring out what to build) from delivery (building it).
Discovery is how you avoid building the wrong thing. Discovery is not optional for competitive products.*

---

## 1. The 4 Product Risks

Every product must clear all four risks before committing to full delivery.

| Risk | Question | Validated By |
|------|----------|-------------|
| **Value** | Will customers choose to use or buy this? | Demand tests, qualitative interviews |
| **Usability** | Can customers figure out how to use it? | Usability testing on prototypes |
| **Feasibility** | Can we build it with our current team, tech, and time? | Engineering spike, feasibility prototype |
| **Business Viability** | Does this work for our business (legal, financial, marketing, sales)? | Stakeholder review |

*Never hand work to engineering with unresolved value or feasibility risk.* One week of discovery
prototyping routinely saves months of misdirected development.

---

## 2. Opportunity Assessment

Before committing to discovery, frame the opportunity with four questions (replaces a traditional
product requirements document at the discovery stage).

1. **Business Objective** — What business result does this tie to? (Maps to an OKR or strategic goal.)
2. **Key Results** — How will we know this succeeded? Define the specific, measurable outcome.
3. **Customer Problem** — What problem does this solve for the customer? (Not a solution statement.)
4. **Target Market** — Which specific customer segment has this problem most acutely?

*If you cannot answer all four, the opportunity is not ready for discovery investment.*

---

## 3. Customer Discovery Program

The goal is to recruit 6 reference customers — real users who will use your product from day one
and whose endorsement you can cite when selling to others.

### Requirements for Reference Customers

- They must be in your single, specific target market (not scattered segments).
- They must test your actual product (not a slide deck or whitepaper).
- They must be willing to recommend the product to peers after launch.

### Process

1. Define your single target market segment precisely.
2. Recruit 6 prospective reference customers before writing significant code.
3. Give them early access to prototypes; gather direct, honest feedback.
4. Iterate on the product until all 6 are genuinely enthusiastic — not just polite.
5. These 6 become your launch references, beta testers, and case study sources.

*A single target market is not a limitation — it is a requirement for focus. Trying to be everything
to everyone in discovery produces a product that is nothing to no one.*

---

## 4. Discovery Framing Techniques

Use these at the start of discovery to align the team before generating solutions.

### Customer Letter Technique
Write the press release announcing the product — from the customer's point of view — *before*
building it. Forces the team to articulate customer value in plain language. If you cannot write
this letter compellingly, the opportunity is not yet well understood.

### Story Map Technique
Map the end-to-end customer journey as a 2D grid: user tasks across the top (time axis),
story details beneath each task. Reveals gaps in coverage, prioritisation candidates, and
the MVP slice (the horizontal cut that delivers a complete but minimal journey).

### Startup Canvas Technique
Rapid one-page framing: Problem, Solution, Key Metrics, Unique Value Proposition, Channels,
Customer Segments, Cost Structure, Revenue Streams. Use for new product lines or pivots.

---

## 5. Discovery Planning Techniques

### Customer Interviews
The single most important and most misused discovery tool.

**Rules:**
- Interview in the customer's environment, not a conference room.
- Ask about the past (what they actually do today), not the future (what they wish they had).
- Never describe your solution during a discovery interview — you will bias every answer.
- Ask "why" at least three times before accepting any answer as the real motivation.
- Target: 6–12 interviews per discovery cycle before drawing conclusions.

### Concierge Test Technique
Do the job manually for the customer before building the software. If you cannot do it manually
for 5 customers, you do not yet understand the problem well enough to build it.

---

## 6. Prototype Spectrum

Prototypes are learning tools, not deliverables. Build the cheapest prototype that answers
the specific risk question. Never gold-plate a discovery prototype.

| Prototype Type | Purpose | Risk Addressed | Fidelity |
|---------------|---------|----------------|---------|
| **Feasibility Prototype** | Prove a technical approach is buildable | Feasibility | Low (code spike) |
| **User Prototype** | Test usability and user flow | Usability, Value | Low-Medium (click-through) |
| **Live-Data Prototype** | Test with real data at small scale | Value, Feasibility | Medium-High |
| **Hybrid Prototype** | Combines manual + automated to simulate full product | All 4 risks | Varies |

*A Figma click-through costs 1 hour and answers usability questions that 2 weeks of engineering
cannot answer. Build the prototype first.*

---

## 7. Testing Techniques

### Testing Value — Demand

Use before building to verify customers want the solution enough to act.

- **Fake Door / 404 Test:** Add a button or menu item for the non-existent feature. Count clicks.
  If the users requesting the feature most loudly will not click a stub, do not build it.
- **Landing Page Test:** Build a one-page site describing the product. Measure sign-up or
  pre-order conversion against a defined threshold before committing to build.
- **Customer Discovery Program:** Reference customer agreement is the ultimate demand proof.

### Testing Value — Qualitative

- Run a usability test but also ask the participant to complete a specific value-laden task
  (e.g., complete a purchase, submit a report, onboard a new team member).
- Observe whether the participant reaches the value moment without assistance.
- Ask: "Would you pay for this? What would make you not pay for it?"

### Testing Value — Quantitative

- **A/B Test:** Only valid when you have sufficient traffic (typically >1,000 users per variant).
  Tests *what* performs better, not *why*. Pair with qualitative research.
- **Invite-Only Test:** Release to a small cohort; measure activation and retention rates
  against a defined threshold before rolling out broadly.

### Testing Feasibility

Engineering lead runs a technical spike (time-boxed prototype) to validate:
- The algorithm or integration works as expected.
- Performance meets requirements under realistic load.
- Dependencies (third-party APIs, hardware, platforms) behave as documented.

### Testing Business Viability

Present the proposed solution to each internal stakeholder group and get explicit sign-off:

- **Marketing:** Can we position and message this effectively?
- **Sales:** Can we sell this at the expected price point?
- **Customer Success:** Can we support this at scale?
- **Finance:** Does the unit economics work?
- **Legal:** Are there regulatory or IP concerns?
- **Security:** Does this introduce unacceptable risk?

*Do not hand off to delivery without explicit viability sign-off from each relevant stakeholder.*

---

## 8. Discovery Sprint Technique

A time-boxed (1–2 week) intensive discovery cycle for high-risk opportunities.

### Team Composition
Product Manager + Product Designer + 1–2 Engineers (for feasibility) + optional: data analyst.

### Sprint Structure

1. **Day 1–2:** Frame the opportunity (Opportunity Assessment + Story Map).
2. **Day 3–4:** Customer interviews (minimum 6 sessions).
3. **Day 5–6:** Prototype the top 2–3 solution directions.
4. **Day 7–8:** Test prototypes with 5 target users.
5. **Day 9–10:** Synthesise findings; make a go/no-go/pivot decision.

### Exit Criteria
- All 4 product risks assessed (not necessarily cleared — but explicitly evaluated).
- At least one prototype tested with real users.
- A written recommendation: Build / Pivot / Kill, with evidence.

---

## 9. Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|-------------|-------------|-----------------|
| Feature Factory | Teams measure output (features shipped), not outcome (value delivered). | Define success metrics before starting discovery. |
| HiPPO decisions | Highest-Paid Person's Opinion overrides evidence. | All decisions require prototype or data evidence. |
| Discovery by committee | Too many voices; no decisions. | PM owns the decision after consulting stakeholders. |
| Skipping feasibility | Builds technically impossible commitments into roadmap. | Engineer must be present in discovery, not just delivery. |
| Validating with colleagues | Colleagues are too polite and too familiar with your thinking. | Test with target customers only. |
| Showing mockups, not prototypes | Customers react to aesthetics, not function. | Use the lowest-fidelity prototype that simulates the key interaction. |

---

## Sources

- Cagan, M. (2017). *INSPIRED: How to Create Tech Products Customers Love* (2nd ed.). Wiley.

## Cross-References

- **Upstream:** `product-strategy-vision` — strategy defines which opportunities to discover
- **Downstream:** `feature-planning` — approved opportunities become planned features
- **Related:** `lean-ux-validation` — UX-focused validation methods; this skill covers broader opportunity and business risk
