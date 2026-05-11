---
name: ai-incident-drill-and-game-day
description: Use when designing and running AI-incident drills and game days — rehearsed scenarios (token-cost runaway, foundation-model deprecation, prompt-injection-via-tool, retrieval-poison, hallucination spike, agent-action incident, provider outage, regulator-notification dry-run), drill cadence, scoring criteria, and the learnings flywheel that turns drill output into engineering investment.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Incident Drill and Game Day
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Designing the AI-incident drill program for a multi-tenant SaaS.
- Running a quarterly or monthly game day.
- Onboarding a new on-call engineer or rotation.
- Validating that a runbook update / new operator surface actually works.

## Do Not Use When

- The task is the live incident — `ai-incident-response-runbook`.
- The task is generic chaos engineering — `reliability-engineering`.
- The task is the eval / red-team — `ai-eval-harness`, `ai-prompt-injection-and-tenant-safety`.

## Required Inputs

- Functional detection signals (`ai-incident-detection-and-triage`).
- Functional mitigation primitives (`ai-incident-response-runbook`).
- Functional evidence bundle exporter (`ai-incident-evidence-capture`).
- A staging or shadow environment that can take the simulated load.
- On-call rotation that can spare 90 minutes for a scheduled drill.

## Workflow

1. Read this `SKILL.md`.
2. Pick the **drill scenario** (§1) from the catalogue.
3. Prepare the **drill plan** (§2) — objective, scope, scoring rubric, observers.
4. Inject the **failure** (§3) — synthetic signal or staged regression.
5. Run the **drill** (§4) — responders follow live runbook; observers score; do not coach.
6. Run the **debrief** (§5) — score, lessons, action items.
7. Flow into the **learnings flywheel** (§6) — drill findings become eng investment.
8. Set the **cadence** (§7).
9. Apply anti-patterns (§8).

## Quality Standards

- A drill runs at least monthly; sev-1 scenario at least quarterly.
- Every drill produces a scored result and at least one action item.
- Drill findings close within one quarter or are escalated to AI leadership.
- The on-call engineer drilled within the last quarter is the primary responder; not always the same engineer.
- Drill plans rotate the failure class so the team is not pattern-matched to one type.
- Drills include the comms-lead and (occasionally) legal / regulator-notification dry-run.

## Anti-Patterns

- "Drill" is reading the runbook in a meeting — not a drill, a review.
- Same scenario every quarter — pattern-matched response, no growth.
- Coaches whispering during the drill — drills test current state, not state-with-help.
- Observers grade leniently to spare feelings — drill findings stop being actionable.
- Action items from drills don't make it into engineering planning — flywheel doesn't turn.
- Drills never include comms / legal — operational muscle is half the response.
- Drill in production without a kill-switch on the drill itself — could become a real incident.

## Outputs

- Drill plan template.
- Scoring rubric.
- Drill scenario catalogue.
- Drill cadence calendar.
- Drill findings register feeding into postmortem-actions tracking.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Operability | Drill plan | Markdown | `drills/2026-05-cost-runaway-plan.md` |
| Operability | Drill scoresheet | Markdown | `drills/2026-05-cost-runaway-score.md` |
| Operability | Drill findings | DB rows | `ai_drill_findings` |
| Operability | Cadence calendar | YAML | `ops/ai/drill-cadence.yaml` |

## References

- `references/game-day-exercises.md` — full scenario catalogue with setup, injection, expected response, scoring.
- `references/drill-cadence.md` — cadence, rotation, success criteria, escalation.
- Companion: `ai-incident-detection-and-triage`, `ai-incident-response-runbook`, `ai-incident-evidence-capture`, `ai-incident-customer-comms`, `ai-incident-postmortem`, `ai-feature-rollout-and-experimentation`.

<!-- dual-compat-end -->

## §1 Drill Scenario Catalogue (Summary)

Full details in `references/game-day-exercises.md`. Scenarios:

1. **Token-cost runaway** — a prompt change inflates tokens-per-request 4×; cost-anomaly fires.
2. **Foundation-model deprecation** — provider announces 30-day deprecation of pinned model; migration drill.
3. **Prompt-injection via tool output** — staged hostile content in a tool's response; observe whether agent obeys.
4. **Retrieval poison** — staged hostile content in the index; observe whether retrieval delivers it and whether output filter catches it.
5. **Hallucination spike** — staged prompt regression causes a faithfulness drop on a subset; triage to mitigation.
6. **Agent-action incident** — staged agent action outside approved scope; observe approval-bypass detection and kill-switch.
7. **Provider outage** — staged provider 5xx burst; observe fallback chain activation.
8. **Tool-vendor schema change** — staged tool response with a missing required field; observe schema-mismatch detection.
9. **Regulator-notification dry-run** — paper drill: confirmed data-exfil scenario; observe whether the 72h GDPR / 15-day EU AI Act clocks are tracked, templates pulled, legal looped in.
10. **Eval drift** — staged judge-vs-human kappa drop; observe whether release gates trigger.

## §2 Drill Plan Template

```markdown
# Drill plan: <scenario name> — <date>

## Objective
What is being tested (specific runbook section, specific primitive, specific signal)?

## Scope
- Environment: staging / shadow-only / synthetic injection.
- Affected features: <list>.
- Affected tenants: <synthetic only>.

## Responders
- Incident commander (primary on-call): <name>.
- Ops-lead: <name>.
- Comms-lead: <name>.
- Scribe: <name>.

## Observers (do not coach)
- AI lead: <name>.
- Engineering manager: <name>.
- Optionally: legal (for regulator drills), CSM (for tenant-comms drills).

## Scoring Rubric
- Time-to-ack target: <value>.
- Time-to-classify target: <value>.
- Time-to-first-mitigation target: <value>.
- Containment-verified within <value>.
- Status-page entry within <value> (if applicable).
- Customer DM within <value> (if applicable).
- Regulator clock noted within <value> (if applicable).
- Evidence bundle exported within <value>.
- Postmortem opened by next business day.

## Drill Kill-Switch
If the drill threatens to become a real incident: <named operator>, <named primitive>, <named verification>.

## Drill Schedule
- T-1 day: brief observers; **do not brief responders**.
- T-0: inject.
- T+90 min: stop drill; begin debrief.

## Debrief Agenda
- Walk the timeline.
- Score against rubric.
- Lessons.
- Action items.
```

## §3 Failure Injection

Each scenario has a defined injection method in `references/game-day-exercises.md`. Common patterns:

- **Synthetic signal injection** — write a fake row to the metrics store that pages the on-call. No system change.
- **Shadow regression** — ship a degraded prompt or model to a shadow run; surface its metrics into the real alert path.
- **Staged data** — insert synthetic hostile content into a staging index.
- **Paper drill** — read a scenario aloud; responders work in shared doc; no system change.

Always: a **drill marker** is set on the alert so responders see "[DRILL] hallucination_burn…" — eliminates "is this real?" confusion. The marker can be stripped at the observer's discretion for harder drills, but only with prior leadership decision.

## §4 Running the Drill

- Start the clock at injection.
- Scribe records every action with timestamp + actor.
- Observers do not coach. They take notes.
- The drill kill-switch is held by a single observer who is **not** an active responder.
- The drill ends at T+90 minutes or when the responders declare "contained + recovery plan drafted".

## §5 Debrief

Within 24 hours, run a 60-minute debrief:

- Score against the rubric — quantitatively.
- Walk what went well and what didn't.
- Action items: at least one technical + at least one process.
- Note any rubric criterion that wasn't tested — schedule a future drill.

Findings go to `ai_drill_findings` with owner + due date.

## §6 Learnings Flywheel

- Drill findings join the postmortem action items in the same tracker.
- Monthly aggregate: drill scores trend, action-item closure rate, recurring weak spots.
- Each weak spot drives an engineering investment line item.
- Engineering investment unblocks the next drill to test a deeper layer.

## §7 Cadence

See `references/drill-cadence.md`. Summary:

| Scenario class | Cadence | Rotation |
|---|---|---|
| Drill (any class) | monthly | round-robin through scenarios |
| Sev-1 scenario | quarterly | high-impact rotation |
| Tabletop / paper drill | bi-monthly | per failure-class on a rolling list |
| Onboarding drill | once per new on-call | within first 30 days |

## §8 Anti-Patterns

- Drill becomes a meeting (review of the runbook).
- Same scenario every quarter; team pattern-matches.
- Drill kill-switch missing or unknown; observers hesitate to invoke when needed.
- Drill scored only by "responders did fine" — no rubric, no numbers, no learning.
- Drill findings never enter engineering planning — flywheel doesn't turn.
- Drills run only on weekdays at 10am; never test the 02:14 condition.
- Drill briefs responders — testing prepared response, not real response.
