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

<!-- dual-compat-start -->
## Use When

- Database reliability engineering: SLOs for databases, operational runbooks, change management, capacity planning, backup verification, incident response, and monitoring strategies for production MySQL. Use when setting up production database...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `database-reliability` or would be better handled by a more specific companion skill.
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
