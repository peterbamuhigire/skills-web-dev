# Build performance

Slow TypeScript builds are a productivity tax. This file covers the dials that actually matter in 2024/25: project references, incremental compilation, fast transpilers (swc/esbuild), and monorepo caching (pnpm + turborepo).

## Golden rules

- `tsc` is the type-checker. Use `tsc --noEmit` in CI; use esbuild/swc/Vite/Next to emit code.
- In dev, skip type-checking (transpile-only) for inner loop speed; run `tsc --noEmit` in a sidecar terminal or pre-commit hook.
- In monorepos, use project references to get incremental builds across packages.
- Cache aggressively at both the workspace layer (pnpm) and the task layer (turborepo/nx).

## Baseline tsconfig for speed

```json
{
  "compilerOptions": {
    "incremental": true,
    "tsBuildInfoFile": "./node_modules/.cache/tsbuildinfo.json",
    "skipLibCheck": true,
    "isolatedModules": true,
    "moduleResolution": "bundler"
  }
}
```

- `incremental: true` — tsc caches type-check results. Re-runs only check changed files.
- `skipLibCheck: true` — skip `node_modules/*.d.ts`. Huge win. Trust your deps.
- `isolatedModules: true` — every file must transpile standalone. Required by swc/esbuild/Babel.

## Project references for monorepos

Project references turn a flat compile into a DAG. Changed packages rebuild; unchanged use cached `.d.ts`.

```text
repo/
  tsconfig.base.json
  tsconfig.json                # references all packages
  packages/
    shared/
      tsconfig.json            # composite: true
      src/
    api/
      tsconfig.json            # references shared
      src/
    web/
      tsconfig.json            # references shared
      src/
```

`tsconfig.base.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "skipLibCheck": true,
    "incremental": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "esModuleInterop": true
  }
}
```

`packages/shared/tsconfig.json`:

```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "composite": true,
    "rootDir": "src",
    "outDir": "dist"
  },
  "include": ["src/**/*"]
}
```

`packages/api/tsconfig.json`:

```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "composite": true,
    "rootDir": "src",
    "outDir": "dist"
  },
  "references": [{ "path": "../shared" }],
  "include": ["src/**/*"]
}
```

Repo-root `tsconfig.json`:

```json
{
  "files": [],
  "references": [
    { "path": "packages/shared" },
    { "path": "packages/api" },
    { "path": "packages/web" }
  ]
}
```

Commands:

```bash
tsc --build                 # build all
tsc --build --watch         # watch mode
tsc --build --clean         # wipe outputs
tsc --build --force         # force full rebuild
```

## swc and esbuild for dev

### swc

```bash
pnpm add -D @swc/core @swc/cli tsx
```

`.swcrc`:

```json
{
  "jsc": {
    "parser": { "syntax": "typescript", "tsx": true, "decorators": true },
    "target": "es2022",
    "transform": { "react": { "runtime": "automatic" } }
  },
  "module": { "type": "es6" },
  "sourceMaps": true
}
```

Run with `tsx` (zero-config for Node):

```bash
tsx watch src/server.ts
```

`tsx` uses esbuild under the hood — ~50x faster than ts-node on cold start.

### esbuild (direct)

```bash
esbuild src/server.ts --bundle --platform=node --target=node20 --outfile=dist/server.js
```

Use esbuild for one-shot builds. Use tsup (wraps esbuild) for libraries.

## Separating type-check from transpile

### CI gates

```yaml
- name: Type check
  run: pnpm tsc --build --noEmit

- name: Lint
  run: pnpm eslint . --max-warnings=0

- name: Test
  run: pnpm vitest run --coverage
```

Keep `tsc --noEmit` in CI only. Bundlers (Next, Vite, tsup) use swc/esbuild for dev builds.

### Dev inner loop

Run three watchers in parallel:

```bash
tsc --build --watch             # type check
vitest                           # tests
tsx watch src/server.ts          # app
```

Or with `concurrently`:

```json
{
  "scripts": {
    "dev": "concurrently \"tsc -b -w\" \"tsx watch src/server.ts\" \"vitest\""
  }
}
```

## pnpm workspace setup

```yaml
# pnpm-workspace.yaml
packages:
  - "packages/*"
  - "apps/*"
```

Benefits:

- Shared, content-addressable `node_modules` cache.
- Workspace protocol (`workspace:*`) for internal packages.
- Fast installs with hard links.

```json
// apps/web/package.json
{
  "dependencies": {
    "@acme/shared": "workspace:*"
  }
}
```

## Turborepo integration

`turbo.json`:

```json
{
  "$schema": "https://turbo.build/schema.json",
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"]
    },
    "type-check": {
      "dependsOn": ["^build"],
      "outputs": []
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    },
    "lint": { "outputs": [] },
    "dev": { "cache": false, "persistent": true }
  }
}
```

Turborepo caches task outputs keyed on file hashes and env. Remote cache (Vercel Remote Cache, self-hosted) shares across the team and CI.

```bash
turbo run build              # build in dependency order, caches hits
turbo run build --filter=@acme/api  # only api + deps
turbo run type-check         # parallel tsc across packages
```

## tsconfig pitfalls that kill perf

- No `skipLibCheck` — checks every dep's `.d.ts`.
- No `incremental` — full re-check every run.
- Wide `include` — compiles test files into prod build.
- Circular project references — `tsc --build` fails or loops.
- `composite: true` without `declaration: true` — compile error.
- Using `types: ["node", "jest", "react"]` in shared base — pulls type roots into every package.

## Measuring build time

```bash
tsc --extendedDiagnostics
# prints: file count, parse/bind/check/emit time, memory, lib check time
```

Watch the "Check time" line. If it's >30s for a typical package, profile:

```bash
tsc --generateTrace trace-output
```

Open `trace-output/trace.json` in `chrome://tracing` to see hot types.

Common culprits:

- A deeply recursive conditional type instantiated across many callers.
- A generic utility type that inlines huge unions.
- Overly liberal `any`/`unknown` that prevents caching.

## Publishing libraries

- Use `tsup` or `tshy` — both wrap esbuild and produce `.d.ts` via `tsc`.
- Ship CJS + ESM with correct `exports` map.
- Emit source maps and declaration maps for good IDE navigation.

```json
// tsup.config.ts
import { defineConfig } from "tsup";
export default defineConfig({
  entry: ["src/index.ts"],
  format: ["esm", "cjs"],
  dts: true,
  sourcemap: true,
  clean: true,
  target: "es2022",
});
```

## Anti-patterns

- Running `tsc` as the build system for bundled apps — use a real bundler.
- Disabling `skipLibCheck` "for safety" — it's not.
- Copying `tsconfig` across packages instead of `extends` — drift kills productivity.
- Shipping `any` to speed up a compile — a time-bomb for later work.
- Barrel files re-exporting everything in a monorepo — forces whole-package rebuilds.

## Cross-reference

Parallels `python-modern-standards/references/tooling-uv-ruff.md` — both ecosystems converge on: fast iteration tool in dev, stricter tool in CI, aggressive caching, monorepo-aware orchestration.
