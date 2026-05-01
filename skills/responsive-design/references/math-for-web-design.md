# Math for Web Design Patterns

Use this reference when a web layout, visual system, animation, or responsive component needs precise sizing, spacing, proportion, or motion rather than trial-and-error CSS.

## Core Rules

- Prefer relationships over fixed numbers: ratios, percentages, `fr`, `rem`, `em`, `ch`, `vw`, `min()`, `max()`, `clamp()`, and `calc()`.
- Use content-driven breakpoints. Resize the layout until the content becomes cramped, stretched, or visually awkward; that width is the real breakpoint.
- Use `aspect-ratio` for media, cards, video, gallery tiles, and placeholders so images do not distort or cause layout shift.
- Use `clamp(min, preferred, max)` for fluid type, section spacing, grid gaps, and component widths where a value should scale smoothly but stay bounded.
- Use `minmax(min(ideal, 100%), 1fr)` with `repeat(auto-fit, ...)` for responsive grids that do not overflow on narrow containers.
- Round intentionally. For display values, progress, and pixel-derived JS values, choose `round`, `floor`, or `ceil` based on the desired visual or business meaning.
- Avoid comparing decimal values directly in JavaScript animation/layout logic; use a small tolerance when equality matters.

## Layout Math

- `aspect-ratio: 16 / 9` for video and wide media.
- `aspect-ratio: 4 / 3` for service-card images and thumbnails.
- `aspect-ratio: 1 / 1` for avatars and logos where cropping is acceptable.
- Use golden-ratio-like proportions sparingly for sidebars or editorial layouts: around `38% / 62%`. Do not force it where content does not fit.

```css
:root {
  --measure: 65ch;
  --space-section: clamp(3rem, 7vw, 7rem);
  --text-hero: clamp(2.25rem, 6vw, 5rem);
}

.auto-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(18rem, 100%), 1fr));
  gap: clamp(1rem, 2vw, 2rem);
}
```

## Typography Math

- Build type scales from a ratio, but cap extremes with `clamp()`.
- Use compact ratios such as `1.2` or `1.25` for dashboards and dense SaaS screens.
- Use more expressive ratios such as `1.333` or `1.5` for editorial pages and landing pages.
- Keep body line length around `50-75` characters using `max-inline-size: 60ch` to `70ch`.
- Use `rem` for font size, `em` for component-relative spacing, and `ch` for measure.

## Color Math

- Use HSL/OKLCH-style thinking when adjusting palettes: hue chooses color family, saturation controls intensity, lightness controls value.
- Check contrast numerically, not by eye.
- When creating shades, change lightness in deliberate steps; avoid arbitrary one-off hex values that break the visual system.
- Use alpha compositing cautiously. Semi-transparent text or overlays can fail contrast when background images change.

## Motion Math

- Animate transform and opacity, not layout properties.
- Use easing curves to express acceleration. Default to ease-out for entrances, ease-in for exits, and ease-in-out for state changes.
- Keep stagger delay mathematical and bounded: `delay = min(index * 60ms, 480ms)`.
- Use trigonometry only when it adds real value: circular menus, orbiting elements, radial charts, wave effects, or custom cursor/particle paths.
- Always provide a `prefers-reduced-motion` fallback.

## JavaScript Precision Notes

```js
const EPSILON = 0.001;
const closeEnough = Math.abs(actual - expected) < EPSILON;
const percent = Math.round((current / total) * 100);
```

- Use `toFixed()` only for display, not continued calculation.
- For layout measurements, read once, calculate, then write DOM styles together to avoid layout thrash.
- For animations, use `requestAnimationFrame()` and time deltas rather than assuming a fixed frame rate.

## Acceptance Checks

- No fixed widths cause overflow at `320px`.
- Fluid values have min and max bounds.
- Grids collapse naturally before media queries are added.
- Aspect-ratio boxes reserve media space before images load.
- Typography respects browser zoom and user font-size preferences.
- Motion uses purposeful easing and remains stable under reduced-motion settings.
