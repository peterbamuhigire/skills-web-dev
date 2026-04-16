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

- Use when laying out any screen, page, dashboard, or editorial surface that needs disciplined alignment, rhythm, and proportion. Covers Swiss-style grid construction (manuscript, column, modular, baseline, hierarchical), column math, baseline grids, type-on-grid alignment, image-field alignment, and mapping these to 4/8/12-col responsive web and mobile grids. Load alongside practical-ui-design and responsive-design whenever layout discipline matters.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `grid-systems` or would be better handled by a more specific companion skill.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| UX quality | Grid layout audit | Markdown doc covering column math, baseline rhythm, and responsive mapping per Müller-Brockmann adaptation | `docs/ux/grid-audit-checkout.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
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
