# GitHub Actions vs GitLab CI

Both engines support the same release-pipeline patterns. Choose based on where the source already lives, the runner story, and the secret-management posture.

## Comparative table

| Concern | GitHub Actions | GitLab CI |
|---------|----------------|-----------|
| Configuration file | `.github/workflows/*.yml` (multiple files) | `.gitlab-ci.yml` (single root file, with `include:`) |
| Reuse primitive | Reusable workflows (`workflow_call`) + composite actions | `include:` + reusable components (`spec:`/`inputs:`) |
| Job graph | Explicit DAG via `needs:` | Stages-then-jobs (DAG via `needs:` available) |
| Variables / secrets | Repo / env / org secrets, OIDC, `secrets: inherit` | CI/CD variables (masked, protected, environment-scoped), OIDC ID tokens |
| Runners | GitHub-hosted + self-hosted; runner groups | GitLab-hosted (gitlab.com) + self-managed; tag-based dispatch |
| Environments | Built-in, with required reviewers + deploy-branch policy | Built-in, with protected environments + approval rules |
| Marketplace | Actions Marketplace | CI/CD Catalog (components) |
| Secrets to cloud | OIDC → AWS / GCP / Vault | OIDC ID token → AWS / GCP / Vault |
| Caching | `actions/cache` + setup-action built-ins | `cache:` keyword keyed on file hash |
| Container build | `docker/build-push-action` + BuildKit | Built-in with `docker:dind` or Buildah |
| Pricing model | Per-minute on hosted runners | Per-minute on hosted runners (CI minutes) |

## When to choose GitHub Actions

- Source already lives on GitHub.com or GitHub Enterprise.
- Heavy use of the marketplace (`actions/checkout`, `aws-actions/*`, `docker/*`).
- Mobile pipelines that need `macos-14` hosted runners.
- Per-environment secrets and required-reviewer protection rules are a fit.

## When to choose GitLab CI

- Source already lives in GitLab CE / EE (self-managed in this repo's stack).
- One-file pipeline preference; auditors who want a single root config.
- Need integrated container registry, package registry, and Pages on the same instance without third-party stitching.
- Self-managed runners on Debian/Ubuntu where the GitLab Runner agent's tag-based dispatch and resource groups fit the existing platform.

## Migration notes

- `jobs.<id>.steps[*].uses:` → no direct equivalent; replace marketplace actions with `script:` blocks or GitLab CI/CD components.
- Reusable workflow → `include:` + `inputs:` (GitLab components) or `extends:` + anchors.
- `permissions:` block → not needed; GitLab issues a per-job CI/CD job token with configurable scope (Project Access Tokens, `CI_JOB_TOKEN` allowlist).
- OIDC subject claim shape differs — re-derive trust-policy `sub` patterns. GitLab's claim is `project_path:<group>/<project>:ref_type:branch:ref:<ref>`.
- Matrix → `parallel:matrix:` keyword.
- Concurrency → `resource_group:` (single job at a time per group, cluster-wide).

## House rule

For repos in the self-managed Debian/Ubuntu stack (Jenkins + GitLab CE + Nexus 3 + Vault) the canonical engine is GitLab CI on self-managed runners. GitHub Actions is used for repos already on GitHub.com — primarily mobile (iOS hosted `macos-14`) and OSS releases. The patterns in this skill apply to both; only the YAML dialect changes.
