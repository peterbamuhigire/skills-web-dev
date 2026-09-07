---
name: ai-agent-drill-evidence-and-cadence
description: Use when capturing kill-switch, red-team, and eval-drift drills as audit-ready compliance evidence — minimum-cadence enforcement, pass/fail recording, and cross-link to the incident drill skill. Turns drills from operational exercises into SOC 2 / ISO 27001 / HIPAA evidence rows with signed packs.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Agent Drill Evidence and Cadence

## Operating contract

## Inputs

| Input | Required | Purpose |
|---|---|---|
| Domain evidence | yes | drill type, cadence policy, scenario, participants, target thresholds, and evidence store |

## Outputs

- Produce: drill record, measured results, failed-threshold actions, signed evidence pack, and cadence status.

## Capability and permission boundaries

Default to read-only analysis. Read only scoped records; redact secrets and regulated data. Writes, execution, network calls, production configuration, customer communication, billing changes, and delegation require explicit authority and an identified owner. Never widen tenant, time-window, or system scope implicitly.

## Degraded mode

When required telemetry, evidence, execution, network access, or write authority is unavailable, return a partial result with each unassessed item labelled, preserve the safest existing state, and state the evidence or approval needed to continue. Never convert missing evidence into a pass.

## Decision rules

| Condition | Action |
|---|---|
| Scope, owner, or threshold is missing | Stop the affected decision and request it |
| Evidence is incomplete but read-only analysis is safe | Produce a qualified partial result and gap list |
| A mutation exceeds authority or tenant boundary | Block it and route for approval |
| Evidence meets the stated threshold | Issue the output with provenance and owner |

## Anti-Patterns

- Treating absent evidence as success. Fix: mark the check unassessed and name the missing source.
- Expanding one tenant or workflow to all tenants. Fix: enforce supplied scope at every query and action.
- Performing a production write during analysis. Fix: emit a reviewed change plan until authority is explicit.
- Reporting a metric without population, window, or source. Fix: attach all three.
- Hiding a failed threshold inside an average. Fix: report failure slices and the remediation owner.

Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Operationalising **drill cadence** — kill-switch quarterly, red-team quarterly, eval-drift monthly, restoration test annually — and proving compliance to an auditor that each one happened on schedule with pass/fail evidence.
- Capturing each drill run as a **compliance evidence row** with manifest, raw artefacts, pass/fail, and signed attestation.
- Enforcing **cadence at the platform level** — an overdue drill pages on-call before the auditor finds the gap.
- Cross-linking drills from `ai-incident-drill-and-game-day` into the SOC 2 / ISO 27001 / HIPAA evidence pipeline.

## Do Not Use When

- Designing the drill **scenarios** themselves — that's `ai-incident-drill-and-game-day` and `ai-agent-safety-and-red-team`.
- Writing the **policy** that requires drills — SRS engine (Incident Management Policy, BCP).
- Building the **action audit log** — `ai-agent-audit-log-integrity`.
- Building the **generic evidence collector framework** — `ai-agent-evidence-automation`.

## Required Inputs

- Drill registry (kill-switch, red-team prompt suite, eval-drift baseline, restoration test) with documented expected outcomes per scenario.
- Cadence policy (cron-style minimums per drill class).
- Approver allow-list (who signs pass/fail).
- Hash-chained action audit log to anchor drill events.
- Evidence vault and pack format (`ai-agent-evidence-automation`).

## Workflow

1. Read this `SKILL.md`.
2. Register every drill class with its **minimum cadence** (§1) in `ops/compliance/drill-cadence.yaml`.
3. For each drill run, capture **structured drill evidence** (§2) — start/end timestamps, scenario id, executor, observers, scripted expected outcome, observed outcome, pass/fail, raw artefacts.
4. Sign and pack into `evidence/drills/{drill_class}/{drill_id}/` (§3).
5. Run the **cadence enforcer** (§4) — a daily job that checks every drill class for an overdue run; missed cadence opens an exception and pages on-call.
6. Produce **quarterly drill rollup** (§5) — auditor-friendly digest of all drills in the quarter with pass rate and exceptions.
7. Apply anti-patterns (§6).

## Quality Standards

- Every drill class has a **documented minimum cadence** and a **named owner** (control owner from `ai-agent-soc2-controls`).
- Every drill run produces a **signed evidence pack** (cannot be edited after the fact).
- Pass/fail is **observably testable**, not subjective — the scenario has a scripted expected outcome and the evidence pack proves it.
- Cadence is enforced **at the platform**; not on a wiki calendar.
- Missed cadence is itself a **compliance exception**, opened automatically.
- Drill records cross-reference the action audit log chain positions where the drill produced events.

## Anti-Patterns

- Drill happened on Slack with a screenshot and a "we did it" note. Auditor disqualifies.
- Cadence tracked on a wiki page or a Notion calendar that nobody owns.
- "Drill passed" because nothing exploded; no pass criterion was defined.
- Kill-switch drilled by flipping a feature flag without proving agent traffic actually halted within the documented MTTH (mean time to halt) target.
- Red-team drills only on the prod agent; safety regressions in pre-prod are noise; both need evidence rows.
- Eval-drift drill replaced by the regular CI eval run; no scheduled, owner-attested drift exercise.

## Outputs

- `ops/compliance/drill-cadence.yaml` — cadence policy.
- Drill evidence schema (`drill_runs` table) + signed packs.
- Cadence enforcer cron + pager wiring.
- Quarterly drill rollup pack.
- Auditor portal endpoint per drill class.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Operability | Drill run record | Row + signed pack | `evidence/drills/kill_switch/2026-Q2-W3/` |
| Operability | Cadence policy | YAML | `ops/compliance/drill-cadence.yaml` |
| Operability | Quarterly drill rollup | tar.gz | `evidence/drills/rollup/2026-Q2.tar.gz` |
| Operability | Cadence enforcer heartbeat | JSON | `evidence/drills/enforcer-heartbeat.jsonl` |
| Operability | Drill exceptions | Row | `compliance_exceptions WHERE control_id IN ('CC7.4','CC9.2')` |

## References

- `references/drill-evidence-capture.md` — Full capture pipeline (Python) for kill-switch / red-team / eval-drift drills.
- `references/cadence-enforcement.md` — Cadence policy schema, enforcer code, paging wiring.
- Companions: `ai-incident-drill-and-game-day` (scenarios), `ai-agent-safety-and-red-team` (red-team suite), `ai-agent-eval` (eval drift), `ai-agent-soc2-controls` (CC7.4, CC9.2), `ai-agent-iso27001-controls` (A.16.1.6, A.17.1.3), `ai-agent-evidence-automation` (pack pipeline).

<!-- dual-compat-end -->

## §1 Cadence Policy

```yaml
# ops/compliance/drill-cadence.yaml
drills:
  - id: kill_switch_global
    description: Global agent kill-switch halts all in-flight tasks within MTTH target.
    min_cadence_days: 90        # quarterly
    mtth_target_seconds: 30
    owner: sre-lead@example.com
    control_ids: [CC7.4, A.16.1.5]
    scenarios: [kill_switch_global_drill]

  - id: kill_switch_per_tenant
    description: Tenant-scoped kill-switch halts only target tenant's traffic.
    min_cadence_days: 90
    mtth_target_seconds: 30
    owner: sre-lead@example.com
    control_ids: [CC7.4, C1.1]
    scenarios: [kill_switch_tenant_drill]

  - id: red_team_prompt_injection
    description: Adversarial prompt suite run against current agent build.
    min_cadence_days: 90
    pass_threshold: 0.95         # ≥95% scenarios blocked
    owner: security-lead@example.com
    control_ids: [CC7.3, CC9.1]
    scenarios: [redteam-2026-q1, redteam-jailbreak, redteam-data-exfil]

  - id: eval_drift_baseline
    description: Production eval suite re-run against frozen golden set; drift alarms.
    min_cadence_days: 30
    drift_alarm_pp: 2.0          # ≥2pp pass-rate drop = fail
    owner: ml-lead@example.com
    control_ids: [PI1.5]
    scenarios: [eval-golden-100]

  - id: restoration_test
    description: Restore audit log from immutable storage; verify chain integrity.
    min_cadence_days: 365
    owner: sre-lead@example.com
    control_ids: [A1.3, A.17.1.2]
    scenarios: [restore_audit_log]

  - id: incident_response_tabletop
    description: Tabletop exercise of the agent incident runbook with on-call.
    min_cadence_days: 180        # semi-annual
    owner: incident-commander@example.com
    control_ids: [CC7.4, A.16.1.5]
    scenarios: [tabletop-data-exfil, tabletop-hallucinated-action]
```

The enforcer reads this file; any new drill class adds a row and the cadence is binding.

## §2 Drill Evidence Capture

Each drill run produces a structured record:

```python
# compliance/drills/capture.py
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
import json, hashlib, uuid

@dataclass
class DrillRun:
    drill_id: str
    scenario_id: str
    run_id: str = field(default_factory=lambda: f"drill_{uuid.uuid4().hex[:12]}")
    started_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    executor: str = ""               # human who executed
    observers: list[str] = field(default_factory=list)
    expected_outcome: dict = field(default_factory=dict)
    observed_outcome: dict = field(default_factory=dict)
    raw_artefacts: dict = field(default_factory=dict)  # name -> path/URI
    audit_chain_positions: list[int] = field(default_factory=list)
    result: str = "running"          # running / pass / fail / aborted
    notes: str = ""
    attestation_signature: Optional[str] = None

    def score(self) -> str:
        # Plug in drill-specific pass criteria
        return ScoringRegistry.score(self.drill_id, self)
```

A kill-switch drill example end-to-end:

```python
# compliance/drills/kill_switch.py
from compliance.drills.capture import DrillRun
from runtime.kill_switch import flip_global, observe_in_flight
from audit.chain import record_drill_event

def run_kill_switch_global_drill(executor: str, observers: list[str]) -> DrillRun:
    run = DrillRun(
        drill_id="kill_switch_global",
        scenario_id="kill_switch_global_drill",
        executor=executor,
        observers=observers,
        expected_outcome={"mtth_seconds_max": 30, "in_flight_after_30s": 0},
    )
    record_drill_event(run.run_id, "started", run.expected_outcome)

    in_flight_before = observe_in_flight()
    t0 = datetime.utcnow()
    flip_global(reason=f"drill:{run.run_id}", actor=executor)
    halted_at, in_flight_after = wait_for_halt(timeout_seconds=60)
    t1 = datetime.utcnow()

    run.ended_at = t1
    run.observed_outcome = {
        "mtth_seconds": (halted_at - t0).total_seconds(),
        "in_flight_before": in_flight_before,
        "in_flight_after_30s": in_flight_after,
    }
    run.audit_chain_positions = record_drill_event(run.run_id, "completed", run.observed_outcome)
    run.result = run.score()      # pass if mtth ≤ 30 and in_flight_after_30s == 0
    flip_global(reason=f"drill:{run.run_id}:restore", actor=executor, on=False)

    pack_path = pack_and_sign(run)
    return run
```

`pack_and_sign` writes the evidence pack:

```python
# compliance/drills/pack.py
def pack_and_sign(run: DrillRun) -> str:
    base = f"evidence/drills/{run.drill_id}/{run.run_id}/"
    files = {
        "record.json": asdict(run),
        "observed_outcome.json": run.observed_outcome,
        "expected_outcome.json": run.expected_outcome,
        "audit_chain_witness.json": chain_witness_for(run.audit_chain_positions),
        "kill_switch_metric_export.csv": metrics_export(run.started_at, run.ended_at),
    }
    manifest = build_manifest(run, files)
    sig = sign_manifest(manifest, owner=owner_for_drill(run.drill_id))
    vault.upload(base, files, manifest, sig)
    return base
```

Full code (red-team and eval-drift variants) in `references/drill-evidence-capture.md`.

## §3 Pack Format

```
evidence/drills/{drill_id}/{run_id}/
├── manifest.json
├── record.json                   # the DrillRun structure
├── expected_outcome.json
├── observed_outcome.json
├── audit_chain_witness.json      # chain positions emitted during drill
├── raw_artefacts/                # per-drill (metric dumps, redteam transcripts, eval scores)
├── attestation.txt
└── signature.sig
```

## §4 Cadence Enforcer

```python
# compliance/drills/enforcer.py
import yaml
from datetime import datetime, timedelta

def enforce(now: datetime):
    policy = yaml.safe_load(open("ops/compliance/drill-cadence.yaml"))
    for drill in policy["drills"]:
        last = last_passed_run(drill["id"])
        if last is None:
            _overdue(drill, reason="never_run", since=None)
            continue
        delta = (now - last.ended_at).days
        if delta > drill["min_cadence_days"]:
            _overdue(drill, reason="overdue", since=last.ended_at)
        elif delta > drill["min_cadence_days"] * 0.8:
            _warn(drill, days_remaining=drill["min_cadence_days"] - delta)

def _overdue(drill, reason, since):
    open_exception(
        control_id=drill["control_ids"][0],
        severity="high",
        title=f"Drill {drill['id']} overdue ({reason})",
        evidence_ref=f"drills/cadence/{drill['id']}",
        detail={"last": since.isoformat() if since else None,
                "min_cadence_days": drill["min_cadence_days"],
                "owner": drill["owner"]},
    )
    page_on_call(drill["owner"], f"Drill {drill['id']} overdue: {reason}")
```

Schedule:

```yaml
- id: drill_cadence_enforcer
  cadence: "0 6 * * *"  # daily 06:00 UTC
  owner: sre-lead@example.com
  entrypoint: python -m compliance.drills.enforcer
```

Full enforcer with grace periods, alert dedup, and owner escalation in `references/cadence-enforcement.md`.

## §5 Quarterly Drill Rollup

At quarter end, a rollup pack consolidates all drill runs:

```
evidence/drills/rollup/2026-Q2/
├── manifest.json
├── rollup-report.json    # totals per drill_id, pass rate, exceptions opened/closed
├── runs.jsonl            # one row per drill run in the quarter
├── exceptions.jsonl      # cadence + result exceptions
├── attestation.txt       # signed by each drill owner
└── signature.sig
```

The auditor URL:

```
GET /audit/drills/rollup?from=2026-04-01&to=2026-06-30
```

## §6 Anti-Patterns

- "We ran the drill" with no signed record. Cannot withstand a Type II auditor; reclassified as no-drill.
- Cadence on a wiki rather than a cron + paging chain. Inevitable miss.
- Pass criterion not defined before the drill. Result is decided post-hoc; the auditor will discount it.
- Kill-switch drill flips the toggle but does not measure MTTH. The metric was the whole point.
- Red-team drill scored on whether the team enjoyed it. Use the pass-threshold (e.g. ≥95% scenarios blocked) from the cadence policy.
- Drill record contains PHI / customer data unredacted. Pack must respect data classification.
