# Evidence Catalogue

One row per evidence type the platform produces. Source of truth for: what evidence exists, who consumes it (which control), how it is produced, where it lives, how long it is retained, who owns it.

This catalogue is exported quarterly as part of the attestation pack.

---

## Format

| # | Evidence | Producer | Trigger / Cadence | Vault Path | Retention | Owner | Consumed By |
|---|---|---|---|---|---|---|---|

---

## Continuous / Per-Event

| # | Evidence | Producer | Trigger | Vault Path | Retention | Owner | Consumed By |
|---|---|---|---|---|---|---|---|
| 1 | Action audit log row | Runtime + tool gateway | Per action | `audit/rows/YYYY/MM/DD.jsonl` | by event class (3-10y) | Platform eng | CC6.1, CC7.2, PI1.1, A.8.15, 164.312(b) |
| 2 | Approval grant / reject | Approval service | Per approval | (inside audit log) | 7y | Security | PI1.1, A.5.15, 164.312(a) |
| 3 | Kill-switch flip | Back-office | Per flip | (inside audit log) | 7y | SRE | CC7.4, A.5.26 |
| 4 | PHI access event | Tool gateway | Per access | (inside audit log) | 6y | HIPAA Security Officer | 164.312(b) |
| 5 | Memory write to long-term | Memory service | Per write | (inside audit log) | 7y | Security | A.8.10, P4 |
| 6 | Memory erasure proof | Erasure verifier | Per erasure request | `erasure/proof-{request_id}.tar.gz` | 7y | DPO | C1.2, A.5.34, A.8.10, P4, 164.310(d) |

---

## Daily

| # | Evidence | Producer | Cadence | Vault Path | Retention | Owner | Consumed By |
|---|---|---|---|---|---|---|---|
| 7 | Audit log daily seal | Seal job | 04:00 daily | `audit/seal/YYYY-MM-DD.json` | indefinite | Platform eng | A.8.15, PI1.5 |
| 8 | Audit log integrity report | Verifier daemon | 05:00 daily | `audit/verify/YYYY-MM-DD.json` | 7y | Platform eng | A.8.15, CC7.2, PI1.5 |
| 9 | Tool registry snapshot | Allowlist collector | 01:00 daily | `compliance/cc6_1/YYYY-MM-DD.tar.gz` | 3y | Platform eng | CC6.1, A.5.15 |
| 10 | Configuration baseline | Config collector | 02:00 daily | `compliance/a8_9/YYYY-MM-DD.tar.gz` | 3y | Platform eng | A.8.9, CC8.1 |
| 11 | BAA drift check | BAA drift detector | 03:00 daily | `compliance/baa/YYYY-MM-DD.json` | 6y | HIPAA Security Officer | 164.308(b)(1) |

---

## Weekly

| # | Evidence | Producer | Cadence | Vault Path | Retention | Owner | Consumed By |
|---|---|---|---|---|---|---|---|
| 12 | Agent runtime monitoring evidence | CC7.2 collector | Mon 02:00 | `compliance/cc7_2/YYYY-WW.tar.gz` | 7y | SRE | CC7.2, A.8.16 |
| 13 | Cross-tenant isolation test | Isolation test runner | Mon 03:00 | `compliance/cc6_8/YYYY-WW.tar.gz` | 7y | Security | CC6.8, A.8.12 |
| 14 | Prompt-injection scan | Scanner | Mon 04:00 | `compliance/cc7_1/YYYY-WW.tar.gz` | 3y | Security | CC7.1, A.8.7 |
| 15 | Vulnerability scan | Dependency scanner | Mon 04:30 | `compliance/cc7_1/vuln-YYYY-WW.tar.gz` | 3y | Security | CC7.1, A.8.8 |

---

## Monthly

| # | Evidence | Producer | Cadence | Vault Path | Retention | Owner | Consumed By |
|---|---|---|---|---|---|---|---|
| 16 | Replay availability test | Replay collector | 1st 03:00 | `compliance/a1_3/YYYY-MM.tar.gz` | 7y | SRE | A1.3 |
| 17 | Approval-audit completeness gap report | Gap detector | 1st 03:00 | `compliance/pi1_1/YYYY-MM.tar.gz` | 7y | Security | PI1.1, A.5.15 |
| 18 | Eval coverage report | Eval harness | 1st 04:00 | `compliance/pi1_4/YYYY-MM.tar.gz` | 3y | AI lead | PI1.4, A.8.29 |
| 19 | Incident records | Incident collector | 1st 06:00 | `compliance/incidents/YYYY-MM.tar.gz` | 7y | SRE | CC7.3, CC7.4, A.5.24-.28 |
| 20 | PHI access slice | HIPAA collector | 1st 04:00 | `compliance/164_312_b/YYYY-MM.tar.gz` | 6y | HIPAA Security Officer | 164.312(b) |
| 21 | Asset register snapshot | A.5.9 collector | 1st 01:00 | `compliance/a5_9/YYYY-MM.tar.gz` | 7y | Platform eng | A.5.9 |
| 22 | Monitoring review sign-off | Monitoring team | Last business day | `compliance/a8_16/YYYY-MM.tar.gz` | 7y | SRE | A.8.16 |
| 23 | Control test report | Control test runner | 1st 07:00 | `compliance/cc4_1/YYYY-MM.tar.gz` | 7y | Compliance lead | CC4.1, A.5.36 |
| 24 | Exception register snapshot | Compliance console | 1st 08:00 | `compliance/exceptions/YYYY-MM.tar.gz` | 7y | Compliance lead | CC4.2, A.5.36 |

---

## Quarterly

| # | Evidence | Producer | Cadence | Vault Path | Retention | Owner | Consumed By |
|---|---|---|---|---|---|---|---|
| 25 | Kill-switch drill record | Drill harness | Per drill (>= 1/q) | `drills/kill_switch-{date}.tar.gz` | 7y | SRE | CC7.4, A.5.24 |
| 26 | Resumability drill record | Drill harness | Per drill (>= 1/q) | `drills/resumability-{date}.tar.gz` | 7y | SRE | A1.2, A.5.24 |
| 27 | Red-team report | Red-team harness | Per quarter | `drills/red_team-{date}.tar.gz` | 7y | Security | CC9.1, A.8.29 |
| 28 | Subprocessor pack | Vendor collector | 1st of quarter | `compliance/cc9_2/YYYY-Q.tar.gz` | 7y | Compliance lead | CC9.2, A.5.19-.23 |
| 29 | Access review sign-off | Quarterly review | Per review | `compliance/cc6_3/YYYY-Q.tar.gz` | 7y | CISO | CC6.3, A.5.18 |
| 30 | Control owner attestation | Per owner | Per quarter | `compliance/attestations/YYYY-Q-{owner}.tar.gz` | 7y | Each control owner | CC1.5 |
| 31 | DPIA refresh log | DPO | Per quarter | `compliance/dpia/YYYY-Q.tar.gz` | 7y | DPO | P8, A.5.34 |
| 32 | Privacy control test | DPO | Per quarter | `compliance/p_tests/YYYY-Q.tar.gz` | 7y | DPO | P1-P8 |

---

## Semi-Annual / Annual

| # | Evidence | Producer | Cadence | Vault Path | Retention | Owner | Consumed By |
|---|---|---|---|---|---|---|---|
| 33 | Workforce training records | HR | Semi-annual | `compliance/cc1_4/YYYY-H.tar.gz` | 7y | HR + CISO | CC1.4, A.6.3, 164.308(a)(5) |
| 34 | Policy versions | CISO | Annual | `compliance/policies/YYYY.tar.gz` | 7y | CISO | CC5.3, A.5.1 |
| 35 | HIPAA annual evaluation | HIPAA Security Officer | Annual | `compliance/164_308_a_8/YYYY.tar.gz` | 6y | HIPAA Security Officer | 164.308(a)(8) |
| 36 | ISO surveillance pack | Compliance lead | Annual | `compliance/iso_surveillance/YYYY.tar.gz` | indefinite | Compliance lead | ISO certification |
| 37 | SOC 2 Type II attestation pack | Compliance lead | Annual | `compliance/soc2_t2/YYYY.tar.gz` | indefinite | Compliance lead | SOC 2 |

---

## Per-Incident / Per-Audit-Request

| # | Evidence | Producer | Trigger | Vault Path | Retention | Owner | Consumed By |
|---|---|---|---|---|---|---|---|
| 38 | Incident evidence bundle | Incident exporter | Per incident | `incidents/inc-{id}/bundle.tar.gz` | 7-10y | SRE | CC7.3, CC7.4, A.5.26-.28 |
| 39 | Postmortem record | Postmortem template | Per incident | `incidents/inc-{id}/postmortem.md` | 7y | SRE | CC7.5, A.5.27 |
| 40 | Audit log export pack | Export endpoint | Per audit request | `exports/aud-{id}/pack.tar.gz` | 7y | Platform eng | (audit ask) |
| 41 | HIPAA breach evidence pack | Breach handler | Per breach | `breach/{id}/pack.tar.gz` | 6y | HIPAA Security Officer | 164.404-.414 |

---

## Catalogue Notes

- The catalogue is exported as `evidence/catalogue/YYYY-Q.csv` quarterly.
- Adding evidence: open a change ticket; review by Compliance lead + CISO; row added; new collector deployed.
- Retiring evidence: must include rationale and reference to the SoA (ISO) / system description (SOC 2) update.
- Coverage check: each control in `trust-criteria-mapping.md`, `annex-a-mapping.md`, `security-rule-mapping.md` must reference at least one catalogue row. A gap means the control is unevidenced — auditor finding.
