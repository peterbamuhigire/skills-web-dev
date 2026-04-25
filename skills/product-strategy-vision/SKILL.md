---
name: product-strategy-vision
description: Frameworks for defining a compelling product vision and a focused product
  strategy. Covers the 10 principles of product vision, product strategy principles,
  OKR technique for product teams, outcome-based roadmaps, product principles, and
  product...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Product Strategy & Vision
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Frameworks for defining a compelling product vision and a focused product strategy. Covers the 10 principles of product vision, product strategy principles, OKR technique for product teams, outcome-based roadmaps, product principles, and product...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `product-strategy-vision` or would be better handled by a more specific companion skill.
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
| Release evidence | Product vision and strategy document | Markdown doc covering the 10 principles of product vision applied to the product, plus the focused strategy that flows from it | `docs/product/vision-strategy-2026-04-16.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
Based on Cagan (2017) *INSPIRED: How to Create Tech Products Customers Love* (2nd ed.)
and Dash (2025) *Mastering Software Product Management*.

## When to Use

- Founding a new product or major product line
- Reviewing a product that has lost strategic direction
- Onboarding a new leadership team to an existing product
- Replacing a feature roadmap with outcome-based planning
- Aligning engineering and business on what "success" means

**The core distinction:** Vision is *where you are going* (3–5 year horizon).
Strategy is *how you will get there* (the series of bets you will make).
A roadmap is *what you will build next* — and a roadmap is NOT a strategy.

---

## 1. The 10 Principles of Product Vision

*A product vision that does not inspire your team will not inspire your customers.*

1. **Start with why.** The vision must articulate the customer problem being solved, not the product
   being built. "We want to help small businesses in Africa pay employees without a bank account"
   is a vision. "We are building a payroll app" is a product description.

2. **Fall in love with the problem, not the solution.** The solution will change many times. The
   problem should stay constant long enough to build a business around it.

3. **Do not describe the product.** The vision is not a product specification. It does not describe
   screens, features, or technology. It describes the future state for the customer.

4. **Be ambitious enough to inspire.** A vision that is easily achieved within 12 months is not a
   vision — it is a quarterly goal. Aim for a 3–5 year horizon.

5. **Be specific enough to guide.** "Improve education in Africa" is too broad to make a decision
   against. "Give every secondary school student in East Africa a personalised study plan" guides
   product decisions.

6. **Evangelise the vision relentlessly.** The PM must repeat the vision at every sprint review,
   all-hands, and hiring conversation. Teams cannot be aligned on a vision they have heard once.

7. **Reflect the values and culture of the team.** A vision the team does not believe in will not
   produce missionaries. Missionaries build better products than mercenaries.

8. **Consider multiple futures.** The best visions acknowledge that the path may change — the goal
   does not. Allow the strategy to adapt while the vision stays stable.

9. **Determine and embrace meaningful trade-offs.** A vision that stands for everything stands for
   nothing. Choosing who you are implicitly chooses who you are not.

10. **Understand the vision is the beginning of the conversation, not the end.** Share it early.
    Get input. Refine it. The best product visions are shaped by customer feedback, not handed
    down from a leadership offsite.

---

## 2. Product Strategy Principles

A product strategy is the sequence of markets you will target and the products you will build to
achieve your vision. It is not a list of features. It is a series of bets.

### The 6 Principles of Product Strategy

1. **Focus on one target market at a time.** Spreading discovery and resources across multiple
   markets simultaneously produces mediocre results in all of them. Dominate one segment; expand.

2. **Product strategy must derive from the company strategy.** If the company is growing through
   enterprise sales, the product strategy cannot be built around consumer virality.

3. **Strategy must define what you will *not* do.** Every "yes" to a market or feature is implicitly
   a "no" to alternatives. Make the trade-offs explicit or you will not hold them.

4. **Strategy is a living document.** Revisit quarterly. Update when market conditions, competitive
   moves, or discovery findings change the bet. A strategy written once and never touched is a
   historical artefact, not a strategic tool.

5. **Strategy must be grounded in market reality.** Use Porter's Five Forces, win/loss data, and
   customer churn analysis to stress-test strategic assumptions. See `competitive-analysis-pm`.

6. **Communicate the strategy to the whole team.** Engineers who understand the strategy make
   better architectural decisions. Designers who understand the strategy make better UX trade-offs.

---

## 3. Product Principles

Product principles are the values that guide decision-making when strategy alone does not resolve
a trade-off. They are not aspirational platitudes — they are tie-breakers.

**Format:** "When we must choose between X and Y, we choose X."

**Examples:**
- "When we must choose between breadth of features and depth of quality, we choose depth."
- "When we must choose between speed for power users and clarity for new users, we choose clarity."
- "When we must choose between a feature our largest client wants and one most users need, we
  choose most users."

*Product principles must be tested against real decisions. If a principle has never cost you
anything, it is not a principle — it is marketing copy.*

---

## 4. The OKR Technique for Product Teams

Objectives and Key Results (OKRs) translate vision and strategy into measurable team-level goals.

### Structure

```
Objective: Qualitative, inspiring statement of what to achieve this quarter.
  Key Result 1: Specific, measurable outcome that proves the objective was met.
  Key Result 2: Specific, measurable outcome.
  Key Result 3: Specific, measurable outcome.
```

### Rules

- **Objectives** are qualitative and motivating: "Make onboarding so good that new users
  succeed without any help."
- **Key Results** are quantitative and binary at quarter-end (achieved or not):
  "Time-to-first-value ≤ 10 minutes for 80% of new users by end of Q2."
- **3 Key Results maximum** per objective. More dilutes focus.
- **Team-level OKRs** are set by the team, not handed down. Leadership sets company OKRs;
  product teams set their own OKRs that contribute to company OKRs.
- **OKRs are not a task list.** They define outcomes, not activities. "Launch feature X" is a
  task. "Reduce churn in the first 30 days from 25% to 15%" is a Key Result.
- **Score at quarter end** (0.0–1.0). A score of 0.7 is healthy. A consistent 1.0 means your
  OKRs were not ambitious enough.

### Common OKR Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Output OKR ("ship X feature") | Measures activity, not outcome | Reframe as customer or business outcome |
| Too many OKRs (> 3 objectives) | Team cannot focus | Choose the one most important thing |
| OKRs set by management, not team | Team has no ownership | Team drafts; leadership aligns |
| Never reviewed mid-quarter | OKRs become irrelevant | Weekly check-in; monthly score review |

---

## 5. The Alternative to Roadmaps

Traditional feature roadmaps fail because they commit to solutions before validating problems,
destroy team morale when plans change, and shift accountability from outcomes to outputs.

### What to Use Instead

**Outcome-Based Planning:** Replace feature lists with outcome-based team objectives (OKRs).
The team owns the *how*; leadership owns the *what outcome* and *why*.

**High-Integrity Commitments:** Reserve the roadmap for genuine, dated commitments — legally
required delivery dates, contractual obligations, regulatory deadlines. These are the only
features that belong on a date-stamped roadmap.

**Opportunity Backlog:** Maintain a prioritised list of customer problems and business
opportunities (not features) for the team to explore via discovery. The backlog is problems,
not solutions.

---

## 6. Sustained Competitive Advantage (SCA)

*From Porter's framework applied to software product management (Dash, 2025).*

A product has SCA when it creates value that competitors cannot easily replicate. The PM's
job is to identify and protect the sources of SCA.

| SCA Source | How PMs Create It |
|-----------|------------------|
| **Network Effects** | Design features that become more valuable as more users join |
| **Switching Costs** | Build deep data integrations, workflows, and habits |
| **Proprietary Data** | Accumulate unique datasets through product use |
| **Brand Trust** | Consistent quality, reliability, and customer success |
| **Intellectual Property** | Patents, trade secrets, unique algorithms |
| **Ecosystem Lock-in** | Marketplaces, APIs, and partner networks |

---

## 7. Product Evangelism

The PM must sell the vision internally as aggressively as the sales team sells the product externally.

### The 9 Tools of Product Evangelism

1. **Use data, but also use story.** Data establishes credibility; story creates emotional investment.
2. **Show the customer pain, not the product feature.** Play the video of a user struggling.
3. **Share the discovery learnings widely.** Post interview notes, prototype test results, and
   user quotes where the whole team can read them.
4. **Build personal credibility.** Know the data better than anyone. Know the customer better
   than anyone. Leaders follow PMs who have done the homework.
5. **Give the team credit.** Engineers and designers who feel ownership evangelise the product
   themselves. The PM who takes credit has fewer missionaries next cycle.
6. **Be genuinely excited.** Enthusiasm is contagious. If the PM is not excited about the vision,
   no one else will be.
7. **Spend time with the team.** Sit with engineers. Attend design crits. Relationship capital
   is spent on hard days; build it during normal ones.
8. **Be transparent when things are not working.** A PM who only shares good news loses trust
   the moment something fails.
9. **Identify and nurture the team's missionaries.** Find the engineer or designer who cares most
   about the product. Give them a platform.

---

## Sources

- Cagan, M. (2017). *INSPIRED: How to Create Tech Products Customers Love* (2nd ed.). Wiley.
- Dash, S. K. (2025). *Mastering Software Product Management*. Orange Education.

## Cross-References

- **Upstream:** None — this is a foundational thinking skill
- **Downstream:** `product-discovery` (strategy identifies which problems to discover), `competitive-analysis-pm` (stress-tests strategy assumptions)
- **Related:** `saas-business-metrics` (OKR Key Results should be drawn from SaaS metrics), `lean-ux-validation` (validates product-level assumptions)
---

## Innovation of meaning vs innovation of solutions (Verganti)

For products in saturated/overcrowded markets, "ship more features" or "out-execute the incumbent" rarely wins. Roberto Verganti's *Overcrowded* (MIT Press, 2016) argues the scarce resource is **direction**, not ideas. Load `references/verganti-overcrowded.md` for the full method. Key contrasts:

- **Innovation of solutions** — better answers to existing questions (the dominant mode of Lean UX, design thinking, JTBD interviews).
- **Innovation of meaning** — redefines *which questions are worth asking*. Yankee Candle redefined candles from "illumination" to "emotional warmth"; Nest redefined thermostats from "control" to "comfort without controlling".

Verganti's process for innovation of meaning:

1. **Individuals** — autonomous envisioning over ~1 month, using the sentence *"I would love a [solution] that enables me to [experience] because [meaning]"*. The *because* clause is the deliverable.
2. **Pairs** — sparring partners deepen each hypothesis through trusted criticism.
3. **Radical circle** — a 15–20 person 2-day workshop ("the meaning factory") where pairs clash and fuse hypotheses; common-enemy framing is the unlock.
4. **Interpreters** — 6–8 outside experts (bias toward out-of-network) at a 1-day "interpreter's lab" halfway through; their deliverable is a *good question*, not a good idea.
5. **Customers** — meet *last*, after a vision exists, to test the new framework rather than to source it.

Use innovation-of-meaning work as a separate track from solution work. A team that ships only solution improvements eventually loses the category to a meaning shift it didn't see coming.
