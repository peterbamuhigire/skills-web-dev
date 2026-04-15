---
name: kubernetes-production
description: Use when operating production Kubernetes — Helm, autoscaling (HPA/VPA),
  resource management, StatefulSets, external-secrets, observability (Prometheus/Grafana/Loki),
  RBAC, Pod Security Standards, NetworkPolicies, admission control, backup (Velero),
  and cost control.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Kubernetes Production

<!-- dual-compat-start -->
## Use When

- Use when operating production Kubernetes — Helm, autoscaling (HPA/VPA), resource management, StatefulSets, external-secrets, observability (Prometheus/Grafana/Loki), RBAC, Pod Security Standards, NetworkPolicies, admission control, backup (Velero), and cost control.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `kubernetes-production` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
The operational bar for running K8s in production — not just running Pods, but running them predictably, securely, observably, and cheaply.

**Prerequisites:** Load `kubernetes-fundamentals` first.

## When this skill applies

- Moving a POC cluster into production.
- Auditing an existing cluster for production readiness.
- Adding observability, security, or cost controls.
- Reviewing Helm charts before deployment.

## The production checklist

```text
[ ] Helm (or Kustomize) — not raw manifests
[ ] requests + limits on every container
[ ] HPA on stateless workloads
[ ] PodDisruptionBudget on every workload with >1 replica
[ ] External secrets (Vault / AWS SM / GCP SM) — not inline Secret manifests
[ ] Observability: Prometheus + Grafana + Loki + Alertmanager
[ ] RBAC: least-privilege ServiceAccounts
[ ] Pod Security Standards enforced (restricted for app workloads)
[ ] NetworkPolicies: default-deny + explicit allow
[ ] Admission control: OPA Gatekeeper or Kyverno
[ ] Image scanning in CI (Trivy, Grype)
[ ] Backups: Velero with off-cluster storage
[ ] Cluster autoscaler or karpenter
[ ] SLOs + runbooks per service
```

## Helm vs Kustomize

```text
Package to distribute to many users / tenants  -> Helm
Env overlays (dev/staging/prod), single app    -> Kustomize
Complex templating + conditionals              -> Helm
Strict "WYSIWYG" manifests                     -> Kustomize
```

We use **Helm** for shipped packages and **Kustomize** for simple in-house env overlays. Never both for the same workload.

See `references/helm-vs-kustomize.md`.

## Resource management

**Requests:** guaranteed minimum; scheduler uses this to place Pods.
**Limits:** cap; exceeded CPU = throttled, exceeded memory = OOMKilled.

Rules:

- Always set both.
- Memory: limit = expected peak + headroom (~30%).
- CPU: request = steady-state; limit = 2–5× request or unset (in carefully-configured clusters).
- Measure before setting — `kubectl top` and Prometheus `container_memory_working_set_bytes`, `rate(container_cpu_usage_seconds_total[5m])`.
- Gradually reduce over-provisioning using VPA in recommend mode.

See `references/resource-management.md`.

## HPA — Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: { name: api, namespace: production }
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: api }
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource: { name: cpu, target: { type: Utilization, averageUtilization: 60 } }
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies: [{ type: Percent, value: 50, periodSeconds: 60 }]
    scaleUp:
      stabilizationWindowSeconds: 0
      policies: [{ type: Percent, value: 100, periodSeconds: 30 }]
```

- Target 60–70% CPU utilisation to leave headroom for spikes.
- `minReplicas: 2` minimum (HA).
- Scale up fast, scale down slow.
- For queue-depth-based or custom metrics: install Prometheus Adapter.

See `references/autoscaling-hpa-vpa.md`.

## Stateful workloads

StatefulSet + PVC for databases, caches, brokers:

- Stable names (`pod-0`, `pod-1`).
- Ordered rollout/rollback.
- Each Pod has its own PersistentVolume.
- Headless Service for stable DNS per Pod.
- PodDisruptionBudget (`minAvailable: N-1`).
- Anti-affinity across nodes/zones.
- Backups to object storage (never rely on PV alone).

For databases, strongly consider managed (RDS, Cloud SQL, Neon) before in-cluster. In-cluster DBs make sense only with serious ops maturity.

See `references/stateful-workloads.md`.

## External secrets

Never commit `Secret` manifests to Git (even base64 is not encryption). Options:

- **external-secrets operator** + Vault / AWS Secrets Manager / GCP Secret Manager / 1Password.
- **Sealed Secrets** (Bitnami) — encrypted manifests safe for Git.
- **SOPS + age** for GitOps-friendly encryption.

Pattern: external-secrets + cloud secret manager is our default in cloud; SOPS for air-gapped or self-hosted.

See `references/secrets-external-secrets.md`.

## Observability stack

**Minimum stack:**

- **Prometheus** — metrics scraping + storage (or Mimir/Thanos for long-term).
- **Grafana** — dashboards.
- **Loki** — logs.
- **Alertmanager** — alert routing.
- **OpenTelemetry Collector** — receive OTLP, fan out to backends.
- **Tempo** or **Jaeger** — traces.

Install via kube-prometheus-stack Helm chart.

**Golden signals per service:** latency, traffic, errors, saturation.

See `references/observability-stack.md`.

## RBAC + Pod Security

**RBAC principles:**

- One ServiceAccount per workload.
- No default ServiceAccount usage (set `automountServiceAccountToken: false` when not needed).
- Roles — least privilege.
- Audit unused ClusterRoleBindings periodically.

**Pod Security Standards** — enforce at namespace level:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

Restricted disallows: privilege escalation, hostPath, hostNetwork, running as root, etc.

See `references/rbac-and-pod-security.md`.

## NetworkPolicies — default deny

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny, namespace: production }
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
```

Then add explicit allows per workload (e.g., api can reach db, web can reach api, everything can reach DNS + external API).

Requires a CNI that enforces NetworkPolicy: Calico, Cilium, or Azure CNI. Flannel does not.

See `references/network-policies.md`.

## Admission control — OPA Gatekeeper or Kyverno

Policy-as-code enforcement at cluster admission:

- Deny `:latest` images.
- Require `resources.requests` and `resources.limits`.
- Require readinessProbe.
- Require specific labels (`app.kubernetes.io/*`, `owner`).
- Restrict which registries are allowed.
- Deny hostPath volumes.

**Kyverno** — YAML-based policies, easier for most teams.
**OPA Gatekeeper** — Rego-based, more powerful, steeper curve.

See `references/admission-control-opa-kyverno.md`.

## Image scanning

- **Trivy** or **Grype** in CI for container images and IaC.
- Fail builds on HIGH/CRITICAL.
- Sign images (cosign) and verify at admission (policy-controller or Kyverno).

## Backup — Velero

```bash
velero backup create weekly-$(date +%Y%m%d) --include-namespaces production --ttl 720h
```

- Backup + restore cluster resources and PersistentVolumes.
- Storage in off-cluster bucket (S3/GCS/Azure Blob).
- Scheduled backups with Velero Schedule.
- Regular restore drills — backups you never restore are hope, not a backup.

See `references/backup-velero.md`.

## Cost control

- **Cluster autoscaler** (or **karpenter** on AWS) — nodes scale with demand.
- **Right-sizing** — VPA in recommend mode, kubectl-cost, kubecost for cost dashboards.
- **Spot / preemptible nodes** — for stateless, fault-tolerant workloads. Use node taints + tolerations to steer.
- **Idle resource alerts** — requests far above usage = over-provisioning.

See `references/cost-control.md`.

## Anti-patterns

- Relying on default ServiceAccount tokens.
- Mounting every ConfigMap/Secret as env vars (file mounts are more secure, support rotation).
- Using Deployment for stateful workloads.
- HPA on workloads with startup > 60s without startup probe.
- Default-allow NetworkPolicy posture.
- Skipping backup/restore drills.
- No PodDisruptionBudget on critical services.

## Read next

- `kubernetes-saas-delivery` — multi-tenant SaaS on K8s, GitOps.
- `observability-monitoring` — SLO design and alert discipline across the stack.
- `reliability-engineering` — incident response + runbooks.

## References

- `references/helm-vs-kustomize.md`
- `references/resource-management.md`
- `references/autoscaling-hpa-vpa.md`
- `references/stateful-workloads.md`
- `references/secrets-external-secrets.md`
- `references/observability-stack.md`
- `references/rbac-and-pod-security.md`
- `references/network-policies.md`
- `references/admission-control-opa-kyverno.md`
- `references/backup-velero.md`
- `references/cost-control.md`
