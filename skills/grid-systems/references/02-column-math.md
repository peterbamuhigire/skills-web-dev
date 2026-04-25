# Column Math

Formulae and worked examples for deriving column width, gutter, margin, and field sizing.

## Core Formulae

Given a container width `W`, column count `n`, gutter `g`, side margin `m`:

```text
usable       = W - 2 * m
columnWidth  = (usable - (n - 1) * g) / n
spanWidth(k) = k * columnWidth + (k - 1) * g
```

Inverse (given a desired `columnWidth`, find container):

```text
W = n * columnWidth + (n - 1) * g + 2 * m
```

## Gutter and Margin Rules of Thumb

- Gutter `g` is an integer multiple of the baseline unit (4 or 8): common values 8, 12, 16, 20, 24, 32.
- Side margin `m >= 2 * g` on desktop; `m = g` acceptable on phones.
- For dashboards with dense content, `m` can be `g` even on desktop to maximise usable area.
- Gutter is fixed across all cells; it is not content-dependent.

## Worked Desktop Examples (12-col, 8pt baseline)

| Container (W) | Margin (m) | Gutter (g) | Usable | Column Width | 4-col Span | 8-col Span |
|---:|---:|---:|---:|---:|---:|---:|
| 1920 | 128 | 32 | 1664 | 109.3 | 533.3 | 1173.3 |
| 1440 | 96  | 32 | 1248 | 74.67 | 394.67 | 821.33 |
| 1280 | 64  | 24 | 1152 | 74    | 368    | 784 |
| 1024 | 48  | 24 | 928  | 55.33 | 293.33 | 625.33 |

Columns don't need to be integer pixels — CSS `1fr` handles fractional widths; we care about span sums being predictable.

## Tablet (8-col)

| Container (W) | Margin (m) | Gutter (g) | Usable | Column Width | 2-col | 4-col | 6-col |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1024 | 48 | 24 | 928 | 95 | 214 | 404 | 594 |
| 768  | 32 | 16 | 704 | 74 | 164 | 312 | 460 |

## Mobile (4-col)

| Container (W) | Margin (m) | Gutter (g) | Usable | Column Width | 2-col | 3-col |
|---:|---:|---:|---:|---:|---:|---:|
| 428 | 16 | 16 | 396 | 85.5  | 187 | 288.5 |
| 390 | 16 | 16 | 358 | 76.5  | 169 | 261.5 |
| 375 | 16 | 16 | 343 | 73.75 | 163.5 | 253.25 |
| 360 | 16 | 16 | 328 | 70    | 156 | 242 |
| 320 | 12 | 12 | 296 | 65    | 142 | 219 |

## Fluid vs Fixed

- **Fluid columns (`1fr`):** Column width flexes with container. Use for responsive grids.
- **Fixed gutter:** Always a fixed pixel value, not a percent. Keeps rhythm consistent across breakpoints.
- **Fluid margin (`clamp`):** `padding-inline: clamp(16px, 5vw, 96px);` collapses gracefully across breakpoints without media queries.
- **Max-width container:** Set `max-width` equal to the target type area for your desired line length.

```css
.container {
  max-width: 1440px;
  padding-inline: clamp(16px, 5vw, 96px);
  margin-inline: auto;
}
.grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: clamp(16px, 2vw, 32px);
}
```

## Asymmetrical and Bespoke Layouts

- Desktop hero: 12-col substrate with a 7+5 or 8+4 split gives editorial tension.
- Two-pane app: sidebar is a fixed pixel width outside the grid (240-320px), main area uses a 12-col grid.
- Tri-pane app (mail, IDE): two fixed sidebars + flexible main. Main uses 12-col or flow layout.

```css
.app-shell {
  display: grid;
  grid-template-columns: 256px 1fr 320px;
}
.app-main .content {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 24px;
}
```

## Sub-Division Trick (Refined Modular)

A 12-col grid can double as a 24-col grid by halving each column:

```css
.refined {
  display: grid;
  grid-template-columns: repeat(24, 1fr);
  gap: 16px;
}
.card-wide { grid-column: span 16; }  /* = 8 of 12 */
.card-kpi  { grid-column: span 6; }   /* = 3 of 12 */
.chart-half { grid-column: span 11; } /* off-grid for asymmetry */
```

Useful for dashboards where some panels want the extra fidelity; keep the visual reference as 12-col.

## Container Queries for Component Grids

When a component may live in either a full-width or narrow context, let the component itself choose columns:

```css
.card-grid {
  container-type: inline-size;
}
.card-grid .cards {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 16px;
}
@container (min-width: 480px) { .card-grid .cards { grid-template-columns: repeat(2, 1fr); } }
@container (min-width: 768px) { .card-grid .cards { grid-template-columns: repeat(3, 1fr); } }
```

## Field Sizing (Content Units)

Fields are groups of modules holding one unit of content. Aspect ratios:

| Field | Columns | Module rows (8pt base) | Aspect | Use |
|---|---:|---:|---|---|
| KPI card | 3 | 2 | 3:1 | Dashboard KPIs |
| Hero card | 8 | 6 | 4:3 | Featured content |
| Square tile | 3 | 3 | 1:1 | Avatar grid, product thumbnails |
| Article card | 4 | 5 | 4:5 | Blog index |
| Chart panel | 6 | 4 | 3:2 | Time-series chart |

Size is always `columns * columnWidth + (columns - 1) * gutter` wide, and `rows * moduleHeight + (rows - 1) * rowGap` tall.

## Validation

- All span sums must equal the column count (`8 + 4 = 12`, `3 + 3 + 3 + 3 = 12`).
- No span can be a fraction (`span 3.5` is a red flag).
- Gutter appears at equal size between all adjacent fields.
- Margin appears at equal size on both sides of the container (or deliberately asymmetric with a design rationale).
