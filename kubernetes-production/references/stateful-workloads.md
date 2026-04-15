# Stateful Workloads — StatefulSet, PVC, Anti-Affinity, PDB

Stateful workloads break the default Kubernetes assumptions (Pods are cattle, storage is ephemeral). Do them wrong and you lose data; do them half-right and you get dual-write split brains.

## First: should this even be in-cluster?

Before deploying an in-cluster database, answer honestly:

```text
Do you have on-call DBAs for PITR, failovers, and major-version upgrades?
Can you run quarterly restore drills from backup?
Is cross-region DR a requirement?  (If yes, managed almost always wins.)
Do you need connection pooling, read replicas, and analytical replicas?
```

If any answer is uncertain, use managed (RDS, Cloud SQL, Neon, Aiven, Supabase, AlloyDB). In-cluster databases are for teams with deep K8s-storage maturity, compliance needs, or cost pressure at scale.

Acceptable in-cluster: Redis/Valkey caches, RabbitMQ, Kafka (via Strimzi), small Postgres for dev/test, Elasticsearch/OpenSearch (via ECK). Still needs all the discipline below.

## StatefulSet vs Deployment

| Feature | Deployment | StatefulSet |
|---|---|---|
| Pod names | Random suffix | Stable: `<name>-0`, `<name>-1` |
| Storage | Shared or ephemeral | Per-Pod PVC via `volumeClaimTemplates` |
| Startup order | Parallel | Ordered (0 before 1 before 2) |
| Rolling update | Unordered | Reverse ordinal |
| Service | Regular | Usually paired with a **headless** Service |
| DNS | Service-level | Per-Pod: `<name>-0.<service>.<ns>.svc` |

Use StatefulSet when: identity matters (leader election, shard assignment), storage must survive restarts, startup order matters.

## Headless Service + StatefulSet

```yaml
apiVersion: v1
kind: Service
metadata: { name: postgres, namespace: data }
spec:
  clusterIP: None                    # headless — gives stable per-Pod DNS
  selector: { app: postgres }
  ports: [{ name: pg, port: 5432 }]
---
apiVersion: apps/v1
kind: StatefulSet
metadata: { name: postgres, namespace: data }
spec:
  serviceName: postgres              # must match headless Service
  replicas: 3
  selector: { matchLabels: { app: postgres } }
  template:
    metadata: { labels: { app: postgres } }
    spec:
      terminationGracePeriodSeconds: 60
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            - labelSelector: { matchLabels: { app: postgres } }
              topologyKey: kubernetes.io/hostname        # one per node
        # additional soft spread across zones
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector: { matchLabels: { app: postgres } }
      containers:
        - name: postgres
          image: postgres:16.4
          ports: [{ containerPort: 5432, name: pg }]
          resources:
            requests: { cpu: "2", memory: 4Gi }
            limits:   { cpu: "2", memory: 4Gi }           # Guaranteed QoS
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
          readinessProbe:
            exec: { command: ["pg_isready","-U","postgres"] }
            initialDelaySeconds: 10
            periodSeconds: 5
  volumeClaimTemplates:
    - metadata: { name: data }
      spec:
        accessModes: [ReadWriteOnce]
        storageClassName: gp3-retain
        resources:
          requests: { storage: 100Gi }
```

DNS per Pod: `postgres-0.postgres.data.svc.cluster.local`. Clients (replication, quorum) rely on this.

## PersistentVolumeClaim strategies

### Storage classes — pick deliberately

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata: { name: gp3-retain }
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
  encrypted: "true"
  kmsKeyId: alias/eks-ebs
reclaimPolicy: Retain                # do NOT delete PV when PVC deleted
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

Rules:
- `reclaimPolicy: Retain` for production data. `Delete` only for caches/scratch.
- `allowVolumeExpansion: true` so you can grow volumes without downtime.
- `volumeBindingMode: WaitForFirstConsumer` so the PV lands in the Pod's zone (otherwise cross-zone attachment fails on AWS/GCP).
- `encrypted: true` and a KMS CMK you control.
- One StorageClass per performance tier (gp3-standard, io2-high, st1-throughput).

### Access modes

- `ReadWriteOnce` — one node at a time. Default for block storage (EBS, GCE PD).
- `ReadWriteOncePod` — one Pod at a time (K8s 1.27+). Stricter; use for databases.
- `ReadWriteMany` — multiple nodes. Needs EFS/Filestore/Azure Files/CephFS. Slower, costlier; avoid for databases.

### Volume expansion (online)

```bash
# 1. Edit PVC requests.storage upward
kubectl patch pvc data-postgres-0 -n data \
  --type=json -p='[{"op":"replace","path":"/spec/resources/requests/storage","value":"200Gi"}]'

# 2. Depending on CSI driver, filesystem grows automatically on restart or online
# Verify:
kubectl get pvc -n data
```

### Shrinking is not supported

To shrink: take a backup, recreate PVC with smaller size, restore. Plan initial size conservatively.

## Anti-affinity — survive node and zone loss

```yaml
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector: { matchLabels: { app: postgres } }
        topologyKey: kubernetes.io/hostname          # no 2 Pods on one node
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector: { matchLabels: { app: postgres } }
          topologyKey: topology.kubernetes.io/zone   # prefer different zones
```

For 3 replicas on a 3-AZ cluster: use `requiredDuringScheduling` at `topologyKey: zone`. You lose scheduling flexibility but gain real zone-failure survival.

## PodDisruptionBudget — stop voluntary evictions from breaking quorum

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: postgres, namespace: data }
spec:
  minAvailable: 2                          # with 3 replicas, tolerate 1 down
  selector: { matchLabels: { app: postgres } }
```

Rules:
- Every StatefulSet with >1 replica needs a PDB.
- Use `minAvailable` (absolute number) for quorum-sensitive systems (etcd, Kafka, Postgres with Patroni, Zookeeper).
- Use `maxUnavailable` for stateless workloads.
- `minAvailable` should never equal `replicas` — otherwise no node drain is ever possible.

## Update strategies

```yaml
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 0       # only Pods ordinal >= partition get updated
      maxUnavailable: 1  # (K8s 1.24+, alpha earlier)
  podManagementPolicy: OrderedReady   # or Parallel
```

Partitioned rollouts:
- Set `partition: 2` on a 3-replica StatefulSet → only `replica-2` updates. Validate, then decrease partition.
- Essential for canary upgrades of stateful systems with replication.

## Backups — PV snapshots are not enough alone

### VolumeSnapshot (CSI)

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata: { name: ebs-snapshot }
driver: ebs.csi.aws.com
deletionPolicy: Retain
---
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata: { name: postgres-0-20251015, namespace: data }
spec:
  volumeSnapshotClassName: ebs-snapshot
  source: { persistentVolumeClaimName: data-postgres-0 }
```

Snapshots are fast for recovery but live in the same cloud account. Back up logically too:
- Postgres: `pg_basebackup` + WAL archiving to S3 (pgBackRest, WAL-G).
- MySQL: Percona XtraBackup to S3.
- MongoDB: `mongodump` or Ops Manager.
- Kafka: MirrorMaker to a DR cluster.

Never rely only on PV snapshots. Velero (see `backup-velero.md`) orchestrates cluster-wide snapshot + S3 offloads.

## Probes for stateful apps

```yaml
startupProbe:                          # gives long initialisations time
  exec: { command: ["pg_isready","-U","postgres"] }
  failureThreshold: 30
  periodSeconds: 10
readinessProbe:                        # controls Service membership
  exec: { command: ["pg_isready","-U","postgres"] }
  periodSeconds: 5
livenessProbe:                         # be careful — restart kills data consistency
  tcpSocket: { port: 5432 }
  initialDelaySeconds: 60
  periodSeconds: 30
  failureThreshold: 3
```

Never use aggressive liveness probes on databases. A false positive reboots a healthy primary and causes failover storms. Prefer a readiness probe + human-triggered restart.

## Operators — prefer over DIY

For production stateful workloads, use a mature operator rather than rolling your own StatefulSet:

| Workload | Operator |
|---|---|
| Postgres | CloudNativePG, Zalando Postgres Operator, Crunchy PGO |
| MySQL | Oracle MySQL Operator, Percona |
| Kafka | Strimzi |
| Elasticsearch / OpenSearch | ECK, OpenSearch Operator |
| MongoDB | MongoDB Community / Enterprise Operator |
| Redis | Redis Operator (Spotahome), Bitnami Redis chart for non-HA |

Operators handle: leader election, failover, backup scheduling, version upgrades, replica joins — the parts that break at 3am.

## Review checklist

- [ ] Is a managed service genuinely not an option? Documented why.
- [ ] StatefulSet backed by headless Service
- [ ] `volumeClaimTemplates` with `Retain` reclaim policy and encryption
- [ ] Anti-affinity across nodes; topology spread across zones
- [ ] PodDisruptionBudget with `minAvailable` safe for quorum
- [ ] `terminationGracePeriodSeconds` long enough for clean shutdown
- [ ] Guaranteed QoS (request == limit)
- [ ] StorageClass has `allowVolumeExpansion: true` and WaitForFirstConsumer
- [ ] Logical backups to off-cluster object storage, not just snapshots
- [ ] Quarterly restore drill documented and executed
- [ ] Operator used instead of hand-rolled StatefulSet where available
- [ ] Liveness probe cannot cause unnecessary restarts
