# Impact Map Construction

An impact map is a four-level mind map that holds the chain *Why → Who → How → What*. It is a tool for *cutting* scope, not for collecting it. The discipline matters more than the visual: every level must connect upward to the goal and downward to a falsifiable bet, otherwise the map is a shopping list with branches.

## The Four Levels

1. **Why (Goal).** One measurable business outcome with a target value and a date. Goals are SMART: Specific, Measurable, Action-oriented, Realistic, Timely. The goal is the root, and there is exactly one. Multiple roots mean multiple maps. "More users" is not a goal; "150K active players in segment X by end of Q3" is.
2. **Who (Actors).** The people whose behaviour can move the metric. Use Cockburn's three classes: **primary** actors whose goals are fulfilled by the service; **secondary** actors who provide a service to primaries (fraud, support, settlement); **off-stage** actors who do not transact but can block or enable (regulators, senior decision-makers, partners). Define actors in this order of preference: specific individual → user persona → role or job title → group or department. Avoid generic terms like "users".
3. **How (Impacts).** The *behaviour change* the actor must make for the goal to move. Impacts are verb phrases from the actor's vantage point and ideally express a *change* from current behaviour, not the behaviour itself: "invite a friend without leaving the level", "submit a structured order instead of free-text", "renew without calling support". Negative impacts (preventing actors from obstructing) are first-class — list ways an actor could *prevent* the goal as well as ways they could enable it.
4. **What (Deliverables).** The product, feature, training, policy change, or campaign that *might* produce the impact. Deliverables are bets, not commitments. They are the *third* thing on the map, never the first.

## Goal Writing

A good goal answers: *who measures it, by when, what is the current value, and what is the target?* Capture each goal with five fields — metric name, owner, measurement method, current baseline, target with deadline — before drawing actors. If a goal cannot be expressed with a baseline and a target, the team is not ready to map; run a measurement workshop first.

When stakeholders arrive with a feature list ("we need a referral programme"), reverse-engineer toward the goal by asking *whose behaviour will this change, in what way,* and *why is that change valuable.* Keep asking until the answer reaches money, regulation, or strategic position. That answer is the goal candidate. Discard features whose behaviour-chain breaks before reaching the goal.

## Building the Map: Order of Construction

Construct strictly top-down, breadth-first:

1. Lock the goal. Write it on the centre node with metric, baseline, target, deadline.
2. List candidate actors as a flat ring. Tag each with primary / secondary / off-stage. Drop actors who cannot decide or whose decisions cannot move the metric.
3. For each actor, generate 3–7 candidate impacts. Force at least one *negative* or obstructive impact per important actor — what they could do to prevent the goal — because hidden blockers usually live there.
4. Only after impacts are stable, brainstorm deliverables. A deliverable that does not connect to a specific impact is parked in a separate "ideas" list, not added to the map.

Do not add a deliverable level to an actor whose impacts are still vague. Vague impacts produce shopping-list deliverables.

## Cutting Rules

The map's value is what it *removes*. Apply these cuts in order each session:

- Drop actors with no measurable influence on the metric.
- Drop impacts that do not move the actor toward the goal even if true.
- Drop deliverables for which there is no plausible mechanism from delivery to impact.
- Drop impacts and deliverables that fall outside the current milestone's time horizon.

After cutting, the map should be readable in one breath, with no branch deeper than four levels.

## Measurability at Every Level

Apply the SMART test not only to the goal but to each impact. For each impact, capture an observation method ("how would we know this changed?") and a directional target ("by how much, in what window?"). If the team cannot describe an observation method, the impact is still a wish, not a target. Common observation methods: log signals, support-ticket reduction, conversion deltas, survey-mounted behavioural questions, sales pipeline movement.

## Treating the Map as a Roadmap

The map encodes two assumption layers:

- **Delivery assumption**: the deliverable will produce the impact.
- **Impact assumption**: the impact will move the goal.

Each assumption layer is a candidate kill point. After a deliverable ships, measure the actor's behaviour first. If the impact did not occur, the *delivery* assumption is wrong — the deliverable does not change behaviour. If the impact occurred but the goal did not move, the *impact* assumption is wrong — that behaviour does not actually drive the metric. Each diagnosis points to a different next move; do not collapse them.

Schedule a review at a fixed cadence (Tom Gilb's 2% rule of overall investment per iteration is a useful upper bound on bet size). At each review:

- Compare current metric to target trajectory.
- Decide: continue this branch, switch to a different impact for the same actor, switch actor, or rethink the goal.
- If the goal is reached early, stop. Unspent budget is a win, not a deficit.

## Alternatives Discipline

For every actor, before committing to a deliverable, force the team to generate at least three alternative impacts. For every impact, force at least three alternative deliverables. The map is a divergence tool first and a convergence tool second; collapsing too quickly produces the most expensive plans.

A useful prompt during convergence: *"If we hit the goal with a completely different deliverable, would we still be happy?"* If yes, the deliverable is a bet, not a requirement. Treat it as such.

## Working Sessions

A good map is built in two sessions, not one:

- Session 1: define the goal, baseline, target, and measurement plan. No actors, no deliverables. Output is one sentence and a measurement protocol.
- Session 2: actors and impacts. Stop when impacts stabilise. Park the deliverables list until the team has slept on the impacts.

For groups larger than six, split into pairs, build maps independently for fifteen minutes, then merge. Merging surfaces alternative actors and impacts that a single group misses.

## When the Map Is Done for Now

A map is "ready to act on" when:

- The goal carries a baseline and target with a date.
- Each surviving actor has at least one impact and one obstructive impact considered.
- Each surviving impact has an observation method and a directional target.
- At least one deliverable per top-priority impact has a kill condition for the next iteration.
- The whole map fits on one page and a stakeholder unfamiliar with the project can follow the chain from any deliverable back to the goal.

If any condition fails, the map is not ready; it is in progress. Resist shipping work driven by an incomplete map.

## Source Grounding

- Adzic's four-level *Why → Who → How → What* impact map structure.
- Cockburn's primary / secondary / off-stage actor classification used by Adzic.
- SMART goal framing (Berkun) applied to both the central goal and impacts.
- Behaviour-change framing for impacts (change from current behaviour, not current behaviour itself).
- Adzic's two-layer assumption model (deliverable to impact, impact to goal) for review and pivot decisions.
- Gilb's small-iteration sizing as a frame for review cadence.
