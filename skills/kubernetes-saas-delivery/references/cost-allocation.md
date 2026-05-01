# Cost Allocation per Tenant

How to attribute cloud spend to tenants on Kubernetes, feed it to
billing, and catch waste early. Read after `SKILL.md`. Cross-reference
`multi-tenant-saas-architecture` for billing integration and
`saas-business-metrics` for unit economics.

## Why this matters

Without per-tenant cost, you cannot answer:

- Is this tenant profitable?
- Which tenants subsidise which?
- Which tier price is mispriced?
- Where is the platform leaking spend?

## The cost sources

```text
Compute       node hours x rate, attributed by Pod CPU/memory share
Storage       PVC GiB-month, S3 bucket GiB-month
Network       egress GB, inter-AZ GB
Managed svc   RDS, ElastiCache, OpenSearch, MSK
Third-party   Datadog, Stripe, Auth0, OpenAI tokens
```

Kubernetes cost tools (kubecost, OpenCost) cover compute, storage, and
in-cluster network. Everything else must be tagged at the cloud
resource level.

## kubecost namespace cost reports

kubecost or OpenCost reads Prometheus metrics plus cloud provider
pricing and emits per-namespace cost.

### Install and expose

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata: { name: kubecost, namespace: argocd }
spec:
  project: platform
  source:
    repoURL: https://github.com/kubecost/cost-analyzer-helm-chart
    targetRevision: prod-2.x
    chart: cost-analyzer
    helm:
      values: |
        prometheus: { server: { enabled: false } }
        global: { prometheus: { fqdn: http://prometheus.monitoring:9090 } }
        kubecostProductConfigs:
          clusterName: prod-eu-west-1
  destination: { server: https://kubernetes.default.svc, namespace: kubecost }
```

### Query per tenant cost

```bash
curl -s "http://kubecost:9090/model/allocation" \
  -G \
  --data-urlencode 'window=30d' \
  --data-urlencode 'aggregate=label:tenant' \
  --data-urlencode 'accumulate=true' | jq '.data[]'
```

Example output fields:

```json
{
  "name": "acme",
  "cpuCost": 41.22,
  "ramCost": 18.73,
  "pvCost": 9.11,
  "networkCost": 3.02,
  "totalCost": 72.08
}
```

## Karpenter nodepool tagging

When using Karpenter, tag nodepools by tier so cost tools can split
node-level cost by tenant cohort and let you enforce segregation.

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata: { name: tenant-enterprise }
spec:
  template:
    metadata:
      labels: { tier: enterprise }
    spec:
      taints:
        - { key: tier, value: enterprise, effect: NoSchedule }
      requirements:
        - { key: "kubernetes.io/arch", operator: In, values: [arm64] }
        - { key: "karpenter.sh/capacity-type", operator: In,
            values: [on-demand] }
      nodeClassRef: { name: default, group: karpenter.k8s.aws, kind: EC2NodeClass }
  limits: { cpu: 1000 }
```

Pods on this pool tolerate the `tier=enterprise` taint. Cloud cost
allocation tags propagate via the NodeClass — spend appears in the
cloud bill split by tier.

### Cloud tag policy

Every AWS resource carries `tenant`, `tier`, and `env` tags. Enforce
via AWS Organizations tag policies. In GCP, use labels. In Azure, use
tags.

## Idle detection

Find waste weekly:

- Pods requesting >2x their actual P95 CPU/memory usage (over-requested).
- Namespaces with Pods but no traffic for 7 days (forgotten).
- PVCs unattached for 14 days.
- LoadBalancers with no backend traffic for 30 days.

```promql
# Over-requested CPU by namespace
sum by (namespace) (kube_pod_container_resource_requests{resource="cpu"})
/
sum by (namespace) (rate(container_cpu_usage_seconds_total[7d])) > 2
```

Push the report into a ticket each Monday; do not leave it in a
dashboard no one reads.

## Tenant tier quotas and cost caps

Quotas (see `namespace-isolation.md`) already cap max spend per
tenant. Layer a secondary soft cap that alerts above a threshold.

```promql
# Alert when a tenant's monthly projected cost exceeds 120% of plan
(
  rate(kubecost_allocation_total_cost{namespace=~"tenant-.+"}[1d])
  * 30
) / on(namespace) group_left plan_cost_cap > 1.2
```

## Monthly reports

Automate a monthly export from kubecost into a warehouse (BigQuery,
Snowflake) joined against the tenant table for:

- Cost per tenant (compute, storage, network).
- Gross margin per tenant (revenue - cost - allocated shared cost).
- Cost per MAU, cost per transaction.
- Cohort trends (are new tenants cheaper or costlier than last
  quarter's cohort?).

### Shared cost allocation

Shared services (ingress, monitoring, logging, control plane) are
allocated proportionally by tenant compute share (simplest) or by
requests per tenant (most accurate).

```text
tenant_share = tenant_total_cpu / sum(all_tenant_cpu)
tenant_shared_cost = shared_pool_cost * tenant_share
```

Document the allocation method; auditors will ask.

## Attribution rules

- Free tier tenants are not billed; absorb their cost into customer
  acquisition expense.
- Enterprise tier tenants on dedicated clusters: 100% of the cluster
  cost plus a fraction of shared control plane.
- Noisy-neighbour tenants in pooled tier: bill at actual usage, not
  at tier flat rate — or move them up a tier.

## Anti-patterns

- Averaging cost across tenants — hides 80/20 distributions.
- Ignoring egress cost — it is frequently the largest line after
  compute.
- Billing based on sampled metrics without calibration — drift between
  kubecost and the cloud bill must stay under 5%.
- Leaking break-glass workloads into tenant cost — tag
  platform-operated jobs with `tenant=platform`.
- Not separating tenant data tax (backups, encryption, HA) from
  tenant feature cost — enterprise tenants see an inflated number
  and ask the wrong questions.
