# ISO 27001 Evidence Collection Pipelines

Per Annex A control, the pipeline that gathers and signs evidence.

---

## A.5.9 — Asset Register Snapshot

```python
# compliance/iso/a5_9_assets.py
from compliance.collectors.base import EvidenceCollector

class A59AssetRegisterCollector(EvidenceCollector):
    control_id = "A.5.9"
    name = "Agent asset register snapshot"
    cadence = "0 1 1 * *"            # monthly 1st 01:00
    owner = "platform-eng@example.com"
    window_days = 30

    def gather(self, start, end):
        from registry import AgentAsset
        snapshot = AgentAsset.snapshot(at=end)
        changes = AgentAsset.changes_in_window(start, end)
        overdue = AgentAsset.overdue_reviews(at=end)
        return {
            "asset_register.csv": snapshot,
            "changes_in_window.csv": changes,
            "overdue_reviews.csv": overdue,
            "summary.json": {
                "total_assets": len(snapshot),
                "by_type": _count_by(snapshot, "asset_type"),
                "by_classification": _count_by(snapshot, "classification"),
                "overdue_count": len(overdue),
            },
        }
```

`overdue_reviews` count is a leading indicator of A.5.9 failure; alert when > 0 for more than 7 days.

---

## A.5.15 — Access Control (Allow-list)

Same as SOC 2 CC6.1 — produce one pack, reference from both.

```python
# compliance/iso/a5_15_access.py
class A515AccessCollector(EvidenceCollector):
    control_id = "A.5.15"
    name = "Per-tenant tool allow-list and min-role enforcement"
    cadence = "0 1 * * *"
    owner = "platform-eng@example.com"

    def gather(self, start, end):
        # Delegate to the SOC 2 CC6.1 collector data — single source
        from compliance.collectors.cc6_1_allowlist import CC61AllowlistCollector
        return CC61AllowlistCollector().gather(start, end)
```

---

## A.5.18 — Quarterly Access Review

```python
# compliance/iso/a5_18_access_review.py
class A518AccessReviewCollector(EvidenceCollector):
    control_id = "A.5.18"
    name = "Quarterly access review of agent privileged roles"
    cadence = "0 9 1 */3 *"          # quarterly 1st 09:00
    owner = "ciso@example.com"
    window_days = 90

    def gather(self, start, end):
        from iam import RoleRegistry, AccessReview
        review = AccessReview.start_for("agent_privileged_roles", end)
        # Auto-pull current membership
        roles_to_review = [
            "kill_switch_operator",
            "agent_admin",
            "compliance_console_operator",
            "evidence_vault_reader",
            "high_risk_approval_reviewer",
        ]
        rows = []
        for role in roles_to_review:
            members = RoleRegistry.members(role, at=end)
            for m in members:
                rows.append({
                    "role": role,
                    "user": m.email,
                    "added_at": m.added_at,
                    "last_used_at": m.last_used_at,
                    "needed_per_role_owner": None,  # owner fills in
                })
        return {
            "review_ticket.json": review.ticket,
            "membership.csv": rows,
            "previous_review.json": AccessReview.previous("agent_privileged_roles"),
            "instructions.md": review.instructions_for_owner,
        }
```

The owner of each role signs the review by responding to the ticket; the signed review is uploaded to the pack within 30 days.

---

## A.5.19-.23 — Supplier Pack

```python
# compliance/iso/a5_19_supplier.py
class A519SupplierCollector(EvidenceCollector):
    control_id = "A.5.19"
    name = "LLM provider and subprocessor due-diligence pack"
    cadence = "0 5 1 */3 *"          # quarterly
    owner = "compliance-lead@example.com"

    def gather(self, start, end):
        from vendors import SubprocessorRegistry, ProviderAttestation
        subs = []
        for v in SubprocessorRegistry.all():
            atts = ProviderAttestation.for_provider(v.id)
            subs.append({
                "name": v.name,
                "service": v.service,
                "data_residency": v.data_residency,
                "data_classes": v.data_classes,
                "soc2_status": atts.soc2,
                "iso27001_status": atts.iso,
                "hipaa_baa": atts.baa,
                "last_attestation": atts.last_received,
                "next_attestation_due": atts.next_due,
                "dpa_version": v.dpa_version,
                "dpa_signed_at": v.dpa_signed_at,
            })
        return {
            "subprocessor_list.csv": subs,
            "attestation_register.csv":
                ProviderAttestation.register_export(),
            "dpa_register.csv":
                SubprocessorRegistry.dpa_register_export(),
            "changes_in_quarter.jsonl":
                SubprocessorRegistry.changes(start, end),
        }
```

---

## A.5.24-.28 — Incident Records

```python
# compliance/iso/a5_24_incidents.py
class A524IncidentCollector(EvidenceCollector):
    control_id = "A.5.24"
    name = "AI incident records — ISO-format export"
    cadence = "0 6 1 * *"            # monthly
    owner = "sre-lead@example.com"

    def gather(self, start, end):
        from incidents import IncidentRegistry
        incidents = IncidentRegistry.query(category="ai", start=start, end=end)
        rows = []
        for i in incidents:
            rows.append({
                "id": i.id,
                "severity": i.severity,
                "failure_class": i.failure_class,
                "detected_at": i.detected_at,
                "ack_at": i.ack_at,
                "mitigated_at": i.mitigated_at,
                "resolved_at": i.resolved_at,
                "evidence_bundle_ref": i.evidence_bundle,
                "postmortem_ref": i.postmortem,
                "iso_clause": "A.5.24-.28",
            })
        return {
            "incidents.csv": rows,
            "drill_log.csv": DrillLog.query(start, end),
        }
```

---

## A.8.9 — Configuration Management (Registry Diff)

```python
# compliance/iso/a8_9_config.py
class A89ConfigCollector(EvidenceCollector):
    control_id = "A.8.9"
    name = "Tool and prompt registry configuration baseline"
    cadence = "0 2 * * *"            # daily 02:00
    owner = "platform-eng@example.com"

    def gather(self, start, end):
        from registry import ToolRegistry, PromptRegistry, ModelPinRegistry
        return {
            "tool_baseline.csv": ToolRegistry.snapshot(at=end),
            "prompt_baseline.csv": PromptRegistry.snapshot(at=end),
            "model_pin_baseline.csv": ModelPinRegistry.snapshot(at=end),
            "drift_from_yesterday.jsonl":
                ToolRegistry.diff(start, end) +
                PromptRegistry.diff(start, end) +
                ModelPinRegistry.diff(start, end),
        }
```

Drift outside the change-management process is an A.8.32 exception.

---

## A.8.15 — Logging (Integrity Report)

```python
# compliance/iso/a8_15_logging.py
class A815LoggingCollector(EvidenceCollector):
    control_id = "A.8.15"
    name = "Hash-chained action audit log integrity"
    cadence = "0 4 * * *"            # daily 04:00 after verification job
    owner = "platform-eng@example.com"

    def gather(self, start, end):
        from audit_integrity import IntegrityVerifier
        report = IntegrityVerifier.last_run()
        return {
            "verification_report.json": report.summary,
            "chain_breaks.jsonl": report.chain_breaks,   # expect empty
            "missing_signatures.jsonl": report.missing_signatures,
            "retention_compliance.json": report.retention_compliance,
        }
```

---

## A.8.16 — Monitoring

```python
# compliance/iso/a8_16_monitoring.py
class A816MonitoringCollector(EvidenceCollector):
    control_id = "A.8.16"
    name = "Agent runtime monitoring evidence"
    cadence = "0 6 1 * *"            # monthly
    owner = "sre-lead@example.com"

    def gather(self, start, end):
        from monitoring import SLOEngine, AlertLog, Dashboard
        return {
            "slo_report.json": SLOEngine.monthly_report(start, end),
            "alert_log.jsonl": AlertLog.query(category="agent", start=start, end=end),
            "dashboard_snapshots/": Dashboard.export_all_for_month(end),
            "review_signoff.txt": MonitoringReview.signoff(end),
        }
```

---

## A.8.25-.34 — Secure Development

```python
# compliance/iso/a8_25_sdlc.py
class A825SDLCCollector(EvidenceCollector):
    control_id = "A.8.25"
    name = "Secure development of prompts, tools, models"
    cadence = "0 7 1 */3 *"          # quarterly
    owner = "eng-leadership@example.com"
    window_days = 90

    def gather(self, start, end):
        from changes import ChangeTicket
        return {
            "prompt_changes.csv":
                ChangeTicket.query(scope="prompt", start=start, end=end),
            "tool_changes.csv":
                ChangeTicket.query(scope="tool", start=start, end=end),
            "model_pin_changes.csv":
                ChangeTicket.query(scope="model_pin", start=start, end=end),
            "review_compliance.json":
                ChangeTicket.review_compliance(start, end),
            "eval_gate_compliance.json":
                ChangeTicket.eval_gate_compliance(start, end),
        }
```

---

## Cron Manifest

```yaml
# ops/compliance/iso-evidence-cadence.yaml
collectors:
  - id: a5_9_assets
    cadence: "0 1 1 * *"
  - id: a5_15_access
    cadence: "0 1 * * *"
  - id: a5_18_access_review
    cadence: "0 9 1 */3 *"
  - id: a5_19_supplier
    cadence: "0 5 1 */3 *"
  - id: a5_24_incidents
    cadence: "0 6 1 * *"
  - id: a8_9_config
    cadence: "0 2 * * *"
  - id: a8_15_logging
    cadence: "0 4 * * *"
  - id: a8_16_monitoring
    cadence: "0 6 1 * *"
  - id: a8_25_sdlc
    cadence: "0 7 1 */3 *"
```
