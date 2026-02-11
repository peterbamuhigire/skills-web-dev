# Design Philosophy: Beautiful, Minimalistic Compose UI

## The Aesthetic Standard

Every app we build should feel like a premium product. Users should think:
"This looks clean," "This is easy to use," and "This feels fast."

### Three Pillars

1. **Clean** - No visual clutter, every pixel earns its place
2. **Consistent** - Same patterns, spacing, colors across every screen
3. **Fast** - Instant response to every touch, smooth transitions

## Visual Hierarchy Rules

### Content Layering (Top to Bottom)

```
1. Primary Action   - What should the user do NOW? (FAB, primary button)
2. Key Information   - What did they come to see? (title, main data)
3. Supporting Detail - What helps them decide? (metadata, stats)
4. Secondary Actions - What else can they do? (edit, share, delete)
```

### Typography Hierarchy

Use **exactly** these roles. Never invent custom text styles:

```kotlin
// Screen-level
headlineLarge  → Main screen title (28sp, bold intent)
headlineMedium → Secondary screen title (24sp)

// Section-level
titleLarge     → Section headers within a screen (22sp)
titleMedium    → Card/item titles (16sp, medium weight)
titleSmall     → Subheadings (14sp, medium weight)

// Body-level
bodyLarge      → Primary body text (16sp)
bodyMedium     → Secondary/supporting text (14sp)
bodySmall      → Tertiary/metadata text (12sp)

// Label-level
labelLarge     → Buttons, prominent labels (14sp, medium)
labelMedium    → Chips, tabs, small labels (12sp, medium)
labelSmall     → Captions, timestamps (11sp)
```

### Color Usage Philosophy

**Less color = more impact.** Use color sparingly and purposefully:

```
Surface colors → 90% of the screen (backgrounds, cards)
Primary color  → Key actions and navigation (FAB, active tab)
Secondary color → Supporting actions (chips, toggles)
Error color    → Errors and destructive actions only
```

**Never use raw hex colors in composables.** Always reference the theme:

```kotlin
// ALWAYS
color = MaterialTheme.colorScheme.primary
color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)

// NEVER
color = Color(0xFF6200EE)
color = Color.Gray
```

### Opacity Standards for Text

```kotlin
// Primary text (titles, body)
MaterialTheme.colorScheme.onSurface              // 100% opacity

// Secondary text (subtitles, metadata)
MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)

// Disabled/tertiary text (placeholders, hints)
MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f)

// Dividers and subtle borders
MaterialTheme.colorScheme.outlineVariant          // Built-in subtle
```

## Spacing System

### The 4dp Grid

All spacing must be multiples of 4dp. This creates visual rhythm:

```kotlin
object Spacing {
    val xs  = 4.dp    // Tight grouping (icon + label)
    val sm  = 8.dp    // Related items (list item padding)
    val md  = 16.dp   // Standard spacing (screen padding, card padding)
    val lg  = 24.dp   // Section separation
    val xl  = 32.dp   // Major section breaks
    val xxl = 48.dp   // Screen-level separation
}
```

### Where to Use Each

| Spacing  | Use Case                                                       |
| -------- | -------------------------------------------------------------- |
| **4dp**  | Icon-to-text gap, inline element spacing                       |
| **8dp**  | Between items in a group, vertical list spacing                |
| **12dp** | Between cards in a list (slightly more breathing room)         |
| **16dp** | Screen edge padding, card internal padding, form field spacing |
| **24dp** | Between distinct sections on a screen                          |
| **32dp** | Before/after major content blocks                              |
| **48dp** | Top/bottom padding on scrollable content                       |

### Card Padding Standard

```kotlin
// Every card follows this internal spacing:
Card {
    Column(modifier = Modifier.padding(16.dp)) {
        // Title row
        Text(title, style = MaterialTheme.typography.titleMedium)
        Spacer(Modifier.height(4.dp))  // Tight: title to subtitle
        Text(subtitle, style = MaterialTheme.typography.bodyMedium)
        Spacer(Modifier.height(12.dp)) // Moderate: content to actions
        // Action row
        Row { /* buttons */ }
    }
}
```

## Shape Language

### Corner Radius Standards

```kotlin
// Small elements (chips, badges, small buttons)
RoundedCornerShape(8.dp)

// Medium elements (cards, dialogs, text fields)
RoundedCornerShape(12.dp)

// Large elements (bottom sheets, full-width cards)
RoundedCornerShape(16.dp)

// Pills (search bars, segmented controls)
RoundedCornerShape(24.dp)

// Circles (avatars, FABs)
CircleShape
```

**Rule:** All shapes must use rounded corners. Never use sharp 0dp corners.

## Elevation Strategy

**Flat design with subtle depth cues.** Avoid heavy shadows:

```kotlin
// Level 0: Flush with background (most content)
CardDefaults.cardElevation(defaultElevation = 0.dp)

// Level 1: Slight lift (cards, list items)
CardDefaults.cardElevation(defaultElevation = 1.dp)

// Level 2: Interactive elements (FAB resting, selected cards)
CardDefaults.cardElevation(defaultElevation = 2.dp)

// Level 3: Overlays only (dialogs, bottom sheets, dropdowns)
// Handled by Material 3 components automatically
```

**Use surface tint over shadows.** Material 3's `tonalElevation` creates depth through color tint rather than shadow, which looks more modern:

```kotlin
Card(
    colors = CardDefaults.cardColors(
        containerColor = MaterialTheme.colorScheme.surfaceColorAtElevation(1.dp)
    )
)
```

## Icon Usage

### Standard Icon Sizes

```kotlin
val IconSmall = 16.dp    // Inside buttons, chips
val IconDefault = 24.dp  // Standard toolbar/list icons
val IconLarge = 32.dp    // Feature icons, section headers
val IconHero = 48.dp     // Empty states, error states
```

### Icon Style Rules

- Use **custom PNG icons** only (no icon libraries)
- Always provide `contentDescription` for accessibility
- Use `tint` from theme when the icon is monochrome; do not hardcode colors

```kotlin
Icon(
    painter = painterResource(R.drawable.favorite),
    contentDescription = "Add to favorites",
    tint = MaterialTheme.colorScheme.onSurface,
    modifier = Modifier.size(24.dp)
)
```

## Dark Theme Standards

Dark theme is not an afterthought. Design for both simultaneously:

```kotlin
// Always preview both:
@Preview(name = "Light")
@Preview(name = "Dark", uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
private fun CardPreview() {
    AppTheme {
        StandardCard { /* content */ }
    }
}
```

### Dark Theme Color Rules

- Background: `#121212` to `#1E1E1E` range (never pure black `#000000`)
- Surface: Slightly lighter than background for card separation
- Text: `#E0E0E0` to `#FFFFFF` (never pure white on pure dark - too much contrast)
- Primary: Use lighter variant of brand color for better readability

## Responsive Design

All apps MUST work on phones AND tablets. Use `WindowSizeClass` for adaptive layouts — never hardcode device checks. See `responsive-adaptive.md` for the complete 4-step playbook.

### Adaptive Spacing (WindowSizeClass-Based)

```kotlin
// Use WindowSizeClass breakpoints — not isTablet() booleans
val screenPadding = when {
    windowSizeClass.isWidthAtLeastBreakpoint(
        WindowSizeClass.WIDTH_DP_EXPANDED_LOWER_BOUND
    ) -> 32.dp
    windowSizeClass.isWidthAtLeastBreakpoint(
        WindowSizeClass.WIDTH_DP_MEDIUM_LOWER_BOUND
    ) -> 24.dp
    else -> 16.dp
}

// Constrain content width on large screens
val maxContentWidth = when {
    windowSizeClass.isWidthAtLeastBreakpoint(
        WindowSizeClass.WIDTH_DP_EXPANDED_LOWER_BOUND
    ) -> 840.dp
    windowSizeClass.isWidthAtLeastBreakpoint(
        WindowSizeClass.WIDTH_DP_MEDIUM_LOWER_BOUND
    ) -> 600.dp
    else -> Dp.Unspecified
}

Box(
    modifier = Modifier.fillMaxSize(),
    contentAlignment = Alignment.TopCenter
) {
    Column(
        modifier = Modifier
            .then(
                if (maxContentWidth != Dp.Unspecified) Modifier.widthIn(max = maxContentWidth)
                else Modifier.fillMaxWidth()
            )
            .padding(horizontal = screenPadding)
    ) {
        // Content stays readable on all screen sizes
    }
}
```

## Checklist: Is This Screen Beautiful?

- [ ] Uses only theme colors (no hardcoded hex values)
- [ ] Uses only theme typography (no custom TextStyles)
- [ ] Spacing follows the 4dp grid
- [ ] Cards have 12-16dp rounded corners
- [ ] Elevation is subtle (0-2dp for content)
- [ ] Touch targets are minimum 48dp
- [ ] Empty/loading/error states are designed, not placeholder
- [ ] Dark theme looks intentional, not accidental
- [ ] Whitespace is generous - screen doesn't feel cramped
- [ ] Visual hierarchy is clear within 2 seconds of looking
- [ ] Layout adapts properly on phone, tablet, and foldable screens
- [ ] No wall of whitespace or stretched components on tablets
