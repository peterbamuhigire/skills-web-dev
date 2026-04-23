---
name: uganda-dppa-compliance
description: Generate Uganda DPPA 2019 compliance annex for software collecting personal
  data. Use for any Uganda-based SaaS to produce SRS compliance sections and flag
  DPIA triggers.
metadata:
  compatibility_notes: Uganda-based systems. Pairs with dpia-generator.
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Skill: Uganda DPPA 2019 Compliance Requirements
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Generate Uganda DPPA 2019 compliance annex for software collecting personal data. Use for any Uganda-based SaaS to produce SRS compliance sections and flag DPIA triggers.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `uganda-dppa-compliance` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Data safety | Uganda DPPA compliance annex | Markdown annex covering lawful basis, data subject rights, cross-border transfer, and breach notification per DPPA 2019 | `docs/compliance/uganda-dppa-annex.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Purpose

Generate a complete Uganda Data Protection and Privacy Act 2019 compliance annex for any Uganda-based software system. The output is a standalone SRS section (or standalone compliance document) covering all legally required system behaviours under the DPPA 2019 and the Data Protection and Privacy Regulations 2021.

Use this skill:
- As an annex to any SRS section that collects personal data in a Uganda-based system
- As input to `dpia-generator` when DPIA triggers are identified
- As a cross-cutting compliance check during Skill 08 (Semantic Auditing)

---

## Inputs Required

Before invoking this skill, read:
- `_context/vision.md` — system scope and user population
- `_context/features.md` — module list (to identify which modules collect personal data)
- `_context/personas.md` — user types who supply personal data
- `_context/glossary.md` — check that DPPA, PDPO, DPO, NIN, special personal data are defined
- `domains/uganda/references/dppa-pii-classification.md` — PII classification matrix

---

## Process

### Step 1 — PII Inventory

Read all context files. Identify every data field collected by the system. Classify each field as:
- **S** — Special personal data (financial information, health, medical, religious/political beliefs, sexual life)
- **P** — Personal data (identifiable: NIN, name, photo, GPS, contact)
- **N** — Non-personal (aggregates, product data, batch data)

Produce a PII inventory table: field name, source module, tier (S/P/N), justification, retention period.

**Uganda-specific alert:** Financial information is **Special personal data** under Section 9 DPPA 2019. This includes: mobile money numbers, salary amounts, bank account details, agent commission amounts, staff loan balances, payment histories. This is a key difference from the GDPR — flag it explicitly in the output.

### Step 2 — Lawful Basis Mapping

For each S and P field, identify the applicable lawful basis from Section 7 DPPA 2019:
- Consent (must be freely given, specific, informed, unambiguous)
- Authorised or required by law (cite the specific enactment)
- Proper performance of a public duty by a public body
- National security
- Prevention/detection/investigation/prosecution of an offence
- Performance of a contract
- Medical purposes
- Compliance with a legal obligation

### Step 3 — Consent Requirements

For every field where lawful basis = consent, generate FR requirements for:
- Consent capture at point of collection (before data is recorded)
- Consent record storage: data subject ID, purpose, data categories, timestamp, collector ID
- Withdrawal mechanism (as easy as giving consent — Section 7(3))
- Notice at collection: purpose, right to access/rectify (Section 13)
- For children's data: age verification and parent/guardian consent (Section 8 + Regulation 11)

### Step 4 — Data Subject Rights

Generate FRs for all four Section 14–16 rights:
1. **Right of Access** (Section 14): Data subject may request a copy of all personal data held
2. **Right to Object** (Section 15): Data subject may object to collection/processing; system must stop unless Section 7(2) exception applies
3. **Right to Rectification/Erasure** (Section 16): Correct/delete inaccurate, irrelevant, excessive, out-of-date, incomplete, misleading, or unlawfully obtained data; 30-day response window; written rejection with reasons if unable to comply
4. **Notification to third parties**: Where data has been rectified/erased, notify third parties to whom data was previously disclosed (Section 28(4))

Generate a data subject rights request log schema (see `dppa-pii-classification.md`).

### Step 5 — Security and Technical Measures

Generate NFRs covering Section 20 requirements:
- AES-256-GCM for S-tier fields at rest
- AES-128+ for P-tier fields at rest
- TLS 1.3 for all data in transit
- Access control: S-tier fields restricted to named roles; every access logged
- Risk identification, safeguard establishment, verification, and update cycle
- Data processor contract clause: written contract requiring confidentiality and security measures (Section 21)

### Step 6 — Retention and Destruction

For each data category, generate:
- Configurable retention period (per data type, not hardcoded)
- Automated expiry alert to DPO
- Destruction method: de-identification (preferred) or destruction preventing reconstruction in intelligible form (Section 18(4)-(5))
- Exception: historical/statistical/research retention with identity protection

### Step 7 — Breach Notification Workflow

Generate FRs for the breach notification procedure (Section 23 + Regulation 33):
- **Trigger:** Detection of unauthorised access or acquisition of personal data
- **Immediate action:** System shall flag the breach event and surface it to DPO dashboard
- **Notification content required:** nature of breach, data categories involved, approximate number of data subjects, likely consequences, remedial measures taken and proposed, DPO contact details
- **Timeline:** IMMEDIATE (Uganda Act — no 72-hour window like GDPR)
- **Who is notified:** PDPO first; PDPO then decides and directs whether data subjects must be notified and by what method (registered mail, email, website, or mass media)
- **DPO receives guidance from PDPO** on managing the breach

Distinguish from GDPR: controller does NOT decide independently whether to notify data subjects — PDPO makes this determination.

### Step 8 — DPIA Trigger Assessment

Assess whether any processing operation in this system triggers a mandatory DPIA under Regulation 12:
- Large-scale processing of special personal data
- Systematic monitoring of individuals
- Use of new technologies affecting rights and freedoms

If DPIA is triggered: flag with `[DPIA-REQUIRED: <reason>]` and recommend invoking `dpia-generator` skill.

### Step 9 — DPO and PDPO Registration Requirements

Generate system requirements:
- Store DPO designation: name, role, email, phone (Section 6 + Regulation 47)
- Store PDPO registration number (Regulation 15-16)
- DPO dashboard: data subject rights requests overdue (>30 days), consent records, breach events, retention expiry alerts
- System configuration warning displayed until PDPO registration number is entered

### Step 10 — Cross-border Transfer Controls

If the system stores or processes data outside Uganda:
- Configuration record confirming destination country adequacy, OR
- Explicit data subject consent recorded for each transfer (Section 19 + Regulation 30)

For on-premise Uganda-only deployments: confirm no data leaves Uganda and document this.

---

## Output Structure

Generate the following sections in the target document:

```
## Section X — Data Protection and Privacy Compliance (DPPA 2019)

### X.1  PII Inventory and Classification
[Table: field, module, tier S/P/N, lawful basis, retention period]

### X.2  Special Personal Data Alert
[Uganda-specific: list all S-tier fields; note financial information as special category]

### X.3  Consent Requirements
[FR table: consent capture, notice, children's safeguard, withdrawal]

### X.4  Data Subject Rights Implementation
[FR table: access, object, rectify/erase, 30-day SLA, written rejection, third-party notification]

### X.5  Security and Technical Measures
[NFR table: encryption tiers, TLS, access control, processor contracts]

### X.6  Retention and Destruction Schedule
[Table: data category, retention period, destruction method]

### X.7  Data Breach Notification Procedure
[FR: detection trigger → DPO dashboard → immediate PDPO notification → await PDPO direction → notify data subjects if directed]

### X.8  DPIA Assessment
[DPIA-REQUIRED flags if triggered; otherwise confirmation that no DPIA is required]

### X.9  DPO and PDPO Registration
[FR: DPO record, PDPO registration number, DPO dashboard]

### X.10 Cross-border Transfer Controls
[NFR: confirmation of Uganda-only storage or adequacy documentation]

### X.11 Human Review Gate
[List all [CONTEXT-GAP] flags; list all [DPIA-REQUIRED] flags; confirm legal review status of GAP-004 type items]
```

---

## Validation Checklist

Before marking this skill complete, confirm:
- [ ] Every module that collects data has at least one field in the PII inventory
- [ ] Every S-tier field has AES-256-GCM encryption specified in Section X.5
- [ ] Every mobile money number is classified as S-tier (financial information)
- [ ] Breach notification is labelled IMMEDIATE (not 72 hours)
- [ ] Data subject rights response SLA is 30 days (not 1 month — use "30 calendar days")
- [ ] PDPO — not the data controller — decides whether to notify data subjects of a breach
- [ ] DPIA assessment is explicit: either DPIA-REQUIRED flag or confirmed not triggered
- [ ] DPO record requirement is generated
- [ ] PDPO registration requirement is generated
- [ ] Children's data safeguard generated if any persona may be under 18

---

## Fail Tags

- `[DPPA-FAIL: S-tier field not encrypted]` — special personal data field without AES-256-GCM specification
- `[DPPA-FAIL: no consent mechanism]` — personal data collected without lawful basis or consent FR
- `[DPPA-FAIL: breach notification > immediate]` — breach notification SLA longer than immediate
- `[DPPA-FAIL: no data subject rights FR]` — module collects personal data but has no corresponding rights FRs
- `[DPIA-REQUIRED: <reason>]` — processing operation triggers mandatory DPIA
- `[CONTEXT-GAP: GAP-004]` — Uganda DPPA 2019 legal review not yet commissioned

---

## References

- Uganda Data Protection and Privacy Act 2019 (No. 9 of 2019)
- Data Protection and Privacy Regulations 2021
- `domains/uganda/references/regulations.md` — full section reference
- `domains/uganda/references/dppa-pii-classification.md` — PII classification matrix and schemas
- `domains/uganda/INDEX.md` — key DPPA differences from GDPR