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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Release evidence | Pipeline configuration record | Markdown doc covering build, test, deploy stages plus secret references | `docs/ci/pipeline-config.md` |
| Release evidence | Latest release run evidence | CI URL plus archived log of the most recent successful release | `docs/ci/release-run-2026-04-16.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
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
