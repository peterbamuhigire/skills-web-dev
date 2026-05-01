# GitOps — ArgoCD and Flux Deep Reference

The Git repository is the single source of truth; a controller continuously reconciles the live cluster to match. Both tools implement the same pull-based reconciliation pattern; they differ in topology and UX.

## ArgoCD — Application and ApplicationSet

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata: { name: api, namespace: argocd }
spec:
  project: platform
  source:
    repoURL: https://github.com/acme/k8s-manifests.git
    targetRevision: main
    path: apps/api/overlays/prod
  destination:
    server: https://kubernetes.default.svc
    namespace: api-prod
  syncPolicy:
    automated: { prune: true, selfHeal: true }
    syncOptions: [CreateNamespace=true]
---
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata: { name: api-per-cluster, namespace: argocd }
spec:
  generators: [{ clusters: { selector: { matchLabels: { env: prod } } } }]
  template:
    metadata: { name: 'api-{{name}}' }
    spec:
      project: platform
      source: { repoURL: https://github.com/acme/k8s-manifests.git, path: 'apps/api/overlays/{{name}}', targetRevision: main }
      destination: { server: '{{server}}', namespace: api }
      syncPolicy: { automated: { prune: true, selfHeal: true } }
```

ArgoCD also exposes PreSync, Sync, and PostSync hooks for blue/green and canary rollouts.

## Flux — bootstrap and core resources

```bash
flux bootstrap github \
  --owner=acme --repository=fleet-infra \
  --branch=main --path=clusters/prod --personal
```

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata: { name: app-manifests, namespace: flux-system }
spec: { interval: 1m, url: https://github.com/acme/k8s-manifests, ref: { branch: main } }
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata: { name: api-prod, namespace: flux-system }
spec:
  interval: 5m
  path: ./apps/api/overlays/prod
  prune: true
  targetNamespace: api-prod
  sourceRef: { kind: GitRepository, name: app-manifests }
---
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata: { name: ingress-nginx, namespace: ingress }
spec:
  interval: 10m
  chart:
    spec:
      chart: ingress-nginx
      version: "4.10.x"
      sourceRef: { kind: HelmRepository, name: ingress-nginx, namespace: flux-system }
  values: { controller: { replicaCount: 2 } }
```

## Drift detection wiring

```yaml
# .github/workflows/drift.yml — scheduled Terraform drift detection
name: drift-detect
on: { schedule: [{ cron: '0 */6 * * *' }] }
jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - run: terraform init
      - run: |
          terraform plan -detailed-exitcode -lock=false || \
            { [ $? -eq 2 ] && echo "::error::drift detected" && exit 1; }
---
# argocd-notifications-cm — route OutOfSync to Slack
data:
  trigger.on-sync-status-unknown: |
    - when: app.status.sync.status == 'OutOfSync'
      send: [slack-out-of-sync]
  template.slack-out-of-sync: { message: "App {{.app.metadata.name}} drifted from Git" }
```

ArgoCD detects drift natively and flips `Application` to `OutOfSync`. For Terraform-managed resources, schedule `terraform plan -detailed-exitcode` every 6 hours and alert on exit code 2.

## Choosing between them

- ArgoCD: first-class web UI for app teams, per-app RBAC, ApplicationSet for multi-cluster fan-out.
- Flux: tight Helm + Kustomize integration with separable controllers, image-update-driven promotion, headless GitOps where every action is a Kubernetes resource.
