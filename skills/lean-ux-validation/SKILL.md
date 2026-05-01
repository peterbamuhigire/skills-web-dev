---
name: lean-ux-validation
description: Hypothesis-driven UX validation process from Laura Klein's UX for Lean
  Startups. Use BEFORE building any feature to validate it is worth building. Covers
  problem/market/product validation, 5-user research, fake button testing, interview...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Lean UX Validation
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Hypothesis-driven UX validation process from Laura Klein's UX for Lean Startups. Use BEFORE building any feature to validate it is worth building. Covers problem/market/product validation, 5-user research, fake button testing, interview...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `lean-ux-validation` or would be better handled by a more specific companion skill.
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
| UX quality | Lean UX validation report | Markdown doc covering hypothesis, MVP, measurement, and learning per Klein's framework | `docs/ux/lean-validation-2026-04-16.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
Based on Klein (2013) *UX for Lean Startups.* Applied to SaaS, mobile, and web product development.

## When to Use

Load this skill when:
- Planning a new feature before writing a line of code
- Deciding whether to build something a user requested
- Designing a user research session
- Setting up metrics for a design change
- Prioritising a feature backlog

**The mantra:** *"You don't have time NOT to do research. A week of research saves months of rebuilding."*

---

## 1. Core Philosophy

**Products are sets of hypotheses, not features.**

Traditional development: "We need comments." → Design → Build → Ship.
Lean UX: "We believe allowing comments will increase engagement. How do we validate that cheaply before building?"

**The difference:** The hypothesis framing forces you to define what success looks like *before* you start. Without this, you cannot know whether your design worked.

**Pain-Driven Design:**
Your role is a doctor's. Ask "where does it hurt?" Observe symptoms. Diagnose. Prescribe treatment. Monitor. Adjust. You are not asking patients to write their own prescriptions — you are listening to their pain and applying expertise.

**Five defining properties of Lean UX:**
1. **Hypothesis-driven** — every design change is a hypothesis with a measurable outcome
2. **User-centred** — relentless focus on real users, real problems, real observation
3. **Agile** — cross-functional teams, short cycles, no waterfall handoffs
4. **Data-informed** — data tells you *what*; research tells you *why*
5. **Waste-eliminating** — unbuilt bad features are money saved for features that work

---

## 2. The 3-Layer Validation Sequence

Validate in this order. Never skip ahead.

### Layer 1: Validate the Problem
Is there a real, painful, specific problem? You know you have validated a problem when specific groups of people are complaining about the *same specific thing*. Problems people "kind of" have are not enough — the pain must be severe enough that they would pay to have it solved.

### Layer 2: Validate the Market
Is the group large enough and specific enough? Do not aim at "women" or "doctors." Aim at "urban working mothers without nannies" or "oncologists in large practices who don't do their own billing." Start narrow; expand later. If you cannot find 5 people with near-identical problems, your market definition is wrong.

### Layer 3: Validate the Product
Does *your specific solution* solve the problem for *this specific market*? Millions want to lose weight; not every diet plan sells. Product validation is iterative and takes the longest.

---

## 3. Validation Tools (Before Writing Code)

### Ethnographic / Contextual Inquiry
Observe 5 people in your target market doing the tasks your product will address. Watch silently. Ask open-ended questions. You will learn things no survey or interview will reveal (e.g., that payroll processing is completely non-linear and interrupt-driven — killing a planned "collaboration" feature before it was built).

### Landing Page Test
Build a one-page site advertising the product as if it exists. Add a Buy or Pre-order button. Drive cheap ad traffic. Measure click-through. No clicks = no market. Cost: near zero. Validates both market and product framing simultaneously.

### Fake Button / Feature Stub Test
Before building a feature, put a placeholder button where the feature would live. Count clicks. If even the users loudly demanding the feature won't click a stub button to show intent, do not build it. Every unbuilt bad feature saves real money.

### Prototype Test (Show, Never Describe)
Show — never describe — your idea. Ask users to interact with a working prototype, however rough. Describing an idea to users is the worst validation method: they answer whether they'd buy their *imagined* version of your idea, not your actual product.

**The cardinal sin:** Pitching your concept and asking "would you use this?" They cannot predict their own future behaviour. They will say yes to end the conversation.

---

## 4. User Research on a Budget

### The 5-User Rule
5 users is sufficient for qualitative research. You stop seeing new patterns after 5–6. Do 5, make changes, do 5 more. Iterating is always more valuable than larger single batches.

### Competitor Testing (Free and Powerful)
Run Google/Facebook/Craigslist ads to find 4–5 users of your competitors. Watch them use the competitor's product in their natural workflow. Ask what frustrates them. You learn real, payable problems — for free.

### Guerrilla Coffee Shop Testing
Take a laptop with your prototype to a coffee shop. Offer to buy someone a coffee for 10 minutes. Give them ONE task, provide only the data they'd naturally have, and observe silently. Costs one coffee; yields more insight than weeks of internal debate.

### Interview Rules
- **Shut up.** You are there to listen, not sell. The moment you explain your concept, you have biased the session.
- **Never give a guided tour.** Let users explore independently. Ask "Show me how you would..." not "Here's how it works."
- **Follow up relentlessly.** "It was cool" is not data. Drill until you reach the actual underlying reaction.
- **Don't accept solutions — listen for problems.** "I want case studies" is a solution. Ask "why?" Users asking for case studies were actually solving three different problems (choice anxiety, value justification, social proof) — each needing a different design response.
- **Surveys are follow-up tools, not discovery tools.** Use surveys to confirm qualitative patterns, not to form initial hypotheses.

---

## 5. Design the Test Before Designing the Product

Before sketching a single screen, define:
1. What metric are we trying to move?
2. How will we measure it?
3. What constitutes success? (Be specific: "statistically significant 15% increase in X within 30 days")

Without this, you cannot know if your design worked. A feature is not "done" when it ships — it is done when it has moved the metric.

---

## 6. Metrics That Matter

**Two layers of measurement:**
- **Quantitative (what):** A/B tests, funnel analytics, cohort analysis, conversion rates, NPS
- **Qualitative (why):** Usability sessions, interviews, observation — use when quant shows something odd and you need to understand the cause

**Vanity metrics trap:** Metrics that look good but don't connect to business goals (e.g., a "second visit" incentive that increased return visits but drove zero additional revenue). Always ask: what is the business goal *behind* this metric?

**Multi-metric principle:** Look for positive movement across *multiple* metrics simultaneously. No single metric tells the full story.

**A/B testing limitations:**
- Can trap you in local maxima — optimising your hill doesn't tell you a taller hill exists
- Cannot replace qualitative research to discover *why* something fails
- Statistical insignificance is common: 3 vs 6 conversions is not a real result

---

## 7. Iterative Design Process (9 Tools)

Run these in order. Never skip Tools 1, 2, 5, or 9.

1. **Understand the problem** — rephrase feature requests as user problems; never lock in a solution first
2. **Design the test first** — define the measurable success metric before designing
3. **Write design stories** — behavioural stories: "A user who is confused about X can quickly find help"
4. **Brainstorm (15 minutes max)** — everyone writes silently, reads aloud, no voting
5. **Make a decision** — map solutions on Expected Return vs Expected Cost axes; indecision is the most common trait of failing products
6. **Try to invalidate first** — can a quick test prove this idea wrong? A fake button can save weeks of engineering
7. **Sketch rapidly** — disposable, iterative; sketch states and flows, not just screens; show to 4–5 people immediately
8. **Build interactive prototypes when warranted** — only if interaction is complex or fixing mistakes would be expensive
9. **Test and iterate** — the first design is never correct; get it in front of users as fast as possible

---

## 8. Feature Prioritisation (UX Perspective)

**ROI graph:** Plot potential features on Expected Return (y) vs Expected Cost (x). Features in the high-return, low-cost quadrant are obvious priorities. Involve engineering for cost estimates.

**Pain first:** Build features that eliminate the most painful friction for the highest-value users. Discover pain by watching users, talking to churned users, and tracking funnel drop-offs.

**The solutions trap:** When users ask for "X," they are giving you a solution. Ask why. The underlying problem may have five better solutions than the one they suggested. Build what solves the pain, not what was requested.

**MVP definition:**
- **Limited product** (correct) — does few things, does them well; clear starting point; not confusing; not ugly enough to scare away your market
- **Crappy product** (wrong) — tries to do many things, does none well; teaches you nothing because you can't tell if the idea or the execution was broken

---

## 9. Common Startup UX Mistakes

1. Solving a problem that doesn't exist
2. Targeting a market that is too broad
3. Describing the product instead of showing it
4. Skipping research because of "no time"
5. Building before trying to invalidate the idea cheaply
6. Jumping to sketches (Tool 7) before understanding the problem (Tool 1)
7. Shipping a crappy MVP and calling it lean
8. Accepting feature requests as design requirements
9. Working in waterfall/silos (designer → developer handoff loses information)
10. Testing only with friends and colleagues who cannot give unbiased feedback

---

## 10. Key Mantras

1. **"Listen to your users. All the time."**
2. **"When you make assumptions, test them before spending time building around them."**
3. **"Iterate. Iterate. Iterate."**
4. **"Validate: Problem → Market → Product. In that order."**
5. **"Users ask for solutions. Listen for the underlying pain."**
6. **"Ship something limited, not something crappy."**
7. **"The closer you get to showing people a real product, the more accurately you can predict whether they will use it."**
8. **"The first design is always wrong. Always test and iterate."**

---

## Sources

- Klein, L. (2013). *UX for Lean Startups: Faster, Smarter User Experience Research and Design.* O'Reilly Media.