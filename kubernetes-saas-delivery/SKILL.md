---
name: kubernetes-saas-delivery
description: Use when running multi-tenant SaaS on Kubernetes — namespace isolation,
  per-tenant deploys, ArgoCD/Flux GitOps, progressive delivery (Argo Rollouts/Flagger),
  tenant onboarding automation, cost allocation, and data deletion.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Kubernetes for SaaS Delivery

<!-- dual-compat-start -->
## Use When

- Use when running multi-tenant SaaS on Kubernetes — namespace isolation, per-tenant deploys, ArgoCD/Flux GitOps, progressive delivery (Argo Rollouts/Flagger), tenant onboarding automation, cost allocation, and data deletion.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `kubernetes-saas-delivery` or would be better handled by a more specific companion skill.
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
| Release evidence | Multi-tenant rollout plan | Markdown doc per `skill-composition-standards/references/release-plan-template.md` covering per-tenant deploy waves and rollback waves | `docs/k8s/tenant-rollout-2026-04-16.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Multi-tenant SaaS on K8s plus GitOps delivery. Where `kubernetes-production` gets the cluster right, this skill gets the tenant model and delivery right.

**Prerequisites:** Load `kubernetes-fundamentals` and `kubernetes-production`. Load `multi-tenant-saas-architecture` for non-K8s tenancy patterns.

## When this skill applies

- Designing tenancy for a new SaaS on K8s.
- Setting up GitOps delivery (ArgoCD or Flux).
- Adopting progressive delivery (canary/blue-green).
- Automating tenant onboarding/offboarding.
- Attributing cost per tenant.

## Multi-tenancy models

```text
Pooled:        all tenants share Pods, tenant_id in every request
               lowest cost, highest blast radius on bugs
Namespace/tenant: each tenant gets a namespace, shared cluster
               balanced; most common for B2B SaaS
Cluster/tenant:  each tenant gets a cluster
               highest isolation; highest cost; for regulated / large tenants
Hybrid:        pooled free tier, namespace per paid, cluster per enterprise
```

Decision rule:

```text
Free/SMB tenants (1000s, small)                              -> Pooled
Business tenants (100s, medium, need isolation)             -> Namespace per tenant
Enterprise tenants (tens, custom SLAs, compliance)          -> Cluster per tenant
```

See `references/multi-tenancy-models.md`.

## Namespace isolation

Per-tenant namespace with:

- **ResourceQuota:** cap CPU/memory/Pods/PVCs.
- **LimitRange:** default requests/limits per container.
- **NetworkPolicy:** default-deny + allows to shared infra (DB, Redis, ingress).
- **Pod Security Standards:** `restricted`.
- **Priority class:** separate priority classes per tier (enterprise > business > free).
- **Tenant-scoped RBAC:** tenant admin token has Role-level access to their namespace only.

```yaml
apiVersion: v1
kind: ResourceQuota
metadata: { name: tenant-quota, namespace: tenant-acme }
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "20"
    persistentvolumeclaims: "5"
---
apiVersion: v1
kind: LimitRange
metadata: { name: tenant-limits, namespace: tenant-acme }
spec:
  limits:
    - type: Container
      default: { cpu: 500m, memory: 256Mi }
      defaultRequest: { cpu: 100m, memory: 128Mi }
      max: { cpu: "2", memory: 2Gi }
```

See `references/namespace-isolation.md`.

## GitOps with ArgoCD

Git is the source of truth; ArgoCD syncs cluster state to Git.

**App of Apps** pattern — one root ArgoCD Application that points at a Git directory of child Applications.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: tenants
  namespace: argocd
spec:
  project: default
  source:
    repoURL: git@github.com:acme/infra.git
    path: tenants/
    targetRevision: main
  destination: { server: https://kubernetes.default.svc, namespace: argocd }
  syncPolicy:
    automated: { prune: true, selfHeal: true }
```

**ApplicationSet** generates Applications from Git directories or lists — scale to hundreds of tenants without duplicating YAML:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata: { name: tenant-apps, namespace: argocd }
spec:
  generators:
    - git:
        repoURL: git@github.com:acme/infra.git
        revision: main
        directories: [{ path: tenants/* }]
  template:
    metadata: { name: "{{path.basename}}" }
    spec:
      project: default
      source:
        repoURL: git@github.com:acme/infra.git
        path: "{{path}}"
        targetRevision: main
      destination:
        server: https://kubernetes.default.svc
        namespace: "tenant-{{path.basename}}"
      syncPolicy: { automated: { prune: true, selfHeal: true } }
```

**Sync waves** order resources (CRDs first, then apps). **Drift detection** catches manual edits.

**ArgoCD vs Flux:** both are excellent. ArgoCD has better UI, ApplicationSets, and broader adoption. Flux is more GitOps-purist and pairs with Flagger for progressive delivery. Pick one; don't run both.

See `references/gitops-argocd.md`.

## Progressive delivery

- **Argo Rollouts** — replaces Deployment with Rollout resource; canary / blue-green with analysis templates that query Prometheus / Datadog.
- **Flagger** — works with Flux; Service mesh or Ingress integration for traffic splitting.

Canary pattern:

1. Deploy new version to 10% of traffic.
2. Analysis template checks error rate, latency, custom SLO metrics for 10 minutes.
3. If pass: shift to 25%, 50%, 100%.
4. If fail: auto-rollback.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata: { name: api }
spec:
  strategy:
    canary:
      steps:
        - setWeight: 10
        - pause: { duration: 5m }
        - analysis:
            templates: [{ templateName: success-rate }]
            args: [{ name: service, value: api }]
        - setWeight: 25
        - pause: { duration: 5m }
        - setWeight: 50
        - pause: { duration: 5m }
        - setWeight: 100
```

See `references/progressive-delivery.md`.

## Tenant onboarding automation

Operators (custom controllers) or GitOps-driven automation:

**GitOps approach (simpler):**

1. Trigger: new tenant created in app DB.
2. App writes a Git commit to `infra-repo/tenants/<tenant-slug>/kustomization.yaml`.
3. ArgoCD ApplicationSet picks it up → creates namespace + quota + secrets + ingress.
4. App receives webhook when Application is healthy → marks tenant as "provisioned."

**Operator approach (dynamic):**

1. Custom `Tenant` CRD.
2. Operator reconciles `Tenant` resources → creates all child resources.
3. Tenant app reads CRD status.

GitOps is recommended unless dynamic lifecycle is truly needed.

See `references/tenant-onboarding-automation.md`.

## Per-tenant secrets

Tenant secrets via external-secrets operator keyed by tenant:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata: { name: tenant-db, namespace: tenant-acme }
spec:
  refreshInterval: 1h
  secretStoreRef: { name: aws-secretsmanager, kind: ClusterSecretStore }
  target: { name: tenant-db }
  data:
    - secretKey: database-url
      remoteRef: { key: "tenants/acme/database-url" }
```

Never hardcode tenant IDs in shared secrets. Never share DB credentials across tenants.

See `references/per-tenant-secrets.md`.

## Observability per tenant

- **Labels:** every metric carries `tenant` label. Use `kube-state-metrics` + relabeling.
- **Grafana folders per tenant** — tenant admins see only their dashboards.
- **Alert routing:** Alertmanager routes based on `tenant` label to per-tenant receivers (email/Slack/webhook).
- **Log isolation:** Loki LogQL filter on `tenant` label. Per-tenant dashboards.

Beware cardinality — a label with 10,000 unique values across metrics = Prometheus dies. Prefer tenant label only on key SLO metrics.

See `references/tenant-observability.md`.

## Cost allocation

- **kubecost** or **OpenCost** — compute per-namespace CPU/memory/storage/network cost.
- Tag cloud resources with `tenant` label where possible (nodes via karpenter nodepool).
- Monthly cost-per-tenant report fed to billing or product.
- Outliers: flag tenants consuming >N× their plan quota.

See `references/cost-allocation.md`.

## Offboarding + data deletion

A clean offboarding procedure is as important as onboarding:

1. Mark tenant as "offboarding" in app DB.
2. Suspend ingress (deny all traffic).
3. Final backup of tenant data to off-cluster storage (retention per contract).
4. Delete tenant namespace → all resources (Pods, PVCs, Secrets) GC'd.
5. Remove tenant row from Git repo → ArgoCD prune → no orphan Apps.
6. Delete tenant secrets from cloud secret manager.
7. Remove tenant from observability dashboards.
8. Keep audit log of deletion for compliance.

Compliance note: some regions require verifiable deletion — document and test this path.

See `references/offboarding-data-deletion.md`.

## Anti-patterns

- One cluster, one namespace, tenant_id everywhere, no isolation at all.
- Deploying a Helm chart per tenant manually.
- Tenant credentials in a shared Secret across namespaces.
- Grafana dashboards without tenant filtering — tenant A sees tenant B data.
- No PodDisruptionBudget on tenant workloads — tenant downtime during node upgrades.
- Skipping offboarding procedure — orphaned resources accumulate cost and risk.
- Mixed GitOps + `kubectl apply` — drift forever.
- Scaling tenants on a single cluster without capacity planning — noisy neighbours.

## Read next

- `multi-tenant-saas-architecture` — non-K8s tenancy patterns.
- `distributed-systems-patterns` — cross-service consistency.
- `observability-monitoring` — SLOs, alerts, runbooks.
- `deployment-release-engineering` — rollout + rollback discipline.

## References

- `references/multi-tenancy-models.md`
- `references/namespace-isolation.md`
- `references/gitops-argocd.md`
- `references/progressive-delivery.md`
- `references/tenant-onboarding-automation.md`
- `references/per-tenant-secrets.md`
- `references/tenant-observability.md`
- `references/cost-allocation.md`
- `references/offboarding-data-deletion.md`
