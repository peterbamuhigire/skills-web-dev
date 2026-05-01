# SRE — SLO/SLI, Error Budgets, Postmortems (database tier)

Deep dive supporting `SKILL.md` "Platform SRE for Databases". Read `SKILL.md` first for the canonical workflow; this file is for theory, derivations, and worked examples that would otherwise bloat the entry point.

## 1. SLI taxonomy for databases

| SLI | Definition | Source signal (MySQL) | Source signal (PostgreSQL) |
|-----|------------|-----------------------|----------------------------|
| Query latency p99 | 99th percentile of query duration over rolling window | `performance_schema.events_statements_summary_*`, proxy histograms | `pg_stat_statements.total_exec_time / calls`, OTel spans |
| Replication lag | seconds the replica is behind primary | `SHOW REPLICA STATUS \G` `Seconds_Behind_Source` | `pg_stat_replication.replay_lag` or LSN diff |
| Error rate | failed queries divided by total queries | server error log + proxy 5xx | server error log + connection pooler stats |
| Availability | minutes the primary accepted writes divided by minutes in window | external health probe with synthetic write | external health probe with synthetic write |

Write SLIs as event ratios (good events / valid events) rather than averages. Averages mask tail behaviour; ratios survive aggregation across replicas, regions, and time windows.

## 2. SLO target selection

Numeric targets are workload-specific. Do not copy targets between products. Procedure:

1. Measure current behaviour for at least 28 days before setting a target.
2. Set the SLO slightly below current performance — close enough to be a real constraint, far enough that the team is not paged on noise.
3. Express the SLO over the same window the error budget covers (28 or 30 days are typical).
4. Re-evaluate quarterly; tighten only after the team has held the target for two consecutive windows.

Example targets for an OLTP SaaS:

- Query latency p99: 99% of measurement minutes have p99 < 50 ms over 30 days.
- Replication lag: 99.9% of measurement minutes have lag < 5 seconds over 30 days.
- Availability: 99.95% writes-accepted minutes over 30 days.

## 3. Error budget arithmetic

For a window of N minutes and SLO target T (as a fraction):

- Allowed bad minutes = N × (1 − T)
- 99.9% over 30 days = 30 × 24 × 60 × 0.001 = 43.2 minutes
- 99.95% over 28 days = 28 × 24 × 60 × 0.0005 ≈ 20.16 minutes
- 99.99% over 30 days = 30 × 24 × 60 × 0.0001 ≈ 4.32 minutes

Burn rate: (bad event rate over short window) ÷ (allowed bad event rate over SLO window). Pages and tickets follow burn-rate pairs (fast burn for paging, slow burn for ticket) — see `observability-monitoring` for the alerting recipe.

## 4. Error budget policy enforcement

Steps to operationalise the policy table in `SKILL.md`:

1. Track current budget consumption in the SLO dashboard. Show remaining %, not just consumed.
2. Automate state transitions: when remaining drops below 25%, post a notification to the platform channel and the change-management board.
3. Freeze list: schema migrations, configuration changes, capacity changes, vendor upgrades. Permitted: reliability fixes, rollback of the change(s) implicated in the burn.
4. Recovery: budget must climb above 25% for at least 24 hours before unfreezing.
5. Escalation: if the budget is exhausted twice in two consecutive windows, escalate to a structural review — the SLO target may be wrong, or the system needs investment.

## 5. Postmortem facilitation playbook

Pre-meeting:

- Facilitator confirms the timeline draft is checked into the wiki.
- All on-call participants pre-fill their contributions to the timeline.
- Rule of psychological safety stated at the top: "we acted in good faith with the information available at the time."

During:

- Read the timeline aloud first; do not jump to root cause.
- Use a five-whys or causal-chain technique to extract contributing factors. "Human error" is never an accepted root cause without a system-level companion factor.
- Capture every action item with an owner and due date in the same meeting; un-owned items are removed.

After:

- Publish within five business days.
- Action items tracked in the same issue tracker as feature work; the SRE/DBRE lead reviews open postmortem items in a monthly operational review.

## 6. Escalation and on-call hand-off detail

- Severity declarations are reversible. Bias upward when in doubt; downgrade later.
- Page noise budget: track pages-per-on-call-shift; if it exceeds the team's agreed threshold, treat as an alerting bug, not a workload to absorb.
- Hand-off doc lives next to the runbooks; minimum fields: open incidents, in-flight changes, suppressed alerts, expiring credentials, recent deploys still in soak.

## 7. Game day playbook

For each scenario in `SKILL.md`:

1. Pre-brief: scope, blast radius, abort criteria, rollback steps.
2. Run the scenario in staging or a clearly labelled non-prod tenant.
3. Observe SLI dashboards live. Record times: detection, page, mitigation, restoration.
4. Debrief in postmortem format. File action items.
5. Repeat the scenario after fixes ship to prove the fix.

Tooling kept minimal:

- `mysqladmin shutdown`, `pg_ctl stop -m immediate` for primary-kill drills.
- `iptables -A INPUT -p tcp --dport 3306 -j DROP` for network partitions.
- `tc qdisc add dev eth0 root netem loss 10%` for slow-network simulation.
- `dd if=/dev/zero of=/var/lib/mysql/fill bs=1M count=...` for disk-full simulation in a scratch volume.

## 8. Cross-references

- `reliability-engineering` — generic retries, timeouts, circuit breakers, degradation modes.
- `observability-monitoring` — SLI instrumentation, multi-burn-rate alert recipes, alert routing.
- `world-class-engineering` — release gates and evidence bundle expectations.
- Existing sections in this skill: backups, replication, capacity planning — those subsystems produce the signals the SLIs depend on.
