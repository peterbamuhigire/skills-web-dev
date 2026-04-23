---
name: e2e-testing
description: Use when writing end-to-end browser tests for production web apps — Playwright
  with TypeScript, Page Object Model, network interception, visual regression, accessibility
  assertions, CI integration (GitHub Actions), parallel execution, and flaky test
  triage.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# End-to-End Testing (Playwright)
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Use when writing end-to-end browser tests for production web apps — Playwright with TypeScript, Page Object Model, network interception, visual regression, accessibility assertions, CI integration (GitHub Actions), parallel execution, and flaky test triage.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `e2e-testing` or would be better handled by a more specific companion skill.
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

## When E2E Tests Are Worth It

E2E tests sit at the top of the Cohn pyramid: 70% unit, 20% integration, 10% E2E. They catch failures unit tests cannot — third-party script regressions, CSS layout breakage, auth cookies, real network timing, browser quirks. *Do not use E2E to verify pure logic*; that belongs in unit tests. Targets: pass rate `>=` 99% over 7 days, wall-clock `<=` 5 min on CI with sharding, flake rate `<=` 1% (quarantine within 24 h).

```typescript
// tests/smoke.spec.ts — minimum smoke test a deploy must pass
import { test, expect } from '@playwright/test';
test('home page renders and primary CTA works', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/Dashboard/);
  await page.getByRole('link', { name: 'Get Started' }).click();
  await expect(page).toHaveURL(/\/signup/);
});
```

## Playwright Setup

Initialise with `npm init playwright@latest` (answer TypeScript, `tests/`, GitHub Actions). Keep E2E under `tests/e2e/` when the repo also has Jest/Vitest units under `tests/unit/`.

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';
export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 4 : undefined,
  reporter: [['html', { open: 'never' }], ['junit', { outputFile: 'results.xml' }], ['list']],
  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    { name: 'chromium', use: { ...devices['Desktop Chrome'] }, dependencies: ['setup'] },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] }, dependencies: ['setup'] },
    { name: 'webkit', use: { ...devices['Desktop Safari'] }, dependencies: ['setup'] },
    { name: 'mobile-chrome', use: { ...devices['Pixel 7'] }, dependencies: ['setup'] },
  ],
  webServer: { command: 'npm run dev', url: 'http://localhost:3000', reuseExistingServer: !process.env.CI, timeout: 120_000 },
});
```

## Page Object Model

One class per page. The class owns locators and exposes intent-level methods. Tests never touch selectors directly — this keeps the suite maintainable when the DOM changes.

```typescript
// tests/e2e/pages/LoginPage.ts
import type { Page, Locator } from '@playwright/test';
import { expect } from '@playwright/test';
export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorAlert: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Sign in' });
    this.errorAlert = page.getByRole('alert');
  }

  async goto() { await this.page.goto('/login'); }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
    await expect(this.page).toHaveURL(/\/dashboard/);
  }
}

// tests/e2e/login.spec.ts — uses the page object
import { test } from '@playwright/test';
import { LoginPage } from './pages/LoginPage';

test('user signs in successfully', async ({ page }) => {
  const login = new LoginPage(page);
  await login.goto();
  await login.login('alice@example.com', 'hunter2-correct');
});
```

## Locator Strategy

Prefer locators that match how a real user finds elements. Priority order:

1. `getByRole` — canonical accessibility query.
2. `getByLabel` — form inputs with associated labels.
3. `getByPlaceholder` — inputs without labels (fix the a11y bug later).
4. `getByText` — static copy and headings.
5. `getByTestId` — last resort when semantics cannot express the target.

```typescript
// Good — survives CSS refactors, signals intent
await page.getByRole('button', { name: 'Save changes' }).click();
await page.getByLabel('Quantity').fill('3');
// Bad — brittle, opaque, couples test to markup internals
await page.locator('.btn.btn-primary.save-btn').click();
await page.locator('#root > div > form > div:nth-child(2) > input').fill('3');
```

Chain to scope: `page.getByRole('row', { name: 'Invoice #42' }).getByRole('button', { name: 'Delete' })`.

## Test Fixtures

Fixtures inject reusable setup. Extend `test` to add authed pages, seeded records, or instrumented API clients.

```typescript
// tests/e2e/fixtures.ts
import { test as base, type Page } from '@playwright/test';
import { LoginPage } from './pages/LoginPage';
export const test = base.extend<{ authedPage: Page }>({
  authedPage: async ({ page }, use) => {
    const login = new LoginPage(page);
    await login.goto();
    await login.login('alice@example.com', 'hunter2-correct');
    await use(page);
  },
});
export { expect } from '@playwright/test';
// Usage — test body starts logged in
import { test, expect } from './fixtures';
test('dashboard loads for authed user', async ({ authedPage }) => {
  await expect(authedPage.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

## Authentication in E2E Tests

Do not re-run the login UI per test. Log in once in a `setup` project, save `storageState`, reuse across the run. Cuts suite time 30-60% and removes login flows from the critical path.

```typescript
// tests/e2e/auth.setup.ts
import { test as setup, expect } from '@playwright/test';
const authFile = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill(process.env.E2E_USER_EMAIL!);
  await page.getByLabel('Password').fill(process.env.E2E_USER_PASSWORD!);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/\/dashboard/);
  await page.context().storageState({ path: authFile });
});

// playwright.config.ts — wire state into dependent projects
{
  name: 'chromium',
  use: { ...devices['Desktop Chrome'], storageState: 'playwright/.auth/user.json' },
  dependencies: ['setup'],
},
```

Add `playwright/.auth/` to `.gitignore`. *Never commit saved auth state* — it contains live session tokens.

## Network Interception

`page.route()` rewrites any request at the browser layer. Use it to mock third-party APIs, inject error states, simulate slow networks.

```typescript
// Mock JSON response
await page.route('**/api/orders', async (route) => {
  await route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ orders: [{ id: 1, total: 42.00 }] }),
  });
});
// Force network failure
await page.route('**/api/payments', (route) => route.abort('failed'));
// Simulate slow backend — 2s delay before the real request continues
await page.route('**/api/reports/*', async (route) => {
  await new Promise((r) => setTimeout(r, 2_000));
  await route.continue();
});
```

Full throttling (CPU + bandwidth) uses CDP: `const client = await page.context().newCDPSession(page); await client.send('Network.emulateNetworkConditions', { offline: false, latency: 400, downloadThroughput: 500_000, uploadThroughput: 500_000 });`.

## Form Submission Testing

Cover three states per form: valid submit, field-level validation, server-side error. Use `getByRole('alert')` to read validation messages.

```typescript
test('contact form validates required fields', async ({ page }) => {
  await page.goto('/contact');
  await page.getByRole('button', { name: 'Send message' }).click();
  const alert = page.getByRole('alert');
  await expect(alert).toContainText('Email is required');
  await expect(alert).toContainText('Message is required');
});

test('contact form accepts file attachment', async ({ page }) => {
  await page.goto('/contact');
  await page.getByLabel('Email').fill('alice@example.com');
  await page.getByLabel('Message').fill('See attached.');
  await page.getByLabel('Upload').setInputFiles('./tests/e2e/fixtures/doc.pdf');
  await page.getByRole('button', { name: 'Send message' }).click();
  await expect(page.getByRole('status')).toContainText('Message sent');
});
```

## Visual Regression Testing

Pixel snapshots catch layout breakage that functional assertions miss. Baseline per platform — rendering differs across macOS, Linux, Windows.

```typescript
test('dashboard matches visual baseline', async ({ page }) => {
  await page.goto('/dashboard');
  await page.waitForLoadState('networkidle');
  await expect(page).toHaveScreenshot('dashboard.png', {
    maxDiffPixelRatio: 0.01,
    mask: [page.getByTestId('current-time'), page.getByRole('img', { name: 'Avatar' })],
  });
});
```

Regenerate baselines with `npx playwright test --update-snapshots`; images land under `tests/e2e/<spec>.spec.ts-snapshots/dashboard-chromium-linux.png`. *Mask every dynamic region* — clocks, randomised charts, avatar URLs — or snapshots flake.

## Accessibility Testing

Fail the build on WCAG 2.2 AA violations using `@axe-core/playwright`. One check per page-level test; full coverage catches regressions the design team would otherwise ship.

```typescript
import AxeBuilder from '@axe-core/playwright';
import { test, expect } from '@playwright/test';
test('dashboard has no accessibility violations', async ({ page }) => {
  await page.goto('/dashboard');
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag22aa'])
    .exclude('#third-party-widget')
    .analyze();
  expect(results.violations).toEqual([]);
});
```

Violations contain `id`, `impact`, `description`, and `nodes[].html` — enough to open a ticket with selector and remediation pointer.

## Mobile Viewport Testing

Three viewports matter: 375 px (iPhone), 768 px (iPad portrait), 1280 px (laptop). Device descriptors set viewport, user agent, touch support in one line.

```typescript
import { test, expect, devices } from '@playwright/test';
test.use({ ...devices['iPhone 15 Pro'] });

test('mobile nav drawer opens on tap', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Open menu' }).tap();
  await expect(page.getByRole('navigation')).toBeVisible();
});

test.describe('responsive breakpoints', () => {
  for (const width of [375, 768, 1280]) {
    test(`renders at ${width}px`, async ({ page }) => {
      await page.setViewportSize({ width, height: 900 });
      await page.goto('/');
      await expect(page.getByRole('main')).toBeVisible();
    });
  }
});
```

## API + UI Combined Tests

The `request` fixture hits the API directly. Use it to seed data before UI assertions and clean up after — faster and more deterministic than driving the UI for setup.

```typescript
import { test, expect } from '@playwright/test';
test('invoice list shows a newly created invoice', async ({ request, page }) => {
  const created = await request.post('/api/invoices', {
    data: { customer: 'Acme', total: 1200 },
    headers: { Authorization: `Bearer ${process.env.API_TOKEN}` },
  });
  expect(created.ok()).toBeTruthy();
  const { id } = await created.json();

  await page.goto('/invoices');
  await expect(page.getByRole('row', { name: /Acme/ })).toBeVisible();
  await test.info().attach('invoice-id', { body: String(id) });
});

test.afterEach(async ({ request }) => {
  await request.delete('/api/invoices/test-cleanup', {
    headers: { Authorization: `Bearer ${process.env.API_TOKEN}` },
  });
});
```

## Parallel Execution

Playwright parallelises at the file level by default. `fullyParallel: true` parallelises at the test level within a file. Use `workers: 4` on CI, unbounded locally.

```typescript
export default defineConfig({ fullyParallel: true, workers: process.env.CI ? 4 : undefined });
// Per-file override when tests mutate shared state
test.describe.configure({ mode: 'serial' });
// Sharding — run 1/4 of the suite per CI job: npx playwright test --shard=2/4
```

Shared state (DB rows, uploaded files) requires serial mode, per-worker isolation (unique tenant per `testInfo.workerIndex`), or a fresh seeded DB per shard.

## CI Integration (GitHub Actions)

Install deps, cache npm and browsers, run tests in a shard matrix, upload the HTML report on failure.

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

## Debugging

Four tools, ranked by frequency of use:

1. **Trace Viewer** — every failure produces `trace.zip`. Open with `npx playwright show-trace trace.zip` for DOM snapshot, network log, console timeline per action.
2. **`--debug`** — `npx playwright test login.spec.ts --debug` opens Inspector (step-through UI + locator picker).
3. **`page.pause()`** — drop in the test body to freeze execution and explore interactively.
4. **Screenshots** — `screenshot: 'only-on-failure'` in config; inspect under `test-results/`.

```typescript
test('dashboard shows recent orders', async ({ page }) => {
  await page.goto('/dashboard');
  await page.pause(); // opens Inspector; remove before commit
  await expect(page.getByRole('table')).toBeVisible();
});
```

## Reporting

HTML reporter is the default. Add JUnit XML for CI plugins, Allure for trend dashboards.

```typescript
reporter: [
  ['html', { open: 'never', outputFolder: 'playwright-report' }],
  ['junit', { outputFile: 'results.xml' }],
  ['allure-playwright', { detail: true, outputFolder: 'allure-results' }],
],
```

Catch flakes early: `retries: 2` tolerates transient issues while reporting them. Run `npx playwright test --repeat-each=20 flaky.spec.ts` locally to prove determinism. Tests failing at least once in 20 runs are quarantined via `test.fixme()` with a ticket inside 24 h.

## Companion Skills

- `advanced-testing-strategy` — test pyramid, quality gates, coverage strategy
- `cicd-pipelines` — GitHub Actions workflow patterns
- `webapp-testing` (Anthropic) — Playwright-driven verification of local apps

## Sources

- Playwright documentation — `playwright.dev/docs`
- Playwright CI guide — `playwright.dev/docs/ci-github`
- *Testing JavaScript Applications* — Lucas da Costa (Manning)
- `@axe-core/playwright` — `github.com/dequelabs/axe-core-npm`