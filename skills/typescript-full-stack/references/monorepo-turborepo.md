# Monorepo with pnpm Workspaces and Turborepo

Cross-ref: `typescript-effective` for `tsconfig` strict flags; `typescript-mastery` for
project-reference inference depth.

## Shape of a mature repo

```text
repo/
|-- apps/
|   |-- api/              Fastify or Next route handlers
|   |-- web/              Next.js App Router
|   `-- mobile/           Expo RN
|-- packages/
|   |-- schemas/          Zod contracts (leaf — no siblings depend inward)
|   |-- api-client/       tRPC / ts-rest client
|   |-- db/               Prisma or Drizzle
|   |-- ui/               React components
|   |-- config/           tsconfig, eslint, prettier
|   `-- utils/            pure TS helpers
|-- pnpm-workspace.yaml
|-- turbo.json
|-- package.json
`-- tsconfig.json         solution file (references only)
```

Rule: `packages/schemas` and `packages/utils` sit at the leaves. Nothing they import
from should live in the same repo except `packages/config` (types only). Everything
else may depend on them.

## pnpm workspace config

`pnpm-workspace.yaml`:

```yaml
packages:
  - "apps/*"
  - "packages/*"
```

Root `package.json`:

```json
{
  "name": "acme",
  "private": true,
  "packageManager": "pnpm@9.12.0",
  "engines": { "node": ">=22" },
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev --parallel",
    "lint": "turbo run lint",
    "test": "turbo run test",
    "type-check": "turbo run type-check",
    "clean": "turbo run clean && rm -rf node_modules"
  },
  "devDependencies": {
    "turbo": "^2.1.0",
    "typescript": "5.6.3"
  }
}
```

Use `workspace:*` protocol for intra-repo deps — never file paths, never semver:

```json
{
  "dependencies": {
    "@acme/schemas": "workspace:*",
    "@acme/db": "workspace:*"
  }
}
```

## Turborepo pipeline

`turbo.json` (v2 syntax):

```json
{
  "$schema": "https://turbo.build/schema.json",
  "ui": "stream",
  "globalEnv": ["NODE_ENV", "CI"],
  "globalDependencies": ["**/.env.*", "tsconfig.base.json"],
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "inputs": ["src/**", "tsconfig.json", "package.json"],
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"]
    },
    "type-check": {
      "dependsOn": ["^build"],
      "inputs": ["src/**", "tsconfig.json"],
      "outputs": []
    },
    "lint": {
      "inputs": ["src/**", ".eslintrc*", "eslint.config.*"],
      "outputs": []
    },
    "test": {
      "dependsOn": ["^build"],
      "inputs": ["src/**", "test/**", "vitest.config.*"],
      "outputs": ["coverage/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "clean": { "cache": false }
  }
}
```

Key rules:

- `^build` runs the dependency graph's `build` first — so `apps/api` waits for
  `packages/db` and `packages/schemas` to compile.
- Declare `inputs` explicitly; stray `README.md` changes must not invalidate cache.
- Mark `outputs` precisely; `.next/cache` must be excluded to prevent cache poisoning.
- `dev` is non-cacheable and persistent (long-running).

## Remote cache

Two options:

1. Vercel Remote Cache — `turbo login && turbo link`. Free for OSS. Zero infra.
2. Self-hosted via [turborepo-remote-cache](https://github.com/ducktors/turborepo-remote-cache)
   behind S3/MinIO. Set `TURBO_API`, `TURBO_TOKEN`, `TURBO_TEAM` in CI.

CI enables it via env:

```yaml
env:
  TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
  TURBO_TEAM: ${{ vars.TURBO_TEAM }}
  TURBO_REMOTE_CACHE_SIGNATURE_KEY: ${{ secrets.TURBO_SIG }}
```

Decision rule: no remote cache until CI wall-clock exceeds 3 minutes. After that,
remote cache typically pays back within a week.

## TypeScript project references

`packages/config/tsconfig.base.json`:

```json
{
  "$schema": "https://json.schemastore.org/tsconfig",
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2023"],
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "useUnknownInCatchVariables": true,
    "forceConsistentCasingInFileNames": true,
    "isolatedModules": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "composite": true,
    "incremental": true
  }
}
```

Per-package `tsconfig.json` (leaf package):

```json
{
  "extends": "@acme/config/tsconfig.base.json",
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src",
    "tsBuildInfoFile": "dist/.tsbuildinfo"
  },
  "include": ["src/**/*"],
  "exclude": ["dist", "node_modules"]
}
```

Consumer package (`apps/api/tsconfig.json`) references upstream:

```json
{
  "extends": "@acme/config/tsconfig.base.json",
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src"
  },
  "references": [
    { "path": "../../packages/schemas" },
    { "path": "../../packages/db" }
  ],
  "include": ["src/**/*"]
}
```

Root `tsconfig.json` is a solution file:

```json
{
  "files": [],
  "references": [
    { "path": "packages/schemas" },
    { "path": "packages/db" },
    { "path": "packages/api-client" },
    { "path": "apps/api" },
    { "path": "apps/web" }
  ]
}
```

Now `tsc --build` walks the graph; incremental typecheck only re-checks what changed.

## Config as a package

`packages/config/package.json`:

```json
{
  "name": "@acme/config",
  "version": "0.0.0",
  "private": true,
  "exports": {
    "./tsconfig.base.json": "./tsconfig.base.json",
    "./tsconfig.nextjs.json": "./tsconfig.nextjs.json",
    "./eslint": "./eslint.config.js",
    "./prettier": "./prettier.config.js"
  }
}
```

Consumers extend shared configs without path-traversal hacks.

## Common failure modes

- Forgetting `"composite": true` — project references silently skip the package.
- Mixing `dependencies` and `devDependencies` wrong — a package used at runtime in
  `apps/api` must live in `dependencies`, otherwise `pnpm deploy` strips it.
- Cache hits without correct `inputs` — builds succeed but include stale code. Audit
  `outputs` and `inputs` quarterly.
- Running `tsc` per package in parallel without references — dramatically slower than
  a single `tsc --build` from root.
- Publishing `workspace:*` to npm — use `pnpm publish` which rewrites the protocol;
  never `npm publish` directly.

## Decision rules

```text
Single app, single team, < 20k LOC         -> single package, no monorepo
Web + API sharing types                    -> monorepo mandatory
Mobile + web + API                         -> monorepo; Expo has well-known pitfalls
5+ services, independent deploy cadence    -> monorepo + polyrepo-per-deployable is also fine
Need to ship an SDK externally             -> monorepo, publish one package only
```

## Migration path from npm/yarn

1. Commit current state.
2. Convert workspace manifests to `workspace:*` deps.
3. `rm -rf node_modules package-lock.json yarn.lock && pnpm install`.
4. Add `turbo.json`, migrate `npm run` calls to `turbo run` calls.
5. Add TypeScript project references incrementally — one leaf package at a time.
6. Wire remote cache last, once local caching proves correct.
