# First 5 / First 30 / First 120 Minutes — Universal AI Incident Playbook

Read top to bottom. Every minute is named. Every action has an owner.

## 0–5 Minutes — Acknowledge and Stabilize the Channel

| Time | Owner | Action |
|---|---|---|
| T+0 | On-call (responder) | Acknowledge the page. Read the alert payload — note `signal_id`, `failure_class_hint`, `runbook` link, `evidence_required` list, `default_severity`. |
| T+1 | Responder | Open incident channel (`#inc-<short-id>`). Post the alert payload. |
| T+2 | Responder | Capture the **four facts** in the channel: <br>1. Deploy log last 24h (code, prompts, model pin, retrieval index version, eval gates). <br>2. Foundation-model provider status pages (Anthropic / OpenAI / Bedrock / vendor). <br>3. Infra changes (region failover, routing change). <br>4. Alert payload again, pinned. |
| T+3 | Responder | Assign roles: **incident commander (IC)**, **ops-lead**, **comms-lead**, **scribe**. IC may be responder for sev-3/sev-4; for sev-1 a dedicated IC is paged. |
| T+4 | Ops-lead | Pull the trace bundle for a representative failing request. Command: <br>`ai-evidence-export --signal <signal_id> --window 30m --output /incidents/<inc-id>/` |
| T+5 | IC | Declare severity per `severity-matrix.md`. Severity is set, not negotiated. |

If the on-call cannot complete 0–5 in 5 minutes, escalate. Do not skip steps.

## 5–30 Minutes — Classify and Mitigate

| Time | Owner | Action |
|---|---|---|
| T+5 | Ops-lead | Run the triage decision tree (`ai-incident-detection-and-triage/references/triage-decision-tree.md`). End with a failure-class label or `unknown`. |
| T+10 | Ops-lead | Open the per-class playbook (`per-failure-class-playbooks.md`). Read the **first mitigation** for the class. |
| T+12 | Ops-lead | Execute first mitigation via the operator surface. Log to `ai_incident_mitigation_log` with reason = "<class>: first mitigation per playbook". |
| T+15 | Comms-lead | Post first status-page entry (template from `ai-incident-customer-comms/references/status-page-templates.md`). Sev-1 mandatory; sev-2 if customer-visible. |
| T+18 | Ops-lead | Run the containment verification check for the executed mitigation. |
| T+20 | IC | If containment verifies, hold. If it does not, ops-lead executes second mitigation. |
| T+25 | Comms-lead | Sev-1: send DM/email to named affected tenants on the HIGH_RISK_TENANTS list. |
| T+30 | IC | Status check: containment verified? Severity correct? Anything escalating? Update incident channel. |

If at T+30 the failure class is still `unknown` for a sev-1, freeze the affected feature (kill-switch or full rollback) and continue investigation under abstain or off state.

## 30–120 Minutes — Root Cause Hypothesis and Recovery Prep

| Time | Owner | Action |
|---|---|---|
| T+30 | Ops-lead | Form root-cause hypothesis using `ai-rca-taxonomy/references/taxonomy-and-patterns.md`. Note the candidate class and the evidence supporting it. |
| T+40 | Ops-lead | Capture full evidence bundle (`ai-incident-evidence-capture/references/evidence-bundle-spec.md`). Bundle includes: trace bundle, prompt/model/tool versions, retrieval set sample, eval-at-incident, customer-affected list, action audit log, reproduce script, price table snapshot. |
| T+50 | IC | Check **regulator notification windows**. Confirmed jailbreak with data exfil, or any safety event affecting an EU AI Act high-risk system: clock starts here. See `ai-incident-customer-comms/references/regulator-notification-templates.md`. |
| T+60 | Comms-lead | Status-page update. Tone: facts, current mitigation, next update time. |
| T+75 | Ops-lead | Verify mitigation still holding (containment check repeat). |
| T+90 | Ops-lead | Begin **recovery plan** drafting (hand off to `ai-incident-recovery-and-rollback`). |
| T+105 | Comms-lead | Sev-1: 90-minute checkpoint comms to affected tenants. |
| T+120 | IC | Decision: continue incident or move to recovery phase? Document either way. |

## Beyond T+120

The incident is in **steady mitigation state**. The remaining work is:

- Drive root cause to a verified explanation (not just a plausible one).
- Build the recovery plan (eval-gated re-promotion path).
- Run the comms cadence (status page every hour for sev-1).
- Capture the full evidence pack with chain-of-custody for the postmortem.
- Schedule the postmortem (within 5 business days for sev-1 and sev-2).

The incident **closes** when:
1. Mitigation is verified holding for a configured window (sev-1: 4h stable; sev-2: 2h stable).
2. Recovery plan is documented (even if execution will take weeks).
3. Postmortem owner is assigned.
4. Final status-page entry is posted.

## Role Definitions

**Incident Commander (IC)** — single-threaded owner of the incident. Decides severity, decides mitigation moves on tie-breaks, owns the channel. Does not execute themselves on sev-1.

**Ops-Lead** — executes mitigations, runs triage tree, captures evidence. Hands keyboard to others as needed.

**Comms-Lead** — owns status page, customer notifications, regulator notifications. Reads from templates; coordinates with legal for sev-1 with data implications.

**Scribe** — captures the timeline. Every action with timestamp + actor + result. Output becomes the postmortem timeline section.

## Anti-Patterns

- Roles not assigned; everyone helps; nobody owns. Decisions stall.
- IC also executes — IC must lead, not pilot.
- Status-page entry written from scratch each time — slow, inconsistent, sometimes wrong. Use templates.
- Evidence captured only after the incident — state has changed, evidence is now lost.
- No T+30 status check — incident drifts.
