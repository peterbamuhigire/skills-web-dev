# Multi-Tenancy Models on Kubernetes

Deep dive on tenancy models for SaaS running on Kubernetes. Read after the
`SKILL.md` overview. Cross-reference `multi-tenant-saas-architecture` for
non-Kubernetes tenancy patterns (application, database, auth), and
`kubernetes-production` for cluster-level concerns (autoscaling, upgrades).

## The four practical models

### 1. Pooled (shared everything)

Every Pod serves every tenant. Tenant identity is a column on every row and
a field in every request. Shared Services, shared Deployments, shared
Databases.

- Cost: lowest — capacity amortised across all tenants.
- Isolation: weak — a bug or hot query in one tenant affects everyone.
- Ops: simplest — one Deployment, one dashboard, one rollout.
- Fit: free tier, SMB, early-stage SaaS, metric cardinality bounded.

### 2. Namespace per tenant (shared cluster)

Each tenant gets a Kubernetes Namespace. Shared control plane, shared nodes
(by default), isolation via ResourceQuota, LimitRange, NetworkPolicy, and
tenant-scoped RBAC.

- Cost: moderate — some waste from per-tenant baseline Pods and sidecars.
- Isolation: good for compute, good for network, weak for kernel (shared
  nodes share a kernel; a container escape crosses tenants).
- Ops: manageable at hundreds to low thousands of tenants with GitOps.
- Fit: the default for most B2B SaaS between seed and Series C.

### 3. Cluster per tenant

Each tenant gets a dedicated cluster (often in a dedicated cloud account
or VPC).

- Cost: highest — control-plane and baseline per tenant, plus node
  minima.
- Isolation: strongest — hard kernel, network, and blast-radius
  separation; per-tenant upgrade windows; per-tenant data residency.
- Ops: hardest — fleet management, per-cluster upgrade automation,
  shared CD across N clusters.
- Fit: regulated sectors (health, finance, government), whales with
  custom SLAs, data residency requirements, BYOC offerings.

### 4. Hybrid (tiered)

Mix the above per plan tier. Typical pattern:

- Free or SMB tier: pooled.
- Business tier: namespace per tenant on a shared cluster.
- Enterprise tier: cluster per tenant (often in a region of choice).

Hybrid buys you the economics of pooled and the differentiation of
dedicated, but adds complexity to billing, onboarding, and control plane.

## Decision rule

```text
Is data co-mingling acceptable for this tenant?            -> No  -> Namespace or Cluster
Is the tenant paying for isolation or compliance?          -> Yes -> Cluster
Does the tenant need a custom upgrade window or version?   -> Yes -> Cluster
Noisy neighbour risk from tenant workload (AI, batch)?     -> Yes -> Namespace with taints
Tenants in the thousands, ARPU low?                        -> Yes -> Pooled
Tenants in the hundreds, ARPU moderate?                    -> Yes -> Namespace per tenant
Tenants in the tens, ARPU high, custom SLAs?               -> Yes -> Cluster per tenant
```

## Trade-off table

| Dimension         | Pooled            | Namespace/tenant  | Cluster/tenant   |
|-------------------|-------------------|-------------------|------------------|
| Cost per tenant   | very low          | low to moderate   | high             |
| Blast radius      | all tenants       | one namespace     | one cluster      |
| Compliance fit    | poor              | moderate          | strong           |
| Upgrade coupling  | all at once       | all at once       | per cluster      |
| Noisy neighbour   | hard to contain   | quotas + taints   | isolated         |
| Onboarding time   | seconds           | minutes           | minutes to hours |
| Offboarding       | row delete        | namespace delete  | cluster delete   |
| Per-tenant tuning | none              | quota, priority   | node class, SKU  |
| Data residency    | one region only   | cluster regions   | any region       |

## Migration paths between models

Migration always moves in the direction of more isolation, rarely less.

### Pooled to namespace per tenant

1. Add a `tenant_id` on every workload, Service, and Secret.
2. Introduce a control-plane job that provisions `tenant-<slug>`
   Namespaces with quotas and network policy.
3. Split shared data first (per-tenant schema or database), then split
   Pods.
4. Route by `tenant_id` at the ingress layer to the per-tenant Service.
5. Migrate tenants in cohorts: smallest first, whales last.

### Namespace to cluster per tenant

1. Stand up a new cluster per whale; reuse the same GitOps repo and
   ApplicationSet with a `cluster` generator.
2. Export tenant data; restore into the new cluster's data plane.
3. Cut DNS to the new cluster's ingress; keep read-only mode in the
   source cluster during the cutover.
4. Retain the source namespace for a deprecation window, then delete.

### Avoid reverse migration

Collapsing from cluster per tenant back to namespace per tenant is rare
and expensive. It usually indicates a pricing mistake rather than a
technical one.

## Anti-patterns

- Starting with cluster per tenant "to be safe" — you will burn 12
  months on fleet tooling that is not differentiated.
- Staying pooled past the point where one tenant's bug takes down the
  rest — the incident cost overtakes the isolation cost.
- Mixing models inside a tier without a clear rule — engineers will
  deploy differently for each tenant and drift wins.
- Letting tenants choose their model — tenants choose the most
  expensive option for free.

## Companion skills

- `multi-tenant-saas-architecture` for non-K8s tenancy patterns.
- `system-architecture-design` for control-plane decomposition.
- `reliability-engineering` for blast radius design.
- `cost-allocation.md` reference in this skill for economics.
