# Pod Security Migration and NetworkPolicy

Pairs with `SKILL.md` §7.

## Migrating a Namespace from Baseline to Restricted

Pod Security Admission supports three modes per profile: `enforce`, `audit`, `warn`. Use them in sequence so existing workloads break loudly, not silently.

1. Label the namespace at `warn` and `audit` for `restricted` while keeping `enforce` at `baseline`:

   ```yaml
   metadata:
     labels:
       pod-security.kubernetes.io/enforce: baseline
       pod-security.kubernetes.io/warn: restricted
       pod-security.kubernetes.io/audit: restricted
   ```

   `kubectl apply -f manifest.yaml` now prints warnings for any pod that would fail `restricted`, and the API server logs an audit annotation.

2. Fix offenders in the workloads — usually `runAsNonRoot`, `seccompProfile`, `readOnlyRootFilesystem`, and dropping all capabilities. The compliant `securityContext` block is in `SKILL.md` §7.

3. Once warnings are clean for at least one release cycle, flip enforcement:

   ```yaml
   pod-security.kubernetes.io/enforce: restricted
   ```

4. Pin the version with `pod-security.kubernetes.io/enforce-version` to match the API server minor.

## Exemptions

Some infrastructure workloads legitimately need `privileged` (CNI agents, node-exporter on host network, storage CSI drivers). Two options:

- Run them in a dedicated namespace (e.g. `kube-system`, `cilium-system`) labelled `enforce: privileged`.
- Configure a cluster-wide `AdmissionConfiguration` exemption by namespace, ServiceAccount, or runtime class. Keep the exemption list short and reviewed.

Never exempt by user — only by namespace or ServiceAccount.

## Default-Deny NetworkPolicy

Apply default-deny ingress and egress to every tenant namespace, then layer allow rules:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny, namespace: team-a }
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: allow-dns, namespace: team-a }
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
    - to:
        - namespaceSelector: { matchLabels: { kubernetes.io/metadata.name: kube-system } }
          podSelector:       { matchLabels: { k8s-app: kube-dns } }
      ports:
        - { protocol: UDP, port: 53 }
        - { protocol: TCP, port: 53 }
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: allow-ingress-from-nginx, namespace: team-a }
spec:
  podSelector: { matchLabels: { app: web } }
  policyTypes: [Ingress]
  ingress:
    - from:
        - namespaceSelector: { matchLabels: { kubernetes.io/metadata.name: ingress-nginx } }
      ports:
        - { protocol: TCP, port: 3000 }
```

## Verification

- `kubectl auth can-i create pod --as=system:serviceaccount:team-a:default -n team-a` for sanity checks.
- `kubectl run probe --rm -it --image=alpine -n team-a -- /bin/sh -c "wget -qO- http://web"` should succeed for allowed paths and time out for denied ones.
- Audit annotations appear in API server audit logs for any pod that violated the configured profile in `audit` mode — surface them in the platform dashboard.

## Anti-Patterns

- Flipping `enforce: restricted` cluster-wide on day one. You will block the next deploy of every team that has not migrated.
- Allowing egress to `0.0.0.0/0` "temporarily" — it will outlive every policy review.
- Using `hostNetwork: true` for application workloads to dodge a NetworkPolicy issue.
- Granting the `default` ServiceAccount permission to create pods inside a tenant namespace.
