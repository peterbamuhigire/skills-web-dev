---
name: game-narrative-and-interactive-story-design
description: Use when designing, reviewing, or implementing interactive game stories, narrative systems, quests, characters, dialogue, environmental storytelling, branching choices, story beats, setups/payoffs, or narrative validation; use level-world-and-content-production for level assembly and content integration.
metadata:
  portable: true
  compatible_with: [claude-code, codex]
---

# Game Narrative and Interactive Story Design

Convert theme, audience, player fantasy, and gameplay constraints into a causal, testable narrative system whose delivery survives player agency, interruption, and production limits.

## Prerequisites

Load `world-class-engineering`, `game-design-and-experience`, `level-world-and-content-production`, accessibility/localisation guidance, and the project's cultural research, rights, safeguarding, and content constraints.

<!-- dual-compat-start -->
## Use When

- Defining premise, theme, characters, wants/needs, conflict, beats, quests, dialogue, choices, consequences, environmental narrative, or story-state logic.
- Diagnosing a story that is incoherent, over-exposed, disconnected from play, culturally unsafe, or impossible to validate.
- Creating narrative requirements, state models, content schemas, review gates, localisation notes, or comprehension playtests.

## Do Not Use When

- The task is level layout, encounter pacing, or content integration without a narrative-system decision; use `level-world-and-content-production`.
- The task is prose-only fiction with no interactive delivery or runtime state.
- Cultural fact claims lack evidence; return to research and cultural review before canonising them.

## Required Inputs

| Input | Required | Missing-input response |
|---|---:|---|
| Audience, player fantasy, genre/tone, platform and session shape | yes | Mark the premise provisional and stop detailed scripting. |
| Approved cultural/source ledger and rights/sensitivity constraints | conditional | Block historical or community-specific canon. |
| Gameplay loop, player verbs, level/content topology and save model | yes | Produce only a narrative hypothesis, not runtime logic. |
| Content budget, localisation/VO plan, rating and accessibility constraints | yes | Flag cost and delivery as unvalidated. |

## Workflow

1. State the player-facing narrative promise, theme, audience need and non-negotiable cultural boundaries in plain language.
2. Build a causal spine: setup, destabilising event, dramatic question, escalating obstacles and choices, climax, resolution, and changed state. Every beat must follow from an action or consequence.
3. Define characters by observable want, deeper need, stakes, tactics, contradiction, relationships, agency and change—not biography volume.
4. Map the spine to player verbs, spaces, encounters and session boundaries. Choose authored, branching, environmental, systemic/emergent or hybrid delivery deliberately.
5. Model story states, prerequisites, mutually exclusive branches, convergence, failure/recovery, save/load, replay and late-join behaviour. Give each state stable identifiers.
6. Specify each delivery unit with trigger, payload, player control, interruption policy, fallback, localisation fields, accessibility channel and acceptance oracle.
7. Track setups, reminders and payoffs; separate essential comprehension from optional depth. Never place a critical fact in one fragile channel.
8. Prototype with the cheapest faithful form, then test comprehension, motivation, pacing, choice legibility and cultural interpretation with named builds and audiences.
9. Stop on broken causality, unreachable state, missing cultural approval, inaccessible critical information, uncontrolled scope, or an untestable emotional claim.
10. Load `references/narrative-playtest-loop.md` for the cross-discipline contract. Retain
    failed-path, branch, audio-off, localisation-expansion, and accessibility evidence;
    standardise only a change that improves the player hypothesis without breaking
    gameplay, performance, rights, or safety constraints.

## Outputs

| Artefact | Acceptance condition |
|---|---|
| Narrative promise, causal spine and character contracts | Wants, stakes, actions, consequences and changed states are explicit. |
| Beat/quest/state map | IDs, prerequisites, branches, convergence, failure and persistence are deterministic. |
| Narrative delivery specification | Trigger, channel, interruption, fallback, localisation and accessibility are defined. |
| Setup/payoff and evidence register | Every essential setup has a reachable payoff and test evidence. |

## Evidence Produced

| Category | Artifact | Format | Example |
|---|---|---|---|
| Correctness | Reachability/state-transition tests and setup-payoff coverage. | Test report and coverage matrix | `docs/narrative/reachability-tests.md` |
| UX quality | Comprehension, motivation, pacing and choice-legibility playtest results. | Playtest report with observations and findings | `docs/narrative/player-experience.md` |
| UX quality | Cultural safety review | Review record: named reviewer, source/provenance link, decision and unresolved caveat | `docs/narrative/cultural-safety-review.md` |
| Release evidence | Build/content revision, localisation completeness and known narrative defects. | Release record with revision identity, localisation status and defect list | `docs/narrative/release-evidence.md` |
<!-- dual-compat-end -->

## Capability and Degraded Mode

Editing canon, dialogue, localisation source or runtime content requires task authority; community representation and public claims require accountable review. Without a playable build, return a desk-reviewed state model and test plan with runtime comprehension, pacing and interruption marked `not assessed`.

## Decision Rules

| Condition | Action |
|---|---|
| Plot beat does not alter player knowledge, goal, relationship, capability or world state | Cut, combine or make its purpose explicit. |
| Critical information has one missable delivery channel | Add an accessible, diegetically appropriate recovery path. |
| Choice has no legible difference or consequence | Reframe as flavour or add a measurable consequence; do not market false agency. |
| Branch cost exceeds budget | Share states/content intentionally and preserve consequence through variables, reactions or later payoffs. |
| Historical authenticity and fun appear to conflict | Escalate to research/cultural owners; label dramatization and never invent certainty. |

## Quality Standards

- Prefer causal verbs and observable player evidence over adjectives such as “immersive” or “meaningful”.
- Interactive flow outranks screenplay shape: the player must understand what to do, why, and what changed.
- Preserve player control or specify the exact, tested reason for taking it away.
- Treat the supplied story text as a design source, not a substitute for cultural evidence or project canon.
- Complete the mechanics-to-meaning matrix for consequential mechanics; agency, feedback, state transitions, and player interpretation must be evidenced rather than assumed.
- Publish the initial product audit at `min(raw_score, 65)` before any improvement claim; the chosen change targets 95/100 and has a reversible test, guardrails, and re-audit evidence.

## Anti-Patterns

- Lore dump before player need. Fix: reveal information through action, consequence and optional depth.
- Branching diagram without state ownership. Fix: assign stable IDs, predicates, persistence and recovery.
- Emotional acceptance criterion (“player feels heroic”). Fix: define observable comprehension/choice/behaviour evidence.
- One “representative” reviewer. Fix: identify role, community relationship, scope and unresolved disagreement.
- Cutscene logic detached from gameplay. Fix: map every major beat to player verbs and state change.

## Read Next

- `level-world-and-content-production` for spatial and encounter integration.
- `gameplay-systems-engineering` for runtime state implementation.
- `game-testing-polish` for playtest and regression evidence.

## References

- [Narrative system contract](references/narrative-system-contract.md)
- [Narrative verification matrix](references/narrative-verification-matrix.md)
- [Narrative and gameplay playtest loop](references/narrative-playtest-loop.md)
- [Narrative mechanics learning matrix](references/narrative-mechanics-learning-matrix.md)
- [Game-development source register](../../../docs/game-dev-analysis/source-register.md)
