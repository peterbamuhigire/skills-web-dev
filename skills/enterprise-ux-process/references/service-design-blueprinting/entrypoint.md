---
name: service-design-blueprinting
description: Use when designing or fixing a service that crosses customer touchpoints, frontstage staff, backstage operations, and supporting systems — produces a service blueprint with evidence, failure points, recovery plays, and CX/EX alignment.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Service Design Blueprinting
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- A service spans multiple channels (web, app, phone, in-person, partner) and the customer is dropping moments-of-truth.
- Customer satisfaction stalls despite UX investment — the bottleneck is operations, staff, or back-office systems.
- A new service is being launched and the team needs to coordinate frontstage and backstage roles before go-live.
- Failure modes are repeating; recovery is improvised, inconsistent, and damaging trust.
- Employee experience is dragging customer experience: handoffs, tools, and incentives are misaligned with the promised customer journey.
- A co-creation workshop with customers, staff, and partners is needed to make a service tangible.

## Do Not Use When

- The artefact under change is a single screen with no operational or staff dependency — use a UX skill.
- The decision is "should we offer this service at all" — use `experience-mapping` or `product-discovery` first to validate demand and impact.
- The work is purely a technology integration with no customer-visible behaviour change.

## Required Inputs

- A specific service scenario with named primary actor, trigger, and end-state.
- Channels in scope (digital, physical, human, partner) and channels explicitly out of scope.
- Access to frontstage staff, backstage staff, and at least one customer who has recently lived the journey.
- Current performance data: volumes, conversion or completion rates, SLA breaches, complaint themes.
- Constraints: regulatory, contractual, system, and union/HR limits on staff role design.

## Workflow

1. Read this SKILL.md, then load only the references for the active stage.
2. **Frame the scenario.** One actor, one trigger, one outcome, one time horizon. Multi-actor scenarios get one blueprint per primary actor with cross-references.
3. **Walk the journey first.** Use a journey map (or import one from `experience-mapping`) — the blueprint is layered *under* the customer-action row, not instead of it.
4. **Lay the swimlanes.** Customer Action → Frontstage (line of interaction) → Backstage (line of visibility) → Support Processes (line of internal interaction) → Evidence. See `references/blueprint-construction-and-swimlanes.md`.
5. **Populate evidence.** Every customer action has at least one physical, digital, or human artefact that signals the service is happening. Missing evidence is a design defect.
6. **Tag failure points.** Mark every step where the service can break: technical, human, handoff, capacity, knowledge. Tag severity and frequency. See `references/service-failure-and-recovery.md`.
7. **Design recovery.** Each high-severity failure point gets a named recovery play, an empowered owner, and a customer-visible signal.
8. **Align frontstage/backstage operations.** For each customer action, name the role on stage, the role behind the line, the system in support, and the SLA between them. See `references/frontstage-backstage-alignment.md`.
9. **Check CX/EX alignment.** For each frontstage role, audit tooling, authority, incentive, and information access. EX gaps that block CX are first-class defects. See `references/cx-ex-alignment.md`.
10. **Co-create and stress-test.** Run a workshop with customers, frontstage, backstage, and support. Walk a real case end-to-end; mark every disagreement as a design issue.
11. **Plan implementation as a service, not a feature.** Each change has a customer signal, a staff signal, a system change, and a metric.

## Quality Standards

- The blueprint fits one large page; if it does not, scenario scope is too wide — split.
- Every customer action has an evidence cell; no blanks.
- Every line of visibility crossing has a named handoff with SLA.
- Every failure point has a recovery owner with the authority to execute it.
- Frontstage staff have read access to the data the customer expects them to know.
- Metrics include both customer (completion, satisfaction, abandonment) and employee (handle time, escalation, error) measures.

## Anti-Patterns

- One-lane "blueprint" that is actually a flowchart with no backstage and no evidence.
- Blueprint drawn without staff in the room — the backstage will be wrong.
- Recovery plays that require manager approval for every case — the line empowerment is broken.
- Ideal-state blueprint with no current-state baseline — improvements cannot be measured.
- Treating channels as parallel ladders rather than a coordinated set — customers experience the *service*, not the channels.
- Designing CX without auditing EX — promises the staff cannot keep.
- Mistaking the blueprint for the deliverable. The blueprint is a coordination tool; the deliverable is the lived service.

## Outputs

- Current-state service blueprint with swimlanes, evidence, failure points.
- Future-state blueprint with diffs called out.
- Failure mode register with severity, frequency, recovery play, and owner.
- Frontstage/backstage role and SLA matrix.
- CX/EX alignment audit per frontstage role.
- Co-creation workshop output: stress-test findings, agreed changes.
- Implementation backlog with paired customer-signal and staff-signal items.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | Service blueprint | Diagram or markdown table with frontstage, backstage, systems, evidence, and handoffs | `docs/service/service-blueprint.md` |
| Operability | Failure and recovery register | Markdown table with severity, frequency, owner, detection, and recovery play | `docs/service/failure-register.md` |
| UX quality | CX/EX alignment note | Markdown summary of staff enablement needed for the promised experience | `docs/service/cx-ex-alignment.md` |

## References

- `references/blueprint-construction-and-swimlanes.md` — swimlane structure, lines, evidence, granularity rules.
- `references/frontstage-backstage-alignment.md` — handoff design, SLAs, channel coordination.
- `references/service-failure-and-recovery.md` — failure taxonomy, severity scoring, recovery patterns.
- `references/cx-ex-alignment.md` — auditing employee experience as a CX enabler; tooling, authority, incentive checks.
- `references/blueprint-anti-patterns.md` — failure modes and corrections.
<!-- dual-compat-end -->

## Decision Gates

| Gate | Question | If Yes | If No |
|------|----------|--------|-------|
| G1 Scope | One actor, one scenario, one outcome? | Build journey row | Re-scope |
| G2 Evidence | Every customer action has evidence? | Tag failures | Add evidence |
| G3 Failures | Each high-severity failure has owner + recovery? | Align ops | Design recovery |
| G4 EX | Frontstage has tools, authority, info to deliver promise? | Stress-test | Fix EX gap |
| G5 Co-create | Real case walked end-to-end with all roles? | Plan implementation | Re-walk |
| G6 Implementation | Each change has customer + staff + system + metric? | Ship | Re-pair |

## Co-Creation Workshop — Minimum Set-up

- 4–8 hours, single room (physical or virtual whiteboard).
- Roles present: customer (or proxy with verbatim), frontstage staff (one per channel in scope), backstage operations (one per workflow), support (IT, finance, supply), facilitator, scribe.
- Pre-work: current-state journey map, recent complaint themes, volume baselines.
- Output gate: workshop closes only when one real recent case has been walked end-to-end on the wall and every disagreement marked.

## Companion Skills

- `experience-mapping` to validate the actor and impact before blueprinting; supplies the journey row.
- `product-discovery` when the service contains an unproven offering and value risk is open.
