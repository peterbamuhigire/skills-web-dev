---
name: typescript-effective
description: Use when writing production TypeScript — clean code idioms, effective-TS
  items, strict tsconfig, migration from JS, build performance, testing, and anti-patterns.
  Complements typescript-mastery (type system depth) and typescript-design-patterns
  (GoF).
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Effective TypeScript

<!-- dual-compat-start -->
## Use When

- Use when writing production TypeScript — clean code idioms, effective-TS items, strict tsconfig, migration from JS, build performance, testing, and anti-patterns. Complements typescript-mastery (type system depth) and typescript-design-patterns (GoF).
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `typescript-effective` or would be better handled by a more specific companion skill.
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
Production-grade TypeScript beyond the type system. Every rule here lifts real code quality, not just appeases the compiler.

**Prerequisite:** Load `typescript-mastery` for type-system depth. Use this skill for day-to-day production idioms.

## When this skill applies

- Code review on TypeScript PRs.
- Starting a new TypeScript project (tsconfig, linting, test setup).
- Migrating a JavaScript codebase to TypeScript gradually.
- Eliminating "any" drift in an existing TS codebase.
- Tuning TypeScript build for large monorepos.

## Non-negotiables

1. `strict: true` plus `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitOverride`.
2. Never use `any`. Use `unknown` at boundaries and narrow.
3. Never cast with `as` unless there is no better option; never `as unknown as T`.
4. Validate every external input with Zod (API responses, env vars, form data, queue payloads).
5. Prefer `union` types over `enum` unless integer values and bidirectional lookup are needed.
6. Use discriminated unions with exhaustive `switch` and `assertNever`.
7. Never throw strings. Throw `Error` subclasses.
8. Model absence with `null`/`undefined` intentionally — don't mix.
9. `readonly` on inputs by default.
10. Error handling — prefer Result/Either for expected failures at boundaries.

## tsconfig for production

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitReturns": true,
    "allowUnreachableCode": false,
    "allowUnusedLabels": false,
    "isolatedModules": true,
    "verbatimModuleSyntax": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "useUnknownInCatchVariables": true
  }
}
```

`strict` alone is not enough. `noUncheckedIndexedAccess` catches real bugs (arr[i] is T | undefined). `exactOptionalPropertyTypes` distinguishes `{ x?: number }` from `{ x?: number | undefined }`. See `references/tsconfig-production.md`.

## Core effective-TS items

**Prefer types that narrow your values:**

```ts
// BAD - primitive obsession
function sendEmail(to: string, subject: string, body: string) { ... }

// GOOD - branded types
type Email = string & { readonly __brand: "Email" };
type Subject = string & { readonly __brand: "Subject" };
function parseEmail(raw: string): Email | null { ... }
```

**Discriminated unions + exhaustive match:**

```ts
type Event =
  | { kind: "login"; userId: string }
  | { kind: "logout"; userId: string; at: Date }
  | { kind: "purchase"; userId: string; amount: number };

function handle(e: Event): string {
  switch (e.kind) {
    case "login":    return `login ${e.userId}`;
    case "logout":   return `logout ${e.userId}`;
    case "purchase": return `bought ${e.amount}`;
    default:         return assertNever(e);
  }
}

function assertNever(x: never): never { throw new Error(`unhandled: ${JSON.stringify(x)}`); }
```

**Narrow `unknown` before use — never silently trust it.**

See `references/effective-ts-items.md` for the full catalogue (~40 items).

## Clean code in TS

- **Small functions** — one reason to change. Functions over 40 lines or 3 levels of nesting: split.
- **Names carry intent** — `isActive(user)` not `check(user)`; `loadUser(id)` not `get(id)`.
- **Comments explain WHY** — TS types explain WHAT. Don't duplicate.
- **SOLID in TS** — Single Responsibility, Interface Segregation, Dependency Inversion via constructor injection or factory functions.
- **Immutability** — `readonly`, `as const`, `Readonly<T>`, spread instead of mutate.
- **Pure functions where possible** — easier to test, reason about, memoise.

See `references/clean-code-ts.md`.

## Error handling — Result/Either at boundaries

Throwing is fine inside a module; at boundaries (API handlers, workers, UI event handlers), return typed results:

```ts
type Ok<T> = { ok: true; value: T };
type Err<E> = { ok: false; error: E };
type Result<T, E> = Ok<T> | Err<E>;

const ok = <T>(value: T): Ok<T> => ({ ok: true, value });
const err = <E>(error: E): Err<E> => ({ ok: false, error });

async function loadUser(id: string): Promise<Result<User, "not_found" | "db_down">> {
  try {
    const user = await db.user.findUnique({ where: { id } });
    return user ? ok(user) : err("not_found");
  } catch {
    return err("db_down");
  }
}
```

Libraries: `neverthrow`, `ts-results`, or hand-roll as above. Pick one per project. See `references/error-handling-result.md`.

## Zod at boundaries

Every external input parsed with Zod, every internal type inferred from the schema.

```ts
import { z } from "zod";

const UserCreate = z.object({
  email: z.string().email(),
  age: z.number().int().min(0).max(150),
  role: z.enum(["admin", "member", "viewer"]),
}).strict();

type UserCreate = z.infer<typeof UserCreate>;

app.post("/users", (req, res) => {
  const parsed = UserCreate.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ errors: parsed.error.flatten() });
  // parsed.data is fully typed
});
```

Sources of truth: Zod schema → inferred type. Never define the type separately. See `references/zod-boundaries.md`.

## Migration JS → TS

Gradual, not big-bang. See `references/migration-js-to-ts.md` for the playbook. Summary:

1. `allowJs: true`, `checkJs: true` — TS checks JS files.
2. Add JSDoc types as light annotation.
3. Rename `.js` → `.ts` file by file, fix errors.
4. Turn on `noImplicitAny`, then `strict`, then stricter flags one at a time.
5. Never convert in a single PR more than one team can review.

## Build performance

- **Project references** for monorepos — incremental builds across packages.
- **`isolatedModules`** lets bundlers type-check per-file.
- **`transpile-only`** in dev (ts-node with swc/esbuild, tsup).
- **Type-check in CI** separately from bundling.
- **Skip lib check** (`skipLibCheck: true`) — trust dep types.

See `references/build-performance.md`.

## Testing

- **vitest** for Node + browser — fast, Jest-compatible, TypeScript-native.
- **Type tests** with `expectTypeOf` (vitest) or `tsd` for library APIs.
- **Property-based tests** with `fast-check` for pure logic.
- **Fixtures** strongly typed via schemas — reuse Zod schemas for test data generators.

See `references/testing-vitest.md`.

## Anti-patterns

- `any` — signals "I give up on types." Fix, don't paper over.
- `as T` (type assertion) — silently lies to the compiler.
- `as unknown as T` — the double lie. Always wrong.
- `!` non-null assertion — use narrowing or a type guard.
- `Function` type — use `(...args: never[]) => unknown` or specific signatures.
- `Object` / `{}` type — use `Record<string, unknown>` or a specific shape.
- `enum` for small string sets — use union of string literals.
- Class with all static methods — use a namespace-less module.
- `namespace` — use ES modules.
- Parameter properties in class constructors where they hurt readability.
- Silent `catch (e) {}` — log or re-throw.
- Mutating function arguments.
- `delete obj.key` on typed objects — use spread to build a new object.

See `references/anti-patterns.md`.

## CI gates

```text
tsc --noEmit
eslint . --max-warnings=0
vitest run --coverage --coverage.thresholds.lines=80
```

## Read next

- `typescript-mastery` — deep type system when you need it.
- `typescript-design-patterns` — GoF patterns in TS.
- `typescript-full-stack` — shared types FE↔BE, Zod everywhere.
- `react-development` / `nextjs-app-router` — framework-specific.

## References

- `references/tsconfig-production.md`
- `references/effective-ts-items.md`
- `references/clean-code-ts.md`
- `references/error-handling-result.md`
- `references/zod-boundaries.md`
- `references/migration-js-to-ts.md`
- `references/build-performance.md`
- `references/testing-vitest.md`
- `references/anti-patterns.md`
