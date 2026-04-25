---
name: responsive-design
description: Mobile-first responsive design standards covering content-driven breakpoints,
  container queries, pointer/hover detection, safe areas, responsive images, layout
  adaptation patterns, and real-device testing. Cross-platform web skill. Based on...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Responsive Design Skill
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Mobile-first responsive design standards covering content-driven breakpoints, container queries, pointer/hover detection, safe areas, responsive images, layout adaptation patterns, and real-device testing. Cross-platform web skill. Based on...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `responsive-design` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| UX quality | Responsive breakpoint audit | Markdown doc covering content-driven breakpoints, container queries, and pointer/hover detection per page | `docs/web/responsive-audit-checkout.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Plugins (Load Alongside)

| Companion Skill | When to Load |
|---|---|
| `practical-ui-design` | Visual system (colour, type, spacing) |
| `webapp-gui-design` | Web app-specific implementations |
| `form-ux-design` | Responsive form patterns |
| `frontend-performance` | Image and loading optimisation |
| `ai-slop-prevention` | Avoid generic responsive templates |

---

## 1. Mobile-First (Non-Negotiable)

### Base Styles = Mobile

Write base CSS for the smallest screen. Add complexity with `min-width` media queries.

```css
/* Base: mobile */
.layout { display: flex; flex-direction: column; gap: var(--space-md); }

/* Tablet and up */
@media (min-width: 768px) {
  .layout { flex-direction: row; }
}

/* Desktop */
@media (min-width: 1200px) {
  .layout { max-width: 1200px; margin-inline: auto; }
}
```

### Why Not Desktop-First?

- Mobile forces you to prioritise content (what actually matters)
- Adding complexity (`min-width`) is easier than removing it (`max-width`)
- Mobile traffic is 55-70% for most products

### NEVER Use `max-width` Queries

`max-width` queries indicate desktop-first thinking. Refactor to `min-width`.

---

## 2. Content-Driven Breakpoints

### Don't Chase Devices

There are too many screen sizes to target specific devices. Instead, let **content** determine where the layout breaks.

### The Three-Breakpoint System

Most designs need only **three breakpoints**:

| Name | Typical Range | Purpose |
|---|---|---|
| **Compact** | < 600px | Single column, stacked layout |
| **Medium** | 600-1024px | Two columns, side-by-side where appropriate |
| **Expanded** | > 1024px | Full layout, multi-column, sidebars |

### How to Find Breakpoints

1. Start with mobile layout
2. Slowly widen the browser
3. When the layout looks awkward or wastes space — that's your breakpoint
4. Add a `min-width` query at that exact pixel value
5. **Never add a breakpoint "just because"** — only when content demands it

---

## 3. Detect Input Method (Not Just Screen Size)

### Pointer Queries

Screen size does NOT tell you about the input device. A 1024px iPad is touch; a 1024px laptop has a mouse.

```css
/* Mouse/trackpad — fine pointer, hover available */
@media (pointer: fine) and (hover: hover) {
  .button { padding: 8px 16px; }
  .tooltip { display: block; } /* hover tooltips work */
}

/* Touch — coarse pointer, no reliable hover */
@media (pointer: coarse) {
  .button { padding: 12px 24px; min-height: 48px; }
  .tooltip { display: none; } /* use tap/long-press instead */
}
```

### Key Combinations

| Query | Device Type | Design Implication |
|---|---|---|
| `pointer: fine` + `hover: hover` | Mouse/trackpad | Hover states, smaller targets OK |
| `pointer: coarse` + `hover: none` | Phone/tablet touch | 48px targets, no hover-dependent features |
| `pointer: fine` + `hover: none` | Stylus | Fine targets OK, no hover |
| `pointer: coarse` + `hover: hover` | Game controller, TV remote | Large targets, hover possible |

### Rule

**Never hide essential functionality behind hover.** Touch users cannot hover. Always provide tap/click alternatives.

---

## 4. Safe Areas (Notches and Dynamic Islands)

Modern devices have notches, rounded corners, and dynamic islands that obscure content.

```css
/* Apply safe area padding */
.app-shell {
  padding-top: env(safe-area-inset-top);
  padding-right: env(safe-area-inset-right);
  padding-bottom: env(safe-area-inset-bottom);
  padding-left: env(safe-area-inset-left);
}

/* Combine with existing padding */
.bottom-nav {
  padding-bottom: calc(16px + env(safe-area-inset-bottom));
}
```

### Meta Tag Required

```html
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
```

The `viewport-fit=cover` enables `env(safe-area-inset-*)` values.

---

## 5. Container Queries (Component-Level Responsiveness)

Media queries respond to the **viewport**. Container queries respond to the **parent container** — making components truly reusable regardless of where they're placed.

```css
/* Define a containment context */
.card-container {
  container-type: inline-size;
  container-name: card;
}

/* Respond to container width, not viewport */
@container card (min-width: 400px) {
  .card { display: grid; grid-template-columns: 200px 1fr; }
}

@container card (max-width: 399px) {
  .card { display: flex; flex-direction: column; }
}
```

### When to Use Container vs Media Queries

| Use Container Queries | Use Media Queries |
|---|---|
| Reusable components (cards, widgets) | Page-level layout |
| Sidebar vs main content adaptations | Navigation structure |
| Components used in different contexts | Typography scale changes |
| Design system components | Global spacing adjustments |

---

## 6. Responsive Images

### srcset with Width Descriptors

```html
<img
  src="photo-800.jpg"
  srcset="photo-400.jpg 400w, photo-800.jpg 800w, photo-1200.jpg 1200w"
  sizes="(min-width: 1024px) 33vw, (min-width: 600px) 50vw, 100vw"
  alt="Descriptive alt text"
  loading="lazy"
  decoding="async"
>
```

### Art Direction with `<picture>`

```html
<picture>
  <source media="(min-width: 1024px)" srcset="hero-wide.jpg">
  <source media="(min-width: 600px)" srcset="hero-medium.jpg">
  <img src="hero-mobile.jpg" alt="Hero image description">
</picture>
```

### Rules

- Serve images at **2x display density** maximum (3x is negligible quality gain)
- Use `loading="lazy"` for below-the-fold images
- Use `loading="eager"` for hero/above-the-fold images (LCP)
- Use modern formats: WebP (95% support), AVIF (85% support)
- Set explicit `width` and `height` attributes to prevent layout shift (CLS)

---

## 7. Layout Adaptation Patterns

### Navigation

| Screen | Pattern |
|---|---|
| **Compact** (< 600px) | Bottom tab bar (3-5 items) + hamburger for overflow |
| **Medium** (600-1024px) | Compact horizontal nav (icons + labels) or rail |
| **Expanded** (> 1024px) | Full horizontal nav with dropdowns, or sidebar |

### Tables → Cards

```css
/* Desktop: standard table */
.data-table { display: table; }

/* Mobile: stack as cards */
@media (max-width: 599px) {
  .data-table, .data-table tbody, .data-table tr, .data-table td {
    display: block;
  }
  .data-table thead { display: none; }
  .data-table td::before {
    content: attr(data-label);
    font-weight: bold;
    display: block;
  }
}
```

### Grid Adaptation

```css
/* Self-adjusting grid — no media queries needed */
.auto-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(280px, 100%), 1fr));
  gap: var(--space-md);
}
```

### Content Priority

| Element | Compact | Medium | Expanded |
|---|---|---|---|
| Primary content | Full width | 2/3 width | Main column |
| Secondary content | Below primary | 1/3 width or tabbed | Sidebar |
| Tertiary content | Hidden or collapsible | Collapsible | Right panel |
| Decorative images | Hidden | Reduced | Full size |

---

## 8. Fluid Typography

```css
/* Fluid type: scales between 18px (at 320px viewport) and 22px (at 1200px) */
body {
  font-size: clamp(1.125rem, 1rem + 0.5vw, 1.375rem);
}

/* Fluid heading */
h1 {
  font-size: clamp(2rem, 1.5rem + 2vw, 3.5rem);
}
```

### Rules

- Set `min` and `max` bounds with `clamp()` — never let text grow/shrink without limits
- Reduce heading scale on mobile to prevent excessive wrapping
- Body text minimum: **16px** (never smaller, even on mobile)
- Test at browser zoom levels: 100%, 150%, 200% (WCAG requirement)

---

## 9. Testing Protocol

### Don't Trust DevTools Alone

DevTools device emulation does NOT accurately represent:

- Touch behaviour and gesture support
- Font rendering differences
- Keyboard/input method behaviour
- Performance on actual hardware
- Safe area rendering
- Haptic feedback and motion sensitivity

### Required Testing Matrix

| Dimension | Test On |
|---|---|
| **iOS** | iPhone SE (small), iPhone 15 (standard), iPad |
| **Android** | Budget phone (e.g., Samsung A series), flagship, tablet |
| **Desktop** | 1366px (common laptop), 1920px (standard), 2560px (wide) |
| **Input** | Mouse, trackpad, touch, keyboard-only |
| **Browser** | Chrome, Safari, Firefox (minimum) |
| **Orientation** | Portrait + landscape on all mobile/tablet |
| **Zoom** | 100%, 150%, 200% |

### Checklist Per Breakpoint

- [ ] Content is readable without horizontal scrolling
- [ ] Touch targets are >= 48px on touch devices
- [ ] Navigation is reachable and usable
- [ ] Images scale appropriately (no overflow, no pixelation)
- [ ] Forms are usable (fields aren't tiny, labels visible)
- [ ] Modals/dialogs fit within viewport
- [ ] Fixed/sticky elements don't obscure content
- [ ] Safe areas are respected on notched devices
- [ ] No content is cut off or hidden unintentionally
- [ ] Performance is acceptable on mid-range mobile (< 3s load)

---

## 10. Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| Desktop-first with `max-width` overrides | Rewrite mobile-first with `min-width` |
| Device-specific breakpoints (320px, 375px, 414px) | Use content-driven breakpoints |
| Hiding content on mobile with `display: none` | Restructure or use progressive disclosure |
| Hover-only interactions | Add tap/click alternatives |
| Fixed pixel widths for containers | Use `%`, `fr`, `min()`, `clamp()` |
| Text in images (unscalable) | Use real text with CSS styling |
| Assuming portrait orientation | Test and design for both orientations |
| Ignoring safe areas | Apply `env(safe-area-inset-*)` |

---

*Sources: Impeccable responsive-design reference (Bakaus, 2025); MDN Web Docs — Responsive Design; Web.dev — Learn Responsive Design.*