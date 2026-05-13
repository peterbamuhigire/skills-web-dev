# Control Test Suite — Code

One test function per control. All return a `TestResult`. Run monthly by default; some weekly.

---

## CC6.1 — Allow-list enforcement

```python
def cc6_1_allowlist_enforced(start, end) -> TestResult:
    """Every tool call in the window was permitted by the allow-list at call time."""
    sample = ActionAuditLog.random_sample(event_class="tool_call",
                                            start=start, end=end, n=100)
    failures = []
    for c in sample:
        allowlist = ToolRegistry.allowlist_snapshot_at(c.tenant_id, c.occurred_at)
        if c.tool_name not in allowlist:
            failures.append({"id": c.id, "tool": c.tool_name})
    return TestResult(
        test_id="cc6_1_allowlist_enforced",
        outcome="pass" if not failures else "fail",
        detail=f"sampled={len(sample)} failures={len(failures)}",
        failures=failures,
    )
```

## CC6.3 — Quarterly access review completion

```python
def cc6_3_access_review_completed(start, end) -> TestResult:
    """An access review was signed off for the privileged agent roles in the quarter."""
    review = AccessReview.last_completed("agent_privileged_roles")
    if not review or review.signed_off_at < end - timedelta(days=90):
        return TestResult("cc6_3", "fail",
                           f"last access review {review.signed_off_at if review else 'never'}")
    return TestResult("cc6_3", "pass", f"signed {review.signed_off_at}")
```

## CC6.6 — Tool gateway enforces classifications

```python
def cc6_6_gateway_classifications(start, end) -> TestResult:
    """Every tool call carries data_class; PHI tools call only from PHI-scope features."""
    sample = ActionAuditLog.random_sample(event_class="tool_call",
                                            start=start, end=end, n=200)
    missing_class = [c.id for c in sample if not c.data_class]
    phi_violations = []
    for c in sample:
        if not c.phi_flag:
            continue
        feature_scope = AgentFeature.scope_at(c.feature_id, c.occurred_at)
        if feature_scope in ("no_phi", "metadata_only"):
            phi_violations.append({"id": c.id, "feature": c.feature_id,
                                    "scope": feature_scope})
    outcome = "pass" if not (missing_class or phi_violations) else "fail"
    return TestResult("cc6_6", outcome,
                       f"missing_class={len(missing_class)} phi_violations={len(phi_violations)}",
                       failures={"missing_class": missing_class,
                                  "phi_violations": phi_violations})
```

## CC7.2 — Monitoring evidence exists for every week

```python
def cc7_2_monitoring_coverage(start, end) -> TestResult:
    """A monitoring evidence pack exists for every ISO-week in the window."""
    expected_weeks = iso_weeks_in(start, end)
    actual_packs = EvidencePackRegistry.find("CC7.2", start, end)
    actual_weeks = {iso_week(p.window_end) for p in actual_packs}
    missing = expected_weeks - actual_weeks
    return TestResult("cc7_2", "pass" if not missing else "fail",
                       f"missing_weeks={sorted(missing)}")
```

## CC7.4 — Kill-switch drill within the window

```python
def cc7_4_kill_switch_drilled(start, end) -> TestResult:
    """At least one passing kill-switch drill in any 90-day sub-window."""
    drills = DrillLog.query(scenario="kill_switch", start=start, end=end)
    passing = [d for d in drills if d.outcome == "pass"]
    if not passing:
        return TestResult("cc7_4", "fail", "no passing drills in window")
    last = max(passing, key=lambda d: d.run_at)
    if last.run_at < datetime.utcnow() - timedelta(days=120):
        return TestResult("cc7_4", "fail",
                           f"last passing drill > 120 days ago at {last.run_at}")
    return TestResult("cc7_4", "pass", f"{len(passing)} passing drills; last {last.run_at}")
```

## CC8.1 — Change records exist for every controlled change

```python
def cc8_1_changes_recorded(start, end) -> TestResult:
    """Every prompt / tool / model pin change in window has a change ticket."""
    changes = (
        PromptRegistry.diff(start, end) +
        ToolRegistry.diff(start, end) +
        ModelPinRegistry.diff(start, end)
    )
    unrecorded = [c for c in changes if not ChangeTicket.exists_for(c)]
    return TestResult("cc8_1", "pass" if not unrecorded else "fail",
                       f"changes={len(changes)} unrecorded={len(unrecorded)}",
                       failures=unrecorded)
```

## CC9.2 — Subprocessor BAA status current

```python
def cc9_2_subprocessor_baa(start, end) -> TestResult:
    """No subprocessor in production has an expired or missing BAA where one is required."""
    failures = []
    for v in SubprocessorRegistry.active():
        if not v.baa_required:
            continue
        if not v.baa_signed:
            failures.append({"provider": v.name, "issue": "no BAA"})
        elif v.baa_expiry and v.baa_expiry < date.today():
            failures.append({"provider": v.name, "issue": f"BAA expired {v.baa_expiry}"})
    return TestResult("cc9_2", "pass" if not failures else "fail",
                       f"failures={len(failures)}", failures=failures)
```

## A1.2 — Resumability drill within window

```python
def a1_2_resumability_drilled(start, end) -> TestResult:
    drills = DrillLog.query(scenario="worker_crash_mid_task",
                             start=start, end=end)
    passing = [d for d in drills if d.outcome == "pass"]
    return TestResult("a1_2", "pass" if passing else "fail",
                       f"passing_drills={len(passing)}")
```

## A1.3 — Replay availability test passing

```python
def a1_3_replay_availability(start, end) -> TestResult:
    """Last replay availability test in window showed >= 95% deterministic."""
    pack = EvidencePackRegistry.latest("A1.3", start, end)
    if not pack:
        return TestResult("a1_3", "fail", "no replay pack in window")
    summary = pack.read_json("availability_pct.json")
    pct = summary["successful_replays"] / summary["total_replays"]
    return TestResult(
        "a1_3", "pass" if pct >= 0.95 else "fail",
        f"availability={pct:.2%}")
```

## C1.2 — Memory erasure proofs exist for every erasure request

```python
def c1_2_erasure_proofs(start, end) -> TestResult:
    """Every erasure request received in window has a signed proof."""
    requests = ErasureRequest.received_in(start, end)
    missing_proofs = []
    for r in requests:
        if not MemoryErasureProof.exists_for(r.id):
            missing_proofs.append(r.id)
    return TestResult("c1_2", "pass" if not missing_proofs else "fail",
                       f"requests={len(requests)} missing={len(missing_proofs)}",
                       failures=missing_proofs)
```

## PI1.1 — Approval-audit completeness

```python
def pi1_1_completeness(start, end) -> TestResult:
    """Every irreversible action in the window has a documented approval."""
    from completeness import ApprovalGapDetection
    gaps = ApprovalGapDetection.run(start, end).gaps
    return TestResult("pi1_1", "pass" if not gaps else "fail",
                       f"gaps={len(gaps)}", failures=gaps)
```

## PI1.3 — State-machine idempotency tests passing

```python
def pi1_3_state_machine_tests(start, end) -> TestResult:
    """The agent state-machine idempotency test suite has passed in every CI run in window."""
    runs = CITestRunner.runs_for("agent_state_machine_test", start, end)
    failures = [r for r in runs if r.outcome != "pass"]
    return TestResult("pi1_3", "pass" if not failures else "fail",
                       f"runs={len(runs)} failures={len(failures)}")
```

## PI1.4 — Eval coverage threshold

```python
def pi1_4_eval_coverage(start, end) -> TestResult:
    """Every agent feature in production has at least 50 goldens and ≥ 95% monthly pass rate."""
    failures = []
    for feature in AgentFeature.in_production():
        cov = EvalRegistry.coverage(feature.id)
        if cov.golden_count < 50:
            failures.append({"feature": feature.id, "issue": f"only {cov.golden_count} goldens"})
            continue
        rate = EvalRun.pass_rate(feature.id, start, end)
        if rate < 0.95:
            failures.append({"feature": feature.id, "issue": f"pass rate {rate:.2%}"})
    return TestResult("pi1_4", "pass" if not failures else "fail",
                       f"failures={len(failures)}", failures=failures)
```

## 164.312(b) — PHI access log captures every PHI action

```python
def hipaa_312_b_phi_logged(start, end) -> TestResult:
    """Every PHI action in the window has a row in the action audit log with phi_flag=True."""
    phi_actions = PHIDetector.scan(start, end)
    logged = ActionAuditLog.count(phi_flag=True, start=start, end=end)
    if phi_actions != logged:
        return TestResult("164_312_b", "fail",
                           f"detected={phi_actions} logged={logged}")
    return TestResult("164_312_b", "pass",
                       f"detected={phi_actions} logged={logged}")
```

## 164.308(a)(5) — Workforce training completion

```python
def hipaa_308_a_5_training(start, end) -> TestResult:
    """Every engineer with write access to PHI-scoped features completed agent-specific training in last 12 months."""
    engineers = AgentFeatureAccess.write_access_to_phi_scoped()
    missing = []
    for e in engineers:
        last = TrainingRecord.last_for(e.email, course="agent-phi-handling")
        if not last or last.completed_at < datetime.utcnow() - timedelta(days=365):
            missing.append(e.email)
    return TestResult("164_308_a_5", "pass" if not missing else "fail",
                       f"missing={len(missing)}", failures=missing)
```

## A.5.9 — Asset register has no overdue reviews

```python
def a5_9_no_overdue_reviews(start, end) -> TestResult:
    overdue = AgentAsset.overdue_reviews(at=datetime.utcnow())
    return TestResult("a5_9", "pass" if not overdue else "fail",
                       f"overdue={len(overdue)}",
                       failures=[a.name for a in overdue])
```

## A.8.15 — Audit log integrity intact

```python
def a8_15_audit_integrity(start, end) -> TestResult:
    """No chain breaks, seal breaks, or archive drift detected in window."""
    reports = AuditIntegrityReport.in_window(start, end)
    breaks = sum(r.chain_break_count + r.seal_break_count + r.archive_drift_count
                 for r in reports)
    return TestResult("a8_15", "pass" if breaks == 0 else "fail",
                       f"integrity_breaks={breaks}")
```

## Registry

```python
# compliance/tests/registry.py
ALL_TESTS = [
    ControlTest("cc6_1", "CC6.1", "Allow-list enforced", "critical", cc6_1_allowlist_enforced),
    ControlTest("cc6_3", "CC6.3", "Access review completed", "high", cc6_3_access_review_completed),
    ControlTest("cc6_6", "CC6.6", "Gateway enforces classifications", "critical", cc6_6_gateway_classifications),
    ControlTest("cc7_2", "CC7.2", "Monitoring coverage", "high", cc7_2_monitoring_coverage),
    ControlTest("cc7_4", "CC7.4", "Kill-switch drilled", "high", cc7_4_kill_switch_drilled),
    ControlTest("cc8_1", "CC8.1", "Changes recorded", "critical", cc8_1_changes_recorded),
    ControlTest("cc9_2", "CC9.2", "Subprocessor BAA current", "critical", cc9_2_subprocessor_baa),
    ControlTest("a1_2",  "A1.2",  "Resumability drilled", "high", a1_2_resumability_drilled),
    ControlTest("a1_3",  "A1.3",  "Replay availability", "high", a1_3_replay_availability),
    ControlTest("c1_2",  "C1.2",  "Erasure proofs exist", "critical", c1_2_erasure_proofs),
    ControlTest("pi1_1", "PI1.1", "Approval completeness", "critical", pi1_1_completeness),
    ControlTest("pi1_3", "PI1.3", "State-machine tests", "high", pi1_3_state_machine_tests),
    ControlTest("pi1_4", "PI1.4", "Eval coverage", "medium", pi1_4_eval_coverage),
    ControlTest("164_312_b", "164.312(b)", "PHI access logged", "critical", hipaa_312_b_phi_logged),
    ControlTest("164_308_a_5", "164.308(a)(5)", "Workforce training", "high", hipaa_308_a_5_training),
    ControlTest("a5_9", "A.5.9", "Asset register reviews current", "medium", a5_9_no_overdue_reviews),
    ControlTest("a8_15", "A.8.15", "Audit log integrity", "critical", a8_15_audit_integrity),
]
```
