---
name: ai-agent-approval-audit-completeness
description: Use when checking that every irreversible agent action has signed approval evidence linked to the action audit log, and producing an approval-gap register or audit evidence pack.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Agent Approval-Audit Completeness

## Operating contract

## Inputs

| Input | Required | Purpose |
|---|---|---|
| Domain evidence | yes | approval-audit window, irreversible-action export, approval records, signer identities, and hash-chain witness |

## Outputs

- Produce: approval completeness report, gap register, exception dispositions, and signed evidence-pack manifest.

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

- An auditor (SOC 2 Type II / ISO 27001 / HIPAA) asks: *"Show me every irreversible action your agents took in Q2; prove each one had a documented approval before execution."*
- Building the **completeness check** (also called the gap-detection job) that, for every irreversible action in the audit window, verifies an approval row exists, was signed by an authorised approver, occurred before the action, and is linked back to the action audit row.
- Producing the **SOC 2 Processing Integrity (PI1.1)** evidence pack — system processing is complete, accurate, timely, and authorised.
- Closing the loop between the approval mechanism (`ai-agent-action-approval-and-hitl`) and the tamper-evident audit log (`ai-agent-audit-log-integrity`) so that a missing or backfilled approval is detected automatically.

## Do Not Use When

- Designing the approval **mechanism / state machine** — that is `ai-agent-action-approval-and-hitl`.
- Designing the **tamper-evident storage** of the audit log — `ai-agent-audit-log-integrity`.
- Building **per-control SOC 2 collectors** generally — `ai-agent-soc2-controls`; this skill is the dedicated PI1.1 collector.
- Writing **policy narrative** (control description, RACI) — SRS engine.

## Required Inputs

- Action audit log with `event_class`, `reversibility ∈ {reversible, soft_reversible, irreversible}`, `tool_name`, `task_id`, `step_index`, `tenant_id`, `occurred_at`, `payload_ref`, hash-chained per `ai-agent-audit-log-integrity`.
- Approval table with `approval_id`, `request_id`, `approver_id`, `approver_role`, `approved_at`, `signature`, `linked_action_id`, `policy_version`.
- Tool registry with `tool_id → required_approval_level` (none / single-approver / dual-approver / break-glass).
- Approver allow-list per tenant (role → identity).
- Clock authority (NTP-disciplined, monotonic check) so `approved_at < action_occurred_at` is provable.

## Workflow

1. Read this `SKILL.md`.
2. Run the **completeness check** (§1) over the rolling window — joins the action audit log to the approval table, classifies every row.
3. Triage **gaps** (§2) — there are five canonical gap classes; each has a remediation path.
4. Produce the **completeness evidence pack** (§3) — signed pack with totals, gap report, sample of approvals (auditor-pulled), integrity-chain witness.
5. Auto-open **exceptions** for any gap that is not a benign legacy / migration artefact (§4).
6. Wire the job into the **evidence pipeline** (`ai-agent-evidence-automation`) on a monthly cadence with per-quarter rollup.
7. Apply anti-patterns (§5).

## Quality Standards

- **Zero unexplained gaps.** Every irreversible-action row in the window either has a matching approval row OR a documented exception that has been triaged.
- **Temporal proof.** Every approval timestamp is strictly before the linked action timestamp; clock-skew tolerance is documented (≤ 2s) and any breach is itself an exception.
- **Cryptographic linkage.** Approval row carries `linked_action_chain_pos` (the chain position of the audit row it authorised). Verification job re-derives the chain hash to confirm linkage.
- **Approver authority.** Every approver identity is verified against the approver allow-list **as of the policy_version** in force at approval time — not the current allow-list.
- **No self-approval.** Approver identity ≠ initiator identity. Dual-approval requires two distinct approvers.
- **Job heartbeat is itself evidence.** A missed run is an exception.

## Anti-Patterns

- Joining on `approval.linked_action_id` only; missing the chain-position cross-check. A backfilled approval would pass.
- Comparing `approved_at < action_occurred_at` with database clock instead of an authoritative monotonic clock. Backdating is undetected.
- Allow-list checked against the **current** state at job time. Approvers who have since been removed look as if they were never authorised.
- Treating "approval missing" the same as "approval explicit-bypass with kill-switch flip". Different controls; different evidence rows.
- One giant gap report at audit time. Auditor wants monthly cadence inside the window.

## Outputs

- Gap-detection job (Python) running monthly.
- Completeness report schema (totals, by-tool, by-tenant, gap rows).
- Completeness evidence pack format (PI1.1).
- Exception register entries auto-opened for unresolved gaps.
- Auditor portal endpoint returning the latest signed pack per window.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Security | Approval completeness report | JSON + signed PDF | `evidence/soc2/PI1.1/2026-Q2/completeness-report.json` |
| Security | Gap rows (per irreversible action without approval) | JSONL | `.../gaps.jsonl` |
| Security | Sample of approvals (auditor sample) | JSONL | `.../approvals-sample.jsonl` |
| Security | Integrity-chain witness for the window | JSON | `.../chain-witness.json` |
| Security | Quarterly rollup | tar.gz pack | `.../PI1.1-2026Q2.tar.gz` |
| Security | Exception entries (open / closed during window) | JSONL | `.../exceptions.jsonl` |

## References

- `references/gap-detection-job.md` — Full Python implementation of the completeness / gap-detection job.
- `references/completeness-evidence.md` — Evidence pack schema for SOC 2 PI1.1.
- Companions: `ai-agent-action-approval-and-hitl` (approval mechanism), `ai-agent-audit-log-integrity` (storage), `ai-agent-soc2-controls` (PI1.1 control narrative consumer), `ai-agent-evidence-automation` (pack pipeline), `ai-agent-control-testing-and-attestation` (test wrapper).

<!-- dual-compat-end -->

## §1 The Completeness Check

The check is a **set-difference + temporal-validity** join across two tables, executed inside the database for atomicity.

```sql
-- compliance/queries/approval_completeness.sql
WITH irreversible_actions AS (
  SELECT
    al.id            AS action_id,
    al.chain_pos     AS action_chain_pos,
    al.tenant_id,
    al.task_id,
    al.step_index,
    al.tool_name,
    al.actor_id      AS initiator_id,
    al.occurred_at   AS action_at,
    al.policy_version
  FROM action_audit_log al
  WHERE al.reversibility = 'irreversible'
    AND al.occurred_at >= :window_start
    AND al.occurred_at <  :window_end
),
matched AS (
  SELECT
    ia.*,
    ap.id            AS approval_id,
    ap.approver_id,
    ap.approver_role,
    ap.approved_at,
    ap.signature,
    ap.linked_action_chain_pos,
    ap.policy_version AS approval_policy_version
  FROM irreversible_actions ia
  LEFT JOIN approvals ap
    ON ap.linked_action_id = ia.action_id
)
SELECT
  *,
  CASE
    WHEN approval_id IS NULL                                   THEN 'gap_missing'
    WHEN approved_at >= action_at                              THEN 'gap_after_action'
    WHEN linked_action_chain_pos <> action_chain_pos           THEN 'gap_chain_mismatch'
    WHEN approver_id = initiator_id                            THEN 'gap_self_approval'
    WHEN approval_policy_version <> policy_version             THEN 'gap_policy_version'
    ELSE 'ok'
  END AS classification
FROM matched;
```

Approver authority is checked in a second pass in Python against the **historical** allow-list (versioned per `policy_version`), not the current state.

```python
# compliance/jobs/approval_completeness.py
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable
import hashlib, json

from audit.chain import verify_slice
from policy.versions import resolve_allowlist_at

@dataclass(frozen=True)
class Gap:
    action_id: int
    classification: str
    detail: dict

class ApprovalCompletenessJob:
    def __init__(self, db, evidence_vault, clock_skew_seconds: int = 2):
        self.db = db
        self.vault = evidence_vault
        self.skew = clock_skew_seconds

    def run(self, window_start: datetime, window_end: datetime) -> dict:
        rows = self.db.execute(
            open("compliance/queries/approval_completeness.sql").read(),
            window_start=window_start, window_end=window_end,
        ).fetchall()

        totals = {"irreversible_actions": len(rows), "matched": 0, "gaps": 0}
        gap_buckets: dict[str, list[Gap]] = {}

        for r in rows:
            cls = r["classification"]
            # Second-pass: historical allow-list check
            if cls == "ok":
                allow = resolve_allowlist_at(r["tenant_id"], r["policy_version"])
                if r["approver_id"] not in allow.get(r["approver_role"], set()):
                    cls = "gap_unauthorised_approver"
            # Clock-skew check
            if cls == "gap_after_action":
                drift = (r["approved_at"] - r["action_at"]).total_seconds()
                if drift <= self.skew:
                    cls = "ok_within_skew_tolerance"

            if cls.startswith("gap_"):
                totals["gaps"] += 1
                gap_buckets.setdefault(cls, []).append(
                    Gap(action_id=r["action_id"], classification=cls, detail=dict(r))
                )
            else:
                totals["matched"] += 1

        # Integrity witness over the audit-log slice
        witness = verify_slice(window_start, window_end)

        report = {
            "control_id": "PI1.1",
            "window_start": window_start.isoformat(),
            "window_end":   window_end.isoformat(),
            "totals":       totals,
            "gap_classes":  {k: len(v) for k, v in gap_buckets.items()},
            "chain_witness": witness,
            "policy_versions_observed": sorted({r["policy_version"] for r in rows}),
            "produced_at":  datetime.utcnow().isoformat(),
        }

        # Persist the report + gap rows + a sampled approvals JSONL
        report_path = self.vault.put_json("PI1.1", window_start, window_end, "completeness-report.json", report)
        gap_path    = self.vault.put_jsonl("PI1.1", window_start, window_end, "gaps.jsonl",
                                           [g.detail for bucket in gap_buckets.values() for g in bucket])
        sample_path = self.vault.put_jsonl("PI1.1", window_start, window_end, "approvals-sample.jsonl",
                                           self._sample_approvals(rows, n=200))

        # Open exceptions for each non-benign gap
        for cls, gaps in gap_buckets.items():
            for g in gaps:
                self._open_exception(g, cls)

        return {
            "report_path": report_path, "gap_path": gap_path, "sample_path": sample_path,
            "totals": totals, "gap_classes": report["gap_classes"],
        }

    def _sample_approvals(self, rows, n: int) -> list[dict]:
        import random
        ok = [r for r in rows if r["classification"] == "ok"]
        return random.sample(ok, min(n, len(ok)))

    def _open_exception(self, gap: Gap, cls: str):
        from compliance.exceptions import open_exception
        open_exception(
            control_id="PI1.1",
            severity={"gap_missing": "high", "gap_after_action": "high",
                      "gap_chain_mismatch": "critical", "gap_self_approval": "critical",
                      "gap_unauthorised_approver": "critical",
                      "gap_policy_version": "medium"}.get(cls, "medium"),
            title=f"Approval completeness gap: {cls} on action {gap.action_id}",
            evidence_ref=f"PI1.1/{gap.action_id}",
            detail=gap.detail,
        )
```

Full implementation including the SQL, second-pass policy resolver, exception opener, and the evidence-pack writer in `references/gap-detection-job.md`.

## §2 Gap Classes and Remediation

| Class | Meaning | Remediation |
|---|---|---|
| `gap_missing` | Irreversible action has no approval row | Investigate: bypass via kill-switch? backfill? Bug? Open exception; if explicit kill-switch flip, link kill-switch record and reclassify. |
| `gap_after_action` | Approval `approved_at >= action_at` (beyond skew tolerance) | Backdated or out-of-order. Critical for PI1.1. |
| `gap_chain_mismatch` | Approval's `linked_action_chain_pos` ≠ action's actual chain position | Approval references a different action; usually a row-ID reuse bug. Critical. |
| `gap_self_approval` | Approver = initiator | Segregation-of-duties failure. Critical. |
| `gap_unauthorised_approver` | Approver not on the allow-list as of `policy_version` | Identity / role drift. Critical. |
| `gap_policy_version` | Approval signed under a different policy version than the action | Stale approval; usually means policy changed mid-flight. Medium. |

## §3 Completeness Evidence Pack

The pack is a tar.gz containing:

```
PI1.1-2026Q2/
├── manifest.json                   # control_id, window, signer, sha256 of every file
├── completeness-report.json        # totals + gap class counts + chain witness
├── gaps.jsonl                      # one row per gap with full context
├── approvals-sample.jsonl          # sampled ok approvals (n=200) for auditor inspection
├── chain-witness.json              # audit-log chain seal at window_start / window_end
├── exceptions.jsonl                # exceptions opened during window + closure refs
├── attestation.txt                 # control-owner signature over manifest.sha256
└── signature.sig                   # ed25519 signature of manifest.json
```

The auditor pulls the pack at one URL:

```
GET /audit/soc2/control/PI1.1?window_start=2026-04-01&window_end=2026-06-30
```

Full schema in `references/completeness-evidence.md`.

## §4 Exception Lifecycle

A gap row opens a `compliance_exceptions` entry (schema in `ai-agent-soc2-controls`). The control owner triages within SLO (critical: 5 business days, high: 10, medium: 20). Closure requires a remediation note + evidence ref. Open exceptions appear in the quarterly attestation pack; the auditor will scope a finding if they exceed SLO.

## §5 Anti-Patterns

- Running the completeness job only at audit time. Detection is too late; gaps cannot be remediated retroactively.
- Defining "approval" purely by row existence. Cryptographic linkage to the chain position is what makes the evidence resistant to backfill.
- Allow-listing approvers from "the current role table." Use the policy version that was active at approval time.
- Treating every `gap_missing` as a critical incident. Some are explicit kill-switch flips with a documented bypass; reclassify those as `bypass_documented` and link to the kill-switch record.
- Sampling 5 approvals. Auditors typically pull 25 minimum per quarter; default to n=200 and let them sample.
- Skipping the chain witness. Without it, an auditor cannot rule out wholesale audit-log rewrite.
