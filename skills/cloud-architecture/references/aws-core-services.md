# AWS Core Services — CLI Reference

Service-by-service commands and patterns for EC2, S3, RDS, IAM, ALB, ASG, CloudFront, and CloudWatch. Use named profiles (`--profile prod`) per environment. OIDC or SSO preferred over long-lived keys.

## Global Setup

```bash
aws configure sso --profile prod
aws configure sso --profile staging
aws sts get-caller-identity --profile prod
```

Put a `.aws/config` snippet per environment and export `AWS_PROFILE` in your shell.

## EC2

### Launch with Instance Profile

```bash
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type m7i.large \
  --subnet-id subnet-0aaa \
  --security-group-ids sg-0bbb \
  --iam-instance-profile Name=app-instance-profile \
  --user-data file://bootstrap.sh \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=app-prod-web-01},{Key=Environment,Value=prod}]' \
  --block-device-mappings '[{"DeviceName":"/dev/xvda","Ebs":{"VolumeSize":30,"VolumeType":"gp3","Encrypted":true}}]'
```

### AMI Hygiene

- Build AMIs with Packer from a pinned base (Ubuntu 22.04 LTS or Debian 12).
- Store AMI IDs in SSM Parameter Store — never hard-code them.
- Rotate AMIs monthly for security patches; deploy via ASG refresh.

### Instance Family Cheat Sheet

| Family | When |
|--------|------|
| `t4g`, `t3a` | Burstable workloads, dev/staging, low-traffic prod |
| `m7i`, `m6g` | General-purpose, balanced CPU/memory |
| `c7i`, `c6g` | CPU-bound (encoding, compile, ML inference) |
| `r7i`, `r6g` | Memory-heavy (caches, in-memory DB) |
| `i4i`, `im4gn` | NVMe-heavy (local SSD) |

## S3

### Create Secure Bucket

```bash
aws s3api create-bucket \
  --bucket app-prod-user-uploads \
  --region eu-west-1 \
  --create-bucket-configuration LocationConstraint=eu-west-1

aws s3api put-public-access-block \
  --bucket app-prod-user-uploads \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

aws s3api put-bucket-encryption \
  --bucket app-prod-user-uploads \
  --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

aws s3api put-bucket-versioning \
  --bucket app-prod-user-uploads \
  --versioning-configuration Status=Enabled
```

### Lifecycle Rule (transition + expiry)

```json
{
  "Rules": [
    {
      "ID": "archive-cold-uploads",
      "Status": "Enabled",
      "Filter": { "Prefix": "uploads/" },
      "Transitions": [
        { "Days": 30,  "StorageClass": "STANDARD_IA" },
        { "Days": 90,  "StorageClass": "GLACIER_IR" },
        { "Days": 365, "StorageClass": "DEEP_ARCHIVE" }
      ]
    }
  ]
}
```

### Presigned URLs

Never hand bucket credentials to browser clients. Issue short-lived presigned URLs (5–15 minutes) from the server.

## RDS

### Create Multi-AZ Postgres

```bash
aws rds create-db-instance \
  --db-instance-identifier app-prod-pg \
  --db-instance-class db.m7g.large \
  --engine postgres \
  --engine-version 16.4 \
  --master-username appadmin \
  --master-user-password "$(aws secretsmanager get-secret-value --secret-id rds/app-prod/master --query SecretString --output text)" \
  --allocated-storage 100 --storage-type gp3 --storage-encrypted \
  --multi-az \
  --backup-retention-period 14 \
  --preferred-backup-window "02:00-03:00" \
  --preferred-maintenance-window "sun:03:00-sun:04:00" \
  --enable-performance-insights \
  --monitoring-interval 60 \
  --deletion-protection
```

### Read Replica

```bash
aws rds create-db-instance-read-replica \
  --db-instance-identifier app-prod-pg-ro-1 \
  --source-db-instance-identifier app-prod-pg \
  --db-instance-class db.m7g.large
```

### Rules

- Always Multi-AZ for production.
- Backup retention at minimum 14 days, 35 for regulated workloads.
- Rotate master credentials through Secrets Manager with scheduled Lambda.
- Do not disable `deletion-protection` to shortcut operations — use a separate maintenance account.

## IAM

### Least-Privilege Instance Profile Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadConfig",
      "Effect": "Allow",
      "Action": ["ssm:GetParameter", "ssm:GetParameters"],
      "Resource": "arn:aws:ssm:eu-west-1:123456789012:parameter/app/prod/*"
    },
    {
      "Sid": "ReadSecrets",
      "Effect": "Allow",
      "Action": ["secretsmanager:GetSecretValue"],
      "Resource": "arn:aws:secretsmanager:eu-west-1:123456789012:secret:app/prod/*"
    },
    {
      "Sid": "PutLogs",
      "Effect": "Allow",
      "Action": ["logs:CreateLogStream", "logs:PutLogEvents"],
      "Resource": "arn:aws:logs:eu-west-1:123456789012:log-group:/app/prod/*"
    }
  ]
}
```

### GitHub Actions OIDC Role (trust policy)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com" },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": { "token.actions.githubusercontent.com:aud": "sts.amazonaws.com" },
        "StringLike":   { "token.actions.githubusercontent.com:sub": "repo:my-org/my-repo:ref:refs/heads/main" }
      }
    }
  ]
}
```

## ALB, ASG, Target Group

### Target Group with Health Check

```bash
aws elbv2 create-target-group \
  --name app-prod-web-tg \
  --protocol HTTP --port 3000 \
  --vpc-id vpc-0123 \
  --target-type instance \
  --health-check-path /healthz \
  --health-check-interval-seconds 15 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 2 \
  --matcher HttpCode=200
```

### Auto-Scaling Group

```bash
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name app-prod-web-asg \
  --launch-template "LaunchTemplateName=app-prod-web-lt,Version=\$Latest" \
  --min-size 2 --max-size 10 --desired-capacity 2 \
  --vpc-zone-identifier "subnet-0aaa,subnet-0bbb" \
  --target-group-arns arn:aws:elasticloadbalancing:eu-west-1:123456789012:targetgroup/app-prod-web-tg/abc \
  --health-check-type ELB --health-check-grace-period 90
```

### Target-Tracking Policy (request count per target)

```bash
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name app-prod-web-asg \
  --policy-name tt-rpt \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration '{
    "TargetValue": 800,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ALBRequestCountPerTarget",
      "ResourceLabel": "app/app-prod-alb/abc/targetgroup/app-prod-web-tg/def"
    }
  }'
```

## CloudFront

- Use CloudFront in front of S3 static buckets with OAC (Origin Access Control), not public buckets.
- Use CloudFront in front of ALB for API cache + DDoS absorption.
- Signed URLs or cookies for private content.
- Invalidate narrow paths, not `/*` — repeated wide invalidations cost money and raise origin load.

```bash
aws cloudfront create-invalidation \
  --distribution-id E1ABCDEF \
  --paths "/static/css/*" "/static/js/*"
```

## CloudWatch, Logs, Alarms

- One log group per service (`/app/prod/web`, `/app/prod/worker`).
- Retention set explicitly (14, 30, 90, 365, 400 days) — never leave default "never expire".
- Metric alarms on error rate, latency p95, 5xx %, queue depth, and cost anomaly.

```bash
aws logs put-retention-policy --log-group-name /app/prod/web --retention-in-days 90

aws cloudwatch put-metric-alarm \
  --alarm-name app-prod-web-5xx-high \
  --metric-name HTTPCode_Target_5XX_Count \
  --namespace AWS/ApplicationELB \
  --statistic Sum --period 60 --threshold 10 --evaluation-periods 3 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:eu-west-1:123456789012:prod-alerts
```

## Cost Guardrails

```bash
aws budgets create-budget --account-id 123456789012 --budget '{
  "BudgetName":"prod-monthly",
  "BudgetLimit":{"Amount":"2000","Unit":"USD"},
  "TimeUnit":"MONTHLY",
  "BudgetType":"COST"
}'
```

Set Cost Anomaly Detection on every production account. Tag every resource with `Environment`, `Service`, `Owner`, `CostCenter`.
