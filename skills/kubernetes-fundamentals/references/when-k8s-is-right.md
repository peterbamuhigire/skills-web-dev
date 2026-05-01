# When Kubernetes Is The Right Tool

Most Kubernetes pain comes from adopting it one stage too early. The cost of K8s is a small platform team, steep learning curve, upgrade treadmill, and a long tail of YAML. It pays back only when you have enough services, enough rollout frequency, and enough self-healing demand to justify it.

## Decision framework

Walk this ladder from top to bottom. Stop at the first row where the constraint fits.

| Shape of system | Fit | Why |
|---|---|---|
| 1 service, 1 VM, stable load, infrequent releases | `systemd` on Debian/Ubuntu | Plain process supervision is enough. Add `linux-security-hardening` baseline. |
| 1-5 services, 1-2 hosts, no autoscaling needed | Docker Compose on a VM | One file, one `docker compose up`, trivial to reason about. |
| 5-20 services, teams want independent releases, traffic spikes | Managed K8s (EKS, GKE, AKS) | Self-healing, rolling updates, HPA, and an ecosystem of operators justify the platform tax. |
| Web app + background workers, no K8s team, PaaS acceptable | ECS Fargate, Cloud Run, Heroku, Railway, Render, Fly.io | Paying a margin for managed runtime is cheaper than hiring a platform engineer. |
| Strict compliance, air-gapped, on-prem | Self-hosted K8s (kubeadm, k3s, RKE2, OpenShift) | Accept the ops cost; budget for two platform engineers minimum. |
| Single long-running batch job | `cron` + a script, or managed batch (AWS Batch, Cloud Run Jobs) | K8s Job/CronJob only if the rest of the estate is already K8s. |

## Cost and complexity snapshot

These numbers are order-of-magnitude; tune to your region and vendor.

| Platform | Monthly floor (infra) | Platform team needed | Time to first deploy | Upgrade cadence you own |
|---|---|---|---|---|
| systemd on one VM | USD 10-30 | 0 | Hours | OS patches only |
| Docker Compose on VM | USD 20-60 | 0 | Hours | OS + Docker |
| Cloud Run / Heroku / Railway | USD 0-50 idle, per-request after | 0 | Minutes | None |
| ECS Fargate | USD 50-200 | 0.25 FTE | Day | AWS-managed |
| GKE Autopilot | USD 75 control plane + pods | 0.5 FTE | Day | Minor versions quarterly |
| EKS + Karpenter | USD 75 control plane + nodes | 1 FTE | Week | Control plane + node AMIs + Karpenter + addons |
| Self-hosted kubeadm | Hardware + USD 0 software | 2+ FTE | Weeks | Full stack, including etcd |

## Signs you have outgrown the lower rungs

**Outgrown systemd on a single VM**

- You have added a second VM for HA and now maintain two copies of every change by hand.
- Deploys require SSH into the box and manual service restart.
- `journalctl` is your only observability and log rotation fails under load.
- A bad deploy has no automated rollback, only git revert plus re-run.

**Outgrown Docker Compose**

- You need more than one host. Compose is single-host by design; Swarm is effectively unmaintained.
- Services need independent rollout, blue-green, or canary.
- You want autoscaling by CPU, memory, or queue depth.
- You want one engineer to deploy without coordinating with others.

**Outgrown ECS Fargate**

- You hit ECS quotas (task definitions, parameters, target groups) and juggle workarounds.
- You need sidecars, init containers, and pod-level networking semantics.
- You want a richer ecosystem: operators, service mesh, progressive delivery controllers.
- You are multi-cloud or may be in 18 months.

**Outgrown Cloud Run / Heroku / PaaS**

- Cold starts hurt latency SLOs even with minimum instances.
- You need persistent volumes, stateful workloads, or long-running WebSockets at scale.
- Per-request pricing has passed the cost of running nodes 24x7.
- You are building a platform and need tenancy controls the PaaS cannot express.

**Outgrown managed K8s**

- You need hardware you cannot rent: GPUs with a specific driver stack, HSMs, bare-metal NVMe.
- Compliance requires you own the control plane and etcd keys.
- Data gravity or network egress cost forces on-prem.
- Only then adopt self-hosted; not before.

## Kubernetes cost drivers that surprise teams

- Control plane fee: EKS and GKE Standard both charge per cluster per hour. One cluster per environment adds up.
- Load balancers: a LoadBalancer Service per app is expensive. Prefer one Ingress controller with host/path routing.
- NAT egress: private nodes without VPC endpoints pay NAT Gateway fees per GB of egress.
- Observability stack: Prometheus + Loki + Grafana is not free. Managed Datadog or Grafana Cloud is faster but meters aggressively.
- Idle capacity: `requests` booked by Deployments reserve nodes even when traffic is low. Tune HPA and use Karpenter or cluster-autoscaler.

## Rules of thumb

- If one engineer can deploy every service via a shell script in 10 minutes, you do not need K8s yet.
- If you have fewer than five services and no plan to grow past ten, prefer ECS Fargate or Cloud Run.
- If you are a two-person team, avoid self-hosted K8s unless infrastructure is your product.
- If you already use a managed K8s in another product and your team knows it, carrying that skill forward is a valid reason to start there sooner.

## What K8s does not solve

- A bad deploy pipeline. Adopt `cicd-pipelines` and `deployment-release-engineering` first.
- A broken observability story. Logs, metrics, traces still need `observability-monitoring`.
- Tenancy and isolation. Namespaces are not a security boundary by default; see `kubernetes-saas-delivery`.
- Data model design. Your schema pain stays. See `database-design-engineering`.

## Migration order when you do adopt K8s

1. Containerise cleanly first; if the image is broken, K8s will not help.
2. Start with stateless workloads; leave databases on managed services.
3. Use a managed control plane: GKE Autopilot, EKS, or AKS. Do not self-host to learn.
4. Pick Helm or Kustomize and commit to one.
5. Run a non-production cluster for a full quarter before migrating production.
6. Move one bounded context at a time; do not lift-and-shift the monolith.

## Exit criteria before go-live on K8s

- Every workload has resource requests and limits.
- Every Service has a matching readiness probe.
- Rollout + rollback tested end-to-end with real traffic shape.
- PodDisruptionBudget on anything that cannot tolerate a node drain.
- Observability: logs shipped, metrics scraped, a real SLO with an alert.
- Disaster recovery: cluster rebuild runbook tested, not just written.

Load `cloud-architecture` alongside this file for the non-K8s options in full detail.
