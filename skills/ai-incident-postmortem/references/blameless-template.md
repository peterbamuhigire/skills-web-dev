# Blameless AI Postmortem Template

Use this template for any sev-1 or sev-2 AI incident. Replace bracketed prompts with content; keep section order; do not delete sections (mark as `n/a` if not applicable). Customer-facing variant in `customer-summary-template.md`.

---

```markdown
# Postmortem: <one-line title that names the AI failure class>

| Field | Value |
|---|---|
| Incident ID | inc-1923 |
| Severity (final) | sev-1 |
| Failure class | hallucination-spike (primary), prompt-drift (contributing) |
| Feature(s) | support-copilot |
| Detected at (UTC) | 2026-05-11T14:08:00Z |
| Mitigated at (UTC) | 2026-05-11T14:53:00Z |
| Resolved at (UTC) | 2026-05-11T17:14:00Z |
| Authors | <name>, <name> |
| Facilitator | <name> |
| Status | draft / in review / published |
| Customer-facing version | <link> |
| Regulator submission | <yes/no> + <link if yes> |

## Summary

Three sentences. What happened. What the impact was. What the primary root cause class is.

> Example: At 14:08 UTC on 11 May 2026 the support-copilot's answer faithfulness fell from 96% to 78% on the Pro and Enterprise tiers, affecting ~1,840 requests across 12 tenants. The drop followed a prompt change deployed at 13:45 UTC that altered the abstain-threshold behaviour. The primary root cause class is prompt-drift; a missing prompt-diff-eval gate in the release pipeline allowed the change to ship.

## Severity

Final: sev-1.

Severity history:
- T+5 declared sev-2 (broad-scope, suggestion-only).
- T+18 escalated to sev-1: HIGH_RISK_TENANTS rule applied (financial-services tenant on the affected list).

## Impact

| Dimension | Value |
|---|---|
| Affected requests | 1,843 |
| Affected tenants | 12 (3 Enterprise, 7 Pro, 2 Free) |
| High-risk tenants affected | 1 (regulated bank) |
| Duration (detection → recovery) | 3h 06m |
| Cost-runaway estimate | $0 (no cost dimension) |
| Customer-reported tickets | 4 |
| Regulator notification triggered | no |
| GDPR Art. 33 triggered | no |
| EU AI Act Art. 73 triggered | no |

## Timeline (UTC)

| Time | Event | Actor |
|---|---|---|
| 13:45 | Prompt v18 deployed via release pipeline | release bot |
| 14:08 | hallucination_burn_rate_2x fires; page issued | alerting |
| 14:09 | On-call ack | alice |
| 14:11 | Four facts captured in #inc-1923 | alice |
| 14:14 | Triage tree completed; class = hallucination-spike; subclass = prompt-drift suspected | alice |
| 14:18 | abstain-mode applied (threshold 0.85) | alice |
| 14:23 | Containment verifies — abstain rate at 14% (was 3%); faithfulness recovering | alice |
| 14:27 | Severity escalated sev-2 → sev-1 (HIGH_RISK_TENANTS rule) | bob (IC) |
| 14:30 | First status-page entry posted | comms |
| 14:35 | prompt-pin to v17 applied | alice |
| 14:53 | Containment verifies on v17; abstain-mode released | alice |
| 15:14 | First named-tenant DM to bank | csm |
| 17:14 | Stability window passed; incident moved to recovery | bob |

## Root Cause

Primary class: **prompt-drift** (AI RCA taxonomy §model.prompt-drift).

Mechanism: Prompt v18 attempted to reduce abstain frequency by relaxing the "if uncertain say I don't know" instruction, but the relaxation propagated to all uncertainty cases, including ones where the model previously correctly abstained from fabricating. The eval suite did not detect this because the goldens do not include questions where the source is genuinely missing (the abstain-vs-fabricate axis). The eval canary phase showed a small abstain-rate drop but did not page because no threshold existed for that signal.

Contributing classes:
- **eval.missing-test-coverage** — no golden for the abstain-vs-fabricate axis.
- **process.missed-release-gate** — abstain-rate-drop is not on the release gate.
- **monitoring.threshold-not-set** — abstain-rate-drop alert existed but threshold was not configured.

## Contributing Factor Map

| Category | Contribution |
|---|---|
| Model | non-contributing |
| Prompt | **primary** |
| Retrieval | non-contributing |
| Tool / Agent | n/a (no agent on this feature) |
| Eval | contributing — missing axis |
| Data | non-contributing |
| Infra | non-contributing |
| Commercial | non-contributing |
| Process | contributing — release gate gap |

## What Went Well

- Time to acknowledge: 1 minute (target: 5 minutes for sev-1).
- Triage tree produced a class within 5 minutes of ack.
- abstain-mode primitive worked in < 60s; containment verified at T+15.
- CSM-led tenant DM landed within 1h of sev-1 escalation.

## What Did Not Go Well

- Initial severity classification missed the HIGH_RISK_TENANTS rule. Severity remained sev-2 for ~12 minutes longer than it should have.
- Eval canary phase reported the abstain-rate drop in a daily digest, not as a release-blocking gate.
- prompt-pin operator UI required two attempts because of a stale cached registry view.
- Status page entry wording was edited three times in 20 minutes — template was found mid-incident, not before.

## Action Items

| # | Description | Category | Owner | Due | Verification |
|---|---|---|---|---|---|
| 1 | Add an "abstain-vs-fabricate" subset to support-copilot goldens with 50 cases | eval.add-golden | <name> | 2026-05-25 | Eval harness shows new subset green or appropriately failing |
| 2 | Add `abstain_rate_drop` as a release-gate signal (block deploy if drop > 5pp on canary) | release-gate.add | <name> | 2026-05-30 | A canary with this drop blocks promotion in CI |
| 3 | Auto-apply HIGH_RISK_TENANTS escalation rule in the alert router | tooling.alerting | <name> | 2026-06-05 | Test alert against a fixture HIGH_RISK_TENANT triggers sev escalation |
| 4 | Add severity-matrix lint to incident channel bot (reads alert payload, suggests severity) | tooling.incident | <name> | 2026-06-15 | Bot output observed during next sev-2 game day |
| 5 | Fix prompt-pin UI staleness | tooling.operator | <name> | 2026-05-20 | Manual test from clean browser session |
| 6 | Pre-stage status-page templates in the comms tooling so they autoload by failure class | tooling.comms | <name> | 2026-05-30 | Template visible to comms-lead within 30s of class assignment |

## Lessons

- An eval suite that doesn't include the **axis** that the prompt change moved gives a false-green on canary. Every prompt change must include a "what axis does this move" question in the PR template; if the eval suite doesn't cover that axis, the PR is gated.
- HIGH_RISK_TENANTS escalation must be automatic, not at the IC's judgement.
- Operator surfaces are part of the runbook; UI bugs slow incident response in measurable minutes.

## Appendix

- Evidence bundle: `s3://evidence-vault-prod/inc-1923/bundle.tar.gz` (sha256: …, signed: …, retention until 2033-05-11).
- Mitigation log: `mitigations/inc-1923.jsonl` (in bundle).
- Comms log: `comms/inc-1923/`.
- Public summary: `postmortems/public/inc-1923.md`.
```

---

## Customer-Facing Summary (Variant)

A shorter document. Required sections:

```markdown
# Incident summary — <feature> on <date>

## What happened

Two sentences in plain language.

## When

Detection → resolution UTC; impact window.

## Who was affected

Counts and tiers; no tenant names; no provider names.

## What we did

3–5 bullets of mitigations and recovery in plain language.

## What we are doing to prevent it

3–5 bullets of action items in plain language.

## Questions

Contact: <support@>
```

## Anti-Patterns in Template Use

- Sections deleted because "not applicable" — should be marked `n/a`, not removed.
- Timeline reconstructed from memory, not from the scribe's notes.
- Action items without owner or due date.
- Severity history not documented when severity changed mid-incident.
- "Root cause: human error" — always points to a missing process, gate, or tool.
- Customer summary copy-pasted from internal — leaks operational detail.
