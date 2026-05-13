---
name: mysql-operations
description: Use when administering, tuning, backing up, restoring, monitoring, or troubleshooting MySQL production systems. Load absorbed MySQL administration and query-performance reference files for operational runbooks, indexes, replication, and incident response.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# MySQL Operations
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

Use this parent skill as the active MySQL operations entrypoint. Operational advice must be tied to observable evidence and a reversible execution path.

<!-- dual-compat-start -->
## Use When

- Troubleshooting slow queries, lock waits, replication lag, connection exhaustion, deadlocks, or storage pressure.
- Designing backup, restore, HA, monitoring, capacity, and maintenance plans for MySQL.
- Reviewing production configuration, operational runbooks, and incident evidence.

## Do Not Use When

- The task is unrelated to this parent skill or is better handled by a narrower active parent named in the workflow.
- The request only needs a trivial answer and no reference module needs to be loaded.

## Required Inputs

- Gather the concrete system, repository, environment, constraints, and deliverable before loading references.
- Identify which absorbed reference file is needed; do not load every migrated reference by default.
## Workflow

1. Load `database-reliability` for SLOs, recovery objectives, and incident handling.
2. Load the task-specific reference:
   - `references/mysql-administration.md` for roles, backup, restore, replication, upgrades, and maintenance.
   - `references/mysql-query-performance.md` for query tuning, indexes, EXPLAIN review, and capacity analysis.
3. Pair with `mysql-engineering` when schema or SQL changes are part of the work.
4. Pair with `observability-monitoring` for dashboards, alerts, and production telemetry.

## Quality Standards

- State measurement source, rollback path, and verification command before production changes.
- Treat backup restore tests as required evidence, not documentation claims.
- Avoid global tuning changes when query, index, or workload fixes are the real issue.

## Anti-Patterns

- Treating absorbed reference files as active skills or separate routing entrypoints.
- Loading every migrated child reference instead of the one that matches the task.
- Producing generic advice without constraints, evidence, or next verification steps.
## Outputs

- MySQL runbook, tuning plan, incident review, backup/restore plan, or operational checklist.

## References

- Load only the eferences/<old-skill>.md files named in the workflow when their depth is required.
<!-- dual-compat-end -->
