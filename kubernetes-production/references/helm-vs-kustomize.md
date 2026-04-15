# Helm vs Kustomize

Package manager vs overlay engine. They solve different problems; the wrong one adds complexity without value.

## TL;DR decision table

```text
Situation                                         | Tool
---------------------------------------------------|-------------------
Distribute an app to many users/tenants            | Helm
Small env overlay (dev/staging/prod), single app   | Kustomize
Conditional logic, loops, generated names          | Helm
Strict "what you see is what you get" manifests    | Kustomize
Third-party app installation (Prometheus, Redis)   | Helm (upstream charts)
Patch a third-party Helm chart output              | Helm template + Kustomize
Pure GitOps with ArgoCD/Flux and env drift review  | Kustomize (or Helm + Argo)
Secrets templating with complex conditionals       | Helm
Want manifest diffs on PRs to look plain           | Kustomize
```

## Helm — the package manager

A chart is a versioned, distributable bundle of templated manifests plus a `values.yaml` default.

### Chart anatomy

```text
mychart/
  Chart.yaml              # name, version, appVersion
  values.yaml             # default values
  values.schema.json      # (recommended) JSON Schema for values
  templates/
    _helpers.tpl          # named template definitions (define/include)
    deployment.yaml
    service.yaml
    serviceaccount.yaml
    hpa.yaml
    networkpolicy.yaml
    NOTES.txt             # shown after install
  charts/                 # sub-chart dependencies (from Chart.yaml)
  crds/                   # CRDs installed before templates (not templated)
```

### Minimal Chart.yaml

```yaml
apiVersion: v2
name: api
description: Public API service
type: application
version: 1.4.2         # chart version — bump on any template change
appVersion: "2025.10"  # shipped app version — surfaced in labels
dependencies:
  - name: redis
    version: 19.x.x
    repository: oci://registry-1.docker.io/bitnamicharts
    condition: redis.enabled
```

### Minimal deployment template

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "api.fullname" . }}
  labels: {{- include "api.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels: {{- include "api.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels: {{- include "api.selectorLabels" . | nindent 8 }}
    spec:
      serviceAccountName: {{ include "api.serviceAccountName" . }}
      automountServiceAccountToken: false
      securityContext: {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - containerPort: {{ .Values.service.port }}
          readinessProbe: {{- toYaml .Values.readinessProbe | nindent 12 }}
          resources: {{- toYaml .Values.resources | nindent 12 }}
```

### values.yaml hygiene

- Everything a user might legitimately override belongs here — even at the cost of verbosity.
- Group by concern (`image`, `resources`, `service`, `ingress`, `autoscaling`).
- Provide `values.schema.json` so `helm install` fails fast on typos.
- Never hard-code hostnames, image tags, or resource values inside templates — read from `.Values`.
- Mark secrets as `null` defaults; force the user to supply via `--set-file` or external-secrets.

```yaml
# values.yaml — trim and stable
replicaCount: 2
image:
  repository: ghcr.io/acme/api
  tag: ""            # defaults to .Chart.AppVersion
  pullPolicy: IfNotPresent
resources:
  requests: { cpu: 100m, memory: 256Mi }
  limits:   { cpu: 1,    memory: 512Mi }
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70
service:
  type: ClusterIP
  port: 8080
```

### Helm release commands

```bash
# Render without installing (for review)
helm template api ./charts/api -f values-prod.yaml > rendered.yaml

# Diff before upgrade (requires helm-diff plugin)
helm diff upgrade api ./charts/api -f values-prod.yaml -n production

# Install/upgrade with atomic rollback on failure
helm upgrade --install api ./charts/api \
  -n production --create-namespace \
  -f values-prod.yaml \
  --atomic --timeout 5m

# Rollback
helm rollback api 3 -n production
```

## Kustomize — the overlay engine

No templates. No logic. A `kustomization.yaml` file lists resources and patches them declaratively.

### Base + overlays layout

```text
k8s/
  base/
    kustomization.yaml
    deployment.yaml
    service.yaml
  overlays/
    dev/
      kustomization.yaml
      patch-replicas.yaml
    staging/
      kustomization.yaml
    production/
      kustomization.yaml
      patch-replicas.yaml
      patch-resources.yaml
```

### base/kustomization.yaml

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
commonLabels:
  app.kubernetes.io/name: api
  app.kubernetes.io/part-of: platform
```

### overlays/production/kustomization.yaml

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: production
resources:
  - ../../base
images:
  - name: ghcr.io/acme/api
    newTag: 2025.10.3
patches:
  - path: patch-replicas.yaml
    target: { kind: Deployment, name: api }
  - path: patch-resources.yaml
    target: { kind: Deployment, name: api }
replicas:
  - name: api
    count: 5
```

### Strategic merge patch

```yaml
# patch-resources.yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: api }
spec:
  template:
    spec:
      containers:
        - name: api
          resources:
            requests: { cpu: 500m, memory: 1Gi }
            limits:   { cpu: 2,    memory: 2Gi }
```

### Commands

```bash
kubectl kustomize overlays/production                 # render
kubectl apply -k overlays/production                  # apply
kubectl diff -k overlays/production                   # dry-run diff
```

## Combining them — helm template + kustomize patch

Sometimes you want an upstream Helm chart but need changes the chart author did not expose. Render with Helm, then patch with Kustomize.

```yaml
# kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
helmCharts:
  - name: kube-prometheus-stack
    repo: https://prometheus-community.github.io/helm-charts
    version: 62.3.0
    releaseName: kps
    namespace: monitoring
    valuesFile: values-kps.yaml
patches:
  - path: patch-grafana-ingress.yaml
    target: { kind: Ingress, name: kps-grafana }
```

Rule: only use this pattern when upstream does not expose the knob you need and a fork would be heavier to maintain. Avoid patching rendered charts for anything that could have been a values override.

## When NOT to mix

- Never manage the same workload with both Helm and Kustomize simultaneously (ownership conflicts, `helm upgrade` will clobber Kustomize changes).
- Never use Helm for pure env overlays on a single in-house service — Kustomize is lighter.
- Never use Kustomize to distribute a product to external tenants — versioning and dependencies are Helm's job.

## Review checklist

- [ ] `Chart.yaml` bumped on every template-affecting change
- [ ] `values.schema.json` exists and matches `values.yaml`
- [ ] No plaintext secrets in values files committed to Git
- [ ] `helm template | kubeconform -strict` passes in CI
- [ ] `--atomic --timeout` on production `helm upgrade`
- [ ] Kustomize overlays do not duplicate resources from base
- [ ] `commonLabels` and `commonAnnotations` only at base level
- [ ] `kubectl diff -k overlays/<env>` produces expected change set
