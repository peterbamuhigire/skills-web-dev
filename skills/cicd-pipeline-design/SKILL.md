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

## FinOps & Cost Governance

### Resource Tagging Strategy

Mandatory tag keys that every cloud resource must carry:

- `Environment` — `dev` / `staging` / `production`
- `Team` — owning team name (e.g., `payments`, `platform`)
- `CostCenter` — finance code for chargeback
- `Project` — logical project or product name
- `Owner` — primary on-call email

Enforce via Terraform `default_tags` at provider level:

```hcl
provider "aws" {
  region = "eu-west-1"
  default_tags {
    tags = {
      Environment = var.environment
      Team        = var.team
      CostCenter  = var.cost_center
      Project     = var.project
      Owner       = var.owner_email
      ManagedBy   = "terraform"
    }
  }
}
```

Enforce at admission time via AWS Config Rule `required-tags` or a Gatekeeper Constraint on K8s.

### AWS Cost Explorer & Budgets

- Cost Explorer: enable granularity by `DAILY`, group by `TAG:Team` and `TAG:Environment`
- Create a monthly budget via AWS CLI:

```bash
aws budgets create-budget \
  --account-id 123456789012 \
  --budget '{
    "BudgetName": "monthly-cap",
    "BudgetLimit": {"Amount": "500", "Unit": "USD"},
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST"
  }' \
  --notifications-with-subscribers '[
    {
      "Notification": {
        "NotificationType": "FORECASTED",
        "ComparisonOperator": "GREATER_THAN",
        "Threshold": 80,
        "ThresholdType": "PERCENTAGE"
      },
      "Subscribers": [{"SubscriptionType": "EMAIL", "Address": "finance@example.com"}]
    }
  ]'
```

- Anomaly detection: `AWS Cost Anomaly Detection` — subscribe to a SNS topic for `DAILY` anomaly alerts above threshold.

### Kubernetes Resource Quotas

Per-namespace `ResourceQuota`:

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
```

Cost per namespace tracking via Kubecost or OpenCost; correlate with CostExplorer via the `kubernetes.io/cluster/<name>` tag.

### Utilisation Targets

- CPU ≥ 70% average, memory ≥ 60% average across 30-day window
- Under-utilised = < 40% average CPU for 7+ days → right-size or consolidate
- Use AWS Compute Optimizer for EC2/RDS recommendations
- For K8s: VPA recommendations + HPA targets tuned to keep average between 60–80%

### Spot Instance Strategy

- CI runners: use `github-actions-runner-controller` on K8s with Spot node pool, `karpenter` provisioner filtering on Spot interruption rate
- Batch jobs / ML training: `aws ec2 run-instances` with `InstanceMarketOptions.MarketType=spot` and `MaxPrice` at 50% of on-demand
- Production web: only on Spot with multi-AZ / multi-instance-type diversification and graceful interruption handling (draining on `spot-instance-interruption-warning`)
- Never Spot for: stateful databases (RDS, Elasticsearch primary), single-replica critical services

### FinOps Maturity Model

Three stages — crawl / walk / run:

- **Crawl**: monthly manual cost review meeting, tags enforced on new resources, budget alerts wired to Slack. Expected savings: 10–15%.
- **Walk**: automated anomaly detection, dedicated cost owner per team, reserved instance strategy for steady-state workloads, right-sizing recommendations reviewed monthly. Expected savings: 20–30%.
- **Run**: chargeback to teams in internal accounting, cost impact reviewed per PR for significant infra changes, automated Spot/Reserved mix optimisation, unit economics dashboard ($/user, $/transaction). Expected savings: 30–45% plus improved decision quality.

Choose the stage that matches current operational maturity; do not skip stages.

## References

- [references/pipeline-governance.md](references/pipeline-governance.md): Pipeline trust, evidence, and stop-the-line response.
- [../deployment-release-engineering/references/deployment-pipeline.md](../deployment-release-engineering/references/deployment-pipeline.md): Canonical release stage model and release packet.
- [../world-class-engineering/references/source-patterns.md](../world-class-engineering/references/source-patterns.md): CI/CD and DevOps patterns derived from the supplied books.