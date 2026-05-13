# Absorbed Skill: cicd-pipeline-design

Original entrypoint: `skills/cicd-pipeline-design/SKILL.md`
Active parent skill: `skills/cicd-pipelines/SKILL.md`
Status: Absorbed as reference material; this file preserves the old skill content for progressive disclosure.

---
name: cicd-pipeline-design
description: Use when designing or reviewing production CI/CD pipelines, deployment
  pipelines, artifact promotion, branch strategy, release controls, rollback paths,
  and delivery-system metrics for any language or platform.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# CI/CD Pipeline Design
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Use when designing or reviewing production CI/CD pipelines, deployment pipelines, artifact promotion, branch strategy, release controls, rollback paths, and delivery-system metrics for any language or platform.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `cicd-pipeline-design` or would be better handled by a more specific companion skill.
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
| Release evidence | Pipeline design decision record | Markdown doc per `skill-composition-standards/references/adr-template.md` covering artifact-promotion, branch-strategy, and gate picks | `docs/ci/pipeline-design-adr.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Use this skill when the pipeline must function as a trusted delivery system. The goal is not merely automation. The goal is to keep changes small, verifiable, promotable, observable, and reversible.

## Load Order

1. Load `world-class-engineering`.
2. Load `deployment-release-engineering` for rollout and rollback design.
3. Load this skill to define the pipeline, artifact flow, and branch strategy.
4. Pair it with `advanced-testing-strategy`, `observability-monitoring`, and `cicd-devsecops`.

## Core Principles

- Pipeline is the only normal route to production.
- Build once and promote the same artifact through environments.
- Keep cheap checks early and deeper checks later, but do not remove meaningful risk checks.
- Treat broken default-branch pipelines as urgent delivery defects.
- Track throughput and stability together through DORA-style metrics.
- Optimise for flow, feedback, and learning: short-lived branches, visible queues, release markers, actionable alerts, and recurring pipeline-pain removal.

## Executable Outputs

For non-trivial pipeline work, produce:

- stage map with entry and exit criteria
- artifact promotion model
- branch and release-control model
- migration and rollback steps
- telemetry, alert, and release-marker plan
- pipeline bottlenecks and remediation priorities

## Pipeline Workflow

### 1. Define the Delivery Path

Capture:

- source control and branch strategy
- commit stage checks
- deeper validation stages
- artifact repository and promotion flow
- rollout path to each environment
- rollback or feature-disable path

### 2. Build a Canonical Stage Model

Use a shape like:

1. checkout and dependency restore
2. build and package
3. unit tests, lint, and static checks
4. security and dependency checks
5. artifact publish
6. deploy to lower environment
7. smoke, integration, contract, and acceptance checks as risk requires
8. performance or resilience checks where justified
9. production rollout and observation window

### 3. Design Artifact Promotion

- Promote the same artifact through environments.
- Keep environment differences in configuration and secrets, not rebuilt binaries.
- Version artifacts so release candidates, production builds, and ephemeral snapshots are distinguishable.
- Keep provenance and release notes attached to the promoted artifact.

### 4. Choose Branch and Release Controls

- Prefer trunk-based development or similarly short-lived branches.
- Use feature flags, dark launches, or canaries when deployment can complete before exposure should.
- Keep `main` or the releasable branch deployable.
- Require status checks and review on the branch that feeds production.

### 5. Design Migration and Rollback Safety

- Put schema and data changes into the pipeline explicitly.
- Use expand-contract for overlapping-version support on live systems.
- Define migration verification queries and rollback posture before release.
- Classify data changes as reversible, compensating-only, or forward-fix-only.

### 6. Observe and Improve the Pipeline

- Emit release markers so telemetry can answer what changed recently.
- Measure pipeline duration, red-time, flaky stages, and rerun frequency.
- Remove stale or low-signal stages that erode trust.
- Treat pipeline pain as engineering debt with owners and follow-up dates.
- Review the full value stream, not only tool execution time: branch age, manual approval delay, environment wait time, deployment queue time, and incident recovery time are pipeline design inputs.

## Standards

### Commit Stage

- Fast enough to run on every normal integration.
- Strong enough to reject obviously unsafe changes.
- Clear failure messages with links to evidence when possible.

### Promotion

- Artifact immutability is preferred.
- Rebuild drift between staging and production is not acceptable.
- Pipeline definition should live in version control.

### Branching

- Long-lived branches are a warning sign, not a default.
- Protect trunk quality with review, tests, and rapid repair of failures.
- Do not hide poor release slicing behind long integration delay.

### Release Evidence

- Keep records of what passed, what was skipped, and what remains unproven.
- Attach migration notes, rollback notes, and post-deploy watch lists to risky releases.
- Make observation ownership explicit for production rollout windows.

## Review Checklist

- [ ] The pipeline is the normal route to production.
- [ ] The same artifact is promoted through environments.
- [ ] Branch strategy keeps integration delay low.
- [ ] Stage purpose, owner, and failure evidence are explicit.
- [ ] Migration and rollback steps are part of the pipeline, not side notes.
- [ ] Release markers and telemetry support post-deploy diagnosis.
- [ ] Pipeline bottlenecks and flaky stages have remediation owners.

## FinOps and Cost Governance

The pipeline is also a cost surface: build minutes, runner sizing, cache effectiveness, artifact retention, and the clusters the pipeline deploys into all consume budget. Treat cost as a first-class delivery-system metric alongside throughput and stability.

### F.1 The FinOps Foundation framework

Source: FinOps Foundation framework page, https://www.finops.org/framework/.

Stated purpose: "FinOps is an operational framework and cultural practice which maximizes the business value of technology."

Four domains and their capabilities:

1. Understand Usage and Cost — Data Ingestion, Allocation, Reporting and Analytics, Anomaly Management.
2. Quantify Business Value — Planning and Estimating, Forecasting, Budgeting, KPIs and Benchmarking, Unit Economics.
3. Optimize Usage and Cost — Architecting and Workload Placement, Usage Optimization, Rate Optimization, Licensing and SaaS, Sustainability.
4. Manage the FinOps Practice — Executive Strategy Alignment, Practice Operations, Governance, Education and Enablement, Invoicing and Chargeback, Assessment, Automation and Tools, Intersecting Disciplines.

Six principles:

1. Teams need to collaborate.
2. Business value drives technology decisions.
3. "Everyone takes ownership for their technology usage."
4. FinOps data should be accessible, timely, and accurate.
5. "FinOps should be enabled centrally."
6. Take advantage of the variable cost model of the cloud.

Personas — Core: FinOps Practitioner, Engineering, Finance, Leadership, Procurement, Product. Allied: ITAM, ITFM, ITSM, Security, Sustainability.

### F.2 Inform / Optimize / Operate lifecycle

The framework's well-known three-phase operating model (confirm exact phase wording on the live page at implementation time):

- Inform — collect cost and usage data; tag resources; build dashboards; surface unit economics.
- Optimize — rightsize, eliminate waste, negotiate rates, schedule non-prod off-hours.
- Operate — embed cost into the engineering daily loop; budgets, alerts, automated guardrails.

Identify the team's current phase before recommending tools; skipping Inform produces dashboards no one trusts.

### F.3 Resource quotas — Kubernetes and cloud account

Kubernetes `ResourceQuota` (per-namespace) caps aggregate requests, limits, and object counts. `LimitRange` (per-namespace) sets defaults, mins, and maxes for individual containers. Combined, they prevent one namespace from starving others.

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-quota
  namespace: payments
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 40Gi
    limits.cpu: "40"
    limits.memory: 80Gi
    persistentvolumeclaims: "10"
    services.loadbalancers: "2"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: payments-defaults
  namespace: payments
spec:
  limits:
    - type: Container
      default:
        cpu: 500m
        memory: 512Mi
      defaultRequest:
        cpu: 100m
        memory: 128Mi
      max:
        cpu: "2"
        memory: 2Gi
```

Cloud-account level: AWS Service Quotas + IAM policies bounding instance types and regions; GCP quota policies and project-level budgets.

### F.4 Tagging / labelling taxonomy

Minimum-viable taxonomy (applies to AWS tags, GCP labels, and K8s labels):

| Tag / label   | Cardinality | Example                         |
|---------------|-------------|---------------------------------|
| `environment` | low         | `prod` / `staging` / `dev` / `preview` |
| `team`        | medium      | `payments`                      |
| `service`     | high        | `subscription-renewal-worker`   |
| `tenant`      | very high   | tenant id or hash (multi-tenant SaaS) |
| `cost-center` | medium      | `engineering-platform`          |

Enforce tag presence at admission time (Gatekeeper constraint — see `cicd-devsecops` policy guidance) and at IaC plan time (Terraform `default_tags`, OPA pre-plan checks). Tags are how every downstream FinOps capability — allocation, anomaly detection, chargeback, unit economics — actually works.

### F.5 Cost dashboards

- AWS Cost Explorer and AWS Cost and Usage Report (CUR): hierarchical breakdown by service, account, and tag; CUR exports to S3 for downstream BI. Pin a verified canonical URL from the AWS Cost Management documentation at implementation time.
- GCP Billing Reports and BigQuery billing export: daily granular billing data piped to BigQuery for SQL analysis. Pin the canonical post-redirect Cloud Billing docs URL at implementation time.

Both clouds support exporting to a warehouse and building unit-economics dashboards (cost per active tenant, cost per request) — this is the framework's Unit Economics capability.

### F.6 Budgets and alerts

Design against two failure modes:

1. Slow leak — small overspend that compounds over the month. Mitigation: percentage-of-forecast alerts (e.g., 80% of monthly forecast).
2. Sudden spike — a runaway loop, stuck retry, or accidental large instance. Mitigation: anomaly detection plus hard daily caps where the provider supports them.

Wire both alerts to the same channel that receives pipeline failures so cost regressions get the same response discipline.

### F.7 CI runner cost — self-hosted vs hosted

| Factor              | Hosted runners (GitHub / GitLab.com) | Self-hosted (Debian/Ubuntu VPS)         |
|---------------------|--------------------------------------|------------------------------------------|
| Per-minute cost     | Direct spend, $/min                  | Sunk capacity, opportunity cost          |
| Operational toil    | None                                 | Patching, scaling, security              |
| Build cache locality| Limited                              | Excellent (local Nexus, shared volumes)  |
| Egress              | Provider's                           | Yours                                    |
| Best fit            | Bursty, low-volume                   | High-volume, large-image, cache-sensitive |

Decision rule of thumb: if monthly hosted-runner spend exceeds 2× the cost of running 2–3 always-on self-hosted runners with capacity to spare, switch. Always keep hosted runners as a fallback and for jobs that must run outside your VPC.

For Jenkins / GitLab CE on self-managed Debian/Ubuntu (this repository's default stack), the cost equation is dominated by runner utilisation, cache hit rate, and artifact retention in Nexus — not per-minute billing. Track build-minute budgets per pipeline and cache hit rate per stage.

### F.8 Chargeback vs showback

| Mechanism  | Real money moves? | Cultural pre-requisite      | Accounting maturity        |
|------------|-------------------|------------------------------|-----------------------------|
| Showback   | No                | Cost-aware engineering       | Low — a dashboard suffices  |
| Chargeback | Yes (internal recharges) | Strong cost ownership   | High — internal billing process |

Most organisations should start with showback. Chargeback works only when "Everyone takes ownership for their technology usage" is operationally true.

### Pipeline-specific cost levers

- Build-minute budget per pipeline; alert when a pipeline's 7-day average exceeds its budget.
- Cache effectiveness target: ≥ 80% hit rate on dependency restore stages; track and alert on regression.
- Artifact retention: tiered policy in Nexus / S3 — release artifacts retained per compliance, snapshots aged out at 14–30 days, ephemeral PR builds at 7 days.
- Runner sizing: match runner CPU/memory to the largest stage's actual peak, not its theoretical peak; oversized runners idle most of the time.
- Schedule non-prod environments off outside business hours where the pipeline owns the lifecycle.

See [references/finops.md](references/finops.md) for worked examples, deeper governance patterns, and acceptance criteria for the FinOps section of a pipeline review.

## References

- [references/pipeline-governance.md](references/pipeline-governance.md): Pipeline trust, evidence, and stop-the-line response.
- [references/finops.md](references/finops.md): FinOps deep reference — lifecycle phase rules, tagging enforcement, ResourceQuota + LimitRange examples, runner crossover analysis, budget patterns, showback-to-chargeback transition, and review acceptance criteria.
- [../deployment-release-engineering/references/deployment-pipeline.md](../deployment-release-engineering/references/deployment-pipeline.md): Canonical release stage model and release packet.
- [../deployment-release-engineering/references/devops-book-patterns.md](../deployment-release-engineering/references/devops-book-patterns.md): DevOps value-stream, deployment, GitOps, observability, DevSecOps, and PHP runtime delivery patterns.
- [../world-class-engineering/references/source-patterns.md](../world-class-engineering/references/source-patterns.md): CI/CD and DevOps patterns derived from the supplied books.

