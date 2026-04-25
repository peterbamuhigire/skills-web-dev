# Deployment Patterns — Runbooks

Blue-green, canary, and rolling deployments with explicit rollback steps. Every pattern assumes backwards-compatible schema changes, scripted rollback, and an SLO-linked abort condition.

## Pattern Selection

| Shape | Pattern |
|-------|---------|
| Stateless web, small blast radius, no schema change | Rolling |
| Significant version jump, quick rollback need | Blue-Green |
| Risky or experimental change, want real-traffic signal | Canary |
| Unproven service needing behaviour validation | Shadow (traffic mirroring) |

All of them require:

1. Artefact pinned by digest — not by tag.
2. Health check endpoint that exercises real dependencies (DB reachable, cache reachable, queue reachable).
3. Abort criteria tied to SLOs: error rate, p95 latency, 5xx percentage.
4. Signed deployment record in a persistent store.

## Rolling Deployment (Default for Stateless Web)

### Flow

1. Build and sign image. Push to ECR/GCR with immutable tag and digest.
2. Update the Launch Template / Task Definition to reference the new digest.
3. Trigger ASG Instance Refresh or ECS Service update with a small max-unavailable (for example 25%).
4. New instances register with the target group only after passing the health check.
5. Old instances drain (connection draining 30–60s) and are terminated.
6. Abort condition: if any new instance fails health checks twice, pause the refresh.

### Rollback

- ECS: update the service back to the previous task definition revision.
- ASG: run another Instance Refresh with the prior Launch Template version.
- The old digest must still exist in the registry (retention ≥ 30 days).

## Blue-Green Deployment

### Setup

- Two identical environments: `blue` and `green`.
- A shared ALB with two target groups (`tg-blue`, `tg-green`).
- DNS or ALB listener rule points to one target group at a time (the "live" colour).

### Cutover Flow

1. Determine which colour is live (`blue`).
2. Deploy the new release to the idle colour (`green`).
3. Run smoke tests and health checks directly against `green` (internal DNS or tagged listener).
4. Flip the production listener to forward to `green`.
5. Monitor error and latency for 5–15 minutes.
6. Keep `blue` warm for the rollback window (24h typical).

### Rollback

- Flip the listener back to `blue`. No container rebuild, no re-deploy. Expected rollback time is seconds.

### Database Rule

Schema changes must be backwards-compatible with both colours. Use the expand → migrate → contract pattern:

1. **Expand:** add new columns/tables, dual-write if needed. Ship to both colours.
2. **Migrate:** backfill data. Switch reads to the new shape.
3. **Contract:** drop old columns/tables in a later release.

Never do a destructive migration in the same deploy as a blue-green cutover. The rollback path must not need a schema revert.

## Canary Deployment

### Setup

- Route a weighted slice of traffic (start at 1–5%) to the new version.
- ALB weighted target groups, ECS Appmesh, or CloudFront traffic splitter — any weighted router works.
- The canary runs the same code as the new release with the same configuration.

### Promotion Flow

1. Deploy new version behind a weight of 1%.
2. Observe SLOs on the canary pool for a defined soak window (for example 15 minutes).
3. Promote in steps: 1% → 5% → 25% → 50% → 100%, with a soak window at each step.
4. Abort if the canary's error rate exceeds baseline by a defined budget (for example 0.5 pp).

### Rollback

- Set canary weight to 0. Traffic returns to the stable pool.
- Investigate before re-promoting. Do not retry the same version without a change.

### Metrics to Compare (canary vs stable)

- HTTP 5xx rate
- Request latency p50, p95, p99
- Error logs per minute
- Saturation signals: CPU, memory, GC, thread pool
- Downstream error rate (DB, cache, third-party API)

## Shadow (Traffic Mirroring)

Send a copy of production traffic to the new service without affecting user responses.

Use when:

- Replacing a legacy service with a new implementation.
- Validating a refactor under real traffic with no user risk.

Tooling:

- Envoy / Istio traffic mirroring.
- ALB + Lambda fan-out for smaller use cases.

Shadowed traffic should not mutate state. Write targets go to a shadow database or are dropped entirely.

## Health Check Requirements

A reliable health endpoint returns 200 only when:

- The process can accept traffic.
- The primary database answers a cheap query.
- The cache responds to a `PING`.
- Required feature flags and config are loaded.

Return 503 during graceful shutdown so the load balancer removes the instance from rotation before TCP reset.

## Deployment Record (every deploy)

Emit a signed JSON record to a durable log:

```json
{
  "service": "web",
  "environment": "prod",
  "artifact_digest": "sha256:abcd...",
  "released_by": "github-actions:my-org/my-repo@sha:...",
  "released_at": "2026-04-15T10:42:13Z",
  "commit": "f3c0a1...",
  "changelog_ref": "https://github.com/my-org/my-repo/releases/tag/v1.42.0",
  "approvers": ["alice@example.com", "bob@example.com"],
  "rollback_target": "sha256:prev-digest"
}
```

Store in S3 with Object Lock (compliance mode) or in an immutable log stream. This is the forensic record when something goes wrong a week later.

## Abort Criteria (apply to all patterns)

Abort and rollback if any of:

- 5xx rate above baseline + 0.5 pp for 3 consecutive minutes.
- p95 latency above baseline + 30% for 3 consecutive minutes.
- Health-check failure rate above 5% across the new pool.
- Any security scanner emits a Critical finding on the running artefact.

## Post-Deploy Verification

- Run a synthetic smoke test against the canonical user journeys.
- Compare a pre-defined dashboard with the last good baseline. Store the screenshot or metric snapshot with the release record.
- Confirm downstream consumers (reports, analytics, webhooks) still receive data.
- Close the deploy in the change management system with the signed record attached.
