---
name: cicd-pipelines
description: Use when designing or implementing a CI/CD pipeline — stage gates, GitHub Actions production patterns (matrix, reusable workflows, environments), OIDC federation to AWS/GCP/Vault, dependency and Docker-layer caching, fan-out/fan-in orchestration, blue/green and canary deployment, pipeline observability (DORA metrics, queue time), and choosing between GitHub Actions and GitLab CI.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# CI/CD Pipelines
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.
<!-- dual-compat-start -->
## Use When

- Use when designing or implementing a release pipeline that turns every commit into a release candidate progressing through automated stages with clear pass/fail gates.
- Use when picking GitHub Actions vs GitLab CI, federating CI to cloud or Vault via OIDC, or wiring blue/green / canary deploys into a workflow.
- Use when adding pipeline observability (DORA metrics, queue time, stage duration) or fixing anti-patterns like cache poisoning, mega-workflows, or rebuild-per-environment.

## Do Not Use When

- Jenkins-on-Debian operations, plugin governance, or controller hardening — load `references/cicd-jenkins-debian.md`.
- Vault server architecture, PKI, exception governance, or compliance controls — load `references/cicd-devsecops.md`.
- High-level pipeline shape and stage-boundary design from a blank slate — start with `references/cicd-pipeline-design.md`, then return here for the engine-specific implementation.

## Required Inputs

- Source-control engine (GitHub, GitLab CE, both) and runner story (self-managed Debian/Ubuntu, hosted, mix).
- Target deploy surface (Debian VPS, Kubernetes, ECS, mobile stores) and the chosen deployment strategy.
- Secret-management posture (Vault, AWS Secrets Manager, env secrets) and whether OIDC federation is already wired.

## Workflow

- Read this `SKILL.md` first; load only the referenced files needed for the engine and deploy surface in front of you.
- Apply the stage-gate model in §1 before writing YAML — pipelines without explicit gates rot into mega-workflows.
- Produce the deliverable (workflow YAML, trust policy, deploy record schema) with assumptions and rollback plan made explicit.

## Quality Standards

- Build once, deploy many: a single artefact (digest-pinned image, signed AAB, `.ipa`) is promoted through every environment.
- Least-privilege `permissions:` per workflow and per job; no static cloud keys when OIDC is available.
- Every production deploy emits a deployment record (git SHA, image digest, environment, actor, timestamp, run URL) to an append-only sink.

## Anti-Patterns

- Echoing constructed strings containing secrets; pinning third-party actions to mutable tags; one mega-workflow per repo.
- Cache keys without a lockfile hash; rebuilding per environment; deploying without a `concurrency:` group on production.
- Long-lived static `AWS_ACCESS_KEY_ID` in repo secrets when OIDC federation is available.

## Outputs

- Reusable workflow with versioned inputs/outputs; environment-specific deploy workflows; rollback workflow.
- OIDC trust policy, least-privilege IAM/Vault role binding, deployment-record schema and sink.
- Pipeline-observability dashboard spec (DORA quad + queue time + stage p95) wired into SigNoz/Prometheus.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Release evidence | Pipeline configuration record | Markdown doc covering build, test, deploy stages plus secret references | `docs/ci/pipeline-config.md` |
| Release evidence | Latest release run evidence | CI URL plus archived log of the most recent successful release | `docs/ci/release-run-2026-04-16.md` |
| Release evidence | Deployment record sink schema | JSON schema + sample row | `docs/ci/deployment-record.md` |

## References

- `references/oidc-federation.md` — OIDC → AWS, GCP, and Vault with bound-claim trust policies.
- `references/pipeline-observability.md` — DORA metrics, queue time, scraper sketch, dashboards.
- `references/reference-architectures.md` — three end-to-end pipelines (PHP/MySQL SaaS, Node.js/TS service, container library).
- `references/anti-patterns.md` — broken vs fixed examples.
- `references/github-vs-gitlab.md` — engine comparison and migration notes.
- `references/github-actions-workflows.md`, `references/mobile-pipelines.md`, `references/ios-fastlane-pipeline.md`, `references/android-pipeline.md` — domain templates.
<!-- dual-compat-end -->

## Load Order

1. Load `world-class-engineering` and `git-collaboration-workflow` for the baseline.
2. Load `references/cicd-pipeline-design.md` for the high-level pipeline shape.
3. Load this skill for engine-specific implementation (GitHub Actions primary, GitLab CI secondary).
4. Pair with `references/cicd-devsecops.md` for secrets policy, `references/cicd-jenkins-debian.md` when the engine is Jenkins, `deployment-release-engineering` for rollout, `observability-monitoring` for post-deploy verification, `cloud-architecture` for traffic-shifting plumbing.

## §1 What a CI/CD pipeline is and is not

The deployment pipeline is the canonical model: every commit produces a release candidate that progresses through automated stages, and any failed stage stops the candidate. Continuous Delivery (Humble & Farley, Addison-Wesley, 2010, ISBN 978-0-321-60191-9) frames the pipeline as the mechanism by which you build quality in rather than testing it in afterwards. The DevOps Handbook (2nd ed., Kim, Humble, Debois, Willis, IT Revolution, 2021, ISBN 978-1-950508-40-2) reinforces this with the First Way (flow from development to operations) and Second Way (fast feedback via short-lived automated pipelines).

Stage-gate convention used throughout this skill, derived from the canonical 5-stage model:

| Stage | Purpose | Target duration |
|-------|---------|-----------------|
| Commit | Compile, unit tests, lint, type-check | < 5 min |
| Build artefact | Reproducible artefact (image digest, jar, signed AAB, `.ipa`) | < 5 min |
| Acceptance / integration | Service-level tests against real dependencies | < 15 min |
| Security scan | SAST, dependency scan, container scan, secret scan | parallel with acceptance |
| Deploy to staging | Automated, no human gate | < 5 min |
| Deploy to production | Gated (manual approval or progressive delivery) | minutes |

Pipeline-as-code, deploy-on-green, and a single artefact promoted across environments are the three load-bearing principles. Branch-based release calendars (cut a branch, freeze, manually QA) are the failure mode this model replaces.

## §2 GitHub Actions production patterns

Workflow files live under `.github/workflows/*.yml` and are triggered by `on:` events: `push`, `pull_request`, `schedule`, `workflow_dispatch`, `workflow_call`, `release`. Filename is the stable reference; `name:` is human-readable. Jobs run in parallel by default; use `needs:` to serialise.

The two reuse primitives:

- Reusable workflow (`on: workflow_call`) — job-level reuse. Accepts `inputs:` and `secrets:`; callers can pass `secrets: inherit` to forward all secrets without listing each one. Up to 10 levels of nesting.
- Composite action (`action.yml` in a directory) — step-level reuse. Bundles multiple steps as a single `uses:`.

Use composite actions for "set up the build toolchain", reusable workflows for "the standard CI job for a Node service".

Matrix, concurrency, permissions:

```yaml
strategy:
  fail-fast: false
  matrix:
    node: ['18', '20', '22']
    os: [ubuntu-24.04, macos-14]

concurrency:
  group: deploy-${{ github.ref }}-${{ matrix.environment }}
  cancel-in-progress: false

permissions:
  contents: read
  id-token: write
  packages: read
```

`fail-fast: false` is the platform-engineering default — see all matrix-leg failures, not just the first.

Environments wrap a deploy target with policy: required reviewers, wait timer, deployment-branch policy, environment-scoped secrets. Production deploys always run inside an environment:

```yaml
jobs:
  deploy-prod:
    environment: { name: production, url: https://app.example.com }
    runs-on: ubuntu-24.04
```

GitLab CI dialect differences live in `references/github-vs-gitlab.md`; the patterns here apply to both engines.

## §3 Secret injection without long-lived credentials

`GITHUB_TOKEN` is automatically issued per workflow run with permissions the workflow specifies; grant the least required access. Pin per job and never rely on legacy write-all defaults.

`id-token: write` enables OIDC federation — the workflow exchanges a short-lived OIDC token for a cloud or Vault credential. No static `AWS_ACCESS_KEY_ID` anywhere.

Minimal AWS pattern:

```yaml
permissions: { id-token: write, contents: read }
steps:
  - uses: actions/checkout@v4
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789012:role/github-actions-deploy
      aws-region: eu-west-1
  - run: aws sts get-caller-identity
```

Bind the IAM trust policy to the exact `sub` (`repo:acme/api:environment:production`), never `repo:*`. Vault's JWT auth method consumes the same OIDC token; the Vault role binds the same `sub` claim and a short token TTL. GCP uses Workload Identity Federation with the same shape. Full trust-policy JSON, GCP WIF binding, and Vault role config live in `references/oidc-federation.md`.

Secret scoping:

- Repository secrets — unscoped; reuse across workflows (e.g., `CODECOV_TOKEN`).
- Environment secrets — scoped to a GitHub Environment (`dev`, `staging`, `production`). Production secrets never leak into PR builds.
- Organisation secrets — shared across repos; use sparingly, prefer environment scoping.

## §4 Artifact and dependency management

Lockfile-keyed dependency caches:

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
    restore-keys: ${{ runner.os }}-npm-
```

Targets: `~/.npm`, `~/.cache/pnpm`, `~/.cache/composer`, `~/.gradle/caches` + `~/.gradle/wrapper`, `Pods/` (keyed on `Podfile.lock`), `~/.cargo/registry` + `target/`, `~/.cache/pip` (keyed on `requirements*.txt`). The `setup-node` / `setup-python` / `setup-java` actions have a built-in `cache:` parameter — prefer it when the lockfile is at the repo root.

Docker BuildKit cache via `type=gha` with `mode=max` stores all intermediate layers. Order Dockerfile instructions from least-likely-to-change to most-likely-to-change — once a layer changes, all downstream layers rebuild. Cache size limit is 10 GB per repo; evict old caches via `gh cache delete`.

Cross-job artefacts use `actions/upload-artifact` / `actions/download-artifact`. Container images go to GHCR (`ghcr.io/<owner>/<repo>:<sha>`) tied to repo permissions; ECR via OIDC for AWS-hosted services.

Multi-platform images only when the runtime differs (ARM Graviton, Apple Silicon dev) — it doubles build time. Sign with `cosign` keyless and emit `provenance: true` and `sbom: true` from `docker/build-push-action` so consumers can verify before deploy.

## §5 Parallelism, fan-out / fan-in, manual approvals, concurrency

Four orchestration primitives:

- Fan-out: matrix strategy or multiple top-level jobs running in parallel.
- Fan-in: dependent jobs declared via `needs: [job-a, job-b]`.
- Manual approval: environment with required reviewers — the deploy job pauses until approved.
- Concurrency: `concurrency: { group: deploy-prod, cancel-in-progress: false }` ensures only one prod deploy runs at a time. For PR previews use `cancel-in-progress: true` so superseded commits abandon in-flight runs.

Test parallelisation pattern (Playwright shards, then merge reports):

```yaml
e2e:
  strategy:
    fail-fast: false
    matrix: { shard: [1/4, 2/4, 3/4, 4/4] }
  runs-on: ubuntu-24.04
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with: { node-version: '20', cache: 'npm' }
    - run: npm ci && npx playwright install --with-deps
    - run: npx playwright test --shard=${{ matrix.shard }} --reporter=blob
    - uses: actions/upload-artifact@v4
      with: { name: blob-report-${{ strategy.job-index }}, path: blob-report, retention-days: 1 }

merge-reports:
  if: always()
  needs: [e2e]
  runs-on: ubuntu-24.04
  steps:
    - uses: actions/download-artifact@v4
      with: { path: reports, pattern: blob-report-*, merge-multiple: true }
    - run: npx playwright merge-reports --reporter=html ./reports
```

Jest shards via `jest --shard=1/4` across a matrix or `--maxWorkers=50%` on one large runner. Report merging is mandatory — reviewers need a single HTML report.

## §6 Deployment strategies invoked from a pipeline

| Strategy | When to use | Key implementation knob |
|----------|-------------|--------------------------|
| Rolling | Stateless service, minor risk | Replicas updated N at a time |
| Blue / green | Need atomic cutover, easy rollback | Two parallel environments + traffic switch |
| Canary | High-risk change, gradual rollout | % traffic shift over time, automated abort on SLO breach |

Detailed traffic-shifting plumbing (Kubernetes Service swap, Argo Rollouts, AWS CodeDeploy, Nginx symlink swap on Debian VPS) lives in `cloud-architecture` and `deployment-release-engineering`. The pipeline's job is to invoke the strategy, watch the health gate, and trigger rollback on SLO breach.

Promotion is `workflow_dispatch` with an `image_digest` input — never a rebuild:

```yaml
name: promote
on:
  workflow_dispatch:
    inputs:
      image_digest: { description: 'sha256:... to promote', required: true }
      target:
        description: 'Target environment'
        required: true
        type: choice
        options: [staging, production]
jobs:
  deploy:
    runs-on: ubuntu-24.04
    environment: { name: ${{ inputs.target }} }
    steps:
      - run: deploy.sh "${{ inputs.image_digest }}" "${{ inputs.target }}"
```

Rollback is the same workflow with the previous digest. Three rollbacks in a week on the same service freezes deploys until a post-mortem is filed. A nightly scheduled staging re-deploy detects drift between `main` HEAD and live.

## §7 Pipeline observability

The four DORA metrics — deployment frequency, lead time for changes, change failure rate, mean time to restore — are the canonical indicators of pipeline health (The DevOps Handbook). Augment with:

- Queue time (`run.created_at` → `run.started_at`) — p95 < 60 s.
- Stage duration distribution (p50 / p95 / p99 per stage) — commit-stage p95 < 5 min.
- Cache hit rate (actions/cache + BuildKit) — > 80%.
- Workflow failure rate on `main` — < 10%.

Workflow timings come from `GET /repos/{owner}/{repo}/actions/runs` and `/runs/{id}/jobs`. A small scraper polls and ships line-protocol to the platform observability backend (SigNoz OTLP or Prometheus pushgateway). Schema and scraper pseudocode live in `references/pipeline-observability.md`.

Every successful production deploy emits one row to an append-only sink (S3 + Athena, BigQuery, or a Postgres `deployments` table). DORA metrics are computed from this table — not reconstructed from logs. Pair with `observability-monitoring` for SLO and alert design.

## §8 GitHub Actions vs GitLab CI

For repos in the self-managed Debian/Ubuntu stack (Jenkins + GitLab CE + Nexus 3 + Vault), the canonical engine is GitLab CI on self-managed runners. GitHub Actions is used for repos already on GitHub.com — primarily mobile (iOS hosted `macos-14`) and OSS releases.

Quick-decision summary:

| Concern | GitHub Actions | GitLab CI |
|---------|----------------|-----------|
| Configuration | `.github/workflows/*.yml` (multiple) | `.gitlab-ci.yml` (single, with `include:`) |
| Reuse | Reusable workflows + composite actions | `include:` + components |
| Job graph | DAG via `needs:` | Stages-then-jobs (DAG via `needs:`) |
| Secrets | Repo / env / org, OIDC, `secrets: inherit` | CI/CD variables (masked, protected, env-scoped), OIDC ID token |
| Concurrency | `concurrency:` keyword | `resource_group:` |

Full comparison and migration notes (claim shapes for OIDC `sub`, matrix → `parallel:matrix:`, marketplace → components) live in `references/github-vs-gitlab.md`.

## §9 Anti-patterns and pitfalls

Headline list — broken-vs-fixed examples in `references/anti-patterns.md`:

- Echoing secrets via constructed strings (URL with embedded token) bypasses GitHub's redactor.
- Cache keys without a lockfile hash poison subsequent builds with stale dependencies.
- The mega-workflow — one 800-line `ci.yml` — is unmaintainable; split per concern with reusable workflows.
- Missing `permissions:` block defaults to write-all on older repos; pin per workflow and per job.
- No `concurrency:` on production allows two simultaneous deploys to race on `kubectl apply`.
- Rebuilding per environment lets staging and production drift silently; build once on merge to `main`, promote the digest.
- Pinning third-party actions to mutable tags (`@v1`) lets a publisher repoint to a malicious commit; pin to a full SHA on security paths.
- Logging the entire environment can leak vended Vault tokens that the redactor never registered.

## §10 Reference architectures

Three worked examples covered end-to-end in `references/reference-architectures.md`:

1. PHP/MySQL SaaS — composer install, PHPUnit, PHPStan, Trivy on container, OIDC → Vault → DB creds, blue/green via Nginx symlink swap on Debian VPS.
2. Node.js/TypeScript service — pnpm, vitest, `tsc --noEmit`, esbuild bundle, container build, push to GHCR, canary via Argo Rollouts.
3. Container image library — multi-arch BuildKit, SBOM via syft, keyless cosign signing — produces signed images consumed by both pipelines above.

The mobile pipelines (iOS Fastlane match/gym/pilot, Android `gradlew assembleRelease` + Fastlane supply) live in `references/mobile-pipelines.md`, `references/ios-fastlane-pipeline.md`, and `references/android-pipeline.md`.

## Branch strategy and semantic versioning

- GitHub Flow (default for SaaS web/API): long-lived `main`, short feature branches merged via PR, deploys from `main`.
- Trunk-based (10+ engineers): very short branches (< 1 day), feature flags hide unfinished work, `main` always releasable.
- Release branches (mobile, firmware, versioned SDKs): `main` for ongoing work, `release/v1.2` cut and tagged for ship.

Pick one per repo and document in `CONTRIBUTING.md`. Conventional commits drive `semantic-release` for tag, CHANGELOG, GitHub Release, npm publish on merge to `main` (`feat:` → minor, `fix:` → patch, `feat!:` or `BREAKING CHANGE:` → major). Config lives in `.releaserc.json`.

## Verification

- Every workflow PR is reviewed by someone other than the author; `actionlint` is a required status check on any `.github/workflows/*.yml` change.
- Track DORA metrics off the deployment-record sink; alert when change-failure rate or queue time p95 breach the SLO.
- Claude Code and Codex users on the same repo work from the same files — nothing platform-specific in workflow YAML.

## Companion Skills

- `references/cicd-pipeline-design.md` — high-level pipeline shape, stage boundaries, gate design, FinOps.
- `references/cicd-devsecops.md` — secrets policy, Vault server architecture, scan thresholds, exception governance.
- `references/cicd-jenkins-debian.md` — when the CI server is Jenkins, not GitHub Actions or GitLab CI.
- `deployment-release-engineering` — rollout, canary, blue/green, post-deploy verification.
- `kubernetes-platform` reference `references/kubernetes-saas-delivery.md` — ArgoCD GitOps for multi-tenant SaaS.
- `observability-monitoring` — deploy markers, SLO burn, MTTR, dashboards.
- `cloud-architecture` — traffic-shifting plumbing for the deployment strategies invoked here.
- `ios-development`, `android-development` — app build config upstream of the mobile pipelines.

## Sources

- Continuous Delivery, Humble & Farley, Addison-Wesley, 2010, ISBN 978-0-321-60191-9.
- The DevOps Handbook, 2nd ed., Kim, Humble, Debois, Willis, IT Revolution, 2021, ISBN 978-1-950508-40-2.
- GitHub Actions docs: [docs.github.com/actions](https://docs.github.com/actions); Reusing workflows: [docs.github.com/en/actions/using-workflows/reusing-workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows).
- Automatic token authentication: [docs.github.com/en/actions/security-guides/automatic-token-authentication](https://docs.github.com/en/actions/security-guides/automatic-token-authentication).
- GitLab CI docs: [docs.gitlab.com/ci](https://docs.gitlab.com/ci); Docker Build cache: [docs.docker.com/build/cache](https://docs.docker.com/build/cache).
- Trivy: [aquasecurity.github.io/trivy](https://aquasecurity.github.io/trivy); semantic-release: [semantic-release.gitbook.io](https://semantic-release.gitbook.io); Fastlane: [docs.fastlane.tools](https://docs.fastlane.tools).

