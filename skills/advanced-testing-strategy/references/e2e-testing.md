# Absorbed Skill: e2e-testing

Original entrypoint: `skills/e2e-testing/SKILL.md`
Active parent skill: `skills/advanced-testing-strategy/SKILL.md`
Status: Absorbed as reference material; this file preserves the old skill content for progressive disclosure.

---
name: e2e-testing
description: Use when writing end-to-end browser tests for production web apps — Playwright with TypeScript, locator strategy, Page Object and component-object patterns, fixtures and worker model, network interception, storageState auth reuse, visual regression, flake mitigation, sharded CI, and a Cypress decision aid.
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

## Isolation Model

Each test gets its own `Page`, which lives inside its own `BrowserContext` (an isolated cookie and localStorage jar), which shares an underlying `Browser` instance across tests for performance. That hierarchy is why two tests can run in parallel against the same site without leaking auth or state — never share contexts manually unless a test deliberately exercises cross-tab behaviour.

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

Prefer locators that match how a real user finds elements. All `getBy*` locators auto-wait and retry. Priority order from the official docs:

1. `getByRole` — canonical accessibility query: `page.getByRole('button', { name: 'Sign in' }).click()`.
2. `getByText` — static copy and headings: `expect(page.getByText('Welcome, John!')).toBeVisible()`.
3. `getByLabel` — form controls by associated label: `page.getByLabel('Password').fill('secret')`.
4. `getByPlaceholder` — inputs without labels (fix the a11y bug later): `page.getByPlaceholder('name@example.com').fill('test@example.com')`.
5. `getByAltText` — images and other elements with text alternatives: `page.getByAltText('playwright logo').click()`.
6. `getByTitle` — elements identified by `title` attribute: `expect(page.getByTitle('Issues count')).toHaveText('25 issues')`.
7. `getByTestId` — last resort when semantics cannot express the target: `page.getByTestId('directions').click()`.

Prefer role/text/label because they encode the user's mental model and survive layout refactors. Reach for `data-testid` only when an element has no semantic identity (icon-only buttons, third-party widgets).

```typescript
// Good — survives CSS refactors, signals intent
await page.getByRole('button', { name: 'Save changes' }).click();
await page.getByLabel('Quantity').fill('3');
// Bad — brittle, opaque, couples test to markup internals
await page.locator('.btn.btn-primary.save-btn').click();
await page.locator('#root > div > form > div:nth-child(2) > input').fill('3');
```

Chain to scope: `page.getByRole('row', { name: 'Invoice #42' }).getByRole('button', { name: 'Delete' })`.

## Page Object vs Component Objects

POM gives one class per page. Use it when flows are long, shared across many tests, and the page surface is stable. It hurts when the page changes fast and the abstraction lags — every refactor touches both the page object and the test.

A *component object* is a fixture-backed class per UI component (login form, search bar, invoice row). Smaller blast radius, easier to compose across pages, and aligns naturally with `test.extend`. Reach for component objects when the same widget appears on many pages or when tests are organised by feature rather than route.

```typescript
// tests/e2e/components/SearchBar.ts
import type { Page, Locator } from '@playwright/test';
export class SearchBar {
  readonly input: Locator;
  readonly submit: Locator;
  constructor(public page: Page, root: Locator = page.getByRole('search')) {
    this.input = root.getByRole('searchbox');
    this.submit = root.getByRole('button', { name: 'Search' });
  }
  async search(term: string) {
    await this.input.fill(term);
    await this.submit.click();
  }
}
```

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

Built-in fixtures: `page`, `context`, `browser`, `browserName`, `request`. Custom fixtures support three scopes:

- **test-scoped** (default) — recreated for every test; safe for stateful objects like a seeded record.
- **worker-scoped** — `{ scope: 'worker' }` — created once per worker process; use for expensive shared resources (DB pool, prebuilt tenant) where the cost of per-test setup dominates.
- **automatic** — `{ auto: true }` — runs even if a test never references it; use for tracing setup, console-error guards, or per-test cleanup hooks.

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

Use `page.waitForResponse` to assert on the network shape that produced the UI state — this catches regressions where the UI looks right but the request payload silently changed:

```typescript
const [response] = await Promise.all([
  page.waitForResponse((r) => r.url().endsWith('/api/orders') && r.request().method() === 'POST'),
  page.getByRole('button', { name: 'Place order' }).click(),
]);
expect(response.status()).toBe(201);
expect(await response.json()).toMatchObject({ status: 'pending' });
```

The `request` fixture exposes an `APIRequestContext` that hits endpoints directly without a browser — use it for setup, teardown, and pure backend assertions that would be wasteful to drive through the UI. See `api-testing-verification` for contract and schema-level coverage that complements browser flows.

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
    maxDiffPixels: 100,
    mask: [page.getByTestId('current-time'), page.getByRole('img', { name: 'Avatar' })],
  });
});

// playwright.config.ts — global tolerance + injected stylesheet that hides volatile UI
export default defineConfig({
  expect: {
    toHaveScreenshot: {
      maxDiffPixels: 100,
      stylePath: './tests/e2e/screenshot.css', // hides clocks, spinners, avatars
    },
  },
});
```

Snapshot filenames follow `<name>-<index>-<browser>-<platform>.png`. Regenerate baselines with `npx playwright test --update-snapshots`; images land under `tests/e2e/<spec>.spec.ts-snapshots/dashboard-chromium-linux.png`. *Mask every dynamic region* — clocks, randomised charts, avatar URLs — or use `stylePath` to hide them globally; otherwise snapshots flake. For non-image artifacts (JSON, text), use `expect(value).toMatchSnapshot('name.json')`.

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

Three jobs to wire up: install deps, cache npm and browsers, run tests in a shard matrix, upload the HTML report on failure. Use `npx playwright install --with-deps` so Linux system libraries land alongside the browser binaries. Combine `strategy.matrix.shard: [1/4, 2/4, 3/4, 4/4]` with `npx playwright test --shard=${{ matrix.shard }}` to scale wall-clock; cache `~/.cache/ms-playwright` keyed on `package-lock.json` so browser downloads only re-run on version bumps. Upload `playwright-report/` with `if: always()` so failed shards are inspectable from the PR. Full workflow YAML (production sharded + minimal scaffolder variant) lives in `references/github-actions-shard.md`.

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

## Choosing Playwright vs Cypress

Default to Playwright for new suites: cross-browser parity (WebKit), out-of-process Node-driven tests, first-class multi-tab and multi-origin, native mobile device emulation, free sharding without a paid dashboard. Pick Cypress only when the team already has it, the app is a single-origin SPA, and the live time-travel debugger is the highest-value feature. See `references/cypress-comparison.md` for the full decision table and migration notes.

## Companion Skills

- `advanced-testing-strategy` — test pyramid, risk-based depth, release evidence
- `api-testing-verification` — contract, schema, and API-level assertions to pair with the `request` fixture
- `sdlc-testing` — where E2E sits across plan, build, verify, release stages
- `cicd-pipelines` — GitHub Actions workflow patterns
- `webapp-testing` (Anthropic) — Playwright-driven verification of local apps

## Sources

- Playwright getting started — `playwright.dev/docs/intro`
- Playwright locators — `playwright.dev/docs/locators`
- Playwright fixtures — `playwright.dev/docs/test-fixtures`
- Playwright parallelism and sharding — `playwright.dev/docs/test-parallel`
- Playwright network — `playwright.dev/docs/network`
- Playwright auth — `playwright.dev/docs/auth`
- Playwright visual comparisons — `playwright.dev/docs/test-snapshots`
- Playwright CI intro — `playwright.dev/docs/ci-intro`
- Cypress documentation — `docs.cypress.io` (comparison only)
- `@axe-core/playwright` — `github.com/dequelabs/axe-core-npm`
