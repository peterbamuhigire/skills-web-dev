# Three Reference Architectures

These pin the patterns from the main skill (matrix, reusable workflows, OIDC, BuildKit cache, environment promotion, deployment strategy) to three concrete shapes. Engine assumption: GitHub Actions on self-managed Debian/Ubuntu runners; switch the `runs-on:` label to migrate to GitLab CI runners or GitHub-hosted runners without changing the job graph.

## A. PHP/MySQL SaaS on Debian VPS (blue/green via Nginx symlink swap)

Stages: composer install → PHPUnit → PHPStan → Trivy on container → push to GHCR → deploy via SSH to Debian VPS, swap Nginx symlink, drain old release.

```yaml
name: php-saas-release
on: { push: { branches: [main] }, pull_request: }
permissions: { contents: read, id-token: write, packages: write }
concurrency: { group: php-${{ github.ref }}, cancel-in-progress: true }

jobs:
  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: shivammathur/setup-php@v2
        with: { php-version: '8.3', tools: composer:v2, coverage: none }
      - run: composer install --no-interaction --prefer-dist --no-progress
      - run: vendor/bin/phpstan analyse --memory-limit=1G
      - run: vendor/bin/phpunit --testdox

  build:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    outputs: { digest: ${{ steps.push.outputs.digest }} }
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with: { registry: ghcr.io, username: ${{ github.actor }}, password: ${{ secrets.GITHUB_TOKEN }} }
      - uses: aquasecurity/trivy-action@master
        with: { scan-type: fs, severity: HIGH,CRITICAL, exit-code: '1' }
      - id: push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          provenance: true
          sbom: true

  deploy-bluegreen:
    needs: build
    runs-on: ubuntu-24.04
    environment: { name: production, url: https://app.example.com }
    steps:
      - uses: hashicorp/vault-action@v3
        with:
          url: https://vault.example.com:8200
          method: jwt
          role: github-actions-php-saas
          secrets: |
            kv/data/php/prod db_password | DB_PASSWORD ;
            ssh/sign/deploy public_key | DEPLOY_SSH_CERT
      - name: Deploy + symlink swap
        run: |
          ssh deploy@vps "set -e
            docker pull ghcr.io/${{ github.repository }}:${{ github.sha }}
            docker run -d --name app-green --env-file /etc/app/prod.env \
              ghcr.io/${{ github.repository }}:${{ github.sha }}
            curl -fsS http://localhost:8081/health
            ln -sfn /etc/nginx/sites-available/app-green.conf /etc/nginx/sites-enabled/app.conf
            nginx -s reload
            sleep 30 && docker rm -f app-blue || true
            docker rename app-green app-blue"
```

Rollback: re-run the deploy job with the previous `image_digest` input — symlink flips back, the old container is recreated from cache.

## B. Node.js/TypeScript Service to Kubernetes (canary)

Stages: pnpm install → vitest → tsc --noEmit → esbuild bundle → BuildKit container → push GHCR → Argo Rollouts canary (10% → 50% → 100% with automated abort on SLO breach). Detailed traffic-shifting plumbing lives in `cloud-architecture`; the pipeline only invokes the rollout and watches the gate.

```yaml
name: ts-service-release
on: { push: { branches: [main] } }
permissions: { contents: read, id-token: write, packages: write }

jobs:
  ci:
    uses: ./.github/workflows/reusable-node-ci.yml
    with: { node-version: '20', package-manager: pnpm }

  build:
    needs: ci
    runs-on: ubuntu-24.04
    outputs: { digest: ${{ steps.push.outputs.digest }} }
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with: { registry: ghcr.io, username: ${{ github.actor }}, password: ${{ secrets.GITHUB_TOKEN }} }
      - id: push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  canary:
    needs: build
    runs-on: ubuntu-24.04
    environment: { name: production }
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with: { role-to-assume: arn:aws:iam::123456789012:role/github-actions-eks, aws-region: eu-west-1 }
      - run: aws eks update-kubeconfig --name prod
      - run: |
          kubectl argo rollouts set image api api=ghcr.io/${{ github.repository }}@${{ needs.build.outputs.digest }}
          kubectl argo rollouts get rollout api --watch --timeout 30m
```

Argo Rollouts AnalysisTemplate watches Prometheus error-rate and p95 latency; SLO breach aborts and reverts automatically.

## C. Container Image Library (multi-arch, signed, SBOM)

Reusable workflow consumed by both pipelines above. Multi-arch BuildKit, SBOM via `anchore/sbom-action` (syft), keyless signing via `cosign` with OIDC.

```yaml
name: container-image
on:
  workflow_call:
    inputs:
      image: { required: true, type: string }
      context: { required: false, type: string, default: '.' }
    outputs:
      digest: { value: ${{ jobs.build.outputs.digest }} }

permissions: { contents: read, id-token: write, packages: write }

jobs:
  build:
    runs-on: ubuntu-24.04
    outputs: { digest: ${{ steps.push.outputs.digest }} }
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-qemu-action@v3
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with: { registry: ghcr.io, username: ${{ github.actor }}, password: ${{ secrets.GITHUB_TOKEN }} }
      - id: push
        uses: docker/build-push-action@v5
        with:
          context: ${{ inputs.context }}
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ghcr.io/${{ inputs.image }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          provenance: true
          sbom: true
      - uses: anchore/sbom-action@v0
        with: { image: ghcr.io/${{ inputs.image }}@${{ steps.push.outputs.digest }}, format: spdx-json }
      - uses: sigstore/cosign-installer@v3
      - run: cosign sign --yes ghcr.io/${{ inputs.image }}@${{ steps.push.outputs.digest }}
```

Consumers verify before deploy: `cosign verify --certificate-identity-regexp '^https://github.com/acme/' ghcr.io/...`.
