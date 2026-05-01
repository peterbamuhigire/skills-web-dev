# Common AWS Terraform Patterns

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

## Terratest behavioural test

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

Gate every CI pipeline on three checks before `apply`: `terraform fmt -check -recursive`, `terraform validate`, and `terraform plan -out=plan.tfplan` reviewed by a human or policy tool (`conftest`, `checkov`, `tfsec`).
