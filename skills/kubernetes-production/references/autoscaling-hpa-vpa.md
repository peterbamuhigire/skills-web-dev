# Autoscaling — HPA, VPA, KEDA, Cluster Autoscaler, Karpenter

Three layers: Pods scale horizontally (HPA), Pods resize vertically (VPA), nodes scale under them (CA / Karpenter). Event-driven scaling (KEDA) sits alongside HPA for queues, streams, and schedulers.

## Layer map

```text
Requests per second rising?    -> HPA (more Pods)
One Pod always at memory cap?  -> VPA (bigger Pod)
Queue depth growing?           -> KEDA (scale on external metric, incl. scale-to-zero)
No space on existing nodes?    -> Cluster Autoscaler or Karpenter (more nodes)
Cost too high at idle?         -> Karpenter consolidation + spot
```

Never run HPA and VPA in `Auto` mode on the same metric (both fight for CPU/memory). VPA in `Off`/`Initial` alongside HPA is fine.

## HPA v2 — the common case

### CPU target

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: { name: api, namespace: production }
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: api }
  minReplicas: 2
  maxReplicas: 30
  metrics:
    - type: Resource
      resource:
        name: cpu
        target: { type: Utilization, averageUtilization: 65 }
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - { type: Percent, value: 100, periodSeconds: 30 }  # double fast
        - { type: Pods,    value: 4,   periodSeconds: 30 }
      selectPolicy: Max
    scaleDown:
      stabilizationWindowSeconds: 300                         # 5 min grace
      policies:
        - { type: Percent, value: 25, periodSeconds: 60 }     # drop slow
      selectPolicy: Min
```

### CPU + memory together

```yaml
metrics:
  - type: Resource
    resource:
      name: cpu
      target: { type: Utilization, averageUtilization: 65 }
  - type: Resource
    resource:
      name: memory
      target: { type: Utilization, averageUtilization: 75 }
```

HPA picks the metric demanding the most replicas. Memory-based HPA is controversial — memory rarely releases back, so it can ratchet up. Prefer CPU and custom metrics; use memory only for caches or JVM apps with known GC behaviour.

### Custom metric via Prometheus Adapter

Install the adapter, expose a rule for your metric, then reference it:

```yaml
# prometheus-adapter values excerpt
rules:
  custom:
    - seriesQuery: 'http_requests_per_second{namespace!="", pod!=""}'
      resources:
        overrides:
          namespace: { resource: namespace }
          pod:       { resource: pod }
      name:
        matches: "^(.*)$"
        as: "${1}"
      metricsQuery: 'sum(rate(http_requests_total{<<.LabelMatchers>>}[2m])) by (<<.GroupBy>>)'
```

```yaml
metrics:
  - type: Pods
    pods:
      metric: { name: http_requests_per_second }
      target: { type: AverageValue, averageValue: "100" }   # 100 rps per Pod
```

### External metric (SQS, Pub/Sub) — prefer KEDA

```yaml
metrics:
  - type: External
    external:
      metric:
        name: sqs_queue_messages
        selector:
          matchLabels: { queue: jobs-prod }
      target: { type: AverageValue, averageValue: "30" }  # 30 msgs per Pod
```

## HPA tuning rules

- Set `minReplicas >= 2` for HA. `minReplicas: 1` means any node drain = outage.
- Target 60–70% CPU utilisation (leaves headroom for traffic spikes during scale-up).
- `scaleUp` aggressive (stabilisation 0, percent 100). Scaling too slow is an outage.
- `scaleDown` conservative (stabilisation 5 min, percent 25). Scaling too fast thrashes.
- Startup time matters. If containers take > 60s to become ready, pair with a `startupProbe` and raise `scaleUp` stabilisation to avoid launching useless Pods during a spike.
- Use `topologySpreadConstraints` so new Pods land on different nodes/zones.

## VPA — three modes

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata: { name: api-vpa, namespace: production }
spec:
  targetRef: { apiVersion: apps/v1, kind: Deployment, name: api }
  updatePolicy:
    updateMode: "Off"        # Off | Initial | Recreate | Auto
  resourcePolicy:
    containerPolicies:
      - containerName: '*'
        controlledResources: ["cpu", "memory"]
        minAllowed: { cpu: 50m,  memory: 64Mi }
        maxAllowed: { cpu: 4,    memory: 8Gi }
```

| Mode | Action | When to use |
|---|---|---|
| `Off` | Recommend only | Default. 2+ weeks in production before trusting. |
| `Initial` | Apply at Pod creation | Jobs, CronJobs, single-replica workloads. |
| `Recreate` | Evict Pods to resize | Deployments that tolerate restarts. |
| `Auto` | Currently same as Recreate | Risky; only for batch or dev. |

VPA does not work on Deployments without PodDisruptionBudget — it will ignore evictions it cannot perform. Always pair with a PDB.

### VPA + HPA — safe combination

- HPA on CPU or custom metric.
- VPA in `Off` mode for memory recommendations only.
- Review VPA recommendation monthly; bake into Deployment spec manually.

## KEDA — event-driven autoscaling

KEDA scales Deployments on external signals (SQS, Kafka lag, RabbitMQ queue, Prometheus query, cron, Azure Service Bus, etc.), including **scale to zero**.

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata: { name: worker, namespace: production }
spec:
  scaleTargetRef: { name: worker }
  minReplicaCount: 0
  maxReplicaCount: 50
  pollingInterval: 15
  cooldownPeriod: 300
  triggers:
    - type: aws-sqs-queue
      authenticationRef: { name: keda-aws-auth }
      metadata:
        queueURL: https://sqs.eu-west-1.amazonaws.com/123/jobs-prod
        queueLength: "20"         # target msgs per Pod
        awsRegion: eu-west-1
    - type: prometheus
      metadata:
        serverAddress: http://prometheus.monitoring:9090
        metricName: job_queue_lag
        query: max(job_queue_lag_seconds)
        threshold: "30"
```

### When KEDA wins over HPA

- Queue-based workers (SQS, Kafka, RabbitMQ, Service Bus).
- Scheduled scale-ups (`cron` trigger — scale up at 08:00 before load arrives).
- Scale-to-zero for rarely-used workloads.
- External metrics without the Prometheus Adapter dance.

## Cluster Autoscaler — traditional node scaling

Works with Auto Scaling Groups / MIGs / VMSS. Adds nodes when Pods are `Pending` for lack of capacity; removes nodes underutilised for 10 minutes.

```bash
# EKS example
eksctl create nodegroup --cluster=prod \
  --name=general --node-type=m6i.xlarge \
  --nodes-min=2 --nodes-max=20 \
  --asg-access \
  --tags k8s.io/cluster-autoscaler/enabled=true,k8s.io/cluster-autoscaler/prod=owned
```

Limitations:
- Scales one node type per ASG — needs multiple node groups for diverse workloads.
- Slow to react (minutes).
- Cannot pack bin-efficiently across node types.

## Karpenter — modern AWS node autoscaler

Karpenter provisions nodes directly from EC2 (no ASG), picks the cheapest instance type that fits pending Pods, and consolidates aggressively.

### NodePool + EC2NodeClass (Karpenter v1)

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata: { name: default }
spec:
  template:
    spec:
      requirements:
        - key: kubernetes.io/arch
          operator: In
          values: ["amd64"]
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot", "on-demand"]
        - key: karpenter.k8s.aws/instance-category
          operator: In
          values: ["c", "m", "r"]
        - key: karpenter.k8s.aws/instance-size
          operator: NotIn
          values: ["nano", "micro", "small"]
      nodeClassRef:
        group: karpenter.k8s.aws
        kind: EC2NodeClass
        name: default
      expireAfter: 168h                     # recycle weekly for patching
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
    consolidateAfter: 30s
  limits: { cpu: "1000", memory: "2000Gi" }
```

### Karpenter decision rules

- Default to mixed `spot` + `on-demand`. Use `preferredDuringSchedulingIgnoredDuringExecution` on critical Pods to steer them to on-demand.
- Set `expireAfter` so nodes get patched even without deploys.
- Enable consolidation — it is the main cost win over ASG + CA.
- Use separate NodePools for GPUs, ARM, and heavy-memory workloads.

## Decision rules

- Stateless web API: HPA on CPU + Karpenter/CA.
- Async worker on queue: KEDA on queue depth + Karpenter with spot.
- Latency-sensitive low-QPS API: HPA on custom metric (rps or in-flight) + on-demand only.
- Batch / ML training: Karpenter with spot + diverse instance types + KEDA cron.
- Legacy service with fixed replicas: VPA `Initial` + PDB; no HPA.
- Memory-heavy cache (Redis, ES): no HPA; use StatefulSet + node pool pinning.

## Review checklist

- [ ] Every stateless Deployment has an HPA (or KEDA ScaledObject)
- [ ] `minReplicas >= 2` on all HPAs
- [ ] `scaleDown` stabilisation window >= 180s
- [ ] Custom metrics go through Prometheus Adapter or KEDA, not directly into HPA
- [ ] VPA runs in `Off` mode on production unless workload is explicitly allow-listed
- [ ] Cluster Autoscaler or Karpenter installed and tested against pending Pod storms
- [ ] Karpenter NodePool has `expireAfter` for patching churn
- [ ] Spot node pools have `PodDisruptionBudget` on sensitive workloads
- [ ] Load test shows scale-up reaches target in < 120s
