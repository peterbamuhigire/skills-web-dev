---
name: postgresql-operations
description: Use when administering, tuning, backing up, restoring, monitoring, or troubleshooting PostgreSQL production systems. Load the absorbed PostgreSQL administration and performance reference files for operational runbooks, query tuning, vacuum, replication, and incident response.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# PostgreSQL Operations
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

Use this parent skill as the active PostgreSQL operations entrypoint. Keep operational decisions tied to evidence: metrics, logs, query plans, lock graphs, replication state, backup history, and recovery objectives.

<!-- dual-compat-start -->
## Use When

- Troubleshooting slow queries, lock contention, bloat, vacuum pressure, replication lag, or connection exhaustion.
- Designing backup, restore, HA, maintenance, monitoring, or capacity plans for PostgreSQL.
- Reviewing production database configuration, operational runbooks, and incident evidence.

## Do Not Use When

- The task is unrelated to this parent skill or is better handled by a narrower active parent named in the workflow.
- The request only needs a trivial answer and no reference module needs to be loaded.

## Required Inputs

- Gather the concrete system, repository, environment, constraints, and deliverable before loading references.
- Identify which absorbed reference file is needed; do not load every migrated reference by default.
## Workflow

1. Load `database-reliability` for SLOs, error budgets, incident posture, and recovery evidence.
2. Load the task-specific reference:
   - `references/postgresql-administration.md` for administration, backup, restore, roles, maintenance, and replication.
   - `references/postgresql-performance.md` for query tuning, indexing, EXPLAIN review, statistics, vacuum, and capacity work.
3. Pair with `postgresql-engineering` when schema or SQL changes are part of the fix.
4. Pair with `observability-monitoring` when dashboards, alerting, traces, or metrics need implementation.

## Quality Standards

- No operational recommendation without a measurement path and rollback plan.
- State RPO, RTO, maintenance window, blast radius, and verification command for every risky operation.
- Prefer small, testable changes over broad tuning sweeps.

## Anti-Patterns

- Treating absorbed reference files as active skills or separate routing entrypoints.
- Loading every migrated child reference instead of the one that matches the task.
- Producing generic advice without constraints, evidence, or next verification steps.
## Outputs

- Runbook, tuning plan, incident analysis, backup/restore plan, or operational review with verification commands.

## References

- Load only the eferences/<old-skill>.md files named in the workflow when their depth is required.
<!-- dual-compat-end -->
