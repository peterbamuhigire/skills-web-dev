# Retention Policies by Event Class

The audit log retains different event classes for different windows. Retention is enforced at storage layer (object-lock) and reconciled by the verification job.

---

## 1. Retention Classes (Authoritative Table)

| Class | Minimum Retention | Driver | Notes |
|---|---|---|---|
| `hipaa_6y` | 6 years | HIPAA §164.316(b)(2)(i) | PHI events; clock starts later of date created or last in effect |
| `financial_7y` | 7 years | SOX, IRS, sector financial | Irreversible financial actions; jurisdictional max |
| `soc2_iso_7y` | 7 years | SOC 2 historical + ISO 27001 | Kill-switch flips, incident records, approval grants |
| `erasure_proof_7y` | 7 years | GDPR Art. 5(2) accountability | Proof of erasure must survive longer than erased data |
| `eu_aia_10y` | 10 years | EU AI Act Art. 12 record-keeping | High-risk AI systems |
| `soc2_baseline_3y` | 3 years | SOC 2 Type II + 1 buffer year | Default for non-sensitive |
| `operational_1y` | 1 year | Operability only | Lifecycle events without compliance burden |
| `legal_hold` | indefinite | Litigation hold | Overrides scheduled retention; flag on the row |

## 2. Assignment Logic

`retention_class` is assigned at emission time and **immutable thereafter**.

```python
def assign_retention(event: dict, feature: AgentFeature) -> str:
    if event.get("legal_hold"):
        return "legal_hold"
    if feature.eu_aia_risk_class == "high_risk":
        return "eu_aia_10y"
    if event.get("phi_flag"):
        return "hipaa_6y"
    ec = event["event_class"]
    if ec == "kill_switch_flip":
        return "soc2_iso_7y"
    if ec == "memory_erasure":
        return "erasure_proof_7y"
    if ec == "irreversible_action_executed":
        dc = event.get("data_class")
        if dc in ("financial", "billing", "pci"):
            return "financial_7y"
        return "soc2_iso_7y"
    if ec in ("approval_granted", "approval_rejected"):
        return "soc2_iso_7y"
    if ec in ("task_completed", "task_failed", "step_started"):
        return "operational_1y"
    return "soc2_baseline_3y"
```

## 3. Storage Layer Enforcement

Object-lock retention is set at PUT time based on the row's `retention_class`:

```python
RETENTION_DAYS = {
    "operational_1y":   365,
    "soc2_baseline_3y": 365 * 3,
    "hipaa_6y":          365 * 6,
    "soc2_iso_7y":       365 * 7,
    "financial_7y":      365 * 7,
    "erasure_proof_7y":  365 * 7,
    "eu_aia_10y":        365 * 10,
    "legal_hold":        365 * 100,    # effectively indefinite; lifted by legal action only
}

def compute_retention_for_seal(day: date) -> datetime:
    rows = audit_db.fetch_all(
        "SELECT retention_class FROM agent_action_audit WHERE DATE(occurred_at) = ?",
        day)
    max_days = max(RETENTION_DAYS[r["retention_class"]] for r in rows)
    return datetime.combine(day, time.min) + timedelta(days=max_days)
```

Daily archive object inherits the **maximum** retention of any row that day. The seal is retained indefinitely.

## 4. Legal Hold

A litigation hold sets `legal_hold=True` on a row (or set of rows) and overrides scheduled retention. Removal of legal hold requires a counter-event in the audit log itself (chain-of-custody).

```sql
CREATE TABLE legal_holds (
  id              BIGINT PRIMARY KEY,
  matter_id       VARCHAR(64) NOT NULL,
  matter_name     VARCHAR(256),
  predicate       JSON NOT NULL,         -- e.g. {"tenant_id":42, "occurred_at":[start,end]}
  applied_at      TIMESTAMP NOT NULL,
  applied_by      VARCHAR(128) NOT NULL,
  applied_reason  TEXT,
  released_at     TIMESTAMP,
  released_by     VARCHAR(128),
  released_reason TEXT,
  status          ENUM('active','released') NOT NULL
);
```

Rows under an active hold cannot be archived to lower-retention tiers.

## 5. Pruning Procedure

Rows past their retention are **not** deleted from the live database silently. The procedure is:

1. Mark rows with `pruning_eligible_at <= NOW()`.
2. Run the verification job over the affected day(s) to confirm the chain.
3. Emit a `retention_pruning` event into the audit log (chain entry).
4. Archive the rows to a long-term-cold tier; remove from hot DB.
5. The seal remains in the off-platform vault; rows are recoverable from the archive if needed.

The chain remains intact because `prev_hash` of post-prune rows still references the row_hash of (now archived) prior rows.

## 6. Cross-Regulator Application

When multiple regulators apply (HIPAA + EU AI Act + SOC 2), retention is the **maximum** of applicable windows.

| Scenario | Effective Retention |
|---|---|
| Clinical chatbot (HIPAA + EU AI Act high-risk) | 10 years (`eu_aia_10y`) |
| Financial agent (SOC 2 + SOX) | 7 years |
| Clinical agent without EU exposure (HIPAA only) | 6 years |
| Memory erasure proof | 7 years (GDPR Art 5(2)) |

## 7. Customer-Initiated Retention Overrides

Some enterprise tenants demand specific retention (e.g. 10 years on all their data for sector reasons). Tenant-level retention is captured at the row level via `retention_class_override`:

```sql
ALTER TABLE agent_action_audit
  ADD COLUMN retention_class_override VARCHAR(32);
```

`effective_retention = max(retention_class, retention_class_override)`. Tenants cannot shorten retention below the regulatory floor.

## 8. Evidence

Quarterly retention report:

```python
# compliance/collectors/retention.py
class RetentionCollector(EvidenceCollector):
    control_id = "retention"
    name = "Audit log retention enforcement"
    cadence = "0 5 1 */3 *"

    def gather(self, start, end):
        return {
            "retention_by_class.json": audit_db.scalar_sql("""
                SELECT retention_class, COUNT(*) AS rows,
                       MIN(occurred_at) AS oldest,
                       MAX(occurred_at) AS newest
                FROM agent_action_audit GROUP BY retention_class"""),
            "object_lock_attestation.json": ObjectLockArchive.attestation(),
            "pruning_events_in_window.jsonl": audit_db.fetch_filtered_query(
                "event_class = 'retention_pruning'", start, end),
            "legal_holds_active.csv": LegalHold.active(),
        }
```
