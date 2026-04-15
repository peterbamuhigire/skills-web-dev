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
