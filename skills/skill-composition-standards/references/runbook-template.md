# Runbook Template

One runbook per service or per critical flow. Produced by `observability-monitoring` and `reliability-engineering`. Used by on-call.

## Template

```markdown
# Runbook — <service or flow name>

**Owner team:** <team>
**On-call rota:** <link>
**Last drill:** YYYY-MM-DD
**Last reviewed:** YYYY-MM-DD

## At a glance

- **Purpose:** one sentence on what this service does
- **Dependencies:** <upstream / downstream services>
- **Primary dashboard:** <link>
- **Primary logs:** <link>
- **SLOs:** <link to SLO doc>
- **Tier:** P1 | P2 | P3 (for page severity)

## Common alerts

### Alert: `<service>-availability-burning-fast`

**Symptom:** availability SLO burn-rate > 14.4× for > 5 minutes.

**First actions (within 5 min):**

1. Open the dashboard; check which endpoint is failing.
2. Check upstream dependencies (see "Dependencies" above). Are they healthy?
3. Check recent deploys: `kubectl -n prod rollout history deployment/<service>` — any in last 2 hours?
4. If recent deploy + errors align, initiate rollback. See `rollback-plan-<service>.md`.
5. If no recent deploy, check the top error code. Follow the relevant diagnosis path below.

**Diagnosis paths:**

- Top error = `UPSTREAM_TIMEOUT` — upstream dep is slow or down. Check its runbook.
- Top error = `INTERNAL` — check recent changes + logs for panic traces.
- Top error = `RATE_LIMITED` (from upstream) — check upstream quota; consider adaptive rate limiting.
- Top error = `UNAVAILABLE` — check pod health, node health, resource pressure.

**Escalation:**

- No resolution in 20 minutes → page on-call lead.
- No resolution in 45 minutes → declare a P1 incident, page service owner.

### Alert: `<service>-latency-burning`

**Symptom:** p95 latency > 2× target for > 10 minutes.

**First actions:**

1. Check dashboard — is it one endpoint or all?
2. Check recent deploys.
3. Check DB: slow query log, connection pool saturation, lock waits.
4. Check cache: hit rate, eviction rate, memory pressure.
5. Check external deps: are they slow?

**Diagnosis paths:**

- One endpoint slow → recent code change? missing index?
- All endpoints slow → infra issue (DB, cache, network)?
- Slow + high CPU → runaway loop or inefficient query deployed?
- Slow + high memory → leak or oversized payload?

### Alert: `<service>-error-budget-exhausted`

**Symptom:** 90% of error budget consumed with > 5 days left in window.

**Not a page, but a strong signal:**

1. Pause new feature deploys for this service until budget recovers.
2. Schedule reliability work to reduce the incident class driving the burn.

## Diagnosis tools

```bash
# Tail logs for last 1000 lines of errors
kubectl -n prod logs deployment/<service> --tail 1000 | grep -E 'level=(error|warn)'

# Check pod status
kubectl -n prod get pods -l app=<service>

# DB slow queries (MySQL)
mysql> SELECT * FROM mysql.slow_log ORDER BY start_time DESC LIMIT 20;

# Prometheus ad-hoc query
# rate(http_requests_total{service="<service>",status=~"5.."}[5m])
```

## Playbooks by symptom

### Symptom: database connection pool exhausted

Signs: errors mentioning "no available connections", p95 latency doubled, all endpoints affected.

Actions:

1. Check pool size config vs concurrency:
   `kubectl -n prod describe configmap <service>-config | grep pool`
2. Check for query plan regressions (long-running queries holding connections).
3. Short-term: increase pool size OR restart stuck pods.
4. Long-term: identify slow query; add index or fix N+1.

### Symptom: cache stampede

Signs: sudden DB CPU spike; cache hit rate crashes to near zero; many duplicate in-flight requests.

Actions:

1. Check if a cache was just invalidated (log "cache_flush" events).
2. Enable jittered re-population (if deployed via flag).
3. If cache is down, scale DB temporarily and investigate cache health.

### Symptom: thundering herd on startup

Signs: service pod starts → immediate DB overload; pod marked unhealthy; loops.

Actions:

1. Check startup probe: should use `/startup` endpoint, not `/ready`.
2. Add warm-up logic; stagger pod restarts.

## Contacts

- Service owner (normal hours): <team>
- Service owner (on-call pager): <pager>
- DB owner: <team>
- Upstream service owner: <team>
- Security on-call (for security incidents only): <pager>

## Known-issues log

| Date | Issue | Mitigation | Permanent fix tracker |
|---|---|---|---|
| YYYY-MM-DD | Cron job X causes p95 spike at :00 | Spread schedule with jitter | ticket-123 |

## Revision log

| Date | Change | Author |
|---|---|---|
| YYYY-MM-DD | initial | ... |
```

## Rules

1. One runbook per service or critical flow — not one mega-runbook.
2. Every alert in the alert rules has a matching section in this runbook.
3. First actions are timed — "within 5 min", "within 15 min" — so on-call knows when to escalate.
4. Diagnosis paths are symptom-based, not technology-based.
5. Known-issues log captures recurring problems that have workarounds.
6. Runbook is reviewed quarterly OR after any incident that surfaced a gap.

## Common failures

- **Runbook is a wiki page from 3 years ago** — first-actions reference tools that no longer exist.
- **No escalation timer** — on-call keeps trying alone for hours.
- **Alert with no runbook section** — page without guidance.
- **Runbook not linked from the alert** — on-call has to find it.
- **No known-issues log** — the same problem is diagnosed from scratch every time.
