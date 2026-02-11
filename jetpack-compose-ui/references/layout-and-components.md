# Layouts, Modifiers & Material Components

## Layout Composables

### Column (Vertical Stack)

```kotlin
Column(
    modifier = Modifier.fillMaxWidth().padding(16.dp),
    horizontalAlignment = Alignment.CenterHorizontally,
    verticalArrangement = Arrangement.spacedBy(12.dp) // Consistent spacing
) {
    Text("Title")
    Text("Subtitle")
    Button(onClick = {}) { Text("Action") }
}
```

### Row (Horizontal Stack)

```kotlin
Row(
    modifier = Modifier.fillMaxWidth().padding(16.dp),
    verticalAlignment = Alignment.CenterVertically,
    horizontalArrangement = Arrangement.SpaceBetween
) {
    Text("Label")
    Switch(checked = isEnabled, onCheckedChange = onToggle)
}
```

### Box (Overlay/Stack)

```kotlin
Box(modifier = Modifier.fillMaxSize()) {
    // Background content
    LazyColumn { /* list */ }
    // Floating overlay
    FloatingActionButton(
        onClick = {},
        modifier = Modifier.align(Alignment.BottomEnd).padding(16.dp)
    ) { Icon(painterResource(R.drawable.add), "Add") }
}
```

### LazyColumn (Scrollable List)

```kotlin
LazyColumn(
    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
    verticalArrangement = Arrangement.spacedBy(12.dp)
) {
    // Section header
    item { SectionHeader("Recent") }

    // Items with keys (CRITICAL for performance)
    items(items = recentItems, key = { it.id }) { item ->
        ItemCard(item)
    }

    // Another section
    item { SectionHeader("All Items") }

    items(items = allItems, key = { it.id }) { item ->
        ItemCard(item)
    }

    // Bottom spacer for FAB clearance
    item { Spacer(Modifier.height(72.dp)) }
}
```

### LazyVerticalGrid

```kotlin
LazyVerticalGrid(
    columns = GridCells.Adaptive(minSize = 160.dp),
    contentPadding = PaddingValues(16.dp),
    horizontalArrangement = Arrangement.spacedBy(12.dp),
    verticalArrangement = Arrangement.spacedBy(12.dp)
) {
    items(items = items, key = { it.id }) { item ->
        GridItemCard(item)
    }
}
```

## Modifier Patterns

### Order Matters

Modifiers apply **outside-in**. This sequence is standard:

```kotlin
Modifier
    .fillMaxWidth()                    // 1. Size constraints
    .padding(horizontal = 16.dp)       // 2. Outer padding (margin effect)
    .clip(RoundedCornerShape(16.dp))   // 3. Shape clipping
    .background(MaterialTheme.colorScheme.surface) // 4. Background
    .clickable { }                     // 5. Interaction
    .padding(16.dp)                    // 6. Inner padding (content padding)
```

### Standard Modifier Chains

```kotlin
// Card modifier
val cardModifier = Modifier
    .fillMaxWidth()
    .clip(RoundedCornerShape(16.dp))

// List item modifier
val listItemModifier = Modifier
    .fillMaxWidth()
    .clickable(onClick = onClick)
    .padding(horizontal = 16.dp, vertical = 12.dp)

// Image modifier (circular)
val avatarModifier = Modifier
    .size(48.dp)
    .clip(CircleShape)
    .border(2.dp, MaterialTheme.colorScheme.primary, CircleShape)

// Divider-like bottom border
val bottomBorderModifier = Modifier
    .fillMaxWidth()
    .drawBehind {
        drawLine(
            color = Color.LightGray,
            start = Offset(0f, size.height),
            end = Offset(size.width, size.height),
            strokeWidth = 1.dp.toPx()
        )
    }
```

## Material 3 Components

### TopAppBar Variants

```kotlin
// Standard
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StandardTopBar(
    title: String,
    onBack: () -> Unit,
    actions: @Composable RowScope.() -> Unit = {}
) {
    TopAppBar(
        title = { Text(title) },
        navigationIcon = {
            IconButton(onClick = onBack) {
                Icon(painterResource(R.drawable.back), "Back")
            }
        },
        actions = actions
    )
}

// Large (collapsing)
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LargeTopBar(
    title: String,
    scrollBehavior: TopAppBarScrollBehavior,
    onBack: () -> Unit
) {
    LargeTopAppBar(
        title = { Text(title) },
        navigationIcon = {
            IconButton(onClick = onBack) {
                Icon(painterResource(R.drawable.back), "Back")
            }
        },
        scrollBehavior = scrollBehavior
    )
}
```

### TextField (Standard Form Input)

```kotlin
@Composable
fun AppTextField(
    value: String,
    onValueChange: (String) -> Unit,
    label: String,
    modifier: Modifier = Modifier,
    error: String? = null,
    leadingIconRes: Int? = null,
    keyboardType: KeyboardType = KeyboardType.Text,
    singleLine: Boolean = true
) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        label = { Text(label) },
        isError = error != null,
        supportingText = error?.let { { Text(it, color = MaterialTheme.colorScheme.error) } },
        leadingIcon = leadingIconRes?.let { { Icon(painterResource(it), null) } },
        modifier = modifier.fillMaxWidth(),
        singleLine = singleLine,
        keyboardOptions = KeyboardOptions(keyboardType = keyboardType),
        shape = RoundedCornerShape(12.dp)
    )
}
```

### Button Hierarchy

```kotlin
// Primary action (ONE per screen)
Button(
    onClick = onSubmit,
    modifier = Modifier.fillMaxWidth().height(48.dp),
    shape = RoundedCornerShape(12.dp)
) {
    Text("Submit", style = MaterialTheme.typography.labelLarge)
}

// Secondary action
OutlinedButton(
    onClick = onCancel,
    modifier = Modifier.fillMaxWidth().height(48.dp),
    shape = RoundedCornerShape(12.dp)
) {
    Text("Cancel")
}

// Tertiary / inline action
TextButton(onClick = onSkip) {
    Text("Skip for now")
}

// Icon action (toolbar, list items)
IconButton(onClick = onMore) {
    Icon(painterResource(R.drawable.more), "More options")
}

// FAB (floating primary action)
FloatingActionButton(
    onClick = onCreate,
    shape = RoundedCornerShape(16.dp),
    containerColor = MaterialTheme.colorScheme.primaryContainer
) {
    Icon(painterResource(R.drawable.add), "Create")
}
```

### Chips

```kotlin
// Filter chip (toggle on/off)
FilterChip(
    selected = isSelected,
    onClick = onToggle,
    label = { Text("Active") },
    leadingIcon = if (isSelected) {
        { Icon(painterResource(R.drawable.check), null, Modifier.size(16.dp)) }
    } else null
)

// Input chip (removable tag)
InputChip(
    selected = true,
    onClick = {},
    label = { Text("Tag Name") },
    trailingIcon = {
        IconButton(onClick = onRemove, modifier = Modifier.size(16.dp)) {
            Icon(painterResource(R.drawable.close), "Remove")
        }
    }
)
```

### Bottom Sheet

```kotlin
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OptionsBottomSheet(
    onDismiss: () -> Unit,
    options: List<BottomSheetOption>,
    onOptionClick: (BottomSheetOption) -> Unit
) {
    ModalBottomSheet(
        onDismissRequest = onDismiss,
        shape = RoundedCornerShape(topStart = 24.dp, topEnd = 24.dp)
    ) {
        Column(modifier = Modifier.padding(bottom = 32.dp)) {
            options.forEach { option ->
                ListItem(
                    headlineContent = { Text(option.title) },
                    supportingContent = option.subtitle?.let { { Text(it) } },
                    leadingContent = { Icon(painterResource(option.iconRes), null) },
                    modifier = Modifier.clickable { onOptionClick(option); onDismiss() }
                )
            }
        }
    }
}
```

### Dialogs

```kotlin
@Composable
fun ConfirmDialog(
    title: String,
    message: String,
    confirmText: String = "Confirm",
    dismissText: String = "Cancel",
    isDestructive: Boolean = false,
    onConfirm: () -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(title) },
        text = { Text(message) },
        confirmButton = {
            TextButton(onClick = onConfirm) {
                Text(
                    confirmText,
                    color = if (isDestructive) MaterialTheme.colorScheme.error
                    else MaterialTheme.colorScheme.primary
                )
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text(dismissText) }
        }
    )
}
```

## Scaffold Structure

Every screen uses Scaffold as the root:

```kotlin
Scaffold(
    topBar = { /* TopAppBar */ },
    bottomBar = { /* NavigationBar (main screens only) */ },
    floatingActionButton = { /* FAB (optional) */ },
    snackbarHost = { SnackbarHost(snackbarHostState) }
) { innerPadding ->
    // ALWAYS apply innerPadding to content
    Content(modifier = Modifier.padding(innerPadding))
}
```

## Bottom Navigation

```kotlin
@Composable
fun AppBottomNav(
    currentRoute: String,
    onNavigate: (String) -> Unit
) {
    NavigationBar {
        bottomNavItems.forEach { item ->
            NavigationBarItem(
                selected = currentRoute == item.route,
                onClick = { onNavigate(item.route) },
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

data class BottomNavItem(
    val route: String,
    val label: String,
    val selectedIcon: ImageVector,
    val unselectedIcon: ImageVector
)
```

## Tab Layout

```kotlin
@Composable
fun TabSection(
    tabs: List<String>,
    selectedIndex: Int,
    onTabSelected: (Int) -> Unit,
    modifier: Modifier = Modifier
) {
    TabRow(selectedTabIndex = selectedIndex, modifier = modifier) {
        tabs.forEachIndexed { index, title ->
            Tab(
                selected = selectedIndex == index,
                onClick = { onTabSelected(index) },
                text = { Text(title) }
            )
        }
    }
}
```
