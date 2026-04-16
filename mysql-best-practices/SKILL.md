---
name: mysql-best-practices
description: MySQL 8.x best practices for high-performance, secure SaaS applications.
  Use when designing database schemas, writing queries, optimizing performance, implementing
  multi-tenant isolation, configuring servers, setting up replication, hardening...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# MySQL Best Practices for SaaS

<!-- dual-compat-start -->
## Use When

- MySQL 8.x best practices for high-performance, secure SaaS applications. Use when designing database schemas, writing queries, optimizing performance, implementing multi-tenant isolation, configuring servers, setting up replication, hardening...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `mysql-best-practices` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references, examples` only as needed.
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
| Data safety | Schema and constraints register | Markdown doc per `skill-composition-standards/references/entity-model-template.md` | `docs/data/mysql-schema-orders.md` |
| Performance | Query plan review | Markdown doc covering EXPLAIN output for hot paths | `docs/data/mysql-explain-orders.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
- Use the `examples/` directory for concrete patterns when implementation shape matters.
<!-- dual-compat-end -->
Production-grade MySQL patterns for high-performance, secure, scalable SaaS applications.

**Core Principle:** Performance is query response time. Optimize queries and indexes first, tune server second, scale hardware last.

**Access Policy (Required):** Frontend clients must never access the database directly. All data access must flow through backend services exposed via APIs.

**Deep References:** `references/query-performance.md`, `references/indexing-deep-dive.md`, `references/server-tuning-mycnf.md`, `references/security-hardening.md`, `references/high-availability.md`, `references/advanced-sql-patterns.md`, `references/backup-recovery.md`, `references/transaction-locking.md`, `references/benchmarking-tools.md`

**SQL References:** `references/stored-procedures.sql`, `references/triggers.sql`, `references/partitioning.sql`

## Deployment Environments

| Environment | OS | Database | Notes |
|---|---|---|---|
| **Development** | Windows 11 (WAMP) | MySQL 8.4.7 | User: `root`, no password |
| **Staging** | Ubuntu VPS | MySQL 8.x | User: `peter`, password required |
| **Production** | Debian VPS | MySQL 8.x | User: `peter`, password required |

**Cross-platform rules:**
- Always use `utf8mb4_unicode_ci` collation (never `utf8mb4_0900_ai_ci` or `utf8mb4_general_ci`)
- Never use platform-specific SQL features; test on MySQL 8.x
- Production migrations go in `database/migrations-production/` with `-production` suffix

## Additional Guidance

Extended guidance for `mysql-best-practices` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `When to Use`
- `Schema Design`
- `Indexing`
- `Query Performance`
- `Security`
- `Transactions & Locking`
- `Advanced SQL`
- `Server Tuning`
- `Operations`
- `MySQL 8 Exclusive Features`
- `Checklist`
