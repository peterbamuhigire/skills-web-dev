# CI/CD Anti-Patterns: Broken vs Fixed

Each entry shows the broken example, the failure mode, and the fix.

## 1. Echoing secrets

Broken:

```yaml
- run: echo "Token is $TOKEN — calling $URL?key=$TOKEN"
```

Failure: GitHub redacts known secret values, but constructed strings (URL with embedded token, base64-encoded blob, JSON `{"key":"$TOKEN"}`) bypass the redactor and land in run logs.

Fix:

```yaml
- run: curl -fsS -H "Authorization: Bearer $TOKEN" "$URL"
  env: { TOKEN: ${{ secrets.API_TOKEN }} }
```

Pass the secret via the env block, never interpolate into a shell-quoted string the runner will print.

## 2. Cache poisoning

Broken:

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-npm
```

Failure: every PR shares the same cache key. A malicious PR (or just a stale lockfile) writes bad content; subsequent builds restore it. Builds become non-deterministic.

Fix:

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
    restore-keys: ${{ runner.os }}-npm-
```

Lockfile hash in the key. PRs from forks should not be allowed to write the cache (`actions/cache` already restricts this — do not work around it).

## 3. The mega-workflow

Broken: one `ci.yml` with 50 jobs, 800 lines, mixing PR checks, release, security scan, and infra apply. Edits collide, reviewers cannot reason about it, partial failures are unclear.

Fix: split per concern — `pr-checks.yml`, `release.yml`, `security-scan.yml`, `infra-apply.yml`. Share steps via a reusable workflow (`reusable-node-ci.yml`) called with `uses:` and inputs.

## 4. Missing `permissions:` block

Broken:

```yaml
jobs:
  deploy:
    runs-on: ubuntu-24.04
    steps: [...]
```

Failure: on older repos `GITHUB_TOKEN` defaults to write-all. A compromised step can push to `main`, edit issues, or create releases.

Fix: always pin per workflow, narrow per job:

```yaml
permissions: { contents: read }

jobs:
  release:
    permissions: { contents: write, id-token: write }
```

Set the org default to "Restricted" so new repos start from least-privilege.

## 5. No concurrency on production

Broken: two merges to `main` within 30 seconds → two deploy jobs assume the same role, race on `kubectl apply`, leave the cluster in a mixed state.

Fix:

```yaml
concurrency:
  group: deploy-prod-${{ github.workflow }}
  cancel-in-progress: false
```

`cancel-in-progress: false` is mandatory for production — the second run waits, never cancels mid-rollout. Use `true` only for PR previews.

## 6. Rebuilding per environment

Broken: separate build jobs in `deploy-staging.yml` and `deploy-prod.yml`. Staging passes, production builds slightly different code (different cache state, different time-of-day, different transitive dep), production fails or — worse — diverges silently.

Fix: build once on merge to `main`, output the digest, promote the same digest through every environment via `workflow_dispatch` with an `image_digest` input.

## 7. Pinning actions to mutable tags

Broken: `uses: third-party/action@v1`. Tag is mutable; the publisher (or a compromised account) repoints `v1` to a malicious commit.

Fix: pin to a full commit SHA on any security-sensitive path:

```yaml
- uses: third-party/action@a1b2c3d4e5f6...   # v1.4.2
```

Dependabot keeps the SHA fresh. First-party actions (`actions/checkout`, `aws-actions/*`) at major-tag is acceptable; everything else gets the SHA.

## 8. Logging the entire environment

Broken: `- run: env` in a debug step. GitHub redacts known secrets but environment-encoded credentials (a Vault token vended into `VAULT_TOKEN`) may slip through depending on registration order.

Fix: `printenv | grep -v -i -E '(token|secret|key|password)'` if you must dump env. Better: ship structured logs to the platform observability backend, not the run log.
