# Terraform Modules and State — Deep Reference

## Module skeleton

```text
modules/network/
  main.tf          # resources
  variables.tf     # typed, documented inputs (defaults only when safe)
  outputs.tf       # exported values consumers depend on
  versions.tf      # required_providers, required_version
  README.md        # usage example, input/output table
```

```hcl
# modules/network/variables.tf
variable "name" {
  type        = string
  description = "Project slug used in resource names."
}
variable "cidr" {
  type        = string
  description = "Top-level VPC CIDR."
}
variable "azs" {
  type        = list(string)
  description = "Availability zones."
}

# modules/network/outputs.tf
output "vpc_id"             { value = aws_vpc.this.id }
output "private_subnet_ids" { value = aws_subnet.private[*].id }
```

## Versioning and registry conventions

- Tag modules in Git with semver tags (`v1.2.0`).
- Consumers reference an exact tag — `main` can break on any push.
- Public modules consumed via the Terraform Registry use `source = "namespace/name/provider"` and `version = "x.y.z"`.
- Registry naming convention: `terraform-<PROVIDER>-<NAME>` for module repositories (e.g. `terraform-aws-vpc`).

```hcl
module "vpc" {
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

## Composability rule of thumb

A module should do one thing — a network, a database, a service. Avoid the "everything module" — it forces consumers to accept defaults they cannot opt out of and turns every change into a blast-radius event.

## State management commands

```bash
terraform state list                      # all addresses in current state
terraform state show <addr>               # attributes of one resource
terraform state rm <addr>                 # untrack without destroying
terraform import <addr> <provider-id>     # bring existing infra under management
```

## Importing existing infrastructure

```bash
# Bring an existing AWS S3 bucket under Terraform management
terraform import aws_s3_bucket.assets acme-prod-assets
# Then write the resource block to match — terraform plan should show no diff
```

## Splitting state

Separate state files per blast-radius boundary:

- `network/` — VPCs, subnets, IGW, NAT, peering, DNS zones
- `data/` — RDS, ElastiCache, S3 lifecycle policies
- `app/` — ECS, Lambda, ALB rules, scaling

Cross-reference outputs via the `terraform_remote_state` data source:

```hcl
data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "acme-tfstate-prod"
    key    = "platform/network/terraform.tfstate"
    region = "eu-west-1"
  }
}

resource "aws_db_subnet_group" "this" {
  subnet_ids = data.terraform_remote_state.network.outputs.private_subnet_ids
}
```

## Backend choice

| Backend | When | Locking |
|---|---|---|
| S3 + `use_lockfile = true` | AWS-hosted, current best practice | Native S3 conditional writes |
| S3 + `dynamodb_table` | Legacy; existing configs | DynamoDB partition key `LockID` (string) |
| GCS | GCP-hosted projects | Native object generation locking |
| Terraform Cloud / Enterprise | Hosted, team workflows | Built in |

DynamoDB-based locking is deprecated; new configurations should use `use_lockfile = true`. Existing configurations may run both arguments during the transition, then drop the DynamoDB table.

## Common backend trap

Never commit `terraform.tfstate` to Git — it stores secrets in plaintext and creates merge-conflict disasters. Treat the state backend as a sensitive store: encrypt at rest, restrict IAM/ACL access, enable bucket versioning so a corrupted state can be rolled back.
