# Multi-Tenant Isolation — Namespace vs vCluster vs Cluster

Three real isolation choices. Pick the weakest one that meets your isolation, blast-radius, and compliance requirements.

## The three models

| Model | Isolation | Cost / tenant | Ops cost | Tenant API access |
|---|---|---|---|---|
| Namespace per tenant | Soft (RBAC, NetworkPolicy, quotas) | Lowest | Low | Restricted to namespace |
| vCluster (loft.sh) | Medium (dedicated control plane in a Pod) | Low-medium | Medium | Full kube-API inside the vCluster |
| Cluster per tenant | Hard (separate kube-apiserver, etcd, nodes) | High | High | Full and isolated |

## Decision rule

```text
Tenants do not touch the Kubernetes API directly                            -> namespace
Tenants need their own CRDs / operators / kubectl access                    -> vCluster
Compliance mandates separate control plane / data residency / hard tenancy  -> cluster
Noisy-neighbour CPU/memory dominates and quotas are not enough              -> cluster (or dedicated nodepool per tenant)
Per-tenant cost > $X/month and tenant count is bounded                      -> reconsider; namespace is almost always cheaper
```

## Namespace tenancy — what you must combine

A namespace alone is not a tenant boundary. It only becomes one when you stack:

1. `ResourceQuota` (CPU, memory, Pods, PVCs, LoadBalancers).
2. `LimitRange` (defaults so tenants cannot ship Pods with no limits).
3. Default-deny `NetworkPolicy` + explicit allows.
4. Pod Security Standards `restricted` enforced on the namespace.
5. Tenant-scoped RBAC (Role, never ClusterRole).
6. Per-tenant ServiceAccount; never share SAs across tenants.
7. `automountServiceAccountToken: false` by default; opt in per workload.
8. Distinct PriorityClass per tier so noisy free-tier work cannot evict paid work.
9. Per-tenant ingress with TLS; never share Ingress objects across tenants.
10. Audit logs filtered by namespace shipped to tenant-isolated storage if contractual.

What namespaces do NOT isolate:

- The Kubernetes API itself — a tenant with `get configmaps -A` sees everything.
- The kernel — a container escape exits the tenant boundary.
- Node-local resources — disk, PIDs, inotify watches, file descriptors.
- CRDs — they are cluster-scoped; tenants cannot have their own CRDs without conflict.

## vCluster — when the kube-API is the product

A vCluster runs a dedicated kube-apiserver, controller-manager, and scheduler inside Pods of a host namespace. Tenant workloads schedule onto host nodes via the vCluster syncer.

Use when:

- Tenants need to install their own CRDs/operators (e.g., dev sandboxes, internal platforms).
- Tenants want kubectl access without seeing other tenants.
- You want a per-tenant API audit log without provisioning real clusters.

Tradeoffs:

- Each vCluster adds a control-plane Pod set and etcd (or sqlite) — non-zero overhead.
- Pod scheduling still shares host nodes — you still need quotas + Pod Security on the host.
- Backup/restore is per-vCluster.
- Networking still shares the host CNI — NetworkPolicy on the host applies.

## Cluster per tenant — when isolation is the contract

Pick this when:

- Regulatory requirement: separate control plane, separate audit trail, separate node pool.
- Tenants get their own region / data residency.
- Single tenant is large enough to justify the cost.
- You can automate cluster provisioning end-to-end (Terraform + Crossplane + Argo).

Operational cost is real: control plane fees, separate observability stacks (or per-tenant Prom remote-write to a central Mimir/Thanos), separate upgrade cycles, separate backup runs.

## Hybrid is the common answer

Most production SaaS ends up here:

- Free / SMB -> pooled or namespace.
- Business -> namespace per tenant on a shared cluster.
- Enterprise -> cluster per tenant (or dedicated nodepool per tenant on a shared control plane).

Hybrid means tooling has to handle all three. Do not under-invest in the automation.

## Cross-cutting controls regardless of model

- Image provenance: tenants pull only from your allowed registries (admission control).
- Egress control: NetworkPolicy egress rules + an egress gateway (Cilium, Istio) so a compromised tenant cannot exfiltrate to the internet.
- Resource fairness: HPA + Cluster Autoscaler + per-tenant priority classes.
- Tenant-scoped observability: every metric and log carries a `tenant` label, enforced by relabeling.
- Tenant offboarding tested quarterly. See `offboarding-data-deletion.md`.

## Anti-patterns

- Calling a namespace "isolated" without quotas, NetworkPolicy, and Pod Security.
- Sharing a default ServiceAccount across tenants.
- A single Grafana org for all tenants with no folder/data-source isolation.
- Giving tenants a ClusterRole "for convenience".
- Mixing vCluster and namespace tenants on the same nodepool with no priority classes — noisy neighbours guaranteed.
- Cluster per tenant without provisioning automation — fleet drift within months.
