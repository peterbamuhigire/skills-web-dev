---
name: cloud-architecture
description: Use when designing cloud deployments, Dockerising applications, laying out AWS or GCP environments, choosing a deployment pattern, or moving a workload from a single VM to a resilient multi-AZ topology.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Cloud Architecture

Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Use when designing cloud deployments, Dockerising applications, laying out AWS or GCP environments, choosing a deployment pattern, or moving a workload from a single VM to a resilient multi-AZ topology.

## Do Not Use When

- The task is unrelated to cloud architecture or would be better handled by a more specific companion skill (`kubernetes-platform` for K8s ops, `infrastructure-as-code` for IaC tooling depth, `cicd-pipelines` for full pipeline construction).

## Required Inputs

- Project context, target users, latency and residency constraints, current stack, and the concrete problem to solve.
- The desired deliverable: design, Dockerfile, compose stack, deploy plan, migration plan, audit, or runbook.

## Workflow

1. Read this SKILL.md, then load only the referenced deep-dive files relevant to the task.
2. Apply the ordered guidance, decision rules, and checklists.
3. Produce the deliverable with assumptions, risks, and follow-up work made explicit.

## Quality Standards

- Execution-oriented and concise; aligned with `world-class-engineering`.
- Self-managed Debian/Ubuntu first, cloud-managed second, in line with the repository's engine stack.
- Deterministic reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Jumping to Kubernetes when EC2 + Compose or ECS Fargate would meet the requirement.
- Baking secrets or environment-specific URLs into images.

## Outputs

- Workload classification, compute model choice with rationale, VPC + subnet layout, Dockerfile, Compose file, IAM role inventory, deploy pattern + rollback runbook, cost posture, CDN/TLS/WAF/auto-scaling configuration.
- Assumptions, tradeoffs, and unresolved gaps when context is incomplete.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | Cloud topology decision record | Markdown ADR per `skill-composition-standards/references/adr-template.md` | `docs/cloud/topology-adr.md` |
| Security | Cloud account hardening checklist | Markdown doc covering root, IAM, network, logging baseline | `docs/cloud/hardening-checklist.md` |

## References

- `references/aws-core-services.md` — EC2, S3, RDS, IAM, ALB, ASG, CloudFront CLI recipes.
- `references/docker-compose-patterns.md` — Full local-parity stack template.
- `references/deployment-patterns.md` — Blue-green, rolling, canary runbooks with rollback.
- `references/github-actions-overview.md` — Workflow file structure and reference pipeline.
- `references/environment-management.md` — Staging/production parity and promotion flow.
<!-- dual-compat-end -->

## Load Order

1. `world-class-engineering` for the production bar.
2. `system-architecture-design` for decomposition and contracts.
3. This skill for the cloud runtime shape.
4. Pair with `cicd-pipelines` for delivery, `cicd-devsecops` for gate policy, `observability-monitoring` for telemetry, `deployment-release-engineering` for rollout, `reliability-engineering` for failure design, `kubernetes-platform` for clusters, `infrastructure-as-code` for IaC depth.

## §1 Cloud Foundations & The SaaS-Relevant Subset

The AWS Well-Architected Framework defines six pillars: Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, and Sustainability (`aws.amazon.com/architecture/well-architected/`). This skill uses these pillars as the spine of its review checklist (§9).

### Compute Model Decision Matrix

| Workload pattern | First choice | Second choice | Why |
|------------------|--------------|---------------|-----|
| Steady web/API, predictable traffic | Container on Debian/Ubuntu VPS (Compose or systemd) | EC2 / Compute Engine VM | Predictable cost, full control |
| Bursty / event-driven (webhooks, schedules) | Lambda / Cloud Functions | Containers + autoscaling | Sub-second cold-start tolerable, pay-per-invocation |
| Long-running background jobs (>15 min) | Container on VM with queue worker | ECS / Cloud Run | Lambda 15-minute hard limit |
| Stateful data layer (MySQL primary) | Managed RDS / Cloud SQL | Self-hosted on VPS | Backup, failover, patching automation |
| Object/file storage | S3 / Cloud Storage | Self-hosted MinIO | Eleven-nines durability, lifecycle policies |
| Multiple services, no platform team | ECS Fargate with ALB | Container on VPS | Managed control plane, ALB integration |
| Polyglot multi-tenant platform | Kubernetes (`kubernetes-platform`) | ECS Fargate | Workload isolation, per-tenant policies |

Kubernetes is a commitment, not a default.

### SaaS-Relevant AWS Subset

- EC2 — compute primitives. `t3`/`t4g` for steady, `c6i`/`c7i` CPU-bound, `m6i`/`m7i` balanced, `r6i`/`r7i` memory-bound, `i4i` NVMe-heavy.
- S3 — object store for assets, backups, exports. Lifecycle policies move cold data to S3-IA / Glacier.
- RDS — managed MySQL/PostgreSQL with Multi-AZ for production.
- Lambda — event handlers, scheduled jobs, lightweight APIs.
- IAM — identity and policy: least-privilege roles for services, MFA on humans, OIDC for CI.

### GCP Equivalents Map

| AWS | GCP |
|-----|-----|
| EC2 | Compute Engine |
| S3 | Cloud Storage |
| RDS | Cloud SQL |
| Lambda | Cloud Functions / Cloud Run |
| IAM | Cloud IAM |
| ALB | HTTPS Load Balancer |
| CloudFront | Cloud CDN |
| ACM | Certificate Manager |

### Cloud Provider Selection (East African Workloads)

| Dimension | AWS | GCP | Azure |
|-----------|-----|-----|-------|
| Closest region | `af-south-1` Cape Town (~30 ms) | `europe-west1` (~160 ms) | `southafricanorth` (~40 ms) |
| Data-residency fit | Strong (af-south-1 + KMS) | Weak (no ZA region for many services) | Strong (ZA North + Customer Lockbox) |
| Support in EAT | 24/7 Business; EMEA TAM overlap | 24/7 Standard | 24/7 ProDirect; ZA partners |
| Managed services breadth | Widest | Data/ML led | Microsoft-stack integration |

Default to AWS `af-south-1` for Uganda workloads with DPPA 2019 data; use Azure `southafricanorth` only for .NET-heavy stacks with an existing EA licence; avoid GCP as primary for DPPA-scoped data until a ZA region is GA.

## §2 Docker Fundamentals

- Image vs container — image is the read-only template (layers + manifest); container is the running instance with a writable layer on top.
- Layers — each Dockerfile instruction creates a layer. Order from least-frequently-changing (base, system deps) to most-frequently-changing (application code) to maximise cache hits.
- Multi-stage builds — separate `builder` (compilers, dev deps) from `runtime` (slim, no build tools).
- Registries — Docker Hub, GHCR, AWS ECR, GCP Artifact Registry. Tag with both an environment alias and an immutable `:sha-<git-sha>` tag; never deploy `:latest` to production.
- Security basics — run as non-root, scan images with Trivy or Grype, pin base image digest, keep images small (≤200 MB), `.dockerignore` excludes `.git`, `node_modules`, logs, fixtures.

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

## §3 Docker Compose For App + Dependencies

The Compose Specification consolidates legacy 2.x/3.x file formats; the modern format does not require a `version:` top-level key. One `docker-compose.yml` in the repo root mirrors production. Named volumes for stateful services; never bind-mount databases. Declare `healthcheck` on every dependency and gate startup with `depends_on.condition: service_healthy`.

```yaml
services:
  app:
    build: .
    environment:
      DATABASE_URL: mysql://app:${DB_PASSWORD}@db:3306/app
      REDIS_URL: redis://cache:6379
    depends_on:
      db: { condition: service_healthy }
      cache: { condition: service_started }
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/healthz"]
      interval: 10s
      retries: 6
    restart: unless-stopped

  db:
    image: mysql:8.4
    environment:
      MYSQL_DATABASE: app
      MYSQL_USER: app
      MYSQL_PASSWORD: ${DB_PASSWORD}
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
    volumes: [dbdata:/var/lib/mysql]
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 5s
      retries: 10

  cache:
    image: redis:7-alpine
    restart: unless-stopped

  proxy:
    image: caddy:2
    ports: ["80:80", "443:443"]
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
    depends_on: [app]

volumes:
  dbdata: {}
  caddy_data: {}
```

Caddy is recommended for VPS-first deployments because it automates Let's Encrypt issuance and renewal out of the box (`caddyserver.com/docs/automatic-https`). Commit `.env.example`, ignore `.env`, and provide env through the orchestrator in production. See `references/docker-compose-patterns.md` for the full template.

## §4 GitHub Actions CI/CD Overview

Workflows live in `.github/workflows/*.yml`. Top-level keys: `name`, `on`, `permissions`, `env`, `defaults`, `concurrency`, `jobs`. Each job needs `runs-on` and `steps`; jobs run in parallel by default.

Minimal pattern: `build-test` job builds the image, runs tests, pushes to GHCR with an immutable `sha-<git-sha>` tag; `deploy-vps` job (gated by `environment: production` for required reviewers) SSHes in and runs `docker compose pull && up -d`. Secrets discipline: only short-lived deploy credentials in GitHub Actions secrets; long-lived secrets (DB password, API keys) live in Vault and are pulled at runtime.

Full workflow file, cloud-target variants, and concurrency control: `references/github-actions-overview.md`. Pipeline depth, matrix strategy, reusable workflows: `cicd-pipelines`. DevSecOps gates: `cicd-devsecops`.

## §5 Staging / Production Environment Management

Four axes of separation:

| Axis | Staging | Production |
|------|---------|------------|
| Data | Anonymised production-like fixture; never live PII. | Live data, encrypted at rest, backed up. |
| Secrets | Separate Vault path; non-production keys only. | Vault production path; rotation enforced. |
| Traffic | Synthetic + internal users. | Real users; protected by WAF + rate limits. |
| Observability | Same instrumentation; lower retention; alerts page no one. | Full retention; on-call paging on SLO-linked alerts. |

**Build once, deploy many.** The same image SHA that passed staging is the image that runs in production. Configuration differs (env vars, secrets, replica count); the artifact does not. Promotion flow: feature branch → PR + checks → main → staging deploy → smoke + soak → production deploy (same SHA, gated by required reviewers).

Configuration layering, sanitisation script policy, and full promotion checklist: `references/environment-management.md`.

## §6 SSL/TLS, CDN, Auto-Scaling

### SSL/TLS Automation

- AWS ALB / CloudFront / API Gateway → ACM certificates: free, auto-renewed, DNS-validated via Route 53. ACM-issued certs cannot be exported.
- VPS-first → Caddy auto-issues and renews from Let's Encrypt with no extra config; nginx + certbot for hosts where Caddy is not viable.
- Kubernetes → `cert-manager` with a `ClusterIssuer` for Let's Encrypt ACME HTTP-01 or DNS-01.

```bash
aws acm request-certificate --domain-name app.example.co.ug \
  --subject-alternative-names "*.app.example.co.ug" \
  --validation-method DNS --key-algorithm RSA_2048
sudo certbot --nginx -d app.example.co.ug --deploy-hook "systemctl reload nginx"
```

TLS 1.2 minimum, prefer 1.3. Enable HSTS `max-age=31536000; includeSubDomains; preload` once the production cert path is stable.

### CDN

| Goal | First choice | Notes |
|------|--------------|-------|
| AWS-native edge caching | CloudFront | Native ACM integration, Lambda@Edge for request rewrite. |
| Multi-cloud or VPS in front | Cloudflare | Free tier viable for SaaS MVPs; WAF and bot mitigation included. |

CloudFront or Cloudflare in front of every static asset and cacheable API response. Enable Origin Shield close to origin to cut origin fetches by 60–80%. Attach AWS WAF with the Managed Rules Core Rule Set plus Known Bad Inputs and IP-Reputation; add a rate-based rule at 2000 req/5 min/IP for unauthenticated endpoints. Invalidate surgically — use versioned asset paths (`/static/v=<build-sha>/`); cache-bust HTML only.

### Auto-Scaling

Target tracking first, step scaling second, predictive third. Scale on request count per target and P95 latency — not CPU alone. AWS ASG scales EC2 horizontally on CloudWatch metrics; Lambda concurrency is governed by reserved/provisioned concurrency. For VPS-first with Compose, scale vertically first (bigger VPS), then introduce a load balancer in front of multiple VPS instances. Kubernetes HPA → `kubernetes-platform`.

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

CPU target 70% for CPU-bound services; never below 40% (wastes capacity). Predictive scaling needs ≥14 days of CloudWatch history and a regular pattern. Warm pools for slow-booting AMIs (>3 min boot).

## §7 Zero-Downtime Deployment Patterns

| Pattern | How it works | When to use | Trade-off |
|---------|--------------|-------------|-----------|
| Rolling | Replace instances N at a time, health-check each. | Default for stateless web apps with ≥2 instances. | Mixed-version window during rollout. |
| Blue/green | Run new version (green) alongside old (blue); flip traffic via load balancer / DNS. | Schema-compatible releases needing instant rollback. | Doubles infra cost during cutover. |
| Canary | Send a small % of traffic to the new version, expand on green metrics. | High-risk changes with observability fast enough to detect regression. | Requires traffic-splitting layer (ALB weighted target groups, Cloudflare LB, service mesh). |

Automatic rollback triggers on health-check failure, 5xx-rate regression > 0.5% over 5 min, or P95 latency regression beyond SLO budget. Schema migrations must be backwards-compatible across two application versions (expand → migrate → contract). Every deploy writes a signed record: who, what, when, artifact digest.

### VPS-First Blue/Green With Caddy

1. Deploy `app-green` on port 3001 alongside `app-blue` on port 3000 (`docker compose --profile green up -d`).
2. Health-check `app-green` for N minutes against `/healthz`.
3. Update Caddy upstream from `:3000` to `:3001` and reload (`caddy reload --config /etc/caddy/Caddyfile`); Caddy reloads without dropping connections.
4. Hold blue for a soak window (≥30 minutes) as a hot rollback target.
5. Stop `app-blue` once error-rate and latency SLOs hold.

### Cloud-Managed Blue/Green With ALB

```bash
aws elbv2 create-target-group --name app-tg-green --protocol HTTP --port 3000 \
  --vpc-id vpc-0abc --health-check-path /healthz --health-check-interval-seconds 15 \
  --healthy-threshold-count 2 --unhealthy-threshold-count 3 --matcher HttpCode=200
aws elbv2 modify-listener --listener-arn $LISTENER_ARN \
  --default-actions Type=forward,TargetGroupArn=$TG_GREEN
```

Rolling refresh on ASG:

```bash
aws autoscaling start-instance-refresh --auto-scaling-group-name app-prod-asg \
  --strategy Rolling --preferences '{
    "MinHealthyPercentage": 90, "InstanceWarmup": 180,
    "CheckpointPercentages": [25, 50, 100], "CheckpointDelay": 600
  }'
```

Rollback: re-point the listener to `app-tg-blue` (blue/green) or `aws autoscaling cancel-instance-refresh` and roll forward with the prior Launch Template version. Full runbooks: `references/deployment-patterns.md`.

## §8 Cost-Aware Architecture Decisions

The Cost Optimization pillar of AWS Well-Architected centres on five design principles: implement cloud financial management, adopt a consumption model, measure overall efficiency, stop spending on undifferentiated heavy lifting, and analyse and attribute expenditure (`aws.amazon.com/architecture/well-architected/`).

### Cost Levers

| Lever | Action | Notes |
|-------|--------|-------|
| Right-sizing | Match instance class/size to actual CPU+memory profile after ≥2 weeks of metrics. | Measure before resizing; project must confirm savings. |
| Reserved / Savings Plans | 1- or 3-year commitment for steady-state baseline (70–80% of average compute); spot/preemptible for batch. | Prefer Compute Savings Plans 1y no-upfront initially; 3y only when headcount and roadmap are certain. |
| S3 lifecycle | Move logs/backups to S3-IA after 30 d, Glacier after 90 d. | Storage-class delta; project must measure. |
| Egress | Keep traffic intra-AZ where possible; CDN absorbs repeat reads. | NAT GW per AZ avoids cross-AZ data charges. |
| Right-data-tier | MySQL primary on managed RDS; cold reports → S3 + Athena. | Avoids overprovisioning RDS. |
| Spot / preemptible | Async workers, CI runners with graceful shutdown handler for interruption notice. | Pair with on-demand fallback. |
| Tagging | Tag every resource with `Environment`, `Team`, `CostCenter`, `Project`; activate as cost-allocation tags. | Cost Explorer + per-environment budgets from day one. |

```bash
aws ce list-cost-allocation-tags --status Active --region us-east-1
aws budgets create-budget --account-id 111122223333 --budget '{
  "BudgetName": "ug-prod-monthly",
  "BudgetLimit": { "Amount": "5000", "Unit": "USD" },
  "TimeUnit": "MONTHLY", "BudgetType": "COST",
  "CostFilters": { "TagKeyValue": ["user:Environment$prod"] }
}'
```

Verify pricing figures against the current AWS pricing page before publishing — do not quote saving percentages without a fresh source.

## §9 Architecture Review Checklist (Six Pillars)

Walk each Well-Architected pillar against the deployment under review:

- **Operational Excellence** — runbooks documented, deployments automated, postmortems blameless, observability covers all four golden signals (latency, traffic, errors, saturation), telemetry routed to SigNoz.
- **Security** — IAM least-privilege, secrets in Vault not env files or images, SSL/TLS everywhere including internal hops, audit log retention defined, MFA on every human, root locked away with hardware MFA, OIDC federation for CI.
- **Reliability** — VPC spans ≥2 AZs, data stores Multi-AZ, backup + restore tested quarterly, RTO/RPO recorded, error budget defined, dependency timeouts and retries explicit.
- **Performance Efficiency** — instance sizing measured, caching tier present, database indexed for top queries, CDN in front of static assets, P95 latency tracked.
- **Cost Optimization** — billing alerts on, untagged resources rejected, reserved-vs-on-demand reviewed quarterly, Spot use paired with shutdown handling.
- **Sustainability** — over-provisioning eliminated, cold storage tiering on, idle dev environments shut down outside work hours, regional choice considers carbon intensity.

## Backup, Multi-Region, Security Baseline

These cross-cutting concerns are summarised below; deep CLI is in `references/aws-core-services.md`.

- **Backup & DR** — typical SaaS targets RTO ≤ 4 h, RPO ≤ 15 min. RDS automated backups 7–35 days with PITR; weekly manual snapshots retained 90 days; cross-region snapshot copy to `eu-west-1` as a sovereignty-preserving DR site. S3 versioning + Cross-Region Replication for critical buckets. EBS daily snapshots via AWS Backup. Rehearse restore quarterly.
- **Multi-Region** — `af-south-1` ~30 ms; `eu-west-1` ~150 ms; `us-east-1` ~220 ms from East Africa. Active-passive (primary `af-south-1`, warm standby `eu-west-1`) is the common starting posture; active-active only when conflict-resolution is designed in.
- **Account Security Baseline** — CloudTrail multi-region with log-file validation and KMS, AWS Config with the Foundational Security Best Practices conformance pack, GuardDuty in every region with S3 and EKS protection, Security Hub aggregating in a delegated admin account, IAM Access Analyzer at organization level reviewed weekly.

## Networking & Load Balancers (Quick Reference)

Design VPC across ≥3 AZs for production, 2 for non-production. Allocate /16; carve /20 public and /20 private subnets per AZ. NAT gateway per AZ in production — single-AZ NAT is a SPOF and cross-AZ data charges bite. Security groups (stateful, instance-level) are the primary tool; NACLs (stateless, subnet-level) only for coarse boundaries.

| Feature | ALB | NLB |
|---------|-----|-----|
| Layer | 7 (HTTP/HTTPS/gRPC) | 4 (TCP/UDP/TLS) |
| Routing | Host, path, header, query | Port-based |
| TLS termination | At ALB | Passthrough or at NLB |
| Use case | Web APIs, microservices | High-throughput TCP, static IPs, PrivateLink |

Health checks hit a dedicated `/healthz` path; verify dependencies shallowly — deep checks cause cascading failures evicting healthy targets. Full networking and AWS-core CLI: `references/aws-core-services.md`.

## Decision rules
| Condition | Action |
|---|---|
| Single-zone failure breaches SLO | Use multi-zone placement |
| Managed service fits need and budget | Prefer managed service |
| Data residency uncertain | Stop region selection |

## Domain Anti-Patterns
- Adding multi-region without recovery need. Fix: derive it from RTO/RPO.
- Exposing databases publicly. Fix: use private networking.
- Giving workloads broad IAM roles. Fix: scope permissions.
- Treating autoscaling as capacity planning. Fix: test limits.
- Ignoring egress and idle cost. Fix: model traffic costs.

## Platform Notes

- Codex: `aws` CLI and `docker` CLI are the primary surface. Configure profiles with `aws configure sso`; use named profiles per environment.
- Codex: treat every command as a patch candidate; keep commands in shell blocks so they stay portable.
