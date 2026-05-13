# Service Failure and Recovery

Most services are designed for the happy path; recovery is improvised under pressure by the frontstage role with the least authority. Designed recovery converts failures into trust events. Shostack's blueprint convention marks fail points with an "F" so that recovery can be designed alongside the rest of the service rather than after launch. This reference encodes the failure taxonomy, severity scoring, and recovery patterns that hang off those marks.

## Failure Taxonomy

Six failure classes — distinct because each has a distinct corrective:

| Class | Description | Typical fix |
|-------|-------------|-------------|
| Technical | A system fails or is unavailable. | Resilience, redundancy, status communication. |
| Capacity | Demand exceeds supply (queue, stock, staff). | Forecasting, surge plan, demand shaping. |
| Knowledge | Staff cannot answer or decide. | Training, knowledge base, authority delegation. |
| Handoff | Work is dropped or duplicated between roles. | Tracked handoff, SLA, ownership clarification. |
| Promise | What was promised is not what is delivered. | Promise audit, copy fix, training. |
| Trust | Customer doubts safety, motive, or fairness. | Evidence, transparency, recovery generosity. |

Misclassifying a failure leads to wrong fixes — adding training to a capacity problem, or adding capacity to a trust problem. Classify before specifying the fix.

## Where Failures Live on the Blueprint

Failures cluster predictably:

- **At line crossings** (interaction, visibility, internal). Most handoff failures live here. Review every crossing as a candidate fail point.
- **At wait points**. Time itself is a fail-amplifier; the customer's emotional reading of a queue is harsher than the queue's actual length.
- **At moments of truth**. Carlzon's emotionally loaded interactions amplify minor failures into trust events. A small failure at a moment of truth produces a worse customer perception than a major failure outside one.
- **Where channels diverge**. A promise made in one channel and unmet in another is a Promise failure, not a Technical one.

Mark each fail-point candidate with an "F" on the blueprint with a code referencing the recovery record.

## Severity Scoring

For each fail point, score on three axes 1–5:

- **Customer harm** — financial, time, safety, emotional. 5 = the customer leaves.
- **Frequency** — how often the fail point fires in current operations.
- **Recoverability** — how recoverable the failure is once detected. 5 = irrecoverable; 1 = trivially fixed mid-interaction.

Combined risk = harm × frequency × recoverability. Treat the top decile as design-must-fix; design recovery for the next quartile; accept the rest with monitoring.

## Detection Before Recovery

Recovery requires detection. For each fail point, document:

- **Detection signal** — what observable change tells anyone that the failure has fired (system alert, customer complaint, repeat call, sentiment, queue length, ticket re-open).
- **Detector** — the role or system that catches the signal.
- **Detection latency** — how long between failure and detection.

Most "service recovery" programmes are actually *complaint handling*; they only detect failures the customer reports. Reduce detection latency by adding upstream signals (a system error log, a frontstage flag, a queue threshold alert) so recovery can begin before the customer escalates.

## Recovery Patterns

Match the recovery move to the failure class:

- **Technical**: status communication first, restore second. Customers tolerate technical failure; they do not tolerate silence. Build the status channel before the redundancy.
- **Capacity**: shape demand (off-peak incentives, appointment-only, virtual queues with accurate wait estimates). Adding capacity is expensive and the problem reappears.
- **Knowledge**: surface authority to the frontstage role at the moment of need (knowledge base lookup, decision tree, escalation hot-line). Training alone does not solve it because staff turn over.
- **Handoff**: make handoffs trackable end-to-end, with owner notification on miss. The cure is structural, not cultural.
- **Promise**: fix the promise. If the service genuinely cannot keep it, retract it from copy and scripts; do not paper over with apology. Consistent over-promising is itself a Trust failure in waiting.
- **Trust**: invest in evidence (audit, certification, transparency artefacts), not reassurance. Reassurance from the party under suspicion does not move trust.

## The Recovery Record

For each design-must-fix fail point, write a recovery record:

- Failure description and class.
- Detection signal, detector, latency.
- First responder role and authority cap.
- Recovery move script or system action.
- Customer-visible communication at each stage (acknowledgement, progress, resolution, follow-up).
- Compensation policy if applicable, with cap.
- Escalation path and trigger.
- Learning loop — how the failure data feeds back into design.

Recovery without a learning loop produces the same failure indefinitely. The loop is the difference between recovery as service and recovery as overhead.

## Recovery Generosity Calibration

Compensation sized too small registers as insulting; sized too large creates moral-hazard incentives for customers to provoke failures. Calibrate:

- For minor failures, recovery generosity should noticeably exceed the customer's loss (apology + small gesture beyond replacement).
- For major failures, compensation should be paired with structural reassurance (audit findings, change record) — money alone does not restore trust.
- For Trust failures, transparency outperforms compensation. Show the audit, name the fix, accept oversight.

## Recovery Authority at the Front

Frontstage staff need pre-authorised recovery authority calibrated to the most common fail points they handle. The Carlzon-era convention — empowering frontline staff to resolve within a known cap, on the spot, without escalation — is operationally the largest lever in service recovery. Without it, the recovery process itself becomes the secondary failure: long hold times, repeated explanations, escalation theatre.

For each frontstage role, capture the recovery authority cap in the same record as ordinary authority, and refresh it against current case mix at least annually.

## Failure Modes That Become Trust Events

A failure becomes a *trust event* — a positive shift in the customer's relationship — only when:

- The failure was acknowledged by the service first, not the customer.
- Recovery exceeded the customer's expectation in pace or generosity.
- The communication treated the customer as informed adult rather than complaining party.
- The fix was visible: the customer sees that something changed because of their experience.

Most "we recovered well" stories are actually "we avoided escalation" stories. The discriminator is whether the customer's relationship deepened.

## Anti-Patterns in Recovery

- Apology scripts without authority ("I'm sorry, I'll have to escalate").
- Recovery only on customer complaint; no upstream detection.
- Compensation policy hidden from the frontstage role responsible for executing it.
- Treating Promise failures as Knowledge failures and adding training instead of fixing the promise.
- Aggregated complaint dashboards with no failure-class taxonomy, so the same fail point appears in five buckets.
- Closing tickets without feeding the failure record back into the blueprint.

## When Recovery Design Is "Done for Now"

- Every fail point on the blueprint has a class, severity score, and detection signal.
- Top-decile fail points have full recovery records with first-responder authority and customer-visible communication scripted.
- Frontstage authority caps cover the common recovery moves without escalation.
- A learning loop feeds detected failures back into the next blueprint review.

## Source Grounding

- Shostack's "F" fail-point convention on the blueprint, used to design recovery alongside primary flow.
- Stage metaphor and the line of visibility / line of interaction as natural boundaries where handoff and Promise failures concentrate.
- Carlzon's moments-of-truth framing as fail-point amplifiers.
- Service evidencing as the mechanism for Trust recovery (transparency outperforms reassurance).
- Frontstage authority delegation as the operational lever for in-the-moment recovery.
- Coherency-across-channels as the discriminator for Promise failures.
