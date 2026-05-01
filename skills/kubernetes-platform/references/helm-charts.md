# Helm Chart Authoring Patterns

Pairs with `SKILL.md` §4. For the Helm-vs-Kustomize tradeoff see `kubernetes-production` §"Helm vs Kustomize".

## Chart Skeleton

```text
charts/web/
  Chart.yaml
  values.yaml
  values.schema.json
  templates/
    _helpers.tpl
    deployment.yaml
    service.yaml
    ingress.yaml
    serviceaccount.yaml
    NOTES.txt
  charts/        # subcharts
  crds/          # installed before templates, not templated
```

## Named Templates and Helpers

Put repeated label and selector blocks in `_helpers.tpl`:

```yaml
{{- define "web.labels" -}}
app.kubernetes.io/name: {{ include "web.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "web.selectorLabels" -}}
app.kubernetes.io/name: {{ include "web.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

Use `app.kubernetes.io/...` labels everywhere; tools and dashboards key off them.

## values.schema.json

Catch malformed values at `helm install` time, not at apply time:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["image", "replicas"],
  "properties": {
    "image": {
      "type": "object",
      "required": ["repository", "tag"],
      "properties": {
        "repository": { "type": "string" },
        "tag":        { "type": "string", "minLength": 1 }
      }
    },
    "replicas": { "type": "integer", "minimum": 1, "maximum": 50 }
  }
}
```

## Subchart Value Overrides

In the parent `values.yaml`, set subchart values under the subchart's name:

```yaml
postgresql:
  auth:
    username: app
    database: app
  primary:
    persistence:
      size: 20Gi
```

Pass `--reset-values` on `helm upgrade` to drop drift from prior `--set` flags. Pass `--reuse-values` only when intentionally extending the existing release.

## Release Discipline

- One release per logical app per namespace. Do not co-host two unrelated apps in a single release.
- Pin the chart version with `--version` in CI.
- Emit the Helm release name as a label so dashboards and alerts can group by it.
- Keep `values.<env>.yaml` files in the same git repo as the chart; never edit values out-of-band on the cluster.

## Testing

- `helm lint ./charts/web` in CI on every PR.
- `helm template ./charts/web -f values.prod.yaml | kubeval` (or `kubeconform`) to schema-check rendered manifests.
- `helm test web -n app` runs chart test pods after install in a staging cluster.

## Anti-Patterns

- Templating CRDs through `templates/` — put CRDs under `crds/` so Helm installs them before the templated resources.
- Embedding secrets in `values.yaml`. Use a SealedSecret, External Secrets Operator, or Vault Agent injection instead.
- One mega-chart that deploys an entire platform. Prefer one chart per app and an umbrella chart that depends on them only when truly co-released.
