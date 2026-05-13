# Responsive Mapping & Hierarchy

How a grid reshapes across breakpoints, and how span + rhythm drive hierarchy.

## Default Responsive Ladder

| Breakpoint | Columns | Gutter | Margin | Container |
|---:|---:|---:|---:|---|
| >= 1440 | 12 | 32 | 96 | `max-width: 1440px` |
| 1024-1439 | 12 | 24 | 64 | 100% |
| 768-1023 | 8 | 24 | 48 | 100% |
| 640-767 | 8 | 16 | 32 | 100% |
| 375-639 | 4 | 16 | 16 | 100% |
| < 375 | 4 | 12 | 12 | 100% |

Rules:

- Columns *reduce* as viewport shrinks (12 -> 8 -> 4). Never stretch a 12-col to a phone.
- Gutter shrinks with viewport but remains an integer of the baseline.
- Margin shrinks faster than gutter; phones get `margin = gutter`.
- A content region that spanned `col-span-4` at 12-col usually spans `col-span-4` at 8-col (half the width) then `col-span-4` = full at 4-col.

## Collapse Rules (12-col -> 8-col -> 4-col)

| Desktop span (of 12) | Tablet span (of 8) | Mobile span (of 4) |
|---:|---:|---:|
| 12 | 8 | 4 |
| 8 | 6 | 4 |
| 6 | 4 | 4 (stack) |
| 4 | 4 | 4 (stack) |
| 3 | 4 | 4 (stack) |
| 2 | 2 | 2 |

When collapsing reduces the count of items per row, stack them vertically rather than shrinking each item below its minimum legible width.

## Container Queries (Component-Level)

Page-level breakpoints are blunt. When a component may appear in a 400px sidebar or a 1200px main, use container queries:

```css
.feature-card {
  container-type: inline-size;
  container-name: card;
}
@container card (min-width: 640px) {
  .feature-card .media { width: 40%; }
  .feature-card .body  { width: 60%; }
}
@container card (max-width: 640px) {
  .feature-card { flex-direction: column; }
  .feature-card .media { width: 100%; }
}
```

Rule of thumb: pages use viewport breakpoints, components use container queries.

## Fluid Grids Without Media Queries

Auto-fit + minmax handles many card lists elegantly:

```css
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}
```

- `auto-fit` collapses empty tracks to keep the grid tight.
- `auto-fill` preserves empty tracks (for alignment with a fixed-width sibling).
- `minmax(min, 1fr)` ensures minimum card width and fluid up.

Use for card grids, logo walls, portfolio tiles. Do not use for editorial layouts with meaningful spans.

## Safe Areas and Notches

- iOS and Android phones reserve safe areas at top and bottom. Respect `env(safe-area-inset-top)` and `env(safe-area-inset-bottom)`.
- Ensure tappable elements sit inside the safe area.
- Side safe areas on landscape phones (notch + gesture bar) — use `env(safe-area-inset-left)` and `-right`.

```css
.app-shell {
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
  padding-inline: max(16px, env(safe-area-inset-left));
}
```

## Hierarchy Through Grid

Grid is the backbone of editorial hierarchy; size and span do the work, not decoration.

### Span Hierarchy

- Hero: `col-span-12` with tall row height.
- Primary: `col-span-8`, secondary: `col-span-4`.
- Equal peers: `col-span-4 x 3`, `col-span-3 x 4`, `col-span-6 x 2`.
- Tension: `col-span-5 + col-span-7` or `col-span-7 + col-span-5` feels editorial; reserve for landing pages.

### Row Hierarchy

- Hero row: 2-3x standard row height.
- Body rows: standard height.
- Inter-row gap: larger between sections, standard within a section.

### Asymmetry

- Break grid symmetry deliberately: a hero image bleeds past the type area; a quote indents 2 columns.
- Always re-anchor: asymmetry without a regular grid to measure it against looks sloppy.

### Whitespace as a Grid Element

- Reserve a whole column or row as deliberate whitespace.
- Treat whitespace as a piece of content; plan its width and height the same as any card.
- Do not fill every gap — emptiness is part of the composition.

### Rule of Thirds (Digital Adaptation)

- On a 12-col grid: focal points at columns 4 and 8 (start of the middle and start of the rightmost third) feel balanced.
- Vertically: place key elements one-third from top or one-third from bottom of a hero region.
- Useful for hero composition, not for flat app screens.

### Diagonal Balance (Gutenberg)

- Primary optical area: top-left.
- Terminal area: bottom-right. Place the CTA here on landing pages.
- Weak areas: top-right and bottom-left; safe for tertiary content or whitespace.

### Focal Point Rules

- One dominant focal point per screen; anything competing reduces its power.
- Size, contrast, whitespace around, and column span all make an element focal; combine two of the four.
- Faces and arrows draw attention; use their direction to pull the eye toward the CTA, not away.

## Density Modes

Some apps need density switching (comfortable / default / compact). Derive each mode as a baseline multiplier:

- Comfortable: baseline 8, padding doubled, heights 56.
- Default: baseline 8, standard values.
- Compact: baseline 4, halved padding, heights 40.

Never invent a density mode with irregular pixel values; it must follow the same base.
