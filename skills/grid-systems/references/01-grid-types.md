# Grid Types

Five canonical grid types, when to use each, and digital translation.

## Manuscript Grid (Single-Block)

- **Structure:** One large text block filling the type area. Margins hold breathing space.
- **Use when:** Long-form prose — essays, articles, documentation, book pages.
- **Digital tokens:** `max-width: 65ch`, generous `margin-inline: auto`, large top/bottom padding.
- **Pitfalls:** Boring if applied without care; use type scale and pull-quotes for rhythm.
- **Variation:** Add a marginal notes column (footnotes, sidebars, table of contents) to form a near-2-col without breaking the single-block feel.

## Column Grid

- **Structure:** Vertical columns separated by fixed gutters. Content fields span 1..N columns.
- **Use when:** Editorial pages, marketing sites, blog indexes, magazine layouts.
- **Column counts by purpose:**
  - 2-col: features, image + caption articles.
  - 3-col: card grids, news index, product catalogue.
  - 4-col: denser product grids, portfolios.
  - 5 or 6-col: complex editorial with pull-quotes, images, and sidebars.
- **Span pattern:** Mix spans to create rhythm (8+4, 6+6, 4+4+4, 3+6+3).
- **Digital token:** `display: grid; grid-template-columns: repeat(N, 1fr); gap: <gutter>;`.

## Modular Grid (Rows + Columns)

- **Structure:** Columns intersected by horizontal divisions to form a matrix of modules. Content occupies integer counts of modules in both axes.
- **Use when:** Dashboards, admin panels, data-dense apps, photo galleries, asymmetrical magazine layouts.
- **Digital:** CSS Grid with `grid-template-rows` and `grid-template-columns` and spans. Allows rich density without chaos.
- **Refinement trick:** Start with a 12-col column grid, then subdivide each column into half-rows on the baseline — gives a 12 x many modular grid without extra tokens.

```css
.dashboard {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-auto-rows: 64px;   /* module height = 8 baseline units */
  gap: 16px 32px;
}
.card--wide { grid-column: span 8; grid-row: span 2; }
.card--kpi  { grid-column: span 3; grid-row: span 1; }
```

- **Pitfalls:** Over-gridding — every component forced into perfect modules feels robotic. Break modular rules deliberately for focal content.

## Baseline Grid

- **Structure:** Horizontal lines spaced at a fixed baseline unit (the body `line-height`). Every line of type, every image edge, and every card padding aligns to this rhythm.
- **Use when:** Always, underlying any other grid.
- **Key rule:** Type `line-height` and spacing tokens are integer multiples of the baseline. No exceptions for components.
- **See:** `03-baseline-grid.md` for the full vertical-rhythm system.

## Hierarchical Grid

- **Structure:** Non-uniform grid derived from content importance. Regions sized to their content class, often with asymmetry.
- **Use when:** Landing page heroes, portfolio showcases, editorial covers, one-off marketing pages where content density varies sharply.
- **Construction:** Start from a 12-col substrate to keep alignment honest, but vary row heights, span ratios (5+7, 8+4), and introduce generous whitespace regions deliberately.
- **Pitfalls:** Freeform hierarchy can look like no grid at all; always prove the 12-col spine exists even when content breaks it.

## Compound Grids

- Two grids overlaid — e.g. a 4-col + 3-col = 12-col grid where either parent snaps. Rarely needed; reserve for editorial covers and large marketing pages.
- Requires a clear rule for which parent to obey in each region.

## When to Use Which

| Surface | First choice | Second choice |
|---|---|---|
| Documentation site | Manuscript + side nav | 2-col column |
| Blog / article list | 3-col column | 2-col column |
| Magazine homepage | 6-col column | Hierarchical |
| SaaS dashboard | 12-col modular | 24-col modular (data density) |
| Admin CRUD table screen | Manuscript (table fills) + sidebar | 12-col column |
| E-commerce product grid | 4-col column | 3-col column (tablet) |
| Product landing page | Hierarchical (hero) + 12-col | Compound |
| Chart composition | Modular (fixed square modules) | Column |
| Mobile app feed | 4-col column | Manuscript (single column) |
| POS / data entry | 12-col modular for desktop, 4-col mobile | 8-col modular for tablet |

## Trade-offs Summary

| Type | Strength | Weakness |
|---|---|---|
| Manuscript | Simplest, best for reading | Weak hierarchy, limited layout options |
| Column | Flexible spans, rhythm through repetition | Rigid horizontally; rows drift |
| Modular | Handles 2D density, great for dashboards | Can feel mechanical if overused |
| Baseline | Universal vertical rhythm | Fragile under variable fonts / user zoom — test |
| Hierarchical | Strong visual identity, bespoke feel | Hard to reuse; maintenance-heavy |

## Detection: What Grid Is a Page Using?

1. Measure: find the narrowest consistent content column width; note side margins and content widths.
2. Count: divide the type area by candidate column counts (4, 6, 8, 12) and see which divides evenly with plausible gutters.
3. Look for modules: scan vertically for repeating horizontal divisions aligned across columns.
4. Baseline: check that heading and body `line-height` values snap to a common divisor.
5. If none of the above yields clean math, the page lacks a real grid — start from scratch rather than patching.
