# Phase 04: Observability & SRE

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build full-stack production visibility so that any system built with this engine can be monitored, diagnosed, and operated to SLO targets.

**Architecture:** One new skill directory (`observability-platform`) plus targeted enhancements to `database-reliability` (Platform SRE section) and `cicd-jenkins-debian` (Linux hardening). Primary stack: SigNoz (self-hosted, open-source — replaces three separate tools). PHP + Node.js + Android + iOS instrumentation examples throughout.

**Tech Stack:** SigNoz, OpenTelemetry, Prometheus, Grafana, Sentry, structured JSON logging, SLO/SLI/error budgets, sysctl, cgroups, auditd.

---

## Dual-Compatibility Contract

Every `SKILL.md` must include:
```
Use When → Do Not Use When → Required Inputs →
Workflow → Quality Standards → Anti-Patterns → Outputs → References
```

Frontmatter:
```yaml
metadata:
  portable: true
  compatible_with: [claude-code, codex]
```

Platform Notes only — no Required Plugins blockers. Validate after every write:
```bash
python -X utf8 skill-writing/scripts/quick_validate.py <skill-directory>
```

---

## Task 1: Create `observability-platform` skill

**Files:**
- Create: `observability-platform/SKILL.md`
- Create: `observability-platform/references/structured-logging.md`
- Create: `observability-platform/references/metrics-and-dashboards.md`
- Create: `observability-platform/references/distributed-tracing.md`
- Create: `observability-platform/references/slo-error-budgets.md`

**Step 1:** Write `observability-platform/SKILL.md` covering:

- The three pillars: logs, metrics, traces — what each answers
- SigNoz: self-hosted install (Docker Compose), ingesting OpenTelemetry data, built-in dashboards, alert rules
- OpenTelemetry: SDK setup for Node.js and PHP, auto-instrumentation vs. manual spans, OTLP exporter config
- Structured logging: JSON log format, mandatory fields (timestamp, level, service, trace_id, request_id), log levels (DEBUG/INFO/WARN/ERROR), avoiding log spam
- Prometheus: scrape config, metric types (counter, gauge, histogram, summary), PromQL basics
- Grafana: dashboard panels, variables, alert rules, PagerDuty/OpsGenie webhook integration
- Sentry: SDK install for Node.js, PHP, React, iOS, Android; error grouping, release tracking, performance monitoring
- Alert design: alert on symptoms not causes, avoid alert fatigue, runbook link in every alert

Anti-Patterns: logging inside tight loops, alerting on every error (vs. error rate), no trace correlation IDs, dashboards with no alert thresholds, storing secrets in log output.

**Step 2:** Write `references/structured-logging.md` — log format spec, Node.js (Pino), PHP (Monolog), iOS (OSLog structured), Android (Timber) with JSON formatter. Log shipping to SigNoz via OTLP/Fluent Bit.

**Step 3:** Write `references/metrics-and-dashboards.md` — Node.js Prometheus client, PHP metrics middleware, standard SaaS dashboard panels (request rate, error rate, latency p50/p95/p99, DB connection pool, queue depth).

**Step 4:** Write `references/distributed-tracing.md` — trace propagation across HTTP services (W3C TraceContext headers), Node.js OpenTelemetry SDK setup, PHP OpenTelemetry SDK, span attributes for SaaS context (tenant_id, user_id, plan_tier).

**Step 5:** Write `references/slo-error-budgets.md` — SLI definition (availability, latency), SLO target setting (99.5% vs 99.9% — cost comparison), error budget calculation, error budget policy (freeze deployments when budget < 10%), blameless postmortem template.

**Step 6:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py observability-platform
git add observability-platform/
git commit -m "feat: add observability-platform skill (SigNoz, OpenTelemetry, SLO, Sentry)"
```

---

## Task 2: Enhance `database-reliability`

**Files:**
- Modify: `database-reliability/SKILL.md`
- Create: `database-reliability/references/platform-sre-practices.md`

**Step 1:** Read `database-reliability/SKILL.md` in full before editing.

**Step 2:** Add **Platform SRE** section to SKILL.md:
- SLO/SLI for databases: availability SLI (successful queries / total queries), latency SLI (p99 < 50ms), data durability SLI
- Error budget consumption triggers: slow query spike, replication lag > threshold, backup verification failure
- Blameless postmortem: timeline, contributing factors (not root cause), action items, owner + deadline
- Escalation: on-call rotation design, escalation path, war room protocol for P0 incidents
- Database chaos: simulated failure exercises — kill replica, induce disk pressure, inject network latency

**Step 3:** Write `references/platform-sre-practices.md` — full postmortem template, SLO dashboard spec, chaos exercise runbook.

**Step 4:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py database-reliability
git add database-reliability/
git commit -m "feat: enhance database-reliability — Platform SRE, SLO/error budgets, postmortems"
```

---

## Task 3: Enhance `cicd-jenkins-debian`

**Files:**
- Modify: `cicd-jenkins-debian/SKILL.md`
- Create: `cicd-jenkins-debian/references/linux-hardening.md`

**Step 1:** Read `cicd-jenkins-debian/SKILL.md` in full before editing.

**Step 2:** Add **Linux Systems Hardening** section to SKILL.md:
- sysctl tuning: TCP buffer sizes, SYN flood protection, kernel panic behaviour
- cgroups v2: resource limits per service unit (CPU, memory, IO), systemd slice configuration
- auditd: rule sets for file access, privilege escalation, network connections, user auth; log shipping to SIEM
- Network stack: UFW rule ordering, nftables for stateful filtering, fail2ban for SSH brute-force, rate limiting at kernel level
- SSH hardening: `sshd_config` — PermitRootLogin no, PasswordAuthentication no, AllowUsers whitelist, MaxAuthTries

**Step 3:** Write `references/linux-hardening.md` — full hardening checklist, sysctl.conf template, auditd rules file, UFW rule set for web server.

**Step 4:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py cicd-jenkins-debian
git add cicd-jenkins-debian/
git commit -m "feat: enhance cicd-jenkins-debian — Linux hardening, sysctl, cgroups, auditd"
```

---

## Success Gate

- [ ] `observability-platform` passes validator, ≤ 500 lines, portable metadata present
- [ ] `database-reliability` still passes validator after enhancement
- [ ] `cicd-jenkins-debian` still passes validator after enhancement
- [ ] SigNoz is positioned as primary (self-hosted), with cloud alternatives noted in Platform Notes
- [ ] All four instrumentation examples present: Node.js, PHP, iOS, Android

---

## Reading Material

| Priority | Resource | Format | Cost | Unlocks |
|----------|----------|--------|------|---------|
| 1 | *Observability Engineering* — Majors, Fong-Jones, Miranda (O'Reilly) | Book | ~$55 | Full observability skill content |
| 2 | *Site Reliability Engineering* — Google | Free (sre.google/books) | Free | SLO/SLI/error budget design |
| 3 | SigNoz documentation | Free (signoz.io/docs) | Free | Self-hosted setup and instrumentation |
| 4 | OpenTelemetry documentation | Free (opentelemetry.io/docs) | Free | SDK setup for all languages |
| 5 | Sentry documentation | Free (docs.sentry.io) | Free | Error tracking SDK integration |
| 6 | *Linux System Administration Handbook* — Nemeth et al. (5th ed.) | Book | ~$60 | Linux hardening depth |
| 7 | Prometheus documentation | Free (prometheus.io/docs) | Free | Metrics and PromQL |

**Read first:** *Observability Engineering* then the Google SRE Book (free). Both before writing the skill.

---

*Next → `phase-05-quality-e2e-testing.md`*
