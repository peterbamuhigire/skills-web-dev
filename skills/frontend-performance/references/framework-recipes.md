# Framework-Specific Recipes

Parent skill: `../SKILL.md`.

Thin wrappers around the core decisions for the main frameworks in this repository.

## React

- Route-based code split with `React.lazy()` + `Suspense`.
- `React.memo()` on expensive pure components — measure first; the default is to not memoise.
- `useMemo` / `useCallback` only for referential stability that downstream memoised components rely on. Do not sprinkle everywhere.
- Colocate state near the consumer. Lift only when two siblings share. Use context with selector libraries (`use-context-selector`) to avoid whole-tree re-renders.
- Prefer uncontrolled inputs and `defer`/`transition` (`useDeferredValue`, `useTransition`) for large lists.
- Disable React strict-mode double-invocation analysis in perf profiling builds.

## Next.js App Router

- Server components by default. Client components only where interactivity or hooks require it.
- Use `next/image` with explicit `priority` on the LCP image and explicit `sizes` for responsive breakpoints.
- Streaming with `loading.tsx` and `Suspense` for above-fold-then-below-fold layering.
- Parallel routes + `@modal` slots keep non-critical UI off the critical path.
- `dynamic(() => import(...), { ssr: false })` for heavy client-only widgets (map, editor, chart library).
- Route segment config: `export const dynamic = 'force-static'` or `revalidate = N` where data allows.
- Middleware only for lightweight concerns (rewrite, auth cookie check); heavy logic belongs in route handlers.

Pair with `nextjs-app-router` for the full routing, caching, and RSC pattern set.

## Vue / Nuxt

- `defineAsyncComponent()` for heavy widgets.
- `<KeepAlive>` for tabbed layouts to avoid re-mount cost, but audit memory.
- Nuxt: `useLazyAsyncData` for non-critical data; avoid cascading `await` on the server path.

## Vanilla / multi-page

- Under 1,500 total DOM nodes and under 60 nesting depth as a firm ceiling.
- Event delegation: one listener on the parent, not per child.
- Prefer CSS transitions/animations over JS-driven DOM mutation.
- Use `<template>` and `<slot>` for frequently cloned structures.
- Service Worker for repeat-visit caching once the core flow is stable.

## Service workers (offline-first)

```javascript
self.addEventListener('fetch', event => {
  if (event.request.url.includes('/api/')) {
    event.respondWith(networkFirst(event.request));
  } else {
    event.respondWith(cacheFirst(event.request));
  }
});
```

Rules:

- Never cache first-party HTML without a versioning story, or users get stuck on stale shells.
- Version the cache name on deploy; old caches must be deleted in `activate`.
- Surface SW errors to the RUM pipeline — silent SW failures cause invisible regressions.

## Measurement tools cheat-sheet

- Lab: Lighthouse (CI), WebPageTest (occasional deep dive), Chrome DevTools Performance panel.
- Field: `web-vitals` JS beaconed to the RUM backend, Chrome UX Report (CrUX) for public pages.
- Always test on a real mid-range device (Moto G Power class) with throttled network — not the development machine.
