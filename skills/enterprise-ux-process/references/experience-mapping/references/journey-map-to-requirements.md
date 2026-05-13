# Journey Map to Requirements

A journey map is only useful if it ends in scope decisions. Kalbach calls these maps a class of *alignment diagram* — a document whose job is to align an individual's experience with the services of an organisation so that teams can make coherent decisions. This reference is the bridge from observed experience to traceable, testable requirements.

## Scope of a Journey Map

Before drawing, fix four boundaries:

1. **Actor** — exactly one named role per map. Multi-actor journeys belong in a service blueprint or an ecosystem map.
2. **Scenario** — the trigger and goal that frame the journey ("first-time renewal of policy", not "using the app"). The scenario is the customer's job, not yours.
3. **Time horizon** — start moment and end moment. A "lifecycle" map collapses to a journey only when start and end are real events, not "discovery" and "advocacy".
4. **Channel set** — the physical, digital, and human channels in scope. Anything outside the set is marked "off-map" and not silently dropped.

Without these four, the map drifts into a generic "user life" diagram and loses its decision power.

## The Four-Phase Mapping Process

Build the map in four phases — initiate, investigate, illustrate, align — and resist starting in *illustrate*:

- **Initiate**: agree the actor, scenario, time horizon, and channel set. Lock the question the map is supposed to answer.
- **Investigate**: research with real users; do not draw the map from internal opinion. The map is grounded in artefacts, quotes, and observations, not stakeholder workshop hypotheses.
- **Illustrate**: draft the visual, but treat the draft as scaffolding for alignment, not the deliverable.
- **Align**: workshop the draft with the teams responsible for delivery. The draft becomes the alignment artefact only when those teams have used it to decide something.

A map that completes *illustrate* but not *align* has no requirements value.

## Layered Structure

A working journey map has six layers, top to bottom:

| Layer | Content | Source |
|-------|---------|--------|
| Stages | Phases of the scenario (4–7). | Inferred from interviews. |
| User goal per stage | What the actor is trying to accomplish *now*. | Direct quotes. |
| Action / touchpoint | What the actor does and on which channel. | Observation. |
| Thoughts | What the actor is reasoning or asking themselves. | Verbatim quotes. |
| Feelings | Emotional valence with intensity. | Verbatim plus ethnographic inference. |
| Pain points / opportunities | What is broken or under-served. | Researcher synthesis with evidence pointer. |

Optional layers depending on purpose: *organisation actions*, *backstage processes*, *evidence*, *strategy / principles*. When the map needs more than four optional layers it is becoming a service blueprint; switch tools rather than overload the journey map.

## Moments of Truth

Identify the points on the map where the actor's overall judgement of the service is set — Carlzon's *moments of truth*. They are not all touchpoints; they are the emotionally charged interactions where the customer commits, abandons, or recommits. Mark them explicitly on the map. Most maps have three to seven; if everything is a moment of truth, none is.

Requirements written for moments of truth are weighted higher than those for ordinary touchpoints. Failure-recovery work, evidence design, and frontline authority all concentrate at moments of truth.

## From Pain Point to Requirement

For every pain point on the map, generate a requirement record with these fields:

- **Stage and touchpoint** — anchor on the map.
- **Actor goal** — the user's goal at that step (not your KPI).
- **Observed behaviour** — what the actor actually does, with evidence pointers (interview ID, observation note, log signal).
- **Hypothesised cause** — why this is happening; flagged as hypothesis, not fact.
- **Proposed change** — what the deliverable does differently.
- **Success measure** — how the change will be observed (behaviour, time, error rate, conversion). Tied to a specific signal, not "improved experience".
- **Kill switch** — the observation that would prove the change did not work, and the date by which it must be measured.

Pain points without these fields are research findings, not requirements. They go to the backlog tagged "needs definition" and do not become work.

## Mapping to the Impact Map

Every requirement should be traceable to one impact node on the parent impact map. Practical rules:

- A requirement whose actor differs from the impact map's actor is suspect — confirm the role match.
- A requirement that does not move at least one impact is "nice to have" and is parked, not scheduled.
- A requirement that would move the goal but not through the listed impacts means the impact map is missing a branch — update the impact map first.

This traceability protects against the most common drift, where journey maps generate wishlists that the impact map cannot prioritise.

## Future-State Maps

A future-state journey map is the proposed scenario after the deliverable lands. Build it next to the current-state map, not on top of it:

- For each pain point, show the proposed touchpoint sequence.
- Mark the *change*: removed steps, new steps, re-ordered steps, recovered moments of truth.
- Keep the actor and scenario identical between current and future state. Comparing across actors or scenarios produces optimism bias.

The future-state map becomes the acceptance reference: if the deliverable ships and the actor's real journey does not match the future state at the marked stages, the deliverable did not work, regardless of what was built.

## Requirements Granularity

Granularity should match the audience using the map:

- For roadmap discussions: epic-level requirements aligned to stages.
- For backlog grooming: story-level requirements tied to actions and pain points.
- For acceptance: testable behaviour-level requirements tied to moments of truth.

A single map should not try to serve all three at once. Maintain three views over the same map rather than three different maps.

## Living Document Discipline

The map is a "living document" only if someone owns updating it. Without an owner, the map ages out within a quarter and becomes wallpaper. Assign an owner, schedule a review cadence (typically the same cadence as impact-map reviews), and update with new behavioural signal, not with stakeholder requests.

## Source Grounding

- Kalbach's framing of journey maps as a class of alignment diagrams whose purpose is value alignment between user and organisation.
- The four-phase mapping process: initiate, investigate, illustrate, align.
- Carlzon's moments of truth as critical, emotionally charged interaction points warranting weighted attention.
- The six-layer journey map (stages, goals, actions/touchpoints, thoughts, feelings, pain points/opportunities) used as the working scaffold.
- The "living document" discipline of revising maps against changing evidence rather than treating them as fixed deliverables.
- Traceability from journey-map pain point to impact map node so requirements remain prioritisable.
