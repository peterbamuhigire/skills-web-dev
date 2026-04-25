---
name: every-layout
description: Use when building or reviewing CSS layouts for any web or app interface — provides the 12 algorithmic layout primitives (Stack, Box, Center, Cluster, Sidebar, Switcher, Cover, Grid, Frame, Reel, Imposter, Icon) from Pickering & Bell's *Every Layout*, plus the meta-principles (axiomatic CSS, intrinsic web design, container-aware layout via `min`/`max`/`clamp`) that let layouts respond to content, not breakpoints. Use this instead of writing bespoke flex/grid CSS for common compositions.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Every Layout — CSS Layout Primitives

Source: Heydon Pickering & Andy Bell, *Every Layout* (every-layout.dev).

## Use when

- Building any web or app UI that needs responsive layout — pages, cards, hero sections, dashboards, modals.
- Reviewing CSS for over-use of `@media` breakpoints, hard-coded widths, or duplicated spacing rules.
- Extracting reusable layout components from one-off bespoke CSS.
- Migrating a design system from breakpoint-driven CSS to container-aware, intrinsic CSS.
- Authoring layout for a JS framework (React, Vue, Svelte) where each primitive becomes a component.

## Do not use when

- The task is purely about visual styling (colour, typography, motion) — load `practical-ui-design`, `color-theory`, `motion-design` instead.
- The task is about choosing colours or building a design system token set — load `color-theory` or `design-system`.
- The task is data visualisation specifically — load `data-visualization`.

## Prerequisites

- A modern browser target (last two major versions of Chrome/Firefox/Safari/Edge). The primitives use logical properties, `min()`/`max()`/`clamp()`, `aspect-ratio`, `gap`, `inset-*`. Pre-2021 browsers need progressive-enhancement fallbacks documented in `references/legacy-fallbacks.md`.
- A global stylesheet that establishes: `box-sizing: border-box` on `*`, `max-inline-size: 100%` on media, and a modular spacing scale on `:root`.

## Required inputs

- The element tree or component the layout describes (header, card, hero, dialog, list, etc.).
- The content that lives inside (variable text length? fixed image ratio? unknown number of items?).
- The container the layout sits inside (full-bleed? inside an article column? inside a sidebar?).
- Brand-system constraints if any (existing spacing scale, token names).

## Outputs

- One or more layout primitives selected and parameterised (custom-property values set from the spacing scale).
- The composition tree (which primitives nest inside which).
- The CSS (either authored directly or expressed as `class="stack"`, `class="cluster"` etc. against the canonical primitive stylesheet).
- For framework projects: component files (`<Stack>`, `<Cluster>`) wrapping the canonical CSS.

## Non-negotiables

1. **Algorithmic layout, not artisanal layout.** Describe the rules; let the browser compute the result. No pixel-prescribed positions, no breakpoint cascades for the same component.
2. **Container-aware, not viewport-aware.** A two-column layout that stacks on narrow containers is a Sidebar, not a `@media` query. The primitive must work the same inside a 320px modal and a 1920px page.
3. **`gap` over margin for sibling spacing.** Inside flex/grid contexts, use `gap`. The owl selector (`* + *` with `margin-block-start`) is reserved for the Stack primitive itself, where `margin: auto` must remain available for the splitter variant.
4. **Logical properties over physical.** `margin-inline`, `inline-size`, `inset-block-start` — never `margin-left`, `width`, `top` for content layout.
5. **One concern per primitive.** Stack only does vertical rhythm. Box only does padding/border. Don't bolt extra concerns onto a primitive — compose two.
6. **Custom properties on children, not parents.** `.stack > * + * { margin-block-start: var(--space, 1.5rem); }` so nested same-class instances override correctly.
7. **`box-sizing: border-box` is global.** Center is the one primitive that overrides to `content-box`; do not redeclare on Box, Stack, etc.

## Decision rules — picking the primitive

| You want… | Use | Key prop |
|---|---|---|
| Vertical rhythm between siblings | **Stack** | `--space` |
| Padded card / callout / panel | **Box** | `padding`, `invert` |
| Centre a column at measure | **Center** | `max` (default `60ch`) |
| Wrapping inline group (tags, chips, button row) | **Cluster** | `gap`, `justify`, `align` |
| Two-up that stacks when narrow | **Sidebar** | `sideWidth`, `contentMin` |
| N equal columns that all switch to vertical at threshold | **Switcher** | `--threshold`, `limit` |
| Full-viewport hero with vertically centred principal child | **Cover** | `centered`, `minHeight` |
| Auto-flowing card grid that reflows | **Grid** | `--minimum` |
| Crop media to a fixed aspect ratio | **Frame** | `--n` / `--d` |
| Horizontally scrolling row | **Reel** | `--item-width` |
| Overlay / dialog / tooltip | **Imposter** | `fixed`, `contain` |
| Inline icon scaling with text | **Icon** | `--space` |

### Sidebar vs Switcher vs Grid (the most-confused trio)

| Concern | Sidebar | Switcher | Grid |
|---|---|---|---|
| Number of children | 2 | 2–N | many |
| Children equal-width? | No (one fixed, one fluid) | Yes | Yes |
| Wrap behaviour | Both stack 100% when narrow | All children switch to vertical at threshold | Items reflow into more/fewer columns |
| Triggered by | Container width | Container width vs `--threshold` | `minmax(--minimum, 1fr)` math |
| Typical use | Media object, app shell | Pricing tiers, peer cards | Card gallery, dashboard tiles |

### When to break a primitive (almost never)

- If the layout you need is **single-purpose and used in one place**, write bespoke CSS — do not invent a 13th primitive for one use.
- If the layout you need recurs across the app, check whether it composes from existing primitives. If not, propose a new primitive with the same shape (one concern, one custom-property contract, no breakpoints).

## Workflow

1. **Identify the visible composition.** Read the design or describe the page tree: outermost container, sections, cards, item rows.
2. **Map each region to a primitive.** Use the decision table above. Most pages are: Cover (hero) → Stack (page body) → Center → Stack (article) → Grid (gallery) → Box × N (cards) → Stack (card body).
3. **Set custom properties from the modular scale.** `--space: var(--s1)` not `--space: 24px`. Token-driven from the start.
4. **Compose by nesting.** Boxes inside Grids inside Stacks. Don't write new CSS — re-arrange primitives.
5. **Test container responsiveness.** Resize the container (not the viewport) and confirm Sidebar/Switcher behave. Test inside a narrow parent like a sidebar nav.
6. **Confirm logical-property correctness.** Apply `dir="rtl"` and confirm the layout flips coherently. If it doesn't, you've used physical properties.

## Composition examples

**Marketing landing page**
```
Stack (page body, --space=var(--s2))
├── Cover (hero, centered=h1)
│   └── Center (intrinsic, max=40ch)
│       └── Stack (h1, p, button)
├── Center (article, max=60ch)
│   └── Stack (h2, p, p, blockquote, p)
├── Switcher (pricing, threshold=30rem)
│   └── Box × 3 (Stack inside each)
└── Sidebar (footer, sideWidth=15rem)
    └── img / Stack (link list)
```

**Dashboard card**
```
Box (padding=var(--s1), invert=false)
└── Stack (--space=var(--s0))
    ├── Cluster (header: title + Icon button)
    ├── Frame (16:9 chart container)
    └── Cluster (footer: tags)
```

**Modal dialog**
```
Imposter (fixed, contain, --margin=1rem)
└── Box (padding=var(--s1))
    └── Stack
        ├── h2
        ├── p
        └── Cluster (action buttons, justify=flex-end)
```

## Anti-patterns

- **Writing `@media (min-width: 768px)` to switch a 2-column layout to 1-column.** Use Sidebar or Switcher; viewport is not the right signal.
- **Adding `margin-top` to elements inside a Stack.** The Stack owns vertical margin via the owl selector; element-level margins fight it.
- **Setting `margin: 0 auto` on a Center inside a Stack.** Zeroes the Stack's `margin-block-start`. Use `margin-inline: auto`.
- **Hard-coding `width: 250px` on Grid items.** Defeats the auto-flow algorithm. Use `--minimum` on the Grid container.
- **Putting a Stack inside a Cluster expecting a row.** Cluster is for inline groupings; for stacked cards in a row use Switcher or Grid.
- **Two Cover sections with two `<h1>`.** One `<h1>` per page. Subsequent Covers use `centered="h2"`.
- **Padding on every side except one** (e.g. `padding: 1rem 1rem 0 1rem`). Asymmetric padding is a different primitive (probably a Sidebar). Don't deform the Box.
- **Re-implementing Grid as nested flexboxes** to "have more control". The control is illusory; you've reinvented Grid badly.

## Anti-pattern fixes (before/after)

```css
/* Before: viewport-driven 2-up */
.layout {
  display: flex;
  flex-direction: column;
}
@media (min-width: 768px) {
  .layout { flex-direction: row; }
  .layout > .aside { width: 20rem; }
  .layout > .main { flex: 1; }
}

/* After: container-aware Sidebar */
.with-sidebar { display: flex; flex-wrap: wrap; gap: 1rem; }
.with-sidebar > .sidebar { flex-basis: 20rem; flex-grow: 1; }
.with-sidebar > .not-sidebar { flex-basis: 0; flex-grow: 999; min-inline-size: 50%; }
```

```css
/* Before: each card child gets margin-top */
.card > * + * { margin-top: 1rem; }

/* After: Stack on the card body, with the modular scale */
.stack > * { margin-block: 0; }
.stack > * + * { margin-block-start: var(--space, var(--s1)); }
```

## Read next

- `practical-ui-design` — visual styling that lives inside layouts (typography, colour, spacing scale).
- `responsive-design` — viewport-driven media queries when they *are* needed (typography, font scale, breakpoints for major page architecture).
- `grid-systems` — when you need a strict grid-line architecture rather than auto-flow.
- `tailwind-css` — translates these primitives into utility classes (`flex flex-col gap-y-6` ≈ Stack).

## References

- `references/primitives.md` — the full canonical CSS for all 12 primitives, with custom properties, variants, gotchas, and per-primitive composition notes.
- `references/meta-principles.md` — axiomatic CSS, intrinsic web design, the role of `min()`/`max()`/`clamp()`, the modular scale, logical properties, owl selector philosophy.
- `references/composition-recipes.md` — recipes for common compositions (marketing pages, dashboards, modals, app shells) expressed as primitive trees.
- `references/legacy-fallbacks.md` — progressive-enhancement notes for older browser targets.
