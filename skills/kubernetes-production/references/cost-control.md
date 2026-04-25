# Cost Control — Kubecost, OpenCost, Right-Sizing, Spot, Karpenter

Kubernetes bills are dominated by over-provisioned requests and idle nodes. The wins come from measuring allocation vs usage, consolidating nodes, and using spot capacity where workloads tolerate it.

## Cost anatomy of a cluster

```text
Total cluster cost
  = compute (nodes, ~70%)
  + storage (PVs, ~15%)
  + network egress (~5-10%)
  + managed control plane (~2-5%)
  + observability storage (Prometheus, Loki retention)
```

Compute is where nearly all the optimisation lives. Storage is the next lever (unattached PVs, over-provisioned volume sizes). Network egress is painful for chatty microservices and cross-AZ traffic.

## OpenCost vs Kubecost

- **OpenCost** — open-source CNCF project, reads Prometheus data, computes per-workload cost. Free.
- **Kubecost** — commercial wrapper on top of OpenCost + extra features (recommendations, idle detection, multi-cluster, network cost, savings plans). Free tier for one cluster.

Start with OpenCost. Move to Kubecost (or Grafana Cloud Cost Analysis, CAST AI, etc.) when you need per-tenant chargeback, multi-cluster, or commitment/savings-plan blending.

### Install OpenCost

```bash
helm repo add opencost https://opencost.github.io/opencost-helm-chart
helm upgrade --install opencost opencost/opencost \
  -n opencost --create-namespace \
  --set opencost.exporter.defaultClusterId=prod-eu-west-1 \
  --set opencost.prometheus.internal.enabled=true \
  --set opencost.prometheus.internal.serviceName=kps-prometheus \
  --set opencost.prometheus.internal.namespaceName=monitoring
```

Grafana dashboards (id 18429, 18430) render the OpenCost metrics.

### Core OpenCost queries

```promql
# $/hour per namespace
sum by (namespace) (
  node_cpu_hourly_cost * kube_pod_container_resource_requests{resource="cpu"}
) +
sum by (namespace) (
  node_ram_hourly_cost * kube_pod_container_resource_requests{resource="memory"} / 1024 / 1024 / 1024
)
```

## Right-sizing — the biggest lever

Over-provisioning is the default. Aim for **CPU request ≈ p95 usage**, **memory request ≈ p95 + 20%**.

### Spot recommendations

Use VPA in recommend mode (see `resource-management.md`) or Kubecost recommendations. Typical wins on a greenfield cluster: 30–60% reduction in requested CPU.

### Process

1. Enable VPA recommend-only or Kubecost right-sizing.
2. Wait 7+ days for representative load.
3. Review recommendations by workload, sanity-check.
4. Apply in waves — start with largest overprovisioning, lowest risk.
5. After each wave: watch latency, error rate, OOMKills for 48h.
6. Repeat quarterly.

### PromQL — find the worst offenders

```promql
# Requested CPU / actual usage ratio (top 20 worst)
topk(20,
  sum by (namespace, pod) (kube_pod_container_resource_requests{resource="cpu"})
  /
  sum by (namespace, pod) (rate(container_cpu_usage_seconds_total{container!=""}[1h]))
)

# Same for memory
topk(20,
  sum by (namespace, pod) (kube_pod_container_resource_requests{resource="memory"})
  /
  sum by (namespace, pod) (container_memory_working_set_bytes{container!=""})
)
```

A ratio > 3 means "you reserved more than 3× what you use" — candidate for reduction.

## Spot / preemptible instances

Spot instances are 60–90% cheaper than on-demand with a catch: they can be reclaimed with 2 minutes' notice.

### Good fit

- Stateless APIs with HPA and PDB.
- Batch jobs / CI runners.
- Workers on idempotent queues.
- Dev/staging clusters entirely.

### Bad fit

- Stateful databases / quorum systems without replication to on-demand.
- Long-running jobs that cannot checkpoint.
- Ingress controllers (may survive if replicated; still prefer on-demand for stability).
- Leader-elected controllers with expensive re-election.

### Pattern: mixed spot + on-demand

```yaml
# Karpenter NodePool with spot-preferred
apiVersion: karpenter.sh/v1
kind: NodePool
metadata: { name: general-mixed }
spec:
  template:
    spec:
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot", "on-demand"]
        - key: karpenter.k8s.aws/instance-family
          operator: In
          values: ["m6i","m6a","m7i","c6i","c7i","r6i"]
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
    consolidateAfter: 30s
```

### Steer critical Pods to on-demand

```yaml
spec:
  template:
    spec:
      affinity:
        nodeAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              preference:
                matchExpressions:
                  - key: karpenter.sh/capacity-type
                    operator: In
                    values: ["on-demand"]
      tolerations:
        - key: spot
          operator: Exists
          effect: NoSchedule
```

Combine with `PodDisruptionBudget` (`minAvailable: 1`) so at least one on-demand replica survives a spot reclamation wave.

## Karpenter consolidation — always on

Consolidation shuts down underutilised nodes and re-schedules Pods onto fewer, cheaper instances. Biggest idle-capacity win.

```yaml
spec:
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
    consolidateAfter: 30s
    budgets:
      - nodes: "10%"                # don't churn more than 10% of nodes at once
      - nodes: "0"                  # pause during business hours
        schedule: "0 9 * * mon-fri"
        duration: 9h
```

## Idle resource alerts

Alerts worth paging (or at least ticketing):

```promql
# Namespace requesting > 3x what it uses
(
  sum by (namespace) (kube_pod_container_resource_requests{resource="cpu"})
  /
  sum by (namespace) (rate(container_cpu_usage_seconds_total{container!=""}[1d]))
) > 3

# PVs unattached (bound but zero activity) for 7 days
kube_persistentvolume_status_phase{phase="Released"} == 1

# Load balancers with no endpoints for 24h
kube_service_status_load_balancer_ingress * on (service) kube_endpoint_address_available == 0
```

## Storage cost hygiene

- Delete released PVs if the PVC is gone and `reclaimPolicy: Retain` leaked a volume.
- Downsize volumes to actual usage (requires backup + recreate; shrinking not supported online).
- Use lifecycle rules on object storage for backups and logs.
- Right-size Prometheus/Loki retention: tier to long-term storage instead of keeping 90d in Prometheus local disk.

```bash
# Find released PVs (orphaned)
kubectl get pv -o json | jq '.items[] | select(.status.phase=="Released") | .metadata.name'

# Find oversized PVCs (< 20% used)
kubectl get pvc -A -o json \
  | jq '.items[] | {ns:.metadata.namespace, name:.metadata.name, size:.status.capacity.storage}'
```

## Network egress

- Cross-AZ traffic is billed. Co-locate chatty services via `topologySpreadConstraints`.
- NAT gateway data-processing charges are significant; use VPC endpoints (S3, ECR, Secrets Manager) where possible.
- LoadBalancer per Service is expensive; use one Ingress (ALB/GLB) sharing an LB across many Services.

## Commitments and savings plans

For stable baseline capacity:
- AWS Savings Plans or Reserved Instances — 30–50% off.
- Karpenter/cluster autoscaler still scales on-demand/spot above the committed floor.
- Target utilisation of commitment: 85–95%.

## Dashboards — what to put in front of finance and engineers

- Cluster spend per day (trend, WoW/MoM).
- Cost per namespace / team / product (chargeback view).
- Spot vs on-demand mix and effective savings.
- Idle capacity $/day (unused reservations).
- Top 10 over-provisioned workloads.
- PV utilisation distribution.

## FinOps loop

1. **Inform** — show teams what they spend (Kubecost dashboards, per-namespace reports).
2. **Optimise** — right-size, consolidate, add spot, shorten retention.
3. **Operate** — budgets, alerts on anomalies, chargeback-backed decisions.

Run monthly: finance + platform + product teams review top 10 spenders and top 10 reductions.

## Anti-patterns

- "Just add more nodes" as a response to performance issues without checking resource saturation.
- Over-provisioning to hide a memory leak instead of fixing it.
- 100% on-demand for dev/staging clusters.
- Keeping 90 days of high-cardinality Prometheus data on local disk.
- No per-namespace ResourceQuota — any workload can burn the cluster budget.
- Treating observability as "free" and never aging out data.
- Ignoring cross-AZ traffic because it does not show on the workload's balance sheet.

## Review checklist

- [ ] OpenCost or Kubecost installed and dashboards shared with teams
- [ ] Monthly right-sizing review producing action items
- [ ] Karpenter consolidation enabled with sensible budgets
- [ ] Spot used for stateless workloads; steered away from critical services
- [ ] Savings plans / committed use covering 60–80% of baseline capacity
- [ ] ResourceQuota per namespace to cap blast radius
- [ ] Alerts on request/usage ratio > 3 per namespace
- [ ] Unattached PVs cleaned up quarterly
- [ ] Prometheus long-term storage tiered; local retention ≤ 30 days
- [ ] VPC endpoints used for S3, ECR, Secrets Manager
- [ ] Monthly FinOps review with finance + engineering
