# GitHub Actions CI/CD — Overview Reference

This reference covers workflow file structure for cloud deployment from GitHub Actions. Pipeline depth, gates, matrix strategy, reusable workflows, and DevSecOps controls live in `cicd-pipelines` and `cicd-devsecops`.

## Workflow File Structure

Workflow files live in `.github/workflows/*.yml`. Top-level keys:

| Key | Purpose |
|-----|---------|
| `name` | Workflow display name in the Actions UI. |
| `on` | Triggering events (`push`, `pull_request`, `schedule`, `workflow_dispatch`, `release`). |
| `permissions` | Modifies default permissions on `GITHUB_TOKEN` — set least-privilege explicitly. |
| `env` | Workflow-wide environment variables. |
| `defaults` | Default settings applied to all jobs (shell, working directory). |
| `concurrency` | Cancel-in-progress group; prevents overlapping deploys to the same environment. |
| `jobs` | One or more jobs, parallel by default; each requires `runs-on` and `steps`. |

Source: GitHub Actions workflow syntax docs (`docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions`, fetched 2026-05-01).

## Reference Workflow — Build, Test, Push, Deploy to VPS

```yaml
name: ci-cd
on:
  push: { branches: [main] }
permissions:
  contents: read
  packages: write
concurrency:
  group: deploy-prod
  cancel-in-progress: false
jobs:
  build-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: npm }
      - run: npm ci
      - run: npm test
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:sha-${{ github.sha }}

  deploy-vps:
    needs: build-test
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.VPS_HOST }}
          username: deploy
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /srv/app
            docker compose pull
            docker compose up -d --remove-orphans
            docker image prune -f
```

## Secrets Discipline

- Store only short-lived deploy credentials (SSH keys, registry tokens) in GitHub Actions secrets.
- Long-lived secrets (database passwords, third-party API keys) live in Vault. The runtime pulls them at boot via Vault Agent or `vault kv get` against the appropriate role — covered in `cicd-devsecops`.
- Tag tags with the immutable git SHA (`:sha-<git-sha>`) plus an environment alias (`:prod`); never deploy `:latest` to production.
- Use `environment: production` on deploy jobs to gate via required reviewers and environment secrets.

## Cloud Targets

| Target | Approach |
|--------|----------|
| Debian/Ubuntu VPS | SSH action runs `docker compose pull && up -d` against the host. |
| ECS Fargate | `aws ecs update-service --force-new-deployment` after image push. |
| Lambda | `aws lambda update-function-code --image-uri` for container Lambdas. |
| Kubernetes | `kubectl set image` or ArgoCD sync — defer to `kubernetes-platform`. |
