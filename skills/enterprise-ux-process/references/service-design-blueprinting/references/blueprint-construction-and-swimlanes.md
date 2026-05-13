# Blueprint Construction and Swimlanes

A service blueprint is a structured cross-section of a service over time. It traces back to G. Lynn Shostack's 1984 article "Designing Services That Deliver" and is the oldest formal experience-mapping technique. Its purpose, in Shostack's words, is to surface the lack of *systematic design and control* that produces most service problems — to identify fail points before they happen and to give management a higher-level view of service delivery. This reference fixes the lanes, the lines, and the granularity rules so blueprints become coordination tools rather than decorative flowcharts.

## The Five Lanes

Top to bottom, in this order:

1. **Physical / Digital Evidence** — artefacts the customer perceives at each step: signage, ad, paperwork, lobby, room, screen, receipt, message, packaging, voice prompt, employee dress, vehicle. In Shostack's hotel example these include the cart for bags, desk, elevators, key, room, bill — every tangible cue the customer encounters.
2. **Customer Action** — what the customer is doing in their own words and goals (make reservation, arrive, give bags to bellperson, check in, go to room, call room service, receive food).
3. **Frontstage** — the people, screens, and channels the customer interacts with directly. The boundary above this row is the *line of interaction*.
4. **Backstage** — the staff and systems whose work the customer does not see but whose output reaches the customer. The boundary above this row is the *line of visibility*.
5. **Support Processes** — internal services consumed by backstage: IT, finance, supply, vendor, legal, regulatory. The boundary above this row is the *line of internal interaction*.

The three lines are crossings, not decorations. Every crossing is a handoff and must have an owner, a trigger, and a service-level expectation. A blueprint that draws the lines but never identifies the crossings has paid only the visual cost.

## Time Axis

The columns are stages or steps from the customer's journey. Use the same stage labels as the source journey map so the artefacts cross-reference. Do not mix time grains — if one column is "30 seconds" and the next is "two days", split. Mixed time grains hide the queueing and waiting points where most service failures live.

## Granularity Rule

Granularity is set by the question the blueprint must answer:

- **Strategy / discovery**: 6–12 columns covering the end-to-end service. Lanes filled at one-line granularity. Used to find which phase of the service to redesign.
- **Design**: 15–40 columns at workflow granularity. Lanes filled with specific roles, systems, and artefacts. Used to specify the redesign.
- **Operations**: every column an executable step. Used to brief, train, and audit the running service.

Pick one. A single blueprint cannot be all three at once — the strategy view is illegible at operations granularity, and the operations view collapses under the weight of strategy abstractions. Maintain three views over the same service rather than one omnibus diagram.

## Construction Order

Build top-down following the customer, not bottom-up following systems:

1. Lock the **scenario** — actor, trigger, end state. One scenario per blueprint. Multi-scenario services produce one blueprint each.
2. Lay out **customer action** columns across the time axis, using verbs from the customer's vantage point.
3. Add **physical / digital evidence** above each column — what the customer perceives there. Empty cells are design defects.
4. Add **frontstage** roles below — who the customer touches at each step. If frontstage is "system", name which system and which screen.
5. Add **backstage** support — who or what produces what frontstage delivers, and how the work crosses the line of visibility.
6. Add **support processes** — what backstage depends on and what is shared with other services.
7. Mark **fail points** (Shostack's "F" markers) where the service can break or become inconsistent. Wait points and queues count as fail points.

Stop at the deepest lane that materially affects the customer's experience. If support processes are stable and shared, they can be referenced rather than detailed.

## The Three Lines as Design Constraints

- **Line of interaction**: every customer action must cross it; if it does not, the customer is not actually doing anything at that step (remove or merge the column).
- **Line of visibility**: anything above is co-designed with the customer's perception in mind; anything below is invisible but its quality reaches the customer through frontstage. Note where backstage decisions leak across the line accidentally (e.g., backend errors becoming customer-visible messages).
- **Line of internal interaction**: marks where the service depends on a separately-managed function. SLAs at this line are the most-skipped governance step in service design and the most common source of late delivery.

## Handoff Specification

Every line crossing is a handoff. Specify each one with:

- **Trigger** — what event initiates the handoff (customer action, system event, time).
- **Carrier** — what crosses the line (form, message, ticket, notification, instruction).
- **Owner** — the role on the receiving side responsible for picking it up.
- **Expected response time** — the SLA the customer-facing experience depends on.
- **Failure mode** — what happens when the SLA is missed (escalation, default action, customer notification).

Unspecified handoffs are the dominant cause of "transitional volatility" — Kalbach's term for the disorienting reorientation a customer experiences when moving between touchpoints. Each unspecified handoff produces some volatility; enough volatility makes a coherent service feel like multiple disconnected ones.

## Fail Points and Wait Points

Mark fail points explicitly on the blueprint, following Shostack's convention. Two classes:

- **Process fail point**: the service can produce an incorrect or inconsistent output (wrong room, missing bag, mis-routed call).
- **Wait point**: the service is waiting on something — a queue, a backstage handoff, a third party. Wait points are not failures themselves but they are where customers form the worst impressions.

For each fail point, document the recovery move at the same column (see the service-failure-and-recovery reference).

## The Living Document

Blueprints work only when they are revised periodically. The "living document" framing applies in two ways: the blueprint must be reviewed against changes in customer behaviour and channel mix, and it must be co-owned by the teams whose work it describes. A blueprint produced by one designer in isolation, however accurate, will be ignored. Build collaboratively: a co-creation workshop with frontstage, backstage, and support representatives produces a blueprint the teams will actually maintain.

## Coherency Over Uniformity

Strive for coherency in the conception and design of the service across touchpoints, not for uniform sameness. The customer should experience the service as one organisation; that does not mean every channel looks identical. Coherency is in the promise, the evidence cues, the recovery posture, and the language. Uniformity for its own sake costs flexibility without buying customer perception.

## When the Blueprint Is Done for Now

Use these gates:

- Every column has filled cells in evidence, customer action, and frontstage. Backstage and support are filled where the customer's experience depends on them.
- Every line crossing has trigger, carrier, owner, SLA, and failure mode.
- Fail points and wait points are marked, with recovery moves documented.
- The granularity matches the audience and decision the blueprint must support.
- An owner is named and a review cadence is scheduled.

A blueprint that cannot pass these gates is in progress, not done; do not commit to delivery from it.

## Source Grounding

- Shostack's original blueprint structure and the "F" fail-point markers from her 1984 article and the hotel example.
- Stickdorn et al.'s lane structure: physical evidence, customer action, frontstage, backstage, support processes.
- Lines of interaction, visibility, and internal interaction as boundary markers between lanes.
- Kalbach's transitional-volatility framing of unspecified handoffs as a source of disjointed customer experience.
- Co-creation and "living document" framing of the blueprint produced collaboratively across departments.
- Coherency-not-uniformity as the design objective across touchpoints.
