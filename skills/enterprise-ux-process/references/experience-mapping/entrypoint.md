---
name: experience-mapping
description: Use when discovering or de-risking a product direction by mapping user experiences, impact chains, and validation hypotheses — couples journey mapping, impact mapping, and lean customer-development interviews into one evidence-driven loop.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Experience Mapping
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- A team wants to build features but has not stated the *behaviour change* the feature must produce.
- A roadmap exists but no traceability between business outcomes, actors, and deliverables.
- Customer research is anecdotal — assumptions are unwritten and untested.
- Stakeholders disagree about scope and the disagreement is really about *who the user is* or *what success looks like*.
- A delivery team is about to commit more than two sprints to a direction that lacks validated demand.

## Do Not Use When

- The work is a contained bug fix, copy edit, or accessibility patch with a known correct outcome.
- A validated impact map and journey map already exist and the only open question is implementation sequencing — use a delivery-planning skill instead.
- The decision is a pure technical trade-off with no user-behaviour component.
- Compliance or regulatory work where the requirement is fixed by external authority.

## Required Inputs

- Stated business goal with a measurable target (number, direction, deadline).
- At least one named primary actor (role, not persona archetype) and access to 5+ real instances of that actor for interviews.
- Current evidence inventory: what is *known* vs. *assumed* about the actor, problem, and willingness to act.
- Constraint list: budget for discovery, decision deadline, and the cost of being wrong.

## Workflow

1. Read this SKILL.md, then load only the references needed for the active gate.
2. **Frame the goal.** Write the business outcome as a measurable change in actor behaviour. Reject vague verbs ("improve", "enable") — replace with countable verbs ("complete X within Y", "renew at rate Z").
3. **Build the impact map.** Goal → Actors → Impacts (behaviour changes) → Deliverables. Treat every branch as a hypothesis. See `references/impact-map-construction.md`.
4. **List assumptions and rank them.** For each branch, list what must be true. Score by *impact if wrong* × *current evidence*. Top-ranked assumptions become interview targets.
5. **Design discovery interviews.** Past behaviour, not future preference. Five-interview minimum per assumption cluster. See `references/discovery-interview-patterns.md`.
6. **Set validation thresholds before fieldwork.** Define the signal that would cause persevere, pivot, or kill — in advance. See `references/hypothesis-and-validation-thresholds.md`.
7. **Map the journey** for the validated actor and impact. Stages → goals → touchpoints → emotion/friction → moments of truth. See `references/journey-map-to-requirements.md`.
8. **Trace to deliverables.** Every requirement traces back to a journey moment, an impact, and an actor. Anything that does not trace is removed.
9. **Plan earn-or-learn milestones.** Each milestone either earns the business outcome or eliminates a top assumption. No "build for build's sake" milestones.
10. **Re-enter the loop** when evidence shifts: returning users behave differently, the metric does not move, or a new actor emerges.

## Quality Standards

- Every map node has an owner and a falsifiable check.
- Every assumption has a *named* validation method and a pre-set threshold.
- Journey emotions are sourced from interview quotes, not designer empathy.
- The deliverables list is shorter at the end than at the start of the workshop.
- Goals use the form "increase/decrease *metric* from *X* to *Y* by *date*" — never "make it better".

## Anti-Patterns

- Persona-as-fiction: writing a stock photo and hobbies block instead of an actor whose behaviour can be observed.
- Branch-everywhere impact maps that try to be exhaustive and become wallpaper.
- Asking customers to predict their own future behaviour ("would you use…", "how much would you pay…").
- Treating an interview that confirms the founder's hypothesis as evidence — confirmation without disconfirmation is not validation.
- Mapping a journey for an actor with no business outcome attached — pretty diagram, no decision.
- Letting the deliverables column expand each session; impact mapping is a *cutting* tool, not an additive one.
- Conflating output (feature shipped) with impact (behaviour changed).

## Outputs

- Goal statement (measurable, dated).
- Impact map: goal → actors → impacts → deliverables, with assumption labels per branch.
- Assumption ledger ranked by impact × evidence, each with validation method and threshold.
- Discovery interview guide and synthesis notes (quotes, behaviours, surprises).
- Journey map for the priority actor with moments of truth flagged.
- Outcome-to-feature traceability matrix.
- Earn-or-learn milestone plan with kill criteria.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | Experience map and hypothesis ledger | Markdown or diagram with assumptions, evidence, thresholds, and decision states | `docs/discovery/experience-map.md` |
| UX quality | Journey-to-requirements matrix | Markdown table mapping stages, pain points, features, content, and metrics | `docs/discovery/journey-requirements-matrix.md` |
| Release evidence | Alignment workshop decision record | Markdown notes with decisions, owners, and unresolved risks | `docs/discovery/alignment-decisions.md` |

## References

- `references/hypothesis-and-validation-thresholds.md` — assumption ranking, falsification thresholds, evidence calculus.
- `references/impact-map-construction.md` — Why → Who → How → What discipline; pruning rules; goal-writing patterns.
- `references/journey-map-to-requirements.md` — stage decomposition, moments of truth, traceability matrix.
- `references/discovery-interview-patterns.md` — recruitment, question patterns, behavioural probes, synthesis.
- `references/experience-mapping-anti-patterns.md` — failure modes and the corrective move for each.
<!-- dual-compat-end -->

## Decision Gates

| Gate | Question | If Yes | If No |
|------|----------|--------|-------|
| G1 Frame | Is the goal a measurable behaviour change? | Build impact map | Rewrite goal |
| G2 Map | Does each deliverable trace to an impact and actor? | Rank assumptions | Prune untraced branches |
| G3 Validate | Are top-3 assumptions falsifiable with a pre-set threshold? | Run interviews | Rewrite assumptions |
| G4 Field | Did 5+ interviews show *behavioural* (not stated) signal above threshold? | Map journey | Pivot or kill |
| G5 Trace | Does every requirement link to a journey moment? | Plan milestones | Cut requirement |
| G6 Milestone | Does each milestone earn outcome OR eliminate an assumption? | Ship | Redesign milestone |

## Map vs. Test — When to Choose

- **Map** when the team disagrees on *who*, *why*, or *what success means*. Mapping is an alignment tool.
- **Test** when the team agrees on framing but is uncertain whether users will *behave* as predicted.
- If both are unknown, map first to a depth that makes a test designable, then test. Do not map to exhaustion before the first test.
- A map without a follow-on test is a wall decoration. A test without a map produces orphan findings.

## Companion Skills

- `product-discovery` for the four product risks and prototype selection once an impact branch is selected for testing.
- `service-design-blueprinting` when the validated journey crosses staff, channels, and back-office systems.
