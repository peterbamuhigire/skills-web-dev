---
name: ai-agent-memory-erasure-proof
description: Use when proving agent-memory erasure was complete and verifiable for GDPR / CCPA / POPIA / KE DPA requests — the 9-step cascade verification job emits a signed-off evidence pack. Pairs with `ai-agent-memory` (three-tier memory + erasure cascade) and `saas-tenant-data-portability-and-erasure` (tenant-level erasure pipeline).
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# AI Agent Memory Erasure Proof

## Operating contract

## Inputs

| Input | Required | Purpose |
|---|---|---|
| Domain evidence | yes | verified subject or tenant scope, legal request, memory-store inventory, retention exceptions, and deletion job identifiers |

## Outputs

- Produce: store-by-store erasure verdict, residual-data exceptions, independent verification result, and signed proof pack.

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

- A data subject (or controller on their behalf) submits an erasure request under **GDPR Art. 17**, **CCPA / CPRA**, **POPIA s.24**, **KE DPA s.40** that includes agent-derived memory (working / episodic / semantic / vectors / fine-tune corpora).
- Proving end-to-end that the **9-step cascade** ran to completion and that **no residue remains** in any tier, any replica, any backup index, any vector store, any subprocessor cache.
- Producing a **signed proof-of-erasure** artefact the data subject's controller (or regulator) can verify offline.
- Closing the loop between `ai-agent-memory` (which performs the cascade) and the compliance evidence pipeline.

## Do Not Use When

- Designing the **memory tiers** themselves — `ai-agent-memory`.
- Designing the **tenant-level erasure orchestrator** (whole tenant erasure) — `saas-tenant-data-portability-and-erasure`.
- Drafting the **policy / DPIA** — SRS engine.
- Erasing **action audit log** entries — those have a separate **redaction** flow (audit log is retained per regulatory minima with PII redaction, not deleted).

## Required Inputs

- Erasure request envelope: `request_id`, `subject_id`, `tenant_id`, `data_classes ⊆ {working,episodic,semantic,vectors,fine_tune,uploads,derivatives}`, `legal_basis` (regulation citation), `received_at`, `requester_identity_proof_ref`.
- Memory tier catalogue with **storage locator** for each tier (DB tables, object stores, vector indexes, LLM-provider knowledge-base IDs, fine-tune model IDs).
- Subprocessor inventory with **erasure-API surface** (which subprocessors hold subject data and how to delete from each).
- Hash-chained action audit log (so the cascade itself is recorded as `event_class=erasure_step`).

## Workflow

1. Read this `SKILL.md`.
2. **Receive** the request, validate identity, record `subject_id → erasure_request_id` on the action audit log (§1).
3. Run the **9-step cascade** (§2) — each step writes a step record, calls the underlying tier API, and emits a verification probe.
4. After the cascade, run the **verification job** (§3) — probes every tier (and subprocessors) for residue using the deterministic subject fingerprint.
5. Produce the **proof-of-erasure pack** (§4) — signed, hash-chained, includes step records + verification results.
6. **Notify** the requester with the pack reference and the `verified_at` timestamp; honour the regulatory clock (GDPR: 1 month, CCPA: 45 days, POPIA / KE DPA: "without undue delay").
7. **Retain the proof** for the retention class (minimum 6 years; longer in HIPAA-adjacent contexts) — the request and the proof are evidence, the underlying data is gone.
8. Apply anti-patterns (§5).

## Quality Standards

- The 9 steps are **idempotent** — re-running the cascade is safe and emits identical results.
- Each step record carries **before / after fingerprints** so the auditor can verify the deletion observably reduced the search space.
- Verification probes are **independent** of the deletion path (different code, different storage handles).
- **Subprocessor receipts** are stored alongside the proof (LLM provider deletion ticket IDs, vector-store deletion confirmations).
- **No silent failures** — a step that cannot complete (e.g. fine-tune model still in use) opens a regulator-grade exception within SLO.
- The proof is **portable** — the requester / their controller / a regulator can verify the signature without our platform.

## Anti-Patterns

- Soft-delete with a `deleted_at` flag in the memory table. Not erasure; data still recoverable.
- Vector store deletion via "remove from index" without confirming the underlying record was purged. ANN indexes often retain shards.
- Fine-tune corpora deleted from source but the fine-tuned model retained. The model itself contains the data; either retrain or document why retention is lawful (Art. 17(3) exception with documented justification).
- Subprocessor "we deleted it" e-mail. Need an API confirmation with a ticket ID stored in the proof.
- Erasing the action audit log entries about the subject. The audit log is retained with PII redacted; deleting it destroys evidence that the erasure happened.
- Single-tier erasure (e.g. only working memory) without checking the others. Episodic and semantic often contain reconstructions of the same subject.
- Pack signed by the engineer who ran the cascade. Segregation-of-duties failure; sign by a separate compliance owner.

## Outputs

- `erasure_requests` table + step-by-step `erasure_steps` table.
- 9-step cascade orchestrator (Python).
- Independent verification job (Python).
- Signed proof-of-erasure pack format.
- Subprocessor receipt collator.
- Auditor portal endpoint.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Data safety | Erasure request record | DB row + JSON snapshot | `evidence/erasure/{request_id}/request.json` |
| Data safety | Step records (×9) | JSONL | `.../steps.jsonl` |
| Data safety | Verification probe results | JSON | `.../verification.json` |
| Data safety | Subprocessor receipts | JSONL | `.../subprocessor-receipts.jsonl` |
| Data safety | Proof-of-erasure pack | tar.gz + signature | `.../proof.tar.gz` |
| Data safety | Audit-log redaction record | JSON | `.../audit-log-redaction.json` |

## References

- `references/erasure-verification-job.md` — Full Python implementation of the cascade orchestrator + independent verification job + proof pack writer.
- Companions: `ai-agent-memory` (the cascade implementer), `saas-tenant-data-portability-and-erasure` (tenant-level), `ai-agent-audit-log-integrity` (redaction not deletion), `ai-agent-evidence-automation` (pack pipeline), `ai-agent-hipaa-security-controls` (PHI agent erasure constraints), `uganda-dppa-compliance` (KE / UG specifics), `ai-agent-soc2-controls` (C1.2, P5).

<!-- dual-compat-end -->

## §1 Intake

```python
# privacy/erasure/intake.py
from dataclasses import dataclass
from datetime import datetime, timedelta

REGULATORY_CLOCKS = {
    "GDPR":  timedelta(days=30),
    "CCPA":  timedelta(days=45),
    "POPIA": timedelta(days=30),    # "reasonable time" — internally bound to 30
    "KE_DPA": timedelta(days=30),
}

@dataclass
class ErasureRequest:
    request_id: str
    tenant_id: str
    subject_id: str
    data_classes: list[str]
    legal_basis: str
    received_at: datetime
    requester_identity_proof_ref: str
    sla_deadline: datetime

def accept(request: dict) -> ErasureRequest:
    req = ErasureRequest(
        request_id=request["request_id"],
        tenant_id=request["tenant_id"],
        subject_id=request["subject_id"],
        data_classes=request.get("data_classes", ["working","episodic","semantic","vectors","fine_tune","uploads","derivatives"]),
        legal_basis=request["legal_basis"],
        received_at=datetime.fromisoformat(request["received_at"]),
        requester_identity_proof_ref=request["requester_identity_proof_ref"],
        sla_deadline=datetime.fromisoformat(request["received_at"]) + REGULATORY_CLOCKS[request["legal_basis"]],
    )
    audit.emit(event_class="erasure_request_accepted",
               subject_id=req.subject_id, request_id=req.request_id,
               legal_basis=req.legal_basis, sla_deadline=req.sla_deadline.isoformat())
    return req
```

## §2 The 9-Step Cascade

| # | Step | Tier / Action |
|---|---|---|
| 1 | Working memory | Wipe in-flight session state for subject. |
| 2 | Episodic memory | Delete subject-tagged rows in episodic store; verify replication lag drained. |
| 3 | Semantic memory | Delete subject-attributed nodes; rebuild affected entity graph. |
| 4 | Vector store | Delete vectors by subject metadata; rebuild affected ANN shards. |
| 5 | Fine-tune corpora | Delete subject-attributed examples from training datasets; record affected model lineage. |
| 6 | Uploads / artefacts | Delete object-store blobs (with replicas across regions). |
| 7 | Derivatives | Delete embeddings, summaries, indexes derived from subject data. |
| 8 | Subprocessors | Issue delete API calls to LLM provider knowledge bases, vector-store SaaS, fine-tune providers; collect receipts. |
| 9 | Audit-log redaction | **Redact** (not delete) PII fields in action audit log entries; preserve hashes and chain. |

```python
# privacy/erasure/cascade.py
from datetime import datetime
import hashlib, json

CASCADE = [
    ("working",     wipe_working_memory),
    ("episodic",    delete_episodic),
    ("semantic",    delete_semantic),
    ("vectors",     delete_vectors),
    ("fine_tune",   purge_finetune_corpora),
    ("uploads",     delete_uploads),
    ("derivatives", delete_derivatives),
    ("subprocessor", delete_at_subprocessors),
    ("audit_log",   redact_audit_log),
]

def run_cascade(req: ErasureRequest) -> list[dict]:
    fp_before = subject_fingerprint(req)
    steps: list[dict] = []
    for name, fn in CASCADE:
        if name not in req.data_classes and name != "audit_log":  # audit_log always redacted
            continue
        rec = {"step": name, "started_at": datetime.utcnow().isoformat()}
        before = fp_before[name]
        try:
            out = fn(req)
            after = probe_residue(req, tier=name)
            rec.update({"status": "ok", "before_count": before, "after_count": after, "output": out})
        except Exception as e:
            rec.update({"status": "fail", "error": str(e)})
        rec["ended_at"] = datetime.utcnow().isoformat()
        steps.append(rec)
        audit.emit(event_class="erasure_step",
                   subject_id=req.subject_id, request_id=req.request_id, step=name,
                   status=rec["status"], after_count=rec.get("after_count"))
    return steps
```

`subject_fingerprint(req)` returns per-tier residue counts **before** the cascade, so the proof shows before / after.

Full per-step implementations and the residue probes are in `references/erasure-verification-job.md`.

## §3 Independent Verification Job

The verification job is a **separate code path** that re-queries every tier (and subprocessors) using a freshly-resolved subject fingerprint and asserts residue is zero.

```python
# privacy/erasure/verify.py
def verify(req: ErasureRequest) -> dict:
    probes = {
        "working":     probe_working_memory(req),
        "episodic":    probe_episodic(req),
        "semantic":    probe_semantic(req),
        "vectors":     probe_vectors(req),
        "fine_tune":   probe_finetune(req),
        "uploads":     probe_uploads(req),
        "derivatives": probe_derivatives(req),
        "subprocessor": probe_subprocessors(req),
        "audit_log_redacted": probe_audit_log_redaction(req),
    }
    all_clear = all(v["residue"] == 0 for k, v in probes.items() if k != "audit_log_redacted") and probes["audit_log_redacted"]["unredacted_pii_count"] == 0
    return {"verified_at": datetime.utcnow().isoformat(), "all_clear": all_clear, "probes": probes}
```

If `all_clear == False`, the erasure is **not complete**; an exception opens and the requester is **not** notified yet.

## §4 Proof-of-Erasure Pack

```
evidence/erasure/{request_id}/
├── manifest.json
├── request.json                 # the validated ErasureRequest
├── steps.jsonl                  # one row per cascade step
├── verification.json            # the verification probe results
├── subprocessor-receipts.jsonl  # API ticket IDs per subprocessor
├── audit-log-redaction.json     # the redaction range + chain witness
├── attestation.txt              # signed by DPO (not the cascade runner)
└── signature.sig
```

Sample `manifest.json`:

```json
{
  "pack_id": "erasure-req-001928",
  "request_id": "req-001928",
  "subject_id": "sub_5e3a... (hashed)",
  "tenant_id": "ten_0440",
  "legal_basis": "GDPR",
  "received_at": "2026-04-20T09:11:00Z",
  "completed_at": "2026-04-22T15:44:00Z",
  "sla_deadline": "2026-05-20T09:11:00Z",
  "all_clear": true,
  "signer": "dpo@example.com",
  "signature_key_id": "compliance-dpo-2026",
  "files": [...]
}
```

## §5 Anti-Patterns

- Soft-delete (`deleted_at` flag) — not erasure under GDPR/CCPA/POPIA/KE DPA.
- Vector "remove from index" without underlying record purge.
- Deleting fine-tune corpora but keeping the fine-tuned model. Either retrain or document a lawful retention basis (Art. 17(3)).
- "Deletion confirmed via email" from a subprocessor. Require API confirmation with ticket ID.
- Deleting audit log rows. Redact PII; keep the chain.
- Verification done by the same code path as the cascade. Independent probes are required.
- Pack signed by the engineer who ran the cascade. Sign by an independent DPO.
- Re-running the cascade is unsafe (non-idempotent). Each step must tolerate replay.
- Not capturing the subprocessor receipts. The auditor will ask for them; verbal assurance does not pass.

## §6 Cross-Links

- **`ai-agent-memory`** — implements the actual tier deletes; this skill consumes those.
- **`saas-tenant-data-portability-and-erasure`** — whole-tenant erasure orchestrator; references this skill for the agent-memory leg.
- **`ai-agent-audit-log-integrity`** — defines the PII redaction (not deletion) flow for the audit log; redaction record is part of the proof.
- **`ai-agent-soc2-controls`** — C1.2 (confidential information disposal), P5 (retention and disposal).
- **`ai-agent-hipaa-security-controls`** — additional constraints when subject is a patient (BAA / 164.310(d)(2)(i) media disposal).
- **`uganda-dppa-compliance`** — KE / UG specifics for `legal_basis ∈ {KE_DPA, UG_DPPA}`.
