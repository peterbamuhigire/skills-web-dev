> Consolidated from skills/ai-agent-control-testing-and-attestation/SKILL.md into ai-agent-compliance-controls on 2026-05-13. Load this through skills/ai-agent-compliance-controls/SKILL.md, not as an active skill entrypoint.

# AI Agent Control Testing and Attestation
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Building **automated control tests** that run on cadence (monthly default) for each agent compliance control.
- Wiring control test failure to **tickets** with severity, owner, target close.
- Producing **auditor-friendly test reports** that show evidence-of-operation for the audit window.
- Producing the **attestation evidence pack** for SOC 2 Type II / ISO surveillance / HIPAA periodic review.
- Producing the **control owner quarterly attestation** workflow.

## Do Not Use When

- The task is the **control implementation** — the SOC 2 / ISO / HIPAA skills.
- The task is the **evidence pack format** — `ai-agent-evidence-automation`.
- The task is the **audit log integrity** — `ai-agent-audit-log-integrity`.

## Required Inputs

- Per-control implementations (from SOC 2 / ISO / HIPAA skills).
- Evidence collectors emitting packs (from `ai-agent-evidence-automation`).
- Ticket system (Jira, Linear, GitHub Issues) for exceptions.
- Compliance console (`saas-admin-backoffice-tooling`) for run-status views.
- Audit calendar (when SOC 2 Type II observation window opens, when ISO surveillance is scheduled).

## Workflow

1. Read this `SKILL.md`.
2. Build the **control test suite** (§1). Each test is a small Python function with deterministic pass/fail. See `references/control-test-suite.md`.
3. Wire the **monthly run** (§2) — scheduler picks up the suite; results go to a run record + pack.
4. Wire **failure to ticket** (§3) — exception opened in the ticket system; tracked to closure.
5. Build the **attestation pack builder** (§4). See `references/attestation-evidence-pack.md`.
6. Wire the **quarterly control owner attestation** (§5) — owner signs the run summary; signature stored.
7. Apply anti-patterns (§6).

## Quality Standards

- Every control listed in the TSC / Annex A / HIPAA mapping has at least one automated test.
- Test pass / fail is deterministic. "Flaky test" → fix the test or remediate the underlying flakiness.
- Failure opens a ticket within 15 minutes; ticket carries the test name, the expected vs actual, and the pack URL.
- Tickets are tracked to closure with target-close dates per severity (critical 7 days, high 30, medium 90, low 180).
- Attestation pack is generated from the run history + ticket register; auditor reads one URL.

## Anti-Patterns

- Control test that always passes ("we have a kill-switch — yes we do"). No actual verification.
- Test that runs but failure is logged. No ticket, no owner, no closure.
- Tests written once at audit prep and not maintained. Drift between implementation and test.
- Attestation pack built by manual collation. Auditor reads stale data.
- Control owner attests without reading the run summary. Signature is hollow.
- Test failure remediated by silencing the test. Compliance theatre.

## Outputs

- Control test suite (Python).
- Scheduler integration (monthly).
- Failure → ticket wiring.
- Attestation pack builder.
- Control owner attestation workflow.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Compliance | Control test run record | DB + monthly pack | `evidence/cc4_1/2026-MM.tar.gz` |
| Compliance | Exception register | DB + monthly export | `evidence/exceptions/2026-MM.csv` |
| Compliance | SOC 2 Type II attestation pack | tar.gz + manifest + signature | `evidence/attestation/soc2-t2-2026.tar.gz` |
| Compliance | ISO surveillance pack | tar.gz | `evidence/attestation/iso-2026.tar.gz` |
| Compliance | HIPAA annual evaluation pack | tar.gz | `evidence/attestation/hipaa-2026.tar.gz` |
| Compliance | Control owner attestation | Signed records | `evidence/attestations/2026-Q-{owner}.tar.gz` |

## References

- `references/control-test-suite.md` — Test code per control.
- `references/attestation-evidence-pack.md` — Pack builder + format per framework.
- Companion: `ai-agent-soc2-controls`, `ai-agent-iso27001-controls`, `ai-agent-hipaa-security-controls`, `ai-agent-evidence-automation`, `ai-agent-audit-log-integrity`.

<!-- dual-compat-end -->

## §1 Control Test Suite

Each test is a function:

```python
# compliance/tests/base.py
from dataclasses import dataclass
from typing import Callable

@dataclass
class ControlTest:
    test_id: str
    control_id: str          # e.g. "CC6.1"
    name: str
    severity: str            # "critical","high","medium","low" if it fails
    runner: Callable[[date, date], "TestResult"]
    cadence: str = "monthly"

@dataclass
class TestResult:
    test_id: str
    started_at: datetime
    finished_at: datetime
    outcome: str             # "pass","fail","error"
    detail: str
    evidence_refs: list[str] # pack ids
```

Example test:

```python
# compliance/tests/cc6_1_allowlist_enforcement.py
def cc6_1_allowlist_enforced(start: date, end: date) -> TestResult:
    """Every tool call in the window was permitted by the allow-list at call time."""
    started = datetime.utcnow()
    # Sample 100 random tool calls from the window
    sample = ActionAuditLog.random_sample(
        event_class="tool_call", start=start, end=end, n=100)
    failures = []
    for call in sample:
        allowlist_at_call = ToolRegistry.allowlist_snapshot_at(
            call.tenant_id, call.occurred_at)
        if call.tool_name not in allowlist_at_call:
            failures.append({
                "call_id": call.id,
                "tenant_id": call.tenant_id,
                "tool": call.tool_name,
                "occurred_at": call.occurred_at.isoformat(),
            })
    outcome = "pass" if not failures else "fail"
    return TestResult(
        test_id="cc6_1_allowlist_enforced",
        started_at=started,
        finished_at=datetime.utcnow(),
        outcome=outcome,
        detail=f"sampled={len(sample)} failures={len(failures)}",
        evidence_refs=[],
    )
```

Full list of tests in `references/control-test-suite.md`.

## §2 Monthly Run

```python
# compliance/test_runner.py
def run_monthly(window_start: date, window_end: date) -> "RunSummary":
    from compliance.tests.registry import ALL_TESTS
    run = RunSummary(id=ulid(), window=(window_start, window_end))
    for t in ALL_TESTS:
        result = t.runner(window_start, window_end)
        run.add(result)
        if result.outcome == "fail":
            _open_exception(t, result, window_start, window_end)
        elif result.outcome == "error":
            _alert(t, result)
    # Build evidence pack for this run
    pack = EvidencePack(
        control_id="CC4.1",
        control_framework="SOC2",
        window=(window_start, window_end),
        owner="compliance-lead@example.com")
    pack.add("run_summary.json", run.to_dict())
    pack.add("results.jsonl", [asdict(r) for r in run.results])
    pack.add("test_versions.json", _test_versions())
    pack_url = pack.sign_and_upload()
    run.pack_url = pack_url
    run.persist()
    return run
```

## §3 Failure → Ticket

```python
# compliance/exception_opener.py
SEVERITY_TO_TARGET_DAYS = {"critical": 7, "high": 30, "medium": 90, "low": 180}

def _open_exception(test: ControlTest, result: TestResult,
                     window_start: date, window_end: date):
    target = datetime.utcnow() + timedelta(
        days=SEVERITY_TO_TARGET_DAYS[test.severity])
    ticket = TicketSystem.create(
        title=f"Compliance exception: {test.control_id} — {test.name}",
        body=f"""Control test {test.test_id} failed.

**Control:** {test.control_id}
**Severity:** {test.severity}
**Window:** {window_start} – {window_end}
**Outcome:** {result.outcome}
**Detail:** {result.detail}
**Test run record:** {result.test_id}

Target close: {target.date()}.

Remediation:
1. Triage with control owner.
2. Determine root cause.
3. Remediate.
4. Re-run test on remediation.
5. Update runbook if process gap.
6. Close ticket with link to remediation evidence pack.
""",
        labels=["compliance", test.control_id, f"sev-{test.severity}"],
        assignee=ControlOwners.get(test.control_id),
        target_close=target,
    )
    ComplianceException.record(
        control_id=test.control_id,
        test_id=test.test_id,
        opened_at=datetime.utcnow(),
        severity=test.severity,
        ticket_url=ticket.url,
        target_close=target,
        evidence_pack_url=result.evidence_refs,
        status="open")
```

## §4 Attestation Pack Builder

The annual attestation pack collates a year of monthly runs + exception register + access reviews + drills + incident records. See `references/attestation-evidence-pack.md` for the full builder code.

Summary:

```python
def build_soc2_type2_pack(audit_window: tuple[date, date]) -> str:
    pack = EvidencePack(
        control_id="SOC2_T2",
        control_framework="SOC2",
        window=audit_window,
        owner="compliance-lead@example.com")
    # Monthly runs
    runs = RunSummary.in_window(*audit_window)
    pack.add("monthly_runs/index.json", [r.summary for r in runs])
    for r in runs:
        pack.add(f"monthly_runs/{r.id}.json", r.to_dict())
    # Exception register
    pack.add("exceptions/active.csv", ComplianceException.active())
    pack.add("exceptions/closed_in_window.csv",
              ComplianceException.closed_in(*audit_window))
    # Constituent control packs
    pack.add("constituent_packs.json", EvidencePackRegistry.references_for_window(*audit_window))
    # Drills
    pack.add("drills/kill_switch.jsonl", DrillLog.in_window("kill_switch", *audit_window))
    pack.add("drills/resumability.jsonl", DrillLog.in_window("resumability", *audit_window))
    pack.add("drills/red_team.jsonl", DrillLog.in_window("red_team", *audit_window))
    # Access reviews
    pack.add("access_reviews/", AccessReview.exports(*audit_window))
    # Incidents
    pack.add("incidents/index.csv", IncidentRegistry.in_window(*audit_window))
    # Control owner attestations
    pack.add("attestations/quarterly.csv", ControlOwnerAttestation.in_window(*audit_window))
    return pack.sign_and_upload()
```

## §5 Quarterly Control Owner Attestation

Each control owner signs quarterly that:

1. The control operated for the quarter.
2. Test results have been reviewed.
3. Exceptions have been opened and tracked.
4. No undocumented exceptions exist.

```sql
CREATE TABLE control_owner_attestations (
  id              BIGINT PRIMARY KEY,
  control_id      VARCHAR(64) NOT NULL,
  owner           VARCHAR(256) NOT NULL,
  quarter         VARCHAR(8) NOT NULL,           -- "2026-Q2"
  signed_at       TIMESTAMP NOT NULL,
  signed_payload  JSON NOT NULL,                  -- run ids + exception ids + pack refs
  signature       BLOB NOT NULL,                  -- detached signature
  status          ENUM('pending','signed','declined') NOT NULL,
  decline_reason  TEXT
);
```

A pending attestation that ages > 30 days into the new quarter pages the CISO. Declines require remediation before the next quarter close.

## §6 Anti-Patterns

- Test is a print statement. No pass/fail; no ticket; no evidence.
- Test runs and the result is read by a human who decides to ignore. No audit trail of the ignore.
- Severity assigned arbitrarily; "critical" loses meaning. Calibrate severity to regulatory consequence.
- Target close dates not enforced. Tickets age indefinitely; auditor reads the register and scopes findings.
- Attestation pack regenerated on the day of audit. Auditor reads timestamp; disqualifies.
- Owner attests without evidence; signature is theatre. Require owner to acknowledge the specific run ids and exceptions.


