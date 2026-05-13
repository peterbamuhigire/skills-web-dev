# Forget-on-Erase Cascade — GDPR / CCPA Through Agent Memory

When a user invokes Article 17 (right to erasure) or CCPA equivalent, the platform-wide cascade (`saas-tenant-data-portability-and-erasure`) reaches AI memory stores via this leaf. This document defines what runs.

## Trigger

The erasure pipeline emits an event:

```json
{
  "event": "erasure.requested",
  "scope": "user",                    // or "tenant"
  "tenant_id": 42,
  "user_id": 17,                      // null when scope=tenant
  "requested_at": "2026-05-11T09:00:00Z",
  "due_by": "2026-06-10T09:00:00Z",   // 30 days
  "case_id": "ERA-2026-0042"
}
```

The agent-memory service subscribes and runs the cascade procedure.

## Cascade Procedure

### Step 1: Short-term memory

```sql
DELETE FROM agent_memory_short
WHERE tenant_id = :tenant AND user_id = :user;
```

Redis ephemeral keys: `DEL memory:short:{conversation_id}` for each of the user's conversations.

### Step 2: Working memory

```sql
DELETE FROM agent_memory_working
WHERE tenant_id = :tenant
  AND user_id   = :user
  AND task_id IN (SELECT id FROM agent_tasks WHERE user_id = :user);
```

### Step 3: Long-term memory

The user's facts AND facts written by the user about others:

```sql
-- facts where the user is the subject
DELETE FROM agent_memory_long
WHERE tenant_id = :tenant AND subject_user_id = :user;

-- facts the user wrote (may concern other entities; policy-driven)
DELETE FROM agent_memory_long
WHERE tenant_id = :tenant AND written_by_user_id = :user
  AND kind IN ('preference','workflow_shortcut');
-- Entity-attribute facts written by the user about other entities are kept;
-- the platform's data is not personal data of the user.
```

Vector store: for every deleted row, delete the embedding by `embedding_id`. Run a verification pass:

```python
def verify_vstore_deletion(deleted_memory_ids):
    for mid in deleted_memory_ids:
        if vstore.exists(mid):
            log_compliance_drift(mid)
            vstore.delete(mid)
```

Drift is logged as a compliance incident.

### Step 4: Conversation history

```sql
DELETE FROM agent_messages
WHERE conversation_id IN (SELECT id FROM agent_conversations WHERE user_id = :user);

DELETE FROM agent_conversations WHERE user_id = :user;
```

### Step 5: Audit log redaction (not deletion)

Audit logs are immutable for SOC2 / compliance reasons. Redact:

```sql
UPDATE agent_memory_audit
SET before = jsonb_redact_user_pii(before, :user),
    after  = jsonb_redact_user_pii(after, :user),
    by_actor = CASE WHEN by_actor = CONCAT('user:', :user) THEN 'tombstone:erased' ELSE by_actor END
WHERE tenant_id = :tenant AND (
    before->>'subject_user_id' = :user::text OR
    after->>'subject_user_id' = :user::text OR
    by_actor = CONCAT('user:', :user)
);
```

`jsonb_redact_user_pii` replaces email, name, phone, address fields with tombstones.

### Step 6: Agent traces and steps

```sql
-- Mark spans for redaction; do not delete (traces are immutable)
UPDATE agent_steps
SET tool_args = jsonb_redact_user_pii(tool_args, :user),
    observation = jsonb_redact_user_pii(observation, :user),
    thought = redact_user_pii_text(thought, :user)
WHERE tenant_id = :tenant
  AND task_id IN (SELECT id FROM agent_tasks WHERE user_id = :user);
```

### Step 7: Fine-tunes / adapters

If the platform has trained a model on tenant data including this user:

```sql
SELECT * FROM ai_fine_tunes
WHERE tenant_id = :tenant
  AND included_user_ids @> ARRAY[:user];
```

For each row, the policy:
- **If the tune is opt-in for the user** and the user has now erased: schedule retraining without the user's data; pin the old tune to deprecation; rotate the gateway pin to the next-best non-tuned model until retraining lands; record the schedule in `ai_fine_tune_retraining_queue`.
- **If the tune cannot be retrained** within the SLA: the platform-wide cascade decides whether to deprecate the tune entirely.

This is a high-impact branch — coordinate with the platform erasure runbook.

### Step 8: Eval datasets and goldens

```sql
DELETE FROM eval_goldens
WHERE tenant_id = :tenant AND sourced_from_user_id = :user;
```

If goldens were derived from the user's traffic, they go too.

### Step 9: Emit completion

```json
{
  "event": "erasure.scope_complete",
  "scope_handler": "agent-memory",
  "tenant_id": 42,
  "user_id": 17,
  "case_id": "ERA-2026-0042",
  "rows_deleted": { "short": 42, "working": 88, "long": 19 },
  "rows_redacted": { "audit": 56, "steps": 244 },
  "vstore_deleted": 19,
  "fine_tune_retraining_scheduled": false,
  "completed_at": "2026-05-12T10:00:00Z"
}
```

The platform aggregates handler completions; the case closes when all handlers report complete and the platform legal team confirms.

## Tenant-Scope Erasure

When the scope is the full tenant (offboarding, dispute):

- All tables: `DELETE WHERE tenant_id = :tenant`.
- Vector store: bulk delete by metadata filter `tenant_id = :tenant`.
- Audit: do not delete; rotate `tenant_id` to a tombstone where required.
- Fine-tunes trained on this tenant's data: deprecate; remove from gateway routing; preserve artifact for legal hold if applicable.
- Memory writes by users in the tenant: same as above.

## "Forget This Fact" (User-Initiated, Single Item)

Distinct from full erasure. The user clicks "Forget" on a memory item:

```python
def forget_memory(memory_id, ctx):
    row = db.get(agent_memory_long, memory_id, tenant_id=ctx.tenant_id)
    if row is None: return not_found()
    audit.write(operation='forget', memory_id=memory_id, by=ctx.user_id, before=row.snapshot())
    vstore.delete(row.embedding_id)
    db.delete(row)
    return ok()
```

No fine-tune retraining is triggered for single-item forgets (too small to matter).

## Verification

After each cascade, run a probe:

```python
def cross_check(user_id, tenant_id):
    # Spot-check that no stray facts remain
    for q in CROSS_CHECK_QUERIES:
        hits = vstore.query(embed(q), filter={"tenant_id": tenant_id, "subject_user_id": user_id})
        assert len(hits) == 0, f"stray memory hits: {hits}"
```

`CROSS_CHECK_QUERIES` is a small set of common patterns ("remember me as", "my preference is", "I work at"). Failures page the compliance on-call.

## Timing

- Synchronous handlers (DB deletes): immediate.
- Vector store deletes: within the provider's API SLA (some providers eventual-consistent; verify within 24h).
- Fine-tune retraining: scheduled, may take days; the user-facing erasure acknowledgement should reflect this (a longer SLA for tunes).

## SOC2 / ISO Evidence

Each cascade leaves an evidence row in `compliance_erasure_events` with:
- `case_id`, `scope`, `target_id`, all step results, `started_at`, `completed_at`, `verified_by`.

This is the artifact auditors look for.
