# Docker for Node Production Images

Cross-ref: `cloud-architecture` for deploy patterns; `kubernetes-fundamentals` for
probes and resources; `kubernetes-production` for scaling; `reliability-engineering`
for shutdown; `cicd-devsecops` for image signing and scanning.

Target: a reproducible, small, rootless image for a pnpm monorepo service that
starts in under two seconds and passes a Kubernetes `startupProbe` reliably.

## The multi-stage Dockerfile

`apps/api/Dockerfile`:

```dockerfile
# syntax=docker/dockerfile:1.7
ARG NODE_VERSION=22.11.0
ARG PNPM_VERSION=9.12.0

# --- base --------------------------------------------------------------------
FROM node:${NODE_VERSION}-bookworm-slim AS base
ENV PNPM_HOME=/pnpm PATH=/pnpm:$PATH
RUN corepack enable && corepack prepare pnpm@${PNPM_VERSION} --activate
WORKDIR /repo

# --- deps (cached) -----------------------------------------------------------
FROM base AS deps
# Copy only manifests + lockfile for cache reuse
COPY pnpm-lock.yaml pnpm-workspace.yaml package.json ./
COPY apps/api/package.json ./apps/api/
COPY packages/schemas/package.json ./packages/schemas/
COPY packages/db/package.json ./packages/db/
COPY packages/api-client/package.json ./packages/api-client/
COPY packages/config/package.json ./packages/config/
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm install --frozen-lockfile

# --- build -------------------------------------------------------------------
FROM deps AS build
COPY . .
RUN pnpm --filter @acme/api... run build
# Produce a deploy-ready prunable dir with only the api's prod deps
RUN pnpm --filter @acme/api --prod deploy /out

# --- runtime -----------------------------------------------------------------
FROM node:${NODE_VERSION}-bookworm-slim AS runtime
ENV NODE_ENV=production \
    NODE_OPTIONS="--enable-source-maps --max-old-space-size=384" \
    TZ=UTC
WORKDIR /app

# Security: non-root user, strict umask, no shell for service
RUN apt-get update && apt-get install -y --no-install-recommends \
        tini ca-certificates curl \
      && rm -rf /var/lib/apt/lists/* \
  && groupadd --system --gid 10001 app \
  && useradd  --system --uid 10001 --gid app --home /app --shell /usr/sbin/nologin app

COPY --from=build --chown=app:app /out/node_modules ./node_modules
COPY --from=build --chown=app:app /out/dist         ./dist
COPY --from=build --chown=app:app /out/package.json ./package.json
# If Prisma, copy the engine and generated client:
# COPY --from=build --chown=app:app /out/node_modules/.prisma ./node_modules/.prisma

USER app
EXPOSE 3000
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["node", "dist/server.js"]

HEALTHCHECK --interval=15s --timeout=3s --start-period=20s --retries=3 \
  CMD curl -fsS http://127.0.0.1:3000/health || exit 1
```

Key points:

- `pnpm deploy` produces `/out` containing only what `@acme/api` needs at runtime,
  with `workspace:*` dependencies rewritten to real paths. Image stays small without
  pruning gymnastics.
- `tini` is PID 1 so zombies are reaped and signals forwarded to Node.
- Non-root user with a locked shell.
- `--enable-source-maps` makes production stack traces readable.
- `max-old-space-size` caps heap at ~384 MB in a 512 MB container, leaving headroom
  for native allocations.

## Slim vs distroless

| Aspect | `node:22-slim` (Debian) | `gcr.io/distroless/nodejs22-debian12` |
| --- | --- | --- |
| Size (compressed) | ~75 MB | ~50 MB |
| Shell / coreutils | yes (minimal) | no |
| Debuggability | easy (apt install) | hard (no shell, no curl) |
| Healthcheck via curl | works | requires Node-native probe |
| CVE surface | moderate | small |

Pick slim by default — exec-based debugging matters during incidents. Pick distroless
once you have a solid observability stack and a Node-native healthcheck.

Distroless healthcheck alternative:

```dockerfile
# Write a tiny healthcheck.mjs alongside dist/
HEALTHCHECK --interval=15s --timeout=3s CMD ["node", "dist/healthcheck.mjs"]
```

```js
// dist/healthcheck.mjs
import http from "node:http";
http.get("http://127.0.0.1:3000/health", (r) => process.exit(r.statusCode === 200 ? 0 : 1))
   .on("error", () => process.exit(1));
```

## .dockerignore

```text
**/node_modules
**/dist
**/.next
**/.turbo
**/coverage
**/.env*
**/.git
**/.github
**/*.log
**/.DS_Store
```

Missing this entry doubles image size and leaks secrets. Verify with `docker build
--progress=plain` and check the "transferring context" line.

## Environment injection

Never bake secrets into the image. Three layers:

1. Build-time: only non-secret `NODE_ENV`, `NEXT_PUBLIC_*`.
2. Runtime from orchestrator: `envFrom: secretRef` in Kubernetes, AWS Parameter Store
   via IAM role, Vault agent injector.
3. On startup: read, validate with Zod, fail loud.

```ts
// src/config.ts
import { z } from "zod";

const Env = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]),
  PORT: z.coerce.number().int().default(3000),
  DATABASE_URL: z.string().url(),
  REDIS_URL: z.string().url().optional(),
  LOG_LEVEL: z.enum(["fatal", "error", "warn", "info", "debug", "trace"]).default("info"),
  SENTRY_DSN: z.string().url().optional(),
});

export const env = Env.parse(process.env);
```

Crash on invalid config; don't start a half-configured server.

## Healthchecks — three endpoints

```ts
// Liveness — is the process alive?
app.get("/health", async () => ({ ok: true }));

// Readiness — are dependencies reachable?
app.get("/ready", async (_req, reply) => {
  try {
    await app.db.$queryRaw`SELECT 1`;
    if (app.redis) await app.redis.ping();
    return { ok: true };
  } catch (err) {
    return reply.code(503).send({ ok: false, err: (err as Error).message });
  }
});

// Startup — different threshold for slow boot
app.get("/startup", async () => ({ ok: true }));
```

Kubernetes `Deployment`:

```yaml
livenessProbe:
  httpGet: { path: /health, port: 3000 }
  periodSeconds: 10
  failureThreshold: 3
readinessProbe:
  httpGet: { path: /ready, port: 3000 }
  periodSeconds: 5
  failureThreshold: 2
startupProbe:
  httpGet: { path: /startup, port: 3000 }
  periodSeconds: 5
  failureThreshold: 30   # 150s to boot
```

Rule: readiness must fail when the DB is down, or the load balancer keeps sending
traffic to a broken instance. Liveness must not fail on transient DB errors, or
Kubernetes kills an otherwise-healthy pod.

## Graceful shutdown in Kubernetes

```yaml
spec:
  terminationGracePeriodSeconds: 60
  containers:
    - name: api
      lifecycle:
        preStop:
          exec: { command: ["sleep", "10"] }
```

`preStop` sleeps so the load balancer deregisters before Node starts refusing
connections. Inside the app, `SIGTERM` triggers `app.close()` which drains in-flight
requests and closes DB pools. See `fastify-backend.md` for the code.

## Build perf — BuildKit cache

Enable in CI:

```yaml
- uses: docker/build-push-action@v6
  with:
    context: .
    file: apps/api/Dockerfile
    cache-from: type=gha
    cache-to: type=gha,mode=max
    platforms: linux/amd64,linux/arm64
    push: true
    tags: ghcr.io/acme/api:${{ github.sha }}
    provenance: true
    sbom: true
```

The `--mount=type=cache,id=pnpm` line above preserves the pnpm store across builds —
critical for repo-wide caching when only one package changed.

## Image size budget

```text
node:22-slim base             ~75 MB
+ node_modules (trimmed)     +40-120 MB
+ dist                       +1-5 MB
Total target                  <250 MB compressed
```

Red flags: an image above 500 MB usually means `node_modules` wasn't pruned or the
`.dockerignore` is missing entries. Run `docker history <img>` to find the culprit
layer.

## Image hardening

- Sign with cosign in CI; verify at admission (Kyverno, Sigstore policy-controller).
- Scan with Trivy or Grype in the pipeline; block on HIGH/CRITICAL without waiver.
- Generate SBOM (`--sbom=true` with BuildKit) and attach to the registry.
- Set `seccompProfile: RuntimeDefault` and drop all Linux capabilities in the Pod
  spec.
- Read-only root filesystem:

```yaml
securityContext:
  readOnlyRootFilesystem: true
  runAsNonRoot: true
  runAsUser: 10001
  allowPrivilegeEscalation: false
  capabilities: { drop: ["ALL"] }
volumes:
  - name: tmp
    emptyDir: {}
volumeMounts:
  - { name: tmp, mountPath: /tmp }
```

## Running migrations

Never on app startup — races, half-migrated replicas, downgrade hell. Patterns:

1. Kubernetes `Job` in CI before rollout:
   ```yaml
   apiVersion: batch/v1
   kind: Job
   metadata: { name: migrate-{{sha}} }
   spec:
     template:
       spec:
         restartPolicy: Never
         containers:
           - name: migrate
             image: ghcr.io/acme/api:{{sha}}
             command: ["node", "dist/migrate.js"]
             envFrom: [{ secretRef: { name: api-env } }]
   ```
2. Helm `pre-upgrade` hook for the Job.
3. Rollback story: migrations must be forward- and backward-safe for the window of
   at least one version. Expand/contract pattern.

See `deployment-release-engineering`.

## Compose for local dev

`docker-compose.yml`:

```yaml
services:
  db:
    image: postgres:16-alpine
    environment: { POSTGRES_PASSWORD: dev, POSTGRES_DB: acme }
    ports: ["5432:5432"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 10
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
  api:
    build: { context: ., dockerfile: apps/api/Dockerfile, target: build }
    command: pnpm --filter @acme/api dev
    depends_on: { db: { condition: service_healthy } }
    environment: { DATABASE_URL: postgres://postgres:dev@db:5432/acme }
    volumes: [".:/repo"]
    ports: ["3000:3000"]
```

## Anti-patterns

- Running `node` as root, even "just in the base image". Attackers chain from RCE to
  host root.
- `npm install` in the Dockerfile of a pnpm workspace — breaks hoisting, bloats the
  image.
- `ENV NODE_ENV=production` before `pnpm install` — skips devDependencies needed for
  the build stage.
- `CMD pnpm start` — spawns a shell tree, pnpm, then node; signals do not propagate.
  `CMD ["node", "dist/server.js"]` is the right form.
- Healthcheck that hits the database — a blip in the DB kills every pod.
- Baking secrets with `--build-arg`. Leaks into image layers.
- One "latest" tag used in Kubernetes. Always pin to SHA digest.

## Decision rules

```text
Small service, need fast debug             -> node:22-slim + tini
Security team demands minimal CVEs         -> distroless, Node-native healthcheck
Cold-start-sensitive (lambda-like)         -> node:22-slim, preload modules
Native deps (bcrypt, argon2, sharp)        -> include glibc (slim), not alpine
Alpine                                      -> avoid except for static binaries
Multi-arch (arm64 on Graviton / M-series)  -> buildx with cache-to=type=gha
```
