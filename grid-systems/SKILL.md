---
name: grid-systems
description: Use when laying out any screen, page, dashboard, or editorial surface
  that needs disciplined alignment, rhythm, and proportion. Covers Swiss-style grid
  construction (manuscript, column, modular, baseline, hierarchical), column math,
  baseline grids, type-on-grid alignment, image-field alignment, and mapping these
  to 4/8/12-col responsive web and mobile grids. Load alongside practical-ui-design
  and responsive-design whenever layout discipline matters.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Grid Systems

<!-- dual-compat-start -->
## Use When

- You are designing or reviewing a layout, page template, dashboard, editorial article, product landing page, mobile feed, or dense data screen, and spatial order has to hold across breakpoints.
- You need to decide column count, gutter, margin, baseline rhythm, or image proportions from first principles rather than by eye.
- You are pairing this with `practical-ui-design`, `responsive-design`, `webapp-gui-design`, `swiftui-design`, `jetpack-compose-ui`, or `healthcare-ui-design` and want their visual tokens to sit on a real grid.

## Do Not Use When

- The surface is a tiny fragment (a single modal, toast, or icon) where grid math adds no value.
- The task is purely content writing, a backend change, or a text-only CLI — no spatial design decisions are being made.
- A platform skill (`jetpack-compose-ui`, `swiftui-design`, `webapp-gui-design`) already encodes a fixed grid and the task is only to use it; load this skill only when the grid itself is being chosen or stress-tested.

## Required Inputs

- Target surface: viewport widths (min/max), content classes (text, image, data table, card, chart), density intent (editorial / application / dashboard / mobile feed).
- Known constraints: brand margins, existing design-token scale, baseline line-height of body type, any mandated framework grid (Bootstrap 12, Tailwind, Material, iOS 8-col).
- The deliverable: a grid spec, a layout review, a responsive mapping, or corrected layout code.

## Workflow

1. Classify the surface (editorial / application / dashboard / mobile) — this picks the grid type.
2. Define the **baseline unit** from the body line-height (usually 4pt or 8pt).
3. Derive the **spacing scale** as integer multiples of the baseline (4, 8, 12, 16, 24, 32, 48, 64, 96).
4. Choose **column count** per breakpoint using the rules in `references/01-grid-types.md`.
5. Compute **column width, gutter, margin** using the formulae in `references/02-column-math.md`.
6. Set **baseline grid** (vertical rhythm) and align all type, images, and elements to it per `references/03-baseline-grid.md`.
7. Map the base grid to each responsive breakpoint per `references/04-responsive-mapping.md`.
8. Validate with the checklist in `references/07-checklist.md` (squint test, module fidelity, baseline alignment, no orphans).

## Quality Standards

- Every column width, gutter, and margin must be expressible as a formula or integer token; no "eyeballed" values.
- Baseline rhythm must hold across headings, body, cards, and image captions — changing font size must preserve vertical rhythm via multiples of the baseline unit.
- The same page must not mix more than one grid system; refined/modular grids are sub-divisions of a single base grid, not rivals to it.
- On responsive breakpoints, grids must simplify (fewer columns), never multiply; never stretch a desktop 12-col blindly onto a 375px phone.
- Images, charts, and media must align to integer module counts (1x1, 2x1, 3x2, 4x3) — no arbitrary aspect ratios inside a grid.

## Anti-Patterns

- Using multiple inconsistent gutter widths on the same page (e.g. 16 here, 20 there, 24 elsewhere).
- Setting arbitrary heading `line-height` values that break baseline rhythm; headings must sit on N baseline units.
- Stretching text across full viewport width so line length exceeds 75 characters.
- Mapping a desktop 12-col grid 1:1 onto a tablet or phone without collapsing columns.
- Placing images or charts on fractional module widths (image spans 3.5 columns).
- Treating the grid as a wireframe-only tool and letting production code break it.
- Forcing card rows of unequal heights without a baseline snap.
- Nesting a second grid inside a cell with a different base unit.
- Using `margin: auto` for layout without a container max-width tied to line-length.
- Relying on whitespace alone for hierarchy while abandoning the grid; whitespace is part of the grid, not an escape from it.

## Outputs

- A grid spec (column count, column width formula, gutter, margin, baseline unit, spacing tokens) per breakpoint.
- Worked CSS/Tailwind/SwiftUI/Compose code snippets showing the grid applied.
- A short rationale for column count and baseline unit, tied to content class and body line-height.
- Optional: layout audit notes with fixes for misalignment, baseline drift, or broken responsive mapping.

## References

- `references/01-grid-types.md` — manuscript, column, modular, baseline, hierarchical grids; when each applies; detection.
- `references/02-column-math.md` — formulae for column width, gutter, margin; worked desktop/tablet/mobile examples; fluid grids and container queries.
- `references/03-baseline-and-type.md` — vertical rhythm, type-on-grid alignment, spacing-scale derivation, cap-height compensation.
- `references/04-responsive-and-hierarchy.md` — 12/8/4-col responsive ladder, collapse rules, container queries, hierarchy through span and whitespace, focal points.
- `references/05-examples-and-checklist.md` — worked examples (editorial, dashboard, landing, mobile feed, chart) and the grid review checklist + launch gate.
<!-- dual-compat-end -->

## Core Concept (One-Screen Summary)

A grid is a repeating system of reference lines that keeps type, image, and space in predictable proportion. In Swiss typography (Müller-Brockmann) the grid is built from:

```text
page format  ->  type area  ->  margins  ->  columns  ->  modules  ->  gutters  ->  baseline  ->  fields
```

- **Page format** — the outer bounds (viewport, safe area).
- **Type area** — the active rectangle after margins.
- **Margins** — space between page edge and type area; bigger on outer edge for bindings in print, symmetrical in digital.
- **Columns** — vertical divisions of the type area.
- **Gutters** — fixed gaps between columns.
- **Modules** — rectangular cells formed where columns cross horizontal divisions.
- **Baseline grid** — horizontal lines spaced at body `line-height` that carry vertical rhythm.
- **Fields** — groups of modules that hold one unit of content (image, headline, paragraph, card).

Digital adapts this: `margin`, `gap`, and `grid-template-columns` map directly to margin, gutter, and columns. Baseline rhythm maps to `line-height` and `padding` multiples.

## Grid Type Decision Table

Pick the grid type before touching CSS. Load `references/01-grid-types.md` for trade-offs.

| Surface | Grid Type | Typical Columns | Body Line Length |
|---|---|---|---|
| Long-form article, essay, documentation | Manuscript + optional 2-col | 1 (text) + 1 (notes) | 60-75ch |
| Magazine, editorial, marketing site | Column (2-6) | 2, 3, 4, 5, 6 | 45-75ch |
| SaaS app, dashboard, admin panel | Modular refined 12-col | 12 (24 sub) | 40-60ch in panels |
| Data-dense analytics, charts, tables | Modular 12 or 24-col | 12 or 24 | n/a |
| Product landing hero + sections | Hierarchical (hero) + 12-col below | 12 | 50-70ch |
| Mobile feed, card list, POS screen | 4-col | 4 | 30-50ch |
| Tablet app | 8-col | 8 | 40-60ch |

## Baseline Unit Rules

- Pick **one** baseline unit for the whole product: usually **4pt** (dense apps) or **8pt** (typical web and mobile).
- Body text drives it: `baseline = body line-height`. Example: body 16px, line-height 1.5 = 24px -> baseline 8pt (24 is a clean multiple of 8).
- Spacing scale uses integer multiples only: 4, 8, 12, 16, 24, 32, 48, 64, 96 (8pt scale) or 4, 8, 12, 16, 20, 24, 32 (4pt refined).
- Headings must snap to integer baseline multiples: e.g. H1 48px with line-height 56px = 7 x 8pt; H2 32px with line-height 40px = 5 x 8pt.
- Section padding, card padding, and gap values must all be integer multiples of the baseline. No "17px" or "20px" values when base is 8.

## Column Math (Quick)

For a container width `W`, column count `n`, gutter `g`, side margin `m`:

```text
usable = W - 2 * m
columnWidth = (usable - (n - 1) * g) / n
```

Worked common values (desktop-first, 8pt scale):

| Container | Columns | Gutter | Margin | Column Width |
|---|---|---|---|---|
| 1440 | 12 | 32 | 96 | 88 |
| 1280 | 12 | 24 | 64 | 80.67 |
| 1024 | 8 | 24 | 48 | 99 |
| 768 | 8 | 16 | 32 | 72 |
| 390 (iPhone) | 4 | 16 | 16 | 79.5 |
| 360 (Android) | 4 | 16 | 16 | 72 |

Full derivations, non-square containers, and asymmetrical layouts: `references/02-column-math.md`.

## Minimum Web Implementation (12-col, 8pt baseline)

```css
:root {
  --baseline: 8px;
  --grid-cols: 12;
  --grid-gap: calc(var(--baseline) * 4);   /* 32 */
  --grid-margin: calc(var(--baseline) * 12); /* 96 on wide desktop */
  --container-max: 1440px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(var(--grid-cols), 1fr);
  gap: var(--grid-gap);
  max-width: var(--container-max);
  padding-inline: var(--grid-margin);
  margin-inline: auto;
}

@media (max-width: 1024px) {
  :root { --grid-cols: 8; --grid-gap: 24px; --grid-margin: 48px; }
}
@media (max-width: 640px) {
  :root { --grid-cols: 4; --grid-gap: 16px; --grid-margin: 16px; }
}
```

Tailwind analogue:

```html
<div class="mx-auto max-w-[1440px] px-24 grid grid-cols-12 gap-8
            lg:px-12 lg:gap-6 md:grid-cols-8 md:px-8 md:gap-4 sm:grid-cols-4">
  <article class="col-span-8">...</article>
  <aside   class="col-span-4">...</aside>
</div>
```

SwiftUI analogue (4-col mobile, 8-col tablet):

```swift
let columns: [GridItem] = Array(
  repeating: GridItem(.flexible(), spacing: 16),
  count: horizontalSizeClass == .regular ? 8 : 4
)
LazyVGrid(columns: columns, spacing: 16) { /* cells */ }
  .padding(.horizontal, 16)
```

Jetpack Compose:

```kotlin
LazyVerticalGrid(
  columns = GridCells.Fixed(if (isTablet) 8 else 4),
  horizontalArrangement = Arrangement.spacedBy(16.dp),
  verticalArrangement = Arrangement.spacedBy(16.dp),
  contentPadding = PaddingValues(16.dp),
) { /* items */ }
```

## Type-on-Grid Alignment (Quick Rules)

- Body `line-height` = baseline unit (or 2x baseline); do not invent fractional values.
- Heading `line-height` in integer baseline multiples. Round up, never down.
- First-line of a text block should sit on a baseline line (`padding-top` absorbs the difference between cap-height and x-height if needed).
- When type scale steps are narrow, use the **half-baseline** trick: 8pt baseline with 4pt refinements for captions or dense tables.
- Image captions sit on the next baseline below the image, not a visually guessed gap.

Details, cap-height compensation, and fluid scaling: `references/03-baseline-grid.md`.

## Image and Media Alignment

- Image aspect ratios must match integer module counts: 1:1, 3:2, 4:3, 16:9 aligned to whole columns.
- A card image spanning 4 modules at 80px module + 24px gutter is `4*80 + 3*24 = 392px` wide; pick image aspect (e.g. 16:9 -> 220.5px ~ 220px height, re-snap to baseline).
- Charts: x-axis tick spacing and y-axis gridlines align to the page grid or a sub-grid that is an integer division of it.
- Icons: sized in baseline units (16, 24, 32) and vertically centred on the body baseline using flex/inline-flex.

## Hierarchy Through Grid

Size and span, not decoration, create editorial hierarchy:

- Hero: spans full 12 (or 10 with offset) with a taller row height.
- Primary content: spans 8 of 12; secondary spans 4.
- Equal peers: 4 + 4 + 4 or 3 + 3 + 3 + 3.
- Asymmetry: 5 + 7 or 7 + 5 creates tension; reserve for landing pages, not product UI.
- Rule of thirds: a 12-col grid quarters cleanly; vertical focal points at columns 4 and 8 feel balanced.

Deeper patterns: `references/05-hierarchy-through-grid.md`.

## Responsive Mapping (Default Ladder)

| Breakpoint | Columns | Gutter | Margin | Notes |
|---|---|---|---|---|
| >= 1440 | 12 | 32 | 96 | Full editorial / app canvas |
| 1024-1439 | 12 | 24 | 64 | Compact desktop |
| 768-1023 | 8 | 24 | 48 | Tablet landscape; collapse 3-col into 2-col |
| 640-767 | 8 | 16 | 32 | Tablet portrait |
| 375-639 | 4 | 16 | 16 | Phone; single-column stacks are common |
| < 375 | 4 | 12 | 12 | Small phones (iPhone SE) |

Content-query patterns (container queries) for component-level grids: `references/04-responsive-mapping.md`.

## Non-Negotiables

1. One baseline unit per product.
2. Spacing scale = integer multiples of the baseline only.
3. Column count, gutter, and margin are derived, not drawn.
4. Every heading `line-height` is an integer baseline multiple.
5. Text line length 45-75ch for body copy; 20-45ch for ultra-short columns.
6. Images and media fill integer module counts.
7. Grids simplify at smaller breakpoints; they do not scale linearly.
8. Maximum one grid system per page; refinements are sub-divisions of it.
9. Max-width container is set by desired line length, not by guesswork.
10. Validate with the squint test and a visible baseline overlay during review.

## Companion Skills

| Skill | When to Load |
|---|---|
| `practical-ui-design` | Visual tokens — colour, typography, spacing — that ride on this grid. |
| `responsive-design` | Breakpoint philosophy, container queries, pointer/hover detection. |
| `webapp-gui-design` | Tabler/Bootstrap web apps needing 12-col grid enforcement. |
| `swiftui-design` / `ios-development` | iOS layouts using `LazyVGrid` and `GridItem`. |
| `jetpack-compose-ui` / `android-development` | Android layouts using `LazyVerticalGrid`. |
| `healthcare-ui-design` | High-density clinical screens built on refined 24-col modular grids. |
| `design-audit` | Runs grid adherence as part of the UI quality audit. |
| `data-visualization` | Chart composition on a shared grid for dashboards. |
| `mobile-reports` / `mobile-report-tables` | Table and report rhythm on 4-col phones. |

## Source

Josef Müller-Brockmann, *Grid Systems in Graphic Design* (1981). Adapted for digital screens with guidance from Swiss modernist typography, Bringhurst's *Elements of Typographic Style*, Material Design, Apple Human Interface Guidelines, and the 8pt/4pt community spacing conventions.
