# Phase 03: Platform Engineering

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the container orchestration and infrastructure-as-code skills that make production environments repeatable, auditable, and self-healing.

**Architecture:** Two new skill directories (`kubernetes-platform`, `infrastructure-as-code`) plus enhancements to two existing skills (`microservices-architecture-models`, `cicd-pipeline-design`). Target self-managed clusters on Debian/Ubuntu VPS first; cloud-managed second. IaC uses Terraform for cloud resources and Ansible for server configuration with ArgoCD for GitOps.

**Tech Stack:** Kubernetes, Helm, ArgoCD, Terraform, Ansible, Kong/Traefik, Nginx/HAProxy, FinOps tooling.

---

## Dual-Compatibility Contract

Same contract as Phases 01–02. Every `SKILL.md` must include:

```
Use When → Do Not Use When → Required Inputs →
Workflow → Quality Standards → Anti-Patterns → Outputs → References
```

Frontmatter:
```yaml
metadata:
  portable: true
  compatible_with: [claude-code, codex]
```

Optional helpers in **Platform Notes** only. Validate after every skill write:
```bash
python -X utf8 skill-writing/scripts/quick_validate.py <skill-directory>
```

---

## Task 1: Create `kubernetes-platform` skill

**Files:**
- Create: `kubernetes-platform/SKILL.md`
- Create: `kubernetes-platform/references/cluster-setup-debian.md`
- Create: `kubernetes-platform/references/helm-workloads.md`
- Create: `kubernetes-platform/references/k8s-security-hardening.md`
- Create: `kubernetes-platform/references/gitops-argocd.md`

**Step 1:** Write `kubernetes-platform/SKILL.md` covering:
- Core objects: Pod, Deployment, ReplicaSet, Service (ClusterIP, NodePort, LoadBalancer), Ingress, ConfigMap, Secret
- Namespaces: tenant isolation, RBAC per namespace, resource quotas, LimitRanges
- Storage: PersistentVolume, PersistentVolumeClaim, StorageClass, dynamic provisioning
- Health: readinessProbe, livenessProbe, startupProbe — what each checks and when it fires
- Scaling: HorizontalPodAutoscaler (CPU/memory/custom metrics), VerticalPodAutoscaler
- Pod security: runAsNonRoot, readOnlyRootFilesystem, securityContext, Pod Security Standards (restricted profile)
- Workload types: Deployment vs. StatefulSet vs. DaemonSet vs. Job vs. CronJob — decision table
- Networking: CoreDNS, NetworkPolicy, Ingress controller (Nginx Ingress), cert-manager + Let's Encrypt

Anti-Patterns: running containers as root, no resource requests/limits, storing secrets in ConfigMaps, NodePort exposure in production, skipping health probes.

**Step 2:** Write `references/cluster-setup-debian.md` — kubeadm install on Debian/Ubuntu VPS: control plane init, worker join, CNI (Calico or Flannel), kubectl config, kubeconfig setup.

**Step 3:** Write `references/helm-workloads.md` — Helm chart structure, `values.yaml` patterns, `helm upgrade --install` workflow, chart templating, Helmfile for multi-chart environments.

**Step 4:** Write `references/k8s-security-hardening.md` — RBAC role/rolebinding patterns, Pod Security Admission, network policies, image scanning with Trivy in CI, secrets encryption at rest.

**Step 5:** Write `references/gitops-argocd.md` — ArgoCD install, Application CRD, auto-sync, health checks, multi-environment promotion (dev → staging → prod), rollback via ArgoCD UI/CLI.

**Step 6:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py kubernetes-platform
git add kubernetes-platform/
git commit -m "feat: add kubernetes-platform skill (cluster ops, Helm, ArgoCD, security)"
```

---

## Task 2: Create `infrastructure-as-code` skill

**Files:**
- Create: `infrastructure-as-code/SKILL.md`
- Create: `infrastructure-as-code/references/terraform-patterns.md`
- Create: `infrastructure-as-code/references/ansible-server-config.md`
- Create: `infrastructure-as-code/references/iac-gitops-workflow.md`

**Step 1:** Write `infrastructure-as-code/SKILL.md` covering:
- IaC principles: idempotency, declarative vs. imperative, drift detection, immutable infrastructure
- Terraform: provider config, resource blocks, variables, outputs, state (local vs. remote S3+DynamoDB), modules, workspaces
- Terraform workflow: `init` → `plan` → `apply` → `destroy`; `plan` output must be reviewed in CI
- Ansible: inventory (static and dynamic), playbooks, roles, handlers, `become`, idempotency checks, `--check` dry-run
- GitOps: every infrastructure change goes through a PR; no manual console changes in production
- Drift detection: `terraform plan` in CI nightly to detect manual console changes
- State security: encrypt remote state, restrict state bucket access, never commit state files

Anti-Patterns: manual console changes in production, storing secrets in plain Terraform variables, no remote state locking, single monolithic Terraform root module.

**Step 2:** Write `references/terraform-patterns.md` — module structure for VPC + EC2 + RDS + S3, remote state config, `terraform.tfvars` vs. environment variables for secrets.

**Step 3:** Write `references/ansible-server-config.md` — playbook examples: install and harden Nginx, configure Node.js app as systemd service, PostgreSQL installation, user management.

**Step 4:** Write `references/iac-gitops-workflow.md` — full PR workflow: branch → plan → review plan output in PR comment → approve → merge → apply runs in CI.

**Step 5:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py infrastructure-as-code
git add infrastructure-as-code/
git commit -m "feat: add infrastructure-as-code skill (Terraform, Ansible, GitOps)"
```

---

## Task 3: Enhance `microservices-architecture-models`

**Files:**
- Modify: `microservices-architecture-models/SKILL.md`
- Create: `microservices-architecture-models/references/reverse-proxy-ops.md`
- Create: `microservices-architecture-models/references/api-gateway-ops.md`

**Step 1:** Read `microservices-architecture-models/SKILL.md` in full before editing.

**Step 2:** Add two new sections to SKILL.md (move depth to references to stay ≤ 500 lines):
- **Reverse Proxy Ops** — Nginx upstream config, load balancing, health checks, config reload without downtime, rate limiting, HAProxy as alternative for TCP-level balancing
- **API Gateway Ops** — Kong routing rules, plugins (JWT auth, rate limit, request transformation), Traefik as a Kubernetes-native alternative, plugin lifecycle

**Step 3:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py microservices-architecture-models
git add microservices-architecture-models/
git commit -m "feat: enhance microservices-architecture-models — reverse proxy ops, API gateway ops"
```

---

## Task 4: Enhance `cicd-pipeline-design`

**Files:**
- Modify: `cicd-pipeline-design/SKILL.md`
- Create: `cicd-pipeline-design/references/finops-cost-governance.md`

**Step 1:** Read `cicd-pipeline-design/SKILL.md` in full before editing.

**Step 2:** Add **FinOps / Cost Governance** section to SKILL.md:
- Resource quotas per namespace / environment
- Utilisation targets: CPU ≥ 60%, memory ≥ 70% before scaling out
- Budget guardrails: AWS Budgets / GCP Billing alerts, automated shutdowns for non-prod outside business hours
- Cost tagging strategy: every resource tagged with `env`, `team`, `product`
- Monthly cost review ritual: top-10 cost drivers, rightsizing recommendations

**Step 3:** Write `references/finops-cost-governance.md` — Terraform cost estimation with Infracost, AWS Cost Explorer queries, reserved capacity decision framework.

**Step 4:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py cicd-pipeline-design
git add cicd-pipeline-design/
git commit -m "feat: enhance cicd-pipeline-design — FinOps and cost governance section"
```

---

## Success Gate

- [ ] `kubernetes-platform` passes validator, portable metadata present
- [ ] `infrastructure-as-code` passes validator, portable metadata present
- [ ] `microservices-architecture-models` still passes validator after enhancement
- [ ] `cicd-pipeline-design` still passes validator after enhancement
- [ ] All new skills have `Platform Notes` not `Required Plugins`

---

## Reading Material

| Priority | Resource | Format | Cost | Unlocks |
|----------|----------|--------|------|---------|
| 1 | *Kubernetes in Action* — Marko Luksa (2nd ed.) | Book | ~$55 | `kubernetes-platform` core |
| 2 | *Production Kubernetes* — Rosso, Lander, Brand, Harris | Book | ~$50 | Ops-grade K8s, security hardening |
| 3 | *Terraform: Up & Running* — Yevgeniy Brikman (3rd ed.) | Book | ~$50 | `infrastructure-as-code` Terraform |
| 4 | *Infrastructure as Code* — Kief Morris (O'Reilly, 2nd ed.) | Book | ~$50 | IaC patterns, GitOps principles |
| 5 | ArgoCD documentation | Free (argo-cd.readthedocs.io) | Free | GitOps workflows |
| 6 | Helm documentation | Free (helm.sh/docs) | Free | Chart authoring and management |
| 7 | Infracost documentation | Free (infracost.io/docs) | Free | Terraform cost estimation |

**Read first:** *Kubernetes in Action* — it is the single best K8s book. Then *Terraform: Up & Running* for IaC.

---

*Next → `phase-04-observability-sre.md`*
