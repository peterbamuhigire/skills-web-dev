# ISO 27001:2022 Annex A → Agent Implementation Mapping

The full Annex A → agent control mapping. ISO 27001:2022 has 93 Annex A controls grouped into 4 themes. Only agent-relevant controls are mapped here; the remainder are covered by the platform ISMS.

Columns: Clause / Title / Agent Implementation / Evidence Artefact / Cadence / Owner.

---

## A.5 — Organisational Controls

| Clause | Title | Agent Implementation | Evidence | Cadence | Owner |
|---|---|---|---|---|---|
| A.5.1 | Policies for information security | AI Use Policy + Agent Code of Conduct | Signed policy version log | Annual | CISO |
| A.5.2 | Information security roles and responsibilities | Control owners table | `docs/compliance/control-owners.md` | Quarterly | CISO |
| A.5.7 | Threat intelligence | LLM provider CVE feed; prompt-injection threat feed | Threat-feed dashboard exports | Weekly | Security |
| A.5.8 | Information security in project management | Per-feature DPIA + risk assessment | DPIA docs in repo | Per feature | Product + Security |
| **A.5.9** | **Inventory of information and other associated assets** | Agent asset register: prompts, tools, models, indices, agent identities, datasets, adapters | `evidence/iso/asset-register-YYYY-MM.csv` | Monthly snapshot | Platform eng |
| **A.5.12** | **Classification of information** | Per-tool / per-prompt classification (public / internal / confidential / restricted / PHI / PCI) | Tool registry export | Daily | Security |
| **A.5.13** | **Labelling of information** | Trace span carries data classification; tool I/O carries classification | Span sample | Continuous | Platform eng |
| **A.5.15** | **Access control** | Per-tenant tool allow-list; per-tool min-role | Allow-list export | Daily | Platform eng |
| A.5.16 | Identity management | SSO/SCIM for staff; service identities for agents | SCIM event log | Per event | IT ops |
| A.5.17 | Authentication information | MFA on approvers; rotation of agent service credentials | MFA enforcement log; rotation log | Monthly | IT ops |
| **A.5.18** | **Access rights** | Quarterly review of agent admin / kill-switch operator roles | Access review sign-off | Quarterly | CISO |
| **A.5.19-.23** | **Supplier relationships** | LLM provider due-diligence pack; subprocessor list; data-processing terms | `evidence/iso/subprocessors-YYYY-Q.csv` | Quarterly + per change | Compliance lead |
| **A.5.24** | **Planning and preparation** | AI incident runbook + drill cadence | Runbook docs; drill log | Quarterly drill | SRE |
| **A.5.25** | **Assessment and decision on info security events** | Severity matrix | Severity rubric doc | Quarterly review | SRE |
| **A.5.26** | **Response to incidents** | Per-class playbooks | Incident records | Per incident | SRE |
| **A.5.27** | **Learning from incidents** | Postmortem template; learnings flywheel | Postmortem records | Per incident | SRE |
| **A.5.28** | **Collection of evidence** | Evidence bundle exporter | Bundles in evidence vault | Per incident | SRE |
| **A.5.34** | **Privacy and PII protection** | Memory erasure proof; consent records | Erasure proof packs | Per event | DPO |
| **A.5.36** | **Compliance with policies** | Control test suite | Test report | Monthly | Compliance lead |
| **A.5.37** | **Documented operating procedures** | Agent runbook; incident runbook | Runbook docs in repo | Quarterly review | SRE |

---

## A.6 — People Controls

| Clause | Title | Agent Implementation | Evidence | Cadence | Owner |
|---|---|---|---|---|---|
| A.6.1 | Screening | Background check for staff who can flip kill-switch or approve high-risk agents | Screening records | Per hire | HR |
| A.6.2 | Terms and conditions of employment | AI Use Policy in employment contract | Signed contracts | Per hire | HR |
| **A.6.3** | **Information security awareness, education, training** | Engineer training on the agent stack; on-call AI incident training | Training log + completion records | Semi-annual | Eng leadership |
| A.6.4 | Disciplinary process | Process for AI Use Policy violations | Documented process | Annual review | HR + CISO |
| A.6.6 | Confidentiality / NDAs | NDAs cover prompts, training data, agent design | Signed NDAs | Per hire | Legal |
| A.6.7 | Remote working | Endpoint policy for staff approving agent actions | Endpoint policy | Annual | IT ops |
| A.6.8 | Information security event reporting | Agent incident reporting channel | Reporting docs | Quarterly review | SRE |

---

## A.7 — Physical Controls

Mostly inherited from the cloud provider; document the provider attestations. Agent-specific: none beyond physical access controls for evidence vault key storage.

| Clause | Title | Agent Implementation | Evidence | Cadence | Owner |
|---|---|---|---|---|---|
| A.7.1-.6 | Various | Inherited from cloud provider SOC 2 / ISO | Provider attestations | Annual | IT ops |
| A.7.10 | Storage media | Evidence vault HSM key custody | Key custody log | Annual | CISO |

---

## A.8 — Technological Controls

| Clause | Title | Agent Implementation | Evidence | Cadence | Owner |
|---|---|---|---|---|---|
| A.8.1 | User endpoint devices | N/A unless agent runs on endpoint | — | — | — |
| **A.8.2** | **Privileged access rights** | Back-office kill-switch operator role; reviewer of irreversible approvals | Role membership export | Quarterly review | CISO |
| A.8.3 | Information access restriction | Tool gateway enforces per-tenant allow-list | Gateway enforcement log | Continuous | Platform eng |
| A.8.4 | Access to source code | Repository access controls; prompt registry write access | Repo audit logs | Quarterly review | Eng leadership |
| **A.8.5** | **Secure authentication** | SSO/SCIM; MFA on approvers and admins | MFA enforcement log | Monthly | IT ops |
| A.8.6 | Capacity management | Step / token / wallclock / cost budgets | Budget enforcement log | Continuous | SRE |
| A.8.7 | Protection against malware | Sandbox for tool execution; prompt-injection scanner | Scanner log | Daily | Security |
| A.8.8 | Management of technical vulnerabilities | Dependency / CVE scanning; provider CVE feed | Scan reports | Weekly | Security |
| **A.8.9** | **Configuration management** | Tool registry + prompt registry are configuration baselines | Registry export | Daily | Platform eng |
| **A.8.10** | **Information deletion** | Memory erasure proof; tenant erasure cascade | Erasure proof packs | Per event | DPO |
| A.8.11 | Data masking | Trace redaction; evidence pack redaction | Redaction policy + sample | Quarterly | Security |
| **A.8.12** | **Data leakage prevention** | Cross-tenant leak test; prompt-injection scanner | Test reports | Weekly | Security |
| A.8.13 | Information backup | Audit log backups; replay artefact backups | Backup attestations | Monthly | IT ops |
| A.8.14 | Redundancy of information processing facilities | Multi-region agent runtime | Runtime topology | Quarterly review | Platform eng |
| **A.8.15** | **Logging** | Hash-chained action audit log | Audit log integrity report | Daily + weekly verification | Platform eng |
| **A.8.16** | **Monitoring activities** | Agent runtime SLO + alerting | Dashboards + alert log | Continuous | SRE |
| A.8.17 | Clock synchronisation | NTP across runtime + audit log | NTP attestation | Annual | IT ops |
| A.8.18 | Use of privileged utility programs | Compliance console operator role | Console access log | Continuous | CISO |
| A.8.19 | Installation of software on operational systems | Prompt / tool / model deployment procedure | Deployment records | Per change | Eng leadership |
| A.8.20-.24 | Network security | Tool gateway as network boundary; egress allow-list | Gateway config; egress log | Monthly | Platform eng |
| **A.8.25** | **Secure development lifecycle** | Prompt as code; eval harness; canary deploy | SDLC doc + deployment records | Quarterly review | Eng leadership |
| A.8.26 | Application security requirements | Tool input schema validation | Schema test report | Per release | Eng leadership |
| A.8.27 | Secure system architecture | Agent runtime as control plane; separate deployment | Architecture doc | Annual review | Eng leadership |
| A.8.28 | Secure coding | Prompt code of conduct; refusal language standards | Style guide + reviews | Per release | AI lead |
| A.8.29 | Security testing in development | Red-team plan; eval harness | Test results | Per release | Security |
| A.8.30 | Outsourced development | LLM provider DPA; subprocessor list | DPAs + subprocessor list | Per supplier | Compliance lead |
| A.8.31 | Separation of dev, test, and production | Distinct agent runtimes; separate prompt registries | Topology doc | Annual review | Platform eng |
| **A.8.32** | **Change management** | Tool / prompt / model pin change procedure | Change ticket log | Per change | Eng leadership |
| A.8.33 | Test information | Eval golden datasets; PII-free test data | Golden dataset registry | Quarterly | AI lead |
| A.8.34 | Protection of information systems during audit testing | Read-only auditor portal access | Auditor access log | Per audit | Compliance lead |

---

## Statement of Applicability (SoA) Coordination

The SoA is produced by the SRS engine. It declares for each Annex A control:

1. Whether the control applies (Y/N).
2. If yes, the implementation reference (one of the rows above).
3. If no, the justification (e.g. A.8.1 N/A because agent does not run on endpoints).

This engineering mapping is the source of truth for the implementation references. When the SRS engine writes the SoA, it cites these rows; the auditor verifies by opening the evidence pack.

---

## Recertification / Surveillance Audit Notes

- ISO 27001 surveillance audits run annually for 2 years after the initial certification, with full recertification at year 3.
- The auditor will sample assets, changes, incidents, and access reviews from the year's window.
- The control test suite (`ai-agent-control-testing-and-attestation`) produces a monthly report; the cumulative annual report is the surveillance evidence.
- Asset register is the most-sampled artefact — investment in its accuracy pays back at every audit.
