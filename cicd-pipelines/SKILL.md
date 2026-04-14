---
name: cicd-pipelines
description: Use when implementing GitHub Actions pipelines for web, API, and mobile apps — Node.js/PHP build and deploy, iOS TestFlight via Fastlane, Android Google Play via Supply, environment promotion, OIDC secrets, caching, and rollback.
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
- The repository ships software that must move from commit to production through reviewable, versioned workflow files.

## Do Not Use When

- The task is only pipeline architecture and governance — use `cicd-pipeline-design` for the higher-level structure first.
- Security gate policy is the subject — use `cicd-devsecops` for secrets, scan policy, and compliance gates.
- The pipeline target is Jenkins — use `cicd-jenkins-debian`.

## Required Inputs

- Languages and build tools in the repository (Node.js/npm, PHP/Composer, Gradle, Xcode, Python/pip, etc.).
- Target platforms: web host, container registry, TestFlight, Play Console, static CDN.
- Secret store posture: GitHub OIDC federation to AWS/GCP, environment-scoped secrets, external Vault integration.
- Branch and environment model: trunk-based vs release branches, dev/staging/prod environments.
- Rollback expectation: manual, automatic-on-health-fail, both.

## Workflow

1. Inventory runtime stacks and the artefacts each produces (Docker image, AAB, IPA, static bundle, deb package).
2. Set up GitHub Environments for `dev`, `staging`, and `production` with protection rules and required reviewers.
3. Wire OIDC to the cloud provider — remove any long-lived access keys from repo secrets.
4. Build language-specific workflows using reusable workflows and caches.
5. Promote artefacts by digest between environments — do not rebuild per environment.
6. Gate production with manual approval plus automated smoke tests.
7. Add automatic rollback on health-check failure and a documented manual rollback workflow.
8. Emit a deployment record and notification to the release channel on success or failure.

## Quality Standards

- Every workflow file is linted (`actionlint`) and the entire tree passes `workflow_call` reusability checks.
- Every job uses the minimum `permissions:` block required — never the default all-write token.
- Secrets pulled via OIDC federation or environment-scoped secrets. No `AWS_ACCESS_KEY_ID` in repo secrets.
- Every artefact is tagged with the full commit SHA and an immutable digest before promotion.
- Every pipeline writes a signed deployment record consumable by the audit log.

## Anti-Patterns

- Long-lived cloud keys stored in `secrets.AWS_*` — always prefer OIDC.
- Branch-per-environment deployments where `staging` and `main` drift apart.
- Rebuilding the same artefact for each environment instead of promoting by digest.
- Pinning actions by tag alone (`@v4`) instead of by SHA for security-critical jobs.
- Inline scripts that grow to hundreds of lines inside a single step — extract to a repo script.
- Uploading signing keys into repo secrets as base64 blobs when a keychain service or Match repo is available.

## Outputs

- One or more `.github/workflows/*.yml` files producing the required builds and deployments.
- A `release.yml` or equivalent that promotes artefacts through environments with gates.
- A written rollback runbook linked from the repo README.
- A deployment record schema and sink (S3, CloudWatch, Datadog, Slack, etc.).

## References

- [references/github-actions-workflows.md](references/github-actions-workflows.md): Copy-paste YAML templates for Node.js, PHP, Docker, and reusable workflows.
- [references/ios-fastlane-pipeline.md](references/ios-fastlane-pipeline.md): Fastlane lanes for test/beta/release + Match code signing.
- [references/android-pipeline.md](references/android-pipeline.md): Gradle build, unit tests, signed AAB, Google Play via Supply.
<!-- dual-compat-end -->

## Load Order

1. Load `world-class-engineering` and `git-collaboration-workflow` for the baseline.
2. Load `cicd-pipeline-design` for the high-level pipeline shape.
3. Load this skill for GitHub Actions, Fastlane, and environment promotion specifics.
4. Pair with `cicd-devsecops` for secrets and scan policy, `deployment-release-engineering` for rollout, `observability-monitoring` for post-deploy verification, `cloud-architecture` for the target infrastructure shape.

## Executable Outputs

- reusable workflow file with versioned inputs and outputs
- environment-specific deploy workflows (`deploy-dev.yml`, `deploy-staging.yml`, `deploy-prod.yml`)
- Fastlane `Fastfile` for iOS and Android when mobile apps ship
- OIDC role trust policy and least-privilege IAM policy
- rollback workflow (`rollback.yml`) triggered manually with artefact-digest input
- signed deployment record schema and example

## GitHub Actions — Core Rules

### Structure

- Top-level `name:` is human-readable; the filename is the stable reference (`build-web.yml`).
- Triggers are explicit: `on: push`, `pull_request`, `workflow_dispatch`, `schedule`, `release`, or `workflow_call` for reusables.
- Jobs run on `ubuntu-latest` by default; pin to `ubuntu-24.04` for reproducibility on security-critical paths.
- `concurrency` blocks guarantee no two runs of the same workflow race on the same environment.

```yaml
concurrency:
  group: deploy-${{ github.ref }}-${{ matrix.environment }}
  cancel-in-progress: false
```

### Permissions

Every workflow starts with an explicit minimum:

```yaml
permissions:
  contents: read
  id-token: write   # for OIDC
  packages: read
```

Add other scopes (`pull-requests: write`, `issues: write`) only when a job needs them.

### Secrets

- Repo secrets for unscoped values.
- Environment secrets for environment-scoped values (production DB URL, Play service account, Apple API key).
- OIDC federation for cloud providers. No static `AWS_ACCESS_KEY_ID` in any repo.
- For Vault integration, use `hashicorp/vault-action` with OIDC auth.

### OIDC to AWS (Node.js deploy)

```yaml
permissions:
  id-token: write
  contents: read

steps:
  - uses: actions/checkout@v4

  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789012:role/github-actions-deploy
      aws-region: eu-west-1

  - run: aws sts get-caller-identity
```

### Caching

- Node: `actions/cache` keyed on `package-lock.json`; restore `~/.npm`.
- Gradle: `actions/cache` on `~/.gradle/caches` and `~/.gradle/wrapper`.
- CocoaPods: `actions/cache` on `Pods/` keyed on `Podfile.lock`.
- pip: `actions/cache` on `~/.cache/pip` keyed on `requirements*.txt`.
- Docker buildx: `type=gha` cache with `mode=max`.

See `references/github-actions-workflows.md` for full caching snippets.

## Language Pipelines

### Node.js

```
install → lint → test → build → docker build → push ECR → deploy
```

- Use `npm ci` for reproducibility.
- Run typecheck and lint in parallel jobs to shorten the critical path.
- Tests and coverage go to an artefact uploaded on every run.
- Docker image tagged with commit SHA + semver tag for release builds.

### PHP

```
composer install → PHPStan → PHPUnit → rsync/ssh deploy
```

- Composer cache keyed on `composer.lock`.
- PHPStan at level 8 or agreed baseline; PHPUnit runs against a containerised DB.
- Deploy via `rsync -avz --delete` or a containerised image.

### Docker

- One image per service; pushed to ECR/GCR/GHCR by digest.
- Multi-platform (`linux/amd64,linux/arm64`) only when the runtime actually differs; do not do it by reflex.

## Environment Promotion

```
feature branch → pull request checks → merge to main → build+push once →
deploy dev → automated tests → deploy staging → manual approval → deploy prod
```

Rules:

- Build the artefact once. Promote the digest. Never rebuild for staging or prod.
- `production` environment requires a human reviewer and a passing staging smoke test.
- Promotion actions are `workflow_dispatch` inputs (`image_digest`), not free-form shell.

```yaml
jobs:
  deploy:
    environment:
      name: production
      url: https://app.example.com
    runs-on: ubuntu-24.04
    steps: ...
```

Add a scheduled staging re-deploy (nightly or weekly) to catch drift between what is in `main` and what is actually live.

## Rollback

### Automatic

- Post-deploy health checks fail → revert service to previous task definition / deployment revision.
- ALB target-health drops below threshold for 3 consecutive minutes → trigger `rollback.yml`.

### Manual

`rollback.yml` accepts `image_digest` and environment as inputs, assumes the OIDC role, and re-deploys without a build step. Keep the trigger authenticated and audited.

### Rollback Does Not Restart a Broken Deploy Loop

Record a reason on rollback. If three rollbacks happen inside a week for the same service, freeze deploys and investigate — do not keep re-deploying hoping the next one works.

## Verification

- Every workflow PR must be reviewed by someone other than the author.
- Run `actionlint` as a required status check.
- Track DORA metrics (deploy frequency, lead time, change-failure rate, MTTR) off the deployment record sink.

## Platform Notes

- Claude Code users: GitHub Actions workflows can be generated and validated locally with `actionlint` via the CLI. Codex users on the same repo work from the same files — nothing platform-specific goes in workflow YAML.

## References

- [references/github-actions-workflows.md](references/github-actions-workflows.md): Node.js, PHP, Docker, and reusable workflow templates.
- [references/ios-fastlane-pipeline.md](references/ios-fastlane-pipeline.md): TestFlight and App Store release lanes with Match.
- [references/android-pipeline.md](references/android-pipeline.md): Signed AAB + Play Console release via Fastlane Supply.
- GitHub Actions docs: [docs.github.com/actions](https://docs.github.com/actions)
- Fastlane docs: [docs.fastlane.tools](https://docs.fastlane.tools)
