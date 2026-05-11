# Attestation Evidence Pack Builder

Annual / surveillance attestation packs. Per framework: SOC 2 Type II, ISO 27001 surveillance, HIPAA periodic review.

---

## 1. SOC 2 Type II Pack

```python
# compliance/attestation/soc2_t2.py
def build_soc2_type2_pack(audit_window: tuple[date, date]) -> str:
    """SOC 2 Type II evidence pack for the audit window (typically 6-12 months)."""
    ws, we = audit_window
    pack = EvidencePack(
        control_id="SOC2_T2",
        control_framework="SOC2",
        window=audit_window,
        owner="compliance-lead@example.com",
        meta={"control_name": "SOC 2 Type II Annual Attestation"})

    # 1. Monthly run history
    runs = RunSummary.in_window(ws, we)
    pack.add("monthly_runs/index.json", [r.summary for r in runs])
    for r in runs:
        pack.add(f"monthly_runs/{r.id}.json", r.to_dict())

    # 2. Constituent control packs (references; the auditor pulls these from the portal)
    refs = []
    for tsc in SOC2_CONTROLS:
        packs = EvidencePackRegistry.find(tsc, ws, we)
        refs.append({
            "control_id": tsc,
            "pack_count": len(packs),
            "packs": [{"pack_id": p.pack_id, "sha256": p.manifest_sha256,
                        "window": [p.window_start.isoformat(), p.window_end.isoformat()]}
                       for p in packs],
        })
    pack.add("constituent_packs.json", refs)

    # 3. Drills
    pack.add("drills/kill_switch.jsonl", DrillLog.in_window("kill_switch", ws, we))
    pack.add("drills/resumability.jsonl", DrillLog.in_window("worker_crash_mid_task", ws, we))
    pack.add("drills/red_team.jsonl",     DrillLog.in_window("red_team", ws, we))

    # 4. Exception register
    pack.add("exceptions/opened.csv",  ComplianceException.opened_in(ws, we))
    pack.add("exceptions/closed.csv",  ComplianceException.closed_in(ws, we))
    pack.add("exceptions/active_at_end.csv", ComplianceException.active_as_of(we))

    # 5. Access reviews
    pack.add("access_reviews/", AccessReview.exports(ws, we))

    # 6. Incidents (high level; bundles linked)
    incidents = IncidentRegistry.in_window(ws, we)
    pack.add("incidents/index.csv", incidents)
    pack.add("incidents/bundle_references.json", [
        {"incident_id": i.id, "bundle_url": i.evidence_bundle_url,
         "bundle_sha256": i.evidence_bundle_sha256}
        for i in incidents])

    # 7. Control owner attestations
    pack.add("attestations/quarterly.csv", ControlOwnerAttestation.in_window(ws, we))

    # 8. Audit log integrity for the window
    integrity = AuditIntegrityReport.summary_for_window(ws, we)
    pack.add("audit_log_integrity_summary.json", integrity)

    # 9. System description reference (authored by SRS engine)
    pack.add("system_description_ref.txt",
              f"See: docs/compliance/soc2-system-description-v{SystemDescription.current_version()}.md")

    # 10. Subprocessor / vendor pack reference
    pack.add("subprocessor_pack_refs.json",
              EvidencePackRegistry.find("CC9.2", ws, we))

    return pack.sign_and_upload()
```

## 2. ISO 27001 Surveillance Pack

```python
# compliance/attestation/iso_surveillance.py
def build_iso_surveillance_pack(audit_year: int) -> str:
    """ISO 27001 annual surveillance audit pack."""
    ws = date(audit_year, 1, 1)
    we = date(audit_year, 12, 31)
    pack = EvidencePack(
        control_id="ISO_SURVEILLANCE",
        control_framework="ISO27001",
        window=(ws, we),
        owner="compliance-lead@example.com",
        meta={"control_name": f"ISO 27001 Annual Surveillance {audit_year}"})

    # 1. SoA + risk register (authored by SRS engine, referenced)
    pack.add("soa_ref.txt", f"docs/compliance/iso27001-soa-v{SoA.current_version()}.md")
    pack.add("risk_register_ref.txt",
              f"docs/compliance/iso27001-risk-register-v{RiskRegister.current_version()}.md")

    # 2. Asset register snapshots (12 monthly snapshots)
    asset_packs = EvidencePackRegistry.find("A.5.9", ws, we)
    pack.add("asset_register/index.json",
              [{"pack_id": p.pack_id, "month": p.window_end.strftime("%Y-%m")}
               for p in asset_packs])

    # 3. Annex A control packs (one per control with packs in window)
    annex_refs = []
    for clause in ANNEX_A_IN_SCOPE:
        clause_packs = EvidencePackRegistry.find(clause, ws, we)
        if clause_packs:
            annex_refs.append({
                "clause": clause,
                "pack_count": len(clause_packs),
                "packs": [p.pack_id for p in clause_packs],
            })
    pack.add("annex_a_packs.json", annex_refs)

    # 4. Internal audit report (mandatory clause 9.2)
    pack.add("internal_audit_ref.txt",
              f"docs/compliance/iso27001-internal-audit-{audit_year}.md")

    # 5. Management review minutes (mandatory clause 9.3)
    pack.add("management_review_ref.txt",
              f"docs/compliance/iso27001-management-review-{audit_year}.md")

    # 6. Corrective actions
    pack.add("corrective_actions.csv",
              CorrectiveAction.in_window(ws, we))

    # 7. Incidents
    pack.add("incidents.csv", IncidentRegistry.in_window(ws, we))

    # 8. Change records
    pack.add("changes.csv", ChangeTicket.in_window(ws, we))

    return pack.sign_and_upload()
```

## 3. HIPAA Periodic Review Pack

```python
# compliance/attestation/hipaa_annual.py
def build_hipaa_annual_pack(year: int) -> str:
    """HIPAA §164.308(a)(8) annual evaluation pack."""
    ws = date(year, 1, 1)
    we = date(year, 12, 31)
    pack = EvidencePack(
        control_id="HIPAA_ANNUAL_EVAL",
        control_framework="HIPAA",
        window=(ws, we),
        owner="hipaa-security-officer@example.com",
        meta={"control_name": f"HIPAA Annual Evaluation {year}"})

    # 1. HIPAA Risk Analysis + Risk Management Plan refs
    pack.add("risk_analysis_ref.txt",
              f"docs/compliance/hipaa-risk-analysis-v{RiskAnalysis.current_version()}.md")
    pack.add("risk_management_plan_ref.txt",
              f"docs/compliance/hipaa-risk-management-plan-v{RiskMgmtPlan.current_version()}.md")

    # 2. PHI access log slices (monthly)
    phi_packs = EvidencePackRegistry.find("164.312(b)", ws, we)
    pack.add("phi_access_packs.json",
              [{"pack_id": p.pack_id, "month": p.window_end.strftime("%Y-%m")}
               for p in phi_packs])

    # 3. BAA register snapshot at year end
    pack.add("baa_register.csv", LLMProviderBAA.snapshot(at=we))
    pack.add("baa_drift_alerts.jsonl",
              BAADrift.alerts_in_window(ws, we))

    # 4. Workforce training compliance
    pack.add("training_completion.csv",
              TrainingRecord.completion_summary(ws, we))

    # 5. Breaches (and "near-breaches" — events that triggered investigation but were ruled not breaches)
    pack.add("breaches.csv", BreachRegistry.in_window(ws, we))
    pack.add("breach_investigations.csv",
              BreachInvestigation.in_window(ws, we))

    # 6. Drills (DR, contingency, incident response)
    pack.add("drills/dr.jsonl", DrillLog.in_window("disaster_recovery", ws, we))
    pack.add("drills/contingency.jsonl", DrillLog.in_window("contingency", ws, we))

    # 7. Access reviews
    pack.add("access_reviews/", AccessReview.exports(ws, we))

    # 8. PHI scope register changes
    pack.add("phi_scope_changes.csv",
              AgentFeaturePHIScope.changes_in(ws, we))

    # 9. Annual evaluation summary signed by HIPAA Security Officer
    pack.add("annual_evaluation_summary.md",
              AnnualEvaluation.draft(year))
    # Signing happens after Security Officer review

    return pack.sign_and_upload()
```

## 4. Pack Generation Workflow

```python
# compliance/attestation/runner.py
def schedule_attestation_packs():
    # SOC 2 Type II: builds when audit window opens (e.g. 90 days before next audit)
    if AuditCalendar.soc2_next_starts_within(days=90):
        eng = AuditCalendar.soc2_next_engagement()
        build_soc2_type2_pack(eng.window)

    # ISO surveillance: annual, 60 days before scheduled audit
    if AuditCalendar.iso_surveillance_within(days=60):
        year = AuditCalendar.iso_surveillance_year()
        build_iso_surveillance_pack(year)

    # HIPAA annual: 30 days after year end
    if date.today().month == 1 and date.today().day == 30:
        build_hipaa_annual_pack(date.today().year - 1)
```

## 5. Signing Ceremony

The attestation pack signing has a small ceremony:

1. Pack drafted by the builder.
2. Compliance lead reviews summary; opens any final exceptions.
3. CISO signs (HSM key custody).
4. CTO co-signs (segregation of duties).
5. Final pack uploaded to evidence vault under indefinite retention.
6. Auditor portal notification: pack ready for `engagement_id`.

The signing ceremony itself is logged in the audit log as a `attestation_pack_signed` event.

## 6. Pack-of-Packs Verification

The auditor verifies the attestation pack by:

1. `verify.py` confirms the attestation pack's manifest.
2. For each constituent pack referenced, the auditor pulls it from the portal.
3. The auditor runs `verify.py` on each constituent pack.
4. The auditor confirms the constituent pack's `manifest_sha256` matches the value recorded in `constituent_packs.json`.

This is the chain-of-custody for evidence: attestation references control packs which reference events which chain to the audit log seal.
