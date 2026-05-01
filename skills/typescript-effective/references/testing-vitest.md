# Testing TypeScript with Vitest

Vitest is the default test runner for TypeScript in 2024/25 — Jest-compatible API, native ESM, swc/esbuild transform, and first-class type testing. This file covers setup, patterns for unit/integration/type/property-based tests, mocking, and coverage.

## Why Vitest over Jest

- Native ESM without Babel transforms.
- Uses your Vite config (same resolver, same env).
- Much faster on TS — swc or esbuild transform.
- Built-in `expectTypeOf` for type-level assertions.
- Watch mode is instant on change.

## Install and config

```bash
pnpm add -D vitest @vitest/coverage-v8
```

`vitest.config.ts`:

```ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "node",           // or "jsdom" for browser-like
    globals: false,                // prefer explicit imports
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "lcov"],
      thresholds: { lines: 80, functions: 80, branches: 75, statements: 80 },
      exclude: ["**/*.config.*", "**/*.d.ts", "**/dist/**"],
    },
    include: ["src/**/*.test.ts", "src/**/*.spec.ts"],
    setupFiles: ["src/test/setup.ts"],
  },
});
```

For React / DOM tests switch `environment` to `jsdom` or `happy-dom`.

## Structure

Co-locate tests next to source: `user.ts` + `user.test.ts`. Keep one concept per file. Use `describe` to group and `it` for each behaviour.

```ts
import { describe, it, expect, beforeEach, vi } from "vitest";
import { loadUser } from "./user";

describe("loadUser", () => {
  beforeEach(() => { vi.resetAllMocks(); });

  it("returns the user when found", async () => {
    const r = await loadUser("123");
    expect(r.ok).toBe(true);
    if (r.ok) expect(r.value.id).toBe("123");
  });

  it("returns not_found when missing", async () => {
    const r = await loadUser("missing");
    expect(r).toEqual({ ok: false, error: "not_found" });
  });
});
```

## Matchers cheatsheet

- `toBe` — `Object.is`.
- `toEqual` — deep equality.
- `toStrictEqual` — deep equality including class and undefined properties.
- `toMatchObject` — partial deep match.
- `toContain` — array/string inclusion.
- `toThrow` — function throws (optionally matches message/class).
- `resolves` / `rejects` — unwrap promises.
- `toMatchInlineSnapshot` — inline-pinned snapshot (avoid for complex objects).

## Type tests with `expectTypeOf`

```ts
import { expectTypeOf } from "vitest";

it("infers user type", () => {
  expectTypeOf<User>().toEqualTypeOf<{ id: string; email: string; role: Role }>();
  expectTypeOf(loadUser).parameter(0).toBeString();
  expectTypeOf(loadUser).returns.toEqualTypeOf<Promise<Result<User, UserError>>>();
});
```

Use type tests for exported library APIs and critical domain types. Don't type-test internal helpers — the tests become change-detectors.

### tsd as an alternative

For standalone library type tests, `tsd` runs a dedicated typecheck against `.test-d.ts` files:

```bash
pnpm add -D tsd
```

```ts
// src/index.test-d.ts
import { expectType } from "tsd";
import { parseEmail, Email } from "./email";
expectType<Email | null>(parseEmail("a@b.c"));
```

Prefer `expectTypeOf` (runs in your normal test suite) unless you publish a library with a type-only contract.

## Property-based testing with fast-check

```bash
pnpm add -D fast-check
```

```ts
import { fc, test } from "@fast-check/vitest";

test.prop([fc.integer({ min: 0, max: 1_000 })])(
  "tax is monotone in amount",
  (amount) => {
    expect(tax(amount, 0.2)).toBeGreaterThanOrEqual(tax(amount, 0.1));
  },
);

test.prop([fc.array(fc.integer())])(
  "reverse twice is identity",
  (xs) => expect(reverse(reverse(xs))).toEqual(xs),
);
```

Use property-based tests for pure logic with clear invariants: parsers, serialisers, comparators, pure maths. Avoid for side-effectful code.

## Mocking

### `vi.mock` — module-level

```ts
import { vi, describe, it, expect } from "vitest";

vi.mock("./db", () => ({
  db: { user: { findUnique: vi.fn() } },
}));

import { db } from "./db";
import { loadUser } from "./user";

it("calls the repo", async () => {
  vi.mocked(db.user.findUnique).mockResolvedValue({ id: "1", email: "a@b.c" });
  const r = await loadUser("1");
  expect(r.ok).toBe(true);
  expect(db.user.findUnique).toHaveBeenCalledWith({ where: { id: "1" } });
});
```

### `vi.fn` — function-level

```ts
const logger = { info: vi.fn(), error: vi.fn() };
const svc = new UserService(repo, logger);
// assert logger.error.toHaveBeenCalledWith(...)
```

### Fake timers

```ts
vi.useFakeTimers();
vi.setSystemTime(new Date("2024-01-01"));
// run code under test
vi.advanceTimersByTime(1000);
vi.useRealTimers();
```

### Network — MSW

Prefer MSW (Mock Service Worker) for HTTP mocks. It intercepts `fetch`/`axios` requests at the network layer; tests match real calls.

```ts
import { setupServer } from "msw/node";
import { http, HttpResponse } from "msw";

const server = setupServer(
  http.get("https://api.example.com/user/:id", ({ params }) =>
    HttpResponse.json({ id: params.id, email: "a@b.c" })),
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## Integration tests

- Keep a separate script: `pnpm test:integration`.
- Spin up real Postgres via `testcontainers-node` or Docker Compose.
- Reuse Zod schemas for factory data:

```ts
import { UserCreate } from "@acme/schemas";
import { faker } from "@faker-js/faker";

export const aUser = (over: Partial<UserCreate> = {}): UserCreate =>
  UserCreate.parse({
    email: faker.internet.email(),
    name: faker.person.fullName(),
    age: 25,
    role: "member",
    ...over,
  });
```

## Snapshot tests — sparingly

Snapshots are fine for:

- Stable DTO shapes.
- HTML/markdown output with tiny diffs.

Never snapshot:

- Timestamps.
- Random IDs.
- Error stack traces.
- Whole component trees (too noisy; brittle).

Prefer `toMatchInlineSnapshot` over file snapshots — keeps diffs visible in review.

## Coverage with c8/v8 / istanbul

- `@vitest/coverage-v8` — fast, no instrumentation, uses Node's V8 profiler.
- `@vitest/coverage-istanbul` — slower but with more precise branch coverage on transpiled code.

Pick v8 for speed; switch to istanbul only if branch coverage is wrong.

Thresholds in config block CI when coverage regresses. Keep the bar realistic: 80% lines is a good default; 95% for critical domain modules.

## Running tests

```bash
pnpm vitest                     # watch mode, default
pnpm vitest run                 # single run
pnpm vitest run --coverage      # with coverage
pnpm vitest --ui                # browser UI
pnpm vitest path/to/file.test.ts
pnpm vitest -t "returns not_found"   # filter by test name
```

## Typed test utilities

```ts
export function expectOk<T, E>(r: Result<T, E>): asserts r is Ok<T> {
  if (!r.ok) throw new Error(`expected ok, got err: ${JSON.stringify(r.error)}`);
}
export function expectErr<T, E>(r: Result<T, E>): asserts r is Err<E> {
  if (r.ok) throw new Error(`expected err, got ok: ${JSON.stringify(r.value)}`);
}

// usage
const r = await loadUser(id);
expectOk(r);
expect(r.value.email).toBe("a@b.c");
```

`asserts` return types narrow after the helper runs.

## CI gating

```bash
tsc --build --noEmit
eslint . --max-warnings=0
vitest run --coverage
```

Three gates, all must pass. Add `--reporter=junit` for CI dashboards.

## Anti-patterns

- Tests that don't assert — only call the function.
- `any` in tests — defeats type safety at the exact point you need it.
- Shared mutable fixtures between tests.
- Snapshot tests over complex DOM trees.
- Mocking what you own instead of refactoring to accept dependencies.
- Integration tests without cleanup between runs.
- Using real time (`Date.now()`) in tests.

## Cross-reference

Parallel of `python-modern-standards/references/testing-pytest.md`. Both stacks push property-based tests for pure logic, clear separation of unit/integration, and type-aware assertions.
