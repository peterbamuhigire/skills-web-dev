---
name: ai-agent-soc2-controls
description: Use when implementing SOC 2 Trust Service Criteria controls for an agentic SaaS — per-criterion (Security / Availability / Confidentiality / Processing Integrity / Privacy) agent-specific control implementation pattern, automated evidence collector, and sampling cadence. Auditor-ready engineering of controls; pair with the SRS engine's SOC 2 narrative + control matrix.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Agent SOC 2 Controls
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Implementing SOC 2 Type II controls for an agentic multi-tenant SaaS — the engineering side that an auditor will sample evidence from during a 6-12 month observation window.
- Deciding **per Trust Service Criterion** (TSC: Security CC, Availability A, Confidentiality C, Processing Integrity PI, Privacy P) which agent control satisfies it and what evidence proves the control operated.
- Wiring **automated evidence collectors** that run on cadence so the auditor pulls evidence from one place, not from ten engineers' DMs.
- Choosing a **sampling cadence** (continuous / daily / weekly / monthly / per-event) per control so the evidence volume matches the audit window.

## Do Not Use When

- The task is writing the **SOC 2 System Description** narrative or control matrix document — that is the SRS engine.
- The task is **ISO 27001** Annex A controls — `ai-agent-iso27001-controls`.
- The task is **HIPAA Security Rule** mapping — `ai-agent-hipaa-security-controls`.
- The task is the **audit log integrity** primitive — `ai-agent-audit-log-integrity` (this skill consumes that primitive).
- The task is the **evidence pack format** mechanics — `ai-agent-evidence-automation` (this skill defines what evidence; that skill defines how it is packaged).

## Required Inputs

- The agent runtime emitting lifecycle events (`ai-agent-runtime-architecture`).
- The tool catalogue with reversibility classification (`ai-agent-tool-catalogue-and-action-gating`).
- The approval state machine (`ai-agent-action-approval-and-hitl`).
- The hash-chained action audit log (`ai-agent-audit-log-integrity`).
- The kill-switch (`ai-agent-safety-and-red-team`, `ai-incident-response-runbook`).
- The replay system (`ai-agent-observability-and-replay`).
- The eval harness (`ai-agent-eval`).
- The drill cadence (`ai-incident-drill-and-game-day`, `ai-agent-drill-evidence-and-cadence`).
- The SOC 2 audit window (start / end dates) and the **System Description** authored by the SRS engine (control narratives, RACI, in-scope systems).

## Workflow

1. Read this `SKILL.md`.
2. Map each agent-specific control to its **Trust Service Criterion** (§1). Use the full table in `references/trust-criteria-mapping.md`.
3. For each control, define the **automated evidence collector** (§2). Code in `references/automated-evidence-collectors.md`.
4. Set the **sampling cadence** per control (§3) — continuous (every event) / daily / weekly / monthly / per-event-with-trigger.
5. Wire each collector into the **evidence pack pipeline** (§4) — calls `ai-agent-evidence-automation` to bundle.
6. Implement **control owner attestation** (§5) — each control has a named human who signs the evidence quarterly.
7. Wire **exception tracking** (§6) — when a control test fails, an exception ticket is opened, tracked to closure, and included in the next pack.
8. Apply anti-patterns (§7).

## Quality Standards

- Every TSC has at least one mapped agent control with an automated evidence collector and a named owner.
- Evidence is produced on a documented cadence; no control depends on a human to remember to export.
- Evidence is **content-addressed and signed**; signatures verifiable independent of the engineer who produced them.
- Exceptions are tracked as tickets with severity, owner, target close date; visible in the compliance console.
- The auditor's question "show me Q2 evidence for CC7.2 (system monitoring)" is answered by **one URL** that returns a signed pack.

## Anti-Patterns

- One giant "SOC 2 binder" PDF assembled manually before audit. Auditor disqualifies — Type II requires evidence from across the window, not a snapshot.
- Control narrative says "we have a kill-switch" but no evidence that it was ever drilled inside the audit window. Auditor scopes it as a finding.
- Evidence stored on engineering laptops or Slack. Chain-of-custody dies.
- Per-event evidence (e.g. every approval) collected but no sampling plan — auditor cannot sample.
- Control with no owner. Findings cannot be closed.
- "Evidence" is a screenshot of a Grafana dashboard with no timestamp / no signature / no underlying log link.

## Outputs

- TSC → agent control mapping (full table).
- Automated evidence collector code per control.
- Cadence schedule (cron expressions per collector).
- Evidence pack manifest schema.
- Control owner table (human + backup).
- Exception register schema.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Compliance | TSC → control mapping | Markdown table | `docs/compliance/soc2-tsc-mapping.md` |
| Compliance | Per-control evidence pack | tar.gz + manifest.json + signature | `evidence/soc2/2026-Q2/CC7.2/` |
| Compliance | Cadence schedule | YAML | `ops/compliance/evidence-cadence.yaml` |
| Compliance | Exception register | DB + monthly export | `evidence/soc2/exceptions/2026-Q2.json` |
| Compliance | Control owner table | Markdown | `docs/compliance/control-owners.md` |

## References

- `references/trust-criteria-mapping.md` — Full TSC → agent control mapping with implementation, evidence, cadence per row.
- `references/automated-evidence-collectors.md` — Python collector code per control with cron schedule.
- Companion: `ai-agent-iso27001-controls`, `ai-agent-hipaa-security-controls`, `ai-agent-audit-log-integrity`, `ai-agent-evidence-automation`, `ai-agent-control-testing-and-attestation`, `ai-agent-approval-audit-completeness`, `ai-agent-drill-evidence-and-cadence`, `ai-incident-evidence-capture`, `saas-control-plane-engineering`, `saas-admin-backoffice-tooling`.

<!-- dual-compat-end -->

## §1 TSC → Agent Control Mapping (Summary)

The five Trust Service Criteria each have agent-specific control implementations. The summary table below is the index; the full mapping with evidence specs is in `references/trust-criteria-mapping.md`.

| TSC | Common Criteria | Agent control(s) | Primary evidence |
|---|---|---|---|
| **Security (CC)** | CC6.1 Logical access, CC6.6 Boundary protection, CC7.2 System monitoring, CC7.3 Anomaly response, CC7.4 Incident response | Per-tenant tool allow-list, per-tool min-role, kill-switch, action audit log, jailbreak detector | Tool registry export, kill-switch drill log, jailbreak event stream |
| **Availability (A)** | A1.1 Capacity, A1.2 Environmental, A1.3 Recovery | Step / wallclock / cost budgets, replay availability, agent runtime SLO | Budget enforcement logs, replay test results, runtime SLO report |
| **Confidentiality (C)** | C1.1 Confidential info identification, C1.2 Disposal | Per-tenant memory isolation, PHI/PII tagging on tools, memory-erasure proof | Cross-tenant leak test report, memory-erasure evidence packs |
| **Processing Integrity (PI)** | PI1.1 System processing complete + accurate + timely + authorised, PI1.2-1.5 Outputs / inputs / processing / re-processing | Approval-audit completeness (every irreversible action ↔ approval), action replay determinism, eval coverage | Gap-detection job output, replay drift report, eval coverage report |
| **Privacy (P)** | P1-P8 Notice, choice, collection, use, retention, disclosure, quality, monitoring | Memory consent capture, memory-erasure proof, retention policy enforcement, subprocessor (LLM provider) list | Consent records, erasure proofs, retention enforcement logs |

## §2 Automated Evidence Collector Pattern

Every control has a **collector** — a function that runs on cadence and produces a signed pack.

```python
# compliance/collectors/base.py
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import json, hashlib

@dataclass
class EvidenceCollector:
    control_id: str          # e.g. "CC7.2"
    name: str
    cadence: str             # cron expression or "per_event"
    owner: str               # email of human accountable
    window_days: int = 90    # default rolling window

    def collect(self, window_end: datetime) -> Path:
        window_start = window_end - timedelta(days=self.window_days)
        artefacts = self.gather(window_start, window_end)
        return self.pack(artefacts, window_start, window_end)

    def gather(self, start: datetime, end: datetime) -> dict:
        raise NotImplementedError

    def pack(self, artefacts: dict, start: datetime, end: datetime) -> Path:
        # Delegate to ai-agent-evidence-automation EvidencePack
        from compliance.evidence_pack import EvidencePack
        pack = EvidencePack(
            control_id=self.control_id,
            window=(start, end),
            owner=self.owner,
        )
        for name, content in artefacts.items():
            pack.add(name, content)
        return pack.sign_and_upload()
```

A concrete collector for CC7.2 (system monitoring) for agents:

```python
# compliance/collectors/cc7_2_agent_monitoring.py
class CC72AgentMonitoringCollector(EvidenceCollector):
    control_id = "CC7.2"
    name = "Agent runtime monitoring and anomaly response"
    cadence = "0 2 * * 1"  # weekly Mon 02:00
    owner = "sre-lead@example.com"
    window_days = 7

    def gather(self, start, end):
        return {
            "agent_task_volume.json": AgentTask.count_by_state(start, end),
            "kill_switch_state.json": KillSwitchRegistry.dump(),
            "anomaly_alerts.jsonl": AlertLog.query(category="agent", start=start, end=end),
            "burn_rate_breaches.jsonl": SLOEngine.breaches("hallucination_slo", start, end),
            "responder_acks.jsonl": IncidentLog.acks_for_agent_alerts(start, end),
            "dashboard_screenshot.png": Grafana.export("agent-runtime", end),
        }
```

See `references/automated-evidence-collectors.md` for the full set (16 controls × collector each).

## §3 Sampling Cadence Per Control

| Cadence | When to use | Example controls |
|---|---|---|
| **Per-event with capture** | Every event is evidence (irreversible actions, approvals, kill-switch flips, erasures) | CC6.1, PI1.1, P5 |
| **Continuous (streaming)** | High-volume signals that the auditor will sample from | CC7.2 monitoring streams, action audit log |
| **Daily** | Lightweight state checks (allow-list snapshot, budget enforcement summary) | CC6.6, A1.1 |
| **Weekly** | Operational reviews (runtime health, replay availability) | CC7.2, A1.3 |
| **Monthly** | Reviews and tests (control test suite, eval coverage) | CC4.1, PI1.5 |
| **Quarterly** | Drills, red-team, attestations | CC7.4, CC9.2, P8 |
| **Per-trigger** | Run on an incident or audit request | CC7.3, A1.3 |

Cadence is recorded as a cron expression in `ops/compliance/evidence-cadence.yaml`:

```yaml
collectors:
  - id: cc7_2_agent_monitoring
    cadence: "0 2 * * 1"      # weekly Mon 02:00
    owner: sre-lead@example.com
    retention_years: 7
  - id: pi1_1_approval_completeness
    cadence: "0 3 1 * *"       # monthly 1st 03:00
    owner: security-lead@example.com
    retention_years: 7
  - id: c1_2_memory_erasure_proof
    cadence: "per_event"
    owner: dpo@example.com
    retention_years: 7
  - id: cc7_4_kill_switch_drill
    cadence: "0 0 1 */3 *"     # quarterly
    owner: sre-lead@example.com
    retention_years: 7
```

## §4 Pipeline Wiring

Every collector pushes its pack to the **evidence vault** via `ai-agent-evidence-automation`. The auditor portal indexes packs by `control_id`, `window_start`, `window_end`. The auditor's URL is:

```
GET /audit/soc2/control/{control_id}?window_start=2026-04-01&window_end=2026-06-30
→ 200 OK
[
  {"pack_id": "evp-cc72-2026-04-01-2026-04-07", "url": "...", "sha256": "...", "signed_by": "..."},
  ...
]
```

## §5 Control Owner Attestation

Quarterly, each control owner signs an attestation that:

1. The control operated for the quarter.
2. Exceptions have been raised for any test failures.
3. The collector has produced the expected packs (cadence honoured).

Signature is over `pack_id` list + manifest sha256. Stored alongside the pack in the vault.

## §6 Exception Tracking

When a control test fails (e.g. an approval gap was found, or a kill-switch drill was missed), an **exception** is opened:

```sql
CREATE TABLE compliance_exceptions (
  id              BIGINT PRIMARY KEY,
  control_id      VARCHAR(32) NOT NULL,
  opened_at       DATETIME NOT NULL,
  severity        ENUM('low','medium','high','critical') NOT NULL,
  title           VARCHAR(256) NOT NULL,
  description     TEXT,
  owner           VARCHAR(128) NOT NULL,
  target_close    DATE NOT NULL,
  status          ENUM('open','mitigating','closed','accepted') NOT NULL,
  closed_at       DATETIME,
  evidence_pack   VARCHAR(256),     -- pack that exposed the gap
  remediation     TEXT
);
```

Open exceptions are included in the quarterly attestation pack. The auditor will scope a finding if exceptions are not closed within target.

## §7 Anti-Patterns

- "We'll assemble the binder before audit." Type II requires evidence from across the entire window, not a year-end snapshot.
- Collector cadence not honoured because the cron job silently failed. Mitigate with a heartbeat check that itself is evidence (CC7.2).
- Per-event collectors that store everything raw with no sampling plan. Auditor cannot scope a 90-day window with 50M events. Sample.
- Control with no owner. Findings have no one to close.
- Evidence pack contains the right data but is not signed. Auditor must accept your word for it — they will not.
- Same engineer who runs the collector also signs the attestation. Segregation of duties failure (CC1.4).
