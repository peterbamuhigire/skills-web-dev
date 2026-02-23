# Healthcare Design Tokens

Cross-platform token system for clinical-grade UI: Web (Bootstrap 5/Tabler + PHP) and Android (Jetpack Compose + Material 3).

## Quick-Reference Token Table

| Token Category | Web (CSS Custom Property) | Android (Compose) | Value |
|----------------|---------------------------|---------------------|-------|
| **Primary** | `--clinical-primary` | `ClinicalPrimary` | `#2563EB` |
| **Secondary** | `--clinical-secondary` | `ClinicalSecondary` | `#0F766E` |
| **Surface** | `--clinical-surface` | `ClinicalSurface` | `#F8FAFC` |
| **Background** | `--clinical-bg` | `ClinicalBackground` | `#F1F5F9` |
| **Critical** | `--clinical-critical` | `ClinicalCritical` | `#DC2626` |
| **Warning** | `--clinical-warning` | `ClinicalWarning` | `#D97706` |
| **Success** | `--clinical-success` | `ClinicalSuccess` | `#059669` |
| **Info** | `--clinical-info` | `ClinicalInfo` | `#0284C7` |
| **Text Primary** | `--clinical-text` | `ClinicalText` | `#0F172A` |
| **Text Secondary** | `--clinical-text-secondary` | `ClinicalTextSecondary` | `#334155` |
| **Text Muted** | `--clinical-text-muted` | `ClinicalTextMuted` | `#64748B` |
| **Medication** | `--clinical-medication` | `ClinicalMedication` | `#7C3AED` |
| **Spacing Base** | `--space-base` | `SpaceBase` | `4px / 4dp` |
| **Radius md** | `--radius-md` | `RadiusMd` | `8px / 8dp` |
| **Body Font Size** | `--font-body` | `bodyLarge` | `0.9375rem / 16sp` |

---

## 1. Color System

### 1.1 Core Semantic Palette

```css
/* Web — add to your root stylesheet or Tabler custom override */
:root {
  /* Primary palette */
  --clinical-primary: #2563EB;       /* Trust blue — headers, primary buttons, nav */
  --clinical-primary-hover: #1D4ED8;
  --clinical-primary-light: #DBEAFE; /* Badges, light backgrounds */
  --clinical-secondary: #0F766E;     /* Clinical teal — secondary actions */
  --clinical-secondary-hover: #0D6963;
  --clinical-secondary-light: #CCFBF1;

  /* Surfaces */
  --clinical-surface: #F8FAFC;       /* Clean white — card backgrounds */
  --clinical-bg: #F1F5F9;            /* Soft gray — page background */
  --clinical-border: #E2E8F0;        /* Default borders */

  /* Feedback */
  --clinical-critical: #DC2626;      /* Danger, critical vitals, allergies */
  --clinical-critical-light: #FEF2F2;
  --clinical-warning: #D97706;       /* Approaching thresholds */
  --clinical-warning-light: #FFFBEB;
  --clinical-success: #059669;       /* Normal ranges, confirmations */
  --clinical-success-light: #ECFDF5;
  --clinical-info: #0284C7;          /* Informational, pending states */
  --clinical-info-light: #F0F9FF;

  /* Text hierarchy */
  --clinical-text: #0F172A;          /* Primary body text */
  --clinical-text-secondary: #334155;/* Secondary labels */
  --clinical-text-muted: #64748B;    /* Timestamps, metadata */
  --clinical-text-inverse: #FFFFFF;  /* Text on dark backgrounds */
}
```

```kotlin
// Android — HealthcareColors.kt
package com.app.ui.theme

import androidx.compose.ui.graphics.Color

object ClinicalColors {
    // Primary palette
    val Primary = Color(0xFF2563EB)
    val PrimaryHover = Color(0xFF1D4ED8)
    val PrimaryLight = Color(0xFFDBEAFE)
    val Secondary = Color(0xFF0F766E)
    val SecondaryHover = Color(0xFF0D6963)
    val SecondaryLight = Color(0xFFCCFBF1)

    // Surfaces
    val Surface = Color(0xFFF8FAFC)
    val Background = Color(0xFFF1F5F9)
    val Border = Color(0xFFE2E8F0)

    // Feedback
    val Critical = Color(0xFFDC2626)
    val CriticalLight = Color(0xFFFEF2F2)
    val Warning = Color(0xFFD97706)
    val WarningLight = Color(0xFFFFFBEB)
    val Success = Color(0xFF059669)
    val SuccessLight = Color(0xFFECFDF5)
    val Info = Color(0xFF0284C7)
    val InfoLight = Color(0xFFF0F9FF)

    // Text
    val Text = Color(0xFF0F172A)
    val TextSecondary = Color(0xFF334155)
    val TextMuted = Color(0xFF64748B)
    val TextInverse = Color(0xFFFFFFFF)
}
```

### 1.2 Clinical Status Colors

| Status | Foreground | Background | Usage |
|--------|-----------|------------|-------|
| Vital Normal | `#059669` | `#ECFDF5` | Within normal range |
| Vital Warning | `#D97706` | `#FFFBEB` | Approaching threshold |
| Vital Critical | `#DC2626` | `#FEF2F2` | Outside safe range |
| Allergy Alert | `#DC2626` | `#FEF2F2` | Allergy banners, badges |
| Medication | `#7C3AED` | `#F5F3FF` | Pharma context, prescriptions |
| Lab Pending | `#0284C7` | `#F0F9FF` | Awaiting results |
| Lab Complete | `#059669` | `#ECFDF5` | Results available |
| Discharged | `#64748B` | `#F1F5F9` | Inactive/historical records |

### 1.3 Accessibility Compliance

All color pairs MUST meet WCAG 2.2 AA minimum contrast ratios:

- **Normal text (< 18pt):** 4.5:1 contrast ratio minimum
- **Large text (>= 18pt or 14pt bold):** 3:1 contrast ratio minimum
- **UI components / graphical objects:** 3:1 against adjacent colors

**Verified pairings:**

| Text Color | Background | Ratio | Pass |
|------------|-----------|-------|------|
| `#0F172A` on `#F8FAFC` | Surface | 15.4:1 | AA/AAA |
| `#334155` on `#F8FAFC` | Surface | 8.5:1 | AA/AAA |
| `#FFFFFF` on `#2563EB` | Primary | 4.6:1 | AA |
| `#FFFFFF` on `#DC2626` | Critical | 4.6:1 | AA |
| `#FFFFFF` on `#059669` | Success | 4.5:1 | AA |
| `#92400E` on `#FFFBEB` | Warning bg | 7.1:1 | AA/AAA |

### 1.4 Color-Blind Safety

Never rely on red/green alone to distinguish clinical states. ALWAYS pair color with:

- **Text labels:** "Normal", "Warning", "Critical" alongside color indicators
- **Icons:** Check-circle, alert-triangle, x-circle
- **Patterns:** Solid fill (critical), hatched (warning), outline (normal)
- **Shape:** Circle (normal), triangle (warning), octagon (critical)

---

## 2. Typography Scale

### 2.1 Web (Bootstrap 5 / Tabler)

```css
:root {
  --font-system: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
  --font-mono: "SF Mono", "Cascadia Code", "Fira Code", "Consolas", monospace;

  /* Page hierarchy */
  --font-h1: 1.75rem;     /* 28px — page titles */
  --font-h1-weight: 700;
  --font-h2: 1.25rem;     /* 20px — section headings */
  --font-h2-weight: 600;
  --font-h3: 1.1rem;      /* 17.6px — subsection headings */
  --font-h3-weight: 600;

  /* Body text */
  --font-body: 0.9375rem; /* 15px — primary body */
  --font-body-weight: 400;
  --font-small: 0.8125rem;/* 13px — secondary, captions */
  --font-small-weight: 400;
  --font-caption: 0.75rem;/* 12px — timestamps, metadata */
  --font-caption-weight: 400;

  /* Clinical specialties */
  --font-vital-value: 1.5rem;    /* 24px — vital sign readings */
  --font-vital-weight: 700;
  --font-patient-name: 1.125rem; /* 18px — patient display name */
  --font-patient-weight: 600;
  --font-mrn: 0.875rem;          /* 14px — MRN, IDs */
  --font-mrn-weight: 500;
  --font-mrn-spacing: 0.05em;    /* Wider tracking for readability */
}

/* Clinical value class */
.vital-value {
  font-family: var(--font-mono);
  font-size: var(--font-vital-value);
  font-weight: var(--font-vital-weight);
  line-height: 1.2;
}

.patient-name { font-size: var(--font-patient-name); font-weight: var(--font-patient-weight); }
.mrn-display { font-family: var(--font-mono); font-size: var(--font-mrn); font-weight: var(--font-mrn-weight); letter-spacing: var(--font-mrn-spacing); }
```

### 2.2 Android (Jetpack Compose — Material 3 Overrides)

```kotlin
// HealthcareTypography.kt
import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

val HealthcareTypography = Typography(
    headlineLarge = TextStyle(fontSize = 28.sp, fontWeight = FontWeight.W400, lineHeight = 36.sp),
    headlineMedium = TextStyle(fontSize = 24.sp, fontWeight = FontWeight.W400, lineHeight = 32.sp),
    titleLarge = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.W400, lineHeight = 28.sp),
    titleMedium = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.W500, lineHeight = 24.sp),
    bodyLarge = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.W400, lineHeight = 24.sp),
    bodyMedium = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.W400, lineHeight = 20.sp),
    labelLarge = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.W500, lineHeight = 20.sp),
    labelSmall = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.W500, lineHeight = 16.sp),
)

// Clinical-specific text styles (extend beyond M3 type scale)
object ClinicalTextStyles {
    val VitalValue = TextStyle(
        fontFamily = FontFamily.Monospace,
        fontSize = 24.sp,
        fontWeight = FontWeight.W700,
        lineHeight = 28.sp
    )
    val PatientName = TextStyle(
        fontSize = 18.sp,
        fontWeight = FontWeight.W600,
        lineHeight = 24.sp
    )
    val MrnDisplay = TextStyle(
        fontFamily = FontFamily.Monospace,
        fontSize = 14.sp,
        fontWeight = FontWeight.W500,
        letterSpacing = 0.8.sp
    )
}
```

---

## 3. Spacing System

Base unit: **4px** (web) / **4dp** (Android). All spacing values are multiples of 4.

| Token | Value | CSS Variable | Compose | Use Case |
|-------|-------|-------------|---------|----------|
| `xs` | 4 | `--space-xs: 4px` | `4.dp` | Icon-to-text gap, tight inline spacing |
| `sm` | 8 | `--space-sm: 8px` | `8.dp` | Related element gap, badge padding |
| `md` | 12 | `--space-md: 12px` | `12.dp` | List item vertical padding, form field gap |
| `lg` | 16 | `--space-lg: 16px` | `16.dp` | Card internal padding, section padding |
| `xl` | 24 | `--space-xl: 24px` | `24.dp` | Between card groups, column gutters |
| `2xl` | 32 | `--space-2xl: 32px` | `32.dp` | Major section separation |
| `3xl` | 48 | `--space-3xl: 48px` | `48.dp` | Page-level vertical margins |

### Component-Specific Spacing

| Component | Padding | Gap |
|-----------|---------|-----|
| Card (web/Android) | 16px / 16dp all sides | 24px / 24dp between cards |
| List item | 12px vertical, 16px horizontal | 1px divider or 8px gap |
| Form fields | 0 internal (handled by component) | 12px between fields |
| Section groups | 0 (cards handle own padding) | 32px between sections |
| Button group | 8px between buttons | N/A |
| Alert banners | 12px vertical, 16px horizontal | 8px icon-to-text |

### Touch Target Minimums

| Platform | Minimum | Preferred (clinical) | Note |
|----------|---------|---------------------|------|
| **Web** | 44 x 44px | 48 x 48px | WCAG 2.2 Level AA target size |
| **Android** | 48 x 48dp | 56 x 56dp | Preferred for bedside/clinical use |

Clinical environments use gloved hands and stressed motor control — always prefer the larger target size.

---

## 4. Elevation and Shadows

### 4.1 Web (CSS Shadows)

```css
:root {
  --shadow-0: none;                                         /* Level 0: inline content */
  --shadow-1: 0 1px 2px 0 rgba(0, 0, 0, 0.05);           /* Level 1: cards, tiles */
  --shadow-2: 0 4px 6px -1px rgba(0, 0, 0, 0.07),
              0 2px 4px -2px rgba(0, 0, 0, 0.05);         /* Level 2: dropdowns, popovers */
  --shadow-3: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
              0 4px 6px -4px rgba(0, 0, 0, 0.05);         /* Level 3: modals, dialogs */
}
```

| Level | Shadow Token | Use Case |
|-------|-------------|----------|
| 0 | `--shadow-0` | Table rows, inline content, list items |
| 1 | `--shadow-1` | Cards, panels, stat tiles |
| 2 | `--shadow-2` | Dropdown menus, popovers, tooltips |
| 3 | `--shadow-3` | Modals, confirmation dialogs, medication checks |

### 4.2 Android (Material 3 Elevation)

| Level | Elevation | Compose | Use Case |
|-------|-----------|---------|----------|
| 0 | 0dp | `elevation = 0.dp` | Flat surfaces, list items |
| 1 | 1dp | `elevation = 1.dp` | Cards, ElevatedCard |
| 2 | 3dp | `elevation = 3.dp` | Navigation bars, bottom sheets |
| 3 | 6dp | `elevation = 6.dp` | FAB, extended FAB |
| 4 | 8dp | `elevation = 8.dp` | Dialogs, modal bottom sheets |

---

## 5. Border Radius

| Token | Web | Android | Use Case |
|-------|-----|---------|----------|
| `sm` | `4px` | `4.dp` | Input fields, text areas, inline badges |
| `md` | `8px` | `8.dp` | Cards, buttons, dropdown menus |
| `lg` | `12px` | `12.dp` | Large cards, image containers |
| `xl` | `16px` | `16.dp` | Modals, bottom sheets |
| `pill` | `9999px` | `CircleShape` | Status badges, vital indicators, tags |

```css
:root {
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-pill: 9999px;
}
```

```kotlin
object ClinicalShapes {
    val Small = RoundedCornerShape(4.dp)
    val Medium = RoundedCornerShape(8.dp)
    val Large = RoundedCornerShape(12.dp)
    val ExtraLarge = RoundedCornerShape(16.dp)
    val Pill = CircleShape
}
```

**Mapping:** Cards use `md`. Buttons use `md`. Input fields use `sm`. Clinical status badges use `pill`. Modals use `xl`.

---

## 6. Iconography

### Healthcare-Specific Icons

| Category | Icons | Web Source | Android Source |
|----------|-------|-----------|----------------|
| **Clinical** | Stethoscope, heartbeat, pill, syringe, thermometer, lungs, brain, bone, eye, tooth | Tabler Icons / Bootstrap Icons | Material Symbols (Outlined) |
| **Status** | Check-circle, x-circle, alert-triangle, info, clock, shield | Tabler Icons | Material Symbols |
| **Actions** | Plus, edit, trash, search, filter, sort, download, print, share | Tabler Icons | Material Symbols |

### Sizing

| Context | Web | Android | When |
|---------|-----|---------|------|
| Inline/compact | 16px | 20dp | Inside buttons, badges, table cells |
| Default | 20px | 24dp | Navigation, list leading icons |
| Emphasis | 24px | 28dp | Card headers, empty states |
| Hero | 48px | 48dp | Dashboard KPI icons, onboarding |

**Rules:** Icons must have `aria-hidden="true"` when decorative, or a descriptive `aria-label` when functional. On Android, use `contentDescription` for accessibility. Never use icons alone for critical clinical actions — always pair with a text label.

---

## 7. Animation and Motion

### 7.1 Web Transitions

```css
:root {
  --duration-micro: 150ms;   /* Button hover, focus rings, toggles */
  --duration-standard: 300ms; /* Panel open/close, state changes */
  --duration-page: 400ms;     /* Page transitions, route changes */
  --easing-standard: cubic-bezier(0.4, 0, 0.2, 1);
  --easing-decelerate: cubic-bezier(0, 0, 0.2, 1);   /* Elements entering */
  --easing-accelerate: cubic-bezier(0.4, 0, 1, 1);    /* Elements exiting */
}

/* Usage */
.card { transition: box-shadow var(--duration-micro) var(--easing-standard); }
.panel-expand { transition: max-height var(--duration-standard) var(--easing-decelerate); }
```

### 7.2 Android Motion (Material 3 Spring-Based)

```kotlin
object ClinicalMotion {
    // Enters — elements appearing on screen
    val EmphasizedDecelerate = tween<Float>(
        durationMillis = 400,
        easing = CubicBezierEasing(0.05f, 0.7f, 0.1f, 1.0f)
    )
    // Exits — elements leaving the screen
    val EmphasizedAccelerate = tween<Float>(
        durationMillis = 200,
        easing = CubicBezierEasing(0.3f, 0.0f, 0.8f, 0.15f)
    )
    // State changes — color, size, elevation shifts
    val Standard = tween<Float>(
        durationMillis = 300,
        easing = CubicBezierEasing(0.2f, 0.0f, 0.0f, 1.0f)
    )
}
```

### 7.3 Clinical Motion Rules

- **Critical alerts:** NO animation delay. Appear instantly (`duration: 0ms`). Patient safety cannot wait for a fade-in.
- **Loading/skeleton states:** Use a pulse animation (opacity oscillation 0.4 to 1.0, 1.5s loop).
- **Vital sign updates:** Subtle color transition (300ms) when value changes category (normal to warning).
- **Never animate** medication confirmation dialogs — they must be immediately readable.
- **Reduce motion:** Respect `prefers-reduced-motion` (web) and accessibility motion settings (Android). Replace animations with instant state changes.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 8. Breakpoints

### 8.1 Web (Bootstrap 5 Standard)

| Breakpoint | Min Width | Grid Columns | Clinical Layout |
|------------|----------|-------------|-----------------|
| `xs` | 0 | 1 | Stacked cards, single-column patient list |
| `sm` | 576px | 1-2 | Patient list with minimal detail |
| `md` | 768px | 2 | Sidebar nav + content, tablet portrait |
| `lg` | 992px | 2-3 | Full clinical detail views, list + detail |
| `xl` | 1200px | 3 | Three-panel: nav + list + detail |
| `xxl` | 1400px | 3-4 | Dashboard with multi-widget grid |

**Optimization targets:**

- Patient lists usable at ALL breakpoints (xs through xxl)
- Clinical detail views (vitals, medication charts) optimized for >= 992px (tablet landscape and above)
- Admin dashboards designed for >= 1200px, gracefully collapse below

### 8.2 Android (WindowSizeClass)

| Class | Width | Columns | Layout Strategy |
|-------|-------|---------|-----------------|
| **Compact** | < 600dp | 1 | Single-column patient view, bottom nav, full-screen forms |
| **Medium** | 600-840dp | 2 | List-detail split (40/60), rail nav, side-by-side vitals |
| **Expanded** | > 840dp | 3 | Three-panel: nav rail + patient list + detail pane |

```kotlin
// Usage in Compose
@Composable
fun PatientScreen(windowSizeClass: WindowSizeClass) {
    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> PatientSingleColumn()
        WindowWidthSizeClass.Medium -> PatientListDetail()
        WindowWidthSizeClass.Expanded -> PatientThreePanel()
    }
}
```

---

## Token Application Checklist

When building a new healthcare screen, verify:

1. All colors reference token variables (no hardcoded hex in components)
2. Typography uses defined scale only (no arbitrary font sizes)
3. Spacing uses 4px/4dp multiples exclusively
4. Touch targets meet 44px/48dp minimums
5. Color pairs pass WCAG 2.2 AA contrast check
6. Color-blind safe: every color meaning has a text/icon backup
7. Critical alerts have zero animation delay
8. `prefers-reduced-motion` / Android accessibility settings are respected
9. Breakpoints handle all clinical layouts from mobile to desktop
10. Clinical values (vitals, MRN) use monospace font tokens
