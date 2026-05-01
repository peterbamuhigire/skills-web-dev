# PWA Tooling and Tests

Deeper configs and test scaffolds referenced from `SKILL.md`. Load only when wiring a fresh project or extending CI gates.

## Vite + Workbox (full config)

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [VitePWA({
    registerType: 'autoUpdate',
    strategies: 'generateSW',
    includeAssets: ['favicon.svg', 'robots.txt', 'offline.html'],
    manifest: { /* see Web App Manifest section in SKILL.md */ },
    workbox: {
      globPatterns: ['**/*.{js,css,html,woff2,svg,png}'],
      navigateFallback: '/offline.html',
      cleanupOutdatedCaches: true,
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

## Next.js PWA integration (full config)

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

## Lighthouse CI

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

## Playwright offline test

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
