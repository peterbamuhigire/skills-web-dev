---
name: kubernetes-platform
description: Use as the index for Kubernetes work on this repo — routes to kubernetes-fundamentals
  for setup and core objects, kubernetes-production for Helm/scaling/security/observability, and
  kubernetes-saas-delivery for multi-tenancy and GitOps. Load this first to pick the right skill.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Kubernetes Platform — Navigator

<!-- dual-compat-start -->
## Use When

- Use as the index for Kubernetes work on this repo — routes to kubernetes-fundamentals for setup and core objects, kubernetes-production for Helm/scaling/security/observability, and kubernetes-saas-delivery for multi-tenancy and GitOps. Load this first to pick the right skill.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `kubernetes-platform` or would be better handled by a more specific companion skill.
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

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->

This skill is a navigator. It does not repeat content already covered in the three Kubernetes skills below; it decides which of them owns the task at hand.

## Baseline Load Order

Load skills in the order that matches the work:

1. New to Kubernetes, setting up a cluster, writing first manifests, debugging a single Pod — load `kubernetes-fundamentals`.
2. Running Kubernetes in production — Helm, autoscaling, secrets, observability, RBAC, Pod Security, NetworkPolicy, backups, cost control — load `kubernetes-production` after fundamentals.
3. Multi-tenant SaaS on Kubernetes, GitOps with ArgoCD or Flux, progressive delivery, tenant onboarding and offboarding — load `kubernetes-saas-delivery` after production.

Always layer upward. Do not skip `kubernetes-fundamentals` for a team new to K8s, and do not jump to `kubernetes-saas-delivery` without the production baseline in place.

## Topic Map

Every topic the repository covers on Kubernetes is owned by exactly one of the three skills below. Use this table to route work.

| Topic | Authoritative Skill | Section |
|---|---|---|
| Cluster Architecture and When K8s Is Right | `kubernetes-fundamentals` | When K8s Is the Right Tool; Cluster Options |
| Self-Managed Setup (kubeadm, k3s, kind) | `kubernetes-fundamentals` | Cluster Options |
| Core Workloads (Deployment, StatefulSet, DaemonSet, Job, CronJob) | `kubernetes-fundamentals` | Core Objects — The Mental Model |
| Services and Networking | `kubernetes-fundamentals` | Core Objects |
| Ingress and Ingress Controllers | `kubernetes-fundamentals` | Ingress Controllers |
| ConfigMaps and Secrets (basics) | `kubernetes-fundamentals` | Core Objects |
| Helm (and Helm vs Kustomize) | `kubernetes-production` | Helm vs Kustomize |
| Namespaces and RBAC | `kubernetes-production` | RBAC + Pod Security |
| Resource Management (requests, limits, ResourceQuota, LimitRange) | `kubernetes-production` | Resource Management |
| Pod Security (PodSecurityAdmission, restricted) | `kubernetes-production` | RBAC + Pod Security |
| Auto-Scaling (HPA, VPA, KEDA via Prometheus Adapter) | `kubernetes-production` | HPA — Horizontal Pod Autoscaler |
| Storage (PV, PVC, StorageClass, StatefulSet PVCs) | `kubernetes-production` | Stateful Workloads |
| Health Checks (liveness, readiness, startup probes) | `kubernetes-fundamentals` | Probes — Get Them Right |
| ArgoCD and GitOps (App of Apps, ApplicationSet, Flux) | `kubernetes-saas-delivery` | GitOps With ArgoCD |
| Deployment Strategies (rolling, blue-green, canary, Argo Rollouts) | `kubernetes-saas-delivery` | Progressive Delivery |
| Node Operations (drain, cordon, taints, tolerations) | `kubernetes-production` | Cost Control; Stateful Workloads |
| Observability (metrics-server, Prometheus, Grafana, Loki) | `kubernetes-production` | Observability Stack |
| Troubleshooting Playbook (CrashLoopBackOff, Pending, ImagePullBackOff) | `kubernetes-fundamentals` | kubectl Workflow |

## Common Task Recipes

- "Set up my first cluster on a VPS" — `kubernetes-fundamentals` (Cluster Options; Minimal Manifests).
- "Deploy a Next.js app with Helm and ArgoCD to production" — `kubernetes-production` (Helm, HPA, Observability) plus `kubernetes-saas-delivery` (GitOps) plus `cicd-pipelines`.
- "Harden Pod Security Admission to restricted" — `kubernetes-production` (RBAC + Pod Security).
- "Multi-tenant namespace isolation with RBAC and ResourceQuota" — `kubernetes-saas-delivery` (Namespace Isolation).
- "Progressive delivery with Argo Rollouts and Prometheus analysis" — `kubernetes-saas-delivery` (Progressive Delivery).
- "Troubleshoot CrashLoopBackOff or ImagePullBackOff" — `kubernetes-fundamentals` (kubectl Workflow; Probes).
- "Attribute cluster cost per tenant for billing" — `kubernetes-saas-delivery` (Cost Allocation) plus `kubernetes-production` (Cost Control).

## When to Stop Using Kubernetes

Kubernetes is overkill when any of the following hold:

- A single-tenant application with fewer than 3 long-running services.
- Team smaller than 5 engineers with no dedicated SRE or platform capacity.
- Predictable traffic that does not need horizontal scaling or self-healing on a 24x7 schedule.
- One person can deploy all services with a shell script in under 10 minutes.

Prefer a managed container platform instead: AWS ECS Fargate, Google Cloud Run, Fly.io, Render, Railway, or a PaaS. Revisit Kubernetes once service count, traffic variability, or compliance obligations outgrow the managed platform. See `kubernetes-fundamentals` Section "When K8s Is the Right Tool" for the full decision rule.

## Companion Skills

- `cloud-architecture` — VPC, load balancers, DNS, and the cloud substrate the cluster lives inside.
- `cicd-pipelines` — GitHub Actions workflows that build images and deploy to Kubernetes.
- `infrastructure-as-code` — Terraform modules that provision the cluster, node pools, and IAM.
- `observability-monitoring` — Prometheus, Grafana, logs, traces, SLOs, and alert routing beyond the cluster.
- `deployment-release-engineering` — release strategies, rollback patterns, and migration-safe deploys across stacks.

## Sources

- *Kubernetes in Action* (2nd ed.) — Marko Luksa (Manning).
- *Production Kubernetes* — Rosso, Lander, Brand, Harris (O'Reilly).
- Kubernetes documentation — `kubernetes.io/docs`.
- ArgoCD documentation — `argo-cd.readthedocs.io`.
- Helm documentation — `helm.sh/docs`.
