# Resource Management — Requests, Limits, QoS

Getting requests and limits right is the single biggest lever on cluster stability and cost. Wrong values cause OOMKills, throttling, noisy neighbours, and wasted spend.

## The mental model

- **Request** — guaranteed minimum. Scheduler reserves this on a node before placement.
- **Limit** — hard cap. CPU over limit = throttled. Memory over limit = OOMKilled.
- The difference between request and limit is your burst headroom — and your overcommit risk.

## QoS classes — how Kubernetes kills under pressure

Kubernetes assigns every Pod a QoS class based on its requests/limits. Under node pressure, the kubelet evicts in this order:

```text
BestEffort      -> no requests, no limits          -> evicted first
Burstable       -> some requests < limits          -> evicted next
Guaranteed      -> requests == limits on ALL resources and containers -> evicted last
```

### Guaranteed — for tier-1 critical workloads

```yaml
resources:
  requests: { cpu: "1", memory: "1Gi" }
  limits:   { cpu: "1", memory: "1Gi" }
```

Use for: databases, critical auth services, payment processors. Predictable, no throttling surprises, last to be evicted.

### Burstable — for most application workloads

```yaml
resources:
  requests: { cpu: "200m", memory: "512Mi" }
  limits:   { cpu: "1",    memory: "1Gi" }
```

Use for: APIs, workers, cron jobs. Good balance of density and safety.

### BestEffort — avoid in production

No requests or limits. First to be killed, zero scheduling guarantees. Only acceptable for throwaway jobs.

## Sizing — measure, don't guess

### Step 1: observe actual usage

```promql
# Memory working set over 7 days, per container, 99th percentile
quantile_over_time(0.99,
  container_memory_working_set_bytes{namespace="production", container!=""}[7d]
)

# CPU usage over 7 days, 95th percentile
quantile_over_time(0.95,
  rate(container_cpu_usage_seconds_total{namespace="production", container!=""}[5m])[7d:5m]
)
```

### Step 2: apply sizing rules

| Resource | Request | Limit |
|---|---|---|
| Memory | p95 actual + 20% | p99 actual + 30% (or request × 1.5) |
| CPU | p95 actual | p95 × 2–5, OR unset on well-tuned clusters |

### Step 3: validate with load

Run a realistic load test. Watch `container_cpu_cfs_throttled_periods_total` and memory near limit. If throttling > 5% of periods, raise CPU limit.

## CPU throttling diagnosis

CPU limits enforce via Linux CFS quota, per 100 ms period. A Pod with limit `500m` gets 50 ms of CPU every 100 ms. Bursty workloads (GC pauses, request spikes) can exhaust the quota early and stall.

### Symptoms

- p99 latency much higher than p50 despite low average CPU utilisation.
- `container_cpu_cfs_throttled_periods_total / container_cpu_cfs_periods_total > 0.25`.

### Diagnosis query

```promql
sum by (pod, container) (
  rate(container_cpu_cfs_throttled_periods_total{namespace="production"}[5m])
) / sum by (pod, container) (
  rate(container_cpu_cfs_periods_total{namespace="production"}[5m])
)
```

### Fixes

- Raise CPU limit (or remove if cluster allows and workload is trusted).
- Reduce thread pool / concurrency inside the app.
- Switch from `limit` to `request`-only on latency-sensitive workloads in clusters with `--cpu-manager-policy=static`.
- For Java/Go: set `GOMAXPROCS` or `-XX:ActiveProcessorCount` to match the limit, not the node cores.

## OOMKilled diagnosis

Memory limits are hard. Exceeding by 1 byte = SIGKILL. No graceful shutdown.

### Confirm OOMKill

```bash
kubectl describe pod <pod> | grep -A5 "Last State"
# Look for: Reason: OOMKilled, ExitCode: 137

kubectl get events --sort-by=.lastTimestamp | grep -i oom
```

### Dig into memory behaviour

```promql
# Working set vs limit over time
container_memory_working_set_bytes{pod="api-7f..."}
  / on(pod,container) group_left kube_pod_container_resource_limits{resource="memory"}

# RSS vs cache
container_memory_rss{pod="api-7f..."}
container_memory_cache{pod="api-7f..."}
```

### Common causes and fixes

| Symptom | Cause | Fix |
|---|---|---|
| Slow memory growth until OOM | Leak | Heap profile; fix app; bump limit only as stopgap |
| Sudden spike on specific request | Unbounded input (large JSON, image) | Limit request body size, stream processing |
| OOM at startup | JVM/Node heap too close to limit | Set `-Xmx` to ~75% of limit; set `--max-old-space-size` for Node |
| OOM only on one replica | Load imbalance | Check session affinity; use `topologySpreadConstraints` |
| OOM after upgrade | Working set grew | Re-profile; raise limit; investigate regression |

## JVM and Node.js — container awareness

Both runtimes have historically ignored cgroup limits. Modern versions are better but still need hints.

```bash
# Java 17+: respects container limits; still pin MaxRAMPercentage
JAVA_OPTS="-XX:MaxRAMPercentage=75 -XX:+UseG1GC -XX:MaxGCPauseMillis=200"

# Node.js: explicit heap cap
NODE_OPTIONS="--max-old-space-size=1536"  # for a 2Gi limit
```

## Init containers and sidecars — count them all

QoS is computed across **all** containers in the Pod. A BestEffort sidecar (logging shipper without requests) downgrades the entire Pod. Set requests/limits on sidecars too.

```yaml
initContainers:
  - name: db-migrate
    resources:
      requests: { cpu: 100m, memory: 128Mi }
      limits:   { cpu: 500m, memory: 256Mi }
containers:
  - name: app
    resources:
      requests: { cpu: 200m, memory: 512Mi }
      limits:   { cpu: 1,    memory: 1Gi }
  - name: otel-agent
    resources:
      requests: { cpu: 50m,  memory: 64Mi }
      limits:   { cpu: 200m, memory: 128Mi }
```

## LimitRange — safety net per namespace

Prevent BestEffort Pods by default. Force everyone to think.

```yaml
apiVersion: v1
kind: LimitRange
metadata: { name: defaults, namespace: production }
spec:
  limits:
    - type: Container
      default:        { cpu: 500m, memory: 512Mi }
      defaultRequest: { cpu: 100m, memory: 128Mi }
      max:            { cpu: 4,    memory: 8Gi }
      min:            { cpu: 10m,  memory: 32Mi }
```

## ResourceQuota — cap a namespace's blast radius

```yaml
apiVersion: v1
kind: ResourceQuota
metadata: { name: production-quota, namespace: production }
spec:
  hard:
    requests.cpu: "100"
    requests.memory: 200Gi
    limits.cpu: "200"
    limits.memory: 400Gi
    pods: "500"
    persistentvolumeclaims: "50"
```

## The VPA — recommend mode first

Never put VPA straight into `Auto` on production. Use `Off` (recommend only) for at least 2 weeks, review the target recommendations, then decide.

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata: { name: api-vpa, namespace: production }
spec:
  targetRef: { apiVersion: apps/v1, kind: Deployment, name: api }
  updatePolicy: { updateMode: "Off" }
  resourcePolicy:
    containerPolicies:
      - containerName: api
        minAllowed: { cpu: 100m, memory: 128Mi }
        maxAllowed: { cpu: 4,    memory: 4Gi }
```

Read recommendation with:

```bash
kubectl describe vpa api-vpa -n production | grep -A20 "Recommendation:"
```

## Review checklist

- [ ] Every container (including initContainers and sidecars) has requests and limits
- [ ] Memory limit sized on p99 + 30% headroom
- [ ] CPU limit either unset or 2–5× request
- [ ] Critical workloads are Guaranteed QoS
- [ ] `LimitRange` in every namespace
- [ ] `ResourceQuota` on tenant/application namespaces
- [ ] Throttling < 5% of CFS periods on latency-sensitive services
- [ ] No container in `CrashLoopBackOff` due to OOMKill in last 24h
- [ ] JVM/Node runtimes respect container limits
