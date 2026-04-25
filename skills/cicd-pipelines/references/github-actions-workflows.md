# GitHub Actions Workflows — Copy-Paste Templates

Production-grade YAML templates for Node.js, PHP, Docker, reusable workflows, and OIDC deploys. Pin action SHAs in security-critical jobs.

## Node.js — Build, Test, Docker, Deploy

`.github/workflows/web.yml`

```yaml
name: web

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

concurrency:
  group: web-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read
  id-token: write

jobs:
  check:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm test -- --coverage
      - uses: actions/upload-artifact@v4
        with:
          name: coverage
          path: coverage/

  build:
    needs: check
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    outputs:
      digest: ${{ steps.push.outputs.digest }}
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-deploy
          aws-region: eu-west-1
      - uses: aws-actions/amazon-ecr-login@v2
        id: ecr
      - uses: docker/setup-buildx-action@v3
      - id: push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          platforms: linux/amd64
          tags: |
            ${{ steps.ecr.outputs.registry }}/web:${{ github.sha }}
            ${{ steps.ecr.outputs.registry }}/web:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-dev:
    needs: build
    runs-on: ubuntu-24.04
    environment: dev
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-deploy
          aws-region: eu-west-1
      - run: |
          aws ecs update-service \
            --cluster dev \
            --service web \
            --force-new-deployment
```

## Reusable Workflow — Deploy

`.github/workflows/_deploy.yml`

```yaml
name: _deploy

on:
  workflow_call:
    inputs:
      environment: { required: true, type: string }
      image_digest: { required: true, type: string }
    secrets:
      aws_role_arn: { required: true }

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-24.04
    environment: ${{ inputs.environment }}
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.aws_role_arn }}
          aws-region: eu-west-1
      - run: |
          aws ecs update-service \
            --cluster ${{ inputs.environment }} \
            --service web \
            --task-definition $(aws ecs register-task-definition --cli-input-json file://task.json --query 'taskDefinition.taskDefinitionArn' --output text) \
            --force-new-deployment
```

Caller:

```yaml
jobs:
  prod:
    uses: ./.github/workflows/_deploy.yml
    with:
      environment: production
      image_digest: sha256:abcd...
    secrets:
      aws_role_arn: ${{ secrets.PROD_DEPLOY_ROLE }}
```

## PHP — Composer, PHPStan, PHPUnit, rsync

`.github/workflows/api.yml`

```yaml
name: api

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  check:
    runs-on: ubuntu-24.04
    services:
      mysql:
        image: mysql:8.4
        env:
          MYSQL_ROOT_PASSWORD: rootpw
          MYSQL_DATABASE: test
        ports: ['3306:3306']
        options: >-
          --health-cmd="mysqladmin ping -prootpw"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=10
    steps:
      - uses: actions/checkout@v4
      - uses: shivammathur/setup-php@v2
        with:
          php-version: '8.3'
          tools: composer
          coverage: pcov
      - uses: actions/cache@v4
        with:
          path: ~/.composer/cache
          key: composer-${{ hashFiles('composer.lock') }}
      - run: composer install --no-progress --prefer-dist --no-interaction
      - run: vendor/bin/phpstan analyse --no-progress
      - env:
          DB_HOST: 127.0.0.1
          DB_PASSWORD: rootpw
        run: vendor/bin/phpunit --coverage-clover coverage.xml

  deploy:
    needs: check
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: webfactory/ssh-agent@v0.9.0
        with:
          ssh-private-key: ${{ secrets.DEPLOY_SSH_KEY }}
      - run: |
          rsync -avz --delete --exclude='.git' \
            ./ deploy@api.example.com:/var/www/api/
          ssh deploy@api.example.com 'sudo systemctl reload php8.3-fpm'
```

## Docker — Build, Scan, Push

```yaml
- uses: docker/setup-buildx-action@v3

- uses: docker/build-push-action@v6
  with:
    context: .
    load: true
    tags: local/web:ci
    cache-from: type=gha
    cache-to: type=gha,mode=max

- uses: aquasecurity/trivy-action@0.24.0
  with:
    image-ref: local/web:ci
    format: sarif
    output: trivy.sarif
    severity: CRITICAL,HIGH
    exit-code: '1'

- uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: trivy.sarif
```

## Caching Recipes

### Node

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '22'
    cache: 'npm'
    cache-dependency-path: '**/package-lock.json'
```

### Gradle

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.gradle/caches
      ~/.gradle/wrapper
    key: gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}
```

### CocoaPods

```yaml
- uses: actions/cache@v4
  with:
    path: Pods
    key: pods-${{ hashFiles('Podfile.lock') }}
```

### Python

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: pip-${{ hashFiles('**/requirements*.txt') }}
```

## Matrix Builds

```yaml
strategy:
  fail-fast: false
  matrix:
    node: ['20', '22']
    os:   [ubuntu-24.04, macos-14]
  max-parallel: 4

runs-on: ${{ matrix.os }}
steps:
  - uses: actions/setup-node@v4
    with: { node-version: ${{ matrix.node }} }
```

## Required Status Checks

In the repository's branch protection:

- `check` (lint + typecheck + test)
- `security` (Trivy + OWASP Dependency-Check)
- `actionlint` (workflow lint)
- For mobile repos: `ios-build`, `android-build`

## Deployment Record Emission

```yaml
- name: Record deployment
  run: |
    aws s3 cp - s3://deploy-records/${{ github.repository }}/${{ github.run_id }}.json <<JSON
    {
      "service": "web",
      "environment": "production",
      "artifact_digest": "${{ needs.build.outputs.digest }}",
      "commit": "${{ github.sha }}",
      "released_by": "github-actions:${{ github.repository }}@${{ github.sha }}",
      "released_at": "${{ github.event.head_commit.timestamp }}"
    }
    JSON
```

## Lint and Verify

- Install `actionlint` and run it as a pre-commit hook.
- Add a `workflows-lint.yml` that runs `actionlint` on every change under `.github/workflows/**`.
- Pin third-party actions by full SHA in any workflow that has `id-token: write` or deploys to production.
