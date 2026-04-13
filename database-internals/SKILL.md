---
name: database-internals
description: 'Deep database internals: B-tree storage, WAL/REDO logging, MVCC, buffer
  pool mechanics, transaction isolation, and distributed database concepts. Use when
  making database design decisions that require understanding how MySQL works internally
  —...'
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Database Internals

<!-- dual-compat-start -->
## Use When

- Deep database internals: B-tree storage, WAL/REDO logging, MVCC, buffer pool mechanics, transaction isolation, and distributed database concepts. Use when making database design decisions that require understanding how MySQL works internally —...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `database-internals` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
Mental models from *Database Internals* (Alex Petrov, O'Reilly 2019) translated into
practical design rules. Each section ends with a **So what** block — the actionable
implication for real MySQL/SaaS work.

---

## 1. B-Tree Structure — The Clustered Index IS the Table

InnoDB organises every table as a **B+-Tree index-organised table (IOT)**. The primary
key is not a pointer to a row — it *is* the row. Leaf nodes of the clustered index hold
the full row data.

```
Root
 └─ Internal nodes (separator keys only)
     └─ Leaf nodes (PK + all column data)
```

Every **secondary index** stores the primary key value, not a physical row pointer.
A secondary index lookup therefore does **two B-tree traversals**:

1. Traverse the secondary index B-tree → find the PK value.
2. Traverse the clustered index B-tree → find the row.

A **covering index** contains all columns the query needs, so step 2 is skipped.

```sql
-- Two traversals: secondary index + clustered index
SELECT name FROM orders WHERE status = 'paid';

-- One traversal: status+name covering index eliminates the second lookup
SELECT name FROM orders WHERE status = 'paid';  -- with INDEX(status, name)
```

**UUID vs AUTO_INCREMENT PK impact:**
- AUTO_INCREMENT inserts always append to the rightmost leaf. B-tree splits are
  predictable, pages stay ~70–90% full. PostgreSQL calls this the "fastpath".
- Random UUID inserts hit random leaf positions, causing splits throughout the tree,
  leaving pages ~50% full and generating 2–3× more write I/O. InnoDB page
  fragmentation accumulates rapidly.

**So what:** Always use `INT UNSIGNED AUTO_INCREMENT` or `BIGINT AUTO_INCREMENT` as PK.
If UUIDs are required for business reasons, use UUIDv7 (time-ordered) or store the UUID
as a BINARY(16) with a separate auto-increment surrogate PK for the clustered index.

---

## Additional Guidance

Extended guidance for `database-internals` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `2. Page Structure — The 16 KB Unit of All I/O`
- `3. Write-Ahead Log (WAL / Redo Log)`
- `4. Buffer Pool Mechanics — The Memory Manager`
- `5. MVCC — Consistent Reads Without Locking`
- `6. Transaction Isolation Levels — What Each Actually Does`
- `7. Lock Types and Interactions`
- `8. LSM Trees vs B-Trees — The Core Tradeoff`
- `9. Distributed Systems Concepts Applied to MySQL`
- `10. Index Structures Beyond B-Trees`
- `11. Write Amplification — Why SSDs Matter`
- `12. MySQL vs PostgreSQL Internals — Key Architectural Differences`
- `13. Design Rules Derived from Internals`
- Additional deep-dive sections continue in the reference file.
