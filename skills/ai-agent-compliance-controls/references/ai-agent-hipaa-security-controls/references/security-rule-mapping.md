# HIPAA Security Rule (45 CFR §§ 164.306–.318) — Agent Implementation Mapping

The full Security Rule clause → agent implementation table. Used by the auditor when sampling controls and by the HIPAA Security Officer when signing the quarterly attestation.

**A** = Addressable (must be implemented or documented as not reasonable + alternative chosen). **R** = Required.

---

## § 164.306 — General Requirements

The covered entity / business associate must:

1. Ensure CIA of ePHI it creates, receives, maintains, transmits.
2. Protect against reasonably anticipated threats to security or integrity.
3. Protect against reasonably anticipated impermissible uses/disclosures.
4. Ensure workforce compliance.

Agent implementation: all of this skill's other safeguards, anchored by the HIPAA Risk Analysis (SRS engine).

---

## § 164.308 — Administrative Safeguards

| Standard | Spec | R/A | Agent Implementation | Evidence |
|---|---|---|---|---|
| (a)(1) Security management process | Risk analysis | R | HIPAA Risk Analysis (SRS engine) covers agents | DOC in repo, annual review |
| (a)(1) | Risk management | R | Risk treatment plan with agent-specific risks | Plan + tracking ticket |
| (a)(1) | Sanction policy | R | Disciplinary process for AI Use Policy violation | Policy doc, signed |
| (a)(1) | Information system activity review | R | Action audit log review monthly | Review records |
| (a)(2) Assigned security responsibility | — | R | Named HIPAA Security Officer | `control-owners.md` |
| (a)(3) Workforce security | Authorisation/supervision | A | Per-tenant tool allow-list + per-tool min-role | Allow-list export |
| (a)(3) | Clearance procedure | A | Background screening for kill-switch operators and approvers | Screening records |
| (a)(3) | Termination procedure | R | SCIM deprovisioning on termination | SCIM event log |
| (a)(4) Info access management | Isolating health care clearinghouse | R | N/A unless clearinghouse | — |
| (a)(4) | Access authorisation | A | PHI scope classification per agent + tool registration gate | Scope register, registration log |
| (a)(4) | Access establishment/modification | A | Approval workflow for adding PHI scope to a feature | Change ticket |
| (a)(5) Security awareness and training | Security reminders | A | Agent PHI handling reminders in code review tooling | Reminder log |
| (a)(5) | Protection from malicious software | A | Sandbox for tool execution + prompt-injection scanner | Scanner log |
| (a)(5) | Log-in monitoring | A | SSO + agent admin session log | Session log |
| (a)(5) | Password management | A | MFA on approvers; rotation | MFA enforcement log |
| (a)(6) Security incident procedures | Response and reporting | R | AI incident runbook + HIPAA breach notification path | Incident records |
| (a)(7) Contingency plan | Data backup plan | R | Audit log + agent state backups | Backup attestations |
| (a)(7) | Disaster recovery plan | R | Multi-region runtime; recovery procedures | DR drill records |
| (a)(7) | Emergency mode operation plan | R | Degraded mode (read-only / abstain-mode) for agents | Runbook |
| (a)(7) | Testing and revision | A | Quarterly DR + resumability drill | Drill records |
| (a)(7) | Applications and data criticality analysis | A | Per-feature criticality classification | Catalogue |
| (a)(8) Evaluation | — | R | Annual HIPAA evaluation via control test suite | Annual report |
| (b)(1) Business associate contracts | Written agreements | R | BAA register; LLM provider BAA enforcement | BAA register export |

---

## § 164.310 — Physical Safeguards

Largely inherited from the cloud provider. Document inheritance with provider attestations (SOC 2, HITRUST, ISO 27001 / 27018).

| Standard | Implementation |
|---|---|
| (a) Facility access controls | Cloud provider |
| (b) Workstation use | Workforce endpoint policy |
| (c) Workstation security | Endpoint policy |
| (d) Device and media controls | HSM custody for evidence vault key |

---

## § 164.312 — Technical Safeguards

| Standard | Spec | R/A | Agent Implementation | Evidence |
|---|---|---|---|---|
| (a)(1) Access control | Unique user identification | R | SSO user ID flows from request → agent task → tool call → audit row | Action audit log sample |
| (a)(2)(i) | Emergency access procedure | R | Back-office break-glass with audit + post-incident review | Break-glass log |
| (a)(2)(ii) | Automatic logoff | A | Session timeout; agent task auto-paused on signout | Session config |
| (a)(2)(iii) | Encryption / decryption | A | TLS in transit; AES-256 at rest; tool args encrypted in audit log | Config export |
| (b) Audit controls | — | R | Hash-chained action audit log; PHI-flag on rows; 6-year retention | Audit log integrity report, retention log |
| (c)(1) Integrity | — | R | Hash chain prevents undetected modification; nightly verification | Integrity verification report |
| (c)(2) | Mechanism to authenticate ePHI | A | Patient-ID cross-check before write; receiver verification on transmissions | Test results |
| (d) Person or entity authentication | — | R | SSO + MFA on approvers; service identity for agents | MFA log; service identity log |
| (e)(1) Transmission security | — | R | TLS 1.2+ enforced to all providers and partners | Cipher suite enforcement log |
| (e)(2)(i) | Integrity controls | A | Receiver signature verification on partner transmissions | Verification log |
| (e)(2)(ii) | Encryption | A | TLS enforced; cipher allow-list | Allow-list config |

---

## §§ 164.314 — Organisational Requirements

| Standard | Implementation |
|---|---|
| (a) BAA with subcontractors | BAA register; tool registration gated on provider BAA |
| (b) Health plan / group plan documents | N/A for SaaS |

---

## § 164.316 — Policies and Procedures and Documentation Requirements

| Standard | Implementation |
|---|---|
| (a) Policies and procedures | Information Security Policy + AI Use Policy + Agent Code of Conduct |
| (b)(1) Documentation | Documents retained 6 years from later of date created or last in effect |
| (b)(2)(i) Time limit | 6-year retention enforced on policy versions |
| (b)(2)(ii) Availability | Documents stored in compliance evidence vault |
| (b)(2)(iii) Updates | Annual policy review + per-incident updates |

---

## § 164.404–.414 — Breach Notification

| Standard | Implementation |
|---|---|
| 164.404 Notification to individuals | Detection signal → HIPAA Security Officer → 60-day notification |
| 164.406 Notification to media | > 500 in a state → press release within 60 days |
| 164.408 Notification to HHS | > 500 → immediately; less → annually within 60 days of end of calendar year |
| 164.410 Notification by BA | Subprocessor breach → BA notifies CE within 60 days |
| 164.412 Law enforcement delay | Documented if LE requests delay |
| 164.414 Administrative requirements | Breach incident record retained 6 years; evidence pack |

Breach detection signals wired into AI incident triage; severity matrix already pages the HIPAA Security Officer on `cross_tenant_phi_leak`, `phi_to_provider_without_baa`, `agent_phi_to_wrong_recipient`.

---

## Notes for the Auditor

- 6-year retention applies broadly across HIPAA: action audit log, policies, training records, BAA records, incident records.
- For each Addressable spec we either implement OR document the reason it is not reasonable AND the chosen alternative. The HIPAA Risk Analysis (SRS engine) captures this rationale.
- LLM providers are Business Associates. Without a BAA, the provider cannot see PHI. The runtime enforces this at tool registration time, not at request time.
- The OCR audit protocol (HHS Office for Civil Rights) is the source of truth for "what does an auditor sample"; this mapping is structured to satisfy that protocol's evidence asks.
