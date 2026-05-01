# Cluster Lifecycle — Upgrades, Certs, etcd Restore

Pairs with `SKILL.md` §8. For the production-side rolling-upgrade playbook see `kubernetes-production` §"Cluster and Node Upgrades".

## Version Skew Rules

- `kube-apiserver` may be at most one minor ahead of `kubelet` and `kube-proxy`.
- `kubelet` must not be ahead of `kube-apiserver`.
- `kubectl` may be one minor on either side of `kube-apiserver`.

Upgrade in this order: control-plane apiservers first, then control-plane controller-manager and scheduler, then kubelets on control-plane nodes, then kubelets on workers, then kubectl clients. kubeadm does the first three steps for you.

## Upgrade Sequence

```bash
# On the FIRST control-plane node
sudo apt-mark unhold kubeadm
sudo apt-get install -y kubeadm=<target-version>
sudo apt-mark hold kubeadm

sudo kubeadm upgrade plan
sudo kubeadm upgrade apply v<minor>.<patch>

# Drain, upgrade kubelet/kubectl, uncordon
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data
sudo apt-mark unhold kubelet kubectl
sudo apt-get install -y kubelet=<target-version> kubectl=<target-version>
sudo apt-mark hold kubelet kubectl
sudo systemctl daemon-reload && sudo systemctl restart kubelet
kubectl uncordon <node>

# On EACH remaining control-plane node and EACH worker
sudo kubeadm upgrade node
# then drain/kubelet-upgrade/uncordon as above
```

Verify after each node: `kubectl get nodes`, every system pod `Running`, application probes green.

## PodDisruptionBudgets

Before draining, every business-critical workload should have a PDB:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: web, namespace: app }
spec:
  minAvailable: 2
  selector: { matchLabels: { app: web } }
```

A drain that violates PDBs blocks until pods can be evicted. If the upgrade window is hard-bounded, raise replica counts before draining so PDB constraints can be satisfied without downtime.

## Add-On Upgrade Order

After the cluster minor is upgraded, walk the platform layer in this order:

1. CNI (per its upstream upgrade docs).
2. CoreDNS (kubeadm normally upgrades this with the control plane).
3. metrics-server.
4. Ingress controller.
5. cert-manager.
6. Workload Helm releases.

Each step has its own compatibility matrix — check the project docs before bumping.

## Certificate Rotation

```bash
sudo kubeadm certs check-expiration
sudo kubeadm certs renew all
# Restart the static control-plane pods to pick up the new certs
sudo mv /etc/kubernetes/manifests/{kube-apiserver,kube-controller-manager,kube-scheduler}.yaml /tmp/
sleep 10
sudo mv /tmp/{kube-apiserver,kube-controller-manager,kube-scheduler}.yaml /etc/kubernetes/manifests/
```

kubeadm's auto-renewal happens on every `kubeadm upgrade`, so a regular upgrade cadence (every 3-6 months) keeps certs from ever expiring in the wild.

After renewing, regenerate any `kubeconfig` files for human users that were issued from the old CA.

## etcd Restore Drill

Run a restore drill at least quarterly on a non-production cluster.

```bash
# Stop static pods
sudo mv /etc/kubernetes/manifests /etc/kubernetes/manifests.bak

# Restore the snapshot to a fresh data dir
ETCDCTL_API=3 etcdctl snapshot restore /backup/etcd-2026-04-01.db \
  --data-dir=/var/lib/etcd-restored

# Point the etcd static pod at the restored data dir
sudo sed -i 's|/var/lib/etcd|/var/lib/etcd-restored|g' /etc/kubernetes/manifests.bak/etcd.yaml
sudo mv /etc/kubernetes/manifests.bak /etc/kubernetes/manifests
```

Document the exact filenames, paths, and rollback steps for the cluster you actually run; the drill is the documentation.

## Anti-Patterns

- Skipping `kubeadm upgrade plan` and going straight to `apply` — you lose the skew warning.
- Running `kubeadm upgrade apply` on more than one control-plane node concurrently.
- Deleting `/var/lib/etcd` before the restore command writes the new directory.
- Letting kubeadm certs expire because the cluster has been "stable for a year" — `kubeadm certs check-expiration` is a monthly task.
- Treating the etcd snapshot job as installed once snapshot files appear — verify a restore.
