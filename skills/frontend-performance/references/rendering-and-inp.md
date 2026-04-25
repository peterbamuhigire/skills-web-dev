# Rendering, CLS, and INP — Deep Dive

Parent skill: `../SKILL.md`.

Everything that happens after bytes arrive: layout, paint, main-thread budget, and the INP interaction model that replaced FID.

## Layout thrashing

Forcing a layout recalculation by reading a layout property after writing one:

```javascript
// BAD: forces layout per iteration
items.forEach(item => {
  const height = item.offsetHeight;         // READ (forces layout)
  item.style.height = (height + 10) + 'px'; // WRITE (invalidates layout)
});

// GOOD: batch reads, then batch writes
const heights = items.map(item => item.offsetHeight);
items.forEach((item, i) => {
  item.style.height = (heights[i] + 10) + 'px';
});
```

Modern FLIP helpers (`fastdom`) or `ResizeObserver` callbacks already batch correctly; hand-rolled loops are the main offender.

## Layout-triggering properties

Avoid animating or frequently mutating:

- `width`, `height`, `top`, `left`, `right`, `bottom`
- `margin`, `padding`, `border-width`
- `font-size`, `line-height`
- `display`, `position`, `float`

Compositor-only, GPU-accelerated, safe to animate at 60fps: `transform`, `opacity`, `filter` (for small elements).

## Paint reduction

- `will-change: transform` on elements about to animate, removed immediately after.
- `contain: layout` or `contain: paint` to isolate repaint areas for independent widgets.
- Avoid large `box-shadow` or `filter: blur()` animations — extremely expensive paint.
- `content-visibility: auto` on long scrollable lists to skip offscreen rendering.

## Virtual scrolling

For lists with 100+ items, render only the visible window plus a small buffer.

| Platform | Library |
|---|---|
| React | `@tanstack/virtual`, `react-window` |
| Vue | `vue-virtual-scroller` |
| Vanilla | `IntersectionObserver` + manual pool |

## CLS prevention

| Cause | Fix |
|---|---|
| Images without dimensions | Always set `width` and `height` (or CSS `aspect-ratio`) |
| Ads / embeds loading late | Reserve space with `aspect-ratio` or fixed container |
| Web fonts reflowing text | `font-display: swap` plus `size-adjust` on the fallback |
| Dynamic content above viewport | Insert below the current scroll position |
| Late-loading CSS | Inline critical CSS |
| Lazy components popping in | Skeletons with exact dimensions |

```css
.image-container {
  aspect-ratio: 16 / 9;
  width: 100%;
  background: var(--color-surface-alt);
}
```

## INP optimisation (<200ms field target)

Rules for every event handler:

- Main-thread work per interaction stays under 50ms.
- Heavy computation moves to a Web Worker.
- Non-urgent work runs in `requestIdleCallback` or `scheduler.postTask({ priority: 'background' })`.
- Rapid inputs (scroll, resize, keypress) are debounced or throttled.

Yielding to the main thread inside a long task:

```javascript
async function processItems(items) {
  let start = performance.now();
  for (const item of items) {
    processItem(item);
    if (performance.now() - start > 50) {
      await new Promise(resolve => setTimeout(resolve, 0));
      start = performance.now();
    }
  }
}
```

Prioritising visible feedback before work:

```javascript
button.addEventListener('click', async () => {
  button.classList.add('loading');
  await new Promise(resolve => requestAnimationFrame(resolve));
  await saveData();
  button.classList.remove('loading');
});
```

Use `scheduler.yield()` where available (Chromium 129+) instead of the `setTimeout(0)` dance.
