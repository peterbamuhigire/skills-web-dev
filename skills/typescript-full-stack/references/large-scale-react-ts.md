# Large-scale React + TypeScript architecture

Distilled from *Large Scale Apps with React and TypeScript* (Damiano Fusco) and observed production patterns. Use when scaling beyond a single-product SPA into multi-package, multi-team, or multi-environment territory.

## Project layout (single app)

```text
src/
  models/                # interfaces and domain types only — no logic
    Item.interface.ts
    User.interface.ts
  api/
    ApiClient.ts         # transport: fetch wrapper, headers, retries
    items/
      ItemsApiClient.ts          # live
      ItemsApiClient.mock.ts     # in-memory mock for tests + Storybook
      ItemsApiClient.interface.ts
  store/                 # state management (Zustand/Redux Toolkit/MobX)
    items.store.ts
  config/
    Config.interface.ts
    config.dev.ts
    config.prod.ts
    ConfigProvider.tsx
  localization/
    i18n.ts
    formatters/
      numberFormatter.ts
      dateFormatter.ts
  primitives/            # design-system atoms (no domain knowledge)
    ElText.tsx
    ElButton.tsx
    ElModal.tsx
  components/            # higher-level composites that use primitives + store
    Item.component.tsx
    ItemsList.component.tsx
  views/                 # page-level compositions
    Items.view.tsx
  hooks/
    useModal.ts
    useLocalization.ts
  test/
    setup.ts
```

Rule: dependency arrows only point inward. `primitives` know nothing of `store` or `api`; `views` may depend on everything below them.

## File naming convention (Fusco)

- `Foo.interface.ts` for type-only modules — clarifies intent and lets bundlers tree-shake.
- `Foo.component.tsx` for components, `Foo.view.tsx` for routed pages.
- `useFoo.ts` for hooks. `*.mock.ts` for test doubles.
- `*.test.ts(x)` colocated next to the file it tests.

The dot-suffix convention beats subfolders for grep-ability across large repos.

## Config strategy

1. Define `Config.interface.ts` with every key the app needs.
2. Build environment-specific files (`config.dev.ts`, `config.prod.ts`) that satisfy the interface.
3. Resolve at boot via `import.meta.env.MODE` (Vite) or `process.env.NODE_ENV` and inject through a `ConfigProvider` Context.
4. NEVER read `process.env` directly inside components. Read once at boot, pass via Context, then `useConfig()` everywhere else.
5. Validate the resolved config with Zod before mounting the app — fail loud if a key is missing.

## API client pattern

- One `HttpClient` (transport) — handles base URL, auth headers, JSON parsing, retry/backoff, AbortController plumbing.
- One `ApiClient` per domain (`ItemsApiClient`, `OrdersApiClient`) wrapping `HttpClient` with typed methods.
- Each domain client has an `*.interface.ts` plus a `*.mock.ts`. Tests, Storybook, and offline mode all swap to mocks via `ApiClientProvider`.
- Never pass raw `fetch` Response objects through the store. Parse + validate at the client boundary.

## Localization

- `i18next` + `react-i18next` for strings; `Intl.NumberFormat` / `Intl.DateTimeFormat` for numbers and dates (do not pull in moment/date-fns just for formatting).
- Keep translation JSON in `localization/locales/<lang>/<namespace>.json`.
- Expose a `useLocalization()` hook that returns `{ t, locale, setLocale, formatNumber, formatDate }` so components don't import i18next directly. Swappable later.
- Currency, percentage, units: derive from `locale + currencyCode`, not hard-coded `$` / `,`.

## Primitives (design-system atoms)

- `Atomic Design`: atoms (`ElText`, `ElIcon`, `ElButton`) → molecules (`ElField`, `ElCard`) → organisms (`ItemsList`).
- Primitives accept a `variant` prop, never raw `className`. Variant decides Tailwind classes via a lookup map. This blocks one-off styling drift.
- Primitives never call the store, never call the API, never use i18n directly. They take strings and callbacks.
- Modals: implement as `.ts` (no JSX) returning a render function plus a `useModal()` hook for open/close state. Avoids stuck-modal bugs from re-renders.

## When to extract a component library

Trigger conditions (any one):

- Two apps in the monorepo need the same primitive.
- A primitive has stabilised over 3+ sprints with no API change.
- Outside teams want to consume it.

Workflow: Vite library mode (or `tsup`), set `package.json` `exports` map, ship ESM + types, mark `react`/`react-dom` as `peerDependencies`, never bundle them. Publish to a private npm scope (`@org/ui`).

## Monorepo turning points

Move from single repo to monorepo (pnpm + Turborepo or Nx) when:

- 2+ deployable apps share more than ~5 modules.
- Build time exceeds 60s and incremental builds would help.
- Different teams own different packages and need independent versioning.

Until then, a single repo with the layout above scales fine to ~50 KLoC.

## Testing tier (Vitest + RTL)

- Vitest replaces Jest in modern Vite/Next projects: faster, native ESM, native TS, same `expect` API.
- Test the `*.component.tsx` via React Testing Library — assert on rendered text and roles, not implementation details.
- Test `*.store.ts`, `*.api.ts`, formatters as plain TS unit tests.
- Mock the API client by injecting the `*.mock.ts` via `ApiClientProvider` in the test wrapper. Don't mock `fetch` globally.

## Anti-patterns (Fusco-grade)

- Global singletons for store, config, or API client. Use Context + Providers so tests can swap.
- Reading env vars inside leaf components.
- A "components" folder with 200 files at one level. Group by domain or by atomic-design tier.
- `index.ts` barrel files that re-export 50 components — they kill tree-shaking and slow `tsc`. Import direct paths.
- Translating strings inside primitives (couples primitives to i18n).
- Putting all interfaces in one `types.ts` — split per domain so the build can prune.
- Skipping `Config.interface.ts`: leads to scattered `process.env.X ?? "default"` reads that drift across files.
