# Phase 05: Quality & E2E Testing

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the end-to-end testing skill that provides delivery confidence at the UI layer, and deepen the existing `advanced-testing-strategy` skill with risk-based test depth and AI-assisted test generation.

**Architecture:** One new skill directory (`e2e-testing`) plus an enhancement pass on `advanced-testing-strategy`. Playwright is the chosen E2E framework — it supports Chromium, Firefox, and WebKit, has a native TypeScript API, and integrates cleanly with GitHub Actions.

**Tech Stack:** Playwright, Page Object Model, TypeScript, GitHub Actions, visual regression testing, network mocking, `@playwright/test` reporter, MSW (Mock Service Worker).

---

## Dual-Compatibility Contract

Every `SKILL.md` must include:
```
Use When → Do Not Use When → Required Inputs →
Workflow → Quality Standards → Anti-Patterns → Outputs → References
```

Frontmatter:
```yaml
metadata:
  portable: true
  compatible_with: [claude-code, codex]
```

Platform Notes only. Validate:
```bash
python -X utf8 skill-writing/scripts/quick_validate.py <skill-directory>
```

---

## Task 1: Create `e2e-testing` skill

**Files:**
- Create: `e2e-testing/SKILL.md`
- Create: `e2e-testing/references/playwright-setup.md`
- Create: `e2e-testing/references/page-object-model.md`
- Create: `e2e-testing/references/network-mocking.md`
- Create: `e2e-testing/references/ci-integration.md`

**Step 1:** Write `e2e-testing/SKILL.md` covering:

- When to use E2E vs. unit vs. integration — the test pyramid and when to invert it for SaaS
- Playwright fundamentals: `test()`, `expect()`, `page.goto()`, `page.click()`, `page.fill()`, `page.waitForSelector()`
- Locator strategy: prefer `page.getByRole()`, `page.getByLabel()`, `page.getByTestId()` — avoid CSS selectors and XPath
- Test isolation: one browser context per test, no shared state, `beforeEach` to reset to known state
- Page Object Model: class per page, expose typed actions, no assertions in POMs, test file does assertions
- Fixtures: `test.extend()` for custom fixtures (authenticated user, seeded database, specific tenant)
- Visual regression: `expect(page).toHaveScreenshot()`, snapshot storage in git, update command
- Network mocking: `page.route()` to intercept API calls, mock error responses, simulate slow networks
- Parallel execution: `--workers=4`, shard across CI matrix, test file ordering for stability
- Reporting: HTML report, GitHub Actions summary, failure screenshots and videos as CI artifacts

Anti-Patterns: waiting with `page.waitForTimeout()` (use `waitForSelector` or `waitForResponse`), asserting on raw CSS selectors, tests that depend on execution order, flaky selectors that break on copy change.

**Step 2:** Write `references/playwright-setup.md` — `npm init playwright`, `playwright.config.ts` for a Next.js SaaS app (base URL, retries, reporter, projects for Chromium/Firefox), TypeScript config.

**Step 3:** Write `references/page-object-model.md` — complete POM example: LoginPage, DashboardPage, BillingPage with TypeScript. Show how test files compose them.

**Step 4:** Write `references/network-mocking.md` — mock Stripe API responses, mock AI streaming endpoints (SSE), mock file upload, simulate 429 rate limit response and test retry behaviour.

**Step 5:** Write `references/ci-integration.md` — full GitHub Actions workflow: install Playwright, cache browser binaries, run tests in parallel with matrix sharding, upload HTML report and failure screenshots as artifacts, fail PR if any test fails.

**Step 6:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py e2e-testing
git add e2e-testing/
git commit -m "feat: add e2e-testing skill (Playwright, POM, visual regression, CI integration)"
```

---

## Task 2: Enhance `advanced-testing-strategy`

**Files:**
- Modify: `advanced-testing-strategy/SKILL.md`
- Create: `advanced-testing-strategy/references/ai-assisted-test-generation.md`
- Create: `advanced-testing-strategy/references/risk-based-test-depth.md`

**Step 1:** Read `advanced-testing-strategy/SKILL.md` in full before editing.

**Step 2:** Add two sections to SKILL.md (move depth to references):

**AI-Assisted Test Generation:**
- Using Claude/GPT to generate test cases from a function signature + docstring
- Prompting strategy: give the model the function, its expected invariants, and edge cases to explore
- Human review gate: AI-generated tests must be read and understood before committing — never auto-commit
- Mutation testing: use Stryker (JS/TS) to verify tests actually catch bugs, not just execute lines
- Property-based testing: `fast-check` (TypeScript) for invariant discovery

**Risk-Based Test Depth:**
- Decision matrix: financial calculations → 100% unit coverage + property tests; UI layout → snapshot only; happy-path CRUD → integration test sufficient
- Release evidence checklist: what must pass before merging to main (unit suite, integration suite, E2E smoke suite, security scan, performance budget)

**Step 3:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py advanced-testing-strategy
git add advanced-testing-strategy/
git commit -m "feat: enhance advanced-testing-strategy — AI test generation, risk-based depth, mutation testing"
```

---

## Success Gate

- [ ] `e2e-testing` passes validator, ≤ 500 lines, portable metadata present
- [ ] `advanced-testing-strategy` still passes validator after enhancement
- [ ] `e2e-testing` references `cicd-pipelines` (from Phase 01) in its CI integration section
- [ ] No `Required Plugins` blockers in either skill

---

## Reading Material

| Priority | Resource | Format | Cost | Unlocks |
|----------|----------|--------|------|---------|
| 1 | Playwright documentation | Free (playwright.dev/docs) | Free | All `e2e-testing` content |
| 2 | *Testing JavaScript Applications* — Lucas da Costa (Manning) | Book | ~$50 | Full JS testing stack, E2E chapter |
| 3 | Stryker Mutator documentation | Free (stryker-mutator.io) | Free | Mutation testing for `advanced-testing-strategy` |
| 4 | fast-check documentation | Free (fast-check.dev) | Free | Property-based testing |
| 5 | Playwright GitHub Actions guide | Free (playwright.dev/docs/ci-intro) | Free | CI integration reference |

**Read first:** Playwright docs (free, outstanding quality) — read the Getting Started and CI sections fully before writing the skill.

---

*Next → `phase-06-mobile-pwa-completeness.md`*
