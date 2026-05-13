# Drill Cadence and Rotation

The drill program is a calendar, not a wish. Every drill is scheduled in advance, owned by a named coordinator, and the calendar is reviewed quarterly.

## Cadence (Default)

| Drill type | Cadence | Audience |
|---|---|---|
| Standard scenario drill | monthly | primary on-call + comms-lead |
| Sev-1 scenario | quarterly | full incident roster + observers |
| Paper / tabletop (regulator, model deprecation) | bi-monthly | full roster + legal |
| Onboarding drill | once per new on-call | individual; within first 30 days |
| Off-hours drill | bi-annually | weekend / late-night on-call |
| Cross-team drill (with vendors / customers) | annually | named cross-functional roster |

## Scenario Rotation

The catalogue has 10 scenarios. Standard cadence cycles through them in 10 months — so the same scenario is not run twice in any 9-month window. Adjustments:

- A scenario that scored < 60% on its last run is repeated within 2 months until ≥ 80%.
- A scenario tied to a recent incident class is reordered to be the next drill (immediately while learnings are fresh).
- A new scenario added when a real incident introduces a class not in the catalogue.

## Owner and Roles

- **Drill coordinator** — owns the calendar, the planning, and the debrief. Rotates yearly.
- **Drill observers** — 2–3 per drill, drawn from non-responder ranks. Observers are scored too: did they coach (bad) or note (good)?
- **Drill kill-switch holder** — one person, designated per drill, with authority to stop the drill if it threatens to become a real incident. Documented in the drill plan.

## Success Criteria

- 80%+ pass on rubric for known scenarios.
- 60%+ pass on rubric for unfamiliar scenarios.
- Action items from drills close at 70%+ within a quarter.
- A new on-call passes onboarding drill within 30 days.

## Escalation

- A drill that scored < 60% on a known scenario for two consecutive runs is escalated to AI leadership; engineering investment is required.
- A drill that exposed a missing operator surface (e.g., no quota-cap UI) is escalated and the surface becomes a release-blocking item.
- A drill that revealed a comms gap (e.g., regulator clock missed) is escalated to legal + comms-lead.

## Documentation

- Every drill produces: a plan (pre-drill), a scoresheet (post-drill), and a debrief writeup (within 24h).
- Drill findings join `ai_drill_findings` tracker; same review cadence as `ai_postmortem_actions`.
- The drill catalogue's scenarios are versioned; updates are logged.

## Anti-Patterns

- Drills slip; the calendar drifts; quarterly drill happens twice a year.
- Same coordinator forever — pattern-matches the team, hides their own blind spots.
- Observers turn into coaches — drill measures coaching ability, not on-call ability.
- Off-hours drills never happen — on-call surprised every weekend incident.
- Drill findings tracked in a different tracker than postmortems — leadership can't see the whole picture.
- Drills always run on staging — real-environment quirks (region failover, cache state) never tested.
- No kill-switch holder named; drill threatens production; everyone hesitates.
