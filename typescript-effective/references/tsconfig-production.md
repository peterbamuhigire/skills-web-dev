# tsconfig for production

Every option in a production `tsconfig.json` earns its place. This is the reference for what each flag does, when to turn it on, and what trade-offs apply. Matches TypeScript 5.4+ semantics.

## Recommended baseline

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022"],
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
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "isolatedModules": true,
    "verbatimModuleSyntax": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "useUnknownInCatchVariables": true,
    "incremental": true,
    "tsBuildInfoFile": "./node_modules/.cache/tsbuildinfo.json"
  },
  "include": ["src/**/*"],
  "exclude": ["**/*.test.ts", "dist", "node_modules"]
}
```

## Target, lib, module

- `target` — JS syntax output. `ES2022` covers top-level await, `#private`, `Object.hasOwn`. For Node 20+ use `ES2022`; for browsers with wide support go `ES2020`.
- `lib` — DOM types or not. Omit `DOM` on Node projects to prevent accidental `window`/`document` use. Next.js server files still need DOM types — use per-package configs.
- `module` — `ESNext` for bundler-driven projects, `NodeNext` for Node-native ESM. `CommonJS` only for legacy.
- `moduleResolution`:
  - `bundler` — the 2024 default for Vite/webpack/esbuild/Next. Allows extensionless imports, path mappings, and modern resolution. Use this unless Node runs your `.ts` directly.
  - `node16`/`nodenext` — strict Node-style resolution with mandatory file extensions (`import "./foo.js"` even in `.ts`). Mandatory for publishable packages.
  - `node` — legacy CJS resolution. Avoid in new work.

## Strict family

`strict: true` enables:

- `noImplicitAny` — flag variables whose types cannot be inferred.
- `strictNullChecks` — `null`/`undefined` are not assignable to `T` unless `T | null`.
- `strictFunctionTypes` — contravariant parameter check.
- `strictBindCallApply` — typed `bind`, `call`, `apply`.
- `strictPropertyInitialization` — class fields initialised in constructor.
- `alwaysStrict` — emit `"use strict"`.
- `useUnknownInCatchVariables` — `catch (e: unknown)` by default.
- `noImplicitThis` — `this` must be typed.

Turn these on as a block. Turning them off individually is a smell.

## Beyond `strict` — the flags that actually catch bugs

### `noUncheckedIndexedAccess`

```ts
const xs = ["a", "b"];
// without the flag: const first: string
// with the flag:    const first: string | undefined
const first = xs[0];
```

Every array or record access becomes `T | undefined`. This matches reality. Cost: forced narrowing or `!` (which you should not use). Worth it.

### `exactOptionalPropertyTypes`

```ts
interface Config { readonly timeout?: number; }

// without the flag: both allowed
// with the flag: the second is rejected
const a: Config = {};
const b: Config = { timeout: undefined };
```

Distinguishes "missing property" from "property set to undefined". Essential for correct JSON serialisation and for APIs whose optional field semantics differ between "omit" and "null".

### `noImplicitOverride`

Forces `override` keyword on subclass methods that override a base. Catches drift when the base class rename goes unnoticed.

### `noFallthroughCasesInSwitch`, `noImplicitReturns`

Catch control-flow errors that tests miss.

### `noUnusedLocals`, `noUnusedParameters`

Keep files clean. Prefix intentionally unused parameters with `_`. Combine with ESLint `no-unused-vars` disabled — TS handles it.

## Module-related flags

### `isolatedModules`

Every file must be independently transpilable (no cross-file type inference at emit time). Required for Vite, esbuild, swc, and Babel users. Even with tsc-only projects, enable it — it forces good module hygiene (no `const enum` re-export, etc.).

### `verbatimModuleSyntax`

```ts
// must write `import type` when the binding is type-only
import type { User } from "./user";
import { loadUser } from "./user";
```

Replaces `importsNotUsedAsValues` and `preserveValueImports`. The compiler no longer guesses — you declare intent. Required for correct ESM output and tree-shaking. Use with `verbatimModuleSyntax: true` and keep type imports isolated.

### `esModuleInterop`, `allowSyntheticDefaultImports`

Let you write `import express from "express"` for CJS libs. Default on in modern configs. Keep on.

### `resolveJsonModule`

Import `.json` files as typed objects. Combine with `"include": ["src/**/*"]` plus `.json` in includes.

## Cross-cutting quality flags

- `skipLibCheck: true` — don't type-check `node_modules/*.d.ts`. Massive build speedup. You trust your deps; if one ships broken types, pin a version.
- `forceConsistentCasingInFileNames` — prevents case-sensitivity bugs between macOS/Windows/Linux.
- `useUnknownInCatchVariables` — already in `strict`, but always keep on.
- `incremental` + `tsBuildInfoFile` — cache type-check results between runs.

## Project references for monorepos

```json
// packages/shared/tsconfig.json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "composite": true,
    "rootDir": "src",
    "outDir": "dist"
  },
  "include": ["src/**/*"]
}

// packages/api/tsconfig.json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": { "composite": true, "rootDir": "src", "outDir": "dist" },
  "references": [{ "path": "../shared" }],
  "include": ["src/**/*"]
}

// tsconfig.json at repo root
{
  "files": [],
  "references": [
    { "path": "packages/shared" },
    { "path": "packages/api" },
    { "path": "packages/web" }
  ]
}
```

Run `tsc --build` at the root. Changed packages rebuild; unchanged are cached. See `build-performance.md` for more.

## Variants by project type

### Node-native ESM library (publishable)

```json
{
  "module": "NodeNext",
  "moduleResolution": "nodenext",
  "target": "ES2022",
  "declaration": true,
  "declarationMap": true,
  "sourceMap": true,
  "outDir": "dist"
}
```

### Bundler-driven app (Vite, Next)

Use the baseline. Omit `declaration` (bundler handles output).

### Library dual-published CJS + ESM

Use `tsup` or `tshy` with two `tsconfig` variants. Avoid hand-rolling.

## Decision rules

- Do not disable strict flags to unblock migration — use the incremental migration in `migration-js-to-ts.md`.
- Do not add `"lib": ["DOM"]` to Node packages. Use a per-package `tsconfig`.
- Never commit `tsconfig.json` with `allowJs: true` on a pure-TS codebase.
- `moduleResolution: "bundler"` only in app packages — libraries need `nodenext`.
- If a flag change causes >20 new errors, open a dedicated PR with a clean codemod commit, not a feature PR.

## Anti-patterns

- `"strict": false` with selective strict flags — either commit to strict or don't pretend.
- `"noEmitOnError": false` in CI — masking errors.
- Mixing `moduleResolution: "node"` with `module: "ESNext"` — inconsistent output.
- Omitting `isolatedModules` in a project using esbuild/swc/Babel — build will silently produce broken output.
- `"strict": true` plus `//@ts-nocheck` at file top — defeats the purpose.

## Cross-reference

Parallels `python-modern-standards/references/typing-mypy-pyright.md` — strict type checking is earned through config discipline in both ecosystems.
