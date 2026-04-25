# Tenant Onboarding Automation

End-to-end automation for provisioning a tenant on Kubernetes. Three
implementation styles: GitOps-driven, operator-driven, and webhook
choreography. Read after `SKILL.md` and `gitops-argocd.md`. Cross-
reference `multi-tenant-saas-architecture` for the non-K8s parts of
tenant lifecycle.

## What "onboarding" means

A tenant goes from "signed up" to "fully provisioned" when all of:

- Tenant row exists in the control-plane DB with state `provisioning`.
- Kubernetes namespace created with quotas, limits, and network
  policies.
- Per-tenant secrets materialised from the secret store.
- Ingress or tenant subdomain resolves (`acme.app.example.com`).
- First admin user invited and verified.
- Billing account created in Stripe and linked.
- Observability wired (dashboards, alert routes, log labels).

Then, and only then, flip the state to `active`.

## Style 1: GitOps-driven (recommended default)

Flow:

```text
Signup API -> commit to infra-repo/tenants/<slug>/ -> PR auto-merge ->
ArgoCD ApplicationSet picks up -> namespace provisions ->
ArgoCD notifies back via webhook -> control-plane marks active
```

### Signup handler (pseudo-Go)

```go
func OnTenantCreated(t Tenant) error {
    tree := map[string]string{
        "kustomization.yaml":   renderKustomization(t),
        "namespace.yaml":       renderNamespace(t),
        "quota.yaml":           renderQuotaForTier(t.Tier),
        "externalsecret.yaml":  renderExternalSecret(t),
        "ingress.yaml":         renderIngress(t),
    }
    pr, err := gitCommitAndPR(
        repo:   "acme/infra",
        branch: fmt.Sprintf("tenant/%s", t.Slug),
        path:   fmt.Sprintf("tenants/%s", t.Slug),
        files:  tree,
        msg:    fmt.Sprintf("onboard tenant %s (%s)", t.Slug, t.Tier),
    )
    if err != nil { return err }
    return autoMerge(pr)
}
```

### ArgoCD completion webhook

Configure an ArgoCD notification on `on-sync-succeeded` that POSTs to
the control plane:

```yaml
apiVersion: v1
kind: ConfigMap
metadata: { name: argocd-notifications-cm, namespace: argocd }
data:
  trigger.on-tenant-ready: |
    - when: app.status.sync.status == 'Synced' and
            app.status.health.status == 'Healthy' and
            app.metadata.labels.tenant != ''
      send: [tenant-ready]
  template.tenant-ready: |
    webhook:
      tenant-callback:
        method: POST
        body: |
          {"tenant":"{{.app.metadata.labels.tenant}}","status":"active"}
```

### Why this is the default

- Every provisioning action is a Git commit — auditable, revertable.
- ArgoCD is already the reconciler; no second controller to operate.
- Rollback = `git revert`.

### Trade-offs

- Git is the critical path. A repo outage pauses onboarding.
- Template drift across tenants is possible without strong linting.

## Style 2: Operator-driven (Tenant CRD)

Use this when you need dynamic reconciliation beyond "render
templates" — for example, minting per-tenant databases, provisioning
managed cloud resources via Crossplane, or tenants with per-account IAM.

### CRD shape

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata: { name: tenants.saas.acme.io }
spec:
  group: saas.acme.io
  scope: Cluster
  names: { plural: tenants, singular: tenant, kind: Tenant }
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              required: [slug, tier]
              properties:
                slug: { type: string, pattern: "^[a-z0-9-]{3,40}$" }
                tier: { type: string, enum: [free, business, enterprise] }
                region: { type: string }
                dataResidency: { type: string }
            status:
              type: object
              properties:
                phase: { type: string }
                conditions: { type: array, items: { type: object } }
      subresources: { status: {} }
```

### Controller skeleton (Go, controller-runtime)

```go
func (r *TenantReconciler) Reconcile(ctx context.Context,
    req ctrl.Request) (ctrl.Result, error) {

    var t saasv1.Tenant
    if err := r.Get(ctx, req.NamespacedName, &t); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }
    if !t.DeletionTimestamp.IsZero() {
        return r.finalise(ctx, &t)
    }
    if err := r.ensureNamespace(ctx, &t); err != nil { return ctrl.Result{}, err }
    if err := r.ensureQuota(ctx, &t);     err != nil { return ctrl.Result{}, err }
    if err := r.ensureSecrets(ctx, &t);   err != nil { return ctrl.Result{}, err }
    if err := r.ensureIngress(ctx, &t);   err != nil { return ctrl.Result{}, err }
    if err := r.ensureBilling(ctx, &t);   err != nil { return ctrl.Result{}, err }
    return r.markActive(ctx, &t)
}
```

### Python alternative (kopf)

```python
import kopf, kubernetes

@kopf.on.create('saas.acme.io', 'v1', 'tenants')
def on_tenant_create(spec, name, **_):
    ensure_namespace(name, spec)
    ensure_quota(name, spec['tier'])
    ensure_external_secret(name)
    ensure_ingress(name, spec.get('region'))
    return {'phase': 'Active'}
```

### Trade-offs

- Operator is a new component to run, upgrade, monitor.
- Dynamic behaviour is easier than with GitOps.
- Still pairs well with ArgoCD — operator creates the CR, ArgoCD syncs
  the namespace manifests it generates.

## Style 3: Webhook choreography

The control plane fires webhooks; each downstream system (billing,
secrets, K8s, observability) listens and reports back. No central
controller.

```text
signup -> EventBus -> [k8s-provisioner, stripe-provisioner,
                      secrets-provisioner, obs-provisioner]
          each publishes "tenant.k8s.ready", etc.
control-plane aggregator waits for all -> tenant.active
```

Use when teams own their own pipelines and you want loose coupling.
Requires idempotent consumers, retries, and a saga-style tracker (see
`distributed-systems-patterns`).

## Decision rule

```text
Tenant provisioning = render manifests only?         -> GitOps
Tenant provisioning needs managed cloud resources?   -> Operator + Crossplane
Multiple independent teams own pieces?               -> Webhook choreography
Regulated, must be auditable end-to-end?             -> GitOps (git log is the audit)
```

## Idempotency and retries

- Every step must be idempotent — onboarding is retried on failure.
- Use server-side apply (`ServerSideApply=true`) to avoid last-writer-
  wins bugs.
- Record per-step status on the Tenant CR or in a control-plane table.
- Budget for partial failures: an orphaned namespace without billing is
  a daily alert, not a silent loss.

## Anti-patterns

- Manual `kubectl apply` to "fix" a failed onboarding — drift enters
  Git and ArgoCD will fight you.
- Non-idempotent onboarding — the first retry destroys tenant data.
- No rollback path — when onboarding breaks mid-way, you need a clean
  undo that works from Git alone.
- Hard-coded cluster in templates — you cannot move tenants between
  clusters later.
