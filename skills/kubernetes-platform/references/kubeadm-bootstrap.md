# kubeadm Bootstrap — Debian/Ubuntu Runbook

Self-managed cluster bring-up. Pairs with `SKILL.md` §2.

## Host Prerequisites

- Debian 12 or Ubuntu 22.04 LTS, fully patched.
- Swap disabled: `sudo swapoff -a` and remove the swap line from `/etc/fstab`.
- `br_netfilter` kernel module loaded; sysctl `net.bridge.bridge-nf-call-iptables=1` and `net.ipv4.ip_forward=1`.
- Time synced via `chrony` or `systemd-timesyncd`.
- Unique hostname, MAC, and `product_uuid` per host.

## Install containerd, kubeadm, kubelet, kubectl

Use the official Kubernetes apt repo for the target minor version. Pin all four packages with `apt-mark hold` so an unattended upgrade cannot move the kubelet ahead of the control plane.

```bash
sudo apt-get update && sudo apt-get install -y apt-transport-https ca-certificates curl gpg
# Install containerd from the distro or upstream package; configure /etc/containerd/config.toml
# Set SystemdCgroup = true under [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
sudo systemctl enable --now containerd

# Add the Kubernetes apt repo for the chosen minor; install kubeadm/kubelet/kubectl
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl
```

## Single Control-Plane Init

```bash
sudo kubeadm init \
  --apiserver-advertise-address=<control-plane-ip> \
  --pod-network-cidr=10.244.0.0/16 \
  --service-cidr=10.96.0.0/12
```

Save the printed `kubeadm join` command in a secrets vault — the bootstrap token expires in 24 hours. Re-issue with `kubeadm token create --print-join-command`.

## HA Control Plane

For three control-plane nodes behind a virtual IP or external load balancer:

1. Stand up the load balancer first (kube-vip, HAProxy + keepalived, or cloud LB) on TCP/6443.
2. Init the first control-plane node with `--control-plane-endpoint=<lb-ip-or-dns>:6443 --upload-certs`.
3. Use the printed `kubeadm join ... --control-plane --certificate-key=<key>` on the second and third control-plane nodes.
4. Workers join with the standard worker join command.

Configuration files for non-trivial clusters:

```yaml
# kubeadm-config.yaml
apiVersion: kubeadm.k8s.io/v1beta3
kind: InitConfiguration
nodeRegistration:
  kubeletExtraArgs:
    node-labels: "node-role/platform=true"
---
apiVersion: kubeadm.k8s.io/v1beta3
kind: ClusterConfiguration
kubernetesVersion: v1.30.0
controlPlaneEndpoint: "k8s-api.example.com:6443"
networking:
  podSubnet: 10.244.0.0/16
  serviceSubnet: 10.96.0.0/12
```

Run `sudo kubeadm init --config=kubeadm-config.yaml --upload-certs`.

## CNI Selection

Pick one and pin it. Do not mix.

| CNI | Strengths | Tradeoffs |
|---|---|---|
| Cilium | eBPF dataplane, NetworkPolicy, observability, optional service mesh. | Higher learning curve; kernel version requirements. |
| Calico | Mature, BGP routing optional, strong NetworkPolicy. | Plain iptables dataplane unless eBPF is enabled. |
| Flannel | Simple VXLAN overlay. | No NetworkPolicy on its own — pair with Calico for policy. |

Default recommendation for a small Debian/Ubuntu platform team: Cilium. Apply per the upstream install instructions for the version that matches the cluster minor.

## Post-Bootstrap Checklist

- `kubectl get nodes` — all `Ready`.
- `kubectl get pods -A` — every system pod `Running`.
- Label nodes by role: `kubectl label node <name> node-role/worker=true`.
- Apply taints for dedicated control-plane: kubeadm sets `node-role.kubernetes.io/control-plane:NoSchedule` by default.
- Copy `/etc/kubernetes/admin.conf` to the bastion under `~/.kube/config` with mode 0600.
- Schedule the etcd snapshot cron from `SKILL.md` §8 immediately, before the cluster has any tenants.

## Common Bootstrap Failures

- `kubelet` looping with cgroup driver mismatch — set `SystemdCgroup = true` in containerd and restart.
- `coredns` `Pending` — no CNI installed yet; install the pod network add-on.
- Workers cannot reach `kube-apiserver` — firewall on TCP/6443 or the wrong `--apiserver-advertise-address`.
- Node `NotReady` with `runtime network not ready` — CNI manifest applied but pods not yet scheduled; wait, then check the CNI DaemonSet.
