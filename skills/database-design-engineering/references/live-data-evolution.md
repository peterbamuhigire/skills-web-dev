# Live Data Evolution

Use this reference when schema or data changes must happen on live systems without corrupting correctness.

## Migration Sequence

1. Expand schema in a backward-compatible way.
2. Deploy code that can read old and new shapes safely.
3. Backfill or dual-write with explicit monitoring.
4. Verify counts, invariants, and critical queries.
5. Cut traffic or reads fully to the new shape.
6. Contract old columns, indexes, or projections later.

## Verification Rules

- Define row counts, checksums, invariant checks, or reconciliation queries before running the migration.
- Make backfill progress and failure visible to operators.
- Classify rollback posture before release: reversible, compensating-only, or forward-fix-only.
- Keep auditability for financially or legally material data changes.
