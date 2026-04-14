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

<!-- dual-compat-start -->
## Use When

- Use when designing cloud deployments, Dockerising applications, laying out AWS or GCP environments, choosing a deployment pattern, or moving a workload from a single VM to a resilient multi-AZ topology.
- The task needs decisions about compute shape, data durability, traffic routing, cost posture, or deployment safety that must survive production load.

## Do Not Use When

- The task is a local developer experience fix with no cloud impact.
- Kubernetes is the target runtime — load `kubernetes-platform` instead once Phase 03 is in scope.
- The task is only about CI pipeline steps — use `cicd-pipelines` or `cicd-pipeline-design`.

## Required Inputs

- Workload shape: stateless web, stateful service, batch, async worker, scheduled job.
- Traffic profile: baseline RPS, peak RPS, burst duration, geographical spread.
- Data profile: size, durability tier, recovery point objective (RPO), recovery time objective (RTO).
- Budget posture: spend ceiling, willingness to use spot/reserved capacity, commitment horizon.
- Compliance constraints: data residency, encryption, audit retention.

## Workflow

1. Confirm workload shape, traffic profile, data durability tier, and compliance posture.
2. Select the compute model: single-host Docker Compose, EC2 ASG, ECS/Fargate, or Kubernetes (defer to Phase 03 skill).
3. Write the Dockerfile using the multi-stage pattern and a pinned distroless or slim base.
4. Lay out the `docker-compose.yml` for local parity with production service topology.
5. Size the AWS footprint: VPC with two or more AZs, subnets per tier, NAT, ALB, ASG, RDS with Multi-AZ, S3, CloudFront.
6. Define IAM roles and instance profiles using least privilege — no static keys.
7. Pick a deployment pattern (blue-green, canary, rolling) from the shape, traffic, and rollback budget.
8. Attach TLS (Certbot + Let's Encrypt or ACM), CDN, auto-scaling policy, and cost guardrails.
9. Document the runbook: deploy, rollback, scale, failure recovery.

## Quality Standards

- Multi-AZ for any production data store and any load-balanced compute tier.
- No credentials in Dockerfiles, images, Git history, or environment files committed to source.
- Every production image is signed, scanned, and pinned by digest before promotion.
- Every workload has a documented rollback path validated at least quarterly.
- Every account has billing alerts at 50%, 80%, and 100% of the monthly budget.

## Anti-Patterns

- Credentials in Dockerfiles, ENTRYPOINT scripts, or committed `.env` files.
- Single-AZ production topologies for paid customer traffic.
- Using the AWS root account or an engineer's IAM user as the application identity.
- Fat runtime containers with build toolchains left in the final image.
- Auto-scaling based only on CPU when request latency is the real pressure signal.
- Manual snapshot-and-copy "blue-green" without scripted, rehearsed rollback.

## Outputs

- Architecture diagram or topology description covering VPC, subnets, AZs, and data flow.
- Dockerfile(s) and `docker-compose.yml` for local parity.
- IaC skeleton or a written account plan naming every AWS resource to create.
- Deployment pattern selection with rollback runbook.
- Cost and scaling posture: reserved vs on-demand vs spot, auto-scaling triggers, CDN posture.

## References

- [references/aws-core-services.md](references/aws-core-services.md): Service-by-service CLI reference for EC2, S3, RDS, IAM, ALB, ASG, CloudFront.
- [references/docker-compose-patterns.md](references/docker-compose-patterns.md): Local-parity stack: Node.js + MySQL + Redis + vector DB sidecar.
- [references/deployment-patterns.md](references/deployment-patterns.md): Blue-green and canary runbooks with rollback steps.
<!-- dual-compat-end -->

## Load Order

1. Load `world-class-engineering` for the production bar.
2. Load `system-architecture-design` for decomposition and contracts.
3. Load this skill for the cloud runtime shape.
4. Pair with `cicd-pipelines` for delivery, `cicd-devsecops` for gate policy, `observability-monitoring` for telemetry, `deployment-release-engineering` for rollout, and `reliability-engineering` for failure design.

## Executable Outputs

For meaningful cloud architecture work produce:

- workload classification: stateless, stateful, async, batch, scheduled
- chosen compute model with rationale (Compose, EC2 ASG, ECS, K8s)
- VPC + subnet + routing layout across AZs
- Dockerfile using multi-stage pattern and pinned base
- `docker-compose.yml` mirroring production services
- IAM role inventory with least-privilege policy statements
- deployment pattern choice and rollback runbook
- cost posture: reserved / on-demand / spot split, savings plan assessment
- CDN, TLS, WAF, and auto-scaling configuration

## Compute Model Decision Rules

Use this decision ladder before writing any infra:

1. Single app, low traffic, one region → EC2 + Docker Compose on a managed instance, backed by RDS Multi-AZ and S3.
2. Multiple services, scaling needs, no operator skill in Kubernetes → ECS Fargate with ALB.
3. Multiple services, team ready for platform work, polyglot runtime, multi-tenant isolation → Kubernetes (defer to `kubernetes-platform` in Phase 03).
4. Async fan-out, batch, or event pipeline → Lambda + SQS + EventBridge, with state in DynamoDB or RDS.

Do not jump to Kubernetes because it is fashionable. Kubernetes is a commitment, not a default.

## Docker Standards

### Dockerfile Checklist

- Multi-stage build: compile/install in `builder`, copy only runtime artifacts to final stage.
- Pin base images by version and digest (`node:22.11.0-slim@sha256:...`).
- Prefer distroless or slim images for runtime stage.
- Run as non-root (`USER node`, `USER nobody`, or a dedicated UID).
- Set `WORKDIR`, `EXPOSE`, and `HEALTHCHECK` explicitly.
- Pass secrets through mounted files or environment from the orchestrator — never bake them in.
- Keep `.dockerignore` tight: exclude `.git`, `node_modules`, local logs, test fixtures, editor config.
- Order `COPY` statements from least-changing (package manifests) to most-changing (source) to preserve layer caching.

### Multi-Stage Skeleton (Node.js)

```dockerfile
FROM node:22.11.0-slim@sha256:<digest> AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --include=dev
COPY . .
RUN npm run build && npm prune --omit=dev

FROM gcr.io/distroless/nodejs22-debian12:nonroot AS runtime
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./
USER nonroot
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s CMD ["node", "dist/healthcheck.js"]
CMD ["dist/server.js"]
```

### Docker Compose for Local Parity

- One `docker-compose.yml` in the repo root that mirrors the production topology.
- Named volumes for all stateful services; never rely on bind mounts for databases.
- `depends_on` with `condition: service_healthy` when startup order matters.
- Use a `.env.example` committed to source, a `.env` ignored by Git, and an orchestrator-provided env in production.
- See `references/docker-compose-patterns.md` for the full template.

## AWS Core Services

### EC2

- Choose instance family by workload: `t4g`/`t3a` for burstable, `m7i`/`m6g` for balanced, `c7i` for CPU, `r7i` for memory, `i4i` for NVMe-heavy.
- Use AMIs built by Packer or EC2 Image Builder with an immutable pipeline — no manual console edits.
- User-data installs the runtime agent, CloudWatch agent, and a pinned application bootstrap only.
- Place production instances in private subnets. Expose only via ALB/NLB.

### S3

- Enable default encryption, block public access, and turn on versioning for any data you cannot reconstruct.
- Lifecycle rules: transition cold data to Glacier Instant Retrieval or Deep Archive, expire temporary objects.
- Presigned URLs for customer uploads and downloads — never hand out credentials.
- Use separate buckets for public static assets, private user data, backups, and audit logs.

### RDS

- Multi-AZ for production. Automated backups with a retention window that matches your recovery policy.
- Read replicas for read-heavy workloads, never for durability.
- Enable Performance Insights and Enhanced Monitoring from day one.
- Rotate credentials through Secrets Manager or Vault; no hard-coded DB passwords.

### IAM

- Roles, not users, for workloads. Use instance profiles on EC2 and task roles on ECS.
- Policy statements scoped to the specific ARNs and actions needed — no `*:*`.
- No long-lived access keys for CI/CD; use OIDC federation from GitHub Actions to assume role.
- MFA required for every human account. Root account locked away with hardware MFA.

## Deployment Patterns

Choose deliberately. See `references/deployment-patterns.md` for full runbooks.

| Pattern | When to use | Rollback cost |
|---------|------------|---------------|
| Rolling | Stateless services, small blast radius, no schema migration | Medium: in-flight requests can hit mixed versions |
| Blue-Green | Significant version jump, quick rollback requirement, schema-compatible changes only | Low: DNS or target-group flip |
| Canary | Risky change, want real-traffic signal before full promotion | Low: pull canary weight to zero |
| Shadow | Unproven new service receiving mirrored traffic for validation | Zero for users, high for infra |

### Rules

- Schema migrations must be backwards-compatible across at least two application versions (expand → migrate → contract).
- Every deploy runs a health check before target-group registration.
- Every deploy writes a signed deployment record (who, what, when, which artifact digest).
- Automatic rollback triggers on health-check failure, 5xx-rate regression, or latency regression beyond a defined SLO budget.

## TLS, CDN, Scaling, Cost

### TLS

- ACM-issued certs on ALB/CloudFront/API Gateway in AWS.
- Certbot + Let's Encrypt on Nginx for single-host or VPS footprints.
- TLS 1.2 minimum, prefer 1.3. HSTS with long max-age once the production cert path is stable.

### CDN

- CloudFront or Cloudflare in front of every static asset and cacheable API response.
- Signed URLs or signed cookies for private content.
- Invalidate surgically — never ship a workflow that calls `invalidate /*` on every deploy.

### Auto-Scaling

- Target tracking on request count per target or p95 latency — not CPU alone.
- Warm pools for slow-booting AMIs.
- Step scaling only when predictable load patterns justify it.

### Cost Optimisation

- Reserved Instances or Savings Plans for steady baseline compute; on-demand for burst.
- Spot for non-critical async workers with a graceful shutdown handler.
- S3 Intelligent-Tiering on buckets with unpredictable access patterns.
- Turn on Cost Explorer, Cost Anomaly Detection, and per-environment cost allocation tags from the first day.

## Review Checklist

- [ ] Workload classified and compute model justified in writing.
- [ ] VPC spans at least two AZs; data stores are Multi-AZ.
- [ ] No credentials in images, committed files, or Git history.
- [ ] IAM uses roles and OIDC, not long-lived keys.
- [ ] Deployment pattern chosen with rollback runbook validated.
- [ ] TLS, CDN, WAF posture documented.
- [ ] Auto-scaling signal is request- or latency-driven, not CPU-only.
- [ ] Billing alerts active; Cost Explorer tags applied; Spot use paired with shutdown handling.

## Platform Notes

- Claude Code users: the `aws` CLI and `docker` CLI are the primary execution surface. Configure profiles with `aws configure sso` and use named profiles per environment.
- Codex users: treat every command as a patch candidate. Keep commands in shell blocks so they stay portable.

## References

- [references/aws-core-services.md](references/aws-core-services.md): EC2, S3, RDS, IAM, ALB, ASG, CloudFront CLI recipes.
- [references/docker-compose-patterns.md](references/docker-compose-patterns.md): Full local-parity stack template.
- [references/deployment-patterns.md](references/deployment-patterns.md): Blue-green and canary runbooks with rollback steps.
- AWS Well-Architected Framework: [aws.amazon.com/architecture/well-architected](https://aws.amazon.com/architecture/well-architected/)
- *Docker Deep Dive* — Nigel Poulton (reading programme, Phase 01 priority 1).
