# RBAC and Pod Security Standards

RBAC controls *who* can do *what* to the cluster API. Pod Security Standards control *what* Pods may do at runtime. Both need to be least-privilege by default.

## RBAC — the four objects

```text
Role          -> namespace-scoped set of verbs on resources
ClusterRole   -> cluster-wide or template for namespace binding
RoleBinding   -> binds a Role to a subject in one namespace
ClusterRoleBinding -> binds a ClusterRole to a subject cluster-wide
```

Subjects can be: `User`, `Group`, or `ServiceAccount` (cluster-internal workload identity).

## ServiceAccount per workload — always

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: api
  namespace: production
automountServiceAccountToken: false      # turn off unless the app calls the K8s API
```

Rules:
- One ServiceAccount per workload (never share, never use `default`).
- `automountServiceAccountToken: false` unless the app genuinely talks to the K8s API.
- Turn it on explicitly at Pod spec level when needed.

### Pod-level override

```yaml
spec:
  serviceAccountName: api
  automountServiceAccountToken: true     # only for workloads that need API access
```

## Role — least privilege

Bad (wildcard):

```yaml
rules:
  - apiGroups: ["*"]
    resources: ["*"]
    verbs: ["*"]
```

Good (explicit):

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: { name: api-reader, namespace: production }
rules:
  - apiGroups: [""]
    resources: ["configmaps", "secrets"]
    resourceNames: ["api-config", "api-db"]       # scope to specific names
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["events"]
    verbs: ["create", "patch"]                      # emit events only
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata: { name: api-reader, namespace: production }
subjects:
  - kind: ServiceAccount
    name: api
    namespace: production
roleRef:
  kind: Role
  name: api-reader
  apiGroup: rbac.authorization.k8s.io
```

## ClusterRole — reuse across namespaces

Aggregated ClusterRoles allow permission composition:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: tenant-admin
  labels: { rbac.example.com/aggregate-to-tenant-admin: "true" }
aggregationRule:
  clusterRoleSelectors:
    - matchLabels: { rbac.example.com/aggregate-to-tenant-admin: "true" }
rules: []       # filled by aggregation controller
```

## Common anti-patterns

- Binding `cluster-admin` to a human user "temporarily" (it never ends).
- Using `system:masters` group for ServiceAccounts (bypasses all RBAC).
- Granting `secrets` `get` cluster-wide — lets a compromised workload steal everything.
- Permitting `pods/exec` outside debugging ServiceAccounts (= shell access to any Pod).
- Permitting `create` on `roles` or `rolebindings` — an attacker can escalate.

## Least-privilege recipes

### Read-only cluster observer (for Grafana/Prometheus)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata: { name: observer }
rules:
  - apiGroups: [""]
    resources: ["nodes", "nodes/metrics", "nodes/proxy", "services", "endpoints", "pods"]
    verbs: ["get", "list", "watch"]
  - nonResourceURLs: ["/metrics"]
    verbs: ["get"]
```

### CI deployer — scoped to one namespace

```yaml
kind: Role
metadata: { name: ci-deployer, namespace: production }
rules:
  - apiGroups: ["apps"]
    resources: ["deployments", "statefulsets"]
    verbs: ["get", "list", "watch", "patch", "update"]
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get", "list", "create", "update", "patch"]
```

No `delete`, no `create` on new types — forces review of destructive or structural changes.

## Audit unused bindings

```bash
# Find ClusterRoleBindings with no subjects (likely stale)
kubectl get clusterrolebindings -o json \
  | jq '.items[] | select(.subjects == null) | .metadata.name'

# Find everything bound to cluster-admin
kubectl get clusterrolebindings -o json \
  | jq '.items[] | select(.roleRef.name == "cluster-admin") | {name: .metadata.name, subjects: .subjects}'

# Use rbac-lookup
rbac-lookup --kind ServiceAccount --output wide
```

Tooling: `rbac-tool`, `rbac-lookup`, `kubectl-who-can`, `krane` for continuous auditing.

## Pod Security Standards (PSS) — three levels

Replace deprecated PodSecurityPolicy. Enforced natively by K8s 1.25+ at namespace level via labels.

| Level | Intent | Allowed |
|---|---|---|
| **privileged** | No restrictions | Everything (system workloads only) |
| **baseline** | Prevent known privilege escalations | No hostPath, no host namespaces, no privileged containers, no root capabilities beyond defaults |
| **restricted** | Hardened, current best practice | baseline + runAsNonRoot, seccomp RuntimeDefault, drop ALL capabilities, readOnlyRootFilesystem suggested |

### Namespace label enforcement

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/audit-version: latest
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/warn-version: latest
```

Three modes:
- **enforce** — block non-compliant Pods at admission.
- **audit** — record violations in audit log, allow.
- **warn** — return warning at `kubectl apply`, allow.

Rollout pattern: start with `warn` + `audit` → fix workloads → flip to `enforce`.

### A restricted-compliant Pod spec

```yaml
spec:
  serviceAccountName: api
  automountServiceAccountToken: false
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    runAsGroup: 10001
    fsGroup: 10001
    seccompProfile: { type: RuntimeDefault }
  containers:
    - name: api
      image: ghcr.io/acme/api:2025.10.3
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities: { drop: ["ALL"] }
      volumeMounts:
        - { name: tmp,       mountPath: /tmp }
        - { name: var-cache, mountPath: /var/cache }
  volumes:
    - name: tmp
      emptyDir: { medium: Memory, sizeLimit: 64Mi }
    - name: var-cache
      emptyDir: {}
```

Key points:
- `runAsNonRoot: true` — PSS restricted requires this. Add to your Dockerfile: `USER 10001`.
- `readOnlyRootFilesystem: true` — mount writable paths as `emptyDir`.
- `capabilities.drop: ["ALL"]` — almost no app needs Linux capabilities.
- `seccompProfile.type: RuntimeDefault` — the container runtime's default seccomp filter.

## PSS exemptions — narrow, tracked

Sometimes a workload legitimately needs baseline (log shipper reading host logs, CNI agent). Exempt at namespace level, not cluster-wide:

```yaml
metadata:
  name: kube-system
  labels:
    pod-security.kubernetes.io/enforce: privileged   # system namespace
```

Keep a documented list of which namespaces run at which level and why. Review quarterly.

## Running containers as non-root — common rewrites

Dockerfile:

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY --chown=10001:10001 . .
RUN npm ci --omit=dev
USER 10001
CMD ["node", "server.js"]
```

If the app binds to a port < 1024, either:
- Change the port to >= 1024 (recommended).
- Grant `CAP_NET_BIND_SERVICE` via securityContext (breaks `drop: ALL`).

## Admission control chain

Order a Pod passes through:

```text
AuthN -> AuthZ (RBAC) -> Mutating admission (webhooks, PSS label -> mutation)
      -> Validating admission (PSS enforce, Kyverno/Gatekeeper) -> etcd
```

PSS is implemented as a built-in admission controller. For policies richer than PSS offers (image registry allowlists, label requirements), add Kyverno or Gatekeeper — see `admission-control-opa-kyverno.md`.

## Review checklist

- [ ] Every workload has a dedicated ServiceAccount
- [ ] `automountServiceAccountToken: false` on workloads that do not call the API
- [ ] No `cluster-admin` bindings to human users or app ServiceAccounts
- [ ] No wildcards (`*`) in RBAC rules outside system namespaces
- [ ] All production namespaces labelled `pod-security.kubernetes.io/enforce: restricted`
- [ ] Container images run as non-root (`USER` in Dockerfile)
- [ ] `readOnlyRootFilesystem: true` with `emptyDir` for writable paths
- [ ] `capabilities.drop: ["ALL"]` on every container
- [ ] `seccompProfile: RuntimeDefault` on every container
- [ ] Quarterly audit of ClusterRoleBindings and stale ServiceAccounts
