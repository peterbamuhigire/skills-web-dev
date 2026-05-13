> Consolidated from skills/ai-agent-audit-log-integrity/SKILL.md into ai-agent-compliance-controls on 2026-05-13. Load this through skills/ai-agent-compliance-controls/SKILL.md, not as an active skill entrypoint.

# AI Agent Audit Log Integrity
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Building the **action audit log** that records every agent action with tamper-evident integrity (hash chain).
- Designing **retention policies** per event class so financial actions retain 7 years, PHI actions 6 years, baseline 3-7 years.
- Implementing the **nightly integrity verification job** that detects any modification to the chain.
- Building the **export-on-audit-request** endpoint so an auditor can pull a verifiable slice in minutes.
- Wiring **write-once / object-lock storage** for log archives.

## Do Not Use When

- The task is the agent runtime state machine itself — `ai-agent-runtime-architecture`.
- The task is the platform audit log spine — `saas-control-plane-engineering` (this skill extends it for agents).
- The task is the incident evidence bundle — `ai-incident-evidence-capture`.
- The task is the auditor portal UI — `ai-agent-evidence-automation`.

## Required Inputs

- Agent runtime emitting per-step records (`ai-agent-runtime-architecture`).
- Tool catalogue with reversibility classification and data classification (`ai-agent-tool-catalogue-and-action-gating`).
- HSM or KMS for signing (production key).
- Object-lock-capable storage (S3 Object Lock, GCS retention policies, Azure immutable blobs).
- Retention requirements (SOC 2 / ISO / HIPAA / sector / contractual).

## Workflow

1. Read this `SKILL.md`.
2. Design the **action audit log schema** (§1) — hash-chained per row.
3. Implement the **chain emission** (§2) at every state machine transition and tool call.
4. Implement **write-once archival** (§3) — daily seal to object-lock storage.
5. Build the **integrity verification job** (§4) — runs nightly; alerts on any break.
6. Define **retention policies by event class** (§5). Code in `references/retention-policies.md`.
7. Build the **export endpoint** (§6) — return a verifiable slice with chain proof.
8. Apply anti-patterns (§7).

## Quality Standards

- Every action row carries `prev_hash`, `row_hash`, signed daily seal hash.
- A modified row breaks the chain; verification detects within 24 hours.
- Daily seal is signed by the production HSM key; signature retained alongside.
- Retention is enforced by event class, not by age alone (a 7-year financial row cannot be pruned at 3 years just because the SOC 2 window is shorter).
- Object-lock retention is set at write time and cannot be shortened by the application.
- Export endpoint returns a slice **plus** the chain proof: `prev_hash` of first row, `next_hash` of last row, daily seal that contains them.
- Verification job has its own evidence pack (CC7.2 monitoring artefact).

## Anti-Patterns

- Plain `audit_log` table with no chain — any mutation is invisible.
- Hash chain but no daily seal — chain can be replaced wholesale.
- Daily seal but no off-platform replication — same operator can rewrite both.
- Retention by `created_at < 3 years ago → DELETE` ignores event-class retention (HIPAA 6y, financial 7y, EU AI Act high-risk 10y).
- Verification job runs but failure is a Slack message — no alert escalation.
- Export returns the rows but not the proof; auditor cannot verify the slice corresponds to the live chain.
- Action audit log lives in the same DB user as the application; application bug can mutate it.

## Outputs

- Hash-chained action audit schema.
- Chain emission code at every relevant runtime point.
- Daily seal + off-platform replication.
- Integrity verification job + alerting.
- Retention policy YAML by event class.
- Export endpoint with chain proof.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Compliance | Hash-chain design | Markdown + code | `docs/compliance/audit-log-integrity.md` |
| Compliance | Daily seal record | JSON + signature | `evidence/audit/seal/2026-05-11.json` |
| Compliance | Integrity verification report | JSON | `evidence/audit/integrity/2026-05-11.json` |
| Compliance | Retention policy | YAML | `ops/compliance/audit-log-retention.yaml` |
| Compliance | Export proof bundle | tar.gz + manifest + signature | `evidence/audit/export/aud-1234.tar.gz` |

## References

- `references/hash-chain-design.md` — Schema + chain emission code.
- `references/retention-policies.md` — Retention by event class across SOC 2 / ISO / HIPAA / GDPR / financial / EU AI Act.
- `references/integrity-verification-job.md` — Verification job code + alerting wiring.
- Companion: `ai-agent-runtime-architecture`, `ai-agent-tool-catalogue-and-action-gating`, `ai-agent-soc2-controls`, `ai-agent-iso27001-controls`, `ai-agent-hipaa-security-controls`, `ai-agent-evidence-automation`, `saas-control-plane-engineering`.

<!-- dual-compat-end -->

## §1 Schema

```sql
CREATE TABLE agent_action_audit (
  id              BIGINT PRIMARY KEY,
  occurred_at     TIMESTAMP(6) NOT NULL,
  tenant_id       BIGINT NOT NULL,
  actor_type      ENUM('user','agent','system','admin') NOT NULL,
  actor_id        VARCHAR(128) NOT NULL,
  task_id         BIGINT,
  step_index      INT,
  event_class     VARCHAR(64) NOT NULL,          -- e.g. "tool_call", "approval_granted", "kill_switch_flip", "phi_access"
  tool_name       VARCHAR(128),
  tool_version    VARCHAR(32),
  reversibility   ENUM('reversible','irreversible','compensable') ,
  data_class      VARCHAR(32),                   -- "public","internal","confidential","phi","pci"
  phi_flag        BOOLEAN NOT NULL DEFAULT FALSE,
  outcome         ENUM('ok','denied','error') NOT NULL,
  payload_summary JSON NOT NULL,                 -- redacted summary
  payload_ref     VARCHAR(256),                  -- pointer to encrypted full payload in vault
  retention_class VARCHAR(32) NOT NULL,          -- e.g. "soc2_7y","hipaa_6y","financial_7y","eu_aia_10y"
  -- Chain fields
  prev_hash       CHAR(64) NOT NULL,             -- sha256 hex of previous row's row_hash
  row_hash        CHAR(64) NOT NULL,             -- sha256 over canonical(this row excluding row_hash)
  -- Indices
  INDEX idx_task (task_id, step_index),
  INDEX idx_tenant_time (tenant_id, occurred_at),
  INDEX idx_event_class_time (event_class, occurred_at)
);

CREATE TABLE agent_action_audit_seal (
  seal_day        DATE PRIMARY KEY,
  first_row_id    BIGINT NOT NULL,
  last_row_id     BIGINT NOT NULL,
  first_prev_hash CHAR(64) NOT NULL,
  last_row_hash   CHAR(64) NOT NULL,
  seal_hash       CHAR(64) NOT NULL,             -- sha256 over (day, first_row_id, last_row_id, last_row_hash)
  signature       BLOB NOT NULL,                 -- HSM signature over seal_hash
  signing_key_id  VARCHAR(128) NOT NULL,
  sealed_at       TIMESTAMP NOT NULL,
  replicated_to_object_lock_at TIMESTAMP
);
```

The chain is per-tenant **and** global. The global chain provides absolute integrity; the per-tenant chain provides easy export.

## §2 Chain Emission

```python
# audit/log.py
import hashlib, json
from datetime import datetime

def canonical(d: dict) -> bytes:
    return json.dumps(d, sort_keys=True, separators=(",", ":")).encode()

def emit(row: dict) -> int:
    with audit_db.transaction(isolation="serializable"):
        prev = audit_db.scalar(
            "SELECT row_hash FROM agent_action_audit "
            "ORDER BY id DESC LIMIT 1 FOR UPDATE")
        prev_hash = prev or ("0" * 64)
        row["prev_hash"] = prev_hash
        row["occurred_at"] = row.get("occurred_at") or datetime.utcnow().isoformat()
        # Compute row_hash over canonical row, excluding row_hash field
        row_for_hash = {k: v for k, v in row.items() if k != "row_hash"}
        row["row_hash"] = hashlib.sha256(canonical(row_for_hash)).hexdigest()
        new_id = audit_db.execute_insert("agent_action_audit", row)
        return new_id
```

Every relevant runtime point calls `emit`:

| Runtime point | event_class |
|---|---|
| Task created | `task_created` |
| Step `PLANNING` entered | `step_started` |
| LLM call done | `llm_call` |
| Tool call invoked | `tool_call` |
| Approval requested | `approval_requested` |
| Approval granted / rejected | `approval_granted` / `approval_rejected` |
| Action executed (irreversible) | `irreversible_action_executed` |
| Kill-switch flipped | `kill_switch_flip` |
| Task completed / failed / killed | `task_completed` / `task_failed` / `task_killed` |
| PHI read / written / transmitted | `phi_access` / `phi_write` / `phi_transmit` |
| Memory write / erasure | `memory_write` / `memory_erasure` |

Implementation note: serializable isolation prevents two concurrent emitters from both reading the same `prev_hash` and producing a fork.

## §3 Daily Seal + Object-Lock Replication

A nightly job seals the day's rows:

```python
# audit/seal.py
def seal_day(day: date):
    rows = audit_db.fetch(
        "SELECT id, row_hash, prev_hash FROM agent_action_audit "
        "WHERE DATE(occurred_at) = ? ORDER BY id ASC", day)
    if not rows:
        return None
    first = rows[0]; last = rows[-1]
    seal = {
        "seal_day": day.isoformat(),
        "first_row_id": first["id"],
        "last_row_id": last["id"],
        "first_prev_hash": first["prev_hash"],
        "last_row_hash": last["row_hash"],
    }
    seal_hash = sha256_hex(canonical(seal))
    sig = HSM.sign("audit-log-seal-key", bytes.fromhex(seal_hash))
    audit_db.insert("agent_action_audit_seal",
        seal_hash=seal_hash, signature=sig,
        signing_key_id="audit-log-seal-key",
        sealed_at=datetime.utcnow(),
        **seal)
    # Replicate full day's rows + seal to object-lock storage
    ObjectLockArchive.put(
        key=f"audit/{day.isoformat()}.jsonl",
        body=jsonl(rows),
        retention_until=compute_retention(day))
    ObjectLockArchive.put(
        key=f"audit/seal/{day.isoformat()}.json",
        body=json.dumps({**seal, "seal_hash": seal_hash, "signature": sig.hex()}),
        retention_until=compute_retention(day, retention_class="forever"))
```

Object-lock retention is set at write time. The application cannot shorten it.

## §4 Integrity Verification Job

See `references/integrity-verification-job.md` for the full code. The job:

1. Walks the chain from `last_verified_id + 1` to current.
2. Recomputes `row_hash` and confirms `prev_hash` matches the previous row's `row_hash`.
3. Verifies daily seals' signatures.
4. Cross-checks object-lock archive against live DB (row count + hash sample).
5. Emits a verification report; alerts on any break.

## §5 Retention by Event Class

Full table in `references/retention-policies.md`. Summary:

| Event class | Default retention | Driver |
|---|---|---|
| `phi_access` / `phi_write` / `phi_transmit` | 6 years | HIPAA §164.316(b)(2)(i) |
| `irreversible_action_executed` (financial / billing scope) | 7 years | SOX-class financial records |
| `kill_switch_flip` | 7 years | SOC 2 + ISO incident records |
| `memory_erasure` | 7 years | GDPR proof |
| `tool_call` (default) | 3 years | SOC 2 + ISO baseline |
| `task_*` (lifecycle) | 1 year | Operability |
| `eu_aia_high_risk_action` | 10 years | EU AI Act Article 12 |

A row's `retention_class` is set at emission time based on `event_class`, `data_class`, `phi_flag`, and feature classification.

## §6 Export with Chain Proof

```python
# audit/export.py
def export_slice(start: datetime, end: datetime,
                 filters: dict, audit_id: str) -> Path:
    rows = audit_db.fetch_filtered(start, end, filters)
    if not rows:
        return _empty_pack(audit_id)
    # Find the day-seal that contains the first row
    first_seal = SealRegistry.containing(rows[0]["id"])
    last_seal = SealRegistry.containing(rows[-1]["id"])
    proof = {
        "first_row_id": rows[0]["id"],
        "last_row_id": rows[-1]["id"],
        "first_seal": first_seal,
        "last_seal": last_seal,
        "row_count": len(rows),
        "verification_instructions_ref": "ai-agent-audit-log-integrity/references/integrity-verification-job.md",
    }
    pack = EvidencePack(control_id="audit-export", window=(start, end),
                        owner="compliance-lead@example.com")
    pack.add("rows.jsonl", rows)
    pack.add("proof.json", proof)
    pack.add("verification_script.py", _generate_verification_script(rows, proof))
    return pack.sign_and_upload()
```

The verification script is part of the pack; the auditor runs it against `rows.jsonl` and confirms the chain holds and matches the seals.

## §7 Anti-Patterns

- Chain emission outside a serializable transaction — two concurrent writers fork the chain.
- Daily seal computed inside the same DB instance with no off-platform copy. Operator with DB access can rewrite both.
- `prev_hash` stored but never verified. Chain integrity assumed, never proven.
- Retention by age only, no event-class awareness. HIPAA / financial / EU AI Act windows missed.
- Object-lock retention set in the application instead of at storage layer. Bug shortens retention silently.
- Verification job runs but failure is a metric, not a page. Chain breaks go unnoticed.
- Export returns rows alone — auditor cannot prove they were not selected to exclude inconvenient entries.


