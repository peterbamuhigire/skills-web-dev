# Screen Implementation Patterns

Complete screen templates with state management, error handling, and lifecycle awareness.

## Local Development Networking (WAMP)

- On local Windows/Ubuntu dev machines, the Android emulator must reach the backend via the host machine's static LAN IP, not `localhost`.
- Ensure firewall rules allow inbound access to the WAMP HTTP port.

**References:** See [Compose Samples](https://github.com/android/compose-samples) for real screen implementations and [Architecture Samples](https://github.com/android/architecture-samples) for MVVM screen patterns with Repository integration.

## Standard Screen Template

Every screen should include:

1. State management with ViewModel
2. Error handling with retry
3. Loading states
4. Empty states
5. Pull-to-refresh
6. Side effect handling

```kotlin
@Composable
fun UserProfileScreen(
    userId: String,
    onNavigateBack: () -> Unit,
    onEditProfile: () -> Unit,
    modifier: Modifier = Modifier,
    viewModel: UserProfileViewModel = hiltViewModel()
) {
    // Collect UI state (lifecycle-aware)
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    // Initial data load
    LaunchedEffect(userId) {
        viewModel.loadUserProfile(userId)
    }

    // Error dialog — ALWAYS use AppDialog, NEVER Snackbar for errors/success
    uiState.error?.let { errorMessage ->
        AppDialog(
            title = "Error",
            message = errorMessage,
            type = DialogType.ERROR,
            onDismiss = viewModel::clearError
        )
    }

    // Screen structure — no snackbarHost needed
    Scaffold(
        topBar = {
            StandardTopBar(
                title = "Profile",
                onNavigationClick = onNavigateBack,
                actions = {
                    IconButton(onClick = onEditProfile) {
                        Icon(painterResource(R.drawable.edit), contentDescription = "Edit")
                    }
                }
            )
        }
    ) { paddingValues ->
        UserProfileContent(
            uiState = uiState,
            onRefresh = viewModel::refreshProfile,
            modifier = modifier.padding(paddingValues)
        )
    }
}
```

## Content with Pull-to-Refresh

```kotlin
@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun UserProfileContent(
    uiState: UserProfileUiState,
    onRefresh: () -> Unit,
    modifier: Modifier = Modifier
) {
    val pullRefreshState = rememberPullToRefreshState()

    PullToRefreshBox(
        isRefreshing = uiState.isRefreshing,
        onRefresh = onRefresh,
        state = pullRefreshState,
        modifier = modifier.fillMaxSize()
    ) {
        when {
            uiState.isLoading && uiState.user == null -> {
                LoadingIndicator()
            }
            uiState.isEmpty -> {
                EmptyState(
                    title = "No Profile Data",
                    message = "Complete your profile to get started",
                    actionText = "Complete Profile",
                    onAction = { /* navigate */ }
                )
            }
            uiState.user != null -> {
                LazyColumn(
                    verticalArrangement = Arrangement.spacedBy(DesignSystem.Spacing.md),
                    contentPadding = PaddingValues(DesignSystem.Spacing.md)
                ) {
                    item { UserHeaderCard(uiState.user) }
                    item { StatsSection(uiState.stats) }

                    if (uiState.recentActivity.isNotEmpty()) {
                        item {
                            Text(
                                "Recent Activity",
                                style = MaterialTheme.typography.titleMedium
                            )
                        }
                        items(
                            items = uiState.recentActivity,
                            key = { it.id }
                        ) { activity ->
                            ActivityItem(activity)
                        }
                    }
                }
            }
        }
    }
}
```

## List Screen Pattern

```kotlin
@Composable
fun OrderListScreen(
    onNavigateBack: () -> Unit,
    onOrderClick: (String) -> Unit,
    modifier: Modifier = Modifier,
    viewModel: OrderListViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val searchQuery by viewModel.searchQuery.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            SearchableTopBar(
                title = "Orders",
                searchQuery = searchQuery,
                onSearchQueryChange = viewModel::onSearchQueryChange,
                onNavigationClick = onNavigateBack
            )
        },
        floatingActionButton = {
            FloatingActionButton(onClick = { /* create new */ }) {
                Icon(painterResource(R.drawable.add), contentDescription = "New Order")
            }
        }
    ) { paddingValues ->
        OrderListContent(
            uiState = uiState,
            onOrderClick = onOrderClick,
            onRefresh = viewModel::refresh,
            onLoadMore = viewModel::loadNextPage,
            modifier = modifier.padding(paddingValues)
        )
    }
}

@Composable
private fun OrderListContent(
    uiState: OrderListUiState,
    onOrderClick: (String) -> Unit,
    onRefresh: () -> Unit,
    onLoadMore: () -> Unit,
    modifier: Modifier = Modifier
) {
    when {
        uiState.isLoading && uiState.orders.isEmpty() -> LoadingIndicator()
        uiState.orders.isEmpty() -> EmptyState(
            title = "No Orders",
            message = "You haven't placed any orders yet"
        )
        else -> {
            LazyColumn(
                modifier = modifier.fillMaxSize(),
                contentPadding = PaddingValues(DesignSystem.Spacing.md),
                verticalArrangement = Arrangement.spacedBy(DesignSystem.Spacing.sm)
            ) {
                items(
                    items = uiState.orders,
                    key = { it.id }
                ) { order ->
                    OrderCard(
                        order = order,
                        onClick = { onOrderClick(order.id) }
                    )
                }

                // Pagination loading
                if (uiState.hasMore) {
                    item {
                        LaunchedEffect(Unit) { onLoadMore() }
                        Box(
                            modifier = Modifier.fillMaxWidth().padding(DesignSystem.Spacing.md),
                            contentAlignment = Alignment.Center
                        ) {
                            CircularProgressIndicator(modifier = Modifier.size(24.dp))
                        }
                    }
                }
            }
        }
    }
}
```

## Form Screen Pattern

```kotlin
@Composable
fun EditProfileScreen(
    onNavigateBack: () -> Unit,
    modifier: Modifier = Modifier,
    viewModel: EditProfileViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val formState by viewModel.formState.collectAsStateWithLifecycle()

    // Confirm discard on back press with unsaved changes
    var showDiscardDialog by remember { mutableStateOf(false) }
    BackHandler(enabled = formState.hasChanges) {
        showDiscardDialog = true
    }

    Scaffold(
        topBar = {
            StandardTopBar(
                title = "Edit Profile",
                onNavigationClick = {
                    if (formState.hasChanges) showDiscardDialog = true
                    else onNavigateBack()
                },
                actions = {
                    TextButton(
                        onClick = viewModel::save,
                        enabled = formState.isValid && !uiState.isSaving
                    ) {
                        if (uiState.isSaving) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(16.dp),
                                strokeWidth = 2.dp
                            )
                        } else {
                            Text("Save")
                        }
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = modifier
                .padding(paddingValues)
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(DesignSystem.Spacing.md),
            verticalArrangement = Arrangement.spacedBy(DesignSystem.Spacing.md)
        ) {
            OutlinedTextField(
                value = formState.name,
                onValueChange = viewModel::onNameChange,
                label = { Text("Name") },
                isError = formState.nameError != null,
                supportingText = formState.nameError?.let { { Text(it) } },
                modifier = Modifier.fillMaxWidth()
            )

            OutlinedTextField(
                value = formState.email,
                onValueChange = viewModel::onEmailChange,
                label = { Text("Email") },
                isError = formState.emailError != null,
                supportingText = formState.emailError?.let { { Text(it) } },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
                modifier = Modifier.fillMaxWidth()
            )

            OutlinedTextField(
                value = formState.phone,
                onValueChange = viewModel::onPhoneChange,
                label = { Text("Phone") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
                modifier = Modifier.fillMaxWidth()
            )
        }
    }

    if (showDiscardDialog) {
        AlertDialog(
            onDismissRequest = { showDiscardDialog = false },
            title = { Text("Discard Changes?") },
            text = { Text("You have unsaved changes. Are you sure you want to leave?") },
            confirmButton = {
                TextButton(onClick = { showDiscardDialog = false; onNavigateBack() }) {
                    Text("Discard")
                }
            },
            dismissButton = {
                TextButton(onClick = { showDiscardDialog = false }) {
                    Text("Keep Editing")
                }
            }
        )
    }
}
```

## Adaptive List-Detail Pattern

The standard approach for list screens that need a detail view on tablets. Two-pane on medium/expanded, single-pane navigation on compact.

```kotlin
@Composable
fun AdaptiveItemListScreen(
    windowSizeClass: WindowSizeClass,
    onNavigateBack: () -> Unit,
    viewModel: ItemListViewModel = hiltViewModel(),
    navController: NavHostController = rememberNavController()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val selectedItem = viewModel.getItemById(viewModel.selectedItemId)

    Scaffold(
        topBar = {
            StandardTopBar(title = "Items", onNavigationClick = onNavigateBack)
        }
    ) { padding ->
        when {
            windowSizeClass.isWidthAtLeastBreakpoint(
                WindowSizeClass.WIDTH_DP_MEDIUM_LOWER_BOUND
            ) -> {
                // Two-pane: list + detail side by side
                Row(modifier = Modifier.padding(padding).fillMaxSize()) {
                    ItemListContent(
                        uiState = uiState,
                        onItemClick = { viewModel.selectItem(it) },
                        modifier = Modifier.weight(0.4f)
                    )
                    VerticalDivider()
                    if (selectedItem != null) {
                        ItemDetailContent(
                            item = selectedItem,
                            modifier = Modifier.weight(0.6f)
                        )
                        BackHandler { viewModel.selectItem(null) }
                    } else {
                        Box(
                            modifier = Modifier.weight(0.6f).fillMaxHeight(),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                "Select an item to view details",
                                style = MaterialTheme.typography.bodyLarge,
                                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                            )
                        }
                    }
                }
            }
            else -> {
                // Single-pane: navigate between list and detail
                NavHost(
                    navController = navController,
                    startDestination = "list",
                    modifier = Modifier.padding(padding)
                ) {
                    composable("list") {
                        ItemListContent(
                            uiState = uiState,
                            onItemClick = { id ->
                                viewModel.selectItem(id)
                                navController.navigate("detail/$id")
                            }
                        )
                    }
                    composable(
                        "detail/{itemId}",
                        arguments = listOf(navArgument("itemId") { type = NavType.StringType })
                    ) { backStackEntry ->
                        val itemId = backStackEntry.arguments?.getString("itemId")
                        val item = viewModel.getItemById(itemId)
                        if (item != null) {
                            ItemDetailContent(
                                item = item,
                                showBackButton = true,
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
}
```

**Key rules for adaptive list-detail:**

- ViewModel holds selection state (not the composable)
- `BackHandler` in two-pane clears selection instead of exiting
- Detail pane shows placeholder when nothing is selected
- Use `VerticalDivider()` between panes for visual separation
- Weight ratio 0.4/0.6 is the standard starting point

## Screen Pattern Rules

1. **Screen composable** owns Scaffold, receives navigation callbacks
2. **Content composable** is private, receives uiState, handles display only
3. **ViewModel** manages state and business logic, never UI elements
4. **Error/success feedback** via `AppDialog` (DialogType.ERROR/SUCCESS/WARNING/INFO) — NEVER Snackbar
5. **Back handler** for unsaved changes in form screens
6. **Pull-to-refresh** for data-display screens
7. **Pagination** via `LaunchedEffect` at list bottom
8. **Keys** always provided in `LazyColumn` items
9. **Adaptive layouts** — screens with list+detail must use two-pane on tablets
10. **WindowSizeClass** passed to screens that adapt their layout
