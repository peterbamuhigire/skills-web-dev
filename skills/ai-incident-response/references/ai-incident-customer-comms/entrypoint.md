> Consolidated from skills/ai-incident-customer-comms/SKILL.md into ai-incident-response on 2026-05-13. Load this through skills/ai-incident-response/SKILL.md, not as an active skill entrypoint.

# AI Incident Customer Comms
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Drafting or sending status-page entries during an AI incident.
- Drafting per-tenant DMs/emails for high-risk and named tenants.
- Notifying regulators on confirmed safety events / data exfil / serious incidents.
- Auditing whether comms-readiness exists *before* the next AI incident.

## Do Not Use When

- The task is non-AI generic platform comms — use the platform incident-comms runbook.
- The task is marketing or product launch comms — different track.
- The task is the technical mitigation — `ai-incident-response-runbook`.

## Required Inputs

- Severity for the current incident (`ai-incident-detection-and-triage`).
- Failure-class label (`ai-rca-taxonomy`).
- List of affected tenants and the HIGH_RISK_TENANTS list.
- Per-jurisdiction regulator inventory (EU AI Act competent authorities, GDPR DPA, sector regulators).
- Status page tooling, customer-comms tooling.

## Workflow

1. Read this `SKILL.md`.
2. Identify the **comms posture** (§1) — status page only, status page + tenant DMs, status page + tenant DMs + regulator.
3. Pull the **right template** (§2) per failure class.
4. Apply the **language patterns** (§3).
5. Run the **escalation cadence** (§4) — every N minutes.
6. Trigger **regulator notification** (§5) when applicable; the clock has already started.
7. Run the **close-out comms** (§6) after recovery.
8. Apply anti-patterns (§7).

## Quality Standards

- First status-page entry posted within 15 minutes for sev-1, 1h for sev-2.
- Templates exist before the incident; no comms drafted from scratch under pressure.
- Tenant DMs are named (use tenant's account manager / CSM) and human-signed; not generic mass-email.
- Regulator notification clocks tracked from the moment of detection, not the moment of response.
- Language is factual; speculative cause is not stated as fact; product impact is named clearly; mitigation is named clearly.
- Close-out comms include a summary, customer-actionable detail, and the postmortem-availability date.

## Anti-Patterns

- First status-page entry says "we are investigating" with no product impact named. Useless.
- Naming the model provider when contractually you must not. Lawsuit risk.
- Speculating about cause publicly before the postmortem. Forces a retraction.
- Sending the same template to a regulated-bank tenant and a hobbyist Free-tier user.
- Missing the 72-hour GDPR breach window because nobody on the responder team owned regulator comms.
- Status-page entry contradicts the per-tenant DM — internal incoherence visible to enterprise customers.
- Close-out comms never sent; tenants don't know the incident is over.
- Letting the AI write the customer comms — tone-deaf to the very incident they're communicating about.

## Outputs

- Comms posture decision matrix.
- Status-page templates per class.
- Per-tenant DM templates per severity.
- Regulator notification templates with jurisdiction-specific clocks.
- Close-out comms template.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Compliance | Status page entries | Markdown + timestamps | `comms/inc-1923/statuspage.md` |
| Compliance | Tenant DMs sent | JSONL | `comms/inc-1923/tenant-dms.jsonl` |
| Compliance | Regulator notifications | PDF + manifest | `comms/inc-1923/regulator/` |
| Compliance | Close-out report | Markdown | `comms/inc-1923/close-out.md` |

## References

- `references/status-page-templates.md` — templates per failure class, language patterns.
- `references/per-tenant-notification-templates.md` — DM/email templates per severity.
- `references/regulator-notification-templates.md` — EU AI Act Art. 73 + GDPR + sector regulators with clocks.
- Companion: `ai-incident-detection-and-triage`, `ai-incident-response-runbook`, `ai-incident-postmortem`, `saas-transactional-email-infrastructure`, `saas-lifecycle-email-orchestration`.

<!-- dual-compat-end -->

## §1 Comms Posture

| Severity | Public status page | Per-tenant DM (high-risk) | Regulator |
|---|---|---|---|
| sev-1 | within 15 min | within 30 min | per regulator clock (see §5) |
| sev-2 | within 1h | within 2h for high-risk tenants | only if class triggers it |
| sev-3 | maintenance entry, summary in weekly digest | only if customer-facing | typically no |
| sev-4 | no | no | no |

Special: any confirmed jailbreak with data exfil is **always** sev-1 comms posture regardless of base severity.

## §2 Templates Per Failure Class

See `references/status-page-templates.md`. Each class has:
- A short title (≤ 8 words).
- A first-entry template (what happened, product impact, mitigation in progress, next update time).
- An update template (what changed, mitigation status).
- A close-out template (incident resolved, postmortem availability).

## §3 Language Patterns

- **Name the product impact** clearly. "Some answers may be incorrect" is better than "We are investigating an issue".
- **Avoid speculation** about root cause until the postmortem. "An underlying model has changed behaviour" not "OpenAI broke their model".
- **Avoid naming providers** unless contractually required.
- **No jargon**. "Hallucination rate exceeded our threshold" → "Some answers were not as accurate as we require".
- **Time-bound everything**. "Next update by HH:MM UTC".
- **Apologise when warranted**, briefly, once, in the close-out.
- **Don't promise** what hasn't happened. "We are working on…" not "We have fixed…".

## §4 Escalation Cadence

| Severity | Public update cadence | Tenant update cadence |
|---|---|---|
| sev-1 | every 30 min | every 60 min direct to high-risk tenants |
| sev-2 | every 60 min | every 2h to high-risk tenants |
| sev-3 | as needed | as needed |

Cadence holds until **recovery confirmed**, then close-out comms.

## §5 Regulator Notification

See `references/regulator-notification-templates.md` for full templates. Summary clocks:

| Regulator | Trigger | Clock | Owner |
|---|---|---|---|
| EU AI Act competent authority (Art. 73) | Serious incident on a high-risk AI system | within 15 days; within 2 days if widespread infringement; within 10 days if critical infrastructure | Legal + AI ops |
| GDPR DPA (Art. 33) | Personal data breach | 72 hours of awareness | Legal + DPO |
| Sector regulators (banking, health, energy) | per sector rules | varies | Legal |
| Contractual customer notifications | per contract | per contract | Legal + CSM |

The clock starts at **detection** (when the on-call has reasonable belief), not at "confirmation". Document the detection moment in the incident channel.

## §6 Close-Out Comms

Once recovery is confirmed and stable for the configured window:

1. Final status-page entry: "Incident resolved. Summary: <one-line product impact>. Postmortem available by <date>."
2. Per-tenant close-out DM to all affected tenants on the high-risk list. Includes: timeline, product impact for that tenant, actions taken, what the customer should do (if anything), postmortem availability.
3. Regulator follow-up if open: confirmation of remediation, postmortem extract.
4. Internal: postmortem assignment confirmed, due date confirmed.

## §7 Anti-Patterns

- Status-page entry written from scratch at T+12. Slow, inconsistent, often wrong.
- Tenant DM is the same email template sent en masse — Enterprise tenant gets a Free-tier voice.
- Regulator clock starts at "now we want to tell them" — already late.
- No close-out comms — customers think the incident is ongoing or come back days later asking.
- Comms team and engineering team have different facts in front of customers vs in the incident channel.


