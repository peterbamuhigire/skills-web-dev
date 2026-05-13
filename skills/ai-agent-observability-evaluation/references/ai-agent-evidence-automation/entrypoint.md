> Consolidated from skills/ai-agent-evidence-automation/SKILL.md into ai-agent-observability-evaluation on 2026-05-13. Load this through skills/ai-agent-observability-evaluation/SKILL.md, not as an active skill entrypoint.

# AI Agent Evidence Automation
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Building the evidence collection plumbing that the SOC 2 / ISO 27001 / HIPAA control skills consume.
- Defining the **evidence catalogue** — one row per evidence type the platform produces.
- Defining the **evidence pack format** — tar.gz + manifest + signature.
- Building the **auditor portal** — read-only surface where the auditor pulls packs themselves.
- Wiring the existing incident evidence exporter as a special case of the broader compliance pipeline.

## Do Not Use When

- The task is defining **which** controls to satisfy — that is SOC 2 / ISO / HIPAA skills.
- The task is the **integrity** of the audit log itself — `ai-agent-audit-log-integrity`.
- The task is the **incident bundle** specifically — `ai-incident-evidence-capture` (this skill generalises it).
- The task is the **compliance console UI** internal to back-office — `saas-admin-backoffice-tooling`.

## Required Inputs

- Per-control collector code (from SOC 2 / ISO / HIPAA skills).
- HSM-backed signing key.
- Object-lock evidence vault.
- Auditor identity store (separate from staff IdP — auditors are external).
- The audit window calendar (when audits run, which control × window is needed).

## Workflow

1. Read this `SKILL.md`.
2. Define the **evidence catalogue** (§1). See `references/evidence-catalogue.md`.
3. Define the **evidence pack format** (§2). See `references/evidence-pack-format.md`.
4. Build the **scheduler** (§3) that runs collectors on cadence.
5. Build the **trigger** path (§4) — incident, audit request, control failure.
6. Build the **auditor portal** (§5). See `references/auditor-portal-design.md`.
7. Wire **retention** of packs themselves (§6) — packs live in the evidence vault under the longest applicable retention.
8. Apply anti-patterns (§7).

## Quality Standards

- Every collector either runs successfully or pages on failure. Silent miss is forbidden.
- Pack manifest is content-addressed (sha256 over contents) and signed with the platform evidence key.
- Auditor portal returns a one-URL view per control × window; no auditor needs to call the on-call engineer.
- The portal is **read-only** to auditors; they cannot trigger evidence regeneration after the fact.
- Packs are immutable once signed. Re-running a collector produces a **new** pack; the old one is preserved.

## Anti-Patterns

- Manual screenshot-and-zip the night before audit. Type II disqualifies; ISO surveillance scopes as a finding.
- Packs without a manifest. Auditor cannot validate contents.
- Signature stored separately from pack in a different bucket without retention. Pack outlives signature.
- Auditor portal that pulls from production live. Auditor traffic can spike production load.
- Re-generating packs to "fix" a finding. Tampering with evidence; auditor disqualifies the program.
- Single shared auditor login. No per-auditor audit trail.
- Compliance console that lets a single operator delete a pack. Pack must outlive the operator.

## Outputs

- Evidence catalogue document.
- Evidence pack format + manifest schema + signature spec.
- Collector scheduler service.
- Trigger-driven collection path.
- Auditor portal API + UI spec.
- Retention enforcement on packs.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Compliance | Evidence catalogue | Markdown | `docs/compliance/evidence-catalogue.md` |
| Compliance | Pack manifest schema | JSON Schema | `schemas/evidence-pack-manifest.schema.json` |
| Compliance | Auditor portal API spec | OpenAPI | `docs/compliance/auditor-portal-api.yaml` |
| Compliance | Auditor portal access log | Append-only | `evidence/portal/access-YYYY-MM.jsonl` |
| Compliance | Collector run log | DB + monthly export | `evidence/collector/runs-YYYY-MM.csv` |

## References

- `references/evidence-catalogue.md` — Full evidence catalogue.
- `references/evidence-pack-format.md` — Pack tar.gz + manifest + signature spec.
- `references/auditor-portal-design.md` — Portal API + UI + access control.
- Companion: `ai-agent-soc2-controls`, `ai-agent-iso27001-controls`, `ai-agent-hipaa-security-controls`, `ai-agent-audit-log-integrity`, `ai-agent-control-testing-and-attestation`, `ai-incident-evidence-capture`, `saas-admin-backoffice-tooling`.

<!-- dual-compat-end -->

## §1 Evidence Catalogue (Summary)

One row per evidence type: who consumes it (which control), how it is produced, where it lives, how long it is retained, who owns it. Full catalogue in `references/evidence-catalogue.md`.

| Evidence | Producer | Cadence | Retention | Owner |
|---|---|---|---|---|
| Action audit log integrity report | Verifier daemon | Daily | 7y | Platform eng |
| Tool registry snapshot | Allowlist collector | Daily | 3y | Platform eng |
| Kill-switch drill record | Drill harness | Per drill (quarterly min) | 7y | SRE |
| Resumability drill record | Drill harness | Quarterly | 7y | SRE |
| Replay availability test | Replay collector | Monthly | 7y | SRE |
| Eval coverage report | Eval harness | Monthly | 3y | AI lead |
| Approval-completeness gap report | Gap detector | Monthly | 7y | Security |
| Memory erasure proof | Erasure verifier | Per event | 7y | DPO |
| PHI access log slice | HIPAA collector | Monthly | 6y | HIPAA Security Officer |
| Subprocessor pack | Vendor collector | Quarterly | 7y | Compliance lead |
| Workforce training record | HR system export | Semi-annual | 7y | HR + CISO |
| Access review sign-off | Quarterly review | Quarterly | 7y | CISO |
| Incident evidence bundle | Incident exporter | Per incident | 7-10y | SRE |
| Postmortem record | Postmortem template | Per incident | 7y | SRE |

## §2 Evidence Pack Format

Each pack is a tar.gz with a strict structure:

```
evp-{control_id}-{start}-{end}.tar.gz
├── manifest.json                       # canonical metadata
├── manifest.signature                  # detached HSM signature over manifest.json
├── public-key.pem                      # platform verification key
├── artefacts/                          # the collected evidence
│   ├── {artefact-1}.json
│   ├── {artefact-2}.jsonl
│   ├── {artefact-3}.csv
│   └── ...
├── verify.py                           # auditor-runnable offline verification
└── README.md                           # contents + verification instructions
```

Manifest schema in `references/evidence-pack-format.md`. The signature is over the manifest only; the manifest contains sha256 of every artefact file, so verifying the manifest verifies the pack.

## §3 Scheduler

```python
# compliance/scheduler.py
from datetime import datetime
from croniter import croniter

class EvidenceScheduler:
    def __init__(self, collectors: list[EvidenceCollector]):
        self.collectors = collectors

    def tick(self, now: datetime):
        for c in self.collectors:
            if c.cadence == "per_event":
                continue                # event-triggered elsewhere
            schedule = croniter(c.cadence, c.last_run or epoch())
            next_run = schedule.get_next(datetime)
            if next_run <= now:
                self._run(c, now)

    def _run(self, c: EvidenceCollector, now: datetime):
        try:
            pack_url = c.collect(now)
            CollectorRunLog.record(c.control_id, "ok", pack_url, now)
            MetricsClient.incr("compliance.collector.success",
                                tags={"control": c.control_id})
        except Exception as e:
            CollectorRunLog.record(c.control_id, "fail", str(e), now)
            MetricsClient.incr("compliance.collector.failure",
                                tags={"control": c.control_id})
            AlertManager.page(
                severity="high",
                title=f"Compliance collector failed: {c.control_id}",
                error=str(e),
                runbook="docs/runbooks/collector-failure.md")
```

The scheduler itself emits a heartbeat metric; an alert fires if no tick happens for 1 hour (`compliance.scheduler.heartbeat` stale).

## §4 Triggered Collection

Some collectors run on event triggers, not cadence:

| Trigger | Collector | Purpose |
|---|---|---|
| `incident.opened` | Incident evidence exporter | Bundle per `ai-incident-evidence-capture` |
| `erasure.requested` | Memory erasure verifier | Per-event proof |
| `control.test.failed` | Control test pack | Capture failure state |
| `audit.window.opened` | Attestation pack builder | Bundle for the audit window |
| `subprocessor.changed` | Vendor pack | Updated subprocessor list + notification |
| `phi.breach.suspected` | HIPAA breach evidence pack | Breach evidence frozen |

```python
# compliance/trigger_bus.py
class TriggerBus:
    HANDLERS = {
        "incident.opened":          IncidentEvidenceCollector,
        "erasure.requested":         MemoryErasureProofCollector,
        "control.test.failed":       ControlTestFailurePack,
        "audit.window.opened":       AttestationPackBuilder,
        "subprocessor.changed":      VendorPackCollector,
        "phi.breach.suspected":      HIPAABreachPackCollector,
    }

    @classmethod
    def emit(cls, trigger: str, **payload):
        handler = cls.HANDLERS.get(trigger)
        if not handler:
            return
        return handler().collect_for_trigger(payload)
```

## §5 Auditor Portal

Read-only surface for the auditor. Full design in `references/auditor-portal-design.md`. Summary:

```
GET  /audit/v1/controls                              # list all controls + latest pack per window
GET  /audit/v1/controls/{control_id}                 # control narrative + history
GET  /audit/v1/controls/{control_id}/packs?window=   # packs filtered by window
GET  /audit/v1/packs/{pack_id}                       # pack metadata + signed download URL
GET  /audit/v1/packs/{pack_id}/download              # one-time signed URL to the pack
GET  /audit/v1/attestations                          # quarterly attestation packs
GET  /audit/v1/incidents                             # incident records + bundle refs
GET  /audit/v1/access-log/me                         # auditor's own access history
```

Auditor identity is a separate IdP role (`role:external_auditor`). Access is scoped by audit engagement: an auditor for engagement E sees only the controls in scope for E and only the windows of E.

Every fetch writes an entry to `evidence/portal/access-YYYY-MM.jsonl`.

## §6 Pack Retention

Packs live in the evidence vault under the **longest applicable retention** of their constituent evidence. Defaults:

| Pack type | Retention |
|---|---|
| Incident bundle (high-risk AI) | 10 years |
| Incident bundle (default) | 7 years |
| Memory erasure proof | 7 years |
| HIPAA evidence | 6 years |
| SOC 2 / ISO routine | 7 years |
| Attestation pack | 10 years |

Packs do not move between retention tiers; they keep their original retention permanently. Object-lock at write time.

## §7 Anti-Patterns

- Pack with no manifest. Contents can be silently dropped.
- Re-signing a pack after editing contents. Evidence tampering; auditor disqualifies.
- Auditor portal that allows download but no access log. Cannot prove who pulled what.
- Single signing key, no rotation policy. Compromise of key invalidates entire history.
- Collector failure raises in Slack, not in metrics + page. Silent failures pile up before audit.
- Packs stored on engineering laptops "for convenience". Out of chain-of-custody.
- Manual re-creation of last quarter's pack "because the original got lost". Auditor reads the regeneration timestamp and disqualifies.


