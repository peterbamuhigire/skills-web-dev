# Integrity Verification Job — Code

The verification job is a daemon that runs nightly (typically 04:00 local), walks the chain from the last-verified point to current, and emits a signed verification report.

---

## 1. Top-Level Driver

```python
# audit/verify.py
from datetime import datetime, timedelta, date

class IntegrityVerifier:
    @classmethod
    def run(cls, window_end: datetime | None = None) -> "VerificationReport":
        window_end = window_end or datetime.utcnow()
        last = VerificationCursor.read()
        start_day = (last["day"] if last else GENESIS_DAY) + timedelta(days=1)
        end_day = window_end.date() - timedelta(days=1)   # only seal-completed days

        report = VerificationReport(started_at=datetime.utcnow(),
                                     start_day=start_day, end_day=end_day)

        try:
            cls._verify_chain(start_day, end_day, report)
            cls._verify_seals(start_day, end_day, report)
            cls._verify_archive_correspondence(start_day, end_day, report)
            cls._verify_retention_compliance(report)
        except ChainBreak as e:
            report.add_chain_break(e)
        except SealBreak as e:
            report.add_seal_break(e)

        report.finished_at = datetime.utcnow()
        report.sign(HSM.signing_key("audit-verifier-key"))
        report.persist()

        if report.has_breaks():
            AlertManager.page(
                severity="critical",
                title="Audit log integrity break detected",
                report_url=report.url,
                runbook="docs/runbooks/audit-log-chain-break.md")
        else:
            VerificationCursor.advance(end_day)

        return report
```

## 2. Chain Walk

```python
    @staticmethod
    def _verify_chain(start_day: date, end_day: date, report):
        expected_prev = SealRegistry.last_row_hash_before(start_day) or ("0" * 64)
        for day in date_range(start_day, end_day):
            rows = audit_db.fetch_all(
                "SELECT * FROM agent_action_audit "
                "WHERE DATE(occurred_at) = ? ORDER BY id ASC",
                day)
            for r in rows:
                if r["prev_hash"] != expected_prev:
                    raise ChainBreak(
                        row_id=r["id"], day=day,
                        expected_prev=expected_prev,
                        actual_prev=r["prev_hash"],
                        reason="prev_hash mismatch")
                recomputed = row_hash_hex(r)
                if r["row_hash"] != recomputed:
                    raise ChainBreak(
                        row_id=r["id"], day=day,
                        expected_row=recomputed,
                        actual_row=r["row_hash"],
                        reason="row_hash mismatch (row modified)")
                expected_prev = r["row_hash"]
            report.record_day(day, row_count=len(rows))
```

## 3. Seal Verification

```python
    @staticmethod
    def _verify_seals(start_day: date, end_day: date, report):
        for day in date_range(start_day, end_day):
            seal = SealRegistry.for_day(day)
            if not seal:
                # No rows that day — acceptable
                if audit_db.scalar(
                    "SELECT COUNT(*) FROM agent_action_audit WHERE DATE(occurred_at) = ?",
                    day) > 0:
                    raise SealBreak(day=day, reason="rows exist but no seal")
                continue
            if not HSM.verify(
                key_id=seal["signing_key_id"],
                payload=bytes.fromhex(seal["seal_hash"]),
                signature=seal["signature"],
            ):
                raise SealBreak(day=day, reason="signature invalid")
            # Cross-check seal vs DB
            db_last = audit_db.scalar(
                "SELECT row_hash FROM agent_action_audit "
                "WHERE DATE(occurred_at) = ? ORDER BY id DESC LIMIT 1", day)
            if db_last != seal["last_row_hash"]:
                raise SealBreak(day=day, reason="last_row_hash mismatch DB vs seal",
                                  seal_last=seal["last_row_hash"],
                                  db_last=db_last)
            report.record_seal(day)
```

## 4. Archive Correspondence

The off-platform archive must contain the same rows the DB does.

```python
    @staticmethod
    def _verify_archive_correspondence(start_day: date, end_day: date, report):
        for day in date_range(start_day, end_day):
            archive_key = f"audit/rows/{day.year:04d}/{day.month:02d}/{day.day:02d}.jsonl"
            archived_rows = ObjectLockArchive.get(archive_key)
            if not archived_rows:
                if audit_db.scalar(
                    "SELECT COUNT(*) FROM agent_action_audit WHERE DATE(occurred_at) = ?",
                    day) > 0:
                    raise ArchiveMissing(day=day)
                continue
            archived_hashes = [_canonical_hash(line) for line in archived_rows]
            db_hashes = audit_db.fetch_column(
                "SELECT row_hash FROM agent_action_audit "
                "WHERE DATE(occurred_at) = ? ORDER BY id ASC", day)
            if archived_hashes != db_hashes:
                raise ArchiveDrift(day=day,
                                    archive_count=len(archived_hashes),
                                    db_count=len(db_hashes))
            report.record_archive(day)
```

## 5. Retention Compliance

```python
    @staticmethod
    def _verify_retention_compliance(report):
        # Rows whose retention has expired but are still present (must be in archive or under legal hold)
        rows = audit_db.fetch_all("""
            SELECT id, occurred_at, retention_class
            FROM agent_action_audit
            WHERE retention_eligible_at < NOW()
              AND archived_at IS NULL
              AND legal_hold = FALSE
            LIMIT 1000
        """)
        report.retention_violations = rows

        # Rows past retention that have been pruned without a corresponding pruning event
        orphans = ArchiveRegistry.orphans()
        report.archive_orphans = orphans
```

## 6. Verification Report

```python
@dataclass
class VerificationReport:
    started_at: datetime
    finished_at: datetime | None = None
    start_day: date | None = None
    end_day: date | None = None
    days_verified: int = 0
    rows_verified: int = 0
    seals_verified: int = 0
    archives_verified: int = 0
    chain_breaks: list[ChainBreak] = field(default_factory=list)
    seal_breaks: list[SealBreak] = field(default_factory=list)
    archive_drift: list = field(default_factory=list)
    retention_violations: list = field(default_factory=list)
    archive_orphans: list = field(default_factory=list)
    signature: bytes | None = None

    def has_breaks(self) -> bool:
        return bool(self.chain_breaks or self.seal_breaks or self.archive_drift)

    def to_dict(self) -> dict:
        return asdict(self)

    def sign(self, key):
        canonical = json.dumps(self.to_dict(), sort_keys=True, default=str).encode()
        self.signature = HSM.sign(key, hashlib.sha256(canonical).digest())

    def persist(self):
        path = EvidenceVault.put(
            key=f"audit/verify/{self.started_at.date().isoformat()}.json",
            body=json.dumps({**self.to_dict(), "signature": self.signature.hex()}),
            retention_class="soc2_iso_7y")
        self.url = path
```

## 7. Alerting Wiring

```yaml
# ops/alerts/audit-integrity.yaml
alerts:
  - name: audit_chain_break
    expr: audit_integrity_verifier_chain_breaks_total > 0
    severity: critical
    page: ciso, sre-oncall
    runbook: docs/runbooks/audit-log-chain-break.md
  - name: audit_seal_break
    expr: audit_integrity_verifier_seal_breaks_total > 0
    severity: critical
    page: ciso, sre-oncall
    runbook: docs/runbooks/audit-log-seal-break.md
  - name: audit_archive_drift
    expr: audit_integrity_verifier_archive_drift_total > 0
    severity: high
    page: platform-eng-oncall
    runbook: docs/runbooks/audit-log-archive-drift.md
  - name: audit_verifier_did_not_run
    expr: time() - audit_integrity_verifier_last_run_timestamp > 36 * 3600
    severity: high
    page: platform-eng-oncall
```

The last alert is critical: if the verifier silently dies, integrity is unchecked. The verifier's heartbeat is itself evidence.

## 8. Auditor-Facing Verification Script

When an auditor pulls an export, the script in the pack runs the same chain walk locally:

```python
# evidence/audit/export/aud-1234/verify.py
"""Auditor-runnable verification script.

Verifies the included rows.jsonl chain is well-formed and matches the included proof.
Does NOT require access to production systems.
"""

import json, hashlib, sys
from pathlib import Path

CHAIN_FIELDS = [...]   # copy from audit/hash.py

def row_hash_hex(r):
    return hashlib.sha256(json.dumps(
        {k: r.get(k) for k in CHAIN_FIELDS},
        sort_keys=True, separators=(",", ":"), default=str
    ).encode()).hexdigest()

def main():
    rows = [json.loads(line) for line in Path("rows.jsonl").read_text().splitlines()]
    proof = json.loads(Path("proof.json").read_text())
    expected_prev = rows[0]["prev_hash"]
    for r in rows:
        if r["prev_hash"] != expected_prev:
            print(f"FAIL: chain break at {r['id']}"); sys.exit(2)
        if r["row_hash"] != row_hash_hex(r):
            print(f"FAIL: row_hash mismatch at {r['id']}"); sys.exit(2)
        expected_prev = r["row_hash"]
    if expected_prev != proof["last_seal"]["last_row_hash"]:
        print("FAIL: last row does not match seal"); sys.exit(2)
    # Signature verification using the platform-published public key (in pack)
    pub = Path("platform-pubkey.pem").read_bytes()
    sig = bytes.fromhex(proof["last_seal"]["signature"])
    payload = bytes.fromhex(proof["last_seal"]["seal_hash"])
    if not verify_sig(pub, payload, sig):
        print("FAIL: seal signature invalid"); sys.exit(2)
    print(f"OK: {len(rows)} rows verified; seal valid.")

if __name__ == "__main__":
    main()
```

This is the auditor's offline proof. They run it without your production access. The pack carries the platform's published verification key (separate from the signing key) so the auditor can verify without trusting your infrastructure.

## 9. Recovery Procedure on Break

A real chain break is severity-critical. The runbook (`docs/runbooks/audit-log-chain-break.md`):

1. Page CISO + CTO.
2. Freeze audit log writes (kill-switch on emission).
3. Acquire the off-platform archive copy.
4. Identify the modified row(s) by comparing DB vs archive.
5. Investigate (mis-deploy, malicious actor, storage corruption).
6. If malicious: incident response, regulator notification.
7. Re-emit corrupted rows with `prev_hash` referencing archive truth; record the recovery in the chain itself.

The recovery itself is auditable. The chain heals forward; the historical break is permanent in the record.
