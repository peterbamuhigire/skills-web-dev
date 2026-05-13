# Hash-Chain Design — Engineering Reference

Full implementation of the tamper-evident action audit log.

---

## 1. Goals

- A modification to any historical row is detected within 24 hours (verification job cadence).
- The chain cannot be re-written wholesale (daily seal + off-platform replication).
- Two concurrent emitters cannot fork the chain (serializable isolation).
- A slice can be exported with a portable proof the auditor can verify offline.

## 2. Per-Row Hashing

```python
# audit/hash.py
import hashlib, json

CHAIN_FIELDS = (
    "id", "occurred_at", "tenant_id",
    "actor_type", "actor_id",
    "task_id", "step_index",
    "event_class", "tool_name", "tool_version",
    "reversibility", "data_class", "phi_flag",
    "outcome", "payload_summary", "payload_ref",
    "retention_class", "prev_hash",
)

def row_hash_bytes(row: dict) -> bytes:
    canonical = json.dumps(
        {k: row.get(k) for k in CHAIN_FIELDS},
        sort_keys=True, separators=(",", ":"),
        default=str
    ).encode()
    return hashlib.sha256(canonical).digest()

def row_hash_hex(row: dict) -> str:
    return row_hash_bytes(row).hex()
```

`payload_summary` is a **redacted** JSON object; the full unredacted payload lives encrypted at `payload_ref` in the vault. The chain commits to the redacted summary so chain verification does not require unsealing PHI / PII.

## 3. Emission

```python
# audit/emit.py
from datetime import datetime
from contextlib import contextmanager

@contextmanager
def serializable_tx():
    with audit_db.connection() as cn:
        cn.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
        try:
            yield cn
            cn.commit()
        except Exception:
            cn.rollback()
            raise

def emit(row: dict) -> int:
    if "occurred_at" not in row:
        row["occurred_at"] = datetime.utcnow().isoformat()
    with serializable_tx() as cn:
        prev = cn.fetchone(
            "SELECT row_hash FROM agent_action_audit "
            "ORDER BY id DESC LIMIT 1 FOR UPDATE"
        )
        row["prev_hash"] = (prev or {}).get("row_hash") or ("0" * 64)
        # Reserve id (auto-increment) and compute hash with id included
        new_id = cn.execute_insert_returning_id(
            "agent_action_audit",
            {**row, "row_hash": "<pending>"}
        )
        row["id"] = new_id
        rh = row_hash_hex(row)
        cn.execute("UPDATE agent_action_audit SET row_hash = ? WHERE id = ?",
                    rh, new_id)
        return new_id
```

Note: because `row_hash` depends on `id` (we want the id in the chain so a row insert that mis-orders ids is detectable), we insert with a placeholder and then update. The serializable lock on the previous row prevents another emitter from seeing a partially-committed state.

Alternative (slightly stronger): allocate the id from a sequence ahead of the insert, build the row including id, compute hash, then insert atomically.

```python
def emit_seq(row: dict) -> int:
    with serializable_tx() as cn:
        prev = cn.fetchone(
            "SELECT row_hash FROM agent_action_audit "
            "ORDER BY id DESC LIMIT 1 FOR UPDATE")
        new_id = cn.scalar("SELECT nextval('agent_action_audit_id_seq')")
        row["id"] = new_id
        row["prev_hash"] = (prev or {}).get("row_hash") or ("0" * 64)
        row["row_hash"] = row_hash_hex(row)
        cn.execute_insert("agent_action_audit", row)
        return new_id
```

## 4. Retention Class Assignment

```python
# audit/retention.py
def retention_class_for(event: dict) -> str:
    if event.get("phi_flag"):
        return "hipaa_6y"
    if event["event_class"] == "kill_switch_flip":
        return "soc2_iso_7y"
    if event["event_class"] in ("irreversible_action_executed", "approval_granted"):
        if event.get("data_class") in ("financial", "billing", "pci"):
            return "financial_7y"
    if event["event_class"] == "memory_erasure":
        return "erasure_proof_7y"
    if event.get("feature_risk_class") == "eu_aia_high_risk":
        return "eu_aia_10y"
    return "soc2_baseline_3y"
```

Default is the longest applicable. Application cannot shorten; can only extend.

## 5. Daily Seal

```python
# audit/seal.py
from datetime import date

def seal_day(day: date) -> dict | None:
    rows = audit_db.fetch_all(
        "SELECT id, row_hash, prev_hash FROM agent_action_audit "
        "WHERE DATE(occurred_at) = ? ORDER BY id ASC", day)
    if not rows:
        return None
    first, last = rows[0], rows[-1]
    seal = {
        "seal_day": day.isoformat(),
        "first_row_id": first["id"],
        "last_row_id": last["id"],
        "first_prev_hash": first["prev_hash"],
        "last_row_hash": last["row_hash"],
        "row_count": len(rows),
    }
    seal_hash = hashlib.sha256(
        json.dumps(seal, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    sig = HSM.sign("audit-log-seal-key", bytes.fromhex(seal_hash))

    audit_db.execute_insert("agent_action_audit_seal", {
        **seal,
        "seal_hash": seal_hash,
        "signature": sig,
        "signing_key_id": "audit-log-seal-key",
        "sealed_at": datetime.utcnow(),
    })

    # Off-platform: object-lock archive + cloud-cross-region copy
    ObjectLockArchive.put(
        bucket="evidence-vault-primary",
        key=f"audit/seal/{day.isoformat()}.json",
        body=json.dumps({**seal, "seal_hash": seal_hash, "signature": sig.hex()}),
        retention_until=compute_retention_for_seal(day))
    ObjectLockArchive.put(
        bucket="evidence-vault-secondary-region",
        key=f"audit/seal/{day.isoformat()}.json",
        body=json.dumps({**seal, "seal_hash": seal_hash, "signature": sig.hex()}),
        retention_until=compute_retention_for_seal(day))

    return seal
```

Compute retention for seal = max retention class in the day's rows (default `forever` for evidence vault practical purposes).

## 6. Off-Platform Cross-Region

The seal is replicated to a different region and (where the regulator requires) a different cloud provider. A platform-wide compromise that wipes the primary cannot wipe the seal.

## 7. Chain Genesis

The first row in the chain has `prev_hash = "0" * 64`. The genesis is also sealed and archived; the system bootstraps with the genesis seal already in the off-platform store. Auditor verifies all subsequent seals chain back to genesis.

## 8. Schema for Off-Platform Storage

Object key convention:

```
s3://evidence-vault/{environment}/audit/
  rows/YYYY/MM/DD.jsonl              -- one file per day, full row payload (redacted summary)
  seal/YYYY-MM-DD.json               -- the seal record + signature
  genesis.json                        -- one-time genesis seal
```

Object-lock retention: governance mode for the production environment, with retention-until set per day's max retention class.

## 9. Verification — Outline

(Full verification job in `integrity-verification-job.md`.)

```python
def verify_chain(start_day, end_day):
    expected_prev = SealRegistry.last_row_hash_before(start_day) or ("0" * 64)
    for day in date_range(start_day, end_day):
        rows = audit_db.fetch_all(
            "SELECT * FROM agent_action_audit WHERE DATE(occurred_at) = ? ORDER BY id ASC",
            day)
        for r in rows:
            if r["prev_hash"] != expected_prev:
                raise ChainBreak(at=r["id"], expected_prev=expected_prev,
                                  actual_prev=r["prev_hash"])
            if r["row_hash"] != row_hash_hex(r):
                raise ChainBreak(at=r["id"], reason="row_hash mismatch")
            expected_prev = r["row_hash"]
        # Verify seal
        seal = SealRegistry.for_day(day)
        if seal:
            if not HSM.verify("audit-log-seal-key", seal["seal_hash"], seal["signature"]):
                raise SealBreak(day=day, reason="signature invalid")
            if seal["last_row_hash"] != expected_prev:
                raise SealBreak(day=day, reason="last_row_hash mismatch")
```

## 10. Performance Notes

- High-volume runtimes can shard the chain by tenant (a per-tenant chain) and roll a global chain over the per-tenant sealed days. This keeps the serializable lock contention per-tenant.
- Sample rate is **not** applicable — every action is chained. If volume requires reduction, sample at the `payload_summary` size (truncate large args; reference vault for full).
- Daily seal runs in a maintenance window (off-peak). Verification job runs after seal.

## 11. Key Custody

- `audit-log-seal-key` lives in the production HSM. Access is split between two custodians (CISO and CTO); both required to rotate.
- Signature verification key is published in the auditor portal so the auditor can verify seals offline.
- Key rotation: every 2 years; old key retained for verification of historical seals.
