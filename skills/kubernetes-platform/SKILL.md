---
name: kubernetes-platform
description: Use when running Kubernetes as a platform team — bootstrapping self-managed clusters on Debian/Ubuntu, designing multi-tenant RBAC, enforcing Pod Security and resource quotas, and operating cluster lifecycle (upgrades, certs, etcd, ingress, cert-manager, metrics-server). Self-managed first, cloud-managed second.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# kubernetes-platform

Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Standing up a self-managed Kubernetes cluster on Debian/Ubuntu VPS hosts (kubeadm).
- Designing namespace, RBAC, ResourceQuota, LimitRange, and Pod Security boundaries for a multi-team or multi-tenant cluster.
- Owning cluster lifecycle: upgrades, certificate rotation, etcd backup and restore.
- Installing the minimum platform layer above the cluster: ingress controller, cert-manager, metrics-server.
- Choosing between self-managed kubeadm and cloud-managed control planes (EKS, GKE, AKS).

## Do Not Use When

- Authoring the application architecture inside the cluster — use `microservices-architecture` reference `references/microservices-architecture-models.md` and `microservices-architecture` reference `references/microservices-communication.md`.
- Provisioning the cluster's underlying VMs, VPC, or DNS through code — use `infrastructure-as-code` and `cloud-architecture`.
- Building CI/CD pipelines that deploy into Kubernetes — use `cicd-pipelines` or `cicd-pipelines` reference `references/cicd-pipeline-design.md`.
- Cluster-level observability deep-dives — use `observability-monitoring` reference `references/observability-platform.md` (SigNoz primary).
- Service mesh design (Istio, Linkerd, Cilium service mesh) — out of scope.

## Sibling Kubernetes Skills

This skill is the platform-team angle. Cross-reference rather than duplicate:

- `references/kubernetes-fundamentals.md` — first cluster, mental model of core objects, kubectl workflow, debug triage.
- `references/kubernetes-production.md` — Helm release patterns, HPA/VPA, observability stack, troubleshooting playbook.
- `references/kubernetes-saas-delivery.md` — multi-tenant isolation models, GitOps with ArgoCD, progressive delivery.

Load the sibling that owns a specific topic. This skill owns the bootstrap, governance, security, and lifecycle layer that those skills assume is in place.

## Required Inputs

- Target host inventory (control-plane and worker IPs, OS, RAM, CPU).
- Pod and service CIDR plan that does not collide with the host network.
- Tenant or team list for namespace and RBAC design.
- Compliance and data-residency constraints that drive self-managed vs managed.

## Prerequisite Skills

- `cloud-architecture` — for the network substrate.
- `cicd-pipelines` reference `references/cicd-jenkins-debian.md` — for the Linux operations baseline on Debian/Ubuntu hosts.
- `web-app-security-audit` — for baseline application security posture.

## Workflow

1. Confirm scope: bootstrap, governance, security, lifecycle, or platform-component install. Route topics owned by sibling skills (`references/kubernetes-fundamentals.md`, `references/kubernetes-production.md`, `references/kubernetes-saas-delivery.md`) to those skills before starting here.
2. Capture inputs: host inventory, CIDR plan, tenant list, compliance constraints.
3. Apply §1–§10 of this skill in order for a green-field cluster, or jump to the relevant section for a targeted change.
4. Load the matching `references/<topic>.md` file only when the depth is needed.
5. Produce the runbooks listed in `Outputs` and check them into the platform repo before handing the cluster to tenants.

## Quality Standards

- Self-managed kubeadm on Debian/Ubuntu is the default; cloud-managed is the alternative when constraints in §10 flip.
- Every namespace ships with RBAC, ResourceQuota, LimitRange, and a `restricted` Pod Security label before workloads land.
- Every cluster has an etcd snapshot cron and a documented restore drill. Untested backups do not count.
- Every platform component (ingress, cert-manager, metrics-server, CNI) is version-pinned in `platform/versions.yaml`.
- Cross-reference sibling Kubernetes skills rather than duplicating their guidance.

## §1 Cluster Architecture

Control-plane components (kubernetes.io/docs/concepts/overview/components/, fetched 2026-05-01):

| Component | Role |
|---|---|
| kube-apiserver | "The core component server that exposes the Kubernetes HTTP API." |
| etcd | "Consistent and highly-available key value store for all API server data." |
| kube-scheduler | "Looks for Pods not yet bound to a node, and assigns each Pod to a suitable node." |
| kube-controller-manager | "Runs controllers to implement Kubernetes API behavior." |
| cloud-controller-manager | "Integrates with underlying cloud provider(s)." Optional. |

Node components:

| Component | Role |
|---|---|
| kubelet | "Ensures that Pods are running, including their containers." |
| kube-proxy | "Maintains network rules on nodes to implement Services." Optional. |
| Container runtime | "Software responsible for running containers." |

For self-managed Debian/Ubuntu clusters, containerd is the default runtime. Verify against the current kubernetes.io container-runtimes page before pinning a version.

## §2 Self-Managed Bootstrap on Debian/Ubuntu

The full kubeadm bootstrap flow, kubelet flags, HA control-plane variant, and CNI selection rubric live in `references/kubeadm-bootstrap.md`. Minimum viable sequence:

```bash
# Control-plane node (Debian/Ubuntu, kubeadm + kubelet + containerd installed)
sudo kubeadm init \
  --apiserver-advertise-address=<control-plane-ip> \
  --pod-network-cidr=10.244.0.0/16   # match the chosen CNI

mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Install a CNI (Cilium, Calico, or Flannel) — required for Pod networking
# kubectl apply -f <CNI-manifest>

sudo kubeadm token create --print-join-command
```

Each worker:

```bash
sudo kubeadm join <control-plane-address>:<port> \
  --token <token> \
  --discovery-token-ca-cert-hash sha256:<hash>
```

Post-init: install the Pod network add-on, label nodes by role, and copy `admin.conf` to any management workstation. For HA control planes, use `InitConfiguration` and `JoinConfiguration` files; pass kubelet overrides through `nodeRegistration.kubeletExtraArgs`.

CNI choice (Cilium, Calico, Flannel) is left to the implementing team — pick one and pin it; do not mix.

## §3 Workloads — Minimum-Viable Manifests

Authoring core workloads is owned by `references/kubernetes-fundamentals.md`. The platform team still needs a reference for what "compliant by default" looks like, because every tenant manifest is reviewed against it. A Deployment + Service + Ingress that satisfies the `restricted` Pod Security profile:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: web, namespace: app }
spec:
  replicas: 3
  selector: { matchLabels: { app: web } }
  template:
    metadata: { labels: { app: web } }
    spec:
      serviceAccountName: web
      securityContext:
        runAsNonRoot: true
        seccompProfile: { type: RuntimeDefault }
      containers:
        - name: web
          image: ghcr.io/example/web:sha-abc1234
          ports: [{ containerPort: 3000 }]
          resources:
            requests: { cpu: "100m", memory: "128Mi" }
            limits:   { cpu: "500m", memory: "512Mi" }
          readinessProbe: { httpGet: { path: /healthz, port: 3000 }, periodSeconds: 5 }
          livenessProbe:  { httpGet: { path: /healthz, port: 3000 }, periodSeconds: 15 }
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities: { drop: ["ALL"] }
---
apiVersion: v1
kind: Service
metadata: { name: web, namespace: app }
spec:
  selector: { app: web }
  ports: [{ port: 80, targetPort: 3000 }]
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web
  namespace: app
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls: [{ hosts: [web.example.com], secretName: web-tls }]
  rules:
    - host: web.example.com
      http: { paths: [{ path: /, pathType: Prefix, backend: { service: { name: web, port: { number: 80 } } } }] }
```

Probe and lifecycle detail → see `references/kubernetes-fundamentals.md` §"Probes — Get Them Right". Mental model of Deployments, StatefulSets, Services → `references/kubernetes-fundamentals.md` §"Core Objects".

## §4 Helm

Chart structure and reserved directories (helm.sh/docs/topics/charts, fetched 2026-05-01):

| Path | Purpose |
|---|---|
| `Chart.yaml` | "A YAML file containing information about the chart." |
| `values.yaml` | "The default configuration values for this chart." |
| `templates/` | "A directory of templates that, when combined with values, will generate valid Kubernetes manifest files." |
| `charts/` | "A directory containing any charts upon which this chart depends." |
| `crds/` | Custom Resource Definitions installed before templates. |
| `values.schema.json` | Optional JSON Schema used to validate `values.yaml`. |
| `templates/NOTES.txt` | Post-install message printed to the user. |

> Helm reserves use of the `charts/`, `crds/`, and `templates/` directories. (helm.sh, fetched 2026-05-01.)

Release lifecycle:

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install web ./charts/web -n app --create-namespace -f values.prod.yaml
helm upgrade web ./charts/web -n app -f values.prod.yaml
helm rollback web 1 -n app
helm uninstall web -n app
```

Chart authoring patterns (named templates, subchart values overrides, chart testing, schema-validated values) → see `references/helm-charts.md`. Helm-vs-Kustomize tradeoff → `references/kubernetes-production.md` §"Helm vs Kustomize".

## §5 RBAC

Four object kinds: `Role` (namespace-scoped), `RoleBinding` (namespace-scoped), `ClusterRole` (cluster-scoped), `ClusterRoleBinding` (cluster-scoped). `ServiceAccount` is the workload identity. (kubernetes.io/docs/reference/access-authn-authz/rbac/.)

Namespace-admin Role + RoleBinding:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: { namespace: team-a, name: ns-admin }
rules:
  - apiGroups: [""]
    resources: ["pods", "services", "configmaps", "secrets"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
  - apiGroups: ["apps"]
    resources: ["deployments", "replicasets", "statefulsets"]
    verbs: ["*"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata: { namespace: team-a, name: team-a-admins }
subjects:
  - kind: Group
    name: team-a-admins
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: ns-admin
  apiGroup: rbac.authorization.k8s.io
```

Decision rubric:

| Need | Use |
|---|---|
| Permissions for users/groups inside one namespace | Role + RoleBinding |
| Cross-cluster permissions for platform admins | ClusterRole + ClusterRoleBinding |
| Permissions for a workload (pod) | ServiceAccount + Role/RoleBinding |
| Read-only "view" across all namespaces | Bind built-in `view` ClusterRole via ClusterRoleBinding |

Aggregated ClusterRoles, OIDC group mapping, audit patterns, and breakglass identities → `references/rbac-patterns.md`.

## §6 Resource Governance

`ResourceQuota` enforces aggregate limits per namespace (kubernetes.io/docs/concepts/policy/resource-quotas/, fetched 2026-05-01):

| Category | Example resource names |
|---|---|
| Compute | `requests.cpu`, `limits.cpu`, `requests.memory`, `limits.memory`, `hugepages-<size>` |
| Storage | `requests.storage`, `persistentvolumeclaims`, `<storage-class>.storageclass.storage.k8s.io/requests.storage` |
| Object counts | `pods`, `services`, `configmaps`, `deployments.apps`, etc. |
| Extended / DRA | `requests.nvidia.com/gpu`, DRA device-class quotas |

Key behaviour: namespace-scoped, non-retroactive, and once a CPU or memory quota is in force every pod in the namespace must declare matching `requests` and `limits`. Over-quota submissions are rejected with HTTP 403.

`LimitRange` sets default requests/limits and min/max values so authors get sane defaults when they omit them. `PriorityClass` lets the scheduler preempt low-priority pods to make room for critical workloads.

Quota + LimitRange for a tenant namespace:

```yaml
apiVersion: v1
kind: ResourceQuota
metadata: { name: team-a-quota, namespace: team-a }
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    pods: "100"
    persistentvolumeclaims: "20"
---
apiVersion: v1
kind: LimitRange
metadata: { name: team-a-defaults, namespace: team-a }
spec:
  limits:
    - type: Container
      default:        { cpu: "500m", memory: "512Mi" }
      defaultRequest: { cpu: "100m", memory: "128Mi" }
      max:            { cpu: "2",    memory: "4Gi" }
```

Per-tenant quota sizing, PriorityClass design for system vs workload tiers, and HPA interaction with quotas → `references/kubernetes-production.md` §"Resource Management".

## §7 Pod Security

Three Pod Security Standards profiles, cumulative (kubernetes.io/docs/concepts/security/pod-security-standards/, fetched 2026-05-01):

| Profile | Stance | Notable restrictions |
|---|---|---|
| Privileged | Unrestricted. | None — known privilege escalations allowed. For system/infrastructure workloads only. |
| Baseline | Minimally restrictive. | No host namespaces (`hostNetwork`, `hostPID`, `hostIPC`); no privileged containers; HostPath volumes restricted; capabilities limited; host ports restricted; seccomp not Unconfined; AppArmor/SELinux overrides restricted. |
| Restricted | Hardened best-practice. | All Baseline restrictions plus: run as non-root, read-only root filesystem, drop all capabilities, additional capability restrictions. |

Enforce by labelling the namespace: `pod-security.kubernetes.io/enforce: restricted` (verify the exact label key against the current Pod Security Admission docs before applying in production).

Compliant `securityContext` for `restricted`:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 10001
  seccompProfile: { type: RuntimeDefault }
containers:
  - name: app
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities: { drop: ["ALL"] }
```

`NetworkPolicy` is the namespace firewall. Default-deny ingress + egress, then allow only what is needed:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny, namespace: team-a }
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
```

Migrating an existing namespace from `baseline` to `restricted`, exempting infrastructure namespaces, and warn-vs-enforce strategy → `references/pod-security.md`.

## §8 Cluster Lifecycle

Upgrade flow:

1. `kubeadm upgrade plan` to see available targets and skew rules.
2. `kubeadm upgrade apply v<minor>.<patch>` on the first control-plane node.
3. `kubeadm upgrade node` on the remaining control-plane nodes and on every worker, one at a time, draining before and uncordoning after.

Verify the exact command sequence against the current kubeadm upgrade docs for the target minor version before running in production.

Certificate rotation: `kubeadm certs check-expiration` and `kubeadm certs renew all` rotate the kubeadm-issued control-plane certificates. After renewal, restart the static pods (`kube-apiserver`, `kube-controller-manager`, `kube-scheduler`) by removing and re-adding their manifests in `/etc/kubernetes/manifests/`.

etcd snapshot:

```bash
ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot save /backup/etcd-$(date +%F).db
```

Schedule the snapshot with cron and ship it to off-host storage. Restore with `etcdctl snapshot restore` per the upstream etcd docs.

Drain ordering, PodDisruptionBudgets, version-skew rules between kubelet and apiserver, and add-on upgrade order → `references/cluster-lifecycle.md`. Production-side rolling upgrade playbook → `references/kubernetes-production.md` §"Cluster and Node Upgrades".

## §9 Cluster-Managed Components

Minimum platform layer above a kubeadm cluster (CNI plus the three below):

| Component | Purpose | Reference |
|---|---|---|
| Ingress controller (ingress-nginx, Traefik) | Implements `Ingress` resources, terminates HTTPS, routes by host/path. | https://kubernetes.github.io/ingress-nginx/ |
| cert-manager | Issues TLS certs from Let's Encrypt or other ACME issuers and internal CAs; renews them automatically. | https://cert-manager.io/docs/ |
| metrics-server | Provides resource metrics for HPA and `kubectl top`. | https://github.com/kubernetes-sigs/metrics-server |

Pin a version per component, install with Helm or static manifest, and bake the chosen versions into the cluster bootstrap script. Detail on ClusterIssuer patterns, wildcard certs, ingress-class isolation per tenant, and metrics-server TLS flags → `references/cluster-managed-components.md`.

## §10 Self-Managed vs Managed

Lead with self-managed kubeadm on Debian/Ubuntu. Treat managed control planes as the alternative when the constraints below flip:

| Constraint | Choice | Why |
|---|---|---|
| Sovereignty / data residency on-prem or own VPS | Self-managed kubeadm on Debian/Ubuntu | Full control over node OS, no cloud lock-in. |
| Small platform team, predictable workload | Self-managed | Lower per-cluster cost; predictable ops surface. |
| Need elastic scale, multi-region failover, integrated cloud IAM | Cloud-managed (EKS/GKE/AKS) | Control-plane HA and upgrades handled by the provider. |
| Need GPU pools, integrated cloud services (S3, IAM) | Cloud-managed | Cluster-native cloud auth and storage classes. |

If two or more "cloud-managed" rows apply, do not self-manage — the operational tax outweighs the sovereignty benefit.

## Anti-Patterns

- Running tenant workloads in the same namespace as platform components.
- Granting `cluster-admin` to a team because RBAC design felt slow.
- Setting CPU `limits` equal to `requests` everywhere by reflex — causes throttling under spikes; reserve that pattern for latency-sensitive workloads.
- Enforcing `restricted` cluster-wide on day one without first running it as `warn` and fixing offenders.
- Skipping the etcd snapshot cron because "we never had to restore" — the first restore drill is not the day of the outage.
- Mixing two CNIs in one cluster.
- Copy-pasting EKS/GKE manifests into a kubeadm cluster without checking that the storage class, load-balancer class, and IAM assumptions still hold.

## Outputs

- A bootstrap runbook for the chosen control-plane and worker layout.
- A namespace, RBAC, ResourceQuota, and LimitRange template per tenant tier.
- A Pod Security enforcement plan with `warn` → `enforce` migration steps.
- An upgrade and etcd-backup runbook with rotation and restore drills.
- A pinned-version manifest for ingress controller, cert-manager, and metrics-server.

## Companion Skills

- `references/kubernetes-fundamentals.md` — core objects, kubectl, debug triage.
- `references/kubernetes-production.md` — Helm release patterns, scaling, observability stack.
- `references/kubernetes-saas-delivery.md` — multi-tenant isolation, GitOps, progressive delivery.
- `cloud-architecture` — VPC, load balancers, DNS substrate.
- `infrastructure-as-code` — Terraform modules that provision the VMs and network.
- `cicd-pipelines`, `cicd-pipelines` reference `references/cicd-pipeline-design.md`, `cicd-pipelines` reference `references/cicd-jenkins-debian.md` — pipelines that build and deploy into the cluster.
- `observability-monitoring` reference `references/observability-platform.md` — SigNoz-led observability above the cluster.
- `web-app-security-audit` — application-layer security for workloads inside the cluster.

## References

Tier 1 — Canonical:

- Kubernetes in Action, Marko Luksa, Manning.
- Production Kubernetes, Josh Rosso, Rich Lander, Alex Brand, John Harris, O'Reilly.
- kubernetes.io documentation — https://kubernetes.io/docs/.
- Components page — https://kubernetes.io/docs/concepts/overview/components/.
- kubeadm cluster guide — https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/.
- Pod Security Standards — https://kubernetes.io/docs/concepts/security/pod-security-standards/.
- Resource Quotas — https://kubernetes.io/docs/concepts/policy/resource-quotas/.
- Helm chart docs — https://helm.sh/docs/topics/charts/.

Tier 2 — Supporting:

- ingress-nginx — https://kubernetes.github.io/ingress-nginx/.
- cert-manager — https://cert-manager.io/docs/.
- metrics-server — https://github.com/kubernetes-sigs/metrics-server.

Tier 3 — Supplementary:

- kubeadm upgrade — https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/.

Deep-dives in `references/`:

- `kubeadm-bootstrap.md` — full bootstrap runbook, HA control plane, CNI selection.
- `helm-charts.md` — chart authoring patterns, schema validation, subchart overrides.
- `rbac-patterns.md` — aggregated roles, OIDC group mapping, audit, breakglass.
- `pod-security.md` — `warn` to `enforce` migration, exemptions, NetworkPolicy patterns.
- `cluster-lifecycle.md` — upgrade ordering, version skew, etcd restore drill.
- `cluster-managed-components.md` — ingress, cert-manager, metrics-server install patterns.
<!-- dual-compat-end -->

