---
name: enterprise-ux-process
description: Operationalize Synechron's enterprise UX process for premium-priced enterprise engagements (financial services, insurance, regulated industries, large internal apps, B2B SaaS). Produces maturity-level declaration + activity evidence pack + heuristic evaluation + 5-outcomes pre-launch declaration. Cite when scoping, executing, or auditing premium enterprise UX work.
---

# Enterprise UX Process Skill
**Source:** Operationalizes `book-extractions/enterprise-ux-financial-insurance-extraction.md` (Synechron, 2018; derived from The Design Ladder + Natalie Hanson's UX Maturity Model).

---

## Use when

- Scoping or executing a premium-priced enterprise UX engagement (financial services, insurance, healthcare, regulated industries, large internal apps, B2B SaaS)
- Auditing whether an enterprise project is positioned correctly on the maturity scale
- Defending a premium-pricing claim against an internal or external review
- Bridging strategy (Levy) and tactical UX work (Branson, Deacon, Fekeshazi) into a single enterprise-grade process

## Do not use when

- The work is consumer-grade (single-interaction, low-stakes) — use simpler skills
- The artifact is a prototype or experiment, not a production deliverable
- The project is explicitly priced as standard tier and the team has agreed not to pursue premium positioning

## Required inputs

Before invoking this skill, the following must be available or generated:

- Problem definition statement (what is the need; why now; for whom)
- Stakeholder list with roles (funder, owner, executor)
- Business objective (what success means in measurable terms)
- Success criteria (signed off by stakeholders)
- Target maturity level: **3 (UX Design)** for standard premium, **4 (Experience Design)** for top-tier

## Workflow — 9 phases

The process maps directly to Synechron's Activity-by-Level matrix. All 9 phases must produce documented evidence at Level 3+; the additional Level 4 activities are noted inline.

### Phase 1 — Problem Definition + Business Objective
- UX team meets with business stakeholders and product owners
- Answer: What is the need? Why now? For whom? How does this make life easier for the end user?
- Document vision, hopes, aspirations, and fears from the business perspective
- Output: signed problem-definition document

### Phase 2 — Stakeholder Discussions / Interviews
- Identify funders, owners, executors
- Conduct focused-group discussions OR individual interviews
- Capture: roles, expectations from UX, problem perception, end-user identification, collective goals, organizational/competitive/scope context
- Output: stakeholder-interview transcripts + summary brief

### Phase 3 — Success Criteria sign-off
- Checklist of measures the deliverable must hit to be successful
- Documented and agreed by all stakeholders
- Treat as non-negotiable acceptance criteria
- Output: signed success-criteria document

### Phase 4 — User Research (qualitative + quantitative)
- Methodologies: interviews, contextual inquiries, eye tracking, surveys, A/B testing, web analytics, field studies
- Quantitative: how many, what %
- Qualitative: why behaviors occur, what users notice
- Output: user-research report with both data types

### Phase 5 — Competitor Analysis
- Use Levy's 19-column competitive matrix (cite `book-extractions/levy-ux-strategy-extraction.md` Part VII or, in `website-skills`, `skills/design-reference/references/levy-competitive-matrix.md`)
- Minimum: 5 direct + 3 indirect competitors
- Output: filled matrix + 1-page distilled brief

### Phase 6 — Personas + User Journeys + Information Architecture
- Personas: apply Branson's discipline (Essential Persona declared, Mechanics floor — name, demographics, goals, environment, pain points, stress points)
- User Journeys: chronological touch-point sequence per primary persona
- Information Architecture: organization, structure, labelling of all content; navigation strategy/flow; site map; content buckets; intuitive labels
- **Level 4 also requires:** Experience Maps
- Output: persona deck + journey deck + IA deck

### Phase 7 — Wireframes + Clickable Prototype + Visual Design Mockups
- Wireframes: low-fidelity (paper) + high-fidelity (no color, focus on flow)
- Clickable prototype: stitched screens behaving like the real product per crucial user scenarios
- Visual design mockups: full-scale static representation with colors, branding, graphics
- **Level 4 also requires:** Mood Boards
- Output: wireframe pack + interactive prototype + mockup set

### Phase 8 — Heuristic Evaluation
- UX expert reviews against Nielsen-style heuristics:
  1. Visibility of System Status
  2. Match Between System and the Real World
  3. User Control and Freedom
  4. Consistency and Standards
  5. Error Prevention & Error Handling
  6. Recognizing Rather than Recall
  7. Flexibility and Efficiency of Use
  8. Aesthetic and Minimal Design
  9. Help and Documentation
- Plus Branson's 4-stage cognitive affordance audit per primary CTA (Presence → Visibility → Recognizability → Intelligibility)
- Output: heuristic evaluation report listing flaws + improvements

### Phase 9 — Usability Testing + ADA / Section 508 verification (Level 4 + all-levels accessibility)
- Usability testing: moderated in-person, moderated remote, OR unmoderated remote
- Test scenarios derived from actual use cases and task flows
- ADA / Section 508 / WCAG 2.1 AA verification — required at ALL maturity levels
- Output: usability test report + accessibility audit

## Outputs

A complete enterprise-ux-process engagement produces:

1. **Maturity-level declaration** — single sentence at the top of the engagement summary: "This engagement operates at UX Maturity Level [3 / 4], per Synechron's 5-level model."
2. **Activity-by-level evidence pack** — see `references/maturity-checklist.md` for the matrix and required evidence per activity
3. **Heuristic evaluation report** — Phase 8 output
4. **Five-outcomes pre-launch declaration** — Yes/No with evidence per outcome:
   - Useful (persona-validated)
   - Easy to use (first-task success without coaching)
   - Efficient (task time benchmarked)
   - Pleasing (≥ 4/5 first-impression rating)
   - Accessible (ADA/Section 508/WCAG 2.1 AA)
   - **Rule:** 4-of-5 disqualifies premium pricing. One No = no launch.

## Cross-references

### Canonical extraction (source-of-truth)
- `book-extractions/enterprise-ux-financial-insurance-extraction.md`

### Related skills in this engine
- `book-extractions/levy-ux-strategy-extraction.md` — strategy framing (Four Tenets) that should sit upstream of this process
- `book-extractions/branson-ux-ui-design-extraction.md` — persona discipline + working memory + 4-stage affordance applied within phases 6 and 8
- `book-extractions/deacon-ux-ui-strategy-extraction.md` — 3 levels of UX scope; declare in Phase 1
- `book-extractions/fekeshazi-pm-ux-guide-extraction.md` — PM collaboration rules and the "design is ongoing" stance

### Operational skills in other engines
- `website-skills/skills/design-quality-score/` — Category 8 (UX Maturity) scores the same artifacts independently
- `website-skills/skills/premium-ui-ux-design/references/enterprise-five-outcomes.md` — same 5-outcomes gate applied to website templates
- `srs-skills/01-strategic-vision/07-premium-product-positioning/` — premium-positioning gate using the same 5+5 model
- `srs-skills/03-design-documentation/05-ux-specification/` — UX spec produced under this process

### Quick-use checklist
- `references/maturity-checklist.md` — standalone activity-by-level checklist for use in project workspaces
