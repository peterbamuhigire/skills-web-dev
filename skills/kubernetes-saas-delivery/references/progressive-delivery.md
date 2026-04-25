# Progressive Delivery on Kubernetes

Canary, blue-green, and experiment patterns for multi-tenant SaaS. Read
after `SKILL.md`. Cross-reference `deployment-release-engineering` for
gates and rollbacks and `observability-monitoring` for SLO-based
analysis metrics.

## Argo Rollouts vs Flagger

| Dimension          | Argo Rollouts               | Flagger                    |
|--------------------|-----------------------------|----------------------------|
| CRD                | `Rollout` replaces Deployment | `Canary` wraps Deployment |
| Traffic split      | Ingress, SMI, Istio, Gateway | Istio, Linkerd, App Mesh, Gloo, Contour |
| Analysis           | AnalysisTemplate             | MetricTemplate             |
| Experimentation    | first-class                  | via webhooks               |
| Pairs naturally with | ArgoCD                     | Flux                       |

Decision rule:

- ArgoCD shop with Ingress-NGINX or Istio: Argo Rollouts.
- Flux shop with a service mesh: Flagger.
- No service mesh and no strong preference: Argo Rollouts with ingress
  traffic splitting is the simpler path.

## Canary with Prometheus analysis (Argo Rollouts)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata: { name: success-rate, namespace: app }
spec:
  args: [{ name: service }]
  metrics:
    - name: success-rate
      interval: 1m
      count: 5
      successCondition: result[0] >= 0.995
      failureLimit: 2
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            sum(rate(http_requests_total{service="{{args.service}}",
              status!~"5.."}[2m]))
            /
            sum(rate(http_requests_total{service="{{args.service}}"}[2m]))
    - name: latency-p99
      interval: 1m
      count: 5
      successCondition: result[0] < 0.500
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            histogram_quantile(0.99,
              sum by (le) (rate(
                http_request_duration_seconds_bucket{service="{{args.service}}"}[2m]
              ))
            )
```

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata: { name: api, namespace: app }
spec:
  replicas: 10
  strategy:
    canary:
      canaryService: api-canary
      stableService: api-stable
      trafficRouting:
        istio:
          virtualService: { name: api-vs, routes: [primary] }
      steps:
        - setWeight: 10
        - pause: { duration: 5m }
        - analysis:
            templates: [{ templateName: success-rate }]
            args: [{ name: service, value: api }]
        - setWeight: 25
        - pause: { duration: 10m }
        - analysis:
            templates: [{ templateName: success-rate }]
        - setWeight: 50
        - pause: { duration: 10m }
        - setWeight: 100
      abortScaleDownDelaySeconds: 60
```

Rule: every analysis step must fail closed. If Prometheus is down, the
analysis fails and the rollout aborts — never promote on missing data.

## Blue-green pattern (Argo Rollouts)

```yaml
spec:
  strategy:
    blueGreen:
      activeService: api-active
      previewService: api-preview
      autoPromotionEnabled: false
      scaleDownDelaySeconds: 300
      prePromotionAnalysis:
        templates: [{ templateName: success-rate }]
      postPromotionAnalysis:
        templates: [{ templateName: success-rate }]
```

Blue-green is the right choice when:

- Traffic must cut instantaneously (stateful session handoff).
- Canary cost (running N% extra replicas for long windows) is high.
- You need a manual promote gate.

## Experiments — side-by-side comparisons

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Experiment
metadata: { name: api-experiment-v1-vs-v2 }
spec:
  duration: 30m
  templates:
    - name: baseline
      replicas: 2
      selector: { matchLabels: { app: api, variant: baseline } }
      template:
        metadata: { labels: { app: api, variant: baseline } }
        spec: { containers: [{ name: api, image: api:1.12.3 }] }
    - name: canary
      replicas: 2
      selector: { matchLabels: { app: api, variant: canary } }
      template:
        metadata: { labels: { app: api, variant: canary } }
        spec: { containers: [{ name: api, image: api:1.13.0 }] }
  analyses:
    - name: compare
      templateName: error-budget-comparison
      args:
        - { name: baseline, value: baseline }
        - { name: canary, value: canary }
```

Use Experiments for A/B on non-customer-visible changes (new cache
strategy, new query planner) before committing to a canary roll-out.

## Flagger canary (Linkerd example)

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata: { name: api, namespace: app }
spec:
  targetRef: { apiVersion: apps/v1, kind: Deployment, name: api }
  service:
    port: 80
    targetPort: 8080
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
      - name: request-success-rate
        thresholdRange: { min: 99 }
        interval: 1m
      - name: request-duration
        thresholdRange: { max: 500 }
        interval: 1m
    webhooks:
      - name: load-test
        url: http://flagger-loadtester.test/
        metadata: { cmd: "hey -z 1m -q 20 -c 2 http://api-canary.app/" }
```

## Service mesh integration

- Istio: `VirtualService` and `DestinationRule` define subsets; the
  rollout controller adjusts weights.
- Linkerd: uses `ServiceProfile` and `TrafficSplit` (SMI) — Flagger
  is first class.
- Without a mesh: ingress-nginx canary annotations work, but session
  affinity and advanced routing suffer.

## Multi-tenant caveats

- Roll out to a canary tenant cohort first (internal, free tier), then
  promote globally. Use tenant labels on the Rollout and an
  analysis query scoped to that cohort.
- Tenant-specific rollbacks must be cheap. If a tenant triggers abort,
  only their namespace reverts — hence per-tenant Deployment per
  namespace when using ApplicationSet.
- Do not canary data migrations with progressive delivery — migrations
  use expand-contract plus feature flags.

## Anti-patterns

- Canary steps without analysis — it is just a slow rollout.
- Analysis on synthetic traffic only — real user signal is needed.
- Promoting on a single 1-minute window — flaky tests flap the gate.
- Running canary and blue-green on the same Rollout — pick one.
- Skipping `abortScaleDownDelaySeconds` — you lose the canary pods
  before you can debug.
