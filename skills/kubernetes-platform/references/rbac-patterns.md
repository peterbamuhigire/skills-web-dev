# RBAC Patterns

Pairs with `SKILL.md` §5.

## Layered Role Design

Platform clusters end up with three layers of access:

1. **Platform admins** — full cluster reach. Bind to `cluster-admin` for breakglass only; for daily work, bind a custom `ClusterRole` that excludes raw etcd, node proxy, and webhook configurations.
2. **Tenant admins** — full reach inside one namespace. The `ns-admin` Role in `SKILL.md` §5 is the template.
3. **Workload identities** — `ServiceAccount` per app, with the smallest namespaced `Role` that lets the app function (read its own ConfigMap, write its own Lease, etc.).

## Aggregated ClusterRoles

Aggregate fine-grained ClusterRoles into a top-level role using label selectors:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: platform-admin
aggregationRule:
  clusterRoleSelectors:
    - matchLabels: { rbac.example.com/aggregate-to-platform-admin: "true" }
rules: []   # filled by aggregation
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: platform-admin-nodes
  labels: { rbac.example.com/aggregate-to-platform-admin: "true" }
rules:
  - apiGroups: [""]
    resources: ["nodes"]
    verbs: ["get", "list", "watch", "patch"]
```

Adding a new capability is a one-line label addition, not a sprawling Role edit.

## OIDC Group Mapping

Bind RoleBindings to groups, never to individual users:

```yaml
subjects:
  - kind: Group
    name: oidc:platform-admins
    apiGroup: rbac.authorization.k8s.io
```

Configure the API server with `--oidc-issuer-url`, `--oidc-client-id`, `--oidc-username-claim`, and `--oidc-groups-claim`. Prefix groups (e.g. `oidc:`) so they cannot collide with built-in Kubernetes groups.

## Workload ServiceAccount Pattern

```yaml
apiVersion: v1
kind: ServiceAccount
metadata: { name: web, namespace: app, annotations: {} }
automountServiceAccountToken: false   # default-deny
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: { namespace: app, name: web }
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    resourceNames: ["web-config"]
    verbs: ["get", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata: { namespace: app, name: web }
subjects: [{ kind: ServiceAccount, name: web, namespace: app }]
roleRef:  { kind: Role, name: web, apiGroup: rbac.authorization.k8s.io }
```

If the workload does not call the API, set `automountServiceAccountToken: false` on the pod and on the ServiceAccount.

## Audit and Review

- Enable API server audit logging (`--audit-policy-file`, `--audit-log-path`).
- Ship audit logs to the same observability backend as application logs.
- Quarterly review: `kubectl auth can-i --list --as=system:serviceaccount:<ns>:<sa>` for every workload SA; remove unused verbs.
- `kubectl get clusterrolebindings,rolebindings -A -o wide` and diff against a checked-in inventory.

## Breakglass

- A dedicated `breakglass` user with `cluster-admin`, kept in a separate identity provider or a sealed `kubeconfig` in a vault.
- Use only on incident; rotate credentials immediately after.
- Audit log entries for the breakglass user trigger an alert by default.

## Anti-Patterns

- Granting `cluster-admin` to a tenant team because RBAC felt slow.
- Wildcard verbs (`["*"]`) on wildcard resources at cluster scope.
- Using the `default` ServiceAccount for workloads.
- Long-lived static `kubeconfig` files for human users instead of short-lived OIDC tokens.
