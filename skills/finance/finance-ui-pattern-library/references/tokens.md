# Design Tokens

The token bundle for Chwezi finance UI. Reference values; consumer projects can shift the brand hue but not the semantic colours or the typographic scale.

## JSON bundle

```json
{
  "type": {
    "family-sans": "Inter, IBM Plex Sans, system-ui, sans-serif",
    "family-mono": "JetBrains Mono, IBM Plex Mono, ui-monospace, monospace",
    "numerals": "tabular-nums",
    "scale": { "1": 11, "2": 12, "3": 14, "4": 16, "5": 18, "6": 24, "7": 32 },
    "weight": { "regular": 400, "medium": 500, "semibold": 600, "bold": 700 },
    "leading": { "tight": 1.15, "normal": 1.4, "loose": 1.6 }
  },
  "space": { "base": 4, "1": 4, "2": 8, "3": 12, "4": 16, "5": 24, "6": 32, "7": 48 },
  "radius": { "none": 0, "sm": 2, "md": 4, "lg": 6, "pill": 9999 },
  "elevation": {
    "flat": "none",
    "menu": "0 4px 12px rgba(0,0,0,0.08)",
    "dialog": "0 12px 40px rgba(0,0,0,0.12)"
  },
  "motion": {
    "fast-ms": 120,
    "default-ms": 200,
    "never-ms": 0
  },
  "color": {
    "brand-primary": "#0F4C81",
    "neutral-bg":    "#FFFFFF",
    "neutral-fg":    "#0F172A",
    "neutral-muted": "#64748B",
    "neutral-line":  "#E2E8F0",
    "gain":          "#137A4A",
    "loss":          "#B22222",
    "warning":       "#A15C00",
    "info":          "#1F4E96",
    "locked":        "#475569",
    "reversed":      "#5B3F8C",
    "env-prod":      "transparent",
    "env-staging":   "#FFF7E6",
    "env-test":      "#FFE6E6"
  },
  "density": {
    "comfortable": { "row-h": 44, "pad-y": 12, "pad-x": 16 },
    "compact":     { "row-h": 28, "pad-y": 4,  "pad-x": 8 }
  }
}
```

## CSS variables (workflow surface — light, comfortable)

```css
:root {
  --font-sans: Inter, "IBM Plex Sans", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", "IBM Plex Mono", ui-monospace, monospace;
  --numerals: tabular-nums;

  --t-1: 11px; --t-2: 12px; --t-3: 14px; --t-4: 16px;
  --t-5: 18px; --t-6: 24px; --t-7: 32px;
  --w-regular: 400; --w-medium: 500; --w-semibold: 600; --w-bold: 700;

  --s-1: 4px; --s-2: 8px; --s-3: 12px; --s-4: 16px;
  --s-5: 24px; --s-6: 32px; --s-7: 48px;

  --c-brand: #0F4C81;
  --c-bg:    #FFFFFF;
  --c-fg:    #0F172A;
  --c-mute:  #64748B;
  --c-line:  #E2E8F0;

  --c-gain:     #137A4A;
  --c-loss:     #B22222;
  --c-warning:  #A15C00;
  --c-info:     #1F4E96;
  --c-locked:   #475569;
  --c-reversed: #5B3F8C;

  --row-h: 44px;
  --pad-y: 12px;
  --pad-x: 16px;
  --motion-fast: 120ms;
  --motion-default: 200ms;
}

[data-density="compact"] {
  --row-h: 28px; --pad-y: 4px; --pad-x: 8px;
}

[data-theme="dark"] {
  --c-bg: #0B1220;
  --c-fg: #E2E8F0;
  --c-mute: #94A3B8;
  --c-line: #1E293B;
}

.money {
  font-variant-numeric: var(--numerals);
  font-feature-settings: "tnum" 1;
  text-align: right;
}
```

## Tailwind extension (excerpt)

```js
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'IBM Plex Sans', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'IBM Plex Mono', 'ui-monospace', 'monospace'],
      },
      fontSize: {
        '1': ['11px',{lineHeight:'1.4'}],
        '2': ['12px',{lineHeight:'1.4'}],
        '3': ['14px',{lineHeight:'1.4'}],
        '4': ['16px',{lineHeight:'1.4'}],
        '5': ['18px',{lineHeight:'1.3'}],
        '6': ['24px',{lineHeight:'1.2'}],
        '7': ['32px',{lineHeight:'1.15'}],
      },
      colors: {
        brand:    { DEFAULT: '#0F4C81' },
        gain:     '#137A4A',
        loss:     '#B22222',
        warning:  '#A15C00',
        info:     '#1F4E96',
        locked:   '#475569',
        reversed: '#5B3F8C',
      }
    }
  }
}
```

## Mobile-native tokens

For React Native / Flutter / Kotlin / Swift, expose the same JSON bundle and consume per platform. Native modules must respect `motion-never-ms = 0` on numbers and `tabular-nums` everywhere money appears (use `SF Mono` / `Roboto Mono` for fallback on platforms without Inter tabular-nums).

## Print tokens

See `print-stylesheet-template.md` for the full print override set.

## Forbidden token usage

- Brand colour applied to status (use semantic colours).
- Semantic colour applied to chrome or brand surfaces.
- Type sizes outside the seven-step scale.
- Custom spacing values outside the 4 / 8 grid.

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
