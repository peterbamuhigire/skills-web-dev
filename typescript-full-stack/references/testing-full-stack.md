# Testing the Full Stack

Cross-ref: `advanced-testing-strategy` for pyramid/risk sizing; `typescript-effective`
for `expectTypeOf`; `deployment-release-engineering` for release gates.

Goal: confidence proportional to blast radius. Unit tests prove logic; integration
tests prove boundaries; E2E tests prove the critical-path user journeys; contract
tests prove API compatibility; type tests prove that misuse will not compile.

## Layout

```text
apps/
  api/
    src/...
    test/
      unit/        (vitest)
      integration/ (vitest + Testcontainers)
  web/
    src/...
    test/          (vitest + @testing-library/react)
    e2e/           (playwright)
packages/
  schemas/
    test/          (vitest + expectTypeOf)
  db/
    test/          (vitest + Testcontainers)
```

Per-package `vitest.config.ts`:

```ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "node",               // "jsdom" in apps/web
    include: ["src/**/*.test.ts", "test/**/*.test.ts"],
    setupFiles: ["./test/setup.ts"],
    coverage: { provider: "v8", reporter: ["text", "lcov"], thresholds: { lines: 80 } },
    typecheck: { enabled: true, tsconfig: "./tsconfig.test.json" },
  },
});
```

Rule: every package has its own test runner config. No shared root `vitest` that has
to serve all stacks.

## Unit tests — fast, isolated, pure

```ts
// packages/schemas/test/user.test.ts
import { describe, it, expect } from "vitest";
import { UserCreate } from "../src/user.js";

describe("UserCreate", () => {
  it("rejects invalid email", () => {
    const res = UserCreate.safeParse({ email: "nope", name: "x", role: "member", orgId: "..." });
    expect(res.success).toBe(false);
  });

  it("normalises email case", () => {
    const res = UserCreate.parse({
      email: "A@B.COM",
      name: "x",
      role: "member",
      orgId: "018f0c02-0000-7000-a000-000000000000",
    });
    expect(res.email).toBe("a@b.com");
  });
});
```

## Integration tests — real database via Testcontainers

```ts
// apps/api/test/integration/setup.ts
import { PostgreSqlContainer, StartedPostgreSqlContainer } from "@testcontainers/postgresql";
import { afterAll, beforeAll } from "vitest";
import { exec } from "node:child_process";
import { promisify } from "node:util";

const run = promisify(exec);
let container: StartedPostgreSqlContainer;

beforeAll(async () => {
  container = await new PostgreSqlContainer("postgres:16-alpine")
    .withDatabase("test")
    .withUsername("test")
    .withPassword("test")
    .start();

  process.env.DATABASE_URL = container.getConnectionUri();
  await run("pnpm prisma migrate deploy", { env: { ...process.env } });
}, 60_000);

afterAll(async () => {
  await container?.stop();
});
```

```ts
// apps/api/test/integration/user.test.ts
import { describe, it, expect, beforeEach } from "vitest";
import { buildApp } from "../../src/app.js";
import { db } from "@acme/db";

describe("POST /v1/users", () => {
  beforeEach(async () => {
    await db.user.deleteMany();
  });

  it("creates a user and rejects duplicate email", async () => {
    const app = await buildApp();

    const first = await app.inject({
      method: "POST",
      url: "/v1/users",
      payload: { email: "a@b.com", name: "A", role: "member", orgId: "018f0c02-..." },
    });
    expect(first.statusCode).toBe(201);

    const dup = await app.inject({
      method: "POST",
      url: "/v1/users",
      payload: { email: "a@b.com", name: "B", role: "member", orgId: "018f0c02-..." },
    });
    expect(dup.statusCode).toBe(409);
    expect(dup.json()).toMatchObject({ error: "conflict" });
  });
});
```

`app.inject` runs the Fastify router without opening a socket — fast and hermetic.

### Alternative: pg-lite for speed

For small services, `@electric-sql/pglite` runs Postgres in-process, ~50 ms cold
start. Loses `pg_stat_statements`, extensions, and large data tests; great for fast
unit-ish integration tests.

```ts
import { PGlite } from "@electric-sql/pglite";
const pg = new PGlite();
await pg.exec("CREATE TABLE users (...)");
```

## Contract snapshot tests

Freeze the external API shape. A PR that changes behaviour produces a red diff.

```ts
// apps/api/test/contract/openapi.test.ts
import { describe, it, expect } from "vitest";
import { generateOpenApi } from "@ts-rest/open-api";
import { userContract } from "@acme/contracts";

describe("contract", () => {
  it("openapi matches committed snapshot", async () => {
    const doc = generateOpenApi(userContract, {
      info: { title: "Acme API", version: "1.0.0" },
    });
    await expect(JSON.stringify(doc, null, 2)).toMatchFileSnapshot("./__snapshots__/openapi.json");
  });
});
```

Rule: reviewers read the diff, not just the file name. Snapshot bypass ("just update
it") on a public API is a contract break — bump the version.

## Type tests — catch misuse at compile time

```ts
// packages/api-client/test/types.test.ts
import { expectTypeOf, test } from "vitest";
import type { inferProcedureInput, inferProcedureOutput } from "@trpc/server";
import type { AppRouter } from "@acme/api";

test("user.byId input is { id: string }", () => {
  type In = inferProcedureInput<AppRouter["user"]["byId"]>;
  expectTypeOf<In>().toEqualTypeOf<{ id: string }>();
});

test("user.byId output is User", () => {
  type Out = inferProcedureOutput<AppRouter["user"]["byId"]>;
  expectTypeOf<Out>().toMatchTypeOf<{ id: string; email: string }>();
});
```

Enable `typecheck: { enabled: true }` in `vitest.config.ts` and the test runner
surfaces both runtime and type failures.

## React component tests

```tsx
// apps/web/test/user-form.test.tsx
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { UserForm } from "../src/components/UserForm.js";

describe("UserForm", () => {
  it("shows validation error for bad email", async () => {
    const onSubmit = vi.fn();
    render(<UserForm onSubmit={onSubmit} />);
    await userEvent.type(screen.getByLabelText(/email/i), "nope");
    await userEvent.click(screen.getByRole("button", { name: /save/i }));
    expect(await screen.findByText(/invalid email/i)).toBeVisible();
    expect(onSubmit).not.toHaveBeenCalled();
  });
});
```

Run with `environment: "jsdom"` for `apps/web`.

## E2E tests — Playwright

`apps/web/playwright.config.ts`:

```ts
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 4 : 2,
  use: {
    baseURL: process.env.E2E_BASE_URL ?? "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "webkit", use: { ...devices["Desktop Safari"] } },
    { name: "mobile-chrome", use: { ...devices["Pixel 7"] } },
  ],
  webServer: process.env.CI
    ? { command: "pnpm start", port: 3000, reuseExistingServer: false }
    : undefined,
});
```

`apps/web/e2e/sign-in.spec.ts`:

```ts
import { test, expect } from "@playwright/test";

test("user can sign in and reach dashboard", async ({ page }) => {
  await page.goto("/sign-in");
  await page.getByLabel(/email/i).fill("e2e@acme.io");
  await page.getByLabel(/password/i).fill(process.env.E2E_PASSWORD!);
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page).toHaveURL(/\/app/);
  await expect(page.getByRole("heading", { name: /dashboard/i })).toBeVisible();
});
```

Rules:

- E2E fixtures spin up via an API-level seed, not via clicking through the UI.
- Never seed with random data — use deterministic IDs so tests are debuggable.
- Keep the E2E suite under 50 scenarios; anything more becomes flaky.
- Tag tests `@critical`, `@smoke`, `@full`; CI runs `@critical` on every PR, `@full`
  nightly.

## Test pyramid targets

```text
Unit:         ~70%  of total tests, <50ms each
Integration:  ~25%  of total tests, <1s each
E2E:          ~5%   of total tests, <30s each
```

Contract tests and type tests are cheap — run them on every PR.

## CI pipeline order

```yaml
jobs:
  test:
    steps:
      - lint
      - type-check            # fails early, fastest signal
      - test:unit
      - test:types
      - test:integration      # Testcontainers
      - test:contract         # snapshot
      - test:e2e --project=chromium @critical
  nightly:
    steps:
      - test:e2e --project=all @full
      - load-test             # k6, optional
```

Run tests in parallel across packages using `turbo run test`.

## Flakiness hygiene

- Tag flaky tests with `.skip.if(someCondition)` rather than deleting.
- Failing test without a log line is a bug — assert on `log` mocks where relevant.
- Never `setTimeout` in a test; use `vi.useFakeTimers()` or Playwright's
  `expect.poll`.
- A test that passes when isolated but fails in the suite is an ordering bug —
  inspect shared state (DB rows, module-level singletons).

## Anti-patterns

- Mocking the ORM in integration tests. The whole point of integration is the
  boundary. Use a real database.
- Asserting on internal implementation details in component tests. Test behaviour.
- E2E tests that drive seed data through the UI. Slow, brittle, no value.
- Snapshots of opaque blobs (minified JS, binary). Use targeted structural
  snapshots.
- `console.log` in a test file. Tests should be silent unless failing.

## Decision rules

```text
Pure function, no IO                       -> unit
Crosses a network / DB boundary            -> integration (Testcontainers)
Has multi-service orchestration            -> integration with docker-compose
Critical user journey                      -> E2E
External API shape                         -> contract snapshot
Type-level contract (generic, inference)   -> expectTypeOf
Perf regression risk                       -> k6 or autocannon in nightly
```
