# GitOps with ArgoCD for SaaS Delivery

Deep dive on ArgoCD for multi-tenant SaaS delivery. Git is the single source
of truth; ArgoCD reconciles cluster state to Git. Cross-reference
`deployment-release-engineering` for rollout discipline and
`cicd-pipelines` for CI that produces images and manifest PRs.

## Install

Install from upstream manifests or the official Helm chart. HA install is
mandatory for production (three `argocd-repo-server`, three
`argocd-application-controller` shards, Redis in HA mode).

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f \
  https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/ha/install.yaml
```

Expose the server via Ingress with TLS; never via NodePort. Front with
an identity-aware proxy or SSO.

## Repositories, Projects, Applications

- Repository: a Git repo registered with ArgoCD (SSH or HTTPS).
- Project: a logical boundary — source repos, destinations, RBAC.
- Application: one Git path reconciled to one cluster and namespace.

Use Projects to fence tenants and teams.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata: { name: tenants, namespace: argocd }
spec:
  description: All per-tenant applications
  sourceRepos:
    - git@github.com:acme/infra.git
  destinations:
    - server: https://kubernetes.default.svc
      namespace: "tenant-*"
  clusterResourceWhitelist: []
  namespaceResourceWhitelist:
    - { group: "*", kind: "*" }
  roles:
    - name: tenant-ops
      policies:
        - p, proj:tenants:tenant-ops, applications, sync, tenants/*, allow
        - p, proj:tenants:tenant-ops, applications, get,  tenants/*, allow
      groups: [platform-ops]
```

Project scopes prevent a tenant Application from accidentally creating
a ClusterRoleBinding or deploying into `kube-system`.

## ApplicationSets — the scaling primitive

A single Application per tenant does not scale past ~50 tenants by
hand. Use ApplicationSet with a generator that enumerates tenants.

### Git directory generator

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata: { name: tenant-apps, namespace: argocd }
spec:
  goTemplate: true
  generators:
    - git:
        repoURL: git@github.com:acme/infra.git
        revision: main
        directories:
          - path: tenants/*
  template:
    metadata:
      name: "{{.path.basename}}"
      labels: { tenant: "{{.path.basename}}" }
    spec:
      project: tenants
      source:
        repoURL: git@github.com:acme/infra.git
        path: "{{.path.path}}"
        targetRevision: main
      destination:
        server: https://kubernetes.default.svc
        namespace: "tenant-{{.path.basename}}"
      syncPolicy:
        automated: { prune: true, selfHeal: true }
        syncOptions: [CreateNamespace=true, ServerSideApply=true]
```

### List generator (explicit tenants)

```yaml
generators:
  - list:
      elements:
        - { tenant: acme,  tier: business,   cluster: https://eu.k8s }
        - { tenant: globex, tier: enterprise, cluster: https://us.k8s }
```

Use list for small, explicit fleets or for bootstrap.

### Cluster generator (fleet)

```yaml
generators:
  - clusters:
      selector:
        matchLabels: { env: prod }
```

Use when the same app must land on many clusters (regions, shards).

### Matrix generator (cluster x tenant)

```yaml
generators:
  - matrix:
      generators:
        - clusters: { selector: { matchLabels: { env: prod } } }
        - git:
            repoURL: git@github.com:acme/infra.git
            directories: [{ path: tenants/* }]
```

Matrix is the building block for regional-SaaS at scale.

## Sync waves and hooks

Sync waves order resources inside an Application.

```yaml
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "-1"
```

Common wave plan:

```text
-2   CRDs and PriorityClasses
-1   Namespaces, RBAC, NetworkPolicies, Quotas
 0   ConfigMaps, Secrets (ExternalSecret), Services
 1   Deployments, StatefulSets, Rollouts
 2   Ingress, HPAs, PDBs
 3   PostSync hooks (smoke tests, migration verifiers)
```

Hooks — `PreSync`, `Sync`, `PostSync`, `SyncFail` — run Jobs at specific
stages. Use `PreSync` for DB migrations; use `PostSync` for smoke tests;
use `SyncFail` to page on-call.

## ignoreDifferences — living with controllers

Some fields are mutated by controllers (HPA replicas, Service
`clusterIP`, webhook `caBundle`). Tell ArgoCD to ignore them or it
will fight the controller.

```yaml
spec:
  ignoreDifferences:
    - group: apps
      kind: Deployment
      jsonPointers: [/spec/replicas]
    - group: admissionregistration.k8s.io
      kind: MutatingWebhookConfiguration
      jqPathExpressions:
        - '.webhooks[].clientConfig.caBundle'
```

## SSO and RBAC

Plug ArgoCD into OIDC (Okta, Entra, Google, Keycloak). Map IdP groups
to ArgoCD RBAC roles. No local users except break-glass.

```yaml
apiVersion: v1
kind: ConfigMap
metadata: { name: argocd-rbac-cm, namespace: argocd }
data:
  policy.default: role:readonly
  policy.csv: |
    p, role:admin, applications, *, */*, allow
    p, role:tenant-viewer, applications, get, tenants/*, allow
    g, platform-engineers, role:admin
    g, support, role:tenant-viewer
```

Enforce MFA at the IdP, not in ArgoCD.

## ArgoCD vs Flux — choose one

| Dimension             | ArgoCD                      | Flux                       |
|-----------------------|-----------------------------|----------------------------|
| UI                    | rich, first-class           | minimal; add Weave GitOps  |
| ApplicationSet        | native, mature              | Kustomize + Flux           |
| Multi-cluster         | built-in cluster generator  | via Flux on each cluster   |
| Progressive delivery  | Argo Rollouts (same family) | Flagger (same family)      |
| OCI artifact GitOps   | supported                   | native, idiomatic          |
| Extensibility         | CMPs, plugins               | controllers, FluxCD source |

Pick one and commit. Running both doubles the operational cost with no
upside.

## Anti-patterns

- Using `kubectl apply` after ArgoCD is live — drift will eat your
  weekends. Either remove the access or configure ArgoCD with
  `selfHeal` plus Gatekeeper to block it.
- One Application for the entire platform — blast radius is the whole
  cluster on a bad sync.
- Hand-writing Applications per tenant — does not scale past 50.
- Enabling `selfHeal` without `prune` — you will leak orphaned
  resources on rename.
- Storing image tags as `latest` — ArgoCD cannot diff; you lose
  rollback.
