# Frontstage and Backstage Alignment

Customers experience a single service; staff deliver it through dozens of handoffs across a stage they cannot see. Stickdorn et al. extend Shostack's stage metaphor explicitly: a service moment, like a play, consists of what is happening *front of stage* and the multiple *backstage* processes that make it possible — cleaning, inventory, training, IT, supply. Misalignment between the two stages is the most common cause of "good UX, bad service" complaints. This reference encodes the alignment moves that the blueprint must capture.

## The Alignment Triangle

Every customer action sits at the apex of a triangle:

- **Frontstage role** — the staff member or interface in contact with the customer.
- **Backstage role** — the staff or system producing what frontstage delivers.
- **Support service** — the dependency that lets backstage produce on time (IT, supply, finance, partner, regulator).

If any of the three is unnamed, the action is not yet designed. The most common gap is a frontstage role with no clearly identified backstage producer — a promise the customer will hear, with no one accountable for honouring it.

## Service Evidencing Across the Line of Visibility

A backstage process exists for the customer only through *evidence*. Service evidencing — promoting once-inconspicuous backstage work into visible signals (the chocolate on the pillow, the "your bag is being prepared" status, the cleaner's signed checklist on the bathroom door) — converts hidden labour into perceived value. Two design moves:

- **Surface high-value backstage work** the customer would otherwise miss. If your team folds towels into swans and the customer only sees a flat towel, the swan never paid for itself.
- **Conceal low-value backstage friction** the customer should not have to absorb. Internal handoffs, system delays, approval queues, and escalation paths belong below the line of visibility unless surfacing them serves the customer.

A blueprint annotates each evidence cell with its *deliberate visibility decision*: surfaced, concealed, or accidental. Accidental visibility is a design defect.

## Handoff Specification

For every line crossing (interaction, visibility, internal), specify:

| Field | Purpose |
|-------|---------|
| Trigger | What event hands the work over (customer click, queue arrival, system flag, time elapsed). |
| Carrier | What physically crosses (ticket, message, form, instruction, voice call, alert). |
| Owner on the receiving side | The named role responsible for picking it up. |
| Acknowledgement | How the sender knows it was received and is being acted on. |
| SLA | The expected response time the customer experience depends on. |
| Fallback | What happens when the SLA is missed. |

A handoff missing any field is a candidate fail point. Audit periodically — handoffs degrade silently as systems and rosters change.

## Frontstage Authority

The frontstage role can only deliver on promises within its authority. Map authority explicitly per role per stage:

- What can the role decide unilaterally (refund cap, override, exception, expedite)?
- What requires escalation, to whom, with what response time?
- What is forbidden, and is the prohibition known to the customer at the line of interaction?

Authority gaps — promises the frontstage role makes but cannot keep — are visible to the customer as broken trust. Either expand the authority or change the promise; do not leave the gap.

## Backstage Producer Accountability

Each backstage role has a production output that crosses the line of visibility into a frontstage interaction. Capture per backstage role:

- **Output** — what they produce (room ready, claim approved, parts shipped, account opened).
- **Cycle time** — how long production takes under normal load.
- **Quality variance** — how often the output is wrong or late.
- **Demand source** — what triggers production and how visible the trigger is to backstage in advance.

Backstage roles whose demand source is invisible until it arrives ("we get the request when the customer is already on the phone") will produce inconsistent output regardless of skill.

## Coherency Across Channels

Stickdorn et al. emphasise *coherency* across touchpoints rather than uniformity. The frontstage-backstage alignment job is to ensure the same customer perception across channels even though the underlying production differs:

- Voice support and self-service portal must surface the same authority limits.
- Branch staff and call-centre staff must read the same customer record.
- Web and mobile channels must show the same status and the same recovery options.

When channels diverge, the customer learns to "shop" channels, picking the one with the loosest interpretation of policy. This is a symptom of misalignment, not customer cleverness.

## Co-Creation Across the Two Stages

A blueprint built by one stage produces alignment failure. Co-create with frontstage, backstage, and support representatives in the room. Practical moves:

- Walk the actual service with frontstage staff before the workshop. Observe at least one full customer cycle.
- In the workshop, draft the blueprint top-down (customer first), but invite backstage to challenge each frontstage commitment for feasibility before moving to the next column.
- Capture disagreements as design defects, not interpersonal issues. Most of them are real — frontstage makes a promise backstage cannot keep within the SLA.

The co-creation produces a "living document" both stages own; without that ownership, the blueprint will be silently abandoned within months.

## Service Roleplay as an Alignment Tool

When the blueprint reveals contested handoffs, walk them through with roleplay rather than debate. Staff enact the customer scenario, switching between customer, frontstage, and backstage roles, with prompt cards setting persona and mood. Roleplay surfaces missing authority, missing information, and missing handoffs faster than diagram review and produces shared ownership over the fix.

## Auditing an Existing Service

For a service already in production, audit alignment with the following sweep:

1. List every customer-facing promise (advertising, contracts, scripts, messaging copy).
2. For each, identify the frontstage role responsible.
3. For each frontstage role, identify the backstage producer.
4. For each backstage producer, identify the support service.
5. Mark every gap. Each gap is a class of customer complaint waiting to happen.

The output is a *promise audit* that can be prioritised by customer impact and used to drive the next blueprint iteration.

## When Alignment Is "Done for Now"

- Every customer action has a complete triangle (frontstage, backstage, support).
- Every line crossing has a fully specified handoff.
- Every frontstage role has an authority map.
- Every backstage role has output, cycle time, variance, and demand source documented.
- Channels are coherent on authority limits and customer record.
- The blueprint is co-owned by frontstage, backstage, and support representatives.

## Source Grounding

- Stickdorn et al.'s stage metaphor: front of stage, backstage, and the play-rehearsal framing of service delivery.
- Service evidencing — deliberately promoting inconspicuous backstage work into visible signals to influence customer perception.
- Lines of interaction, visibility, and internal interaction inherited from Shostack's blueprint and reused in This Is Service Design Thinking.
- Coherency over uniformity across touchpoints as the alignment objective.
- Co-creation across departments as the practice that produces an owned, "living" blueprint.
- Service roleplay as a staging technique to surface missing handoffs and authority gaps.
