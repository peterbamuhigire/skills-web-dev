---
name: it-proposal-writing
description: Framework for writing persuasive IT project proposals that win work.
  Covers Basis of Decision (BOD), Unique Selling Points (USP), proposal strategy,
  document structure, persuasive prose techniques, the 5-level destruction model,
  grammar rules...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# IT Proposal Writing

<!-- dual-compat-start -->
## Use When

- Framework for writing persuasive IT project proposals that win work. Covers Basis of Decision (BOD), Unique Selling Points (USP), proposal strategy, document structure, persuasive prose techniques, the 5-level destruction model, grammar rules...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `it-proposal-writing` or would be better handled by a more specific companion skill.
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
| Release evidence | IT proposal document | Markdown doc covering Basis of Decision (BOD), Unique Selling Points, scope, pricing, and risk per opportunity | `docs/proposals/proposal-2026-04-16.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
Based on Coombs, P. (2005). *IT Project Proposals: Writing to Win*. Cambridge University Press.

## When to Use

- Responding to a client Request for Proposal (RFP) or tender
- Writing an unsolicited proposal for a prospect
- Preparing an internal business case for a technology project
- Reviewing a proposal before submission

**The core truth about proposals:** *Your proposal is your shop window. A proposal full of
accurate facts, buried in jargon and poor structure, will lose to a clearly written proposal
from a weaker competitor. Good communication is what makes or breaks the deal.*

---

## 1. The Proposal Lifecycle

Every winning proposal follows this sequence. Do not skip steps.

```
1. Establish the Strategy  →  BOD + USP + Reader + Approach
       ↓
2. Choose the Content      →  What the reader needs to see (not what you want to say)
       ↓
3. Determine the Structure →  Document plan, sections, headings
       ↓
4. Write the Proposal      →  Persuasive, specific, plain-language prose
       ↓
5. Review and Rate         →  Internal review using the Proposal Evaluation Questionnaire
       ↓
6. Submit                  →  Final check: compliance, presentation, contact details
```

The lifecycle is iterative. Content choices may force you to revise the structure.
A review finding may require rewriting a section. Allow time for iteration.

---

## 2. Establishing the Strategy

### Basis of Decision (BOD)

The BOD is the set of criteria — stated or unstated — that the reader will use to evaluate your
proposal. Understanding it is the most important step in proposal strategy.

**Sources of the BOD:**
- The RFP itself (stated evaluation criteria)
- Knowledge of the client's organisation, budget pressures, and political context
- Prior conversations with the client
- The problem statement the client has articulated

*If you do not know the BOD, you cannot write a targeted proposal. You will write a generic
document that answers questions nobody asked.*

**Questions to determine the BOD:**
1. What is the client's primary problem, stated in their own words?
2. What does success look like to the key decision-maker?
3. What are the unstated concerns (risk aversion, budget justification, internal politics)?
4. Who else is the client likely to receive proposals from?
5. What would make the client choose a competitor over you?

### Unique Selling Points (USP)

Your USP is the answer to: *"Why should this client choose us over every other option?"*

A USP must be:
- **Specific:** "We have delivered 3 school management systems in Uganda with a combined user
  base of 40,000 students" — not "we have extensive education sector experience."
- **Relevant to this client:** Connect your strength to their specific need.
- **Credible:** Backed by evidence (case study, reference, data).
- **Differentiated:** Something the competition cannot honestly say.

*If your USP is "we are experienced, professional, and client-focused," you have no USP.
Every proposal says this. None of it persuades.*

### Knowing the Reader

Write for the decision-maker, not for yourself.

- Who will read this proposal? (Procurement officer? CTO? Board member? All three?)
- What is their technical level? Do not write for your own level of expertise.
- What are they worried about? Address their risk explicitly — do not wait for them to ask.
- How long will they spend reading it? Assume less time than you expect. Every word competes
  for attention.

---

## 3. The 5 Levels of Proposal Failure

Coombs identifies 5 progressive ways a writer's message is destroyed before it reaches the reader.

| Level | Problem | Example |
|-------|---------|---------|
| 1 | **Inappropriate content** | Answering the question you wished they asked, not the one they asked |
| 2 | **Confusing structure** | Key differentiators buried on page 23; executive summary missing |
| 3 | **Unconvincing prose** | Vague claims, passive voice, over-abstraction, no evidence |
| 4 | **Poor grammar** | Sentences that require re-reading; dangling modifiers; incorrect tense |
| 5 | **Typos and spelling mistakes** | "We provide profesional servies" — destroys technical credibility |

*Level 5 errors make the client doubt Level 1. If you cannot proofread a document, the client
doubts whether you can manage a project.*

---

## 4. Choosing Content

### The Golden Rule of Content

Include only what advances your argument that you are the best solution to the client's problem.
Every sentence should satisfy one of these tests:

- It demonstrates that you understand the client's problem.
- It shows that your solution is credible and complete.
- It provides evidence that you can deliver (past projects, methodology, team expertise).
- It addresses a specific risk or concern the client has stated or implied.

*Nothing else belongs in the proposal. No company history unless it directly supports a claim.
No technical deep dives unless the reader is technical and the detail is evaluatively relevant.*

### Typical Proposal Sections

| Section | Purpose | Notes |
|---------|---------|-------|
| **Executive Summary** | One page: problem, solution, why us, price | Written last; read first |
| **Understanding of Requirements** | Prove you understood the brief | Mirror the client's language |
| **Proposed Solution** | What you will build / deliver | Specific, testable, visual where possible |
| **Methodology / Approach** | How you will deliver | Risk-addressed, phased, milestoned |
| **Team and Experience** | Why your team can do this | Relevant roles, relevant past projects |
| **Timeline** | When it will be done | Phased, with milestones and dependencies |
| **Pricing** | How much and what for | Itemised; tied to deliverables |
| **References** | Who can vouch for you | Names, not anonymous testimonials |
| **Risk and Mitigation** | What can go wrong and how you handle it | Proactively addressing concerns builds trust |

---

## 5. Structuring the Document

### The Inverted Pyramid

Put the most important information first. Decision-makers read executive summaries and skim the
rest. If your key differentiator is on page 8, it will not be read by everyone.

**Structure of the Executive Summary (mandatory):**
1. Statement of the client's problem (in their language — not yours)
2. Your proposed solution in 2–3 sentences
3. The key reason to choose you (top USP, evidence-backed)
4. Total investment (price) and timeline

### Section Headings That Work

Headings must stand on their own. A reader scanning headings should understand the proposal arc.

| Weak Heading | Strong Heading |
|-------------|---------------|
| "Our Approach" | "Three-Phase Delivery Approach with Weekly Client Reviews" |
| "Experience" | "5 Completed School Management Systems in East Africa" |
| "The Solution" | "A Custom Fee Management System Integrated with Your Existing EMIS" |
| "Pricing" | "Phased Investment: Prototype at UGX 12M, Full System at UGX 45M" |

---

## 6. Writing Persuasive Prose

### Spin the Words: Benefit-First Writing

Every technical claim must be translated into a reader benefit.

**Before:** "The system uses a microservices architecture."
**After:** "The system's modular design means you can add the HR module in Phase 3 without
rebuilding any existing functionality — saving an estimated 200 hours of rework."

### Avoid Abstraction

Abstract claims lose readers. Concrete specifics persuade.

| Abstract | Concrete |
|---------|---------|
| "We have vast experience" | "We have delivered 7 school systems across Uganda and Kenya since 2019" |
| "The system is fast" | "Bulk report generation for 5,000 students completes in < 4 seconds" |
| "We deliver on time" | "Our last 4 projects: delivered within 3 days of agreed deadline on average" |
| "We understand education" | "Our lead developer spent 3 years as a systems administrator at Makerere" |

### Plain Language Rules

- Use active voice: "The system generates the report" not "The report is generated by the system."
- Sentences under 25 words. Split anything longer.
- One idea per paragraph.
- Avoid jargon unless the reader is technical and the term is precise.
- Define every acronym on first use.

### Remove Boilerplate

Boilerplate is the text that appears in every proposal regardless of client: company history paragraphs,
mission statements, generic team introductions. Every paragraph of boilerplate is a paragraph the
client skips — and a paragraph that crowds out your real argument.

*Test: If this paragraph could appear word-for-word in a proposal to a different client, delete it.*

---

## 7. Grammar Rules That Matter in Proposals

### Apostrophes

- **Possessive singular:** The client's requirements (one client).
- **Possessive plural:** The clients' accounts (multiple clients).
- **It's** = it is. **Its** = belonging to it. Never use "it's" as a possessive.
- Misplaced apostrophe on a front page signals carelessness to every professional reader.

### Bullet Lists

- Lead-in sentence ending with a colon: bullet items continue the sentence — no full stop at
  the end of each item unless the items are grammatically complete sentences.
- All items in a list must be parallel: all noun phrases, or all sentences, not a mixture.
- Maximum 7 items per list. Beyond 7, the reader stops absorbing and starts skimming.

### Capitalisation

- Choose one style (title case or sentence case for headings) and hold it throughout.
- Do not capitalise for emphasis. Bold serves that function.
- Product and company names are capitalised; roles generally are not ("the project manager").

---

## 8. The Proposal Evaluation Questionnaire

Use this checklist to score a draft proposal before submission. Score 1–5 on each dimension.

| Dimension | Question | Score (1–5) |
|-----------|---------|------------|
| **Strategy** | Does the proposal clearly address the stated BOD? | |
| **USP** | Is our key differentiator stated specifically and early? | |
| **Understanding** | Does it prove we understand the client's real problem? | |
| **Evidence** | Are all claims backed by specific evidence (data, case study, reference)? | |
| **Structure** | Does the document flow logically? Can a skim reader grasp the argument? | |
| **Prose quality** | Is every section written in plain, active, benefit-first language? | |
| **Risk addressed** | Does it proactively address the client's likely concerns? | |
| **Pricing clarity** | Is pricing itemised, justified, and tied to deliverables? | |
| **Grammar and presentation** | Zero typos, consistent formatting, correct grammar? | |
| **Compliance** | Does it answer every question asked in the RFP? | |

**Scoring:**
- 45–50: Submit. Strong proposal.
- 35–44: Revise targeted sections, then submit.
- < 35: Major rewrite required. Do not submit in current state.

---

## 9. Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Writing about the solution before proving problem understanding | Client feels unheard | Section 1 must mirror the client's problem statement |
| Starting with company history | Nobody cares yet | Lead with the client's problem |
| Vague team introductions ("extensive experience") | Not credible | Name specific projects, roles, and outcomes |
| No executive summary | Decision-makers will not read further | One-page executive summary is mandatory |
| Price as afterthought | Creates anxiety and undermines trust | Price clearly stated, phased, and justified |
| Passive voice throughout | Weak, evasive tone | Rewrite in active voice |
| Boilerplate filling pages | Signals you did not customise for this client | Every paragraph must be this-client-specific |

---

## Sources

- Coombs, P. (2005). *IT Project Proposals: Writing to Win.* Cambridge University Press.

## Cross-References

- **Upstream:** `software-business-models` (services model depends on winning proposals), `software-pricing-strategy` (pricing section in proposals)
- **Downstream:** `sdlc-planning` (winning the proposal triggers SDLC planning), `project-requirements` (requirements gathering follows after project award)
- **Related:** `technology-grant-writing` (grants are specialised proposals with different evaluation criteria)
