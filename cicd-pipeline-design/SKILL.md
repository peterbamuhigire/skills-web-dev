---
name: cicd-pipeline-design
description: Design and implement production CI/CD pipelines — canonical stage sequence,
  DORA metrics, branching strategy, build-once-deploy-many, artifact management, and
  deployment strategies (blue-green, rolling, canary). Synthesised from DevOps Design
  Patterns (Chintale), CI/CD Unleashed (Clark 2025), CI/CD Pipeline with Docker and
  Jenkins (Rawat). Use when designing or reviewing a pipeline for any language or
  platform.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# CI/CD Pipeline Design

<!-- dual-compat-start -->
## Use When

- Design and implement production CI/CD pipelines — canonical stage sequence, DORA metrics, branching strategy, build-once-deploy-many, artifact management, and deployment strategies (blue-green, rolling, canary). Synthesised from DevOps Design Patterns (Chintale), CI/CD Unleashed (Clark 2025), CI/CD Pipeline with Docker and Jenkins (Rawat). Use when designing or reviewing a pipeline for any language or platform.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `cicd-pipeline-design` or would be better handled by a more specific companion skill.
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
**Target environment:** Self-managed Linux servers (Debian/Ubuntu). No cloud dependency required.

---

## Core Principles

- **Pipeline is the only route to production** — no direct server deploys, ever
- **Build once, deploy many** — build the artifact once; promote the same binary through all environments
- **Fail fast** — cheap checks (lint, unit tests) run first; expensive checks (E2E, perf) run later
- **Hermetic builds** — given the same inputs, the build always produces the same outputs
- **DORA metrics are your pipeline KPIs**: deployment frequency, lead time, MTTR, change failure rate

---

## 1. Canonical Pipeline Stages

Run stages in this order. Parallelise where marked.

```
Stage 1:  SCM Checkout
Stage 2:  Install Dependencies       ← proxy through Nexus for reliability
Stage 3:  Build                      ← Docker multi-stage preferred
Stage 4:  Unit Tests + Lint          ← PARALLEL; fail build if coverage drops below threshold
Stage 5:  Security Scan              ← OWASP DC (deps) + SonarQube (code) + Trivy (image)
Stage 6:  Version + Tag              ← semver from conventional commits; git tag the commit
Stage 7:  Publish Artifact           ← push Docker image or package to Nexus
Stage 8:  Deploy Dev                 ← Ansible playbook; DB migration (Flyway/Liquibase)
Stage 9:  Smoke Tests                ← hit /health + 2–3 critical journeys
Stage 10: Deploy Staging             ← blue-green or rolling; mirrors prod config
Stage 11: Integration + E2E Tests    ← API tests (Newman/Karate); UI tests (Playwright)
Stage 12: Performance Tests          ← only if contractual SLAs exist; gate on SLO thresholds
Stage 13: Deploy Production          ← main branch only; blue-green preferred; manual gate optional
Stage 14: Notify Stakeholders        ← Slack/Teams webhook (automated, not manual)
```

### Stage Rules

- Stages 4 (lint) and 4 (unit tests) must run in parallel — never sequentially
- Stage 5 security scan runs before artifact is published — never after
- Stage 13 only triggers on `main`/`master` branch — feature branches stop at Stage 10
- Never skip stages to "save time" — fix the underlying cause instead

---

## 2. Branching Strategy

Use **trunk-based development** for teams; **GitHub Flow** for solo/small teams.

```
main (trunk)          ← always deployable; protected branch
  ↑
feature/TICKET-123    ← short-lived (<2 days); merge via PR
  ↑
hotfix/TICKET-456     ← branches from main; merges back to main only
```

**Branch protection rules (enforce in GitLab/GitHub):**
- Require PR/MR approval before merge to `main`
- Require all pipeline stages to pass (status checks)
- Require signed commits for `main`
- No direct pushes to `main` — not even from admins

---

## 3. Build-Once, Deploy-Many

```
Build → Tag artifact with version → Store in Nexus
                                          ↓
                             Deploy same artifact to Dev
                                          ↓
                             Promote same artifact to QA
                                          ↓
                             Promote same artifact to Staging
                                          ↓
                             Promote same artifact to Production
```

**Never rebuild for each environment.** Config changes between environments via:
- Environment variables injected at deploy time (Ansible `vars`, Docker `--env-file`)
- HashiCorp Vault secrets pulled at runtime — never baked into images
- Config files rendered from templates by Ansible per environment

---

## 4. Artifact Management (Nexus 3)

Nexus 3 is the self-hosted standard. Install on a dedicated Debian server.

| Repository Type | Use |
|---|---|
| Docker (hosted) | Store built Docker images |
| Docker (proxy) | Cache Docker Hub pulls — eliminates rate limits |
| Maven (hosted) | Store Java JARs/WARs |
| npm (proxy) | Cache npm registry |
| PyPI (proxy) | Cache pip packages |
| Raw (hosted) | Store compiled binaries, APKs |

**Versioning convention:**
```
image:1.4.2          ← stable, promoted to prod
image:1.4.2-rc.1     ← release candidate, staging only
image:dev-abc1234    ← dev snapshot, never promoted
```

---

## 5. Deployment Strategies

### Blue-Green (Production Default)

```
Load Balancer
├── Blue (v1) ← live, 100% traffic
└── Green (v2) ← deploy here, run smoke tests
               ← switch traffic to Green (seconds)
               ← Blue becomes standby for rollback
```

- **Fastest rollback**: switch routing back to Blue in <30 seconds
- **Cost**: requires 2× resources during cutover window
- **Tool**: Traefik weighted routing or Nginx upstream swap

### Rolling (QA/Staging)

Replace instances one-by-one behind the load balancer. Zero downtime. Rollback is slow (also rolling).
Use for staging where resource cost matters more than rollback speed.

### Canary (Advanced)

```
Load Balancer
├── Stable (v1) ← 90% traffic
└── Canary (v2) ← 10% traffic → monitor DORA metrics → cut over
```

Use when you want data-driven promotion decisions. Requires load balancer with weighted routing.

---

## 6. Database Migrations

Run DB migrations as a pipeline stage **before** deploying new application code.

**Tool: Flyway or Liquibase** (both have Maven/Gradle plugins and Docker images)

```
Stage 8a: Run Flyway migrate (Dev DB)
Stage 8b: Deploy application (Dev)
...
Stage 13a: Run Flyway migrate (Prod DB) ← use expand-contract pattern for zero downtime
Stage 13b: Deploy application (Prod)
```

**Expand-contract pattern** for zero-downtime schema changes:
1. **Expand**: add new column (nullable); old code still runs
2. **Deploy**: new app code uses new column
3. **Contract**: drop old column in next release cycle

---

## 7. DORA Metrics — Pipeline KPIs

| Metric | Elite | High | Medium | Low |
|---|---|---|---|---|
| Deployment frequency | Multiple/day | Weekly | Monthly | <Monthly |
| Lead time for changes | <1 hour | <1 week | <1 month | >1 month |
| MTTR | <1 hour | <1 day | <1 week | >1 week |
| Change failure rate | 0–5% | 5–10% | 10–15% | >15% |

Track these in Grafana using Jenkins build data exported to Prometheus.

---

## 8. Monitoring Stack (Self-Hosted)

```
Application → metrics → Prometheus → dashboards → Grafana
Application → logs    → Loki       → dashboards → Grafana
Application → traces  → Jaeger     → dashboards → Jaeger UI
Prometheus  → alerts  → Alertmanager → Slack/PagerDuty
```

**Alert design rule** (from Clark 2025):
- **Alert**: human action required NOW (page someone)
- **Ticket**: action required within days (create a Jira ticket automatically)
- **Log**: diagnostic only (write to log, no human action)

Never page on metrics that don't require immediate human action — alert fatigue kills MTTR.

---

## 9. Pipeline as Code Rules

- Jenkinsfile/workflow YAML lives in the **application repository** alongside source code
- Changes to the pipeline go through the same PR review process as application code
- Never configure pipelines through UI — UI config is not version-controlled
- One Jenkinsfile per repo; use shared libraries for cross-repo patterns

---

## References

- `references/stage-templates.md` — Jenkinsfile snippets for each stage
- `references/nexus-setup.md` — Nexus 3 installation and repository configuration
- `references/dora-dashboard.md` — Prometheus metrics and Grafana dashboard config
