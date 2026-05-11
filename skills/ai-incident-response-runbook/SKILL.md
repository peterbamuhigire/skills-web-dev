---
name: ai-incident-response-runbook
description: Use when responding to a paged AI incident — the universal first 5 / 30 / 120-minute playbook, and the per-failure-class playbooks (hallucination spike, prompt drift, model regression, jailbreak, cost runaway, agent-action incident, retrieval drift, training-data shift, provider outage, tool-vendor change). Names the exact mitigation moves (kill-switch, model-fallback, prompt-rollback, index-pin, abstain-mode, read-only-mode) and who flips which switch.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Incident Response Runbook
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- An AI signal has paged the on-call and the triage tree has produced a failure class.
- You are designing the operator-side surfaces (kill-switch, model-pin, prompt-pin, abstain-mode toggle) that the runbook depends on.
- Auditing whether the engine can actually execute the moves the runbook calls for in < 60 seconds.

## Do Not Use When

- The task is the detection / triage — `ai-incident-detection-and-triage`.
- The task is the postmortem — `ai-incident-postmortem`.
- The task is the recovery / re-promotion — `ai-incident-recovery-and-rollback`.
- The task is generic platform incident response — `reliability-engineering`.

## Required Inputs

- Triaged failure class label (from `ai-incident-detection-and-triage`).
- Functional kill-switch + model-pin + prompt-pin + gateway routing pin (from `ai-model-gateway`).
- Functional abstain-mode / read-only-mode per feature.
- Evidence-capture pipeline ready (from `ai-incident-evidence-capture`).
- Customer-comms templates ready (from `ai-incident-customer-comms`).

## Workflow

1. Read this `SKILL.md`.
2. Follow the **first 5 / 30 / 120-minute** universal playbook (§1).
3. Branch to the **per-failure-class playbook** (§2) using the failure-class label.
4. Decide and execute the **mitigation primitive** (§3).
5. Run **containment verification** (§4) — confirm the mitigation worked, not just that the switch was flipped.
6. Hand off to **recovery** (`ai-incident-recovery-and-rollback`) once stable.
7. Hand off to **postmortem** (`ai-incident-postmortem`) once recovered.
8. Apply anti-patterns (§5).

## Quality Standards

- Every mitigation primitive (kill-switch, model-pin, prompt-pin, index-pin, abstain-mode, read-only-mode, full feature rollback) is executable from a single operator surface in < 60 seconds.
- The on-call engineer never needs to write or edit code to execute a mitigation.
- Every mitigation logs a structured event with actor, timestamp, primitive, scope, reason.
- Containment is verified by signal (signal recovered) not assumed by switch flip.
- Time-to-mitigate target: sev-1 ≤ 1h, sev-2 ≤ 4h.
- Every playbook ends with a handoff into recovery + postmortem.

## Anti-Patterns

- Mitigation requires a PR, code review, and deploy. Not a runbook — a rebuild.
- Kill-switch flips silently, comms team finds out hours later from a customer ticket.
- Operator surface has no `dry_run` — every action is destructive on first click.
- Per-failure-class playbooks copy the same generic text — useless when on-call needs class-specific moves.
- "Mitigation = restart the service." Doesn't address any AI-specific class.
- No verification step. Switch was flipped, signal still firing, on-call walks away.
- Runbook says "consult the AI team" — no specific human, no contact path, no escalation tree.

## Outputs

- Universal first-N-minute playbook (deliverable: `docs/runbooks/ai-incident-first-n.md`).
- Per-failure-class playbooks.
- Mitigation primitive specs with operator surfaces.
- Containment verification checklist.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Operability | First-N-minute runbook | Markdown | `docs/runbooks/ai-incident-first-n.md` |
| Operability | Per-class playbooks | Markdown | `docs/runbooks/ai-classes/<class>.md` |
| Operability | Mitigation primitive log | DB rows | `ai_incident_mitigation_log` |
| Operability | Containment checks | YAML | `ops/ai/containment-checks.yaml` |

## References

- `references/first-five-first-thirty-first-two.md` — universal playbook with timestamps and roles.
- `references/per-failure-class-playbooks.md` — 10 class-specific playbooks.
- Companion: `ai-incident-detection-and-triage`, `ai-incident-evidence-capture`, `ai-incident-customer-comms`, `ai-incident-recovery-and-rollback`, `ai-incident-postmortem`, `ai-model-gateway`, `ai-feature-rollout-and-experimentation`, `saas-admin-backoffice-tooling`, `ai-rca-taxonomy`.

<!-- dual-compat-end -->

## §1 Universal Playbook

See `references/first-five-first-thirty-first-two.md` for the full timeline. Summary:

- **0–5 min** — acknowledge, open incident channel, capture the four facts (deploy log, provider status, index version, alert payload), assign roles (incident-commander, ops-lead, comms-lead, scribe). Pull the trace bundle.
- **5–30 min** — classify via triage tree, execute first mitigation, verify containment, post first status-page entry, notify regulated tenants if applicable.
- **30–120 min** — root-cause hypothesis, second-level mitigation if first didn't hold, prepare recovery plan, full evidence bundle captured, regulator notification window check.
- **2h+** — hand off to recovery; postmortem opened.

## §2 Per-Failure-Class Playbooks

Each class has its own playbook with: detection signal, first mitigation, second mitigation, comms posture, evidence to capture, recovery handoff. See `references/per-failure-class-playbooks.md` for full text. Classes:

1. **hallucination-spike** — first move: `abstain-mode` on the affected feature (raise abstain threshold so the system refuses rather than fabricates); second move: prompt-rollback or model-pin to last-known-good.
2. **prompt-drift** — first move: prompt-rollback to last-known-good prompt version via gateway prompt-pin.
3. **model-regression** — first move: model-pin to last-known-good model version; second: route to fallback provider.
4. **jailbreak** — first move: tighten safety classifier threshold + add the jailbreak pattern to the deny-list; second: rotate any leaked credentials/data; third: regulator/customer notification if data exfil confirmed.
5. **cost-runaway** — first move: per-tenant quota cap (or per-feature) to halt bleed; second: identify cause (loop, prompt bloat, price change, fallback misfire) and apply targeted fix.
6. **agent-action incident** — first move: agent kill-switch (pause all in-flight tasks for the affected feature/tenant); second: undo reversible actions, document irreversible ones; third: customer + (if applicable) regulator notification.
7. **retrieval-drift** — first move: index-pin to the last-known-good index snapshot; second: pause ingest pipeline if data is corrupting; third: rebuild index from clean source.
8. **training-data-shift / data-evolution** — first move: abstain-mode on affected slices; second: ingest schema validation; third: rolling fix in pipeline.
9. **provider-incident** — first move: activate fallback chain (gateway routing pin to next provider); second: degrade gracefully (read-only-mode if dependent feature can't fall back).
10. **tool-vendor outage / schema change** — first move: tool-disable for affected feature (agent stops calling it); second: vendor liaison opens ticket; third: schema-mismatch detection-tightening.

## §3 Mitigation Primitives

These are the operator-facing surfaces every runbook depends on. They must exist *before* any incident occurs.

| Primitive | What it does | Where it lives | Propagation |
|---|---|---|---|
| **kill-switch** (feature) | Stops the feature entirely; returns a "feature unavailable" message. | `ai-model-gateway` + back-office | < 60s |
| **kill-switch** (agent task) | Pauses one in-flight agent task; cancels remaining steps. | `ai-agents-tools` runtime | immediate |
| **abstain-mode** | Raises abstain threshold; system answers fewer queries, refuses more. | per-feature config in gateway | < 60s |
| **read-only-mode** | Disables write actions for feature/agent; reads still served. | per-feature config | < 60s |
| **model-pin** | Forces a specific model version for a feature; ignores tier-based routing. | gateway | < 60s |
| **prompt-pin** | Forces a specific prompt version for a feature. | gateway | < 60s |
| **index-pin** | Forces a specific retrieval index snapshot. | retrieval service | < 60s |
| **tool-pin** | Forces a specific tool version / disables the tool. | agent runtime | < 60s |
| **gateway routing pin** | Forces a specific provider/region. | gateway | < 60s |
| **per-tenant feature pause** | Disables the feature only for the affected tenant(s). | gateway + entitlements | < 60s |
| **quota cap** | Per-tenant or per-feature hard cap on tokens/cost/requests. | gateway | < 60s |
| **full feature rollback** | Reverts the feature flag to previous variant for everyone. | feature-flag platform | < 60s |

Every primitive logs `(actor, timestamp, primitive, scope, reason, ticket_id)` to `ai_incident_mitigation_log`. Reason is mandatory — no anonymous flips.

## §4 Containment Verification

Containment is **proven by signal**, not by switch flip. For each mitigation:

| Mitigation | Verification check | Time |
|---|---|---|
| abstain-mode | abstain rate rises in 10 min to expected level; faithfulness recovers | 15 min |
| model-pin | model_version label in traces matches the pinned value | 5 min |
| prompt-pin | prompt_version label in traces matches the pinned value | 5 min |
| index-pin | index_version label in retrieval spans matches | 5 min |
| kill-switch (feature) | feature-call rate drops to ~0 | 2 min |
| kill-switch (agent task) | in-flight task count drops to 0 for scope | immediate |
| gateway routing pin | provider distribution shifts as expected | 5 min |
| quota cap | per-tenant cost rate plateaus | 15 min |

If containment doesn't verify within target, the mitigation failed. Move to second-level mitigation in the per-class playbook. Do **not** flip a second switch and walk away.

## §5 Anti-Patterns

- Mitigation primitives exist in code but no operator UI — on-call writes SQL or runs ad-hoc scripts at 02:14.
- Containment is "I flipped the switch, signal looked better for a minute" — without a defined verification check.
- Per-class playbooks copy-pasted from a generic platform incident template.
- No handoff into recovery; incident closed when signal recovers, leaving the rollback as the new permanent state.
- Comms not part of the runbook — operator focuses on tech, customers find out from Twitter.
- Mitigation primitive log isn't structured — postmortem cannot reconstruct what was flipped when.
