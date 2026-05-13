# SOC 2 Trust Service Criteria → Agent Control Mapping

This is the full mapping table the auditor will sample against. Each row: TSC, control description, **agent-specific** implementation, evidence artefact, cadence, owner.

References use the AICPA 2017 TSC framework (CC = Common Criteria for Security; A = Availability; C = Confidentiality; PI = Processing Integrity; P = Privacy).

---

## CC — Security (Common Criteria)

### CC1 — Control Environment

| TSC | Agent Implementation | Evidence | Cadence | Owner |
|---|---|---|---|---|
| **CC1.1** Demonstrates commitment to integrity and ethical values | AI Use Policy, agent code of conduct, prompt registry usage rules | Signed AI Use Policy, training completion records | Annual + new-hire | CISO |
| **CC1.4** Demonstrates commitment to competence | Engineers building agents are trained on the agent stack; competency log | Training log per engineer, agent skill certifications | Semi-annual | Eng leadership |
| **CC1.5** Holds individuals accountable | Each agent control has a named owner in `control-owners.md` | Owner table + quarterly attestations | Quarterly | CISO |

### CC2 — Communication and Information

| TSC | Agent Implementation | Evidence | Cadence | Owner |
|---|---|---|---|---|
| **CC2.1** Information to support functioning of internal control | Compliance console + auditor portal | Console screenshots + access logs | Monthly | Compliance lead |
| **CC2.2** Internal communication of objectives | AI Use Policy distributed; agent-incident lessons broadcast | Distribution log; postmortem broadcasts | Quarterly | CISO |
| **CC2.3** External communication | Trust portal; subprocessor list (LLM providers) public | Trust portal change log | Per change | Compliance lead |

### CC3 — Risk Assessment

| TSC | Agent Implementation | Evidence | Cadence | Owner |
|---|---|---|---|---|
| **CC3.1** Specifies suitable objectives | Agent feature catalogue with stated objectives, risk class per feature | Catalogue export | Quarterly | Product + Security |
| **CC3.2** Identifies and analyses risks | DPIA per agent feature; red-team plan | DPIA docs; red-team results | Per feature + quarterly | Security |
| **CC3.4** Identifies and assesses changes | Tool / prompt / model change log gated by review | Change log entries | Per change | Eng leadership |

### CC4 — Monitoring Activities

| TSC | Agent Implementation | Evidence | Cadence | Owner |
|---|---|---|---|---|
| **CC4.1** Evaluates internal control performance | Control test suite (`ai-agent-control-testing-and-attestation`) runs monthly | Control test report | Monthly | SRE |
| **CC4.2** Evaluates and communicates deficiencies | Exception register; control failures → ticket | Exception register export | Monthly | Compliance lead |

### CC5 — Control Activities

| TSC | Agent Implementation | Evidence | Cadence | Owner |
|---|---|---|---|---|
| **CC5.1** Selects and develops control activities | Per-TSC control mapping table (this doc) | This doc, version-controlled | Quarterly review | Compliance lead |
| **CC5.2** Selects technology controls | Hash-chained audit log, kill-switch, idempotency, approval gates | Tech stack inventory | Quarterly | Eng leadership |
| **CC5.3** Policies and procedures | AI Use Policy, agent runbook | Policy docs | Annual | CISO |

### CC6 — Logical and Physical Access Controls

| TSC | Agent Implementation | Evidence | Cadence | Owner |
|---|---|---|---|---|
| **CC6.1** Restricts logical access | Per-tenant tool allow-lists; per-tool min-role; SSO/SCIM | Tool registry export per tenant; SSO config | Daily snapshot | Platform eng |
| **CC6.2** New access registered, prior access removed | SCIM provisioning + deprovisioning; agent role table | SCIM event log; deprovisioning timing | Per event + monthly summary | IT ops |
| **CC6.3** User access reviewed | Quarterly access review of agent admin roles and back-office kill-switch operators | Access review sign-off | Quarterly | CISO |
| **CC6.6** Restricts logical access to systems | Agent runtime is a separate deployment; tool gateway enforces allow-list at the tool boundary (not the prompt) | Deployment topology; tool gateway logs | Daily | Platform eng |
| **CC6.7** Restricts physical access | Cloud provider attestations (AWS / GCP / Azure SOC 2 reports) | Provider attestations on file | Annual | IT ops |
| **CC6.8** Restricts external access to public information | Tenant-isolation tests; cross-tenant leak tests | Test reports | Monthly | Security |

### CC7 — System Operations

| TSC | Agent Implementation | Evidence | Cadence | Owner |
|---|---|---|---|---|
| **CC7.1** Detects new vulnerabilities | Agent prompt-injection scanner; tool dependency scanner; model provider CVE feed | Scan reports | Weekly | Security |
| **CC7.2** Monitors system components | Agent runtime SLO dashboard; per-step span emission; anomaly alerting on cost / refusal / abstain / hallucination rates | Dashboard exports + alert log | Weekly | SRE |
| **CC7.3** Evaluates incidents | Triage tree, severity matrix (`ai-incident-detection-and-triage`) | Incident records | Per incident | SRE |
| **CC7.4** Responds to incidents | AI incident runbook; kill-switch; mitigation primitives | Incident postmortems + drill records | Per incident + quarterly drill | SRE |
| **CC7.5** Recovers from incidents | Replay / re-promotion playbook; rollback evidence | Recovery records | Per incident | SRE |

### CC8 — Change Management

| TSC | Agent Implementation | Evidence | Cadence | Owner |
|---|---|---|---|---|
| **CC8.1** Authorises, designs, develops, configures, documents, tests, approves, and implements changes | Tool version pinning + review; prompt registry change review; model pin change procedure | Change tickets + review approvals | Per change | Eng leadership |

### CC9 — Risk Mitigation

| TSC | Agent Implementation | Evidence | Cadence | Owner |
|---|---|---|---|---|
| **CC9.1** Identifies, selects, and develops risk mitigation activities | Red-team plan; reversibility classification; blast-radius limits | Red-team plan + classification doc | Quarterly | Security |
| **CC9.2** Vendor and business partner risk | LLM provider due-diligence pack; subprocessor list; BAA where applicable | Vendor pack; subprocessor change log | Per change + annual | Compliance lead |

---

## A — Availability

| TSC | Agent Implementation | Evidence | Cadence | Owner |
|---|---|---|---|---|
| **A1.1** Maintains, monitors, and evaluates current processing capacity | Step / token / wallclock / cost budgets enforced at runtime; per-tenant quotas | Budget enforcement logs; capacity dashboard | Daily | SRE |
| **A1.2** Authorises, designs, develops, and tests recovery infrastructure | Resumability drill: kill a worker mid-task, prove the next worker resumes without re-charging | Resumability drill report | Quarterly | SRE |
| **A1.3** Tests recovery plan | Action replay availability test: pick a random task from 30 days ago, prove replay still works | Replay availability report | Monthly | SRE |

---

## C — Confidentiality

| TSC | Agent Implementation | Evidence | Cadence | Owner |
|---|---|---|---|---|
| **C1.1** Identifies and maintains confidential information | Data classification on every tool registration; PHI / PII flag; per-tenant memory tagging | Tool registry export with classifications | Daily | Security |
| **C1.2** Disposes of confidential information | Memory-erasure proof (`ai-agent-memory-erasure-proof`); tenant erasure cascade | Erasure evidence packs | Per event | DPO |

---

## PI — Processing Integrity

| TSC | Agent Implementation | Evidence | Cadence | Owner |
|---|---|---|---|---|
| **PI1.1** System processing achieves objectives — complete, valid, accurate, timely, authorised | Approval-audit completeness (every irreversible action has documented approval); hash-chained action audit log; agent loop state machine resumability | Gap-detection report; audit log integrity report | Monthly | Security |
| **PI1.2** Inputs are complete and accurate | Tool input schema validation at registry boundary; tool input audit | Input validation test report | Monthly | Eng leadership |
| **PI1.3** Processing is complete, valid, accurate, timely, authorised | Per-step persistence before next state; idempotency keys; budget enforcement | State machine test suite; idempotency tests | Per release + monthly | Eng leadership |
| **PI1.4** Outputs are complete and accurate | Eval harness golden coverage; hallucination SLO compliance | Eval coverage report | Monthly | AI lead |
| **PI1.5** Storage of inputs and outputs is complete, valid, accurate, timely, authorised | Action audit log + retention enforcement | Retention enforcement log | Monthly | Platform eng |

---

## P — Privacy

| TSC | Agent Implementation | Evidence | Cadence | Owner |
|---|---|---|---|---|
| **P1** Notice and communication of objectives | Privacy notice covers agent use, memory, LLM subprocessors | Privacy notice version log | Annual + per change | DPO |
| **P2** Choice and consent | Memory consent capture; opt-out per agent feature | Consent records | Per event | DPO |
| **P3** Collection | Tool input schema is minimal; data classification flags | Tool registry classification doc | Quarterly | Security |
| **P4** Use, retention, and disposal | Retention policy per memory tier; per-event-class retention on audit log | Retention enforcement log | Monthly | Platform eng |
| **P5** Access | User-facing "what the agent remembers about me" surface; user can delete | Surface screenshots + delete logs | Quarterly | Product |
| **P6** Disclosure and notification | Subprocessor list (LLM providers); breach notification procedure | Subprocessor list version log; breach drill records | Per change + quarterly | DPO |
| **P7** Quality | Memory consent timestamp + source + confidence on every row | Memory schema export | Quarterly | Security |
| **P8** Monitoring and enforcement | Privacy control test suite; DPIA refresh | Test report; DPIA log | Quarterly + per feature | DPO |

---

## Notes for the Auditor

- All evidence is signed (HSM-backed key). Signature verification instructions in `ai-agent-audit-log-integrity/references/integrity-verification-job.md`.
- Evidence packs are content-addressed; the manifest sha256 is the canonical pack identifier.
- The auditor portal exposes one URL per control × window; see `ai-agent-evidence-automation/references/auditor-portal-design.md`.
- Subprocessor list (LLM providers) tracks data residency, BAA status, SOC 2 / ISO 27001 status, and last attestation date per provider.
- Exception register is open-source within the audit context; closed exceptions are summarised in the quarterly attestation.
