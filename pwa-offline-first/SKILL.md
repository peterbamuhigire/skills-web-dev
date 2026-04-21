---
name: pwa-offline-first
description: Use when building offline-first Progressive Web Apps — Service Worker lifecycle,
  Workbox caching strategies, IndexedDB via Dexie.js, Background Sync for queued writes,
  Web Push notifications, Lighthouse gates, and Next.js PWA integration. Default for
  apps that must work on EDGE/2G or intermittent connectivity.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# PWA Offline-First

<!-- dual-compat-start -->
## Use When

- Use when building offline-first Progressive Web Apps — Service Worker lifecycle, Workbox caching strategies, IndexedDB via Dexie.js, Background Sync for queued writes, Web Push notifications, Lighthouse gates, and Next.js PWA integration. Default for apps that must work on EDGE/2G or intermittent connectivity.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `pwa-offline-first` or would be better handled by a more specific companion skill.
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

## Why Offline-First for East Africa

Connectivity in Uganda, Kenya, and Tanzania is bimodal: urban fibre and 4G in Kampala CBD, Westlands, or Masaki, then EDGE/2G the moment a user boards a boda, enters a Bushenyi cooperative, or works inside a hospital ward with poor indoor coverage. Field workers counting inventory in Mbale, community health workers in Arua, and agents confirming MTN MoMo or Airtel Money disbursements in village kiosks all tolerate zero bars for minutes at a time. Co-working spaces on Kampala Road and Ngong Road suffer 30-second uplink stalls mid-upload. Every write path must queue locally and sync when connectivity returns; every read path must fall back to a cached response rather than a spinner.

## PWA Checklist

- Served over HTTPS (localhost exempt); Web App Manifest present and linked from `<head>`.
- Service Worker registered at the narrowest scope needed.
- Icons at 192x192, 512x512, and maskable variants.
- `beforeinstallprompt` captured and surfaced as an in-app install button.
- Lighthouse PWA score greater than or equal to 90.
- Core content renders with JavaScript disabled; interactive features degrade gracefully.
- `start_url` returns HTTP 200 when offline (served from cache).

## Web App Manifest

```json
{
  "name": "Field Inventory Uganda",
  "short_name": "FieldInv",
  "id": "/",
  "start_url": "/?source=pwa",
  "scope": "/",
  "display": "standalone",
  "orientation": "portrait",
  "theme_color": "#0f172a",
  "background_color": "#ffffff",
  "lang": "en-UG",
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ],
  "shortcuts": [
    { "name": "New Visit", "url": "/visits/new" },
    { "name": "Pending Sync", "url": "/sync" }
  ]
}
```

Link from head: `<link rel="manifest" href="/manifest.webmanifest">`.

## Service Worker Lifecycle

States: `installing` -> `installed (waiting)` -> `activating` -> `activated`. A new version waits until all old-worker tabs close, unless `skipWaiting()` is called.

```javascript
// sw.js
const CACHE_VERSION = 'v2025-11-01';
const SHELL_CACHE = `shell-${CACHE_VERSION}`;

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(SHELL_CACHE).then((cache) =>
    cache.addAll(['/', '/offline.html', '/styles/app.css', '/scripts/app.js'])));
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(caches.keys().then((keys) =>
    Promise.all(keys.filter((k) => k !== SHELL_CACHE).map((k) => caches.delete(k)))
  ).then(() => self.clients.claim()));
});
```

Client-side update prompt:

```javascript
navigator.serviceWorker.register('/sw.js').then((reg) => {
  reg.addEventListener('updatefound', () => {
    const incoming = reg.installing;
    incoming?.addEventListener('statechange', () => {
      if (incoming.state === 'installed' && navigator.serviceWorker.controller)
        showUpdateToast(() => incoming.postMessage({ type: 'SKIP_WAITING' }));
    });
  });
});
```

## Workbox Setup

`vite-plugin-pwa` for Vite, `next-pwa` for Next.js. Default to `generateSW`; switch to `injectManifest` only when custom Service Worker logic is required.

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [VitePWA({
    registerType: 'autoUpdate',
    strategies: 'generateSW',
    includeAssets: ['favicon.svg', 'robots.txt', 'offline.html'],
    manifest: { /* see Web App Manifest section */ },
    workbox: {
      globPatterns: ['**/*.{js,css,html,woff2,svg,png}'],
      navigateFallback: '/offline.html',
      runtimeCaching: [
        { urlPattern: ({ url }) => url.pathname.startsWith('/api/catalog'),
          handler: 'NetworkFirst',
          options: { cacheName: 'api-catalog', networkTimeoutSeconds: 10, expiration: { maxAgeSeconds: 3600 } } },
        { urlPattern: ({ request }) => request.destination === 'image',
          handler: 'CacheFirst',
          options: { cacheName: 'images', expiration: { maxAgeSeconds: 2592000, maxEntries: 200 } } }
      ]
    }
  })]
});
```

## Caching Strategies

| Strategy | Use Case | TTL |
|---|---|---|
| NetworkFirst | Catalog, user profile, dashboards | 10 min |
| CacheFirst | Fonts, hashed JS/CSS, versioned images | 30 days |
| StaleWhileRevalidate | Help docs, blog, release notes | 24 hours |
| NetworkOnly | POST/PUT/DELETE, payment, auth | Never cached |

```javascript
import { registerRoute } from 'workbox-routing';
import { NetworkFirst, CacheFirst, StaleWhileRevalidate, NetworkOnly } from 'workbox-strategies';
import { ExpirationPlugin } from 'workbox-expiration';

registerRoute(({ url }) => url.pathname.startsWith('/api/profile'),
  new NetworkFirst({ cacheName: 'profile', networkTimeoutSeconds: 10 }));
registerRoute(({ request }) => request.destination === 'font',
  new CacheFirst({ cacheName: 'fonts',
    plugins: [new ExpirationPlugin({ maxAgeSeconds: 60 * 60 * 24 * 30 })] }));
registerRoute(({ url }) => url.pathname.startsWith('/help'),
  new StaleWhileRevalidate({ cacheName: 'help-docs' }));
registerRoute(({ url }) => url.pathname.startsWith('/api/payments'),
  new NetworkOnly(), 'POST');
```

Never cache mutation verbs. Workbox caches POST responses only when asked; doing so is almost always a bug.

## App Shell Architecture

The shell is the minimal HTML, CSS, and JavaScript needed to render UI chrome. Precached on install; content is fetched at runtime and layered in.

```text
App Shell (cached)  ---  API content (network + cache fallback)
  header, nav, skeleton     /api/visits, /api/customers
  critical CSS              images, documents
  app.js bootstrap          falls back to IndexedDB when offline
```

```javascript
// sw.ts (injectManifest mode)
import { precacheAndRoute, createHandlerBoundToURL } from 'workbox-precaching';
import { NavigationRoute, registerRoute } from 'workbox-routing';

precacheAndRoute(self.__WB_MANIFEST);
const handler = createHandlerBoundToURL('/index.html');
registerRoute(new NavigationRoute(handler, { denylist: [/^\/api\//] }));
```

## IndexedDB with Dexie.js

Raw IndexedDB is verbose and transaction-leaky. Dexie wraps it with promises, typed tables, and migrations. Install with `npm install dexie`.

```typescript
// src/db/index.ts
import Dexie, { Table } from 'dexie';
type SyncStatus = 'synced' | 'pending' | 'error';

export interface Customer { id?: number; externalId: string; name: string; phone: string; district: string; syncStatus: SyncStatus; updatedAt: number; }
export interface Visit { id?: number; customerId: number; notes: string; amountUgx: number; capturedAt: number; syncStatus: SyncStatus; }
export interface PendingSync { id?: number; endpoint: string; method: 'POST' | 'PUT' | 'DELETE'; body: string; attemptCount: number; createdAt: number; lastError?: string; }

export class FieldDB extends Dexie {
  customers!: Table<Customer, number>;
  visits!: Table<Visit, number>;
  pendingSyncs!: Table<PendingSync, number>;
  constructor() {
    super('field-inventory-db');
    this.version(1).stores({
      customers: '++id, externalId, district, syncStatus, [district+syncStatus]',
      visits: '++id, customerId, capturedAt, syncStatus',
      pendingSyncs: '++id, endpoint, createdAt'
    });
  }
}

export const db = new FieldDB();
export const queuePendingCustomers = () => db.customers.where('syncStatus').equals('pending').toArray();
export const markCustomerSynced = (id: number) => db.customers.update(id, { syncStatus: 'synced' });
```

Compound indexes (`[district+syncStatus]`) let you query "all pending customers in Bushenyi" without a full-table scan.

## Offline Form Submissions

Write to IndexedDB first. Network is a best-effort add-on.

```typescript
import { db } from './db';

export async function saveVisit(input: Omit<Visit, 'id' | 'syncStatus'>) {
  const id = await db.visits.add({ ...input, syncStatus: 'pending' });
  await db.pendingSyncs.add({
    endpoint: '/api/visits', method: 'POST',
    body: JSON.stringify({ ...input, localId: id }),
    attemptCount: 0, createdAt: Date.now()
  });
  const reg = await navigator.serviceWorker.ready;
  if ('sync' in reg) await (reg as any).sync.register('sync-pending');
  return id;
}
```

The user sees "Saved" immediately; the Service Worker drains the queue on reconnect.

## Background Sync API

Feature-detect first; fall back to an `online` listener on platforms without Background Sync (Safari as of iOS 17).

```javascript
// sw.js
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-pending') event.waitUntil(syncPendingData());
});

async function syncPendingData() {
  const db = await openDB();
  for (const row of await db.getAll('pendingSyncs')) {
    try {
      const res = await fetch(row.endpoint, {
        method: row.method,
        headers: { 'Content-Type': 'application/json' },
        body: row.body
      });
      if (res.ok) await db.delete('pendingSyncs', row.id);
      else if (res.status === 409) await handleConflict(db, row, await res.json());
      else await db.put('pendingSyncs', { ...row, attemptCount: row.attemptCount + 1, lastError: `${res.status}` });
    } catch (err) {
      await db.put('pendingSyncs', { ...row, attemptCount: row.attemptCount + 1, lastError: String(err) });
      throw err;
    }
  }
}
```

Fallback for Safari:

```javascript
window.addEventListener('online', () => {
  navigator.serviceWorker?.controller?.postMessage({ type: 'MANUAL_SYNC' });
});
```

## Conflict Resolution

1. **Last-write-wins** — trivial; acceptable for non-financial fields (notes, address corrections). Client timestamp overwrites server.
2. **Server-authoritative** — server rejects stale writes with HTTP 409 + canonical record. Use for money, stock quantities, MoMo refs.
3. **Timestamp-based merge** — each field carries an `updatedAt`; newer value per-field wins. Use when two offline clients edit the same record.

```typescript
async function handleConflict(db: IDBDatabase, row: PendingSync, server: any) {
  const local = JSON.parse(row.body);
  const merged = {
    ...server,
    notes: local.updatedAt > server.updatedAt ? local.notes : server.notes,
    amountUgx: server.amountUgx, // money: server wins
    updatedAt: Date.now()
  };
  await fetch(row.endpoint, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'If-Match': server.etag },
    body: JSON.stringify(merged)
  });
}
```

Money defaults to server-authoritative: the ledger is the single source of truth.

## Push Notifications

Generate a VAPID keypair once per environment (`npx web-push generate-vapid-keys`) and store the private key on the server.

```typescript
// Client
export async function subscribePush(vapidPublicKey: string) {
  if ((await Notification.requestPermission()) !== 'granted') return null;
  const reg = await navigator.serviceWorker.ready;
  const subscription = await reg.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
  });
  await fetch('/api/push/subscribe', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(subscription)
  });
  return subscription;
}
```

```javascript
// sw.js
self.addEventListener('push', (event) => {
  const data = event.data?.json() ?? { title: 'Update', body: '' };
  event.waitUntil(self.registration.showNotification(data.title, {
    body: data.body, icon: '/icons/icon-192.png', badge: '/icons/badge-72.png',
    data: { url: data.url ?? '/' }
  }));
});
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(self.clients.openWindow(event.notification.data.url));
});
```

## Testing PWAs

```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI
on: [pull_request]
jobs:
  lhci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci && npm run build
      - run: npx @lhci/cli@0.13.x autorun --collect.staticDistDir=./dist
```

Playwright offline test:

```typescript
import { test, expect } from '@playwright/test';

test('visit saves offline then syncs', async ({ page, context }) => {
  await page.goto('/');
  await context.setOffline(true);
  await page.getByRole('button', { name: 'New Visit' }).click();
  await page.getByLabel('Notes').fill('Boda delivered 12 kg matooke');
  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page.getByText('Saved offline')).toBeVisible();
  await context.setOffline(false);
  await expect(page.getByText('Synced')).toBeVisible({ timeout: 15000 });
});
```

## Next.js PWA Integration

```javascript
// next.config.js
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development',
  runtimeCaching: [
    { urlPattern: /^\/api\/payments\/.*$/, handler: 'NetworkOnly' },
    { urlPattern: /^\/api\/catalog\/.*$/, handler: 'NetworkFirst',
      options: { cacheName: 'api-catalog', networkTimeoutSeconds: 10, expiration: { maxAgeSeconds: 3600 } } },
    { urlPattern: /\.(?:png|jpg|jpeg|svg|webp)$/, handler: 'CacheFirst',
      options: { cacheName: 'images', expiration: { maxEntries: 200, maxAgeSeconds: 60 * 60 * 24 * 30 } } }
  ]
});

module.exports = withPWA({ reactStrictMode: true });
```

Payment and authentication routes must be `NetworkOnly`; a cached 200 on `/api/payments/confirm` is a double-spend waiting to happen.

## Performance Budget

- Time to Interactive less than or equal to 3 s on Slow 3G (400 Kbps, 400 ms RTT).
- First Contentful Paint less than or equal to 1.8 s on Slow 3G; offline cache load less than or equal to 1 s.
- Precache manifest less than or equal to 1 MB; critical-path JS less than or equal to 170 KB compressed.
- Largest Contentful Paint less than or equal to 2.5 s at P75 (Core Web Vitals "Good").
- Cumulative Layout Shift less than 0.1; Interaction to Next Paint less than 200 ms.

Enforce via Lighthouse CI assertions; a red budget fails the build rather than warning.

## Companion Skills

- `nextjs-app-router` — Next.js App Router patterns, layouts, server/client components.
- `frontend-performance` — Core Web Vitals, bundle budget, render-path analysis.
- `image-compression` — Client-side image compression before offline upload queueing.

## Sources

- Workbox — `developer.chrome.com/docs/workbox`; Dexie.js — `dexie.org/docs`
- MDN Service Worker API — `developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API`
- web.dev PWA — `web.dev/progressive-web-apps`; Lighthouse CI — `github.com/GoogleChrome/lighthouse-ci`
- *Building Progressive Web Apps* — Tal Ater (O'Reilly)
