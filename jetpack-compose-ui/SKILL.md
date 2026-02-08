---
name: jetpack-compose-ui
description: "Jetpack Compose UI standards for beautiful, sleek, minimalistic Android apps. Enforces Material 3 design, unidirectional data flow, state hoisting, consistent theming, smooth animations, and performance patterns. Use when building or reviewing Compose UI code to ensure modern, user-friendly, fast-loading interfaces that are standard across all apps."
---

# Jetpack Compose UI Standards

## Design Philosophy

**Goal:** Every screen should feel beautiful, sleek, fast, and effortless to use.

### Core Design Principles

1. **Minimalism over decoration** - Remove anything that doesn't serve the user
2. **Consistency over novelty** - Same patterns across every app screen
3. **Whitespace is a feature** - Generous spacing creates visual breathing room
4. **Speed is UX** - If it feels slow, it's broken regardless of how it looks
5. **Content-first hierarchy** - Important information is immediately visible
6. **Touch-friendly targets** - Minimum 48dp for all interactive elements

### Visual Standards

| Element | Standard |
|---------|----------|
| **Corner radius** | 12-16dp for cards, 8dp for inputs, 24dp for FABs |
| **Card elevation** | 0-2dp (subtle shadows, never heavy) |
| **Content padding** | 16dp horizontal, 8-16dp vertical between items |
| **Screen padding** | 16dp all sides (24dp on tablets) |
| **Touch targets** | Minimum 48dp height/width |
| **Icon size** | 24dp standard, 20dp in buttons, 48dp for empty states |
| **Typography scale** | Use Material 3 type scale exclusively |

## Quick Reference

| Topic | Reference File | When to Use |
|-------|---------------|-------------|
| **Design Philosophy** | `references/design-philosophy.md` | Visual standards, spacing, color, typography |
| **Composable Patterns** | `references/composable-patterns.md` | State hoisting, MVVM, screen templates |
| **Layouts & Components** | `references/layout-and-components.md` | Layouts, modifiers, Material components |
| **Animation & Polish** | `references/animation-and-polish.md` | Transitions, micro-interactions, loading |
| **Navigation & Perf** | `references/navigation-and-performance.md` | Nav setup, deep links, optimization |

## Core Compose Principles

### 1. Declarative UI

Describe **what** the UI looks like, not **how** to build it:

```kotlin
// The UI is a function of state - nothing more
@Composable
fun UserCard(user: User, modifier: Modifier = Modifier) {
    Card(modifier = modifier) {
        Text(user.name, style = MaterialTheme.typography.titleMedium)
    }
}
```

### 2. Unidirectional Data Flow

```
State flows DOWN  (ViewModel -> Screen -> Components)
Events flow UP    (Components -> Screen -> ViewModel)
```

### 3. State Hoisting (CRITICAL)

Every reusable composable must be **stateless**:

```kotlin
// ALWAYS: Stateless composable (testable, reusable, previewable)
@Composable
fun SearchBar(
    query: String,
    onQueryChange: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    OutlinedTextField(
        value = query,
        onValueChange = onQueryChange,
        modifier = modifier.fillMaxWidth(),
        placeholder = { Text("Search...") },
        leadingIcon = { Icon(Icons.Default.Search, null) },
        singleLine = true,
        shape = RoundedCornerShape(12.dp)
    )
}
```

## Composable Function Signature

Always follow this parameter order:

```kotlin
@Composable
fun MyComponent(
    // 1. Required data
    title: String,
    items: List<Item>,
    // 2. Optional data with defaults
    subtitle: String = "",
    isLoading: Boolean = false,
    // 3. Modifier (always with default)
    modifier: Modifier = Modifier,
    // 4. Event callbacks (last)
    onClick: () -> Unit = {},
    onItemClick: (Item) -> Unit = {}
)
```

## Screen Architecture Pattern

Every screen follows this structure:

```kotlin
@Composable
fun FeatureScreen(
    onNavigateBack: () -> Unit,
    viewModel: FeatureViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Scaffold(
        topBar = { /* TopAppBar */ }
    ) { padding ->
        when (val state = uiState) {
            is UiState.Loading -> LoadingScreen()
            is UiState.Empty -> EmptyScreen(onAction = { /* ... */ })
            is UiState.Error -> ErrorScreen(
                message = state.message,
                onRetry = viewModel::retry
            )
            is UiState.Success -> FeatureContent(
                data = state.data,
                onItemClick = viewModel::onItemClick,
                modifier = Modifier.padding(padding)
            )
        }
    }
}

// Content is ALWAYS a separate private composable
@Composable
private fun FeatureContent(
    data: List<Item>,
    onItemClick: (Item) -> Unit,
    modifier: Modifier = Modifier
) {
    LazyColumn(
        modifier = modifier,
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        items(items = data, key = { it.id }) { item ->
            ItemCard(item = item, onClick = { onItemClick(item) })
        }
    }
}
```

## Theming (Consistent Across Apps)

### Color Strategy

Use Material 3 dynamic color with brand fallbacks:

```kotlin
@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            if (darkTheme) dynamicDarkColorScheme(LocalContext.current)
            else dynamicLightColorScheme(LocalContext.current)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = AppTypography,
        content = content
    )
}
```

### Typography Hierarchy

```kotlin
// Use consistently across ALL screens:
MaterialTheme.typography.headlineLarge   // Screen titles
MaterialTheme.typography.titleLarge      // Section headers
MaterialTheme.typography.titleMedium     // Card titles
MaterialTheme.typography.bodyLarge       // Primary body text
MaterialTheme.typography.bodyMedium      // Secondary body text
MaterialTheme.typography.labelLarge      // Button text
MaterialTheme.typography.labelMedium     // Chips, tags, metadata
```

### Spacing System (Design Tokens)

```kotlin
object Spacing {
    val xs = 4.dp
    val sm = 8.dp
    val md = 16.dp
    val lg = 24.dp
    val xl = 32.dp
    val xxl = 48.dp
}
```

Use these exclusively. No arbitrary values like 13.dp or 19.dp.

## Essential UI Patterns

### Card Pattern (Standard across apps)

```kotlin
@Composable
fun StandardCard(
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
    content: @Composable ColumnScope.() -> Unit
) {
    Card(
        modifier = modifier.fillMaxWidth().then(
            if (onClick != null) Modifier.clickable(onClick = onClick)
            else Modifier
        ),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp),
        content = content
    )
}
```

### Loading / Error / Empty States

Every screen must handle all three. Use consistent components:

```kotlin
// Loading: centered progress indicator
@Composable
fun LoadingScreen(modifier: Modifier = Modifier) {
    Box(modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        CircularProgressIndicator()
    }
}

// Empty: icon + title + subtitle + optional action
@Composable
fun EmptyScreen(
    icon: ImageVector = Icons.Outlined.Inbox,
    title: String,
    subtitle: String,
    modifier: Modifier = Modifier,
    actionLabel: String? = null,
    onAction: (() -> Unit)? = null
)

// Error: icon + message + retry button
@Composable
fun ErrorScreen(
    message: String,
    modifier: Modifier = Modifier,
    onRetry: (() -> Unit)? = null
)
```

## Performance Essentials

### 1. Always use keys in lazy lists

```kotlin
items(items = list, key = { it.id }) { item -> ItemRow(item) }
```

### 2. Remember expensive computations

```kotlin
val filtered = remember(items, query) {
    items.filter { it.name.contains(query, ignoreCase = true) }
}
```

### 3. Use derivedStateOf for computed booleans

```kotlin
val showScrollToTop by remember {
    derivedStateOf { listState.firstVisibleItemIndex > 0 }
}
```

### 4. Never allocate in composition

```kotlin
// BAD: creates new lambda on every recomposition
Button(onClick = { viewModel.onClick(item) })

// GOOD: stable reference
val callback = remember(item) { { viewModel.onClick(item) } }
Button(onClick = callback)
```

## Animation Standards

Use subtle, purposeful animations:

```kotlin
// Content visibility transitions
AnimatedVisibility(
    visible = isVisible,
    enter = fadeIn() + expandVertically(),
    exit = fadeOut() + shrinkVertically()
)

// Smooth value changes
val elevation by animateDpAsState(
    targetValue = if (isPressed) 0.dp else 2.dp,
    animationSpec = tween(150)
)

// Crossfade between states
Crossfade(targetState = currentTab, label = "tab") { tab ->
    when (tab) {
        Tab.Home -> HomeContent()
        Tab.Profile -> ProfileContent()
    }
}
```

**Rules:** Keep animations under 300ms. Use `tween` for most cases. Never animate on first composition unless it's a staggered list.

## Patterns & Anti-Patterns

### DO

- Hoist all state out of reusable composables
- Use `Modifier` parameter with default on every composable
- Use MaterialTheme tokens for all colors, typography, shapes
- Provide `@Preview` for every public composable (light + dark)
- Use `key` parameter in all lazy lists
- Handle Loading, Error, Empty states on every screen
- Keep composables small and focused (one responsibility)
- Use `remember` for expensive computations

### DON'T

- Hardcode colors, dimensions, or font sizes
- Create ViewModels inside composables
- Put business logic in composables
- Use `mutableStateOf` without `remember`
- Use `Column`/`Row` for long scrollable lists (use `LazyColumn`/`LazyRow`)
- Skip the empty/error states ("I'll add them later")
- Use heavy animations that block the UI thread
- Nest scrollable containers (LazyColumn inside Column with scroll)

## Integration with Other Skills

```
feature-planning → Define screens, user stories, acceptance criteria
      |
android-development → Architecture (MVVM, Clean, Hilt)
      |
jetpack-compose-ui → Beautiful, consistent UI implementation (THIS SKILL)
      |
android-tdd → Test composables and ViewModels
```

**Key integrations:**
- **android-development**: Architecture, DI, design tokens (this skill builds on that foundation)
- **android-tdd**: Compose testing with `createComposeRule()`, `onNodeWithTag()`
- **feature-planning**: Screen specs become composable implementations

## References

- **Compose Samples**: github.com/android/compose-samples
- **Material 3 Design**: m3.material.io
- **Compose Documentation**: developer.android.com/jetpack/compose
- **Architecture Samples**: github.com/android/architecture-samples
