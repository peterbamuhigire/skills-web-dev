# FinOps and Cost Governance — Deep Reference

Companion to the FinOps section of `SKILL.md`. Load when designing or reviewing the cost-governance posture of a delivery system.

## Source

- FinOps Foundation framework — https://www.finops.org/framework/.
- AWS Cost Management documentation — verify and pin a working canonical URL at implementation time.
- GCP Cloud Billing documentation — follow the redirect from `https://cloud.google.com/billing/docs` and pin the canonical post-redirect URL.
- Kubernetes documentation — `ResourceQuota` and `LimitRange` (pin to current API version at implementation time).

## Lifecycle phase decision rules

Use these to identify the team's current phase and the next move:

- No tag taxonomy enforced, no per-team cost view: still in **Inform**. Next move is admission-time tag enforcement plus a single dashboard the engineering leads agree on.
- Tags clean, dashboards exist, but no one acts on them: stuck between **Inform** and **Optimize**. Next move is to assign a cost owner per team and pick three concrete optimisation targets (idle envs, oversized runners, unused snapshots).
- Optimisations land but regressions appear weeks later: ready to move to **Operate**. Next move is automated guardrails — budget alerts, anomaly detection, hard caps where supported, and cost diffs in PR review.

Do not skip phases. A chargeback model on top of an unreliable tag taxonomy creates billing disputes, not cost discipline.

## Tagging enforcement patterns

- IaC plan time — Terraform `default_tags` at provider level + a Conftest / OPA policy that fails the plan when required tags are missing.
- Admission time — Gatekeeper `ConstraintTemplate` rejecting `Pod` / `Service` / `PersistentVolumeClaim` resources without the five mandatory labels (cross-reference `cicd-devsecops` for policy plumbing).
- Drift detection — daily job that lists untagged or mistagged resources and posts to the team channel; treat as a P3 ticket not a silent backlog.

## Worked ResourceQuota + LimitRange example

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: payments-quota
  namespace: payments
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 40Gi
    limits.cpu: "40"
    limits.memory: 80Gi
    persistentvolumeclaims: "10"
    services.loadbalancers: "2"
    count/jobs.batch: "50"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: payments-defaults
  namespace: payments
spec:
  limits:
    - type: Container
      default: { cpu: 500m, memory: 512Mi }
      defaultRequest: { cpu: 100m, memory: 128Mi }
      max: { cpu: "2", memory: 2Gi }
      min: { cpu: 50m, memory: 64Mi }
```

The `LimitRange` is what stops a single pod from consuming the namespace quota; without it, one runaway workload exhausts the quota and starves siblings.

## Pipeline cost levers — concrete targets

| Lever                        | Target / rule                                                  | Signal                                  |
|------------------------------|----------------------------------------------------------------|-----------------------------------------|
| Build-minute budget per pipeline | Set per-pipeline monthly budget; alert at 80% forecast      | 7-day rolling average exceeds budget    |
| Cache hit rate               | ≥ 80% on dependency restore stages                             | Drop > 10pp week-over-week              |
| Artifact retention           | Releases per compliance; snapshots 14–30d; PR builds 7d        | Nexus / S3 storage growth > 20% / month |
| Runner utilisation           | 50–75% average; scale down below, scale up above               | Sustained < 30% for 14d → consolidate   |
| Non-prod schedules           | Off outside business hours where pipeline owns lifecycle       | Non-prod cost < 30% of prod             |
| Egress per pipeline run      | Track per-stage bytes out; flag stages > 1 GiB                 | Sudden 2× regression                    |

## CI runner crossover — worked example

Assume a hosted runner costs $0.008 / minute and the pipeline consumes 200,000 build minutes / month: $1,600 / month. A self-hosted Debian runner on a 4 vCPU / 16 GiB VPS at $40 / month, with three always-on instances and a small build cache server, totals roughly $180 / month plus operational toil. Crossover is reached well before the 2× rule. Keep a hosted-runner pool for jobs that need clean-room network isolation (e.g., third-party penetration test scaffolds) and as the disaster fallback when self-hosted infra is degraded.

For Jenkins / GitLab CE on Debian/Ubuntu (the default stack here), the dominant levers are:

- agent JVM heap sized to the largest realistic build, not the theoretical peak.
- Nexus 3 as a local proxy cache for npm, Maven, PyPI, Docker — measure hit rate and fail loud when it regresses.
- Workspace cleanup policy on agents — stale workspaces silently consume disk faster than usage.
- Concurrent build cap per agent tuned to actual contention, not nominal CPU count.

## Budget and alert configuration patterns

Two failure modes:

1. **Slow leak** — monthly forecast crawls upward. Configure percentage-of-forecast alerts at 50%, 80%, and 100%. Route the 80% alert to engineering, the 100% alert to engineering + finance.
2. **Sudden spike** — anomaly detection on daily granularity, threshold tuned per service to suppress noise. Route to the on-call channel; treat as a P2 unless explained within an hour.

Where the provider supports hard caps (e.g., GCP project-level budget kill-switch via Pub/Sub + Cloud Function), enable them on non-prod environments. Production hard caps are usually unsafe — an outage is more expensive than an overspend.

## Showback to chargeback transition

A repeatable path:

1. Two months of clean tag data — no team disputes the allocation.
2. Three months of showback dashboards reviewed in monthly engineering reviews — teams act on the top three line items.
3. Pilot chargeback with one or two teams that have strong cost ownership culture; finance issues internal recharge but does not move money yet.
4. Full chargeback after one quarter of pilot stability, with an agreed dispute process and a quarterly review of the allocation rules.

Skipping straight to step 4 is the single most common reason FinOps programmes lose engineering trust.

## Acceptance criteria for a FinOps pipeline review

A pipeline review covers FinOps adequately when it includes:

- The five-tag taxonomy is enforced at IaC plan time and admission time, with drift detection.
- At least one `ResourceQuota` + `LimitRange` example per workload-bearing namespace.
- A monthly budget per pipeline and per environment with at least one forecast-percentage alert and one anomaly alert.
- A documented decision on chargeback vs showback, matched to current accounting maturity.
- A re-verified canonical URL for the chosen cloud's cost dashboard documentation.
- A CI-runner crossover note showing where the team currently sits and the next decision trigger.
- A unit-economics line item (cost per active tenant, cost per request, or equivalent) on at least one dashboard.

## Anti-patterns

- Treating cost dashboards as a finance artefact — engineering must own the day-to-day.
- Enforcing tags only at the dashboard layer — if untagged resources can be created, the data is permanently dirty.
- Optimising before informing — premature rightsizing without a baseline produces incidents, not savings.
- Using Spot / preemptible instances for stateful systems with no graceful interruption handling.
- Hiding non-prod cost behind production aggregates — non-prod is where most waste lives.
- Setting budgets and never reviewing them — stale budgets are noise, not signal.
