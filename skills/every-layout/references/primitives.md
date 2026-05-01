# Every Layout — Practical Extraction

Source: *Every Layout* by Heydon Pickering & Andy Bell (every-layout.dev).

## Meta-Principles

### 1. Algorithmic layout, not artisanal layout
The web is a fluid medium of unknown viewport, font size, zoom, language, and content length. Trying to *prescribe* exact pixel positions ("artisanal" layout, like print) leads to brittle code with cascading `@media` breakpoints. **Describe the rules and let the browser solve the layout.** You are the browser's mentor, not its micro-manager (John Allsopp, *The Dao of Web Design*). Each primitive is a tiny algorithm parameterised by CSS custom properties; the browser computes the rest.

### 2. Axiomatic CSS
Style the *context*, not the individual element. Far-reaching universal rules + the cascade overriding them in exceptions. The "lobotomized owl" `* + *` (Heydon Pickering, *A List Apart*) is the canonical axiom: any element preceded by another element gets a top margin — a margin is a property of the *relationship* between two siblings, not of an element alone. This is what makes the **Stack** primitive composable.

### 3. Intrinsic Web Design (Jen Simmons)
Tools that let elements size themselves *from their content* — `min-content`, `max-content`, `fit-content`, `flex-basis`, `auto`, `ch` units, `min()`/`max()`/`clamp()`. Prefer intrinsic to extrinsic sizing; provide *suggestions* (`max-inline-size`, `flex-basis`) rather than *prescriptions* (`width`). A button's natural width is the width of its content — leave it alone.

### 4. `min()` / `max()` / `clamp()` as in-CSS conditionals
`min(250px, 100%)` returns the smaller of the two — caps a value while still allowing it to shrink. This single function eliminates many container-query workarounds, especially inside `repeat(auto-fit, minmax(min(250px, 100%), 1fr))` (the Grid primitive). `clamp(min, ideal, max)` powers fluid type without breakpoints.

### 5. Logical properties over physical
Use `margin-inline`, `margin-block`, `inline-size`, `block-size`, `inset-block-start`, `padding-inline-end`. They honour writing mode and `dir="rtl"` automatically. `margin-right` becomes wrong as soon as direction flips.

### 6. Why `display:flex` + `gap` beats margin for spacing siblings
`gap` only inserts space *between* items, never on the outer edges, regardless of count, wrapping, or order. It's direction-agnostic. Margins on each child require the owl selector or `:last-child` resets to avoid extraneous outer margin. Use the owl (`* + *` with `margin-block-start`) only where flex/grid `gap` is unsuitable — the Stack itself uses `flex-direction: column` *without* `gap` so that `margin: auto` can act as a "splitter".

### 7. Modular scale
Define spacing and font sizes as a geometric series of CSS custom properties (`--s-2`, `--s-1`, `--s0`, `--s1`, `--s2`, …) on `:root`. Every primitive's `--space` defaults to a point on this scale. `--measure: 60ch` is the global maximum line-length axiom.

### 8. Composition over configuration
Each primitive does **one thing**. Stack only inserts vertical margin. Box only handles padding/border/background. Grid only does grid columns. Real layouts emerge from *nesting* primitives. Because each primitive sets `--space` on children (not the parent), nested same-class primitives override correctly.

### 9. Custom-property placement
Set `--space` on the *children* (`.stack > * + * { margin-block-start: var(--space, 1.5rem); }`), not the parent. Setting it on the parent breaks nested same-class instances.

### 10. Exceptions via the cascade, not specificity wars
`* + *` has zero specificity, so a sibling selector like `.stack-exception, .stack-exception + *` wins by source order at the same specificity. Don't escalate to `!important`.

### 11. Global resets every primitive assumes
```css
* { box-sizing: border-box; }
img, video, svg { max-inline-size: 100%; }
:root { --measure: 60ch; --s1: 1.5rem; --border-thin: 1px; }
```

---

## The Primitives

### 1. Stack

**What it is.** A primitive that injects equal vertical (`block`) margin between successive flow elements via their common parent. One concern: vertical rhythm.

**When to use it.** Anywhere flow content stacks vertically — form fields, article body (paragraphs/headings/images/blockquotes), card internals, dialog body, sidebar nav. If elements stack, a Stack should be in effect. Grid cells *contain* Stacks; they aren't themselves Stacked (the grid handles that spacing).

**Core CSS.**
```css
.stack {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.stack > * {
  margin-block: 0;
}

.stack > * + * {
  margin-block-start: var(--space, 1.5rem);
}
```

**Splitter variant** (push everything after child *n* to the bottom — useful for cards with footers):
```css
.stack > :nth-child(2) { margin-block-end: auto; }
.stack:only-child { block-size: 100%; }
```

**Recursive variant** (drop `>` to apply at any nesting depth — beware list/table side-effects):
```css
.stack * + * { margin-block-start: 1.5rem; }
```

**Nested variants** (different scales without recursion):
```css
[class^='stack'] > * { margin-block: 0; }
.stack-large > * + * { margin-block-start: 3rem; }
.stack-small > * + * { margin-block-end: 0.5rem; }
```

**Per-element exception:**
```css
.stack-exception, .stack-exception + * { --space: 3rem; }
```

**Custom properties.** `--space` (default `1.5rem` / `var(--s1)`).
**Component props.** `space`, `recursive` (boolean), `splitAfter` (integer).

**Composition.** Stack is the outermost wrapper of nearly every region. Boxes, Centers, Grids, Sidebars, Switchers go *inside* a Stack. Stack also lives inside Box (card body), Sidebar (nav column), Cover (page sections).

**Gotchas.**
- `margin: 0 auto` on a child Center inside a Stack zeroes the Stack's `margin-block-start`. Use `margin-inline: auto` on the Center.
- Stack uses `flex-direction: column`, *not* `gap`, so `margin: auto` can act as the splitter.
- `<label>` needs `display: block` for vertical margins to apply.
- Don't use Stack inside Cluster/Switcher/Reel/Grid — those primitives own their own spacing via `gap`.

---

### 2. Box

**What it is.** A padded container with optional border/background. Owns padding, border, background-color, color inheritance. Nothing else.

**When to use it.** Cards, callouts, notes, banners, dialog bodies — any *visible* rectangular region. If you want "a `<div>` with padding and a border," that's a Box.

**Core CSS.**
```css
.box {
  padding: var(--s1);
  border: var(--border-thin) solid;
  outline: var(--border-thin) transparent;
  outline-offset: calc(var(--border-thin) * -1);
  --color-light: #fff;
  --color-dark: #000;
  color: var(--color-dark);
  background-color: var(--color-light);
}

.box * {
  color: inherit;
}

.box.invert {
  color: var(--color-light);
  background-color: var(--color-dark);
}
```

**Custom properties.** `--s1`, `--border-thin`, `--color-light`, `--color-dark`.
**Component props.** `padding`, `borderWidth`, `invert`.

**Composition.** Box is *the* visual atom. Wraps a Stack to make a card. `Box > Center > Stack` makes a single-column page. A "Box with a header" is a Box containing two child Boxes (the header gets `invert`).

**Gotchas.**
- Padding must be on **all sides or none**. Asymmetric padding is something else (probably a Sidebar) — don't deform the Box.
- Always include the transparent `outline` + negative `outline-offset` so Windows High Contrast mode redraws the box edge when backgrounds are stripped.
- Don't use `border` to separate child elements (they double up); use a Stack with a border on the owl.
- `box-sizing: border-box` is assumed globally; don't redeclare on `.box`. (Center is the one primitive that overrides to `content-box`.)

---

### 3. Center

**What it is.** Horizontally centers a block of content inside its parent and caps its width at the typographic measure (~60ch).

**When to use it.** Article main column, prose pages, single-column landing sections — anywhere content needs centring with a maximum readable line length. Combine with Cover for both-axis centring.

**Core CSS.**
```css
.center {
  box-sizing: content-box;
  max-inline-size: 60ch;
  margin-inline: auto;
  padding-inline-start: var(--s1);
  padding-inline-end: var(--s1);
}
```

**Intrinsic-centering variant** (centres each child to its own content width too):
```css
.center {
  box-sizing: content-box;
  max-inline-size: 60ch;
  margin-inline: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}
```

**Component props.** `max` (default `var(--measure)`), `gutters`, `intrinsic`, `andText` (`text-align: center`).

**Composition.** Common pattern: `Box > Center > Stack`. Use `intrinsic` inside a Cover to centre a button or callout on both axes.

**Gotchas.**
- Use `margin-inline: auto`, **never** `margin: 0 auto` — the latter zeroes vertical margins applied by an enclosing Stack.
- Override `box-sizing: border-box` to `content-box` so padding adds *outside* the 60ch threshold (otherwise padding eats the measure).
- Centred content can disappear from zoomed-in users' viewports if the surrounding layout isn't flexible.

---

### 4. Cluster

**What it is.** A wrapping flex row of items separated by a uniform `gap`, with configurable justification and alignment. Not a grid — no equal columns, no shared height.

**When to use it.** Inline groupings of disparate-sized items: tag lists, button groups, footer link rows, breadcrumbs, action toolbars, badges, navigation chips. "A bunch of inline things wrap when they run out of room."

**Core CSS.**
```css
.cluster {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space, 1rem);
  justify-content: center;
  align-items: center;
}
```

**Component props.** `space` (default `var(--s1)`), `justify`, `align`.

**Composition.** Usually a leaf containing text + buttons + icons. Mark up as `<ul role="list">` with `<li>` children when conceptually a list.

**Gotchas.**
- Don't put Stacks inside a Cluster expecting row layout — Cluster is for inline groupings.
- Don't add fallback margins; they'd compound with `gap`.
- Items keep *intrinsic* widths — for equal-width items, use Switcher or Grid.

---

### 5. Sidebar

**What it is.** Two side-by-side elements: one (the sidebar) has a fixed width, the other consumes the rest, *unless* the available space is too narrow, in which case both stack vertically and each takes 100%. A "quantum" layout: configuration is decided by the *container*, not the viewport.

**When to use it.** Media objects (avatar + body, image + caption), input + button pairs, app shells with a real sidebar, label/control pairs, cards with a thumbnail.

**Core CSS.**
```css
.with-sidebar {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.sidebar {
  flex-basis: 20rem;
  flex-grow: 1;
}

.not-sidebar {
  flex-basis: 0;
  flex-grow: 999;
  min-inline-size: 50%;
}
```

**Why it works.** `.not-sidebar`'s `flex-grow: 999` eats all available space; the sidebar's `flex-basis` is subtracted from total available space, fixing its width. When `.not-sidebar` would shrink to ≤ 50%, `min-inline-size: 50%` forces it onto the next row, where wrapping makes both children full-width.

**Intrinsic sidebar.** Omit `flex-basis` on `.sidebar` — its width becomes the natural width of its content (e.g. an `<img width="15rem">` makes a 15rem sidebar).

**Component props.** `side` (`"left"`/`"right"`), `sideWidth`, `contentMin` (% threshold for wrapping, default `"50%"`), `space`, `noStretch`.

**Composition.** App shell: `Sidebar(nav-Stack, main-Center-wrapped-in-div)`. Media object: `Sidebar(img, p)`. Search input: `Sidebar(input, button)` with `side="right"` and `contentMin="66.666%"`.

**Gotchas.**
- Default `align-items: stretch` makes both columns equal height — usually wanted, but pass `noStretch` (`align-items: flex-start`) when one child is an image (otherwise it distorts).
- `@media` width queries cannot solve this — they reflect viewport, not container width. Sidebar is the canonical container-aware layout.
- When nesting a Center inside a Sidebar, wrap it in an extra `<div>` so the Sidebar's flex logic operates on the wrapper, not the Center.

---

### 6. Switcher

**What it is.** A row of equal-width children that *all simultaneously* switch from horizontal to vertical when the container hits a threshold. Unlike Sidebar, every child is equal; unlike Cluster, items don't wrap individually.

**When to use it.** Pricing tiers, equal-weight feature columns, numbered "step" rows, peer card lineups. Threshold is usually `var(--measure)`.

**Core CSS.**
```css
.switcher {
  display: flex;
  flex-wrap: wrap;
  gap: var(--gutter, var(--s1));
  --threshold: 30rem;
}

.switcher > * {
  flex-grow: 1;
  flex-basis: calc((var(--threshold) - 100%) * 999);
}

.switcher > :nth-last-child(n+5),
.switcher > :nth-last-child(n+5) ~ * {
  flex-basis: 100%;
}
```

**The trick.** `calc((var(--threshold) - 100%) * 999)` — when container > threshold, the value is hugely negative (clamped to 0, items go horizontal); when container < threshold, the value is hugely positive (clamped to 100%, items wrap vertically). A 1-line container query.

**Component props.** `threshold` (default `var(--measure)`), `space`, `limit` (max horizontal items, default 4).

**Composition.** Children are typically Box-containing-Stack cards. Switcher itself sits in the page Stack.

**Gotchas.**
- Children wider than the threshold still try to share space; the algorithm assumes peers.
- `--threshold` is a *container* breakpoint, not a viewport one — that's the point.
- Above `limit` items, the row goes vertical even if there's room. Set `limit` very high to disable.

---

### 7. Cover

**What it is.** A vertical flex container with a `min-block-size` (typically `100vh`) and a designated principal child that auto-margins itself to centre vertically. Optional header above and footer below.

**When to use it.** Hero sections, splash screens, full-viewport landing intros, "above the fold" splash with header/footer, modal-like full-bleed messages.

**Core CSS.**
```css
.cover {
  --space: var(--s1);
  display: flex;
  flex-direction: column;
  min-block-size: 100vh;
  padding: var(--space);
}

.cover > * {
  margin-block: var(--s1);
}

.cover > :first-child:not(h1) {
  margin-block-start: 0;
}

.cover > :last-child:not(h1) {
  margin-block-end: 0;
}

.cover > h1 {
  margin-block: auto;
}
```

**Component props.** `centered` (selector for principal child, default `"h1"`), `space`, `minHeight` (default `"100vh"`), `noPad`.

**Composition.** Cover wraps a Center (with `intrinsic`) for both-axis centring of a content-width element. Cover usually sits at the top of a page-level Stack.

**Gotchas.**
- One `<h1>` per page. Multiple Covers — only the first uses `<h1>`; subsequent ones use `<h2>` and the `centered` prop changes.
- `box-sizing: border-box` is required so padding doesn't add to `100vh` and trigger scrollbars.
- The principal child's `margin-block: auto` does the centring — don't override its margins.

---

### 8. Grid

**What it is.** CSS-Grid-based "automatic columns": items reflow into as many columns as fit, each at least `--minimum` wide, sharing space and height. The closest thing to "design to a grid" the dynamic web allows.

**When to use it.** Card galleries, product grids, image teasers, tile dashboards. When N peer items must align on both axes and reflow without `@media`.

**Core CSS.**
```css
.grid {
  display: grid;
  grid-gap: 1rem;
  --minimum: 20ch;
}

@supports (width: min(var(--minimum), 100%)) {
  .grid {
    grid-template-columns: repeat(auto-fit, minmax(min(var(--minimum), 100%), 1fr));
  }
}
```

**Why `min(var(--minimum), 100%)`.** Without `min()`, in a container narrower than `--minimum`, the grid item overflows horizontally. `min()` caps the minimum at `100%` of the container — eliminates overflow without JS or container queries.

**Component props.** `min` (default `"250px"`), `space` (default `var(--s1)`).

**Composition.** Grid items are typically `Box > Stack` cards. Grid sits inside the page Stack.

**Gotchas.**
- All items share the largest item's height (`align-items: stretch` default) — usually wanted.
- `auto-fit` collapses empty tracks; use `auto-fill` to reserve space for trailing empty columns.
- This isn't a true container query — it can't change card *internals* at a threshold, only column count.
- Without `min()` support, grid is implicitly a single column.

---

### 9. Frame

**What it is.** Forces a child (typically `<img>` / `<video>`) into a fixed aspect ratio with `object-fit: cover` cropping.

**When to use it.** Image cards in a Grid where every thumbnail must be 16:9, hero video frames, avatar circles (1:1), responsive embeds — anywhere the *shape* of the slot is constant regardless of source dimensions.

**Core CSS.**
```css
.frame {
  --n: 16;
  --d: 9;
  aspect-ratio: var(--n) / var(--d);
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
}

.frame > img,
.frame > video {
  inline-size: 100%;
  block-size: 100%;
  object-fit: cover;
}
```

**Component props.** `ratio` (e.g. `"16:9"`, `"4:3"`, `"1:1"`).

**Composition.** Drop a Frame inside a Box-Stack card for consistent thumbnails. Switch shape per orientation:
```css
@media (orientation: portrait) { .frame { aspect-ratio: 1 / 1; } }
```

**Gotchas.**
- Exactly **one** child element. Multiple children break the centring.
- `object-fit: cover` crops; use `contain` to show the entire image (with letterboxing).
- Pre-`aspect-ratio` browsers need the padding-bottom hack; the canonical CSS assumes support.

---

### 10. Reel

**What it is.** A horizontally scrolling single-row strip of fixed-width items. Native browser scrolling — no JS for the layout itself.

**When to use it.** Netflix-style content rows, image galleries, mobile horizontal nav, tag scrollers — anywhere `overflow-x` scrolling beats wrapping. Especially good on touch.

**Core CSS.**
```css
.reel {
  --space: 1rem;
  --color-light: #fff;
  --color-dark: #000;
  --reel-height: auto;
  --item-width: 25ch;
  display: flex;
  block-size: var(--reel-height);
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-color: var(--color-light) var(--color-dark);
}

.reel::-webkit-scrollbar { block-size: 1rem; }
.reel::-webkit-scrollbar-track { background-color: var(--color-dark); }
.reel::-webkit-scrollbar-thumb {
  background-color: var(--color-dark);
  background-image: linear-gradient(var(--color-dark) 0, var(--color-dark) 0.25rem, var(--color-light) 0.25rem, var(--color-light) 0.75rem, var(--color-dark) 0.75rem);
}

.reel > * {
  flex: 0 0 var(--item-width);
}

.reel > img {
  block-size: 100%;
  flex-basis: auto;
  width: auto;
}

.reel > * + * {
  margin-inline-start: var(--space);
}

.reel.overflowing:not(.no-bar) {
  padding-block-end: var(--space);
}

.reel.no-bar { scrollbar-width: none; }
.reel.no-bar::-webkit-scrollbar { display: none; }
```

**Optional JS.** A small IIFE adds `.overflowing` when `scrollWidth > clientWidth` (using `ResizeObserver` + `MutationObserver`) so bottom padding only appears when the scrollbar appears.

**Component props.** `itemWidth` (default `"auto"`), `space`, `height`, `noBar`.

**Composition.** Children are usually Box-Stack cards. Reel sits in the page Stack. Mark up as `role="list"` with `role="listitem"` children.

**Gotchas.**
- Use `flex: 0 0 var(--item-width)` — plain `width` is overridden by default `flex-shrink: 1`.
- Avoid bidirectional scrolling on a single element (WCAG 1.4.10 Reflow failure). Always pair `overflow-x: auto` with `overflow-y: hidden`.
- Visible scrollbars improve affordance; hide (`noBar`) only when another visual cue (shadow, button, dots) signals scrollability.

---

### 11. Imposter

**What it is.** Absolutely (or fixed) positions an element centred over its positioning ancestor.

**When to use it.** Modal dialogs, popovers, tooltips, video captions, "play" buttons over a thumbnail, alerts — anything that visually overlays other content.

**Core CSS.**
```css
.imposter {
  position: var(--positioning, absolute);
  inset-block-start: 50%;
  inset-inline-start: 50%;
  transform: translate(-50%, -50%);
}

.imposter.contain {
  --margin: 0px;
  overflow: auto;
  max-inline-size: calc(100% - (var(--margin) * 2));
  max-block-size: calc(100% - (var(--margin) * 2));
}
```

**Component props.** `breakout` (allow overflow outside container), `margin`, `fixed` (use `position: fixed` for viewport-anchored dialogs).

**Composition.** Place an Imposter inside any container with `position: relative`. The Imposter usually contains a Box (dialog body) which contains a Stack.

**Gotchas.**
- The translate trick is the only no-flex method that handles unknown content height robustly. Without `.contain`, content taller than the parent overflows visually.
- For real dialogs prefer `<dialog>` wrapped by an Imposter (`fixed`) — covers focus, ESC, backdrop.
- Set `aria-hidden="true"` on obscured siblings, or trap focus inside the Imposter so screen readers don't read through.
- `--margin` *must* include a unit (`0px`, not `0`) for `calc()` to be valid.

---

### 12. Icon

**What it is.** An SVG sized in `em` / `cap` / `ex` units so it scales with adjacent text, with optional `inline-flex` wrapping to control the gap to its label.

**When to use it.** Any inline icon next to text — buttons, links, list items, status indicators, decorative icons in headings.

**Core CSS.**
```css
.icon {
  height: 0.75em;
  height: 1cap;
  width: 0.75em;
  width: 1cap;
}

.with-icon {
  display: inline-flex;
  align-items: baseline;
}

.with-icon .icon {
  margin-inline-end: var(--space, 0.5em);
}
```

**Recommended SVG markup.**
```html
<svg viewBox="0 0 10 10" width="0.75em" height="0.75em" stroke="currentColor" stroke-width="2">
  <path d="M1,1 9,9 M9,1 1,9" />
</svg>
```

**Component props.** `space`, `label` (when supplied, applies `role="img"` + `aria-label`).

**Composition.** Icon nests inside `<button>`, `<a>`, headings. Without a `.with-icon` wrapper, the natural U+0020 word space between SVG and text gives a sensible default gap that flips correctly under `dir="rtl"`.

**Gotchas.**
- `0.75em` ≈ uppercase letter height across most fonts; `1cap` is the precise emerging unit. Use `1ex` for lowercase contexts.
- Set `width`/`height` *attributes* on the SVG so it doesn't render gigantic when CSS fails to load.
- Use `stroke="currentColor"` (or `fill="currentColor"`) so icons inherit text colour.
- For RTL, prefer the natural word-space approach (no `.with-icon`) — `dir="rtl"` flips it for free. With `margin`, use `margin-inline-end` (not `margin-right`).
- Always provide an accessible label: visually-hidden span, `<title>` inside SVG, or `aria-label` on the parent button.

---

## Cheat Sheet — Picking the Primitive

| You want… | Use |
| --- | --- |
| Vertical rhythm between siblings | **Stack** |
| Padded card / callout / panel | **Box** |
| Centre a column at measure | **Center** |
| Wrapping inline group (tags, chips) | **Cluster** |
| Two-up that becomes stacked when narrow | **Sidebar** |
| N equal columns that all switch to vertical at threshold | **Switcher** |
| Full-viewport hero with vertically centred principal child | **Cover** |
| Auto-flowing card grid that reflows | **Grid** |
| Crop media to a fixed aspect ratio | **Frame** |
| Horizontally scrolling row | **Reel** |
| Overlay / dialog / tooltip | **Imposter** |
| Inline icon scaling with text | **Icon** |

## The composition reflex

A typical page is a *tree of primitives*:

```
Cover (hero)
  Stack (header / h1 / footer area)
Stack (page body)
  Center
    Stack (article)
      h1
      p, p, blockquote, p
      Grid (gallery)
        Box > Stack (card) × N
      Switcher
        Box × 3 (pricing tiers)
      Sidebar
        img / Stack (text)
Imposter (dialog, when triggered)
  Box > Stack
```

When asked to build a UI, the agent's job is: **decompose the problem into the smallest set of primitives, set their custom properties from the modular scale, and *compose by nesting* — not by writing new CSS.**
