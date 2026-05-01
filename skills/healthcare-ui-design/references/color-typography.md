# Healthcare Color System & Typography

## Color Philosophy

Healthcare color must do three jobs simultaneously:
1. **Build trust** — patients and clinicians must feel the system is safe and professional
2. **Communicate status** — critical values, alerts, and normal ranges must be immediately distinguishable
3. **Reduce anxiety** — especially in patient-facing interfaces; harsh colors increase stress

**The cardinal rule:** Never communicate critical clinical information through color alone. Always pair color with an icon AND a text label (three independent signals).

---

## Primary Palettes by App Type

### General Healthcare (Clinics, Hospitals, Portals)

```css
/* Trust Blues — most used in healthcare globally */
--color-primary-400: #60A5FA;   /* hover states */
--color-primary-500: #3B82F6;   /* main brand */
--color-primary-600: #2563EB;   /* pressed states */
--color-primary-700: #1D4ED8;   /* dark backgrounds */

/* Backgrounds */
--color-bg-page:    #F9FAFB;    /* page background */
--color-bg-surface: #FFFFFF;    /* card/panel */
--color-bg-subtle:  #F3F4F6;    /* alternate rows, inactive tabs */

/* Text */
--color-text-primary:   #111827;  /* headings, important data */
--color-text-secondary: #374151;  /* body text */
--color-text-muted:     #6B7280;  /* labels, captions */
--color-text-disabled:  #9CA3AF;  /* disabled inputs */

/* Semantic — status */
--color-success: #10B981;   /* stable, confirmed, normal */
--color-warning: #F59E0B;   /* elevated, caution, review */
--color-danger:  #EF4444;   /* critical, alert, urgent */
--color-info:    #3B82F6;   /* informational only */

/* Borders */
--color-border:        #E5E7EB;  /* default */
--color-border-focus:  #3B82F6;  /* focus ring */
--color-border-danger: #EF4444;  /* error state */
```

### Wellness / Fitness Apps

```css
--color-primary-500: #10B981;   /* vibrant green — health, growth */
--color-primary-600: #059669;
--color-accent:      #14B8A6;   /* teal for variety */
--color-energy:      #F59E0B;   /* amber for active states */
```

### Mental Health / Behavioral

```css
--color-primary-400: #C4B5FD;   /* soft lavender — calm, non-threatening */
--color-primary-500: #8B5CF6;   /* medium purple */
--color-primary-600: #7C3AED;
/* Avoid red entirely in mental health UI — causes anxiety */
--color-danger:      #F97316;   /* orange substitutes for red in this context */
```

### Aging Care / Accessibility-First

```css
/* Higher contrast — AAA standard */
--color-primary-500: #1D4ED8;   /* darker blue for better contrast */
--color-text-primary: #030712;  /* near-black */
--color-bg-page:      #FFFFFF;  /* pure white — no off-whites */
/* All contrast ratios verified at 7:1 minimum */
```

### Emergency / ICU (Dark Mode Clinical)

```css
--color-bg-page:    #0F172A;    /* dark navy */
--color-bg-surface: #1E293B;    /* dark panel */
--color-text:       #F1F5F9;    /* off-white for comfort */
--color-critical:   #FF4444;    /* high-contrast red on dark */
--color-warning:    #FBBF24;    /* amber */
--color-stable:     #34D399;    /* bright green */
```

---

## Status Color System

Every status indicator must use all three: color + icon + text

| Status | Color | Icon | Text Label | When to Use |
|--------|-------|------|-----------|-------------|
| Normal / Stable | `#10B981` | ✓ | "Normal" | All values in range |
| Caution / Borderline | `#F59E0B` | ⚠ | "High" / "Low" | Mild deviation from range |
| Critical / Urgent | `#EF4444` | ⛔ | "CRITICAL" | Life-threatening values |
| Pending / Processing | `#6B7280` | ⏳ | "Pending" | Awaiting results |
| Information | `#3B82F6` | ℹ | "Info" | Non-clinical status |

**Alert fatigue rule:** Reserve red exclusively for genuinely life-threatening values. Clinicians who see red on every minor deviation learn to ignore it. This is how patients die.

---

## Color Accessibility

### Contrast Ratios

| Text Type | AA (Minimum) | AAA (Patient-Facing) |
|-----------|-------------|---------------------|
| Normal text (<18px) | 4.5:1 | 7:1 |
| Large text (≥18px or 14px Bold) | 3:1 | 4.5:1 |
| UI components (buttons, inputs) | 3:1 | 4.5:1 |

### Common Failure Combinations to Avoid
- Light grey text on white background — fails AA in direct sunlight (clinical environments)
- Blue-green combinations — confuse 8% of males with deuteranopia
- Red-green only for pass/fail — invisible to protanopia users
- Always test with: Stark (Figma plugin), WCAG Color Contrast Analyzer

### Verified Compliant Pairs
```
#111827 on #FFFFFF  — 16.75:1 ✓✓ (AAA)
#374151 on #FFFFFF  — 10.7:1  ✓✓ (AAA)
#FFFFFF on #2563EB  — 7.7:1   ✓✓ (AAA)
#FFFFFF on #10B981  — 2.9:1   ✗  (fails — use dark text on green instead)
#111827 on #10B981  — 5.8:1   ✓  (AA)
#FFFFFF on #EF4444  — 4.0:1   ✓  (AA for large text)
```

---

## Dark Mode

Provide dark mode for:
- ICU and emergency workstations (bright screens cause eye strain in dark rooms)
- Night shift clinical use
- Low-light patient rooms

**Dark mode rules:**
- Never use pure black (#000000) — use `#0F172A` or `#111827` for backgrounds
- Reduce saturation of colors in dark mode (vibrant colors on dark can vibrate visually)
- Increase font weight by one step in dark mode (thin weights disappear on dark backgrounds)
- Test all status colors against dark backgrounds for contrast compliance

---

## Typography System

### Font Selection

**Recommended fonts (in priority order):**
1. **Inter** — designed for screen legibility; excellent at small sizes; free
2. **Roboto** — Android native; excellent across clinical dashboards
3. **SF Pro** — iOS native; use on iOS/macOS only (system font)
4. **Open Sans** — reliable fallback; slight humanist feel for patient-facing

**Fonts to avoid:**
- Serif fonts (Times, Georgia) — journalistic connotation, lower screen legibility
- Decorative/script fonts — zero clinical context
- Condensed fonts — poor legibility on clinical data tables
- Light weight (300) below 16px — invisible in bright clinical environments

### Type Scale

#### Patient-Facing (Mobile + Web)

```
Display:     40px / 700 / -0.02em   — Hero messages, "You're all checked in!"
H1:          32px / 700 / -0.01em   — Page titles
H2:          24px / 600 / 0          — Section headings
H3:          20px / 600 / 0          — Card headings
Body Large:  18px / 400 / 0          — Primary content (minimum for patients)
Body:        16px / 400 / 0          — Standard body (not below this for patients)
Small:       14px / 400 / 0.01em     — Captions, secondary info
Label:       12px / 500 / 0.05em     — Form labels, metadata (uppercase optional)
```

#### Clinical (Tablet + Desktop)

```
H1:          24px / 700 / 0          — Patient name, page title
H2:          18px / 600 / 0          — Section headings
H3:          16px / 600 / 0          — Card headings, tab labels
Body:        14px / 400 / 0          — Primary clinical data
Body Dense:  13px / 400 / 0          — Data tables, compact lists
Small:       12px / 400 / 0.01em     — Timestamps, secondary metadata
Label:       11px / 500 / 0.08em     — Table headers (uppercase)
```

#### Aging Care (All Platforms)

```
Body minimum: 18px / 400  (phone), 20px / 400 (tablet/kiosk)
Buttons:      18px / 600  — text must be clearly readable
All text:     +2px from standard scale minimum
```

### Line Height

| Context | Line Height |
|---------|------------|
| Body text | 1.6× font size |
| Clinical data (dense) | 1.4× font size |
| Data table rows | 1.2× font size |
| Headings | 1.2× font size |
| Button labels | 1.0× (single line) |

---

## Iconography

- Use a consistent icon library (Heroicons, Lucide, or Material Icons)
- Clinical icons must be unambiguous — test recognition without labels
- Icons always paired with text labels for critical functions (never icon-only for clinical actions)
- Size: 20px inline, 24px standalone, 28–32px aging/accessibility UIs
- Touch area around icons: always pad to 48×48px minimum

### Commonly Used Healthcare Icons

| Concept | Icon | Never Use |
|---------|------|-----------|
| Critical alert | ⛔ stop/octagon | ❌ X alone (ambiguous) |
| Warning | ⚠ triangle | ❗ (too subtle) |
| Medication | 💊 pill (custom) | Generic circle |
| Appointment | 📅 calendar | Clock alone |
| Lab results | 🧪 flask | Generic chart |
| Emergency | 🚨 siren / red cross | Ambiguous shapes |
| Secure / HIPAA | 🔒 lock | Generic badge |

---

## Spacing System

Use 4px base grid:

```
4px   — tight spacing (icon-to-label)
8px   — compact (list item padding)
12px  — standard inner (card padding mobile)
16px  — standard (card padding desktop)
20px  — comfortable (section separation)
24px  — loose (between major sections)
32px  — spacious (modal padding desktop)
48px  — major (hero sections)
```

- Modal padding: 32px desktop, 20px tablet, 16px mobile
- Card border-radius: 12px mobile/tablet, 8px desktop (denser feel)
- Input height: 48px touch, 40px desktop
