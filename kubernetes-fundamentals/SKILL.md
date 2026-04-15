---
name: kubernetes-fundamentals
description: Use when starting with Kubernetes — core objects, kubectl workflow, manifests,
  probes, ingress, cluster setup (EKS/GKE/kind), and deciding when K8s is the right
  tool vs systemd, Docker Compose, ECS/Fargate, or PaaS.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Kubernetes Fundamentals

<!-- dual-compat-start -->
## Use When

- Use when starting with Kubernetes — core objects, kubectl workflow, manifests, probes, ingress, cluster setup (EKS/GKE/kind), and deciding when K8s is the right tool vs systemd, Docker Compose, ECS/Fargate, or PaaS.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `kubernetes-fundamentals` or would be better handled by a more specific companion skill.
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
Core concepts and the mental model before anything else. The trap with K8s is adopting it too early; the second trap is adopting it without the mental model.

## When this skill applies

- Evaluating whether to adopt K8s.
- Starting a new cluster.
- Writing your first manifests.
- Onboarding engineers onto K8s.
- Building a proof-of-concept deployment.

## When K8s is the right tool

```text
1 service, 1 VM, stable load                     -> systemd on Debian (use linux-security-hardening)
1-5 services, 1-2 hosts, simple scaling          -> Docker Compose (use cloud-architecture)
5-20 services, need scaling / self-heal / rollouts -> Kubernetes (managed: EKS / GKE / AKS)
Full managed PaaS acceptable, no K8s team        -> ECS Fargate / Cloud Run / Heroku / Railway / Render
Strict compliance, on-prem                       -> Self-hosted K8s
```

Rule: don't adopt K8s before you have enough services that orchestration + rollout + self-healing pays for the operational cost. If one person can deploy all your services with a shell script in 10 minutes, you don't need K8s yet.

See `references/when-k8s-is-right.md`.

## Core objects — the mental model

**Pod** — one or more containers sharing network + storage. Never create Pods directly; use a controller.

**Deployment** — declarative Pod management. You say "I want 3 replicas of this image with these env vars"; K8s keeps that true.

**Service** — stable virtual IP + DNS name that load-balances across matching Pods. Pods come and go; Services stay.

**Ingress** — HTTP(S) routing rules from outside the cluster to Services. Requires an Ingress controller (nginx, Traefik).

**ConfigMap / Secret** — configuration decoupled from images. Mount as env vars or files.

**Namespace** — logical isolation. One per environment per tenant (or per team, per app).

**PersistentVolume / PersistentVolumeClaim** — storage lifecycle separated from Pods.

**Job / CronJob** — run-to-completion workloads.

**StatefulSet** — Pods with stable identity (databases, brokers).

**DaemonSet** — one Pod per node (agents, collectors).

See `references/core-objects.md`.

## Minimal manifests (learn these by heart)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels: { app: api }
  template:
    metadata:
      labels: { app: api }
    spec:
      containers:
        - name: api
          image: myregistry/api:v1.2.3   # never :latest
          ports:
            - containerPort: 3000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef: { name: api-secrets, key: database-url }
          resources:
            requests: { cpu: 100m, memory: 128Mi }
            limits:   { cpu: 500m, memory: 256Mi }
          readinessProbe:
            httpGet: { path: /ready, port: 3000 }
            initialDelaySeconds: 3
            periodSeconds: 5
          livenessProbe:
            httpGet: { path: /live, port: 3000 }
            initialDelaySeconds: 15
            periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata: { name: api, namespace: production }
spec:
  type: ClusterIP
  selector: { app: api }
  ports: [{ port: 80, targetPort: 3000 }]
```

Four rules this manifest enforces:

1. Never `:latest` — always a pinned tag.
2. Always `resources.requests` and `resources.limits` — otherwise scheduling is unpredictable and OOM risk is high.
3. Always readiness probe — Service won't route to Pods not ready.
4. Liveness probe only for genuine stuck/crashed detection — misconfigured liveness causes restart loops.

## kubectl workflow

```bash
# Always use namespace context
kubectl config set-context --current --namespace=production

# Apply is declarative; use it
kubectl apply -f manifests/

# Debugging triad
kubectl get pods              # what exists
kubectl describe pod <name>   # why it's not healthy (events!)
kubectl logs <pod> -c <container> --tail=200 -f
kubectl exec -it <pod> -- sh  # into the container

# Rollouts
kubectl rollout status deployment/api
kubectl rollout undo deployment/api
kubectl rollout history deployment/api

# Resource usage
kubectl top pods
kubectl top nodes
```

Prefer `kubectl apply -k` (Kustomize) or Helm for real work — raw manifests are fine for learning. See `references/kubectl-workflow.md`.

## Labels, selectors, annotations

**Labels** — identifying metadata used for selection. Services find Pods via label selectors. Use the recommended labels: `app.kubernetes.io/name`, `app.kubernetes.io/instance`, `app.kubernetes.io/version`, `app.kubernetes.io/component`, `app.kubernetes.io/managed-by`.

**Annotations** — non-identifying metadata (build number, commit SHA, owner email, change-cause).

**Never** rely on a Pod name; rely on labels.

## Probes — get them right

- **Readiness probe:** is this Pod ready to receive traffic? Failing = Service stops routing. Uses: DB connection, cache warm-up, dependency check.
- **Liveness probe:** is this Pod stuck? Failing = kubelet restarts container. Uses: deadlock detection only. If you can't distinguish "stuck" from "slow under load," don't set a liveness probe.
- **Startup probe:** for slow-starting apps. Disables liveness until startup succeeds.

Anti-pattern: making liveness call DB. DB blip → all Pods restart → cascade.

See `references/probes-and-lifecycles.md`.

## Ingress controllers

- **nginx-ingress** — most widely used. Reliable, feature-rich.
- **Traefik** — great UX, dashboard, automatic Let's Encrypt.
- **Cloud LB-backed:** AWS LB Controller (ALB), GCP GCE Ingress — tighter cloud integration.
- **Gateway API** — newer, standard-track replacement for Ingress. Use if your controller supports it.

Pattern: one Ingress per app/tenant with TLS via cert-manager. See `references/ingress-controllers.md`.

## Cluster options

| Option | Use when |
|---|---|
| **EKS** (AWS) | You're on AWS; pay for control plane; add karpenter for cheap node scaling |
| **GKE** (GCP) | You're on GCP; best managed K8s experience; Autopilot for zero-node-ops |
| **AKS** (Azure) | Azure-first organisation |
| **DigitalOcean / Linode LKE** | Small team, cost-sensitive |
| **kind / minikube / k3d** | Local development and CI |
| **k3s / k0s** | Edge / on-prem, low-resource |
| **kubeadm** | Only if you must self-host; expect ops cost |

See `references/cluster-setup-eks-gke.md` and `references/local-kind-minikube.md`.

## Anti-patterns

- `:latest` image tags.
- No resource requests/limits.
- Liveness probe hitting a dependency.
- Secrets committed in Git in `Secret` manifests (use sealed-secrets, SOPS, or external-secrets).
- hostPath volumes.
- Privileged containers.
- Missing PodDisruptionBudget on stateful workloads.
- One giant namespace for everything.
- `kubectl edit` for permanent changes — bypasses Git source of truth.
- Long-running jobs as Deployments — use Job/CronJob.

## Read next

- `kubernetes-production` — Helm, autoscaling, observability, security baseline.
- `kubernetes-saas-delivery` — multi-tenant patterns, GitOps, progressive delivery.
- `cloud-architecture` — non-K8s alternatives and Docker baseline.

## References

- `references/when-k8s-is-right.md`
- `references/core-objects.md`
- `references/kubectl-workflow.md`
- `references/probes-and-lifecycles.md`
- `references/ingress-controllers.md`
- `references/cluster-setup-eks-gke.md`
- `references/local-kind-minikube.md`
- `references/anti-patterns.md`
