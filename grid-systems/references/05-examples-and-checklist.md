# Worked Examples and Review Checklist

Real-world layouts step-by-step, plus the grid review gate.

## Example 1: Editorial Article (Manuscript + Side Notes)

**Target:** 1440 desktop, blog article.

- Baseline: 8pt. Body 18/28 (28 = 3.5 x 8 -> round to 32 = 4 x 8; use `line-height: 32px`).
- Type area: max-width 720px (60ch at 18/32 body), centred.
- Side notes: 240px column, offset 48px to the right of type area, visible >= 1280.
- Images: full-bleed within type area (720px wide); pull-quotes indent 2 columns if placed in side rail.
- Baseline visible in heading scale: H1 48/56, H2 32/40, H3 24/32, H4 20/32, body 18/32, small 14/24.

```css
.article { max-width: 720px; margin-inline: auto; padding-block: 96px; }
.article h1 { font-size: 48px; line-height: 56px; margin-block-end: 32px; }
.article h2 { font-size: 32px; line-height: 40px; margin-block: 48px 16px; }
.article p  { font-size: 18px; line-height: 32px; margin-block-end: 24px; }
@media (min-width: 1280px) {
  .article-with-notes {
    display: grid;
    grid-template-columns: 720px 48px 240px;
    justify-content: center;
  }
  .article-with-notes aside { grid-column: 3; }
}
```

## Example 2: SaaS Dashboard (12-col Modular)

**Target:** 1440 desktop. Dashboard with 4 KPI cards + 2 charts + 1 table.

- Baseline 8, gutter 24, margin 64, module height 96 (12 x 8).
- Columns: 12. Sidebar fixed 256px outside the grid.
- Row 1: 4 KPI cards, each `col-span-3`, `row: 1`.
- Row 2: 2 charts, `col-span-6` each, `row-span: 2` (192px tall).
- Row 3: 1 table, `col-span-12`, height auto.

```css
.dashboard { display: grid; grid-template-columns: 256px 1fr; }
.main {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  grid-auto-rows: 96px;
  gap: 24px;
  padding: 32px 64px;
}
.kpi  { grid-column: span 3; grid-row: span 1; }
.chart { grid-column: span 6; grid-row: span 2; }
.table { grid-column: span 12; }
```

Tablet (1024-): collapse to 8-col, KPIs `span 4` (2 per row), charts `span 8`, table still full.
Mobile (639-): collapse to 4-col, everything `span 4` stacked.

## Example 3: Product Landing Page (Hierarchical + 12-col)

**Target:** 1440 desktop, scrolling landing page.

- Hero: full bleed, 80vh tall, H1 72/80, subhead 24/32, CTA buttons in terminal area (bottom-right of hero).
- Section 1 — 3 feature cards: 12-col, each card `col-span-4`.
- Section 2 — big feature image + copy: `col-span-6` image + `col-span-6` copy.
- Section 3 — testimonials: 4-col subgrid with asymmetric weights (`col-span-5`, `col-span-7`).
- Section 4 — CTA banner: `col-span-12`.

```css
.hero { min-height: 80vh; display: grid; place-items: end start;
        padding: 96px clamp(16px, 5vw, 96px); }
.hero h1 { font-size: 72px; line-height: 80px; max-width: 16ch; }
.features { display: grid; grid-template-columns: repeat(12, 1fr);
            gap: 32px; padding: 96px clamp(16px, 5vw, 96px); }
.feature { grid-column: span 4; }
```

## Example 4: Mobile Feed (4-col Column)

**Target:** 375px iPhone, infinite feed.

- Margin 16, gutter 16. Column width = (375 - 32 - 48) / 4 = 73.75px.
- Feed items: each card `col-span-4` (full width). Secondary meta row: avatar 48 + text `col-span-3` with offset.
- Baseline 8; body 16/24; card padding 16; between cards 8.
- Safe area: top includes `env(safe-area-inset-top)`; bottom nav has its own safe area.

```css
.feed { display: flex; flex-direction: column; gap: 8px;
        padding: env(safe-area-inset-top) 16px 96px 16px; }
.card { padding: 16px; border-radius: 16px; background: var(--surface); }
.card-header { display: grid; grid-template-columns: 48px 1fr 24px;
               gap: 12px; align-items: center; }
```

## Example 5: Chart Composition (Grid as Data Frame)

**Target:** Time-series line chart inside a dashboard card.

- Card: `col-span-6`, module height 96, `row-span 4` = 384px tall.
- Chart padding 24 all sides -> draw area 696 * 336 (for 1440 parent with 12-col, span-6 = ~752px; subtract padding).
- Y-axis gridlines every 56px (7 gridlines -> 6 rows, each 56px = 7 x 8 baseline units). 56 is a clean multiple.
- X-axis ticks align to 8px grid too; auto-layout picks tick spacing that snaps to 8.
- Legend sits on baseline above chart; captions below on next baseline.

## Grid Review Checklist

Run before approving a design or merging layout code.

### Construction
- [ ] Baseline unit is documented (4pt or 8pt) and consistent.
- [ ] Spacing scale used throughout is an integer multiple of the baseline.
- [ ] Column count, gutter, margin are derived from formulae, not guessed.
- [ ] Max-width container is tied to target line length (45-75ch for prose).

### Type on Grid
- [ ] All `line-height` values are integer baseline multiples.
- [ ] No `line-height: 1.3` decimal heading values.
- [ ] Body line length 45-75ch.
- [ ] First line of text blocks sits on a baseline.

### Images and Media
- [ ] Image widths are integer column spans.
- [ ] Image heights snap to baseline multiples.
- [ ] Aspect ratios are rational (1:1, 4:3, 3:2, 16:9).
- [ ] Captions sit on next baseline below the image.

### Hierarchy and Composition
- [ ] One dominant focal point per screen.
- [ ] Spans sum to the column count (no leftover slivers).
- [ ] Asymmetry, where used, is intentional and re-anchored to the 12-col.
- [ ] Whitespace is planned, not accidental.

### Responsive
- [ ] 12-col collapses cleanly to 8-col then 4-col; no squashed cards.
- [ ] Gutter shrinks at smaller breakpoints but stays integer.
- [ ] Margin equal to or greater than gutter at every breakpoint.
- [ ] Container queries used for nested components, not viewport queries.
- [ ] Safe areas respected on mobile.

### Validation
- [ ] Baseline overlay toggled on — everything aligns.
- [ ] Squint test: visible hierarchy without content detail.
- [ ] Browser resize from 360 to 1920 — layout reflows without overlap or broken spans.
- [ ] Checked at `prefers-reduced-motion` and at 200% zoom (type on grid should still hold).

### Anti-Pattern Scan
- [ ] No `17px`, `22px`, `28px` or other off-baseline values in padding/gap tokens.
- [ ] No fractional `col-span-*` classes.
- [ ] No mixing of 2 base units (`gap: 4` on one component, `gap: 8` on another without reason).
- [ ] No desktop 12-col shoved onto phone.
- [ ] No nested grid with different base unit.

## Launch Gate

A layout is grid-ready when:

1. The three-line spec exists in the design tokens file: `baseline`, `columns per breakpoint`, `spacing scale`.
2. The baseline overlay passes in the dev build.
3. The designer and the engineer can both describe the grid in one sentence.
4. A second reviewer can detect the grid in under 15 seconds from the rendered page.

If any of these fail, the grid is not real yet. Fix it before shipping.
