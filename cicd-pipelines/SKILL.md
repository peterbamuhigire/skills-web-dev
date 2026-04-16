---
name: cicd-pipelines
description: Use when implementing GitHub Actions pipelines for web, API, and mobile
  apps — Node.js/PHP build and deploy, iOS TestFlight via Fastlane, Android Google
  Play via Supply, environment promotion, OIDC secrets, caching, and rollback.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# CI/CD Pipelines

<!-- dual-compat-start -->
## Use When

- Use when implementing GitHub Actions pipelines for web, API, and mobile apps — Node.js/PHP build and deploy, iOS TestFlight via Fastlane, Android Google Play via Supply, environment promotion, OIDC secrets, caching, and rollback.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `cicd-pipelines` or would be better handled by a more specific companion skill.
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

1. Load `world-class-engineering` and `git-collaboration-workflow` for the baseline.
2. Load `cicd-pipeline-design` for the high-level pipeline shape.
3. Load this skill for GitHub Actions, Fastlane, and environment promotion specifics.
4. Pair with `cicd-devsecops` for secrets and scan policy, `deployment-release-engineering` for rollout, `observability-monitoring` for post-deploy verification, `cloud-architecture` for the target infrastructure shape.

## Executable Outputs

- reusable workflow with versioned inputs/outputs; environment-specific deploy workflows (`deploy-dev.yml`, `deploy-staging.yml`, `deploy-prod.yml`)
- Fastlane `Fastfile` for iOS and Android when mobile apps ship
- OIDC role trust policy, least-privilege IAM policy, rollback workflow (`rollback.yml`), signed deployment record

## Pipeline Design Principles

- Fast feedback: unit tests and lint under 60 seconds on PR; slower jobs run in a follow-up stage, not the PR gate.
- Fail fast: lint and type-check before tests; tests before Docker build; Docker build before deploy. Cheap signals block expensive steps.
- Build once, deploy many: a single artefact (Docker digest, signed AAB, `.ipa`, tarball) produced on merge to `main` and promoted through every environment — never rebuild per environment.
- Same binary everywhere: environment differences live in configuration and secrets, not images; digests are identical across dev, staging, production.
- Immutable builds: no mutable tags like `latest` in production. Every deploy references a digest (`sha256:...`) or a signed semver tag; rollback is re-deploying an older digest.
- Every run emits a deployment record (git SHA, image digest, environment, actor, timestamp) to an append-only store for audit and DORA metrics.

## GitHub Actions Fundamentals

- Workflow files live in `.github/workflows/*.yml`. Filename is the stable reference; `name:` is human-readable.
- Triggers: `push` for branch builds, `pull_request` for PR gates, `workflow_dispatch` for manual runs with inputs, `schedule` for cron, `release` for tag-driven publishes, `workflow_call` for reusable workflows.
- Jobs run in parallel by default; use `needs:` to serialise. Each job gets a fresh runner and must restore its own cache and checkout its own code.
- Steps run sequentially inside a job. `uses:` calls a reusable action (pin to full SHA on security-critical paths); `run:` executes shell.
- Matrix, concurrency, and permissions:

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

## Secrets & Environment Variables

- Repository secrets: unscoped values reused across workflows (`CODECOV_TOKEN`).
- Environment secrets: scoped to a GitHub Environment (`dev`, `staging`, `production`). Production secrets never leak into PR builds.
- Organisation secrets: shared across repos (e.g., ECR pull credentials). Use sparingly.
- Environment protection rules gate promotion. Configure `required_reviewers`, `wait_timer`, and deployment-branches in the environment settings UI, then reference in YAML:

```yaml
jobs:
  deploy-prod:
    environment: { name: production, url: https://app.example.com }
    runs-on: ubuntu-24.04
    steps:
      - run: echo "deploying"
```

- OIDC to AWS is mandatory. No static `AWS_ACCESS_KEY_ID` anywhere. Configure a trust policy on the IAM role restricting `sub` to the intended repo and branch:

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

- HashiCorp Vault: `hashicorp/vault-action` with JWT/OIDC. GCP: `google-github-actions/auth@v2` with Workload Identity Federation.

## Node.js / PHP Pipeline

Complete workflow: lint → type-check → unit tests → build Docker → push to ECR → deploy to ECS. For PHP, swap the install and test steps for `composer install --no-dev` and `vendor/bin/phpunit`.

```yaml
name: build-and-deploy-api

on:
  push: { branches: [main] }
  pull_request:

concurrency: { group: api-${{ github.ref }}, cancel-in-progress: true }
permissions: { contents: read, id-token: write, packages: read }

jobs:
  lint-typecheck:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'npm' }
      - run: npm ci
      - run: npm run lint && npm run typecheck

  unit-tests:
    needs: lint-typecheck
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'npm' }
      - run: npm ci && npm test -- --coverage
      - uses: actions/upload-artifact@v4
        with: { name: coverage, path: coverage/ }
  build-and-push:
    needs: unit-tests
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    outputs: { image: ${{ steps.push.outputs.image }} }
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with: { role-to-assume: arn:aws:iam::123456789012:role/github-actions-ecr, aws-region: eu-west-1 }
      - uses: aws-actions/amazon-ecr-login@v2
        id: ecr
      - uses: docker/setup-buildx-action@v3
      - id: push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.ecr.outputs.registry }}/api:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
  deploy-ecs:
    needs: build-and-push
    runs-on: ubuntu-24.04
    environment: { name: production, url: https://api.example.com }
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with: { role-to-assume: arn:aws:iam::123456789012:role/github-actions-deploy, aws-region: eu-west-1 }
      - run: aws ecs update-service --cluster prod --service api --force-new-deployment
```

For EC2 via SSM replace the ECS step with `aws ssm send-command --document-name AWS-RunShellScript`.

## Next.js Pipeline

Type-check → Playwright E2E (see the `e2e-testing` skill for test authoring) → build → deploy to Vercel or Kubernetes.

```yaml
name: nextjs-release

on:
  push: { branches: [main] }
  pull_request:

permissions: { contents: read, id-token: write }

jobs:
  typecheck:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'npm' }
      - run: npm ci && npm run typecheck

  e2e:
    needs: typecheck
    runs-on: ubuntu-24.04
    strategy:
      fail-fast: false
      matrix: { shard: [1/4, 2/4, 3/4, 4/4] }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'npm' }
      - run: npm ci && npx playwright install --with-deps chromium
      - run: npx playwright test --shard=${{ matrix.shard }}
  deploy-vercel:
    needs: e2e
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    environment: { name: production, url: https://app.example.com }
    steps:
      - uses: actions/checkout@v4
      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

For Kubernetes targets swap the Vercel step for `kubectl apply -f k8s/ --record` after `aws eks update-kubeconfig --name prod`.

## Docker Build & Push

Multi-platform only when the runtime differs (ARM Graviton, Apple Silicon dev boxes) — it doubles build time. Cache via `type=gha` with `mode=max`. Push to ECR via OIDC; never commit registry passwords.

```yaml
- uses: docker/setup-qemu-action@v3
- uses: docker/setup-buildx-action@v3
- uses: aws-actions/configure-aws-credentials@v4
  with: { role-to-assume: arn:aws:iam::123456789012:role/github-actions-ecr, aws-region: eu-west-1 }
- uses: aws-actions/amazon-ecr-login@v2
  id: ecr
- uses: docker/build-push-action@v5
  with:
    context: .
    platforms: linux/amd64,linux/arm64
    push: true
    tags: ${{ steps.ecr.outputs.registry }}/api:${{ github.sha }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
    provenance: true
    sbom: true
```

## Kubernetes Deployment

Option A — direct `kubectl apply` from GitHub Actions. Assume an IAM role mapped to a Kubernetes RBAC binding, update kubeconfig, apply:

```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with: { role-to-assume: arn:aws:iam::123456789012:role/github-actions-eks, aws-region: eu-west-1 }
- uses: azure/setup-kubectl@v4
  with: { version: 'v1.30.0' }
- run: aws eks update-kubeconfig --name prod-cluster --region eu-west-1
- run: |
    kubectl set image deployment/api api=${{ needs.build-and-push.outputs.image }} -n production
    kubectl rollout status deployment/api -n production --timeout=5m
```

Option B (recommended for multi-cluster SaaS) — ArgoCD Image Updater watches the registry and updates the Git manifest when a new semver tag appears. CI only builds and pushes; ArgoCD reconciles. No cluster credentials live in CI. Pair with `kubernetes-saas-delivery` for the full GitOps pattern.

## Environment Promotion

- Flow: feature branch → PR checks → merge to `main` → build and push once → deploy `dev` → smoke tests → deploy `staging` → manual approval → deploy `production`.
- Each environment is a GitHub Environment with its own secrets and protection rules; production requires `required_reviewers` and restricts deploy branches to `main`.
- Promotion is a `workflow_dispatch` with an `image_digest` input — never rebuilds.

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
    strategy:
      matrix: { cluster: [cluster-a, cluster-b] }
    steps:
      - run: echo "Deploying ${{ inputs.image_digest }} to ${{ inputs.target }}/${{ matrix.cluster }}"
```

- Nightly scheduled staging re-deploy detects drift between `main` HEAD and live.

## Test Parallelisation

Playwright shards run in parallel via matrix and merge reports at the end:

```yaml
jobs:
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
        with:
          name: blob-report-${{ strategy.job-index }}
          path: blob-report
          retention-days: 1

  merge-reports:
    if: always()
    needs: [e2e]
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'npm' }
      - run: npm ci
      - uses: actions/download-artifact@v4
        with: { path: reports, pattern: blob-report-*, merge-multiple: true }
      - run: npx playwright merge-reports --reporter=html ./reports
```

- Jest: `jest --shard=1/4` across a matrix, or `--maxWorkers=50%` on a single large runner.
- Report merging is mandatory — reviewers need a single HTML report, not four.

## Mobile Pipelines (iOS and Android)

Full iOS and Android CI/CD details live in `references/mobile-pipelines.md` (plus `references/ios-fastlane-pipeline.md` and `references/android-pipeline.md`). Headlines:

- iOS: Fastlane `match` for code signing (read-only in CI), `gym` to build, `pilot`/`deliver` to upload. Runs on `macos-14` with Xcode 15+.
- Android: `./gradlew assembleRelease` with keystore base64-decoded from a GitHub Secret; upload via Fastlane `supply` or `r0adkll/upload-google-play@v1`.
- Both flows tag `v1.2.3` and promote a single signed artefact to TestFlight/internal-track first, then staged rollout.

## Branch Strategy

- GitHub Flow (default for SaaS web/API): long-lived `main`, short feature branches merged via PR, deploys from `main`. Every merge is a potential production deploy; best when shipping multiple times per day.
- Trunk-based (10+ engineers): very short-lived branches (< 1 day), feature flags hide unfinished work, `main` always releasable. Pair with LaunchDarkly/Unleash/Flagsmith to decouple deploy from release.
- Release branches (mobile, firmware, versioned SDKs): `main` holds ongoing work; `release/v1.2` is cut, stabilised, tagged `v1.2.0`, shipped. Hotfixes land in the release branch and cherry-pick back to `main`.
- Pick one per repo and document in `CONTRIBUTING.md`; mixing strategies confuses reviewers and breaks automation.

## Semantic Versioning

- Conventional commits drive version bumps: `feat:` → minor, `fix:` → patch, `feat!:` or `BREAKING CHANGE:` in body → major, `chore:`/`docs:`/`refactor:` → no release.
- `semantic-release` automates tag, CHANGELOG, GitHub Release, and npm publish on merge to `main`:

```yaml
name: release
on:
  push: { branches: [main] }
permissions: { contents: write, issues: write, pull-requests: write, id-token: write }
jobs:
  release:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0, persist-credentials: false }
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'npm', registry-url: 'https://registry.npmjs.org' }
      - run: npm ci && npx semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

- Config lives in `.releaserc.json` with plugins: `commit-analyzer`, `release-notes-generator`, `changelog`, `npm`, `github`, `git`.

## Artefact Caching

`actions/cache@v4` caches directories keyed on a lockfile hash — the key changes when the lockfile changes, invalidating the cache:

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
    restore-keys: ${{ runner.os }}-npm-
```

- Targets: `~/.npm`, `~/.cache/pnpm`, `~/.cache/composer`, `~/.gradle/caches` + `~/.gradle/wrapper`, `Pods/` (keyed on `Podfile.lock`), `~/.cargo/registry` + `target/`, `~/.cache/pip` (keyed on `requirements*.txt`).
- Docker buildx: `type=gha` with `mode=max` stores all intermediate layers. Cache size limit: 10 GB per repo total — evict old caches via `gh cache delete`.
- `setup-node` / `setup-python` / `setup-java` have a built-in `cache:` parameter — prefer it when the lockfile is at the repo root.

## Slack/Email Notifications

Failure alerts to a Slack channel via `slackapi/slack-github-action`:

```yaml
- name: Notify Slack on failure
  if: failure()
  uses: slackapi/slack-github-action@v1.26.0
  with:
    channel-id: 'C012ABCDEF'
    slack-message: |
      Failed: ${{ github.workflow }} / ${{ github.ref }} / ${{ github.actor }}
      ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
  env:
    SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}
```

- Deployment announcements include the deploy URL, image digest, and actor. Post to `#deploys` on success, `#incidents` on failure.
- Email via `dawidd6/action-send-mail` or an SMTP relay — reserve for on-call paging; Slack covers day-to-day.
- PR status uses GitHub's built-in check runs; do not duplicate pass/fail into Slack for every PR.

## Security Scanning in CI

Trivy scans Docker images for OS and language CVEs. Fail on HIGH or CRITICAL:

```yaml
- uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ steps.ecr.outputs.registry }}/api:${{ github.sha }}
    format: sarif
    output: trivy-results.sarif
    severity: HIGH,CRITICAL
    exit-code: '1'
- uses: github/codeql-action/upload-sarif@v3
  if: always()
  with: { sarif_file: trivy-results.sarif }
```

- Dependency audit: `npm audit --audit-level=high`, `composer audit`, `pip-audit`, `bundle-audit` — run on every PR.
- SAST gate: CodeQL (free for public, GHAS for private) or Snyk Code. CodeQL runs weekly on `main` and on every PR.
- Secret scanning: GitHub's native scanner plus `gitleaks` on PRs. Rotate any leaked secret immediately — removing the commit does not help once pushed.
- CVE exceptions live in a tracked `.trivyignore` with a reason and expiry date. Renew quarterly.
- See `cicd-devsecops` for policy, gating thresholds, and exception governance.

## Rollback

- Automatic: post-deploy health checks failing, ALB target-health dropping below threshold for 3 consecutive minutes, or error-rate SLO burn triggers `rollback.yml`.
- Manual `rollback.yml` takes `image_digest` and `environment` inputs, assumes the OIDC role, re-deploys without a build step.
- Record a reason on every rollback. Three rollbacks in a week on the same service freezes deploys until a post-mortem is filed.

## Verification & Platform Notes

- Every workflow PR must be reviewed by someone other than the author; `actionlint` is a required status check on any `.github/workflows/*.yml` change.
- Track DORA metrics (deploy frequency, lead time, change-failure rate, MTTR) off the deployment-record sink.
- Claude Code and Codex users on the same repo work from the same files — nothing platform-specific goes in workflow YAML.

## Companion Skills

- `cicd-pipeline-design` — high-level pipeline shape, stage boundaries, gate design.
- `cicd-devsecops` — secrets policy, scan thresholds, exception governance.
- `cicd-jenkins-debian` — when the CI server is Jenkins, not GitHub Actions.
- `deployment-release-engineering` — rollout, canary, blue/green, post-deploy verification.
- `kubernetes-saas-delivery` — ArgoCD GitOps for multi-tenant SaaS.
- `observability-monitoring` — deploy markers, error-rate SLO burn, MTTR.
- `ios-development`, `android-development` — app build config upstream of the pipeline.

## Sources

- [references/github-actions-workflows.md](references/github-actions-workflows.md): Node.js, PHP, Docker, reusable workflow templates.
- [references/ios-fastlane-pipeline.md](references/ios-fastlane-pipeline.md): TestFlight and App Store release lanes with Match.
- [references/android-pipeline.md](references/android-pipeline.md): Signed AAB + Play Console release via Fastlane Supply.
- [references/mobile-pipelines.md](references/mobile-pipelines.md): iOS + Android CI/CD overview, Fastfile snippets, `macos-14` runner setup.
- GitHub Actions: [docs.github.com/actions](https://docs.github.com/actions); Fastlane: [docs.fastlane.tools](https://docs.fastlane.tools)
- Trivy: [aquasecurity.github.io/trivy](https://aquasecurity.github.io/trivy); semantic-release: [semantic-release.gitbook.io](https://semantic-release.gitbook.io)
