---
name: database-reliability
description: Use when defining database SLOs, error budgets, backup verification, capacity policy, incident response, game days, or MySQL and PostgreSQL on-call practice.
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

## Do Not Use When

- The request concerns logical schema design without recovery, availability, or operational risk; use `database-design-engineering`.
- The task asks for a vendor command copied into production without an approved maintenance window, tested backup, and rollback path.

## Required Inputs

| Input | Required | Why it matters |
|---|---|---|
| Business RPO and RTO by datastore | yes | Sets backup frequency and recovery architecture |
| Topology, engine version, and data size | yes | Constrains replication, restore, and failover procedures |
| Backup, retention, encryption, and access configuration | yes | Establishes whether recoverable copies exist |
| Incident history and capacity trends | conditional | Reveals recurring failure and saturation modes |

## Workflow

Translate RPO and RTO into controls, map failure modes, inspect backup and replication paths, perform a controlled restore, validate recovered data and application behavior, then record gaps, owners, and the next exercise date.

## Quality Standards

Backup presence is not recovery evidence. Claims require a timed restore or failover exercise, integrity checks, documented dependencies, and measured RPO and RTO results against the stated target.

## Outputs

| Output | Consumer | Acceptance condition |
|---|---|---|
| Recovery design | Platform and database owners | Maps each failure class to backup, replication, failover, and corruption controls |
| Restore or failover evidence | Risk and operations reviewers | Records timestamps, recovered point, integrity checks, observed RPO and RTO, and deviations |
| Remediation register | Accountable owners | Prioritizes gaps with owner, deadline, operational risk, and verification step |

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

### SRE — overview and positioning

SRE applies the SLO / error-budget / postmortem loop to operations work. This section turns database operations from "best effort" into a measurable, budgeted activity. Read it after the existing content on backups, replication, and query tuning, because the SLIs reference those subsystems. For application-tier SRE mechanics (alert routing, multi-burn-rate alerting, instrumentation), cross-reference the `observability-monitoring` and `reliability-engineering` skills rather than duplicating that material here.

Per Google SRE Book ch. 4 (Jones, Wilkes, Murphy, Smith — sre.google/sre-book/service-level-objectives/):

- An SLI is "a carefully defined quantitative measure of some aspect of the level of service that is provided".
- An SLO is "a target value or range of values for a service level that is measured by an SLI".
- An SLA "includes consequences of meeting (or missing) the SLOs".

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

### Error Budget Tracking and Policy

Per Google SRE Workbook, "Implementing SLOs" (Thurgood, Ferguson, Hidalgo, Beyer — sre.google/workbook/implementing-slos/):

> the error budget is 100% minus the SLO

A 99.9% availability SLO yields a 0.1% budget — about 43 m 12 s per 30 days. The error budget policy is "a policy outlining what to do when your service runs out of budget" (same source). For a database tier, the typical policy actions are:

| Budget state | Action |
|--------------|--------|
| ≥ 50% remaining | normal change cadence |
| 25–50% remaining | review every change for SLO impact; high-risk changes require sign-off |
| < 25% remaining | freeze schema changes and config changes; permit only reliability fixes |
| Exhausted | full freeze; postmortem the incident(s) that consumed the budget; resume only after the budget recovers above threshold |

Approval: per the SRE workbook, the policy must be agreed by product, dev, and SRE — for the data tier this means the application owner, the database team, and the platform team.

Tracking mechanics:

- Replication lag budget: allow max 1 hour of lag > 30 seconds per month. Alert at 50% burn.
- Query latency budget: alert at 2% budget burn in 1 hour (fast burn) or 10% in 6 hours (slow burn). For multi-window multi-burn-rate alerting mechanics, see `observability-monitoring`.
- Publish a weekly SLO report (Grafana snapshot) to the engineering channel.

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

### Blameless Database Postmortem

Per Google SRE Book "Postmortem Culture" (Lunney, Lueder, O'Connor — sre.google/sre-book/postmortem-culture/):

> For a postmortem to be truly blameless, it must focus on identifying the contributing causes of the incident without indicting any individual or team for bad or inappropriate behavior.

Required template sections (synthesised from the same chapter):

- Title and date
- Authors and reviewers
- Status (draft / review / final)
- Summary (one paragraph)
- Impact (customers affected, duration, financial impact if quantifiable)
- Timeline (UTC, machine-readable)
- Root cause and contributing factors
- Detection (how the incident was detected; was there an alert; lead time)
- Response (what worked, what didn't)
- Lessons learned (what went well / poorly / where we got lucky)
- Action items (owner, due date, ticket link)

Anti-patterns: blaming an individual; "human error" as a root cause without a system-level contributing factor; action items without owners or dates; postmortems that never close.

Facilitation rules: one facilitator (not the on-call who handled the incident); recorded timeline before discussion; all participants agree to "we acted in good faith with the information available at the time".

#### Worked example template

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

### Escalation Policies

Severity definitions, PagerDuty Incident Response (response.pagerduty.com/before/severity_levels/):

- SEV-1: "Critical issue that warrants public notification and liaison with executive teams."
- SEV-2: "Critical system issue actively impacting many customers' ability to use the product."
- SEV-3: "Stability or minor customer-impacting issues that require immediate attention from service owners."
- SEV-4: "Minor issues requiring action, but not affecting customer ability to use the product."
- SEV-5: "Cosmetic issues or bugs, not affecting customer ability to use the product."

PagerDuty also notes that when in doubt during an active incident, "treat it as the more urgent level rather than debating the distinction" (same source).

Paging tiers for the database tier:

- SEV-1/2: page primary on-call DBA + platform on-call + incident commander; open war-room channel.
- SEV-3: ticket primary on-call; respond within business hours unless aging breaches SLO.
- SEV-4/5: backlog.

Runbook hand-off:

- Every page links to a runbook URL.
- Hand-off between on-call rotations: written status of open incidents, in-flight changes, and known noisy alerts. Verbal hand-off without a written record is a defect.

War-room conventions:

- One channel per incident, named with the incident ID.
- Roles assigned: Incident Commander, Communications, Operations (per PagerDuty's role definitions on response.pagerduty.com).
- Decisions logged in-channel; chat history is the source of truth for the postmortem timeline.

### Game Days and DB-tier Chaos (lightweight)

Lightweight scope: only what applies directly to MySQL/PostgreSQL operations. Generic chaos-engineering platforms (Chaos Mesh, Litmus, etc.) belong in the Kubernetes platform skill, not here.

| Scenario | What it tests |
|----------|---------------|
| Promote a replica (planned failover drill) | replication health, app reconnection, DNS / proxy switchover |
| Kill primary (SIGKILL mysqld / postgres) | failover automation, runbook accuracy, alert fan-out |
| Disk-full on primary | monitoring of disk SLI, runbook for emergency cleanup |
| Slow network (10% packet loss between primary and replica) | replication-lag SLO, alert thresholds |
| Restore from backup to a scratch host | RTO measurement; backup integrity (links to existing backup section) |

Cadence: quarterly minimum. Every game day produces a written report in the same template as a postmortem. Tooling: `mysqladmin`, `pg_ctl`, `iptables`, and `tc` (traffic control) cover the scenarios above; derive command sequences per environment.

For deeper SRE / SLO theory and burn-rate alerting math, see [references/sre-slo.md](references/sre-slo.md) and the `reliability-engineering` and `observability-monitoring` skills.

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

## Capability contract
Assess SLOs, backups, capacity, and incident controls read-only by default. Do not fail over, restore, kill sessions, change replication, or run chaos tests without production approval and a rollback plan.

## Degraded mode
If telemetry or restore evidence is unavailable, mark the SLO or recovery objective unverified and return the exact validation runbook.

## Decision rules
| Condition | Action |
|---|---|
| Restore has not been tested | Treat backup recoverability as unknown |
| Error budget exhausted | Freeze risky database changes |
| Replica lag threatens correctness | Route or shed affected reads |

## Domain Anti-Patterns
- Calling backup success recovery proof. Fix: test restores.
- Alerting on every transient spike. Fix: alert on user-impacting symptoms.
- Failing over without a fencing plan. Fix: prevent split brain.
- Running game days without abort criteria. Fix: predefine stop conditions.
- Hiding capacity assumptions. Fix: record headroom and growth evidence.
