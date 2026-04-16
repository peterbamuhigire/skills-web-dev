---
name: cloud-architecture
description: Use when designing cloud deployments, Dockerising applications, laying
  out AWS or GCP environments, choosing a deployment pattern, or moving a workload
  from a single VM to a resilient multi-AZ topology.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Cloud Architecture

<!-- dual-compat-start -->
## Use When

- Use when designing cloud deployments, Dockerising applications, laying out AWS or GCP environments, choosing a deployment pattern, or moving a workload from a single VM to a resilient multi-AZ topology.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `cloud-architecture` or would be better handled by a more specific companion skill.
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

## Load Order

1. Load `world-class-engineering` for the production bar.
2. Load `system-architecture-design` for decomposition and contracts.
3. Load this skill for the cloud runtime shape.
4. Pair with `cicd-pipelines` for delivery, `cicd-devsecops` for gate policy, `observability-monitoring` for telemetry, `deployment-release-engineering` for rollout, and `reliability-engineering` for failure design.

## Executable Outputs

For meaningful cloud architecture work produce: workload classification (stateless, stateful, async, batch, scheduled), chosen compute model with rationale, VPC + subnet + routing layout across AZs, Dockerfile (multi-stage, pinned base), `docker-compose.yml` mirroring production, IAM role inventory with least-privilege policies, deployment pattern choice and rollback runbook, cost posture (reserved/on-demand/spot split, Savings Plan assessment), and CDN/TLS/WAF/auto-scaling configuration.

## Cloud Provider Selection

East African SaaS workloads (Uganda, Kenya, Tanzania) weigh four dimensions: latency to users, data-residency obligations under Uganda DPPA 2019, support hours overlapping EAT (UTC+3), and price-per-workload.

| Dimension | AWS | GCP | Azure |
|-----------|-----|-----|-------|
| Closest region | `af-south-1` Cape Town (~30 ms) | `europe-west1` (~160 ms) | `southafricanorth` (~40 ms) |
| Data-residency fit | Strong (af-south-1 + KMS) | Weak (no ZA region for many services) | Strong (ZA North + Customer Lockbox) |
| Support in EAT | 24/7 Business; EMEA TAM overlap | 24/7 Standard | 24/7 ProDirect; ZA partners |
| Managed services breadth | Widest | Data/ML led | Microsoft-stack integration |

Default to AWS `af-south-1` for Uganda workloads with S-tier DPPA 2019 data; use Azure `southafricanorth` only for .NET-heavy stacks with an existing EA licence; avoid GCP as primary for DPPA-scoped data until a ZA region is GA.

```bash
aws configure set region af-south-1 --profile ug-prod
aws ec2 describe-availability-zones --region af-south-1 --query "AvailabilityZones[].ZoneName"
```

## Compute Model Decision Rules

1. Single app, low traffic, one region → EC2 + Docker Compose, backed by RDS Multi-AZ and S3.
2. Multiple services, scaling needs, no Kubernetes skill → ECS Fargate with ALB.
3. Multiple services, platform-ready team, polyglot runtime, multi-tenant isolation → Kubernetes (defer to `kubernetes-platform`).
4. Async fan-out, batch, or event pipeline → Lambda + SQS + EventBridge, with state in DynamoDB or RDS.

Kubernetes is a commitment, not a default.

## Docker Fundamentals

Images are immutable, content-addressed layers. Containers are processes isolated by namespaces and cgroups. Disciplined Dockerfile authorship controls image size, cache behaviour, and attack surface.

### Dockerfile Checklist

- Multi-stage: compile/install in `builder`, copy only runtime artifacts to the final stage.
- Pin base images by version and digest (`node:22.11.0-slim@sha256:...`).
- Prefer distroless or `alpine` for runtime; target image ≤ 200 MB.
- Run as non-root (`USER nonroot` or dedicated UID ≥ 10000). Set `WORKDIR`, `EXPOSE`, `HEALTHCHECK` explicitly.
- Secrets via mounted files or orchestrator env — never baked in. `.dockerignore` excludes `.git`, `node_modules`, logs, fixtures, editor config.
- Order `COPY` from least-changing (manifests) to most-changing (source) to preserve layer caching.

### Production Node.js Dockerfile

```dockerfile
# syntax=docker/dockerfile:1.7
FROM node:22.11.0-slim@sha256:<digest> AS builder
WORKDIR /app
COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm npm ci --include=dev
COPY . .
RUN npm run build && npm prune --omit=dev

FROM gcr.io/distroless/nodejs22-debian12:nonroot AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder --chown=nonroot:nonroot /app/node_modules ./node_modules
COPY --from=builder --chown=nonroot:nonroot /app/dist ./dist
COPY --from=builder --chown=nonroot:nonroot /app/package.json ./
USER nonroot
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD ["node", "dist/healthcheck.js"]
CMD ["dist/server.js"]
```

## Docker Compose

One `docker-compose.yml` in the repo root mirrors production. Named volumes for stateful services; never bind-mount databases. Declare `healthcheck` on every dependency and gate startup with `depends_on.condition: service_healthy`.

```yaml
name: saas-local
services:
  web:
    build: .
    env_file: .env
    ports: ["3000:3000"]
    depends_on:
      db: { condition: service_healthy }
      redis: { condition: service_healthy }
    healthcheck:
      test: ["CMD", "node", "dist/healthcheck.js"]
      interval: 30s
      timeout: 5s
      retries: 3
  db:
    image: postgres:16.4-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
      POSTGRES_DB: app
    volumes: ["db-data:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 10s
      timeout: 3s
      retries: 5
    secrets: [db_password]
  redis:
    image: redis:7.4-alpine
    command: ["redis-server", "--appendonly", "yes"]
    volumes: ["redis-data:/data"]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
volumes:
  db-data: {}
  redis-data: {}
secrets:
  db_password: { file: ./.secrets/db_password }
```

Commit `.env.example`, ignore `.env`, and provide env through the orchestrator in production. See `references/docker-compose-patterns.md` for the full template.

## AWS Core Services

### Compute

Instance families: `t3`/`t4g` burstable (dev, low-traffic), `m6i`/`m7i` balanced production, `c6i`/`c7i` CPU-bound, `r6i`/`r7i` memory-bound, `i4i` NVMe-heavy. Place production instances in private subnets; expose only via ALB/NLB. Build AMIs with Packer or EC2 Image Builder; no manual console edits.

```yaml
LaunchTemplate:
  Type: AWS::EC2::LaunchTemplate
  Properties:
    LaunchTemplateName: app-prod-lt
    LaunchTemplateData:
      ImageId: ami-0123456789abcdef0
      InstanceType: m6i.large
      IamInstanceProfile: { Name: app-prod-instance-profile }
      SecurityGroupIds: [sg-app]
      MetadataOptions: { HttpTokens: required, HttpEndpoint: enabled }
AppASG:
  Type: AWS::AutoScaling::AutoScalingGroup
  Properties:
    MinSize: 2
    MaxSize: 10
    DesiredCapacity: 3
    HealthCheckType: ELB
    HealthCheckGracePeriod: 120
    VPCZoneIdentifier: [subnet-priv-a, subnet-priv-b, subnet-priv-c]
    LaunchTemplate:
      LaunchTemplateId: !Ref LaunchTemplate
      Version: !GetAtt LaunchTemplate.LatestVersionNumber
    TargetGroupARNs: [!Ref AppTargetGroup]
```

### Storage

Enable default encryption, block public access, and turn on versioning for any data you cannot reconstruct. Lifecycle: transition > 30 days to Standard-IA, > 90 days to Glacier Instant Retrieval, expire multipart uploads > 7 days. Use presigned URLs for customer uploads/downloads; never hand out credentials. Multipart upload threshold ≥ 100 MB; part size 8–16 MB.

```bash
aws s3 presign s3://app-prod-uploads/customer/42/invoice.pdf \
  --expires-in 900 --region af-south-1

aws configure set default.s3.multipart_threshold 100MB
aws configure set default.s3.multipart_chunksize 16MB
```

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyInsecureTransport",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": ["arn:aws:s3:::app-prod-uploads", "arn:aws:s3:::app-prod-uploads/*"],
      "Condition": { "Bool": { "aws:SecureTransport": "false" } }
    }
  ]
}
```

### Database

Multi-AZ for every production RDS MySQL/PostgreSQL; synchronous standby in a second AZ. Automated backups retention 7–35 days with PITR. Read replicas for read-heavy paths, never for durability. Parameter groups hold tunings; never edit defaults in place.

```bash
aws rds create-db-parameter-group --db-parameter-group-name app-pg16-prod \
  --db-parameter-group-family postgres16 --description "Prod PG16 params"
aws rds create-db-instance --db-instance-identifier app-prod \
  --engine postgres --engine-version 16.4 --db-instance-class db.m6i.large \
  --allocated-storage 200 --storage-type gp3 --storage-encrypted \
  --multi-az --backup-retention-period 14 --db-parameter-group-name app-pg16-prod \
  --monitoring-interval 60 --enable-performance-insights
```

### Serverless

Lambda triggers: S3 object-created, SQS queue, API Gateway, EventBridge schedule, DynamoDB Streams. Cold-start mitigation: provisioned concurrency for latency-sensitive paths; a 5-minute EventBridge keep-warm rule as a low-cost fallback. Keep deployment package ≤ 50 MB zipped; container images only when native deps demand it.

```bash
aws lambda put-provisioned-concurrency-config \
  --function-name order-api --qualifier live \
  --provisioned-concurrent-executions 5
```

### IAM

Roles, not users, for workloads — instance profiles on EC2, task roles on ECS. Policy statements scoped to specific ARNs and actions — no `*:*`. CI uses OIDC federation to assume role; no long-lived keys. MFA on every human account; root locked away with hardware MFA.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AppReadUploads",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::app-prod-uploads/*"
    },
    {
      "Sid": "AppReadSecrets",
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "arn:aws:secretsmanager:af-south-1:111122223333:secret:app/prod/*"
    }
  ]
}
```

## Networking

Design the VPC across ≥ 3 AZs for production, 2 for non-production. Allocate a /16 and carve /20 public and /20 private subnets per AZ. One NAT gateway per AZ in production — single-AZ NAT is a SPOF and cross-AZ data charges bite.

| Layer | CIDR example | Routing |
|-------|--------------|---------|
| Public subnets | 10.20.0.0/20 per AZ | IGW default route |
| Private app subnets | 10.20.32.0/20 per AZ | NAT gateway in same AZ |
| Private data subnets | 10.20.64.0/20 per AZ | No outbound route |

Security groups are stateful instance-level allow-lists — the primary tool. NACLs are stateless subnet-level deny/allow lists — use only for coarse boundaries (blocking known-bad CIDRs). Reserve ≥ /18 headroom for peering or Transit Gateway.

```bash
aws ec2 create-vpc --cidr-block 10.20.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=ug-prod-vpc}]'
aws ec2 create-nat-gateway --subnet-id subnet-pub-a --allocation-id eipalloc-aaa
```

## Load Balancers

| Feature | ALB | NLB |
|---------|-----|-----|
| Layer | 7 (HTTP/HTTPS/gRPC) | 4 (TCP/UDP/TLS) |
| Routing | Host, path, header, query | Port-based |
| TLS termination | At ALB | Passthrough or at NLB |
| Sticky sessions | Cookie-based | Source-IP flow hash |
| Use case | Web APIs, microservices | High-throughput TCP, static IPs, PrivateLink |

Health checks hit a dedicated `/healthz` path on a dedicated port when feasible; verify dependencies shallowly — not deeply, or cascading failures evict healthy targets.

```bash
aws elbv2 create-target-group --name app-tg-blue --protocol HTTP --port 3000 \
  --vpc-id vpc-0abc --health-check-path /healthz --health-check-interval-seconds 15 \
  --healthy-threshold-count 2 --unhealthy-threshold-count 3 --matcher HttpCode=200
aws elbv2 create-listener --load-balancer-arn $ALB_ARN --protocol HTTPS --port 443 \
  --certificates CertificateArn=$ACM_ARN \
  --ssl-policy ELBSecurityPolicy-TLS13-1-2-2021-06 \
  --default-actions Type=forward,TargetGroupArn=$TG_BLUE
```

## CDN

CloudFront or Cloudflare in front of every static asset and cacheable API response. Enable Origin Shield in a region close to the origin to cut origin fetches by 60–80%. Attach AWS WAF with the Managed Rules Core Rule Set plus Known Bad Inputs and IP-Reputation lists; add a rate-based rule at 2000 requests per 5 minutes per IP for unauthenticated endpoints.

```bash
aws cloudfront create-distribution --distribution-config file://cf-dist.json
aws wafv2 create-web-acl --name app-prod-waf --scope CLOUDFRONT --default-action Allow={} \
  --visibility-config SampledRequestsEnabled=true,CloudWatchMetricsEnabled=true,MetricName=app-prod-waf \
  --rules file://waf-managed-rules.json
```

Invalidate surgically — never `invalidate /*` on every deploy; use versioned asset paths (`/static/v=<build-sha>/`) and cache-bust only HTML.

## SSL/TLS Automation

- AWS ALB, CloudFront, API Gateway → ACM certificates: free, auto-renewed, DNS-validated via Route 53.
- VPS or single host → Certbot + Let's Encrypt with the installer's systemd timer; nightly cron only when systemd is unavailable.
- Kubernetes → `cert-manager` with a `ClusterIssuer` for Let's Encrypt ACME HTTP-01 or DNS-01.

```bash
aws acm request-certificate --domain-name app.example.co.ug \
  --subject-alternative-names "*.app.example.co.ug" \
  --validation-method DNS --key-algorithm RSA_2048
sudo certbot --nginx -d app.example.co.ug --deploy-hook "systemctl reload nginx"
kubectl apply -f cert-manager/letsencrypt-prod-issuer.yaml
```

TLS 1.2 minimum, prefer 1.3. Enable HSTS `max-age=31536000; includeSubDomains; preload` once the production cert path is stable.

## Auto-Scaling

Target tracking first, step scaling second, predictive third. Scale on request count per target and P95 latency — not CPU alone.

```bash
aws application-autoscaling put-scaling-policy --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount --resource-id service/app-cluster/app-svc \
  --policy-name tt-reqcount --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 1000,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ALBRequestCountPerTarget",
      "ResourceLabel": "app/alb-arn/tg-arn"
    },
    "ScaleOutCooldown": 60, "ScaleInCooldown": 300
  }'
```

- CPU target 70% for CPU-bound services; never below 40% (wastes capacity). Scheduled scaling for predictable load (EAT business hours 07:00–19:00). Predictive scaling requires ≥ 14 days of CloudWatch history and a regular daily/weekly pattern — otherwise predictions are noise. Warm pools for slow-booting AMIs (> 3 min boot).

## Zero-Downtime Deployments

Blue-green via ALB target-group swap for stateful-client apps; ASG instance refresh for stateless fleets. Canary for risky changes (pull weight to zero to rollback); shadow for unproven services receiving mirrored traffic. Automatic rollback triggers on health-check failure, 5xx-rate regression > 0.5% over 5 min, or P95 latency regression beyond SLO budget.

Blue-green procedure: register green with `app-tg-green`, wait for all targets `healthy` via `aws elbv2 describe-target-health`, then swap the listener:

```bash
aws elbv2 modify-listener --listener-arn $LISTENER_ARN \
  --default-actions Type=forward,TargetGroupArn=$TG_GREEN
```

Hold blue for 30 minutes as a hot rollback target; deregister only after error-rate and latency SLOs hold. Rolling update via ASG instance refresh:

```bash
aws autoscaling start-instance-refresh --auto-scaling-group-name app-prod-asg \
  --strategy Rolling --preferences '{
    "MinHealthyPercentage": 90, "InstanceWarmup": 180,
    "CheckpointPercentages": [25, 50, 100], "CheckpointDelay": 600
  }'
```

Rollback: re-point the listener to `app-tg-blue` (blue-green), or `aws autoscaling cancel-instance-refresh` and roll forward with the prior Launch Template version. Schema migrations must be backwards-compatible across two application versions (expand → migrate → contract). Every deploy writes a signed record: who, what, when, artifact digest.

## Backup & Disaster Recovery

Define RTO (how fast to recover) and RPO (how much data loss is tolerable) before picking tools. Typical production SaaS targets RTO ≤ 4 h, RPO ≤ 15 min.

- RDS: automated backups retention 7–35 days with PITR; weekly manual snapshots retained 90 days; cross-region snapshot copy to `eu-west-1` as a sovereignty-preserving DR site.
- S3: versioning on every data bucket; lifecycle moves non-current versions to Glacier Deep Archive after 60 days; Cross-Region Replication for critical buckets.
- EBS: daily snapshots via AWS Backup with a 30-day retention plan.

```bash
aws rds copy-db-snapshot \
  --source-db-snapshot-identifier arn:aws:rds:af-south-1:111122223333:snapshot:app-prod-2026-04-15 \
  --target-db-snapshot-identifier app-prod-2026-04-15-dr \
  --kms-key-id alias/rds-dr --source-region af-south-1 --region eu-west-1
aws s3api put-bucket-versioning --bucket app-prod-uploads --versioning-configuration Status=Enabled
```

Rehearse restore quarterly — an untested backup is a hypothesis, not a backup.

## Cost Optimisation

- Reserved Instances or Savings Plans for steady baseline (70–80% of average compute); on-demand for burst. Prefer Compute Savings Plans (1y no-upfront starting posture; 3y only when headcount and roadmap are certain) — they apply across EC2, Fargate, Lambda.
- Spot for non-critical async workers and CI runners with a graceful shutdown handler for the 2-minute interruption notice.
- S3 Intelligent-Tiering on buckets with unpredictable access; tag every resource with `Environment`, `Team`, `CostCenter`, `Project` and activate these as cost-allocation tags in Billing.
- Cost Explorer, Cost Anomaly Detection, and per-environment budgets on from day one.

```bash
aws ce list-cost-allocation-tags --status Active --region us-east-1
aws budgets create-budget --account-id 111122223333 --budget '{
  "BudgetName": "ug-prod-monthly",
  "BudgetLimit": { "Amount": "5000", "Unit": "USD" },
  "TimeUnit": "MONTHLY", "BudgetType": "COST",
  "CostFilters": { "TagKeyValue": ["user:Environment$prod"] }
}'
```

## Multi-Region Considerations

- Latency from East Africa: `af-south-1` ~ 30 ms; `eu-west-1` ~ 150 ms; `us-east-1` ~ 220 ms. Place user-facing tiers in `af-south-1` whenever available.
- Data residency: Uganda DPPA 2019 requires personal data of Ugandan data subjects to be processed in a jurisdiction with adequate protection; `af-south-1` with KMS customer-managed keys is the low-friction default. Log the data-flow and cross-border transfer basis in `_context/compliance.md`.
- Replication: active-passive (primary `af-south-1`, warm standby `eu-west-1`) is the common starting posture; active-active only when conflict-resolution is designed in (DynamoDB Global Tables, Aurora Global Database with write forwarding). Route 53 health-checked failover records for DR, not client-side retry loops.

```bash
aws route53 create-health-check --caller-reference "ug-app-$(date +%s)" --health-check-config file://hc.json
aws dynamodb update-table --table-name orders --replica-updates '[{"Create": {"RegionName": "eu-west-1"}}]'
```

## Security Baseline

Enable these on the management account and every member account on day one. All commands are idempotent — safe to re-run.

```bash
aws cloudtrail create-trail --name org-trail --s3-bucket-name org-cloudtrail-logs \
  --is-multi-region-trail --is-organization-trail --enable-log-file-validation \
  --kms-key-id alias/cloudtrail
aws cloudtrail start-logging --name org-trail
aws s3api put-bucket-versioning --bucket org-cloudtrail-logs --versioning-configuration Status=Enabled
aws configservice start-configuration-recorder --configuration-recorder-name default
aws guardduty create-detector --enable --finding-publishing-frequency FIFTEEN_MINUTES
aws securityhub enable-security-hub --enable-default-standards
aws accessanalyzer create-analyzer --analyzer-name org-analyzer --type ORGANIZATION
```

- CloudTrail: all regions, S3 bucket with versioning, log-file validation, KMS-encrypted.
- AWS Config: enable the AWS Foundational Security Best Practices conformance pack.
- GuardDuty: detector in every region with S3 and EKS protection on.
- Security Hub: aggregate findings in a delegated admin account; resolve Critical/High within team SLO. IAM Access Analyzer: organization-level, reviewed weekly.

## Review Checklist

- [ ] Workload classified; compute model justified in writing.
- [ ] VPC spans ≥ 2 AZs; data stores Multi-AZ.
- [ ] No credentials in images, committed files, or Git history; IAM uses roles + OIDC, not long-lived keys.
- [ ] Deployment pattern chosen with rollback runbook validated; TLS, CDN, WAF posture documented.
- [ ] Auto-scaling signal is request- or latency-driven, not CPU-only.
- [ ] CloudTrail, Config, GuardDuty, Security Hub enabled across all regions; backups tested with a quarterly restore rehearsal (RTO/RPO documented); billing alerts active, Cost Explorer tags applied, Spot use paired with shutdown handling.

## Platform Notes

- Claude Code: `aws` CLI and `docker` CLI are the primary surface. Configure profiles with `aws configure sso`; use named profiles per environment.
- Codex: treat every command as a patch candidate; keep commands in shell blocks so they stay portable.

## References

- [references/aws-core-services.md](references/aws-core-services.md): EC2, S3, RDS, IAM, ALB, ASG, CloudFront CLI recipes.
- [references/docker-compose-patterns.md](references/docker-compose-patterns.md): Full local-parity stack template.
- [references/deployment-patterns.md](references/deployment-patterns.md): Blue-green and canary runbooks with rollback steps.
- AWS Well-Architected Framework: [aws.amazon.com/architecture/well-architected](https://aws.amazon.com/architecture/well-architected/)
- *Docker Deep Dive* — Nigel Poulton (reading programme, Phase 01 priority 1).
