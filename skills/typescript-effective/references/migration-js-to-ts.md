# Migrating JavaScript to TypeScript

Big-bang rewrites lose. Gradual migration ships value every week, keeps production stable, and trains the team. This is the playbook.

## Phases

1. Prepare the codebase (lint, tests, tooling).
2. Turn on TS with `allowJs` + `checkJs`.
3. Add JSDoc types to the worst offenders.
4. Rename file-by-file with `.ts` / `.tsx`.
5. Turn on `strict` family incrementally.
6. Remove the compatibility scaffolding.

## Phase 1 — prepare

- Pin Node version and package manager.
- ESLint with `eslint-config-*` that covers JS.
- Test coverage on the modules you plan to migrate first (refactoring without tests is gambling).
- Remove dead code aggressively. Don't port what you don't use.
- Enforce CI: `eslint .` and test run on every PR.

## Phase 2 — install TS, turn on checkJs

```bash
pnpm add -D typescript @types/node
```

`tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowJs": true,
    "checkJs": true,
    "noEmit": true,
    "strict": false,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"]
}
```

- `allowJs: true` — TS compiles JS.
- `checkJs: true` — TS type-checks JS via JSDoc and inference.
- `noEmit: true` — your bundler still emits; TS is the checker.
- `strict: false` — start loose; we tighten later.

Run `tsc --noEmit`. Expect many errors. Triage: add `// @ts-nocheck` at the top of files you cannot fix today, track them with a lint rule to remove later.

## Phase 3 — JSDoc types

Add types without renaming files. Benefits immediately; no runtime risk.

```js
// user.js
/**
 * @typedef {Object} User
 * @property {string} id
 * @property {string} email
 * @property {"admin" | "member"} role
 */

/**
 * @param {string} id
 * @returns {Promise<User | null>}
 */
export async function loadUser(id) {
  // ...
}
```

More advanced:

```js
/**
 * @template T
 * @param {readonly T[]} xs
 * @param {(x: T) => boolean} pred
 * @returns {T | undefined}
 */
export function findFirst(xs, pred) { /* ... */ }

/** @type {import('./schemas.js').UserCreate} */
const draft = { email: "a@b.c", role: "member" };
```

Key forms:

- `@param`, `@returns`, `@type`, `@typedef`.
- `@template T` — generics.
- `@satisfies` — Zod-like narrow (TS 4.9+).
- `import("./file.js").Name` — cross-file references.

Use JSDoc aggressively for exported APIs; internal helpers can wait.

## Phase 4 — rename file-by-file

Pick the smallest, most depended-on files first (utils, constants). Rename `.js` → `.ts` or `.jsx` → `.tsx`.

- Fix errors that surface. Do not cast to `any` — narrow properly. If a type is unknowable today, use `unknown` and add a `TODO`.
- Keep each rename a small PR. A PR that flips 80 files is unreviewable.
- Update barrel re-exports; they often need explicit typing.

Rename order:

1. Pure functions and utilities.
2. Domain models and schemas.
3. Services (db/API wrappers).
4. Handlers / controllers.
5. UI components.

Don't rename entry files (`src/index.js`) until everything upstream is TS.

## Phase 5 — turn on strict, one flag at a time

Each flag gets its own PR. Order that minimises pain:

1. `noImplicitAny` — the biggest value, often the biggest fix.
2. `strictNullChecks` — second biggest; many "cannot be undefined" fixes.
3. `strictFunctionTypes`, `strictBindCallApply` — smaller impact.
4. `strictPropertyInitialization` — class fields.
5. `noImplicitThis`, `alwaysStrict` — usually no-op.
6. Collapse to `"strict": true`.

Then add the extra flags:

- `noUncheckedIndexedAccess`
- `exactOptionalPropertyTypes`
- `noImplicitOverride`
- `noFallthroughCasesInSwitch`, `noImplicitReturns`

Each of these will surface real bugs. Plan a week per flag for large codebases.

## Phase 6 — remove scaffolding

- Remove `allowJs` and `checkJs` after all files are `.ts`.
- Add `isolatedModules` and `verbatimModuleSyntax`.
- Remove `// @ts-nocheck` / `// @ts-ignore` files. Replace with proper fixes or `// @ts-expect-error` with a comment explaining why and a tracking issue.

## Common pitfalls

### Implicit `this` in class methods

```ts
class X {
  value = 1;
  // this becomes `any` without `strict`
  tick() { return this.value++; }
}
```

Fix: turn on `noImplicitThis`.

### Import extensions

Under `"moduleResolution": "node16"`/`"nodenext"`, you must write `import "./foo.js"` even in `.ts` files. Surprising but correct for Node-native ESM.

### CommonJS interop

```ts
// some-cjs-package has no default export typings
import * as pkg from "some-cjs-package";
// or
import pkg from "some-cjs-package";  // with esModuleInterop
```

Turn on `esModuleInterop` from day one.

### `@types/*` vs inline types

- Prefer `@types/<pkg>` from DefinitelyTyped where available.
- If a library ships types, prefer those.
- If types are wrong, open a PR against DefinitelyTyped or use module augmentation locally.

### `any` drift

Grep regularly: `rg ": any" src/ && rg "as any" src/`. Block new `any` via ESLint `@typescript-eslint/no-explicit-any`.

### Third-party libraries without types

```ts
// types/my-lib.d.ts
declare module "my-lib" {
  export function doThing(x: string): number;
}
```

File it under `types/` and reference in `tsconfig`'s `typeRoots` or `include`.

### Test files trailing the migration

Convert tests along with source. Tests with mismatched types are the best bug-finders.

## Migration metrics to track

- Percentage of files that are `.ts` (target 100%).
- Count of `any`, `as`, `@ts-ignore`, `@ts-nocheck` (target trending down).
- Percentage of strict flags on.
- Build time for `tsc --noEmit` (should not regress once scaffolding is removed).

## Example migration timeline

Codebase of ~1k files, 4 engineers:

- Week 1-2: Prepare, install TS, `allowJs`/`checkJs`, JSDoc on top-5 modules.
- Week 3-6: Rename utils and domain layer (~200 files).
- Week 7-10: Rename services and handlers.
- Week 11-13: Rename UI components.
- Week 14-16: Enable `strict` flags one by one.
- Week 17-18: Enable extra strict flags, remove scaffolding.

Shippable in ~4 months for a seasoned team. Larger codebases scale linearly.

## Anti-patterns

- Flipping `strict: true` in one PR with 900 `any` casts to make it compile.
- Using `any` as an escape hatch when the type is knowable.
- Mixing `.js` and `.ts` versions of the same module (ambiguous resolution).
- Running TS in a branch "for experimentation" that never merges.
- Adding TypeScript without tests — you're just moving bugs to a new file type.

## Cross-reference

Parallel of gradual type-adoption in Python via `python-modern-standards/references/typing-mypy-pyright.md`.
