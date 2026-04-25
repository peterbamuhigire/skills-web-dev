# Namespace Isolation Templates

Practical templates for isolating tenants within a shared Kubernetes cluster.
Read after the `SKILL.md` summary and the `multi-tenancy-models.md`
reference. Cross-reference `multi-tenant-saas-architecture` for the
application-layer isolation guarantees you still need.

## Guarantees this file gives you

- Compute containment: ResourceQuota and LimitRange.
- Network containment: NetworkPolicy default-deny plus allow-lists.
- Runtime safety: Pod Security Standards at `restricted`.
- Scheduling fairness: PriorityClass per tier and optional taints.
- Policy enforcement: Gatekeeper or Kyverno constraints for required labels.

## ResourceQuota template (per tier)

Quotas are always per tier, never bespoke per tenant. Use three tiers.

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: tenant-quota
  namespace: tenant-acme
  labels:
    tenant: acme
    tier: business
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "20"
    services: "10"
    services.loadbalancers: "0"
    services.nodeports: "0"
    persistentvolumeclaims: "5"
    requests.storage: 50Gi
    count/secrets: "30"
    count/configmaps: "30"
```

Tier table (starting point; tune per workload):

| Tier       | req.cpu | req.mem | lim.cpu | lim.mem | Pods | PVCs |
|------------|---------|---------|---------|---------|------|------|
| free       | 0.5     | 1Gi     | 1       | 2Gi     | 5    | 1    |
| business   | 4       | 8Gi     | 8       | 16Gi    | 20   | 5    |
| enterprise | 16      | 64Gi    | 32      | 128Gi   | 100  | 20   |

## LimitRange template

Pods without explicit requests break autoscaling and scheduling. Enforce
defaults at the namespace boundary.

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: tenant-limits
  namespace: tenant-acme
spec:
  limits:
    - type: Container
      default: { cpu: 500m, memory: 256Mi }
      defaultRequest: { cpu: 100m, memory: 128Mi }
      max: { cpu: "2", memory: 2Gi }
      min: { cpu: 10m, memory: 16Mi }
    - type: PersistentVolumeClaim
      max: { storage: 20Gi }
      min: { storage: 1Gi }
```

Decision rule: `max` on LimitRange must be less than or equal to
`limits.cpu` and `limits.memory` on ResourceQuota, otherwise Pods are
admitted but cannot schedule.

## NetworkPolicy — default-deny plus allow-lists

Default-deny everything, then allow the minimum surface.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny, namespace: tenant-acme }
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: allow-ingress-from-gateway, namespace: tenant-acme }
spec:
  podSelector: {}
  policyTypes: [Ingress]
  ingress:
    - from:
        - namespaceSelector:
            matchLabels: { kubernetes.io/metadata.name: ingress-nginx }
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: allow-egress-shared-infra, namespace: tenant-acme }
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
    - to:
        - namespaceSelector:
            matchLabels: { kubernetes.io/metadata.name: kube-system }
      ports: [{ protocol: UDP, port: 53 }, { protocol: TCP, port: 53 }]
    - to:
        - namespaceSelector: { matchLabels: { shared: "true" } }
          podSelector: { matchLabels: { app: postgres } }
      ports: [{ protocol: TCP, port: 5432 }]
    - to:
        - namespaceSelector: { matchLabels: { shared: "true" } }
          podSelector: { matchLabels: { app: redis } }
      ports: [{ protocol: TCP, port: 6379 }]
```

Rule: no Pod in a tenant namespace talks to another tenant's namespace,
ever. Shared infra (DB, Redis, object store) lives in its own namespace
with `shared: "true"` and explicit allow rules.

## Pod Security Standards (restricted)

Enforce `restricted` at the namespace level so non-root, no-privilege
escalation, and read-only root filesystem are the defaults.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: tenant-acme
  labels:
    tenant: acme
    tier: business
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
    shared: "false"
```

## PriorityClass per tier

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata: { name: tenant-enterprise }
value: 1000
globalDefault: false
description: Enterprise tenants — survive eviction first.
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata: { name: tenant-business }
value: 500
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata: { name: tenant-free }
value: 100
```

Gatekeeper or Kyverno enforces that Pods in `tenant-<slug>` namespaces
carry the matching `priorityClassName`.

## Gatekeeper constraint — required tenant labels

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata: { name: require-tenant-label }
spec:
  match:
    kinds: [{ apiGroups: [""], kinds: [Namespace] }]
    namespaceSelector:
      matchExpressions:
        - { key: kubernetes.io/metadata.name, operator: In,
            values: [] }  # populated by CI from tenant list
  parameters:
    labels:
      - key: tenant
      - key: tier
```

Also enforce that every Pod, Service, and PVC in a tenant namespace
carries `tenant=<slug>` — this powers cost reporting and observability.

## Tenant-scoped RBAC

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: { name: tenant-admin, namespace: tenant-acme }
rules:
  - apiGroups: [""]
    resources: [pods, services, configmaps, persistentvolumeclaims]
    verbs: [get, list, watch]
  - apiGroups: [apps]
    resources: [deployments, statefulsets]
    verbs: [get, list, watch]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata: { name: tenant-admin, namespace: tenant-acme }
subjects:
  - kind: Group
    name: "tenant:acme:admins"
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: tenant-admin
  apiGroup: rbac.authorization.k8s.io
```

Never grant `cluster-admin` or cross-namespace `list` to tenant users.

## Checklist

- [ ] Namespace carries `tenant`, `tier`, and PSS labels.
- [ ] ResourceQuota matches the tier table.
- [ ] LimitRange max values fit inside ResourceQuota.
- [ ] NetworkPolicy default-deny is installed first.
- [ ] PriorityClass matches tenant tier.
- [ ] Gatekeeper/Kyverno blocks namespace creation without required
      labels.
- [ ] Tenant RBAC is namespace-scoped, never cluster-scoped.
