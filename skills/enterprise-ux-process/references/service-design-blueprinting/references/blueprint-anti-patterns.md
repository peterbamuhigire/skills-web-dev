# Blueprint Anti-Patterns

Patterns that produce a blueprint-shaped artefact without the design value. Each entry: symptom, cause, correction. Most of these failures come from missing one of Shostack's original purposes — that the blueprint should identify *fail points ahead of time* and give management a *higher-level view of service prerogatives*. A blueprint that does neither is decoration.

## 1. Flowchart in Disguise

- **Symptom**: a single-lane diagram labelled "blueprint" with arrows between boxes.
- **Cause**: skipped customer-action and evidence rows; jumped to systems.
- **Correction**: redraw with five lanes (evidence, customer action, frontstage, backstage, support). If any lane is empty, do not call it a blueprint.

## 2. Empty Evidence Row

- **Symptom**: customer actions populated, evidence cells blank or "email confirmation" repeated.
- **Cause**: evidence treated as decorative.
- **Correction**: at every customer action, name the specific physical, digital, human, or sensory artefact the customer perceives. Missing cells are design defects, not stylistic gaps.

## 3. Manager-Only Workshop

- **Symptom**: the blueprint was drawn in a meeting with managers and consultants only.
- **Cause**: co-creation skipped because "it would take too long".
- **Correction**: invite frontstage and backstage representatives to co-author. The blueprint they did not co-create is one they will not maintain. A blueprint without an internal owner ages out within a quarter.

## 4. Lines Without Crossings

- **Symptom**: lines of interaction, visibility, and internal interaction are drawn but the work that crosses them is not specified.
- **Cause**: visual convention treated as governance.
- **Correction**: for every line crossing, document trigger, carrier, owner, acknowledgement, SLA, and fallback. Unspecified handoffs are the dominant cause of transitional volatility.

## 5. Uniform Time Grain

- **Symptom**: every column is one step regardless of duration; a thirty-second screen interaction sits next to a two-day waiting period.
- **Cause**: visual layout prioritised over time fidelity.
- **Correction**: split mixed grains. Wait points need their own columns because that is where customer perception forms.

## 6. No Fail Points

- **Symptom**: the blueprint shows a clean happy path with no "F" markers.
- **Cause**: failure analysis postponed; team optimistic about controlled rollout.
- **Correction**: deliberately mark fail points at line crossings, wait points, and moments of truth. A blueprint without fail points has not done Shostack's primary job.

## 7. Promise Without Producer

- **Symptom**: marketing copy or scripts promise something the blueprint does not show being produced backstage.
- **Cause**: outside-in design without inside-across alignment; promise written before production was modelled.
- **Correction**: run a promise audit (catalogue every customer-facing promise, trace each to a frontstage role, then to a backstage producer, then to a support service). Each broken chain is a Promise failure waiting to happen.

## 8. Authority Cap Hidden from Front-Line

- **Symptom**: the blueprint specifies a recovery generosity (e.g., "refund up to $50") but front-line staff cannot find or apply it.
- **Cause**: policy designed in one team, executed by another, no propagation.
- **Correction**: surface authority caps in the same artefact the front-line uses at the line of interaction. Refresh against current case mix annually.

## 9. Strategy/Operations Conflation

- **Symptom**: a single blueprint tries to be the strategic overview, the design specification, and the operational runbook at once.
- **Cause**: one diagram per service treated as canonical.
- **Correction**: maintain three views over the same service at three granularities (strategy 6–12 columns, design 15–40 columns, operations every executable step). Same blueprint family, different audiences.

## 10. Channel-Inconsistent Blueprint

- **Symptom**: web, branch, and call-centre channels each have their own blueprint with different authority caps, different scripts, different recovery options.
- **Cause**: blueprints owned by channel teams; no service-level integration.
- **Correction**: hold channels coherent on customer-visible policy (authority caps, status, recovery options, customer record). Channel-specific differences belong in production, not in customer-facing promise.

## 11. Backstage Black Box

- **Symptom**: backstage row reads "operations team handles".
- **Cause**: blueprint authored by customer-experience function with no backstage participation.
- **Correction**: backstage rows must name role, output, cycle time, and demand source. "Ops handles it" is not a design.

## 12. Accidental Visibility

- **Symptom**: a backstage system error becomes a customer-facing message; an internal status code appears in a confirmation email; queue length is visible only to staff but not to customers waiting in it.
- **Cause**: the line of visibility is uncontrolled — nothing decides what crosses it.
- **Correction**: annotate every evidence cell with a deliberate visibility decision (surfaced, concealed, accidental). Fix accidentals in the next iteration.

## 13. Wallpaper Blueprint

- **Symptom**: a wall-sized blueprint sits in the design studio, referenced for tours but not for decisions.
- **Cause**: blueprint produced as deliverable, not as alignment artefact.
- **Correction**: cut to the granularity of the decisions actually being made. The blueprint is finished only when teams have used it to decide, not when it is printed.

## 14. Recovery as Apology Script

- **Symptom**: recovery is "I'm sorry, I'll have to escalate".
- **Cause**: recovery designed without authority; treated as PR rather than service.
- **Correction**: design recovery alongside the failure with first-responder authority, customer-visible communication, and learning loop. Recovery without authority is the secondary failure.

## 15. EX Layer Missing

- **Symptom**: the blueprint shows frontstage roles but not their tools, authority, information, or incentive context.
- **Cause**: customer-experience design without inside-across alignment.
- **Correction**: pair each frontstage role with the four-dimension EX audit. CX promises that the EX layer cannot support are noise.

## 16. Stale Blueprint

- **Symptom**: the blueprint shows channels, systems, or roles that no longer exist.
- **Cause**: produced once, never revised; no owner.
- **Correction**: assign an owner; schedule a periodic review (typically quarterly). The blueprint is a *living document* by design — Stickdorn et al.'s framing — not an asset.

## 17. Confused Tool Choice

- **Symptom**: a blueprint is being used to track product-feature decisions, or a journey map is being used to track multi-actor handoffs.
- **Cause**: one tool overloaded for several jobs.
- **Correction**: separate the artefacts. Single-actor experience belongs in a journey map. Multi-actor handoffs belong in a service blueprint. System interactions belong in an ecosystem map. Goal/behaviour decisions belong in an impact map.

## 18. No Learning Loop

- **Symptom**: failures are recovered but the same fail point recurs unchanged month after month.
- **Cause**: recovery records do not feed back into blueprint revision.
- **Correction**: at each periodic review, fold detected failures and recovery records into the blueprint. The blueprint that does not learn is the one that ages out fastest.

## Source Grounding

- Shostack's blueprint as a tool to identify fail points ahead of time and give management a higher-level view of service.
- Stickdorn et al.'s five-lane structure (evidence, customer action, frontstage, backstage, support) and the three lines (interaction, visibility, internal interaction).
- Kalbach's transitional-volatility framing for unspecified handoffs and inconsistent touchpoints.
- Co-creation and "living document" framing — blueprint as collaboratively owned artefact periodically revised.
- Coherency-not-uniformity across channels as the alignment objective.
- Inside-across EX/CX alignment requiring frontstage tools, authority, information, and incentives to support customer-facing promises.
