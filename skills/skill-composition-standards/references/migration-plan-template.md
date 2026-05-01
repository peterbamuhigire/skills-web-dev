# Migration Plan Template

Produced by `database-design-engineering` or `deployment-release-engineering`. Consumed by the deployer and reviewed by DBA.

## Template

```markdown
# Migration plan — <change description>

**Owner:** <name>
**Linked release plan:** <path>
**DB:** <engine + version>
**Target schema version:** NNNN

## Summary

<One paragraph: what is changing and why.>

## Strategy

- **Pattern:** additive-only | expand-contract | online-schema-change | destructive (avoid)
- **Lock behaviour:** non-blocking | brief lock (< 500ms) | long lock (> 500ms, requires maintenance window)
- **Rollback mechanism:** revert migration | forward-fix only | restore from snapshot

## Sequenced steps

### Phase 1 — Expand (add new, keep old)

Migration file: `0042_add_order_status_v2.sql`

```sql
-- Add new column without dropping or modifying old
ALTER TABLE orders ADD COLUMN status_v2 text;
UPDATE orders SET status_v2 = CASE status
  WHEN 'created' THEN 'pending'
  WHEN 'paid' THEN 'confirmed'
  ELSE status
END;
CREATE INDEX CONCURRENTLY idx_orders_status_v2 ON orders(tenant_id, status_v2);
```

**Lock assessment:** `ALTER TABLE ADD COLUMN` without default = instant metadata change on Postgres 11+. `UPDATE` runs in batches of 10,000 to avoid long transaction. `CREATE INDEX CONCURRENTLY` non-blocking.

**Verification after phase 1:**

- Row count `status_v2 IS NOT NULL` = total row count.
- Index exists: `SELECT * FROM pg_indexes WHERE indexname = 'idx_orders_status_v2';`

### Phase 2 — Dual-write (code update)

Deploy application version that reads old, writes both.

**Verification after phase 2:**

- All rows created in last 24h have both `status` and `status_v2` populated and consistent.

### Phase 3 — Read switch

Deploy application version that reads new, writes both.

**Verification:** application logs show reads from `status_v2`.

### Phase 4 — Contract (drop old)

Migration file: `0043_drop_order_status_old.sql`

```sql
ALTER TABLE orders DROP COLUMN status;
```

**Only after:** phase 3 has been deployed for at least 1 week with no rollback.

## Online-safe guarantees

Verify for every operation:

- [ ] `ALTER TABLE ADD COLUMN` without `NOT NULL` default — instant
- [ ] `ALTER TABLE ADD COLUMN ... DEFAULT ...` — instant on PG 11+, not MySQL < 8
- [ ] `CREATE INDEX CONCURRENTLY` (Postgres) or `ALGORITHM=INPLACE` (MySQL) used
- [ ] No `ALTER COLUMN TYPE` on large tables without a rewrite strategy
- [ ] No `DROP COLUMN` while application still reads it

## Forbidden without maintenance window

- Rewriting a large table (>10M rows) synchronously
- Adding a `NOT NULL` column with no default to a large table
- Changing a column type in a way that requires a table scan
- Adding a foreign key on a large table without `NOT VALID + VALIDATE CONSTRAINT` staging

## Rollback

- Phase 1 rollback: `DROP COLUMN status_v2; DROP INDEX idx_orders_status_v2;` — safe.
- Phase 2 rollback: revert code deploy; data still dual-written.
- Phase 3 rollback: revert code deploy (reads old again).
- Phase 4 rollback: **not possible** without restore. Only advance to phase 4 after week-long soak.

## Pre-migration checklist

- [ ] Staging has been migrated successfully
- [ ] Staging has prod-scale data (or test with pg_restore of recent snapshot)
- [ ] Production snapshot taken with name `pre-<change>-<date>`
- [ ] DBA reviewed and approved
- [ ] On-call paged (informational) with migration window

## Post-migration verification

- [ ] Schema version recorded in `schema_migrations`
- [ ] Query performance baseline unchanged (compare p95 from last 24h vs next 24h)
- [ ] No elevated error rate
- [ ] No lock contention alerts

## Revision log

| Date | Change | Author |
|---|---|---|
| YYYY-MM-DD | initial | ... |
```

## Rules

1. Default to expand-contract (also called additive-first). Destructive migrations only in a maintenance window.
2. `CREATE INDEX CONCURRENTLY` (PG) or `ALGORITHM=INPLACE, LOCK=NONE` (MySQL) for any index on a live table.
3. Long-running `UPDATE` or data backfill runs in batches, not a single statement.
4. Snapshot taken before migration. Snapshot named predictably (`pre-<change>-<date>`).
5. Migration tested on staging with representative data volume.
6. Drop column only after week-long soak on read-new.

## Common failures

- **One-shot destructive migration on Friday afternoon.** Obvious, still happens.
- **`ALTER TABLE ADD COLUMN NOT NULL DEFAULT ...`** on MySQL < 8 with a large table — full table rewrite.
- **`ALTER COLUMN TYPE`** on a varchar → text migration — scans the whole table.
- **Backfill in a single `UPDATE`** — long transaction, blocks replication.
- **Foreign key validation** as part of the migration — use `NOT VALID` then `VALIDATE CONSTRAINT` separately.
- **No rollback documented for phase 4.** Drop is irreversible without restore.
