# Automated Evidence Collectors

Per-control Python collector implementations. Each collector inherits from `EvidenceCollector` in `compliance/collectors/base.py` (see `SKILL.md` §2).

All collectors:
1. Pull data from a defined source.
2. Apply redaction by data classification.
3. Bundle into an `EvidencePack`.
4. Sign with the production evidence key (HSM-backed).
5. Upload to the evidence vault (object-lock storage).
6. Index the pack in the auditor portal.

---

## CC6.1 — Per-tenant tool allow-list snapshot

```python
# compliance/collectors/cc6_1_allowlist.py
from compliance.collectors.base import EvidenceCollector

class CC61AllowlistCollector(EvidenceCollector):
    control_id = "CC6.1"
    name = "Per-tenant tool allow-list and per-tool min-role"
    cadence = "0 1 * * *"            # daily 01:00
    owner = "platform-eng@example.com"
    window_days = 1

    def gather(self, start, end):
        from registry import ToolRegistry, TenantRegistry, RoleRegistry
        rows = []
        for tenant in TenantRegistry.active(end):
            for tool in ToolRegistry.tools_for_tenant(tenant.id, end):
                rows.append({
                    "tenant_id": tenant.id,
                    "tenant_tier": tenant.tier,
                    "tool_name": tool.name,
                    "tool_version": tool.version,
                    "reversibility": tool.reversibility,
                    "min_role": tool.min_role,
                    "data_classification": tool.data_classification,
                    "phi_flag": tool.phi_flag,
                    "baa_scoped": tool.baa_scoped,
                })
        diff = ToolRegistry.diff_since(start, end)
        return {
            "allowlist.jsonl": rows,
            "diff_24h.jsonl": diff,
            "tenant_count.json": {"active": len(rows)},
        }
```

---

## CC6.6 — Boundary protection (agent runtime isolation)

```python
# compliance/collectors/cc6_6_boundary.py
class CC66BoundaryCollector(EvidenceCollector):
    control_id = "CC6.6"
    name = "Agent runtime isolation and tool-gateway enforcement"
    cadence = "0 2 * * 1"            # weekly Mon 02:00
    owner = "platform-eng@example.com"
    window_days = 7

    def gather(self, start, end):
        from infra import DeploymentTopology
        from gateway import ToolGateway
        return {
            "topology.json": DeploymentTopology.snapshot(end),
            "gateway_enforcement_log.jsonl":
                ToolGateway.enforcement_events(start, end),
            "denied_calls.jsonl":
                ToolGateway.denied_calls(start, end),
            "isolation_test_run.json":
                run_synthetic_cross_tenant_test(),  # weekly test
        }
```

---

## CC7.2 — Agent runtime monitoring

```python
# compliance/collectors/cc7_2_monitoring.py
class CC72MonitoringCollector(EvidenceCollector):
    control_id = "CC7.2"
    name = "Agent runtime monitoring and anomaly response"
    cadence = "0 2 * * 1"
    owner = "sre-lead@example.com"
    window_days = 7

    def gather(self, start, end):
        from runtime import AgentTask
        from slo import SLOEngine
        from alerts import AlertLog
        return {
            "task_volume_by_state.json":
                AgentTask.count_by_state(start, end),
            "slo_burn_rates.jsonl":
                SLOEngine.burn_rates(["hallucination", "refusal", "abstain"],
                                     start, end),
            "burn_rate_breaches.jsonl":
                SLOEngine.breaches(start, end),
            "alerts.jsonl":
                AlertLog.query(category="agent", start=start, end=end),
            "alert_ack_times.json":
                AlertLog.ack_time_distribution(start, end),
            "dashboard_screenshot.png":
                Grafana.export("agent-runtime-overview", end),
        }
```

---

## CC7.4 — Kill-switch drill evidence

```python
# compliance/collectors/cc7_4_kill_switch_drill.py
class CC74KillSwitchDrillCollector(EvidenceCollector):
    control_id = "CC7.4"
    name = "Kill-switch drill quarterly evidence"
    cadence = "per_event_with_quarterly_check"
    owner = "sre-lead@example.com"
    window_days = 90

    def gather(self, start, end):
        from drills import DrillLog
        from cadence import CadenceEnforcer
        drills = DrillLog.query(scenario="kill_switch", start=start, end=end)
        cadence_check = CadenceEnforcer.check("kill_switch_drill", end)
        return {
            "drills_in_window.jsonl": [d.to_evidence() for d in drills],
            "cadence_compliance.json": {
                "expected_min": 1,
                "observed": len(drills),
                "satisfied": cadence_check.satisfied,
                "last_drill_at": cadence_check.last_event_at,
            },
            "drill_pass_rate.json": {
                "pass": sum(1 for d in drills if d.outcome == "pass"),
                "fail": sum(1 for d in drills if d.outcome == "fail"),
            },
        }
```

---

## A1.2 — Resumability drill evidence

```python
# compliance/collectors/a1_2_resumability.py
class A12ResumabilityCollector(EvidenceCollector):
    control_id = "A1.2"
    name = "Agent runtime resumability drill"
    cadence = "0 0 1 */3 *"          # quarterly 1st 00:00
    owner = "sre-lead@example.com"
    window_days = 90

    def gather(self, start, end):
        from drills import DrillLog
        drills = DrillLog.query(scenario="worker_crash_mid_task",
                                 start=start, end=end)
        return {
            "drills.jsonl": [d.to_evidence() for d in drills],
            "rerun_charge_check.json": {
                "tasks_resumed": sum(d.tasks_resumed for d in drills),
                "duplicate_charges": sum(d.duplicate_charges for d in drills),
                "expected_duplicates": 0,
            },
            "state_machine_test_run.json":
                CITestRunner.last_pass("agent_state_machine_test"),
        }
```

---

## A1.3 — Replay availability test

```python
# compliance/collectors/a1_3_replay.py
class A13ReplayCollector(EvidenceCollector):
    control_id = "A1.3"
    name = "Action replay availability monthly test"
    cadence = "0 3 1 * *"            # monthly 1st 03:00
    owner = "sre-lead@example.com"
    window_days = 30

    def gather(self, start, end):
        from replay import ReplayEngine
        from runtime import AgentTask
        # Pick 10 random tasks across the window
        sample = AgentTask.random_sample(start, end, n=10)
        results = []
        for task in sample:
            r = ReplayEngine.replay(task.id, mode="mock_provider")
            results.append({
                "task_id": task.id,
                "replay_started_at": r.started_at,
                "replay_finished_at": r.finished_at,
                "deterministic": r.deterministic,
                "drift": r.drift_summary,
            })
        return {
            "replay_sample.jsonl": results,
            "availability_pct": {
                "successful_replays": sum(1 for r in results if r["deterministic"]),
                "total_replays": len(results),
            },
        }
```

---

## C1.2 — Memory erasure proof

```python
# compliance/collectors/c1_2_memory_erasure.py
class C12MemoryErasureCollector(EvidenceCollector):
    control_id = "C1.2"
    name = "Agent memory erasure proof per request"
    cadence = "per_event"
    owner = "dpo@example.com"
    window_days = 0

    def collect_for_request(self, erasure_request_id: str):
        from erasure import MemoryErasureProof
        proof = MemoryErasureProof.run(erasure_request_id)
        artefacts = {
            "request.json": proof.request,
            "cascade_steps.jsonl": proof.steps,           # 9-step cascade
            "post_erasure_verification.json": proof.verification,
            "signed_attestation.txt": proof.attestation,
        }
        return self.pack(artefacts,
                          proof.request["received_at"],
                          proof.completed_at)
```

---

## PI1.1 — Approval-audit completeness

```python
# compliance/collectors/pi1_1_approval_completeness.py
class PI11ApprovalCompletenessCollector(EvidenceCollector):
    control_id = "PI1.1"
    name = "Every irreversible action had documented approval"
    cadence = "0 3 1 * *"            # monthly
    owner = "security-lead@example.com"
    window_days = 30

    def gather(self, start, end):
        from completeness import ApprovalGapDetection
        report = ApprovalGapDetection.run(start, end)
        return {
            "irreversible_action_count.json": {
                "total": report.total_irreversible,
                "with_approval": report.with_approval,
                "without_approval": report.without_approval,
            },
            "gap_list.jsonl": report.gaps,
            "remediation_tickets.jsonl": report.remediation_tickets,
        }
```

---

## PI1.4 — Eval coverage

```python
# compliance/collectors/pi1_4_eval_coverage.py
class PI14EvalCoverageCollector(EvidenceCollector):
    control_id = "PI1.4"
    name = "Agent output quality evidence (eval coverage)"
    cadence = "0 4 1 * *"            # monthly
    owner = "ai-lead@example.com"
    window_days = 30

    def gather(self, start, end):
        from eval_harness import EvalRegistry, EvalRun
        return {
            "golden_coverage.json": EvalRegistry.coverage_by_feature(),
            "monthly_pass_rate.jsonl":
                EvalRun.pass_rate_by_feature(start, end),
            "drift_alerts.jsonl":
                EvalRun.drift_alerts(start, end),
            "judge_calibration.json":
                EvalRegistry.judge_calibration_summary(),
        }
```

---

## CC9.2 — Vendor / subprocessor (LLM provider) due diligence

```python
# compliance/collectors/cc9_2_vendor.py
class CC92VendorCollector(EvidenceCollector):
    control_id = "CC9.2"
    name = "LLM provider and subprocessor due-diligence pack"
    cadence = "0 5 1 */3 *"          # quarterly
    owner = "compliance-lead@example.com"
    window_days = 90

    def gather(self, start, end):
        from vendors import SubprocessorRegistry
        rows = []
        for v in SubprocessorRegistry.all():
            rows.append({
                "name": v.name,
                "service": v.service,
                "data_residency": v.data_residency,
                "soc2_status": v.soc2,
                "iso27001_status": v.iso,
                "hipaa_baa": v.baa,
                "last_attestation_date": v.last_attestation,
                "data_classes_processed": v.data_classes,
            })
        return {
            "subprocessor_list.jsonl": rows,
            "changes_in_window.jsonl":
                SubprocessorRegistry.changes(start, end),
        }
```

---

## Scheduler Wiring

```python
# compliance/schedule.py
from compliance.collectors import (
    CC61AllowlistCollector, CC66BoundaryCollector, CC72MonitoringCollector,
    CC74KillSwitchDrillCollector, A12ResumabilityCollector, A13ReplayCollector,
    PI11ApprovalCompletenessCollector, PI14EvalCoverageCollector,
    CC92VendorCollector,
)

ALL = [
    CC61AllowlistCollector(),
    CC66BoundaryCollector(),
    CC72MonitoringCollector(),
    CC74KillSwitchDrillCollector(),
    A12ResumabilityCollector(),
    A13ReplayCollector(),
    PI11ApprovalCompletenessCollector(),
    PI14EvalCoverageCollector(),
    CC92VendorCollector(),
]

def run_due(now):
    for c in ALL:
        if cron_match(c.cadence, now):
            try:
                pack = c.collect(now)
                MetricsClient.incr("compliance.collector.success",
                                    tags={"control": c.control_id})
            except Exception as e:
                MetricsClient.incr("compliance.collector.failure",
                                    tags={"control": c.control_id})
                AlertManager.page("compliance-collector-failed",
                                   control=c.control_id, error=str(e))
```

A collector failure is itself a CC7.2 monitoring event and pages the on-call. The auditor will ask about collector reliability — show this metric.
