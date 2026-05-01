# Responsive & Adaptive Design

All apps MUST be responsive for both phones and tablets. Android 16+ makes adaptive UI mandatory.

**Core principle:** Don't think "phone vs. tablet." Think "how much space do I have?"

**Dependency:** Add Material 3 adaptive library:

```kotlin
implementation("androidx.compose.material3.adaptive:adaptive:1.2.0-alpha07")
```

## The 4-Step Responsive Playbook

Apply these steps to every composable — from a card to an entire screen.

### Step 1: Know Your Space (WindowSizeClass)

Calculate once at the top level, then pass down:

```kotlin
// MainActivity.kt
import androidx.compose.material3.adaptive.currentWindowAdaptiveInfo

override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    setContent {
        val windowSizeClass = currentWindowAdaptiveInfo().windowSizeClass
        AppTheme {
            AppNavigation(windowSizeClass = windowSizeClass)
        }
    }
}
```

### Step 2: Pass the Knowledge Down

Any composable that adapts its layout accepts `WindowSizeClass` as a parameter:

```kotlin
@Composable
fun ProfileCard(
    user: User,
    windowSizeClass: WindowSizeClass,
    modifier: Modifier = Modifier
) {
    // Layout adapts based on windowSizeClass
}
```

### Step 3: Adapt Layout with `when`

Use width breakpoints to switch between layouts:

```kotlin
@Composable
fun ProfileCard(
    user: User,
    windowSizeClass: WindowSizeClass,
    modifier: Modifier = Modifier
) {
    Card(modifier = modifier) {
        when {
            windowSizeClass.isWidthAtLeastBreakpoint(
                WindowSizeClass.WIDTH_DP_MEDIUM_LOWER_BOUND
            ) -> {
                // Medium/Expanded: side-by-side
                Row(
                    modifier = Modifier.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    ProfileImage(user.avatarUrl)
                    Spacer(Modifier.width(16.dp))
                    ProfileDetails(user)
                }
            }
            else -> {
                // Compact: stacked vertically
                Column(
                    modifier = Modifier.padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    ProfileImage(user.avatarUrl)
                    Spacer(Modifier.height(8.dp))
                    ProfileDetails(user)
                }
            }
        }
    }
}
```

### Step 4: Polish (Transitions & State)

**Smooth transitions with AnimatedContent:**

```kotlin
Card(modifier = modifier) {
    AnimatedContent(
        targetState = windowSizeClass,
        label = "profileCardAnimation"
    ) { targetSizeClass ->
        when {
            targetSizeClass.isWidthAtLeastBreakpoint(
                WindowSizeClass.WIDTH_DP_MEDIUM_LOWER_BOUND
            ) -> { /* Row layout */ }
            else -> { /* Column layout */ }
        }
    }
}
```

**Bulletproof state with rememberSaveable:**

```kotlin
// Survives configuration changes (rotation, window resize)
var isFollowed by rememberSaveable { mutableStateOf(false) }
```

## Window Size Breakpoints

| Width Class | Range | Typical Devices | Layout Strategy |
|-------------|-------|-----------------|-----------------|
| **Compact** | < 600dp | Phones (portrait) | Single column, bottom nav |
| **Medium** | 600-840dp | Tablets (portrait), foldables | Two-pane optional, nav rail |
| **Expanded** | > 840dp | Tablets (landscape), desktop | Two-pane, permanent nav drawer |

**Breakpoint API:**

```kotlin
// Check width breakpoints
windowSizeClass.isWidthAtLeastBreakpoint(WindowSizeClass.WIDTH_DP_MEDIUM_LOWER_BOUND)  // >= 600dp
windowSizeClass.isWidthAtLeastBreakpoint(WindowSizeClass.WIDTH_DP_EXPANDED_LOWER_BOUND) // >= 840dp

// Check height breakpoints
windowSizeClass.isHeightAtLeastBreakpoint(WindowSizeClass.HEIGHT_DP_MEDIUM_LOWER_BOUND)
```

## Adaptive Layout Patterns

### Content Width Constraint

Prevent overly wide content on large screens:

```kotlin
@Composable
fun AdaptiveContent(
    windowSizeClass: WindowSizeClass,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    val maxWidth = when {
        windowSizeClass.isWidthAtLeastBreakpoint(
            WindowSizeClass.WIDTH_DP_EXPANDED_LOWER_BOUND
        ) -> 840.dp
        windowSizeClass.isWidthAtLeastBreakpoint(
            WindowSizeClass.WIDTH_DP_MEDIUM_LOWER_BOUND
        ) -> 600.dp
        else -> Dp.Unspecified
    }

    Box(
        modifier = modifier.fillMaxSize(),
        contentAlignment = Alignment.TopCenter
    ) {
        Box(
            modifier = if (maxWidth != Dp.Unspecified) {
                Modifier.widthIn(max = maxWidth)
            } else Modifier.fillMaxWidth()
        ) {
            content()
        }
    }
}
```

### Adaptive Grid Columns

```kotlin
val columns = when {
    windowSizeClass.isWidthAtLeastBreakpoint(
        WindowSizeClass.WIDTH_DP_EXPANDED_LOWER_BOUND
    ) -> 3
    windowSizeClass.isWidthAtLeastBreakpoint(
        WindowSizeClass.WIDTH_DP_MEDIUM_LOWER_BOUND
    ) -> 2
    else -> 1
}

LazyVerticalGrid(
    columns = GridCells.Fixed(columns),
    contentPadding = PaddingValues(16.dp),
    horizontalArrangement = Arrangement.spacedBy(12.dp),
    verticalArrangement = Arrangement.spacedBy(12.dp)
) {
    items(items = data, key = { it.id }) { item ->
        ItemCard(item)
    }
}
```

### Adaptive Spacing

```kotlin
val screenPadding = when {
    windowSizeClass.isWidthAtLeastBreakpoint(
        WindowSizeClass.WIDTH_DP_EXPANDED_LOWER_BOUND
    ) -> 32.dp
    windowSizeClass.isWidthAtLeastBreakpoint(
        WindowSizeClass.WIDTH_DP_MEDIUM_LOWER_BOUND
    ) -> 24.dp
    else -> 16.dp
}
```

## Adaptive Navigation

Switch navigation component based on available width:

```kotlin
@Composable
fun AdaptiveAppNavigation(
    windowSizeClass: WindowSizeClass,
    currentRoute: String,
    onNavigate: (String) -> Unit,
    content: @Composable () -> Unit
) {
    when {
        windowSizeClass.isWidthAtLeastBreakpoint(
            WindowSizeClass.WIDTH_DP_EXPANDED_LOWER_BOUND
        ) -> {
            // Expanded: permanent drawer
            PermanentNavigationDrawer(
                drawerContent = {
                    PermanentDrawerSheet(Modifier.width(240.dp)) {
                        NavigationDrawerContent(currentRoute, onNavigate)
                    }
                },
                content = content
            )
        }
        windowSizeClass.isWidthAtLeastBreakpoint(
            WindowSizeClass.WIDTH_DP_MEDIUM_LOWER_BOUND
        ) -> {
            // Medium: navigation rail
            Row {
                NavigationRail {
                    navItems.forEach { item ->
                        NavigationRailItem(
                            selected = currentRoute == item.route,
                            onClick = { onNavigate(item.route) },
                            icon = { Icon(item.icon, item.label) },
                            label = { Text(item.label) }
                        )
                    }
                }
                Box(Modifier.weight(1f)) { content() }
            }
        }
        else -> {
            // Compact: bottom navigation bar
            Scaffold(
                bottomBar = {
                    NavigationBar {
                        navItems.forEach { item ->
                            NavigationBarItem(
                                selected = currentRoute == item.route,
                                onClick = { onNavigate(item.route) },
                                icon = { Icon(item.icon, item.label) },
                                label = { Text(item.label) }
                            )
                        }
                    }
                }
            ) { padding ->
                Box(Modifier.padding(padding)) { content() }
            }
        }
    }
}
```

## List-Detail Adaptive Pattern

The most common adaptive layout — list on one side, detail on the other:

```kotlin
@Composable
fun AdaptiveListDetailScreen(
    windowSizeClass: WindowSizeClass,
    viewModel: ListDetailViewModel = hiltViewModel(),
    navController: NavHostController = rememberNavController()
) {
    val items by viewModel.items.collectAsStateWithLifecycle()
    val selectedItem = viewModel.getItemById(viewModel.selectedItemId)

    when {
        windowSizeClass.isWidthAtLeastBreakpoint(
            WindowSizeClass.WIDTH_DP_MEDIUM_LOWER_BOUND
        ) -> {
            // Two-pane layout
            Row(modifier = Modifier.fillMaxSize()) {
                ItemList(
                    items = items,
                    onItemClick = { viewModel.selectItem(it) },
                    modifier = Modifier.weight(0.4f)
                )
                VerticalDivider()
                if (selectedItem != null) {
                    ItemDetail(
                        item = selectedItem,
                        onBack = { viewModel.selectItem(null) },
                        modifier = Modifier.weight(0.6f)
                    )
                    BackHandler { viewModel.selectItem(null) }
                } else {
                    EmptyDetailPlaceholder(Modifier.weight(0.6f))
                }
            }
        }
        else -> {
            // Single-pane with navigation
            NavHost(navController = navController, startDestination = "list") {
                composable("list") {
                    ItemList(
                        items = items,
                        onItemClick = { id ->
                            viewModel.selectItem(id)
                            navController.navigate("detail/$id")
                        }
                    )
                }
                composable("detail/{itemId}") { backStackEntry ->
                    val itemId = backStackEntry.arguments?.getString("itemId")
                    val item = viewModel.getItemById(itemId)
                    if (item != null) {
                        ItemDetail(
                            item = item,
                            onBack = {
                                viewModel.selectItem(null)
                                navController.popBackStack()
                            }
                        )
                    }
                }
            }
        }
    }
}
```

## Preview Configurations

Always preview at multiple sizes:

```kotlin
@Preview(name = "Phone", device = Devices.PHONE, showBackground = true)
@Preview(name = "Tablet", device = Devices.TABLET, showBackground = true)
@Preview(name = "Foldable", device = Devices.FOLDABLE, showBackground = true)
@Composable
private fun AdaptiveScreenPreview() {
    val windowSizeClass = currentWindowAdaptiveInfo().windowSizeClass
    AppTheme {
        MyScreen(windowSizeClass = windowSizeClass)
    }
}
```

## Adaptive Design Checklist

- [ ] Material 3 adaptive library added to dependencies
- [ ] `WindowSizeClass` calculated in `MainActivity` and passed down
- [ ] Screens adapt layout for compact/medium/expanded widths
- [ ] Navigation adapts: bottom bar (compact) / rail (medium) / drawer (expanded)
- [ ] List-detail screens show two-pane on medium+ screens
- [ ] `AnimatedContent` wraps layout transitions between size classes
- [ ] State uses `rememberSaveable` to survive configuration changes
- [ ] Grids use adaptive column counts
- [ ] Content width is constrained on expanded screens (no wall of whitespace)
- [ ] Previews include phone, tablet, and foldable device configurations

## Anti-Patterns

- **Hardcoding `isTablet()` booleans** - Use `WindowSizeClass` breakpoints instead
- **Ignoring medium screens** - Foldables and small tablets hit this breakpoint
- **Only adapting spacing** - Layouts should structurally change (Column → Row)
- **Forgetting BackHandler in two-pane** - Back should deselect, not exit app
- **Testing only on phone** - Always verify on tablet emulator before shipping
