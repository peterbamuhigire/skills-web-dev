---
name: frontend-performance
description: "Frontend performance optimisation covering Core Web Vitals (LCP, INP, CLS), image optimisation, JavaScript bundling, CSS efficiency, font loading, rendering performance, network optimisation, and real-device measurement. Use when building or auditing any web frontend. Based on Impeccable (Bakaus, 2025)."
---

# Frontend Performance Skill

## Plugins (Load Alongside)

| Companion Skill | When to Load |
|---|---|
| `responsive-design` | Image and layout optimisation |
| `motion-design` | Animation performance |
| `webapp-gui-design` | Web app implementation |
| `image-compression` | Image upload compression patterns |

---

## 1. Core Web Vitals Targets

| Metric | Good | Needs Work | Poor | What It Measures |
|---|---|---|---|---|
| **LCP** | < 2.5s | 2.5-4s | > 4s | Largest visible content painted |
| **INP** | < 200ms | 200-500ms | > 500ms | Input responsiveness (replaces FID) |
| **CLS** | < 0.1 | 0.1-0.25 | > 0.25 | Unexpected layout shifts |

### Measurement Tools

- **Lab**: Lighthouse, WebPageTest, Chrome DevTools Performance tab
- **Field**: Chrome User Experience Report (CrUX), web-vitals.js library
- **Always measure on mid-range mobile** (e.g., Moto G Power) — not your development machine

---

## 2. Loading Performance

### 2.1 Image Optimisation (Usually Biggest Win)

| Technique | Impact | How |
|---|---|---|
| Modern formats | 25-50% smaller | WebP (95% support), AVIF (85% support) |
| Responsive images | Serve right size | `srcset` with width descriptors |
| Lazy loading | Defer offscreen | `loading="lazy"` on below-fold images |
| Explicit dimensions | Prevent CLS | Always set `width` and `height` attributes |
| Eager LCP image | Faster paint | `loading="eager"` + `fetchpriority="high"` on hero |
| Max 2x density | Diminishing returns | Don't serve 3x or 4x images |

```html
<!-- Hero image (LCP candidate) -->
<img
  src="hero-800.webp"
  srcset="hero-400.webp 400w, hero-800.webp 800w, hero-1200.webp 1200w"
  sizes="100vw"
  width="1200" height="600"
  alt="Description"
  loading="eager"
  fetchpriority="high"
  decoding="async"
>
```

### 2.2 JavaScript Optimisation

| Technique | Impact |
|---|---|
| Code splitting | Load only what's needed for current route |
| Tree shaking | Remove unused exports |
| Dynamic imports | Lazy-load heavy components (`import()`) |
| Defer non-critical | `<script defer>` for below-fold interactivity |
| Minification | Remove whitespace, shorten variables |
| Bundle analysis | Find and eliminate large dependencies |

**Budget**: Total JS < 200KB compressed for initial load (main bundle).

### 2.3 CSS Optimisation

| Technique | Impact |
|---|---|
| Critical CSS inline | Render above-fold without blocking |
| Remove unused CSS | PurgeCSS or framework tree-shaking |
| Avoid `@import` | Causes sequential loading (use `<link>` instead) |
| Minify | Remove whitespace and comments |
| Logical properties | Reduce RTL-specific overrides |

### 2.4 Font Loading

```css
@font-face {
  font-family: 'Brand';
  src: url('brand.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
  font-display: swap; /* Show fallback immediately, swap when loaded */
}
```

| Strategy | When |
|---|---|
| `font-display: swap` | Default — prevents invisible text |
| `font-display: optional` | Performance-critical — skip custom font if slow |
| `preload` | For critical above-fold fonts only |
| Subset | Include only needed character ranges |
| Variable fonts | One file for all weights (if using 3+ weights) |

```html
<!-- Preload critical font -->
<link rel="preload" href="brand.woff2" as="font" type="font/woff2" crossorigin>
```

### 2.5 Resource Hints

```html
<!-- DNS prefetch for third-party domains -->
<link rel="dns-prefetch" href="https://api.example.com">

<!-- Preconnect for critical third-party -->
<link rel="preconnect" href="https://cdn.example.com" crossorigin>

<!-- Prefetch next likely page -->
<link rel="prefetch" href="/dashboard">
```

---

## 3. Rendering Performance

### 3.1 Avoid Layout Thrashing

**Layout thrashing** occurs when you read layout properties then write them in a loop, forcing the browser to recalculate layout on every iteration.

```javascript
// BAD: forces layout recalculation per iteration
items.forEach(item => {
  const height = item.offsetHeight; // READ (forces layout)
  item.style.height = height + 10 + 'px'; // WRITE (invalidates layout)
});

// GOOD: batch reads, then batch writes
const heights = items.map(item => item.offsetHeight); // all READS
items.forEach((item, i) => {
  item.style.height = heights[i] + 10 + 'px'; // all WRITES
});
```

### 3.2 Properties That Trigger Layout

Avoid animating or frequently changing:

- `width`, `height`, `top`, `left`, `right`, `bottom`
- `margin`, `padding`, `border-width`
- `font-size`, `line-height`
- `display`, `position`, `float`

**Safe to animate**: `transform`, `opacity` (compositor-only, GPU-accelerated)

### 3.3 Reduce Paint Area

- Use `will-change: transform` on elements about to animate (remove after)
- Use `contain: layout` or `contain: paint` to isolate repaint areas
- Avoid large box-shadow animations (expensive paint)
- Use `content-visibility: auto` for long scrollable lists

### 3.4 Virtual Scrolling

For lists with 100+ items, virtualise — only render visible items plus a buffer.

| Platform | Library |
|---|---|
| React | `react-window`, `@tanstack/virtual` |
| Vue | `vue-virtual-scroller` |
| Vanilla | `IntersectionObserver` + manual pool |

---

## 4. Cumulative Layout Shift (CLS) Prevention

| Cause | Fix |
|---|---|
| Images without dimensions | Always set `width` and `height` attributes |
| Ads/embeds loading late | Reserve space with `aspect-ratio` or fixed container |
| Web fonts causing reflow | Use `font-display: swap` + size-adjust fallback |
| Dynamic content above viewport | Insert below current scroll position |
| Late-loading CSS | Inline critical CSS |
| Lazy components popping in | Use skeleton placeholders with exact dimensions |

```css
/* Reserve space for dynamic content */
.image-container {
  aspect-ratio: 16 / 9;
  width: 100%;
  background: var(--color-surface-alt); /* placeholder color */
}
```

---

## 5. Interaction to Next Paint (INP) Optimisation

### Keep Event Handlers Fast

- Main thread work per interaction: **< 50ms**
- Move heavy computation to Web Workers
- Use `requestIdleCallback` for non-urgent work
- Debounce rapid inputs (scroll, resize, keypress)

### Yield to Main Thread

```javascript
// Break up long tasks
async function processItems(items) {
  for (const item of items) {
    processItem(item);
    // Yield every 50ms to keep UI responsive
    if (performance.now() - start > 50) {
      await new Promise(resolve => setTimeout(resolve, 0));
      start = performance.now();
    }
  }
}
```

### Prioritise Visual Feedback

```javascript
button.addEventListener('click', async () => {
  // 1. Immediate visual feedback
  button.classList.add('loading');

  // 2. Yield to let browser paint
  await new Promise(resolve => requestAnimationFrame(resolve));

  // 3. Do the actual work
  await saveData();

  // 4. Update UI with result
  button.classList.remove('loading');
});
```

---

## 6. Network Optimisation

### Reduce Requests

- Combine small files (icon sprites, CSS bundles)
- Use HTTP/2 or HTTP/3 (multiplexing eliminates bundling need for many small files)
- **HTTP/3 (QUIC):** Runs over UDP, eliminates head-of-line blocking, handles connection migration (WiFi-to-cellular seamlessly). Beneficial for mobile users on unstable networks. Enable via CDN (Cloudflare, AWS CloudFront) or Nginx `quic` module.
- Cache aggressively: `Cache-Control: public, max-age=31536000, immutable` for hashed assets

### Compression

| Format | Support | Use |
|---|---|---|
| Brotli | 97% | Default (20-30% smaller than gzip) |
| gzip | 99% | Fallback |

### Service Workers (Offline-First)

```javascript
// Cache-first for static assets, network-first for API
self.addEventListener('fetch', event => {
  if (event.request.url.includes('/api/')) {
    event.respondWith(networkFirst(event.request));
  } else {
    event.respondWith(cacheFirst(event.request));
  }
});
```

---

## 7. Framework-Specific Optimisation

### React

- `React.memo()` for expensive pure components
- `useMemo` / `useCallback` for referential stability
- `React.lazy()` + `Suspense` for code splitting
- Avoid re-renders: lift state up or use context selectively

### Vanilla / Multi-Page

- Minimise DOM nodes (< 1,500 total, < 60 depth)
- Use event delegation (one listener on parent, not per-child)
- Prefer CSS for visual changes over JS DOM manipulation
- Use `<template>` for frequently cloned structures

---

## 8. Performance Budget

| Resource | Budget (Compressed) |
|---|---|
| HTML | < 50 KB |
| CSS (total) | < 100 KB |
| JS (initial) | < 200 KB |
| Fonts | < 100 KB (1-2 fonts max) |
| Images (above fold) | < 200 KB total |
| **Total initial load** | **< 650 KB** |

### Enforcement

- Add bundle size checks to CI pipeline
- Use `bundlesize` or `size-limit` npm packages
- Review Lighthouse score on every PR
- Alert on Core Web Vitals regressions (web-vitals.js + monitoring)

---

## 9. Measurement Checklist

Before shipping, measure on a **real mid-range device** over a **3G/4G connection**:

- [ ] LCP < 2.5s
- [ ] INP < 200ms
- [ ] CLS < 0.1
- [ ] Total initial transfer < 650 KB compressed
- [ ] No layout thrashing in Performance tab
- [ ] Images use modern formats (WebP/AVIF) with srcset
- [ ] Fonts use `font-display: swap` with preload for critical fonts
- [ ] Below-fold images are lazy loaded
- [ ] JS is code-split by route
- [ ] No unused CSS > 10 KB
- [ ] Animations run at 60fps (no janky frames)
- [ ] Service worker caches static assets (if applicable)

---

*Sources: Impeccable optimize skill (Bakaus, 2025); Web.dev — Core Web Vitals; Google Lighthouse documentation; MDN Performance guides.*
