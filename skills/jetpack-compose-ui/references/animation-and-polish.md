# Animation & Visual Polish

## Animation Philosophy

Animations should be **subtle, purposeful, and fast**. They communicate state changes, guide attention, and make the app feel alive - never slow it down.

### Rules

1. **Under 300ms** for all micro-interactions
2. **Under 500ms** for screen transitions
3. **Purpose-driven** - every animation communicates something
4. **No animation on first composition** unless it's a staggered list entrance
5. **Respect user preferences** - check `LocalReducedMotion`

## Content Visibility

### AnimatedVisibility (Show/Hide)

```kotlin
AnimatedVisibility(
    visible = isVisible,
    enter = fadeIn(animationSpec = tween(200)) +
            expandVertically(animationSpec = tween(200)),
    exit = fadeOut(animationSpec = tween(150)) +
           shrinkVertically(animationSpec = tween(150))
) {
    Card {
        Text("Expandable content")
    }
}
```

### Crossfade (Swap Content)

```kotlin
Crossfade(
    targetState = selectedTab,
    animationSpec = tween(200),
    label = "tab-crossfade"
) { tab ->
    when (tab) {
        Tab.Home -> HomeContent()
        Tab.Search -> SearchContent()
        Tab.Profile -> ProfileContent()
    }
}
```

### AnimatedContent (Complex Transitions)

```kotlin
AnimatedContent(
    targetState = uiState,
    transitionSpec = {
        fadeIn(tween(200)) togetherWith fadeOut(tween(150))
    },
    label = "state-transition"
) { state ->
    when (state) {
        is UiState.Loading -> LoadingScreen()
        is UiState.Success -> SuccessContent(state.data)
        is UiState.Error -> ErrorScreen(state.message)
    }
}
```

## Value Animations

### Animated Dp (Size, Padding, Elevation)

```kotlin
val elevation by animateDpAsState(
    targetValue = if (isSelected) 4.dp else 1.dp,
    animationSpec = tween(200),
    label = "card-elevation"
)

val cornerRadius by animateDpAsState(
    targetValue = if (isExpanded) 8.dp else 16.dp,
    animationSpec = tween(250),
    label = "corner-radius"
)

Card(
    elevation = CardDefaults.cardElevation(defaultElevation = elevation),
    shape = RoundedCornerShape(cornerRadius)
) { /* content */ }
```

### Animated Color

```kotlin
val backgroundColor by animateColorAsState(
    targetValue = if (isSelected)
        MaterialTheme.colorScheme.primaryContainer
    else
        MaterialTheme.colorScheme.surface,
    animationSpec = tween(200),
    label = "bg-color"
)

Surface(color = backgroundColor) { /* content */ }
```

### Animated Float (Alpha, Scale)

```kotlin
val alpha by animateFloatAsState(
    targetValue = if (isEnabled) 1f else 0.4f,
    animationSpec = tween(150),
    label = "alpha"
)

Box(modifier = Modifier.graphicsLayer { this.alpha = alpha }) {
    // Content with animated opacity
}
```

## Loading States

### Shimmer/Skeleton Loading

```kotlin
@Composable
fun ShimmerEffect(modifier: Modifier = Modifier) {
    val shimmerColors = listOf(
        MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.6f),
        MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.2f),
        MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.6f)
    )

    val transition = rememberInfiniteTransition(label = "shimmer")
    val translateAnimation = transition.animateFloat(
        initialValue = 0f,
        targetValue = 1000f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 1200, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "shimmer-translate"
    )

    val brush = Brush.linearGradient(
        colors = shimmerColors,
        start = Offset(translateAnimation.value - 200f, 0f),
        end = Offset(translateAnimation.value, 0f)
    )

    Box(modifier = modifier.background(brush, shape = RoundedCornerShape(8.dp)))
}

// Skeleton card matching your real card layout
@Composable
fun SkeletonCard(modifier: Modifier = Modifier) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            ShimmerEffect(Modifier.fillMaxWidth(0.6f).height(20.dp))
            Spacer(Modifier.height(8.dp))
            ShimmerEffect(Modifier.fillMaxWidth(0.9f).height(14.dp))
            Spacer(Modifier.height(4.dp))
            ShimmerEffect(Modifier.fillMaxWidth(0.4f).height(14.dp))
        }
    }
}

// Loading screen with skeletons
@Composable
fun SkeletonListLoading(modifier: Modifier = Modifier, count: Int = 5) {
    LazyColumn(
        modifier = modifier,
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        items(count) { SkeletonCard() }
    }
}
```

### Pull-to-Refresh

```kotlin
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RefreshableContent(
    isRefreshing: Boolean,
    onRefresh: () -> Unit,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    PullToRefreshBox(
        isRefreshing = isRefreshing,
        onRefresh = onRefresh,
        modifier = modifier
    ) {
        content()
    }
}
```

## Micro-Interactions

### Button Press Effect

```kotlin
@Composable
fun PressableCard(
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    content: @Composable ColumnScope.() -> Unit
) {
    val interactionSource = remember { MutableInteractionSource() }
    val isPressed by interactionSource.collectIsPressedAsState()

    val scale by animateFloatAsState(
        targetValue = if (isPressed) 0.97f else 1f,
        animationSpec = tween(100),
        label = "press-scale"
    )

    Card(
        modifier = modifier
            .graphicsLayer { scaleX = scale; scaleY = scale }
            .clickable(
                interactionSource = interactionSource,
                indication = LocalIndication.current,
                onClick = onClick
            ),
        shape = RoundedCornerShape(16.dp),
        content = content
    )
}
```

### Counter Animation

```kotlin
@Composable
fun AnimatedCounter(
    count: Int,
    modifier: Modifier = Modifier,
    style: TextStyle = MaterialTheme.typography.titleLarge
) {
    AnimatedContent(
        targetState = count,
        transitionSpec = {
            if (targetState > initialState) {
                slideInVertically { -it } + fadeIn() togetherWith
                    slideOutVertically { it } + fadeOut()
            } else {
                slideInVertically { it } + fadeIn() togetherWith
                    slideOutVertically { -it } + fadeOut()
            }.using(SizeTransform(clip = false))
        },
        label = "counter"
    ) { target ->
        Text(text = "$target", style = style, modifier = modifier)
    }
}
```

### Success Checkmark

```kotlin
@Composable
fun SuccessAnimation(modifier: Modifier = Modifier) {
    val scale = remember { Animatable(0f) }

    LaunchedEffect(Unit) {
        scale.animateTo(
            targetValue = 1f,
            animationSpec = spring(
                dampingRatio = Spring.DampingRatioMediumBouncy,
                stiffness = Spring.StiffnessLow
            )
        )
    }

    Box(
        modifier = modifier
            .size(64.dp)
            .graphicsLayer { scaleX = scale.value; scaleY = scale.value }
            .background(
                MaterialTheme.colorScheme.primaryContainer,
                CircleShape
            ),
        contentAlignment = Alignment.Center
    ) {
        Icon(
            painterResource(R.drawable.check),
            contentDescription = "Success",
            tint = MaterialTheme.colorScheme.onPrimaryContainer,
            modifier = Modifier.size(32.dp)
        )
    }
}
```

## Staggered List Entrance

```kotlin
@Composable
fun StaggeredListItem(
    index: Int,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    val alpha = remember { Animatable(0f) }
    val offsetY = remember { Animatable(20f) }

    LaunchedEffect(Unit) {
        delay(index * 50L) // Stagger delay
        launch { alpha.animateTo(1f, tween(200)) }
        launch { offsetY.animateTo(0f, tween(200)) }
    }

    Box(
        modifier = modifier.graphicsLayer {
            this.alpha = alpha.value
            translationY = offsetY.value
        }
    ) {
        content()
    }
}
```

## Transition Between Screens

### Shared Element-like Transition

```kotlin
// Use Compose Navigation with animated transitions
NavHost(
    navController = navController,
    startDestination = "list",
    enterTransition = { fadeIn(tween(300)) + slideInHorizontally { it / 4 } },
    exitTransition = { fadeOut(tween(200)) },
    popEnterTransition = { fadeIn(tween(300)) + slideInHorizontally { -it / 4 } },
    popExitTransition = { fadeOut(tween(200)) }
) {
    composable("list") { ListScreen() }
    composable("detail/{id}") { DetailScreen() }
}
```

## Snackbar with Action

```kotlin
@Composable
fun UndoSnackbar(
    snackbarHostState: SnackbarHostState,
    onUndo: () -> Unit
) {
    LaunchedEffect(Unit) {
        val result = snackbarHostState.showSnackbar(
            message = "Item deleted",
            actionLabel = "Undo",
            duration = SnackbarDuration.Short
        )
        if (result == SnackbarResult.ActionPerformed) {
            onUndo()
        }
    }
}
```

## Polish Checklist

- [ ] Loading states use skeleton/shimmer (not just a spinner)
- [ ] State changes animate smoothly (no jarring jumps)
- [ ] Button presses give immediate visual feedback
- [ ] Lists use `animateItemPlacement()` for reorder
- [ ] Screen transitions feel connected (slide + fade)
- [ ] Counters/numbers animate when changing
- [ ] Pull-to-refresh on all data screens
- [ ] Success actions show brief confirmation animation
- [ ] Errors animate in (don't just appear)
- [ ] All animations respect reduced motion preferences
