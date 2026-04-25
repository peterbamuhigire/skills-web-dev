---
name: infrastructure-as-code
description: Use when provisioning or changing cloud infrastructure with Terraform or Ansible
  — modules, remote state with S3+DynamoDB locking, workspaces, common AWS patterns, idempotent
  Ansible roles, GitOps with ArgoCD/Flux, drift detection, and Vault secret injection.
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

- Use when provisioning or changing cloud infrastructure with Terraform or Ansible — modules, remote state with S3+DynamoDB locking, workspaces, common AWS patterns, idempotent Ansible roles, GitOps with ArgoCD/Flux, drift detection, and Vault secret injection.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `infrastructure-as-code` or would be better handled by a more specific companion skill.
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

## Why IaC

Snowflake servers — hand-configured, undocumented, irreplaceable — cause outages nobody can recover from. IaC puts environments in version-controlled code, making drift a diffable artifact.

| Concern | Terraform | Ansible |
|---|---|---|
| Primary job | Provision cloud resources (VPC, EC2, RDS, IAM) | Configure OS and apps inside those resources |
| Model | Declarative, stateful (`.tfstate`) | Procedural tasks, stateless |
| Idempotency | Built in via resource graph | Per-task, author's responsibility |

Use both: Terraform creates the EC2 instance and emits its IP into an Ansible inventory; Ansible installs Nginx, users, firewall rules.

## Terraform Fundamentals

Pin provider and Terraform versions — a minor provider bump can silently change resource behaviour.

```hcl
# main.tf
terraform {
  required_version = ">= 1.6.0"
  required_providers { aws = { source = "hashicorp/aws", version = "~> 5.40" } }
}
provider "aws" { region = var.region }
data "aws_availability_zones" "available" { state = "available" }
locals { common_tags = { Project = var.project, Environment = terraform.workspace } }
resource "aws_s3_bucket" "app" {
  bucket = "${var.project}-${terraform.workspace}-app"
  tags   = local.common_tags
}
output "app_bucket_name" { value = aws_s3_bucket.app.id }
# variables.tf
variable "region"  { type = string; default = "eu-west-1" }
variable "project" {
  type = string; description = "Project slug used in resource names"
  validation {
    condition     = can(regex("^[a-z0-9-]{3,20}$", var.project))
    error_message = "project must be 3-20 chars, lowercase, digits, or hyphens."
  }
}
```

## State Management

Never commit `terraform.tfstate` to Git — it contains secrets in plaintext and creates merge-conflict disasters. Use a remote backend with locking. The DynamoDB table needs a single string partition key named `LockID`; create it once per org. State commands: `terraform state list`, `terraform state show <addr>`, `terraform import <addr> <id>`, `terraform state rm <addr>`.

```hcl
terraform {
  backend "s3" {
    bucket = "acme-tfstate-prod"
    key    = "platform/network/terraform.tfstate"
    region = "eu-west-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
    kms_key_id     = "alias/terraform-state"
  }
}
```

## Modules

A module is a directory of `.tf` files consumed via `module "name" { source = "..." }`. Pin to an exact Git tag — `main` can break you on any push.

```hcl
module "vpc" {
  source = "git::https://github.com/acme/tf-modules.git//modules/vpc?ref=v1.2.0"
  name = "acme-prod"; cidr = "10.20.0.0/16"; azs = ["eu-west-1a", "eu-west-1b"]
}
# modules/vpc/variables.tf
variable "name" { type = string }
variable "cidr" { type = string }
variable "azs"  { type = list(string) }
# modules/vpc/outputs.tf
output "vpc_id" { value = aws_vpc.this.id }
output "private_subnet_ids" { value = aws_subnet.private[*].id }
```

## Workspaces

Workspaces separate state files per environment while sharing code. Treat `terraform.workspace` as the environment name. Layout: `infra/{main.tf, dev.tfvars, staging.tfvars, prod.tfvars}`.

```bash
terraform workspace new prod && terraform workspace select prod
terraform apply -var-file="prod.tfvars"
```

```hcl
locals { instance_size = { dev = "t3.micro", staging = "t3.small", prod = "m6i.large" }[terraform.workspace] }
```

For stricter isolation (prod in a separate AWS account), prefer one directory per environment instead of workspaces.

## Common Patterns

VPC with public and private subnets across 2 AZs, NAT and IGW; ECS service behind an ALB; RDS MySQL 8 with parameter group; S3 bucket with versioning and GLACIER lifecycle.

```hcl
# VPC
resource "aws_vpc" "this" { cidr_block = var.cidr; enable_dns_hostnames = true; tags = { Name = var.name } }
resource "aws_internet_gateway" "this" { vpc_id = aws_vpc.this.id }
resource "aws_subnet" "public" {
  count = length(var.azs); vpc_id = aws_vpc.this.id
  cidr_block = cidrsubnet(var.cidr, 8, count.index)
  availability_zone = var.azs[count.index]; map_public_ip_on_launch = true
}
resource "aws_subnet" "private" {
  count = length(var.azs); vpc_id = aws_vpc.this.id
  cidr_block = cidrsubnet(var.cidr, 8, count.index + 10)
  availability_zone = var.azs[count.index]
}
resource "aws_eip" "nat" { count = length(var.azs); domain = "vpc" }
resource "aws_nat_gateway" "this" {
  count = length(var.azs)
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
}
# ECS service behind an ALB
resource "aws_ecs_cluster" "this" { name = "${var.name}-cluster" }
resource "aws_ecs_task_definition" "api" {
  family = "${var.name}-api"; network_mode = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu = "512"; memory = "1024"; execution_role_arn = aws_iam_role.ecs_exec.arn
  container_definitions = jsonencode([{
    name = "api", image = "${var.image_uri}:${var.image_tag}",
    portMappings = [{ containerPort = 8080, protocol = "tcp" }]
  }])
}
resource "aws_lb_target_group" "api" {
  name = "${var.name}-tg"; port = 8080; protocol = "HTTP"
  target_type = "ip"; vpc_id = var.vpc_id
  health_check { path = "/healthz"; healthy_threshold = 2; unhealthy_threshold = 3 }
}
resource "aws_ecs_service" "api" {
  name = "${var.name}-api"; cluster = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count = 2; launch_type = "FARGATE"
  network_configuration { subnets = var.private_subnet_ids; security_groups = [aws_security_group.api.id] }
  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name = "api"; container_port = 8080
  }
}
# RDS MySQL 8 with parameter group
resource "aws_db_parameter_group" "mysql8" {
  name = "${var.name}-mysql8"; family = "mysql8.0"
  parameter { name = "slow_query_log";  value = "1" }
  parameter { name = "long_query_time"; value = "1" }
}
resource "aws_db_instance" "primary" {
  identifier = "${var.name}-db"
  engine = "mysql"; engine_version = "8.0"
  instance_class = "db.t3.micro"; allocated_storage = 20; storage_encrypted = true
  parameter_group_name = aws_db_parameter_group.mysql8.name
  username = var.db_username; password = var.db_password
  skip_final_snapshot = var.environment == "prod" ? false : true
  deletion_protection = var.environment == "prod"
  backup_retention_period = var.environment == "prod" ? 14 : 1
}
# S3 bucket with versioning and GLACIER lifecycle
resource "aws_s3_bucket" "archive" { bucket = "${var.name}-archive" }
resource "aws_s3_bucket_versioning" "archive" {
  bucket = aws_s3_bucket.archive.id
  versioning_configuration { status = "Enabled" }
}
resource "aws_s3_bucket_lifecycle_configuration" "archive" {
  bucket = aws_s3_bucket.archive.id
  rule {
    id = "transition-to-glacier"; status = "Enabled"
    transition { days = 30; storage_class = "GLACIER" }
    noncurrent_version_expiration { noncurrent_days = 90 }
  }
}
```

## Terraform Testing

Gate every CI pipeline on three checks before `apply`: `terraform fmt -check -recursive` (unformatted files fail), `terraform validate` (syntax/undefined vars), and `terraform plan -out=plan.tfplan` reviewed by a human or policy tool (`conftest`, `checkov`). Terratest for behavioural tests:

```go
func TestS3Bucket(t *testing.T) {
    opts := &terraform.Options{TerraformDir: "../examples/s3", Vars: map[string]interface{}{"name": "terratest-example"}}
    defer terraform.Destroy(t, opts)
    terraform.InitAndApply(t, opts)
    bucket := terraform.Output(t, opts, "app_bucket_name")
    aws.AssertS3BucketExists(t, "eu-west-1", bucket)
    assert.Contains(t, bucket, "terratest-example")
}
```

## Ansible Fundamentals

Static inventory, dynamic AWS inventory, and a minimum Nginx playbook:

```ini
# inventories/prod/hosts.ini
[web]
web-01 ansible_host=10.20.1.10
[web:vars]
ansible_user=ubuntu
ansible_ssh_private_key_file=~/.ssh/prod.pem
```

```yaml
# inventories/prod/aws_ec2.yml
plugin: amazon.aws.aws_ec2
regions: [eu-west-1]
filters: { tag:Environment: prod }
keyed_groups: [{ key: tags.Role, prefix: role }]
---
- hosts: web
  become: true
  tasks:
    - ansible.builtin.apt: { name: nginx, state: present, update_cache: true, cache_valid_time: 3600 }
    - ansible.builtin.template: { src: nginx-site.conf.j2, dest: /etc/nginx/sites-available/app.conf }
      notify: reload nginx
  handlers:
    - name: reload nginx
      ansible.builtin.systemd: { name: nginx, state: reloaded }
```

Variable precedence (most-specific wins): `-e` > task > block > role > play > host > group > role defaults.

## Ansible Roles

Roles give a conventional folder (`tasks/`, `handlers/`, `defaults/`, `templates/`, `vars/`, `meta/`) so playbooks stay short. Install community content (`ansible-galaxy install geerlingguy.nginx`, `ansible-galaxy collection install amazon.aws community.general`). Declare dependencies in `meta/main.yml`:

```yaml
dependencies:
  - role: geerlingguy.security
    vars: { security_ssh_permit_root_login: "no" }
  - role: geerlingguy.firewall
```

## Idempotency

Running the playbook ten times should leave the system identical to running it once. Ansible modules are idempotent by default; raw shell commands are not.

```yaml
# BAD — always reports changed
- ansible.builtin.shell: mkdir -p /var/cache/app
# GOOD — declarative, idempotent
- ansible.builtin.file: { path: /var/cache/app, state: directory, owner: app, mode: "0750" }
# Command with explicit change status
- ansible.builtin.command: nginx -t
  register: nginx_check
  changed_when: false
  failed_when: "'syntax is ok' not in nginx_check.stderr"
```

Dry-run before prod: `ansible-playbook -i inventories/prod site.yml --check --diff`.

## Ansible for Server Config

Baseline Ubuntu hardening and Nginx install:

```yaml
- hosts: web
  become: true
  tasks:
    - ansible.builtin.apt: { name: [nginx, ufw, fail2ban, unattended-upgrades], state: latest, update_cache: true, cache_valid_time: 3600 }
    - ansible.builtin.user: { name: deploy, groups: sudo, shell: /bin/bash }
    - ansible.posix.authorized_key: { user: deploy, key: "{{ lookup('file', 'files/deploy.pub') }}" }
    - community.general.ufw: { rule: allow, port: "{{ item }}", proto: tcp }
      loop: [22, 443]
    - community.general.ufw: { state: enabled, policy: deny }
    - ansible.builtin.systemd: { name: nginx, state: started, enabled: true }
```

## GitOps with ArgoCD

The Git repo is the single source of truth; a controller reconciles the live cluster to match. ArgoCD ships a web UI and a CRD-driven controller. Multi-cluster via `ApplicationSet`.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata: { name: api, namespace: argocd }
spec:
  project: platform
  source: { repoURL: https://github.com/acme/k8s-manifests.git, targetRevision: main, path: apps/api/overlays/prod }
  destination: { server: https://kubernetes.default.svc, namespace: api-prod }
  syncPolicy: { automated: { prune: true, selfHeal: true }, syncOptions: [CreateNamespace=true] }
---
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata: { name: api-per-cluster, namespace: argocd }
spec:
  generators: [{ clusters: { selector: { matchLabels: { env: prod } } } }]
  template:
    metadata: { name: 'api-{{name}}' }
    spec:
      project: platform
      source: { repoURL: https://github.com/acme/k8s-manifests.git, path: 'apps/api/overlays/{{name}}', targetRevision: main }
      destination: { server: '{{server}}', namespace: api }
      syncPolicy: { automated: { prune: true, selfHeal: true } }
```

## Flux as Alternative

Flux v2 is headless — no UI, every action is a Kubernetes resource. Bootstrap: `flux bootstrap github --owner=acme --repository=fleet-infra --branch=main --path=clusters/prod --personal`.

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata: { name: app-manifests, namespace: flux-system }
spec: { interval: 1m, url: https://github.com/acme/k8s-manifests, ref: { branch: main } }
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata: { name: api-prod, namespace: flux-system }
spec:
  interval: 5m
  path: ./apps/api/overlays/prod
  prune: true
  targetNamespace: api-prod
  sourceRef: { kind: GitRepository, name: app-manifests }
---
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata: { name: ingress-nginx, namespace: ingress }
spec:
  interval: 10m
  chart:
    spec: { chart: ingress-nginx, version: "4.10.x", sourceRef: { kind: HelmRepository, name: ingress-nginx, namespace: flux-system } }
  values: { controller: { replicaCount: 2 } }
```

Pick ArgoCD for UI and per-app RBAC; pick Flux when pipelines are fully headless and GitOps policy lives in code.

## Drift Detection

Drift happens when someone clicks in the console or a pipeline edits a resource Terraform owns. Detect it with scheduled `plan`; ArgoCD detects drift natively and flips `Application` to `OutOfSync`.

```yaml
# .github/workflows/drift.yml
name: drift-detect
on: { schedule: [{ cron: '0 */6 * * *' }] }
jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - run: terraform init
      - run: |
          terraform plan -detailed-exitcode -lock=false || \
            { [ $? -eq 2 ] && echo "::error::drift detected" && exit 1; }
---
# argocd-notifications-cm routes OutOfSync to Slack
data:
  trigger.on-sync-status-unknown: |
    - when: app.status.sync.status == 'OutOfSync'
      send: [slack-out-of-sync]
  template.slack-out-of-sync: { message: "App {{.app.metadata.name}} drifted from Git" }
```

## Secret Injection

Never bake secrets into `.tfvars` or playbook files. Pull them at runtime. Ansible + Vault Agent sidecar: the agent renders Vault secrets into `/etc/app/db.env` and a systemd unit sources it; the playbook installs the agent, never the secret. Kubernetes uses `external-secrets-operator`.

```hcl
provider "vault" { address = "https://vault.acme.internal" }
data "vault_generic_secret" "rds" { path = "secret/data/prod/rds" }
resource "aws_db_instance" "primary" {
  username = data.vault_generic_secret.rds.data["username"]
  password = data.vault_generic_secret.rds.data["password"]
}
```

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata: { name: api-db, namespace: api-prod }
spec:
  refreshInterval: 15m
  secretStoreRef: { name: vault-backend, kind: ClusterSecretStore }
  target: { name: api-db }
  data: [{ secretKey: password, remoteRef: { key: prod/rds, property: password } }]
```

## IaC Repository Structure

Monorepo layout and branching strategy:

```
infra/
  modules/{vpc,rds}/
  environments/
    dev/{main.tf,terraform.tfvars}
    staging/
    prod/
  ansible/{roles,playbooks,inventories}/
```

- `main` mirrors prod. A merge to `main` is a production change.
- Feature branches target `main` via PR; CI runs `fmt`, `validate`, `plan` on every PR and posts the plan as a PR comment.
- `terraform apply` against prod runs only from `main` after PR approval, through a protected workflow with manual approval.
- Dev and staging apply automatically on merge to their directories so feedback cycles stay short.

## Companion Skills

- `cloud-architecture` — AWS services Terraform modules target
- `kubernetes-platform` — K8s cluster Terraform often provisions
- `cicd-pipelines` — GitHub Actions that run `terraform plan`/`apply`
- `cicd-devsecops` — secret scanning, SBOM, IaC linting (`tflint`, `tfsec`)
- `linux-security-hardening` — Ansible roles that harden the OS

## Sources

- *Terraform: Up & Running* (3rd ed.) — Yevgeniy Brikman (O'Reilly)
- *Infrastructure as Code* (2nd ed.) — Kief Morris (O'Reilly)
- Terraform documentation — `developer.hashicorp.com/terraform/docs`
- Ansible documentation — `docs.ansible.com/ansible/latest`
- ArgoCD documentation — `argo-cd.readthedocs.io`
- Flux documentation — `fluxcd.io/flux`
- Terratest — `terratest.gruntwork.io`