# GitHub Actions — Sharded Playwright Workflow

Production-ready workflow that installs deps, caches Playwright browsers, runs tests across a 4-way shard matrix, and uploads HTML reports for any failed shard.

```yaml
# .github/workflows/e2e.yml
name: E2E
on:
  pull_request:
  push:
    branches: [main]
jobs:
  e2e:
    timeout-minutes: 20
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        shard: [1/4, 2/4, 3/4, 4/4]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - name: Cache Playwright browsers
        uses: actions/cache@v4
        with:
          path: ~/.cache/ms-playwright
          key: pw-${{ runner.os }}-${{ hashFiles('package-lock.json') }}
      - run: npx playwright install --with-deps
      - run: npx playwright test --shard=${{ matrix.shard }}
        env:
          BASE_URL: http://localhost:3000
          E2E_USER_EMAIL: ${{ secrets.E2E_USER_EMAIL }}
          E2E_USER_PASSWORD: ${{ secrets.E2E_USER_PASSWORD }}
      - name: Upload HTML report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report-${{ strategy.job-index }}
          path: playwright-report/
          retention-days: 14
```

## Minimal scaffolder workflow

The official `playwright.dev/docs/ci-intro` scaffolder emits a single-job workflow without sharding — useful as a starting point on small repos:

```yaml
name: Playwright Tests
on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]
jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v5
        with:
          node-version: lts/*
      - name: Install dependencies
        run: npm ci
      - name: Install Playwright Browsers
        run: npx playwright install --with-deps
      - name: Run Playwright tests
        run: npx playwright test
```

Promote to the sharded workflow as soon as the suite exceeds ~5 minutes on a single runner, or whenever a pre-merge check is gating PRs.

## Tuning notes

- `fail-fast: false` so a flake on one shard does not cancel sibling shards.
- `timeout-minutes` capped per job; a hung browser process otherwise burns the whole CI budget.
- Cache key pinned to `package-lock.json` so a Playwright version bump invalidates the browser cache automatically.
- Secrets passed via `env`, never logged. Use a service-account test user, never a real human account.
- Upload reports `if: always()` so failures are inspectable; gate the artifact behind `if: failure()` only when storage cost matters.
