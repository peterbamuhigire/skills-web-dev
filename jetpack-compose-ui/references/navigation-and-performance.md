# Navigation & Performance

## Navigation Setup

### Define Routes

```kotlin
sealed class Screen(val route: String) {
    data object Home : Screen("home")
    data object Search : Screen("search")
    data object Profile : Screen("profile")
    data object Settings : Screen("settings")

    // Screens with arguments
    data object ItemDetail : Screen("item/{itemId}") {
        fun createRoute(itemId: String) = "item/$itemId"
    }
    data object EditItem : Screen("item/{itemId}/edit") {
        fun createRoute(itemId: String) = "item/$itemId/edit"
    }
}
```

### Navigation Host

```kotlin
@Composable
fun AppNavigation(
    navController: NavHostController = rememberNavController()
) {
    NavHost(
        navController = navController,
        startDestination = Screen.Home.route,
        enterTransition = { fadeIn(tween(200)) + slideInHorizontally { it / 4 } },
        exitTransition = { fadeOut(tween(150)) },
        popEnterTransition = { fadeIn(tween(200)) + slideInHorizontally { -it / 4 } },
        popExitTransition = { fadeOut(tween(150)) }
    ) {
        // Bottom nav destinations
        composable(Screen.Home.route) {
            HomeScreen(
                onItemClick = { id ->
                    navController.navigate(Screen.ItemDetail.createRoute(id))
                }
            )
        }

        composable(Screen.Search.route) {
            SearchScreen(
                onResultClick = { id ->
                    navController.navigate(Screen.ItemDetail.createRoute(id))
                }
            )
        }

        composable(Screen.Profile.route) {
            ProfileScreen(
                onSettingsClick = { navController.navigate(Screen.Settings.route) }
            )
        }

        // Detail screens
        composable(
            route = Screen.ItemDetail.route,
            arguments = listOf(navArgument("itemId") { type = NavType.StringType })
        ) {
            ItemDetailScreen(
                onNavigateBack = { navController.popBackStack() },
                onEditClick = { id ->
                    navController.navigate(Screen.EditItem.createRoute(id))
                }
            )
        }

        composable(
            route = Screen.EditItem.route,
            arguments = listOf(navArgument("itemId") { type = NavType.StringType })
        ) {
            EditItemScreen(
                onNavigateBack = { navController.popBackStack() }
            )
        }
    }
}
```

### Main Activity with Bottom Nav

```kotlin
@Composable
fun MainScreen() {
    val navController = rememberNavController()
    val currentBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = currentBackStackEntry?.destination?.route

    // Only show bottom nav on main screens
    val showBottomBar = currentRoute in listOf(
        Screen.Home.route,
        Screen.Search.route,
        Screen.Profile.route
    )

    Scaffold(
        bottomBar = {
            if (showBottomBar) {
                NavigationBar {
                    bottomNavItems.forEach { item ->
                        NavigationBarItem(
                            selected = currentRoute == item.route,
                            onClick = {
                                navController.navigate(item.route) {
                                    popUpTo(navController.graph.findStartDestination().id) {
                                        saveState = true
                                    }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            },
                            icon = {
                                Icon(
                                    if (currentRoute == item.route) item.selectedIcon
                                    else item.unselectedIcon,
                                    contentDescription = item.label
                                )
                            },
                            label = { Text(item.label) }
                        )
                    }
                }
            }
        }
    ) { padding ->
        Box(modifier = Modifier.padding(padding)) {
            AppNavigation(navController)
        }
    }
}

val bottomNavItems = listOf(
    BottomNavItem(Screen.Home.route, "Home", Icons.Filled.Home, Icons.Outlined.Home),
    BottomNavItem(Screen.Search.route, "Search", Icons.Filled.Search, Icons.Outlined.Search),
    BottomNavItem(Screen.Profile.route, "Profile", Icons.Filled.Person, Icons.Outlined.Person)
)
```

### Navigation Best Practices

- Pass only IDs as arguments, not objects
- Use `popUpTo` with `saveState` for bottom nav
- Use `launchSingleTop = true` to avoid duplicate screens
- Screen composables receive navigation callbacks, never `NavController`
- ViewModel gets IDs from `SavedStateHandle`, not composable arguments

```kotlin
@HiltViewModel
class ItemDetailViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle,
    private val repository: Repository
) : ViewModel() {
    private val itemId: String = checkNotNull(savedStateHandle["itemId"])
    // Load data using itemId
}
```

## Performance Optimization

### 1. Stability and Recomposition

Compose skips recomposition when inputs haven't changed. Ensure stability:

```kotlin
// STABLE: data class with immutable properties
data class Item(
    val id: String,
    val name: String,
    val price: Double
)

// UNSTABLE: mutable properties cause unnecessary recomposition
data class BadItem(
    val id: String,
    var name: String,  // var = unstable
    val tags: MutableList<String>  // MutableList = unstable
)

// Fix unstable types with @Immutable or @Stable
@Immutable
data class ItemList(
    val items: List<Item>  // List (not MutableList) is stable
)
```

### 2. Remember Expensive Operations

```kotlin
@Composable
fun FilteredList(items: List<Item>, query: String) {
    // Only recomputes when items or query changes
    val filtered = remember(items, query) {
        items.filter { it.name.contains(query, ignoreCase = true) }
    }

    // Only recomputes when filtered list changes
    val sortedFiltered = remember(filtered) {
        filtered.sortedBy { it.name }
    }

    LazyColumn {
        items(items = sortedFiltered, key = { it.id }) { item ->
            ItemRow(item)
        }
    }
}
```

### 3. derivedStateOf for Computed Booleans

```kotlin
@Composable
fun SmartScrollContent(items: List<Item>) {
    val listState = rememberLazyListState()

    // Only triggers recomposition when the boolean CHANGES
    val showScrollToTop by remember {
        derivedStateOf { listState.firstVisibleItemIndex > 2 }
    }

    val showHeader by remember {
        derivedStateOf { listState.firstVisibleItemScrollOffset < 10 }
    }

    Box {
        LazyColumn(state = listState) {
            items(items = items, key = { it.id }) { item ->
                ItemRow(item)
            }
        }

        AnimatedVisibility(
            visible = showScrollToTop,
            modifier = Modifier.align(Alignment.BottomEnd).padding(16.dp)
        ) {
            FloatingActionButton(
                onClick = {
                    // Scroll to top
                }
            ) {
                Icon(Icons.Default.KeyboardArrowUp, "Scroll to top")
            }
        }
    }
}
```

### 4. Lazy List Optimization

```kotlin
LazyColumn(
    // Content padding instead of wrapping padding
    contentPadding = PaddingValues(16.dp),
    // Consistent spacing between items
    verticalArrangement = Arrangement.spacedBy(12.dp)
) {
    items(
        items = items,
        key = { it.id },             // ALWAYS provide keys
        contentType = { it.type }     // Helps compose reuse compositions
    ) { item ->
        // Use stable composable references
        when (item.type) {
            ItemType.HEADER -> HeaderItem(item)
            ItemType.CONTENT -> ContentItem(item)
        }
    }
}
```

### 5. Image Loading

```kotlin
// Use Coil for async image loading
AsyncImage(
    model = ImageRequest.Builder(LocalContext.current)
        .data(imageUrl)
        .crossfade(200)
        .memoryCacheKey(imageUrl) // Cache key for recomposition
        .build(),
    contentDescription = description,
    modifier = Modifier
        .size(64.dp)
        .clip(RoundedCornerShape(12.dp)),
    contentScale = ContentScale.Crop,
    placeholder = painterResource(R.drawable.placeholder),
    error = painterResource(R.drawable.error_image)
)
```

### 6. Avoid Common Performance Traps

```kotlin
// BAD: New lambda on every recomposition
items(items) { item ->
    ItemRow(onClick = { viewModel.onItemClick(item.id) })
}

// GOOD: Stable callback reference
items(items) { item ->
    val onClick = remember(item.id) { { viewModel.onItemClick(item.id) } }
    ItemRow(onClick = onClick)
}

// BAD: Reading state unnecessarily wide
@Composable
fun ParentScreen(viewModel: ViewModel) {
    val allState by viewModel.uiState.collectAsStateWithLifecycle()
    // allState changes recompose EVERYTHING below
    ChildA(allState.fieldA)
    ChildB(allState.fieldB)
}

// GOOD: Read state at the lowest level possible
@Composable
fun ParentScreen(viewModel: ViewModel) {
    ChildA(viewModel)  // Each child reads only what it needs
    ChildB(viewModel)
}

// BAD: Allocating inside composition
@Composable
fun BadModifier() {
    val shape = RoundedCornerShape(16.dp) // Creates new object every recomposition
    Card(shape = shape) { }
}

// GOOD: Remember or use constants
private val CardShape = RoundedCornerShape(16.dp)

@Composable
fun GoodModifier() {
    Card(shape = CardShape) { }
}
```

### 7. Pagination

```kotlin
@Composable
fun PaginatedList(
    items: List<Item>,
    isLoadingMore: Boolean,
    hasMore: Boolean,
    onLoadMore: () -> Unit,
    modifier: Modifier = Modifier
) {
    val listState = rememberLazyListState()

    // Trigger load when approaching end
    val shouldLoadMore by remember {
        derivedStateOf {
            val lastVisibleItem = listState.layoutInfo.visibleItemsInfo.lastOrNull()?.index ?: 0
            val totalItems = listState.layoutInfo.totalItemsCount
            hasMore && !isLoadingMore && lastVisibleItem >= totalItems - 3
        }
    }

    LaunchedEffect(shouldLoadMore) {
        if (shouldLoadMore) onLoadMore()
    }

    LazyColumn(
        state = listState,
        modifier = modifier,
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        items(items = items, key = { it.id }) { item ->
            ItemCard(item)
        }

        if (isLoadingMore) {
            item {
                Box(
                    Modifier.fillMaxWidth().padding(16.dp),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator(Modifier.size(24.dp))
                }
            }
        }
    }
}
```

## Performance Checklist

- [ ] All lazy list items have stable `key` parameters
- [ ] Expensive computations wrapped in `remember(dependencies)`
- [ ] Boolean state derived from scroll/list uses `derivedStateOf`
- [ ] Data classes use `val` (not `var`) and immutable collections
- [ ] Images use Coil `AsyncImage` with cache keys
- [ ] Lambdas in loops use `remember` for stability
- [ ] Shapes, colors, and other objects defined as constants outside composables
- [ ] State is read at the lowest possible level in the tree
- [ ] `contentType` provided for heterogeneous lists
- [ ] Pagination loads before user reaches the end
