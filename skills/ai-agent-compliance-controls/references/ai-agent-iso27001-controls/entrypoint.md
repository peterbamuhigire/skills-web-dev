> Consolidated from skills/ai-agent-iso27001-controls/SKILL.md into ai-agent-compliance-controls on 2026-05-13. Load this through skills/ai-agent-compliance-controls/SKILL.md, not as an active skill entrypoint.

# AI Agent ISO 27001 Controls
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Implementing ISO/IEC 27001:2022 Annex A controls for an agentic multi-tenant SaaS.
- Building the agent-specific asset register (prompts, tools, models, vector indices, fine-tunes, agent identities) under A.5.9 / A.8.
- Wiring operations security (A.8.16 monitoring, A.8.32 change management) for agent runtime.
- Wiring secure development practice (A.8.25-.34) for prompts as code artefacts.
- Integrating agent incidents with ISO incident management (A.5.24-.28).

## Do Not Use When

- The task is the **Statement of Applicability (SoA)** or **risk register / risk treatment plan** document — that is the SRS engine.
- The task is SOC 2 trust criteria — `ai-agent-soc2-controls`.
- The task is HIPAA — `ai-agent-hipaa-security-controls`.
- The task is the platform-wide ISMS — general security skills.

## Required Inputs

- Agent runtime, tool catalogue, approval, audit log, kill-switch, eval, replay, memory primitives (companion skills).
- The risk register (SRS engine) — the risks this skill's controls treat.
- The SoA (SRS engine) — declaration of which Annex A controls apply.
- The audit window for ISO surveillance / recertification.

## Workflow

1. Read this `SKILL.md`.
2. Map each agent control to its **Annex A clause** (§1) and the full mapping in `references/annex-a-mapping.md`.
3. Build the **agent asset register** (§2) — prompts, tools, models, indices, agent identities, datasets.
4. Wire **operations security** (§3) — A.8.16 logging and monitoring, A.8.32 change management for prompts / tools / models.
5. Wire **secure development for prompts** (§4) — prompt as code, review, versioning, testing.
6. Wire **incident management** (§5) — link to the AI incident stack with ISO event lifecycle.
7. Wire **compliance and audit** (§6) — A.5.34 privacy, A.5.36 compliance with policies, A.5.37 documented operating procedures.
8. Build **evidence collection pipelines** (§7); code in `references/evidence-collection-pipelines.md`.
9. Apply anti-patterns (§8).

## Quality Standards

- The asset register is complete (zero unregistered prompts in production, zero unregistered tools).
- Every asset has an owner, classification, retention, and review date.
- Every change to a controlled asset (prompt, tool, model pin) has a change record, reviewer, test result, deployment record.
- Incidents flow through the same lifecycle as ISMS-managed incidents; agent incidents do not bypass.
- Evidence is collected on cadence and signed.

## Anti-Patterns

- Prompts as untracked strings in feature code — A.5.9 / A.8.9 asset failure.
- Tool registration that does not record owner — control failure at first surveillance.
- Model pin changed by deploy without a change ticket — A.8.32 failure.
- Agent incidents handled outside the ISMS incident process — A.5.24 / A.5.26 failure.
- SoA declares "all of Annex A applies" with no justification or implementation — auditor disqualifies.

## Outputs

- Agent asset register schema + seed.
- Asset classification rubric.
- Change management procedure for prompts / tools / models.
- ISO incident handoff procedure with the AI incident stack.
- Evidence collection pipelines per Annex A control.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Compliance | Annex A → agent control mapping | Markdown | `docs/compliance/iso27001-annex-a.md` |
| Compliance | Agent asset register | DB + monthly export | `evidence/iso/asset-register-2026-Q2.csv` |
| Compliance | Change records (prompts/tools/models) | Ticket export | `evidence/iso/changes-2026-Q2.csv` |
| Compliance | ISO incident records | Ticket export | `evidence/iso/incidents-2026-Q2.csv` |
| Compliance | Per-control evidence pack | tar.gz + manifest.json + signature | `evidence/iso/A.8.16/2026-Q2/` |

## References

- `references/annex-a-mapping.md` — Full Annex A → agent implementation table.
- `references/evidence-collection-pipelines.md` — Pipelines per Annex A control.
- Companion: `ai-agent-soc2-controls`, `ai-agent-hipaa-security-controls`, `ai-agent-audit-log-integrity`, `ai-agent-evidence-automation`, `ai-agent-runtime-architecture`, `ai-agent-tool-catalogue-and-action-gating`, `ai-incident-evidence-capture`, `saas-control-plane-engineering`.

<!-- dual-compat-end -->

## §1 Annex A → Agent Control (Summary)

ISO/IEC 27001:2022 Annex A has 93 controls in 4 themes: A.5 Organisational, A.6 People, A.7 Physical, A.8 Technological. Most agent-relevant controls land in A.5 (policy / asset management / supplier / incident / compliance) and A.8 (operations / development).

| Annex A | Title | Agent Implementation |
|---|---|---|
| **A.5.9** | Inventory of information and other associated assets | Agent asset register: prompts, tools, models, indices, agent identities, datasets |
| **A.5.12** | Classification of information | Per-tool / per-prompt data classification; PHI flag; PII flag |
| **A.5.13** | Labelling of information | Tool registry classification field; trace span carries data class |
| **A.5.15** | Access control | Per-tenant tool allow-list; per-tool min-role |
| **A.5.18** | Access rights | Quarterly review of agent admin / kill-switch operator roles |
| **A.5.19-.23** | Supplier relationships | LLM provider due-diligence; subprocessor list |
| **A.5.24-.28** | Information security incident management | Link to AI incident stack with ISO event lifecycle |
| **A.5.34** | Privacy and PII protection | Per `ai-agent-memory` + erasure proof |
| **A.5.36** | Compliance with policies | Control test suite |
| **A.5.37** | Documented operating procedures | Agent runbook, incident runbook |
| **A.6.3** | Information security awareness, education, training | Engineer training on the agent stack |
| **A.8.1** | User endpoint devices | Out of scope unless agent runs on endpoint |
| **A.8.2** | Privileged access rights | Back-office kill-switch operator role; reviewer of irreversible approvals |
| **A.8.5** | Secure authentication | SSO/SCIM; MFA on approvers |
| **A.8.9** | Configuration management | Tool registry + prompt registry are configuration baselines |
| **A.8.10** | Information deletion | Memory erasure proof |
| **A.8.12** | Data leakage prevention | Cross-tenant leak test; prompt-injection scanner |
| **A.8.15** | Logging | Hash-chained action audit log |
| **A.8.16** | Monitoring activities | Agent runtime SLO + alerting |
| **A.8.20-.24** | Network security | Tool gateway as network boundary; egress restriction |
| **A.8.25-.34** | Secure development | Prompt as code; review / versioning / testing |
| **A.8.32** | Change management | Tool / prompt / model pin change procedure |

Full table with implementation, evidence, cadence, owner in `references/annex-a-mapping.md`.

## §2 Agent Asset Register

The asset register is the foundation. ISO auditors will sample assets and ask: who owns this prompt, when was it last reviewed, what is its classification, where is the retention recorded.

```sql
CREATE TABLE agent_assets (
  id                BIGINT PRIMARY KEY,
  asset_type        ENUM('prompt','tool','model_pin','index','agent_identity','dataset','adapter') NOT NULL,
  asset_name        VARCHAR(256) NOT NULL,
  asset_version     VARCHAR(64) NOT NULL,
  owner             VARCHAR(128) NOT NULL,
  classification    ENUM('public','internal','confidential','restricted','phi','pci') NOT NULL,
  data_residency    VARCHAR(64),
  retention_class   VARCHAR(32) NOT NULL,
  review_cadence    VARCHAR(32) NOT NULL,        -- e.g. "quarterly"
  last_reviewed_at  DATETIME,
  next_review_due   DATETIME,
  status            ENUM('draft','active','deprecated','retired') NOT NULL,
  baa_scoped        BOOLEAN NOT NULL DEFAULT FALSE,
  notes             TEXT,
  created_at        DATETIME NOT NULL,
  updated_at        DATETIME NOT NULL,
  UNIQUE KEY (asset_type, asset_name, asset_version)
);
```

A nightly job exports the register; an "overdue review" alert pages the owner.

```python
# compliance/asset_register.py
def overdue_reviews(now: datetime) -> list[AgentAsset]:
    return AgentAsset.where("next_review_due < ?", now,
                             status__in=["active"]).all()
```

## §3 Operations Security (A.8.16 + A.8.32)

### A.8.16 monitoring

- Agent runtime SLOs (hallucination, refusal, abstain, cost burn) emit metrics into the platform monitoring stack.
- Alert routing → on-call → AI incident triage tree.
- Monthly monitoring review captured in `evidence/iso/A.8.16/2026-MM.json`.

### A.8.32 change management

A "controlled change" for agents covers:

| Change type | Required record | Reviewer |
|---|---|---|
| Prompt version | Prompt registry change ticket; before/after diff; eval delta; deployment record | AI lead + product |
| Tool version | Tool registry change ticket; reversibility re-classification check; allow-list impact | Eng lead + security |
| Model pin | Model pin change ticket; eval delta; cost delta; provider attestation diff | AI lead + cost ops |
| Index rebuild | Index version ticket; recall test; retrieval-set drift | AI lead |
| Allow-list change | Allow-list change ticket; tenant impact; tier-policy check | Platform eng + commercial |

A monthly export of all controlled changes is the evidence artefact.

## §4 Secure Development for Prompts (A.8.25-.34)

Prompts are code. They get:

- A repository (the prompt registry) with versions.
- A pull-request workflow with two reviewers (AI lead + domain owner).
- A test suite (eval harness golden tests) that runs before deploy.
- A deployment record with environment, who deployed, when, rollback target.
- A code-of-conduct (prompt style, refusal language, citation requirements).

Prompts in feature code (string literals) are an A.8.9 / A.8.25 failure. A monthly grep for `f"You are"` / `"system"` strings in repos catches drift.

## §5 Incident Management Handoff (A.5.24-.28)

The AI incident stack (`ai-incident-detection-and-triage`, `ai-incident-response-runbook`, `ai-incident-evidence-capture`, `ai-incident-postmortem`) is the operational layer. ISO requires:

| ISO clause | Engineering link |
|---|---|
| A.5.24 Planning and preparation | Runbook + drill cadence |
| A.5.25 Assessment and decision on info security events | Severity matrix |
| A.5.26 Response to information security incidents | Runbook + per-class playbook |
| A.5.27 Learning from incidents | Postmortem template; learnings flywheel |
| A.5.28 Collection of evidence | Evidence bundle exporter |

Every agent incident creates an ISO incident record with the same id. Monthly export to `evidence/iso/incidents-2026-MM.csv`.

## §6 Compliance and Audit (A.5.34, A.5.36, A.5.37)

- **A.5.34** Privacy: `ai-agent-memory-erasure-proof` evidence packs.
- **A.5.36** Compliance with policies: control test suite (`ai-agent-control-testing-and-attestation`) monthly run.
- **A.5.37** Documented operating procedures: runbook in `docs/runbooks/agent-*.md`, exported into the evidence pack.

## §7 Evidence Pipelines

See `references/evidence-collection-pipelines.md` for one collector per Annex A control with code and cron schedule.

## §8 Anti-Patterns

- SoA declares all 93 controls apply without justifying coverage. Auditor disqualifies the SoA.
- Asset register is a spreadsheet maintained by one person. First absence breaks the register's accuracy.
- Change records exist for "real code" but not for prompts. Prompts ship without review.
- Agent incidents go to the AI team and the ISMS incident log is parallel — two records of truth.
- Review cadence is "annual" with no overdue alerts. Reviews go un-done.
- Owner field is "the team" — no accountable individual.


