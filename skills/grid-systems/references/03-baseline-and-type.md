# Baseline Grid & Type Alignment

Vertical rhythm, spacing scale, and type-on-grid rules.

## Pick One Baseline Unit

- **8pt** for typical web and mobile (default).
- **4pt** for dense apps, data-heavy dashboards, or where half-step refinement is needed.
- Document the choice once in the design-tokens file; never mix bases within one product.

## Derive the Baseline From Body Line-Height

- Body text: 16px base, `line-height` 1.5 = 24px. Baseline = 8pt (24 is 3 x 8).
- Body text: 17px base (iOS default), `line-height` 1.47 = 25px -> round to 24 = 8pt baseline.
- Body text: 14px dense apps, `line-height` 1.43 = 20px -> 4pt baseline (20 is 5 x 4).

## Spacing Scale (Integer Multiples)

8pt scale: `0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 128`.
4pt refined: `0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 48, 56, 64`.

Guidelines:
- 4 — tight intra-component (icon-to-label, chip padding).
- 8 — innermost padding.
- 16 — default gap between related elements.
- 24 — card padding, between related form fields.
- 32 — section gap.
- 48 — between major page sections.
- 64+ — hero and large editorial breaks.

## Heading Line-Heights (Integer Multiples of Baseline)

On an 8pt baseline:

| Heading | Font-size | Line-height | Baseline units |
|---|---|---|---|
| H1 | 48px | 56px | 7 |
| H2 | 36px | 48px | 6 |
| H3 | 28px | 40px | 5 |
| H4 | 22px | 32px | 4 |
| Body | 16px | 24px | 3 |
| Small | 14px | 20px | 2.5 (4pt refinement) |
| Caption | 12px | 16px | 2 |

Never write `line-height: 1.3` for a heading — compute the pixel line-height as an integer multiple of the baseline, then express it as a unitless ratio if you must.

## Cap-Height Compensation

Fonts ship with default leading that makes text sit visually below the baseline. If this bothers the layout:

- Use `text-box-trim` / `text-box-edge` (CSS) where supported to trim leading to the cap-height.
- Fallback: set `line-height` slightly smaller than one baseline and absorb the difference with `padding-top`.

For production, pin `line-height` to the baseline and accept the small visual offset; it's consistent enough that users do not notice.

## Fluid Type Scaling

When type scales with viewport (`clamp`), baseline must scale with it. Two approaches:

**Fixed baseline, fluid type:** keep baseline 8px, let body shrink gracefully.

```css
body { font-size: clamp(14px, 1vw + 8px, 18px); line-height: 24px; }
```

**Scaling baseline:** rare, for responsive editorial. Define baseline in `em` relative to body.

```css
:root { --baseline: 0.375rem; /* 6px at 16, 7.5px at 20 */ }
```

Prefer fixed baseline; fluid baselines break modular consistency.

## Image and Card Alignment

- Image heights snap to baseline multiples: 24, 48, 72, 96, 120, 144, 192, 240, 288.
- Caption sits on the next baseline below the image.
- Card padding: top and bottom are equal baseline multiples (usually 16 or 24).
- Card heights: snap to baseline multiples; if content varies, set `min-height` to an integer multiple.

```css
.card { padding: 24px; min-height: 192px; }
.card img { height: 120px; }
.card figcaption { margin-block-start: 8px; line-height: 24px; }
```

## Form Field Rhythm

- Input height: 40 or 48px (5 or 6 baseline units at 8pt) — also meets WCAG touch target 44px+.
- Label-to-field gap: 4 or 8px.
- Between field groups: 24 or 32px.
- Help text / hint: `line-height` 20px (4pt refinement for 14px hint).

## Table Row Rhythm

- Row height: baseline multiple; 40 (5x8) compact, 48 (6x8) default, 56 (7x8) comfortable.
- Header row 1.25x body row; optional.
- Vertical padding inside cell: 8 or 12.

## Visualising the Baseline

Dev-only overlay for verification:

```css
body.debug::before {
  content: "";
  position: fixed;
  inset: 0;
  background: repeating-linear-gradient(
    to bottom,
    transparent 0,
    transparent 23px,
    rgba(255, 0, 128, 0.15) 23px,
    rgba(255, 0, 128, 0.15) 24px
  );
  pointer-events: none;
  z-index: 9999;
}
```

Toggle with a keyboard shortcut during design review. Anything that fails to sit on the line is a bug.

## Common Baseline Mistakes

- Using `line-height` in decimals with rounding errors (body 1.6 of 17px = 27.2 — not a baseline multiple).
- Setting form field height 44px with input text 16px — 44 is not an 8pt multiple; use 40 or 48.
- Mixing `gap` values not on the scale (17px, 20px, 28px not on 8pt).
- Using fonts with outsized leading and not accounting for it in heading `line-height`.
- Letting auto-grown content drift off baseline (e.g. user-generated quotes) without explicit min-height snapping.

## Companion Reference

- `02-column-math.md` for horizontal alignment.
- `05-examples-checklist.md` for worked layouts and the review checklist.
