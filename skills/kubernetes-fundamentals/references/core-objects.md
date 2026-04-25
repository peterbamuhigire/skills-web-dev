# Core Objects Reference

Every K8s object that fundamentals-level work touches, what it does, when to reach for it, and the sharp edges.

## Pod

The smallest deployable unit. One or more containers sharing network namespace (localhost, shared ports), IPC, and volumes. Pods are ephemeral; IPs change on restart.

```yaml
apiVersion: v1
kind: Pod
metadata: { name: debug, namespace: default }
spec:
  containers:
    - name: tools
      image: nicolaka/netshoot:v0.12
      command: ["sleep", "3600"]
```

- Use directly only for ad hoc debugging, never for workloads.
- Multi-container Pods are for tight coupling only: a main app + its sidecar (log shipper, proxy), or init containers.

## ReplicaSet

Keeps N identical Pods running. You almost never write one yourself; Deployments produce them.

- Only reach for a raw ReplicaSet if you need a custom controller that owns rollout.
- `kubectl get rs` is useful for spotting leftover ReplicaSets that kept replicas after a failed rollout.

## Deployment

Declarative stateless workload. Owns ReplicaSets and performs rolling updates.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: api, namespace: production }
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxUnavailable: 0, maxSurge: 1 }
  revisionHistoryLimit: 5
  selector: { matchLabels: { app: api } }
  template:
    metadata: { labels: { app: api } }
    spec:
      containers:
        - name: api
          image: registry.example.com/api:v1.4.2
          ports: [{ containerPort: 3000 }]
          resources:
            requests: { cpu: 100m, memory: 128Mi }
            limits:   { cpu: 500m, memory: 256Mi }
```

- Use for every stateless service: APIs, web, workers that do not need stable identity.
- `maxUnavailable: 0` preserves capacity during rollouts; tune `maxSurge` to budget.
- `revisionHistoryLimit` keeps rollback options without hoarding ReplicaSets.

## StatefulSet

Stable pod identity, ordered deployment, stable storage. Pods are named `myapp-0`, `myapp-1`.

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata: { name: kafka, namespace: data }
spec:
  serviceName: kafka-headless
  replicas: 3
  selector: { matchLabels: { app: kafka } }
  template:
    metadata: { labels: { app: kafka } }
    spec:
      containers:
        - name: kafka
          image: bitnami/kafka:3.7.0
          ports: [{ containerPort: 9092 }]
          volumeMounts: [{ name: data, mountPath: /var/lib/kafka }]
  volumeClaimTemplates:
    - metadata: { name: data }
      spec:
        accessModes: [ReadWriteOnce]
        resources: { requests: { storage: 50Gi } }
```

- Use for databases, queues, consensus systems: anything that needs predictable DNS or per-pod disks.
- Prefer managed RDS/Cloud SQL/managed Kafka over running these in-cluster unless you have ops depth.
- Scaling down does not delete PVCs; clean up explicitly.

## DaemonSet

One Pod per node (or per labelled node). Use for node-level agents: log collectors, metric exporters, CSI drivers, security agents.

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata: { name: fluent-bit, namespace: logging }
spec:
  selector: { matchLabels: { app: fluent-bit } }
  template:
    metadata: { labels: { app: fluent-bit } }
    spec:
      tolerations:
        - operator: Exists
      containers:
        - name: fluent-bit
          image: fluent/fluent-bit:3.0.7
          resources:
            requests: { cpu: 50m, memory: 64Mi }
            limits:   { cpu: 200m, memory: 128Mi }
```

- Tolerations let the DaemonSet run on tainted nodes (control-plane, GPU).
- Prefer running platform agents as DaemonSets, not as sidecars inside every app Pod.

## Job

Run-to-completion workload. Retries on failure up to `backoffLimit`.

```yaml
apiVersion: batch/v1
kind: Job
metadata: { name: db-migrate, namespace: production }
spec:
  backoffLimit: 3
  ttlSecondsAfterFinished: 3600
  template:
    spec:
      restartPolicy: OnFailure
      containers:
        - name: migrate
          image: registry.example.com/api:v1.4.2
          command: ["npm", "run", "migrate"]
```

- Use for migrations, one-off imports, data repair.
- `ttlSecondsAfterFinished` cleans up completed Jobs automatically.

## CronJob

Scheduled Jobs.

```yaml
apiVersion: batch/v1
kind: CronJob
metadata: { name: nightly-export, namespace: production }
spec:
  schedule: "15 2 * * *"
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 3
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: export
              image: registry.example.com/exporter:v0.3.1
```

- Schedule is in cluster timezone; most clusters are UTC.
- `concurrencyPolicy: Forbid` prevents overlapping runs when a previous execution is slow.

## Service

Stable virtual IP and DNS name that load-balances to matching Pods. The Service type determines exposure:

- `ClusterIP` (default): internal only.
- `NodePort`: exposes on every node on a high port. Rarely used directly.
- `LoadBalancer`: provisions a cloud LB. Expensive if overused.
- `ExternalName`: DNS CNAME to an external host.
- Headless (`clusterIP: None`): DNS-only, returns all Pod IPs. Used by StatefulSets.

```yaml
apiVersion: v1
kind: Service
metadata: { name: api, namespace: production }
spec:
  type: ClusterIP
  selector: { app: api }
  ports: [{ name: http, port: 80, targetPort: 3000 }]
```

- Keep Services ClusterIP and expose through Ingress or Gateway.

## Ingress

HTTP(S) routing from outside to Services. Needs an Ingress controller.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api
  namespace: production
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt
spec:
  ingressClassName: nginx
  tls:
    - hosts: [api.example.com]
      secretName: api-tls
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend: { service: { name: api, port: { number: 80 } } }
```

- Gateway API is the standard-track successor; adopt it if your controller supports it.

## ConfigMap

Non-secret configuration.

```yaml
apiVersion: v1
kind: ConfigMap
metadata: { name: api-config, namespace: production }
data:
  APP_ENV: production
  LOG_LEVEL: info
```

- Mount as env vars (`envFrom`) or as files (volume). Prefer files for larger configs.
- Changing a ConfigMap does not restart Pods; add a checksum annotation or use Reloader.

## Secret

Base64-encoded secret data. Base64 is not encryption; protect with RBAC, encryption-at-rest, and an external secret store.

```yaml
apiVersion: v1
kind: Secret
metadata: { name: api-secrets, namespace: production }
type: Opaque
stringData:
  database-url: postgres://user:pass@db:5432/app
```

- Never commit raw Secret manifests to git. Use sealed-secrets, SOPS, or external-secrets + cloud secret manager.
- Mount via `envFrom.secretRef` or as files; files are safer (no leak into process env dumps).

## Namespace

Logical partition of cluster resources. Scopes most objects (Pods, Services, Secrets, Deployments). Not a security boundary by default.

- One namespace per application environment (`production`, `staging`), or per team, or per tenant.
- Apply ResourceQuota, LimitRange, and NetworkPolicy per namespace.

## PersistentVolume and PersistentVolumeClaim

PV is a piece of storage in the cluster. PVC is a request for storage. StorageClass provisions PVs dynamically.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata: { name: data, namespace: production }
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: gp3
  resources: { requests: { storage: 20Gi } }
```

- Most workloads use dynamic provisioning via StorageClass; you rarely write PV manifests directly.
- ReadWriteOnce is one node at a time. ReadWriteMany needs a filesystem that supports it (EFS, Filestore).

## HorizontalPodAutoscaler

Scales replicas based on CPU, memory, or custom metrics.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: { name: api, namespace: production }
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: api }
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target: { type: Utilization, averageUtilization: 70 }
```

- Requires metrics-server; without it HPA reports `unknown`.
- CPU target should match real-world saturation, not an aspirational number.

## PodDisruptionBudget

Protects availability during voluntary disruptions (node drain, cluster upgrade).

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: api, namespace: production }
spec:
  minAvailable: 2
  selector: { matchLabels: { app: api } }
```

- Use `minAvailable` for most apps. `maxUnavailable: 1` is handy for small replica sets.
- Set a PDB for anything stateful or latency-sensitive; without it the cluster upgrade can take them all down at once.

## When in doubt

- Stateless web or API -> Deployment + Service + Ingress + HPA + PDB.
- Stateful with identity or storage -> StatefulSet + headless Service + PVC.
- Per-node agent -> DaemonSet.
- One-off work -> Job. Scheduled work -> CronJob.
- Secret material -> Secret + external-secrets operator.
- Non-secret config -> ConfigMap.
