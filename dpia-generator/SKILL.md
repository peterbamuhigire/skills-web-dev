# Skill: DPIA Generator (Uganda DPPA 2019)

## Purpose

Generate a Uganda Data Protection and Privacy Act 2019 — compliant Data Protection Impact Assessment (DPIA) document for a specific processing operation that has been flagged with `[DPIA-REQUIRED]`. Implements Regulation 12 of the Data Protection and Privacy Regulations 2021.

Use this skill when:
- The `uganda-dppa-compliance` skill has flagged `[DPIA-REQUIRED: <reason>]` for a processing operation
- The consultant is preparing for Phase 3 go-live involving farmer personal data
- Any new processing feature involves large-scale, systematic, or special personal data collection
- A PDPO auditor requests a DPIA on file

---

## Inputs Required

Before invoking this skill, read:
- `_context/vision.md` — system scope
- `_context/features.md` — the specific processing operation being assessed
- `_context/personas.md` — data subjects affected
- `_context/gap-analysis.md` — open privacy gaps
- The specific `[DPIA-REQUIRED]` flag text and its context in the originating document
- `domains/uganda/references/dppa-pii-classification.md` — PII classification matrix

Ask the consultant to identify: **Which processing operation is being assessed?** (e.g., "bulk collection of farmer NIN, GPS, photo, and mobile money number during cooperative registration")

---

## DPIA Structure (Regulation 12)

### Section 1 — Processing Operation Description

**1.1 Operation name and purpose**
Name the specific processing operation. State its purpose. Cite the module and FR identifiers.

**1.2 Data controller and DPO**
Name the data controller (organisation), designated DPO, and PDPO registration number.

**1.3 Categories of data subjects**
Describe who is affected: number of individuals, demographics, vulnerability factors (e.g., rural smallholder farmers with limited digital literacy).

**1.4 Data categories collected**
List every field. Classify each as S (special personal data), P (personal data), or N (non-personal). For S-tier fields, cite the Section 9 category.

| Field | Tier | Section 9 Category | Volume |
|---|---|---|---|
| Mobile money number | S | Financial information | 6,440+ |
| NIN | P | Identification number | 6,440+ |
| GPS farm coordinates | P | Location/identity | 6,440+ |
| Photograph | P | Identity data | 6,440+ |

**1.5 Processing activities**
Describe what happens to the data: collection, storage, use, disclosure, retention, destruction.

**1.6 Lawful basis**
For each data category, cite the applicable Section 7 lawful basis.

**1.7 Data processors involved**
List any third parties processing data (MTN MoMo, Airtel, NIRA, etc.) and confirm written contracts exist per Section 21.

**1.8 Cross-border transfer**
State whether data is processed or stored outside Uganda. If yes, document adequacy or consent.

---

### Section 2 — Necessity and Proportionality Assessment

**2.1 Necessity**
Is the data collection necessary for the stated purpose? Could the purpose be achieved with less data or less intrusive means?

**2.2 Proportionality**
Is the scope of collection proportionate to the legitimate purpose?

**2.3 Data minimisation**
Confirm that only the minimum necessary data is collected. Flag any field that is not strictly necessary.

**2.4 Purpose limitation**
Confirm data will not be used for purposes incompatible with the original purpose (Section 17). State research/statistical exceptions if applicable (must not reveal identity).

**2.5 Storage limitation**
State the retention period and destruction method at expiry.

---

### Section 3 — Risk Assessment

Identify and rate each risk using the matrix below.

**Risk Rating Matrix:**

| Likelihood | Low Impact | Medium Impact | High Impact |
|---|---|---|---|
| Unlikely | Low | Low | Medium |
| Possible | Low | Medium | High |
| Likely | Medium | High | Critical |

**Risk categories to assess:**

| # | Risk | Description | Likelihood | Impact | Rating |
|---|---|---|---|---|---|
| R-1 | Unauthorised access to S-tier financial data | Mobile money numbers accessed by unauthorised staff | | | |
| R-2 | GPS data misuse | Farm location data enables physical targeting of farmers | | | |
| R-3 | NIN data breach | Mass NIN exposure creates identity fraud risk | | | |
| R-4 | Consent not obtained | Data collected without valid consent; PDPO enforcement risk | | | |
| R-5 | Data shared with unauthorised third parties | Farmer data disclosed outside permitted recipients | | | |
| R-6 | Breach not notified immediately | PDPO notification delayed; criminal liability for DPO | | | |
| R-7 | Data retained beyond retention period | Historical data not destroyed; creates ongoing liability | | | |
| R-8 | Children's data collected without guardian consent | Farmers under 18 registered without parental consent | | | |
| R-9 | Cross-border storage | Cloud backup transfers data outside Uganda without adequacy or consent | | | |
| R-10 | Data subject rights not fulfilled | Requests not responded to within 30 days | | | |

Add system-specific risks based on the processing operation being assessed.

---

### Section 4 — Measures to Address Risks

For each risk rated Medium, High, or Critical, specify the control measure:

| Risk # | Control Measure | FR/NFR Reference | Owner | Status |
|---|---|---|---|---|
| R-1 | AES-256-GCM encryption + role-based access + access logging | NFR-DPPA-002 | Dev Lead | Planned |
| R-2 | GPS stored encrypted; access restricted to Procurement/Finance | NFR-FAR-001 | Dev Lead | Planned |
| R-3 | NIN encrypted + masked in display; NIRA validation only via API | NFR-DPPA-002 | Dev Lead | Planned |
| R-4 | Consent capture FR at farmer registration; consent record persisted | FR-FAR-xxx | Dev Lead | Planned |
| R-5 | API-layer RBAC; data processor contracts signed | NFR-DPPA-005 | Legal | Pending |
| R-6 | Breach notification workflow; DPO dashboard alert; auto-generates PDPO notification form | NFR-DPPA-005 | Dev Lead | Planned |
| R-7 | Retention schedule enforced; DPO expiry alert; destruction audit log | NFR-DPPA-006 | Dev Lead | Planned |
| R-8 | Age verification step in registration; parent/guardian consent prompt for under-18 | FR-FAR-xxx | Dev Lead | Planned |
| R-9 | On-premise only; no cloud backup outside Uganda; server location documented | NFR-DPPA-010 | BIRDC IT | Pending |
| R-10 | Data subject rights log; 30-day DPO dashboard alert | NFR-DPPA-004 | Dev Lead | Planned |

---

### Section 5 — Residual Risk Assessment

After controls: rate residual risk for each item. If any residual risk remains High or Critical, escalate to PDPO consultation (Regulation 12 — high residual risk requires PDPO prior consultation).

---

### Section 6 — PDPO Consultation Determination

If any processing operation carries residual high risk that cannot be mitigated internally:
- Consult the PDPO before commencing processing
- Document the consultation outcome
- Obtain PDPO guidance in writing

---

### Section 7 — Sign-off

| Role | Name | Date | Signature |
|---|---|---|---|
| Data Protection Officer | | | |
| Consultant / System Architect | Peter Bamuhigire | | |
| Client Authorising Officer | | | |

---

## Output Format

Generate a `.md` file in `projects/<ProjectName>/09-governance-compliance/dpia/DPIA_<OperationName>_<ProjectName>.md` covering all 7 sections above.

Build to `.docx` using: `bash scripts/build-doc.sh projects/<ProjectName>/09-governance-compliance/dpia DPIA_<OperationName>_<ProjectName>`

---

## Validation Checklist

Before marking this skill complete:
- [ ] Every S-tier field has an explicit control measure
- [ ] No residual risk is rated Critical without PDPO consultation recommendation
- [ ] Retention period is specified for every data category
- [ ] Children's data assessed
- [ ] Cross-border transfer status confirmed
- [ ] Sign-off table populated (roles at minimum; names/dates pending client)
- [ ] `[CONTEXT-GAP: GAP-004]` retained if legal review not yet complete

---

## References

- Data Protection and Privacy Act 2019 (No. 9 of 2019) — Section 23 (breach), Section 9 (special data)
- Data Protection and Privacy Regulations 2021 — Regulation 12 (DPIA), Regulation 33 (breach notification)
- `domains/uganda/references/regulations.md`
- `domains/uganda/references/dppa-pii-classification.md`
- `skills/uganda-dppa-compliance/SKILL.md` — prerequisite skill
