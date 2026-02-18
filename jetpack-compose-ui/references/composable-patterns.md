# Composable Patterns: State, MVVM, and Screen Templates

## State Management Hierarchy

Choose the right state mechanism for each scope:

```
Scope            | Mechanism                | Survives Recomposition | Survives Config Change
-----------------|--------------------------|----------------------|----------------------
UI-only          | remember { }             | Yes                  | No
Config-safe      | rememberSaveable { }     | Yes                  | Yes
Screen-level     | ViewModel + StateFlow    | Yes                  | Yes
App-level        | Repository + DataStore   | Yes                  | Yes (persisted)
```

### Local UI State

```kotlin
// Transient state (expanded/collapsed, hover, focus)
var isExpanded by remember { mutableStateOf(false) }

// State that survives rotation
var searchQuery by rememberSaveable { mutableStateOf("") }
```

### Screen State (ViewModel)

```kotlin
class FeatureViewModel @Inject constructor(
    private val repository: Repository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    init { loadData() }

    fun loadData() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            repository.getData()
                .onSuccess { _uiState.value = UiState.Success(it) }
                .onFailure { _uiState.value = UiState.Error(it.message ?: "Unknown error") }
        }
    }

    fun retry() = loadData()
}

sealed interface UiState {
    data object Loading : UiState
    data class Success(val data: List<Item>) : UiState
    data class Error(val message: String) : UiState
}
```

## State Hoisting: The Complete Pattern

### Level 1: Simple Component

```kotlin
@Composable
fun QuantitySelector(
    quantity: Int,
    onQuantityChange: (Int) -> Unit,
    modifier: Modifier = Modifier,
    minValue: Int = 0,
    maxValue: Int = 99
) {
    Row(
        modifier = modifier,
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        IconButton(
            onClick = { onQuantityChange((quantity - 1).coerceAtLeast(minValue)) },
            enabled = quantity > minValue
        ) {
            Icon(painterResource(R.drawable.minus), "Decrease")
        }
        Text(
            text = quantity.toString(),
            style = MaterialTheme.typography.titleMedium,
            modifier = Modifier.widthIn(min = 32.dp),
            textAlign = TextAlign.Center
        )
        IconButton(
            onClick = { onQuantityChange((quantity + 1).coerceAtMost(maxValue)) },
            enabled = quantity < maxValue
        ) {
            Icon(painterResource(R.drawable.plus), "Increase")
        }
    }
}
```

### Level 2: Compound Component

```kotlin
@Composable
fun ProductCard(
    product: Product,
    quantity: Int,
    onQuantityChange: (Int) -> Unit,
    modifier: Modifier = Modifier,
    onAddToCart: () -> Unit = {}
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(product.name, style = MaterialTheme.typography.titleMedium)
            Spacer(Modifier.height(4.dp))
            Text(
                product.formattedPrice,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
            )
            Spacer(Modifier.height(12.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                QuantitySelector(
                    quantity = quantity,
                    onQuantityChange = onQuantityChange
                )
                Spacer(Modifier.weight(1f))
                Button(onClick = onAddToCart) {
                    Text("Add to Cart")
                }
            }
        }
    }
}
```

### Level 3: Screen with ViewModel

```kotlin
@Composable
fun ProductScreen(
    onNavigateBack: () -> Unit,
    viewModel: ProductViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val quantities by viewModel.quantities.collectAsStateWithLifecycle()

    ProductScreenContent(
        uiState = uiState,
        quantities = quantities,
        onQuantityChange = viewModel::updateQuantity,
        onAddToCart = viewModel::addToCart,
        onNavigateBack = onNavigateBack
    )
}
```

## Screen Templates

### List Screen Template

```kotlin
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ItemListScreen(
    onNavigateBack: () -> Unit,
    onItemClick: (String) -> Unit,
    viewModel: ItemListViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val searchQuery by viewModel.searchQuery.collectAsStateWithLifecycle()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Items") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(painterResource(R.drawable.back), "Back")
                    }
                }
            )
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = { /* create new */ },
                shape = RoundedCornerShape(16.dp)
            ) {
                Icon(painterResource(R.drawable.add), "Add item")
            }
        }
    ) { padding ->
        Column(modifier = Modifier.padding(padding)) {
            // Search bar
            OutlinedTextField(
                value = searchQuery,
                onValueChange = viewModel::onSearchQueryChange,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                placeholder = { Text("Search items...") },
                leadingIcon = { Icon(painterResource(R.drawable.search), null) },
                singleLine = true,
                shape = RoundedCornerShape(12.dp)
            )

            // Content
            when (val state = uiState) {
                is UiState.Loading -> LoadingScreen()
                is UiState.Empty -> EmptyScreen(
                    iconRes = R.drawable.inbox,
                    title = "No items yet",
                    subtitle = "Tap + to add your first item"
                )
                is UiState.Error -> ErrorScreen(
                    message = state.message,
                    onRetry = viewModel::retry
                )
                is UiState.Success -> {
                    LazyColumn(
                        contentPadding = PaddingValues(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        items(items = state.data, key = { it.id }) { item ->
                            ItemCard(
                                item = item,
                                onClick = { onItemClick(item.id) }
                            )
                        }
                    }
                }
            }
        }
    }
}
```

### Detail Screen Template

```kotlin
@Composable
fun ItemDetailScreen(
    itemId: String,
    onNavigateBack: () -> Unit,
    viewModel: ItemDetailViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    LaunchedEffect(itemId) { viewModel.loadItem(itemId) }

    // Error dialog — NEVER use Snackbar
    uiState.error?.let { errorMessage ->
        AppDialog(
            title = "Error",
            message = errorMessage,
            type = DialogType.ERROR,
            onDismiss = viewModel::clearError
        )
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Details") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(painterResource(R.drawable.back), "Back")
                    }
                },
                actions = {
                    IconButton(onClick = viewModel::onEditClick) {
                        Icon(painterResource(R.drawable.edit), "Edit")
                    }
                    IconButton(onClick = viewModel::onDeleteClick) {
                        Icon(painterResource(R.drawable.delete), "Delete")
                    }
                }
            )
        }
    ) { padding ->
        when (val state = uiState) {
            is UiState.Loading -> LoadingScreen()
            is UiState.Error -> ErrorScreen(state.message, onRetry = viewModel::retry)
            is UiState.Success -> {
                DetailContent(
                    item = state.data,
                    modifier = Modifier.padding(padding)
                )
            }
        }
    }
}
```

### Form Screen Template

```kotlin
@Composable
fun CreateItemScreen(
    onNavigateBack: () -> Unit,
    viewModel: CreateItemViewModel = hiltViewModel()
) {
    val formState by viewModel.formState.collectAsStateWithLifecycle()
    val isSaving by viewModel.isSaving.collectAsStateWithLifecycle()
    var showDiscardDialog by remember { mutableStateOf(false) }

    BackHandler(enabled = formState.hasChanges) { showDiscardDialog = true }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("New Item") },
                navigationIcon = {
                    IconButton(onClick = {
                        if (formState.hasChanges) showDiscardDialog = true
                        else onNavigateBack()
                    }) {
                        Icon(painterResource(R.drawable.cancel), "Cancel")
                    }
                },
                actions = {
                    TextButton(
                        onClick = viewModel::save,
                        enabled = formState.isValid && !isSaving
                    ) {
                        if (isSaving) CircularProgressIndicator(
                            Modifier.size(16.dp), strokeWidth = 2.dp
                        ) else Text("Save")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            OutlinedTextField(
                value = formState.name,
                onValueChange = viewModel::onNameChange,
                label = { Text("Name") },
                isError = formState.nameError != null,
                supportingText = formState.nameError?.let { { Text(it) } },
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp)
            )
            // ... more fields
        }
    }

    if (showDiscardDialog) {
        AlertDialog(
            onDismissRequest = { showDiscardDialog = false },
            title = { Text("Discard changes?") },
            text = { Text("You have unsaved changes.") },
            confirmButton = {
                TextButton(onClick = { showDiscardDialog = false; onNavigateBack() }) {
                    Text("Discard")
                }
            },
            dismissButton = {
                TextButton(onClick = { showDiscardDialog = false }) { Text("Keep editing") }
            }
        )
    }
}
```

## Error & Success Feedback: Dialogs over Snackbars

**RULE: Always use `AppDialog` for error/success/warning messages. Never use Snackbars for user-facing feedback.**

Snackbars are easily missed, auto-dismiss, and feel cheap. Dialogs (SweetAlert-style) are impossible to miss, force acknowledgment, and feel professional.

### AppDialog Component (reusable across all screens)

```kotlin
// Available types: ERROR, SUCCESS, WARNING, INFO
// Each has a distinct icon and color

// Error dialog (login failed, API error, validation)
uiState.error?.let { errorMessage ->
    AppDialog(
        title = "Login Failed",
        message = errorMessage,
        type = DialogType.ERROR,
        onDismiss = viewModel::clearError
    )
}

// Success dialog (created, saved, updated)
if (uiState.saveSuccess) {
    AppDialog(
        title = "Success",
        message = "Client created successfully",
        type = DialogType.SUCCESS,
        onDismiss = {
            viewModel.clearSaveState()
            onBack()
        }
    )
}
```

### When to use what:
| Scenario | Component |
|---|---|
| API errors, login failures | `AppDialog(type = ERROR)` |
| Create/update/delete success | `AppDialog(type = SUCCESS)` |
| Destructive action confirmation | `AppDialog(type = WARNING)` |
| Full-screen load failure with retry | `ErrorState` composable |
| **NEVER use for errors/success** | ~~Snackbar~~ |

### Pattern: Dialog-driven error in screens

```kotlin
@Composable
fun FeatureScreen(viewModel: FeatureViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsState()

    // Error dialog — replaces LaunchedEffect + snackbar pattern
    uiState.error?.let { errorMessage ->
        AppDialog(
            title = "Error",
            message = errorMessage,
            type = DialogType.ERROR,
            onDismiss = viewModel::clearError
        )
    }

    Scaffold { padding ->
        // No snackbarHost needed
        Content(modifier = Modifier.padding(padding))
    }
}
```

## Preview Best Practices

```kotlin
// Always preview light AND dark
@Preview(name = "Light", showBackground = true)
@Preview(name = "Dark", showBackground = true, uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
private fun ItemCardPreview() {
    AppTheme {
        ItemCard(
            item = Item.preview(),
            onClick = {}
        )
    }
}

// Create .preview() factory for easy test data
data class Item(val id: String, val name: String, val description: String) {
    companion object {
        fun preview() = Item("1", "Sample Item", "A description for preview")
    }
}
```
