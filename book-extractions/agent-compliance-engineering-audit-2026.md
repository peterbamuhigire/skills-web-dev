# AI Agent Compliance Engineering Skills Audit — May 2026

**Lens:** Engineer the **agent-specific** control implementations and automated-evidence pipelines so an agentic SaaS can pass **SOC 2 Type II**, **ISO/IEC 27001:2022**, and **HIPAA Security Rule** audits. Pairs with the SRS engine session which produces the policy, control-mapping, and attestation-package documents. This audit is for the engineering / tooling / automated-evidence side: code, jobs, schemas, evidence collectors, integrity verification, gap-detection.

**Inputs reviewed:** agent stack (`ai-agent-runtime-architecture`, `ai-agent-tool-catalogue-and-action-gating`, `ai-agent-action-approval-and-hitl`, `ai-agent-safety-and-red-team`, `ai-agent-observability-and-replay`, `ai-agent-memory`, `ai-agent-eval`, `ai-agent-reversibility-and-blast-radius`, `ai-agent-cost-and-step-budgets`); incident stack (`ai-incident-evidence-capture`, `ai-incident-drill-and-game-day`, `ai-incident-postmortem`, `ai-incident-response-runbook`); platform (`saas-control-plane-engineering`, `saas-tenant-data-portability-and-erasure`, `saas-admin-backoffice-tooling`, `saas-sso-scim-enterprise-auth`, `ai-security`, `ai-tenant-isolation-patterns`, `multi-tenant-saas-architecture`, `uganda-dppa-compliance`).

**Prior verdict:** the engine has solid agentic primitives (state machine, tool gating, HITL approval, kill-switch, replay, memory, eval, red-team) and a strong incident response stack (evidence bundle exporter, drills). What is missing is the **compliance layer that turns those primitives into evidence on a cadence and proves controls were satisfied during the audit window** (SOC 2 Type II = continuous evidence over 6-12 months; ISO 27001 = annual surveillance; HIPAA = ongoing). An auditor will not accept "we have an approval table" — they require: "Show me every irreversible action in Q2, prove each had a documented approval, prove the audit log was tamper-evident, prove the kill-switch was drilled monthly with pass/fail evidence, prove the action-replay is available on demand, prove memory-erasure completed end-to-end for the 7 erasure requests in the window." That is engineering work, not policy work, and it does not yet exist in the engine.

---

## Existing Compliance-Related Coverage Audit

| Skill | Coverage today | Gap for agent compliance |
|---|---|---|
| `saas-control-plane-engineering` | Audit log spine, tenant lifecycle | Audit log is not hash-chained or tamper-evident; no agent-specific retention; no integrity verification job. |
| `saas-tenant-data-portability-and-erasure` | GDPR / POPIA / KE DPA erasure cascade | Mentions agent-memory leaf but no signed proof-of-erasure evidence pack; no verification job. |
| `saas-admin-backoffice-tooling` | Tenant ops, kill-switch console | No compliance console: no per-control status view, no evidence-pack export, no auditor portal. |
| `ai-incident-evidence-capture` | Incident evidence bundle | Bundle is per-incident only; not a continuous-evidence pipeline; no SOC 2 / HIPAA control mapping. |
| `ai-incident-drill-and-game-day` | Drill cadence | Drills are not captured as compliance evidence; no cadence enforcement at the platform level; no auditor-friendly drill report. |
| `ai-agent-action-approval-and-hitl` | Approval state machine + table | No completeness check (every irreversible action ↔ approval row); no gap-detection job. |
| `ai-agent-memory` | Three-tier memory + erasure cascade | No signed proof-of-erasure; cascade not exercised as a periodic job for evidence. |
| `ai-agent-eval` | Eval harness | Eval results not exported as compliance evidence on cadence. |
| `ai-agent-safety-and-red-team` | Red-team test catalogue | Results not exported as evidence; no minimum cadence. |
| `ai-agent-observability-and-replay` | Replay tool | Replay availability not measured / proven as SLA-bearing evidence. |
| `uganda-dppa-compliance` | KE / UG data protection mapping | Region-specific; no SOC 2 / ISO 27001 / HIPAA. |
| `ai-security` | AI threat model | Not mapped to control framework. |

---

## Cross-Cutting Gaps

1. **No SOC 2 trust-service-criteria mapping for agents.** No skill maps Security, Availability, Confidentiality, Processing Integrity, Privacy to agent-specific controls (kill-switch, approval gates, action audit, replay availability, eval coverage). Auditor asks: "how do you implement Processing Integrity for an LLM-driven action?" — no answer in the engine.
2. **No ISO 27001 Annex A mapping for agents.** A.5 / A.8 / A.12 / A.14 / A.16 / A.18 controls do not yet have agent implementations (asset register for tools and prompts; secure development for prompts; operations including the kill-switch as a documented operational control; incident management tying to the AI incident stack).
3. **No HIPAA Security Rule mapping for clinical PHI agents.** 164.306–.318 (administrative, physical, technical safeguards) does not exist for agents handling PHI; admin-only constraint for clinical use; BAA implications when LLM provider is in the loop.
4. **No tamper-evident action audit log.** Action audit log is in the runtime spec but not hash-chained, not write-once, not integrity-verified. Auditor will reject "we have a row in the database" as evidence if the row is mutable.
5. **No automated evidence collection pipeline.** Every control needs an evidence collector that runs on cadence and produces auditor-ready artefacts. None of this is engineered.
6. **No control-testing automation.** Controls must be tested on cadence; failures must become tickets; reports must be auditor-friendly. Missing.
7. **No approval-audit completeness check.** Cannot today prove that every irreversible action in Q2 had an approval. Gap-detection job does not exist.
8. **No drill-evidence pipeline.** Drills are run (`ai-incident-drill-and-game-day`) but the evidence is not captured in a SOC 2 / HIPAA-friendly format with pass/fail recording and cadence enforcement.
9. **No memory-erasure proof.** Erasure runs but does not emit a signed, auditor-ready proof artefact.
10. **No evidence catalogue.** No single document tells the auditor "here is every piece of evidence we collect, when it is collected, where it lives, who signs it, how long it is retained."
11. **No auditor portal.** No read-only surface where the auditor can pull evidence packs themselves.

---

## NEW SKILLS (9)

| # | Skill | Purpose |
|---|---|---|
| 1 | `ai-agent-soc2-controls` | SOC 2 TSC mapping for agents (Security, Availability, Confidentiality, Processing Integrity, Privacy); per-control implementation pattern + automated-evidence collector + sampling cadence. |
| 2 | `ai-agent-iso27001-controls` | ISO 27001 Annex A controls relevant to agents (A.5 policies, A.8 asset management for tools/prompts/models, A.12 operations, A.14 secure development for prompts, A.16 incident management, A.18 compliance); per-control implementation + evidence. |
| 3 | `ai-agent-hipaa-security-controls` | HIPAA Security Rule (164.306–.318) for agents handling PHI; access controls, audit controls, integrity controls, transmission security, contingency planning; admin-only constraint for clinical PHI agents; BAA implications when LLM provider is in the loop. |
| 4 | `ai-agent-audit-log-integrity` | Write-once / hash-chained action audit log; tamper-evident storage; retention by event class (7yr financial, 6yr HIPAA, configurable for SOC 2); integrity verification job; export-on-audit-request. |
| 5 | `ai-agent-evidence-automation` | Automated evidence collection pipelines for each compliance control; cron / triggered exporters; evidence catalogue; evidence-pack format; tie to incident evidence capture; auditor portal. |
| 6 | `ai-agent-control-testing-and-attestation` | Automated control tests on cadence; failure → ticket; auditor-friendly reports; attestation evidence packs (SOC 2 Type II window, ISO surveillance audit, HIPAA periodic review). |
| 7 | `ai-agent-approval-audit-completeness` | Proving every irreversible action had documented approval; completeness check / gap detection; approval-evidence cross-link to action-audit-log; evidence pack for SOC 2 Processing Integrity. |
| 8 | `ai-agent-drill-evidence-and-cadence` | Automated capture of kill-switch drills, red-team drills, eval-drift drills as compliance evidence; minimum cadence enforcement; pass/fail recording; cross-link to incident drill skill. |
| 9 | `ai-agent-memory-erasure-proof` | Proving GDPR / CCPA / POPIA / KE DPA erasure was complete for agent memory; 9-step cascade verification job emits signed-off evidence; cross-link to agent-memory skill. |

---

## SKILLS ENHANCED (12)

| Skill | Enhancement |
|---|---|
| `ai-agent-runtime-architecture` | Add compliance-evidence emissions to state machine (every transition emits a compliance event). |
| `ai-agent-tool-catalogue-and-action-gating` | Every tool registration emits compliance-relevant metadata (data classification, PHI flag, BAA-scoped, reversibility, retention class). |
| `ai-agent-action-approval-and-hitl` | Approval event is a compliance evidence point; emits signed event into audit log integrity stream. |
| `ai-agent-memory` | Cross-link to memory-erasure-proof; retention policy per memory tier under each regime (SOC 2 / ISO 27001 / HIPAA). |
| `ai-agent-observability-and-replay` | Replay availability measured monthly and exported as evidence (SOC 2 Availability + Processing Integrity). |
| `ai-agent-safety-and-red-team` | Red-team test results exported as quarterly evidence packs. |
| `ai-agent-eval` | Eval coverage exported as monthly evidence (golden coverage %, drift, pass rate). |
| `ai-incident-evidence-capture` | Generalise the evidence-bundle pipeline to a compliance-evidence superset (incident is one trigger; cadence is the other). |
| `ai-incident-drill-and-game-day` | Drills emit compliance evidence packs; cadence enforced at platform level. |
| `saas-tenant-data-portability-and-erasure` | Reference agent-erasure-proof; emit signed proof artefacts. |
| `saas-admin-backoffice-tooling` | Compliance console (run evidence collection, view control status, run integrity verification). |
| `saas-control-plane-engineering` | Audit log spine now includes hash-chain spec and retention by event class. |

---

## REFERENCE FILES (rich, with code)

| Path | Purpose |
|---|---|
| `ai-agent-soc2-controls/references/trust-criteria-mapping.md` | Full SOC 2 TSC → agent control mapping table. |
| `ai-agent-soc2-controls/references/automated-evidence-collectors.md` | Per-control collector code (Python). |
| `ai-agent-iso27001-controls/references/annex-a-mapping.md` | ISO 27001 Annex A → agent implementation table. |
| `ai-agent-iso27001-controls/references/evidence-collection-pipelines.md` | Pipelines per Annex A control. |
| `ai-agent-hipaa-security-controls/references/security-rule-mapping.md` | §164.306–.318 → agent implementation table. |
| `ai-agent-hipaa-security-controls/references/phi-agent-constraints.md` | Admin-only constraint, BAA-scoped tool flags, allowed model providers. |
| `ai-agent-hipaa-security-controls/references/baa-implications.md` | BAA decision tree for LLM provider selection. |
| `ai-agent-audit-log-integrity/references/hash-chain-design.md` | Hash-chained audit log schema + verification code. |
| `ai-agent-audit-log-integrity/references/retention-policies.md` | Retention by event class across SOC 2 / HIPAA / GDPR / financial. |
| `ai-agent-audit-log-integrity/references/integrity-verification-job.md` | Nightly integrity verification job code. |
| `ai-agent-evidence-automation/references/evidence-catalogue.md` | The full evidence catalogue (one row per evidence type). |
| `ai-agent-evidence-automation/references/evidence-pack-format.md` | Pack format (tar.gz + manifest + signature). |
| `ai-agent-evidence-automation/references/auditor-portal-design.md` | Read-only auditor portal API + UI spec. |
| `ai-agent-control-testing-and-attestation/references/control-test-suite.md` | Automated control test code. |
| `ai-agent-control-testing-and-attestation/references/attestation-evidence-pack.md` | SOC 2 Type II / ISO surveillance / HIPAA periodic review pack format. |
| `ai-agent-approval-audit-completeness/references/gap-detection-job.md` | Gap-detection job code (every irreversible action has an approval). |
| `ai-agent-approval-audit-completeness/references/completeness-evidence.md` | Evidence pack format for SOC 2 Processing Integrity. |
| `ai-agent-drill-evidence-and-cadence/references/drill-evidence-capture.md` | Drill evidence capture pipeline. |
| `ai-agent-drill-evidence-and-cadence/references/cadence-enforcement.md` | Cadence enforcement (overdue drill → page on-call). |
| `ai-agent-memory-erasure-proof/references/erasure-verification-job.md` | 9-step cascade verification job code. |

---

## Cross-Engine Handoff (paired with SRS engine)

This engine produces the **engineering / tooling / automated-evidence** side; the SRS engine produces the **policy / control-mapping / attestation-package documents** that an auditor reads.

- **SRS deliverables (paired session):** Information Security Policy, Acceptable Use, Access Control Policy, Cryptography Policy, Operations Security Policy, Supplier Security Policy, Incident Management Policy, Business Continuity Policy, Data Protection Policy + DPIA, HIPAA Security Risk Analysis, SOC 2 System Description, SOC 2 control narratives + mapping matrix, ISO 27001 SoA + risk register + treatment plan, HIPAA Risk Management Plan, BAA template, Subprocessor list.
- **This engine deliverables (this session):** hash-chained audit log code, gap-detection job, automated evidence collectors, integrity verification job, drill evidence pipeline, memory-erasure verification job, auditor portal API, compliance console UI spec, control test suite, attestation evidence pack builder.
- **Handoff:** SRS policies cite the engineering artefacts here as evidence; the auditor reads the policy + opens the evidence pack and verifies the implementation matches. Policy without engineering is hand-waving; engineering without policy fails the auditor's "show me your documented program" question.

---

## Critical Gaps Beyond This Session

1. **EU AI Act high-risk classification overlap.** Agent classes used in employment, credit scoring, education, law enforcement, critical infrastructure require Article 9 (risk management), Article 10 (data governance), Article 12 (record-keeping), Article 13 (transparency), Article 14 (human oversight), Article 15 (accuracy, robustness, cybersecurity) — a separate engineering session.
2. **PCI-DSS for agents touching cardholder data.** Treat as out-of-scope: do not let agents touch PAN; document the constraint.
3. **FedRAMP / StateRAMP for US public sector.** Separate session.
4. **Sector-specific (FINRA / SEC / OSC for financial; FDA for medical SaMD).** Separate session.
5. **Internal compliance vs external attestation roles.** Who in the org owns each control? RACI matrix is in the SRS engine.

---

## Recommended Next Sessions

1. **EU AI Act high-risk engineering** — Article 9/10/12/13/14/15 implementation for agent classes (paired with SRS for Article 11 technical documentation, Article 17 quality management system, Article 18 record-keeping, Article 73 incident reporting).
2. **Agent-vendor due diligence** — auto-evaluating LLM provider SOC 2 / ISO / HIPAA / BAA / data residency at procurement time; subprocessor monitoring.
3. **Continuous compliance monitoring** — drift between declared controls and observed implementation; auto-alert when a tool ships without a compliance metadata.
4. **Customer-facing trust portal** — public surface (trust.example.com) listing SOC 2 / ISO / HIPAA status, last attestation date, evidence available under NDA.
5. **Regulator notification automation** — connecting incident evidence pipeline to EU AI Act Article 73 serious-incident reporting; GDPR Article 33/34 breach notification; HIPAA breach notification (164.404–.414).
