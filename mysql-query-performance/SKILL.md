---
name: mysql-query-performance
description: 'Expert MySQL 8 query performance tuning: EXPLAIN analysis, index design,
  optimizer hints, slow query diagnosis, and profiling. Use when optimizing slow queries,
  designing indexes, analyzing EXPLAIN output, or diagnosing MySQL performance problems.'
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# MySQL Query Performance — Expert Reference
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Expert MySQL 8 query performance tuning: EXPLAIN analysis, index design, optimizer hints, slow query diagnosis, and profiling. Use when optimizing slow queries, designing indexes, analyzing EXPLAIN output, or diagnosing MySQL performance problems.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `mysql-query-performance` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Performance | Slow-query diagnosis and tuning report | Markdown doc covering EXPLAIN, index, and tuning changes | `docs/data/mysql-tuning-2026-04-16.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
**Sources:** MySQL 8 Query Performance Tuning (Krogh, Apress 2020) + Efficient MySQL Performance (Nichter, O'Reilly 2022)

## 1. EXPLAIN ANALYZE vs EXPLAIN FORMAT=JSON

`EXPLAIN ANALYZE` (MySQL 8.0.18+) **executes** the query and returns actual measured statistics alongside estimates. This is the single most important diagnostic upgrade over plain EXPLAIN.

```sql
-- Standard EXPLAIN: estimates only, query NOT executed
EXPLAIN FORMAT=JSON SELECT * FROM orders WHERE customer_id = 42;

-- EXPLAIN ANALYZE: executes query, returns actual vs estimated
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 42;
```

**Reading EXPLAIN ANALYZE output — key fields:**

```
-> Index lookup on orders using idx_customer (customer_id=42)
   (cost=18.50 rows=41)
   (actual time=0.134..2.847 rows=38 loops=1)
```

- `cost=18.50 rows=41` — optimizer's **estimate** before execution
- `actual time=0.134..2.847` — real elapsed ms (first row .. last row)
- `rows=38 loops=1` — actual rows returned, loop count for nested joins
- When `rows` (estimated) diverges greatly from `actual rows`, index statistics are stale or a histogram is needed
- `loops=N` on an inner table means the entire sub-operation ran N times — multiply `actual time` by `loops` for total cost

**EXPLAIN FORMAT=JSON** shows the cost model breakdown without executing:

```sql
EXPLAIN FORMAT=JSON SELECT o.id, c.name
FROM orders o JOIN customers c ON o.customer_id = c.id
WHERE o.status = 'pending'\G
```

Look for `"cost_info"` → `"read_cost"` + `"eval_cost"` to understand why the optimizer chose a plan. The `"chosen"` boolean inside `"considered_execution_plans"` reveals rejected alternatives.

**EXPLAIN FOR CONNECTION** — get the live plan of a running query without re-running it (critical when index stats may have changed): `EXPLAIN FOR CONNECTION 42;`

---

## Additional Guidance

Extended guidance for `mysql-query-performance` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `2. Index Selection — Why MySQL Ignores Your Index`
- `3. Covering Index Strategy and ICP`
- `4. Index Merge — Usually a Warning Sign`
- `5. Invisible Index Trick`
- `6. Histogram Statistics`
- `7. Optimizer Hints (MySQL 8.0)`
- `8. Derived Table Materialization`
- `9. Slow Query Log Analysis`
- `10. Essential Performance Schema Queries`
- `11. InnoDB Buffer Pool`
- `12. Sort Optimisation (filesort vs Index Sort)`
- `13. JOIN Algorithms`
- Additional deep-dive sections continue in the reference file.