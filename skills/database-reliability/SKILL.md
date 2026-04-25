---
name: database-reliability
description: 'Database reliability engineering: SLOs for databases, operational runbooks,
  change management, capacity planning, backup verification, incident response, and
  monitoring strategies for production MySQL. Use when setting up production database...'
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Database Reliability Engineering
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Database reliability engineering: SLOs for databases, operational runbooks, change management, capacity planning, backup verification, incident response, and monitoring strategies for production MySQL. Use when setting up production database...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `database-reliability` or would be better handled by a more specific companion skill.
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
| Operability | Database SLO record | Markdown doc per `skill-composition-standards/references/slo-template.md` covering query latency, availability, and replication-lag SLOs | `docs/data/db-slo.md` |
| Operability | Backup verification log | Markdown doc tracking restore-test runs and recovery-time measurements | `docs/data/backup-verify-log.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
## Core Philosophy

Databases are not special snowflakes. Treat every node as cattle: replaceable, automated, and monitored. The DBRE role is engineering, not firefighting. Toil (manual, repetitive, automatable work that scales linearly with growth) is the enemy — eliminate it.

---

## 1. Database SLOs

### Availability Targets

| Tier | SLO | Downtime/Year | Downtime/Week |
|------|-----|---------------|---------------|
| Standard | 99.9% | 8.7 hours | 10.08 minutes |
| High | 99.95% | 4.4 hours | 5.04 minutes |
| Critical | 99.99% | 52 minutes | 1 minute |

**Sample SLO:** 99.9% availability averaged over one week; no single incident >10.08 minutes; downtime declared when >5% of users affected; one annual 4-hour maintenance window (2 weeks notice, <10% users).

### Latency SLOs

Never use averages — they are lossy and hide tail latency. Use percentiles over 1-minute windows at 99% of requests.

```
p50 < 5ms   (pk lookups)  |  p95 < 50ms (indexed queries)
p99 < 200ms (joins/agg)   |  max 500ms  (circuit breaker)
```

### Replication and Connection SLOs

```
Replication lag:     <5s normal | alert 10s | critical 30s
Connections:         <80% of max_connections (alert), >20% headroom required
Slow query rate:     <1% of total queries
```

### Error Budget

Track weekly. 30% consumed by Tuesday → create ticket. 70% consumed with 3+ days left → freeze non-critical deployments. 99.9% SLO = 604.8 seconds budget per week.

```sql
SELECT ROUND(SUM(duration_seconds) / 604.8, 1) AS budget_pct_used
FROM downtime_log WHERE week_start = CURDATE() - INTERVAL WEEKDAY(CURDATE()) DAY;
```

---

## Platform SRE for Databases

### Database SLIs

Concrete SLIs a production DB must track:

- Query P95 latency (ms) — `histogram_quantile(0.95, sum(rate(mysql_query_duration_seconds_bucket[5m])) by (le))` for MySQL; `pg_stat_statements` for PostgreSQL
- Replication lag (seconds) — MySQL `Seconds_Behind_Master`, PostgreSQL `pg_last_wal_replay_lsn` vs primary `pg_current_wal_lsn`
- Connection pool utilisation — `sum(pool_active_connections) / sum(pool_max_connections)` per service
- Deadlock rate — MySQL `SHOW ENGINE INNODB STATUS` deadlock counter, PostgreSQL `deadlocks` in `pg_stat_database`
- Error rate — query errors per minute, grouped by error class

### Database SLOs

Example SLO targets for a production SaaS DB:

- Query P95 ≤ 100ms for 99.5% of requests over 28 days
- Availability ≥ 99.95% (downtime ≤ 20.16 minutes per 28d)
- Replication lag P95 ≤ 5 seconds over 28d
- Error budget: `(1 - 0.995) × 28d = 3h 22min` of query-latency-breach allowed per 28d

### Error Budget Tracking

How to track against the budget:

- Replication lag budget: allow max 1 hour of lag > 30 seconds per month. Alert at 50% burn.
- Query latency budget: alert at 2% budget burn in 1 hour (fast burn) or 10% in 6 hours (slow burn)
- Publish a weekly SLO report (Grafana snapshot) to the engineering channel

Sample SLO definition YAML (Sloth-compatible):

```yaml
version: "prometheus/v1"
service: "mysql-primary"
slos:
  - name: "query-latency-p95"
    objective: 99.5
    description: "P95 query latency under 100ms"
    sli:
      events:
        error_query: "sum(rate(mysql_query_duration_seconds_bucket{le='0.1'}[5m]))"
        total_query: "sum(rate(mysql_query_duration_seconds_count[5m]))"
    alerting:
      name: MySQLQueryLatencyP95
      page_alert:
        labels:
          severity: critical
      ticket_alert:
        labels:
          severity: warning
```

### Chaos Engineering for Databases

Controlled drills to run quarterly in staging (never prod without a rollback plan):

- Primary failover drill — promote replica, measure RTO, verify application auto-reconnect
- Connection pool exhaustion — open connections until pool is saturated, confirm circuit breaker trips
- Replica lag injection — `SELECT pg_sleep(60)` on replica to simulate 60s lag; confirm read traffic falls back to primary
- Disk full simulation — fill test volume to 95%, confirm alerts fire and read-only mode kicks in
- Query killer test — run a runaway `SELECT SLEEP(300)` and confirm the query killer terminates after 30s

Record every drill in a runbook with observed RTO/RPO.

### Blameless Database Postmortem Template

```markdown
# Postmortem: <incident title>

- Date: YYYY-MM-DD
- Severity: SEV1/2/3/4
- Duration: HH:MM (start → resolved)
- Services affected:
- Authors:

## Timeline (UTC)

- HH:MM first alert fired
- HH:MM on-call acknowledged
- HH:MM root cause identified
- HH:MM mitigation applied
- HH:MM service restored

## Root Cause (5-Whys)

1. Why did service degrade? Query latency jumped
2. Why did query latency jump? Missing index on new column
3. Why was the index missing? Migration added column without CREATE INDEX
4. Why did migration ship without the index? Review did not catch it
5. Why did review not catch it? No migration-review checklist in PR template

## Action Items

- [ ] Add migration-review checklist to PR template — owner, JIRA-XXXX, due YYYY-MM-DD
- [ ] Run pt-online-schema-change to add the missing index — owner, JIRA-XXXX, due YYYY-MM-DD

## What Went Well / What Went Poorly

- Went well: alert fired within 2 min; runbook was up to date
- Went poorly: no schema-change CI gate; post-deploy smoke test did not exercise the new query
```

### Toil Identification and Automation

Tasks that must be automated away (anything repeated > 2 times per month):

- Backup verification — cron job that restores yesterday's backup to a scratch instance and runs a checksum query
- Index maintenance — `pt-online-schema-change` scheduled via Ansible for large-table DDL
- Stale connection cleanup — `pg_terminate_backend` on connections idle > 1 hour with open transactions
- Log rotation and retention — `logrotate` configured via Ansible role

### Runbook Structure

Every DB runbook must follow this structure:

```markdown
# Runbook: <alert name>

- Severity: SEV1/2/3
- Trigger: <PromQL or alert condition>
- SLA to acknowledge: < 5 min for SEV1

## Investigation

1. <command to run first>
2. <metric or log to check>
3. <decision tree>

## Resolution

1. <primary mitigation>
2. <rollback steps if mitigation fails>

## Escalation

- Primary on-call → Secondary → DBRE lead → VP Engineering
- External: DB vendor support (ticket URL)

## Related

- Grafana dashboard URL
- Recent postmortem links
- Vendor docs
```

---

## Additional Guidance

Extended guidance for `database-reliability` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `2. Toil Reduction — What to Automate`
- `3. Change Management for Databases`
- `4. Backup Verification Runbook`
- `5. Monitoring Pyramid`
- `6. Alert Fatigue Prevention`
- `7. Capacity Planning`
- `8. Incident Response Runbook`
- `9. Connection Exhaustion Response`
- `10. Replication Failure Recovery`
- `11. Security Incident Response`
- `12. Planned Maintenance Checklist`
- `13. Chaos Engineering for Databases`
- Additional deep-dive sections continue in the reference file.