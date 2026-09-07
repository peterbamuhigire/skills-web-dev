---
name: customer-service-excellence
description: Use when handling service recovery, escalations, complaints, apology language, frontline empowerment, CX measurement, or prevention loops.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Customer Service Excellence
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.


## Required Inputs

| Input | Required | Use |
|---|---|---|
| Decision, audience, and deliverable | yes | Bound the business outcome |
| Source evidence, constraints, and owner | yes | Ground recommendations and accountability |
| Approved budget, customer data, or production artefacts | conditional | Support high-impact execution |

## Capability and permission contract

Default to read-only analysis and drafting. Do not publish, send, price, promise, alter customer records, commit budget, or modify production artefacts without explicit authority and a named approver. Minimise confidential data, preserve provenance, and keep reversible copies.

## Degraded mode

If evidence, stakeholder decisions, specialist tooling, or authoritative commercial data are unavailable, deliver a labelled draft, checklist, or decision memo. State what was not verified and do not claim approval, publication, financial accuracy, or customer acceptance.

## Decision rules

| Condition | Action | Stop condition |
|---|---|---|
| Output creates a commercial, customer, or delivery commitment | Obtain named approval before release | Authority or terms are unclear |
| Evidence supports a reversible draft | Produce it with assumptions and owner | Required evidence conflicts |
| Tooling or data is incomplete | Specify validation | A final executable artefact is expected |

## Domain Anti-Patterns

- Inventing customer evidence, prices, benchmarks, or approvals. Fix: cite the source or mark the gap.
- Publishing or sending a draft without authority. Fix: retain draft status and name the approver.
- Hiding assumptions inside polished prose. Fix: expose them beside each affected decision.
- Polishing presentation while the decision remains unclear. Fix: resolve audience, owner, and acceptance criteria.
- Treating unavailable tooling as passed validation. Fix: record the unassessed check.


<!-- dual-compat-start -->
## Use When

- Handling a live service issue (complaint, error, delay, escalation, public-channel post).
- Drafting service language: apology, empathy, ownership, timeline, confirmation, escalation, refusal.
- Designing or auditing the service recovery and retention loop.
- Measuring service quality across response, resolution, recovery, retention.
- Aligning frontline empowerment with escalation paths and knowledge management (CX-EX alignment).
- Building a prevention loop so the same failure does not recur.

## Do Not Use When

- The work is pre-sale conversation; use `premium-client-sales`.
- The work is product feature evaluation; use `product-discovery`.
- The work is internal team conflict unrelated to a customer; use a coaching framework.
- The work is marketing copy at the top of the funnel; use the marketing/positioning skill.

## Required Inputs

- The customer's words (verbatim where possible) and the channel they used.
- Account context: tenure, value, prior issues, contract terms.
- The actual failure: what happened, what was promised, what gap.
- Authority limits of the agent handling the interaction (refund cap, credit cap, escalation triggers).

## Workflow

1. Run the **recovery-and-retention loop**: listen, acknowledge, diagnose, explain, options, act, confirm, document, prevent, follow up. Do not skip steps; the order matters.
2. Match the interaction type to a **difficult-interaction framework** (angry, anxious, technical-novice, executive, public-channel) and adapt language accordingly.
3. Use **service language patterns** for apology, empathy, ownership, timeline, confirmation, escalation. Each pattern has a structure and a prohibited phrase list.
4. Honour the **frontline empowerment ceiling**: if the resolution exceeds the agent's authority, escalate immediately rather than negotiating beyond authority.
5. Close with **explicit confirmation**: name what was done, what comes next, and the date the customer can hold you to.
6. Document the interaction with structured tags so it feeds the **service quality measurement** dashboard and the **prevention loop**.
7. Run a follow-up after resolution. Without follow-up, recovery is half-done.

## Quality Standards

- The customer's words are mirrored before any explanation begins.
- Apology is specific and ownership-bearing, not "we apologize for any inconvenience".
- Every commitment has a date, an owner, and a confirmation channel.
- Escalation is a service tool, not a defeat. Escalate before negotiating beyond authority.
- Public-channel responses move to private channel for resolution but acknowledge publicly first.
- Every documented failure produces either a knowledge-base entry, a process change, or a known-acceptable-loss decision.

## Anti-Patterns

- Apologising in passive voice ("mistakes were made"). Specific ownership outperforms generic regret.
- Explaining policy before acknowledging impact.
- Promising a callback "soon" instead of a specific time window.
- Treating the angry customer's tone as the issue. The tone is data; the issue is the failure.
- Closing the ticket because the customer went silent. Silence is not resolution.
- Making the customer repeat the story to a second agent. Hand-off discipline is part of service.
- Using empathy phrases as filler. Empathy without diagnosis is theatre.

## Outputs

- A resolved or escalated case with named owner and date.
- A written confirmation to the customer (channel of their choice).
- A structured tag set for measurement (response time, resolution path, recovery used, retention outcome).
- A prevention entry: knowledge-base update, process change, or accepted-loss note.
- A follow-up scheduled at an explicit date.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Operability | Service recovery plan | Markdown with acknowledgement, owner, update cadence, escalation, and closure condition | `docs/service/recovery-plan.md` |
| Release evidence | Support language script set | Markdown library for acknowledgement, referral, escalation, follow-up, and recovery | `docs/service/support-scripts.md` |
| UX quality | Service quality dashboard definition | Markdown or CSV with response, resolution, recurrence, and satisfaction metrics | `docs/service/service-quality-dashboard.md` |

## References

- `references/recovery-and-retention-loop.md` for the ten-step loop and exit criteria per step.
- `references/service-language-patterns.md` for apology, empathy, ownership, timeline, confirmation, escalation, refusal patterns with prohibited phrases.
- `references/difficult-interaction-frameworks.md` for angry, anxious, technical-novice, executive, public-channel handling.
- `references/service-quality-measurement.md` for the four-metric dashboard (response, resolution, recovery success, retention impact).
- `references/cx-ex-alignment.md` for frontline empowerment, escalation paths, and knowledge management.
- Use `continuous-improvement-system` to feed prevention entries into operating cadence reviews.
- Use `premium-client-sales` for the inverse direction (pre-sale conversations).
<!-- dual-compat-end -->

## Recovery and Retention Loop (the order, every time)

Listen -> Acknowledge -> Diagnose -> Explain -> Options -> Act -> Confirm -> Document -> Prevent -> Follow up.

Skipping listen produces explanation theatre. Skipping diagnose produces apology theatre. Skipping prevent produces the same failure next month. Skipping follow up produces silent churn.

## Authority Ceiling Rule

Frontline agents must have a published refund cap, credit cap, and escalation trigger. Negotiating beyond authority destroys two relationships at once: the customer's trust (they sense the discomfort) and the agent's relationship with their manager (escalating after a promise burns capital both ways).

## The Public-Channel Move

Public complaint -> public acknowledgement (under one hour, no defence, no detail) -> private channel handover -> resolution in private -> public closing note (only if the customer agrees). Resolving in public is theatre and invites pile-on.

## Service Failure Prevention Loop

Every documented failure produces one of three outcomes:

- A knowledge-base entry (the agent could have answered with the right information).
- A process change (the system allowed the failure; fix it or it recurs).
- An accepted-loss note (the failure cost is below the prevention cost; document and move on).

Without the third option, prevention loops accumulate well-meaning policy that no one follows.
