# Admission Control — Kyverno and OPA Gatekeeper

Admission webhooks intercept every create/update to the API server. Policy-as-code at admission stops bad manifests before they reach etcd — much cheaper than catching them in production.

## Kyverno vs Gatekeeper — pick one, not both

| Dimension | Kyverno | OPA Gatekeeper |
|---|---|---|
| Policy language | YAML (Kubernetes-native) | Rego |
| Learning curve | Low | Steep |
| Mutation | Yes (first-class) | Yes |
| Validation | Yes | Yes |
| Generation (auto-create resources) | Yes | No (limited) |
| External data | Via API calls | Via constraint data |
| Performance | Generally excellent | Excellent once policies compile |
| Community / ecosystem | Growing fast, big library | Mature, CNCF graduated |
| Who should pick it | Most teams | Teams with OPA elsewhere, Rego skills |

**Default pick: Kyverno** unless you already run OPA across the stack.

## Kyverno — install

```bash
helm repo add kyverno https://kyverno.github.io/kyverno/
helm upgrade --install kyverno kyverno/kyverno \
  -n kyverno --create-namespace \
  --set admissionController.replicas=3 \
  --set backgroundController.replicas=2 \
  --set cleanupController.replicas=2 \
  --set reportsController.replicas=2
```

Then install the baseline policies chart:

```bash
helm upgrade --install kyverno-policies kyverno/kyverno-policies \
  -n kyverno \
  --set podSecurityStandard=restricted \
  --set validationFailureAction=Enforce     # start Audit, flip to Enforce
```

## Kyverno — real policies you should ship

### Deny `:latest` and tagless images

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: disallow-latest-tag }
spec:
  validationFailureAction: Enforce
  background: true
  rules:
    - name: require-image-tag
      match:
        any:
          - resources: { kinds: [Pod] }
      validate:
        message: "Image tag ':latest' or missing tag is not allowed."
        pattern:
          spec:
            containers:
              - image: "!*:latest & *:*"
            =(initContainers):
              - image: "!*:latest & *:*"
```

### Require resource requests and limits

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: require-resources }
spec:
  validationFailureAction: Enforce
  rules:
    - name: require-requests-and-limits
      match:
        any:
          - resources: { kinds: [Pod] }
      validate:
        message: "CPU and memory requests and limits are required on every container."
        pattern:
          spec:
            containers:
              - name: "*"
                resources:
                  requests: { memory: "?*", cpu: "?*" }
                  limits:   { memory: "?*" }
```

### Require standard labels

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: require-labels }
spec:
  validationFailureAction: Enforce
  rules:
    - name: require-app-labels
      match:
        any:
          - resources:
              kinds: [Deployment, StatefulSet, DaemonSet]
      validate:
        message: "Required labels: app.kubernetes.io/name, app.kubernetes.io/part-of, owner."
        pattern:
          metadata:
            labels:
              app.kubernetes.io/name: "?*"
              app.kubernetes.io/part-of: "?*"
              owner: "?*"
```

### Image registry allowlist

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: allowed-registries }
spec:
  validationFailureAction: Enforce
  rules:
    - name: validate-registries
      match:
        any:
          - resources: { kinds: [Pod] }
      validate:
        message: "Image must come from ghcr.io/acme/ or <ACCOUNT>.dkr.ecr.eu-west-1.amazonaws.com/"
        pattern:
          spec:
            containers:
              - image: "ghcr.io/acme/* | *.dkr.ecr.eu-west-1.amazonaws.com/*"
            =(initContainers):
              - image: "ghcr.io/acme/* | *.dkr.ecr.eu-west-1.amazonaws.com/*"
```

### Require readiness probe

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: require-readiness-probe }
spec:
  validationFailureAction: Enforce
  rules:
    - name: validate-probes
      match:
        any:
          - resources:
              kinds: [Deployment, StatefulSet]
      validate:
        message: "Every container must define a readinessProbe."
        pattern:
          spec:
            template:
              spec:
                containers:
                  - name: "*"
                    readinessProbe:
                      =(httpGet): { path: "?*" }
                      =(tcpSocket): { port: "?*" }
                      =(exec): { command: "?*" }
```

### Mutate — add default resources

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: add-default-resources }
spec:
  rules:
    - name: add-default-requests
      match:
        any:
          - resources: { kinds: [Pod] }
      mutate:
        patchStrategicMerge:
          spec:
            containers:
              - (name): "*"
                resources:
                  requests:
                    +(cpu): "100m"
                    +(memory): "128Mi"
```

### Verify image signatures (cosign)

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: verify-images }
spec:
  validationFailureAction: Enforce
  webhookTimeoutSeconds: 30
  rules:
    - name: verify-ghcr
      match:
        any:
          - resources: { kinds: [Pod] }
      verifyImages:
        - imageReferences: ["ghcr.io/acme/*"]
          attestors:
            - entries:
                - keyless:
                    issuer: "https://token.actions.githubusercontent.com"
                    subject: "https://github.com/acme/*"
```

## OPA Gatekeeper — install

```bash
helm repo add gatekeeper https://open-policy-agent.github.io/gatekeeper/charts
helm upgrade --install gatekeeper gatekeeper/gatekeeper \
  -n gatekeeper-system --create-namespace \
  --set replicas=3 --set auditInterval=60
```

## Gatekeeper — ConstraintTemplate + Constraint

### ConstraintTemplate (reusable policy logic)

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata: { name: k8srequiredlabels }
spec:
  crd:
    spec:
      names: { kind: K8sRequiredLabels }
      validation:
        openAPIV3Schema:
          type: object
          properties:
            labels: { type: array, items: { type: string } }
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        violation[{"msg": msg}] {
          required := input.parameters.labels
          provided := input.review.object.metadata.labels
          missing := required[_]
          not provided[missing]
          msg := sprintf("Missing required label: %v", [missing])
        }
```

### Constraint (applies template with parameters)

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata: { name: require-app-labels }
spec:
  enforcementAction: deny
  match:
    kinds:
      - { apiGroups: ["apps"], kinds: ["Deployment", "StatefulSet"] }
    namespaces: ["production", "staging"]
  parameters:
    labels: ["app.kubernetes.io/name", "owner"]
```

### Gatekeeper — disallow privileged containers

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata: { name: k8spspprivilegedcontainer }
spec:
  crd:
    spec: { names: { kind: K8sPSPPrivilegedContainer } }
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8spspprivileged
        violation[{"msg": msg}] {
          c := input_containers[_]
          c.securityContext.privileged
          msg := sprintf("Privileged container is not allowed: %v", [c.name])
        }
        input_containers[c] { c := input.review.object.spec.containers[_] }
        input_containers[c] { c := input.review.object.spec.initContainers[_] }
```

## Rollout pattern — never start at Enforce

1. Apply policies with `validationFailureAction: Audit` (Kyverno) or `enforcementAction: dryrun` (Gatekeeper).
2. Observe violations for 1–2 weeks: `kubectl get policyreport -A` (Kyverno) or Gatekeeper audit logs.
3. Engage workload owners to remediate.
4. Exempt legitimate system workloads explicitly (kube-system, monitoring operators).
5. Flip to `Enforce` / `deny` one policy at a time.
6. Monitor for broken deploys during the first week post-flip.

## Exemptions — scoped, tracked

```yaml
# Kyverno: exclude specific namespaces
spec:
  rules:
    - name: require-resources
      match:
        any:
          - resources: { kinds: [Pod] }
      exclude:
        any:
          - resources:
              namespaces: [kube-system, gatekeeper-system, kyverno]
```

Maintain a registry of exemptions in Git. Review quarterly; delete expired ones.

## Performance tips

- Keep `webhookTimeoutSeconds: 10` or less. A hanging webhook = API server outage.
- Set `failurePolicy: Fail` only once stable; during rollout, `Ignore` is safer.
- Run admission controllers with `replicas >= 3` and a PDB.
- Restrict `namespaceSelector` / `objectSelector` so webhooks only fire on targets.

## Monitoring

- Kyverno PolicyReports: `kubectl get polr -A` and `kubectl get cpolr`.
- Kyverno metrics: scrape via ServiceMonitor; watch `kyverno_admission_request_duration_seconds`.
- Gatekeeper audit: `kubectl get constraint -A` and check `status.violations`.
- Alert on `kyverno_client_queries_total{status="failed"}` and webhook latency p99.

## Review checklist

- [ ] One admission controller chosen (Kyverno or Gatekeeper), not both
- [ ] Admission controller HA: 3 replicas + PDB + anti-affinity
- [ ] Policies rolled out Audit → Enforce with remediation window
- [ ] Disallow `:latest` and tagless images
- [ ] Require requests and limits on every container
- [ ] Require `readinessProbe` on Deployments and StatefulSets
- [ ] Require standard labels (owner, app, part-of)
- [ ] Image registry allowlist enforced
- [ ] cosign / sigstore verification for internal images
- [ ] System namespaces explicitly exempted and tracked in Git
- [ ] PolicyReport metrics in Grafana dashboard
- [ ] Webhook timeout ≤ 10s; failurePolicy set deliberately
