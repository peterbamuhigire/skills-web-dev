# Regulator Notification Templates and Clocks

Note: These templates are operational starting points. They must be reviewed by legal counsel in each jurisdiction before submission. Clocks below summarise published rules current to early 2026 and are not a substitute for legal advice.

## Clocks Summary

| Regulator | Trigger | Clock from detection | Owner | Template |
|---|---|---|---|---|
| EU AI Act competent authority (Art. 73) — serious incident | Incident on a high-risk AI system causing serious harm, infringement, or widespread harm | within 15 days of awareness; **within 2 days** if widespread infringement; **within 10 days** if death or serious damage to critical infrastructure | Legal + AI ops + DPO | §1 |
| GDPR DPA (Art. 33, 34) | Personal data breach | within 72 hours; affected subjects "without undue delay" if high risk | Legal + DPO | §2 |
| UK ICO (UK GDPR Art. 33, 34) | Personal data breach | within 72 hours | Legal + DPO | similar to §2 |
| Sector-specific — banking (e.g., DORA in EU) | Major ICT-related incident | initial notification within 4 hours of classification; intermediate report 72h; final 1 month | Legal + AI ops | §3 |
| Sector-specific — healthcare (HIPAA-equivalent depending on jurisdiction) | Breach of PHI | varies; HHS within 60 days for >500 affected | Legal + DPO | §3 |
| Customer contractual notifications | Per signed contracts | Per contract (often 24–72 hours) | Legal + CSM | n/a |

**The clock starts at detection** — when the on-call has reasonable belief of a reportable incident. Detection is timestamped in the incident channel; this timestamp is the legal starting point.

## §1 EU AI Act Art. 73 — Serious Incident Notification

Use when: a serious incident occurs on an AI system classified as high-risk under the EU AI Act. "Serious incident" includes: death or serious damage; serious and irreversible disruption of critical infrastructure; infringement of fundamental rights (Charter); serious harm to property or environment.

Template:

```
To:      <competent national authority>
From:    <provider / deployer name + AI Act registered representative>
Subject: Serious Incident Notification — Art. 73 EU AI Act
Date:    <date>

1. Identification of the AI system
   System name:          <system name>
   System ID (EU DB):    <if registered>
   High-risk category:   <Annex III category>
   Provider:             <legal entity, address>
   Deployer (if different): <legal entity, address>

2. Detection and notification
   Date and time of detection (UTC): <ISO 8601>
   Date and time of notification (UTC): <ISO 8601>
   Reason for any delay beyond 15 / 10 / 2 day window: <if applicable>

3. Description of the serious incident
   Nature:               <serious incident type per Art. 3(49)>
   Location:             <jurisdiction(s)>
   Affected persons / entities (estimate): <count + categories>
   Description of harm:  <facts; no speculation>

4. Description of the AI system behaviour at issue
   Intended purpose:     <as documented>
   Behaviour observed:   <facts>
   Logs / evidence:      <reference to evidence bundle id, retention policy>

5. Containment and mitigation measures
   Immediate measures:   <list>
   Status of operation:  <suspended / restricted / running with mitigation>

6. Preliminary root cause
   <Best current understanding; mark as preliminary>

7. Proposed corrective actions
   Short term:           <list>
   Medium term:          <list>
   Re-promotion criteria: <eval gates that must pass>

8. Contact
   Notifying officer:    <name, role, email, phone>
   Legal representative: <name, role, contact>

Annexes:
A. Evidence bundle manifest (signed).
B. Mitigation log extract.
C. Affected-persons estimate methodology.
```

## §2 GDPR Art. 33 — Data Breach Notification

Use when: personal data has been or is likely to have been accessed, disclosed, lost, or altered in an unintended way.

Template:

```
To:      <competent supervisory authority (DPA)>
From:    <controller>
Subject: Personal Data Breach Notification — Art. 33 GDPR
Date:    <date>

1. Nature of the breach
   Type:                 <confidentiality / integrity / availability>
   Categories of data:   <list — including any special-category data>
   Categories of subjects: <list>
   Estimated number of subjects: <count>
   Estimated number of records: <count>

2. Likely consequences
   <Risk to rights and freedoms of data subjects>

3. Measures taken
   Immediate technical and organisational measures: <list>
   Mitigation of adverse effects: <list>

4. Contact
   Data Protection Officer: <name, contact>

5. Cross-border processing
   Lead supervisory authority: <DPA>
   One-stop-shop mechanism applies: <yes/no>
```

Article 34 notification to data subjects is required when the breach is likely to result in high risk to rights and freedoms; coordinate with §per-tenant-notification-templates.md (data implication template).

## §3 Sector-Specific Notification (Skeleton)

Sector regulators (DORA for EU finance, HIPAA-equivalent for health, etc.) have their own forms. Maintain a one-pager per sector regulator with:

- Trigger condition.
- Clock from detection.
- Submission form / portal.
- Required fields (system id, incident class, harm description, mitigation, recovery, root cause, evidence reference).
- Internal owner.

A central legal-ops table maps `(jurisdiction, sector, incident_class) → regulator + clock + form + owner` so the comms-lead does not have to search at T+30 of a sev-1.

## Detection Timestamp — Critical

The single most important field in any regulator submission is the **detection timestamp**. It anchors every clock. Practices:

- The incident channel records the detection timestamp at T+0 of the page.
- The mitigation log first entry is the detection event.
- The evidence bundle manifest records detection time as the window-start of significance.
- Any later regulator submission references this single timestamp; do not redefine it after the fact.

## Anti-Patterns

- Lawyer first reads the templates at T+30 of a sev-1.
- Clock starts at "when we decided to tell them" — already late, sometimes by hours.
- Multiple jurisdictions need notification; only the largest is filed.
- Templates kept in a private wiki the on-call doesn't have access to.
- Filing the regulator submission before the customer notification, when the regulator's rules require subject notification.
- Speculative cause stated as fact in the regulator submission — fixing it later weakens credibility.
