# Backup and Disaster Recovery — Velero

Velero backs up Kubernetes resources (as YAML) and PersistentVolumes (via CSI snapshots or Restic/Kopia file copy) to an object store. A backup you cannot restore is a fiction; restore drills are the only thing that proves DR.

## What Velero covers and does not

Covers:
- All Kubernetes API resources (Deployments, Services, ConfigMaps, Secrets, RBAC, CRDs, namespaces).
- PersistentVolumes via CSI VolumeSnapshot (fast, block-level) or FS backup (Kopia/Restic, file-level).
- Scheduled backups, retention, restore, partial restore, cross-cluster migration.

Does not cover well:
- Logical consistency of databases (a filesystem-level snapshot of a running Postgres data directory is risky — use `pg_basebackup` + WAL archiving as well).
- Very large PVs with FS backup (Kopia scales better than Restic but still has limits).
- etcd itself — use a separate etcd backup job for the control plane.

## Install on AWS (example)

```bash
# 1. S3 bucket + IAM user or IRSA role with putObject/getObject/listObject

# 2. Install Velero CLI, then:
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.10.0 \
  --bucket velero-backups-prod \
  --backup-location-config region=eu-west-1 \
  --snapshot-location-config region=eu-west-1 \
  --secret-file ./credentials-velero \
  --use-node-agent \
  --uploader-type kopia \
  --features=EnableCSI \
  --default-volumes-to-fs-backup=false
```

For IRSA (recommended over static keys):

```bash
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.10.0 \
  --bucket velero-backups-prod \
  --backup-location-config region=eu-west-1 \
  --no-secret \
  --pod-annotations eks.amazonaws.com/role-arn=arn:aws:iam::123:role/velero \
  --use-node-agent --uploader-type kopia \
  --features=EnableCSI
```

GCP: `velero-plugin-for-gcp`, GCS bucket. Azure: `velero-plugin-for-microsoft-azure`, Blob storage.

## BackupStorageLocation and VolumeSnapshotLocation

```yaml
apiVersion: velero.io/v1
kind: BackupStorageLocation
metadata: { name: default, namespace: velero }
spec:
  provider: aws
  objectStorage:
    bucket: velero-backups-prod
    prefix: clusters/prod-eu-west-1
  config:
    region: eu-west-1
    kmsKeyId: alias/velero-backups
  accessMode: ReadWrite
---
apiVersion: velero.io/v1
kind: VolumeSnapshotLocation
metadata: { name: aws-eu-west-1, namespace: velero }
spec:
  provider: aws
  config:
    region: eu-west-1
```

Rules:
- Store backups in a **different account or project** from the cluster (blast-radius isolation).
- Enable bucket versioning + MFA delete.
- Use KMS encryption with a key the cluster cannot overwrite.
- Use cross-region replication for critical backups.

## One-off backup

```bash
velero backup create prod-manual-$(date +%Y%m%d-%H%M) \
  --include-namespaces production,payment \
  --include-cluster-resources=true \
  --snapshot-volumes=true \
  --ttl 720h0m0s                            # 30 days

velero backup describe prod-manual-20251015-1200 --details
velero backup logs   prod-manual-20251015-1200
```

## Scheduled backups

```yaml
apiVersion: velero.io/v1
kind: Schedule
metadata: { name: daily, namespace: velero }
spec:
  schedule: "0 2 * * *"                       # 02:00 UTC daily
  template:
    includedNamespaces: [production, payment, identity]
    includedClusterScopedResources:
      - clusterroles.rbac.authorization.k8s.io
      - clusterrolebindings.rbac.authorization.k8s.io
      - customresourcedefinitions.apiextensions.k8s.io
    excludedResources: [events, events.events.k8s.io]
    snapshotVolumes: true
    storageLocation: default
    volumeSnapshotLocations: [aws-eu-west-1]
    ttl: 168h0m0s                             # 7 days
    hooks:
      resources:
        - name: postgres-quiesce
          includedNamespaces: [production]
          labelSelector:
            matchLabels: { app: postgres }
          pre:
            - exec:
                container: postgres
                command: ["/bin/bash","-c","psql -U postgres -c 'CHECKPOINT;'"]
                onError: Continue
                timeout: 30s
---
apiVersion: velero.io/v1
kind: Schedule
metadata: { name: weekly, namespace: velero }
spec:
  schedule: "0 3 * * 0"
  template:
    includedNamespaces: ["*"]
    ttl: 2160h0m0s                            # 90 days
    snapshotVolumes: true
```

Retention schedule example:
- Hourly for 24h (ops mistakes)
- Daily for 7 days (short recovery)
- Weekly for 90 days (regulatory)
- Monthly for 1 year (compliance)

## Pre/post hooks for database consistency

Filesystem snapshots of an open database can be inconsistent. Use exec hooks:

```yaml
hooks:
  resources:
    - name: pg-consistent
      includedNamespaces: [data]
      labelSelector: { matchLabels: { app: postgres } }
      pre:
        - exec:
            container: postgres
            command: ["/bin/sh","-c","pg_start_backup('velero', true)"]
            timeout: 30s
            onError: Fail
      post:
        - exec:
            container: postgres
            command: ["/bin/sh","-c","pg_stop_backup()"]
            timeout: 30s
```

Better still, layer Velero on top of native DB backups (pgBackRest, WAL-G, XtraBackup). Velero restores the cluster state; the DB backup tool restores the data.

## CSI snapshot vs FS backup

| Dimension | CSI snapshot | FS backup (Kopia/Restic) |
|---|---|---|
| Speed | Fast (block-level) | Slow (file-level) |
| Portability | Stuck in cloud/region | Portable across clouds |
| Cost | Snapshot storage charges | Object storage only |
| RPO | Near-instant | Depends on copy time |
| Restore to different cluster | Tricky (same cloud) | Easy |
| Use for | Same-region restore | Cross-cluster/migration |

Use both: CSI snapshots for fast restore, periodic FS backup for portable DR copies.

## Restore

```bash
# List backups
velero backup get

# Restore whole backup
velero restore create --from-backup prod-manual-20251015-1200

# Partial restore (one namespace)
velero restore create --from-backup daily-20251015020000 \
  --include-namespaces production \
  --restore-volumes=true

# Restore to a different namespace (e.g., for drill or investigation)
velero restore create drill-$(date +%s) \
  --from-backup daily-20251015020000 \
  --namespace-mappings production:production-drill
```

## Restore drills — mandatory

A backup never restored is hope. Schedule quarterly:

1. Spin up a sandbox cluster (kind, minikube, or a scratch cloud cluster).
2. Install Velero pointing at the production BackupStorageLocation (read-only credentials).
3. Pick a recent backup; restore a non-production namespace into the sandbox.
4. Verify: workloads come up, volumes mount, app answers, sample queries succeed.
5. Time the restore end-to-end — this is your RTO evidence.
6. Document gaps. File tickets. Re-test the fix.

Automate the drill with a GitHub Action / GitLab job that runs monthly:

```yaml
# .github/workflows/dr-drill.yml
name: DR drill
on:
  schedule: [{ cron: "0 6 1 * *" }]             # 1st of each month
jobs:
  restore-drill:
    runs-on: ubuntu-latest
    steps:
      - uses: engineerd/setup-kind@v0.6.0
      - run: |
          # Install Velero, restore latest backup, run smoke tests
          velero install --provider aws --bucket $BUCKET --no-secret \
            --plugins velero/velero-plugin-for-aws:v1.10.0
          LATEST=$(velero backup get -o json | jq -r '.items | sort_by(.metadata.creationTimestamp) | last | .metadata.name')
          velero restore create drill-${LATEST} --from-backup $LATEST
          ./scripts/smoke-test.sh
```

## etcd — separate from Velero

Velero runs in-cluster and cannot back up etcd itself (the control plane). For self-managed clusters, run etcd snapshots separately:

```bash
ETCDCTL_API=3 etcdctl snapshot save /backup/etcd-$(date +%F).db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/etcd/ca.crt \
  --cert=/etc/etcd/server.crt \
  --key=/etc/etcd/server.key

# Off-host: upload to S3/GCS with lifecycle rules
```

Managed clusters (EKS, GKE, AKS) handle control-plane state for you — still back up app data via Velero.

## Anti-patterns

- Backup bucket in the same account as the cluster with the same IAM role (ransomware blast radius).
- Trusting "snapshotVolumes: true" to capture a running database consistently.
- No restore drill in the past 90 days.
- Retention that only covers 7 days for data required for 1 year of legal holds.
- Encryption keys for backups sitting in the backed-up cluster's secret store (chicken-and-egg restore).
- No monitoring: silent backup failures go unnoticed until you need them.

## Monitoring Velero

Scrape the `/metrics` endpoint. Alert on:

```promql
# Backup failures in last 24h
increase(velero_backup_failure_total[24h]) > 0

# Last successful backup older than 36h
(time() - max(velero_backup_last_successful_timestamp)) > 36 * 3600

# Restore failures
increase(velero_restore_failed_total[1h]) > 0
```

## Review checklist

- [ ] Velero installed with uploader Kopia (or CSI + FS backup mix)
- [ ] Backup bucket in a separate account/project with versioning + MFA delete
- [ ] KMS encryption on objects
- [ ] Scheduled daily + weekly + monthly backups with appropriate TTLs
- [ ] Database-specific backups (pg_basebackup / XtraBackup / mongodump) in addition to Velero
- [ ] Pre/post hooks for stateful workloads
- [ ] Restore drill performed in last quarter with documented RTO
- [ ] Automated monthly DR drill in CI
- [ ] etcd snapshots (if self-managed control plane)
- [ ] Prometheus alerts on backup failure and staleness
- [ ] Restore runbook reviewed at quarterly game day
