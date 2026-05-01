# Loading Performance — Deep Dive

Parent skill: `../SKILL.md`.

Covers image, JavaScript, CSS, font, and resource-hint tactics that push LCP below the 2.5s field target and keep the initial transfer under the declared budget.

## Image optimisation (usually the biggest LCP win)

| Technique | Impact | How |
|---|---|---|
| Modern formats | 25–50% smaller | WebP (~95% support), AVIF (~85% support) with fallbacks |
| Responsive `srcset` | Serve the right size | Width descriptors plus `sizes` attribute |
| Lazy loading | Defer offscreen | `loading="lazy"` on below-fold images only |
| Explicit dimensions | Prevent CLS | Always set `width` and `height` attributes |
| Eager LCP image | Faster paint | `loading="eager"` + `fetchpriority="high"` on hero |
| Max 2x density | Diminishing returns | Do not serve 3x/4x raster images |

Canonical hero markup:

```html
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

## JavaScript optimisation

| Technique | Impact |
|---|---|
| Route-based code splitting | Load only what the current route needs |
| Tree shaking | Remove unused exports (requires ESM) |
| Dynamic `import()` | Lazy-load heavy widgets (editor, charts, maps) |
| `<script defer>` | Non-critical interactivity below the fold |
| Minification + compression | Terser/esbuild + Brotli at the edge |
| Bundle analysis | `source-map-explorer` or `rollup-plugin-visualizer` on every PR |

Budget: total initial JS under 200KB compressed for the main bundle. Route chunks under 100KB each.

## CSS optimisation

| Technique | Impact |
|---|---|
| Critical CSS inlined | Renders above-fold without a blocking roundtrip |
| Unused-CSS removal | PurgeCSS / Tailwind JIT / framework tree-shaking |
| Avoid `@import` | Causes sequential loading — use `<link>` instead |
| Logical properties | Reduces RTL-specific overrides |
| Minify + compress | Remove whitespace and comments |

## Font loading

```css
@font-face {
  font-family: 'Brand';
  src: url('brand.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}
```

| Strategy | When to use |
|---|---|
| `font-display: swap` | Default — prevents invisible text |
| `font-display: optional` | Performance-critical — skip custom font if slow network |
| `preload` | Only for critical above-fold fonts |
| Subset | Include only the character ranges actually rendered |
| Variable fonts | One file for 3+ weights or variable axes |

```html
<link rel="preload" href="brand.woff2" as="font" type="font/woff2" crossorigin>
```

Pair the fallback font with `size-adjust`, `ascent-override`, and `descent-override` to eliminate font-swap CLS.

## Resource hints

```html
<link rel="dns-prefetch" href="https://api.example.com">
<link rel="preconnect" href="https://cdn.example.com" crossorigin>
<link rel="prefetch" href="/dashboard">
```

Rules:

- `preconnect` is strictly rationed — three origins maximum. Every extra connection competes for bandwidth during the critical path.
- `prefetch` only for routes with >30% probability of next-navigation based on analytics, otherwise it is waste.
- `preload` the LCP image and critical font. Never preload the whole bundle.

## Compression and transport

| Format | Support | Use |
|---|---|---|
| Brotli | ~97% | Default, 20–30% smaller than gzip |
| gzip | ~99% | Fallback for ancient clients |

HTTP/2 and HTTP/3 (QUIC) remove the old "one request per asset hurts" rule — stop concatenating small files once HTTP/2 is in place, but keep hashed long-cache headers (`Cache-Control: public, max-age=31536000, immutable`).
