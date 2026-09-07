---
name: infrastructure-as-code
description: Use when provisioning or changing cloud infrastructure with Terraform or Ansible — modules, remote state with S3 native locking, workspaces vs directory-per-env, common AWS patterns, idempotent Ansible roles for Debian/Ubuntu, GitOps with ArgoCD/Flux, drift detection, and Vault secret injection.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Infrastructure as Code

Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Provisioning or changing cloud infrastructure with Terraform or Ansible — modules, remote state, workspaces, AWS patterns, idempotent Ansible roles, GitOps with ArgoCD/Flux, drift detection, Vault secret injection.

## Do Not Use When

- Vault PKI, dynamic secrets, or rotation depth is needed — load `cicd-devsecops`.
- The work is CI/CD pipeline construction around IaC — load `cicd-pipelines` or `cicd-pipeline-design`.
- The work is Kubernetes object authoring (Deployments, Services, Helm charts) — load `kubernetes-platform`.

## Required Inputs

- Project context, target cloud (or self-managed Debian/Ubuntu), and the concrete change to make.
- Confirm deliverable: design, code, review, migration plan, audit, or runbook.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that the task needs.
- Apply the ordered guidance, decision rules, and acceptance criteria here instead of cherry-picking snippets.
- Make assumptions, risks, and follow-up work explicit when they matter.

## Quality Standards

- Outputs are execution-oriented, concise, and consistent with the repository engineering baseline.
- Preserve existing project conventions unless this skill requires a stronger standard.
- Prefer deterministic, reviewable steps over tool-specific magic.

## Outputs

- Concrete result fitted to the task: implementation guidance, review findings, ADR-style decisions, templates, or generated artifacts.
- Explicit assumptions, tradeoffs, or unresolved gaps when context is incomplete.

## References

- `references/terraform-modules-state.md` — module skeleton, registry conventions, state commands, import, splitting state, backend choice.
- `references/aws-patterns.md` — VPC, ECS+ALB, RDS, S3 lifecycle, Terratest.
- `references/ansible-debian.md` — inventory, role layout, idempotency patterns, hardening playbook, tags.
- `references/gitops-argocd-flux.md` — ArgoCD `Application`/`ApplicationSet`, Flux bootstrap, drift wiring.
<!-- dual-compat-end -->

## Why IaC

## Inputs
| Input | Required | Purpose |
|---|---|---|
| Desired resources and environment | yes | Bound change |
| Existing state and provider versions | yes | Prevent drift damage |
| Identity and approval policy | yes | Set execution boundary |

## Capability contract
Author and validate code by default. Apply, destroy, import, state edits, and secret writes require explicit environment authority and a reviewed plan.

## Degraded mode
If credentials or state are unavailable, run static validation and return an unverified plan checklist; never simulate apply results.

## Decision rules
| Condition | Action |
|---|---|
| Plan replaces stateful resource | Require recovery plan |
| Existing resource lacks state ownership | Import or document exception |
| Secret would enter source or state | Use external secret boundary |

## Domain Anti-Patterns
- Editing remote state manually. Fix: use supported commands with backup.
- Applying an unreviewed plan. Fix: approve a saved plan.
- Hardcoding secrets. Fix: inject references at runtime.
- Copying divergent environment modules. Fix: share versioned modules.
- Ignoring drift. Fix: schedule read-only plans.

Snowflake servers — hand-configured, undocumented, irreplaceable — cause outages nobody can recover from. IaC puts environments in version-controlled code, making drift a diffable artifact and rebuilds a routine operation.

## §1 Terraform Fundamentals

Terraform's core blocks:

| Block | Role |
|---|---|
| `terraform` | `required_providers`, `required_version`, `backend`. |
| `provider` | Configures a provider (`aws`, `google`, `kubernetes`, `helm`, `vault`). |
| `resource` | Declares a managed object (e.g. `aws_instance`, `aws_s3_bucket`). |
| `data` | Reads existing infrastructure without managing it. |
| `variable` / `output` | Input/output contract of a configuration or module. |
| `locals` | Computed expressions reused inside the config. |
| `module` | Composition: include another configuration. |

Pin provider and Terraform versions — a minor provider bump can silently change resource behaviour.

```hcl
terraform {
  required_version = ">= 1.7.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  backend "s3" {
    bucket       = "acme-tfstate"
    key          = "envs/prod/main.tfstate"
    region       = "eu-west-1"
    encrypt      = true
    use_lockfile = true   # native S3 locking — preferred
  }
}

provider "aws" { region = var.region }

variable "region"      { type = string }
variable "environment" { type = string }
variable "project" {
  type        = string
  description = "Project slug used in resource names"
  validation {
    condition     = can(regex("^[a-z0-9-]{3,20}$", var.project))
    error_message = "project must be 3-20 chars, lowercase, digits, or hyphens."
  }
}

module "network" {
  source      = "./modules/network"
  cidr        = "10.20.0.0/16"
  environment = var.environment
}

resource "aws_s3_bucket" "assets" {
  bucket = "acme-${var.environment}-assets"
  tags   = { Project = var.project, Environment = var.environment }
}

output "vpc_id"           { value = module.network.vpc_id }
output "app_bucket_name"  { value = aws_s3_bucket.assets.id }
```

For a full VPC + ECS + RDS + S3 lifecycle example see `references/aws-patterns.md`.

## §2 State Management

Never commit `terraform.tfstate` to Git — it stores secrets in plaintext and creates merge conflicts. Use a remote backend with locking.

The HashiCorp S3-backend documentation is explicit on locking:

> Locking can be enabled via S3 or DynamoDB. However, DynamoDB-based locking is deprecated. To enable S3 state locking directly, use the `use_lockfile` argument (set to true).

The legacy `dynamodb_table` argument requires a table whose partition key is `LockID` of type String. New configurations should use `use_lockfile = true`; existing configurations may run both during transition.

Backend choice:

| Backend | When | Locking |
|---|---|---|
| S3 + `use_lockfile = true` | AWS-hosted, current best practice | Native S3 conditional writes |
| S3 + `dynamodb_table` | Legacy; existing configs | DynamoDB partition key `LockID` (string) |
| GCS | GCP-hosted projects | Native object generation locking |
| Terraform Cloud / Enterprise | Hosted, team workflows | Built in |

Importing existing infrastructure:

```bash
# Bring an existing AWS S3 bucket under Terraform management
terraform import aws_s3_bucket.assets acme-prod-assets
# Then write the resource block to match — terraform plan should show no diff.

terraform state list
terraform state show aws_s3_bucket.assets
terraform state rm aws_s3_bucket.assets       # untrack without destroying
```

Split state per blast-radius boundary — `network/`, `data/`, `app/` — and cross-reference outputs through `terraform_remote_state`. See `references/terraform-modules-state.md`.

## §3 Module Design

A module is a directory of `.tf` files consumed via `module "name" { source = "..." }`. Pin to an exact Git tag — `main` can break you on any push.

Module skeleton:

```text
modules/network/
  main.tf          # resources
  variables.tf     # typed, documented inputs
  outputs.tf       # exported values consumers depend on
  versions.tf      # required_providers, required_version
  README.md        # usage example, input/output table
```

Versioning and registry:

- Tag modules in Git with semver (`v1.2.0`); consumers reference by tag.
- Public modules consumed via the Terraform Registry use `source = "namespace/name/provider"` and `version = "x.y.z"`.
- Registry naming convention: `terraform-<PROVIDER>-<NAME>` for module repositories (e.g. `terraform-aws-vpc`).

```hcl
module "vpc_git" {
  source = "git::https://github.com/acme/tf-modules.git//modules/vpc?ref=v1.2.0"
  name   = "acme-prod"
  cidr   = "10.20.0.0/16"
  azs    = ["eu-west-1a", "eu-west-1b"]
}

module "vpc_registry" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.5.1"
  # ...
}
```

Composability rule of thumb: a module should do one thing — a network, a database, a service. Avoid the "everything module" — it forces consumers to accept defaults they cannot opt out of. Deeper input/output contract patterns in `references/terraform-modules-state.md`.

## §4 Workspaces and Environments

| Pattern | When to use | Trade-off |
|---|---|---|
| `terraform workspace` (named workspaces, single backend key path) | Lightweight per-env separation in the same configuration | Easy to apply to the wrong env; small blast radius only. |
| Directory per environment (`envs/dev`, `envs/staging`, `envs/prod`) with separate backends | Strong isolation; each env has its own state | More duplication; manage with module composition. |
| Terragrunt-style stacks | Many envs / regions, DRY backend config | Extra tool to learn. |

For production SaaS, prefer directory-per-env with module composition. For small projects, workspaces are fine:

```bash
terraform workspace new prod && terraform workspace select prod
terraform apply -var-file="prod.tfvars"
```

```hcl
locals {
  instance_size = {
    dev = "t3.micro", staging = "t3.small", prod = "m6i.large"
  }[terraform.workspace]
}
```

When prod must live in a separate AWS account, directory-per-env is mandatory — workspaces share backend credentials.

## §5 Ansible for Debian/Ubuntu

The Ansible playbook documentation defines the model:

> A playbook consists of one or more "plays" in an ordered list. Each play executes part of the overall goal of the playbook, running one or more tasks. Each task calls an Ansible module.

Each play needs `hosts` (the targeted managed nodes) and at least one task. Plays and tasks execute top-to-bottom; each task runs against all matched hosts before the next task starts.

Minimum nginx role and inventory:

```ini
# inventories/prod/hosts.ini
[web]
web1.example.com
web2.example.com

[debian:children]
web

[debian:vars]
ansible_user=deploy
ansible_python_interpreter=/usr/bin/python3
```

```yaml
# roles/nginx/tasks/main.yml
- name: Ensure nginx is installed
  ansible.builtin.apt:
    name: nginx
    state: present
    update_cache: true
    cache_valid_time: 3600

- name: Deploy nginx site config
  ansible.builtin.template:
    src: site.conf.j2
    dest: /etc/nginx/sites-available/{{ site_name }}.conf
    owner: root
    group: root
    mode: "0644"
  notify: Reload nginx

# roles/nginx/handlers/main.yml
- name: Reload nginx
  ansible.builtin.service: { name: nginx, state: reloaded }
```

Idempotency rule: running the playbook ten times leaves the system identical to running it once. Ansible modules are idempotent by default; raw shell commands are not — use `ansible.builtin.file`, `apt`, `template`, `systemd`, and only fall back to `command`/`shell` with explicit `changed_when` and `failed_when`.

Variable precedence (most-specific wins): `-e` > task > block > role > play > host > group > role defaults. Dry-run before prod with `ansible-playbook -i inventories/prod site.yml --check --diff`.

For role layout, dynamic AWS inventory, dependency declarations, and a baseline Ubuntu hardening playbook (`ufw`, `fail2ban`, `unattended-upgrades`, deploy user, SSH keys), see `references/ansible-debian.md`.

## §6 GitOps — ArgoCD and Flux

The Git repo is the single source of truth; a controller continuously reconciles the live cluster to match.

ArgoCD's documented model:

> Argo CD continuously monitors running applications and compares the current, live state against the desired target state (as specified in the Git repo). Applications that deviate from this target configuration are flagged as `OutOfSync`.

ArgoCD `syncPolicy` fields:

| Field | Effect |
|---|---|
| `automated.enabled` | Activate automated sync. |
| `automated.prune: true` | Automatically delete resources removed from Git. |
| `automated.selfHeal: true` | Re-sync when the live cluster state deviates from Git. |
| `automated.allowEmpty` | Permit applications with empty manifests when pruning. |
| `retry.refresh` | Refresh on new revisions during sync retries. |

ArgoCD also supports `PreSync`, `Sync`, and `PostSync` hooks for blue/green and canary rollouts, plus `ApplicationSet` for multi-cluster fan-out.

Flux is multi-controller and headless:

| Controller | Role |
|---|---|
| `source-controller` | Watches Git/OCI/Helm repositories and produces an artifact for other controllers. |
| `kustomize-controller` | Reconciles Kubernetes resources from Kustomize overlays. |
| `helm-controller` | Ensures the state of the Helm release matches what is defined in the resource, performs a release if this is not the case. |
| `notification-controller` | Manages alerts, events, and outbound webhooks. |
| Image automation controllers | Detect new images and update Git automatically. |

Decision rubric:

| Need | Choice |
|---|---|
| First-class web UI for app teams | ArgoCD |
| Tight Helm + Kustomize integration with separable controllers | Flux |
| Image-update-driven promotion across environments | Flux (image-automation controllers) |
| `ApplicationSet` / multi-cluster fan-out | ArgoCD |

Drift detection: ArgoCD flips `Application` to `OutOfSync` natively. For Terraform-managed resources, schedule `terraform plan -detailed-exitcode` every 6 hours and alert on exit code 2. Concrete manifests, bootstrap commands, and notification wiring live in `references/gitops-argocd-flux.md`.

## §7 Terraform vs Ansible Decision Matrix

| Dimension | Terraform | Ansible |
|---|---|---|
| Primary purpose | Provisioning cloud resources, declarative with a state file. | Server configuration and change application — procedural-feeling but idempotent modules. |
| Lifecycle model | Plan/apply against state; destroy is first-class. | Run-to-converge; no state file. |
| Best at | "Make these cloud resources exist." | "Make these existing servers look like this." |
| Worst at | Imperative, ordered changes on existing servers. | Tracking desired vs actual state of cloud resources at scale. |
| Idempotency model | State file plus provider plan. | Module-level idempotency checks. |

Rule of thumb: **Terraform creates the VPS; Ansible configures it.** For Kubernetes, GitOps replaces both — Terraform creates the cluster, ArgoCD or Flux reconciles workloads from Git.

In practice the two cooperate: Terraform creates the EC2 instance and emits its IP into an Ansible inventory; Ansible installs nginx, users, firewall rules.

## §8 Secrets at the IaC Boundary

Risks:

1. Secrets read by Terraform end up in plaintext inside the state file. Treat the state backend as a sensitive store — encrypt at rest, restrict IAM/ACL access, version the bucket.
2. `sensitive = true` on a variable or output suppresses console echo but does not encrypt state.
3. Ansible Vault encrypts variable files at rest, but the playbook process sees plaintext at runtime — secure the runner and the SSH path.

Patterns:

| Pattern | Tooling | Notes |
|---|---|---|
| Pull at apply time from HashiCorp Vault | `vault` provider in Terraform; `community.hashi_vault` in Ansible | Centralised rotation; depth in `cicd-devsecops`. |
| Pull from cloud KMS / Secrets Manager | `aws_secretsmanager_secret_version`, `google_secret_manager_secret_version` | Avoids running an additional service. |
| Encrypt-at-rest var files | Ansible Vault, SOPS, age | Useful when there is no Vault yet. |

```hcl
provider "vault" { address = "https://vault.acme.internal" }
data "vault_generic_secret" "rds" { path = "secret/data/prod/rds" }

resource "aws_db_instance" "primary" {
  username = data.vault_generic_secret.rds.data["username"]
  password = data.vault_generic_secret.rds.data["password"]
}
```

For Kubernetes workloads use `external-secrets-operator` so manifests reference a Vault path, not a literal secret:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata: { name: api-db, namespace: api-prod }
spec:
  refreshInterval: 15m
  secretStoreRef: { name: vault-backend, kind: ClusterSecretStore }
  target: { name: api-db }
  data:
    - secretKey: password
      remoteRef: { key: prod/rds, property: password }
```

For Ansible, run a Vault Agent sidecar that renders secrets into `/etc/app/db.env` and have a systemd unit source it; the playbook installs the agent, never the secret. Cross-reference: `cicd-devsecops` covers Vault PKI, dynamic secrets, key rotation, and encryption-at-rest. This skill only handles the IaC entry point.

## IaC Repository Layout

```text
infra/
  modules/{vpc,rds,ecs}/
  envs/
    dev/{main.tf,terraform.tfvars}
    staging/
    prod/
  ansible/{roles,playbooks,inventories}/
```

- `main` mirrors prod — a merge to `main` is a production change.
- Feature branches target `main` via PR; CI runs `fmt`, `validate`, `plan` on every PR and posts the plan as a PR comment.
- `terraform apply` against prod runs only from `main` after PR approval, through a protected workflow with manual approval.
- Dev and staging apply automatically on merge so feedback cycles stay short.

## Companion Skills

- `cloud-architecture` — AWS services Terraform modules target.
- `kubernetes-platform` — K8s cluster Terraform often provisions and where GitOps reconciles.
- `cicd-pipelines`, `cicd-pipeline-design` — pipelines that run `terraform plan`/`apply`.
- `cicd-devsecops` — Vault depth, secret scanning, SBOM, IaC linting (`tflint`, `tfsec`, `checkov`).
- `linux-security-hardening` — Ansible roles that harden the OS baseline.

## Sources

- Terraform documentation — `developer.hashicorp.com/terraform`.
- Terraform S3 backend — `developer.hashicorp.com/terraform/language/backend/s3`.
- Terraform GCS backend — `developer.hashicorp.com/terraform/language/backend/gcs`.
- Terraform Registry publishing — `developer.hashicorp.com/terraform/registry/modules/publish`.
- Ansible playbook intro — `docs.ansible.com/ansible/latest/playbook_guide/playbooks_intro.html`.
- Ansible roles — `docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html`.
- ArgoCD — `argo-cd.readthedocs.io/en/stable/`.
- ArgoCD auto-sync — `argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/`.
- Flux concepts — `fluxcd.io/flux/concepts/`.
- Terratest — `terratest.gruntwork.io`.
