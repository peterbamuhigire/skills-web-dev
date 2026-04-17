# Cluster and Node Upgrade Runbook

A failed upgrade is a prolonged incident. Treat upgrades like a release, not a routine task.

## Cadence and version skew

- Kubernetes minor releases every ~4 months; each minor is supported ~14 months.
- Never let the cluster fall more than 2 minors behind. Skipping minors is unsupported — upgrade one at a time (1.27 -> 1.28 -> 1.29).
- Version skew rules: kubelet may be up to 3 minors behind kube-apiserver; never ahead.

## Pre-upgrade checks

1. Read the target release notes for removed/deprecated APIs (e.g. `policy/v1beta1 PodDisruptionBudget` removed at 1.25).
2. Run `kubectl deprecations` (Pluto, kube-no-trouble) against all manifests in Git.
3. Confirm Helm chart and operator compatibility with the target version.
4. Backup with Velero (resources + PVs). Verify the backup with a real restore in a sandbox cluster.
5. Check etcd health and snapshot it (managed clusters do this for you).
6. Drain test on one canary node — does PDB hold? Do workloads come back fast enough?

## Order of operations

```text
1. Control plane upgrade (managed: click the button; self-managed: kubeadm upgrade)
2. Wait until all control-plane components report the new version
3. Upgrade node groups one at a time
4. Upgrade kubectl/helm/argocd-cli on operator workstations
5. Upgrade add-ons (CNI, CoreDNS, metrics-server, ingress controller, cert-manager)
```

Add-ons last, because they often have their own version-skew matrix against the API server.

## Node upgrade pattern (rolling)

```bash
# Cordon + drain
kubectl cordon <node>
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data --grace-period=120

# Upgrade kubelet/runtime
# Uncordon
kubectl uncordon <node>
```

For managed node pools (EKS managed nodegroup, GKE node pool) prefer surge upgrades:

- `maxSurge: 1, maxUnavailable: 0` on small clusters — adds a node, drains an old one, removes it.
- Karpenter: drift-based replacement; let it churn nodes one at a time.

## PodDisruptionBudget discipline

A drain blocks on PDB. Without a PDB, all Pods of a Deployment can be evicted at once.

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: api }
spec:
  minAvailable: 50%        # or "N-1" for stateful
  selector: { matchLabels: { app: api } }
```

Rules:

- Every workload with replicas > 1 has a PDB.
- StatefulSets: `minAvailable: replicas - 1`.
- DaemonSets do not need PDBs (one per node by definition); upgrade them via `updateStrategy: RollingUpdate, maxUnavailable: 1`.
- A PDB of `minAvailable: 100%` blocks drains forever. Don't do that.

## Stateful workloads during upgrade

- Quiesce write-heavy workloads if possible (maintenance window or read-only mode).
- Confirm the StatefulSet `podManagementPolicy` and `updateStrategy` match what you want.
- Snapshot PVs before draining. Cloud storage snapshots are cheap; restore is the only thing that matters.
- Re-attach time on cloud disks is non-zero (30-120s). Plan for it in your SLO budget.

## Add-on upgrade order

```text
CNI (Calico/Cilium)        first - networking must be stable before anything else
kube-proxy / proxy mode
CoreDNS
metrics-server
ingress controller
cert-manager
operators (Argo, Prometheus stack, external-secrets)
service mesh (Istio/Linkerd) - last; they have the strictest skew
```

## Rollback

- Control plane: managed providers do not roll back minor versions. Plan forward — fix forward.
- Add-ons: keep the previous Helm release; `helm rollback <release> <previous-revision>`.
- Workloads: `kubectl rollout undo deployment/<name>`.
- Cluster-wide disaster: restore Velero backup into a fresh cluster of the previous version.

## Verification after upgrade

```bash
kubectl get nodes -o wide                                    # all Ready, target version
kubectl get pods -A | grep -v Running | grep -v Completed    # nothing stuck
kubectl get apiservices | grep False                         # no broken aggregated APIs
kubectl get --raw='/readyz?verbose'                          # api-server self-check
```

Smoke test: deploy a canary workload, exercise probes, hit ingress through the LB, run a backup, restore one resource.

## Anti-patterns

- Upgrading the control plane and node pools in the same change window.
- No PDB on tier-1 services — drain takes everything down.
- Trusting cloud provider auto-upgrade in production without staging the same version first.
- Upgrading add-ons before the API server.
- Skipping a Velero restore drill — backups you have never restored are not backups.
- Treating CRDs as upgradeable with `helm upgrade` — most charts intentionally do not upgrade CRDs; do it explicitly.
